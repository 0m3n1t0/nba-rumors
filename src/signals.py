"""Stage 1b: what people are WATCHING and SEARCHING right now.

The collector knows what the media writes. This stage adds what the audience does:

1. YouTube heat: the most-watched NBA videos of the last 24 hours (YouTube Data API,
   our own read-only token), measured in views per hour. A topic gets "heat" when its
   players or teams appear in those videos' titles.
2. Search demand: YouTube search autocomplete for NBA seeds and for today's top names,
   i.e. what people are typing right now. A topic gets "search hits" when its names
   appear in those suggestions. The phrases also go to the script stage for titles.

This stage must never stop the pipeline: if YouTube or autocomplete fails, the run
continues without the signals.

Output: data/signals.json, and data/topics.json enriched with youtube_heat / search_hits.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from collect import names  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TOP_TOPICS = 40
SEARCH_QUERIES = ["NBA", "NBA drama OR beef OR trade OR fight"]
SEEDS = ["nba ", "nba drama", "nba beef", "nba trade", "nba fight", "nba news today"]
AUTOCOMPLETE = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&q={q}"
READONLY = "https://www.googleapis.com/auth/youtube.readonly"


# ---------- YouTube: what people are watching ----------

def youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    info = json.loads(os.environ["YT_CLIENT_SECRET"])
    c = info.get("installed") or info.get("web")
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        token_uri=c["token_uri"], client_id=c["client_id"],
                        client_secret=c["client_secret"], scopes=[READONLY])
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def trending_videos() -> list[dict]:
    yt = youtube()
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids: list[str] = []
    for q in SEARCH_QUERIES:
        res = yt.search().list(part="id", q=q, type="video", order="viewCount",
                               publishedAfter=since, maxResults=50, regionCode="US",
                               relevanceLanguage="en").execute()
        ids += [i["id"]["videoId"] for i in res.get("items", []) if i["id"].get("videoId")]
    ids = list(dict.fromkeys(ids))[:100]

    videos = []
    for chunk in (ids[i:i + 50] for i in range(0, len(ids), 50)):
        res = yt.videos().list(part="snippet,statistics", id=",".join(chunk)).execute()
        for v in res.get("items", []):
            published = datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
            hours = max(1.0, (datetime.now(timezone.utc) - published).total_seconds() / 3600)
            views = int(v["statistics"].get("viewCount", 0))
            videos.append({
                "title": v["snippet"]["title"],
                "channel": v["snippet"]["channelTitle"],
                "views": views,
                "views_per_hour": round(views / hours),
            })
    return sorted(videos, key=lambda v: -v["views_per_hour"])


# ---------- Search: what people are typing ----------

def suggestions(seed: str) -> list[str]:
    url = AUTOCOMPLETE.format(q=urllib.parse.quote(seed))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    return [s for s in data[1] if isinstance(s, str)]


# ---------- Matching topics to signals ----------

def topic_keys(topic: dict) -> set[str]:
    """Surnames of the people in a topic. Team names are NOT used: every full-game
    highlight video has two team names, so teams would make every topic look hot."""
    found = set()
    for title in [topic["headline"]] + [it["title"] for it in topic["items"][:6]]:
        found |= names(title)  # per title, so two titles never glue into a fake name
    keys = set()
    for n in found:
        last = n.split()[-1].lower()
        # A rare surname alone is enough ("embiid"); a common one needs the full name ("jalen smith").
        keys.add(n.lower() if last in COMMON_SURNAMES or len(last) < 5 else last)
    return keys


COMMON_SURNAMES = set("""smith johnson williams brown jones james green davis miller wilson moore
taylor anderson thomas jackson white harris martin thompson young allen walker king wright scott
hill adams baker nelson carter mitchell roberts turner phillips campbell parker evans edwards
collins stewart morris murphy cook rogers morgan cooper peterson bailey reed bell howard ward
hunter porter murray holiday george paul""".split())


# Words that show people are searching for a STORY about someone, not just their highlights.
STORY_WORDS = re.compile(
    r"\b(trade|traded|beef|fight|drama|fined|suspended|ejected|technical|shove|injury|injured|"
    r"contract|fired|rumou?rs?|news|reaction|responds|calls out|diss|feud|angry|argument|history)\b",
    re.I,
)
# Suggestions that are noise for us (a rapper named NBA YoungBoy, video games, betting...)
NOISE = re.compile(r"youngboy|2k\d*|\bpicks\b|\bodds\b|\blive\b|type beat|\bmeme", re.I)


GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo=US"   # public, free, hourly


def google_trends() -> list[dict]:
    """What the US is searching on Google right now (Trending Now, public RSS feed): the query,
    its approximate traffic and the headlines Google links to it. Spikes often show up here
    before YouTube catches up."""
    import urllib.request
    import xml.etree.ElementTree as ET
    req = urllib.request.Request(GOOGLE_TRENDS_RSS, headers={"User-Agent": "Mozilla/5.0 (nba-rumors pipeline)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    local = lambda tag: tag.rsplit("}", 1)[-1]
    out = []
    for item in root.iter("item"):
        query, traffic, news = "", 0, []
        for el in item.iter():
            name = local(el.tag)
            if name == "title" and not query:
                query = (el.text or "").strip()
            elif name == "approx_traffic":
                traffic = int(re.sub(r"[^0-9]", "", el.text or "") or 0)
            elif name == "news_item_title":
                news.append((el.text or "").strip())
        if query:
            out.append({"query": query, "traffic": traffic, "news": news})
    return out


def mentions(keys: set[str], text: str) -> bool:
    return any(re.search(rf"\b{re.escape(k)}\b", text, re.I) for k in keys)


def main() -> None:
    topics = json.loads((DATA / "topics.json").read_text(encoding="utf-8"))
    signals: dict = {"videos": [], "suggestions": [], "errors": []}

    try:
        signals["videos"] = trending_videos()
        print(f"[+] YouTube: {len(signals['videos'])} NBA videos from the last 24h")
    except Exception as exc:
        signals["errors"].append(f"youtube: {exc}")
        print(f"[!] YouTube signal skipped: {exc}")

    try:
        signals["google_trends"] = google_trends()
        print(f"[+] Google Trends: {len(signals['google_trends'])} trending searches")
    except Exception as exc:
        signals["google_trends"] = []
        signals["errors"].append(f"google trends: {exc}")
        print(f"[!] Google Trends signal skipped: {exc}")

    # Seeds: general NBA ones plus today's top names (what people type about them).
    top_names = []
    for t in topics[:15]:
        for n in names(t["headline"]):
            if n not in top_names:
                top_names.append(n)
    seeds = SEEDS + [f"{n.lower()} " for n in top_names[:12]]
    found: list[str] = []
    for seed in seeds:
        try:
            found += suggestions(seed)
        except Exception as exc:
            signals["errors"].append(f"autocomplete '{seed}': {exc}")
    signals["suggestions"] = [x for x in dict.fromkeys(found) if not NOISE.search(x)]
    print(f"[+] Search: {len(signals['suggestions'])} live search phrases")

    raw = {}
    for i, t in enumerate(topics[:TOP_TOPICS]):
        keys = topic_keys(t)
        raw[i] = sum(v["views_per_hour"] for v in signals["videos"] if keys and mentions(keys, v["title"]))
        # A name search only counts when people pair the name with a story word
        # ("embiid shove", "bronny james kwame brown"), and the phrase is not just the name.
        story = [x for x in signals["suggestions"]
                 if keys and mentions(keys, x) and (STORY_WORDS.search(x) or len(keys & set(x.split())) > 1)]
        t["search_hits"] = len(story)
        t["search_phrases"] = story[:8]
        # Google Trends: a trending US search about this topic's people (0-10, log of the traffic:
        # 200+ searches ~ 4.6, 20K+ ~ 8.6, 100K+ = 10)
        hits = [g for g in signals.get("google_trends", [])
                if keys and (mentions(keys, g["query"]) or any(mentions(keys, n) for n in g["news"]))]
        best = max((g["traffic"] for g in hits), default=0)
        t["google_trend"] = round(min(10.0, 2 * math.log10(best)), 1) if best > 1 else 0
        t["google_queries"] = [g["query"] for g in hits][:3]
    top = max(raw.values(), default=0) or 1
    for i, t in enumerate(topics[:TOP_TOPICS]):
        # 0-10 relative to today's hottest topic (square root: differences stay visible,
        # one monster video still does not flatten everything else)
        t["youtube_heat"] = round(10 * math.sqrt(raw[i] / top), 1) if raw[i] else 0

    (DATA / "topics.json").write_text(json.dumps(topics, indent=2), encoding="utf-8")
    (DATA / "signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")

    lines = ["## 📈 Audience signals", "",
             f"YouTube videos read: {len(signals['videos'])} · search phrases: {len(signals['suggestions'])}"
             + (f" · ⚠️ {len(signals['errors'])} errors" if signals["errors"] else ""), "",
             "**Most watched NBA videos (last 24h, views/hour):**", ""]
    for v in signals["videos"][:10]:
        lines.append(f"- {v['views_per_hour']:,}/h · {v['title']} ({v['channel']})")
    lines += ["", "**Topics people are watching and searching:**", "",
              "| YouTube heat | search hits | Google trend | topic |", "|---|---|---|---|"]
    hot = sorted(topics[:TOP_TOPICS], key=lambda t: -(t.get("youtube_heat", 0) + t.get("search_hits", 0)
                                                     + t.get("google_trend", 0)))
    for t in hot[:12]:
        gq = f" ({', '.join(t['google_queries'])})" if t.get("google_queries") else ""
        lines.append(f"| {t.get('youtube_heat', 0)} | {t.get('search_hits', 0)} | {t.get('google_trend', 0)}{gq} | {t['headline']} |")
    nba_trends = [g for g in signals.get("google_trends", [])
                  if re.search(r"nba|lakers|celtics|warriors|knicks|bucks|heat|nuggets|suns|mavericks|"
                               r"76ers|sixers|nets|bulls|cavaliers|thunder|spurs|rockets|clippers|kings|"
                               r"pistons|pacers|hawks|hornets|magic|raptors|wizards|jazz|blazers|"
                               r"grizzlies|pelicans|timberwolves|basketball", g["query"] + " " + " ".join(g["news"]), re.I)]
    lines += ["", "**Google Trends (US, now), basketball-related:** "
              + (" · ".join(f"{g['query']} ({g['traffic']:,}+)" for g in nba_trends[:10]) or "none right now")]
    matched = list(dict.fromkeys(p for t in topics[:TOP_TOPICS] for p in t.get("search_phrases", [])))
    lines += ["", "**What people are typing about today's stories:** " + (" · ".join(matched[:25]) or "none yet")]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

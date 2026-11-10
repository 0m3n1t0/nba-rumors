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


MOMENTUM = DATA / "history" / "momentum.json"   # kept between runs by the GitHub cache


def momentum(topics: list[dict]) -> None:
    """Story velocity: how many MORE outlets cover a story than at the previous run (0-5).
    A story that jumps from 1 to 5 outlets in a few hours is breaking; one stuck at 5 for a
    day is old news. Matched by the people in it (2 shared surnames, or 1 if it has only 1)."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    try:
        prev = json.loads(MOMENTUM.read_text(encoding="utf-8"))
        age = (now - datetime.fromisoformat(prev["time"])).total_seconds() / 3600
        prev = prev["topics"] if age <= 30 else None      # a snapshot older than ~a day says nothing
    except (OSError, ValueError, KeyError):
        prev = None
    snap = []
    for t in topics[:TOP_TOPICS]:
        keys = topic_keys(t)
        outlets = t.get("outlets", 0) or 0
        if prev is not None and keys:
            need = 1 if len(keys) == 1 else 2
            before = max((p["outlets"] for p in prev if len(keys & set(p["keys"])) >= need), default=0)
            t["momentum"] = max(0, min(5, outlets - before))
            t["outlets_before"] = before
        else:
            t["momentum"] = 0
        snap.append({"keys": sorted(keys), "outlets": outlets})
    MOMENTUM.parent.mkdir(parents=True, exist_ok=True)
    MOMENTUM.write_text(json.dumps({"time": now.isoformat(timespec="minutes"), "topics": snap}),
                        encoding="utf-8")


WIKI_UA = {"User-Agent": "nba-rumors-pipeline/1.0 (https://github.com/0m3n1t0/nba-rumors)"}
SPORTS_DESC = re.compile(r"basketball|\bnba\b|coach|executive|sports|athlete|broadcaster|analyst", re.I)


def wiki_fame(all_names: set[str]) -> dict[str, float]:
    """How famous each person is RIGHT NOW: English Wikipedia views of their page in the last
    7 days (free, no key), 0-10 on a log scale (7K views a week ~ 0, 70K ~ 5, 700K+ = 10).
    Names are resolved through Wikipedia's redirects first ("Nikola Jokic" -> "Nikola Jokić",
    otherwise the biggest stars with accents would look unknown), and only pages whose short
    description is about basketball or sports count (never a same-name actor)."""
    from datetime import date
    names_list = sorted(all_names)[:150]
    resolved: dict[str, str] = {}
    for i in range(0, len(names_list), 50):
        q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1,
                                    "prop": "pageprops", "ppprop": "wikibase-shortdesc",
                                    "titles": "|".join(names_list[i:i + 50])})
        req = urllib.request.Request(f"https://en.wikipedia.org/w/api.php?{q}", headers=WIKI_UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))["query"]
        alias = {}
        for step in ("normalized", "redirects"):
            for m in data.get(step, []):
                alias[m["from"]] = m["to"]
        sports = {p["title"] for p in data.get("pages", {}).values()
                  if "missing" not in p and SPORTS_DESC.search(p.get("pageprops", {}).get("wikibase-shortdesc", ""))}
        for n in names_list[i:i + 50]:
            t = alias.get(alias.get(n, n), alias.get(n, n))
            if t in sports:
                resolved[n] = t
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=6)
    views: dict[str, int] = {}
    fame = {}
    for n, title in resolved.items():
        if title not in views:
            url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/"
                   f"all-access/user/{urllib.parse.quote(title.replace(' ', '_'), safe='')}/daily/"
                   f"{start:%Y%m%d}00/{end:%Y%m%d}00")
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=WIKI_UA), timeout=20) as r:
                    views[title] = sum(x["views"] for x in json.loads(r.read().decode("utf-8"))["items"])
            except Exception:
                views[title] = 0
        v = views[title]
        fame[n] = round(max(0.0, min(10.0, 5 * math.log10(v / 7000))), 1) if v > 7000 else 0.0
    return fame


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


NBA_WORDS = re.compile(r"\b(nba|basketball|lakers|celtics|warriors|knicks|bucks|heat|nuggets|suns|"
                       r"mavericks|76ers|sixers|nets|bulls|cavaliers|thunder|spurs|rockets|clippers|"
                       r"kings|pistons|pacers|hawks|hornets|magic|raptors|wizards|jazz|blazers|"
                       r"grizzlies|pelicans|timberwolves)\b", re.I)


REDDIT_RSS = "https://www.reddit.com/r/nba/hot/.rss?limit=50"   # public feed, no key


def reddit_hot() -> list[str]:
    """Titles of r/nba's hot posts, in order (the public RSS feed). Fans argue about a beef
    there before the news sites catch up. Skipped quietly when the feed is not reachable."""
    import urllib.request
    import xml.etree.ElementTree as ET
    req = urllib.request.Request(REDDIT_RSS, headers={"User-Agent": "nba-rumors-pipeline/1.0 (trend signal; "
                                                                    "github.com/0m3n1t0/nba-rumors)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    return [(el.text or "").strip() for e in root.iter() if e.tag.endswith("entry")
            for el in e if el.tag.endswith("title")]


def reddit_heat(topic: dict, titles: list[str]) -> float:
    """0-10: how many of r/nba's hot posts are about this topic's real people (a post in the
    top 10 counts double)."""
    keys = star_keys(topic)
    if not keys:
        return 0.0
    hits = sum(2 if rank < 10 else 1 for rank, t in enumerate(titles) if mentions(keys, t))
    return round(min(10.0, 2.0 * hits), 1)


def star_keys(topic: dict) -> set[str]:
    """Search keys only for the topic's people that Wikipedia confirmed as sports people."""
    keys = set()
    for entry in topic.get("star_names") or []:
        name = re.sub(r"\s+[\d.]+$", "", entry).strip()      # "Jayson Tatum 6.1" -> "Jayson Tatum"
        last = name.split()[-1].lower() if name else ""
        if last:
            keys.add(name.lower() if last in COMMON_SURNAMES or len(last) < 5 else last)
    return keys


def trend_matches(topic: dict, trend: dict) -> bool:
    """The trending search itself names one of the topic's real people, or one of its news
    headlines names them AND is about basketball."""
    keys = star_keys(topic)
    if not keys:
        return False
    if mentions(keys, trend.get("query", "")):
        return True
    return any(mentions(keys, n) and NBA_WORDS.search(n) for n in trend.get("news", []))


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
    top = max(raw.values(), default=0) or 1
    for i, t in enumerate(topics[:TOP_TOPICS]):
        # 0-10 relative to today's hottest topic (square root: differences stay visible,
        # one monster video still does not flatten everything else)
        t["youtube_heat"] = round(10 * math.sqrt(raw[i] / top), 1) if raw[i] else 0

    # Star power: how famous the people in each story are right now (Wikipedia views)
    try:
        people = {t_i: set().union(*[names(x) for x in [t["headline"]] + [it["title"] for it in t["items"][:6]]])
                  for t_i, t in enumerate(topics[:TOP_TOPICS])}
        fame = wiki_fame(set().union(*people.values()) if people else set())
        for t_i, t in enumerate(topics[:TOP_TOPICS]):
            ranked = sorted(((fame.get(n, 0), n) for n in people[t_i]), reverse=True)
            t["star_fame"] = ranked[0][0] if ranked else 0
            t["star_names"] = [f"{n} {f}" for f, n in ranked[:3] if f]
        print(f"[+] Star power: {sum(1 for f in fame.values() if f)} people found on Wikipedia")
    except Exception as exc:
        signals["errors"].append(f"star power: {exc}")
        print(f"[!] star power skipped: {exc}")

    # Google Trends: a trending US search about this topic's people (0-10, log of the traffic:
    # 200+ searches ~ 4.6, 20K+ ~ 8.6, 100K+ = 10). Only through REAL sports people (the names
    # Wikipedia confirmed above): a Title Case headline makes fake "names" ("Perfect Lineup",
    # "Blank Space") that matched "snowfall forecast" or "gta vi" and lifted dull stories.
    for t in topics[:TOP_TOPICS]:
        hits = [g for g in signals.get("google_trends", []) if trend_matches(t, g)]
        best = max((g["traffic"] for g in hits), default=0)
        t["google_trend"] = round(min(10.0, 2 * math.log10(best)), 1) if best > 1 else 0
        t["google_queries"] = [g["query"] for g in hits][:3]

    try:
        signals["reddit"] = reddit_hot()
        print(f"[+] Reddit r/nba: {len(signals['reddit'])} hot posts")
    except Exception as exc:
        signals["reddit"] = []
        signals["errors"].append(f"reddit: {exc}")
        print(f"[!] Reddit signal skipped: {exc}")
    for t in topics[:TOP_TOPICS]:
        t["reddit"] = reddit_heat(t, signals["reddit"])

    try:
        momentum(topics)
    except Exception as exc:
        signals["errors"].append(f"momentum: {exc}")
        print(f"[!] momentum skipped: {exc}")
    (DATA / "topics.json").write_text(json.dumps(topics, indent=2), encoding="utf-8")
    (DATA / "signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")

    lines = ["## 📈 Audience signals", "",
             f"YouTube videos read: {len(signals['videos'])} · search phrases: {len(signals['suggestions'])}"
             + (f" · ⚠️ {len(signals['errors'])} errors" if signals["errors"] else ""), "",
             "**Most watched NBA videos (last 24h, views/hour):**", ""]
    for v in signals["videos"][:10]:
        lines.append(f"- {v['views_per_hour']:,}/h · {v['title']} ({v['channel']})")
    lines += ["", "**Topics people are watching and searching:**", "",
              "| YouTube heat | search hits | Google trend | Reddit | rising (new outlets) | star power | topic |", "|---|---|---|---|---|---|---|"]
    hot = sorted(topics[:TOP_TOPICS], key=lambda t: -(t.get("youtube_heat", 0) + t.get("search_hits", 0)
                                                     + t.get("google_trend", 0) + t.get("reddit", 0)))
    for t in hot[:12]:
        gq = f" ({', '.join(t['google_queries'])})" if t.get("google_queries") else ""
        rise = f"+{t['momentum']}" if t.get("momentum") else "0"
        lines.append(f"| {t.get('youtube_heat', 0)} | {t.get('search_hits', 0)} | {t.get('google_trend', 0)}{gq} | "
                     f"{t.get('reddit', 0)} | {rise} | {t.get('star_fame', 0)} | {t['headline']} |")
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

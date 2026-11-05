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
from collect import TEAMS, names  # noqa: E402

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
    """Words that identify a topic in other titles: surnames and team names."""
    text = " ".join([topic["headline"]] + [it["title"] for it in topic["items"][:6]])
    keys = {n.split()[-1].lower() for n in names(text)}
    keys |= {t for t in TEAMS if re.search(rf"\b{t}\b", text, re.I)}
    return {k for k in keys if len(k) > 3}


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
    signals["suggestions"] = list(dict.fromkeys(found))
    print(f"[+] Search: {len(signals['suggestions'])} live search phrases")

    max_vph = max([v["views_per_hour"] for v in signals["videos"]] + [1])
    for t in topics[:TOP_TOPICS]:
        keys = topic_keys(t)
        vph = sum(v["views_per_hour"] for v in signals["videos"] if mentions(keys, v["title"]))
        # 0-10, log scale: one monster video should not drown everything else
        t["youtube_heat"] = round(10 * math.log1p(vph) / math.log1p(max_vph), 1) if vph else 0
        t["search_hits"] = sum(1 for s in signals["suggestions"] if mentions(keys, s))
        t["search_phrases"] = [s for s in signals["suggestions"] if mentions(keys, s)][:8]

    (DATA / "topics.json").write_text(json.dumps(topics, indent=2), encoding="utf-8")
    (DATA / "signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")

    lines = ["## 📈 Audience signals", "",
             f"YouTube videos read: {len(signals['videos'])} · search phrases: {len(signals['suggestions'])}"
             + (f" · ⚠️ {len(signals['errors'])} errors" if signals["errors"] else ""), "",
             "**Most watched NBA videos (last 24h, views/hour):**", ""]
    for v in signals["videos"][:10]:
        lines.append(f"- {v['views_per_hour']:,}/h · {v['title']} ({v['channel']})")
    lines += ["", "**Topics people are watching and searching:**", "",
              "| YouTube heat | search hits | topic |", "|---|---|---|"]
    hot = sorted(topics[:TOP_TOPICS], key=lambda t: -(t.get("youtube_heat", 0) + t.get("search_hits", 0)))
    for t in hot[:12]:
        lines.append(f"| {t.get('youtube_heat', 0)} | {t.get('search_hits', 0)} | {t['headline']} |")
    lines += ["", "**What people are typing:** " + " · ".join(signals["suggestions"][:25])]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

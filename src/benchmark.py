"""Benchmark: what already works in our niche (NBA drama / rumors Shorts).

Finds the most-viewed NBA drama, beef, rumor and news Shorts of the last 30 days,
the channels behind them, and the patterns in their titles and lengths. The report
ends with a watch list: the top Shorts to watch and note the voice (male/female,
AI/human), the pace and the visuals.

Collection is ours (YouTube Data API, the same read-only token as signals.py, about
650 quota units per run). The outlier analysis is youtube-agent-skill's yt-viral
(vendor/youtube-agent-skill/skills/yt-viral/swipe.py): each Short is ranked by how far it beat its own channel.

Output: data/benchmark.csv and a report on the Actions page.
"""

from __future__ import annotations

import csv
import json
import os
import re
import statistics
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from signals import youtube  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
VENDOR = ROOT / "vendor" / "youtube-agent-skill" / "skills"
DAYS = 30
QUERIES = ["NBA drama", "NBA beef", "NBA rumors", "NBA trade rumors", "NBA news", "NBA fight"]
STOP = set("the a an of to in on for with and or is are was his her he she they this that it at by "
           "from as be vs nba shorts short".split())


def seconds(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    h, mi, s = (int(x) if x else 0 for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + s


def pct(n: int, items: list) -> int:
    return round(100 * n / max(len(items), 1))


NICHE = ROOT / "plan" / "niche.json"
OFF_NICHE = re.compile(r"high school|streetball|hooper|handles|wnba|caitlin|highlights|full game|mixtape|"
                       r"\bkids?\b|college|ncaa|nfl|soccer|glitch|laws of physics", re.I)
DRAMA = re.compile(r"beef|fight|exposed|banned|called? out|confront|feud|trade|rumou?r|drama|heated|ejected|"
                   r"fined|suspend|trash|exchange|turn(ed)? against|speak out|media training|cheat|shocking|"
                   r"ended|refused|ruined|slammed|clap|disrespect|fired|benched|demand|leak|snub", re.I)
MIN_MEDIAN = 3000     # a channel whose normal Short gets fewer views says nothing about the audience
MAX_MULTIPLE = 500    # beyond this it is a fluke, not a pattern


def save_niche(videos: list[dict], viral: dict) -> None:
    """What wins in the niche right now, for the daily editor and script writer (plan/niche.json).
    Titles are other channels' text: kept short and used only as patterns, never copied."""
    # Keep only real NBA drama/news Shorts from channels with a real audience: the raw list also
    # holds streetball, high school fights, highlight reels and flukes from tiny channels.
    keep = [r for r in viral.get("outliers", [])
            if not OFF_NICHE.search(r["title"]) and (r.get("median") or 0) >= MIN_MEDIAN
            and r.get("multiple", 0) <= MAX_MULTIPLE]
    keep.sort(key=lambda r: (not DRAMA.search(r["title"]), -r["multiple"]))
    outliers = keep[:15]
    lens = [v["seconds"] for v in videos[:50]]
    data = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "median_seconds": round(statistics.median(lens)) if lens else None,
        "outliers": [{"title": r["title"][:100], "multiple": r["multiple"], "views": r["views"],
                      "formula": r.get("formula", "")} for r in outliers],
        "top_viewed": [{"title": v["title"][:100], "views": v["views"], "seconds": v["seconds"]}
                       for v in videos[:15]],
        "formulas": [f for f, _ in Counter(r.get("formula", "") for r in keep).most_common(8)
                     if f and f.lower() != "unclassified"][:6],
    }
    NICHE.parent.mkdir(parents=True, exist_ok=True)
    NICHE.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    yt = youtube()
    since = (datetime.now(timezone.utc) - timedelta(days=DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    ids: list[str] = []
    for q in QUERIES:
        res = yt.search().list(part="id", q=q, type="video", videoDuration="short", order="viewCount",
                               publishedAfter=since, maxResults=50, regionCode="US",
                               relevanceLanguage="en").execute()
        ids += [i["id"]["videoId"] for i in res.get("items", []) if i["id"].get("videoId")]
    ids = list(dict.fromkeys(ids))

    videos = []
    for chunk in (ids[i:i + 50] for i in range(0, len(ids), 50)):
        res = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(chunk)).execute()
        for v in res.get("items", []):
            dur = seconds(v["contentDetails"].get("duration"))
            if dur == 0 or dur > 180:  # Shorts only
                continue
            st = v["statistics"]
            published = datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
            days = max(1.0, (datetime.now(timezone.utc) - published).total_seconds() / 86400)
            views = int(st.get("viewCount", 0))
            videos.append({
                "title": v["snippet"]["title"],
                "channel": v["snippet"]["channelTitle"],
                "channel_id": v["snippet"]["channelId"],
                "views": views,
                "views_per_day": round(views / days),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
                "seconds": dur,
                "url": f"https://www.youtube.com/shorts/{v['id']}",
            })

    # Channel sizes, so we can spot outliers (a small channel with a huge Short = a format that works)
    channel_ids = list(dict.fromkeys(v["channel_id"] for v in videos))
    subs = {}
    for chunk in (channel_ids[i:i + 50] for i in range(0, len(channel_ids), 50)):
        res = yt.channels().list(part="statistics", id=",".join(chunk)).execute()
        for c in res.get("items", []):
            subs[c["id"]] = int(c["statistics"].get("subscriberCount", 0) or 0)
    for v in videos:
        v["channel_subs"] = subs.get(v["channel_id"], 0)
        v["outlier"] = round(v["views"] / max(v["channel_subs"], 1000), 1)

    videos.sort(key=lambda v: -v["views"])

    # yt-viral needs 4+ videos per channel to know each channel's normal (its median).
    # So for the top channels we also read their latest Shorts.
    collected = [{"channel": v["channel"], "title": v["title"], "views": v["views"],
                  "url": v["url"], "duration": v["seconds"]} for v in videos]
    top_channels = list(dict.fromkeys(v["channel_id"] for v in videos))[:20]
    res = yt.channels().list(part="contentDetails,snippet", id=",".join(top_channels)).execute() if top_channels else {}
    seen = {v["url"] for v in collected}
    for c in res.get("items", []):
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        items = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=20).execute()
        vids = [i["contentDetails"]["videoId"] for i in items.get("items", [])]
        if not vids:
            continue
        info = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(vids)).execute()
        for v in info.get("items", []):
            dur = seconds(v["contentDetails"].get("duration"))
            url = f"https://www.youtube.com/shorts/{v['id']}"
            if 0 < dur <= 180 and url not in seen:
                seen.add(url)
                collected.append({"channel": v["snippet"]["channelTitle"], "title": v["snippet"]["title"],
                                  "views": int(v["statistics"].get("viewCount", 0)), "url": url, "duration": dur})
    (DATA / "collected.json").write_text(json.dumps(collected, indent=1), encoding="utf-8")

    # youtube-agent-skill / yt-viral: rank by how far each Short beat its OWN channel's median
    swipe = subprocess.run([sys.executable, str(VENDOR / "yt-viral" / "swipe.py"), str(DATA / "collected.json"),
                            "--min", "2.0", "--json"], capture_output=True, text=True)
    viral = json.loads(swipe.stdout) if swipe.returncode == 0 and swipe.stdout.strip() else {"outliers": []}
    with open(DATA / "benchmark.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(videos[0].keys()) if videos else ["title"])
        w.writeheader()
        w.writerows(videos)

    save_niche(videos, viral)

    top = videos[:50]
    lines = [f"## 🔍 Benchmark: NBA drama / rumors Shorts, last {DAYS} days", "",
             f"{len(videos)} Shorts found across {len(set(v['channel'] for v in videos))} channels.", ""]
    if top:
        lens = [v["seconds"] for v in top]
        titles = [v["title"] for v in top]
        words = Counter(w for t in titles for w in re.findall(r"[a-z']+", t.lower())
                        if w not in STOP and len(w) > 2)
        lines += [
            "### Patterns in the top 50",
            "",
            f"- Length: median **{statistics.median(lens):.0f}s** (shortest {min(lens)}s, longest {max(lens)}s)",
            f"- Titles with a number: **{pct(sum(bool(re.search(r'[0-9]', t)) for t in titles), titles)}%** · "
            f"with a question: **{pct(sum('?' in t for t in titles), titles)}%** · "
            f"median title length: **{statistics.median(len(t) for t in titles):.0f} characters**",
            f"- Most used title words: {', '.join(w for w, _ in words.most_common(20))}",
            "",
            "### 🎧 Watch list: watch these 10 and note the voice",
            "",
            "For each one note: **male / female**, **AI / human voice**, **pace** (calm / fast / very fast), "
            "**visuals** (game clips / photos / text cards / face).",
            "",
            "| # | views | length | channel (subs) | Short |",
            "|---|---|---|---|---|",
        ]
        for i, v in enumerate(top[:10], 1):
            lines.append(f"| {i} | {v['views']:,} | {v['seconds']}s | {v['channel']} ({v['channel_subs']:,}) | "
                         f"[{v['title'][:70]}]({v['url']}) |")
        lines += ["", "### 🚀 yt-viral: Shorts that beat their own channel (a format that works, not a big name)", "",
                  "Multiple = this Short's views ÷ the channel's median Short. "
                  "The formula is yt-viral's reading of the TITLE, not proof of why it worked.", "",
                  "| multiple | views | channel median | channel | formula | Short |", "|---|---|---|---|---|---|"]
        for r in viral.get("outliers", [])[:15]:
            lines.append(f"| {r['multiple']}x | {r['views']:,} | {r['median']:,} | {r['channel']} | "
                         f"{r['formula']} | [{r['title'][:60]}]({r['url']}) |")
        formulas = Counter(r["formula"] for r in viral.get("outliers", []))
        if formulas:
            lines += ["", "**Title formulas that win most often:** "
                      + ", ".join(f"{f} ({n})" for f, n in formulas.most_common(6))]
        by_channel = Counter()
        for v in videos:
            by_channel[v["channel"]] += v["views"]
        lines += ["", "### Channels with the most views in the niche", ""]
        lines += [f"- {c}: {n:,} views" for c, n in by_channel.most_common(10)]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

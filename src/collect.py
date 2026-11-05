"""Stage 1: collect NBA headlines from RSS feeds and rank them into topics.

Output:
  data/items.json   every headline collected (deduplicated)
  data/topics.json  headlines grouped into topics, scored, best first
  A readable summary in the GitHub Actions job page (GITHUB_STEP_SUMMARY)

Run locally:  python src/collect.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

sys.path.insert(0, str(Path(__file__).parent))
from sources import FEEDS, TIER1_PUBLISHERS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MAX_AGE_HOURS = 36
USER_AGENT = "Mozilla/5.0 (compatible; NBARumorsBot/1.0)"

# Words that make a story more clickable. Weights are added to the topic score.
HOT_WORDS = {
    "trade": 3, "traded": 4, "rumor": 2, "rumors": 2, "request": 3, "demands": 4,
    "feud": 5, "beef": 5, "drama": 4, "fight": 4, "ejected": 3, "suspended": 4,
    "fined": 3, "fired": 5, "locker": 3, "rift": 5, "frustrated": 3, "unhappy": 4,
    "blasts": 4, "slams": 4, "calls out": 5, "injury": 2, "torn": 4, "acl": 5,
    "out for season": 5, "surgery": 3, "contract": 2, "extension": 2, "max": 2,
    "free agent": 3, "buyout": 3, "waived": 2, "signs": 2, "sources": 2,
    "per": 1, "reportedly": 2, "shocking": 2, "blockbuster": 5,
}

STOPWORDS = set(
    "a an the and or but of to in on for with at by from as is are was were be been "
    "it its this that after before over into about up down out new says said report "
    "reports nba vs his her their they he she we you".split()
)


def fetch_all() -> list[dict]:
    items = []
    for feed in FEEDS:
        try:
            parsed = feedparser.parse(feed["url"], agent=USER_AGENT)
        except Exception as exc:  # network errors must never kill the run
            print(f"[!] {feed['name']}: {exc}")
            continue
        count = 0
        for entry in parsed.entries:
            item = normalize(entry, feed)
            if item:
                items.append(item)
                count += 1
        print(f"[+] {feed['name']}: {count} items")
    return dedupe(items)


def normalize(entry, feed) -> dict | None:
    title = (entry.get("title") or "").strip()
    link = entry.get("link") or ""
    if not title or not link:
        return None

    publisher = feed["name"]
    tier = feed["tier"]
    # Google News titles look like "Headline - Publisher"
    if feed["name"].startswith("GN:"):
        src = entry.get("source", {}) or {}
        publisher = src.get("title") or (title.rsplit(" - ", 1)[-1] if " - " in title else "Unknown")
        if " - " in title:
            title = title.rsplit(" - ", 1)[0].strip()
        tier = 1 if any(p in publisher.lower() for p in TIER1_PUBLISHERS) else 2

    published = None
    for key in ("published_parsed", "updated_parsed"):
        if entry.get(key):
            published = datetime.fromtimestamp(time.mktime(entry[key]), tz=timezone.utc)
            break
    if published and published < datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS):
        return None

    summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "") or "")
    summary = re.sub(r"\s+", " ", summary).strip()[:400]

    return {
        "title": title,
        "link": link,
        "publisher": publisher,
        "tier": tier,
        "published": published.isoformat() if published else None,
        "summary": summary,
    }


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        key = re.sub(r"\W+", "", it["title"].lower())[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def cluster(items: list[dict], threshold: float = 0.35) -> list[list[dict]]:
    """Group headlines about the same story (simple word overlap)."""
    groups: list[tuple[set[str], list[dict]]] = []
    for it in items:
        tk = tokens(it["title"])
        if not tk:
            continue
        best, best_sim = None, 0.0
        for g_tokens, g_items in groups:
            sim = len(tk & g_tokens) / len(tk | g_tokens)
            if sim > best_sim:
                best, best_sim = (g_tokens, g_items), sim
        if best and best_sim >= threshold:
            best[0].update(tk)
            best[1].append(it)
        else:
            groups.append((set(tk), [it]))
    return [g for _, g in groups]


def score(group: list[dict]) -> dict:
    publishers = {it["publisher"].lower() for it in group}
    tier1 = {it["publisher"] for it in group if it["tier"] == 1}
    text = " ".join(it["title"].lower() for it in group)

    hot = sum(w for word, w in HOT_WORDS.items() if word in text)
    newest = max((it["published"] for it in group if it["published"]), default=None)
    hours_old = 24.0
    if newest:
        hours_old = (datetime.now(timezone.utc) - datetime.fromisoformat(newest)).total_seconds() / 3600

    value = (
        len(publishers) * 4          # many outlets covering it = big story
        + len(tier1) * 3             # trusted outlets = safer and bigger
        + min(hot, 15)               # drama / click words, capped
        + max(0, 12 - hours_old) / 2 # freshness bonus for the last 12 hours
    )
    headline = max(group, key=lambda it: (it["tier"] == 1, len(it["title"])))["title"]
    return {
        "headline": headline,
        "score": round(value, 1),
        "outlets": len(publishers),
        "tier1_outlets": sorted(tier1),
        "verified": bool(tier1),     # the source rule: no tier 1 outlet = not publishable
        "newest": newest,
        "items": sorted(group, key=lambda it: it["tier"]),
    }


def write_summary(topics: list[dict], n_items: int) -> None:
    lines = [
        f"## 🏀 NBA Rumors: {len(topics)} topics from {n_items} headlines",
        "",
        "| # | Score | Outlets | Verified | Topic |",
        "|---|---|---|---|---|",
    ]
    for i, t in enumerate(topics[:20], 1):
        mark = "✅" if t["verified"] else "⚠️"
        lines.append(f"| {i} | {t['score']} | {t['outlets']} | {mark} | {t['headline']} |")
    text = "\n".join(lines)
    print(text)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    items = fetch_all()
    topics = sorted((score(g) for g in cluster(items)), key=lambda t: t["score"], reverse=True)
    (DATA / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    (DATA / "topics.json").write_text(json.dumps(topics, indent=2), encoding="utf-8")
    write_summary(topics, len(items))
    if not items:
        sys.exit("[!] No headlines collected. Check the feeds.")


if __name__ == "__main__":
    main()

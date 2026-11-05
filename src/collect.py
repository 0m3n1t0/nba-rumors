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
    "reportedly": 2, "shocking": 2, "blockbuster": 5,
}

# Routine in-game notes ("X exits to locker room") are not stories.
ROUTINE = re.compile(
    r"\b(exits?|heads?|leaves?|goes|went|returns?) (to|for|from) (the )?locker room\b"
    r"|\b(questionable|probable|doubtful) (to return|for)\b|\bnot listed on injury report\b",
    re.I,
)
# Speculation and filler ("predicted to trade", "trade idea") is not news.
SPECULATION = re.compile(
    r"\b(predicted|prediction|trade idea|proposal|mock|could trade|should trade|"
    r"could part|could land|ideal trade|dream trade|hypothetical|ranking every)\b",
    re.I,
)
# Overlapping pairs of capitalized words, so Title Case Headlines still match names.
NAME = re.compile(r"(?=\b([A-Z][a-z]+(?:[-'][A-Za-z]+)?) ([A-Z][a-z]+(?:[-'][A-Za-z]+)?)\b)")
NOT_NAMES = {"Trade Rumors", "Free Agency", "Trade Deadline", "Locker Room", "Season Debut",
             "Golden State", "New York", "Los Angeles", "San Antonio", "Oklahoma City",
             "New Orleans", "Trail Blazers", "Breaking News", "Injury Report"}

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


# Ordinary headline words. A "name" containing one of these is not a person.
GENERIC = set("""
nba rumors rumor trade trades traded could would should make makes massive contract decision
key assets roster upgrade grow grows team teams star stars news season debut insider report
reports update updates injury injuries free agency agent deadline big huge major new latest
breaking final first last top best worst game games win wins loss lose loses night today week
deal deals sign signs signed waive waived buyout extension max offer offers interest pursuit
proposal idea predicted major league draft pick picks coach coaches front office owner fans
receive receives scary obvious problem possibilities involving motivated agree reveal reveals
level stance market path part young center guard forward veteran champion all nine time
lakers celtics warriors bucks bulls hornets nuggets cavaliers rockets heat knicks nets suns
clippers mavericks spurs thunder jazz kings pistons pacers hawks magic raptors wizards grizzlies
pelicans timberwolves blazers trail sixers 76ers
""".split())


def names(text: str) -> set[str]:
    """Player / person names in a headline ("Kon Knueppel", "Nikola Jokic")."""
    found = set()
    for first, last in NAME.findall(text):
        if first.lower() in GENERIC or last.lower() in GENERIC:
            continue
        if first.lower() in STOPWORDS or last.lower() in STOPWORDS:
            continue
        found.add(f"{first} {last}")
    return found - NOT_NAMES


def cluster(items: list[dict], threshold: float = 0.3) -> list[list[dict]]:
    """Group headlines about the same story.

    Two headlines join when they share a person's name (same player, same day),
    or when their words overlap strongly.
    """
    groups: list[dict] = []
    for it in items:
        tk = tokens(it["title"])
        nm = names(it["title"])
        if not tk:
            continue
        best, best_sim = None, 0.0
        for g in groups:
            sim = len(tk & g["tokens"]) / len(tk | g["tokens"])
            if nm & g["names"] and len(tk & g["tokens"]) >= 2:
                sim += 0.3
            if sim > best_sim:
                best, best_sim = g, sim
        if best and best_sim >= threshold:
            best["tokens"].update(tk)
            best["names"].update(nm)
            best["items"].append(it)
        else:
            groups.append({"tokens": set(tk), "names": set(nm), "items": [it]})
    return [g["items"] for g in groups]


def score(group: list[dict]) -> dict:
    publishers = {it["publisher"].lower() for it in group}
    tier1 = {it["publisher"] for it in group if it["tier"] == 1}
    text = " ".join(it["title"].lower() for it in group)

    hot = sum(w for word, w in HOT_WORDS.items() if re.search(rf"\b{re.escape(word)}\b", text))
    routine = all(ROUTINE.search(it["title"]) for it in group)
    speculative = all(SPECULATION.search(it["title"]) for it in group)
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
    if routine:
        value *= 0.3   # in-game notes: keep, but push far down
    if speculative:
        value *= 0.5   # opinion / prediction pieces
    headline = max(group, key=lambda it: (it["tier"] == 1, len(it["title"])))["title"]
    return {
        "headline": headline,
        "score": round(value, 1),
        "outlets": len(publishers),
        "tier1_outlets": sorted(tier1),
        "verified": bool(tier1) and not speculative,  # source rule: needs a tier 1 outlet
        "kind": "routine" if routine else "speculation" if speculative else "story",
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

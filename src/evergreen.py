"""B20 / C4: historical beefs for weak days (owner's plan, 2026-11-11).

When the day has fewer than SHORTS_PER_RUN strong stories (viral score >= 60), the empty slot
is filled with a famous NBA beef from the bank below, but ONLY one that is back in the news:
at least FRESH_MIN articles in the last FRESH_DAYS days name both people (a new podcast, an
interview, an anniversary). So the Short is about an old feud with a fresh reason, never a
random history lesson. A beef is used at most once every REUSE_DAYS days.

Sources are what every story uses: the recent articles (read in full by script.py) and the
Wikipedia article on the feud (read through Wikimedia's API with our token). The bank holds
only NAMES and a neutral label; every fact, date and quote comes from those sources.

The bank is deliberately plain data: add a line to add a beef, nothing else changes.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USED = ROOT / "data" / "history" / "evergreen_used.json"   # kept in the private state repo
GOOGLE = "https://news.google.com/rss/search?q={q}+when:{days}d&hl=en-US&gl=US&ceid=US:en"
FRESH_DAYS = 30
FRESH_MIN = 2          # articles naming both people in the last FRESH_DAYS days
REUSE_DAYS = 90
# B20 step 2a: an article ABOUT the two of them (what one says of the other, the history, the
# feud), not one that only names both ("Shai threatens Durant and Westbrook's record").
ABOUT_THEM = re.compile(
    r"\b(says?|said|recalls?|remembers?|reveals?|revealed|responds?|fires? back|admits?|explains?|"
    r"opens? up|claims?|blasts?|rips?|slams?|calls? out|praises?|defends?|apologi[sz]es?|"
    r"feud|beef|rivalry|rift|relationship|friendship|fallout|falling out|tension|clash|"
    r"history|reunion|regrets?|story|stories|truth|why|on (?:his|their|the) relationship)\b", re.I)


def about_them(title: str) -> bool:
    return bool(ABOUT_THEM.search(title or ""))

# (person A, person B, neutral label used as the story's working headline)
BANK = [
    ("Kobe Bryant", "Shaquille O'Neal", "the Lakers feud between Kobe Bryant and Shaquille O'Neal"),
    ("Michael Jordan", "Isiah Thomas", "the Michael Jordan and Isiah Thomas feud"),
    ("Kevin Durant", "Russell Westbrook", "Kevin Durant and Russell Westbrook after Oklahoma City"),
    ("Draymond Green", "Jordan Poole", "the Draymond Green punch on Jordan Poole"),
    ("Draymond Green", "Kevin Durant", "the Draymond Green and Kevin Durant argument in Golden State"),
    ("LeBron James", "Paul Pierce", "the LeBron James and Paul Pierce rivalry"),
    ("Kyrie Irving", "LeBron James", "Kyrie Irving leaving LeBron James in Cleveland"),
    ("Dwight Howard", "Kobe Bryant", "Dwight Howard and Kobe Bryant on the Lakers"),
    ("Jimmy Butler", "Karl-Anthony Towns", "Jimmy Butler's practice blowup in Minnesota"),
    ("Kevin Garnett", "Carmelo Anthony", "the Kevin Garnett and Carmelo Anthony clash"),
    ("Dennis Rodman", "Karl Malone", "Dennis Rodman and Karl Malone in the Finals"),
    ("Reggie Miller", "Spike Lee", "Reggie Miller and Spike Lee at Madison Square Garden"),
    ("Magic Johnson", "Isiah Thomas", "the Magic Johnson and Isiah Thomas friendship that broke"),
    ("Larry Bird", "Magic Johnson", "the Larry Bird and Magic Johnson rivalry"),
    ("Kawhi Leonard", "San Antonio Spurs", "Kawhi Leonard's exit from the Spurs"),
    ("James Harden", "Daryl Morey", "James Harden and Daryl Morey in Philadelphia"),
    ("Ben Simmons", "Joel Embiid", "Ben Simmons and Joel Embiid in Philadelphia"),
    ("Dillon Brooks", "LeBron James", "Dillon Brooks calling out LeBron James"),
    ("Ja Morant", "Jordan Poole", "Ja Morant and Jordan Poole trash talk"),
    ("Patrick Beverley", "Chris Paul", "Patrick Beverley and Chris Paul"),
    ("Kendrick Perkins", "Kevin Durant", "Kendrick Perkins and Kevin Durant"),
    ("Charles Barkley", "Michael Jordan", "the Charles Barkley and Michael Jordan falling out"),
    ("Stephen A. Smith", "LeBron James", "Stephen A. Smith and LeBron James"),
    ("Joel Embiid", "Karl-Anthony Towns", "the Joel Embiid and Karl-Anthony Towns rivalry"),
    ("Trae Young", "New York Knicks", "Trae Young and the Knicks crowd"),
    ("Rajon Rondo", "Chris Paul", "the Rajon Rondo and Chris Paul feud"),
    ("Kevin Durant", "Kendrick Perkins", "the Kevin Durant and Kendrick Perkins feud"),
    ("Draymond Green", "Rudy Gobert", "the Draymond Green chokehold on Rudy Gobert"),
    ("Luka Doncic", "Dallas Mavericks", "the Luka Doncic trade from Dallas"),
    ("Anthony Davis", "New Orleans Pelicans", "Anthony Davis forcing his way out of New Orleans"),
]


def fold(t: str) -> str:
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(ch)).lower()


def used() -> dict:
    try:
        return json.loads(USED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def mark_used(key: str, now: dt.datetime | None = None) -> None:
    data = used()
    data[key] = (now or dt.datetime.now(dt.timezone.utc)).date().isoformat()
    USED.parent.mkdir(parents=True, exist_ok=True)
    USED.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")


def key_of(a: str, b: str) -> str:
    return " vs ".join(sorted([a, b]))


def recently_used(key: str, now: dt.datetime | None = None) -> bool:
    day = used().get(key)
    if not day:
        return False
    now = now or dt.datetime.now(dt.timezone.utc)
    return (now.date() - dt.date.fromisoformat(day)).days < REUSE_DAYS


def names_both(text: str, a: str, b: str) -> bool:
    """Both people (by surname, or the team's nickname) are in the headline."""
    t = fold(text)
    return all(fold(x).split()[-1] in t for x in (a, b))


def fresh_news(a: str, b: str, tier1: tuple[str, ...] = ()) -> list[dict]:
    """Articles of the last FRESH_DAYS days that name both, as story items (title, link,
    publisher, tier) the script stage already knows how to read."""
    import feedparser
    q = urllib.parse.quote_plus(f'"{a}" "{b}"')
    try:
        parsed = feedparser.parse(GOOGLE.format(q=q, days=FRESH_DAYS),
                                  agent="NBARumorsPipeline/1.0 (https://github.com/0m3n1t0/nba-rumors)")
    except Exception as exc:   # one bad search never stops the run
        print(f"[!] evergreen search failed for {a} / {b}: {exc}")
        return []
    out, seen = [], set()
    for e in parsed.entries:
        title, link = (e.get("title") or "").strip(), e.get("link") or ""
        if not title or not link:
            continue
        publisher = ((e.get("source") or {}).get("title")
                     or (title.rsplit(" - ", 1)[-1] if " - " in title else "Unknown"))
        if " - " in title:
            title = title.rsplit(" - ", 1)[0].strip()
        if not names_both(title, a, b) or fold(title) in seen:
            continue
        seen.add(fold(title))
        tier = 1 if any(p in publisher.lower() for p in tier1) else 2
        out.append({"title": title, "link": link, "publisher": publisher, "tier": tier, "summary": "",
                    "about": about_them(title)})
    out.sort(key=lambda it: not it["about"])      # articles about the two of them first (stable)
    return out


def wikipedia_item(a: str, b: str) -> dict | None:
    """The Wikipedia article that best covers the feud (Wikimedia search, with our token)."""
    import wiki_http
    q = urllib.parse.urlencode({"action": "query", "list": "search", "format": "json", "srlimit": 1,
                                "srsearch": f"{a} {b} feud OR rivalry OR conflict"})
    try:
        hits = json.loads(wiki_http.fetch("https://en.wikipedia.org/w/api.php?" + q,
                                          "NBARumorsPipeline/1.0 (https://github.com/0m3n1t0/nba-rumors)"))
        title = ((hits.get("query") or {}).get("search") or [{}])[0].get("title")
    except Exception as exc:
        print(f"[!] Wikipedia search failed for {a} / {b}: {exc}")
        return None
    if not title:
        return None
    return {"title": f"{title} (Wikipedia)", "link": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "publisher": "Wikipedia", "tier": 1, "summary": ""}   # the record of an OLD feud: trusted for its dates


def candidates(tier1: tuple[str, ...] = (), now: dt.datetime | None = None, limit: int = 3) -> list[dict]:
    """Beefs back in the news, most mentioned first, as ready-made topics:
    {"key", "headline", "items", "why", "people"}. Searches stop after `limit` found."""
    import random
    found = []
    order = list(BANK)
    random.Random((now or dt.datetime.now(dt.timezone.utc)).date().toordinal()).shuffle(order)
    order.sort(key=lambda x: used().get(key_of(x[0], x[1]), ""))   # never used first, then oldest
    for a, b, label in order:
        key = key_of(a, b)
        if recently_used(key, now):
            continue
        news = fresh_news(a, b, tier1)
        if len(news) < FRESH_MIN or not any(it.get("about") for it in news):
            continue      # not back in the news, or only named in passing
        found.append({"key": key, "people": [a, b], "news": news, "label": label})
        if len(found) >= limit:
            break
    found.sort(key=lambda x: (-sum(bool(it.get("about")) for it in x["news"]), -len(x["news"])))
    out = []
    for f in found:
        wiki = wikipedia_item(*f["people"])
        newest = f["news"][0]["title"]
        out.append({
            "key": f["key"], "people": f["people"],
            "headline": f"{newest} (back in the news: {f['label']})",
            "items": f["news"] + ([wiki] if wiki else []),
            "why": (f"HISTORIC BEEF back in the news. The feud itself is OLD ({f['label']}); the fresh "
                    f"reason is: \"{newest}\". Open on the fresh reason, then tell the old feud with its "
                    "real dates from the sources (\"back in 2004...\"). NEVER present the old events as "
                    "new, and give every date only as the sources give it."),
        })
    return out

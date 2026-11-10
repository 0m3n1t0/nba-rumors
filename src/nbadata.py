"""Official NBA results (balldontlie API, free plan: teams and games, 5 requests a minute).

Used for ONE thing: a claim whose numbers are a final score ("a 124 to 114 win over the Hawks")
or a team's record ("the Lakers are 10-2") is checked against the league's real results. When
EVERY number in the claim matches, the claim is marked as confirmed by the official results.

It only ever confirms. It never downgrades or blocks a claim, and without the key (or when the
API is down) nothing changes: the claim keeps the status the source check gave it.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request

API = "https://api.balldontlie.io/v1/"
KEY = os.environ.get("BALLDONTLIE_API_KEY", "")
GAP = 12.5            # seconds between requests: the free plan allows 5 a minute
LOG: list[str] = []   # what happened, for the Summary (never the key)

# nicknames people use for the official team names
ALIASES = {"sixers": "76ers", "cavs": "cavaliers", "mavs": "mavericks", "wolves": "timberwolves",
           "blazers": "trail blazers", "dubs": "warriors", "knicks": "knicks", "nuggs": "nuggets"}
SCORE = re.compile(r"\b(\d{2,3})\s*(?:-|–|to)\s*(\d{2,3})\b")
RECORD = re.compile(r"\b(\d{1,2})\s*-\s*(\d{1,2})\b")
NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")

_last = [0.0]
_cache: dict[str, object] = {}


def _get(path: str, params: dict) -> dict:
    wait = GAP - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    url = API + path + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "nba-rumors-pipeline/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    finally:
        _last[0] = time.time()


def teams() -> list[dict]:
    if "teams" not in _cache:
        _cache["teams"] = [t for t in _get("teams", {"per_page": 100}).get("data", [])
                           if (t.get("conference") or "").strip()]      # the 30 NBA teams only
    return _cache["teams"]  # type: ignore[return-value]


def season_of(day: dt.date) -> int:
    return day.year if day.month >= 9 else day.year - 1


def recent_games(today: dt.date, days: int = 10) -> list[dict]:
    key = f"recent{today}"
    if key not in _cache:
        data = _get("games", {"start_date": str(today - dt.timedelta(days=days)), "end_date": str(today),
                              "per_page": 100})
        _cache[key] = [g for g in data.get("data", []) if str(g.get("status", "")).lower().startswith("final")]
    return _cache[key]  # type: ignore[return-value]


def team_games(team_id: int, today: dt.date) -> list[dict]:
    key = f"team{team_id}{today}"
    if key not in _cache:
        data = _get("games", {"seasons[]": season_of(today), "team_ids[]": team_id, "per_page": 100,
                              "end_date": str(today)})
        _cache[key] = [g for g in data.get("data", [])
                       if str(g.get("status", "")).lower().startswith("final") and not g.get("postseason")]
    return _cache[key]  # type: ignore[return-value]


def teams_in(text: str, all_teams: list[dict]) -> list[dict]:
    low = text.lower()
    for nick, official in ALIASES.items():
        low = re.sub(rf"\b{nick}\b", official, low)
    return [t for t in all_teams if re.search(rf"\b{re.escape(t['name'].lower())}\b", low)]


def record(team_id: int, games: list[dict]) -> tuple[int, int]:
    w = l = 0
    for g in games:
        home = g["home_team"]["id"] == team_id
        mine, theirs = ((g["home_team_score"], g["visitor_team_score"]) if home
                        else (g["visitor_team_score"], g["home_team_score"]))
        if mine > theirs:
            w += 1
        elif theirs > mine:
            l += 1
    return w, l


def confirm(text: str, today: dt.date | None = None) -> str:
    """'' or why the claim is confirmed by the official results (all its numbers matched)."""
    today = today or dt.date.today()
    nums = NUMBER.findall(text)
    if not nums:
        return ""
    found = teams_in(text, teams())
    if not found:
        return ""
    covered: list[str] = []
    why = []
    for a, b in SCORE.findall(text):
        if int(a) < 60 or int(b) < 60:
            continue
        pair = {int(a), int(b)}
        ids = {t["id"] for t in found}
        hit = [g for g in recent_games(today) if {g["home_team_score"], g["visitor_team_score"]} == pair
               and {g["home_team"]["id"], g["visitor_team"]["id"]} & ids]
        if not hit:
            return ""                     # a score that does not match: confirm nothing
        g = hit[0]
        covered += [a, b]
        why.append(f"{g['visitor_team']['name']} {g['visitor_team_score']}-{g['home_team_score']} "
                   f"{g['home_team']['name']} ({g['date'][:10]})")
    for a, b in RECORD.findall(text):
        if int(a) >= 60 or int(b) >= 60 or len(found) != 1:
            continue
        w, l = record(found[0]["id"], team_games(found[0]["id"], today))
        if (w, l) != (int(a), int(b)):
            return ""                     # a record that does not match: confirm nothing
        covered += [a, b]
        why.append(f"{found[0]['name']} {w}-{l}")
    if not why or sorted(covered) != sorted(nums):   # every number must be a checked score/record
        return ""
    return "official NBA results: " + "; ".join(why)


def annotate(claims: list[dict], today: dt.date | None = None) -> int:
    """Mark the claims the official results confirm. Returns how many. Never raises."""
    if not KEY:
        return 0
    n = 0
    for c in claims:
        if not isinstance(c, dict):
            continue
        try:
            why = confirm(c.get("text", ""), today)
        except Exception as exc:          # the API is down or changed: nothing changes
            LOG.append(f"balldontlie unavailable ({type(exc).__name__}): claims keep their status")
            return n
        if why:
            c["official_result"] = why
            n += 1
    return n

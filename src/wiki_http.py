"""Polite, authenticated requests to Wikimedia (Wikipedia, Commons, Wikidata).

Why: since 2026 Wikimedia limits anonymous API calls PER IP address. A shared cloud IP
(GitHub's runners, Claude's own session) can be over that limit before we send a single
request, so Wikimedia answers "429 Too Many Requests". Calls made with a personal access token
are counted per ACCOUNT instead, with a much higher limit.

  * WIKIMEDIA_TOKEN (a GitHub Secret, never in code or chat): an OAuth 2.0 "owner-only" access
    token from meta.wikimedia.org. When it is set, API calls carry "Authorization: Bearer ...".
    Without it everything works exactly as before (anonymous).
  * A token Wikimedia refuses (401/403) is dropped for the rest of the run and the call is
    repeated anonymously, so a bad or revoked token can never stop the pipeline.
  * 429/503 from Wikimedia: wait as long as Wikimedia asks (Retry-After, at most 30 s) and try
    again, twice at most, with a total waiting budget per run so a blocked network can never
    make a run hang.
  * Every other website is fetched exactly as before: one plain request, no retries.
"""
from __future__ import annotations

import os
import re
import time
import urllib.error
import urllib.request

WIKI_HOST = re.compile(r"^https://([a-z0-9-]+\.)*(wikipedia|wikimedia|wikidata)\.org/", re.I)
API_PATHS = ("/w/api.php", "/api/rest_v1/", "/w/rest.php/")   # the token goes only to the APIs
TOKEN = [os.environ.get("WIKIMEDIA_TOKEN", "").strip()]
MAX_WAIT = 30.0          # never wait longer than this for one answer
WAIT_BUDGET = [90.0]     # seconds of waiting per run, in total
TRIES = 3
_sleep = time.sleep      # tests replace it


def is_wiki(url: str) -> bool:
    return bool(WIKI_HOST.match(url or ""))


def headers(url: str, ua: str) -> dict:
    h = {"User-Agent": ua}
    if TOKEN[0] and is_wiki(url) and any(p in url for p in API_PATHS):
        h["Authorization"] = "Bearer " + TOKEN[0]
    return h


def _retry_after(exc: urllib.error.HTTPError) -> float:
    try:
        return max(1.0, float((exc.headers or {}).get("Retry-After", "5")))
    except (TypeError, ValueError):
        return 5.0


def fetch(url: str, ua: str, timeout: int = 30) -> bytes:
    if not is_wiki(url):
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    for attempt in range(TRIES):
        h = headers(url, ua)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = attempt == TRIES - 1
            if exc.code in (401, 403) and "Authorization" in h:
                print(f"[!] Wikimedia did not accept WIKIMEDIA_TOKEN (HTTP {exc.code}); "
                      "continuing without it")
                TOKEN[0] = ""
                if not last:
                    continue
            if exc.code in (429, 503) and not last:
                wait = min(_retry_after(exc), MAX_WAIT)
                if wait <= WAIT_BUDGET[0]:
                    WAIT_BUDGET[0] -= wait
                    _sleep(wait)
                    continue
            raise
    raise RuntimeError("unreachable")

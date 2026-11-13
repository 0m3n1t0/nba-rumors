"""Regression tests for the 2026-11-11 fixes (PROJECT.md section 6). They protect what works:
each test is a real case from a real run that once went wrong. Offline and fast: no voice
engine, no ffmpeg, no network (every outside call is replaced by a fake answer), so they run in
the "Safety tests" step before anything is installed or made.

  1. voice: quote marks never lower the "words heard" count; the best take is kept
  2. footage: a clip that is not of the story's person must prove it is the NBA
  3. namesakes: a different birth year on the file = another person
  4. the player's own Commons category: Wikidata's name, the "by year" level, no false drop
  5. empty beats: no unjudged stock clip; the gate holds any unjudged clip
  6. script: hook replayed in a beat, repeated beat, weak payoff -> one safe repair pass
  7. quotes in single quotes are checked against the sources too
  8. yt-edit: only real silence over 0.7 s is shortened, natural pauses never
  9. end card: after the voice's last real sound, never over it
 10. the public run page is short; the full report and working data are kept privately
 11. the weekly plan and competitor scan come from the private repository (not this public one)
 12. one photo in two crops is ONE picture: never shown twice in a Short
 13. today's uniform: the player's current team (Wikidata) decides which of his photos come first
 14. Wikimedia: the account token goes only to Wikimedia's APIs, a refused token is dropped, a 429
     is waited out (within a budget), and every other site is fetched exactly as before
 15. one game per Short at most 3 times while other fitting photos of the person exist (run
     43011651547 showed 9 of 13 photos from "Celtics at Wizards", 15 Dec 2024)
 16. the story's own article is read first; when it cannot be read, the script is told not to
     promise what it says (run 43027675858: "Brown explains why..." never said why)
 17. must-know context: who each person is in the story, who went where in a trade, who won the
     game, roles exactly as the sources give them (run 43027675858)
 18. her analysis is her own: a payoff that only agrees with an outlet ("...and I think that's
     right") goes to the repair pass (run 43027675858)
 19. the hook pick sees the whole Short and the names fans know: no question the Short never
     answers, no line built on a name nobody knows (run 43027675858)
 20. details (venue, crowd, someone's job) only as the sources give them: a hook with one goes
     back, the repair pass fixes the beats, the gate holds what is left (run 43011651547)
 21. length: 45-65 words after the hook, up to 72 only when must-know context or her own reason
     needs it (owner's choice "გ"); the longest Short still counts as ready
 23. photos: a photo taken before his NBA career ("PRE-NBA", run 43066151290: Brown at a 2015
     high school game) goes last and Claude is told; off-court events score low; a Commons
     derivative ("File:X.jpg ... derivative work") is the same picture as X
 25. TWO VERSIONS (C1): the editor names where two accounts clash, the writer puts both sides
     in (attributed), the critic checks it; never invented
 26. RUMOR LABELS (C2): an anonymous report, a rumor or a speculation is voiced as such in its
     own sentence; a fact stated plainly is never forced to sound like a rumor
 27. PODCASTS (C3): two Google News searches for what was said on NBA podcasts and shows
 28. HISTORIC BEEFS (B20/C4): a weak day's empty slot gets a famous beef that is back in the
     news (2+ articles in 30 days), never one used in the last 90 days, told as OLD
 29. stale Wikidata (run 43080115985): an undated "current" team is not trusted; college / high
     school photos are PRE-NBA from their own text; a former role is said as former
 30. Openverse kept: a good search is kept 14 days per person; a failed one uses it
 31. sentences never split at an initial ("Stephen A. smart?" is one question; run 43088629255
     held a good Short for "repeating" because of it)
 32. one feud, one Short in 48 hours (run 43088629255: three Shorts on Brown and Tatum in a day),
     unless a major turn or a new voice leads the story
 33. run 43199348111: a meaning word ("on-screen") is never dropped; the same Commons file from
     two sources is one picture; Openverse needs the full name as one phrase; the description
     links the article itself, not a Google News redirect
 34. the hook is a STATED shock (owner, 2026-11-12): statements rank first, a question loses
     points; name + shock in the first 8 words; a rumor hook opens with its source
 35. a historic beef follows the 48-hour feud rule too (also against this run's Shorts)
 36. every photo of the story's people is tagged once (kept), each beat gets a shortlist that fits
     its line; never more than 3 photos of one scene; burst shots are one picture; political
     photos only when the line is about them
 37. every outlet's report of the same story is read (up to MAX_ARTICLES); "45.0" counts as 45
 38. the chosen hook with a detail the sources word differently is rewritten in their words, not dropped
 39. where a feud stands now: "silence" while a source tells of contact since -> repair, else REVIEW
 40. a broken tag answer keeps its good entries; an untagged photo never fills when the person has tags
 41. a beat that replays the hook in other order, and "that stretch" never said -> repair
 42. a fresh, spreading fight just under the line (55+) is made before an old feud fills the run
 43. bold but true: the chosen hook is read against the sources; an overstated one gets its boldest true line
 44. one event (All-Star 2022...) counts like one scene; college photos marked PRE-NBA; small figures
     and other eras/teams kept for when the line asks for them
 45. the full reports never reach the public logs or run summaries (audit, 2026-11-13)
 46. captions and voice split sentences like the script checks (initials); Pillow 14 ready
 47. another man with his surname and a look-alike first name (Isaiah for Isiah Thomas) is never
     his photo (run 43353547001)
 48. a corrected quote is only the quote: never the words glued before it ("hurt Luka Doncic:"),
     never "said Barkley", never a cut-off source (run 43395656602)
 49. final laws on the finished Short, whatever made the mistake: a quote must be inside quote
     marks in a source; no glued "Doncic:Not" text; no photo in the jersey of a team its man
     never played for (media leaves it out, the gate holds it if it is still there)
 50. each Short's source texts are kept with the run, and replay.py runs today's checks on every
     kept run (a change is tried on real Shorts before it reaches main)
 51. (changed 2026-11-14 by his rule) the hook must be scandalous, intriguing and effective; the
     day's news is secondary: no line wins only because it says the news (run 43353547001 case kept)
 52. a question is never the payoff's answer: "Why was Luka even back in up 20? I'd blame that."
     goes to the repair pass (run 43395656602)
 53. an independent final read (final_read.py): a clear error with real evidence, or a Short it
     could not read, is held by the gate; an error without real evidence is only a doubt
 54. D16: contact sheets are opened all at once (one step), not one per step: each step re-reads
     everything before it (run 43395656602: a 5-sheet tag call cost 136k tokens); turns logged
 55. no name is used in a function before that function imports it (run 43407418420: render.py
     crashed after making both videos, so the gate never ran)
 56. a photo in the player's OWN Commons category is his, however the title spells his first name
     (run 43407418420: 27 "Dejonte Murray" photos of Dejounte Murray were left out by rule 47)
 57. the final reader's WRONG PICTURE follows the picture rules already agreed: a former team's
     jersey with no team or time in the line, or a teammate on a line about the team, is at
     most a doubt (run 43407418420); each media Claude call is named in the budget (D16)
 58. a fresh story whose own article cannot be read in any copy is skipped before writing and
     the next story is tried; evergreens keep their own rule (run 43407418420)
 59. every Google News search puts "when:1d" first (the podcast search ignored it and gave only
     May items); a silent feed says why in the log and falls back to its outlet through Google
     News (ESPN gave 0 items in every run, HoopsHype's feed answers 402)
 60. the owner's source review: ClutchPoints, Hoops Rumors, SB Nation, Defector, TrueHoop, five
     new searches, seven podcast channels (titles only), r/nba rising as a signal; multi-sport
     feeds keep only NBA items
 61. D22: a photo taken before the DAY his NBA career began (Wikidata, dated to the day) is PRE-NBA
     on every path, Openverse included (the day in the file name counts); the Commons copy of a
     file wins over its Openverse copy; the final read calls a PRE-NBA picture on an NBA line an
     error (run 43446225184: Lendeborg in Michigan #23 on "a 24-year-old rookie")
 62. D23: the jersey law trusts a photo that is HIS (own Commons category, or his first and last
     name in the title): Wikidata had no Nets spell for Kyrie Irving and 12 real photos were lost
 63. D24: the titles are read against the sources too (bold but true): "Curry's two weeks is a
     LIE?" steps behind a true title; every title overstated = the Short is held
 64. D25: the pick prompt names every contact sheet ("beat_0.jpg, beat_0_2.jpg, ..."): Claude
     cannot list the folder and opened them one guess per step (15-19 steps, up to 169k tokens)
 65. D26 (owner): a conflict between popular players/teams weighs slightly more than other drama
     around a popular player: +6 for any conflict, plus up to +4 by star power (0 at 5, 4 at 10)
 67b. (2026-11-14, his answers) hook 8-12 words (3-4 s at 2.8 words a second); MAJOR_TURN without
     plain "trade"; articles read up to 6000 characters; tier 1 + 5 newspapers/broadcasters
 66. who said it, and is it still true: an outlet's conclusion is never given to the insider it
     reports on; an ended fact (a streak) is never said as still running (writer, critic, final read)
 67. D27: a rewritten hook (truth or detail fix) keeps every hook rule: no profanity, the story's
     lead person in the first 8 words; a profane hook never leads (run 43485568700)
 68. D29 (owner): a named beat reporter credited for an on-record quote ("Mitchell told Chris
     Fedor of Cleveland.com") is a reliable source: no "provenance unclear" hold, no RUMOR downgrade
 69. D28: unjudged top-up photos keep the team order (today's team / no team first, a former
     team after, never dropped): Mitchell's Jazz photos had filled Cavs lines
 70. D30 (owner): top-ups by relevance - photos and clips Claude scored 8+ for the beat first,
     best first; an unscored one only after them, only if he is seen (face or from behind) AND
     the jersey fits the line (a named team allows that team; a time only: today's team)
 24. Openverse: a 504 (a search new to it) is retried 6 times over ~2 minutes (runs 43027675858,
     43066151290: three quick tries, every search lost)
 22. five articles, read with no time limit (only a site silent for 5 min is left, after a second
     try), Claude's answer up to 20 min (owner, 2026-11-11); questions: no
     middle beat re-asks the hook's question, the closing question loops to the hook and brings
     in no one the Short never introduced (run 43066151290)
 (12 also: a crop named after the person, "...-036 (White).jpg", is the same picture, run 43027675858)
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import types
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import os  # noqa: E402
# the tests must never write the pipeline's real history (it is saved to the private repo)
os.environ.setdefault("NBA_OV_CACHE", str(Path(tempfile.gettempdir()) / "nba_test_openverse_cache.json"))
os.environ.setdefault("NBA_TAG_CACHE", str(Path(tempfile.gettempdir()) / "nba_test_photo_tags.json"))

import numpy as np  # noqa: E402  (in requirements.txt)

# tts.py imports soundfile (installed later, with the voice engine): a stand-in is enough here,
# the tests never write real audio
if "soundfile" not in sys.modules:
    try:
        import soundfile  # noqa: F401
    except ImportError:
        _sf = types.ModuleType("soundfile")
        _sf.write = lambda path, data, rate: Path(path).write_text("wav")
        sys.modules["soundfile"] = _sf

# The Luka Short of run 42877530241: what Whisper heard, and the script
LUKA_HEARD = ("Luca Doncic really tell Hawks fans you all wish you would have had me. Atlanta drafted "
              "Luca third, then traded him for Tree Young. Yahoo! Sports reported Luca told Hawks fans, "
              "you all wish you would have had me. One fired back, we had you. A fan gave in, I wish we "
              "did, I do. Luca dropped 32 in the win. That fan was the honest one. So who's right, him, "
              "or the one who never wanted Luca?")
LUKA_HOOK = "Did Luka Doncic really tell Hawks fans 'You all wish you would have had me'?"
LUKA_BEATS = [
    {"say": "Atlanta drafted Luka third, then traded him for Trae Young.", "on_screen": "Luka",
     "tone": "calm", "role": "context", "stage": "setup"},
    {"say": "Yahoo Sports reported Luka told Hawks fans, 'You all wish you would have had me.' "
            "One fired back, 'We had you.'", "on_screen": "Luka", "tone": "tense", "role": "fact",
     "stage": "conflict"},
    {"say": "A fan gave in: 'I wish we did, I do.'", "on_screen": "Hawks fans", "tone": "amused",
     "role": "reaction", "stage": "twist"},
    {"say": "Luka dropped 32 in the win.", "on_screen": "Luka", "tone": "calm", "role": "analysis",
     "stage": "payoff"},
    {"say": "That fan was the honest one. So who's right: him, or the one who never wanted Luka?",
     "on_screen": "Luka", "tone": "amused", "role": "question", "stage": "exit"},
]


class Voice(unittest.TestCase):
    """1. The voice check (tts.py)."""

    def test_quote_marks_do_not_count_as_words(self):
        import tts
        self.assertEqual(tts.tokens("'You all wish you would have had me.'"),
                         ["you", "all", "wish", "you", "would", "have", "had", "me"])
        self.assertEqual(tts.tokens("who's Giannis' 'I"), ["who's", "giannis", "i"])
        words = [{"word": w, "start": 0.0, "end": 0.0} for w in LUKA_HEARD.split()]
        text = " ".join([LUKA_HOOK] + [b["say"] for b in LUKA_BEATS])
        # was 59% before the fix (the voice was fine: the count was wrong)
        self.assertGreaterEqual(tts.coverage(text, words), 0.85)

    def _voice(self, plan: dict, performer: bool = True):
        """tts.main() with fake engines: plan = {(engine, seed): words heard share, or "boom"}."""
        import tts
        saved = {k: getattr(tts, k) for k in ("SCRIPTS", "AUDIO", "load_pipeline", "Performer", "speak",
                                               "finish", "word_times", "coverage", "duration_of")}
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "short_1.json").write_text(json.dumps(
                {"n": 1, "headline": "h", "ready": True, "hook": {"text": "Did Luka say it?"},
                 "beats": [{"say": "He did.", "tone": "calm"}]}))
            tts.SCRIPTS, tts.AUDIO = tmp / "scripts", tmp / "audio"
            calls = []

            class Fake:
                rate = 24000

                def __init__(self, *a):
                    if not performer:
                        raise RuntimeError("no chatterbox")

                def speak_parts(self, parts, seed):
                    calls.append(("chatterbox", seed))
                    if plan[("chatterbox", seed)] == "boom":
                        raise RuntimeError("boom")
                    return np.zeros(10, dtype=np.float32)
                speak = speak_parts

            def kokoro(*a):
                calls.append(("kokoro", 0))
                if plan[("kokoro", 0)] == "boom":
                    raise RuntimeError("boom")
                return np.zeros(10, dtype=np.float32)

            def heard(text, words):
                eng, seed = words[0]["word"].split(".take_")[1][:-4].rsplit("_", 1)
                return plan[(eng, int(seed))]
            tts.load_pipeline = lambda: (None, None)
            tts.Performer, tts.speak = Fake, kokoro
            tts.finish = lambda wav, mp3, tempo=1.0: Path(mp3).write_text(Path(mp3).name)
            tts.word_times = lambda mp3: [{"word": Path(mp3).read_text(), "start": 0.0, "end": 1.0}]
            tts.coverage, tts.duration_of = heard, (lambda mp3: 10.0)
            tts.main()
            timing = tmp / "audio" / "short_1.timing.json"
            files = sorted(p.name for p in (tmp / "audio").iterdir())
            return (json.loads(timing.read_text()) if timing.exists() else None), files, calls
        finally:
            for k, v in saved.items():
                setattr(tts, k, v)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_best_take_is_kept(self):
        import tts
        s = tts.CONFIG["chatterbox"]["seed"]
        # both Chatterbox takes just under the bar, Kokoro worse: Chatterbox stays (the old code
        # always took Kokoro)
        res, files, _ = self._voice({("chatterbox", s): .83, ("chatterbox", s + 1): .82, ("kokoro", 0): .59})
        self.assertEqual((res["engine"], res["heard"]), ("chatterbox", .83))
        self.assertEqual(files, ["short_1.mp3", "short_1.timing.json"])      # no take left behind
        # a good first take: nothing else is tried
        res, _, calls = self._voice({("chatterbox", s): .95, ("chatterbox", s + 1): .1, ("kokoro", 0): .1})
        self.assertEqual(calls, [("chatterbox", s)])
        # Kokoro really better: Kokoro
        res, _, _ = self._voice({("chatterbox", s): .70, ("chatterbox", s + 1): .75, ("kokoro", 0): .90})
        self.assertEqual(res["engine"], "kokoro")
        # a tie: Chatterbox (the channel's voice)
        res, _, _ = self._voice({("chatterbox", s): .80, ("chatterbox", s + 1): .80, ("kokoro", 0): .80})
        self.assertEqual(res["engine"], "chatterbox")
        # every engine fails: no narration for this Short, nothing left behind
        res, files, _ = self._voice({("chatterbox", s): "boom", ("chatterbox", s + 1): "boom", ("kokoro", 0): "boom"})
        self.assertIsNone(res)
        self.assertEqual(files, [])
        # no Chatterbox at all: Kokoro, as before
        res, _, _ = self._voice({("kokoro", 0): .70}, performer=False)
        self.assertEqual(res["engine"], "kokoro")


def _fake_media_get(wiki: dict, cats: dict, p373: dict, videos: list):
    def get(url, timeout=30):
        if "wikipedia.org" in url:
            return json.dumps(wiki).encode()
        q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
        if "wikidata.org" in url:
            v = p373.get(q.get("entity"))
            return json.dumps({"claims": {"P373": [{"mainsnak": {"datavalue": {"value": v}}}]} if v else {}}).encode()
        if q.get("prop") == "videoinfo":
            return json.dumps({"query": {"pages": {str(i): v for i, v in enumerate(videos)}}}).encode()
        if q.get("list") == "search" or q.get("generator") == "search":
            return json.dumps({"query": {}}).encode()
        files, subs = cats.get(q.get("gcmtitle") or q.get("cmtitle"), ([], []))
        if q.get("list") == "categorymembers":
            return json.dumps({"query": {"categorymembers": [{"title": c} for c in subs]}}).encode()
        return json.dumps({"query": {"pages": {str(i): f for i, f in enumerate(files)}}}).encode()
    return get


def _photo(title: str, desc: str, cats: str = "") -> dict:
    return {"title": title, "imageinfo": [{"mime": "image/jpeg", "width": 1200, "height": 1600, "thumburl": "u",
            "descriptionurl": "https://commons.wikimedia.org/wiki/" + title,
            "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "A"},
                            "ImageDescription": {"value": desc}, "Categories": {"value": cats}}}]}


def _video(title: str, desc: str, cats: str) -> dict:
    return {"title": "File:" + title, "videoinfo": [{"url": "u", "size": 1, "derivatives": [
        {"type": "video/webm", "height": 480, "src": "s"}], "extmetadata": {
        "ImageDescription": {"value": desc}, "Categories": {"value": cats},
        "LicenseShortName": {"value": "CC BY-SA 3.0"}, "Artist": {"value": "own work"},
        "Credit": {"value": "Own work"}, "Duration": {"value": "20"}}}]}


WIKI = {"query": {"redirects": [{"from": "Luka Doncic", "to": "Luka Dončić"},
                                {"from": "Robert Williams", "to": "Robert Williams III"}], "pages": {
    "1": {"title": "Luka Dončić", "pageprops": {"wikibase-shortdesc": "Slovenian basketball player (born 1999)",
                                                "wikibase_item": "Q1"}},
    "2": {"title": "Devin Booker", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1996)",
                                                 "wikibase_item": "Q2"}},
    "3": {"title": "Robert Williams III", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1997)"}},
    "4": {"title": "Bomani Jones", "pageprops": {"wikibase-shortdesc": "American sports journalist"}}}}}
P373 = {"Q1": "Luka Dončić", "Q2": "Devin Booker (basketball, born 1996)"}
CATS = {   # the real shapes found with diagnose.yml on 2026-11-11
    "Category:Luka Dončić": ([], ["Category:Luka Dončić by year"]),
    "Category:Luka Dončić by year": ([], ["Category:Luka Dončić in 2019", "Category:Luka Dončić in 2025",
                                          "Category:Luka Dončić in 2026"]),
    "Category:Luka Dončić in 2026": ([_photo("File:LD 2026.jpg", "Dončić")], []),
    "Category:Luka Dončić in 2025": ([_photo("File:LD 2025.jpg", "Dončić, Lakers")], []),
    "Category:Luka Dončić in 2019": ([_photo("File:LD 2019.jpg", "Dončić")], []),
    "Category:Devin Booker": ([], []),
    "Category:Devin Booker (basketball, born 1996)": ([_photo("File:Booker Suns 2025.jpg", "Booker")], []),
    "Category:Robert Williams": ([_photo("File:RW speech.jpg", "Senator at a hearing")], []),
    "Category:Robert Williams III": ([_photo("File:RWIII.jpg", "Robert Williams III")], []),
}
VIDEOS = [
    _video("13 November 2011 Canberra Capitals game 2204.theora.ogv", "Canberra Capitals game at the AIS Arena.",
           "2011 in basketball|Canberra Capitals|Basketball matches at AIS Arena"),
    _video("Basketball CEO speech - iPhone (Cellular).theora.ogv", "Basketball CEO speech", "Basketball"),
    _video("Boston Celtics warm-up 2019.webm", "Celtics players warming up before a basketball game",
           "Boston Celtics|Basketball videos"),
    _video("WNBA game.webm", "basketball game", "WNBA|Basketball videos"),
    _video("Devin Booker (basketball, born 1991) dunk.webm", "Devin Booker dunk", "Devin Booker (basketball, born 1991)"),
    _video("Devin Booker Suns warm-up.webm", "Devin Booker basketball", "Devin Booker|Phoenix Suns"),
]


class MediaCase(unittest.TestCase):
    """Common set-up: media.py talks to a fake Commons / Wikipedia / Wikidata."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("get", "commons_trusted")}
        self.caches = [media._person_cache, media._birth_year, media._wiki_title, media._wikidata,
                       media._commons_cat, media._vid_cache, media._photo_cache, media.PHOTO_STATS]
        self.backup = [dict(c) for c in self.caches]
        for c in self.caches:
            c.clear()
        media.get = _fake_media_get(WIKI, CATS, P373, VIDEOS)
        media.commons_trusted = lambda meta, title, video=False: True
        media.real_people(["Luka Doncic", "Devin Booker", "Robert Williams", "Bomani Jones"])  # as people() does

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        for c, b in zip(self.caches, self.backup):
            c.clear()
            c.update(b)


class Footage(MediaCase):
    """2 and 3: no women's games, no namesakes."""

    def test_generic_clip_must_prove_nba(self):
        kept = [c["title"] for c in self.m.commons_videos("basketball game")]
        # Canberra Capitals (Australian women's team, "women" written nowhere), a CEO speech and a
        # WNBA game are out; real NBA clips stay
        self.assertEqual(kept, ["Boston Celtics warm-up 2019.webm", "Devin Booker Suns warm-up.webm"])

    def test_namesake_clip_and_photo(self):
        self.m._vid_cache.clear()
        self.assertEqual([c["title"] for c in self.m.commons_videos('"Devin Booker"', "Devin Booker")],
                         ["Devin Booker Suns warm-up.webm"])
        n = self.m.namesake
        self.assertTrue(n("Devin Booker", "Devin Booker (basketball, born 1991) Olimpia Milan Euroleague"))
        self.assertFalse(n("Devin Booker", "Devin Booker (born 1996) Suns"))
        self.assertFalse(n("Devin Booker", "Devin Booker 2023 Phoenix Suns"))      # no year: kept
        self.assertFalse(n("Bomani Jones", "Bomani Jones born 1980"))               # year unknown: kept
        self.assertFalse(n("Luka Doncic", "Luka Dončić and Asel Roberts, 2026"))    # a date is not a birth year

    def test_namesake_needs_no_extra_request(self):
        calls = []

        def down(url, timeout=30):
            calls.append(url)
            raise OSError("down")
        self.m.get = down
        self.assertFalse(self.m.namesake("Jaylen Brown", "Jaylen Brown (born 1990)"))
        self.assertEqual(calls, [])


class Category(MediaCase):
    """4. The player's own Commons category (Luka 0 -> 71 photos, Booker 0 -> 38 in real runs)."""

    def files(self, who: str) -> list[str]:
        self.m.PHOTO_STATS.clear()
        return sorted(f["title"] for f in self.m.category_files(who))

    def test_by_year_and_wikidata(self):
        # Luka: no photo in the category itself, only "by year" -> "in 2025" (two levels down)
        self.assertEqual(self.files("Luka Doncic"), ["File:LD 2019.jpg", "File:LD 2025.jpg", "File:LD 2026.jpg"])
        # Booker: "Category:Devin Booker" is empty; Wikidata names the real one
        self.assertEqual(self.files("Devin Booker"), ["File:Booker Suns 2025.jpg"])
        # a politician's category under the plain name is skipped, and the search goes on
        self.assertEqual(self.files("Robert Williams"), ["File:RWIII.jpg"])

    def test_plain_spelling_still_first(self):
        calls = []
        fake = self.m.get

        def spy(url, timeout=30):
            calls.append(url)
            return fake(url, timeout)
        self.m.get = spy
        self.files("Luka Doncic")
        self.assertIn("Luka+Doncic+%28basketball%29", calls[0])

    def test_wikidata_down_changes_nothing_else(self):
        fake = self.m.get

        def no_wikidata(url, timeout=30):
            if "wikidata.org" in url:
                raise OSError("down")
            return fake(url, timeout)
        self.m.get = no_wikidata
        self.assertEqual(len(self.files("Luka Doncic")), 3)    # found by his Wikipedia name


class EmptyBeats(unittest.TestCase):
    """5. Empty beats and unjudged clips."""

    def test_no_unjudged_stock_clip(self):
        import media
        saved = {k: getattr(media, k) for k in ("pixabay_videos", "download", "person_photos", "picture_hash")}
        asked = []
        folder = media.ROOT / "data" / "_test_fill"
        try:
            media.pixabay_videos = lambda q: asked.append(q) or [
                {"kind": "video", "id": 139533, "url": "u", "title": "basketball, game, fitness", "page": "p",
                 "author": "a", "license": "Pixabay Content License", "source": "Pixabay", "duration": 5}]
            media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            media.person_photos = lambda person, shown: []
            media.picture_hash = lambda p: None
            photo = {"kind": "photo", "file": "data/x.jpg", "page": "ph1", "title": "Luka Dončić 2025.jpg", "match": 8}
            got = media.fill_empty([photo, None, None], 3, folder, set(), ["Luka Doncic"], None)
            self.assertEqual([x and x["kind"] for x in got], ["photo", None, None])   # the picture continues
            self.assertEqual(asked, [])                                                # Pixabay never asked
            got = media.fill_empty([None, None, None], 3, folder, set(), ["Luka Doncic"], None)
            self.assertEqual([x and x["kind"] for x in got], ["video", None, None])   # never a blank video
        finally:
            for k, v in saved.items():
                setattr(media, k, v)
            shutil.rmtree(folder, ignore_errors=True)
        import gate
        verdict, notes = gate.check_visuals(got, {"people": ["Luka Doncic"]})
        self.assertEqual(verdict, "REVIEW")
        self.assertTrue(any("clip not judged" in n for n in notes))
        judged = [{"kind": "video", "match": 4, "title": "Boston Celtics warm-up", "license": "CC BY 3.0",
                   "author": "A", "page": "p2"}]
        self.assertEqual(gate.check_visuals(judged, {"people": ["Luka Doncic"]})[0], "PASS")


class Script(unittest.TestCase):
    """6 and 7. The script's repair pass and the quote check."""

    TEXT = ("During the Lakers' 124-114 win over the Hawks, Luka Doncic told Hawks fans courtside "
            "'You all wish you would have had me.' One fan replied 'We had you' and another said "
            "'I wish we did, I do.' Atlanta drafted Doncic third in 2018 and traded his rights to Dallas "
            "for Trae Young and a future first-round pick. Doncic finished with 32 points, 10 assists, "
            "eight rebounds, five steals and two blocks. ") * 3
    GOOD = [
        {"say": "Atlanta drafted Luka third, then traded him for Trae Young.", "on_screen": "Luka", "tone": "calm",
         "role": "context", "stage": "setup"},
        {"say": "Yahoo Sports reported he really said it, and one fan fired back, 'We had you.'", "on_screen": "Luka",
         "tone": "tense", "role": "fact", "stage": "conflict"},
        {"say": "But another fan gave in: 'I wish we did, I do.'", "on_screen": "Hawks fans", "tone": "amused",
         "role": "reaction", "stage": "twist"},
        {"say": "So the trade still stings in Atlanta, and the fans know it better than anyone.", "on_screen": "Luka",
         "tone": "calm", "role": "analysis", "stage": "payoff"},
        {"say": "So who's right about Luka: the fan who gave in, or the one who never wanted him?",
         "on_screen": "Luka", "tone": "amused", "role": "question", "stage": "exit"}]

    def test_quotes_in_both_styles(self):
        import script
        q = script.quotes_in
        self.assertEqual(q("Luka told fans, 'You all wish you would have had me.' One fired back, 'We had you.'"),
                         ["You all wish you would have had me."])
        self.assertEqual(q("He said 'He's not my coach, and I don't care' after the game."),
                         ["He's not my coach, and I don't care"])
        self.assertEqual(q('Tatum called it "another game on the schedule" before tip.'),
                         ["another game on the schedule"])
        self.assertEqual(q("Luka's Lakers beat the Hawks' bench, and Doncic's night was huge."), [])
        self.assertEqual(q("one fan fired back, 'We had you.' But another fan gave in: 'I wish we did, I do.'"),
                         ["I wish we did, I do."])        # a short quote never swallows the next one
        sources = [{"title": "t", "summary": "", "text": self.TEXT}]
        self.assertEqual(script.quote_check("one fan yelled 'Go back to Dallas, Luka, nobody wants you'", sources),
                         ["Go back to Dallas, Luka, nobody wants you"])     # an invented single-quoted quote

    def test_problems_found(self):
        import script
        beats = copy.deepcopy(LUKA_BEATS)
        problems = script.repair_needed(LUKA_HOOK, beats, script.retention_check(beats))
        self.assertEqual(len(problems), 3)      # hook replayed in beat 2, beat 5 repeats, payoff is a stat
        self.assertEqual(script.repair_needed(LUKA_HOOK, copy.deepcopy(self.GOOD),
                                              script.retention_check(copy.deepcopy(self.GOOD))), [])
        take = [{"say": "Doc was half right and fully clumsy.", "stage": "payoff"}]
        self.assertFalse(script.weak_payoff(take))    # a short take of her own is an answer

    def _build(self, repair_beats, limit: bool = False, draft_beats=None, hook: str = LUKA_HOOK):
        import nbadata
        import script
        calls = []
        draft = {"hooks": [{"text": hook, "formula": "The Receipt"}],
                 "strategy": {"kind": "beef", "central_question": "Who was right?", "headline_gap": "The trade."},
                 "angles": ["a"], "angle": "a",
                 "beats": copy.deepcopy(draft_beats if draft_beats is not None else LUKA_BEATS),
                 "titles": ["Luka Doncic TROLLED Hawks fans"], "thumbnail_text": "LUKA vs HAWKS FANS",
                 "receipt": "", "sources_used": [1],
                 "claims": [{"text": "Doncic told fans 'You all wish you would have had me.'", "status": "CONFIRMED",
                             "source": 1}],
                 "queries": ["luka doncic hawks fans"], "description": "Luka trolled Hawks fans.\nWhy.",
                 "tags": ["Luka Doncic"]}

        def fake(prompt, model=""):
            if "THE PROBLEMS TO FIX" in prompt:
                calls.append("repair")
                if limit:
                    raise script.UsageLimit("limit")
                return {"beats": copy.deepcopy(repair_beats)}
            if "sound human" in prompt:
                return {}
            if "scrolling Shorts" in prompt:
                return {"order": [1]}
            return copy.deepcopy(draft)
        saved = (script.ask_claude, script.gather_sources, nbadata.annotate)
        script.ask_claude = fake
        script.gather_sources = lambda topic, editor, tid: [
            {"publisher": "Yahoo Sports", "title": "Luka trolls Hawks fans", "link": "https://sports.yahoo.com/x",
             "url": "https://sports.yahoo.com/x", "text": self.TEXT, "trusted": True, "tier": 1,
             "main": True}]      # the story's own article, read (as gather_sources marks it; rule 58)
        nbadata.annotate = lambda claims: None
        try:
            editor = {"topics": [{"headline": "Luka Doncic trolls Hawks fans", "search_phrases": []}],
                      "ranked": [{"id": 0, "virality": 8}]}
            short = script.build_short(1, 0, editor, "voice", {"hooks": [{"name": "x", "shape": "y", "example": "z"}],
                                                               "rules": ["r"]})
            return short, calls
        finally:
            script.ask_claude, script.gather_sources, nbadata.annotate = saved

    def test_repair_pass(self):
        import script
        short, calls = self._build(self.GOOD)
        self.assertEqual(calls, ["repair"])
        self.assertEqual(len(short["repaired"]), 3)
        self.assertEqual(short["retention"]["hard"], [])
        # a repair that invents a number is refused: the original stays and is held
        bad = copy.deepcopy(self.GOOD)
        bad[3]["say"] = "So the trade still stings, and Luka has 45 points in his last game."
        short, _ = self._build(bad)
        self.assertEqual(short["repaired"], [])
        self.assertIn("beat 2 repeats the hook", short["retention"]["hard"])
        self.assertFalse(short["ready"])
        # a repair that invents a quote is refused too
        bad = copy.deepcopy(self.GOOD)
        bad[1]["say"] = "Yahoo Sports reported he said it, and one fan yelled 'Go back to Dallas, Luka.'"
        short, _ = self._build(bad)
        self.assertEqual(short["repaired"], [])
        # the Claude limit stops the run cleanly, as everywhere else
        with self.assertRaises(script.UsageLimit):
            self._build(self.GOOD, limit=True)
        # nothing to repair: the repair pass is never paid for
        _, calls = self._build(self.GOOD, draft_beats=self.GOOD,
                               hook="Did Luka Doncic just rub the 2018 trade in the Hawks fans' faces courtside?")
        self.assertEqual(calls, [])


class Timing(unittest.TestCase):
    """8 and 9. yt-edit and the end card."""

    @staticmethod
    def audio(*parts: tuple[str, float]) -> np.ndarray:
        """("voice", 1.0), ("silence", 0.8) ... at 16 kHz."""
        rate, out = 16000, []
        rng = np.random.default_rng(1)
        for kind, sec in parts:
            n = int(sec * rate)
            out.append(rng.uniform(-0.5, 0.5, n).astype(np.float32) if kind == "voice" else np.zeros(n, np.float32))
        return np.concatenate(out)

    def test_natural_pauses_are_never_cut(self):
        import audio_qc
        # Chatterbox's own pauses run up to ~0.6 s (measured on 7 real recordings): never touched
        for pause in (0.45, 0.62, 0.68):
            a = self.audio(("voice", 1.0), ("silence", pause), ("voice", 1.0))
            self.assertIsNone(audio_qc.silence_cut(a, 16000, 0.9, 1.0 + pause + 0.1, 0.29), pause)

    def test_long_silence_is_shortened_to_a_breath(self):
        import audio_qc
        a = self.audio(("voice", 1.0), ("silence", 1.2), ("voice", 1.0))
        cut = audio_qc.silence_cut(a, 16000, 0.9, 2.3, 0.29)
        self.assertIsNotNone(cut)
        self.assertGreaterEqual(cut["start"], 1.0)          # never into the sound before
        self.assertLessEqual(cut["end"], 2.2)               # never into the sound after
        self.assertAlmostEqual(1.2 - (cut["end"] - cut["start"]), audio_qc.LEFT, delta=0.05)

    def test_breath_in_the_gap_is_not_cut_through(self):
        import audio_qc
        # a long gap that is not silent (a breath in the middle): only the silent part may go
        a = self.audio(("voice", 1.0), ("silence", 0.5), ("voice", 0.3), ("silence", 0.5), ("voice", 1.0))
        self.assertIsNone(audio_qc.silence_cut(a, 16000, 0.9, 2.4, 0.29))

    def test_voice_end_and_end_card(self):
        import audio_qc
        import render
        a = self.audio(("voice", 2.0), ("silence", 0.6))
        saved = audio_qc.pcm
        audio_qc.pcm = lambda mp3, rate=16000: a
        try:
            self.assertAlmostEqual(audio_qc.sound_end(Path("x.mp3")), 2.0, delta=0.03)
        finally:
            audio_qc.pcm = saved
        # 0.4 s after the last real sound, never after the file ends; unmeasured = the file's end
        self.assertAlmostEqual(render.end_card_at({"duration": 29.07, "voice_end": 28.68}), 29.07, delta=0.001)
        self.assertAlmostEqual(render.end_card_at({"duration": 31.0, "voice_end": 28.0}), 28.4, delta=0.001)
        self.assertEqual(render.end_card_at({"duration": 30.0}), 30.0)
        self.assertEqual(render.END_CARD_SECONDS, 2.0)


class PrivateReport(unittest.TestCase):
    """10. Public repository: the run page shows counts only; the full report goes private."""

    def setUp(self):
        import public_summary
        import state
        self.mods = (state, public_summary)
        self.saved = (state.DATA, public_summary.DATA)
        self.tmp = Path(tempfile.mkdtemp())
        data = self.tmp / "data"
        for sub in ("scripts", "media", "gate", "audio", "video"):
            (data / sub).mkdir(parents=True)
        (data / "summary.md").write_text("## Scripts\nDid Luka Doncic really tell Hawks fans...")
        (data / "scripts" / "short_1.json").write_text(json.dumps({"hook": {"text": "Did Luka Doncic really..."}}))
        (data / "scripts" / "short_2.json").write_text("{}")
        (data / "media" / "short_1.json").write_text("[]")
        (data / "gate" / "short_1.json").write_text(json.dumps({"verdict": "PASS"}))
        (data / "gate" / "short_2.json").write_text(json.dumps({"verdict": "REVIEW"}))
        (data / "audio" / "short_1.timing.json").write_text("{}")
        (data / "audio" / "short_1.mp3").write_bytes(b"x" * 1000)
        (data / "video" / "short_1.mp4").write_bytes(b"x" * 1000)
        state.DATA = public_summary.DATA = data

    def tearDown(self):
        (state, public_summary) = self.mods
        state.DATA, public_summary.DATA = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_public_page_has_no_story(self):
        import public_summary
        text = "\n".join(public_summary.lines())
        self.assertIn("| 2 | 1 | 1 | 1 | 0 |", text)        # scripts, videos, PASS, REVIEW, REJECT
        self.assertNotIn("Luka", text)                       # no headline, hook or script

    def test_full_report_kept_privately_14_days(self):
        import tarfile
        from datetime import datetime, timezone
        import state
        home = self.tmp / "state" / "nba"
        (home / "runs").mkdir(parents=True)
        (home / "runs" / "2026-10-20_111.tar.gz").write_bytes(b"old")     # older than 14 days
        (home / "runs" / "2026-11-01_222.tar.gz").write_bytes(b"recent")
        kept = state.bundle_run(home, datetime(2026, 11, 11, tzinfo=timezone.utc))
        with tarfile.open(kept) as tar:
            names = sorted(tar.getnames())
        self.assertEqual(names, ["audio/short_1.timing.json", "gate/short_1.json", "gate/short_2.json",
                                 "media/short_1.json", "scripts/short_1.json", "scripts/short_2.json", "summary.md"])
        self.assertEqual(sorted(p.name for p in (home / "runs").iterdir()),
                         ["2026-11-01_222.tar.gz", kept.name])         # the old one is gone, no MP3/MP4


class PrivatePlan(unittest.TestCase):
    """11. plan/ is no longer in this public repository: every run restores it privately."""

    def test_restore_brings_the_plan(self):
        import state
        saved = (state.ROOT, state.DATA, state.STATE, state.HOME)
        tmp = Path(tempfile.mkdtemp())
        try:
            state.ROOT, state.DATA = tmp, tmp / "data"
            state.STATE = tmp / "state"
            state.HOME = state.STATE / "nba"
            (state.STATE / ".git").mkdir(parents=True)
            (state.HOME / "plan").mkdir(parents=True)
            (state.HOME / "plan" / "niche.json").write_text('{"date": "2026-11-09"}')
            (state.HOME / "plan" / "week.json").write_text('{"week_of": "2026-11-09"}')
            state.restore()
            self.assertEqual(sorted(p.name for p in (tmp / "plan").iterdir()), ["niche.json", "week.json"])
        finally:
            state.ROOT, state.DATA, state.STATE, state.HOME = saved
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertIn("plan/", (ROOT / ".gitignore").read_text())


# run 43011651547 (Brown snubs Tatum): what was on screen, beat by beat (main picture + alts)
RUN_43011651547 = [
    ["Celtics at Wizards 2024-12-015 (cropped).jpg", "Celtics at Wizards 2024-12-044 (cropped 2).jpg"],
    ["Jaylen Brown 2022.jpg", "Celtics at Wizards 2024-12-023.jpg", "Jaylen Brown (51840869654).jpg"],
    ["Celtics at Wizards 2024-12-036.jpg", "Jaylen Brown 2022 (cropped).jpg"],
    ["Anthony Tolliver defending Paul George.jpg", "Celtics at Wizards 2024-12-038.jpg"],
    ["Celtics at Wizards 2024-12-015.jpg", "Celtics at Wizards 2024-12-044 (cropped).jpg"],
    ["Celtics at Wizards 2024-12-013.jpg", "Celtics at Wizards 2024-12-019.jpg"],
]


def _commons(title: str) -> dict:
    return {"kind": "photo", "title": title, "source": "Wikimedia Commons",
            "page": "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_")}


class OnePhotoOnce(unittest.TestCase):
    """12. A photo and its crops ("X.jpg", "X (cropped).jpg", "X (cropped 2).jpg") are one picture."""

    def test_names(self):
        from picture_ids import already_shown, base_name, mark_shown
        self.assertEqual(base_name("Celtics at Wizards 2024-12-044 (cropped 2).jpg"),
                         ("celtics at wizards 2024-12-044", True))
        self.assertEqual(base_name("File:Jaylen_Brown_2022_cropped.jpg"), ("jaylen brown 2022", True))
        self.assertEqual(base_name("Jaylen Brown 2022.jpg"), ("jaylen brown 2022", False))
        shown: set = set()
        mark_shown(_commons("Jaylen Brown 2022.jpg"), shown)
        self.assertTrue(already_shown(_commons("Jaylen Brown 2022 (cropped).jpg"), shown))
        self.assertFalse(already_shown(_commons("Jaylen Brown 2023.jpg"), shown))        # another photo
        self.assertFalse(already_shown(_commons("Jaylen Brown 2022 (2).jpg"), shown))    # numbered = another shot
        # Flickr titles are not unique: two different "Jaylen Brown" photos are never merged
        flickr = {"kind": "photo", "title": "Jaylen Brown", "source": "Flickr via Openverse", "page": "f1"}
        shown2: set = set()
        mark_shown(flickr, shown2)
        self.assertFalse(already_shown({**flickr, "page": "f2"}, shown2))

    def _items(self):
        out = []
        for beat, titles in enumerate(RUN_43011651547):
            main, *alts = [_commons(t) for t in titles]
            out.append({**main, "beat": beat, "alts": alts, "alt": alts[0] if alts else None})
        return out

    def test_the_real_run_has_no_repeat(self):
        import media
        import render
        for mod in (media, render):
            saved = mod.picture_hash
            mod.picture_hash = lambda path: None        # no files here: only the names decide
            try:
                got = mod.no_repeats(copy.deepcopy(self._items()))
            finally:
                mod.picture_hash = saved
            shown = [x["title"] for it in got if it for x in [it] + (it.get("alts") or [])]
            self.assertEqual(len(shown), 10, mod.__name__)      # 13 shots, 3 were repeats of a photo
            for gone in ("Jaylen Brown 2022 (cropped).jpg", "Celtics at Wizards 2024-12-015.jpg",
                         "Celtics at Wizards 2024-12-044 (cropped).jpg"):
                self.assertNotIn(gone, shown, mod.__name__)
            self.assertIn("Celtics at Wizards 2024-12-015 (cropped).jpg", shown)   # the first one stays

    def test_a_crop_named_after_the_person(self):
        """Run 43027675858: "...-036 (White).jpg" (Derrick White cut out) and "...-036.jpg" were
        both on screen. A "(name)" after a numbered file is a crop; other names stay apart."""
        from picture_ids import already_shown, base_name, mark_shown
        shown = set()
        mark_shown(_commons("Celtics at Wizards 2024-12-036 (White).jpg"), shown)
        self.assertTrue(already_shown(_commons("Celtics at Wizards 2024-12-036.jpg"), shown))
        self.assertFalse(already_shown(_commons("Celtics at Wizards 2024-12-038.jpg"), shown))
        for own in ("Doc Rivers (coach).jpg", "Jayson Tatum (2018).jpg", "Doc Rivers (31361603010).jpg",
                    "20150401 MCDAAG Jaylen Brown floater (1).JPG"):
            self.assertFalse(base_name(own)[1], own)

    def test_commons_files_found_through_openverse(self):
        """Run 43088629255: "Jaylen Brown 2022" and "Jaylen Brown 2022 (cropped)" came through
        Openverse (source "Wikimedia via Openverse") and were both shown."""
        from picture_ids import already_shown, mark_shown
        ov = lambda t, cur: {"kind": "photo", "source": "Wikimedia via Openverse", "title": t,
                             "page": f"https://commons.wikimedia.org/w/index.php?curid={cur}",
                             "url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/x.jpg"}
        shown = set()
        mark_shown(ov("Jaylen Brown 2022", 115872550), shown)
        self.assertTrue(already_shown(ov("Jaylen Brown 2022 (cropped)", 131264916), shown))
        self.assertTrue(already_shown(_commons("Jaylen Brown 2022 (cropped).jpg"), shown))   # across sources
        self.assertFalse(already_shown(ov("Jaylen Brown (51840869654)", 115872551), shown))  # another file
        flickr = {"kind": "photo", "source": "Flickr", "title": "Jaylen Brown 2022 (cropped)",
                  "page": "https://www.flickr.com/photos/x/1", "url": "https://live.staticflickr.com/1.jpg"}
        self.assertFalse(already_shown(flickr, shown))                                       # not Commons

    def test_fill_never_brings_another_crop(self):
        import media
        saved = {k: getattr(media, k) for k in ("person_photos", "download", "picture_hash", "image_ok")}
        folder = media.ROOT / "data" / "_test_crop"
        try:
            clear = {"v": "C", "s": "game", "t": "drives"}    # D30: a top-up must show him clearly
            offered = [{**_commons("Jaylen Brown 2022.jpg"), "url": "u1", "tag": clear},
                       {**_commons("Jaylen Brown 2024.jpg"), "url": "u2", "tag": clear}]
            media.person_photos = lambda person, shown: [dict(c) for c in offered]
            media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            media.image_ok = lambda path: True
            media.picture_hash = lambda path: None
            items = [{**_commons("Jaylen Brown 2022 (cropped).jpg"), "file": "data/x.jpg", "match": 8}, None]
            got = media.fill_empty(items, 2, folder, set(), ["Jaylen Brown"], None)
            self.assertEqual(got[1]["title"], "Jaylen Brown 2024.jpg")   # not the uncropped original again
        finally:
            for k, v in saved.items():
                setattr(media, k, v)
            shutil.rmtree(folder, ignore_errors=True)


class CurrentTeam(unittest.TestCase):
    """13. Run 43011651547 showed Jaylen Brown in a Celtics jersey while the story said "now in
    Philly", and Paul George in a Pacers jersey: today's uniform comes first now."""

    CLAIMS = {"Q19664817": [   # Jaylen Brown: Celtics 2016-2026, 76ers since 2026, a college spell
        {"mainsnak": {"datavalue": {"value": {"id": "Q131371"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2016-06-23T00:00:00Z"}}}],
                        "P582": [{"datavalue": {"value": {"time": "+2026-07-01T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q138089"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2026-07-01T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q999"}}}, "rank": "normal", "qualifiers": {}}]}
    LABELS = {"Q131371": "Boston Celtics", "Q138089": "Philadelphia 76ers", "Q999": "California Golden Bears"}

    def setUp(self):
        import media
        self.m = media
        self.saved = (media.get, dict(media._wikidata), dict(media._teams))
        media._wikidata.clear()
        media._teams.clear()
        media._wikidata["Jaylen Brown"] = "Q19664817"
        claims, labels = self.CLAIMS, self.LABELS

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("action") == "wbgetclaims":
                return json.dumps({"claims": {"P54": claims.get(q["entity"], [])}}).encode()
            if q.get("action") == "wbgetentities":
                return json.dumps({"entities": {i: {"labels": {"en": {"value": labels[i]}}}
                                                for i in q["ids"].split("|") if i in labels}}).encode()
            raise OSError("unexpected")
        media.get = get

    def tearDown(self):
        self.m.get = self.saved[0]
        self.m._wikidata.clear()
        self.m._wikidata.update(self.saved[1])
        self.m._teams.clear()
        self.m._teams.update(self.saved[2])

    def test_current_and_former_teams(self):
        self.assertEqual(self.m.teams_of("Jaylen Brown"), ("philadelphia 76ers", {"boston celtics"}))
        t = self.m.photo_team
        self.assertEqual(t("Jaylen Brown", "Celtics at Wizards 2024-12-015 (cropped).jpg"), "former")
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown 76ers media day 2026"), "current")
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown, Sixers vs Celtics"), "current")   # today's team named
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown 2022.jpg"), "")                   # no team: unchanged
        # an older photo naming today's team is not today's uniform (Brown was a Celtic in 2023)
        self.assertEqual(t("Jaylen Brown", "Celtics at 76ers 2023", 2023), "former")
        self.assertEqual(t("Jaylen Brown", "76ers media day", 2026), "current")
        self.assertEqual(self.m.people_line(["Jaylen Brown", "Bomani Jones"]),
                         "Jaylen Brown (now with the Philadelphia 76ers), Bomani Jones")
        self.assertIn("UNIFORMS", self.m.PICK_PROMPT)

    def test_photo_order_today_first(self):
        m = self.m
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "team": "former"}, {"page": "b", "score": 20, "team": ""},
                {"page": "c", "score": 10, "team": "current"}, {"page": "d", "score": 25, "team": ""}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            self.assertEqual([p["page"] for p in m.photos("Jaylen Brown")], ["c", "d", "b", "a"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])

    def test_unknown_or_down_changes_nothing(self):
        self.assertEqual(self.m.teams_of("Bomani Jones"), ("", set()))       # no Wikidata item: no request
        self.assertEqual(self.m.photo_team("Bomani Jones", "Celtics at Wizards"), "")
        self.m._teams.clear()

        def down(url, timeout=30):
            raise OSError("down")
        self.m.get = down
        self.assertEqual(self.m.teams_of("Jaylen Brown"), ("", set()))
        self.assertEqual(self.m.people_line(["Jaylen Brown"]), "Jaylen Brown")


class WikimediaPolite(unittest.TestCase):
    """2026-11-11: Wikimedia answered 429 to a shared cloud IP before we sent anything. With a
    token the limit is per account; without one nothing may change."""

    def setUp(self):
        import urllib.error
        import urllib.request
        import wiki_http
        self.w, self.err, self.req = wiki_http, urllib.error, urllib.request
        self.saved = (wiki_http.TOKEN[0], wiki_http.WAIT_BUDGET[0], wiki_http._sleep,
                      urllib.request.urlopen)
        self.calls, self.slept, self.answers = [], [], []
        wiki_http._sleep = self.slept.append

        class Reply:
            def __init__(s, body): s.body = body
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return s.body

        def fake(req, timeout=30):
            self.calls.append(dict(req.header_items()))
            a = self.answers.pop(0)
            if isinstance(a, int):
                raise self.err.HTTPError(req.full_url, a, "x", {"Retry-After": "20"}, None)
            return Reply(a)
        urllib.request.urlopen = fake

    def tearDown(self):
        w = self.w
        w.TOKEN[0], w.WAIT_BUDGET[0], w._sleep, self.req.urlopen = self.saved

    API = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=Q1"

    def test_token_only_to_wikimedia_apis(self):
        self.w.TOKEN[0] = "t0k"
        self.assertEqual(self.w.headers(self.API, "UA").get("Authorization"), "Bearer t0k")
        for url in ("https://upload.wikimedia.org/wikipedia/commons/a/a1/X.jpg",
                    "https://api.openverse.org/v1/images/?q=x",
                    "https://evil.example/w/api.php?wikipedia.org/",
                    "https://en.wikipedia.org.evil.example/w/api.php"):
            self.assertNotIn("Authorization", self.w.headers(url, "UA"), url)
        self.w.TOKEN[0] = ""
        self.assertNotIn("Authorization", self.w.headers(self.API, "UA"))

    def test_429_waited_out_then_answer(self):
        self.answers = [429, b"ok"]
        self.assertEqual(self.w.fetch(self.API, "UA"), b"ok")
        self.assertEqual(self.slept, [20.0])

    def test_wait_budget_never_hangs_a_run(self):
        self.w.WAIT_BUDGET[0] = 10.0
        self.answers = [429]
        with self.assertRaises(self.err.HTTPError):
            self.w.fetch(self.API, "UA")
        self.assertEqual(self.slept, [])

    def test_refused_token_dropped_and_call_repeated(self):
        self.w.TOKEN[0] = "old"
        self.answers = [401, b"ok"]
        self.assertEqual(self.w.fetch(self.API, "UA"), b"ok")
        self.assertIn("Authorization", self.calls[0])
        self.assertNotIn("Authorization", self.calls[1])
        self.assertEqual(self.w.TOKEN[0], "")

    def test_other_sites_exactly_as_before(self):
        self.w.TOKEN[0] = "t0k"
        self.answers = [429]
        with self.assertRaises(self.err.HTTPError):
            self.w.fetch("https://pixabay.com/api/?q=x", "UA")
        self.assertEqual((len(self.calls), self.slept), (1, []))
        self.assertNotIn("Authorization", self.calls[0])

    def test_media_and_signals_use_it(self):
        import media
        import signals
        self.assertIs(media.wiki_http, self.w)
        self.assertIs(signals.wiki_http, self.w)
        self.answers = [b"{}"]
        self.assertEqual(media.get(self.API), b"{}")


class SceneSpread(unittest.TestCase):
    """Run 43011651547: 9 of its 13 photos were Hameltion's "Celtics at Wizards 2024-12-0NN"."""

    def setUp(self):
        import media
        from collections import Counter
        self.m, self.Counter = media, Counter

    def ph(self, title, author="Hameltion", date="2024-12-15"):
        return {"kind": "photo", "title": title, "author": author, "date": date, "page": title}

    def test_scene_keys(self):
        m = self.m
        a = m.scene_of(self.ph("Celtics at Wizards 2024-12-015 (cropped).jpg"))
        self.assertEqual(a, m.scene_of(self.ph("Celtics at Wizards 2024-12-044.jpg")))
        jak = "Pemain Bola Basket NBA dari Amerika Melatih Pelajar SMA di Jakarta (%s)"
        s1 = m.scene_of(self.ph(jak % "42950693724", "U.S. Embassy Jakarta", ""))
        self.assertIsNotNone(s1)
        self.assertEqual(s1, m.scene_of(self.ph(jak % "42950705794", "U.S. Embassy Jakarta", "")))
        # no date and no numbered series, or no real author: unknown, never grouped
        self.assertIsNone(m.scene_of(self.ph("Jaylen Brown", "Keith Allison", "")))
        self.assertIsNone(m.scene_of(self.ph("Celtics at Wizards 2024-12-015.jpg", "unknown author")))
        self.assertIsNone(m.scene_of({"kind": "video", "title": "x", "author": "a", "date": "2024"}))

    def _pool(self):
        h = [self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg") for n in (15, 23, 36, 38, 44)]
        other = [self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"),
                 self.ph("Jaylen Brown Sixers.jpg", "Someone", "2026-10-30")]
        return h + other

    def test_full_scene_goes_behind_everything_else(self):
        """Owner, 2026-11-12: a 4th photo of one scene only when nothing else is left, then by
        score (before: it waited only behind equally related photos scoring 6+)."""
        m, c = self.m, self._pool()
        scenes = self.Counter({m.scene_of(c[0]): 3})
        tier = lambda j: 3
        scores = {0: 8, 1: 8, 5: 7, 6: 6}
        self.assertEqual(m.spread_scenes([0, 1, 5, 6], c, tier, scores, scenes), [5, 6, 0, 1])
        self.assertEqual(m.spread_scenes([0, 1, 5], c, tier, scores, self.Counter()), [0, 1, 5])
        self.assertEqual(m.spread_scenes([0, 1], c, tier, scores, scenes), [0, 1])  # nothing else: by score
        # behind a less related or weaker photo too (the old rule kept it in front of those)
        self.assertEqual(m.spread_scenes([0, 5], c, {0: 3, 5: 2}.get, {0: 8, 5: 9}, scenes), [5, 0])
        self.assertEqual(m.spread_scenes([0, 5], c, tier, {0: 8, 5: 5}, scenes), [5, 0])

    def test_scene_from_the_file_name(self):
        m = self.m
        wh = {"kind": "photo", "author": "The White House", "date": "",
              "title": "Joe Biden Steph Curry Steve Kerr P20230117AS-1347.jpg"}
        self.assertEqual(m.scene_of(wh), ("the white house", "2023-01-17"))
        self.assertEqual(m.scene_of(wh), m.scene_of({**wh, "title": "P20230117AS-2061 (52636052765).jpg",
                                                     "date": "2023-01-17"}))
        self.assertIsNone(m.TITLE_DAY.search("Steph Curry (51913909237).jpg"))   # a Flickr id is no date

    def test_replay_of_the_run(self):
        """The run's 13 shots in its own order, with two fitting photos of other games added to
        the pool: the Wizards game is shown at most SCENE_MAX times, nothing is lost."""
        m = self.m
        run = [self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg") for n in (15, 44, 23, 36, 38, 13, 19, 11, 12)]
        others = [self.ph(f"Jaylen Brown {k}.jpg", "All-Pro Reels", "2022-01-23") for k in range(2)] + \
                 [self.ph(f"Jaylen Brown game {k}.jpg", f"Author {k}", f"2025-0{k + 1}-02") for k in range(6)]
        pool = run + others
        scores = {j: 8 if j < len(run) else 6 for j in range(len(pool))}
        scenes, shown = self.Counter(), []
        for _ in range(13):
            order = [j for j in range(len(pool)) if j not in shown]
            left = m.spread_scenes(order, pool, lambda j: 3, scores, scenes)
            if not left:
                break
            j = left[0]
            shown.append(j)
            scenes.update([m.scene_of(pool[j])])
        # before B11: 9 of 13 from the Wizards game. Now 3, then the 8 other photos, then (pool
        # used up) 2 more Wizards shots rather than a frozen picture
        self.assertEqual(sum(1 for j in shown if j < len(run)), 5)
        self.assertEqual(len(set(shown)), 13)
        self.assertTrue(all(j >= len(run) for j in shown[3:11]))
        self.assertEqual(shown[:m.SCENE_MAX], [0, 1, 2])     # the best come first, as before

    def test_flickr_photos_know_their_day(self):
        m = self.m
        saved = (m.FLICKR_KEY, m.get, m.namesake, dict(m.PHOTO_STATS))
        reply = {"stat": "ok", "photos": {"photo": [
            {"title": "Jaylen Brown", "tags": "basketball nba", "license": k, "owner": "o", "id": str(n),
             "ownername": "Keith Allison", "datetaken": f"2019-03-0{n} 19:30:00",
             "url_k": f"https://live.staticflickr.com/{n}.jpg", "width_k": "1400", "height_k": "2000"}
            for n, k in ((1, next(k for k, v in m.FLICKR_LICENCES.items() if m.licence_ok(v))),)]}}
        try:
            m.FLICKR_KEY, m.namesake = "k", (lambda p, t: False)
            m.get = lambda url, timeout=30: json.dumps(reply).encode()
            got = m.flickr_photos("Jaylen Brown")
            self.assertEqual(got[0]["date"], "2019-03-01")
            self.assertEqual(m.scene_of(got[0]), ("keith allison", "2019-03-01"))
        finally:
            m.FLICKR_KEY, m.get, m.namesake = saved[:3]
            m.PHOTO_STATS.clear(); m.PHOTO_STATS.update(saved[3])

    def test_fill_prefers_another_game(self):
        m = self.m
        saved = {k: getattr(m, k) for k in ("person_photos", "download", "picture_hash", "image_ok")}
        folder = m.ROOT / "data" / "_test_scene"
        try:
            clear = {"v": "C", "s": "game", "t": "drives"}    # D30: a top-up must show him clearly
            wiz = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "url": f"w{n}", "tag": clear} for n in (11, 12, 13)]
            new = {**self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"), "url": "a", "tag": clear}
            m.person_photos = lambda person, shown: [dict(c) for c in wiz + [new]]
            m.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            m.image_ok = lambda path: True
            m.picture_hash = lambda path: None
            on = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "file": "data/x.jpg"} for n in (15, 23, 36)]
            items = [{**on[0], "file": "data/x.jpg", "match": 8, "alts": on[1:]}, None, None]
            got = m.fill_empty(items, 3, folder, set(), ["Jaylen Brown"], None)
            self.assertEqual(got[1]["title"], "Jaylen Brown 2022.jpg")       # another game first
            self.assertEqual(got[2]["title"], "Celtics at Wizards 2024-12-011.jpg")  # nothing else left
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
            shutil.rmtree(folder, ignore_errors=True)

    def test_fill_counts_what_is_on_screen(self):
        m = self.m
        items = [{**self.ph("Celtics at Wizards 2024-12-015.jpg"),
                  "alts": [self.ph("Celtics at Wizards 2024-12-023.jpg"), self.ph("Celtics at Wizards 2024-12-036.jpg")]}]
        sc = m.count_scenes(x for it in items for x in [it] + it["alts"])
        self.assertTrue(m.scene_full(self.ph("Celtics at Wizards 2024-12-044.jpg"), sc))
        self.assertFalse(m.scene_full(self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"), sc))


class OwnArticleFirst(unittest.TestCase):
    """Run 43027675858: 47 headlines, 3 articles read, the pick's own one ("Jaylen Brown explains
    why he ignored...") 6th in line and never read. Offline: reading is faked."""

    HEAD = "Jaylen Brown explains why he ignored Jayson Tatum\u2019s attempt at pre-game embrace before first-ever clash"

    def _editor(self):
        it = lambda t, tier, link: {"title": t, "tier": tier, "link": link, "publisher": "P"}
        return {"ranked": [{"id": 0, "same_as": [1]}],
                "topics": [{"headline": self.HEAD, "items": [
                    it("Kevin O'Connor calls out 76ers' Jaylen Brown", 1, "https://a/1"),
                    it("The Bounce: Jaylen Brown's real beef is with the Celtics", 1, "https://a/2"),
                    it("Payton Pritchard on Jaylen Brown, Jayson Tatum relationship", 1, "https://a/3"),
                    it("People Close to Jayson Tatum, Jaylen Brown Keep Saying the Same Thing", 1, "https://a/4"),
                    it(self.HEAD, 1, "https://a/own"),
                    it("Jaylen Brown explains why he ignored Jayson Tatum pregame", 2, "https://b/copy")]},
                           {"headline": "Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win", "items": [
                    it("Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win", 1, "https://a/merged")]}]}

    def run_with(self, readable):
        import script
        saved = (script.read_article, script.decode_google)
        tried = []

        def fake(it, real):
            tried.append(it["link"])
            if it["link"] in readable:
                it["text"] = "x" * 700
                return True
            return False
        script.read_article, script.decode_google = fake, (lambda links: {})
        try:
            e = self._editor()
            return script.gather_sources(e["topics"][0], e, 0), tried
        finally:
            script.read_article, script.decode_google = saved

    def test_own_article_read_first(self):
        import script
        src, tried = self.run_with({"https://a/own", "https://a/1", "https://a/2", "https://a/merged"})
        self.assertEqual(tried[0], "https://a/own")
        self.assertEqual(tried[1], "https://a/merged")     # the merged story's own headline next
        self.assertTrue(src[0]["main"])
        self.assertEqual(sum(bool(s["text"]) for s in src), 4)   # every readable one, up to MAX_ARTICLES
        self.assertIn("read in full, source [1]", script.main_note(src, self.HEAD))

    def test_other_outlets_of_the_same_story_are_read_too(self):
        """37. Run 43253965466: Zion's story from Yahoo, Bleacher Report, RealGM and ESPN, all near
        the headline: 1 of 4 read (the other copies were never tried). Now up to MAX_ARTICLES."""
        import script
        head = "Zion Williamson tears into Pelicans after 'unacceptable' loss to Nets"
        it = lambda t, tier, link: {"title": t, "tier": tier, "link": link, "publisher": "P"}
        e = {"ranked": [{"id": 0, "same_as": []}], "topics": [{"headline": head, "items": [
            it(head, 1, "https://yahoo/1"),
            it("Zion Williamson Calls Out Pelicans After Loss to Nets", 1, "https://br/1"),
            it("Zion Williamson Calls Pelicans' 145-111 Loss To Nets 'Unacceptable'", 2, "https://realgm/1"),
            it("Zion Williamson calls out Pelicans for another 'unacceptable' blowout loss", 1, "https://espn/1")]}]}
        saved = (script.read_article, script.decode_google)
        tried = []

        def fake(x, real):
            tried.append(x["link"])
            x["text"] = "y" * 700
            return True
        script.read_article, script.decode_google = fake, (lambda links: {})
        try:
            src = script.gather_sources(e["topics"][0], e, 0)
        finally:
            script.read_article, script.decode_google = saved
        self.assertEqual(tried[0], "https://yahoo/1")
        self.assertEqual(sorted(tried), sorted(["https://yahoo/1", "https://br/1", "https://realgm/1", "https://espn/1"]))
        self.assertEqual(sum(bool(x["text"]) for x in src), 4)
        self.assertEqual([x["link"] for x in src if x["main"]], ["https://yahoo/1"])   # one main only

    def test_45_0_is_45(self):
        """37. Run 43253965466: "averaged a staggering 45.0 points" in the source, "45" in the hook."""
        import script
        src = [{"title": "", "text": "Luka averaged a staggering 45.0 points, 7.0 rebounds and 8.30 assists"}]
        self.assertEqual(script.fact_check("Luka Doncic averaged 45 points, 7 rebounds, 8.3 assists.", src), [])
        self.assertEqual(script.fact_check("Luka Doncic averaged 46 points.", src), ["46"])
        self.assertEqual(script.numbers("100 and 10 and 0.5 and 2026"), {"100", "10", "0.5", "2026"})

    def test_same_article_from_another_outlet(self):
        import script
        src, tried = self.run_with({"https://b/copy", "https://a/1"})
        self.assertEqual(tried[:2], ["https://a/own", "https://b/copy"])
        self.assertEqual([s["link"] for s in src if s["main"]], ["https://b/copy"])

    def test_unread_own_article_is_never_promised(self):
        import script
        src, _ = self.run_with({"https://a/1", "https://a/2"})
        self.assertFalse(any(s["main"] for s in src))
        note = script.main_note(src, self.HEAD)
        self.assertIn("NOT READ", note)
        self.assertIn("Never promise", note)
        self.assertIn("{main_note}", script.PROMPT)

    def test_closeness(self):
        import script
        self.assertEqual(script.closeness(self.HEAD, self.HEAD), 1.0)
        self.assertGreaterEqual(script.closeness("Jaylen Brown explains why he ignored Jayson Tatum pregame", self.HEAD),
                                script.NEAR)
        self.assertLess(script.closeness("Kevin O'Connor calls out 76ers' Jaylen Brown", self.HEAD), script.NEAR)
        self.assertEqual(script.closeness("Jaylen Brown Tatum", self.HEAD), 0.0)   # too short to tell


class MustKnowContext(unittest.TestCase):
    """Run 43027675858: Paul George's 36 points without "the player Boston got for Brown", no
    game result, no "Giannis now plays for Miami", and "Heat radio host" for a podcast host.
    The writer is told, and the critic checks it again."""

    def test_writer_and_critic_both_have_the_rule(self):
        import script
        w, c = script.PROMPT, script.HUMANIZE
        self.assertIn("MUST-KNOW CONTEXT", w)
        self.assertIn("MUST-KNOW CONTEXT", c)
        for need in ("who they are in THIS story", "who went where", "its result (who won",
                     "current team", "never fill it from memory", "as the sources\n     give it"):
            self.assertIn(need, w, need)
        for need in ("who is that?", "without who went where", "without who won",
                     "exactly as the sources"):
            self.assertIn(need, c, need)

    def test_prompts_still_format(self):
        import script
        script.HUMANIZE.format(voice="v", sources="s", draft="d")
        self.assertIn("MUST-KNOW", script.PROMPT.format(**{k: "x" for k in (
            "skill_script", "skill_package", "skill_seo", "voice", "formulas", "rules", "headline",
            "main_note", "why", "two_versions", "story_type", "niche", "search", "history", "sources")}))


class OwnTake(unittest.TestCase):
    """Run 43027675858's payoff: "The New York Times argues Brown's real fight is with Boston,
    and I think that's right." Agreement is not analysis."""

    REAL = ("Derrick White said \"No beef.\" The New York Times argues Brown's real fight is with "
            "Boston, and I think that's right.")

    def pay(self, say):
        return [{"say": "Brown snubbed Tatum.", "stage": "setup"}, {"say": say, "stage": "payoff"},
                {"say": "So who was he mad at, Tatum or Boston?", "stage": "exit"}]

    def doc(self, say):
        return [{"say": "Doc Rivers questioned Giannis's IQ, then apologized.", "stage": "setup"},
                {"say": say, "stage": "payoff"}, {"say": "So is Doc's apology enough?", "stage": "exit"}]

    def test_agreement_only_goes_to_repair(self):
        import script
        for say in (self.REAL, "The Times says it's Boston. I agree.", "Honestly, they're not wrong.",
                    "Bomani says he blames others, and honestly, Bomani is right.", "I buy it."):
            self.assertTrue(script.borrowed_take(self.pay(say)), say)
        problems = script.repair_needed("Did Brown snub Tatum?", self.pay(self.REAL), {})
        self.assertTrue(any("her OWN reason" in p for p in problems), problems)

    def test_her_own_takes_stay(self):
        """Every real payoff of the earlier runs, and agreement WITH a reason, is left alone."""
        import script
        for say in ("I think the apology fixed the wording, not the pattern.",
                    "I think that snub backfired, the scoreboard got the last word.",
                    "Bomani Jones said parts were correct, but an apology fixes the wording, not the point.",
                    "One fan said he only has value in Golden State. I think the passing says otherwise.",
                    "The Times says it's Boston, and I think that's right, because he went quiet that night.",
                    "I think Doc is wrong.", "Honestly, Doc is wrong.", "Doc was half right and fully clumsy."):
            self.assertFalse(script.borrowed_take(self.pay(say)), say)
        self.assertEqual(script.repair_needed("Did Doc apologize?",
                                              self.doc("I think the apology fixed the wording, not the pattern."), {}), [])

    def test_writer_critic_repair_told(self):
        import script
        self.assertIn("Agreeing with an outlet", script.PROMPT)
        self.assertIn("never only agreeing with someone else's view", script.HUMANIZE)
        self.assertIn("never only agreeing with someone else's view", script.REPAIR)


class HookPick(unittest.TestCase):
    """Run 43027675858: "Why did Jaylen Brown leave Jayson Tatum's pregame dap hanging...?" (the
    Short never said why) and "Did Brendan Tobin just tell Doc Rivers...?" (a podcaster first)."""

    def test_the_fan_sees_story_and_known_names(self):
        import script
        seen = {}

        def fake(prompt, model=None, **kw):
            seen["prompt"] = prompt
            return {"best": 2}
        saved = script.ask_claude
        script.ask_claude = fake
        try:
            hooks = [{"text": "Did Brendan Tobin just tell Doc Rivers the blame is his?", "question": True, "score": 41},
                     {"text": "Did Doc Rivers just say sorry to Giannis, and mean it?", "question": True, "score": 45}]
            got = script.intrigue_pick(hooks, "Doc Rivers apologizes", "Doc Rivers questioned Giannis's IQ...",
                                       ["Giannis Antetokounmpo 3.4", "Doc Rivers 2.3"])
        finally:
            script.ask_claude = saved
        p = seen["prompt"]
        self.assertIn("Giannis Antetokounmpo, Doc Rivers", p)      # names, not their fame numbers
        self.assertNotIn("3.4", p)
        self.assertIn("Doc Rivers questioned Giannis's IQ", p)      # the whole Short
        self.assertIn("THE SHORT PAYS IT OFF", p)
        self.assertIn("THE FIRST 3 SECONDS", p)
        self.assertIn("A STRANGER GETS IT AT ONCE", p)
        self.assertTrue(got[0]["intrigue_pick"])
        self.assertEqual(got[0]["text"], hooks[1]["text"])

    def test_old_call_still_works(self):
        import script
        saved = script.ask_claude
        script.ask_claude = lambda prompt, model=None, **kw: {"best": 1}
        try:
            hooks = [{"text": "A?", "question": True, "score": 50}, {"text": "B?", "question": True, "score": 45}]
            self.assertEqual(script.intrigue_pick(hooks, "h")[0]["text"], "A?")
        finally:
            script.ask_claude = saved


class DetailsFromSources(unittest.TestCase):
    """Run 43011651547's hook: "...in front of his own crowd": no source said where it was.
    Run 43027675858's "Heat radio host Brendan Tobin" WAS in the source ("Miami sports radio
    host Brendan Tobin"): a true detail must pass."""

    TOBIN = [{"title": "Heat Journalist Goes Ballistic On Doc Rivers", "tier": 1, "text":
              "Doc Rivers' comments drew criticism, including from Miami sports radio host Brendan "
              "Tobin. Speaking on the Heat Collective podcast, Tobin said..."}]
    SNUB = [{"title": "Jaylen Brown appears to blow off Jayson Tatum's greeting", "tier": 1, "text":
             "Brown did not greet Tatum before tip-off. Tatum scored 21 and Paul George 36."}]

    def test_true_details_pass(self):
        import compliance as C
        self.assertEqual(C.unsupported_details("Heat radio host Brendan Tobin says that's on you.", self.TOBIN), [])
        self.assertEqual(C.unsupported_details("On his podcast, Tobin went off.", self.TOBIN), [])
        self.assertEqual(C.unsupported_details("Brown snubbed Tatum, and Booker watched.", self.SNUB), [])

    def test_invented_details_caught(self):
        import compliance as C
        self.assertEqual(C.unsupported_details("Brown snubbed Tatum in front of his own crowd.", self.SNUB), ["crowd"])
        self.assertEqual(C.unsupported_details("The fans booed him on the road.", self.SNUB), ["booed", "on the road"])
        self.assertEqual(C.unsupported_details("ESPN analyst Tobin said it.", self.TOBIN), ["analyst"])

    def test_gate_holds_it(self):
        import compliance as C
        v, notes = C.check_fabrication("Brown snubbed Tatum in front of his own crowd.", self.SNUB, [], [])
        self.assertEqual(v, C.REVIEW)
        self.assertTrue(any("details not in the sources: crowd" in n for n in notes))
        v, _ = C.check_fabrication("Heat radio host Brendan Tobin says that's on you.", self.TOBIN, [], [])
        self.assertEqual(v, C.PASS)

    def test_repair_fixes_beats_not_the_fixed_hook(self):
        import script
        beats = [{"say": "Brown snubbed Tatum in front of his own crowd.", "stage": "setup"},
                 {"say": "I think the snub said more than his 13 points, because he went quiet.", "stage": "payoff"},
                 {"say": "So who won that night, Brown or Tatum?", "stage": "exit"}]
        problems = script.repair_needed("Did Brown snub Tatum?", beats, {}, self.SNUB)
        self.assertTrue(any("not in any source: crowd" in p for p in problems), problems)
        beats[0]["say"] = "Brown snubbed Tatum before tip-off."
        self.assertEqual(script.repair_needed("Did Brown snub Tatum in front of his own crowd?", beats, {}, self.SNUB), [])
        self.assertEqual(script.repair_needed("Did Brown snub Tatum?", beats, {}), [])   # old call unchanged


class FlexibleLength(unittest.TestCase):
    """Every Short of the earlier runs hit the 65-word ceiling (63-66 words): with context and
    her own reason required, the owner chose a flexible limit (2026-11-11, option "გ")."""

    def test_limits(self):
        import script
        self.assertEqual(script.BEAT_WORDS_MAX, 72)
        # the longest allowed Short (an 18-word hook + 72 words) is still "ready" (18-42 s)
        self.assertLessEqual(round((18 + 72) / script.WPM * 60), 42)

    def test_every_writer_knows_the_exception(self):
        import script
        for name in ("PROMPT", "HUMANIZE", "REPAIR"):
            text = getattr(script, name)
            self.assertIn("45-65 words", text, name)
            self.assertIn("72", text, name)
        self.assertIn("Never pad", script.PROMPT)
        self.assertIn("Never cut must-know context", script.TRIM)
        self.assertIn("72 spoken words or fewer", script.TRIM)


class ReadingAndQuestions(unittest.TestCase):
    """Owner, 2026-11-11: read five articles, give every site the time it needs. Run 43066151290:
    "So how was he not paying attention?" re-asked the hook; "Is Payton Pritchard right...?"
    brought in someone never introduced, and did not come back to the hook."""

    HOOK = "Jaylen Brown ignored Jayson Tatum twice in one night, so was he really not paying attention?"
    BEATS = [{"say": "Brown got traded to Philly for Paul George, and Tuesday was his first game vs Tatum.", "stage": "setup"},
             {"say": "Tatum tapped his chest at tip-off, but Brown skipped him after Boston's win.", "stage": "conflict"},
             {"say": "Yahoo reported Brown said beforehand he didn't intend to speak with Tatum. So how was he not paying attention?", "stage": "escalation"},
             {"say": "I think you can't announce a plan, then say you missed it.", "stage": "payoff"},
             {"say": "Is Payton Pritchard right that there was never beef, or was this planned?", "stage": "exit"}]

    def test_reading_limits(self):
        import script
        self.assertEqual(script.MAX_ARTICLES, 5)
        self.assertEqual(script.READ_CONFIG.get("DEFAULT", "DOWNLOAD_TIMEOUT"), "300")
        self.assertFalse(hasattr(script, "READ_BUDGET"))          # no limit on a story's reading
        self.assertGreaterEqual(script.TIMEOUT, 1200)              # Claude's analysis is never cut
        self.assertEqual(script.READ_TRIES, 2)

    def test_slow_site_gets_a_second_try(self):
        import script
        saved = (script.trafilatura.fetch_url, script.trafilatura.extract)
        calls = []

        def fetch(url, config=None):
            calls.append(config.get("DEFAULT", "DOWNLOAD_TIMEOUT"))
            return None if len(calls) == 1 else "<html>x</html>"
        script.trafilatura.fetch_url, script.trafilatura.extract = fetch, (lambda html: "article text " * 60)
        try:
            it = {"link": "https://a/1"}
            self.assertTrue(script.read_article(it, {}))
            self.assertEqual(calls, ["300", "300"])
        finally:
            script.trafilatura.fetch_url, script.trafilatura.extract = saved

    def test_the_run_is_caught(self):
        import script
        self.assertEqual(script.re_asked(self.HOOK, self.BEATS), [2])
        self.assertEqual(script.new_names_at_exit(self.HOOK, self.BEATS), ["Payton", "Pritchard"])
        self.assertFalse(script.loops_back(self.HOOK, self.BEATS[-1]["say"]))
        problems = script.repair_needed(self.HOOK, self.BEATS, {})
        for need in ("brings in Payton, Pritchard", "does not come back to the hook", "beat 3 asks the hook's question"):
            self.assertTrue(any(need in p for p in problems), (need, problems))

    def test_good_endings_left_alone(self):
        import script
        good = [dict(b) for b in self.BEATS]
        good[2]["say"] = "Yahoo reported Brown said beforehand he didn't intend to speak with Tatum."
        good[-1]["say"] = "So was Brown really not paying attention to Tatum, or was this planned?"
        self.assertEqual(script.re_asked(self.HOOK, good), [])
        self.assertEqual(script.new_names_at_exit(self.HOOK, good), [])
        self.assertTrue(script.loops_back(self.HOOK, good[-1]["say"]))
        # a possessive is the same name: "Doc's apology" loops to "Doc Rivers"
        self.assertTrue(script.loops_back("Did Doc Rivers just apologize to Giannis?", "So is Doc's apology enough?"))
        self.assertIn("QUESTIONS:", script.PROMPT)
        self.assertIn("QUESTIONS:", script.HUMANIZE)


class PhotoEra(CurrentTeam):
    """23. Run 43066151290: Brown's 2015 high school all-star photos in Paul George's Short, a
    2018 youth clinic in Jakarta as the hook, and a Commons derivative next to its original."""

    def test_before_his_nba_career(self):
        m = self.m
        m._nba_debut.clear()
        self.assertEqual(m.photo_team("Jaylen Brown", "20150401 MCDAAG Jaylen Brown dunk", 2015), "pre-nba")
        self.assertEqual(m.photo_team("Jaylen Brown", "Celtics at Wizards 2024-12-054", 2024), "former")
        self.assertEqual(m.photo_team("Jaylen Brown", "Jaylen Brown 76ers 2026", 2026), "current")
        self.assertEqual(m.photo_team("Jaylen Brown", "Jaylen Brown", None), "")   # no year: unchanged
        self.assertEqual(sorted(["pre-nba", "former", "", "current"], key=m.TEAM_ORDER.get),
                         ["current", "", "former", "pre-nba"])

    def test_claude_is_told(self):
        m = self.m
        self.assertEqual(m.photo_era({"date": "2015-04-01", "team": "pre-nba"}), "2015 PRE-NBA")
        self.assertEqual(m.photo_era({"date": "2014-03-05", "team": "former"}), "2014 OLD TEAM")
        self.assertEqual(m.photo_era({"date": "2026-04-02", "team": "current"}), "2026")
        self.assertEqual(m.photo_era({}), "")
        for rule in ("PRE-NBA", "score it 3 at most", "OFF COURT", "score it 4 at most", "OLD TEAM"):
            self.assertIn(rule, m.PICK_PROMPT, rule)

    def test_derivative_is_the_same_picture(self):
        from picture_ids import already_shown, mark_shown
        orig = _commons("Anthony Tolliver defending Paul George.jpg")
        der = {**_commons("Paul George Pacers.jpg"),
               "author": "File:Anthony Tolliver defending Paul George.jpg: joshuak8 derivative work: Chrishmt0423"}
        for first, second in ((orig, der), (der, orig)):
            shown = set()
            mark_shown(first, shown)
            self.assertTrue(already_shown(second, shown))
        shown = set()
        mark_shown(der, shown)
        self.assertFalse(already_shown(_commons("Pacers Paul George (cropped).jpg"), shown))


class OpenverseRetries(unittest.TestCase):
    """24. Openverse answers 504 to a search it has not seen, finishes it behind the scenes, and
    answers the same search fast a little later. Three quick tries lost every search."""

    def test_504s_then_the_answer(self):
        import time
        import urllib.error
        import urllib.request
        import media
        saved = (urllib.request.urlopen, time.sleep, media.OPENVERSE_BUDGET[0], media.openverse_token,
                 media.namesake, dict(media.PHOTO_STATS))
        slept, tries = [], []

        class Reply:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return json.dumps({"results": [{"title": "Paul George Celtics", "url": "https://x/1.jpg",
                                                         "width": 1200, "height": 1600, "license": "by",
                                                         "license_version": "2.0", "creator": "A"}]}).encode()

        def fake(req, timeout=30):
            tries.append(timeout)
            if len(tries) <= 4:
                raise urllib.error.HTTPError(req.full_url, 504, "Gateway Timeout", {}, None)
            return Reply()
        urllib.request.urlopen, time.sleep = fake, slept.append
        media.OPENVERSE_BUDGET[0], media.openverse_token, media.namesake = 50, (lambda: ""), (lambda p, t: False)
        saved_cache = media.OV_CACHE
        media.OV_CACHE = Path(tempfile.mkdtemp()) / "openverse_cache.json"
        try:
            got = media.openverse_photos("Paul George")
        finally:
            media.OV_CACHE = saved_cache
            (urllib.request.urlopen, time.sleep, media.OPENVERSE_BUDGET[0], media.openverse_token,
             media.namesake) = saved[:5]
            media.PHOTO_STATS.clear(); media.PHOTO_STATS.update(saved[5])
        self.assertEqual(len(got), 1)
        self.assertEqual(len(tries), 5)
        self.assertEqual(slept, [5, 10, 20, 30])
        self.assertEqual(sum(media.OPENVERSE_WAITS), 125)        # about two minutes at most


class TwoVersions(unittest.TestCase):
    """C1 (owner's plan, 2026-11-11): the channel lives on two accounts that clash. Run
    43066151290 had one ("wasn't paying attention" vs "said beforehand he wouldn't speak")."""

    def test_editor_names_it(self):
        import editor
        self.assertIn('"two_versions"', editor.PROMPT)
        self.assertIn("Never invent the other side", editor.PROMPT)

    def test_writer_and_critic(self):
        import script
        self.assertIn("TWO VERSIONS", script.PROMPT)
        self.assertIn("{two_versions}", script.PROMPT)
        self.assertIn("Never manufacture a contradiction", script.PROMPT)
        self.assertIn("TWO VERSIONS", script.HUMANIZE)
        self.assertIn("never invented", script.HUMANIZE)


class RumorLabels(unittest.TestCase):
    """C2 (owner's plan, 2026-11-11): one "reportedly" somewhere used to cover every rumor."""

    SPOKEN = ("Did the Lakers just put Austin Reaves on the table? Sources told ESPN the Lakers are "
              "shopping Reaves. The Kings want a guard before February. Windhorst thinks Reaves "
              "stays. So does LeBron keep his guard?")

    def claims(self, *pairs):
        return [{"text": t, "status": st, "source": 1} for st, t in pairs]

    def test_bare_rumor_caught_hedged_ones_pass(self):
        import compliance as C
        cl = self.claims(("ANONYMOUS", "The Lakers are shopping Austin Reaves"),
                         ("RUMOR", "The Kings want a guard before February"),
                         ("SPECULATION", "Windhorst thinks Reaves stays with the Lakers"))
        self.assertEqual(C.bare_claims(cl, self.SPOKEN), ["The Kings want a guard before February"])

    def test_facts_and_reports_untouched(self):
        import compliance as C
        cl = self.claims(("CONFIRMED", "Brown was traded to the 76ers for Paul George"),
                         ("REPORTED", "Brown said he did not intend to speak with Tatum"))
        self.assertEqual(C.bare_claims(cl, "Brown got traded to Philly for Paul George. Brown "
                                           "said beforehand he wouldn't speak with Tatum."), [])

    def test_gate_and_repair(self):
        import compliance as C
        import script
        cl = self.claims(("RUMOR", "The Kings want a guard before February"))
        v, notes, _ = C.check_claims(cl, [{"title": "x", "tier": 1, "text": "x"}], self.SPOKEN)
        self.assertEqual(v, C.REVIEW)
        self.assertTrue(any("sounds like a fact" in n for n in notes))
        beats = [{"say": "The Kings want a guard before February.", "stage": "setup"},
                 {"say": "I think the Lakers blink first, because Reaves is their second scorer.", "stage": "payoff"},
                 {"say": "So does LeBron keep his guard?", "stage": "exit"}]
        problems = script.repair_needed("Did LeBron's Lakers just shop Austin Reaves?", beats, {}, None, cl)
        self.assertTrue(any("sounds like a fact" in p for p in problems), problems)
        for word in ("ANONYMOUS", "SPECULATION", "IN ITS OWN SENTENCE"):
            self.assertIn(word, script.PROMPT)


class PodcastSources(unittest.TestCase):
    """C3 (owner's plan, 2026-11-11): beefs often start on podcasts (Arenas ripping Tatum and
    Brown, Stephen A. and Garnett). Articles about them come in through Google News."""

    def test_feeds(self):
        from sources import FEEDS
        by = {f["name"]: f for f in FEEDS}
        for name in ("GN: podcasts", "GN: podcast clash"):
            self.assertIn(name, by)
            self.assertEqual(by[name]["tier"], 2)            # never trusted alone for a rumor
            self.assertIn("when:1d", by[name]["url"])
            self.assertIn("-odds", by[name]["url"])          # betting previews kept out
        self.assertEqual(len(by), len(FEEDS))                # no name used twice


class HistoricBeefs(unittest.TestCase):
    """B20 / C4 (owner's plan, 2026-11-11): weak days get a famous beef that is back in the news."""

    def setUp(self):
        import tempfile
        import evergreen
        self.e = evergreen
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (evergreen.USED, evergreen.fresh_news, evergreen.wikipedia_item, evergreen.BANK)
        evergreen.USED = self.tmp / "evergreen_used.json"
        evergreen.BANK = [("Kobe Bryant", "Shaquille O'Neal", "the Kobe and Shaq feud"),
                          ("Michael Jordan", "Isiah Thomas", "the Jordan and Isiah feud"),
                          ("Kevin Durant", "Russell Westbrook", "Durant and Westbrook")]
        news = {"Kobe Bryant": 3, "Michael Jordan": 1, "Kevin Durant": 2}

        def fake(a, b, tier1=()):
            return [{"title": f"{a} recalls the {b} story {k}", "link": f"https://x/{a}{k}", "publisher": "P",
                     "tier": 2, "about": True} for k in range(news[a])]
        evergreen.fresh_news = fake
        evergreen.wikipedia_item = lambda a, b: {"title": "Feud (Wikipedia)", "link": "https://en.wikipedia.org/wiki/F",
                                                 "publisher": "Wikipedia", "tier": 1}
        import editor                       # never read the real made history in a test
        self.made, self.saved_made = [], editor.made_recently
        editor.made_recently = lambda: list(self.made)

    def tearDown(self):
        import editor
        editor.made_recently = self.saved_made
        self.e.USED, self.e.fresh_news, self.e.wikipedia_item, self.e.BANK = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_fill(self, shorts):
        import script
        saved = (script.build_short, script.OUT)
        script.OUT = self.tmp
        script.build_short = lambda n, tid, editor, voice, formulas: {"headline": editor["topics"][tid]["headline"], "beats": []}
        try:
            editor = {"topics": [], "ranked": []}
            self.assertFalse(script.fill_with_evergreen(shorts, editor, "", {}))
        finally:
            script.build_short, script.OUT = saved

    def test_same_feud_in_48_hours_is_skipped(self):
        """35. Run 43208765485: Draymond vs Poole made 17 h after a Short on the same two people."""
        import datetime as dt
        import editor
        recent = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=17)).isoformat()
        self.made = [{"time": recent, "headline": "Fans mock Kobe's claim he'd have no issue with O'Neal",
                      "hook": "Did Kobe really say that?"}]
        shorts = [{"headline": "today's strong story"}]
        self.run_fill(shorts)
        self.assertEqual(len(shorts), 2)
        self.assertNotEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        self.assertNotIn(self.e.key_of("Kobe Bryant", "Shaquille O'Neal"), self.e.used())   # not used up
        # older than 48 hours: allowed again
        self.made[0]["time"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=50)).isoformat()
        self.assertEqual(editor.pair_made_recently(["Kobe Bryant", "Shaquille O'Neal"], self.made), "")
        # only ONE of the two people in that Short: not the same feud
        self.made[0].update(time=recent, headline="Shaq rips the Lakers' bench", hook="Is Shaq right?")
        self.assertEqual(editor.pair_made_recently(["Kobe Bryant", "Shaquille O'Neal"], self.made), "")

    def test_same_feud_already_made_this_run_is_skipped(self):
        import datetime as dt
        import editor
        shorts = [{"headline": "Shaquille O'Neal fires back at Kobe Bryant's old teammate", "hook": {"text": "Shaq just fired back at Kobe."}}]
        self.run_fill(shorts)
        self.assertEqual(len(shorts), 2)
        self.assertNotEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        real = [{"time": "2026-11-11T18:46+00:00",
                 "headline": "'Would Welcome With Closed Fists,' 'Stop Lying' - NBA Fans Mock Draymond Green's Claim "
                             "That He'd Have 'No Issue' With Jordan Poole Warriors Reunion", "hook": ""}]
        now = dt.datetime(2026, 11, 12, 11, 28, tzinfo=dt.timezone.utc)
        self.assertTrue(editor.pair_made_recently(["Draymond Green", "Jordan Poole"], real, now))

    def test_only_fresh_and_not_recent(self):
        e = self.e
        got = e.candidates()
        self.assertEqual([c["key"] for c in got], [e.key_of("Kobe Bryant", "Shaquille O'Neal"),
                                                   e.key_of("Kevin Durant", "Russell Westbrook")])  # Jordan: 1 article
        self.assertIn("OLD", got[0]["why"])
        self.assertIn("NEVER present the old events as new", got[0]["why"])
        self.assertEqual(got[0]["items"][-1]["publisher"], "Wikipedia")
        e.mark_used(got[0]["key"])
        self.assertNotIn(got[0]["key"], [c["key"] for c in e.candidates()])          # 90 days
        import datetime as dt
        later = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=e.REUSE_DAYS + 1)
        self.assertIn(got[0]["key"], [c["key"] for c in e.candidates(now=later)])

    def test_about_them_not_just_named(self):
        e = self.e
        self.assertTrue(e.about_them("Derek Fisher on the Shaq and Kobe relationship: iron sharpening iron"))
        self.assertTrue(e.about_them("Kyrie Irving explains why he will not follow LeBron James path"))
        self.assertFalse(e.about_them("Thunder's Shai Gilgeous-Alexander Threatens Kevin Durant, Russell Westbrook Record"))
        only_named = [{"title": "SGA threatens Durant and Westbrook record", "link": "https://x/1", "tier": 2, "about": False},
                      {"title": "Durant and Westbrook record in danger", "link": "https://x/2", "tier": 2, "about": False}]
        e.fresh_news = lambda a, b, tier1=(): only_named if a == "Kevin Durant" else []
        self.assertEqual(e.candidates(), [])                     # named in passing only: not chosen

    def test_fills_only_the_empty_slot(self):
        import script
        saved = (script.build_short, script.OUT)
        made = []
        script.OUT = self.tmp
        script.build_short = lambda n, tid, editor, voice, formulas: (
            made.append(editor["topics"][tid]["headline"]) or {"headline": editor["topics"][tid]["headline"], "beats": []})
        try:
            editor = {"topics": [], "ranked": []}
            shorts = [{"headline": "today's strong story"}]
            self.assertFalse(script.fill_with_evergreen(shorts, editor, "", {}))
        finally:
            script.build_short, script.OUT = saved
        self.assertEqual(len(shorts), script.SHORTS_PER_RUN)                       # quota kept: one added
        self.assertEqual(len(made), 1)
        self.assertEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        self.assertIn(shorts[1]["evergreen"], self.e.used())
        self.assertTrue(editor["topics"][0]["verified"])

    def test_a_failure_never_costs_the_day(self):
        import script
        saved = script.build_short

        def boom(*a, **k):
            raise ValueError("not enough material")
        script.build_short = boom
        try:
            shorts = [{"headline": "x"}]
            self.assertFalse(script.fill_with_evergreen(shorts, {"topics": [], "ranked": []}, "", {}))
            self.assertEqual(len(shorts), 1)
            self.assertEqual(self.e.used(), {})                                        # nothing marked
        finally:
            script.build_short = saved


class StaleWikidata(CurrentTeam):
    """29. Run 43080115985: Jordan Poole's Wikidata spells have no dates and still say Golden
    State; his 2018 Michigan photos were not marked PRE-NBA."""

    def test_undated_current_team_not_trusted(self):
        m = self.m
        self.CLAIMS["Q50820763"] = [
            {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal", "qualifiers": {}},
            {"mainsnak": {"datavalue": {"value": {"id": "Q169165"}}}, "rank": "normal",
             "qualifiers": {"P582": [{"datavalue": {"value": {"time": "+2024-01-01T00:00:00Z"}}}]}}]
        self.LABELS.update({"Q157376": "Golden State Warriors", "Q169165": "Washington Wizards"})
        m._wikidata["Jordan Poole"] = "Q50820763"
        try:
            self.assertEqual(m.teams_of("Jordan Poole"), ("", set()))
            self.assertEqual(m.people_line(["Jordan Poole"]), "Jordan Poole")    # no false "now with"
        finally:
            del self.CLAIMS["Q50820763"]

    def test_college_photo_by_its_text(self):
        m = self.m
        self.assertEqual(m.photo_team("Jordan Poole", "20180206 UM-NW Jordan Poole Category:Michigan Wolverines men's basketball players"), "pre-nba")
        self.assertEqual(m.photo_team("Jaylen Brown", "20150401 MCDAAG Jaylen Brown dunk"), "pre-nba")
        self.assertNotEqual(m.photo_team("Kevin Durant", "Kevin Durant United States men's national basketball team 2012"), "pre-nba")
        self.assertNotEqual(m.photo_team("Draymond Green", "Draymond Green 2022 Warriors"), "pre-nba")
        self.assertNotEqual(m.photo_team("Jaylen Brown", "Jaylen Brown NBA Summer League 2016 college"), "pre-nba")

    def test_former_role_rule(self):
        import script
        self.assertIn("a FORMER role stays former", script.PROMPT)


class OpenverseKept(unittest.TestCase):
    """30. Run 43080115985: 3 of 5 Openverse searches still 504 after ~2 minutes of tries."""

    def setUp(self):
        import media
        self.m = media
        self.saved = media.OV_CACHE
        media.OV_CACHE = Path(tempfile.mkdtemp()) / "openverse_cache.json"

    def tearDown(self):
        shutil.rmtree(self.m.OV_CACHE.parent, ignore_errors=True)
        self.m.OV_CACHE = self.saved

    def test_kept_and_used_when_openverse_fails(self):
        import datetime as dt
        m = self.m
        photo = {"kind": "photo", "url": "https://x/1.jpg", "title": "Doc Rivers", "score": 3}
        m.openverse_keep("Doc Rivers", [photo])
        self.assertEqual(m.openverse_cached("Doc Rivers"), [photo])
        self.assertEqual(m.openverse_cached("Jordan Poole"), [])
        old = json.loads(m.OV_CACHE.read_text())
        old["Doc Rivers"]["day"] = (dt.date.today() - dt.timedelta(days=m.OV_CACHE_DAYS)).isoformat()
        m.OV_CACHE.write_text(json.dumps(old))
        self.assertEqual(m.openverse_cached("Doc Rivers"), [])             # too old: not used
        m.openverse_keep("Paul George", [photo])
        self.assertNotIn("Doc Rivers", json.loads(m.OV_CACHE.read_text()))  # and dropped on write

    def test_a_failed_search_returns_the_kept_one(self):
        import urllib.error
        import urllib.request
        import time
        m = self.m
        photo = {"kind": "photo", "url": "https://x/2.jpg", "title": "Doc Rivers", "score": 3}
        m.openverse_keep("Doc Rivers", [photo])
        saved = (urllib.request.urlopen, time.sleep, m.OPENVERSE_BUDGET[0], m.openverse_token, dict(m.PHOTO_STATS))

        def always_504(req, timeout=30):
            raise urllib.error.HTTPError(req.full_url, 504, "Gateway Timeout", {}, None)
        urllib.request.urlopen, time.sleep = always_504, (lambda s: None)
        m.OPENVERSE_BUDGET[0], m.openverse_token = 50, (lambda: "")
        try:
            got = m.openverse_photos("Doc Rivers")
            note = m.PHOTO_STATS["Doc Rivers"]["openverse"]
        finally:
            urllib.request.urlopen, time.sleep, m.OPENVERSE_BUDGET[0], m.openverse_token = saved[:4]
            m.PHOTO_STATS.clear(); m.PHOTO_STATS.update(saved[4])
        self.assertEqual(got, [photo])
        self.assertIn("kept", note)


class Initials(unittest.TestCase):
    """31. Run 43088629255: "So was Stephen A. smart to stand down from LeBron, or did money
    win?" was cut after "A.", the piece "So was Stephen A." counted as a repeat, Short held."""

    BEATS = [{"say": "LeBron confronted Stephen A. over his Bronny comments, and he let it go.", "stage": "setup"},
             {"say": "He told Kevin Garnett why: \"It's the first day of my new contract.\" 100 million from ESPN.", "stage": "conflict"},
             {"say": "He says he knew it would be a problem.", "stage": "escalation"},
             {"say": "I think that was smart: no argument is worth that kind of money. Now he says he's over it.", "stage": "payoff"},
             {"say": "So was Stephen A. smart to stand down from LeBron, or did money win?", "stage": "exit"}]

    def test_split(self):
        import compliance as C
        self.assertEqual(C.split_sentences("So was Stephen A. smart? Yes. J.R. Smith said no. Then Brown left."),
                         ["So was Stephen A. smart?", "Yes.", "J.R. Smith said no.", "Then Brown left."])
        self.assertEqual(C.split_sentences("Gary Payton Jr. scored. Dr. J smiled."), ["Gary Payton Jr. scored.", "Dr. J smiled."])

    def test_the_held_short_passes(self):
        import script
        self.assertEqual(script.retention_check(self.BEATS)["hard"], [])
        repeat = [dict(b) for b in self.BEATS]
        repeat[4]["say"] = "No argument is worth that kind of money. So was Stephen A. smart, or did money win?"
        self.assertIn("beat 5 repeats what was already said", script.retention_check(repeat)["hard"])   # real repeats still caught


class OneFeudIn48Hours(unittest.TestCase):
    """32. The made history of 2026-11-11 and the topics of run 43088629255."""

    MADE = [{"time": "2026-11-11T13:20+00:00",
             "headline": "Jayson Tatum won't give air to Jaylen Brown drama after snub",
             "hook": "Did Jaylen Brown just ignore Jayson Tatum twice?"},
            {"time": "2026-11-11T18:46+00:00",
             "headline": "Players Should Start Talking Crazy About Coaches Too - Draymond Green Calls Out Doc Rivers",
             "hook": "Is Draymond Green about to turn NBA players loose on coaches over Giannis Antetokounmpo?"}]

    def topic(self, headline, *stars):
        return {"headline": headline, "star_names": [f"{n} 2.0" for n in stars]}

    def setUp(self):
        import datetime as dt
        import editor
        self.e, self.now = editor, dt.datetime(2026, 11, 11, 19, 40, tzinfo=dt.timezone.utc)

    def test_same_feud_is_a_repeat(self):
        t = self.topic("Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win",
                       "Jaylen Brown", "Jayson Tatum", "Paul George")
        self.assertIn("won't give air", self.e.same_feud_recent(t, self.MADE, self.now))

    def test_exceptions(self):
        e, now = self.e, self.now
        # a major turn
        self.assertEqual(e.same_feud_recent(self.topic("Jaylen Brown fined after Jayson Tatum altercation",
                                                       "Jaylen Brown", "Jayson Tatum"), self.MADE, now), "")
        # another person's own story (only one of them in the headline)
        self.assertEqual(e.same_feud_recent(self.topic("Paul George explains his middle finger to a 76ers fan",
                                                       "Jaylen Brown", "Jayson Tatum", "Paul George"), self.MADE, now), "")
        # a new voice leads: Garnett was not in the earlier Short
        self.assertEqual(e.same_feud_recent(self.topic("Kevin Garnett rips Jaylen Brown and Jayson Tatum",
                                                       "Jaylen Brown", "Jayson Tatum", "Kevin Garnett"), self.MADE, now), "")
        # after 48 hours the feud is open again
        import datetime as dt
        later = now + dt.timedelta(hours=49)
        self.assertEqual(e.same_feud_recent(self.topic("Jayson Tatum responds to Jaylen Brown",
                                                       "Jaylen Brown", "Jayson Tatum"), self.MADE, later), "")

    def test_the_editor_drops_it(self):
        import json as _j
        e = self.e
        topics = [self.topic("Jayson Tatum responds to Jaylen Brown snub", "Jaylen Brown", "Jayson Tatum"),
                  self.topic("Stephen A. Smith stood down from LeBron James", "LeBron James")]
        for t in topics:
            t["items"] = [{"title": t["headline"], "tier": 1, "link": "https://x", "publisher": "ESPN"}]
        raw = _j.dumps({"ranked": [{"id": 0, "nba": True, "kind": "player_vs_player", "virality": 9, "drama": 9,
                                    "star_power": 9, "debate": 9, "repeat": False, "why": "", "same_as": []},
                                   {"id": 1, "nba": True, "kind": "player_vs_media", "virality": 7, "drama": 7,
                                    "star_power": 7, "debate": 7, "repeat": False, "why": "", "same_as": []}],
                        "shorts": [0, 1], "long": {}})
        saved = e.made_recently
        e.made_recently = lambda: [{**self.MADE[0], "time": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="minutes")}]
        try:
            data = e.parse(raw, 2, topics)
        finally:
            e.made_recently = saved
        self.assertEqual(data["shorts"], [1])
        self.assertTrue(data["ranked"][0]["repeat"])

    def test_rule_told_to_the_editor(self):
        import editor
        self.assertIn("ONE FEUD, ONE SHORT IN 48 HOURS", editor.history_note.__code__.co_consts.__repr__())


class Run43199348111(unittest.TestCase):
    """33. "Ayesha Curry's kiss" (the source: an ON-SCREEN kiss); Charles Bassey's photo twice;
    a painting for Marcus Smart; Google News links in the description."""

    CLAIM = [{"status": "CONFIRMED", "source": 1,
              "text": "Arenas and Nick Young criticized Ayesha Curry's on-screen kiss on the We Said What We Said podcast"}]

    def test_meaning_word(self):
        import compliance as C
        import script
        bad = "Arenas and Steph's old teammate Nick Young picked apart Ayesha Curry's kiss on their podcast."
        good = "Arenas and Steph's old teammate Nick Young picked apart Ayesha Curry's on-screen kiss on their podcast."
        self.assertEqual(len(C.dropped_meaning(self.CLAIM, bad)), 1)
        self.assertEqual(C.dropped_meaning(self.CLAIM, good), [])
        v, notes, _ = C.check_claims(self.CLAIM, [{"title": "x", "tier": 1, "text": "x"}], bad)
        self.assertIn(v, (C.REVIEW, C.REJECT))                      # never PASS
        self.assertTrue(any("changes what happened" in n for n in notes), notes)
        beats = [{"say": bad, "stage": "setup"},
                 {"say": "I think Young was smart, because he kept Steph and left Gil explaining himself.", "stage": "payoff"},
                 {"say": "So who owes Steph the better apology, Arenas or Young?", "stage": "exit"}]
        problems = script.repair_needed("Did Gilbert Arenas really call Ayesha Curry a blemish?", beats, {}, None, self.CLAIM)
        self.assertTrue(any("changes what happened" in p for p in problems), problems)
        self.assertIn("on-screen", script.PROMPT)
        self.assertIn("MEANING WORDS", script.HUMANIZE)

    def test_same_file_two_sources(self):
        from picture_ids import already_shown, mark_shown
        commons = _commons("Charles Bassey San Antonio Spurs 2024.jpg")
        via_ov = {"kind": "photo", "source": "Wikimedia via Openverse", "title": "Charles Bassey San Antonio Spurs 2024",
                  "page": "https://commons.wikimedia.org/w/index.php?curid=1", "url": "https://upload.wikimedia.org/x.jpg"}
        shown = set()
        mark_shown(commons, shown)
        self.assertTrue(already_shown(via_ov, shown))

    def test_full_name_as_one_phrase(self):
        import media
        self.assertFalse(media.names_together("Marcus Smart", "Profile portrait of a smart young man by S. M. Marcus (c.1840)"))
        self.assertTrue(media.names_together("Marcus Smart", "Marcus Smart (51688317634) basketball"))
        self.assertTrue(media.names_together("Shai Gilgeous-Alexander", "Shai Gilgeous-Alexander dunks"))
        self.assertTrue(media.names_together("Stephen Curry", "stephen curry warriors"))

    def test_description_links_the_article(self):
        import inspect
        import script
        self.assertIn("s.get('url') or s['link']", inspect.getsource(script))


class StatedShockHook(unittest.TestCase):
    """34. Owner, 2026-11-12: "Did Gilbert Arenas really call...?" is not shocking enough;
    "Gilbert Arenas called Ayesha Curry the only blemish..." is. The first 3 seconds decide."""

    # his rule 2026-11-14: a hook fits the first 3-4 seconds = 8-12 words (the old fixtures had 13 and 15)
    STATED = "Gilbert Arenas called Ayesha Curry the only blemish on Steph's family."
    ASKED = "Did Gilbert Arenas really call Ayesha Curry the Curry family's blemish?"

    def test_statement_is_a_valid_hook_and_ranks_first(self):
        import script
        self.assertTrue(script.one_question(self.STATED))
        self.assertTrue(script.one_question(self.ASKED))              # a question still works
        self.assertFalse(script.one_question("Arenas. Curry. Blemish."))  # never two sentences
        self.assertGreater(script.nba_hook_score(self.STATED)[1], script.nba_hook_score(self.ASKED)[1])
        self.assertIn("question, not a stated shock", [f for f, _ in script.hook_flaws(self.ASKED)])
        self.assertGreaterEqual(script.nba_hook_score(self.STATED)[1], 40)  # usable: no extra rewrite call
        hooks = [{"text": self.ASKED, "question": True, "score": 50},
                 {"text": self.STATED, "question": True, "score": 41}]
        hooks.sort(key=script.hook_rank)
        self.assertEqual(hooks[0]["text"], self.STATED)

    def test_rules_and_safety(self):
        import script
        p = script.PROMPT
        for need in ("THE HOOK IS A SHOT, NOT A QUESTION", "first 8 words", "Shams: the Lakers",
                     "a question hook only when the story has no shocking fact"):
            self.assertIn(need, p, need)
        self.assertIn("8-12 words", script.HOOK_RETRY if hasattr(script, "HOOK_RETRY") else p)   # his rule 2026-11-14
        self.assertNotIn("8-14 words", p)
        self.assertFalse(script.one_question("Gilbert Arenas just called Ayesha Curry the only blemish on the Curry family."))  # 14: too long now
        self.assertIn("PUNCH:", script.HUMANIZE)
        # audit 2026-11-13: no other line of the prompt may give the hook another length
        self.assertNotIn("10-18 words", p)
        self.assertNotIn("10-24 words", p)
        # a stated rumor without its source is still caught by the rumor check (C2)
        import compliance as C
        cl = [{"status": "RUMOR", "text": "The Lakers are shopping Austin Reaves before the deadline", "source": 1}]
        self.assertTrue(C.bare_claims(cl, "The Lakers are shopping Austin Reaves before the deadline."))
        self.assertFalse(C.bare_claims(cl, "Shams: the Lakers are shopping Austin Reaves before the deadline."))
        # a team name before the colon is a headline, not a source
        self.assertTrue(C.bare_claims(cl, "Lakers: they are shopping Austin Reaves before the deadline."))


class EveryPhotoLookedAt(unittest.TestCase):
    """36. Owner, 2026-11-12: the editor saw 3 of Curry's 94 photos per beat (the first 12 only),
    and 5 White House shots went into an injury Short. Now every photo is tagged once, the tags
    are kept, and each beat gets the photos that fit its line. Offline: Claude and downloads faked."""

    def setUp(self):
        import tempfile
        import photo_tags
        import media
        self.t, self.m = photo_tags, media
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (photo_tags.CACHE, photo_tags.fetch_thumbs, photo_tags._sleep)
        photo_tags.CACHE = self.tmp / "tags.json"
        photo_tags._sleep = lambda s: None

        def thumbs(urls, folder, ua):
            out = []
            for k, u in enumerate(urls):
                p = folder / f"t{k}.jpg"
                self.fake_download(u, p)
                out.append(p)
            return out
        photo_tags.fetch_thumbs = thumbs

    def tearDown(self):
        self.t.CACHE, self.t.fetch_thumbs, self.t._sleep = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ph(self, n, date="2022-02-20", author="Erik Drost"):
        return {"kind": "photo", "page": f"p{n}", "title": f"Steph Curry ({51900000000 + n}).jpg",
                "url": f"https://x/{n}.jpg", "author": author, "date": date}

    def fake_download(self, url, path, timeout=60):
        from PIL import Image
        Image.new("RGB", (500, 400), (int(url.split("/")[-1].split(".")[0]) * 7 % 255, 80, 80)).save(path)
        return True

    def test_parse_keeps_only_known_values(self):
        tags, groups = self.t.parse_tags({"photos": [
            {"n": 1, "v": "C", "s": "game", "e": "sad", "t": "walks off head down"},
            {"n": 2, "v": "a", "s": "made-up", "e": "x", "t": ""},
            {"n": 9, "v": "C"}, {"n": "x"}, {"v": "C"}],
            "same": [[1, 2], [3], ["7", 8, 99]]}, 8)
        self.assertEqual(set(tags), {1, 2})
        self.assertEqual(tags[2]["s"], "other")
        self.assertEqual(groups, [[1, 2], [7, 8]])

    def test_tagged_once_kept_and_same_moment_marked(self):
        pool = [self.ph(n) for n in range(1, 12)]
        calls = []

        def ask(prompt, folder=None, timeout=0, **kw):
            calls.append(sorted(os.listdir(folder)))
            self.assertIn("Steph Curry", prompt)
            return {"photos": [{"n": k, "v": "A" if k == 11 else "C", "s": "game", "e": "calm", "t": "plays"}
                               for k in range(1, 12)], "same": [[2, 3]]}
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        self.assertEqual(n, 11)
        self.assertEqual(calls, [["tags_1.jpg", "tags_2.jpg"]])          # 9 a sheet
        self.assertEqual(pool[1]["moment"], pool[2]["moment"])
        self.assertFalse(self.t.usable(pool[10]))
        fresh = [self.ph(n) for n in range(1, 12)]
        self.assertEqual(self.t.tag_person("Steph Curry", fresh, ask, "ua",
                                           self.m.photo_era, self.m.scene_of), 0)
        self.assertEqual(len(calls), 1)                                   # kept: no second look
        self.assertEqual(fresh[0]["tag"]["s"], "game")
        self.assertEqual(fresh[1]["moment"], fresh[2]["moment"])

    def test_big_pools_are_asked_in_parts_and_a_broken_answer_once_more(self):
        """Preview 43222583073: one call for 120+ photos returned broken JSON and the whole Short
        fell back. Now 45 a call; a broken answer is asked again once, then only that part waits."""
        pool = [self.ph(n) for n in range(1, 101)]
        calls = []

        def ask(prompt, folder=None, timeout=0, **kw):
            calls.append(len(os.listdir(folder)))
            if len(calls) in (2, 4, 5):
                raise ValueError("Expecting ',' delimiter")
            n = len(os.listdir(folder)) and min(45, 100 - 45 * (0 if len(calls) == 1 else 1 if len(calls) == 3 else 2))
            return {"photos": [{"n": k, "v": "C", "s": "game", "e": "calm", "t": "x"} for k in range(1, n + 1)]}
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        # 45 + 45 + 10 photos; part 2 asked twice; the last part failed twice, so its 10 photos get
        # one more look (owner, 2026-11-13), which answers
        self.assertEqual(calls, [5, 5, 5, 2, 2, 2])
        self.assertEqual(n, 100)
        self.assertTrue(all(c.get("tag") for c in pool))

    def test_a_broken_answer_keeps_its_good_entries(self):
        """40. Run 43288011054: one broken spot in a 45-photo answer, twice, lost all 45 tags."""
        broken = ('{"photos":[{"n":1,"v":"C","s":"game","e":"sad","t":"walks off"},\n'
                  '{"n":2,"v":"C","s":"game","e":"calm","t":"holds the "MVP" trophy"},\n'
                  '{"n":3,"v":"A","s":"other","e":"unclear","t":"popcorn"}\n'
                  '{"n":4,"v":"S","s":"bench","e":"calm","t":"sits"}],"same":[[1,4]]}')
        out = self.t.parse_answer(broken)
        self.assertEqual([p["n"] for p in out["photos"]], [1, 3, 4])      # only the broken entry is lost
        self.assertEqual(out["same"], [[1, 4]])
        self.assertEqual(self.t.parse_answer({"photos": []}), {"photos": []})
        with self.assertRaises(ValueError):
            self.t.parse_answer("Sorry, I cannot see the sheets.")
        pool = [self.ph(n) for n in range(1, 5)]
        answers = [broken, '{"photos":[{"n":1,"v":"C","s":"game","e":"smiling","t":"holds the MVP trophy"}]}']
        sheets_seen = []

        def ask(prompt, folder=None, timeout=0, **kw):
            sheets_seen.append(len(os.listdir(folder)))
            return answers.pop(0)
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        # owner, 2026-11-13: the photo whose entry broke is looked at again, not left out
        self.assertEqual(n, 4)
        self.assertEqual(sheets_seen, [1, 1])
        self.assertEqual(pool[1]["tag"]["t"], "holds the MVP trophy")
        self.assertTrue(all(c.get("tag") for c in pool))

    def test_untagged_photo_never_fills_when_the_person_has_tags(self):
        m = self.m
        pool = [{**self.ph(1), "title": "Steph Curry golf.jpg"},                       # nobody looked at it
                {**self.ph(2), "title": "Steph Curry game.jpg", "tag": {"v": "C", "s": "game"}, "hoops": True}]
        saved = m.photos
        try:
            m.photos = lambda who: pool
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p2"])
            m.photos = lambda who: [{**self.ph(1), "title": "Steph Curry golf.jpg"}]   # nobody tagged: as before
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p1"])
        finally:
            m.photos = saved

    def test_thumbnails_one_at_a_time_and_stop_on_a_second_429(self):
        import urllib.error
        import urllib.request
        t = self.t
        t.fetch_thumbs = self.saved[1]
        seen, slept = [], []
        t._sleep = slept.append

        class Resp:
            def __init__(self, b): self.b = b
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return self.b

        def fake_open(req, timeout=0):
            seen.append(req.full_url)
            if req.full_url.endswith("/2.jpg"):
                raise urllib.error.HTTPError(req.full_url, 429, "slow down", {"Retry-After": "7"}, None)
            from io import BytesIO
            from PIL import Image
            buf = BytesIO()
            Image.new("RGB", (50, 50)).save(buf, "JPEG")
            return Resp(buf.getvalue())
        saved_open = urllib.request.urlopen
        urllib.request.urlopen = fake_open
        try:
            got = t.fetch_thumbs([f"https://upload.wikimedia.org/{k}.jpg" for k in range(1, 7)], self.tmp, "ua")
        finally:
            urllib.request.urlopen = saved_open
        self.assertEqual([bool(x) for x in got], [True, False, False, False, False, False])
        self.assertEqual(len(seen), 3)                # 1 ok; 2: 429, waited 7 s, 429 again: stop
        self.assertIn(7.0, slept)
        self.assertIn(t.PACE, slept)

    def test_same_moment_is_one_picture(self):
        from picture_ids import already_shown, mark_shown
        a, b = {**self.ph(33), "moment": "p33"}, {**self.ph(34), "moment": "p33"}
        shown = set()
        mark_shown(a, shown, a["page"])
        self.assertTrue(already_shown(b, shown, b["page"]))
        self.assertFalse(already_shown(self.ph(35), shown, "p35"))

    def test_shortlist_reads_tags_and_skips_absent(self):
        curry = [{**self.ph(n), "tag": {"v": v, "s": s, "e": e, "t": t}} for n, (v, s, e, t) in enumerate([
            ("C", "political", "smiling", "with Biden at the White House"),
            ("C", "game", "sad", "walks off head down, Warriors jersey"),
            ("A", "other", "unclear", "popcorn bucket"),
            ("O", "game", "calm", "Jokic shoots")])]
        seen = {}

        def ask(prompt, folder=None, timeout=0, **kw):
            seen["prompt"] = prompt
            return {"beats": [{"beat": 0, "photos": ["a1", "a0", "a2", "zz", "a1"]}, {"beat": "x"}]}
        got = self.t.shortlists([{"say": "Curry left with an abdominal injury."}], [{"person": "Steph Curry"}],
                                ["Steph Curry"], "Curry hurt", {"Steph Curry": curry}, ask,
                                self.m.photo_era, self.m.scene_of)
        self.assertEqual([c["page"] for c in got[0]], ["p1", "p0"])       # absent / unknown ids dropped
        self.assertNotIn("popcorn", seen["prompt"])
        self.assertNotIn("Jokic", seen["prompt"])
        self.assertIn("walks off head down", seen["prompt"])
        self.assertIn('"political"', seen["prompt"])
        self.assertIsNone(self.t.shortlists([{"say": "x"}], [{}], ["Steph Curry"], "s",
                                            {"Steph Curry": curry[2:]}, ask, self.m.photo_era, self.m.scene_of))

    def test_beat_sees_the_shortlist(self):
        m = self.m
        tagged = [{**self.ph(n), "tag": {"v": "C", "s": "game", "e": "calm", "t": "x"}} for n in range(20)]
        untagged = [self.ph(100 + n) for n in range(5)]
        saved = {k: getattr(m, k) for k in ("photos", "download", "image_ok", "commons_videos", "pixabay_videos")}
        try:
            m.photos = lambda who: tagged if who == "Steph Curry" else untagged
            m.download, m.image_ok = self.fake_download, (lambda p: True)
            m.commons_videos = lambda *a, **k: []
            m.pixabay_videos = lambda q: []
            got = m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 0, set(), "Steph Curry",
                               ("Kevin Durant",), tagged[5:13])
            self.assertEqual([c["page"] for c in got], [f"p{n}" for n in range(5, 13)] + ["p100", "p101", "p102"])  # Durant untagged: as before
            old = m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 0, set(), "Steph Curry", (), None)
            self.assertEqual(len(old), m.MAX_PHOTOS)                      # no tags: the old way
        finally:
            for k, v in saved.items():
                setattr(m, k, v)

    def test_round_two_never_brings_back_untagged_first_photos(self):
        """Audit 2026-11-13: round 2 called candidates() without the shortlist, so a tagged
        person's first photos in the old order came back (absent, political...)."""
        m = self.m
        tagged = [{**self.ph(n), "tag": {"v": "C", "s": "game", "e": "calm", "t": "x"}} for n in range(10)]
        saved = {k: getattr(m, k) for k in ("photos", "download", "image_ok", "commons_videos", "pixabay_videos")}
        try:
            m.photos = lambda who: tagged
            m.download, m.image_ok = self.fake_download, (lambda p: True)
            m.commons_videos = lambda *a, **k: []
            m.pixabay_videos = lambda q: []
            self.assertEqual(m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 100, set(),
                                          "Steph Curry", (), []), [])
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
        import inspect
        src = inspect.getsource(m.collect_for)
        self.assertIn('[] if lists is not None else None)', src[src.index("round 2 adds footage"):])

    def test_big_beats_get_more_sheets(self):
        m = self.m
        from PIL import Image
        cands = []
        for n in range(17):
            p = self.tmp / f"c{n}.jpg"
            Image.new("RGB", (600, 800), "gray").save(p)
            cands.append({"kind": "photo", "thumb": str(p)})
        m.contact_sheet(cands, self.tmp / "beat_3.jpg", "BEAT 3: x")
        names = sorted(x.name for x in self.tmp.glob("beat_3*.jpg"))
        self.assertEqual(names, ["beat_3.jpg", "beat_3_2.jpg"])           # 4 a row, 3 rows a sheet
        with Image.open(self.tmp / "beat_3.jpg") as im:
            self.assertLessEqual(im.height, 1600)
        self.assertIn("beat_0_2.jpg", m.PICK_PROMPT)

    def test_unjudged_top_ups_use_the_tags(self):
        m = self.m
        pool = [{**self.ph(1), "title": "Steph Curry White House.jpg", "tag": {"v": "C", "s": "political"}},
                {**self.ph(6), "title": "Steph Curry Davidson.jpg", "team": "pre-nba"},
                {**self.ph(2), "title": "Steph Curry popcorn.jpg", "tag": {"v": "A", "s": "other"}},
                {**self.ph(3), "title": "Steph Curry stage.jpg", "tag": {"v": "C", "s": "stage"}},
                {**self.ph(4), "title": "Steph Curry far.jpg", "tag": {"v": "S", "s": "game"}, "hoops": True},
                {**self.ph(5), "title": "Steph Curry game.jpg", "tag": {"v": "C", "s": "game"}, "hoops": True}]
        saved = m.photos
        try:
            m.photos = lambda who: pool
            # p4 is only a small figure (v S): not used unjudged since run 43317261723 (D15)
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p5"])
        finally:
            m.photos = saved

    def test_rules_in_the_prompts(self):
        m, t = self.m, self.t
        self.assertIn("POLITICAL event", m.PICK_PROMPT)
        self.assertIn("the line is about that very event or that politician", m.PICK_PROMPT)
        for need in ('"A" = he is NOT in it', '"O" = the photo is about SOMEONE ELSE', "THE SAME MOMENT", "Never guess"):
            self.assertIn(need, t.TAG_PROMPT)
        for need in ("WHO first", "Fit the MOMENT", "at most 3 photos with the same sc", '"political"'):
            self.assertIn(need, t.PICK_PROMPT)

    def test_a_failure_falls_back_to_the_first_photos(self):
        m = self.m
        saved = {k: getattr(m, k) for k in ("photos", "people")}
        errors = list(m.MEDIA_ERRORS)
        try:
            m.people = lambda short: ["Steph Curry"]

            def boom(who):
                raise ValueError("Commons down")
            m.photos = boom
            self.assertIsNone(m.shortlist_photos({"headline": "x"}, [{"say": "x"}], [{"person": "Steph Curry"}]))
            self.assertTrue(any("photo tags" in e for e in m.MEDIA_ERRORS))
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
            m.MEDIA_ERRORS[:] = errors


class HookDetailInSourceWords(unittest.TestCase):
    """38. Run 43262308476: the fan's pick "...cussed him out over one radio comment in 2012." lost
    to a weaker hook because the source says "on ESPN 1000's Waddle & Silvy", never "radio". The
    detail is put in the sources' words; the new line must pass the checks again."""

    SRC = [{"title": "Charles Barkley recalls Michael Jordan", "summary": "", "tier": 1, "publisher": "ES",
            "text": "On ESPN 1000's Waddle & Silvy, Barkley said Jordan needed to stop hiring yes-men. "
                    "Jordan didn't take it well. And he is cussing me up and down, that's the last time we spoke."}]
    HOOK = "Charles Barkley says Michael Jordan cussed him out over one radio comment in 2012."

    def run_fix(self, answer):
        import script
        import compliance
        hook = {"text": self.HOOK, "score": 51, "question": True, "intrigue_pick": True,
                "unsupported_details": compliance.unsupported_details(self.HOOK, self.SRC)}
        self.assertEqual(hook["unsupported_details"], ["radio"])
        saved = script.ask_claude
        seen = {}

        def ask(prompt, model=""):
            seen["prompt"], seen["model"] = prompt, model
            if isinstance(answer, Exception):
                raise answer
            return {"text": answer}
        script.ask_claude = ask
        try:
            return script.fix_hook_detail(hook, self.SRC), hook, seen
        finally:
            script.ask_claude = saved

    def test_detail_in_the_sources_words_keeps_the_hook(self):
        import script
        ok, hook, seen = self.run_fix("Charles Barkley says Jordan cussed him out over an ESPN 1000 comment.")
        self.assertTrue(ok)
        self.assertNotIn("radio", hook["text"])
        self.assertEqual(hook["unsupported_details"], [])
        self.assertEqual(hook["detail_fixed"], ["radio"])
        self.assertTrue(hook["intrigue_pick"])
        self.assertIn("radio", seen["prompt"])
        self.assertIn("Waddle & Silvy", seen["prompt"])
        self.assertEqual(seen["model"], script.CLAUDE_MODEL_LIGHT)

    def test_a_bad_rewrite_changes_nothing(self):
        for answer in ("Charles Barkley says Jordan cussed him out on the radio in 2012.",   # still radio
                       "Barkley. Jordan. Cussed out.",                                      # not one line
                       ValueError("broken JSON")):
            ok, hook, _ = self.run_fix(answer)
            self.assertFalse(ok)
            self.assertEqual(hook["text"], self.HOOK)
            self.assertEqual(hook["unsupported_details"], ["radio"])

    def test_wired_in_before_the_hook_order(self):
        import inspect
        import script
        src = inspect.getsource(script.build_short)
        # (audit 2026-11-13: the ordering moved into truth_order, still after the detail fix)
        self.assertLess(src.index("fix_hook_detail(hooks[0], sources, lead)"), src.index("truth_order(hooks, sources, lead)"))   # D27: + lead


class WhereTheFeudStandsNow(unittest.TestCase):
    """39 (D13). Run 43262308476: "they stopped talking ... still no update on a reunion", while the
    source said Vince Coleman got them talking and Barkley planned golf with Jordan."""

    SRC = [{"title": "Charles Barkley recalls Michael Jordan", "summary": "",
            "text": "Jordan didn't take it well. It stayed that way for more than a decade. The man who reunited "
                    "them was former St. Louis Cardinals outfielder Vince Coleman. While golfing with Jordan at "
                    "The Grove, Coleman called Barkley and told them it was time to talk. There has been no update "
                    "on it yet."}]
    SPOKEN = ("Barkley says Jordan cussed him out, and they stopped talking. He later called the silence "
              "stubborn, and there's still no update on a reunion. So who should've picked up the phone first?")

    def test_silence_while_a_source_tells_of_contact(self):
        import compliance as C
        self.assertIn("reunited", C.missed_turn(self.SPOKEN, self.SRC))
        fixed = self.SPOKEN.replace("there's still no update on a reunion",
                                    "Vince Coleman finally got them talking again")
        self.assertEqual(C.missed_turn(fixed, self.SRC), "")
        # a turn about other people (no name the Short says nearby) is not this feud's turn
        other = [{"title": "", "summary": "", "text": "Nick Young apologized to Ayesha Curry on his podcast."}]
        self.assertEqual(C.missed_turn(self.SPOKEN, other), "")
        # no silence in the Short: nothing to check
        self.assertEqual(C.missed_turn("Barkley and Jordan were Dream Team teammates.", self.SRC), "")

    def test_repair_then_gate(self):
        import compliance as C
        import script
        beats = [{"say": s} for s in compliance_split(self.SPOKEN)]
        problems = script.repair_needed("Charles Barkley says Michael Jordan cussed him out.", beats,
                                        {"stages": [], "hard": [], "soft": []}, self.SRC, [])
        self.assertTrue(any("contact since" in p for p in problems))
        verdict, notes, _ = C.check_claims([{"text": "Barkley says Jordan cussed him out", "status": "CONFIRMED",
                                             "source": 1}], self.SRC, self.SPOKEN)
        self.assertEqual(verdict, C.REVIEW)
        self.assertTrue(any("contact since" in n for n in notes))
        self.assertIn("where a feud or a friendship stands NOW", script.PROMPT)


def compliance_split(text):
    import compliance
    return compliance.split_sentences(text)


class NoReplayNoDanglingReference(unittest.TestCase):
    """41 (D14). Run 43288011054: the hook "Alperen Sengun tangled with Steph Curry, and Curry now
    has a torn oblique." was followed by "Curry tangled with Alperen Sengun, ...", and the closing
    question asked about "that stretch", a schedule the Short never said."""

    HOOK = "Alperen Sengun tangled with Steph Curry, and Curry now has a torn oblique."
    BEATS = [{"say": "Curry tangled with Alperen Sengun, grabbed his side, and was done after six minutes."},
             {"say": "Steve Kerr said concern is high."},
             {"say": "So do the Warriors survive that stretch without him, or was the run just Curry?"}]

    def test_reworded_replay_is_caught(self):
        import script
        self.assertEqual(script.hook_repeats(self.HOOK, self.BEATS), [0])
        # the past Shorts that only continue the hook are left alone
        self.assertEqual(script.hook_repeats(
            "Did Dillon Brooks just troll LeBron James with a King Blocker, then lose his opener by 41?",
            [{"say": "Brooks did a Kalshi ad for the King Blocker 9000, a gadget that mutes LeBron."}, {"say": "x"}]), [])
        self.assertEqual(script.hook_repeats(
            "Will the Bucks get the same hammer the Clippers got, now that Gary Trent Jr. is under investigation?",
            [{"say": "The NBA is investigating the Bucks over Gary Trent Jr.'s 64 million contract."}, {"say": "x"}]), [])
        # the closing question may come back to the hook's words
        self.assertEqual(script.hook_repeats(self.HOOK, self.BEATS[1:] + [
            {"say": "So Curry tangled with Alperen Sengun, but do the Warriors survive without him?"}]), [])

    def test_closing_question_points_to_something_said(self):
        import script
        self.assertEqual(script.dangling_refs(self.HOOK, self.BEATS), ["that stretch"])
        said = self.BEATS[:2] + [{"say": "Next comes a stretch of Spurs, Mavericks and Pelicans, back to back."},
                                 self.BEATS[2]]
        self.assertEqual(script.dangling_refs(self.HOOK, said), [])
        self.assertEqual(script.dangling_refs(self.HOOK, [{"say": "So who's winning this feud?"}]), [])
        problems = script.repair_needed(self.HOOK, self.BEATS, {"stages": [], "hard": [], "soft": []})
        self.assertTrue(any("that stretch" in p for p in problems))
        self.assertTrue(any("beat 1 repeats the hook" in p for p in problems))


class FreshFightBeatsOldFeud(unittest.TestCase):
    """42. Owner, 2026-11-13: Dejounte Murray's deleted "inside sabotage" tweet (59.5, rising +2
    outlets) was skipped three runs in a row while old feuds filled the runs."""

    # the real record of run 43317261723 (59.5)
    MURRAY = {"id": 6, "nba": True, "kind": "player_vs_team", "conflict": True, "virality": 7, "drama": 8,
              "star_power": 5, "debate": 7, "repeat": False, "search_hits": 0, "youtube_heat": 0,
              "google_trend": 0, "momentum": 2, "reddit": 0.0, "star_fame": 0.0, "hours_old": 0.8}

    def test_near_miss(self):
        import editor as E
        topic = {"verified": True, "outlets": 4}
        r = dict(self.MURRAY)
        self.assertEqual(E.short_score(r), 59.5)
        self.assertTrue(E.near_miss(r, topic))
        calm = {**r, "conflict": False, "virality": 10, "debate": 10}            # in range, but no fight
        self.assertTrue(E.NEAR_SCORE <= E.short_score(calm) < E.MIN_SCORE)
        self.assertFalse(E.near_miss(calm, topic))
        self.assertFalse(E.near_miss({**r, "drama": 6}, topic))                 # not dramatic enough
        self.assertFalse(E.near_miss({**r, "repeat": True}, topic))             # already made
        self.assertFalse(E.near_miss({**r, "momentum": 0}, {"verified": True, "outlets": 2}))  # not spreading
        self.assertTrue(E.near_miss({**r, "momentum": 0}, {"verified": True, "outlets": 3}))
        self.assertFalse(E.near_miss({**r, "kind": "filler"}, topic))

    def test_made_before_the_old_feuds(self):
        import inspect
        import script
        src = inspect.getsource(script.main)
        self.assertLess(src.index("queue += near"), src.index("for topic_id in queue:"))
        self.assertLess(src.index("for topic_id in queue:"), src.index("fill_with_evergreen(shorts"))


class BoldButTrue(unittest.TestCase):
    """43 (D17). Owner, 2026-11-13: every hook hyped and scandalous, at the edge of the truth, never
    past it. Run 43317261723: "Draymond Green says nobody owes Luka Doncic respect until they've
    played him." when he said "You earn respect"."""

    SRC = [{"title": "Draymond Green uses Kevin Durant lesson to defend Warriors rookie vs Luka Doncic",
            "summary": "", "tier": 1, "publisher": "BasketNews",
            "text": "Green said Lendeborg should keep talking to Doncic. 'You earn respect,' Green said. "
                    "Doncic finished with 28 points in the 127 to 105 Lakers win."}]
    HOOK = "Draymond Green says nobody owes Luka Doncic respect until they've played him."

    def run_check(self, answer):
        import script
        hook = {"text": self.HOOK, "score": 45, "question": True}
        saved = script.ask_claude
        seen = {}

        def ask(prompt, model=""):
            seen["prompt"], seen["model"] = prompt, model
            if isinstance(answer, Exception):
                raise answer
            return answer
        script.ask_claude = ask
        try:
            return script.check_hook_truth(hook, self.SRC), hook, seen
        finally:
            script.ask_claude = saved

    def test_ok_keeps_the_bold_line(self):
        res, hook, seen = self.run_check({"verdict": "ok"})
        self.assertEqual((res, hook["text"]), ("ok", self.HOOK))
        self.assertIn("NOT overstated: keep them", seen["prompt"])
        self.assertEqual(seen["model"], "")                         # the main model judges

    def test_overstated_gets_the_bold_true_line(self):
        res, hook, _ = self.run_check({"verdict": "overstated", "why": "stronger than he said",
                                       "text": "Draymond Green told a rookie to make Luka Doncic earn respect."})
        self.assertEqual(res, "fixed")
        self.assertEqual(hook["text"], "Draymond Green told a rookie to make Luka Doncic earn respect.")
        self.assertEqual(hook["truth_fixed"], "stronger than he said")
        self.assertFalse(hook.get("overstated"))

    def test_a_bad_rewrite_steps_behind(self):
        for text in ("Draymond Green just told a rookie to make Luka Doncic earn it after 41 points.",  # 41 invented
                     "Draymond. Luka. Respect.", ""):
            res, hook, _ = self.run_check({"verdict": "overstated", "why": "x", "text": text})
            self.assertEqual(res, "overstated")
            self.assertEqual(hook["text"], self.HOOK)
            self.assertTrue(hook["overstated"])
        hooks = [{"text": "a", "unsupported_details": [], "overstated": "x"}, {"text": "b", "unsupported_details": []}]
        hooks.sort(key=lambda h: (bool(h["unsupported_details"]), bool(h.get("recycled")), bool(h.get("overstated"))))
        self.assertEqual(hooks[0]["text"], "b")

    def test_a_failed_check_changes_nothing(self):
        res, hook, _ = self.run_check(ValueError("broken JSON"))
        self.assertEqual((res, hook["text"]), ("skipped", self.HOOK))
        self.assertFalse(hook.get("overstated"))

    def test_rule_in_the_prompt_and_wired(self):
        import inspect
        import script
        self.assertIn("BOLD BUT TRUE", script.PROMPT)
        self.assertIn("never past it", script.PROMPT)
        src = inspect.getsource(script.build_short)
        self.assertIn("truth_order(hooks, sources, lead)", src)   # D27: + the lead person

    def test_an_overstated_leading_hook_holds_the_short(self):
        """Audit 2026-11-13: if every checked hook stayed overstated, the Short is held (REVIEW)."""
        import inspect
        import script
        src = inspect.getsource(script.build_short)
        hold = src.index('if hooks and hooks[0].get("overstated"):')
        self.assertIn('retention["hard"].append(f"the hook says more than the sources', src[hold:hold + 200])
        self.assertLess(hold, src.index('"ready": bool(hooks)'))
        self.assertIn('not retention["hard"]', src[src.index('"ready": bool(hooks)'):][:200])

    def test_the_next_hook_is_read_too_when_the_first_was_overstated(self):
        """Audit 2026-11-13: the hook that takes an overstated one's place is read as well."""
        import script
        saved = script.ask_claude
        read = []

        def ask(prompt, model=""):
            line = prompt.split("THE LINE (untrusted script text): ")[1].split("\n")[0]
            read.append(line)
            return {"verdict": "overstated", "why": "x", "text": ""} if line.startswith("A ") else {"verdict": "ok"}
        script.ask_claude = ask
        try:
            hooks = [{"text": "A Draymond Green says nobody owes Luka Doncic respect.", "unsupported_details": []},
                     {"text": "B Draymond Green just told a rookie to make Luka earn it.", "unsupported_details": []},
                     {"text": "C third", "unsupported_details": []}]
            script.truth_order(hooks, self.SRC)
            self.assertEqual([h["text"][0] for h in hooks], ["B", "C", "A"])
            self.assertEqual([x[0] for x in read], ["A", "B"])          # B read once, C never
            read.clear()
            hooks = [{"text": "B fine", "unsupported_details": []}, {"text": "C", "unsupported_details": []}]
            script.truth_order(hooks, self.SRC)
            self.assertEqual([x[0] for x in read], ["B"])               # a good first hook: one call only
        finally:
            script.ask_claude = saved


class OneEventTheRightEra(unittest.TestCase):
    """44 (D10, D15). The Curry preview: 7 of 13 photos from the 2022 All-Star weekend (two days,
    several photographers). Run 43317261723: Shaq in Suns colours for "traded to Miami in 2004",
    Lendeborg in Michigan colours as "Warriors rookie", a crowd where Green is tiny."""

    def test_one_event_counts_across_photographers_and_days(self):
        from collections import Counter
        import media as m
        allstar = [{"kind": "photo", "page": f"p{k}", "author": a, "date": d, "title": f"Curry {k}.jpg",
                    "tag": {"v": "C", "s": "allstar"}}
                   for k, (a, d) in enumerate([("Erik Drost", "2022-02-19"), ("Erik Drost", "2022-02-20"),
                                               ("All-Pro Reels", "2022-02-20"), ("Keith Allison", "2022-02-18")])]
        self.assertEqual(m.event_of(allstar[0]), ("event", "allstar", "2022"))
        self.assertEqual(len({m.scene_of(c) for c in allstar}), 4)            # four scenes, one event
        scenes = Counter()
        for c in allstar[:3]:
            self.assertFalse(m.scene_full(c, scenes))
            m.count_scene(c, scenes)
        self.assertTrue(m.scene_full(allstar[3], scenes))                     # the 4th waits (last resort)
        self.assertEqual(m.spread_scenes([0, 1], [allstar[3], {"kind": "photo", "page": "x", "title": "y"}],
                                         lambda j: 3, {0: 9, 1: 5}, scenes), [1, 0])
        game = {**allstar[0], "tag": {"v": "C", "s": "game"}}
        self.assertIsNone(m.event_of(game))                                   # games stay per scene
        self.assertIsNone(m.event_of({**allstar[0], "date": "", "title": "Curry.jpg"}))   # no year: no event

    def test_a_college_photo_is_marked_pre_nba(self):
        import photo_tags
        c = {"page": "p1"}
        photo_tags._apply(c, {"v": "C", "s": "pre_nba", "e": "calm", "t": "defends, Michigan"})
        self.assertEqual(c["team"], "pre-nba")
        d = {"page": "p2", "team": "former"}
        photo_tags._apply(d, {"v": "C", "s": "pre_nba"})
        self.assertEqual(d["team"], "former")                                 # team data wins

    def test_rules_in_the_prompts(self):
        import media
        import photo_tags
        for need in ("A SMALL FIGURE", "THE LINE'S TIME AND TEAM", "Suns jersey"):
            self.assertIn(need, media.PICK_PROMPT)
        self.assertIn("THE LINE'S TIME AND TEAM", photo_tags.PICK_PROMPT)
        self.assertIn("a small figure (v S) only when no clear photo", photo_tags.PICK_PROMPT)
        self.assertIn("the team on his jersey", photo_tags.TAG_PROMPT)
        self.assertFalse(photo_tags.fill_ok({"tag": {"v": "S", "s": "game"}}))


class PrivateReportsStayPrivate(unittest.TestCase):
    """45 (audit, 2026-11-13). This repository is public, and so are its Actions logs and run
    summaries. The owner's decision (2026-11-11): the full report is private. Every stage still
    PRINTED its full report into the public log, and the weekly / benchmark runs wrote the
    stories, signals and the competitor scan into the public run summary."""

    STAGES = ("collect", "editor", "media", "render", "script", "signals", "budget", "benchmark")

    def test_stages_print_the_report_only_by_hand(self):
        import re
        for name in self.STAGES:
            src = (ROOT / "src" / f"{name}.py").read_text(encoding="utf-8")
            prints = [m.start() for m in re.finditer(r"\n\s*print\(text\)", src)]
            self.assertTrue(prints, name)
            for at in prints:
                self.assertIn('if not os.environ.get("GITHUB_STEP_SUMMARY"):', src[max(0, at - 120):at], name)

    def test_weekly_and_benchmark_keep_their_summary_private(self):
        for wf, steps in (("weekly.yml", ("python src/collect.py", "python src/benchmark.py")),
                          ("benchmark.yml", ("python src/benchmark.py",))):
            text = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            for step in steps:
                before = text[:text.index(step)]
                self.assertIn('export GITHUB_STEP_SUMMARY="$RUNNER_TEMP/private_summary.md"',
                              before[before.rfind("run: |"):], f"{wf}: {step}")


class OneSentenceSplitEverywhere(unittest.TestCase):
    """46 (audit, 2026-11-13). The script checks stopped splitting sentences after initials
    ("Stephen A. Smith", "Gary Trent Jr."), but the captions and the voice still did; and
    Pillow 14 drops Image.getdata (D12)."""

    def test_captions_keep_the_name_after_an_initial(self):
        import render
        self.assertIn("smith", render.key_words([{"say": "Stephen A. Smith ripped him. Smith said no."}]))

    def test_voice_parts_never_end_after_an_initial(self):
        import tts
        cls = next(v for v in vars(tts).values() if isinstance(v, type) and hasattr(v, "chunks"))
        words = ("He said it again and again on the air. " * 9 + "Then Stephen A. Smith ripped him on live TV "
                 "for the whole country to hear. " + "Nobody in the building said a single word about it. " * 6)
        for part in cls.chunks(None, words):
            self.assertFalse(part.rstrip().endswith(" A."), part[-30:])

    def test_picture_hash_is_the_same_with_the_new_pillow_call(self):
        import tempfile
        from PIL import Image
        import media
        import render
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.jpg"
            Image.radial_gradient("L").convert("RGB").save(p)
            with Image.open(p) as im:
                g = im.convert("L").resize((9, 8), Image.LANCZOS)
            px = list(getattr(g, "get_flattened_data", g.getdata)())
            old = sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
            self.assertEqual(media.picture_hash(p), old)
            self.assertEqual(render.picture_hash(p), old)
        for name in ("media", "render"):
            self.assertNotIn("list(g.getdata())", (ROOT / "src" / f"{name}.py").read_text(encoding="utf-8"))



class NotTheOtherThomas(unittest.TestCase):
    """47 (run 43353547001). Isiah Thomas's Commons pool held two Flickr photos titled
    "Isaiah Thomas (50639077836).jpg": the Wizards #4, not the Pistons legend. Both play
    basketball, so the photo tagger called them him (match 8 and 7) and they were shown for
    "hands in 1991". A first name with the same first letter that is not his (nor a short form
    or nickname of it) next to his surname = another man. Two players in one title are not."""

    def setUp(self):
        import media
        self.m = media

    def test_the_other_man_is_left_out(self):
        f = self.m.look_alike_name
        self.assertTrue(f("Isiah Thomas", "Isaiah Thomas (50639077836).jpg"))
        self.assertTrue(f("Isaiah Thomas", "Isiah_Thomas_1989.jpg"))
        self.assertTrue(f("Stephen Curry", "Seth Curry 2019.jpg"))
        self.assertTrue(f("Stephen Curry", "Seth Curry.jpg"))            # the ".jpg" is not part of the name
        self.assertTrue(f("Derek Fisher", "David_fisher_and_tex_winter_(3215053324).jpg"))

    def test_his_own_name_and_other_players_are_kept(self):
        f = self.m.look_alike_name
        for person, title in [("Isiah Thomas", "Isiah Thomas 1989.jpg"), ("Stephen Curry", "Steph Curry.jpg"),
                              ("Stephen Curry", "Stephen Curry and Seth Curry.jpg"),
                              ("Michael Brown", "Mike Brown coach.jpg"), ("Shaq O'Neal", "Shaquille O'Neal.jpg"),
                              ("Kevin Durant", "Harden_Durant_2013_playoffs.jpg"),
                              ("Kevin Durant", "Iguodala,_Calderon,_Durant,_Westbrook_in_Barcelona.jpg"),
                              ("Stephen Curry", "Seth Curry guards his brother Stephen.jpg"),
                              ("Jalen Brunson", "Rick Brunson embraces Jalen after the game.jpg"),
                              ("Marcus Smart", "Isaiah Thomas, Marcus Smart (34075954590).jpg"),
                              ("LeBron", "LeBron James.jpg")]:
            self.assertFalse(f(person, title), title)

    def test_the_pool_never_holds_him(self):
        m = self.m
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Isiah Thomas Pistons 1989.jpg"},
                {"page": "b", "score": 20, "title": "Isaiah Thomas (50639077836).jpg"}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = lambda person: []
            m.openverse_photos = lambda person: [{"page": "c", "score": 25, "title": "Isaiah Thomas (50639144552).jpg"}]
            self.assertEqual([p["page"] for p in m.photos("Isiah Thomas")], ["a"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])



class OnlyTheQuote(unittest.TestCase):
    """48 (run 43395656602). Yahoo's article held a tweet glued to its quote: 'hurt Luka
    Doncic:"Not a good play right there. That's not cool man, not letting guys land"When will'.
    The quote correction took 'hurt Luka Doncic:Not a good play right there. That's not' and
    the Short said it as Barkley's words (gate PASS). The article's own form, '"...right there,"
    said Barkley. "Not letting...', gave "...right there, said Barkley." inside the quote."""

    TWEET = ("Charles Barkley just called out Kyle Kuzma for his dirty play that hurt Luka Doncic:\"Not a good "
             "play right there. That's not cool man, not letting guys land\"When will the NBA finally stop "
             "these guys from their dirty hits on Luka Doncic? First time he's gotten this call.")
    ARTICLE = ("While showing highlights Charles Barkley called out Kuzma in passing. \"That's not a good play "
               "right there,\" said Barkley. \"Not letting guys land. That's not cool at all.\" Then it went on.")

    def fix(self, text, quote):
        import script
        b = [{"say": f'Barkley said on Inside the NBA, "{quote}"'}]
        script.soften_quotes(b, [{"title": "Barkley calls out Kuzma", "summary": "", "text": text}])
        return b[0]["say"]

    def test_the_glued_tweet(self):
        said = self.fix(self.TWEET, "That's not a good play right there. Not letting guys land.")
        self.assertEqual(said, 'Barkley said on Inside the NBA, "Not a good play right there. '
                               'That\'s not cool man, not letting guys land"')

    def test_said_barkley_is_not_his_words(self):
        said = self.fix(self.ARTICLE, "That's not a good play right there. Not letting guys land.")
        self.assertNotIn("said Barkley", said.split('"')[1])
        self.assertIn('"That\'s not a good play right there"', said)

    def test_a_cut_off_source_is_never_the_quote(self):
        said = self.fix('Barkley on Kuzma: "Not a good play right there. That\'s not\u2026 https://t.co/x',
                        "That's not a good play right there. Not letting guys land.")
        self.assertNotIn("That's not\"", said)
        self.assertNotIn("Kuzma:", said)

    def test_the_record_survives_the_repair(self):
        import inspect, script
        self.assertIn("softened + cand_soft", inspect.getsource(script))



class FinalLaws(unittest.TestCase):
    """49 (owner, 2026-11-13: fix the kind of mistake, not the one case). The checks asked "are
    these words in the source?" and "does this look like him?"; both said yes to Barkley's
    broken quote and to Isaiah Thomas in a Wizards jersey. These laws read the finished result."""

    SRC = [{"title": "Barkley calls out Kuzma", "summary": "",
            "text": "While showing highlights Charles Barkley called out Kuzma for the play that hurt Luka "
                    "Doncic. \"That's not a good play right there,\" said Barkley. \"Not letting guys land. "
                    "That's not cool at all.\" Kuzma starts for the 1-11 Bucks."}]

    def test_a_quote_must_be_someones_own_words(self):
        import script
        ok = 'Barkley said, "That\'s not a good play right there. Not letting guys land."'
        self.assertEqual(script.quotes_outside_marks(ok, self.SRC), [])        # broken by "said Barkley": still his
        narration = 'Barkley said, "the play that hurt Luka Doncic was not a good play."'
        self.assertTrue(script.quotes_outside_marks(narration, self.SRC))      # the article's words, not his
        self.assertEqual(script.quotes_outside_marks("Kuzma's closeout hurt Luka.", self.SRC), [])
        head = [{"title": "\u2018I Love Random NBA Beefs,\u2019 Fans Divided", "summary": "", "text": ""}]
        self.assertEqual(script.quotes_outside_marks('Fans said "I love random NBA beefs."', head), [])

    def test_broken_text_is_caught(self):
        import script
        self.assertTrue(script.BROKEN_TEXT.search("Barkley said, hurt Luka Doncic:Not a good play"))
        self.assertTrue(script.BROKEN_TEXT.search('not letting guys land"When will'))
        for fine in ("At 3:30 on Friday.", 'He said "no." Then left.', "Luka's ankle, the Lakers' bench."):
            self.assertIsNone(script.BROKEN_TEXT.search(fine), fine)

    def test_the_laws_hold_the_short(self):
        import inspect, script
        src = inspect.getsource(script)
        self.assertIn("quotes_outside_marks(spoken, sources)", src)
        self.assertIn("broken = BROKEN_TEXT.search(spoken)", src)
        self.assertIn('retention["hard"].append(f\'broken text', src)

    def test_his_jersey_his_teams(self):
        import media, compliance as C
        j = media.jersey_team
        self.assertEqual(j({"s": "game", "t": "dribbles in Wizards jersey"}), "washington wizards")
        self.assertEqual(j({"s": "game", "t": "shoots a three, Suns"}), "phoenix suns")
        self.assertEqual(j({"s": "game", "t": "dribbles past Cavaliers defender"}), "")      # the opponent
        self.assertEqual(j({"s": "game", "t": "goes up to score against Thunder, Wizards"}), "washington wizards")
        self.assertEqual(j({"s": "bench", "t": "stands on sideline, Warriors"}), "")          # a coach
        self.assertFalse(C.jersey_ok("washington wizards", ["detroit pistons"]))
        self.assertTrue(C.jersey_ok("washington wizards", []))                               # career unknown
        self.assertTrue(C.jersey_ok("charlotte hornets", ["new orleans pelicans"]))         # the old Hornets
        self.assertTrue(C.jersey_ok("", ["detroit pistons"]))

    def test_media_leaves_him_out_and_the_gate_holds(self):
        import media, gate
        m = media
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos),
                 m.photo_tags.tag_person, m.photo_tags.shortlists, m.career_teams)
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Isiah Thomas 1989.jpg", "tag": {"v": "C", "s": "game", "t": "drives, Pistons"}},
                {"page": "b", "score": 20, "title": "IT 2021.jpg", "tag": {"v": "C", "s": "game", "t": "dribbles in Wizards jersey"}}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            m.photo_tags.tag_person = lambda *a, **k: 0
            m.photo_tags.shortlists = lambda *a, **k: None
            m.career_teams = lambda person: {"detroit pistons"}
            m.shortlist_photos({"headline": "Isiah Thomas on Jordan", "_name": "t"}, [{"say": "x"}],
                               [{"person": "Isiah Thomas"}])
            self.assertEqual([p["page"] for p in m.photos("Isiah Thomas")], ["a"])
        finally:
            (m.commons_photos, m.flickr_photos, m.openverse_photos) = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])
            m.photo_tags.tag_person, m.photo_tags.shortlists, m.career_teams = saved[4:]
        shown = [{"kind": "photo", "person": "Isiah Thomas", "jersey": "washington wizards", "title": "IT.jpg",
                  "license": "CC BY 2.0", "page": "p", "author": "x", "match": 8}]
        v, notes = gate.check_visuals(shown, {"careers": {"Isiah Thomas": ["detroit pistons"]}})
        self.assertEqual(v, "REVIEW")
        self.assertIn("never played for", " ".join(notes))
        shown[0]["jersey"] = "detroit pistons"
        self.assertEqual(gate.check_visuals(shown, {"careers": {"Isiah Thomas": ["detroit pistons"]}})[0], "PASS")



class ReplayOnRealRuns(unittest.TestCase):
    """50 (owner, 2026-11-13). Checking a change on real runs needed the articles again; some were
    gone or behind a paywall (The Athletic). The texts each Short was checked against are kept
    with the run, and replay.py tries today's checks on every kept run."""

    def test_sources_are_kept_with_the_run(self):
        import script, state, tempfile
        self.assertIn("sources/short_*.json", state.RUN_FILES)
        old = script.SOURCES_OUT
        with tempfile.TemporaryDirectory() as d:
            try:
                script.SOURCES_OUT = Path(d)
                script.keep_sources(2, [{"publisher": "Yahoo", "title": "t", "text": "body", "link": "u", "extra": 1}])
                kept = json.loads((Path(d) / "short_2.json").read_text(encoding="utf-8"))
            finally:
                script.SOURCES_OUT = old
        self.assertEqual(kept[0]["text"], "body")
        self.assertNotIn("extra", kept[0])
        import inspect
        self.assertIn("keep_sources(n, sources)", inspect.getsource(script.build_short))

    def test_replay_finds_what_the_run_missed(self):
        import replay, tarfile, tempfile, io
        from unittest.mock import patch
        short = {"gate": "PASS", "hook": {"text": "Barkley called out Kuzma."},
                 "beats": [{"say": 'Barkley said, "the play that hurt Luka Doncic was bad."'},
                           {"say": "Then hurt Luka Doncic:Not a good play."}],
                 "unsupported_numbers": [], "unsupported_quotes": []}
        sources = [{"title": "Barkley calls out Kuzma", "summary": "", "text": "Barkley called out Kuzma for the "
                    "play that hurt Luka Doncic was bad. \"Not letting guys land,\" he said."}]
        with tempfile.TemporaryDirectory() as d:
            with tarfile.open(Path(d) / "2026-11-13_1.tar.gz", "w:gz") as tar:
                for name, obj in (("scripts/short_1.json", short), ("sources/short_1.json", sources)):
                    raw = json.dumps(obj).encode()
                    info = tarfile.TarInfo(name)
                    info.size = len(raw)
                    tar.addfile(info, io.BytesIO(raw))
            out = io.StringIO()
            with patch("sys.stdout", out):
                n = replay.replay(Path(d))
        self.assertEqual(n, 1)
        self.assertIn("broken text", out.getvalue())
        self.assertIn("not inside quote marks", out.getvalue())



class TheNewsInTheHook(unittest.TestCase):
    """51 (run 43353547001). "Smart suspended three games" opened with "Marcus Smart punched
    Charles Bassey, and the Rockets' next opponents are all below .500": yesterday's punch (we had
    made that Short) and a schedule detail, while two lines said "the NBA suspended Smart"."""

    HEAD = "Rockets' Marcus Smart suspended three games for punching Warriors' Charles Bassey"

    def hooks(self):
        return [{"text": "Marcus Smart punched Charles Bassey, and the Rockets' next opponents are all below .500.",
                 "question": True, "score": 52},
                {"text": "Charles Bassey just called Marcus Smart's punch fake toughness, and the NBA suspended Smart.",
                 "question": True, "score": 43},
                {"text": "The NBA just suspended Marcus Smart for punching Charles Bassey in the face.",
                 "question": True, "score": 43}]

    def test_the_news_is_said(self):
        import script
        f = script.says_the_news
        self.assertFalse(f(self.hooks()[0]["text"], self.HEAD))
        self.assertTrue(f(self.hooks()[2]["text"], self.HEAD))
        self.assertTrue(f("Curry now has a torn oblique.", "Stephen Curry injury: out two weeks with oblique tear"))
        for head in ("Lakers show signs of life", "Rudy Gobert fired back at Kuminga", "Luka is fine, per Shams",
                     "Warriors on a tear", "Kuminga rips Gobert after loss"):
            self.assertTrue(f("Anything at all.", head), head)                  # no news event: nothing to check

    def test_the_fan_pick_decides_not_the_news(self):
        # his rule (2026-11-14): the hook must be scandalous, intriguing and effective; the day's news
        # is secondary. The "a line with the news always wins" order was mine and is gone: every good
        # line goes to the fan's pick, and its choice leads.
        import script
        with patch.object(script, "ask_claude", return_value={"best": 1}) as ask:
            got = script.intrigue_pick(self.hooks(), self.HEAD, "story")
        self.assertIn("below .500", ask.call_args[0][0].split("WHAT THE SHORT SAYS")[1])   # offered too
        self.assertEqual(got[0]["text"], self.hooks()[0]["text"])
        self.assertTrue(got[0]["intrigue_pick"])

    def test_no_news_line_changes_nothing(self):
        import script
        hooks = [h for h in self.hooks()[:1]] + [{"text": "Smart and Bassey went at it again.", "question": True, "score": 45}]
        with patch.object(script, "ask_claude", return_value={"best": 1}):
            got = script.intrigue_pick(hooks, self.HEAD, "story")
        self.assertEqual(got[0]["text"], hooks[0]["text"])



class AQuestionIsNoAnswer(unittest.TestCase):
    """52 (run 43395656602). The payoff "Why was Luka even back in up 20? I'd blame that." passed
    as an answer (10 words). It is a question and a 3-word scrap (blame what? whom?)."""

    def test_question_payoff_is_weak(self):
        import script
        bad = [{"say": "Why was Luka even back in up 20? I'd blame that.", "stage": "payoff"}]
        self.assertTrue(script.weak_payoff(bad))
        self.assertTrue(script.weak_payoff([{"say": "So was it dirty, or just a bad landing for Luka?", "stage": "payoff"}]))
        good = [{"say": "Why was Luka even in? Redick left him out there up 20, and that is on him.", "stage": "payoff"}]
        self.assertFalse(script.weak_payoff(good))
        self.assertFalse(script.weak_payoff([{"say": "Doc was half right and fully clumsy.", "stage": "payoff"}]))
        problems = script.repair_needed("Barkley called out Kuzma.", bad + [{"say": "So was Kuzma dirty, Barkley?", "stage": "exit"}],
                                        {"hard": [], "soft": []})
        self.assertTrue(any("or a question" in p for p in problems))



class IndependentFinalRead(unittest.TestCase):
    """53 (owner, 2026-11-13). A fresh Claude reads the finished Short like a viewer, with the
    picture under every line and the sources. It must quote real evidence: an invented reason
    can never hold a good Short, and a Short it could not read is never published unread."""

    SHORT = {"hook": {"text": "Charles Barkley calls out Kyle Kuzma on live TV."},
             "beats": [{"say": 'Barkley said, "hurt Luka Doncic:Not a good play right there. That\'s not"'},
                       {"say": "So was it dirty?"}]}
    ITEMS = [{"beat": 0, "kind": "photo", "person": "Charles Barkley", "title": "Barkley 2019.jpg",
              "tag": {"s": "stage", "t": "talks on a TV set"}},
             {"beat": 1, "kind": "photo", "person": "Luka Doncic", "title": "Luka.jpg", "jersey": "los angeles lakers",
              "tag": {"s": "game", "t": "drives, Lakers"}, "alts": [{"kind": "photo", "person": "Kyle Kuzma", "title": "Kuz.jpg"}]}]
    SOURCES = [{"publisher": "Yahoo Sports", "title": "Barkley calls out Kuzma", "summary": "",
                "text": "\"That's not a good play right there,\" said Barkley. \"Not letting guys land.\""}]

    def test_every_line_gets_its_pictures(self):
        import final_read
        rows = final_read.lines_of(self.SHORT, self.ITEMS)
        self.assertEqual([r["line"] for r in rows], [0, 1, 2])
        self.assertIn("Charles Barkley", rows[0]["pictures"][0])
        self.assertEqual(len(rows[1]["pictures"]), 2)                   # the picture and its alternate
        self.assertIn("jersey: los angeles lakers", rows[1]["pictures"][0])

    def test_only_real_evidence_holds(self):
        import final_read
        rows = final_read.lines_of(self.SHORT, self.ITEMS)
        real = {"errors": [{"line": 1, "kind": "NONSENSE", "what": "broken quote",
                            "evidence": "hurt Luka Doncic:Not a good play right there"}]}
        self.assertEqual(final_read.judge(real, rows, self.SOURCES)["verdict"], "REVIEW")
        made_up = {"errors": [{"line": 1, "kind": "WRONG WORDS", "what": "x",
                               "evidence": "Barkley later apologized to Kuzma on air"}]}
        got = final_read.judge(made_up, rows, self.SOURCES)
        self.assertEqual(got["verdict"], "PASS")
        self.assertIn("evidence not found", got["doubts"][0]["what"])
        self.assertEqual(final_read.judge({"doubts": [{"line": 2, "what": "weak"}]}, rows, self.SOURCES)["verdict"], "PASS")

    def test_the_gate_holds_and_never_publishes_unread(self):
        import gate
        self.assertEqual(gate.check_final_read(None), ("PASS", []))
        self.assertEqual(gate.check_final_read({"verdict": "PASS", "errors": [], "doubts": [{"what": "x"}]})[0], "PASS")
        self.assertEqual(gate.check_final_read({"verdict": "REVIEW", "errors": [{"line": 1, "what": "w"}]})[0], "REVIEW")
        self.assertEqual(gate.check_final_read({"failed": "Claude limit reached"}),
                         ("REVIEW", ["not read by the final reader: Claude limit reached"]))
        src = (ROOT / "src" / "gate.py").read_text(encoding="utf-8")
        self.assertIn('{"failed": "no final read for this Short"}) if REVIEW.is_dir() else None', src)

    def test_the_stage_reads_every_short(self):
        import final_read, script, tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for sub in ("scripts", "media", "sources", "review"):
                (d / sub).mkdir()
            for n in (1, 2, 3):
                (d / "scripts" / f"short_{n}.json").write_text(json.dumps(self.SHORT), encoding="utf-8")
            for n in (1, 3):
                (d / "sources" / f"short_{n}.json").write_text(json.dumps(self.SOURCES), encoding="utf-8")
            answers = iter([{"errors": [{"line": 1, "kind": "NONSENSE", "what": "broken",
                                         "evidence": "hurt Luka Doncic:Not a good play right there"}]},
                            script.UsageLimit("5-hour limit")])

            def fake(*a, **k):
                x = next(answers)
                if isinstance(x, Exception):
                    raise x
                return x
            saved = (final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW)
            try:
                final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW = (
                    d / "scripts", d / "media", d / "sources", d / "review")
                with patch.object(script, "ask_claude", side_effect=fake) as ask, patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}):
                    final_read.main()
                self.assertEqual(ask.call_args_list[0].kwargs.get("where"), "final_read")
                self.assertEqual(ask.call_args_list[0].args[1], script.CLAUDE_MODEL)    # the main model (his choice)
            finally:
                final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW = saved
            got = {n: json.loads((d / "review" / f"short_{n}.json").read_text(encoding="utf-8")) for n in (1, 2, 3)}
        self.assertEqual(got[1]["verdict"], "REVIEW")
        self.assertIn("not kept", got[2]["failed"])                         # no sources: never "read"
        self.assertIn("limit", got[3]["failed"])

    def test_wired_into_the_run(self):
        import state
        wf = (ROOT / ".github" / "workflows" / "collect.yml").read_text(encoding="utf-8")
        self.assertLess(wf.index("python src/final_read.py"), wf.index("python src/gate.py"))
        self.assertIn("review/short_*.json", state.RUN_FILES)



class SheetsOpenedAtOnce(unittest.TestCase):
    """54 (D16). Claude Code re-sends the whole conversation at every step. Opening 5 sheets one
    per step made a 45-photo tag call cost about 15k + 18k + 21k + 24k + 27k + 30k = 136k tokens
    (run 43395656602's biggest call was 136,625); all at once: about 15k + 30k."""

    def test_both_sheet_prompts_ask_for_one_step(self):
        import media, photo_tags
        for prompt in (photo_tags.TAG_PROMPT, media.PICK_PROMPT):
            self.assertIn("ALL AT ONCE", prompt)
            self.assertIn("never one sheet per step", " ".join(prompt.split()))

    def test_turns_are_logged(self):
        import media, script, tempfile
        out = json.dumps({"usage": {"input_tokens": 5, "cache_read_input_tokens": 10}, "num_turns": 6,
                          "duration_ms": 2000, "total_cost_usd": 0.1})
        for mod in (media, script):
            with tempfile.TemporaryDirectory() as d:
                fake = Path(d) / "src" / "x.py"
                with patch.object(mod, "__file__", str(fake)):
                    mod.log_claude_usage(out, "t")
                row = json.loads((Path(d) / "data" / "claude_usage.jsonl").read_text(encoding="utf-8"))
            self.assertEqual((row["turns"], row["in"]), (6, 15))



class NoNameBeforeItsImport(unittest.TestCase):
    """55 (run 43407418420). The audit's "print only without GITHUB_STEP_SUMMARY" (e54499d) put
    os.environ before a leftover "import os" inside render.main: Python then treats os as a local
    name, the stage crashed after both videos were made, and the gate never ran. Checked for
    every function in every stage, so no stage can fail this way again."""

    def test_every_function(self):
        import ast
        found = []
        for path in sorted((ROOT / "src").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for fn in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
                first = {}
                for n in ast.walk(fn):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        for a in n.names:
                            name = (a.asname or a.name).split(".")[0]
                            first[name] = min(first.get(name, n.lineno), n.lineno)
                found += [f"{path.name}:{n.lineno} {fn.name} uses {n.id} before line {first[n.id]}"
                          for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id in first and n.lineno < first[n.id]]
        self.assertEqual(found, [])



class HisOwnCategoryIsHim(unittest.TestCase):
    """56 (run 43407418420). Rule 47 (another man with his surname) took 27 of Dejounte Murray's
    31 Commons photos: Flickr titled them "Dejonte Murray". They were in his OWN Commons category,
    which people file by hand under that very player. A wrong-team photo still meets the jersey law."""

    def test_own_category_is_kept(self):
        m = self.m = __import__("media")
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Dejonte Murray (51915001522).jpg", "own_category": True},
                {"page": "b", "score": 20, "title": "Dejonte Murray (51915008527).jpg"},
                {"page": "c", "score": 10, "title": "Dejounte Murray Pelicans.jpg"}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            self.assertEqual([p["page"] for p in m.photos("Dejounte Murray")], ["a", "c"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])

    def test_commons_records_the_category(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('"own_category": title in in_category,', src)



class FinalReadKeepsThePictureRules(unittest.TestCase):
    """57 (run 43407418420). The first real final read held Luka in a Dallas jersey on "no word
    from Luka" and Zion on "the Pelicans are 1 and 8 with Murray": both are allowed by the agreed
    picture rules (a former team scores lower, another person from the story fits a team line).
    Zion over "He wrote that the sabotage is real, deleted it" stays an error: the viewer takes
    Zion for the one who wrote it."""

    def test_prompt(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("someone else shown while the line says what HE said or did", p)
        self.assertIn("the right man in a former team's jersey when the line names no team or time", p)
        self.assertIn("NOT an error (at most a doubt)", p)

    def test_media_calls_are_named(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        for step in ("media_plan", "media_tags", "media_shortlist", "media_pick", "media_pick2"):
            self.assertIn(f'where="{step}"', src)
        self.assertIn("log_claude_usage(res.stdout, where)", src)



class OnlyAHeadlineIsSkipped(unittest.TestCase):
    """58 (run 43407418420). Cunningham's claim about Luka: its one copy unread, two Luka-injury
    pieces read instead, so the 600-character bar passed and the Short could only say "from an
    outlet I can't verify" (held). Replay on 29 Shorts: only that one is a fresh story with its
    own article unread; the evergreens without it (two of them PASS) are untouched."""

    def build(self, evergreen, main):
        import script
        editor = {"topics": [{"headline": "Cunningham says Luka wanted the fan gone", "items": []}],
                  "ranked": [{"id": 0, **({"evergreen": "k"} if evergreen else {})}]}
        src = [{"publisher": "HITC", "title": "Luka injury update", "text": "x" * 3000, "main": main, "link": "l",
                "tier": 2, "summary": ""}]
        with patch.object(script, "gather_sources", return_value=src), \
                patch.object(script, "ask_claude", side_effect=RuntimeError("written")):
            try:
                script.build_short(1, 0, editor, "", {"hooks": [], "rules": []})
            except Exception as exc:          # noqa: BLE001
                return str(exc)
        return ""

    def test_fresh_story_unread_is_skipped_before_claude(self):
        self.assertIn("could not be read in any copy", self.build(evergreen=False, main=False))

    def test_read_story_and_evergreens_go_on(self):
        self.assertEqual(self.build(evergreen=False, main=True), "written")   # reached the writer
        self.assertEqual(self.build(evergreen=True, main=False), "written")



class NoSilentFeeds(unittest.TestCase):
    """59 (2026-11-13). Three sources were silent in every run and nobody saw it: ESPN (0 items
    on GitHub's servers, 17 elsewhere), HoopsHype (402 Payment Required) and the podcast search
    (39 items, all from May: "when:1d" at the end, after "-prediction", was ignored)."""

    def test_when_first_in_every_search(self):
        import sources
        for f in sources.FEEDS:
            for url in (f["url"], f.get("fallback") or ""):
                if "news.google.com" in url:
                    self.assertIn("search?q=when:1d+", url, f["name"])
                    self.assertNotIn("+when:1d&", url, f["name"])

    def test_silent_feed_falls_back_and_says_why(self):
        import collect, feedparser, io
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).timetuple()
        D = feedparser.FeedParserDict

        def entry(title):
            return D(title=title, link="https://news.google.com/x/" + title.replace(" ", ""), published_parsed=now,
                     summary="NBA", source=D(title="ESPN"))
        feeds = [{"name": "ESPN", "url": "https://espn/rss", "tier": 1, "fallback": "https://news.google.com/rss/search?q=when:1d+site:espn.com/nba"},
                 {"name": "CBS Sports", "url": "https://cbs/rss", "tier": 1}]
        answers = {"https://espn/rss": D(entries=[], status=403, bozo=0, feed=D()),
                   feeds[0]["fallback"]: D(entries=[entry("Draymond rips Kerr after loss NBA")]
                                           + [entry(f"Suns 101-96 Hornets (Nov 12, 2026) Game Recap {i}") for i in range(3)]
                                           + [entry(f"Lakers NBA story number {i}") for i in range(40)], status=200, bozo=0, feed=D()),
                   "https://cbs/rss": D(entries=[], status=200, bozo=0, feed=D())}
        out = io.StringIO()
        with patch.object(collect, "FEEDS", feeds), patch.object(collect.feedparser, "parse", lambda u, agent=None: answers[u]), \
                patch("sys.stdout", out):
            items = collect.fetch_all()
        log = out.getvalue()
        self.assertIn("ESPN gave nothing: HTTP 403", log)
        self.assertEqual(len(items), collect.FALLBACK_MAX)
        self.assertFalse(any("Game Recap" in i["title"] for i in items))
        self.assertEqual({i["publisher"] for i in items}, {"ESPN"})
        self.assertEqual(items[0]["tier"], 1)                       # ESPN stays a tier 1 outlet
        self.assertIn("CBS Sports gave nothing: HTTP 200", log)    # no fallback: only the reason



class MoreSourcesForTheBeef(unittest.TestCase):
    """60 (owner, 2026-11-13: ChatGPT's source list, checked one by one). Kept only what is free,
    answers GitHub's servers (run 43441957341) and brings beef, scandal or intrigue."""

    def test_the_new_sources_are_there(self):
        import sources
        names = {f["name"] for f in sources.FEEDS}
        for n in ("ClutchPoints", "Hoops Rumors", "SB Nation", "Defector", "TrueHoop", "GN: statements", "GN: scandal",
                  "GN: vs coach or teammate", "GN: viral", "GN: insiders", "Gil's Arena (podcast)",
                  "The Draymond Green Show (podcast)", "Pablo Torre Finds Out (podcast)", "Club 520 (podcast)",
                  "All the Smoke (podcast)"):
            self.assertIn(n, names)
        pods = [f for f in sources.FEEDS if f["name"].endswith("(podcast)")]
        self.assertTrue(all(f.get("filter") and "channel_id=UC" in f["url"] for f in pods))
        self.assertTrue(next(f for f in sources.FEEDS if f["name"] == "Defector").get("filter"))
        self.assertEqual(len(names), len(sources.FEEDS))                   # no source twice

    def test_multi_sport_feeds_keep_only_nba(self):
        import collect, feedparser
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).timetuple()
        D = feedparser.FeedParserDict
        feed = {"name": "Dan Patrick Show (podcast)", "url": "u", "tier": 2, "filter": True, "video": True}
        nfl = D(title="Kurt Warner Looks At J.J. McCarthy's Results With The Giants", link="https://y/1",
                published_parsed=now, summary="NFL quarterbacks")
        nba = D(title="Luka Doncic Hits His 5th Three-Pointer Of The Game For The Lakers", link="https://y/2",
                published_parsed=now, summary="")
        self.assertIsNone(collect.normalize(nfl, feed))
        got = collect.normalize(nba, feed)
        self.assertEqual((got["publisher"], got["tier"]), ("Dan Patrick Show (podcast)", 2))
        plain = {"name": "ClutchPoints", "url": "u", "tier": 2}            # an NBA-only feed: not filtered
        self.assertIsNotNone(collect.normalize(D(title="Jeff Teague says Brunson needs help", link="https://c/1",
                                                 published_parsed=now, summary=""), plain))

    def test_reddit_rising_follows_hot_after_a_pause(self):
        import signals
        calls = []

        def fake(url=signals.REDDIT_RSS):
            calls.append(url)
            return ["Smart punches Bassey", "Curry out"] if url == signals.REDDIT_RSS else ["Curry out", "Kuminga wants out"]
        topics = [{"headline": "Kuminga wants out", "items": [{"title": "Jonathan Kuminga wants out of Golden State"}]}]
        with patch.object(signals, "reddit_hot", side_effect=fake), patch.object(signals.time, "sleep") as nap:
            got = signals.reddit_titles()
        self.assertEqual(calls, [signals.REDDIT_RSS, signals.REDDIT_RISING])
        nap.assert_called_with(signals.REDDIT_PAUSE)
        self.assertEqual(got[0], ["Smart punches Bassey", "Curry out", "Kuminga wants out"])

    def test_a_video_page_is_never_read_as_an_article(self):
        import script
        with patch.object(script.trafilatura, "fetch_url", return_value="<html>Subscribe! Gil's Arena</html>") as fetch:
            for url in ("https://www.youtube.com/watch?v=abc", "https://youtu.be/abc"):
                it = {"link": url, "text": ""}
                self.assertFalse(script.read_article(it, {}))
                self.assertEqual(it["text"], "")
            fetch.assert_not_called()

    def test_rising_failing_keeps_hot(self):
        import signals

        def fake(url=signals.REDDIT_RSS):
            if url == signals.REDDIT_RISING:
                raise OSError("HTTP Error 429")
            return ["Smart punches Bassey"]
        with patch.object(signals, "reddit_hot", side_effect=fake), patch.object(signals.time, "sleep"):
            titles, errors = signals.reddit_titles()
        self.assertEqual(titles, ["Smart punches Bassey"])
        self.assertTrue(any("rising" in e for e in errors))


class CollegeDaysBeforeTheDraft(unittest.TestCase):
    """61. D22 (run 43446225184): Yaxel Lendeborg, a Warriors rookie (Wikidata: Golden State from
    2026-06-23), was shown in three Michigan #23 photos of 11 Feb 2026 on "a 24-year-old rookie" and
    "8-4 start"; none was marked PRE-NBA. The copies shown came through Openverse (no date, no
    categories), the Commons copy of the same file was the one with the facts, and a year alone
    (2026 = 2026) can never mark a rookie's last college season."""

    CLAIMS = {"Q123": [
        {"mainsnak": {"datavalue": {"value": {"id": "Q7863702"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2023-00-00T00:00:00Z"}}}],
                        "P582": [{"datavalue": {"value": {"time": "+2025-00-00T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q6837797"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2025-00-00T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2026-06-23T00:00:00Z"}}}]}}],
        "Q456": [   # a year-only start: he may have joined mid-season, so no day is trusted
        {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2019-00-00T00:00:00Z"}}}]}}]}
    LABELS = {"Q7863702": "UIC Flames men's basketball", "Q6837797": "Michigan Wolverines men's basketball",
              "Q157376": "Golden State Warriors"}

    def setUp(self):
        import media
        self.m = media
        self.saved = (media.get, dict(media._wikidata), dict(media._teams), dict(media._nba_debut),
                      dict(media._nba_debut_day), media.commons_photos, media.flickr_photos,
                      media.openverse_photos, dict(media._all_photos))
        for d in (media._wikidata, media._teams, media._nba_debut, media._nba_debut_day, media._all_photos):
            d.clear()
        media._wikidata.update({"Yaxel Lendeborg": "Q123", "Late Joiner": "Q456"})
        claims, labels = self.CLAIMS, self.LABELS

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("action") == "wbgetclaims":
                return json.dumps({"claims": {"P54": claims.get(q["entity"], [])}}).encode()
            if q.get("action") == "wbgetentities":
                return json.dumps({"entities": {i: {"labels": {"en": {"value": labels[i]}}}
                                                for i in q["ids"].split("|") if i in labels}}).encode()
            raise OSError("unexpected")
        media.get = get
        media.flickr_photos = lambda person: []

    def tearDown(self):
        m, s = self.m, self.saved
        m.get, m.commons_photos, m.flickr_photos, m.openverse_photos = s[0], s[5], s[6], s[7]
        for d, old in ((m._wikidata, s[1]), (m._teams, s[2]), (m._nba_debut, s[3]), (m._nba_debut_day, s[4]),
                       (m._all_photos, s[8])):
            d.clear()
            d.update(old)

    @staticmethod
    def commons(title, date="", team=""):
        return {"kind": "photo", "title": title, "source": "Wikimedia Commons", "date": date, "team": team,
                "page": "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"),
                "url": "https://upload.wikimedia.org/x/" + title.replace(" ", "_"), "score": 20}

    @staticmethod
    def openverse(title):
        return {"kind": "photo", "title": title, "source": "Wikimedia via Openverse", "team": "",
                "page": "https://commons.wikimedia.org/w/index.php?curid=" + str(abs(hash(title)) % 10**9),
                "url": "https://upload.wikimedia.org/y/" + title.replace(" ", "_") + ".jpg", "score": 9}

    def test_the_day_his_nba_career_began(self):
        m = self.m
        self.assertEqual(m.teams_of("Yaxel Lendeborg")[0], "golden state warriors")
        self.assertEqual(m._nba_debut_day["Q123"], "2026-06-23")
        m.teams_of("Late Joiner")
        self.assertNotIn("Q456", m._nba_debut_day)
        self.assertEqual(m.title_day("20260211 Yaxel Lendeborg 13"), "2026-02-11")
        self.assertEqual(m.title_day("Celtics at Wizards 2024-12-15 (cropped).jpg"), "2024-12-15")
        self.assertEqual(m.title_day("Yaxel Lendeborg (51831075412).jpg"), "")   # a Flickr id is no day

    def test_lendeborg_pool(self):
        m = self.m
        m.commons_photos = lambda person: [self.commons("20260211 Yaxel Lendeborg 13.jpg", "2026-02-11"),
                                           self.commons("Yaxel Lendeborg Warriors 2026.jpg", "2026-10-30", "current")]
        m.openverse_photos = lambda person: [self.openverse("20260211 Yaxel Lendeborg 13"),   # the same file
                                             self.openverse("20260211 Yaxel Lendeborg 05"),   # only here
                                             self.openverse("20261105 Yaxel Lendeborg 02"),   # an NBA game
                                             self.openverse("20260621 NBA Draft Yaxel Lendeborg")]
        got = {p["title"]: p for p in m.photos("Yaxel Lendeborg")}
        self.assertNotIn("20260211 Yaxel Lendeborg 13", got)              # one picture: the Commons copy
        self.assertEqual(got["20260211 Yaxel Lendeborg 13.jpg"]["team"], "pre-nba")
        self.assertEqual(got["20260211 Yaxel Lendeborg 05"]["team"], "pre-nba")
        self.assertEqual(got["20260211 Yaxel Lendeborg 05"]["date"], "2026-02-11")
        self.assertEqual(got["20261105 Yaxel Lendeborg 02"]["team"], "")
        self.assertEqual(got["20260621 NBA Draft Yaxel Lendeborg"]["team"], "")   # says NBA: not school
        self.assertEqual(got["Yaxel Lendeborg Warriors 2026.jpg"]["team"], "current")
        self.assertEqual([p["team"] for p in m.photos("Yaxel Lendeborg")][-2:], ["pre-nba", "pre-nba"])

    def test_nothing_changes_without_a_day(self):
        m = self.m
        m.commons_photos = lambda person: [self.commons("Late Joiner 2019.jpg", "2019-03-01")]
        m.openverse_photos = lambda person: [self.openverse("20190301 Late Joiner")]
        self.assertEqual([p["team"] for p in m.photos("Late Joiner")], ["", ""])
        self.assertFalse(m.pre_nba_by_day("Yaxel Lendeborg", {"date": "2026-02-11", "team": "former"}))
        self.assertFalse(m.pre_nba_by_day("Yaxel Lendeborg", {"date": "2026", "team": ""}))

    def test_final_read_sees_it(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("A picture marked PRE-NBA (high school, college) on a line about his NBA career", p)
        self.assertIn("PRE-NBA", final_read.picture_line({"person": "Yaxel Lendeborg", "team": "pre-nba",
                                                           "title": "20260211 Yaxel Lendeborg 13"}))


class WikidataCanMissASpell(unittest.TestCase):
    """62. D23 (run 43446225184): Kyrie Irving's Wikidata teams are Cavaliers, Celtics, Mavericks
    (and Duke), with no Nets 2019-2023, so 12 real photos of him in a Nets jersey were left out as
    "a team he never played for". A photo that is HIS (his own Commons category, or his first and
    last name in the title) is trusted; the law still stops Isaiah Thomas shown as Isiah Thomas."""

    CAREER = ["boston celtics", "cleveland cavaliers", "dallas mavericks"]

    def test_his_own_photo_is_trusted(self):
        import compliance as C
        import media
        nets = {"s": "game", "t": "brings ball up court, Nets jersey"}
        cases = [({"title": "Kyrie Irving (51831075412).jpg", "tag": nets}, True),
                 ({"title": "Kyrie_Irving_-_51832441040.jpg", "tag": nets}, True),
                 ({"title": "Darius Garland (51830745547).jpg", "tag": nets, "own_category": True}, True),
                 ({"title": "Darius Garland (51830745547).jpg", "tag": nets}, False),
                 ({"title": "Irving dribbles (2021).jpg", "tag": nets}, False)]
        for c, ok in cases:
            self.assertEqual(media.his_own("Kyrie Irving", c), ok, c["title"])
            self.assertEqual(C.jersey_ok(media.jersey_team(c["tag"]), self.CAREER, media.his_own("Kyrie Irving", c)),
                             ok, c["title"])

    def test_the_isaiah_law_still_holds(self):
        import compliance as C
        import media
        c = {"title": "Isaiah Thomas (50639077836).jpg", "tag": {"s": "game", "t": "dribbles in Wizards jersey"}}
        self.assertFalse(media.his_own("Isiah Thomas", c))
        self.assertFalse(C.jersey_ok("washington wizards", ["detroit pistons"], media.his_own("Isiah Thomas", c)))
        self.assertTrue(C.jersey_ok("brooklyn nets", self.CAREER, True))
        self.assertFalse(C.jersey_ok("brooklyn nets", self.CAREER))

    def test_the_pool_and_the_gate(self):
        import gate
        import media
        self.assertIn("C.jersey_ok(jersey_team(c.get(\"tag\")), career, his_own(person, c))",
                      (ROOT / "src" / "media.py").read_text(encoding="utf-8"))
        self.assertIn('x["his_own"] = his_own(x.get("person") or "", x)',
                      (ROOT / "src" / "media.py").read_text(encoding="utf-8"))
        nets = {"kind": "photo", "person": "Kyrie Irving", "jersey": "brooklyn nets", "page": "p", "url": "u",
                "author": "a", "license": "CC BY-SA 2.0", "match": 7, "title": "Kyrie Irving (51831075412)"}
        flags = {"careers": {"Kyrie Irving": self.CAREER}}
        _, notes = gate.check_visuals([dict(nets, his_own=True)], flags)
        self.assertFalse(any("never played for" in n for n in notes), notes)
        _, notes = gate.check_visuals([dict(nets, his_own=False, title="Isaiah Thomas", person="Isiah Thomas",
                                            jersey="washington wizards")],
                                      {"careers": {"Isiah Thomas": ["detroit pistons"]}})
        self.assertTrue(any("never played for" in n for n in notes), notes)


class TitleBoldButTrue(unittest.TestCase):
    """63. D24 (run 43446225184): the title "Curry's two weeks is a LIE? 😳" called the Warriors'
    "re-evaluated in two weeks" a lie; the hook was read against the sources (D17), the title never
    was. Now one call reads the top titles: an overstated one steps behind, the best true one leads;
    all of them overstated = the Short is held; a failed call changes nothing."""

    TITLES = [{"title": "Curry's two weeks is a LIE? 😳", "score": 100},
              {"title": "Stephen Curry is out WAY longer 😬", "score": 100},
              {"title": "Warriors face a BIG Curry problem 😳", "score": 100}]
    SOURCES = [{"publisher": "Yahoo Sports", "title": "Warriors brace", "text": "re-evaluated in two weeks", "tier": 1}]

    def run_with(self, answer):
        import script
        saved = script.ask_claude
        seen = []

        def ask(prompt, *a, **k):
            seen.append(prompt)
            if isinstance(answer, Exception):
                raise answer
            return answer
        script.ask_claude = ask
        try:
            return script.check_title_truth(copy.deepcopy(self.TITLES), self.SOURCES), seen
        finally:
            script.ask_claude = saved

    def test_the_lie_steps_behind(self):
        got, seen = self.run_with({"overstated": [1], "why": "nobody lied"})
        self.assertEqual(len(seen), 1)
        self.assertIn("1. Curry's two weeks is a LIE?", seen[0])
        self.assertEqual(got[0]["title"], "Stephen Curry is out WAY longer 😬")
        self.assertEqual(got[-1]["overstated"], "nobody lied")
        self.assertFalse(got[0].get("all_overstated"))

    def test_all_overstated_or_failed(self):
        got, _ = self.run_with({"overstated": [1, 2, 3], "why": "x"})
        self.assertTrue(got[0].get("all_overstated"))
        got, _ = self.run_with(OSError("down"))
        self.assertEqual([t["title"] for t in got], [t["title"] for t in self.TITLES])
        self.assertFalse(any(t.get("overstated") for t in got))
        got, _ = self.run_with({"overstated": [], "why": ""})
        self.assertEqual(got[0]["title"], self.TITLES[0]["title"])

    def test_wired_in(self):
        import script
        src = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn("titles = check_title_truth(titles, sources)", src)
        self.assertIn('if titles and titles[0].get("all_overstated"):', src)
        self.assertEqual(script.TITLES_CHECKED, 10)   # his answer: every title is read
        p = " ".join(script.TITLE_TRUTH.split())
        self.assertNotIn('"Is X a LIE?"', p)    # his answer (2026-11-14): no special rule for question titles
        self.assertIn("BOLD BUT TRUE", p)


class PickSheetsByName(unittest.TestCase):
    """64. D25 (run 43446225184): the pick took 15 and 19 steps (169k and 138k tokens). Its prompt
    said "beat_0.jpg, beat_1.jpg, ..." and Claude cannot list the folder (no Glob), so it opened one
    sheet, then guessed the next name, a step each. The exact names let it open all in one step."""

    def test_names_in_beat_order(self):
        import media
        with tempfile.TemporaryDirectory() as d:
            for n in ("beat_10.jpg", "beat_0_2.jpg", "beat_1.jpg", "beat_0.jpg", "beat_2.jpg", "note.txt"):
                (Path(d) / n).write_bytes(b"x")
            self.assertEqual(media.sheet_names(Path(d)), "beat_0.jpg, beat_0_2.jpg, beat_1.jpg, beat_2.jpg, beat_10.jpg")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(media.sheet_names(Path(d)), "none")

    def test_both_pick_calls_name_the_sheets(self):
        import media
        p = " ".join(media.PICK_PROMPT.split())
        self.assertIn("are exactly these contact sheets (one or more per beat): SHEETS.", p)
        self.assertNotIn("beat_0.jpg, beat_1.jpg, ...", p)
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertEqual(src.count('PICK_PROMPT.replace("SHEETS", sheet_names(sheets))'), 2)


class PopularConflictWeighsMore(unittest.TestCase):
    """65. D26 (owner, 2026-11-13): a conflict between popular teams or players weighs slightly more
    than another kind of scandal, intrigue or drama around a popular player. Run 43446225184 gave a
    Curry injury follow-up (no conflict) the slot. On top of the +6 for any real conflict: +0 at
    star power 5 or less, up to +4 at 10. Replayed on every kept run: 3 runs (43253965466,
    43262308476, 43294793044) would have made "Mike Brown calls out refs" (S8-9) instead of an old
    feud; nothing else changes."""

    BASE = {"drama": 7, "virality": 7, "debate": 7, "search_hits": 3, "youtube_heat": 5, "hours_old": 2,
            "nba": True, "kind": "player_vs_player"}

    def score(self, **k):
        import editor
        return editor.short_score({**self.BASE, **k})

    def test_the_popular_fight_weighs_more(self):
        calm = self.score(star_power=10, conflict=False)
        self.assertAlmostEqual(self.score(star_power=10, conflict=True) - calm, 10.0, places=1)    # 6 + 4
        self.assertAlmostEqual(self.score(star_power=5, conflict=True) - self.score(star_power=5, conflict=False), 6.0, places=1)
        self.assertAlmostEqual(self.score(star_power=8, conflict=True) - self.score(star_power=8, conflict=False), 8.4, places=1)
        self.assertAlmostEqual(self.score(star_power=3, conflict=True) - self.score(star_power=3, conflict=False), 6.0, places=1)

    def test_only_slightly(self):
        # a popular fight beats an equally popular non-fight of the same size, but a much bigger
        # story without a fight still wins (popularity weighs as much as the beef: his earlier rule)
        self.assertGreater(self.score(star_power=9, conflict=True), self.score(star_power=9, conflict=False, debate=9))
        self.assertGreater(self.score(star_power=10, conflict=False, drama=9, virality=9, youtube_heat=9),
                           self.score(star_power=6, conflict=True))


class WhoSaidItAndIsItStillTrue(unittest.TestCase):
    """66. Run 43446225184 (D2 notes): "Shams Charania told ESPN that's just a checkpoint" - the
    word was the Yahoo writer's conclusion, not Shams's; "eight straight wins now rest on
    Lendeborg" - the streak had ended. The final read saw the second only as a doubt. Now the
    writer and the critic give each claim to its owner and say an ended fact as over, and the
    final read counts both as errors (with the source's words as evidence)."""

    def test_writer_and_critic(self):
        import script
        p = " ".join(script.PROMPT.split())
        self.assertIn("WHO SAID IT, AND IS IT STILL TRUE", p)
        self.assertIn("is the outlet's, never the insider's or player's it writes about", p)
        h = " ".join(script.HUMANIZE.split())
        self.assertIn("- WHO SAID IT: every \"X said / told / says\" gives X only what X said in the sources", h)
        self.assertIn("A fact that has ended (a streak, a spell, a record) is said as over", h)
        self.assertIn("WHO SAID IT", script.HUMANIZE.format(voice="v", sources="s", draft="d"))   # no stray braces

    def test_final_read_errors(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("Also when \"X said / told / says\" gives X a claim that, in the sources, is the outlet's own "
                      "conclusion and not X's words", p)
        self.assertIn("a fact the sources show has ENDED or changed, said as still true now", p)


class RewriteKeepsTheHookRules(unittest.TestCase):
    """67. D27 (run 43485568700): the bold-true rewrite of a hook only had to pass the fact checks.
    It gave Mitchell's Short "Donovan Mitchell fires back at Barkley: 'Who gives a f—k?'..." (gate
    REJECT, one of the run's two Shorts lost) and Arenas's "Steph Curry is out at least two weeks,
    and Gilbert Arenas warns..." (the story's lead at word 9). Now a rewrite keeps every hook rule
    (no profanity, the lead person in the first 8 words), else the old order stays; a profane hook
    never leads, and the order is applied before the truth read so the read hook can lead."""

    def test_the_two_real_rewrites_fail(self):
        import script
        r = script.rewrite_keeps_hook_rules
        self.assertFalse(r("Steph Curry is out at least two weeks, and Gilbert Arenas warns Draymond Green will "
                           "struggle without him.", "Gilbert Arenas just buried Draymond Green without Steph Curry.",
                           "arenas"))
        self.assertFalse(r("Donovan Mitchell fires back at Barkley: 'Who gives a f—k?' after Cavs 'suck' remark.",
                           "Donovan Mitchell told Barkley nobody in Cleveland cares.", "mitchell"))
        self.assertTrue(r("Gilbert Arenas warns Draymond Green will struggle without Steph Curry.",
                          "Gilbert Arenas just buried Draymond Green without Steph Curry.", "arenas"))
        # the 7 real rewrites of 43395656602-43485568700: 4 keep passing; Kyrie's (run 43446225184) put
        # Kyrie at word 9 behind Ujiri, so the next hook leads now ("Dallas is winning with Kyrie Irving...")
        self.assertFalse(r("Masai Ujiri said the Mavs truly believe in Kyrie Irving, yet rival teams still eye him.",
                           "Masai Ujiri says the Mavs are keeping Kyrie Irving, but rivals want him.", "irving"))
        self.assertTrue(r("Dejounte Murray deleted two angry posts after the Nets blowout, Pelicans sinking at 4-8.",
                          "Dejounte Murray blasted the Pelicans, then deleted it.", "murray"))
        self.assertTrue(r("Charles Barkley calls out Kyle Kuzma on live TV for not letting Luka Doncic land.",
                          "Charles Barkley ripped Kyle Kuzma for hurting Luka Doncic.", "barkley"))
        # no lead known: a name of the old first 8 words stays in the first 8
        self.assertFalse(r("After a long night in Boston, the fans saw Tatum snub Brown.", "Tatum snubbed Brown again.", ""))

    def test_profane_never_leads_and_order_first(self):
        import script
        hooks = [{"text": "Mitchell to Barkley: 'Who gives a f—k?'", "unsupported_details": []},
                 {"text": "Charles Barkley said the Cavs suck, and Donovan Mitchell fired straight back.",
                  "unsupported_details": []}]
        read = []
        saved = script.check_hook_truth
        script.check_hook_truth = lambda h, s, lead="": read.append(h["text"]) or "ok"
        try:
            script.truth_order(hooks, [], "barkley")
        finally:
            script.check_hook_truth = saved
        self.assertTrue(hooks[0]["text"].startswith("Charles Barkley said"))
        self.assertEqual(read, [hooks[0]["text"]])      # the hook that leads is the one that was read


class OnRecordBeatReporter(unittest.TestCase):
    """68. D29 (owner, 2026-11-13: an on-record quote a team's beat journalist published is a
    reliable source). Run 43485568700 held Mitchell vs Barkley ("only secondary outlets and no
    named insider") though Hoops Wire wrote: "Chuck ain't here," Mitchell told Chris Fedor of
    Cleveland.com. A named reporter of a named outlet credited for a direct quote counts; an
    outlet alone, a reporter with no quote, or "a source told" does not."""

    def test_who_counts(self):
        import compliance as C
        cases = {'“Chuck ain’t here,” Mitchell told Chris Fedor of Cleveland.com. Barkley said': ["chris fedor (cleveland.com)"],
                 '“We are fine,” he said, according to The Athletic’s Joe Vardon.': ["joe vardon (the athletic)"],
                 '“Who gives a f—k?” Mitchell said, per Cleveland.com. “Chuck': ["(cleveland.com)"],   # his answer: an outlet is enough
                 '“I hate him,” a league source said, per ESPN.': [],                                # anonymous never
                 '“Let’s go,” Brown told Tatum before the game.': [],                                 # "told X" alone: X may be a player
                 'Chris Fedor of Cleveland.com reported the Cavs are shopping Allen.': [],
                 '“I hate him,” a source told Bleacher Report.': [],
                 'Mitchell told Chris Fedor of Cleveland.com he is not worried.': []}   # no quote: not on record
        for text, want in cases.items():
            self.assertEqual(C.on_record_reporters([{"text": text}]), want, text)

    def test_the_mitchell_story_passes(self):
        import compliance as C
        secondary = {"publisher": "Hoops Wire", "tier": 2, "title": "Mitchell dismisses Barkley",
                     "text": 'Donovan Mitchell answered. “Chuck ain’t here,” Mitchell told Chris Fedor of Cleveland.com.'}
        self.assertEqual(C.check_sources([secondary])[0], C.PASS)
        plain = dict(secondary, text='Donovan Mitchell answered Barkley, a blog says.')
        self.assertEqual(C.check_sources([plain])[0], C.REVIEW)
        claim = [{"text": "Mitchell told Fedor Chuck ain't here", "status": "REPORTED", "source": 1}]
        _, _, out = C.check_claims(claim, [secondary], "Mitchell told Cleveland.com that Chuck ain't here.")
        self.assertEqual(out[0]["status"], "REPORTED")
        _, _, out = C.check_claims(claim, [plain], "Mitchell reportedly said Chuck ain't here.")
        self.assertEqual(out[0]["status"], "RUMOR")


class TopUpsKeepTheTeamOrder(unittest.TestCase):
    """69. D28 (run 43485568700): the unjudged extra shots ranked only by face and game, so three
    Utah Jazz photos of Donovan Mitchell (2018-19) filled Cavs lines ("Are the Cavs the same
    failing team...?") while Cavs photos were left. The agreed order now holds for top-ups too:
    today's team or no team first, a former team after - never dropped."""

    def test_order(self):
        import photo_tags
        clear = {"v": "C", "s": "game", "t": "drives"}
        pool = [{"page": "utah", "team": "former", "tag": clear, "hoops": True},
                {"page": "cavs", "team": "current", "tag": clear, "hoops": True},
                {"page": "plain", "team": "", "tag": {"v": "B", "s": "game", "t": "back turned"}, "hoops": True},
                {"page": "untagged", "team": "", "hoops": True}]
        self.assertEqual([c["page"] for c in sorted(pool, key=photo_tags.fill_rank)],
                         ["cavs", "plain", "utah", "untagged"])

    def test_person_photos_both_ways(self):
        import media
        saved = (media.photos, media.solo_title)
        media.solo_title = lambda c, p: True
        try:
            pool = [{"page": "u", "team": "former", "hoops": True, "title": "Donovan Mitchell Utah"},
                    {"page": "c", "team": "current", "hoops": False, "title": "Donovan Mitchell"}]
            media.photos = lambda person: [dict(p) for p in pool]
            self.assertEqual([c["page"] for c in media.person_photos("Donovan Mitchell", set())], ["c", "u"])
        finally:
            media.photos, media.solo_title = saved


class TopUpsByRelevanceTeamAndFace(unittest.TestCase):
    """70. D30 (owner, 2026-11-14: "team and face are both important and both must be right; which
    photo is chosen is left to the relevance score"). The extra shots of a long beat now come first
    from the photos Claude scored 6+ for that very beat (best score first); an unscored photo only
    after them, and only if he is clearly seen AND, on a line naming a team or a time, not in a
    former team's photo or another team's jersey (run 43485568700: Mitchell in a Jazz jersey on
    "Are the Cavs the same failing team?")."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("person_photos", "download", "picture_hash", "image_ok",
                                                      "teams_of", "beat_seconds", "spoken")}
        media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
        media.image_ok = lambda path: True
        media.picture_hash = lambda path: None
        media.teams_of = lambda person: ("cleveland cavaliers", {"utah jazz"})
        self.folder = media.ROOT / "data" / "_test_topup"

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        shutil.rmtree(self.folder, ignore_errors=True)

    @staticmethod
    def ph(title, team="", t="drives", v="C", s="game"):
        return {"kind": "photo", "title": title, "page": "https://commons.wikimedia.org/wiki/File:" + title,
                "url": "u-" + title, "author": "a-" + title, "team": team, "tag": {"v": v, "s": s, "t": t}}

    def test_both_rules(self):
        ok = self.m.topup_ok
        line = "Are the Cavs the same failing team, or should Mitchell tune Chuck out?"
        self.assertFalse(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"), line, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2019", "", "shoots, Jazz jersey"), line, "Donovan Mitchell"))
        self.assertTrue(ok(self.ph("Mitchell back", "current", v="B"), line, "Donovan Mitchell"))    # his answer: from behind is fine
        self.assertFalse(ok(self.ph("Mitchell far", "current", v="S"), line, "Donovan Mitchell"))    # a small figure never
        # a line naming his former team allows that team (his answer); today's team still fits a Cavs line
        utah = "In his Utah years Mitchell carried the Jazz."
        self.assertTrue(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"), utah, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell Cavs", "current", "dribbles, Cavaliers white"), utah, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2018", "former", "lines up a free throw"), utah, "Donovan Mitchell"))  # which old team? unknown: no
        # a time only ("last year", "now"): today's team or no team
        self.assertFalse(ok(self.ph("Mitchell 2019", "former", "shoots"), "He was great last year.", "Donovan Mitchell"))
        self.assertTrue(ok(self.ph("Mitchell 2024", "current", "shoots"), "He was great last year.", "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2018", "former", "lines up a free throw"), line, "Donovan Mitchell"))  # no jersey word
        self.assertTrue(ok(self.ph("Mitchell Cavs", "current", "dribbles, Cavaliers white"), line, "Donovan Mitchell"))
        # a line with no team and no time: a former team stays allowed (agreed picture rules)
        self.assertTrue(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"),
                           "Mitchell fired straight back at Barkley.", "Donovan Mitchell"))
        self.assertFalse(ok({**self.ph("untagged"), "tag": None}, "Mitchell fired back.", "Donovan Mitchell"))

    def test_scored_spares_first_then_safe_unscored(self):
        m = self.m
        line = "Are the Cavs the same failing team, or should Mitchell tune Chuck out?"
        m.spoken = lambda short: [{"say": line}]
        m.beat_seconds = lambda short, i: 12.0          # 4 shots: the first + 3 top-ups
        m.person_photos = lambda person, shown: [self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"),
                                                 self.ph("Mitchell Cavs 2023", "current", "dribbles, Cavaliers white")]
        clip = {"kind": "video", "id": "v1", "title": "Mitchell clip", "page": "pv1", "url": "uv1", "author": "a", "match": 9}
        first = {**self.ph("Mitchell podium", "current"), "file": "data/x.jpg", "match": 8, "alts": [],
                 "_spare": [{**self.ph("Mitchell Cavs 2024", "current"), "match": 8}, clip]}   # best score first
        got = m.fill_empty([first], 1, self.folder, set(), ["Donovan Mitchell"], {"beats": [{"say": line}]})
        titles = [a["title"] for a in got[0]["alts"]]
        self.assertEqual(titles, ["Mitchell clip", "Mitchell Cavs 2024", "Mitchell Cavs 2023"])   # clips too, by score
        self.assertEqual([a.get("match") for a in got[0]["alts"]], [9, 8, None])
        self.assertNotIn("_spare", got[0])

    def test_spares_are_kept_in_the_pick(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('chosen["_spare"] = [', src)
        self.assertIn("scores.get(j, 0) >= SPARE_MIN", src)
        import media
        self.assertEqual(media.SPARE_MIN, 8)       # his answer: only the person the line is about
        self.assertIn("next_spare(it, i, f\"more{k}\") or next_face(i, f\"more{k}\")", src)


class HisAnswersOnTheOlderRules(unittest.TestCase):
    """71. 2026-11-14, his answers on sub-logics of the older code (each was mine): the hook fits
    the first 3-4 seconds (8-12 words at our voice's measured 2.8 words a second); "trade" alone is
    no major turn (62 of 287 real headlines were plain rumors); an article is read up to 6000
    characters; five big newspapers / broadcasters are tier 1."""

    def test_hook_length(self):
        import script
        self.assertEqual((script.HOOK_MIN, script.HOOK_MAX), (8, 12))
        self.assertTrue(script.one_question("Shams says Stephen Curry is out closer to a month."))       # 10
        self.assertFalse(script.one_question("Steph Curry is out at least two weeks, and Gilbert Arenas warns Draymond."))  # 14
        self.assertFalse(script.one_question("Curry is out a month."))                                    # 5

    def test_major_turn(self):
        import editor
        t = editor.MAJOR_TURN.search
        for h in ("Kyrie Irving Trade Rumors Updated by NBA Insider", "Lakers sign center to two-way contract",
                  "Celtics in a fight for the East", "Luka is fine with ankle tweak"):
            self.assertIsNone(t(h), h)
        for h in ("Nick Young: I Apologize Like a Man", "Bassey Rips Smart After Getting Punched",
                  "Jaylen Brown requests a trade", "Smart suspended three games", "Pelicans waive Murray",
                  "Bucks fired Doc Rivers"):
            self.assertIsNotNone(t(h), h)
        self.assertIsNone(t("Draymond fired back at Rivers"))

    def test_article_and_tier1(self):
        import script, sources
        self.assertEqual(script.ARTICLE_CHARS, 6000)
        for p in ("washington post", "los angeles times", "boston globe", "sporting news", "sportsnet"):
            self.assertIn(p, sources.TIER1_PUBLISHERS)
        for p in ("heavy", "fadeaway world", "essentiallysports", "sportskeeda"):
            self.assertNotIn(p, sources.TIER1_PUBLISHERS)

    def test_new_details(self):
        import compliance as C
        src = [{"text": "Barkley said it on the show. Mitchell spoke after the game.", "title": ""}]
        self.assertEqual(C.unsupported_details("Barkley said it on live TV, postgame.", src), [])
        self.assertEqual(sorted(C.unsupported_details("He was in tears courtside, then posted on Instagram.", src)),
                         ["courtside", "in tears", "on social media"])
        self.assertEqual(C.unsupported_details("He laughed in the tunnel.", src), ["tunnel", "laughed"])


if __name__ == "__main__":
    unittest.main()

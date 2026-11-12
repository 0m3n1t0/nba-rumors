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
             "url": "https://sports.yahoo.com/x", "text": self.TEXT, "trusted": True, "tier": 1}]
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
            offered = [{**_commons("Jaylen Brown 2022.jpg"), "url": "u1"},
                       {**_commons("Jaylen Brown 2024.jpg"), "url": "u2"}]
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

    def test_full_scene_is_dropped(self):
        """Owner, 2026-11-12: never more than SCENE_MAX photos of one scene (was: it waited)."""
        m, c = self.m, self._pool()
        scenes = self.Counter({m.scene_of(c[0]): 3})
        tier = lambda j: 3
        scores = {0: 8, 1: 8, 5: 7, 6: 6}
        self.assertEqual(m.spread_scenes([0, 1, 5, 6], c, tier, scores, scenes), [5, 6])
        self.assertEqual(m.spread_scenes([0, 1, 5], c, tier, scores, self.Counter()), [0, 1, 5])
        self.assertEqual(m.spread_scenes([0, 1], c, tier, scores, scenes), [])     # nothing else: empty

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
        # before B11: 9 of 13 from the Wizards game. Since 2026-11-12: 3 of them, then the 8 other
        # photos, then nothing more (no 4th Wizards shot; fill_empty or the previous picture)
        self.assertEqual(sum(1 for j in shown if j < len(run)), 3)
        self.assertEqual(len(set(shown)), 11)
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
            wiz = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "url": f"w{n}"} for n in (11, 12, 13)]
            new = {**self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"), "url": "a"}
            m.person_photos = lambda person, shown: [dict(c) for c in wiz + [new]]
            m.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            m.image_ok = lambda path: True
            m.picture_hash = lambda path: None
            on = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "file": "data/x.jpg"} for n in (15, 23, 36)]
            items = [{**on[0], "file": "data/x.jpg", "match": 8, "alts": on[1:]}, None, None]
            got = m.fill_empty(items, 3, folder, set(), ["Jaylen Brown"], None)
            self.assertEqual(got[1]["title"], "Jaylen Brown 2022.jpg")       # another game first
            self.assertIsNone(got[2])        # never a 4th Wizards shot: the previous picture goes on
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

    STATED = "Gilbert Arenas just called Ayesha Curry the only blemish on Steph Curry's family."
    ASKED = "Did Gilbert Arenas really call Ayesha Curry the only blemish in Stephen Curry's family?"

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
        self.assertIn("8-14 words", script.HOOK_RETRY if hasattr(script, "HOOK_RETRY") else p)
        self.assertIn("PUNCH:", script.HUMANIZE)
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
        self.saved = photo_tags.CACHE
        photo_tags.CACHE = self.tmp / "tags.json"

    def tearDown(self):
        self.t.CACHE = self.saved
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

        def ask(prompt, folder=None, timeout=0):
            calls.append(sorted(os.listdir(folder)))
            self.assertIn("Steph Curry", prompt)
            return {"photos": [{"n": k, "v": "A" if k == 11 else "C", "s": "game", "e": "calm", "t": "plays"}
                               for k in range(1, 12)], "same": [[2, 3]]}
        n = self.t.tag_person("Steph Curry", pool, ask, self.fake_download, self.m.photo_era, self.m.scene_of)
        self.assertEqual(n, 11)
        self.assertEqual(calls, [["tags_1.jpg", "tags_2.jpg"]])          # 9 a sheet
        self.assertEqual(pool[1]["moment"], pool[2]["moment"])
        self.assertFalse(self.t.usable(pool[10]))
        fresh = [self.ph(n) for n in range(1, 12)]
        self.assertEqual(self.t.tag_person("Steph Curry", fresh, ask, self.fake_download,
                                           self.m.photo_era, self.m.scene_of), 0)
        self.assertEqual(len(calls), 1)                                   # kept: no second look
        self.assertEqual(fresh[0]["tag"]["s"], "game")
        self.assertEqual(fresh[1]["moment"], fresh[2]["moment"])

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

        def ask(prompt, folder=None, timeout=0):
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
                {**self.ph(2), "title": "Steph Curry popcorn.jpg", "tag": {"v": "A", "s": "other"}},
                {**self.ph(3), "title": "Steph Curry stage.jpg", "tag": {"v": "C", "s": "stage"}},
                {**self.ph(4), "title": "Steph Curry far.jpg", "tag": {"v": "S", "s": "game"}, "hoops": True},
                {**self.ph(5), "title": "Steph Curry game.jpg", "tag": {"v": "C", "s": "game"}, "hoops": True}]
        saved = m.photos
        try:
            m.photos = lambda who: pool
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p5", "p4"])
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


if __name__ == "__main__":
    unittest.main()

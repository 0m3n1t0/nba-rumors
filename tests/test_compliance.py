"""Monetization safety tests: python -m unittest discover -s tests -v

Each case is a small, realistic story (sources + script) run through the SAME code the
pipeline uses. Case 13 matters most: a legitimate dramatic NBA story must still PASS.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import compliance as C  # noqa: E402
import gate  # noqa: E402


def src(publisher, title, text, tier=1):
    return {"publisher": publisher, "title": title, "summary": "", "text": text, "tier": tier,
            "link": f"https://example.com/{publisher.lower().replace(' ', '-')}"}


def short(spoken, beats, titles, thumb, claims, hook=None):
    return {"spoken": spoken, "beats": beats, "titles": [{"title": t, "score": 90} for t in titles],
            "thumbnail_text": thumb, "claims": claims, "hook": {"text": hook or spoken.split("?")[0] + "?"},
            "unsupported_quotes": [], "unsupported_numbers": [], "too_similar_to": ""}


BEEF_SOURCES = [
    src("ESPN", "Jaylen Brown says there's nothing to talk about with Jayson Tatum",
        "Jaylen Brown told reporters on Monday that he has nothing to talk about with Jayson Tatum "
        "before facing the Celtics for the first time since his trade to Philadelphia. Brown answered "
        "a Tatum video with a cap emoji, per ESPN's Shams Charania. Tatum said there is no beef and that "
        "they are fine, adding a little lamb chops and some gravy. The 76ers host Boston on Tuesday."),
    src("Yahoo Sports", "Brown, Tatum and the cap emoji",
        "According to Shams Charania, Brown's cap emoji was aimed at Tatum. The two won a title together "
        "in 2024 before the trade split them up last summer."),
]


class Story(unittest.TestCase):

    # 1. Confirmed trade: official word -> PASS, CONFIRMED stays CONFIRMED
    def test_01_confirmed_trade(self):
        sources = [src("NBA.com", "Thunder acquire Nique Clifford from Kings",
                       "The Oklahoma City Thunder announced Monday that they have officially acquired "
                       "Nique Clifford from the Sacramento Kings in exchange for a 2027 second-round pick."),
                   src("ESPN", "OKC lands Clifford", "The Thunder completed the trade for Nique Clifford, "
                       "the team announced in a statement. The Kings get a second-round pick.")]
        claims = [{"text": "The Thunder traded for Nique Clifford", "status": "CONFIRMED", "source": 1}]
        v, notes, out = C.check_claims(claims, sources, "The Thunder just traded for Nique Clifford.")
        self.assertEqual(out[0]["status"], "CONFIRMED")
        self.assertEqual(v, C.PASS)
        self.assertEqual(C.check_headline("Thunder TRADED for Nique Clifford", out, sources, "title")[0], C.PASS)

    # 2. Credible but unconfirmed trade report: REPORTED, eligible when attributed
    def test_02_reported_trade(self):
        sources = [src("ESPN", "Warriors exploring Porzingis trade",
                       "The Golden State Warriors are exploring trades for Kristaps Porzingis, per ESPN's "
                       "Shams Charania. Rival executives want draft picks attached.")]
        claims = [{"text": "Warriors exploring a Porzingis trade", "status": "REPORTED", "source": 1,
                   "reported_by": "Shams Charania"}]
        v, _, out = C.check_claims(claims, sources, "Per ESPN, the Warriors are exploring a Porzingis trade.")
        self.assertEqual(v, C.PASS)
        self.assertEqual(out[0]["status"], "REPORTED")
        # a title that says the trade is DONE is not allowed on a report; a question is
        self.assertNotEqual(C.check_headline("Warriors TRADED Porzingis", out, sources, "title")[0], C.PASS)
        self.assertEqual(C.check_headline("Are the Warriors trading Porzingis?", out, sources, "title")[0], C.PASS)

    # 3. Unsupported rumor: secondary blog, no insider -> not publishable automatically
    def test_03_unsupported_rumor(self):
        sources = [src("HoopsBuzz Blog", "Could LeBron be traded?",
                       "Some fans online think LeBron James could be moved before the deadline.", tier=2)]
        v, _, _ = C.check_sources(sources)
        self.assertEqual(v, C.REVIEW)
        claims = [{"text": "LeBron could be traded", "status": "REPORTED", "source": 1}]
        _, _, out = C.check_claims(claims, sources, "Rumors say LeBron could be traded.")
        self.assertEqual(out[0]["status"], "RUMOR")
        v2, _, _ = C.check_claims([{"text": "LeBron asked out", "status": "UNVERIFIED", "source": 1}],
                                   sources, "Rumors say LeBron asked out.")
        self.assertEqual(v2, C.REVIEW)

    # 4. Two sites repeating ONE original report are one report, not corroboration
    def test_04_repeated_report_is_one(self):
        sources = [src("Bleacher Report", "Report: Kings shopping Sabonis",
                       "The Kings are shopping Domantas Sabonis, per Marc Stein."),
                   src("ClutchPoints", "Sabonis on the block?",
                       "According to Marc Stein, Sacramento is listening to offers for Sabonis.", tier=2)]
        self.assertEqual(C.independent_reports(sources), 1)
        claims = [{"text": "Kings shopping Sabonis", "status": "CONFIRMED", "source": 1}]
        _, notes, out = C.check_claims(claims, sources, "Per Marc Stein, the Kings are shopping Sabonis.")
        self.assertEqual(out[0]["status"], "REPORTED")      # downgraded, never upgraded
        self.assertTrue(any("downgraded" in n for n in notes))

    # 5. Fabricated locker-room conversation / invented source -> REJECT
    def test_05_fabricated_locker_room(self):
        spoken = ("In the locker room, he yelled at Tatum. A league source says Brown wanted out. "
                  "Per ESPN, there is nothing to talk about.")
        v, notes = C.check_fabrication(spoken, BEEF_SOURCES, [], [])
        self.assertEqual(v, C.REJECT)
        self.assertTrue(any("invented" in n for n in notes))

    # 6. Misleading conflict headline: a fight that no source reports -> REJECT
    def test_06_misleading_conflict_headline(self):
        claims = [{"text": "Brown says nothing to talk about with Tatum", "status": "REPORTED", "source": 1}]
        v, notes = C.check_headline("Jaylen Brown PUNCHED Tatum", claims, BEEF_SOURCES, "title")
        self.assertEqual(v, C.REJECT)

    # 7. Incorrect first-frame claim: names someone not in the story -> REJECT
    def test_07_incorrect_thumbnail(self):
        claims = [{"text": "Brown vs Tatum", "status": "REPORTED", "source": 1}]
        known = C.known_names(["LeBron James out vs Pistons", "Jaylen Brown on Tatum"])
        self.assertEqual(C.check_headline("BROWN vs LEBRON", claims, BEEF_SOURCES, "thumbnail", known)[0], C.REJECT)
        self.assertEqual(C.check_headline("BROWN vs TATUM", claims, BEEF_SOURCES, "thumbnail")[0], C.PASS)

    # 8. Unlicensed music: a library track with no licence record, or an NC track -> not PASS
    def test_08_unlicensed_music(self):
        v, _ = gate.check_music({"library": True, "file": "music_library/tense/unknown.mp3"})
        self.assertNotEqual(v, C.PASS)
        v, _ = gate.check_music({"kind": "music", "license": "CC BY-NC 4.0", "file": "x.mp3"})
        self.assertEqual(v, C.REJECT)

    # 9. Incorrect licence metadata on a picture (non-commercial label) -> REJECT
    def test_09_bad_picture_licence(self):
        item = {"kind": "photo", "license": "CC BY-NC-SA 2.0", "author": "someone",
                "page": "https://flickr.com/x", "file": "a.jpg"}
        self.assertEqual(gate.check_visuals([item], {})[0], C.REJECT)
        tv = {"kind": "video", "license": "CC BY 3.0", "author": "uploader", "source": "Wikimedia Commons",
              "page": "https://commons.wikimedia.org/wiki/File:ESPN_full_game_highlights.webm",
              "title": "ESPN full game highlights", "file": "b.webm"}
        self.assertEqual(gate.check_visuals([tv], {})[0], C.REJECT)

    # 10. The same photo twice in ONE Short is removed (across different Shorts it is allowed)
    def test_10_repeated_photo_within_short(self):
        import render
        from PIL import Image, ImageDraw
        tmp = Path(tempfile.mkdtemp())
        try:
            im = Image.new("RGB", (800, 1000), (40, 90, 160))
            ImageDraw.Draw(im).ellipse((300, 200, 500, 450), fill=(230, 190, 150))
            ImageDraw.Draw(im).rectangle((100, 700, 700, 900), fill=(200, 30, 30))
            im.save(tmp / "a.jpg")
            im.resize((640, 800)).save(tmp / "a_copy.jpg")          # same photo, other size/address
            other = Image.new("RGB", (800, 1000), (10, 10, 10))
            ImageDraw.Draw(other).rectangle((50, 50, 400, 950), fill=(250, 250, 250))
            other.save(tmp / "b.jpg")
            old = render.ROOT
            render.ROOT = tmp
            items = [{"kind": "photo", "file": "a.jpg", "page": "A", "alts": [{"kind": "photo", "file": "b.jpg", "page": "B"}]},
                     {"kind": "photo", "file": "a_copy.jpg", "page": "A2"}]
            out = render.no_repeats(items)
            render.ROOT = old
            self.assertIsNone(out[1])                       # the copy is dropped in the same Short
            self.assertEqual(len(out[0]["alts"]), 1)        # the different photo stays
        finally:
            shutil.rmtree(tmp)

    # 11. Recycled script with different player names -> caught as too similar
    def test_11_recycled_script(self):
        import script
        a = ("Did Jaylen Brown just call out Jayson Tatum on live TV? He said there is nothing to talk "
             "about. Honestly? That is not what no beef sounds like. So who is right?")
        b = ("Did Devin Booker just call out Kevin Durant on live TV? He said there is nothing to talk "
             "about. Honestly? That is not what no beef sounds like. So who is right?")
        self.assertGreaterEqual(script.similarity(script.skeleton(a), script.skeleton(b)), script.SCRIPT_SAME)

    # 12. Graphic / advertiser-sensitive story -> held for review, not auto-published
    def test_12_sensitive_story(self):
        sources = [src("ESPN", "Player arrested on domestic violence charges",
                       "Police arrested the player on domestic violence charges, per ESPN. His lawyer denied "
                       "the allegations in a statement.")]
        spoken = "Per ESPN, he was arrested on domestic violence charges. Graphic details were bloody."
        v, notes, cats = C.check_suitability(spoken, "Arrested", "ARRESTED", "", sources, [], C.original_reporters(sources))
        self.assertIn("crime", cats)
        self.assertNotEqual(v, C.PASS)                     # bloody + left out the denial
        v2, _, _ = C.check_suitability("Fuck that", "What the fuck", "", "", sources, [], {})
        self.assertEqual(v2, C.REJECT)                     # profanity in the title

    # 13. A valid, dramatic NBA beef must PASS end to end
    def test_13_valid_controversial_story_passes(self):
        beats = [{"say": "Brown told reporters there's nothing to talk about with Tatum.", "role": "fact"},
                 {"say": "Then he answered Tatum's video with a cap emoji, per ESPN.", "role": "fact"},
                 {"say": "These two won a title together in 2024. Now he won't even talk to him.", "role": "context"},
                 {"say": "Tuesday is the first time they meet since the trade, so every look gets watched.",
                  "role": "analysis"},
                 {"say": "Honestly? That is not what no beef sounds like. So who blinks first, Brown or Tatum?",
                  "role": "question"}]
        spoken = ("Did Jaylen Brown just tell Jayson Tatum there's nothing to talk about? "
                  + " ".join(b["say"] for b in beats))
        claims = [{"text": "Brown said there is nothing to talk about with Tatum", "status": "CONFIRMED", "source": 1},
                  {"text": "Brown's cap emoji was aimed at Tatum", "status": "REPORTED", "source": 1,
                   "reported_by": "Shams Charania"}]
        s = short(spoken, beats, ["Jaylen Brown's cap emoji was a SHOT 🧢"], "BROWN vs TATUM", claims)
        result = C.evaluate_script(s, BEEF_SOURCES)
        failing = {k: c["notes"] for k, c in result["checks"].items() if c["verdict"] != C.PASS}
        self.assertEqual(result["verdict"], C.PASS, failing)


if __name__ == "__main__":
    unittest.main(verbosity=2)

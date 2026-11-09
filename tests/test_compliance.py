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


class Stage2(unittest.TestCase):

    # 9b. Openverse says CC BY, but the Flickr page now says non-commercial: the photo is dropped
    def test_09b_openverse_relabelled_on_flickr(self):
        import media
        old = media.flickr_licence
        try:
            pages = {"https://flickr.com/p/1": "by-nc", "https://flickr.com/p/2": "by-sa", "https://flickr.com/p/3": None}
            media.flickr_licence = lambda page: pages[page]
            mk = lambda n: {"kind": "photo", "source": "Flickr via Openverse", "page": f"https://flickr.com/p/{n}",
                            "license": "CC BY 2.0", "file": f"{n}.jpg"}
            out = media.verify_openverse([{**mk(1), "alts": [mk(2)]}, mk(3)])
            self.assertEqual(out[0]["page"], "https://flickr.com/p/2")      # NC dropped, the next one leads
            self.assertTrue(out[0]["license_verified"])
            self.assertFalse(out[1]["license_verified"])                    # unreadable page: kept, marked
        finally:
            media.flickr_licence = old

    # Commons: a "CC BY" TV clip, an unflagged own-work clip, a photo Commons flags
    def test_14_commons_provenance(self):
        import media
        tv = {"Credit": "YouTube", "ImageDescription": "ESPN broadcast, full game", "Categories": ""}
        fan = {"Credit": "Own work", "ImageDescription": "Warm-ups before the game", "Categories": "Basketball"}
        flagged = {"Categories": "Deletion requests November 2026|Lakers"}
        self.assertFalse(media.commons_trusted(tv, "File:Lakers highlights.webm", video=True))
        self.assertTrue(media.commons_trusted(fan, "File:Warmups.webm", video=True))
        self.assertFalse(media.commons_trusted(flagged, "File:Player.jpg"))

    # Music: a new library track is recorded but NOT usable until the owner confirms it
    def test_15_music_ledger(self):
        import media
        tmp = Path(tempfile.mkdtemp())
        old = (media.LIBRARY, media.MUSIC_LICENSES)
        try:
            (tmp / "lib" / "tense").mkdir(parents=True)
            (tmp / "lib" / "tense" / "song.mp3").write_bytes(b"x")
            (tmp / "lib" / "tense" / "credit_song.mp3").write_bytes(b"x")
            (tmp / "lib" / "tense" / "credit_song.txt").write_text("Song by Artist, CC BY 4.0")
            media.LIBRARY, media.MUSIC_LICENSES = tmp / "lib", tmp / "music_licenses.json"
            tracks = media.music_ledger()
            self.assertFalse(tracks["tense/song.mp3"]["confirmed"])
            self.assertTrue(tracks["tense/credit_song.mp3"]["attribution_required"])
            v, _ = gate.check_music({"library": True, "library_key": "tense/song.mp3", "file": "x"})
            self.assertNotEqual(v, C.PASS)
            import json as _j
            led = _j.loads(media.MUSIC_LICENSES.read_text())
            led["confirm_all_current"] = True
            media.MUSIC_LICENSES.write_text(_j.dumps(led))
            tracks = media.music_ledger()
            self.assertTrue(all(t["confirmed"] for t in tracks.values()))
        finally:
            media.LIBRARY, media.MUSIC_LICENSES = old
            shutil.rmtree(tmp)

    # History survives a deleted cache: saved to the private repository, restored from it
    def test_16_history_backup_and_restore(self):
        import subprocess
        import state
        tmp = Path(tempfile.mkdtemp())
        old = (state.ROOT, state.DATA, state.STATE, state.HOME)
        try:
            remote = tmp / "remote.git"
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
            work = tmp / "repo"
            subprocess.run(["git", "clone", "-q", str(remote), str(work / "state")], check=True,
                           capture_output=True)
            state.ROOT, state.DATA = work, work / "data"
            state.STATE, state.HOME = work / "state", work / "state" / "nba"
            (state.DATA / "history").mkdir(parents=True)
            (state.DATA / "history" / "made.json").write_text('[{"headline": "Brown vs Tatum"}]')
            state.save("test")
            shutil.rmtree(state.DATA)                                  # the cache is gone
            fresh = tmp / "fresh"                                     # a new runner
            subprocess.run(["git", "clone", "-q", str(remote), str(fresh / "state")], check=True,
                           capture_output=True)
            state.ROOT, state.DATA = fresh, fresh / "data"
            state.STATE, state.HOME = fresh / "state", fresh / "state" / "nba"
            state.restore()
            self.assertIn("Brown vs Tatum", (fresh / "data" / "history" / "made.json").read_text())
        finally:
            state.ROOT, state.DATA, state.STATE, state.HOME = old
            shutil.rmtree(tmp)


class Stage3(unittest.TestCase):

    # The hook score rewards named people + a clash in third-person NBA hooks, not vague ones
    def test_17_hook_score_nba(self):
        import script
        import hookscore
        clash = "Did Jason Kidd just fire back at Doc Rivers over Giannis Antetokounmpo's basketball IQ?"
        vague = "What happened yesterday was surprising for many people around the league?"
        self.assertGreater(script.nba_hook_score(clash)[1], hookscore.score(clash)[1])
        self.assertEqual(script.nba_hook_score(vague)[1], hookscore.score(vague)[1])   # no free points

    # SEO: an accented name matches its plain spelling, and the tags carry both
    def test_18_seo_names(self):
        import script
        r = script.query_test("Warriors want Porziņģis GONE", "Kristaps Porziņģis trade talk.", ["porzingis trade warriors"])
        self.assertTrue(r[0]["pass"], r)

    # 19. Story flow: a beat that only repeats an earlier one, or no closing question -> not ready
    def test_19_retention_check(self):
        import script
        good = [{"say": "Brown said there is nothing to talk about with Tatum.", "stage": "setup"},
                {"say": "Then he answered a Tatum video with a cap emoji, per ESPN.", "stage": "conflict"},
                {"say": "But Tatum says there is no beef at all.", "stage": "twist"},
                {"say": "Off the court they are fine. On it, nobody gives an inch.", "stage": "payoff"},
                {"say": "So who blinks first Tuesday, Brown or Tatum?", "stage": "exit"}]
        r = script.retention_check(good)
        self.assertEqual(r["hard"], [], r)
        self.assertEqual(r["soft"], [], r)
        repeat = good[:2] + [{"say": "Brown said there's nothing to talk about with Tatum.", "stage": "escalation"}] + good[3:]
        self.assertTrue(any("repeats" in x for x in script.retention_check(repeat)["hard"]))
        no_q = good[:-1] + [{"say": "We will see on Tuesday.", "stage": "exit"}]
        self.assertTrue(script.retention_check(no_q)["hard"])
        backwards = [good[2], good[0], good[3], good[4]]
        self.assertTrue(any("backwards" in x for x in script.retention_check(backwards)["soft"]))

    # 20. Captions: phrases of 3-4 words that end at punctuation; names and numbers marked
    def test_20_phrase_captions(self):
        import render
        words = [{"word": w, "start": k * 0.3, "end": k * 0.3 + 0.25} for k, w in
                 enumerate("Then it flipped. Rivers coached him for 3 years, honestly.".split())]
        groups = [" ".join(x["word"] for x in g) for g in render.phrase_groups(words)]
        self.assertEqual(groups[0], "Then it flipped.")
        self.assertTrue(all(len(g.split()) <= 4 for g in groups), groups)
        keys = render.key_words([{"say": "Then it flipped. Rivers coached Giannis for 3 years."}],
                                "Jason Kidd fires back at Doc Rivers")
        self.assertTrue({"rivers", "giannis", "3"} <= keys, keys)
        self.assertNotIn("then", keys)

    # 21. The edit follows the story: each stage gets its own move; the twist punches in
    def test_21_stage_moves(self):
        import render
        short = {"beats": [{"say": "a", "stage": "setup"}, {"say": "b", "stage": "twist"},
                           {"say": "c", "role": "analysis"}, {"say": "d?"}]}
        stages = [render.stage_of(short, i) for i in range(5)]
        self.assertEqual(stages, ["hook", "setup", "twist", "payoff", "exit"])
        self.assertEqual(render.shot_move("twist", 0), "punch")
        self.assertEqual(render.shot_move("escalation", 1), "pan")
        self.assertNotEqual(render.shot_move("setup", 1), render.shot_move("setup", 2))

    # 22. Unjudged photos must be OF the person: a team photo that only mentions him is refused;
    #     the VS frame only for two PEOPLE in the thumbnail
    def test_22_identity_and_vs(self):
        import media
        p = "Kristaps Porziņģis"
        self.assertTrue(media.solo_title({"title": "File:Kristaps Porzingis Wizards 2023.jpg", "hoops": True}, p))
        self.assertFalse(media.solo_title({"title": "File:Taj Gibson media day.jpg", "hoops": True}, p))
        self.assertFalse(media.solo_title({"title": "File:Porzingis and Kuzma.jpg", "hoops": True}, p))
        # a portrait of the RIGHT person is fine even without a basketball word (it beats generic footage)
        self.assertTrue(media.solo_title({"title": "File:Giannis Antetokounmpo (2019).jpg", "hoops": False},
                                         "Giannis Antetokounmpo"))
        self.assertTrue(media.solo_title({"title": "File:Doc Rivers 2.jpg"}, "Doc Rivers"))
        self.assertFalse(media.solo_title({"title": "File:Erik Spoelstra with Doc Rivers.jpg"}, "Doc Rivers"))
        # basketball photos of the person come first
        orig = media.photos
        media.photos = lambda person: [{"page": "1", "title": "Doc Rivers portrait.jpg", "hoops": False},
                                       {"page": "2", "title": "Doc Rivers Bucks game.jpg", "hoops": True},
                                       {"page": "3", "title": "Taj Gibson media day.jpg", "hoops": True}]
        try:
            self.assertEqual([c["page"] for c in media.person_photos("Doc Rivers", set())], ["2", "1"])
        finally:
            media.photos = orig
        who = ["Jason Kidd", "Doc Rivers", "Giannis Antetokounmpo"]
        self.assertEqual(media.vs_sides("KIDD vs RIVERS", who), ["Jason Kidd", "Doc Rivers"])
        self.assertEqual(media.vs_sides("WARRIORS VS PORZINGIS", ["Kristaps Porziņģis"]), [])
        self.assertEqual(media.vs_sides("TRADE DEMAND?", who), [])

    # 23. Sound design is made in code and lands where the story turns
    def test_23_sound_design(self):
        import render
        self.assertIn("between(t", render.swell([(1.0, 2.0)]))
        if not shutil.which("ffmpeg"):   # the safety tests run before ffmpeg is installed
            self.skipTest("ffmpeg not installed yet: the effects are built later, in the render step")
        work = Path(tempfile.mkdtemp())
        try:
            out = render.sfx_track([(0.5, "whoosh"), (1.2, "impact"), (2.0, "logo")], 3.0, work)
            self.assertTrue(out and out.exists() and out.stat().st_size > 1000)
        finally:
            shutil.rmtree(work, ignore_errors=True)

    # 24. The picture rule: relevance first. A relevant clip beats a relevant photo; a generic
    #     clip (or one that only matches a phrase, not the person) never beats a relevant photo.
    def test_24_clip_or_photo(self):
        import media

        def best(cands, scores, who):
            choice = {"ranking": list(range(1, len(cands) + 1)), "scores": scores, "who": who}
            return media.rank_candidates([{"kind": k} for k in cands], choice)[0][0]
        # the person in a clip vs the person in a photo -> the clip
        self.assertEqual(best(["photo", "video"], {"1": 9, "2": 8}, {"1": "P", "2": "P"}), 1)
        # generic basketball clip vs a photo of the person -> the photo
        self.assertEqual(best(["video", "photo"], {"1": 5, "2": 8}, {"1": "G", "2": "P"}), 1)
        # a clip that matches the words with strangers (X) never goes on screen
        ranked = media.rank_candidates([{"kind": "video"}, {"kind": "photo"}],
                                       {"ranking": [1, 2], "scores": {"1": 9, "2": 6}, "who": {"1": "X", "2": "S"}})[0]
        self.assertEqual(ranked, [1])
        # both about the story's people, about as relevant -> the clip
        self.assertEqual(best(["photo", "video"], {"1": 7, "2": 6}, {"1": "S", "2": "S"}), 1)
        # both about the story's people, the photo clearly more relevant -> the photo
        self.assertEqual(best(["video", "photo"], {"1": 5, "2": 8}, {"1": "S", "2": "S"}), 1)
        # a beat with a relevant picture (7+) is not searched again; a weak one is
        self.assertFalse(media.retry_needed([{}], {"score": 8}))
        self.assertTrue(media.retry_needed([{}], {"score": 6}))
        # a beat Claude did not judge: only a photo surely OF one of the story's people
        who = ["Kristaps Porziņģis", "Steve Kerr"]
        self.assertTrue(media.unjudged_ok({"kind": "photo", "title": "File:Kristaps Porzingis 2023.jpg"}, who))
        self.assertFalse(media.unjudged_ok({"kind": "photo", "title": "File:Taj Gibson media day.jpg"}, who))
        self.assertFalse(media.unjudged_ok({"kind": "video", "title": "Porzingis dunk"}, who))

    # 25. The closing question is always the last sentence; stock catchphrases are flagged
    def test_25_question_last_and_tics(self):
        import script
        beats = [{"say": "Rivers went 97 and 103 in Milwaukee."},
                 {"say": "So who's right, Doc or Giannis? Tell me I'm wrong. Subscribe, NBA drama drops here every day."}]
        script.add_cta(beats, "seed")
        self.assertTrue(beats[-1]["say"].endswith("Doc or Giannis?"), beats[-1]["say"])
        self.assertEqual(script.retention_check(beats)["hard"], [])
        self.assertIn("tell me i'm wrong", script.stock_tics(beats))
        clean = [{"say": "Brown got traded to Philly this summer, and Tuesday he faces Tatum."},
                 {"say": "So is it really no beef?"}]
        self.assertEqual(script.stock_tics(clean), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

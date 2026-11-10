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

    # 26. Faces never get lost: the second search keeps every photo of the story's people,
    #     each beat sees different photos of the person, attribution words are not people,
    #     a brief Openverse 504 is retried
    def test_26_faces_kept(self):
        import media
        keep = [{"kind": "video", "id": "c1", "page": "c1"}]
        faces = [{"kind": "photo", "page": "tatum1"}, {"kind": "photo", "page": "brown1"}]
        more = [{"kind": "video", "id": "s1", "page": "s1"}]
        pool = media.round2_pool(keep, faces, more)
        self.assertEqual([c["page"] for c in pool], ["c1", "tatum1", "brown1", "s1"])
        photos = [{"page": str(k)} for k in range(10)]
        beat0 = media.photo_window(photos, 3, 0)
        beat1 = media.photo_window(photos, 3, 1)
        self.assertEqual([c["page"] for c in beat0], ["0", "1", "2"])   # beat 0 unchanged: the best
        self.assertFalse({c["page"] for c in beat0} & {c["page"] for c in beat1})
        self.assertEqual(len(media.photo_window(photos[:2], 3, 4)), 2)
        self.assertTrue(media.not_a_person("Per Yahoo"))
        self.assertTrue(media.not_a_person("Yahoo Sports"))
        self.assertFalse(media.not_a_person("De'Aaron Fox"))
        self.assertFalse(media.not_a_person("Jayson Tatum"))
        import io, json as js, urllib.error
        calls = []

        def fake(req, timeout=30):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError("u", 504, "Gateway Timeout", {}, None)
            return io.BytesIO(js.dumps({"results": [{"title": "Jayson Tatum dunk", "width": 1200, "height": 1600,
                                                     "license": "by", "license_version": "2.0", "url": "x",
                                                     "foreign_landing_url": "https://flickr.com/p/9"}]}).encode())
        orig_open, orig_sleep, budget = media.urllib.request.urlopen, __import__("time").sleep, media.OPENVERSE_BUDGET[0]
        media.urllib.request.urlopen = fake
        __import__("time").sleep = lambda s: None
        media.OPENVERSE_BUDGET[0] = 50
        try:
            found = media.openverse_photos("Jayson Tatum")
        finally:
            media.urllib.request.urlopen, media.OPENVERSE_BUDGET[0] = orig_open, budget
            __import__("time").sleep = orig_sleep
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(found), 1)

    # 27. Only relevant pictures: no objects, no women's/college games on an NBA channel, no fake
    #     "names" from Title Case headlines, refused photos never come back, the hook never opens
    #     on a plain background
    def test_27_relevance_guards(self):
        import media, render
        for junk in ["Gobert Again", "During Timberwolves-Pelicans", "Blank Space", "Golden State", "Per Yahoo"]:
            self.assertTrue(media.not_a_person(junk), junk)
        for real in ["Rudy Gobert", "Jonathan Kuminga", "Taylor Swift", "Magic Johnson", "De'Aaron Fox",
                     "Will Richard", "Derrick White", "Jalen Green", "Kon Knueppel"]:
            self.assertFalse(media.not_a_person(real), real)
        short = {"headline": "Jonathan Kuminga Gets Frustrated With Rudy Gobert Again During Timberwolves-Pelicans Game",
                 "beats": [{"say": "Kuminga yelled at Gobert."}]}
        old_check, media.PEOPLE_CHECK = media.PEOPLE_CHECK, False   # the word filter alone (offline)
        try:
            self.assertEqual(sorted(media.people(short)), ["Jonathan Kuminga", "Rudy Gobert"])
        finally:
            media.PEOPLE_CHECK = old_check
        self.assertTrue(media.NOT_NBA_LEVEL.search("Women's basketball game Stanford vs UConn"))
        self.assertTrue(media.NOT_NBA_LEVEL.search("Baloncesto femenino final"))
        self.assertFalse(media.NOT_NBA_LEVEL.search("Real Madrid vs Barcelona basketball Euroleague"))
        self.assertFalse(media.HOOPS_TAGS.search("coffee, cup, desk, microphone, interview"))
        cands = [{"kind": "photo", "page": "a"}, {"kind": "photo", "page": "b"}, {"kind": "video", "page": "c"}]
        self.assertEqual(media.rejected_photos(cands, {"ranking": [1, 3], "who": {"1": "P", "2": "X"}}), {"b"})
        self.assertEqual(media.rejected_photos(cands, {}), set())
        self.assertEqual(render.opening_picture([None, None, {"f": 1}, {"f": 2}], 4), [{"f": 1}, None, None, {"f": 2}])
        self.assertEqual(render.opening_picture([{"f": 0}, None], 2), [{"f": 0}, None])

    # 28. Google Trends only counts for the story's real people, and only basketball news
    def test_28_trends_and_threshold(self):
        import signals, editor
        topic = {"star_names": ["Tyler Kolek 3.1", "Jayson Tatum 6.0"]}
        self.assertFalse(signals.trend_matches(topic, {"query": "sarah jukaku", "news": ["Sarah Jukaku stuns fans"]}))
        self.assertFalse(signals.trend_matches(topic, {"query": "snowfall forecast", "news": ["Snow in Boston"]}))
        self.assertTrue(signals.trend_matches(topic, {"query": "jayson tatum", "news": []}))
        self.assertTrue(signals.trend_matches(topic, {"query": "celtics 76ers", "news": ["Tatum and the Celtics fall"]}))
        self.assertFalse(signals.trend_matches({"star_names": []}, {"query": "lineup", "news": []}))
        self.assertGreaterEqual(editor.MIN_SCORE, 60)

    # 29. Hooks the way the best openers are written; commentary required for monetization;
    #     an interview only counts when it is the right person
    def test_29_hook_craft_commentary_interview(self):
        import script, compliance, media
        weak = "Did Jonathan Kuminga just go off on Rudy Gobert again, and is this where it breaks in Minnesota?"
        strong = "Did Jonathan Kuminga just scream at Rudy Gobert on camera, mid-game?"
        self.assertIn("two questions", [f for f, _ in script.hook_flaws(weak)])
        self.assertEqual(script.hook_flaws(strong), [])
        self.assertIn("fog word", [f for f, _ in script.hook_flaws("Is the Celtics drama about to explode?")])
        self.assertGreater(script.nba_hook_score(strong)[1], script.nba_hook_score(weak)[1])
        background_only = [{"say": "Brown got traded to Philly this summer.", "role": "context", "stage": "setup"},
                           {"say": "So is it really no beef?", "role": "question", "stage": "exit"}]
        v, notes, _ = compliance.check_originality(background_only, [])
        self.assertEqual(v, compliance.REVIEW)
        with_take = background_only[:1] + [{"say": "I think the silence says more than any quote.",
                                            "role": "analysis", "stage": "payoff"}] + background_only[1:]
        self.assertEqual(compliance.check_originality(with_take, [])[0], compliance.PASS)
        self.assertIn("Somebody ELSE's interview", media.PICK_PROMPT)

    # 30. Flickr straight from the source: allowed licences only, the person named, big enough,
    #     no key = skipped (nothing changes), the same photo via Openverse counts once
    def test_30_flickr(self):
        import media, io, json as js
        self.assertEqual(media.flickr_id("https://www.flickr.com/photos/allproreels/53012345678/"), "53012345678")
        self.assertNotIn("1", media.FLICKR_LICENCES)          # NC never requested
        old_key = media.FLICKR_KEY
        media.FLICKR_KEY = ""
        self.assertEqual(media.flickr_photos("Jayson Tatum"), [])
        media.FLICKR_KEY = "test"
        reply = {"stat": "ok", "photos": {"photo": [
            {"id": "1", "owner": "o", "ownername": "All-Pro Reels", "title": "Jayson Tatum", "tags": "basketball celtics",
             "license": "5", "datetaken": "2025-03-01", "url_h": "u1", "width_h": "1067", "height_h": "1600"},
            {"id": "2", "owner": "o", "ownername": "x", "title": "Jayson Tatum", "tags": "nba", "license": "4",
             "datetaken": "2024-01-01", "url_l": "u2", "width_l": "683", "height_l": "1024"},
            {"id": "3", "owner": "o", "ownername": "x", "title": "Celtics game", "tags": "basketball", "license": "4",
             "datetaken": "2025-01-01", "url_h": "u3", "width_h": "1600", "height_h": "1067"}]}}
        orig = media.get
        media.get = lambda url, timeout=30: js.dumps(reply).encode()
        try:
            found = media.flickr_photos("Jayson Tatum")
        finally:
            media.get, media.FLICKR_KEY = orig, old_key
        self.assertEqual([f["page"] for f in found], ["https://www.flickr.com/photos/o/1/"])   # 2 too small, 3 not him
        self.assertEqual(found[0]["license"], "CC BY-SA 2.0")

    # 31. A running story: our earlier Shorts about the same people; the receipt must be said and
    #     sourced; the closing question loops back to the hook
    def test_31_history_receipt_loop(self):
        import script
        script.RECENT.clear()
        script.RECENT.extend([
            {"time": "2026-11-05T10:00", "headline": "Jaylen Brown doesn't expect to talk to Jayson Tatum", "hook": "h1", "spoken": "x"},
            {"time": "2026-11-07T10:00", "headline": "Austin Reaves savage reaction", "hook": "h2", "spoken": "x"},
            {"time": "2026-11-08T10:00", "headline": "Jayson Tatum injury update", "hook": "h3", "spoken": "x"}])
        try:
            hist = script.rivalry_history("Jayson Tatum won't give air to Jaylen Brown drama")
        finally:
            script.RECENT.clear()
        lines = hist.splitlines()
        self.assertIn("Jaylen Brown doesn't expect", lines[0])          # both people: first
        self.assertNotIn("Reaves", hist)
        beats = [{"say": "Giannis said \"He's not my coach.\" Then he left."}]
        src = [{"title": "t", "text": "Giannis said: He\u2019s not my coach. My coach is Erik Spoelstra."}]
        self.assertEqual(script.checked_receipt("He's not my coach", beats, src), "He's not my coach")
        self.assertEqual(script.checked_receipt("He is a fraud", beats, src), "")
        self.assertTrue(script.loops_back("Did Jaylen Brown just shrug off Jayson Tatum?",
                                          "Tuesday decides it. So who blinks first, Brown or Tatum?"))
        self.assertFalse(script.loops_back("Did Jaylen Brown just shrug off Jayson Tatum?", "So would you trade him?"))

    # 32. Reddit adds demand only: a topic without Reddit data scores exactly as before
    def test_32_reddit_adds_only(self):
        import signals, editor
        topic = {"star_names": ["Jayson Tatum 6.0"]}
        titles = ["Jayson Tatum on facing Brown: 'another game'"] + ["other post"] * 20 + ["Tatum highlights"]
        self.assertEqual(signals.reddit_heat(topic, titles), 6.0)
        self.assertEqual(signals.reddit_heat({"star_names": []}, titles), 0.0)
        base = {"drama": 7, "virality": 7, "youtube_heat": 2, "search_hits": 4, "google_trend": 0, "conflict": True}
        self.assertEqual(editor.short_score(base), editor.short_score({**base, "reddit": 0}))
        self.assertGreater(editor.short_score({**base, "reddit": 6}), editor.short_score(base))

    # 33. The receipt is found in the spoken words and gets its own big caption
    def test_33_receipt_caption(self):
        import render
        words = [{"word": w, "start": k * 0.3, "end": k * 0.3 + 0.25} for k, w in
                 enumerate("Then he said He's not my coach. Wow.".split())]
        marked, at = render.mark_receipt(words, "He's not my coach")
        self.assertAlmostEqual(at, 0.9)
        groups = render.phrase_groups(marked)
        self.assertIn(["He's", "not", "my", "coach."], [[w["word"] for w in g] for g in groups])
        self.assertEqual(render.mark_receipt(words, "")[1], None)

    # 34. Commons player categories (free, no key): the player's own category and his newest
    #     sub-categories are read; a namesake's category is ignored; licence and size rules stay
    def test_34_commons_category(self):
        import media, json as js
        def page(title, w=1200, h=1600, lic="CC BY-SA 4.0", desc="Boston Celtics basketball"):
            return {"title": title, "imageinfo": [{"mime": "image/jpeg", "width": w, "height": h, "thumburl": "u",
                    "descriptionurl": "https://commons.wikimedia.org/wiki/" + title,
                    "extmetadata": {"LicenseShortName": {"value": lic}, "Artist": {"value": "A"},
                                    "ImageDescription": {"value": desc}, "Categories": {"value": ""}}}]}
        cats = {"Category:Jayson Tatum (basketball)": ([], []),
                "Category:Jayson Tatum": ([page("File:JT dunk.jpg"), page("File:JT small.jpg", 500, 600),
                                           page("File:JT nc.jpg", lic="CC BY-NC 2.0")],
                                          ["Category:Jayson Tatum in 2019", "Category:Jayson Tatum in 2025"]),
                "Category:Jayson Tatum in 2025": ([page("File:Celtics 2025 02.jpg")], []),
                "Category:Jayson Tatum in 2019": ([page("File:Old.jpg")], [])}

        def fake_get(url, timeout=30):
            q = dict(__import__("urllib.parse").parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("generator") == "search":
                return js.dumps({}).encode()
            cat = q.get("gcmtitle") or q.get("cmtitle")
            files, subs = cats.get(cat, ([], []))
            if q.get("list") == "categorymembers":
                return js.dumps({"query": {"categorymembers": [{"title": c} for c in subs]}}).encode()
            return js.dumps({"query": {"pages": {str(i): f for i, f in enumerate(files)}}}).encode()
        orig, media.get = media.get, fake_get
        media._photo_cache.pop("Jayson Tatum", None)
        try:
            found = media.commons_photos("Jayson Tatum")
        finally:
            media.get = orig
            media._photo_cache.pop("Jayson Tatum", None)
        titles = sorted(f["title"] for f in found)
        # "JT dunk" has no name in its file name but is in his category; small and NC are refused
        self.assertEqual(titles, ["Celtics 2025 02.jpg", "JT dunk.jpg", "Old.jpg"])
        # a namesake's category (no basketball anywhere) is not used
        cats2 = {"Category:Robert Williams": ([page("File:RW speech.jpg", desc="Senator at a hearing")], [])}
        def fake2(url, timeout=30):
            q = dict(__import__("urllib.parse").parse.parse_qsl(url.split("?", 1)[1]))
            files, subs = cats2.get(q.get("gcmtitle") or q.get("cmtitle"), ([], []))
            if q.get("list") == "categorymembers":
                return js.dumps({"query": {"categorymembers": []}}).encode()
            return js.dumps({"query": {"pages": {str(i): f for i, f in enumerate(files)}}}).encode()
        media.get = fake2
        try:
            self.assertEqual(media.category_files("Robert Williams"), [])
        finally:
            media.get = orig

    # 35. Exactly 2 scripts per run, a held one included (no extra try: even Claude budget)
    def test_35_quota(self):
        import script
        r = lambda *flags: [{"ready": f} for f in flags]
        self.assertTrue(script.quota_reached(r(True, True), 2))
        self.assertTrue(script.quota_reached(r(False, True), 2))
        self.assertFalse(script.quota_reached(r(True), 2))
        self.assertFalse(script.quota_reached(r(False), 2))

    # 36. No spoken "subscribe": the question closes the Short (the end card asks on screen); a
    #     fact that contains the word stays; a beat that was only a call to action goes
    def test_36_no_spoken_cta(self):
        import script
        beats = [{"say": "He subscribed to that theory."}, {"say": "Subscribe for more."}, {"say": "So who's right?"}]
        script.add_cta(beats, "seed")
        self.assertEqual([b["say"] for b in beats], ["He subscribed to that theory.", "So who's right?"])
        beats = [{"say": "Context."}, {"say": "Subscribe for daily NBA drama. So who's right, Doc or Giannis?"}]
        script.add_cta(beats, "seed")
        self.assertEqual(beats[-1]["say"], "So who's right, Doc or Giannis?")
        beats = [{"say": "So who's right? Hit subscribe for more."}]
        script.add_cta(beats, "seed")
        self.assertEqual(beats[-1]["say"], "So who's right?")
        self.assertIn("STRATEGY FIRST", script.PROMPT)
        self.assertIn("CRITICAL EDITOR", script.HUMANIZE)

    # 37. Quotes: a reworded quote is CORRECTED to the source's exact words (it stays the
    #     player's words, never the narrator's); narration is never pulled into it; an invented
    #     quote is still caught; the receipt follows the same balance
    def test_37_quote_balance(self):
        import script
        src = [{"title": "t", "summary": "", "text": "Asked about Rivers, Giannis said: He is not my coach. "
                                                     "My coach is Erik Spoelstra, and we are 4 and 6. Then he left."}]
        exact = "He is not my coach. My coach is Erik Spoelstra, and we are 4 and 6."
        for written in ["He's not my coach. My coach is Erik Spoelstra, and we are 4 and 6.",
                        "Rivers is not my coach, Spoelstra is my coach, and we are 4 and 6."]:
            b = [{"say": f'Giannis said "{written}"'}]
            script.soften_quotes(b, src)
            self.assertEqual(b[0]["say"], f'Giannis said "{exact}"')
            self.assertEqual(script.quote_check(b[0]["say"], src), [])
        src2 = [{"title": "t", "text": "Brown told reporters there is no beef but it might be a little lamb chop "
                                       "and some gravy. He should stay ready."}]
        b = [{"say": 'Brown said "there\'s no beef, but maybe a little lamb chop and gravy."'}]
        script.soften_quotes(b, src2)
        self.assertEqual(b[0]["say"], 'Brown said "there is no beef but it might be a little lamb chop and some gravy."')
        b = [{"say": 'Giannis said "Doc Rivers ruined my whole career forever."'}]
        script.soften_quotes(b, src)
        self.assertTrue(script.quote_check(b[0]["say"], src))             # invented: still flagged
        self.assertEqual(script.checked_receipt("4 and 6", [{"say": "Miami sits 4 and 6 now."}], src), "4 and 6")
        self.assertEqual(script.checked_receipt("4 and 9", [{"say": "Miami sits 4 and 9 now."}], src), "")

    # 38. Fan reaction is balanced: any sign of a public reaction (or a measurably hot story) is
    #     enough; only a reaction with no sign anywhere is held. Hook, title and frame: one promise
    def test_38_social_proof_and_promise(self):
        import compliance, script
        quiet = [{"title": "Kolek says he misspoke", "text": "Kolek said he misspoke about Taylor Swift."}]
        loud = [{"title": "Swifties slam Kolek", "text": "Kolek drew a backlash online after his comments."}]
        line = "Fans are furious with Kolek."
        self.assertEqual(compliance.check_social_proof(line, quiet)[0], compliance.REVIEW)
        self.assertEqual(compliance.check_social_proof(line, loud)[0], compliance.PASS)
        self.assertEqual(compliance.check_social_proof(line, quiet, audience_hot=True)[0], compliance.PASS)
        self.assertEqual(compliance.check_social_proof("Kolek said he misspoke.", quiet)[0], compliance.PASS)
        self.assertTrue(script.one_promise("Did Tyler Kolek just call Taylor Swift a fake Knicks fan?",
                                           "Kolek vs Taylor Swift got PERSONAL", "KOLEK vs SWIFT"))
        self.assertFalse(script.one_promise("Did the Knicks just lose their best guard?",
                                            "Knicks in TROUBLE", "KOLEK vs SWIFT"))
        # the title COMPLEMENTS the frame (no shared word needed), both match the hook
        self.assertTrue(script.one_promise("Did Kevin Durant just demand a trade from Phoenix?",
                                           "Durant WANTS OUT of Phoenix", "TRADE DEMAND?"))
        self.assertEqual(compliance.check_social_proof("The people in charge are quiet.",
                                                       [{"title": "x", "text": "Nothing."}])[0], compliance.PASS)

    # 39. Story strategist: the headline gap, the controversy kind, a new angle for a running
    #     story, no generic ending, a reworded quote in the HOOK corrected too, and the silent
    #     agree/disagree line on the end screen (rotating, never spoken)
    def test_39_strategist(self):
        import script
        for p in ("headline_gap", "controversy", "What do you think?", "DIFFERENT angle"):
            self.assertIn(p, script.PROMPT)
        self.assertIn("headline_gap", script.HUMANIZE)
        self.assertEqual(script.stock_tics([{"say": "So who blinks first, Brown or Tatum?"}]), [])
        self.assertIn("what do you think?", script.stock_tics([{"say": "Wild night. What do you think?"}]))
        old = list(script.RECENT)
        try:
            script.RECENT[:] = [{"time": "2026-11-01T10:00", "headline": "Kuminga rips Gobert after loss",
                                 "hook": "Did Jonathan Kuminga just call out Rudy Gobert?",
                                 "angle": "pressure on Kuminga's contract", "spoken": "x"}]
            note = script.rivalry_history("Rudy Gobert fires back at Jonathan Kuminga")
            self.assertIn("our angle: pressure on Kuminga's contract", note)
        finally:
            script.RECENT[:] = old
        src = [{"title": "t", "text": "Asked about Rivers, Giannis said: He is not my coach. "
                                      "My coach is Erik Spoelstra. Then he left."}]
        h = {"say": 'Did Giannis just say "Rivers is not my coach, Spoelstra is my coach" on camera?'}
        script.soften_quotes([h], src)
        self.assertIn('"He is not my coach. My coach is Erik Spoelstra."', h["say"])
        try:
            import render
        except ImportError as e:
            self.skipTest(f"render needs {e.name}")
        lines = {render.engage_line(f"story {k}") for k in range(40)}
        self.assertGreater(len(lines), 1)                                  # the wording rotates
        self.assertEqual(render.engage_line("same"), render.engage_line("same"))
        img = render.cta_card("#FACC15", "Kuminga vs Gobert")
        self.assertEqual(img.size, (render.W, render.H))


    # 40. Visual fixes after the Cousins/Luka run: the accented Commons category is found, two
    #     photos of one scene count as one only among EQUALLY relevant picks (relevance order
    #     never changes), the credit moves to the description (licence link + changes note)
    def test_40_visual_fixes(self):
        import json, media
        old_get = media.get
        calls = []

        def fake(url, timeout=30):
            calls.append(url)
            if "list=search" in url:
                return json.dumps({"query": {"search": [{"title": "Category:Luka Dončić"},
                                                        {"title": "Category:Luka Dončić (disambiguation)"},
                                                        {"title": "Category:Luka Dončić in 2024"}]}}).encode()
            if "Don%C4%8Di%C4%87" in url and "generator=categorymembers" in url:
                return json.dumps({"query": {"pages": {"1": {"title": "File:Luka Dončić Lakers.jpg",
                                  "imageinfo": [{"mime": "image/jpeg", "extmetadata": {
                                      "ImageDescription": {"value": "Luka Dončić, basketball"}}}]}}}}).encode()
            return json.dumps({"query": {}}).encode()
        try:
            media.get = fake
            self.assertEqual(media.category_titles("Luka Doncic"), ["Category:Luka Dončić"])
            calls.clear()
            files = media.category_files("Luka Doncic")
            self.assertEqual([f["title"] for f in files], ["File:Luka Dončić Lakers.jpg"])
            # the plain spelling is still tried first (unchanged path)
            self.assertIn("Category%3ALuka+Doncic+%28basketball%29", calls[0])
        finally:
            media.get = old_get
        self.assertEqual(media.shot_date("2019-06-10 19:38:23"), "2019-06-10")
        self.assertEqual(media.shot_date("<time>2019:06:10</time>"), "2019-06-10")
        self.assertEqual(media.shot_date("June 2019"), "")
        a = {"kind": "photo", "author": "Chensiyuan", "date": "2019-06-10", "hoops": True}
        b = {"kind": "photo", "author": "Chensiyuan", "date": "2019-06-10", "hoops": True}
        c = {"kind": "photo", "author": "Erik Drost", "date": "2021-01-02", "hoops": True}
        d = {"kind": "photo", "author": "Embassy", "date": "", "hoops": False}
        clip = {"kind": "video"}
        cands = [a, b, c, d, clip]
        tier = lambda j: {0: 3, 1: 3, 2: 3, 3: 3, 4: 1}[j]
        scenes = {media.scene_of(a)}
        # equal relevance: the new scene goes first
        self.assertEqual(media.fresh_first([1, 2], cands, tier, {1: 8, 2: 8}, scenes), [2, 1])
        # a MORE relevant photo of the same scene still wins: relevance is never overruled
        self.assertEqual(media.fresh_first([1, 2], cands, tier, {1: 9, 2: 8}, scenes), [1, 2])
        # the hook prefers a basketball photo among equals, not over a better one
        self.assertEqual(media.fresh_first([3, 2], cands, tier, {3: 8, 2: 8}, set(), hook=True), [2, 3])
        self.assertEqual(media.fresh_first([3, 2], cands, tier, {3: 9, 2: 8}, set(), hook=True), [3, 2])
        self.assertEqual(media.fresh_first([3, 4], cands, tier, {3: 8, 4: 8}, scenes), [3, 4])
        self.assertIsNone(media.scene_of(d))
        text = media.credits([{"kind": "photo", "author": "Erik Drost", "license": "CC BY 2.0",
                               "license_url": "https://creativecommons.org/licenses/by/2.0/",
                               "source": "Openverse", "page": "https://x/1"}])
        self.assertIn("CC BY 2.0 (https://creativecommons.org/licenses/by/2.0/)", text)
        self.assertIn(media.CHANGES_NOTE, text)
        self.assertNotIn(media.CHANGES_NOTE, media.credits([]))

    # 41. The gate honours the script stage's hold; the closing question may name the hook's
    #     people again (the loop); "nothing beyond the headline" is held; "per X" is noted
    def test_41_editorial_hold(self):
        import gate, compliance, script
        self.assertEqual(gate.check_editorial({"ready": True})[0], compliance.PASS)
        self.assertEqual(gate.check_editorial({})[0], compliance.PASS)
        v, notes = gate.check_editorial({"ready": False, "retention": {"hard": ["beat 3 repeats what was already said"]}})
        self.assertEqual(v, compliance.REVIEW)
        self.assertIn("beat 3 repeats what was already said", notes)
        beats = [{"say": "Cousins picked a Laker, and it was not Luka.", "stage": "setup"},
                 {"say": "Luka leads the league at 40 points a game.", "stage": "conflict"},
                 {"say": "So who's your favorite Laker, Luka or Cousins' pick?", "stage": "exit"}]
        self.assertEqual(script.retention_check(beats)["hard"], [])
        beats[2]["say"] = "Luka leads the league at 40 points a game. So who's right?"
        self.assertTrue(any("repeats" in h for h in script.retention_check(beats)["hard"]))
        self.assertTrue(script.NO_DEPTH.match("Nothing beyond the headline on what Cousins said."))
        self.assertFalse(script.NO_DEPTH.match("Atlanta drafted him third and traded him."))
        self.assertEqual(script.SPOKEN_PER.findall('He said "me," per Yahoo Sports.'), ["per Yahoo"])
        self.assertEqual(script.SPOKEN_PER.findall("He scored 30 per game."), [])
        try:
            import render
        except ImportError as e:
            self.skipTest(f"render needs {e.name}")
        self.assertFalse(render.SHOW_CREDIT)
        x = render.overlay(None, "", "#FACC15", credit="Photo: Erik Drost / CC BY 2.0")
        y = render.overlay(None, "", "#FACC15", credit="")
        self.assertEqual(x.tobytes(), y.tobytes())


    # 42. The Draymond run: "Only Has" / "World Reacts" were taken for people and found a doll,
    #     a beach photo and an arch. Only Wikipedia-confirmed sports people are searched, an
    #     unjudged photo needs the FULL name in its title, and the gate holds anything else.
    def test_42_only_real_people(self):
        import json, media, gate, compliance
        old_get, old_cache, old_check = media.get, dict(media._person_cache), media.PEOPLE_CHECK

        def fake(url, timeout=30):
            return json.dumps({"query": {
                "redirects": [{"from": "Luka Doncic", "to": "Luka Dončić"}],
                "pages": {"1": {"title": "Draymond Green", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1990)"}},
                          "2": {"title": "Luka Dončić", "pageprops": {"wikibase-shortdesc": "Slovenian basketball player"}},
                          "3": {"title": "Sam Amick", "pageprops": {"wikibase-shortdesc": "American sports journalist"}},
                          "-1": {"title": "Only Has", "missing": ""},
                          "-2": {"title": "World Reacts", "missing": ""},
                          "4": {"title": "Taylor Swift", "pageprops": {"wikibase-shortdesc": "American singer-songwriter"}}}}}).encode()
        try:
            media.get, media.PEOPLE_CHECK = fake, True
            media._person_cache.clear()
            got = media.real_people(["Draymond Green", "Only Has", "World Reacts", "Luka Doncic", "Sam Amick", "Taylor Swift"])
            self.assertEqual(got, ["Draymond Green", "Luka Doncic", "Sam Amick"])
            short = {"headline": "“He Only Has Value in Golden State” – NBA World Reacts as Insider Drops "
                                 "Bombshell Draymond Green Trade Report", "beats": [{"say": "Sam Amick says the Warriors will listen."}]}
            self.assertNotIn("Only Has", media.people(short))
            self.assertIn("Draymond Green", media.people(short))

            def down(url, timeout=30):
                raise OSError("offline")
            media.get = down
            media._person_cache.clear()
            self.assertIsNone(media.real_people(["Draymond Green"]))      # unreachable: old behaviour
        finally:
            media.get, media.PEOPLE_CHECK = old_get, old_check
            media._person_cache.clear()
            media._person_cache.update(old_cache)
        self.assertFalse(media.solo_title({"title": "St. Louis Only Has One Arch"}, "Draymond Green"))
        self.assertFalse(media.solo_title({"title": "File:Green field in spring.jpg"}, "Draymond Green"))
        self.assertTrue(media.solo_title({"title": "File:Draymond Green (33053301711).jpg"}, "Draymond Green"))
        self.assertTrue(media.solo_title({"title": "File:Luka Dončić 2024.jpg"}, "Luka Doncic"))
        items = [{"kind": "photo", "title": "Draymond Green 2016.jpg", "match": 8, "license": "CC BY 2.0",
                  "author": "A", "page": "p1",
                  "alts": [{"kind": "photo", "title": "SHE ONLY HAS EYES FOR ME..", "match": None,
                            "license": "CC BY 2.0", "author": "B", "page": "p2"}]},
                 {"kind": "photo", "title": "File:Draymond Green (cropped).jpg", "match": None,
                  "license": "CC BY-SA 2.0", "author": "C", "page": "p3"}]
        v, notes = gate.check_visuals(items, {"people": ["Draymond Green", "Sam Amick"]})
        self.assertEqual(v, compliance.REVIEW)
        self.assertEqual(len(notes), 1)
        self.assertIn("SHE ONLY HAS EYES", notes[0])
        items[0]["alts"] = []
        self.assertEqual(gate.check_visuals(items, {"people": ["Draymond Green"]})[0], compliance.PASS)
        self.assertEqual(gate.check_visuals(items, {})[0], compliance.PASS)       # older runs: unchanged


    # 43. Official results (balldontlie) only ever CONFIRM: a score or a record whose every number
    #     matches; a claim with any unchecked number (player points) stays as it was; no key or a
    #     dead API changes nothing. YuNet finds faces, and the old detector takes over without it.
    def test_43_official_results_and_faces(self):
        import datetime as dt, nbadata, compliance
        lakers = {"id": 14, "name": "Lakers", "conference": "West"}
        hawks = {"id": 1, "name": "Hawks", "conference": "East"}
        pistons = {"id": 9, "name": "Pistons", "conference": "East"}
        g1 = {"date": "2026-11-09", "status": "Final", "home_team": hawks, "visitor_team": lakers,
              "home_team_score": 114, "visitor_team_score": 124, "postseason": False}
        g2 = {"date": "2026-11-08", "status": "Final", "home_team": lakers, "visitor_team": pistons,
              "home_team_score": 120, "visitor_team_score": 101, "postseason": False}
        calls = []

        def fake(path, params):
            calls.append(path)
            if path == "teams":
                return {"data": [lakers, hawks, pistons, {"id": 99, "name": "Old Team", "conference": ""}]}
            if "team_ids[]" in params:
                return {"data": [g1, g2]}
            return {"data": [g1, g2]}
        old = (nbadata._get, nbadata.KEY, dict(nbadata._cache))
        try:
            nbadata._get, nbadata.KEY = fake, "test"
            nbadata._cache.clear()
            today = dt.date(2026, 11, 10)
            self.assertIn("Lakers 124-114 Hawks", nbadata.confirm("The Lakers beat the Hawks 124 to 114.", today))
            self.assertIn("Lakers 2-0", nbadata.confirm("The Lakers are 2-0.", today))
            self.assertEqual(nbadata.confirm("The Lakers are 10-2.", today), "")              # wrong record
            self.assertEqual(nbadata.confirm("The Lakers beat the Hawks 125 to 114.", today), "")
            self.assertEqual(nbadata.confirm("Doncic had 32 points in the 124 to 114 win over the Hawks.", today), "")
            self.assertEqual(nbadata.confirm("Doncic is the best player in the league.", today), "")
            claims = [{"text": "The Lakers beat the Hawks 124 to 114.", "status": "REPORTED", "source": 1},
                      {"text": "Doncic had 32 points.", "status": "REPORTED", "source": 1}]
            self.assertEqual(nbadata.annotate(claims, today), 1)
            src = [{"title": "t", "text": "x", "tier": 1, "publisher": "Yahoo Sports"}]
            _, notes, out = compliance.check_claims(claims, src, "The Lakers beat the Hawks, per Yahoo.")
            self.assertEqual([c["status"] for c in out], ["CONFIRMED", "REPORTED"])

            def down(path, params):
                raise OSError("offline")
            nbadata._get = down
            nbadata._cache.clear()
            claims2 = [{"text": "The Lakers beat the Hawks 124 to 114.", "status": "REPORTED", "source": 1}]
            self.assertEqual(nbadata.annotate(claims2, today), 0)
            self.assertNotIn("official_result", claims2[0])
            nbadata.KEY = ""
            self.assertEqual(nbadata.annotate([{"text": "The Lakers are 2-0."}], today), 0)
        finally:
            nbadata._get, nbadata.KEY = old[0], old[1]
            nbadata._cache.clear()
            nbadata._cache.update(old[2])
        try:
            import cv2, numpy as np, render
        except ImportError as e:
            self.skipTest(f"render needs {e.name}")
        self.assertTrue(render.YUNET.exists())
        blank = np.zeros((400, 300, 3), dtype=np.uint8)
        self.assertEqual(render.yunet_faces(cv2, blank, 30), [])
        render._yunet.clear()
        old_model = render.YUNET
        try:
            render.YUNET = render.ROOT / "missing.onnx"
            self.assertIsNone(render.yunet_faces(cv2, blank, 30))          # -> the Haar detector
        finally:
            render.YUNET = old_model
            render._yunet.clear()


    # 44. Voice: a season is read as a season ("2020-21" was spoken "2020 to 21"), scores and
    #     records keep their old readings
    def test_44_speakable_seasons(self):
        try:
            import tts
        except ImportError as e:
            self.skipTest(f"tts needs {e.name}")
        self.assertEqual(tts.speakable("his most since 2020-21."), "his most since 2020 21.")
        self.assertEqual(tts.speakable("the 1999-00 season"), "the 1999 2000 season")
        self.assertEqual(tts.speakable("Lakers won 124-114"), "Lakers won 124 to 114")
        self.assertEqual(tts.speakable("a 10-2 record"), "a 10 and 2 record")
        self.assertEqual(tts.speakable("52-24-8 shooting"), "52, 24, 8 shooting")


if __name__ == "__main__":
    unittest.main(verbosity=2)

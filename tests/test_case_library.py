"""Stage 2 of the class-fix plan (his answers 2026-11-18): a CASE LIBRARY per failure class
(FAILURE_CLASSES.md). Every case is a real picture from a kept run or the eval, labelled by Claude
only where the answer is clear under the agreed rules, with its source and the reason. The library
runs offline on a one-time career snapshot (tests/cases/careers.json) and blocks main: one failing
case = the pre-push hook refuses the push (his answer "a failing case blocks main").

  P1 who is in the picture   tests/cases/p1_who.json      (the pick: D71; the top-ups: D50, D63, D72;
                                                         titles and names with a suffix: D73)
  P2 which uniform / era     tests/cases/p2_uniform.json  (team_fits: D30, D38, D42, D59, D60, D61)
  D96 ambiguous words by meaning (his rule 2026-11-25), the real cases of each module, with the
  judgement recorded as Claude gave or would give it ("judged" / "signs" / "attributed"; absent =
  no answer, the agreed safe side):
  E1 story choice            tests/cases/e1_choice.json   (modules 4-5: collect, editor, signals)
  F1 fact fidelity           tests/cases/f1_facts.json    (module 6 parts 1-2: articles, Short, titles)
  P1 / P2 words              tests/cases/d96_p_words.json (module 2 speech verbs, module 3 now/today)
  S1 story build (style)     tests/cases/s1_style.json    (module 6 part 3: hook clash / fog, payoff "so")

Adding a case: a real one, clear under a rule he agreed, with "source" and "why". A case that today's
code gets wrong is NOT added as an expected failure: it is fixed first (his answer "first fix, then
the library"), each fix with his yes."""
import io
import json
import shutil
import sys
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

import no_real_claude  # noqa: F401,E402  D98: the tests never call the real Claude (first)
import no_network  # noqa: F401,E402  D99: the tests never reach the network (right after D98)
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CASES = ROOT / "tests" / "cases"


LIBRARIES = ("p1_who.json", "p2_uniform.json", "e1_choice.json", "f1_facts.json", "d96_p_words.json", "s1_style.json")


def load(name):
    return json.loads((CASES / name).read_text(encoding="utf-8"))


class Snapshot:
    """Installs the career snapshot into media's caches; no network at all."""

    CACHES = ("_wikidata", "_wiki_title", "_teams", "_team_since", "_nba_debut", "_nba_debut_day",
              "_career", "_spells", "_coached", "_college", "_commons_cat")

    def __enter__(self):
        import media
        self.m = media
        self.saved = {k: dict(getattr(media, k)) for k in self.CACHES}
        for k in self.CACHES:
            getattr(media, k).clear()
        for person, c in load("careers.json")["people"].items():
            q = c["wikidata"]
            media._wikidata[person] = q
            media._wiki_title[person] = c["wiki_title"]
            media._teams[q] = (c["current"], set(c["former"]))
            if c["since"]:
                media._team_since[q] = c["since"]
            if c["debut"]:
                media._nba_debut[q] = c["debut"]
            media._career[q] = set(c["career"])
            media._spells[q] = [tuple(s) for s in c["spells"]]
            media._coached[q] = set(c["coached"])
            media._college[q] = list(c["college"])
        self.net = patch.object(media, "get", side_effect=RuntimeError("the case library is offline"))
        self.net.start()
        self.unknown = set(media._career_unknown)
        media._career_unknown.clear()
        return media

    def __exit__(self, *exc):
        self.net.stop()
        for k, v in self.saved.items():
            getattr(self.m, k).clear()
            getattr(self.m, k).update(v)
        self.m._career_unknown.clear()
        self.m._career_unknown.update(self.unknown)


@contextmanager
def lookup_failed(m, case):
    """D92: the case's "career_unknown" men had a career lookup that did not answer in the run
    (no Wikidata item known, marked unknown), exactly as media leaves them after a failed request."""
    names = case.get("career_unknown", [])
    gone = {n: m._wikidata.pop(n) for n in names if n in m._wikidata}
    m._career_unknown.update(names)
    try:
        yield
    finally:
        m._career_unknown.difference_update(names)
        m._wikidata.update(gone)


class LibraryShape(unittest.TestCase):
    def test_every_case_has_its_source_and_reason(self):
        for name in LIBRARIES:
            ids = set()
            for c in load(name):
                self.assertTrue(c.get("source") and c.get("why"), c.get("id"))
                self.assertNotIn(c["id"], ids)
                ids.add(c["id"])

    def test_both_answers_are_in_the_library(self):
        # a library of only "refused" (or only "allowed") cases would let a rule that refuses (or
        # allows) everything pass
        for name in LIBRARIES:
            exp = {c["expect"] for c in load(name) if "expect" in c}
            self.assertEqual(exp, {True, False}, name)


class P2UniformLibrary(unittest.TestCase):
    def test_cases(self):
        with Snapshot() as m:
            for c in load("p2_uniform.json"):
                with self.subTest(c["id"], line=c["line"], jersey=c["photo"]["tag"].get("t")):
                    photo = {"kind": "photo", **c["photo"]}
                    self.assertEqual(m.team_fits(photo, c["line"], c["person"], [c["person"]]), c["expect"], c["why"])


class P1WhoLibrary(unittest.TestCase):
    def test_pick_cases(self):
        with Snapshot() as m:
            for c in [c for c in load("p1_who.json") if c["kind"] == "pick"]:
                with self.subTest(c["id"], on_screen=c["on_screen"], photo=c["photo"]["title"]):
                    photo = {"kind": "photo", **c["photo"]}
                    # D94: the pick asks line_lock (speaker, outsider, else D71's note); Wikipedia's
                    # "outside sport" answer is the case's own list (offline)
                    with lookup_failed(m, c), patch.object(m, "outside_person", lambda n, c=c: n in c.get("outside", [])):
                        mode, men = m.line_lock(c["line"], c["on_screen"], c["who"])
                        self.assertEqual(m.lock_allows(photo, mode, men, c["who"], c["on_screen"]), c["expect"], c["why"])

    def test_title_cases(self):
        # D73: a title counts as a suffixed man's only with the same suffix, both where an unjudged
        # photo is taken by its title (solo_title) and where the jersey law trusts a title (his_own)
        with Snapshot() as m:
            for c in [c for c in load("p1_who.json") if c["kind"] == "title"]:
                with self.subTest(c["id"], person=c["person"], title=c["title"]):
                    self.assertEqual(m.solo_title({"title": c["title"]}, c["person"]), c["expect"], c["why"])
                    self.assertEqual(m.his_own(c["person"], {"title": c["title"]}), c["expect"], c["why"])

    def test_gate_agrees_on_titles(self):
        # D73: the gate re-checks an unjudged photo's title (full_name_in); it must give the
        # media stage's answer, or a photo the media stage took would be held (D71's lesson)
        import gate, media
        self.assertEqual(gate.SUFFIXES, media.SUFFIXES)
        for c in [c for c in load("p1_who.json") if c["kind"] == "title"]:
            with self.subTest(c["id"], person=c["person"], title=c["title"]):
                self.assertEqual(gate.full_name_in(c["title"], c["person"]), c["expect"], c["why"])

    def test_name_cases(self):
        with Snapshot() as m:
            for c in [c for c in load("p1_who.json") if c["kind"] == "name"]:
                with self.subTest(c["id"], text=c["text"]):
                    got = m.people_names(c["text"])
                    for n in c["names"]:
                        self.assertIn(n, got, c["why"])
                    for n in c["not_names"]:
                        self.assertNotIn(n, got, c["why"])

    def test_top_up_cases(self):
        folder = ROOT / "data" / "_test_case_library"
        with Snapshot() as m:
            try:
                for c in [c for c in load("p1_who.json") if c["kind"] == "top-up"]:
                    with self.subTest(c["id"], line=c["line"]):
                        pools = {p: [{"kind": "photo", "title": f"{p} 2026.jpg", "page": "p-" + p, "url": "u-" + p,
                                      "author": "a-" + p, "team": "", "hoops": True,
                                      "tag": {"v": "C", "s": "interview", "t": "speaks", "who": p}}]
                                 for p in c["who"] if p not in c.get("no_photo", [])}
                        with patch.multiple(m, spoken=lambda short, c=c: [{"say": c["line"], "on_screen": c["on_screen"]}],
                                            photos=lambda person, pools=pools: list(pools.get(person, [])),
                                            download=lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1],
                                            image_ok=lambda path: True, picture_hash=lambda path: None,
                                            beat_seconds=lambda short, i: 2.0,
                                            college_faces=lambda person, shown: [], national_faces=lambda person, shown: []):
                            with redirect_stdout(io.StringIO()), lookup_failed(m, c), \
                                    patch.object(m, "outside_person", lambda n, c=c: n in c.get("outside", [])):
                                got = m.fill_empty([None], 1, folder, set(), c["who"], {"_name": "t", "beats": [{}]})[0]
                        # D92: no expected person = the line must stay without another man's photo
                        want = f"{c['expect_person']} 2026.jpg" if c["expect_person"] else None
                        self.assertEqual((got or {}).get("title"), want, c["why"])
            finally:
                shutil.rmtree(folder, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


class D96MeaningLibrary(unittest.TestCase):
    """D96 (his rule 2026-11-25): each module's real cases; both answers present per file."""

    def test_e1_story_choice(self):
        import collect
        import editor
        import signals
        for c in load("e1_choice.json"):
            with self.subTest(c["id"], title=c["title"]):
                j, k = c.get("judged"), c["kind"]
                if k == "speculation":
                    item = {"title": c["title"], **({"speculative": j} if j is not None else {})}
                    got = collect.spec_title(item)
                elif k == "league":
                    it = {"title": c["title"], "tier": 1, "publisher": "x", "_ask_league": True}
                    if collect.OTHER_LEAGUE.search(c["title"]):
                        got = False                               # normalize drops it before any question
                    else:
                        got = bool(collect.judge_titles([it], ask=lambda p, j=j: '{"yes": [1]}' if j else '{"yes": []}'))
                elif k == "turn":
                    got = editor.major_turn(c["title"], j)
                elif k == "opinion":
                    got = bool(editor.OPINION.search(c["title"]))
                elif k == "benchmark_drama":
                    import benchmark
                    benchmark._judged.clear()
                    if j is not None:
                        benchmark._judged[("DRAMA", c["title"])] = j
                    got = benchmark.drama(c["title"])
                    benchmark._judged.clear()
                else:
                    signals._judged.clear()
                    key = "nba" if k == "trend" else "story"
                    if j is not None:
                        signals._judged[(key, c["title"])] = j
                    got = signals.nba_text(c["title"]) if k == "trend" else signals.story_phrase(c["title"])
                    signals._judged.clear()
                self.assertEqual(got, c["expect"], c["why"])

    def test_f1_facts(self):
        import compliance as C
        for c in load("f1_facts.json"):
            with self.subTest(c["id"], text=c["text"][:60]):
                k, signs, judged = c["kind"], c.get("signs"), c.get("judged")
                src = [{"title": "", "summary": "", "text": c["text"], "tier": 1, "publisher": "x"}]
                if k == "official":
                    got = C.original_reporters(src, signs)["official"]
                elif k == "reaction":
                    got = C.check_social_proof("Fans are furious about it.", src, False, signs)[0] == C.PASS
                elif k == "response_articles":
                    got = C.response_in_articles(c["text"], signs)
                elif k == "silence":
                    got = C.silence_told(c["text"], judged)
                elif k == "turn_articles":
                    got = bool(C.missed_turn("Bron and the critics stopped talking.", src, {}, signs))
                else:
                    got = C.title_hedged(c["text"], [c["text"]] if c.get("attributed") else ())
                self.assertEqual(got, c["expect"], c["why"])

    def test_p_words(self):
        import media
        import photo_tags
        saved = media._TIME_LINES[0]
        try:
            for c in [c for c in load("d96_p_words.json") if c["kind"] == "pre_nba"]:
                with self.subTest(c["id"], title=c["title"]), Snapshot() as m:
                    photo = {"kind": "photo", "title": c["title"], "page": c["title"],
                             **m.team_marks(c["person"], c["title"])}
                    photo_tags._apply(photo, c["tag"])
                    got = photo.get("team") == "pre-nba" or m.college_photo(photo, c["person"])
                    self.assertEqual(got, c["expect"], c["why"])
            for c in [c for c in load("d96_p_words.json") if c["kind"] != "pre_nba"]:
                with self.subTest(c["id"], line=c["line"]):
                    if c["kind"] == "speech":
                        got = media.is_speech_line(c["line"], [c["line"]] if c.get("judged") else [])
                    else:
                        tl = c.get("time_lines")
                        media._TIME_LINES[0] = None if tl is None else set(tl)
                        got = media.names_a_time(c["line"], "")
                    self.assertEqual(got, c["expect"], c["why"])
        finally:
            media._TIME_LINES[0] = saved

    def test_s1_style(self):
        import script
        saved = dict(script._style_seen)
        try:
            for c in load("s1_style.json"):
                with self.subTest(c["id"], text=c["text"][:60]):
                    script._style_seen.clear()
                    key = {"fog": "FOG", "reason": "REASON", "clash": "CLASH"}[c["kind"]]
                    if "judged" in c:
                        script._style_seen[(key, c["text"])] = c["judged"]
                    if c["kind"] == "fog":
                        got = any(f == "fog word" for f, _ in script.hook_flaws(c["text"]))
                    elif c["kind"] == "reason":
                        got = script.gives_reason(c["text"])
                    else:
                        got = script.clash_count(c["text"])
                    self.assertEqual(got, c["expect"], c["why"])
        finally:
            script._style_seen.clear()
            script._style_seen.update(saved)

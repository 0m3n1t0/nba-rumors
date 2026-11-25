"""Stage 2 of the class-fix plan (his answers 2026-11-18): a CASE LIBRARY per failure class
(FAILURE_CLASSES.md). Every case is a real picture from a kept run or the eval, labelled by Claude
only where the answer is clear under the agreed rules, with its source and the reason. The library
runs offline on a one-time career snapshot (tests/cases/careers.json) and blocks main: one failing
case = the pre-push hook refuses the push (his answer "a failing case blocks main").

  P1 who is in the picture   tests/cases/p1_who.json      (the pick: D71; the top-ups: D50, D63, D72;
                                                         titles and names with a suffix: D73)
  P2 which uniform / era     tests/cases/p2_uniform.json  (team_fits: D30, D38, D42, D59, D60, D61)

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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CASES = ROOT / "tests" / "cases"


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
        for name in ("p1_who.json", "p2_uniform.json"):
            ids = set()
            for c in load(name):
                self.assertTrue(c.get("source") and c.get("why"), c.get("id"))
                self.assertNotIn(c["id"], ids)
                ids.add(c["id"])

    def test_both_answers_are_in_the_library(self):
        # a library of only "refused" (or only "allowed") cases would let a rule that refuses (or
        # allows) everything pass
        for name in ("p1_who.json", "p2_uniform.json"):
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

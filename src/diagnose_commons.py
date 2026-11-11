"""Diagnosis only (manual workflow diagnose.yml): what Wikipedia and Commons say about a few
players, and why the pipeline does or does not read their Commons category.

Read-only: no secrets, no Claude, no files changed. Claude's own session cannot reach
Wikimedia (a shared cloud IP is rate-limited), GitHub's runner can, so this runs there and
Claude reads the log.

  python src/diagnose_commons.py "Luka Doncic" "Devin Booker"
"""
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import media  # noqa: E402  (the production search code, unchanged)


def caption(f: dict) -> str:
    meta = ((f.get("imageinfo") or [{}])[0].get("extmetadata") or {})
    return f.get("title", "") + " | " + media.clean(meta.get("ImageDescription", {}).get("value", ""))[:90]


def members(cat: str) -> tuple[list[dict], list[str]]:
    q = {"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": cat,
         "gcmtype": "file", "gcmlimit": "50", "prop": "imageinfo", "iiprop": "mime|extmetadata"}
    files = list((json.loads(media.get(media.COMMONS + "?" + urllib.parse.urlencode(q)))
                  .get("query", {}).get("pages") or {}).values())
    q = {"action": "query", "format": "json", "list": "categorymembers", "cmtitle": cat,
         "cmtype": "subcat", "cmlimit": "50"}
    subs = [m["title"] for m in json.loads(media.get(media.COMMONS + "?" + urllib.parse.urlencode(q)))
            .get("query", {}).get("categorymembers", [])]
    return files, subs


def main() -> None:
    names = [n for n in sys.argv[1:] if n.strip()] or ["Luka Doncic", "Devin Booker"]
    real = media.real_people(names)
    print(f"Wikipedia check: {real}")
    for person in names:
        print(f"\n===== {person} =====")
        print(f"Wikipedia page: {media._wiki_title.get(person)!r}, born: {media._birth_year.get(person)!r}, "
              f"Wikidata: {media._wikidata.get(person)!r} -> Commons category {media.commons_category(person)!r}")
        last = media.fold(person).split()[-1]
        wiki = f"Category:{media._wiki_title[person]}" if media._wiki_title.get(person) else ""
        seen = []
        wd = media.commons_category(person)
        for cat in ([f"Category:{person} (basketball)", f"Category:{person}"] + [c for c in (wd, wiki) if c]
                    + media.category_titles(person)):
            if cat in seen:
                continue
            seen.append(cat)
            try:
                files, subs = members(cat)
            except Exception as exc:
                print(f"- {cat}: request failed: {exc}")
                continue
            own = [s for s in subs if last in media.fold(s)]
            old_pass = cat.endswith("(basketball)") or any(media.BASKETBALL.search(caption(f)) for f in files) \
                or any(media.BASKETBALL.search(s) for s in own)
            team = any(media.NBA_PROOF.search(media.fold(caption(f))) for f in files) \
                or any(media.NBA_PROOF.search(media.fold(s)) for s in own)
            print(f"- {cat}: {len(files)} files, {len(subs)} sub-categories ({len(own)} his)")
            if files or subs:
                print(f"    old rule (a caption says basketball): {'PASS' if old_pass else 'FAIL -> category dropped, search stopped'}")
                print(f"    new rule: {'his (Wikidata / Wikipedia name)' if cat in (wd, wiki) else ('PASS' if old_pass or team else 'skipped, search goes on')}")
                for f in files[:6]:
                    print(f"    file: {caption(f)}")
                for s in own[:6]:
                    print(f"    sub:  {s}")
        media.PHOTO_STATS.clear()
        got = media.category_files(person)
        print(f"RESULT with today's code: {len(got)} photos from the category "
              f"(files read: {media.PHOTO_STATS.get(person, {}).get('category', 0)})")


if __name__ == "__main__":
    main()

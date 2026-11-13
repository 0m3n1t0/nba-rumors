"""Replay today's checks on real past runs, before a change reaches main (the owner's rule,
2026-11-13: never undo an earlier fix, never let a solved problem come back).

    python src/replay.py <folder with run bundles>      e.g. the private nba/runs/

Every run bundle (state.py) holds the scripts, the pictures and, from 2026-11-13 on, the exact
source texts each Short was checked against (data/sources/). For every Short this prints what
today's code finds that the run itself did not, and what the run found that today's code no
longer finds. Run it before and after a change: the difference is what the change does to real
Shorts. Reads only; changes nothing. Offline: no Claude, no network.
"""

from __future__ import annotations

import json
import re
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import compliance as C  # noqa: E402
import media  # noqa: E402
import script  # noqa: E402


def members(bundle: Path) -> dict[str, bytes]:
    with tarfile.open(bundle, "r:gz") as tar:
        return {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}


def spoken_of(short: dict) -> str:
    hook = short.get("hook")
    hook = hook.get("text", "") if isinstance(hook, dict) else (hook or "")
    return " ".join([hook] + [b.get("say", "") for b in short.get("beats") or []])


def text_findings(short: dict, sources: list[dict] | None) -> set[str]:
    """What the text checks find today. Without the source texts only the checks that need none."""
    said = spoken_of(short)
    found = set()
    m = script.BROKEN_TEXT.search(said)
    if m:
        found.add(f"broken text: ...{said[max(0, m.start() - 15):m.end() + 15]}...")
    if sources is None:
        return found
    on_screen = " ".join(b.get("on_screen", "") for b in short.get("beats") or [])
    found |= {f"number not in the sources: {x}" for x in script.fact_check(f"{said} {on_screen}", sources)}
    bad = script.quote_check(said, sources)
    found |= {f"quote not in the sources: {q[:70]}" for q in bad}
    if not bad:
        found |= {f"quote not inside quote marks: {q[:70]}" for q in script.quotes_outside_marks(said, sources)}
    return found


def picture_findings(items: list, flags: dict) -> set[str]:
    found = set()
    careers = flags.get("careers") or {}
    for it in items:
        for x in ([it] + (it.get("alts") or []) if it else []):
            person = x.get("person") or ""
            if person and media.look_alike_name(person, x.get("title", "")):
                found.add(f"another man with his surname: {x.get('title', '')[:50]} (as {person})")
            jersey = x.get("jersey") or media.jersey_team(x.get("tag"))
            if not C.jersey_ok(jersey, careers.get(person, [])):
                found.add(f"{person} in a {jersey} jersey: {x.get('title', '')[:50]}")
    return found


def then_findings(short: dict) -> set[str]:
    """What the run itself recorded (its own checks then)."""
    found = {f"number not in the sources: {x}" for x in short.get("unsupported_numbers") or []}
    found |= {f"quote not in the sources: {q[:70]}" for q in short.get("unsupported_quotes") or []}
    return found


def replay(folder: Path) -> int:
    changed = 0
    for bundle in sorted(folder.glob("*.tar.gz")):
        files = members(bundle)
        for name in sorted(n for n in files if re.fullmatch(r"scripts/short_\d+\.json", n)):
            short = json.loads(files[name])
            key = Path(name).stem
            raw = files.get(f"sources/{key}.json")
            sources = json.loads(raw) if raw else None
            for s in sources or []:
                s.setdefault("title", "")
                s.setdefault("text", "")
                s["summary"] = s.get("summary") or ""
            items = json.loads(files.get(f"media/{key}.json", b"[]")) + json.loads(files.get(f"media/{key}_vs.json", b"[]"))
            flags = json.loads(files.get(f"media/{key}_flags.json", b"{}"))
            now = text_findings(short, sources) | picture_findings(items, flags)
            then = then_findings(short) if sources is not None else set()
            new, gone = sorted(now - then), sorted(then - now)
            label = f"{bundle.name[:-7]} {key} ({short.get('gate') or '-'}"
            label += ", sources kept)" if sources is not None else ", no sources kept: text checks limited)"
            if new or gone:
                changed += 1
                print(label)
                print("".join(f"   + today: {x}\n" for x in new) + "".join(f"   - no longer: {x}\n" for x in gone), end="")
            else:
                print(f"{label}: same")
    return changed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(f"\n{replay(Path(sys.argv[1]))} Short(s) where today's checks differ from the run's own")

"""D77 (his answers 2026-11-19): the smoke test after every code push.

One fixed, stored story (nba/smoke/ in the private state repository: a kept Short with a VS card,
its script and its chosen pictures) is made again WITHOUT Claude: voice, voice check, video, gate.
It proves the code still makes a whole Short after a change; the writing and the picture choice
are the unit tests' and the eval's job. It never saves anything back and never uploads.

    python src/smoke.py prepare   the story into data/, its pictures downloaded again, one fixed
                                  music track (the first of the music library, if it is there)
    python src/smoke.py check     a technical failure fails the run: no MP4, or the gate's
                                  technical check (size, length, sound, the voice heard) not PASS;
                                  the content checks (sources, licences, final read) do not count

A picture that cannot be downloaded fails the run too, and says it is the network, not the code
(his answer). Only the narration and the picture titles reach the public log, never the articles.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STORY = ROOT / "state" / "nba" / "smoke"
LIBRARY = ROOT / "music_library"
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".ogg")
FILES = {"script.json": ("scripts", "short_1.json"), "media.json": ("media", "short_1.json"),
         "media_vs.json": ("media", "short_1_vs.json")}


def pictures(media: list, vs: list) -> list[dict]:
    """Every picture the video uses: each beat's, its alternates and the VS card's."""
    out = []
    for it in list(media) + list(vs):
        for x in ([it] + list(it.get("alts") or [])) if it else []:
            if x and x.get("file") and x.get("url"):
                out.append(x)
    return out


def fixed_track() -> Path | None:
    """The music library's first track (moods and files in name order): the same one every time."""
    if not LIBRARY.is_dir():
        return None
    for mood in sorted(p for p in LIBRARY.iterdir() if p.is_dir()):
        files = sorted(f for f in mood.iterdir() if f.suffix.lower() in AUDIO_EXT)
        if files:
            return files[0]
    return None


def prepare(download=None) -> list[str]:
    """Puts the story back; returns the pictures that could not be downloaded (the network)."""
    if download is None:
        import media
        download = media.download
    for src, (sub, name) in FILES.items():
        (DATA / sub).mkdir(parents=True, exist_ok=True)
        if (STORY / src).exists():
            shutil.copy2(STORY / src, DATA / sub / name)
    load = lambda p: json.loads(p.read_text(encoding="utf-8")) if p.exists() else []   # noqa: E731
    failed = []
    for x in pictures(load(DATA / "media" / "short_1.json"), load(DATA / "media" / "short_1_vs.json")):
        path = ROOT / x["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() and not download(x["url"], path):
            failed.append(x.get("title") or x["url"])
    track = fixed_track()
    if track:
        dest = DATA / "media" / "short_1" / f"music{track.suffix.lower()}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(track, dest)
        try:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                        "-of", "csv=p=0", str(dest)], capture_output=True, text=True).stdout.strip())
        except (ValueError, OSError):
            dur = 0.0
        (DATA / "media" / "short_1_music.json").write_text(json.dumps(
            {"kind": "music", "title": track.stem, "duration": dur, "file": str(dest.relative_to(ROOT))}),
            encoding="utf-8")
    return failed


def check() -> list[str]:
    """The technical failures; [] when the Short was made whole."""
    problems = []
    if not (DATA / "video" / "short_1.mp4").exists():
        problems.append("no MP4 was made")
    try:
        gate = json.loads((DATA / "gate" / "short_1.json").read_text(encoding="utf-8"))
        tech = (gate.get("checks") or {}).get("technical_quality") or {}
        if tech.get("verdict") != "PASS":
            problems.append("technical check: " + ("; ".join(tech.get("notes") or []) or "not run"))
    except (OSError, ValueError):
        problems.append("the gate wrote no result")
    return problems


def main() -> int:
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "prepare":
        if not (STORY / "script.json").exists():
            print("[smoke] FAILED: the stored story is missing (state/nba/smoke/script.json)")
            return 1
        failed = prepare()
        if failed:
            print(f"[smoke] FAILED (the network, not the code): {len(failed)} picture(s) could not be "
                  f"downloaded: " + "; ".join(t[:60] for t in failed))
            return 1
        print("[smoke] story ready")
        return 0
    if what == "check":
        problems = check()
        if problems:
            print("[smoke] FAILED: " + " | ".join(problems))
            return 1
        print("[smoke] OK: the Short was made whole")
        return 0
    print("usage: python src/smoke.py prepare|check")
    return 2


if __name__ == "__main__":
    sys.exit(main())

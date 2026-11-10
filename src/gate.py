"""Stage 6: the publication gate. Every Short gets ONE decision, made in code:

  PASS    all mandatory checks pass: the only status that may ever be published automatically
  REVIEW  something important needs a person (held, never auto-published)
  REJECT  a critical problem (never published)

The 11 checks:
  1-5, 8-10  from the script stage (compliance.py): source verification, claim classification,
             factual accuracy, original storytelling, repetition, title accuracy, thumbnail
             accuracy, advertiser suitability
  6  visual asset licensing  every photo and clip: an accepted licence, an author, a source page;
                             no TV broadcast or NBA game footage
  7  music licensing         the track has a confirmed licence record (YouTube Audio Library
                             tracks: music_licenses.json in the private state repository) or an
                             accepted open licence
  11 technical quality       1080x1920, 10-60 s, a video and an audio stream, the voice passed
                             its own check

Writes data/gate/<short>.json and the verdict into the script JSON ("gate"), plus a table in
the run summary. Uploading (when it exists) reads ONLY "gate": "PASS".
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import compliance as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCRIPTS, MEDIA, VIDEO, GATE = DATA / "scripts", DATA / "media", DATA / "video", DATA / "gate"
AUDIO = DATA / "audio"
MIN_HEARD = 0.85   # same bar as tts.py: Whisper must hear this share of the words
MUSIC_LICENSES = DATA / "history" / "music_licenses.json"   # kept in the private state repository
LEDGER = DATA / "history" / "ledger"

ACCEPTED = re.compile(r"^(cc0|public domain|pd|cc by|cc-by|attribution|pixabay content license|"
                      r"public domain mark)", re.I)
REFUSED = re.compile(r"\b(nc|nd)\b|non-?commercial|no ?deriv", re.I)
BROADCAST = re.compile(r"\b(espn|tnt|abc|nbc|nba ?tv|bally|fanduel sports|broadcast|telecast|"
                       r"full game|game highlights|nba highlights|screen ?(recording|capture)|tv feed)\b", re.I)


def licence_accepted(lic: str) -> bool:
    lic = (lic or "").strip()
    return bool(lic) and not REFUSED.search(lic) and bool(ACCEPTED.search(lic))


def check_visuals(items: list, flags: dict) -> tuple[str, list[str]]:
    verdict, notes = C.PASS, []
    if flags.get("unjudged"):
        verdict = C.REVIEW
        notes.append("pictures were not judged (Claude limit): relevance unchecked")
    shown = [x for it in items if it for x in [it] + (it.get("alts") or []) if x]
    if not shown:
        return C.REVIEW, notes + ["no pictures"]
    for x in shown:
        label = x.get("title") or x.get("page") or x.get("file", "")
        if not licence_accepted(x.get("license", "")):
            verdict = C.REJECT
            notes.append(f"licence not accepted ({x.get('license') or 'none'}): {label[:60]}")
        if not x.get("page") and not x.get("url"):
            verdict = C.REJECT
            notes.append(f"no source page recorded: {label[:60]}")
        if not x.get("author") and "pixabay" not in (x.get("license") or "").lower() \
                and not re.search(r"public domain|cc0|pd", x.get("license", ""), re.I):
            verdict = C.worst(verdict, C.REVIEW)
            notes.append(f"no author for the attribution: {label[:60]}")
        if x.get("kind") == "video" and "pixabay" not in (x.get("source") or "").lower():
            if BROADCAST.search(f"{x.get('title', '')} {x.get('page', '')} {x.get('description', '')}"):
                verdict = C.REJECT
                notes.append(f"looks like TV / NBA broadcast footage: {label[:60]}")
    return verdict, notes


def music_record(music: dict) -> dict | None:
    try:
        ledger = json.loads(MUSIC_LICENSES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return ledger.get("tracks", {}).get(music.get("library_key", ""))


def check_music(music: dict | None) -> tuple[str, list[str]]:
    if not music:
        return C.PASS, ["no music"]
    if music.get("library"):
        rec = music_record(music)
        if not rec:
            return C.REVIEW, [f"no licence record for library track {Path(music.get('file', '')).name}"]
        if not rec.get("confirmed"):
            return C.REVIEW, ["library track licence not yet confirmed"]
        if rec.get("attribution_required") and not music.get("credit"):
            return C.REJECT, ["track needs an attribution line, none in the description"]
        return C.PASS, []
    if not licence_accepted(music.get("license", "")):
        return C.REJECT, [f"music licence not accepted: {music.get('license') or 'none'}"]
    return C.PASS, []


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True)
    try:
        return json.loads(out.stdout or "{}")
    except ValueError:
        return {}


def check_technical(video: Path, short: dict) -> tuple[str, list[str]]:
    if not video.exists():
        return C.REJECT, ["no video file"]
    info = probe(video)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    notes, verdict = [], C.PASS
    if not v or (v.get("width"), v.get("height")) != (1080, 1920):
        verdict = C.REJECT
        notes.append(f"picture is not 1080x1920: {v and (v.get('width'), v.get('height'))}")
    if not a:
        verdict = C.REJECT
        notes.append("no sound")
    if not 10 <= dur <= 60:
        verdict = C.worst(verdict, C.REVIEW)
        notes.append(f"length {dur:.1f}s is outside 10-60 s")
    heard = short.get("_heard")
    if heard is None:
        verdict = C.worst(verdict, C.REVIEW)
        notes.append("no voice timing found")
    elif heard < MIN_HEARD:
        verdict = C.worst(verdict, C.REVIEW)
        notes.append(f"only {heard:.0%} of the words are clearly heard")
    return verdict, notes


def check_editorial(short: dict) -> tuple[str, list[str]]:
    """The script stage's own hold (⚠️ needs review: it repeats itself, has no closing question,
    nothing beyond the headline, a number or a quote not in the sources, too close to an
    earlier Short, wrong length). A held script is never published automatically."""
    if short.get("ready", True):
        return C.PASS, []
    notes = list((short.get("retention") or {}).get("hard") or [])
    if ((short.get("compliance") or {}).get("verdict") or C.PASS) != C.PASS:
        notes.append("monetization checks did not pass (see above)")
    for key, what in (("unsupported_numbers", "numbers not in the sources"),
                      ("unsupported_quotes", "quotes not in the sources"),
                      ("banned_phrases", "banned phrases"), ("too_similar_to", "too similar to an earlier Short")):
        if short.get(key):
            notes.append(what)
    return C.REVIEW, notes or ["the script stage held it for review"]


def decide(short: dict, items: list, flags: dict, music: dict | None, video: Path) -> dict:
    checks = dict((short.get("compliance") or {}).get("checks") or {})
    if not checks:
        checks["script_checks"] = {"verdict": C.REVIEW, "notes": ["the script was not checked"]}
    v, n = check_editorial(short)
    checks["editorial"] = {"verdict": v, "notes": n}
    v, n = check_visuals(items, flags)
    checks["visual_licensing"] = {"verdict": v, "notes": n}
    v, n = check_music(music)
    checks["music_licensing"] = {"verdict": v, "notes": n}
    v, n = check_technical(video, short)
    checks["technical_quality"] = {"verdict": v, "notes": n}
    return {"verdict": C.worst(*(c["verdict"] for c in checks.values())), "checks": checks}


def record_video(name: str, short: dict, result: dict) -> None:
    """Permanent record of every video made and its gate decision (the upload stage will add
    the YouTube id). Kept in the private state repository."""
    import datetime as dt
    LEDGER.mkdir(parents=True, exist_ok=True)
    rec = {"time": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "run": os.environ.get("GITHUB_RUN_ID", "local"), "short": name,
           "headline": short.get("headline", ""),
           "title": (short.get("titles") or [{}])[0].get("title", ""),
           "thumbnail_text": short.get("thumbnail_text", ""),
           "gate": result["verdict"],
           "problems": {k: c.get("notes") for k, c in result["checks"].items() if c["verdict"] != C.PASS},
           "claims": short.get("claims", []),
           "sources": [s.get("link") for s in short.get("sources", [])],
           "youtube_id": None}
    with open(LEDGER / "videos.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> None:
    GATE.mkdir(parents=True, exist_ok=True)
    icon = {C.PASS: "✅", C.REVIEW: "🟡", C.REJECT: "⛔"}
    lines = ["## 🚦 Publication gate", "",
             "Only ✅ PASS may be published automatically. 🟡 REVIEW is held, ⛔ REJECT is never published.", ""]
    for script_path in sorted(SCRIPTS.glob("short_*.json")):
        name = script_path.stem
        short = json.loads(script_path.read_text(encoding="utf-8"))
        def load(p: Path, default):
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return default
        short["_heard"] = load(AUDIO / f"{name}.timing.json", {}).get("heard")
        result = decide(short, load(MEDIA / f"{name}_vs.json", []) + load(MEDIA / f"{name}.json", []), load(MEDIA / f"{name}_flags.json", {}),
                        load(MEDIA / f"{name}_music.json", None), VIDEO / f"{name}.mp4")
        (GATE / f"{name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        short.pop("_heard", None)
        short["gate"] = result["verdict"]
        record_video(name, short, result)
        script_path.write_text(json.dumps(short, indent=2, ensure_ascii=False), encoding="utf-8")
        lines += [f"### {name}: {icon[result['verdict']]} {result['verdict']}", "",
                  "| check | verdict | why |", "|---|---|---|"]
        for k, c in result["checks"].items():
            lines.append(f"| {k.replace('_', ' ')} | {icon[c['verdict']]} {c['verdict']} | "
                         f"{'; '.join(c.get('notes') or []) or '-'} |")
        lines.append("")
        print(f"[gate] {name}: {result['verdict']}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))


if __name__ == "__main__":
    main()

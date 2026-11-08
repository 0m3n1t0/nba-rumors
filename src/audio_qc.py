"""Stage 4b: yt-edit on our own narration.

youtube-agent-skill's yt-edit (deadair.py) reads a timestamped transcript and lists
the dead air. Here the transcript is Whisper's word timing of our voice-over, so it
finds the places where the synthetic voice paused too long (Shorts lose viewers in
silences). Only DEAD gaps are cut: yt-edit also flags filler words, but in a script
we wrote on purpose, "so" or "honestly" are style, not mistakes.

The cuts are applied to the MP3 and every beat/word time is shifted to match, so
the video stage stays in sync.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skills import segments_file, summary, tool  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "data" / "audio"
FLOOR = 0.5   # seconds of silence we tolerate between words (a short dramatic pause before a
              # twist is part of the performance; longer is dead air that loses viewers)
PAD = 0.22    # Whisper's word edges are approximate and often END EARLY on a fading last
              # sound ("-s", "-t"): never cut closer than this to a word, or the cut eats it
FADE = 0.012  # a tiny fade at every join, so the cut never clicks


def shift(t: float, cuts: list[dict]) -> float:
    return round(t - sum(min(c["end"], t) - c["start"] for c in cuts if c["start"] < t), 2)


def apply_cuts(mp3: Path, cuts: list[dict], duration: float) -> None:
    keep, last = [], 0.0
    for c in sorted(cuts, key=lambda c: c["start"]):
        keep.append((last, c["start"]))
        last = c["end"]
    keep.append((last, duration + 1))
    parts = "".join(
        f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},"
        f"areverse,afade=t=in:d={FADE},areverse[a{i}];" for i, (a, b) in enumerate(keep))
    concat = "".join(f"[a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[out]"
    tmp = mp3.with_suffix(".tight.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-filter_complex",
                    parts + concat, "-map", "[out]", "-b:a", "192k", str(tmp)], check=True)
    tmp.replace(mp3)


def main() -> None:
    timings = sorted(AUDIO.glob("short_*.timing.json"))
    if not timings:
        print("[=] yt-edit: no narration yet, sleeping")
        return
    lines = ["## ✂️ yt-edit (dead air in our narration)", "", "| Short | cuts | removed | new length | where |",
             "|---|---|---|---|---|"]
    for path in timings:
        timing = json.loads(path.read_text(encoding="utf-8"))
        seg = segments_file(timing["words"], path.with_suffix(".segments.json"))
        report = tool("yt-edit", "deadair.py", str(seg), "--floor", str(FLOOR)) or {}
        seg.unlink(missing_ok=True)
        cuts = [{**c, "start": round(c["start"] + PAD, 3), "end": round(c["end"] - PAD, 3)}
                for c in report.get("cuts", []) if c.get("kind") == "DEAD"]
        cuts = [c for c in cuts if c["end"] - c["start"] >= 0.08]
        # where each cut is, so a clipped word can be traced: "word ✂ next"
        where = []
        for c in cuts:
            before = [w["word"] for w in timing["words"] if w["end"] <= c["start"] + 0.01][-1:]
            after = [w["word"] for w in timing["words"] if w["start"] >= c["start"] - 0.01][:1]
            where.append(f"{' '.join(before)} ✂ {' '.join(after)}")
        if cuts:
            mp3 = path.with_name(path.name.replace(".timing.json", ".mp3"))
            apply_cuts(mp3, cuts, timing["duration"])
            for b in timing["beats"]:
                b["start"], b["end"] = shift(b["start"], cuts), shift(b["end"], cuts)
            for w in timing["words"]:
                w["start"], w["end"] = shift(w["start"], cuts), shift(w["end"], cuts)
            removed = round(sum(c["end"] - c["start"] for c in cuts), 2)
            timing["duration"] = round(timing["duration"] - removed, 2)
            timing["yt_edit_cuts"] = cuts
            path.write_text(json.dumps(timing, indent=2), encoding="utf-8")
        else:
            removed = 0
        name = path.name.replace(".timing.json", "")
        lines.append(f"| {name} | {len(cuts)} | {removed}s | {timing['duration']:.1f}s | {' · '.join(where) or '-'} |")
    summary("\n".join(lines))


if __name__ == "__main__":
    main()

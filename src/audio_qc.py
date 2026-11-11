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
# yt-edit (deadair.py) decides WHICH pauses are dead; WHERE to cut is measured in the sound
# itself, because Whisper's word edges are approximate and often END EARLY on a fading last
# sound (after "positively." the voice still sounds for half a second). The natural rhythm
# of the voice stays untouched (owner, 2026-11-11: never run sentences together): only a
# TRULY silent stretch longer than LONG is shortened, and LEFT of it stays (a full sentence
# pause). Chatterbox's own pauses (0.3-0.5 s) are never cut; mostly the Kokoro fallback's
# long silences are. No sound is ever removed.
LONG = 0.7        # seconds of real silence before a pause counts as dead air
LEFT = 0.5        # what stays of a shortened pause (a natural sentence pause)
SILENT = 0.04     # a 20 ms frame quieter than this share of the speech level is silence
FRAME = 0.02
FADE = 0.012  # a tiny fade at every join, so the cut never clicks


def pcm(mp3: Path, rate: int = 16000):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1",
                          "-ar", str(rate), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def silence_cut(audio, rate: int, start: float, end: float, level: float) -> dict | None:
    """The cuttable middle of the longest truly silent stretch between start and end
    (seconds), or None. Silence = 20 ms frames under SILENT x the speech level."""
    import numpy as np
    n = int(FRAME * rate)
    a, b = int(max(0.0, start) * rate), int(min(len(audio) / rate, end) * rate)
    frames = [float(np.sqrt(np.mean(audio[k:k + n] ** 2))) for k in range(a, b - n + 1, n)]
    best, run_start = (0, 0), None
    for i, v in enumerate(frames + [1.0]):
        if v < SILENT * level:
            run_start = i if run_start is None else run_start
        elif run_start is not None:
            if i - run_start > best[1] - best[0]:
                best = (run_start, i)
            run_start = None
    s0, s1 = a / rate + best[0] * FRAME, a / rate + best[1] * FRAME
    if s1 - s0 < LONG:
        return None                      # a natural pause: never touched
    cut_start, cut_end = s0 + LEFT / 2, s1 - LEFT / 2
    if cut_end - cut_start < 0.08:
        return None
    return {"start": round(cut_start, 3), "end": round(cut_end, 3)}


def sound_end(mp3: Path, rate: int = 16000) -> float | None:
    """Where the voice really stops (the last 20 ms frame that is not silence), in seconds:
    the end card starts after it, never over a fading last sound."""
    import numpy as np
    audio = pcm(mp3, rate)
    loud = audio[np.abs(audio) > 0.02]
    if not len(loud):
        return None
    level, n = float(np.sqrt(np.mean(loud ** 2))), int(FRAME * rate)
    frames = [k for k in range(0, len(audio) - n, n) if float(np.sqrt(np.mean(audio[k:k + n] ** 2))) >= SILENT * level]
    return round((frames[-1] + n) / rate, 2) if frames else None


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
        mp3 = path.with_name(path.name.replace(".timing.json", ".mp3"))
        cuts = []
        dead = [c for c in report.get("cuts", []) if c.get("kind") == "DEAD"]
        if dead and mp3.exists():
            import numpy as np
            audio = pcm(mp3)
            loud = audio[np.abs(audio) > 0.02]
            level = float(np.sqrt(np.mean(loud ** 2))) if len(loud) else 0.1
            for c in dead:
                before = [w["end"] for w in timing["words"] if w["end"] <= c["start"] + 0.01]
                after = [w["start"] for w in timing["words"] if w["start"] >= c["end"] - 0.01]
                if not before or not after:
                    continue
                # search from the word Whisper heard before to the one after (a little past it,
                # in case Whisper's start is late)
                cut = silence_cut(audio, 16000, max(before), min(after) + 0.1, level)
                if cut:
                    cuts.append({**c, **cut})
        # where each cut is, so a clipped word can be traced: "word ✂ next"
        where = []
        for c in cuts:
            before = [w["word"] for w in timing["words"] if w["end"] <= c["start"] + 0.01][-1:]
            after = [w["word"] for w in timing["words"] if w["start"] >= c["start"] - 0.01][:1]
            where.append(f"{' '.join(before)} ✂ {' '.join(after)}")
        if cuts:
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
        if mp3.exists():
            try:
                end = sound_end(mp3)
                if end:
                    timing["voice_end"] = end
                    path.write_text(json.dumps(timing, indent=2), encoding="utf-8")
            except Exception as exc:
                print(f"[!] {path.name}: voice end not measured ({exc}); the end card waits for the file's end")
        name = path.name.replace(".timing.json", "")
        lines.append(f"| {name} | {len(cuts)} | {removed}s | {timing['duration']:.1f}s | {' · '.join(where) or '-'} |")
    summary("\n".join(lines))


if __name__ == "__main__":
    main()

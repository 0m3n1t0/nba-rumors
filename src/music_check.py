"""Measures every track in the music library, so the right song goes under the right story.

No listening by ear needed: each track is measured (from 15 s in, like the videos use it):
  bpm      tempo, from the beat pattern
  bass     share of energy under 150 Hz (the 808 / sub-bass that makes trap "heavy")
  bright   spectral centroid in Hz (low = dark and heavy, high = bright and happy)
  steady   how even the energy is over time (a bed under a voice must not jump around)
The MOOD comes from YouTube's own labels (the Audio Library "Mood" filter the track was
downloaded with = its folder). This check is a quality gate on top: a usable bed under a voice
has a clear, steady beat and no big jumps. Each track gets a 0-10 "bed" score; tracks under 5
are not used. Results are cached (data/history/music_features.json) and shown in the run
summary, so weak tracks can be replaced.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

SR = 22050
MIN_BED = 5.0  # tracks scoring under this are not used

def decode(path: Path, start: float = 15.0, seconds: float = 60.0) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(seconds), "-i", str(path),
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if x.size < SR * 10:  # short track: measure from the start
        raw = subprocess.run(["ffmpeg", "-v", "error", "-t", str(seconds), "-i", str(path), "-ac", "1",
                              "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
    return x


def features(path: Path) -> dict:
    x = decode(path)
    if x.size < SR * 5:
        return {"error": "too short or unreadable"}
    n, hop = 2048, 512
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    power = spec ** 2
    total = power.sum(axis=1) + 1e-12
    bass = float(power[:, freqs < 150].sum() / total.sum())
    bright = float((power * freqs).sum() / total.sum())
    # tempo: autocorrelation of spectral flux
    flux = np.maximum(np.diff(np.log1p(spec), axis=0), 0).sum(axis=1)
    flux = flux - flux.mean()
    ac = np.correlate(flux, flux, mode="full")[flux.size - 1:]
    fps = SR / hop
    lags = np.arange(ac.size)
    ok = (lags >= fps * 60 / 200) & (lags <= fps * 60 / 55)
    lag = lags[ok][np.argmax(ac[ok])]
    bpm = float(60 * fps / lag)
    beat = float(ac[lag] / (ac[0] + 1e-9))  # 0..1: how clearly the beat repeats
    # steadiness: variation of loudness between 2-second blocks
    rms = np.sqrt((frames ** 2).mean(axis=1))
    block = int(fps * 2)
    blocks = [rms[i:i + block].mean() for i in range(0, rms.size - block, block)] or [rms.mean()]
    steady = float(np.std(blocks) / (np.mean(blocks) + 1e-9))
    return {"bpm": round(bpm), "beat": round(beat, 2), "bass": round(bass, 2), "bright": round(bright),
            "steady": round(steady, 2)}


def bed_score(f: dict) -> float:
    """0-10: how good a background bed under narration this track is (not which mood it is)."""
    if "error" in f:
        return 0.0
    score = 4 * min(1.0, f.get("beat", 0) / 0.35)           # clear repeating beat (not ambient drift)
    score += 3 if f["steady"] <= 0.45 else (1.5 if f["steady"] <= 0.7 else 0)  # no big jumps
    score += 2 if 60 <= f["bpm"] <= 180 else 0                # a real groove tempo
    score += 1 if f["bright"] <= 4500 else 0                  # not harsh / hissy
    if f.get("beat", 0) < 0.15:                               # no beat at all: ambient pad, never a bed
        score = min(score, 4.0)
    return round(score, 1)


def measure_library(library: Path, cache_path: Path) -> dict:
    """{"mood/file.mp3": {"bpm":..., ..., "fit": {mood: score}}} for every track (cached)."""
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    out = {}
    for f in sorted(library.glob("*/*")):
        if f.suffix.lower() not in (".mp3", ".wav", ".m4a", ".ogg"):
            continue
        key = f"{f.parent.name}/{f.name}"
        stamp = f"{f.stat().st_size}"
        entry = cache.get(key)
        if not entry or entry.get("stamp") != stamp:
            try:
                entry = {**features(f), "stamp": stamp}
            except Exception as exc:  # never stop the run over one file
                entry = {"error": str(exc)[:80], "stamp": stamp}
            entry["bed"] = bed_score(entry)
        out[key] = entry
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":  # python src/music_check.py music_library  -> prints the table
    import sys
    lib = Path(sys.argv[1] if len(sys.argv) > 1 else "music_library")
    for k, v in measure_library(lib, Path("/tmp/music_features.json")).items():
        print(k, {x: v.get(x) for x in ("bpm", "beat", "bass", "bright", "steady")}, "bed", v["bed"])

"""Stage 4: voice. Turn every ready script into narration audio.

Uses the voice chosen in the audition (config/voice.json), so every video
sounds the same. Each part of the script (hook + beats) is spoken separately
and joined with a short gap, so we know exactly when each beat starts; the
video stage uses that to switch the on-screen cards.

Then faster-whisper listens to the result to get the time of every word,
for the word-by-word captions Shorts need.

Output per short:
  data/audio/short_N.mp3         the narration
  data/audio/short_N.timing.json beat start/end times + every word's time
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCRIPTS = DATA / "scripts"
AUDIO = DATA / "audio"
CONFIG = json.loads((ROOT / "config" / "voice.json").read_text(encoding="utf-8"))
RATE = 24000

# The whole script is spoken in ONE pass, exactly like the audition sample the voice was chosen
# on: Kokoro then carries one natural intonation across the story instead of restarting at
# every beat or sentence (restarting is what made it sound flat and choppy).
ACRONYMS = {"NBA", "ESPN", "MVP", "TNT", "ABC", "NBC", "CBS", "WNBA", "USA", "GOAT", "OKC", "LA"}
BRIGHT = "equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=60"


def speakable(text: str) -> str:
    """Small fixes so the voice reads the way a person would."""
    text = re.sub(r"(\d+)-(\d+)-(\d+)", r"\1, \2, \3", text)      # 52-24-8
    text = re.sub(r"(\d{2,3})-(\d{2,3})", r"\1 to \2", text)       # 112-111
    text = re.sub(r"\b(\d{1,2})-(\d{1,2})\b", r"\1 and \2", text)   # a 3-6 record
    text = text.replace("&", " and ").replace("%", " percent").replace("vs.", "versus")
    text = re.sub(r"\[[^\]]*\]", "", text)                          # stray [notes]
    return re.sub(r"\s+", " ", text).strip()


def lower_caps(text: str) -> str:
    """Words in CAPS for emphasis are read as words, not spelled out letter by letter."""
    return re.sub(r"\b[A-Z]{3,}\b", lambda m: m.group(0) if m.group(0) in ACRONYMS else m.group(0).lower(), text)


def load_pipeline():
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code=CONFIG["lang_code"])
    total = sum(CONFIG["blend"].values())
    voice = sum(pipeline.load_voice(v) * (w / total) for v, w in CONFIG["blend"].items())
    return pipeline, voice


def say_once(pipeline, voice, text: str, speed: float) -> np.ndarray:
    chunks = [a for _, _, a in pipeline(text, voice=voice, speed=speed)]
    return np.concatenate(chunks).astype(np.float32) if chunks else np.zeros(1, dtype=np.float32)


def speak(pipeline, voice, text: str) -> np.ndarray:
    return say_once(pipeline, voice, lower_caps(speakable(text)), CONFIG["speed"])


TOKEN = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower().replace("\u2019", "'"))


def beat_times(parts: list[dict], words: list[dict], duration: float) -> list[dict]:
    """Where each beat starts in the one-pass narration: align the script's words with what
    Whisper heard; a beat whose first words are not found is placed by its share of the words."""
    import difflib
    script, owner = [], []
    for i, part in enumerate(parts):
        toks = tokens(lower_caps(speakable(part["say"])))
        script += toks
        owner += [i] * len(toks)
    heard = [(tokens(w["word"]) or [""])[0] for w in words]
    pos = {}
    for a, b, size in difflib.SequenceMatcher(None, script, heard, autojunk=False).get_matching_blocks():
        for k in range(size):
            pos.setdefault(a + k, b + k)
    starts = []
    for i in range(len(parts)):
        idx = [k for k, o in enumerate(owner) if o == i]
        hit = next((pos[k] for k in idx[:6] if k in pos), None)
        if hit is not None and hit < len(words):
            t = words[hit]["start"]
        else:
            t = duration * (idx[0] / max(len(script), 1)) if idx else (starts[-1] if starts else 0.0)
        starts.append(max(t, starts[-1] if starts else 0.0))
    starts[0] = 0.0
    return [{"index": i, "say": p["say"], "on_screen": p.get("on_screen", ""),
             "start": round(starts[i], 2),
             "end": round(starts[i + 1] if i + 1 < len(parts) else duration, 2)}
            for i, p in enumerate(parts)]


def finish(wav: Path, mp3: Path) -> None:
    parts = []
    pitch = CONFIG.get("pitch", 1.0)
    if pitch != 1.0:
        parts.append(f"asetrate={int(RATE * pitch)},aresample={RATE},atempo={1 / pitch:.4f}")
    if CONFIG.get("bright_eq"):
        parts.append(BRIGHT)
    parts.append("loudnorm=I=-14:TP=-1.5")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", ",".join(parts),
                    "-ar", "44100", "-b:a", "192k", str(mp3)], check=True)


def load_16k(mp3: Path) -> np.ndarray:
    """Decode with ffmpeg to 16 kHz mono float32 (what Whisper expects).

    faster-whisper's own decoder (PyAV) breaks with newer `av` releases,
    so we never let it open files.
    """
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp3), "-f", "f32le",
                          "-ac", "1", "-ar", "16000", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def word_times(mp3: Path) -> list[dict]:
    from faster_whisper import WhisperModel
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(load_16k(mp3), word_timestamps=True, language="en")
    return [{"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)}
            for seg in segments for w in seg.words]


def main() -> None:
    scripts = sorted(SCRIPTS.glob("short_*.json"))
    if not scripts:
        sys.exit("[!] No scripts to voice.")
    AUDIO.mkdir(parents=True, exist_ok=True)
    pipeline, voice = load_pipeline()

    lines = ["## 🎙️ Voice", "", "| Short | Ready | Length | Beats |", "|---|---|---|---|"]
    for path in scripts:
        short = json.loads(path.read_text(encoding="utf-8"))
        parts = [{"say": short["hook"]["text"], "on_screen": "HOOK"}] + short["beats"]

        clip = speak(pipeline, voice, " ".join(p["say"].strip() for p in parts))
        tail = np.zeros(int(RATE * 0.3), dtype=np.float32)
        name = path.stem
        wav = AUDIO / f"{name}.wav"
        sf.write(wav, np.concatenate([clip, tail]), RATE)
        mp3 = AUDIO / f"{name}.mp3"
        finish(wav, mp3)
        wav.unlink()

        duration = round((len(clip) + len(tail)) / RATE, 2)
        words = word_times(mp3)
        beats = beat_times(parts, words, duration)
        timing = {"duration": duration, "beats": beats, "words": words}
        (AUDIO / f"{name}.timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")
        ready = "✅" if short.get("ready") else "⚠️"
        lines.append(f"| {short['n']}: {short['headline'][:60]} | {ready} | {timing['duration']:.0f}s | {len(beats)} |")
        print(f"[+] {name}: {timing['duration']:.1f}s, {len(timing['words'])} words timed")

    text = "\n".join(lines)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

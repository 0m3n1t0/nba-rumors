"""Voice audition: read the same lines with every candidate voice.

Kokoro (Apache 2.0, free for commercial use) American female voices, each at
the channel's Shorts speed, plus "husky" versions pitched about 2 semitones
lower for a deeper, raspier tone.

Output: samples/<name>.mp3  (downloaded from the Actions run as one zip)
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "samples"
RATE = 24000
SPEED = 1.12  # Shorts read a little faster than normal speech

TEXT = (
    "If you missed Wembanyama on Wednesday, you missed fifty-two points, twenty-four rebounds "
    "and eight blocks. A line nobody has posted since 1973. "
    "Now here is where it gets messy. Dallas came back, took the lead in the fourth, "
    "and Wemby went down with an ankle. He came back. Spurs win by one. "
    "So be honest. Is this the best game you have seen all season?"
)

# name: (kokoro voice, pitch factor; below 1.0 = deeper)
CANDIDATES = {
    "01_heart": ("af_heart", 1.0),
    "02_bella": ("af_bella", 1.0),
    "03_nicole_breathy": ("af_nicole", 1.0),
    "04_sky": ("af_sky", 1.0),
    "05_sarah": ("af_sarah", 1.0),
    "06_aoede": ("af_aoede", 1.0),
    "07_kore": ("af_kore", 1.0),
    "08_jessica": ("af_jessica", 1.0),
    "09_nova": ("af_nova", 1.0),
    "10_river": ("af_river", 1.0),
    "11_bella_husky": ("af_bella", 0.89),
    "12_heart_husky": ("af_heart", 0.89),
    "13_nicole_husky": ("af_nicole", 0.89),
    "14_bella_nicole_mix_husky": ("af_bella,af_nicole", 0.91),
}


def synth(pipeline: KPipeline, voice: str) -> np.ndarray:
    chunks = [audio for _, _, audio in pipeline(TEXT, voice=voice, speed=SPEED)]
    return np.concatenate(chunks)


def to_mp3(wav: Path, mp3: Path, pitch: float) -> None:
    # Lower the pitch without changing the length: play slower, then speed back up.
    flt = "loudnorm=I=-14:TP=-1.5"
    if pitch != 1.0:
        flt = f"asetrate={int(RATE * pitch)},aresample={RATE},atempo={1 / pitch:.4f}," + flt
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", flt,
                    "-b:a", "160k", str(mp3)], check=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pipeline = KPipeline(lang_code="a")  # American English
    for name, (voice, pitch) in CANDIDATES.items():
        try:
            audio = synth(pipeline, voice)
        except Exception as exc:  # a missing voice must not stop the audition
            print(f"[!] {name}: {exc}")
            continue
        wav = OUT / f"{name}.wav"
        sf.write(wav, audio, RATE)
        to_mp3(wav, OUT / f"{name}.mp3", pitch)
        wav.unlink()
        print(f"[+] {name} ({voice}, pitch {pitch})")


if __name__ == "__main__":
    main()

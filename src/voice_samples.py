"""Voice audition, round 2: between Bella and Nicole.

Feedback from round 1: the ideal is between 02_bella (energy) and
03_nicole_breathy (timbre), and Nicole's timbre without the whisper.

Kokoro voices are vectors, so they can be blended by weight. Nicole's whisper
is softened by mixing in clearer voices (Heart, Sarah) and by a "presence"
EQ + compressor that pushes the voice forward like a radio host.

Output: samples/<name>.mp3
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
SPEED = 1.12

TEXT = (
    "If you missed Wembanyama on Wednesday, you missed fifty-two points, twenty-four rebounds "
    "and eight blocks. A line nobody has posted since 1973. "
    "Now here is where it gets messy. Dallas came back, took the lead in the fourth, "
    "and Wemby went down with an ankle. He came back. Spurs win by one. "
    "So be honest. Is this the best game you have seen all season?"
)

# Radio "presence": a little more clarity at 3 kHz, less air at 9 kHz (the whisper),
# then a compressor so the voice sounds close and confident.
PRESENCE = ("equalizer=f=180:t=q:w=1:g=2,equalizer=f=3000:t=q:w=1.2:g=3,"
            "equalizer=f=9000:t=q:w=1.5:g=-4,acompressor=threshold=-20dB:ratio=3:attack=5:release=80")

# name: ({voice: weight}, use presence EQ)
CANDIDATES = {
    "A_bella70_nicole30": ({"af_bella": 0.7, "af_nicole": 0.3}, False),
    "B_bella50_nicole50": ({"af_bella": 0.5, "af_nicole": 0.5}, False),
    "C_bella30_nicole70": ({"af_bella": 0.3, "af_nicole": 0.7}, False),
    "D_bella50_nicole50_radio": ({"af_bella": 0.5, "af_nicole": 0.5}, True),
    "E_nicole_radio": ({"af_nicole": 1.0}, True),
    "F_nicole70_heart30": ({"af_nicole": 0.7, "af_heart": 0.3}, False),
    "G_nicole60_sarah40": ({"af_nicole": 0.6, "af_sarah": 0.4}, False),
    "H_nicole60_heart40_radio": ({"af_nicole": 0.6, "af_heart": 0.4}, True),
}


def blend(pipeline: KPipeline, weights: dict[str, float]):
    total = sum(weights.values())
    return sum(pipeline.load_voice(v) * (w / total) for v, w in weights.items())


def synth(pipeline: KPipeline, voice) -> np.ndarray:
    return np.concatenate([audio for _, _, audio in pipeline(TEXT, voice=voice, speed=SPEED)])


def to_mp3(wav: Path, mp3: Path, presence: bool) -> None:
    flt = (PRESENCE + "," if presence else "") + "loudnorm=I=-14:TP=-1.5"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", flt,
                    "-b:a", "160k", str(mp3)], check=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pipeline = KPipeline(lang_code="a")
    for name, (weights, presence) in CANDIDATES.items():
        try:
            audio = synth(pipeline, blend(pipeline, weights))
        except Exception as exc:
            print(f"[!] {name}: {exc}")
            continue
        wav = OUT / f"{name}.wav"
        sf.write(wav, audio, RATE)
        to_mp3(wav, OUT / f"{name}.mp3", presence)
        wav.unlink()
        print(f"[+] {name}")


if __name__ == "__main__":
    main()

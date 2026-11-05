"""Voice audition, round 3: B (Bella 50 / Nicole 50) with more energy.

Feedback from round 2: B is the right sexy timbre, but needs more energy and life.
Four levers, tested one by one and then combined:
  speed      faster delivery
  mix        a bit more Bella (the energetic voice)
  text       punchier punctuation: Kokoro raises its intonation on "!" and short lines
  pitch/eq   a touch higher pitch and a light "bright" EQ for a livelier sound
  flirty     playful, teasing script style (9-11)

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

TEXT_CALM = (
    "If you missed Wembanyama on Wednesday, you missed fifty-two points, twenty-four rebounds "
    "and eight blocks. A line nobody has posted since 1973. "
    "Now here is where it gets messy. Dallas came back, took the lead in the fourth, "
    "and Wemby went down with an ankle. He came back. Spurs win by one. "
    "So be honest. Is this the best game you have seen all season?"
)
TEXT_ENERGY = (
    "If you missed Wembanyama on Wednesday... you missed fifty-two points! Twenty-four rebounds! "
    "Eight blocks! Nobody has done that since 1973. "
    "And here's where it gets messy. Dallas comes back. Takes the lead in the fourth! "
    "Wemby goes down with an ankle... and he comes back! Spurs win by one! "
    "So be honest. Is this the best game you've seen all season?"
)
# Flirty = playful and teasing, not explicit (advertiser-friendly): short teasing lines,
# a pause before the payoff, talking to "you" like a secret.
TEXT_FLIRTY = (
    "Okay, come closer. You missed Wembanyama on Wednesday? Oh, you're gonna hate yourself. "
    "Fifty-two points. Twenty-four rebounds. Eight blocks. Nobody's done that since 1973! "
    "And here's the juicy part... Dallas comes back. Takes the lead in the fourth. "
    "Wemby goes down with an ankle... and then? He comes back. Spurs win by one! "
    "So tell me, babe... is this the best game you've seen all season?"
)
TEXTS = {"calm": TEXT_CALM, "energy": TEXT_ENERGY, "flirty": TEXT_FLIRTY}

BRIGHT = "equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=60"

# name: (weights, speed, text, pitch, bright EQ)
CANDIDATES = {
    "1_B_speed120": ({"af_bella": 0.5, "af_nicole": 0.5}, 1.20, "calm", 1.0, False),
    "2_B_speed125": ({"af_bella": 0.5, "af_nicole": 0.5}, 1.25, "calm", 1.0, False),
    "3_B60_speed120": ({"af_bella": 0.6, "af_nicole": 0.4}, 1.20, "calm", 1.0, False),
    "4_B_energytext_speed120": ({"af_bella": 0.5, "af_nicole": 0.5}, 1.20, "energy", 1.0, False),
    "5_B60_energytext_speed120": ({"af_bella": 0.6, "af_nicole": 0.4}, 1.20, "energy", 1.0, False),
    "6_B60_energytext_speed120_bright": ({"af_bella": 0.6, "af_nicole": 0.4}, 1.20, "energy", 1.0, True),
    "7_B60_energytext_speed120_pitchup": ({"af_bella": 0.6, "af_nicole": 0.4}, 1.20, "energy", 1.03, True),
    "8_B65_energytext_speed125_bright": ({"af_bella": 0.65, "af_nicole": 0.35}, 1.25, "energy", 1.0, True),
    "9_B_flirty_speed115": ({"af_bella": 0.5, "af_nicole": 0.5}, 1.15, "flirty", 1.0, False),
    "10_B60_flirty_speed120_bright": ({"af_bella": 0.6, "af_nicole": 0.4}, 1.20, "flirty", 1.0, True),
    "11_B45_flirty_speed115": ({"af_bella": 0.45, "af_nicole": 0.55}, 1.15, "flirty", 1.0, True),
}


def blend(pipeline: KPipeline, weights: dict[str, float]):
    total = sum(weights.values())
    return sum(pipeline.load_voice(v) * (w / total) for v, w in weights.items())


def to_mp3(wav: Path, mp3: Path, pitch: float, bright: bool) -> None:
    parts = []
    if pitch != 1.0:
        parts.append(f"asetrate={int(RATE * pitch)},aresample={RATE},atempo={1 / pitch:.4f}")
    if bright:
        parts.append(BRIGHT)
    parts.append("loudnorm=I=-14:TP=-1.5")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", ",".join(parts),
                    "-b:a", "160k", str(mp3)], check=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pipeline = KPipeline(lang_code="a")
    for name, (weights, speed, text, pitch, bright) in CANDIDATES.items():
        try:
            voice = blend(pipeline, weights)
            audio = np.concatenate([a for _, _, a in pipeline(TEXTS[text], voice=voice, speed=speed)])
        except Exception as exc:
            print(f"[!] {name}: {exc}")
            continue
        wav = OUT / f"{name}.wav"
        sf.write(wav, audio, RATE)
        to_mp3(wav, OUT / f"{name}.mp3", pitch, bright)
        wav.unlink()
        print(f"[+] {name}")


if __name__ == "__main__":
    main()

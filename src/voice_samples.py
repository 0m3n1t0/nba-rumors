"""Voice audition, round 4: Chatterbox (expressive) with OUR voice.

Feedback from round 3: voice #11 has the right timbre (sexy, flirty) but no life:
no human intonation, no energy. That is the ceiling of Kokoro.

Chatterbox (Resemble AI, MIT license, free for commercial use) is an expressive
model with an emotion "exaggeration" control. It can copy a voice from a short
reference clip. The reference is our own voice #11, made with Kokoro right here,
so the channel keeps the voice we chose and gets a human delivery.

Also new: a human-written script (story, reactions, opinion), to hear how much
the text itself changes the energy.

Output: samples/<name>.mp3
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "samples"
CONFIG = json.loads((ROOT / "config" / "voice.json").read_text(encoding="utf-8"))
KOKORO_RATE = 24000

REFERENCE_TEXT = (
    "So here's the thing about this league. Everybody wants to talk about the big names, "
    "but the stories that really matter? They're usually hiding in the details. "
    "And honestly, that's my favorite part. Let me show you what I mean."
)

STORY = (
    "Wembanyama has been sick. He said it himself. And then he goes out and drops fifty-two on Dallas. "
    "Fifty-two points, twenty-four rebounds, eight blocks. Nobody has done that since 1973. "
    "And it wasn't even easy! Dallas came all the way back, took the lead in the fourth, "
    "Wemby goes down with an ankle... and he comes back. Free throw. Spurs win by one. "
    "I mean, come on. Sick, hurt, and still the best player on the floor? "
    "Honestly, I think he's already the scariest player in the league. Tell me I'm wrong."
)

BRIGHT = "equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=60"

# name: (exaggeration, cfg_weight, temperature)
#   exaggeration: 0.5 neutral, higher = more emotion and energy
#   cfg_weight: lower = faster, livelier pacing
CANDIDATES = {
    "2_chatterbox_exag05_cfg05": (0.5, 0.5, 0.8),
    "3_chatterbox_exag07_cfg04": (0.7, 0.4, 0.8),
    "4_chatterbox_exag08_cfg03": (0.8, 0.3, 0.8),
    "5_chatterbox_exag10_cfg03": (1.0, 0.3, 0.8),
    "6_chatterbox_exag08_cfg03_temp09": (0.8, 0.3, 0.9),
}


def kokoro_voice():
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code=CONFIG["lang_code"])
    total = sum(CONFIG["blend"].values())
    voice = sum(pipeline.load_voice(v) * (w / total) for v, w in CONFIG["blend"].items())
    return pipeline, voice


def kokoro_say(pipeline, voice, text: str, path: Path) -> None:
    audio = np.concatenate([a for _, _, a in pipeline(text, voice=voice, speed=CONFIG["speed"])])
    sf.write(path, audio, KOKORO_RATE)


def to_mp3(wav: Path, mp3: Path, bright: bool = True) -> None:
    flt = (BRIGHT + "," if bright else "") + "loudnorm=I=-14:TP=-1.5"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", flt,
                    "-b:a", "160k", str(mp3)], check=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    # 1) Our chosen Kokoro voice: the reference clip, and the new story for comparison.
    pipeline, voice = kokoro_voice()
    reference = OUT / "reference_voice11.wav"
    kokoro_say(pipeline, voice, REFERENCE_TEXT, reference)
    story_kokoro = OUT / "1_kokoro_voice11_newstory.wav"
    kokoro_say(pipeline, voice, STORY, story_kokoro)
    to_mp3(story_kokoro, OUT / "1_kokoro_voice11_newstory.mp3")
    story_kokoro.unlink()
    print("[+] reference + kokoro comparison")

    # 2) Chatterbox copies that voice and performs the story with emotion.
    import torch
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    torch.manual_seed(7)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    for name, (exag, cfg, temp) in CANDIDATES.items():
        try:
            wav = model.generate(STORY, audio_prompt_path=str(reference),
                                 exaggeration=exag, cfg_weight=cfg, temperature=temp)
        except Exception as exc:
            print(f"[!] {name}: {exc}")
            continue
        path = OUT / f"{name}.wav"
        ta.save(str(path), wav, model.sr)
        to_mp3(path, OUT / f"{name}.mp3")
        path.unlink()
        print(f"[+] {name}")
    reference.unlink()


if __name__ == "__main__":
    main()

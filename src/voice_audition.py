"""Voice audition, round 5: a livelier engine with OUR chosen voice.

Feedback after the one-pass Kokoro runs: the timbre of voice #11 is right, but the
intonation is still flat and slightly unnatural. Kokoro has no emotion control, so this
round tests Chatterbox (Resemble AI, MIT license, free for commercial use, runs on CPU),
which copies a voice from a short reference clip. The reference is our own voice #11 made
with Kokoro right here, so the channel keeps the voice that was chosen and only the delivery
changes.

Every sample reads the SAME real script from the pipeline (a beef story, hook + beats),
so the comparison is fair:

  1_kokoro_now.mp3               what the channel sounds like today (baseline)
  2_chatterbox_exag06.mp3        Chatterbox, a little more emotion than neutral
  3_chatterbox_exag08.mp3        Chatterbox, clearly more emotion
  4_chatterbox_exag10.mp3        Chatterbox, strong emotion
  5_chatterbox_turbo_tags.mp3    Chatterbox Turbo (faster model) with a few natural sounds
                                 such as a short laugh, written into the text

Output: samples/*.mp3 (download the "voice-samples" artifact).
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

# Reference clip for the voice copy: 10-15 s of voice #11, lively, no names or numbers.
REFERENCE_TEXT = (
    "Okay, so here's the thing about this league. Everybody wants to talk about the big names, "
    "but the stories that really matter? They're hiding in the details. And honestly, that's my "
    "favorite part. Let me show you what I mean!"
)

# A real script written by the pipeline (Short 1 of the last run, facts from its sources).
SCRIPT = (
    "LeSean McCoy or Eddie Johnson: who is right about Ayesha Curry's movie kiss, and why is "
    "Jemele Hill calling it misogyny? McCoy on the Speakeasy podcast: \"Now you want us to see "
    "kissing a dude?\" Eddie Johnson fired back on X. \"Just go sit in the stands and be a trophy!\" "
    "Ayesha, to a fan: \"It's not even real.\" Neither Curry has answered McCoy, reportedly. "
    "Honestly? It's a Christmas movie. I think she gets to act! Subscribe, we track every NBA "
    "rumor daily. So who's right, McCoy or Johnson?"
)
# Turbo reads inline sound tags; only a few, where a person would really make that sound.
SCRIPT_TURBO = SCRIPT.replace("Honestly? It's a Christmas movie.",
                              "Honestly? [chuckle] It's a Christmas movie.")

BRIGHT = "equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=60"

# name: (exaggeration, cfg_weight, temperature)
#   exaggeration: 0.5 = neutral, higher = more emotion and energy
#   cfg_weight: lower = livelier, faster pacing
CANDIDATES = {
    "2_chatterbox_exag06": (0.6, 0.35, 0.8),
    "3_chatterbox_exag08": (0.8, 0.3, 0.8),
    "4_chatterbox_exag10": (1.0, 0.3, 0.85),
}


def kokoro_voice():
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code=CONFIG["lang_code"])
    total = sum(CONFIG["blend"].values())
    voice = sum(pipeline.load_voice(v) * (w / total) for v, w in CONFIG["blend"].items())
    return pipeline, voice


def kokoro_say(pipeline, voice, text: str, path: Path) -> None:
    """One pass, exactly like the production voice stage."""
    audio = np.concatenate([a for _, _, a in pipeline(text, voice=voice, speed=CONFIG["speed"])])
    sf.write(path, audio, KOKORO_RATE)


def to_mp3(wav: Path, mp3: Path, bright: bool = True) -> None:
    flt = (BRIGHT + "," if bright else "") + "loudnorm=I=-14:TP=-1.5"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", flt,
                    "-b:a", "160k", str(mp3)], check=True)


def speed_up(wav: Path, factor: float) -> None:
    """Chatterbox speaks at its own pace; match the channel's faster delivery (pitch unchanged)."""
    tmp = wav.with_suffix(".fast.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", f"atempo={factor}",
                    str(tmp)], check=True)
    tmp.replace(wav)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    # 1) Our chosen Kokoro voice: the reference clip, and today's sound as the baseline.
    pipeline, voice = kokoro_voice()
    reference = OUT / "reference_voice11.wav"
    kokoro_say(pipeline, voice, REFERENCE_TEXT, reference)
    base = OUT / "1_kokoro_now.wav"
    kokoro_say(pipeline, voice, SCRIPT, base)
    to_mp3(base, OUT / "1_kokoro_now.mp3")
    base.unlink()
    print("[+] reference + kokoro baseline")

    import torch
    import torchaudio as ta

    # 2) Chatterbox copies voice #11 and performs the script with more emotion.
    from chatterbox.tts import ChatterboxTTS
    torch.manual_seed(7)
    model = ChatterboxTTS.from_pretrained(device="cpu")
    for name, (exag, cfg, temp) in CANDIDATES.items():
        try:
            wav = model.generate(SCRIPT, audio_prompt_path=str(reference),
                                 exaggeration=exag, cfg_weight=cfg, temperature=temp)
        except Exception as exc:
            print(f"[!] {name}: {exc}")
            continue
        path = OUT / f"{name}.wav"
        ta.save(str(path), wav, model.sr)
        speed_up(path, 1.08)
        to_mp3(path, OUT / f"{name}.mp3")
        path.unlink()
        print(f"[+] {name}")
    del model

    # 3) Chatterbox Turbo: faster model, no emotion dial, but natural sounds from text tags.
    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        turbo = ChatterboxTurboTTS.from_pretrained(device="cpu")
        wav = turbo.generate(SCRIPT_TURBO, audio_prompt_path=str(reference))
        path = OUT / "5_chatterbox_turbo_tags.wav"
        ta.save(str(path), wav, turbo.sr)
        speed_up(path, 1.08)
        to_mp3(path, OUT / "5_chatterbox_turbo_tags.mp3")
        path.unlink()
        print("[+] 5_chatterbox_turbo_tags")
    except Exception as exc:
        print(f"[!] turbo: {exc}")

    to_mp3(reference, OUT / "0_reference_voice11.mp3")
    reference.unlink()


if __name__ == "__main__":
    main()

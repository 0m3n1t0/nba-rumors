"""Voice audition, round 6: natural emotion that fits the meaning.

Feedback on the per-beat tones (round 5 engine, sample 3_chatterbox_exag08): the timbre is
right, but intonation and emotion still sound off for the content. Two things can cause
that, and this round tests both on the REAL script of the last run (Jason Kidd vs Doc Rivers),
with the tones the script writer gave each line:

  1. the emotion levels: the current ones are strong (tense 0.8, shocked 1.0). Chatterbox's
     own guidance is 0.5 for natural speech, 0.7+ only for dramatic lines;
  2. the reference clip Chatterbox copies the delivery FROM: today it is a flat, even
     sentence. A reference that itself goes up and down (a question, a calm line, a
     surprised line) teaches it a livelier, more human melody. Same voice #11 timbre.

  1_now.mp3                  what the channel sounds like today (per-beat tones, strong)
  2_natural.mp3              per-beat tones, milder and more natural levels
  3_natural_live_ref.mp3     2 + the livelier reference clip
  4_one_pass_live_ref.mp3    the whole script in ONE pass (one melody, no joins), moderate
                             emotion, livelier reference

Output: samples/*.mp3 (download the "voice-samples" artifact).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import tts  # noqa: E402  (the production voice code: same text fixes, trimming, mastering)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "samples"

# The real script of the last run (hook + beats, with the tones the writer gave them).
PARTS = [
    {"say": "Did Jason Kidd just fire back at Doc Rivers over Giannis Antetokounmpo's basketball IQ, "
            "and who actually gets him right?", "tone": "tense"},
    {"say": "Kidd went on ESPN and said it straight. \"I disagree with that. I think Giannis "
            "understands how to play the game.\"", "tone": "tense"},
    {"say": "But he was answering Rivers. On Bill Simmons' podcast, Rivers said Giannis doesn't "
            "necessarily have a super IQ, and he gave Spoelstra the credit for teaching it.", "tone": "serious"},
    {"say": "So Kidd, the coach who made Giannis a ball handler, called him one of the top five "
            "players in the league.", "tone": "tense"},
    {"say": "Honestly? Twenty-seven point three points a game... doesn't look dumb to me. Subscribe, "
            "we track every NBA rumor daily. So who's right, Kidd or Rivers?", "tone": "amused"},
]

# A reference that moves: a question, a calm line, a surprised line, a dry aside.
LIVE_REFERENCE = (
    "Wait, did he really just say that? Okay. So here's what happened. He walked up to the mic, "
    "totally calm, and then, boom! Nobody saw that coming. Honestly? I kind of love it."
)

STRONG = {"calm": [0.55, 0.35], "serious": [0.5, 0.4], "tense": [0.8, 0.3], "shocked": [1.0, 0.3],
          "amused": [0.75, 0.3]}
NATURAL = {"calm": [0.45, 0.5], "serious": [0.45, 0.5], "tense": [0.6, 0.4], "shocked": [0.75, 0.35],
           "amused": [0.6, 0.4]}


def perform(model, parts: list[dict], tones: dict, seed: int = 7) -> np.ndarray:
    """Same as production (tts.Performer.speak_parts): one take per beat in its tone."""
    import torch
    cb = tts.CONFIG["chatterbox"]
    gap = np.zeros(int(model.sr * cb.get("beat_gap", 0.18)), dtype=np.float32)
    pieces = []
    for k, p in enumerate(parts):
        exag, cfg = tones.get(p["tone"], [cb["exaggeration"], cb["cfg_weight"]])
        torch.manual_seed(seed + k)
        for attempt in range(3):
            wav = model.generate(tts.lower_caps(tts.speakable(p["say"])), exaggeration=exag,
                                 cfg_weight=cfg, temperature=cb["temperature"])
            clip = wav.squeeze(0).cpu().numpy().astype(np.float32)
            if not tts.cut_off(clip, model.sr):
                break
            torch.manual_seed(seed + k + 100 * (attempt + 1))
        pieces += [tts.trim_silence(clip, model.sr), gap]
    return np.concatenate(pieces[:-1])


def save(audio: np.ndarray, rate: int, name: str) -> None:
    wav = OUT / f"{name}.wav"
    sf.write(wav, np.concatenate([audio, np.zeros(int(rate * 0.3), dtype=np.float32)]), rate)
    tts.finish(wav, OUT / f"{name}.mp3", tts.CONFIG["chatterbox"]["tempo"])
    wav.unlink()
    print(f"[+] {name}")


def main() -> None:
    import torch
    from chatterbox.tts import ChatterboxTTS
    OUT.mkdir(exist_ok=True)
    pipeline, voice = tts.load_pipeline()
    speed = tts.CONFIG["speed"]
    flat_ref, live_ref = OUT / "ref_now.wav", OUT / "ref_live.wav"
    sf.write(flat_ref, tts.say_once(pipeline, voice, tts.REFERENCE_TEXT, speed), tts.RATE)
    sf.write(live_ref, tts.say_once(pipeline, voice, LIVE_REFERENCE, speed), tts.RATE)
    model = ChatterboxTTS.from_pretrained(device="cpu")

    model.prepare_conditionals(str(flat_ref), exaggeration=0.5)
    save(perform(model, PARTS, STRONG), model.sr, "1_now")
    save(perform(model, PARTS, NATURAL), model.sr, "2_natural")

    model.prepare_conditionals(str(live_ref), exaggeration=0.5)
    save(perform(model, PARTS, NATURAL), model.sr, "3_natural_live_ref")
    torch.manual_seed(7)
    whole = " ".join(p["say"] for p in PARTS)
    takes = []
    for chunk in tts.Performer.chunks(None, tts.lower_caps(tts.speakable(whole))):   # ~40 s max per take
        wav = model.generate(chunk, exaggeration=0.6, cfg_weight=0.45,
                             temperature=tts.CONFIG["chatterbox"]["temperature"])
        takes += [tts.trim_silence(wav.squeeze(0).cpu().numpy().astype(np.float32), model.sr),
                  np.zeros(int(model.sr * 0.12), dtype=np.float32)]
    save(np.concatenate(takes[:-1]), model.sr, "4_one_pass_live_ref")

    for ref in (flat_ref, live_ref):
        tts.finish(ref, OUT / f"0_{ref.stem}.mp3")
        ref.unlink()
    (OUT / "settings.json").write_text(json.dumps({"strong": STRONG, "natural": NATURAL,
                                                   "live_reference": LIVE_REFERENCE}, indent=2))


if __name__ == "__main__":
    main()

"""Stage 4: voice. Turn every ready script into narration audio.

Uses the voice chosen in the audition (config/voice.json), so every video sounds the same:
voice #11 (Kokoro, Bella 45 / Nicole 55) performed by Chatterbox with more emotion
(audition round 5, sample 3_chatterbox_exag08). Kokoro makes a short reference clip of
voice #11, Chatterbox copies that timbre and reads the script with real intonation.
If Chatterbox fails or garbles the text (checked by Whisper), the Short falls back to the
Kokoro voice, so a run never ends without narration.

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


# Reference clip for the voice copy (the same one the audition used): voice #11, lively.
REFERENCE_TEXT = (
    "Okay, so here's the thing about this league. Everybody wants to talk about the big names, "
    "but the stories that really matter? They're hiding in the details. And honestly, that's my "
    "favorite part. Let me show you what I mean!"
)
CHUNK_WORDS = 90      # longer scripts are read in two or more parts (Chatterbox reads ~40 s at most)
MIN_COVERAGE = 0.85   # Whisper must hear at least this share of the script's words


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


def cut_off(clip: np.ndarray, rate: int) -> bool:
    """True if the audio ends while still speaking (the last word lost its final sound):
    the last 80 ms are almost as loud as the speech itself instead of fading out."""
    tail = clip[-int(rate * 0.08):]
    if len(clip) < rate or not len(tail):
        return False
    frame = int(rate * 0.02)
    levels = [float(np.sqrt(np.mean(clip[i:i + frame] ** 2))) for i in range(0, len(clip) - frame, frame)]
    speech = float(np.median([v for v in levels if v > 0.01] or [0.0]))
    return speech > 0 and float(np.sqrt(np.mean(tail ** 2))) > 0.35 * speech


def trim_silence(clip: np.ndarray, rate: int) -> np.ndarray:
    """Chatterbox adds its own silence before and after a line; trimmed so the pause between
    beats is always the same short beat_gap. Generous margins keep every soft first and last
    sound (an "h", a fading "-s")."""
    frame = int(rate * 0.01)
    levels = np.array([float(np.sqrt(np.mean(clip[i:i + frame] ** 2)))
                       for i in range(0, max(len(clip) - frame, 1), frame)])
    if not len(levels) or levels.max() <= 0:
        return clip
    loud = np.where(levels > 0.03 * levels.max())[0]
    if not len(loud):
        return clip
    start = max(0, (loud[0] - 5) * frame)                    # keep 50 ms before the first sound
    end = min(len(clip), (loud[-1] + 1) * frame + int(rate * 0.15))   # and 150 ms after the last
    return clip[start:end]


class Performer:
    """Chatterbox with voice #11 as the reference: same timbre, livelier delivery."""

    def __init__(self, pipeline, voice):
        import torch
        from chatterbox.tts import ChatterboxTTS
        self.torch = torch
        cb = CONFIG["chatterbox"]
        self.cb = cb
        self.reference = AUDIO / "reference_voice11.wav"
        sf.write(self.reference, say_once(pipeline, voice, REFERENCE_TEXT, CONFIG["speed"]), RATE)
        self.model = ChatterboxTTS.from_pretrained(device="cpu")
        self.rate = self.model.sr
        # read the reference voice ONCE (not again for every beat): saves time per Short
        try:
            self.model.prepare_conditionals(str(self.reference), exaggeration=cb["exaggeration"])
            self.prompt = None
        except Exception as exc:
            print(f"[i] reference prepared per call: {exc}")
            self.prompt = str(self.reference)

    def chunks(self, text: str) -> list[str]:
        words = text.split()
        if len(words) <= CHUNK_WORDS:
            return [text]
        sentences = re.split(r"(?<=[.!?])\s+", text)
        n = -(-len(words) // CHUNK_WORDS)
        target = len(words) / n
        out, cur = [], []
        for sent in sentences:
            if cur and len(" ".join(cur + [sent]).split()) > target * 1.15:
                out.append(" ".join(cur))
                cur = []
            cur.append(sent)
        return out + ([" ".join(cur)] if cur else [])

    def speak_parts(self, parts: list[dict], seed: int) -> np.ndarray:
        """Each beat performed in the emotion its words call for (the script's "tone"), instead
        of one emotion level for the whole Short: calm facts stay calm, only the twist sounds
        shocked. A very short beat joins the next one (Chatterbox needs a few words to act)."""
        cb, tones = self.cb, CONFIG.get("tones", {})
        groups = []
        for k, p in enumerate(parts):
            say = p["say"].strip()
            tone = p.get("tone") or ("tense" if k == 0 else "calm")
            if groups and groups[-1]["carry"]:
                say, tone = groups[-1]["say"] + " " + say, tone
                groups.pop()
            groups.append({"say": say, "tone": tone, "carry": len(say.split()) < 5 and k < len(parts) - 1})
        gap = np.zeros(int(self.rate * cb.get("beat_gap", 0.18)), dtype=np.float32)
        pieces = []
        for g_no, g in enumerate(groups):
            exag, cfg = tones.get(g["tone"], [cb["exaggeration"], cb["cfg_weight"]])
            self.torch.manual_seed(seed + g_no)
            for chunk in self.chunks(lower_caps(speakable(g["say"]))):
                for attempt in range(3):
                    wav = self.model.generate(chunk, audio_prompt_path=self.prompt,
                                              exaggeration=exag, cfg_weight=cfg,
                                              temperature=cb["temperature"])
                    clip = wav.squeeze(0).cpu().numpy().astype(np.float32)
                    if not cut_off(clip, self.rate):
                        break
                    print(f"[!] beat {g_no}: the voice stopped mid-sound, generating it again")
                    self.torch.manual_seed(seed + g_no + 100 * (attempt + 1))
                pieces += [trim_silence(clip, self.rate), gap]
        return np.concatenate(pieces[:-1])

    def speak(self, text: str, seed: int) -> np.ndarray:
        cb = self.cb
        self.torch.manual_seed(seed)
        gap = np.zeros(int(self.rate * 0.12), dtype=np.float32)
        pieces = []
        for chunk in self.chunks(lower_caps(speakable(text))):
            wav = self.model.generate(chunk, audio_prompt_path=self.prompt,
                                      exaggeration=cb["exaggeration"], cfg_weight=cb["cfg_weight"],
                                      temperature=cb["temperature"])
            pieces += [wav.squeeze(0).cpu().numpy().astype(np.float32), gap]
        return np.concatenate(pieces[:-1])


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


def finish(wav: Path, mp3: Path, tempo: float = 1.0) -> None:
    parts = [f"atempo={tempo}"] if tempo != 1.0 else []
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


def duration_of(mp3: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(mp3)], check=True, capture_output=True, text=True).stdout
    return round(float(out.strip()), 2)


def coverage(text: str, words: list[dict]) -> float:
    """Share of the script's words that Whisper actually heard (catches skipped or garbled parts)."""
    import difflib
    script = tokens(lower_caps(speakable(text)))
    heard = [t for w in words for t in tokens(w["word"])]
    if not script:
        return 1.0
    matched = sum(b.size for b in difflib.SequenceMatcher(None, script, heard, autojunk=False).get_matching_blocks())
    return matched / len(script)


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
    import time
    pipeline, voice = load_pipeline()
    performer = None
    if CONFIG.get("engine") == "chatterbox":
        try:
            performer = Performer(pipeline, voice)
        except Exception as exc:
            print(f"[!] Chatterbox could not start, using the Kokoro voice: {exc}")

    lines = ["## 🎙️ Voice", "", "| Short | Ready | Length | Beats | Engine | Words heard | Time |",
             "|---|---|---|---|---|---|---|"]
    for path in scripts:
        short = json.loads(path.read_text(encoding="utf-8"))
        parts = [{"say": short["hook"]["text"], "on_screen": "HOOK", "tone": "tense"}] + short["beats"]
        text = " ".join(p["say"].strip() for p in parts)
        name = path.stem
        wav, mp3 = AUDIO / f"{name}.wav", AUDIO / f"{name}.mp3"
        began = time.time()

        # Chatterbox first (two tries with different seeds), Kokoro if it fails or garbles words
        attempts = [("chatterbox", s) for s in (CONFIG["chatterbox"]["seed"], CONFIG["chatterbox"]["seed"] + 1)] \
            if performer else []
        attempts.append(("kokoro", 0))
        for engine, seed in attempts:
            try:
                if engine == "chatterbox":
                    clip = (performer.speak_parts(parts, seed) if CONFIG.get("tones")
                            else performer.speak(text, seed))
                    rate, tempo = performer.rate, CONFIG["chatterbox"]["tempo"]
                else:
                    clip, rate, tempo = speak(pipeline, voice, text), RATE, 1.0
            except Exception as exc:
                print(f"[!] {name}: {engine} failed: {exc}")
                continue
            tail = np.zeros(int(rate * 0.3), dtype=np.float32)
            sf.write(wav, np.concatenate([clip, tail]), rate)
            finish(wav, mp3, tempo)
            wav.unlink()
            words = word_times(mp3)
            heard = coverage(text, words)
            if engine == "kokoro" or heard >= MIN_COVERAGE:
                break
            print(f"[!] {name}: {engine} seed {seed} garbled the text ({heard:.0%} of words heard), retrying")

        duration = duration_of(mp3)
        beats = beat_times(parts, words, duration)
        timing = {"duration": duration, "beats": beats, "words": words, "engine": engine}
        (AUDIO / f"{name}.timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")
        ready = "✅" if short.get("ready") else "⚠️"
        engine_note = "Chatterbox (voice #11)" if engine == "chatterbox" else ("Kokoro (fallback)" if performer else "Kokoro")
        lines.append(f"| {short['n']}: {short['headline'][:60]} | {ready} | {duration:.0f}s | {len(beats)} | "
                     f"{engine_note} | {heard:.0%} | {(time.time() - began) / 60:.1f} min |")
        print(f"[+] {name}: {duration:.1f}s, {engine}, {len(words)} words timed, {heard:.0%} heard")

    text = "\n".join(lines)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

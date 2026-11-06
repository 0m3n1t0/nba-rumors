"""Stage 5: render each Short as a vertical MP4 (1080x1920, 30 fps). No cards.

Every beat shows the real visual media.py picked for it:
  photo  a real photo of the person (Wikimedia Commons), with a slow Ken Burns move
  video  real footage (Pixabay), muted, filled to 9:16
On top: a small "NBA RUMORS" tag, the hook words on the first beat (also the thumbnail),
word-by-word captions driven by the narration timing, a progress bar, and the media credit.
If a beat has no media, it gets the team-colour background.

Output: data/video/short_N.mp4 + short_N_thumb.png
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCRIPTS, AUDIO, VIDEO, MEDIA = DATA / "scripts", DATA / "audio", DATA / "video", DATA / "media"
W, H, FPS = 1080, 1920, 30
FONT_DIR = ROOT / "fonts"
BRAND = "NBA RUMORS"

# Team colors (primary, secondary). Our own colour blocks, no logos.
TEAMS = {
    "hawks": ("#C8102E", "#FDB927"), "celtics": ("#007A33", "#BA9653"), "nets": ("#000000", "#FFFFFF"),
    "hornets": ("#1D1160", "#00788C"), "bulls": ("#CE1141", "#000000"), "cavaliers": ("#860038", "#FDBB30"),
    "cavs": ("#860038", "#FDBB30"), "mavericks": ("#00538C", "#B8C4CA"), "mavs": ("#00538C", "#B8C4CA"),
    "nuggets": ("#0E2240", "#FEC524"), "pistons": ("#C8102E", "#1D42BA"), "warriors": ("#1D428A", "#FFC72C"),
    "rockets": ("#CE1141", "#C4CED4"), "pacers": ("#002D62", "#FDBB30"), "clippers": ("#C8102E", "#1D428A"),
    "lakers": ("#552583", "#FDB927"), "grizzlies": ("#5D76A9", "#12173F"), "heat": ("#98002E", "#F9A01B"),
    "bucks": ("#00471B", "#EEE1C6"), "timberwolves": ("#0C2340", "#78BE20"), "pelicans": ("#0C2340", "#C8102E"),
    "knicks": ("#006BB6", "#F58426"), "thunder": ("#007AC1", "#EF3B24"), "magic": ("#0077C0", "#C4CED4"),
    "76ers": ("#006BB6", "#ED174C"), "sixers": ("#006BB6", "#ED174C"), "suns": ("#1D1160", "#E56020"),
    "blazers": ("#E03A3E", "#000000"), "kings": ("#5A2D81", "#63727A"), "spurs": ("#000000", "#C4CED4"),
    "raptors": ("#CE1141", "#000000"), "jazz": ("#002B5C", "#F9A01B"), "wizards": ("#002B5C", "#E31837"),
}
DEFAULT = ("#111827", "#F97316")  # channel colours when no team is named


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for path in [FONT_DIR / "Anton-Regular.ttf" if bold else FONT_DIR / "Inter.ttf",
                 Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                 Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


def team_colors(text: str) -> tuple[str, str]:
    for name, colors in TEAMS.items():
        if re.search(rf"\b{name}\b", text, re.I):
            return colors
    return DEFAULT


def gradient(c1: str, c2: str) -> Image.Image:
    top, bottom = Image.new("RGB", (W, H), c1), Image.new("RGB", (W, H), "#05070C")
    mask = Image.linear_gradient("L").resize((W, H))
    img = Image.composite(bottom, top, mask)
    glow = Image.new("RGB", (W, H), c2)
    gmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gmask).ellipse((W * 0.15, H * 0.12, W * 0.85, H * 0.5), fill=90)
    return Image.composite(glow, img, gmask.filter(ImageFilter.GaussianBlur(160)))


def photo_bg(path: Path, focus: list | None = None) -> Image.Image:
    """Real photo, cropped to 9:16 around the subject Claude marked, a little darker so captions read."""
    fx, fy = (focus or [0.5, 0.3])[:2]
    img = ImageOps.fit(Image.open(path).convert("RGB"), (W, H), Image.LANCZOS, centering=(fx, fy))
    return ImageEnhance.Brightness(img).enhance(0.8)


def wrap_px(d: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if d.textlength(test, font=f) <= max_w or not line:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def overlay(item: dict | None, hook_text: str, accent: str) -> Image.Image:
    """Transparent layer over the footage: small brand tag, credit, and (beat 0 only) the hook
    words. Shade at top and bottom keeps text readable on any picture."""
    ramp = np.linspace(0, 1, H)[:, None].repeat(W, axis=1)
    top = np.clip((0.28 - ramp) / 0.28, 0, 1) * 170        # dark band behind the brand + hook
    bottom = np.clip((ramp - 0.62) / 0.38, 0, 1) * 200     # dark band behind captions + credit
    alpha = np.maximum(top, bottom).astype("uint8")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), (0, 0, W, H), Image.fromarray(alpha, "L"))
    d = ImageDraw.Draw(img)
    tag = font(40)
    tw = d.textlength(BRAND, font=tag)
    d.rounded_rectangle(((W - tw) / 2 - 24, 170, (W + tw) / 2 + 24, 230), radius=14, fill=accent)
    d.text(((W - tw) / 2, 176), BRAND, font=tag, fill="#000000" if accent != "#000000" else "#FFFFFF")
    if hook_text:
        size = 150
        while True:
            f = font(size)
            lines = wrap_px(d, hook_text.upper(), f, W - 140)
            if len(lines) <= 3 or size <= 70:
                break
            size = int(size * 0.9)
        y = 300
        for line in lines[:3]:
            w = d.textlength(line, font=f)
            d.text(((W - w) / 2, y), line, font=f, fill="#FFFFFF", stroke_width=6, stroke_fill="#000000")
            y += int(size * 1.1)
    if item:
        cf = font(28, bold=False)
        what = "Photo" if item["kind"] == "photo" else "Video"
        label = f"{what}: {item['author'][:40]} / {item['license']} / {item['source']}"
        d.text(((W - d.textlength(label, font=cf)) / 2, 1760), label, font=cf, fill="#D1D5DB",
               stroke_width=2, stroke_fill="#000000")
    return img


# ---------- captions (ASS, word by word) ----------

def ass_time(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def script_words(words: list[dict], beats: list[dict]) -> list[dict]:
    """Captions spelled like the SCRIPT (not like speech recognition heard it: "Dylan" -> "Dillon",
    "warrior's son's" -> "Warriors-Suns"), timed by the recognised words."""
    import difflib
    text = [t for b in beats for t in b.get("say", "").split()]
    if not text or not words:
        return words
    a, b = [norm(w["word"]) for w in words], [norm(t) for t in text]
    out: list[dict] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
            out += [{"word": text[j1 + k], "start": words[i1 + k]["start"], "end": words[i1 + k]["end"]}
                    for k in range(i2 - i1)]
        elif op == "replace":  # different word counts: spread the script words over that time
            t0, t1 = words[i1]["start"], words[i2 - 1]["end"]
            n = j2 - j1
            out += [{"word": text[j1 + k], "start": round(t0 + (t1 - t0) * k / n, 2),
                     "end": round(t0 + (t1 - t0) * (k + 1) / n, 2)} for k in range(n)]
        elif op == "insert" and out:  # script word the recogniser missed: glue to the previous
            out[-1]["word"] += " " + " ".join(text[j1:j2])
        # "delete": recogniser heard something the script does not have -> drop it
    return out or words


def captions(words: list[dict], path: Path, accent: str) -> None:
    """Big viral-style captions: 2 words at a time, centred, the spoken word in the accent
    colour with a small pop."""
    hex6 = accent.lstrip("#")
    bgr = f"&H00{hex6[4:6]}{hex6[2:4]}{hex6[0:2]}"
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, "
        "Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        "Style: Cap,Anton,150,&H00FFFFFF,&H00000000,&HA0000000,1,10,5,5,40,40,0\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
    )
    events = []
    size = 2
    groups = [words[i:i + size] for i in range(0, len(words), size)]
    starts = [w["start"] for w in words]
    for gi, g in enumerate(groups):
        for j, w in enumerate(g):
            idx = gi * size + j
            nxt = starts[idx + 1] if idx + 1 < len(starts) else w["end"] + 0.4
            end = min(nxt, w["end"] + 0.6)  # never overlaps the next caption
            parts = []
            for k, x in enumerate(g):
                word = re.sub(r"[{}\\]", "", x["word"]).upper()
                if k == j:
                    parts.append(f"{{\\c{bgr}\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}}{word}"
                                 f"{{\\c&H00FFFFFF\\fscx100\\fscy100}}")
                else:
                    parts.append(word)
            chars = len(" ".join(x["word"] for x in g))
            fs = min(150, int(150 * 13 / max(13, chars)))  # long words shrink, never run off screen
            events.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Cap,"
                          f"{{\\pos(540,1240)\\fs{fs}}}{' '.join(parts)}")
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


# ---------- assembly ----------

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def still_segment(bg: Image.Image, layer: Image.Image, dur: float, seg: Path, work: Path, i: int,
                  zoom_in: bool) -> None:
    """Photo with a slow Ken Burns move (in or out), overlay on top (not zoomed)."""
    bg_path, ov_path = work / f"bg_{i}.jpg", work / f"ov_{i}.png"
    bg.save(bg_path, quality=92)
    layer.save(ov_path)
    frames = int(round(dur * FPS))
    z = f"1+0.08*on/{frames}" if zoom_in else f"1.08-0.08*on/{frames}"
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(bg_path), "-i", str(ov_path), "-filter_complex",
         f"[0:v]scale={W * 2}:{H * 2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
         f"d={frames}:s={W}x{H}:fps={FPS},setsar=1[b];[b][1:v]overlay=0:0",
         "-frames:v", str(frames), "-an", *ENC, str(seg)])


def video_segment(item: dict, layer: Image.Image, dur: float, seg: Path, work: Path, i: int) -> None:
    """Real footage, muted, filled to 9:16, looped if shorter than the beat."""
    ov_path = work / f"ov_{i}.png"
    layer.save(ov_path)
    fx, fy = (item.get("focus") or [0.5, 0.5])[:2]
    start = float(item.get("start") or 0)
    run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-stream_loop", "-1", "-i", str(ROOT / item["file"]),
         "-i", str(ov_path), "-filter_complex",
         f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
         f"crop={W}:{H}:(iw-{W})*{fx:.3f}:(ih-{H})*{fy:.3f},"
         f"eq=brightness=-0.05:saturation=1.1,fps={FPS},setsar=1[b];[b][1:v]overlay=0:0",
         "-t", f"{dur:.3f}", "-an", *ENC, str(seg)])


ERRORS: list[str] = []


def render(short: dict, timing: dict, mp3: Path, out: Path, work: Path,
           media: list | None = None, music: dict | None = None) -> list[str]:
    work.mkdir(parents=True, exist_ok=True)
    colors = team_colors(" ".join([short["headline"]] + [b.get("say", "") for b in short["beats"]]))
    accent = colors[1] if colors[1] not in ("#000000", "#FFFFFF") else "#FACC15"
    beats = timing["beats"]
    media = list(media or []) + [None] * len(beats)
    segments, log = [], []
    for i, b in enumerate(beats):
        start = 0.0 if i == 0 else b["start"]
        end = beats[i + 1]["start"] if i + 1 < len(beats) else timing["duration"] + 0.4
        dur = max(0.6, end - start)
        item = media[i]
        hook = (short.get("thumbnail_text") or short["hook"]["text"]) if i == 0 else ""
        layer = overlay(item, hook, accent)
        seg = work / f"seg_{i}.mp4"
        failed = False
        if item and item["kind"] == "video":
            try:
                video_segment(item, layer, dur, seg, work, i)
                segments.append(seg)
                log.append("🎥")
                if i == 0:
                    run(["ffmpeg", "-y", "-i", str(seg), "-frames:v", "1", str(work / "thumb.png")])
                continue
            except subprocess.CalledProcessError as exc:
                err = exc.stderr.decode(errors='replace')[-300:]
                print(f"[!] clip failed on beat {i}: {err}")
                failed = True
                ERRORS.append(f"{out.stem} beat {i}: {err.splitlines()[-1] if err else 'ffmpeg error'}")
                item = None
                layer = overlay(None, hook, accent)
        bg = photo_bg(ROOT / item["file"], item.get("focus")) if item else gradient(*colors)
        log.append("❌🎥→⬛" if failed else ("📷" if item else "⬛"))
        still_segment(bg, layer, dur, seg, work, i, zoom_in=i % 2 == 0)
        if i == 0:
            Image.alpha_composite(bg.convert("RGBA"), layer).convert("RGB").save(work / "thumb.png")
        segments.append(seg)
    (work / "list.txt").write_text("".join(f"file '{s.name}'\n" for s in segments))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"), "-c", "copy",
         str(work / "visuals.mp4")])
    ass = work / "captions.ass"
    words = script_words(timing["words"], timing["beats"])
    captions(words, ass, accent)
    log.append(f"captions: {len(words)} words")
    total = timing["duration"] + 0.4
    bar = f"drawbox=x=0:y=0:w='iw*t/{total:.2f}':h=14:color={accent.replace('#', '0x')}@1:t=fill"
    fonts = f":fontsdir={FONT_DIR}" if FONT_DIR.exists() else ""
    vf = f"[0:v]{bar},ass={ass}{fonts}[v]"
    if music and (ROOT / music["file"]).exists():
        # music: start a bit in (skip intros), quiet, ducks under the voice, fades in and out
        offset = min(15.0, max(0.0, music.get("duration", 0) - total - 1))
        af = (f"[1:a]asplit=2[voice][key];"
              f"[2:a]atrim=start={offset:.1f},asetpts=PTS-STARTPTS,volume=0.22,"
              f"afade=t=in:d=0.8,afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5[bed];"
              f"[bed][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
              f"[voice][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3), "-stream_loop", "-1", "-i", str(ROOT / music["file"])]
        log.append("music: " + music.get("mood", ""))
    else:
        af = "[1:a]anull[a]"
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3)]
        log.append("music: none")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart", str(out)])
    return log


def main() -> None:
    VIDEO.mkdir(parents=True, exist_ok=True)
    rendered = []
    for script_path in sorted(SCRIPTS.glob("short_*.json")):
        name = script_path.stem
        timing_path, mp3 = AUDIO / f"{name}.timing.json", AUDIO / f"{name}.mp3"
        if not timing_path.exists() or not mp3.exists():
            print(f"[!] {name}: no narration, skipped")
            continue
        short = json.loads(script_path.read_text(encoding="utf-8"))
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        out = VIDEO / f"{name}.mp4"
        media_path = MEDIA / f"{name}.json"
        media = json.loads(media_path.read_text(encoding="utf-8")) if media_path.exists() else []
        music_path = MEDIA / f"{name}_music.json"
        music = json.loads(music_path.read_text(encoding="utf-8")) if music_path.exists() else None
        try:
            log = render(short, timing, mp3, out, VIDEO / f"_{name}", media, music)
        except subprocess.CalledProcessError as exc:
            print(f"[!] {name}: ffmpeg failed: {exc.stderr.decode(errors='replace')[-800:]}")
            continue
        # keep the hook card as a still (preview / thumbnail)
        (VIDEO / f"_{name}" / "thumb.png").replace(VIDEO / f"{name}_thumb.png")
        rendered.append((name, short, timing, log))
        print(f"[+] {name}: {out.stat().st_size / 1e6:.1f} MB, {timing['duration']:.1f}s")
    lines = ["## 🎬 Video", "", "| Short | length | ready | beats (🎥 clip 📷 photo ⬛ empty) | title |",
             "|---|---|---|---|---|"]
    for name, short, timing, log in rendered:
        title = short["titles"][0]["title"] if short.get("titles") else short["headline"]
        lines.append(f"| {name} | {timing['duration']:.0f}s | {'✅' if short.get('ready') else '⚠️'} | "
                     f"{' '.join(log)} | {title} |")
    if ERRORS:
        lines += ["", "**Render errors:**", ""] + [f"- `{e}`" for e in ERRORS]
    text = "\n".join(lines)
    print(text)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if not rendered:
        sys.exit("[!] No video was rendered.")


if __name__ == "__main__":
    main()

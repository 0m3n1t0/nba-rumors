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
import math
import os
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


FG_W, FG_MAX_H, FG_CY = 1296, 1100, 800  # landscape media: shown whole, a bit wider than the screen


# ---------- nothing ever repeats inside one Short ----------
# The same photo can arrive twice under different addresses (Wikimedia Commons and Openverse
# index the same Flickr picture; a cropped re-upload has a new page). So pictures are compared
# by what they LOOK like (a 64-bit difference hash), not by their address.
SAME_PICTURE = 12   # bits of 64 that may differ and still be the same photo (crop, resize, recompress)


def picture_hash(path: Path) -> int | None:
    try:
        with Image.open(path) as im:
            g = im.convert("L").resize((9, 8), Image.LANCZOS)
        px = list(g.getdata())
        return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
    except Exception:
        return None


def seen_before(h: int | None, hashes: list[int]) -> bool:
    return h is not None and any(bin(h ^ x).count("1") <= SAME_PICTURE for x in hashes)


def item_key(it: dict) -> str:
    return str(it.get("id") or it.get("page") or it.get("url") or it.get("file"))


def no_repeats(items: list) -> list:
    """Every picture and every clip appears ONCE per Short. Later duplicates are dropped; a beat
    left with nothing becomes empty (filled with a NEW picture later, never an old one)."""
    hashes: list[int] = []
    keys: set[str] = set()
    out = []
    for it in items:
        if not it:
            out.append(None)
            continue
        pool = [it] + [a for a in (it.get("alts") or ([it["alt"]] if it.get("alt") else [])) if a]
        keep = []
        for p in pool:
            k = item_key(p)
            h = picture_hash(ROOT / p["file"]) if p.get("kind") == "photo" and p.get("file") else None
            if k in keys or seen_before(h, hashes):
                continue
            keys.add(k)
            if h is not None:
                hashes.append(h)
            keep.append(p)
        if not keep:
            out.append(None)
            continue
        main = {**keep[0], "alts": keep[1:], "alt": keep[1] if len(keep) > 1 else None}
        out.append(main)
    return out


FACE_UNDER_HOOK = 720   # y of the face in the hook shot: below the hook words, above the captions


def photo_bg(path: Path, focus: list | None = None, hook: bool = False) -> Image.Image:
    """Real photo. A tall photo fills the 9:16 frame. A wide photo is NOT cut down to a 9:16
    strip (that cuts heads and faces): it is shown almost whole, centred above the captions,
    over a blurred, darkened copy of itself (the standard Shorts look).
    hook=True (the opening shot, with the big hook words at the top): the photo is placed so
    the face sits BELOW the words, never hidden behind them - the face is what stops the scroll."""
    fx, fy = (focus or [0.5, 0.3])[:2]
    src = Image.open(path).convert("RGB")
    if src.width / src.height <= 0.8:
        if not hook:
            img = ImageOps.fit(src, (W, H), Image.LANCZOS, centering=(fx, fy))
            return ImageEnhance.Brightness(img).enhance(0.8)
        scale = max(W / src.width, H / src.height)
        face = fy * src.height * scale
        if face < FACE_UNDER_HOOK:            # face too high to crop down to: zoom in a little
            scale *= min(1.35, FACE_UNDER_HOOK / max(face, 1))
        sw, sh = round(src.width * scale), round(src.height * scale)
        big = src.resize((sw, sh), Image.LANCZOS)
        left = min(max(0, round(fx * sw - W / 2)), sw - W)
        top = min(max(0, round(fy * sh - FACE_UNDER_HOOK)), sh - H)
        return ImageEnhance.Brightness(big.crop((left, top, left + W, top + H))).enhance(0.8)
    bg = ImageOps.fit(src, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = src.resize((FG_W, round(src.height * FG_W / src.width)), Image.LANCZOS)
    left = round((fg.width - W) * fx)
    top = round(max(0, fg.height - FG_MAX_H) * fy)
    fg = fg.crop((left, top, left + W, top + min(fg.height, FG_MAX_H)))
    y = max(120, FG_CY - fg.height // 2)
    if hook:   # the face (fy of the band) lands under the hook words
        y = min(max(120, round(FACE_UNDER_HOOK - fy * fg.height)), H - fg.height - 200)
    bg.paste(ImageEnhance.Brightness(fg).enhance(0.95), (0, y))
    return bg


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


def cta_card(accent: str) -> Image.Image:
    """Subscribe prompt for the end of every Short: a red pill with the value line, above the
    captions and inside the Shorts safe zone."""
    # a plain, calm background instead of the last picture: the channel logo goes on it as soon
    # as assets/logo.png exists in the repo (until then it stays blank)
    img = Image.new("RGBA", (W, H), (11, 11, 14, 255))
    logo_path = ROOT / "assets" / "logo.png"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((520, 520), Image.LANCZOS)
            img.alpha_composite(logo, ((W - logo.width) // 2, 820 - logo.height))
        except OSError:
            pass
    d = ImageDraw.Draw(img)
    big, small = font(76), font(44)
    t1, t2 = "SUBSCRIBE", "DAILY NBA DRAMA & RUMORS"
    w = max(d.textlength(t1, font=big), d.textlength(t2, font=small)) + 120
    x0, y0 = (W - w) / 2, 860
    d.rounded_rectangle((x0, y0, x0 + w, y0 + 190), radius=40, fill="#E62117", outline="#FFFFFF", width=6)
    d.text(((W - d.textlength(t1, font=big)) / 2, y0 + 22), t1, font=big, fill="#FFFFFF")
    d.text(((W - d.textlength(t2, font=small)) / 2, y0 + 118), t2, font=small, fill=accent if accent != "#E62117" else "#FFFFFF")
    return img


def overlay(item: dict | None, hook_text: str, accent: str) -> Image.Image:
    """Transparent layer over the footage: small brand tag, credit, and (beat 0 only) the hook
    words. Shade at top and bottom keeps text readable on any picture."""
    ramp = np.linspace(0, 1, H)[:, None].repeat(W, axis=1)
    top = np.clip((0.24 - ramp) / 0.24, 0, 1) * 170        # dark band behind the brand + hook
    bottom = np.clip((ramp - 0.62) / 0.38, 0, 1) * 200     # dark band behind captions + credit
    alpha = np.maximum(top, bottom).astype("uint8")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), (0, 0, W, H), Image.fromarray(alpha, "L"))
    d = ImageDraw.Draw(img)
    tag = font(40)
    tw = d.textlength(BRAND, font=tag)
    d.rounded_rectangle(((W - tw) / 2 - 24, 150, (W + tw) / 2 + 24, 210), radius=14, fill=accent)
    d.text(((W - tw) / 2, 156), BRAND, font=tag, fill="#000000" if accent != "#000000" else "#FFFFFF")
    if hook_text:
        # high and compact: the words sit right under the brand tag and the face stays free
        # below them (the face is what stops the scroll, the words say why)
        size = 112
        while True:
            f = font(size)
            lines = wrap_px(d, hook_text.upper(), f, W - 140)
            if len(lines) <= 2 or size <= 64:
                break
            size = int(size * 0.9)
        y = 238
        for line in lines[:2]:
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


def frame_focus(path: Path, focus: list | None) -> tuple[float, float]:
    """Where the face is in the finished 9:16 frame (same layout rules as photo_bg)."""
    fx, fy = (focus or [0.5, 0.3])[:2]
    with Image.open(path) as src:
        tall = src.width / src.height <= 0.8
    return (fx, fy) if tall else (0.5, FG_CY / H)


def still_segment(bg: Image.Image, layer: Image.Image, dur: float, seg: Path, work: Path, i,
                  zoom_in: bool, close: tuple[float, float] | None = None) -> None:
    """Photo with a slow Ken Burns move (in or out), overlay on top (not zoomed).
    close=(fx, fy): a tighter shot of the same photo framed on the face, so even one photo
    changes the picture every ~3 seconds (a "punch-in" cut, like real Shorts editors do)."""
    bg_path, ov_path = work / f"bg_{i}.jpg", work / f"ov_{i}.png"
    bg.save(bg_path, quality=92)
    layer.save(ov_path)
    frames = int(round(dur * FPS))
    # punch-in on the cut (first 6 frames 1.10 -> 1.0), then a slow Ken Burns move
    punch = "if(lt(on,6),0.10*(1-on/6),0)"
    z = (f"1+0.08*on/{frames}+{punch}" if zoom_in else f"1.08-0.08*on/{frames}+{punch}")
    x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if close:
        z = f"1.30+0.06*on/{frames}+{punch}"
        x, y = f"(iw-iw/zoom)*{close[0]:.3f}", f"(ih-ih/zoom)*{max(0.0, close[1] - 0.08):.3f}"
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(bg_path), "-i", str(ov_path), "-filter_complex",
         f"[0:v]scale={W * 2}:{H * 2},zoompan=z='{z}':x='{x}':y='{y}':"
         f"d={frames}:s={W}x{H}:fps={FPS},setsar=1[b];[b][1:v]overlay=0:0",
         "-frames:v", str(frames), "-an", *ENC, str(seg)])


def video_segment(item: dict, layer: Image.Image, dur: float, seg: Path, work: Path, i) -> None:
    """Real footage, muted, filled to 9:16. Never looped (a loop would show the same frames
    twice): a clip shorter than its shot holds its last frame for the rest."""
    ov_path = work / f"ov_{i}.png"
    layer.save(ov_path)
    fx, fy = (item.get("focus") or [0.5, 0.5])[:2]
    start = float(item.get("start") or 0)
    src = str(ROOT / item["file"])
    try:
        vw, vh = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                          "stream=width,height", "-of", "csv=p=0", src],
                                         capture_output=True, text=True).stdout.strip().split(",")[:2])
    except ValueError:
        vw, vh = 16, 9
    if vw / max(vh, 1) <= 0.8:  # tall clip: fill the frame around the subject
        frame = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
                 f"crop={W}:{H}:(iw-{W})*{fx:.3f}:(ih-{H})*{fy:.3f},")
    else:  # wide clip: shown almost whole over a blurred copy, so heads and faces are never cut
        frame = (f"[0:v]fps={FPS},split=2[a][c];"
                 f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"boxblur=25:3,eq=brightness=-0.3[bgv];"
                 f"[c]scale={FG_W}:-2,crop=w={W}:h='min(ih,{FG_MAX_H})':x='(iw-{W})*{fx:.3f}':"
                 f"y='(ih-min(ih,{FG_MAX_H}))*{fy:.3f}'[fg];"
                 f"[bgv][fg]overlay=0:'{FG_CY}-h/2',")
    run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", src,
         "-i", str(ov_path), "-filter_complex",
         frame +
         f"eq=brightness=-0.05:saturation=1.1,fps={FPS},tpad=stop_mode=clone:stop_duration={dur:.2f},"
         # punch-in on the cut: starts 10% bigger and settles in 0.2 s
         f"scale=w='trunc({W}*(1+0.10*max(0,1-t/0.2))/2)*2':h=-2:eval=frame,crop={W}:{H},"
         f"setsar=1[b];[b][1:v]overlay=0:0",
         "-t", f"{dur:.3f}", "-an", *ENC, str(seg)])


ERRORS: list[str] = []
MUSIC_UNDER_DB = float(os.environ.get("MUSIC_UNDER_DB", "14"))  # music bed this many dB under the voice


PHOTO_SHOT, CLIP_SHOT, MIN_SHOT = 3.0, 4.0, 1.5   # seconds (best practice: a change every 2-3 s)


def sharp_enough(item: dict) -> bool:
    """Enough pixels for a ~1.3x punch-in without visible blur."""
    try:
        with Image.open(ROOT / item["file"]) as im:
            w, h = im.size
    except (OSError, KeyError):
        return False
    return h >= 1200 if w / h <= 0.8 else w >= 1000


def plan_shots(main: dict | None, dur: float) -> list[tuple]:
    """Split a beat into shots, each a DIFFERENT picture: a photo at most ~3 s, a clip ~4 s
    (motion holds the eye longer). The beat's other pictures are used in order; the same photo
    is never shown twice. When the pictures run out, the last one simply stays on screen
    longer (a photo with its slow move, a clip keeps playing): nothing ever repeats."""
    if not main:
        return [(None, dur, False)]
    pool = [main] + [a for a in (main.get("alts") or [main.get("alt")]) if a]
    limit = CLIP_SHOT if main["kind"] == "video" else PHOTO_SHOT
    n = max(1, min(math.ceil(dur / limit), int(dur // MIN_SHOT) or 1))
    shots = [[pool[k], 0.0, False] for k in range(min(n, len(pool)))]   # each picture once
    each = round(dur / len(shots), 2)
    for s in shots:
        s[1] = each
    shots[-1][1] = round(dur - each * (len(shots) - 1), 2)
    # a clip used again continues where its last shot ended (never the same frames twice)
    played: dict[int, float] = {}
    for s in shots:
        if s[0]["kind"] == "video":
            key = id(s[0])
            if key in played:
                s[0] = {**s[0], "start": float(s[0].get("start") or 0) + played[key]}
            played[key] = played.get(key, 0.0) + s[1]
    return [tuple(s) for s in shots]


def render(short: dict, timing: dict, mp3: Path, out: Path, work: Path,
           media: list | None = None, music: dict | None = None) -> list[str]:
    work.mkdir(parents=True, exist_ok=True)
    colors = team_colors(" ".join([short["headline"]] + [b.get("say", "") for b in short["beats"]]))
    accent = colors[1] if colors[1] not in ("#000000", "#FFFFFF") else "#FACC15"
    beats = timing["beats"]
    media = no_repeats(list(media or []) + [None] * len(beats))   # last safety net: nothing twice
    # a beat with no picture of its own continues the previous beat's picture (one longer
    # shot): never a repeated picture, never a plain colour card
    runs = []
    for i, b in enumerate(beats):
        start = 0.0 if i == 0 else b["start"]
        end = beats[i + 1]["start"] if i + 1 < len(beats) else timing["duration"] + 0.4
        if media[i] is None and runs and runs[-1][1] is not None:
            runs[-1][2] += max(0.6, end - start)
        else:
            runs.append([i, media[i], max(0.6, end - start)])
    segments, log = [], []
    for i, main, dur in runs:
        hook = (short.get("thumbnail_text") or short["hook"]["text"]) if i == 0 else ""
        shots = plan_shots(main, dur)
        marks = []
        for s_no, (item, sdur, close) in enumerate(shots):
            tag = f"{i}_{s_no}"
            layer = overlay(item, hook, accent)
            seg = work / f"seg_{tag}.mp4"
            failed = False
            if item and item["kind"] == "video":
                try:
                    video_segment(item, layer, sdur, seg, work, tag)
                    segments.append(seg)
                    marks.append("🎥")
                    if i == 0 and s_no == 0:
                        run(["ffmpeg", "-y", "-i", str(seg), "-frames:v", "1", str(work / "thumb.png")])
                    continue
                except subprocess.CalledProcessError as exc:
                    err = exc.stderr.decode(errors='replace')[-300:]
                    print(f"[!] clip failed on beat {i}: {err}")
                    failed = True
                    ERRORS.append(f"{out.stem} beat {i}: {err.splitlines()[-1] if err else 'ffmpeg error'}")
                    item = None
                    layer = overlay(None, hook, accent)
            bg = photo_bg(ROOT / item["file"], item.get("focus"), hook=bool(hook)) if item else gradient(*colors)
            marks.append("❌🎥→⬛" if failed else (("🔍" if close else "📷") if item else "⬛"))
            still_segment(bg, layer, sdur, seg, work, tag, zoom_in=(i + s_no) % 2 == 0,
                          close=frame_focus(ROOT / item["file"], item.get("focus")) if (item and close) else None)
            if i == 0 and s_no == 0:
                Image.alpha_composite(bg.convert("RGBA"), layer).convert("RGB").save(work / "thumb.png")
            segments.append(seg)
        log.append("+".join(marks))
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
    # end card: the last 3 s (after the 85% mark, so nobody swipes early) show a subscribe
    # prompt above the captions
    cta_png = work / "cta.png"
    cta_card(accent).save(cta_png)
    cta_at = max(total - 3.0, total * 0.85)
    # the card covers the picture, never the captions or the progress bar (drawn on top of it)
    vf = (f"[CTA:v]format=rgba,fade=t=in:st={cta_at:.2f}:d=0.25:alpha=1[cta];"
          f"[0:v][cta]overlay=0:0:enable='gte(t,{cta_at:.2f})'[base];"
          f"[base]{bar},ass={ass}{fonts}[v]")
    if music and (ROOT / music["file"]).exists():
        # music: start a bit in (skip intros), quiet, ducks under the voice, fades in and out
        offset = min(15.0, max(0.0, music.get("duration", 0) - total - 1))
        # Mixing by loudness, not by a fixed volume (every track is mastered differently):
        # the voice is at -14 LUFS (YouTube's level); the music bed is measured and set
        # MUSIC_UNDER_DB below it (18 dB = the usual starting point for narration), then ducks
        # a few more dB while she speaks and comes back up in the pauses. Final mix: -14 LUFS.
        bed_lufs = -14 - MUSIC_UNDER_DB
        af = (f"[1:a]asplit=2[voice][key];"
              f"[2:a]atrim=start={offset:.1f},asetpts=PTS-STARTPTS,"
              f"loudnorm=I={bed_lufs}:TP=-9:LRA=7,aresample=44100,"
              f"afade=t=in:d=0.8,afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5[bed];"
              f"[bed][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=400[duck];"
              f"[voice][duck]amix=inputs=2:duration=first:normalize=0,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3), "-stream_loop", "-1", "-i", str(ROOT / music["file"])]
        log.append("music: " + music.get("mood", ""))
    else:
        af = "[1:a]anull[a]"
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3)]
        log.append("music: none")
    vf = vf.replace("[CTA:v]", f"[{inputs.count('-i')}:v]")
    inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", str(cta_png)]
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

"""Stage 5: render each Short as a vertical MP4 (1080x1920, 30 fps). No cards.

Every beat shows the real visual media.py picked for it:
  photo  a real photo of the person (Wikimedia Commons), with a camera move
  video  real footage, muted, filled to 9:16
The EDIT follows the story (the script marks every beat's stage): a calm push on the setup,
a fast push on the conflict, a sideways move as it escalates, a hard punch-in with a white
flash and a low hit on the twist, a slow pull back on the payoff. Beef stories open on a
"VS" frame: a real photo of each side. Sound design is made here in code (whoosh, hit,
sound logo): original, free, no licence. The music lifts on the twist and the question.
On top: a small "NBA RUMORS" tag, the hook words on the first beat (also the thumbnail),
phrase captions (names and numbers in the brand colour, moved up when a face is low in the
frame), a small name label the first time a person appears, a progress bar, the credit.

Output: data/video/short_N.mp4 + short_N_thumb.png
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from picture_ids import already_shown, mark_shown  # noqa: E402  (one photo in two crops = one picture)
import compliance  # noqa: E402  (one sentence split for the whole pipeline)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCRIPTS, AUDIO, VIDEO, MEDIA = DATA / "scripts", DATA / "audio", DATA / "video", DATA / "media"
W, H, FPS = 1080, 1920, 30
END_CARD_SECONDS = 2.0   # the subscribe card, shown after the story (never over the voice);
                         # 2 s keeps every Short inside the niche's 25-35 s (owner, 2026-11-11)
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
# ONE brand colour on every Short (tag, captions, progress bar, VS, labels): viewers learn to
# recognise the channel in the feed. Team colours only tint a picture-less background.
BRAND_COLOR = os.environ.get("BRAND_COLOR", "#FACC15")


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
        # Pillow 14 drops getdata (2027-10-15, D12): get_flattened_data where it exists
        px = list(getattr(g, "get_flattened_data", g.getdata)())
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
            if already_shown(p, keys, k) or seen_before(h, hashes):
                continue
            mark_shown(p, keys, k)
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
BAND_H = 1150           # wide picture with a known face / any clip: a tall band (less blur)

_faces: dict[str, tuple[float, float] | None] = {}


YUNET = ROOT / "assets" / "models" / "face_detection_yunet_2023mar.onnx"   # OpenCV Zoo, Apache-2.0
_yunet: list = []


def yunet_faces(cv2, img, side: int) -> list | None:
    """Faces found by YuNet, OpenCV's small modern face detector (free; finds turned and
    half-lit faces the older Haar detector misses), as (x, y, w, h). None when it cannot run."""
    try:
        if not _yunet:
            if not YUNET.exists() or not hasattr(cv2, "FaceDetectorYN"):
                return None
            _yunet.append(cv2.FaceDetectorYN.create(str(YUNET), "", (320, 320), 0.8, 0.3, 5000))
        det = _yunet[0]
        det.setInputSize((img.shape[1], img.shape[0]))
        _, found = det.detect(img)
        if found is None:
            return []
        return [tuple(int(v) for v in f[:4]) for f in found if f[2] >= side and f[3] >= side]
    except Exception:
        return None


def face_focus(path: Path) -> tuple[float, float] | None:
    """Centre of the biggest face in a photo (0-1), found by OpenCV's free face detector
    (YuNet; the older Haar detector when YuNet cannot run).
    Used for every photo nobody looked at (top-ups, VS) and to keep faces out from under
    the words. None when no face is found or OpenCV is missing."""
    key = str(path)
    if key in _faces:
        return _faces[key]
    found = None
    try:
        import cv2
        img = cv2.imread(key)
        if img is not None:
            h, w = img.shape[:2]
            k = 900 / max(h, w) if max(h, w) > 900 else 1.0
            small = cv2.resize(img, (round(w * k), round(h * k)))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            side = max(30, int(min(gray.shape) * 0.06))
            faces = yunet_faces(cv2, small, side)
            if faces is None:   # no YuNet model / OpenCV without it: the older detector, as before
                det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                faces = det.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(side, side))
            faces = sorted(faces, key=lambda f: -f[2] * f[3]) if len(faces) else []
            # a crowd (many similar faces) has no one subject: better unknown than wrong
            clear = len(faces) < 3 or faces[0][2] * faces[0][3] >= 1.8 * faces[1][2] * faces[1][3]
            if len(faces) and clear:
                x, y, fw, fh = faces[0]
                found = ((x + fw / 2) / gray.shape[1], (y + fh / 2) / gray.shape[0])
    except Exception:
        found = None
    _faces[key] = found
    return found


def focus_of(item: dict) -> tuple[tuple[float, float], bool]:
    """(where the subject is, whether we really know it): Claude's judged focus (it knows WHO),
    made exact by the face detector when the detected face is the same person (close to
    Claude's point across the picture); else a detected face, else the usual head height.
    Claude's point comes from a small contact sheet and is often only roughly right (a face at
    10% of the height marked at 30% put the hook words over the face)."""
    face = face_focus(ROOT / item["file"]) if item.get("kind") == "photo" and item.get("file") else None
    if item.get("focus") and item.get("match") is not None:
        fx, fy = item["focus"][:2]
        if face and abs(face[0] - fx) <= 0.25:
            return face, True
        return (fx, fy), True
    if face:
        return face, True
    return tuple((item.get("focus") or [0.5, 0.3])[:2]), bool(item.get("focus"))


def photo_bg(path: Path, focus: list | tuple | None = None, hook: bool = False,
             known: bool = False) -> tuple[Image.Image, tuple[float, float]]:
    """Real photo, and where the face lands in the finished frame (0-1).
    A tall photo fills the 9:16 frame. A wide photo with a known face is shown as a tall band
    framed on the face; a wide photo with an unknown subject is shown almost whole (cutting it
    blind could cut a head off), over a blurred, darkened copy of itself.
    hook=True (the opening shot, with the hook words at the top): the face sits BELOW the
    words, never hidden behind them - the face is what stops the scroll."""
    fx, fy = (focus or [0.5, 0.3])[:2]
    src = Image.open(path).convert("RGB")
    if src.width / src.height <= 0.8:
        if not hook:
            img = ImageOps.fit(src, (W, H), Image.LANCZOS, centering=(fx, fy))
            return ImageEnhance.Brightness(img).enhance(0.8), (fx, fy)
        scale = max(W / src.width, H / src.height)
        face = fy * src.height * scale
        if face < FACE_UNDER_HOOK:            # face too high to crop down to: zoom in a little
            scale *= min(1.35, FACE_UNDER_HOOK / max(face, 1))
        sw, sh = round(src.width * scale), round(src.height * scale)
        big = src.resize((sw, sh), Image.LANCZOS)
        left = min(max(0, round(fx * sw - W / 2)), sw - W)
        top = min(max(0, round(fy * sh - FACE_UNDER_HOOK)), sh - H)
        where = ((fx * sw - left) / W, (fy * sh - top) / H)
        drop = round(FACE_UNDER_HOOK - fy * sh) if top == 0 else 0
        if drop > 120:
            # the face is so close to the top edge that no crop can bring it under the hook words:
            # the photo moves DOWN over a blurred copy of itself, so the words sit on the blur
            bg = ImageOps.fit(src, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
            bg = ImageEnhance.Brightness(bg).enhance(0.45)
            fg = ImageEnhance.Brightness(big.crop((left, 0, left + W, H - drop))).enhance(0.8)
            bg.paste(fg, (0, drop))
            return bg, ((fx * sw - left) / W, FACE_UNDER_HOOK / H)
        return ImageEnhance.Brightness(big.crop((left, top, left + W, top + H))).enhance(0.8), where
    bg = ImageOps.fit(src, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    if known:
        fw = max(W, round(src.width * BAND_H / src.height))
        fg = src.resize((fw, round(src.height * fw / src.width)), Image.LANCZOS)
        left = min(max(0, round(fx * fw - W / 2)), fw - W)
        top = round(max(0, fg.height - BAND_H) * fy)
        fg = fg.crop((left, top, left + W, top + min(fg.height, BAND_H)))
        face_x = (fx * fw - left) / W
    else:
        fg = src.resize((FG_W, round(src.height * FG_W / src.width)), Image.LANCZOS)
        left = round((fg.width - W) * fx)
        top = round(max(0, fg.height - FG_MAX_H) * fy)
        fg = fg.crop((left, top, left + W, top + min(fg.height, FG_MAX_H)))
        face_x = (fx * FG_W - left) / W
    y = max(120, FG_CY - fg.height // 2)
    if hook:   # the face (fy of the band) lands under the hook words
        y = min(max(120, round(FACE_UNDER_HOOK - fy * fg.height)), H - fg.height - 200)
    bg.paste(ImageEnhance.Brightness(fg).enhance(0.95), (0, y))
    return bg, (face_x, (y + fy * fg.height) / H)


def vs_frame(a: dict, b: dict) -> Image.Image:
    """Beef opener: a real photo of each side, split on a diagonal, faces under the hook words,
    a small VS badge between them. Real photos only (no card)."""
    def half(item: dict, width: int) -> Image.Image:
        (fx, fy), _ = focus_of(item)
        src = Image.open(ROOT / item["file"]).convert("RGB")
        scale = max(width / src.width, H / src.height)
        if fy * src.height * scale < FACE_UNDER_HOOK:
            scale *= min(1.35, FACE_UNDER_HOOK / max(fy * src.height * scale, 1))
        sw, sh = round(src.width * scale), round(src.height * scale)
        big = src.resize((sw, sh), Image.LANCZOS)
        left = min(max(0, round(fx * sw - width / 2)), sw - width)
        top = min(max(0, round(fy * sh - FACE_UNDER_HOOK)), sh - H)
        return ImageEnhance.Brightness(big.crop((left, top, left + width, top + H))).enhance(0.82)
    img = Image.new("RGB", (W, H))
    img.paste(half(a, 640), (0, 0))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(600, 0), (W, 0), (W, H), (480, H)], fill=255)
    right = Image.new("RGB", (W, H))
    right.paste(half(b, 640), (440, 0))
    img = Image.composite(right, img, mask)
    d = ImageDraw.Draw(img)
    d.line([(600, 0), (480, H)], fill=BRAND_COLOR, width=12)
    cx, cy, r = 537, 1000, 86
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BRAND_COLOR, outline="#000000", width=6)
    f = font(92)
    tw = d.textlength("VS", font=f)
    d.text((cx - tw / 2, cy - 62), "VS", font=f, fill="#000000")
    return img


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


# the end screen's silent agree/disagree line (never spoken, so the loop and the length stay as
# they are): agreeing turns into a like, disagreeing into a comment (the strongest signal).
# The wording rotates so the Shorts never repeat one formula.
ENGAGE_LINES = [("AGREE WITH OUR TAKE? LIKE IT", "DISAGREE? TELL US WHY"),
                ("SEE IT OUR WAY? HIT LIKE", "SEE IT DIFFERENTLY? COMMENT WHY"),
                ("ON OUR SIDE? LIKE IT", "NOT BUYING IT? SAY WHY BELOW"),
                ("WE GOT IT RIGHT? LIKE IT", "WE GOT IT WRONG? PROVE IT BELOW")]


def engage_line(seed: str) -> tuple[str, str]:
    return ENGAGE_LINES[int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(ENGAGE_LINES)]


def cta_card(accent: str, seed: str = "") -> Image.Image:
    """Subscribe prompt for the end of every Short: a red pill with the value line, above the
    captions and inside the Shorts safe zone, and above it the silent agree/disagree line."""
    # a plain, calm background instead of the last picture: the channel logo goes on it as soon
    # as assets/logo.png exists in the repo (until then it stays blank)
    img = Image.new("RGBA", (W, H), (11, 11, 14, 255))
    logo_path = ROOT / "assets" / "logo.png"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((520, 520), Image.LANCZOS)
            img.alpha_composite(logo, ((W - logo.width) // 2, 700 - logo.height))
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
    for k, line in enumerate(engage_line(seed)):
        size = 50
        while size > 30 and d.textlength(line, font=font(size)) > W - 120:
            size -= 2
        f = font(size)
        d.text(((W - d.textlength(line, font=f)) / 2, 718 + k * 62), line, font=f,
               fill="#FFFFFF" if k == 0 else accent, stroke_width=3, stroke_fill="#000000")
    return img


def credit_of(items: list[dict]) -> str:
    items = [x for x in items if x]
    if not items:
        return ""
    what = "Photo" if all(x["kind"] == "photo" for x in items) else "Video"
    if len(items) > 1:
        what += "s"
    return f"{what}: " + " · ".join(f"{x['author'][:28 if len(items) > 1 else 40]} / {x['license']}"
                                      for x in items) + f" / {items[0]['source']}"


# every photo's author, licence (with its link) and source are in the description, plus a note
# that the pictures were changed (cropped, zoomed, captioned): that is how CC licences are
# credited in a video ("in any reasonable manner based on the medium"), so the small line at the
# bottom of the picture is off. Set to True to show it again.
SHOW_CREDIT = False
NAME_Y = {True: 1050, False: 760}   # name label: above low captions / below raised captions


def overlay(item: dict | None, hook_text: str, accent: str, label: str = "", low_captions: bool = True,
            credit: str | None = None) -> Image.Image:
    """Transparent layer over the footage: small brand tag, credit, (beat 0 only) the hook
    words, and a small name label the first time a person appears. Shade at top and bottom
    keeps text readable on any picture."""
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
    text = credit if credit is not None else credit_of([item] if item else [])
    if text and SHOW_CREDIT:
        cf = font(28, bold=False)
        while d.textlength(text, font=cf) > W - 40 and cf.size > 18:
            cf = font(cf.size - 2, bold=False)
        d.text(((W - d.textlength(text, font=cf)) / 2, 1760), text, font=cf, fill="#D1D5DB",
               stroke_width=2, stroke_fill="#000000")
    if label:
        lf = font(46)
        y = NAME_Y[low_captions]
        tw = d.textlength(label, font=lf)
        d.rounded_rectangle((56, y, 56 + tw + 64, y + 70), radius=12, fill=(0, 0, 0, 185))
        d.rectangle((56, y, 68, y + 70), fill=BRAND_COLOR)
        d.text((92, y + 6), label, font=lf, fill="#FFFFFF")
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


PHRASE_WORDS, PHRASE_CHARS = 4, 18
CAP_LOW, CAP_HIGH = 1240, 600       # caption centre: normal / when a face is low in the frame
NOT_NAMES = {"i", "im", "id", "ill", "ive", "ok", "okay", "honestly", "wait", "so", "but", "and", "the"}


def phrase_groups(words: list[dict]) -> list[list[dict]]:
    """Captions follow the speech: 3-4 words, a new phrase after punctuation, never a
    half-phrase hanging over a full stop."""
    groups: list[list[dict]] = []
    cur: list[dict] = []
    for w in words:
        chars = len(" ".join(x["word"] for x in cur + [w]))
        if cur and (len(cur) >= PHRASE_WORDS or chars > PHRASE_CHARS or re.search(r"[.,!?;:]$", cur[-1]["word"])
                    or bool(cur[-1].get("receipt")) != bool(w.get("receipt"))):   # the receipt stands alone
            groups.append(cur)
            cur = []
        cur.append(w)
    return groups + ([cur] if cur else [])


def mark_receipt(words: list[dict], receipt: str) -> tuple[list[dict], float | None]:
    """The receipt (the Short's sharpest sourced quote or number) is found in the spoken words
    and marked: it gets its own big caption and a low hit. Returns (words, its start time)."""
    key = [norm(t) for t in (receipt or "").split() if norm(t)]
    toks = [norm(w["word"]) for w in words]
    if not key:
        return words, None
    for i in range(len(toks) - len(key) + 1):
        if toks[i:i + len(key)] == key:
            out = [dict(w) for w in words]
            for w in out[i:i + len(key)]:
                w["receipt"] = True
            return out, words[i]["start"]
    return words, None


def key_words(beats: list[dict], headline: str = "") -> set[str]:
    """Names, teams and numbers in the script: they stay in the brand colour all along.
    A capital inside a sentence is a name; a capital opening a sentence only when the same
    word is a name elsewhere (the headline counts too)."""
    keys: set[str] = set()
    starts: set[str] = set()
    for text in [headline] + [b.get("say", "") for b in beats]:
        # the same sentence split as the script checks: no new sentence after "Stephen A." or
        # "Jr." (audit, 2026-11-13: "Smith" after "A." was taken for a sentence start)
        for sent in compliance.split_sentences(text):
            for k, tok in enumerate(sent.split()):
                bare = re.sub(r"[^\w'’-]", "", tok)
                if any(ch.isdigit() for ch in bare) or bare.lower() in TEAMS:
                    keys.add(norm(bare))
                elif bare[:1].isupper() and norm(bare) not in NOT_NAMES:
                    (keys if k else starts).add(norm(bare))
    keys = {k for k in keys if k}
    keys.update({k + "s" for k in keys})   # "Celtics'"/"Brown's" -> same key
    return keys


def captions(words: list[dict], path: Path, accent: str, keys: set[str] | None = None,
             places: list[tuple[float, float, int]] | None = None) -> None:
    """Big viral-style captions: a short phrase at a time, the spoken word pops, names and
    numbers stay in the brand colour. places=(start, end, y): the caption height per shot."""
    hex6 = accent.lstrip("#")
    bgr = f"&H00{hex6[4:6]}{hex6[2:4]}{hex6[0:2]}"
    keys = keys or set()

    def y_at(t: float) -> int:
        for t0, t1, y in places or []:
            if t0 <= t < t1:
                return y
        return CAP_LOW
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, "
        "Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        "Style: Cap,Anton,150,&H00FFFFFF,&H00000000,&HA0000000,1,10,5,5,40,40,0\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
    )
    events = []
    groups = phrase_groups(words)
    starts = [w["start"] for w in words]
    idx = 0
    for g in groups:
        y = y_at(g[0]["start"])            # one phrase never jumps mid-way
        chars = len(" ".join(x["word"] for x in g))
        fs = min(140, int(140 * 13 / max(13, chars)))  # long phrases shrink, never run off screen
        big = any(x.get("receipt") for x in g)
        if big:                                         # the receipt: bigger, all in the brand colour
            fs = min(160, int(fs * 1.15))
        for j, w in enumerate(g):
            nxt = starts[idx + 1] if idx + 1 < len(starts) else w["end"] + 0.4
            end = min(nxt, w["end"] + 0.6)  # never overlaps the next caption
            idx += 1
            parts = []
            for k, x in enumerate(g):
                word = re.sub(r"[{}\\]", "", x["word"]).upper()
                key = norm(x["word"]) in keys or big
                if k == j:
                    parts.append(f"{{\\c{bgr}\\fscx114\\fscy114\\t(0,90,\\fscx100\\fscy100)}}{word}"
                                 f"{{\\c&H00FFFFFF\\fscx100\\fscy100}}")
                elif key:
                    parts.append(f"{{\\c{bgr}}}{word}{{\\c&H00FFFFFF}}")
                else:
                    parts.append(word)
            events.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Cap,"
                          f"{{\\pos(540,{y})\\fs{fs}}}{' '.join(parts)}")
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


# ---------- assembly ----------

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]


# ---------- the edit follows the story ----------
# The script marks each beat's stage; each stage has its own camera move. Shots after the
# first in a beat alternate calmer moves so the picture never feels like the same slideshow.
STAGES = ["setup", "conflict", "escalation", "twist", "payoff", "exit"]
STAGE_OF_ROLE = {"fact": "setup", "context": "setup", "reaction": "escalation", "analysis": "payoff",
                 "question": "exit"}
STAGE_MOVE = {"hook": "push", "setup": "push", "conflict": "push_fast", "escalation": "pan",
              "twist": "punch", "payoff": "pull", "exit": "push"}
HOT = {"conflict", "escalation", "twist"}          # stages cut with a punch / whoosh


def stage_of(short: dict, i: int) -> str:
    """Stage of narration beat i (0 = the hook)."""
    if i == 0:
        return "hook"
    beats = short.get("beats") or []
    if i - 1 >= len(beats):
        return "setup"
    b = beats[i - 1]
    st = str(b.get("stage") or "").lower()
    if st in STAGES:
        return st
    if i - 1 == len(beats) - 1:
        return "exit"
    return STAGE_OF_ROLE.get(str(b.get("role") or "").lower(), "setup")


def shot_move(stage: str, shot_no: int) -> str:
    move = STAGE_MOVE.get(stage, "push")
    if shot_no == 0:
        return move
    if move == "pan":
        return "pan"                                   # escalation keeps moving sideways
    return ["push", "pull"][shot_no % 2] if stage not in HOT else ["push_fast", "pan"][shot_no % 2]


def motion(move: str, frames: int, face: tuple[float, float], k: int) -> tuple[str, str, str]:
    """zoompan expressions (zoom, x, y). Zoom moves aim at the face, not the frame centre."""
    fx, fy = face
    aim_x = f"max(0,min(iw-iw/zoom,iw*{fx:.3f}-iw/zoom/2))"
    aim_y = f"max(0,min(ih-ih/zoom,ih*{fy:.3f}-ih/zoom/2))"
    small = "if(lt(on,6),0.08*(1-on/6),0)"            # a small punch on a hot cut
    hard = "if(lt(on,8),0.16*(1-on/8),0)"             # the twist: a hard punch-in
    if move == "pull":
        return f"1.10-0.09*on/{frames}", aim_x, aim_y
    if move == "push_fast":
        return f"1+0.15*on/{frames}+{small}", aim_x, aim_y
    if move == "punch":
        return f"1.12+0.05*on/{frames}+{hard}", aim_x, aim_y
    if move == "pan":
        side = f"on/{frames}" if k % 2 == 0 else f"(1-on/{frames})"
        return f"1.14+{small}", f"(iw-iw/zoom)*{side}", aim_y
    return f"1+0.08*on/{frames}", aim_x, aim_y        # push


FLASH = "fade=t=in:st=0:d=0.18:color=white"


def still_segment(bg: Image.Image, layer: Image.Image, dur: float, seg: Path, work: Path, i,
                  move: str = "push", face: tuple[float, float] = (0.5, 0.4), k: int = 0,
                  flash: bool = False) -> None:
    """Photo with the stage's camera move; the overlay on top stays still."""
    bg_path, ov_path = work / f"bg_{i}.jpg", work / f"ov_{i}.png"
    bg.save(bg_path, quality=92)
    layer.save(ov_path)
    frames = int(round(dur * FPS))
    z, x, y = motion(move, frames, face, k)
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(bg_path), "-i", str(ov_path), "-filter_complex",
         f"[0:v]scale={W * 2}:{H * 2},zoompan=z='{z}':x='{x}':y='{y}':"
         f"d={frames}:s={W}x{H}:fps={FPS},setsar=1[b];[b][1:v]overlay=0:0" + (f",{FLASH}" if flash else ""),
         "-frames:v", str(frames), "-an", *ENC, str(seg)])


def video_segment(item: dict, layer: Image.Image, dur: float, seg: Path, work: Path, i,
                  hot: bool = False, flash: bool = False) -> tuple[float, float]:
    """Real footage, muted, filled to 9:16. Never looped (a loop would show the same frames
    twice): a clip shorter than its shot holds its last frame for the rest.
    Returns where the subject sits in the frame (0-1)."""
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
        where = (fx, fy)
    else:  # wide clip: a tall band framed on the subject over a blurred copy (much less blur)
        frame = (f"[0:v]fps={FPS},split=2[a][c];"
                 f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"boxblur=25:3,eq=brightness=-0.3[bgv];"
                 f"[c]scale=w='max({W},trunc(iw*{BAND_H}/ih/2)*2)':h=-2,crop=w={W}:h='min(ih,{BAND_H})':"
                 f"x='(iw-{W})*{fx:.3f}':y='(ih-min(ih,{BAND_H}))*{fy:.3f}'[fg];"
                 f"[bgv][fg]overlay=0:'{FG_CY}-h/2',")
        where = (0.5, (FG_CY - BAND_H / 2 + fy * BAND_H) / H)
    punch = (f"scale=w='trunc({W}*(1+0.12*max(0,1-t/0.2))/2)*2':h=-2:eval=frame,crop={W}:{H},"
             if hot else "")
    run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", src,
         "-i", str(ov_path), "-filter_complex",
         frame +
         f"eq=brightness=-0.05:saturation=1.1,fps={FPS},tpad=stop_mode=clone:stop_duration={dur:.2f},"
         + punch +
         f"setsar=1[b];[b][1:v]overlay=0:0" + (f",{FLASH}" if flash else ""),
         "-t", f"{dur:.3f}", "-an", *ENC, str(seg)])
    return where


# ---------- sound design: made here, in code (original, no licence needed) ----------
SFX_RECIPES = {
    # a soft air sweep on hot cuts
    "whoosh": (["-f", "lavfi", "-i", "anoisesrc=color=pink:duration=0.55:amplitude=0.7:sample_rate=44100"],
               "highpass=f=350,lowpass=f=5500,afade=t=in:st=0:d=0.30:curve=qsin,"
               "afade=t=out:st=0.30:d=0.25:curve=qsin,volume=0.30"),
    # a low hit under the twist
    "impact": (["-f", "lavfi", "-i", "sine=f=52:duration=0.9:sample_rate=44100",
                "-f", "lavfi", "-i", "anoisesrc=color=brown:duration=0.22:amplitude=0.9:sample_rate=44100"],
               None),
    # the channel's two-note sound logo on the end card
    "logo": (["-f", "lavfi", "-i", "sine=f=659.25:duration=0.75:sample_rate=44100",
              "-f", "lavfi", "-i", "sine=f=987.77:duration=0.75:sample_rate=44100"], None),
}
SFX_GRAPH = {
    "impact": "[0:a]afade=t=out:st=0.02:d=0.85:curve=exp,volume=0.9[s];"
              "[1:a]lowpass=f=380,afade=t=out:st=0:d=0.22:curve=exp,volume=0.8[n];"
              "[s][n]amix=inputs=2:normalize=0,volume=0.55[o]",
    "logo": "[0:a]afade=t=out:st=0.04:d=0.4:curve=exp[a];"
            "[1:a]adelay=140,afade=t=out:st=0.18:d=0.55:curve=exp[b];"
            "[a][b]amix=inputs=2:normalize=0,volume=0.22[o]",
}
MAX_WHOOSH = 4      # sound effects support the story; a whoosh on every cut gets annoying


def sfx_track(events: list[tuple[float, str]], total: float, work: Path) -> Path | None:
    """One quiet effects track: each event (time, kind) placed on the timeline."""
    events = [(t, k) for t, k in events if 0 <= t < total]
    if not events:
        return None
    files = {}
    for kind in {k for _, k in events}:
        path = work / f"sfx_{kind}.wav"
        ins, af = SFX_RECIPES[kind]
        if kind in SFX_GRAPH:
            run(["ffmpeg", "-y", *ins, "-filter_complex", SFX_GRAPH[kind], "-map", "[o]", "-ac", "1", str(path)])
        else:
            run(["ffmpeg", "-y", *ins, "-af", af, "-ac", "1", str(path)])
        files[kind] = path
    ins, graph = ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=mono"], []
    for n, (t, kind) in enumerate(events, 1):
        ins += ["-i", str(files[kind])]
        graph.append(f"[{n}:a]adelay={int(t * 1000)}[e{n}]")
    graph.append("[0:a]" + "".join(f"[e{n}]" for n in range(1, len(events) + 1))
                 + f"amix=inputs={len(events) + 1}:duration=first:normalize=0[o]")
    out = work / "sfx.wav"
    run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(graph), "-map", "[o]", "-ac", "1", str(out)])
    return out


def swell(times: list[tuple[float, float]]) -> str:
    """Music volume: lifts (~+4 dB) on the twist and under the final question."""
    if not times:
        return "1"
    return "1+" + "+".join(f"0.6*between(t\\,{a:.2f}\\,{b:.2f})" for a, b in times)


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


def opening_picture(media: list, n: int) -> list:
    """The hook must open on a real picture, never on a plain background: if beat 0 has none,
    the first later picture moves up to the hook (that later beat then continues it, so
    nothing is shown twice)."""
    media = list(media) + [None] * max(0, n - len(media))
    if media and media[0] is None:
        k = next((k for k in range(1, len(media)) if media[k]), None)
        if k is not None:
            media[0], media[k] = media[k], None
    return media


def end_card_at(timing: dict) -> float:
    """When the end card starts: a breath (0.4 s) after the voice's last real sound, measured in
    the audio by audio_qc (Whisper's last word often ends too early); never after the voice
    file ends. Not measured: the file's end."""
    return min(timing["duration"], timing.get("voice_end", timing["duration"]) + 0.4)


def render(short: dict, timing: dict, mp3: Path, out: Path, work: Path,
           media: list | None = None, music: dict | None = None, vs: list | None = None) -> list[str]:
    work.mkdir(parents=True, exist_ok=True)
    # The story is told to the end over its pictures; only THEN the end card (black, the
    # channel logo once assets/logo.png exists) asks for the subscription. It used to cover
    # the last 3 s while the closing question was still being spoken (owner, 2026-11-11).
    cta_at = end_card_at(timing)
    total = cta_at + END_CARD_SECONDS
    colors = team_colors(" ".join([short["headline"]] + [b.get("say", "") for b in short["beats"]]))
    accent = BRAND_COLOR
    beats = timing["beats"]
    vs = [x for x in (vs or []) if x and x.get("file") and (ROOT / x["file"]).exists()]
    # last safety net: nothing twice (the VS photos count too: they are never shown again)
    checked = no_repeats(vs + list(media or []) + [None] * len(beats))
    head, media = checked[:len(vs)], checked[len(vs):]
    vs = head if len(head) == 2 and all(head) else []
    media = opening_picture(media, len(beats))
    # a beat with no picture of its own continues the previous beat's picture (one longer
    # shot): never a repeated picture, never a plain colour card
    runs = []
    for i, b in enumerate(beats):
        start = 0.0 if i == 0 else b["start"]
        end = beats[i + 1]["start"] if i + 1 < len(beats) else total
        if media[i] is None and runs and runs[-1][1] is not None:
            runs[-1][2] += max(0.6, end - start)
        else:
            runs.append([i, media[i], max(0.6, end - start)])
    segments, log = [], []
    places: list[tuple[float, float, int]] = []     # caption height per shot
    sfx: list[tuple[float, str]] = []
    lifts: list[tuple[float, float]] = []
    introduced: set[str] = {x.get("person") for x in vs if x.get("person")}
    for i in range(1, len(beats)):     # per beat (a beat may continue the previous picture)
        st, b0 = stage_of(short, i), beats[i]["start"]
        b1 = beats[i + 1]["start"] if i + 1 < len(beats) else total
        if st == "twist":
            sfx.append((b0, "impact"))
            lifts.append((b0, b0 + 1.8))
        if st == "exit":
            lifts.append((b0, b1))
    t = 0.0
    hook_text = short.get("thumbnail_text") or short["hook"]["text"]
    for i, main, dur in runs:
        stage = stage_of(short, i)
        hook = hook_text if i == 0 else ""
        if i and stage in ("conflict", "escalation") and sum(k == "whoosh" for _, k in sfx) < MAX_WHOOSH:
            sfx.append((max(0.0, t - 0.25), "whoosh"))
        marks = []
        if i == 0 and vs:                                    # beef opener: VS frame first
            vdur = round(min(2.4, max(1.2, dur * 0.5)), 2) if dur > 2.4 else dur
            layer = overlay(None, hook, accent, credit=credit_of(vs))
            bg = vs_frame(vs[0], vs[1])
            seg = work / "seg_vs.mp4"
            still_segment(bg, layer, vdur, seg, work, "vs", move="push", face=(0.5, 0.4))
            Image.alpha_composite(bg.convert("RGBA"), layer).convert("RGB").save(work / "thumb.png")
            segments.append(seg)
            places.append((t, t + vdur, CAP_LOW))
            marks.append("🆚")
            t += vdur
            dur = round(dur - vdur, 2)
            if dur >= 0.5 and sum(k == "whoosh" for _, k in sfx) < MAX_WHOOSH:
                sfx.append((max(0.0, t - 0.25), "whoosh"))
        if dur < 0.5:
            log.append("+".join(marks))
            continue
        shots = plan_shots(main, dur)
        for s_no, (item, sdur, _) in enumerate(shots):
            tag = f"{i}_{s_no}"
            move = shot_move(stage, s_no)
            flash = stage == "twist" and s_no == 0
            hot = stage in HOT and s_no == 0
            person = (item or {}).get("person", "")
            label = person.upper() if person and person not in introduced else ""
            seg = work / f"seg_{tag}.mp4"
            if item and item["kind"] == "video":
                try:
                    where = video_segment(item, overlay(item, hook, accent), sdur, seg, work, tag, hot, flash)
                    low = not (0.53 <= where[1] <= 0.77) or bool(hook)
                    if label:   # the label needs to know where the captions go: render once more
                        video_segment(item, overlay(item, hook, accent, label, low), sdur, seg, work, tag, hot, flash)
                        introduced.add(person)
                    segments.append(seg)
                    places.append((t, t + sdur, CAP_LOW if low else CAP_HIGH))
                    marks.append("🎥")
                    if i == 0 and s_no == 0 and not vs:
                        run(["ffmpeg", "-y", "-ss", "0.3", "-i", str(seg), "-frames:v", "1", str(work / "thumb.png")])
                    t += sdur
                    continue
                except subprocess.CalledProcessError as exc:
                    err = exc.stderr.decode(errors='replace')[-300:]
                    print(f"[!] clip failed on beat {i}: {err}")
                    ERRORS.append(f"{out.stem} beat {i}: {err.splitlines()[-1] if err else 'ffmpeg error'}")
                    item, label = None, ""
            if item:
                focus, known = focus_of(item)
                bg, face = photo_bg(ROOT / item["file"], focus, hook=bool(hook), known=known)
            else:
                bg, face = gradient(*colors), (0.5, 0.4)
            low = not (0.53 <= face[1] <= 0.77) or bool(hook)
            layer = overlay(item, hook, accent, label, low)
            if label:
                introduced.add(person)
            marks.append({"push": "📷", "pull": "📷", "push_fast": "⏩", "pan": "↔️", "punch": "💥"}[move]
                         if item else "⬛")
            still_segment(bg, layer, sdur, seg, work, tag, move=move, face=face, k=i + s_no, flash=flash)
            if i == 0 and s_no == 0 and not vs:
                Image.alpha_composite(bg.convert("RGBA"), layer).convert("RGB").save(work / "thumb.png")
            segments.append(seg)
            places.append((t, t + sdur, CAP_LOW if low else CAP_HIGH))
            t += sdur
        log.append(f"{stage[:4]}:" + "+".join(marks))
    (work / "list.txt").write_text("".join(f"file '{s.name}'\n" for s in segments))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"), "-c", "copy",
         str(work / "visuals.mp4")])
    # end card (from cta_at, after the voice): the captions go back to their usual place
    # there, the sound logo plays
    places = [(a, min(b, cta_at), y) for a, b, y in places if a < cta_at] + [(cta_at, total + 1, CAP_LOW)]
    sfx.append((cta_at + 0.05, "logo"))
    ass = work / "captions.ass"
    words = script_words(timing["words"], timing["beats"])
    words, receipt_at = mark_receipt(words, short.get("receipt", ""))
    if receipt_at is not None and not any(k == "impact" and abs(t - receipt_at) < 1.5 for t, k in sfx):
        sfx.append((max(0.0, receipt_at - 0.05), "impact"))
        log.append(f"receipt @{receipt_at:.1f}s")
    captions(words, ass, accent, key_words([{"say": short["hook"]["text"]}] + short["beats"],
                                        short.get("headline", "") + ". " + (short.get("thumbnail_text") or "").title()), places)
    log.append(f"captions: {len(phrase_groups(words))} phrases")
    bar = f"drawbox=x=0:y=0:w='iw*t/{total:.2f}':h=14:color={accent.replace('#', '0x')}@1:t=fill"
    fonts = f":fontsdir={FONT_DIR}" if FONT_DIR.exists() else ""
    cta_png = work / "cta.png"
    cta_card(accent, short.get("headline", "")).save(cta_png)
    # the card covers the picture, never the captions or the progress bar (drawn on top of it)
    vf = (f"[CTA:v]format=rgba,fade=t=in:st={cta_at:.2f}:d=0.25:alpha=1[cta];"
          f"[0:v][cta]overlay=0:0:enable='gte(t,{cta_at:.2f})'[base];"
          f"[base]{bar},ass={ass}{fonts}[v]")
    try:
        fx_track = sfx_track(sfx, total, work)
    except subprocess.CalledProcessError as exc:
        print(f"[!] sound effects skipped: {exc.stderr.decode(errors='replace')[-200:]}")
        fx_track = None
    if music and (ROOT / music["file"]).exists():
        # music: start a bit in (skip intros), quiet, ducks under the voice, fades in and out
        offset = min(15.0, max(0.0, music.get("duration", 0) - total - 1))
        # Mixing by loudness, not by a fixed volume (every track is mastered differently):
        # the voice is at -14 LUFS (YouTube's level); the music bed is measured and set
        # MUSIC_UNDER_DB below it, ducks a few more dB while she speaks, comes back up in the
        # pauses, and lifts on the twist and the final question. Final mix: -14 LUFS.
        bed_lufs = -14 - MUSIC_UNDER_DB
        af = (f"[1:a]apad=whole_dur={total:.2f},asplit=2[voice][key];"
              f"[2:a]atrim=start={offset:.1f},asetpts=PTS-STARTPTS,"
              f"loudnorm=I={bed_lufs}:TP=-9:LRA=7,aresample=44100,"
              f"afade=t=in:d=0.8,afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5,"
              f"volume='{swell(lifts)}':eval=frame[bed];"
              f"[bed][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=400[duck];"
              f"[voice][duck]{'[FX:a]' if fx_track else ''}amix=inputs={3 if fx_track else 2}:duration=first:normalize=0,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3), "-stream_loop", "-1", "-i", str(ROOT / music["file"])]
        log.append("music: " + music.get("mood", ""))
    else:
        af = (f"[1:a]apad=whole_dur={total:.2f}[vo];[vo][FX:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
              if fx_track else f"[1:a]apad=whole_dur={total:.2f}[a]")
        inputs = ["-i", str(work / "visuals.mp4"), "-i", str(mp3)]
        log.append("music: none")
    vf = vf.replace("[CTA:v]", f"[{inputs.count('-i')}:v]")
    inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", str(cta_png)]
    if fx_track:
        af = af.replace("[FX:a]", f"[{inputs.count('-i')}:a]")
        inputs += ["-i", str(fx_track)]
        log.append("sfx: " + " ".join(f"{k}@{t:.1f}" for t, k in sorted(sfx)))
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
            vs_path = MEDIA / f"{name}_vs.json"
            vs = json.loads(vs_path.read_text(encoding="utf-8")) if vs_path.exists() else []
            log = render(short, timing, mp3, out, VIDEO / f"_{name}", media, music, vs)
        except subprocess.CalledProcessError as exc:
            print(f"[!] {name}: ffmpeg failed: {exc.stderr.decode(errors='replace')[-800:]}")
            continue
        except Exception as exc:   # one broken Short must never stop the others
            import traceback
            traceback.print_exc()
            ERRORS.append(f"{name}: {type(exc).__name__}: {str(exc)[:160]}")
            continue
        # keep the hook card as a still (preview / thumbnail)
        thumb = VIDEO / f"_{name}" / "thumb.png"
        if thumb.exists():
            thumb.replace(VIDEO / f"{name}_thumb.png")
        rendered.append((name, short, timing, log))
        print(f"[+] {name}: {out.stat().st_size / 1e6:.1f} MB, {timing['duration']:.1f}s")
    lines = ["## 🎬 Video", "", "| Short | length | ready | beats (stage: 🆚 VS 🎥 clip 📷 photo ⏩ fast push ↔️ sideways 💥 twist ⬛ empty) | title |",
             "|---|---|---|---|---|"]
    for name, short, timing, log in rendered:
        title = short["titles"][0]["title"] if short.get("titles") else short["headline"]
        lines.append(f"| {name} | {timing['duration']:.0f}s | {'✅' if short.get('ready') else '⚠️'} | "
                     f"{' '.join(log)} | {title} |")
    if ERRORS:
        lines += ["", "**Render errors:**", ""] + [f"- `{e}`" for e in ERRORS]
    text = "\n".join(lines)
    # this repository is public: on GitHub the full report goes ONLY to the private summary file
    # (the run's logs are public too); printed only when run by hand
    if not os.environ.get("GITHUB_STEP_SUMMARY"):
        print(text)
    import os
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if not rendered:
        sys.exit("[!] No video was rendered.")


if __name__ == "__main__":
    main()

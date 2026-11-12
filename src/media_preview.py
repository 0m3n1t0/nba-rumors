"""Contact sheets of the pictures media.py chose, in beat order (media-preview.yml, read-only).

Each tile: beat number, main shot or extra shot, who (person / story / generic), the match score,
the photo tags (scene, emotion) and the file title, so a change to the picture choice can be
compared by eye on the same scripts. Writes data/preview/short_N[_k].jpg."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "preview"
CELL, COLS, PER = 470, 3, 9


def shots(items: list) -> list[tuple[int, str, dict]]:
    out = []
    for i, it in enumerate(items):
        if not it:
            out.append((i, "empty", {}))
            continue
        out.append((i, "main", it))
        out += [(i, f"extra {k + 1}", a) for k, a in enumerate(it.get("alts") or []) if a]
    return out


def tile(beat: int, role: str, it: dict, font) -> Image.Image:
    box = Image.new("RGB", (CELL, CELL + 92), "#111")
    path = ROOT / it["file"] if it.get("file") else None
    if path and path.exists():
        try:
            if it.get("kind") == "video":
                import subprocess
                frame = path.with_suffix(".preview.jpg")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(it.get("start") or 0.5), "-i", str(path),
                                "-frames:v", "1", str(frame)], check=False)
                path = frame
            with Image.open(path) as im:
                pic = ImageOps.contain(im.convert("RGB"), (CELL, CELL))
            box.paste(pic, ((CELL - pic.width) // 2, 92))
        except Exception:
            pass
    t = it.get("tag") or {}
    draw = ImageDraw.Draw(box)
    draw.text((6, 4), f"beat {beat} {role}: {it.get('who', '-')} {it.get('match', '-')}", font=font, fill="#FFD400")
    draw.text((6, 32), f"{t.get('s', '-')} / {t.get('e', '-')} {'(burst group)' if it.get('moment') else ''}",
              font=font, fill="#FFFFFF")
    draw.text((6, 60), (it.get("title") or it.get("kind") or "")[:44], font=font, fill="#AAAAAA")
    return box


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    for f in sorted((DATA / "media").glob("short_*.json")):
        if not f.stem.replace("short_", "").isdigit():
            continue
        items = json.loads(f.read_text(encoding="utf-8"))
        tiles = [tile(b, r, it, font) for b, r, it in shots(items)]
        for page in range(0, len(tiles), PER):
            part = tiles[page:page + PER]
            rows = (len(part) + COLS - 1) // COLS
            sheet = Image.new("RGB", (COLS * (CELL + 10) + 10, rows * (CELL + 102) + 10), "#000")
            for k, t in enumerate(part):
                r, c = divmod(k, COLS)
                sheet.paste(t, (10 + c * (CELL + 10), 10 + r * (CELL + 102)))
            name = f.stem + ("" if page == 0 else f"_{page // PER + 1}") + ".jpg"
            sheet.save(OUT / name, quality=85)
            print(f"[+] {name}: {len(part)} pictures")


if __name__ == "__main__":
    main()

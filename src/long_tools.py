"""Long-video skills: yt-chapters and yt-shorts.

Dormant until the long-video stage produces its first narration
(data/long/long_N.timing.json, same format as the Shorts' timing files).
Then, with no change needed here:

  yt-chapters  chapters.py turns the narration's timing into a chapter list that passes
               YouTube's rules (starts at 0:00, 3+ chapters, each 10s+), and Claude retitles
               the chapters with the yt-chapters method. Added to the video's description.
  yt-shorts    Claude reads the long video's timed transcript with the yt-shorts method and
               picks the self-contained moments that work as Shorts, each with a new first
               line. Saved for the video stage to cut: every long video becomes extra Shorts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skills import claude, segments_file, summary, tool  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LONG = ROOT / "data" / "long"


def transcript_text(timing: dict) -> str:
    """Beats with their start times, the readable form for Claude."""
    return "\n".join(f"[{b['start']:.1f}s - {b['end']:.1f}s] {b['say']}" for b in timing["beats"])


def chapters_for(path: Path, timing: dict) -> list[dict]:
    seg = segments_file(timing["words"], path.with_suffix(".segments.json"))
    draft = tool("yt-chapters", "chapters.py", str(seg), "--target", "6") or {}
    seg.unlink(missing_ok=True)
    chapters = draft.get("chapters", draft if isinstance(draft, list) else [])
    if not chapters:
        return []
    named = claude("yt-chapters",
                   "Retitle these chapters for the NBA Rumors long video. Keep every timestamp "
                   "exactly as given. 2-6 words each, specific (a name or the story), no clickbait. "
                   'Return {"chapters": [{"time": "0:00", "title": "..."}]}',
                   json.dumps({"chapters": chapters, "transcript": transcript_text(timing)}, indent=1))
    return named.get("chapters", [])


def shorts_for(timing: dict) -> list[dict]:
    picks = claude("yt-shorts",
                   "Find 2-4 moments in this long NBA Rumors video that work as stand-alone Shorts "
                   "(20-55 seconds, a complete mini story). For each give the start and end time "
                   "(seconds, from the transcript), a new first line (the hook, 9-24 words, true to "
                   "what is said) and a title. "
                   'Return {"clips": [{"start": 0.0, "end": 0.0, "first_line": "...", "title": "..."}]}',
                   transcript_text(timing))
    clips = []
    for c in picks.get("clips", []):
        try:
            start, end = float(c["start"]), float(c["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if 15 <= end - start <= 60 and 0 <= start < end <= timing["duration"] + 1:
            clips.append(c)
    return clips


def main() -> None:
    timings = sorted(LONG.glob("long_*.timing.json")) if LONG.exists() else []
    if not timings:
        print("[=] yt-chapters / yt-shorts: no long video yet, sleeping")
        return
    lines = ["## 📺 Long-video skills (yt-chapters, yt-shorts)", ""]
    for path in timings:
        timing = json.loads(path.read_text(encoding="utf-8"))
        name = path.name.replace(".timing.json", "")
        out = {"chapters": [], "clips": []}
        try:
            out["chapters"] = chapters_for(path, timing)
        except Exception as exc:
            print(f"[!] yt-chapters {name}: {exc}")
        try:
            out["clips"] = shorts_for(timing)
        except Exception as exc:
            print(f"[!] yt-shorts {name}: {exc}")
        (LONG / f"{name}.skills.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        lines.append(f"**{name}:** {len(out['chapters'])} chapters, {len(out['clips'])} Shorts found inside")
        lines += [f"- {c['time']} {c['title']}" for c in out["chapters"]]
        lines += [f"- ✂️ {c['start']:.0f}-{c['end']:.0f}s: {c.get('title', '')}" for c in out["clips"]]
        lines.append("")
    summary("\n".join(lines))


if __name__ == "__main__":
    main()

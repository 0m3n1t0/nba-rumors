"""The run's PUBLIC Summary page: short on purpose (owner's decision, 2026-11-11).

This repository is public, so the run page shows only how many Shorts were made and what the
publication gate decided: no headlines, scripts, titles, hooks or descriptions (they would be
public before the video is). The full report (every stage's section of data/summary.md) and
the working data are saved to the PRIVATE state repository by state.py, as nba/runs/.

  python src/public_summary.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def verdicts() -> dict[str, int]:
    out = {"PASS": 0, "REVIEW": 0, "REJECT": 0}
    for path in sorted((DATA / "gate").glob("short_*.json")):
        try:
            v = str(json.loads(path.read_text(encoding="utf-8")).get("verdict", "")).upper()
        except (OSError, ValueError):
            continue
        if v in out:
            out[v] += 1
    return out


def lines() -> list[str]:
    scripts = len(list((DATA / "scripts").glob("short_*.json")))
    videos = len(list((DATA / "video").glob("short_*.mp4")))
    v = verdicts()
    out = ["## 🏀 NBA Rumors run", "",
           "| scripts | videos | ✅ PASS | 🟡 REVIEW | ⛔ REJECT |", "|---|---|---|---|---|",
           f"| {scripts} | {videos} | {v['PASS']} | {v['REVIEW']} | {v['REJECT']} |", ""]
    skip = DATA / "skip_reason.txt"
    if skip.exists() and not scripts:
        out.append("No Short this run (no strong story, or the Claude limit was reached).")
        out.append("")
    out.append("The full report is kept in the private repository (this repository is public).")
    return out


def main() -> None:
    text = "\n".join(lines()) + "\n"
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text)


if __name__ == "__main__":
    main()

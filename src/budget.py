"""Budget table: how much of the free resources this run used.

Reads data/claude_usage.jsonl (one line per Claude call, written by every stage) and adds a
table to the run summary: calls, tokens and time per stage. "API-equivalent $" is what the
same calls would cost on the paid API; on the Pro plan it is a measure of how heavy the run was
(it is NOT charged). Comparing runs tells us how many runs a day the Pro plan carries.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    path = DATA / "claude_usage.jsonl"
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    by = defaultdict(lambda: {"calls": 0, "in": 0, "out": 0, "seconds": 0, "cost": 0.0})
    for r in rows:
        b = by[r.get("where", "?")]
        b["calls"] += 1
        b["in"] += r.get("in") or 0
        b["out"] += r.get("out") or 0
        b["seconds"] += r.get("seconds") or 0
        b["cost"] += r.get("cost_usd") or 0
    lines = ["## 💰 Budget (free resources used this run)", ""]
    skip = DATA / "skip_reason.txt"
    if skip.exists():
        lines += [f"Run skipped: {skip.read_text(encoding='utf-8')}", ""]
    lines += ["| stage | Claude calls | tokens in | tokens out | Claude time | API-equivalent $ (not charged) |",
              "|---|---|---|---|---|---|"]
    total = {"calls": 0, "in": 0, "out": 0, "seconds": 0, "cost": 0.0}
    for where, b in sorted(by.items()):
        lines.append(f"| {where} | {b['calls']} | {b['in']:,} | {b['out']:,} | {b['seconds']}s | {b['cost']:.2f} |")
        for k in total:
            total[k] += b[k]
    lines.append(f"| **total** | **{total['calls']}** | **{total['in']:,}** | **{total['out']:,}** | "
                 f"**{total['seconds']}s** | **{total['cost']:.2f}** |")
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()

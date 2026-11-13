"""The channel's permanent memory, kept in a PRIVATE repository (nba-rumors-state), not only in
the GitHub cache (which GitHub deletes after 7 unused days or when it runs out of room) and
never in this public repository.

  python src/state.py restore   start of a run: private copy -> data/history and plan/
  python src/state.py save      end of a run:   data/history -> private copy, committed and pushed

Layout of the private repository (one folder per channel, never mixed):
  <channel>/history/made.json              stories of the last 7 days (the editor's "already made")
  <channel>/history/momentum.json          story velocity between runs
  <channel>/history/music_used.json        music rotation
  <channel>/history/music_licenses.json    the licence record of every library track
  <channel>/history/ledger/scripts.jsonl   every script made (permanent: repetition checks)
  <channel>/history/ledger/assets.jsonl    every picture and clip used, with licence and file hash
  <channel>/history/ledger/videos.jsonl    every video and its gate decision
  <channel>/history/reports/               weekly reports (private, not GitHub Issues)
  <channel>/plan/week.json, niche.json     the weekly plan and competitor scan
  <channel>/runs/<date>_<run id>.tar.gz    each daily run's FULL report and working data (the
                                           public run page shows only a short table): summary.md,
                                           scripts, media and gate decisions, voice timing, Claude
                                           use; kept 14 days. Not the MP3/MP4 files (too big).

If the private copy is missing (first run, or the token is not set), the run still works from
the cache, and the first successful save creates the private copy from it.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHANNEL = os.environ.get("CHANNEL", "nba")
STATE = ROOT / "state"
HOME = STATE / CHANNEL


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    for f in src.rglob("*"):
        if f.is_file():
            target = dst / f.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            n += 1
    return n


RUNS_KEEP_DAYS = 14
# what a run bundle holds (paths inside data/): small text and JSON only
RUN_FILES = ["summary.md", "claude_usage.jsonl", "editor.json", "skip_reason.txt", "scripts/short_*.json",
             "media/short_*.json", "gate/short_*.json", "audio/short_*.timing.json",
             "sources/short_*.json"]     # the source texts each Short was checked against (replay.py)


def bundle_run(home: Path | None = None, today: datetime | None = None) -> Path | None:
    """The run's full report + working data, packed into <channel>/runs/ (private). Bundles older
    than RUNS_KEEP_DAYS are removed. Returns the bundle (None: nothing to keep)."""
    home = home or HOME
    today = today or datetime.now(timezone.utc)
    files = sorted({f for pattern in RUN_FILES for f in DATA.glob(pattern) if f.is_file()})
    if not files:
        return None
    runs = home / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    name = f"{today:%Y-%m-%d}_{os.environ.get('GITHUB_RUN_ID', 'local')}.tar.gz"
    with tarfile.open(runs / name, "w:gz") as tar:
        for f in files:
            tar.add(f, arcname=str(f.relative_to(DATA)))
    cutoff = (today - timedelta(days=RUNS_KEEP_DAYS)).strftime("%Y-%m-%d")
    for old in runs.glob("*.tar.gz"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", old.name)
        if m and m.group(1) < cutoff:
            old.unlink()
    return runs / name


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(STATE), *args], capture_output=True, text=True)


def restore() -> None:
    if not (STATE / ".git").exists():
        print("[!] private state repository not available: working from the cache only")
        return
    n = copy_tree(HOME / "history", DATA / "history") if (HOME / "history").exists() else 0
    p = copy_tree(HOME / "plan", ROOT / "plan") if (HOME / "plan").exists() else 0
    print(f"[+] restored {n} history files and {p} plan files from the private repository")


def save(message: str = "") -> None:
    if not (STATE / ".git").exists():
        print("[!] private state repository not available: history kept in the cache only")
        return
    if (DATA / "history").exists():
        copy_tree(DATA / "history", HOME / "history")
    if os.environ.get("SAVE_RUN_REPORT") == "1":     # the daily pipeline only (not the weekly run)
        try:
            kept = bundle_run()
            if kept:
                print(f"[+] full run report kept privately: {CHANNEL}/runs/{kept.name}")
        except Exception as exc:
            print(f"[!] run report not kept ({exc}); the history is still saved")
    for name in ("week.json", "niche.json"):
        if (ROOT / "plan" / name).exists() and os.environ.get("SAVE_PLAN") == "1":
            (HOME / "plan").mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "plan" / name, HOME / "plan" / name)
    git("config", "user.name", "nba-rumors-bot")
    git("config", "user.email", "nba-rumors-bot@users.noreply.github.com")
    git("add", "-A")
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("[i] nothing new to save")
        return
    git("commit", "-m", message or f"{CHANNEL}: run {os.environ.get('GITHUB_RUN_ID', 'local')}")
    for attempt in range(4):
        pushed = git("push")
        if pushed.returncode == 0:
            print("[+] history saved to the private repository")
            return
        # someone else pushed first (e.g. you edited the music licences): rebase and retry
        git("pull", "--rebase", "--autostash")
        time.sleep(3 * (attempt + 1))
    print(f"[!] could not push the history: {pushed.stderr[-300:]}")
    sys.exit(1)


if __name__ == "__main__":
    {"restore": restore, "save": save}[sys.argv[1]]()

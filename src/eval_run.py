"""The quality eval (D69, his answers 2026-11-17): the 23 kept stories (eval_set.py) are made
again by today's code, as FULL Shorts (script, voice, pictures, final read, the fix after it,
video, gate), one at a time, so a change to a writing or checking rule shows in numbers.

  - The repetition check is OFF here: every story's own Short is already in the history, so it
    would "repeat" itself (in a normal run nothing changes).
  - It touches none of the channel's permanent records (made Shorts, licence ledger, music and
    beef rotation): data/history is never saved back. The one exception: the photo tag cache
    (what is in each photo), which saves later runs Claude calls.
  - Only the results and the scripts are kept (no MP4), privately:
      <channel>/eval/results/<label>/<story>.json   one per story
      <channel>/eval/results/<label>/summary.md     the table and the one number
  - It runs in parts: on the Claude limit it stops cleanly, keeps what is done, and the next run
    with the same label goes on from where it stopped. Each story is saved as soon as it is done.
  - The one number: Shorts with no problem = the script stage did not hold it AND the final read
    (after the fix) found no error. A story with no Short made counts as a problem.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHANNEL = os.environ.get("CHANNEL", "nba")
STATE = ROOT / "state"
EVAL = STATE / CHANNEL / "eval"
STAGES = ("tts.py", "audio_qc.py", "media.py", "final_read.py", "fix_after_read.py", "render.py", "gate.py")
WORK_DIRS = ("scripts", "sources", "audio", "media", "review", "video", "gate")


class Limit(Exception):
    """The Claude limit: stop, keep what is done."""


def load(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def clean_work() -> None:
    for d in WORK_DIRS:
        shutil.rmtree(DATA / d, ignore_errors=True)
        (DATA / d).mkdir(parents=True, exist_ok=True)


def make_script(story: dict, sources: list[dict]) -> dict:
    """The script stage on this story, exactly as a run would call it, with the kept sources."""
    import script
    editor = {"topics": [{"headline": h} for h in story.get("known_headlines") or []], "ranked": [],
              "shorts": [], "long": {}}
    tid = len(editor["topics"])
    editor["topics"].append(story["topic"])
    editor["ranked"].append({"id": tid, **(story.get("judged") or {})})
    editor["shorts"] = [tid]
    script.gather_sources = lambda topic, ed, topic_id: [dict(s) for s in sources]
    script.RECENT.clear()
    script.load_recent = lambda: None          # the repetition check is off in the eval (his answer)
    voice = (ROOT / "voice.md").read_text(encoding="utf-8")
    formulas = json.loads((script.VENDOR / "yt-script" / "hooks.json").read_text(encoding="utf-8"))
    try:
        return script.build_short(1, tid, editor, voice, formulas)
    except script.UsageLimit as exc:
        raise Limit(str(exc)) from exc


def run_stages() -> None:
    for module in STAGES:
        subprocess.run([sys.executable, str(ROOT / "src" / module)], check=False)


def limit_hit() -> bool:
    review = load(DATA / "review" / "short_1.json", {}) or {}
    flags = load(DATA / "media" / "short_1_flags.json", {}) or {}
    return "limit" in str(review.get("failed") or "").lower() or bool(flags.get("unjudged"))


def result_of(story: dict, short: dict | None, why_not: str = "") -> dict:
    if short is None:
        return {"id": story["id"], "headline": story["headline"], "made": False, "why_not": why_not,
                "problem": True}
    review = load(DATA / "review" / "short_1.json", {}) or {}
    gate = load(DATA / "gate" / "short_1.json", {}) or {}
    media = load(DATA / "media" / "short_1.json", []) or []
    timing = load(DATA / "audio" / "short_1.timing.json", {}) or {}
    fixes = load(DATA / "review" / "short_1_fixes.json", []) or []
    short = load(DATA / "scripts" / "short_1.json", short) or short       # after the fix (stage 4e)
    checks = (short.get("compliance") or {}).get("checks") or {}
    held = not short.get("ready", True) or (short.get("compliance") or {}).get("verdict", "PASS") != "PASS"
    errors = review.get("errors") or []
    return {
        "id": story["id"], "headline": story["headline"], "made": True,
        "problem": held or review.get("verdict") != "PASS",
        "script_held": held, "script_why": (short.get("retention") or {}).get("hard") or [],
        "numbers_not_in_sources": len(short.get("unsupported_numbers") or []),
        "quotes_not_in_sources": len(short.get("unsupported_quotes") or []),
        "details_not_in_sources": len(short.get("unsupported_details") or []),
        "longest_copy": (checks.get("original_storytelling") or {}).get("longest_copy"),
        "hook_score": (short.get("hook") or {}).get("score"), "words": short.get("words"),
        "seconds": round(timing.get("duration") or 0, 1), "heard": timing.get("heard"),
        "final_read": review.get("verdict") or "-", "final_read_failed": review.get("failed") or "",
        "final_read_errors": [f"{e.get('kind')}: {e.get('what', '')[:120]}" for e in errors],
        "fix_tries": len(fixes),
        "photos": sum(1 for it in media if it for _ in [it] + (it.get("alts") or [])),
        "empty_beats": sum(1 for it in media if not it),
        "gate": gate.get("verdict") or "-",
        "gate_not_pass": sorted(k for k, c in (gate.get("checks") or {}).items() if c.get("verdict") != "PASS"),
        "script": {"hook": (short.get("hook") or {}).get("text", ""), "beats": [b.get("say", "") for b in short.get("beats") or []],
                   "pictures": [[(x or {}).get("title", "") for x in [it] + (it.get("alts") or [])] if it else []
                                for it in media]},
        "original": story.get("original"),
    }


def summary(label: str, results: list[dict], total: int, previous: tuple[str, list[dict]] | None) -> str:
    done = len(results)
    ok = sum(1 for r in results if not r["problem"])

    def num(rs, key):
        vals = [r.get(key) for r in rs if isinstance(r.get(key), (int, float))]
        return round(sum(vals) / len(vals), 2) if vals else "-"
    lines = [f"# Quality eval: {label}", "",
             f"**Shorts with no problem: {ok} of {done}" + (f" ({ok / done:.0%})" if done else "") + "**"
             + ("" if done == total else f" - in progress: {done} of {total} stories done"), ""]
    if previous and len(previous[1]) == total and done == total:
        p_ok = sum(1 for r in previous[1] if not r["problem"])
        lines += [f"Before ({previous[0]}): {p_ok} of {total}. Change: {ok - p_ok:+d}.", ""]
    keys = ("numbers_not_in_sources", "quotes_not_in_sources", "details_not_in_sources", "longest_copy",
            "hook_score", "seconds", "fix_tries", "photos", "empty_beats")
    lines += ["| measure | average now" + (f" | {previous[0]}" if previous else "") + " |",
              "|---|---|" + ("---|" if previous else "")]
    for k in keys:
        lines.append(f"| {k} | {num(results, k)}" + (f" | {num(previous[1], k)}" if previous else "") + " |")
    lines += ["", "| story | problem | script held | final read | errors | gate | hook |", "|---|---|---|---|---|---|---|"]
    for r in results:
        if not r.get("made"):
            lines.append(f"| {r['headline'][:60]} | ⛔ | not made: {r.get('why_not', '')[:60]} | - | - | - | - |")
            continue
        lines.append(f"| {r['headline'][:60]} | {'⛔' if r['problem'] else '✅'} | {'yes' if r['script_held'] else 'no'} | "
                     f"{r['final_read']} | {len(r['final_read_errors'])} | {r['gate']} | {r['script']['hook'][:70]} |")
    return "\n".join(lines) + "\n"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(STATE), *args], capture_output=True, text=True)


def save(label: str, message: str) -> None:
    """The eval's results and the photo tag cache only: nothing else of the channel's record."""
    tags = DATA / "history" / "photo_tags.json"
    if tags.exists():
        dest = STATE / CHANNEL / "history" / "photo_tags.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tags, dest)
    if not (STATE / ".git").exists():
        return
    git("config", "user.name", "nba-rumors-bot")
    git("config", "user.email", "nba-rumors-bot@users.noreply.github.com")
    git("add", str(EVAL.relative_to(STATE)), str((STATE / CHANNEL / "history" / "photo_tags.json").relative_to(STATE)))
    if git("diff", "--cached", "--quiet").returncode == 0:
        return
    git("commit", "-m", message)
    for _ in range(3):
        if git("push").returncode == 0:
            return
        git("pull", "--rebase", "--autostash")
        time.sleep(5)


def main() -> None:
    label = (os.environ.get("EVAL_LABEL") or "").strip() or \
        subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    stories = sorted(p for p in (EVAL / "set").iterdir() if (p / "story.json").exists()) if (EVAL / "set").exists() else []
    if not stories:
        sys.exit("[!] no eval set in the private repository")
    out = EVAL / "results" / label
    out.mkdir(parents=True, exist_ok=True)
    index = load(EVAL / "results" / "index.json", []) or []
    if label not in index:
        index.append(label)
        (EVAL / "results" / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    prev_label = index[index.index(label) - 1] if index.index(label) > 0 else None

    def collected(lab):
        return [load(p, {}) for p in sorted((EVAL / "results" / lab).glob("*.json"))]
    previous = (prev_label, collected(prev_label)) if prev_label else None
    for folder in stories:
        story = load(folder / "story.json", {})
        if (out / f"{story['id']}.json").exists():
            continue                                   # done in an earlier part
        sources = load(folder / "sources.json", [])
        clean_work()
        try:
            short = make_script(story, sources)
            (DATA / "scripts" / "short_1.json").write_text(json.dumps(short, indent=2, ensure_ascii=False), encoding="utf-8")
            run_stages()
            if limit_hit():
                raise Limit("reached during the voice, pictures or final read")
            result = result_of(story, short)
        except Limit as exc:
            print(f"[i] Claude limit: the eval stops here and goes on next time ({str(exc)[:100]})")
            break
        except Exception as exc:                    # a story the script stage could not make
            result = result_of(story, None, f"{type(exc).__name__}: {str(exc)[:160]}")
        (out / f"{story['id']}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
        (out / "summary.md").write_text(summary(label, collected(label), len(stories), previous), encoding="utf-8")
        save(label, f"eval {label}: {story['id']}")
        print(f"[+] eval {label}: {story['id']} done")
    (out / "summary.md").write_text(summary(label, collected(label), len(stories), previous), encoding="utf-8")
    save(label, f"eval {label}: summary")


if __name__ == "__main__":
    main()

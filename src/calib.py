"""D81b (his answers 2026-11-19 and 2026-11-26): measure two checks against labelled real cases,
before any change to their prompts is accepted.

The final read (stage 4d): one case = one whole Short with every line (his answer), read from the
STORED final verdict of the receipts2 and factsheet evals (the one after the second checks, D76/D80;
his answer), so it needs no Claude call. A catch = the error's line AND kind match the label (his
answer); a line-only match is shown apart. Lines whose rule changed after the verdict (D94 speaker,
D90b time) and lines quoted as examples in a prompt (D85 item 6) are excluded from the numbers and
shown apart (his answers). Catches, misses and false alarms are counted separately, never one total
accuracy (D85 item 2).

The hook truth check (D17): one case = the chosen hook of every Short of the receipts2 and classfix
bases (his answer). An accepted hook leaves no mark and failed reads left none either, so the stored
data cannot tell "read and accepted" from "never read": the check is run again on the cases (his
answer; a Claude job, only with his yes, after the limit resets), and that fresh verdict is measured.

Cases and labels live in the private repository (nba/eval/calib/: articles). Labels are written by
hand after the limit resets, with the blind labelling of D85 item 4.

  python src/calib.py build      # the case lists (no Claude, no network)
  python src/calib.py hooks      # run the hook truth check on the hook cases (Claude; his yes)
  python src/calib.py measure    # compare verdicts with labels
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
EVAL = STATE / "nba" / "eval"
CALIB = EVAL / "calib"
FINAL_READ_EVALS = ("receipts2", "factsheet")   # his answer: the stored final verdicts
HOOK_BASES = ("receipts2", "classfix")          # his answer: every Short's chosen hook


def load(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def final_read_cases(evals: Path = EVAL) -> list[dict]:
    """Every made Short of the chosen evals, with its lines and the stored final verdict."""
    out = []
    for label in FINAL_READ_EVALS:
        for f in sorted((evals / "results" / label).glob("*.json")):
            r = load(f, {})
            if not r.get("made"):
                continue
            sc = r.get("script") or {}
            out.append({"case": f"{label}/{r['id']}", "eval": label, "id": r["id"], "headline": r.get("headline", ""),
                        "lines": [sc.get("hook", "")] + list(sc.get("beats") or []),
                        "pictures": r.get("picture_choice") or [],
                        "verdict": [{"line": e.get("line"), "kind": e.get("kind", "")}
                                    for e in (r.get("final_read_full") or {}).get("errors") or [] if isinstance(e, dict)]})
    return out


def hook_cases(evals: Path = EVAL) -> list[dict]:
    """The chosen hook of every Short of the chosen bases, with where its sources are kept."""
    out = []
    for base in HOOK_BASES:
        for d in sorted(p for p in (evals / "base" / base).iterdir() if (p / "script.json").exists()):
            s = load(d / "script.json", {})
            hook = (s.get("hook") or {}).get("text", "")
            if hook:
                out.append({"case": f"{base}/{d.name}", "base": base, "id": d.name, "hook": hook,
                            "sources": f"base/{base}/{d.name}/sources.json"})
    return out


def score(cases: list[dict], verdicts: dict, labels: dict) -> dict:
    """Catches (line and kind), line-only matches, misses and false alarms, apart; excluded lines
    (rule changed after the verdict, a prompt's example) are left out of all of them and listed."""
    res = {"catch": [], "line_only": [], "miss": [], "false_alarm": [], "excluded": [], "unlabelled": []}
    for c in cases:
        lab = labels.get(c["case"])
        if lab is None:
            res["unlabelled"].append(c["case"])
            continue
        out = {(x["line"], x.get("why", "")) for x in lab.get("excluded") or []}
        skip = {line for line, _ in out}
        res["excluded"] += [(c["case"], line, why) for line, why in sorted(out, key=lambda t: (t[0], t[1]))]
        real = [(x["line"], x.get("kind", "")) for x in lab.get("errors") or [] if x["line"] not in skip]
        said = [(x["line"], x.get("kind", "")) for x in verdicts.get(c["case"], []) if x["line"] not in skip]
        used = set()
        for line, kind in real:
            if (line, kind) in said:
                res["catch"].append((c["case"], line, kind))
                used.add((line, kind))
            elif any(sl == line for sl, _ in said):
                res["line_only"].append((c["case"], line, kind))
                used |= {(sl, sk) for sl, sk in said if sl == line}
            else:
                res["miss"].append((c["case"], line, kind))
        res["false_alarm"] += [(c["case"], line, kind) for line, kind in said if (line, kind) not in used]
    return res


def report(name: str, res: dict) -> str:
    n = {k: len(v) for k, v in res.items()}
    lines = [f"## {name}", "",
             f"- catches (line and kind): {n['catch']}", f"- caught on the line, wrong kind: {n['line_only']}",
             f"- missed: {n['miss']}", f"- false alarms: {n['false_alarm']}",
             f"- excluded lines (rule changed / prompt example): {n['excluded']}", f"- not labelled yet: {n['unlabelled']}", ""]
    for k in ("miss", "false_alarm", "line_only", "excluded"):
        lines += [f"- {k}: {x}" for x in res[k]]
    return "\n".join(lines) + "\n"


def run_hooks(cases: list[dict]) -> dict:
    """The hook truth check, as the pipeline runs it, on every hook case (Claude)."""
    sys.path.insert(0, str(ROOT / "src"))
    import script                                      # noqa: E402  (the pipeline's own check)
    got = {}
    for c in cases:
        hook = {"text": c["hook"]}
        verdict = script.check_hook_truth(hook, load(EVAL / c["sources"], []))
        got[c["case"]] = {"verdict": verdict, "why": hook.get("overstated", "")}
    return got


def main() -> None:
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    CALIB.mkdir(parents=True, exist_ok=True)
    if step == "build":
        (CALIB / "final_read_cases.json").write_text(json.dumps(final_read_cases(), indent=1, ensure_ascii=False), encoding="utf-8")
        (CALIB / "hook_cases.json").write_text(json.dumps(hook_cases(), indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"[+] {len(final_read_cases())} final read cases, {len(hook_cases())} hook cases")
    elif step == "hooks":
        cases = load(CALIB / "hook_cases.json", [])
        (CALIB / "hook_verdicts.json").write_text(json.dumps(run_hooks(cases), indent=1, ensure_ascii=False), encoding="utf-8")
    elif step == "measure":
        fr = load(CALIB / "final_read_cases.json", [])
        text = report("final read", score(fr, {c["case"]: c["verdict"] for c in fr}, load(CALIB / "final_read_labels.json", {})))
        hk = load(CALIB / "hook_cases.json", [])
        hv = {k: ([{"line": 0, "kind": "OVERSTATED"}] if v.get("verdict") == "overstated" else [])
              for k, v in load(CALIB / "hook_verdicts.json", {}).items()}
        text += report("hook truth", score([c for c in hk if c["case"] in hv], hv, load(CALIB / "hook_labels.json", {})))
        (CALIB / "report.md").write_text(text, encoding="utf-8")
        print(text)
    else:
        sys.exit("usage: python src/calib.py build | hooks | measure")


if __name__ == "__main__":
    main()

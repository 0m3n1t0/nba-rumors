"""The quality eval set (D69, his answers 2026-11-17): every kept Short whose source texts were
saved (23 on 2026-11-17), copied once into the private repository so the 14-day clean-up of
run bundles never takes them away:

  <channel>/eval/set/<run>_<short>/story.json   the story as the script stage got it: the topic,
                                                the editor's judgment of it, the editor's topics
                                                (their headlines name the day's known people),
                                                and the original Short's own result for reference
  <channel>/eval/set/<run>_<short>/sources.json the source texts it was written from

  python src/eval_set.py <folder with the unpacked run bundles> <the set folder>

A historic beef (evergreen) is not in the editor's file: its topic is made again the way
evergreen.candidates made it (the same headline, the same "why")."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def load(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def evergreen_topic(short: dict, sources: list[dict]) -> tuple[dict, dict]:
    import evergreen
    key = short["evergreen"]
    people = key.split(" vs ")
    label = next((lab for a, b, lab in evergreen.BANK if evergreen.key_of(a, b) == key), key)
    newest = short["headline"].split(" (back in the news:")[0]
    topic = {"headline": short["headline"], "items": [{k: s.get(k) for k in ("title", "link", "publisher", "tier")}
                                                      for s in sources],
             "verified": True, "outlets": len(sources), "star_names": people, "evergreen": key}
    judged = {"nba": True, "kind": "player_vs_player", "conflict": True, "two_versions": "", "same_as": [],
              "why": (f"HISTORIC BEEF back in the news. The feud itself is OLD ({label}); the fresh "
                      f"reason is: \"{newest}\". Open on the fresh reason, then tell the old feud with its "
                      "real dates from the sources (\"back in 2004...\"). NEVER present the old events as "
                      "new, and give every date only as the sources give it.")}
    return topic, judged


def build(runs: Path, out: Path) -> list[str]:
    made = []
    for run in sorted(p for p in runs.iterdir() if p.is_dir()):
        editor = load(run / "editor.json", {})
        for path in sorted((run / "scripts").glob("short_*.json")):
            name = path.stem
            if not name.replace("short_", "").isdigit():
                continue
            sources = load(run / "sources" / f"{name}.json")
            short = load(path, {})
            if not sources or not short.get("headline") or not editor.get("topics"):
                continue
            tid = short.get("topic_id")
            if short.get("evergreen"):
                topic, judged = evergreen_topic(short, sources)
            elif isinstance(tid, int) and tid < len(editor["topics"]):
                topic = editor["topics"][tid]
                judged = next((r for r in editor.get("ranked", []) if r.get("id") == tid), {})
            else:
                continue
            story = {"id": f"{run.name}_{name}", "headline": short["headline"], "topic": topic,
                     "judged": {k: v for k, v in judged.items() if k != "id"},
                     "known_headlines": [t.get("headline", "") for t in editor["topics"]],
                     "original": {"hook": (short.get("hook") or {}).get("text", ""),
                                  "beats": [b.get("say", "") for b in short.get("beats") or []],
                                  "gate": (load(run / "gate" / f"{name}.json", {}) or {}).get("verdict"),
                                  "final_read": (load(run / "review" / f"{name}.json", {}) or {}).get("verdict")}}
            folder = out / story["id"]
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "story.json").write_text(json.dumps(story, indent=1, ensure_ascii=False), encoding="utf-8")
            (folder / "sources.json").write_text(json.dumps(sources, ensure_ascii=False), encoding="utf-8")
            made.append(story["id"])
    return made


if __name__ == "__main__":
    got = build(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"[+] eval set: {len(got)} stories")

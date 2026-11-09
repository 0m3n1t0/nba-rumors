"""Monetization safety checks that are ENFORCED in code (not only asked of Claude in a prompt).

Every Short gets a verdict per check: PASS, REVIEW (held until a person looks) or REJECT
(never published). gate.py combines them with the media, music and technical checks into the
final publication decision. Everything here is deterministic Python: no Claude calls.

The channel stays what it is: NBA beef, rumors, trades and drama. These checks do not suppress
controversy; they stop what YouTube and advertisers punish: invented facts, rumors told as
facts, invented sources, read-out articles, misleading titles and unsafe wording.
"""

from __future__ import annotations

import re
import unicodedata

PASS, REVIEW, REJECT = "PASS", "REVIEW", "REJECT"
RANK = {PASS: 0, REVIEW: 1, REJECT: 2}
STATUSES = ("CONFIRMED", "REPORTED", "RUMOR", "UNVERIFIED")


def worst(*verdicts: str) -> str:
    return max(verdicts, key=lambda v: RANK[v]) if verdicts else PASS


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text or "")
                   if not unicodedata.combining(c)).lower().replace("’", "'")


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", fold(text))


def material(sources: list[dict]) -> str:
    return " ".join(f"{s.get('title', '')} {s.get('summary', '')} {s.get('text', '')}" for s in sources)


# ---------- 1. who first reported it (original reporting) ----------

# Insiders whose reports other outlets repeat. Two outlets citing the SAME insider are ONE
# report, not two (the "repeated report" trap).
INSIDERS = ["shams charania", "marc stein", "jake fischer", "chris haynes", "brian windhorst",
            "adrian wojnarowski", "jon krawczynski", "sam amick", "anthony slater", "michael scotto",
            "evan sidery", "ramona shelburne", "kevin o'connor", "chris mannix", "ian begley",
            "stefan bondy", "marc spears", "jovan buha", "dave mcmenamin", "tim bontemps",
            "bobby marks", "kendra andrews", "law murray", "kelly iko", "mike vorkunov",
            "fred katz", "joe vardon", "eric nehm", "keith pompey", "tim macmahon"]
OFFICIAL = re.compile(r"\bnba\.com\b|\bnba communications\b|\b(official(ly)?|announced|statement|"
                      r"press release|confirmed by the (team|league|nba))\b", re.I)
ATTRIBUTION = re.compile(r"\b(?:per|according to|reported by|first reported by|via)\s+"
                         r"((?:the\s+)?[A-Z][\w'.&-]*(?:\s+[A-Z][\w'.&-]*){0,3})")


def original_reporters(sources: list[dict]) -> dict:
    """Who broke it, as far as the articles say. Returns the distinct original reports:
    {"insiders": [...], "outlets": [...], "official": bool}. An outlet that only repeats a named
    insider adds nothing; an outlet with no attribution counts as its own report."""
    found_insiders, own_reports, official = set(), set(), False
    for s in sources:
        text = f"{s.get('title', '')} {s.get('summary', '')} {s.get('text', '')}"
        low = fold(text)
        named = {i for i in INSIDERS if i in low}
        cites_other = bool(ATTRIBUTION.search(text))
        if OFFICIAL.search(text) and s.get("tier") == 1:
            official = True
        if named:
            found_insiders |= named
        elif not cites_other and s.get("text"):
            own_reports.add((s.get("publisher") or "").strip().lower())
    return {"insiders": sorted(found_insiders), "outlets": sorted(o for o in own_reports if o),
            "official": official}


def independent_reports(sources: list[dict]) -> int:
    r = original_reporters(sources)
    return len(r["insiders"]) + len(r["outlets"]) + (1 if r["official"] else 0)


def check_sources(sources: list[dict]) -> tuple[str, list[str], dict]:
    """A story needs at least one trusted (tier 1) outlet or a named insider, read in full."""
    read = [s for s in sources if s.get("text")]
    origin = original_reporters(sources)
    notes = []
    if not read:
        return REJECT, ["no article could be read: the story cannot be verified"], origin
    trusted = any(s.get("tier") == 1 for s in read)
    if not trusted and not origin["insiders"]:
        notes.append("only secondary outlets and no named insider: provenance unclear")
        return REVIEW, notes, origin
    return PASS, notes, origin


# ---------- 2. claim classification (stored in the story data, enforced here) ----------

HEDGE = re.compile(r"\b(per|according to|reportedly|report(s|ed)?|says|said|told|rumou?rs?|"
                   r"sources?|insiders?|could|might|may|eyeing|interested|considering|linked|"
                   r"expected to|in talks|wants?|would|if)\b", re.I)


def check_claims(claims: list[dict], sources: list[dict], spoken: str) -> tuple[str, list[str], list[dict]]:
    """Every important claim carries CONFIRMED / REPORTED / RUMOR / UNVERIFIED, written by the
    script writer and CHECKED here against the sources. A status is downgraded when the evidence
    does not carry it (never upgraded because several sites repeat it). Rumors and reports must
    be attributed when spoken; an unverified claim holds the Short."""
    notes, out = [], []
    if not claims:
        return REVIEW, ["no claims listed: the facts cannot be classified"], []
    origin = original_reporters(sources)
    independent = independent_reports(sources)
    verdict = PASS
    for c in claims:
        status = str(c.get("status", "")).upper()
        if status not in STATUSES:
            status = "UNVERIFIED"
        idx = c.get("source")
        src = sources[idx - 1] if isinstance(idx, int) and 1 <= idx <= len(sources) else None
        if src is None and status != "UNVERIFIED":
            notes.append(f"claim has no valid source: {c.get('text', '')[:60]}")
            status = "UNVERIFIED"
        if status == "CONFIRMED" and not (origin["official"] or independent >= 2):
            status = "REPORTED"
            notes.append(f"downgraded to REPORTED (no official word, one original report): {c.get('text', '')[:60]}")
        if status == "REPORTED" and src is not None and src.get("tier") != 1 and not origin["insiders"]:
            status = "RUMOR"
            notes.append(f"downgraded to RUMOR (no trusted outlet or named reporter): {c.get('text', '')[:60]}")
        out.append({**c, "status": status})
        if status == "UNVERIFIED":
            verdict = worst(verdict, REVIEW)
            notes.append(f"UNVERIFIED claim: {c.get('text', '')[:80]}")
    if any(c["status"] in ("REPORTED", "RUMOR") for c in out) and not HEDGE.search(spoken):
        verdict = worst(verdict, REJECT)
        notes.append("a report or rumor is told as fact: no attribution in the narration")
    return verdict, notes, out


# ---------- 3. fabrication: invented sources, conversations, quotes ----------

ANON = re.compile(r"\b(a (league |team )?source|sources (say|said|tell|told|close)|people close to|"
                  r"insiders? (say|said|tell)|one teammate|a teammate (said|told)|told teammates|"
                  r"in the locker room,? he (said|told|yelled|screamed)|behind closed doors,? he)\b", re.I)


def check_fabrication(spoken: str, sources: list[dict], bad_quotes: list[str],
                      unsupported_numbers: list[str]) -> tuple[str, list[str]]:
    notes, verdict = [], PASS
    mat = fold(material(sources))
    for m in ANON.finditer(spoken):
        phrase = fold(m.group(0))
        # what the articles must mention for the phrase to be honest
        need = ("locker room" if "locker" in phrase else "closed doors" if "closed doors" in phrase
                else "people close" if "people close" in phrase else "teammate" if "teammate" in phrase
                else "insider" if "insider" in phrase else "source")
        if need not in mat:
            verdict = REJECT
            notes.append(f"invented source or conversation: \"{m.group(0)}\" is not in any source")
    if bad_quotes:
        verdict = REJECT
        notes.append(f"quote not found in the sources: {bad_quotes[0][:60]}")
    if unsupported_numbers:
        verdict = worst(verdict, REVIEW)
        notes.append(f"numbers not in the sources: {', '.join(unsupported_numbers)}")
    return verdict, notes


# ---------- 4. original storytelling (not a read-out article) ----------

COPY_RUN = 12        # this many words in a row copied from an article (outside a quote) = read out
COPY_SHARE = 0.25    # share of the script's 5-word runs found in the articles


def check_originality(beats: list[dict], sources: list[dict]) -> tuple[str, list[str], dict]:
    say = " ".join(b.get("say", "") for b in beats)
    unquoted = re.sub(r'["“][^"”]*["”]', " ", say)
    w = words(unquoted)
    mat = " " + " ".join(words(material(sources))) + " "
    grams = [" ".join(w[i:i + 5]) for i in range(len(w) - 4)]
    share = sum(1 for g in grams if f" {g} " in mat) / len(grams) if grams else 0.0
    longest = 0
    for i in range(len(w)):
        for j in range(i + longest + 1, len(w) + 1):
            if f" {' '.join(w[i:j])} " in mat:
                longest = j - i
            else:
                break
    roles = {str(b.get("role", "")).lower() for b in beats}
    notes, verdict = [], PASS
    if longest >= COPY_RUN:
        verdict = REVIEW
        notes.append(f"{longest} words in a row copied from an article")
    if share > COPY_SHARE:
        verdict = REVIEW
        notes.append(f"{share:.0%} of the script repeats article wording")
    if not roles & {"context", "analysis"}:
        verdict = REVIEW
        notes.append("no context or analysis beat: the Short only retells the news")
    return verdict, notes, {"copied_share": round(share, 2), "longest_copy": longest,
                            "roles": sorted(r for r in roles if r)}


# ---------- 5. title and first-frame accuracy ----------

EVENTS = {
    "traded": r"\btrad(ed|es)\b|\bdealt\b|\btrade (is )?(done|official|complete)",
    "fired": r"\bfired\b|\bsacked\b|\bdismissed\b",
    "suspended": r"\bsuspend(ed|s|sion)\b",
    "ejected": r"\beject(ed|s|ion)\b|\bkicked out\b|\bthrown out\b",
    "arrested": r"\barrest(ed|s)?\b|\bcharged\b|\bindicted\b",
    "retired": r"\bretir(ed|es|ement)\b",
    "signed": r"\bsign(ed|s)\b|\bagreed to\b",
    "waived": r"\bwaiv(ed|es)\b|\breleased\b|\bcut\b",
    "fined": r"\bfin(ed|es)\b",
    "injured": r"\b(torn|tear|out for (the )?season|season-ending)\b",
    "fight": r"\bfight\b|\bbrawl\b|\bpunch(ed)?\b|\bshov(e|ed)\b",
    "dead": r"\bdied\b|\bdead\b|\bpassed away\b",
}
TITLE_HEDGE = re.compile(r"\?|\b(rumou?rs?|reportedly|could|might|wants?|eyeing|interested|"
                         r"considering|in talks|linked|report|trade talks?)\b", re.I)
STOP_NAMES = {"nba", "the", "is", "was", "vs", "and", "why", "how", "who", "what", "did", "does",
              "can", "will", "just", "real", "big", "new", "not", "now", "his", "her", "this", "that",
              "trade", "beef", "drama", "insane", "shot", "gone", "over", "fan", "fans", "team", "rumor"}


TEAMS = {"lakers", "celtics", "warriors", "knicks", "bucks", "heat", "nuggets", "suns", "mavericks",
         "mavs", "76ers", "sixers", "nets", "bulls", "cavaliers", "cavs", "thunder", "spurs", "rockets",
         "clippers", "kings", "pistons", "pacers", "hawks", "hornets", "magic", "raptors", "wizards",
         "jazz", "blazers", "grizzlies", "pelicans", "timberwolves", "wolves"}


def names_in(text: str, known: set[str] | None = None) -> set[str]:
    """The names (people, teams) in a title or first-frame text, folded. A Capitalized word
    counts as a name. An ALL-CAPS word is usually emphasis ("a SHOT", "INSANE"), so it counts
    only when it is a known NBA name (a team, or a name in today's NBA headlines): that way
    "BROWN vs LEBRON" is checked while "was a SHOT" is not."""
    known = (known or set()) | TEAMS
    out = set()
    for tok in re.findall(r"[A-Za-zÀ-ɏ][\w'À-ɏ-]+", text or ""):
        f = re.sub(r"'s$", "", fold(tok)).strip("'")
        if len(f) <= 2 or f in STOP_NAMES:
            continue
        if tok.isupper():
            if f in known:
                out.add(f)
        elif tok[0].isupper():
            out.add(f)
    return out


def known_names(headlines: list[str]) -> set[str]:
    """Every capitalized name word in today's NBA headlines (all stories), folded: the pool an
    ALL-CAPS first-frame word is matched against."""
    out = set()
    for h in headlines:
        for tok in re.findall(r"[A-ZÀ-ɏ][\w'À-ɏ-]+", h or ""):
            f = re.sub(r"'s$", "", fold(tok)).strip("'")
            if len(f) > 2 and f not in STOP_NAMES:
                out.add(f)
    return out


def check_headline(text: str, claims: list[dict], sources: list[dict], kind: str,
                   known: set[str] | None = None) -> tuple[str, list[str]]:
    """kind = "title" or "thumbnail". Names must be in the story; an event word (traded,
    fired, ejected...) must happen in the sources; a report or rumor may not be stated as done.
    Curiosity and drama are fine: questions and hedges pass."""
    if not text:
        return (REVIEW, [f"no {kind}"]) if kind == "title" else (PASS, [])
    mat = fold(material(sources)) + " " + fold(" ".join(c.get("text", "") for c in claims))
    notes, verdict = [], PASS
    missing = sorted(n for n in names_in(text, known) if n not in mat)
    if missing:
        verdict = REJECT
        notes.append(f"{kind} names someone the story does not: {', '.join(missing)}")
    low = fold(text)
    statuses = {c.get("status") for c in claims}
    for event, pat in EVENTS.items():
        if re.search(pat, low):
            if not re.search(pat, mat):
                verdict = REJECT
                notes.append(f"{kind} says \"{event}\" but no source reports it")
            elif "CONFIRMED" not in statuses and not TITLE_HEDGE.search(text):
                verdict = worst(verdict, REVIEW)
                notes.append(f"{kind} states \"{event}\" as done, but the story is only reported")
    return verdict, notes


# ---------- 6. advertiser suitability and sensitive content ----------

PROFANITY = re.compile(r"\b(f+u+c+k\w*|f[\-—–*]+\s?(it|up|ing|you)?|sh[i1]t\w*|b[i1]tch\w*|"
                       r"motherf\w*|c[u*]nt|a+ss+hole|dick(head)?|bastard|pussy|n[i1]gg\w*|f[a@]gg?\w*)\b", re.I)
CATEGORIES = {
    "sexual": r"\bsexual(ly)? (assault|misconduct|harass\w*|abuse)\b|\brape\b|\bgroom(ing|ed)\b",
    "violence": r"\b(stabb(ed|ing)|shot (dead|and killed)|murder\w*|killed|gunfire|bloody|gore)\b",
    "crime": r"\b(arrest(ed)?|charged with|indict(ed|ment)|felony|dui|domestic (violence|abuse)|"
             r"assault charges?|police (report|investigation)|lawsuit|sued)\b",
    "drugs": r"\b(cocaine|heroin|meth|fentanyl|overdos\w*|drug (use|test|suspension))\b",
    "hate": r"\b(racist|racial slur|homophobic|anti-?semitic|hate speech|slur)\b",
    "threat": r"\b(threaten(ed|ing)? to (kill|hurt|shoot)|death threats?)\b",
    "self_harm": r"\b(suicid\w*|self-harm)\b",
    "private": r"\b(home address|phone number|social security|medical records?)\b",
}
ALWAYS_REVIEW = {"sexual", "violence", "hate", "self_harm"}
INSULT = re.compile(r"\b(he|she|they|[A-Z][a-z]+) (is|was|are|looks like) (a |an )?(clown|idiot|moron|"
                    r"loser|joke|fraud|pathetic|stupid)\b")
RESPONSE = re.compile(r"\b(denied|denies|deny|responded|response|statement|declined to comment|"
                      r"no comment|has(n't| not) commented|lawyer|attorney|apologi[sz]ed)\b", re.I)


def check_suitability(spoken: str, title: str, thumb: str, hook: str, sources: list[dict],
                      claims: list[dict], origin: dict) -> tuple[str, list[str], list[str]]:
    """Legitimate sports drama passes (beef, trash talk, fines, trade demands, ejections).
    Profanity never goes in the title, the first frame or the hook; elsewhere it holds the
    Short. Serious allegations need a trusted outlet or named insider, attribution in the
    narration, and the response when the sources carry one; the most sensitive kinds are
    always held for a person to look at."""
    notes, verdict, found = [], PASS, []
    for where, text in (("title", title), ("first frame", thumb), ("hook", hook)):
        if PROFANITY.search(text or ""):
            verdict = REJECT
            notes.append(f"profanity in the {where}")
    narration = re.sub(r'["“][^"”]*["”]', " ", spoken)
    if PROFANITY.search(spoken):
        verdict = worst(verdict, REVIEW)
        notes.append("profanity in the narration (also inside quotes): reword or bleep")
    if INSULT.search(narration):
        verdict = worst(verdict, REVIEW)
        notes.append(f"the narrator insults a person: \"{INSULT.search(narration).group(0)}\"")
    text = f"{title} {thumb} {spoken}"
    mat = material(sources)
    for cat, pat in CATEGORIES.items():
        if re.search(pat, text, re.I):
            found.append(cat)
    if found:
        strong = any(s.get("tier") == 1 and s.get("text") for s in sources) or bool(origin.get("insiders"))
        attributed = bool(HEDGE.search(spoken))
        response_known = bool(RESPONSE.search(mat))
        response_told = bool(RESPONSE.search(spoken))
        if "private" in found:
            verdict = REJECT
            notes.append("private personal information")
        if set(found) & ALWAYS_REVIEW:
            verdict = worst(verdict, REVIEW)
            notes.append(f"sensitive topic ({', '.join(sorted(set(found) & ALWAYS_REVIEW))}): held for a person to check")
        rest = set(found) - ALWAYS_REVIEW - {"private"}
        if rest:
            if not strong:
                verdict = worst(verdict, REVIEW)
                notes.append(f"{', '.join(sorted(rest))} allegation without a trusted outlet or named insider")
            if not attributed:
                verdict = worst(verdict, REJECT)
                notes.append(f"{', '.join(sorted(rest))} allegation told as proven fact (no attribution)")
            if response_known and not response_told:
                verdict = worst(verdict, REVIEW)
                notes.append("the sources carry a response or denial that the Short leaves out")
    return verdict, notes, found


# ---------- the text part of the gate (run in script.py; media/music/technical in gate.py) ----------

def evaluate_script(short: dict, sources: list[dict], known: set[str] | None = None) -> dict:
    spoken = short.get("spoken", "")
    title = (short.get("titles") or [{}])[0].get("title", "") if short.get("titles") else ""
    thumb = short.get("thumbnail_text", "")
    hook = (short.get("hook") or {}).get("text", "")
    checks = {}
    v, n, origin = check_sources(sources)
    checks["source_verification"] = {"verdict": v, "notes": n, "origin": origin}
    v, n, claims = check_claims(short.get("claims") or [], sources, spoken)
    checks["claim_classification"] = {"verdict": v, "notes": n}
    v, n = check_fabrication(spoken, sources, short.get("unsupported_quotes", []),
                             short.get("unsupported_numbers", []))
    checks["factual_accuracy"] = {"verdict": v, "notes": n}
    v, n, stats = check_originality(short.get("beats", []), sources)
    checks["original_storytelling"] = {"verdict": v, "notes": n, **stats}
    checks["repetition"] = ({"verdict": REVIEW, "notes": [f"too similar to: {short['too_similar_to']}"]}
                            if short.get("too_similar_to") else {"verdict": PASS, "notes": []})
    v, n = check_headline(title, claims, sources, "title", known)
    checks["title_accuracy"] = {"verdict": v, "notes": n}
    v, n = check_headline(thumb, claims, sources, "thumbnail", known)
    checks["thumbnail_accuracy"] = {"verdict": v, "notes": n}
    v, n, cats = check_suitability(spoken, title, thumb, hook, sources, claims, origin)
    checks["advertiser_suitability"] = {"verdict": v, "notes": n, "topics": cats}
    return {"claims": claims, "checks": checks,
            "verdict": worst(*(c["verdict"] for c in checks.values()))}


def pick_safe_title(titles: list[dict], claims: list[dict], sources: list[dict],
                    known: set[str] | None = None) -> list[dict]:
    """Titles that pass the accuracy check go first (the best-scoring of them wins), so a
    strong but misleading title never leads when an accurate one exists."""
    for t in titles:
        t["accuracy"], t["accuracy_notes"] = check_headline(t["title"], claims, sources, "title", known)
    return sorted(titles, key=lambda t: (RANK[t["accuracy"]], -t.get("score", 0)))

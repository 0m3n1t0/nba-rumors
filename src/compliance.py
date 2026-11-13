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
STATUSES = ("CONFIRMED", "REPORTED", "ANONYMOUS", "RUMOR", "SPECULATION", "UNVERIFIED")
HEDGED = ("ANONYMOUS", "RUMOR", "SPECULATION")   # must be voiced as such in their own sentence


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


# The words that make a sentence a report, a rumor or someone's opinion rather than a plain
# fact: attribution to a person ("Bomani says...", "Windhorst thinks...") counts.
SENTENCE_HEDGE = re.compile(
    r"\b(per|according to|says|said|told|tells|claims?|argues?|insists?|reportedly|report(s|ed|edly)?|rumou?r(s|ed)?|sources?|insiders?|people close|"
    r"could|might|may|expected to|in talks|linked|eyeing|interested|considering|thinks?|believes?|"
    r"predicts?|expects?|suggest(s|ed)?|speculat\w*|whispers?|buzz|hears?|heard|apparently|allegedly)\b",
    re.I)
# The stated-shock hook opens a rumor with its source and a colon ("Shams: the Lakers are
# shopping Reaves."): that names the source in the same sentence, so it counts as attribution.
SOURCE_LEAD = re.compile(r"^\s*(?:[A-Z][\w.'’-]*\s+){0,4}[A-Z][\w.'’-]*\s*:\s")
CONTENT_WORD = re.compile(r"[a-z]{4,}")
# A sentence ends at . ! ? followed by space, but NOT after an initial or a short title:
# "So was Stephen A. smart to stand down?" is ONE question (run 43088629255: the split made
# "So was Stephen A." a sentence of its own, and a good Short was held for "repeating").
SENTENCE_END = re.compile(r"(?<!\b[A-Z]\.)(?<!\bJr\.)(?<!\bSr\.)(?<!\bSt\.)(?<!\bDr\.)(?<!\bMr\.)(?<!\bvs\.)(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    return [x for x in SENTENCE_END.split((text or "").strip()) if x and x.strip()]


def bare_claims(claims: list[dict], spoken: str) -> list[str]:
    """C2 (owner's plan): an anonymous-source report, a rumor or a speculation must sound like
    one IN ITS OWN SENTENCE ("sources say...", "reportedly", "he thinks..."); one "reportedly"
    elsewhere no longer covers it. Returns the claims spoken as plain fact. A REPORTED claim is
    left to the whole-script check: many of them are plain facts no league office announced."""
    # a question asserts nothing ("Did the Lakers just shop Reaves?"): only statements count
    sentences = [x for x in split_sentences(spoken) if not x.strip().endswith("?")]
    out = []
    for c in claims or []:
        if str(c.get("status", "")).upper() not in HEDGED:
            continue
        want = set(CONTENT_WORD.findall(fold(c.get("text", ""))))
        if len(want) < 2:
            continue
        best, best_n = None, 0
        for x in sentences:
            n = len(want & set(CONTENT_WORD.findall(fold(x))))
            if n > best_n:
                best, best_n = x, n
        lead = SOURCE_LEAD.search(best or "")
        # "Lakers: Reaves is on the block." is a headline, not a source: the lead must not be
        # one of the claim's own words
        sourced = bool(lead) and not (set(CONTENT_WORD.findall(fold(lead.group(0)))) & want)
        if best and best_n >= max(2, len(want) // 2) and not SENTENCE_HEDGE.search(best) \
                and not sourced:
            out.append(c.get("text", ""))
    return out


# Words that change WHAT happened: dropped, a movie scene becomes a real scandal (run 43199348111:
# the source said "on-screen kiss", the Short said "Ayesha Curry's kiss").
MEANING_WORD = re.compile(r"\b(on-?screen|in (?:a|the|her|his) (?:movie|film|show|series|ad|commercial|skit)|"
                          r"scripted|alleged(?:ly)?|joked|jokingly|in jest|parody|satir\w*|fictional|"
                          r"a?\s?prank)\b", re.I)


def dropped_meaning(claims: list[dict], spoken: str) -> list[str]:
    """Claims whose meaning word ("on-screen", "alleged"...) is missing from the sentence that
    tells them. Same sentence matching as bare_claims."""
    sentences = [x for x in split_sentences(spoken) if not x.strip().endswith("?")]
    out = []
    for c in claims or []:
        m = MEANING_WORD.search(c.get("text", ""))
        if not m:
            continue
        want = set(CONTENT_WORD.findall(fold(c.get("text", ""))))
        best, best_n = None, 0
        for x in sentences:
            n = len(want & set(CONTENT_WORD.findall(fold(x))))
            if n > best_n:
                best, best_n = x, n
        if best and best_n >= max(2, len(want) // 3) and not MEANING_WORD.search(best):
            out.append(f"{c.get('text', '')[:80]} (\"{m.group(0)}\")")
    return out


# D13 (run 43262308476): the Barkley-Jordan Short ended "they stopped talking ... still no update
# on a reunion", but its source said Vince Coleman got them talking and Barkley planned golf with
# Jordan. Where a feud stands NOW is part of the story: a Short that says "silence" while a source
# tells of contact since leaves out the latest turn.
SILENT = re.compile(r"\b(no update|still (?:no|not|silent|hasn't|haven't|feuding)|never (?:spoke|spoken|talked|"
                    r"made up)(?: again)?|stopped (?:talking|speaking)|(?:haven't|hasn't|have not|has not) "
                    r"(?:spoken|talked)|the silence|no reunion|went silent|cut (?:him|each other) off)\b", re.I)
TURN = re.compile(r"\b(reunit\w*|reconcil\w*|made up|patched (?:it|things) up|buried the hatchet|"
                  r"apologi[sz]\w*|time to talk|talking again|spoke again|spoken again|reached out|"
                  r"squashed|hugged|back on good terms)\b", re.I)
NAME = re.compile(r"\b[A-Z][a-z]{2,}\b")


def missed_turn(spoken: str, sources: list[dict]) -> str:
    """A source sentence telling of contact since the falling-out (with a name the Short says
    within two sentences of it), when the Short speaks of silence and never of that turn. ""=fine."""
    if not SILENT.search(spoken) or TURN.search(spoken):
        return ""
    said = {w.lower() for w in NAME.findall(spoken)}
    for s in sources:
        sentences = split_sentences(f"{s.get('summary', '')} {s.get('text', '')}")
        for k, x in enumerate(sentences):
            if TURN.search(x):
                near = " ".join(sentences[max(0, k - 2):k + 3])
                if said & {w.lower() for w in NAME.findall(near)}:
                    return x.strip()[:160]
    return ""


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
        if c.get("official_result"):
            # every number in it matched the league's own results (nbadata.py): official word
            out.append({**c, "status": "CONFIRMED"})
            notes.append(f"confirmed by {c['official_result'][:90]}")
            continue
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
    if any(c["status"] in ("REPORTED",) + HEDGED for c in out) and not HEDGE.search(spoken):
        verdict = worst(verdict, REJECT)
        notes.append("a report or rumor is told as fact: no attribution in the narration")
    for text in dropped_meaning(out, spoken):
        verdict = worst(verdict, REVIEW)
        notes.append(f"a word that changes what happened was dropped: {text}")
    for text in bare_claims(out, spoken):
        verdict = worst(verdict, REVIEW)
        notes.append(f"a rumor / anonymous report / opinion sounds like a fact: {text[:80]}")
    turn = missed_turn(spoken, sources)
    if turn:
        verdict = worst(verdict, REVIEW)
        notes.append(f"the Short speaks of silence, but a source tells of contact since: \"{turn[:100]}\"")
    return verdict, notes, out


# ---------- 3. fabrication: invented sources, conversations, quotes ----------

ANON = re.compile(r"\b(a (league |team )?source|sources (say|said|tell|told|close)|people close to|"
                  r"insiders? (say|said|tell)|one teammate|a teammate (said|told)|told teammates|"
                  r"in the locker room,? he (said|told|yelled|screamed)|behind closed doors,? he)\b", re.I)


# Fan reaction ("fans are furious", "the internet lost it", "it went viral"). Balanced on
# purpose: the sources do not have to use the same words. Any described public reaction in
# the sources (fans, social media, backlash, viral...) or a story that is measurably hot today
# (Reddit, Google Trends, YouTube heat, search) carries it. Only a reaction with no sign of one
# anywhere is held for review.
SOCIAL_PROOF = re.compile(r"\b(fans?|the internet|twitter|social media|everyone|the nba world|swifties|"
                          r"nba twitter)\b[^.!?]{0,30}\b(furious|angry|livid|mad|outraged|split|divided|"
                          r"lost it|losing it|going crazy|melting down|erupt\w*|explod\w*|roasting|"
                          r"reacting|talking about|can'?t stop|in shock|stunned|calling for|demanding)\b|"
                          r"\b(went viral|broke the internet|blew up online)\b", re.I)
REACTION_EVIDENCE = re.compile(r"\b(fans?|supporters|social media|twitter|x\.com|instagram|tiktok|"
                               r"reddit|viral|backlash|outrage|reacted|reaction|criticism|criticized|"
                               r"slammed|mocked|trolled|swifties|online|comments?|buzz|trending|"
                               r"uproar|blasted|ripped)\b", re.I)


def check_social_proof(spoken: str, sources: list[dict], audience_hot: bool = False) -> tuple[str, list[str]]:
    m = SOCIAL_PROOF.search(spoken)
    if not m or audience_hot or REACTION_EVIDENCE.search(material(sources)):
        return PASS, []
    return REVIEW, [f"fan reaction with no sign of one in the sources or today's data: \"{m.group(0)}\""]


# Small details a writer fills in from habit, not from the articles: where it happened, how the
# crowd reacted, what someone's job is. Each must be in the source material (2026-11-11: a hook
# said "in front of his own crowd" with no source for the venue). Pairs: (what was said, what
# the material must contain).
DETAILS = [
    ("crowd", r"\bcrowds?\b", r"\bcrowd"),
    ("booed", r"\bboo(?:s|ed|ing)?\b", r"\bboo(?:s|ed|ing)?\b"),
    ("cheered", r"\bcheer(?:s|ed|ing)?\b", r"\bcheer"),
    ("chanted", r"\bchant(?:s|ed|ing)?\b", r"\bchant"),
    ("sold out", r"\bsold[- ]out\b", r"\bsold[- ]out\b"),
    ("at home", r"\b(?:home court|at home|home crowd|home game|home fans|his own building)\b", r"\bhome\b|\bown building\b"),
    ("on the road", r"\b(?:on the road|road game|road trip)\b", r"\broad\b"),
    ("radio", r"\bradio\b", r"\bradio\b"),
    ("podcast", r"\bpodcast(?:s|er|ers)?\b", r"\bpodcast"),
    ("columnist", r"\bcolumnists?\b", r"\bcolumn"),
    ("analyst", r"\banalysts?\b", r"\banalyst"),
    ("journalist", r"\bjournalists?\b", r"\bjournalis"),
    ("reporter", r"\breporters?\b", r"\breport"),
    ("broadcaster", r"\b(?:broadcasters?|commentators?|anchors?)\b", r"\b(?:broadcast|commentat|anchor|announcer|tv)"),
    ("agent", r"\bagents?\b", r"\bagent"),
]


def unsupported_details(text: str, sources: list[dict]) -> list[str]:
    """Details said in the Short (venue, crowd, someone's job) that no source mentions."""
    t, mat = fold(text), fold(material(sources))
    return [label for label, said, need in DETAILS
            if re.search(said, t) and not re.search(need, mat)]


def check_fabrication(spoken: str, sources: list[dict], bad_quotes: list[str],
                      unsupported_numbers: list[str], audience_hot: bool = False) -> tuple[str, list[str]]:
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
    details = unsupported_details(spoken, sources)
    if details:
        verdict = worst(verdict, REVIEW)
        notes.append(f"details not in the sources: {', '.join(details)}")
    v, n = check_social_proof(spoken, sources, audience_hot)
    return worst(verdict, v), notes + n


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
    stages = {str(b.get("stage", "")).lower() for b in beats}
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
    elif "analysis" not in roles and "payoff" not in stages:
        # YouTube's reused-content rule: monetized videos need SIGNIFICANT ORIGINAL COMMENTARY.
        # Background alone is not commentary: our own reading of what it means is.
        verdict = REVIEW
        notes.append("no analysis or payoff beat: there is no original commentary, only background")
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


def jersey_ok(jersey: str, career: set[str] | list[str], his_own: bool = False) -> bool:
    """A photo's jersey fits the man named: no jersey read, no known career, or a team he played
    for. The Hornets name moved: a "Hornets" jersey from 1988-2013 New Orleans counts for the
    Pelicans franchise too (Chris Paul). D23 (run 43446225184): a photo that is HIS (his own
    Commons category, or his exact name in its title) always fits: Wikidata's career can miss a
    whole spell (Kyrie Irving: no Nets 2019-2023, and 12 real Nets photos were left out)."""
    if not jersey or not career or his_own:
        return True
    return jersey in career or (jersey == "charlotte hornets" and "new orleans pelicans" in career)


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
                             short.get("unsupported_numbers", []), bool(short.get("audience_hot")))
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

"""Regression tests for the 2026-11-11 fixes (PROJECT.md section 6). They protect what works:
each test is a real case from a real run that once went wrong. Offline and fast: no voice
engine, no ffmpeg, no network (every outside call is replaced by a fake answer), so they run in
the "Safety tests" step before anything is installed or made.

  1. voice: quote marks never lower the "words heard" count; the best take is kept
  2. footage: a clip that is not of the story's person must prove it is the NBA
  3. namesakes: a different birth year on the file = another person
  4. the player's own Commons category: Wikidata's name, the "by year" level, no false drop
  5. empty beats: no unjudged stock clip; the gate holds any unjudged clip
  6. script: hook replayed in a beat, repeated beat, weak payoff -> one safe repair pass
  7. quotes in single quotes are checked against the sources too
  8. yt-edit: only real silence over 0.7 s is shortened, natural pauses never
  9. end card: after the voice's last real sound, never over it
 10. the public run page is short; the full report and working data are kept privately
 11. the weekly plan and competitor scan come from the private repository (not this public one)
 12. one photo in two crops is ONE picture: never shown twice in a Short
 13. today's uniform: the player's current team (Wikidata) decides which of his photos come first
 14. Wikimedia: the account token goes only to Wikimedia's APIs, a refused token is dropped, a 429
     is waited out (within a budget), and every other site is fetched exactly as before
 15. one game per Short at most 3 times while other fitting photos of the person exist (run
     43011651547 showed 9 of 13 photos from "Celtics at Wizards", 15 Dec 2024)
 16. the story's own article is read first; when it cannot be read, the script is told not to
     promise what it says (run 43027675858: "Brown explains why..." never said why)
 17. must-know context: who each person is in the story, who went where in a trade, who won the
     game, roles exactly as the sources give them (run 43027675858)
 18. her analysis is her own: a payoff that only agrees with an outlet ("...and I think that's
     right") goes to the repair pass (run 43027675858)
 19. the hook pick sees the whole Short and the names fans know: no question the Short never
     answers, no line built on a name nobody knows (run 43027675858)
 20. details (venue, crowd, someone's job) only as the sources give them: a hook with one goes
     back, the repair pass fixes the beats, the gate holds what is left (run 43011651547)
 21. length: 45-65 words after the hook, up to 72 only when must-know context or her own reason
     needs it (owner's choice "გ"); the longest Short still counts as ready
 23. photos: a photo taken before his NBA career ("PRE-NBA", run 43066151290: Brown at a 2015
     high school game) goes last and Claude is told; off-court events score low; a Commons
     derivative ("File:X.jpg ... derivative work") is the same picture as X
 25. TWO VERSIONS (C1): the editor names where two accounts clash, the writer puts both sides
     in (attributed), the critic checks it; never invented
 26. RUMOR LABELS (C2): an anonymous report, a rumor or a speculation is voiced as such in its
     own sentence; a fact stated plainly is never forced to sound like a rumor
 27. PODCASTS (C3): two Google News searches for what was said on NBA podcasts and shows
 28. HISTORIC BEEFS (B20/C4): a weak day's empty slot gets a famous beef that is back in the
     news (2+ articles in 30 days), never one used in the last 90 days, told as OLD
 29. stale Wikidata (run 43080115985): an undated "current" team is not trusted; college / high
     school photos are PRE-NBA from their own text; a former role is said as former
 30. Openverse kept: a good search is kept 14 days per person; a failed one uses it
 31. sentences never split at an initial ("Stephen A. smart?" is one question; run 43088629255
     held a good Short for "repeating" because of it)
 32. one feud, one Short in 48 hours (run 43088629255: three Shorts on Brown and Tatum in a day),
     unless a major turn or a new voice leads the story
 33. run 43199348111: a meaning word ("on-screen") is never dropped; the same Commons file from
     two sources is one picture; Openverse needs the full name as one phrase; the description
     links the article itself, not a Google News redirect
 34. the hook is a STATED shock (owner, 2026-11-12): statements rank first, a question loses
     points; name + shock in the first 8 words; a rumor hook opens with its source
 35. a historic beef follows the 48-hour feud rule too (also against this run's Shorts)
 36. every photo of the story's people is tagged once (kept), each beat gets a shortlist that fits
     its line; never more than 3 photos of one scene; burst shots are one picture; political
     photos only when the line is about them
 37. every outlet's report of the same story is read (up to MAX_ARTICLES); "45.0" counts as 45
 38. the chosen hook with a detail the sources word differently is rewritten in their words, not dropped
 39. where a feud stands now: "silence" while a source tells of contact since -> repair, else REVIEW
 40. a broken tag answer keeps its good entries; an untagged photo never fills when the person has tags
 41. a beat that replays the hook in other order, and "that stretch" never said -> repair
 42. a fresh, spreading fight just under the line (55+) is made before an old feud fills the run
 43. bold but true: the chosen hook is read against the sources; an overstated one gets its boldest true line
 44. one event (All-Star 2022...) counts like one scene; college photos marked PRE-NBA; small figures
     and other eras/teams kept for when the line asks for them
 45. the full reports never reach the public logs or run summaries (audit, 2026-11-13)
 46. captions and voice split sentences like the script checks (initials); Pillow 14 ready
 47. another man with his surname and a look-alike first name (Isaiah for Isiah Thomas) is never
     his photo (run 43353547001)
 48. a corrected quote is only the quote: never the words glued before it ("hurt Luka Doncic:"),
     never "said Barkley", never a cut-off source (run 43395656602)
 49. final laws on the finished Short, whatever made the mistake: a quote must be inside quote
     marks in a source; no glued "Doncic:Not" text; no photo in the jersey of a team its man
     never played for (media leaves it out, the gate holds it if it is still there)
 50. each Short's source texts are kept with the run, and replay.py runs today's checks on every
     kept run (a change is tried on real Shorts before it reaches main)
 51. (changed 2026-11-14 by his rule) the hook must be scandalous, intriguing and effective; the
     day's news is secondary: no line wins only because it says the news (run 43353547001 case kept)
 52. a question is never the payoff's answer: "Why was Luka even back in up 20? I'd blame that."
     goes to the repair pass (run 43395656602)
 53. an independent final read (final_read.py): a clear error with real evidence, or a Short it
     could not read, is held by the gate; an error without real evidence is only a doubt
 54. D16: contact sheets are opened all at once (one step), not one per step: each step re-reads
     everything before it (run 43395656602: a 5-sheet tag call cost 136k tokens); turns logged
 55. no name is used in a function before that function imports it (run 43407418420: render.py
     crashed after making both videos, so the gate never ran)
 56. a photo in the player's OWN Commons category is his, however the title spells his first name
     (run 43407418420: 27 "Dejonte Murray" photos of Dejounte Murray were left out by rule 47)
 57. the final reader's WRONG PICTURE follows the picture rules already agreed: a former team's
     jersey with no team or time in the line, or a teammate on a line about the team, is at
     most a doubt (run 43407418420); each media Claude call is named in the budget (D16)
 58. a fresh story whose own article cannot be read in any copy is skipped before writing and
     the next story is tried; evergreens keep their own rule (run 43407418420)
 59. every Google News search puts "when:1d" first (the podcast search ignored it and gave only
     May items); a silent feed says why in the log and falls back to its outlet through Google
     News (ESPN gave 0 items in every run, HoopsHype's feed answers 402)
 60. the owner's source review: ClutchPoints, Hoops Rumors, SB Nation, Defector, TrueHoop, five
     new searches, seven podcast channels (titles only), r/nba rising as a signal; multi-sport
     feeds keep only NBA items
 61. D22: a photo taken before the DAY his NBA career began (Wikidata, dated to the day) is PRE-NBA
     on every path, Openverse included (the day in the file name counts); the Commons copy of a
     file wins over its Openverse copy; the final read calls a PRE-NBA picture on an NBA line an
     error (run 43446225184: Lendeborg in Michigan #23 on "a 24-year-old rookie")
 62. D23: the jersey law trusts a photo that is HIS (own Commons category, or his first and last
     name in the title): Wikidata had no Nets spell for Kyrie Irving and 12 real photos were lost
 63. D24: the titles are read against the sources too (bold but true): "Curry's two weeks is a
     LIE?" steps behind a true title; every title overstated = the Short is held
 64. D25: the pick prompt names every contact sheet ("beat_0.jpg, beat_0_2.jpg, ..."): Claude
     cannot list the folder and opened them one guess per step (15-19 steps, up to 169k tokens)
 65. D26 (owner): a conflict between popular players/teams weighs slightly more than other drama
     around a popular player: +6 for any conflict, plus up to +4 by star power (0 at 5, 4 at 10)
 67b. (2026-11-14, his answers) hook 8-12 words (3-4 s at 2.8 words a second); MAJOR_TURN without
     plain "trade"; articles read up to 6000 characters; tier 1 + 5 newspapers/broadcasters
 66. who said it, and is it still true: an outlet's conclusion is never given to the insider it
     reports on; an ended fact (a streak) is never said as still running (writer, critic, final read)
 67. D27: a rewritten hook (truth or detail fix) keeps every hook rule: no profanity, the story's
     lead person in the first 8 words; a profane hook never leads (run 43485568700)
 68. D29 (owner): a named beat reporter credited for an on-record quote ("Mitchell told Chris
     Fedor of Cleveland.com") is a reliable source: no "provenance unclear" hold, no RUMOR downgrade
 69. D28: unjudged top-up photos keep the team order (today's team / no team first, a former
     team after, never dropped): Mitchell's Jazz photos had filled Cavs lines
 70. D30 (owner): top-ups by relevance - photos and clips Claude scored 8+ for the beat first,
     best first; an unscored one only after them, only if he is seen (face or from behind) AND
     the jersey fits the line (a named team allows that team; a time only: today's team)
 72. D32: a beat left without a new picture says why in the log (each reason counted), and a
     Short with no recognised person says so (run 43513168042: Embiid's last two beats, silent)
 73. D33: replay.py applies rule 56 like the pipeline: an own-category photo is never "another man
     with his surname" (run 43513168042: "Dejonte Murray" in Dejounte Murray's own category)
 74. D35 (his answer): only a Wikipedia-confirmed name makes another a fragment: the fake "Question
     Joel" no longer drops the real Joel Embiid (run 43513168042: the Short had nobody; 11 of 35)
 76. D37 (his answers): the pictures' people list also finds names with an inner capital (LeBron),
     two initials (JJ, J.J.) and O'/D' (O'Neal): JJ Redick's own lines had Luka's photos; the
     collector's name finder is unchanged
 77. D39 (his answer): a top-up may be a photo in his own Commons category whatever the title's
     spelling ("Dejonte Murray"); a group title stays out; face and jersey checks still apply
 78. D38 + D41 + D42 (his answers): Claude-scored photos follow the top-ups' team rule (Green in a
     Rockets jersey on a Suns line); a team word counts only with a capital and never as a word of
     a story person's name ("Tragic Magic"); a year before his current spell is his past (Kyrie's
     Cavs on "the 2016 title"), so it is no time named
 79. D43 (his answer): the photo's own person's name words are no team either ("Tragic Magic" on a
     Magic Johnson photo); the tagger's "who" now reaches the photo, so photo_owner can read it
 80. D40 (his answer): a tie in people() goes to the one named first in the headline
 81. D36 (his answer): a Wikipedia description naming a magazine, newspaper, website, network,
     company, team or league is never a person ("Sports Illustrated")
 82. D45 (his answer): a national-team photo (tag names a country or national team/Team USA/
     Olympic/FIBA) fits only a line about a national team, the Olympics, a World Cup or FIBA
 83. D44 (his answer): the gate counts an own-category photo as his, like D39's top-ups (a group
     title still needs his name)
 84. D46 + D47 (his answers): "Stephen A. Smith" (first + one initial + last) is found, and a
     Wikipedia "personality", "commentator", "host" or "podcaster" is a person
 85. D48 (his answer): the story's people are read from the hook too
 86. D49 + D50 + D51 (his answers): a line naming a man with an NBA career shows only the men it
     names (first or last name); a rookie with no usable NBA photo may show his college photo on
     his own line naming no team or time, marked for the final read
 87. D52 (his answer): one Wikipedia page is one person ("Stephen Curry" = "Steph Curry")
 88. D53 (his answer): a story whose headline was already made in the last 7 days is always a
     repeat, whatever the editor says
 89. D54 (his answer): an address that failed to download is not tried again in the same run
 90. D56 (his answer): an infobox listing his NBA spells with none "present" means he plays for no
     team now, whatever an open Wikidata spell says (Redick); an empty infobox field never swallows
     the next one (Draymond's "years1 = ...-present" was lost)
 91. D57 (his answer): a historic beef is exempt from the "own article read" rule (its mark is on
     the topic): run 44047143877 skipped both beefs and made no Short
 92. D60 (his answer): a year in his past allows only a jersey of a team he played for that year
     (infobox spells, both halves of a season): Howard's Hawks photo on "He won the 2020 title"
 93. D59 (his answers): a team named by its city counts, in a line and on a jersey ("Philly",
     "Cleveland jersey"); Los Angeles never; New York = Knicks; "New York Times" is a newspaper
 94. D61 (his answers): a team he never played for nor coached does not judge his jersey (Garnett
     on "...after Denver took Carmelo"); a team he coached does (Rivers on the Bucks line); a line
     naming any NBA team still refuses a PRE-NBA photo
 95. D62 (his answers): a photo whose title or tag names his college (infobox) is PRE-NBA; a college
     name that is also an NBA city counts only when the text does not name that NBA team
 96. D63 (his answer): a line naming nobody shows whom the writer put on screen (on_screen), not
     anyone in the story; when on_screen names nobody either, as before
 97. D2-b (his answers): 12+ words in a row of a source quote, said without quote marks on a line
     naming the man that quote's paragraph names, are put in quote marks (only the copied words)
 99. (his yes 2026-11-17): an article about two people of a historic beef is found by the past
     forms too ("Isiah Thomas claimed..."); the bank holds every pair once; D64: "why" alone does
     not make an article about them
 100. D65 (his answers): the final read's evidence may join the line's and the source's words; every
     piece in quote marks with 2+ words must be real, each where it is; the evidence of an error
     kept only as a doubt is saved
 101. (his answers): a payoff that is only "I think ..." in under 8 words with no because / so / since
     gets one reason from the repair; "Doc was half right and fully clumsy." stays an answer
 102. D66 (his answers): a quote with a word left out INSIDE gets the source's exact words (from its
     first word to its last); quoting part of a sentence stays; never across "..., he said, ..."
 103. D67 (his answers: "D49's copy"): a man whose every usable photo is a national-team one may be
     shown in one on his own line naming no team or time (Brooks); never on a team or time line;
     an NBA photo comes first; the final read sees "NATIONAL, NO NBA PHOTO EXISTS"
 104. stage 4e (his answers): the final read's errors are fixed and the Short redone while each try
     leaves fewer errors; only the error lines change, by the repair pass's checks (a hook by the
     hook rules); a wrong picture never again in that Short; no new voice = the old words stay
 105. D69 (his answers): the quality eval: the kept stories made again as full Shorts, repetition
     check off, no permanent record touched but the photo tags, in parts, one number
 106. D68 (his answers): the RECEIPTS format (quote against quote, same six beats) only when the
     editor proposes it and the articles hold BOTH sides' own words; else the breakdown as before
 98. D2-a/c/d (his answers): the hook truth check and the final read catch facts joined or
     shortened into another meaning; the hook check catches a superlative or always/never/
     everyone word the source does not say; an opinion says an open future as likely, not settled
 75. D34 (his answers): his Wikipedia infobox is always read with Wikidata: its NBA teams join his
     career (Murray, Fears had only a college team: no jersey law; Kyrie: no Nets); the current
     team is the playing spell ending "present" and wins over Wikidata; its year: "2022 end" = 2023;
     career_start is the debut year only when Wikidata has none; a coach's "team =" is ignored
 24. Openverse: a 504 (a search new to it) is retried 6 times over ~2 minutes (runs 43027675858,
     43066151290: three quick tries, every search lost)
 22. five articles, read with no time limit (only a site silent for 5 min is left, after a second
     try), Claude's answer up to 20 min (owner, 2026-11-11); questions: no
     middle beat re-asks the hook's question, the closing question loops to the hook and brings
     in no one the Short never introduced (run 43066151290)
 (12 also: a crop named after the person, "...-036 (White).jpg", is the same picture, run 43027675858)
 107. D71 (his answers 2026-11-18): when the writer's on_screen names a man with an NBA career, the
     picture pick shows no OTHER known man on that line (Arenas run: Draymond on "Steph Curry tore
     his oblique"; kept runs: Garnett on "Carmelo Anthony speaking"); a generic picture may, and an
     on_screen naming only a reporter or an executive keeps D50 (Curry on Shams Charania's line).
 142. D99 (his "კი" to all five recommendations 2026-11-26, class R1 "tests are offline"): the tests
     never reach the network (a full run tried commons.wikimedia.org twice, from test 104
     test_refused_never_offered via media.prewarm_searches -> commons_videos, which swallows the
     error; with network access, as on GitHub, it really searched). tests/no_network.py, imported
     right after no_real_claude by every test file: every name lookup and every connection or send
     in the test process, to any address (127.0.0.1 included), raises at once; a test during which
     one happened fails under its own name even when the code swallows the error; the processes the
     tests start get every proxy variable pointed at a closed local port. Test 104 now stubs the
     Commons search as "nothing found". src/ unchanged.
 141. D98 (his "კი" and answers 2026-11-26, class R1 "tests are offline"): the tests never call the
     real Claude, whether or not the CLI is installed (this cloud environment has it on PATH: the
     suite made 5 real calls and test_gate_and_repair failed). tests/no_real_claude.py, imported
     first by every test file: any start of a program named "claude" in the test process raises at
     once; a fake "claude" first on PATH refuses child processes' calls; a test during which a call
     happened fails under its own name even when the code swallows the error. The 5 tests that
     reached Claude (RumorLabels.test_gate_and_repair, 4 HistoricBeefs) now stub it as "Claude
     did not answer", the case they always checked. src/ unchanged.
 140. D91 Q1 (his answer 2026-11-25: then the gate's copies): gate.py kept COPIES of the media
     stage's rules (BROADCAST, BROADCAST_AMBIG, GROUP_TITLE, SUFFIXES, the full-name test, the
     group test), matched by hand at D44, D73 and D96; now it uses media's own definitions
     (media.full_name_in_title is the one full-name test, also inside solo_title). Same results:
     598 real picture titles x 61 story people, old vs new, differ in 0 for both stages; the
     gate's verdicts on 50 kept Shorts differ in 0. (media now also reads "_" as a space, as the
     gate did; no real title has one.)
 139. D91 F1/Q1 (his answers 2026-11-25): the hook's (D17) and the titles' (D24) truth checks
     follow ONE failure rule, the stricter one: a title truth call that still fails after
     ask_claude's second try counts every title read as overstated (as D83 for the hook), so the
     Short is held ("every title says more than the sources"); before, a failed call changed
     nothing.
 138. D91 P1 (his answer 2026-11-25: one rule for the pick and the top-ups): D50 ("a line naming
     a man with an NBA career shows only the men it names") held only for the top-ups; Claude's
     pick obeyed it only when the on_screen note named a man (D71). media.line_lock now returns
     "line" with those men when the note locks nobody, and lock_allows treats it like "speaker":
     the named men or a generic / team picture, never another story man. The top-ups are
     unchanged (their chain already did this). Kept runs: 40 of 107 picked photos on such lines
     showed another story man (Doc Rivers on Draymond's line, Paul George on Tatum's); P1-46/47.
 137. D91 P2 (stage 5 of the class-fix plan; his answer 2026-11-25: P2 first): team_fits' ten
     layered rules (D30, D38, D41, D43, D45, D49/D67, D59, D60, D61, D62) are ONE rule: the
     photo's era (media.photo_era_of) against the line's scope (media.line_scope) in
     media.era_allowed. Same results: a differential replay of the old and the new function on
     1,119,200 real (line, photo) pairs (kept scripts' lines x tagged photos of the 27 snapshot
     people, every team mark, national-only, judged and unjudged now/today) differs in 0; the P2
     library, the suite and the replay unchanged; every layer's mutant is caught.
 136. D96 module 6 part 4 (his answers 2026-11-25, classes P2, E1): the last lists. Pre-NBA: a
     tagged photo is pre-NBA by the tagger's scene OR its note naming his college
     (media.college_photo reads the note; team_marks keeps the mark without the title's words and
     photo_tags._apply undoes a title-only "pre-nba" when the tagger saw no school scene: "Charles
     Barkley at East Carolina University" is an interview); the title decides only for an
     untagged photo (D62 kept: Kawhi's notes say "San Diego State"). Evergreen ABOUT_THEM split
     (feud, beef, rivalry, rift, fallout, tension, clash, reunion, fires back, calls out,
     apologized, regret clear; says, recalls, reveals, history, story, truth... ambiguous), ONE
     small call for the pairs found (evergreen.judge_about, through the script stage's
     ask_claude). Benchmark OFF_NICHE / DRAMA split, ONE call per run (benchmark.judge_titles;
     benchmark.yml and weekly.yml install Claude before it). No answer: as before. PERSON_DESC
     stays a list (every sense is a person). D91 is a separate task after D96 (his answer).
 135. D96 module 6 part 3 (his answers 2026-11-25, class S1): the script's style words by meaning,
     ONE small "style" call per Short before the hooks are scored (script.judge_style; the
     rewritten hooks of the retry loop in a further small call): CLASH_WORDS keeps vs, versus,
     calls out, fires back, beef, feud, rift, clash, ejected, fined, suspended, benched, shove,
     heckler, disagree (CLASH_AMBIG the rest, "slams it home"); FOG_WORDS are all ambiguous ("talking
     crazy" quoted, "the only thing standing between"); REASON_WORD keeps because / since,
     REASON_AMBIG "so" ("So in 1985..."). No answer: as before (a style score). REFERENT,
     AGREE_ONLY, SPOKEN_PER stay lists. Found while building it (class Q1): a judgement call
     whose answer has no "yes" list (collect, signals, media picture words, style) counted as
     "all no" instead of a failed call; now it is a failed call (each module's agreed side), and
     the D95 call's missing PART C answer counts the lines as a time, as on failure.
 134. D96 case library (his "კი" 2026-11-25; FIX THE CLASS step 4, missed in modules 2-6 and filled
     now): the real cases of modules 2-6 with both answers in tests/cases/e1_choice.json,
     f1_facts.json and d96_p_words.json, run by test_case_library.D96MeaningLibrary. For them the
     decisions became small named predicates, the behaviour unchanged (replay identical):
     editor.major_turn, compliance.silence_told / turn_told / title_hedged / response_in_articles /
     response_in_short.
 133. D96 module 6 part 2 (his answers 2026-11-25, classes F1, Q1): the script's and title's
     ambiguous words by meaning, in the D95 call (no new call). SILENT keeps still silent / still
     feuding / haven't spoken / no reunion / went silent / cut off; TURN keeps reunited,
     reconciled, patched up, buried the hatchet, talking/spoke again, back on good terms;
     TITLE_HEDGE keeps "?", rumors, reportedly, eyeing, in talks, trade talks. The ambiguous ones
     ("he never stopped talking", "narrative squashed", "Curry could play 20 seasons"): in the
     Short by PART D (silence / turn / response, short["short_judged"]), in a title by PART A (the
     titles join the sentences; the title order is redone with them), in the articles by the fact
     sheet's "reconciled" sign. His answer: the safe side is always the STRICTER check (silence
     counts, a turn or response told in the Short does not, a turn or response in the articles
     does) - this also corrects part 1's response side. INSULT and MEANING_WORD stay lists.
 132. D96 module 6 part 1 (his answers 2026-11-25, classes F1, Q1): the articles' ambiguous words by
     meaning. OFFICIAL keeps nba.com, nba communications, press release, confirmed by the
     team/league; REACTION_EVIDENCE keeps backlash, outrage, uproar, trolled, mocked; RESPONSE (in
     the articles) keeps denied, declined to comment, no comment, lawyer, attorney, apologized. The
     ambiguous ones (official, announced, statement; fans, twitter, comments, viral, trending...;
     responded, response) count only when the D82 fact sheet, in the same call, answered by
     meaning that the story was officially announced / the articles report a real fan reaction /
     the accused responded (short["source_signs"]); page furniture ("Comments (0)",
     "pic.twitter.com", "What's Trending Now") and "this beef officially began" no longer count. No
     answer (a failed call, an older Short): the safe side, they do not count. ANONYMOUS stays.
 131. D96 module 5 (his answers 2026-11-25, class E1): the audience signals by meaning. NBA_WORDS
     keeps nba, basketball, lakers, celtics, knicks, mavericks, 76ers, sixers, timberwolves; the
     other team names ("islanders vs kings", "las vegas weather"), STORY_WORDS' news / reaction /
     history ("history career will") and NOISE's picks / odds / live / meme decide only through ONE
     Sonnet call per run (signals.judge_signals: NBA / STORY / NOISE questions); no judgement: as
     before. The trend match (D86), the search hits and the summary's basketball trends agree.
 130. D96 module 4 (his answers 2026-11-25, class E1): the story choice by meaning. Collect:
     SPECULATION's picks, odds, betting, mock, preview, prediction, predicted, proposal and
     OTHER_LEAGUE's college, football, liberty, g league decide only through ONE Sonnet call per run
     (collect.judge_titles: LEAGUE / SPECULATION questions; "stripped draft picks", "Betting
     Scandal", "Fans Mock Draymond", "Jimmy Butler G League rehab" are real NBA events); a failed
     call: as before (dropped, speculation). Editor: a headline starting with why / how / what /
     should / could / would is filler only by the editor's own kind; MAJOR_TURN's ambiguous words
     (traded, signs, released, punish, punch, brawl, charged, sue, statement, apology, reconcile,
     hug, benched, banned, investigation, deleted, fired) count only when the editor judged a NEW
     turn ("turn" in the same call); no answer: as before. Clear words decide alone; ROUTINE stays.
 129. D96 module 3 (his answers 2026-11-25, classes P1, P2, Q1): the picture words by meaning.
     Clear words still decide alone; ambiguous ones (the clip words "slam", "court", "arena",
     "warm-up", "college", "junior", "family", the broadcast words "ESPN", "TNT", the provenance
     words "own work", "government") become a FITS / BROADCAST / TRUSTED / CATEGORY question that
     Claude judges in context (the Short's common searches in ONE call); a failed call is the safe
     side (refused, not trusted); the gate's broadcast check agrees (item["meta_judged"]). "now" and
     "today" name a time only on a line the script's D95 call judged (PART C, short["time_lines"];
     a failed call or a Short never judged: as before). The photo tagger decides a photo's
     basketball scene, national colours (its scene OR its note, D45 kept) and a group ("g"; a photo
     tagged before D96: its title words, as before).
 128. D96 module 2 (his answers 2026-11-25, class P1): D94's speech verbs split as in D95: said,
     says, told, wrote, replied, explained decide alone; added, responded, posted, asked count only
     on a line the script stage's single D95 call judged to report a person's own words
     (short["speech_lines"], also redone by fix_after_read); no judgement: the line works as
     before D94 (the note, D71). "Lendeborg posted 25 points" is no speaker line; "Bassey asked,
     'What you gonna do?'" is, once judged.
 127. D95 (his answers 2026-11-25, class F1, D78 + D93): a report said as fact is repaired, not only
     held: (a) check_claims' REJECT "told as fact" (no attribution anywhere) now goes to the repair
     pass, which names the source in that sentence; (b) a claim the writer marked UNVERIFIED that
     the D82 fact sheet holds takes the sheet item's kind and article (Luka: Yahoo's own words);
     (c) a hook telling a hedged claim as plain fact steps behind like an overstated one (Murray);
     (d) attribution words in two groups (his approved split): clear ones decide alone (said, told,
     reported, according to, wrote, replied, explained, questioned...); ambiguous ones (per, report,
     may, could, might, would, if, wants, interested, considering, expected to, expects, suggests,
     responded, asked, posted, added, heard, hears, buzz, whispers) never decide alone: Claude
     judges such a sentence in context (his rule: an ambiguous word by meaning, never a word list;
     "per ESPN" vs "30 points per game"), recorded in
     short["attributed"] so the gate counts the same - the Arenas hook "just questioned" is no longer a false hold; the
     repair and the hook order read the gate's own statuses (gate_statuses), one matcher
     (claim_sentence) for bare_claims and told_as_fact.
 126. D85 (his answers 2026-11-25): the Claude models are pinned to exact ids, claude-sonnet-5-5
     (CLAUDE_MODEL) and claude-haiku-5-5 (CLAUDE_MODEL_LIGHT), in collect, eval and media-preview
     and as the code defaults (script, media, editor, skills); when Anthropic retires a pinned
     model the run stops with a clear message (data/model_gone.txt; the eval stops too) and never
     moves to another model by itself. The four modules' checks are identical.
 125. D94 (his answers 2026-11-25, class P1): a line telling what X said about Y shows ONLY the
     speaker X: X is a story man named right before one of D68's speech verbs (said, says, told,
     wrote, added, responded, replied, posted, explained, asked) who locks a line (a player or a
     coach, D92 too), the hook included; a reporter's or TV host's words keep D50; a speech line
     whose note names a real person outside sport (Wikidata human, no sports/media description;
     unreachable: the name counts) shows no story man (a generic or team picture, else the previous
     stays). Same rule in the writer's on_screen prompt, the pick, the top-ups and the final read.
     Changed: 108 and P1-16 (Wade says it: Wade, no longer Wembanyama), 107's code check.
     Cases: tests/cases/p1_who.json P1-35..41.
 124. D92 (his answers 2026-11-25, class P1): a named man whose NBA career could NOT be looked up
     (Wikipedia's person check unreachable, a confirmed page with no Wikidata item, the Wikidata or
     Wikipedia career request failing) locks the line to the men it names, like a known career
     (D50/D71, pick and top-ups); a reporter whose lookup answered keeps D50; the college/national
     extras (D49, D67) stay for a known career only. Factsheet eval: Curry on rookie Lendeborg's
     line, Arenas on Luka's. The run flags and the eval result record each man's career and whose
     lookup did not answer. Cases: tests/cases/p1_who.json P1-29..34.
 123. D87 (his answers 2026-11-24, class E1): one rule for all four audience signals (YouTube heat,
     search phrases, Reddit, Google Trends): a surname alone stands for a man only when no other
     sports person with that surname is in today's top stories, as Wikipedia confirms them (one
     page = one man); else his full name. Star power runs first so the signals know. Wikipedia
     unreachable: as before. Real data: 2 of 1200 topics changed, both the Cunningham pair
     (run 2026-11-13_43407418420: Cade, NBA, and Sophie, WNBA).
 122. D86 (his answer 2026-11-24, class E1): a Google trend counts for a story only when the search
     itself names one of its real people: by full name, or by surname with basketball in the search
     or its headlines; a headline merely naming him no longer counts. The 6 real trend hits of 31
     runs: 4 right kept (Bronny James x2, Caleb Wilson x2), 2 wrong dropped (tacko fall -> a
     Tatum-Brown story, philip rivers -> a Doc Rivers story). test_compliance 28 changed with it.
 121. D77 (his answers 2026-11-19): smoke.yml makes one fixed stored story (state nba/smoke/, a kept
     Short with a VS card) again after every push that changes the code, WITHOUT Claude: voice,
     voice check, video, gate; one fixed music track (the library's first); a technical failure or
     a picture that cannot be downloaded ("the network") turns it red; it saves and uploads nothing.
 120. D73 (his answers 2026-11-19, class P1): a generational suffix (Jr., Sr., II, III, IV) is part of a
     story person's name; a title counts as his only with the same suffix (solo_title, his_own); his
     surname is the word before the suffix; a name the script writes bare takes the articles'
     suffix when every full mention in the articles' text carries that same suffix, else (none,
     mixed, a bare one, no text) it stays as it is. Cases: tests/cases/p1_who.json P1-21..28.
     The gate's full_name_in gives the same answer on every title case (it re-checks those photos).
 119. D84b (his answers 2026-11-19): eval and collect keep the apt .deb files (ffmpeg, espeak-ng) in
     the official cache under one fixed key, renewed only by hand; apt still installs them itself,
     downloading only what the cache lacks; with no cache it installs exactly as before.
 118. D85 (his yes 2026-11-19): every Claude call records which exact model ran (the CLI's
     modelUsage) in the usage file and prints it once per model, so the aliases can be pinned;
     nothing else in the row or the call changes.
 117. D83 (his answers 2026-11-19): a Claude answer that is not one JSON object is asked for once
     more (every call); a hook whose truth check still fails steps behind as an overstated one
     (test "a failed check changes nothing" became "steps behind": a changed rule).
 116. D82 (his answers 2026-11-19): before the writer one call (the main model) pulls a FACT SHEET,
     word for word, with who and status; items not word for word in their article are dropped; the
     writer, humanize, the hook retry and the repair get it under the articles; the checks do not;
     a failed or empty sheet leaves every prompt exactly as before; the limit still stops.
 115. D77 (his answer 2026-11-19): an eval of chosen stories (input stories, ids): only those run,
     read against the same stories of the newest eval (or the base when quick); never listed as a
     previous eval, never a base; an unknown id stops it.
 114. D79 (his answers 2026-11-19): a person's Commons category about to be skipped (no "sure" name,
     nothing in it says basketball) is his when its own parent categories say basketball, NBA or an
     NBA team ("Dallas Mavericks players"); "court" or "arena" never prove it.
 113. D80 (his answer 2026-11-19): the final read's doubts are each checked once more (the mirror of
     110): a plain "error": true with one of the five kinds makes it an error; in doubt it stays a
     doubt; D65's "(evidence not found)" and 110's "(second check: not an error" are never re-checked;
     the prompt says another story person is an error on a line about one man's act, and that a
     doubt fitting a rule is an error.
 112. D77 (his answers 2026-11-18): a full eval keeps each story's script, sources, voice timing and
     pictures (as before the fix after the read; text only); a QUICK eval (from_stage media or
     final_read) puts them back and redoes only those stages, read against its base; no video, no
     gate.
 111. Stage 4 (his answers 2026-11-18): the eval counts, per failure class, the Shorts with a problem
     of it (his table; WRONG PICTURE = P1/P2; the gate's final_read/editorial/script_checks never
     twice; an unknown problem shows as "?").
 110. Q1 (his answers 2026-11-18): the final read's prompt says a line found right is never an error,
     and every error of every kind is checked once more, alone, by the main model; a plain "not an
     error" moves it to the doubts (marked), in doubt or on a failed call it stays.
 109. D75 (his answer 2026-11-18): the hook truth check reads the next hook until one is true (the
     Howard eval: two overstated, the third led unread and was false).
 108. D72 (his answer 2026-11-18): the top-ups read on_screen first too, when it names a player (one
     line, one man: Wembanyama, not Wade, on "Still, Wade says he has to get stronger"); test 96's
     "the spoken name still wins" now holds only for a note naming no player (a changed rule).
"""

from __future__ import annotations

import copy
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.parse
from contextlib import redirect_stdout
from pathlib import Path

import no_real_claude  # noqa: F401,E402  D98: the tests never call the real Claude (first)
import no_network  # noqa: F401,E402  D99: the tests never reach the network (right after D98)


def claude_did_not_answer(*_args, **_kwargs):
    """D98 (his answer 4): a test that reaches a Claude call gets "Claude did not answer", the case
    these tests always checked (no Claude CLI in the earlier sandboxes or before the CI installs it)."""
    raise RuntimeError("D98 test stub: Claude did not answer")
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import os  # noqa: E402
# the tests must never write the pipeline's real history (it is saved to the private repo)
os.environ.setdefault("NBA_OV_CACHE", str(Path(tempfile.gettempdir()) / "nba_test_openverse_cache.json"))
os.environ.setdefault("NBA_TAG_CACHE", str(Path(tempfile.gettempdir()) / "nba_test_photo_tags.json"))

import numpy as np  # noqa: E402  (in requirements.txt)

# tts.py imports soundfile (installed later, with the voice engine): a stand-in is enough here,
# the tests never write real audio
if "soundfile" not in sys.modules:
    try:
        import soundfile  # noqa: F401
    except ImportError:
        _sf = types.ModuleType("soundfile")
        _sf.write = lambda path, data, rate: Path(path).write_text("wav")
        sys.modules["soundfile"] = _sf

# The Luka Short of run 42877530241: what Whisper heard, and the script
LUKA_HEARD = ("Luca Doncic really tell Hawks fans you all wish you would have had me. Atlanta drafted "
              "Luca third, then traded him for Tree Young. Yahoo! Sports reported Luca told Hawks fans, "
              "you all wish you would have had me. One fired back, we had you. A fan gave in, I wish we "
              "did, I do. Luca dropped 32 in the win. That fan was the honest one. So who's right, him, "
              "or the one who never wanted Luca?")
LUKA_HOOK = "Did Luka Doncic really tell Hawks fans 'You all wish you would have had me'?"
LUKA_BEATS = [
    {"say": "Atlanta drafted Luka third, then traded him for Trae Young.", "on_screen": "Luka",
     "tone": "calm", "role": "context", "stage": "setup"},
    {"say": "Yahoo Sports reported Luka told Hawks fans, 'You all wish you would have had me.' "
            "One fired back, 'We had you.'", "on_screen": "Luka", "tone": "tense", "role": "fact",
     "stage": "conflict"},
    {"say": "A fan gave in: 'I wish we did, I do.'", "on_screen": "Hawks fans", "tone": "amused",
     "role": "reaction", "stage": "twist"},
    {"say": "Luka dropped 32 in the win.", "on_screen": "Luka", "tone": "calm", "role": "analysis",
     "stage": "payoff"},
    {"say": "That fan was the honest one. So who's right: him, or the one who never wanted Luka?",
     "on_screen": "Luka", "tone": "amused", "role": "question", "stage": "exit"},
]


class Voice(unittest.TestCase):
    """1. The voice check (tts.py)."""

    def test_quote_marks_do_not_count_as_words(self):
        import tts
        self.assertEqual(tts.tokens("'You all wish you would have had me.'"),
                         ["you", "all", "wish", "you", "would", "have", "had", "me"])
        self.assertEqual(tts.tokens("who's Giannis' 'I"), ["who's", "giannis", "i"])
        words = [{"word": w, "start": 0.0, "end": 0.0} for w in LUKA_HEARD.split()]
        text = " ".join([LUKA_HOOK] + [b["say"] for b in LUKA_BEATS])
        # was 59% before the fix (the voice was fine: the count was wrong)
        self.assertGreaterEqual(tts.coverage(text, words), 0.85)

    def _voice(self, plan: dict, performer: bool = True):
        """tts.main() with fake engines: plan = {(engine, seed): words heard share, or "boom"}."""
        import tts
        saved = {k: getattr(tts, k) for k in ("SCRIPTS", "AUDIO", "load_pipeline", "Performer", "speak",
                                               "finish", "word_times", "coverage", "duration_of")}
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "short_1.json").write_text(json.dumps(
                {"n": 1, "headline": "h", "ready": True, "hook": {"text": "Did Luka say it?"},
                 "beats": [{"say": "He did.", "tone": "calm"}]}))
            tts.SCRIPTS, tts.AUDIO = tmp / "scripts", tmp / "audio"
            calls = []

            class Fake:
                rate = 24000

                def __init__(self, *a):
                    if not performer:
                        raise RuntimeError("no chatterbox")

                def speak_parts(self, parts, seed):
                    calls.append(("chatterbox", seed))
                    if plan[("chatterbox", seed)] == "boom":
                        raise RuntimeError("boom")
                    return np.zeros(10, dtype=np.float32)
                speak = speak_parts

            def kokoro(*a):
                calls.append(("kokoro", 0))
                if plan[("kokoro", 0)] == "boom":
                    raise RuntimeError("boom")
                return np.zeros(10, dtype=np.float32)

            def heard(text, words):
                eng, seed = words[0]["word"].split(".take_")[1][:-4].rsplit("_", 1)
                return plan[(eng, int(seed))]
            tts.load_pipeline = lambda: (None, None)
            tts.Performer, tts.speak = Fake, kokoro
            tts.finish = lambda wav, mp3, tempo=1.0: Path(mp3).write_text(Path(mp3).name)
            tts.word_times = lambda mp3: [{"word": Path(mp3).read_text(), "start": 0.0, "end": 1.0}]
            tts.coverage, tts.duration_of = heard, (lambda mp3: 10.0)
            tts.main()
            timing = tmp / "audio" / "short_1.timing.json"
            files = sorted(p.name for p in (tmp / "audio").iterdir())
            return (json.loads(timing.read_text()) if timing.exists() else None), files, calls
        finally:
            for k, v in saved.items():
                setattr(tts, k, v)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_best_take_is_kept(self):
        import tts
        s = tts.CONFIG["chatterbox"]["seed"]
        # both Chatterbox takes just under the bar, Kokoro worse: Chatterbox stays (the old code
        # always took Kokoro)
        res, files, _ = self._voice({("chatterbox", s): .83, ("chatterbox", s + 1): .82, ("kokoro", 0): .59})
        self.assertEqual((res["engine"], res["heard"]), ("chatterbox", .83))
        self.assertEqual(files, ["short_1.mp3", "short_1.timing.json"])      # no take left behind
        # a good first take: nothing else is tried
        res, _, calls = self._voice({("chatterbox", s): .95, ("chatterbox", s + 1): .1, ("kokoro", 0): .1})
        self.assertEqual(calls, [("chatterbox", s)])
        # Kokoro really better: Kokoro
        res, _, _ = self._voice({("chatterbox", s): .70, ("chatterbox", s + 1): .75, ("kokoro", 0): .90})
        self.assertEqual(res["engine"], "kokoro")
        # a tie: Chatterbox (the channel's voice)
        res, _, _ = self._voice({("chatterbox", s): .80, ("chatterbox", s + 1): .80, ("kokoro", 0): .80})
        self.assertEqual(res["engine"], "chatterbox")
        # every engine fails: no narration for this Short, nothing left behind
        res, files, _ = self._voice({("chatterbox", s): "boom", ("chatterbox", s + 1): "boom", ("kokoro", 0): "boom"})
        self.assertIsNone(res)
        self.assertEqual(files, [])
        # no Chatterbox at all: Kokoro, as before
        res, _, _ = self._voice({("kokoro", 0): .70}, performer=False)
        self.assertEqual(res["engine"], "kokoro")


def _fake_media_get(wiki: dict, cats: dict, p373: dict, videos: list):
    def get(url, timeout=30):
        if "wikipedia.org" in url:
            return json.dumps(wiki).encode()
        q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
        if "wikidata.org" in url:
            v = p373.get(q.get("entity"))
            return json.dumps({"claims": {"P373": [{"mainsnak": {"datavalue": {"value": v}}}]} if v else {}}).encode()
        if q.get("prop") == "videoinfo":
            return json.dumps({"query": {"pages": {str(i): v for i, v in enumerate(videos)}}}).encode()
        if q.get("list") == "search" or q.get("generator") == "search":
            return json.dumps({"query": {}}).encode()
        files, subs = cats.get(q.get("gcmtitle") or q.get("cmtitle"), ([], []))
        if q.get("list") == "categorymembers":
            return json.dumps({"query": {"categorymembers": [{"title": c} for c in subs]}}).encode()
        return json.dumps({"query": {"pages": {str(i): f for i, f in enumerate(files)}}}).encode()
    return get


def _photo(title: str, desc: str, cats: str = "") -> dict:
    return {"title": title, "imageinfo": [{"mime": "image/jpeg", "width": 1200, "height": 1600, "thumburl": "u",
            "descriptionurl": "https://commons.wikimedia.org/wiki/" + title,
            "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "A"},
                            "ImageDescription": {"value": desc}, "Categories": {"value": cats}}}]}


def _video(title: str, desc: str, cats: str) -> dict:
    return {"title": "File:" + title, "videoinfo": [{"url": "u", "size": 1, "derivatives": [
        {"type": "video/webm", "height": 480, "src": "s"}], "extmetadata": {
        "ImageDescription": {"value": desc}, "Categories": {"value": cats},
        "LicenseShortName": {"value": "CC BY-SA 3.0"}, "Artist": {"value": "own work"},
        "Credit": {"value": "Own work"}, "Duration": {"value": "20"}}}]}


WIKI = {"query": {"redirects": [{"from": "Luka Doncic", "to": "Luka Dončić"},
                                {"from": "Robert Williams", "to": "Robert Williams III"}], "pages": {
    "1": {"title": "Luka Dončić", "pageprops": {"wikibase-shortdesc": "Slovenian basketball player (born 1999)",
                                                "wikibase_item": "Q1"}},
    "2": {"title": "Devin Booker", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1996)",
                                                 "wikibase_item": "Q2"}},
    "3": {"title": "Robert Williams III", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1997)"}},
    "4": {"title": "Bomani Jones", "pageprops": {"wikibase-shortdesc": "American sports journalist"}}}}}
P373 = {"Q1": "Luka Dončić", "Q2": "Devin Booker (basketball, born 1996)"}
CATS = {   # the real shapes found with diagnose.yml on 2026-11-11
    "Category:Luka Dončić": ([], ["Category:Luka Dončić by year"]),
    "Category:Luka Dončić by year": ([], ["Category:Luka Dončić in 2019", "Category:Luka Dončić in 2025",
                                          "Category:Luka Dončić in 2026"]),
    "Category:Luka Dončić in 2026": ([_photo("File:LD 2026.jpg", "Dončić")], []),
    "Category:Luka Dončić in 2025": ([_photo("File:LD 2025.jpg", "Dončić, Lakers")], []),
    "Category:Luka Dončić in 2019": ([_photo("File:LD 2019.jpg", "Dončić")], []),
    "Category:Devin Booker": ([], []),
    "Category:Devin Booker (basketball, born 1996)": ([_photo("File:Booker Suns 2025.jpg", "Booker")], []),
    "Category:Robert Williams": ([_photo("File:RW speech.jpg", "Senator at a hearing")], []),
    "Category:Robert Williams III": ([_photo("File:RWIII.jpg", "Robert Williams III")], []),
}
VIDEOS = [
    _video("13 November 2011 Canberra Capitals game 2204.theora.ogv", "Canberra Capitals game at the AIS Arena.",
           "2011 in basketball|Canberra Capitals|Basketball matches at AIS Arena"),
    _video("Basketball CEO speech - iPhone (Cellular).theora.ogv", "Basketball CEO speech", "Basketball"),
    _video("Boston Celtics warm-up 2019.webm", "Celtics players warming up before a basketball game",
           "Boston Celtics|Basketball videos"),
    _video("WNBA game.webm", "basketball game", "WNBA|Basketball videos"),
    _video("Devin Booker (basketball, born 1991) dunk.webm", "Devin Booker dunk", "Devin Booker (basketball, born 1991)"),
    _video("Devin Booker Suns warm-up.webm", "Devin Booker basketball", "Devin Booker|Phoenix Suns"),
]


def _fake_meta_judge(prompt, model=None, **kw):
    """D96 module 3: Claude's picture-word judgement for the fake Commons files: an own-work
    upload is trusted, nothing here is a broadcast, every ambiguous clip here is a real NBA scene
    (the women's, CEO and namesake clips are refused by the clear rules before any question)."""
    items = re.findall(r"^(\d+)\. (FITS|BROADCAST|TRUSTED|CATEGORY): (.*)$", prompt.split("ITEMS:")[-1], re.M)
    yes = [int(n) for n, kind, text in items
           if kind in ("FITS", "CATEGORY") or (kind == "TRUSTED" and "own work" in text.lower())]
    return {"yes": yes}


class MediaCase(unittest.TestCase):
    """Common set-up: media.py talks to a fake Commons / Wikipedia / Wikidata."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("get", "commons_trusted")}
        self.saved["ask_claude"] = media.ask_claude
        self.caches = [media._person_cache, media._birth_year, media._wiki_title, media._wikidata,
                       media._commons_cat, media._vid_cache, media._photo_cache, media.PHOTO_STATS,
                       media._meta_seen, media._meta_pending]
        self.backup = [dict(c) for c in self.caches]
        for c in self.caches:
            c.clear()
        media.get = _fake_media_get(WIKI, CATS, P373, VIDEOS)
        media.commons_trusted = lambda meta, title, video=False: True
        media.ask_claude = _fake_meta_judge     # D96 module 3: the ambiguous words judged in context
        media.real_people(["Luka Doncic", "Devin Booker", "Robert Williams", "Bomani Jones"])  # as people() does

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        for c, b in zip(self.caches, self.backup):
            c.clear()
            c.update(b)


class Footage(MediaCase):
    """2 and 3: no women's games, no namesakes."""

    def test_generic_clip_must_prove_nba(self):
        kept = [c["title"] for c in self.m.commons_videos("basketball game")]
        # Canberra Capitals (Australian women's team, "women" written nowhere), a CEO speech and a
        # WNBA game are out; real NBA clips stay
        self.assertEqual(kept, ["Boston Celtics warm-up 2019.webm", "Devin Booker Suns warm-up.webm"])

    def test_namesake_clip_and_photo(self):
        self.m._vid_cache.clear()
        self.assertEqual([c["title"] for c in self.m.commons_videos('"Devin Booker"', "Devin Booker")],
                         ["Devin Booker Suns warm-up.webm"])
        n = self.m.namesake
        self.assertTrue(n("Devin Booker", "Devin Booker (basketball, born 1991) Olimpia Milan Euroleague"))
        self.assertFalse(n("Devin Booker", "Devin Booker (born 1996) Suns"))
        self.assertFalse(n("Devin Booker", "Devin Booker 2023 Phoenix Suns"))      # no year: kept
        self.assertFalse(n("Bomani Jones", "Bomani Jones born 1980"))               # year unknown: kept
        self.assertFalse(n("Luka Doncic", "Luka Dončić and Asel Roberts, 2026"))    # a date is not a birth year

    def test_namesake_needs_no_extra_request(self):
        calls = []

        def down(url, timeout=30):
            calls.append(url)
            raise OSError("down")
        self.m.get = down
        self.assertFalse(self.m.namesake("Jaylen Brown", "Jaylen Brown (born 1990)"))
        self.assertEqual(calls, [])


class Category(MediaCase):
    """4. The player's own Commons category (Luka 0 -> 71 photos, Booker 0 -> 38 in real runs)."""

    def files(self, who: str) -> list[str]:
        self.m.PHOTO_STATS.clear()
        return sorted(f["title"] for f in self.m.category_files(who))

    def test_by_year_and_wikidata(self):
        # Luka: no photo in the category itself, only "by year" -> "in 2025" (two levels down)
        self.assertEqual(self.files("Luka Doncic"), ["File:LD 2019.jpg", "File:LD 2025.jpg", "File:LD 2026.jpg"])
        # Booker: "Category:Devin Booker" is empty; Wikidata names the real one
        self.assertEqual(self.files("Devin Booker"), ["File:Booker Suns 2025.jpg"])
        # a politician's category under the plain name is skipped, and the search goes on
        self.assertEqual(self.files("Robert Williams"), ["File:RWIII.jpg"])

    def test_plain_spelling_still_first(self):
        calls = []
        fake = self.m.get

        def spy(url, timeout=30):
            calls.append(url)
            return fake(url, timeout)
        self.m.get = spy
        self.files("Luka Doncic")
        self.assertIn("Luka+Doncic+%28basketball%29", calls[0])

    def test_wikidata_down_changes_nothing_else(self):
        fake = self.m.get

        def no_wikidata(url, timeout=30):
            if "wikidata.org" in url:
                raise OSError("down")
            return fake(url, timeout)
        self.m.get = no_wikidata
        self.assertEqual(len(self.files("Luka Doncic")), 3)    # found by his Wikipedia name


class EmptyBeats(unittest.TestCase):
    """5. Empty beats and unjudged clips."""

    def test_no_unjudged_stock_clip(self):
        import media
        saved = {k: getattr(media, k) for k in ("pixabay_videos", "download", "person_photos", "picture_hash")}
        asked = []
        folder = media.ROOT / "data" / "_test_fill"
        try:
            media.pixabay_videos = lambda q: asked.append(q) or [
                {"kind": "video", "id": 139533, "url": "u", "title": "basketball, game, fitness", "page": "p",
                 "author": "a", "license": "Pixabay Content License", "source": "Pixabay", "duration": 5}]
            media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            media.person_photos = lambda person, shown: []
            media.picture_hash = lambda p: None
            photo = {"kind": "photo", "file": "data/x.jpg", "page": "ph1", "title": "Luka Dončić 2025.jpg", "match": 8}
            got = media.fill_empty([photo, None, None], 3, folder, set(), ["Luka Doncic"], None)
            self.assertEqual([x and x["kind"] for x in got], ["photo", None, None])   # the picture continues
            self.assertEqual(asked, [])                                                # Pixabay never asked
            got = media.fill_empty([None, None, None], 3, folder, set(), ["Luka Doncic"], None)
            self.assertEqual([x and x["kind"] for x in got], ["video", None, None])   # never a blank video
        finally:
            for k, v in saved.items():
                setattr(media, k, v)
            shutil.rmtree(folder, ignore_errors=True)
        import gate
        verdict, notes = gate.check_visuals(got, {"people": ["Luka Doncic"]})
        self.assertEqual(verdict, "REVIEW")
        self.assertTrue(any("clip not judged" in n for n in notes))
        judged = [{"kind": "video", "match": 4, "title": "Boston Celtics warm-up", "license": "CC BY 3.0",
                   "author": "A", "page": "p2"}]
        self.assertEqual(gate.check_visuals(judged, {"people": ["Luka Doncic"]})[0], "PASS")


class Script(unittest.TestCase):
    """6 and 7. The script's repair pass and the quote check."""

    TEXT = ("During the Lakers' 124-114 win over the Hawks, Luka Doncic told Hawks fans courtside "
            "'You all wish you would have had me.' One fan replied 'We had you' and another said "
            "'I wish we did, I do.' Atlanta drafted Doncic third in 2018 and traded his rights to Dallas "
            "for Trae Young and a future first-round pick. Doncic finished with 32 points, 10 assists, "
            "eight rebounds, five steals and two blocks. ") * 3
    GOOD = [
        {"say": "Atlanta drafted Luka third, then traded him for Trae Young.", "on_screen": "Luka", "tone": "calm",
         "role": "context", "stage": "setup"},
        {"say": "Yahoo Sports reported he really said it, and one fan fired back, 'We had you.'", "on_screen": "Luka",
         "tone": "tense", "role": "fact", "stage": "conflict"},
        {"say": "But another fan gave in: 'I wish we did, I do.'", "on_screen": "Hawks fans", "tone": "amused",
         "role": "reaction", "stage": "twist"},
        {"say": "So the trade still stings in Atlanta, and the fans know it better than anyone.", "on_screen": "Luka",
         "tone": "calm", "role": "analysis", "stage": "payoff"},
        {"say": "So who's right about Luka: the fan who gave in, or the one who never wanted him?",
         "on_screen": "Luka", "tone": "amused", "role": "question", "stage": "exit"}]

    def test_quotes_in_both_styles(self):
        import script
        q = script.quotes_in
        self.assertEqual(q("Luka told fans, 'You all wish you would have had me.' One fired back, 'We had you.'"),
                         ["You all wish you would have had me."])
        self.assertEqual(q("He said 'He's not my coach, and I don't care' after the game."),
                         ["He's not my coach, and I don't care"])
        self.assertEqual(q('Tatum called it "another game on the schedule" before tip.'),
                         ["another game on the schedule"])
        self.assertEqual(q("Luka's Lakers beat the Hawks' bench, and Doncic's night was huge."), [])
        self.assertEqual(q("one fan fired back, 'We had you.' But another fan gave in: 'I wish we did, I do.'"),
                         ["I wish we did, I do."])        # a short quote never swallows the next one
        sources = [{"title": "t", "summary": "", "text": self.TEXT}]
        self.assertEqual(script.quote_check("one fan yelled 'Go back to Dallas, Luka, nobody wants you'", sources),
                         ["Go back to Dallas, Luka, nobody wants you"])     # an invented single-quoted quote

    def test_problems_found(self):
        import script
        beats = copy.deepcopy(LUKA_BEATS)
        problems = script.repair_needed(LUKA_HOOK, beats, script.retention_check(beats))
        self.assertEqual(len(problems), 3)      # hook replayed in beat 2, beat 5 repeats, payoff is a stat
        self.assertEqual(script.repair_needed(LUKA_HOOK, copy.deepcopy(self.GOOD),
                                              script.retention_check(copy.deepcopy(self.GOOD))), [])
        take = [{"say": "Doc was half right and fully clumsy.", "stage": "payoff"}]
        self.assertFalse(script.weak_payoff(take))    # a short take of her own is an answer

    def _build(self, repair_beats, limit: bool = False, draft_beats=None, hook: str = LUKA_HOOK):
        import nbadata
        import script
        calls = []
        draft = {"hooks": [{"text": hook, "formula": "The Receipt"}],
                 "strategy": {"kind": "beef", "central_question": "Who was right?", "headline_gap": "The trade."},
                 "angles": ["a"], "angle": "a",
                 "beats": copy.deepcopy(draft_beats if draft_beats is not None else LUKA_BEATS),
                 "titles": ["Luka Doncic TROLLED Hawks fans"], "thumbnail_text": "LUKA vs HAWKS FANS",
                 "receipt": "", "sources_used": [1],
                 "claims": [{"text": "Doncic told fans 'You all wish you would have had me.'", "status": "CONFIRMED",
                             "source": 1}],
                 "queries": ["luka doncic hawks fans"], "description": "Luka trolled Hawks fans.\nWhy.",
                 "tags": ["Luka Doncic"]}

        def fake(prompt, model=""):
            if "THE PROBLEMS TO FIX" in prompt:
                calls.append("repair")
                if limit:
                    raise script.UsageLimit("limit")
                return {"beats": copy.deepcopy(repair_beats)}
            if "sound human" in prompt:
                return {}
            if "scrolling Shorts" in prompt:
                return {"order": [1]}
            return copy.deepcopy(draft)
        saved = (script.ask_claude, script.gather_sources, nbadata.annotate, script.SOURCES_OUT)
        # run 44047143877: this test wrote data/sources/short_1.json, and the CI's safety tests run
        # before the stages, so a run that wrote no Short bundled the test's fake source
        import tempfile
        script.SOURCES_OUT = Path(tempfile.mkdtemp()) / "sources"
        script.ask_claude = fake
        script.gather_sources = lambda topic, editor, tid: [
            {"publisher": "Yahoo Sports", "title": "Luka trolls Hawks fans", "link": "https://sports.yahoo.com/x",
             "url": "https://sports.yahoo.com/x", "text": self.TEXT, "trusted": True, "tier": 1,
             "main": True}]      # the story's own article, read (as gather_sources marks it; rule 58)
        nbadata.annotate = lambda claims: None
        try:
            editor = {"topics": [{"headline": "Luka Doncic trolls Hawks fans", "search_phrases": []}],
                      "ranked": [{"id": 0, "virality": 8}]}
            short = script.build_short(1, 0, editor, "voice", {"hooks": [{"name": "x", "shape": "y", "example": "z"}],
                                                               "rules": ["r"]})
            return short, calls
        finally:
            shutil.rmtree(script.SOURCES_OUT.parent, ignore_errors=True)
            script.ask_claude, script.gather_sources, nbadata.annotate, script.SOURCES_OUT = saved

    def test_repair_pass(self):
        import script
        short, calls = self._build(self.GOOD)
        self.assertEqual(calls, ["repair"])
        self.assertEqual(len(short["repaired"]), 3)
        self.assertEqual(short["retention"]["hard"], [])
        # a repair that invents a number is refused: the original stays and is held
        bad = copy.deepcopy(self.GOOD)
        bad[3]["say"] = "So the trade still stings, and Luka has 45 points in his last game."
        short, _ = self._build(bad)
        self.assertEqual(short["repaired"], [])
        self.assertIn("beat 2 repeats the hook", short["retention"]["hard"])
        self.assertFalse(short["ready"])
        # a repair that invents a quote is refused too
        bad = copy.deepcopy(self.GOOD)
        bad[1]["say"] = "Yahoo Sports reported he said it, and one fan yelled 'Go back to Dallas, Luka.'"
        short, _ = self._build(bad)
        self.assertEqual(short["repaired"], [])
        # the Claude limit stops the run cleanly, as everywhere else
        with self.assertRaises(script.UsageLimit):
            self._build(self.GOOD, limit=True)
        # nothing to repair: the repair pass is never paid for
        _, calls = self._build(self.GOOD, draft_beats=self.GOOD,
                               hook="Did Luka Doncic just rub the 2018 trade in the Hawks fans' faces courtside?")
        self.assertEqual(calls, [])


class Timing(unittest.TestCase):
    """8 and 9. yt-edit and the end card."""

    @staticmethod
    def audio(*parts: tuple[str, float]) -> np.ndarray:
        """("voice", 1.0), ("silence", 0.8) ... at 16 kHz."""
        rate, out = 16000, []
        rng = np.random.default_rng(1)
        for kind, sec in parts:
            n = int(sec * rate)
            out.append(rng.uniform(-0.5, 0.5, n).astype(np.float32) if kind == "voice" else np.zeros(n, np.float32))
        return np.concatenate(out)

    def test_natural_pauses_are_never_cut(self):
        import audio_qc
        # Chatterbox's own pauses run up to ~0.6 s (measured on 7 real recordings): never touched
        for pause in (0.45, 0.62, 0.68):
            a = self.audio(("voice", 1.0), ("silence", pause), ("voice", 1.0))
            self.assertIsNone(audio_qc.silence_cut(a, 16000, 0.9, 1.0 + pause + 0.1, 0.29), pause)

    def test_long_silence_is_shortened_to_a_breath(self):
        import audio_qc
        a = self.audio(("voice", 1.0), ("silence", 1.2), ("voice", 1.0))
        cut = audio_qc.silence_cut(a, 16000, 0.9, 2.3, 0.29)
        self.assertIsNotNone(cut)
        self.assertGreaterEqual(cut["start"], 1.0)          # never into the sound before
        self.assertLessEqual(cut["end"], 2.2)               # never into the sound after
        self.assertAlmostEqual(1.2 - (cut["end"] - cut["start"]), audio_qc.LEFT, delta=0.05)

    def test_breath_in_the_gap_is_not_cut_through(self):
        import audio_qc
        # a long gap that is not silent (a breath in the middle): only the silent part may go
        a = self.audio(("voice", 1.0), ("silence", 0.5), ("voice", 0.3), ("silence", 0.5), ("voice", 1.0))
        self.assertIsNone(audio_qc.silence_cut(a, 16000, 0.9, 2.4, 0.29))

    def test_voice_end_and_end_card(self):
        import audio_qc
        import render
        a = self.audio(("voice", 2.0), ("silence", 0.6))
        saved = audio_qc.pcm
        audio_qc.pcm = lambda mp3, rate=16000: a
        try:
            self.assertAlmostEqual(audio_qc.sound_end(Path("x.mp3")), 2.0, delta=0.03)
        finally:
            audio_qc.pcm = saved
        # 0.4 s after the last real sound, never after the file ends; unmeasured = the file's end
        self.assertAlmostEqual(render.end_card_at({"duration": 29.07, "voice_end": 28.68}), 29.07, delta=0.001)
        self.assertAlmostEqual(render.end_card_at({"duration": 31.0, "voice_end": 28.0}), 28.4, delta=0.001)
        self.assertEqual(render.end_card_at({"duration": 30.0}), 30.0)
        self.assertEqual(render.END_CARD_SECONDS, 2.0)


class PrivateReport(unittest.TestCase):
    """10. Public repository: the run page shows counts only; the full report goes private."""

    def setUp(self):
        import public_summary
        import state
        self.mods = (state, public_summary)
        self.saved = (state.DATA, public_summary.DATA)
        self.tmp = Path(tempfile.mkdtemp())
        data = self.tmp / "data"
        for sub in ("scripts", "media", "gate", "audio", "video"):
            (data / sub).mkdir(parents=True)
        (data / "summary.md").write_text("## Scripts\nDid Luka Doncic really tell Hawks fans...")
        (data / "scripts" / "short_1.json").write_text(json.dumps({"hook": {"text": "Did Luka Doncic really..."}}))
        (data / "scripts" / "short_2.json").write_text("{}")
        (data / "media" / "short_1.json").write_text("[]")
        (data / "gate" / "short_1.json").write_text(json.dumps({"verdict": "PASS"}))
        (data / "gate" / "short_2.json").write_text(json.dumps({"verdict": "REVIEW"}))
        (data / "audio" / "short_1.timing.json").write_text("{}")
        (data / "audio" / "short_1.mp3").write_bytes(b"x" * 1000)
        (data / "video" / "short_1.mp4").write_bytes(b"x" * 1000)
        state.DATA = public_summary.DATA = data

    def tearDown(self):
        (state, public_summary) = self.mods
        state.DATA, public_summary.DATA = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_public_page_has_no_story(self):
        import public_summary
        text = "\n".join(public_summary.lines())
        self.assertIn("| 2 | 1 | 1 | 1 | 0 |", text)        # scripts, videos, PASS, REVIEW, REJECT
        self.assertNotIn("Luka", text)                       # no headline, hook or script

    def test_full_report_kept_privately_14_days(self):
        import tarfile
        from datetime import datetime, timezone
        import state
        home = self.tmp / "state" / "nba"
        (home / "runs").mkdir(parents=True)
        (home / "runs" / "2026-10-20_111.tar.gz").write_bytes(b"old")     # older than 14 days
        (home / "runs" / "2026-11-01_222.tar.gz").write_bytes(b"recent")
        kept = state.bundle_run(home, datetime(2026, 11, 11, tzinfo=timezone.utc))
        with tarfile.open(kept) as tar:
            names = sorted(tar.getnames())
        self.assertEqual(names, ["audio/short_1.timing.json", "gate/short_1.json", "gate/short_2.json",
                                 "media/short_1.json", "scripts/short_1.json", "scripts/short_2.json", "summary.md"])
        self.assertEqual(sorted(p.name for p in (home / "runs").iterdir()),
                         ["2026-11-01_222.tar.gz", kept.name])         # the old one is gone, no MP3/MP4


class PrivatePlan(unittest.TestCase):
    """11. plan/ is no longer in this public repository: every run restores it privately."""

    def test_restore_brings_the_plan(self):
        import state
        saved = (state.ROOT, state.DATA, state.STATE, state.HOME)
        tmp = Path(tempfile.mkdtemp())
        try:
            state.ROOT, state.DATA = tmp, tmp / "data"
            state.STATE = tmp / "state"
            state.HOME = state.STATE / "nba"
            (state.STATE / ".git").mkdir(parents=True)
            (state.HOME / "plan").mkdir(parents=True)
            (state.HOME / "plan" / "niche.json").write_text('{"date": "2026-11-09"}')
            (state.HOME / "plan" / "week.json").write_text('{"week_of": "2026-11-09"}')
            state.restore()
            self.assertEqual(sorted(p.name for p in (tmp / "plan").iterdir()), ["niche.json", "week.json"])
        finally:
            state.ROOT, state.DATA, state.STATE, state.HOME = saved
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertIn("plan/", (ROOT / ".gitignore").read_text())


# run 43011651547 (Brown snubs Tatum): what was on screen, beat by beat (main picture + alts)
RUN_43011651547 = [
    ["Celtics at Wizards 2024-12-015 (cropped).jpg", "Celtics at Wizards 2024-12-044 (cropped 2).jpg"],
    ["Jaylen Brown 2022.jpg", "Celtics at Wizards 2024-12-023.jpg", "Jaylen Brown (51840869654).jpg"],
    ["Celtics at Wizards 2024-12-036.jpg", "Jaylen Brown 2022 (cropped).jpg"],
    ["Anthony Tolliver defending Paul George.jpg", "Celtics at Wizards 2024-12-038.jpg"],
    ["Celtics at Wizards 2024-12-015.jpg", "Celtics at Wizards 2024-12-044 (cropped).jpg"],
    ["Celtics at Wizards 2024-12-013.jpg", "Celtics at Wizards 2024-12-019.jpg"],
]


def _commons(title: str) -> dict:
    return {"kind": "photo", "title": title, "source": "Wikimedia Commons",
            "page": "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_")}


class OnePhotoOnce(unittest.TestCase):
    """12. A photo and its crops ("X.jpg", "X (cropped).jpg", "X (cropped 2).jpg") are one picture."""

    def test_names(self):
        from picture_ids import already_shown, base_name, mark_shown
        self.assertEqual(base_name("Celtics at Wizards 2024-12-044 (cropped 2).jpg"),
                         ("celtics at wizards 2024-12-044", True))
        self.assertEqual(base_name("File:Jaylen_Brown_2022_cropped.jpg"), ("jaylen brown 2022", True))
        self.assertEqual(base_name("Jaylen Brown 2022.jpg"), ("jaylen brown 2022", False))
        shown: set = set()
        mark_shown(_commons("Jaylen Brown 2022.jpg"), shown)
        self.assertTrue(already_shown(_commons("Jaylen Brown 2022 (cropped).jpg"), shown))
        self.assertFalse(already_shown(_commons("Jaylen Brown 2023.jpg"), shown))        # another photo
        self.assertFalse(already_shown(_commons("Jaylen Brown 2022 (2).jpg"), shown))    # numbered = another shot
        # Flickr titles are not unique: two different "Jaylen Brown" photos are never merged
        flickr = {"kind": "photo", "title": "Jaylen Brown", "source": "Flickr via Openverse", "page": "f1"}
        shown2: set = set()
        mark_shown(flickr, shown2)
        self.assertFalse(already_shown({**flickr, "page": "f2"}, shown2))

    def _items(self):
        out = []
        for beat, titles in enumerate(RUN_43011651547):
            main, *alts = [_commons(t) for t in titles]
            out.append({**main, "beat": beat, "alts": alts, "alt": alts[0] if alts else None})
        return out

    def test_the_real_run_has_no_repeat(self):
        import media
        import render
        for mod in (media, render):
            saved = mod.picture_hash
            mod.picture_hash = lambda path: None        # no files here: only the names decide
            try:
                got = mod.no_repeats(copy.deepcopy(self._items()))
            finally:
                mod.picture_hash = saved
            shown = [x["title"] for it in got if it for x in [it] + (it.get("alts") or [])]
            self.assertEqual(len(shown), 10, mod.__name__)      # 13 shots, 3 were repeats of a photo
            for gone in ("Jaylen Brown 2022 (cropped).jpg", "Celtics at Wizards 2024-12-015.jpg",
                         "Celtics at Wizards 2024-12-044 (cropped).jpg"):
                self.assertNotIn(gone, shown, mod.__name__)
            self.assertIn("Celtics at Wizards 2024-12-015 (cropped).jpg", shown)   # the first one stays

    def test_a_crop_named_after_the_person(self):
        """Run 43027675858: "...-036 (White).jpg" (Derrick White cut out) and "...-036.jpg" were
        both on screen. A "(name)" after a numbered file is a crop; other names stay apart."""
        from picture_ids import already_shown, base_name, mark_shown
        shown = set()
        mark_shown(_commons("Celtics at Wizards 2024-12-036 (White).jpg"), shown)
        self.assertTrue(already_shown(_commons("Celtics at Wizards 2024-12-036.jpg"), shown))
        self.assertFalse(already_shown(_commons("Celtics at Wizards 2024-12-038.jpg"), shown))
        for own in ("Doc Rivers (coach).jpg", "Jayson Tatum (2018).jpg", "Doc Rivers (31361603010).jpg",
                    "20150401 MCDAAG Jaylen Brown floater (1).JPG"):
            self.assertFalse(base_name(own)[1], own)

    def test_commons_files_found_through_openverse(self):
        """Run 43088629255: "Jaylen Brown 2022" and "Jaylen Brown 2022 (cropped)" came through
        Openverse (source "Wikimedia via Openverse") and were both shown."""
        from picture_ids import already_shown, mark_shown
        ov = lambda t, cur: {"kind": "photo", "source": "Wikimedia via Openverse", "title": t,
                             "page": f"https://commons.wikimedia.org/w/index.php?curid={cur}",
                             "url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/x.jpg"}
        shown = set()
        mark_shown(ov("Jaylen Brown 2022", 115872550), shown)
        self.assertTrue(already_shown(ov("Jaylen Brown 2022 (cropped)", 131264916), shown))
        self.assertTrue(already_shown(_commons("Jaylen Brown 2022 (cropped).jpg"), shown))   # across sources
        self.assertFalse(already_shown(ov("Jaylen Brown (51840869654)", 115872551), shown))  # another file
        flickr = {"kind": "photo", "source": "Flickr", "title": "Jaylen Brown 2022 (cropped)",
                  "page": "https://www.flickr.com/photos/x/1", "url": "https://live.staticflickr.com/1.jpg"}
        self.assertFalse(already_shown(flickr, shown))                                       # not Commons

    def test_fill_never_brings_another_crop(self):
        import media
        saved = {k: getattr(media, k) for k in ("person_photos", "download", "picture_hash", "image_ok")}
        folder = media.ROOT / "data" / "_test_crop"
        try:
            clear = {"v": "C", "s": "game", "t": "drives"}    # D30: a top-up must show him clearly
            offered = [{**_commons("Jaylen Brown 2022.jpg"), "url": "u1", "tag": clear},
                       {**_commons("Jaylen Brown 2024.jpg"), "url": "u2", "tag": clear}]
            media.person_photos = lambda person, shown: [dict(c) for c in offered]
            media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            media.image_ok = lambda path: True
            media.picture_hash = lambda path: None
            items = [{**_commons("Jaylen Brown 2022 (cropped).jpg"), "file": "data/x.jpg", "match": 8}, None]
            got = media.fill_empty(items, 2, folder, set(), ["Jaylen Brown"], None)
            self.assertEqual(got[1]["title"], "Jaylen Brown 2024.jpg")   # not the uncropped original again
        finally:
            for k, v in saved.items():
                setattr(media, k, v)
            shutil.rmtree(folder, ignore_errors=True)


class CurrentTeam(unittest.TestCase):
    """13. Run 43011651547 showed Jaylen Brown in a Celtics jersey while the story said "now in
    Philly", and Paul George in a Pacers jersey: today's uniform comes first now."""

    CLAIMS = {"Q19664817": [   # Jaylen Brown: Celtics 2016-2026, 76ers since 2026, a college spell
        {"mainsnak": {"datavalue": {"value": {"id": "Q131371"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2016-06-23T00:00:00Z"}}}],
                        "P582": [{"datavalue": {"value": {"time": "+2026-07-01T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q138089"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2026-07-01T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q999"}}}, "rank": "normal", "qualifiers": {}}]}
    LABELS = {"Q131371": "Boston Celtics", "Q138089": "Philadelphia 76ers", "Q999": "California Golden Bears"}

    def setUp(self):
        import media
        self.m = media
        self.saved = (media.get, dict(media._wikidata), dict(media._teams))
        media._wikidata.clear()
        media._teams.clear()
        media._wikidata["Jaylen Brown"] = "Q19664817"
        claims, labels = self.CLAIMS, self.LABELS

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("action") == "wbgetclaims":
                return json.dumps({"claims": {"P54": claims.get(q["entity"], [])}}).encode()
            if q.get("action") == "wbgetentities":
                return json.dumps({"entities": {i: {"labels": {"en": {"value": labels[i]}}}
                                                for i in q["ids"].split("|") if i in labels}}).encode()
            raise OSError("unexpected")
        media.get = get

    def tearDown(self):
        self.m.get = self.saved[0]
        self.m._wikidata.clear()
        self.m._wikidata.update(self.saved[1])
        self.m._teams.clear()
        self.m._teams.update(self.saved[2])

    def test_current_and_former_teams(self):
        self.assertEqual(self.m.teams_of("Jaylen Brown"), ("philadelphia 76ers", {"boston celtics"}))
        t = self.m.photo_team
        self.assertEqual(t("Jaylen Brown", "Celtics at Wizards 2024-12-015 (cropped).jpg"), "former")
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown 76ers media day 2026"), "current")
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown, Sixers vs Celtics"), "current")   # today's team named
        self.assertEqual(t("Jaylen Brown", "Jaylen Brown 2022.jpg"), "")                   # no team: unchanged
        # an older photo naming today's team is not today's uniform (Brown was a Celtic in 2023)
        self.assertEqual(t("Jaylen Brown", "Celtics at 76ers 2023", 2023), "former")
        self.assertEqual(t("Jaylen Brown", "76ers media day", 2026), "current")
        self.assertEqual(self.m.people_line(["Jaylen Brown", "Bomani Jones"]),
                         "Jaylen Brown (now with the Philadelphia 76ers), Bomani Jones")
        self.assertIn("UNIFORMS", self.m.PICK_PROMPT)

    def test_photo_order_today_first(self):
        m = self.m
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "team": "former"}, {"page": "b", "score": 20, "team": ""},
                {"page": "c", "score": 10, "team": "current"}, {"page": "d", "score": 25, "team": ""}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            self.assertEqual([p["page"] for p in m.photos("Jaylen Brown")], ["c", "d", "b", "a"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])

    def test_unknown_or_down_changes_nothing(self):
        self.assertEqual(self.m.teams_of("Bomani Jones"), ("", set()))       # no Wikidata item: no request
        self.assertEqual(self.m.photo_team("Bomani Jones", "Celtics at Wizards"), "")
        self.m._teams.clear()

        def down(url, timeout=30):
            raise OSError("down")
        self.m.get = down
        self.assertEqual(self.m.teams_of("Jaylen Brown"), ("", set()))
        self.assertEqual(self.m.people_line(["Jaylen Brown"]), "Jaylen Brown")


class WikimediaPolite(unittest.TestCase):
    """2026-11-11: Wikimedia answered 429 to a shared cloud IP before we sent anything. With a
    token the limit is per account; without one nothing may change."""

    def setUp(self):
        import urllib.error
        import urllib.request
        import wiki_http
        self.w, self.err, self.req = wiki_http, urllib.error, urllib.request
        self.saved = (wiki_http.TOKEN[0], wiki_http.WAIT_BUDGET[0], wiki_http._sleep,
                      urllib.request.urlopen)
        self.calls, self.slept, self.answers = [], [], []
        wiki_http._sleep = self.slept.append
        # 2026-11-17: a full waiting budget for each test (an earlier test's real 429s had spent it)
        wiki_http.WAIT_BUDGET[0] = 90.0

        class Reply:
            def __init__(s, body): s.body = body
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return s.body

        def fake(req, timeout=30):
            self.calls.append(dict(req.header_items()))
            a = self.answers.pop(0)
            if isinstance(a, int):
                raise self.err.HTTPError(req.full_url, a, "x", {"Retry-After": "20"}, None)
            return Reply(a)
        urllib.request.urlopen = fake

    def tearDown(self):
        w = self.w
        w.TOKEN[0], w.WAIT_BUDGET[0], w._sleep, self.req.urlopen = self.saved

    API = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=Q1"

    def test_token_only_to_wikimedia_apis(self):
        self.w.TOKEN[0] = "t0k"
        self.assertEqual(self.w.headers(self.API, "UA").get("Authorization"), "Bearer t0k")
        for url in ("https://upload.wikimedia.org/wikipedia/commons/a/a1/X.jpg",
                    "https://api.openverse.org/v1/images/?q=x",
                    "https://evil.example/w/api.php?wikipedia.org/",
                    "https://en.wikipedia.org.evil.example/w/api.php"):
            self.assertNotIn("Authorization", self.w.headers(url, "UA"), url)
        self.w.TOKEN[0] = ""
        self.assertNotIn("Authorization", self.w.headers(self.API, "UA"))

    def test_429_waited_out_then_answer(self):
        self.answers = [429, b"ok"]
        self.assertEqual(self.w.fetch(self.API, "UA"), b"ok")
        self.assertEqual(self.slept, [20.0])

    def test_wait_budget_never_hangs_a_run(self):
        self.w.WAIT_BUDGET[0] = 10.0
        self.answers = [429]
        with self.assertRaises(self.err.HTTPError):
            self.w.fetch(self.API, "UA")
        self.assertEqual(self.slept, [])

    def test_refused_token_dropped_and_call_repeated(self):
        self.w.TOKEN[0] = "old"
        self.answers = [401, b"ok"]
        self.assertEqual(self.w.fetch(self.API, "UA"), b"ok")
        self.assertIn("Authorization", self.calls[0])
        self.assertNotIn("Authorization", self.calls[1])
        self.assertEqual(self.w.TOKEN[0], "")

    def test_other_sites_exactly_as_before(self):
        self.w.TOKEN[0] = "t0k"
        self.answers = [429]
        with self.assertRaises(self.err.HTTPError):
            self.w.fetch("https://pixabay.com/api/?q=x", "UA")
        self.assertEqual((len(self.calls), self.slept), (1, []))
        self.assertNotIn("Authorization", self.calls[0])

    def test_media_and_signals_use_it(self):
        import media
        import signals
        self.assertIs(media.wiki_http, self.w)
        self.assertIs(signals.wiki_http, self.w)
        self.answers = [b"{}"]
        self.assertEqual(media.get(self.API), b"{}")


class SceneSpread(unittest.TestCase):
    """Run 43011651547: 9 of its 13 photos were Hameltion's "Celtics at Wizards 2024-12-0NN"."""

    def setUp(self):
        import media
        from collections import Counter
        self.m, self.Counter = media, Counter

    def ph(self, title, author="Hameltion", date="2024-12-15"):
        return {"kind": "photo", "title": title, "author": author, "date": date, "page": title}

    def test_scene_keys(self):
        m = self.m
        a = m.scene_of(self.ph("Celtics at Wizards 2024-12-015 (cropped).jpg"))
        self.assertEqual(a, m.scene_of(self.ph("Celtics at Wizards 2024-12-044.jpg")))
        jak = "Pemain Bola Basket NBA dari Amerika Melatih Pelajar SMA di Jakarta (%s)"
        s1 = m.scene_of(self.ph(jak % "42950693724", "U.S. Embassy Jakarta", ""))
        self.assertIsNotNone(s1)
        self.assertEqual(s1, m.scene_of(self.ph(jak % "42950705794", "U.S. Embassy Jakarta", "")))
        # no date and no numbered series, or no real author: unknown, never grouped
        self.assertIsNone(m.scene_of(self.ph("Jaylen Brown", "Keith Allison", "")))
        self.assertIsNone(m.scene_of(self.ph("Celtics at Wizards 2024-12-015.jpg", "unknown author")))
        self.assertIsNone(m.scene_of({"kind": "video", "title": "x", "author": "a", "date": "2024"}))

    def _pool(self):
        h = [self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg") for n in (15, 23, 36, 38, 44)]
        other = [self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"),
                 self.ph("Jaylen Brown Sixers.jpg", "Someone", "2026-10-30")]
        return h + other

    def test_full_scene_goes_behind_everything_else(self):
        """Owner, 2026-11-12: a 4th photo of one scene only when nothing else is left, then by
        score (before: it waited only behind equally related photos scoring 6+)."""
        m, c = self.m, self._pool()
        scenes = self.Counter({m.scene_of(c[0]): 3})
        tier = lambda j: 3
        scores = {0: 8, 1: 8, 5: 7, 6: 6}
        self.assertEqual(m.spread_scenes([0, 1, 5, 6], c, tier, scores, scenes), [5, 6, 0, 1])
        self.assertEqual(m.spread_scenes([0, 1, 5], c, tier, scores, self.Counter()), [0, 1, 5])
        self.assertEqual(m.spread_scenes([0, 1], c, tier, scores, scenes), [0, 1])  # nothing else: by score
        # behind a less related or weaker photo too (the old rule kept it in front of those)
        self.assertEqual(m.spread_scenes([0, 5], c, {0: 3, 5: 2}.get, {0: 8, 5: 9}, scenes), [5, 0])
        self.assertEqual(m.spread_scenes([0, 5], c, tier, {0: 8, 5: 5}, scenes), [5, 0])

    def test_scene_from_the_file_name(self):
        m = self.m
        wh = {"kind": "photo", "author": "The White House", "date": "",
              "title": "Joe Biden Steph Curry Steve Kerr P20230117AS-1347.jpg"}
        self.assertEqual(m.scene_of(wh), ("the white house", "2023-01-17"))
        self.assertEqual(m.scene_of(wh), m.scene_of({**wh, "title": "P20230117AS-2061 (52636052765).jpg",
                                                     "date": "2023-01-17"}))
        self.assertIsNone(m.TITLE_DAY.search("Steph Curry (51913909237).jpg"))   # a Flickr id is no date

    def test_replay_of_the_run(self):
        """The run's 13 shots in its own order, with two fitting photos of other games added to
        the pool: the Wizards game is shown at most SCENE_MAX times, nothing is lost."""
        m = self.m
        run = [self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg") for n in (15, 44, 23, 36, 38, 13, 19, 11, 12)]
        others = [self.ph(f"Jaylen Brown {k}.jpg", "All-Pro Reels", "2022-01-23") for k in range(2)] + \
                 [self.ph(f"Jaylen Brown game {k}.jpg", f"Author {k}", f"2025-0{k + 1}-02") for k in range(6)]
        pool = run + others
        scores = {j: 8 if j < len(run) else 6 for j in range(len(pool))}
        scenes, shown = self.Counter(), []
        for _ in range(13):
            order = [j for j in range(len(pool)) if j not in shown]
            left = m.spread_scenes(order, pool, lambda j: 3, scores, scenes)
            if not left:
                break
            j = left[0]
            shown.append(j)
            scenes.update([m.scene_of(pool[j])])
        # before B11: 9 of 13 from the Wizards game. Now 3, then the 8 other photos, then (pool
        # used up) 2 more Wizards shots rather than a frozen picture
        self.assertEqual(sum(1 for j in shown if j < len(run)), 5)
        self.assertEqual(len(set(shown)), 13)
        self.assertTrue(all(j >= len(run) for j in shown[3:11]))
        self.assertEqual(shown[:m.SCENE_MAX], [0, 1, 2])     # the best come first, as before

    def test_flickr_photos_know_their_day(self):
        m = self.m
        saved = (m.FLICKR_KEY, m.get, m.namesake, dict(m.PHOTO_STATS))
        reply = {"stat": "ok", "photos": {"photo": [
            {"title": "Jaylen Brown", "tags": "basketball nba", "license": k, "owner": "o", "id": str(n),
             "ownername": "Keith Allison", "datetaken": f"2019-03-0{n} 19:30:00",
             "url_k": f"https://live.staticflickr.com/{n}.jpg", "width_k": "1400", "height_k": "2000"}
            for n, k in ((1, next(k for k, v in m.FLICKR_LICENCES.items() if m.licence_ok(v))),)]}}
        try:
            m.FLICKR_KEY, m.namesake = "k", (lambda p, t: False)
            m.get = lambda url, timeout=30: json.dumps(reply).encode()
            got = m.flickr_photos("Jaylen Brown")
            self.assertEqual(got[0]["date"], "2019-03-01")
            self.assertEqual(m.scene_of(got[0]), ("keith allison", "2019-03-01"))
        finally:
            m.FLICKR_KEY, m.get, m.namesake = saved[:3]
            m.PHOTO_STATS.clear(); m.PHOTO_STATS.update(saved[3])

    def test_fill_prefers_another_game(self):
        m = self.m
        saved = {k: getattr(m, k) for k in ("person_photos", "download", "picture_hash", "image_ok")}
        folder = m.ROOT / "data" / "_test_scene"
        try:
            clear = {"v": "C", "s": "game", "t": "drives"}    # D30: a top-up must show him clearly
            wiz = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "url": f"w{n}", "tag": clear} for n in (11, 12, 13)]
            new = {**self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"), "url": "a", "tag": clear}
            m.person_photos = lambda person, shown: [dict(c) for c in wiz + [new]]
            m.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
            m.image_ok = lambda path: True
            m.picture_hash = lambda path: None
            on = [{**self.ph(f"Celtics at Wizards 2024-12-0{n}.jpg"), "file": "data/x.jpg"} for n in (15, 23, 36)]
            items = [{**on[0], "file": "data/x.jpg", "match": 8, "alts": on[1:]}, None, None]
            got = m.fill_empty(items, 3, folder, set(), ["Jaylen Brown"], None)
            self.assertEqual(got[1]["title"], "Jaylen Brown 2022.jpg")       # another game first
            self.assertEqual(got[2]["title"], "Celtics at Wizards 2024-12-011.jpg")  # nothing else left
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
            shutil.rmtree(folder, ignore_errors=True)

    def test_fill_counts_what_is_on_screen(self):
        m = self.m
        items = [{**self.ph("Celtics at Wizards 2024-12-015.jpg"),
                  "alts": [self.ph("Celtics at Wizards 2024-12-023.jpg"), self.ph("Celtics at Wizards 2024-12-036.jpg")]}]
        sc = m.count_scenes(x for it in items for x in [it] + it["alts"])
        self.assertTrue(m.scene_full(self.ph("Celtics at Wizards 2024-12-044.jpg"), sc))
        self.assertFalse(m.scene_full(self.ph("Jaylen Brown 2022.jpg", "All-Pro Reels", "2022-01-23"), sc))


class OwnArticleFirst(unittest.TestCase):
    """Run 43027675858: 47 headlines, 3 articles read, the pick's own one ("Jaylen Brown explains
    why he ignored...") 6th in line and never read. Offline: reading is faked."""

    HEAD = "Jaylen Brown explains why he ignored Jayson Tatum\u2019s attempt at pre-game embrace before first-ever clash"

    def _editor(self):
        it = lambda t, tier, link: {"title": t, "tier": tier, "link": link, "publisher": "P"}
        return {"ranked": [{"id": 0, "same_as": [1]}],
                "topics": [{"headline": self.HEAD, "items": [
                    it("Kevin O'Connor calls out 76ers' Jaylen Brown", 1, "https://a/1"),
                    it("The Bounce: Jaylen Brown's real beef is with the Celtics", 1, "https://a/2"),
                    it("Payton Pritchard on Jaylen Brown, Jayson Tatum relationship", 1, "https://a/3"),
                    it("People Close to Jayson Tatum, Jaylen Brown Keep Saying the Same Thing", 1, "https://a/4"),
                    it(self.HEAD, 1, "https://a/own"),
                    it("Jaylen Brown explains why he ignored Jayson Tatum pregame", 2, "https://b/copy")]},
                           {"headline": "Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win", "items": [
                    it("Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win", 1, "https://a/merged")]}]}

    def run_with(self, readable):
        import script
        saved = (script.read_article, script.decode_google)
        tried = []

        def fake(it, real):
            tried.append(it["link"])
            if it["link"] in readable:
                it["text"] = "x" * 700
                return True
            return False
        script.read_article, script.decode_google = fake, (lambda links: {})
        try:
            e = self._editor()
            return script.gather_sources(e["topics"][0], e, 0), tried
        finally:
            script.read_article, script.decode_google = saved

    def test_own_article_read_first(self):
        import script
        src, tried = self.run_with({"https://a/own", "https://a/1", "https://a/2", "https://a/merged"})
        self.assertEqual(tried[0], "https://a/own")
        self.assertEqual(tried[1], "https://a/merged")     # the merged story's own headline next
        self.assertTrue(src[0]["main"])
        self.assertEqual(sum(bool(s["text"]) for s in src), 4)   # every readable one, up to MAX_ARTICLES
        self.assertIn("read in full, source [1]", script.main_note(src, self.HEAD))

    def test_other_outlets_of_the_same_story_are_read_too(self):
        """37. Run 43253965466: Zion's story from Yahoo, Bleacher Report, RealGM and ESPN, all near
        the headline: 1 of 4 read (the other copies were never tried). Now up to MAX_ARTICLES."""
        import script
        head = "Zion Williamson tears into Pelicans after 'unacceptable' loss to Nets"
        it = lambda t, tier, link: {"title": t, "tier": tier, "link": link, "publisher": "P"}
        e = {"ranked": [{"id": 0, "same_as": []}], "topics": [{"headline": head, "items": [
            it(head, 1, "https://yahoo/1"),
            it("Zion Williamson Calls Out Pelicans After Loss to Nets", 1, "https://br/1"),
            it("Zion Williamson Calls Pelicans' 145-111 Loss To Nets 'Unacceptable'", 2, "https://realgm/1"),
            it("Zion Williamson calls out Pelicans for another 'unacceptable' blowout loss", 1, "https://espn/1")]}]}
        saved = (script.read_article, script.decode_google)
        tried = []

        def fake(x, real):
            tried.append(x["link"])
            x["text"] = "y" * 700
            return True
        script.read_article, script.decode_google = fake, (lambda links: {})
        try:
            src = script.gather_sources(e["topics"][0], e, 0)
        finally:
            script.read_article, script.decode_google = saved
        self.assertEqual(tried[0], "https://yahoo/1")
        self.assertEqual(sorted(tried), sorted(["https://yahoo/1", "https://br/1", "https://realgm/1", "https://espn/1"]))
        self.assertEqual(sum(bool(x["text"]) for x in src), 4)
        self.assertEqual([x["link"] for x in src if x["main"]], ["https://yahoo/1"])   # one main only

    def test_45_0_is_45(self):
        """37. Run 43253965466: "averaged a staggering 45.0 points" in the source, "45" in the hook."""
        import script
        src = [{"title": "", "text": "Luka averaged a staggering 45.0 points, 7.0 rebounds and 8.30 assists"}]
        self.assertEqual(script.fact_check("Luka Doncic averaged 45 points, 7 rebounds, 8.3 assists.", src), [])
        self.assertEqual(script.fact_check("Luka Doncic averaged 46 points.", src), ["46"])
        self.assertEqual(script.numbers("100 and 10 and 0.5 and 2026"), {"100", "10", "0.5", "2026"})

    def test_same_article_from_another_outlet(self):
        import script
        src, tried = self.run_with({"https://b/copy", "https://a/1"})
        self.assertEqual(tried[:2], ["https://a/own", "https://b/copy"])
        self.assertEqual([s["link"] for s in src if s["main"]], ["https://b/copy"])

    def test_unread_own_article_is_never_promised(self):
        import script
        src, _ = self.run_with({"https://a/1", "https://a/2"})
        self.assertFalse(any(s["main"] for s in src))
        note = script.main_note(src, self.HEAD)
        self.assertIn("NOT READ", note)
        self.assertIn("Never promise", note)
        self.assertIn("{main_note}", script.PROMPT)

    def test_closeness(self):
        import script
        self.assertEqual(script.closeness(self.HEAD, self.HEAD), 1.0)
        self.assertGreaterEqual(script.closeness("Jaylen Brown explains why he ignored Jayson Tatum pregame", self.HEAD),
                                script.NEAR)
        self.assertLess(script.closeness("Kevin O'Connor calls out 76ers' Jaylen Brown", self.HEAD), script.NEAR)
        self.assertEqual(script.closeness("Jaylen Brown Tatum", self.HEAD), 0.0)   # too short to tell


class MustKnowContext(unittest.TestCase):
    """Run 43027675858: Paul George's 36 points without "the player Boston got for Brown", no
    game result, no "Giannis now plays for Miami", and "Heat radio host" for a podcast host.
    The writer is told, and the critic checks it again."""

    def test_writer_and_critic_both_have_the_rule(self):
        import script
        w, c = script.PROMPT, script.HUMANIZE
        self.assertIn("MUST-KNOW CONTEXT", w)
        self.assertIn("MUST-KNOW CONTEXT", c)
        for need in ("who they are in THIS story", "who went where", "its result (who won",
                     "current team", "never fill it from memory", "as the sources\n     give it"):
            self.assertIn(need, w, need)
        for need in ("who is that?", "without who went where", "without who won",
                     "exactly as the sources"):
            self.assertIn(need, c, need)

    def test_prompts_still_format(self):
        import script
        script.HUMANIZE.format(voice="v", sources="s", draft="d")
        self.assertIn("MUST-KNOW", script.PROMPT.format(**{k: "x" for k in (
            "skill_script", "skill_package", "skill_seo", "voice", "formulas", "rules", "headline",
            "main_note", "why", "two_versions", "story_type", "niche", "search", "history", "sources")}))


class OwnTake(unittest.TestCase):
    """Run 43027675858's payoff: "The New York Times argues Brown's real fight is with Boston,
    and I think that's right." Agreement is not analysis."""

    REAL = ("Derrick White said \"No beef.\" The New York Times argues Brown's real fight is with "
            "Boston, and I think that's right.")

    def pay(self, say):
        return [{"say": "Brown snubbed Tatum.", "stage": "setup"}, {"say": say, "stage": "payoff"},
                {"say": "So who was he mad at, Tatum or Boston?", "stage": "exit"}]

    def doc(self, say):
        return [{"say": "Doc Rivers questioned Giannis's IQ, then apologized.", "stage": "setup"},
                {"say": say, "stage": "payoff"}, {"say": "So is Doc's apology enough?", "stage": "exit"}]

    def test_agreement_only_goes_to_repair(self):
        import script
        for say in (self.REAL, "The Times says it's Boston. I agree.", "Honestly, they're not wrong.",
                    "Bomani says he blames others, and honestly, Bomani is right.", "I buy it."):
            self.assertTrue(script.borrowed_take(self.pay(say)), say)
        problems = script.repair_needed("Did Brown snub Tatum?", self.pay(self.REAL), {})
        self.assertTrue(any("her OWN reason" in p for p in problems), problems)

    def test_her_own_takes_stay(self):
        """Every real payoff of the earlier runs, and agreement WITH a reason, is left alone."""
        import script
        for say in ("I think the apology fixed the wording, not the pattern.",
                    "I think that snub backfired, the scoreboard got the last word.",
                    "Bomani Jones said parts were correct, but an apology fixes the wording, not the point.",
                    "One fan said he only has value in Golden State. I think the passing says otherwise.",
                    "The Times says it's Boston, and I think that's right, because he went quiet that night.",
                    "I think Doc is wrong.", "Honestly, Doc is wrong.", "Doc was half right and fully clumsy."):
            self.assertFalse(script.borrowed_take(self.pay(say)), say)
        self.assertEqual(script.repair_needed("Did Doc apologize?",
                                              self.doc("I think the apology fixed the wording, not the pattern."), {}), [])

    def test_writer_critic_repair_told(self):
        import script
        self.assertIn("Agreeing with an outlet", script.PROMPT)
        self.assertIn("never only agreeing with someone else's view", script.HUMANIZE)
        self.assertIn("never only agreeing with someone else's view", script.REPAIR)


class HookPick(unittest.TestCase):
    """Run 43027675858: "Why did Jaylen Brown leave Jayson Tatum's pregame dap hanging...?" (the
    Short never said why) and "Did Brendan Tobin just tell Doc Rivers...?" (a podcaster first)."""

    def test_the_fan_sees_story_and_known_names(self):
        import script
        seen = {}

        def fake(prompt, model=None, **kw):
            seen["prompt"] = prompt
            return {"best": 2}
        saved = script.ask_claude
        script.ask_claude = fake
        try:
            hooks = [{"text": "Did Brendan Tobin just tell Doc Rivers the blame is his?", "question": True, "score": 41},
                     {"text": "Did Doc Rivers just say sorry to Giannis, and mean it?", "question": True, "score": 45}]
            got = script.intrigue_pick(hooks, "Doc Rivers apologizes", "Doc Rivers questioned Giannis's IQ...",
                                       ["Giannis Antetokounmpo 3.4", "Doc Rivers 2.3"])
        finally:
            script.ask_claude = saved
        p = seen["prompt"]
        self.assertIn("Giannis Antetokounmpo, Doc Rivers", p)      # names, not their fame numbers
        self.assertNotIn("3.4", p)
        self.assertIn("Doc Rivers questioned Giannis's IQ", p)      # the whole Short
        self.assertIn("THE SHORT PAYS IT OFF", p)
        self.assertIn("THE FIRST 3 SECONDS", p)
        self.assertIn("A STRANGER GETS IT AT ONCE", p)
        self.assertTrue(got[0]["intrigue_pick"])
        self.assertEqual(got[0]["text"], hooks[1]["text"])

    def test_old_call_still_works(self):
        import script
        saved = script.ask_claude
        script.ask_claude = lambda prompt, model=None, **kw: {"best": 1}
        try:
            hooks = [{"text": "A?", "question": True, "score": 50}, {"text": "B?", "question": True, "score": 45}]
            self.assertEqual(script.intrigue_pick(hooks, "h")[0]["text"], "A?")
        finally:
            script.ask_claude = saved


class DetailsFromSources(unittest.TestCase):
    """Run 43011651547's hook: "...in front of his own crowd": no source said where it was.
    Run 43027675858's "Heat radio host Brendan Tobin" WAS in the source ("Miami sports radio
    host Brendan Tobin"): a true detail must pass."""

    TOBIN = [{"title": "Heat Journalist Goes Ballistic On Doc Rivers", "tier": 1, "text":
              "Doc Rivers' comments drew criticism, including from Miami sports radio host Brendan "
              "Tobin. Speaking on the Heat Collective podcast, Tobin said..."}]
    SNUB = [{"title": "Jaylen Brown appears to blow off Jayson Tatum's greeting", "tier": 1, "text":
             "Brown did not greet Tatum before tip-off. Tatum scored 21 and Paul George 36."}]

    def test_true_details_pass(self):
        import compliance as C
        self.assertEqual(C.unsupported_details("Heat radio host Brendan Tobin says that's on you.", self.TOBIN), [])
        self.assertEqual(C.unsupported_details("On his podcast, Tobin went off.", self.TOBIN), [])
        self.assertEqual(C.unsupported_details("Brown snubbed Tatum, and Booker watched.", self.SNUB), [])

    def test_invented_details_caught(self):
        import compliance as C
        self.assertEqual(C.unsupported_details("Brown snubbed Tatum in front of his own crowd.", self.SNUB), ["crowd"])
        self.assertEqual(C.unsupported_details("The fans booed him on the road.", self.SNUB), ["booed", "on the road"])
        self.assertEqual(C.unsupported_details("ESPN analyst Tobin said it.", self.TOBIN), ["analyst"])

    def test_gate_holds_it(self):
        import compliance as C
        v, notes = C.check_fabrication("Brown snubbed Tatum in front of his own crowd.", self.SNUB, [], [])
        self.assertEqual(v, C.REVIEW)
        self.assertTrue(any("details not in the sources: crowd" in n for n in notes))
        v, _ = C.check_fabrication("Heat radio host Brendan Tobin says that's on you.", self.TOBIN, [], [])
        self.assertEqual(v, C.PASS)

    def test_repair_fixes_beats_not_the_fixed_hook(self):
        import script
        beats = [{"say": "Brown snubbed Tatum in front of his own crowd.", "stage": "setup"},
                 {"say": "I think the snub said more than his 13 points, because he went quiet.", "stage": "payoff"},
                 {"say": "So who won that night, Brown or Tatum?", "stage": "exit"}]
        problems = script.repair_needed("Did Brown snub Tatum?", beats, {}, self.SNUB)
        self.assertTrue(any("not in any source: crowd" in p for p in problems), problems)
        beats[0]["say"] = "Brown snubbed Tatum before tip-off."
        self.assertEqual(script.repair_needed("Did Brown snub Tatum in front of his own crowd?", beats, {}, self.SNUB), [])
        self.assertEqual(script.repair_needed("Did Brown snub Tatum?", beats, {}), [])   # old call unchanged


class FlexibleLength(unittest.TestCase):
    """Every Short of the earlier runs hit the 65-word ceiling (63-66 words): with context and
    her own reason required, the owner chose a flexible limit (2026-11-11, option "გ")."""

    def test_limits(self):
        import script
        self.assertEqual(script.BEAT_WORDS_MAX, 72)
        # the longest allowed Short (an 18-word hook + 72 words) is still "ready" (18-42 s)
        self.assertLessEqual(round((18 + 72) / script.WPM * 60), 42)

    def test_every_writer_knows_the_exception(self):
        import script
        for name in ("PROMPT", "HUMANIZE", "REPAIR"):
            text = getattr(script, name)
            self.assertIn("45-65 words", text, name)
            self.assertIn("72", text, name)
        self.assertIn("Never pad", script.PROMPT)
        self.assertIn("Never cut must-know context", script.TRIM)
        self.assertIn("72 spoken words or fewer", script.TRIM)


class ReadingAndQuestions(unittest.TestCase):
    """Owner, 2026-11-11: read five articles, give every site the time it needs. Run 43066151290:
    "So how was he not paying attention?" re-asked the hook; "Is Payton Pritchard right...?"
    brought in someone never introduced, and did not come back to the hook."""

    HOOK = "Jaylen Brown ignored Jayson Tatum twice in one night, so was he really not paying attention?"
    BEATS = [{"say": "Brown got traded to Philly for Paul George, and Tuesday was his first game vs Tatum.", "stage": "setup"},
             {"say": "Tatum tapped his chest at tip-off, but Brown skipped him after Boston's win.", "stage": "conflict"},
             {"say": "Yahoo reported Brown said beforehand he didn't intend to speak with Tatum. So how was he not paying attention?", "stage": "escalation"},
             {"say": "I think you can't announce a plan, then say you missed it.", "stage": "payoff"},
             {"say": "Is Payton Pritchard right that there was never beef, or was this planned?", "stage": "exit"}]

    def test_reading_limits(self):
        import script
        self.assertEqual(script.MAX_ARTICLES, 5)
        self.assertEqual(script.READ_CONFIG.get("DEFAULT", "DOWNLOAD_TIMEOUT"), "300")
        self.assertFalse(hasattr(script, "READ_BUDGET"))          # no limit on a story's reading
        self.assertGreaterEqual(script.TIMEOUT, 1200)              # Claude's analysis is never cut
        self.assertEqual(script.READ_TRIES, 2)

    def test_slow_site_gets_a_second_try(self):
        import script
        saved = (script.trafilatura.fetch_url, script.trafilatura.extract)
        calls = []

        def fetch(url, config=None):
            calls.append(config.get("DEFAULT", "DOWNLOAD_TIMEOUT"))
            return None if len(calls) == 1 else "<html>x</html>"
        script.trafilatura.fetch_url, script.trafilatura.extract = fetch, (lambda html: "article text " * 60)
        try:
            it = {"link": "https://a/1"}
            self.assertTrue(script.read_article(it, {}))
            self.assertEqual(calls, ["300", "300"])
        finally:
            script.trafilatura.fetch_url, script.trafilatura.extract = saved

    def test_the_run_is_caught(self):
        import script
        self.assertEqual(script.re_asked(self.HOOK, self.BEATS), [2])
        self.assertEqual(script.new_names_at_exit(self.HOOK, self.BEATS), ["Payton", "Pritchard"])
        self.assertFalse(script.loops_back(self.HOOK, self.BEATS[-1]["say"]))
        problems = script.repair_needed(self.HOOK, self.BEATS, {})
        for need in ("brings in Payton, Pritchard", "does not come back to the hook", "beat 3 asks the hook's question"):
            self.assertTrue(any(need in p for p in problems), (need, problems))

    def test_good_endings_left_alone(self):
        import script
        good = [dict(b) for b in self.BEATS]
        good[2]["say"] = "Yahoo reported Brown said beforehand he didn't intend to speak with Tatum."
        good[-1]["say"] = "So was Brown really not paying attention to Tatum, or was this planned?"
        self.assertEqual(script.re_asked(self.HOOK, good), [])
        self.assertEqual(script.new_names_at_exit(self.HOOK, good), [])
        self.assertTrue(script.loops_back(self.HOOK, good[-1]["say"]))
        # a possessive is the same name: "Doc's apology" loops to "Doc Rivers"
        self.assertTrue(script.loops_back("Did Doc Rivers just apologize to Giannis?", "So is Doc's apology enough?"))
        self.assertIn("QUESTIONS:", script.PROMPT)
        self.assertIn("QUESTIONS:", script.HUMANIZE)


class PhotoEra(CurrentTeam):
    """23. Run 43066151290: Brown's 2015 high school all-star photos in Paul George's Short, a
    2018 youth clinic in Jakarta as the hook, and a Commons derivative next to its original."""

    def test_before_his_nba_career(self):
        m = self.m
        m._nba_debut.clear()
        self.assertEqual(m.photo_team("Jaylen Brown", "20150401 MCDAAG Jaylen Brown dunk", 2015), "pre-nba")
        self.assertEqual(m.photo_team("Jaylen Brown", "Celtics at Wizards 2024-12-054", 2024), "former")
        self.assertEqual(m.photo_team("Jaylen Brown", "Jaylen Brown 76ers 2026", 2026), "current")
        self.assertEqual(m.photo_team("Jaylen Brown", "Jaylen Brown", None), "")   # no year: unchanged
        self.assertEqual(sorted(["pre-nba", "former", "", "current"], key=m.TEAM_ORDER.get),
                         ["current", "", "former", "pre-nba"])

    def test_claude_is_told(self):
        m = self.m
        self.assertEqual(m.photo_era({"date": "2015-04-01", "team": "pre-nba"}), "2015 PRE-NBA")
        self.assertEqual(m.photo_era({"date": "2014-03-05", "team": "former"}), "2014 OLD TEAM")
        self.assertEqual(m.photo_era({"date": "2026-04-02", "team": "current"}), "2026")
        self.assertEqual(m.photo_era({}), "")
        for rule in ("PRE-NBA", "score it 3 at most", "OFF COURT", "score it 4 at most", "OLD TEAM"):
            self.assertIn(rule, m.PICK_PROMPT, rule)

    def test_derivative_is_the_same_picture(self):
        from picture_ids import already_shown, mark_shown
        orig = _commons("Anthony Tolliver defending Paul George.jpg")
        der = {**_commons("Paul George Pacers.jpg"),
               "author": "File:Anthony Tolliver defending Paul George.jpg: joshuak8 derivative work: Chrishmt0423"}
        for first, second in ((orig, der), (der, orig)):
            shown = set()
            mark_shown(first, shown)
            self.assertTrue(already_shown(second, shown))
        shown = set()
        mark_shown(der, shown)
        self.assertFalse(already_shown(_commons("Pacers Paul George (cropped).jpg"), shown))


class OpenverseRetries(unittest.TestCase):
    """24. Openverse answers 504 to a search it has not seen, finishes it behind the scenes, and
    answers the same search fast a little later. Three quick tries lost every search."""

    def test_504s_then_the_answer(self):
        import time
        import urllib.error
        import urllib.request
        import media
        saved = (urllib.request.urlopen, time.sleep, media.OPENVERSE_BUDGET[0], media.openverse_token,
                 media.namesake, dict(media.PHOTO_STATS))
        slept, tries = [], []

        class Reply:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return json.dumps({"results": [{"title": "Paul George Celtics", "url": "https://x/1.jpg",
                                                         "width": 1200, "height": 1600, "license": "by",
                                                         "license_version": "2.0", "creator": "A"}]}).encode()

        def fake(req, timeout=30):
            tries.append(timeout)
            if len(tries) <= 4:
                raise urllib.error.HTTPError(req.full_url, 504, "Gateway Timeout", {}, None)
            return Reply()
        urllib.request.urlopen, time.sleep = fake, slept.append
        media.OPENVERSE_BUDGET[0], media.openverse_token, media.namesake = 50, (lambda: ""), (lambda p, t: False)
        saved_cache = media.OV_CACHE
        media.OV_CACHE = Path(tempfile.mkdtemp()) / "openverse_cache.json"
        try:
            got = media.openverse_photos("Paul George")
        finally:
            media.OV_CACHE = saved_cache
            (urllib.request.urlopen, time.sleep, media.OPENVERSE_BUDGET[0], media.openverse_token,
             media.namesake) = saved[:5]
            media.PHOTO_STATS.clear(); media.PHOTO_STATS.update(saved[5])
        self.assertEqual(len(got), 1)
        self.assertEqual(len(tries), 5)
        self.assertEqual(slept, [5, 10, 20, 30])
        self.assertEqual(sum(media.OPENVERSE_WAITS), 125)        # about two minutes at most


class TwoVersions(unittest.TestCase):
    """C1 (owner's plan, 2026-11-11): the channel lives on two accounts that clash. Run
    43066151290 had one ("wasn't paying attention" vs "said beforehand he wouldn't speak")."""

    def test_editor_names_it(self):
        import editor
        self.assertIn('"two_versions"', editor.PROMPT)
        self.assertIn("Never invent the other side", editor.PROMPT)

    def test_writer_and_critic(self):
        import script
        self.assertIn("TWO VERSIONS", script.PROMPT)
        self.assertIn("{two_versions}", script.PROMPT)
        self.assertIn("Never manufacture a contradiction", script.PROMPT)
        self.assertIn("TWO VERSIONS", script.HUMANIZE)
        self.assertIn("never invented", script.HUMANIZE)


class RumorLabels(unittest.TestCase):
    """C2 (owner's plan, 2026-11-11): one "reportedly" somewhere used to cover every rumor."""

    SPOKEN = ("Did the Lakers just put Austin Reaves on the table? Sources told ESPN the Lakers are "
              "shopping Reaves. The Kings want a guard before February. Windhorst thinks Reaves "
              "stays. So does LeBron keep his guard?")

    def claims(self, *pairs):
        return [{"text": t, "status": st, "source": 1} for st, t in pairs]

    def test_bare_rumor_caught_hedged_ones_pass(self):
        import compliance as C
        cl = self.claims(("ANONYMOUS", "The Lakers are shopping Austin Reaves"),
                         ("RUMOR", "The Kings want a guard before February"),
                         ("SPECULATION", "Windhorst thinks Reaves stays with the Lakers"))
        self.assertEqual(C.bare_claims(cl, self.SPOKEN), ["The Kings want a guard before February"])

    def test_facts_and_reports_untouched(self):
        import compliance as C
        cl = self.claims(("CONFIRMED", "Brown was traded to the 76ers for Paul George"),
                         ("REPORTED", "Brown said he did not intend to speak with Tatum"))
        self.assertEqual(C.bare_claims(cl, "Brown got traded to Philly for Paul George. Brown "
                                           "said beforehand he wouldn't speak with Tatum."), [])

    def test_gate_and_repair(self):
        import compliance as C
        import script
        cl = self.claims(("RUMOR", "The Kings want a guard before February"))
        v, notes, _ = C.check_claims(cl, [{"title": "x", "tier": 1, "text": "x"}], self.SPOKEN)
        self.assertEqual(v, C.REVIEW)
        self.assertTrue(any("sounds like a fact" in n for n in notes))
        beats = [{"say": "The Kings want a guard before February.", "stage": "setup"},
                 {"say": "I think the Lakers blink first, because Reaves is their second scorer.", "stage": "payoff"},
                 {"say": "So does LeBron keep his guard?", "stage": "exit"}]
        with patch.object(script, "ask_claude", claude_did_not_answer):   # D98: never the real Claude
            problems = script.repair_needed("Did LeBron's Lakers just shop Austin Reaves?", beats, {}, None, cl)
        self.assertTrue(any("sounds like a fact" in p for p in problems), problems)
        for word in ("ANONYMOUS", "SPECULATION", "IN ITS OWN SENTENCE"):
            self.assertIn(word, script.PROMPT)


class PodcastSources(unittest.TestCase):
    """C3 (owner's plan, 2026-11-11): beefs often start on podcasts (Arenas ripping Tatum and
    Brown, Stephen A. and Garnett). Articles about them come in through Google News."""

    def test_feeds(self):
        from sources import FEEDS
        by = {f["name"]: f for f in FEEDS}
        for name in ("GN: podcasts", "GN: podcast clash"):
            self.assertIn(name, by)
            self.assertEqual(by[name]["tier"], 2)            # never trusted alone for a rumor
            self.assertIn("when:1d", by[name]["url"])
            self.assertIn("-odds", by[name]["url"])          # betting previews kept out
        self.assertEqual(len(by), len(FEEDS))                # no name used twice


class HistoricBeefs(unittest.TestCase):
    """B20 / C4 (owner's plan, 2026-11-11): weak days get a famous beef that is back in the news."""

    def setUp(self):
        import tempfile
        import evergreen
        self.e = evergreen
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (evergreen.USED, evergreen.fresh_news, evergreen.wikipedia_item, evergreen.BANK)
        evergreen.USED = self.tmp / "evergreen_used.json"
        evergreen.BANK = [("Kobe Bryant", "Shaquille O'Neal", "the Kobe and Shaq feud"),
                          ("Michael Jordan", "Isiah Thomas", "the Jordan and Isiah feud"),
                          ("Kevin Durant", "Russell Westbrook", "Durant and Westbrook")]
        news = {"Kobe Bryant": 3, "Michael Jordan": 1, "Kevin Durant": 2}

        def fake(a, b, tier1=()):
            return [{"title": f"{a} recalls the {b} story {k}", "link": f"https://x/{a}{k}", "publisher": "P",
                     "tier": 2, "about": True} for k in range(news[a])]
        evergreen.fresh_news = fake
        evergreen.wikipedia_item = lambda a, b: {"title": "Feud (Wikipedia)", "link": "https://en.wikipedia.org/wiki/F",
                                                 "publisher": "Wikipedia", "tier": 1}
        import editor                       # never read the real made history in a test
        self.made, self.saved_made = [], editor.made_recently
        editor.made_recently = lambda: list(self.made)
        import script                       # D98: the title judgement never reaches the real Claude
        self.saved_ask, script.ask_claude = script.ask_claude, claude_did_not_answer

    def tearDown(self):
        import editor
        import script
        script.ask_claude = self.saved_ask
        editor.made_recently = self.saved_made
        self.e.USED, self.e.fresh_news, self.e.wikipedia_item, self.e.BANK = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_fill(self, shorts):
        import script
        saved = (script.build_short, script.OUT)
        script.OUT = self.tmp
        script.build_short = lambda n, tid, editor, voice, formulas: {"headline": editor["topics"][tid]["headline"], "beats": []}
        try:
            editor = {"topics": [], "ranked": []}
            self.assertFalse(script.fill_with_evergreen(shorts, editor, "", {}))
        finally:
            script.build_short, script.OUT = saved

    def test_same_feud_in_48_hours_is_skipped(self):
        """35. Run 43208765485: Draymond vs Poole made 17 h after a Short on the same two people."""
        import datetime as dt
        import editor
        recent = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=17)).isoformat()
        self.made = [{"time": recent, "headline": "Fans mock Kobe's claim he'd have no issue with O'Neal",
                      "hook": "Did Kobe really say that?"}]
        shorts = [{"headline": "today's strong story"}]
        self.run_fill(shorts)
        self.assertEqual(len(shorts), 2)
        self.assertNotEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        self.assertNotIn(self.e.key_of("Kobe Bryant", "Shaquille O'Neal"), self.e.used())   # not used up
        # older than 48 hours: allowed again
        self.made[0]["time"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=50)).isoformat()
        self.assertEqual(editor.pair_made_recently(["Kobe Bryant", "Shaquille O'Neal"], self.made), "")
        # only ONE of the two people in that Short: not the same feud
        self.made[0].update(time=recent, headline="Shaq rips the Lakers' bench", hook="Is Shaq right?")
        self.assertEqual(editor.pair_made_recently(["Kobe Bryant", "Shaquille O'Neal"], self.made), "")

    def test_same_feud_already_made_this_run_is_skipped(self):
        import datetime as dt
        import editor
        shorts = [{"headline": "Shaquille O'Neal fires back at Kobe Bryant's old teammate", "hook": {"text": "Shaq just fired back at Kobe."}}]
        self.run_fill(shorts)
        self.assertEqual(len(shorts), 2)
        self.assertNotEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        real = [{"time": "2026-11-11T18:46+00:00",
                 "headline": "'Would Welcome With Closed Fists,' 'Stop Lying' - NBA Fans Mock Draymond Green's Claim "
                             "That He'd Have 'No Issue' With Jordan Poole Warriors Reunion", "hook": ""}]
        now = dt.datetime(2026, 11, 12, 11, 28, tzinfo=dt.timezone.utc)
        self.assertTrue(editor.pair_made_recently(["Draymond Green", "Jordan Poole"], real, now))

    def test_only_fresh_and_not_recent(self):
        e = self.e
        got = e.candidates()
        self.assertEqual([c["key"] for c in got], [e.key_of("Kobe Bryant", "Shaquille O'Neal"),
                                                   e.key_of("Kevin Durant", "Russell Westbrook")])  # Jordan: 1 article
        self.assertIn("OLD", got[0]["why"])
        self.assertIn("NEVER present the old events as new", got[0]["why"])
        self.assertEqual(got[0]["items"][-1]["publisher"], "Wikipedia")
        e.mark_used(got[0]["key"])
        self.assertNotIn(got[0]["key"], [c["key"] for c in e.candidates()])          # 90 days
        import datetime as dt
        later = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=e.REUSE_DAYS + 1)
        self.assertIn(got[0]["key"], [c["key"] for c in e.candidates(now=later)])

    def test_about_them_not_just_named(self):
        e = self.e
        self.assertTrue(e.about_them("Derek Fisher on the Shaq and Kobe relationship: iron sharpening iron"))
        self.assertTrue(e.about_them("Kyrie Irving explains why he will not follow LeBron James path"))
        self.assertFalse(e.about_them("Thunder's Shai Gilgeous-Alexander Threatens Kevin Durant, Russell Westbrook Record"))
        only_named = [{"title": "SGA threatens Durant and Westbrook record", "link": "https://x/1", "tier": 2, "about": False},
                      {"title": "Durant and Westbrook record in danger", "link": "https://x/2", "tier": 2, "about": False}]
        e.fresh_news = lambda a, b, tier1=(): only_named if a == "Kevin Durant" else []
        self.assertEqual(e.candidates(), [])                     # named in passing only: not chosen

    def test_fills_only_the_empty_slot(self):
        import script
        saved = (script.build_short, script.OUT)
        made = []
        script.OUT = self.tmp
        script.build_short = lambda n, tid, editor, voice, formulas: (
            made.append(editor["topics"][tid]["headline"]) or {"headline": editor["topics"][tid]["headline"], "beats": []})
        try:
            editor = {"topics": [], "ranked": []}
            shorts = [{"headline": "today's strong story"}]
            self.assertFalse(script.fill_with_evergreen(shorts, editor, "", {}))
        finally:
            script.build_short, script.OUT = saved
        self.assertEqual(len(shorts), script.SHORTS_PER_RUN)                       # quota kept: one added
        self.assertEqual(len(made), 1)
        self.assertEqual(shorts[1]["evergreen"], self.e.key_of("Kobe Bryant", "Shaquille O'Neal"))
        self.assertIn(shorts[1]["evergreen"], self.e.used())
        self.assertTrue(editor["topics"][0]["verified"])

    def test_a_failure_never_costs_the_day(self):
        import script
        saved = script.build_short

        def boom(*a, **k):
            raise ValueError("not enough material")
        script.build_short = boom
        try:
            shorts = [{"headline": "x"}]
            self.assertFalse(script.fill_with_evergreen(shorts, {"topics": [], "ranked": []}, "", {}))
            self.assertEqual(len(shorts), 1)
            self.assertEqual(self.e.used(), {})                                        # nothing marked
        finally:
            script.build_short = saved


class StaleWikidata(CurrentTeam):
    """29. Run 43080115985: Jordan Poole's Wikidata spells have no dates and still say Golden
    State; his 2018 Michigan photos were not marked PRE-NBA."""

    def test_undated_current_team_not_trusted(self):
        m = self.m
        self.CLAIMS["Q50820763"] = [
            {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal", "qualifiers": {}},
            {"mainsnak": {"datavalue": {"value": {"id": "Q169165"}}}, "rank": "normal",
             "qualifiers": {"P582": [{"datavalue": {"value": {"time": "+2024-01-01T00:00:00Z"}}}]}}]
        self.LABELS.update({"Q157376": "Golden State Warriors", "Q169165": "Washington Wizards"})
        m._wikidata["Jordan Poole"] = "Q50820763"
        try:
            self.assertEqual(m.teams_of("Jordan Poole"), ("", set()))
            self.assertEqual(m.people_line(["Jordan Poole"]), "Jordan Poole")    # no false "now with"
        finally:
            del self.CLAIMS["Q50820763"]

    def test_college_photo_by_its_text(self):
        m = self.m
        self.assertEqual(m.photo_team("Jordan Poole", "20180206 UM-NW Jordan Poole Category:Michigan Wolverines men's basketball players"), "pre-nba")
        self.assertEqual(m.photo_team("Jaylen Brown", "20150401 MCDAAG Jaylen Brown dunk"), "pre-nba")
        self.assertNotEqual(m.photo_team("Kevin Durant", "Kevin Durant United States men's national basketball team 2012"), "pre-nba")
        self.assertNotEqual(m.photo_team("Draymond Green", "Draymond Green 2022 Warriors"), "pre-nba")
        self.assertNotEqual(m.photo_team("Jaylen Brown", "Jaylen Brown NBA Summer League 2016 college"), "pre-nba")

    def test_former_role_rule(self):
        import script
        self.assertIn("a FORMER role stays former", script.PROMPT)


class OpenverseKept(unittest.TestCase):
    """30. Run 43080115985: 3 of 5 Openverse searches still 504 after ~2 minutes of tries."""

    def setUp(self):
        import media
        self.m = media
        self.saved = media.OV_CACHE
        media.OV_CACHE = Path(tempfile.mkdtemp()) / "openverse_cache.json"

    def tearDown(self):
        shutil.rmtree(self.m.OV_CACHE.parent, ignore_errors=True)
        self.m.OV_CACHE = self.saved

    def test_kept_and_used_when_openverse_fails(self):
        import datetime as dt
        m = self.m
        photo = {"kind": "photo", "url": "https://x/1.jpg", "title": "Doc Rivers", "score": 3}
        m.openverse_keep("Doc Rivers", [photo])
        self.assertEqual(m.openverse_cached("Doc Rivers"), [photo])
        self.assertEqual(m.openverse_cached("Jordan Poole"), [])
        old = json.loads(m.OV_CACHE.read_text())
        old["Doc Rivers"]["day"] = (dt.date.today() - dt.timedelta(days=m.OV_CACHE_DAYS)).isoformat()
        m.OV_CACHE.write_text(json.dumps(old))
        self.assertEqual(m.openverse_cached("Doc Rivers"), [])             # too old: not used
        m.openverse_keep("Paul George", [photo])
        self.assertNotIn("Doc Rivers", json.loads(m.OV_CACHE.read_text()))  # and dropped on write

    def test_a_failed_search_returns_the_kept_one(self):
        import urllib.error
        import urllib.request
        import time
        m = self.m
        photo = {"kind": "photo", "url": "https://x/2.jpg", "title": "Doc Rivers", "score": 3}
        m.openverse_keep("Doc Rivers", [photo])
        saved = (urllib.request.urlopen, time.sleep, m.OPENVERSE_BUDGET[0], m.openverse_token, dict(m.PHOTO_STATS))

        def always_504(req, timeout=30):
            raise urllib.error.HTTPError(req.full_url, 504, "Gateway Timeout", {}, None)
        urllib.request.urlopen, time.sleep = always_504, (lambda s: None)
        m.OPENVERSE_BUDGET[0], m.openverse_token = 50, (lambda: "")
        try:
            got = m.openverse_photos("Doc Rivers")
            note = m.PHOTO_STATS["Doc Rivers"]["openverse"]
        finally:
            urllib.request.urlopen, time.sleep, m.OPENVERSE_BUDGET[0], m.openverse_token = saved[:4]
            m.PHOTO_STATS.clear(); m.PHOTO_STATS.update(saved[4])
        self.assertEqual(got, [photo])
        self.assertIn("kept", note)


class Initials(unittest.TestCase):
    """31. Run 43088629255: "So was Stephen A. smart to stand down from LeBron, or did money
    win?" was cut after "A.", the piece "So was Stephen A." counted as a repeat, Short held."""

    BEATS = [{"say": "LeBron confronted Stephen A. over his Bronny comments, and he let it go.", "stage": "setup"},
             {"say": "He told Kevin Garnett why: \"It's the first day of my new contract.\" 100 million from ESPN.", "stage": "conflict"},
             {"say": "He says he knew it would be a problem.", "stage": "escalation"},
             {"say": "I think that was smart: no argument is worth that kind of money. Now he says he's over it.", "stage": "payoff"},
             {"say": "So was Stephen A. smart to stand down from LeBron, or did money win?", "stage": "exit"}]

    def test_split(self):
        import compliance as C
        self.assertEqual(C.split_sentences("So was Stephen A. smart? Yes. J.R. Smith said no. Then Brown left."),
                         ["So was Stephen A. smart?", "Yes.", "J.R. Smith said no.", "Then Brown left."])
        self.assertEqual(C.split_sentences("Gary Payton Jr. scored. Dr. J smiled."), ["Gary Payton Jr. scored.", "Dr. J smiled."])

    def test_the_held_short_passes(self):
        import script
        self.assertEqual(script.retention_check(self.BEATS)["hard"], [])
        repeat = [dict(b) for b in self.BEATS]
        repeat[4]["say"] = "No argument is worth that kind of money. So was Stephen A. smart, or did money win?"
        self.assertIn("beat 5 repeats what was already said", script.retention_check(repeat)["hard"])   # real repeats still caught


class OneFeudIn48Hours(unittest.TestCase):
    """32. The made history of 2026-11-11 and the topics of run 43088629255."""

    MADE = [{"time": "2026-11-11T13:20+00:00",
             "headline": "Jayson Tatum won't give air to Jaylen Brown drama after snub",
             "hook": "Did Jaylen Brown just ignore Jayson Tatum twice?"},
            {"time": "2026-11-11T18:46+00:00",
             "headline": "Players Should Start Talking Crazy About Coaches Too - Draymond Green Calls Out Doc Rivers",
             "hook": "Is Draymond Green about to turn NBA players loose on coaches over Giannis Antetokounmpo?"}]

    def topic(self, headline, *stars):
        return {"headline": headline, "star_names": [f"{n} 2.0" for n in stars]}

    def setUp(self):
        import datetime as dt
        import editor
        self.e, self.now = editor, dt.datetime(2026, 11, 11, 19, 40, tzinfo=dt.timezone.utc)

    def test_same_feud_is_a_repeat(self):
        t = self.topic("Jayson Tatum responds to Jaylen Brown snub with runaway Celtics win",
                       "Jaylen Brown", "Jayson Tatum", "Paul George")
        self.assertIn("won't give air", self.e.same_feud_recent(t, self.MADE, self.now))

    def test_exceptions(self):
        e, now = self.e, self.now
        # a major turn
        self.assertEqual(e.same_feud_recent(self.topic("Jaylen Brown fined after Jayson Tatum altercation",
                                                       "Jaylen Brown", "Jayson Tatum"), self.MADE, now), "")
        # another person's own story (only one of them in the headline)
        self.assertEqual(e.same_feud_recent(self.topic("Paul George explains his middle finger to a 76ers fan",
                                                       "Jaylen Brown", "Jayson Tatum", "Paul George"), self.MADE, now), "")
        # a new voice leads: Garnett was not in the earlier Short
        self.assertEqual(e.same_feud_recent(self.topic("Kevin Garnett rips Jaylen Brown and Jayson Tatum",
                                                       "Jaylen Brown", "Jayson Tatum", "Kevin Garnett"), self.MADE, now), "")
        # after 48 hours the feud is open again
        import datetime as dt
        later = now + dt.timedelta(hours=49)
        self.assertEqual(e.same_feud_recent(self.topic("Jayson Tatum responds to Jaylen Brown",
                                                       "Jaylen Brown", "Jayson Tatum"), self.MADE, later), "")

    def test_the_editor_drops_it(self):
        import json as _j
        e = self.e
        topics = [self.topic("Jayson Tatum responds to Jaylen Brown snub", "Jaylen Brown", "Jayson Tatum"),
                  self.topic("Stephen A. Smith stood down from LeBron James", "LeBron James")]
        for t in topics:
            t["items"] = [{"title": t["headline"], "tier": 1, "link": "https://x", "publisher": "ESPN"}]
        raw = _j.dumps({"ranked": [{"id": 0, "nba": True, "kind": "player_vs_player", "virality": 9, "drama": 9,
                                    "star_power": 9, "debate": 9, "repeat": False, "why": "", "same_as": []},
                                   {"id": 1, "nba": True, "kind": "player_vs_media", "virality": 7, "drama": 7,
                                    "star_power": 7, "debate": 7, "repeat": False, "why": "", "same_as": []}],
                        "shorts": [0, 1], "long": {}})
        saved = e.made_recently
        e.made_recently = lambda: [{**self.MADE[0], "time": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="minutes")}]
        try:
            data = e.parse(raw, 2, topics)
        finally:
            e.made_recently = saved
        self.assertEqual(data["shorts"], [1])
        self.assertTrue(data["ranked"][0]["repeat"])

    def test_rule_told_to_the_editor(self):
        import editor
        self.assertIn("ONE FEUD, ONE SHORT IN 48 HOURS", editor.history_note.__code__.co_consts.__repr__())


class Run43199348111(unittest.TestCase):
    """33. "Ayesha Curry's kiss" (the source: an ON-SCREEN kiss); Charles Bassey's photo twice;
    a painting for Marcus Smart; Google News links in the description."""

    CLAIM = [{"status": "CONFIRMED", "source": 1,
              "text": "Arenas and Nick Young criticized Ayesha Curry's on-screen kiss on the We Said What We Said podcast"}]

    def test_meaning_word(self):
        import compliance as C
        import script
        bad = "Arenas and Steph's old teammate Nick Young picked apart Ayesha Curry's kiss on their podcast."
        good = "Arenas and Steph's old teammate Nick Young picked apart Ayesha Curry's on-screen kiss on their podcast."
        self.assertEqual(len(C.dropped_meaning(self.CLAIM, bad)), 1)
        self.assertEqual(C.dropped_meaning(self.CLAIM, good), [])
        v, notes, _ = C.check_claims(self.CLAIM, [{"title": "x", "tier": 1, "text": "x"}], bad)
        self.assertIn(v, (C.REVIEW, C.REJECT))                      # never PASS
        self.assertTrue(any("changes what happened" in n for n in notes), notes)
        beats = [{"say": bad, "stage": "setup"},
                 {"say": "I think Young was smart, because he kept Steph and left Gil explaining himself.", "stage": "payoff"},
                 {"say": "So who owes Steph the better apology, Arenas or Young?", "stage": "exit"}]
        problems = script.repair_needed("Did Gilbert Arenas really call Ayesha Curry a blemish?", beats, {}, None, self.CLAIM)
        self.assertTrue(any("changes what happened" in p for p in problems), problems)
        self.assertIn("on-screen", script.PROMPT)
        self.assertIn("MEANING WORDS", script.HUMANIZE)

    def test_same_file_two_sources(self):
        from picture_ids import already_shown, mark_shown
        commons = _commons("Charles Bassey San Antonio Spurs 2024.jpg")
        via_ov = {"kind": "photo", "source": "Wikimedia via Openverse", "title": "Charles Bassey San Antonio Spurs 2024",
                  "page": "https://commons.wikimedia.org/w/index.php?curid=1", "url": "https://upload.wikimedia.org/x.jpg"}
        shown = set()
        mark_shown(commons, shown)
        self.assertTrue(already_shown(via_ov, shown))

    def test_full_name_as_one_phrase(self):
        import media
        self.assertFalse(media.names_together("Marcus Smart", "Profile portrait of a smart young man by S. M. Marcus (c.1840)"))
        self.assertTrue(media.names_together("Marcus Smart", "Marcus Smart (51688317634) basketball"))
        self.assertTrue(media.names_together("Shai Gilgeous-Alexander", "Shai Gilgeous-Alexander dunks"))
        self.assertTrue(media.names_together("Stephen Curry", "stephen curry warriors"))

    def test_description_links_the_article(self):
        import inspect
        import script
        self.assertIn("s.get('url') or s['link']", inspect.getsource(script))


class StatedShockHook(unittest.TestCase):
    """34. Owner, 2026-11-12: "Did Gilbert Arenas really call...?" is not shocking enough;
    "Gilbert Arenas called Ayesha Curry the only blemish..." is. The first 3 seconds decide."""

    # his rule 2026-11-14: a hook fits the first 3-4 seconds = 8-12 words (the old fixtures had 13 and 15)
    STATED = "Gilbert Arenas called Ayesha Curry the only blemish on Steph's family."
    ASKED = "Did Gilbert Arenas really call Ayesha Curry the Curry family's blemish?"

    def test_statement_is_a_valid_hook_and_ranks_first(self):
        import script
        self.assertTrue(script.one_question(self.STATED))
        self.assertTrue(script.one_question(self.ASKED))              # a question still works
        self.assertFalse(script.one_question("Arenas. Curry. Blemish."))  # never two sentences
        self.assertGreater(script.nba_hook_score(self.STATED)[1], script.nba_hook_score(self.ASKED)[1])
        self.assertIn("question, not a stated shock", [f for f, _ in script.hook_flaws(self.ASKED)])
        self.assertGreaterEqual(script.nba_hook_score(self.STATED)[1], 40)  # usable: no extra rewrite call
        hooks = [{"text": self.ASKED, "question": True, "score": 50},
                 {"text": self.STATED, "question": True, "score": 41}]
        hooks.sort(key=script.hook_rank)
        self.assertEqual(hooks[0]["text"], self.STATED)

    def test_rules_and_safety(self):
        import script
        p = script.PROMPT
        for need in ("THE HOOK IS A SHOT, NOT A QUESTION", "first 8 words", "Shams: the Lakers",
                     "a question hook only when the story has no shocking fact"):
            self.assertIn(need, p, need)
        self.assertIn("8-12 words", script.HOOK_RETRY if hasattr(script, "HOOK_RETRY") else p)   # his rule 2026-11-14
        self.assertNotIn("8-14 words", p)
        self.assertFalse(script.one_question("Gilbert Arenas just called Ayesha Curry the only blemish on the Curry family."))  # 14: too long now
        self.assertIn("PUNCH:", script.HUMANIZE)
        # audit 2026-11-13: no other line of the prompt may give the hook another length
        self.assertNotIn("10-18 words", p)
        self.assertNotIn("10-24 words", p)
        # a stated rumor without its source is still caught by the rumor check (C2)
        import compliance as C
        cl = [{"status": "RUMOR", "text": "The Lakers are shopping Austin Reaves before the deadline", "source": 1}]
        self.assertTrue(C.bare_claims(cl, "The Lakers are shopping Austin Reaves before the deadline."))
        self.assertFalse(C.bare_claims(cl, "Shams: the Lakers are shopping Austin Reaves before the deadline."))
        # a team name before the colon is a headline, not a source
        self.assertTrue(C.bare_claims(cl, "Lakers: they are shopping Austin Reaves before the deadline."))


class EveryPhotoLookedAt(unittest.TestCase):
    """36. Owner, 2026-11-12: the editor saw 3 of Curry's 94 photos per beat (the first 12 only),
    and 5 White House shots went into an injury Short. Now every photo is tagged once, the tags
    are kept, and each beat gets the photos that fit its line. Offline: Claude and downloads faked."""

    def setUp(self):
        import tempfile
        import photo_tags
        import media
        self.t, self.m = photo_tags, media
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (photo_tags.CACHE, photo_tags.fetch_thumbs, photo_tags._sleep)
        photo_tags.CACHE = self.tmp / "tags.json"
        photo_tags._sleep = lambda s: None

        def thumbs(urls, folder, ua):
            out = []
            for k, u in enumerate(urls):
                p = folder / f"t{k}.jpg"
                self.fake_download(u, p)
                out.append(p)
            return out
        photo_tags.fetch_thumbs = thumbs

    def tearDown(self):
        self.t.CACHE, self.t.fetch_thumbs, self.t._sleep = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ph(self, n, date="2022-02-20", author="Erik Drost"):
        return {"kind": "photo", "page": f"p{n}", "title": f"Steph Curry ({51900000000 + n}).jpg",
                "url": f"https://x/{n}.jpg", "author": author, "date": date}

    def fake_download(self, url, path, timeout=60):
        from PIL import Image
        Image.new("RGB", (500, 400), (int(url.split("/")[-1].split(".")[0]) * 7 % 255, 80, 80)).save(path)
        return True

    def test_parse_keeps_only_known_values(self):
        tags, groups = self.t.parse_tags({"photos": [
            {"n": 1, "v": "C", "s": "game", "e": "sad", "t": "walks off head down"},
            {"n": 2, "v": "a", "s": "made-up", "e": "x", "t": ""},
            {"n": 9, "v": "C"}, {"n": "x"}, {"v": "C"}],
            "same": [[1, 2], [3], ["7", 8, 99]]}, 8)
        self.assertEqual(set(tags), {1, 2})
        self.assertEqual(tags[2]["s"], "other")
        self.assertEqual(groups, [[1, 2], [7, 8]])

    def test_tagged_once_kept_and_same_moment_marked(self):
        pool = [self.ph(n) for n in range(1, 12)]
        calls = []

        def ask(prompt, folder=None, timeout=0, **kw):
            calls.append(sorted(os.listdir(folder)))
            self.assertIn("Steph Curry", prompt)
            return {"photos": [{"n": k, "v": "A" if k == 11 else "C", "s": "game", "e": "calm", "t": "plays"}
                               for k in range(1, 12)], "same": [[2, 3]]}
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        self.assertEqual(n, 11)
        self.assertEqual(calls, [["tags_1.jpg", "tags_2.jpg"]])          # 9 a sheet
        self.assertEqual(pool[1]["moment"], pool[2]["moment"])
        self.assertFalse(self.t.usable(pool[10]))
        fresh = [self.ph(n) for n in range(1, 12)]
        self.assertEqual(self.t.tag_person("Steph Curry", fresh, ask, "ua",
                                           self.m.photo_era, self.m.scene_of), 0)
        self.assertEqual(len(calls), 1)                                   # kept: no second look
        self.assertEqual(fresh[0]["tag"]["s"], "game")
        self.assertEqual(fresh[1]["moment"], fresh[2]["moment"])

    def test_big_pools_are_asked_in_parts_and_a_broken_answer_once_more(self):
        """Preview 43222583073: one call for 120+ photos returned broken JSON and the whole Short
        fell back. Now 45 a call; a broken answer is asked again once, then only that part waits."""
        pool = [self.ph(n) for n in range(1, 101)]
        calls = []

        def ask(prompt, folder=None, timeout=0, **kw):
            calls.append(len(os.listdir(folder)))
            if len(calls) in (2, 4, 5):
                raise ValueError("Expecting ',' delimiter")
            n = len(os.listdir(folder)) and min(45, 100 - 45 * (0 if len(calls) == 1 else 1 if len(calls) == 3 else 2))
            return {"photos": [{"n": k, "v": "C", "s": "game", "e": "calm", "t": "x"} for k in range(1, n + 1)]}
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        # 45 + 45 + 10 photos; part 2 asked twice; the last part failed twice, so its 10 photos get
        # one more look (owner, 2026-11-13), which answers
        self.assertEqual(calls, [5, 5, 5, 2, 2, 2])
        self.assertEqual(n, 100)
        self.assertTrue(all(c.get("tag") for c in pool))

    def test_a_broken_answer_keeps_its_good_entries(self):
        """40. Run 43288011054: one broken spot in a 45-photo answer, twice, lost all 45 tags."""
        broken = ('{"photos":[{"n":1,"v":"C","s":"game","e":"sad","t":"walks off"},\n'
                  '{"n":2,"v":"C","s":"game","e":"calm","t":"holds the "MVP" trophy"},\n'
                  '{"n":3,"v":"A","s":"other","e":"unclear","t":"popcorn"}\n'
                  '{"n":4,"v":"S","s":"bench","e":"calm","t":"sits"}],"same":[[1,4]]}')
        out = self.t.parse_answer(broken)
        self.assertEqual([p["n"] for p in out["photos"]], [1, 3, 4])      # only the broken entry is lost
        self.assertEqual(out["same"], [[1, 4]])
        self.assertEqual(self.t.parse_answer({"photos": []}), {"photos": []})
        with self.assertRaises(ValueError):
            self.t.parse_answer("Sorry, I cannot see the sheets.")
        pool = [self.ph(n) for n in range(1, 5)]
        answers = [broken, '{"photos":[{"n":1,"v":"C","s":"game","e":"smiling","t":"holds the MVP trophy"}]}']
        sheets_seen = []

        def ask(prompt, folder=None, timeout=0, **kw):
            sheets_seen.append(len(os.listdir(folder)))
            return answers.pop(0)
        n = self.t.tag_person("Steph Curry", pool, ask, "ua", self.m.photo_era, self.m.scene_of)
        # owner, 2026-11-13: the photo whose entry broke is looked at again, not left out
        self.assertEqual(n, 4)
        self.assertEqual(sheets_seen, [1, 1])
        self.assertEqual(pool[1]["tag"]["t"], "holds the MVP trophy")
        self.assertTrue(all(c.get("tag") for c in pool))

    def test_untagged_photo_never_fills_when_the_person_has_tags(self):
        m = self.m
        pool = [{**self.ph(1), "title": "Steph Curry golf.jpg"},                       # nobody looked at it
                {**self.ph(2), "title": "Steph Curry game.jpg", "tag": {"v": "C", "s": "game"}, "hoops": True}]
        saved = m.photos
        try:
            m.photos = lambda who: pool
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p2"])
            m.photos = lambda who: [{**self.ph(1), "title": "Steph Curry golf.jpg"}]   # nobody tagged: as before
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p1"])
        finally:
            m.photos = saved

    def test_thumbnails_one_at_a_time_and_stop_on_a_second_429(self):
        import urllib.error
        import urllib.request
        t = self.t
        t.fetch_thumbs = self.saved[1]
        seen, slept = [], []
        t._sleep = slept.append

        class Resp:
            def __init__(self, b): self.b = b
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return self.b

        def fake_open(req, timeout=0):
            seen.append(req.full_url)
            if req.full_url.endswith("/2.jpg"):
                raise urllib.error.HTTPError(req.full_url, 429, "slow down", {"Retry-After": "7"}, None)
            from io import BytesIO
            from PIL import Image
            buf = BytesIO()
            Image.new("RGB", (50, 50)).save(buf, "JPEG")
            return Resp(buf.getvalue())
        saved_open = urllib.request.urlopen
        urllib.request.urlopen = fake_open
        try:
            got = t.fetch_thumbs([f"https://upload.wikimedia.org/{k}.jpg" for k in range(1, 7)], self.tmp, "ua")
        finally:
            urllib.request.urlopen = saved_open
        self.assertEqual([bool(x) for x in got], [True, False, False, False, False, False])
        self.assertEqual(len(seen), 3)                # 1 ok; 2: 429, waited 7 s, 429 again: stop
        self.assertIn(7.0, slept)
        self.assertIn(t.PACE, slept)

    def test_same_moment_is_one_picture(self):
        from picture_ids import already_shown, mark_shown
        a, b = {**self.ph(33), "moment": "p33"}, {**self.ph(34), "moment": "p33"}
        shown = set()
        mark_shown(a, shown, a["page"])
        self.assertTrue(already_shown(b, shown, b["page"]))
        self.assertFalse(already_shown(self.ph(35), shown, "p35"))

    def test_shortlist_reads_tags_and_skips_absent(self):
        curry = [{**self.ph(n), "tag": {"v": v, "s": s, "e": e, "t": t}} for n, (v, s, e, t) in enumerate([
            ("C", "political", "smiling", "with Biden at the White House"),
            ("C", "game", "sad", "walks off head down, Warriors jersey"),
            ("A", "other", "unclear", "popcorn bucket"),
            ("O", "game", "calm", "Jokic shoots")])]
        seen = {}

        def ask(prompt, folder=None, timeout=0, **kw):
            seen["prompt"] = prompt
            return {"beats": [{"beat": 0, "photos": ["a1", "a0", "a2", "zz", "a1"]}, {"beat": "x"}]}
        got = self.t.shortlists([{"say": "Curry left with an abdominal injury."}], [{"person": "Steph Curry"}],
                                ["Steph Curry"], "Curry hurt", {"Steph Curry": curry}, ask,
                                self.m.photo_era, self.m.scene_of)
        self.assertEqual([c["page"] for c in got[0]], ["p1", "p0"])       # absent / unknown ids dropped
        self.assertNotIn("popcorn", seen["prompt"])
        self.assertNotIn("Jokic", seen["prompt"])
        self.assertIn("walks off head down", seen["prompt"])
        self.assertIn('"political"', seen["prompt"])
        self.assertIsNone(self.t.shortlists([{"say": "x"}], [{}], ["Steph Curry"], "s",
                                            {"Steph Curry": curry[2:]}, ask, self.m.photo_era, self.m.scene_of))

    def test_beat_sees_the_shortlist(self):
        m = self.m
        tagged = [{**self.ph(n), "tag": {"v": "C", "s": "game", "e": "calm", "t": "x"}} for n in range(20)]
        untagged = [self.ph(100 + n) for n in range(5)]
        saved = {k: getattr(m, k) for k in ("photos", "download", "image_ok", "commons_videos", "pixabay_videos")}
        try:
            m.photos = lambda who: tagged if who == "Steph Curry" else untagged
            m.download, m.image_ok = self.fake_download, (lambda p: True)
            m.commons_videos = lambda *a, **k: []
            m.pixabay_videos = lambda q: []
            got = m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 0, set(), "Steph Curry",
                               ("Kevin Durant",), tagged[5:13])
            self.assertEqual([c["page"] for c in got], [f"p{n}" for n in range(5, 13)] + ["p100", "p101", "p102"])  # Durant untagged: as before
            old = m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 0, set(), "Steph Curry", (), None)
            self.assertEqual(len(old), m.MAX_PHOTOS)                      # no tags: the old way
        finally:
            for k, v in saved.items():
                setattr(m, k, v)

    def test_round_two_never_brings_back_untagged_first_photos(self):
        """Audit 2026-11-13: round 2 called candidates() without the shortlist, so a tagged
        person's first photos in the old order came back (absent, political...)."""
        m = self.m
        tagged = [{**self.ph(n), "tag": {"v": "C", "s": "game", "e": "calm", "t": "x"}} for n in range(10)]
        saved = {k: getattr(m, k) for k in ("photos", "download", "image_ok", "commons_videos", "pixabay_videos")}
        try:
            m.photos = lambda who: tagged
            m.download, m.image_ok = self.fake_download, (lambda p: True)
            m.commons_videos = lambda *a, **k: []
            m.pixabay_videos = lambda q: []
            self.assertEqual(m.candidates({"person": "Steph Curry", "queries": []}, self.tmp, 100, set(),
                                          "Steph Curry", (), []), [])
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
        import inspect
        src = inspect.getsource(m.collect_for)
        self.assertIn('[] if lists is not None else None)', src[src.index("round 2 adds footage"):])

    def test_big_beats_get_more_sheets(self):
        m = self.m
        from PIL import Image
        cands = []
        for n in range(17):
            p = self.tmp / f"c{n}.jpg"
            Image.new("RGB", (600, 800), "gray").save(p)
            cands.append({"kind": "photo", "thumb": str(p)})
        m.contact_sheet(cands, self.tmp / "beat_3.jpg", "BEAT 3: x")
        names = sorted(x.name for x in self.tmp.glob("beat_3*.jpg"))
        self.assertEqual(names, ["beat_3.jpg", "beat_3_2.jpg"])           # 4 a row, 3 rows a sheet
        with Image.open(self.tmp / "beat_3.jpg") as im:
            self.assertLessEqual(im.height, 1600)
        self.assertIn("beat_0_2.jpg", m.PICK_PROMPT)

    def test_unjudged_top_ups_use_the_tags(self):
        m = self.m
        pool = [{**self.ph(1), "title": "Steph Curry White House.jpg", "tag": {"v": "C", "s": "political"}},
                {**self.ph(6), "title": "Steph Curry Davidson.jpg", "team": "pre-nba"},
                {**self.ph(2), "title": "Steph Curry popcorn.jpg", "tag": {"v": "A", "s": "other"}},
                {**self.ph(3), "title": "Steph Curry stage.jpg", "tag": {"v": "C", "s": "stage"}},
                {**self.ph(4), "title": "Steph Curry far.jpg", "tag": {"v": "S", "s": "game"}, "hoops": True},
                {**self.ph(5), "title": "Steph Curry game.jpg", "tag": {"v": "C", "s": "game"}, "hoops": True}]
        saved = m.photos
        try:
            m.photos = lambda who: pool
            # p4 is only a small figure (v S): not used unjudged since run 43317261723 (D15)
            self.assertEqual([c["page"] for c in m.person_photos("Steph Curry", set())], ["p5"])
        finally:
            m.photos = saved

    def test_rules_in_the_prompts(self):
        m, t = self.m, self.t
        self.assertIn("POLITICAL event", m.PICK_PROMPT)
        self.assertIn("the line is about that very event or that politician", m.PICK_PROMPT)
        for need in ('"A" = he is NOT in it', '"O" = the photo is about SOMEONE ELSE', "THE SAME MOMENT", "Never guess"):
            self.assertIn(need, t.TAG_PROMPT)
        for need in ("WHO first", "Fit the MOMENT", "at most 3 photos with the same sc", '"political"'):
            self.assertIn(need, t.PICK_PROMPT)

    def test_a_failure_falls_back_to_the_first_photos(self):
        m = self.m
        saved = {k: getattr(m, k) for k in ("photos", "people")}
        errors = list(m.MEDIA_ERRORS)
        try:
            m.people = lambda short: ["Steph Curry"]

            def boom(who):
                raise ValueError("Commons down")
            m.photos = boom
            self.assertIsNone(m.shortlist_photos({"headline": "x"}, [{"say": "x"}], [{"person": "Steph Curry"}]))
            self.assertTrue(any("photo tags" in e for e in m.MEDIA_ERRORS))
        finally:
            for k, v in saved.items():
                setattr(m, k, v)
            m.MEDIA_ERRORS[:] = errors


class HookDetailInSourceWords(unittest.TestCase):
    """38. Run 43262308476: the fan's pick "...cussed him out over one radio comment in 2012." lost
    to a weaker hook because the source says "on ESPN 1000's Waddle & Silvy", never "radio". The
    detail is put in the sources' words; the new line must pass the checks again."""

    SRC = [{"title": "Charles Barkley recalls Michael Jordan", "summary": "", "tier": 1, "publisher": "ES",
            "text": "On ESPN 1000's Waddle & Silvy, Barkley said Jordan needed to stop hiring yes-men. "
                    "Jordan didn't take it well. And he is cussing me up and down, that's the last time we spoke."}]
    HOOK = "Charles Barkley says Michael Jordan cussed him out over one radio comment in 2012."

    def run_fix(self, answer):
        import script
        import compliance
        hook = {"text": self.HOOK, "score": 51, "question": True, "intrigue_pick": True,
                "unsupported_details": compliance.unsupported_details(self.HOOK, self.SRC)}
        self.assertEqual(hook["unsupported_details"], ["radio"])
        saved = script.ask_claude
        seen = {}

        def ask(prompt, model=""):
            seen["prompt"], seen["model"] = prompt, model
            if isinstance(answer, Exception):
                raise answer
            return {"text": answer}
        script.ask_claude = ask
        try:
            return script.fix_hook_detail(hook, self.SRC), hook, seen
        finally:
            script.ask_claude = saved

    def test_detail_in_the_sources_words_keeps_the_hook(self):
        import script
        ok, hook, seen = self.run_fix("Charles Barkley says Jordan cussed him out over an ESPN 1000 comment.")
        self.assertTrue(ok)
        self.assertNotIn("radio", hook["text"])
        self.assertEqual(hook["unsupported_details"], [])
        self.assertEqual(hook["detail_fixed"], ["radio"])
        self.assertTrue(hook["intrigue_pick"])
        self.assertIn("radio", seen["prompt"])
        self.assertIn("Waddle & Silvy", seen["prompt"])
        self.assertEqual(seen["model"], script.CLAUDE_MODEL_LIGHT)

    def test_a_bad_rewrite_changes_nothing(self):
        for answer in ("Charles Barkley says Jordan cussed him out on the radio in 2012.",   # still radio
                       "Barkley. Jordan. Cussed out.",                                      # not one line
                       ValueError("broken JSON")):
            ok, hook, _ = self.run_fix(answer)
            self.assertFalse(ok)
            self.assertEqual(hook["text"], self.HOOK)
            self.assertEqual(hook["unsupported_details"], ["radio"])

    def test_wired_in_before_the_hook_order(self):
        import inspect
        import script
        src = inspect.getsource(script.build_short)
        # (audit 2026-11-13: the ordering moved into truth_order, still after the detail fix)
        self.assertLess(src.index("fix_hook_detail(hooks[0], sources, lead)"), src.index("truth_order(hooks, sources, lead, draft.get(\"claims\"))"))   # D27: + lead; D95: + claims


class WhereTheFeudStandsNow(unittest.TestCase):
    """39 (D13). Run 43262308476: "they stopped talking ... still no update on a reunion", while the
    source said Vince Coleman got them talking and Barkley planned golf with Jordan."""

    SRC = [{"title": "Charles Barkley recalls Michael Jordan", "summary": "",
            "text": "Jordan didn't take it well. It stayed that way for more than a decade. The man who reunited "
                    "them was former St. Louis Cardinals outfielder Vince Coleman. While golfing with Jordan at "
                    "The Grove, Coleman called Barkley and told them it was time to talk. There has been no update "
                    "on it yet."}]
    SPOKEN = ("Barkley says Jordan cussed him out, and they stopped talking. He later called the silence "
              "stubborn, and there's still no update on a reunion. So who should've picked up the phone first?")

    def test_silence_while_a_source_tells_of_contact(self):
        import compliance as C
        self.assertIn("reunited", C.missed_turn(self.SPOKEN, self.SRC))
        fixed = self.SPOKEN.replace("there's still no update on a reunion",
                                    "Vince Coleman finally got them talking again")
        self.assertEqual(C.missed_turn(fixed, self.SRC), "")
        # a turn about other people (no name the Short says nearby) is not this feud's turn
        other = [{"title": "", "summary": "", "text": "Nick Young apologized to Ayesha Curry on his podcast."}]
        self.assertEqual(C.missed_turn(self.SPOKEN, other), "")
        # no silence in the Short: nothing to check
        self.assertEqual(C.missed_turn("Barkley and Jordan were Dream Team teammates.", self.SRC), "")

    def test_repair_then_gate(self):
        import compliance as C
        import script
        beats = [{"say": s} for s in compliance_split(self.SPOKEN)]
        problems = script.repair_needed("Charles Barkley says Michael Jordan cussed him out.", beats,
                                        {"stages": [], "hard": [], "soft": []}, self.SRC, [])
        self.assertTrue(any("contact since" in p for p in problems))
        verdict, notes, _ = C.check_claims([{"text": "Barkley says Jordan cussed him out", "status": "CONFIRMED",
                                             "source": 1}], self.SRC, self.SPOKEN)
        self.assertEqual(verdict, C.REVIEW)
        self.assertTrue(any("contact since" in n for n in notes))
        self.assertIn("where a feud or a friendship stands NOW", script.PROMPT)


def compliance_split(text):
    import compliance
    return compliance.split_sentences(text)


class NoReplayNoDanglingReference(unittest.TestCase):
    """41 (D14). Run 43288011054: the hook "Alperen Sengun tangled with Steph Curry, and Curry now
    has a torn oblique." was followed by "Curry tangled with Alperen Sengun, ...", and the closing
    question asked about "that stretch", a schedule the Short never said."""

    HOOK = "Alperen Sengun tangled with Steph Curry, and Curry now has a torn oblique."
    BEATS = [{"say": "Curry tangled with Alperen Sengun, grabbed his side, and was done after six minutes."},
             {"say": "Steve Kerr said concern is high."},
             {"say": "So do the Warriors survive that stretch without him, or was the run just Curry?"}]

    def test_reworded_replay_is_caught(self):
        import script
        self.assertEqual(script.hook_repeats(self.HOOK, self.BEATS), [0])
        # the past Shorts that only continue the hook are left alone
        self.assertEqual(script.hook_repeats(
            "Did Dillon Brooks just troll LeBron James with a King Blocker, then lose his opener by 41?",
            [{"say": "Brooks did a Kalshi ad for the King Blocker 9000, a gadget that mutes LeBron."}, {"say": "x"}]), [])
        self.assertEqual(script.hook_repeats(
            "Will the Bucks get the same hammer the Clippers got, now that Gary Trent Jr. is under investigation?",
            [{"say": "The NBA is investigating the Bucks over Gary Trent Jr.'s 64 million contract."}, {"say": "x"}]), [])
        # the closing question may come back to the hook's words
        self.assertEqual(script.hook_repeats(self.HOOK, self.BEATS[1:] + [
            {"say": "So Curry tangled with Alperen Sengun, but do the Warriors survive without him?"}]), [])

    def test_closing_question_points_to_something_said(self):
        import script
        self.assertEqual(script.dangling_refs(self.HOOK, self.BEATS), ["that stretch"])
        said = self.BEATS[:2] + [{"say": "Next comes a stretch of Spurs, Mavericks and Pelicans, back to back."},
                                 self.BEATS[2]]
        self.assertEqual(script.dangling_refs(self.HOOK, said), [])
        self.assertEqual(script.dangling_refs(self.HOOK, [{"say": "So who's winning this feud?"}]), [])
        problems = script.repair_needed(self.HOOK, self.BEATS, {"stages": [], "hard": [], "soft": []})
        self.assertTrue(any("that stretch" in p for p in problems))
        self.assertTrue(any("beat 1 repeats the hook" in p for p in problems))


class FreshFightBeatsOldFeud(unittest.TestCase):
    """42. Owner, 2026-11-13: Dejounte Murray's deleted "inside sabotage" tweet (59.5, rising +2
    outlets) was skipped three runs in a row while old feuds filled the runs."""

    # the real record of run 43317261723 (59.5)
    MURRAY = {"id": 6, "nba": True, "kind": "player_vs_team", "conflict": True, "virality": 7, "drama": 8,
              "star_power": 5, "debate": 7, "repeat": False, "search_hits": 0, "youtube_heat": 0,
              "google_trend": 0, "momentum": 2, "reddit": 0.0, "star_fame": 0.0, "hours_old": 0.8}

    def test_near_miss(self):
        import editor as E
        topic = {"verified": True, "outlets": 4}
        r = dict(self.MURRAY)
        self.assertEqual(E.short_score(r), 59.5)
        self.assertTrue(E.near_miss(r, topic))
        calm = {**r, "conflict": False, "virality": 10, "debate": 10}            # in range, but no fight
        self.assertTrue(E.NEAR_SCORE <= E.short_score(calm) < E.MIN_SCORE)
        self.assertFalse(E.near_miss(calm, topic))
        self.assertFalse(E.near_miss({**r, "drama": 6}, topic))                 # not dramatic enough
        self.assertFalse(E.near_miss({**r, "repeat": True}, topic))             # already made
        self.assertFalse(E.near_miss({**r, "momentum": 0}, {"verified": True, "outlets": 2}))  # not spreading
        self.assertTrue(E.near_miss({**r, "momentum": 0}, {"verified": True, "outlets": 3}))
        self.assertFalse(E.near_miss({**r, "kind": "filler"}, topic))

    def test_made_before_the_old_feuds(self):
        import inspect
        import script
        src = inspect.getsource(script.main)
        self.assertLess(src.index("queue += near"), src.index("for topic_id in queue:"))
        self.assertLess(src.index("for topic_id in queue:"), src.index("fill_with_evergreen(shorts"))


class BoldButTrue(unittest.TestCase):
    """43 (D17). Owner, 2026-11-13: every hook hyped and scandalous, at the edge of the truth, never
    past it. Run 43317261723: "Draymond Green says nobody owes Luka Doncic respect until they've
    played him." when he said "You earn respect"."""

    SRC = [{"title": "Draymond Green uses Kevin Durant lesson to defend Warriors rookie vs Luka Doncic",
            "summary": "", "tier": 1, "publisher": "BasketNews",
            "text": "Green said Lendeborg should keep talking to Doncic. 'You earn respect,' Green said. "
                    "Doncic finished with 28 points in the 127 to 105 Lakers win."}]
    HOOK = "Draymond Green says nobody owes Luka Doncic respect until they've played him."

    def run_check(self, answer):
        import script
        hook = {"text": self.HOOK, "score": 45, "question": True}
        saved = script.ask_claude
        seen = {}

        def ask(prompt, model=""):
            seen["prompt"], seen["model"] = prompt, model
            if isinstance(answer, Exception):
                raise answer
            return answer
        script.ask_claude = ask
        try:
            return script.check_hook_truth(hook, self.SRC), hook, seen
        finally:
            script.ask_claude = saved

    def test_ok_keeps_the_bold_line(self):
        res, hook, seen = self.run_check({"verdict": "ok"})
        self.assertEqual((res, hook["text"]), ("ok", self.HOOK))
        self.assertIn("NOT overstated: keep them", seen["prompt"])
        self.assertEqual(seen["model"], "")                         # the main model judges

    def test_overstated_gets_the_bold_true_line(self):
        res, hook, _ = self.run_check({"verdict": "overstated", "why": "stronger than he said",
                                       "text": "Draymond Green told a rookie to make Luka Doncic earn respect."})
        self.assertEqual(res, "fixed")
        self.assertEqual(hook["text"], "Draymond Green told a rookie to make Luka Doncic earn respect.")
        self.assertEqual(hook["truth_fixed"], "stronger than he said")
        self.assertFalse(hook.get("overstated"))

    def test_a_bad_rewrite_steps_behind(self):
        for text in ("Draymond Green just told a rookie to make Luka Doncic earn it after 41 points.",  # 41 invented
                     "Draymond. Luka. Respect.", ""):
            res, hook, _ = self.run_check({"verdict": "overstated", "why": "x", "text": text})
            self.assertEqual(res, "overstated")
            self.assertEqual(hook["text"], self.HOOK)
            self.assertTrue(hook["overstated"])
        hooks = [{"text": "a", "unsupported_details": [], "overstated": "x"}, {"text": "b", "unsupported_details": []}]
        hooks.sort(key=lambda h: (bool(h["unsupported_details"]), bool(h.get("recycled")), bool(h.get("overstated"))))
        self.assertEqual(hooks[0]["text"], "b")

    def test_a_failed_check_steps_behind(self):
        # changed by D83 (his answer 2026-11-19): it was "skipped" and the hook kept its place, so an
        # unread hook could lead (classfix eval: 14 such); now it steps behind like an overstated one
        res, hook, _ = self.run_check(ValueError("broken JSON"))
        self.assertEqual((res, hook["text"]), ("overstated", self.HOOK))
        self.assertEqual(hook.get("overstated"), "the truth check could not read it")

    def test_rule_in_the_prompt_and_wired(self):
        import inspect
        import script
        self.assertIn("BOLD BUT TRUE", script.PROMPT)
        self.assertIn("never past it", script.PROMPT)
        src = inspect.getsource(script.build_short)
        self.assertIn("truth_order(hooks, sources, lead, draft.get(\"claims\"))", src)   # D27: + the lead person; D95: + claims

    def test_an_overstated_leading_hook_holds_the_short(self):
        """Audit 2026-11-13: if every checked hook stayed overstated, the Short is held (REVIEW)."""
        import inspect
        import script
        src = inspect.getsource(script.build_short)
        hold = src.index('if hooks and hooks[0].get("overstated"):')
        self.assertIn('retention["hard"].append(f"the hook says more than the sources', src[hold:hold + 200])
        self.assertLess(hold, src.index('"ready": bool(hooks)'))
        self.assertIn('not retention["hard"]', src[src.index('"ready": bool(hooks)'):][:200])

    def test_the_next_hook_is_read_too_when_the_first_was_overstated(self):
        """Audit 2026-11-13: the hook that takes an overstated one's place is read as well."""
        import script
        saved = script.ask_claude
        read = []

        def ask(prompt, model=""):
            line = prompt.split("THE LINE (untrusted script text): ")[1].split("\n")[0]
            read.append(line)
            return {"verdict": "overstated", "why": "x", "text": ""} if line.startswith("A ") else {"verdict": "ok"}
        script.ask_claude = ask
        try:
            hooks = [{"text": "A Draymond Green says nobody owes Luka Doncic respect.", "unsupported_details": []},
                     {"text": "B Draymond Green just told a rookie to make Luka earn it.", "unsupported_details": []},
                     {"text": "C third", "unsupported_details": []}]
            script.truth_order(hooks, self.SRC)
            self.assertEqual([h["text"][0] for h in hooks], ["B", "C", "A"])
            self.assertEqual([x[0] for x in read], ["A", "B"])          # B read once, C never
            read.clear()
            hooks = [{"text": "B fine", "unsupported_details": []}, {"text": "C", "unsupported_details": []}]
            script.truth_order(hooks, self.SRC)
            self.assertEqual([x[0] for x in read], ["B"])               # a good first hook: one call only
        finally:
            script.ask_claude = saved


class OneEventTheRightEra(unittest.TestCase):
    """44 (D10, D15). The Curry preview: 7 of 13 photos from the 2022 All-Star weekend (two days,
    several photographers). Run 43317261723: Shaq in Suns colours for "traded to Miami in 2004",
    Lendeborg in Michigan colours as "Warriors rookie", a crowd where Green is tiny."""

    def test_one_event_counts_across_photographers_and_days(self):
        from collections import Counter
        import media as m
        allstar = [{"kind": "photo", "page": f"p{k}", "author": a, "date": d, "title": f"Curry {k}.jpg",
                    "tag": {"v": "C", "s": "allstar"}}
                   for k, (a, d) in enumerate([("Erik Drost", "2022-02-19"), ("Erik Drost", "2022-02-20"),
                                               ("All-Pro Reels", "2022-02-20"), ("Keith Allison", "2022-02-18")])]
        self.assertEqual(m.event_of(allstar[0]), ("event", "allstar", "2022"))
        self.assertEqual(len({m.scene_of(c) for c in allstar}), 4)            # four scenes, one event
        scenes = Counter()
        for c in allstar[:3]:
            self.assertFalse(m.scene_full(c, scenes))
            m.count_scene(c, scenes)
        self.assertTrue(m.scene_full(allstar[3], scenes))                     # the 4th waits (last resort)
        self.assertEqual(m.spread_scenes([0, 1], [allstar[3], {"kind": "photo", "page": "x", "title": "y"}],
                                         lambda j: 3, {0: 9, 1: 5}, scenes), [1, 0])
        game = {**allstar[0], "tag": {"v": "C", "s": "game"}}
        self.assertIsNone(m.event_of(game))                                   # games stay per scene
        self.assertIsNone(m.event_of({**allstar[0], "date": "", "title": "Curry.jpg"}))   # no year: no event

    def test_a_college_photo_is_marked_pre_nba(self):
        import photo_tags
        c = {"page": "p1"}
        photo_tags._apply(c, {"v": "C", "s": "pre_nba", "e": "calm", "t": "defends, Michigan"})
        self.assertEqual(c["team"], "pre-nba")
        d = {"page": "p2", "team": "former"}
        photo_tags._apply(d, {"v": "C", "s": "pre_nba"})
        self.assertEqual(d["team"], "former")                                 # team data wins

    def test_rules_in_the_prompts(self):
        import media
        import photo_tags
        for need in ("A SMALL FIGURE", "THE LINE'S TIME AND TEAM", "Suns jersey"):
            self.assertIn(need, media.PICK_PROMPT)
        self.assertIn("THE LINE'S TIME AND TEAM", photo_tags.PICK_PROMPT)
        self.assertIn("a small figure (v S) only when no clear photo", photo_tags.PICK_PROMPT)
        self.assertIn("the team on his jersey", photo_tags.TAG_PROMPT)
        self.assertFalse(photo_tags.fill_ok({"tag": {"v": "S", "s": "game"}}))


class PrivateReportsStayPrivate(unittest.TestCase):
    """45 (audit, 2026-11-13). This repository is public, and so are its Actions logs and run
    summaries. The owner's decision (2026-11-11): the full report is private. Every stage still
    PRINTED its full report into the public log, and the weekly / benchmark runs wrote the
    stories, signals and the competitor scan into the public run summary."""

    STAGES = ("collect", "editor", "media", "render", "script", "signals", "budget", "benchmark")

    def test_stages_print_the_report_only_by_hand(self):
        import re
        for name in self.STAGES:
            src = (ROOT / "src" / f"{name}.py").read_text(encoding="utf-8")
            prints = [m.start() for m in re.finditer(r"\n\s*print\(text\)", src)]
            self.assertTrue(prints, name)
            for at in prints:
                self.assertIn('if not os.environ.get("GITHUB_STEP_SUMMARY"):', src[max(0, at - 120):at], name)

    def test_weekly_and_benchmark_keep_their_summary_private(self):
        for wf, steps in (("weekly.yml", ("python src/collect.py", "python src/benchmark.py")),
                          ("benchmark.yml", ("python src/benchmark.py",))):
            text = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            for step in steps:
                before = text[:text.index(step)]
                self.assertIn('export GITHUB_STEP_SUMMARY="$RUNNER_TEMP/private_summary.md"',
                              before[before.rfind("run: |"):], f"{wf}: {step}")


class OneSentenceSplitEverywhere(unittest.TestCase):
    """46 (audit, 2026-11-13). The script checks stopped splitting sentences after initials
    ("Stephen A. Smith", "Gary Trent Jr."), but the captions and the voice still did; and
    Pillow 14 drops Image.getdata (D12)."""

    def test_captions_keep_the_name_after_an_initial(self):
        import render
        self.assertIn("smith", render.key_words([{"say": "Stephen A. Smith ripped him. Smith said no."}]))

    def test_voice_parts_never_end_after_an_initial(self):
        import tts
        cls = next(v for v in vars(tts).values() if isinstance(v, type) and hasattr(v, "chunks"))
        words = ("He said it again and again on the air. " * 9 + "Then Stephen A. Smith ripped him on live TV "
                 "for the whole country to hear. " + "Nobody in the building said a single word about it. " * 6)
        for part in cls.chunks(None, words):
            self.assertFalse(part.rstrip().endswith(" A."), part[-30:])

    def test_picture_hash_is_the_same_with_the_new_pillow_call(self):
        import tempfile
        from PIL import Image
        import media
        import render
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.jpg"
            Image.radial_gradient("L").convert("RGB").save(p)
            with Image.open(p) as im:
                g = im.convert("L").resize((9, 8), Image.LANCZOS)
            px = list(getattr(g, "get_flattened_data", g.getdata)())
            old = sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
            self.assertEqual(media.picture_hash(p), old)
            self.assertEqual(render.picture_hash(p), old)
        for name in ("media", "render"):
            self.assertNotIn("list(g.getdata())", (ROOT / "src" / f"{name}.py").read_text(encoding="utf-8"))



class NotTheOtherThomas(unittest.TestCase):
    """47 (run 43353547001). Isiah Thomas's Commons pool held two Flickr photos titled
    "Isaiah Thomas (50639077836).jpg": the Wizards #4, not the Pistons legend. Both play
    basketball, so the photo tagger called them him (match 8 and 7) and they were shown for
    "hands in 1991". A first name with the same first letter that is not his (nor a short form
    or nickname of it) next to his surname = another man. Two players in one title are not."""

    def setUp(self):
        import media
        self.m = media

    def test_the_other_man_is_left_out(self):
        f = self.m.look_alike_name
        self.assertTrue(f("Isiah Thomas", "Isaiah Thomas (50639077836).jpg"))
        self.assertTrue(f("Isaiah Thomas", "Isiah_Thomas_1989.jpg"))
        self.assertTrue(f("Stephen Curry", "Seth Curry 2019.jpg"))
        self.assertTrue(f("Stephen Curry", "Seth Curry.jpg"))            # the ".jpg" is not part of the name
        self.assertTrue(f("Derek Fisher", "David_fisher_and_tex_winter_(3215053324).jpg"))

    def test_his_own_name_and_other_players_are_kept(self):
        f = self.m.look_alike_name
        for person, title in [("Isiah Thomas", "Isiah Thomas 1989.jpg"), ("Stephen Curry", "Steph Curry.jpg"),
                              ("Stephen Curry", "Stephen Curry and Seth Curry.jpg"),
                              ("Michael Brown", "Mike Brown coach.jpg"), ("Shaq O'Neal", "Shaquille O'Neal.jpg"),
                              ("Kevin Durant", "Harden_Durant_2013_playoffs.jpg"),
                              ("Kevin Durant", "Iguodala,_Calderon,_Durant,_Westbrook_in_Barcelona.jpg"),
                              ("Stephen Curry", "Seth Curry guards his brother Stephen.jpg"),
                              ("Jalen Brunson", "Rick Brunson embraces Jalen after the game.jpg"),
                              ("Marcus Smart", "Isaiah Thomas, Marcus Smart (34075954590).jpg"),
                              ("LeBron", "LeBron James.jpg")]:
            self.assertFalse(f(person, title), title)

    def test_the_pool_never_holds_him(self):
        m = self.m
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Isiah Thomas Pistons 1989.jpg"},
                {"page": "b", "score": 20, "title": "Isaiah Thomas (50639077836).jpg"}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = lambda person: []
            m.openverse_photos = lambda person: [{"page": "c", "score": 25, "title": "Isaiah Thomas (50639144552).jpg"}]
            self.assertEqual([p["page"] for p in m.photos("Isiah Thomas")], ["a"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])



class OnlyTheQuote(unittest.TestCase):
    """48 (run 43395656602). Yahoo's article held a tweet glued to its quote: 'hurt Luka
    Doncic:"Not a good play right there. That's not cool man, not letting guys land"When will'.
    The quote correction took 'hurt Luka Doncic:Not a good play right there. That's not' and
    the Short said it as Barkley's words (gate PASS). The article's own form, '"...right there,"
    said Barkley. "Not letting...', gave "...right there, said Barkley." inside the quote."""

    TWEET = ("Charles Barkley just called out Kyle Kuzma for his dirty play that hurt Luka Doncic:\"Not a good "
             "play right there. That's not cool man, not letting guys land\"When will the NBA finally stop "
             "these guys from their dirty hits on Luka Doncic? First time he's gotten this call.")
    ARTICLE = ("While showing highlights Charles Barkley called out Kuzma in passing. \"That's not a good play "
               "right there,\" said Barkley. \"Not letting guys land. That's not cool at all.\" Then it went on.")

    def fix(self, text, quote):
        import script
        b = [{"say": f'Barkley said on Inside the NBA, "{quote}"'}]
        script.soften_quotes(b, [{"title": "Barkley calls out Kuzma", "summary": "", "text": text}])
        return b[0]["say"]

    def test_the_glued_tweet(self):
        said = self.fix(self.TWEET, "That's not a good play right there. Not letting guys land.")
        self.assertEqual(said, 'Barkley said on Inside the NBA, "Not a good play right there. '
                               'That\'s not cool man, not letting guys land"')

    def test_said_barkley_is_not_his_words(self):
        said = self.fix(self.ARTICLE, "That's not a good play right there. Not letting guys land.")
        self.assertNotIn("said Barkley", said.split('"')[1])
        self.assertIn('"That\'s not a good play right there"', said)

    def test_a_cut_off_source_is_never_the_quote(self):
        said = self.fix('Barkley on Kuzma: "Not a good play right there. That\'s not\u2026 https://t.co/x',
                        "That's not a good play right there. Not letting guys land.")
        self.assertNotIn("That's not\"", said)
        self.assertNotIn("Kuzma:", said)

    def test_the_record_survives_the_repair(self):
        import inspect, script
        self.assertIn("softened + cand_soft", inspect.getsource(script))



class FinalLaws(unittest.TestCase):
    """49 (owner, 2026-11-13: fix the kind of mistake, not the one case). The checks asked "are
    these words in the source?" and "does this look like him?"; both said yes to Barkley's
    broken quote and to Isaiah Thomas in a Wizards jersey. These laws read the finished result."""

    SRC = [{"title": "Barkley calls out Kuzma", "summary": "",
            "text": "While showing highlights Charles Barkley called out Kuzma for the play that hurt Luka "
                    "Doncic. \"That's not a good play right there,\" said Barkley. \"Not letting guys land. "
                    "That's not cool at all.\" Kuzma starts for the 1-11 Bucks."}]

    def test_a_quote_must_be_someones_own_words(self):
        import script
        ok = 'Barkley said, "That\'s not a good play right there. Not letting guys land."'
        self.assertEqual(script.quotes_outside_marks(ok, self.SRC), [])        # broken by "said Barkley": still his
        narration = 'Barkley said, "the play that hurt Luka Doncic was not a good play."'
        self.assertTrue(script.quotes_outside_marks(narration, self.SRC))      # the article's words, not his
        self.assertEqual(script.quotes_outside_marks("Kuzma's closeout hurt Luka.", self.SRC), [])
        head = [{"title": "\u2018I Love Random NBA Beefs,\u2019 Fans Divided", "summary": "", "text": ""}]
        self.assertEqual(script.quotes_outside_marks('Fans said "I love random NBA beefs."', head), [])

    def test_broken_text_is_caught(self):
        import script
        self.assertTrue(script.BROKEN_TEXT.search("Barkley said, hurt Luka Doncic:Not a good play"))
        self.assertTrue(script.BROKEN_TEXT.search('not letting guys land"When will'))
        for fine in ("At 3:30 on Friday.", 'He said "no." Then left.', "Luka's ankle, the Lakers' bench."):
            self.assertIsNone(script.BROKEN_TEXT.search(fine), fine)

    def test_the_laws_hold_the_short(self):
        import inspect, script
        src = inspect.getsource(script)
        self.assertIn("quotes_outside_marks(spoken, sources)", src)
        self.assertIn("broken = BROKEN_TEXT.search(spoken)", src)
        self.assertIn('retention["hard"].append(f\'broken text', src)

    def test_his_jersey_his_teams(self):
        import media, compliance as C
        j = media.jersey_team
        self.assertEqual(j({"s": "game", "t": "dribbles in Wizards jersey"}), "washington wizards")
        self.assertEqual(j({"s": "game", "t": "shoots a three, Suns"}), "phoenix suns")
        self.assertEqual(j({"s": "game", "t": "dribbles past Cavaliers defender"}), "")      # the opponent
        self.assertEqual(j({"s": "game", "t": "goes up to score against Thunder, Wizards"}), "washington wizards")
        self.assertEqual(j({"s": "bench", "t": "stands on sideline, Warriors"}), "")          # a coach
        self.assertFalse(C.jersey_ok("washington wizards", ["detroit pistons"]))
        self.assertTrue(C.jersey_ok("washington wizards", []))                               # career unknown
        self.assertTrue(C.jersey_ok("charlotte hornets", ["new orleans pelicans"]))         # the old Hornets
        self.assertTrue(C.jersey_ok("", ["detroit pistons"]))

    def test_media_leaves_him_out_and_the_gate_holds(self):
        import media, gate
        m = media
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos),
                 m.photo_tags.tag_person, m.photo_tags.shortlists, m.career_teams)
        import wiki_http

        def offline(*a, **k):
            raise OSError("tests never reach the network")
        # 2026-11-17: this test reached Wikipedia for real (a 429 then spent the waiting budget the
        # WikimediaPolite tests need, so they failed by turns); tests are offline (header above)
        real_fetch, wiki_http.fetch = wiki_http.fetch, offline
        self.addCleanup(setattr, wiki_http, "fetch", real_fetch)
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Isiah Thomas 1989.jpg", "tag": {"v": "C", "s": "game", "t": "drives, Pistons"}},
                {"page": "b", "score": 20, "title": "IT 2021.jpg", "tag": {"v": "C", "s": "game", "t": "dribbles in Wizards jersey"}}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            m.photo_tags.tag_person = lambda *a, **k: 0
            m.photo_tags.shortlists = lambda *a, **k: None
            m.career_teams = lambda person: {"detroit pistons"}
            m.shortlist_photos({"headline": "Isiah Thomas on Jordan", "_name": "t"}, [{"say": "x"}],
                               [{"person": "Isiah Thomas"}])
            self.assertEqual([p["page"] for p in m.photos("Isiah Thomas")], ["a"])
        finally:
            (m.commons_photos, m.flickr_photos, m.openverse_photos) = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])
            m.photo_tags.tag_person, m.photo_tags.shortlists, m.career_teams = saved[4:]
        shown = [{"kind": "photo", "person": "Isiah Thomas", "jersey": "washington wizards", "title": "IT.jpg",
                  "license": "CC BY 2.0", "page": "p", "author": "x", "match": 8}]
        v, notes = gate.check_visuals(shown, {"careers": {"Isiah Thomas": ["detroit pistons"]}})
        self.assertEqual(v, "REVIEW")
        self.assertIn("never played for", " ".join(notes))
        shown[0]["jersey"] = "detroit pistons"
        self.assertEqual(gate.check_visuals(shown, {"careers": {"Isiah Thomas": ["detroit pistons"]}})[0], "PASS")



class ReplayOnRealRuns(unittest.TestCase):
    """50 (owner, 2026-11-13). Checking a change on real runs needed the articles again; some were
    gone or behind a paywall (The Athletic). The texts each Short was checked against are kept
    with the run, and replay.py tries today's checks on every kept run."""

    def test_sources_are_kept_with_the_run(self):
        import script, state, tempfile
        self.assertIn("sources/short_*.json", state.RUN_FILES)
        old = script.SOURCES_OUT
        with tempfile.TemporaryDirectory() as d:
            try:
                script.SOURCES_OUT = Path(d)
                script.keep_sources(2, [{"publisher": "Yahoo", "title": "t", "text": "body", "link": "u", "extra": 1}])
                kept = json.loads((Path(d) / "short_2.json").read_text(encoding="utf-8"))
            finally:
                script.SOURCES_OUT = old
        self.assertEqual(kept[0]["text"], "body")
        self.assertNotIn("extra", kept[0])
        import inspect
        self.assertIn("keep_sources(n, sources)", inspect.getsource(script.build_short))

    def test_replay_finds_what_the_run_missed(self):
        import replay, tarfile, tempfile, io
        from unittest.mock import patch
        short = {"gate": "PASS", "hook": {"text": "Barkley called out Kuzma."},
                 "beats": [{"say": 'Barkley said, "the play that hurt Luka Doncic was bad."'},
                           {"say": "Then hurt Luka Doncic:Not a good play."}],
                 "unsupported_numbers": [], "unsupported_quotes": []}
        sources = [{"title": "Barkley calls out Kuzma", "summary": "", "text": "Barkley called out Kuzma for the "
                    "play that hurt Luka Doncic was bad. \"Not letting guys land,\" he said."}]
        with tempfile.TemporaryDirectory() as d:
            with tarfile.open(Path(d) / "2026-11-13_1.tar.gz", "w:gz") as tar:
                for name, obj in (("scripts/short_1.json", short), ("sources/short_1.json", sources)):
                    raw = json.dumps(obj).encode()
                    info = tarfile.TarInfo(name)
                    info.size = len(raw)
                    tar.addfile(info, io.BytesIO(raw))
            out = io.StringIO()
            with patch("sys.stdout", out):
                n = replay.replay(Path(d))
        self.assertEqual(n, 1)
        self.assertIn("broken text", out.getvalue())
        self.assertIn("not inside quote marks", out.getvalue())



class TheNewsInTheHook(unittest.TestCase):
    """51 (run 43353547001). "Smart suspended three games" opened with "Marcus Smart punched
    Charles Bassey, and the Rockets' next opponents are all below .500": yesterday's punch (we had
    made that Short) and a schedule detail, while two lines said "the NBA suspended Smart"."""

    HEAD = "Rockets' Marcus Smart suspended three games for punching Warriors' Charles Bassey"

    def hooks(self):
        return [{"text": "Marcus Smart punched Charles Bassey, and the Rockets' next opponents are all below .500.",
                 "question": True, "score": 52},
                {"text": "Charles Bassey just called Marcus Smart's punch fake toughness, and the NBA suspended Smart.",
                 "question": True, "score": 43},
                {"text": "The NBA just suspended Marcus Smart for punching Charles Bassey in the face.",
                 "question": True, "score": 43}]

    def test_the_news_is_said(self):
        import script
        f = script.says_the_news
        self.assertFalse(f(self.hooks()[0]["text"], self.HEAD))
        self.assertTrue(f(self.hooks()[2]["text"], self.HEAD))
        self.assertTrue(f("Curry now has a torn oblique.", "Stephen Curry injury: out two weeks with oblique tear"))
        for head in ("Lakers show signs of life", "Rudy Gobert fired back at Kuminga", "Luka is fine, per Shams",
                     "Warriors on a tear", "Kuminga rips Gobert after loss"):
            self.assertTrue(f("Anything at all.", head), head)                  # no news event: nothing to check

    def test_the_fan_pick_decides_not_the_news(self):
        # his rule (2026-11-14): the hook must be scandalous, intriguing and effective; the day's news
        # is secondary. The "a line with the news always wins" order was mine and is gone: every good
        # line goes to the fan's pick, and its choice leads.
        import script
        with patch.object(script, "ask_claude", return_value={"best": 1}) as ask:
            got = script.intrigue_pick(self.hooks(), self.HEAD, "story")
        self.assertIn("below .500", ask.call_args[0][0].split("WHAT THE SHORT SAYS")[1])   # offered too
        self.assertEqual(got[0]["text"], self.hooks()[0]["text"])
        self.assertTrue(got[0]["intrigue_pick"])

    def test_no_news_line_changes_nothing(self):
        import script
        hooks = [h for h in self.hooks()[:1]] + [{"text": "Smart and Bassey went at it again.", "question": True, "score": 45}]
        with patch.object(script, "ask_claude", return_value={"best": 1}):
            got = script.intrigue_pick(hooks, self.HEAD, "story")
        self.assertEqual(got[0]["text"], hooks[0]["text"])



class AQuestionIsNoAnswer(unittest.TestCase):
    """52 (run 43395656602). The payoff "Why was Luka even back in up 20? I'd blame that." passed
    as an answer (10 words). It is a question and a 3-word scrap (blame what? whom?)."""

    def test_question_payoff_is_weak(self):
        import script
        bad = [{"say": "Why was Luka even back in up 20? I'd blame that.", "stage": "payoff"}]
        self.assertTrue(script.weak_payoff(bad))
        self.assertTrue(script.weak_payoff([{"say": "So was it dirty, or just a bad landing for Luka?", "stage": "payoff"}]))
        good = [{"say": "Why was Luka even in? Redick left him out there up 20, and that is on him.", "stage": "payoff"}]
        self.assertFalse(script.weak_payoff(good))
        self.assertFalse(script.weak_payoff([{"say": "Doc was half right and fully clumsy.", "stage": "payoff"}]))
        problems = script.repair_needed("Barkley called out Kuzma.", bad + [{"say": "So was Kuzma dirty, Barkley?", "stage": "exit"}],
                                        {"hard": [], "soft": []})
        self.assertTrue(any("or a question" in p for p in problems))



class IndependentFinalRead(unittest.TestCase):
    """53 (owner, 2026-11-13). A fresh Claude reads the finished Short like a viewer, with the
    picture under every line and the sources. It must quote real evidence: an invented reason
    can never hold a good Short, and a Short it could not read is never published unread."""

    SHORT = {"hook": {"text": "Charles Barkley calls out Kyle Kuzma on live TV."},
             "beats": [{"say": 'Barkley said, "hurt Luka Doncic:Not a good play right there. That\'s not"'},
                       {"say": "So was it dirty?"}]}
    ITEMS = [{"beat": 0, "kind": "photo", "person": "Charles Barkley", "title": "Barkley 2019.jpg",
              "tag": {"s": "stage", "t": "talks on a TV set"}},
             {"beat": 1, "kind": "photo", "person": "Luka Doncic", "title": "Luka.jpg", "jersey": "los angeles lakers",
              "tag": {"s": "game", "t": "drives, Lakers"}, "alts": [{"kind": "photo", "person": "Kyle Kuzma", "title": "Kuz.jpg"}]}]
    SOURCES = [{"publisher": "Yahoo Sports", "title": "Barkley calls out Kuzma", "summary": "",
                "text": "\"That's not a good play right there,\" said Barkley. \"Not letting guys land.\""}]

    def test_every_line_gets_its_pictures(self):
        import final_read
        rows = final_read.lines_of(self.SHORT, self.ITEMS)
        self.assertEqual([r["line"] for r in rows], [0, 1, 2])
        self.assertIn("Charles Barkley", rows[0]["pictures"][0])
        self.assertEqual(len(rows[1]["pictures"]), 2)                   # the picture and its alternate
        self.assertIn("jersey: los angeles lakers", rows[1]["pictures"][0])

    def test_only_real_evidence_holds(self):
        import final_read
        rows = final_read.lines_of(self.SHORT, self.ITEMS)
        real = {"errors": [{"line": 1, "kind": "NONSENSE", "what": "broken quote",
                            "evidence": "hurt Luka Doncic:Not a good play right there"}]}
        self.assertEqual(final_read.judge(real, rows, self.SOURCES)["verdict"], "REVIEW")
        made_up = {"errors": [{"line": 1, "kind": "WRONG WORDS", "what": "x",
                               "evidence": "Barkley later apologized to Kuzma on air"}]}
        got = final_read.judge(made_up, rows, self.SOURCES)
        self.assertEqual(got["verdict"], "PASS")
        self.assertIn("evidence not found", got["doubts"][0]["what"])
        self.assertEqual(final_read.judge({"doubts": [{"line": 2, "what": "weak"}]}, rows, self.SOURCES)["verdict"], "PASS")

    def test_the_gate_holds_and_never_publishes_unread(self):
        import gate
        self.assertEqual(gate.check_final_read(None), ("PASS", []))
        self.assertEqual(gate.check_final_read({"verdict": "PASS", "errors": [], "doubts": [{"what": "x"}]})[0], "PASS")
        self.assertEqual(gate.check_final_read({"verdict": "REVIEW", "errors": [{"line": 1, "what": "w"}]})[0], "REVIEW")
        self.assertEqual(gate.check_final_read({"failed": "Claude limit reached"}),
                         ("REVIEW", ["not read by the final reader: Claude limit reached"]))
        src = (ROOT / "src" / "gate.py").read_text(encoding="utf-8")
        self.assertIn('{"failed": "no final read for this Short"}) if REVIEW.is_dir() else None', src)

    def test_the_stage_reads_every_short(self):
        import final_read, script, tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for sub in ("scripts", "media", "sources", "review"):
                (d / sub).mkdir()
            for n in (1, 2, 3):
                (d / "scripts" / f"short_{n}.json").write_text(json.dumps(self.SHORT), encoding="utf-8")
            for n in (1, 3):
                (d / "sources" / f"short_{n}.json").write_text(json.dumps(self.SOURCES), encoding="utf-8")
            answers = iter([{"errors": [{"line": 1, "kind": "NONSENSE", "what": "broken",
                                         "evidence": "hurt Luka Doncic:Not a good play right there"}]},
                            {"error": True},          # 110: the second check of that error (it stays)
                            script.UsageLimit("5-hour limit")])

            def fake(*a, **k):
                x = next(answers)
                if isinstance(x, Exception):
                    raise x
                return x
            saved = (final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW)
            try:
                final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW = (
                    d / "scripts", d / "media", d / "sources", d / "review")
                with patch.object(script, "ask_claude", side_effect=fake) as ask, patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}):
                    final_read.main()
                self.assertEqual(ask.call_args_list[0].kwargs.get("where"), "final_read")
                self.assertEqual(ask.call_args_list[0].args[1], script.CLAUDE_MODEL)    # the main model (his choice)
            finally:
                final_read.SCRIPTS, final_read.MEDIA, final_read.SOURCES, final_read.REVIEW = saved
            got = {n: json.loads((d / "review" / f"short_{n}.json").read_text(encoding="utf-8")) for n in (1, 2, 3)}
        self.assertEqual(got[1]["verdict"], "REVIEW")
        self.assertIn("not kept", got[2]["failed"])                         # no sources: never "read"
        self.assertIn("limit", got[3]["failed"])

    def test_wired_into_the_run(self):
        import state
        wf = (ROOT / ".github" / "workflows" / "collect.yml").read_text(encoding="utf-8")
        self.assertLess(wf.index("python src/final_read.py"), wf.index("python src/gate.py"))
        self.assertIn("review/short_*.json", state.RUN_FILES)



class SheetsOpenedAtOnce(unittest.TestCase):
    """54 (D16). Claude Code re-sends the whole conversation at every step. Opening 5 sheets one
    per step made a 45-photo tag call cost about 15k + 18k + 21k + 24k + 27k + 30k = 136k tokens
    (run 43395656602's biggest call was 136,625); all at once: about 15k + 30k."""

    def test_both_sheet_prompts_ask_for_one_step(self):
        import media, photo_tags
        for prompt in (photo_tags.TAG_PROMPT, media.PICK_PROMPT):
            self.assertIn("ALL AT ONCE", prompt)
            self.assertIn("never one sheet per step", " ".join(prompt.split()))

    def test_turns_are_logged(self):
        import media, script, tempfile
        out = json.dumps({"usage": {"input_tokens": 5, "cache_read_input_tokens": 10}, "num_turns": 6,
                          "duration_ms": 2000, "total_cost_usd": 0.1})
        for mod in (media, script):
            with tempfile.TemporaryDirectory() as d:
                fake = Path(d) / "src" / "x.py"
                with patch.object(mod, "__file__", str(fake)):
                    mod.log_claude_usage(out, "t")
                row = json.loads((Path(d) / "data" / "claude_usage.jsonl").read_text(encoding="utf-8"))
            self.assertEqual((row["turns"], row["in"]), (6, 15))



class NoNameBeforeItsImport(unittest.TestCase):
    """55 (run 43407418420). The audit's "print only without GITHUB_STEP_SUMMARY" (e54499d) put
    os.environ before a leftover "import os" inside render.main: Python then treats os as a local
    name, the stage crashed after both videos were made, and the gate never ran. Checked for
    every function in every stage, so no stage can fail this way again."""

    def test_every_function(self):
        import ast
        found = []
        for path in sorted((ROOT / "src").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for fn in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
                first = {}
                for n in ast.walk(fn):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        for a in n.names:
                            name = (a.asname or a.name).split(".")[0]
                            first[name] = min(first.get(name, n.lineno), n.lineno)
                found += [f"{path.name}:{n.lineno} {fn.name} uses {n.id} before line {first[n.id]}"
                          for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id in first and n.lineno < first[n.id]]
        self.assertEqual(found, [])



class HisOwnCategoryIsHim(unittest.TestCase):
    """56 (run 43407418420). Rule 47 (another man with his surname) took 27 of Dejounte Murray's
    31 Commons photos: Flickr titled them "Dejonte Murray". They were in his OWN Commons category,
    which people file by hand under that very player. A wrong-team photo still meets the jersey law."""

    def test_own_category_is_kept(self):
        m = self.m = __import__("media")
        saved = (m.commons_photos, m.flickr_photos, m.openverse_photos, dict(m._all_photos))
        m._all_photos.clear()
        pool = [{"page": "a", "score": 30, "title": "Dejonte Murray (51915001522).jpg", "own_category": True},
                {"page": "b", "score": 20, "title": "Dejonte Murray (51915008527).jpg"},
                {"page": "c", "score": 10, "title": "Dejounte Murray Pelicans.jpg"}]
        try:
            m.commons_photos = lambda person: [dict(p) for p in pool]
            m.flickr_photos = m.openverse_photos = lambda person: []
            self.assertEqual([p["page"] for p in m.photos("Dejounte Murray")], ["a", "c"])
        finally:
            m.commons_photos, m.flickr_photos, m.openverse_photos = saved[:3]
            m._all_photos.clear()
            m._all_photos.update(saved[3])

    def test_commons_records_the_category(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('"own_category": title in in_category,', src)



class FinalReadKeepsThePictureRules(unittest.TestCase):
    """57 (run 43407418420). The first real final read held Luka in a Dallas jersey on "no word
    from Luka" and Zion on "the Pelicans are 1 and 8 with Murray": both are allowed by the agreed
    picture rules (a former team scores lower, another person from the story fits a team line).
    Zion over "He wrote that the sabotage is real, deleted it" stays an error: the viewer takes
    Zion for the one who wrote it."""

    def test_prompt(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("someone else shown while the line says what HE said or did", p)
        self.assertIn("the right man in a former team's jersey when the line names no team or time", p)
        self.assertIn("NOT an error (at most a doubt)", p)

    def test_media_calls_are_named(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        for step in ("media_plan", "media_tags", "media_shortlist", "media_pick", "media_pick2"):
            self.assertIn(f'where="{step}"', src)
        self.assertIn("log_claude_usage(res.stdout, where)", src)



class OnlyAHeadlineIsSkipped(unittest.TestCase):
    """58 (run 43407418420). Cunningham's claim about Luka: its one copy unread, two Luka-injury
    pieces read instead, so the 600-character bar passed and the Short could only say "from an
    outlet I can't verify" (held). Replay on 29 Shorts: only that one is a fresh story with its
    own article unread; the evergreens without it (two of them PASS) are untouched."""

    def build(self, evergreen, main):
        import script
        editor = {"topics": [{"headline": "Cunningham says Luka wanted the fan gone", "items": []}],
                  "ranked": [{"id": 0, **({"evergreen": "k"} if evergreen else {})}]}
        src = [{"publisher": "HITC", "title": "Luka injury update", "text": "x" * 3000, "main": main, "link": "l",
                "tier": 2, "summary": ""}]
        with patch.object(script, "gather_sources", return_value=src), \
                patch.object(script, "ask_claude", side_effect=RuntimeError("written")):
            try:
                script.build_short(1, 0, editor, "", {"hooks": [], "rules": []})
            except Exception as exc:          # noqa: BLE001
                return str(exc)
        return ""

    def test_fresh_story_unread_is_skipped_before_claude(self):
        self.assertIn("could not be read in any copy", self.build(evergreen=False, main=False))

    def test_read_story_and_evergreens_go_on(self):
        self.assertEqual(self.build(evergreen=False, main=True), "written")   # reached the writer
        self.assertEqual(self.build(evergreen=True, main=False), "written")



class NoSilentFeeds(unittest.TestCase):
    """59 (2026-11-13). Three sources were silent in every run and nobody saw it: ESPN (0 items
    on GitHub's servers, 17 elsewhere), HoopsHype (402 Payment Required) and the podcast search
    (39 items, all from May: "when:1d" at the end, after "-prediction", was ignored)."""

    def test_when_first_in_every_search(self):
        import sources
        for f in sources.FEEDS:
            for url in (f["url"], f.get("fallback") or ""):
                if "news.google.com" in url:
                    self.assertIn("search?q=when:1d+", url, f["name"])
                    self.assertNotIn("+when:1d&", url, f["name"])

    def test_silent_feed_falls_back_and_says_why(self):
        import collect, feedparser, io
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).timetuple()
        D = feedparser.FeedParserDict

        def entry(title):
            return D(title=title, link="https://news.google.com/x/" + title.replace(" ", ""), published_parsed=now,
                     summary="NBA", source=D(title="ESPN"))
        feeds = [{"name": "ESPN", "url": "https://espn/rss", "tier": 1, "fallback": "https://news.google.com/rss/search?q=when:1d+site:espn.com/nba"},
                 {"name": "CBS Sports", "url": "https://cbs/rss", "tier": 1}]
        answers = {"https://espn/rss": D(entries=[], status=403, bozo=0, feed=D()),
                   feeds[0]["fallback"]: D(entries=[entry("Draymond rips Kerr after loss NBA")]
                                           + [entry(f"Suns 101-96 Hornets (Nov 12, 2026) Game Recap {i}") for i in range(3)]
                                           + [entry(f"Lakers NBA story number {i}") for i in range(40)], status=200, bozo=0, feed=D()),
                   "https://cbs/rss": D(entries=[], status=200, bozo=0, feed=D())}
        out = io.StringIO()
        with patch.object(collect, "FEEDS", feeds), patch.object(collect.feedparser, "parse", lambda u, agent=None: answers[u]), \
                patch("sys.stdout", out):
            items = collect.fetch_all()
        log = out.getvalue()
        self.assertIn("ESPN gave nothing: HTTP 403", log)
        self.assertEqual(len(items), collect.FALLBACK_MAX)
        self.assertFalse(any("Game Recap" in i["title"] for i in items))
        self.assertEqual({i["publisher"] for i in items}, {"ESPN"})
        self.assertEqual(items[0]["tier"], 1)                       # ESPN stays a tier 1 outlet
        self.assertIn("CBS Sports gave nothing: HTTP 200", log)    # no fallback: only the reason



class MoreSourcesForTheBeef(unittest.TestCase):
    """60 (owner, 2026-11-13: ChatGPT's source list, checked one by one). Kept only what is free,
    answers GitHub's servers (run 43441957341) and brings beef, scandal or intrigue."""

    def test_the_new_sources_are_there(self):
        import sources
        names = {f["name"] for f in sources.FEEDS}
        for n in ("ClutchPoints", "Hoops Rumors", "SB Nation", "Defector", "TrueHoop", "GN: statements", "GN: scandal",
                  "GN: vs coach or teammate", "GN: viral", "GN: insiders", "Gil's Arena (podcast)",
                  "The Draymond Green Show (podcast)", "Pablo Torre Finds Out (podcast)", "Club 520 (podcast)",
                  "All the Smoke (podcast)"):
            self.assertIn(n, names)
        pods = [f for f in sources.FEEDS if f["name"].endswith("(podcast)")]
        self.assertTrue(all(f.get("filter") and "channel_id=UC" in f["url"] for f in pods))
        self.assertTrue(next(f for f in sources.FEEDS if f["name"] == "Defector").get("filter"))
        self.assertEqual(len(names), len(sources.FEEDS))                   # no source twice

    def test_multi_sport_feeds_keep_only_nba(self):
        import collect, feedparser
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).timetuple()
        D = feedparser.FeedParserDict
        feed = {"name": "Dan Patrick Show (podcast)", "url": "u", "tier": 2, "filter": True, "video": True}
        nfl = D(title="Kurt Warner Looks At J.J. McCarthy's Results With The Giants", link="https://y/1",
                published_parsed=now, summary="NFL quarterbacks")
        nba = D(title="Luka Doncic Hits His 5th Three-Pointer Of The Game For The Lakers", link="https://y/2",
                published_parsed=now, summary="")
        self.assertIsNone(collect.normalize(nfl, feed))
        got = collect.normalize(nba, feed)
        self.assertEqual((got["publisher"], got["tier"]), ("Dan Patrick Show (podcast)", 2))
        plain = {"name": "ClutchPoints", "url": "u", "tier": 2}            # an NBA-only feed: not filtered
        self.assertIsNotNone(collect.normalize(D(title="Jeff Teague says Brunson needs help", link="https://c/1",
                                                 published_parsed=now, summary=""), plain))

    def test_reddit_rising_follows_hot_after_a_pause(self):
        import signals
        calls = []

        def fake(url=signals.REDDIT_RSS):
            calls.append(url)
            return ["Smart punches Bassey", "Curry out"] if url == signals.REDDIT_RSS else ["Curry out", "Kuminga wants out"]
        topics = [{"headline": "Kuminga wants out", "items": [{"title": "Jonathan Kuminga wants out of Golden State"}]}]
        with patch.object(signals, "reddit_hot", side_effect=fake), patch.object(signals.time, "sleep") as nap:
            got = signals.reddit_titles()
        self.assertEqual(calls, [signals.REDDIT_RSS, signals.REDDIT_RISING])
        nap.assert_called_with(signals.REDDIT_PAUSE)
        self.assertEqual(got[0], ["Smart punches Bassey", "Curry out", "Kuminga wants out"])

    def test_a_video_page_is_never_read_as_an_article(self):
        import script
        with patch.object(script.trafilatura, "fetch_url", return_value="<html>Subscribe! Gil's Arena</html>") as fetch:
            for url in ("https://www.youtube.com/watch?v=abc", "https://youtu.be/abc"):
                it = {"link": url, "text": ""}
                self.assertFalse(script.read_article(it, {}))
                self.assertEqual(it["text"], "")
            fetch.assert_not_called()

    def test_rising_failing_keeps_hot(self):
        import signals

        def fake(url=signals.REDDIT_RSS):
            if url == signals.REDDIT_RISING:
                raise OSError("HTTP Error 429")
            return ["Smart punches Bassey"]
        with patch.object(signals, "reddit_hot", side_effect=fake), patch.object(signals.time, "sleep"):
            titles, errors = signals.reddit_titles()
        self.assertEqual(titles, ["Smart punches Bassey"])
        self.assertTrue(any("rising" in e for e in errors))


class CollegeDaysBeforeTheDraft(unittest.TestCase):
    """61. D22 (run 43446225184): Yaxel Lendeborg, a Warriors rookie (Wikidata: Golden State from
    2026-06-23), was shown in three Michigan #23 photos of 11 Feb 2026 on "a 24-year-old rookie" and
    "8-4 start"; none was marked PRE-NBA. The copies shown came through Openverse (no date, no
    categories), the Commons copy of the same file was the one with the facts, and a year alone
    (2026 = 2026) can never mark a rookie's last college season."""

    CLAIMS = {"Q123": [
        {"mainsnak": {"datavalue": {"value": {"id": "Q7863702"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2023-00-00T00:00:00Z"}}}],
                        "P582": [{"datavalue": {"value": {"time": "+2025-00-00T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q6837797"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2025-00-00T00:00:00Z"}}}]}},
        {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2026-06-23T00:00:00Z"}}}]}}],
        "Q456": [   # a year-only start: he may have joined mid-season, so no day is trusted
        {"mainsnak": {"datavalue": {"value": {"id": "Q157376"}}}, "rank": "normal",
         "qualifiers": {"P580": [{"datavalue": {"value": {"time": "+2019-00-00T00:00:00Z"}}}]}}]}
    LABELS = {"Q7863702": "UIC Flames men's basketball", "Q6837797": "Michigan Wolverines men's basketball",
              "Q157376": "Golden State Warriors"}

    def setUp(self):
        import media
        self.m = media
        self.saved = (media.get, dict(media._wikidata), dict(media._teams), dict(media._nba_debut),
                      dict(media._nba_debut_day), media.commons_photos, media.flickr_photos,
                      media.openverse_photos, dict(media._all_photos))
        for d in (media._wikidata, media._teams, media._nba_debut, media._nba_debut_day, media._all_photos):
            d.clear()
        media._wikidata.update({"Yaxel Lendeborg": "Q123", "Late Joiner": "Q456"})
        claims, labels = self.CLAIMS, self.LABELS

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("action") == "wbgetclaims":
                return json.dumps({"claims": {"P54": claims.get(q["entity"], [])}}).encode()
            if q.get("action") == "wbgetentities":
                return json.dumps({"entities": {i: {"labels": {"en": {"value": labels[i]}}}
                                                for i in q["ids"].split("|") if i in labels}}).encode()
            raise OSError("unexpected")
        media.get = get
        media.flickr_photos = lambda person: []

    def tearDown(self):
        m, s = self.m, self.saved
        m.get, m.commons_photos, m.flickr_photos, m.openverse_photos = s[0], s[5], s[6], s[7]
        for d, old in ((m._wikidata, s[1]), (m._teams, s[2]), (m._nba_debut, s[3]), (m._nba_debut_day, s[4]),
                       (m._all_photos, s[8])):
            d.clear()
            d.update(old)

    @staticmethod
    def commons(title, date="", team=""):
        return {"kind": "photo", "title": title, "source": "Wikimedia Commons", "date": date, "team": team,
                "page": "https://commons.wikimedia.org/wiki/File:" + title.replace(" ", "_"),
                "url": "https://upload.wikimedia.org/x/" + title.replace(" ", "_"), "score": 20}

    @staticmethod
    def openverse(title):
        return {"kind": "photo", "title": title, "source": "Wikimedia via Openverse", "team": "",
                "page": "https://commons.wikimedia.org/w/index.php?curid=" + str(abs(hash(title)) % 10**9),
                "url": "https://upload.wikimedia.org/y/" + title.replace(" ", "_") + ".jpg", "score": 9}

    def test_the_day_his_nba_career_began(self):
        m = self.m
        self.assertEqual(m.teams_of("Yaxel Lendeborg")[0], "golden state warriors")
        self.assertEqual(m._nba_debut_day["Q123"], "2026-06-23")
        m.teams_of("Late Joiner")
        self.assertNotIn("Q456", m._nba_debut_day)
        self.assertEqual(m.title_day("20260211 Yaxel Lendeborg 13"), "2026-02-11")
        self.assertEqual(m.title_day("Celtics at Wizards 2024-12-15 (cropped).jpg"), "2024-12-15")
        self.assertEqual(m.title_day("Yaxel Lendeborg (51831075412).jpg"), "")   # a Flickr id is no day

    def test_lendeborg_pool(self):
        m = self.m
        m.commons_photos = lambda person: [self.commons("20260211 Yaxel Lendeborg 13.jpg", "2026-02-11"),
                                           self.commons("Yaxel Lendeborg Warriors 2026.jpg", "2026-10-30", "current")]
        m.openverse_photos = lambda person: [self.openverse("20260211 Yaxel Lendeborg 13"),   # the same file
                                             self.openverse("20260211 Yaxel Lendeborg 05"),   # only here
                                             self.openverse("20261105 Yaxel Lendeborg 02"),   # an NBA game
                                             self.openverse("20260621 NBA Draft Yaxel Lendeborg")]
        got = {p["title"]: p for p in m.photos("Yaxel Lendeborg")}
        self.assertNotIn("20260211 Yaxel Lendeborg 13", got)              # one picture: the Commons copy
        self.assertEqual(got["20260211 Yaxel Lendeborg 13.jpg"]["team"], "pre-nba")
        self.assertEqual(got["20260211 Yaxel Lendeborg 05"]["team"], "pre-nba")
        self.assertEqual(got["20260211 Yaxel Lendeborg 05"]["date"], "2026-02-11")
        self.assertEqual(got["20261105 Yaxel Lendeborg 02"]["team"], "")
        self.assertEqual(got["20260621 NBA Draft Yaxel Lendeborg"]["team"], "")   # says NBA: not school
        self.assertEqual(got["Yaxel Lendeborg Warriors 2026.jpg"]["team"], "current")
        self.assertEqual([p["team"] for p in m.photos("Yaxel Lendeborg")][-2:], ["pre-nba", "pre-nba"])

    def test_nothing_changes_without_a_day(self):
        m = self.m
        m.commons_photos = lambda person: [self.commons("Late Joiner 2019.jpg", "2019-03-01")]
        m.openverse_photos = lambda person: [self.openverse("20190301 Late Joiner")]
        self.assertEqual([p["team"] for p in m.photos("Late Joiner")], ["", ""])
        self.assertFalse(m.pre_nba_by_day("Yaxel Lendeborg", {"date": "2026-02-11", "team": "former"}))
        self.assertFalse(m.pre_nba_by_day("Yaxel Lendeborg", {"date": "2026", "team": ""}))

    def test_final_read_sees_it(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("A picture marked PRE-NBA (high school, college) on a line about his NBA career", p)
        self.assertIn("PRE-NBA", final_read.picture_line({"person": "Yaxel Lendeborg", "team": "pre-nba",
                                                           "title": "20260211 Yaxel Lendeborg 13"}))


class WikidataCanMissASpell(unittest.TestCase):
    """62. D23 (run 43446225184): Kyrie Irving's Wikidata teams are Cavaliers, Celtics, Mavericks
    (and Duke), with no Nets 2019-2023, so 12 real photos of him in a Nets jersey were left out as
    "a team he never played for". A photo that is HIS (his own Commons category, or his first and
    last name in the title) is trusted; the law still stops Isaiah Thomas shown as Isiah Thomas."""

    CAREER = ["boston celtics", "cleveland cavaliers", "dallas mavericks"]

    def test_his_own_photo_is_trusted(self):
        import compliance as C
        import media
        nets = {"s": "game", "t": "brings ball up court, Nets jersey"}
        cases = [({"title": "Kyrie Irving (51831075412).jpg", "tag": nets}, True),
                 ({"title": "Kyrie_Irving_-_51832441040.jpg", "tag": nets}, True),
                 ({"title": "Darius Garland (51830745547).jpg", "tag": nets, "own_category": True}, True),
                 ({"title": "Darius Garland (51830745547).jpg", "tag": nets}, False),
                 ({"title": "Irving dribbles (2021).jpg", "tag": nets}, False)]
        for c, ok in cases:
            self.assertEqual(media.his_own("Kyrie Irving", c), ok, c["title"])
            self.assertEqual(C.jersey_ok(media.jersey_team(c["tag"]), self.CAREER, media.his_own("Kyrie Irving", c)),
                             ok, c["title"])

    def test_the_isaiah_law_still_holds(self):
        import compliance as C
        import media
        c = {"title": "Isaiah Thomas (50639077836).jpg", "tag": {"s": "game", "t": "dribbles in Wizards jersey"}}
        self.assertFalse(media.his_own("Isiah Thomas", c))
        self.assertFalse(C.jersey_ok("washington wizards", ["detroit pistons"], media.his_own("Isiah Thomas", c)))
        self.assertTrue(C.jersey_ok("brooklyn nets", self.CAREER, True))
        self.assertFalse(C.jersey_ok("brooklyn nets", self.CAREER))

    def test_the_pool_and_the_gate(self):
        import gate
        import media
        self.assertIn("C.jersey_ok(jersey_team(c.get(\"tag\")), career, his_own(person, c))",
                      (ROOT / "src" / "media.py").read_text(encoding="utf-8"))
        self.assertIn('x["his_own"] = his_own(x.get("person") or "", x)',
                      (ROOT / "src" / "media.py").read_text(encoding="utf-8"))
        nets = {"kind": "photo", "person": "Kyrie Irving", "jersey": "brooklyn nets", "page": "p", "url": "u",
                "author": "a", "license": "CC BY-SA 2.0", "match": 7, "title": "Kyrie Irving (51831075412)"}
        flags = {"careers": {"Kyrie Irving": self.CAREER}}
        _, notes = gate.check_visuals([dict(nets, his_own=True)], flags)
        self.assertFalse(any("never played for" in n for n in notes), notes)
        _, notes = gate.check_visuals([dict(nets, his_own=False, title="Isaiah Thomas", person="Isiah Thomas",
                                            jersey="washington wizards")],
                                      {"careers": {"Isiah Thomas": ["detroit pistons"]}})
        self.assertTrue(any("never played for" in n for n in notes), notes)


class TitleBoldButTrue(unittest.TestCase):
    """63. D24 (run 43446225184): the title "Curry's two weeks is a LIE? 😳" called the Warriors'
    "re-evaluated in two weeks" a lie; the hook was read against the sources (D17), the title never
    was. Now one call reads the top titles: an overstated one steps behind, the best true one leads;
    all of them overstated = the Short is held; a failed call changes nothing."""

    TITLES = [{"title": "Curry's two weeks is a LIE? 😳", "score": 100},
              {"title": "Stephen Curry is out WAY longer 😬", "score": 100},
              {"title": "Warriors face a BIG Curry problem 😳", "score": 100}]
    SOURCES = [{"publisher": "Yahoo Sports", "title": "Warriors brace", "text": "re-evaluated in two weeks", "tier": 1}]

    def run_with(self, answer):
        import script
        saved = script.ask_claude
        seen = []

        def ask(prompt, *a, **k):
            seen.append(prompt)
            if isinstance(answer, Exception):
                raise answer
            return answer
        script.ask_claude = ask
        try:
            return script.check_title_truth(copy.deepcopy(self.TITLES), self.SOURCES), seen
        finally:
            script.ask_claude = saved

    def test_the_lie_steps_behind(self):
        got, seen = self.run_with({"overstated": [1], "why": "nobody lied"})
        self.assertEqual(len(seen), 1)
        self.assertIn("1. Curry's two weeks is a LIE?", seen[0])
        self.assertEqual(got[0]["title"], "Stephen Curry is out WAY longer 😬")
        self.assertEqual(got[-1]["overstated"], "nobody lied")
        self.assertFalse(got[0].get("all_overstated"))

    def test_all_overstated_or_failed(self):
        got, _ = self.run_with({"overstated": [1, 2, 3], "why": "x"})
        self.assertTrue(got[0].get("all_overstated"))
        # D91 (a changed rule, his answer 2026-11-25: one rule with the hook's D83): a call that
        # still fails counts every title read as overstated, so the Short is held
        got, _ = self.run_with(OSError("down"))
        self.assertEqual(sorted(t["title"] for t in got), sorted(t["title"] for t in self.TITLES))
        self.assertTrue(all(t.get("overstated") for t in got))
        self.assertTrue(got[0].get("all_overstated"))
        got, _ = self.run_with({"overstated": [], "why": ""})
        self.assertEqual(got[0]["title"], self.TITLES[0]["title"])

    def test_wired_in(self):
        import script
        src = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn("titles = check_title_truth(titles, sources)", src)
        self.assertIn('if titles and titles[0].get("all_overstated"):', src)
        self.assertEqual(script.TITLES_CHECKED, 10)   # his answer: every title is read
        p = " ".join(script.TITLE_TRUTH.split())
        self.assertNotIn('"Is X a LIE?"', p)    # his answer (2026-11-14): no special rule for question titles
        self.assertIn("BOLD BUT TRUE", p)


class PickSheetsByName(unittest.TestCase):
    """64. D25 (run 43446225184): the pick took 15 and 19 steps (169k and 138k tokens). Its prompt
    said "beat_0.jpg, beat_1.jpg, ..." and Claude cannot list the folder (no Glob), so it opened one
    sheet, then guessed the next name, a step each. The exact names let it open all in one step."""

    def test_names_in_beat_order(self):
        import media
        with tempfile.TemporaryDirectory() as d:
            for n in ("beat_10.jpg", "beat_0_2.jpg", "beat_1.jpg", "beat_0.jpg", "beat_2.jpg", "note.txt"):
                (Path(d) / n).write_bytes(b"x")
            self.assertEqual(media.sheet_names(Path(d)), "beat_0.jpg, beat_0_2.jpg, beat_1.jpg, beat_2.jpg, beat_10.jpg")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(media.sheet_names(Path(d)), "none")

    def test_both_pick_calls_name_the_sheets(self):
        import media
        p = " ".join(media.PICK_PROMPT.split())
        self.assertIn("are exactly these contact sheets (one or more per beat): SHEETS.", p)
        self.assertNotIn("beat_0.jpg, beat_1.jpg, ...", p)
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertEqual(src.count('PICK_PROMPT.replace("SHEETS", sheet_names(sheets))'), 2)


class PopularConflictWeighsMore(unittest.TestCase):
    """65. D26 (owner, 2026-11-13): a conflict between popular teams or players weighs slightly more
    than another kind of scandal, intrigue or drama around a popular player. Run 43446225184 gave a
    Curry injury follow-up (no conflict) the slot. On top of the +6 for any real conflict: +0 at
    star power 5 or less, up to +4 at 10. Replayed on every kept run: 3 runs (43253965466,
    43262308476, 43294793044) would have made "Mike Brown calls out refs" (S8-9) instead of an old
    feud; nothing else changes."""

    BASE = {"drama": 7, "virality": 7, "debate": 7, "search_hits": 3, "youtube_heat": 5, "hours_old": 2,
            "nba": True, "kind": "player_vs_player"}

    def score(self, **k):
        import editor
        return editor.short_score({**self.BASE, **k})

    def test_the_popular_fight_weighs_more(self):
        calm = self.score(star_power=10, conflict=False)
        self.assertAlmostEqual(self.score(star_power=10, conflict=True) - calm, 10.0, places=1)    # 6 + 4
        self.assertAlmostEqual(self.score(star_power=5, conflict=True) - self.score(star_power=5, conflict=False), 6.0, places=1)
        self.assertAlmostEqual(self.score(star_power=8, conflict=True) - self.score(star_power=8, conflict=False), 8.4, places=1)
        self.assertAlmostEqual(self.score(star_power=3, conflict=True) - self.score(star_power=3, conflict=False), 6.0, places=1)

    def test_only_slightly(self):
        # a popular fight beats an equally popular non-fight of the same size, but a much bigger
        # story without a fight still wins (popularity weighs as much as the beef: his earlier rule)
        self.assertGreater(self.score(star_power=9, conflict=True), self.score(star_power=9, conflict=False, debate=9))
        self.assertGreater(self.score(star_power=10, conflict=False, drama=9, virality=9, youtube_heat=9),
                           self.score(star_power=6, conflict=True))


class WhoSaidItAndIsItStillTrue(unittest.TestCase):
    """66. Run 43446225184 (D2 notes): "Shams Charania told ESPN that's just a checkpoint" - the
    word was the Yahoo writer's conclusion, not Shams's; "eight straight wins now rest on
    Lendeborg" - the streak had ended. The final read saw the second only as a doubt. Now the
    writer and the critic give each claim to its owner and say an ended fact as over, and the
    final read counts both as errors (with the source's words as evidence)."""

    def test_writer_and_critic(self):
        import script
        p = " ".join(script.PROMPT.split())
        self.assertIn("WHO SAID IT, AND IS IT STILL TRUE", p)
        self.assertIn("is the outlet's, never the insider's or player's it writes about", p)
        h = " ".join(script.HUMANIZE.split())
        self.assertIn("- WHO SAID IT: every \"X said / told / says\" gives X only what X said in the sources", h)
        self.assertIn("A fact that has ended (a streak, a spell, a record) is said as over", h)
        self.assertIn("WHO SAID IT", script.HUMANIZE.format(voice="v", sources="s", draft="d"))   # no stray braces

    def test_final_read_errors(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("Also when \"X said / told / says\" gives X a claim that, in the sources, is the outlet's own "
                      "conclusion and not X's words", p)
        self.assertIn("a fact the sources show has ENDED or changed, said as still true now", p)


class RewriteKeepsTheHookRules(unittest.TestCase):
    """67. D27 (run 43485568700): the bold-true rewrite of a hook only had to pass the fact checks.
    It gave Mitchell's Short "Donovan Mitchell fires back at Barkley: 'Who gives a f—k?'..." (gate
    REJECT, one of the run's two Shorts lost) and Arenas's "Steph Curry is out at least two weeks,
    and Gilbert Arenas warns..." (the story's lead at word 9). Now a rewrite keeps every hook rule
    (no profanity, the lead person in the first 8 words), else the old order stays; a profane hook
    never leads, and the order is applied before the truth read so the read hook can lead."""

    def test_the_two_real_rewrites_fail(self):
        import script
        r = script.rewrite_keeps_hook_rules
        self.assertFalse(r("Steph Curry is out at least two weeks, and Gilbert Arenas warns Draymond Green will "
                           "struggle without him.", "Gilbert Arenas just buried Draymond Green without Steph Curry.",
                           "arenas"))
        self.assertFalse(r("Donovan Mitchell fires back at Barkley: 'Who gives a f—k?' after Cavs 'suck' remark.",
                           "Donovan Mitchell told Barkley nobody in Cleveland cares.", "mitchell"))
        self.assertTrue(r("Gilbert Arenas warns Draymond Green will struggle without Steph Curry.",
                          "Gilbert Arenas just buried Draymond Green without Steph Curry.", "arenas"))
        # the 7 real rewrites of 43395656602-43485568700: 4 keep passing; Kyrie's (run 43446225184) put
        # Kyrie at word 9 behind Ujiri, so the next hook leads now ("Dallas is winning with Kyrie Irving...")
        self.assertFalse(r("Masai Ujiri said the Mavs truly believe in Kyrie Irving, yet rival teams still eye him.",
                           "Masai Ujiri says the Mavs are keeping Kyrie Irving, but rivals want him.", "irving"))
        self.assertTrue(r("Dejounte Murray deleted two angry posts after the Nets blowout, Pelicans sinking at 4-8.",
                          "Dejounte Murray blasted the Pelicans, then deleted it.", "murray"))
        self.assertTrue(r("Charles Barkley calls out Kyle Kuzma on live TV for not letting Luka Doncic land.",
                          "Charles Barkley ripped Kyle Kuzma for hurting Luka Doncic.", "barkley"))
        # no lead known: a name of the old first 8 words stays in the first 8
        self.assertFalse(r("After a long night in Boston, the fans saw Tatum snub Brown.", "Tatum snubbed Brown again.", ""))

    def test_profane_never_leads_and_order_first(self):
        import script
        hooks = [{"text": "Mitchell to Barkley: 'Who gives a f—k?'", "unsupported_details": []},
                 {"text": "Charles Barkley said the Cavs suck, and Donovan Mitchell fired straight back.",
                  "unsupported_details": []}]
        read = []
        saved = script.check_hook_truth
        script.check_hook_truth = lambda h, s, lead="": read.append(h["text"]) or "ok"
        try:
            script.truth_order(hooks, [], "barkley")
        finally:
            script.check_hook_truth = saved
        self.assertTrue(hooks[0]["text"].startswith("Charles Barkley said"))
        self.assertEqual(read, [hooks[0]["text"]])      # the hook that leads is the one that was read


class OnRecordBeatReporter(unittest.TestCase):
    """68. D29 (owner, 2026-11-13: an on-record quote a team's beat journalist published is a
    reliable source). Run 43485568700 held Mitchell vs Barkley ("only secondary outlets and no
    named insider") though Hoops Wire wrote: "Chuck ain't here," Mitchell told Chris Fedor of
    Cleveland.com. A named reporter of a named outlet credited for a direct quote counts; an
    outlet alone, a reporter with no quote, or "a source told" does not."""

    def test_who_counts(self):
        import compliance as C
        cases = {'“Chuck ain’t here,” Mitchell told Chris Fedor of Cleveland.com. Barkley said': ["chris fedor (cleveland.com)"],
                 '“We are fine,” he said, according to The Athletic’s Joe Vardon.': ["joe vardon (the athletic)"],
                 '“Who gives a f—k?” Mitchell said, per Cleveland.com. “Chuck': ["(cleveland.com)"],   # his answer: an outlet is enough
                 '“I hate him,” a league source said, per ESPN.': [],                                # anonymous never
                 '“Let’s go,” Brown told Tatum before the game.': [],                                 # "told X" alone: X may be a player
                 'Chris Fedor of Cleveland.com reported the Cavs are shopping Allen.': [],
                 '“I hate him,” a source told Bleacher Report.': [],
                 'Mitchell told Chris Fedor of Cleveland.com he is not worried.': []}   # no quote: not on record
        for text, want in cases.items():
            self.assertEqual(C.on_record_reporters([{"text": text}]), want, text)

    def test_the_mitchell_story_passes(self):
        import compliance as C
        secondary = {"publisher": "Hoops Wire", "tier": 2, "title": "Mitchell dismisses Barkley",
                     "text": 'Donovan Mitchell answered. “Chuck ain’t here,” Mitchell told Chris Fedor of Cleveland.com.'}
        self.assertEqual(C.check_sources([secondary])[0], C.PASS)
        plain = dict(secondary, text='Donovan Mitchell answered Barkley, a blog says.')
        self.assertEqual(C.check_sources([plain])[0], C.REVIEW)
        claim = [{"text": "Mitchell told Fedor Chuck ain't here", "status": "REPORTED", "source": 1}]
        _, _, out = C.check_claims(claim, [secondary], "Mitchell told Cleveland.com that Chuck ain't here.")
        self.assertEqual(out[0]["status"], "REPORTED")
        _, _, out = C.check_claims(claim, [plain], "Mitchell reportedly said Chuck ain't here.")
        self.assertEqual(out[0]["status"], "RUMOR")


class TopUpsKeepTheTeamOrder(unittest.TestCase):
    """69. D28 (run 43485568700): the unjudged extra shots ranked only by face and game, so three
    Utah Jazz photos of Donovan Mitchell (2018-19) filled Cavs lines ("Are the Cavs the same
    failing team...?") while Cavs photos were left. The agreed order now holds for top-ups too:
    today's team or no team first, a former team after - never dropped."""

    def test_order(self):
        import photo_tags
        clear = {"v": "C", "s": "game", "t": "drives"}
        pool = [{"page": "utah", "team": "former", "tag": clear, "hoops": True},
                {"page": "cavs", "team": "current", "tag": clear, "hoops": True},
                {"page": "plain", "team": "", "tag": {"v": "B", "s": "game", "t": "back turned"}, "hoops": True},
                {"page": "untagged", "team": "", "hoops": True}]
        self.assertEqual([c["page"] for c in sorted(pool, key=photo_tags.fill_rank)],
                         ["cavs", "plain", "utah", "untagged"])

    def test_person_photos_both_ways(self):
        import media
        saved = (media.photos, media.solo_title)
        media.solo_title = lambda c, p: True
        try:
            pool = [{"page": "u", "team": "former", "hoops": True, "title": "Donovan Mitchell Utah"},
                    {"page": "c", "team": "current", "hoops": False, "title": "Donovan Mitchell"}]
            media.photos = lambda person: [dict(p) for p in pool]
            self.assertEqual([c["page"] for c in media.person_photos("Donovan Mitchell", set())], ["c", "u"])
        finally:
            media.photos, media.solo_title = saved


class TopUpsByRelevanceTeamAndFace(unittest.TestCase):
    """70. D30 (owner, 2026-11-14: "team and face are both important and both must be right; which
    photo is chosen is left to the relevance score"). The extra shots of a long beat now come first
    from the photos Claude scored 6+ for that very beat (best score first); an unscored photo only
    after them, and only if he is clearly seen AND, on a line naming a team or a time, not in a
    former team's photo or another team's jersey (run 43485568700: Mitchell in a Jazz jersey on
    "Are the Cavs the same failing team?")."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("person_photos", "download", "picture_hash", "image_ok",
                                                      "teams_of", "beat_seconds", "spoken")}
        media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
        media.image_ok = lambda path: True
        media.picture_hash = lambda path: None
        media.teams_of = lambda person: ("cleveland cavaliers", {"utah jazz"})
        self.folder = media.ROOT / "data" / "_test_topup"

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        shutil.rmtree(self.folder, ignore_errors=True)

    @staticmethod
    def ph(title, team="", t="drives", v="C", s="game"):
        return {"kind": "photo", "title": title, "page": "https://commons.wikimedia.org/wiki/File:" + title,
                "url": "u-" + title, "author": "a-" + title, "team": team, "tag": {"v": v, "s": s, "t": t}}

    def test_both_rules(self):
        ok = self.m.topup_ok
        line = "Are the Cavs the same failing team, or should Mitchell tune Chuck out?"
        self.assertFalse(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"), line, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2019", "", "shoots, Jazz jersey"), line, "Donovan Mitchell"))
        self.assertTrue(ok(self.ph("Mitchell back", "current", v="B"), line, "Donovan Mitchell"))    # his answer: from behind is fine
        self.assertFalse(ok(self.ph("Mitchell far", "current", v="S"), line, "Donovan Mitchell"))    # a small figure never
        # a line naming his former team allows that team (his answer); today's team still fits a Cavs line
        utah = "In his Utah years Mitchell carried the Jazz."
        self.assertTrue(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"), utah, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell Cavs", "current", "dribbles, Cavaliers white"), utah, "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2018", "former", "lines up a free throw"), utah, "Donovan Mitchell"))  # which old team? unknown: no
        # a time only ("last year", "now"): today's team or no team
        self.assertFalse(ok(self.ph("Mitchell 2019", "former", "shoots"), "He was great last year.", "Donovan Mitchell"))
        self.assertTrue(ok(self.ph("Mitchell 2024", "current", "shoots"), "He was great last year.", "Donovan Mitchell"))
        self.assertFalse(ok(self.ph("Mitchell 2018", "former", "lines up a free throw"), line, "Donovan Mitchell"))  # no jersey word
        self.assertTrue(ok(self.ph("Mitchell Cavs", "current", "dribbles, Cavaliers white"), line, "Donovan Mitchell"))
        # a line with no team and no time: a former team stays allowed (agreed picture rules)
        self.assertTrue(ok(self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"),
                           "Mitchell fired straight back at Barkley.", "Donovan Mitchell"))
        self.assertFalse(ok({**self.ph("untagged"), "tag": None}, "Mitchell fired back.", "Donovan Mitchell"))

    def test_scored_spares_first_then_safe_unscored(self):
        m = self.m
        line = "Are the Cavs the same failing team, or should Mitchell tune Chuck out?"
        m.spoken = lambda short: [{"say": line}]
        m.beat_seconds = lambda short, i: 12.0          # 4 shots: the first + 3 top-ups
        m.person_photos = lambda person, shown: [self.ph("Mitchell Utah", "former", "free throw, Jazz jersey"),
                                                 self.ph("Mitchell Cavs 2023", "current", "dribbles, Cavaliers white")]
        clip = {"kind": "video", "id": "v1", "title": "Mitchell clip", "page": "pv1", "url": "uv1", "author": "a", "match": 9}
        first = {**self.ph("Mitchell podium", "current"), "file": "data/x.jpg", "match": 8, "alts": [],
                 "_spare": [{**self.ph("Mitchell Cavs 2024", "current"), "match": 8}, clip]}   # best score first
        got = m.fill_empty([first], 1, self.folder, set(), ["Donovan Mitchell"], {"beats": [{"say": line}]})
        titles = [a["title"] for a in got[0]["alts"]]
        self.assertEqual(titles, ["Mitchell clip", "Mitchell Cavs 2024", "Mitchell Cavs 2023"])   # clips too, by score
        self.assertEqual([a.get("match") for a in got[0]["alts"]], [9, 8, None])
        self.assertNotIn("_spare", got[0])

    def test_spares_are_kept_in_the_pick(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('chosen["_spare"] = [', src)
        self.assertIn("scores.get(j, 0) >= SPARE_MIN", src)
        import media
        self.assertEqual(media.SPARE_MIN, 8)       # his answer: only the person the line is about
        self.assertIn("next_spare(it, i, f\"more{k}\") or next_face(i, f\"more{k}\")", src)


class HisAnswersOnTheOlderRules(unittest.TestCase):
    """71. 2026-11-14, his answers on sub-logics of the older code (each was mine): the hook fits
    the first 3-4 seconds (8-12 words at our voice's measured 2.8 words a second); "trade" alone is
    no major turn (62 of 287 real headlines were plain rumors); an article is read up to 6000
    characters; five big newspapers / broadcasters are tier 1."""

    def test_hook_length(self):
        import script
        self.assertEqual((script.HOOK_MIN, script.HOOK_MAX), (8, 12))
        self.assertTrue(script.one_question("Shams says Stephen Curry is out closer to a month."))       # 10
        self.assertFalse(script.one_question("Steph Curry is out at least two weeks, and Gilbert Arenas warns Draymond."))  # 14
        self.assertFalse(script.one_question("Curry is out a month."))                                    # 5

    def test_major_turn(self):
        import editor
        # D96 module 4 (a changed rule): the list is split; an ambiguous word ("Apologize",
        # "fired") is a candidate the editor judges in context ("turn"), so a turn word is either
        t = lambda h: editor.MAJOR_TURN.search(h) or editor.MAJOR_TURN_AMBIG.search(h)     # noqa: E731
        for h in ("Kyrie Irving Trade Rumors Updated by NBA Insider", "Lakers sign center to two-way contract",
                  "Celtics in a fight for the East", "Luka is fine with ankle tweak"):
            self.assertIsNone(t(h), h)
        for h in ("Nick Young: I Apologize Like a Man", "Bassey Rips Smart After Getting Punched",
                  "Jaylen Brown requests a trade", "Smart suspended three games", "Pelicans waive Murray",
                  "Bucks fired Doc Rivers"):
            self.assertIsNotNone(t(h), h)
        self.assertIsNone(t("Draymond fired back at Rivers"))

    def test_article_and_tier1(self):
        import script, sources
        self.assertEqual(script.ARTICLE_CHARS, 6000)
        for p in ("washington post", "los angeles times", "boston globe", "sporting news", "sportsnet"):
            self.assertIn(p, sources.TIER1_PUBLISHERS)
        for p in ("heavy", "fadeaway world", "essentiallysports", "sportskeeda"):
            self.assertNotIn(p, sources.TIER1_PUBLISHERS)

    def test_new_details(self):
        import compliance as C
        src = [{"text": "Barkley said it on the show. Mitchell spoke after the game.", "title": ""}]
        self.assertEqual(C.unsupported_details("Barkley said it on live TV, postgame.", src), [])
        self.assertEqual(sorted(C.unsupported_details("He was in tears courtside, then posted on Instagram.", src)),
                         ["courtside", "in tears", "on social media"])
        self.assertEqual(C.unsupported_details("He laughed in the tunnel.", src), ["tunnel", "laughed"])


if __name__ == "__main__":
    unittest.main()


class FillSaysWhy(unittest.TestCase):
    """72. D32 (run 43513168042): Embiid's last two beats kept one picture for about 12 s and the log
    said nothing. Now every beat left without a new picture prints its reasons, counted; and a
    Short with no recognised person says so at once. Logging only: the pictures do not change."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("person_photos", "download", "picture_hash", "image_ok",
                                                      "teams_of", "beat_seconds", "spoken")}
        media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
        media.image_ok = lambda path: True
        media.picture_hash = lambda path: None
        media.teams_of = lambda person: ("philadelphia 76ers", set())
        self.folder = media.ROOT / "data" / "_test_fillwhy"

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        shutil.rmtree(self.folder, ignore_errors=True)

    def run_fill(self, items, who, photos):
        import io
        from contextlib import redirect_stdout
        m = self.m
        line = "Was Embiid's knee scare real, or did he flop?"
        m.spoken = lambda short: [{"say": line}] * len(items)
        m.beat_seconds = lambda short, i: 6.0
        m.person_photos = lambda person, shown: list(photos)
        out = io.StringIO()
        with redirect_stdout(out):
            got = m.fill_empty(items, len(items), self.folder, set(), who,
                               {"_name": "short_2", "beats": [{"say": line}] * len(items)})
        return got, out.getvalue()

    @staticmethod
    def ph(title, v="C"):
        return {"kind": "photo", "title": title, "page": "https://commons.wikimedia.org/wiki/File:" + title,
                "url": "u-" + title, "author": "a-" + title, "team": "", "tag": {"v": v, "s": "game", "t": "shoots"}}

    def test_no_person_is_said(self):
        got, log = self.run_fill([None, None], [], [])
        self.assertEqual(got, [None, None])
        self.assertIn("[!] short_2: no person recognised in the story", log)
        self.assertIn("[i] short_2 beat 0: no picture (no person recognised x1)", log)
        self.assertIn("[i] short_2 beat 1: no picture (no person recognised x1)", log)

    def test_each_reason_counted(self):
        got, log = self.run_fill([None], ["Joel Embiid"], [self.ph("Joel Embiid far", "S"), self.ph("Joel Embiid crowd", "S")])
        self.assertIsNone(got[0])
        self.assertIn("[i] short_2 beat 0: no picture (face or jersey does not fit x2, no photo of Joel Embiid left x1)", log)
        self.assertNotIn("[!]", log)

    def test_top_ups_missing_say_why(self):
        first = {**self.ph("Joel Embiid dunk"), "file": "data/x.jpg", "match": 8, "alts": []}
        got, log = self.run_fill([first], ["Joel Embiid"], [self.ph("Joel Embiid bench", "S")])
        self.assertEqual(got[0]["alts"], [])
        self.assertIn("[i] short_2 beat 0: 1 of 1 top-ups missing (face or jersey does not fit x1, "
                      "no photo of Joel Embiid left x1)", log)

    def test_a_filled_beat_says_nothing(self):
        got, log = self.run_fill([None], ["Joel Embiid"], [self.ph("Joel Embiid dunk"), self.ph("Joel Embiid free throw")])
        self.assertEqual(got[0]["title"], "Joel Embiid dunk")              # 6 s: the photo and one top-up
        self.assertEqual([a["title"] for a in got[0]["alts"]], ["Joel Embiid free throw"])
        self.assertEqual(log, "")


class ReplayKnowsOwnCategory(unittest.TestCase):
    """73. D33 (run 43513168042): replay.py flagged five photos in Dejounte Murray's OWN Commons
    category ("Dejonte Murray ...") as another man; the pipeline keeps them by rule 56. replay.py
    now applies rule 56 the same way, and still flags a real namesake (Isaiah for Isiah Thomas)."""

    def test_rule_56_in_replay(self):
        import replay
        own = {"kind": "photo", "title": "Dejonte Murray (51913858967).jpg", "person": "Dejounte Murray",
               "own_category": True, "page": "p1"}
        other = {"kind": "photo", "title": "Isaiah Thomas (50639077836).jpg", "person": "Isiah Thomas", "page": "p2"}
        self.assertEqual(replay.picture_findings([own], {}), set())
        self.assertEqual(replay.picture_findings([other], {}),
                         {"another man with his surname: Isaiah Thomas (50639077836).jpg (as Isiah Thomas)"})
        self.assertTrue(replay.picture_findings([{**own, "own_category": False}], {}))


class OnlyRealNamesMakeFragments(unittest.TestCase):
    """74. D35 (his answer 2026-11-16: "only among the confirmed ones"). Run 43513168042: the Title
    Case headline "Hoops Fans Question Joel Embiid's Knee Scare" made the fake name "Question Joel";
    the fragment rule ran BEFORE the Wikipedia check and dropped the real "Joel Embiid" (his first
    name is the fake's last word), then Wikipedia dropped the fakes: nobody, so no top-up photos and
    no jersey law. 11 of 35 kept Shorts lost a real person so (Curry, Luka, Tatum, Embiid...). Now
    Wikipedia first, and the fragment rule only among the names it confirmed."""

    REAL = {"Joel Embiid", "Rudy Gobert", "Ja'Kobe Walter"}

    def people(self, headline, beats, real):
        import media
        with patch.object(media, "real_people", real):
            return media.people({"headline": headline, "beats": [{"say": b} for b in beats]})

    def confirmed(self, names):
        return [n for n in names if n in self.REAL]

    def test_a_fake_name_never_drops_a_real_one(self):
        got = self.people("\u2018Most Egregious Flopper in NBA History,\u2019 \u2018Best LeBron (James) Imitation\u2019 "
                          "\u2014 Hoops Fans Question Joel Embiid\u2019s Knee Scare After Dunk vs. Raptors",   # the run's headline
                          ["Walter's right knee hit his, and Embiid pointed to it."], self.confirmed)
        self.assertEqual(got, ["Joel Embiid"])

    HEAD = "Jayson Tatum Handshake Snub Goes Viral"     # run 43395656602: "Tatum Handshake"

    def test_a_real_name_still_makes_a_fragment(self):
        # were "Tatum Handshake" ever confirmed too, it is still dropped as a fragment of Jayson Tatum
        real = lambda names: [n for n in names if n in {"Jayson Tatum", "Tatum Handshake"}]
        got = self.people(self.HEAD, ["Jayson Tatum walked past."], real)
        self.assertEqual(got, ["Jayson Tatum"])

    def test_wikipedia_down_works_as_before(self):
        got = self.people(self.HEAD, ["Jayson Tatum walked past."], lambda names: None)
        self.assertIn("Jayson Tatum", got)
        self.assertNotIn("Tatum Handshake", got)


class WikipediaCareerJoinsWikidata(unittest.TestCase):
    """75. D34 (run 43513168042; his answers 2026-11-16). Wikidata had only a college team for
    Dejounte Murray and Jeremiah Fears (careers came back empty, so the gate's jersey law checked
    nothing) and no Nets spell for Kyrie Irving. The English Wikipedia infobox (real lines below)
    is now always read too and merged."""

    MURRAY = """{{Infobox basketball biography
| team = New Orleans Pelicans
| draft_team = [[San Antonio Spurs]]
| career_start = 2016
| years1 = {{nbay|2016|start}}–{{nbay|2021|end}}
| team1 = [[San Antonio Spurs]]
| years2 =
| team2 =
| years3 = {{nbay|2022|start}}–{{nbay|2023|end}}
| team3 = [[Atlanta Hawks]]
| years4 = {{nbay|2024|start}}–present
| team4 = [[New Orleans Pelicans]]
}}"""
    KYRIE = """| career_start   = 2011
| years1         = {{nbay|2011|start}}–{{nbay|2016|end}}
| team1          = [[Cleveland Cavaliers]]
| years3         = {{nbay|2019|start}}–{{nbay|2022|end}}
| team3          = [[Brooklyn Nets]]
| years4         = {{nbay|2022|end}}–present
| team4          = [[Dallas Mavericks]]"""
    COACH = """| team = Milwaukee Bucks
| career_start = 1983
| years1 = {{nbay|1983|start}}–{{nbay|1990|end}}
| team1 = [[Atlanta Hawks]]
| coach_years1 = 2024–present
| coach_team1 = [[Milwaukee Bucks]]"""

    def setUp(self):
        import media
        self.m = media
        keep = ("_wikidata", "_teams", "_career", "_team_since", "_nba_debut", "_nba_debut_day", "_wiki_title")
        self.saved = {k: dict(getattr(media, k)) for k in keep}
        self.saved_get = media.get
        for k in keep:
            getattr(media, k).clear()
        P54 = {"Q1": [("Q90", "+2015-01-01T00:00:00Z", True)],                   # Murray: a college only
               "Q2": [("Q91", "+2011-06-23T00:00:00Z", True), ("Q92", "+2017-08-22T00:00:00Z", True),
                      ("Q93", "+2023-02-06T00:00:00Z", False)],                   # Kyrie: no Nets
               "Q3": [("Q94", "+2019-07-01T00:00:00Z", False)],                   # stale: still a Warrior
               "Q4": [],
               "Q5": [("Q94", "+2012-07-01T00:00:00Z", False)], "Q4b": []}                   # a Warrior since 2012
        labels = {"Q90": "Catholic University Cardinals men's basketball", "Q91": "Cleveland Cavaliers",
                  "Q92": "Boston Celtics", "Q93": "Dallas Mavericks", "Q94": "Golden State Warriors"}
        pages = {"Dejounte Murray": self.MURRAY, "Kyrie Irving": self.KYRIE, "Doc Rivers": self.COACH,
                 "Jordan Poole": "| team1 = [[Golden State Warriors]]\n| years1 = 2019–2023\n"
                                 "| team2 = [[Washington Wizards]]\n| years2 = {{nbay|2023|start}}–{{nbay|2024|end}}\n"
                                 "| team3 = [[New Orleans Pelicans]]\n| years3 = {{nbay|2025|start}}–present\n"
                                 "| career_start = 2018",                         # Wikidata says 2019: it stays
                 "Steady Player": "| career_start = 2011\n| team1 = [[Santa Cruz Warriors]]\n| years1 = 2011–2012\n"
                                  "| team2 = [[Golden State Warriors]]\n| years2 = {{nbay|2013|start}}–present",
                 "Euro Star": "| career_start = 2009\n| team1 = [[Real Madrid Baloncesto]]\n| years1 = 2009–present"}

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1]))
            if q.get("action") == "wbgetclaims":
                return json.dumps({"claims": {"P54": [
                    {"mainsnak": {"datavalue": {"value": {"id": t}}}, "rank": "normal",
                     "qualifiers": {"P580": [{"datavalue": {"value": {"time": st}}}],
                                    **({"P582": [{}]} if ended else {})}} for t, st, ended in P54[q["entity"]]]}}).encode()
            if q.get("action") == "wbgetentities":
                return json.dumps({"entities": {i: {"labels": {"en": {"value": labels[i]}}}
                                                for i in q["ids"].split("|") if i in labels}}).encode()
            if q.get("prop") == "revisions":
                return json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": pages[q["titles"]]}}}]}}}}).encode()
            raise OSError("unexpected")
        media.get = get
        for person, item in (("Dejounte Murray", "Q1"), ("Kyrie Irving", "Q2"), ("Jordan Poole", "Q3"), ("Doc Rivers", "Q4"),
                             ("Steady Player", "Q5"), ("Euro Star", "Q4b")):
            media._wikidata[person] = item
            media._wiki_title[person] = person

    def tearDown(self):
        self.m.get = self.saved_get
        for k, v in self.saved.items():
            getattr(self.m, k).clear()
            getattr(self.m, k).update(v)

    def test_murray_gets_his_nba_teams(self):
        m = self.m
        self.assertEqual(m.teams_of("Dejounte Murray"), ("new orleans pelicans", {"san antonio spurs", "atlanta hawks"}))
        self.assertEqual(m.career_teams("Dejounte Murray"), {"new orleans pelicans", "san antonio spurs", "atlanta hawks"})
        self.assertEqual(m._team_since["Q1"], 2024)
        self.assertEqual(m._nba_debut["Q1"], 2016)                 # Wikidata had no NBA start
        import compliance as C
        self.assertFalse(C.jersey_ok("utah jazz", m.career_teams("Dejounte Murray")))   # the law works again

    def test_kyrie_gets_the_nets_and_keeps_wikidata_dates(self):
        m = self.m
        self.assertEqual(m.teams_of("Kyrie Irving"), ("dallas mavericks", {"cleveland cavaliers", "boston celtics", "brooklyn nets"}))
        self.assertEqual(m._team_since["Q2"], 2023)                # same team: Wikidata's dated start stays
        self.assertEqual(m._nba_debut["Q2"], 2011)

    def test_wikipedia_wins_on_the_current_team(self):
        m = self.m
        self.assertEqual(m.teams_of("Jordan Poole")[0], "new orleans pelicans")
        self.assertEqual(m._team_since["Q3"], 2025)
        self.assertIn("golden state warriors", m.teams_of("Jordan Poole")[1])

    def test_a_coach_team_is_not_his_jersey(self):
        m = self.m
        self.assertEqual(m.teams_of("Doc Rivers"), ("", set()))   # played long ago: no current team
        self.assertEqual(m.career_teams("Doc Rivers"), {"atlanta hawks"})

    def test_same_team_keeps_wikidata_and_only_nba_teams_count(self):
        m = self.m
        self.assertEqual(m.teams_of("Steady Player"), ("golden state warriors", set()))   # G League team left out
        self.assertEqual(m._team_since["Q5"], 2012)                # same team: Wikidata's start, not 2013
        m.teams_of("Jordan Poole")
        self.assertEqual(m._nba_debut["Q3"], 2019)                 # Wikidata's debut stays (the page says 2018)

    def test_no_nba_spell_adds_nothing(self):
        m = self.m
        self.assertEqual(m.teams_of("Euro Star"), ("", set()))
        self.assertNotIn("Q4b", m._nba_debut)                      # a career abroad is no NBA debut

    def test_season_years(self):
        self.assertEqual(self.m.nbay_year("{{nbay|2022|end}}–present"), 2023)
        self.assertEqual(self.m.nbay_year("{{nbay|2024|start}}–present"), 2024)
        self.assertEqual(self.m.nbay_year("2019–2023"), 2019)


class WiderNamesForPictures(unittest.TestCase):
    """76. D37 (run 43934705382; his answers 2026-11-16: all three forms, pictures only). "JJ
    Redick Calls Out Lakers' Struggles Despite Luka Doncic": the name finder needed "Abc Def", so
    JJ Redick was nobody and his own lines got Luka's photos (final read: WRONG PICTURE). Kept
    Shorts also lost LeBron James (3) and Shaquille O'Neal (1). Fakes still go at the Wikipedia check."""

    def test_the_three_forms(self):
        import media
        got = media.people_names("JJ Redick, J.J. Redick, LeBron James, DeMar DeRozan, LaMelo Ball, "
                                 "OG Anunoby, Shaquille O'Neal and D'Angelo Russell")
        for n in ("JJ Redick", "J.J. Redick", "LeBron James", "DeMar DeRozan", "LaMelo Ball", "OG Anunoby",
                  "Shaquille O'Neal", "D'Angelo Russell"):
            self.assertIn(n, got)
        self.assertEqual(media.people_names("The LeBron era, Lakers LeBron"), set())   # a stopword or a team: never a name

    def test_redick_is_in_his_short(self):
        import media
        real = lambda names: [n for n in names if n in {"JJ Redick", "Luka Doncic"}]
        with patch.object(media, "real_people", real):
            got = media.people({"headline": "JJ Redick Calls Out Lakers' Struggles Despite Luka Doncic, LA's 12-2 "
                                            "Record After Win vs. Suns", "beats": [{"say": "Redick called it a trend."}]})
        self.assertEqual(got, ["JJ Redick", "Luka Doncic"])   # a tie: first in the headline leads (D40)

    def test_the_collector_is_unchanged(self):
        import collect
        self.assertNotIn("JJ Redick", collect.names("JJ Redick Calls Out Lakers"))
        self.assertNotIn("LeBron James", collect.names("LeBron James scores 40"))


class OwnCategoryTopUps(unittest.TestCase):
    """77. D39 (run 43934705382; his answer 2026-11-16). Murray's beats 2, 4 and 5 ran out of top-up
    photos (D32 log) while 9 of his own-category photos ("Dejonte Murray (...)", face or back seen)
    were never used: a top-up needed his exact first name in the title. Rule 56 now counts here too."""

    def test_rule_56_for_top_ups(self):
        import media
        own = {"title": "Dejonte Murray (51914823201).jpg", "own_category": True}
        self.assertTrue(media.his_by_title(own, "Dejounte Murray"))
        self.assertFalse(media.his_by_title({**own, "own_category": False}, "Dejounte Murray"))
        self.assertFalse(media.his_by_title({"title": "LaMelo Ball and Dejonte Murray (51915389270).jpg",
                                             "own_category": True}, "Dejounte Murray"))      # a group: no
        self.assertTrue(media.his_by_title({"title": "Dejounte Murray 2022.jpg"}, "Dejounte Murray"))
        self.assertFalse(media.unjudged_ok({**own, "kind": "photo"}, ["Dejounte Murray"]))   # that path unchanged

    def test_the_pool_uses_it(self):
        import media
        ph = lambda t, own: {"kind": "photo", "title": t, "page": "p-" + t, "url": "u", "own_category": own,
                             "tag": {"v": "C", "s": "game", "t": "dribbles"}, "hoops": True}
        pool = [ph("Dejonte Murray (1).jpg", True), ph("Dejonte Murray (2).jpg", False)]
        with patch.object(media, "photos", lambda person: pool):
            got = media.person_photos("Dejounte Murray", set())
        self.assertEqual([c["title"] for c in got], ["Dejonte Murray (1).jpg"])


class ScoredPhotosFitTheLine(unittest.TestCase):
    """78. D38 (run 43934705382; his answers 2026-11-16): a photo Claude scored must also fit the
    team or time its line names (the top-ups' rule): Jalen Green in a Rockets jersey on "Phoenix
    reportedly has interest", JJ Redick in Magic and 76ers jerseys on "his own Lakers". Replayed on
    309 scored photos: two gaps of the rule hit good photos and are closed: D41 a team word counts
    only with a capital and not as a word of a story person's name; D42 a year before his current
    spell began is his past ("They won the 2016 title" may show Kyrie as a Cavalier)."""

    def setUp(self):
        import media
        self.m = media
        self.saved = (media.teams_of, dict(media._wikidata), dict(media._team_since))
        cur = {"Jalen Green": ("phoenix suns", 2025), "Kyrie Irving": ("dallas mavericks", 2023), "JJ Redick": ("", 0)}
        media.teams_of = lambda p: (cur.get(p, ("", 0))[0], set())
        for p, (_, y) in cur.items():
            media._wikidata[p] = "Q-" + p
            if y:
                media._team_since["Q-" + p] = y

    def tearDown(self):
        m, s = self.m, self.saved
        m.teams_of = s[0]
        m._wikidata.clear(); m._wikidata.update(s[1])
        m._team_since.clear(); m._team_since.update(s[2])

    @staticmethod
    def ph(title, t, team=""):
        return {"kind": "photo", "title": title, "team": team, "tag": {"v": "C", "s": "game", "t": t}}

    def test_the_run_cases(self):
        fits = self.m.team_fits
        suns = "Phoenix reportedly has interest... but a Suns source told The Athletic there's no talk of a Jalen Green swap."
        self.assertFalse(fits(self.ph("Jalen Green with the Houston Rockets", "shoots, Rockets jersey", "former"), suns, "Jalen Green"))
        self.assertTrue(fits(self.ph("Jalen Green 2026", "drives, Suns jersey", "current"), suns, "Jalen Green"))
        lakers = "JJ Redick just called out his own Lakers after eight straight wins."
        self.assertFalse(fits(self.ph("J. J. Redick.jpg", "shoots, Magic jersey"), lakers, "JJ Redick", ["JJ Redick"]))
        self.assertTrue(fits({"kind": "video", "title": "clip"}, lakers, "JJ Redick"))          # a clip: no jersey read

    def test_d41_a_team_word_needs_a_capital_and_is_no_name(self):
        t = self.m.teams_in
        self.assertEqual(t("But it got worse: the headlines called him Tragic Magic.", ["Magic Johnson"]), set())
        self.assertEqual(t("in the heat of it, for 5 bucks"), set())
        self.assertEqual(t("The Heat beat the Bucks"), {"miami heat", "milwaukee bucks"})
        self.assertEqual(t("Are the Cavs the same?"), {"cleveland cavaliers"})
        self.assertEqual(t("the 76ers lost"), {"philadelphia 76ers"})

    def test_d42_a_past_year_is_his_past(self):
        m = self.m
        line = "They won the 2016 title, but Kyrie requested a 2017 trade."
        cavs = self.ph("Kyrie Irving 2015", "dribbles, Cavaliers jersey")
        self.assertFalse(m.names_a_time(line, "Kyrie Irving"))
        self.assertTrue(m.team_fits(cavs, line, "Kyrie Irving"))
        self.assertTrue(m.names_a_time("In 2024 he carried Dallas.", "Kyrie Irving"))      # from 2023 on: today's team
        self.assertFalse(m.team_fits(cavs, "In 2024 he carried them.", "Kyrie Irving"))
        self.assertTrue(m.names_a_time("Back in 2016.", "Nobody Known"))                   # start unknown: as before
        self.assertTrue(m.names_a_time("He is great now.", "Kyrie Irving"))

    def test_his_spell_start_is_looked_up(self):
        m = self.m
        m._team_since.clear()
        m.teams_of = lambda p: (m._team_since.__setitem__("Q-" + p, 2023), ("dallas mavericks", set()))[1]
        cavs = self.ph("Kyrie Irving 2015", "dribbles, Cavaliers jersey")
        self.assertTrue(m.team_fits(cavs, "They won the 2016 title.", "Kyrie Irving"))

    def test_every_scored_path_uses_it(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn("order = [j for j in order if team_ok(j)]", src)
        self.assertIn("scores.get(j, 0) >= ALT_MIN and team_ok(j)]", src)
        self.assertIn("scores.get(j, 0) >= SPARE_MIN and team_ok(j)]", src)
        self.assertIn("team_fits(cands[j], line, photo_owner(cands[j], who4), who4)", src)
        self.assertIn('topup_ok(c, lines[i] if i < len(lines) else "", person, who or [])', src)

    def test_photo_owner(self):
        o = self.m.photo_owner
        self.assertEqual(o({"tag": {"who": "Jalen Green"}, "title": "x"}, []), "Jalen Green")
        self.assertEqual(o({"title": "Jalen Green 2022.jpg"}, ["Dejounte Murray", "Jalen Green"]), "Jalen Green")
        self.assertEqual(o({"title": "Murray and Green.jpg"}, ["Dejounte Murray", "Jalen Green"]), "")


class PhotoOwnNameIsNoTeam(unittest.TestCase):
    """79. D43 (his answer 2026-11-16). Run 43262308476: "But it got worse: the headlines called him
    Tragic Magic." The script never says "Magic Johnson" in full, so he was no story person and
    D41 could not see the nickname; his Lakers photo would go as "not the Orlando Magic". Now the
    photo's own person (the tagger's "who", which until now never reached the photo) counts too."""

    def test_the_tag_owner_reaches_the_photo(self):
        import photo_tags
        c = {}
        photo_tags._apply(c, {"v": "S", "s": "game", "e": "intense", "t": "jumps for rebound in Lakers jersey",
                              "who": "Magic Johnson", "at": "2026-11-12"})
        self.assertEqual(c["tag"]["who"], "Magic Johnson")
        self.assertNotIn("at", c["tag"])

    def test_tragic_magic(self):
        import media
        photo = {"kind": "photo", "title": "Magic Johnson and Sam Bowie, 1985.jpg", "team": "",
                 "tag": {"v": "S", "s": "game", "t": "jumps for rebound in Lakers jersey", "who": "Magic Johnson"}}
        line = "But it got worse: the headlines called him Tragic Magic."
        owner = media.photo_owner(photo, ["Larry Bird"])
        self.assertEqual(owner, "Magic Johnson")
        with patch.object(media, "teams_of", lambda p: ("", set())):
            self.assertTrue(media.team_fits(photo, line, owner, ["Larry Bird"]))
            self.assertFalse(media.team_fits(photo, "The Celtics beat them.", owner, ["Larry Bird"]))   # another team still counts


class TieGoesToTheHeadline(unittest.TestCase):
    """80. D40 (his answer 2026-11-16): the story's people are ranked by how often they are named; a
    tie had no fixed order (set order), so the main person could change between runs."""

    def test_first_in_the_headline_leads(self):
        import media
        real = lambda names: [n for n in names if n in {"JJ Redick", "Luka Doncic"}]
        for head, first in (("JJ Redick Calls Out Lakers Despite Luka Doncic", "JJ Redick"),
                            ("Luka Doncic Shrugs Off JJ Redick", "Luka Doncic")):
            for _ in range(5):
                with patch.object(media, "real_people", real):
                    self.assertEqual(media.people({"headline": head, "beats": []})[0], first)


class AMagazineIsNoPerson(unittest.TestCase):
    """81. D36 (his answer 2026-11-16). Run 43080115985 searched photos of "Sports Illustrated": its
    Wikipedia description "American sports magazine" matched "sports". Checked on the live
    descriptions of every name in the kept runs: only Sports Illustrated goes."""

    def test_descriptions(self):
        import media
        for d in ("American sports magazine", "American sports website", "Professional basketball league",
                  "American sports television network", "American basketball team", "American media company"):
            self.assertFalse(media.is_person_desc(d), d)
        for d in ("American basketball player (born 1996)", "American sportswriter for ESPN.com (born 1978)",
                  "American basketball coach (born 1984)", "Nigerian-Canadian sports executive (born 1970)",
                  "American former basketball player and sports analyst (born 1972)"):
            self.assertTrue(media.is_person_desc(d), d)

    def test_the_wikipedia_check_uses_it(self):
        import media
        pages = {"1": {"title": "Sports Illustrated", "pageprops": {"wikibase-shortdesc": "American sports magazine"}},
                 "2": {"title": "Jordan Poole", "pageprops": {"wikibase-shortdesc": "American basketball player (born 1999)"}}}
        answer = json.dumps({"query": {"pages": pages}}).encode()
        names = ["Sports Illustrated", "Jordan Poole"]
        for n in names:
            media._person_cache.pop(n, None)
        with patch.object(media, "get", lambda url, timeout=30: answer):
            self.assertEqual(media.real_people(names), ["Jordan Poole"])
        for n in names:
            media._person_cache.pop(n, None)


class NationalColoursOnlyOnNationalLines(unittest.TestCase):
    """82. D45 (run 43945813466; his answer 2026-11-16): five FIBA photos of RJ Barrett in Canada
    colours (one game, Germany v Canada 2023) filled the Knicks-Raptors lines. Checked on all 1518
    cached tags: 62 count as national-team photos, every one really is (USA, Turkey, Canada...)."""

    def test_rule(self):
        import media
        barrett = {"kind": "photo", "title": "2023-08-09 Deutschland gegen Kanada (Basketball-Länderspiel) by Sandro Halank–063.jpg",
                   "own_category": True, "team": "", "tag": {"v": "C", "s": "game", "t": "stares at camera, Canada jersey"}}
        with patch.object(media, "teams_of", lambda p: ("new york knicks", set())):
            self.assertFalse(media.team_fits(barrett, "So he stayed, hit a three, and the Knicks won in overtime.", "RJ Barrett"))
            self.assertFalse(media.team_fits(barrett, "I think being knocked down is a foul, not a flop.", "RJ Barrett"))
            self.assertTrue(media.team_fits(barrett, "He played for Team Canada with Shai.", "RJ Barrett"))
            self.assertTrue(media.team_fits(barrett, "Back at the Olympics, he was the star.", "RJ Barrett"))
            knicks = {**barrett, "tag": {"v": "C", "s": "game", "t": "drives in Knicks jersey"}}
            self.assertTrue(media.team_fits(knicks, "I think being knocked down is a foul, not a flop.", "RJ Barrett"))
        for t, nat in (("dunks in a USA jersey", True), ("claps in Team USA shirt", True), ("stands, Turkey jersey 23", True),
                       ("smiles upward, FIBA World Cup 2023 lanyard", True), ("drives in Knicks jersey", False),
                       ("stands in Lakers warmup", False)):
            self.assertEqual(media.national_photo({"tag": {"t": t}}), nat, t)


class GateKnowsOwnCategory(unittest.TestCase):
    """83. D44 (run 43945813466; his answer 2026-11-16): D39 lets an own-category photo fill whatever
    its title says, but the gate still held "a picture not judged and not named after the story's
    people" (RJ Barrett's own-category photos): my D39 missed the gate. Now the gate mirrors it."""

    def test_gate_mirrors_d39(self):
        import compliance as C
        import gate, media
        self.assertEqual(gate.GROUP_TITLE.pattern, media.GROUP_TITLE.pattern)
        own = {"kind": "photo", "match": None, "own_category": True, "license": "CC BY-SA 4.0",
               "page": "https://commons.wikimedia.org/wiki/File:x.jpg", "author": "Sandro Halank",
               "title": "2023-08-09 Deutschland gegen Kanada (Basketball-Länderspiel) by Sandro Halank–063.jpg"}
        flags = {"people": ["RJ Barrett"]}
        self.assertEqual(gate.check_visuals([own], flags)[0], C.PASS)
        self.assertEqual(gate.check_visuals([{**own, "own_category": False}], flags)[0], C.REVIEW)
        self.assertEqual(gate.check_visuals([{**own, "title": "LaMelo Ball and Dejonte Murray.jpg"}],
                                            {"people": ["Dejounte Murray"]})[0], C.REVIEW)


class StephenASmithIsAPerson(unittest.TestCase):
    """84. D46 + D47 (run 43945813466; his answers 2026-11-16/17): "Stephen A. Smith defends LeBron
    James": the name finder had no "first + initial + last" form, and Wikipedia calls him "American TV
    personality (born 1967)", which was no person; his own line got a LeBron photo."""

    def test_found_and_real(self):
        import media
        self.assertIn("Stephen A. Smith", media.people_names("Stephen A. Smith defends LeBron James"))
        self.assertNotIn("The A. Team", media.people_names("The A. Team"))
        self.assertTrue(media.is_person_desc("American TV personality (born 1967)"))
        for d in ("American sports commentator", "American podcast host (born 1980)", "American podcaster"):
            self.assertTrue(media.is_person_desc(d), d)
        for d in ("2014 studio album by Bulletrain", "African-American-owned multimedia company",
                  "Residence and workplace of the US president"):
            self.assertFalse(media.is_person_desc(d), d)
        real = lambda names: [n for n in names if n in {"Stephen A. Smith", "LeBron James"}]
        with patch.object(media, "real_people", real):
            got = media.people({"headline": "Stephen A. Smith defends LeBron James after Trump calls him a disgrace",
                                "beats": [{"say": "Stephen A. said no."}]})
        self.assertEqual(got, ["Stephen A. Smith", "LeBron James"])


class HookNamesPeople(unittest.TestCase):
    """85. D48 (run 44034519940; his answer 2026-11-17): "Jayson Tatum just called Steve Kerr's Olympic
    benching of him fishy." The beats only say "Tatum", and people() did not read the hook, so Tatum
    was no person in his own Short (no jersey law, no top-ups for him)."""

    def test_hook_counts(self):
        import media
        real = lambda names: [n for n in names if n in {"Jayson Tatum", "Steve Kerr", "Kevin Durant"}]
        short = {"headline": "Steve Kerr rightfully beginning to tinker with Warriors' lineup",
                 "hook": {"text": "Jayson Tatum just called Steve Kerr's Olympic benching of him fishy."},
                 "beats": [{"say": "Tatum told Boardroom Kerr said to be patient because Kevin Durant was back."}]}
        with patch.object(media, "real_people", real):
            got = media.people(short)
            self.assertEqual(got, ["Steve Kerr", "Jayson Tatum", "Kevin Durant"])
            self.assertEqual(media.people({**short, "hook": "Jayson Tatum is mad."})[1], "Jayson Tatum")   # a plain string too


class TheLinesManOnly(unittest.TestCase):
    """86. D49 + D50 + D51 (run 44034519940; his answers 2026-11-17). Draymond's photos stood on
    "Lendeborg sat with a towel over his head" (Lendeborg has only Michigan photos, PRE-NBA), and in
    kept runs Jaylen Brown stood on Paul George's line. Now a line naming a man with an NBA career
    shows only the men it names; a rookie with no usable NBA photo may be shown in college on his
    own line naming no team or time; a line names a man by first OR last name ("Kyrie has...")."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: getattr(media, k) for k in ("photos", "download", "picture_hash", "image_ok", "teams_of",
                                                      "career_teams", "beat_seconds", "spoken")}
        media.download = lambda url, path, timeout=60: (Path(path).write_text("x"), True)[1]
        media.image_ok = lambda path: True
        media.picture_hash = lambda path: None
        media.teams_of = lambda person: ("golden state warriors", set())
        media.career_teams = lambda p: {"golden state warriors"} if p in ("Yaxel Lendeborg", "Draymond Green") else set()
        media.beat_seconds = lambda short, i: 2.0
        self.folder = media.ROOT / "data" / "_test_linesman"

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.m, k, v)
        shutil.rmtree(self.folder, ignore_errors=True)

    @staticmethod
    def ph(title, team="", v="C", t="sits on bench"):
        return {"kind": "photo", "title": title, "page": "p-" + title, "url": "u-" + title, "author": "a",
                "team": team, "hoops": True, "tag": {"v": v, "s": "game", "t": t}}

    def fill(self, line, pools, who):
        m = self.m
        m.spoken = lambda short: [{"say": line}]
        m.photos = lambda person: pools.get(person, [])
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            return m.fill_empty([None], 1, self.folder, set(), who, {"_name": "t", "beats": [{"say": line}]})[0]

    def test_rookie_gets_his_college_photo_not_a_teammate(self):
        pools = {"Yaxel Lendeborg": [self.ph("20260211 Yaxel Lendeborg 05.jpg", "pre-nba")],
                 "Draymond Green": [self.ph("Draymond Green 2022.jpg")]}
        got = self.fill("Lendeborg sat with a towel over his head.", pools, ["Draymond Green", "Yaxel Lendeborg"])
        self.assertEqual(got["title"], "20260211 Yaxel Lendeborg 05.jpg")
        self.assertTrue(got["college_only"])
        import final_read
        self.assertIn("PRE-NBA, NO NBA PHOTO EXISTS", final_read.picture_line(got))

    def test_college_photo_never_on_a_team_or_time_line(self):
        pools = {"Yaxel Lendeborg": [self.ph("20260211 Yaxel Lendeborg 05.jpg", "pre-nba")],
                 "Draymond Green": [self.ph("Draymond Green 2022.jpg")]}
        self.assertIsNone(self.fill("Tonight Lendeborg scored 28 for the Warriors.", pools,
                                    ["Draymond Green", "Yaxel Lendeborg"]))      # the picture stays longer

    def test_an_nba_photo_comes_first(self):
        pools = {"Yaxel Lendeborg": [self.ph("Yaxel Lendeborg Warriors 2026.jpg"),
                                     self.ph("20260211 Yaxel Lendeborg 05.jpg", "pre-nba")]}
        got = self.fill("Lendeborg sat with a towel over his head.", pools, ["Yaxel Lendeborg"])
        self.assertEqual(got["title"], "Yaxel Lendeborg Warriors 2026.jpg")
        self.assertNotIn("college_only", got)

    def test_college_only_when_no_nba_photo_at_all(self):
        nba = self.ph("Yaxel Lendeborg Warriors 2026.jpg")
        pools = {"Yaxel Lendeborg": [nba, self.ph("20260211 Yaxel Lendeborg 05.jpg", "pre-nba")]}
        m = self.m
        lines = ["Lendeborg scored 28.", "Lendeborg sat with a towel over his head."]
        m.spoken = lambda short: [{"say": x} for x in lines]
        m.photos = lambda person: pools.get(person, [])
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):                       # his NBA photo is already on beat 0
            got = m.fill_empty([{**nba, "file": "data/x.jpg", "match": 8, "alts": []}, None], 2, self.folder, set(),
                               ["Yaxel Lendeborg"], {"_name": "t", "beats": [{}, {}]})
        self.assertIsNone(got[1])                                  # he HAS an NBA photo: no college one

    def test_college_photo_must_show_him(self):
        pools = {"Yaxel Lendeborg": [self.ph("20260211 Nick Martinelli and Yaxel Lendeborg.jpg", "pre-nba", v="O"),
                                     self.ph("20260211 Yaxel Lendeborg 01.jpg", "pre-nba", v="S")]}
        self.assertIsNone(self.fill("Lendeborg sat with a towel over his head.", pools, ["Yaxel Lendeborg"]))

    def test_reporters_line_may_show_the_player(self):
        pools = {"Draymond Green": [self.ph("Draymond Green 2022.jpg")]}
        got = self.fill("Shams Charania told ESPN it's a checkpoint.", pools, ["Shams Charania", "Draymond Green"])
        self.assertEqual(got["title"], "Draymond Green 2022.jpg")

    def test_first_name_counts(self):
        m = self.m
        self.assertTrue(m.names_him("Is Draymond right to protect him?", "Draymond Green"))
        self.assertTrue(m.names_him("Kyrie has a $42.4 million deal.", "Kyrie Irving"))
        self.assertTrue(m.names_him("Green said no.", "Draymond Green"))
        self.assertFalse(m.names_him("Draymonds everywhere.", "Draymond Green"))   # a whole word only
        self.assertFalse(m.names_him("Lendeborg sat.", "Draymond Green"))
        pools = {"Draymond Green": [self.ph("Draymond Green 2022.jpg")], "Yaxel Lendeborg": []}
        got = self.fill("Is Draymond right to protect Lendeborg?", pools, ["Yaxel Lendeborg", "Draymond Green"])
        self.assertEqual(got["title"], "Draymond Green 2022.jpg")    # Draymond is named by his first name


class OnePageOnePerson(unittest.TestCase):
    """87. D52 (run 43288011054; his answer 2026-11-17): "Stephen Curry" and "Steph Curry" (one
    Wikipedia page) took two of the four places and Paolo Banchero fell out."""

    def test_the_more_named_one_stays(self):
        import media
        pages = {"Stephen Curry": "Stephen Curry", "Steph Curry": "Stephen Curry", "Alperen Sengun": "Alperen Şengün",
                 "Steve Kerr": "Steve Kerr", "Paolo Banchero": "Paolo Banchero"}

        def real(names):
            media._wiki_title.update({n: pages[n] for n in names if n in pages})
            return [n for n in names if n in pages]
        short = {"headline": "Stephen Curry and Alperen Sengun trade words",
                 "beats": [{"say": "Stephen Curry said it. Steph Curry laughed. Steve Kerr agreed. Paolo Banchero watched."}]}
        try:
            with patch.object(media, "real_people", real):
                got = media.people(short)
        finally:
            for n in pages:
                media._wiki_title.pop(n, None)
        self.assertEqual(got, ["Stephen Curry", "Alperen Sengun", "Steve Kerr", "Paolo Banchero"])


class SameHeadlineIsARepeat(unittest.TestCase):
    """88. D53 (run 44040546534; his answer 2026-11-17): "Steve Kerr rightfully beginning to tinker
    with Warriors' Steph Curry-less lineup" was made again 47 minutes after the first; the editor
    called it "a new development" and the feud guard needs two people in the headline."""

    HEAD = "Steve Kerr rightfully beginning to tinker with Warriors' Steph Curry-less lineup"

    def test_repeat_whatever_the_editor_says(self):
        import editor
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        made = [{"time": (now - timedelta(minutes=47)).isoformat(), "headline": self.HEAD}]
        topics = [{"headline": self.HEAD}, {"headline": "Draymond Green calls out the refs"}]
        answer = json.dumps({"ranked": [{"id": 0, "repeat": False, "why": "a new development", "kind": "player_vs_player"},
                                        {"id": 1, "repeat": False, "why": "", "kind": "player_vs_player"}],
                             "shorts": [0, 1]})
        with patch.object(editor, "made_recently", lambda: made):
            data = editor.parse(answer, 2, topics)
        self.assertTrue(data["ranked"][0]["repeat"])
        self.assertEqual(data["shorts"], [1])

    def test_only_seven_days(self):
        import editor
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        topic = {"headline": self.HEAD}
        self.assertTrue(editor.same_headline_made(topic, [{"time": (now - timedelta(days=6)).isoformat(), "headline": self.HEAD}]))
        self.assertFalse(editor.same_headline_made(topic, [{"time": (now - timedelta(days=8)).isoformat(), "headline": self.HEAD}]))
        self.assertFalse(editor.same_headline_made(topic, [{"time": now.isoformat(), "headline": "Steve Kerr benches Kuminga"}]))


class DeadAddressOnce(unittest.TestCase):
    """89. D54 (run 44040546534; his answer 2026-11-17): Lindsey_Harding.jpg (404) was downloaded 8
    times in one Short."""

    def test_once(self):
        import io
        import media
        from contextlib import redirect_stdout
        calls = []

        def get(url, timeout=30):
            calls.append(url)
            raise OSError("HTTP Error 404: Not Found")
        url = "https://upload.wikimedia.org/wikipedia/commons/0/0d/Lindsey_Harding.jpg"
        media._dead_urls.discard(url)
        try:
            with patch.object(media, "get", get), redirect_stdout(io.StringIO()):
                path = media.ROOT / "data" / "_test_dead.jpg"
                self.assertFalse(media.download(url, path))
                self.assertFalse(media.download(url, path))
                self.assertFalse(media.download(url, path))
            self.assertEqual(calls, [url])
        finally:
            media._dead_urls.discard(url)


class RetiredPlaysForNobody(WikipediaCareerJoinsWikidata):
    """90. D56 (run 44040546534; his answer 2026-11-17). Wikidata ends JJ Redick's spells with an open
    76ers spell from 2017, so a 76ers photo was "current"; his infobox lists six playing spells, none
    "present" (career_end 2021; the Lakers only as coach). Checking it on all 55 people of the kept
    runs found a bug of mine in D34: an empty field ("| career_end =") swallowed the next line, so
    Draymond Green's "years1 = {{nbay|2012|start}}-present" was lost."""

    REDICK = """| team = Los Angeles Lakers
| career_start = 2006
| career_end = 2021
| years1 = {{nbay|2006|start}}–{{nbay|2012|end}}
| team1 = [[Orlando Magic]]
| years4 = {{nbay|2017|start}}–{{nbay|2018|end}}
| team4 = [[Philadelphia 76ers]]
| coach_years1 = {{nbay|2024|start}}–present
| coach_team1 = [[Los Angeles Lakers]]"""
    DRAYMOND = """| team = Golden State Warriors
| career_start = 2012
| career_end =
| years1 = {{nbay|2012|start}}–present
| team1 = [[Golden State Warriors]]"""

    def test_redick_plays_for_nobody(self):
        m = self.m
        self.assertEqual(m.wiki_career(self.REDICK)[1], "")
        m._wikidata["JJ Redick"] = "Q3"          # Wikidata: an open spell (here the Warriors, from 2019)
        m._wiki_title["JJ Redick"] = "Jordan Poole"
        saved = m.get

        def get(url, timeout=30):
            if "prop=revisions" in url:
                return json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": self.REDICK}}}]}}}}).encode()
            return saved(url, timeout)
        m.get = get
        self.assertEqual(m.teams_of("JJ Redick"), ("", set()))
        self.assertNotIn("Q3", m._team_since)

    def test_an_empty_field_swallows_nothing(self):
        teams, current, since, start = self.m.wiki_career(self.DRAYMOND)
        self.assertEqual((teams, current, since, start), ({"golden state warriors"}, "golden state warriors", 2012, 2012))


class HistoricBeefNeedsNoOwnArticle(unittest.TestCase):
    """91. D57 (run 44047143877; his answer 2026-11-17): on a weak day both historic beefs (Dwight
    Howard vs Kobe, Kawhi vs the Spurs) were skipped with "the story's own article could not be read":
    the exemption read judged["evergreen"], but fill_with_evergreen marks the TOPIC. No Short was made."""

    def _build(self, topic):
        import script
        calls = []

        class Stop(Exception):
            pass

        def ask(prompt, model=""):
            calls.append(1)
            raise Stop()
        sources = [{"publisher": "ESPN", "title": "t", "text": "x" * 5000, "tier": 1, "main": False}]
        with patch.object(script, "gather_sources", lambda t, e, i: sources), patch.object(script, "ask_claude", ask):
            editor = {"topics": [topic], "ranked": [{"id": 0, "nba": True, "kind": "player_vs_player"}]}
            try:
                script.build_short(1, 0, editor, "voice", {"hooks": [{"name": "x", "shape": "y", "example": "z"}], "rules": []})
            except Stop:
                return "reached Claude"
            except ValueError as exc:
                return str(exc)
        return "built"

    def test_beef_goes_on_fresh_story_stops(self):
        beef = {"headline": "Dwight Howard vs Kobe Bryant (back in the news)", "items": [], "verified": True,
                "star_names": ["Dwight Howard", "Kobe Bryant"], "evergreen": "Dwight Howard vs Kobe Bryant"}
        self.assertEqual(self._build(beef), "reached Claude")
        fresh = {k: v for k, v in beef.items() if k != "evergreen"}
        self.assertIn("own article could not be read", self._build(fresh))


class PastYearPastTeam(unittest.TestCase):
    """92. D60 (run 44053022347; his answer 2026-11-17). Howard (retired: no team now, D56) in Hawks
    colours on "He won the 2020 title as a rotation player": a year was a time with no team to match,
    so anything passed. Now a past year allows only the jersey of a team he played for that year."""

    HOWARD = """| years1 = {{nbay|2004|start}}–{{nbay|2011|end}}
| team1 = [[Orlando Magic]]
| years4 = {{nbay|2016|full=y}}
| team4 = [[Atlanta Hawks]]
| years7 = {{nbay|2019|full=y}}
| team7 = [[Los Angeles Lakers]]
| years8 = {{nbay|2020|full=y}}
| team8 = [[Philadelphia 76ers]]"""

    def setUp(self):
        import media
        self.m = media
        self.saved = (dict(media._spells), dict(media._wikidata), dict(media._team_since))
        media._wikidata.update({"Dwight Howard": "Q-DH", "Kyrie Irving": "Q-KI"})
        media._spells["Q-DH"] = media.wiki_spells(self.HOWARD)
        media._spells["Q-KI"] = [("cleveland cavaliers", 2011, 2017), ("boston celtics", 2017, 2019),
                                 ("brooklyn nets", 2019, 2023), ("dallas mavericks", 2023, 9999)]
        media._team_since["Q-KI"] = 2023

    def tearDown(self):
        m = self.m
        for d, v in zip((m._spells, m._wikidata, m._team_since), self.saved):
            d.clear(); d.update(v)

    @staticmethod
    def ph(t):
        return {"kind": "photo", "title": "x", "team": "", "tag": {"v": "C", "s": "game", "t": t}}

    def test_spells_are_kept_from_the_infobox(self):
        m = self.m
        m._spells.pop("Q-DH2", None)
        answer = json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": self.HOWARD}}}]}}}}).encode()
        saved = (dict(m._wiki_title), dict(m._teams), dict(m._career))
        try:
            m._wiki_title["Dwight Howard 2"] = "Dwight Howard"
            with patch.object(m, "get", lambda url, timeout=30: answer):
                m.add_wiki_career("Dwight Howard 2", "Q-DH2")
            self.assertIn(("atlanta hawks", 2016, 2017), m._spells["Q-DH2"])
        finally:
            for d, v in zip((m._wiki_title, m._teams, m._career), saved):
                d.clear(); d.update(v)
            m._spells.pop("Q-DH2", None)

    def test_spell_years(self):
        sy = self.m.spell_years
        self.assertEqual(sy("{{nbay|2019|full=y}}"), (2019, 2020))
        self.assertEqual(sy("{{nbay|2006|start}}–{{nbay|2012|end}}"), (2006, 2013))
        self.assertEqual(sy("{{nbay|2012|end}}"), (2013, 2013))
        self.assertEqual(sy("{{nbay|2023|start}}–present"), (2023, 9999))
        self.assertEqual(sy("2019–2023"), (2019, 2023))

    def test_howard_2020(self):
        m = self.m
        line = "I think the fix was a smaller Dwight. He won the 2020 title as a rotation player."
        with patch.object(m, "teams_of", lambda p: ("", set())):
            self.assertFalse(m.team_fits(self.ph("dunks, Hawks jersey"), line, "Dwight Howard"))
            self.assertTrue(m.team_fits(self.ph("smiles on court, Lakers jersey"), line, "Dwight Howard"))
            self.assertTrue(m.team_fits(self.ph("dunks, 76ers jersey"), line, "Dwight Howard"))   # 2020-21: either half
            self.assertTrue(m.team_fits(self.ph("holds ball looking aside"), line, "Dwight Howard"))  # no jersey read
            self.assertTrue(m.team_fits(self.ph("dunks, Hawks jersey"), "Kobe tore an Achilles.", "Dwight Howard"))

    def test_active_player_d42_still_holds(self):
        m = self.m
        line = "They won the 2016 title, but Kyrie requested a 2017 trade."
        with patch.object(m, "teams_of", lambda p: ("dallas mavericks", set())):
            self.assertTrue(m.team_fits({**self.ph("dribbles, Cavaliers jersey"), "team": "former"}, line, "Kyrie Irving"))
            self.assertFalse(m.team_fits(self.ph("drives, Mavericks jersey"), line, "Kyrie Irving"))
            self.assertTrue(m.team_fits(self.ph("drives, Mavericks jersey"), "In 2024 he carried Dallas.", "Kyrie Irving"))


class CityIsTheTeam(unittest.TestCase):
    """93. D59 (run 44053022347; his answers 2026-11-17): LeBron in a "Cleveland jersey" on "LeBron,
    now with the 76ers" and on "Philly is 12 and 3": the city named no team. 16 cached jersey tags and
    31 kept lines name a team only by city; "New York Times" is in 26 kept lines."""

    def test_lines(self):
        t = __import__("media").teams_in
        self.assertEqual(t("He is at career lows at 41, but Philly is 12 and 3."), {"philadelphia 76ers"})
        self.assertEqual(t("Kyrie is 34, and Dallas is 7 and 5 with him."), {"dallas mavericks"})
        self.assertEqual(t("He was traded to New York."), {"new york knicks"})
        self.assertEqual(t("Oklahoma City won."), {"oklahoma city thunder"})
        self.assertEqual(t("OKC is rolling."), {"oklahoma city thunder"})
        self.assertEqual(t("The New York Times reported it, the Boston Globe too."), set())
        self.assertEqual(t("Per the New York Post, Boston won."), {"boston celtics"})
        self.assertEqual(t("Los Angeles is 12 and 2."), set())
        self.assertEqual(t("they left dallas in a hurry"), set())          # no capital: no team (D41)

    def test_jerseys(self):
        j = __import__("media").jersey_team
        self.assertEqual(j({"s": "game", "t": "grimaces and shouts, Cleveland jersey"}), "cleveland cavaliers")
        self.assertEqual(j({"s": "game", "t": "stands in Oklahoma City jersey looking ahead"}), "oklahoma city thunder")
        self.assertEqual(j({"s": "game", "t": "walks with teammate, Houston"}), "houston rockets")
        self.assertEqual(j({"s": "game", "t": "dribbles, Los Angeles jersey"}), "")
        self.assertEqual(j({"s": "game", "t": "looks up, Lakers jersey"}), "los angeles lakers")

    def test_the_run_case(self):
        import media
        photo = {"kind": "photo", "title": "LeBron James Wiz", "team": "",
                 "tag": {"v": "C", "s": "game", "t": "grimaces and shouts, Cleveland jersey"}}
        with patch.object(media, "teams_of", lambda p: ("philadelphia 76ers", set())):
            self.assertFalse(media.team_fits(photo, "He is at career lows at 41, but Philly is 12 and 3.", "LeBron James"))


class AnotherMansTeam(unittest.TestCase):
    """94. D61 (his answers 2026-11-17). "Garnett won MVP in 2003 to 04, right after Denver took
    Carmelo third": Denver is Carmelo's team, yet Garnett's Wolves photo went. A team he never
    played for nor coached no longer judges his jersey. The first version worsened Doc Rivers ("took
    over a 32-14 Bucks team: You're the coach"): the Bucks are his as COACH, so his coached teams
    count too (rule i). On 508 kept photos exactly one changes: Garnett, kept."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: dict(getattr(media, k)) for k in ("_wikidata", "_career", "_coached", "_spells", "_team_since")}
        media._wikidata.update({"Kevin Garnett": "Q-KG", "Doc Rivers": "Q-DR", "Gary Trent": "Q-GT"})
        media._career.update({"Q-KG": {"minnesota timberwolves", "boston celtics", "brooklyn nets"},
                              "Q-DR": {"atlanta hawks", "los angeles clippers", "new york knicks", "san antonio spurs"},
                              "Q-GT": {"portland trail blazers", "toronto raptors"}})
        media._coached["Q-DR"] = {"orlando magic", "boston celtics", "los angeles clippers", "philadelphia 76ers",
                                  "milwaukee bucks"}

    def tearDown(self):
        for k, v in self.saved.items():
            getattr(self.m, k).clear()
            getattr(self.m, k).update(v)

    def test_cases(self):
        m = self.m
        ph = lambda t, team="": {"kind": "photo", "title": "x", "team": team, "tag": {"v": "C", "s": "game", "t": t}}
        with patch.object(m, "teams_of", lambda p: ("", set())):
            self.assertTrue(m.team_fits(ph("drives, Timberwolves jersey"),
                                        "Garnett won MVP in 2003 to 04, right after Denver took Carmelo third.", "Kevin Garnett"))
            self.assertFalse(m.team_fits(ph("smiles on the bench", "former"),
                                         'Rivers took over a 32-14 Bucks team: "You\'re the coach."', "Doc Rivers"))
            self.assertFalse(m.team_fits(ph("shoots in college", "pre-nba"),
                                         "Will the NBA punish the Bucks over Trent, or will it blink?", "Gary Trent"))
            self.assertTrue(m.team_fits(ph("shoots in college", "pre-nba"),
                                        "Will the league punish him, or will it blink?", "Gary Trent"))

    def test_coached_teams_are_kept(self):
        m = self.m
        text = "| team1 = [[Atlanta Hawks]]\n| years1 = 1983–1991\n| coach_team5 = [[Milwaukee Bucks]]"
        answer = json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": text}}}]}}}}).encode()
        saved = (dict(m._wiki_title), dict(m._teams))
        try:
            m._wiki_title["Doc Rivers 2"] = "Doc Rivers"
            with patch.object(m, "get", lambda url, timeout=30: answer):
                m.add_wiki_career("Doc Rivers 2", "Q-DR2")
            self.assertEqual(m._coached["Q-DR2"], {"milwaukee bucks"})
        finally:
            for d, v in zip((m._wiki_title, m._teams), saved):
                d.clear(); d.update(v)

    def test_coached_teams_read(self):
        got = self.m.wiki_coached("""| coach_team1 = [[Orlando Magic]]
| coach_years5 = {{nbay|2023|end}}–{{nbay|2025|end}}
| coach_team5 = [[Milwaukee Bucks]]
| team1 = [[Atlanta Hawks]]""")
        self.assertEqual(got, {"orlando magic", "milwaukee bucks"})


class HisCollegeIsPreNBA(unittest.TestCase):
    """95. D62 (run 44078900140; his answers 2026-11-17): three undated Flickr photos "Kawhi Leonard
    SDSU Aztecs" (tag "San Diego State") stood on his Spurs/NBA lines: the PRE-NBA words did not
    know his college and the tag was not read for it. On the 527 kept photos 4 become PRE-NBA, all
    Kawhi at San Diego State; on 1518 cached tags the college names hit only real college photos."""

    KAWHI = "| college = [[San Diego State Aztecs men's basketball|San Diego State]] (2009–2011)"
    ISIAH = "| college = [[Indiana Hoosiers men's basketball|Indiana]] (1979–1981)"

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: dict(getattr(media, k)) for k in ("_wikidata", "_college")}
        media._wikidata.update({"Kawhi Leonard": "Q-KL", "Isiah Thomas": "Q-IT"})
        media._college["Q-KL"] = media.wiki_college(self.KAWHI)
        media._college["Q-IT"] = media.wiki_college(self.ISIAH)

    def tearDown(self):
        for k, v in self.saved.items():
            getattr(self.m, k).clear()
            getattr(self.m, k).update(v)

    def test_names(self):
        self.assertEqual(self.m.wiki_college(self.KAWHI), ["san diego state aztecs", "san diego state", "aztecs"])

    def test_photos(self):
        m = self.m
        ph = lambda title, t="": {"kind": "photo", "title": title, "team": "", "tag": {"v": "C", "s": "game", "t": t}}
        with patch.object(m, "teams_of", lambda p: ("", set())):
            # D96 module 6 part 4 (a changed rule, his answer: the tagger decides): a TAGGED photo by
            # its note; the title only when nobody looked at it (the real D62 photos' notes say
            # "San Diego State": 14 of 16 kept, the 2 others show no player)
            self.assertFalse(m.college_photo(ph("Kawhi Leonard SDSU Aztecs"), "Kawhi Leonard"))
            self.assertTrue(m.college_photo({"kind": "photo", "title": "Kawhi Leonard SDSU Aztecs", "team": ""},
                                            "Kawhi Leonard"))
            self.assertTrue(m.college_photo(ph("Kawhi Leonard", "reaches for rebound, San Diego State"), "Kawhi Leonard"))
            self.assertFalse(m.college_photo(ph("Kawhi Leonard 2019", "shoots, Raptors jersey"), "Kawhi Leonard"))
            self.assertTrue(m.college_photo(ph("Isiah Thomas and Bobby Knight 1981", "talks with coach in Indiana huddle"), "Isiah Thomas"))
            untagged = lambda title: {"kind": "photo", "title": title, "team": ""}      # noqa: E731 (D96: title rules)
            self.assertFalse(m.college_photo(untagged("Isiah Thomas Indiana Pacers coach"), "Isiah Thomas"))
            self.assertTrue(m.college_photo(untagged("Isiah Thomas Indiana Hoosiers"), "Isiah Thomas"))
            self.assertFalse(m.college_photo(ph("Isiah Thomas Indiana Hoosiers"), "Isiah Thomas"))   # tagged: its note
            line = "His last Spurs team, with Ginobili and Parker, got swept by Golden State."
            photo = ph("Kawhi Leonard SDSU Aztecs", "dribbles past defender, San Diego State")
            self.assertFalse(m.team_fits(photo, line, "Kawhi Leonard"))
            self.assertEqual(photo["team"], "pre-nba")                    # the final read sees PRE-NBA

    def test_photos_marks_by_title_before_any_tag(self):
        m = self.m
        f = {"kind": "photo", "title": "Kawhi Leonard SDSU Aztecs", "page": "https://www.flickr.com/photos/x/5420500049",
             "url": "u", "source": "Flickr", "team": "", "score": 1}
        m._all_photos.pop("Kawhi Leonard", None)
        try:
            with patch.object(m, "teams_of", lambda p: ("", set())), \
                    patch.object(m, "commons_photos", lambda p: []), \
                    patch.object(m, "flickr_photos", lambda p: [f]), \
                    patch.object(m, "openverse_photos", lambda p: []):
                got = m.photos("Kawhi Leonard")
            self.assertEqual([x["team"] for x in got], ["pre-nba"])
        finally:
            m._all_photos.pop("Kawhi Leonard", None)

    def test_college_is_kept_from_the_infobox(self):
        m = self.m
        answer = json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": self.KAWHI}}}]}}}}).encode()
        saved = (dict(m._wiki_title), dict(m._teams))
        try:
            m._wiki_title["Kawhi Leonard 2"] = "Kawhi Leonard"
            with patch.object(m, "get", lambda url, timeout=30: answer):
                m.add_wiki_career("Kawhi Leonard 2", "Q-KL2")
            self.assertEqual(m._college["Q-KL2"], ["san diego state aztecs", "san diego state", "aztecs"])
        finally:
            for d, v in zip((m._wiki_title, m._teams), saved):
                d.clear(); d.update(v)
            m._college.pop("Q-KL2", None)

    def test_tagged_pool_is_marked(self):
        m = self.m
        pool = [{"kind": "photo", "title": "Kawhi Leonard", "page": "p1", "url": "u", "hoops": True,
                 "tag": {"v": "C", "s": "game", "t": "reaches for rebound, San Diego State"}}]
        with patch.object(m, "teams_of", lambda p: ("", set())), patch.object(m, "photos", lambda p: pool):
            self.assertEqual(m.person_photos("Kawhi Leonard", set()), [])


class WhoTheWriterPutOnScreen(TheLinesManOnly):
    """96. D63 (run 44088855986; his answer 2026-11-17): "My read: he had seven of the 18 turnovers"
    (on_screen "Jokic with the ball") got DeMar DeRozan in a Raptors jersey: the top-ups read only
    the spoken line. In the kept runs 10 photos change, every one to the man the line is about;
    none gets worse."""

    def fill_screen(self, line, screen, pools, who):
        m = self.m
        m.spoken = lambda short: [{"say": line, "on_screen": screen}]
        m.photos = lambda person: pools.get(person, [])
        m.career_teams = lambda p: {"denver nuggets"}
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            return m.fill_empty([None], 1, self.folder, set(), who, {"_name": "t", "beats": [{}]})[0]

    def test_on_screen_decides(self):
        pools = {"DeMar DeRozan": [self.ph("DeMar DeRozan (25715231917).jpg")],
                 "Nikola Jokic": [self.ph("Nikola Jokic (51914984866).jpg")]}
        got = self.fill_screen("My read: he had seven of the 18 turnovers, so it's a standard, not a shot.",
                               "Jokic with the ball", pools, ["DeMar DeRozan", "Nikola Jokic"])
        self.assertEqual(got["title"], "Nikola Jokic (51914984866).jpg")

    def test_no_name_anywhere_as_before(self):
        pools = {"DeMar DeRozan": [self.ph("DeMar DeRozan (25715231917).jpg")],
                 "Nikola Jokic": [self.ph("Nikola Jokic (51914984866).jpg")]}
        got = self.fill_screen("I think pressure isn't the real problem.", "Warriors offense struggling",
                               pools, ["DeMar DeRozan", "Nikola Jokic"])
        self.assertEqual(got["title"], "DeMar DeRozan (25715231917).jpg")     # the story's order, as before

    def test_the_spoken_name_wins_when_the_note_names_no_player(self):
        # changed by D72 (his answer 2026-11-18): a note naming a player now comes first (see 108);
        # the spoken name still wins over a note naming only a reporter or an executive (D50)
        pools = {"DeMar DeRozan": [self.ph("DeMar DeRozan (25715231917).jpg")],
                 "Nikola Jokic": [self.ph("Nikola Jokic (51914984866).jpg")]}
        m = self.m
        m.career_teams = lambda p: {"denver nuggets"} if p in ("DeMar DeRozan", "Nikola Jokic") else set()
        m.spoken = lambda short: [{"say": "Yahoo says DeRozan doesn't look like the target.",
                                   "on_screen": "Tim Connelly at the podium"}]
        m.photos = lambda person: pools.get(person, [])
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            got = m.fill_empty([None], 1, self.folder, set(), ["Nikola Jokic", "DeMar DeRozan", "Tim Connelly"],
                               {"_name": "t", "beats": [{}]})[0]
        self.assertEqual(got["title"], "DeMar DeRozan (25715231917).jpg")


REDICK_SOURCES = [
    {"publisher": "Bleacher Report", "title": "Redick calls out Lakers", "summary": "",
     "text": "Per The Athletic's Law Murray, Reddick called out the Lakers for their defensive lapses.\n"
             "\"I told the team this after the game \u2014 we're working too hard, and we're playing too hard, "
             "to build these leads \u2014 it's a disservice to each other to take your foot off the gas,\" "
             "Redick said after the Lakers were outscored 43-27 in the fourth quarter."},
    {"publisher": "Yahoo Sports", "title": "Lakers hold off Suns", "summary": "",
     "text": "Mark Williams said the same thing on Friday.\n"
             "\"Nobody here is going to take their foot off the gas against a team like this one tonight,\" "
             "Williams said."},
]


class CopiedQuoteGetsMarks(unittest.TestCase):
    """97. D2-b (run 43934705382; his answers 2026-11-17): "Redick said after the game he told the
    team it's a disservice to each other to take your foot off the gas" - 13 words of Redick's own
    quote without quote marks, so the gate read them as an article read out (REVIEW). Now exactly
    the copied words get quote marks; in every kept run nothing else changes."""

    def setUp(self):
        import script
        self.s = script

    def beat(self, say):
        return [{"say": say, "stage": "conflict"}]

    def test_redick_words_marked(self):
        import compliance
        beats = self.beat("Per The Athletic, Redick said after the game he told the team it's a disservice "
                          "to each other to take your foot off the gas.")
        got = self.s.mark_copied_quotes(beats, REDICK_SOURCES)
        self.assertEqual(got, ["it's a disservice to each other to take your foot off the gas"])
        self.assertEqual(beats[0]["say"], "Per The Athletic, Redick said after the game he told the team "
                                          "\"it's a disservice to each other to take your foot off the gas.\"")
        self.assertLess(compliance.check_originality(beats, REDICK_SOURCES)[2]["longest_copy"], compliance.COPY_RUN)
        self.assertEqual(self.s.quote_check(beats[0]["say"], REDICK_SOURCES), [])
        self.assertEqual(self.s.quotes_outside_marks(beats[0]["say"], REDICK_SOURCES), [])

    def test_another_man_named(self):
        beats = self.beat("Doncic said after the game he told the team it's a disservice to each other to "
                          "take your foot off the gas.")
        self.assertEqual(self.s.mark_copied_quotes(beats, REDICK_SOURCES), [])

    def test_a_team_is_not_the_man(self):
        beats = self.beat("The Lakers heard it's a disservice to each other to take your foot off the gas.")
        self.assertEqual(self.s.mark_copied_quotes(beats, REDICK_SOURCES), [])

    def test_fewer_than_twelve_words(self):
        beats = self.beat("Redick said it's a disservice to each other to take your foot off.")
        self.assertEqual(self.s.mark_copied_quotes(beats, REDICK_SOURCES), [])

    def test_article_narration_is_not_a_quote(self):
        src = [{"title": "", "summary": "", "text": "Redick called out the Lakers for their defensive "
                "lapses late in games after a long road trip this week."}]
        beats = self.beat("Redick called out the Lakers for their defensive lapses late in games after a "
                          "long road trip.")
        self.assertEqual(self.s.mark_copied_quotes(beats, src), [])

    def test_the_pipeline_marks_the_finished_beats(self):
        long_quote = ("\"I told them all night that they should have kept me here in Atlanta forever,\" "
                      "Doncic said after the game.")
        harness = Script("test_repair_pass")
        harness.TEXT = Script.TEXT + long_quote
        beats = copy.deepcopy(Script.GOOD)
        beats[1]["say"] = ("Doncic said after the game he told them all night that they should have kept me "
                           "here in Atlanta forever.")
        short, calls = harness._build(Script.GOOD, draft_beats=beats)
        said = " ".join(b["say"] for b in short["beats"])
        self.assertIn('"told them all night that they should have kept me here in Atlanta forever."', said)
        self.assertTrue(any("now in quote marks" in x for x in short["softened_quotes"]))

    def test_already_quoted_stays(self):
        say = ("Redick said \"it's a disservice to each other to take your foot off the gas.\"")
        beats = self.beat(say)
        self.assertEqual(self.s.mark_copied_quotes(beats, REDICK_SOURCES), [])
        self.assertEqual(beats[0]["say"], say)


class CarefulTruthRules(unittest.TestCase):
    """98. D2-a/c/d (runs 43934705382, 44078900140; his answers 2026-11-17): Embiid's "back in three
    minutes, he dunked" (the dunk came in the second quarter), Barkley's "after leading New York by
    22" (Game 1 only, then no other win), Wade "one of Wembanyama's harshest critics" (the source:
    "one of the people who gave harsh criticism"), and "he's leaving" on a trade request."""

    def test_hook_truth_catches_joined_facts_and_stronger_words(self):
        import script
        p = " ".join(script.HOOK_TRUTH.split())
        self.assertIn("joins or shortens the sources' facts", p)
        self.assertIn("superlative (harshest, worst, ever) or an always, never or everyone word", p)

    def test_final_read_catches_joined_facts_and_settled_future(self):
        import final_read
        p = " ".join(final_read.PROMPT.split())
        self.assertIn("facts joined or shortened so the line says something the sources do not", p)
        self.assertIn("her opinion stating a future the sources leave open as settled", p)
        self.assertNotIn("superlative", p)        # D2-c: the hook check only (his answer)

    def test_writer_and_editor_keep_the_future_open(self):
        import script
        for prompt in (script.PROMPT, script.HUMANIZE):
            self.assertIn("a future the sources leave open is said as likely, never as settled",
                          " ".join(prompt.split()))


class PastFormsAboutThem(unittest.TestCase):
    """99. Run 44098884631 (his yes 2026-11-17): "Isiah Thomas claimed racial stereotypes led people
    to overlook Magic Johnson's basketball IQ" (two days old) was not counted as an article about
    them: the words had "claims" but not "claimed". Kevin Durant / Kendrick Perkins was in the bank
    twice. Freshness is still only the date window, never the verb."""

    def test_past_forms(self):
        import evergreen as e
        self.assertTrue(e.about_them("Isiah Thomas claimed racial stereotypes led people to overlook Magic Johnson's basketball IQ"))
        self.assertTrue(e.about_them("Shaq slammed Kobe in old interview"))
        self.assertTrue(e.about_them("Durant fired back at Perkins"))
        self.assertFalse(e.about_them("Thunder's Shai Gilgeous-Alexander Threatens Kevin Durant, Russell Westbrook Record"))

    def test_why_alone_is_not_about_them(self):
        # D64 (his answer 2026-11-17): "why" made an injury note a fresh reason for a beef
        import evergreen as e
        self.assertFalse(e.about_them("Why Kyrie Irving will not play vs. Celtics? Mavs announce huge injury update"))
        self.assertFalse(e.about_them('"It\'s like giving up a diamond for some garnets" - Phil Jackson on why Knicks weren\'t good enough'))
        self.assertTrue(e.about_them("Kyrie Irving explains why he will not follow LeBron James path"))

    def test_every_pair_once(self):
        import evergreen as e
        keys = [e.key_of(a, b) for a, b, _ in e.BANK]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), 61)              # 29 + the 32 he approved (2026-11-17)
        self.assertIn("Allen Iverson vs Larry Brown", keys)


class EvidenceInPieces(unittest.TestCase):
    """100. D65 (run 44110628783; his answers 2026-11-17): the final read saw "the Warriors are one
    and three, and Kerr called it terrible" (Kerr: "Another terrible start") and lost it as a doubt:
    the evidence joined the line and the source, which is never one passage."""

    ROWS = [{"line": 3, "says": "Without him, the Warriors are one and three, and Kerr called it terrible.",
             "pictures": ["Steve Kerr | on the sideline | game"]}]
    SOURCES = [{"title": "Short-handed Warriors", "summary": "",
                "text": "They opened with a 38-14 deficit. \"Another terrible start,\" Kerr told reporters after "
                        "Monday's loss. \"We tried to change it up from San Antonio.\""}]

    def test_joined_evidence_holds(self):
        import final_read as f
        # the source's words first, then the line's: never one passage, whatever the order of the text
        ev = ('Source: "Another terrible start," Kerr told reporters. Line: "Without him, the Warriors are '
              'one and three, and Kerr called it terrible."')
        self.assertTrue(f.real_evidence(ev, self.ROWS, self.SOURCES))
        got = f.judge({"errors": [{"line": 3, "kind": "NOT IN THE SOURCES", "what": "x", "evidence": ev}]},
                      self.ROWS, self.SOURCES)
        self.assertEqual(got["verdict"], "REVIEW")

    def test_an_invented_piece_is_still_a_doubt(self):
        import final_read as f
        ev = 'Line: "Kerr called it terrible" Source: "Kerr said the team was terrible without Curry all season"'
        self.assertFalse(f.real_evidence(ev, self.ROWS, self.SOURCES))
        got = f.judge({"errors": [{"line": 3, "kind": "WRONG WORDS", "what": "x", "evidence": ev}]},
                      self.ROWS, self.SOURCES)
        self.assertEqual(got["verdict"], "PASS")
        self.assertEqual(got["doubts"][0]["evidence"], ev)          # saved, so we can see why

    def test_her_opinion_is_never_a_quote(self):
        # his answer 2026-11-17: "I think the cut is smart." was read as a quote (run 44110628783)
        import final_read as f
        p = " ".join(f.PROMPT.split())
        self.assertIn('The narrator\'s own opinion ("I think...", "My read...", "Honestly...") is her own '
                      'words, never a quote: it is never WRONG WORDS', p)
        self.assertIn("is still NOT IN THE SOURCES", p)

    def test_one_word_pieces_never_prove(self):
        import final_read as f
        self.assertFalse(f.real_evidence('"Kerr" "terrible" invented words here', self.ROWS, self.SOURCES))


class VerdictNeedsAReason(unittest.TestCase):
    """101. Run 44110628783 (his answers 2026-11-17): Curry's payoff was only "I think the cut is
    smart." In the kept runs only this payoff is caught; "I think baiting is no excuse for
    swinging." (8 words) is not."""

    def pay(self, say):
        return [{"say": "Context.", "stage": "setup"}, {"say": say, "stage": "payoff"},
                {"say": "Who wins, Curry or the Warriors?", "stage": "exit"}]

    def test_caught(self):
        import script
        self.assertTrue(script.bare_opinion(self.pay("I think the cut is smart.")))
        self.assertTrue(script.bare_opinion(self.pay("Honestly, he is right.")))
        problems = script.repair_needed("Curry took a pay cut?", self.pay("I think the cut is smart."),
                                        {"hard": [], "soft": []})
        self.assertTrue(any("no reason" in p for p in problems))

    def test_not_caught(self):
        import script
        for say in ("I think the cut is smart because it frees cap room.", "I think so too, he is right.",
                    "Doc was half right and fully clumsy.", "I think baiting is no excuse for swinging.",
                    "I'd say it's smart. The cap room comes right when they need it."):
            self.assertFalse(script.bare_opinion(self.pay(say)), say)


class WordLeftOutOfAQuote(unittest.TestCase):
    """102. D66 (run 44110628783; his answers 2026-11-17): Brooks said "I was just trying to
    de-escalate it"; the Short said "I was trying to de-escalate it." Every quoted word was in the
    source, so it counted as exact. In the kept runs only this quote changes."""

    SRC = [{"title": "Brooks", "summary": "",
            "text": "\"I was just trying to de-escalate it,\" Brooks said after the game. \"You weren't trying "
                    "to de-escalate,\" Green said on his podcast. \"You were trying to be the villain.\""}]

    def soft(self, say):
        import script
        beats = [{"say": say}]
        got = script.soften_quotes(beats, self.SRC)
        return beats[0]["say"], got

    def test_word_inside_restored(self):
        say, got = self.soft('Brooks said, "I was trying to de-escalate it."')
        self.assertEqual(say, 'Brooks said, "I was just trying to de-escalate it."')
        self.assertEqual(len(got), 1)

    def test_part_of_a_sentence_stays(self):
        say, got = self.soft('Green said, "trying to be the villain."')
        self.assertEqual(say, 'Green said, "trying to be the villain."')
        self.assertEqual(got, [])

    def test_exact_quote_stays(self):
        say, got = self.soft('Brooks said, "I was just trying to de-escalate it."')
        self.assertEqual(got, [])

    def test_never_across_narration(self):
        import script
        words, toks, owner = script._source_words(self.SRC)
        self.assertEqual(script.missing_inside("de-escalate it You weren't trying", words, toks, owner), "")
        src = [{"title": "", "summary": "", "text": '"I was just trying," Brooks said. "To calm it down."'}]
        words, toks, owner = script._source_words(src)
        self.assertEqual(script.missing_inside("I was just trying to calm it down", words, toks, owner), "")


class HisNationalTeamWhenNoNBAPhoto(TheLinesManOnly):
    """103. D67 (run 44110628783; his answers 2026-11-17): Dillon Brooks was never on screen in his
    own beef: his only usable photos on Commons are Canada national-team ones (D45 keeps them off
    every non-national line). In the kept runs only Brooks has no NBA photo at all."""

    def setUp(self):
        super().setUp()
        self.m.career_teams = lambda p: {"phoenix suns"} if p == "Dillon Brooks" else (
            {"golden state warriors"} if p in ("Yaxel Lendeborg", "Draymond Green") else set())

    @staticmethod
    def canada(title, v="C"):
        return {"kind": "photo", "title": title, "page": "p-" + title, "url": "u-" + title, "author": "a",
                "team": "", "hoops": True, "own_category": True,
                "tag": {"v": v, "s": "national", "t": "dribbles past defender, Canada 24"}}

    def test_brooks_on_his_own_line(self):
        pools = {"Dillon Brooks": [self.canada("Dillon Brooks Canada 2023.jpg")]}
        got = self.fill("Brooks said he was trying to de-escalate it.", pools, ["Draymond Green", "Dillon Brooks"])
        self.assertEqual(got["title"], "Dillon Brooks Canada 2023.jpg")
        self.assertTrue(got["national_only"])
        import final_read
        self.assertIn("NATIONAL, NO NBA PHOTO EXISTS", final_read.picture_line(got))
        self.assertIn("NATIONAL, NO NBA PHOTO EXISTS", final_read.PROMPT)

    def test_never_on_a_team_or_time_line(self):
        pools = {"Dillon Brooks": [self.canada("Dillon Brooks Canada 2023.jpg")]}
        self.assertIsNone(self.fill("Brooks and the Suns lost tonight.", pools, ["Dillon Brooks"]))
        self.assertIsNone(self.fill("Brooks said tonight he is the villain.", pools, ["Dillon Brooks"]))

    def test_an_nba_photo_comes_first(self):
        pools = {"Dillon Brooks": [self.ph("Dillon Brooks Suns 2025.jpg"), self.canada("Dillon Brooks Canada 2023.jpg")]}
        got = self.fill("Brooks said he was trying to de-escalate it.", pools, ["Dillon Brooks"])
        self.assertEqual(got["title"], "Dillon Brooks Suns 2025.jpg")
        self.assertNotIn("national_only", got)

    def test_national_only_when_no_nba_photo_at_all(self):
        import media
        nba = self.ph("Dillon Brooks Suns 2025.jpg")
        media.photos = lambda person: [nba, self.canada("Dillon Brooks Canada 2023.jpg")]
        self.assertEqual(media.national_faces("Dillon Brooks", set()), [])

    def test_must_show_him(self):
        pools = {"Dillon Brooks": [self.canada("Dillon Brooks Canada 2023.jpg", v="O")]}
        self.assertIsNone(self.fill("Brooks said he was trying to de-escalate it.", pools, ["Dillon Brooks"]))


CURRY_SOURCES = [
    {"publisher": "Bleacher Report", "title": "Steph Curry explains pay cut", "summary": "",
     "text": "Curry took a slight pay cut, telling ESPN's Anthony Slater that he wanted to eliminate distractions "
             "and give the Warriors some flexibility. Curry agreed to a two-year, $116 million extension that gave "
             "$10 million in cap space back to the Warriors next summer. \"I assumed that it would probably be one "
             "of, if not the last, contract I signed,\" Curry said."},
    {"publisher": "Yahoo Sports", "title": "Short-handed Warriors struggle without Steph Curry", "summary": "",
     "text": "The Warriors are 1-3 without Curry. They opened with a 38-14 deficit. \"Another terrible start,\" "
             "Kerr told reporters after Monday's loss."}]
CURRY_SHORT = {
    "n": 1, "headline": "Steph Curry explains pay cut", "lead": "curry",
    "hook": {"text": "Steph Curry just admitted his new Warriors contract is probably his last."},
    "beats": [
        {"say": "He took a pay cut that gave the Warriors 10 million in cap space.", "on_screen": "Curry", "stage": "setup"},
        {"say": "He said it's probably his last contract.", "on_screen": "Curry", "stage": "conflict"},
        {"say": "Without him, the Warriors are one and three, and Kerr called it terrible.", "on_screen": "Kerr",
         "stage": "escalation"},
        {"say": "Is the cap room enough for Curry, or is it too late?", "on_screen": "Curry", "stage": "exit"}],
    "titles": [{"title": "Curry's LAST contract?"}], "thumbnail_text": "CURRY'S LAST DEAL?", "claims": [],
    "compliance": {"verdict": "PASS", "checks": {"title_accuracy": {"verdict": "PASS", "notes": []},
                                                 "thumbnail_accuracy": {"verdict": "PASS", "notes": []}}}}
KERR_ERROR = {"line": 3, "kind": "NOT IN THE SOURCES", "what": "Kerr said terrible about a start",
              "evidence": 'Source: "Another terrible start," Kerr told reporters. Line: "Kerr called it terrible."'}


class FixAfterTheRead(unittest.TestCase):
    """104. Stage 4e (run 44110628783; his answers 2026-11-17): Curry's Short was held for two wrong
    lines and lost (he reviews nothing). Now only the lines with an error are fixed (the same checks
    as the repair pass; a hook by the hook rules), a wrong picture is never used again in that
    Short, the Short is redone (voice when the words changed, all pictures, the final read) and
    it goes on while each try leaves fewer errors."""

    def setUp(self):
        import fix_after_read as f
        import script
        self.f, self.s = f, script
        self.saved = (script.ask_claude, f.stage, f.SCRIPTS, f.MEDIA, f.SOURCES, f.REVIEW, f.AUDIO)
        self.tmp = Path(tempfile.mkdtemp())
        for d in ("scripts", "media", "sources", "review", "audio"):
            (self.tmp / d).mkdir()
        f.SCRIPTS, f.MEDIA, f.SOURCES, f.REVIEW, f.AUDIO = (self.tmp / d for d in
                                                            ("scripts", "media", "sources", "review", "audio"))

    def tearDown(self):
        f, s = self.f, self.s
        s.ask_claude, f.stage, f.SCRIPTS, f.MEDIA, f.SOURCES, f.REVIEW, f.AUDIO = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def answer(self, lines):
        self.s.ask_claude = lambda prompt, model="", where="": {"lines": lines}

    def test_only_the_wrong_line_changes(self):
        self.answer([{"line": 3, "says": "Without him, the Warriors are one and three, and Kerr called another "
                                         "start terrible."},
                     {"line": 1, "says": "He took a huge pay cut."}])             # not an error line: ignored
        new, why = self.f.fix_text(copy.deepcopy(CURRY_SHORT), [KERR_ERROR], CURRY_SOURCES, [])
        self.assertEqual(why, "")
        self.assertEqual(new["beats"][2]["say"], "Without him, the Warriors are one and three, and Kerr called "
                                                 "another start terrible.")
        self.assertEqual(new["beats"][0]["say"], CURRY_SHORT["beats"][0]["say"])
        self.assertEqual(new["hook"]["text"], CURRY_SHORT["hook"]["text"])
        self.assertIn("compliance", new)
        self.assertIn("another start terrible", new["spoken"])          # the gate reads the fixed words
        self.assertEqual(new["unsupported_numbers"], [])
        self.assertEqual(new["compliance"]["checks"]["title_accuracy"], {"verdict": "PASS", "notes": []})

    def test_a_fix_that_invents_is_refused(self):
        self.answer([{"line": 3, "says": "Without him, they are 1 and 7, and Kerr called it terrible."}])
        new, why = self.f.fix_text(copy.deepcopy(CURRY_SHORT), [KERR_ERROR], CURRY_SOURCES, [])
        self.assertIsNone(new)
        self.assertIn("number", why)

    def test_a_hook_fix_keeps_the_hook_rules(self):
        err = {**KERR_ERROR, "line": 0}
        self.answer([{"line": 0, "says": "The Warriors made a deal."}])               # too short, no Curry
        new, why = self.f.fix_text(copy.deepcopy(CURRY_SHORT), [err], CURRY_SOURCES, [])
        self.assertIsNone(new)
        self.answer([{"line": 0, "says": "Steph Curry just said his new Warriors deal is probably his last."}])
        new, why = self.f.fix_text(copy.deepcopy(CURRY_SHORT), [err], CURRY_SOURCES, [])
        self.assertEqual(new["hook"]["text"], "Steph Curry just said his new Warriors deal is probably his last.")

    def test_the_picture_the_evidence_names(self):
        a = {"kind": "photo", "page": "pa", "person": "Steve Kerr", "tag": {"t": "on the sideline"}, "beat": 3}
        b = {"kind": "photo", "page": "pb", "person": "Luka Doncic", "tag": {"t": "looks ahead in Dallas jersey"},
             "beat": 3}
        items = [None, None, None, {**a, "alts": [b]}]
        err = {"line": 3, "kind": "WRONG PICTURE", "evidence": 'Picture: "Luka Doncic | looks ahead in Dallas jersey"'}
        self.assertEqual(self.f.refused_pictures([err], items), ["pb"])
        err = {"line": 3, "kind": "WRONG PICTURE", "evidence": 'Picture: "Steve Kerr | game"'}   # his name only
        self.assertEqual(self.f.refused_pictures([err], items), ["pa", "pb"])     # none named: the whole line

    def run_loop(self, reads, voice_ok=True):
        """reads: the final read's error lists after each try."""
        f = self.f
        (f.SCRIPTS / "short_1.json").write_text(json.dumps(CURRY_SHORT))
        (f.SOURCES / "short_1.json").write_text(json.dumps(CURRY_SOURCES))
        (f.REVIEW / "short_1.json").write_text(json.dumps({"verdict": "REVIEW", "errors": [KERR_ERROR, KERR_ERROR]}))
        done, left = [], list(reads)

        def stage(module, name):
            done.append(module)
            if module == "tts.py" and voice_ok:
                (f.AUDIO / "short_1.timing.json").write_text(str(len(done)))
                import os as _os
                _os.utime(f.AUDIO / "short_1.timing.json", (10 ** 9 + len(done), 10 ** 9 + len(done)))
            if module == "final_read.py":
                errs = left.pop(0)
                (f.REVIEW / "short_1.json").write_text(json.dumps({"verdict": "REVIEW" if errs else "PASS",
                                                                   "errors": errs}))
        f.stage = stage
        self.answer([{"line": 3, "says": "Without him, the Warriors are one and three, and Kerr called another "
                                         "start terrible."}])
        return f.fix_short("short_1"), done

    def test_goes_on_while_errors_get_fewer(self):
        tries, done = self.run_loop([[KERR_ERROR], []])
        self.assertEqual(len(tries), 2)
        self.assertEqual(json.loads((self.f.REVIEW / "short_1.json").read_text())["verdict"], "PASS")
        self.assertEqual(done[:4], ["tts.py", "audio_qc.py", "media.py", "final_read.py"])

    def test_stops_without_progress(self):
        tries, done = self.run_loop([[KERR_ERROR, KERR_ERROR], [KERR_ERROR]])
        self.assertEqual(len(tries), 1)
        self.assertIn("no progress", tries[0]["stopped"])

    def test_no_new_voice_keeps_the_old_words(self):
        tries, done = self.run_loop([[]], voice_ok=False)
        self.assertIn("no new voice", tries[0]["stopped"])
        kept = json.loads((self.f.SCRIPTS / "short_1.json").read_text())
        self.assertEqual(kept["beats"][2]["say"], CURRY_SHORT["beats"][2]["say"])
        self.assertNotIn("media.py", done)

    def test_one_short_only(self):
        import only
        with patch.dict("os.environ", {"NBA_ONLY": "short_2"}):
            self.assertTrue(only.wanted("short_2"))
            self.assertFalse(only.wanted("short_1"))
            self.assertTrue(only.active())
        with patch.dict("os.environ", {"NBA_ONLY": ""}):
            self.assertTrue(only.wanted("short_1"))
            self.assertFalse(only.active())


class RedoOneShortsPictures(unittest.TestCase):
    """104 (pictures). When stage 4e redoes a Short's pictures, the refused ones never come back
    (round 1, round 2 and the fill all skip them), and the pictures replaced stay in the permanent
    licence record, marked "replaced" (his answer)."""

    def test_refused_never_offered(self):
        import media
        seen = []
        saved = (media.plan, media.shortlist_photos, media.candidates, media.contact_sheet, media.spoken,
                 media.commons_videos)
        try:
            media.commons_videos = lambda *a, **k: []     # D99 (his answer 5): the Commons search finds nothing
            media.plan = lambda short: [{"person": "Steve Kerr", "queries": []}]
            media.spoken = lambda short: [{"say": "Kerr called it terrible."}]
            media.shortlist_photos = lambda *a, **k: None
            media.candidates = lambda *a, **k: [{"kind": "photo", "page": "pa"}, {"kind": "photo", "page": "pb"}]

            def sheet(cands, *a, **k):
                seen.extend(c["page"] for c in cands)
                raise media.UsageLimit("stop here")
            media.contact_sheet = sheet
            media.REFUSED.clear()
            media.REFUSED.add("pb")
            with self.assertRaises(media.UsageLimit):
                media.collect_for({"headline": "h", "beats": []}, Path(tempfile.mkdtemp()), set())
            self.assertEqual(seen, ["pa"])
            self.assertIn("pb", media.REJECTED)                 # the fill and the VS card skip it too
        finally:
            (media.plan, media.shortlist_photos, media.candidates, media.contact_sheet, media.spoken,
             media.commons_videos) = saved
            media.REFUSED.clear()

    def test_replaced_stay_marked(self):
        import media
        saved = media.LEDGER
        media.LEDGER = Path(tempfile.mkdtemp())
        try:
            media.record_replaced("short_1", [{"kind": "photo", "title": "Luka.jpg", "page": "pb"}])
            rec = json.loads((media.LEDGER / "assets.jsonl").read_text().splitlines()[0])
            self.assertTrue(rec["replaced"])
            self.assertEqual(rec["source_page"], "pb")
        finally:
            shutil.rmtree(media.LEDGER, ignore_errors=True)
            media.LEDGER = saved

    def test_the_other_shorts_keep_their_clips_and_music(self):
        import media
        saved = (media.SCRIPTS, media.MEDIA, media.ROOT)
        tmp = Path(tempfile.mkdtemp())
        try:
            media.SCRIPTS, media.MEDIA, media.ROOT = tmp / "scripts", tmp / "media", tmp
            media.SCRIPTS.mkdir()
            (media.MEDIA / "short_1").mkdir(parents=True)
            for n in (1, 2):
                (media.SCRIPTS / f"short_{n}.json").write_text("{}")
            (media.MEDIA / "short_2.json").write_text(json.dumps([{"kind": "video", "id": "clip9", "alts": []}]))
            (media.MEDIA / "short_2_music.json").write_text(json.dumps({"file": "data/media/short_2/music.mp3",
                                                                         "library_key": "dark/Night Drive.mp3",
                                                                         "url": "https://x/t.mp3"}))
            (media.MEDIA / "short_1" / "music.mp3").write_text("m")
            (media.MEDIA / "short_1_music.json").write_text(json.dumps({"file": "media/short_1/music.mp3"}))
            with patch.dict("os.environ", {"NBA_ONLY": "short_1"}):
                self.assertEqual(media.others_used(), {"clip9", "Night Drive.mp3", "https://x/t.mp3"})
            self.assertEqual(media.music_kept("short_1")["file"], "media/short_1/music.mp3")
            self.assertIsNone(media.music_kept("short_2"))                 # its file is not there
        finally:
            media.SCRIPTS, media.MEDIA, media.ROOT = saved
            shutil.rmtree(tmp, ignore_errors=True)


class QualityEval(unittest.TestCase):
    """105. D69 (his answers 2026-11-17): the kept stories made again as full Shorts by today's code;
    repetition check off; nothing of the channel's record touched but the photo tag cache; results
    only (no MP4); in parts, going on where the Claude limit stopped it; one number = Shorts with no
    problem (not held by the script stage, no final read error; not made = a problem)."""

    def setUp(self):
        import eval_run
        self.e = eval_run
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (eval_run.DATA, eval_run.STATE, eval_run.EVAL, eval_run.make_script, eval_run.run_stages,
                      eval_run.git)
        eval_run.DATA, eval_run.STATE = self.tmp / "data", self.tmp / "state"
        eval_run.EVAL = eval_run.STATE / "nba" / "eval"
        eval_run.git = lambda *a: types.SimpleNamespace(returncode=0, stdout="", stderr="")
        for n in (1, 2, 3):
            d = eval_run.EVAL / "set" / f"run_short_{n}"
            d.mkdir(parents=True)
            (d / "story.json").write_text(json.dumps({"id": f"run_short_{n}", "headline": f"Story {n}",
                                                      "topic": {"headline": f"Story {n}"}, "judged": {}}))
            (d / "sources.json").write_text("[]")

    def tearDown(self):
        e = self.e
        e.DATA, e.STATE, e.EVAL, e.make_script, e.run_stages, e.git = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_stages(self, verdicts):
        e = self.e

        def make(story, sources):
            if story["id"] == "run_short_2" and verdicts.get("limit"):
                raise e.Limit("limit")
            return {"headline": story["headline"], "hook": {"text": "h", "score": 40}, "beats": [{"say": "b"}],
                    "ready": story["id"] != "run_short_3", "compliance": {"verdict": "PASS", "checks": {}}}

        def stages(*a, **k):        # D77: the full eval names the story, to keep its base
            (e.DATA / "review" / "short_1.json").write_text(json.dumps({"verdict": verdicts.get("read", "PASS"),
                                                                        "errors": []}))
            (e.DATA / "history").mkdir(parents=True, exist_ok=True)
            for f in ("photo_tags.json", "made.json"):
                (e.DATA / "history" / f).write_text(json.dumps({"file": f}))
        e.make_script, e.run_stages = make, stages

    def test_one_number_and_records(self):
        self.fake_stages({})
        with patch.dict("os.environ", {"EVAL_LABEL": "after"}):
            self.e.main()
        out = self.e.EVAL / "results" / "after"
        got = {p.stem: json.loads(p.read_text())["problem"] for p in out.glob("run_*.json")}
        self.assertEqual(got, {"run_short_1": False, "run_short_2": False, "run_short_3": True})   # 3: held
        self.assertIn("Shorts with no problem: 2 of 3", (out / "summary.md").read_text())
        hist = self.e.STATE / "nba" / "history"
        self.assertEqual(sorted(p.name for p in hist.iterdir()), ["photo_tags.json"])   # nothing else saved
        self.assertEqual(json.loads((hist / "photo_tags.json").read_text()), {"file": "photo_tags.json"})
        self.assertFalse(list(out.glob("*.mp4")))

    def test_stops_on_the_limit_and_goes_on(self):
        self.fake_stages({"limit": True})
        with patch.dict("os.environ", {"EVAL_LABEL": "x"}):
            self.e.main()
        out = self.e.EVAL / "results" / "x"
        self.assertEqual(sorted(p.stem for p in out.glob("run_*.json")), ["run_short_1"])
        self.assertIn("in progress: 1 of 3", (out / "summary.md").read_text())
        self.fake_stages({})
        made, make = [], self.e.make_script
        self.e.make_script = lambda story, sources: (made.append(story["id"]), make(story, sources))[1]
        with patch.dict("os.environ", {"EVAL_LABEL": "x"}):
            self.e.main()
        self.assertEqual(sorted(p.stem for p in out.glob("run_*.json")), ["run_short_1", "run_short_2", "run_short_3"])
        self.assertEqual(made, ["run_short_2", "run_short_3"])            # the done one is not made again

    def test_the_causes_are_kept(self):
        # his yes 2026-11-18: every problem followed to its cause (gate notes, the script's hold,
        # the final read in full, the fix tries, why each picture was chosen)
        e = self.e
        for d in ("review", "gate", "media", "audio", "scripts"):
            (e.DATA / d).mkdir(parents=True, exist_ok=True)
        (e.DATA / "gate" / "short_1.json").write_text(json.dumps({"verdict": "REVIEW", "checks": {
            "editorial": {"verdict": "REVIEW", "notes": ["too similar to an earlier Short"]},
            "voice": {"verdict": "PASS", "notes": []}}}))
        (e.DATA / "review" / "short_1.json").write_text(json.dumps({"verdict": "PASS", "errors": [],
                                                                    "doubts": [{"line": 2, "what": "x"}]}))
        (e.DATA / "review" / "short_1_fixes.json").write_text(json.dumps([{"errors": [], "stopped": "no progress"}]))
        (e.DATA / "media" / "short_1.json").write_text(json.dumps([{"title": "Draymond.jpg", "person": "Draymond Green",
                                                                    "match": "named", "alts": []}]))
        short = {"headline": "h", "hook": {"text": "h"}, "beats": [{"say": "b", "on_screen": "Steph Curry"}],
                 "ready": False, "retention": {"hard": ["no question"]}, "too_similar_to": "Old Short",
                 "compliance": {"verdict": "PASS", "checks": {}}}
        r = e.result_of({"id": "a", "headline": "h"}, short)
        self.assertEqual(r["gate_notes"], {"editorial": ["too similar to an earlier Short"]})
        self.assertEqual(r["script_hold"]["retention_hard"], ["no question"])
        self.assertEqual(r["script_hold"]["too_similar_to"], "Old Short")
        self.assertEqual(r["final_read_full"]["doubts"], [{"line": 2, "what": "x"}])
        self.assertEqual(r["fixes"][0]["stopped"], "no progress")
        self.assertEqual(r["picture_choice"][0][0]["person"], "Draymond Green")
        self.assertEqual(r["on_screen"], ["Steph Curry"])

    def test_not_made_is_a_problem(self):
        r = self.e.result_of({"id": "a", "headline": "h"}, None, "no article")
        self.assertTrue(r["problem"])

    def test_the_script_stage_as_a_run_calls_it(self):
        import script
        e = self.e
        e.make_script = self.saved[3]
        seen = {}
        saved = (script.build_short, script.gather_sources, script.load_recent, script.SCRIPT_LEDGER)
        ledger = self.tmp / "scripts.jsonl"
        ledger.write_text(json.dumps({"headline": "old", "hook": "h", "spoken": "an old Short"}) + "\n")
        script.SCRIPT_LEDGER = ledger                     # a real history the check would read
        try:
            def build(n, tid, editor, voice, formulas):
                seen.update(topic=editor["topics"][tid], judged=editor["ranked"][0],
                            sources=script.gather_sources(editor["topics"][tid], editor, tid))
                script.load_recent()
                seen["recent"] = list(script.RECENT)
                return {}
            script.build_short = build
            script.RECENT.append({"headline": "old", "spoken": "x"})
            e.make_script({"topic": {"headline": "Story"}, "judged": {"kind": "beef"},
                           "known_headlines": ["A", "B"]}, [{"title": "t", "main": True}])
            self.assertEqual(seen["topic"], {"headline": "Story"})
            self.assertEqual(seen["judged"]["kind"], "beef")
            self.assertEqual(seen["sources"], [{"title": "t", "main": True}])
            self.assertEqual(seen["recent"], [])               # the repetition check is off
            # D68: a format turned on: the editor's format answer joins the story's judgment
            fmt, e.editor_format = e.editor_format, lambda story: {"format": "receipts", "sides": ["A B", "C D"]}
            try:
                e.make_script({"topic": {"headline": "Story"}, "judged": {"kind": "beef"}, "known_headlines": []}, [])
                self.assertEqual((seen["judged"]["format"], seen["judged"]["kind"]), ("receipts", "beef"))
            finally:
                e.editor_format = fmt
        finally:
            script.build_short, script.gather_sources, script.load_recent, script.SCRIPT_LEDGER = saved
            script.RECENT.clear()


class EvalSetKept(unittest.TestCase):
    """105 (set). The set is copied out of the run bundles (cleaned after 14 days): every Short
    with its source texts; a historic beef gets its topic made again as evergreen.py made it."""

    def test_build(self):
        import eval_set
        tmp = Path(tempfile.mkdtemp())
        try:
            run = tmp / "runs" / "2026-11-17_1"
            for d in ("scripts", "sources", "gate", "review"):
                (run / d).mkdir(parents=True)
            (run / "editor.json").write_text(json.dumps({"topics": [{"headline": "Curry pay cut"}],
                                                         "ranked": [{"id": 0, "kind": "contract"}]}))
            (run / "scripts" / "short_1.json").write_text(json.dumps({"headline": "Curry pay cut", "topic_id": 0,
                                                                      "hook": {"text": "h"}, "beats": []}))
            (run / "scripts" / "short_2.json").write_text(json.dumps({
                "headline": "Draymond Green Rips Dillon Brooks (back in the news: the Draymond Green and Dillon "
                            "Brooks feud)", "topic_id": 1, "evergreen": "Dillon Brooks vs Draymond Green",
                "hook": {"text": "h"}, "beats": []}))
            (run / "scripts" / "short_3.json").write_text(json.dumps({"headline": "no sources", "topic_id": 0}))
            for n in (1, 2):
                (run / "sources" / f"short_{n}.json").write_text(json.dumps([{"title": "t", "text": "x", "main": True}]))
            got = eval_set.build(tmp / "runs", tmp / "set")
            self.assertEqual(got, ["2026-11-17_1_short_1", "2026-11-17_1_short_2"])
            beef = json.loads((tmp / "set" / "2026-11-17_1_short_2" / "story.json").read_text())
            self.assertEqual(beef["topic"]["evergreen"], "Dillon Brooks vs Draymond Green")
            self.assertIn('the fresh reason is: "Draymond Green Rips Dillon Brooks"', beef["judged"]["why"])
            plain = json.loads((tmp / "set" / "2026-11-17_1_short_1" / "story.json").read_text())
            self.assertEqual(plain["judged"], {"kind": "contract"})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class ReceiptsFormat(unittest.TestCase):
    """106. D68 (his answers 2026-11-18): the first Short format beyond the breakdown, RECEIPTS
    (quote against quote, the same six beats). The editor proposes it and names the two sides; it
    is used only when the articles hold BOTH sides' own words (his name next to said / told / wrote
    ... in the sentence with the quote marks). In the eval set: Mitchell-Barkley, Green-Brooks and
    Smith-Trump qualify; Arenas-Green (Green never answered) and Howard-Bryant do not."""

    SRC = [{"title": "Mitchell fires back", "summary": "",
            "text": "\"The Cavs aren't built for the playoffs,\" Barkley said on Inside the NBA. "
                    "Donovan Mitchell told reporters, \"Chuck can say what he wants.\" "
                    "Kerr was asked about \"the noise\" and smiled."}]

    def test_spoke(self):
        import script
        self.assertTrue(script.spoke(self.SRC, "Charles Barkley"))
        self.assertTrue(script.spoke(self.SRC, "Donovan Mitchell"))
        self.assertFalse(script.spoke(self.SRC, "LeBron James"))
        mention = [{"title": "", "summary": "", "text": "Barkley said Mitchell's team is \"soft\" again."}]
        self.assertFalse(script.spoke(mention, "Donovan Mitchell"))       # talked about, not talking
        told = [{"title": "", "summary": "", "text": "Barkley told Mitchell on air, \"You are not a closer.\""}]
        self.assertFalse(script.spoke(told, "Donovan Mitchell"))          # talked to, not talking
        self.assertTrue(script.spoke(told, "Charles Barkley"))
        quiet = [{"title": "", "summary": "", "text": "Mitchell said nothing after the game."}]
        self.assertFalse(script.spoke(quiet, "Donovan Mitchell"))         # no quote marks: no receipt

    def setUp(self):
        patcher = patch.dict("os.environ", {"NBA_FORMATS": "receipts"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_off_until_turned_on(self):
        # his answer: off in the daily runs until measured on the eval set
        import script
        import editor
        ok = {"format": "receipts", "sides": ["Charles Barkley", "Donovan Mitchell"]}
        with patch.dict("os.environ", {"NBA_FORMATS": ""}):
            self.assertEqual(script.short_format(ok, self.SRC), ("breakdown", []))
            self.assertEqual(editor.with_formats(editor.PROMPT), editor.PROMPT)        # the editor as before
        self.assertIn(editor.FORMAT_RULE, editor.with_formats(editor.PROMPT))

    def test_format(self):
        import script
        ok = {"format": "receipts", "sides": ["Charles Barkley", "Donovan Mitchell"]}
        self.assertEqual(script.short_format(ok, self.SRC), ("receipts", ["Charles Barkley", "Donovan Mitchell"]))
        one_side = {"format": "receipts", "sides": ["Charles Barkley", "LeBron James"]}
        self.assertEqual(script.short_format(one_side, self.SRC), ("breakdown", []))
        self.assertEqual(script.short_format({"format": "breakdown", "sides": ok["sides"]}, self.SRC), ("breakdown", []))
        self.assertEqual(script.short_format({}, self.SRC), ("breakdown", []))

    def test_note(self):
        import script
        note = " ".join(script.receipts_note(["Charles Barkley", "Donovan Mitchell"]).split())
        self.assertIn("conflict: Charles Barkley's exact words", note)
        self.assertIn("escalation: Donovan Mitchell's exact answer", note)
        self.assertIn("open on the sharpest of their quotes", note)

    def test_the_editor_is_asked(self):
        import editor
        on = editor.with_formats(editor.PROMPT)
        self.assertIn('"format": "receipts" when the headlines show a war of words', on)
        self.assertIn('"format": "breakdown", "sides": []', on)
        self.assertNotIn('"format"', editor.PROMPT)

    def test_the_eval_asks_the_editor_rule(self):
        import eval_run
        import editor
        import script
        asked, saved = [], script.ask_claude
        try:
            script.ask_claude = lambda prompt, model="", where="": asked.append(prompt) or \
                {"format": "receipts", "sides": ["Charles Barkley", "Donovan Mitchell"]}
            story = {"headline": "Mitchell fires back at Barkley", "topic": {"items": [{"title": "Barkley rips Cavs"}]}}
            self.assertEqual(eval_run.editor_format(story)["sides"], ["Charles Barkley", "Donovan Mitchell"])
            self.assertIn(editor.FORMAT_RULE, asked[0])
            with patch.dict("os.environ", {"NBA_FORMATS": ""}):
                self.assertEqual(eval_run.editor_format(story), {})
            self.assertEqual(len(asked), 1)                     # off: no call
        finally:
            script.ask_claude = saved

    def test_the_writer_gets_it(self):
        import script
        harness = Script("test_repair_pass")
        noted, saved = [], (script.short_format, script.receipts_note)
        try:
            script.short_format = lambda judged, sources: ("receipts", ["Luka Doncic", "Hawks fans"])
            script.receipts_note = lambda sides: noted.append(sides) or "\nRECEIPTS"
            short, _ = harness._build(Script.GOOD, draft_beats=Script.GOOD)
            self.assertEqual(noted, [["Luka Doncic", "Hawks fans"]])
            self.assertEqual((short["format"], short["sides"]), ("receipts", ["Luka Doncic", "Hawks fans"]))
            script.short_format = lambda judged, sources: ("breakdown", [])
            noted.clear()
            short, _ = harness._build(Script.GOOD, draft_beats=Script.GOOD)
            self.assertEqual((noted, short["format"]), ([], "breakdown"))     # the breakdown prompt is as before
        finally:
            script.short_format, script.receipts_note = saved


class ScreenNamesOnlyHim(unittest.TestCase):
    """107. D71 (his answers 2026-11-18). Claude's "S" tier (another person of the story) stood in
    when no photo of the man the line is about fitted: Draymond on "Steph Curry tore his oblique"
    (the eval's Arenas Short, twice, 4e could not cure it); in kept runs 19 such pictures where the
    writer's on_screen named someone else. Now the on_screen's men with an NBA career are the only
    known men allowed; a generic or team picture still is; reporters and executives keep D50."""

    WHO = ["Gilbert Arenas", "Steph Curry", "Draymond Green", "Jalen Green", "Carmelo Anthony",
           "Kevin Garnett", "Shams Charania", "Dwyane Wade", "Victor Wembanyama", "Marcus Smart"]
    PLAYERS = set(WHO) - {"Shams Charania"}

    def setUp(self):
        import media
        self.m = media
        self.p = patch.object(media, "career_teams", lambda p: {"some team"} if p in self.PLAYERS else set())
        self.p.start()

    def tearDown(self):
        self.p.stop()

    @staticmethod
    def ph(who, title="x.jpg"):
        return {"kind": "photo", "title": title, "tag": {"v": "C", "s": "game", "t": "t", "who": who} if who else {}}

    def ok(self, photo, screen):
        m = self.m
        return m.shows_only(photo, m.screen_players(screen, self.WHO), self.WHO, screen)

    def test_the_run_cases(self):
        self.assertFalse(self.ok(self.ph("Draymond Green"), "Steph Curry grimacing on the bench"))
        self.assertTrue(self.ok(self.ph("Steph Curry"), "Steph Curry grimacing on the bench"))
        self.assertFalse(self.ok(self.ph("Kevin Garnett"), "Carmelo Anthony speaking"))
        self.assertTrue(self.ok(self.ph("Carmelo Anthony"), "Carmelo Anthony speaking"))

    def test_a_generic_picture_still_may(self):
        self.assertTrue(self.ok(self.ph(""), "Carmelo Anthony speaking"))
        self.assertTrue(self.ok({"kind": "video", "title": "basketball game"}, "Carmelo Anthony speaking"))
        self.assertTrue(self.ok(self.ph("", "Celtics at Wizards 2024-12-020.jpg"), "Carmelo Anthony speaking"))

    def test_d50_reporters_as_before(self):
        self.assertTrue(self.ok(self.ph("Steph Curry"), "Shams Charania on ESPN"))
        self.assertTrue(self.ok(self.ph("Draymond Green"), "HOOK"))
        self.assertTrue(self.ok(self.ph("Draymond Green"), ""))

    def test_a_named_man_outside_the_story(self):
        # kept run 44110628783: Steve Kerr's own photo on "Steve Kerr on the sideline, Warriors playing";
        # a man whose career could not be looked up is no less named (Lendeborg next to Luka)
        self.assertTrue(self.ok(self.ph("Steve Kerr"), "Steve Kerr on the sideline, Draymond Green playing"))
        self.assertFalse(self.ok(self.ph("Steve Kerr"), "Draymond Green on the court"))
        self.PLAYERS.discard("Kevin Garnett")
        try:
            self.assertTrue(self.ok(self.ph("Kevin Garnett"), "Kevin Garnett and Carmelo Anthony"))
        finally:
            self.PLAYERS.add("Kevin Garnett")
        self.assertTrue(self.ok(self.ph("Did Marcus"), "Marcus Smart walking off"))      # an old tag's name
        # the note says only "Steph", the tag says "Stephen Curry", and his career was not looked up
        self.PLAYERS.discard("Steph Curry")
        try:
            self.assertTrue(self.ok(self.ph("Stephen Curry"), "Steph on the bench next to Carmelo Anthony"))
            self.assertFalse(self.ok(self.ph("Kevin Garnett"), "Steph on the bench next to Carmelo Anthony"))
        finally:
            self.PLAYERS.add("Steph Curry")

    def test_two_named_both_allowed(self):
        self.assertTrue(self.ok(self.ph("Victor Wembanyama"), "Dwyane Wade and Victor Wembanyama"))
        self.assertTrue(self.ok(self.ph("Dwyane Wade"), "Dwyane Wade and Victor Wembanyama"))

    def test_spelling_and_namesakes(self):
        self.assertTrue(self.ok(self.ph("Stephen Curry"), "Steph Curry on the bench"))       # an older tag's spelling
        # names_him (D51) counts every story man whose surname the note carries: both Greens, as in the top-ups
        self.assertTrue(self.ok(self.ph("Draymond Green"), "Jalen Green in a Suns jersey"))
        self.assertFalse(self.ok(self.ph("Draymond Green"), "Steph Curry on the bench"))
        self.assertTrue(self.ok(self.ph("", "Steph Curry 2024.jpg"), "Steph Curry on the bench"))
        self.assertFalse(self.ok(self.ph("", "Kevin Garnett 2008-01-13.jpg"), "Carmelo Anthony speaking"))   # the kept run's photo

    def test_the_pick_uses_it(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('screen = beats[i].get("on_screen", "") if i < len(beats) else ""', src)
        # D94 (his answers 2026-11-25): the pick asks line_lock, whose "note" mode is D71's shows_only
        self.assertIn('mode, onscreen = line_lock(line, screen, who_all, short.get("speech_lines") or ())', src)   # D96
        self.assertIn("team_ok = (lambda j, ok=team_ok: ok(j) and lock_allows(cands[j], mode, onscreen, who_all, screen))", src)
        self.assertIn('    note = screen_players(screen, who)', src)          # D91 P1: the note first, then the line
        self.assertIn('    if mode == "note":\n        return shows_only(c, men, who, screen)', src)
        self.assertIn("order = [j for j in order if team_ok(j)]", src)


class TopUpsReadTheNoteFirst(WhoTheWriterPutOnScreen):
    """108. D72 (his answer 2026-11-18). The pick (D71) reads the writer's on_screen, the top-ups
    read the spoken line first: kept run 44078900140, "Still, Wade says he has to get stronger"
    (on_screen "Victor Wembanyama dunking") could show Wembanyama first and Wade next. Now the
    top-ups read the note first when it names a player; otherwise as before (D50, D63)."""

    POOLS = {"Dwyane Wade": [{"kind": "photo", "title": "Dwyane Wade splits defense.jpg", "page": "p-w", "url": "u-w",
                              "author": "a", "team": "", "hoops": True, "tag": {"v": "C", "s": "game", "t": "drives"}}],
             "Victor Wembanyama": [{"kind": "photo", "title": "Victor Wembanyama 2026.jpg", "page": "p-v", "url": "u-v",
                                    "author": "b", "team": "", "hoops": True, "tag": {"v": "C", "s": "game", "t": "dunks"}}]}

    def test_the_run_case(self):
        # D94 (his answer 2026-11-25, a changed rule): Wade SAYS it, so Wade is the line's man
        # (was Wembanyama, the note's man, by D72)
        got = self.fill_screen("Still, Wade says he has to get stronger.", "Victor Wembanyama dunking",
                               self.POOLS, ["Dwyane Wade", "Victor Wembanyama"])
        self.assertEqual(got["title"], "Dwyane Wade splits defense.jpg")
        got = self.fill_screen("Still, he has to get stronger.", "Victor Wembanyama dunking",
                               self.POOLS, ["Dwyane Wade", "Victor Wembanyama"])
        self.assertEqual(got["title"], "Victor Wembanyama 2026.jpg")      # no speaker: D72 as before

    def test_a_note_naming_nobody_as_before(self):
        got = self.fill_screen("Still, Wade says he has to get stronger.", "a crowded arena",
                               self.POOLS, ["Victor Wembanyama", "Dwyane Wade"])
        self.assertEqual(got["title"], "Dwyane Wade splits defense.jpg")

    def test_the_code_reads_the_note_first(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('said = men if mode == "speaker" else screen_players(screens[i] if i < len(screens) else "", who or []) \\', src)


class EveryLeadingHookIsRead(unittest.TestCase):
    """109. D75 (his answer 2026-11-18). truth_order read the first hook and, when it was overstated,
    the next one: when both were overstated the third led UNREAD. Eval (baseline, 23 stories): 4
    such leads; Howard's was false ("Dwight Howard just admitted he left Kobe and the Lakers too
    soon" where he only regrets it and wonders "what if"). Now the next hook is read until one is
    true; all overstated: the overstated one leads and the gate holds (as before)."""

    def order(self, verdicts, texts):
        import script
        read = []

        def check(h, s, lead=""):
            read.append(h["text"])
            if verdicts.get(h["text"]) == "overstated":
                h["overstated"] = "x"
                return "overstated"
            return "ok"
        hooks = [{"text": t, "unsupported_details": []} for t in texts]
        with patch.object(script, "check_hook_truth", check):
            script.truth_order(hooks, [])
        return [h["text"] for h in hooks], read

    def test_the_howard_case(self):
        texts = ["Dwight Howard just said his ego broke the Lakers.",
                 "Dwight Howard never walked out on Kobe, he wonders.",
                 "Dwight Howard just admitted he left Kobe and the Lakers too soon.",
                 "Dwight Howard asks what if he'd stuck it out with Kobe Bryant."]
        bad = {t: "overstated" for t in texts[:3]}
        order, read = self.order(bad, texts)
        self.assertEqual(order[0], texts[3])                  # the true one leads
        self.assertEqual(read, texts)                         # every hook before it was read

    def test_stops_at_the_first_true_one(self):
        texts = ["A one", "B two", "C three", "D four"]
        order, read = self.order({"A one": "overstated"}, texts)
        self.assertEqual((order[0], read), ("B two", ["A one", "B two"]))
        order, read = self.order({}, texts)
        self.assertEqual(read, ["A one"])                     # a good first hook: one call only

    def test_all_overstated_the_gate_holds(self):
        texts = ["A one", "B two", "C three"]
        order, read = self.order({t: "overstated" for t in texts}, texts)
        self.assertEqual(sorted(read), sorted(texts))         # each read once, no endless loop
        self.assertEqual(len(read), 3)

    def test_unreadable_hooks_are_not_read(self):
        import script
        hooks = [{"text": "A", "unsupported_details": [], "overstated": "x"},
                 {"text": "B detail", "unsupported_details": ["radio"]}]
        read = []
        with patch.object(script, "check_hook_truth", lambda h, s, lead="": read.append(h["text"]) or "overstated"):
            script.truth_order(hooks, [])
        self.assertEqual(read, ["A"])                         # a hook with an unsupported detail is never read
        read.clear()
        hooks = [{"text": "C detail", "unsupported_details": ["radio"]}, {"text": "D recycled", "unsupported_details": [], "recycled": True}]
        with patch.object(script, "check_hook_truth", lambda h, s, lead="": read.append(h["text"]) or "ok"):
            script.truth_order(hooks, [])
        self.assertEqual(read, [])                            # as before: such a hook is held by its own check
        hooks = [{"text": "E detail", "unsupported_details": ["radio"]}]
        with patch.object(script, "check_hook_truth", lambda h, s, lead="": read.append(h["text"]) or "ok"):
            script.truth_order(hooks, [])
        self.assertEqual(read, [])


class FinalReadErrorsAreConfirmed(unittest.TestCase):
    """110. Q1 (his answers 2026-11-18). The receipts eval's Kyrie Short was held by an "error" whose
    own text said "...supported; but the Mavs-Kyrie claim is fine. The error: none here."; Howard's
    "Yahoo Sports says Kobe demanded..." was called WRONG WORDS though the line gives the outlet its
    own conclusion. Such false errors stop a Short and stall 4e (nothing to fix, the count never
    drops). Now: a prompt rule, and a second check of each error (all kinds, the main model); a plain
    false moves it to the doubts, marked; in doubt or on a failure it stays an error."""

    SHORT = {"hook": {"text": "Kyrie Irving keeps saying Dallas is home."},
             "beats": [{"say": "Masai Ujiri said they believe in him."}]}
    SRC = [{"publisher": "ESPN", "title": "t", "text": "Mavs president Masai Ujiri said they believe in him."}]
    FAKE = {"line": 1, "kind": "NOT IN THE SOURCES",
            "what": "Masai Ujiri is said to be Mavs president - supported; the error: none here.",
            "evidence": "Masai Ujiri said they believe in him."}
    PIC = {"line": 0, "kind": "WRONG PICTURE", "what": "Kyrie in a Nets jersey on a Dallas line",
           "evidence": "Kyrie Irving keeps saying Dallas is home."}

    def run_read(self, second):
        import final_read as fr
        import script
        calls = []

        def ask(prompt, model="", where=""):
            calls.append((where, model, prompt))
            if where == "final_read":
                return {"errors": [dict(self.FAKE), dict(self.PIC)], "doubts": []}
            return second(prompt)
        with patch.object(script, "ask_claude", ask):
            return fr.read(self.SHORT, [], self.SRC), calls

    def test_a_plain_no_moves_it_to_the_doubts(self):
        res, calls = self.run_read(lambda p: {"error": False, "why": "its own text says it is fine"}
                                   if "none here" in p.split("THE SHORT")[0] else {"error": True})
        self.assertEqual([e["kind"] for e in res["errors"]], ["WRONG PICTURE"])     # the picture error stays
        self.assertEqual(res["verdict"], "REVIEW")
        self.assertTrue(any(d["what"].startswith("(second check: not an error: its own text says it is fine)")
                            for d in res["doubts"]))
        confirms = [c for c in calls if c[0] == "final_read_confirm"]
        self.assertEqual(len(confirms), 2)                                         # every error, of every kind
        import script
        self.assertTrue(all(c[1] == script.CLAUDE_MODEL for c in confirms))        # the main model
        self.assertIn("4. WRONG PICTURE", confirms[0][2])                          # the reader's own rules
        self.assertIn('"kind": "NOT IN THE SOURCES"', confirms[0][2])

    def test_both_false_the_short_passes(self):
        res, _ = self.run_read(lambda p: {"error": False, "why": "fine"})
        self.assertEqual((res["verdict"], res["errors"], len(res["doubts"])), ("PASS", [], 2))

    def test_in_doubt_it_stays(self):
        for second in (lambda p: {"error": True}, lambda p: {}, lambda p: {"error": "false"},
                       lambda p: (_ for _ in ()).throw(RuntimeError("bad json"))):
            res, _ = self.run_read(second)
            self.assertEqual(len(res["errors"]), 2)
            self.assertEqual(res["verdict"], "REVIEW")

    def test_the_limit_still_stops_the_stage(self):
        import script

        def limit(p):
            raise script.UsageLimit("limit")
        with self.assertRaises(script.UsageLimit):
            self.run_read(limit)

    def test_the_prompt_rule(self):
        import final_read as fr
        self.assertIn("A line you checked and found right, or right with nothing wrong in\nit, is never an error", fr.PROMPT)
        self.assertTrue(fr.RULES.startswith("1. NONSENSE") and fr.RULES.endswith("never delivers."))


class EvalCountsPerClass(unittest.TestCase):
    """111. Stage 4 of the class-fix plan (his answers 2026-11-18). The eval gave one number (19 of
    23); now it also counts, per class of FAILURE_CLASSES.md, the Shorts with a problem of it, so a
    fix shows in its own class. On the real baseline: P1/P2 1 (Arenas), F1 2 (Brunson, Howard),
    F2 1 (Howard), R1 1 (Cunningham's unreadable article)."""

    @staticmethod
    def r(**k):
        base = {"made": True, "problem": True, "final_read_full": {"errors": []}, "script_hold": {},
                "gate_not_pass": [], "final_read_failed": ""}
        base.update(k)
        return base

    def test_his_table(self):
        import eval_run as e
        fr = lambda *kinds: {"errors": [{"kind": k} for k in kinds]}
        self.assertEqual(e.classes_of({"made": False, "problem": True}), ["R1"])
        self.assertEqual(e.classes_of(self.r(final_read_full=fr("NOT IN THE SOURCES", "WRONG WORDS"))), ["F1", "F2"])
        self.assertEqual(e.classes_of(self.r(final_read_full=fr("WRONG PICTURE"))), ["P1/P2"])
        self.assertEqual(e.classes_of(self.r(final_read_full=fr("NONSENSE", "BROKEN PROMISE"))), ["S1"])
        self.assertEqual(e.classes_of(self.r(final_read_failed="Claude limit reached: not read")), ["Q1"])
        hard = lambda *n: {"retention_hard": list(n)}
        self.assertEqual(e.classes_of(self.r(script_hold=hard("the hook says more than the sources (x)"))), ["F1"])
        self.assertEqual(e.classes_of(self.r(script_hold=hard("every title says more than the sources (x)"))), ["F1"])
        self.assertEqual(e.classes_of(self.r(script_hold=hard('a quote that no source puts in quote marks: "x"'))), ["F2"])
        for n in ("beat 2 repeats what was already said", "beat 3 repeats the hook",
                  "the last beat does not end with the question", "nothing beyond the headline (no answer)",
                  'broken text in the spoken words: "..."'):
            self.assertEqual(e.classes_of(self.r(script_hold=hard(n))), ["S1"], n)
        self.assertEqual(e.classes_of(self.r(script_hold={"numbers": ["42"]})), ["F1"])
        self.assertEqual(e.classes_of(self.r(script_hold={"details": ["radio"]})), ["F1"])
        self.assertEqual(e.classes_of(self.r(script_hold={"quotes": ["x"]})), ["F2"])
        self.assertEqual(e.classes_of(self.r(script_hold={"banned": ["smash"]})), ["S1"])
        self.assertEqual(e.classes_of(self.r(script_hold={"too_similar_to": "old"})), ["E1"])
        for k, c in (("factual_accuracy", "F1"), ("claim_classification", "F1"), ("source_verification", "F1"),
                     ("title_accuracy", "F1"), ("thumbnail_accuracy", "F1"), ("original_storytelling", "F2"),
                     ("repetition", "E1"), ("technical_quality", "R1"), ("music_licensing", "R1"),
                     ("visual_licensing", "R1"), ("advertiser_suitability", "R1")):
            self.assertEqual(e.classes_of(self.r(gate_not_pass=[k])), [c], k)
            self.assertEqual(e.classes_of(self.r(script_hold={"compliance": {k: ["n"]}})), [c], k)

    def test_never_twice_never_dropped_only_problems(self):
        import eval_run as e
        self.assertEqual(e.classes_of(self.r(gate_not_pass=["final_read", "editorial", "script_checks"])), [])
        self.assertEqual(e.classes_of(self.r(gate_not_pass=["a_new_check"])), ["?"])
        self.assertEqual(e.classes_of(self.r(script_hold={"retention_hard": ["a new hold"]})), ["?"])
        self.assertEqual(e.classes_of(self.r(problem=False, gate_not_pass=["technical_quality"],
                                             details_not_in_sources=1)), [])
        # an old result (no final_read_full): the kinds of its short error lines
        self.assertEqual(e.classes_of({"made": True, "problem": True, "final_read_errors": ["WRONG WORDS: x"]}), ["F2"])

    def test_the_summary_counts_shorts(self):
        import eval_run as e
        rs = [self.r(final_read_full={"errors": [{"kind": "NOT IN THE SOURCES"}, {"kind": "NOT IN THE SOURCES"}]},
                     headline="a", final_read="REVIEW", final_read_errors=["x", "y"], gate="REVIEW",
                     script_held=False, script={"hook": "h"}),
              {"made": False, "problem": True, "headline": "b", "why_not": "unreadable"}]
        out = e.summary("now", rs, 2, ("before", rs[:1]))
        self.assertIn("| F1 | 1 | 1 |", out)            # one Short, though two F1 errors
        self.assertIn("| R1 | 1 | 0 |", out)
        self.assertNotIn("| ? |", out)
        self.assertIn("| a | ⛔ | F1 |", out)


class QuickEval(unittest.TestCase):
    """112. D77 (his answers 2026-11-18: "must the eval remake the whole Short?" - not always). A full
    eval keeps, per story, what a quick one starts from (text only, in the private repo): the script
    and its sources, the voice timing after audio_qc, the pictures after media - all BEFORE the fix
    after the read changes them. A quick eval puts them back and redoes only the stages a change
    touches (from media: media, final read, 4e; from the final read: final read, 4e); no video, no
    gate; its summary is read against its base."""

    def setUp(self):
        import eval_run
        self.e = eval_run
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (eval_run.DATA, eval_run.STATE, eval_run.EVAL, eval_run.make_script, eval_run.git)
        eval_run.DATA, eval_run.STATE = self.tmp / "data", self.tmp / "state"
        eval_run.EVAL = eval_run.STATE / "nba" / "eval"
        eval_run.git = lambda *a: types.SimpleNamespace(returncode=0, stdout="", stderr="")
        for n in (1, 2):
            d = eval_run.EVAL / "set" / f"s{n}"
            d.mkdir(parents=True)
            (d / "story.json").write_text(json.dumps({"id": f"s{n}", "headline": f"Story {n}", "topic": {}, "judged": {}}))
            (d / "sources.json").write_text(json.dumps([{"title": f"src {n}"}]))
        self.ran = []

        def make(story, sources):
            if story["id"] == "s2" and getattr(self, "s2_fails", False):
                raise ValueError("the story's own article could not be read")
            (eval_run.DATA / "sources" / "short_1.json").write_text(json.dumps(sources))
            return {"headline": story["headline"], "hook": {"text": "h " + story["id"]}, "beats": [{"say": "b"}],
                    "compliance": {"verdict": "PASS", "checks": {}}}
        eval_run.make_script = make

        def run(cmd, check=False, **k):
            mod = Path(cmd[-1]).name
            self.ran.append(mod)
            D = eval_run.DATA
            if mod == "tts.py":
                (D / "audio" / "short_1.timing.json").write_text(json.dumps({"duration": 30, "by": "tts"}))
            if mod == "audio_qc.py":
                (D / "audio" / "short_1.timing.json").write_text(json.dumps({"duration": 30, "by": "qc"}))
            if mod == "media.py":
                (D / "media" / "short_1.json").write_text(json.dumps([{"title": "first pick.jpg"}]))
                (D / "media" / "short_1_vs.json").write_text("[]")
            if mod == "final_read.py":
                (D / "review" / "short_1.json").write_text(json.dumps({"verdict": "PASS", "errors": []}))
            if mod == "fix_after_read.py":      # 4e changes the pictures: the base must keep the ones before
                (D / "media" / "short_1.json").write_text(json.dumps([{"title": "after 4e.jpg"}]))
            return types.SimpleNamespace(returncode=0)
        self.p = patch.object(eval_run.subprocess, "run", run)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        e = self.e
        e.DATA, e.STATE, e.EVAL, e.make_script, e.git = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def full(self, label="full1", formats=""):
        with patch.dict("os.environ", {"EVAL_LABEL": label, "NBA_FORMATS": formats, "EVAL_FROM": "", "EVAL_BASE": "", "EVAL_STORIES": ""}):
            self.e.main()

    def quick(self, start, label="q1", base="", formats=""):
        self.ran.clear()
        with patch.dict("os.environ", {"EVAL_LABEL": label, "NBA_FORMATS": formats, "EVAL_FROM": start, "EVAL_BASE": base, "EVAL_STORIES": ""}):
            self.e.main()

    def test_the_full_eval_keeps_its_base_before_4e(self):
        self.full()
        b = self.e.EVAL / "base" / "full1"
        self.assertEqual(json.loads((b / "meta.json").read_text()), {"formats": ""})
        self.assertEqual(json.loads((b / "s1" / "script.json").read_text())["hook"]["text"], "h s1")
        self.assertEqual(json.loads((b / "s1" / "sources.json").read_text()), [{"title": "src 1"}])
        self.assertEqual(json.loads((b / "s1" / "timing.json").read_text())["by"], "qc")      # after audio_qc
        self.assertEqual(json.loads((b / "s1" / "media.json").read_text()), [{"title": "first pick.jpg"}])
        self.assertEqual(sorted(p.suffix for p in b.rglob("*.*")), [".json"] * 11)  # text only (no voice, no video)
        self.assertEqual(self.ran.count("render.py"), 2)                            # the full eval: everything

    def test_quick_from_media(self):
        self.full()
        self.quick("media")
        self.assertEqual(self.ran, ["media.py", "final_read.py", "fix_after_read.py"] * 2)
        r = json.loads((self.e.EVAL / "results" / "q1" / "s1.json").read_text())
        self.assertEqual(r["mode"], "quick from media, on full1")
        self.assertEqual(r["script"]["hook"], "h s1")                                   # the base's script
        summary = (self.e.EVAL / "results" / "q1" / "summary.md").read_text()
        self.assertIn("Before (full1)", summary)                                        # read against its base

    def test_quick_from_the_final_read_puts_the_pictures_back(self):
        self.full()
        seen = []
        run = self.e.subprocess.run

        def spy(cmd, check=False, **k):
            if Path(cmd[-1]).name == "final_read.py":
                seen.append(json.loads((self.e.DATA / "media" / "short_1.json").read_text()))
            return run(cmd, check=check, **k)
        with patch.object(self.e.subprocess, "run", spy):
            self.quick("final_read")
        self.assertEqual(self.ran, ["final_read.py", "fix_after_read.py"] * 2)
        self.assertEqual(seen, [[{"title": "first pick.jpg"}]] * 2)                      # the base's pictures, before 4e

    def test_the_base_matches_formats_and_a_missing_story(self):
        self.s2_fails = True
        self.full("full1")
        self.full("full2", formats="receipts")
        self.quick("media")                                                              # no formats: full1
        r2 = json.loads((self.e.EVAL / "results" / "q1" / "s2.json").read_text())
        self.assertFalse(r2["made"])
        self.assertIn("not in the full eval full1", r2["why_not"])
        self.assertEqual(json.loads((self.e.EVAL / "results" / "q1" / "s1.json").read_text())["mode"],
                         "quick from media, on full1")
        # read against its own base, not the newest label (full2 came after full1)
        self.assertIn("Before (full1)", (self.e.EVAL / "results" / "q1" / "summary.md").read_text())
        self.quick("media", label="q2", formats="receipts")
        self.assertEqual(json.loads((self.e.EVAL / "results" / "q2" / "s1.json").read_text())["mode"],
                         "quick from media, on full2")

    def test_no_base_or_a_wrong_stage_stops(self):
        with self.assertRaises(SystemExit):
            self.quick("media")
        self.full()
        with self.assertRaises(SystemExit):
            self.quick("script")

    def test_the_workflow_inputs(self):
        wf = (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8")
        self.assertIn("EVAL_FROM: ${{ github.event.inputs.from_stage }}", wf)
        self.assertIn("EVAL_BASE: ${{ github.event.inputs.base }}", wf)


class FinalReadDoubtsAreChecked(unittest.TestCase):
    """113. D80 (his answer 2026-11-19). The classfix eval's final read listed 0 errors and 36
    doubts, some of them errors under the agreed rules: Arenas' photos on "Luka grabbed the
    clipboard", Luka in Real Madrid colours on a line naming the Lakers. Now each doubt is checked
    once more, alone (the main model, the reader's rules); D65's and 110's own doubts are left as
    they are; the prompt closes the "another person of the story" door on one man's act."""

    SHORT = {"hook": {"text": "Luka took the clipboard."},
             "beats": [{"say": "The Lakers nearly blew a 31-point lead, and Luka grabbed the clipboard."}]}
    SRC = [{"publisher": "ESPN", "title": "t", "text": "Luka Doncic grabbed the clipboard from Lindsey Harding."}]
    ARENAS = {"line": 1, "what": "Two of the three pictures show Gilbert Arenas while the line is about Luka "
                                 "grabbing the clipboard. He is another person from this story, so this is only a doubt.",
              "evidence": "Luka grabbed the clipboard"}
    STYLE = {"line": 0, "what": "the hook could be bolder", "evidence": ""}
    D65 = {"line": 1, "what": "(evidence not found) a number", "evidence": "x"}

    def run_read(self, doubt_answer, first=None):
        import final_read as fr
        import script
        calls = []

        def ask(prompt, model="", where=""):
            calls.append((where, model, prompt))
            if where == "final_read":
                return first or {"errors": [], "doubts": [dict(self.ARENAS), dict(self.STYLE)]}
            if where == "final_read_confirm":
                return {"error": False, "why": "fine"}
            return doubt_answer(prompt)
        with patch.object(script, "ask_claude", ask):
            return fr.read(self.SHORT, [], self.SRC), calls

    def test_the_classfix_case_becomes_an_error(self):
        res, calls = self.run_read(lambda p: {"error": True, "kind": "WRONG PICTURE", "why": "one man's act"}
                                   if "Gilbert Arenas" in p.split("THE SHORT")[0] else {"error": False})
        self.assertEqual(res["verdict"], "REVIEW")
        self.assertEqual([e["kind"] for e in res["errors"]], ["WRONG PICTURE"])
        self.assertTrue(res["errors"][0]["what"].startswith("(doubt check: an error: one man's act)"))
        self.assertEqual([d["what"] for d in res["doubts"]], ["the hook could be bolder"])
        import script
        checks = [c for c in calls if c[0] == "final_read_doubt"]
        self.assertEqual(len(checks), 2)
        self.assertTrue(all(c[1] == script.CLAUDE_MODEL for c in checks))
        self.assertIn("4. WRONG PICTURE", checks[0][2])
        self.assertNotIn("final_read_confirm", [c[0] for c in calls])     # an error the check found is not re-confirmed

    def test_in_doubt_it_stays_a_doubt(self):
        for ans in (lambda p: {"error": False}, lambda p: {"error": "true", "kind": "WRONG PICTURE"},
                    lambda p: {"error": True, "kind": "UGLY"}, lambda p: {"error": True}, lambda p: {},
                    lambda p: (_ for _ in ()).throw(RuntimeError("bad json"))):
            res, _ = self.run_read(ans)
            self.assertEqual((res["verdict"], len(res["errors"]), len(res["doubts"])), ("PASS", 0, 2))

    def test_the_limit_still_stops_the_stage(self):
        import script

        def limit(p):
            raise script.UsageLimit("limit")
        with self.assertRaises(script.UsageLimit):
            self.run_read(limit)

    def test_d65_and_d76_doubts_are_left_alone(self):
        first = {"errors": [{"line": 1, "kind": "NOT IN THE SOURCES", "what": "a false one",
                             "evidence": "Luka Doncic grabbed the clipboard"}],
                 "doubts": [dict(self.D65)]}
        res, calls = self.run_read(lambda p: {"error": True, "kind": "NOT IN THE SOURCES", "why": "x"}, first)
        self.assertEqual([c[0] for c in calls].count("final_read_doubt"), 0)   # neither is re-checked
        self.assertEqual(res["verdict"], "PASS")
        whats = [d["what"] for d in res["doubts"]]
        self.assertIn("(evidence not found) a number", whats)
        self.assertTrue(any(w.startswith("(second check: not an error: fine)") for w in whats))

    def test_the_prompt_lines(self):
        import final_read as fr
        self.assertIn("on a line saying what one man said or did, a picture\n   of anyone else IS an error, "
                      "another person of this story too.", fr.PROMPT)
        self.assertIn("A doubt says why it is NOT an error under the rules above; something that fits one of the rules\n"
                      "above is an error, not a doubt.", fr.PROMPT)
        self.assertIn("another person of this story too", fr.RULES)          # the checks read the same rule


class CategoryParentsProveIt(MediaCase):
    """114. D79 (his answers 2026-11-19). In the classfix eval Wikidata and Wikipedia were down and
    no photo description in "Category:Luka Dončić" said basketball, so his own category was skipped
    ("nothing in it says basketball") and his photos came untied to him. The category's own parent
    categories prove it (checked live on Commons 2026-11-19: Luka's include "Dallas Mavericks
    players"; Robert Williams's and Dave McMenamin's do not)."""

    PARENTS = {"Category:Luka Dončić": ["Category:1999 births", "Category:Dallas Mavericks players",
                                        "Category:Dončić (surname)"],
               "Category:Robert Williams": [],
               "Category:Dave McMenamin": ["Category:1982 births", "Category:Sports journalists from the United States"],
               "Category:Robert Williams (judge)": ["Category:Justices of the Supreme Court", "Category:Courts in Ohio"]}

    def setUp(self):
        super().setUp()
        fake, self.calls = self.m.get, []

        def get(url, timeout=30):
            q = dict(urllib.parse.parse_qsl(url.split("?", 1)[1])) if "?" in url else {}
            if "wikidata.org" in url or "wikipedia.org" in url:
                raise OSError("down")                               # as in the classfix eval
            if q.get("prop") == "categories":
                self.calls.append(q.get("titles"))
                if q.get("titles") == "Category:Broken":
                    raise OSError("down")
                ps = self.PARENTS.get(q.get("titles"), [])
                return json.dumps({"query": {"pages": {"1": {"title": q.get("titles"),
                                                             "categories": [{"title": c} for c in ps]}}}}).encode()
            return fake(url, timeout)
        self.m.get = get

    def test_the_parents(self):
        p = self.m.parents_say_basketball
        self.assertTrue(p("Category:Luka Dončić"))
        self.assertFalse(p("Category:Robert Williams"))
        self.assertFalse(p("Category:Dave McMenamin"))
        self.assertFalse(p("Category:Robert Williams (judge)"))   # "court" proves nothing here
        self.assertFalse(p("Category:Broken"))                    # a failure: no proof, as before

    def test_the_classfix_case(self):
        self.m._wiki_title.clear()
        self.m._wikidata.clear()
        self.m.PHOTO_STATS.clear()
        got = sorted(f["title"] for f in self.m.category_files("Luka Dončić"))
        self.assertEqual(got, ["File:LD 2019.jpg", "File:LD 2025.jpg", "File:LD 2026.jpg"])
        self.assertIn("Category:Luka Dončić", self.calls)

    def test_a_proven_category_costs_no_request(self):
        CATS["Category:Jaylen Brown"] = ([_photo("File:JB.jpg", "Jaylen Brown, basketball, Celtics")], [])
        try:
            self.m.PHOTO_STATS.clear()
            got = [f["title"] for f in self.m.category_files("Jaylen Brown")]
        finally:
            del CATS["Category:Jaylen Brown"]
        self.assertEqual(got, ["File:JB.jpg"])
        self.assertEqual(self.calls, [])                    # its photos already say basketball


class ChosenStoriesEval(QuickEval):
    """115. D77 (his answer 2026-11-19): a fix aimed at a few cases (Luka's photos, the four
    overstated hooks) is checked on those stories only, in 10-30 minutes instead of hours; the
    whole set stays for big decisions."""

    def run_env(self, **env):
        base = {"EVAL_LABEL": "", "NBA_FORMATS": "", "EVAL_FROM": "", "EVAL_BASE": "", "EVAL_STORIES": ""}
        base.update(env)
        self.ran.clear()
        with patch.dict("os.environ", base):
            self.e.main()

    def test_only_the_chosen_run_and_read_against_the_newest(self):
        self.full()                                            # full1: both stories, a base
        self.run_env(EVAL_LABEL="pick1", EVAL_STORIES="s2")
        self.assertEqual(self.ran.count("tts.py"), 1)          # one story only
        res = self.e.EVAL / "results"
        self.assertEqual(sorted(p.name for p in (res / "pick1").glob("*.json")), ["s2.json"])
        summary = (res / "pick1" / "summary.md").read_text()
        self.assertIn("Before (full1)", summary)               # the same story of the newest eval
        self.assertIn("of 1", summary)
        self.assertEqual(json.loads((res / "index.json").read_text()), ["full1"])   # never a "previous"
        self.assertFalse((self.e.EVAL / "base" / "pick1").exists())                 # never a base
        self.assertEqual(self.e.newest_base(""), "full1")

    def test_quick_on_chosen_stories(self):
        self.full()
        self.run_env(EVAL_LABEL="pick2", EVAL_STORIES="s1", EVAL_FROM="final_read")
        self.assertEqual(self.ran, ["final_read.py", "fix_after_read.py"])
        r = json.loads((self.e.EVAL / "results" / "pick2" / "s1.json").read_text())
        self.assertEqual(r["mode"], "quick from final_read, on full1")

    def test_an_unknown_story_stops(self):
        self.full()
        with self.assertRaises(SystemExit):
            self.run_env(EVAL_LABEL="pick3", EVAL_STORIES="s1, nope")

    def test_the_workflow_input(self):
        wf = (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8")
        self.assertIn("EVAL_STORIES: ${{ github.event.inputs.stories }}", wf)


class FactSheetFirst(Script):
    """116. D82 (his answers 2026-11-19; D81a, "pull quotes first, then write"). The classfix eval
    held Shorts whose report was voiced as fact (Murray's hook: Windhorst's "distressed asset"
    report said plainly): the writer judged its own claims while writing. Now a separate call pulls
    the fact sheet first; the writer and the three editors get it; every check stays as it was."""

    SHEET = {"facts": [
        {"text": "Atlanta drafted Doncic third in 2018 and traded his rights to Dallas", "kind": "confirmed",
         "who": "", "source": 1},
        {"text": "You all wish you would have had me.", "kind": "CONFIRMED", "who": "Luka Doncic", "source": 1},
        {"text": "Luka called the Hawks a joke", "kind": "REPORTED", "who": "Yahoo", "source": 1},   # not in the article
        {"text": "One fan replied", "kind": "MADE UP", "who": "Yahoo Sports", "source": 1},
        {"text": "You all wish you would have had me.", "kind": "CONFIRMED", "who": "x", "source": 9}]}

    def build_with(self, sheet_answer):
        import nbadata
        import script
        prompts = []
        draft = {"hooks": [{"text": LUKA_HOOK, "formula": "The Receipt"}],
                 "strategy": {"kind": "beef", "central_question": "Who was right?", "headline_gap": "The trade."},
                 "angles": ["a"], "angle": "a", "beats": copy.deepcopy(LUKA_BEATS),
                 "titles": ["Luka Doncic TROLLED Hawks fans"], "thumbnail_text": "LUKA vs HAWKS FANS",
                 "receipt": "", "sources_used": [1],
                 "claims": [{"text": "Doncic told fans 'You all wish you would have had me.'", "status": "CONFIRMED",
                             "source": 1}],
                 "queries": ["q"], "description": "d\nd", "tags": ["t"]}

        def fake(prompt, model=""):
            if "pull its FACT SHEET" in prompt:
                prompts.append(("facts", model, prompt))
                return sheet_answer()
            if "THE PROBLEMS TO FIX" in prompt:
                prompts.append(("repair", model, prompt))
                return {"beats": copy.deepcopy(self.GOOD)}
            if "sound human" in prompt:
                prompts.append(("humanize", model, prompt))
                return {}
            if "scrolling Shorts" in prompt:
                return {"order": [1]}
            if "You write YouTube Shorts scripts" in prompt:
                prompts.append(("writer", model, prompt))
            return copy.deepcopy(draft)
        saved = (script.ask_claude, script.gather_sources, nbadata.annotate, script.SOURCES_OUT)
        import tempfile
        script.SOURCES_OUT = Path(tempfile.mkdtemp()) / "sources"
        script.ask_claude = fake
        script.gather_sources = lambda topic, editor, tid: [
            {"publisher": "Yahoo Sports", "title": "Luka trolls Hawks fans", "link": "https://sports.yahoo.com/x",
             "url": "https://sports.yahoo.com/x", "text": self.TEXT, "trusted": True, "tier": 1, "main": True}]
        nbadata.annotate = lambda claims: None
        try:
            editor = {"topics": [{"headline": "Luka Doncic trolls Hawks fans", "search_phrases": []}],
                      "ranked": [{"id": 0, "virality": 8}]}
            short = script.build_short(1, 0, editor, "voice", {"hooks": [{"name": "x", "shape": "y", "example": "z"}],
                                                               "rules": ["r"]})
            return short, prompts
        finally:
            shutil.rmtree(script.SOURCES_OUT.parent, ignore_errors=True)
            script.ask_claude, script.gather_sources, nbadata.annotate, script.SOURCES_OUT = saved

    def test_the_sheet_reaches_the_writer_and_the_editors(self):
        import script
        short, prompts = self.build_with(lambda: copy.deepcopy(self.SHEET))
        self.assertEqual(prompts[0][0], "facts")                               # before the writer
        self.assertEqual(prompts[0][1], script.CLAUDE_MODEL)                   # the main model
        self.assertEqual([f["text"] for f in short["facts"]],                   # word for word only
                         ["Atlanta drafted Doncic third in 2018 and traded his rights to Dallas",
                          "You all wish you would have had me.", "One fan replied"])
        self.assertEqual([f["kind"] for f in short["facts"]], ["CONFIRMED", "CONFIRMED", "UNVERIFIED"])
        for who in ("writer", "humanize", "repair"):
            p = next(x[2] for x in prompts if x[0] == who)
            self.assertIn('[F2] CONFIRMED (Luka Doncic) [source 1]: "You all wish you would have had me."', p, who)
            self.assertIn("is said WITH its who in the same sentence", p, who)
            self.assertNotIn("called the Hawks a joke", p, who)

    def test_no_sheet_every_prompt_as_before(self):
        for answer in (lambda: {}, lambda: {"facts": "x"}, lambda: (_ for _ in ()).throw(RuntimeError("bad json"))):
            short, prompts = self.build_with(answer)
            self.assertEqual(short["facts"], [])
            for who in ("writer", "humanize", "repair"):
                self.assertNotIn("FACT SHEET", next(x[2] for x in prompts if x[0] == who))

    def test_the_limit_still_stops(self):
        import script

        def limit():
            raise script.UsageLimit("limit")
        with self.assertRaises(script.UsageLimit):
            self.build_with(limit)

    def test_the_four_takers_and_the_checks(self):
        src = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertEqual(src.count("sources=src_text"), 4)      # writer, humanize, hook retry, repair
        self.assertEqual(src.count('.replace("SOURCES_TEXT", format_sources(sources))'), 3)   # the checks: untouched
        import script
        self.assertEqual(script.facts_block([]), "")


class OneJsonOrAskAgain(unittest.TestCase):
    """117. D83 (his answers 2026-11-19). The classfix eval: "hook truth check skipped: Extra data"
    (two JSON objects) or "broken JSON" 14 times, so the hook kept its place unread. Now every call
    asks once more when its answer is not one JSON object; a second such answer fails as before."""

    def ask(self, answers):
        import script
        calls = []

        def run(cmd, input="", capture_output=True, text=True, cwd=None, timeout=None):
            calls.append(cmd)
            return types.SimpleNamespace(returncode=0, stderr="",
                                         stdout=json.dumps({"result": answers[len(calls) - 1]}))
        with patch.object(script.subprocess, "run", run), patch.object(script, "log_claude_usage", lambda *a: None):
            try:
                return script.ask_claude("p"), len(calls)
            except ValueError as exc:
                return exc, len(calls)

    def test_one_object_one_call(self):
        self.assertEqual(self.ask(['Sure: {"verdict": "ok"} done']), ({"verdict": "ok"}, 1))

    def test_two_objects_ask_again(self):
        got, n = self.ask(['{"verdict": "ok"}\n\n{"verdict": "overstated"}', '{"verdict": "overstated", "why": "x"}'])
        self.assertEqual((got, n), ({"verdict": "overstated", "why": "x"}, 2))

    def test_no_object_ask_again_then_fail(self):
        got, n = self.ask(["I cannot judge this.", "still no json"])
        self.assertIsInstance(got, ValueError)
        self.assertEqual(n, 2)

    def test_the_limit_is_not_retried(self):
        import script

        def run(*a, **k):
            return types.SimpleNamespace(returncode=1, stdout="", stderr="You've hit your usage limit")
        with patch.object(script.subprocess, "run", run):
            with self.assertRaises(script.UsageLimit):
                script.ask_claude("p")


class ModelIsRecorded(unittest.TestCase):
    """118. D85 (his yes 2026-11-19): the checks ran on the floating aliases "sonnet"/"haiku"; the
    exact model each call ran is recorded and printed once, so it can be pinned on purpose."""

    def test_every_copy_records_and_prints_once(self):
        import io, contextlib, tempfile, importlib
        import script, media, editor, skills
        out = json.dumps({"usage": {"input_tokens": 3, "output_tokens": 2}, "total_cost_usd": 0.1,
                          "duration_ms": 2000, "num_turns": 1,
                          "modelUsage": {"claude-sonnet-x-1": {}, "claude-haiku-y-2": {}}})
        for mod in (script, media, editor, skills):
            with tempfile.TemporaryDirectory() as d:
                fake = Path(d) / "src" / "m.py"
                with patch.object(mod, "__file__", str(fake)), patch.object(mod, "SEEN_MODELS", set()):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        mod.log_claude_usage(out, "w")
                        mod.log_claude_usage(out, "w")
                    rows = [json.loads(l) for l in (Path(d) / "data" / "claude_usage.jsonl").read_text().splitlines()]
                self.assertEqual(len(rows), 2, mod.__name__)
                self.assertEqual(rows[0]["models"], ["claude-haiku-y-2", "claude-sonnet-x-1"], mod.__name__)
                self.assertEqual((rows[0]["where"], rows[0]["in"], rows[0]["out"], rows[0]["seconds"]),
                                 ("w", 3, 2, 2), mod.__name__)
                printed = [l for l in buf.getvalue().splitlines() if l.startswith("[model]")]
                self.assertEqual(printed, ["[model] w: claude-haiku-y-2", "[model] w: claude-sonnet-x-1"],
                                 mod.__name__)

    def test_no_model_usage_changes_nothing_else(self):
        import io, contextlib, tempfile
        import script
        with tempfile.TemporaryDirectory() as d:
            with patch.object(script, "__file__", str(Path(d) / "src" / "m.py")), \
                    patch.object(script, "SEEN_MODELS", set()):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    script.log_claude_usage(json.dumps({"usage": {}}), "w")
                row = json.loads((Path(d) / "data" / "claude_usage.jsonl").read_text())
        self.assertEqual(row["models"], [])
        self.assertEqual(buf.getvalue(), "")


class AptPackagesCached(unittest.TestCase):
    """119. D84b (his answers 2026-11-19): the slow Ubuntu mirror took 20-31 minutes of an eval to
    download ffmpeg and espeak-ng (110 MB at 62 kB/s). The .deb files now come from GitHub's own
    cache; apt installs them itself, so the versions are what a fresh install would give."""

    def test_eval_and_collect(self):
        for name in ("eval.yml", "collect.yml"):
            wf = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
            cache = wf.index("path: ~/apt-debs")
            self.assertIn("key: apt-debs-v1\n", wf[cache:cache + 60], name)       # one fixed key
            self.assertNotIn("restore-keys", wf[cache:cache + 60], name)
            restore = wf.index("sudo cp ~/apt-debs/*.deb /var/cache/apt/archives/ 2>/dev/null || true")
            install = wf.index("sudo apt-get install -y -q -o APT::Keep-Downloaded-Packages=true espeak-ng ffmpeg")
            keep = wf.index("cp /var/cache/apt/archives/*.deb ~/apt-debs/ 2>/dev/null || true")
            self.assertLess(cache, wf.index("name: Install voice engine"), name)   # restored before
            self.assertLess(wf.index("sudo apt-get update -q\n"), restore, name)
            self.assertLess(restore, install, name)
            self.assertLess(install, keep, name)
            self.assertNotIn("apt-get install -y -q espeak-ng ffmpeg", wf, name)   # no second install


class NameSuffixes(unittest.TestCase):
    """120. D73 (his answers 2026-11-19, class P1): run 2026-11-12_43145065648 made "Gary Trent Jr."
    the story person "Gary Trent", and Wikipedia's "Gary Trent" is his father (1974)."""

    def sources(self, d, n, texts):
        (Path(d) / "sources").mkdir(parents=True, exist_ok=True)
        (Path(d) / "sources" / f"short_{n}.json").write_text(
            json.dumps([{"title": t, "summary": "", "text": ""} for t in texts]), encoding="utf-8")

    def test_articles_give_the_suffix(self):
        import tempfile, media
        with tempfile.TemporaryDirectory() as d, patch.object(media, "DATA", Path(d)):
            self.sources(d, 1, ["Gary Trent Jr. case", "Bucks: Gary Trent Jr. suspended"])
            self.sources(d, 2, ["Gary Trent Jr. case", "Gary Trent was drafted in 1995"])      # a bare one
            self.sources(d, 3, ["Gary Trent Jr. case", "Gary Trent Sr. said"])                 # mixed
            self.sources(d, 4, ["Bucks rumors"])                                                # never named
            self.assertEqual(media.suffix_from_sources("Gary Trent", 1), "Gary Trent Jr.")
            self.assertEqual(media.suffix_from_sources("Gary Trent", 2), "Gary Trent")
            self.assertEqual(media.suffix_from_sources("Gary Trent", 3), "Gary Trent")
            self.assertEqual(media.suffix_from_sources("Gary Trent", 4), "Gary Trent")
            self.assertEqual(media.suffix_from_sources("Gary Trent", 9), "Gary Trent")         # no text: as today

    def test_people_uses_it_and_keeps_the_count(self):
        import tempfile, media
        short = {"n": 1, "headline": "Gary Trent suspended", "hook": "Gary Trent is out.",
                 "beats": [{"say": "Trent and Kawhi Leonard. Kawhi Leonard again."}]}
        with tempfile.TemporaryDirectory() as d, patch.object(media, "DATA", Path(d)), \
                patch.object(media, "real_people", lambda ranked: None):
            self.sources(d, 1, ["Gary Trent Jr. suspended"])
            self.assertEqual(media.people(short), ["Gary Trent Jr.", "Kawhi Leonard"])   # 2 + 5 headline vs 2
            self.sources(d, 1, ["Gary Trent suspended"])
            self.assertEqual(media.people(short), ["Gary Trent", "Kawhi Leonard"])

    def test_surname_is_before_the_suffix(self):
        import media
        self.assertEqual(media.name_parts("Gary Trent Jr."), ["gary", "trent"])
        self.assertEqual(media.name_parts("Trey Murphy III"), ["trey", "murphy"])
        self.assertEqual(media.name_parts("Stephen A. Smith"), ["stephen", "a.", "smith"])
        self.assertTrue(media.names_him("Trent hits the three", "Gary Trent Jr."))
        self.assertEqual(media.photo_owner({"title": "Trent drives (2024)"}, ["Gary Trent Jr.", "Kawhi Leonard"]),
                         "Gary Trent Jr.")


class SmokeTest(unittest.TestCase):
    """121. D77 (his answers 2026-11-19): a whole Short made after every code push, without Claude."""

    def test_prepare_puts_the_story_back(self):
        import tempfile, smoke
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = root / "state" / "nba" / "smoke"
            story.mkdir(parents=True)
            pic = lambda k: {"kind": "photo", "url": f"u{k}", "title": f"t{k}", "file": f"data/media/short_1/p{k}.jpg"}
            (story / "script.json").write_text(json.dumps({"headline": "h"}))
            (story / "media.json").write_text(json.dumps([dict(pic(0), alts=[pic(1)]), None, pic(2)]))
            (story / "media_vs.json").write_text(json.dumps([pic(3), pic(4)]))
            for mood, files in (("b_mood", ["a.mp3"]), ("a_mood", ["z.mp3", "c.mp3", "notes.txt"])):
                (root / "music_library" / mood).mkdir(parents=True)
                for f in files:
                    (root / "music_library" / mood / f).write_text("x")
            got = []
            def download(url, path):
                got.append(url)
                if url == "u2":
                    return False
                Path(path).write_text("img")
                return True
            with patch.multiple(smoke, ROOT=root, DATA=root / "data", STORY=story, LIBRARY=root / "music_library"):
                failed = smoke.prepare(download)
            self.assertEqual(sorted(got), ["u0", "u1", "u2", "u3", "u4"])            # alts and the VS card too
            self.assertEqual(failed, ["t2"])                                         # the network, reported
            self.assertTrue((root / "data" / "scripts" / "short_1.json").exists())
            self.assertTrue((root / "data" / "media" / "short_1_vs.json").exists())
            music = json.loads((root / "data" / "media" / "short_1_music.json").read_text())
            self.assertEqual(music["title"], "c")                                    # the first track, by name
            self.assertTrue((root / music["file"]).exists())

    def test_no_library_no_music(self):
        import tempfile, smoke
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with patch.multiple(smoke, ROOT=root, DATA=root / "data", STORY=root / "s", LIBRARY=root / "none"):
                self.assertEqual(smoke.prepare(lambda u, p: True), [])
            self.assertFalse((root / "data" / "media" / "short_1_music.json").exists())

    def test_check_counts_only_technical(self):
        import tempfile, smoke
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "video").mkdir()
            (root / "gate").mkdir()
            with patch.object(smoke, "DATA", root):
                self.assertEqual(len(smoke.check()), 2)                              # no MP4, no gate result
                (root / "video" / "short_1.mp4").write_text("v")
                gate = {"verdict": "REVIEW", "checks": {
                    "technical_quality": {"verdict": "PASS", "notes": []},
                    "final_read": {"verdict": "REVIEW", "notes": ["no final read"]},
                    "music_licensing": {"verdict": "REVIEW", "notes": ["x"]}}}
                (root / "gate" / "short_1.json").write_text(json.dumps(gate))
                self.assertEqual(smoke.check(), [])                                  # content checks do not count
                gate["checks"]["technical_quality"] = {"verdict": "REVIEW", "notes": ["only 70% heard"]}
                (root / "gate" / "short_1.json").write_text(json.dumps(gate))
                self.assertEqual(smoke.check(), ["technical check: only 70% heard"])

    def test_the_workflow(self):
        wf = (ROOT / ".github" / "workflows" / "smoke.yml").read_text(encoding="utf-8")
        on = wf[wf.index("on:"):wf.index("permissions:")]
        self.assertIn("push:", on)
        self.assertIn("branches: [main]", on)
        for p in ('"src/**"', '".github/workflows/**"', '"requirements*.txt"'):
            self.assertIn(p, on)
        self.assertNotIn("tests/", on)                                               # a test change only: no smoke
        for x in ("CLAUDE_CODE_OAUTH_TOKEN", "claude.ai/install", "src/script.py", "src/media.py",
                  "src/final_read.py", "src/fix_after_read.py", "src/editor.py"):
            self.assertNotIn(x, wf)                                                  # no Claude at all
        self.assertNotIn("state.py save", wf)                                        # never saves back
        for x in ("youtube", "upload-artifact", "src/upload"):
            self.assertNotIn(x, wf.lower())                                          # never uploads
        steps = [wf.index(x) for x in ("python src/smoke.py prepare", "python src/tts.py", "python src/audio_qc.py",
                                       "python src/render.py", "python src/gate.py", "python src/smoke.py check")]
        self.assertEqual(steps, sorted(steps))
        self.assertIn("contents: read", wf)


class TrendsAboutHim(unittest.TestCase):
    """122. D86 (his answer 2026-11-24, class E1): every trend hit of the 31 kept runs."""

    def test_real_hits(self):
        import signals
        real = [  # (run, star_names, trending search, right?)
            ("2026-11-11_43080115985", ["Bronny James 3.6"], "los angeles lakers bronny james", True),
            ("2026-11-11_43088629255", ["Bronny James 3.6"], "los angeles lakers bronny james", True),
            ("2026-11-12_43145065648", ["Caleb Wilson 0.3"], "caleb wilson", True),
            ("2026-11-12_43317261723", ["Stephen Curry 5.4", "Caleb Wilson 0.6"], "caleb wilson", True),
            ("2026-11-13_43353547001", ["Jaylen Brown 3.4", "Jayson Tatum 2.7"], "tacko fall", False),
            ("2026-11-13_43485568700", ["Jaylen Brown 3.7", "Jayson Tatum 3.1", "Doc Rivers 2.5"], "philip rivers", False),
        ]
        for run, stars, query, right in real:
            with self.subTest(run, query=query):
                # the headlines were not kept: Tacko Fall's may well name Tatum and the Celtics (a
                # headline alone no longer counts); Philip Rivers's are about the NFL
                news = {"tacko fall": ["Tacko Fall, Jayson Tatum and the Celtics react"],
                        "philip rivers": ["Philip Rivers back with the Colts"]}.get(query, [])
                self.assertEqual(signals.trend_matches({"star_names": stars}, {"query": query, "news": news}), right)

    def test_surname_needs_basketball(self):
        import signals
        doc = {"star_names": ["Doc Rivers 2.5"]}
        self.assertTrue(signals.trend_matches(doc, {"query": "doc rivers", "news": []}))           # full name
        self.assertTrue(signals.trend_matches(doc, {"query": "rivers bucks", "news": []}))         # + basketball
        self.assertTrue(signals.trend_matches(doc, {"query": "rivers", "news": ["Rivers on the Bucks"]}))
        self.assertFalse(signals.trend_matches(doc, {"query": "philip rivers", "news": ["Colts QB returns"]}))
        self.assertFalse(signals.trend_matches(doc, {"query": "bucks news", "news": ["Doc Rivers fired"]}))  # headline only


class OneSurnameRule(unittest.TestCase):
    """123. D87 (his answers 2026-11-24, class E1): run 2026-11-13_43407418420 had a Cade Cunningham
    story and a Sophie Cunningham story; "cunningham" credited each with the other's signals."""

    def setUp(self):
        import signals
        self.s = signals
        self.addCleanup(signals.OWNERS.clear)
        signals.OWNERS.clear()

    def owners(self, resolved):
        self.s.OWNERS.clear()
        self.s.OWNERS.update(self.s.surname_owners(resolved))

    def test_shared_surname_needs_the_full_name_everywhere(self):
        sophie = {"star_names": ["Sophie Cunningham 3.0"], "headline": "Sophie Cunningham says the fan was ejected",
                  "items": [{"title": "Sophie Cunningham on the ejected fan"}]}
        cade = {"star_names": ["Cade Cunningham 5.0"], "headline": "Cade Cunningham scores 52", "items": []}
        self.assertEqual(self.s.star_keys(sophie), {"cunningham"})                 # nothing known: as before
        self.owners({"Sophie Cunningham": "Sophie Cunningham", "Cade Cunningham": "Cade Cunningham"})
        self.assertEqual(self.s.star_keys(sophie), {"sophie cunningham"})          # Reddit, Trends
        self.assertEqual(self.s.star_keys(cade), {"cade cunningham"})
        self.assertIn("sophie cunningham", self.s.topic_keys(sophie))               # YouTube, search
        self.assertNotIn("cunningham", self.s.topic_keys(sophie))
        self.assertEqual(self.s.reddit_heat(sophie, ["Cade Cunningham drops 52 on the Lakers"]), 0.0)
        self.assertFalse(self.s.trend_matches(sophie, {"query": "cunningham pistons", "news": []}))
        self.assertTrue(self.s.trend_matches(cade, {"query": "cade cunningham", "news": []}))

    def test_one_page_is_one_man(self):
        self.owners({"Steph Curry": "Stephen Curry", "Stephen Curry": "Stephen Curry",
                     "Jalen Green": "Jalen Green (basketball)", "Gary Trent Jr.": "Gary Trent Jr."})
        self.assertEqual(self.s.star_keys({"star_names": ["Stephen Curry 9"]}), {"curry"})   # not shared
        self.assertEqual(self.s.surname_of("Jalen Green (basketball)"), "green")
        self.assertEqual(self.s.surname_of("Gary Trent Jr."), "trent")
        self.assertEqual(self.s.surname_of("Luka Dončić"), "doncic")
        self.assertEqual(self.s.star_keys({"star_names": ["Luka Dončić 9"]}), {"dončić"})    # key as before

    def test_unique_surname_and_the_old_list_unchanged(self):
        self.owners({"Joel Embiid": "Joel Embiid", "LeBron James": "LeBron James"})
        self.assertEqual(self.s.star_keys({"star_names": ["Joel Embiid 8"]}), {"embiid"})
        self.assertEqual(self.s.star_keys({"star_names": ["LeBron James 9"]}), {"lebron james"})   # common list

    def test_star_power_runs_before_the_signals(self):
        src = (ROOT / "src" / "signals.py").read_text(encoding="utf-8")
        main = src[src.index("def main()"):]
        star = main.index("OWNERS.update(surname_owners(resolved))")
        self.assertLess(main.index("OWNERS.clear()"), star)
        for later in ("raw[i] = sum(", "t[\"search_hits\"] =", "trend_matches(t, g)", "reddit_heat(t, "):
            self.assertLess(star, main.index(later), later)


class UnknownCareerLocksTheLine(unittest.TestCase):
    """124. D92 (his answers 2026-11-25, class P1). The lock "a line about one man shows no other
    known man" (D50, D71, D72) held only when the man's NBA career was FOUND; when the lookup did not
    answer he was treated like a reporter and anyone in the story could stand in (factsheet eval:
    Curry on rookie Lendeborg's line, Arenas on Luka's; both careers are found today). Now an
    unknown career locks too; an answered "no NBA career" keeps D50."""

    def setUp(self):
        import media
        self.m = media
        self.saved = {k: dict(getattr(media, k)) for k in ("_wikidata", "_wiki_title", "_person_cache", "_teams", "_career")}
        self.unknown = set(media._career_unknown)
        media._career_unknown.clear()

    def tearDown(self):
        for k, v in self.saved.items():
            getattr(self.m, k).clear()
            getattr(self.m, k).update(v)
        self.m._career_unknown.clear()
        self.m._career_unknown.update(self.unknown)

    def test_the_person_check_unreachable_marks_every_name(self):
        m = self.m
        with patch.object(m, "PEOPLE_CHECK", True), patch.object(m, "get", side_effect=RuntimeError("down")), \
                redirect_stdout(io.StringIO()):
            self.assertIsNone(m.real_people(["Brian Windhorst", "Yaxel Lendeborg"]))
        self.assertTrue(m.career_unknown("Brian Windhorst"))
        self.assertTrue(m.career_unknown("Yaxel Lendeborg"))
        self.assertEqual(m.screen_players("Brian Windhorst on ESPN", ["Gary Trent", "Brian Windhorst"]), ["Brian Windhorst"])

    def test_a_page_without_a_wikidata_item_is_unknown_and_an_answer_clears_it(self):
        m = self.m
        pages = {"pages": {"1": {"title": "Yaxel Lendeborg", "pageprops": {"wikibase-shortdesc": "American basketball player"}}}}
        with patch.object(m, "PEOPLE_CHECK", True), patch.object(m, "get", return_value=json.dumps({"query": pages})):
            m.real_people(["Yaxel Lendeborg"])
        self.assertIn("Yaxel Lendeborg", m._career_unknown)
        m._person_cache.pop("Yaxel Lendeborg", None)
        pages["pages"]["1"]["pageprops"]["wikibase_item"] = "Q1"
        with patch.object(m, "PEOPLE_CHECK", True), patch.object(m, "get", return_value=json.dumps({"query": pages})):
            m.real_people(["Yaxel Lendeborg"])
        self.assertNotIn("Yaxel Lendeborg", m._career_unknown)

    def test_a_failed_career_request_is_unknown(self):
        m = self.m
        m._wikidata["Luka Doncic"] = "Q-test-luka"
        m._wiki_title["Luka Doncic"] = "Luka Dončić"
        m._teams.pop("Q-test-luka", None)
        with patch.object(m, "get", side_effect=RuntimeError("down")), redirect_stdout(io.StringIO()):
            self.assertTrue(m.career_unknown("Luka Doncic"))
        self.assertTrue(m.locks_line("Luka Doncic"))

    def one_side_fails(self, failing: str) -> bool:
        """Wikidata OR Wikipedia's infobox fails, the other answers with no NBA team: still unknown."""
        m = self.m
        m._career_unknown.clear()
        m._wikidata["Luka Doncic"] = "Q-test-luka2"
        m._wiki_title["Luka Doncic"] = "Luka Dončić"
        m._teams.pop("Q-test-luka2", None)
        m._career.pop("Q-test-luka2", None)
        answers = {"wikidata": json.dumps({"claims": {"P54": []}}),
                   "wikipedia": json.dumps({"query": {"pages": {"1": {"revisions": [{"slots": {"main": {"*": "{{Infobox}}"}}}]}}}})}

        def fake(url, timeout=30):
            side = "wikidata" if "wikidata.org" in url else "wikipedia"
            if side == failing:
                raise RuntimeError("down")
            return answers[side]
        with patch.object(m, "get", fake), redirect_stdout(io.StringIO()):
            return m.career_unknown("Luka Doncic")

    def test_either_career_request_failing_is_unknown(self):
        self.assertTrue(self.one_side_fails("wikidata"))
        self.assertTrue(self.one_side_fails("wikipedia"))
        self.assertFalse(self.one_side_fails("none"))         # both answered, no NBA team: not unknown

    def test_an_answered_no_career_keeps_d50(self):
        m = self.m
        with patch.object(m, "career_teams", lambda p: set()):
            self.assertFalse(m.career_unknown("Shams Charania"))
            self.assertFalse(m.locks_line("Shams Charania"))
            self.assertEqual(m.screen_players("Shams Charania on ESPN", ["Steph Curry", "Shams Charania"]), [])
        with patch.object(m, "career_teams", lambda p: {"golden state warriors"} if p == "Steph Curry" else set()):
            m._career_unknown.add("Steph Curry")              # a known career is never "unknown"
            self.assertFalse(m.career_unknown("Steph Curry"))
            self.assertTrue(m.locks_line("Steph Curry"))

    def test_both_stages_use_it_and_the_record_keeps_it(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn("return named if any(locks_line(p) for p in named) else []", src)
        self.assertIn("players = [p for p in said if locks_line(p)]", src)
        self.assertIn("for person in [p for p in players if career_teams(p)]:", src)   # D49/D67 as before
        self.assertIn('flags["career_unknown"] = [p for p in flags["people"] if career_unknown(p)]', src)
        import eval_run
        with tempfile.TemporaryDirectory() as d, patch.object(eval_run, "DATA", Path(d)):
            (Path(d) / "media").mkdir()
            (Path(d) / "media" / "short_1_flags.json").write_text(json.dumps(
                {"careers": {"Luka Doncic": []}, "career_unknown": ["Luka Doncic"]}), encoding="utf-8")
            got = eval_run.result_of({"id": "s", "headline": "h"}, {"hook": {"text": "x"}, "beats": []})
        self.assertEqual((got["careers"], got["career_unknown"]), ({"Luka Doncic": []}, ["Luka Doncic"]))


class OnlyTheSpeaker(unittest.TestCase):
    """125. D94 (his answers 2026-11-25, class P1). receipts2: Trump's words over LeBron, Smith's
    over LeBron, Breen's over Embiid: the writer's note named the man spoken ABOUT and the picker
    obeyed (D71) while the final read (D80) called it an error. His rule: only the speaker."""

    WHO = ["Dwyane Wade", "Victor Wembanyama", "Stephen A. Smith", "LeBron James"]

    def setUp(self):
        import media
        self.m = media
        self.p = patch.object(media, "career_teams", lambda p: set() if p == "Stephen A. Smith" else {"t"})
        self.p.start()
        self.saved = dict(media._outside)
        media._outside.clear()

    def tearDown(self):
        self.p.stop()
        self.m._outside.clear()
        self.m._outside.update(self.saved)

    @staticmethod
    def ph(who):
        return {"kind": "photo", "title": "x.jpg", "tag": {"v": "C", "s": "game", "t": "t", "who": who} if who else {}}

    def test_the_verbs_are_d68s_list(self):
        # D96 module 2 (his answer 2026-11-25, a changed rule): D68's list split as in D95: clear
        # verbs decide alone, ambiguous ones only on a line judged to report someone's words
        self.assertEqual(self.m.SPEECH_VERBS, ("said", "says", "told", "wrote", "replied", "explained"))
        self.assertEqual(self.m.SPEECH_AMBIG, ("added", "responded", "posted", "asked"))

    def test_speakers(self):
        sp = self.m.speakers
        self.assertEqual(sp("Still, Wade says he has to get stronger.", self.WHO), ["Dwyane Wade"])
        self.assertEqual(sp("Dwyane Wade told reporters it was fair.", self.WHO), ["Dwyane Wade"])
        self.assertEqual(sp("Victor said nothing, Wade wrote back.", self.WHO), ["Dwyane Wade", "Victor Wembanyama"])
        self.assertEqual(sp("Wade, smiling, said it.", self.WHO), [])            # not right before the verb
        self.assertEqual(sp("Wade claims it.", self.WHO), [])                    # not in the list
        self.assertEqual(sp("He said Wade was right.", self.WHO), [])

    def test_modes(self):
        m = self.m
        with patch.object(m, "outside_person", lambda n: n == "Donald Trump"):
            self.assertEqual(m.line_lock("Still, Wade says he has to get stronger.", "Victor Wembanyama playing", self.WHO),
                             ("speaker", ["Dwyane Wade"]))
            self.assertEqual(m.line_lock("He said it over an anthem video.", "Donald Trump at a rally", self.WHO),
                             ("outside", []))
            # D91 P1 (a changed rule, his answer 2026-11-25): the line names a player and the note locks
            # nobody: only him (D50 for the pick too), no longer "no limit"
            self.assertEqual(m.line_lock("LeBron skipped the visit.", "Donald Trump at a rally", self.WHO), ("line", ["LeBron James"]))
            # a TV host speaking keeps D50: the note decides, as before
            self.assertEqual(m.line_lock("Smith says LeBron wouldn't visit.", "LeBron James speaking", self.WHO),
                             ("note", ["LeBron James"]))
            self.assertEqual(m.line_lock("Wembanyama dunked.", "Victor Wembanyama dunking", self.WHO),
                             ("note", ["Victor Wembanyama"]))

    def test_what_each_mode_allows(self):
        m, W = self.m, self.WHO
        self.assertFalse(m.lock_allows(self.ph("Victor Wembanyama"), "speaker", ["Dwyane Wade"], W, "Victor Wembanyama playing"))
        self.assertTrue(m.lock_allows(self.ph("Dwyane Wade"), "speaker", ["Dwyane Wade"], W, "Victor Wembanyama playing"))
        self.assertTrue(m.lock_allows(self.ph(""), "speaker", ["Dwyane Wade"], W, ""))                  # generic / team
        self.assertFalse(m.lock_allows(self.ph("LeBron James"), "outside", [], W, "Donald Trump and LeBron James"))
        self.assertTrue(m.lock_allows(self.ph("Donald Trump"), "outside", [], W, "Donald Trump at a rally"))
        self.assertTrue(m.lock_allows(self.ph(""), "outside", [], W, "Donald Trump at a rally"))

    def test_outside_person(self):
        m = self.m

        def fake(desc, p31):
            def get(url, timeout=30):
                if "wikipedia" in url:
                    return json.dumps({"query": {"pages": {"1": {"title": "x", "pageprops": {
                        "wikibase_item": "Q1", "wikibase-shortdesc": desc}}}}})
                return json.dumps({"claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": p31}}}}]}})
            return get
        cases = [("President of the United States", "Q5", True), ("American sports journalist", "Q5", False),
                 ("American basketball player (born 1984)", "Q5", False), ("American TV personality", "Q5", False),
                 ("2016 film", "Q11424", False)]
        for desc, p31, want in cases:
            m._outside.clear()
            with patch.object(m, "get", fake(desc, p31)):
                self.assertEqual(m.outside_person("Some Name"), want, desc)
        m._outside.clear()
        with patch.object(m, "get", side_effect=RuntimeError("down")), redirect_stdout(io.StringIO()):
            self.assertTrue(m.outside_person("Some Name"))       # unreachable: the name counts

    def test_every_stage_has_it(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('if mode == "outside":\n            skip(i, "the speaker is outside sport")\n            return None', src)
        self.assertIn("on_screen names the SPEAKER by", (ROOT / "src" / "script.py").read_text(encoding="utf-8"))
        import final_read
        self.assertIn("On a line telling what X said\n   ABOUT Y", final_read.RULES)
        self.assertIn("the man the\n   line is about is the speaker X", final_read.PROMPT)
        self.assertIn("a reporter's, TV host's or\n   commentator's words about a player may show that player", final_read.RULES)


class PinnedModels(unittest.TestCase):
    """126. D85 (his answers 2026-11-25). The floating aliases "sonnet"/"haiku" would silently
    change every writer and judge at a new release, and every eval comparison with them. The
    factsheet eval's log showed the exact ids; they are pinned, and a retired one stops the run."""

    MODULES = ("script", "media", "editor", "skills")

    def test_pinned_everywhere(self):
        for wf in ("collect", "eval", "media-preview"):
            text = (ROOT / ".github" / "workflows" / f"{wf}.yml").read_text(encoding="utf-8")
            self.assertIn("  CLAUDE_MODEL: claude-sonnet-5-5", text, wf)
            self.assertIn("  CLAUDE_MODEL_LIGHT: claude-haiku-5-5", text, wf)
        for name in self.MODULES:
            src = (ROOT / "src" / f"{name}.py").read_text(encoding="utf-8")
            self.assertNotRegex(src, r'get\("CLAUDE_MODEL(?:_LIGHT)?", "(?:sonnet|haiku|opus)"\)', name)
            self.assertIn('"claude-sonnet-5-5"', src, name)

    def test_the_four_checks_are_one(self):
        import importlib
        mods = [importlib.import_module(n) for n in self.MODULES]
        self.assertEqual({m.MODEL_GONE.pattern for m in mods}, {mods[0].MODEL_GONE.pattern})
        for n in self.MODULES:
            src = (ROOT / "src" / f"{n}.py").read_text(encoding="utf-8")
            self.assertEqual(src.count("check_model("), 2, n)     # defined once, called at its one Claude call

    def test_a_retired_model_stops_the_run(self):
        import script
        gone = ['{"type":"result","is_error":true,"result":"API Error: 404 {\\"type\\":\\"error\\",\\"error\\":'
                '{\\"type\\":\\"not_found_error\\",\\"message\\":\\"model: claude-sonnet-5-5\\"}}"}',
                "There's an issue with the selected model (claude-sonnet-5-5). It may not exist or you may not have access to it.",
                "Error: model claude-haiku-5-5 has been retired"]
        with tempfile.TemporaryDirectory() as d, patch.object(script, "DATA", Path(d)):
            for text in gone:
                with self.assertRaises(SystemExit) as cm:
                    script.check_model(text, "", "claude-sonnet-5-5")
                self.assertIn("no longer available", str(cm.exception.code))
                self.assertTrue((Path(d) / "model_gone.txt").exists())
            for fine in ('{"type":"result","result":"{\\"ok\\": true}"}', "You've hit your 5-hour limit",
                         'The player was not found in the lineup; the model of the offense changed.',
                         '{"type":"result","is_error":false,"result":"the model is not available in stores"}'):
                script.check_model(fine, "", "claude-sonnet-5-5")       # no exit

    def test_the_eval_stops_on_it(self):
        src = (ROOT / "src" / "eval_run.py").read_text(encoding="utf-8")
        self.assertIn('if (DATA / "model_gone.txt").exists():', src)


class ReportsAreRepairedNotOnlyHeld(unittest.TestCase):
    """127. D95 (his answers 2026-11-25, D78 + D93). The F1 class "a report said as fact" held 8 eval
    Shorts and was never repaired: an UNVERIFIED label and a whole-script REJECT never reached the
    repair pass, a hook could lead with a rumor as fact, and "questioned" was no attribution."""

    def test_the_new_verbs_attribute_but_not_stats(self):
        import compliance as C
        # his approved split (2026-11-25): clear words decide by themselves, ambiguous ones never do
        for v in ("wrote", "replied", "explained", "questioned", "says", "reported", "reports",
                  "according to", "linked", "eyeing", "in talks"):
            self.assertTrue(C.SENTENCE_HEDGE.search(f"Arenas {v} it."), v)
        for v in ("wrote", "replied", "explained", "questioned", "reported", "according to"):
            self.assertTrue(C.HEDGE.search(f"Arenas {v} it."), v)
        for v in ("per", "report", "may", "could", "might", "would", "if", "wants", "interested",
                  "considering", "expected to", "expects", "suggests", "responded", "asked", "posted",
                  "added", "heard", "hears", "buzz", "whispers"):
            self.assertFalse(C.SENTENCE_HEDGE.search(f"Lendeborg {v} it."), v)
            self.assertFalse(C.HEDGE.search(f"Lendeborg {v} it."), v)
            self.assertTrue(C.SENTENCE_AMBIG.search(f"Lendeborg {v} it."), v)

    def test_the_arenas_hook_is_no_false_hold(self):
        import compliance as C
        claims = [{"text": "Arenas questioned how Draymond Green can function without Curry and said a rookie", "status": "SPECULATION"}]
        hook = "Gilbert Arenas just questioned whether Draymond Green works without Steph Curry."
        self.assertEqual(C.bare_claims(claims, hook), [])
        self.assertTrue(C.bare_claims(claims, "Draymond Green can't function without Curry."))   # still caught

    def test_the_murray_hook_steps_behind(self):
        import script
        claims = [{"text": "Multiple teams view Murray as a distressed asset", "status": "RUMOR"}]
        hooks = [{"text": "Multiple teams now see Dejounte Murray as a distressed asset.", "unsupported_details": []},
                 {"text": "Windhorst: rival teams see Dejounte Murray as a distressed asset.", "unsupported_details": []}]
        with patch.object(script, "check_hook_truth", lambda h, s, lead="": "ok"), \
                patch.object(script.compliance, "gate_statuses", lambda c, s: c):
            script.truth_order(hooks, [], "", claims)
        self.assertTrue(hooks[0]["text"].startswith("Windhorst:"))
        self.assertTrue(hooks[1]["bare_report"])
        # every hook bare: it leads and the gate holds, as before
        hooks = [{"text": "Multiple teams now see Dejounte Murray as a distressed asset.", "unsupported_details": []}]
        with patch.object(script, "check_hook_truth", lambda h, s, lead="": "ok"), \
                patch.object(script.compliance, "gate_statuses", lambda c, s: c):
            script.truth_order(hooks, [], "", claims)
        self.assertEqual(len(hooks), 1)

    def test_told_as_fact_goes_to_the_repair(self):
        import compliance as C, script
        claims = [{"text": "Curry tore his oblique and is out at least two weeks", "status": "REPORTED", "source": 1}]
        beats = [{"say": "Curry tore his oblique in Houston and is out at least two weeks."},
                 {"say": "I think the Warriors are in trouble."}]
        hook = "Gilbert Arenas wonders how the Warriors survive without Steph Curry."
        self.assertEqual(C.told_as_fact(claims, hook + " " + " ".join(b["say"] for b in beats)),
                         ["Curry tore his oblique in Houston and is out at least two weeks."])
        with patch.object(C, "gate_statuses", lambda c, s: c):
            probs = script.repair_needed(hook, beats, {"hard": [], "soft": []}, [], claims)
        self.assertTrue(any("said as fact with no source anywhere" in p for p in probs))
        # every wording the problem suggests is one the gate accepts as attribution by itself (clear
        # words: "per" is ambiguous since his rule of 2026-11-25, so it is not suggested)
        for w in ("the Warriors said", "ESPN reported", "according to Yahoo"):
            self.assertTrue(C.HEDGE.search(w), w)
            self.assertIn(w, " ".join(probs))
        beats[0]["say"] = "The Warriors said Curry tore his oblique and is out at least two weeks."
        self.assertEqual(C.told_as_fact(claims, hook + " " + " ".join(b["say"] for b in beats)), [])   # attributed: nothing

    def test_relabel_from_the_fact_sheet(self):
        import script
        sheet = [{"text": "The moment went viral as the Lakers nearly blew a 31-point second-half lead, with some "
                          "interpreting Doncic's actions as disrespectful toward Harding.", "kind": "REPORTED",
                  "who": "Yahoo Sports", "source": 1},
                 {"text": "Arenas strongly disagreed with that interpretation.", "kind": "REPORTED", "who": "Yahoo Sports", "source": 1}]
        claims = [{"text": "Some people interpreted the grab as disrespectful toward Harding", "status": "UNVERIFIED"},
                  {"text": "Luka secretly asked for a trade last week", "status": "UNVERIFIED"},
                  {"text": "Arenas disagreed with that interpretation", "status": "SPECULATION", "source": 1}]
        changed = script.relabel_from_sheet(claims, sheet)
        self.assertEqual(changed, ["Some people interpreted the grab as disrespectful toward Harding"])
        self.assertEqual((claims[0]["status"], claims[0]["source"]), ("REPORTED", 1))
        self.assertEqual(claims[1]["status"], "UNVERIFIED")          # not on the sheet: held, as before
        self.assertEqual(claims[2]["status"], "SPECULATION")         # only UNVERIFIED is relabelled
        self.assertEqual(script.relabel_from_sheet([dict(claims[1])], []), [])   # no sheet: as before

    def test_wired(self):
        src = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn('for text in relabel_from_sheet(draft.get("claims") or [], sheet):', src)
        self.assertLess(src.index("relabel_from_sheet(draft.get"), src.index("truth_order(hooks, sources, lead, draft.get"))
        self.assertIn("judged = compliance.gate_statuses(claims, sources) if sources is not None else claims", src)

    def test_posted_added_are_judged_in_context(self):
        import compliance as C, script
        claims = [{"text": "Murray hinted the sabotage inside the Pelicans is real", "status": "RUMOR"}]
        stat = "Murray posted 25 points while hinting the sabotage inside the Pelicans is real."
        post = "Murray posted on Instagram that the sabotage inside the Pelicans is real."
        self.assertIn(stat, C.ambiguous_deciders(claims, stat))
        self.assertEqual(C.bare_claims(claims, post), [claims[0]["text"]])             # not judged: a bare claim
        self.assertEqual(C.bare_claims(claims, post, [post]), [])                       # judged his words
        calls = []

        def fake(prompt, model="", where=""):
            calls.append(prompt)
            return {"words": [2]}
        script._attribution_seen.clear()
        with patch.object(script, "ask_claude", fake):
            got = script.judged_attributions([stat, post, post], "context")
            again = script.judged_attributions([post], "context")
        self.assertEqual((got, again, len(calls)), ([post, post], [post], 1))   # one call, cached
        self.assertIn("30 points per game", script.ATTRIBUTION_ASK)
        self.assertIn("posted 25 points", script.ATTRIBUTION_ASK)
        script._attribution_seen.clear()
        with patch.object(script, "ask_claude", side_effect=RuntimeError("down")), redirect_stdout(io.StringIO()):
            self.assertEqual(script.judged_attributions([post], "c"), [])       # failure: not attribution
        script._attribution_seen.clear()
        with patch.object(script, "ask_claude", side_effect=script.UsageLimit("limit")):
            with self.assertRaises(script.UsageLimit):
                script.judged_attributions([post], "c")
        script._attribution_seen.clear()
        # the whole-Short test counts a judged sentence too
        rep = [{"text": "the sabotage inside the Pelicans is real", "status": "REPORTED", "source": 1}]
        self.assertTrue(C.told_as_fact(rep, post))
        self.assertEqual(C.told_as_fact(rep, post, [post]), [])

    def test_the_gate_counts_the_same(self):
        src = (ROOT / "src" / "compliance.py").read_text(encoding="utf-8")
        self.assertIn('check_claims(short.get("claims") or [], sources, spoken, short.get("attributed") or (), signs, judged)', src)   # D96 m6
        self.assertIn("not attributed_anywhere(spoken, attributed)", src)
        sc = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        # D96 module 2: one call judges both questions (attribution and speech)
        self.assertIn('short["attributed"], short["speech_lines"] = judge_ambiguous(', sc)
        self.assertLess(sc.index('short["attributed"], short["speech_lines"] = judge_ambiguous('), sc.index("result = compliance.evaluate_script(short, sources, known)"))
        fx = (ROOT / "src" / "fix_after_read.py").read_text(encoding="utf-8")
        self.assertLess(fx.index('short["attributed"], short["speech_lines"] = script.judge_ambiguous('), fx.index("result = C.evaluate_script(short, sources)"))


    def test_the_whole_short_and_the_sensitive_topic_count_judged_sentences(self):
        import compliance as C
        said = "The Lakers may have to answer for the lawsuit."
        spoken = f"{said} I think it gets ugly."
        rep = [{"text": "the lawsuit against the Lakers", "status": "REPORTED", "source": 1}]
        self.assertIn(said, C.ambiguous_deciders(rep, spoken))        # no clear attribution anywhere
        src = [{"title": "t", "publisher": "ESPN", "tier": 1, "text": "x", "summary": ""}]
        v, notes, _ = C.check_suitability(spoken, "", "", "", src, rep, {"insiders": []})
        self.assertTrue(any("told as proven fact" in n for n in notes))
        v, notes, _ = C.check_suitability(spoken, "", "", "", src, rep, {"insiders": []}, [said])
        self.assertFalse(any("told as proven fact" in n for n in notes))   # judged in context: attributed


class AmbiguousSpeechVerbsInContext(unittest.TestCase):
    """128. D96 module 2 (his rule 2026-11-25: an ambiguous word by meaning, never a list)."""

    WHO = ["Yaxel Lendeborg", "Steph Curry", "Charles Bassey", "Marcus Smart"]

    def setUp(self):
        import media
        self.m = media
        self.p = patch.object(media, "career_teams", lambda p: {"t"})
        self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_an_ambiguous_verb_needs_the_judgement(self):
        m = self.m
        stat = "Lendeborg posted 25 points and Curry sat."
        quote = 'Udoka said Bassey asked, "What you gonna do?" and Smart swung.'
        self.assertEqual(m.speakers(stat, self.WHO), [])
        self.assertEqual(m.speakers(stat, self.WHO, [stat]), ["Yaxel Lendeborg"])   # only if judged speech
        self.assertEqual(m.speakers(quote, self.WHO), [])
        self.assertEqual(m.speakers(quote, self.WHO, [quote]), ["Charles Bassey"])
        self.assertEqual(m.speakers("Curry said it.", self.WHO), ["Steph Curry"])       # clear: alone
        self.assertFalse(m.is_speech_line("He posted 25 points."))
        self.assertTrue(m.is_speech_line("He posted on Instagram.", ["He posted on Instagram."]))
        self.assertTrue(m.is_speech_line("He said it."))
        self.assertEqual(m.line_lock(stat, "Steph Curry on the bench", self.WHO), ("note", ["Steph Curry"]))

    def test_one_call_judges_both(self):
        import script
        calls = []

        def fake(prompt, model="", where=""):
            calls.append(prompt)
            return {"words": [1], "speech": [2]}
        script._attribution_seen.clear(); script._speech_seen.clear()
        with patch.object(script, "ask_claude", fake):
            a, sp = script.judge_ambiguous(["Per ESPN, he is out."], ["He posted 25 points.", "He posted on X."], "ctx")
        self.assertEqual((a, sp, len(calls)), (["Per ESPN, he is out."], ["He posted on X."], 1))
        self.assertIn("PART B", calls[0])
        script._attribution_seen.clear(); script._speech_seen.clear()
        with patch.object(script, "ask_claude", side_effect=RuntimeError("down")), redirect_stdout(io.StringIO()):
            self.assertEqual(script.judge_ambiguous(["a"], ["b posted"], "c"), ([], []))   # safe side
        script._attribution_seen.clear(); script._speech_seen.clear()
        short = {"hook": {"text": "Bassey asked for it."}, "beats": [{"say": "He said no."}, {"say": "He added 10 rebounds."}]}
        self.assertEqual(script.ambiguous_speech_lines(short), ["Bassey asked for it.", "He added 10 rebounds."])

    def test_the_picker_reads_it(self):
        src = (ROOT / "src" / "media.py").read_text(encoding="utf-8")
        self.assertIn('(short or {}).get("speech_lines") or ())', src)
        self.assertIn("    if is_speech_line(say, speech) and outside_speaker(screen, who):", src)



class PictureWordsByMeaning(unittest.TestCase):
    """129. D96 module 3 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def setUp(self):
        import media
        import script
        self.m, self.s = media, script
        self.saved = (media.ask_claude, dict(media._meta_seen), media._TIME_LINES[0])
        media._meta_seen.clear()
        media._meta_pending.clear()

    def tearDown(self):
        m = self.m
        m.ask_claude = self.saved[0]
        m._meta_seen.clear()
        m._meta_seen.update(self.saved[1])
        m._meta_pending.clear()
        m._TIME_LINES[0] = self.saved[2]

    def test_ambiguous_clip_word_is_judged(self):
        m = self.m
        seen = []

        def judge(prompt, model=None, **kw):
            seen.append(prompt)
            return {"yes": [1]}
        m.ask_claude = judge
        c = {"_ask": [("fits", "File:Court.webm", "Lakers on the court")]}
        self.assertTrue(m.meta_ok(c))
        self.assertEqual(c["meta_judged"], {"fits": True})
        self.assertIn("FITS: Lakers on the court", seen[0])
        m._meta_seen.clear()
        m.ask_claude = lambda prompt, model=None, **kw: {"yes": []}
        self.assertFalse(m.meta_ok({"_ask": [("fits", "File:Court2.webm", "a family court")]}))

    def test_failed_judgement_is_the_safe_side(self):
        m = self.m

        def down(prompt, model=None, **kw):
            raise RuntimeError("down")
        m.ask_claude = down
        self.assertFalse(m.meta_ok({"_ask": [("fits", "a", "x")]}))
        self.assertFalse(m.meta_ok({"_ask": [("broadcast", "b", "ESPN")]}))     # counted as broadcast
        self.assertFalse(m.meta_ok({"_ask": [("trusted", "c", "own work")]}))

    def test_common_searches_wait_for_one_call(self):
        m = self.m
        calls = []
        m.ask_claude = lambda prompt, model=None, **kw: calls.append(prompt) or {"yes": [1, 2]}
        m._META_DEFER[0] = True
        try:
            self.assertIsNone(m.meta_answer("fits", "k1", "arena"))
            self.assertIsNone(m.meta_answer("trusted", "k2", "own work"))
            self.assertEqual(calls, [])
        finally:
            m._META_DEFER[0] = False
        m.meta_judge_pending()
        self.assertEqual(len(calls), 1)
        self.assertTrue(m._meta_seen["fits|k1"] and m._meta_seen["trusted|k2"])

    def test_clear_words_still_decide_alone(self):
        m = self.m
        m.ask_claude = lambda *a, **k: self.fail("a clear word needs no question")
        ok, asks = m.video_trust({"Credit": "White House", "ImageDescription": "", "Categories": ""}, "File:x.webm")
        self.assertEqual((ok, asks), (True, []))
        ok, asks = m.video_trust({"Credit": "", "ImageDescription": "Fox Sports telecast", "Categories": ""}, "File:y.webm")
        self.assertFalse(ok)

    def test_gate_broadcast_agrees(self):
        import gate
        x = {"kind": "video", "title": "ESPN warmups", "page": "", "match": 8, "source": "Wikimedia Commons"}
        flags = {"people": []}
        v_unjudged, notes_unjudged = gate.check_visuals([x], flags)
        v_judged, notes_judged = gate.check_visuals([{**x, "meta_judged": {"broadcast": False}}], flags)
        self.assertTrue(any("broadcast" in n.lower() for n in notes_unjudged))
        self.assertFalse(any("broadcast" in n.lower() for n in notes_judged))

    def test_now_and_today_by_meaning(self):
        m, s = self.m, self.s
        m._TIME_LINES[0] = None                                    # never judged: as before
        self.assertTrue(m.names_a_time("Now, here is the twist.", ""))
        m._TIME_LINES[0] = {"He is a Laker now."}
        self.assertTrue(m.names_a_time("He is a Laker now.", ""))
        self.assertFalse(m.names_a_time("Now, here is the twist.", ""))
        self.assertTrue(m.names_a_time("Tonight he faces Boston.", ""))   # a clear word
        s._time_seen.clear()
        saved = s.ask_claude
        try:
            s.ask_claude = lambda prompt, model=None, **kw: {"words": [], "speech": [], "now": [1]}
            s.judge_ambiguous([], [], "ctx", ["He is a Laker now.", "Now, here is the twist."])
            self.assertEqual(s.judged_time_lines(["He is a Laker now.", "Now, here is the twist."]), ["He is a Laker now."])
            s._time_seen.clear()

            def down(prompt, model=None, **kw):
                raise RuntimeError("down")
            s.ask_claude = down
            s.judge_ambiguous([], [], "ctx", ["Today he is out."])
            self.assertEqual(s.judged_time_lines(["Today he is out."]), ["Today he is out."])   # safe: a time
        finally:
            s.ask_claude = saved
            s._time_seen.clear()
        short = {"hook": {"text": "Now he is a Laker."}, "beats": [{"say": "He scored 30."}, {"say": "Today he rests."}]}
        self.assertEqual(s.ambiguous_time_lines(short), ["Now he is a Laker.", "Today he rests."])

    def test_the_tagger_decides(self):
        import photo_tags as pt
        m = self.m
        tags, _ = pt.parse_tags({"photos": [{"n": 1, "v": "C", "s": "game", "e": "calm", "t": "x", "g": "group"},
                                            {"n": 2, "v": "C", "s": "game", "e": "calm", "t": "x", "g": "maybe"}]}, 2)
        self.assertEqual(tags[1]["g"], "group")
        self.assertNotIn("g", tags[2])
        self.assertIn('"g": "alone"', pt.TAG_PROMPT)
        # a group by what the tagger saw; no "g" (tagged before D96): the title words
        alone = {"title": "File:Stephen Curry with the ball.jpg", "tag": {"v": "C", "s": "game", "g": "alone"}}
        group = {"title": "File:Stephen Curry 2019.jpg", "tag": {"v": "C", "s": "game", "g": "group"}}
        old = {"title": "File:Stephen Curry with the ball.jpg", "tag": {"v": "C", "s": "game"}}
        self.assertTrue(m.solo_title(alone, "Stephen Curry"))
        self.assertFalse(m.solo_title(group, "Stephen Curry"))
        self.assertFalse(m.solo_title(old, "Stephen Curry"))
        import gate
        self.assertFalse(gate.group_of({**alone, "own_category": True}))
        self.assertTrue(gate.group_of({**group, "own_category": True}))
        self.assertTrue(gate.group_of(old))
        # basketball by the scene; untagged by the title, as before
        self.assertTrue(pt.hoops({"tag": {"s": "game"}, "hoops": False}))
        self.assertFalse(pt.hoops({"tag": {"s": "pre_nba"}, "hoops": True}))
        self.assertTrue(pt.hoops({"hoops": True}))
        # national colours: the scene OR the note (D45 kept)
        self.assertTrue(m.national_photo({"tag": {"s": "national", "t": "anthem"}}))
        self.assertTrue(m.national_photo({"tag": {"s": "game", "t": "stares at camera, Canada jersey"}}))
        self.assertFalse(m.national_photo({"tag": {"s": "game", "t": "drives in Knicks jersey"}}))


class StoryWordsByMeaning(unittest.TestCase):
    """130. D96 module 4 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def item(self, title, league=False):
        return {"title": title, "tier": 1, "publisher": "ESPN", "published": None,
                **({"_ask_league": True} if league else {})}

    def test_one_call_judges_the_ambiguous_titles(self):
        import collect
        calls = []

        def ask(prompt):
            calls.append(prompt)
            # 1 LEAGUE Butler: NBA (yes); 2 LEAGUE college football: no; 3 SPECULATION betting scandal: no;
            # 4 SPECULATION picks preview: yes
            return '{"yes": [1, 4]}'
        items = [self.item("Jimmy Butler plans G League rehab stint", True),
                 self.item("Texas climbs in college football rankings", True),
                 self.item("Jontay Porter says threats drove NBA betting scandal"),
                 self.item("Celtics vs. 76ers NBA picks: Tatum could have a big night"),
                 self.item("Smart ejected for punching Bassey")]
        kept = collect.judge_titles(items, ask=ask)
        self.assertEqual(len(calls), 1)
        self.assertIn("LEAGUE: Jimmy Butler", calls[0])
        self.assertNotIn("Smart ejected", calls[0])                    # nothing ambiguous: no question
        self.assertEqual([i["title"][:12] for i in kept], ["Jimmy Butler", "Jontay Porte", "Celtics vs. ", "Smart ejecte"])
        self.assertFalse(collect.spec_title(kept[1]))                  # a real scandal: not speculation
        self.assertTrue(collect.spec_title(kept[2]))
        self.assertTrue(all("_ask_league" not in i and "league" not in i for i in kept))

    def test_failed_call_is_as_before(self):
        import collect

        def down(prompt):
            raise SystemExit("claude failed")
        kept = collect.judge_titles([self.item("Jimmy Butler plans G League rehab stint", True),
                                     self.item("NBA betting scandal grows")], ask=down)
        self.assertEqual([i["title"] for i in kept], ["NBA betting scandal grows"])   # the league one dropped
        self.assertTrue(collect.spec_title(kept[0]))                                  # the word counts

    def test_clear_words_decide_alone(self):
        import collect
        self.assertTrue(collect.SPECULATION.search("NBA player props and best bets"))
        self.assertTrue(collect.OTHER_LEAGUE.search("WNBA finals tonight"))
        self.assertIsNone(collect.OTHER_LEAGUE.search("Jimmy Butler G League stint"))
        self.assertIsNone(collect.SPECULATION.search("Bucks stripped of draft picks"))
        calls = []
        kept = collect.judge_titles([self.item("NBA player props, odds, picks for Friday")],
                                    ask=lambda p: calls.append(p) or '{"yes": []}')
        self.assertEqual(calls, [])                         # a clear word needs no question
        self.assertTrue(collect.spec_title(kept[0]))

    def test_the_feed_filter_asks_instead_of_dropping(self):
        import collect
        feed = {"name": "GN: NBA", "tier": 2}
        entry = {"title": "Jimmy Butler plans G League rehab stint - ESPN", "link": "https://x",
                 "source": {"title": "ESPN"}, "summary": "The Warriors forward ..."}
        it = collect.normalize(entry, feed)
        self.assertTrue(it and it.get("_ask_league"))
        self.assertIsNone(collect.normalize({**entry, "title": "Liberty win WNBA title - ESPN"}, feed))   # a clear word
        plain = collect.normalize({**entry, "title": "Warriors beat the Rockets - ESPN"}, feed)
        self.assertNotIn("_ask_league", plain)

    def test_opinion_start_words_go_to_the_editor(self):
        import editor
        self.assertIsNone(editor.OPINION.search("What Draymond said about Rivers"))
        self.assertIsNone(editor.OPINION.search("Why Kyrie wants out of Dallas"))
        self.assertTrue(editor.OPINION.search("10 takeaways from the Celtics win"))
        self.assertTrue(editor.OPINION.search("NBA power rankings week 5"))

    def test_turn_by_meaning(self):
        import datetime as dt
        import editor as e
        made = [{"time": "2026-11-11T13:20+00:00", "headline": "Jayson Tatum won't give air to Jaylen Brown drama",
                 "hook": "Did Jaylen Brown ignore Jayson Tatum?"}]
        now = dt.datetime(2026, 11, 11, 19, 40, tzinfo=dt.timezone.utc)
        t = {"headline": "Jayson Tatum could be traded as Jaylen Brown feud grows",
             "star_names": ["Jaylen Brown 2.0", "Jayson Tatum 2.0"]}
        self.assertEqual(e.same_feud_recent(t, made, now), "")                    # no answer: as before
        self.assertEqual(e.same_feud_recent(t, made, now, turn=True), "")
        self.assertTrue(e.same_feud_recent(t, made, now, turn=False))            # judged no new turn: a repeat
        t2 = {**t, "headline": "Jayson Tatum fined after Jaylen Brown altercation"}
        self.assertEqual(e.same_feud_recent(t2, made, now, turn=False), "")      # a clear word decides alone
        self.assertIn('"turn": true if the headline reports a NEW decisive event', e.PROMPT)
        import json as _j
        raw = _j.dumps({"ranked": [{"id": 0, "nba": True, "kind": "player_vs_player", "virality": 9, "drama": 9,
                                    "star_power": 9, "debate": 9, "repeat": False, "why": "", "same_as": [],
                                    "turn": False}], "shorts": [0], "long": {}})
        topics = [{**t, "items": [{"title": t["headline"], "tier": 1, "link": "https://x", "publisher": "ESPN"}]}]
        old = e.made_recently
        fresh = [{**made[0], "time": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat()}]
        e.made_recently = lambda: fresh
        try:
            data = e.parse(raw, 1, topics)
        finally:
            e.made_recently = old
        self.assertTrue(data["ranked"][0].get("repeat"))


class SignalWordsByMeaning(unittest.TestCase):
    """131. D96 module 5 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def setUp(self):
        import signals
        self.s = signals
        self.saved = dict(signals._judged)
        signals._judged.clear()

    def tearDown(self):
        self.s._judged.clear()
        self.s._judged.update(self.saved)

    def test_one_call_and_its_answers(self):
        s = self.s
        calls = []

        def ask(prompt):
            calls.append(prompt)
            # 1 NBA "islanders vs kings": no; 2 NBA "heat vs bulls" with NBA-free headlines: yes;
            # 3 NOISE "jaylen brown draft picks trade": no; 4 STORY "history career will": no;
            # 5 STORY "luka doncic trade reaction" has a clear word: never asked
            return '{"yes": [2]}'
        trends = [{"query": "islanders vs kings", "news": ["Islanders top Kings in overtime"]},
                  {"query": "heat vs bulls", "news": ["Butler returns to Miami"]},
                  {"query": "lakers score", "news": []}]
        found = ["jaylen brown draft picks trade", "history career will", "luka doncic trade reaction",
                 "lebron 2k26 rating"]
        s.judge_signals(found, trends, ask=ask)
        self.assertEqual(len(calls), 1)
        self.assertIn("NBA: islanders vs kings", calls[0])
        self.assertNotIn("lakers score", calls[0])                  # a clear word: no question
        self.assertNotIn("STORY: luka doncic trade reaction", calls[0])
        self.assertNotIn("2k26", calls[0])
        self.assertFalse(s.nba_text(s.trend_text(trends[0])))
        self.assertTrue(s.nba_text(s.trend_text(trends[1])))
        self.assertTrue(s.nba_text(s.trend_text(trends[2])))
        self.assertFalse(s.noise("jaylen brown draft picks trade"))
        self.assertTrue(s.noise("lebron 2k26 rating"))
        self.assertFalse(s.story_phrase("history career will"))
        self.assertTrue(s.story_phrase("luka doncic trade reaction"))

    def test_failed_call_is_as_before(self):
        s = self.s

        def down(prompt):
            raise SystemExit("claude failed")
        s.judge_signals(["jaylen brown draft picks trade", "get bad news game"],
                        [{"query": "islanders vs kings", "news": []}], ask=down)
        self.assertTrue(s.nba_text("islanders vs kings"))
        self.assertTrue(s.noise("jaylen brown draft picks trade"))
        self.assertTrue(s.story_phrase("get bad news game"))

    def test_the_trend_match_uses_it(self):
        s = self.s
        topic = {"headline": "Doc Rivers fires back", "star_names": ["Doc Rivers 5.0"]}
        trend = {"query": "rivers kings", "news": ["Kings win in Los Angeles"]}
        s._judged[("nba", s.trend_text(trend))] = False
        self.assertFalse(s.trend_matches(topic, trend))
        s._judged[("nba", s.trend_text(trend))] = True
        self.assertTrue(s.trend_matches(topic, trend))

    def test_main_uses_it(self):
        src = (ROOT / "src" / "signals.py").read_text(encoding="utf-8")
        call = src.index('    judge_signals(found, signals.get("google_trends", []))')
        self.assertLess(call, src.index('    signals["suggestions"] = [x for x in dict.fromkeys(found) if not noise(x)]'))
        self.assertIn("(story_phrase(x) or len(keys & set(x.split())) > 1)", src)
        self.assertIn("if nba_text(trend_text(g))", src)


class ArticleSignsByMeaning(unittest.TestCase):
    """132. D96 module 6 part 1 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def src(self, text, tier=1):
        return [{"title": "t", "summary": "", "text": text, "tier": tier, "publisher": "ESPN"}]

    def test_the_fact_sheet_answers_them(self):
        import script
        saved = script.ask_claude
        try:
            script.ask_claude = lambda prompt, model=None, **kw: {
                "facts": [], "signs": {"official": True, "fan_reaction": "yes", "response": False, "x": True}}
            signs = {}
            script.fact_sheet(self.src("The Pelicans announced it."), signs)
            self.assertEqual(signs, {"official": True, "response": False})      # only real booleans
            self.assertIn('"official": did the team, the league or the player\'s camp OFFICIALLY', script.FACTS)

            def down(prompt, model=None, **kw):
                raise RuntimeError("down")
            script.ask_claude = down
            signs = {}
            script.fact_sheet(self.src("x"), signs)
            self.assertEqual(signs, {})
        finally:
            script.ask_claude = saved

    def test_official(self):
        import compliance as C
        recap = self.src("This beef officially began on March 6, when LeBron confronted Smith.")
        self.assertFalse(C.original_reporters(recap)["official"])                       # not judged: safe side
        self.assertFalse(C.original_reporters(recap, {"official": False})["official"])
        self.assertTrue(C.original_reporters(self.src("The Pelicans announced it."), {"official": True})["official"])
        self.assertTrue(C.original_reporters(self.src("Per a press release, he is out."))["official"])   # clear
        self.assertFalse(C.original_reporters(self.src("The Pelicans announced it.", tier=2),
                                              {"official": True})["official"])          # tier 1 still needed

    def test_fan_reaction(self):
        import compliance as C
        line = "Fans are furious about it."
        furniture = self.src("Murray is out. Comments (0) pic.twitter.com/abc What's Trending Now")
        self.assertEqual(C.check_social_proof(line, furniture)[0], C.REVIEW)
        self.assertEqual(C.check_social_proof(line, furniture, signs={"fan_reaction": True})[0], C.PASS)
        self.assertEqual(C.check_social_proof(line, self.src("A huge backlash followed."))[0], C.PASS)   # clear
        self.assertEqual(C.check_fabrication(line, furniture, [], [], False, {"fan_reaction": True})[0], C.PASS)
        self.assertEqual(C.check_fabrication(line, furniture, [], [])[0], C.REVIEW)
        # the claims check reads the same answer: CONFIRMED stays only with official word
        claim = [{"text": "The Pelicans announced Murray is out.", "status": "CONFIRMED", "source": 1}]
        ann = self.src("The Pelicans announced Murray is out.")
        said = "The Pelicans said Murray is out."
        self.assertEqual(C.check_claims(claim, ann, said, (), {"official": True})[2][0]["status"], "CONFIRMED")
        self.assertEqual(C.check_claims(claim, ann, said)[2][0]["status"], "REPORTED")

    def test_response(self):
        import compliance as C
        spoken = "Per ESPN, he was arrested on domestic violence charges."
        mat = self.src("Police arrested him, per ESPN. The team needed a response after the loss.")
        # part 2 (his answer 2026-11-25: the safe side is always the STRICTER check, a changed rule):
        # with no answer the ambiguous word in the articles counts; "no response" lets it go
        held = lambda notes: any("response or denial" in n for n in notes)       # noqa: E731
        _, notes, _ = C.check_suitability(spoken, "", "", "", mat, [], C.original_reporters(mat))
        self.assertTrue(held(notes))
        _, notes, _ = C.check_suitability(spoken, "", "", "", mat, [], C.original_reporters(mat), (), {"response": False})
        self.assertFalse(held(notes))
        _, notes, _ = C.check_suitability(spoken, "", "", "", mat, [], C.original_reporters(mat), (), {"response": True})
        self.assertTrue(held(notes))
        told = spoken + " He responded on Instagram that it is false."
        _, notes, _ = C.check_suitability(told, "", "", "", mat, [], C.original_reporters(mat), (), {"response": True})
        self.assertTrue(held(notes))                                   # the Short's "responded" not judged: not told
        _, notes, _ = C.check_suitability(told, "", "", "", mat, [], C.original_reporters(mat), (), {"response": True},
                                          {"response": True})
        self.assertFalse(held(notes))

    def test_the_gate_reads_them(self):
        src = (ROOT / "src" / "compliance.py").read_text(encoding="utf-8")
        self.assertIn('    signs = short.get("source_signs")', src)
        self.assertIn("v, n, origin = check_sources(sources, signs)", src)
        sc = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn('"source_signs": signs,', sc)
        self.assertIn("sheet = fact_sheet(sources, signs)", sc)


class ScriptWordsByMeaning(unittest.TestCase):
    """133. D96 module 6 part 2 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    SRC = [{"title": "t", "summary": "", "tier": 1, "publisher": "ESPN",
            "text": "Barkley and Jordan stopped talking years ago. Barkley said Jordan reached out to him last week."}]

    def test_silence_and_turn(self):
        import compliance as C
        spoken = "Barkley says Jordan cussed him out, and they stopped talking."
        self.assertTrue(C.missed_turn(spoken, self.SRC))                                  # no answer: stricter
        self.assertFalse(C.missed_turn(spoken, self.SRC, {"silence": False}))            # judged: not silence
        self.assertFalse(C.missed_turn(spoken, self.SRC, {}, {"reconciled": False}))     # articles: no turn
        told = spoken + " Then Jordan reached out to him."
        self.assertTrue(C.missed_turn(told, self.SRC))                                    # the Short's turn not judged
        self.assertFalse(C.missed_turn(told, self.SRC, {"turn": True}))
        self.assertFalse(C.missed_turn("Draymond never stopped talking.", self.SRC, {"silence": False}))
        self.assertTrue(C.missed_turn("Barkley and Jordan still haven't spoken.", self.SRC, {"silence": False}))   # clear decides
        claims = [{"text": "Barkley and Jordan stopped talking", "status": "REPORTED", "source": 1}]
        said = "Per ESPN, Barkley and Jordan stopped talking."
        turn_note = lambda r: any("speaks of silence" in n for n in r[1])        # noqa: E731
        self.assertTrue(turn_note(C.check_claims(claims, self.SRC, said)))
        self.assertFalse(turn_note(C.check_claims(claims, self.SRC, said, (), None, {"silence": False})))

    def test_title_hedge(self):
        import compliance as C
        claims = [{"text": "Rivers could be fired", "status": "REPORTED", "source": 1}]
        src = [{"title": "t", "summary": "", "tier": 1, "publisher": "ESPN", "text": "Doc Rivers could be fired, per ESPN."}]
        title = "Doc Rivers could be FIRED"
        self.assertEqual(C.check_headline(title, claims, src, "title")[0], C.REVIEW)       # not judged: stricter
        self.assertEqual(C.check_headline(title, claims, src, "title", None, [title])[0], C.PASS)
        self.assertEqual(C.check_headline("Is Doc Rivers getting FIRED?", claims, src, "title")[0], C.PASS)   # clear

    def test_the_d95_call_carries_them(self):
        import script
        script._attribution_seen.clear(); script._short_seen.clear()
        saved = script.ask_claude
        prompts = []
        try:
            def ask(prompt, model=None, **kw):
                prompts.append(prompt)
                return {"words": [1], "speech": [], "now": [], "short": {"silence": False, "turn": "yes"}}
            script.ask_claude = ask
            a, _ = script.judge_ambiguous(["Doc Rivers could be FIRED"], [], "ctx", (), ["silence", "turn"])
            self.assertEqual(a, ["Doc Rivers could be FIRED"])
            self.assertEqual(script.judged_short(["silence", "turn"], "ctx"), {"silence": False})   # only booleans
            self.assertIn("PART D QUESTIONS:\nsilence\nturn", prompts[0])
            self.assertEqual(len(prompts), 1)
        finally:
            script.ask_claude = saved
            script._attribution_seen.clear(); script._short_seen.clear()
        short = {"spoken": "They stopped talking. Then he apologized.", "titles": [{"title": "Curry could play 20 seasons"},
                 {"title": "Is it over?"}], "thumbnail_text": "COULD HE?"}
        self.assertEqual(script.short_questions(short), ["silence", "turn"])
        self.assertEqual(script.ambiguous_titles(short["titles"], short["thumbnail_text"]), ["Curry could play 20 seasons"])
        self.assertEqual(script.short_questions({"spoken": "They still haven't spoken."}), [])     # clear: no question

    def test_the_articles_sign(self):
        import script
        self.assertIn('"reconciled": do the articles tell', script.FACTS)

    def test_the_stages_pass_them(self):
        src = (ROOT / "src" / "compliance.py").read_text(encoding="utf-8")
        self.assertIn('    judged = short.get("short_judged")', src)
        self.assertIn('v, n = check_headline(title, claims, sources, "title", known, attributed)', src)
        self.assertIn("short_judged", (ROOT / "src" / "fix_after_read.py").read_text(encoding="utf-8"))
        sc = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn('short["short_judged"] = judged_short(short_questions(short), short.get("spoken", ""))', sc)
        self.assertIn('short["titles"] = compliance.pick_safe_title(short["titles"], short.get("claims") or [], sources, known,', sc)
        self.assertIn("+ ambiguous_titles(short.get(\"titles\"), short.get(\"thumbnail_text\", \"\")),", sc)


class StyleWordsByMeaning(unittest.TestCase):
    """135. D96 module 6 part 3 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def setUp(self):
        import script
        self.s = script
        self.saved = (script.ask_claude, dict(script._style_seen))
        script._style_seen.clear()

    def tearDown(self):
        self.s.ask_claude = self.saved[0]
        self.s._style_seen.clear()
        self.s._style_seen.update(self.saved[1])

    def test_one_call(self):
        s = self.s
        calls = []

        def ask(prompt, model=None, **kw):
            calls.append(prompt)
            return {"yes": []}
        s.ask_claude = ask
        hooks = ["Did Draymond Green just warn NBA coaches that players will start talking crazy about them?",
                 "The NBA just suspended Marcus Smart, and Bassey slams him for it."]
        s.judge_style(hooks, ["So in 1985 he beat Boston.", "I think he's right, because Luka is so good."])
        self.assertEqual(len(calls), 1)
        self.assertIn("CLASH: Did Draymond", calls[0])
        self.assertIn("FOG: Did Draymond", calls[0])
        self.assertIn("REASON: So in 1985", calls[0])
        self.assertNotIn("CLASH: The NBA just suspended", calls[0])   # a clear clash word: no question
        self.assertNotIn("because Luka", calls[0])              # a clear reason word: no question
        self.assertFalse(any(f == "fog word" for f, _ in s.hook_flaws(hooks[0])))
        self.assertEqual(s.clash_count(hooks[0]), 0)
        self.assertFalse(s.gives_reason("So in 1985 he beat Boston."))
        s.judge_style(hooks)
        self.assertEqual(len(calls), 1)                        # cached

    def test_failed_or_broken_answer_is_as_before(self):
        s = self.s
        for answer in (RuntimeError("down"), {"words": []}, "not json"):
            s._style_seen.clear()

            def ask(prompt, model=None, answer=answer, **kw):
                if isinstance(answer, Exception):
                    raise answer
                return answer
            s.ask_claude = ask
            s.judge_style(["Jokic blasts Nuggets after a crazy loss."], ["So in 1985 he beat Boston."])
            self.assertEqual(s._style_seen, {}, answer)
            self.assertEqual(s.clash_count("Jokic blasts Nuggets after a crazy loss."), 1)
            self.assertTrue(any(f == "fog word" for f, _ in s.hook_flaws("Jokic blasts Nuggets after a crazy loss.")))
            self.assertTrue(s.gives_reason("So in 1985 he beat Boston."))

    def test_broken_answers_elsewhere_are_failures(self):
        import collect
        import signals
        import media
        kept = collect.judge_titles([{"title": "NBA betting scandal grows", "tier": 1, "publisher": "x"}],
                                    ask=lambda p: '{"answer": "fine"}')
        self.assertTrue(collect.spec_title(kept[0]))                          # as before, not "all no"
        signals._judged.clear()
        signals.judge_signals(["get bad news game"], [], ask=lambda p: '{"answer": "fine"}')
        self.assertTrue(signals.story_phrase("get bad news game"))
        signals._judged.clear()
        saved = (media.ask_claude, dict(media._meta_seen))
        try:
            media._meta_seen.clear()
            media.ask_claude = lambda prompt, model=None, **kw: {"answer": "fine"}
            self.assertFalse(media.meta_ok({"_ask": [("broadcast", "File:x.webm", "ESPN warmups")]}))   # the safe side
        finally:
            media.ask_claude = saved[0]
            media._meta_seen.clear()
            media._meta_seen.update(saved[1])
        s = self.s
        saved = s.ask_claude
        try:
            s._time_seen.clear()
            s.ask_claude = lambda prompt, model=None, **kw: {"words": []}
            s.judge_ambiguous([], [], "ctx", ["Today he rests."])
            self.assertEqual(s.judged_time_lines(["Today he rests."]), ["Today he rests."])
        finally:
            s.ask_claude = saved
            s._time_seen.clear()

    def test_the_builder_calls_it(self):
        src = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertLess(src.index("    judge_style([h.get(\"text\", \"\") for h in draft.get(\"hooks\", [])[:5]],"),
                        src.index("        parts, verdict, formula = nba_hook_score(h[\"text\"])\n        hooks.append"))
        self.assertIn("        judge_style([h.get(\"text\", \"\") for h in more.get(\"hooks\", [])[:5]])", src)


class LastListsByMeaning(unittest.TestCase):
    """136. D96 module 6 part 4 (his rule 2026-11-25: an ambiguous word by meaning in context, never a list)."""

    def test_pre_nba_by_the_tagger(self):
        import photo_tags
        c = {"title": "File:Charles Barkley at East Carolina University.jpg", "team": "pre-nba",
             "pre_nba_text": True, "team_without_text": ""}
        photo_tags._apply(c, {"v": "C", "s": "interview", "e": "calm", "t": "speaks at a press table"})
        self.assertEqual(c["team"], "")
        c = {"title": "File:Jalen Brunson IHSA Class 4A championship game.jpg", "team": "pre-nba",
             "pre_nba_text": True, "team_without_text": ""}
        photo_tags._apply(c, {"v": "C", "s": "pre_nba", "e": "calm", "t": "drives, high school jersey"})
        self.assertEqual(c["team"], "pre-nba")                      # the tagger saw school: stays
        c = {"title": "x", "team": "pre-nba"}                       # pre-NBA by its date, not its title
        photo_tags._apply(c, {"v": "C", "s": "game", "e": "calm", "t": "dunks"})
        self.assertEqual(c["team"], "pre-nba")

    def test_team_marks(self):
        import media
        from unittest.mock import patch
        with patch.object(media, "teams_of", lambda p: ("", set())):
            got = media.team_marks("Charles Barkley", "Charles Barkley at East Carolina University")
        self.assertEqual(got, {"team": "pre-nba", "pre_nba_text": True, "team_without_text": ""})

    def test_evergreen_about(self):
        import evergreen as E
        E._about_seen.clear()
        try:
            t1, t2 = "Shai says he wants Durant and Westbrook's record", "Durant recalls Westbrook fallout"
            calls = []
            E.judge_about([(t1, "Kevin Durant", "Russell Westbrook"), (t2, "Kevin Durant", "Russell Westbrook")],
                          lambda p: calls.append(p) or {"yes": []})
            self.assertEqual(len(calls), 1)
            self.assertIn(t1, calls[0])
            self.assertNotIn(t2, calls[0])                          # "fallout" is a clear word
            self.assertFalse(E.about_them(t1))
            self.assertTrue(E.about_them(t2))
            E._about_seen.clear()
            E.judge_about([(t1, "a", "b")], lambda p: {"answer": "x"})   # broken answer: as before
            self.assertTrue(E.about_them(t1))
        finally:
            E._about_seen.clear()

    def test_evergreen_drops_a_pair_judged_not_about(self):
        import evergreen as E
        from unittest.mock import patch
        E._about_seen.clear()
        news = [{"title": "Shai says he wants Durant and Westbrook's record", "tier": 1},
                {"title": "Durant and Westbrook both named All-NBA", "tier": 1}]
        for n in news:
            n["about"] = E.about_them(n["title"])
        try:
            with patch.object(E, "BANK", [("Kevin Durant", "Russell Westbrook", "KD and Russ")]), \
                    patch.object(E, "fresh_news", lambda a, b, t=(): [dict(x) for x in news]), \
                    patch.object(E, "recently_used", lambda k, now=None: False), \
                    patch.object(E, "used", lambda: {}), patch.object(E, "wikipedia_item", lambda a, b: None):
                self.assertEqual(E.candidates(ask=lambda p: {"yes": []}), [])          # judged: only named
                E._about_seen.clear()
                self.assertEqual(len(E.candidates(ask=lambda p: {"yes": [1]})), 1)
        finally:
            E._about_seen.clear()

    def test_benchmark(self):
        import benchmark as B
        B._judged.clear()
        try:
            calls = []
            B.judge_titles(["Ja Morant & Devin Booker exchange words", "Kyrie handles mixtape",
                            "LeBron highlights vs Celtics"], ask=lambda p: calls.append(p) or {"yes": [1]})
            self.assertEqual(len(calls), 1)
            self.assertNotIn("mixtape", calls[0])                   # a clear off-niche word: no question
            self.assertTrue(B.drama("Ja Morant & Devin Booker exchange words"))
            self.assertFalse(B.off_niche("LeBron highlights vs Celtics"))     # judged: not off the niche
            self.assertTrue(B.off_niche("Kyrie handles mixtape"))
        finally:
            B._judged.clear()

    def test_the_callers_pass_it(self):
        sc = (ROOT / "src" / "script.py").read_text(encoding="utf-8")
        self.assertIn('ask=lambda p: ask_claude(p, CLAUDE_MODEL, where="evergreen"))', sc)
        bm = (ROOT / "src" / "benchmark.py").read_text(encoding="utf-8")
        self.assertIn("    judge_titles([r[\"title\"] for r in viral.get(\"outliers\", [])])", bm)
        for wf in ("benchmark.yml", "weekly.yml"):
            y = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            self.assertLess(y.index("Install Claude Code"), y.index("python src/benchmark.py"), wf)


class OneEraRule(unittest.TestCase):
    """137. D91 P2: team_fits is one rule (era against scope)."""

    def test_one_rule(self):
        import inspect
        import media
        body = inspect.getsource(media.team_fits)
        self.assertIn("return era_allowed(photo_era_of(c, person), line_scope(line, person, names))", body)
        scope = {"nba_named": False, "named": set(), "timed": False, "national_line": False, "current": "",
                 "past_years": [], "spells": []}
        era = {"jersey": "", "pre_nba": False, "former": True, "national": False, "national_only": False}
        self.assertTrue(media.era_allowed(era, scope))                                   # D30: no team, no time
        self.assertFalse(media.era_allowed(era, {**scope, "timed": True}))               # D42: a time, today's team
        self.assertFalse(media.era_allowed({**era, "former": False, "pre_nba": True}, {**scope, "nba_named": True}))
        nat = {**era, "former": False, "national": True}
        self.assertFalse(media.era_allowed(nat, scope))                                  # D45
        self.assertTrue(media.era_allowed({**nat, "national_only": True}, scope))        # D67
        self.assertTrue(media.era_allowed(nat, {**scope, "national_line": True}))
        past = {**scope, "past_years": [2020], "spells": [("los angeles lakers", 2018, 2025)]}
        self.assertFalse(media.era_allowed({**era, "former": False, "jersey": "atlanta hawks"}, past))   # D60
        self.assertTrue(media.era_allowed({**era, "former": False, "jersey": "los angeles lakers"}, past))


class OneWhoRule(unittest.TestCase):
    """138. D91 P1: the pick follows D50 too, through line_lock's "line" mode."""

    def test_line_mode(self):
        import media
        from unittest.mock import patch
        who = ["Luka Doncic", "Charles Barkley", "Kyle Kuzma"]
        with patch.object(media, "locks_line", lambda p: p != "Charles Barkley"), \
                patch.object(media, "outside_person", lambda n: False):
            mode, men = media.line_lock("But Redick called Luka fine.", "JJ Redick on the sideline", who)
            self.assertEqual((mode, men), ("line", ["Luka Doncic"]))
            barkley = {"kind": "photo", "title": "Charles Barkley 2019.jpg", "tag": {"who": "Charles Barkley", "v": "C"}}
            generic = {"kind": "photo", "title": "Crypto.com Arena.jpg", "tag": {"v": "A"}}
            self.assertFalse(media.lock_allows(barkley, mode, men, who, "JJ Redick on the sideline"))
            self.assertTrue(media.lock_allows(generic, mode, men, who, "JJ Redick on the sideline"))
            # a line naming only a man who locks nothing (a TV analyst): no limit, as before (D50)
            self.assertEqual(media.line_lock("Barkley laughed it off.", "", who), ("note", []))
            # the note first (D71 / D72): it names Kuzma, so Kuzma, not the line's Luka
            self.assertEqual(media.line_lock("Luka was fine.", "Kyle Kuzma on the floor", who), ("note", ["Kyle Kuzma"]))


class GateUsesMediaRules(unittest.TestCase):
    """140. D91 Q1: one definition for both stages."""

    def test_same_objects(self):
        import gate
        import media
        self.assertIs(gate.BROADCAST, media.BROADCAST)
        self.assertIs(gate.BROADCAST_AMBIG, media.BROADCAST_AMBIG)
        self.assertIs(gate.GROUP_TITLE, media.GROUP_TITLE)
        src = (ROOT / "src" / "gate.py").read_text(encoding="utf-8")
        self.assertNotIn("re.compile(r\"\\b(abc sports", src)          # no copy left
        for t, p, want in (("Gary Trent Jr. 2023.jpg", "Gary Trent Jr.", True), ("Gary Trent 1998.jpg", "Gary Trent Jr.", False),
                           ("Jaylen_Brown_2022.jpg", "Jaylen Brown", True), ("Green field.jpg", "Draymond Green", False)):
            self.assertEqual(gate.full_name_in(t, p), want, t)
            self.assertEqual(media.full_name_in_title(t, p), want, t)


class NoNetworkInTests(unittest.TestCase):
    """142. D99: the tests never reach the network (tests/no_network.py)."""

    def setUp(self):
        self.mark = no_network.mark()

    def tearDown(self):
        no_network.forget_since(self.mark)           # the calls these tests make on purpose

    def test_every_test_file_loads_the_guard(self):
        import ast
        files = sorted((ROOT / "tests").glob("test_*.py"))
        self.assertGreaterEqual(len(files), 3)
        for f in files:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            top = [a.name for n in tree.body if isinstance(n, ast.Import) for a in n.names]
            self.assertIn("no_network", top, f"{f.name} must import no_network (D99)")

    def test_every_way_in_this_process_is_refused(self):
        import http.client
        import socket
        import urllib.request
        import media
        import wiki_http
        G = no_network
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tries = [lambda: socket.getaddrinfo("commons.wikimedia.org", 443),
                     lambda: socket.gethostbyname("localhost"),
                     lambda: socket.gethostbyname_ex("example.com"),
                     lambda: socket.gethostbyaddr("127.0.0.1"),
                     lambda: socket.create_connection(("127.0.0.1", 80), timeout=1),
                     lambda: tcp.connect(("127.0.0.1", 80)),
                     lambda: tcp.connect_ex(("10.0.0.1", 80)),
                     lambda: udp.sendto(b"x", ("8.8.8.8", 53)),
                     lambda: udp.sendto(b"x", 0, ("8.8.8.8", 53)),
                     lambda: udp.sendmsg([b"x"], [], 0, ("8.8.8.8", 53)),
                     lambda: http.client.HTTPSConnection("commons.wikimedia.org", timeout=1).connect(),
                     lambda: urllib.request.urlopen("https://commons.wikimedia.org/w/api.php", timeout=1),
                     lambda: wiki_http.fetch("https://commons.wikimedia.org/w/api.php", "ua", 1),
                     lambda: media.get("https://example.com/")]
            for n, call in enumerate(tries):
                before = len(G.CALLS)
                with self.assertRaises(OSError, msg=n):       # NetworkCall, or urllib's URLError around it
                    call()
                self.assertEqual(len(G.CALLS), before + 1, n)
        finally:
            udp.close()
            tcp.close()

    def test_a_child_process_gets_a_closed_proxy(self):
        for name in no_network.PROXY_VARS:
            self.assertEqual(os.environ.get(name), no_network.DEAD_PROXY, name)
        self.assertNotIn("NO_PROXY", os.environ)
        self.assertNotIn("no_proxy", os.environ)
        code = ("import urllib.request, sys\n"
                "try:\n    urllib.request.urlopen('https://commons.wikimedia.org/w/api.php', timeout=5)\n"
                "except Exception as e:\n    sys.exit(7 if 'refused' in str(e).lower() else 3)\nsys.exit(0)")
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 7, r.stderr)          # the closed port refused it at once

    def test_a_swallowed_call_still_fails_its_test(self):
        import socket

        class Inner(unittest.TestCase):
            def test_swallows(self):
                try:                                   # like media.commons_videos: everything caught
                    socket.getaddrinfo("commons.wikimedia.org", 443)
                except BaseException:                  # noqa: BLE001
                    pass

            def test_clean(self):
                pass
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(Inner).run(result)
        self.assertEqual([t.id().rsplit(".", 1)[1] for t, _ in result.failures], ["test_swallows"])
        self.assertIn("reached the network", result.failures[0][1])
        self.assertFalse(result.wasSuccessful())

    def test_the_commons_search_of_test_104_is_stubbed(self):
        src = (ROOT / "tests" / "test_regressions.py").read_text(encoding="utf-8")
        body = src.split("def test_refused_never_offered", 1)[1].split("def test_replaced_stay_marked", 1)[0]
        self.assertIn("media.commons_videos = lambda *a, **k: []", body)


class NoRealClaudeInTests(unittest.TestCase):
    """141. D98: the tests never call the real Claude (tests/no_real_claude.py)."""

    def setUp(self):
        self.mark = no_real_claude.mark()

    def tearDown(self):
        no_real_claude.forget_since(self.mark)       # the calls these tests make on purpose

    def test_every_test_file_loads_the_guard(self):
        import ast
        files = sorted((ROOT / "tests").glob("test_*.py"))
        self.assertGreaterEqual(len(files), 3)
        for f in files:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            top = [a.name for n in tree.body if isinstance(n, ast.Import) for a in n.names]
            self.assertIn("no_real_claude", top, f"{f.name} must import no_real_claude (D98)")

    def test_every_way_in_this_process_is_refused(self):
        G = no_real_claude
        tries = [lambda: subprocess.run(["claude", "-p", "--model", "x"], input="hi", capture_output=True, text=True),
                 lambda: subprocess.run(["/opt/node22/bin/claude", "-p"]),
                 lambda: subprocess.run("claude -p 'hi'", shell=True),
                 lambda: subprocess.check_output(["claude", "--version"]),
                 lambda: subprocess.Popen([Path("/usr/bin/claude")]),
                 lambda: os.system("claude -p hi")]
        if hasattr(os, "posix_spawnp"):
            tries.append(lambda: os.posix_spawnp("claude", ["claude", "-p"], dict(os.environ)))
        for n, call in enumerate(tries):
            before = len(G.CALLS)
            with self.assertRaises(G.RealClaudeCall, msg=n):
                call()
            self.assertEqual(len(G.CALLS), before + 1, n)
        # other programs run as before, also ones whose name only starts with "claude"
        self.assertFalse(G._is_claude(["claude-helper"]) or G._is_claude(["git", "claude"]) or G._is_claude([]))
        self.assertEqual(subprocess.run(["true"]).returncode, 0)

    def test_a_shell_or_a_child_process_gets_the_fake(self):
        G = no_real_claude
        self.assertEqual(shutil.which("claude"), str(G.FAKE))
        r = subprocess.run("echo hi >/dev/null; claude -p hi", shell=True, capture_output=True, text=True)
        self.assertEqual(r.returncode, G.EXIT)
        r = subprocess.run([sys.executable, "-c", "import subprocess, sys; "
                            "sys.exit(subprocess.run(['claude', '-p'], input='x', text=True).returncode)"],
                           stderr=subprocess.DEVNULL)
        self.assertEqual(r.returncode, G.EXIT)
        self.assertEqual(G.mark()[1], self.mark[1] + 2)

    def test_a_swallowed_call_still_fails_its_test(self):
        class Inner(unittest.TestCase):
            def test_swallows(self):
                try:                                   # like evergreen.judge_about: everything caught
                    subprocess.run(["claude", "-p"])
                except BaseException:                  # noqa: BLE001
                    pass

            def test_child(self):
                subprocess.run("claude -p", shell=True, stderr=subprocess.DEVNULL)   # only the fake answers

            def test_clean(self):
                pass
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(Inner).run(result)
        self.assertEqual(sorted(t.id().rsplit(".", 1)[1] for t, _ in result.failures), ["test_child", "test_swallows"])
        self.assertTrue(all("called the real Claude" in text for _, text in result.failures))
        self.assertFalse(result.wasSuccessful())

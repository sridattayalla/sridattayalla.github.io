# Architecture — What Krishna Said

This document is the binding per-page contract. Writers follow it exactly; the checker
(`python3 tools/check.py`) enforces the mechanical parts. When this document and a fact
sheet disagree, the fact sheet wins and this document is wrong.

## The method (every page)

Three layers, one rule:

1. **The verse, literally.** Every verse appears as IAST text plus a literal gloss, copied
   verbatim from the registry (see `docs/versepacks/<page-file>.html`). The gloss is
   deliberately plain — it is the floor, not the ceiling, of meaning.
2. **The lenses, attributed.** Every interpretation is named: "Shankara reads...",
   "Gandhi called...", "Ambedkar charged...". No interpretation floats free.
3. **No verdicts.** The book never says "the correct reading is...". It says "readers
   disagree; here is the disagreement." The reader is handed the tools, not a conclusion.

## Voice (every page)

- Second person, plain words, concrete images. "You have read a table of contents" beats
  "The reader will encounter structural elements."
- Real numbers over adjectives — and every number carries a `<!-- prov: FS-ID -->`
  annotation (see the writer contract).
- No "simply", "just", "obviously", "of course". No filler praise. No rhetorical questions
  stacked three deep.
- Sanskrit words appear in IAST diacritics when they are terms (dharma, guṇa); plain
  transliteration for names (Krishna, Arjuna, Sanjaya).
- Takeaways are written as claims a reader could repeat from memory, not section titles.

## The five parts

| Part | Pages | Owns | Ends by handing off |
|---|---|---|---|
| 0 Orientation | 01–04 | The reading toolkit: how verses are shown, the epic frame, the cast, the chapter map | a folded map and four words to carry |
| 1 Four Words | 05–08 | dharma, karma, yoga, ātman/brahman — the load-bearing vocabulary | the vocabulary the poem will use |
| 2 The Walk | 09–27 | All 18 chapters in order, verse by verse, with the argument each chapter makes | the poem finished, the reading not begun |
| 3 The Lenses | 28–37 | How the Gita became many Gitas: classical schools, modern activists, critics, global and scholarly readers | every lens attributed, none crowned |
| 4 Your Reading | 38–40 | The contested verses assembled; the questions that never close; the full-circle loop | the door out |

## Source IDs (provenance)

| FS-ID | Sheet | Use for |
|---|---|---|
| FS-TEXT | research/text-facts.md | text, structure, verse counts, chapter contents |
| FS-MAH | research/mahabharata-facts.md | epic frame, characters, war numbers |
| FS-LENSES | research/lenses-facts.md | classical commentators and schools |
| FS-MOD | research/modern-facts.md | Vivekananda, Tilak, Aurobindo, Gandhi, Ambedkar, Bhaktivedanta, Wilkins, Oppenheimer |
| FS-PATT | research/pattanaik-facts.md | Pattanaik's My Gita and its critics |
| FS-ACAD | research/academic-facts.md | dating, layers, methods |
| FS-GLOBAL | research/global-facts.md | global journeys and receptions |
| SRC-IAST | research/text-facts.md (pinned IAST source) | claims about the Sanskrit text itself |

## Term hazards (read before writing any page)

The term ledger (`tools/terms.json`) gives every term exactly one defining page. The
checker fires if a term appears earlier. Three defenses, in order of preference:

1. **Rephrase.** On pages before a term's defining page, use plain English ("duty",
   "the discipline", "the deathless self") instead of the term.
2. **Annotate.** If the term is unavoidable (the Sanskrit literally contains it), put
   `<!-- term-ok: foreshadowed; defined on NN -->` within three lines of *every* use.
3. **Compounds are usually safe.** "dharmakṣetre" does not match the "dharma" pattern
   (the diacritic blocks it); "yogaśāstra" does not match "yoga". Check, don't assume.

Known hazards: "dharma" is defined on 05, but pages 02–04 naturally want it (the field is
dharmakṣetra; the cast discussion wants "a kshatriya's dharma"). Use "duty" or "role"
there, or one annotated foreshadow. "karma" is defined on 06 — pages before that say
"action and its consequences". "yoga" is defined on 07 — pages before that say
"discipline". "bhakti" is defined on 18-ch09 — before that, "devotion" (lowercase, plain).

Takeaways and ledes follow the same rules — the checker scans them too (takeaways are
scanned for terms and provenance; ledes and kickers are scanned for terms).

## SVG conventions

Five pages carry diagrams (04, 22, 23, 24, 40 — specs below). Rules:

- Inline `<svg role="img" viewBox="...">` with a `<title>` child. Strokes use
  `currentColor`; fills use `none` or design tokens from DESIGN.md. No external images.
- Text inside SVG: font-size at least 12 in a viewBox no larger than 800×520. Keep labels
  short — SVG text does not wrap.
- Diagram labels and captions are excluded from term-order and provenance checks (the
  figure carries class `diagram`), but they still count toward the word window.
- One diagram per page. A diagram teaches exactly one structure.

## Verse figures that carry ledger terms (read before writing a verse page)

Verse glosses and notes are registry-locked — you copy them verbatim and cannot reword
them. A few contain ledger terms. Two consequences:

1. **Dfn placement.** Where a note or gloss on YOUR page contains a term your page
   defines, place that term's `<dfn>` in your prose BEFORE the first verse figure that
   carries it — otherwise the figure counts as a use before the definition:

   | Page | Verse | Field | Term |
   |---|---|---|---|
   | 11-ch02-sage | 2.39 | note | sāṅkhya, buddhi-yoga |
   | 11-ch02-sage | 2.47 | note | adhikāra |
   | 11-ch02-sage | 2.72 | note | nirvāṇa |
   | 12-ch03 | 3.9 | note | yajña |
   | 13-ch04 | 4.6 | gloss and note | māyā |
   | 13-ch04 | 4.7 | note | avatāra |
   | 20-ch11 | 11.33 | note | nimitta |
   | 24-ch15 | 15.1 | note | aśvattha |
   | 27-ch18 | 18.2 | note | saṃnyāsa, tyāga |

2. **Provenance inside notes.** One registry note carries a year: on 20-ch11, the 11.12
   note mentions 1958 (the Jungk retelling). Place `<!-- prov: FS-GLOBAL -->` within ten
   lines of that figure; the fact lives in research/global-facts.md.

## Part 0 — Orientation

### 01-how-to-read.html — How to Read This Book

**Purpose** — Teach the reading interface before the content: what the three layers are,
how IAST works, what a śloka is, and what "no verdict" means.

**Lede** — Every verse appears in three layers: the Sanskrit in Roman letters, a literal
gloss, and the arguments readers have had about it — this book never picks a winner.

**Sections**
1. "Three layers" — walk through one example figure format (describe it, no verse yet):
   IAST line, gloss line, translation note when translators disagree.
2. "Sanskrit you can read" — define IAST (Roman letters with diacritics; karmaṇyeva as the
   worked example of sandhi: karmaṇi + eva fused), define sandhi, show how the gloss
   unfuses it.
3. "The verse form" — define śloka: a couplet, two lines of two halves each; note that
   this book's verse figures show the halves separated by a vertical bar. The Gita runs to
   seven hundred ślokas (prov FS-TEXT).
4. "How to argue with this book" — every interpretation attributed; disagreements shown
   side by side; the book's silence is a feature. Point forward: the lenses arrive in
   Part 3.

**Terms defined** — IAST, sandhi, śloka.

**Term warnings** — Do not use: dharma, karma, yoga, bhakti, ātman (all defined later).
Use "the load-bearing words arrive next" phrasing. "Veda" and "upaniṣad" are defined on
04 — avoid here.

**Takeaways**
- Every verse appears in three layers: IAST text, a literal gloss, and a translation note
  where translators disagree.
- IAST is Sanskrit in Roman letters with marks that make pronunciation unambiguous.
- A śloka is a couplet of two lines, each split into two halves; the Gita runs to seven
  hundred of them.
- Interpretations are always attributed; this book never declares a winner.

**Bridge-in** — First page: state where the reader stands (the cover promised no verdicts;
here is the machinery that keeps that promise).

**Handoff to 02** — Before the poem, the frame: a blind king, a reporter with divine
sight, and two armies drawn up on a field.

**Sources** — FS-TEXT.

### 02-the-frame.html — The Frame: A King, a Reporter, Two Armies

**Purpose** — The Mahabharata container: who is listening, who is narrating, and why the
frame changes everything you hear.

**Lede** — The Gita is eighteen chapters inside the world's longest poem, narrated by a
reporter with divine sight to a blind king who has already set the war in motion.

**Sections**
1. "The bigger poem" — define Mahabharata (the epic of the Bharata dynasty; roughly a
   hundred thousand verse lines, prov FS-MAH; eighteen books). The Gita sits in the sixth
   book — define Bhishma Parvan (the Book of Bhishma, named for the general who commands
   on the war's first days).
2. "The narrator and his listener" — Sanjaya: charioteer, court reporter, granted
   distant sight by the sage Vyasa; Dhritarashtra: the blind Kaurava king whose hundred
   sons face his brother's five. The dialogue you read is a battlefield speech reported
   live to the anxious sponsor of the war.
3. "Why the frame matters" — the poem's first verse names the field dharmakṣetra — the
   field of duty (one term-ok foreshadow of dharma allowed here, or say "the field where
   duty is tested"); the king's first recorded word is māmakāḥ — "mine". The frame stages
   possessiveness before the poem answers it.
4. "What you are about to overhear" — define Kurukshetra (the plain near modern Delhi
   where the war is fought, prov FS-MAH); set expectations: eighteen days of war, a
   conversation of about an hour inside it (frame timing from FS-MAH).

**Terms defined** — Mahabharata, Bhishma Parvan, Kurukshetra.

**Term warnings** — "dharma" belongs to 05: prefer "duty" or one annotated foreshadow in
section 3. No karma/yoga/atman vocabulary.

**Takeaways**
- The Gita is Book 6 of the Mahabharata, an epic about two branches of one family
  fighting a war of succession.
- Sanjaya narrates: he reports the battlefield to the blind king Dhritarashtra.
- The first verse names the field "the field of duty", and the king's first word is
  "mine" — the frame stages the question the poem will press.
- What Krishna says is heard twice over: once by Arjuna, once by the anxious king.

**Bridge-in** — From 01's takeaways: you know how every verse will be presented; now see
where the conversation happens and who is eavesdropping.

**Handoff to 03** — The frame is a conversation between a reporter and a king; the cast
is who they are reporting on.

**Sources** — FS-MAH, FS-TEXT.

### 03-the-cast.html — The Cast of the War

**Purpose** — The people on the field: the two families, Arjuna and Krishna, and the
fourfold social order the poem will lean on.

**Lede** — Two cousins lead armies of cousins; the charioteer is a god in disguise; every
fighter carries a role the poem names without explaining.

**Sections**
1. "One family, two arrays" — the five Pandava brothers (Yudhishthira, Bhima, Arjuna,
   Nakula, Sahadeva) against the hundred Kaurava sons of Dhritarashtra; the shared
   grandfather Bhishma and the teacher Drona fight for the Kaurava side — Arjuna's
   beloveds are his targets (FS-MAH).
2. "The archer and his driver" — Arjuna: third Pandava, the family's supreme archer.
   Krishna: of the Vrishni clan, divine by reputation, who offered his army to one side
   and himself to the other — both sides chose; he drives Arjuna's chariot and will not
   fight (FS-MAH).
3. "The fourfold order" — define varna (the fourfold social division of work), then
   brahmin (priests, teachers), kshatriya (warriors, rulers), vaishya (merchants,
   farmers, herders), shudra (laborers, service). State plainly: this is the order the
   poem will invoke, and later readers will fight over those invocations — the fight
   arrives in Parts 3 and 4.
4. "The scale of the array" — an akṣauhiṇī is the epic's counting unit for an army
   (defined properly on 04; here give the sense of hugeness, numbers on 04).

**Terms defined** — varna, kshatriya, brahmin, vaishya, shudra.

**Term warnings** — "dharma" still belongs to 05 — say "a kshatriya's role" or "the
warrior's work". akṣauhiṇī is defined on 04: mention it by name once with a term-ok, or
defer the word to 04 and say "the epic's unit of army-counting" here.

**Takeaways**
- The war is one family split in two: five Pandava brothers against a hundred Kaurava
  cousins.
- Arjuna is the Pandavas' finest archer; Krishna has vowed not to fight and drives
  Arjuna's chariot.
- Varna is the fourfold social order of work: brahmin, kshatriya, vaishya, shudra.
- The Gita will lean on varna in verses that later readers fight over — meet the word
  now, judge it later.

**Bridge-in** — From 02: the frame showed who is listening; now meet who is being
reported on.

**Handoff to 04** — The people stand on the field; here is the shape of the conversation
they are about to have.

**Sources** — FS-MAH.

### 04-the-map.html — The Map: Eighteen Chapters, Three Hexads

**Purpose** — The Gita's own architecture: eighteen chapters in three blocks of six, the
colophon formula, the older books underneath, the army-scale numbers, and the reading map
for Part 2.

**Lede** — Eighteen chapters fall into three blocks of six — a collapse, a cure, a
closing — and every chapter ends with a receipt naming the dialogue itself.

**Sections**
1. "Three hexads" — chapters 1–6 answer the collapse; 7–12 put the divine in full view;
   13–18 settle the self and close the deal. Name the hexads; promise the diagram.
2. "The receipt at the end of each chapter" — define colophon: every chapter closes with
   the same formula placing the dialogue "in the Brahmavidyā, the yogaśāstra, the
   dialogue of Krishna and Arjuna" (SRC-IAST / FS-TEXT for the formula). The poem
   describes itself as a teaching inside a report.
3. "The books under the floor" — define Veda (the oldest hymn collections, ritual and
   recitation) and upaniṣad (the later forest dialogues on the self); the Gita quotes
   both worlds and argues with both (FS-TEXT, FS-ACAD). Define parvan (a book of the
   Mahabharata — the Gita lives in the sixth).
4. "The scale" — define akṣauhiṇī precisely: chariots, elephants, horse, foot in the
   epic's ratio (numbers from FS-MAH, prov'd); eighteen akṣauhiṇīs on the field, nine a
   side.
5. "Your map" — the diagram (below); Part 2 of this book walks the chapters in order.

**Terms defined** — parvan, akṣauhiṇī, upaniṣad, Veda, colophon.

**Term warnings** — Varna and kshatriya are free (defined 03). "Dharma" belongs to 05
and "karma" to 06 — say "duty" and "consequences". The English word "yoga" belongs to
07: quote the colophon's Sanskrit compound (yogaśāstra — pattern-safe) and never write
the English word; "discipline" is the plain substitute. "Ātman"/"brahman" belong to 08.

**SVG spec** — 18-chapter grid: three rows of six rounded cells; row captions "The
response (1–6)", "The divine (7–12)", "The self (13–18)"; cells numbered 1–18; the
chapter numbers are structural labels (diagram class exempts them from provenance). A
subtle arrow left-to-right within rows and a return arrow from 18 back toward 1 is
optional — keep it clean. Title: "Eighteen chapters in three hexads".

**Takeaways**
- Eighteen chapters in three blocks of six: the response, the divine, the self.
- Every chapter ends with the same colophon naming the dialogue itself.
- The Gita's vocabulary comes from older strata: the Vedas' ritual world, the Upaniṣads'
  inquiry into the self.
- The Walk pages of this book follow the chapters in order — that grid is your map.

**Bridge-in** — From 03: the cast stands on the field; now see the shape of the
conversation they are about to have.

**Handoff to 05** — The map is folded; the walk begins with four words the poem cannot
stop using.

**Sources** — FS-MAH, FS-TEXT.

## Part 1 — Four Words

### 05-dharma.html — Dharma: The Load-Bearing Word

**Purpose** — The untranslatable word the whole poem leans on: what holds, what unravels,
and the collision Arjuna's collapse stages.

**Lede** — Dharma is the word the Gita leans on hardest and never defines: what holds —
a beam, a duty, an order, a role.

**Sections**
1. "A word from a root that means to hold" — define dharma (from dhṛ, to hold: that
   which holds up a person, a role, a world), define adharma (what unravels the holding),
   define svadharma (your own holding — the duty attached to your position). The word
   family carries architecture, not just ethics.
2. "Why translation fails" — duty, law, religion, righteousness each catch one facet;
   every translation of the Gita is already an interpretation (FS-LENSES for translator
   choices). Point back to 01's translation-note layer.
3. "The collision the poem stages" — Arjuna's crisis in chapter 1 is two holdings
   colliding: the kshatriya's role to fight and the kinsman's dread of destroying his
   family. The poem will not dissolve this tension; it will walk through it.
4. "Where the word will return" — the svadharma verses (the fork of chapter 3's better-
   own-path teaching, and the settlement chapter's last rulings), and the varna verse
   that ties social order to divine order — flagged honestly as the most contested verse
   in the poem, handled in Parts 3 and 4.

**Terms defined** — dharma, adharma, svadharma.

**Term warnings** — "karma" belongs to 06: say "consequences". "yoga" belongs to 07: say
"discipline". Varna/kshatriya already defined on 03 — free to use.

**Takeaways**
- Dharma comes from a root meaning "to hold": what holds up a person, a role, a world.
- Adharma is what unravels; svadharma is your own holding — the duty attached to your
  position.
- No English word carries all of it; every translation of the Gita is already an
  interpretation.
- Arjuna's collapse is two dharmas colliding — his role as a warrior against his dread
  as a kinsman.

**Bridge-in** — From 04's map: the poem's eighteen chapters lean on a handful of words;
the first is the load-bearing one.

**Handoff to 06** — Dharma says what holds; the next word says what your actions leave
behind.

**Sources** — FS-TEXT, FS-LENSES.

### 06-karma.html — Karma: Action and Its Echo

**Purpose** — Karma's three senses in one word, the misunderstanding to avoid, and why
the Gita cannot say "stop acting".

**Lede** — Karma means the action, the action's echo, and the wheel of echo after echo —
and the Gita's answer to it is not to stop acting.

**Sections**
1. "Three senses in one word" — the deed itself; the trace it leaves; the cycle the
   traces drive (rebirth — name it plainly, the full vocabulary arrives on 08). The word
   is a family, not a single idea.
2. "The older background" — the Vedic ritual act whose power was mechanical; the
   Upaniṣadic questioning of it; the Gita's twist: act, but release the claim on results
   (FS-TEXT, FS-ACAD). The famous verse that states it arrives in the walk (2.47);
   name-check without quoting.
3. "The misunderstanding to avoid" — karma is not fate. It says acts are effective and
   consequences are real, not that your script is written. The difference matters: the
   poem will command action, not resignation.
4. "Why the poem cannot say stop" — existence itself acts (the argument chapter 3 makes,
   previewed): breath is action; the question is never whether to act but how to hold
   the acting.

**Terms defined** — karma.

**Term warnings** — dharma is now free (defined 05) — use it. "yoga" still belongs to
07. "saṃsāra"/"mokṣa" belong to 08 — say "the cycle" and "release".

**Takeaways**
- Karma names three things at once: the deed, its consequence, and the cycle the
  consequences drive.
- The Gita's move is not inaction but detached action — give up the claim on fruits,
  not the act.
- Karma is not fate: it says acts are effective, not that your script is written.
- Every later lens in this book reads "detached action" differently — hold the word,
  defer the verdict.

**Bridge-in** — From 05: dharma is what holds; karma is what moves and what sticks.

**Handoff to 07** — If action cannot stop, the poem needs a word for how to act: yoga.

**Sources** — FS-TEXT, FS-ACAD.

### 07-yoga.html — Yoga: The Yoke

**Purpose** — Yoga as the Gita uses it: any discipline that harnesses; the three great
paths; jñāna as knowledge's engine; the fork of which path is supreme.

**Lede** — Yoga in the Gita is not postures — it is a yoke: any discipline that harnesses
you to a path, and the poem offers three.

**Sections**
1. "From yoke to discipline" — define yoga (root yuj, to yoke: a discipline, a method, a
   harness). In the Gita the word names methods and states — including equanimity itself.
   No postures, no mats; those arrive centuries later in other texts (FS-TEXT).
2. "The three paths" — define karma-yoga (the discipline of action), jñāna-yoga (the
   discipline of knowledge), bhakti-yoga (the discipline of devotion). The poem deploys
   all three; which is supreme is a question the text opens and readers never closed
   (FS-LENSES).
3. "Jñāna" — define jñāna (knowledge — specifically the Upaniṣadic knowledge of the
   self); distinguish from information; it is the driver of the knowledge path.
4. "The fork previewed" — chapter 2 announces two disciplines, the chapter of action
   defends one, the devotional chapters crown another — the ranking dispute begins inside
   the poem itself, and every lens in Part 3 inherits it.

**Terms defined** — yoga, karma-yoga, jñāna-yoga, bhakti-yoga, jñāna.

**Term warnings** — karma, dharma free. "ātman"/"brahman"/"saṃsāra"/"mokṣa" belong to
08 — "the self", "the all", "the cycle", "release". Hyphenate the compound terms exactly
as the ledger spells them: karma-yoga, jñāna-yoga, bhakti-yoga. Written with a space
("bhakti yoga"), the plain word bhakti fires early-use (defined on 18-ch09); the
hyphenated compound is pattern-safe.

**Takeaways**
- Yoga is a yoke: a discipline that binds you to a path — the Gita uses the word for
  methods, not stretches.
- The poem names three great disciplines: action, knowledge, devotion.
- Jñāna is the knowledge of the self the Upaniṣads pursue — one of yoga's engines.
- Which path is supreme is a fork the Gita itself opens and readers never closed.

**Bridge-in** — From 06: karma says you cannot stop acting; yoga is how to act.

**Handoff to 08** — The last two words of the four are about who is acting — and what
the self stands on.

**Sources** — FS-TEXT, FS-LENSES.

### 08-atman.html — Atman: The Self and Its Background

**Purpose** — The Upaniṣadic floor: the deathless self, the all it belongs to, the wheel
it rides, the stopping of the wheel — and the deepest fork in the book.

**Lede** — Behind the battlefield conversation stands an older claim: the self is
deathless, it belongs to an all, and the wheel it rides can be stopped.

**Sections**
1. "The self beneath the changes" — define ātman (the self beneath body and mind; the
   verse that says it was never born arrives in the walk — 2.20 previewed).
2. "The all" — define brahman (the Upaniṣads' name for the one reality behind
   appearances; not a god among gods, but the floor under the floor). Relation to ātman:
   the poem will say they are kin — how kin is the dispute.
3. "The wheel and the stop" — define saṃsāra (the wheel of death and rebirth the
   echoes of action drive) and mokṣa (release, the wheel's stopping; the poem's word for
   the state — brahmanirvāṇa — arrives in the walk).
4. "The deepest fork" — are ātman and brahman identical? One great reader says yes,
   another says the souls are real parts of God, a third says they never merge. The
   three answers become the first three lenses of Part 3. This book will not rank them.

**Terms defined** — ātman, brahman, saṃsāra, mokṣa.

**Term warnings** — All four of this page's terms defined here. bhakti still belongs to
18-ch09 — "devotion" only.

**Takeaways**
- Ātman is the self beneath the changing body and mind — the Gita says it was never
  born and never dies.
- Brahman is the Upaniṣads' name for the reality behind all appearances.
- Saṃsāra is the wheel of rebirth karma drives; mokṣa is its stopping.
- Whether ātman and brahman are identical is the deepest fork in the book — three
  chapters of lenses will disagree.

**Bridge-in** — From 07: the three disciplines are paths; these last two words name who
walks them and where they lead.

**Handoff to 09** — Four words carried; the poem begins — a chariot stops between two
armies.

**Sources** — FS-TEXT, FS-LENSES.

## Part 2 — The Walk

Walk pages follow a fixed inner shape: bridge from the previous chapter → scene-setting
(one or two paragraphs) → verse beats (the chapter's argument, woven through the figures
in order) → a closing movement that hands off. Verses are copied verbatim from
`docs/versepacks/<page-file>.html` in the order the manifest lists them. Word window
1200–2200.

### 09-ch01.html — Chapter 1 — The Collapse

**Verses** — 1.1, 1.21, 1.22, 1.28, 1.29, 1.30, 1.41, 1.42, 1.47.
**Beats** — 1.1 the king's question (dharmakṣetra, "mine"); 1.21–22 Arjuna has Krishna
place the chariot between the armies, facing his teachers and kinsmen; 1.28–30 seeing
them, his limbs fail, mouth dries, bow slips; 1.41–42 the cascade — family law breaks,
women are corrupted, the mixing of castes, ancestors fall; 1.47 he sits down, casting
aside bow and arrows.
**Lede** — The poem opens not with teaching but with a breakdown: the greatest archer of
his age looks at the enemy line and cannot lift his bow.
**Sections** — (1) "A question from the stands" — the frame voice and the field;
(2) "Place my chariot" — Arjuna's survey of the enemy line; (3) "The bow slips" — the
body's mutiny and the cascade argument; (4) "Seated in the middle" — the collapse
completed, the teaching about to begin.
**Takeaways**
- The Gita begins in refusal: Arjuna, seeing cousins and teachers across the line,
  drops his bow.
- His stated reason is an argument about consequences: winning this way destroys the
  family order.
- The frame watches: Sanjaya reports every tremor to the king who set the war in motion.
- Chapter 2 will open with Arjuna's own diagnosis — grief and confusion — and a request
  to be taught.
**Bridge-in** — From 08: four words carried, the poem begins — not with a teaching but
with a collapse.
**Handoff to 10** — Krishna's first answer will not mention duty at all: it cuts deeper,
to the self.
**Sources** — FS-MAH, FS-TEXT.

### 10-ch02-self.html — Chapter 2 (Part 1) — The Deathless Self

**Verses** — 2.11, 2.13, 2.20, 2.22, 2.23, 2.27, 2.31, 2.32, 2.37, 2.38.
**Beats** — 2.11 you grieve for those who need no grief; 2.13 as the embodied passes
through bodies; 2.20 the self is never born, never dies; 2.22–23 garments are shed,
weapons do not cut it, fire does not burn it; 2.27 death is certain for the born;
2.31–32 the warrior's role — no better battle for a kshatriya than a lawful war; 2.37–38
stand and win — without attachment, without enemy-heat.
**Lede** — Krishna's first reply ignores the family-law arithmetic entirely: the one who
grieves — the self — was never born and cannot die.
**Sections** — (1) "The rebuke before the comfort" — 2.11's refusal of the premise;
(2) "The self that sheds bodies" — the garment argument and its limits (the verse is a
claim, not a proof — note that the poem asserts, it does not demonstrate);
(3) "The second argument, worldly" — the kshatriya case, dharma's first appearance in
Krishna's voice; (4) "Equal heat" — 2.37–38 close the first movement.
**Takeaways**
- Krishna's opening move is not consolation but a claim: the self does not die.
- The argument runs from the unchanging self to the harmlessness of killing — asserted,
  not proven; the poem asks for trust here.
- Then a second argument, worldly: a warrior's role makes this the right battle.
- The movement ends where the next one begins: equal-mindedness in gain and loss.
**Bridge-in** — From 09: Arjuna ended chapter 1 seated, bow cast aside; chapter 2 opens
with Krishna refusing his premise.
**Handoff to 11** — Verse 2.39 will announce a turn: two disciplines, and the chapter's
second half teaches the one Arjuna will actually walk.
**Sources** — FS-TEXT.

### 11-ch02-sage.html — Chapter 2 (Part 2) — The Fork in the Road

**Verses** — 2.39, 2.47, 2.48, 2.54, 2.55, 2.62, 2.63, 2.70, 2.72.
**Beats** — 2.39 this wisdom you have heard; now hear of the discipline of action (the
fork announced); 2.47 your right is to the action alone, never to its fruits; 2.48
equanimity is called yoga; 2.54 Arjuna asks how the settled one speaks, sits, moves;
2.55–70 the portrait of the sthitaprajña, ending in the ocean image (2.70); 2.62–63 the
chain of ruin — attachment, desire, anger, delusion, lost memory, lost discernment;
2.72 the state of brahman, the poem's word nirvāṇa.
**Lede** — Verse 2.39 splits chapter 2 in two: knowledge or disciplined action — and the
most quoted verse in the poem stands at the gate between them.
**Sections** — (1) "Two disciplines announced" — the fork in the text itself; (2) "The
verse everyone knows" — 2.47 read slowly, both halves; (3) "The settled one" — the
portrait verses; (4) "The chain of ruin" — 2.62–63 as psychology; (5) "A borrowed word"
— nirvāṇa in a poem arguing with Buddhist rivals (FS-ACAD for the Buddhist context).
**Terms defined** — sāṅkhya, buddhi-yoga, adhikāra, sthitaprajña, nirvāṇa.
**Takeaways**
- Verse 2.39 announces two paths — the fork every later reader maps onto.
- Your right is to the act alone, never to its fruits: the most translated line in the
  poem.
- The portrait of the settled one makes the teaching visible as conduct, not creed.
- The chain of ruin gives the mechanism: attachment hardens into delusion.
- The chapter's last word, nirvāṇa, is borrowed from the poem's Buddhist rivals — the
  Gita is in conversation, not in a vacuum.
**Bridge-in** — From 10: the deathless-self movement closed with equal-mindedness; now
the chapter names the discipline that produces it.
**Handoff to 12** — Chapter 3 answers the obvious objection: if fruits don't belong to
you, why lift a finger at all?
**Sources** — FS-TEXT, FS-ACAD.

### 12-ch03.html — Chapter 3 — The Case for Action

**Verses** — 3.5, 3.9, 3.19, 3.27, 3.35, 3.37, 3.42, 3.43.
**Beats** — 3.5 no one exists even for a moment without acting; 3.9 act with sacrifice
as the frame, free of attachment; 3.19 therefore act without attachment, as Janaka did;
3.27 the strands act on the strands — the "I do it" is confusion; 3.35 better your own
path imperfect than another's done well; 3.37 desire is the enemy, born of passion;
3.42–43 the ladder — senses, mind, discernment, and desire above them all.
**Lede** — Chapter 3 takes the hardest objection head-on: if the fruits don't belong to
you, why lift a finger at all?
**Sections** — (1) "The objection in Arjuna's mouth" — why the chapter exists;
(2) "Existence acts" — 3.5 and 3.19; (3) "The actor relocates" — 3.27's strands
(yajña's Vedic frame given its due); (4) "Your own imperfect path" — svadharma's second
appearance; (5) "The enemy above the watchtower" — 3.37–43.
**Terms defined** — guṇa, yajña, prakṛti.
**Takeaways**
- Action is not optional: existence itself acts.
- The strands act on the strands — the "I" that claims authorship is a misreading.
- Better your own path walked imperfectly than another's walked well.
- Desire, not action, is the enemy — and it hides above the mind's watchtower.
**Bridge-in** — From 11: the famous verse detached the act from its fruits; chapter 3
defends the act itself.
**Handoff to 13** — Where did this teaching come from? Chapter 4 claims it is older than
either speaker.
**Sources** — FS-TEXT, FS-ACAD.

### 13-ch04.html — Chapter 4 — The Descending Teaching

**Verses** — 4.1, 4.2, 4.6, 4.7, 4.8, 4.13, 4.34, 4.37, 4.38.
**Beats** — 4.1–2 the lineage — taught to the sun, to Manu, to Ikṣvāku, lost by time,
now retold; 4.6 I take birth by my own power, not karma's; 4.7–8 whenever right order
fades I take birth — to protect the good, ruin the wicked, set the order right; 4.13 the
four varnas created by me, according to strands and actions; 4.34 approach the knowers,
question, serve; 4.37–38 as fire turns fuel to ash, knowledge turns action's residue to
ash — nothing purifies like knowledge.
**Lede** — Krishna breaks the frame: he did not learn this teaching — he authored it,
and he has descended before, whenever the holding fails.
**Sections** — (1) "A lineage and a loss" — the recovery story; (2) "The descent" — the
avatāra doctrine in two verses; (3) "The contested verse" — 4.13 stated plainly with its
two futures (the classical reading: strands-and-actions as criteria; the plain reading
that will indict the poem in Part 3 — flag both, resolve neither); (4) "How knowledge
arrives" — 4.34's humility; (5) "Fire" — 4.37–38.
**Terms defined** — avatāra, māyā.
**Takeaways**
- The chapter stages its own recovery: a lineage, a loss, a retelling.
- Whenever right order fades, the divine descends to restore it — the avatāra doctrine.
- The four varnas are tied to strands and actions — the most contested verse in the
  poem, read as criteria by some and as decree by others.
- Knowledge burns action's residue like fire turning fuel to ash.
**Bridge-in** — From 12: chapter 3 ended with desire above the watchtower; chapter 4
opens with a claim of authority older than the war.
**Handoff to 14** — Chapter 5 referees the apparent dispute between the paths of
renunciation and action.
**Sources** — FS-TEXT, FS-LENSES (for the 4.13 readings), FS-ACAD.

### 14-ch05.html — Chapter 5 — Renounce or Act

**Verses** — 5.2, 5.8, 5.9, 5.18, 5.29.
**Beats** — 5.2 both renunciation and disciplined action lead to the highest, but action
is better; 5.8–9 the sage says "I do nothing at all" while seeing, hearing, touching —
the senses' report; 5.18 the same self in the learned brahmin, the cow, the elephant,
the dog, the outcaste; 5.29 knowing me as the sacrifice's enjoyer, the worlds' lord, the
beings' friend — the state of peace.
**Lede** — Chapter 5 opens as a courtroom: renounce the world or act in it — and the
verdict is that the two descriptions fit one actor.
**Sections** — (1) "The referee verse" — 5.2 settles and defers; (2) "I do nothing" —
the sage's perception, not idleness; (3) "The leveling gaze" — 5.18's catalog and its
two futures (Gandhi's charter, Part 3; the metaphysics-is-not-sociology objection,
Part 4 — flagged, not argued); (4) "The friend" — 5.29's three titles.
**Takeaways**
- Both paths reach the goal; disciplined action is the surer road.
- The sage's "I do nothing" is a way of seeing, not a way of sitting still.
- The same self stands in scholar, cow, elephant, dog, and outcaste — the verse Gandhi
  will build on and Ambedkar will cross-examine.
- The chapter closes with Krishna's self-introduction: enjoyer, lord, friend.
**Bridge-in** — From 13: chapter 4 ended in knowledge's fire; chapter 5 asks whether
that fire requires leaving the world.
**Handoff to 15** — Chapter 6 turns from argument to practice: how to sit, where, how
long.
**Sources** — FS-TEXT, FS-MOD (5.18's later readers).

### 15-ch06.html — Chapter 6 — The Meditation Manual

**Verses** — 6.5, 6.16, 6.17, 6.19, 6.34, 6.35, 6.47.
**Beats** — 6.5 lift yourself by yourself — the self is friend and enemy of the self;
6.16–17 yoga is not for one who eats or sleeps too much, or too little — moderation;
6.19 the lamp in a windless place; 6.34 Arjuna objects — the mind is restless,
turbulent, as hard to hold as wind; 6.35 the reply — practice and dispassion; 6.47 the
best yogin is the one who worships me with faith.
**Lede** — Chapter 6 is the poem's manual: posture, diet, sleep — and the restless mind
that Arjuna says cannot be held.
**Sections** — (1) "Lift yourself" — the self-relation at the base of practice; (2) "The
anti-extreme rule" — 6.16–17 against both indulgence and mortification; (3) "The lamp"
— 6.19's image; (4) "The realist's objection" — Arjuna's wind; (5) "The answer is
method" — practice plus dispassion, and the quiet promotion of devotion at 6.47.
**Takeaways**
- The self is its own friend and its own enemy — practice is self-directed.
- The manual is anti-extreme: yoga fails on too much food or sleep, or too little.
- Arjuna's realism about the restless mind is answered by method: repetition plus
  dispassion.
- The chapter's last verse quietly ranks the devotee above the adept — the devotional
  turn begins.
**Bridge-in** — From 14: chapter 5 ended in friendship; chapter 6 hands the reader a
practice.
**Handoff to 16** — Chapters 1–6 close; the second hexad opens with God explaining
himself.
**Sources** — FS-TEXT.

### 16-ch07.html — Chapter 7 — The Two Natures of God

**Verses** — 7.5, 7.14, 7.16, 7.19, 7.21, 7.22.
**Beats** — 7.5 the two natures — the lower eightfold (earth, water, fire, wind, ether,
mind, discernment, egoity) and the higher, the living thread that carries beings;
7.14 the divine power of the strands is hard to cross — those who take refuge cross it;
7.16 four kinds of devotees come — the distressed, the curious, the wealth-seeker, the
knower; 7.19 after many births, the great soul arrives: all is the divine one; 7.21–22
whatever form a devotee worships with faith, that faith I steady.
**Lede** — The second hexad opens with an inventory: God's lower nature is the world's
matter, and it is a maze only refuge exits.
**Sections** — (1) "Eightfold and higher" — the two prakṛtis; (2) "The maze" — 7.14's
refuge; (3) "Four kinds of seeker" — 7.16's typology, none despised; (4) "The rare
arrival" — 7.19; (5) "Steadying every faith" — 7.21–22, the pluralist moment.
**Terms defined** — īśvara.
**Takeaways**
- God's nature is twofold: an eightfold matter, and a living thread that carries
  beings.
- The strands' maze is crossed by refuge, not analysis.
- Four motivations bring seekers — distress, curiosity, wealth, knowledge — and none is
  turned away.
- Worship aimed elsewhere is steadied by the one worshipped: the poem's pluralist
  moment.
**Bridge-in** — From 15: the manual ended with devotion ranked highest; chapter 7
explains what devotion is aimed at.
**Handoff to 17** — Chapter 8 asks the exit question: how one leaves the world at death.
**Sources** — FS-TEXT.

### 17-ch08.html — Chapter 8 — The Last Thought

**Verses** — 8.3, 8.5, 8.6, 8.7, 8.22.
**Beats** — 8.3 the definitions begin — brahman the imperishable, the syllable, the
offering; 8.5 at the end, remembering me, one attains my being; 8.6 whatever being one
leaves the body remembering, to that one goes; 8.7 therefore remember me and fight;
8.22 the supreme person, reached by devotion that does not covet — in whom beings rest.
**Lede** — Chapter 8 takes the method to its edge: the state of mind at the moment of
death decides where the self goes next.
**Sections** — (1) "A chapter of definitions" — the vocabulary review; (2) "The last
thought is the door" — 8.5–6; (3) "The whole teaching in four words" — remember me and
fight; (4) "The resting place" — 8.22.
**Terms defined** — puruṣa.
**Takeaways**
- The last thought is the door: what you hold at leaving is where you go.
- The chapter compresses the teaching into one sentence: remember me, and fight.
- Its vocabulary — puruṣa, brahman — is borrowed from older cosmologies and re-aimed at
  Krishna.
- What begins as deathbed mechanics ends in intimacy: the one in whom all things rest.
**Bridge-in** — From 16: chapter 7 ended at the maze's exit; chapter 8 asks what the
exit leads to.
**Handoff to 18** — Chapter 9 calls its own content the royal secret — and opens the
doors wide.
**Sources** — FS-TEXT.

### 18-ch09.html — Chapter 9 — The Royal Secret

**Verses** — 9.4, 9.22, 9.26, 9.29, 9.30, 9.31, 9.32, 9.34.
**Beats** — 9.4 all beings sit in me; I do not sit in them — support without
containment; 9.22 those who worship me, thinking of no other — I carry what they lack;
9.26 the leaf, the flower, the water offered with love — I accept it; 9.29 the same to
all beings, neither favoring nor hating; yet those who worship me are in me and I in
them; 9.30–31 even a man of terrible conduct who worships with single devotion must be
counted righteous — quickly he becomes righteous; 9.32 women, merchants, laborers — even
they take the highest way; how much more the brahmin and the royal seer; 9.34 fix your
mind on me, worship me, bow to me — you will come to me.
**Lede** — The royal secret is radical inclusion: any offering from anyone who loves is
accepted — even, the poem says, from people of terrible conduct.
**Sections** — (1) "The paradox of support" — 9.4; (2) "The democratized offering" —
9.26 against ritual scale; (3) "The scandal of grace" — 9.30–31 read slowly and
honestly; (4) "The open door and its argument" — 9.32 quoted plainly, both its futures
flagged (the inclusion reading and the concession reading — Part 4 handles the fight);
(5) "The summons" — 9.34.
**Terms defined** — bhakti.
**Takeaways**
- Beings dwell in God, who does not dwell in them: support without containment.
- A leaf and water, offered in love, suffice — ritual scale replaced by intent.
- Even terrible conduct plus devotion is a path: read closely, it is grace.
- The door opens to women, merchants, and laborers — the verse later activists will
  wield, and argue over.
**Bridge-in** — From 17: the last-thought chapter ended in the resting one; chapter 9
reveals what that one is like.
**Handoff to 19** — Chapter 10 lets the divine speak in the first person of abundance.
**Sources** — FS-TEXT, FS-MOD (9.32's later readers).

### 19-ch10.html — Chapter 10 — The Catalogue of Splendor

**Verses** — 10.8, 10.20, 10.41.
**Beats** — 10.8 I am the source of all; the wise who delight in this worship me;
10.20 I am the self seated in the hearts of all beings — the beginning, middle, and end
of beings; 10.41 whatever being has splendor — know it as a fragment of my abundance.
**Lede** — Chapter 10 is a list poem: the divine catalogs itself in images — and every
excellence anywhere is declared a splinter of one abundance.
**Sections** — (1) "A god who lists" — the chapter's grammar is first-person;
(2) "The self in every heart" — 10.20 returning the poem's earlier teaching with a
divine face; (3) "The rule of splinters" — 10.41; (4) "Why a catalog" — abundance
shown, not argued (and note: the full catalog is long; this book shows the spine, not
every entry — say so).
**Takeaways**
- The chapter's grammar is first-person: the divine lists itself in images, not
  arguments.
- The self in every heart — the earlier teaching returns wearing a divine face.
- Whatever has splendor anywhere is a splinter of one abundance.
**Bridge-in** — From 18: the secret was opened to everyone; chapter 10 answers "opened
to what" — an inexhaustible inventory.
**Handoff to 20** — Arjuna asks to see it, and chapter 11 grants the request the reader
should dread.
**Sources** — FS-TEXT.

### 20-ch11.html — Chapter 11 — The Vision

**Verses** — 11.12, 11.28, 11.32, 11.33, 11.53, 11.54, 11.55.
**Beats** — 11.12 if the light of a thousand suns rose at once — that splendor; 11.28
as rivers rush to the sea, so these warriors rush into your mouths; 11.32 time grown
mature, the world-destroyer — the verse a physicist will quote at a bomb test (flag:
Part 3 tells that story); 11.33 stand, win — I have already slain them; you be my
instrument; 11.53 not by the Vedas, not by effort — by undivided devotion is this seen;
11.54 devotion's price; 11.55 the one who does my work, holds me supreme, without
enmity — comes to me.
**Lede** — Arjuna asks for the face behind the voice — and sees mouths eating the
world: time, the destroyer, grown mature.
**Sections** — (1) "The request granted" — what Arjuna asked and what he gets;
(2) "Rivers into mouths" — the vision's terrible form; (3) "Time" — 11.32 and its long
afterlife (foreshadow Oppenheimer in one sentence, no details — Part 3); (4) "The
instrument" — 11.33's nimitta, the verse every ethics-of-command argument returns to
(Part 4); (5) "How the form is seen" — 11.53–55.
**Terms defined** — nimitta.
**Takeaways**
- The friend driving the chariot shows the face that ends worlds.
- You be my instrument: the verse that will comfort soldiers and indict generals — the
  poem does not choose.
- The form is seen by devotion alone — not by study, not by effort.
- After the terror, the condition of return: do the work, hold me supreme, harbor no
  enemy.
**Bridge-in** — From 19: the catalog ended in splinters of splendor; chapter 11
assembles them into one unbearable face.
**Handoff to 21** — The vision ended in a condition; chapter 12 asks which is better —
the face seen or the formless loved.
**Sources** — FS-TEXT, FS-GLOBAL (the 11.32 afterlife).

### 21-ch12.html — Chapter 12 — The Beloved Devotee

**Verses** — 12.2, 12.5, 12.13, 12.14, 12.15, 12.16.
**Beats** — 12.2 those who fix their minds on me, worshipping with faith, I hold the
best disciplined; 12.5 the formless is harder for the embodied to reach; 12.13–16 the
beloved's portrait — friendly, compassionate, without possession and pride, equal in
pleasure and pain, patient, content, steady, without disturbance and exultation, sorrow
and fear; free of craving, purity, skill, indifference.
**Lede** — The shortest chapter of the second hexad is a love poem with a question
inside: worship the face, or the formlessness?
**Sections** — (1) "The question answered by preference" — 12.2's one-vote margin;
(2) "The concession" — 12.5's honest cost; (3) "The portrait" — 12.13–16 as ethics
delivered as a person-description; connect back to the settled one of chapter 2.
**Takeaways**
- The personal is called the better and the easier — one reading of "best".
- The formless path is conceded to be agony for embodied beings.
- The beloved is described by how he treats you — theology as a person-list.
**Bridge-in** — From 20: the vision's terror closed into a condition; chapter 12 sets
devotion's furniture.
**Handoff to 22** — The second hexad ends; the third opens with the poem's most patient
distinction — the field and its knower.
**Sources** — FS-TEXT.

### 22-ch13.html — Chapter 13 — Field and Knower

**Verses** — 13.1, 13.2, 13.7, 13.8, 13.19, 13.20, 13.23, 13.27, 13.28.
**Beats** — 13.1 this body is the field; the one who knows it is the field-knower;
13.2 know me as the field-knower in all fields; 13.7–8 the field's disciplines —
humility, honesty, non-violence, and the marks of knowledge; 13.19 nature and the
person are both beginningless; 13.20 the cause of effect and instrument; 13.23 the
witness, the permitter, seated in the field; 13.27 whatever is born, moving or still,
is born of field-and-knower joining; 13.28 seeing the same lord in all — the equal
sight.
**Lede** — The third hexad opens with the poem's calmest tool: a distinction — you are
not the field you are watching; you are the watching.
**Sections** — (1) "The pair defined" — field, knower; (2) "The divine claim" — 13.2;
(3) "The field's disciplines" — knowledge is conduct before content; (4) "The witness
seated in the field" — 13.23; (5) "The equal sight" — 13.27–28.
**Terms defined** — kṣetra, kṣetrajña.
**SVG spec** — Field and knower: a large rounded region labeled "the field — body,
senses, mind"; inside it, a small luminous point labeled "the knower — the witness";
above the region, an arc spanning outward labeled "the knower in all fields". Title:
"The field and its knower". One structure only: containment and witness.
**Takeaways**
- The body is the field; the one who knows it is the field-knower.
- Krishna claims to be the knower in every field — the distinction turns theological.
- The field's disciplines are conduct — humility, honesty, non-violence — before they
  are content.
- Seeing the same lord in all beings is the sight this chapter trains.
**Bridge-in** — From 21: the beloved was described by conduct; chapter 13 describes the
one who loves — as a knower in a field.
**Handoff to 23** — The field has strands; chapter 14 names them and counts them three.
**Sources** — FS-TEXT.

### 23-ch14.html — Chapter 14 — The Three Strands

**Verses** — 14.5, 14.6, 14.7, 14.8, 14.19, 14.26.
**Beats** — 14.5 the three strands born of nature bind the embodied; 14.6 sattva —
luminous, healthy, binds by attachment to happiness and knowledge; 14.7 rajas —
passion, born of craving, binds by action; 14.8 tamas — darkness, born of confusion,
binds by sloth, sleep, error; 14.19 when the seer sees no doer but the strands, they
attain my being; 14.26 the tree of the strands is escaped by devotion.
**Lede** — The field runs on three strands — light, drive, and dark — and each binds you
by the thing you enjoy most.
**Sections** — (1) "Three strands, three snares" — each strand binds; even luminous
sattva is a bond; (2) "The exit through seeing" — 14.19; (3) "The exit through
devotion" — 14.26.
**Terms defined** — sattva, rajas, tamas.
**SVG spec** — Guṇa triangle: vertices labeled sattva (binds through pleasantness),
rajas (binds through craving), tamas (binds through numbness); the containing outline
labeled prakṛti. Title: "Three strands, three bindings". One structure: containment.
**Takeaways**
- The strands are the field's machinery: sattva, rajas, tamas.
- Every strand is still a strand — even luminous clarity is a bond.
- Seeing no doer but the strands, the seer stands free of the doer-claim.
- Devotion is the other exit: the strand-machine cannot bind the devotee.
**Bridge-in** — From 22: the field and its knower were distinguished; now the field is
dissected.
**Handoff to 24** — Chapter 15 grows the strands into a tree — upside-down.
**Sources** — FS-TEXT.

### 24-ch15.html — Chapter 15 — The Upside-Down Tree

**Verses** — 15.1, 15.2, 15.3, 15.4, 15.6, 15.15, 15.16, 15.17, 15.18.
**Beats** — 15.1 the banyan with roots above, branches below, its leaves the hymns —
who knows it knows the Vedas; 15.2 the branches spread, fed by the strands; the sprouts
are the sense-objects; 15.3 its true form is not seen here — no beginning, no end — cut
it with the axe of detachment; 15.4 the cut path: seek that seat from which, gone, none
return; 15.6 neither sun nor moon nor fire lights it; 15.15 seated in hearts — from me
memory, knowledge, and their loss; I am the knowable of the Vedas; 15.16 two persons —
the perishable and the imperishable; 15.17 the highest, the lord who enters the three
worlds; 15.18 I am beyond the perishable, the best — in the world and the Veda.
**Lede** — The poem's strangest image: a banyan rooted in heaven, fruiting as your
experience — and the only tool that cuts it is detachment's axe.
**Sections** — (1) "The tree described" — roots above, branches below; (2) "The axe" —
not knowledge alone; (3) "The seat beyond the lights" — 15.4, 15.6; (4) "Three persons
stacked" — 15.16–18: perishable beings, the imperishable witness, the highest.
**Terms defined** — aśvattha.
**SVG spec** — Inverted banyan: a root cluster at the top labeled "the primal root";
branches descending and spreading, labeled "fed by the strands"; buds at branch-tips
labeled "sense-objects"; an axe glyph on the trunk labeled "detachment"; beyond the
tree, a plain circle labeled "the seat no lights illumine". Title: "The upside-down
tree". One structure: inversion.
**Takeaways**
- The banyan is the cycle of rebirth as vegetation: rooted above, fruiting as
  experience below.
- The tree's cut is not knowledge alone — the axe is detachment.
- The destination is a seat that no sun, moon, or fire lights.
- Three persons are stacked: perishable beings, the imperishable witness, the highest —
  and Krishna names himself the last.
**Bridge-in** — From 23: the strands were counted; now they grow into a tree.
**Handoff to 25** — Chapter 16 clears ground: two lists, two estates, no middle.
**Sources** — FS-TEXT.

### 25-ch16.html — Chapter 16 — Two Estates

**Verses** — 16.1, 16.2, 16.3, 16.4, 16.8, 16.13, 16.14, 16.21, 16.23, 16.24.
**Beats** — 16.1–3 the divine estate — fearlessness, purity of being, self-restraint,
sacrifice, study, harmlessness, truth, non-anger, renunciation, tranquility,
compassion, gentleness; 16.4 the other estate — pride, arrogance, conceit, anger,
harshness, ignorance; 16.8 the demonic creed quoted: the universe is without truth,
without basis, without a lord, born of intercourse, nothing but appetite; 16.13–14 the
possessive self-talk: I gained this, I will gain that, this wealth is mine, my enemies
are slain; 16.21 three gates of hell — craving, anger, greed; 16.23 self-will above
scripture leads nowhere; 16.24 let scripture be your rule for what to do and what not
to do.
**Lede** — Chapter 16 is not gray: two lists, two estates — and a rule of thumb about
which one you feed.
**Sections** — (1) "The divine list" — social before mystical; (2) "The other estate" —
quoted, not described; (3) "The possessive tell" — 16.13–14 in first person; (4) "Three
gates" — 16.21; (5) "Scripture as umpire" — 16.24, the verse a later reader will
cross-examine (flag Ambedkar, Part 3).
**Takeaways**
- The divine list is social before it is mystical: fearlessness, truth, non-harm,
  compassion.
- The other estate is quoted in its own voice: appetite without ground.
- The possessive is the tell — "mine, mine" — the self-talk of ruin.
- Craving, anger, greed: three gates of hell; scripture closes the chapter as umpire —
  and becomes evidence in a later trial.
**Bridge-in** — From 24: the tree was cut with detachment's axe; chapter 16 names what
is cut away and what remains.
**Handoff to 26** — Chapter 17 re-admits gray: faith has three flavors, and so does
dinner.
**Sources** — FS-TEXT, FS-MOD (16.24's later reader).

### 26-ch17.html — Chapter 17 — Faith, Food, Speech

**Verses** — 17.3, 17.8, 17.9, 17.10, 17.15, 17.23.
**Beats** — 17.3 one's faith is each one's own — one becomes as one's faith is;
17.8–10 the foods: juicy, mild, sustaining (sattva); bitter, sour, salty, scorching
(rajas); stale, tasteless, rotten (tamas); 17.15 speech that is non-harming, true,
pleasant, and beneficial; 17.23 the threefold syllable — the marking of offering, gift,
and austerity.
**Lede** — Gray returns: your faith takes one of three tints, and so does your dinner —
the chapter sorts by strand, without contempt.
**Sections** — (1) "You become what you trust" — 17.3 as the chapter's law; (2) "The
taxonomy" — food as the readable example (show all three verses); (3) "The speech rule"
— 17.15, the book's most quotable ethics; (4) "The syllable that seals" — 17.23.
**Takeaways**
- One becomes one's faith: trust is self-shaping.
- Food, worship, austerity, gift, and speech are each sorted into three strands — the
  chapter is a taxonomy.
- The speech rule — true, pleasant, beneficial, non-harming — is the poem's portable
  ethics.
- The threefold syllable seals every act as an offering.
**Bridge-in** — From 25: the two estates had no middle; chapter 17 supplies the
gradients between them.
**Handoff to 27** — The final chapter referees everything — and its last verses are the
ones everyone quotes.
**Sources** — FS-TEXT.

### 27-ch18.html — Chapter 18 — The Closing Settlement

**Verses** — 18.1, 18.2, 18.13, 18.14, 18.15, 18.41, 18.47, 18.61, 18.65, 18.66,
18.73, 18.78.
**Beats** — 18.1–2 the definitional pair — renunciation and the relinquishing of
fruits; 18.13–15 the five factors of every act — the body, the actor, the instruments,
the motion, and the fifth, the divine; plus the doer's claim; 18.41 each order's works
named — the four varnas' works; 18.47 better your own imperfect path than another's
done well (echo of chapter 3); 18.61 the lord seated in all hearts turns all beings as
if mounted on a machine; 18.65 think of me, be devoted, worship me — you will come to
me; 18.66 the final verse: relinquishing all holdings, take refuge in me alone; I will
free you — do not grieve; 18.73 Arjuna's answer: my delusion is destroyed, I stand,
memory restored; I will do as you say; 18.78 the reporter's exit: where Krishna and
Arjuna are, there is splendor, victory, wealth, and unwavering order.
**Lede** — The last chapter is a settlement conference: every disputed word returns once
more, and Arjuna ends it with the shortest sentence in the poem — "I will do as you
say."
**Sections** — (1) "Two releases defined" — the pair; (2) "The five factors" — the
committee theory of acts; (3) "The orders and their works" — 18.41 stated plainly
(flag: Part 3's trial and Part 4's fork); (4) "The machine" — 18.61 and the freedom
question (flag Part 4); (5) "The refuge" — 18.66, the verse schools were built on;
(6) "The yes" — 18.73; (7) "The reporter's exit" — 18.78 and the frame closing.
**Terms defined** — saṃnyāsa, tyāga, carama śloka.
**Takeaways**
- The chapter distinguishes the two releases: renouncing the act, and releasing its
  fruits — the Gita endorses the second.
- Every act has five factors — the doer's "I did it" is one voice in a committee.
- The final verse hands the reader refuge — the line great schools were built on.
- Arjuna's answer is not agreement but restored willingness: "I will do as you say."
- The frame's last word: where those two are, there is splendor and unwavering order.
**Bridge-in** — From 26: the taxonomies sorted faith, food, and speech; chapter 18
gathers every open question into one settlement.
**Handoff to 28** — The poem is over; the reading has not begun — one text is about to
become many Gitas.
**Sources** — FS-TEXT, FS-LENSES (18.66's afterlife).

## Part 3 — The Lenses

Lens pages follow a fixed inner shape: bridge from the walk → who the reader is (dates,
place, prov'd) → what they did with the text (the lens, attributed) → the verse shown,
read through the lens → the cost or critique of the lens, attributed → handoff. No lens
is ranked; each page ends by giving the next lens the floor.

### 28-many-gitas.html — How One Poem Became Many Gitas

**Purpose** — The reception toolkit: why there is no single Gita, what a commentary is,
and the rules of Part 3.
**Lede** — There is no single Gita — there is the Gita plus centuries of readers who
built systems on it; this chapter is the toolkit for hearing them.
**Sections** — (1) "A text plus its readers" — the afterlife in commentaries (earliest
surviving complete commentary, prov FS-LENSES; the tradition's chronological spread);
(2) "Views" — define darśana (a view or sightline; the classical schools as angles, not
systems); (3) "The running commentary" — define bhāṣya (a genre with rules: every verse
accounted for, contradictions reconciled — reading as jurisprudence); (4) "The lineage"
— define paramparā (the teacher-chain that transmits reading as practice);
(5) "The rules of this part" — each lens in its own voice; the book stays silent; no
lens is neutral, including the ones that claim to be.
**Terms defined** — darśana, bhāṣya, paramparā.
**Takeaways**
- Darśana means view: each classical school is a sightline on one shared text.
- A commentary is a discipline — every verse accounted for, contradictions reconciled.
- A lineage transmits reading as practice, not information.
- No lens in the coming chapters is neutral, including the ones that claim to be.
**Bridge-in** — From 27: Arjuna said yes, the armies moved, the poem froze — and its
readers began.
**Handoff to 29** — The first lens is the oldest famous one: the world as appearance.
**Sources** — FS-LENSES.

### 29-shankara.html — Shankara's Lens: The World as Appearance

**Verse** — 2.47 (reprise).
**Purpose** — Advaita: one reality, the world as appearance, and 2.47 as a ladder to be
climbed past.
**Lede** — For Shankara the poem's deepest teaching is that one non-dual reality is all
there is — and its most famous verse is a rung, not a roof.
**Sections** — (1) "The wanderer" — the man, the era, the travels, the debates (dates
prov FS-LENSES; treat hagiography honestly — the life is tradition, the texts are
ours); (2) "Not two" — define advaita; brahman alone real, the world appearance, the
self brahman; (3) "His verse" — 2.47 read as provisional: detachment disciplines the
mind until knowledge dissolves the actor; (4) "The cost" — if the world is appearance,
suffering can look like scenery; his critics said so, and his answer was two levels of
truth (attributed, not adjudicated).
**Terms defined** — advaita.
**Takeaways**
- Advaita means not-two: one reality appearing as many.
- On this lens, detachment is a rung: it disciplines the mind until knowledge dissolves
  the separate actor.
- The cost is real: the world's suffering can read as stage scenery — his critics said
  so.
**Bridge-in** — From 28: the toolkit is in hand; the first sightline is the oldest
famous one.
**Handoff to 30** — Two southerners will refuse the dissolution: souls are real, and
so is the world.
**Sources** — FS-LENSES.

### 30-ramanuja-madhva.html — Ramanuja and Madhva: Souls That Never Merge

**Verse** — 18.66 (reprise).
**Purpose** — The two realist refusals: qualified non-dualism and dualism; 18.66 as the
refuge charter.
**Lede** — Ramanuja and Madhva both refuse the ladder's top rung: souls are real,
matter is real — and the final verse becomes the charter of surrender.
**Sections** — (1) "The temple philosopher" — Ramanuja (dates prov FS-LENSES); define
viśiṣṭādvaita (the world as God's body: real, dependent, never dissolved);
(2) "The refuge" — define prapatti and śaraṇāgati (self-surrender; 18.66 as its
charter — refuge for those who cannot perfect themselves); (3) "The hard dualist" —
Madhva (dates prov); define dvaita (the five eternal distinctions, including that souls
never merge — and are graded, a doctrine some later readers reject); (4) "Why these
lenses matter" — real selves ground real communities: temple, feast, lineage.
**Terms defined** — viśiṣṭādvaita, dvaita, prapatti, śaraṇāgati.
**Takeaways**
- The world is God's body: real, dependent, never dissolved — the qualified
  non-dualist's answer.
- Dualism proper: five eternal distinctions — the self and God never merge, in anyone.
- The final verse becomes the charter of surrender: refuge, not achievement.
- Real souls anchor real communities — the theologies that ground temple and lineage.
**Bridge-in** — From 29: the ladder dissolved its climber; the next two lenses refuse
the dissolution.
**Handoff to 31** — The classical age produced more lenses than the famous three.
**Sources** — FS-LENSES.

### 31-other-classical.html — The Other Classical Lenses

**Verse** — 6.47 (reprise).
**Purpose** — The between-schools, the aesthetician, and the Marathi saint: the
classical crowd beyond the big three.
**Lede** — The famous three had rivals: between-and-both schools, a Kashmiri
aesthetician, and a Marathi saint who made the Gita sing to farmers.
**Sections** — (1) "Between and both" — difference-and-non-difference schools (Bhāskara,
Nimbarka, Vallabha's pure-grace reading; one paragraph each, prov FS-LENSES);
(2) "The aesthetician" — Abhinavagupta's Kashmir: the Gita read as literature, its
effect counted (his summary work, prov FS-LENSES); (3) "The saint" — the Marathi
retelling around 1290 (prov FS-LENSES): the Gita for the village, God as mother and
friend; (4) "The contest verse" — 6.47: every lens claims the best-disciplined crown.
**Takeaways**
- Between non-dualism and dualism sat whole families of both-and schools.
- One Kashmiri reader counted the poem's beauty, not only its doctrine.
- A Marathi saint took the poem to people who could not read Sanskrit.
- Every lens wants the crown of the chapter that ranks the devotee highest.
**Bridge-in** — From 30: two refusals of the ladder; here is the rest of the classical
crowd.
**Handoff to 32** — The moderns arrive with a question the classics never asked: what
does the Gita do in history?
**Sources** — FS-LENSES.

### 32-action-moderns.html — The Activists: Vivekananda, Tilak, Aurobindo

**Verse** — 5.2 (reprise).
**Purpose** — The three action-moderns: practical Vedanta, the prison treatise, and the
evolutionary mystic.
**Lede** — A monk, a prisoner, and a revolutionary mystic reread the Gita as a manual
for acting in history — not escaping it.
**Sections** — (1) "The monk" — Vivekananda (dates prov FS-MOD; the 1893 Chicago
address, prov): strength, work as worship, the Gita as practical; (2) "The prisoner" —
Tilak (dates prov; the Mandalay years, prov): the treatise written in prison arguing
that the poem's core is action — his proof-text, 5.2; (3) "The mystic of evolution" —
Aurobindo (dates prov; revolutionary turned Pondicherry recluse): the divine laboring
in history, the essays on the Gita (prov); (4) "What they share" — all read the poem
against world-denial, under empire; all made it a political instrument (state plainly).
**Takeaways**
- The moderns' shared move: the Gita calls you to act in the world, not to leave it.
- The prisoner's case: both paths lead, but action is the better — his proof-text from
  chapter 5.
- The evolutionary adds an arc: the divine works through history, not around it.
- Each reading was also a political instrument — against empire, and sometimes against
  rivals at home.
**Bridge-in** — From 31: the classical lenses parsed being; the moderns ask about
doing — under colonial rule.
**Handoff to 33** — The most famous action-reader made the poem itself into
nonviolence.
**Sources** — FS-MOD.

### 33-gandhi.html — Gandhi's Gita: The Battle Within

**Verse** — 2.47 (reprise).
**Purpose** — The allegorical reading: the war within, anāsakti, the practice — and the
honest cost of overruling the frame.
**Lede** — Gandhi read the battlefield as the human breast: the armies are impulses, the
war is daily — while admitting the poem is, on its face, about a war.
**Sections** — (1) "The daily reader" — the decades of practice, the translation and
discourses (dates prov FS-MOD; his names for the book — mother, spiritual reference book);
(2) "The allegory" — the body-field, the base impulses as the opposing army, the soul
in crisis; his coinage for the teaching: non-attachment; (3) "His verse" — 2.47 as the
engine of nonviolent resistance: act, release the fruits; (4) "The honest problem" —
the text stages a real war and a command to fight; Gandhi's answer: the Gita teaches by
analogy, and killing cannot be the way to nonviolence; his critics: he simply refuses
the frame (both stated, neither crowned; Part 4 returns).
**Takeaways**
- Gandhi's Gita is interior: the war is the self's civil war, fought daily.
- The act-without-fruits verse became the engine of nonviolent resistance.
- He called the book his spiritual reference book and read it as a mother reads — practice
  before theory.
- The allegory's cost: it must overrule the poem's own frame — Gandhi accepted the
  cost.
**Bridge-in** — From 32: the action-moderns made the Gita historical; Gandhi made it
interior without losing the action.
**Handoff to 34** — The fiercest reader of the era read the same poem and saw the
machine of caste.
**Sources** — FS-MOD.

### 34-ambedkar.html — Ambedkar's Indictment

**Verse** — 4.13 (reprise).
**Purpose** — The counter-reading: the Gita as the philosophical defense of the social
order — stated at full strength, with the counter-case, unranked.
**Lede** — Ambedkar read the same poem and saw the machine: a divine decree for the
fourfold order, and a doctrine that tells the oppressed their station is deserved.
**Sections** — (1) "The jurist" — the man, the era, the quarrel with Gandhi over caste
and scripture (dates prov FS-MOD; the published exchange, prov); (2) "His Gita" — the
riddles he left: the Gita as philosophical defense of the fourfold order and of the
warrior's duty; Krishna as retrofitted teacher; (3) "The verse on trial" — 4.13 plain:
the four orders, created by me; the softening glosses (criteria of strands and actions)
versus the plain reading (decree); both attributed; (4) "His deeper charge" — karma as
the doctrine that tells the suffering their suffering is earned; (5) "The counter-case"
— readers who answer from within the poem: the criteria reading, the open-door verse of
chapter 9, the poem's own tensions. The book presents both sides and decides nothing.
**Takeaways**
- The charge: the Gita is the theological defense of the social order — the four-varna
  verse read plainly.
- The deeper charge: karma tells the oppressed their station is deserved.
- The counter-reading exists inside the text itself: strands-and-actions as criteria,
  not birth — the ambiguity is the battlefield.
- The quarrel with Gandhi was over scripture's authority, not just its meaning — this
  book shows both and decides nothing.
**Bridge-in** — From 33: the interior war met its prosecutor: the reader for whom the
social frame was the whole point.
**Handoff to 35** — A mythologist walks the poem out of the courtroom and into the folk
pantheon.
**Sources** — FS-MOD.

### 35-pattanaik.html — Pattanaik's My Gita — and Its Critics

**Verse** — 13.2 (reprise).
**Purpose** — The popular present: thematic retelling, subjectivity as method — and the
critique of both.
**Lede** — In our own decade a mythologist rearranged the Gita by theme instead of
chapter, called it My Gita, and told readers the poem makes meaning rather than gives
messages — critics called it shallow; both are now part of the Gita.
**Sections** — (1) "The mythologist" — who he is, what he wrote, the year (prov
FS-PATT); the arrangement: thematic, first-person, illustrated; (2) "His Gita" —
knowledge as subjective making; the field-knower verse as his frame; Sanskrit glossed
warmly, folklore foregrounded; (3) "The critics" — the published reviews that charged
cherry-picking and flattened categories (prov FS-PATT; quote or closely paraphrase one);
(4) "The pattern" — every era remakes the Gita; the present's remake is evidence, not
anomaly (connect to Part 4).
**Takeaways**
- The retelling reads by theme, not chapter — an arrangement that says arrangement
  itself is interpretation.
- His field-knower verse: knowledge is subjective making — the poem as mirror.
- The critics' charge: warmth is not rigor — categories flattened, hard verses
  softened.
- Every era's Gita is somebody's Gita — the present's is no exception.
**Bridge-in** — From 34: the indictment came from the courthouse; the pop retelling
comes from the marketplace — same poem, new room.
**Handoff to 36** — The poem has been leaving India for over two centuries — see what
it wore abroad.
**Sources** — FS-PATT, FS-MOD.

### 36-global-gita.html — The Gita Goes Global

**Verse** — 11.32 (reprise).
**Purpose** — The world travels: first translation, New England, the Theosophists, the
physicist and the bomb, the mass-distributed edition and its controversies.
**Lede** — Since the first English translation, the Gita has traveled light: Emerson
pocketed it, Thoreau read it by a pond, and the physicist who built the bomb quoted it
at the flash.
**Sections** — (1) "The first crossing" — the 1785 translation by the East India Company
man (prov FS-GLOBAL; the patron who funded it); empire's fingerprints on the gift;
(2) "New England" — Emerson and Thoreau (prov); the Theosophists; the monk's 1893
Chicago stage (cross-reference page 32); (3) "The flash" — the physicist's 1945
quotation of the time-verse (prov; the interview years later; the 11.32 figure carries
the verse); (4) "The mass era" — the edition that became the most distributed Gita in
English (prov; its controversies — edited translations, a preface that warns the reader
— state both facts, attribute both).
**Takeaways**
- The first English Gita was an empire's gift — funded by a governor, translated by a
  company man.
- New England made it American: conscience over ritual.
- The time-verse outlived its chapter: quoted at the first bomb test, remembered at the
  hearing after.
- The most distributed English edition is also the most contested — an "as it is" with
  edits.
**Bridge-in** — From 35: the marketplace lens showed the Gita as everybody's own; the
travels prove it — with suitcases.
**Handoff to 37** — Alongside readers came scholars: dating the poem, cutting its
layers, doubting its unity.
**Sources** — FS-GLOBAL.

### 37-scholars-gita.html — The Scholars' Gita: Dates, Layers, Methods

**Verse** — 6.17 (reprise).
**Purpose** — The academic lens: the date range, the layer theories, the Buddhist
conversation — and what survives the doubt.
**Lede** — Strip away the commentaries and the scholars hand you a colder Gita: a date
range measured in centuries, layers argued verse by verse, a Krishna grown divine by
redaction — and still one of the most disciplined poems ever built.
**Sections** — (1) "How old" — the range the handbooks give (prov FS-ACAD), why it is a
range (no autograph manuscripts; the epics grew); (2) "The layer theories" — the
reconstructed short original and its later growth (prov FS-ACAD; the evidence: sudden
escalations, repetitions, the commentators' reconciling labors); (3) "Arguing with the
Buddhists" — the borrowed nirvāṇa, the self-doctrine as counter-position (cross-ref
page 11); (4) "What survives" — 6.17 as the scholars' emblem: the moderate spine that
holds under any dating.
**Takeaways**
- The Gita's date is a range measured in centuries — the manuscripts are younger than
  the fame.
- Layer theories read the poem as a growing text: a core teaching, then theological
  amplification.
- Its vocabulary argues with Buddhist rivals — the self-doctrine as counter-position.
- Under the scalpel the poem keeps a spine: moderation, discipline, the examined act.
**Bridge-in** — From 36: the world took the poem at face value; the scholars took it
apart — and face value turns out to be a layer too.
**Handoff to 38** — Now the forks: the verses on which every lens you met actually
turns.
**Sources** — FS-ACAD.

## Part 4 — Your Reading

### 38-forks-1.html — The Forks I: Four Verses, Many Gitas

**Verses** — 2.47, 4.13, 9.32, 18.66 (all reprises, shown once each in the page's
order).
**Purpose** — The contested verses assembled: each shown again with two or three
attributed readings, side by side, no verdict.
**Lede** — Four verses carry the weight of every reading you have met — here they are
again, with the readers who fight over them in the same room.
**Sections** — (1) "The act and its fruits" — 2.47: the non-dualist's rung, the
prisoner's politics, the nonviolent resister's engine; what all three share: the
release of the claim on results; (2) "The decree and the criteria" — 4.13: the
classical criteria reading, the plain-decree reading, the indictment; the honest
statement that the tension with chapter 9's open door is inside the text; (3) "The open
door and its hinges" — 9.32: the inclusion reading, the concession reading; (4) "The
refuge" — 18.66: surrender's charter, knowledge's final verse, fearless action's call.
End with the method restated: the reader, not the book, holds the scale.
**Takeaways**
- The same verse honestly read supports devotion, knowledge, and action — the readers
  are the variable.
- The four-varna verse and the open-door verse pull opposite directions inside one
  poem — that tension is the Gita's live wire.
- The refuge verse means surrender to one school and clarity to another.
- The verdict was never this book's to assign.
**Bridge-in** — From 37: the scholars cut the layers; the reader must still walk them —
here are the four steepest forks.
**Handoff to 39** — Three questions the poem opens and never closes.
**Sources** — FS-LENSES, FS-MOD, FS-ACAD.

### 39-forks-2.html — The Forks II: The Questions That Never Close

**Verses** — 11.33, 18.61, 5.18 (reprises).
**Purpose** — The open questions: the instrument and violence; the machine and freedom;
the equal gaze and society.
**Lede** — Three questions the poem opens and never closes: can a good person be an
instrument of violence, does the machine-driver leave us free, and what does it mean to
see a scholar and a dog as the same?
**Sections** — (1) "The instrument" — 11.33: the plain frame's comfort to a soldier,
Gandhi's refusal, the historian's warning; the verse does not choose; (2) "The machine"
— 18.61: beings mounted and turned — read against the poem's own final counsel, that
knowledge having been taught, the choosing is yours (18.63, paraphrased and attributed
— the tension is structural, not accidental); (3) "The equal gaze" — 5.18: Gandhi's
equality of souls against the objection that metaphysics is not sociology; the question
left standing.
**Takeaways**
- The instrument verse has comforted soldiers and indicted generals — it does not
  choose.
- Beings are mounted on a machine, then addressed as free choosers — the tension is
  structural.
- The equal gaze was a charter to one reader and insufficient to another — seeing alike
  is not yet treating alike.
- Questions that survive centuries are not failures of reading; they are the engine.
**Bridge-in** — From 38: four verses showed the forks; three questions show why the
forks never close.
**Handoff to 40** — The loop closes: one walk through the whole, and the door out.
**Sources** — FS-LENSES, FS-MOD.

### 40-the-loop.html — The Loop: One Walk Through the Whole

**Verses** — none.
**Purpose** — The full-circle mental model: the whole book as one walkable loop, ending
at verse one read differently — plus the only external links in the book.
**Lede** — One last walk, unaided: from a king's anxious question, through a collapse
and two answers, to the lens that is yours — and back to the first verse, which you now
read differently.
**Sections** — (1) "The loop, walked" — the numbered stations, one sentence each: the
frame, the collapse, the deathless self, the discipline of action, the practice, the
divine in full view, the vision, the field and its strands, the settlement, the lenses,
your reading, verse one again; (2) "What you now carry" — the four words, the three
hexads, the forks, the attributed-reading method; (3) "Where to go next" — the links
section (the only external links in this book): the pinned Sanskrit source, the first
English translation's story, the nonviolent reader's discourses, the jurist's riddles,
the mass edition's preface, the mystic's essays, the prison treatise's story, the
physicist's archive — each with a one-line description of what it is and why it is
listed; (4) "The last word" — the book hands the verdict to the reader; the poem's own
exit (the reporter's final line, paraphrased from page 27) is echoed, not decided.
**SVG spec** — The loop: a circle of stations — frame, collapse, self, discipline,
practice, divine, vision, field, settlement, lenses — with a closing arc labeled "your
reading" returning to the frame. Title: "The loop: one walk through the whole". One
structure: the return.
**Links section** — Must be `<section class="links">`; every external URL in the book
lives here and only here. Use the URLs from tools/sources.json.
**Takeaways**
- The Gita is a loop, not a line: every reading changes the reader who rereads.
- You can now walk the poem unaided — frame, collapse, answers, disciplines, divine,
  field, settlement.
- The lenses were never the destination; they were proof that reading is a verb.
- The verdict was never this book's to give — the last word is the poem's own: where
  those two are, there is splendor and unwavering order.
**Bridge-in** — From 39: the open questions are the engine; the loop is the ride.
**Handoff** — None: final page. The page-nav next link returns to the cover.
**Sources** — FS-TEXT, FS-LENSES, FS-MOD, FS-GLOBAL, FS-ACAD, FS-PATT, FS-MAH.

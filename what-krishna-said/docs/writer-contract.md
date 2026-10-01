# Writer Contract — What Krishna Said

This is the binding contract for every page writer. The checker
(`python3 tools/check.py <your-page>.html`) enforces the mechanical parts; your judgment
enforces the rest. When this contract and `docs/architecture.md` disagree, the
architecture wins; when the architecture and a fact sheet disagree, the fact sheet wins.

## Your job

You write exactly ONE page. The file already exists as a scaffold with correct chrome
(title, kicker, h1, table of contents, page navigation, script, stylesheet — verified by
the checker). You replace the `TODO-` regions and nothing else. You edit no other file.
You do not commit to git.

What you replace:

| Region | Becomes |
|---|---|
| `TODO-LEDE` | Your lede: one or two sentences, from the spec's lede direction |
| `TODO-BRIDGE` | Your bridge: two or three sentences picking up the previous page's takeaways (see "Parallel safety" below) |
| `TODO-BODY` | The whole body: sections with `<h2>` heads, verse figures, diagrams — per the spec's section outline and verse beats |
| `TODO-TAKEAWAY-1/2/3` | The spec's takeaway bullets, verbatim, as `<li>` items (3–5 items) |
| `TODO-SOURCE-1/2` | Real source items: `<li data-fs="FS-TEXT">Text and structure facts</li>` — the FS-IDs the spec names, at least two |

What you never touch: the `<title>`, `<p class="kicker">`, `<h1>`, the `<nav id="toc">`
block, the `<nav class="page-nav">` block, the `<script>` tag, the stylesheet link, the
topbar, the skip link. They are correct. If you believe one is wrong, stop and report it
instead of editing.

## Verse figures (pages that have verses)

Your page's verses are prepared in `docs/versepacks/<your-page-file>.html` in exactly the
order the architecture spec lists them. **Copy each `<figure class="verse">` block
verbatim from the versepack into your body.** Do not retype, reword, re-punctuate, or
"fix" the IAST — the checker compares every figure against the registry
character-for-character. The figure shape is:

```html
<figure class="verse" data-verse="2.47">
<figcaption>Bhagavad Gita 2.47</figcaption>
<blockquote class="iast">karmaṇyevādhikāraste mā phaleṣu kadācana | mā karmaphalaheturbhūrmā te saṅgo'stvakarmaṇi</blockquote>
<p class="gloss">Your right is to the action alone, never to its fruits.</p>
<p class="note"><strong>Translation note</strong> The most translated verse.</p>
</figure>
```

The note line appears only when the versepack includes one. Weave prose between figures:
a figure is never self-explanatory; the beats in the spec tell you what each verse does
in the chapter's argument. Every verse assigned to your page must appear exactly once —
the checker counts.

## Terms

The ledger (`tools/terms.json`) gives each Sanskrit term exactly one defining page.

- **Terms your page defines** (the spec's "Terms defined"): each appears in `<dfn>` exactly
  once, and the `<dfn>` comes before any plain reuse on the page. Example:
  `<p>The <dfn>karma</dfn> names three things at once...</p>` — later paragraphs may then
  use "karma" freely.
- **Terms defined on earlier pages**: free to use.
- **Terms defined on later pages**: do not use. Rephrase with plain English ("duty" for
  dharma, "the discipline" for yoga, "the self" for ātman, "devotion" for bhakti). If the
  term is genuinely unavoidable, mark every use:
  `...the field of dharma<!-- term-ok: foreshadowed; defined on 05-dharma -->...` — the
  comment must sit within three lines of each use.
- Sanskrit compounds with diacritics usually do not trip the pattern ("dharmakṣetre" does
  not match "dharma") — but check with the checker rather than assuming.
- The scan covers your lede, body, takeaways, and section headings. Verse IAST blocks,
  the kicker, page-nav, sources, and diagram labels are exempt.

## Provenance

Every factual number in your prose carries a source. The rule: if the text contains a
year (1500–2099), any number of two or more digits, or a single digit followed by a unit
word (verses, chapters, days, armies, books, volumes, pages, years, centuries, decades,
commentaries, parvans, editions, translations, commentators, hexads, guṇas, varṇas), put
the fact-sheet ID in an HTML comment within ten lines:

```html
<p>The first English translation appeared in 1785. <!-- prov: FS-GLOBAL --></p>
```

Exemptions you may rely on: verse references like 2.47 (stripped), text pointers like
"Chapter 14" and "verse 39" (the word chapter or verse before the digit; stripped — but
"14 chapters" and "39 verses" are quantities and need prov), spelled-out numbers
("seven hundred"), text inside verse IAST blocks, the kicker, page-nav, sources footer,
and diagram labels. Takeaways are scanned — keep them free of digits except verse
references. Two escapes exist: `<!-- prov-ok: structural number, not a claim -->` within
two lines for numbers that are bookkeeping (a chapter count in a heading, say), and
wrapping the number itself in `<span class="prov">…</span>`. Prefer the comment.

Valid FS-IDs (anything else fails): FS-TEXT, FS-MAH, FS-LENSES, FS-MOD, FS-PATT,
FS-ACAD, FS-GLOBAL, SRC-IAST. If a number you want to cite is not in a fact sheet, cut
the number — do not invent constants.

## Word window

1200–2200 words, counted over the article's text. Verse glosses and figcaptions count;
verse IAST blocks, the kicker, takeaways, sources, page-nav, and diagram labels do not.
Target 1400–1900. The checker reports your count when you miss the window; the fastest
way to read it is to run the checker.

## Voice

- Second person, plain, concrete. "You have read a table of contents" beats "The reader
  will encounter structural elements."
- No "simply", "just", "obviously", "of course". No filler praise. No stacked rhetorical
  questions.
- Real numbers over adjectives — "the epic runs to about a hundred thousand verse
  lines" (with prov) beats "the enormous epic".
- Sanskrit terms in IAST diacritics (dharma, guṇa, ātman); names in plain transliteration
  (Krishna, Arjuna, Sanjaya). Never both spellings for the same word.
- Interpretations are attributed to named readers: "Shankara reads...", "Gandhi
  called...", "Ambedkar charged...". The book never says "the correct reading is". End
  disagreements by showing them, not settling them.

## Parallel safety (why bridges work without reading neighbors)

Pages are written in parallel; you cannot read your neighbor's final prose. The
architecture spec solves this: **bridge-in picks up the previous page's pinned takeaways**
(quoted in your spec's "Bridge-in"), and **your takeaways are pinned in the spec** so the
next page's writer bridges from them. Close your page pointing toward your spec's
"Handoff" direction. Do not improvise a different handoff.

Takeaways are the spec's bullets **verbatim** — the next page's bridge depends on them
word-for-word.

## Diagrams (only the five pages the spec marks)

If your spec has an "SVG spec" block, build exactly one diagram: a
`<figure class="diagram">` containing inline `<svg role="img" viewBox="...">` with a
`<title>` child (the diagram's name), strokes in `currentColor`, no fills except `none`
or design tokens from DESIGN.md, font-size at least 12, viewBox no larger than 800×520.
Labels short — SVG text does not wrap. One diagram teaches exactly one structure; resist
adding a second. Everyone else: no diagrams.

## Hard structure rules (the checker rejects violations)

- No `<pre>` or `<code>`. No `<img>`. No external URLs (`http://`, `https://`, `mailto:`,
  `data:`, anything absolute). No new `<script>` or stylesheet. Internal links only to
  book pages or `index.html`.
- Section heads inside the body are `<h2>` (never a second `<h1>`).
- Leave no `TODO-` marker anywhere.
- Character encoding is UTF-8; write diacritics and em dashes directly.

## Self-check loop (mandatory)

```
cd /home/sridatta/temp/books/what-krishna-said
python3 tools/check.py <your-page-file>.html
```

Iterate until your page shows zero issues. The scaffold starts with exactly these
errors, and each disappears as you write: `E_NO_TODO` (you removed the markers),
`E_WORD_LOW` (you reached the window), `E_DFN_MISSING` (your terms got their `<dfn>`s),
`E_VERSE_MISSING` (your figures landed). If you see anything else — `E_TERM_EARLY`,
`E_PROV`, `E_TAKEAWAY_COUNT`, and so on — the message names the line; fix the page, never
the checker. Then run the full `python3 tools/check.py` and confirm no new issues for
other pages.

## Report

Reply with: the final checker output for your page (verbatim), your prose word count,
and one line on anything in the spec you had to deviate from and why.

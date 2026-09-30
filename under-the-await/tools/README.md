# tools/ — site QA checker for "Under the Await"

`check_site.py` is the QA gate for content writers. It is **read-only** (never
mutates site files), Python 3.10 stdlib only, single file.

## Usage

```
python3 tools/check_site.py                     # check the real site (parent of tools/)
python3 tools/check_site.py <site_root>         # check another site root
python3 tools/check_site.py --strict            # pending pages become errors
python3 tools/check_site.py --min-words 1200    # word-count floor (default 1200)
python3 tools/check_site.py --fixtures          # built-in self-test
```

The term ledger `tools/terms.json` is a checker resource (not per-site data):
a JSON array of `{"term": <regex>, "defined_in": "pNN-MM"}` entries. Extending
it is encouraged; each `term` is matched whole-word, case-insensitive.

## What is checked

**Page discovery** — `site_root/index.html` plus every `*.html` inside
two-digit part dirs (`NN-slug/`). `tools/`, `templates/`, `research/` and
dot-dirs are never treated as pages. `templates/page.html` is excluded from
page checks but IS offline-scanned. `assets/vendor/` is never scanned.

**Manifest** — the JSON between the exact marker comments
`/* PAGES-MANIFEST-START */` / `/* PAGES-MANIFEST-END */` in
`assets/main.js`. Entry schema: `{id, part, title, file, blurb}`; `file` is
site-root-relative. Unparseable manifest → exit 2.

1. **structure** (per page): doctype present; `<html lang>`; `<meta charset>`;
   `<meta name="viewport">`; exactly one `<h1>`; `<body data-page>` equals BOTH
   the manifest id and the path-derived id (`index.html` → `index`;
   `NN-dir/MM-*.html` → `pNN-MM`).
2. **manifest consistency**: every discovered page file is listed; every entry
   exists on disk or is reported PENDING (error under `--strict`); no
   duplicate ids; derived id must equal manifest id.
3. **links**: internal `<a href>` (fragment stripped) must resolve to an
   existing file relative to the page dir. External `http(s)` `<a>` links are
   allowed ONLY on page `p05-06`. `href="#"` → warning.
4. **offline purity** (pages + `templates/page.html` + `assets/style.css` +
   `assets/main.js`): any `https?://`, `fetch(`, `XMLHttpRequest`, `@import`
   occurrence, or inline `on*` handler attribute in HTML → error.
5. **code blocks**: every `<pre><code>` needs `class="language-X"` with
   X ∈ {rust, c, javascript, python, bash, plaintext, go, java} (case-sensitive);
   missing/unknown → error; block > 30 lines → warning.
6. **svg**: every `<svg>` needs `aria-hidden="true"` OR (`role="img"` AND a
   `<title>` descendant); otherwise error.
7. **word count**: visible prose (excludes head, script, style, pre, code,
   svg, nav, title). Content pages below `--min-words` → warning; above 2400
   words → warning. `index.html` is exempt from the minimum only.
8. **term discipline**: each `terms.json` term appearing in prose
   (whole-word, case-insensitive, code/pre excluded) on a page whose manifest
   position is EARLIER than its `defined_in` page → warning
   "used before defined". `index.html` is exempt — the roadmap necessarily
   teases terms that the parts go on to define. An intentional, glossed
   preview (a map page naming a component it links forward to) can be marked
   with an HTML comment containing `term-ok:` — e.g.
   `<!-- term-ok: scheduler — glossed preview; defined on p04-03 -->` —
   within ±10 lines of the use; annotated uses do not warn.
9. **fs heuristic**: numeric-with-unit claims in prose
   (`\d[\d,._]* (ms|µs|us|ns|s|bytes|KB|MB|GB|threads|cores|%|levels|slots|ops)`)
   with no HTML comment containing `fs:` within ±10 lines → warning.
   Best-effort — see limitations.

## Exit codes

| code | meaning                                             |
|------|-----------------------------------------------------|
| 0    | no errors (warnings allowed)                        |
| 1    | at least one error                                  |
| 2    | invocation / manifest / terms-ledger failure        |

`--min-words` ≤ 0 → exit 2. The `--fixtures` self-test exits 2 if any
assertion fails (valid fixture must be exit 0 with zero errors and zero
terms warnings; broken fixture must be exit 1 with errors covering
structure/links/offline/code/svg plus ≥ 1 terms warning).

## Self-test fixtures

- `tests/fixtures/valid/` — minimal conforming site (manifest has one pending
  entry; note it therefore holds 4 entries incl. `index`, since every
  discovered page must be listed). `01-a` carries an annotated `term-ok:`
  early use of "thread" (defined on the later `p01-02`), exercising the
  term-preview suppression.
- `tests/fixtures/broken/` — one clean violation per error category
  (structure on `01-a`, links on `02-b`, offline on `02-b`/`03-c`, code and
  svg on `01-a`) plus term and fs warning cases; the code violation uses the
  disallowed `language-cobol`.

## Known limitations (deliberate simplicity)

- **fs heuristic is best-effort.** Only the listed units are recognised;
  spelled-out units ("seconds", "milliseconds") and unusual formats are not
  flagged. The ±10-line window is line-based, not semantically aware.
- **offline vs external links overlap.** CHECK 4 flags any `https?://`
  anywhere in scanned files, so an external `<a>` link (allowed on p05-06 by
  CHECK 3) still trips CHECK 4. In practice the site must stay link-pure too.
- **Term matching is lexical.** Common-word patterns (`send`, `sync`,
  `static`, `arc`, `watch`, `context`, `task`, `poll` vs `poll(2)`) can
  produce advisory-only false positives. Longest-pattern-first matching
  suppresses overlaps (e.g. `non-blocking` wins over `blocking`).
- **Bare `<pre>` without `<code>`** is not language-checked (spec covers
  `<pre><code>` only).
- **Link schemes.** `mailto:`/`tel:` hrefs are treated as internal paths and
  will fail resolution; `#fragment` anchors on the same page are fine.
- **Manifest paths are literal.** `file` values must be exact site-root-
  relative POSIX paths (`01-foundations/01-x.html`), no `./` prefixes.
- The 2400-word upper bound is fixed, not scaled by `--min-words`.

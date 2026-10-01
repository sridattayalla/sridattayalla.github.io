# DESIGN.md — What Krishna Said (static book site)

## 0. Research Log
- **Embedded references**: skipped — this is an offline `file://` book artifact, not a product UI;
  the Layer A direction chosen is *editorial minimalism* (typographic, book-like), which the
  curated brand set does not cover better than a disciplined type system.
- **Lazyweb real-product screens**: skipped — product-screenshot research is the wrong genre for
  a long-form reading artifact, and the artifact must work offline with zero external assets.
- **Imagen concept drafts**: skipped — no image-generation tooling is available in this session.
- **ui-ux-db lookups**: typography and contrast decisions below follow WCAG AA + standard
  editorial practice (66–75ch measure, 1.6–1.7 line-height); no palette lookup needed for a
  two-theme text-first design.

## 1. Product statement
A 40-page static book (no build step, no framework, works from `file://`) that walks a motivated
beginner through the Bhagavad Gita verse-by-verse and lens-by-lens. The design must disappear
behind the text: reading comfort over everything, print-like calm, zero decoration that does not
encode structure.

## 2. Tokens

### Color — light theme (`:root`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#faf7f2` (warm paper) | page background |
| `--ink` | `#1c1917` | body text (15.8:1 on bg) |
| `--ink-soft` | `#57534e` | secondary text (7.0:1) |
| `--rule` | `#e7e0d5` | hairlines, borders |
| `--card` | `#fffdf9` | verse blocks, asides |
| `--accent` | `#8a3324` (burnt sienna) | links, kickers, active nav (5.5:1) |
| `--accent-ink` | `#fffdf9` | text on accent |

### Color — dark theme (`[data-theme="dark"]`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#191614` (warm near-black) | page background |
| `--ink` | `#ece7df` | body text (13.9:1) |
| `--ink-soft` | `#b3aba0` | secondary text (6.9:1) |
| `--rule` | `#3a342e` | hairlines |
| `--card` | `#211d1a` | verse blocks |
| `--accent` | `#d99a83` (light sienna) | links, kickers (6.1:1) |
| `--accent-ink` | `#191614` | text on accent |

Theme toggle: button in top bar; persisted in `localStorage`; default follows
`prefers-color-scheme`. All pairs verified ≥ 4.5:1 (WCAG AA normal text).

### Type
| Token | Value |
|---|---|
| `--font-body` | `Georgia, 'Iowan Old Style', 'Times New Roman', serif` |
| `--font-ui` | `'Helvetica Neue', Helvetica, Arial, sans-serif` |
| `--font-verse` | same as body, italic for IAST lines |
| Scale | 1.25 ratio: 16 (body) / 18 (lede) / 22 (h2) / 28 (h1) / 12–13 (UI chrome, kickers) |

### Spacing & layout
- Prose measure: `max-width: 42rem` (≈ 68ch at 16px Georgia).
- Page gutters: `1.25rem` mobile → `2rem` desktop.
- Vertical rhythm: `1rem` base unit; section spacing `2.5rem`.
- Verse figure: card background, `1.25rem` padding, hairline left border (3px accent).
- Takeaways aside: hairline top+bottom rules, `--card` background, list with square markers.

## 3. Primitives
1. **Top bar** — book title (links to index), theme toggle. Sticky, hairline bottom border.
2. **TOC drawer** — slide-in panel (checkbox-free, JS-toggled), full 40-page list grouped by part;
   current page marked. On desktop ≥ 1024px it becomes a persistent left sidebar (fixed 16rem).
3. **Article header** — kicker (part name + page num), h1, lede paragraph.
4. **Verse figure** — `<figure class="verse" data-verse="2.47">`: IAST lines (`.iast`, italic),
   literal gloss (`.gloss`), optional note (`.note`, smaller, `--ink-soft`, labeled "Translation
   note").
5. **Takeaways aside** — `<aside class="takeaways">` with h2 "Takeaways" + 3–5 `<li>`.
6. **Page nav** — prev/next links with titles, hairline top border.
7. **Sources footer** — `<footer class="sources">` with `<li data-fs="FS-...">` items.
8. **Diagrams** — inline SVG, `role="img"` + `<title>` + `<desc>`, `aria-hidden` never (all
   diagrams here are informative); stroke/fill from CSS vars so themes work.

## 4. Motion
- Only: TOC drawer slide (`transform: translateX`, 200ms ease-out), theme cross-fade
  (150ms), focus outlines. `@media (prefers-reduced-motion: reduce)` disables all transitions.
- No scroll animations, no hover effects on non-interactive text. Links: underline offset only.

## 5. Accessibility constraints
- Skip link to `#main` on every page. Focus-visible rings (`outline: 2px solid var(--accent)`).
- All SVGs: `role="img"` + `<title>`; text inside SVG ≥ 12px equivalent, inside viewBox.
- Color never sole carrier of meaning (verse notes carry a text label).
- Landmarks: `header`, `nav`, `main`, `footer`. Pages have `<title>` = "NN — Title · What Krishna Said".

## 6. Responsive behavior
- Mobile (<768px): single column, TOC via hamburger-style button, verse padding reduced.
- Desktop (≥1024px): sidebar TOC + article column, top bar full width.
- No horizontal scroll at any width ≥ 320px (long IAST words wrap with `overflow-wrap: break-word`).

## 7. Offline purity
- Zero external requests: no webfonts, no CDNs, no images (SVG inline only), no analytics.
- JS is progressive enhancement only (TOC, theme): the book is fully readable with JS disabled.

## 8. Accepted debt
- No print stylesheet in v1 (possible follow-up).
- System serif (Georgia) rather than embedded font — deliberate: keeps the artifact offline-pure
  and dependency-free.
- Word-count enforcement is content-level (checker), not visual.

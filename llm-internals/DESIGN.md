# DESIGN.md — LLM Internals

Design system for the static teaching site "LLM Internals — How Large Language Models Actually Work". Every color, font size, spacing value, and component pattern in `assets/style.css` must trace back to this file. The site is plain HTML/CSS/JS served from `file://`, with zero external requests from any page except outbound anchors on `links.html`.

## 0. Research Log

| Lane | Status | Deliverable |
|---|---|---|
| Layer A style skill | LOADED | `minimalist-skill.md` (in full): warm monochrome, editorial serif display, ultra-flat surfaces, hairline 1px borders, muted pastel accents, motion restraint; bans Inter/Roboto/Open Sans primaries, gradients, heavy shadows, pill containers, emojis, AI copy clichés. |
| Layer B design system | LOADED | `linear.app.md` (in full): dark-mode token ramp (near-black canvas, #f7f8f8-class text, semi-transparent white borders), single indigo accent reserved for interaction, luminance-stepped elevation instead of shadows, negative display tracking, weight discipline 400/510/590. |
| imagegen concept drafts | SKIPPED | No image-generation tool exists in this environment. All imagery is hand-authored inline SVG (1.5px ink strokes, one pastel wash fill), per minimalist-skill's illustration directive. |
| lazyweb real-app screens | SKIPPED | Artifact is offline by requirement (`file://`, request-blocking QA); the two loaded references carry the visual direction. |
| ui-ux-db / beui interaction catalog | SKIPPED | Reading surface; interaction surface = nav + drawer + theme toggle only. |
| React dev-tooling gate | SKIPPED | Not a React project (plain HTML/CSS/JS by requirement). |
| open-design library | SKIPPED | Curated Layer B fit found (linear.app). |
| stitch DESIGN.md export | SKIPPED | Not requested. |

Routing: Layer A = minimalist-ui (editorial reading surface, restraint is correct); Layer B = linear.app (technical precision for an LLM-internals audience). Synthesis: minimalist's warm paper light theme + Linear's instrument dark theme, one shared indigo accent, hairline structure everywhere.

## 1. Direction (committed)

A quiet engineering field manual. Light theme is warm paper; dark theme is a near-black instrument panel. Editorial serif carries headlines; precise monospace carries every number, matrix, and token; a sans body carries prose. Color is scarce: one indigo for interaction and citations, four muted washes for semantic panels. The signature moment is the worked-example panel — hand-checkable matrices typeset like instrument readouts inside a hairline frame with a pastel header strip. No gradients, no shadows above 0.06 opacity, no glass; depth comes from luminance steps and 1px hairlines, never blur.

## 2. Typography

System stacks only (offline purity; no webfonts, ever):

- `--font-display`: `Charter, "Bitstream Charter", "Sitka Text", Cambria, Georgia, "Liberation Serif", "Noto Serif", serif` — editorial serif for h1/h2 and pull statements.
- `--font-body`: `"SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Helvetica, Arial, "Noto Sans", "Liberation Sans", sans-serif` — prose and UI.
- `--font-mono`: `ui-monospace, "SF Mono", "Cascadia Code", "JetBrains Mono", Menlo, Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace` — code, token IDs, matrices, prov marks, captions.

Scale (rem-based):

| Role | Size | Line-height | Weight | Tracking | Family |
|---|---|---|---|---|---|
| h1 | clamp(1.9rem, 1.2rem + 2.6vw, 2.5rem) | 1.12 | 650 | -0.015em | display |
| h2 | 1.55rem | 1.22 | 620 | -0.01em | display |
| h3 | 1.18rem | 1.35 | 600 | -0.005em | body |
| lede | 1.15rem | 1.6 | 400 | 0 | body, ink-2 |
| body | 1.0625rem (17px) | 1.65 | 400 | 0 | body |
| small | 0.875rem | 1.55 | 400 | 0 | body |
| caption | 0.78rem | 1.4 | 550 | 0.07em, uppercase | mono |
| code block | 0.9rem | 1.6 | 400 | 0 | mono |
| inline code | 0.88em | inherit | 400 | 0 | mono |

Measure: prose `max-width: 70ch`; content column capped at 46rem (736px). Body text never pure black. Numbers in prose keep their units spaced (`128 KiB`, `175 billion`); scientific notation written as `3.15 × 10<sup>23</sup>`, never `3.15e23`.

## 3. Color

CSS custom properties on `:root` (light) and `:root[data-theme="dark"]`; a `prefers-color-scheme: dark` block re-applies the dark set for `[data-theme]`-less roots. Dark tokens are written twice (media query + explicit) — deliberate, keeps one file and no imports.

Light ("paper"):

```
--bg: #F7F6F3          --surface: #FFFFFF      --surface-2: #F0EEE8
--ink: #20242A         --ink-2: #525A66        --ink-3: #666E78
--border: #E3E1DA      --border-strong: #C8C5BC
--accent: #4C56B8      --accent-strong: #3B44A0    --accent-wash: #E9EAF8
--code-bg: #EFEDE6     --sel: #E1F3FE
--w-red: #FBE9EA       --w-red-ink: #96302E
--w-blue: #E1F3FE      --w-blue-ink: #1E6B9E
--w-green: #ECF2EB     --w-green-ink: #33643A
--w-yellow: #FAF2D9    --w-yellow-ink: #8A5E00
```

Dark ("instrument"):

```
--bg: #0B0C0F          --surface: #14161B      --surface-2: #1B1E24
--ink: #F2F3F5         --ink-2: #C4CAD3        --ink-3: #949BA6
--border: rgba(255,255,255,0.09)   --border-strong: rgba(255,255,255,0.20)
--accent: #8F9AFF      --accent-strong: #ADB6FF   --accent-wash: rgba(143,154,255,0.12)
--code-bg: #181B21     --sel: rgba(143,154,255,0.22)
--w-red: rgba(226,106,106,0.13)    --w-red-ink: #E39B99
--w-blue: rgba(94,148,255,0.14)    --w-blue-ink: #93BDEC
--w-green: rgba(64,160,84,0.14)    --w-green-ink: #85C893
--w-yellow: rgba(214,164,45,0.14)  --w-yellow-ink: #D9B45F
```

Locked shades: `--ink-3` light `#666E78` (≥4.5:1 on surface), dark `#949BA6` (≥4.5:1 on bg). Accent-as-text: `#4C56B8` on paper ≈ 4.8:1; `#8F9AFF` on instrument ≈ 7.5:1. Wash inks all ≥4.5:1 on their washes in both themes. Rules: accent only for links, active states, citation marks, focus rings. Washes are semantic: green = takeaways, yellow = worked example, blue = note, red = warning. Never fill large areas with accent; never introduce a fifth hue.

## 4. Layout & spacing

- Spacing scale (8px base): 4, 8, 12, 16, 24, 32, 48, 64, 96 (`--s1..--s9`).
- Desktop ≥1120px: CSS grid `[sidebar 280px][content 1fr]`; sidebar sticky, height 100dvh, own scroll; content centered, `padding-inline: clamp(20px, 5vw, 48px)`.
- 768–1119px: top bar (mark, hamburger, theme toggle) + slide-in drawer reusing the sidebar markup.
- <768px: same drawer; content padding 18px.
- Pager: 2-column grid, gap 12px; stacks below 560px.
- Radii: `--r1` 4px (kbd, inline code), `--r2` 6px (buttons, inputs), `--r3` 10px (cards, pre, figures), `--r4` 14px (worked panels, showcase cards). Pills only for tag badges.
- Borders: 1px `--border` everywhere structural; active nav gets a 2px accent left bar.
- Print: hide sidebar/header/pager/theme toggle; black on white; expand code blocks.

## 5. Components & states

Canonical page skeleton (enforced structurally by `tools/check.py`):

```
<!DOCTYPE html><html lang="en"><head>
  charset, viewport, title, inline no-FOUC theme script, <link assets/style.css>
</head>
<body data-page="ID">
  skip link -> #main
  <header class="topbar"> mark | hamburger | theme toggle </header>
  <nav class="site-nav"> part-grouped links (excluded from term checks) </nav>
  <div class="drawer-backdrop"></div>
  <main id="main"> article: h1, lede, sections; figures; worked panels; pager </main>
  <aside class="takeaways"> h2 + 3-5 li </aside>
  <script src="assets/site.js" defer>
</body></html>
```

Primitives (each with rest/hover/focus-visible/active states; showcased in `assets/showcase.html`):

1. **Nav link** — rest ink-2; hover ink + underline; active ink + 2px accent bar; focus 2px accent outline offset 2px. Group labels as caption-style mono.
2. **Pager card** — surface + hairline border, radius 10; caption "PREVIOUS/NEXT" + page title; hover border-strong; whole card is the link.
3. **Theme toggle** — 36px circular icon button, hairline border, inline SVG sun/moon; JS sets `data-theme` on `<html>`, persists `localStorage["llmi-theme"]`, honors `prefers-color-scheme` when unset; `aria-pressed` reflects state; works with JS off (site stays readable, toggle hidden via `noscript`-safe CSS).
4. **Mobile drawer** — hamburger 40px with `aria-expanded`/`aria-controls`; drawer slides 240ms; backdrop rgba(0,0,0,0.4) click-to-close; Esc closes; focus returns to hamburger.
5. **Takeaways aside** — green wash bg, tinted border, caption header "TAKEAWAYS", square accent bullets, 3-5 items.
6. **Worked panel** (`.worked`) — yellow wash header strip (caption "WORKED EXAMPLE"), mono body 0.85rem, hairline border, radius 14; matrices as aligned mono text.
7. **Note callout** — blue wash, caption "NOTE".
8. **Warning callout** — red wash, caption "WATCH OUT".
9. **Prov mark** — inline `<a class="prov" data-src="research/x.md" href="links.html#s-x">[key]</a>`; mono, 0.72em, accent; hover accent-strong + underline; `title` attribute names the source.
10. **dfn term link** — `<dfn>`/`<a>` to `glossary.html#t-slug`; dotted accent-strong underline.
11. **Inline code** — `--code-bg`, radius 4, 0.88em, padding 1px 5px.
12. **Code block** — `pre>code.language-python|text`; `--code-bg`, radius 10, hairline border, padding 16px 20px, optional caption filename header; horizontal scroll, no wrap.
13. **kbd** — border `--border-strong`, radius 4, bg `--surface-2`, mono 0.78rem.
14. **Tag pill** — caption style, wash+ink pair, radius 9999px; part labels only.
15. **Figure/SVG frame** — hairline border, surface bg, padding 16, figcaption caption ink-3; SVG: `role="img"` + `<title>`, viewBox always, 1.5px `currentColor` strokes, pastel wash fills, mono labels ≥11px.
16. **Formula** (`.math`) — display serif 1.15rem, centered block, mono annotations, prov-marked constants.
17. **Data table** — hairline row borders, header row `--surface-2`, mono numerals, caption header.

Showcase location: `assets/showcase.html` (outside the manifest root scan by design — it is a QA harness, not a reading page; exercises every primitive and both themes).

## 6. Motion

- Color/border/background transitions: 160ms `ease`.
- Drawer: 240ms transform `cubic-bezier(0.2, 0, 0, 1)`.
- Card hover: border-color change only — no lift, no scale, no shadow.
- `prefers-reduced-motion: reduce` → all transitions 1ms.
- No scroll-triggered animation (decision: reading surface, offline robustness; restraint over spectacle).

## 7. Accessibility

- WCAG AA both themes on all token pairs above; verified pairs listed in §3.
- Focus-visible never removed (2px accent outline, 2px offset); skip link to `#main`.
- Drawer: `aria-expanded`, Esc, backdrop click, focus return. Toggle: `aria-label="Toggle dark theme"`.
- SVGs: `role="img"` + `<title>`, or `aria-hidden="true"` when decorative.
- Tap targets ≥40px; `lang="en"`; no color-only meaning (prov marks bracketed `[key]` text, not color alone).
- No-JS contract: every page fully readable and navigable with JavaScript disabled; JS only enhances theme/drawer.

## 8. Anti-patterns (hard bans)

- No Inter/Roboto/Open Sans as identity fonts; no webfonts, CDNs, or external requests (except links.html outbound anchors).
- No gradients, neon, glassmorphism, shadows above 0.06 opacity; no pill-shaped containers; pills only for tag badges.
- No emojis anywhere (code, markup, alt text, headings). No placeholder copy. No "Elevate/Seamless/Unleash/Next-Gen/Game-changer/Delve".
- No JS-dependent content; no layout-triggering animations; no autoplay; no `alert()/confirm()`.
- No raw hex in pages — all styling through tokens defined here.

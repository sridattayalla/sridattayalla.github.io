# Design — Rust Design Decisions

What the artifact looks like, why, and the numbers that justify it. The
aesthetic is inherited from the sibling book (`../llm-internals`): a
paper-and-instrument pairing built to survive printing, dark rooms, and
`file://` delivery. This file records the deviations and the measurements.

## Identity

- One accent: rust-orange. It marks links, prov marks, the active nav bar,
  focus outlines, and the site mark. Everything else is ink on paper.
- Warm-paper light theme, near-black instrument dark theme. Hairline
  borders, no gradients, no shadows, no webfonts, no external requests:
  the site works from `file://` offline.
- System stacks: serif display (Charter/Georgia), sans body, mono code.

## Palette

| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | `#F7F6F3` | `#0B0C0F` | page background |
| `--surface` | `#FFFFFF` | `#14161B` | cards, figures |
| `--surface-2` | `#F0EEE8` | `#1B1E24` | table heads, codeblock captions |
| `--ink` | `#20242A` | `#F2F3F5` | body text |
| `--ink-2` | `#525A66` | `#C4CAD3` | secondary text |
| `--ink-3` | `#636B75` | `#949BA6` | kickers, captions, dim labels |
| `--accent` | `#9A4A1F` | `#E8975F` | links, prov marks, active nav |
| `--accent-strong` | `#7E3A16` | `#F5B380` | hover state |
| `--accent-wash` | `#F7E9DF` | `rgba(232,151,95,.12)` | accent fills |
| `--sel` | `#F8E7DA` | `rgba(232,151,95,.22)` | selection |
| washes | unchanged from the sibling base | unchanged | note, warn, takeaways, worked |

Every text-relevant pair is measured by `tools/contrast.py` (WCAG 2.1
relative luminance; rgba washes composited over both `--bg` and `--surface`;
the duplicate dark block inside the `@media` query must not drift — the
script fails on drift). Run of 2026-09-26:

- worst light pair: `ink-3` on `surface-2` at 4.65:1 (AA text is 4.5:1)
- worst dark pair: `ink-3` on `surface-2` at 5.96:1
- `accent` on `bg`: 5.76:1 light, 8.40:1 dark; on `surface`: 6.23:1 / 7.78:1
- every wash ink clears 5.05:1 light and 6.90:1 dark

Deviations from the sibling base, and why:

- The accent family is rust-orange instead of indigo, and `--sel` is warm
  instead of pale blue: the book's identity color, with selection in
  agreement.
- `--ink-3` light was darkened from the sibling's `#666E78` to `#636B75`:
  the sibling value measures 4.45:1 on `--surface-2` (codeblock captions),
  a hair under AA; `#636B75` measures 4.65:1.

## Verdict-marked code

The book's core move is showing the code the compiler refuses next to the
code it accepts, and never claiming a verdict the toolchain did not produce:

- `figure.codeblock.reject` / `pre.reject` — red left border, red caption:
  the snippet is rejected (`data-verify="fail" data-error="E0382"`).
- `figure.codeblock.accept` / `pre.accept` — green left border: the snippet
  compiles (`data-verify="ok"`), and with `data-verify="run"` it prints the
  quoted output.

Every marked block is machine-verified by `tools/verify.py` (rustc 1.98.1
for Rust; gcc 11.4.0 for plain C runs; clang 14.0.0 for sanitizer runs —
gcc 11 folds the dangling-return pattern the stack-use-after-return check
depends on; all C compiles at `-O0` because optimization runs before
instrumentation and can delete the bug being verified). `tools/check.py`
refuses missing or stale results (`E_VERIFY`).

## Theme mechanism

An inline head script adds `.js` and applies the stored choice (localStorage
key `rdd-theme`) before first paint — no flash of wrong theme. The OS
preference is followed while no explicit choice exists; clearing the stored
key returns control to the OS. With JavaScript disabled the toggle and
drawer hide, the nav renders as a static list, and every page stays fully
readable and navigable.

## Layout

Sticky topbar; at 1120px and wider a sticky 280px sidebar nav; below that a
hamburger drawer with focus trap and Escape handling. Article column 46rem.
Print stylesheet drops the chrome and wraps code.

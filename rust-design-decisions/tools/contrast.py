#!/usr/bin/env python3
"""Palette gate for assets/style.css.

Measures WCAG 2.1 contrast ratios for every text-relevant token pair in both
themes. rgba() washes are composited over both --bg and --surface before
measuring, so a pair passes only if it passes on every plausible backdrop.
The duplicate dark-token block inside the @media (prefers-color-scheme)
query must stay identical to :root[data-theme='dark']; drift fails the run.
Exits 1 if any pair falls below 4.5:1 (WCAG AA for text)."""

import os
import re

AA = 4.5

TEXT_PAIRS = [
    ("ink", "bg"), ("ink", "surface"), ("ink", "code-bg"),
    ("ink-2", "bg"), ("ink-2", "surface"), ("ink-2", "surface-2"),
    ("ink-3", "bg"), ("ink-3", "surface"), ("ink-3", "surface-2"),
    ("accent", "bg"), ("accent", "surface"),
    ("accent-strong", "bg"), ("accent-strong", "surface"),
    ("accent", "accent-wash"),
    ("ink", "w-green"), ("ink", "w-blue"), ("ink", "w-red"),
    ("w-red-ink", "w-red"), ("w-blue-ink", "w-blue"),
    ("w-green-ink", "w-green"), ("w-yellow-ink", "w-yellow"),
]

DARK = ":root[data-theme='dark']"
MEDIA_DARK = ":root:not([data-theme='light'])"


def theme_tokens(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    if not m:
        raise SystemExit(f"style.css: selector {selector!r} not found")
    tokens = {}
    for decl in m.group(1).split(";"):
        if ":" not in decl:
            continue
        name, _, value = decl.partition(":")
        name = name.strip()
        if name.startswith("--"):
            tokens[name[2:]] = value.strip()
    return tokens


def resolve(value, base_rgb):
    value = value.strip()
    if value.startswith("#"):
        v = value[1:]
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"rgba?\(([^)]+)\)", value)
    if not m:
        raise SystemExit(f"style.css: cannot parse color {value!r}")
    parts = [p.strip() for p in m.group(1).split(",")]
    rgb = [float(p) for p in parts[:3]]
    alpha = float(parts[3]) if len(parts) > 3 else 1.0
    return tuple(round(c * alpha + b * (1.0 - alpha))
                 for c, b in zip(rgb, base_rgb))


def rel_lum(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    l1, l2 = sorted((rel_lum(fg), rel_lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def check_theme(name, tokens):
    failures = []
    bases = [resolve(tokens["bg"], (0, 0, 0)),
             resolve(tokens["surface"], (0, 0, 0))]
    for fg_name, bg_name in TEXT_PAIRS:
        seen = set()
        for base in bases:
            bg_rgb = resolve(tokens[bg_name], base)
            if bg_rgb in seen:
                continue
            seen.add(bg_rgb)
            ratio = contrast(resolve(tokens[fg_name], bg_rgb), bg_rgb)
            ok = ratio >= AA
            if not ok:
                failures.append(f"{name} theme: {fg_name} on {bg_name} "
                                f"is {ratio:.2f}:1, below {AA}:1")
            print(f"{name:<5} {fg_name:<13} on {bg_name:<12} "
                  f"{ratio:6.2f}:1  {'PASS' if ok else 'FAIL'}")
    return failures


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "assets", "style.css"),
              encoding="utf-8") as f:
        css = f.read()
    light = theme_tokens(css, ":root")
    dark = theme_tokens(css, DARK)
    media_dark = theme_tokens(css, MEDIA_DARK)
    failures = []
    for key in sorted(set(dark) | set(media_dark)):
        if dark.get(key) != media_dark.get(key):
            failures.append(f"dark tokens drifted from the @media block: "
                            f"--{key}: {dark.get(key)!r} vs "
                            f"{media_dark.get(key)!r}")
    failures += check_theme("light", light)
    failures += check_theme("dark", dark)
    if failures:
        print()
        for f in failures:
            print(f"CONTRAST FAIL: {f}")
        raise SystemExit(1)
    print(f"\nCONTRAST PASS: every text pair clears WCAG AA ({AA}:1) "
          "in both themes")


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Scaffold the 41 book pages from tools/manifest.json.

Usage: python3 tools/scaffold.py

Writes every manifest page with chrome (head, TOC, kicker, page-nav) filled in
and body content left as TODO- placeholders for the writer waves. Existing
files are NEVER overwritten — reruns are safe. Also refreshes
docs/page-template.html as a reference copy with TODO placeholders.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Final

BOOK_ROOT: Final = Path(__file__).resolve().parent.parent

TEMPLATE: Final = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
<button class="toc-toggle" aria-expanded="false" aria-controls="toc">Contents</button>
<a class="home" href="index.html">What Krishna Said</a>
<button class="theme-toggle" aria-label="Toggle dark mode">&#9686;</button>
</header>
<nav id="toc" class="toc" aria-label="Book contents">
<button class="toc-close" aria-label="Close contents">&#215;</button>
{{TOC}}
</nav>
<main id="main" class="page">
<article>
<header class="page-head">
<p class="kicker">{{KICKER}}</p>
<h1>{{H1}}</h1>
<p class="lede">TODO-LEDE — one or two sentences framing the page.</p>
</header>
<section class="bridge">
<p>TODO-BRIDGE — two or three sentences picking up from the previous page's takeaways.</p>
</section>
TODO-BODY
<aside class="takeaways">
<h2>Takeaways</h2>
<ol>
<li>TODO-TAKEAWAY-1</li>
<li>TODO-TAKEAWAY-2</li>
<li>TODO-TAKEAWAY-3</li>
</ol>
</aside>
<nav class="page-nav" aria-label="Page navigation">
<a class="prev" href="{{PREV_HREF}}"><span class="dir">Previous</span>{{PREV_LABEL}}</a>
<a class="next" href="{{NEXT_HREF}}"><span class="dir">Next</span>{{NEXT_LABEL}}</a>
</nav>
<footer class="sources">
<h2>Sources for this page</h2>
<ul>
<li data-fs="FS-TEXT">TODO-SOURCE-1 — name the fact sheet.</li>
<li data-fs="FS-TEXT">TODO-SOURCE-2 — name the fact sheet.</li>
</ul>
</footer>
</article>
</main>
<script src="assets/book.js"></script>
</body>
</html>
"""

BODY_PLACEHOLDER: Final = """<p>TODO-BODY — prose sections, verse figures, diagrams. Delete this block.</p>"""


@dataclass(frozen=True, slots=True)
class PageSpec:
    file: str
    num: str
    title: str
    part: int
    part_name: str


def load_pages() -> list[PageSpec]:
    manifest = json.loads((BOOK_ROOT / "tools" / "manifest.json").read_text(encoding="utf-8"))
    return [
        PageSpec(
            file=entry["file"],
            num=entry["num"],
            title=entry["title"],
            part=entry["part"],
            part_name=entry["partName"],
        )
        for entry in manifest["pages"]
    ]


def render_toc(pages: list[PageSpec], current_file: str) -> str:
    """Build the sidebar TOC, grouped by part, marking the current page."""
    lines: list[str] = ['<h2>Contents</h2>']
    for idx, page in enumerate(pages):
        if idx == 0 or pages[idx - 1].part != page.part:
            lines.append(f'<p class="toc-part">{escape(page.part_name)}</p>')
            lines.append("<ul>")
        label = f'{page.num} &#183; {escape(page.title)}'
        current = ' aria-current="page"' if page.file == current_file else ""
        lines.append(f'<li><a href="{page.file}"{current}>{label}</a></li>')
        if idx == len(pages) - 1 or pages[idx + 1].part != page.part:
            lines.append("</ul>")
    return "\n".join(lines)


def neighbor_label(page: PageSpec, pages: list[PageSpec], direction: str) -> tuple[str, str]:
    """Return (href, label) for prev/next, wrapping to the cover."""
    idx = next(i for i, p in enumerate(pages) if p.file == page.file)
    if direction == "prev":
        if idx == 0:
            return "index.html", "Cover &amp; contents"
        prev = pages[idx - 1]
        return prev.file, f"{prev.num} &#183; {escape(prev.title)}"
    if idx == len(pages) - 1:
        return "index.html", "Cover &amp; contents"
    nxt = pages[idx + 1]
    return nxt.file, f"{nxt.num} &#183; {escape(nxt.title)}"


def render_page(page: PageSpec, pages: list[PageSpec]) -> str:
    prev_href, prev_label = neighbor_label(page, pages, "prev")
    next_href, next_label = neighbor_label(page, pages, "next")
    replacements = {
        "{{TITLE}}": f"{page.num} — {escape(page.title)} &#183; What Krishna Said",
        "{{KICKER}}": f"{escape(page.part_name)} &#183; {page.num}",
        "{{H1}}": escape(page.title),
        "{{TOC}}": render_toc(pages, page.file),
        "{{PREV_HREF}}": prev_href,
        "{{PREV_LABEL}}": prev_label,
        "{{NEXT_HREF}}": next_href,
        "{{NEXT_LABEL}}": next_label,
    }
    html = TEMPLATE
    for token, value in replacements.items():
        html = html.replace(token, value)
    return html.replace("TODO-BODY", BODY_PLACEHOLDER)


def main() -> None:
    pages = load_pages()
    created: list[str] = []
    skipped: list[str] = []
    for page in pages:
        target = BOOK_ROOT / page.file
        if target.exists():
            skipped.append(page.file)
            continue
        target.write_text(render_page(page, pages), encoding="utf-8")
        created.append(page.file)
    template_copy = BOOK_ROOT / "docs" / "page-template.html"
    template_copy.write_text(render_page(pages[0], pages), encoding="utf-8")
    print(f"created: {len(created)} pages")
    for name in created:
        print(f"  + {name}")
    print(f"skipped (already exist): {len(skipped)}")
    print("reference template written to docs/page-template.html")


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Structural conformance rules: template chrome, navigation, offline purity."""
from __future__ import annotations

from checker.model import Book, Issue, PageSpec, normalize_ws
from checker.dom import Node

EXTERNAL_PREFIXES: tuple[str, ...] = (
    "http://",
    "https://",
    "//",
    "mailto:",
    "data:",
    "ftp://",
)
INDEX_TITLE = "What Krishna Said — the Bhagavad Gita without a verdict"


def is_external(url: str) -> bool:
    return url.startswith(EXTERNAL_PREFIXES)


def _expected_title(page: PageSpec) -> str:
    return f"{page.num} — {page.title} · What Krishna Said"


def _expected_prev(page: PageSpec, book: Book) -> str:
    return "index.html" if page.index == 0 else book.pages[page.index - 1].file


def _expected_next(page: PageSpec, book: Book) -> str:
    last = len(book.pages) - 1
    return "index.html" if page.index == last else book.pages[page.index + 1].file


def _external_urls(root: Node, page_file: str) -> list[tuple[int, str]]:
    """Collect (line, url) for external href/src, allowing the links section
    of the book's final page (40-the-loop.html)."""
    allowed: set[int] = set()
    if page_file == "40-the-loop.html":
        for section in root.find_all("section", class_="links"):
            for node in section.walk():
                allowed.add(id(node))
    out: list[tuple[int, str]] = []
    for node in root.walk():
        if id(node) in allowed:
            continue
        for attr in ("href", "src"):
            url = node.attrs.get(attr, "")
            if url and is_external(url):
                out.append((node.line, url))
    return out


def _internal_links(root: Node, book: Book) -> list[tuple[int, str]]:
    """Collect (line, href) for links that do not resolve."""
    valid_files = {page.file for page in book.pages} | {"index.html"}
    page_ids = {n.attrs["id"] for n in root.walk() if n.attrs.get("id")}
    out: list[tuple[int, str]] = []
    for anchor in root.find_all("a"):
        href = anchor.attrs.get("href", "")
        if not href or is_external(href):
            continue
        if href.startswith("#"):
            if len(href) > 1 and href[1:] not in page_ids:
                out.append((anchor.line, href))
            continue
        target = href.split("#")[0]
        if target.endswith(".html") and target not in valid_files:
            out.append((anchor.line, href))
    return out


def check_structure(page: PageSpec, root: Node, raw: str, book: Book) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 0) -> None:
        issues.append(Issue(page.file, code, message, line))

    titles = root.find_all("title")
    title_text = normalize_ws(titles[0].text()) if titles else ""
    if title_text != _expected_title(page):
        add("E_TITLE", f"title is {title_text!r}, want {_expected_title(page)!r}")

    skip = root.find("a", class_="skip")
    mains = [n for n in root.find_all("main") if n.attrs.get("id") == "main"]
    if skip is None or skip.attrs.get("href") != "#main" or not mains:
        add("E_SKIP", "skip link to #main or main#main missing")

    topbar = root.find("header", class_="topbar")
    home = topbar.find("a", class_="home") if topbar else None
    if topbar is None or home is None or home.attrs.get("href") != "index.html":
        add("E_TOPBAR", "header.topbar with a.home -> index.html missing")

    articles = root.find_all("article")
    article = articles[0] if articles else root
    main_ok = bool(mains) and any(
        id(a) in {id(n) for n in mains[0].walk()} for a in articles
    )
    if not main_ok:
        add("E_MAIN", "main#main containing article missing")

    toc = next((n for n in root.find_all("nav") if n.attrs.get("id") == "toc"), None)
    if toc is None or not toc.find_all("a"):
        add("E_TOC_MISSING", "nav#toc with links missing")
    else:
        toc_hrefs = {a.attrs.get("href", "") for a in toc.find_all("a")}
        missing = [p.file for p in book.pages if p.file not in toc_hrefs]
        if missing:
            add("E_TOC_LINKS", f"TOC missing {len(missing)} pages: {missing[:3]}")
        currents = [a for a in toc.find_all("a") if a.attrs.get("aria-current") == "page"]
        if len(currents) != 1 or currents[0].attrs.get("href") != page.file:
            add("E_TOC_CURRENT", f"want exactly one aria-current link -> {page.file}")

    kicker = article.find("p", class_="kicker")
    kicker_text = normalize_ws(kicker.text()) if kicker else ""
    if kicker_text != f"{page.part_name} · {page.num}":
        add("E_KICKER", f"kicker is {kicker_text!r}")

    h1s = article.find_all("h1")
    if len(h1s) != 1:
        add("E_H1_MULTI", f"{len(h1s)} h1 elements, want exactly 1")
    if not h1s or normalize_ws(h1s[0].text()) != page.title:
        add("E_H1", "h1 text missing or mismatched")

    head = article.find("header", class_="page-head")
    lede = head.find("p", class_="lede") if head else None
    if lede is None or not normalize_ws(lede.text()):
        add("E_LEDE", "p.lede missing or empty")

    bridge = article.find("section", class_="bridge")
    if bridge is None or not normalize_ws(bridge.text()):
        add("E_BRIDGE", "section.bridge missing or empty")

    nav = article.find("nav", class_="page-nav")
    prev = nav.find("a", class_="prev") if nav else None
    nxt = nav.find("a", class_="next") if nav else None
    if prev is None or prev.attrs.get("href") != _expected_prev(page, book):
        add("E_NAV_PREV", f"prev href != {_expected_prev(page, book)!r}")
    if nxt is None or nxt.attrs.get("href") != _expected_next(page, book):
        add("E_NAV_NEXT", f"next href != {_expected_next(page, book)!r}")

    scripts = root.find_all("script")
    script_ok = (
        len(scripts) == 1
        and scripts[0].attrs.get("src") == "assets/book.js"
        and not normalize_ws(scripts[0].text())
    )
    if not script_ok:
        add("E_SCRIPT", "want exactly one script, src=assets/book.js, no inline code")

    links = [l for l in root.find_all("link") if l.attrs.get("rel") == "stylesheet"]
    if not any(l.attrs.get("href") == "assets/style.css" for l in links):
        add("E_STYLESHEET", "stylesheet link to assets/style.css missing")

    if root.find_all("pre") or root.find_all("code"):
        add("E_PRE", "pre/code blocks are not allowed in this book")
    if root.find_all("img"):
        add("E_IMG", "img tags are not allowed (inline SVG only)")

    for svg in root.find_all("svg"):
        # HTMLParser lowercases attribute names; real markup may use viewBox.
        if not any(k.lower() == "viewbox" for k in svg.attrs):
            add("E_SVG_VIEWBOX", "svg without viewBox", svg.line)
        hidden = svg.attrs.get("aria-hidden") == "true"
        has_title = any(normalize_ws(t.text()) for t in svg.find_all("title"))
        if not hidden and (svg.attrs.get("role") != "img" or not has_title):
            add("E_SVG_ROLE", "svg needs role=img + <title>, or aria-hidden", svg.line)

    for line, url in _external_urls(root, page.file):
        add("E_EXTERNAL", f"external URL {url!r} (offline purity)", line)
    for line, href in _internal_links(root, book):
        add("E_INTERNAL_LINK", f"unresolved link {href!r}", line)

    if "TODO-" in raw:
        add("E_NO_TODO", "page still contains TODO- markers")
    return issues


def check_index(root: Node, raw: str, book: Book) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 0) -> None:
        issues.append(Issue("index.html", code, message, line))

    titles = root.find_all("title")
    title_text = normalize_ws(titles[0].text()) if titles else ""
    if title_text != INDEX_TITLE:
        add("E_INDEX_TITLE", f"title is {title_text!r}")
    hrefs = {a.attrs.get("href", "") for a in root.find_all("a")}
    missing = [p.file for p in book.pages if p.file not in hrefs]
    if missing:
        add("E_INDEX_LINKS", f"missing {len(missing)} page links: {missing[:3]}")
    for node in root.walk():
        for attr in ("href", "src"):
            url = node.attrs.get(attr, "")
            if url and is_external(url):
                add("E_INDEX_EXTERNAL", f"external URL {url!r}", node.line)
    if "TODO-" in raw:
        add("E_NO_TODO", "index still contains TODO- markers")
    return issues

# /// script
# requires-python = ">=3.10"
# dependencies = []
# -*-
"""Content rules: word window, verse registry, term ledger, provenance, takeaways, sources."""
from __future__ import annotations

import re

from checker.dom import Node
from checker.model import Book, Issue, PageSpec, Verse, display_iast, normalize_ws

WORD_EXCLUDE: frozenset[str] = frozenset({"iast", "takeaways", "sources", "page-nav", "kicker"})
TERM_EXCLUDE: frozenset[str] = frozenset({"iast", "sources", "page-nav", "kicker", "diagram"})
TERM_ORDER_EXCLUDE: frozenset[str] = frozenset({"iast", "sources", "page-nav", "kicker", "page-head", "diagram"})
PROV_EXCLUDE: frozenset[str] = frozenset({"iast", "sources", "page-nav", "kicker", "diagram"})
PROV_EXCLUDE_TAGS: frozenset[str] = frozenset({"h1"})

VERSE_REF = re.compile(r"\d+\.\d+")
# "Chapter 14" and "verse 39" are pointers into the text, not quantities;
# "14 chapters" still fires via NUM_UNIT.
POINTER_REF = re.compile(
    r"(?i)\b(?:chapters?|verses?)\s+\d+(?:\s*(?:,|and|to|through|–|-)\s*\d+)*"
)
YEAR = re.compile(r"\b(?:1[6-9]\d{2}|20\d{2})\b")
NUM2 = re.compile(r"(?<![\d.,])\d{2,}(?![\d.])")
UNIT = (
    r"(?:verses?|chapters?|days?|armies|gu[nṇ]as?|var[nṇ]as?|books?|volumes?|pages|"
    r"years?|centur(?:y|ies)|decades?|commentaries|parvans?|editions?|"
    r"translations?|commentators?|hexads?)"
)
NUM_UNIT = re.compile(rf"\b\d\s*{UNIT}\b", re.IGNORECASE)


def _term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(rf"(?i)\b{escaped}[a-z]{{0,2}}\b")


def _active_terms_in(text: str, terms: dict[str, str]) -> set[str]:
    """Ledger terms with an unsuppressed match in this text chunk.

    A match that lies inside the match of a longer ledger term is a fragment
    of that compound (bhakti inside bhakti-yoga, yoga inside karma-yoga) and
    does not count as a use of the shorter term.
    """
    spans: list[tuple[int, int, str]] = []
    for term in terms:
        for m in _term_pattern(term).finditer(text):
            spans.append((m.start(), m.end(), term))
    active: set[str] = set()
    for start, end, term in spans:
        if any(
            s <= start and end <= e and len(other) > len(term)
            for (s, e, other) in spans
        ):
            continue
        active.add(term)
    return active


def has_numeric_claim(text: str) -> bool:
    stripped = POINTER_REF.sub(" ", VERSE_REF.sub(" ", text))
    return bool(YEAR.search(stripped) or NUM2.search(stripped) or NUM_UNIT.search(stripped))


def _comment_near(
    comments: list[tuple[int, str]], line: int, prefix: str, window: int
) -> list[str]:
    return [c for (cline, c) in comments if c.startswith(prefix) and abs(cline - line) <= window]


def _prov_ok_near(comments: list[tuple[int, str]], line: int) -> bool:
    return bool(_comment_near(comments, line, "prov-ok", 2))


def _term_ok_near(comments: list[tuple[int, str]], line: int) -> bool:
    return bool(_comment_near(comments, line, "term-ok", 3))


def _prov_fs_near(comments: list[tuple[int, str]], line: int) -> str | None:
    hits = _comment_near(comments, line, "prov:", 10)
    if not hits:
        return None
    match = re.search(r"prov:\s*([A-Za-z0-9-]+)", hits[0])
    return match.group(1) if match else ""


def _check_word_count(article: Node, book: Book, add) -> None:
    text = article.text(WORD_EXCLUDE)
    words = [w for w in text.split() if any(c.isalnum() for c in w)]
    low, high = book.words_window
    if len(words) < low:
        add("E_WORD_LOW", f"{len(words)} words, window starts at {low}")
    if len(words) > high:
        add("E_WORD_HIGH", f"{len(words)} words, window ends at {high}")


def _check_verse(fig: Node, vid: str, verse: Verse, add) -> None:
    caps = fig.find_all("figcaption")
    if not caps or normalize_ws(caps[0].text()) != f"Bhagavad Gita {vid}":
        add("E_VERSE_CAPTION", f"{vid}: figcaption mismatch", fig.line)
    iasts = fig.find_all(class_="iast")
    want_iast = normalize_ws(display_iast(verse.iast))
    if not iasts or normalize_ws(iasts[0].text()) != want_iast:
        add("E_VERSE_IAST", f"{vid}: IAST does not match registry", fig.line)
    glosses = fig.find_all(class_="gloss")
    if not glosses or normalize_ws(glosses[0].text()) != normalize_ws(verse.gloss):
        add("E_VERSE_GLOSS", f"{vid}: gloss does not match registry", fig.line)
    notes = fig.find_all(class_="note")
    if verse.note:
        want_note = normalize_ws(f"Translation note {verse.note}")
        if not notes or normalize_ws(notes[0].text()) != want_note:
            add("E_VERSE_NOTE", f"{vid}: translation note mismatch", fig.line)
    elif notes:
        add("E_VERSE_NOTE", f"{vid}: registry has no note but page shows one", fig.line)


def _check_verses(article: Node, page: PageSpec, book: Book, add) -> None:
    seen: set[str] = set()
    for fig in article.find_all("figure", class_="verse"):
        vid = fig.attrs.get("data-verse", "")
        if vid not in book.verses:
            add("E_VERSE_REGISTRY", f"{vid!r} not in verse registry", fig.line)
            continue
        if vid not in page.verses:
            add("E_VERSE_ALLOWED", f"{vid} not assigned to this page", fig.line)
        seen.add(vid)
        _check_verse(fig, vid, book.verses[vid], add)
    for vid in page.verses:
        if vid not in seen:
            add("E_VERSE_MISSING", f"{vid} assigned to this page but not shown")


def _check_dfns(article: Node, page: PageSpec, add) -> None:
    dfn_texts = [normalize_ws(d.text()) for d in article.find_all("dfn")]
    for text in set(dfn_texts):
        if dfn_texts.count(text) > 1:
            add("E_DFN_DUP", f"{text!r} defined {dfn_texts.count(text)} times on this page")
        if text not in page.defines:
            add("E_DFN_NOT_PLANNED", f"{text!r} not in this page's defines list")
    for term in page.defines:
        if term not in dfn_texts:
            add("E_DFN_MISSING", f"planned term {term!r} has no <dfn> on this page")


def _check_terms(article: Node, page: PageSpec, book: Book, comments, add) -> None:
    file_index = {p.file: p.index for p in book.pages}

    def scan(exclude: frozenset[str]) -> list[tuple[int, bool, set[str]]]:
        return [
            (line, dfn, _active_terms_in(text, book.terms))
            for (text, line, dfn, _prov) in article.text_items(exclude)
        ]

    active_all = scan(TERM_EXCLUDE)
    active_body = scan(TERM_ORDER_EXCLUDE)
    for term, def_file in book.terms.items():
        hits_all = [(line, dfn) for (line, dfn, active) in active_all if term in active]
        if not hits_all:
            continue
        if page.file == def_file:
            hits_body = [
                (line, dfn) for (line, dfn, active) in active_body if term in active
            ]
            if hits_body:
                first_line, first_dfn = hits_body[0]
                has_dfn_hit = any(dfn for _, dfn in hits_body)
                if not first_dfn and has_dfn_hit and not _term_ok_near(comments, first_line):
                    add("E_TERM_ORDER", f"{term!r} used before its <dfn>", first_line)
        elif page.index < file_index[def_file]:
            for line, dfn in hits_all:
                if not dfn and not _term_ok_near(comments, line):
                    add("E_TERM_EARLY", f"{term!r} used before its defining page", line)
                    break


def _check_provenance(article: Node, comments, book: Book, add) -> None:
    items = article.text_items(PROV_EXCLUDE, PROV_EXCLUDE_TAGS)
    for text, line, _dfn, in_prov in items:
        if in_prov or not has_numeric_claim(text):
            continue
        if _prov_ok_near(comments, line):
            continue
        fsid = _prov_fs_near(comments, line)
        if fsid is None:
            add("E_PROV", f"numeric claim without prov annotation: {text.strip()[:60]!r}", line)
        elif fsid not in book.sources:
            add("E_PROV_FS", f"prov names unknown source {fsid!r}", line)


def _check_asides(article: Node, book: Book, add) -> None:
    takeaways = article.find("aside", class_="takeaways")
    if takeaways is None:
        add("E_TAKEAWAY_MISSING", "aside.takeaways missing")
    else:
        count = len(takeaways.find_all("li"))
        if not 3 <= count <= 5:
            add("E_TAKEAWAY_COUNT", f"{count} takeaway items, want 3-5")
    sources = article.find("footer", class_="sources")
    if sources is None:
        add("E_SOURCES_MISSING", "footer.sources missing")
        return
    items = [li for li in sources.find_all("li") if li.attrs.get("data-fs")]
    if len(items) < 2:
        add("E_SOURCES_COUNT", f"{len(items)} source items, want at least 2")
    for li in items:
        fsid = li.attrs.get("data-fs", "")
        if fsid not in book.sources:
            add("E_SOURCES_FS", f"unknown source id {fsid!r}", li.line)


def check_content(
    page: PageSpec, root: Node, comments: list[tuple[int, str]], book: Book
) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, line: int = 0) -> None:
        issues.append(Issue(page.file, code, message, line))

    articles = root.find_all("article")
    article = articles[0] if articles else root
    _check_word_count(article, book, add)
    _check_verses(article, page, book, add)
    _check_dfns(article, page, add)
    _check_terms(article, page, book, comments, add)
    _check_provenance(article, comments, book, add)
    _check_asides(article, book, add)
    return issues

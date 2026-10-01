# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Content gate for the book "What Krishna Said".

Usage:
  python3 tools/check.py                     # all manifest pages without TODO- + index
  python3 tools/check.py 11-ch02-sage.html   # explicit pages (checked even with TODO-)
  python3 tools/check.py --selftest          # fixture selftest (valid clean, seeds caught)
  python3 tools/check.py --root DIR          # alternate book root (used by selftest)

Exit code 0 = clean, 1 = issues found.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checker.dom import parse_html
from checker.model import Book, Issue, PageSpec, load_book
from checker.rules_content import check_content
from checker.rules_structure import check_index, check_structure

BOOK_ROOT = Path(__file__).resolve().parent.parent

SEEDS: dict[str, set[str]] = {
    "02-broken.html": {
        "E_TITLE", "E_SKIP", "E_TOPBAR", "E_MAIN", "E_TOC_CURRENT", "E_TOC_LINKS",
        "E_KICKER", "E_H1", "E_H1_MULTI", "E_LEDE", "E_BRIDGE", "E_NAV_PREV",
        "E_NAV_NEXT", "E_SCRIPT", "E_STYLESHEET", "E_PRE", "E_IMG", "E_SVG_ROLE",
        "E_SVG_VIEWBOX", "E_EXTERNAL", "E_INTERNAL_LINK", "E_NO_TODO", "E_WORD_LOW",
        "E_VERSE_REGISTRY", "E_VERSE_ALLOWED", "E_VERSE_CAPTION", "E_VERSE_IAST",
        "E_VERSE_GLOSS", "E_VERSE_NOTE", "E_VERSE_MISSING", "E_DFN_NOT_PLANNED",
        "E_DFN_MISSING", "E_DFN_DUP", "E_TERM_EARLY", "E_TERM_ORDER", "E_PROV",
        "E_PROV_FS", "E_TAKEAWAY_COUNT", "E_SOURCES_COUNT", "E_SOURCES_FS",
    },
    "04-broken2.html": {
        "E_TOC_MISSING", "E_WORD_HIGH", "E_TAKEAWAY_MISSING", "E_SOURCES_MISSING",
    },
    "index.html": {"E_INDEX_TITLE", "E_INDEX_LINKS", "E_INDEX_EXTERNAL"},
}


def check_page(book: Book, path: Path, page: PageSpec) -> list[Issue]:
    raw = path.read_text(encoding="utf-8")
    root, comments = parse_html(raw)
    issues = check_structure(page, root, raw, book)
    issues.extend(check_content(page, root, comments, book))
    return issues


def run(
    book_root: Path, files: list[str] | None = None
) -> tuple[list[Issue], list[str], list[str]]:
    """Check pages; return (issues, checked, skipped-by-TODO)."""
    book = load_book(book_root)
    skipped: list[str] = []
    if files is None:
        files = []
        for page in book.pages:
            raw = (book_root / page.file).read_text(encoding="utf-8")
            (skipped if "TODO-" in raw else files).append(page.file)
    issues: list[Issue] = []
    checked: list[str] = []
    for fname in files:
        page = book.page_by_file(fname)
        if page is None:
            issues.append(Issue(fname, "E_NOT_IN_MANIFEST", "file not in manifest", 0))
            continue
        checked.append(fname)
        issues.extend(check_page(book, book_root / fname, page))
    index_path = book_root / "index.html"
    if index_path.exists():
        raw = index_path.read_text(encoding="utf-8")
        root, _comments = parse_html(raw)
        issues.extend(check_index(root, raw, book))
    return issues, checked, skipped


def report(issues: list[Issue], checked: list[str], skipped: list[str]) -> None:
    by_file: dict[str, list[Issue]] = {}
    for issue in issues:
        by_file.setdefault(issue.file, []).append(issue)
    for fname, file_issues in by_file.items():
        print(f"== {fname} ==")
        for issue in sorted(file_issues, key=lambda i: (i.line, i.code)):
            loc = f"line {issue.line}: " if issue.line else ""
            print(f"  [{issue.code}] {loc}{issue.message}")
    print(
        f"checked {len(checked)} pages + index, "
        f"skipped {len(skipped)} (TODO), {len(issues)} issues"
    )


def run_selftest() -> int:
    fixtures = BOOK_ROOT / "tools" / "fixtures"
    failures: list[str] = []
    book = load_book(fixtures)

    valid_page = book.page_by_file("01-valid.html")
    assert valid_page is not None
    valid_issues = check_page(book, fixtures / "01-valid.html", valid_page)
    if valid_issues:
        failures.append(
            f"01-valid.html should be clean, got {sorted({i.code for i in valid_issues})}"
        )

    for fname, codes in SEEDS.items():
        if fname == "index.html":
            raw = (fixtures / fname).read_text(encoding="utf-8")
            root, _comments = parse_html(raw)
            issues = check_index(root, raw, book)
        else:
            page = book.page_by_file(fname)
            assert page is not None
            issues = check_page(book, fixtures / fname, page)
        produced = {i.code for i in issues}
        for code in sorted(codes):
            if code not in produced:
                failures.append(f"{fname}: seeded {code} not caught")

    _issues, checked, skipped = run(fixtures)
    if "03-todo.html" not in skipped:
        failures.append("03-todo.html not skipped by default selection")
    if "01-valid.html" not in checked:
        failures.append("01-valid.html not selected by default run")

    if failures:
        print("SELFTEST FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    total = sum(len(codes) for codes in SEEDS.values())
    print(
        f"SELFTEST PASSED: valid page clean, {total} seeded errors all caught, "
        "TODO-skip works"
    )
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return run_selftest()
    root = BOOK_ROOT
    positional: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--root":
            root = Path(argv[index + 1])
            index += 2
            continue
        positional.append(arg)
        index += 1
    files = positional if positional else None
    issues, checked, skipped = run(root, files)
    report(issues, checked, skipped)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

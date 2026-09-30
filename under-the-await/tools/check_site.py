#!/usr/bin/env python3
# allow: SIZE_OK — spec mandates a single self-contained checker file (tools/check_site.py).
"""Static-site QA checker for the "Under the Await" Tokio tutorial site.

Read-only: never mutates site files. Python 3.10, stdlib only.

Checks:
  1 structure  doctype, html lang, meta charset, meta viewport, one h1,
               body data-page == manifest id == path-derived id
  2 manifest   discovered pages listed, files exist (else PENDING, error
               under --strict), no duplicate ids, id/file consistency
  3 links      internal hrefs resolve, external http(s) <a> only on p05-06,
               href="#" warning
  4 offline    no https?://, fetch(, XMLHttpRequest, @import, on* handlers
               in pages + templates/page.html + assets/style.css + main.js
  5 code       pre>code needs class="language-X", X in allowlist;
               >30-line blocks warn
  6 svg        aria-hidden="true" OR (role="img" AND <title>)
  7 words      content pages: < min-words or > 2400 prose words warn
               (index exempt from the minimum)
  8 terms      terms.json terms used on a page earlier than defined_in warn
  9 fs         numeric claims with units need an "fs:" comment within 10 lines

Exit codes: 0 no errors, 1 at least one error, 2 invocation/manifest failure.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator

MANIFEST_START = "/* PAGES-MANIFEST-START */"
MANIFEST_END = "/* PAGES-MANIFEST-END */"
ALLOWED_LANGUAGES = frozenset(
    {"rust", "c", "javascript", "python", "bash", "plaintext", "go", "java"}
)
EXTERNAL_LINK_PAGE = "p05-06"
MAX_CODE_LINES = 30
MAX_WORDS = 2400
FS_WINDOW = 10
TERM_OK_WINDOW = 10
EXCLUDED_TAGS = frozenset(
    {"head", "script", "style", "pre", "code", "svg", "nav", "title"}
)
CHECK_ORDER = (
    "structure",
    "manifest",
    "links",
    "offline",
    "code",
    "svg",
    "words",
    "terms",
    "fs",
)
CHECK_TITLES = {
    "structure": "CHECK 1 — structure",
    "manifest": "CHECK 2 — manifest consistency",
    "links": "CHECK 3 — links",
    "offline": "CHECK 4 — offline purity",
    "code": "CHECK 5 — code blocks",
    "svg": "CHECK 6 — svg accessibility",
    "words": "CHECK 7 — word count",
    "terms": "CHECK 8 — term discipline",
    "fs": "CHECK 9 — fs heuristic (numeric claims need fs: sources)",
}

PART_DIR_RE = re.compile(r"^\d{2}-")
PAGE_PATH_RE = re.compile(r"^(\d{2})-[^/]+/(\d{2})-[^/]+\.html$")
LANG_CLASS_RE = re.compile(r"(?:^|\s)language-([\w-]+)")
ON_ATTR_RE = re.compile(r"^on[a-z]+$")
FS_CLAIM_RE = re.compile(
    r"\d[\d,._]*\s*(?:ms|[µμ]s|us|ns|s|bytes?|KB|MB|GB|threads?|cores?|%"
    r"|levels?|slots?|ops?)(?![A-Za-z])"
)
OFFLINE_REGEXES = tuple(
    re.compile(p) for p in ("https?://", r"fetch\(", "XMLHttpRequest", "@import")
)


class FatalError(Exception):
    """Invocation-level failure (bad manifest, bad terms ledger, bad args)."""


@dataclass(frozen=True, slots=True)
class Issue:
    check: str
    severity: str
    page: str
    line: int | None
    message: str


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    id: str
    file: str
    title: str = ""


@dataclass(frozen=True, slots=True)
class TermRule:
    pattern: str
    defined_in: str
    regex: re.Pattern[str]


@dataclass
class Link:
    href: str
    line: int


@dataclass
class CodeBlock:
    line: int
    code_seen: bool = False
    language: str | None = None
    text: str = ""


@dataclass
class SvgNode:
    line: int
    aria_hidden: bool
    role: str | None
    has_title: bool = False


@dataclass
class PageData:
    path: Path
    rel: str
    derived_id: str
    text: str = ""
    doctype: bool = False
    html_lang: str | None = None
    has_charset: bool = False
    has_viewport: bool = False
    h1_count: int = 0
    h1_first_line: int | None = None
    body_data_page: str | None = None
    body_line: int | None = None
    links: list[Link] = field(default_factory=list)
    event_handlers: list[tuple[str, int]] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    svgs: list[SvgNode] = field(default_factory=list)
    fs_comment_lines: list[int] = field(default_factory=list)
    term_ok_lines: list[int] = field(default_factory=list)
    prose: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class CheckResult:
    issues: list[Issue]
    pending: list[ManifestEntry]
    entries: list[ManifestEntry]
    pages: list[PageData]

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


# ---------------------------------------------------------------- parsing


class PageParser(HTMLParser):
    """Single-pass collector for one page; fills a PageData with line numbers."""

    def __init__(self, data: PageData) -> None:
        super().__init__(convert_charrefs=True)
        self.data = data
        self.excluded: dict[str, int] = {}
        self.pre_depth = 0
        self.block: CodeBlock | None = None
        self.svg_stack: list[SvgNode] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.data.doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        amap = dict(attrs)
        if tag == "html" and self.data.html_lang is None:
            self.data.html_lang = amap.get("lang")
        elif tag == "meta":
            if amap.get("charset") is not None:
                self.data.has_charset = True
            content = (amap.get("content") or "").lower()
            equiv = (amap.get("http-equiv") or "").lower()
            if equiv == "content-type" and "charset=" in content:
                self.data.has_charset = True
            if (amap.get("name") or "").lower() == "viewport":
                self.data.has_viewport = True
        elif tag == "h1":
            self.data.h1_count += 1
            if self.data.h1_first_line is None:
                self.data.h1_first_line = line
        elif tag == "body":
            self.data.body_data_page = amap.get("data-page")
            self.data.body_line = line
        elif tag == "a":
            href = amap.get("href")
            if href is not None:
                self.data.links.append(Link(href=href, line=line))
        if tag == "pre":
            self.pre_depth += 1
            self.block = CodeBlock(line=line)
        elif tag == "code" and self.block is not None and not self.block.code_seen:
            self.block.code_seen = True
            match = LANG_CLASS_RE.search(amap.get("class") or "")
            self.block.language = match.group(1) if match else None
        elif tag == "svg":
            self.svg_stack.append(
                SvgNode(
                    line=line,
                    aria_hidden=amap.get("aria-hidden") == "true",
                    role=amap.get("role"),
                )
            )
        elif tag == "title" and self.svg_stack:
            self.svg_stack[-1].has_title = True
        for name, _ in attrs:
            if ON_ATTR_RE.match(name):
                self.data.event_handlers.append((name, line))
        if tag in EXCLUDED_TAGS:
            self.excluded[tag] = self.excluded.get(tag, 0) + 1

    def handle_endtag(self, tag: str) -> None:
        if tag in EXCLUDED_TAGS:
            self.excluded[tag] = max(0, self.excluded.get(tag, 0) - 1)
        if tag == "pre":
            self.pre_depth = max(0, self.pre_depth - 1)
            if self.pre_depth == 0 and self.block is not None:
                if self.block.code_seen:
                    self.data.code_blocks.append(self.block)
                self.block = None
        elif tag == "svg" and self.svg_stack:
            self.data.svgs.append(self.svg_stack.pop())

    def handle_data(self, chunk: str) -> None:
        if self.block is not None:
            self.block.text += chunk
        if not any(self.excluded.values()):
            self.data.prose.append((chunk, self.getpos()[0]))

    def handle_comment(self, text: str) -> None:
        if "fs:" in text:
            self.data.fs_comment_lines.append(self.getpos()[0])
        if "term-ok:" in text:
            self.data.term_ok_lines.append(self.getpos()[0])


def derived_id_for(rel: str) -> str | None:
    if rel == "index.html":
        return "index"
    match = PAGE_PATH_RE.match(rel)
    return f"p{match.group(1)}-{match.group(2)}" if match else None


def parse_page(path: Path, site_root: Path) -> PageData:
    rel = path.relative_to(site_root).as_posix()
    data = PageData(path=path, rel=rel, derived_id=derived_id_for(rel) or "")
    data.text = path.read_text(encoding="utf-8", errors="replace")
    parser = PageParser(data)
    parser.feed(data.text)
    parser.close()
    return data


def discover_pages(site_root: Path) -> list[Path]:
    pages: list[Path] = []
    index = site_root / "index.html"
    if index.is_file():
        pages.append(index)
    for entry in sorted(site_root.iterdir()):
        if entry.is_dir() and PART_DIR_RE.match(entry.name):
            pages.extend(sorted(entry.glob("*.html")))
    return pages


def load_manifest(site_root: Path) -> list[ManifestEntry]:
    main_js = site_root / "assets" / "main.js"
    try:
        text = main_js.read_text(encoding="utf-8")
    except OSError as exc:
        raise FatalError(f"cannot read {main_js}: {exc}") from exc
    try:
        start = text.index(MANIFEST_START) + len(MANIFEST_START)
        end = text.index(MANIFEST_END)
    except ValueError as exc:
        raise FatalError(f"manifest markers not found in {main_js}") from exc
    try:
        raw = json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        raise FatalError(f"manifest JSON invalid in {main_js}: {exc}") from exc
    if not isinstance(raw, list):
        raise FatalError("manifest is not a JSON array")
    entries: list[ManifestEntry] = []
    for i, item in enumerate(raw):
        ok = (
            isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and isinstance(item.get("file"), str)
        )
        if not ok:
            raise FatalError(f"manifest entry #{i} needs string 'id' and 'file'")
        title = item.get("title", "")
        entries.append(
            ManifestEntry(
                id=item["id"], file=item["file"],
                title=title if isinstance(title, str) else "",
            )
        )
    return entries


def load_terms() -> list[TermRule]:
    terms_path = Path(__file__).resolve().parent / "terms.json"
    try:
        raw = json.loads(terms_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalError(f"cannot read term ledger {terms_path}: {exc}") from exc
    if not isinstance(raw, list):
        raise FatalError("terms.json is not a JSON array")
    rules: list[TermRule] = []
    for i, item in enumerate(raw):
        ok = (
            isinstance(item, dict)
            and isinstance(item.get("term") or item.get("pattern"), str)
            and isinstance(item.get("defined_in"), str)
        )
        if not ok:
            raise FatalError(f"terms.json entry #{i} needs term/pattern + defined_in")
        pattern = item.get("pattern") or item["term"]
        try:
            regex = re.compile(r"(?<!\w)(?:" + pattern + r")(?!\w)", re.IGNORECASE)
        except re.error as exc:
            raise FatalError(f"terms.json entry #{i} regex invalid: {exc}") from exc
        rules.append(TermRule(pattern=pattern, defined_in=item["defined_in"], regex=regex))
    # Longest pattern first: the most specific term claims a span, suppressing
    # shorter overlapping terms (e.g. "non-blocking" beats "blocking").
    rules.sort(key=lambda r: len(r.pattern), reverse=True)
    return rules


# ---------------------------------------------------------------- checks


def check_structure(page: PageData, manifest_id: str | None) -> list[Issue]:
    issues: list[Issue] = []
    add = page.rel
    if not page.doctype:
        issues.append(Issue("structure", "error", add, 1, "missing <!DOCTYPE html>"))
    if not page.html_lang:
        issues.append(Issue("structure", "error", add, None, "<html> has no lang attribute"))
    if not page.has_charset:
        issues.append(Issue("structure", "error", add, None, "missing <meta charset=...>"))
    if not page.has_viewport:
        issues.append(Issue("structure", "error", add, None, 'missing <meta name="viewport">'))
    if page.h1_count != 1:
        issues.append(
            Issue("structure", "error", add, page.h1_first_line,
                  f"expected exactly one <h1>, found {page.h1_count}")
        )
    if page.body_data_page is None:
        issues.append(
            Issue("structure", "error", add, page.body_line,
                  "<body> has no data-page attribute")
        )
    else:
        if page.body_data_page != page.derived_id:
            issues.append(
                Issue("structure", "error", add, page.body_line,
                      f"data-page {page.body_data_page!r} != path-derived id {page.derived_id!r}")
            )
        if manifest_id is not None and page.body_data_page != manifest_id:
            issues.append(
                Issue("structure", "error", add, page.body_line,
                      f"data-page {page.body_data_page!r} != manifest id {manifest_id!r}")
            )
    return issues


def check_manifest(
    entries: list[ManifestEntry],
    pages: list[PageData],
    site_root: Path,
    strict: bool,
) -> tuple[list[Issue], list[ManifestEntry]]:
    issues: list[Issue] = []
    by_file = {e.file: e for e in entries}
    seen: dict[str, str] = {}
    for entry in entries:
        if entry.id in seen:
            issues.append(
                Issue("manifest", "error", entry.file, None,
                      f"duplicate id {entry.id!r} (first used by {seen[entry.id]})")
            )
        else:
            seen[entry.id] = entry.file
    pending = [e for e in entries if not (site_root / e.file).is_file()]
    if strict:
        for entry in pending:
            issues.append(
                Issue("manifest", "error", entry.file, None,
                      "page file missing (--strict)")
            )
    for entry in entries:
        derived = derived_id_for(entry.file)
        exists = (site_root / entry.file).is_file()
        if derived is not None and exists and derived != entry.id:
            issues.append(
                Issue("manifest", "error", entry.file, None,
                      f"id {entry.id!r} does not match path-derived id {derived!r}")
            )
    for page in pages:
        if page.rel not in by_file:
            issues.append(
                Issue("manifest", "error", page.rel, None,
                      "discovered page is not listed in the manifest")
            )
    return issues, pending


def check_links(page: PageData) -> list[Issue]:
    issues: list[Issue] = []
    page_dir = page.path.parent
    for link in page.links:
        href = link.href.strip()
        if href.startswith(("http://", "https://")):
            if page.derived_id != EXTERNAL_LINK_PAGE:
                issues.append(
                    Issue("links", "error", page.rel, link.line,
                          f"external link only allowed on {EXTERNAL_LINK_PAGE}: {href}")
                )
        elif href == "#":
            issues.append(
                Issue("links", "warning", page.rel, link.line, 'placeholder href="#"')
            )
        elif href.startswith("#"):
            continue  # same-page anchor
        else:
            target = href.split("#", 1)[0]
            if target and not (page_dir / target).is_file():
                issues.append(
                    Issue("links", "error", page.rel, link.line,
                          f"internal link target missing: {href}")
                )
    return issues


def _scan_text(text: str, rel: str) -> Iterator[Issue]:
    for lineno, line in enumerate(text.splitlines(), 1):
        for regex in OFFLINE_REGEXES:
            for match in regex.finditer(line):
                yield Issue("offline", "error", rel, lineno,
                            f"offline violation: {match.group(0)!r}")


def check_offline(pages: list[PageData], site_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for page in pages:
        issues.extend(_scan_text(page.text, page.rel))
    extras = [
        site_root / "templates" / "page.html",
        site_root / "assets" / "style.css",
        site_root / "assets" / "main.js",
    ]
    for path in extras:
        if path.is_file():
            rel = path.relative_to(site_root).as_posix()
            issues.extend(_scan_text(path.read_text(encoding="utf-8", errors="replace"), rel))
    for page in pages:
        for attr, line in page.event_handlers:
            issues.append(
                Issue("offline", "error", page.rel, line,
                      f"inline event handler attribute {attr!r}")
            )
    return issues


def check_code(page: PageData) -> list[Issue]:
    issues: list[Issue] = []
    for block in page.code_blocks:
        if block.language is None:
            issues.append(
                Issue("code", "error", page.rel, block.line,
                      "code block missing language-X class")
            )
        elif block.language not in ALLOWED_LANGUAGES:
            issues.append(
                Issue("code", "error", page.rel, block.line,
                      f"unknown code language {block.language!r}")
            )
        stripped = block.text.strip()
        nlines = stripped.count("\n") + 1 if stripped else 0
        if nlines > MAX_CODE_LINES:
            issues.append(
                Issue("code", "warning", page.rel, block.line,
                      f"code block is {nlines} lines (> {MAX_CODE_LINES})")
            )
    return issues


def check_svg(page: PageData) -> list[Issue]:
    issues: list[Issue] = []
    for svg in page.svgs:
        if svg.aria_hidden or (svg.role == "img" and svg.has_title):
            continue
        issues.append(
            Issue("svg", "error", page.rel, svg.line,
                  'svg needs aria-hidden="true" or role="img" with a <title>')
        )
    return issues


def check_words(page: PageData, min_words: int) -> list[Issue]:
    words = sum(len(chunk.split()) for chunk, _ in page.prose)
    issues: list[Issue] = []
    if page.derived_id != "index" and words < min_words:
        issues.append(
            Issue("words", "warning", page.rel, None,
                  f"only {words} prose words (minimum {min_words})")
        )
    if words > MAX_WORDS:
        issues.append(
            Issue("words", "warning", page.rel, None,
                  f"{words} prose words exceeds {MAX_WORDS}")
        )
    return issues


def check_terms(
    page: PageData, page_pos: int, entries: list[ManifestEntry], rules: list[TermRule]
) -> list[Issue]:
    if page_pos < 0:
        return []
    pos_by_id = {e.id: i for i, e in enumerate(entries)}
    issues: list[Issue] = []
    for text, line in page.prose:
        claimed: list[tuple[int, int]] = []
        for rule in rules:
            def_pos = pos_by_id.get(rule.defined_in)
            if def_pos is None:
                continue
            for match in rule.regex.finditer(text):
                span = (match.start(), match.end())
                if any(span[0] < b and a < span[1] for a, b in claimed):
                    continue
                claimed.append(span)
                if page_pos < def_pos:
                    use_line = line + text[: match.start()].count("\n")
                    near = any(
                        abs(c - use_line) <= TERM_OK_WINDOW
                        for c in page.term_ok_lines
                    )
                    if not near:
                        issues.append(
                            Issue("terms", "warning", page.rel, use_line,
                                  f"term {match.group(0)!r} used before defined "
                                  f"({rule.defined_in})")
                        )
    return issues


def check_fs(page: PageData) -> list[Issue]:
    issues: list[Issue] = []
    for text, line in page.prose:
        for match in FS_CLAIM_RE.finditer(text):
            claim_line = line + text[: match.start()].count("\n")
            near = any(abs(c - claim_line) <= FS_WINDOW for c in page.fs_comment_lines)
            if not near:
                issues.append(
                    Issue("fs", "warning", page.rel, claim_line,
                          f"numeric claim {match.group(0)!r} has no fs: comment "
                          f"within {FS_WINDOW} lines")
                )
    return issues


# ---------------------------------------------------------------- driver


def run_checks(site_root: Path, min_words: int, strict: bool) -> CheckResult:
    site_root = site_root.resolve()
    entries = load_manifest(site_root)
    rules = load_terms()
    pages = [parse_page(p, site_root) for p in discover_pages(site_root)]
    by_file = {e.file: e for e in entries}
    pos_by_id = {e.id: i for i, e in enumerate(entries)}
    issues: list[Issue] = []
    for page in pages:
        entry = by_file.get(page.rel)
        issues.extend(check_structure(page, entry.id if entry else None))
    manifest_issues, pending = check_manifest(entries, pages, site_root, strict)
    issues.extend(manifest_issues)
    for page in pages:
        issues.extend(check_links(page))
    issues.extend(check_offline(pages, site_root))
    for page in pages:
        issues.extend(check_code(page))
        issues.extend(check_svg(page))
        issues.extend(check_words(page, min_words))
        entry = by_file.get(page.rel)
        page_pos = pos_by_id[entry.id] if entry else -1
        if page.derived_id != "index":  # roadmap prose legitimately teases terms
            issues.extend(check_terms(page, page_pos, entries, rules))
        issues.extend(check_fs(page))
    return CheckResult(issues=issues, pending=pending, entries=entries, pages=pages)


def _clip(text: str, limit: int = 90) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def print_report(result: CheckResult, site_root: Path, min_words: int) -> None:
    print(f"check_site: {site_root}")
    print(
        f"pages discovered: {len(result.pages)}  "
        f"manifest entries: {len(result.entries)}  min-words: {min_words}"
    )
    for check in CHECK_ORDER:
        issues = [i for i in result.issues if i.check == check]
        if not issues:
            continue
        print(f"\n== {CHECK_TITLES[check]} ==")
        by_page: dict[str, list[Issue]] = {}
        for issue in issues:
            by_page.setdefault(issue.page, []).append(issue)
        for page, page_issues in by_page.items():
            print(f"  {page}")
            for issue in page_issues:
                loc = f"line {issue.line}: " if issue.line is not None else ""
                print(f"    {loc}{issue.severity}: {_clip(issue.message)}")
    print(f"\nsummary: {result.error_count} error(s), {result.warning_count} warning(s)")
    if result.pending:
        print("pending pages (not written yet):")
        for entry in result.pending:
            suffix = f" ({entry.title})" if entry.title else ""
            print(f"  {entry.id} — {entry.file}{suffix}")


def run_fixtures() -> int:
    tools_dir = Path(__file__).resolve().parent
    valid_root = tools_dir / "tests" / "fixtures" / "valid"
    broken_root = tools_dir / "tests" / "fixtures" / "broken"
    results: list[bool] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        results.append(ok)
        suffix = f" — {detail}" if detail and not ok else ""
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

    for label, root in (("valid", valid_root), ("broken", broken_root)):
        print(f"\n===== fixtures: {label} ({root}) =====")
        try:
            result = run_checks(root, 5, False)
        except FatalError as exc:
            print(f"fatal: {exc}")
            record(f"{label}: checker runs", False, str(exc))
            continue
        print_report(result, root, 5)
        code = 0 if result.error_count == 0 else 1
        print(f"[{label}] exit code would be: {code}")
        if label == "valid":
            record("valid: exit code 0", code == 0, f"got {code}")
            record("valid: zero errors", result.error_count == 0,
                   f"{result.error_count} error(s)")
            record("valid: zero terms warnings",
                   not any(i.check == "terms" and i.severity == "warning"
                           for i in result.issues),
                   "unexpected terms warning(s)")
        else:
            record("broken: exit code 1", code == 1, f"got {code}")
            got = {i.check for i in result.issues if i.severity == "error"}
            need = {"structure", "links", "offline", "code", "svg"}
            record("broken: errors cover structure/links/offline/code/svg",
                   need <= got, f"missing {sorted(need - got)}")
            record("broken: at least one terms warning",
                   any(i.check == "terms" and i.severity == "warning"
                       for i in result.issues))
    print()
    if results and all(results):
        print("fixtures: ALL PASS")
        return 0
    print("fixtures: FAILED")
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="QA checker for the Under the Await tutorial site"
    )
    parser.add_argument(
        "site_root", nargs="?", default=None,
        help="site root (default: parent of tools/)"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="treat pending (missing) manifest pages as errors"
    )
    parser.add_argument(
        "--fixtures", action="store_true", help="run the built-in self-test"
    )
    parser.add_argument(
        "--min-words", type=int, default=1200,
        help="minimum prose words per content page (default 1200)"
    )
    args = parser.parse_args(argv)
    if args.min_words <= 0:
        print("error: --min-words must be a positive integer", file=sys.stderr)
        return 2
    if args.fixtures:
        return run_fixtures()
    root = (
        Path(args.site_root).resolve()
        if args.site_root
        else Path(__file__).resolve().parent.parent
    )
    if not root.is_dir():
        print(f"error: site root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        result = run_checks(root, args.min_words, args.strict)
    except FatalError as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        return 2
    print_report(result, root, args.min_words)
    return 0 if result.error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

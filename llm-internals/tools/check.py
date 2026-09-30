#!/usr/bin/env python3
"""
Contract checker for the LLM Internals teaching site.

Enforces, per page:
  E_MANIFEST   manifest completeness, orphan pages, term-ledger integrity
  E_STRUCT     document structure (lang, charset, viewport, data-page, title,
               single h1, main, nav, prev/next chain)
  E_TAKEAWAYS  takeaways aside present with 3-5 items (content + index pages)
  E_LINK       internal links and anchors resolve
  E_EXTERNAL   offline purity: no external URLs except on the links page
  E_CODELANG   code blocks carry an allowed language- class
  E_CODELEN    code blocks are at most 30 lines
  E_SVG        svg accessibility (role="img"+<title> or aria-hidden) + viewBox
  E_WORDS      per-page prose word window from manifest
  E_TERM       term-before-use against terms.json, honoring <!-- term-ok --> escapes
  E_PROV       numeric claims carry provenance within +/-10 lines;
               prov data-src files exist; content pages carry >= 2 prov marks
  E_GLOSSARY   glossary defines every ledger term and links its defining page

Stdlib only. Usage:
  python3 tools/check.py [--root DIR] [--partial] [page.html ...]

--partial: manifest pages that do not exist yet are skipped (missing internal
links to those pages are tolerated); orphan detection still runs on full runs.
File filters imply a partial, single-page run (no orphan detection).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

VERSION = "1.0"

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}
# Text inside these tags never counts as prose/terms/numbers.
TERM_EXCL_TAGS = {"nav", "pre", "code", "svg", "title", "style", "script", "textarea"}
# Elements with these classes are navigation chrome or citations, not prose.
TERM_EXCL_CLASSES = {"toc", "pager", "prov"}
# Panels that restate already-cited claims (takeaways) skip number provenance.
PROV_EXCL_CLASSES = {"takeaways"}

NUM_RE = re.compile(r"(?<![A-Za-z0-9])\d[\d,\.]*(?![A-Za-z])")
WORD_RE = re.compile(r"[A-Za-z0-9']+")


class Scan(HTMLParser):
    """One pass over a page collecting everything the checks need."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        # collected
        self.word_count = 0
        self.words = []            # (line, word)
        self.nums = []             # (line, numstr)
        self.ids = set()
        self.links = []            # (line, href, rel, in_nav)
        self.srcs = []             # (line, url)
        self.pres = []             # dicts
        self.svgs = []             # dicts
        self.provs = []            # (line, data_src)
        self.events = []           # ("dt", line, id) | ("link", line, href)
        self.takeaway_lis = 0
        self.has_takeaways = False
        self.h1_count = 0
        self.has_main = False
        self.body_data_page = None
        self.html_lang = ""
        self.title = []
        self.term_esc = []         # lines holding <!-- term-ok ... -->
        self.prov_esc = []         # lines holding <!-- prov-ok ... -->
        # state
        self.frames = []           # [tag, term_ex, prov_ex, in_takeaways, in_nav]
        self._pre = None
        self._svg = None
        self._in_html_title = False

    # -- capture ------------------------------------------------------------

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        d = {k: (v if v is not None else "") for k, v in attrs}
        cls = set((d.get("class") or "").split())
        term_ex = (tag in TERM_EXCL_TAGS
                   or bool(TERM_EXCL_CLASSES & cls)
                   or "data-term-ok" in d)
        prov_ex = term_ex or bool(PROV_EXCL_CLASSES & cls)
        in_ta = tag == "aside" and "takeaways" in cls
        if in_ta:
            self.has_takeaways = True
        in_nav = tag == "nav"
        if tag not in VOID_TAGS:
            self.frames.append([tag, term_ex, prov_ex, in_ta, in_nav])

        if tag == "html":
            self.html_lang = d.get("lang", "")
        if tag == "body":
            self.body_data_page = d.get("data-page")
        if tag == "main":
            self.has_main = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "title" and self._svg is None:
            self._in_html_title = True
        if d.get("id"):
            self.ids.add(d["id"])
        if "href" in d:
            nav_now = in_nav or any(f[4] for f in self.frames)
            self.links.append((line, d["href"], d.get("rel", ""), nav_now))
            self.events.append(("link", line, d["href"]))
        if "src" in d:
            self.srcs.append((line, d["src"]))
        if "prov" in cls and "data-src" in d:
            self.provs.append((line, d.get("data-src", "")))
        if tag == "dt":
            self.events.append(("dt", line, d.get("id", "")))
        if tag == "li" and any(f[3] for f in self.frames):
            self.takeaway_lis += 1
        if tag == "pre":
            self._pre = {"line": line, "cls": "", "has_code": False, "buf": []}
        elif self._pre is not None and tag == "code":
            self._pre["has_code"] = True
            self._pre["cls"] = d.get("class", "")
        if tag == "svg":
            self._svg = {"line": line, "role": d.get("role", ""),
                         "aria_hidden": d.get("aria-hidden", ""),
                         "viewbox": d.get("viewBox", d.get("viewbox", "")),
                         "title": False}
        elif self._svg is not None and tag == "title":
            self._svg["title"] = True

    def handle_endtag(self, tag):
        if tag == "title" and self._svg is None:
            self._in_html_title = False
        for i in range(len(self.frames) - 1, -1, -1):
            if self.frames[i][0] == tag:
                del self.frames[i:]
                break
        if tag == "pre" and self._pre is not None:
            text = "".join(self._pre["buf"])
            nlines = text.count("\n") + (1 if text.strip() else 0)
            self.pres.append({"line": self._pre["line"], "cls": self._pre["cls"],
                              "has_code": self._pre["has_code"],
                              "nlines": nlines})
            self._pre = None
        if tag == "svg" and self._svg is not None:
            self.svgs.append(self._svg)
            self._svg = None

    def handle_data(self, data):
        if self._in_html_title:
            self.title.append(data)
            return
        if self._pre is not None:
            self._pre["buf"].append(data)
            return
        term_ex = any(f[1] for f in self.frames)
        prov_ex = any(f[2] for f in self.frames)
        line = self.getpos()[0]
        if not term_ex:
            self.word_count += len(data.split())
            for w in WORD_RE.findall(data):
                self.words.append((line, w))
        if not prov_ex:
            for m in NUM_RE.finditer(data):
                s = m.group().rstrip(".,")
                if s:
                    self.nums.append((line, s))

    def handle_comment(self, data):
        line = self.getpos()[0]
        t = data.strip()
        if t.startswith("term-ok"):
            self.term_esc.append(line)
        elif t.startswith("prov-ok"):
            self.prov_esc.append(line)


# -- errors -------------------------------------------------------------------


class Errors:
    def __init__(self):
        self.items = []  # (page, code, line, msg)

    def add(self, page, code, msg, line=None):
        self.items.append((page, code, line, msg))


# -- helpers ------------------------------------------------------------------


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def scan_file(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    s = Scan()
    s.feed(raw)
    s.close()
    return s, raw


def find_term_hits(words, term):
    """Lines where `term` (or its plural) occurs as a whole-word sequence."""
    tw = [w.lower() for w in WORD_RE.findall(term)]
    hits = []
    n = len(words)
    L = len(tw)
    for i in range(n - L + 1):
        ok = True
        for j, want in enumerate(tw):
            have = words[i + j][1].lower()
            last = j == L - 1
            if have == want or (last and (have == want + "s" or have == want + "es")):
                continue
            ok = False
            break
        if ok:
            hits.append(words[i][0])
    return hits


def page_kind(fname, manifest):
    if fname == manifest.get("glossary_page"):
        return "glossary"
    if fname == manifest.get("external_links_page"):
        return "links"
    pages = manifest.get("pages", [])
    if pages and pages[0]["file"] == fname:
        return "index"
    return "content"


# -- per-page checks -----------------------------------------------------------


def check_url(errors, fname, line, url, root, same_ids, ext_ok, partial,
              manifest_files, ids_cache):
    u = (url or "").strip()
    if not u:
        return
    low = u.lower()
    if low.startswith(("http://", "https://", "//")):
        if not ext_ok:
            errors.add(fname, "E_EXTERNAL",
                       f"external URL {u!r} (only the links page may link out)", line)
        return
    if low.startswith(("mailto:", "tel:")):
        return
    if low.startswith(("data:", "javascript:")):
        errors.add(fname, "E_EXTERNAL", f"non-static URL {u!r}", line)
        return
    if u.startswith("#"):
        frag = u[1:]
        if frag and frag not in (same_ids or set()):
            errors.add(fname, "E_LINK", f"anchor #{frag} not found on this page", line)
        return
    path_part, _, frag = u.partition("#")
    target = os.path.normpath(os.path.join(root, path_part))
    if not os.path.exists(target):
        if partial and path_part in manifest_files:
            return  # page not written yet (wave in progress)
        errors.add(fname, "E_LINK", f"link target {path_part!r} does not exist", line)
        return
    if frag and target.endswith(".html"):
        key = os.path.basename(path_part)
        tids = ids_cache.get(key)
        if tids is None:
            try:
                tscan, _ = scan_file(target)
                tids = tscan.ids
            except Exception:
                tids = set()
            ids_cache[key] = tids
        if frag not in tids:
            errors.add(fname, "E_LINK", f"anchor #{frag} not found in {path_part}", line)


def check_chain(errors, fname, which, expected, found):
    if expected is None:
        if found:
            errors.add(fname, "E_STRUCT",
                       f"unexpected rel={which} link {found[0]!r} (no {which} page in manifest)")
        return
    good = [h for h in found if h == expected]
    if not good:
        errors.add(fname, "E_STRUCT",
                   f"missing rel={which} link to {expected!r} (found {found or 'none'})")
    bad = [h for h in found if h != expected]
    for h in bad:
        errors.add(fname, "E_STRUCT",
                   f"rel={which} link points to {h!r}, expected {expected!r}")


def check_page(root, fname, scan, raw, meta, manifest, terms, idx, errors,
               partial):
    s = scan
    kind = "orphan" if meta is None else page_kind(fname, manifest)
    manifest_files = {p["file"] for p in manifest.get("pages", [])}
    ids_cache = {}

    # -- E_STRUCT ------------------------------------------------------------
    if (s.html_lang or "").lower() != "en":
        errors.add(fname, "E_STRUCT", f'<html lang="en"> missing or wrong (got {s.html_lang!r})')
    if not re.search(r"<meta[^>]*charset\s*=\s*[\"']?utf-8", raw, re.I):
        errors.add(fname, "E_STRUCT", 'missing <meta charset="utf-8">')
    if not re.search(r"<meta[^>]*name\s*=\s*[\"']viewport[\"']", raw, re.I):
        errors.add(fname, "E_STRUCT", "missing viewport meta tag")
    if meta is not None:
        if s.body_data_page != meta.get("id"):
            errors.add(fname, "E_STRUCT",
                       f'data-page {s.body_data_page!r} does not match manifest id {meta.get("id")!r}')
        title = "".join(s.title).strip()
        if meta.get("title") and meta["title"] not in title:
            errors.add(fname, "E_STRUCT",
                       f"title {title!r} does not contain manifest title {meta['title']!r}")
        i = idx[fname]
        pages = manifest["pages"]
        exp_prev = pages[i - 1]["file"] if i > 0 else None
        exp_next = pages[i + 1]["file"] if i + 1 < len(pages) else None
        prev_hrefs = [h for (_, h, rel, _) in s.links if "prev" in rel]
        next_hrefs = [h for (_, h, rel, _) in s.links if "next" in rel]
        check_chain(errors, fname, "prev", exp_prev, prev_hrefs)
        check_chain(errors, fname, "next", exp_next, next_hrefs)
    if s.h1_count != 1:
        errors.add(fname, "E_STRUCT", f"expected exactly one <h1>, found {s.h1_count}")
    if not s.has_main:
        errors.add(fname, "E_STRUCT", "missing <main> element")
    nav_links = [h for (_, h, _, in_nav) in s.links if in_nav]
    if len(nav_links) < 3:
        errors.add(fname, "E_STRUCT",
                   f"nav must contain at least 3 internal links, found {len(nav_links)}")

    # -- E_TAKEAWAYS ----------------------------------------------------------
    if kind in ("content", "index"):
        if not s.has_takeaways:
            errors.add(fname, "E_TAKEAWAYS", "missing takeaways aside")
        elif not (3 <= s.takeaway_lis <= 5):
            errors.add(fname, "E_TAKEAWAYS",
                       f"takeaways must have 3-5 items, found {s.takeaway_lis}")

    # -- E_LINK / E_EXTERNAL --------------------------------------------------
    ext_ok = (fname == manifest.get("external_links_page"))
    for (line, href, rel, _) in s.links:
        check_url(errors, fname, line, href, root, s.ids, ext_ok, partial,
                  manifest_files, ids_cache)
    for (line, url) in s.srcs:
        check_url(errors, fname, line, url, root, None, ext_ok, partial,
                  manifest_files, ids_cache)

    # -- E_CODELANG / E_CODELEN ------------------------------------------------
    allowed = set(manifest.get("allowed_code_languages", ["python", "text"]))
    for pre in s.pres:
        if not pre["has_code"]:
            errors.add(fname, "E_CODELANG", "code block missing <code> child", pre["line"])
            continue
        m = re.search(r"language-([\w+-]+)", pre["cls"])
        if not m:
            errors.add(fname, "E_CODELANG", "code block missing language- class", pre["line"])
        elif m.group(1) not in allowed:
            errors.add(fname, "E_CODELANG",
                       f"code language {m.group(1)!r} not allowed (allowed: {sorted(allowed)})",
                       pre["line"])
        if pre["nlines"] > 30:
            errors.add(fname, "E_CODELEN",
                       f"code block has {pre['nlines']} lines (max 30)", pre["line"])

    # -- E_SVG ------------------------------------------------------------------
    for sv in s.svgs:
        if not sv["viewbox"]:
            errors.add(fname, "E_SVG", "svg missing viewBox", sv["line"])
        if (sv["aria_hidden"] or "").lower() != "true":
            if not (sv["role"] == "img" and sv["title"]):
                errors.add(fname, "E_SVG",
                           'svg needs role="img" with a <title>, or aria-hidden="true"',
                           sv["line"])

    # -- E_WORDS ----------------------------------------------------------------
    if meta is not None:
        lo, hi = meta.get("word_window") or manifest.get(
            "default_word_window", [1200, 2200])
        if not (lo <= s.word_count <= hi):
            errors.add(fname, "E_WORDS",
                       f"prose word count {s.word_count} outside window [{lo}, {hi}]")

    # -- E_TERM -----------------------------------------------------------------
    if kind not in ("glossary", "links", "orphan"):
        for term, defpage in terms.items():
            if defpage not in idx:
                continue  # defining page not written yet
            if fname == defpage:
                continue
            if idx[fname] > idx[defpage]:
                continue  # usage after definition: fine
            for line in sorted(set(find_term_hits(s.words, term))):
                if any(line - 3 <= el <= line for el in s.term_esc):
                    continue  # escape hatch
                errors.add(fname, "E_TERM",
                           f"term {term!r} used before its defining page {defpage}", line)

    # -- E_PROV -------------------------------------------------------------------
    if kind != "links":  # the links page IS the citation list
        prov_lines = [pl for (pl, _) in s.provs]
        for (line, num) in s.nums:
            if any(abs(line - pl) <= 10 for pl in prov_lines):
                continue
            if any(abs(line - el) <= 10 for el in s.prov_esc):
                continue
            errors.add(fname, "E_PROV",
                       f"numeric claim {num!r} lacks provenance within 10 lines", line)
    for (pl, src) in s.provs:
        p = src.split("#")[0].strip()
        if not p or not os.path.exists(os.path.join(root, p)):
            errors.add(fname, "E_PROV", f"prov data-src {src!r} does not resolve", pl)
    if kind == "content" and len(s.provs) < 2:
        errors.add(fname, "E_PROV",
                   f"content page carries {len(s.provs)} prov marks (minimum 2)")

    # -- E_GLOSSARY -----------------------------------------------------------------
    if fname == manifest.get("glossary_page"):
        dts = [(l, i) for (t, l, i) in s.events if t == "dt"]
        links_ev = [(l, h) for (t, l, h) in s.events if t == "link"]
        for term, defpage in terms.items():
            slug = "t-" + term.replace(" ", "-")
            hit = next(((l, i) for (l, i) in dts if i == slug), None)
            if hit is None:
                errors.add(fname, "E_GLOSSARY",
                           f"glossary is missing entry {slug!r} for term {term!r}")
                continue
            dt_line = hit[0]
            next_dt = min((l for (l, _) in dts if l > dt_line), default=10 ** 9)
            hrefs = [h for (l, h) in links_ev if dt_line <= l < next_dt]
            if defpage not in hrefs:
                errors.add(fname, "E_GLOSSARY",
                           f"entry {term!r} does not link its defining page {defpage}")


# -- manifest-level checks -------------------------------------------------------


def check_manifest(root, manifest, terms, errors, partial, file_filter):
    pages = manifest.get("pages", [])
    files = [p["file"] for p in pages]
    if len(set(files)) != len(files):
        errors.add("(manifest)", "E_MANIFEST", "duplicate page files in manifest")
    ids = [p.get("id") for p in pages]
    if len(set(ids)) != len(ids):
        errors.add("(manifest)", "E_MANIFEST", "duplicate page ids in manifest")
    if not partial:
        for f in files:
            if not os.path.exists(os.path.join(root, f)):
                errors.add("(manifest)", "E_MANIFEST", f"manifest page {f!r} does not exist")
    if not file_filter:
        listed = set(files)
        for f in sorted(os.listdir(root)):
            if f.endswith(".html") and f not in listed:
                errors.add(f, "E_MANIFEST", "html file not listed in manifest (orphan)")
    for term, defpage in terms.items():
        if defpage not in files:
            errors.add("(terms)", "E_MANIFEST",
                       f"term {term!r} defines on unknown page {defpage!r}")


# -- main --------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description="LLM Internals contract checker")
    ap.add_argument("--root", default=None, help="site root (default: parent of tools/)")
    ap.add_argument("--partial", action="store_true",
                    help="tolerate not-yet-written manifest pages")
    ap.add_argument("files", nargs="*", help="optional page filters (e.g. index.html)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root or os.path.join(os.path.dirname(__file__), ".."))
    try:
        manifest = load_json(os.path.join(root, "manifest.json"))
        terms = load_json(os.path.join(root, "terms.json")).get("terms", {})
        terms = {k: v for k, v in terms.items() if not k.startswith("_")}
    except Exception as e:
        print(f"FATAL: cannot load manifest/terms from {root}: {e}", file=sys.stderr)
        return 2

    file_filter = [f for f in args.files if f]
    partial = args.partial or bool(file_filter)
    errors = Errors()
    check_manifest(root, manifest, terms, errors, partial, file_filter)

    idx = {p["file"]: i for i, p in enumerate(manifest["pages"])}
    meta = {p["file"]: p for p in manifest["pages"]}

    if file_filter:
        targets = file_filter
    else:
        targets = [p["file"] for p in manifest["pages"]]
        for f in sorted(os.listdir(root)):
            if f.endswith(".html") and f not in idx:
                targets.append(f)  # orphans: checked too (they already failed manifest)

    order = {f: i for i, f in enumerate(targets)}
    scanned = []
    for fname in targets:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            if partial:
                continue
            continue  # already reported by check_manifest
        try:
            s, raw = scan_file(path)
        except Exception as e:
            errors.add(fname, "E_STRUCT", f"cannot parse: {e}")
            continue
        scanned.append(fname)
        check_page(root, fname, s, raw, meta.get(fname), manifest, terms,
                   idx, errors, partial)

    # report
    pages_checked = len(scanned)
    if errors.items:
        by_page = {}
        for (page, code, line, msg) in errors.items:
            by_page.setdefault(page, []).append((code, line, msg))
        def sort_key(p):
            return (0, order.get(p, -1)) if p in order else ((1, -1) if p in idx else (2, 0))
        for page in sorted(by_page, key=sort_key):
            print(f"== {page}")
            for (code, line, msg) in by_page[page]:
                loc = f"line {line}: " if line else ""
                print(f"  [{code}] {loc}{msg}")
        n = len(errors.items)
        print(f"\nFAIL: {pages_checked} page(s) checked, {n} error(s)")
        return 1
    print(f"PASS: {pages_checked} page(s) checked, 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())

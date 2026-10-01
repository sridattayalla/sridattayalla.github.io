# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Typed loaders for the book's registries (manifest, verses, terms, sources)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PageSpec:
    file: str
    num: str
    title: str
    part: int
    part_name: str
    defines: tuple[str, ...]
    verses: tuple[str, ...]
    index: int


@dataclass(frozen=True, slots=True)
class Verse:
    id: str
    iast: str
    gloss: str
    note: str


@dataclass(frozen=True, slots=True)
class Issue:
    file: str
    code: str
    message: str
    line: int


@dataclass(frozen=True, slots=True)
class Book:
    pages: tuple[PageSpec, ...]
    verses: dict[str, Verse]
    terms: dict[str, str]
    sources: dict[str, str]
    words_window: tuple[int, int]

    def page_by_file(self, file: str) -> PageSpec | None:
        for page in self.pages:
            if page.file == file:
                return page
        return None


def display_iast(iast: str) -> str:
    """Registry form -> display form: pāda separator ' . | ' becomes ' | '."""
    return iast.replace(" . | ", " | ")


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def load_book(root: Path) -> Book:
    manifest = json.loads((root / "tools" / "manifest.json").read_text(encoding="utf-8"))
    verses_raw = json.loads((root / "tools" / "verses.json").read_text(encoding="utf-8"))
    terms = json.loads((root / "tools" / "terms.json").read_text(encoding="utf-8"))
    sources_raw = json.loads((root / "tools" / "sources.json").read_text(encoding="utf-8"))
    pages = tuple(
        PageSpec(
            file=entry["file"],
            num=entry["num"],
            title=entry["title"],
            part=entry["part"],
            part_name=entry["partName"],
            defines=tuple(entry.get("defines", [])),
            verses=tuple(entry.get("verses", [])),
            index=i,
        )
        for i, entry in enumerate(manifest["pages"])
    )
    page_files = {p.file for p in pages}
    for term, def_file in terms.items():
        if def_file not in page_files:
            raise ValueError(
                f"terms.json: term {term!r} references unknown page {def_file!r}"
            )
    verses = {
        key: Verse(id=v["id"], iast=v["iast"], gloss=v["gloss"], note=v["note"])
        for key, v in verses_raw.items()
    }
    sources = {fsid: entry["label"] for fsid, entry in sources_raw.items()}
    window = manifest["book"]["wordsWindow"]
    return Book(
        pages=pages,
        verses=verses,
        terms=terms,
        sources=sources,
        words_window=(window[0], window[1]),
    )

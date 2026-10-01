# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate per-page verse figure packs from tools/manifest.json + tools/verses.json.

Usage: python3 tools/make_versepacks.py

Writers copy the <figure> blocks from docs/versepacks/<page-file> VERBATIM into
their page. The IAST shown here is the display form (pāda separator ' | ');
tools/check.py applies the same transform to the registry when validating.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Final

BOOK_ROOT: Final = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class Verse:
    id: str
    iast: str
    gloss: str
    note: str


def display_iast(iast: str) -> str:
    """Registry form -> display form: ' . | ' becomes ' | '."""
    return iast.replace(" . | ", " | ")


def figure_html(verse: Verse) -> str:
    parts = [
        f'<figure class="verse" data-verse="{verse.id}">',
        f"<figcaption>Bhagavad Gita {verse.id}</figcaption>",
        f'<blockquote class="iast">{escape(display_iast(verse.iast))}</blockquote>',
        f'<p class="gloss">{escape(verse.gloss)}</p>',
    ]
    if verse.note:
        parts.append(
            f'<p class="note"><strong>Translation note</strong> {escape(verse.note)}</p>'
        )
    parts.append("</figure>")
    return "\n".join(parts)


def main() -> None:
    manifest = json.loads((BOOK_ROOT / "tools" / "manifest.json").read_text(encoding="utf-8"))
    registry_raw = json.loads((BOOK_ROOT / "tools" / "verses.json").read_text(encoding="utf-8"))
    registry = {
        key: Verse(id=v["id"], iast=v["iast"], gloss=v["gloss"], note=v["note"])
        for key, v in registry_raw.items()
    }
    out_dir = BOOK_ROOT / "docs" / "versepacks"
    out_dir.mkdir(parents=True, exist_ok=True)
    pack_count = 0
    for entry in manifest["pages"]:
        verse_ids = entry["verses"]
        if not verse_ids:
            continue
        missing = [vid for vid in verse_ids if vid not in registry]
        if missing:
            raise ValueError(f"page {entry['file']}: verses not in registry: {missing}")
        blocks = [figure_html(registry[vid]) for vid in verse_ids]
        header = (
            f"<!-- Verse pack for {entry['file']} — copy figures VERBATIM into the page.\n"
            f"     Order below is the suggested order of appearance. -->\n"
        )
        target = out_dir / entry["file"]
        target.write_text(header + "\n\n".join(blocks) + "\n", encoding="utf-8")
        pack_count += 1
    print(f"wrote {pack_count} verse packs to docs/versepacks/")


if __name__ == "__main__":
    main()

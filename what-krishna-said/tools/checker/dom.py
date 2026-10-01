# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Minimal DOM over stdlib html.parser for the book checker."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser

VOID: frozenset[str] = frozenset(
    "area base br col embed hr img input link meta param source track wbr".split()
)


@dataclass(slots=True)
class Text:
    data: str
    line: int


@dataclass(slots=True)
class Node:
    tag: str
    attrs: dict[str, str]
    children: list  # list[Node | Text]
    line: int

    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def walk(self) -> list[Node]:
        """Self and all descendant element nodes, in document order."""
        out = [self]
        for child in self.children:
            if isinstance(child, Node):
                out.extend(child.walk())
        return out

    def find_all(self, tag: str | None = None, class_: str | None = None) -> list[Node]:
        out: list[Node] = []
        for node in self.walk():
            if tag is not None and node.tag != tag:
                continue
            if class_ is not None and class_ not in node.classes():
                continue
            out.append(node)
        return out

    def find(self, tag: str | None = None, class_: str | None = None) -> Node | None:
        found = self.find_all(tag, class_)
        return found[0] if found else None

    def text_items(
        self,
        exclude_classes: frozenset[str] = frozenset(),
        exclude_tags: frozenset[str] = frozenset(),
        in_dfn: bool = False,
        in_prov: bool = False,
    ) -> list[tuple[str, int, bool, bool]]:
        """Ordered (text, line, inside_dfn, inside_prov) for non-excluded text."""
        if self.classes() & exclude_classes or self.tag in exclude_tags:
            return []
        dfn = in_dfn or self.tag == "dfn"
        prov = in_prov or "prov" in self.classes()
        out: list[tuple[str, int, bool, bool]] = []
        for child in self.children:
            if isinstance(child, Text):
                out.append((child.data, child.line, dfn, prov))
            else:
                out.extend(child.text_items(exclude_classes, exclude_tags, dfn, prov))
        return out

    def text(
        self,
        exclude_classes: frozenset[str] = frozenset(),
        exclude_tags: frozenset[str] = frozenset(),
    ) -> str:
        return "".join(item[0] for item in self.text_items(exclude_classes, exclude_tags))


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("[root]", {}, [], 0)
        self._stack: list[Node] = [self.root]
        self.comments: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {k: (v or "") for k, v in attrs}, [], self.getpos()[0])
        self._stack[-1].children.append(node)
        if tag not in VOID:
            self._stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):
            if self._stack[i].tag == tag:
                del self._stack[i:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self._stack[-1].children.append(Text(data, self.getpos()[0]))

    def handle_comment(self, data: str) -> None:
        self.comments.append((self.getpos()[0], data.strip()))


def parse_html(source: str) -> tuple[Node, list[tuple[int, str]]]:
    """Parse HTML; return (root node, comments as (line, text))."""
    builder = TreeBuilder()
    builder.feed(source)
    builder.close()
    return builder.root, builder.comments

#!/usr/bin/env python3
"""Fixture self-test helper: the entries for the named page must agree on
(line, mode, ok, expect) between a live verify.py report and the static
fixture report. This proves the static report is not lying."""
import json
import sys


def entries(path, page):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return sorted((e["line"], e["mode"], e["ok"], e.get("expect"))
                  for e in data.get("entries", []) if e.get("page") == page)


def main():
    if len(sys.argv) != 4:
        print("usage: compare_reports.py LIVE STATIC PAGE", file=sys.stderr)
        return 2
    live = entries(sys.argv[1], sys.argv[3])
    static = entries(sys.argv[2], sys.argv[3])
    if live != static:
        print(f"reports disagree for {sys.argv[3]}:")
        print(f"  live  : {live}")
        print(f"  static: {static}")
        return 1
    print(f"agree: {len(live)} entries for {sys.argv[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

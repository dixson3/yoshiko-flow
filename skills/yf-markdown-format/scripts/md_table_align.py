#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Strict GFM table aligner.

Normalizes every pipe table in a Markdown file so columns are uniform-width and
pipe-aligned, with explicit alignment markers (`:` always present):

- left   -> ``:---``
- center -> ``:--:``
- right  -> ``---:``

Existing center/right markers are preserved; columns with no marker default to
explicit left. Cell text is justified to match its column alignment. Fenced code
blocks (``` and ~~~) are left untouched. Cell display width is east-asian-aware.

Usage:
  md_table_align.py --check PATH...   # exit 1 if any file would change (lint gate)
  md_table_align.py --write PATH...   # rewrite files in place
  md_table_align.py PATH...           # print the normalized file to stdout
"""
import argparse
import sys
import unicodedata


def _w(s: str) -> int:
    """Display width: East-Asian Wide/Fullwidth count as 2, everything else 1."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad(s: str, width: int, align: str) -> str:
    gap = width - _w(s)
    if gap <= 0:
        return s
    if align == "right":
        return " " * gap + s
    if align == "center":
        left = gap // 2
        return " " * left + s + " " * (gap - left)
    return s + " " * gap  # left


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # split on unescaped pipes
    cells, buf, esc = [], "", False
    for ch in line:
        if esc:
            buf += ch
            esc = False
        elif ch == "\\":
            buf += ch
            esc = True
        elif ch == "|":
            cells.append(buf)
            buf = ""
        else:
            buf += ch
    cells.append(buf)
    return [c.strip() for c in cells]


def _is_delim(cells: list[str]) -> bool:
    if not cells:
        return False
    for c in cells:
        c = c.strip()
        if not c or not set(c) <= set(":-") or "-" not in c:
            return False
        if c.count(":") > 2 or c.strip(":").find(":") != -1:
            return False
    return True


def _align_of(cell: str) -> str:
    c = cell.strip()
    left, right = c.startswith(":"), c.endswith(":")
    if left and right:
        return "center"
    if right:
        return "right"
    return "left"


def _format_block(rows: list[list[str]], aligns: list[str]) -> list[str]:
    ncol = len(aligns)
    norm = [r + [""] * (ncol - len(r)) if len(r) < ncol else r[:ncol] for r in rows]
    widths = []
    for i in range(ncol):
        w = max((_w(r[i]) for r in norm), default=0)
        widths.append(max(w, 3))  # min 3 so delimiter has room for ':' + '-' + ':'
    out = []
    # header
    out.append("| " + " | ".join(_pad(norm[0][i], widths[i], aligns[i]) for i in range(ncol)) + " |")
    # delimiter
    dl = []
    for i in range(ncol):
        w = widths[i]
        a = aligns[i]
        if a == "center":
            dl.append(":" + "-" * (w - 2) + ":")
        elif a == "right":
            dl.append("-" * (w - 1) + ":")
        else:
            dl.append(":" + "-" * (w - 1))
    out.append("| " + " | ".join(dl) + " |")
    # body
    for r in norm[1:]:
        out.append("| " + " | ".join(_pad(r[i], widths[i], aligns[i]) for i in range(ncol)) + " |")
    return out


def transform(text: str) -> str:
    lines = text.split("\n")
    out = []
    i = 0
    in_fence = False
    fence = ""
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        # fenced code tracking
        if in_fence:
            out.append(line)
            if stripped.startswith(fence):
                in_fence = False
            i += 1
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = True
            fence = stripped[:3]
            out.append(line)
            i += 1
            continue
        # table detection: a pipe line followed by a delimiter row
        if "|" in line and i + 1 < len(lines) and "|" in lines[i + 1]:
            header = _split_row(line)
            delim = _split_row(lines[i + 1])
            if _is_delim(delim) and len(delim) == len(header):
                aligns = [_align_of(c) for c in delim]
                block = [header]
                j = i + 2
                while j < len(lines) and "|" in lines[j] and lines[j].strip():
                    block.append(_split_row(lines[j]))
                    j += 1
                indent = line[: len(line) - len(line.lstrip())]
                for fl in _format_block(block, aligns):
                    out.append(indent + fl)
                i = j
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict GFM table aligner.")
    ap.add_argument("paths", nargs="+")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="exit 1 if any file would change")
    g.add_argument("--write", action="store_true", help="rewrite files in place")
    args = ap.parse_args()

    changed = []
    for p in args.paths:
        with open(p, encoding="utf-8") as f:
            src = f.read()
        new = transform(src)
        if new != src:
            changed.append(p)
            if args.write:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(new)
            elif not args.check:
                sys.stdout.write(new)
        elif not args.check and not args.write:
            sys.stdout.write(new)

    if args.check:
        if changed:
            print("md_table_align: tables not strictly aligned in:")
            for c in changed:
                print(f"  {c}")
            return 1
        print("md_table_align: all tables strictly aligned")
        return 0
    if args.write:
        if changed:
            print("md_table_align: aligned tables in:")
            for c in changed:
                print(f"  {c}")
        else:
            print("md_table_align: no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

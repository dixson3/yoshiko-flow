#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Convert Markdown to a single, self-contained HTML file via pandoc.

The output is a standalone HTML document with every resource embedded — images,
the default stylesheet, and math — so it renders offline with no external host or
network fetch at view time:

  * --standalone --to=html5 --embed-resources  : one self-contained file.
  * --resource-path=<dir of the source .md>     : relative image references
    (`![](diagrams/foo.png)`) resolve against the source dir, then get embedded.
  * a broad-coverage default stylesheet (default.css) inlined via --css. Omit it
    with --no-default-css; add another with --css PATH.
  * --mathml : self-contained math (no CDN). MathJax/KaTeX are deliberately NOT
    used — they load script from a CDN, which would break --embed-resources.

CriticMarkup (opt-in): --criticmarkup renders the five constructs to styled HTML
(<ins>/<del>/<mark>/<span> with cm-add/cm-del/cm-hl/cm-comment classes) via
criticmarkup.lua. It reads with `-f gfm-strikeout`, which is REQUIRED (default
`gfm` parses a substitution's inner `~~…~~` as strikeout and destroys it before
any filter runs). TRADEOFF: while --criticmarkup is on, real GFM `~~strikethrough~~`
is disabled and renders literally, so CriticMarkup substitutions survive. Default
OFF: plain `gfm`, CriticMarkup passes through literally.

Usage:
    uv run md2html.py <input.md> [<input2.md> ...] [-o OUT.html]
                      [--criticmarkup] [--css PATH] [--no-default-css]
                      [-- <extra pandoc args>]

-o is only valid with a single input. With multiple inputs each <name>.md is
written to <name>.html beside the source. Anything after a literal `--` is passed
through to pandoc verbatim.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_CSS = Path(__file__).parent / "default.css"
CRITICMARKUP_FILTER = Path(__file__).parent / "criticmarkup.lua"


def check_deps() -> None:
    import shutil

    if shutil.which("pandoc") is None:
        sys.exit(
            "error: missing required tool: pandoc. Install pandoc "
            "(https://pandoc.org/installing.html)."
        )


def convert(src: Path, out: Path, criticmarkup: bool, default_css: bool,
            extra_css: list[Path], passthrough: list[str]) -> None:
    # --criticmarkup requires -f gfm-strikeout (disable the strikeout reader
    # extension) so a substitution's inner `~~…~~` is not consumed as Strikeout
    # before the filter runs. Default off: plain gfm, literal pass-through.
    reader = "gfm-strikeout" if criticmarkup else "gfm"
    cmd = [
        "pandoc", str(src), "-o", str(out),
        "-f", reader,
        "--standalone",
        "--to=html5",
        "--embed-resources",
        "--mathml",
        f"--resource-path={src.parent}",
    ]
    if default_css:
        cmd += ["--css", str(DEFAULT_CSS)]
    for css in extra_css:
        cmd += ["--css", str(css)]
    if criticmarkup:
        cmd += ["--lua-filter", str(CRITICMARKUP_FILTER)]
    cmd += passthrough

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(f"error: pandoc failed on {src} (exit {proc.returncode})")
    if proc.stderr.strip():
        sys.stderr.write(proc.stderr)
    print(f"  wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> self-contained HTML (pandoc).")
    ap.add_argument("inputs", nargs="+", type=Path, help="Markdown source file(s)")
    ap.add_argument("-o", "--output", type=Path,
                    help="Output HTML path (single input only)")
    ap.add_argument("--criticmarkup", action="store_true",
                    help="render CriticMarkup constructs to styled HTML (default off / "
                         "literal pass-through). Reads with gfm-strikeout, which disables "
                         "real GFM ~~strikethrough~~ while on (it renders literally).")
    ap.add_argument("--css", action="append", type=Path, default=[], metavar="PATH",
                    help="additional stylesheet to embed (repeatable)")
    ap.add_argument("--no-default-css", action="store_true",
                    help="omit the built-in default stylesheet (default.css)")
    args, passthrough = ap.parse_known_args()
    # argparse leaves a leading "--" in the remainder; drop it.
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    if args.output and len(args.inputs) > 1:
        sys.exit("error: -o/--output is only valid with a single input file")

    check_deps()

    default_css = not args.no_default_css
    for src in args.inputs:
        if not src.is_file():
            sys.exit(f"error: not a file: {src}")
        out = args.output if args.output else src.with_suffix(".html")
        convert(src, out, args.criticmarkup, default_css, args.css, passthrough)
    return 0


if __name__ == "__main__":
    sys.exit(main())

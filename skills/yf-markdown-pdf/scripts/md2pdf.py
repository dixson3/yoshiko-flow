#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10"]
# ///
"""Convert Markdown to PDF via the pandoc + xelatex pipeline.

A validated pandoc + xelatex pipeline: xelatex engine, a broad-coverage Unicode
main font on macOS (so glyphs like →, ≤, ≈ render), 1in margins, blue links, and
a resource-path anchored to the source file's directory so relative image
references (`![](diagrams/foo.png)`) resolve.

Raster normalization: 16-bit-per-channel and/or alpha PNGs embed but render
*blank* under xelatex. Before rendering, such referenced PNGs are flattened to
8-bit RGB (alpha composited onto white) in a run-scoped temp dir, which is
prepended to --resource-path so the normalized copy is used; the source images
are never modified. Disable with --no-normalize-images.

Table handling (the usual pain point for wide tables):
  * --table-font shrinks all table text (default footnotesize) so dense, many-
    column tables fit without cell content bleeding between columns.
  * --landscape-cols N rotates any table with more than N columns onto a
    landscape page (pdflscape). 0 (default) disables it. Applied via a Lua
    filter at render time, so the Markdown source stays pure GFM.
  * Column widths in the PDF come from the dash counts in each pipe table's
    separator row (pandoc behaviour). Obsidian and GitHub ignore dash counts,
    so tuning them to bias width toward text-heavy columns is portable. Caveat:
    pandoc only honours the dash counts once the separator row is wider than
    --columns (default 72); below that all columns render equal-width. Lower
    --columns to make the knob engage on narrower tables.

Usage:
    uv run md2pdf.py <input.md> [<input2.md> ...] [-o OUT.pdf]
                     [--mainfont NAME] [--monofont NAME] [--margin SIZE]
                     [--table-font SIZE] [--landscape-cols N] [--columns N]
                     [-- <extra pandoc args>]

-o is only valid with a single input. With multiple inputs each <name>.md is
written to <name>.pdf beside the source. Anything after a literal `--` is passed
through to pandoc verbatim.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Font defaults are platform-aware. On macOS, Arial Unicode MS / Menlo cover the
# math/arrow glyphs (→ ≤ ≈) the LaTeX default fonts miss. Those fonts do NOT exist
# on Linux/Windows, and naming a missing font makes xelatex HARD-FAIL (fontspec
# "cannot be found") — so off macOS we force no font: xelatex falls back to its
# default (Latin Modern) and merely *warns* on missing glyphs, keeping the default
# invocation portable. Pass --mainfont a Unicode-complete font (e.g. "DejaVu Sans"
# on Linux) for full glyph coverage.
_IS_MACOS = sys.platform == "darwin"
DEFAULT_MAINFONT: str | None = "Arial Unicode MS" if _IS_MACOS else None
DEFAULT_MONOFONT: str | None = "Menlo" if _IS_MACOS else None
DEFAULT_MARGIN = "1in"
DEFAULT_TABLE_FONT = "footnotesize"

# Valid LaTeX size macros, smallest to largest. "normalsize" = no shrink.
TABLE_FONT_SIZES = (
    "tiny", "scriptsize", "footnotesize", "small",
    "normalsize", "large", "Large",
)
LANDSCAPE_FILTER = Path(__file__).parent / "landscape_wide_tables.lua"
BLOCKS_FILTER = Path(__file__).parent / "blocks.lua"
GLYPH_FALLBACK = Path(__file__).parent / "glyph-fallback.tex"


def check_deps() -> None:
    missing = [t for t in ("pandoc", "xelatex") if shutil.which(t) is None]
    if missing:
        sys.exit(
            f"error: missing required tool(s): {', '.join(missing)}. "
            "Install pandoc and a LaTeX distribution providing xelatex."
        )


# Image references: Markdown inline `![alt](path)` and raw HTML `<img src=...>`.
# Reference-style images (`![alt][id]`) are not resolved — uncommon for local
# rasters and out of scope for this normalizer.
_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)>\s]+)>?", re.MULTILINE)
_HTML_IMG_RE = re.compile(r"""<img\b[^>]*?\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def _referenced_images(md_text: str) -> set[str]:
    """Local image targets referenced by the Markdown (inline + raw <img>)."""
    refs: set[str] = set()
    for rx in (_MD_IMG_RE, _HTML_IMG_RE):
        for m in rx.finditer(md_text):
            refs.add(m.group(1))
    return refs


def _png_needs_flatten(path: Path) -> bool:
    """True when `path` is a PNG that xelatex renders blank: 16-bit-per-channel
    depth and/or an alpha channel (#44). Reads only the 26-byte IHDR — pure
    stdlib, no decode. Non-PNG rasters (jpeg/etc.) are 8-bit and opaque, so they
    return False and are left untouched."""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
    except OSError:
        return False
    if len(head) < 26 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    bit_depth = head[24]
    color_type = head[25]  # 4 = gray+alpha, 6 = RGBA
    return bit_depth == 16 or color_type in (4, 6)


def _flatten_png(src_path: Path, dest_path: Path) -> bool:
    """Write an 8-bit RGB copy of `src_path` to `dest_path`, compositing any
    alpha onto white. Returns False (and writes nothing) if Pillow is absent or
    the image can't be read — the caller then leaves the original in place."""
    try:
        from PIL import Image
    except Exception:
        return False
    try:
        with Image.open(src_path) as im:
            im.load()
            if "A" in im.mode or (im.mode == "P" and "transparency" in im.info):
                rgba = im.convert("RGBA")
                out = Image.new("RGB", rgba.size, (255, 255, 255))
                out.paste(rgba, mask=rgba.split()[-1])
            else:
                out = im.convert("RGB")  # also collapses 16-bit -> 8-bit
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            out.save(dest_path, format="PNG")  # 8-bit RGB, no alpha
        return True
    except Exception:
        return False


def normalize_images(src: Path, tmp_root: str) -> Path | None:
    """Flatten 16-bit / alpha PNGs referenced by `src` into 8-bit RGB copies
    under a run-scoped mirror dir, preserving each image's path relative to the
    source dir. Returns the mirror dir to PREPEND to pandoc's --resource-path (so
    the normalized copy is found before the original), or None when nothing
    needed flattening. Degrades to None (originals used) if Pillow is absent."""
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    src_dir = src.parent.resolve()
    mirror = Path(tmp_root) / src.stem
    made_any = False
    for ref in _referenced_images(text):
        if ref.startswith(("http://", "https://", "data:")) or os.path.isabs(ref):
            continue
        rel = Path(ref)
        resolved = (src.parent / rel).resolve()
        # Only mirror images that live under the source dir — the resource-path
        # trick relies on a clean relative path (a `../` escape can't be mirrored).
        try:
            resolved.relative_to(src_dir)
        except ValueError:
            continue
        if not resolved.is_file() or not _png_needs_flatten(resolved):
            continue
        if _flatten_png(resolved, mirror / rel):
            made_any = True
    return mirror if made_any else None


def build_header(table_font: str, landscape: bool) -> str:
    """LaTeX preamble: shrink table fonts, and load pdflscape when needed."""
    parts = []
    if table_font != "normalsize":
        # etoolbox lets us inject a size macro at the start of every table env.
        parts.append(r"\usepackage{etoolbox}")
        for env in ("longtable", "tabular"):
            parts.append(rf"\AtBeginEnvironment{{{env}}}{{\{table_font}}}")
    if landscape:
        parts.append(r"\usepackage{pdflscape}")
    return "\n".join(parts) + "\n" if parts else ""


def convert(src: Path, out: Path, mainfont: str | None, monofont: str | None,
            margin: str, pre_args: list[str], passthrough: list[str],
            env: dict[str, str], resource_path: str) -> None:
    cmd = [
        "pandoc", str(src), "-o", str(out),
        "--pdf-engine=xelatex",
        "-V", f"geometry:margin={margin}",
        "-V", "linkcolor=blue",
    ]
    # Only force a font when one is set (macOS default, or an explicit --mainfont/
    # --monofont). Off macOS the defaults are None, so xelatex uses Latin Modern.
    if mainfont:
        cmd += ["-V", f"mainfont={mainfont}"]
    if monofont:
        cmd += ["-V", f"monofont={monofont}"]
    cmd += [
        f"--resource-path={resource_path}",
        *pre_args,
        *passthrough,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    # pandoc emits per-glyph "Missing character" warnings on stderr without
    # failing — surface them so a bad font choice is visible.
    warnings = [ln for ln in proc.stderr.splitlines() if "Missing character" in ln]
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(f"error: pandoc failed on {src} (exit {proc.returncode})")
    if warnings:
        n = len(warnings)
        print(f"  warning: {n} missing-glyph warning(s) — try a different --mainfont")
        for w in warnings[:5]:
            print(f"    {w.strip()}")
    print(f"  wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> PDF (pandoc + xelatex).")
    ap.add_argument("inputs", nargs="+", type=Path, help="Markdown source file(s)")
    ap.add_argument("-o", "--output", type=Path,
                    help="Output PDF path (single input only)")
    ap.add_argument("--mainfont", default=DEFAULT_MAINFONT)
    ap.add_argument("--monofont", default=DEFAULT_MONOFONT)
    ap.add_argument("--margin", default=DEFAULT_MARGIN)
    ap.add_argument("--table-font", default=DEFAULT_TABLE_FONT,
                    choices=TABLE_FONT_SIZES,
                    help="LaTeX size macro applied to tables (default footnotesize; "
                         "normalsize = no shrink)")
    ap.add_argument("--landscape-cols", type=int, default=0, metavar="N",
                    help="Rotate tables with more than N columns to landscape "
                         "(0 = disabled, the default)")
    ap.add_argument("--columns", type=int, default=72, metavar="N",
                    help="pandoc --columns (default 72). Dash-count column-width "
                         "tuning only engages once a table's separator row is "
                         "wider than this; lower it to tune narrower tables.")
    ap.add_argument("--no-render-fences", action="store_true",
                    help="keep ```d2```/```csv``` fences verbatim instead of "
                         "rendering them to PDF (default: render via blocks.lua). "
                         "Use when documenting d2/csv syntax itself.")
    ap.add_argument("--no-normalize-images", action="store_true",
                    help="skip flattening 16-bit / alpha PNGs to 8-bit RGB "
                         "(default: normalize, so they don't render blank under "
                         "xelatex). Originals are never modified in place.")
    args, passthrough = ap.parse_known_args()
    # argparse leaves a leading "--" in the remainder; drop it.
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    if args.output and len(args.inputs) > 1:
        sys.exit("error: -o/--output is only valid with a single input file")

    check_deps()

    landscape = args.landscape_cols > 0
    env = dict(os.environ)

    pre_args: list[str] = [f"--columns={args.columns}"]
    if landscape:
        pre_args += ["--lua-filter", str(LANDSCAPE_FILTER)]
        env["LANDSCAPE_COLS"] = str(args.landscape_cols)

    # Glyph fallback (macOS best-effort): remap color-emoji xelatex cannot render
    # (e.g. ✅) onto a monochrome symbol. Skipped off macOS — newunicodechar.sty and
    # Arial Unicode MS are MacTeX-guaranteed; elsewhere a missing glyph merely warns
    # (never a hard fail), so we do not risk loading a package that may be absent.
    if _IS_MACOS and GLYPH_FALLBACK.is_file():
        pre_args += ["--include-in-header", str(GLYPH_FALLBACK)]

    # Renderable fences (d2 -> PDF image, csv -> table) are rendered by default via
    # blocks.lua. The filter writes per-run d2 PDFs into MD2PDF_FENCE_TMPDIR, which
    # we own and reap in `finally` AFTER pandoc/xelatex have embedded them (so a
    # rendered diagram outlives the filter pass with no temp leak).
    render_fences = not args.no_render_fences
    fence_tmpdir: str | None = None

    # Raster normalization (#44): 16-bit / alpha PNGs render blank under xelatex,
    # so flatten them to 8-bit RGB copies in a run-scoped dir and prepend that dir
    # to --resource-path. Originals are never touched; reaped with the dir below.
    normalize = not args.no_normalize_images
    img_tmpdir: str | None = None

    header = build_header(args.table_font, landscape)
    header_path: Path | None = None
    try:
        if render_fences:
            fence_tmpdir = tempfile.mkdtemp(prefix="md2pdf-fence-")
            env["MD2PDF_FENCE_TMPDIR"] = fence_tmpdir
            pre_args += ["--lua-filter", str(BLOCKS_FILTER)]

        if normalize:
            img_tmpdir = tempfile.mkdtemp(prefix="md2pdf-img-")

        if header:
            fd, name = tempfile.mkstemp(suffix=".tex", prefix="md2pdf-hdr-")
            header_path = Path(name)
            with os.fdopen(fd, "w") as fh:
                fh.write(header)
            pre_args += ["--include-in-header", str(header_path)]

        for src in args.inputs:
            if not src.is_file():
                sys.exit(f"error: not a file: {src}")
            out = args.output if args.output else src.with_suffix(".pdf")
            rpaths = [str(src.parent)]
            if normalize and img_tmpdir is not None:
                mirror = normalize_images(src, img_tmpdir)
                if mirror is not None:
                    rpaths.insert(0, str(mirror))  # normalized copy wins
            convert(src, out, args.mainfont, args.monofont, args.margin,
                    pre_args, passthrough, env, os.pathsep.join(rpaths))
    finally:
        if header_path is not None:
            header_path.unlink(missing_ok=True)
        if fence_tmpdir is not None:
            shutil.rmtree(fence_tmpdir, ignore_errors=True)
        if img_tmpdir is not None:
            shutil.rmtree(img_tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

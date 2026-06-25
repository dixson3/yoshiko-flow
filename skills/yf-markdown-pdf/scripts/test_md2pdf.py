# /// script
# requires-python = ">=3.11"
# ///
"""Tests for md2pdf.py — renderable-fence rendering (d2/csv), the glyph fallback,
temp-artifact reaping, and the --no-render-fences opt-out.

Run:  uv run --with pytest python3 -m pytest test_md2pdf.py -q
      (add --with pypdf to exercise the PDF text-content assertions)

The full-render tests need the pandoc + xelatex + d2 toolchain and skip without it;
the unit tests (file presence, flag, glyph recipe) always run.
"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("md2pdf", _HERE / "md2pdf.py")
md2pdf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(md2pdf)

_HAS_TOOLS = all(shutil.which(t) for t in ("pandoc", "xelatex", "d2"))
_needs_tools = pytest.mark.skipif(not _HAS_TOOLS, reason="needs pandoc+xelatex+d2")

FIXTURE = (
    "# Renderable fence fixture\n\n"
    "A diagram:\n\n"
    "```d2\n"
    "a -> b -> c\n"
    "```\n\n"
    "A table:\n\n"
    "```csv\n"
    "name,score\n"
    "alice,10\n"
    "bob,20\n"
    "```\n\n"
    "Status: ✅ done.\n"   # U+2705 color check-mark -> monochrome remap
)


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(_HERE / "md2pdf.py"), *args],
        capture_output=True, text=True, cwd=cwd,
    )


def _fence_tmp_leftovers():
    return list(Path(tempfile.gettempdir()).glob("md2pdf-fence-*"))


def _img_tmp_leftovers():
    return list(Path(tempfile.gettempdir()).glob("md2pdf-img-*"))


# --- unit: wiring is present (no toolchain needed) ---------------------------

def test_blocks_filter_and_glyph_files_exist():
    assert md2pdf.BLOCKS_FILTER.is_file()
    assert md2pdf.GLYPH_FALLBACK.is_file()


def test_glyph_fallback_has_emoji_remap():
    text = md2pdf.GLYPH_FALLBACK.read_text(encoding="utf-8")
    assert "newunicodechar" in text
    assert "✅" in text          # the remapped color emoji
    assert "2714" in text            # the monochrome target slot


def test_help_lists_no_render_fences():
    # --help exits during arg parse, before check_deps — runs without pandoc.
    proc = _run(["--help"])
    assert proc.returncode == 0
    assert "--no-render-fences" in proc.stdout
    assert "--no-normalize-images" in proc.stdout


# --- unit: raster normalization (#44) ----------------------------------------

def _png(path, mode, size=(4, 3)):
    """Write a PNG of the given Pillow mode."""
    from PIL import Image

    Image.new(mode, size, 0).save(path, format="PNG")


def _png_ihdr_stub(path, bit_depth, color_type):
    """Write a file with a valid PNG signature + IHDR header carrying the given
    bit_depth/color_type. _png_needs_flatten reads only the 26-byte IHDR, so the
    rest need not be a decodable image — avoids Pillow's deprecated 16-bit save."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = (b"\x00\x00\x00\x0dIHDR"          # length + chunk type
            + b"\x00\x00\x00\x04\x00\x00\x00\x03"  # width=4, height=3
            + bytes([bit_depth, color_type]))
    path.write_bytes(sig + ihdr + b"\x00\x00\x00")


def test_referenced_images_parses_md_and_html():
    md = (
        "![a](rel/one.png)\n"
        '![b](<two.png> "title")\n'
        '<img src="three.png" width="40">\n'
        "![remote](https://x/y.png)\n"
    )
    refs = md2pdf._referenced_images(md)
    assert {"rel/one.png", "two.png", "three.png"} <= refs


def test_png_needs_flatten_classification(tmp_path):
    pytest.importorskip("PIL")
    rgb = tmp_path / "rgb.png"
    _png(rgb, "RGB")
    assert not md2pdf._png_needs_flatten(rgb)        # 8-bit opaque -> leave

    rgba = tmp_path / "rgba.png"
    _png(rgba, "RGBA")
    assert md2pdf._png_needs_flatten(rgba)           # alpha -> flatten

    gray16 = tmp_path / "g16.png"
    _png_ihdr_stub(gray16, bit_depth=16, color_type=0)
    assert md2pdf._png_needs_flatten(gray16)         # 16-bit -> flatten

    # Non-PNG (and non-image) inputs are never flagged.
    txt = tmp_path / "note.txt"
    txt.write_text("not a png", encoding="utf-8")
    assert not md2pdf._png_needs_flatten(txt)


def test_flatten_png_yields_8bit_rgb_no_alpha(tmp_path):
    from PIL import Image

    src = tmp_path / "rgba.png"
    _png(src, "RGBA")
    dest = tmp_path / "out" / "rgba.png"
    assert md2pdf._flatten_png(src, dest)
    with Image.open(dest) as im:
        assert im.mode == "RGB"                      # alpha gone
    # IHDR confirms 8-bit RGB (color_type 2, bit_depth 8).
    head = dest.read_bytes()[:26]
    assert head[24] == 8 and head[25] == 2


def test_normalize_images_mirrors_only_flagged(tmp_path):
    pytest.importorskip("PIL")
    (tmp_path / "sub").mkdir()
    _png(tmp_path / "keep.png", "RGB")               # opaque 8-bit -> not mirrored
    _png(tmp_path / "sub" / "alpha.png", "RGBA")     # alpha -> mirrored
    src = tmp_path / "doc.md"
    src.write_text("![k](keep.png)\n![a](sub/alpha.png)\n", encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        mirror = md2pdf.normalize_images(src, td)
        assert mirror is not None
        assert (mirror / "sub" / "alpha.png").is_file()   # preserves rel path
        assert not (mirror / "keep.png").exists()         # opaque untouched


# --- integration: full render (needs pandoc + xelatex + d2) ------------------

@_needs_tools
def test_renders_fixture_and_leaves_no_temp_leak(tmp_path):
    src = tmp_path / "fix.md"
    src.write_text(FIXTURE, encoding="utf-8")
    out = tmp_path / "out.pdf"
    before = set(_fence_tmp_leftovers())
    proc = _run([str(src), "-o", str(out)])
    assert proc.returncode == 0, proc.stderr
    assert out.is_file() and out.stat().st_size > 0
    # no per-run d2 temp dir survives the render (red-team C3)
    assert set(_fence_tmp_leftovers()) == before


@_needs_tools
def test_repeated_renders_do_not_accumulate_temp(tmp_path):
    src = tmp_path / "fix.md"
    src.write_text(FIXTURE, encoding="utf-8")
    before = set(_fence_tmp_leftovers())
    for k in range(3):
        assert _run([str(src), "-o", str(tmp_path / f"o{k}.pdf")]).returncode == 0
    assert set(_fence_tmp_leftovers()) == before


@_needs_tools
def test_no_raw_d2_source_in_rendered_pdf(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    src = tmp_path / "fix.md"
    src.write_text(FIXTURE, encoding="utf-8")
    out = tmp_path / "out.pdf"
    assert _run([str(src), "-o", str(out)]).returncode == 0
    text = "".join(p.extract_text() for p in pypdf.PdfReader(str(out)).pages)
    assert "a -> b" not in text       # d2 source rendered, not shown verbatim
    assert "alice" in text            # csv became a real table


@_needs_tools
def test_no_render_fences_keeps_source_verbatim(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    src = tmp_path / "fix.md"
    src.write_text("# t\n\n```d2\na -> b\n```\n", encoding="utf-8")
    out = tmp_path / "out.pdf"
    assert _run([str(src), "-o", str(out), "--no-render-fences"]).returncode == 0
    text = "".join(p.extract_text() for p in pypdf.PdfReader(str(out)).pages)
    assert "a -> b" in text           # fence left verbatim


@_needs_tools
def test_alpha_png_renders_and_embeds_8bit_rgb(tmp_path):
    # #44: a 16-bit/alpha PNG must render (not blank). We can't assert pixels, but
    # the embedded image must be the normalized 8-bit RGB (no smask), and no img
    # temp dir may survive the render.
    from PIL import Image

    img = tmp_path / "sample.png"
    Image.new("RGBA", (40, 20), (200, 150, 100, 128)).save(img, format="PNG")
    src = tmp_path / "doc.md"
    src.write_text("# t\n\n![s](sample.png)\n", encoding="utf-8")
    out = tmp_path / "doc.pdf"
    before = set(_img_tmp_leftovers())
    proc = _run([str(src), "-o", str(out)])
    assert proc.returncode == 0, proc.stderr
    assert out.is_file() and out.stat().st_size > 0
    assert set(_img_tmp_leftovers()) == before        # no temp leak
    if shutil.which("pdfimages"):
        listing = subprocess.run(
            ["pdfimages", "-list", str(out)], capture_output=True, text=True
        ).stdout
        assert "smask" not in listing                 # alpha flattened away
    # The source image is never modified in place.
    with Image.open(img) as orig:
        assert orig.mode == "RGBA"


@_needs_tools
def test_no_normalize_images_opt_out(tmp_path):
    from PIL import Image

    Image.new("RGBA", (40, 20), (10, 20, 30, 200)).save(
        tmp_path / "a.png", format="PNG"
    )
    src = tmp_path / "doc.md"
    src.write_text("# t\n\n![a](a.png)\n", encoding="utf-8")
    out = tmp_path / "doc.pdf"
    # Opt-out still renders (just without the flatten) and must not hard-fail.
    proc = _run([str(src), "-o", str(out), "--no-normalize-images"])
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()


@_needs_tools
def test_glyph_degrades_without_mainfont_never_hard_fails(tmp_path):
    # Forcing no mainfont ("" is falsy) simulates the off-macOS path: ✅ (and its
    # monochrome target) may be missing -> xelatex WARNS but must NOT hard-fail.
    src = tmp_path / "g.md"
    src.write_text("# t\n\nStatus: ✅ done.\n", encoding="utf-8")
    out = tmp_path / "g.pdf"
    proc = _run([str(src), "-o", str(out), "--mainfont", ""])
    assert proc.returncode == 0, proc.stderr   # graceful degrade, not a failure
    assert out.is_file()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

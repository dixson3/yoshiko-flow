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

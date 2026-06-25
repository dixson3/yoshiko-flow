# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
"""Tests for render.py's embed/lift/inline round-trip (the d2 renderable fence).

The d2-binary-free logic (markdown parse + rewrite) is always tested. Actual
.png rendering is exercised only when a `d2` binary is on PATH; otherwise the
lift test asserts the degrade path (`.d2` written, .png skipped, fence still
replaced) instead of skipping outright.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

HAS_D2 = shutil.which("d2") is not None

D2_SRC = "a -> b: hello\nb -> c: world"


# --- helpers ----------------------------------------------------------------

def make_args(**kw):
    base = {"json": False, "anchor": None, "out": None, "alt": None, "d2": None,
            "theme": render.DEFAULT_THEME, "layout": render.DEFAULT_LAYOUT}
    base.update(kw)
    return render._ns(**base)


# --- fence helpers ----------------------------------------------------------

def test_make_fence_roundtrips_source():
    fence = render.make_fence(D2_SRC)
    assert fence.startswith("```d2\n")
    assert fence.endswith("\n```")
    found = render.find_d2_fence(f"intro\n\n{fence}\n\noutro\n")
    assert found is not None
    _, _, source = found
    assert source == D2_SRC


def test_find_d2_fence_ignores_other_langs():
    text = "```python\nprint(1)\n```\n\n```d2\nx -> y\n```\n"
    found = render.find_d2_fence(text)
    assert found is not None
    assert found[2] == "x -> y"


def test_find_d2_fence_none_when_absent():
    assert render.find_d2_fence("no fences here\n```python\np\n```\n") is None


# --- embed ------------------------------------------------------------------

def test_embed_appends_fence(tmp_path):
    src = tmp_path / "diag.d2"
    src.write_text(D2_SRC + "\n")
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\nbody\n")
    rc = render.cmd_embed(make_args(source=str(src), target=str(md)))
    assert rc == 0
    found = render.find_d2_fence(md.read_text())
    assert found is not None and found[2] == D2_SRC


def test_embed_anchor_inserts_after_line(tmp_path):
    src = tmp_path / "diag.d2"
    src.write_text(D2_SRC + "\n")
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n<!-- DIAGRAM -->\n\nrest\n")
    rc = render.cmd_embed(make_args(source=str(src), target=str(md), anchor="DIAGRAM"))
    assert rc == 0
    lines = md.read_text().splitlines()
    anchor_idx = next(i for i, ln in enumerate(lines) if "DIAGRAM" in ln)
    fence_idx = next(i for i, ln in enumerate(lines) if ln.strip() == "```d2")
    assert fence_idx > anchor_idx
    assert "rest" in md.read_text()


def test_embed_missing_anchor_errors(tmp_path):
    src = tmp_path / "diag.d2"
    src.write_text(D2_SRC + "\n")
    md = tmp_path / "doc.md"
    md.write_text("# Title\n")
    rc = render.cmd_embed(make_args(source=str(src), target=str(md), anchor="NOPE"))
    assert rc == 2


# --- lift -------------------------------------------------------------------

def test_lift_extracts_d2_and_replaces_with_link(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(f"# Title\n\n```d2\n{D2_SRC}\n```\n\ntail\n")
    rc = render.cmd_lift(make_args(target=str(md)))
    d2_file = tmp_path / "doc.d2"
    assert d2_file.is_file()
    assert d2_file.read_text().rstrip("\n") == D2_SRC
    # fence gone, image link present
    assert render.find_d2_fence(md.read_text()) is None
    assert "![doc](doc.png)" in md.read_text()
    if HAS_D2:
        assert rc == 0
        assert (tmp_path / "doc.png").is_file()
    else:
        # degrade path: rc==0 (d2 absent is not a failure), png not rendered
        assert rc == 0


def test_lift_no_fence_errors(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\nno diagram\n")
    rc = render.cmd_lift(make_args(target=str(md)))
    assert rc == 1


# --- inline -----------------------------------------------------------------

def test_inline_replaces_link_with_fence(tmp_path):
    (tmp_path / "doc.d2").write_text(D2_SRC + "\n")
    (tmp_path / "doc.png").write_bytes(b"\x89PNG\r\n")  # placeholder render
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n![doc](doc.png)\n\ntail\n")
    rc = render.cmd_inline(make_args(target=str(md)))
    assert rc == 0
    found = render.find_d2_fence(md.read_text())
    assert found is not None and found[2] == D2_SRC
    assert "![doc](doc.png)" not in md.read_text()


def test_inline_no_resolvable_link_errors(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n![orphan](missing.png)\n")  # no sibling .d2
    rc = render.cmd_inline(make_args(target=str(md)))
    assert rc == 1


# --- round-trip -------------------------------------------------------------

def test_embed_lift_inline_roundtrip(tmp_path):
    """embed -> lift -> inline returns equivalent d2 source."""
    src = tmp_path / "src.d2"
    src.write_text(D2_SRC + "\n")
    md = tmp_path / "doc.md"
    md.write_text("# Diagram doc\n\nintro paragraph\n")

    assert render.cmd_embed(make_args(source=str(src), target=str(md))) == 0
    embedded = render.find_d2_fence(md.read_text())
    assert embedded is not None and embedded[2] == D2_SRC

    assert render.cmd_lift(make_args(target=str(md))) == 0
    assert render.find_d2_fence(md.read_text()) is None  # now an image link
    assert (tmp_path / "doc.d2").read_text().rstrip("\n") == D2_SRC

    assert render.cmd_inline(make_args(target=str(md))) == 0
    final = render.find_d2_fence(md.read_text())
    assert final is not None
    assert final[2] == D2_SRC  # source survived the full round-trip


def test_lift_inline_roundtrip_from_inline_start(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(f"# Doc\n\n```d2\n{D2_SRC}\n```\n")
    assert render.cmd_lift(make_args(target=str(md))) == 0
    assert render.cmd_inline(make_args(target=str(md))) == 0
    found = render.find_d2_fence(md.read_text())
    assert found is not None and found[2] == D2_SRC


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

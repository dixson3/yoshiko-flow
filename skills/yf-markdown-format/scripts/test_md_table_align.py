#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8"]
# ///
"""Tests for md_table_align.py — the strict GFM table aligner.

Covers REQ-MDFMT-001 (explicit-marker normalization), REQ-MDFMT-002 (--check /
--write / bare modes), REQ-MDFMT-003 (idempotent --write), REQ-MDFMT-004
(East-Asian width), REQ-MDFMT-005 (fenced-code skip), REQ-MDFMT-006 (file-level
--check output).

Run:  uv run test_md_table_align.py
      (self-runs pytest against this file; PEP-723 pulls pytest in)
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_ALIGN = _HERE / "md_table_align.py"
_spec = importlib.util.spec_from_file_location("md_table_align", _ALIGN)
mta = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mta)


def _run(args):
    """Invoke the script as a subprocess; return (rc, stdout)."""
    r = subprocess.run(
        [sys.executable, str(_ALIGN), *args],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout


MISALIGNED = "# t\n\n| A | Bee | C |\n|---|---|---|\n| 1 | 2 | 33 |\n"


# --- REQ-MDFMT-001: explicit-marker, uniform-width normalization ---

def test_bare_delimiter_gets_explicit_left_marker():
    out = mta.transform(MISALIGNED)
    # every delimiter column carries an explicit ':' left marker now
    delim = [ln for ln in out.splitlines() if ln.startswith("|") and set(ln) <= set("|:- ") and "-" in ln][0]
    assert delim.count(":") == 3  # one per column, all left
    # columns are uniform-width / pipe-aligned
    rows = [ln for ln in out.splitlines() if ln.startswith("|")]
    assert len({len(r) for r in rows}) == 1


def test_center_and_right_markers_preserved():
    text = "| A | B | C |\n| :-: | ---: | --- |\n| 1 | 2 | 3 |\n"
    out = mta.transform(text)
    delim = [ln for ln in out.splitlines() if ln.startswith("|") and set(ln) <= set("|:- ") and "-" in ln][0]
    cells = [c.strip() for c in delim.strip("|").split("|")]
    assert mta._align_of(cells[0]) == "center"  # center kept
    assert mta._align_of(cells[1]) == "right"   # right kept
    assert mta._align_of(cells[2]) == "left"    # unmarked -> explicit left
    assert cells[2].startswith(":")             # explicit marker added


# --- REQ-MDFMT-005: fenced code blocks are left untouched ---

def test_fenced_pipe_table_untouched():
    text = "```\n| A | B |\n|---|---|\n| 1 | 2 |\n```\n"
    assert mta.transform(text) == text


# --- REQ-MDFMT-004: East-Asian width awareness ---

def test_east_asian_width_counts_double():
    assert mta._w("漢字") == 4
    assert mta._w("ab") == 2
    # a fullwidth cell aligns on display width, not codepoint count
    text = "| 名前 | x |\n| :-- | :-- |\n| 田 | yy |\n"
    out = mta.transform(text)
    rows = [ln for ln in out.splitlines() if ln.startswith("|")]
    # rows are equal DISPLAY width (East-Asian aware), though codepoint counts differ
    assert len({mta._w(r) for r in rows}) == 1


# --- REQ-MDFMT-003: --write is idempotent (twice = no-op) ---

def test_write_is_idempotent(tmp_path):
    p = tmp_path / "t.md"
    p.write_text(MISALIGNED, encoding="utf-8")

    rc1, _ = _run(["--write", str(p)])
    assert rc1 == 0
    after_first = p.read_text(encoding="utf-8")
    assert after_first != MISALIGNED  # first write changed something

    rc2, out2 = _run(["--write", str(p)])
    assert rc2 == 0
    after_second = p.read_text(encoding="utf-8")
    assert after_second == after_first  # second run is a zero-diff no-op
    assert "no changes" in out2

    # and --check now agrees the file is a fixed point (REQ-MDFMT-002)
    rc_check, _ = _run(["--check", str(p)])
    assert rc_check == 0


# --- REQ-MDFMT-002 / 006: --check gate on a mis-aligned table exits 1, file-level ---

def test_check_flags_misaligned_table_exit_1(tmp_path):
    p = tmp_path / "bad.md"
    p.write_text(MISALIGNED, encoding="utf-8")
    rc, out = _run(["--check", str(p)])
    assert rc == 1
    assert "not strictly aligned" in out
    assert "bad.md" in out  # file-granularity finding (REQ-MDFMT-006)
    # --check mutates nothing
    assert p.read_text(encoding="utf-8") == MISALIGNED


def test_check_clean_file_exit_0(tmp_path):
    p = tmp_path / "ok.md"
    p.write_text(MISALIGNED, encoding="utf-8")
    _run(["--write", str(p)])  # normalize first
    rc, out = _run(["--check", str(p)])
    assert rc == 0
    assert "all tables strictly aligned" in out


# --- REQ-MDFMT-002: bare mode writes normalized doc to stdout ---

def test_bare_mode_writes_to_stdout(tmp_path):
    p = tmp_path / "t.md"
    p.write_text(MISALIGNED, encoding="utf-8")
    rc, out = _run([str(p)])
    assert rc == 0
    assert out == mta.transform(MISALIGNED)
    assert p.read_text(encoding="utf-8") == MISALIGNED  # source unchanged


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

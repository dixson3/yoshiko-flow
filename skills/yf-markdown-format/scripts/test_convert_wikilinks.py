#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8"]
# ///
"""Tests for convert_wikilinks.py — the Obsidian->GFM wiki-link migrator.

Covers REQ-MDFMT-010 (wiki-link -> GFM rewrite, incl. alias/anchor/embed forms),
REQ-MDFMT-011 (code-aware: frontmatter / fenced-code / inline-code protection),
REQ-MDFMT-012 (best-effort Obsidian resolution, unresolved surfaced not aborted),
REQ-MDFMT-013 (idempotence on an already-migrated tree), REQ-MDFMT-014 (dry-run
vs in-place write).

Run:  uv run test_convert_wikilinks.py
      (self-runs pytest against this file; PEP-723 pulls pytest in)
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_CONV = _HERE / "convert_wikilinks.py"
_spec = importlib.util.spec_from_file_location("convert_wikilinks", _CONV)
cw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cw)


def _run(args):
    """Invoke the script as a subprocess; return (rc, stdout)."""
    r = subprocess.run(
        [sys.executable, str(_CONV), *args],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout


def _convert(vault: Path, dry: bool = False):
    """Convert every .md under `vault` in-process; return the Stats object."""
    index = cw.VaultIndex(vault)
    st = cw.Stats()
    for p in sorted(vault.rglob("*.md")):
        cw.convert_file(p, index, st, dry)
    return st


# --- REQ-MDFMT-010: wiki-links rewrite to GFM links / images ---

def test_basic_wikilink_and_alias_and_embed(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    (tmp_path / "pic.png").write_bytes(b"")
    src = tmp_path / "note.md"
    src.write_text(
        "See [[Target]] and [[Target|the alias]].\n\n![[pic.png]]\n",
        encoding="utf-8",
    )
    _convert(tmp_path)
    out = src.read_text(encoding="utf-8")
    assert "[Target](Target.md)" in out          # bare link
    assert "[the alias](Target.md)" in out        # aliased display text
    assert "![pic.png](pic.png)" in out           # image embed stays an image
    assert "[[" not in out                        # no wiki-link syntax remains


# --- REQ-MDFMT-014: dry-run reports would-be rewrites without touching files ---

def test_dry_run_leaves_file_untouched_but_reports_change(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    src = tmp_path / "note.md"
    original = "Link to [[Target]].\n"
    src.write_text(original, encoding="utf-8")

    index = cw.VaultIndex(tmp_path)
    st = cw.Stats()
    changed = cw.convert_file(src, index, st, dry=True)

    assert changed is True                         # it *would* rewrite
    assert st.converted == 1                        # and counted the link
    assert src.read_text(encoding="utf-8") == original  # but wrote nothing


def test_in_place_write_mutates_file(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    src = tmp_path / "note.md"
    src.write_text("Link to [[Target]].\n", encoding="utf-8")

    index = cw.VaultIndex(tmp_path)
    st = cw.Stats()
    changed = cw.convert_file(src, index, st, dry=False)

    assert changed is True
    assert "[[" not in src.read_text(encoding="utf-8")   # file actually rewritten


# --- REQ-MDFMT-011: code-aware — frontmatter / fenced code / inline code protected ---

def test_frontmatter_and_code_fences_are_protected(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    src = tmp_path / "note.md"
    src.write_text(
        "---\n"
        "aliases: [[Target]]\n"          # YAML frontmatter — must NOT convert
        "---\n"
        "\n"
        "Real link: [[Target]].\n"       # body — SHOULD convert
        "\n"
        "```\n"
        "code [[Target]] fenced\n"       # fenced code — must NOT convert
        "```\n"
        "\n"
        "Inline `[[Target]]` span.\n",   # inline code — must NOT convert
        encoding="utf-8",
    )
    _convert(tmp_path)
    out = src.read_text(encoding="utf-8")

    # frontmatter, fenced, and inline-code wiki-links survive verbatim
    assert "aliases: [[Target]]" in out
    assert "code [[Target]] fenced" in out
    assert "`[[Target]]`" in out
    # the one body occurrence became a GFM link
    assert "Real link: [Target](Target.md)." in out


# --- REQ-MDFMT-012: unresolved links are best-effort converted, not aborting ---

def test_unresolved_link_is_best_effort_and_surfaced(tmp_path):
    src = tmp_path / "note.md"
    src.write_text("Dangling [[Nowhere]] link.\n", encoding="utf-8")
    st = _convert(tmp_path)
    out = src.read_text(encoding="utf-8")
    assert "[Nowhere](Nowhere.md)" in out     # best-effort .md guess
    assert st.unresolved                       # and surfaced in the report stats


# --- REQ-MDFMT-013: migration is idempotent (second run = no-op) ---

def test_idempotent_second_run_is_noop(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    src = tmp_path / "note.md"
    src.write_text("Link [[Target]] and ![[pic.png]] here.\n", encoding="utf-8")
    (tmp_path / "pic.png").write_bytes(b"")

    _convert(tmp_path)                          # first pass rewrites
    after_first = src.read_text(encoding="utf-8")
    assert "[[" not in after_first

    st2 = _convert(tmp_path)                     # second pass over migrated tree
    after_second = src.read_text(encoding="utf-8")
    assert after_second == after_first           # zero further change
    assert st2.converted == 0                     # nothing left to convert


def test_idempotent_via_cli_dry_run_after_write(tmp_path):
    (tmp_path / "Target.md").write_text("# Target\n", encoding="utf-8")
    src = tmp_path / "note.md"
    src.write_text("Link [[Target]] here.\n", encoding="utf-8")

    rc1, _ = _run([str(tmp_path), "--vault-root", str(tmp_path)])
    assert rc1 == 0
    migrated = src.read_text(encoding="utf-8")
    assert "[[" not in migrated

    # a dry-run over the already-migrated tree would change nothing
    rc2, _ = _run([str(tmp_path), "--vault-root", str(tmp_path), "--dry-run"])
    assert rc2 == 0
    assert src.read_text(encoding="utf-8") == migrated


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

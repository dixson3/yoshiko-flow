# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6",
#     "pytest>=8",
# ]
# ///
"""Unit tests for incubator-index.py — the OKF-INCUBATOR adapter (plan-029, Issue 5.2).

Run from anywhere:  uv run skills/yf-incubator/scripts/test_incubator_index.py

Covers: engine-routed frontmatter reads (report-only), merge-and-preserve typing of the
seven pre-OKF keys + additive type/okf_spec (REQ-INCUB-002/040), the single-file
reserved-file exemption (REQ-INCUB-042 / REQ-OKF-050), dir-form reserved-file scaffolding
and the `## Files`→index.md / `## Decision log`→log.md promotion move (REQ-INCUB-041), and
that `Incubator/INDEX.md` stays untyped and outside the bundle model (REQ-INCUB-043).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parent / "incubator-index.py"
_spec = importlib.util.spec_from_file_location("incubator_index", _PATH)
assert _spec and _spec.loader
ii = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ii)
okf = ii.okf


SEVEN_KEY_FM = """---
title: Widget Mesh
created: 2026-05-13
tags: [incubator, agents, mesh]
status: incubating
last_reviewed: 2026-05-17
priority: normal
aliases: [widget-mesh]
---

## Resume

- **Next action**: validate the flow.

## Status

Exploring.

## Files

- [notes.md](research/notes.md) — the raw notes

## Decision log

- 2026-05-15 — chose Dolt — embedded git+db
- 2026-05-13 — kicked off — initial premise

## Beads to file

"""


# --- parse_frontmatter: engine-routed, report-only ---------------------------

def test_parse_frontmatter_reads_via_engine(tmp_path):
    f = tmp_path / "x.md"
    f.write_text(SEVEN_KEY_FM)
    fm = ii.parse_frontmatter(f)
    assert fm is not None
    assert fm["status"] == "incubating"
    assert fm["aliases"] == ["widget-mesh"]


def test_parse_frontmatter_malformed_is_report_only(tmp_path):
    f = tmp_path / "bad.md"
    f.write_text("---\ntitle: [unterminated\n---\n\n## Resume\n")
    # Malformed YAML must not raise — the entry becomes unmanaged (returns None).
    assert ii.parse_frontmatter(f) is None


def test_parse_frontmatter_no_frontmatter_is_none(tmp_path):
    f = tmp_path / "plain.md"
    f.write_text("# Just a heading\n")
    assert ii.parse_frontmatter(f) is None


# --- typing: merge-and-preserve (REQ-INCUB-002/040, REQ-OKF-070) -------------

def test_type_state_file_merge_preserves_seven_keys(tmp_path):
    f = tmp_path / "widget.md"
    f.write_text(SEVEN_KEY_FM)
    ii.type_state_file(f)
    fm, body = okf.read_frontmatter(f)
    # seven pre-OKF keys survive, values intact
    for k in ("title", "created", "tags", "status", "last_reviewed", "priority", "aliases"):
        assert k in fm
    assert fm["aliases"] == ["widget-mesh"]
    assert fm["tags"] == ["incubator", "agents", "mesh"]
    # two OKF keys added
    assert fm["type"] == "Incubator"
    assert fm["okf_spec"] == "OKF-INCUBATOR"
    # order: pre-OKF keys first, OKF keys appended last
    assert list(fm.keys())[-2:] == ["type", "okf_spec"]
    # body untouched
    assert "## Decision log" in body


def test_type_state_file_idempotent(tmp_path):
    f = tmp_path / "widget.md"
    f.write_text(SEVEN_KEY_FM)
    ii.type_state_file(f)
    once = f.read_text()
    ii.type_state_file(f)
    assert f.read_text() == once


# --- single-file exemption (REQ-INCUB-042 / REQ-OKF-050) ---------------------

def test_scaffold_single_file_is_reserved_exempt(tmp_path):
    f = tmp_path / "idea.md"
    f.write_text(SEVEN_KEY_FM)
    res = ii.scaffold(f)
    assert res["single_file"] is True
    assert res["reserved"] == []
    # no reserved files created next to a single-file incubator
    assert not (tmp_path / "index.md").exists()
    assert not (tmp_path / "log.md").exists()
    # sections stay in-body
    _fm, body = okf.read_frontmatter(f)
    assert "## Files" in body and "## Decision log" in body


def test_is_single_file(tmp_path):
    f = tmp_path / "idea.md"
    f.write_text("x")
    assert ii.is_single_file(f) is True
    d = tmp_path / "bundle"
    d.mkdir()
    assert ii.is_single_file(d) is False


# --- dir-form reserved-file scaffolding (REQ-INCUB-041) ----------------------

def test_scaffold_dirform_creates_untyped_reserved_files(tmp_path):
    d = tmp_path / "bundle"
    d.mkdir()
    (d / "README.md").write_text(SEVEN_KEY_FM)
    res = ii.scaffold(d)
    assert res["single_file"] is False
    assert res["reserved"] == ["index.md", "log.md"]
    assert (d / "index.md").exists()
    assert (d / "log.md").exists()
    # README typed; reserved files carry no type/okf_spec (REQ-OKF-031)
    rfm, _ = okf.read_frontmatter(d / "README.md")
    assert rfm["type"] == "Incubator"
    ifm, _ = okf.read_frontmatter(d / "index.md")
    assert "type" not in ifm and "okf_spec" not in ifm
    lfm, _ = okf.read_frontmatter(d / "log.md")
    assert "type" not in lfm and "okf_spec" not in lfm
    # README kept, never renamed to index.md (REQ-INCUB-040)
    assert (d / "README.md").exists()


# --- promotion: single-file -> dir-form, moving sections (REQ-INCUB-041) -----

def test_promote_moves_files_and_decision_log(tmp_path):
    f = tmp_path / "widget.md"
    f.write_text(SEVEN_KEY_FM)
    plan = ii.promote(f)
    bundle = tmp_path / "widget"
    assert set(plan["moved"]) == {"index.md", "log.md"}
    # single file becomes README.md; original removed
    assert not f.exists()
    assert (bundle / "README.md").exists()
    # README keeps type + drops the two promoted sections (never other sections)
    rfm, rbody = okf.read_frontmatter(bundle / "README.md")
    assert rfm["type"] == "Incubator"
    assert "## Files" not in rbody
    assert "## Decision log" not in rbody
    assert "## Resume" in rbody and "## Beads to file" in rbody
    # moved content preserved (never dropped — REQ-INCUB-003)
    assert "notes.md" in (bundle / "index.md").read_text()
    log_txt = (bundle / "log.md").read_text()
    assert log_txt.startswith("# Log")
    assert "chose Dolt" in log_txt
    # reserved files untyped
    ifm, _ = okf.read_frontmatter(bundle / "index.md")
    assert "type" not in ifm
    assert "okf_version" in ifm  # bundle-root reserved key


def test_promote_dry_run_no_writes(tmp_path):
    f = tmp_path / "widget.md"
    f.write_text(SEVEN_KEY_FM)
    plan = ii.promote(f, dry_run=True)
    assert set(plan["moved"]) == {"index.md", "log.md"}
    assert f.exists()  # unchanged
    assert not (tmp_path / "widget").exists()


# --- INDEX.md exemption + collect (REQ-INCUB-043) ----------------------------

def _make_managed(d: Path, name: str, status="incubating", priority="normal",
                  last="2026-05-17"):
    b = d / name
    b.mkdir()
    (b / "README.md").write_text(
        f"---\ntitle: {name}\ncreated: 2026-05-01\ntags: [incubator]\n"
        f"status: {status}\nlast_reviewed: {last}\npriority: {priority}\n"
        f"aliases: [{name}]\ntype: Incubator\nokf_spec: OKF-INCUBATOR\n---\n\n## Resume\n")
    return b


def test_collect_skips_index_catalog(tmp_path):
    root = tmp_path / "Incubator"
    root.mkdir()
    _make_managed(root, "alpha")
    (root / "INDEX.md").write_text("# catalog\n")
    managed, unmanaged = ii.collect(root)
    names = [m["name"] for m in managed] + [u["name"] for u in unmanaged]
    assert "INDEX.md" not in names
    assert "INDEX" not in names
    assert any(m["name"] == "alpha" for m in managed)


def test_scaffold_refuses_index_catalog(tmp_path):
    root = tmp_path / "Incubator"
    root.mkdir()
    (root / "INDEX.md").write_text("# catalog\n")
    with pytest.raises(ValueError):
        ii.scaffold(root / "INDEX.md")


def test_list_write_index_has_no_frontmatter(tmp_path, capsys):
    root = tmp_path / "Incubator"
    root.mkdir()
    _make_managed(root, "alpha")
    ns = type("NS", (), {"root": str(root), "json": False, "write": True})()
    assert ii.cmd_list(ns) == 0
    idx = (root / "INDEX.md").read_text()
    # cross-incubator catalog: plain GFM, no OKF frontmatter/type/okf_spec
    assert not idx.startswith("---")
    assert "type:" not in idx.splitlines()[0]
    assert "okf_spec" not in idx


def test_collect_unmanaged_when_missing_status(tmp_path):
    root = tmp_path / "Incubator"
    root.mkdir()
    b = root / "beta"
    b.mkdir()
    (b / "README.md").write_text("---\ntitle: beta\ntype: Incubator\n---\n\n## Resume\n")
    managed, unmanaged = ii.collect(root)
    assert not managed
    assert unmanaged and unmanaged[0]["reason"].startswith("frontmatter missing")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

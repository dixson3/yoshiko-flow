# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1", "pyyaml", "pytest"]
# ///
"""Tests for the OKF-RESEARCH index_manager adapter: index.md / log.md split,
the OKF bullet listing shape, and frontmatter stamping (REQ-PORT-007/009)."""
from pathlib import Path

import pytest
from click.testing import CliRunner

import okf
import index_manager as im


def _init(tmp: Path, topic="001-my-topic"):
    r = CliRunner().invoke(im.cli, ["init", str(tmp), topic])
    assert r.exit_code == 0, r.output
    return tmp


def _add(tmp: Path, phase, artifact, desc, ts="2026-07-19T10:00"):
    r = CliRunner().invoke(im.cli, ["add", str(tmp), phase, artifact, desc, "-t", ts])
    assert r.exit_code == 0, r.output
    return r


# --- reserved file rename + creation ---------------------------------------

def test_reserved_filename_is_index_md():
    assert im.INDEX_FILENAME == "index.md"
    assert im.LOG_FILENAME == "log.md"


def test_init_creates_index_and_log_not_legacy(tmp_path):
    _init(tmp_path)
    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "log.md").exists()
    assert not (tmp_path / "_index.md").exists()


def test_init_index_has_okf_version_and_heading(tmp_path):
    _init(tmp_path, "007-widgets")
    fm, body = okf.read_frontmatter(tmp_path / "index.md")
    assert fm.get("okf_version") == okf.okf_version
    assert "# Research Index: 007-widgets" in body


def test_reserved_files_carry_no_type_or_okf_spec(tmp_path):
    _init(tmp_path)
    for name in ("index.md", "log.md"):
        fm, _ = okf.read_frontmatter(tmp_path / name)
        assert okf.TYPE_KEY not in fm
        assert okf.OKF_SPEC_KEY not in fm


# --- add: index listing + log ledger ----------------------------------------

def test_add_appends_index_bullet(tmp_path):
    _init(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "triangulation.md").write_text("# T\n")
    _add(tmp_path, "triangulate", "artifacts/triangulation.md", "cross-ref")
    body = (tmp_path / "index.md").read_text()
    assert "- [artifacts/triangulation.md](artifacts/triangulation.md) - [triangulate] cross-ref" in body


def test_add_writes_timestamped_log_entry(tmp_path):
    _init(tmp_path)
    (tmp_path / "sources.md").write_text("# S\n")
    _add(tmp_path, "package", "sources.md", "source list", ts="2026-07-19T11:22")
    log = (tmp_path / "log.md").read_text()
    assert "## 2026-07-19" in log
    assert "2026-07-19T11:22 · [package] sources.md — source list" in log


def test_add_index_entry_idempotent(tmp_path):
    _init(tmp_path)
    (tmp_path / "sources.md").write_text("# S\n")
    _add(tmp_path, "package", "sources.md", "source list")
    _add(tmp_path, "package", "sources.md", "source list")
    body = (tmp_path / "index.md").read_text()
    assert body.count("[sources.md](sources.md)") == 1


# --- add: frontmatter stamping ----------------------------------------------

def test_add_stamps_summary_report_and_member_keys(tmp_path):
    _init(tmp_path)
    (tmp_path / "Summary.md").write_text(
        "# Summary\n\n"
        "**Research project:** 001-my-topic · **Phase:** synthesize · **Date:** 2026-07-18\n\n"
        "## Executive summary\n\nbody\n"
    )
    _add(tmp_path, "synthesize", "Summary.md", "the report")
    fm, _ = okf.read_frontmatter(tmp_path / "Summary.md")
    assert fm["type"] == "Research Report"
    assert fm["okf_spec"] == "OKF-RESEARCH"
    assert fm["idx"] == "001"
    assert fm["topic"] == "my-topic"
    assert fm["created"] == "2026-07-18"
    assert fm["status"] == "synthesize"


def test_add_stamps_artifact_type(tmp_path):
    _init(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "critique.md").write_text("# C\n")
    _add(tmp_path, "critique", "artifacts/critique.md", "adversarial")
    fm, _ = okf.read_frontmatter(tmp_path / "artifacts" / "critique.md")
    assert fm["type"] == "Research Artifact"
    assert fm["okf_spec"] == "OKF-RESEARCH"


def test_add_stamps_sources_reference(tmp_path):
    _init(tmp_path)
    (tmp_path / "sources.md").write_text("# S\n")
    _add(tmp_path, "package", "sources.md", "sources")
    fm, _ = okf.read_frontmatter(tmp_path / "sources.md")
    assert fm["type"] == "Reference"


def test_add_does_not_stamp_non_md(tmp_path):
    _init(tmp_path)
    (tmp_path / "diagrams").mkdir()
    (tmp_path / "diagrams" / "x.png").write_text("binary-ish")
    _add(tmp_path, "package", "diagrams/x.png", "a diagram")
    # png untouched — no frontmatter injected
    assert (tmp_path / "diagrams" / "x.png").read_text() == "binary-ish"


def test_summary_member_keys_fall_back_to_dirname(tmp_path):
    keys = im._summary_member_keys("# Summary\n\nno header here\n", str(tmp_path / "042-foo-bar"))
    assert keys["idx"] == "042"
    assert keys["topic"] == "foo-bar"


def test_stamp_is_merge_and_preserve(tmp_path):
    _init(tmp_path)
    (tmp_path / "sources.md").write_text("---\nforeign: keep\n---\n# S\n")
    _add(tmp_path, "package", "sources.md", "sources")
    fm, _ = okf.read_frontmatter(tmp_path / "sources.md")
    assert fm["foreign"] == "keep"
    assert fm["type"] == "Reference"


# --- list -------------------------------------------------------------------

def test_parse_rows_recovers_phase(tmp_path):
    content = (
        "# Research Index: x\n\n"
        "- [Summary.md](Summary.md) - [synthesize] the report\n"
        "- [a.md](a.md) - [retrieve] cluster\n"
    )
    rows = im._parse_rows(content)
    assert rows[0] == {"phase": "synthesize", "artifact": "Summary.md", "description": "the report"}
    assert rows[1]["phase"] == "retrieve"


def test_list_phase_filter(tmp_path):
    _init(tmp_path)
    (tmp_path / "sources.md").write_text("# S\n")
    (tmp_path / "Summary.md").write_text("# Sum\n")
    _add(tmp_path, "package", "sources.md", "sources")
    _add(tmp_path, "synthesize", "Summary.md", "report")
    r = CliRunner().invoke(im.cli, ["list", str(tmp_path), "-j", "-p", "package"])
    assert r.exit_code == 0, r.output
    import json
    rows = json.loads(r.output)
    assert len(rows) == 1
    assert rows[0]["artifact"] == "sources.md"


# --- end-to-end conformance -------------------------------------------------

def test_migrated_bundle_is_okf_conformant(tmp_path):
    _init(tmp_path, "001-my-topic")
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "Summary.md").write_text(
        "# Summary\n\n"
        "**Research project:** 001-my-topic · **Phase:** package · **Date:** 2026-07-18\n\n"
        "## Executive summary\n\nbody\n"
    )
    (tmp_path / "sources.md").write_text("# S\n\n## Body\n")
    (tmp_path / "artifacts" / "critique.md").write_text("# C\n\n## Body\n")
    _add(tmp_path, "synthesize", "Summary.md", "report")
    _add(tmp_path, "package", "sources.md", "sources")
    _add(tmp_path, "critique", "artifacts/critique.md", "critique")
    findings = okf.check_conformance(tmp_path)
    assert findings.ok, findings.as_dict()
    # zero warnings too — the adapter completes idx/topic/created
    assert findings.findings == [], findings.as_dict()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))

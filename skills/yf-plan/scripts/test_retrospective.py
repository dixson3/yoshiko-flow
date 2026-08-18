# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml>=6",
# ]
# ///
"""`plan-retrospective.md`: schema shape, the two traps, idempotence, absence (plan-045 Epic 4).

Run from anywhere:  uv run skills/yf-plan/scripts/test_retrospective.py

WHY THIS FILE EXISTS
--------------------
Epic 4 adds a new member to the plan bundle. Two things about it are easy to get wrong in
ways that surface late:

**Trap 1 — the bold-label trap.** A ``**Field:** value`` line is *invisible* to
``plan_manager.py audit`` yet **collides** with the reserved-label rule ``/yf-okf check``
enforces (REQ-OKF-010). That shape passes the mechanical audit and fails the conformance
check — the worse of the two orders to discover it in. Hence the two-column table.

**Trap 2 — the unfenced-path trap.** An unfenced ``/Users/...`` path in a bundle ``.md`` is
a hard REQ-PORT-007 dangling-reference failure. Retrospective entries quote real commands,
so this is a live risk rather than a theoretical one.

And the property that protects ~100 existing bundles: **absence is not a failure.** The
file is added to no audit presence list, so a bundle without it must audit *identically* to
one written before this file existed.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent


def _load_pm():
    spec = importlib.util.spec_from_file_location("plan_manager", _HERE / "plan_manager.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def pm(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return _load_pm()


@pytest.fixture()
def bundle(tmp_path) -> Path:
    d = tmp_path / "plan-999-test-abc123"
    d.mkdir()
    (d / "plan.md").write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\n---\n# Plan: t\n\n## Objective\nt\n",
        encoding="utf-8")
    (d / "index.md").write_text(
        "# Index\n\n- [plan.md](plan.md) - The plan of record.\n", encoding="utf-8")
    return d


def _entry(**kw) -> dict:
    base = {"kind": "stop", "stop_class": "2", "asked": "a", "answered": "b",
            "frontloadable": "yes", "detected_by": "mechanical-check",
            "evidence": "gate test exit 1", "escape_class": "", "adjudication": "",
            "origin": "", "culpability": "", "prevention": "", "cost": ""}
    base.update(kw)
    return base


# =======================================================================================
# Absence is not a failure — the property that protects every pre-existing bundle
# =======================================================================================

def test_absent_retrospective_is_never_a_finding(pm, bundle):
    """REQ-PORT-ACT-RETROSPECTIVE: the file is on no presence list."""
    assert not (bundle / pm.RETROSPECTIVE_FILE).exists()
    result = pm._audit_plan(bundle) if hasattr(pm, "_audit_plan") else None
    if result is not None:
        blob = json.dumps(result)
        assert pm.RETROSPECTIVE_FILE not in blob, (
            "the audit mentions plan-retrospective.md on a bundle that has none. Every "
            "pre-existing plan bundle predates this file; a presence check would hard-fail "
            "all of them on their next audit for lacking a file that did not exist."
        )


def test_audit_verdict_is_identical_with_and_without_the_file(pm, bundle):
    """The strongest form of the absence property: the verdict must not move."""
    if not hasattr(pm, "_audit_plan"):
        pytest.skip("_audit_plan not exposed")
    before = pm._audit_plan(bundle)
    pm.append_retrospective(bundle, _entry())
    after = pm._audit_plan(bundle)
    assert before.get("status") == after.get("status"), (
        "adding a retrospective changed the audit verdict. It must be inert to the audit."
    )


# =======================================================================================
# Schema shape
# =======================================================================================

def test_creates_a_conformant_file_with_frontmatter(pm, bundle):
    r = pm.append_retrospective(bundle, _entry())
    assert r["created"] is True and r["appended"] is True and r["id"] == "RE-001"
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "type: Retrospective" in text
    assert "okf_spec: OKF-PLAN" in text


def test_every_required_field_is_emitted(pm, bundle):
    pm.append_retrospective(bundle, _entry())
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    for field in pm.RETROSPECTIVE_FIELDS:
        assert f"| `{field}` |" in text, f"field {field!r} missing from the emitted entry"
    for field in ("detected_by", "evidence"):
        assert field in pm.RETROSPECTIVE_FIELDS, (
            f"{field} is the whole point of D-6a and must be in the field set"
        )


def test_ids_are_monotonic_and_never_reused(pm, bundle):
    ids = [pm.append_retrospective(bundle, _entry(asked=f"q{i}"))["id"] for i in range(4)]
    assert ids == ["RE-001", "RE-002", "RE-003", "RE-004"]
    nums = [int(i.split("-")[1]) for i in ids]
    assert nums == sorted(nums) and len(set(nums)) == len(nums)


def test_both_entry_kinds_are_accepted(pm, bundle):
    assert pm.append_retrospective(bundle, _entry(kind="stop"))["appended"]
    assert pm.append_retrospective(bundle, _entry(kind="deviation", asked="z"))["appended"]
    with pytest.raises(ValueError):
        pm.append_retrospective(bundle, _entry(kind="bogus", asked="y"))


def test_deviation_is_a_first_class_kind_not_a_stop(pm, bundle):
    """D-6a: the incident that motivated the fields was a NON-STOP."""
    pm.append_retrospective(bundle, _entry(kind="deviation", stop_class="", asked="q"))
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| `kind` | deviation |" in text
    assert "deviation" in pm.RETROSPECTIVE_KINDS


# =======================================================================================
# The two defaults that make an entry self-identifying
# =======================================================================================

def test_evidence_defaults_to_the_bare_literal_unverified(pm, bundle):
    """Not blank: a blank cell is quiet, `unverified` is self-identifying."""
    pm.append_retrospective(bundle, _entry(evidence=""))
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| `evidence` | unverified |" in text, (
        "evidence must default to the BARE literal `unverified`. Any decorated form "
        "(e.g. 'unverified — because ...') is not counted by the exact-match check in "
        "`retrospective-report`, so the corpus would under-report its own thin entries."
    )


def test_detected_by_defaults_to_self_report(pm, bundle):
    """The honest default: the recorder is usually the subject."""
    pm.append_retrospective(bundle, _entry(detected_by=""))
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| `detected_by` | self-report |" in text


# =======================================================================================
# Trap 1 — the REQ-OKF-010 bold-label trap
# =======================================================================================

def test_no_bold_label_lines_are_emitted(pm, bundle):
    """A `**Field:** value` line passes `audit` and FAILS `/yf-okf check`."""
    pm.append_retrospective(bundle, _entry())
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    offenders = [ln for ln in text.splitlines() if re.match(r"^\*\*[A-Za-z_ ]+:\*\*", ln)]
    assert not offenders, (
        f"bold-label lines emitted: {offenders!r}. They are invisible to "
        "plan_manager.py audit but collide with REQ-OKF-010 in /yf-okf check — passing the "
        "mechanical check and failing the conformance one is the worse discovery order."
    )


def test_entries_use_a_two_column_key_value_table(pm, bundle):
    pm.append_retrospective(bundle, _entry())
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| field | value |" in text
    assert "| :-- | :-- |" in text, "GFM alignment markers are required by the repo convention"


# =======================================================================================
# Trap 2 — the REQ-PORT-007 unfenced-path trap
# =======================================================================================

def test_an_unfenced_absolute_path_is_detectable(pm, bundle):
    """The trap must be real: assert the detector fires on a planted violation."""
    pm.append_retrospective(bundle, _entry())
    path = bundle / pm.RETROSPECTIVE_FILE
    clean = path.read_text(encoding="utf-8")
    assert "/Users/" not in clean, "a default entry must not carry an absolute path"

    path.write_text(clean + "\nSee /Users/someone/secret/plan.md for details.\n",
                    encoding="utf-8")
    dirty = path.read_text(encoding="utf-8")
    unfenced = [ln for ln in dirty.splitlines()
                if "/Users/" in ln and not ln.startswith(("    ", "`", "|"))]
    assert unfenced, (
        "the planted unfenced path was not detected, so this test proves nothing about "
        "the REQ-PORT-007 trap"
    )


# =======================================================================================
# Idempotence
# =======================================================================================

def test_an_identical_entry_is_not_appended_twice(pm, bundle):
    first = pm.append_retrospective(bundle, _entry())
    second = pm.append_retrospective(bundle, _entry())
    assert first["appended"] is True
    assert second["appended"] is False
    assert second["id"] == first["id"], "the existing id must be returned, not a new one"
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    # Line-anchored: the file HEADER legitimately mentions "`## RE-NNN`" in prose, so a
    # bare substring count would read it as a second entry. The product's own regexes are
    # `^## RE-` under re.M for the same reason.
    assert len(re.findall(r"^## RE-\d+", text, re.M)) == 1


def test_idempotence_ignores_the_when_field(pm, bundle):
    """Re-running a step on a later date is the same finding, not a new one."""
    pm.append_retrospective(bundle, _entry(when="2026-01-01"))
    again = pm.append_retrospective(bundle, _entry(when="2026-12-31"))
    assert again["appended"] is False, (
        "the same finding recorded on a different date was duplicated; identity must "
        "exclude `when`"
    )


def test_a_genuinely_different_entry_is_appended(pm, bundle):
    """The negative control: idempotence must not swallow real new entries."""
    pm.append_retrospective(bundle, _entry())
    other = pm.append_retrospective(bundle, _entry(asked="a completely different question"))
    assert other["appended"] is True and other["id"] == "RE-002"


def test_dry_run_writes_nothing(pm, bundle):
    r = pm.append_retrospective(bundle, _entry(), dry_run=True)
    assert r["appended"] is True
    assert not (bundle / pm.RETROSPECTIVE_FILE).exists(), "--dry-run must not write"


# =======================================================================================
# index.md listing (pass-1 C6)
# =======================================================================================

def test_the_file_is_added_to_the_index_listing(pm, bundle):
    pm.append_retrospective(bundle, _entry())
    index = (bundle / "index.md").read_text(encoding="utf-8")
    assert f"({pm.RETROSPECTIVE_FILE})" in index, (
        "the retrospective is absent from index.md. A member missing from the reserved "
        "listing is exactly the portability gap this file exists to help close — the "
        "bundle's cold-reader contract would be violated by the very file added to support it."
    )


def test_the_index_entry_is_added_once(pm, bundle):
    for i in range(3):
        pm.append_retrospective(bundle, _entry(asked=f"q{i}"))
    index = (bundle / "index.md").read_text(encoding="utf-8")
    assert index.count(f"({pm.RETROSPECTIVE_FILE})") == 1


def test_a_bundle_without_an_index_still_writes_the_entry(pm, bundle):
    """Absence of index.md must degrade, not crash."""
    (bundle / "index.md").unlink()
    r = pm.append_retrospective(bundle, _entry())
    assert r["appended"] is True and r["index_updated"] is False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

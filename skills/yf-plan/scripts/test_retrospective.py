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


# =======================================================================================
# plan-071 Issue 1.1 — the `fidelity` kind (REQ-PLAN-084): two numbers, both REQUIRED
# =======================================================================================

def _fid(**kw) -> dict:
    base = _entry(kind="fidelity", stop_class="", asked="", answered="",
                  sc_flipped_post_approval="3", halts_post_irreversible="1",
                  evidence="retrospective-report --fidelity")
    base.update(kw)
    return base


def test_fidelity_is_a_kind_and_carries_both_numbers(pm, bundle):
    assert "fidelity" in pm.RETROSPECTIVE_KINDS
    assert set(pm.RETROSPECTIVE_FIDELITY_FIELDS) <= set(pm.RETROSPECTIVE_FIELDS)
    r = pm.append_retrospective(bundle, _fid())
    assert r["appended"] is True
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| `kind` | fidelity |" in text
    assert "| `sc_flipped_post_approval` | 3 |" in text
    assert "| `halts_post_irreversible` | 1 |" in text


def test_fidelity_refuses_a_missing_number(pm, bundle):
    """A fidelity entry with one number is a narration about the other."""
    with pytest.raises(ValueError, match="sc_flipped_post_approval"):
        pm.append_retrospective(bundle, _fid(sc_flipped_post_approval=""))
    with pytest.raises(ValueError, match="halts_post_irreversible"):
        pm.append_retrospective(bundle, _fid(halts_post_irreversible=""))
    with pytest.raises(ValueError, match="integer"):
        pm.append_retrospective(bundle, _fid(sc_flipped_post_approval="many"))
    assert not (bundle / pm.RETROSPECTIVE_FILE).exists(), "a refused entry wrote nothing"


def test_fidelity_accepts_no_record_for_halts_but_not_for_flips(pm, bundle):
    """A bundle predating the `landing-halt:` bullet reports `no-record`, never zero."""
    assert pm.append_retrospective(bundle, _fid(halts_post_irreversible="no-record"))["appended"]
    with pytest.raises(ValueError):
        pm.append_retrospective(bundle, _fid(sc_flipped_post_approval="no-record", asked="x"))


def test_fidelity_renders_as_the_existing_two_column_table(pm, bundle):
    pm.append_retrospective(bundle, _fid())
    text = (bundle / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    block = text[text.index("## RE-001"):]
    assert "| field | value |" in block and "| :-- | :-- |" in block
    assert not re.search(r"^\*\*[A-Za-z_ ]+:\*\*", block, re.M), "no bold-label lines"


def test_other_kinds_do_not_require_the_fidelity_numbers(pm, bundle):
    assert pm.append_retrospective(bundle, _entry(kind="stop"))["appended"]
    assert pm.append_retrospective(bundle, _entry(kind="deviation", asked="d"))["appended"]


# =======================================================================================
# plan-071 Issue 1.2 — `retrospective-report --fidelity` DERIVES the two numbers
# =======================================================================================

import subprocess as _sp


def _git(*args, cwd):
    _sp.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


_PLAN_ID = "plan-998-test-fidel1"

_PLAN_TEMPLATE = """---
type: Plan
okf_spec: OKF-PLAN
id: {pid}
status: executing
---
# Plan: fidelity fixture

**ID:** {pid}
**Status:** executing

## Objective
t

## Epics
### Epic 1: e
- Issue 1.1: do a thing

## Success Criteria
{preamble}| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | one | `{sc1}` → exit 0 | 1.1 |
| SC2 | two | `true` → exit 0 | 1.1 |
| SC3 | three | `true` → exit 0 | 1.1 |
"""


@pytest.fixture()
def fidelity_repo(tmp_path, monkeypatch):
    """A git repo with an INTAKE commit, then a post-approval edit to SC1's Verification."""
    root = tmp_path / "repo"
    pdir = root / "docs" / "plans" / _PLAN_ID
    pdir.mkdir(parents=True)
    _git("init", "-q", "-b", "main", ".", cwd=root)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T"),
                 ("commit.gpgsign", "false")):
        _git("config", k, v, cwd=root)
    (pdir / "plan.md").write_text(
        _PLAN_TEMPLATE.format(pid=_PLAN_ID, preamble="", sc1="true"), encoding="utf-8")
    (pdir / "log.md").write_text("# Log\n\n## 2026-01-01\n- scoping: init\n", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", f"{_PLAN_ID}: INTAKE approved (awaiting /yf-plan execute)",
         cwd=root)
    # The post-approval flip: SC1's cell changes. Uncommitted is fine — the diff is against
    # the intake commit, not against HEAD.
    (pdir / "plan.md").write_text(
        _PLAN_TEMPLATE.format(pid=_PLAN_ID, preamble="", sc1="test -d ."), encoding="utf-8")
    monkeypatch.chdir(root)
    return root, pdir


def test_fidelity_derivation_counts_a_flipped_cell_and_a_false_row(pm, fidelity_repo):
    root, pdir = fidelity_repo
    (pdir / "log.md").write_text(
        "# Log\n\n## 2026-01-02\n"
        "- landing-halt: L_PUSHED_1 l7_reconcile_writes irreversible=true\n"
        "- landing-halt: L_MERGED_UNCOMMITTED l3_validate_merged irreversible=false\n"
        "## 2026-01-01\n- scoping: init\n", encoding="utf-8")
    out = pm._fidelity_derive(pdir, recheck={"verdict": "FAIL", "failed": ["SC2"]}, root=root)
    assert out["intake_commit"], "the intake commit must be found by its fixed subject"
    kinds = {f["id"]: f["kind"] for f in out["sc_flipped"]}
    assert kinds == {"SC1": "amended", "SC2": "false-at-landing"}, kinds
    assert out["sc_flipped_post_approval"] == 2
    # Only the halt at/after L_PUSHED_1 counts; the L3 halt is pre-irreversible.
    assert out["halts_post_irreversible"] == 1
    assert out["source"] == "log.md"


def test_fidelity_reports_no_record_when_no_halt_bullet_exists(pm, fidelity_repo):
    root, pdir = fidelity_repo
    out = pm._fidelity_derive(pdir, recheck={"verdict": "PASS", "failed": []}, root=root)
    assert out["halts_post_irreversible"] == "no-record"
    assert out["source"] == "no-record"
    assert out["sc_flipped_post_approval"] == 1     # SC1 only


def test_fidelity_counts_a_manual_conversion_as_a_flip(pm, fidelity_repo):
    """R8: amending a criterion to `manual:` before landing is exactly what is counted."""
    root, pdir = fidelity_repo
    text = (pdir / "plan.md").read_text(encoding="utf-8")
    text = text.replace("| SC3 | three | `true` → exit 0 |", "| SC3 | three | manual: no |")
    (pdir / "plan.md").write_text(text, encoding="utf-8")
    out = pm._fidelity_derive(pdir, recheck=None, root=root)
    kinds = {f["id"]: f["kind"] for f in out["sc_flipped"]}
    assert kinds["SC3"] == "converted-to-manual"


def test_irreversible_boundary_is_l_pushed_1_and_rejected_push_2(pm):
    assert pm._landing_phase_is_irreversible("L_PUSHED_1")
    assert pm._landing_phase_is_irreversible("L_CLOSED")
    assert pm._landing_phase_is_irreversible("L_REJECTED_PUSH_2")
    assert not pm._landing_phase_is_irreversible("L_VALIDATED")
    assert not pm._landing_phase_is_irreversible("L_REJECTED_PUSH_1")
    assert not pm._landing_phase_is_irreversible("L_CONFLICT_MERGE")


def test_fidelity_report_runs_recheck_itself_and_records(pm, fidelity_repo):
    """The verb runs `recheck-criteria` ITSELF (pass-1 C11) and `--record` writes the kind."""
    from click.testing import CliRunner
    root, pdir = fidelity_repo
    r = CliRunner().invoke(pm.cli, ["retrospective-report", str(pdir), "--fidelity",
                                    "--record", "--timeout", "20", "--json"])
    assert r.exit_code == 0, r.output
    out = json.loads(r.output)
    assert out["recheck_verdict"] in ("PASS", "FAIL", "HARNESS_INCOMPLETE", "INCONCLUSIVE")
    assert out["sc_flipped_post_approval"] == 1
    assert out["recorded"]["appended"] is True
    text = (pdir / pm.RETROSPECTIVE_FILE).read_text(encoding="utf-8")
    assert "| `kind` | fidelity |" in text
    assert "| `halts_post_irreversible` | no-record |" in text


# =======================================================================================
# #364 — the criteria preamble env is established by recheck-criteria ITSELF
# =======================================================================================

def test_criteria_preamble_is_read_from_the_fence_before_the_table(pm):
    text = _PLAN_TEMPLATE.format(pid="p", preamble="```sh\nexport T=set-by-preamble\n```\n\n",
                                 sc1="true")
    assert pm._criteria_preamble(text).strip() == "export T=set-by-preamble"
    assert pm._criteria_preamble(_PLAN_TEMPLATE.format(pid="p", preamble="", sc1="true")) == ""


def test_recheck_establishes_the_preamble_env(pm, tmp_path, monkeypatch):
    from click.testing import CliRunner
    pdir = tmp_path / "plan-997-test-pream1"
    pdir.mkdir()
    (pdir / "plan.md").write_text(
        _PLAN_TEMPLATE.format(pid="plan-997-test-pream1",
                              preamble="```sh\nexport T=set-by-preamble\n```\n\n",
                              sc1='test "$T" = set-by-preamble'), encoding="utf-8")
    monkeypatch.delenv("T", raising=False)
    r = CliRunner().invoke(pm.cli, ["recheck-criteria", str(pdir), "--json", "--advisory",
                                    "--timeout", "20"])
    out = json.loads(r.output)
    assert out["preamble_present"] is True
    sc1 = next(c for c in out["criteria"] if c["id"] == "SC1")
    assert sc1["status"] == "holds", out

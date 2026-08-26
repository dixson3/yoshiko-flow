# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for audit check #9 — the `**Epic:**` ref resolves.

REQ-CLI-020 / plan-044 #143. Run from anywhere:

    uv run skills/yf-plan/scripts/test_epic_ref_audit.py

`bd` is NEVER shelled out to — `_all_plan_beads` is monkeypatched. No subprocess, no
network, in any test.

Covers all THREE states the requirement distinguishes:

  (fail) a dangling ref on a NON-grandfathered plan. This is the defect: a
         dangling-but-PRESENT field makes `resume-scan` report
         `found: true, total: 0`, so a resumed execute session reads "no open
         work" and skips the plan entirely — a silent false success.
  (warn) `bd` unavailable. A plan bundle is portable by contract; hard-failing its
         own audit merely for being read on a beads-less machine would punish the
         portability it is designed for.
  (pass) a ref that resolves.

Plus the severity choice that makes the check useful at all: it keys on
`missing_level`, NOT `okf_missing_level`. The latter downgrades every legacy bundle
to `warn` — which would have silently suppressed all 14 real dangling refs.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")

PLAN_ID = "plan-999-tester-abc123"
# After the portability activation date, so the plan is NOT grandfathered and
# `missing_level` is `fail` — the configuration under which check #9 must bite.
RECENT = "2026-08-01"


def _write_plan(tmp_path: Path, epic: str | None, scoped: str = RECENT) -> Path:
    pdir = tmp_path / PLAN_ID
    pdir.mkdir(parents=True, exist_ok=True)
    epic_line = f"**Epic:** {epic}\n" if epic else ""
    # DUAL-WRITE the frontmatter `epic:` key alongside the `**Epic:**` header line
    # (REQ-DATA-015). This helper wrote only the header line, so every test built on it
    # exercised exactly ONE of the two surfaces a real plan.md carries — and `clear-epic`
    # (REQ-CLI-027) has to remove BOTH. A fixture that can only ever contain one of them
    # cannot observe a verb that clears one and leaves the other, which is the precise
    # failure mode #207's operators hit by hand-editing plan.md.
    epic_fm = f"epic: {epic}\n" if epic else ""
    (pdir / "plan.md").write_text(
        f"---\ntype: Plan\nid: {PLAN_ID}\n{epic_fm}---\n"
        f"# Plan: tester\n\n**ID:** {PLAN_ID}\n**Status:** executing\n{epic_line}"
        f"**Phase log:**\n- {scoped} scoping: initial scope captured\n\n"
        "## Objective\n\ntest\n\n"
        "## Motivation\n\nbecause\n\n"
        "## Success Criteria\n\n1. x\n",
        encoding="utf-8",
    )
    return pdir


def _findings(pdir: Path, item: str):
    res = pm._audit_plan(pdir)
    return [f for f in res["findings"] if f["item"] == item]


def test_dangling_ref_is_a_hard_fail(tmp_path, monkeypatch):
    """The 14-bundle defect. A present-but-unresolvable ref must FAIL loudly."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, "beads-skills-mol-s3x")
    hits = _findings(pdir, "epic-ref")
    assert len(hits) == 1, "a dangling ref must produce exactly one finding"
    assert hits[0]["status"] == "fail"
    assert "does not resolve" in hits[0]["detail"]


def test_bd_unavailable_is_warn_not_fail(tmp_path, monkeypatch):
    """A portable bundle on a beads-less machine must not hard-fail its own audit."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-anything")
    hits = _findings(pdir, "epic-ref")
    assert len(hits) == 1
    assert hits[0]["status"] == "warn", "bd absence is not the plan's fault"
    assert "unavailable" in hits[0]["detail"]


def test_resolving_ref_produces_no_finding(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-9c09122b": {"id": "yf-9c09122b"}})
    pdir = _write_plan(tmp_path, "yf-9c09122b")
    assert _findings(pdir, "epic-ref") == []


def test_absent_epic_field_is_not_this_checks_business(tmp_path, monkeypatch):
    """No `**Epic:**` at all is a different condition — check #9 stays silent."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, None)
    assert _findings(pdir, "epic-ref") == []


def test_severity_is_missing_level_not_okf_missing_level(tmp_path, monkeypatch):
    """The choice that makes the check useful.

    All 14 real dangling refs live in OKF-LEGACY bundles (no plan.md frontmatter).
    Keying severity on `okf_missing_level` would downgrade every one of them to
    `warn` and suppress exactly what the check exists to surface. This asserts a
    legacy bundle still FAILS, provided it is not date-grandfathered.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = tmp_path / PLAN_ID
    pdir.mkdir()
    # NO frontmatter -> okf_legacy, so okf_missing_level would be "warn".
    (pdir / "plan.md").write_text(
        f"# Plan: tester\n\n**ID:** {PLAN_ID}\n**Status:** executing\n"
        f"**Epic:** beads-skills-mol-nxk\n**Phase log:**\n"
        f"- {RECENT} scoping: initial scope captured\n\n"
        "## Objective\n\ntest\n\n## Motivation\n\nbecause\n\n"
        "## Success Criteria\n\n1. x\n",
        encoding="utf-8",
    )
    res = pm._audit_plan(pdir)
    hits = [f for f in res["findings"] if f["item"] == "epic-ref"]
    assert len(hits) == 1
    assert hits[0]["status"] == "fail", (
        "a legacy bundle's dangling ref must still FAIL — using okf_missing_level "
        "here would have hidden all 14"
    )


# ---------------------------------------------------------------------------
# resume-scan's `epic_resolves` (REQ-CLI-013, plan-044 Issue 3.9)
# ---------------------------------------------------------------------------

def test_resume_scan_reports_epic_resolves_false_on_a_dangling_ref(tmp_path, monkeypatch):
    """The signal the EXECUTE path needs.

    `found` reports only that an id was RECORDED, so a dangling ref yields
    `found: true` with zero descendants — indistinguishable from a legitimately
    completed plan. `resume-scan` is the only verb the execute path consults, so
    without this the session reads "no open work" and skips the plan silently.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, "beads-skills-mol-GONE")
    res = pm._resume_scan(pdir)
    assert res["found"] is True, "the misleading signal is unchanged (a ref IS recorded)"
    assert res["epic_resolves"] is False, "the new signal must discriminate"
    assert res.get("total", 0) == 0


def test_resume_scan_epic_resolves_true_when_the_bead_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-ok": {"id": "yf-ok"}})
    pdir = _write_plan(tmp_path, "yf-ok")
    assert pm._resume_scan(pdir)["epic_resolves"] is True


def test_resume_scan_epic_resolves_is_none_when_unknowable(tmp_path, monkeypatch):
    """None, not False — `bd` unreadable must not libel a healthy plan.

    "No beads at all" cannot distinguish an absent database from an empty one.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-whatever")
    assert pm._resume_scan(pdir)["epic_resolves"] is None
    # And with no `**Epic:**` field at all there is nothing to resolve.
    (tmp_path / "b").mkdir()
    pdir2 = _write_plan(tmp_path / "b", None)
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    assert pm._resume_scan(pdir2)["epic_resolves"] is None




# --- plan-053 / #207: the SIX-VALUED `epic_state` -----------------------------------------
#
# THE DEFECT, RESTATED. `found` is one boolean carrying two facts whose handling is
# OPPOSITE: "a pointer is recorded" and "that pointer is live". A burned epic reports
# `found: true, total: 0`, which is indistinguishable from a legitimately completed plan, so
# `SKILL.md` §5.2 — which extracts only `found` — reads "no open work" and skips the plan
# entirely. `epic_resolves` has shipped since plan-044 and answers the second question
# already (D-11: read the check that exists, do not re-implement it); the defect is that
# nothing reads it.
#
# These five assertions fail today with `KeyError: 'epic_state'`, which is the strongest
# possible RED — the field does not exist at all.


def _scan(tmp_path, monkeypatch, epic, beads):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: beads)
    return pm._resume_scan(_write_plan(tmp_path, epic))


def _epic(bid, plan_dir, status="open"):
    return {"id": bid, "issue_type": "epic", "status": status,
            "metadata": {"plan_dir": plan_dir}}


def test_epic_state_none_when_no_epic_is_recorded(tmp_path, monkeypatch):
    r = _scan(tmp_path, monkeypatch, None, {"yf-other": _epic("yf-other", "/somewhere/else")})
    assert r["epic_state"] == "none"
    # EXECUTE must POUR here — this is the normal first execution.
    assert r["found"] is False, "back-compat: `found` keeps its meaning verbatim"


def test_epic_state_stale_on_a_dangling_ref(tmp_path, monkeypatch):
    """#207's wedge. The recorded id resolves to NOTHING."""
    r = _scan(tmp_path, monkeypatch, "yf-BURNED", {"yf-live": _epic("yf-live", "/elsewhere")})
    assert r["epic_state"] == "stale"
    # The two legacy fields are UNCHANGED — that is what makes `epic_state` additive.
    assert r["found"] is True
    assert r["epic_resolves"] is False


def test_epic_state_present_when_the_epic_resolves_with_open_work(tmp_path, monkeypatch):
    pdir = str(tmp_path / PLAN_ID)
    beads = {
        "yf-e": _epic("yf-e", pdir),
        "yf-e.1": {"id": "yf-e.1", "issue_type": "task", "status": "open", "parent": "yf-e"},
    }
    r = _scan(tmp_path, monkeypatch, "yf-e", beads)
    assert r["epic_state"] == "present"
    assert r["epic_resolves"] is True


def test_epic_state_complete_when_every_descendant_is_terminal(tmp_path, monkeypatch):
    pdir = str(tmp_path / PLAN_ID)
    beads = {
        "yf-e": _epic("yf-e", pdir, status="closed"),
        "yf-e.1": {"id": "yf-e.1", "issue_type": "task", "status": "closed", "parent": "yf-e"},
    }
    r = _scan(tmp_path, monkeypatch, "yf-e", beads)
    assert r["epic_state"] == "complete", (
        "an epic whose work is all terminal is COMPLETE, not PRESENT — and it must never "
        "re-pour"
    )


def test_epic_state_foreign_when_the_epic_belongs_to_another_bundle(tmp_path, monkeypatch):
    """EXP-005's measured live hazard: a COPIED bundle silently resumes another plan's epic."""
    beads = {"yf-e": _epic("yf-e", "/some/other/plan-042-someone-else")}
    r = _scan(tmp_path, monkeypatch, "yf-e", beads)
    assert r["epic_state"] == "foreign"
    assert r["epic_plan_dir"] == "/some/other/plan-042-someone-else", (
        "the caller must be able to report WHY, not merely THAT"
    )
    # It RESOLVES — which is exactly why `epic_resolves` alone cannot catch this.
    assert r["epic_resolves"] is True


def test_epic_state_unknown_when_bd_is_unreadable(tmp_path, monkeypatch):
    """`unknown` is NOT a synonym for "gone"."""
    r = _scan(tmp_path, monkeypatch, "yf-e", {})
    assert r["epic_state"] == "unknown", (
        "an unreachable tracker looks EXACTLY like a burned epic; guessing 'gone' produces "
        "the duplicate pour REQ-RESUME-004 exists to prevent"
    )
    assert r["epic_resolves"] is None


def test_epic_status_and_plan_dir_are_surfaced(tmp_path, monkeypatch):
    pdir = str(tmp_path / PLAN_ID)
    r = _scan(tmp_path, monkeypatch, "yf-e", {"yf-e": _epic("yf-e", pdir, status="in_progress")})
    assert r["epic_status"] == "in_progress"
    assert r["epic_plan_dir"] == pdir


def test_a_gates_only_bead_dict_does_not_libel_a_healthy_epic(tmp_path, monkeypatch):
    """The latent false negative D-11 names.

    `_all_plan_beads` MERGES two `bd list` calls. A partial failure yields a dict holding
    only the gate query's results — non-empty, so the `not beads` guard does not fire — in
    which a perfectly healthy epic reports `epic_resolves: false` and would be classified
    `stale`. A `stale` verdict sends EXECUTE to POUR, which is the duplicate-epic failure.
    """
    beads = {"yf-g": {"id": "yf-g", "issue_type": "gate", "status": "open", "metadata": {}}}
    r = _scan(tmp_path, monkeypatch, "yf-e", beads)
    assert r["epic_state"] == "unknown", (
        "a bead dict carrying no non-gate bead at all is not evidence that an epic is gone; "
        "it is evidence that the query was partial"
    )


# --- plan-053 / #207: `clear-epic` (REQ-CLI-027) -------------------------------------------


def test_clear_epic_removes_BOTH_dual_written_surfaces(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-BURNED")
    before = (pdir / "plan.md").read_text()
    assert "epic: yf-BURNED" in before and "**Epic:** yf-BURNED" in before

    res = pm._clear_epic(pdir, force=True)
    after = (pdir / "plan.md").read_text()
    assert "yf-BURNED" not in after, (
        "hand-editing reliably removes ONE of the two surfaces; the verb must remove both"
    )
    assert res["cleared"] is True


def test_clear_epic_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-BURNED")
    pm._clear_epic(pdir, force=True)
    res = pm._clear_epic(pdir, force=True)
    assert res["cleared"] is False and res.get("verdict") == "noop"


def test_clear_epic_refuses_on_present_and_unknown_without_force(tmp_path, monkeypatch):
    pdir_s = str(tmp_path / PLAN_ID)
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-e": _epic("yf-e", pdir_s)})
    pdir = _write_plan(tmp_path, "yf-e")
    res = pm._clear_epic(pdir, force=False)
    assert res["cleared"] is False and res["verdict"] == "refused", (
        "clearing a LIVE pointer strands real work"
    )

    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir2 = _write_plan(tmp_path / "u", "yf-e")
    res2 = pm._clear_epic(pdir2, force=False)
    assert res2["cleared"] is False and res2["verdict"] == "refused", (
        "clearing a pointer whose state could not be determined is that same act, blind"
    )


def test_clear_epic_reports_metadata_fallback_remains(tmp_path, monkeypatch):
    """R6, measured: clearing the fields does NOT reopen the pour path.

    `_resume_scan` falls back to the epic bead's `metadata.plan_dir`, so a surviving epic
    bead is still found. A verb that appears to succeed and changes nothing is the
    silent-success class this plan exists to close.
    """
    pdir_s = str(tmp_path / PLAN_ID)
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-e": _epic("yf-e", pdir_s)})
    pdir = _write_plan(tmp_path, "yf-e")
    res = pm._clear_epic(pdir, force=True)
    assert res["metadata_fallback_remains"] is True
    # And the fallback really does still resolve the epic.
    assert pm._resume_scan(pdir)["epic_id"] == "yf-e"


def test_clear_epic_keeps_the_intake_history_and_appends_pointer_cleared(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-BURNED")
    (pdir / "log.md").write_text(
        "# Log\n\n## 2026-08-25\n\n- intake: epic yf-BURNED poured\n", encoding="utf-8")
    pm._clear_epic(pdir, force=True, reason="burned by hand")
    log = (pdir / "log.md").read_text()
    assert "intake: epic yf-BURNED poured" in log, (
        "the record of WHAT WAS POURED survives the clearing of the pointer to it"
    )
    assert "pointer cleared" in log


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

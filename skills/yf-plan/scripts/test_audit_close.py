# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for `audit-close` (REQ-PLAN-075 / REQ-CLI-019, plan-043 #140).

Run from anywhere:  uv run skills/yf-plan/scripts/test_audit_close.py

The central property under test is a NEGATIVE one: this step must never be able to stop
completion. A fail-loud close-time audit would have blocked 22% of plans that legitimately
completed, so "advisory" is a safety property, not a stylistic preference — and a property
asserted only in prose is exactly what plan-043 exists to stop trusting.

Covers (tagged REQ-PLAN-075):
  (a) SC5 — a bundle with real failing findings still exits 0, so `set complete` proceeds;
  (b) the verdict is never `halting` for ANY finding set;
  (c) findings are IDENTICAL to the plan-phase `audit` engine (no second implementation);
  (d) SC6 — the §6.4 invocation order places `audit-close` above the `classify-deliverable`
      block (which contains the `set-deliverable-class` plan.md dual-write), parsed from
      SKILL.md source rather than assumed;
  (e) envelope conformance (REQ-COMPLETE-003) on every path;
  (f) the banner-vocabulary carve-out — no `FAIL-LOUD:` in the advisory wiring.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

_HERE = Path(__file__).resolve().parent
_SKILL_MD = _HERE.parent / "SKILL.md"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _bundle(tmp_path: Path, *, complete: bool) -> Path:
    """A plan bundle. `complete=False` omits the portability scaffolding, so the
    audit engine produces real failing findings."""
    pdir = tmp_path / "plan-997-audit-tester-abc123"
    pdir.mkdir(parents=True)
    body = (
        "---\ntype: Plan\nid: plan-997-audit-tester-abc123\n---\n"
        "# Plan: audit tester\n\n"
        "**ID:** plan-997-audit-tester-abc123\n\n"
        "## Objective\n\ntest\n\n"
    )
    if complete:
        body += "## Motivation\n\nbecause\n\n"
    body += "## Upstream Issues\n\n| Issue | Title | Disposition | Notes | Resolved By |\n"
    body += "| :-- | :-- | :-- | :-- | :-- |\n\n## Success Criteria\n\n1. x\n"
    (pdir / "plan.md").write_text(body, encoding="utf-8")
    (pdir / "log.md").write_text(
        "# Log\n\n## 2026-08-16\n\n- scoping: created\n", encoding="utf-8")
    if complete:
        (pdir / "index.md").write_text("# Index\n\n- plan.md\n", encoding="utf-8")
        (pdir / "context.md").write_text("# Context\n\nhost: t\n", encoding="utf-8")
        for sub in ("findings", "references", "reviews"):
            (pdir / sub).mkdir()
    return pdir


def _run(pdir: Path) -> tuple[int, dict]:
    res = CliRunner().invoke(pm.cli, ["audit-close", str(pdir), "--json"])
    assert res.output.strip(), "envelope must be on stdout on EVERY path"
    return res.exit_code, json.loads(res.output)


# ---------------------------------------------------------------------------
# (a)/(b) THE property: advisory, unconditionally
# ---------------------------------------------------------------------------

def test_failing_bundle_still_exits_zero(tmp_path):
    """SC5 — a failing bundle must not gate `set complete`."""
    pdir = _bundle(tmp_path, complete=False)
    rc, out = _run(pdir)
    assert out["fail_count"] > 0, (
        "fixture produced no failing findings — it no longer exercises the property"
    )
    assert out["verdict"] == "fail"
    assert rc == 0, "SC5: an advisory step must exit 0 even when it reports failures"
    assert out["advisory"] is True


def test_clean_bundle_passes(tmp_path):
    pdir = _bundle(tmp_path, complete=True)
    rc, out = _run(pdir)
    assert rc == 0 and out["advisory"] is True
    assert out["verdict"] in ("pass", "fail")   # content may still warn; exit is the point


def test_exit_code_is_zero_for_every_finding_set(tmp_path):
    """(b) There is no finding set for which this step halts."""
    for complete in (True, False):
        pdir = _bundle(tmp_path / f"c{complete}", complete=complete)
        rc, _ = _run(pdir)
        assert rc == 0, f"halted with complete={complete}"


def test_no_conditional_halt_option_exists():
    """The advisory guarantee must not be defeasible by a flag.

    A `--strict`/`--fail-on-findings` option would reintroduce exactly the 22% block
    rate the advisory classification exists to avoid, one caller at a time.
    """
    res = CliRunner().invoke(pm.cli, ["audit-close", "--help"])
    for forbidden in ("--strict", "--fail", "--gate", "--halt"):
        assert forbidden not in res.output, (
            f"`audit-close` exposes {forbidden}, which can make an advisory step halt"
        )


# ---------------------------------------------------------------------------
# (c) same engine as the plan-phase audit
# ---------------------------------------------------------------------------

def test_findings_identical_to_plan_phase_audit(tmp_path):
    """No second implementation — close-time and plan-time findings cannot diverge."""
    pdir = _bundle(tmp_path, complete=False)
    _, out = _run(pdir)
    engine = pm._audit_plan(pdir)
    assert out["findings"] == engine["findings"]
    assert out["audit_status"] == engine["status"]


def test_plan_phase_audit_still_halts(tmp_path):
    """The contrast that makes the separate verb necessary: `audit` DOES exit non-zero.

    If this ever passes with rc == 0, the two verbs have collapsed and the close chain
    silently inherited (or lost) a halt.
    """
    pdir = _bundle(tmp_path, complete=False)
    res = CliRunner().invoke(pm.cli, ["audit", str(pdir), "--json-output"])
    assert res.exit_code != 0, "the plan-phase `audit` gate must still halt on fail"


# ---------------------------------------------------------------------------
# (d) SC6 — ordering, parsed from SKILL.md source
# ---------------------------------------------------------------------------

_INVOKE_RE = re.compile(
    r"uv\s+run\s+\$\{SKILL_DIR\}/scripts/[A-Za-z_][\w.]*\.py(?:\s+(?P<verb>[a-z][\w-]*))?"
)


def _section_64() -> str:
    lines = _SKILL_MD.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("### 6.4"))
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("###")),
               len(lines))
    return "\n".join(lines[start:end])


def _invocation_order() -> list[str]:
    """Positions of actual INVOCATIONS, not of any prose mention of a verb name."""
    return [m.group("verb") or "close_cascade.py" for m in _INVOKE_RE.finditer(_section_64())]


def test_audit_close_runs_above_the_dual_write():
    """SC6 — above the `classify-deliverable` block, which contains the
    `set-deliverable-class` plan.md dual-write. Not merely above the `log.md` write.

    An audit placed below the close step's own writes judges artifacts that step just
    created — a real, previously-observed failure.
    """
    order = _invocation_order()
    assert "audit-close" in order, "audit-close is not wired into §6.4"
    i = order.index("audit-close")
    for later in ("classify-deliverable", "set-deliverable-class"):
        assert later in order, f"{later} vanished from §6.4"
        assert i < order.index(later), (
            f"audit-close runs AFTER {later}; it must run above the dual-write "
            "(REQ-COMPLETE-001 constraint 1 / REQ-PLAN-075)"
        )


def test_status_transition_is_last():
    """REQ-COMPLETE-001 constraint 4 — nothing follows `update-status`."""
    order = _invocation_order()
    assert order[-1] == "update-status", f"chain does not end in update-status: {order}"


def test_verify_reconcile_precedes_the_first_destructive_step():
    """REQ-COMPLETE-001 constraint 2."""
    order = _invocation_order()
    assert order.index("verify-reconcile") < order.index("close_cascade.py")


# ---------------------------------------------------------------------------
# (e)/(f) envelope + banner vocabulary
# ---------------------------------------------------------------------------

def test_envelope_conformance(tmp_path):
    for complete in (True, False):
        _, out = _run(_bundle(tmp_path / f"e{complete}", complete=complete))
        assert out["verdict"] in ("pass", "fail", "inconclusive")
        assert out["passed"] == (out["verdict"] == "pass")
        assert out["reason"]
        if out["verdict"] != "pass":
            assert out["remediation"]
            assert "capture" in out["remediation"], (
                "an advisory finding must recommend the remediation path"
            )


def test_advisory_wiring_avoids_fail_loud_vocabulary():
    """(f) `FAIL-LOUD:` is reserved for halting steps.

    Checks the audit-close wiring specifically, not the whole block — the halting steps
    below it legitimately use the banner.
    """
    block = _section_64()
    start = block.find("audit-close")
    end = block.find("classify-deliverable", start)
    assert start != -1 and end != -1
    # Only EXECUTED lines count. The wiring deliberately carries a `#` comment telling
    # authors NOT to add a FAIL-LOUD banner here; that prohibition must not trip its own
    # rule (which is itself a small instance of the comment-handling care this plan needed).
    executed = [
        ln for ln in block[start:end].splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert not any("FAIL-LOUD" in ln for ln in executed), (
        "the advisory audit-close wiring emits halting-step banner vocabulary"
    )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

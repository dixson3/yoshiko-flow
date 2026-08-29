# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
# ]
# ///
"""REQ-PLAN-080 as amended by plan-056 Issue 0.13/1.10 (#265).

Run from anywhere:  uv run skills/yf-plan/scripts/test_recheck_criteria.py

WHY THIS FILE EXISTS
--------------------
`recheck-criteria` counted an `inconclusive` row in NEITHER `failed` NOR `evaluated`, so an
unjudged criterion vanished from the verdict arithmetic: **one** green criterion alongside
**any number** of unjudged ones produced `verdict: PASS`, exit `0`, and the reason string
*"all 1 evaluated criterion/criteria hold"*. That sentence is true as written and profoundly
misleading as read, and it defeated the requirement's own rationale — *"a criterion is only as
good as the last time something re-ran it"* — with a criterion nothing can run. It affected
every plan in the repository, and was filed as CRITICAL upstream (#265).

`evaluated_fraction` was emitted and consumed by nothing, so the information needed to detect
the state was present and unread.

THE CONTROL IS A PAIR OF EXITS, NEVER A SINGLE NON-ZERO. A criterion asserting only "this
exits non-zero" is satisfied by the engine being ABSENT — `uv run <missing>.py` itself exits
2. So every arm below asserts the completion-binding exit AND the `--advisory` exit and that
they DIFFER.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MANAGER = _HERE / "plan_manager.py"


def _run(plan_dir: Path, *args, depth=None):
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)
    if depth is not None:
        env["YF_RECHECK_DEPTH"] = str(depth)
    else:
        env.pop("YF_RECHECK_DEPTH", None)
    proc = subprocess.run(
        ["uv", "run", str(_MANAGER), "recheck-criteria", str(plan_dir), "--json", *args],
        capture_output=True, text=True, env=env, timeout=300,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:  # pragma: no cover - diagnostic path
        pytest.fail(f"non-JSON stdout (rc={proc.returncode}):\n{proc.stdout}\n{proc.stderr}")


def _plan(tmp_path: Path, criteria_rows: str, name="plan-999-fixture-aaaaaa") -> Path:
    """A minimal bundle carrying only what `recheck-criteria` reads."""
    d = tmp_path / name
    d.mkdir(parents=True)
    (d / "log.md").write_text("# Log\n\n## 2026-08-28\n\n- scoping: fixture\n")
    (d / "plan.md").write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\n"
        f"id: {name}\nauthor: t\ncreated: '2026-08-28'\nstatus: reconciling\n---\n"
        f"# Plan: fixture\n\n**ID:** {name}\n**Status:** reconciling\n\n"
        "## Objective\nfixture\n\n## Motivation\nfixture\n\n"
        "## Upstream Issues\n| Issue | Title | Disposition | Notes | Resolved By |\n"
        "|-------|-------|-------------|-------|-------------|\n\n"
        "## Investigation Findings\nnone\n\n## Approach\nnone\n\n"
        "## Epics\n### Epic 1: e\n- Issue 1.1: a thing\n\n"
        "## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n\n"
        "### Reconcile Gate\n- Type: auto (all execution beads closed)\n- Blocks: reconcile step\n\n"
        "## Risks & Mitigations\n| # | Risk | Severity | Mitigation |\n| :-- | :-- | :-- | :-- |\n"
        "| R1 | r | low | m |\n\n"
        "## Success Criteria\n| # | Criterion | Verification | Discharged-by |\n"
        "| :-- | :-- | :-- | :-- |\n" + criteria_rows + "\n"
    )
    return d


# A criterion whose command EXISTS and succeeds -> judged, holds.
_GREEN = "| SC1 | it holds | `true` → exit 0 | 1.1 |\n"
# A criterion whose command CANNOT BE RUN -> 127, which the engine classifies `inconclusive`.
# This is the unjudged class-A row: the plan DECLARES it machine-readable and the harness
# could not judge it.
_UNJUDGED = "| SC2 | unjudgeable | `definitely-not-a-real-command-xyz` → exit 0 | 1.1 |\n"


def test_unjudged_class_a_blocks(tmp_path):
    """SC36: an unjudged class-A criterion BLOCKS completion instead of vanishing.

    The pre-fix behaviour on this exact fixture was `verdict: PASS`, exit **0**, reason
    "all 1 evaluated criterion/criteria hold" — with SC2 unjudged and invisible.
    """
    d = _plan(tmp_path, _GREEN + _UNJUDGED)

    rc, out = _run(d)
    assert rc == 1, f"expected a HALT at the completion binding, got {rc}: {out}"
    assert out["verdict"] == "HARNESS_INCOMPLETE"
    assert out["severity"] == "error"
    assert out["unjudged"] == ["SC2"]
    assert out["harness_incomplete"] is True
    # It is NOT reported as a criterion being false — that is a different claim.
    assert not out.get("failed")

    # THE SECOND BRANCH. Without it, an ABSENT engine (exit 2, or any non-zero) satisfies
    # the assertion above and the test is vacuous.
    rc_adv, out_adv = _run(d, "--advisory")
    assert rc_adv == 0, f"--advisory must not halt, got {rc_adv}: {out_adv}"
    assert rc_adv != rc, "the two bindings must produce DIFFERENT exits"
    assert out_adv["verdict"] == "PASS"


def test_pass_path_still_reports_the_gap(tmp_path):
    """`harness_incomplete` and `unjudged` are emitted on EVERY path, including PASS.

    A field emitted only on the failing path cannot be used to detect the condition
    BEFORE it becomes one — which is how `evaluated_fraction` came to be consumed by
    nothing.
    """
    d = _plan(tmp_path, _GREEN + _UNJUDGED)
    rc, out = _run(d, "--advisory")
    assert rc == 0 and out["verdict"] == "PASS"
    assert out["harness_incomplete"] is True and out["unjudged"] == ["SC2"]
    # And it says so in the reason, not only in a field a reader must know to look at.
    assert "UNJUDGED" in out["reason"]
    # A PASS carrying an unjudged row is `warn`, never `ok`.
    assert out["severity"] == "warn"


def test_all_judged_is_a_clean_pass(tmp_path):
    """The NON-VACUITY control: with nothing unjudged, the binding is silent.

    Without this arm the test suite would pass against an engine that returns
    HARNESS_INCOMPLETE unconditionally.
    """
    d = _plan(tmp_path, _GREEN)
    rc, out = _run(d)
    assert rc == 0, f"a fully judged plan must pass, got {rc}: {out}"
    assert out["verdict"] == "PASS" and out["severity"] == "ok"
    assert out["harness_incomplete"] is False and out["unjudged"] == []


def test_a_false_criterion_is_still_FAIL_not_HARNESS_INCOMPLETE(tmp_path):
    """The three verdicts stay DISTINGUISHABLE — this is the whole point of the amendment.

    FAIL = judged and false. HARNESS_INCOMPLETE = declared judgeable, not judged.
    Collapsing them re-creates the conflation one layer over.
    """
    d = _plan(tmp_path, "| SC1 | it is false | `false` → exit 0 | 1.1 |\n")
    rc, out = _run(d)
    assert rc == 1 and out["verdict"] == "FAIL"
    assert out["failed"] == ["SC1"]
    assert out["harness_incomplete"] is False


def test_unmigrated_plan_stays_INCONCLUSIVE(tmp_path):
    """A plan with NO clause-form criterion is INCONCLUSIVE (exit 2), unchanged.

    Measured at authoring time: 6 of 52 bundles carry the four-column shape and exactly 1
    carries a clause-form criterion, so INCONCLUSIVE is the EXPECTED verdict almost
    everywhere. HARNESS_INCOMPLETE must not reach it, or the amendment becomes a repo-wide
    outage rather than a check.
    """
    d = _plan(tmp_path, "| SC1 | prose only | manual: someone looks | 1.1 |\n")
    rc, out = _run(d)
    assert rc == 2 and out["verdict"] == "INCONCLUSIVE"
    assert out["severity"] == "warn"


def test_nested_depth_never_halts(tmp_path):
    """MID-FLIGHT RUNS STAY ADVISORY (REQ-PLAN-080).

    A criterion's own command routes through the plan's harness and therefore runs one
    level down under the close chain. Halting there would make every fixture-driven
    control valid standalone and failing under the chain.
    """
    d = _plan(tmp_path, _GREEN + _UNJUDGED)
    rc, out = _run(d, depth=1)
    assert rc == 0, f"depth 1 must not halt, got {rc}: {out}"
    assert out["at_completion_binding"] is False
    assert out["harness_incomplete"] is True    # still REPORTED, just not halting


def test_require_evaluated_threshold(tmp_path):
    """`--require-evaluated` lets a plan declare a lower bar DELIBERATELY.

    The point is that a lower bar is reached by declaration rather than by accident, which
    is what the shipped behaviour did for every plan in the repo.
    """
    d = _plan(tmp_path, _GREEN + _UNJUDGED)
    rc_strict, _ = _run(d, "--require-evaluated", "1.0")
    rc_loose, out_loose = _run(d, "--require-evaluated", "0.5")
    assert rc_strict == 1 and rc_loose == 0
    assert rc_strict != rc_loose
    # Even under the loosened threshold the gap is still reported, never hidden.
    assert out_loose["harness_incomplete"] is True


if __name__ == "__main__":
    # ARGUMENTS ARE FORWARDED (REQ-CLI-028). The bare `pytest.main([])` form this repo used
    # elsewhere DISCARDS `sys.argv`, so `uv run <this file> -k <name>` silently ran the whole
    # file — making every criterion routed through it assert "some test passed".
    sys.exit(pytest.main([__file__, *sys.argv[1:]]))

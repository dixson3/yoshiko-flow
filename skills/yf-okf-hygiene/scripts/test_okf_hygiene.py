#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest", "pyyaml"]
# ///
"""Tests for okf_hygiene.py — corpus-level OKF health (REQ-OKFH-001..010, #189).

THREE THINGS IN THIS HEADER ARE LOAD-BEARING, and each was measured:

  (a) the PEP 723 `dependencies` block — without it the target's own deps are never
      installed;
  (b) `import pytest` — without it `check-pytest-ran.sh`'s ASSERTION 0 returns INCONCLUSIVE
      (2), which would leave SEVEN criteria unjudged rather than failed;
  (c) the `__main__` RUNNER BLOCK at the bottom — without it `uv run <file>` merely IMPORTS
      the module, executes NO test, and exits **0**. Spiked on two otherwise-identical files
      each containing `assert False`: no-runner exit 0, runner exit 1. That is a coin flip,
      not a formality — 36 of 74 test files in this repo carry no `__main__` block — and
      without it SC17 would be a criterion that CANNOT FAIL.

Run:  uv run skills/yf-okf-hygiene/scripts/test_okf_hygiene.py
 (or: scripts/checks/check-pytest-ran.sh <this file> <test-name>)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("okf_hygiene", _HERE / "okf_hygiene.py")
hyg = importlib.util.module_from_spec(_spec)
sys.modules["okf_hygiene"] = hyg
_spec.loader.exec_module(hyg)

REPO = _HERE.parents[2]


def okf_read(path):
    """Frontmatter + body, VIA THE SHIPPED ENGINE — never a second parser in the test."""
    return hyg.okf.read_frontmatter(path)


# --- helpers ---------------------------------------------------------------------------

PLAN_MD = """---
type: Plan
okf_spec: OKF-PLAN
id: plan-900-fixture-aaaaaa
author: t
created: '2026-08-28'
status: complete
---
# Plan: {objective}

**ID:** plan-900-fixture-aaaaaa
**Status:** complete

**Phase log:**
{phaselog}

## Objective
{objective}

## Motivation
m

## Approach
a
"""

LEGACY_README = """# {name}

> {objective}

This plan folder is portable.

## File map

- `plan.md` — the plan.
- `context.md` — environment snapshot.
"""


def make_legacy(tmp_path, name="plan-900-fixture-aaaaaa", *, objective="An objective",
                readme_objective=None, phaselog="- 2026-08-01 scoping: started\n",
                legacy_name="README.md", extra=()):
    b = tmp_path / name
    (b / "findings").mkdir(parents=True)
    (b / "plan.md").write_text(PLAN_MD.format(objective=objective, phaselog=phaselog))
    (b / "context.md").write_text("# Context\n\nenvironment.\n")
    (b / "findings" / "exp-001.md").write_text("# A finding\n")
    (b / legacy_name).write_text(LEGACY_README.format(
        name=name, objective=readme_objective if readme_objective is not None else objective))
    for rel, text in extra:
        p = b / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return b


def _fingerprint(plan_dir: Path) -> str | None:
    """`plan.md`'s content fingerprint, FROM THE SHIPPED IMPLEMENTATION.

    Never re-derived here: a second implementation of a hash is a second hash, and the two
    would agree right up until the moment the answer mattered.
    """
    pm = REPO / "skills" / "yf-plan" / "scripts" / "plan_manager.py"
    if not pm.is_file():
        return None
    proc = subprocess.run(["uv", "run", str(pm), "fingerprint", "check", str(plan_dir),
                           "--json"], capture_output=True, text=True)
    try:
        return json.loads(proc.stdout).get("current_fingerprint")
    except Exception:
        return None


# --- classification core (REQ-OKFH-004) ------------------------------------------------

@pytest.mark.parametrize("legacy_name,expected", [
    ("README.md", "legacy-readme"),
    ("_index.md", "legacy-underscore-index"),
])
def test_two_variant_equivalence(tmp_path, legacy_name, expected):
    """REQ-OKFH-004/010 — the two legacy variants CLASSIFY to their own class, by detected
    member rather than by filename.

    **THE TRANSFORM ROUTE DOES NOT YET MATCH THE CLASSIFICATION ROUTE, AND THIS TEST NOW SAYS SO
    (plan-064 Issue 4.1/4.5).** Until the dry run became predictive (REQ-OKFH-011) this test
    asserted `would-backfill` for BOTH variants and passed — but only because the dry run never
    staged, so it could not see the `manufactured-hybrid` post-condition. Measured on the real
    apply path, before and after that change:

        README.md  ->  dry: would-backfill   apply: backfilled
        _index.md  ->  dry: halt             apply: halt (manufactured-hybrid)

    So `_index.md` under the `yf-plan` member ALWAYS halted under `--apply`; the previous green
    was the blind dry run disagreeing with apply, which is exactly the defect REQ-OKFH-011
    closes. The cause: `okf.migrate` is member-driven and OKF-PLAN's `index_source` is
    `README.md`, so for an `_index.md` bundle it scaffolds a fresh `index.md` and leaves
    `_index.md` beside it — the `hybrid-partial` state the tool refuses to create.

    Repairing that routing means changing `okf.migrate`'s `index_source` resolution across six
    vendored engine copies, which is outside every epic of plan-064. It is recorded as a finding
    and filed as a follow-on (Issues 4.5 / 5.3) rather than silently absorbed — and this test now
    asserts the MEASURED behaviour of each variant, so the divergence cannot be re-hidden.
    """
    b = make_legacy(tmp_path, legacy_name=legacy_name)
    cls, detail = hyg.classify(b)
    assert cls == expected
    assert detail["legacy_index"] == [legacy_name]

    plan = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")

    if legacy_name == "README.md":
        assert plan["action"] == "would-backfill"
        assert plan["steps"][0] == "migrate" and plan["steps"][-1] == "regenerate-listing"
    else:
        # THE RECORDED DIVERGENCE. Asserted, not skipped: if the routing is ever repaired this
        # arm FAILS and forces the finding above to be revisited, which is what makes it a
        # record rather than a comment.
        assert plan["action"] == "halt", (
            "the _index.md transform route now succeeds — REQ-OKFH-010's two-variant equivalence "
            "may have been delivered. Re-measure, update this arm, and close the follow-on."
        )
        assert [h["kind"] for h in plan["halts"]] == ["manufactured-hybrid"], plan

    # THE PREDICTIVE PROPERTY ITSELF (REQ-OKFH-011): whatever the dry run says, apply agrees.
    b2 = make_legacy(tmp_path / "apply-side", legacy_name=legacy_name)
    applied = hyg.backfill_one(tmp_path / "apply-side", b2, apply=True, skill="yf-plan")
    corresponding = {"would-backfill": "backfilled", "halt": "halt", "skip": "skip"}
    assert applied["action"] == corresponding[plan["action"]], (
        f"the dry run said {plan['action']!r} and apply did {applied['action']!r} — "
        f"the dry run is NOT predictive of apply (REQ-OKFH-011)"
    )


def test_classification_covers_every_class(tmp_path):
    """All five classes are REACHABLE. A class no fixture can produce is a class the audit
    can never report, which is indistinguishable from not having it."""
    seen = set()
    seen.add(hyg.classify(make_legacy(tmp_path / "a"))[0])
    seen.add(hyg.classify(make_legacy(tmp_path / "b", legacy_name="_index.md"))[0])

    hybrid = make_legacy(tmp_path / "c")
    (hybrid / "index.md").write_text("# i\n\n- [plan.md](plan.md)\n")
    seen.add(hyg.classify(hybrid)[0])

    conf = make_legacy(tmp_path / "d")
    (conf / "README.md").unlink()
    (conf / "index.md").write_text("# i\n\n- [plan.md](plan.md)\n")
    seen.add(hyg.classify(conf)[0])

    bare = tmp_path / "e" / "not-a-bundle"
    bare.mkdir(parents=True)
    (bare / "notes.md").write_text("# n\n")
    seen.add(hyg.classify(bare)[0])

    assert seen == set(hyg.CLASSES), f"unreachable class(es): {set(hyg.CLASSES) - seen}"


def test_audit_readonly_and_reindex_refusal(tmp_path):
    """SC15 / REQ-OKFH-003 + REQ-OKFH-010 — `audit` never writes, and `reindex` REFUSES a
    legacy prose index rather than appending a generated listing beneath it."""
    b = make_legacy(tmp_path)
    before = {p: p.stat().st_mtime_ns for p in sorted(b.rglob("*")) if p.is_file()}
    before_names = sorted(p.name for p in b.iterdir())

    rows = hyg.discover([tmp_path], 2, hyg.DEFAULT_EXCLUDE_GLOBS)
    assert b in rows                      # NON-VACUITY: it really inspected the bundle
    for r in rows:
        hyg.classify(r)

    after = {p: p.stat().st_mtime_ns for p in sorted(b.rglob("*")) if p.is_file()}
    assert before == after, "audit MUTATED the corpus"
    assert sorted(p.name for p in b.iterdir()) == before_names

    # `reindex` on a legacy prose index refuses (exit 1) rather than appending beneath it.
    proc = subprocess.run(
        ["uv", "run", str(_HERE / "okf_hygiene.py"), "reindex", str(b), "--apply"],
        capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout
    assert json.loads(proc.stdout)["verdict"] == "refused"
    assert not (b / "index.md").exists(), "a refusal must not have created an index"

    # POSITIVE CONTROL: on a conformant bundle the same verb works — so the refusal above is
    # the rule firing, not the verb being broken.
    (b / "README.md").unlink()
    (b / "index.md").write_text("---\nokf_version: '0.2'\n---\n\n# b\n\n- [plan.md](plan.md) - p\n")
    proc = subprocess.run(
        ["uv", "run", str(_HERE / "okf_hygiene.py"), "reindex", str(b), "--apply"],
        capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout


def test_root_detection_self_contained(tmp_path):
    """SC16 / REQ-OKFH-005 — finds an incubator-analog root the four known roots miss, skips
    worktrees, and skips frozen fixture trees, using a SELF-CONTAINED default set.

    Self-contained is the load-bearing word: the 40 foreign repositories this skill must be
    able to run in carry no yf-plan-private member file, so a default set that depended on
    one would make the skill unable to run anywhere but here.
    """
    (tmp_path / "yf" / "some-slug" / "plans" / "plan-901-x").mkdir(parents=True)
    (tmp_path / "yf" / "some-slug" / "plans" / "plan-901-x" / "plan.md").write_text("# p\n")
    (tmp_path / ".worktrees" / "wt" / "plan-902-y").mkdir(parents=True)
    (tmp_path / ".worktrees" / "wt" / "plan-902-y" / "plan.md").write_text("# p\n")
    (tmp_path / "docs" / "plans" / "p" / "assets" / "fixtures" / "plan-903-z").mkdir(parents=True)
    (tmp_path / "docs" / "plans" / "p" / "assets" / "fixtures" / "plan-903-z" / "plan.md").write_text("# p\n")

    found = {p.name for p in hyg.discover([tmp_path], 5, hyg.DEFAULT_EXCLUDE_GLOBS)}
    assert "plan-901-x" in found, "the incubator-analog root was missed"
    assert "plan-902-y" not in found, "a worktree was not skipped"
    assert "plan-903-z" not in found, "a frozen fixture tree was not skipped"

    # The default exclusion set names no consumer-private file.
    joined = " ".join(hyg.DEFAULT_EXCLUDE_DIRS) + " " + " ".join(hyg.DEFAULT_EXCLUDE_GLOBS)
    assert "OKF-EXTENSION" not in joined and "yf-plan" not in joined


# --- the transform (REQ-OKFH-006..009) --------------------------------------------------

def test_fingerprint_invariance(tmp_path):
    """SC9 / REQ-OKFH-009 — the backfill preserves `plan.md`'s fingerprinted sections.

    Recorded honestly: this is the WEAKEST of the three guarantees. The fingerprint covers
    `plan.md`'s content sections only and excludes every file the transform mutates, so a
    green here is very nearly a tautology. It is asserted because it is cheap and because its
    FAILURE would be meaningful — not because its success proves much.
    """
    b = make_legacy(tmp_path)
    before = _fingerprint(b)
    if before is None:
        pytest.skip("plan_manager.py unavailable in this address space")
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec
    assert _fingerprint(b) == before


def test_plan030_hybrid_log_preserved(tmp_path):
    """SC10 / REQ-OKFH-009 — every phase-log BULLET and DISTINCT DATE survives.

    Named for the measured case: plan-030 was found to strand 10 bullets across 2 dates. This
    is the signal the fingerprint is STRUCTURALLY BLIND to — the phase log lives above the
    first `## ` and is excluded from the hash — so it is checked separately and fail-closed.
    """
    phaselog = ("- 2026-08-01 scoping: started\n"
                "- 2026-08-01 review: pass 1\n"
                "- 2026-08-02 approved: operator approved\n")
    b = make_legacy(tmp_path, phaselog=phaselog)
    src_bul, src_dates = hyg._log_signature((b / "plan.md").read_text())
    assert len(src_dates) == 2 and len(src_bul) >= 3      # NON-VACUITY

    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec

    _, dst_dates = hyg._log_signature((b / "log.md").read_text())
    assert src_dates <= dst_dates, f"phase-log dates lost: {src_dates - dst_dates}"


def test_backfill_is_three_step_not_migrate_alone(tmp_path):
    """REQ-OKFH-006 — the transform is `migrate` -> DELETE -> REGENERATE, and the difference
    from `migrate` alone is OBSERVABLE: the legacy File-map prose is gone and the index is a
    real listing."""
    b = make_legacy(tmp_path)
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec
    idx = (b / "index.md").read_text()
    assert "## File map" not in idx, "the legacy prose survived — this was `migrate` alone"
    assert not (b / "README.md").exists()
    assert "- [plan.md](plan.md)" in idx
    assert "- [findings/exp-001.md](findings/exp-001.md)" in idx   # rule D reached inside


def test_backfill_never_worsens_the_audit_verdict(tmp_path):
    """SC12 / REQ-OKFH-009 — the per-bundle audit delta, and the reason the record exists."""
    b = make_legacy(tmp_path)
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec
    rank = {"pass": 0, "warn": 1, "fail": 2, "unknown": -1}
    before, after = rank[rec["before"]["verdict"]], rank[rec["after"]["verdict"]]
    if before < 0 or after < 0:
        pytest.skip("the shipped audit was unavailable in this address space")
    assert after <= before, f"regressed: {rec['before']} -> {rec['after']}"


def test_objective_divergence_halts(tmp_path):
    """SC/REQ-OKFH-007 — a legacy objective that differs from `plan.md`'s H1 HALTS.

    The comparator is the H1, and that is measured rather than chosen: over this repo's 31
    legacy bundles the H1 reading flags **7** divergences — D-5's independently recorded
    figure — while comparing the `## Objective` SECTION BODY flags 22. A halt class that
    fires on 22 of 31 is an outage, and it would train the operator to wave the gate through.
    """
    b = make_legacy(tmp_path, objective="The real objective",
                    readme_objective="A DIFFERENT objective")
    rec = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")
    assert rec["action"] == "halt"
    assert [h["kind"] for h in rec["halts"]] == ["objective-divergence"]
    # NON-VACUITY: agreeing objectives do NOT halt.
    ok = make_legacy(tmp_path / "agree", objective="Same", readme_objective="Same")
    assert hyg.backfill_one(tmp_path, ok, apply=False, skill="yf-plan")["action"] \
        == "would-backfill"


def test_hybrid_partial_halts(tmp_path):
    """REQ-OKFH-007 — the other halt class. Both surfaces exist and may disagree; which one
    the author meant is not derivable, so the tool refuses rather than choosing."""
    b = make_legacy(tmp_path)
    (b / "index.md").write_text("# i\n\n- [plan.md](plan.md)\n")
    rec = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")
    assert rec["action"] == "halt"
    assert "hybrid-partial" in [h["kind"] for h in rec["halts"]]


# =========================================================================================
# REQ-OKFH-008 as amended — CRASH RECOVERY, DRIVEN BY THE REAL SWAP (plan-064 Epic 3).
#
# `test_crash_recovery_all_states` USED TO LIVE HERE AND WAS REPLACED, NOT REPAIRED (Issue 3.6).
#
# THE MEASURED DIAGNOSIS. It HAND-CONSTRUCTED each journal state — `shutil.copytree`,
# `j.write("S1")`, `os.rename`, `j.write("S2")` — and NEVER INVOKED `backfill`'s swap. So it
# mocked the call site it existed to observe: applying Issue 3.1's phase-ordering change and
# re-running it yielded BYTE-IDENTICAL output, because it never executed the ordering it was
# meant to be checking. It was insensitive to the production ordering BY CONSTRUCTION, which is
# why it was green against violating code, and why patching its assertions would have left the
# false green intact under a new name.
#
# THE REPLACEMENT DRIVES THE REAL `backfill_one` SWAP and interposes a deterministic crash. Two
# seams, and WHICH ONE a window needs is not a style choice:
#
#   * the `os.rename` seam reaches windows delimited by a RENAME;
#   * the JOURNAL-WRITE seam reaches windows delimited by a JOURNAL WRITE — including the
#     `S3`-recorded / `S2`-physical window Issue 3.1 opens, which the rename seam CANNOT reach
#     by construction (it lies between a journal write and the rename that follows it).
#
# This is the same "every instrument was calibrated against the call site instead of the callee"
# class plan-063 recorded, on a third engine.
# =========================================================================================

class _Crash(RuntimeError):
    """A deterministic stand-in for SIGKILL, raised at a chosen seam inside the real swap."""


def _drive_swap_crashing(monkeypatch, root, bundle, *, at_journal=None, before_journal=None,
                         at_rename=None, skill="yf-plan"):
    """Run the REAL `backfill_one` and crash at one deterministic seam.

    ``at_journal``      crash AFTER the journal write of this phase (the record is durable).
    ``before_journal``  crash BEFORE it (the record still holds the PREVIOUS phase).
    ``at_rename``       crash BEFORE the Nth `os.rename` (1-based) inside the swap.
    """
    real_write = hyg.Journal.write
    real_rename = hyg.os.rename
    calls = {"rename": 0}

    def fake_write(self, phase, **extra):
        if before_journal is not None and phase == before_journal:
            raise _Crash(f"before journal write {phase}")
        real_write(self, phase, **extra)
        if at_journal is not None and phase == at_journal:
            raise _Crash(f"after journal write {phase}")

    def fake_rename(src, dst, *a, **k):
        calls["rename"] += 1
        if at_rename is not None and calls["rename"] == at_rename:
            raise _Crash(f"before rename {calls['rename']}")
        return real_rename(src, dst, *a, **k)

    monkeypatch.setattr(hyg.Journal, "write", fake_write)
    monkeypatch.setattr(hyg.os, "rename", fake_rename)
    try:
        hyg.backfill_one(root, bundle, apply=True, skill=skill)
    except _Crash:
        pass
    else:
        raise AssertionError("the seam never fired — this arm would be vacuous")
    finally:
        monkeypatch.setattr(hyg.Journal, "write", real_write)
        monkeypatch.setattr(hyg.os, "rename", real_rename)


def _assert_content_preserved(bundle, marker):
    """The bundle's content survived — as EITHER a roll-back OR a completed roll-forward.

    BOTH ARE CORRECT RECOVERIES AND THE DISTINCTION IS WORTH ASSERTING RATHER THAN GLOSSING.
    From the `S2`-physical window `recover` completes rename 2, so the bundle holds the
    TRANSFORMED content (`plan.md` with its phase log extracted into `log.md`); from the
    pre-rename-1 window it holds the ORIGINAL. What must never happen is a third outcome — a
    missing bundle, an empty `plan.md`, or a bundle whose objective has been lost — so the
    assertion enumerates the two legal states instead of pinning one.
    """
    assert (bundle / "plan.md").is_file(), "plan.md is gone"
    text = (bundle / "plan.md").read_text()
    assert text.strip(), "plan.md is empty"

    rolled_back = text == marker
    rolled_forward = (bundle / "index.md").is_file() and (bundle / "log.md").is_file()
    assert rolled_back or rolled_forward, (
        "the bundle is in NEITHER legal state: it is not the original content, and it is not a "
        "completed transform (index.md + log.md present)"
    )
    # Whichever it is, the plan's own subject matter survived.
    assert "## Objective" in text, "the plan's Objective section was lost"
    return "rolled-back" if rolled_back else "rolled-forward"


def _assert_recovers_intact(root, bundle, marker, *, expect_phase=None):
    """Recover, and assert the BUNDLE IS PRESENT with its content — the SC11 invariant."""
    j = hyg.Journal(root, bundle)
    rec = j.read()
    assert rec is not None, "no journal survived the crash — nothing to recover from"
    if expect_phase is not None:
        assert rec["phase"] == expect_phase, f"recorded {rec['phase']!r}, expected {expect_phase!r}"

    out = hyg.recover(root, bundle)
    assert bundle.is_dir(), f"THE BUNDLE DID NOT SURVIVE RECOVERY: {out}"
    out["outcome"] = _assert_content_preserved(bundle, marker)
    assert out["recovered"] is True, out
    assert not j.staging.exists(), f"staging residue: {out}"
    assert not j.stash.exists(), f"stash residue: {out}"
    assert not j.path.exists(), f"journal residue: {out}"
    return out


def test_crash_s1_bundle_present(tmp_path, monkeypatch):
    """SC11 — crash STAGED, BEFORE RENAME 1. The bundle is present; recovery must keep it.

    Swap-driven by construction, so it is one of the two arms Issue 3.8's control may pin to.
    """
    root = tmp_path / "r"
    root.mkdir()
    b = make_legacy(root)
    marker = (b / "plan.md").read_text()

    _drive_swap_crashing(monkeypatch, root, b, at_rename=1)

    # THE PHASE-ORDERING ASSERTION. Under the fixed ordering the journal already reads `S2`
    # here, even though physically rename 1 has NOT run. That over-approximation is the whole
    # point: recovery may believe more happened than did, never less. Against the OLD ordering
    # this window recorded `S1`.
    j = hyg.Journal(root, b)
    assert j.read()["phase"] == "S2", (
        "the journal does not record S2 before rename 1 — the phase-ordering fix (Issue 3.1) "
        "is not in effect, and a crash here would be recovered from a phase whose branch "
        "rmtree's the staged copy"
    )
    assert b.is_dir(), "precondition: the bundle is still present before rename 1"

    _assert_recovers_intact(root, b, marker, expect_phase="S2")


def test_crash_s2_errno66(tmp_path, monkeypatch):
    """SC11 / Issue 3.3 — no UNHANDLED errno-66, on the JOURNAL-WRITE seam.

    Red-team pass 5's window: `S2` is recorded while the bundle is still PRESENT, so a recovery
    that rolls forward renames staging onto a live directory and raises an uncaught `OSError`
    (`ENOTEMPTY` — errno 66 on macOS, 39 on Linux). No data is lost, but `recover()` wedges
    IDEMPOTENTLY: every later invocation raises the same exception. SC11 forbids it.

    The `os.rename` seam cannot reach this window — it lies between a journal write and the
    rename that follows — which is the same blindness diagnosed for `S3`. Hence the journal seam.
    """
    root = tmp_path / "r"
    root.mkdir()
    b = make_legacy(root)
    marker = (b / "plan.md").read_text()

    # Crash immediately AFTER `S2` is written — before staging, before rename 1.
    _drive_swap_crashing(monkeypatch, root, b, at_journal="S2")

    j = hyg.Journal(root, b)
    assert j.read()["phase"] == "S2"
    assert b.is_dir(), "precondition: the bundle is present while S2 is recorded"

    # MUST NOT RAISE. The assertion is the absence of an exception, so it is written as a call.
    out = hyg.recover(root, b)
    assert b.is_dir(), f"the bundle did not survive: {out}"
    # Crashed BEFORE rename 1, so this window must roll BACK — the original content, exactly.
    assert _assert_content_preserved(b, marker) == "rolled-back", out
    assert out["recovered"] is True, out

    # IDEMPOTENT: a second recovery is a clean no-op, not a second exception.
    again = hyg.recover(root, b)
    assert again["recovered"] is False and "nothing to recover" in again["action"], again
    assert b.is_dir()


def test_crash_s3_recorded_physical_s2(tmp_path, monkeypatch):
    """SC11 / Issue 3.9 — THE WINDOW ISSUE 3.1 OPENS, and the one that would destroy the bundle.

    `S3` is written BEFORE rename 2, so a crash in between records `S3` while the physical state
    is `S2`: the bundle is ABSENT, staging and stash both present. The SHIPPED `S3`/`S4` branch
    assumed the swap had completed and unconditionally `rmtree`d both — returning
    `recovered: True, "completed cleanup"` WITH THE BUNDLE DESTROYED.

    So the phase-ordering fix alone would have RELOCATED the total-loss window from `S1` to `S3`
    rather than closing it. This arm is what makes that non-hypothetical.

    IT MUST USE THE JOURNAL-WRITE SEAM. The `os.rename` seam cannot reach this window by
    construction — an arm hung off it is blind to exactly the defect this test exists for.
    """
    root = tmp_path / "r"
    root.mkdir()
    b = make_legacy(root)
    marker = (b / "plan.md").read_text()

    _drive_swap_crashing(monkeypatch, root, b, at_journal="S3")

    j = hyg.Journal(root, b)
    # THE PRECONDITIONS ARE THE POINT — assert the window really is the dangerous one.
    assert j.read()["phase"] == "S3", "the fixture did not reach the S3-recorded window"
    assert not b.exists(), "S3-recorded/S2-physical means the bundle is ABSENT"
    assert j.staging.exists(), "staging must survive — rename 2 has not run"
    assert j.stash.exists(), "the stash must survive — it holds the original"

    out = _assert_recovers_intact(root, b, marker, expect_phase="S3")
    assert out.get("physical") == "S2", out


def test_crash_s4_recorded_physical_s3(tmp_path, monkeypatch):
    """SC11 — `S4` is written BEFORE the stash cleanup, so it too may be one step ahead."""
    root = tmp_path / "r"
    root.mkdir()
    b = make_legacy(root)

    _drive_swap_crashing(monkeypatch, root, b, at_journal="S4")

    j = hyg.Journal(root, b)
    assert j.read()["phase"] == "S4"
    assert b.is_dir(), "rename 2 completed, so the bundle is present"
    assert j.stash.exists(), "the stash has not been cleaned up yet — that is the window"

    out = hyg.recover(root, b)
    assert out["recovered"] is True, out
    assert b.is_dir() and (b / "index.md").is_file(), "the TRANSFORMED bundle must survive"
    assert not j.stash.exists() and not j.path.exists()


def test_crash_recovery_every_reachable_state_survives(tmp_path, monkeypatch):
    """SC11 / REQ-OKFH-008 — THE REPLACEMENT for `test_crash_recovery_all_states` (Issue 3.6).

    Every seam below drives the REAL `backfill_one` swap. "All states" means all PHYSICAL states
    under the amended over-approximation reading: `S1` is recovery-time-only and is never
    WRITTEN, so enumerating recorded labels would leave the `S1` window — the one where the
    bundle is destroyed — unexercised. That is why the table is keyed on seams, not on labels.
    """
    seams = [
        ("before-staging",   dict(at_journal="S2"), "S2"),
        ("before-rename-1",  dict(at_rename=1),     "S2"),
        ("before-rename-2",  dict(at_journal="S3"), "S3"),
        ("before-cleanup",   dict(at_journal="S4"), "S4"),
    ]
    seen_phases = set()
    for name, kw, expect in seams:
        root = tmp_path / name
        root.mkdir()
        b = make_legacy(root)
        marker = (b / "plan.md").read_text()

        _drive_swap_crashing(monkeypatch, root, b, **kw)
        j = hyg.Journal(root, b)
        rec = j.read()
        assert rec is not None, f"{name}: no journal survived"
        assert rec["phase"] == expect, f"{name}: recorded {rec['phase']!r}, expected {expect!r}"
        seen_phases.add(rec["phase"])

        out = hyg.recover(root, b)
        # THE ONE INVARIANT THAT HOLDS FROM EVERY SEAM: the bundle exists and its content is
        # intact. Everything else about recovery is negotiable; this is not.
        assert b.is_dir(), f"{name}: THE BUNDLE DID NOT SURVIVE RECOVERY — {out}"
        _assert_content_preserved(b, marker)
        assert out["recovered"] is True, f"{name}: {out}"
        assert not j.staging.exists() and not j.stash.exists() and not j.path.exists(), \
            f"{name}: residue after recovery — {out}"

    # NON-VACUITY: the seams really did produce distinct recorded phases, not four of one.
    assert seen_phases == {"S2", "S3", "S4"}, seen_phases
    # ...and `S1` is never WRITTEN, which is the amended table's claim.
    assert "S1" not in seen_phases
    assert set(hyg.STATES) == {"S0", "S1", "S2", "S3", "S4"}, hyg.STATES


def test_recover_verb_exists(tmp_path, monkeypatch):
    """SC12 / Issue 3.2 — recovery is OPERATOR-INVOCABLE, not merely present as a function."""
    root = tmp_path / "r"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    b = make_legacy(root)
    marker = (b / "plan.md").read_text()

    _drive_swap_crashing(monkeypatch, root, b, at_journal="S3")
    assert not b.exists(), "precondition: the crash left the bundle absent"

    # DRY RUN BY DEFAULT — it reports the journal and changes nothing.
    dry = _run(root, "recover")
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert json.loads(dry.stdout)["journals"], dry.stdout
    assert not b.exists(), "the dry run recovered something — it must not"

    applied = _run(root, "recover", "--apply")
    assert applied.returncode == 0, applied.stdout + applied.stderr
    assert b.is_dir(), "the verb did not recover the bundle"
    _assert_content_preserved(b, marker)


def test_backfill_refuses_stale_journal(tmp_path, monkeypatch):
    """SC12 / Issue 3.4 — `backfill` REFUSES over a journal from an unfinished run.

    Measured: nothing looked. `recover()` had no caller and no verb, so a stale journal was never
    noticed and the next `backfill` would stage over a half-swapped bundle.
    """
    root = tmp_path / "r"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    b = make_legacy(root)

    _drive_swap_crashing(monkeypatch, root, b, at_journal="S3")
    assert hyg.stale_journals(root), "precondition: a stale journal exists"

    proc = _run(root, "backfill", "--root", ".", "--apply")
    assert proc.returncode == 1, proc.stdout
    out = json.loads(proc.stdout)
    assert out["verdict"] == "refused"
    assert out["stale_journals"], out
    assert "recover" in out["remediation"]

    # ...and after recovering, backfill runs again — the refusal is a gate, not a wall.
    assert _run(root, "recover", "--apply").returncode == 0
    assert not hyg.stale_journals(root)
    assert _run(root, "backfill", "--root", ".", "--apply").returncode == 0


def test_backfill_leaves_no_residue(tmp_path):
    """REQ-OKFH-008 — a completed transform leaves NO scaffolding behind, INCLUDING the empty
    parent directories.

    This is not tidiness. The staging parent lives at `<root>/.okf-hygiene-staging`, i.e.
    inside the very directory the corpus drift driver enumerates with `docs/plans/*` — so two
    leftover empty directories were counted as two extra bundles on the live corpus
    (64 -> 66 enumerated, both reported `no-index`). A tool that inflates the census it exists
    to clean is reporting on itself, and the earlier version of this suite asserted only that
    the staging CHILD was gone, which is why it passed while the parent accumulated.
    """
    b = make_legacy(tmp_path)
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec

    residue = [p for p in tmp_path.iterdir()
               if p.name in (hyg.STAGING_DIR, hyg.JOURNAL_DIR)
               or p.name.endswith(".okf-stash")]
    assert residue == [], f"scaffolding residue survived the transform: {residue}"
    # ...and nothing dot-prefixed at all, which is the shape the drift driver's glob catches.
    assert [p.name for p in tmp_path.iterdir() if p.name.startswith(".okf-")] == []


def test_journal_is_fsynced_and_inside_the_tree(tmp_path):
    """REQ-OKFH-008 — staging lives INSIDE the repo tree, never a system temp dir.

    A cross-filesystem staging turns `os.rename` into a copy, which voids every durability
    claim the journal makes (measured EXDEV risk).
    """
    b = make_legacy(tmp_path)
    j = hyg.Journal(tmp_path, b)
    assert j.staging.is_relative_to(tmp_path)
    assert j.stash.is_relative_to(tmp_path)
    assert j.path.is_relative_to(tmp_path)
    j.write("S1")
    assert json.loads(j.path.read_text())["phase"] == "S1"


def test_underscore_index_live_target(tmp_path):
    """SC13 / REQ-OKFH-010 — the `_index.md` route is exercised against the ONE LIVE in-repo
    target, not only fixtures.

    Scope is recorded honestly rather than hidden: the 47% figure motivating this route is
    227-of-243 in a single FOREIGN repository this plan may not touch, so beyond this one
    bundle the route is built against self-authored fixtures.
    """
    live = REPO / "docs" / "research" / "001-okf-compliance-delta"
    if not live.is_dir():
        pytest.skip("the live _index.md target is not present in this address space")
    cls, detail = hyg.classify(live)
    assert cls in ("legacy-underscore-index", "conformant"), (cls, detail)
    if cls == "legacy-underscore-index":
        assert detail["legacy_index"] == ["_index.md"]
        # Exercise the transform on a COPY — the live target is never mutated by a test.
        work = tmp_path / "live"
        shutil.copytree(live, work)
        rec = hyg.backfill_one(tmp_path, work, apply=True, skill="yf-research")
        assert rec["action"] == "backfilled", rec
        assert (work / "index.md").is_file() and not (work / "_index.md").exists()


# =========================================================================================
# REQ-OKFH-010 as amended + REQ-OKFH-013 — the RECORD, and the three REFUSALS (plan-064 Epic 2).
#
# `test_restore_round_trip` USED TO LIVE HERE AND WAS REPLACED, NOT REPAIRED (Issue 2.8).
# Measured: it exited 0 against the `restore` EXP-001 proved is NOT record-driven. It
# hand-constructed an UNVERSIONED record carrying no operations and then asserted on the op
# list `restore` RE-DERIVED from `rglob` + `git ls-files` — so it asserted the presence of the
# very behaviour `REQ-OKFH-010` forbids, and would have passed under both implementations.
# A test that passes under both measures nothing. Patching its assertions would have left the
# false green intact under a familiar name, which is why the replacement asserts the reversal is
# DRIVEN BY THE RECORDED OP LIST and fails against a filesystem-derived one.
# =========================================================================================

def _git_legacy_repo(tmp_path, **kw):
    """A legacy bundle inside a real git work tree, COMMITTED.

    Committed on purpose: `restore`'s mechanism is `git checkout`, so an uncommitted fixture
    exercises the untracked-at-HEAD refusal instead of the happy path — which is a different
    test (`test_restore_refuses_untracked`).
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    b = make_legacy(root, **kw)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
                   cwd=root, check=True)
    return root, b


def _run(root, *args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["uv", "run", str(_HERE / "okf_hygiene.py"), *args],
                          capture_output=True, text=True, cwd=root, env=e)


def _backfill_with_record(root, bundle_parent="."):
    """Run a real `backfill --apply --record` and return (proc, record dict)."""
    proc = _run(root, "backfill", "--root", bundle_parent, "--apply", "--record", "rec.json")
    rec_path = root / "rec.json"
    data = json.loads(rec_path.read_text()) if rec_path.is_file() else None
    return proc, data, rec_path


def test_backfill_record_is_versioned_and_carries_operations(tmp_path):
    """Issue 2.1 / REQ-OKFH-010 + REQ-OKFH-013 — the record RECORDS."""
    root, b = _git_legacy_repo(tmp_path)
    proc, data, _ = _backfill_with_record(root)
    assert data is not None, proc.stdout + proc.stderr
    assert data["schema_version"] == hyg.RECORD_SCHEMA_VERSION

    entries = data["bundles"]
    assert entries, f"no bundle recorded: {proc.stdout}"
    ops = entries[0]["operations"]
    assert ops, "the record carries NO operations — this is the exact EXP-001 defect"

    kinds = {o["kind"] for o in ops}
    assert kinds <= {"created", "deleted", "modified"}, kinds
    # The transform's signature: index.md/log.md CREATED, the legacy README DELETED.
    assert any(o["path"].endswith("index.md") and o["kind"] == "created" for o in ops), ops
    assert any(o["path"].endswith("log.md") and o["kind"] == "created" for o in ops), ops
    assert any(o["path"].endswith("README.md") and o["kind"] == "deleted" for o in ops), ops
    # Content hashes, not just names — a reversal claim is checkable only against them.
    for o in ops:
        if o["kind"] in ("created", "modified"):
            assert o["sha256_after"], o
        if o["kind"] in ("deleted", "modified"):
            assert o["sha256_before"], o


def test_restore_record_driven(tmp_path):
    """SC8 / REQ-OKFH-010 — the reversal is DRIVEN BY THE RECORDED OP LIST.

    THE ARM THAT REPLACES `test_restore_round_trip`. It is built so a `restore` that re-derives
    from `rglob` + `git ls-files` FAILS it: the record is mutated to omit one created path, and a
    record-driven restore must then leave that path alone. A filesystem-derived restore cannot
    see the omission — it re-discovers the file and unlinks it anyway — so the two
    implementations are DISTINGUISHABLE here, which is precisely what the old test lacked.
    """
    root, b = _git_legacy_repo(tmp_path)
    _, data, rec_path = _backfill_with_record(root)
    assert (b / "index.md").is_file() and (b / "log.md").is_file()

    # NON-VACUITY: both files really were recorded as `created`.
    created = [o["path"] for o in data["bundles"][0]["operations"] if o["kind"] == "created"]
    assert any(p.endswith("index.md") for p in created), created
    assert any(p.endswith("log.md") for p in created), created

    # Drop `log.md` from the RECORD only. The file stays on disk.
    data["bundles"][0]["operations"] = [
        o for o in data["bundles"][0]["operations"] if not o["path"].endswith("log.md")
    ]
    rec_path.write_text(json.dumps(data))

    proc = _run(root, "restore", "--record", "rec.json", "--apply", "--force")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    assert not (b / "index.md").exists(), "a RECORDED created path was not reversed"
    assert (b / "log.md").exists(), (
        "an UNRECORDED path was unlinked — the reversal is driven by the filesystem, not by "
        "the record (REQ-OKFH-010's record-driven clause)"
    )


def test_restore_bundle_filter(tmp_path):
    """SC8 / REQ-OKFH-010 — a batch record does not force whole-batch reversal (Issue 2.4)."""
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    a = make_legacy(root, name="plan-901-fixture-aaaaaa")
    c = make_legacy(root, name="plan-902-fixture-bbbbbb")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "s"],
                   cwd=root, check=True)

    _, data, _ = _backfill_with_record(root)
    assert len(data["bundles"]) == 2, data          # NON-VACUITY: it really is a batch.
    assert (a / "index.md").is_file() and (c / "index.md").is_file()

    proc = _run(root, "restore", "--record", "rec.json", "--bundle", a.name, "--apply", "--force")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not (a / "index.md").exists(), "the named bundle was not reversed"
    assert (c / "index.md").is_file(), "an UNNAMED bundle was reversed — the filter is not honoured"

    # An unknown --bundle is a REFUSAL, never a silent reversal of a different set.
    bad = _run(root, "restore", "--record", "rec.json", "--bundle", "no-such-bundle", "--apply")
    assert bad.returncode == 1, bad.stdout
    assert json.loads(bad.stdout)["verdict"] == "refused"


def test_restore_refuses_legacy_record(tmp_path):
    """SC8 / REQ-OKFH-013 — an UNVERSIONED record is REFUSED, not misread.

    This is the arm that catches the silent no-op: the legacy shape carries no operations, so a
    record-driven restore reading it would reverse NOTHING and report `pass`.
    """
    root, b = _git_legacy_repo(tmp_path)
    _backfill_with_record(root)

    # The pre-REQ-OKFH-013 shape, verbatim: a verdict, and no operations.
    (root / "legacy.json").write_text(json.dumps({"bundles": [
        {"bundle": b.name, "before": {"verdict": "pass"}, "after": {"verdict": "pass"}}]}))

    proc = _run(root, "restore", "--record", "legacy.json", "--apply")
    assert proc.returncode == 1, proc.stdout
    out = json.loads(proc.stdout)
    assert out["verdict"] == "refused"
    assert "schema_version" in out["reason"]
    # AND IT REVERSED NOTHING: refusal means refusal, not a partial pass.
    assert (b / "index.md").is_file()

    # An unrecognised FUTURE version is refused too — refusing beats guessing field meanings.
    (root / "future.json").write_text(json.dumps({"schema_version": 999, "bundles": []}))
    fut = _run(root, "restore", "--record", "future.json", "--apply")
    assert fut.returncode == 1, fut.stdout
    assert json.loads(fut.stdout)["verdict"] == "refused"


def test_restore_refuses_non_git(tmp_path):
    """SC9 / REQ-OKFH-010 — LOSS PATH 1: a non-git tree. Measured: the bundle was DELETED."""
    root, b = _git_legacy_repo(tmp_path)
    _, data, _ = _backfill_with_record(root)

    # Move the backfilled bundle and its record OUT of any work tree.
    loose = tmp_path / "loose"
    loose.mkdir()
    shutil.copytree(b, loose / b.name)
    (loose / "rec.json").write_text(json.dumps(data))

    # NON-VACUITY: this really is not a work tree.
    assert not hyg._is_git_tree(loose)
    before = sorted(p.name for p in (loose / b.name).iterdir())
    assert before, "fixture bundle is empty; the arm would be vacuous"

    proc = _run(loose, "restore", "--record", "rec.json", "--apply")
    assert proc.returncode == 1, proc.stdout
    assert json.loads(proc.stdout)["verdict"] == "refused"
    # THE POINT OF THE ARM: nothing was deleted.
    assert sorted(p.name for p in (loose / b.name).iterdir()) == before


def test_restore_refuses_untracked(tmp_path):
    """SC9 / REQ-OKFH-010 — LOSS PATH 2: the bundle is untracked at HEAD. Measured: TOTAL LOSS.

    The realistic case for an uncommitted plan: nothing to check out, so the unlink pass runs
    alone and takes the whole bundle with it.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    # A commit that does NOT contain the bundle, so HEAD exists but the bundle is absent from it.
    (root / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "add", "seed.txt"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
                   cwd=root, check=True)
    b = make_legacy(root)

    _, data, _ = _backfill_with_record(root)
    assert data["bundles"], data

    # NON-VACUITY: the bundle really is absent from HEAD.
    assert not hyg._tracked_at_head(root, f"{b.name}/plan.md")
    before = sorted(p.name for p in b.iterdir())

    proc = _run(root, "restore", "--record", "rec.json", "--apply")
    assert proc.returncode == 1, proc.stdout
    assert json.loads(proc.stdout)["verdict"] == "refused"
    assert sorted(p.name for p in b.iterdir()) == before, "the bundle was mutated despite refusal"


def test_restore_refuses_dirty(tmp_path):
    """SC9 / REQ-OKFH-010 — LOSS PATH 3: post-backfill edits.

    Measured: every untracked file in the bundle was unlinked, with no dirty-tree guard and no
    warning. Overridable by explicit `--force` — a deliberate re-reversal over known local edits
    is legitimate if rare — but the operator must SAY SO.
    """
    root, b = _git_legacy_repo(tmp_path)
    _backfill_with_record(root)

    # An edit made AFTER the backfill, to a file the backfill created.
    (b / "index.md").write_text((b / "index.md").read_text() + "\n<!-- hand edit -->\n")
    precious = b / "notes-since-backfill.md"
    precious.write_text("# work that exists nowhere else\n")

    proc = _run(root, "restore", "--record", "rec.json", "--apply")
    assert proc.returncode == 1, proc.stdout
    out = json.loads(proc.stdout)
    assert out["verdict"] == "refused"
    assert out["dirty"], out
    assert precious.is_file(), "the untracked post-backfill file was destroyed despite refusal"

    # ...and `--force` is a real override, not decoration.
    forced = _run(root, "restore", "--record", "rec.json", "--apply", "--force")
    assert forced.returncode == 0, forced.stdout + forced.stderr


def test_mixed_run_exit_is_legible(tmp_path):
    """SC10 / Issue 2.6 — a run that MUTATES N and HALTS on M is not readable as 'nothing happened'.

    The exit code cannot carry this: `1` is the same number whether the first bundle halted
    before touching anything or the tenth halted after nine were rewritten. Only the second is a
    state an operator must not walk away from, so the counts are reported separately and named.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    good = make_legacy(root, name="plan-901-fixture-aaaaaa")
    # A bundle that HALTS: its README objective diverges from plan.md's H1.
    bad = make_legacy(root, name="plan-902-fixture-bbbbbb",
                      objective="The real objective", readme_objective="A stale objective")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "s"],
                   cwd=root, check=True)

    proc, data, _ = _backfill_with_record(root)
    out = json.loads(proc.stdout)

    # NON-VACUITY: the fixture really is mixed.
    assert out["mutated"] >= 1 and out["halted"] >= 1, out
    assert out["mixed_run"] is True, out
    assert "PARTIAL" in out["mixed_run_note"]
    assert out["mutated_bundles"] and out["halted_bundles"]
    assert set(out["mutated_bundles"]).isdisjoint(out["halted_bundles"])
    assert proc.returncode == 1, "a halt must still be a non-zero exit"

    # THE RECORD SAYS WHICH. A halted bundle carries no operations to reverse.
    recorded = {e["bundle"] for e in data["bundles"]}
    assert recorded == set(out["mutated_bundles"]), (recorded, out["mutated_bundles"])
    assert bad.name not in recorded, "a HALTED bundle appears in the record as reversible"
    assert data["mixed_run"] is True


# =========================================================================================
# REQ-OKFH-011 / REQ-OKFH-012 / REQ-DATA-075 — an honest dry run, and objective reconciliation.
# =========================================================================================

def test_dry_run_predictive(tmp_path):
    """SC15 / REQ-OKFH-011 — every halt condition apply evaluates, the dry run evaluates.

    THE ARM IS BUILT ON THE HALT THAT MEASURABLY ESCAPED. `phase-log-loss` was computed AFTER
    staging, inside `if apply:`, so `plan-030` — the one target bundle of eight that cleared the
    dry run — then halted under `--apply` on exactly that guard. A dry run that under-reports
    halts is worse than one that reports none: an operator consents on evidence that does not
    cover the condition that stops it.
    """
    # A bundle whose phase log would be LOST: dated bullets in plan.md that the transform
    # cannot carry into log.md.
    b = make_legacy(tmp_path, phaselog="- 2026-08-01 scoping: started\n- 2026-08-02 drafting: x\n")
    (b / "plan.md").write_text(
        (b / "plan.md").read_text().replace("**Phase log:**", "**Not a phase log:**"))

    dry = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")

    # NON-VACUITY: the fixture really does trip a POST-STAGING guard, not a pre-staging one.
    assert dry["action"] == "halt", dry
    kinds = [h["kind"] for h in dry["halts"]]
    assert "phase-log-loss" in kinds, kinds

    # ...and apply agrees. THIS is the predictive property: same input, same verdict.
    b2 = make_legacy(tmp_path / "apply-side",
                     phaselog="- 2026-08-01 scoping: started\n- 2026-08-02 drafting: x\n")
    (b2 / "plan.md").write_text(
        (b2 / "plan.md").read_text().replace("**Phase log:**", "**Not a phase log:**"))
    applied = hyg.backfill_one(tmp_path / "apply-side", b2, apply=True, skill="yf-plan")
    assert applied["action"] == "halt", applied
    assert [h["kind"] for h in applied["halts"]] == kinds, (dry["halts"], applied["halts"])

    # THE DRY RUN LEFT NOTHING BEHIND — no staging, and crucially NO JOURNAL, which would make
    # the next backfill refuse (Issue 3.4).
    assert not hyg.stale_journals(tmp_path), "the dry run wrote a journal"
    assert not (b.parent / hyg.STAGING_DIR).exists(), "the dry run left staging residue"


def test_dry_run_leaves_no_residue_on_the_happy_path(tmp_path):
    """REQ-OKFH-011 — staging-without-swapping must be invisible afterwards."""
    b = make_legacy(tmp_path)
    before = sorted(p.name for p in b.iterdir())

    dry = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")
    assert dry["action"] == "would-backfill", dry

    assert sorted(p.name for p in b.iterdir()) == before, "the dry run MUTATED the bundle"
    assert not (b.parent / hyg.STAGING_DIR).exists(), "staging residue"
    assert not hyg.stale_journals(tmp_path), "journal residue"


def test_reconcile_objective(tmp_path):
    """SC16 / REQ-OKFH-012 — `plan.md`'s H1 is authoritative, OPT-IN, and reported per bundle."""
    def fixture(root):
        return make_legacy(root, objective="The current objective",
                           readme_objective="A stale objective")

    # DEFAULT: the halt is retained. A guard whose remedy is on by default is not a guard.
    b = fixture(tmp_path)
    halted = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")
    assert halted["action"] == "halt", halted
    assert [h["kind"] for h in halted["halts"]] == ["objective-divergence"], halted
    assert "reconcile-objective" in halted["halts"][0]["remediation"]

    # OPT-IN: the same bundle clears, and the rewrite is REPORTED.
    root2 = tmp_path / "opt-in"
    b2 = fixture(root2)
    ok = hyg.backfill_one(root2, b2, apply=True, skill="yf-plan", reconcile_objective=True)
    assert ok["action"] == "backfilled", ok
    assert ok["reconciled_objective"]["from"] == "A stale objective"
    assert ok["reconciled_objective"]["to"] == "The current objective"
    assert ok["reconciled_objective"]["authority"] == "plan.md H1"

    # THE AUTHORITY IS plan.md's H1, and it reached the generated index.
    idx = (b2 / "index.md").read_text()
    assert "> The current objective" in idx, idx[:400]
    assert "A stale objective" not in idx


def test_stamps_description(tmp_path):
    """SC16 / REQ-DATA-075 — the transform stamps `description:`, derived and never invented."""
    b = make_legacy(tmp_path)
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec

    fm, _ = okf_read(b / "plan.md")
    assert str(fm.get("description") or "").strip(), f"plan.md carries no description: {fm}"
    assert fm["description"] == "An objective", fm["description"]

    ffm, _ = okf_read(b / "findings" / "exp-001.md")
    assert str(ffm.get("description") or "").strip() == "A finding", ffm

    # EXEMPT, and the exemption is DECLARED (REQ-DATA-075): context.md would carry the same
    # string in every bundle, and a key constant across the corpus carries zero information.
    cfm, _ = okf_read(b / "context.md")
    assert not str(cfm.get("description") or "").strip(), cfm

    # RESERVED files carry no frontmatter at all (REQ-OKF-031) — never stamped.
    assert not (b / "index.md").read_text().startswith("---\ntype:")
    assert "description:" not in (b / "log.md").read_text().split("\n#")[0]


def test_description_is_never_invented(tmp_path):
    """REQ-DATA-075 / REQ-OKF-011 — a file with no derivable description is left UNSTAMPED.

    A manufactured string satisfies the letter of the requirement and defeats its purpose, so
    "no H1, no description" must be the behaviour rather than "no H1, invent one".
    """
    b = make_legacy(tmp_path, extra=(("findings/no-heading.md", "just prose, no H1 at all\n"),))
    hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")

    fm, _ = okf_read(b / "findings" / "no-heading.md")
    assert fm, "the transform stamped no frontmatter at all — arm would be vacuous"
    assert not str(fm.get("description") or "").strip(), \
        f"a description was INVENTED for a file with no H1: {fm}"


def test_migration_samples_are_untouched(tmp_path):
    """The frozen before/after migration-diff corpus is a FIXTURE: its exact bytes are the
    test. Discovery must not reach into it, so no repair can ever be proposed for it."""
    samples = REPO / "docs" / "plans" / "plan-029-james-dixson-75fd34" / "findings" \
        / "okf-migration-samples"
    if not samples.is_dir():
        pytest.skip("the migration-sample corpus is not present in this address space")
    found = hyg.discover([REPO / "docs" / "plans"], 6, hyg.DEFAULT_EXCLUDE_GLOBS)
    assert not any("okf-migration-samples" in str(p) for p in found), \
        "discovery reached into the frozen migration-sample fixtures"


# THE RUNNER BLOCK. Without it `uv run <this file>` imports the module, runs nothing, and
# exits 0 — which would make SC17 a criterion that cannot fail. See the module docstring.
if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

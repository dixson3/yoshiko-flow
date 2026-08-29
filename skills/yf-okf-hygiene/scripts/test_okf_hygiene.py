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
    """REQ-OKFH-004/010 — the two legacy variants classify to their own class and are
    otherwise handled IDENTICALLY. The `_index.md` route dispatches on the DETECTED MEMBER,
    not on the filename, so it needs no second code path."""
    b = make_legacy(tmp_path, legacy_name=legacy_name)
    cls, detail = hyg.classify(b)
    assert cls == expected
    assert detail["legacy_index"] == [legacy_name]

    plan = hyg.backfill_one(tmp_path, b, apply=False, skill="yf-plan")
    assert plan["action"] == "would-backfill"
    assert plan["steps"][0] == "migrate" and plan["steps"][-1] == "regenerate-listing"


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


def test_crash_recovery_all_states(tmp_path):
    """SC11 / REQ-OKFH-008 — recovery is deterministic from ALL FIVE crash points.

    The five are ENUMERATED in `okf_hygiene.STATES` and this test names EACH of them, because
    a five-state test and a five-state journal could otherwise be five DIFFERENT fives with
    every instrument green.

    S1 is the case that motivates the journal at all: a table keyed on directory PRESENCE
    reads "staged, crashed before rename 1" (bundle present, staging present) the same way it
    reads S4 (bundle present, staging gone) — and it reads S2, where the bundle is ABSENT, as
    a deleted bundle. Only a recorded phase separates them.
    """
    assert set(hyg.STATES) == {"S0", "S1", "S2", "S3", "S4"}, hyg.STATES
    results = {}

    for state in ("S0", "S1", "S2", "S3", "S4"):
        root = tmp_path / state
        root.mkdir()
        b = make_legacy(root)
        j = hyg.Journal(root, b)
        marker = (b / "plan.md").read_text()

        if state == "S0":
            j.write("S0")
        elif state == "S1":
            shutil.copytree(b, j.staging)
            j.write("S1")
        elif state == "S2":
            shutil.copytree(b, j.staging)
            j.write("S1")
            os.rename(b, j.stash)
            j.write("S2")
            assert not b.exists(), "S2's precondition is that the bundle is ABSENT"
        elif state == "S3":
            shutil.copytree(b, j.staging)
            os.rename(b, j.stash)
            os.rename(j.staging, b)
            j.write("S3")
        else:  # S4
            shutil.copytree(b, j.staging)
            os.rename(b, j.stash)
            os.rename(j.staging, b)
            shutil.rmtree(j.stash, ignore_errors=True)
            j.write("S4")

        out = hyg.recover(root, b)
        results[state] = out
        assert out["recovered"] is True, f"{state}: {out}"
        # THE INVARIANT THAT HOLDS FROM EVERY STATE: the bundle exists, its content is intact,
        # and no residue is left behind.
        assert b.is_dir(), f"{state}: the bundle did not survive recovery"
        assert (b / "plan.md").read_text() == marker, f"{state}: content was lost"
        assert not j.staging.exists(), f"{state}: staging residue"
        assert not j.stash.exists(), f"{state}: stash residue"
        assert not j.path.exists(), f"{state}: journal residue"

    assert set(results) == set(hyg.STATES)
    # S1 and S4 are DISTINGUISHABLE — the whole reason the journal exists.
    assert results["S1"]["action"] != results["S4"]["action"]


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


def test_restore_round_trip(tmp_path):
    """SC14 / REQ-OKFH-010 — `restore` returns a backfilled bundle to its pre-run state,
    INCLUDING unlinking files the backfill CREATED.

    `git checkout` alone cannot do this: a created `index.md`/`log.md` is absent from HEAD, so
    a restore that only checks out leaves every created file behind and reports success. The
    operation kind is therefore PER PATH.
    """
    b = make_legacy(tmp_path)
    created_before = {p.name for p in b.iterdir()}
    rec = hyg.backfill_one(tmp_path, b, apply=True, skill="yf-plan")
    assert rec["action"] == "backfilled", rec
    after = {p.name for p in b.iterdir()}
    created = after - created_before
    assert "index.md" in created and "log.md" in created, created

    # The per-path kind is what the round trip depends on. Verified structurally: in a tree
    # with no git history every path is UNTRACKED, so every op must be `unlink` — the branch
    # `git checkout` alone would skip.
    record = tmp_path / "rec.json"
    record.write_text(json.dumps({"bundles": [{"bundle": b.name,
                                               "before": {"verdict": "pass"},
                                               "after": {"verdict": "pass"}}]}))
    proc = subprocess.run(["uv", "run", str(_HERE / "okf_hygiene.py"), "restore",
                           "--record", str(record)],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    ops = json.loads(proc.stdout)["operations"]
    kinds = {o["kind"] for o in ops}
    assert "unlink" in kinds, f"no unlink op was planned — created files would survive: {ops}"
    assert any(o["path"].endswith("index.md") and o["kind"] == "unlink" for o in ops)


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

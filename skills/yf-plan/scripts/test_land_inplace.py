#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml",
# ]
# ///
"""`land` under `execute.worktree: false` — the in-place path (dixson3/yoshiko-flow#331).

plan-068 Epic 2. EXP-001 measured that **no test anywhere** exercised `_land_manifest`,
`_land_execute` or any L-step under `execute.worktree: false`, and the spec had **zero** hits
for in-place landing. So this file is the whole coverage for the property #331 is about, and it
is written to fail on each of the four defects Epic 2 fixes rather than only on the headline
one.

**The end-to-end test drives `land_rehearsal.py`'s `_build_sandbox`** — a throwaway repo with a
**local bare `origin`** — plus its `SandboxRunner`. That dependency is deliberate and is why
Issue 2.5 depends on Epic 1: EXP-002 measured that **unpatched**, the runner sees `['git']` only
and the run halts at `l14_pour_fidelity` at 18 rows. Without the seam this test cannot reach
`L_DONE` at all.

**The tty gate is passed an EXPLICIT allow-list** rather than relying on `#334`'s bypass
(pass-2 C9), so plan-069's fix to that bypass cannot break this test.

THE `__main__` IS THE FORWARDING FORM (REQ-CLI-028).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pm = _load("pm_inplace", "plan_manager.py")
reh = _load("reh_inplace", "land_rehearsal.py")


def _git(*a, cwd):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True)


# ============================================================================================
# Fixtures
# ============================================================================================

@pytest.fixture
def inplace(tmp_path, monkeypatch):
    """A sandbox repo configured `execute.worktree: false`, cwd'd into.

    `os.chdir` is real rather than mocked because `_worktree_ensure` resolves its root through
    `_git_root()`, which is cwd-keyed — that is the very shape Issue 1.1 gave the landing
    helpers a `root=` to escape, and it is unchanged for `_worktree_ensure`, whose contract is
    "the repo I am standing in".
    """
    work, origin = reh._build_sandbox(tmp_path)
    # The execute branch that `_build_sandbox` pre-creates would defeat the create arm, so
    # remove it: this fixture is for testing the CUT.
    _git("branch", "-D", f"{reh.PLAN_ID}-execute", cwd=work)
    cfg = work / ".yf" / "plan"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "config.local.json").write_text(json.dumps({"execute.worktree": False}))
    (work / ".beads").mkdir(exist_ok=True)
    monkeypatch.chdir(work)
    return work, origin


PLAN_REL = Path("docs/plans") / reh.PLAN_ID
BRANCH = f"{reh.PLAN_ID}-execute"


# ============================================================================================
# Issue 2.1 — the three-way in-place branch cut
# ============================================================================================

def test_in_place_CUTS_AND_CHECKS_OUT_the_execute_branch(inplace):
    """SC4 (first half). `viable: false, reason: opted-out` — AND the branch now exists.

    The verdict shape is unchanged on purpose: the caller must still run in-place. What
    changes is that `<plan-id>-execute` exists and is HEAD before it does.
    """
    work, _ = inplace
    assert _git("rev-parse", "--verify", "--quiet", BRANCH, cwd=work).returncode != 0, (
        "the fixture is meant to start WITHOUT the execute branch, or the create arm is not "
        "the arm under test")

    v = pm._worktree_ensure(PLAN_REL)
    assert v["viable"] is False, "in-place must not claim a viable worktree"
    assert v["reason"] == "opted-out"
    assert v["action"] == "created-in-place"
    assert v["branch"] == BRANCH
    assert _git("rev-parse", "--verify", "--quiet", BRANCH, cwd=work).returncode == 0, (
        "the branch was not created")
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=work).stdout.strip() == BRANCH, (
        "CREATE-WITHOUT-CHECKOUT IS SILENTLY WRONG — the whole point is that ctx.root's HEAD "
        "IS the execute branch, which is what makes L1's down-merge real rather than a "
        "self-merge")


def test_the_cut_is_PINNED_to_the_resolved_base_not_ambient_HEAD(inplace):
    """REQ-BRANCH-002 clause (i). The start-point is explicit.

    Load-bearing structurally, not stylistically: the `opted-out` short-circuit used to sit
    ABOVE `_resolve_execute_base`, so the in-place path never reached the base resolver at all.
    This asserts it does now — the branch must point at the resolved base, and the fixture puts
    HEAD somewhere else to make "ambient" and "pinned" distinguishable.
    """
    work, _ = inplace
    # Move HEAD off the base so ambient != pinned.
    _git("checkout", "-q", "-b", "somewhere-else", cwd=work)
    (work / "noise.txt").write_text("noise\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "noise", cwd=work)
    ambient = _git("rev-parse", "HEAD", cwd=work).stdout.strip()

    v = pm._worktree_ensure(PLAN_REL)
    assert v["reason"] == "opted-out" and v["action"] == "created-in-place", v
    assert v["base"] == "main", v
    tip = _git("rev-parse", BRANCH, cwd=work).stdout.strip()
    main = _git("rev-parse", "main", cwd=work).stdout.strip()
    assert tip == main, "the branch was not cut from the pinned base"
    assert tip != ambient, (
        "the branch was cut from AMBIENT HEAD — REQ-BRANCH-002's whole subject is the "
        "start-point, and this is the #47 root cause")


def test_the_three_way_branch_is_IDEMPOTENT_across_sessions(inplace):
    """REQ-BRANCH-002 clause (i). `_worktree_ensure` runs on EVERY execute invocation.

    Its own docstring promises "idempotent create-or-reattach", while `git checkout -b` on an
    existing branch exits **128** — so multi-session execution is the normal case and a
    two-way branch would break the second session of every in-place plan.

    All three arms are exercised, and each reports a DISTINCT `action`, because "it did not
    crash" is not the same claim as "it took the right arm".
    """
    work, _ = inplace

    first = pm._worktree_ensure(PLAN_REL)
    assert first["action"] == "created-in-place", first

    second = pm._worktree_ensure(PLAN_REL)
    assert second["action"] == "already-on-branch", (
        f"a second call must be a NO-OP while HEAD is already the execute branch; got {second}")

    _git("checkout", "-q", "main", cwd=work)
    third = pm._worktree_ensure(PLAN_REL)
    assert third["action"] == "reattached-branch-in-place", (
        f"an existing branch must be plain-checked-out, never `checkout -b` (exit 128); "
        f"got {third}")
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=work).stdout.strip() == BRANCH


def test_outside_a_git_repo_the_reason_stays_opted_out(tmp_path, monkeypatch):
    """`opted-out` is the OPERATOR'S DECISION and an environmental detail must not replace it.

    The caller runs in-place either way, so a reason that changes with the weather is a reason
    a caller cannot branch on. `branch_cut` carries the environmental fact instead.
    """
    (tmp_path / ".yf" / "plan").mkdir(parents=True)
    (tmp_path / ".yf" / "plan" / "config.local.json").write_text(
        json.dumps({"execute.worktree": False}))
    monkeypatch.chdir(tmp_path)
    v = pm._worktree_ensure(Path("docs/plans/plan-x"))
    assert v["viable"] is False and v["reason"] == "opted-out", v
    assert v["branch_cut"] == {"ok": False, "reason": "not-a-git-repo"}, v


# ============================================================================================
# Issue 2.2 — the dirty-tree refusal class (SC7)
# ============================================================================================

def test_a_dirty_tree_is_a_DECLARED_REFUSAL_not_a_raw_git_error(inplace):
    """SC7 / REQ-BRANCH-002 clause (ii).

    Measured: `git checkout -b` on a dirty divergent tree emits `error: Your local changes
    would be overwritten by checkout`, exits 1, and leaves HEAD unmoved — a class
    `_worktree_ensure` had no guard for, so it surfaced as a raw `git` error at the moment
    execution began.
    """
    work, _ = inplace
    # Dirty in a way a checkout would have to overwrite: modify a tracked file that DIFFERS
    # between HEAD and the branch that is about to be created... the create arm cuts from
    # `main`, so any uncommitted modification is enough to trip the guard.
    (work / "skills" / "base.txt").write_text("locally modified\n")
    head_before = _git("rev-parse", "HEAD", cwd=work).stdout.strip()

    v = pm._worktree_ensure(PLAN_REL)
    assert v["viable"] is False
    assert v["reason"] == "dirty-tree-in-place", (
        f"the refusal must carry its DECLARED class, not `opted-out` and not a raw git error; "
        f"got {v}")
    assert v["dirty"] is True and v["dirty_files"], v
    assert "dirty" in v["detail"].lower()

    # NOTHING WAS CHANGED. A refusal that half-acted would be worse than the raw error.
    assert _git("rev-parse", "HEAD", cwd=work).stdout.strip() == head_before
    assert _git("rev-parse", "--verify", "--quiet", BRANCH, cwd=work).returncode != 0, (
        "the branch was created despite the refusal")


def test_the_refusal_does_NOT_fire_when_already_on_the_branch(inplace):
    """The refusal is scoped to the two branch-MOVING arms, and the scope is the point.

    Being already on the execute branch is a no-op that cannot overwrite anything, so a dirty
    tree there is ordinary in-flight work. Refusing it would make every RESUMED in-place
    session unable to continue — a guard that blocks the normal case is worse than no guard.
    """
    work, _ = inplace
    assert pm._worktree_ensure(PLAN_REL)["action"] == "created-in-place"
    (work / "skills" / "base.txt").write_text("work in progress\n")

    v = pm._worktree_ensure(PLAN_REL)
    assert v["reason"] == "opted-out" and v["action"] == "already-on-branch", (
        f"a dirty tree while already on the execute branch is ordinary in-flight work; "
        f"got {v}")


# ============================================================================================
# Issue 2.1 / SC4 — the manifest shape in-place
# ============================================================================================

def test_the_manifest_STOPS_halting_execute_branch_missing(inplace):
    """SC4. The halt EXP-001 measured, gone — and gone for the right reason.

    `_land_manifest` halts on a bare `git rev-parse --verify <plan-id>-execute` and NEVER
    calls `_worktree_opted_out()`. So the fix is not a special case in the manifest: it is that
    the branch now exists. This asserts BOTH directions, because "no halt" alone would also be
    satisfied by a manifest that stopped checking.
    """
    work, _ = inplace

    before = pm._land_manifest(PLAN_REL)
    halts_before = [h.get("reason") or h.get("halt") or str(h) for h in (before.get("halts") or [])]
    assert any("execute-branch-missing" in h for h in halts_before), (
        f"the fixture does not reproduce #331's halt, so the after-state proves nothing; "
        f"halts were {halts_before}")

    pm._worktree_ensure(PLAN_REL)

    after = pm._land_manifest(PLAN_REL)
    assert not (after.get("halts") or []), f"still halting: {after.get('halts')}"
    assert after["facts"]["git"]["execute_branch"] == BRANCH
    # The in-place shape: no worktree, and the manifest says so rather than pretending.
    assert after["facts"]["git"]["execute_worktree_present"] is False, (
        "in-place there IS no worktree — a manifest claiming one would be false")


# ============================================================================================
# Issue 2.3 — L1 operates on the execute branch, NOT ambient HEAD (SC5)
# ============================================================================================

def test_l1_operates_on_the_execute_branch_not_ambient_head(inplace):
    """SC5, and WRITTEN TO FAIL UNDER 2.1 ALONE (pass-2 C12).

    That constraint is what makes this test worth having. Once the in-place cut lands,
    `ctx.root`'s HEAD *is* the execute branch and EXP-001's measured self-merge disappears
    without Issue 2.3's explicit checkout — so a test that merely ran L1 in-place would pass
    against 2.1 alone and assert nothing about 2.3.

    So this test MOVES HEAD OFF THE EXECUTE BRANCH immediately before calling L1. Under 2.1
    alone that reproduces the original defect exactly: L1 merges the target into whatever HEAD
    is, reports `Already up to date.` / exit 0 / verdict `pass`, and journals `L_DOWNMERGED`.
    """
    work, _ = inplace
    pm._worktree_ensure(PLAN_REL)
    # Put a real commit on the execute branch so a genuine down-merge is distinguishable from
    # a self-merge.
    (work / "skills" / "landed.py").write_text("print('landed')\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "the work", cwd=work)
    # And a commit on the target, so the down-merge has something to bring in.
    _git("checkout", "-q", "main", cwd=work)
    (work / "on_main.txt").write_text("main moved\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "main moves", cwd=work)

    # HEAD IS NOW `main`, NOT THE EXECUTE BRANCH. This is the arrangement that makes the test
    # fail under 2.1 alone.
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=work).stdout.strip() == "main"

    manifest = pm._land_manifest(PLAN_REL)
    ctx = pm.LandingContext(PLAN_REL, {"steps": {}}, manifest, root=work,
                            runner=reh.SandboxRunner(work, reh.PLAN_ID))
    out = pm._land_l1_down_merge(ctx)

    assert out["verdict"] == "pass", out
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=work).stdout.strip() == BRANCH, (
        "L1 did not check out the execute branch — it operated on ambient HEAD, which is "
        "EXP-001's silent self-merge: `Already up to date.`, exit 0, verdict pass")
    # The down-merge is REAL: the target's commit is now an ancestor of the execute branch.
    anc = _git("merge-base", "--is-ancestor", "main", BRANCH, cwd=work)
    assert anc.returncode == 0, (
        "the target is not an ancestor of the execute branch, so no down-merge happened — "
        "L1 reported `pass` on a merge that did nothing")


def test_l1_HALTS_when_the_execute_branch_cannot_be_checked_out(inplace):
    """A failed checkout is a halt, not a warning.

    If the branch cannot be checked out there is no state in which the rest of L1 means
    anything: the merge would run against the wrong tree and report `pass`.
    """
    work, _ = inplace
    pm._worktree_ensure(PLAN_REL)
    manifest = pm._land_manifest(PLAN_REL)
    _git("checkout", "-q", "main", cwd=work)
    _git("branch", "-D", BRANCH, cwd=work)          # the branch is gone

    ctx = pm.LandingContext(PLAN_REL, {"steps": {}}, manifest, root=work,
                            runner=reh.SandboxRunner(work, reh.PLAN_ID))
    out = pm._land_l1_down_merge(ctx)
    assert out["verdict"] == "fail" and out["halting"] is True, out
    assert "check out" in out["reason"]


# ============================================================================================
# Issue 2.4 — merge-preview directionality, and the changed set (SC6)
# ============================================================================================

def test_merge_preview_is_directional(inplace):
    """SC6 / REQ-LAND-038. A branch BEHIND its target introduces NOTHING.

    Measured (EXP-001) with the two-argument `git diff <target> <execute_branch>` form: a merge
    guaranteed to be a no-op reported `changed_paths: ["work.txt"]` and `available: true`,
    naming the TARGET's changes and attributing them to the branch.
    """
    work, _ = inplace
    pm._worktree_ensure(PLAN_REL)
    _git("checkout", "-q", "main", cwd=work)
    (work / "work.txt").write_text("only on main\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "main moves ahead", cwd=work)

    # The branch is strictly BEHIND main and introduces nothing.
    behind = pm._land_merge_preview("main", BRANCH, root=work)
    assert behind["available"] is True
    assert behind["changed_paths"] == [], (
        f"a behind-branch merge introduces NOTHING, but the preview named "
        f"{behind['changed_paths']} — that is the target's changes attributed to the branch")
    assert behind["touches_skills"] is False

    # THE CONTRAST ARM. Without it, an always-empty `changed_paths` would pass above.
    _git("checkout", "-q", BRANCH, cwd=work)
    (work / "skills" / "new.py").write_text("x\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "real work on the branch", cwd=work)
    ahead = pm._land_merge_preview("main", BRANCH, root=work)
    assert "skills/new.py" in ahead["changed_paths"], ahead
    assert "work.txt" not in ahead["changed_paths"], (
        "the target's own change leaked into the branch's introduced set — still symmetric")
    assert ahead["touches_skills"] is True


def test_touches_skills_is_L19s_redeploy_precondition_and_follows_the_direction(inplace):
    """REQ-LAND-038's named consequence, asserted rather than left as an inference.

    A behind-branch preview naming a `skills/` path the branch never touched would ARM a
    redeploy the landing has no reason to perform.
    """
    work, _ = inplace
    pm._worktree_ensure(PLAN_REL)
    _git("checkout", "-q", "main", cwd=work)
    (work / "skills" / "only_on_main.py").write_text("x\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "skills change on MAIN only", cwd=work)

    p = pm._land_merge_preview("main", BRANCH, root=work)
    assert p["touches_skills"] is False, (
        "a `skills/` change that exists ONLY ON THE TARGET must not arm L19's redeploy — the "
        "branch introduces no skills change at all")


def test_changed_set_reads_the_merge_range_in_place(inplace):
    """SC6 (second half) / Issue 2.4. `HEAD^1..HEAD` after a REAL in-place merge.

    EXP-001 measured `_land_changed_set` degrading in-place because with no execute branch
    there was no merge and `HEAD` was not a merge commit, so the single-commit fallback fired
    and the landed set was one commit rather than the whole landing.

    The repair is NOT in that function: the in-place branch cut makes L2's `--no-ff` merge real,
    so `HEAD` becomes a genuine merge commit. That reasoning is asserted here rather than
    inferred.
    """
    work, _ = inplace
    pm._worktree_ensure(PLAN_REL)
    for name in ("skills/a.py", "docs/b.md"):
        f = work / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "work one", cwd=work)
    (work / "skills" / "c.py").write_text("y\n")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "work two", cwd=work)

    _git("checkout", "-q", "main", cwd=work)
    m = _git("merge", "--no-ff", "-m", "land it", BRANCH, cwd=work)
    assert m.returncode == 0, m.stderr

    # HEAD is a REAL merge commit — the property the in-place cut buys.
    parents = _git("rev-list", "--parents", "-n", "1", "HEAD", cwd=work).stdout.split()[1:]
    assert len(parents) == 2, (
        f"HEAD has {len(parents)} parent(s) — without a real merge the single-commit fallback "
        f"fires and the landed set is one commit rather than the landing")

    changed = pm._land_changed_set(work)
    assert set(changed) == {"skills/a.py", "docs/b.md", "skills/c.py"}, changed


# ============================================================================================
# Issue 2.5 — THE END-TO-END IN-PLACE LANDING (SC4)
# ============================================================================================

def test_end_to_end_in_place_landing_reaches_L_DONE(tmp_path):
    """SC4. `worktree ensure` -> commit -> `land --dry-run` -> `--apply` -> `L_DONE`.

    THE PROPERTY #331 IS ACTUALLY ABOUT. pass-1 flagged that nothing asserted the full path,
    and EXP-001 measured no test anywhere exercising `_land_manifest`, `_land_execute` or any
    L-step under `execute.worktree: false`.

    THE RUNNER'S CONTRACT IS LOAD-BEARING (pass-3 C5). `_dispatch` routes EVERY program
    through an injected runner, `git` included, so a runner that stubbed everything would make
    `L_DONE` a fiction. `SandboxRunner` passes `git` THROUGH to the sandbox — it is the local
    bare `origin` that makes the push safe, not the runner — and intercepts `bd`/`gh`/`uv`/`yf`
    with argv-recognising fakes that FAIL AT 127 on an unrecognised argv rather than returning
    0. That refusal set is asserted below.

    THE TTY ALLOW-LIST IS EXPLICIT (pass-2 C9), not `#334`'s bypass, so plan-069's fix to that
    bypass cannot break this test. It is passed as a decision-level enable of the executor,
    which never consults the tty gate — the gate lives in the CLI preamble, and this test
    drives `_land_execute` directly for exactly that reason.
    """
    work, origin = reh._build_sandbox(tmp_path)
    cfg = work / ".yf" / "plan"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "config.local.json").write_text(json.dumps({"execute.worktree": False}))
    (work / ".beads").mkdir(exist_ok=True)
    # `_build_sandbox` pre-creates the execute branch; drop it so `ensure` performs the CUT,
    # which is the step under test.
    _git("branch", "-D", BRANCH, cwd=work)

    cwd0 = os.getcwd()
    os.chdir(work)
    try:
        # 1. `worktree ensure` -> branch cut AND checked out, in-place.
        v = pm._worktree_ensure(PLAN_REL)
        assert v["reason"] == "opted-out" and v["action"] == "created-in-place", v
        assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=work).stdout.strip() == BRANCH

        # 2. Work committed on the execute branch.
        (work / "skills" / "landed.py").write_text("print('landed')\n")
        _git("add", "-A", cwd=work)
        _git("commit", "-q", "-m", "the work", cwd=work)

        # 3. `land --dry-run` -> a manifest with NO halts.
        manifest = pm._land_manifest(PLAN_REL)
        assert not (manifest.get("halts") or []), (
            f"the dry run still halts in-place: {manifest.get('halts')}")
        # NESTED UNDER `facts["git"]`, not top-level. Read from the manifest rather than
        # assumed: a `.get("merge_preview")` at the wrong level returns `{}` and every
        # assertion against it would then be vacuously satisfiable by `or []`.
        preview = manifest["facts"]["git"]["merge_preview"]
        assert "skills/landed.py" in (preview.get("changed_paths") or []), preview
        assert preview.get("touches_skills") is True, (
            "the branch introduces a skills/ path, so L19's redeploy precondition must be armed")

        # 4. `--apply` -> the executor, over the real step functions.
        runner = reh.SandboxRunner(work, reh.PLAN_ID)
        decision = {
            "schema": pm.LAND_SCHEMA_DECISION,
            "manifest_digest": pm._land_digest(manifest["facts"]),
            "plan_id": reh.PLAN_ID,
            "authored_by": "test_land_inplace",
            "summary": "in-place end-to-end",
            "upstream_writes": [],
            "steps": {**{k: "enable" for k in pm.LAND_STEPS},
                      "l19_redeploy": "skip:the sandbox has no `yf` binary, and redeploy is "
                                      "the only step that mutates the machine outside the "
                                      "repository"},
        }
        ctx = pm.LandingContext(PLAN_REL, decision, manifest, root=work, runner=runner)
        result = pm._land_execute(ctx)
    finally:
        os.chdir(cwd0)

    # 5. `L_DONE`.
    assert result.get("halted") is False, (
        f"halted at {result.get('at')} — verdicts: "
        f"{[(r['step'], r['verdict']) for r in result.get('results', [])]}")
    assert result.get("journal_phase") == "L_DONE", result.get("journal_phase")
    assert result.get("reached_terminal_state") is True

    # The runner was never asked for an argv it does not model. A green run whose runner was
    # asked something it invented an answer for proves nothing.
    assert runner.unrecognised == [], (
        f"a step invoked something the sandbox never modelled: {runner.unrecognised}")
    # `git` really ran: refs moved on the fake origin.
    landed = _git("ls-tree", "--name-only", "-r", "main", cwd=origin).stdout.split()
    assert any("landed" in p for p in landed), (
        f"nothing reached the fake origin, so the pushes were not real; origin has {landed}")
    # And the origin is a throwaway, never this repository.
    url = _git("remote", "get-url", "origin", cwd=work).stdout.strip()
    assert url.endswith("fake-origin.git") and "yoshiko-flow" not in url, url


def test_the_end_to_end_test_would_not_pass_without_the_seam():
    """EXP-002, pinned: unpatched, the runner sees `['git']` only.

    Recorded as an executable dependency rather than a comment, because Issue 2.5's dependency
    on Epic 1 is the kind of edge that quietly stops being true. If every L-step's launches
    were off the seam again, the run would halt at `l14_pour_fidelity` and never reach `L_DONE`
    — so this asserts the seam is still there to be depended on.
    """
    r = subprocess.run(
        [sys.executable, str(HERE.parent.parent.parent / "scripts" / "checks"
                             / "check_land_seam.py"), "--json"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, (
        f"the seam check is red, so the end-to-end test's premise is gone:\n{r.stdout}")
    payload = json.loads(r.stdout)
    assert payload["verdict"] == "PASS"
    assert not payload["direct_violations"]


# ============================================================================================
# Issue 2.6 — the SPEC text and the implemented L1/L2 behaviour AGREE (SC9c)
# ============================================================================================

LANDING_SPEC = HERE.parent / "spec" / "landing.md"
PM_SOURCE = HERE / "plan_manager.py"


def test_the_landed_spec_matches_the_implemented_L1_behaviour():
    """SC9c, L1 half. `REQ-LAND-002` as amended says L1 checks out the execute branch.

    Read off BOTH sides rather than asserted about one: the SPEC must carry the clause, and
    the implementation must exhibit it. Either alone is satisfiable while the pair diverges,
    which is the whole subject of this issue.
    """
    spec = LANDING_SPEC.read_text()
    assert "AMBIENT HEAD IS NOT A FACT" in spec, (
        "REQ-LAND-002's in-place amendment is gone from the SPEC")
    flat = " ".join(spec.split())
    assert "L1 shall check out `ctx.execute_branch` explicitly" in flat, (
        "the SPEC no longer states L1's explicit-checkout obligation")
    src = PM_SOURCE.read_text()
    body = src[src.index("def _land_l1_down_merge"):src.index("def _land_l2_merge")]
    assert 'ctx.run("git", ["checkout", ctx.execute_branch]' in body, (
        "L1 does not check out the execute branch — the SPEC says it shall, so SPEC and "
        "implementation have DIVERGED")
    # And the checkout is a HALT on failure, not a warning.
    assert 'if co.returncode != 0:' in body and 'halting=True' in body, (
        "L1's checkout failure is not halting; a non-halting checkout failure means the merge "
        "runs against the wrong tree and reports `pass`")


def test_the_landed_spec_matches_the_implemented_L2_behaviour():
    """SC9c, L2 half — and this is the half that could have been trivially green.

    `REQ-LAND-004`'s amendment does NOT specify what L2 should do in-place. It records what L2
    DOES, and declares the work a scope boundary routed to plan-069. So agreement here means
    the two recorded facts are still true of the code:

      1. `git checkout <target>` runs in `ctx.root`;
      2. the following `git pull --rebase`'s return code is IGNORED.

    A test that only read the SPEC would pass forever. A test that only read the code would
    pass forever. This reads both and FAILS when either moves without the other — including
    the good direction: closing the ignored return code without moving the boundary is drift,
    and drift is what this check is for.
    """
    spec = LANDING_SPEC.read_text()
    flat = " ".join(spec.split())
    assert "L2 IN-PLACE IS A DECLARED SCOPE BOUNDARY" in flat, (
        "REQ-LAND-004's declared boundary is gone from the SPEC")
    assert "runs `git checkout <target>` **in `ctx.root`**" in flat, (
        "the SPEC no longer records fact 1 (the checkout runs in ctx.root)")
    assert "return code is **ignored**" in flat, (
        "the SPEC no longer records fact 2 (the pull --rebase return code is ignored)")
    assert "routed to **plan-069**" in flat or "plan-069" in flat, (
        "the SPEC declares a boundary but names no destination for the work")

    src = PM_SOURCE.read_text()
    body = src[src.index("def _land_l2_merge"):src.index("def _land_l3_validate_merged")]

    # Fact 1 — still true.
    assert 'ctx.run("git", ["checkout", ctx.target], cwd=ctx.root)' in body, (
        "L2 no longer checks out the target in ctx.root. If that is a FIX, move "
        "REQ-LAND-004's declared boundary in the same change-set — the SPEC currently records "
        "this as the measured status quo.")

    # Fact 2 — still true. Asserted by the ABSENCE of a binding, which is the only way to
    # state "the return code is ignored" mechanically.
    pull_line = next(
        (ln for ln in body.splitlines() if 'pull", "--rebase"' in ln), None)
    assert pull_line is not None, "L2 no longer pulls --rebase"
    assert "=" not in pull_line.split("ctx.run")[0], (
        f"L2's `git pull --rebase` return code is now BOUND, so it may be checked — that is "
        f"the plan-069 work, and REQ-LAND-004's declared boundary must move with it. Line: "
        f"{pull_line.strip()}")

    # The code names the boundary, so a reader of the code finds the SPEC rather than
    # discovering the ignored return code and assuming it is a bug nobody noticed.
    assert "DECLARED SCOPE BOUNDARY" in body and "REQ-LAND-004" in body, (
        "L2's docstring does not name the declared boundary; the SPEC records it, but a reader "
        "of the code would meet the two facts with no pointer to why they are as they are")


def test_no_plan_068_issue_implements_L2_in_place_which_is_why_the_boundary_is_DECLARED():
    """The honesty check on Issue 0.4's own reasoning (pass-3 C7), made executable.

    0.4's argument for recording rather than specifying was: *"No issue in Plan A implements or
    tests L2 in-place, so specifying it here would leave SC9c/2.6 trivially green."* That
    argument is only sound while it is TRUE — so it is asserted rather than trusted.

    If a later change does implement L2 in-place, this test fails and the SPEC boundary must
    move. That is the intended outcome, not a nuisance.
    """
    # THE EXECUTABLE BODY, WITH THE DOCSTRING STRIPPED. Checked via the AST rather than by
    # slicing text, because L2's docstring legitimately says "in-place" several times — it is
    # where the boundary is recorded. A substring check over the whole function would fire on
    # the very note that declares the boundary, which is the opposite of what this asserts.
    tree = ast.parse(PM_SOURCE.read_text())
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_land_l2_merge")
    stmts = fn.body[1:] if (fn.body and isinstance(fn.body[0], ast.Expr)
                            and isinstance(fn.body[0].value, ast.Constant)) else fn.body
    code = "\n".join(ast.unparse(st) for st in stmts)

    assert "_worktree_opted_out" not in code, (
        "L2 now branches on in-place mode. REQ-LAND-004 records L2's in-place behaviour as a "
        "DECLARED BOUNDARY routed to plan-069, and that declaration is now false — move it.")
    assert "worktree" not in code, (
        "L2's executable body now reasons about the worktree. If it has learned about in-place "
        "mode, REQ-LAND-004's declared boundary must move in the same change-set — a boundary "
        "the code has already crossed is not a boundary.")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

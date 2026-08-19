# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Unit tests for the plan_manager.py worktree verb cluster (plan-009 Issue 1.4).

Run from anywhere:  uv run skills/yf-plan/scripts/test_worktree.py

Covers (per Issue 1.4): create, re-attach idempotency, teardown refuse-on-dirty,
non-git fallback, branch-name == plan id, bd-db-unresolved teardown-and-fallback,
and the gitignore-append idempotency (Issue 1.2).

The `bd` shared-DB probe (`_bd_resolves_from`, INV-2) is monkeypatched: these tests
exercise the worktree *mechanics* in a throwaway git repo, not a live beads DB. The
real bd resolution is covered by the capability gate + the runtime fallback path
(reason=bd-db-unresolved) which IS tested here with the probe forced to False.

NOTE: the landing-lock contention test named in Issue 1.4 lives with the landing
lock itself (Issue 3.4) — the lock does not exist at 1.4 time.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

# Import the script-under-test as a module (it is a PEP 723 script, not a package).
_PM_PATH = Path(__file__).resolve().parent / "plan_manager.py"
_spec = importlib.util.spec_from_file_location("plan_manager", _PM_PATH)
assert _spec and _spec.loader
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


@pytest.fixture
def git_repo(tmp_path, monkeypatch):
    """A throwaway git repo with one commit and a `.beads/` marker, cwd-set."""
    _git(["init"], tmp_path)
    _git(["config", "user.email", "t@t"], tmp_path)
    _git(["config", "user.name", "t"], tmp_path)
    _git(["config", "commit.gpgsign", "false"], tmp_path)
    (tmp_path / "README.md").write_text("seed\n")
    _git(["add", "."], tmp_path)
    _git(["commit", "-m", "seed"], tmp_path)
    (tmp_path / ".beads").mkdir()  # primary owns the shared Dolt DB (INV-2 precond)
    monkeypatch.chdir(tmp_path)
    # bd resolution is fragile/environment-specific; stub it True for mechanics tests.
    monkeypatch.setattr(pm, "_bd_resolves_from", lambda _wt: True)
    return tmp_path


PLAN_DIR = Path("docs/plans/plan-009-james-dixson-996e44")
PLAN_ID = "plan-009-james-dixson-996e44"
EXEC_BRANCH = f"{PLAN_ID}-execute"       # named per-phase branch (REQ-BRANCH-001)


# ---------------------------------------------------------------------------
# Pure-computation verbs
# ---------------------------------------------------------------------------

def test_plan_id_and_path_default_root():
    assert pm._plan_id_from_dir(PLAN_DIR) == PLAN_ID
    assert pm._worktree_path(PLAN_DIR) == Path(".worktrees") / PLAN_ID


def test_plan_id_and_path_incubator_root():
    pd = Path("Incubator/flow/plans/plan-012-x-abc")
    assert pm._plan_id_from_dir(pd) == "plan-012-x-abc"
    assert pm._worktree_path(pd) == Path(".worktrees/plan-012-x-abc")


# ---------------------------------------------------------------------------
# gitignore management (Issue 1.2)
# ---------------------------------------------------------------------------

def test_gitignore_append_idempotent(git_repo):
    assert pm._ensure_worktrees_gitignored(git_repo) is True
    # Second call is a no-op (returns False) and does not duplicate the anchor.
    assert pm._ensure_worktrees_gitignored(git_repo) is False
    body = (git_repo / ".gitignore").read_text()
    assert body.count(pm.WORKTREES_GITIGNORE_ANCHOR) == 1


# ---------------------------------------------------------------------------
# Viability fallbacks
# ---------------------------------------------------------------------------

def test_non_git_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # tmp_path is not a git repo
    result = pm._worktree_ensure(PLAN_DIR)
    assert result["viable"] is False
    assert result["reason"] == "not-a-git-repo"


def test_beads_not_initialized_fallback(git_repo):
    (git_repo / ".beads").rmdir()
    result = pm._worktree_ensure(PLAN_DIR)
    assert result["viable"] is False
    assert result["reason"] == "beads-not-initialized"


def test_bd_unresolved_tears_down_and_falls_back(git_repo, monkeypatch):
    monkeypatch.setattr(pm, "_bd_resolves_from", lambda _wt: False)
    result = pm._worktree_ensure(PLAN_DIR)
    assert result["viable"] is False
    assert result["reason"] == "bd-db-unresolved"
    assert result["torn_down"] is True
    # The freshly-created worktree + branch were cleaned up — no orphan left behind.
    assert not (git_repo / ".worktrees" / PLAN_ID).exists()
    assert not pm._branch_exists(EXEC_BRANCH, git_repo)


# ---------------------------------------------------------------------------
# Create / reattach / teardown mechanics
# ---------------------------------------------------------------------------

def test_create_then_reattach_idempotency(git_repo):
    first = pm._worktree_ensure(PLAN_DIR)
    assert first["viable"] is True
    assert first["action"] == "created"
    assert first["branch"] == EXEC_BRANCH        # named execute branch (REQ-BRANCH-001)
    assert first["gitignore_updated"] is True
    assert (git_repo / ".worktrees" / PLAN_ID).is_dir()

    second = pm._worktree_ensure(PLAN_DIR)
    assert second["viable"] is True
    assert second["action"] == "reattached-worktree"   # never a second worktree
    assert second["gitignore_updated"] is False


def test_reattach_existing_branch_without_worktree(git_repo):
    # Execute branch exists but no worktree registered -> add WITHOUT -b (re-attach).
    pm._run_git(["branch", EXEC_BRANCH], cwd=git_repo)
    result = pm._worktree_ensure(PLAN_DIR)
    assert result["viable"] is True
    assert result["action"] == "reattached-branch"


def test_teardown_clean(git_repo):
    pm._worktree_ensure(PLAN_DIR)
    result = pm._worktree_teardown(PLAN_DIR, force=False)
    assert result["status"] == "ok"
    assert result["steps"]["branch_delete"]["ok"] is True
    assert not (git_repo / ".worktrees" / PLAN_ID).exists()
    assert not pm._branch_exists(EXEC_BRANCH, git_repo)


def test_teardown_refuse_on_dirty(git_repo):
    pm._worktree_ensure(PLAN_DIR)
    # An untracked file makes `git worktree remove` refuse without --force.
    (git_repo / ".worktrees" / PLAN_ID / "scratch.txt").write_text("wip\n")
    blocked = pm._worktree_teardown(PLAN_DIR, force=False)
    assert blocked["status"] == "blocked"
    assert blocked["steps"]["remove"]["ok"] is False
    # The branch is NOT deleted while the worktree still holds (possibly unmerged) work.
    assert pm._branch_exists(EXEC_BRANCH, git_repo)
    # --force escalates and clears it.
    forced = pm._worktree_teardown(PLAN_DIR, force=True)
    assert forced["status"] == "ok"
    assert not (git_repo / ".worktrees" / PLAN_ID).exists()


# ---------------------------------------------------------------------------
# Landing lock (Issue 3.4 — the contention test named in 1.4)
# ---------------------------------------------------------------------------

@pytest.fixture
def lock_cwd(tmp_path, monkeypatch):
    """A clean cwd so .yf/yf-plan/landing.lock is created under tmp_path."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_landing_lock_acquire_free(lock_cwd):
    r = pm._landing_lock_acquire("plan-x")
    assert r["acquired"] is True
    assert r["lock"]["plan_id"] == "plan-x"
    assert pm.LANDING_LOCK.exists()


def test_landing_lock_contention_live_same_host(lock_cwd, monkeypatch):
    assert pm._landing_lock_acquire("plan-x")["acquired"] is True
    # A second acquirer sees a live same-host holder -> blocked, not reclaimable.
    monkeypatch.setattr(pm, "_pid_alive", lambda _pid: True)
    r = pm._landing_lock_acquire("plan-y")
    assert r["acquired"] is False
    assert r["reclaimable"] is False


def test_landing_lock_reclaims_dead_same_host(lock_cwd, monkeypatch):
    assert pm._landing_lock_acquire("plan-x")["acquired"] is True
    # Holder PID is dead and same host -> stale, reclaimed on the next acquire.
    monkeypatch.setattr(pm, "_pid_alive", lambda _pid: False)
    r = pm._landing_lock_acquire("plan-y")
    assert r["acquired"] is True
    assert r["lock"]["plan_id"] == "plan-y"


def test_landing_lock_other_host_never_reclaimed(lock_cwd, monkeypatch):
    pm._landing_lock_acquire("plan-x")
    # Rewrite the lock as if held by another host with a (locally) dead PID.
    pm.LANDING_LOCK.write_text(json.dumps(
        {"hostname": "other-host", "pid": 999999, "plan_id": "plan-z"}))
    monkeypatch.setattr(pm, "_pid_alive", lambda _pid: False)
    r = pm._landing_lock_acquire("plan-y")
    assert r["acquired"] is False
    assert r["reclaimable"] is False   # cross-host locks are never auto-broken


def test_landing_lock_release_ownership(lock_cwd):
    pm._landing_lock_acquire("plan-x")
    # A different plan cannot release without --force.
    refused = pm._landing_lock_release("plan-other", force=False)
    assert refused["released"] is False
    assert pm.LANDING_LOCK.exists()
    # The owner releases cleanly.
    ok = pm._landing_lock_release("plan-x", force=False)
    assert ok["released"] is True
    assert not pm.LANDING_LOCK.exists()


# ---------------------------------------------------------------------------
# validate-merged (Issue 3.2 — layer-b + honesty notice)
# ---------------------------------------------------------------------------

def test_validate_merged_unset_emits_notice(lock_cwd):
    # No .yf-plan.local.json -> no validate-cmd -> pass with the cross-plan notice.
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["status"] == "pass"
    assert r["validate_cmd_configured"] is False
    assert "CROSS-PLAN REGRESSIONS NOT CHECKED" in r["notice"]


def test_validate_merged_runs_configured_cmd(lock_cwd):
    (lock_cwd / ".yf-plan.local.json").write_text(json.dumps({"validate-cmd": "true"}))
    passing = pm._validate_merged(Path("docs/plans/plan-x"))
    assert passing["status"] == "pass"
    assert passing["validate_cmd_configured"] is True
    assert passing["notice"] is None
    (lock_cwd / ".yf-plan.local.json").write_text(json.dumps({"validate-cmd": "false"}))
    failing = pm._validate_merged(Path("docs/plans/plan-x"))
    assert failing["status"] == "fail"


def test_worktree_opt_out_config(lock_cwd):
    (lock_cwd / ".yf-plan.local.json").write_text(json.dumps({"execute.worktree": False}))
    assert pm._worktree_opted_out() is True
    r = pm._worktree_ensure(Path("docs/plans/plan-x"))
    assert r["viable"] is False
    assert r["reason"] == "opted-out"


# ---------------------------------------------------------------------------
# validate-merged 3-tier delegation (plan-015 D.1 / D.3)
#
# Tier 1 (yf-change-validation engine) → Tier 2 (validate-cmd) → Tier 3 (notice).
# The `engine` discriminator ("change-validation"|"validate-cmd"|"none") plus the
# preserved schema keys are asserted across all tiers; the exit-3-on-non-pass
# contract is exercised through the Click `validate-merged` command.
# ---------------------------------------------------------------------------

# The real engine script, resolvable on disk; tier-1 tests point the runtime
# soft-dep resolver here so delegation runs the actual engine over the fixture repo.
_ENGINE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "yf-change-validation" / "scripts" / "change_validation.py"
)

# Schema keys preserved across every tier (the additive `engine` is checked separately).
_VALIDATE_MERGED_KEYS = {
    "plan_dir", "validate_cmd_configured", "layer_b", "notice", "status",
}


def _write_manifest(repo: Path, *, approved: bool, full_cmd: str) -> None:
    """Write a minimal CHANGE-VALIDATION.md with a single trivial FULL-tier row.

    `full_cmd` is a shell command (`true` → pass, `false` → fail) so the engine's
    `run --tier full` resolves deterministically with no real toolchain.
    """
    status = "yes" if approved else "no"
    (repo / pm.CHANGE_VALIDATION_MANIFEST).write_text(
        "# CHANGE-VALIDATION.md\n\n"
        "## 0. Status\n\n"
        f"approved: {status}\n\n"
        "## 1. Tiers\n\n"
        "### fast\n\n"
        "| id | cmd | cwd | timeout |\n"
        "|:--|:--|:--|--:|\n"
        "| | | | |\n\n"
        "### full\n\n"
        "| id | cmd | cwd | timeout |\n"
        "|:--|:--|:--|--:|\n"
        f"|  | `{full_cmd}` |  |  |\n\n"
        "## 2. Signal Fingerprint\n\n"
        "| source-path | parsed-value-or-hash |\n"
        "|:--|:--|\n"
        "| | |\n\n"
        "## 3. Trigger Scope\n\n"
        "| changed-path glob | scopes to (FAST ids) |\n"
        "|:--|:--|\n"
        "| | |\n"
    )


@pytest.fixture
def cv_repo(git_repo, monkeypatch):
    """A git repo (from `git_repo`) wired so the change-validation soft-dep resolves.

    `_repo_root()` (git from cwd) already returns the fixture repo, so the engine
    runs there and finds the repo-root manifest. We only redirect the script
    resolver to the real engine on disk (the fixture has no skills/ tree).
    """
    monkeypatch.setattr(pm, "_change_validation_script", lambda _root: _ENGINE_SCRIPT)
    return git_repo


# --- Resolver discovery (#74 regression) ------------------------------------
#
# The tier-1 tests above monkeypatch `_change_validation_script`, so they never
# exercise real path discovery — which is exactly how #74 slipped through: the
# resolver checked only `<repo>/skills/...` and returned None for every normal
# (user- or `.claude`/`.agents`-scope) install, silently yielding `engine: none`.
# These tests drive the un-patched resolver against on-disk install surfaces.

def _plant_engine(root: Path) -> Path:
    """Create a stub engine script at a skill-surface root; return its path."""
    p = root / "yf-change-validation" / "scripts" / "change_validation.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# stub engine\n")
    return p


def test_change_validation_resolver_finds_user_scope(tmp_path, monkeypatch):
    # A `~/.claude/skills` (user-scope) install must resolve — the #74 case.
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    (home / ".claude" / "skills").mkdir(parents=True)
    repo.mkdir()
    monkeypatch.setenv("HOME", str(home))
    planted = _plant_engine(home / ".claude" / "skills")
    assert pm._change_validation_script(repo) == planted


def test_change_validation_resolver_finds_project_agents_scope(tmp_path, monkeypatch):
    # A `<git-root>/.agents/skills` (project-scope) install must resolve too.
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    (home).mkdir()
    (repo / ".agents" / "skills").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    planted = _plant_engine(repo / ".agents" / "skills")
    assert pm._change_validation_script(repo) == planted


def test_change_validation_resolver_prefers_in_tree_source(tmp_path, monkeypatch):
    # yoshiko-flow's own in-tree source (`<repo>/skills/...`) wins over an install
    # surface so the repo dogfoods the engine it is developing.
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    (home / ".claude" / "skills").mkdir(parents=True)
    repo.mkdir()
    monkeypatch.setenv("HOME", str(home))
    _plant_engine(home / ".claude" / "skills")
    in_tree = _plant_engine(repo / "skills")
    assert pm._change_validation_script(repo) == in_tree


def test_change_validation_resolver_none_when_absent(tmp_path, monkeypatch):
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    home.mkdir()
    repo.mkdir()
    monkeypatch.setenv("HOME", str(home))
    assert pm._change_validation_script(repo) is None


# --- Tier 1: approved manifest → delegate to the engine ---------------------

def test_validate_merged_tier1_delegates_pass(cv_repo):
    _write_manifest(cv_repo, approved=True, full_cmd="true")
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["engine"] == "change-validation"
    assert r["status"] == "pass"
    # The engine's parsed payload is surfaced under layer_b.
    assert r["layer_b"]["status"] == "pass"
    assert _VALIDATE_MERGED_KEYS <= set(r)


def test_validate_merged_tier1_delegates_fail(cv_repo):
    _write_manifest(cv_repo, approved=True, full_cmd="false")
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["engine"] == "change-validation"
    assert r["status"] == "fail"
    assert r["layer_b"]["status"] == "fail"


def test_validate_merged_tier1_fail_exits_3(cv_repo):
    # The Click wrapper's exit-3-on-non-pass contract over a failing delegation.
    # In-process via CliRunner so the cv_repo monkeypatch (engine-script resolver)
    # is honored — a subprocess would not see it and would fall through to tier 3.
    from click.testing import CliRunner

    _write_manifest(cv_repo, approved=True, full_cmd="false")
    plan_dir = cv_repo / "docs" / "plans" / "plan-x"
    plan_dir.mkdir(parents=True)
    result = CliRunner().invoke(
        pm.cli, ["validate-merged", str(plan_dir), "--json"],
    )
    assert result.exit_code == 3
    payload = json.loads(result.output)
    assert payload["engine"] == "change-validation"
    assert payload["status"] == "fail"


def test_validate_merged_tier3_exits_0(git_repo):
    # The pass side of the exit contract: tier-3 notice still exits 0.
    from click.testing import CliRunner

    plan_dir = git_repo / "docs" / "plans" / "plan-x"
    plan_dir.mkdir(parents=True)
    result = CliRunner().invoke(
        pm.cli, ["validate-merged", str(plan_dir), "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["engine"] == "none"
    assert payload["status"] == "pass"


# --- Tier 2: unapproved/absent manifest → validate-cmd fallback -------------

def test_validate_merged_tier2_unapproved_manifest_falls_through(cv_repo):
    # Manifest present but `approved: no` → engine refuses cleanly → fall through
    # to the configured validate-cmd (engine == validate-cmd, NOT a failure).
    _write_manifest(cv_repo, approved=False, full_cmd="false")
    (cv_repo / ".yf-plan.local.json").write_text(json.dumps({"validate-cmd": "true"}))
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["engine"] == "validate-cmd"
    assert r["status"] == "pass"
    assert r["validate_cmd_configured"] is True
    assert _VALIDATE_MERGED_KEYS <= set(r)


def test_validate_merged_tier2_no_manifest_runs_validate_cmd(cv_repo):
    (cv_repo / ".yf-plan.local.json").write_text(json.dumps({"validate-cmd": "false"}))
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["engine"] == "validate-cmd"
    assert r["status"] == "fail"


# --- Tier 3: neither manifest nor validate-cmd → notice ---------------------

def test_validate_merged_tier3_notice(git_repo):
    # No approved manifest, no validate-cmd → verbatim cross-plan-not-checked notice.
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["engine"] == "none"
    assert r["status"] == "pass"
    assert r["validate_cmd_configured"] is False
    assert "CROSS-PLAN REGRESSIONS NOT CHECKED" in r["notice"]
    assert _VALIDATE_MERGED_KEYS <= set(r)


# ---------------------------------------------------------------------------
# audit --json-output control-char serialization (#36 regression)
#
# #36 reported `audit --json-output` emitting INVALID JSON when a finding string
# carried a raw control char (tab/newline) — `json.load` failed with
# "Invalid control character at line 20". The current `audit` command serializes
# via `json.dumps` (plan_manager.py audit()), which escapes control chars, so the
# bug is already absent. This test PINS that invariant: a finding `detail`/`report`
# carrying a literal tab and newline must round-trip `json.dumps`→`json.loads`
# with the control chars preserved. A regression to manual string assembly would
# fail here.
# ---------------------------------------------------------------------------

def test_audit_json_output_handles_control_chars(tmp_path, monkeypatch):
    """`audit --json-output` must emit JSON-escaped control chars (#36).

    Pins the `json.dumps` invariant in the `audit` command: a finding detail
    containing a raw tab (`\t`) and newline (`\n`) must produce valid JSON that
    `json.loads` parses, with the control characters preserved verbatim. Manual
    string assembly (the original #36 bug) would emit invalid JSON here.
    """
    from click.testing import CliRunner

    # A plan dir that exists so the click.Path(exists=True) argument validates;
    # _audit_plan is stubbed to return a finding carrying raw control chars, the
    # cleanest way to drive a control char through the real serialization path.
    plan_dir = tmp_path / "docs" / "plans" / "plan-x"
    plan_dir.mkdir(parents=True)

    control_detail = "line-one\tafter-tab\nline-two"
    control_report = "Portability audit\n\twith control chars"

    def _stub_audit(_pd):
        return {
            "status": "fail",
            "findings": [pm._audit_finding("ctrl", "fail", control_detail)],
            "report": control_report,
            "grandfathered": False,
        }

    monkeypatch.setattr(pm, "_audit_plan", _stub_audit)

    result = CliRunner().invoke(pm.cli, ["audit", str(plan_dir), "--json-output"])
    # status=fail → exit 1, but stdout must still be a complete, valid JSON doc.
    assert result.exit_code == 1

    # The raw control chars must NOT appear unescaped in the wire output (that was
    # the #36 bug); json.dumps escapes them as \t / \n.
    assert "\\t" in result.output
    assert "\\n" in result.output

    # Round-trip: parsing succeeds (no JSONDecodeError) and control chars survive.
    payload = json.loads(result.output)
    assert payload["findings"][0]["detail"] == control_detail
    assert payload["report"] == control_report


# ---------------------------------------------------------------------------
# Branch model: base-pinning, named branches, landing-strategy (Issue 6.1 / #47)
# ---------------------------------------------------------------------------

def test_named_branch_helpers():
    assert pm._development_branch(PLAN_ID) == f"{PLAN_ID}-development"
    assert pm._feature_branch(PLAN_ID) == PLAN_ID
    assert pm._execute_branch(PLAN_ID) == f"{PLAN_ID}-execute"


def test_landing_strategy_resolution(lock_cwd):
    assert pm._resolve_landing_strategy() == "main"          # default (no config)
    (lock_cwd / ".yf-plan.local.json").write_text(
        json.dumps({"landing-strategy": "feature-branch"}))
    assert pm._resolve_landing_strategy() == "feature-branch"
    (lock_cwd / ".yf-plan.local.json").write_text(
        json.dumps({"landing-strategy": "bogus"}))
    assert pm._resolve_landing_strategy() == "main"          # invalid → default


def test_execute_base_pinned_not_ambient(git_repo):
    # REQ-BRANCH-002: the execute branch is cut from the PINNED base (default branch),
    # never ambient HEAD — even when a different branch is checked out.
    default = pm._default_branch(git_repo)
    pm._run_git(["checkout", "-b", "other"], cwd=git_repo)
    (git_repo / "x.txt").write_text("x\n")
    pm._run_git(["add", "."], cwd=git_repo)
    pm._run_git(["commit", "-m", "ahead"], cwd=git_repo)

    r = pm._worktree_ensure(PLAN_DIR)
    assert r["viable"] is True
    assert r["base"] == default
    exec_head = pm._run_git(["rev-parse", EXEC_BRANCH], cwd=git_repo).stdout.strip()
    base_head = pm._run_git(["rev-parse", default], cwd=git_repo).stdout.strip()
    other_head = pm._run_git(["rev-parse", "other"], cwd=git_repo).stdout.strip()
    assert exec_head == base_head        # cut from the pinned base
    assert exec_head != other_head       # NOT from ambient HEAD


def test_execute_base_feature_branch_strategy(git_repo):
    # feature-branch strategy → base is the feature <plan-id> branch.
    (git_repo / ".yf-plan.local.json").write_text(
        json.dumps({"landing-strategy": "feature-branch"}))
    pm._run_git(["branch", PLAN_ID], cwd=git_repo)   # the feature branch (base)
    r = pm._worktree_ensure(PLAN_DIR)
    assert r["viable"] is True
    assert r["base"] == PLAN_ID


def test_execute_base_unresolved_when_feature_missing(git_repo):
    # feature-branch strategy with no feature branch → base cannot be resolved.
    (git_repo / ".yf-plan.local.json").write_text(
        json.dumps({"landing-strategy": "feature-branch"}))
    r = pm._worktree_ensure(PLAN_DIR)
    assert r["viable"] is False
    assert r["reason"] == "base-unresolved"


def test_teardown_preserves_feature_branch(git_repo):
    # REQ-BRANCH-004: teardown deletes only <plan-id>-execute; the feature <plan-id>
    # branch is PRESERVED under the feature-branch strategy.
    (git_repo / ".yf-plan.local.json").write_text(
        json.dumps({"landing-strategy": "feature-branch"}))
    pm._run_git(["branch", PLAN_ID], cwd=git_repo)   # feature branch (base)
    pm._worktree_ensure(PLAN_DIR)                     # creates <plan-id>-execute
    result = pm._worktree_teardown(PLAN_DIR, force=True)
    assert result["status"] == "ok"
    assert not pm._branch_exists(EXEC_BRANCH, git_repo)   # execute branch deleted
    assert pm._branch_exists(PLAN_ID, git_repo)           # feature branch preserved


# ---------------------------------------------------------------------------
# Content-fingerprint re-review gate (Issue 6.2 / #64)
# ---------------------------------------------------------------------------

_PLAN_MD = """# Plan: fingerprint test

**ID:** plan-999
**Status:** approved
**Epic:** yf-mol-x1
**Phase log:**
- 2026-07-02 scoping: init

## Objective
Original objective.

## Upstream Issues
| Issue | Resolved By |
|:------|:------------|
| #1 | — |

## Success Criteria
- works
"""


@pytest.fixture
def plan_fp(tmp_path):
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_PLAN_MD)
    return pd


def test_fingerprint_write_and_field(plan_fp):
    fp = pm._plan_content_fingerprint(plan_fp)
    assert fp
    assert pm._write_fingerprint_field(plan_fp, fp) == "written"
    assert f"**Fingerprint:** {fp}" in (plan_fp / "plan.md").read_text()
    assert pm._write_fingerprint_field(plan_fp, fp) == "updated"   # idempotent


def test_fingerprint_field_self_excluded(plan_fp):
    # Writing the **Fingerprint:** header must not change the content hash (self-excluded).
    before = pm._plan_content_fingerprint(plan_fp)
    pm._write_fingerprint_field(plan_fp, before)
    assert pm._plan_content_fingerprint(plan_fp) == before


def test_fingerprint_bookkeeping_edits_do_not_flip(plan_fp):
    fp = pm._plan_content_fingerprint(plan_fp)
    pm._write_fingerprint_field(plan_fp, fp)
    p = plan_fp / "plan.md"
    # (a) filling the Upstream Issues "Resolved By" column (RT-C2) → NOT stale.
    p.write_text(p.read_text().replace("| #1 | — |", "| #1 | yf-mol-x1.2 |"))
    assert pm._fingerprint_status(plan_fp)["stale_approved"] is False
    # (b) a phase-log / review write → NOT stale.
    p.write_text(p.read_text().replace(
        "- 2026-07-02 scoping: init",
        "- 2026-07-02 scoping: init\n- 2026-07-02 review: pass-1"))
    assert pm._fingerprint_status(plan_fp)["stale_approved"] is False


def test_fingerprint_content_edit_flips(plan_fp):
    fp = pm._plan_content_fingerprint(plan_fp)
    pm._write_fingerprint_field(plan_fp, fp)
    p = plan_fp / "plan.md"
    p.write_text(p.read_text().replace("Original objective.", "Changed objective."))
    assert pm._fingerprint_status(plan_fp)["stale_approved"] is True


# --- Fingerprint stability under OKF adoption (Issue 3.6 / REQ-PORT-040, REQ-OKF-
# MIG-003): every metadata surface sits above the first `## `, so adding frontmatter,
# relocating the phase log, and dual-writing both field surfaces are all hash-neutral.

def test_fingerprint_adding_frontmatter_block_is_hash_neutral(plan_fp):
    # (1) Adding a YAML frontmatter block above the first `## ` does not change the
    # content hash — OKF adoption is hash-neutral by construction (REQ-OKF-010).
    import okf as _okf
    before = pm._plan_content_fingerprint(plan_fp)
    _okf.write_frontmatter(
        plan_fp / "plan.md",
        {"type": "Plan", "okf_spec": "OKF-PLAN", "status": "approved"},
    )
    text = (plan_fp / "plan.md").read_text()
    assert text.lstrip().startswith("---")                     # frontmatter present
    assert text.index("okf_spec") < text.index("## Objective")  # above the first `## `
    assert pm._plan_content_fingerprint(plan_fp) == before


def test_fingerprint_removing_phase_log_block_is_hash_neutral(plan_fp):
    # (2) Relocating the **Phase log:** block out of plan.md (Issue 3.4 -> log.md) is
    # hash-neutral: the block lives above the first `## ` (REQ-PORT-040).
    before = pm._plan_content_fingerprint(plan_fp)
    p = plan_fp / "plan.md"
    p.write_text(p.read_text().replace(
        "**Phase log:**\n- 2026-07-02 scoping: init\n", ""))
    assert "**Phase log:**" not in p.read_text()
    assert pm._plan_content_fingerprint(plan_fp) == before


def test_fingerprint_dual_write_both_surfaces_is_hash_neutral(plan_fp):
    # (3) The dual-write of `**Field:**` + frontmatter (one model, both surfaces)
    # does not change the fingerprint — both surfaces are self-excluded.
    before = pm._plan_content_fingerprint(plan_fp)
    pm._write_plan_fields(plan_fp, {"status": "approved", "fingerprint": "deadbeef"})
    text = (plan_fp / "plan.md").read_text()
    # both surfaces landed (dual-write consistency), both above the first `## `
    assert "**Status:** approved" in text
    fm, _ = __import__("okf").read_frontmatter(text)
    assert fm.get("status") == "approved"
    assert text.index("**Status:**") < text.index("## Objective")
    assert pm._plan_content_fingerprint(plan_fp) == before


# ---------------------------------------------------------------------------
# Dual-mode header-field accessor (Issue 3.2 / REQ-DATA-015 / REQ-OKF-020/021)
# ---------------------------------------------------------------------------

_LEGACY_PLAN = """# Plan: dual test

**ID:** plan-777
**Author:** tester
**Created:** 2026-07-01
**Status:** review
**Epic:** yf-mol-z9
**Phase log:**
- 2026-07-01 scoping: init

## Objective
Body.
"""

_FRONTMATTER_PLAN = """---
type: Plan
okf_spec: OKF-PLAN
id: plan-777
author: tester
created: 2026-07-01
status: review
epic: yf-mol-z9
---
# Plan: dual test

## Objective
Body.
"""

_DUAL_PLAN = """---
type: Plan
okf_spec: OKF-PLAN
id: plan-777
author: tester
created: 2026-07-01
status: review
epic: yf-mol-z9
---
# Plan: dual test

**ID:** plan-777
**Author:** tester
**Created:** 2026-07-01
**Status:** review
**Epic:** yf-mol-z9
**Phase log:**
- 2026-07-01 scoping: init

## Objective
Body.
"""


def test_read_field_all_three_forms_identical():
    # A **Field:**-only (legacy), a frontmatter-only, and a dual plan must read
    # IDENTICALLY through the single accessor (REQ-DATA-015 / REQ-OKF-021).
    for key, want in [("status", "review"), ("epic", "yf-mol-z9"),
                      ("id", "plan-777"), ("author", "tester"),
                      ("created", "2026-07-01")]:
        a = pm._read_plan_field(_LEGACY_PLAN, key)
        b = pm._read_plan_field(_FRONTMATTER_PLAN, key)
        c = pm._read_plan_field(_DUAL_PLAN, key)
        assert a == b == c == want, (key, a, b, c)


def test_read_field_frontmatter_wins_over_stale_field_line():
    # Frontmatter value overrides a divergent legacy **Field:** line (REQ-OKF-021).
    stale = _DUAL_PLAN.replace("status: review", "status: approved")
    assert pm._read_plan_field(stale, "status") == "approved"


def test_read_field_absent_returns_none():
    assert pm._read_plan_field(_LEGACY_PLAN, "fingerprint") is None


def test_read_status_epic_fp_route_through_accessor():
    assert pm._read_plan_status(_FRONTMATTER_PLAN) == "review"
    assert pm._read_plan_epic_field(_FRONTMATTER_PLAN) == "yf-mol-z9"
    assert pm._read_plan_fingerprint_field(_FRONTMATTER_PLAN) is None


def test_semantic_accessors_identical_across_all_three_forms():
    # Consolidated dual-representation read (Issue 3.6, extends 3.2): the SEMANTIC
    # accessors (status/epic) resolve a `**Field:**`-only (legacy), a frontmatter-only,
    # and a dual plan IDENTICALLY — not just the low-level `_read_plan_field`.
    for text in (_LEGACY_PLAN, _FRONTMATTER_PLAN, _DUAL_PLAN):
        assert pm._read_plan_status(text) == "review", text
        assert pm._read_plan_epic_field(text) == "yf-mol-z9", text
        assert pm._read_plan_fingerprint_field(text) is None, text


def _both_surfaces(plan_dir, key, label):
    """Return (frontmatter_value, field_line_value) for a header key."""
    import okf as _okf  # vendored sibling, importable because pm added scripts/ to path
    text = (plan_dir / "plan.md").read_text()
    fm, _ = _okf.read_frontmatter(text)
    line_val = None
    for ln in text.splitlines():
        if ln.startswith(f"**{label}:**"):
            line_val = ln.split(f"**{label}:**", 1)[1].strip()
            break
    return fm.get(key), line_val


def test_write_plan_fields_emits_both_surfaces(tmp_path):
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN)  # frontmatter-free start
    pm._write_plan_fields(pd, {"status": "approved"})
    # Both surfaces present and in sync for the updated field AND the pre-existing
    # identity fields (dual-write consistency — never one surface alone).
    for key, label, want in [("status", "Status", "approved"),
                             ("id", "ID", "plan-777"),
                             ("epic", "Epic", "yf-mol-z9")]:
        fm_v, line_v = _both_surfaces(pd, key, label)
        assert fm_v == line_v == want, (key, fm_v, line_v)


def test_write_plan_fields_preserves_phase_log(tmp_path):
    # The 3.2 dual-writer preserves a legacy in-plan.md **Phase log:** block verbatim
    # (it is not a PLAN_FIELD_LABELS label); Issue 3.4 does not touch that path. With
    # no log.md present, the relocated reader falls back to the legacy block.
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN)
    pm._write_plan_fields(pd, {"status": "approved"})
    text = (pd / "plan.md").read_text()
    assert "**Phase log:**" in text
    assert "- 2026-07-01 scoping: init" in text
    # No log.md → reader falls back to the in-plan.md phase-log block.
    assert not (pd / "log.md").exists()
    assert pm._plan_first_scoping_date(pd) == "2026-07-01"


def test_update_status_dual_writes(tmp_path):
    from click.testing import CliRunner
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN)
    r = CliRunner().invoke(pm.update_status, [str(pd), "approved", "-m", "ready"])
    assert r.exit_code == 0, r.output
    fm_v, line_v = _both_surfaces(pd, "status", "Status")
    assert fm_v == line_v == "approved"
    # Issue 3.4: the phase-transition entry is appended to the reserved log.md
    # (newest-first, `- <status>: <message>`), NOT plan.md.
    log_text = (pd / "log.md").read_text()
    assert "- approved: ready" in log_text
    assert re.search(r"## \d{4}-\d{2}-\d{2}", log_text)
    assert "approved: ready" not in (pd / "plan.md").read_text()


def test_record_epic_dual_writes(tmp_path):
    from click.testing import CliRunner
    pd = tmp_path / "plan"
    pd.mkdir()
    plan = _LEGACY_PLAN.replace("**Epic:** yf-mol-z9\n", "")  # no epic yet
    (pd / "plan.md").write_text(plan)
    r = CliRunner().invoke(pm.record_epic, [str(pd), "yf-mol-new"])
    assert r.exit_code == 0, r.output
    fm_v, line_v = _both_surfaces(pd, "epic", "Epic")
    assert fm_v == line_v == "yf-mol-new"
    # Issue 3.4: the inert intake entry is appended to the reserved log.md, not plan.md.
    assert "- intake: epic yf-mol-new poured" in (pd / "log.md").read_text()
    assert "intake: epic yf-mol-new poured" not in (pd / "plan.md").read_text()
    # Idempotent: re-running does not append a duplicate intake entry.
    r2 = CliRunner().invoke(pm.record_epic, [str(pd), "yf-mol-new"])
    assert r2.exit_code == 0, r2.output
    assert (pd / "log.md").read_text().count("intake: epic yf-mol-new poured") == 1


def test_dual_write_is_hash_neutral(tmp_path):
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN)
    before = pm._plan_content_fingerprint(pd)
    pm._write_plan_fields(pd, {"status": "approved", "fingerprint": "deadbeef"})
    assert pm._plan_content_fingerprint(pd) == before


# ---------------------------------------------------------------------------
# Phase-log relocation to reserved log.md (Issue 3.4 / REQ-DATA-012, REQ-PORT-006,
# REQ-PORT-ACT) — the R1 guard: three plan.md-text parsers must rebind to log.md
# (newest-first heading+bullet form) while a legacy in-plan.md **Phase log:** block
# still resolves for the ~29 un-migrated plans.
# ---------------------------------------------------------------------------

# A newest-first reserved log.md (as `okf.append_log` produces): headings descend,
# newest bullet first under each heading. Note the OLDEST scoping is 2026-05-01.
_LOG_MD = """# Log

## 2026-06-10

- review: presented v2
- approved: ready

## 2026-05-20

- review: presented v1

## 2026-05-01

- scoping: initial scope captured
"""

# A legacy plan with the phase log still IN plan.md and NO log.md (un-migrated).
_LEGACY_PLAN_WITH_PHASE_LOG = """# Plan: legacy

**ID:** plan-legacy
**Status:** review
**Phase log:**
- 2026-05-01 scoping: initial scope captured
- 2026-05-20 review: presented v1
- 2026-06-10 review: presented v2

## Objective
Body.
"""


def _plan_with_log(tmp_path, log_text=_LOG_MD, plan_text=_LEGACY_PLAN):
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(plan_text)
    (pd / "log.md").write_text(log_text)
    return pd


def test_first_scoping_date_from_log_md(tmp_path):
    # Oldest ## YYYY-MM-DD heading bearing a scoping: bullet (log.md is newest-first).
    pd = _plan_with_log(tmp_path)
    assert pm._plan_first_scoping_date(pd) == "2026-05-01"


def test_first_scoping_date_legacy_fallback(tmp_path):
    # No log.md → fall back to the in-plan.md **Phase log:** block (un-migrated plan).
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN_WITH_PHASE_LOG)
    assert not (pd / "log.md").exists()
    assert pm._plan_first_scoping_date(pd) == "2026-05-01"


def test_review_count_from_log_md(tmp_path):
    # Count `- review:` bullets across log.md date headings (REQ-PORT-006).
    pd = _plan_with_log(tmp_path)
    assert pm._plan_review_line_count(pd) == 2


def test_review_count_legacy_fallback(tmp_path):
    # No log.md → count legacy inline-date review lines in the plan.md phase log.
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN_WITH_PHASE_LOG)
    assert pm._plan_review_line_count(pd) == 2


def test_log_md_takes_precedence_over_legacy_block(tmp_path):
    # When BOTH surfaces exist, log.md is authoritative — the stale plan.md block is
    # NOT merged/double-counted. log.md here carries 2 reviews; the plan.md block 3.
    pd = _plan_with_log(tmp_path, plan_text=_LEGACY_PLAN_WITH_PHASE_LOG)
    assert pm._plan_review_line_count(pd) == 2          # from log.md, not 3
    assert pm._plan_first_scoping_date(pd) == "2026-05-01"


def test_empty_log_md_does_not_fall_back(tmp_path):
    # A present-but-empty log.md means "migrated, no entries yet" — it must NOT
    # trigger the legacy fallback (which would resurrect a stale plan.md block).
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN_WITH_PHASE_LOG)
    (pd / "log.md").write_text("# Log\n\n")
    assert pm._plan_review_line_count(pd) == 0
    assert pm._plan_first_scoping_date(pd) is None


def test_seed_plan_md_seeds_scoping_to_log_md(tmp_path):
    # A fresh plan seeds the initial scoping entry into log.md — NOT a plan.md block —
    # so the grandfather date survives the first update_status (which creates log.md).
    pd = tmp_path / "plan"
    pd.mkdir()
    pm.seed_plan_md(pd, "plan-001-t-abc123", "seed test", "tester")
    plan_text = (pd / "plan.md").read_text()
    assert "**Phase log:**" not in plan_text
    log_text = (pd / "log.md").read_text()
    assert "- scoping: initial scope captured" in log_text
    assert re.search(r"## \d{4}-\d{2}-\d{2}", log_text)
    assert pm._plan_first_scoping_date(pd) is not None


def test_update_status_appends_newest_first_to_log_md(tmp_path):
    from click.testing import CliRunner
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text(_LEGACY_PLAN)
    # Seed an older-dated entry, then append a newer one; newest heading must lead.
    pm.okf.append_log(pd, "scoping: init", date="2026-05-01")
    r = CliRunner().invoke(pm.update_status, [str(pd), "review", "-m", "v1"])
    assert r.exit_code == 0, r.output
    log_text = (pd / "log.md").read_text()
    headings = re.findall(r"## (\d{4}-\d{2}-\d{2})", log_text)
    # Newest-first: the review append's (today's) heading precedes the seeded 2026-05-01.
    assert headings == sorted(headings, reverse=True)
    assert headings[-1] == "2026-05-01"
    assert "- review: v1" in log_text


def test_seeded_plan_survives_first_update_status(tmp_path):
    # End-to-end R1 guard: seed → update_status must NOT lose the scoping date.
    from click.testing import CliRunner
    pd = tmp_path / "plan"
    pd.mkdir()
    pm.seed_plan_md(pd, "plan-002-t-def456", "e2e", "tester")
    seeded_scoping = pm._plan_first_scoping_date(pd)
    assert seeded_scoping is not None
    r = CliRunner().invoke(pm.update_status, [str(pd), "review", "-m", "v1"])
    assert r.exit_code == 0, r.output
    # scoping date preserved; one review now counted from log.md.
    assert pm._plan_first_scoping_date(pd) == seeded_scoping
    assert pm._plan_review_line_count(pd) == 1


# ---------------------------------------------------------------------------
# OKF-PLAN bundle construction (Issue 3.3 / REQ-PORT-001, REQ-PORT-050,
# REQ-OKF-031) — a freshly-constructed bundle is born OKF-conformant.
# ---------------------------------------------------------------------------

def _fresh_bundle(tmp_path):
    """Construct a bundle exactly as `init` does (seed plan.md + scaffolding)."""
    import okf as _okf  # noqa: F401 (ensures the vendored engine is importable)
    pd = tmp_path / "plan-101-t-abc123"
    pm.make_plan_dir("plan-101-t-abc123", pd.parent)
    pm.seed_plan_md(pd, "plan-101-t-abc123", "bundle build test", "tester")
    pm.seed_portability_scaffolding(pd, "plan-101-t-abc123", "bundle build test", "tester")
    return pd


def test_construction_seeds_index_not_readme(tmp_path):
    # The orientation surface is the OKF-reserved `index.md`, not `README.md`.
    pd = _fresh_bundle(tmp_path)
    assert (pd / "index.md").exists()
    assert not (pd / "README.md").exists()
    idx = (pd / "index.md").read_text()
    # A listing: `#` heading + child bullets, NOT the legacy File map/Reading order.
    assert idx.lstrip().startswith("---")            # okf_version frontmatter
    assert "okf_version:" in idx
    assert re.search(r"^# ", idx, re.MULTILINE)
    assert "- [plan.md](plan.md)" in idx
    assert "- [context.md](context.md)" in idx
    assert "File map" not in idx and "Reading order" not in idx


def test_construction_reserved_files_carry_no_type(tmp_path):
    # Reserved index.md / log.md carry no `type` and no `okf_spec` (REQ-OKF-031).
    import okf as _okf
    pd = _fresh_bundle(tmp_path)
    for reserved in ("index.md", "log.md"):
        fm, _ = _okf.read_frontmatter((pd / reserved).read_text())
        assert "type" not in fm, reserved
        assert "okf_spec" not in fm, reserved


def test_construction_plan_md_typed_and_dual(tmp_path):
    # plan.md carries type: Plan + okf_spec + the dual identity fields (frontmatter
    # AND `**Field:**`), all above the first `## ` (REQ-PORT-050 / REQ-OKF-020/010).
    import okf as _okf
    pd = _fresh_bundle(tmp_path)
    text = (pd / "plan.md").read_text()
    fm, _ = _okf.read_frontmatter(text)
    assert fm.get("type") == "Plan"
    assert fm.get("okf_spec") == "OKF-PLAN"
    assert fm.get("id") == "plan-101-t-abc123"
    assert fm.get("status") == "scoping"
    # dual surface: the `**Field:**` header lines still present and in sync
    for key, label in [("id", "ID"), ("status", "Status")]:
        fm_v, line_v = _both_surfaces(pd, key, label)
        assert fm_v == line_v, (key, fm_v, line_v)
    # frontmatter + field block sit above the first `## `
    assert text.index("okf_spec") < text.index("## Objective")
    assert text.index("**ID:**") < text.index("## Objective")


def test_construction_context_md_typed_environment(tmp_path):
    # context.md is the Environment concept doc (OKF-EXTENSION §1a).
    import okf as _okf
    pd = _fresh_bundle(tmp_path)
    fm, _ = _okf.read_frontmatter((pd / "context.md").read_text())
    assert fm.get("type") == "Environment"
    assert fm.get("okf_spec") == "OKF-PLAN"


def test_construction_reference_typed_reference(tmp_path):
    # references/upstream-<N>.md is a Reference concept doc.
    import okf as _okf
    pd = _fresh_bundle(tmp_path)
    pm.seed_upstream_triage(
        pd, "bundle build test",
        [{"number": 42, "title": "T", "body": "b", "state": "open",
          "labels": ["x"], "url": "u"}],
    )
    fm, _ = _okf.read_frontmatter((pd / "references" / "upstream-42.md").read_text())
    assert fm.get("type") == "Reference"
    assert fm.get("okf_spec") == "OKF-PLAN"
    # upstream-triage.md is typed Reference too (§1a)
    tfm, _ = _okf.read_frontmatter((pd / "upstream-triage.md").read_text())
    assert tfm.get("type") == "Reference"


def test_construction_bundle_passes_engine_check(tmp_path):
    # `yf-okf check` (the vendored engine's check_conformance) on a freshly-
    # constructed init bundle is error-free (REQ-PORT-050 conformance floor).
    import okf as _okf
    pd = _fresh_bundle(tmp_path)
    findings = _okf.check_conformance(pd, skill="yf-plan")
    assert findings.ok, [f.as_dict() for f in findings.findings]
    assert "OKF-PLAN" in findings.rulesets_composed


# ---------------------------------------------------------------------------
# Portability AUDIT rework to the OKF model (Issue 3.5 / REQ-PORT-001, REQ-PORT-006,
# REQ-PORT-050, REQ-DATA-015 R7). These drive the REAL `_audit_plan` (not a stub):
# check #1 (index.md listing shape), #5 (count-equality from log.md), #7 (OKF
# conformance floor), #8 (dual-write divergence), and the OKF-legacy grandfather gate.
# ---------------------------------------------------------------------------

_AUDIT_PLAN_MD = """---
type: Plan
okf_spec: OKF-PLAN
id: plan-500-t-abc
author: tester
created: 2026-05-01
status: review
---
# Plan: audit fixture

**ID:** plan-500-t-abc
**Author:** tester
**Created:** 2026-05-01
**Status:** review

## Objective
A conformant OKF-native plan bundle.

## Motivation
This plan exists to exercise the reworked portability audit against a fully
OKF-conformant, portable bundle. Affected: the yf-plan maintainers.

## Success Criteria
- The reworked audit passes clean.
"""

_AUDIT_INDEX_MD = """---
okf_version: 0.2
---

# plan-500-t-abc

> audit fixture

- [plan.md](plan.md) - the plan of record
- [context.md](context.md) - environment snapshot
"""

_AUDIT_LOG_MD = """# Log

## 2026-05-01

- scoping: initial scope captured
"""

_AUDIT_CONTEXT_MD = """---
type: Environment
okf_spec: OKF-PLAN
---
# Context

## Project environment
The beads-skills repository — a Python skill codebase for Claude Code.

## Tool inventory
<!-- snapshot: host=testhost date=2026-05-01 -->
- `bd`: 1.1.0
- `git`: 2.40

## Paths
- repo root: the git toplevel of beads-skills.

## Operator identity
tester, project maintainer, full authority to approve.

## Runtime assumptions
Assumes uv and python3 are on PATH.
"""


def _okf_bundle(tmp_path, *, reviews=0):
    """Construct a fully OKF-conformant, portable, OKF-NATIVE plan bundle that the
    reworked `_audit_plan` passes clean. `reviews` seeds N `review:` log entries + N
    matching `reviews/pass-<i>.md` files (count-equality, REQ-PORT-006)."""
    pd = tmp_path / "plan-500-t-abc"
    pd.mkdir()
    (pd / "plan.md").write_text(_AUDIT_PLAN_MD)
    (pd / "index.md").write_text(_AUDIT_INDEX_MD)
    (pd / "context.md").write_text(_AUDIT_CONTEXT_MD)
    log_text = _AUDIT_LOG_MD
    if reviews:
        review_lines = "".join(f"- review: presented v{i + 1}\n" for i in range(reviews))
        log_text = f"# Log\n\n## 2026-05-02\n\n{review_lines}\n## 2026-05-01\n\n- scoping: initial scope captured\n"
        rdir = pd / "reviews"
        rdir.mkdir()
        for i in range(reviews):
            (rdir / f"pass-{i + 1}.md").write_text(
                "---\ntype: Review\nokf_spec: OKF-PLAN\n---\n"
                f"# Review pass-{i + 1}\n\n## Verdict: APPROVE\n")
    (pd / "log.md").write_text(log_text)
    return pd


def test_audit_fresh_okf_bundle_passes_clean(tmp_path):
    # A fully OKF-conformant, portable, OKF-native bundle → status pass, no findings.
    pd = _okf_bundle(tmp_path)
    result = pm._audit_plan(pd)
    assert result["status"] == "pass", result["report"]
    assert result["okf_native"] is True
    assert not any(f["status"] == "fail" for f in result["findings"]), result["report"]


def test_audit_legacy_bundle_passes_with_warns_only(tmp_path):
    # An un-migrated legacy bundle (README, in-plan.md phase log, NO frontmatter, NO
    # index.md/log.md) is OKF-legacy: missing OKF scaffolding downgrades to warn, so
    # the bundle PASSES (the key regression guard for the ~29 existing plans).
    pd = tmp_path / "plan-legacy"
    pd.mkdir()
    (pd / "plan.md").write_text(
        "# Plan: legacy\n\n"
        "**ID:** plan-legacy\n"
        "**Status:** review\n"
        "**Phase log:**\n"
        "- 2026-05-01 scoping: initial scope captured\n\n"  # scoping only, 0 reviews
        "## Objective\nBody.\n"
    )  # no frontmatter → OKF-legacy
    (pd / "README.md").write_text("# Legacy\n\n## File map\n## Reading order\n")
    (pd / "context.md").write_text(_AUDIT_CONTEXT_MD.split("---\n", 2)[2])  # strip fm
    (pd / "motivation.md").write_text("Real motivation prose for the legacy plan.\n")
    result = pm._audit_plan(pd)
    assert result["okf_native"] is False
    # index.md + type/okf_spec absences are warns, not fails.
    okf_findings = [f for f in result["findings"] if f["item"].startswith(("index.md", "okf:"))]
    assert okf_findings, "expected OKF scaffolding findings"
    assert all(f["status"] == "warn" for f in okf_findings), result["report"]
    assert result["status"] == "pass", result["report"]


def test_audit_okf_native_missing_index_fails(tmp_path):
    # An OKF-native bundle (plan.md frontmatter present) with NO index.md → check #1
    # hard-fails (REQ-PORT-001). Not grandfathered, not OKF-legacy.
    pd = _okf_bundle(tmp_path)
    (pd / "index.md").unlink()
    result = pm._audit_plan(pd)
    assert result["status"] == "fail"
    idx = [f for f in result["findings"] if f["item"] == "index.md"]
    assert idx and idx[0]["status"] == "fail", result["report"]


def test_audit_index_not_a_listing_fails(tmp_path):
    # An OKF-native bundle whose index.md is legacy README prose (no `- [x](y)`
    # bullets) fails the listing-shape check (REQ-PORT-001).
    pd = _okf_bundle(tmp_path)
    (pd / "index.md").write_text(
        "---\nokf_version: 0.2\n---\n# plan\n\n## File map\n\n## Reading order\n")
    result = pm._audit_plan(pd)
    idx = [f for f in result["findings"] if f["item"] == "index.md"]
    assert idx and idx[0]["status"] == "fail"
    assert "not an OKF listing" in idx[0]["detail"], result["report"]


def test_audit_typeless_nonreserved_md_fails_req_port_050(tmp_path):
    # A non-reserved .md with no frontmatter/type in an OKF-native bundle → the
    # REQ-PORT-050 conformance floor hard-fails (backed by check_conformance).
    pd = _okf_bundle(tmp_path)
    (pd / "findings").mkdir()
    (pd / "findings" / "exp-001.md").write_text("# Experiment\n\nno frontmatter here.\n")
    result = pm._audit_plan(pd)
    assert result["status"] == "fail"
    port050 = [f for f in result["findings"]
               if f["item"].startswith("okf:") and "exp-001" in f["item"]]
    assert port050 and all(f["status"] == "fail" for f in port050), result["report"]


def test_audit_wrong_okf_spec_value_fails(tmp_path):
    # A non-reserved .md whose okf_spec is present but NOT `OKF-PLAN` → REQ-PORT-050
    # selector failure (engine checks presence; the audit checks the value).
    pd = _okf_bundle(tmp_path)
    (pd / "findings").mkdir()
    (pd / "findings" / "exp-001.md").write_text(
        "---\ntype: Finding\nokf_spec: OKF-RESEARCH\n---\n# Exp\n")
    result = pm._audit_plan(pd)
    bad = [f for f in result["findings"]
           if f["item"].startswith("okf:") and "OKF-RESEARCH" in f["detail"]]
    assert bad and all(f["status"] == "fail" for f in bad), result["report"]


def test_audit_dual_write_divergence_fails_r7(tmp_path):
    # A divergence between the frontmatter value and the `**Field:**` line (writer bug
    # or hand-edit) is a hard fail (R7 / REQ-DATA-015) — always, never grandfathered.
    pd = _okf_bundle(tmp_path)
    p = pd / "plan.md"
    # frontmatter says status: review; corrupt the **Status:** line to disagree.
    p.write_text(p.read_text().replace("**Status:** review", "**Status:** approved"))
    result = pm._audit_plan(pd)
    assert result["status"] == "fail"
    r7 = [f for f in result["findings"] if f["item"] == "dual-write:status"]
    assert r7 and r7[0]["status"] == "fail", result["report"]
    assert "divergence" in r7[0]["detail"]


def test_audit_dual_write_in_sync_passes_r7(tmp_path):
    # No divergence when the two surfaces agree → no R7 finding.
    pd = _okf_bundle(tmp_path)
    result = pm._audit_plan(pd)
    assert not any(f["item"].startswith("dual-write:") for f in result["findings"]), \
        result["report"]


def test_audit_review_count_equality_from_log_md(tmp_path):
    # Count-equality (REQ-PORT-006) keys on log.md `review:` entries. Two review
    # entries + two pass files → pass; delete one pass file → count mismatch fail.
    pd = _okf_bundle(tmp_path, reviews=2)
    result = pm._audit_plan(pd)
    assert result["status"] == "pass", result["report"]
    (pd / "reviews" / "pass-2.md").unlink()  # now 1 file vs 2 log review entries
    result2 = pm._audit_plan(pd)
    rev = [f for f in result2["findings"] if f["item"] == "reviews/"]
    assert rev and rev[0]["status"] == "fail", result2["report"]
    assert "expected 2" in rev[0]["detail"]


# ---------------------------------------------------------------------------
# Migrated-legacy-plan SAFETY (Issue 3.6 capability gate — Epic 3): a REAL legacy
# plan folder, once migrated by okf.migrate, passes the audit as GRANDFATHERED with
# count-equality (REQ-PORT-006) and content fingerprint (REQ-OKF-MIG-003) preserved.
# Exercises the real engine migrate over real content (README->index.md verbatim,
# **Phase log:** -> log.md transcription, per-file type stamping).
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LEGACY_PLAN_SRC = _REPO_ROOT / "docs" / "plans" / "plan-001-james-dixson-c88e7a"

# A portable, pre-activation context.md (legacy form, no frontmatter) — replaces
# plan-001's genuinely-unfilled placeholder sections so the ONLY variables under test
# are the migration effects (grandfather / count-equality / fingerprint), not
# plan-001's own pre-portability-contract incompleteness.
_PORTABLE_LEGACY_CONTEXT = """# Project Environment Context

## Project environment

The beads-skills repository: a Python skill codebase for Claude Code, managed
with uv and git.

## Tool inventory

<!-- snapshot: host=testhost date=2026-04-04 -->

- `bd`: 1.1.0
- `git`: 2.50

## Paths

- Repo root: the git toplevel of beads-skills.

## Operator identity

tester, project maintainer, with full authority to approve plans.

## Runtime assumptions

Assumes uv and python3 are on PATH; no network side effects at plan time.
"""


def _legacy_plan_copy(tmp_path):
    """Copy the REAL plan-001 legacy folder and sanitize the COPY into a genuine
    *pre-activation, portable* legacy plan: backdate the first `scoping:` date to
    strictly before the activation date (so it is date-grandfathered — plan-001's
    real scoping date lands exactly ON activation), and fill the placeholder context
    sections. Everything else (README, in-plan.md **Phase log:** with its two
    `review:` lines, reviews/pass-1&2.md, references/) is the real legacy content."""
    import shutil
    dst = tmp_path / "plan-001-copy"
    shutil.copytree(_LEGACY_PLAN_SRC, dst)
    # backdate first scoping: 2026-04-05 (== activation) -> 2026-04-04 (< activation)
    p = dst / "plan.md"
    p.write_text(p.read_text().replace(
        "- 2026-04-05 scoping: initial scope captured",
        "- 2026-04-04 scoping: initial scope captured", 1))
    (dst / "context.md").write_text(_PORTABLE_LEGACY_CONTEXT)
    return dst


@pytest.mark.skipif(not _LEGACY_PLAN_SRC.is_dir(),
                    reason="real plan-001 legacy folder not present in this checkout")
def test_migrated_legacy_plan_audit_passes_grandfathered(tmp_path):
    # THE capability-gate assertion: a migrated legacy plan folder passes the audit.
    import okf as _okf
    pd = _legacy_plan_copy(tmp_path)

    # Pre-migration it is a grandfathered OKF-legacy bundle -> already passes (warns).
    pre = pm._audit_plan(pd)
    assert pre["status"] == "pass", pre["report"]
    assert pre["grandfathered"] is True
    assert pre["okf_native"] is False  # no plan.md frontmatter yet

    fp_before = pm._plan_content_fingerprint(pd)
    scoping_before = pm._plan_first_scoping_date(pd)
    reviews_before = pm._plan_review_line_count(pd)
    passfiles = len(list((pd / "reviews").glob("pass-*.md")))
    assert reviews_before == passfiles == 2  # count-equal before migration

    _okf.migrate(pd, skill="yf-plan")  # migrate the COPY in place

    post = pm._audit_plan(pd)
    # (a) audit status: pass — migration gaps only warn on a grandfathered plan
    assert post["status"] == "pass", post["report"]
    # (b) now OKF-native (migrate stamped plan.md frontmatter) yet still grandfathered
    assert post["okf_native"] is True
    assert post["grandfathered"] is True
    # (c) grandfather status preserved: first scoping date intact and < activation
    assert pm._plan_first_scoping_date(pd) == scoping_before == "2026-04-04"
    assert scoping_before < pm.PORTABILITY_ACTIVATION_DATE
    # (d) REQ-PORT-006 count-equality preserved across migration (2 == 2)
    assert pm._plan_review_line_count(pd) == 2
    assert len(list((pd / "reviews").glob("pass-*.md"))) == 2
    assert not any(f["item"] == "reviews/" for f in post["findings"]), post["report"]
    # (e) content fingerprint unchanged (REQ-OKF-MIG-003 — not stale-approved)
    assert pm._plan_content_fingerprint(pd) == fp_before


@pytest.mark.skipif(not _LEGACY_PLAN_SRC.is_dir(),
                    reason="real plan-001 legacy folder not present in this checkout")
def test_migrated_legacy_index_verbatim_only_warns(tmp_path):
    # The 3.5 migrate flag: README.md -> index.md is renamed VERBATIM (not a listing).
    # On a grandfathered plan this must only WARN, never fail (REQ-PORT-ACT-OKF gate).
    import okf as _okf
    pd = _legacy_plan_copy(tmp_path)
    _okf.migrate(pd, skill="yf-plan")
    assert (pd / "index.md").exists() and not (pd / "README.md").exists()
    assert not pm._index_is_listing((pd / "index.md").read_text())  # verbatim, not a listing
    result = pm._audit_plan(pd)
    idx = [f for f in result["findings"] if f["item"] == "index.md"]
    assert idx and idx[0]["status"] == "warn", result["report"]  # warn, not fail
    assert result["status"] == "pass", result["report"]


@pytest.mark.skipif(not _LEGACY_PLAN_SRC.is_dir(),
                    reason="real plan-001 legacy folder not present in this checkout")
def test_migrated_legacy_plan_count_equality_preserved(tmp_path):
    # Focused REQ-PORT-006 guard: the **Phase log:**'s two `review:` lines survive the
    # extract-log transcription into log.md (the engine fix), so the log-review count
    # still equals the reviews/pass-*.md count after migration.
    import okf as _okf
    pd = _legacy_plan_copy(tmp_path)
    _okf.migrate(pd, skill="yf-plan")
    log_text = (pd / "log.md").read_text()
    assert log_text.count("- review:") == 2, log_text
    assert pm._plan_review_line_count(pd) == len(list((pd / "reviews").glob("pass-*.md")))


def _seed_plan(git_repo, branch=None):
    pd = Path("docs/plans/plan-999")
    (git_repo / pd).mkdir(parents=True, exist_ok=True)
    (git_repo / pd / "plan.md").write_text(
        "# Plan: obj\n\n**Status:** approved\n\n## Objective\nx\n")
    if branch:
        pm._run_git(["checkout", "-b", branch], cwd=git_repo)
    return pd


def test_commit_plan_refuses_default_branch(git_repo):
    pd = _seed_plan(git_repo)
    r = pm._commit_plan(pd)
    assert r["status"] == "refused"
    assert r["reason"] == "default-branch"


def test_commit_plan_refuses_detached_head(git_repo):
    pd = _seed_plan(git_repo)
    pm._run_git(["add", "."], cwd=git_repo)
    pm._run_git(["commit", "-m", "p"], cwd=git_repo)
    pm._run_git(["checkout", "--detach"], cwd=git_repo)
    r = pm._commit_plan(pd)
    assert r["status"] == "refused"
    assert r["reason"] == "detached-head"


def test_commit_plan_commits_on_plan_branch_then_noop(git_repo):
    pd = _seed_plan(git_repo, branch="plan-999")
    r = pm._commit_plan(pd)
    assert r["status"] == "committed"
    assert r["branch"] == "plan-999"
    assert "commit" in r
    # nothing new staged → idempotent no-op (no empty commit)
    assert pm._commit_plan(pd)["status"] == "noop"


def test_commit_plan_skips_gitignored_beads_local_only(git_repo):
    # Local-only beads: `.beads/` is gitignored (gh-only interchange). commit-plan
    # must commit the plan dir cleanly and SKIP `.beads/` instead of erroring on the
    # ignored pathspec (#71). Without the fix `git add -- ... .beads` fails.
    (git_repo / ".beads" / "local.db").write_text("x")  # an ignored path under .beads
    (git_repo / ".gitignore").write_text(".beads/\n")
    pm._run_git(["add", ".gitignore"], cwd=git_repo)
    pm._run_git(["commit", "-m", "ignore beads"], cwd=git_repo)
    pd = _seed_plan(git_repo, branch="plan-777")
    r = pm._commit_plan(pd)
    assert r["status"] == "committed"
    assert "beads_note" in r  # operator told beads state was not co-committed
    # `.beads/` must NOT be in the commit (it is ignored).
    files = pm._run_git(
        ["show", "--name-only", "--pretty=format:", "HEAD"], cwd=git_repo).stdout
    assert ".beads" not in files


def test_commit_plan_co_commits_tracked_beads(git_repo):
    # The standard (non-local-only) model: `.beads/` is tracked, so it is co-committed.
    (git_repo / ".beads" / "issues.jsonl").write_text('{"id":"x"}\n')
    pd = _seed_plan(git_repo, branch="plan-778")
    r = pm._commit_plan(pd)
    assert r["status"] == "committed"
    assert "beads_note" not in r
    files = pm._run_git(
        ["show", "--name-only", "--pretty=format:", "HEAD"], cwd=git_repo).stdout
    assert ".beads/issues.jsonl" in files


# ---------------------------------------------------------------------------
# ready-check gate (Issue 1.5 / #69) — REQ-PLAN-066
#
# ready-check verifies BOTH approval-prompt preconditions: the LAST recorded
# red-team verdict (highest reviews/pass-N.md) is APPROVE (REQ-PLAN-030), AND the
# portability audit passes (REQ-PLAN-033). Exit 3 when not ready, 0 when ready.
# `_audit_plan` is stubbed to control the audit half in isolation.
# ---------------------------------------------------------------------------

def _mk_review_plan(tmp_path, verdicts):
    """A plan dir with reviews/pass-N.md carrying `verdicts` (1-indexed)."""
    pd = tmp_path / "plan"
    (pd / "reviews").mkdir(parents=True)
    (pd / "plan.md").write_text("# Plan: x\n\n**Status:** review\n\n## Objective\nx\n")
    for i, v in enumerate(verdicts, start=1):
        (pd / "reviews" / f"pass-{i}.md").write_text(
            f"# Plan Red-Team: x — pass {i}\n\n## Verdict: {v}\n\n## Strengths\n- ok\n")
    return pd


def _stub_audit_status(monkeypatch, status):
    monkeypatch.setattr(pm, "_audit_plan",
                        lambda _pd: {"status": status, "findings": [],
                                     "report": "", "grandfathered": False})


def test_latest_review_verdict_picks_highest_pass(tmp_path):
    # An earlier APPROVE followed by a later REVISE → last verdict is REVISE.
    pd = _mk_review_plan(tmp_path, ["APPROVE", "REVISE"])
    # Third element is the pass file itself (REQ-PLAN-072).
    n, verdict, path = pm._latest_review_verdict(pd)
    assert (n, verdict) == (2, "REVISE")
    assert path is not None and path.name == "pass-2.md"


def test_latest_review_verdict_none_when_absent(tmp_path):
    pd = tmp_path / "p"
    pd.mkdir()
    assert pm._latest_review_verdict(pd) == (None, None, None)


def test_ready_check_not_ready_on_last_verdict_revise(tmp_path, monkeypatch):
    from click.testing import CliRunner
    pd = _mk_review_plan(tmp_path, ["APPROVE", "REVISE"])   # last = REVISE
    _stub_audit_status(monkeypatch, "pass")
    result = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert result.exit_code == 3
    payload = json.loads(result.output)
    assert payload["ready"] is False
    assert payload["verdict"] == "REVISE"
    assert any("REVISE" in r for r in payload["reasons"])


def test_ready_check_not_ready_on_audit_fail(tmp_path, monkeypatch):
    from click.testing import CliRunner
    pd = _mk_review_plan(tmp_path, ["APPROVE"])            # verdict green
    _stub_audit_status(monkeypatch, "fail")               # audit red
    result = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert result.exit_code == 3
    payload = json.loads(result.output)
    assert payload["ready"] is False
    assert any("audit" in r.lower() for r in payload["reasons"])


def test_ready_check_not_ready_when_no_review(tmp_path, monkeypatch):
    from click.testing import CliRunner
    pd = tmp_path / "plan"
    pd.mkdir()
    (pd / "plan.md").write_text("# Plan: x\n\n## Objective\nx\n")
    _stub_audit_status(monkeypatch, "pass")
    result = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert result.exit_code == 3
    assert json.loads(result.output)["ready"] is False


def test_ready_check_ready_when_both_green(tmp_path, monkeypatch):
    from click.testing import CliRunner
    # A REVISE re-reviewed to APPROVE (last verdict APPROVE) + audit pass → ready.
    pd = _mk_review_plan(tmp_path, ["REVISE", "APPROVE"])
    _stub_audit_status(monkeypatch, "pass")
    result = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ready"] is True
    assert payload["reasons"] == []
    assert payload["verdict"] == "APPROVE"
    assert payload["audit_status"] == "pass"


# ---------------------------------------------------------------------------
# Parked-plan classifier + approved-phase commit subject (#86, plan-028 Issue 2.6)
# ---------------------------------------------------------------------------

def _fp(stored, current):
    return {"stored_fingerprint": stored, "current_fingerprint": current,
            "stale_approved": bool(stored) and stored != current}


def test_is_parked_approved_fresh_fingerprint():
    # approved + stored present and fresh (stored == current) → parked.
    assert pm._is_parked("approved", _fp("abc", "abc")) is True


def test_is_parked_stale_approved_not_parked():
    # approved + stale (stored != current) → NOT parked; the stale tag owns it.
    assert pm._is_parked("approved", _fp("abc", "xyz")) is False


def test_is_parked_approved_no_fingerprint_not_parked():
    # approved but no stored fingerprint → NOT parked (would get a contradictory nudge).
    assert pm._is_parked("approved", _fp(None, "abc")) is False
    assert pm._is_parked("approved", _fp("", "abc")) is False


def test_is_parked_executing_not_parked():
    assert pm._is_parked("executing", _fp("abc", "abc")) is False


def test_is_parked_complete_not_parked():
    assert pm._is_parked("complete", _fp("abc", "abc")) is False


def _mk_intake_plan(root: Path, status: str, objective: str = "My objective") -> Path:
    pd = root / "plan-999-tester-abc123"
    pd.mkdir(parents=True)
    (pd / "plan.md").write_text(
        f"# Plan: {objective}\n\n**Status:** {status}\n\n## Objective\n{objective}\n")
    return pd


def test_commit_subject_approved_signals_state(git_repo):
    # On a plan branch (not default), an approved-phase intake commit uses the
    # state-signalling subject; the objective moves to the body (#86, REQ-PLAN-064).
    _git(["checkout", "-b", "plan-999-tester-abc123-execute"], git_repo)
    pd = _mk_intake_plan(git_repo, "approved")
    result = pm._commit_plan(pd)
    assert result["status"] == "committed", result
    subject = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"], cwd=git_repo,
        capture_output=True, text=True, check=True).stdout.strip()
    body = subprocess.run(
        ["git", "log", "-1", "--pretty=%b"], cwd=git_repo,
        capture_output=True, text=True, check=True).stdout.strip()
    assert subject == "plan-999-tester-abc123: INTAKE approved (awaiting /yf-plan execute)"
    assert "shipped" not in subject.lower()
    assert body == "My objective"


def test_commit_subject_non_approved_phase_plain(git_repo):
    # A non-approved phase keeps the plain `plan-NNN: <phase> — <objective>` subject.
    _git(["checkout", "-b", "plan-999-tester-abc123-execute"], git_repo)
    pd = _mk_intake_plan(git_repo, "drafting")
    result = pm._commit_plan(pd)
    assert result["status"] == "committed", result
    subject = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"], cwd=git_repo,
        capture_output=True, text=True, check=True).stdout.strip()
    assert subject == "plan-999-tester-abc123: drafting — My objective"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

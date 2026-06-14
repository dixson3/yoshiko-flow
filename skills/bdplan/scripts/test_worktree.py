# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
# ]
# ///
"""Unit tests for the plan_manager.py worktree verb cluster (plan-009 Issue 1.4).

Run from anywhere:  uv run skills/bdplan/scripts/test_worktree.py

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
    assert not pm._branch_exists(PLAN_ID, git_repo)


# ---------------------------------------------------------------------------
# Create / reattach / teardown mechanics
# ---------------------------------------------------------------------------

def test_create_then_reattach_idempotency(git_repo):
    first = pm._worktree_ensure(PLAN_DIR)
    assert first["viable"] is True
    assert first["action"] == "created"
    assert first["branch"] == PLAN_ID            # branch name == plan id (INV-1)
    assert first["gitignore_updated"] is True
    assert (git_repo / ".worktrees" / PLAN_ID).is_dir()

    second = pm._worktree_ensure(PLAN_DIR)
    assert second["viable"] is True
    assert second["action"] == "reattached-worktree"   # never a second worktree
    assert second["gitignore_updated"] is False


def test_reattach_existing_branch_without_worktree(git_repo):
    # Branch exists but no worktree registered -> add WITHOUT -b (re-attach).
    pm._run_git(["branch", PLAN_ID], cwd=git_repo)
    result = pm._worktree_ensure(PLAN_DIR)
    assert result["viable"] is True
    assert result["action"] == "reattached-branch"


def test_teardown_clean(git_repo):
    pm._worktree_ensure(PLAN_DIR)
    result = pm._worktree_teardown(PLAN_DIR, force=False)
    assert result["status"] == "ok"
    assert result["steps"]["branch_delete"]["ok"] is True
    assert not (git_repo / ".worktrees" / PLAN_ID).exists()
    assert not pm._branch_exists(PLAN_ID, git_repo)


def test_teardown_refuse_on_dirty(git_repo):
    pm._worktree_ensure(PLAN_DIR)
    # An untracked file makes `git worktree remove` refuse without --force.
    (git_repo / ".worktrees" / PLAN_ID / "scratch.txt").write_text("wip\n")
    blocked = pm._worktree_teardown(PLAN_DIR, force=False)
    assert blocked["status"] == "blocked"
    assert blocked["steps"]["remove"]["ok"] is False
    # The branch is NOT deleted while the worktree still holds (possibly unmerged) work.
    assert pm._branch_exists(PLAN_ID, git_repo)
    # --force escalates and clears it.
    forced = pm._worktree_teardown(PLAN_DIR, force=True)
    assert forced["status"] == "ok"
    assert not (git_repo / ".worktrees" / PLAN_ID).exists()


# ---------------------------------------------------------------------------
# Landing lock (Issue 3.4 — the contention test named in 1.4)
# ---------------------------------------------------------------------------

@pytest.fixture
def lock_cwd(tmp_path, monkeypatch):
    """A clean cwd so .state/bdplan/landing.lock is created under tmp_path."""
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
    # No .bdplan.local.json -> no validate-cmd -> pass with the cross-plan notice.
    r = pm._validate_merged(Path("docs/plans/plan-x"))
    assert r["status"] == "pass"
    assert r["validate_cmd_configured"] is False
    assert "CROSS-PLAN REGRESSIONS NOT CHECKED" in r["notice"]


def test_validate_merged_runs_configured_cmd(lock_cwd):
    (lock_cwd / ".bdplan.local.json").write_text(json.dumps({"validate-cmd": "true"}))
    passing = pm._validate_merged(Path("docs/plans/plan-x"))
    assert passing["status"] == "pass"
    assert passing["validate_cmd_configured"] is True
    assert passing["notice"] is None
    (lock_cwd / ".bdplan.local.json").write_text(json.dumps({"validate-cmd": "false"}))
    failing = pm._validate_merged(Path("docs/plans/plan-x"))
    assert failing["status"] == "fail"


def test_worktree_opt_out_config(lock_cwd):
    (lock_cwd / ".bdplan.local.json").write_text(json.dumps({"execute.worktree": False}))
    assert pm._worktree_opted_out() is True
    r = pm._worktree_ensure(Path("docs/plans/plan-x"))
    assert r["viable"] is False
    assert r["reason"] == "opted-out"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

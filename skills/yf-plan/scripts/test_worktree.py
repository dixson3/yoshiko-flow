# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

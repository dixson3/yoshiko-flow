# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for the config tiers and configurable roots (plan-037, #100/#107/#101).

Run from anywhere:  uv run skills/yf-plan/scripts/test_config_tiers.py

Covers:
  (a) REQ-YF-PRE-004 precedence — canonical-only, committed-only, legacy-only,
      all-present (highest wins), none (defaults), and the KEY-BY-KEY merge that
      distinguishes this from whole-file first-match;
  (b) import-safety (REQ-PLAN-079) — malformed JSON in any tier, a non-dict
      top-level, and an unreadable tier must degrade to defaults, never raise;
  (c) REQ-PLAN-079 root configurability — `plans-root` / `incubator-root` observed
      end-to-end through a real `init`, including a non-default root;
  (d) #100 state migration — pre-existing `.yf/yf-plan/` state moves to `.yf/plan/`,
      idempotently and without clobbering a canonical file that already exists;
  (e) #101 — change_validation's validate-cmd seed reads the same tiers in the same
      order and reports the tier it used.

Each test drives a real temp repo and re-imports the module with that repo as CWD,
because the roots bind at import time — the exact constraint REQ-PLAN-079 is about.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_CV = _HERE.parent.parent / "yf-change-validation" / "scripts" / "change_validation.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_pm_in(cwd: Path):
    """Import plan_manager.py with `cwd` as the process working directory.

    The config tiers and PLANS_DIR / INCUBATOR_PARENT are CWD-relative and bind at
    import, so a fresh import under a fresh CWD is the only faithful way to test them.
    """
    prev = Path.cwd()
    os.chdir(cwd)
    try:
        return _load(f"pm_{abs(hash(str(cwd)))}", _HERE / "plan_manager.py")
    finally:
        os.chdir(prev)


def _in_cwd(cwd: Path, fn, *args, **kwargs):
    """Call `fn` with `cwd` as the process working directory.

    Needed because `_load_pm_in` restores the CWD after import: the module-level
    constants captured the temp repo, but a *later* call to a CWD-relative reader
    would otherwise resolve against the test runner's directory.
    """
    prev = Path.cwd()
    os.chdir(cwd)
    try:
        return fn(*args, **kwargs)
    finally:
        os.chdir(prev)


LOCAL = ".yf/plan/config.local.json"
SHARED = ".yf/plan/config.json"
LEGACY = ".yf-plan.local.json"


def _write(root: Path, rel: str, payload) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload))


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True)
    return tmp_path


# ---------------------------------------------------------------------------
# (a) REQ-YF-PRE-004 — tier precedence
# ---------------------------------------------------------------------------

def test_no_config_yields_defaults(repo):
    pm = _load_pm_in(repo)
    assert pm.PLANS_DIR == Path("docs/plans")
    assert pm.INCUBATOR_PARENT == Path("Incubator")
    assert pm._bootstrap_config() == {}


def test_canonical_local_only(repo):
    _write(repo, LOCAL, {"plans-root": "L/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("L/plans")


def test_committed_only(repo):
    _write(repo, SHARED, {"plans-root": "S/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("S/plans")


def test_legacy_only_still_read(repo):
    """The legacy root dotfile is a fallback that is never removed."""
    _write(repo, LEGACY, {"plans-root": "G/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("G/plans")


def test_all_three_present_highest_tier_wins(repo):
    _write(repo, LOCAL, {"plans-root": "L/plans"})
    _write(repo, SHARED, {"plans-root": "S/plans"})
    _write(repo, LEGACY, {"plans-root": "G/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("L/plans")


def test_committed_beats_legacy(repo):
    _write(repo, SHARED, {"plans-root": "S/plans"})
    _write(repo, LEGACY, {"plans-root": "G/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("S/plans")


def test_merge_is_key_by_key_not_whole_file(repo):
    """The decisive test for the plan-037 revision.

    Under the OLD whole-file first-match-wins semantics, a local file setting only
    `landing-strategy` would mask the committed `plans-root` entirely and the root
    would fall back to the default. Under merge, each key resolves independently.
    """
    _write(repo, LOCAL, {"landing-strategy": "feature-branch"})
    _write(repo, SHARED, {"plans-root": "S/plans", "incubator-root": "S/inc"})
    _write(repo, LEGACY, {"validate-cmd": "make check"})
    pm = _load_pm_in(repo)
    cfg = _in_cwd(repo, pm._bootstrap_config)
    assert cfg["landing-strategy"] == "feature-branch"   # tier 1
    assert cfg["plans-root"] == "S/plans"                # tier 2, NOT masked
    assert cfg["validate-cmd"] == "make check"           # tier 3
    assert pm.PLANS_DIR == Path("S/plans")
    assert pm.INCUBATOR_PARENT == Path("S/inc")


def test_read_config_matches_bootstrap(repo):
    _write(repo, SHARED, {"landing-strategy": "main"})
    pm = _load_pm_in(repo)
    assert _in_cwd(repo, pm._read_config) == {"landing-strategy": "main"}


def test_read_config_observes_a_config_written_after_import(repo):
    """`_read_config` re-reads; only the roots are frozen at import."""
    pm = _load_pm_in(repo)
    _write(repo, SHARED, {"landing-strategy": "feature-branch"})
    assert _in_cwd(repo, pm._read_config)["landing-strategy"] == "feature-branch"


# ---------------------------------------------------------------------------
# (b) import-safety (REQ-PLAN-079)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier", [LOCAL, SHARED, LEGACY])
def test_malformed_json_in_any_tier_is_tolerated_at_import(repo, tier):
    _write(repo, tier, "{ this is not json ")
    pm = _load_pm_in(repo)          # must not raise
    assert pm.PLANS_DIR == Path("docs/plans")


def test_malformed_tier_does_not_suppress_the_others(repo):
    _write(repo, LOCAL, "}}} broken")
    _write(repo, SHARED, {"plans-root": "S/plans"})
    assert _load_pm_in(repo).PLANS_DIR == Path("S/plans")


@pytest.mark.parametrize("payload", ['"a string"', "[1,2,3]", "null", "42"])
def test_non_dict_top_level_is_ignored(repo, payload):
    _write(repo, SHARED, payload)
    pm = _load_pm_in(repo)
    assert pm.PLANS_DIR == Path("docs/plans")


def test_empty_root_value_falls_back_to_default(repo):
    _write(repo, SHARED, {"plans-root": "", "incubator-root": None})
    pm = _load_pm_in(repo)
    assert pm.PLANS_DIR == Path("docs/plans")
    assert pm.INCUBATOR_PARENT == Path("Incubator")


# ---------------------------------------------------------------------------
# (c) REQ-PLAN-079 — roots end-to-end through `init`
# ---------------------------------------------------------------------------

def _init_plan(repo: Path, objective: str) -> dict:
    from click.testing import CliRunner
    pm = _load_pm_in(repo)
    prev = Path.cwd()
    os.chdir(repo)
    try:
        res = CliRunner().invoke(pm.cli, ["init", objective])
        assert res.exit_code == 0, res.output
        return json.loads(res.output)
    finally:
        os.chdir(prev)


def test_init_uses_default_root_when_unconfigured(repo):
    out = _init_plan(repo, "default roots")
    assert out["plan_dir"].startswith("docs/plans/")
    assert (repo / out["plan_dir"]).is_dir()


def test_init_uses_non_default_root_from_committed_tier(repo):
    _write(repo, SHARED, {"plans-root": "Notes/plans"})
    out = _init_plan(repo, "vault-shaped roots")
    assert out["plan_dir"].startswith("Notes/plans/")
    pd = repo / out["plan_dir"]
    # Full bundle structure, not just the top dir.
    for sub in ("findings", "diagrams", "assets", "references", "reviews"):
        assert (pd / sub).is_dir(), sub
    assert (pd / "plan.md").is_file()
    assert not (repo / "docs" / "plans").exists()


def test_incubator_root_is_configurable(repo):
    _write(repo, SHARED, {"incubator-root": "Notes/Inc"})
    pm = _load_pm_in(repo)
    assert pm.INCUBATOR_PARENT == Path("Notes/Inc")
    assert pm.resolve_plans_dir("topic") == Path("Notes/Inc/topic/plans")


# ---------------------------------------------------------------------------
# (d) #100 — short-name state dir + migration
# ---------------------------------------------------------------------------

def test_state_dir_is_short_name(repo):
    pm = _load_pm_in(repo)
    assert pm.STATE_DIR == Path(".yf/plan")
    assert pm.LANDING_LOCK == Path(".yf/plan/landing.lock")


def test_legacy_state_is_migrated_to_short_name(repo):
    _write(repo, ".yf/yf-plan/landing.lock", {"plan": "plan-001", "host": "h"})
    pm = _load_pm_in(repo)
    assert (repo / ".yf/plan/landing.lock").is_file()
    assert json.loads((repo / ".yf/plan/landing.lock").read_text())["plan"] == "plan-001"
    assert not (repo / ".yf/yf-plan").exists()
    assert pm.STATE_DIR == Path(".yf/plan")


def test_migration_does_not_clobber_an_existing_canonical_file(repo):
    _write(repo, ".yf/yf-plan/landing.lock", {"plan": "OLD"})
    _write(repo, ".yf/plan/landing.lock", {"plan": "CURRENT"})
    _load_pm_in(repo)
    assert json.loads((repo / ".yf/plan/landing.lock").read_text())["plan"] == "CURRENT"
    assert not (repo / ".yf/yf-plan").exists()


def test_migration_is_idempotent(repo):
    _write(repo, ".yf/yf-plan/landing.lock", {"plan": "plan-001"})
    _load_pm_in(repo)
    _load_pm_in(repo)          # second import: legacy dir already gone
    assert (repo / ".yf/plan/landing.lock").is_file()


# ---------------------------------------------------------------------------
# (e) #101 — the change-validation seed reads the same tiers
# ---------------------------------------------------------------------------

cv = _load("change_validation", _CV)


def test_validate_cmd_seed_tier_order(repo):
    _write(repo, LOCAL, {"validate-cmd": "local-cmd"})
    _write(repo, SHARED, {"validate-cmd": "shared-cmd"})
    _write(repo, LEGACY, {"validate-cmd": "legacy-cmd"})
    got = cv.read_validate_cmd(repo)
    assert got["validate_cmd"] == "local-cmd"
    assert got["source"] == LOCAL


def test_validate_cmd_seed_falls_through_to_committed(repo):
    _write(repo, SHARED, {"validate-cmd": "shared-cmd"})
    _write(repo, LEGACY, {"validate-cmd": "legacy-cmd"})
    got = cv.read_validate_cmd(repo)
    assert got["validate_cmd"] == "shared-cmd"
    assert got["source"] == SHARED


def test_validate_cmd_seed_still_reads_legacy(repo):
    _write(repo, LEGACY, {"validate-cmd": "legacy-cmd"})
    got = cv.read_validate_cmd(repo)
    assert got["validate_cmd"] == "legacy-cmd"
    assert got["source"] == LEGACY


def test_validate_cmd_seed_skips_a_tier_without_the_key(repo):
    """A tier present but silent on validate-cmd must not shadow a lower tier."""
    _write(repo, LOCAL, {"landing-strategy": "main"})
    _write(repo, SHARED, {"validate-cmd": "shared-cmd"})
    assert cv.read_validate_cmd(repo)["validate_cmd"] == "shared-cmd"


def test_validate_cmd_seed_absent_everywhere(repo):
    assert cv.read_validate_cmd(repo) is None


def test_validate_cmd_seed_tolerates_malformed_tier(repo):
    _write(repo, LOCAL, "{{{ broken")
    _write(repo, SHARED, {"validate-cmd": "shared-cmd"})
    assert cv.read_validate_cmd(repo)["validate_cmd"] == "shared-cmd"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml",
# ]
# ///
"""Tier-1 tests for `land --dry-run` — the manifest (plan-060 Epic 1, Issue 1.8).

THROWAWAY GIT REPOS IN `tmp_path`, every external call local, NO NETWORK. The
`test_worktree.py` precedent.

THE `__main__` BELOW IS THE FORWARDING FORM, AND THAT IS NOT A STYLE CHOICE (REQ-CLI-028,
Issue 0.9). The house shim `pytest.main([__file__, "-q"])` **discards `sys.argv`**, so
`uv run <file>.py -k this_matches_nothing` runs ALL tests and exits **0** — every criterion
routed through it asserts only "some test passed" and STAYS GREEN WHEN THE NAMED TEST IS
DELETED. Red-team pass 1 measured 20 of this plan's 31 criteria vacuous for exactly that
reason. `pytest.main([__file__, *sys.argv[1:]])` forwards the selector, and
`scripts/checks/check-pytest-ran.sh` is what the criteria actually invoke.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_PM = _HERE / "plan_manager.py"


def _load():
    spec = importlib.util.spec_from_file_location("plan_manager_under_test", _PM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["plan_manager_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


pm = _load()


# --------------------------------------------------------------------------------------
# Fixtures — throwaway repos, no network
# --------------------------------------------------------------------------------------

def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _init_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", "-b", "main", cwd=root)
    _git("config", "user.email", "t@example.invalid", cwd=root)
    _git("config", "user.name", "T", cwd=root)
    _git("config", "commit.gpgsign", "false", cwd=root)


def _commit(root: Path, msg: str) -> None:
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", msg, cwd=root)


PLAN_ID = "plan-060-test-abc123"


def _seed_plan(root: Path, plan_id: str = PLAN_ID) -> Path:
    pdir = root / "docs" / "plans" / plan_id
    (pdir / "assets").mkdir(parents=True, exist_ok=True)
    (pdir / "plan.md").write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\nid: %s\nstatus: reconciling\n---\n"
        "# Plan: t\n\n**ID:** %s\n**Status:** reconciling\n\n"
        "## Objective\nt\n\n## Motivation\nt\n\n"
        "## Upstream Issues\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        "| #301 | a | include | n | 1.1 |\n"
        "| #293 | b | partial | n | 1.2 |\n"
        "| #255 | c | exclude | n | — |\n\n"
        "## Investigation Findings\nt\n\n## Approach\nt\n\n"
        "## Epics\n### Epic 1: e\n- Issue 1.1: x\n\n"
        "## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n\n"
        "## Risks & Mitigations\n| # | Risk | Severity | Mitigation |\n| :-- | :-- | :-- | :-- |\n\n"
        "## Success Criteria\n| # | Criterion | Verification | Discharged-by |\n"
        "| :-- | :-- | :-- | :-- |\n" % (plan_id, plan_id),
        encoding="utf-8")
    (pdir / "log.md").write_text("# Log\n\n## 2026-08-29\n- scoping: t\n", encoding="utf-8")
    return pdir


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A throwaway repo with `main`, an execute branch, and a seeded plan bundle."""
    root = tmp_path / "repo"
    _init_repo(root)
    _seed_plan(root)
    (root / "skills").mkdir(exist_ok=True)
    (root / "skills" / "keep.txt").write_text("base\n", encoding="utf-8")
    _commit(root, "base")

    _git("checkout", "-q", "-b", f"{PLAN_ID}-execute", cwd=root)
    (root / "skills" / "new.py").write_text("print('landed')\n", encoding="utf-8")
    _commit(root, "work")
    _git("checkout", "-q", "main", cwd=root)

    monkeypatch.chdir(root)
    return root


# --------------------------------------------------------------------------------------
# SC6 — the dry run mutates nothing
# --------------------------------------------------------------------------------------

def test_dry_run_does_not_mutate(repo):
    """SC6 / REQ-LAND-026. `git status --porcelain` is EMPTY after a dry run.

    Deliberately NOT phrased as "writes nothing at all": `merge-tree --write-tree` creates
    an unreferenced ODB tree object, and asserting the stronger claim would assert something
    false. The claim tested is the claim the requirement makes.
    """
    before = _git("status", "--porcelain", cwd=repo).stdout
    head_before = _git("rev-parse", "HEAD", cwd=repo).stdout
    refs_before = _git("for-each-ref", "--format=%(refname) %(objectname)", cwd=repo).stdout

    m = pm._land_manifest(Path("docs/plans") / PLAN_ID)

    assert _git("status", "--porcelain", cwd=repo).stdout == before
    assert _git("rev-parse", "HEAD", cwd=repo).stdout == head_before
    assert _git("for-each-ref", "--format=%(refname) %(objectname)", cwd=repo).stdout == refs_before
    assert m["facts"]["plan"]["plan_id"] == PLAN_ID


# --------------------------------------------------------------------------------------
# SC7 — merge preview reports conflicts + a predicted tree without touching the tree
# --------------------------------------------------------------------------------------

def test_merge_preview_no_mutation(repo):
    """SC7 / Issue 1.2. Clean case: a predicted tree, no conflicts, empty porcelain."""
    before = _git("status", "--porcelain", cwd=repo).stdout
    p = pm._land_merge_preview("main", f"{PLAN_ID}-execute", repo)

    assert p["available"] is True
    assert p["conflicts"] == []
    assert p["predicted_tree"] and len(p["predicted_tree"]) >= 40
    assert "skills/new.py" in p["changed_paths"]
    assert p["touches_skills"] is True
    assert _git("status", "--porcelain", cwd=repo).stdout == before


def test_merge_preview_reports_conflicts(repo):
    """The conflicting case — a preview that PREDICTS rather than performs."""
    (repo / "skills" / "clash.txt").write_text("main side\n", encoding="utf-8")
    _commit(repo, "main edit")
    _git("checkout", "-q", f"{PLAN_ID}-execute", cwd=repo)
    (repo / "skills" / "clash.txt").write_text("branch side\n", encoding="utf-8")
    _commit(repo, "branch edit")
    _git("checkout", "-q", "main", cwd=repo)

    before = _git("status", "--porcelain", cwd=repo).stdout
    p = pm._land_merge_preview("main", f"{PLAN_ID}-execute", repo)

    assert p["conflicts"], "a real conflict must be predicted"
    assert any("clash.txt" in c for c in p["conflicts"])
    # THE POINT: predicted, not performed.
    assert _git("status", "--porcelain", cwd=repo).stdout == before
    assert not (repo / ".git" / "MERGE_HEAD").exists()


# --------------------------------------------------------------------------------------
# SC8 — the digest covers the merge preview and the target tip
# --------------------------------------------------------------------------------------

def test_digest_covers_merge_preview(repo):
    """SC8 / Issue 1.5 / REQ-LAND-018.

    Two assertions, and the SECOND is the load-bearing one:
      (a) the digest is stable across recomputation on an unchanged tree; and
      (b) it CHANGES when the target moves — which is the staleness a digest omitting
          `predicted_tree` and `resolved_target_tip` could not detect.
    """
    pdir = Path("docs/plans") / PLAN_ID
    d1 = pm._land_digest(pm._land_manifest(pdir)["facts"])
    assert d1 == pm._land_digest(pm._land_manifest(pdir)["facts"]), "digest must be stable"

    (repo / "skills" / "other.txt").write_text("another plan landed\n", encoding="utf-8")
    _commit(repo, "target advances")

    d2 = pm._land_digest(pm._land_manifest(pdir)["facts"])
    assert d2 != d1, (
        "the digest MUST change when the merge target moves — otherwise a decision minted "
        "against the old target applies against a tree it never saw")

    facts = pm._land_manifest(pdir)["facts"]
    assert facts["git"]["resolved_target_tip"]
    assert facts["git"]["merge_preview"]["predicted_tree"]
    blob = pm._land_canonical(facts)
    assert facts["git"]["resolved_target_tip"] in blob
    assert facts["git"]["merge_preview"]["predicted_tree"] in blob
    assert "generated_at" not in blob, "generated_at must be OUTSIDE the digested object"


# --------------------------------------------------------------------------------------
# SC9 — a plan-number collision is a halting finding
# --------------------------------------------------------------------------------------

def test_number_collision_halts(repo):
    """SC9 / Issue 1.3 / REQ-LAND-024.

    The fixture reproduces the MEASURED case: two bundles sharing `NNN`, differing only by
    hash suffix. They merge CLEANLY, which is why merge-back is the only detection point —
    so the test asserts BOTH that the merge is clean AND that the collision still halts.
    """
    other = repo / "docs" / "plans" / "plan-060-someone-else-999zzz"
    other.mkdir(parents=True)
    (other / "plan.md").write_text("# other\n", encoding="utf-8")
    _commit(repo, "a second plan-060 bundle lands on main")

    collisions = pm._land_number_collisions(PLAN_ID, "main", repo)
    assert collisions == ["plan-060-someone-else-999zzz"]

    preview = pm._land_merge_preview("main", f"{PLAN_ID}-execute", repo)
    assert preview["conflicts"] == [], (
        "the two bundles MERGE CLEANLY — that is precisely why the collision needs its own "
        "detector rather than being caught by the merge")

    m = pm._land_manifest(Path("docs/plans") / PLAN_ID)
    codes = [h["code"] for h in m["halts"]]
    assert "plan-number-collision" in codes


def test_number_collision_absent_when_unique(repo):
    """The negative direction: a check that cannot report absence cannot report presence."""
    assert pm._land_number_collisions(PLAN_ID, "main", repo) == []
    assert "plan-number-collision" not in [
        h["code"] for h in pm._land_manifest(Path("docs/plans") / PLAN_ID)["halts"]]


# --------------------------------------------------------------------------------------
# SC10 — the changed set is HEAD^1..HEAD
# --------------------------------------------------------------------------------------

def test_changed_set_nonempty(repo):
    """SC10 / Issue 1.4 / REQ-LAND-025 / #303.

    BOTH DIRECTIONS, because the point is a COMPARISON: after a real merge the documented
    `<target>...HEAD` expression is EMPTY while `HEAD^1..HEAD` is not. A test asserting only
    that ours is non-empty would pass against an implementation that had the same bug.
    """
    _git("merge", "--no-ff", "-q", "-m", "merge", f"{PLAN_ID}-execute", cwd=repo)

    documented = _git("diff", "--name-only", "main...HEAD", cwd=repo).stdout.split()
    assert documented == [], (
        "the DOCUMENTED expression is empty by construction once HEAD == the target — this "
        "is #303 reproduced in a fixture")

    ours = pm._land_changed_set(repo)
    assert "skills/new.py" in ours
    assert ours, "HEAD^1..HEAD must be non-empty where the documented expression is empty"


def test_changed_set_total_on_non_merge_head(repo):
    """Totality: a non-merge HEAD returns that commit's own diff rather than raising."""
    out = pm._land_changed_set(repo)
    assert isinstance(out, list)


# --------------------------------------------------------------------------------------
# SC10b — enumeration uses git plumbing, and gets the hard fixture exactly right
# --------------------------------------------------------------------------------------

def test_enumeration_uses_git_plumbing(repo, monkeypatch):
    """SC10b / Issue 1.9.

    THE FIXTURE CARRIES ALL FOUR STATES INSIDE A LINKED WORKTREE, and every element defeats
    a specific wrong implementation:

      * a TRACKED draft      defeats `--others`-only
      * an UNTRACKED draft   defeats `ls-files`-only
      * a SYMLINKED draft    defeats `find -type f`
      * an ignored .DS_Store defeats `find ! -type d` used without filtering

    AND THE ENUMERATING PROCESS'S CWD IS PINNED TO THE PRIMARY CHECKOUT. Without that pin a
    test author can enumerate with `git -C <worktree>` and make the word "gitignored"
    vacuous — which is how this blindness survived three review rounds.
    """
    wt = repo / ".worktrees" / PLAN_ID
    (repo / ".gitignore").write_text(".worktrees/\n.DS_Store\n", encoding="utf-8")
    _commit(repo, "ignore worktrees")
    r = _git("worktree", "add", "-q", str(wt), f"{PLAN_ID}-execute", cwd=repo)
    assert r.returncode == 0, r.stderr

    drafts = wt / "docs" / "plans" / PLAN_ID / "assets" / "upstream-drafts"
    drafts.mkdir(parents=True)
    (drafts / "301.md").write_text("tracked draft\n", encoding="utf-8")
    _git("add", "-A", cwd=wt)
    _git("-c", "user.email=t@example.invalid", "-c", "user.name=T",
         "commit", "-q", "-m", "tracked draft", cwd=wt)
    (drafts / "293.md").write_text("untracked draft\n", encoding="utf-8")
    (drafts / "real.md").write_text("symlink target\n", encoding="utf-8")
    os.symlink("real.md", drafts / "304.md")
    (drafts / ".DS_Store").write_bytes(b"\x00junk")

    # THE PIN. cwd is the PRIMARY checkout, not the worktree.
    monkeypatch.chdir(repo)
    assert Path.cwd() == repo.resolve() or Path.cwd() == repo

    names = {Path(p).name for p in pm._land_enumerate(drafts, checkout_root=wt)}

    assert "301.md" in names, "the TRACKED draft was dropped — `--others`-only blindness"
    assert "293.md" in names, "the UNTRACKED draft was dropped — `ls-files`-only blindness"
    assert "304.md" in names, "the SYMLINKED draft was dropped — `find -type f` blindness"
    assert ".DS_Store" not in names, "ignored junk was counted as a draft"


def test_enumeration_path_contains_no_recursive_grep():
    """SC10b's absence half. No `grep -r`/`grep -R` anywhere in the enumeration path.

    Read from the SOURCE TEXT rather than by running a recursive search, because a recursive
    search is the very thing being forbidden — and measured, `grep -r` across both roots
    DOUBLE-COUNTS while the harness wrapper UNDER-reports across `.gitignore`.
    """
    src = _PM.read_text(encoding="utf-8")
    start = src.index("def _land_enumerate(")
    end = src.index("\ndef ", start + 10)
    body = src[start:end]
    code = "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("#"))
    # The docstring names the forbidden forms in prose; strip it before asserting.
    q = code.find('"""')
    if q != -1:
        q2 = code.find('"""', q + 3)
        code = code[:q] + code[q2 + 3:]
    for forbidden in ("grep -r", "grep -R", '"grep"', "--porcelain=v2"):
        assert forbidden not in code, f"enumeration path uses {forbidden!r}"
    assert "ls-files" in code and "--others" in code and "--cached" in code, (
        "the union of --cached and --others IS the prescription; neither alone is a "
        "presence fact")


# --------------------------------------------------------------------------------------
# SC11 — the printed --apply command is fully qualified
# --------------------------------------------------------------------------------------

def test_apply_command_is_fully_qualified(repo):
    """SC11 / Issue 1.7 / REQ-LAND-010.

    It must name the checkout, and that checkout must be the PRIMARY one even when the
    command is generated from inside a linked worktree — L2 checks out the merge target, and
    a linked worktree cannot check out a branch another worktree holds.
    """
    pdir = Path("docs/plans") / PLAN_ID
    cmd = pm._land_apply_command(pdir)
    assert cmd.startswith("cd "), "the command must name the checkout it runs from"
    assert " && " in cmd
    assert "plan_manager.py land" in cmd and "--apply" in cmd
    assert pdir.as_posix() in cmd
    assert str(repo) in cmd or str(repo.resolve()) in cmd

    wt = repo / ".worktrees" / PLAN_ID
    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    _commit(repo, "ignore worktrees")
    assert _git("worktree", "add", "-q", str(wt), f"{PLAN_ID}-execute", cwd=repo).returncode == 0

    cwd = os.getcwd()
    try:
        os.chdir(wt)
        from_wt = pm._land_apply_command(pdir)
    finally:
        os.chdir(cwd)

    assert str(wt) not in from_wt, (
        "generated from inside the worktree, the command named the WORKTREE — the operator "
        "would be handed a command that cannot check out the merge target")
    assert str(repo) in from_wt or str(repo.resolve()) in from_wt


# --------------------------------------------------------------------------------------
# The envelope / exit contract (REQ-CLI-030)
# --------------------------------------------------------------------------------------

def test_envelope_is_three_valued_and_never_coerces():
    """`inconclusive` is a distinct third value and cannot be smuggled in as `fail`."""
    for v in ("pass", "fail", "inconclusive"):
        env = pm._land_envelope(v, "r")
        assert env["verdict"] == v
        assert env["passed"] is (v == "pass")
    with pytest.raises(ValueError):
        pm._land_envelope("FAIL", "r")
    with pytest.raises(ValueError):
        pm._land_envelope("error", "r")
    assert pm._land_exit_code("pass") == 0
    assert pm._land_exit_code("fail") == 1
    assert pm._land_exit_code("inconclusive") == 2


def test_halt_class_is_present_only_on_a_halt():
    assert "halt_class" not in pm._land_envelope("pass", "r")
    assert pm._land_envelope("fail", "r", halt_class=5)["halt_class"] == 5


def test_step_and_journal_sets_are_the_declared_ones():
    """The two closed sets, asserted here so a silent edit to either is caught."""
    assert len(pm.LAND_STEPS) == 20
    assert pm.LAND_STEPS[0] == "l0_lock_acquire"
    assert pm.LAND_STEPS[-1] == "l19_redeploy"
    assert pm.LAND_NON_SKIPPABLE <= set(pm.LAND_STEPS)
    assert "l16_commit_and_push_two" in pm.LAND_NON_SKIPPABLE, (
        "skipping L16 reproduces D-2's residue exactly")
    assert len(pm.LAND_JOURNAL_STATES) == 17
    assert pm.LAND_TERMINAL_STATE == "L_DONE"
    conflict = [s for s in pm.LAND_JOURNAL_STATES if "CONFLICT" in s or "REJECTED" in s]
    assert len(conflict) == 4, "one journal state per conflict site, and there are four"


# --------------------------------------------------------------------------------------
# SC5 — the cited-figure instrument agrees with the repository
# --------------------------------------------------------------------------------------

def test_cited_figures_match_repository():
    """SC5 / Issue 0.10 / #289.

    Runs the real instrument against this bundle's registry. INCONCLUSIVE (exit 2) is
    reported as a SKIP rather than a failure — the instrument could not run is a different
    fact from a figure that drifted, and collapsing them is the defect #263 catalogues.
    """
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if not root:
        pytest.skip("not in a git repository")
    root = Path(root)
    checker = root / "scripts" / "checks" / "check-cited-figures.py"

    # THE REGISTRY IS A PLAN-FOLDER ARTIFACT AND THE CHECKER IS CODE, so before the landing
    # merges them they live in DIFFERENT CHECKOUTS. Resolving only against `--show-toplevel`
    # would SKIP here — and a skip is not a pass (`check-pytest-ran.sh` exits 1 on one), so
    # the criterion would be red for a reason that has nothing to do with the figures. Look
    # in the primary checkout too, which `--git-common-dir` names from either address space.
    rel = Path("docs/plans/plan-060-james-dixson-6a6ac9/assets/cited-figures.md")
    candidates = [root / rel]
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, text=True).stdout.strip()
    if common and Path(common).name == ".git":
        candidates.append(Path(common).parent / rel)
    registry = next((c for c in candidates if c.is_file()), None)
    if not checker.is_file() or registry is None:
        pytest.skip("instrument or registry not present in this tree")

    proc = subprocess.run(["uv", "run", str(checker), str(registry), "--min-figures", "6"],
                          capture_output=True, text=True, cwd=root)
    if proc.returncode == 2:
        pytest.skip(f"INCONCLUSIVE, not a drift: {proc.stderr.strip()}")
    assert proc.returncode == 0, (
        f"a cited figure has DRIFTED from the repository:\n{proc.stderr}\n{proc.stdout}")


if __name__ == "__main__":
    # THE FORWARDING FORM (REQ-CLI-028). `pytest.main([__file__, "-q"])` discards sys.argv,
    # so a `-k` selector never reaches pytest and the criterion asserts only "some test
    # passed" — staying green when the named test is deleted.
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

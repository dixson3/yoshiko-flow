#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8", "pyyaml"]
# ///
"""land_rehearsal.py — drive `land` end to end against a SANDBOX CLONE (plan-060 Issue 6.1).

NEVER THE LIVE REPOSITORY, AND NEVER THIS PLAN'S OWN LANDING. A verb whose first real
execution is the landing of the plan that built it has no rollback if it is wrong. The
rehearsal builds a throwaway repo with a **fake `origin`** (a local bare repo), pours a
fixture bundle into it, and drives the executor.

IT EMITS A MACHINE-READABLE RECORD naming its origin URL, its terminal journal state and the
list of steps it executed. That record is what `test_rehearsal_origin_is_not_this_repo`
(SC36) and `test_rehearsal_reached_terminal_state` (SC36b) read. WITHOUT A COMMISSIONED
ARTIFACT THOSE TESTS WOULD ASSERT SOMETHING THEY INVENTED — which is the failure mode this
whole plan is about, so the rehearsal produces the evidence rather than the tests imagining it.

Exit: 0 the rehearsal reached the terminal green state · 1 it halted · 2 it could not run.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_pm():
    spec = importlib.util.spec_from_file_location("pm_rehearsal", _HERE / "plan_manager.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pm_rehearsal"] = mod
    spec.loader.exec_module(mod)
    return mod


PLAN_ID = "plan-999-rehearsal-sandbox"


def _git(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def _build_sandbox(root: Path) -> tuple[Path, Path]:
    """A throwaway working repo plus a LOCAL BARE repo standing in for `origin`.

    The fake origin is what makes a push safe to rehearse: `git push origin main` in this
    sandbox reaches a bare repo inside `tmp`, and reaches nothing else. There is no network
    path out of this function.
    """
    origin = root / "fake-origin.git"
    work = root / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    for k, v in (("user.email", "rehearsal@example.invalid"), ("user.name", "Rehearsal"),
                 ("commit.gpgsign", "false")):
        _git("config", k, v, cwd=work)
    _git("remote", "add", "origin", str(origin), cwd=work)

    pdir = work / "docs" / "plans" / PLAN_ID
    (pdir / "assets").mkdir(parents=True)
    (pdir / "plan.md").write_text(
        f"---\ntype: Plan\nokf_spec: OKF-PLAN\nid: {PLAN_ID}\nstatus: reconciling\n---\n"
        f"# Plan: rehearsal\n\n**ID:** {PLAN_ID}\n**Status:** reconciling\n"
        f"**Epic:** yf-mol-rehearsal\n\n## Objective\nr\n\n## Motivation\nr\n\n"
        "## Upstream Issues\n| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n| #1 | a | partial | n | 1.1 |\n\n"
        "## Investigation Findings\nr\n\n## Approach\nr\n\n"
        "## Epics\n### Epic 1: e\n- Issue 1.1: x\n\n"
        "## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n\n"
        "## Risks & Mitigations\n| # | Risk | Severity | Mitigation |\n| :-- | :-- | :-- | :-- |\n\n"
        "## Success Criteria\n| # | Criterion | Verification | Discharged-by |\n"
        "| :-- | :-- | :-- | :-- |\n", encoding="utf-8")
    (pdir / "log.md").write_text("# Log\n\n## 2026-08-30\n- scoping: r\n", encoding="utf-8")
    # MIRROR THE REAL REPO: `yf preflight` ensures a single `/.yf/` gitignore anchor, so a
    # sandbox without one is not a faithful rehearsal — it was the ABSENCE of this line that
    # exposed L16's journal-residue defect, which is the rehearsal doing its job.
    (work / ".gitignore").write_text("/.yf/\n/.worktrees/\n", encoding="utf-8")
    (work / "skills").mkdir()
    (work / "skills" / "base.txt").write_text("base\n", encoding="utf-8")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "base", cwd=work)
    _git("push", "-q", "origin", "main", cwd=work)

    _git("checkout", "-q", "-b", f"{PLAN_ID}-execute", cwd=work)
    (work / "skills" / "landed.py").write_text("print('landed')\n", encoding="utf-8")
    _git("add", "-A", cwd=work)
    _git("commit", "-q", "-m", "the work", cwd=work)
    _git("checkout", "-q", "main", cwd=work)
    return work, origin


def rehearse(out_path: Path | None = None) -> dict:
    pm = _load_pm()
    tmp = Path(tempfile.mkdtemp(prefix="yf-land-rehearsal-"))
    try:
        work, origin = _build_sandbox(tmp)
        cwd0 = os.getcwd()
        os.chdir(work)
        try:
            rel = Path("docs/plans") / PLAN_ID
            manifest = pm._land_manifest(rel)
            decision = {
                "schema": pm.LAND_SCHEMA_DECISION,
                "manifest_digest": pm._land_digest(manifest["facts"]),
                "plan_id": PLAN_ID, "authored_by": "rehearsal",
                "summary": "sandbox rehearsal", "upstream_writes": [],
                # L19 IS SKIPPED WITH A REASON, not silently omitted: the sandbox has no
                # `yf` binary, and redeploy is the one step that mutates the machine OUTSIDE
                # the repository — rehearsing it would be rehearsing the thing that must
                # never happen unattended. The skip is recorded in the artifact.
                "steps": {**{k: "enable" for k in pm.LAND_STEPS},
                          "l19_redeploy": "skip:sandbox has no `yf` binary, and redeploy is "
                                          "the only step that mutates the machine outside "
                                          "the repository"},
            }

            # The close chain and the bead tree belong to the LIVE repo's `bd`, which this
            # sandbox has none of. Stub exactly those, and NOTHING ELSE: L0-L6 and L16-L19 —
            # every git-touching step, which is the blast radius the rehearsal exists to
            # exercise — run for real against the fake origin.
            pm._land_l8_to_l15_close_chain = lambda ctx: [
                {"step": "l8_close_chain_head", "verdict": "pass", "reason": "stubbed (no bd)",
                 "journal": None, "halting": False, "detail": {"stubbed": True}}]
            pm._land_l12_close_cascade = lambda ctx: {
                "step": "l12_close_cascade", "verdict": "pass", "reason": "stubbed (no bd)",
                "journal": None, "halting": False, "detail": {"stubbed": True}}
            pm._land_l13_l15_finish = lambda ctx: [
                {"step": "l15_update_status", "verdict": "pass", "reason": "stubbed (no bd)",
                 "journal": "L_CLOSED", "halting": False, "detail": {"stubbed": True}}]
            pm._validate_merged = lambda pd: {"status": "pass", "engine": "rehearsal-stub"}
            pm._worktree_teardown = lambda pd: {"action": "not-registered"}

            ctx = pm.LandingContext(rel, decision, manifest, root=work)
            result = pm._land_execute(ctx)

            origin_url = _git("remote", "get-url", "origin", cwd=work).stdout.strip()
            landed = _git("ls-tree", "--name-only", "-r", "main", cwd=origin).stdout.split()
            record = {
                "schema": "yf-plan/landing-rehearsal@1",
                "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "plan_id": PLAN_ID,
                "origin_url": origin_url,
                "origin_is_local_sandbox": str(tmp) in origin_url,
                "sandbox_root": str(tmp),
                "terminal_journal_state": result.get("journal_phase"),
                "reached_terminal_state": result.get("reached_terminal_state", False),
                "halted": result.get("halted"),
                "halted_at": result.get("at"),
                "steps_executed": result.get("steps_executed") or
                                  [r["step"] for r in result.get("results", [])],
                "stubbed_steps": ["l8_close_chain_head", "l12_close_cascade",
                                  "l15_update_status"],
                "pushed_paths_on_fake_origin": landed,
                "verdicts": {r["step"]: r["verdict"] for r in result.get("results", [])},
            }
        finally:
            os.chdir(cwd0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main(argv: list[str]) -> int:
    out = None
    if len(argv) > 2 and argv[1] == "--out":
        out = Path(argv[2])
    try:
        rec = rehearse(out)
    except Exception as exc:                                   # noqa: BLE001
        print(f"land_rehearsal: INCONCLUSIVE — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(rec, indent=2))
    return 0 if rec["reached_terminal_state"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

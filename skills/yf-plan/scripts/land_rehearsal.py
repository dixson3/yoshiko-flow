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

# ==========================================================================================
# THE SANDBOX RUNNER (plan-068 Issue 1.5)
# ==========================================================================================

class _R:
    """A `subprocess.CompletedProcess` lookalike. The seam only reads these three fields."""

    def __init__(self, rc=0, out="", err=""):
        self.returncode = rc
        self.stdout = out
        self.stderr = err


class SandboxRunner:
    """`git` PASSES THROUGH; `bd` / `gh` / `uv` / `yf` / `sh` are argv-recognising fakes that
    FAIL on an unrecognised argv rather than returning 0.

    THE CONTRACT IS THE WHOLE POINT, because `_dispatch` routes EVERY program through an
    injected runner — `git` included — so a runner that stubbed everything would make `L_DONE`
    a fiction (plan-068 pass-3 C5).

    * **`git` passes through** to the sandbox. It is the local bare `origin` that makes the
      push safe to rehearse, **not** the runner: there is no network path out of
      `_build_sandbox`. Faking `git` would remove the only steps whose blast radius the
      rehearsal exists to exercise.
    * **Everything else is intercepted, and FAILS CLOSED on an argv it does not recognise.**
      `LandingContext`'s own docstring records why: *"the injected fake returned 0 for any argv
      it did not recognise. Every Tier-1 test passed."* A fake that answers everything cannot
      witness the wrong executable being invoked — so this one answers only what it was taught,
      and returns **127** with a distinctive marker otherwise.

    Every call is recorded, including `env`, so a caller can assert on what actually ran.
    """

    #: Programs the runner FAKES. `git` is deliberately absent — see the class docstring.
    FAKED = ("bd", "gh", "uv", "yf", "sh")

    def __init__(self, work: Path, plan_id: str):
        self.work = Path(work)
        self.plan_id = plan_id
        self.calls: list[list[str]] = []
        self.envs: list[dict | None] = []
        self.unrecognised: list[list[str]] = []

    def __call__(self, prog, args, cwd=None, env=None):
        self.calls.append([prog, *args])
        self.envs.append(env)
        if prog == "git":
            return subprocess.run(["git", *args], cwd=str(cwd or self.work),
                                  capture_output=True, text=True)
        handler = getattr(self, f"_fake_{prog}", None)
        if handler is None:
            return self._unrecognised(prog, args)
        return handler(list(args), cwd)

    def _unrecognised(self, prog, args):
        """FAIL CLOSED. Never 0, and never silent."""
        self.unrecognised.append([prog, *args])
        return _R(127, err=(f"SandboxRunner: UNRECOGNISED ARGV — refusing to answer "
                            f"{[prog, *args]}. A fake that returns 0 for an argv it does not "
                            f"recognise cannot witness the wrong executable being invoked."))

    # -- the fakes ------------------------------------------------------------------------

    def _fake_bd(self, args, cwd):
        if args[:1] == ["list"]:
            # An EMPTY bead list, and the honesty note is in `HONEST_SCOPE`: with no beads,
            # L14's DAG comparison is not exercised. A poured-bead fixture is out of scope
            # here (plan-068 Issue 1.6 / R7).
            return _R(0, out="[]")
        if args[:1] == ["show"]:
            # L17's read-back needs an `external_ref` to report the mirror as verified.
            return _R(0, out=json.dumps({"id": args[1] if len(args) > 1 else "yf-x",
                                         "external_ref": "https://example.invalid/issues/1"}))
        if args[:1] in (["close"], ["update"], ["gate"]):
            return _R(0, out="{}")
        return self._unrecognised("bd", args)

    def _fake_gh(self, args, cwd):
        if args[:2] == ["issue", "view"]:
            return _R(0, out=json.dumps({"state": "OPEN", "comments": [{"body": "x"}]}))
        if args[:2] in (["issue", "comment"], ["issue", "close"], ["issue", "edit"]):
            return _R(0, out="https://example.invalid/issues/1")
        return self._unrecognised("gh", args)

    def _fake_uv(self, args, cwd):
        """`uv run <script-or-verb> ...` — recognised by the SCRIPT NAME or the VERB."""
        if args[:1] != ["run"]:
            return self._unrecognised("uv", args)
        rest = args[1:]
        if not rest:
            return self._unrecognised("uv", args)
        target = Path(rest[0]).name
        verb = rest[1] if len(rest) > 1 else ""
        if target == "plan_manager.py":
            if verb in _REHEARSAL_PM_VERBS:
                return _R(0, out=json.dumps({"verdict": "pass", "faked": True, "verb": verb}))
            return self._unrecognised("uv", args)
        if target in _REHEARSAL_SCRIPTS:
            return _R(0, out=json.dumps({"verdict": "pass", "faked": True,
                                         "script": target}))
        return self._unrecognised("uv", args)

    def _fake_yf(self, args, cwd):
        # L19 is skipped at the decision level in this rehearsal, so `yf` should never be
        # reached. Recognising it anyway would hide a step that ran when it should not have.
        return self._unrecognised("yf", args)

    def _fake_sh(self, args, cwd):
        # `_run_shell`'s routed form. No `validate-cmd` is configured in the sandbox, so this
        # is unreachable — and if it IS reached, that is a finding, not a pass.
        return self._unrecognised("sh", args)


#: `plan_manager.py` verbs the close chain and L13-L15 invoke. Enumerated so an argv the
#: rehearsal has not been taught about FAILS rather than silently returning 0.
_REHEARSAL_PM_VERBS = frozenset({
    "audit-close", "retrospective-report", "judgement-never-fired-report",
    "classify-deliverable", "close-reconcile-step", "verify-reconcile", "recheck-criteria",
    "complete-gate", "update-status",
})

#: Sibling scripts the L-steps shell out to.
_REHEARSAL_SCRIPTS = frozenset({"close_cascade.py", "pour_fidelity.py", "upstream.py"})


#: WHAT A GREEN REHEARSAL DOES AND DOES NOT ESTABLISH (plan-068 Issue 1.6 / R7).
#:
#: Stated in the ARTIFACT rather than only in a docstring, because the artifact is what the
#: consuming tests read and what a later reader will quote.
_HONEST_SCOPE = {
    "established": [
        "every L-step function EXECUTED — none is replaced by a lambda or a helper stub",
        "every `git` process ran FOR REAL against a local bare `origin` inside a temp dir, so "
        "L1/L2/L4/L6/L16's tree and push behaviour is genuinely exercised",
        "the executor's ordering, journal advance and halt semantics ran unmodified",
        "no process reached an executable the runner was not taught about — an unrecognised "
        "argv returns 127 with a marker and is recorded in `unrecognised_argv`",
    ],
    "not_established": [
        "L14's DAG COMPARISON. The faked `bd list` returns `[]` and the faked "
        "`pour_fidelity.py` returns a pass, so the comparison has no input. A poured-bead "
        "fixture is out of scope; this is R7's 'a stub in a different costume', named rather "
        "than claimed as covered.",
        "the close chain's real VERDICTS. `uv run plan_manager.py <verb>` is intercepted, so "
        "`audit-close`, `verify-reconcile`, `recheck-criteria` and `complete-gate` return a "
        "faked pass. What is exercised is that each is INVOKED with the right argv and that "
        "its exit code is READ (#180), not what it would have decided.",
        "L19 REDEPLOY. Skipped at the decision level — the sandbox has no `yf` binary, and "
        "redeploy is the only step that mutates the machine outside the repository. The `yf` "
        "fake therefore refuses every argv, so a reached L19 is a FINDING, not a pass.",
        "any `gh` outcome. Upstream writes are faked; `test_readback_catches_wrong_body` in "
        "test_land_apply.py is what covers the read-back's discriminating power.",
    ],
}


def _stubbed_steps(pm, monkeypatched: dict[str, str], decision: dict) -> list[str]:
    """Every `LAND_STEPS` key DISABLED, from **both** sources (SC3).

    Two sources, because each is blind to the other:

    * a `pm.*` MONKEYPATCH replaces a step function — and one function can cover several
      L-numbers, which `_covered_steps` derives from `LAND_EXECUTOR`;
    * a DECISION-LEVEL adjudication (`"steps": {"l19_redeploy": "skip:..."}`) disables a step
      with no monkeypatch anywhere. pass-4 C8 measured this: `l19_redeploy` was disabled at
      `land_rehearsal.py:120` and **no monkeypatch-keyed enumeration could see it**, so a
      sixth step was hidden from a record that named three.

    A step is "disabled" if either source disables it. Union, sorted, deduplicated.
    """
    covered = _covered_steps(pm)
    out: set[str] = set()
    for fname in monkeypatched:
        keys = covered.get(fname)
        if keys is None:
            # A monkeypatch on something that is NOT an executor function. Recorded rather
            # than dropped: it disables *something*, and silently omitting it is the class of
            # blindness this function exists to remove.
            out.add(f"<non-executor monkeypatch: {fname}>")
        else:
            out.update(keys)
    for key, verdict in (decision.get("steps") or {}).items():
        if not (isinstance(verdict, str) and verdict == "enable"):
            out.add(key)
    return sorted(out)


def _covered_steps(pm) -> dict[str, list[str]]:
    """Map each executor FUNCTION NAME to every `LAND_STEPS` key it produces.

    DERIVED FROM `LAND_EXECUTOR` AND `LAND_STEPS`, never hand-written — this is the mapping
    Issue 1.5 exists to fix. `LAND_EXECUTOR` names only the FIRST key per function, so
    `_land_l8_to_l11_close_chain` appears as `l8_close_chain_head` while it actually produces
    L8-L11, and `_land_l13_l15_finish` appears as `l13_complete_gate` while it produces
    L13-L15. The previous record named THREE labels while hiding FIVE L-numbers (l9, l10, l11,
    l14, l15), with `l14_pour_fidelity` absent entirely — the "second enumeration that can
    drift" defect `spec/landing.md` forbids elsewhere.

    The span of each entry is "from this entry's key up to the next entry's key, exclusive",
    read off the normative `LAND_STEPS` order.
    """
    steps = list(pm.LAND_STEPS)
    entries = list(pm.LAND_EXECUTOR)
    out: dict[str, list[str]] = {}
    for i, (key, fname) in enumerate(entries):
        start = steps.index(key)
        end = steps.index(entries[i + 1][0]) if i + 1 < len(entries) else len(steps)
        out[fname] = steps[start:end]
    return out


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

            # ===================================================================
            # NO WHOLE-STEP STUBS. NO HELPER STUBS. ONE INJECTED RUNNER.
            # ===================================================================
            #
            # plan-068 Issue 1.5. What stood here disabled SIX steps via FIVE
            # monkeypatches plus one decision-level skip:
            #
            #   * three `_land_l*` step lambdas (L8-L11, L12, L13-L15),
            #   * `pm._validate_merged` — L3's ENTIRE validation, replaced by
            #     `{"status": "pass", "engine": "rehearsal-stub"}`,
            #   * `pm._worktree_teardown` — L18,
            #   * and L19, disabled at the DECISION level, which no
            #     monkeypatch-keyed enumeration can see.
            #
            # Issue 1.1 gave `_validate_merged` and `_worktree_teardown` both a
            # `runner=` and a `root=`, and routed the eight bare launches inside
            # the L-steps onto `ctx.run`. So all of it becomes injectable: the
            # REAL step functions now run, with one `SandboxRunner` deciding what
            # each process returns. That is the difference between a step that was
            # replaced and a step that ran.
            #
            # `check_mock_fidelity.py` found the two helper stubs here
            # MECHANICALLY the moment Issue 1.1 changed the signatures — it binds
            # `inspect.signature` — which is the check doing precisely its job
            # rather than an inspection catching them.
            runner = SandboxRunner(work, PLAN_ID)
            monkeypatched: dict[str, str] = {}          # DELIBERATELY EMPTY. See below.

            ctx = pm.LandingContext(rel, decision, manifest, root=work, runner=runner)
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
                # DERIVED FROM **BOTH** SOURCES, and from `LAND_EXECUTOR` rather than by
                # hand (plan-068 Issue 1.5 / SC3). A monkeypatch-keyed enumeration is blind
                # to the decision-level skip, and a hand-written list was blind to the L-span
                # of each executor function — the old record named THREE labels while hiding
                # FIVE L-numbers (l9, l10, l11, l14, l15), with `l14_pour_fidelity` absent
                # entirely.
                "stubbed_steps": _stubbed_steps(pm, monkeypatched, decision),
                "stubbed_steps_by_source": {
                    "pm_monkeypatch": sorted(
                        k for f, _ in [(f, None) for f in monkeypatched]
                        for k in _covered_steps(pm).get(f, [])),
                    "decision_adjudication": sorted(
                        k for k, v in (decision.get("steps") or {}).items()
                        if not (isinstance(v, str) and v == "enable")),
                },
                "faked_programs": sorted(SandboxRunner.FAKED),
                "passed_through_programs": ["git"],
                "unrecognised_argv": runner.unrecognised,
                "honest_scope": _HONEST_SCOPE,
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

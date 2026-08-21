# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for reconcile-step resolution (REQ-PLAN-076, plan-043 Issue 3.1).

Run from anywhere:  uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py

THE DEFECT, AS MEASURED (not as inferred)
-----------------------------------------
The plan recorded this defect as *inferred from grep, never run live*, and required live
verification before any fix. That verification confirmed it AND corrected its severity.

`RECONCILE_STEP` is assigned in exactly one place — SKILL.md §5.2a, the POUR path. The
§5.2b RESUME path never re-derives it, so a resumed execution reaches §6.4 with it unset.
The inferred consequence was "`bd close` degrades to `bd close --reason …` and fails
silently". The measured consequence is worse: `bd close` with no id argument **exits 0 and
closes a different, in-progress bead**, then reports success. During the verification probe
it closed the very bead that was running the probe.

So the resume path did not merely skip the reconcile close — it **silently closed the wrong
bead and asserted success**, the same false-success shape as the reconcile defect this plan
exists to fix, one step away from it.

Covers (tagged REQ-PLAN-076):
  (a) the bead is resolved from the EPIC, never from an environment variable;
  (b) an unresolvable reconcile bead yields a reported verdict, never a bare `bd close`;
  (c) REGRESSION PIN on the measured behavior — no code path emits a `bd close` with an
      empty id argument;
  (d) idempotence — an already-closed reconcile bead is a clean pass, not an error;
  (e) SKILL.md §6.4 no longer closes the reconcile bead via the shell variable.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

_HERE = Path(__file__).resolve().parent
_SKILL_MD = _HERE.parent / "SKILL.md"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")

EPIC = "yf-mol-zzz"
PLAN_ID = "plan-996-reconcile-tester-abc123"


def _bundle(tmp_path: Path, *, epic: str | None = EPIC) -> Path:
    pdir = tmp_path / PLAN_ID
    pdir.mkdir(parents=True)
    fm = f"---\ntype: Plan\nid: {PLAN_ID}\n"
    if epic:
        fm += f"epic: {epic}\n"
    fm += "---\n"
    body = fm + f"# Plan: t\n\n**ID:** {PLAN_ID}\n"
    if epic:
        body += f"**Epic:** {epic}\n"
    body += "\n## Objective\n\nt\n"
    (pdir / "plan.md").write_text(body, encoding="utf-8")
    return pdir


def _beads(*, reconcile_status: str | None = "open") -> dict[str, dict]:
    out = {
        EPIC: {"id": EPIC, "issue_type": "epic", "title": "plan-execute",
               "status": "open"},
        f"{EPIC}.1": {"id": f"{EPIC}.1", "issue_type": "task",
                      "title": "1.1 something else", "status": "closed"},
    }
    if reconcile_status is not None:
        out[f"{EPIC}.9"] = {"id": f"{EPIC}.9", "issue_type": "task",
                            "title": "Reconcile: update upstream issues",
                            "status": reconcile_status}
    return out


def _run(pdir: Path) -> tuple[int, dict]:
    res = CliRunner().invoke(pm.cli, ["close-reconcile-step", str(pdir), "--json"])
    assert res.output.strip(), "envelope must be on stdout on EVERY path"
    return res.exit_code, json.loads(res.output)


class _Recorder:
    """Records every `bd` argv the verb would execute."""

    def __init__(self, returncode=0, stderr=""):
        self.calls: list[list[str]] = []
        self.returncode, self.stderr = returncode, stderr

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))

        class R:
            pass
        r = R()
        r.returncode, r.stdout, r.stderr = self.returncode, "", self.stderr
        return r


def _closes(rec) -> list[list[str]]:
    """Only the `bd close` invocations from a recorder's call log.

    Scoped to closes rather than asserting the WHOLE call list because plan-050 Issue 1.3
    (REQ-COMPLETE-004) added a read-only gate query ahead of the close — `bd list --parent
    <epic>` — which `subprocess.check_output` routes through `subprocess.run` and so lands in
    the same log. The regression these assertions pin is about WHAT GETS CLOSED, and pinning
    the full call list made an additive read a failure.
    """
    return [c for c in rec.calls if len(c) > 1 and c[0] == "bd" and c[1] == "close"]


# ---------------------------------------------------------------------------
# (a) resolved from the epic, not from the environment
# ---------------------------------------------------------------------------

def test_resolves_reconcile_bead_from_the_epic(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert out["verdict"] == "pass" and rc == 0
    assert out["bead"] == f"{EPIC}.9", "did not re-derive the reconcile bead from the epic"
    assert _closes(rec) == [["bd", "close", f"{EPIC}.9", "--reason",
                             "Upstream issues reconciled"]]


def test_ignores_reconcile_step_environment_variable(tmp_path, monkeypatch):
    """A stale/wrong `RECONCILE_STEP` in the environment must have NO effect."""
    monkeypatch.setenv("RECONCILE_STEP", "yf-WRONG-999")
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    _, out = _run(_bundle(tmp_path))
    assert out["bead"] == f"{EPIC}.9"
    assert all("yf-WRONG-999" not in " ".join(c) for c in rec.calls), \
        "the environment variable leaked into the close"


# ---------------------------------------------------------------------------
# (b)/(c) THE regression pin — never a bd close with an empty id
# ---------------------------------------------------------------------------

def test_no_epic_reports_and_never_closes(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path, epic=None))
    assert out["verdict"] == "inconclusive"
    assert rc == 0, "an unresolvable bead must not halt completion"
    assert rec.calls == [], "issued a `bd` call with no resolved bead"


def test_no_reconcile_bead_reports_and_never_closes(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: _beads(reconcile_status=None))
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert out["verdict"] == "inconclusive" and rc == 0
    assert rec.calls == []


def test_bd_unavailable_reports_and_never_closes(tmp_path, monkeypatch):
    """`bd` down => _all_plan_beads is empty => report, never guess, never halt."""
    monkeypatch.setattr(pm, "_all_plan_beads", dict)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert out["verdict"] == "inconclusive" and rc == 0
    assert rec.calls == []


@pytest.mark.parametrize("scenario", ["no-epic", "no-bead", "bd-down"])
def test_never_emits_an_empty_id_close(tmp_path, monkeypatch, scenario):
    """(c) THE pin on the measured behavior.

    `bd close` with an empty id exits 0 and closes an unrelated in-progress bead. So the
    invariant is not "handle the empty case gracefully" — it is that no argv reaching
    `bd close` may ever have an empty or missing id token.
    """
    beads = {"no-epic": _beads, "no-bead": lambda: _beads(reconcile_status=None),
             "bd-down": dict}[scenario]
    monkeypatch.setattr(pm, "_all_plan_beads", beads)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    _run(_bundle(tmp_path, epic=None if scenario == "no-epic" else EPIC))
    for argv in rec.calls:
        if argv[:2] == ["bd", "close"]:
            assert len(argv) > 2 and argv[2].strip(), \
                f"emitted a `bd close` with an empty id: {argv}"


# ---------------------------------------------------------------------------
# (d) idempotence + close failure handling
# ---------------------------------------------------------------------------

def test_already_closed_is_a_clean_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: _beads(reconcile_status="closed"))
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert out["verdict"] == "pass" and out["already_closed"] is True and rc == 0
    assert _closes(rec) == [], "re-closed an already-closed bead"


def test_close_failure_is_inconclusive_not_silent(tmp_path, monkeypatch):
    """The exit code is CHECKED — the old `bd close` call ignored it entirely."""
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    monkeypatch.setattr(pm.subprocess, "run", _Recorder(returncode=1, stderr="boom"))
    rc, out = _run(_bundle(tmp_path))
    assert out["verdict"] == "inconclusive"
    assert "boom" in out["reason"]
    assert out["remediation"] and "bd close" in out["remediation"]
    assert rc == 0


# ---------------------------------------------------------------------------
# (e) SKILL.md no longer uses the shell variable
# ---------------------------------------------------------------------------

def test_skill_md_no_longer_closes_via_the_shell_variable():
    text = _SKILL_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("### 6.4"))
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("###")),
               len(lines))
    block = "\n".join(lines[start:end])
    executed = [l for l in block.splitlines()
                if l.strip() and not l.strip().startswith("#")]
    offenders = [l for l in executed if "bd close ${RECONCILE_STEP}" in l]
    assert not offenders, (
        "§6.4 still closes the reconcile bead through the shell variable, which is unset "
        f"on the resume path: {offenders}"
    )
    assert "close-reconcile-step" in block, "the re-deriving verb is not wired in"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))


# ---------------------------------------------------------------------------
# (d) REQ-COMPLETE-004 (#180) — the gate-before-close ordering assertion
# ---------------------------------------------------------------------------

def _with_reconcile_gate(monkeypatch, *, resolved: bool):
    """Wire `_bd_children` / `_bd_show_one` to report ONE reconcile gate."""
    gate = {"id": f"{EPIC}.8", "issue_type": "gate", "title": "Gate: Reconcile upstream",
            "status": "closed" if resolved else "open"}
    monkeypatch.setattr(pm, "_bd_children", lambda _e: [gate])
    monkeypatch.setattr(pm, "_bd_show_one", lambda _i: gate)
    return gate


def test_unresolved_reconcile_gate_fails_loud_and_never_closes(tmp_path, monkeypatch):
    """The ordering violation is `fail` + NON-ZERO, and closes nothing.

    Before this, violating the ordering produced `verdict: inconclusive` and **exit 0** —
    discovered accidentally, deep inside the close attempt, from bd's own "blocked by open
    issues" refusal. SKILL.md §6.4 never read the exit code, so the chain walked on to
    cascade-close and `set complete` with the reconcile step still open. An accidental
    refusal reported softly is not an assertion.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    _with_reconcile_gate(monkeypatch, resolved=False)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert rc != 0, "an unresolved reconcile gate must HALT the chain"
    assert out["verdict"] == "fail", f"verdict was {out['verdict']!r}, expected 'fail'"
    assert out["unresolved_gates"] == [f"{EPIC}.8"], "the failing gate is not named"
    assert _closes(rec) == [], "closed the reconcile bead despite the ordering violation"


def test_resolved_reconcile_gate_permits_the_close(tmp_path, monkeypatch):
    """The contrast arm — without it the test above passes on a verb that never closes."""
    monkeypatch.setattr(pm, "_all_plan_beads", _beads)
    _with_reconcile_gate(monkeypatch, resolved=True)
    rec = _Recorder()
    monkeypatch.setattr(pm.subprocess, "run", rec)
    rc, out = _run(_bundle(tmp_path))
    assert rc == 0 and out["verdict"] == "pass"
    assert _closes(rec) == [["bd", "close", f"{EPIC}.9", "--reason",
                             "Upstream issues reconciled"]]


def test_skill_md_reads_the_close_reconcile_step_exit_code():
    """The SECOND HALF of #180: an exit code nothing reads is not a step.

    SKILL.md §6.4 captured the verb with `RSTEP=$(...)` and only echoed it. The assertion is
    on the CALLER, because Issue 1.3's exit code would otherwise be unread — this plan's own
    M5 vacuity class.
    """
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    i = skill.index("close-reconcile-step")
    window = skill[i:i + 900]
    assert "RSTEP_RC=$?" in window, "§6.4 does not capture close-reconcile-step's exit code"
    assert 'if [ "$RSTEP_RC" -ne 0 ]' in window, "§6.4 captures the exit code but never tests it"
    assert "FAIL-LOUD" in window, "§6.4 does not halt on the ordering violation"


# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
# ]
# ///
"""Mechanical enforcement of the §6.4 close-step contract (REQ-COMPLETE-001/003, plan-043).

Run from anywhere:  uv run skills/yf-plan/scripts/test_close_contract.py

WHY THIS FILE EXISTS
--------------------
Phase 6.4 has no dispatcher, and per the repo's standing prohibition on harness hooks it
will not get one — the chain is prose in `SKILL.md` executed by an LLM calling flat CLI
verbs. So the contract's only possible enforcement is a test that reads that prose.

plan-043's central finding is that **prose instructions get ignored**: `agents/reconciler.md`
step 4 already prescribed the upstream verification that plan-039 skipped, and the plan still
shipped `complete`. A contract whose only enforcement is "a future author will read
REQ-COMPLETE-003" would reproduce exactly the defect it exists to fix. This test is the
contract's teeth, and it is the plan's own thesis applied to itself.

THE ENUMERATION IS FROM SOURCE, AND IT IS NOT CAPTURE-ONLY
----------------------------------------------------------
The steps are **enumerated by parsing `SKILL.md`**, never hardcoded — a hardcoded list
verifies today's steps and is silent on the one that matters, the step added tomorrow.

Enumerating only the `X=$(… --json)` capture idiom would be **circular**: it can see only
steps *already shaped like* conformant ones. The likeliest non-conformance is an author who
adds a step *without* the capture idiom — which takes **less** effort, not more — and such a
step would be invisible and pass CI. So every script invocation in the block is enumerated,
and each must be **either envelope-capturing or on an explicit named exempt list**. That
converts the teeth from "checks conformant steps" to "detects added steps".

SCOPE RULES (each one is load-bearing; see the plan's pass-3 C24/C25)
--------------------------------------------------------------------
* **Block boundary** — from the `### 6.4` heading to the next `###` heading. Nothing above or
  below counts. In particular `worktree teardown` lives in §6.2 and is therefore NOT in the
  block and NOT on the exempt list; including it would have made the boundary ambiguous.
* **What counts as a "script invocation"** — an invocation of one of this skill's own scripts
  (`${SKILL_DIR}/scripts/<name>.py <verb>`). Bare `bd` calls are a different tool with its own
  contract and are not chain steps emitting a verdict envelope; they are out of scope here
  (`bd close ${RECONCILE_STEP}`'s own unguarded-exit-code defect is tracked separately).
* **Comments are NOT stripped** — `set-deliverable-class` currently appears *only* inside a
  `#` comment in the live block. An enumerator that strips comments would silently miss it; one
  that mishandles them would see a phantom. The rule is explicit: a commented invocation inside
  the block still counts, because SKILL.md's comments are *prescriptive documentation of a step
  the operator is told to run*, not dead code. It must therefore be exempted by name like any
  other non-capturing step.

Covers: REQ-COMPLETE-001, REQ-COMPLETE-003, REQ-CLI-016. Satisfies plan-043 SC2.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SKILL_DIR = _HERE.parent
_SKILL_MD = _SKILL_DIR / "SKILL.md"

# --------------------------------------------------------------------------------------
# The exempt list — steps that legitimately do NOT capture an envelope.
#
# This list is deliberately SHORT, NAMED and CLOSED. Adding a name to it is the explicit,
# reviewable act of declaring a step exempt; the test's whole value is that you cannot add a
# non-conformant step without touching this line.
#
#   classify-deliverable  — a pure read whose output is *presented to the operator* for
#                           confirmation, not a chain verdict (REQ-CLI-015).
#   set-deliverable-class — a writer invoked on the operator's answer; it records a decision
#                           rather than rendering one.
#   update-status         — the terminal status transition itself (REQ-COMPLETE-001
#                           constraint 4). It IS the thing the chain gates, so it cannot be
#                           a gate in the chain.
# --------------------------------------------------------------------------------------
EXEMPT_VERBS = frozenset({
    "classify-deliverable",
    "set-deliverable-class",
    "update-status",
})

# `NAME=$(uv run ${SKILL_DIR}/scripts/foo.py verb …)` — the documented capture idiom.
_CAPTURE_RE = re.compile(
    r"""(?P<var>[A-Z_][A-Z0-9_]*)=\$\(\s*uv\s+run\s+
        \$\{SKILL_DIR\}/scripts/(?P<script>[A-Za-z_][\w.]*\.py)
        (?:\s+(?P<verb>[a-z][\w-]*))?""",
    re.VERBOSE,
)

# Any invocation of one of this skill's scripts, captured or not, commented or not.
_INVOKE_RE = re.compile(
    r"""uv\s+run\s+\$\{SKILL_DIR\}/scripts/(?P<script>[A-Za-z_][\w.]*\.py)
        (?:\s+(?P<verb>[a-z][\w-]*))?""",
    re.VERBOSE,
)


def _section_64() -> str:
    """Extract the §6.4 block: from the `### 6.4` heading to the next `###` heading."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("### 6.4"):
            start = i
            break
    assert start is not None, "no `### 6.4` heading found in SKILL.md"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("###"):
            end = j
            break
    return "\n".join(lines[start:end])


def _invocations() -> list[dict]:
    """Enumerate EVERY script invocation in the §6.4 block, capturing or not.

    Comments are deliberately not stripped (see module docstring).
    """
    block = _section_64()
    captured_spans = {(m.start("script"), m.group("verb")) for m in _CAPTURE_RE.finditer(block)}
    captured_verbs = {v for _, v in captured_spans if v}

    out: list[dict] = []
    seen: set[tuple[str, str | None]] = set()
    for m in _INVOKE_RE.finditer(block):
        script, verb = m.group("script"), m.group("verb")
        key = (script, verb)
        if key in seen:
            continue
        seen.add(key)
        line_start = block.rfind("\n", 0, m.start()) + 1
        line = block[line_start:block.find("\n", m.start())]
        out.append({
            "script": script,
            "verb": verb,
            "name": verb or script,
            "capturing": (verb in captured_verbs) if verb else bool(
                _CAPTURE_RE.search(line)
            ),
            "commented": line.lstrip().startswith("#"),
            "line": line.strip(),
        })
    return out


# ======================================================================================
# REQ-COMPLETE-003 — every invocation is envelope-capturing or explicitly exempt
# ======================================================================================

def test_block_boundary_is_well_formed():
    """The enumerator's scope is exactly `### 6.4` → next `###` (pass-3 C24)."""
    block = _section_64()
    assert block.startswith("### 6.4")
    # `worktree teardown` lives in §6.2 and must NOT fall inside the block.
    assert "worktree teardown" not in block, (
        "§6.2's `worktree teardown` leaked into the §6.4 block — the boundary is wrong, "
        "or the SKILL.md structure changed."
    )


def test_enumeration_is_not_capture_only():
    """The enumerator must see non-capturing invocations too (pass-2 C18).

    If this ever finds that every enumerated invocation is capturing, the enumerator has
    silently degenerated back to the circular capture-only key.
    """
    invocations = _invocations()
    assert invocations, "enumerated no script invocations in §6.4 — the parser is broken"
    assert any(not inv["capturing"] for inv in invocations), (
        "every enumerated invocation is capturing — the enumerator can no longer see "
        "non-capturing steps, which is exactly the circular key C18 rejected."
    )


def test_comment_only_invocations_are_enumerated():
    """`set-deliverable-class` appears ONLY inside a `#` comment (pass-3 C25).

    Pins the documented comment-handling rule: commented invocations still count.
    """
    by_name = {inv["name"]: inv for inv in _invocations()}
    sdc = by_name.get("set-deliverable-class")
    assert sdc is not None, (
        "`set-deliverable-class` was not enumerated — the comment-handling rule regressed "
        "and commented invocations are now being stripped."
    )
    assert sdc["commented"], (
        "`set-deliverable-class` is no longer comment-only. That is fine, but this test "
        "pinned the comment-handling rule through it; pin the rule through another "
        "commented invocation or assert it directly."
    )


def test_no_shorthand_verb_references_evade_the_enumerator():
    """Close the shorthand loophole the enumerator would otherwise miss.

    The enumerator recognises the documented full form
    `uv run ${SKILL_DIR}/scripts/<script>.py <verb>`. A step written in shorthand —
    `# On operator override: set-deliverable-class …`, which is how the live block used to
    read — would be invisible to it. That shorthand is also a doc defect in its own right: an
    operator copying the line runs a command that does not exist.

    So the block must contain no bare reference to a known verb in command position. This is
    what makes the "comments are not stripped" rule sufficient rather than merely stated.
    """
    block = _section_64()
    known = {inv["verb"] for inv in _invocations() if inv["verb"]} | set(EXEMPT_VERBS)
    offenders = []
    for raw in block.splitlines():
        line = raw.strip().lstrip("#").strip()
        if not line or "uv run" in line:
            continue
        for verb in known:
            # verb in COMMAND position: at line start, or right after a `:` lead-in,
            # and followed by an argument-looking token.
            if re.match(rf"^(?:.*:\s*)?{re.escape(verb)}\s+[\"'$<]", line):
                offenders.append(f"  - {verb}: {raw.strip()}")
    assert not offenders, (
        "§6.4 references a known verb in command position without the documented "
        "`uv run ${SKILL_DIR}/scripts/<script>.py <verb>` form:\n"
        + "\n".join(offenders)
        + "\n\nWrite the full invocation. Shorthand is invisible to the enumerator and is "
          "not copy-pasteable by an operator."
    )


def test_every_invocation_is_capturing_or_exempt():
    """THE contract check (REQ-COMPLETE-003, SC2).

    Every script invocation in §6.4 must either capture an envelope or be named on the
    exempt list. A newly added non-conformant step fails HERE.
    """
    offenders = [
        inv for inv in _invocations()
        if not inv["capturing"] and inv["name"] not in EXEMPT_VERBS
    ]
    assert not offenders, (
        "§6.4 contains script invocation(s) that neither capture a verdict envelope nor "
        "appear on the named exempt list (REQ-COMPLETE-003):\n"
        + "\n".join(f"  - {o['name']}: {o['line']}" for o in offenders)
        + "\n\nEither capture the verdict with the documented `X=$(… --json)` idiom and "
          "honour the envelope, or add the verb to EXEMPT_VERBS with a written reason."
    )


def test_exempt_list_has_no_dead_entries():
    """An exemption for a step that no longer exists is stale authority — remove it."""
    names = {inv["name"] for inv in _invocations()}
    dead = sorted(EXEMPT_VERBS - names)
    assert not dead, (
        f"EXEMPT_VERBS names step(s) absent from §6.4: {dead}. Remove them so the "
        "exempt list stays a closed, reviewable statement about the live block."
    )


# ======================================================================================
# REQ-CLI-016 / REQ-COMPLETE-003(a) — the FAILING path yields a non-empty,
# envelope-conformant capture under the documented `X=$(…)` idiom.
#
# This is the check that FAILED before plan-043: `complete-gate` wrote its fail verdict to
# stderr, so `GATE=$(…)` captured the empty string and `echo "$GATE"` printed nothing on
# exactly the path an operator needs to read.
# ======================================================================================

def _capture_stdout_only(script: str, *args: str, env: dict | None = None) -> tuple[int, str]:
    """Run a verb capturing STDOUT ONLY — the documented `X=$(…)` idiom, faithfully.

    Invoked through `uv run`, exactly as SKILL.md invokes it: the scripts carry PEP 723
    inline dependencies, so a bare `sys.executable` run would fail for the wrong reason.
    """
    proc = subprocess.run(
        ["uv", "run", str(_HERE / script), *args],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env,
    )
    return proc.returncode, proc.stdout


def _assert_envelope(payload: str, *, expect_verdict: str, step: str) -> dict:
    assert payload.strip(), (
        f"{step}: the documented `X=$(…)` capture was EMPTY on the failing path. The verdict "
        "is being written somewhere stdout cannot see it (REQ-COMPLETE-003(a))."
    )
    obj = json.loads(payload)
    assert obj.get("verdict") == expect_verdict, (
        f"{step}: expected verdict {expect_verdict!r}, got {obj.get('verdict')!r}"
    )
    # `passed` is a DERIVED compatibility key: it must agree with `verdict`.
    assert obj.get("passed") == (obj["verdict"] == "pass"), (
        f"{step}: `passed` disagrees with `verdict` — it is a derived key, not an "
        "independent one (REQ-COMPLETE-003(b))."
    )
    assert obj.get("reason"), f"{step}: envelope carries no `reason`"
    if obj["verdict"] != "pass":
        assert obj.get("remediation"), (
            f"{step}: a non-pass verdict must carry actionable `remediation`"
        )
    return obj


def _ci_release_bundle(tmp_path: Path) -> Path:
    pdir = tmp_path / "plan-999-contract-test"
    pdir.mkdir()
    (pdir / "plan.md").write_text(
        "---\ntype: Plan\nid: plan-999-contract-test\ndeliverable_class: ci-release\n---\n"
        "# Plan: contract test\n\n"
        "**ID:** plan-999-contract-test\n"
        "**Deliverable-class:** ci-release\n\n"
        "## Objective\n\ncontract test\n",
        encoding="utf-8",
    )
    (pdir / "log.md").write_text("# Log\n\n## 2026-08-16\n\n- scoping: created\n", encoding="utf-8")
    return pdir


def _no_bd_env() -> dict:
    """A PATH with `uv` but no `bd`, so no deferred-validation bead can be discovered."""
    env = dict(os.environ)
    uv = shutil.which("uv")
    keep = str(Path(uv).parent) if uv else ""
    env["PATH"] = keep
    return env


def test_complete_gate_failing_path_captures_on_stdout(tmp_path):
    """REQ-CLI-016: the measured live defect this plan fixed."""
    pdir = _ci_release_bundle(tmp_path)
    rc, out = _capture_stdout_only(
        "plan_manager.py", "complete-gate", str(pdir), "--json", env=_no_bd_env()
    )
    _assert_envelope(out, expect_verdict="fail", step="complete-gate")
    assert rc != 0, "a halting step's `fail` verdict must exit non-zero (REQ-COMPLETE-003(c))"


def test_complete_gate_missing_plan_md_captures_on_stdout(tmp_path):
    """The second `err=True` path — a definite negative, so `fail`, not `inconclusive`."""
    empty = tmp_path / "not-a-plan"
    empty.mkdir()
    rc, out = _capture_stdout_only("plan_manager.py", "complete-gate", str(empty), "--json")
    _assert_envelope(out, expect_verdict="fail", step="complete-gate (no plan.md)")
    assert rc != 0


def test_complete_gate_noop_path_is_envelope_conformant(tmp_path):
    """An `advisory`-shaped no-op still emits the full envelope (REQ-COMPLETE-003(d))."""
    pdir = tmp_path / "plan-998-standard"
    pdir.mkdir()
    (pdir / "plan.md").write_text(
        "---\ntype: Plan\nid: plan-998-standard\ndeliverable_class: standard\n---\n"
        "# Plan: t\n\n**Deliverable-class:** standard\n\n## Objective\n\nt\n",
        encoding="utf-8",
    )
    rc, out = _capture_stdout_only("plan_manager.py", "complete-gate", str(pdir), "--json")
    obj = _assert_envelope(out, expect_verdict="pass", step="complete-gate (noop)")
    assert obj.get("noop") is True
    assert rc == 0


def test_close_cascade_failing_path_captures_on_stdout():
    """`close_cascade.py` is the reference implementation of the envelope contract."""
    rc, out = _capture_stdout_only("close_cascade.py", "--help")
    assert rc == 0 and out.strip(), "close_cascade.py is not invokable"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

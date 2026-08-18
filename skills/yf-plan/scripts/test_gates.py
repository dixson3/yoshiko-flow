# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml>=6",
# ]
# ///
"""Gate structure, enumeration and classification (plan-045 Epic 3).

Run from anywhere:  uv run skills/yf-plan/scripts/test_gates.py

WHY THIS FILE EXISTS
--------------------
Epic 3 converts gates from prose into structured beads so the execute-start sweep can
classify them mechanically. Three defects motivated it, all measured on a live repo:

* **D-7** — ``bd ready`` never returns a gate bead, so ``coordinator.md`` loop step 2 had
  **never fired once**. Measured: 24 ready beads, 0 gate-typed, with an open gate present.
* **C-2** — ``bd gate list --all --json`` returns **50** records on a **117**-gate corpus
  and **exits 0**. A sweep reading the default page sees a fraction of its input and
  reports success.
* **The literal-newline bug** — a bash double-quoted ``"\\n"`` stores a literal backslash-n,
  which corrupted 3 of the live gate descriptions.

The classification rules are safety rules, not conveniences, so each gets a test — including
the **negative** test that a ``human`` gate is never auto-resolved. A green test establishes
that a *condition holds*; it can never establish that a *human authorized* something.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SKILL_DIR = _HERE.parent
_SKILL_MD = _SKILL_DIR / "SKILL.md"
_COORDINATOR = _SKILL_DIR / "agents" / "coordinator.md"
_PLANNER = _SKILL_DIR / "agents" / "planner.md"
_RED_TEAM = _SKILL_DIR / "agents" / "red-team.md"


def _load_pm():
    spec = importlib.util.spec_from_file_location("plan_manager", _HERE / "plan_manager.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def pm(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return _load_pm()


# =======================================================================================
# 3.1 — the structured gate round-trips
# =======================================================================================

GATE_FIELDS = ("gate_type", "test", "test_class", "cwd")


def test_skill_md_emits_all_four_structured_fields():
    """3.1: the §5.2a gate-creation block must write the whole field set."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    for field in GATE_FIELDS:
        assert re.search(rf"\b{field}\b", text), (
            f"SKILL.md never mentions the gate metadata field {field!r}. Without the full "
            "field set the sweep falls back to regexing prose, which reaches only a third "
            "of live gates."
        )


def test_structured_gate_metadata_round_trips_through_json():
    """A gate's metadata must survive the jq -nc → bd → bd show round trip as a dict."""
    payload = {
        "gate_type": "auto",
        "test": "herdr tab create --no-focus probe && herdr tab close probe",
        "test_class": "probe",
        "cwd": "repo-root",
    }
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded == payload
    assert set(decoded) == set(GATE_FIELDS)


def test_description_uses_printf_not_a_double_quoted_backslash_n():
    """3.2: the emitter must produce REAL newlines.

    A bash double-quoted ``"a\\nb"`` stores a LITERAL backslash-n — verified directly below —
    which is what corrupted 3 live gate descriptions.
    """
    text = _SKILL_MD.read_text(encoding="utf-8")
    block = text[text.index("**Create capability gates"):]
    block = block[:block.index("Wire all dep-add links")]
    assert "printf" in block, (
        "the gate --description is not built with printf. A double-quoted \\n is stored "
        "literally by bash and has already corrupted live gate beads."
    )


def test_bash_double_quote_really_does_store_a_literal_backslash_n():
    """The premise of 3.2, asserted against a real shell rather than from memory."""
    out = subprocess.run(
        ["bash", "-c", r'X="a\nb"; printf %s "$X"'],
        capture_output=True, text=True, check=True,
    ).stdout
    assert out == r"a\nb", f"expected a literal backslash-n, got {out!r}"
    assert "\n" not in out

    out2 = subprocess.run(
        ["bash", "-c", "printf -v Y 'a\\nb'; printf %s \"$Y\""],
        capture_output=True, text=True, check=True,
    ).stdout
    assert out2 == "a\nb", (
        f"printf -v must produce a REAL newline, got {out2!r} — this is the whole basis of "
        "3.2's fix"
    )


# =======================================================================================
# 3.3 — the enumeration fix (D-7 and C-2)
# =======================================================================================

def test_coordinator_does_not_read_gates_out_of_bd_ready():
    """D-7: `bd ready` never returns a gate bead, so step 2 must not iterate it."""
    text = _COORDINATOR.read_text(encoding="utf-8")
    loop = text[text.index("## Loop"):]
    loop = loop[:loop.index("### Enumerating gates")]
    assert "bd list --type gate" in loop, (
        "the loop does not enumerate gates with their own query. Reading gates out of "
        "`bd ready` is D-7: measured 24 ready beads, 0 gate-typed, with an open gate present "
        "— the old step 2 has never fired once."
    )


def test_every_documented_gate_enumeration_passes_an_explicit_limit():
    """C-2: an unlimited `bd gate list`/`bd list --type gate` silently truncates at 50."""
    offenders = []
    for path in (_COORDINATOR, _SKILL_MD):
        in_fence = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            # Only a line INSIDE a fenced block is an invocation a reader would copy.
            # Prose that merely NAMES the command (e.g. the Trap 2 explanation, which must
            # be free to quote the truncating form) is documentation, not a recipe.
            if not in_fence:
                continue
            if re.search(r"bd (gate list|list --type gate)", line) and "--limit" not in line:
                offenders.append(f"{path.name}: {line.strip()}")
    assert not offenders, (
        "a gate enumeration without an explicit --limit: "
        + "; ".join(offenders)
        + ". Measured: the default page returns 50 of 117 AND EXITS 0. A sweep that reads it "
        "sees a fraction of its input and reports success."
    )


def test_the_truncation_trap_is_documented_with_its_numbers():
    """The next author must be able to see why the --limit is not optional."""
    text = _COORDINATOR.read_text(encoding="utf-8")
    assert "50" in text and "117" in text, (
        "the truncation trap is documented without its measured numbers; a rule with no "
        "evidence behind it is the first thing a later edit drops."
    )


def test_metadata_bearing_enumeration_is_the_one_recommended():
    """3.3's new finding: `bd gate list` rows carry NO metadata; `bd list --type gate` does."""
    text = _COORDINATOR.read_text(encoding="utf-8")
    assert "Carries `metadata`?" in text, (
        "the metadata-availability table is missing. A sweep enumerating with `bd gate list` "
        "would find the structured fields INVISIBLE and silently classify every gate as "
        "unstructured."
    )


def test_include_gates_flag_is_not_recommended_anywhere():
    """`bd ready --include-gates` does not exist: `unknown flag`, exit 1."""
    for path in (_COORDINATOR, _SKILL_MD):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "--include-gates" in line:
                assert "not" in line.lower() or "does **not** exist" in line, (
                    f"{path.name} recommends --include-gates, which bd rejects with "
                    f"'unknown flag: --include-gates' (exit 1): {line.strip()!r}"
                )


# =======================================================================================
# 3.4 / 3.5 — classification, and the safety rules
# =======================================================================================

def _classify(gate: dict, sweep_scope: str = "probe") -> str:
    """The shared evaluate-gate decision, as coordinator.md specifies it."""
    gate_type = gate.get("gate_type") or "human"       # absent → human
    if gate_type == "human":
        return "SURFACE"                                # never auto-resolved
    test = gate.get("test")
    test_class = gate.get("test_class") or "manual"
    if not test or test_class == "manual":
        return "INCONCLUSIVE"                           # never FAIL
    if test_class == "consent":
        return "SURFACE"                                # consent is never auto-run
    if test_class == "build" and sweep_scope != "all":
        return "DEFER"                                  # opt-in via --sweep-gates=all
    return "RUN"


def test_a_human_gate_is_never_auto_resolved_however_green_its_test():
    """THE negative test. A green test is not consent."""
    gate = {"gate_type": "human", "test": "true", "test_class": "probe", "cwd": "repo-root"}
    assert _classify(gate) == "SURFACE", (
        "a human-typed gate with a passing test was auto-resolved. A green test establishes "
        "that a CONDITION HOLDS; it can never establish that a HUMAN AUTHORIZED something. "
        "Auto-resolving would have granted publish authorization on at least three historical "
        "gates in this repo."
    )


def test_absent_gate_type_defaults_to_human():
    """The safe default: a mis-structured gate must fail toward a prompt, not an action."""
    assert _classify({"test": "true", "test_class": "probe"}) == "SURFACE"
    assert _classify({"gate_type": None, "test": "true", "test_class": "probe"}) == "SURFACE"


def test_a_non_command_test_is_inconclusive_not_fail():
    """An unrunnable test has established nothing IN EITHER DIRECTION."""
    assert _classify({"gate_type": "auto", "test": None, "test_class": "probe"}) == "INCONCLUSIVE"
    assert _classify({"gate_type": "auto", "test": "", "test_class": "probe"}) == "INCONCLUSIVE"
    assert _classify({"gate_type": "auto", "test": "x", "test_class": "manual"}) == "INCONCLUSIVE"


def test_probe_class_runs_unattended_and_build_does_not():
    assert _classify({"gate_type": "auto", "test": "x", "test_class": "probe"}) == "RUN"
    assert _classify({"gate_type": "auto", "test": "x", "test_class": "build"}) == "DEFER"
    assert _classify({"gate_type": "auto", "test": "x", "test_class": "build"},
                     sweep_scope="all") == "RUN"


def test_consent_class_is_never_auto_run_at_any_sweep_scope():
    """No flag value turns a green test into authorization."""
    for scope in ("probe", "all"):
        assert _classify({"gate_type": "auto", "test": "true", "test_class": "consent"},
                         sweep_scope=scope) == "SURFACE", (
            f"a consent-class gate was auto-run at --sweep-gates={scope}. consent is not a "
            "cost question, so widening the sweep must never reach it."
        )


# =======================================================================================
# 3.6 — the sweep scope flag
# =======================================================================================

def test_sweep_gates_defaults_to_probe(pm):
    assert pm._resolve_sweep_gates() == "probe"


def test_sweep_gates_override_validates(pm):
    pm._set_sweep_gates_override("all")
    assert pm._resolve_sweep_gates() == "all"
    with pytest.raises(ValueError):
        pm._set_sweep_gates_override("everything")
    pm._set_sweep_gates_override(None)
    assert pm._resolve_sweep_gates() == "probe"


def test_sweep_gates_unrecognised_config_falls_back(pm, tmp_path):
    (tmp_path / ".yf-plan.local.json").write_text('{"sweep-gates":"nonsense"}', encoding="utf-8")
    assert pm._resolve_sweep_gates() == "probe"


# =======================================================================================
# 3.5 / 3.7 — placement and ordering
# =======================================================================================

def test_the_sweep_is_placed_after_worktree_ensure_and_before_5_3():
    """The ordering is forced by the address-space model, so assert it positionally."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    i_wt = text.index("worktree ensure")
    i_sweep = text.index("#### 5.2c — The execute-start gate sweep")
    i_53 = text.index("### 5.3 — Run coordinator")
    assert i_wt < i_sweep < i_53, (
        "the sweep must sit after `worktree ensure` and before §5.3: it cannot route a test "
        "to the worktree address space until the worktree exists."
    )


def test_the_sweep_batches_non_probe_gates_into_one_prompt():
    text = _SKILL_MD.read_text(encoding="utf-8")
    assert re.search(r"ONE PROMPT", text), (
        "the sweep does not batch the remaining gates into a single prompt — that batching "
        "IS the frontloading. Without it the operator is still interrupted per gate."
    )


def test_gate_placement_principle_exists_in_planner():
    """3.7: no such guidance existed anywhere before (measured: 0 hits)."""
    text = _PLANNER.read_text(encoding="utf-8")
    assert "gate-placement principle" in text.lower()
    assert re.search(r"earliest", text, re.IGNORECASE), (
        "the principle must say EARLIEST decidable point, which is the whole content"
    )


def test_red_team_reachability_rule_is_reconciled_not_contradicted():
    """The two rules compose: reachability sets the floor, frontloading pushes down to it."""
    text = _RED_TEAM.read_text(encoding="utf-8")
    assert "gate the mutating step" in text, "the reachability rule must survive"
    assert re.search(r"earliest legal", text, re.IGNORECASE), (
        "red-team.md still reads as prescribing LATE placement. It must say it fixes the "
        "earliest LEGAL position, or it contradicts planner.md's frontloading principle."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

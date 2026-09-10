#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml",
# ]
# ///
"""REQ-LAND-037 — the `ctx.run` seam, and the declared ctx-less-helper set.

Three things are pinned here, and they are pinned to each other rather than to a number written
in any one place:

* the **derived** closure (`derive_land_launchers.py`, seeded on process-launch primitives),
* the **declared** constants (`LAND_CTXLESS_HELPERS`, `LAND_CTXLESS_HELPERS_UNROOTED`),
* the **SPEC text** (`spec/landing.md`'s REQ-LAND-037).

The reason all three exist is that any two of them can agree while the requirement is violated.
plan-068 pass-2 C1 measured the specific case: a token-keyed check on `subprocess.*` is
structurally blind to `_run_git`, so a check written against obligation 1 alone reports green
while obligation 2 is violated at five call sites.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PM = HERE / "plan_manager.py"
DERIVE = HERE / "derive_land_launchers.py"
SPEC = HERE.parent / "spec" / "landing.md"


def _load_pm():
    spec = importlib.util.spec_from_file_location("pm_seam", PM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pm_seam"] = mod
    spec.loader.exec_module(mod)
    return mod


pm = _load_pm()


def _derive():
    sys.path.insert(0, str(HERE))
    try:
        spec = importlib.util.spec_from_file_location("derive_seam", DERIVE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.derive(PM.read_text())
    finally:
        sys.path.pop(0)


# --------------------------------------------------------------------------------------------
# Obligation 2 — the declaration and the derivation agree
# --------------------------------------------------------------------------------------------

def test_declared_ctxless_helpers_match_the_derived_closure():
    """The hand-declared allowlist equals the mechanically derived transitive closure.

    Both directions. A one-directional check (`declared ⊆ closure`) is satisfiable by an
    over-broad declaration that hides nothing but proves nothing; the other direction
    (`closure ⊆ declared`) is the one that fails when someone adds a `subprocess` call to a
    helper an L-step reaches.
    """
    derived = set(_derive()["closure"])
    declared = set(pm.LAND_CTXLESS_HELPERS)

    undeclared = derived - declared
    stale = declared - derived
    assert not undeclared, (
        "indirect launchers reachable from an L-step but NOT declared in "
        f"LAND_CTXLESS_HELPERS: {sorted(undeclared)}. Either route the call through ctx.run "
        "or declare the helper (and give it an explicit root)."
    )
    assert not stale, (
        f"declared but unreachable from any L-step — a stale declaration: {sorted(stale)}"
    )


def test_the_declared_set_is_not_empty_and_the_spec_says_so():
    """REQ-LAND-037 explicitly refuses to claim this set will be empty.

    plan-068 Issue 0.3: *'What is not safe is landing a constant the SPEC says should be
    empty.'* So the SPEC's non-emptiness sentence and the constant's non-emptiness are asserted
    together — a later edit that empties one must confront the other.
    """
    assert pm.LAND_CTXLESS_HELPERS, "the declared set is empty"
    text = SPEC.read_text()
    assert "The declared set is NOT empty" in text, (
        "REQ-LAND-037 no longer carries its non-emptiness clause"
    )
    for name in ("_land_abort_merge", "_land_capture_conflict", "_land_changed_set"):
        assert name in text, f"REQ-LAND-037 does not name the off-seam helper {name}"
        assert name in pm.LAND_CTXLESS_HELPERS, f"{name} is not declared"


def test_unrooted_is_a_subset_and_is_recorded_as_a_defect_not_an_exemption():
    unrooted = set(pm.LAND_CTXLESS_HELPERS_UNROOTED)
    declared = set(pm.LAND_CTXLESS_HELPERS)
    assert unrooted <= declared, (
        f"LAND_CTXLESS_HELPERS_UNROOTED must be a subset of the declared set; "
        f"extra: {sorted(unrooted - declared)}"
    )
    # Each unrooted member must genuinely take no cwd-bearing parameter — otherwise the
    # residue list is stale and reads as a defect that no longer exists.
    tree = ast.parse(PM.read_text())
    sigs = {
        n.name: {a.arg for a in n.args.args} | {a.arg for a in n.args.kwonlyargs}
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in sorted(unrooted):
        params = sigs.get(name)
        assert params is not None, f"{name} is declared unrooted but is not a module function"
        assert not (params & {"root", "cwd", "repo_root", "runner"}), (
            f"{name} is listed in LAND_CTXLESS_HELPERS_UNROOTED but its signature now takes "
            f"{sorted(params & {'root', 'cwd', 'repo_root', 'runner'})} — remove it from the "
            "residue list rather than leaving a fixed defect recorded as open"
        )


def test_every_rooted_declared_helper_really_takes_an_explicit_root():
    """Obligation 2's second half: a declared helper resolves cwd from an explicit argument.

    Checked for every declared helper NOT on the unrooted residue list, so the residue list
    cannot be used to wave a helper through — a member must be on one list or satisfy the
    other.
    """
    tree = ast.parse(PM.read_text())
    sigs = {
        n.name: {a.arg for a in n.args.args} | {a.arg for a in n.args.kwonlyargs}
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    unrooted = set(pm.LAND_CTXLESS_HELPERS_UNROOTED)
    offenders = []
    for name in pm.LAND_CTXLESS_HELPERS:
        if name in unrooted:
            continue
        params = sigs.get(name, set())
        if not (params & {"root", "cwd", "repo_root", "runner"}):
            offenders.append(name)
    assert not offenders, (
        f"declared ctx-less helpers with no explicit cwd-bearing parameter: {offenders}. "
        "Give each a root=/cwd= argument, or record it in LAND_CTXLESS_HELPERS_UNROOTED."
    )


# --------------------------------------------------------------------------------------------
# The derivation itself — the properties the closure depends on
# --------------------------------------------------------------------------------------------

def test_the_seed_is_process_launch_primitives_not_a_helper_name():
    """pass-4's finding, pinned: seeding on a helper list misses `_repo_root` / `_git_root`.

    Both are bare `subprocess.run(["git", "rev-parse", "--show-toplevel"])` with no `cwd`.
    A hand-picked seed of `{subprocess, _run_git, _run_shell, _run_change_validation}` never
    reaches them, and they are exactly the `yf-i127` defect class. So the derivation must find
    them, and it must find them as DIRECT launchers.
    """
    d = _derive()
    assert "_repo_root" in d["direct_launchers"]
    assert "_git_root" in d["direct_launchers"]
    assert "_repo_root" in d["closure"]
    assert "_git_root" in d["closure"]


def test_the_seam_edge_is_excluded_explicitly_not_by_accident():
    """`ctx.run` / `_dispatch` must not be call-graph edges.

    Today the exclusion would hold anyway, because `self.run = self._dispatch` is an
    assignment and the AST resolves no callee named `run`. That is an accident. This test
    asserts the deriver names the exclusion, so a future `def run` cannot silently explode the
    closure to nearly the whole module.
    """
    src = DERIVE.read_text()
    assert "SEAM_NAMES" in src
    mod_tree = ast.parse(src)
    seam = None
    for node in mod_tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SEAM_NAMES" for t in node.targets
        ):
            seam = ast.literal_eval(node.value)
    assert seam == {"_dispatch", "run"}, f"SEAM_NAMES is {seam!r}"
    # And the closure must not contain the dispatcher itself.
    assert "_dispatch" not in _derive()["closure"]


def test_depth1_frontier_is_a_strict_subset_of_the_transitive_closure():
    """"Reachable" is transitive — pinned as a property, not as a pair of numbers.

    An earlier draft asserted the closure was ten when executing the mandated derivation
    yields thirteen (pass-5 C1): the same constant-vs-derivation mismatch this whole mechanism
    exists to remove. So the assertion is structural: the transitive set strictly contains the
    depth-1 set. A deriver that lost its transitivity would collapse the two and fail here.
    """
    d = _derive()
    frontier = set(d["depth1_frontier"])
    closure = set(d["closure"])
    assert frontier < closure, (
        f"depth-1 frontier ({sorted(frontier)}) is not a strict subset of the closure "
        f"({sorted(closure)}) — the derivation may have lost its transitive step"
    )


def test_derive_check_exits_zero():
    """The SPEC's own Verification line, executed."""
    r = subprocess.run(
        [sys.executable, str(DERIVE), "--check", "--json"],
        capture_output=True, text=True, cwd=str(HERE),
    )
    assert r.returncode == 0, f"derive --check failed:\n{r.stdout}\n{r.stderr}"


# --------------------------------------------------------------------------------------------
# The SPEC text and the constant cannot drift
# --------------------------------------------------------------------------------------------

def test_spec_quotes_the_script_rather_than_restating_a_number():
    """REQ-LAND-037 must point at the deriver, not carry a second enumeration.

    Issue 0.3: *'The SPEC quotes whatever the script emits; it does not restate a number.'*
    """
    text = SPEC.read_text()
    assert "REQ-LAND-037" in text
    assert "derive_land_launchers.py" in text
    assert "LAND_CTXLESS_HELPERS" in text
    # The two counts the SPEC does state are stated as derived facts about the frontier and
    # the closure, and the deriver must still emit them.
    d = _derive()
    assert d["counts"]["depth1_frontier"] == 6, d["counts"]
    assert d["counts"]["closure"] == 13, d["counts"]
    assert "depth-1 frontier is six" in text
    assert "transitive\nclosure is thirteen" in text or "closure is thirteen" in text


def test_req_land_031_carve_out_is_retired_in_text_and_031_itself_is_unchanged():
    """0.3's decision: the carve-out was an over-read; REQ-LAND-031's own text does not move.

    REQ-LAND-031 constrains the CALL (`force=False` in keyword form, branch on `status`). It
    says nothing about how the callee launches, so a fully-on-seam call satisfies it verbatim.
    """
    text = SPEC.read_text()
    assert "`REQ-LAND-031`'s carve-out is RETIRED as an over-read" in text
    # REQ-LAND-031's own clauses survive untouched.
    assert "shall call\n`_worktree_teardown` with `force=False` in **keyword** form" in text
    assert "shall **branch on the returned\n`status`**" in text


def test_the_no_runner_intercepts_a_filesystem_read_reason_is_recorded():
    """pass-5 C4: `runner=` alone closes only half the escape.

    The half a runner cannot close is *resolution* — `_validate_merged`'s tier-1 decision is
    three filesystem/config probes keyed on `_repo_root()`. Recording the reason is what stops
    a later reader from "simplifying" `root=` away as redundant with `runner=`.
    """
    text = SPEC.read_text()
    assert "no runner intercepts a filesystem read" in text.lower()
    assert "_approved_manifest_present" in text
    assert "_change_validation_script" in text


if __name__ == "__main__":
    # THE FORWARDING FORM (REQ-CLI-028): the house shim discards `sys.argv`, so a `-k`
    # selector never reaches pytest and a criterion routed through it stays green when
    # the named test is deleted.
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

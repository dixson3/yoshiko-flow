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
import json
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

    # THE COUNTS ARE PARSED FROM THE SPEC AND COMPARED TO A LIVE DERIVATION — never asserted
    # against a literal written here. Issue 0.3's mandate is *"the SPEC quotes whatever the
    # script emits; it does not restate a number"*, and an earlier version of this test pinned
    # `closure == 13`, which went stale one issue later when Epic 1's routing added the `_git`
    # shim and made it 14. A literal in the test is the same defect as a literal in the SPEC,
    # relocated: both are a second enumeration that can drift.
    m = re.search(r"^DERIVED: depth1_frontier=(\d+) closure=(\d+)$", text, re.M)
    assert m, "spec/landing.md carries no machine-readable `DERIVED:` counts line"
    d = _derive()
    assert int(m.group(1)) == d["counts"]["depth1_frontier"], (
        f"SPEC says depth-1 frontier={m.group(1)}, the deriver emits "
        f"{d['counts']['depth1_frontier']} — regenerate with derive_land_launchers.py"
    )
    assert int(m.group(2)) == d["counts"]["closure"], (
        f"SPEC says closure={m.group(2)}, the deriver emits {d['counts']['closure']} "
        "— regenerate with derive_land_launchers.py"
    )


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


# --------------------------------------------------------------------------------------------
# Issue 1.3 — the AST mechanical check, and its NEGATIVE CONTROLS
# --------------------------------------------------------------------------------------------

CHECK = HERE.parent.parent.parent / "scripts" / "checks" / "check_land_seam.py"


def _run_check(source_text: str, tmp: Path):
    """Run the check against a MUTATED COPY of plan_manager.py."""
    mutant = tmp / "plan_manager.py"
    mutant.write_text(source_text)
    r = subprocess.run(
        [sys.executable, str(CHECK), "--source", str(mutant), "--json"],
        capture_output=True, text=True, cwd=str(HERE),
    )
    return r


def test_the_ast_check_passes_on_the_real_module():
    r = subprocess.run([sys.executable, str(CHECK), "--json"],
                       capture_output=True, text=True, cwd=str(HERE))
    assert r.returncode == 0, f"{r.stdout}\n{r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["verdict"] == "PASS"
    assert payload["steps_checked"] >= 15, payload
    # NOT VACUOUS BY CONSTRUCTION: a check that inspected zero L-steps would "pass".
    assert payload["closure"], "the check saw an EMPTY closure — it proved nothing"


def test_obligation_1_fires_on_a_direct_launch_inside_an_L_step(tmp_path):
    """NEGATIVE CONTROL. Inject `subprocess.run` into an L-step; the check must FAIL.

    Without this, `test_the_ast_check_passes_on_the_real_module` is satisfiable by a check that
    never looks at anything — the shape #263 names and this repository has shipped four times.
    """
    src = PM.read_text()
    needle = 'def _land_l0_lock_acquire(ctx: LandingContext) -> dict:'
    assert needle in src
    mutated = src.replace(
        needle,
        needle + '\n    subprocess.run(["true"])  # INJECTED BY A NEGATIVE CONTROL',
        1,
    )
    r = _run_check(mutated, tmp_path)
    assert r.returncode == 1, f"the check did NOT fire on an injected direct launch:\n{r.stdout}"
    payload = json.loads(r.stdout)
    assert payload["verdict"] == "FAIL"
    assert any(v["function"] == "_land_l0_lock_acquire"
               for v in payload["direct_violations"]), payload


def test_obligation_2_fires_on_an_UNDECLARED_indirect_launcher(tmp_path):
    """NEGATIVE CONTROL, and the one that matters most.

    pass-2 C1 measured that a token-keyed check on `subprocess.*` is structurally BLIND to
    `_run_git`, so obligation 1 could pass while obligation 2 was violated at five call sites.
    This drops one name from the declared allowlist while leaving the code untouched: the
    closure is unchanged, so ONLY the second clause can catch it.
    """
    src = PM.read_text()
    assert '    "_run_git",\n' in src
    mutated = src.replace('    "_run_git",\n', "", 1)
    r = _run_check(mutated, tmp_path)
    assert r.returncode == 1, (
        "the check did NOT fire on an undeclared indirect launcher — obligation 2 is blind, "
        f"which is pass-2 C1's measured defect:\n{r.stdout}"
    )
    payload = json.loads(r.stdout)
    assert any(v["helper"] == "_run_git" for v in payload["indirect_violations"]), payload
    # AND obligation 1 must be SILENT on it, which is what proves the two clauses are
    # independent rather than one clause counted twice.
    assert not payload["direct_violations"], (
        "obligation 1 fired too — then this control does not establish that clause 2 is "
        "load-bearing"
    )


def test_a_token_list_would_not_have_worked(tmp_path):
    """pass-4 C9, pinned: `os.system` occurs ZERO times in this module.

    So a check keyed on a token list would be green forever while proving nothing about the
    tokens that DO occur. Recorded as an executable fact rather than a comment, because the
    argument for deriving the seed is only as good as the measurement behind it.
    """
    src = PM.read_text()
    assert "os.system" not in src, (
        "os.system now occurs in plan_manager.py — pass-4 C9's measurement has changed, and "
        "the argument for a derived seed should be re-stated from the new evidence rather "
        "than inherited"
    )
    # The derived seed finds real launchers anyway, which is the point.
    assert len(_derive()["direct_launchers"]) > 10, _derive()["counts"]


def test_the_check_is_INCONCLUSIVE_not_green_when_it_cannot_run(tmp_path):
    """Exit 2, never 0. A check that cannot run must not report a pass.

    REQ-DATA-057's precedent: an INCONCLUSIVE is a statement about the INSTRUMENT, not a
    verdict on the artifact. A missing source reporting 0 is the silent-failure class this
    whole plan is about.
    """
    r = subprocess.run(
        [sys.executable, str(CHECK), "--source", str(tmp_path / "nope.py"), "--json"],
        capture_output=True, text=True, cwd=str(HERE),
    )
    assert r.returncode == 2, f"expected INCONCLUSIVE (2), got {r.returncode}: {r.stdout}"
    assert "INCONCLUSIVE" in r.stderr


def test_the_two_out_of_L_step_bd_calls_take_an_explicit_root():
    """Issue 1.4 / SC2. Neither has `ctx` in scope, so each needs an explicit root argument.

    pass-1 flagged that leaving these advisory would let this plan close #348's normative
    sentence while two calls still read a database from the wrong cwd.
    """
    tree = ast.parse(PM.read_text())
    sigs = {
        n.name: {a.arg for a in n.args.args} | {a.arg for a in n.args.kwonlyargs}
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in ("_land_epic_from_bd", "_land_route_record_findings"):
        assert name in sigs, f"{name} is gone — re-scope SC2 rather than deleting the check"
        assert "root" in sigs[name], (
            f"{name} takes no explicit `root` — it has no `ctx` in scope, so a runner has "
            f"nothing to be given and a declared working directory is what REQ-LAND-037's "
            f"ctx-less clause requires. Signature: {sorted(sigs[name])}"
        )


if __name__ == "__main__":
    # THE FORWARDING FORM (REQ-CLI-028): the house shim discards `sys.argv`, so a `-k`
    # selector never reaches pytest and a criterion routed through it stays green when
    # the named test is deleted.
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Contract check for REQ-BUP-071 / REQ-BUP-073: no per-bead subprocess over the universe.

Run:  uv run skills/yf-beads-upstream/scripts/check_no_universe_fanout.py
      uv run skills/yf-beads-upstream/scripts/check_no_universe_fanout.py --check-timeouts
Exit: 0 = clean, 1 = a banned construct is present, 2 = the check could not run.

WHY THIS IS AN AST CHECK AND NOT A TOKEN OR SUBSTRING SCANNER
-------------------------------------------------------------
Its sibling `check_gh_direct.py` blanks STRING tokens and matches substrings. That
idiom was tried here first, twice, and it FAILS IN BOTH DIRECTIONS on this file:

  UNDER-MATCH.  Blanking every STRING turns `run(["bd", "dep", "list", bid])` into
                `run([ , , , ])`. The needle can never fire. (A corollary, filed
                separately: several of `check_gh_direct.py`'s own FORBIDDEN_SUBSTRINGS
                are string literals and are therefore vacuous for the same reason.)

  OVER-MATCH.   Scanning the RAW source instead matches `edge_type()`'s DOCSTRING,
                which legitimately says "bd dep list" while explaining the field-name
                divergence. The check would be RED ON CORRECTLY-FIXED CODE, and the
                only escape would be deleting a docstring that `check_gh_direct.py`'s
                own design forbids erasing and that Issue 1.1 depends on keeping.

An AST is blind to comments and docstrings and sees the CONSTRUCT. It also gives
enclosing-function tracking for free, which three of the rules below need.

WHY RULE (b) MUST FOLLOW HELPERS
--------------------------------
Measured on the pre-fix file: the only `bd show` argv sites were `:474` (inside
`external_for`) and `:552` (inside `deps_for_show`) — NEITHER lexically inside a loop.
The #268 defect was `for bid in sorted(beads): deps_for_show(bid)`, and the second N+1
was `external_for(bid)` in a loop. A rule matching only a literal argv inside a `for`
would not have fired on the pre-fix code and would not fire on its reintroduction — it
would ship green over an unenforced invariant (R15).

WHAT THIS CHECK DOES *NOT* CLAIM
--------------------------------
It matches a FIXED SET of AST constructs, not every possible N+1. That is not a
completeness claim (R9). It is strictly better than the prose prohibition that already
failed — `external_for`'s docstring says NEVER to call it in a loop over the whole
universe, and `cmd_enumerate` did exactly that, in the same file.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "upstream.py"

# Rule (e): the ONLY functions permitted to call `external_for`. The allow-list exists
# for the legitimate `[external_for(bid) for bid in ids]` comprehension in
# `cmd_mappings`, which operates on an EXPLICIT, operator-supplied id list — not the
# universe. `plan_hoist` is retained from the plan's specification even though it no
# longer calls it, so the allow-list is a superset of live usage.
EXTERNAL_FOR_ALLOWED = frozenset({"cmd_mappings", "plan_hoist"})

# Rule (d): the ONLY functions permitted to call `subprocess.run` directly. Everything
# else must route through the bounded primitives (REQ-BUP-072).
SUBPROCESS_RUN_ALLOWED = frozenset({"run", "run_unchecked", "_config_get"})

SPAWNERS = frozenset({"run", "run_unchecked"})

# Rule (c): a function deleted by Issue 1.2 and forbidden from returning.
BANNED_FUNCTION_NAMES = frozenset({"deps_for_show"})


class Finding:
    def __init__(self, rule: str, line: int, message: str):
        self.rule, self.line, self.message = rule, line, message
        # Set by `main` to the file actually checked. It defaults to the TARGET name so
        # a finding is still legible when `check()` is called directly (as the control
        # tests do), but a `--path` run must not misreport WHICH file it read.
        self.path = TARGET.name

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.rule}] {self.message}"


def _leading_constants(call: ast.Call) -> list[str]:
    """The leading string constants of a `run([...])`-style first argument.

    Returns [] for a call whose first argument is not a list literal — this check
    reasons about constructed argv lists, and says nothing about a dynamic one.
    """
    if not call.args:
        return []
    first = call.args[0]
    if not isinstance(first, (ast.List, ast.Tuple)):
        return []
    out = []
    for elt in first.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.append(elt.value)
        else:
            break
    return out


def _argv_matches(call: ast.Call, prefix: list[str]) -> bool:
    return _leading_constants(call)[: len(prefix)] == prefix


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _is_subprocess_run(call: ast.Call) -> bool:
    f = call.func
    return (isinstance(f, ast.Attribute) and f.attr == "run"
            and isinstance(f.value, ast.Name) and f.value.id == "subprocess")


def _functions_issuing(tree: ast.AST, prefix: list[str]) -> set[str]:
    """Names of module-level-or-nested functions whose OWN body issues `run([prefix...])`.

    This is what makes rule (b) follow helpers. It is one level of indirection, which
    is the level both real defects used; it is not a full call-graph closure, and the
    module docstring says so.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and _call_name(inner) in SPAWNERS
                    and _argv_matches(inner, prefix)):
                names.add(node.name)
                break
    return names


def _enclosing_functions(tree: ast.AST) -> dict[ast.AST, str]:
    """Map every node to the name of its nearest enclosing FunctionDef.

    Declared ONCE and used by every rule that needs it — rule (b)'s allow-list
    exemption, rule (d), and rule (e). An earlier design budgeted this for one rule and
    silently assumed it for another; an AST walk gives it for free.
    """
    out: dict[ast.AST, str] = {}

    def walk(node: ast.AST, current: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            nxt = child.name if isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef)) else current
            if nxt is not None:
                out[child] = nxt
            walk(child, nxt)

    walk(tree, None)
    return out


def _loop_bodies(tree: ast.AST) -> set[ast.AST]:
    """Every node lexically inside a `for`/`while`/comprehension."""
    inside: set[ast.AST] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While,
                             ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for child in ast.walk(node):
                if child is not node:
                    inside.add(child)
    return inside


def check(source: str, *, check_timeouts: bool = False,
          include_dep_list_rules: bool = False) -> list[Finding]:
    """Return every finding. An empty list is a clean tree.

    `include_dep_list_rules` gates the two rules that PRESUPPOSE Issue 1.7 having
    landed (see Issue 3.1c). They are off by default and deliberately so: Issue 1.7
    sits behind a human consent gate that may legitimately DECLINE, and a rule that is
    red until 1.7 lands would make the "Mechanical fan-out check green" gate
    permanently unpassable and the plan unclosable on a legal operator answer.
    """
    tree = ast.parse(source)
    enclosing = _enclosing_functions(tree)
    in_loop = _loop_bodies(tree)
    findings: list[Finding] = []

    show_helpers = _functions_issuing(tree, ["bd", "show"])
    dep_helpers = _functions_issuing(tree, ["bd", "dep", "list"])

    for node in ast.walk(tree):
        # --- rule (c): a deleted function must not be reintroduced -------------------
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in BANNED_FUNCTION_NAMES:
                findings.append(Finding(
                    "c", node.lineno,
                    f"`{node.name}` was deleted by REQ-BUP-071 (it issued one `bd show` "
                    f"per bead) and must not be reintroduced"))

        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        fn = enclosing.get(node)

        # --- rule (e): external_for is restricted to an explicit-id allow-list -------
        if name == "external_for" and fn not in EXTERNAL_FOR_ALLOWED:
            findings.append(Finding(
                "e", node.lineno,
                f"`external_for` called from `{fn}` — it issues one `bd show` per bead "
                f"and is permitted only in {sorted(EXTERNAL_FOR_ALLOWED)}. Read the "
                f"field off the row with `external_from_row(row)` instead"))

        # --- rule (d): direct subprocess.run outside the bounded primitives ----------
        if check_timeouts and _is_subprocess_run(node):
            if fn not in SUBPROCESS_RUN_ALLOWED:
                findings.append(Finding(
                    "d", node.lineno,
                    f"`subprocess.run` called directly from `{fn}` — every spawn must "
                    f"be bounded (REQ-BUP-072). Route through `run`/`run_unchecked`, "
                    f"which resolve the timeout from `cmd[0]`"))

        # --- rule (b): a per-bead `bd show`, directly OR via a helper, inside a loop --
        if node not in in_loop:
            continue
        # `cmd_mappings`/`plan_hoist` operate on an EXPLICIT id list, not the universe.
        # Without this exemption rule (b) is red on the legitimate comprehension in
        # `cmd_mappings` — an over-match of exactly the kind this check exists to avoid.
        if fn in EXTERNAL_FOR_ALLOWED:
            continue
        direct_show = name in SPAWNERS and _argv_matches(node, ["bd", "show"])
        via_helper = name in show_helpers
        if direct_show or via_helper:
            how = "directly" if direct_show else f"via helper `{name}`"
            findings.append(Finding(
                "b", node.lineno,
                f"per-bead `bd show` inside a loop ({how}) in `{fn}` — this is the "
                f"#268 fan-out. `bd list --all --json` already carries the field "
                f"(REQ-BUP-071)"))

        if include_dep_list_rules:
            direct_dep = name in SPAWNERS and _argv_matches(node, ["bd", "dep", "list"])
            via_dep_helper = name in dep_helpers
            if direct_dep or via_dep_helper:
                how = "directly" if direct_dep else f"via helper `{name}`"
                findings.append(Finding(
                    "a", node.lineno,
                    f"per-bead `bd dep list` inside a loop ({how}) in `{fn}` — the "
                    f"enclosing `bd list --parent <pid> --all --json` already returns "
                    f"`dependencies[]` (REQ-BUP-071)"))

    return sorted(findings, key=lambda f: (f.line, f.rule))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-timeouts", action="store_true",
                    help="also assert no unbounded subprocess.run remains (REQ-BUP-072)")
    ap.add_argument("--include-dep-list-rules", action="store_true",
                    help="also apply the `bd dep list` rules (Issue 3.1c; presupposes 1.7)")
    ap.add_argument("--path", default=str(TARGET))
    args = ap.parse_args()

    path = Path(args.path)
    try:
        source = path.read_text()
    except OSError as e:
        print(f"INCONCLUSIVE: cannot read {path}: {e}", file=sys.stderr)
        return 2
    try:
        findings = check(source, check_timeouts=args.check_timeouts,
                         include_dep_list_rules=args.include_dep_list_rules)
    except SyntaxError as e:
        print(f"INCONCLUSIVE: cannot parse {path}: {e}", file=sys.stderr)
        return 2

    for f in findings:
        f.path = path.name
    if findings:
        print(f"FAIL: {len(findings)} banned construct(s) in {path.name}:")
        for f in findings:
            print(f"  {f}")
        print("\nRemove the loop, not the check.")
        return 1
    print(f"OK: no per-bead universe fan-out in {path.name}"
          + (" (timeouts checked)" if args.check_timeouts else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

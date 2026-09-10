#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Derive REQ-LAND-037's ctx-less-helper closure MECHANICALLY from `plan_manager.py`.

Four consecutive review passes of plan-068 found a hand-written enumeration of this set short,
and pass-4 showed that even the *seed* was short: seeding on a hand-picked helper list
(`{subprocess, _run_git, _run_shell, _run_change_validation}`) misses `_repo_root` and
`_git_root`, both bare `subprocess.run(["git", "rev-parse", "--show-toplevel"])` with **no
`cwd`**, falling back to `Path.cwd()` / `Path(".")` — the `yf-i127` defect class exactly.

So this seeds on **process-launch primitives**, never on a helper name:

    subprocess.*        os.system / os.popen / os.spawn* / os.exec*        pty.*

Algorithm:

1. Mark every module-level function whose body contains a process-launch attribute call a
   **direct launcher**.
2. Take the **transitive closure** over the intra-module call graph: any function that calls a
   launcher is itself a launcher. `REQ-LAND-037`'s word "reachable" is transitive, and this
   step is what makes it so.
3. BFS from every `_land_l<N>_*` step function over that call graph, and report the launchers
   it reaches, **excluding the step functions themselves**.

**The seam edge is excluded EXPLICITLY** (`ctx.run`, `LandingContext._dispatch`). Today that
exclusion holds only by accident: `self.run = self._dispatch` is an *assignment*, so the AST
resolves no callee named `run`. If a future edit makes `run` a real `def`, the closure explodes
to nearly the whole module. Naming the exclusion means that edit changes nothing here.

Exit contract, three-valued:
  0  the closure was derived and printed
  1  the derived closure disagrees with `LAND_CTXLESS_HELPERS` (only under `--check`)
  2  INCONCLUSIVE — the source could not be read or parsed
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

#: The process-launch primitives the closure is SEEDED on. Attribute-call roots only —
#: `subprocess.run(...)`, `os.system(...)`, `pty.spawn(...)`. Never a helper name: a helper
#: name is the hand-written enumeration this module exists to replace.
LAUNCH_ROOTS = {"subprocess", "pty"}
LAUNCH_OS_ATTRS = re.compile(r"^(system|popen|spawn\w*|exec\w*|posix_spawn\w*|fork\w*)$")

#: The seam. Excluded from the closure explicitly rather than by accident — see the module
#: docstring.
SEAM_NAMES = {"_dispatch", "run"}

STEP_RE = re.compile(r"^_land_l\d+")


def inconclusive(msg: str) -> int:
    print(f"INCONCLUSIVE: {msg}", file=sys.stderr)
    return 2


def _is_launch_call(node: ast.Call) -> bool:
    f = node.func
    if not isinstance(f, ast.Attribute):
        return False
    root = f.value
    if not isinstance(root, ast.Name):
        return False
    if root.id in LAUNCH_ROOTS:
        return True
    if root.id == "os" and LAUNCH_OS_ATTRS.match(f.attr):
        return True
    return False


def _callee_names(node: ast.AST) -> set[str]:
    """Every intra-module callee name this function invokes, MINUS the seam.

    A bare `Name` callee (`_run_git(...)`) resolves to a module-level function. An `Attribute`
    callee (`ctx.run(...)`, `self._dispatch(...)`) is a method call — the seam — and is what
    this function drops.
    """
    out: set[str] = set()
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Name):
            if f.id not in SEAM_NAMES:
                out.add(f.id)
        elif isinstance(f, ast.Attribute):
            # Method / seam call. `ctx.run`, `self._dispatch`, `subprocess.run` — none of
            # these names a module-level function, so none contributes a call-graph edge.
            continue
    return out


def derive(source: str) -> dict:
    tree = ast.parse(source)

    funcs: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs[node.name] = node

    # 1. direct launchers — a process-launch primitive appears in the body
    direct = {
        name for name, fn in funcs.items()
        if any(isinstance(s, ast.Call) and _is_launch_call(s) for s in ast.walk(fn))
    }

    # call graph, intra-module, seam excluded
    calls = {name: (_callee_names(fn) & funcs.keys()) for name, fn in funcs.items()}

    # 2. transitive closure — a caller of a launcher is a launcher
    launchers = set(direct)
    changed = True
    while changed:
        changed = False
        for name, callees in calls.items():
            if name not in launchers and (callees & launchers):
                launchers.add(name)
                changed = True

    # 3. BFS from every L-step
    steps = sorted(n for n in funcs if STEP_RE.match(n))
    reached: set[str] = set()
    frontier = list(steps)
    seen = set(steps)
    depth1: set[str] = set()
    for s in steps:
        depth1 |= (calls.get(s, set()) & launchers)
    while frontier:
        cur = frontier.pop()
        for callee in calls.get(cur, set()):
            if callee in seen:
                continue
            seen.add(callee)
            frontier.append(callee)
            if callee in launchers:
                reached.add(callee)

    return {
        "steps": steps,
        "direct_launchers": sorted(direct),
        "closure": sorted(reached),
        "depth1_frontier": sorted(depth1),
        "counts": {
            "steps": len(steps),
            "direct_launchers": len(direct),
            "closure": len(reached),
            "depth1_frontier": len(depth1),
        },
    }


def declared_constant(source: str) -> list[str] | None:
    """Read `LAND_CTXLESS_HELPERS` out of the source without importing it."""
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == "LAND_CTXLESS_HELPERS":
                if node.value is None:
                    return None
                try:
                    val = ast.literal_eval(node.value)
                except ValueError:
                    return None
                return sorted(val)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default=None,
                    help="path to plan_manager.py (default: alongside this script)")
    ap.add_argument("--check", action="store_true",
                    help="compare the derived closure against LAND_CTXLESS_HELPERS and exit 1 "
                         "on disagreement")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    src_path = Path(a.source) if a.source else Path(__file__).resolve().parent / "plan_manager.py"
    try:
        source = src_path.read_text()
        result = derive(source)
    except (OSError, SyntaxError) as exc:
        return inconclusive(f"could not read/parse {src_path}: {exc}")

    result["source"] = str(src_path)
    result["declared"] = declared_constant(source)

    rc = 0
    if a.check:
        declared = result["declared"]
        if declared is None:
            return inconclusive("LAND_CTXLESS_HELPERS is not defined (or is not a literal)")
        # The DECLARED set is the allowlist REQ-LAND-037 requires. It is legitimately a
        # SUBSET of the derived closure once Issue 1.1 routes helpers onto the seam — a
        # routed helper leaves the declared set but stays in the closure as a `ctx.run`
        # consumer's callee. What is NEVER legitimate is a closure member that is neither
        # declared nor routed: that is an UNDECLARED indirect launcher.
        result["undeclared"] = sorted(set(result["closure"]) - set(declared))
        result["declared_but_unreached"] = sorted(set(declared) - set(result["closure"]))
        if result["undeclared"] or result["declared_but_unreached"]:
            rc = 1

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        c = result["counts"]
        print(f"source: {src_path}")
        print(f"L-steps: {c['steps']}  direct launchers: {c['direct_launchers']}")
        print(f"depth-1 frontier ({c['depth1_frontier']}): "
              f"{', '.join(result['depth1_frontier'])}")
        print(f"TRANSITIVE CLOSURE ({c['closure']}):")
        for n in result["closure"]:
            print(f"  {n}")
        if a.check:
            print(f"declared ({len(result['declared'] or [])}): "
                  f"{', '.join(result['declared'] or [])}")
            if result.get("undeclared"):
                print("FAIL: undeclared indirect launchers reachable from an L-step: "
                      f"{', '.join(result['undeclared'])}")
            if result.get("declared_but_unreached"):
                print("FAIL: declared but not reachable from any L-step (stale declaration): "
                      f"{', '.join(result['declared_but_unreached'])}")
            if rc == 0:
                print("PASS: the declared set and the derived closure agree.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

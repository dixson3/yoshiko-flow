#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""REQ-LAND-037 enforced MECHANICALLY, on both obligations.

Grep cannot do this. The requirement is about *where a call appears* and *what it reaches*, and
both are structure, not text — so this walks the AST.

**Two clauses, because a check written against the first alone reports green while the second is
violated.** plan-068 pass-2 C1 measured exactly that: a token-keyed check on `subprocess.*` is
structurally **blind** to `_run_git`, so obligation 1 passed while obligation 2 was violated at
five call sites, and both of the plan's criteria for the check would have been satisfied.

1. **No DIRECT process launch inside any `_land_l<N>_*` function.** Keyed on the *derived
   launcher set* from `derive_land_launchers.py`, not on a token list. pass-4 C9: `os.system`
   occurs **zero** times in this module, so a token list is the same hand-written-enumeration
   shape the derived closure just retired — it would pass forever while proving nothing about
   the tokens that do occur.

2. **No call to an INDIRECT launcher outside the declared set.** The allowlist is
   `LAND_CTXLESS_HELPERS`, read from the source. Deliberately **not** the call graph alone,
   which would make the check tautological — the constant is a hand-written declaration, and
   the whole value is that adding a `subprocess` call to a helper an L-step reaches breaks this
   check until someone declares it.

Exit contract, three-valued:
  0  both obligations hold
  1  a violation of either
  2  INCONCLUSIVE — the source could not be read or parsed, or the deriver is missing
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PM = REPO / "skills" / "yf-plan" / "scripts" / "plan_manager.py"
DERIVE = REPO / "skills" / "yf-plan" / "scripts" / "derive_land_launchers.py"
STEP_RE = re.compile(r"^_land_l\d+")


def inconclusive(msg: str) -> int:
    print(f"check_land_seam: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def _load_derive():
    spec = importlib.util.spec_from_file_location("derive_land_launchers", DERIVE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default=str(PM))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    src = Path(a.source)
    if not DERIVE.is_file():
        return inconclusive(f"the deriver is missing: {DERIVE}")
    try:
        source = src.read_text()
        tree = ast.parse(source)
        d = _load_derive()
        derived = d.derive(source)
        declared = d.declared_constant(source)
    except (OSError, SyntaxError) as exc:
        return inconclusive(f"could not read/parse {src}: {exc}")
    if declared is None:
        return inconclusive("LAND_CTXLESS_HELPERS is not defined (or is not a literal)")

    funcs = {
        n.name: n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    steps = sorted(n for n in funcs if STEP_RE.match(n))
    if not steps:
        return inconclusive(
            "no `_land_l<N>_*` function was found — the check had nothing to inspect, which is "
            "a statement about the instrument rather than a green verdict"
        )

    launchers = set(derived["direct_launchers"])
    allowlist = set(declared)

    # ---- Obligation 1: no DIRECT launch inside an L-step -----------------------------------
    direct_violations = []
    for name in steps:
        for sub in ast.walk(funcs[name]):
            if isinstance(sub, ast.Call) and d._is_launch_call(sub):
                f = sub.func
                direct_violations.append({
                    "function": name,
                    "line": sub.lineno,
                    "call": f"{getattr(f.value, 'id', '?')}.{f.attr}",
                })

    # ---- Obligation 2: no call to an UNDECLARED indirect launcher ---------------------------
    #
    # Checked over the WHOLE reachable closure, not only the L-steps' own bodies. "Reachable"
    # in REQ-LAND-037 is transitive, so a violation one frame down is still a violation — and
    # one frame down is where the five call sites pass-2 C1 measured actually lived.
    indirect_violations = []
    for name in derived["closure"]:
        if name not in allowlist:
            indirect_violations.append({
                "helper": name,
                "reason": "reachable from an L-step but absent from LAND_CTXLESS_HELPERS",
            })
    stale = [
        {"helper": n, "reason": "declared but not reachable from any L-step"}
        for n in sorted(allowlist - set(derived["closure"]))
    ]

    result = {
        "source": str(src),
        "steps_checked": len(steps),
        "direct_launcher_functions": len(launchers),
        "declared": sorted(allowlist),
        "closure": derived["closure"],
        "direct_violations": direct_violations,
        "indirect_violations": indirect_violations,
        "stale_declarations": stale,
    }
    bad = direct_violations or indirect_violations or stale
    result["verdict"] = "FAIL" if bad else "PASS"

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        if direct_violations:
            print("check_land_seam: FAIL — obligation 1: DIRECT process launch inside an "
                  "L-step function:")
            for v in direct_violations:
                print(f"  {src.name}:{v['line']} {v['function']} calls {v['call']} — route it "
                      f"through `ctx.run`")
        if indirect_violations:
            print("check_land_seam: FAIL — obligation 2: UNDECLARED indirect launcher "
                  "reachable from an L-step:")
            for v in indirect_violations:
                print(f"  {v['helper']} — {v['reason']}. Either route the call through "
                      f"`ctx.run` or declare it in LAND_CTXLESS_HELPERS (and give it an "
                      f"explicit root).")
        if stale:
            print("check_land_seam: FAIL — a STALE declaration:")
            for v in stale:
                print(f"  {v['helper']} — {v['reason']}")
        if not bad:
            print(f"check_land_seam: PASS — {len(steps)} L-step(s), no direct launch; "
                  f"{len(derived['closure'])} indirect launcher(s), all declared.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

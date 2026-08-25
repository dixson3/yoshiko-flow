#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Structured retrospective fields: `prevention_formula` and `prevention_vars` (#196).

**`prevention` STAYS PROSE, deliberately.** A retrospective's prevention narrative is a human
judgement, and mechanizing it would produce fake entries — the same failure `manual:` exists to
prevent in the Verification grammar. What IS mechanizable is a FORMULA NAME: an identifier with
a CLOSED DOMAIN (`bd formula list`), where an unchecked typo silently prevents nothing. So this
is the smallest slice of #196 that has an exit code, and no more.

Both directions matter. A checker that rejects everything passes a one-sided test while being
useless, so `--check-formula` accepts a known name and rejects an unknown one — and the known
set is READ FROM bd rather than hard-coded, so it cannot drift from the thing it validates.

Exit: 0 accepted · 1 REJECTED (a real negative) · 2 the checker could not run (INCONCLUSIVE —
bd absent or unreadable, which is a statement about the instrument, not about the name).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

INCONCLUSIVE = 2


def known_formulas(runner=subprocess.run) -> list[str] | None:
    """The closed domain, read from `bd formula list`. None when bd cannot be reached."""
    try:
        proc = runner(["bd", "formula", "list", "--json"],
                      capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        # Fall back to the human table: `  <name>   <description>`.
        names = re.findall(r"^\s{2}([a-z][a-z0-9-]*)\s{2,}", proc.stdout, re.M)
        return sorted(set(names)) or None
    if isinstance(rows, dict):
        rows = rows.get("formulas") or []
    return sorted({str(r.get("name")) for r in rows if isinstance(r, dict) and r.get("name")})


def check_formula(name: str, known: list[str] | None) -> tuple[int, str]:
    """-> (exit code, message). Pure given `known`."""
    if known is None:
        return INCONCLUSIVE, ("INCONCLUSIVE: could not read the formula domain from bd; "
                              "the name is unvalidated, which is not the same as invalid")
    if not (name or "").strip():
        return 1, "FAIL: prevention_formula is empty — an empty name prevents nothing"
    if name in known:
        return 0, f"ok: prevention_formula {name!r} is a known formula"
    return 1, (f"FAIL: prevention_formula {name!r} is not a known formula. "
               f"Known: {', '.join(known) or '(none)'}. An unchecked name is a typo that "
               f"silently prevents nothing.")


def parse_vars(pairs: list[str]) -> tuple[dict, list[str]]:
    """`k=v` pairs -> (dict, errors). `prevention_vars` is structured, unlike `prevention`."""
    out, errs = {}, []
    for p in pairs or []:
        if "=" not in p:
            errs.append(f"{p!r} is not a k=v pair")
            continue
        k, _, v = p.partition("=")
        k = k.strip()
        if not k:
            errs.append(f"{p!r} has an empty key")
            continue
        out[k] = v.strip()
    return out, errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-formula", metavar="NAME",
                    help="validate a prevention_formula name against `bd formula list`")
    ap.add_argument("--var", action="append", default=[], metavar="K=V",
                    help="a prevention_vars entry; repeatable")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    if a.check_formula is None:
        ap.error("--check-formula is required")

    known = known_formulas()
    code, msg = check_formula(a.check_formula, known)
    pvars, verrs = parse_vars(a.var)
    if verrs and code == 0:
        code, msg = 1, "FAIL: " + "; ".join(verrs)

    if a.as_json:
        print(json.dumps({
            "prevention_formula": a.check_formula,
            "prevention_vars": pvars,
            "known_formulas": known,
            "verdict": {0: "PASS", 1: "FAIL", INCONCLUSIVE: "INCONCLUSIVE"}[code],
            "message": msg,
            # Stated in the output, so a reader meets it where they use it.
            "note": "`prevention` itself remains PROSE — a narrative is a human judgement, "
                    "and mechanizing it would produce fake entries.",
        }, indent=1))
    else:
        print(msg, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

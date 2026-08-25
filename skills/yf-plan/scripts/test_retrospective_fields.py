#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for retrospective_fields (plan-052 Issue 5.3, #196).

`known_formulas` is injected, so no test depends on the machine's bd state — a checker tested
against live formulas would pass or fail for reasons unrelated to its logic.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

_spec = importlib.util.spec_from_file_location(
    "retrospective_fields", pathlib.Path(__file__).resolve().parent / "retrospective_fields.py")
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(("ok   " if ok else "FAIL ") + label + (f" — {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(label)


KNOWN = ["plan-execute", "plan-investigate", "plan-review", "yf-research"]

# --- both directions. A checker that rejects everything is useless. -----------------------
code, msg = rf.check_formula("plan-review", KNOWN)
check("a KNOWN formula is accepted (exit 0)", code == 0, msg)

code, msg = rf.check_formula("definitely-not-a-formula", KNOWN)
check("an UNKNOWN formula is REJECTED (exit 1, a real negative)", code == 1, msg)
check("...and the rejection names the closed domain", "plan-review" in msg, msg)

code, msg = rf.check_formula("", KNOWN)
check("an EMPTY name is rejected — an empty name prevents nothing", code == 1, msg)

# --- INCONCLUSIVE is not FAIL ------------------------------------------------------------
code, msg = rf.check_formula("plan-review", None)
check("an unreachable domain is INCONCLUSIVE (exit 2), never FAIL",
      code == rf.INCONCLUSIVE, msg)
check("...and says the name is UNVALIDATED, not invalid", "unvalidated" in msg.lower(), msg)

# --- near-misses must not slip through ----------------------------------------------------
for near in ("plan-reviews", "Plan-Review", "plan_review", " plan-review"):
    code, _ = rf.check_formula(near, KNOWN)
    check(f"near-miss {near!r} is rejected", code == 1)

# --- prevention_vars is structured; `prevention` itself is not touched --------------------
out, errs = rf.parse_vars(["a=1", "b=two"])
check("prevention_vars parses k=v pairs", out == {"a": "1", "b": "two"} and not errs, str(out))
out, errs = rf.parse_vars(["novalue"])
check("a malformed prevention_vars entry is an error, not silently dropped",
      errs and not out, f"{out} {errs}")
out, errs = rf.parse_vars(["=v"])
check("an empty KEY is an error", bool(errs), f"{out} {errs}")
out, errs = rf.parse_vars(["k=a=b"])
check("only the FIRST '=' splits, so a value may contain one", out == {"k": "a=b"}, str(out))

# --- the domain reader tolerates both bd output shapes ------------------------------------
class _P:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


check("known_formulas reads the --json shape",
      rf.known_formulas(lambda *a, **k: _P(0, '[{"name":"x"},{"name":"y"}]')) == ["x", "y"])
check("known_formulas falls back to the human table",
      rf.known_formulas(lambda *a, **k: _P(0, "  alpha   desc\n  beta    desc\n")) ==
      ["alpha", "beta"])
check("a bd failure yields None (INCONCLUSIVE), never an empty-and-therefore-strict domain",
      rf.known_formulas(lambda *a, **k: _P(1, "")) is None)

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s)")
    sys.exit(1)
print("all passed")

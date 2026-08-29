#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Paired controls for `check_no_universe_fanout.py` (REQ-BUP-073, plan-058 Issue 3.1b).

Run:  uv run skills/yf-beads-upstream/scripts/test_check_no_universe_fanout.py
Exit: 0 = every control passed, 1 = a control failed.

EVERY RULE GETS **BOTH** CONTROLS, AND THAT IS THE POINT
--------------------------------------------------------
  NEGATIVE control — a fixture containing the banned construct, asserted to FAIL.
                     Catches a rule that CANNOT FIRE.
  POSITIVE control — the rule asserted GREEN against correct code.
                     Catches a rule that FIRES ON CORRECT CODE.

Two review cycles of plan-058 produced exactly one failure of each kind: an
under-matching token scan that could never fire, and an over-matching source scan that
was red on correctly-fixed code and would have made a gate permanently unpassable.
A negative control alone catches only the first. Requiring both is what closes the class.

THE STRONGEST CONTROL HERE IS NOT A FIXTURE
-------------------------------------------
`test_fires_on_the_real_prefix_source` runs the check against the ACTUAL pre-fix
`upstream.py` recovered from git. A hand-written fixture proves a rule matches what its
author imagined; the real pre-fix file proves it matches THE DEFECT THAT SHIPPED.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location(
    "check_no_universe_fanout", _HERE / "check_no_universe_fanout.py")
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)

FAILURES: list[str] = []
CHECKS = 0


def expect(label: str, condition: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if condition:
        print(f"ok   {label}")
    else:
        print(f"FAIL {label}" + (f"\n       {detail}" if detail else ""))
        FAILURES.append(label)


def rules_fired(source: str, **kw) -> set[str]:
    return {f.rule for f in chk.check(source, **kw)}


# --- The correct, post-fix source: the POSITIVE control's subject ---------------------
REAL = (_HERE / "upstream.py").read_text()


# =====================================================================================
# RULE (b) — a per-bead `bd show` inside a loop, DIRECTLY or VIA A HELPER
# =====================================================================================

NEG_B_DIRECT = '''
def run(cmd): pass
def walk(beads):
    for bid in beads:
        run(["bd", "show", bid, "--json"])
'''

NEG_B_HELPER = '''
def run(cmd): pass
def deps_for_bead(bid):
    return run(["bd", "show", bid, "--json"])
def walk(beads):
    for bid in beads:
        deps_for_bead(bid)
'''

NEG_B_COMPREHENSION = '''
def run(cmd): pass
def ext(bid):
    return run(["bd", "show", bid, "--json"])
def walk(beads):
    return [ext(b) for b in beads]
'''

POS_B = '''
def walk(beads):
    for bid in beads:
        for dep in beads[bid].get("dependencies") or []:
            pass
'''

expect("(b) NEG: a literal `bd show` argv inside a for-loop FAILS",
       "b" in rules_fired(NEG_B_DIRECT))
expect("(b) NEG: a HELPER-MEDIATED `bd show` inside a for-loop FAILS",
       "b" in rules_fired(NEG_B_HELPER),
       "this is the form BOTH real defects took — neither argv site was lexically in a loop")
expect("(b) NEG: a helper-mediated `bd show` in a COMPREHENSION FAILS",
       "b" in rules_fired(NEG_B_COMPREHENSION))
expect("(b) POS: reading `dependencies[]` off the row is GREEN",
       "b" not in rules_fired(POS_B))
expect("(b) POS: the real post-fix upstream.py is GREEN",
       "b" not in rules_fired(REAL),
       "a rule red on correct code makes its gate permanently unpassable")


# =====================================================================================
# RULE (c) — `deps_for_show` must not be reintroduced
# =====================================================================================

NEG_C = '''
def deps_for_show(bead_id):
    return []
'''

expect("(c) NEG: reintroducing `deps_for_show` as a FunctionDef FAILS",
       "c" in rules_fired(NEG_C))
expect("(c) POS: the real post-fix upstream.py is GREEN (Issue 1.2 deleted it)",
       "c" not in rules_fired(REAL))
expect("(c) POS: the NAME in a comment or docstring does NOT fire",
       "c" not in rules_fired('"""deps_for_show was deleted."""\n# deps_for_show\n'),
       "an AST is blind to prose — this is the over-match a raw-source scan produced")


# =====================================================================================
# RULE (d) — no unbounded `subprocess.run` outside the bounded primitives
# =====================================================================================

NEG_D = '''
import subprocess
def helper(cmd):
    return subprocess.run(cmd, capture_output=True)
'''

POS_D = '''
import subprocess
def run(cmd, *, timeout=None):
    return subprocess.run(cmd, capture_output=True, timeout=timeout or 60)
def run_unchecked(cmd, *, timeout=None):
    return subprocess.run(cmd, capture_output=True, timeout=timeout or 60)
def _config_get(key):
    return subprocess.run(["bd", "config", "get", key], timeout=60)
'''

expect("(d) NEG: `subprocess.run` outside the bounded primitives FAILS",
       "d" in rules_fired(NEG_D, check_timeouts=True))
expect("(d) POS: the three bounded primitives are GREEN",
       "d" not in rules_fired(POS_D, check_timeouts=True))
expect("(d) POS: the real post-fix upstream.py is GREEN under --check-timeouts",
       "d" not in rules_fired(REAL, check_timeouts=True))
expect("(d) is OFF by default — it is a separate mode, not always-on",
       "d" not in rules_fired(NEG_D))


# =====================================================================================
# RULE (e) — `external_for` restricted to the explicit-id allow-list
# =====================================================================================

NEG_E = '''
def external_for(bid): pass
def cmd_enumerate(rows):
    return [external_for(r["id"]) for r in rows]
'''

POS_E = '''
def external_for(bid): pass
def cmd_mappings(ids):
    return [external_for(bid) for bid in ids]
'''

expect("(e) NEG: `external_for` called from a non-allow-listed function FAILS",
       "e" in rules_fired(NEG_E))
expect("(e) POS: `external_for` inside `cmd_mappings` is GREEN",
       "e" not in rules_fired(POS_E),
       "the legitimate explicit-id comprehension must not be flagged")
expect("(e) POS: the real post-fix upstream.py is GREEN",
       "e" not in rules_fired(REAL))


# =====================================================================================
# THE STRONGEST NEGATIVE CONTROL: the ACTUAL pre-fix source, recovered from git
# =====================================================================================

def _prefix_source() -> str | None:
    for rev in ("b065196", "main", "HEAD~5"):
        r = subprocess.run(["git", "show", f"{rev}:skills/yf-beads-upstream/scripts/upstream.py"],
                           capture_output=True, text=True, cwd=_HERE)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    return None


PREFIX = _prefix_source()
if PREFIX is None:
    # INCONCLUSIVE, reported — not silently skipped. A control that quietly vanishes is
    # indistinguishable from one that passed.
    print("WARN the pre-fix source could not be recovered from git — "
          "the real-defect control did not run (this is INCONCLUSIVE, not a pass)")
else:
    fired = rules_fired(PREFIX)
    expect("REAL NEG: the check FAILS on the actual pre-fix upstream.py",
           bool(fired), f"rules fired: {sorted(fired)}")
    expect("REAL NEG: rule (b) fires on the shipped #268 fan-out",
           "b" in fired,
           "if this fails, the rule detects neither N+1 this plan fixed")
    expect("REAL NEG: rule (e) fires on the shipped cmd_enumerate N+1",
           "e" in fired)
    expect("REAL NEG: rule (c) fires on the shipped `deps_for_show`",
           "c" in fired)


# =====================================================================================
# ISSUE 3.1c's SPLIT, verified rather than asserted
# =====================================================================================
#
# The `bd dep list` rules PRESUPPOSE Issue 1.7. If they shipped in the default rule set
# they would be red on the tree until 1.7 lands — and PERMANENTLY red if the operator
# declines at the Follow-on activation gate, making the "Mechanical fan-out check green"
# gate unpassable and the plan unclosable on a legal answer. This asserts the split
# holds mechanically, not merely by intent.

expect("3.1c SPLIT: the default rule set is GREEN on the current tree",
       chk.check(REAL) == [],
       "the core recurrence guard must not be held behind an unrelated consent gate")

_dep_default = rules_fired(REAL)
expect("3.1c SPLIT: rule (a) does NOT run by default",
       "a" not in _dep_default)

print()
if FAILURES:
    print(f"FAILED: {len(FAILURES)} of {CHECKS} controls failed:")
    for f in FAILURES:
        print(f"  - {f}")
    raise SystemExit(1)
print(f"all {CHECKS} paired controls passed")

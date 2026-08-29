#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1"]
# ///
"""Tier-1 tests for the yf-judgement trigger (plan-059 Epics 3 and 5).

  ctl-269-payload-both-paths  the `escalation` key is emitted FIRED and NOT-FIRED alike
  ctl-269-exit-3-preserved    the exit-3 escalating contract is unchanged by the payload
  ctl-270-seam                the payload is TRANSPORT-NEUTRAL, so #270 is a move not a redesign
  ctl-269-echo-external       the echo is observed by DIFFING log.md, never self-reported
  ctl-269-echo-removal        removing the echo call turns the check RED

`ctl-269-echo-removal` is the one that matters and the one nothing else covers. Every other
observability remedy in Epic 5 — enumerating the report by name in the close contract, a
tagged test at the call site — detects an ADDED step that ignores the contract; none detects
a REMOVED one. This arm mutates a scratch copy of `plan_manager.py` to delete the
`_judgement_echo` call and asserts `judgement-echo-check` goes red, which is the only way to
show the detector detects the thing it exists to detect.

Run:  uv run skills/yf-plan/scripts/test_judgement_trigger.py
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent.parent.parent
PM = SCRIPTS / "plan_manager.py"
BUNDLE = REPO / "docs/plans/plan-059-james-dixson-55137e"
FORMULA = SCRIPTS.parent / "formulas" / "plan-review.formula.toml"

#: The payload keys that are legal at all. Anything outside this set names a
#: `review-loop-check` internal and would have to be redesigned to move onto the #270 gate.
NEUTRAL_KEYS = {
    "question", "alternatives", "recommended", "on_no_answer", "detected_by",
    "evidence", "asked_of", "fired", "trigger", "stop_class",
}
#: Keys that MUST stay at top level. If any of these leaked into the payload, the payload
#: would carry the trigger's own bookkeeping and stop being movable.
TRIGGER_INTERNALS = {"cycles", "limit", "escalates", "autonomy", "raised"}

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def rlc(pdir: Path, script: Path = PM) -> tuple[int, dict]:
    r = subprocess.run(["uv", "run", str(script), "review-loop-check", str(pdir), "--json"],
                       capture_output=True, text=True, cwd=REPO)
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {"_stdout": r.stdout, "_stderr": r.stderr}


with tempfile.TemporaryDirectory() as td:
    fired_b = Path(td) / "fired"
    shutil.copytree(BUNDLE, fired_b)
    quiet_b = Path(td) / "quiet"
    shutil.copytree(BUNDLE, quiet_b)
    for f in (quiet_b / "reviews").glob("pass-*.md"):
        f.unlink()

    # ---- ctl-269-payload-both-paths / ctl-269-exit-3-preserved --------------------------
    rc_f, res_f = rlc(fired_b)
    rc_q, res_q = rlc(quiet_b)

    check("ctl-269-payload-both-paths: the escalation key is present on the FIRED path",
          "escalation" in res_f, f"{res_f}")
    check("ctl-269-payload-both-paths: and on the NOT-FIRED path",
          "escalation" in res_q,
          "a key present only when firing makes its absence mean two different things — "
          "'did not fire' and 'not installed'")
    check("ctl-269-payload-both-paths: `fired` genuinely differs between the two",
          res_f.get("escalation", {}).get("fired") is True
          and res_q.get("escalation", {}).get("fired") is False,
          f"fired={res_f.get('escalation',{}).get('fired')} "
          f"quiet={res_q.get('escalation',{}).get('fired')} — if they agreed, the two arms "
          f"would be one arm run twice")
    check("ctl-269-payload-both-paths: `on_no_answer` is non-null on BOTH paths",
          res_f.get("escalation", {}).get("on_no_answer")
          and res_q.get("escalation", {}).get("on_no_answer"),
          "the transport has no answer-return primitive; an escalation with no default "
          "pretends to a round-trip that cannot be delivered")

    check("ctl-269-exit-3-preserved: the escalating path still exits 3",
          rc_f == 3, f"exit {rc_f} — the payload must not disturb a contract callers branch on")
    check("ctl-269-exit-3-preserved: the converging path still exits 0", rc_q == 0, f"exit {rc_q}")

    # ---- ctl-270-seam -------------------------------------------------------------------
    payload = res_f.get("escalation", {})
    extra = set(payload) - NEUTRAL_KEYS
    check("ctl-270-seam: the payload carries ONLY transport-neutral keys",
          not extra,
          f"unexpected {sorted(extra)} — a payload naming its own trigger's internals cannot "
          f"move onto the #270 plan-review gate without redesign")
    leaked = set(payload) & TRIGGER_INTERNALS
    check("ctl-270-seam: no review-loop-check internal leaked into the payload",
          not leaked, f"leaked {sorted(leaked)}")
    check("ctl-270-seam: the trigger's own bookkeeping really IS at top level",
          TRIGGER_INTERNALS.issubset(set(res_f)),
          "if it were absent everywhere, 'did not leak' would be vacuously true")
    try:
        json.dumps(payload)
        serialisable = True
    except (TypeError, ValueError):
        serialisable = False
    check("ctl-270-seam: the payload round-trips as JSON (so it can be gate metadata)",
          serialisable)
    check("ctl-270-seam: the seam is NAMED in plan-review.formula.toml",
          "#270 SEAM" in FORMULA.read_text(),
          "a seam recorded only in the plan that made it is a seam the next reader re-derives")

    # ---- ctl-269-echo-external ----------------------------------------------------------
    r = subprocess.run(["uv", "run", str(PM), "judgement-echo-check", str(quiet_b), "--json"],
                       capture_output=True, text=True, cwd=REPO)
    echo = json.loads(r.stdout)
    check("ctl-269-echo-external: exactly one judgement line is added, observed by diff",
          r.returncode == 0 and echo["lines_added"] == 1, f"{echo}")
    check("ctl-269-echo-external: the not-fired literal is `judgement: not-fired`",
          "judgement: not-fired" in (echo.get("added_line") or ""), f"{echo.get('added_line')}")
    check("ctl-269-echo-external: and it does NOT match the fired literal",
          "judgement: fired" not in (echo.get("added_line") or ""),
          "the two literals must be genuinely independent, or SC6 and SC6d are one test")

    # ---- ctl-269-echo-removal: the detector detects a REMOVAL ---------------------------
    # The mutated copy must live BESIDE the real script: `plan_manager.py` imports siblings
    # (`okf`, `plan_template`) from its own directory, so a copy in a temp dir dies at import
    # and the arm would "fail" for a reason that has nothing to do with the mutation.
    broken = SCRIPTS / "_mutant_plan_manager.py"
    src = PM.read_text()
    patched, n = re.subn(
        r'result\["judgement_echo"\] = _judgement_echo\(',
        'result["judgement_echo"] = {} or _no_echo(',
        src,
    )
    check("ctl-269-echo-removal: the echo call site was found (the mutation is real)",
          n == 1, f"substituted {n} times — if 0, the arm below proves nothing")
    patched = patched.replace(
        "def _judgement_echo(plan_dir: Path, fired: bool, detail: str) -> dict:",
        "def _no_echo(*a, **k) -> dict:\n    return {'appended': False}\n\n\n"
        "def _judgement_echo(plan_dir: Path, fired: bool, detail: str) -> dict:",
        1,
    )
    broken.write_text(patched)
    scratch = Path(td) / "scratch"
    shutil.copytree(quiet_b, scratch)
    r2 = subprocess.run(["uv", "run", str(broken), "judgement-echo-check", str(scratch), "--json"],
                        capture_output=True, text=True, cwd=REPO)
    try:
        broken_res = json.loads(r2.stdout)
    except json.JSONDecodeError:
        broken_res = {"_stdout": r2.stdout, "_stderr": r2.stderr[-300:]}
    check("ctl-269-echo-removal: deleting the echo call turns judgement-echo-check RED",
          r2.returncode != 0 and broken_res.get("lines_added") == 0,
          f"rc={r2.returncode} res={broken_res} — a detector that stays green when the thing "
          f"it detects is removed is not a detector")
    broken.unlink(missing_ok=True)

# ---- ctl-269-callsite: the trigger's INVOCATION SITE is asserted, not assumed -----------
# Issue 5.3's "a tagged test that fails if the trigger is removed from its invocation site".
# `ctl-269-echo-removal` above proves the ECHO's removal is detected; this proves the
# TRIGGER's call site is, which is a different removal with the same silent signature.
CLOSE = SCRIPTS / "test_close_contract.py"


def assert_invocation(verb: str) -> tuple[int, dict]:
    r = subprocess.run(["uv", "run", str(CLOSE), "--assert-invocation", verb],
                       capture_output=True, text=True, cwd=REPO)
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {"_stdout": r.stdout[:300]}


for verb in ("escalation-raise", "escalation-push", "judgement-never-fired-report"):
    rc_v, res_v = assert_invocation(verb)
    check(f"ctl-269-callsite: `{verb}` is invoked at a real site",
          rc_v == 0 and res_v.get("sites"),
          f"rc={rc_v} res={res_v} — a verb registered but invoked nowhere is the "
          f"'ships unable to fire' defect (#145 finding 4)")

rc_v, res_v = assert_invocation("no-such-verb")
check("ctl-269-callsite: an UNRECOGNISED verb exits non-zero rather than being swallowed",
      rc_v != 0 and res_v.get("registered") is False,
      f"rc={rc_v} res={res_v} — before this the flag was silently ignored and the bare "
      f"suite passed, so the criterion was green before the work")

_steps = subprocess.run(["uv", "run", str(CLOSE), "--list-steps", "--json"],
                        capture_output=True, text=True, cwd=REPO)
check("ctl-269-callsite: --list-steps emits JSON as the SOLE stdout",
      _steps.returncode == 0 and _steps.stdout.lstrip().startswith("{"),
      f"stdout starts {_steps.stdout[:80]!r} — pytest's session banner corrupts the stream "
      f"unless the flag short-circuits BEFORE pytest (measured: jq parse error, rc=5)")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

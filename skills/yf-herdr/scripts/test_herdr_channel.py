#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 tests for the herdr channel facts (plan-059 Issue 4.2b, REQ-HERDR-027).

  ctl-264-exit0-not-found   a failed `herdr agent prompt` is not detectable from its exit code
  ctl-264-structural-rule   the structural predicate accepts only a confirmed delivery
  ctl-264-spec-records-it   the SPEC actually carries the claim this file tests

**Why this file exists.** REQ-HERDR-027 makes an empirical claim about a third-party tool —
that a *failed* delivery cannot be detected from its exit code — and until this file no code
asserted it. The claim is now backed by two DISAGREEING measurements: plan-059's EXP-004 saw
`agent_not_found` at exit `0`, and the same probe during that plan's execution saw exit `1`.
That disagreement strengthens the requirement rather than weakening it — a caller reading `$?`
is wrong under one of them and cannot tell which build it is on. A SPEC claim
with no test behind it is the shape plan-059 spent an experiment measuring: it survives right
up until someone writes `herdr agent prompt … && echo sent`, at which point a push into a
nonexistent pane is recorded as delivered and the escalation it carried is lost.

**The live arm degrades HONESTLY.** On a machine with no `herdr`, `ctl-264-exit0-not-found`
cannot be run and says so — it is reported `SKIP`, never `ok`. The structural arm is a pure
unit test of the decision rule and runs everywhere, so this file is never a silent green:
`ctl-264-structural-rule` alone would fail if the rule were relaxed to trust an exit code.

Run:  uv run skills/yf-herdr/scripts/test_herdr_channel.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

SPEC = Path(__file__).resolve().parent.parent / "SPEC.md"

failures: list[str] = []
skipped: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def skip(name: str, why: str) -> None:
    print(f"SKIP {name} — {why}")
    skipped.append(name)


def delivered(payload_text: str) -> bool:
    """THE REFERENCE IMPLEMENTATION of REQ-HERDR-027's structural predicate.

    Note what it does NOT take as an argument: the exit code. That omission is the whole
    requirement — a predicate that could see `$?` would eventually be written to consult it.
    """
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return False  # an unreadable answer is not a yes
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        return False
    return (payload.get("result") or {}).get("type") == "agent_prompted"


# ---- ctl-264-structural-rule ------------------------------------------------------------
check("ctl-264-structural-rule: a confirmed delivery is accepted",
      delivered('{"result": {"type": "agent_prompted", "agent": {"pane_id": "wK:p1"}}}'))
check("ctl-264-structural-rule: `agent_not_found` is NOT a delivery",
      not delivered('{"error": "agent_not_found"}'),
      "this is the payload the tool returns AT EXIT 0")
check("ctl-264-structural-rule: a missing `result.type` is NOT a delivery",
      not delivered('{"result": {"agent": {"pane_id": "wK:p1"}}}'))
check("ctl-264-structural-rule: a non-JSON stream is NOT a delivery",
      not delivered("Prompt sent to agent claude."),
      "a success-looking line is not evidence; the payload is")
check("ctl-264-structural-rule: an empty stream is NOT a delivery", not delivered(""))
check("ctl-264-structural-rule: a multi-document array is read at its first element",
      delivered('[{"result": {"type": "agent_prompted"}}, {"noise": 1}]'),
      "herdr and bd both emit array-wrapped JSON on some paths")

# ---- ctl-264-exit0-not-found (live) -----------------------------------------------------
if not shutil.which("herdr"):
    skip("ctl-264-exit0-not-found",
         "herdr is not on PATH; the live claim cannot be exercised on this machine. The "
         "structural arm above still constrains the decision rule.")
else:
    target = "yf-plan-059-nonexistent-pane-do-not-create"
    proc = subprocess.run(["herdr", "agent", "prompt", target, "probe"],
                          capture_output=True, text=True, timeout=60)
    raw = (proc.stdout or "").strip()
    check("ctl-264-exit0-not-found: a prompt to a NONEXISTENT target does not deliver",
          not delivered(raw),
          f"the structural predicate accepted {raw[:200]!r} — the channel fact may have "
          f"changed, or the target name is no longer nonexistent")
    if proc.returncode == 0:
        check("ctl-264-exit0-not-found: and it does so AT EXIT 0 (the documented hazard)",
              True)
        print("     ^ REQ-HERDR-027 confirmed live: exit 0, delivery NOT confirmed.")
    else:
        # NOT a failure. The requirement's POINT is that the exit code cannot be trusted in
        # EITHER direction — a version that exits non-zero here has not refuted it, it has
        # merely stopped exhibiting it, and a caller reading `$?` would still be wrong the
        # next time it changes.
        print(f"     ^ NOTE: this build exited {proc.returncode} rather than 0. The structural "
              f"rule is unaffected — it never reads the exit code, which is the requirement.")

# ---- ctl-264-spec-records-it ------------------------------------------------------------
spec = SPEC.read_text(encoding="utf-8")
for token, why in (
    ("REQ-HERDR-027", "the channel-facts requirement itself"),
    ("agent_not_found", "the exit-0 hazard, named"),
    ("REQ-HERDR-025a", "`working` is not evidence of phase advancement"),
    ("REQ-HERDR-028", "provenance-derived autonomy"),
):
    check(f"ctl-264-spec-records-it: SPEC.md carries {token} ({why})", token in spec)

print(f"\n{len(failures)} failure(s)" if failures else
      f"\nall passed" + (f" ({len(skipped)} skipped)" if skipped else ""))
sys.exit(1 if failures else 0)

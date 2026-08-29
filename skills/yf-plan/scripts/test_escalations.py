#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1"]
# ///
"""Tier-1 tests for `escalations.md` (plan-059 Epic 2, REQ-PORT-053 / REQ-PORT-054).

Four tags, and the third and fourth pull against each other on purpose:

  ctl-269-esc-domain-rules   raise refuses a malformed escalation ON WRITE
  ctl-269-esc-immutable      resolve mutates ONE entry and provably touches no other
  ctl-269-esc-audit-silent   the audit reports NOTHING about escalations, in either direction
  ctl-145-esc-not-retro      the retrospective was rejected as the surface, and stays rejected

`ctl-269-esc-audit-silent` is the one that is easy to satisfy vacuously. Asserting "no
escalation finding" against a bundle with no findings at all proves nothing, so it runs
against `plan-050`, which carries a substantial real finding set — the same non-vacuity
discipline plan-059's SC2c applies.

Run:  uv run skills/yf-plan/scripts/test_escalations.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent.parent.parent
PM = SCRIPTS / "plan_manager.py"
BUNDLE = REPO / "docs/plans/plan-059-james-dixson-55137e"
FINDINGS_BUNDLE = REPO / "docs/plans/plan-050-james-dixson-d0414b"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def pm(*args: str) -> tuple[int, str]:
    r = subprocess.run(["uv", "run", str(PM), *args], capture_output=True, text=True, cwd=REPO)
    return r.returncode, r.stdout


def pm_json(*args: str) -> tuple[int, dict]:
    rc, out = pm(*args)
    try:
        return rc, json.loads(out)
    except json.JSONDecodeError:
        return rc, {"_stdout": out}


# ---- ctl-269-esc-domain-rules: validate ON WRITE ---------------------------------------
with tempfile.TemporaryDirectory() as td:
    b = Path(td) / "b"
    shutil.copytree(BUNDLE, b)
    (b / "escalations.md").unlink(missing_ok=True)

    base = [str(b), "--question", "q", "--on-no-answer", "a", "--json"]

    rc, res = pm_json("escalation-raise", *base, "--alternative", "a",
                      "--recommended", "a")
    check("ctl-269-esc-domain-rules: ONE alternative is refused",
          rc != 0 and res.get("verdict") == "refused",
          f"rc={rc} res={res} — an escalation with one option is a notification, not a question")

    rc, res = pm_json("escalation-raise", *base, "--alternative", "a",
                      "--alternative", "b", "--recommended", "c")
    check("ctl-269-esc-domain-rules: a `recommended` outside `alternatives` is refused",
          rc != 0 and res.get("verdict") == "refused",
          f"rc={rc} res={res} — this is the type's load-bearing rule")

    rc, res = pm_json("escalation-raise", str(b), "--question", "q",
                      "--alternative", "a", "--alternative", "b",
                      "--recommended", "a", "--on-no-answer", "", "--json")
    check("ctl-269-esc-domain-rules: an empty `on_no_answer` is refused",
          rc != 0,
          "fire-and-forget is the actual semantics; an entry with no default pretends "
          "to a round-trip the transport cannot deliver")

    # THE REGRESSION ARM. This defect shipped and was caught by the portability audit, not by
    # this test — an alternative containing the `;` SEPARATOR passed validate-on-write (which
    # checked the in-memory list) and then FAILED ITS OWN SCHEMA on re-read, because the value
    # split. Validating the in-memory list was checking the wrong artifact: the document is
    # what the schema judges.
    rc, res = pm_json("escalation-raise", *base,
                      "--alternative", "an option; with a semicolon inside it",
                      "--alternative", "b",
                      "--recommended", "an option; with a semicolon inside it")
    check("ctl-269-esc-domain-rules: an alternative containing the `;` SEPARATOR is refused",
          rc != 0 and res.get("verdict") == "refused",
          f"rc={rc} res={res} — it would split on re-read, so `recommended` would match "
          f"nothing and the written entry would fail its own schema")

    check("ctl-269-esc-domain-rules: no refusal wrote a file",
          not (b / "escalations.md").exists(),
          "validate-on-write means a malformed escalation never reaches the artifact")

    rc, res = pm_json("escalation-raise", *base, "--alternative", "a",
                      "--alternative", "b", "--recommended", "b")
    check("ctl-269-esc-domain-rules: a conforming escalation IS written",
          rc == 0 and res.get("id") == "ESC-001" and res.get("state") == "raised",
          f"rc={rc} res={res} — if nothing could be written the refusals above are vacuous")
    check("ctl-269-esc-domain-rules: `evidence` defaults to the literal `unverified`",
          "| `evidence` | unverified |" in (b / "escalations.md").read_text(),
          "a blank default would make an unsubstantiated escalation quiet rather than "
          "self-identifying — the R4 Goodhart counterweight")
    check("ctl-269-esc-domain-rules: the new member is listed in the reserved index.md",
          "](escalations.md)" in (b / "index.md").read_text(),
          "an unindexed bundle member is the defect Issue 2.4 exists to prevent")

# ---- ctl-269-esc-immutable: resolve touches exactly one entry ---------------------------
with tempfile.TemporaryDirectory() as td:
    b = Path(td) / "b"
    shutil.copytree(BUNDLE, b)
    before = (b / "escalations.md").read_text()

    rc, res = pm_json("escalation-resolve", str(b), "ESC-001", "--answer", "x", "--json")
    check("ctl-269-esc-immutable: resolve moves the target to `resolved`",
          rc == 0 and res.get("state") == "resolved", f"rc={rc} res={res}")
    check("ctl-269-esc-immutable: prior entries are provably unchanged",
          res.get("prior_entries_unchanged") is True,
          "and it is computed from a pre/post hash of the untouched blocks, never asserted")
    check("ctl-269-esc-immutable: the two hashes really are EQUAL, not merely reported so",
          res.get("prior_entries_hash_before") == res.get("prior_entries_hash_after")
          and bool(res.get("prior_entries_hash_before")),
          "a verb that reports its own correctness has reported nothing")

    after = (b / "escalations.md").read_text()
    check("ctl-269-esc-immutable: the file DID change (the arm above is non-vacuous)",
          after != before,
          "if nothing changed, 'prior entries unchanged' would be trivially true")
    check("ctl-269-esc-immutable: ids are append-only — no id was renumbered",
          after.count("## ESC-001") == 1 and after.count("## ESC-002") == 1,
          "a lost mutation must be detectable rather than silent")

    rc, res = pm_json("escalation-resolve", str(b), "ESC-999", "--answer", "x", "--json")
    check("ctl-269-esc-immutable: an unknown id is REFUSED, not silently created",
          rc != 0 and res.get("verdict") == "refused", f"rc={rc} res={res}")

# ---- ctl-269-esc-audit-silent / ctl-145-esc-not-retro ----------------------------------
rc, audit = pm_json("audit", str(FINDINGS_BUNDLE), "--json-output")
n_findings = len(audit.get("findings", []))
check("ctl-269-esc-audit-silent: the control bundle carries a real finding set",
      n_findings >= 5,
      f"only {n_findings} findings — with none, 'no escalation finding' is vacuously true")
esc_findings = [f for f in audit.get("findings", [])
                if "escalation" in (f.get("item", "") + " " + f.get("detail", "")).lower()]
check("ctl-269-esc-audit-silent: a bundle with NO escalations.md gets no escalation finding",
      len(esc_findings) == 0,
      f"got {esc_findings} — REQ-PORT-ACT-ESCALATION: the file is in no presence list, and "
      f"absence is never a finding of ANY severity")

rc, audit59 = pm_json("audit", str(BUNDLE), "--json-output")
esc59 = [f for f in audit59.get("findings", [])
         if "escalation" in (f.get("item", "") + " " + f.get("detail", "")).lower()]
check("ctl-269-esc-audit-silent: a bundle WITH escalations.md also gets no audit finding",
      len(esc59) == 0,
      f"got {esc59} — the audit is silent in BOTH directions; the close-time chain, not the "
      f"audit, is where an OPEN escalation produces its signal")

retro_src = PM.read_text()
check("ctl-145-esc-not-retro: the rejection of plan-retrospective.md is RECORDED in code",
      "REJECTED as the escalation surface" in retro_src,
      "the two files look interchangeable and are not; a reader who cannot find the reason "
      "will merge them")
check("ctl-145-esc-not-retro: escalations are not a retrospective entry kind",
      "escalation" not in " ".join(
          l for l in retro_src.splitlines()
          if l.strip().startswith("RETROSPECTIVE_KINDS")),
      "R2: one append-only stream shared by open questions and closed adjudications would "
      "make retrospective-report count an unanswered question as a recorded event")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

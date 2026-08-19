#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""POSITIVE CONTROL for the pour-fidelity comparator (plan-047 Issue 5.4).

**This control is the entire reason the 40% divergence figure is trustworthy.** A comparator
that reports "17 of 43 plans are dirty" is worthless unless it can be shown to (a) fire on a
known mutation and (b) stay silent on the unmutated original. EXP-003 established exactly that
and it ships here so it runs in CI rather than being re-established by hand.

Three mutations, each of which MUST make the comparator fail:

  1. delete an issue line          -> a bead exists with no declared issue
  2. delete a `depends-on` bullet  -> an edge exists in `bd` and nowhere in the plan
  3. delete a gate block           -> the gate counts disagree

and the unmutated copy must be CLEAN.

Run:  uv run _shared/test_pour_fidelity.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
_spec = importlib.util.spec_from_file_location("pf", SHARED / "pour_fidelity.py")
pf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pf)

PLAN = REPO / "docs" / "plans" / "plan-047-james-dixson-dec9ff"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def bead_dump(dest: Path) -> bool:
    """Dump the live bead graph. `--include-gates` is MANDATORY (#166)."""
    try:
        r = subprocess.run(
            ["bd", "list", "--all", "--include-gates", "--limit", "5000", "--json"],
            capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    if r.returncode != 0 or not r.stdout.strip():
        return False
    dest.write_text(r.stdout)
    return True


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    beads = tmp / "beads.json"
    if not bead_dump(beads):
        # INCONCLUSIVE, not a pass: say so rather than reporting a green nobody earned.
        print("INCONCLUSIVE: `bd` unavailable or returned no graph — the control did not run.")
        sys.exit(2)

    def result(plan_dir: Path) -> dict:
        return pf.run(beads, [plan_dir])["results"][0]

    # --- 0. THE UNMUTATED ORIGINAL MUST BE CLEAN --------------------------------------
    # Without this the three mutations below prove nothing: a comparator that always fails
    # would "detect" every mutation.
    base = result(PLAN)
    check("the unmutated plan-047 is CLEAN", base["clean"] is True,
          json.dumps(base["verdict"]) + f' unnumbered={len(base["unnumbered_beads"])}')
    check("...and joins every issue by `plan_issue` METADATA, not by title",
          base["id_source"].get("metadata", 0) == base["issues"]["bd"]
          and base["id_source"].get("title", 0) == 0, str(base["id_source"]))

    def mutate(name: str, fn) -> dict:
        d = tmp / name
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(PLAN, d)
        p = d / "plan.md"
        p.write_text(fn(p.read_text()))
        return result(d)

    # --- 1. DELETE AN ISSUE LINE -------------------------------------------------------
    r = mutate("m1", lambda t: t.replace(
        "- Issue 5.4: **Ship the comparator's positive control with it and run it in CI.**", "", 1))
    check("deleting an issue line makes the comparator FAIL", r["clean"] is False)
    check("...and it is reported as an EXTRA bead, naming the id",
          "5.4" in r["issues"]["extra_beads"], str(r["issues"]["extra_beads"]))

    # --- 2. DELETE A `depends-on` BULLET ------------------------------------------------
    r = mutate("m2", lambda t: t.replace("  - depends-on: 5.3\n", "", 1))
    check("deleting a depends-on makes the comparator FAIL", r["clean"] is False)
    check("...and the edge is reported as INVENTED (present in bd, declared nowhere)",
          len(r["edges"]["invented"]) == 1, str(r["edges"]["invented"]))

    # --- 3. DELETE A GATE BLOCK ---------------------------------------------------------
    def drop_gate(t: str) -> str:
        i = t.index("### Capability Gate: carve-outs detectable")
        j = t.index("### Capability Gate: normalizer aggregate diff")
        return t[:i] + t[j:]

    r = mutate("m3", drop_gate)
    check("deleting a gate block makes the comparator FAIL", r["clean"] is False)
    check("...and the gate counts disagree",
          r["gates"]["plan"] != r["gates"]["bd"], str(r["gates"]))

    # --- 4. THE THREE POPULATIONS ARE REPORTED SEPARATELY (REQ-DATA-026 / review M1) ----
    all_plans = sorted((REPO / "docs" / "plans").glob("plan-*"))
    full = pf.run(beads, all_plans)
    pops = full["populations"]
    for key in ("no_mapping", "dropped_among_joinable",
                "invented_in_cleanly_parsed_plans",
                "invented_where_document_is_unreadable"):
        check(f"population `{key}` is reported as a distinct count", key in pops)
    check("the no-mapping population is exactly the three EXP-003 plans (006/007/036)",
          sorted(x.split("-")[1] for x in pops["no_mapping"]["plans"]) == ["006", "007", "036"],
          str(pops["no_mapping"]["plans"]))

    # --- 5. --strict is the close-gate mode --------------------------------------------
    rc = subprocess.run(
        [sys.executable, str(SHARED / "pour_fidelity.py"), str(beads), str(PLAN),
         "--strict", "--plan", PLAN.name],
        capture_output=True, text=True).returncode
    check("--strict exits 0 on a clean plan", rc == 0, f"got {rc}")
    d = tmp / "m4"
    shutil.copytree(PLAN, d)
    (d / "plan.md").write_text((d / "plan.md").read_text().replace(
        "  - depends-on: 5.3\n", "", 1))
    rc = subprocess.run(
        [sys.executable, str(SHARED / "pour_fidelity.py"), str(beads), str(d),
         "--strict", "--plan", d.name],
        capture_output=True, text=True).returncode
    check("--strict exits 1 on a divergent plan", rc == 1, f"got {rc}")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

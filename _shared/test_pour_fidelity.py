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

TWO TIERS, and the split is the point (plan-053 Issue 3.4 / #210).

  TIER A — SELF-CONTAINED. Builds its own plan bundle and its own bead graph in a temp dir.
           Needs no `bd`, no live bead state, and no `docs/plans/` corpus, so it runs in ANY
           repository. Every plan-053 arm lives here.
  TIER B — CORPUS. The three original mutation arms against `plan-047` and the live `bd`
           graph. RICHER but NOT PORTABLE, so it SKIPS with a stated reason when `bd` or the
           corpus is absent.

Before this split the whole suite exited 2 the moment `bd` was unavailable — so it could not
run in any repository but this one, which is *the same portability defect #210 is about*, in
the suite that guards #210's fix. A skip is reported as a skip; it never counts as a pass.

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


skipped: list[str] = []


def skip(name: str, why: str) -> None:
    """Report a SKIP. Never counted as a pass — a green nobody earned is the defect class."""
    print(f"SKIP {name} — {why}")
    skipped.append(name)


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    beads = tmp / "beads.json"
    _tier_b = bead_dump(beads) and PLAN.is_dir()

    def result(plan_dir: Path) -> dict:
        return pf.run(beads, [plan_dir])["results"][0]

  # ======================================================================================
  # TIER B — CORPUS ARMS. Richer, but NOT portable: they need `bd` and this repo's corpus.
  # ======================================================================================
    if not _tier_b:
        skip("TIER B (corpus mutation arms)",
             "`bd` is unavailable or docs/plans/plan-047 is absent — these arms are "
             "corpus-bound by construction. Tier A below covers the portable contract.")
    else:
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


  # ======================================================================================
  # TIER A — SELF-CONTAINED (plan-053 Issue 3.4 / #210).
  #
  # Builds its own bundle and its own bead graph. No `bd`, no live bead state, no corpus —
  # so it runs under a sandboxed HOME in any repository. SC5b asserts exactly this.
  # ======================================================================================
    def _bundle(name: str, *, epic: str | None = "fx-e", body_extra: str = "") -> Path:
        d = tmp / name
        d.mkdir(parents=True, exist_ok=True)
        epic_line = f"**Epic:** {epic}\n" if epic else ""
        (d / "plan.md").write_text(
            "---\ntype: Plan\nokf_spec: OKF-PLAN\nid: " + name + "\nauthor: fixture\n"
            "created: 2026-08-25\nstatus: executing\n---\n"
            f"# Plan: {name}\n\n**ID:** {name}\n{epic_line}\n"
            "## Objective\nfixture\n\n## Motivation\nfixture\n\n"
            "## Upstream Issues\n| Issue | Title | Disposition | Notes | Resolved By |\n"
            "|-------|-------|-------------|-------|-------------|\n\n"
            "## Investigation Findings\nNone.\n\n## Approach\nNone.\n\n"
            "## Epics\n### Epic 1: Work\n"
            "- Issue 1.1: The first issue\n"
            "- Issue 1.2: The second issue\n  - depends-on: 1.1\n"
            + body_extra +
            "\n## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n\n"
            "## Risks & Mitigations\n| # | Risk | Severity | Mitigation |\n| :-- | :-- | :-- | :-- |\n"
            "| R1 | none | low | none |\n\n"
            "## Success Criteria\n| # | Criterion | Verification | Discharged-by |\n"
            "| :-- | :-- | :-- | :-- |\n| SC1 | none | `true` \u2192 exit 0 | 1.1 |\n",
            encoding="utf-8")
        return d

    def _beads(path: Path, *, joinable: bool) -> Path:
        """A realistic pour: root epic, child epic, gate, two tasks.

        CONTAINMENT IS THE `parent` KEY — `load_beads` builds its tree from `b["parent"]`, not
        from a parent-child `dependencies` entry. And the child epic and gate are REQUIRED for
        `clean`, which checks epic_count and gate_count as well as issues and edges.
        """
        md = (lambda i: {"plan_issue": i}) if joinable else (lambda i: {})
        title = (lambda i, t: t) if joinable else (lambda i, t: t)
        path.write_text(json.dumps([
            {"id": "fx-e", "title": "plan-execute", "issue_type": "epic", "status": "open",
             "metadata": {"plan_dir": "x"}},
            {"id": "fx-e.e1", "title": "Epic 1: Work", "issue_type": "epic",
             "status": "closed", "parent": "fx-e", "metadata": {}},
            {"id": "fx-e.g1", "title": "Gate: Start Gate", "issue_type": "gate",
             "status": "closed", "parent": "fx-e", "metadata": {}},
            {"id": "fx-e.1", "title": title("1.1", "Do the first thing"), "issue_type": "task",
             "status": "closed", "parent": "fx-e.e1", "metadata": md("1.1")},
            {"id": "fx-e.2", "title": title("1.2", "Do the second thing"), "issue_type": "task",
             "status": "closed", "parent": "fx-e.e1", "metadata": md("1.2"),
             "dependencies": [{"depends_on_id": "fx-e.1", "type": "blocks"}]},
        ]))
        return path

    def _strict(beads_path: Path, plan_dir: Path, plan: str | None) -> int:
        cmd = [sys.executable, str(SHARED / "pour_fidelity.py"), str(beads_path),
               str(plan_dir), "--strict", "--json"]
        if plan:
            cmd += ["--plan", plan]
        return subprocess.run(cmd, capture_output=True, text=True).returncode

    ok_beads = _beads(tmp / "a-ok.json", joinable=True)
    nomap_beads = _beads(tmp / "a-nomap.json", joinable=False)

    # --- A0. THE BASELINE MUST BE CLEAN AND EXIT 0 -------------------------------------
    # Without this every arm below is satisfiable by a comparator that always returns 2.
    ok_dir = _bundle("plan-a0-fixture-aaaaaa")
    check("TIER A baseline: a clean, joinable, in-scope plan exits 0",
          _strict(ok_beads, ok_dir, ok_dir.name) == 0)

    # --- A1. EXIT 2 ON AN UNPARSED CONSTRUCT (REQ-DATA-043) ----------------------------
    # A plan the extractor could not fully read has a knowably incomplete declared DAG, so a
    # "dropped edge" verdict is unfounded and a "clean" verdict is worse — false-clean,
    # manufactured by the parser's blind spot rather than measured.
    bad_dir = _bundle("plan-a1-fixture-bbbbbb",
                      body_extra="- This is a column-0 bullet that is not a conformant issue\n")
    check("A1: --strict exits 2 (INCONCLUSIVE) when plan.md has an unparsed construct",
          _strict(ok_beads, bad_dir, bad_dir.name) == 2,
          f"got {_strict(ok_beads, bad_dir, bad_dir.name)}")

    # --- A2. EXIT 2 ON THE `no-mapping` POPULATION UNDER --strict -----------------------
    # THE POPULATION #210 JUSTIFIES THE GATE BY. #186/#187's masked titles are exactly what
    # destroys the title fallback, so the plans the gate most needs to judge were the ones it
    # silently passed at exit 0.
    nm_dir = _bundle("plan-a2-fixture-cccccc")
    check("A2: --strict exits 2 on a `no-mapping` plan (was a silent 0)",
          _strict(nomap_beads, nm_dir, nm_dir.name) == 2,
          f"got {_strict(nomap_beads, nm_dir, nm_dir.name)}")
    check("A2: ...and the plan really IS in the no-mapping population (not vacuous)",
          pf.run(nomap_beads, [nm_dir])["results"][0]["population"] == "no-mapping")

    # --- A3. EXIT 2 WHEN `--plan` MATCHES NOTHING ---------------------------------------
    # A typo, a renamed bundle, or a plan whose beads were never poured.
    check("A3: --strict exits 2 when --plan selects nothing",
          _strict(ok_beads, ok_dir, "plan-does-not-exist-zzzzzz") == 2,
          f"got {_strict(ok_beads, ok_dir, 'plan-does-not-exist-zzzzzz')}")

    # --- A4. EXIT 2 ON A SKIPPED DIR (no `**Epic:**`) -----------------------------------
    # `run()` puts such a bundle in `skipped[]` and never in `results`.
    noepic_dir = _bundle("plan-a4-fixture-dddddd", epic=None)
    check("A4: --strict exits 2 on a bundle with no **Epic:** field",
          _strict(ok_beads, noepic_dir, noepic_dir.name) == 2,
          f"got {_strict(ok_beads, noepic_dir, noepic_dir.name)}")
    check("A4: ...and it is reported in skipped[], with a reason",
          any(sk["reason"] for sk in pf.run(ok_beads, [noepic_dir])["skipped"]))

    # --- A5. THE NARROWNESS GUARD -------------------------------------------------------
    # Re-asserted AFTER the four exit-2 arms: if the fix had blanketed --strict with a 2,
    # A1-A4 would all pass while the verb was broken. A0 alone, run first, is not enough —
    # this is the same assertion made where a reader meets the risk.
    check("A5 (NARROWNESS): the clean plan STILL exits 0 after all four exit-2 arms",
          _strict(ok_beads, ok_dir, ok_dir.name) == 0,
          "a blanket `return 2 under --strict` satisfies A1-A4 and breaks the verb")

if skipped:
    print(f"\n{len(skipped)} skipped (stated, never counted as a pass): {skipped}")
print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

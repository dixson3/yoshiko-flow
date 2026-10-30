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
      # plan-074 (REQ-DATA-026 as amended): plan-047 predates the REQ-DATA-077 role receipt, so
      # strict completion can no longer judge its gate population by count alone. That is the
      # deliberate, documented boundary — NOT a pass. Tier A's A0/A5 carry the exit-0 contract
      # on a receipt-bound plan; the divergent arm below still proves exit 1.
      check("--strict on clean plan-047 (no role receipt) is INCONCLUSIVE (2), never a silent 0",
            rc == 2, f"got {rc}")
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
    FPR = "f" * 64

    def _bundle(name: str, *, epic: str | None = "fx-e", body_extra: str = "",
                receipt: bool = True) -> Path:
        """SYNTHETIC bundle. With `receipt`, it carries a finalized REQ-DATA-077 receipt over a
        retained pour capture, so the ONLY reason an arm below exits non-zero is that arm's cause
        (plan-074: a receipt-less plan is INCONCLUSIVE at strict completion)."""
        d = tmp / name
        d.mkdir(parents=True, exist_ok=True)
        if receipt and epic:
            (d / "assets").mkdir(exist_ok=True)
            (d / "assets" / "pour.json").write_text(json.dumps({"new_epic_id": epic, "id_mapping": {
                "plan-execute": epic, "plan-execute.start-gate": f"{epic}.w",
                "plan-execute.gate-start-gate": f"{epic}.g1"}}))
            (d / "references").mkdir(exist_ok=True)
            (d / "references" / "execution-roles.json").write_text(json.dumps({
                "schema": "yf-plan-execution-roles/v1", "plan_id": name, "fingerprint": FPR,
                "plan_dir": str(d), "root": epic, "bd_version": "fixture",
                "evidence_kind": "native", "state": "finalized",
                "evidence": [{"path": "assets/pour.json", "sha256": __import__("hashlib")
                              .sha256((d / "assets" / "pour.json").read_bytes()).hexdigest()}],
                "roles": {"plan-execute": epic, "plan-execute.start-gate": f"{epic}.w",
                          "plan-execute.gate-start-gate": f"{epic}.g1"},
                "gates": {"Start Gate (mandatory)": f"{epic}.g1"}}))
        epic_line = f"**Epic:** {epic}\n**Fingerprint:** {FPR}\n" if epic else ""
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

    def _beads(path: Path, *, joinable: bool, plan_dir: Path | None = None) -> Path:
        """A realistic pour: root epic, child epic, gate, two tasks.

        CONTAINMENT IS THE `parent` KEY — `load_beads` builds its tree from `b["parent"]`, not
        from a parent-child `dependencies` entry. And the child epic and gate are REQUIRED for
        `clean`, which checks epic_count and gate_count as well as issues and edges.
        """
        md = (lambda i: {"plan_issue": i}) if joinable else (lambda i: {})
        title = (lambda i, t: t) if joinable else (lambda i, t: t)

        def pc(i, parent):   # the native parent-child containment edge every child carries
            return {"issue_id": i, "depends_on_id": parent, "type": "parent-child"}
        # SYNTHETIC native-shaped pour: a gate-typed wrapper `fx-e.w` blocking the actual human
        # gate `fx-e.g1`, both direct children of the root; the entry issue waits on the wrapper.
        path.write_text(json.dumps([
            {"id": "fx-e", "title": "plan-execute", "issue_type": "epic", "status": "open",
             "metadata": {"plan_dir": str(plan_dir) if plan_dir else "x",
                          "yf_origin_fingerprint": FPR}},   # SYNTHETIC new-pour stamp (REQ-DATA-077)
            {"id": "fx-e.e1", "title": "Epic 1: Work", "issue_type": "epic",
             "status": "closed", "parent": "fx-e", "metadata": {}, "dependencies": [pc("fx-e.e1", "fx-e")]},
            {"id": "fx-e.w", "title": "Begin: fixture", "issue_type": "gate", "status": "closed",
             "parent": "fx-e", "dependencies": [pc("fx-e.w", "fx-e"),
                                                {"issue_id": "fx-e.w", "depends_on_id": "fx-e.g1",
                                                 "type": "blocks"}]},
            {"id": "fx-e.g1", "title": "Gate: human", "issue_type": "gate", "await_type": "human",
             "status": "closed", "parent": "fx-e", "metadata": {}, "dependencies": [pc("fx-e.g1", "fx-e")]},
            {"id": "fx-e.1", "title": title("1.1", "Do the first thing"), "issue_type": "task",
             "status": "closed", "parent": "fx-e.e1", "metadata": md("1.1"),
             "dependencies": [pc("fx-e.1", "fx-e.e1"),
                              {"issue_id": "fx-e.1", "depends_on_id": "fx-e.w", "type": "blocks"}]},
            {"id": "fx-e.2", "title": title("1.2", "Do the second thing"), "issue_type": "task",
             "status": "closed", "parent": "fx-e.e1", "metadata": md("1.2"),
             "dependencies": [pc("fx-e.2", "fx-e.e1"),
                              {"issue_id": "fx-e.2", "depends_on_id": "fx-e.1", "type": "blocks"}]},
        ]))
        return path

    def _strict(beads_path: Path, plan_dir: Path, plan: str | None) -> int:
        cmd = [sys.executable, str(SHARED / "pour_fidelity.py"), str(beads_path),
               str(plan_dir), "--strict", "--json"]
        if plan:
            cmd += ["--plan", plan]
        return subprocess.run(cmd, capture_output=True, text=True).returncode

    # --- A0. THE BASELINE MUST BE CLEAN AND EXIT 0 -------------------------------------
    # Without this every arm below is satisfiable by a comparator that always returns 2.
    ok_dir = _bundle("plan-a0-fixture-aaaaaa")
    ok_beads = _beads(tmp / "a-ok.json", joinable=True, plan_dir=ok_dir)
    check("TIER A baseline: a clean, joinable, in-scope plan exits 0",
          _strict(ok_beads, ok_dir, ok_dir.name) == 0)

    # --- A1. EXIT 2 ON AN UNPARSED CONSTRUCT (REQ-DATA-043) ----------------------------
    # A plan the extractor could not fully read has a knowably incomplete declared DAG, so a
    # "dropped edge" verdict is unfounded and a "clean" verdict is worse — false-clean,
    # manufactured by the parser's blind spot rather than measured.
    bad_dir = _bundle("plan-a1-fixture-bbbbbb",
                      body_extra="- This is a column-0 bullet that is not a conformant issue\n")
    bad_beads = _beads(tmp / "a-bad.json", joinable=True, plan_dir=bad_dir)
    check("A1: --strict exits 2 (INCONCLUSIVE) when plan.md has an unparsed construct",
          _strict(bad_beads, bad_dir, bad_dir.name) == 2,
          f"got {_strict(bad_beads, bad_dir, bad_dir.name)}")

    # --- A2. EXIT 2 ON THE `no-mapping` POPULATION UNDER --strict -----------------------
    # THE POPULATION #210 JUSTIFIES THE GATE BY. #186/#187's masked titles are exactly what
    # destroys the title fallback, so the plans the gate most needs to judge were the ones it
    # silently passed at exit 0.
    nm_dir = _bundle("plan-a2-fixture-cccccc")
    nomap_beads = _beads(tmp / "a-nomap.json", joinable=False, plan_dir=nm_dir)
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

    # --- A6. plan-074: the receipt boundary (REQ-DATA-026 as amended) ---------------------
    # The SAME clean beads with the receipt removed must be INCONCLUSIVE, not 0 — gate identity
    # cannot be judged by count (an equal-count substitution would pass).
    nr_dir = _bundle("plan-a6-fixture-eeeeee", receipt=False)
    nr_beads = _beads(tmp / "a-nr.json", joinable=True, plan_dir=nr_dir)
    check("A6: clean plan WITHOUT a role receipt -> --strict exits 2",
          _strict(nr_beads, nr_dir, nr_dir.name) == 2, f"got {_strict(nr_beads, nr_dir, nr_dir.name)}")
    # A definite issue-edge divergence is still 1 even without a receipt (it was observed).
    nr2 = _bundle("plan-a6b-fixture-ffffff", receipt=False)
    nr2_beads = _beads(tmp / "a-nr2.json", joinable=True, plan_dir=nr2)
    (nr2 / "plan.md").write_text((nr2 / "plan.md").read_text().replace("  - depends-on: 1.1\n", "", 1))
    check("A6b: definite edge divergence without a receipt -> 1 (observed, not unjudgeable)",
          _strict(nr2_beads, nr2, nr2.name) == 1, f"got {_strict(nr2_beads, nr2, nr2.name)}")
    # Receipt present but naming the wrong actual gate -> role FAIL -> 1.
    rf = _bundle("plan-a6c-fixture-gggggg")
    rf_beads = _beads(tmp / "a-rf.json", joinable=True, plan_dir=rf)
    rr = json.loads((rf / "references" / "execution-roles.json").read_text())
    rr["roles"]["plan-execute.start-gate"], rr["roles"]["plan-execute.gate-start-gate"] = "fx-e.g1", "fx-e.w"
    rr["gates"]["Start Gate (mandatory)"] = "fx-e.w"
    (rf / "references" / "execution-roles.json").write_text(json.dumps(rr))
    check("A6c: receipt contradicting the graph (swapped roles) -> --strict exits 1",
          _strict(rf_beads, rf, rf.name) == 1, f"got {_strict(rf_beads, rf, rf.name)}")
    # --roles is READ-ONLY and needs exactly one plan dir.
    ext = tmp / "external-roles.json"
    shutil.copy2(ok_dir / "references" / "execution-roles.json", ext)
    (nr_dir / "assets").mkdir(exist_ok=True)
    shutil.copy2(ok_dir / "assets" / "pour.json", nr_dir / "assets" / "pour.json")
    ext.write_text(ext.read_text().replace(str(ok_dir), str(nr_dir)).replace(
        "plan-a0-fixture-aaaaaa", "plan-a6-fixture-eeeeee"))
    before = sorted((p, p.read_bytes()) for p in nr_dir.rglob("*") if p.is_file())
    rc = subprocess.run([sys.executable, str(SHARED / "pour_fidelity.py"), str(nr_beads), str(nr_dir),
                         "--strict", "--plan", nr_dir.name, "--roles", str(ext)],
                        capture_output=True, text=True).returncode
    after = sorted((p, p.read_bytes()) for p in nr_dir.rglob("*") if p.is_file())
    check("A6d: --roles <external receipt> verifies the receipt-less bundle -> 0, writing nothing",
          rc == 0 and before == after, f"got {rc}")
    rc = subprocess.run([sys.executable, str(SHARED / "pour_fidelity.py"), str(nr_beads), str(nr_dir),
                         str(ok_dir), "--strict", "--roles", str(ext)], capture_output=True,
                        text=True).returncode
    check("A6e: --roles with two plan dirs -> 2", rc == 2, f"got {rc}")
    check("A6f (NARROWNESS): the receipt-bound clean plan STILL exits 0 after the A6 arms",
          _strict(ok_beads, ok_dir, ok_dir.name) == 0)

if skipped:
    print(f"\n{len(skipped)} skipped (stated, never counted as a pass): {skipped}")
print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

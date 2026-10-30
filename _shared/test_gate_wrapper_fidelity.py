#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""REQ-DATA-026 (as amended by plan-074) controls: receipt-bound gate identity in pour fidelity.

Run:  uv run _shared/test_gate_wrapper_fidelity.py     (exit 0 all passed · 1 failure)

Every judgement drives the REAL `_shared/pour_fidelity.py --strict` as a subprocess.

Inputs, labelled:
  GENUINE   plan-074's own B0 1.3.1 capture (`_shared/fixtures/gate-roles/b0-1.3.1-linked`),
            whose plan subgraph is FILTERED from a genuine snapshot; and PIM H0's frozen
            18-node snapshot + plan + executor-authored mapping, copied from the plan-074 bundle
            (`assets/fixtures/pim-h0`) and never modified in place.
  DERIVED   the B0 receipt, and the PIM legacy-attested receipt — both written by the REAL
            `record-execution-roles` verb in a scratch git repo.
  SYNTHETIC the PIM provenance acceptance (authored here, NOT an operator decision) and every
            graph/receipt mutation, labelled at the case.

The H0 red-to-green arm is the headline: the recorded installed verdict was divergent ONLY on
`gate_count_match` (3 declared vs 4 observed); with a receipt it must pass while the 8 issues,
7 issue edges and 4 epics denominators stay EXACTLY as recorded.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
PF = SHARED / "pour_fidelity.py"
PM = REPO / "skills" / "yf-plan" / "scripts" / "plan_manager.py"
B0 = SHARED / "fixtures" / "gate-roles" / "b0-1.3.1-linked"
PIM = REPO / "docs" / "plans" / "plan-074-james-dixson-4b8fe0" / "assets" / "fixtures" / "pim-h0"
P074, P012 = "plan-074-james-dixson-4b8fe0", "plan-012-james-dixson-d1af33"

failures: list[str] = []
ran = 0


def check(name, cond, detail=""):
    global ran
    ran += 1
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        failures.append(f"{name}: {str(detail)[:700]}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


ENV = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}


def strict(root: Path, beads: Path, plan_rel: str, *extra) -> tuple[int, dict, str]:
    r = subprocess.run([sys.executable, str(PF), str(beads), plan_rel, "--strict", "--plan",
                        Path(plan_rel).name, "--json", *extra], cwd=root, capture_output=True,
                       text=True, env=ENV, timeout=300)
    try:
        res = json.loads(r.stdout)["results"][0]
    except (json.JSONDecodeError, KeyError, IndexError):
        res = {}
    return r.returncode, res, r.stderr


TMP = Path(tempfile.mkdtemp(prefix="yf-p074-fidelity-"))
try:
    # ---- B0 genuine 1.3.1 -------------------------------------------------------------------
    root = TMP / "b0"
    bundle = root / "docs" / "plans" / P074
    cap = bundle / "assets" / "execution-roles"
    (cap / "creates").mkdir(parents=True)
    shutil.copy2(B0 / "plan" / "plan.md", bundle / "plan.md")
    for f in ("pour.json", "gate-creates.json"):
        shutil.copy2(B0 / f, cap / f)
    for f in ("gate-capability.json", "gate-reconcile.json"):
        shutil.copy2(B0 / "creates" / f, cap / "creates" / f)
    graph = root / "graph.json"
    shutil.copy2(B0 / "plan-subgraph.list.json", graph)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    PREL = f"docs/plans/{P074}"
    r = subprocess.run(["uv", "run", str(PM), "record-execution-roles", PREL, "--graph", str(graph),
                        "--pour", f"{PREL}/assets/execution-roles/pour.json", "--creates",
                        f"{PREL}/assets/execution-roles/gate-creates.json", "--bd-version",
                        "bd version 1.3.1 (Homebrew)", "--json"], cwd=root, capture_output=True,
                       text=True, env=ENV)
    check("DERIVED B0 finalized receipt written by the real verb", r.returncode == 0, r.stdout + r.stderr)

    rc, res, err = strict(root, graph, PREL)
    check("GENUINE B0 1.3.1 gate-wrapper graph + finalized receipt -> --strict exit 0",
          rc == 0 and res.get("clean") is True, (rc, err, res.get("verdict")))
    check("B0: wrapper excluded BY ID, three real gates counted, gate edges match",
          res.get("gates", {}).get("wrapper_excluded") == "yf-mol-r0p2"
          and res.get("gates", {}).get("bd") == 3 == res.get("gates", {}).get("plan")
          and res.get("verdict", {}).get("gate_identity_match") is True
          and res.get("verdict", {}).get("gate_edges_match") is True, res.get("gates"))
    check("B0: 8 issues / 7 edges / 4 epics", (res.get("issues", {}).get("bd"),
          res.get("edges", {}).get("bd"), res.get("epics", {}).get("bd")) == (8, 7, 4), res)

    base_graph = json.loads(graph.read_text())

    def mut(label, fn, code, receipt_fn=None):
        """SYNTHETIC mutation of the FILTERED genuine graph (and optionally the receipt)."""
        g = copy.deepcopy(base_graph)
        fn(g)
        gp = TMP / f"g-{ran}.json"
        gp.write_text(json.dumps(g))
        rp = bundle / "references" / "execution-roles.json"
        saved = rp.read_text()
        if receipt_fn:
            rr = json.loads(saved)
            receipt_fn(rr)
            rp.write_text(json.dumps(rr))
        try:
            rc, res, err = strict(root, gp, PREL)
        finally:
            rp.write_text(saved)
        check(f"{label} -> --strict exit {code}", rc == code, (rc, err[-400:], res.get("verdict")))
        return res

    def node(g, i):
        return next(n for n in g if n["id"] == i)

    def add_gate(g, gid, title="Gate: extra"):
        g.append({"id": gid, "issue_type": "gate", "status": "open", "title": title,
                  "parent": "yf-mol-9s78", "dependencies": [
                      {"issue_id": gid, "depends_on_id": "yf-mol-9s78", "type": "parent-child"}]})

    CAP, REC, ISSUE = "yf-mol-9s78.5", "yf-mol-9s78.6", "yf-mol-9s78.2.1"
    mut("SYNTHETIC extra unmapped real gate", lambda g: add_gate(g, "yf-x1"), 1)
    mut("SYNTHETIC Begin-titled extra gate (no title-based exclusion)",
        lambda g: add_gate(g, "yf-x2", "Begin: lookalike"), 1)
    mut("SYNTHETIC missing mapped gate (snapshot incomplete)",
        lambda g: g.remove(node(g, CAP)), 2)

    def substitute(g):   # count-preserving: the capability gate moves out, a stranger moves in
        c = node(g, CAP)
        c["parent"] = "yf-elsewhere"
        c["dependencies"] = [{"issue_id": CAP, "depends_on_id": "yf-elsewhere", "type": "parent-child"}]
        g.append({"id": "yf-elsewhere", "issue_type": "epic", "status": "open", "title": "x", "dependencies": []})
        add_gate(g, "yf-x3", c["title"])
        for n in g:
            for d in n.get("dependencies") or []:
                if d.get("depends_on_id") == CAP and n["id"] != CAP:
                    d["depends_on_id"] = "yf-x3"
    mut("SYNTHETIC count-preserving substituted capability gate", substitute, 1)
    mut("SYNTHETIC duplicate gate mapping in the receipt", lambda g: None, 2,
        lambda rr: rr["gates"].update({"Reconcile Gate": CAP}))
    mut("SYNTHETIC dropped gate-blocking edge (issue no longer waits on the capability gate)",
        lambda g: node(g, ISSUE).update(dependencies=[d for d in node(g, ISSUE)["dependencies"]
                                                      if d["depends_on_id"] != CAP]), 1)
    mut("SYNTHETIC invented gate-blocking edge (issue waits on the reconcile gate)",
        lambda g: node(g, ISSUE)["dependencies"].append(
            {"issue_id": ISSUE, "depends_on_id": REC, "type": "blocks"}), 1)
    mut("SYNTHETIC dropped entry-issue gating on the wrapper",
        lambda g: node(g, "yf-mol-9s78.1.1").update(dependencies=[
            d for d in node(g, "yf-mol-9s78.1.1")["dependencies"] if d["depends_on_id"] != "yf-mol-r0p2"]), 1)
    mut("SYNTHETIC reconcile step no longer gated", lambda g: node(g, "yf-mol-9s78.7").update(
        dependencies=[d for d in node(g, "yf-mol-9s78.7")["dependencies"] if d["depends_on_id"] != REC]), 1)
    mut("SYNTHETIC dropped issue edge (existing population still fires)",
        lambda g: node(g, "yf-mol-9s78.2.2").update(dependencies=[
            d for d in node(g, "yf-mol-9s78.2.2")["dependencies"] if d["depends_on_id"] != "yf-mol-9s78.2.1"]), 1)
    mut("SYNTHETIC start-only receipt at completion", lambda g: None, 2,
        lambda rr: rr.update(state="start-only", gates={"Start Gate (mandatory)": "yf-mol-nh83"}))
    mut("SYNTHETIC mapped real gate retyped task is counted, not dropped",
        lambda g: node(g, CAP).update(issue_type="task"), 0)
    rp = bundle / "references" / "execution-roles.json"
    saved = rp.read_text()
    rp.unlink()
    rc, res, err = strict(root, graph, PREL)
    rp.write_text(saved)
    check("absent receipt on the GENUINE B0 graph -> 2 (no title fallback), gate count alone unjudged",
          rc == 2 and res.get("gates", {}).get("bd") == 4, (rc, res.get("gates")))
    check("no receipt file was created by any strict run", sorted(p.name for p in (bundle / "references").iterdir())
          == ["execution-roles.json"])

    # ---- PIM H0 archived snapshot: recorded red -> green ---------------------------------------
    hist = json.loads((PIM / "historical-fidelity.json").read_text())["results"][0]
    check("recorded installed verdict was RED solely on gate count 3 vs 4",
          hist["gates"] == {"plan": 3, "bd": 4} and hist["verdict"]["gate_count_match"] is False
          and all(v for k, v in hist["verdict"].items() if k != "gate_count_match"), hist["verdict"])
    pim_before = {str(p): sha(p) for p in PIM.rglob("*") if p.is_file()}
    proot = TMP / "pim"
    pb = proot / "docs" / "plans" / P012
    (pb / "references").mkdir(parents=True)
    shutil.copy2(PIM / P012 / "plan.md", pb / "plan.md")
    shutil.copy2(PIM / "execution-epic-mapping.json", pb / "references" / "execution-epic-mapping.json")
    pgraph = proot / "beads.json"
    shutil.copy2(PIM / "beads.json", pgraph)
    subprocess.run(["git", "init", "-q"], cwd=proot, check=True)
    PPREL = f"docs/plans/{P012}"
    rc, res, err = strict(proot, pgraph, PPREL)
    check("H0 copy WITHOUT a receipt -> 2 (no longer a false red, never a false green)",
          rc == 2 and res.get("gates") and res["gates"]["bd"] == 4, (rc, err[-300:]))
    acc = TMP / "pim-acceptance.json"
    acc.write_text(json.dumps({
        "schema": "yf-plan-legacy-acceptance/v1", "plan_id": P012, "plan_dir": PPREL,
        "fingerprint": "2dd5d32c657cac2a4b15027285cf62f1760181494fbd3b46aa6b143aa05d2db7",
        "root": "pim-mol-vp2", "mapping_sha256": sha(pb / "references" / "execution-epic-mapping.json"),
        "decision": "SYNTHETIC TEST ACCEPTANCE — not an operator decision",
        "decided_by": "test_gate_wrapper_fidelity.py", "at": "2026-10-29T00:00:00Z"}))
    ext = TMP / "external" / "pim-roles.json"
    r = subprocess.run(["uv", "run", str(PM), "record-execution-roles", PPREL, "--graph", str(pgraph),
                        "--import-legacy", f"{PPREL}/references/execution-epic-mapping.json",
                        "--acceptance", str(acc), "--out", str(ext), "--bd-version",
                        "bd version 1.3.1 (Homebrew)", "--json"], cwd=proot, capture_output=True,
                       text=True, env=ENV)
    check("DERIVED external legacy-attested receipt for the H0 copy", r.returncode == 0, r.stdout + r.stderr)
    copy_before = {str(p): sha(p) for p in pb.rglob("*") if p.is_file()}
    rc, res, err = strict(proot, pgraph, PPREL, "--roles", str(ext))
    check("H0 copy + external receipt via read-only --roles -> GREEN (exit 0)", rc == 0, (rc, err[-400:]))
    check("H0 green keeps the recorded denominators: 8 issues, 7 edges, 4 epics; 3 = 3 gates",
          (res.get("issues", {}).get("bd"), res.get("issues", {}).get("plan"),
           res.get("edges", {}).get("bd"), res.get("edges", {}).get("plan"),
           res.get("epics", {}).get("bd"), res.get("gates", {}).get("bd"), res.get("gates", {}).get("plan"))
          == (8, 8, 7, 7, 4, 3, 3), res)
    check("H0: the excluded node is the mapped wrapper pim-mol-3pg, by id",
          res.get("gates", {}).get("wrapper_excluded") == "pim-mol-3pg", res.get("gates"))
    check("--roles wrote nothing into the H0 copy", {str(p): sha(p) for p in pb.rglob("*") if p.is_file()} == copy_before)
    check("the plan-074 bundle's frozen PIM evidence is byte-unchanged",
          {str(p): sha(p) for p in PIM.rglob("*") if p.is_file()} == pim_before)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

check("scratch removed", not TMP.exists())
if ran < 25:
    failures.append(f"only {ran} checks ran")
print(f"\n{ran} checks, {len(failures)} failure(s)" if failures else f"\n{ran} checks, all passed")
for f in failures:
    print("  " + f)
sys.exit(1 if failures else 0)

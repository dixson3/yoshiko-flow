#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""REQ-DATA-077 controls for `plan_manager.py record-execution-roles` (plan-074 Issue 1.2, #417).

Run:  uv run skills/yf-plan/scripts/test_execution_roles.py   (exit 0 all passed · 1 failure)

Every case drives the REAL verb as a subprocess (`uv run plan_manager.py record-execution-roles
...`) against a throwaway git repository holding a COPY of a bundle. Nothing here writes into
this repository's tracked bundles, and the last check asserts that.

Inputs:
  * GENUINE  plan-074's own B0 pour/create captures (`_shared/fixtures/gate-roles/b0-1.3.1-linked`)
             and the FILTERED plan subgraph from the same capture.
  * GENUINE  PIM H0's frozen snapshot (bundle `assets/fixtures/pim-h0`), copied: its plan.md, its
             executor-authored `execution-epic-mapping.json` and 18-node `beads.json`. The
             acceptance file the legacy path needs is SYNTHETIC — authored by this test inside its
             scratch dir and never placed in any live bundle. It is not an operator decision.
  * SYNTHETIC every refusal input, labelled at the case.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
PM = HERE / "plan_manager.py"
B0 = REPO / "_shared" / "fixtures" / "gate-roles" / "b0-1.3.1-linked"
PIM = REPO / "docs" / "plans" / "plan-074-james-dixson-4b8fe0" / "assets" / "fixtures" / "pim-h0"
LIVE_RECEIPT = REPO / "docs" / "plans" / "plan-074-james-dixson-4b8fe0" / "references" / "execution-roles.json"
P074 = "plan-074-james-dixson-4b8fe0"
P012 = "plan-012-james-dixson-d1af33"

failures: list[str] = []
skipped: list[str] = []
ran = 0


def check(name, cond, detail=""):
    global ran
    ran += 1
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        failures.append(f"{name}: {str(detail)[:600]}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_digest(root: Path) -> dict:
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*")) if p.is_file()
            and ".git" not in p.relative_to(root).parts}


def pm(cwd: Path, *args) -> tuple[int, dict]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    r = subprocess.run(["uv", "run", str(PM), "record-execution-roles", *args, "--json"],
                       cwd=str(cwd), capture_output=True, text=True, env=env, timeout=300)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        out = {"_raw": r.stdout[-400:], "_err": r.stderr[-400:]}
    return r.returncode, out


live_before = LIVE_RECEIPT.exists() and sha(LIVE_RECEIPT)
TMP = Path(tempfile.mkdtemp(prefix="yf-p074-roles-"))


FP_B0 = "8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c"


def b0_repo(name: str, unstamped: bool = False, stamp_fp: str = FP_B0) -> tuple[Path, Path]:
    """A scratch git repo holding a COPY of plan-074's bundle with the B0 captures retained under
    `assets/execution-roles/` exactly as SKILL.md §5.2a lays them out."""
    root = TMP / name
    bundle = root / "docs" / "plans" / P074
    cap = bundle / "assets" / "execution-roles"
    (cap / "creates").mkdir(parents=True)
    shutil.copy2(B0 / "plan" / "plan.md", bundle / "plan.md")
    shutil.copy2(B0 / "pour.json", cap / "pour.json")
    shutil.copy2(B0 / "gate-creates.json", cap / "gate-creates.json")
    for f in ("gate-capability.json", "gate-reconcile.json"):
        shutil.copy2(B0 / "creates" / f, cap / "creates" / f)
    # SYNTHETIC: stamp the root as new-pour linkage now does (REQ-DATA-077 DEV guard); the
    # genuine B0 root predates the guard. `unstamped=True` keeps the genuine bytes.
    g = json.loads((B0 / "plan-subgraph.list.json").read_text())
    if not unstamped:
        for n in g:
            if n["id"] == "yf-mol-9s78":
                n["metadata"] = {**(n.get("metadata") or {}), "yf_origin_fingerprint": stamp_fp}
    (root / "graph.json").write_text(json.dumps(g))
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root, bundle


BD = ["--bd-version", "bd version 1.3.1 (Homebrew)"]
B_REL = f"docs/plans/{P074}"
CAP = f"{B_REL}/assets/execution-roles"
try:
    # --- native lifecycle ---------------------------------------------------------------------
    root, bundle = b0_repo("native")
    rcpt = bundle / "references" / "execution-roles.json"
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json", *BD)
    check("start-only write from the GENUINE B0 pour -> exit 0, written", rc == 0
          and out.get("action") == "written" and out.get("state") == "start-only", out)
    r1 = json.loads(rcpt.read_text()) if rcpt.exists() else {}
    check("start-only receipt binds the native role keys to the pour's ids",
          r1.get("roles", {}).get("plan-execute.start-gate") == "yf-mol-r0p2"
          and r1.get("roles", {}).get("plan-execute.gate-start-gate") == "yf-mol-nh83"
          and r1.get("gates") == {"Start Gate (mandatory)": "yf-mol-nh83"}
          and r1.get("plan_dir") == B_REL and r1.get("evidence_kind") == "native", r1)
    s1 = sha(rcpt)
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json", *BD)
    check("identical re-run is a no-op (exit 0, unchanged, bytes identical)",
          rc == 0 and out.get("action") == "unchanged" and sha(rcpt) == s1, out)
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json",
                 "--creates", f"{CAP}/gate-creates.json", *BD)
    r2 = json.loads(rcpt.read_text())
    check("finalize from the GENUINE create outputs -> exit 0, finalized", rc == 0
          and out.get("state") == "finalized" and r2.get("state") == "finalized", out)
    check("finalized map: three declarations -> start gate, capability, reconcile (raw-derived)",
          r2.get("gates") == {"Start Gate (mandatory)": "yf-mol-nh83",
                              "Capability Gate: Explicit compatibility policy and bootstrap decisions": "yf-mol-9s78.5",
                              "Reconcile Gate": "yf-mol-9s78.6"}, r2.get("gates"))
    check("finalized evidence lists pour, index and both raw creates with digests",
          {e["path"] for e in r2.get("evidence", [])} == {
              "assets/execution-roles/pour.json", "assets/execution-roles/gate-creates.json",
              "assets/execution-roles/creates/gate-capability.json",
              "assets/execution-roles/creates/gate-reconcile.json"}, r2.get("evidence"))
    s2 = sha(rcpt)
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json", *BD)
    check("start-only after finalized -> exit 0 already-finalized, no write",
          rc == 0 and out.get("action") == "already-finalized" and sha(rcpt) == s2, out)
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json",
                 "--creates", f"{CAP}/gate-creates.json", *BD)
    check("finalized identical re-run -> unchanged", rc == 0 and out.get("action") == "unchanged"
          and sha(rcpt) == s2, out)
    # SYNTHETIC conflict: a different pour (wrapper id changed) against the existing receipt.
    alt = json.loads((bundle / "assets/execution-roles/pour.json").read_text())
    alt["id_mapping"]["plan-execute.start-gate"] = "yf-mol-zzzz"
    (bundle / "assets/execution-roles/pour-alt.json").write_text(json.dumps(alt))
    before = tree_digest(bundle)
    rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour-alt.json", *BD)
    check("SYNTHETIC conflicting pour -> non-zero, zero writes", rc != 0
          and tree_digest(bundle) == before and out.get("written") == [], out)

    # --- refusals on a fresh bundle (each asserts zero writes) --------------------------------
    def refuse(label, code, mutate, *args, graph="graph.json"):
        root, bundle = b0_repo(label.replace(" ", "-").replace("/", "-")[:40])
        mutate(root, bundle)
        before = tree_digest(root)
        rc, out = pm(root, B_REL, "--graph", graph, *args, *BD)
        check(f"{label} -> exit {code}, zero writes", rc == code and tree_digest(root) == before
              and not (bundle / "references" / "execution-roles.json").exists(), (rc, out))

    def edit_plan(*pairs):
        """Apply (old, new) replacements; `record-epic` dual-writes the Epic into BOTH the
        frontmatter and the `**Epic:**` line, so a root edit must change both."""
        def f(root, bundle):
            p = bundle / "plan.md"
            t = p.read_text()
            for old, new in zip(pairs[::2], pairs[1::2]):
                assert old in t, old
                t = t.replace(old, new, 1)
            p.write_text(t)
        return f

    nop = lambda root, bundle: None  # noqa: E731
    POUR = ("--pour", f"{CAP}/pour.json")
    refuse("SYNTHETIC stale fingerprint (plan content edited)", 1,
           edit_plan("## Objective\n", "## Objective\nEdited after approval.\n"), *POUR)
    refuse("SYNTHETIC foreign root (plan Epic differs from pour)", 1,
           edit_plan("**Epic:** yf-mol-9s78", "**Epic:** yf-mol-other",
                     "epic: yf-mol-9s78", "epic: yf-mol-other"), *POUR)
    refuse("SYNTHETIC no recorded Epic", 2,
           edit_plan("**Epic:** yf-mol-9s78\n", "", "epic: yf-mol-9s78\n", ""), *POUR)
    refuse("pour retained OUTSIDE the bundle", 1,
           lambda root, b: shutil.copy2(B0 / "pour.json", root / "pour.json"), "--pour", "pour.json")
    refuse("SYNTHETIC missing raw create output", 2,
           lambda root, b: (b / "assets/execution-roles/creates/gate-reconcile.json").unlink(),
           *POUR, "--creates", f"{CAP}/gate-creates.json")

    def bad_index(root, b):
        p = b / "assets/execution-roles/gate-creates.json"
        d = json.loads(p.read_text())
        d["Reconcile Gate"]["id"] = "yf-mol-9s78.99"
        p.write_text(json.dumps(d))
    refuse("SYNTHETIC index id disagrees with its raw output", 1, bad_index,
           *POUR, "--creates", f"{CAP}/gate-creates.json")

    def bad_pour(root, b):
        p = b / "assets/execution-roles/pour.json"
        d = json.loads(p.read_text())
        del d["id_mapping"]["plan-execute.gate-start-gate"]
        p.write_text(json.dumps(d))
    refuse("SYNTHETIC pour missing a native role key", 2, bad_pour, *POUR)
    refuse("SYNTHETIC pour is an error envelope", 2,
           lambda root, b: (b / "assets/execution-roles/pour.json").write_text('{"error": "x"}'), *POUR)
    refuse("graph file missing", 2, nop, *POUR, graph="absent.json")
    refuse("SYNTHETIC graph error envelope", 2,
           lambda root, b: (root / "g.json").write_text('{"error": "no db"}'), *POUR, graph="g.json")

    def broken_graph(root, b):
        g = json.loads((root / "graph.json").read_text())
        for n in g:
            if n["id"] == "yf-mol-r0p2":
                n["dependencies"] = [d for d in n["dependencies"] if d["type"] != "blocks"]
        (root / "graph.json").write_text(json.dumps(g))
    refuse("SYNTHETIC graph contradicts the receipt (wrapper edge removed)", 1, broken_graph, *POUR)
    refuse("--out naming a non-default path inside the bundle", 1, nop, *POUR,
           "--out", f"{B_REL}/references/other.json")
    refuse("SYNTHETIC unparsed plan construct", 2,
           edit_plan("- Issue 0.1:", "- Issue 0.1 malformed"), *POUR)
    refuse("both --pour and --import-legacy", 2, nop, *POUR, "--import-legacy", "x.json",
           "--acceptance", "y.json")

    # --- DEV origin-stamp guard on BOTH output paths (REQ-DATA-077) ----------------------------
    for label, kw, code in (("GENUINE unstamped (pre-guard) root", {"unstamped": True}, 2),
                            ("SYNTHETIC stamp from a different approval", {"stamp_fp": "0" * 64}, 1)):
        for out_args in ((), ("--out", "EXT")):
            root, bundle = b0_repo(("st-" + label[:12] + str(len(out_args))).replace(" ", "-"), **kw)
            ext = TMP / f"ext-{ran}.json"
            args = tuple(str(ext) if a == "EXT" else a for a in out_args)
            before = tree_digest(root)
            rc, out = pm(root, B_REL, "--graph", "graph.json", "--pour", f"{CAP}/pour.json", *args, *BD)
            check(f"{label}, {'--out' if out_args else 'default'} output -> exit {code}, zero writes",
                  rc == code and tree_digest(root) == before and not ext.exists()
                  and not (bundle / "references" / "execution-roles.json").exists(), (rc, out))

    # --- legacy-attested import over an immutable PIM copy -------------------------------------
    def pim_repo(name):
        root = TMP / name
        bundle = root / "docs" / "plans" / P012
        bundle.mkdir(parents=True)
        shutil.copy2(PIM / P012 / "plan.md", bundle / "plan.md")
        (bundle / "references").mkdir()
        shutil.copy2(PIM / "execution-epic-mapping.json", bundle / "references" / "execution-epic-mapping.json")
        shutil.copy2(PIM / "beads.json", root / "graph.json")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        return root, bundle

    def acceptance(bundle, **over):
        a = {"schema": "yf-plan-legacy-acceptance/v1", "plan_id": P012,
             "plan_dir": f"docs/plans/{P012}",
             "fingerprint": "2dd5d32c657cac2a4b15027285cf62f1760181494fbd3b46aa6b143aa05d2db7",
             "root": "pim-mol-vp2",
             "mapping_sha256": sha(bundle / "references" / "execution-epic-mapping.json"),
             "decision": "SYNTHETIC TEST ACCEPTANCE — not an operator decision",
             "decided_by": "test_execution_roles.py", "at": "2026-10-29T00:00:00Z"}
        a.update(over)
        return a

    MAP = f"docs/plans/{P012}/references/execution-epic-mapping.json"
    root, bundle = pim_repo("pim-ok")
    ext = TMP / "external" / "pim-roles.json"
    acc = TMP / "pim-ok-acceptance.json"
    acc.write_text(json.dumps(acceptance(bundle)))
    before = tree_digest(bundle)
    rc, out = pm(root, f"docs/plans/{P012}", "--graph", "graph.json", "--import-legacy", MAP,
                 "--acceptance", str(acc), "--out", str(ext), *BD)
    rx = json.loads(ext.read_text()) if ext.exists() else {}
    check("legacy-attested import of the GENUINE PIM mapping -> exit 0, EXTERNAL receipt",
          rc == 0 and rx.get("evidence_kind") == "legacy-attested" and rx.get("state") == "finalized", out)
    check("PIM bundle copy is byte-unchanged by an external import", tree_digest(bundle) == before)
    check("legacy receipt maps three actual gates and never the wrapper",
          rx.get("gates") == {"Start Gate (mandatory)": "pim-mol-0u3",
                              "Capability Gate: Explicit bounded policy and profile acceptance": "pim-mol-vp2.5",
                              "Reconcile Gate": "pim-mol-vp2.6"}
          and rx.get("roles", {}).get("plan-execute.start-gate") == "pim-mol-3pg", rx)
    check("legacy receipt carries no fabricated formula field and records the acceptance digest",
          "formula_sha256" not in rx and rx.get("acceptance", {}).get("sha256") == sha(acc), rx)

    def legacy_refuse(label, code, acc_over=None, mutate=None, extra=()):
        root, bundle = pim_repo("pim-" + label.split()[1][:20] + str(ran))
        if mutate:
            mutate(bundle)
        a = TMP / f"acc-{ran}.json"
        a.write_text(json.dumps(acceptance(bundle, **(acc_over or {}))) if acc_over != "unknown"
                     else json.dumps({**acceptance(bundle), "extra": 1}))
        out_p = TMP / f"ext-{ran}.json"
        before = tree_digest(bundle)
        rc, out = pm(root, f"docs/plans/{P012}", "--graph", "graph.json", "--import-legacy", MAP,
                     "--acceptance", str(a), "--out", str(out_p), *BD, *extra)
        check(f"{label} -> exit {code}, zero writes", rc == code and not out_p.exists()
              and tree_digest(bundle) == before, (rc, out))

    legacy_refuse("SYNTHETIC stale-fingerprint acceptance", 1, {"fingerprint": "0" * 64})
    legacy_refuse("SYNTHETIC foreign-plan acceptance", 1, {"plan_id": "plan-999-x-000000"})
    legacy_refuse("SYNTHETIC wrong-root acceptance", 1, {"root": "pim-mol-zzz"})
    legacy_refuse("SYNTHETIC unknown-field acceptance", 1, "unknown")
    legacy_refuse("SYNTHETIC empty-decision acceptance", 1, {"decision": " "})

    def remap(bundle):
        p = bundle / "references" / "execution-epic-mapping.json"
        d = json.loads(p.read_text())
        d["capability_gate"] = "pim-mol-vp2.6"
        p.write_text(json.dumps(d))
    # acceptance digest computed AFTER mutation would bind the new bytes; this one binds the old
    root_m, bundle_m = pim_repo("pim-digest")
    acc_m = TMP / "acc-digest.json"
    acc_m.write_text(json.dumps(acceptance(bundle_m)))
    remap(bundle_m)
    rc, out = pm(root_m, f"docs/plans/{P012}", "--graph", "graph.json", "--import-legacy", MAP,
                 "--acceptance", str(acc_m), "--out", str(TMP / "ext-digest.json"), *BD)
    check("SYNTHETIC mapping altered after acceptance -> exit 1 (digest no longer bound)",
          rc == 1 and not (TMP / "ext-digest.json").exists(), out)
    legacy_refuse("SYNTHETIC conflicting map (capability->reconcile id) -> classification refuses",
                  1, mutate=remap)
    legacy_refuse("SYNTHETIC --formula on a historical import", 1, extra=("--formula", "graph.json"))

    root, bundle = pim_repo("pim-noacc")
    rc, out = pm(root, f"docs/plans/{P012}", "--graph", "graph.json", "--import-legacy", MAP, *BD)
    check("legacy import without --acceptance -> exit 2, no receipt",
          rc == 2 and not (bundle / "references" / "execution-roles.json").exists(), out)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

check("scratch removed", not TMP.exists())
check("no receipt written into this repository's live plan-074 bundle",
      (LIVE_RECEIPT.exists() and sha(LIVE_RECEIPT)) == live_before)

if ran < 35:
    failures.append(f"only {ran} checks ran")
print(f"\n{ran} checks, {len(failures)} failure(s)" if failures else f"\n{ran} checks, all passed")
for f in failures:
    print("  " + f)
sys.exit(1 if failures else 0)

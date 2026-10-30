#!/usr/bin/env python3
"""Tier-2 driver for `gate-wrapper.sh` (plan-074 Issue 3.1, REQ-PLAN-077/087, REQ-DATA-026/077).

Runs INSIDE the sandbox the shell harness built: an owned HOME holding the MODIFIED, sandbox-
installed yf-plan skill, owned git repos and owned `bd` stores, and a `bd` shim that logs every
argv (with cwd) before exec'ing the REAL native binary and refuses any cwd outside the sandbox.

It mechanically reproduces SKILL.md §5.2a with the installed manager verbs — pour (raw output
retained), root linkage, start-only receipt, plan-DAG creates (raw outputs retained), finalized
receipt, start resolution — then judges with the installed fidelity checker. The same graphs are
also put to the OPERATOR'S CURRENTLY INSTALLED (old) resolver and checker, read-only, so "old
fails / new passes on the same native graph" is an observation, not an assumption.

Exit 0 every check passed · 1 a check failed · 2 INCONCLUSIVE (a required control could not run).
Writes a JSON report to the path given as argv[1].
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPORT = Path(sys.argv[1])
SB = Path(os.environ["YFGW_ROOT"])
SKILL = Path(os.environ["YFGW_SKILL"])
REPO_SRC = Path(os.environ["YFGW_REPO"])
OLD_SKILL = Path(os.environ["YFGW_OLD_SKILL"])
LOG = Path(os.environ["YFGW_LOG"])
BD131 = os.environ["YFGW_BD131"]
BD110 = os.environ.get("YFGW_BD110", "")
PY = os.environ["YFGW_PY"]
FIX = REPO_SRC / "_shared" / "fixtures" / "gate-roles" / "b0-1.3.1-linked" / "plan" / "plan.md"
PLAN_ID = "plan-074-james-dixson-4b8fe0"
PREL = f"docs/plans/{PLAN_ID}"
FORMULA_SHA = "792fa24f8f707be7bc46b8031053d2f5b19066b994ec592c61d76dc7af31d65c"

checks: list[dict] = []
inconclusive: list[str] = []


def check(name: str, ok: bool, detail="") -> bool:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if ok else str(detail)[:900]})
    print(("ok   " if ok else "FAIL ") + name, flush=True)
    return ok


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def env(real_bd: str, with_bd: bool = True) -> dict:
    e = dict(os.environ)
    e["YFGW_REAL_BD"] = real_bd
    if not with_bd:
        e["PATH"] = os.pathsep.join(p for p in e["PATH"].split(os.pathsep)
                                    if p != str(SB / "bin"))
    return e


def run(argv, cwd, real_bd, with_bd=True, stdin=None, timeout=600):
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, input=stdin,
                          env=env(real_bd, with_bd), timeout=timeout)


def bd(cwd, real_bd, *args, stdin=None):
    return run(["bd", *args], cwd, real_bd, stdin=stdin)


def pm(skill: Path, cwd, real_bd, *args, with_bd=True):
    # plan_manager.py declares PEP 723 deps (click, pyyaml): run it the way SKILL.md does, via
    # `uv run`, with uv's cache and python pinned by the harness (UV_CACHE_DIR inside the sandbox).
    return run(["uv", "run", "--quiet", str(skill / "scripts" / "plan_manager.py"), *args],
               cwd, real_bd, with_bd)


def jout(r):
    try:
        return json.loads(r.stdout)
    except (json.JSONDecodeError, TypeError):
        lines = (r.stdout or "").strip().splitlines()
        try:
            return json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            return {"_raw": (r.stdout or "")[-400:], "_err": (r.stderr or "")[-400:]}


def log_mark() -> int:
    return len(LOG.read_text().splitlines()) if LOG.exists() else 0


def log_since(mark: int) -> list[dict]:
    lines = LOG.read_text().splitlines() if LOG.exists() else []
    return [json.loads(x) for x in lines[mark:] if x.strip()]


def mutations(entries) -> list[list[str]]:
    out = []
    for e in entries:
        a = e["argv"]
        if a[:2] == ["gate", "resolve"] or a[:1] in (["close"], ["update"], ["create"], ["dep"],
                                                     ["batch"], ["reopen"], ["delete"]):
            out.append(a)
    return out


def show(cwd, real_bd, i) -> dict:
    d = json.loads(bd(cwd, real_bd, "show", i, "--json").stdout)
    return d[0] if isinstance(d, list) else d


def new_repo(name: str, real_bd: str) -> Path:
    root = SB / "work" / name
    root.mkdir(parents=True)
    run(["git", "init", "-q"], root, real_bd)
    run(["git", "config", "user.email", "gw@sandbox.invalid"], root, real_bd)
    run(["git", "config", "user.name", "gw-sandbox"], root, real_bd)
    r = bd(root, real_bd, "init", "--skip-hooks", "--skip-agents", "--prefix", "gw")
    if r.returncode != 0:
        raise RuntimeError(f"bd init failed: {r.stderr[-300:]}")
    bd(root, real_bd, "config", "set", "dolt.local-only", "true")
    # The UNMODIFIED native formula, from the sandbox-installed skill (staged as yf preflight does).
    fdir = root / ".beads" / "formulas"
    fdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILL / "formulas" / "plan-execute.formula.toml", fdir / "plan-execute.formula.toml")
    bundle = root / PREL
    bundle.mkdir(parents=True)
    text = FIX.read_text()
    text = "\n".join(ln for ln in text.split("\n")
                     if not ln.startswith("epic: ") and not ln.startswith("**Epic:**"))
    (bundle / "plan.md").write_text(text)
    return root


def extract(root: Path) -> dict:
    r = run([PY, str(SKILL / "scripts" / "plan_extract.py"), PREL, "--json", "--strict"], root, BD131)
    d = json.loads(r.stdout)
    return d[0] if isinstance(d, list) else d


FP_PLAN = "8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c"   # fixture plan.md


def pour_and_wire(label: str, root: Path, real_bd: str, *, full: bool = True,
                  stamp: str | None = FP_PLAN) -> dict:
    """SKILL.md §5.2a, mechanically. Returns the ids."""
    cap = root / PREL / "assets" / "execution-roles"
    (cap / "creates").mkdir(parents=True)
    r = bd(root, real_bd, "mol", "pour", "plan-execute", "--var",
           "objective=Gate-wrapper compatibility for start resolution and pour fidelity",
           "--var", f"plan_dir={PREL}", "--json")
    (cap / "pour.json").write_text(r.stdout)
    (cap / "pour.stderr").write_text(r.stderr)
    (cap / "pour-result.json").write_text(json.dumps({"exit": r.returncode}))
    check(f"[{label}] native pour exit 0 with raw output retained BEFORE id extraction",
          r.returncode == 0 and (cap / "pour.json").stat().st_size > 0, r.stderr[-300:])
    pour = json.loads(r.stdout)
    m = pour["id_mapping"]
    ids = {"root": m["plan-execute"], "wrapper": m["plan-execute.start-gate"],
           "gate": m["plan-execute.gate-start-gate"], "cap": root / PREL / "assets"}
    # SKILL.md §5.2a linkage: plan_dir + the prospective yf_origin_fingerprint (REQ-DATA-077).
    meta = {"plan_dir": PREL} if stamp is None else {"plan_dir": PREL, "yf_origin_fingerprint": stamp}
    bd(root, real_bd, "update", ids["root"], "--metadata", json.dumps(meta), "-q")
    r = pm(SKILL, root, real_bd, "record-epic", PREL, ids["root"])
    check(f"[{label}] record-epic links the root", r.returncode == 0, r.stdout + r.stderr)
    if stamp is not None and stamp != FP_PLAN:
        return ids            # guard scenario: the caller drives the refusal itself
    g = cap / "graph-start.json"
    g.write_text(bd(root, real_bd, "list", "--all", "--include-gates", "--limit", "0", "--json").stdout)
    r = pm(SKILL, root, real_bd, "record-execution-roles", PREL, "--graph", str(g), "--pour",
           f"{PREL}/assets/execution-roles/pour.json", "--json")
    if stamp is None:
        return {**ids, "_record": r}
    check(f"[{label}] start-only receipt recorded from the retained native pour",
          r.returncode == 0 and jout(r).get("state") == "start-only", r.stdout + r.stderr)
    if not full:
        return ids
    plan = extract(root)
    epic_ids, issue_ids = {}, {}
    for e in plan["epics"]:
        rr = bd(root, real_bd, "create", f"Epic: {e['name']}", f"--description=Plan: {PLAN_ID}",
                "-t", "epic", "-p", "2", "--parent", ids["root"], "--json")
        epic_ids[e["num"]] = json.loads(rr.stdout)["id"]
    for i in plan["issues"]:
        deps = ",".join(issue_ids[x] for x in i["depends_on"]) if i["depends_on"] else ids["wrapper"]
        rr = bd(root, real_bd, "create", f"Issue {i['id']}: {i['title']}",
                f"--description=Plan: {PLAN_ID} | Bundle: {PREL} (repo-relative)", "-t", "task",
                "-p", "2", "--parent", epic_ids[i["epic"]], "--deps", deps, "--metadata",
                json.dumps({"plan_issue": i["id"], "plan": PLAN_ID, "plan_dir": PREL}), "--json")
        issue_ids[i["id"]] = json.loads(rr.stdout)["id"]
    index, cap_ids = {}, {}
    for n, gd in enumerate(x for x in plan["gates"] if x["name"].startswith("Capability Gate")):
        rr = bd(root, real_bd, "create", f"Gate: {gd['name'].split(': ', 1)[1]}",
                f"--description=Condition: {gd['condition']}\nTest: {gd['test']}", "-t", "gate",
                "--parent", ids["root"], "--metadata",
                json.dumps({"gate_type": "human", "test": gd["test"], "test_class": "consent",
                            "cwd": "repo-root"}), "--json")
        (cap / "creates" / f"cap-{n}.json").write_text(rr.stdout)
        index[gd["name"]] = {"raw": f"creates/cap-{n}.json"}
        cap_ids[gd["name"]] = json.loads(rr.stdout)["id"]
    rr = bd(root, real_bd, "create", "Gate: Reconcile upstream",
            "--description=Blocks reconciliation until execution complete.", "-t", "gate",
            "--parent", ids["root"], "--json")
    (cap / "creates" / "reconcile-gate.json").write_text(rr.stdout)
    index["Reconcile Gate"] = {"raw": "creates/reconcile-gate.json"}
    rec = json.loads(rr.stdout)["id"]
    bd(root, real_bd, "create", "Reconcile: update upstream issues",
       "--description=Update upstream issues per plan dispositions.", "-t", "task", "-p", "1",
       "--parent", ids["root"], "--deps", rec, "--metadata",
       json.dumps({"agent": "agents/reconciler.md", "context": ["plan.md"]}), "--json")
    ops = "".join(f"dep add {issue_ids[b['ref']]} {cap_ids[gd['name']]}\n"
                  for gd in plan["gates"] if gd["name"] in cap_ids
                  for b in gd["blocks"] if b["kind"] == "issue")
    r = bd(root, real_bd, "batch", "-m", f"plan-{PLAN_ID} dep wiring", stdin=ops)
    check(f"[{label}] dep wiring batch exit 0", r.returncode == 0, r.stderr[-300:])
    (cap / "gate-creates.json").write_text(json.dumps(index, indent=2))
    g = cap / "graph-final.json"
    g.write_text(bd(root, real_bd, "list", "--all", "--include-gates", "--limit", "0", "--json").stdout)
    r = pm(SKILL, root, real_bd, "record-execution-roles", PREL, "--graph", str(g), "--pour",
           f"{PREL}/assets/execution-roles/pour.json", "--creates",
           f"{PREL}/assets/execution-roles/gate-creates.json", "--json")
    check(f"[{label}] finalized receipt from retained native create outputs",
          r.returncode == 0 and jout(r).get("state") == "finalized", r.stdout + r.stderr)
    ids.update(cap=cap_ids, rec=rec, issues=issue_ids, epics=epic_ids)
    return ids


def fidelity(skill: Path, root: Path, real_bd: str, tag: str):
    snap = SB / "tmp" / f"snap-{tag}.json"
    snap.write_text(bd(root, real_bd, "list", "--all", "--include-gates", "--limit", "0", "--json").stdout)
    r = run([PY, str(skill / "scripts" / "pour_fidelity.py"), str(snap), PREL, "--strict",
             "--plan", PLAN_ID, "--json"], root, real_bd)
    try:
        res = json.loads(r.stdout)["results"][0]
    except Exception:
        res = {}
    return r.returncode, res, r.stderr


def scenario(label: str, real_bd: str, wrapper_type: str):
    root = new_repo(label, real_bd)
    ver = bd(root, real_bd, "--version").stdout.strip()
    check(f"[{label}] native tool is {ver!r}", ("1.3.1" in ver) if label == "bd131" else ("1.1.0" in ver), ver)
    staged = root / ".beads" / "formulas" / "plan-execute.formula.toml"
    check(f"[{label}] unmodified native formula (sha {FORMULA_SHA[:12]}…)", sha(staged) == FORMULA_SHA, sha(staged))
    ids = pour_and_wire(label, root, real_bd)
    w = show(root, real_bd, ids["wrapper"])
    a = show(root, real_bd, ids["gate"])
    check(f"[{label}] wrapper natively typed {wrapper_type!r}, no await; actual gate await=human",
          w.get("issue_type") == wrapper_type and not w.get("await_type")
          and a.get("issue_type") == "gate" and a.get("await_type") == "human", (w, a))

    # OLD installed checker vs NEW sandbox-installed checker on the SAME native graph.
    rc_old, res_old, _ = fidelity(OLD_SKILL, root, real_bd, f"{label}-old")
    rc_new, res_new, err_new = fidelity(SKILL, root, real_bd, f"{label}-new")
    if wrapper_type == "gate":
        check(f"[{label}] OLD (pre-plan-074) fidelity FAILS the genuine gate-wrapper graph (gates 3 vs 4)",
              rc_old == 1 and res_old.get("gates") == {"plan": 3, "bd": 4}, (rc_old, res_old.get("gates")))
    else:
        check(f"[{label}] OLD (pre-plan-074) fidelity passes the task-wrapper graph (title scaffold)", rc_old == 0,
              (rc_old, res_old.get("gates")))
    check(f"[{label}] NEW sandbox-installed fidelity PASSES the same graph without retyping or dropping gates",
          rc_new == 0 and res_new.get("gates", {}).get("bd") == 3 == res_new.get("gates", {}).get("plan")
          and res_new.get("gates", {}).get("wrapper_excluded") == ids["wrapper"], (rc_new, err_new[-300:], res_new.get("gates")))
    check(f"[{label}] 8 issues / 7 edges / 4 epics", (res_new.get("issues", {}).get("bd"),
          res_new.get("edges", {}).get("bd"), res_new.get("epics", {}).get("bd")) == (8, 7, 4), res_new)

    # Refusals BEFORE resolution — each must make ZERO mutations.
    rp = root / PREL / "references" / "execution-roles.json"
    saved = rp.read_text()
    rp.unlink()
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    check(f"[{label}] resolver without a receipt -> exit 2, zero mutations",
          r.returncode == 2 and mutations(log_since(k)) == [], (r.returncode, r.stdout[-300:]))
    sw = json.loads(saved)
    sw["roles"]["plan-execute.start-gate"], sw["roles"]["plan-execute.gate-start-gate"] = ids["gate"], ids["wrapper"]
    sw["gates"]["Start Gate (mandatory)"] = ids["wrapper"]
    rp.write_text(json.dumps(sw))
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    check(f"[{label}] resolver with swapped receipt ids -> exit 1, zero mutations",
          r.returncode == 1 and mutations(log_since(k)) == [], (r.returncode, r.stdout[-300:]))
    rp.write_text(saved)
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json", with_bd=False)
    check(f"[{label}] resolver with bd absent -> exit 2, zero mutations",
          r.returncode == 2 and mutations(log_since(k)) == [], (r.returncode, r.stdout[-300:]))

    # Authorized resolution (this harness stands in for the fresh-session caller).
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    muts = mutations(log_since(k))
    check(f"[{label}] resolver -> exit 0, passed", r.returncode == 0 and jout(r).get("passed") is True,
          r.stdout[-400:] + r.stderr[-200:])
    check(f"[{label}] mutations were exactly: gate resolve <actual>, then ordinary close <wrapper>",
          [x[:3] for x in muts] == [["gate", "resolve", ids["gate"]], ["close", ids["wrapper"], "--reason"]]
          and not any("--force" in x for x in muts), muts)
    check(f"[{label}] both re-read closed on the REAL store",
          show(root, real_bd, ids["gate"])["status"] == "closed"
          and show(root, real_bd, ids["wrapper"])["status"] == "closed")
    capid = next(iter(ids["cap"].values()))
    check(f"[{label}] the human CAPABILITY gate is untouched and still open (no consent inferred)",
          show(root, real_bd, capid)["status"] == "open")
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    check(f"[{label}] idempotent re-run -> exit 0, zero mutations",
          r.returncode == 0 and mutations(log_since(k)) == [], r.stdout[-300:])
    rc, res, err = fidelity(SKILL, root, real_bd, f"{label}-after")
    check(f"[{label}] structural fidelity still 0 after resolution (roles do not change on close)",
          rc == 0, (rc, err[-300:]))
    return root, ids


def wrong_target(real_bd: str):
    """Native fact re-proved on the REAL 1.3.1 store, then the new resolver's response to it."""
    root = new_repo("bd131-wrongtarget", real_bd)
    ids = pour_and_wire("bd131-wrongtarget", root, real_bd, full=False)
    k = log_mark()
    old = pm(OLD_SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    od = jout(old)
    check("[old-resolver] OLD (pre-plan-074) resolver on genuine 1.3.1 graph: INCONCLUSIVE, "
          "passed=false (at exit 0), zero mutations",
          old.returncode == 0 and od.get("passed") is False and od.get("verdict") == "inconclusive"
          and mutations(log_since(k)) == [], (old.returncode, old.stdout[-300:]))
    r = bd(root, real_bd, "gate", "resolve", ids["wrapper"], "--reason", "HARNESS wrong-target probe")
    w, a = show(root, real_bd, ids["wrapper"]), show(root, real_bd, ids["gate"])
    check("[wrong-target] native `bd gate resolve <wrapper>` CLOSES the 1.3.1 wrapper and leaves the "
          "actual human gate OPEN", w["status"] == "closed" and a["status"] == "open", (r.returncode, w["status"], a["status"]))
    k = log_mark()
    r = pm(SKILL, root, real_bd, "resolve-start-gate", PREL, "--json")
    muts = mutations(log_since(k))
    check("[wrong-target] new resolver does not read the closed wrapper as consent: it resolves the "
          "ACTUAL gate (authorized caller) and verifies it",
          r.returncode == 0 and [x[:3] for x in muts] == [["gate", "resolve", ids["gate"]]]
          and show(root, real_bd, ids["gate"])["status"] == "closed", (r.stdout[-300:], muts))


def origin_guard(real_bd: str):
    """REQ-DATA-077 DEV guard on REAL bd: unstamped and mismatched roots are refused, zero writes."""
    root = new_repo("bd131-unstamped", real_bd)
    ids = pour_and_wire("bd131-unstamped", root, real_bd, full=False, stamp=None)
    r = ids["_record"]
    rp = root / PREL / "references" / "execution-roles.json"
    check("[origin-guard] REAL unstamped linkage: record-execution-roles -> exit 2, no receipt",
          r.returncode == 2 and not rp.exists(), (r.returncode, r.stdout[-300:]))
    root = new_repo("bd131-mismatch", real_bd)
    pour_and_wire("bd131-mismatch", root, real_bd, full=False, stamp="0" * 64)
    cap = root / PREL / "assets" / "execution-roles"
    g = cap / "graph-start.json"
    g.write_text(bd(root, real_bd, "list", "--all", "--include-gates", "--limit", "0", "--json").stdout)
    ext = SB / "tmp" / "ext-mismatch.json"
    for args, where in (((), "default"), (("--out", str(ext)), "--out")):
        r = pm(SKILL, root, real_bd, "record-execution-roles", PREL, "--graph", str(g), "--pour",
               f"{PREL}/assets/execution-roles/pour.json", *args, "--json")
        check(f"[origin-guard] REAL stamp from another approval, {where} output -> exit 1, zero writes",
              r.returncode == 1 and not (root / PREL / "references" / "execution-roles.json").exists()
              and not ext.exists(), (r.returncode, r.stdout[-300:]))


def main() -> int:
    op_before = {str(p): sha(p) for d in (OLD_SKILL,) for p in d.rglob("*.py")}
    try:
        scenario("bd131", BD131, "gate")
        wrong_target(BD131)
        origin_guard(BD131)
        if BD110:
            scenario("bd110", BD110, "task")
        else:
            inconclusive.append("bd 1.1.0 native tool unavailable (see harness provenance)")
    except Exception as e:  # an unexpected crash is INCONCLUSIVE evidence, never a pass
        import traceback
        inconclusive.append(f"driver crashed: {e!r}")
        traceback.print_exc()
    entries = [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()] if LOG.exists() else []
    outside = [e for e in entries if not e["cwd"].startswith(str(SB))]
    check("every bd call ran inside the sandbox (shim guard + log)", not outside and len(entries) > 50,
          (len(entries), outside[:3]))
    check("old-control yf-plan scripts byte-unchanged by the drive",
          {str(p): sha(p) for d in (OLD_SKILL,) for p in d.rglob("*.py")} == op_before)
    failed = [c for c in checks if not c["ok"]]
    code = 1 if failed else (2 if inconclusive else 0)
    if len(checks) < 40 and code == 0:
        inconclusive.append(f"only {len(checks)} checks ran")
        code = 2
    REPORT.write_text(json.dumps({"exit": code, "checks": checks, "failed": len(failed),
                                  "passed": sum(c["ok"] for c in checks), "selected": len(checks),
                                  "inconclusive": inconclusive, "bd_calls": len(entries)}, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())

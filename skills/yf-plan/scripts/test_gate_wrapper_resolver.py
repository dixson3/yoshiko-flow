#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""REQ-PLAN-077 (as amended by plan-074) controls for `plan_manager.py resolve-start-gate`.

Run:  uv run skills/yf-plan/scripts/test_gate_wrapper_resolver.py   (exit 0 all passed · 1 failure)

WHAT IS REAL AND WHAT IS STUBBED — stated, because the claim under test is about which bead
gets mutated:

  REAL      the verb, driven as a subprocess (`uv run plan_manager.py resolve-start-gate ...`);
            its role receipt, written by the real `record-execution-roles` verb from GENUINE
            native pour output; the graph STATES it is served (genuine B0 1.3.1 capture and
            the genuine EXP-001 1.1.0 probe, root-linked SYNTHETICALLY as labelled).
  STUB      `bd` itself: a small script put first on PATH that serves those states from a JSON
            file, applies `gate resolve`/`close` to them, and LOGS EVERY ARGV. The log is how
            "only the actual gate was resolved", "the wrapper was ordinary-closed", "never
            --force" and "zero mutations on refusal" are asserted. Real `bd` behaviour is
            exercised by the Tier-2 harness `test-harness/gate-wrapper.sh` (plan-074 Issue 3.1).
"""

from __future__ import annotations

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
FX = REPO / "_shared" / "fixtures" / "gate-roles"
B0 = FX / "b0-1.3.1-linked"
P074 = "plan-074-james-dixson-4b8fe0"
B_REL = f"docs/plans/{P074}"

failures: list[str] = []
ran = 0


def check(name, cond, detail=""):
    global ran
    ran += 1
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        failures.append(f"{name}: {str(detail)[:700]}")


FAKE_BD = r'''#!/usr/bin/env python3
import json, os, sys
state_p, log_p = os.environ["FAKEBD_STATE"], os.environ["FAKEBD_LOG"]
fail = set(filter(None, os.environ.get("FAKEBD_FAIL", "").split(",")))
a = sys.argv[1:]
with open(log_p, "a") as f:
    f.write(json.dumps(a) + "\n")
st = json.load(open(state_p))
by = {n["id"]: n for n in st}
def save():
    json.dump(st, open(state_p, "w"))
if a[:1] == ["--version"]:
    print("bd version 1.3.1 (stub)"); sys.exit(0)
if a[:1] == ["list"]:
    if "list" in fail: print("boom", file=sys.stderr); sys.exit(1)
    if "list-error" in fail: print(json.dumps({"error": "database locked"})); sys.exit(0)
    if "list-truncated" in fail: print('[{"id": '); sys.exit(0)
    print(json.dumps(st)); sys.exit(0)
if a[:1] == ["show"]:
    if "show" in fail: sys.exit(1)
    n = by.get(a[1])
    if n is None: print(json.dumps({"error": "not found"})); sys.exit(1)
    print(json.dumps([n])); sys.exit(0)
if a[:2] == ["gate", "resolve"]:
    if "gate-resolve" in fail: print("cannot resolve", file=sys.stderr); sys.exit(1)
    if "gate-resolve-noop" in fail: sys.exit(0)
    by[a[2]]["status"] = "closed"; save(); sys.exit(0)
if a[:1] == ["close"]:
    if "close" in fail: print("cannot close", file=sys.stderr); sys.exit(1)
    by[a[1]]["status"] = "closed"
    if "--reason" in a: by[a[1]]["close_reason"] = a[a.index("--reason") + 1]
    save(); sys.exit(0)
print("stub bd: unsupported " + " ".join(a), file=sys.stderr); sys.exit(2)
'''

TMP = Path(tempfile.mkdtemp(prefix="yf-p074-resolver-"))
BIN = TMP / "bin"
BIN.mkdir()
(BIN / "bd").write_text(FAKE_BD)
(BIN / "bd").chmod(0o755)
UV = shutil.which("uv")
GIT = shutil.which("git")


def env_for(state: Path, log: Path, fail="", with_bd=True):
    path = [str(BIN)] if with_bd else []
    path += [str(Path(UV).parent), str(Path(GIT).parent), "/usr/bin", "/bin"]
    e = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "PATH")}
    e.update(PATH=os.pathsep.join(dict.fromkeys(path)), FAKEBD_STATE=str(state),
             FAKEBD_LOG=str(log), FAKEBD_FAIL=fail)
    return e


FP_B0 = "8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c"


def make_case(name, *, ver="1.3.1", mutate_state=None, receipt=True, stamped=True):
    """Scratch repo + plan bundle + state file. Receipt written by the REAL verb from the GENUINE
    pour. Returns (root, state_path)."""
    root = TMP / name
    bundle = root / B_REL
    cap = bundle / "assets" / "execution-roles"
    cap.mkdir(parents=True)
    plan = (B0 / "plan" / "plan.md").read_text()
    if ver == "1.3.1":
        shutil.copy2(B0 / "pour.json", cap / "pour.json")
        state = json.loads((B0 / "plan-subgraph.list.json").read_text())
        root_id = "yf-mol-9s78"
    else:
        d = FX / "native-1.1.0"
        shutil.copy2(d / "pour.stdout", cap / "pour.json")
        root_id = json.loads((d / "pour.stdout").read_text())["new_epic_id"]
        state = json.loads((d / "list.stdout").read_text())
        for n in state:                       # SYNTHETIC: the yf root linkage EXP-001 omitted
            if n["id"] == root_id:
                n["metadata"] = {"plan_dir": B_REL}
        plan = plan.replace("epic: yf-mol-9s78", f"epic: {root_id}").replace(
            "**Epic:** yf-mol-9s78", f"**Epic:** {root_id}")
    (bundle / "plan.md").write_text(plan)
    if stamped:   # SYNTHETIC: the yf_origin_fingerprint new-pour linkage now writes (REQ-DATA-077)
        for n in state:
            if n["id"] == root_id:
                n["metadata"] = {**(n.get("metadata") or {}), "yf_origin_fingerprint": FP_B0}
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    sp = root / "state.json"
    sp.write_text(json.dumps(state))
    if receipt:
        r = subprocess.run([UV, "run", str(PM), "record-execution-roles", B_REL, "--graph",
                            str(sp), "--pour", f"{B_REL}/assets/execution-roles/pour.json",
                            "--bd-version", f"bd version {ver}", "--json"], cwd=root,
                           capture_output=True, text=True, env=env_for(sp, root / "rec.log"))
        assert r.returncode == 0, r.stdout + r.stderr
    if mutate_state:
        st = json.loads(sp.read_text())
        mutate_state(st)
        sp.write_text(json.dumps(st))
    return root, sp


def resolve(root, sp, fail="", with_bd=True):
    log = root / f"bd-{ran}.log"
    log.write_text("")
    r = subprocess.run([UV, "run", str(PM), "resolve-start-gate", B_REL, "--json"], cwd=root,
                       capture_output=True, text=True, env=env_for(sp, log, fail, with_bd),
                       timeout=300)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = {"_raw": r.stdout[-500:], "_err": r.stderr[-500:]}
    calls = [json.loads(ln) for ln in log.read_text().splitlines() if ln.strip()]
    return r.returncode, out, calls


def mutations(calls):
    return [c for c in calls if c[:2] == ["gate", "resolve"] or c[:1] == ["close"]]


def status(sp, i):
    return next(n for n in json.loads(sp.read_text()) if n["id"] == i)["status"]


W, G = "yf-mol-r0p2", "yf-mol-nh83"
try:
    # --- genuine 1.3.1 gate-typed wrapper -----------------------------------------------------
    root, sp = make_case("b0")
    rc, out, calls = resolve(root, sp)
    m = mutations(calls)
    check("1.3.1 gate-typed wrapper: exit 0, passed", rc == 0 and out.get("passed") is True, out)
    check("only the ACTUAL gate is gate-resolved, then the wrapper is ordinary-closed",
          [c[:3] for c in m] == [["gate", "resolve", G], ["close", W, "--reason"]], m)
    check("the wrapper is never `gate resolve`d and nothing uses --force",
          not any(c[:3] == ["gate", "resolve", W] for c in calls)
          and not any("--force" in c for c in calls), calls)
    check("both re-read terminal and reported as observed",
          status(sp, G) == "closed" and status(sp, W) == "closed"
          and out.get("observed") == {"gate": "closed", "wrapper": "closed"}, out)
    check("graph acquired complete (list --all --include-gates --limit 0)",
          any(c[:1] == ["list"] and "--include-gates" in c and "--all" in c for c in calls), calls)
    rc, out, calls = resolve(root, sp)
    check("idempotent re-run: exit 0, zero mutations",
          rc == 0 and mutations(calls) == []
          and out.get("actions") == ["gate-already-resolved", "wrapper-already-closed"], out)

    # --- genuine 1.1.0 task wrapper -----------------------------------------------------------
    root, sp = make_case("v110", ver="1.1.0")
    p = json.loads((FX / "native-1.1.0" / "pour.stdout").read_text())["id_mapping"]
    rc, out, calls = resolve(root, sp)
    check("1.1.0 task wrapper: exit 0 and the same actual-gate-only order",
          rc == 0 and [c[:3] for c in mutations(calls)] ==
          [["gate", "resolve", p["plan-execute.gate-start-gate"]],
           ["close", p["plan-execute.start-gate"], "--reason"]], (out, calls))

    # --- false-consent control: pre-closed wrapper over an OPEN human gate --------------------
    def preclose(st):
        for n in st:
            if n["id"] == W:
                n["status"] = "closed"
    root, sp = make_case("preclosed", mutate_state=preclose)
    rc, out, calls = resolve(root, sp)
    check("pre-closed wrapper is NOT treated as a discharged pair: the open actual gate is "
          "resolved (authorized caller) and verified",
          rc == 0 and [c[:3] for c in mutations(calls)] == [["gate", "resolve", G]]
          and out.get("actions") == ["gate-resolved", "wrapper-already-closed"]
          and status(sp, G) == "closed", (out, calls))

    # --- refusals: zero mutations --------------------------------------------------------------
    def refused(label, root, sp, code, fail="", with_bd=True):
        before = sp.read_text()
        rc, out, calls = resolve(root, sp, fail, with_bd)
        check(f"{label} -> exit {code}, passed=false, ZERO mutations",
              rc == code and out.get("passed") is False and mutations(calls) == []
              and sp.read_text() == before, (rc, out, calls))
        return out

    root, sp = make_case("unstamped", stamped=False, receipt=False)
    rp = root / B_REL / "references"
    rp.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TMP / "b0" / B_REL / "references" / "execution-roles.json", rp / "execution-roles.json")
    refused("GENUINE unstamped (pre-guard) root with a native receipt", root, sp, 2)

    root, sp = make_case("noreceipt", receipt=False)
    refused("no role receipt (no title fallback)", root, sp, 2)

    def lookalike(st):   # SYNTHETIC: a copied Begin/Gate pair beside the real one
        st.append({"id": "yf-x1", "issue_type": "task", "status": "open", "title": "Begin: copy",
                   "parent": "yf-mol-9s78", "dependencies": [
                       {"issue_id": "yf-x1", "depends_on_id": "yf-mol-9s78", "type": "parent-child"},
                       {"issue_id": "yf-x1", "depends_on_id": "yf-x2", "type": "blocks"}]})
        st.append({"id": "yf-x2", "issue_type": "gate", "status": "open", "title": "Gate: human",
                   "await_type": "human", "parent": "yf-mol-9s78", "dependencies": [
                       {"issue_id": "yf-x2", "depends_on_id": "yf-mol-9s78", "type": "parent-child"}]})
    root, sp = make_case("lookalike", mutate_state=lookalike)
    refused("SYNTHETIC competing lookalike pair", root, sp, 1)

    def masquerade(st):  # SYNTHETIC: actual gate retyped task
        for n in st:
            if n["id"] == G:
                n["issue_type"] = "task"
    root, sp = make_case("masq", mutate_state=masquerade)
    refused("SYNTHETIC actual gate masquerading as task", root, sp, 1)

    root, sp = make_case("swapped")
    rp = root / B_REL / "references" / "execution-roles.json"
    r = json.loads(rp.read_text())
    r["roles"]["plan-execute.start-gate"], r["roles"]["plan-execute.gate-start-gate"] = G, W
    r["gates"]["Start Gate (mandatory)"] = W
    rp.write_text(json.dumps(r))
    out = refused("SYNTHETIC swapped receipt ids (wrong-target prevention)", root, sp, 1)

    root, sp = make_case("stale")
    pmd = root / B_REL / "plan.md"
    pmd.write_text(pmd.read_text().replace("## Objective\n", "## Objective\nChanged.\n", 1))
    refused("SYNTHETIC stale fingerprint", root, sp, 1)

    root, sp = make_case("noepic")
    pmd = root / B_REL / "plan.md"
    pmd.write_text(pmd.read_text().replace("epic: yf-mol-9s78\n", "").replace("**Epic:** yf-mol-9s78\n", ""))
    refused("no **Epic:** root", root, sp, 2)

    root, sp = make_case("clierr")
    refused("bd list exits non-zero", root, sp, 2, fail="list")
    refused("bd list error envelope at exit 0", root, sp, 2, fail="list-error")
    refused("bd list truncated JSON", root, sp, 2, fail="list-truncated")
    refused("bd absent from PATH", root, sp, 2, with_bd=False)

    # --- partial mutation and recovery ---------------------------------------------------------
    root, sp = make_case("partial")
    rc, out, calls = resolve(root, sp, fail="close")
    check("partial: gate resolved, wrapper close fails -> exit 1 with explicit-id recovery",
          rc == 1 and out.get("passed") is False and status(sp, G) == "closed"
          and status(sp, W) == "open" and any(W in s and "--force" not in s.split("(")[0]
                                              for s in out.get("recovery", []))
          and any(G in s for s in out.get("recovery", [])), out)
    rc, out, calls = resolve(root, sp)
    check("recovery re-run: closes the wrapper only, exit 0",
          rc == 0 and [c[:2] for c in mutations(calls)] == [["close", W]], (out, calls))

    root, sp = make_case("gatefail")
    rc, out, calls = resolve(root, sp, fail="gate-resolve")
    check("actual gate resolve fails -> exit 1, wrapper untouched",
          rc == 1 and status(sp, W) == "open"
          and not any(c[:1] == ["close"] for c in calls), (out, calls))
    root, sp = make_case("noop")
    rc, out, calls = resolve(root, sp, fail="gate-resolve-noop")
    check("gate resolve exits 0 but the gate re-reads open -> exit 1, wrapper NOT closed",
          rc == 1 and status(sp, W) == "open"
          and not any(c[:1] == ["close"] for c in calls), (out, calls))
finally:
    shutil.rmtree(TMP, ignore_errors=True)

check("scratch removed", not TMP.exists())
if ran < 20:
    failures.append(f"only {ran} checks ran")
print(f"\n{ran} checks, {len(failures)} failure(s)" if failures else f"\n{ran} checks, all passed")
for f in failures:
    print("  " + f)
sys.exit(1 if failures else 0)

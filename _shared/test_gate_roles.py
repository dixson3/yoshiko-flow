#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""REQ-PLAN-087 controls for `_shared/gate_roles.py` (plan-074 Issue 1.1, #417).

Run:  uv run _shared/test_gate_roles.py      (exit 0 all passed · 1 a check failed)

EVIDENCE LABELS — every case states what it is, because the point of the module is that a
same-topology graph is NOT native evidence:

  GENUINE   bytes captured from a real native `bd` run, retained byte-exact under
            `_shared/fixtures/gate-roles/` (see PROVENANCE.json + SHA256SUMS there).
  FILTERED  genuine node objects selected by id from a genuine snapshot; values unchanged.
  DERIVED   a receipt computed from genuine captures (what `record-execution-roles` does).
  SYNTHETIC an explicit mutation of genuine input, made in memory to exercise a refusal.

The `native-1.x` probes were poured by EXP-001 WITHOUT yf's root linkage step, so their roots
carry no `plan_dir`; classifying them as-is is INCONCLUSIVE by design. Their bound positives add
that one field and are labelled SYNTHETIC accordingly. The B0 capture is the fully linked
genuine 1.3.1 graph from plan-074's own execution pour.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures" / "gate-roles"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gr = _load("gate_roles")
pe = _load("plan_extract")

failures: list[str] = []
ran = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global ran
    ran += 1
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        failures.append(f"{name}: {detail}")


def jload(p: Path):
    return json.loads(p.read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- 0. fixture integrity -------------------------------------------------------------------
sums = (FX / "SHA256SUMS").read_text().splitlines()
bad = [ln for ln in sums if ln.strip() and sha(FX / ln.split("  ", 1)[1]) != ln.split("  ", 1)[0]]
check("fixtures: every retained file matches SHA256SUMS", not bad and len(sums) >= 30, str(bad))

# --- B0 genuine linked 1.3.1 ------------------------------------------------------------------
B0 = FX / "b0-1.3.1-linked"
PLAN = pe.extract(B0 / "plan" / "plan.md")
PLAN_ID = "plan-074-james-dixson-4b8fe0"
FPR = "8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c"
PDIR = "docs/plans/plan-074-james-dixson-4b8fe0"
POUR = jload(B0 / "pour.json")
ROOT = POUR["new_epic_id"]
WRAP = POUR["id_mapping"][gr.ROLE_WRAPPER]
GATE = POUR["id_mapping"][gr.ROLE_GATE]
CREATES = jload(B0 / "gate-creates.json")
SUB_RAW = jload(B0 / "plan-subgraph.list.json")          # FILTERED, genuine bytes (pre-guard root)
SHOWS_RAW = [jload(B0 / f)[0] for f in ("root-show.json", "wrapper-show.json", "gate-show.json")]


def stamp(records, root, fp="8c5b67da2c5640331746e67a1ae718c4602867079ef75a89190f848d0aa9f85c"):
    """SYNTHETIC: add the prospective `yf_origin_fingerprint` that new-pour linkage now writes
    (REQ-DATA-077 DEV guard). The genuine B0 root predates the guard and carries none."""
    out = copy.deepcopy(records)
    for r in out:
        if r["id"] == root:
            r["metadata"] = {**(r.get("metadata") or {}), "yf_origin_fingerprint": fp}
    return out


SUB = stamp(SUB_RAW, "yf-mol-9s78")
SHOWS = stamp(SHOWS_RAW, "yf-mol-9s78")
CAP_DECL = next(g["name"] for g in PLAN["gates"] if g["name"].startswith("Capability Gate"))
CAP, REC = CREATES[CAP_DECL]["id"], CREATES["Reconcile Gate"]["id"]
EVID = ["pour.json", "gate-creates.json", "creates/gate-capability.json", "creates/gate-reconcile.json"]


def receipt(state="finalized", **over):
    """DERIVED: the receipt record-execution-roles computes from the genuine B0 captures."""
    r = {
        "schema": gr.SCHEMA, "plan_id": PLAN_ID, "fingerprint": FPR, "plan_dir": PDIR,
        "root": ROOT, "bd_version": "bd version 1.3.1 (Homebrew)", "evidence_kind": "native",
        "evidence": [{"path": p, "sha256": sha(B0 / p)} for p in EVID],
        "state": state,
        "roles": {k: POUR["id_mapping"][k] for k in gr.ROLE_KEYS},
        "gates": ({"Start Gate (mandatory)": GATE, CAP_DECL: CAP, "Reconcile Gate": REC}
                  if state == "finalized" else {"Start Gate (mandatory)": GATE}),
    }
    r.update(over)
    return r


def run(records, rcpt="default", **kw):
    args = dict(plan=PLAN, plan_id=PLAN_ID, fingerprint=FPR, plan_dir=PDIR, recorded_root=ROOT,
                records=records, receipt=receipt() if rcpt == "default" else rcpt)
    args.update(kw)
    return gr.classify(**args)


def mutate(records, nid, fn):
    out = copy.deepcopy(records)
    for r in out:
        if r["id"] == nid:
            fn(r)
    return out


check("plan fixture extracts with no unparsed constructs and records the B0 root",
      PLAN["unparsed"] == [] and PLAN["epic_bead"] == ROOT and PLAN["fingerprint"] == FPR)

v = run(SUB, evidence_base=B0)
check("GENUINE 1.3.1 linked list shape + DERIVED finalized receipt -> pass",
      v["verdict"] == "pass" and v["wrapper"] == WRAP and v["gate"] == GATE, str(v))
check("pass names the evidence source", v["evidence_source"] == "native")
v = run(SHOWS, rcpt=receipt("start-only"), evidence_base=B0)
check("GENUINE 1.3.1 linked show shape + start-only receipt -> pass", v["verdict"] == "pass", str(v))
v = run(SUB + SHOWS)
check("GENUINE list+show mix of the same nodes -> pass", v["verdict"] == "pass", str(v))
v = run(SHOWS, rcpt=receipt("start-only"), require_final=True)
check("start-only receipt where finalized is required -> inconclusive", v["verdict"] == "inconclusive")

# normalization equivalence
gl, gs = gr.normalize(SUB), gr.normalize(SHOWS)
check("list and show shapes normalize to the same wrapper edges",
      gl.out(WRAP) == gs.out(WRAP) == {(WRAP, GATE, "blocks")}, f"{gl.out(WRAP)} {gs.out(WRAP)}")


# --- native probes (1.1.0 task wrapper, 1.3.1 gate wrapper), open and resolved ---------------
def probe(ver):
    d = FX / f"native-{ver}"
    pour = jload(d / "pour.stdout")
    m = pour["id_mapping"]
    plan = copy.deepcopy(PLAN)
    plan["epic_bead"] = m[gr.ROLE_ROOT]
    rc = receipt("start-only", root=m[gr.ROLE_ROOT], roles={k: m[k] for k in gr.ROLE_KEYS},
                 gates={"Start Gate (mandatory)": m[gr.ROLE_GATE]},
                 bd_version=(d / "version.stdout").read_text().strip(),
                 evidence=[{"path": "pour.stdout", "sha256": sha(d / "pour.stdout")}])
    return d, m, plan, rc


def link(records, root):
    """SYNTHETIC: add only the yf root linkage (`metadata.plan_dir`) EXP-001 did not perform."""
    return mutate(records, root, lambda r: r.update(metadata={"plan_dir": PDIR,
                                                              "yf_origin_fingerprint": FPR}))


for ver, wtype in (("1.1.0", "task"), ("1.3.1", "gate")):
    d, m, plan, rc = probe(ver)
    root = m[gr.ROLE_ROOT]
    kw = dict(plan=plan, recorded_root=root, rcpt=rc)
    for f, state in (("list.stdout", "open"), ("final-list.stdout", "resolved")):
        recs = jload(d / f)
        types = {r["id"]: r.get("issue_type") for r in recs}
        check(f"GENUINE {ver}: wrapper is natively typed {wtype}", types[m[gr.ROLE_WRAPPER]] == wtype)
        v = run(recs, **kw, evidence_base=d)
        check(f"GENUINE {ver} {state} unlinked probe -> inconclusive (no root plan_dir)",
              v["verdict"] == "inconclusive", str(v))
        v = run(link(recs, root), **kw, evidence_base=d)
        check(f"SYNTHETIC-linked GENUINE {ver} {state} list -> pass", v["verdict"] == "pass", str(v))
    shows = [jload(d / f)[0] for f in ("show-root.stdout", "show-wrapper.stdout", "show-gate.stdout")]
    v = run(link(shows, root), **kw)
    check(f"SYNTHETIC-linked GENUINE {ver} show shape -> pass", v["verdict"] == "pass", str(v))

    # FALSE-CONSENT CONTROL (GENUINE): `bd gate resolve <wrapper>`. On 1.3.1 it CLOSED the
    # gate-typed wrapper while the actual human gate stayed OPEN.
    after_w = jload(d / "resolve-wrapper-wrapper.stdout")[0]
    after_g = jload(d / "resolve-wrapper-gate.stdout")[0]
    if ver == "1.3.1":
        check("GENUINE 1.3.1: wrong-target resolve closed the wrapper, actual gate still open",
              after_w["status"] == "closed" and after_g["status"] == "open",
              f"{after_w['status']} {after_g['status']}")
    wp = jload(d / "resolve-wrapper-pour.stdout")["id_mapping"]
    _, _, plan2, _ = probe(ver)
    plan2["epic_bead"] = wp[gr.ROLE_ROOT]
    rc2 = copy.deepcopy(rc)
    rc2.update(root=wp[gr.ROLE_ROOT], roles={k: wp[k] for k in gr.ROLE_KEYS},
               gates={"Start Gate (mandatory)": wp[gr.ROLE_GATE]})
    rshow = {"id": wp[gr.ROLE_ROOT], "issue_type": "molecule", "status": "open",
             "title": "plan-execute", "metadata": {"plan_dir": PDIR, "yf_origin_fingerprint": FPR},
             "dependencies": []}
    v = run([rshow, after_w, after_g], plan=plan2, recorded_root=wp[gr.ROLE_ROOT], rcpt=rc2)
    check(f"closed wrapper over OPEN human gate ({ver}): roles classify, but nothing reads as consent",
          v["verdict"] == "pass" and after_g["status"] == "open"
          and not any(k in v for k in ("discharged", "consent", "resolved", "passed")), str(v))

# --- DEV origin-stamp guard (REQ-DATA-077) ---------------------------------------------------
v = run(SUB_RAW)
check("GENUINE unstamped (pre-guard) B0 root, native receipt -> inconclusive",
      v["verdict"] == "inconclusive" and any("yf_origin_fingerprint" in d for d in v["diagnostics"]), str(v))
check("GENUINE unstamped B0 show shape -> inconclusive",
      run(SHOWS_RAW, rcpt=receipt("start-only"))["verdict"] == "inconclusive")
check("SYNTHETIC stamp from a DIFFERENT approval -> fail",
      run(stamp(SUB_RAW, "yf-mol-9s78", "0" * 64))["verdict"] == "fail")
check("SYNTHETIC empty stamp -> inconclusive",
      run(stamp(SUB_RAW, "yf-mol-9s78", ""))["verdict"] == "inconclusive")
_leg = receipt(evidence_kind="legacy-attested", acceptance={"sha256": "0" * 64, "decision": "SYNTHETIC",
                                                              "decided_by": "test", "at": "x"})
check("legacy-attested receipt on the unstamped root is NOT subject to the native stamp guard",
      run(SUB_RAW, rcpt=_leg)["verdict"] == "pass")

# --- R1: duplicate same-id records must agree on binding metadata, ORDER-INDEPENDENT ----------
_root_good = next(r for r in SUB if r["id"] == "yf-mol-9s78")
_root_bad = copy.deepcopy(_root_good)
_root_bad["metadata"]["yf_origin_fingerprint"] = "0" * 64
_root_nostamp = copy.deepcopy(_root_good)
del _root_nostamp["metadata"]["yf_origin_fingerprint"]
_root_otherdir = copy.deepcopy(_root_good)
_root_otherdir["metadata"]["plan_dir"] = "docs/plans/elsewhere"
for label, extra in (("conflicting stamp", _root_bad), ("stamp present vs absent", _root_nostamp),
                     ("conflicting plan_dir", _root_otherdir)):
    a = run(SUB + [extra])                     # good record first, conflicting duplicate appended
    b = run([extra] + SUB)                     # conflicting duplicate first
    check(f"R1 SYNTHETIC duplicate root, {label}: good-first -> inconclusive", a["verdict"] == "inconclusive", str(a))
    check(f"R1 SYNTHETIC duplicate root, {label}: bad-first -> inconclusive", b["verdict"] == "inconclusive", str(b))
check("R1 agreeing duplicate root records (list + identical copy) still pass",
      run(SUB + [copy.deepcopy(_root_good)])["verdict"] == "pass")
check("R1 agreeing list + show of the same nodes still pass", run(SUB + SHOWS)["verdict"] == "pass")

# --- binding adversaries (SYNTHETIC) ---------------------------------------------------------
check("copied topology with NO receipt -> inconclusive", run(SUB, rcpt=None)["verdict"] == "inconclusive")
for label, over in (("foreign plan", {"plan_id": "plan-999-x-000000"}),
                    ("stale fingerprint", {"fingerprint": "0" * 64}),
                    ("foreign bundle", {"plan_dir": "docs/plans/elsewhere"}),
                    ("wrong root", {"root": "yf-mol-zzzz"})):
    check(f"receipt {label} -> fail", run(SUB, rcpt=receipt(**over))["verdict"] == "fail")
check("recorded root differs from receipt root -> fail",
      run(SUB, recorded_root="yf-mol-other")["verdict"] == "fail")
check("no recorded root -> inconclusive", run(SUB, recorded_root=None)["verdict"] == "inconclusive")
check("plan without a fingerprint -> inconclusive even when the receipt also carries none",
      run(SUB, fingerprint=None, rcpt=receipt(fingerprint=None))["verdict"] == "inconclusive")
bad_ev = receipt()
bad_ev["evidence"][0]["sha256"] = "f" * 64
check("altered evidence digest -> fail", run(SUB, rcpt=bad_ev, evidence_base=B0)["verdict"] == "fail")
miss_ev = receipt()
miss_ev["evidence"].append({"path": "absent.json", "sha256": "0" * 64})
check("missing evidence file -> inconclusive",
      run(SUB, rcpt=miss_ev, evidence_base=B0)["verdict"] == "inconclusive")
esc_ev = receipt()
esc_ev["evidence"].append({"path": "../../../../etc/hosts", "sha256": "0" * 64})
check("evidence path escaping the bundle -> fail",
      run(SUB, rcpt=esc_ev, evidence_base=B0)["verdict"] == "fail")
swapped = receipt()
swapped["roles"] = {gr.ROLE_ROOT: ROOT, gr.ROLE_WRAPPER: GATE, gr.ROLE_GATE: WRAP}
swapped["gates"]["Start Gate (mandatory)"] = WRAP
check("swapped wrapper/gate ids with consistent map -> fail", run(SUB, rcpt=swapped)["verdict"] == "fail",
      str(run(SUB, rcpt=swapped)))
sw2 = receipt(roles={gr.ROLE_ROOT: ROOT, gr.ROLE_WRAPPER: GATE, gr.ROLE_GATE: WRAP})
check("swapped role ids, gate map kept -> not pass", run(SUB, rcpt=sw2)["verdict"] in ("fail", "inconclusive"))
rep = receipt(roles={gr.ROLE_ROOT: ROOT, gr.ROLE_WRAPPER: WRAP, gr.ROLE_GATE: WRAP})
check("repeated role id -> inconclusive (invalid receipt)", run(SUB, rcpt=rep)["verdict"] == "inconclusive")
dup = receipt()
dup["gates"][CAP_DECL] = REC
check("gate map repeats an id -> inconclusive", run(SUB, rcpt=dup)["verdict"] == "inconclusive")
check("start declaration mapped to a capability gate -> fail",
      run(SUB, rcpt=receipt(gates={"Start Gate (mandatory)": CAP, CAP_DECL: GATE, "Reconcile Gate": REC}))
      ["verdict"] == "fail")
for label, over in (("unknown schema", {"schema": "yf-plan-execution-roles/v9"}),
                    ("unknown state", {"state": "partial"}),
                    ("unknown evidence kind", {"evidence_kind": "inferred"})):
    check(f"{label} -> inconclusive", run(SUB, rcpt=receipt(**over))["verdict"] == "inconclusive")
uf = receipt()
uf["extra"] = 1
check("unknown receipt field -> inconclusive", run(SUB, rcpt=uf)["verdict"] == "inconclusive")
part = receipt()
del part["roles"]
check("partial receipt (no roles) -> inconclusive", run(SUB, rcpt=part)["verdict"] == "inconclusive")
check("legacy-attested without acceptance -> inconclusive",
      run(SUB, rcpt=receipt(evidence_kind="legacy-attested"))["verdict"] == "inconclusive")
up = copy.deepcopy(PLAN)
up["unparsed"] = [{"line": 1, "reason": "x", "raw": "x"}]
check("plan with unparsed constructs -> inconclusive", run(SUB, plan=up)["verdict"] == "inconclusive")


# --- structural adversaries (SYNTHETIC mutations of the FILTERED genuine subgraph) ------------
def edge_list(r):
    return r.setdefault("dependencies", [])


def add_edge(r, to, ty):
    edge_list(r).append({"issue_id": r["id"], "depends_on_id": to, "type": ty})


def drop_edges(r, to=None, ty=None):
    r["dependencies"] = [d for d in edge_list(r)
                         if not ((to is None or d["depends_on_id"] == to) and (ty is None or d["type"] == ty))]


def node(nid, ty, parent=ROOT, title="", **kw):
    r = {"id": nid, "issue_type": ty, "status": "open", "title": title, "parent": parent,
         "dependencies": [{"issue_id": nid, "depends_on_id": parent, "type": "parent-child"}]}
    r.update(kw)
    return r


S = SUB
check("arbitrary Begin title on the real wrapper changes nothing -> pass",
      run(mutate(S, WRAP, lambda r: r.update(title="Something else")))["verdict"] == "pass")
check("an extra Begin-titled TASK lookalike (no gate edge) is not a wrapper -> pass",
      run(S + [node("yf-x1", "task", title="Begin: lookalike")])["verdict"] == "pass")
look = S + [node("yf-x1", "task", title="Begin: lookalike"),
            node("yf-x2", "gate", title="Gate: human", await_type="human")]
add_edge(look[-2], "yf-x2", "blocks")
check("copied lookalike pair beside the real one -> fail (competing pair)",
      run(look)["verdict"] == "fail")
# Under a START-ONLY receipt the finalized identity check does not run, so only the
# competing-pair predicate can refuse the lookalike here.
lv = run(look, rcpt=receipt("start-only"))
check("lookalike pair under a start-only receipt -> fail via the competing-pair predicate",
      lv["verdict"] == "fail" and any("competing" in d for d in lv["diagnostics"]), str(lv))
lg = S + [node("yf-x6", "gate", title="Gate: human", await_type="human")]
lgv = run(lg, rcpt=receipt("start-only"))
check("unmapped extra HUMAN gate under a start-only receipt -> fail",
      lgv["verdict"] == "fail" and any("competing human gate" in d for d in lgv["diagnostics"]), str(lgv))
check("unmapped Begin-titled extra GATE -> fail (unmapped observed gate)",
      run(S + [node("yf-x3", "gate", title="Begin: x")])["verdict"] == "fail")
check("conflicting parents (field vs edge) -> fail",
      run(mutate(S, WRAP, lambda r: r.update(parent=CAP)))["verdict"] == "fail")
check("wrapper not a direct sibling (reparented under an epic) -> fail",
      run(mutate(S, WRAP, lambda r: (r.update(parent=f"{ROOT}.1"),
                                      drop_edges(r, ty="parent-child"),
                                      add_edge(r, f"{ROOT}.1", "parent-child"))))["verdict"] == "fail")
check("actual gate masquerading as task -> fail",
      run(mutate(S, GATE, lambda r: r.update(issue_type="task")))["verdict"] == "fail")
check("wrapper typed epic -> fail", run(mutate(S, WRAP, lambda r: r.update(issue_type="epic")))["verdict"] == "fail")
check("await semantics on the wrapper -> fail",
      run(mutate(S, WRAP, lambda r: r.update(await_type="human")))["verdict"] == "fail")
check("wrong actual await type -> fail",
      run(mutate(S, GATE, lambda r: r.update(await_type="timer")))["verdict"] == "fail")
check("missing wrapper->gate edge -> fail",
      run(mutate(S, WRAP, lambda r: drop_edges(r, to=GATE)))["verdict"] == "fail")
check("extra wrapper blocking dependency -> fail",
      run(mutate(S, WRAP, lambda r: add_edge(r, CAP, "blocks")))["verdict"] == "fail")
rev = mutate(mutate(S, WRAP, lambda r: drop_edges(r, to=GATE)), GATE, lambda r: add_edge(r, WRAP, "blocks"))
check("reversed wrapper edge -> fail", run(rev)["verdict"] == "fail")
check("related edge substituted for blocks -> fail",
      run(mutate(S, WRAP, lambda r: (drop_edges(r, to=GATE), add_edge(r, GATE, "related"))))["verdict"] == "fail")
check("containment-only (no blocks) -> fail",
      run(mutate(S, WRAP, lambda r: drop_edges(r, to=GATE, ty="blocks")))["verdict"] == "fail")
cyc = mutate(S, ROOT, lambda r: (r.update(parent=WRAP), add_edge(r, WRAP, "parent-child")))
check("containment cycle -> fail", run(cyc)["verdict"] == "fail")
check("parent field without its parent-child edge -> inconclusive",
      run(mutate(S, CAP, lambda r: drop_edges(r, ty="parent-child")))["verdict"] == "inconclusive")

# --- gate identity (finalized map) ------------------------------------------------------------
check("finalized map missing a declared gate -> fail",
      run(S, rcpt=receipt(gates={"Start Gate (mandatory)": GATE, "Reconcile Gate": REC}))["verdict"] == "fail")
check("extra observed real gate under the root -> fail",
      run(S + [node("yf-x4", "gate", title="Gate: extra")])["verdict"] == "fail")
check("mapped gate absent from graph -> inconclusive",
      run([r for r in S if r["id"] != CAP])["verdict"] == "inconclusive")
elsewhere = {"id": "yf-elsewhere", "issue_type": "epic", "status": "open", "title": "other", "dependencies": []}
sub_gate = mutate(S, CAP, lambda r: (r.update(parent="yf-elsewhere"), drop_edges(r, ty="parent-child"),
                                      add_edge(r, "yf-elsewhere", "parent-child")))
sub_gate += [elsewhere, node("yf-x5", "gate", title=f"Gate: {CAP_DECL.split(': ', 1)[1]}")]
check("count-preserving substituted gate -> fail", run(sub_gate)["verdict"] == "fail", str(run(sub_gate)))
check("a mapped real gate typed task is still counted, not dropped -> pass",
      run(mutate(S, CAP, lambda r: r.update(issue_type="task")))["verdict"] == "pass")

# --- malformed / unavailable input ------------------------------------------------------------
check("type alias conflict -> inconclusive",
      run(mutate(S, WRAP, lambda r: r.update(type="task")))["verdict"] == "inconclusive")
check("edge alias conflict -> inconclusive",
      run(mutate(S, WRAP, lambda r: r["dependencies"][-1].update(dependency_type="related")))["verdict"] == "inconclusive")
check("error envelope in records -> inconclusive", run([{"id": "x", "error": "boom"}])["verdict"] == "inconclusive")
check("non-array graph -> inconclusive", run({"error": "x"})["verdict"] == "inconclusive")
check("graph missing the role nodes -> inconclusive", run([SUB[0]])["verdict"] == "inconclusive")
dang = mutate(S, WRAP, lambda r: add_edge(r, "yf-ghost", "blocks"))
check("graph not closed over the root -> inconclusive", run(dang)["verdict"] == "inconclusive")


class R:
    def __init__(self, rc, out, err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def live(fn):
    try:
        gr.acquire_live(run=fn)
        return "returned"
    except gr.Inconclusive:
        return "inconclusive"


def _missing(*a, **k):
    raise FileNotFoundError("bd")


check("acquire: bd missing -> inconclusive", live(_missing) == "inconclusive")
check("acquire: non-zero exit -> inconclusive", live(lambda *a, **k: R(1, "[]", "err")) == "inconclusive")
check("acquire: error JSON object at exit 0 -> inconclusive",
      live(lambda *a, **k: R(0, '{"error": "no db"}')) == "inconclusive")
check("acquire: truncated JSON -> inconclusive", live(lambda *a, **k: R(0, '[{"id": ')) == "inconclusive")
argv_seen = []
gr.acquire_live(run=lambda argv, **k: argv_seen.append(argv) or R(0, "[]"))
check("acquire uses --all --include-gates --limit 0 (never default bd children)",
      bool(argv_seen) and argv_seen[0][:2] == ["bd", "list"] and "--include-gates" in argv_seen[0]
      and "--all" in argv_seen[0] and argv_seen[0][argv_seen[0].index("--limit") + 1] == "0")

# --- purity: classification performs no subprocess and no writes -------------------------------
real_run = subprocess.run
before = {p: sha(p) for p in FX.rglob("*") if p.is_file()}


def _forbidden(*a, **k):
    raise AssertionError("classify spawned a process")


subprocess.run = _forbidden
try:
    pure = run(SUB, evidence_base=B0)["verdict"] == "pass"
except AssertionError:
    pure = False
finally:
    subprocess.run = real_run
after = {p: sha(p) for p in FX.rglob("*") if p.is_file()}
check("classify spawns no process and writes nothing", pure and before == after)

if ran < 60:
    failures.append(f"only {ran} checks ran — the suite did not execute its controls")
print(f"\n{ran} checks, {len(failures)} failure(s)" if failures else f"\n{ran} checks, all passed")
for f in failures:
    print("  " + f)
sys.exit(1 if failures else 0)

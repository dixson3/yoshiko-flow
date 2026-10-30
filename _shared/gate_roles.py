#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Receipt-bound start-gate role classification (REQ-PLAN-087, plan-074, #417).

WHY THIS EXISTS
---------------
The `plan-execute` pour expands its one `type = "gate"` step into two beads: a WRAPPER that entry
issues depend on (`plan-execute.start-gate`) and the ACTUAL human gate
(`plan-execute.gate-start-gate`). `bd` 1.1.0 types the wrapper `task`; `bd` 1.3.1 types it `gate`
(EXP-001, identical installed formula). Two consumers broke on the second shape:

* the start resolver searched for a `task` titled `Begin:` and found nothing, then fell back to
  ANY `Gate:`-titled gate — which could be a capability gate;
* pour fidelity counted four gates against three declarations (PIM H0, EXP-003).

Native graph fields alone cannot tell the real pair from a deliberately copied lookalike, and a
persisted graph carries no formula/role provenance. So identity comes from the REQ-DATA-077
receipt — the native pour/create output retained when the tool emitted it — and the graph is
only checked AGAINST it. Titles, id prefixes and array order never decide anything here.

WHAT THIS MODULE IS NOT
-----------------------
It performs no writes, resolves no gate and grants no consent. `pass` means "the roles are the
ones the receipt says, and the graph is shaped the way a native pour shapes it". It does NOT mean
any gate may be resolved: that authority stays with the caller's fresh-session approval checks.
A receipt digest proves BYTES, not authorship.

THREE-VALUED
------------
`inconclusive` — this instrument could not judge (missing/partial/unknown receipt, incomplete or
malformed graph, unavailable CLI). `fail` — a definite contradiction. `pass` — every predicate held.
Callers map them to exits 2 / 1 / 0 and must halt on both non-zero codes.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

SCHEMA = "yf-plan-execution-roles/v1"
ROLE_ROOT = "plan-execute"
ROLE_WRAPPER = "plan-execute.start-gate"
ROLE_GATE = "plan-execute.gate-start-gate"
ROLE_KEYS = (ROLE_ROOT, ROLE_WRAPPER, ROLE_GATE)
STATES = ("start-only", "finalized")
EVIDENCE_KINDS = ("native", "legacy-attested")
RECEIPT_FIELDS = {
    "schema", "plan_id", "fingerprint", "plan_dir", "root", "formula_sha256", "bd_version",
    "evidence_kind", "evidence", "state", "roles", "gates", "acceptance",
}
RECEIPT_REQUIRED = RECEIPT_FIELDS - {"acceptance", "formula_sha256"}
WRAPPER_TYPES = ("task", "gate")
# Fields whose presence on a node means "this node awaits something". The native wrapper has none.
AWAIT_FIELDS = ("await_type", "await_id", "timeout", "waiters")
CONTAINMENT = "parent-child"
#: Root metadata the role binding depends on. Every record of one id must agree on these.
BINDING_METADATA_KEYS = ("plan_dir", "yf_origin_fingerprint")

PASS, FAIL, INCONCLUSIVE = "pass", "fail", "inconclusive"
EXIT = {PASS: 0, FAIL: 1, INCONCLUSIVE: 2}


class Inconclusive(Exception):
    """The input could not be judged. Never an empty graph, never a pass."""


# --------------------------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------------------------

# Plain classes, not dataclasses: every consumer loads `_shared` modules through
# `importlib.util.spec_from_file_location` without registering them in `sys.modules`, and
# `@dataclass` under postponed annotations dereferences `sys.modules[cls.__module__]`.
class Node:
    def __init__(self, id, type, status, parent, title, metadata, awaits):
        self.id, self.type, self.status, self.parent = id, type, status, parent
        self.title, self.metadata, self.awaits = title, metadata, awaits


class Graph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        # (from, to, type) — `from` depends on `to`; for `blocks`, `to` blocks `from`.
        self.edges: set[tuple[str, str, str]] = set()

    def out(self, nid: str, *, include_containment: bool = False):
        return {e for e in self.edges if e[0] == nid
                and (include_containment or e[2] != CONTAINMENT)}

    def into(self, nid: str, *, include_containment: bool = False):
        return {e for e in self.edges if e[1] == nid
                and (include_containment or e[2] != CONTAINMENT)}

    def children(self, nid: str) -> list[str]:
        return sorted(n.id for n in self.nodes.values() if n.parent == nid)

    def descendants(self, nid: str) -> list[str]:
        out, stack = [], [nid]
        while stack:
            for c in self.children(stack.pop()):
                out.append(c)
                stack.append(c)
        return out


def _meta(raw) -> dict:
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            v = json.loads(raw)
        except json.JSONDecodeError:
            raise Inconclusive(f"unparseable metadata string {raw[:60]!r}")
        if isinstance(v, dict):
            return v
    raise Inconclusive(f"metadata is neither an object nor a JSON object string: {raw!r:.60}")


def _node_type(rec: dict) -> str | None:
    a, b = rec.get("issue_type"), rec.get("type")
    if a and b and a != b:
        raise Inconclusive(f"{rec.get('id')}: conflicting type aliases issue_type={a!r} type={b!r}")
    return a or b


def _edges_of(rec: dict) -> set[tuple[str, str, str]]:
    nid = rec["id"]
    out = set()
    for d in rec.get("dependencies") or []:
        if not isinstance(d, dict):
            raise Inconclusive(f"{nid}: dependency entry is not an object")
        list_to, list_ty = d.get("depends_on_id"), d.get("type")
        show_to, show_ty = d.get("id"), d.get("dependency_type")
        if list_to is not None:
            # list shape. A list-shape `type` is the EDGE type; refuse a contradicting show alias.
            src = d.get("issue_id", nid)
            if src != nid:
                raise Inconclusive(f"{nid}: list-shape edge names issue_id {src!r}")
            if show_ty is not None and list_ty is not None and show_ty != list_ty:
                raise Inconclusive(f"{nid}: conflicting edge type aliases {list_ty!r}/{show_ty!r}")
            to, ty = list_to, list_ty or show_ty
        elif show_ty is not None:
            # show shape: the dependency is embedded as a node object, its type under
            # `dependency_type`; `type`/`issue_type` there describe the NODE, not the edge.
            to, ty = show_to, show_ty
        else:
            raise Inconclusive(f"{nid}: dependency entry has neither list nor show shape")
        if not to or not ty:
            raise Inconclusive(f"{nid}: dependency entry missing target or type")
        out.add((nid, str(to), str(ty)))
    return out


def normalize(records) -> Graph:
    """Normalize bd list/show records (any mix) into one Graph, or raise Inconclusive/ValueError.

    Duplicate ids are allowed ONLY when they describe the same node (e.g. a list snapshot and a
    show of the same bead); any structural disagreement is refused rather than merged by order.
    """
    if not isinstance(records, list):
        raise Inconclusive("graph input is not a JSON array")
    g = Graph()
    for rec in records:
        if not isinstance(rec, dict) or not rec.get("id"):
            raise Inconclusive("graph record without an id")
        if "error" in rec:
            raise Inconclusive(f"error envelope in graph input: {rec.get('error')!r:.80}")
        nid = str(rec["id"])
        node = Node(
            id=nid, type=_node_type(rec), status=rec.get("status"),
            parent=rec.get("parent"), title=str(rec.get("title") or ""),
            metadata=_meta(rec.get("metadata")),
            awaits={k: rec[k] for k in AWAIT_FIELDS if rec.get(k) not in (None, "", [], {})},
        )
        edges = _edges_of(rec)
        if nid in g.nodes:
            prev = g.nodes[nid]
            if (prev.type, prev.parent, prev.awaits) != (node.type, node.parent, node.awaits):
                raise Inconclusive(f"{nid}: duplicate records disagree structurally")
            # Binding-critical metadata must agree in PRESENCE and VALUE across every record of
            # the same id, or the verdict would depend on input order (independent review R1).
            for key in BINDING_METADATA_KEYS:
                a = (key in prev.metadata, prev.metadata.get(key))
                b = (key in node.metadata, node.metadata.get(key))
                if a != b:
                    raise Inconclusive(f"{nid}: duplicate records disagree on binding metadata "
                                       f"{key!r}; refusing rather than choosing by input order")
            # Other status/metadata may legitimately differ between two reads; keep the first.
        else:
            g.nodes[nid] = node
        g.edges |= edges
    _check_containment(g)
    return g


class GraphFailure(Exception):
    """A definite structural inconsistency (not an incomplete read)."""


def _check_containment(g: Graph) -> None:
    for (src, dst, ty) in g.edges:
        if ty != CONTAINMENT:
            continue
        node = g.nodes.get(src)
        if node is None:
            continue
        if node.parent is None:
            node.parent = dst
        elif node.parent != dst:
            raise GraphFailure(f"{src}: parent field {node.parent!r} disagrees with parent-child "
                               f"edge to {dst!r}")
    for n in g.nodes.values():
        if n.parent and (n.id, n.parent, CONTAINMENT) not in g.edges:
            # A show of a node lists its parent-child edge; a list does too. Absence means the
            # record was not a complete bd record.
            raise Inconclusive(f"{n.id}: parent {n.parent!r} without a parent-child edge")
        seen, cur = set(), n.id
        while cur is not None:
            if cur in seen:
                raise GraphFailure(f"containment cycle through {cur}")
            seen.add(cur)
            cur = g.nodes[cur].parent if cur in g.nodes else None


def acquire_live(run=subprocess.run, cwd=None) -> list:
    """Read the complete gate-inclusive graph. Any failure is Inconclusive, never []."""
    argv = ["bd", "list", "--all", "--include-gates", "--limit", "0", "--json"]
    try:
        r = run(argv, capture_output=True, text=True, timeout=120, cwd=cwd)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
        raise Inconclusive(f"bd unavailable: {e}")
    if r.returncode != 0:
        raise Inconclusive(f"`{' '.join(argv)}` exited {r.returncode}: {(r.stderr or '')[:200]}")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise Inconclusive(f"bd list output is not JSON: {e}")
    if isinstance(data, dict):
        raise Inconclusive(f"bd list returned an object, not an array: {str(data)[:120]}")
    return data


# --------------------------------------------------------------------------------------------
# Receipt
# --------------------------------------------------------------------------------------------

def validate_receipt(obj) -> list[str]:
    """Schema problems of a receipt object ([] = schema-valid). Never consults the graph."""
    if not isinstance(obj, dict):
        return ["receipt is not a JSON object"]
    probs = []
    if obj.get("schema") != SCHEMA:
        probs.append(f"unknown schema {obj.get('schema')!r}")
    unknown = set(obj) - RECEIPT_FIELDS
    if unknown:
        probs.append(f"unknown receipt fields {sorted(unknown)}")
    missing = RECEIPT_REQUIRED - set(obj)
    if missing:
        probs.append(f"missing receipt fields {sorted(missing)}")
    if obj.get("state") not in STATES:
        probs.append(f"unknown state {obj.get('state')!r}")
    kind = obj.get("evidence_kind")
    if kind not in EVIDENCE_KINDS:
        probs.append(f"unknown evidence_kind {kind!r}")
    if kind == "legacy-attested" and not obj.get("acceptance"):
        probs.append("legacy-attested receipt without a recorded operator acceptance")
    if kind == "native" and obj.get("acceptance"):
        probs.append("native receipt must not carry a legacy acceptance")
    roles = obj.get("roles")
    if not isinstance(roles, dict) or set(roles) != set(ROLE_KEYS):
        probs.append(f"roles must carry exactly {list(ROLE_KEYS)}")
    elif len({str(v) for v in roles.values()}) != 3 or not all(roles.values()):
        probs.append("role ids must be three distinct non-empty ids")
    gates = obj.get("gates")
    if not isinstance(gates, dict):
        probs.append("gates must be an object")
    else:
        ids = [str(v) for v in gates.values()]
        if len(set(ids)) != len(ids):
            probs.append("gates map repeats an id")
        if any(not k or not v for k, v in gates.items()):
            probs.append("gates map has an empty name or id")
        if isinstance(roles, dict) and roles.get(ROLE_WRAPPER) in ids:
            probs.append("the wrapper id is mapped as a real gate")
    ev = obj.get("evidence")
    if not isinstance(ev, list) or not ev:
        probs.append("evidence must be a non-empty list")
    else:
        for e in ev:
            if not isinstance(e, dict) or set(e) != {"path", "sha256"}:
                probs.append("each evidence entry must be exactly {path, sha256}")
                break
    return probs


def verify_evidence(receipt: dict, base: Path) -> tuple[str, list[str]]:
    """(verdict, diags): FAIL on a digest mismatch, INCONCLUSIVE on a missing file."""
    diags, verdict = [], PASS
    for e in receipt.get("evidence") or []:
        p = (base / e["path"]).resolve()
        if base.resolve() not in p.parents and p != base.resolve():
            return FAIL, [f"evidence path escapes the bundle: {e['path']}"]
        if not p.is_file():
            verdict = INCONCLUSIVE if verdict == PASS else verdict
            diags.append(f"evidence file missing: {e['path']}")
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != e["sha256"]:
            return FAIL, [f"evidence digest mismatch for {e['path']}"]
    return verdict, diags


def start_declaration(plan: dict) -> str | None:
    """The plan's start-gate declaration NAME (plan grammar `### Start Gate ...`)."""
    names = [g["name"] for g in plan.get("gates", []) if str(g.get("name", "")).startswith("Start Gate")]
    return names[0] if len(names) == 1 else None


# --------------------------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------------------------

def _verdict(v, diags, **kw) -> dict:
    out = {"verdict": v, "exit": EXIT[v], "diagnostics": diags}
    out.update(kw)
    return out


def classify(*, plan: dict, plan_id: str, fingerprint: str, plan_dir: str,
             recorded_root: str | None, records, receipt, require_final: bool = False,
             evidence_base: Path | None = None) -> dict:
    """Classify start-gate roles. Pure: no writes, no gate resolution, no consent.

    `plan` is one `plan_extract.extract()` record. `records` is raw bd list/show JSON (any mix)
    or an Inconclusive raised by the caller's acquisition. `receipt` is the parsed receipt or
    None. `evidence_base` (the bundle dir) enables evidence digest verification.
    """
    base = dict(wrapper=None, gate=None, root=recorded_root, evidence_source=None, gates={})
    if plan.get("unparsed"):
        return _verdict(INCONCLUSIVE, [f"plan has unparsed constructs: {plan['unparsed']}"], **base)
    if not recorded_root:
        return _verdict(INCONCLUSIVE, ["plan has no recorded **Epic:** root"], **base)
    if not fingerprint:
        return _verdict(INCONCLUSIVE, ["plan has no approved fingerprint to bind"], **base)
    if receipt is None:
        return _verdict(INCONCLUSIVE, ["no execution role receipt"], **base)
    probs = validate_receipt(receipt)
    if probs:
        return _verdict(INCONCLUSIVE, probs, **base)
    base["evidence_source"] = receipt["evidence_kind"]
    roles = {k: str(v) for k, v in receipt["roles"].items()}
    gates_map = {k: str(v) for k, v in receipt["gates"].items()}
    base.update(wrapper=roles[ROLE_WRAPPER], gate=roles[ROLE_GATE], gates=gates_map)

    # Binding: plan, fingerprint, bundle, root. A mismatch is a FOREIGN or STALE receipt.
    binding = []
    if receipt["plan_id"] != plan_id:
        binding.append(f"receipt plan {receipt['plan_id']!r} != {plan_id!r}")
    if receipt["fingerprint"] != fingerprint:
        binding.append("receipt fingerprint differs from the fresh approved fingerprint")
    if receipt["plan_dir"] != plan_dir:
        binding.append(f"receipt plan_dir {receipt['plan_dir']!r} != {plan_dir!r}")
    if receipt["root"] != recorded_root or roles[ROLE_ROOT] != recorded_root:
        binding.append(f"receipt root {receipt['root']!r}/{roles[ROLE_ROOT]!r} != recorded "
                       f"{recorded_root!r}")
    if binding:
        return _verdict(FAIL, binding, **base)

    if evidence_base is not None:
        ev, ediag = verify_evidence(receipt, evidence_base)
        if ev != PASS:
            return _verdict(ev, ediag, **base)

    start_decl = start_declaration(plan)
    if start_decl is None:
        return _verdict(INCONCLUSIVE, ["plan has no unique `Start Gate` declaration"], **base)
    if gates_map.get(start_decl) not in (None, roles[ROLE_GATE]):
        return _verdict(FAIL, [f"receipt maps {start_decl!r} to {gates_map[start_decl]!r}, not "
                               f"the actual gate {roles[ROLE_GATE]!r}"], **base)
    declared = {g["name"] for g in plan.get("gates", [])}
    if receipt["state"] == "finalized":
        if set(gates_map) != declared:
            return _verdict(FAIL, [f"finalized gate map names {sorted(gates_map)} != declared "
                                   f"{sorted(declared)}"], **base)
    else:
        if require_final:
            return _verdict(INCONCLUSIVE, ["receipt is start-only; a finalized receipt is "
                                           "required here"], **base)
        if set(gates_map) - declared:
            return _verdict(FAIL, [f"gate map names undeclared gates "
                                   f"{sorted(set(gates_map) - declared)}"], **base)

    try:
        g = records if isinstance(records, Graph) else normalize(records)
    except Inconclusive as e:
        return _verdict(INCONCLUSIVE, [str(e)], **base)
    except GraphFailure as e:
        return _verdict(FAIL, [str(e)], **base)

    root, wid, gid = recorded_root, roles[ROLE_WRAPPER], roles[ROLE_GATE]
    absent = [i for i in (root, wid, gid) if i not in g.nodes]
    if absent:
        return _verdict(INCONCLUSIVE, [f"graph is missing role nodes {absent}"], **base)
    # Closure over the root's subtree: every edge from a member must land on a known node.
    members = set(g.descendants(root)) | {root}
    dangling = sorted({e[1] for e in g.edges if e[0] in members and e[1] not in g.nodes})
    if dangling:
        return _verdict(INCONCLUSIVE, [f"graph does not close over the root: {dangling}"], **base)

    fails = []
    rmeta = g.nodes[root].metadata
    if "plan_dir" not in rmeta:
        return _verdict(INCONCLUSIVE, [f"root {root} carries no plan_dir binding"], **base)
    # DEV delivery guard (REQ-DATA-077): a NATIVE receipt is bound to the approval the pour was
    # linked under, recorded prospectively at new-pour linkage as `yf_origin_fingerprint`. Missing
    # is INCONCLUSIVE (an unstamped, pre-guard root is not native evidence); a different value is a
    # FAIL. This module never writes metadata, so nothing here stamps, backfills or migrates a root.
    # Legacy-attested imports are a separate human-attested mode and are not subject to it.
    if receipt["evidence_kind"] == "native":
        stamp = rmeta.get("yf_origin_fingerprint")
        if not stamp:
            return _verdict(INCONCLUSIVE, [f"root {root} carries no yf_origin_fingerprint stamp; "
                                           f"a pre-guard or unlinked root is not native evidence"],
                            **base)
        if stamp != fingerprint or stamp != receipt["fingerprint"]:
            return _verdict(FAIL, [f"root {root} yf_origin_fingerprint {stamp!r} does not match the "
                                   f"current approved fingerprint"], **base)
    if rmeta.get("plan_dir") != plan_dir:
        fails.append(f"root plan_dir {rmeta.get('plan_dir')!r} != {plan_dir!r}")
    w, a = g.nodes[wid], g.nodes[gid]
    if w.parent != root or a.parent != root:
        fails.append(f"wrapper/actual gate are not direct siblings under {root} "
                     f"(parents {w.parent!r}, {a.parent!r})")
    if w.type not in WRAPPER_TYPES:
        fails.append(f"wrapper {wid} has type {w.type!r}, not task|gate")
    if w.awaits:
        fails.append(f"wrapper {wid} carries await semantics {sorted(w.awaits)}")
    if a.type != "gate":
        fails.append(f"actual gate {gid} has type {a.type!r}")
    if a.awaits.get("await_type") != "human":
        fails.append(f"actual gate {gid} await_type {a.awaits.get('await_type')!r} != 'human'")
    w_out = g.out(wid)
    if w_out != {(wid, gid, "blocks")}:
        fails.append(f"wrapper edges {sorted(w_out)} are not exactly the native "
                     f"{wid} -> {gid} blocks edge")
    a_out = g.out(gid)
    if a_out:
        fails.append(f"actual gate {gid} has outgoing dependencies {sorted(a_out)}")
    # Competing pairs: any OTHER direct child of the root shaped like a wrapper over a human gate.
    for sib in g.children(root):
        if sib in (wid, gid):
            continue
        sn = g.nodes[sib]
        for (_, dst, ty) in g.out(sib):
            dn = g.nodes.get(dst)
            if (ty == "blocks" and dn is not None and dn.parent == root and dn.type == "gate"
                    and dn.awaits.get("await_type") == "human"):
                fails.append(f"competing wrapper pair {sib} -> {dst}")
        if sn.type == "gate" and sn.awaits.get("await_type") == "human" and sib not in gates_map.values():
            fails.append(f"unmapped competing human gate {sib}")
    if fails:
        return _verdict(FAIL, fails, **base)

    # Gate identity under the root: every observed gate other than the proven wrapper is mapped.
    observed = {n for n in members if g.nodes[n].type == "gate" and n != wid}
    mapped = set(gates_map.values())
    if receipt["state"] == "finalized":
        missing = sorted(mapped - set(g.nodes))
        if missing:
            return _verdict(INCONCLUSIVE, [f"mapped gates absent from graph {missing}"], **base)
        foreign = sorted(i for i in mapped if i not in members)
        extra = sorted(observed - mapped)
        if foreign or extra:
            return _verdict(FAIL, [f"gate identity mismatch: mapped outside root {foreign}, "
                                   f"unmapped observed gates {extra}"], **base)
    return _verdict(PASS, [], **base)


def main() -> int:  # pragma: no cover - thin CLI for diagnostics
    import argparse
    import importlib.util
    import sys
    ap = argparse.ArgumentParser(description="Classify start-gate roles (read-only).")
    ap.add_argument("plan_dir", type=Path)
    ap.add_argument("--graph", type=Path, help="bd list/show JSON; default: live read")
    ap.add_argument("--roles", type=Path, help="receipt; default: <plan_dir>/references/execution-roles.json")
    ap.add_argument("--require-final", action="store_true")
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("pe", Path(__file__).with_name("plan_extract.py"))
    if spec is None or spec.loader is None:
        raise ImportError("cannot build an import spec for plan_extract.py")
    pe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pe)
    plan = pe.extract(a.plan_dir / "plan.md")
    rp = a.roles or a.plan_dir / "references" / "execution-roles.json"
    try:
        receipt = json.loads(rp.read_text()) if rp.is_file() else None
        records = json.loads(a.graph.read_text()) if a.graph else acquire_live()
    except (Inconclusive, json.JSONDecodeError) as e:
        print(json.dumps({"verdict": INCONCLUSIVE, "exit": 2, "diagnostics": [str(e)]}))
        return 2
    v = classify(plan=plan, plan_id=plan.get("plan_id"), fingerprint=plan.get("fingerprint"),
                 plan_dir=str(a.plan_dir).rstrip("/"), recorded_root=plan.get("epic_bead"),
                 records=records, receipt=receipt, require_final=a.require_final,
                 evidence_base=a.plan_dir)
    print(json.dumps(v, indent=2))
    sys.stdout.flush()
    return v["exit"]


if __name__ == "__main__":
    raise SystemExit(main())

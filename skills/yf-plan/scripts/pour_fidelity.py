#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Compare a plan's DECLARED issue DAG against the beads the pour actually created.

**The number this exists to produce.** Measured over 43 comparable plans by EXP-003: 17
carried a pour divergence — 885 declared dependency edges against 860 in `bd`, **45 dropped
and 20 invented**. A dropped `blocks` edge means the coordinator marked a bead ready *before
its declared predecessor*. Nothing checked this; `yf-herdr` listed the mismatch as a deviation
for a human to watch for, which is an admission that a person was the only checksum.

## Three populations, reported SEPARATELY (REQ-DATA-026, review M1)

An aggregate conflates an identity artifact with a real ordering defect:

1. **no-mapping** — plans whose beads carry no recoverable issue id (006, 007, 036). These
   account for **43 of the 45** "dropped" edges purely because nothing can be joined.
2. **dropped** — edges declared in `plan.md` and absent from `bd`, among JOINABLE plans. The
   real defect class, and only **2** of the 45 once the artifact is separated out.
3. **invented** — edges present in `bd` and declared nowhere.

## The join

`plan_issue` bead **metadata** is preferred (REQ-DATA-026 / D-10); a leading `N.M` token in the
bead TITLE is the fallback for plans poured before that field existed. Titles get rewritten,
which is why metadata is primary. A bead matching neither is reported as `unnumbered` — never
guessed at.

**`--include-gates` is MANDATORY when producing the bead dump.** Without it 121 gate beads and
every gate edge are invisible **with no error at all** (#166).

Usage:

    bd list --all --include-gates --limit 5000 --json > /tmp/beads.json
    uv run _shared/pour_fidelity.py /tmp/beads.json docs/plans/plan-0* [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pe", SHARED / "plan_extract.py")
pe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pe)

_gspec = importlib.util.spec_from_file_location("gate_roles_for_pf", SHARED / "gate_roles.py")
if _gspec is None or _gspec.loader is None:
    raise ImportError("cannot build an import spec for gate_roles.py")
gr = importlib.util.module_from_spec(_gspec)
_gspec.loader.exec_module(gr)

TITLE_ID = re.compile(r"^\s*(?:Issue\s+)?((?:\d+|[A-Z])\.\d+[a-z]?)\s*[:.\s]")
EPIC_NUM = re.compile(r"^Epic\s*:?\s*(\d+|[A-Z])\s*:")
SCAFFOLD = re.compile(r"^\s*(Begin|Reconcile)\s*:", re.I)


def load_beads(path: Path):
    beads = json.load(path.open())
    if isinstance(beads, dict):
        beads = beads.get("issues", [])
    by_id = {b["id"]: b for b in beads}
    kids: dict[str, list[str]] = {}
    for b in beads:
        parent = b.get("parent") or (b.get("metadata") or {}).get("parent")
        if parent:
            kids.setdefault(parent, []).append(b["id"])
    return by_id, kids


def _repo_relative(plan_dir: Path) -> str:
    import subprocess
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, cwd=str(plan_dir), timeout=30)
        if top.returncode == 0 and top.stdout.strip():
            return str(plan_dir.resolve().relative_to(Path(top.stdout.strip()).resolve()))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    return str(plan_dir).rstrip("/")


#: The manager's canonical freshness chain (REQ-PORT-040/041), reused VERBATIM — never
#: reimplemented here (independent review R2). Only these definitions are executed, so importing
#: plan_manager's module top level (which runs `_migrate_state_dir()`, a state-moving write) never
#: happens in this read-only comparator. A missing definition fails closed.
_CANONICAL_FP_DEFS = ("FINGERPRINT_EXCLUDE_SECTIONS", "_read_plan_field", "_plan_content_sections",
                      "_plan_content_fingerprint", "_read_plan_fingerprint_field",
                      "_fingerprint_status")
_FP_STATUS = None


def _canonical_fingerprint_status(plan_dir: Path) -> dict:
    global _FP_STATUS
    if _FP_STATUS is None:
        import ast
        import hashlib
        here = Path(__file__).resolve().parent
        pm = next((c for c in (here / "plan_manager.py",
                               here.parent / "skills" / "yf-plan" / "scripts" / "plan_manager.py")
                   if c.is_file()), None)
        okp = next((c for c in (here / "okf.py", here.parent / "_shared" / "okf.py") if c.is_file()),
                   None)
        if pm is None or okp is None:
            raise FileNotFoundError("canonical plan_manager.py / okf.py not found")
        ospec = importlib.util.spec_from_file_location("okf_for_pf", okp)
        if ospec is None or ospec.loader is None:
            raise ImportError(f"cannot build an import spec for {okp}")
        okf_mod = importlib.util.module_from_spec(ospec)
        # okf declares dataclasses, which resolve their module through sys.modules at class creation.
        sys.modules["okf_for_pf"] = okf_mod
        ospec.loader.exec_module(okf_mod)
        tree = ast.parse(pm.read_text(encoding="utf-8"))
        picked = []
        for node in tree.body:
            name = getattr(node, "name", None)
            if name is None and isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
            if name in _CANONICAL_FP_DEFS:
                picked.append(node)
        found = {getattr(n, "name", None) or n.targets[0].id for n in picked}
        if found != set(_CANONICAL_FP_DEFS):
            raise ImportError(f"canonical fingerprint definitions missing: "
                              f"{sorted(set(_CANONICAL_FP_DEFS) - found)}")
        ns = {"__name__": "plan_manager_fingerprint", "okf": okf_mod, "re": re,
              "hashlib": hashlib, "Path": Path}
        exec(compile(ast.Module(body=picked, type_ignores=[]), str(pm), "exec"), ns)
        _FP_STATUS = ns["_fingerprint_status"]
    return _FP_STATUS(plan_dir)


def role_analysis(plan_dir: Path, ext: dict, epic_id: str, records: list,
                  roles_path: Path | None = None) -> dict:
    """REQ-DATA-026 (as amended by plan-074): classify the start-gate roles from the bundle's
    finalized REQ-DATA-077 receipt. READ-ONLY — `roles_path` only names WHICH receipt to read
    (the diagnostic `--roles`); nothing is written and no environment variable can substitute."""
    rp = roles_path or plan_dir / "references" / "execution-roles.json"
    # R2: establish canonical CURRENT-content freshness first; classify against the verified value.
    try:
        fp = _canonical_fingerprint_status(plan_dir)
    except Exception as e:  # noqa: BLE001 - any failure to evaluate freshness is INCONCLUSIVE
        return {"status": "inconclusive", "receipt": str(rp),
                "diagnostics": [f"canonical fingerprint freshness unavailable: {e}"]}
    if not fp.get("stored_fingerprint"):
        return {"status": "inconclusive", "receipt": str(rp),
                "diagnostics": ["plan has no stored approved fingerprint"]}
    if fp.get("stale_approved") or fp["stored_fingerprint"] != fp.get("current_fingerprint"):
        return {"status": gr.FAIL, "receipt": str(rp),
                "diagnostics": [f"stale approval: stored fingerprint {fp['stored_fingerprint']} != "
                                f"current content fingerprint {fp.get('current_fingerprint')}"]}
    current_fp = fp["current_fingerprint"]
    if not rp.is_file():
        return {"status": "no-receipt", "receipt": str(rp), "diagnostics":
                [f"no execution role receipt at {rp}"]}
    try:
        receipt = json.loads(rp.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"status": "inconclusive", "receipt": str(rp), "diagnostics": [str(e)]}
    v = gr.classify(plan=ext, plan_id=plan_dir.name, fingerprint=current_fp,
                    plan_dir=_repo_relative(plan_dir), recorded_root=epic_id, records=records,
                    receipt=receipt, require_final=True, evidence_base=plan_dir)
    return {"status": v["verdict"], "receipt": str(rp), "wrapper": v["wrapper"],
            "gate": v["gate"], "gates": v["gates"], "evidence_source": v["evidence_source"],
            "diagnostics": v["diagnostics"]}


def descendants(root: str, kids) -> list[str]:
    out, stack = [], list(kids.get(root, []))
    while stack:
        i = stack.pop()
        out.append(i)
        stack += kids.get(i, [])
    return out


def bead_issue_id(b: dict) -> tuple[str | None, str]:
    """`(issue_id, source)` — metadata first (REQ-DATA-026), title as the legacy fallback."""
    meta = b.get("metadata") or {}
    if isinstance(meta, dict) and meta.get("plan_issue"):
        return str(meta["plan_issue"]), "metadata"
    m = TITLE_ID.match(b.get("title") or "")
    return (m.group(1), "title") if m else (None, "none")


def compare(plan_md: Path, epic_id: str, by_id, kids, records: list | None = None,
            roles_path: Path | None = None) -> dict:
    ext = pe.extract(plan_md)
    ids = descendants(epic_id, kids)
    beads = [by_id[i] for i in ids if i in by_id]
    roles = (role_analysis(plan_md.parent, ext, epic_id, records, roles_path)
             if records is not None else {"status": "not-evaluated", "diagnostics": []})
    proven = roles["status"] == gr.PASS
    wrapper = roles.get("wrapper") if proven else None

    # With a PROVEN wrapper, the wrapper is removed BY ID — never by its `Begin:` title, and a
    # task-typed wrapper (bd 1.1.0) is excluded from the issue population the same way. Without
    # a receipt the legacy title scaffold is kept for historical corpus reporting only; strict
    # completion refuses that case as INCONCLUSIVE (see main()).
    if proven:
        tasks = [b for b in beads if b.get("issue_type") == "task" and b["id"] != wrapper
                 and not re.match(r"^\s*Reconcile\s*:", b.get("title") or "", re.I)]
        gates = [b for b in beads if b.get("issue_type") == "gate" and b["id"] != wrapper]
        # A mapped real gate typed `task` is COUNTED, never silently dropped.
        mapped = set(roles["gates"].values())
        gates += [b for b in beads if b["id"] in mapped and b.get("issue_type") != "gate"]
        tasks = [b for b in tasks if b["id"] not in mapped]
    else:
        tasks = [b for b in beads if b.get("issue_type") == "task"
                 and not SCAFFOLD.match(b.get("title") or "")]
        gates = [b for b in beads if b.get("issue_type") == "gate"]
    bepics = [b for b in beads if b.get("issue_type") == "epic"]

    by_iid: dict[str, dict] = {}
    unnumbered, duplicate, sources = [], [], {"metadata": 0, "title": 0}
    for b in tasks:
        iid, src = bead_issue_id(b)
        if iid is None:
            unnumbered.append({"id": b["id"], "title": (b.get("title") or "")[:80]})
            continue
        sources[src] = sources.get(src, 0) + 1
        if iid in by_iid:
            duplicate.append(iid)
        else:
            by_iid[iid] = b

    plan_ids = {i["id"] for i in ext["issues"]}
    joinable = bool(by_iid) and bool(plan_ids)

    missing = sorted(plan_ids - set(by_iid), key=pe.natural_key)
    extra = sorted(set(by_iid) - plan_ids, key=pe.natural_key)

    # --- edges ---------------------------------------------------------------------------
    plan_edges = {(e["from"], e["to"]) for e in ext["edges"]}
    rev = {b["id"]: iid for iid, b in by_iid.items()}
    bd_edges, touching_unjoined = set(), 0
    for iid, b in by_iid.items():
        for dep in b.get("dependencies") or []:
            # `bd` emits {issue_id, depends_on_id, type}. ONLY `blocks` is a declared
            # dependency — `parent-child` is the CONTAINMENT edge every bead has to its
            # epic. Counting containment here would invent one edge per issue on every
            # plan in the corpus, which is a fabricated defect rate, not a measurement.
            if isinstance(dep, dict):
                if (dep.get("type") or "").lower() not in ("blocks", "blocked-by", ""):
                    continue
                dep_id = dep.get("depends_on_id") or dep.get("id")
            else:
                dep_id = dep
            if dep_id is None:
                continue
            if dep_id in rev:
                bd_edges.add((iid, rev[dep_id]))
            else:
                touching_unjoined += 1

    dropped = sorted(plan_edges - bd_edges)
    invented = sorted(bd_edges - plan_edges)

    verdict = {
        "issue_count_match": len(plan_ids) == len(by_iid),
        "issue_id_set_match": not missing and not extra and not duplicate,
        "edge_set_match": plan_edges == bd_edges,
        "gate_count_match": len(ext["gates"]) == len(gates),
        "epic_count_match": len(ext["epics"]) == len(bepics),
    }

    # --- receipt-bound gate identity and gate-blocking edges (plan-074) ----------------------
    gate_edges = None
    if proven:
        gmap = roles["gates"]
        verdict["gate_identity_match"] = {b["id"] for b in gates} == set(gmap.values())
        expected, observed = set(), set()
        for i in ext["issues"]:
            if not i["depends_on"]:
                expected.add((i["id"], "<start-wrapper>"))
        for g in ext["gates"]:
            for blk in g.get("blocks") or []:
                if blk.get("kind") == "issue":
                    expected.add((blk["ref"], g["name"]))
        target = {wrapper: "<start-wrapper>", **{v: k for k, v in gmap.items()}}
        for iid, b in by_iid.items():
            for dep in b.get("dependencies") or []:
                if not isinstance(dep, dict) or (dep.get("type") or "").lower() not in ("blocks", ""):
                    continue
                to = dep.get("depends_on_id") or dep.get("id")
                if to in target:
                    observed.add((iid, target[to]))
        rec_decl = next((g["name"] for g in ext["gates"] if any(
            blk.get("kind") == "sentinel" for blk in g.get("blocks") or [])), None)
        # The reconcile gate's declared block is the SENTINEL "reconcile step": some non-issue
        # task under the root must depend on the mapped reconcile gate with a `blocks` edge.
        rec_ok = True
        if rec_decl and rec_decl in gmap:
            issue_bead_ids = {x["id"] for x in by_iid.values()}
            rec_ok = False
            for b in beads:
                if b.get("issue_type") != "task" or b["id"] in issue_bead_ids or b["id"] == wrapper:
                    continue
                for d in b.get("dependencies") or []:
                    if (isinstance(d, dict) and (d.get("depends_on_id") or d.get("id")) == gmap[rec_decl]
                            and (d.get("type") or "blocks").lower() == "blocks"):
                        rec_ok = True
        gate_edges = {"expected": len(expected), "observed": len(observed),
                      "dropped": sorted(map(list, expected - observed)),
                      "invented": sorted(map(list, observed - expected)),
                      "reconcile_step_gated": rec_ok}
        verdict["gate_edges_match"] = expected == observed and rec_ok
    return {
        "plan": plan_md.parent.name,
        "epic_bead": epic_id,
        "joinable": joinable,
        "population": ("no-mapping" if not joinable else
                       ("clean" if all(verdict.values()) and not unnumbered else "divergent")),
        "id_source": sources,
        "issues": {"plan": len(plan_ids), "bd": len(by_iid),
                   "missing_beads": missing, "extra_beads": extra,
                   "duplicate_ids": sorted(set(duplicate))},
        "unnumbered_beads": unnumbered,
        "edges": {"plan": len(plan_edges), "bd": len(bd_edges),
                  "dropped": [list(x) for x in dropped],
                  "invented": [list(x) for x in invented],
                  "touching_unjoined": touching_unjoined},
        "gates": {"plan": len(ext["gates"]), "bd": len(gates),
                  "wrapper_excluded": wrapper, "edges": gate_edges},
        "roles": roles,
        "epics": {"plan": len(ext["epics"]), "bd": len(bepics)},
        "extractor_unparsed": ext["counts"]["unparsed"],
        "verdict": verdict,
        "clean": all(verdict.values()) and not unnumbered and joinable,
    }


def run(beads_path: Path, plan_dirs: list[Path], roles_path: Path | None = None) -> dict:
    by_id, kids = load_beads(beads_path)
    raw = json.load(beads_path.open())
    records = raw.get("issues", []) if isinstance(raw, dict) else raw
    results, skipped = [], []
    for d in plan_dirs:
        pm = d / "plan.md" if d.is_dir() else d
        if not pm.is_file():
            skipped.append({"plan": d.name, "reason": "no plan.md"})
            continue
        ext_epic = re.search(r"^\*\*Epic:\*\*\s*(\S+)", pm.read_text(encoding="utf-8"), re.M)
        if not ext_epic:
            skipped.append({"plan": pm.parent.name, "reason": "no **Epic:** field"})
            continue
        results.append(compare(pm, ext_epic.group(1), by_id, kids, records, roles_path))

    no_map = [r for r in results if r["population"] == "no-mapping"]
    joinable = [r for r in results if r["joinable"]]
    divergent = [r for r in joinable if not r["clean"]]
    return {
        "comparable": len(results),
        "skipped": skipped,
        # THE THREE POPULATIONS, kept apart (REQ-DATA-026 / review M1).
        "populations": {
            "no_mapping": {"plans": [r["plan"] for r in no_map], "count": len(no_map)},
            "dropped_among_joinable": {
                "plans": [r["plan"] for r in joinable if r["edges"]["dropped"]],
                "edges": sum(len(r["edges"]["dropped"]) for r in joinable)},
            # `invented` is split by whether the extractor could READ that plan cleanly.
            # An edge present in `bd` but absent from the extracted DAG has TWO possible
            # causes, and conflating them overstates the pour's defect rate:
            #   * the plan declared it in a form this parser refuses (an unparsed
            #     `depends-on`) — the pour was RIGHT and the DOCUMENT is malformed;
            #   * the plan declared it nowhere at all — a genuinely invented edge.
            # Only the second is a pour defect. Measured: with a strict parser, 14 plans
            # show "invented" edges but only the subset below have a clean extraction.
            "invented_in_cleanly_parsed_plans": {
                "plans": [r["plan"] for r in joinable
                          if r["edges"]["invented"] and r["extractor_unparsed"] == 0],
                "edges": sum(len(r["edges"]["invented"]) for r in joinable
                             if r["extractor_unparsed"] == 0)},
            "invented_where_document_is_unreadable": {
                "plans": [r["plan"] for r in joinable
                          if r["edges"]["invented"] and r["extractor_unparsed"] > 0],
                "edges": sum(len(r["edges"]["invented"]) for r in joinable
                             if r["extractor_unparsed"] > 0),
                "note": ("NOT a pour defect: the plan declared these in a form the "
                         "REQ-DATA-019 grammar refuses, so the edge exists in `bd` and "
                         "not in the extracted DAG. The document is malformed, not the pour.")},
        },
        "divergent_plans": len(divergent),
        "totals": {
            "plan_edges": sum(r["edges"]["plan"] for r in results),
            "bd_edges": sum(r["edges"]["bd"] for r in results),
            "plan_issues": sum(r["issues"]["plan"] for r in results),
            "bd_issues": sum(r["issues"]["bd"] for r in results),
        },
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("beads_json", type=Path)
    ap.add_argument("plan_dirs", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 if any JOINABLE plan diverges (the close-gate mode).")
    ap.add_argument("--plan", help="Restrict --strict to one plan dir name (close-gate use).")
    ap.add_argument("--roles", type=Path, default=None,
                    help="READ-ONLY diagnostic: verify against this explicit role receipt instead "
                         "of the bundle default. Requires exactly one plan dir. Writes nothing.")
    a = ap.parse_args()
    if a.roles is not None and len(a.plan_dirs) != 1:
        print("INCONCLUSIVE: --roles names one receipt, so exactly one plan dir is required.",
              file=sys.stderr)
        return 2

    res = run(a.beads_json, a.plan_dirs, a.roles)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        p = res["populations"]
        print(f"comparable={res['comparable']} skipped={len(res['skipped'])} "
              f"divergent={res['divergent_plans']}")
        print(f"  no-mapping            : {p['no_mapping']['count']} plans "
              f"{p['no_mapping']['plans']}")
        print(f"  dropped (joinable)    : {p['dropped_among_joinable']['edges']} edges in "
              f"{len(p['dropped_among_joinable']['plans'])} plans")
        pi = p["invented_in_cleanly_parsed_plans"]
        pu = p["invented_where_document_is_unreadable"]
        print(f"  invented (clean docs) : {pi['edges']} edges in {len(pi['plans'])} plans")
        print(f"  invented (unreadable) : {pu['edges']} edges in {len(pu['plans'])} plans "
              f"— NOT a pour defect")
        print(f"  totals: plan_edges={res['totals']['plan_edges']} "
              f"bd_edges={res['totals']['bd_edges']}")

    if a.strict:
        # EMPTY SCOPE IS INCONCLUSIVE (2), NEVER A CLEAN 0 — D-7 / #210, Issue 3.1.
        #
        # `any([])` is False, so the `return 1 if any(...) else 0` below issued a CLEAN BILL
        # OF HEALTH after examining NOTHING. Three measured paths reach it:
        #
        #   A. the `no-mapping` population — beads carry no recoverable issue id, so
        #      `joinable` is false and the plan is filtered OUT of `scope` by the very
        #      predicate below. This is the population #210 justifies the gate BY: #186/#187's
        #      masked titles are exactly what destroys the title fallback, so the plans the
        #      gate most needs to judge were the ones it silently passed.
        #   B. a `--plan` value matching nothing — a typo, a renamed bundle, or a plan whose
        #      beads were never poured.
        #   C. a plan dir with no `**Epic:**` — `run()` puts it in `skipped[]`, never in
        #      `results`.
        #
        # `extractor_unparsed` already gets this treatment ten lines down, for the identical
        # reason: a verdict cannot be founded on input the instrument never saw. FAIL (1) is
        # as false as PASS (0) here — no divergence was observed either.
        #
        # THE FIX IS NARROW BY CONSTRUCTION: it fires only when the scope is EMPTY, and when
        # a `--plan`-scoped plan landed in `no-mapping`. A clean, joinable, in-scope plan
        # still returns 0 — `ctl-210-empty-scope`'s negative control asserts exactly that, so
        # a blanket "return 2 under --strict" cannot satisfy the control.
        scope = [r for r in res["results"]
                 if (a.plan in r["plan"] if a.plan else True) and r["joinable"]]

        in_plan_scope = [r for r in res["results"]
                         if (a.plan in r["plan"] if a.plan else True)]
        unjoinable = [r for r in in_plan_scope if not r["joinable"]]
        if not scope:
            if unjoinable:
                for r in unjoinable:
                    print(f"INCONCLUSIVE: {r['plan']} is in the `no-mapping` population — no "
                          f"bead carries a recoverable issue id, so the plan's DAG and the "
                          f"poured DAG cannot be joined at all. Fidelity is unjudgeable, not "
                          f"clean.", file=sys.stderr)
            elif a.plan:
                print(f"INCONCLUSIVE: `--plan {a.plan}` selected no comparable plan. Nothing "
                      f"was examined, so this is not a clean result.", file=sys.stderr)
            else:
                print("INCONCLUSIVE: no comparable plan in scope (every plan dir was skipped "
                      "— e.g. no `**Epic:**` field). Nothing was examined.", file=sys.stderr)
            for sk in res["skipped"]:
                print(f"INCONCLUSIVE:   skipped {sk['plan']}: {sk['reason']}", file=sys.stderr)
            return 2
        # REQ-DATA-043: gate on `unparsed[]` BEFORE judging fidelity. A plan the extractor
        # could not fully read yields a knowably incomplete `plan_edges` set, so a
        # "dropped edge" verdict against it is unfounded and a "clean" verdict is worse —
        # it is FALSE-CLEAN, manufactured by the parser's blind spot rather than measured.
        # INCONCLUSIVE (2) is the honest verdict; FAIL (1) is reserved for a readable plan
        # whose poured DAG genuinely diverges.
        unreadable = [r for r in scope if r.get("extractor_unparsed")]
        if unreadable:
            for r in unreadable:
                print(f"INCONCLUSIVE: {r['plan']} has {r['extractor_unparsed']} unparsed "
                      f"construct(s); its declared DAG is incomplete, so pour fidelity "
                      f"cannot be judged.", file=sys.stderr)
            return 2
        # plan-074 (REQ-DATA-026 as amended). PRECEDENCE: a definite issue/edge/epic divergence
        # is reported as 1 even without a receipt (it was observed); then a role FAIL is 1;
        # then a missing / start-only / inconclusive receipt is 2 — the gate population cannot
        # be judged by count alone, because an equal-count substitution would pass. A clean
        # verdict REQUIRES a proven, finalized receipt.
        legacy = ("issue_count_match", "issue_id_set_match", "edge_set_match", "epic_count_match")
        if any(not all(r["verdict"][k] for k in legacy) or r["unnumbered_beads"] for r in scope):
            return 1
        role_fail = [r for r in scope if r["roles"]["status"] == gr.FAIL]
        for r in role_fail:
            print(f"DIVERGENT: {r['plan']} start-gate roles FAIL: "
                  + "; ".join(r["roles"]["diagnostics"]), file=sys.stderr)
        if role_fail:
            return 1
        unproven = [r for r in scope if r["roles"]["status"] != gr.PASS]
        for r in unproven:
            print(f"INCONCLUSIVE: {r['plan']} has no proven finalized role receipt "
                  f"({r['roles']['status']}): " + "; ".join(r["roles"]["diagnostics"])
                  + ". Gate identity cannot be judged by count; completion halts.",
                  file=sys.stderr)
        if unproven:
            return 2
        return 1 if any(not r["clean"] for r in scope) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

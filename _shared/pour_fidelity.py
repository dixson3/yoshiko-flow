#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
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


def compare(plan_md: Path, epic_id: str, by_id, kids) -> dict:
    ext = pe.extract(plan_md)
    ids = descendants(epic_id, kids)
    beads = [by_id[i] for i in ids if i in by_id]

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
        "gates": {"plan": len(ext["gates"]), "bd": len(gates)},
        "epics": {"plan": len(ext["epics"]), "bd": len(bepics)},
        "extractor_unparsed": ext["counts"]["unparsed"],
        "verdict": verdict,
        "clean": all(verdict.values()) and not unnumbered and joinable,
    }


def run(beads_path: Path, plan_dirs: list[Path]) -> dict:
    by_id, kids = load_beads(beads_path)
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
        results.append(compare(pm, ext_epic.group(1), by_id, kids))

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
    a = ap.parse_args()

    res = run(a.beads_json, a.plan_dirs)
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
        scope = [r for r in res["results"]
                 if (a.plan in r["plan"] if a.plan else True) and r["joinable"]]
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
        return 1 if any(not r["clean"] for r in scope) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

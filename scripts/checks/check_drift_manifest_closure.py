#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_drift_manifest_closure.py — the tagged test for REQ-CHECK-008(a) / REQ-SCHEMA-002 /
REQ-DRIFT-011, the plan-066 Epic-0 amendment.

WHAT IT ASSERTS. `DRIFT-CHECK.md` is referentially closed under the WIDENED §6 rule:

  * every §2 edge names §1 nodes that exist;
  * every §3 `Per-Edge Contracts` row names a §2 edge that exists;
  * every §6 `Trigger Scope` *Scopes To* entry names a §2 EDGE **or** a §1 NODE that exists.

The third clause is the amendment. Before plan-066 it admitted edge IDs only, which made
`REQ-CHECK-008(a)`'s node-keyed dispatch — the mechanism that gives the node-level Reachability
check of `REQ-CHECK-004(a)` a firing surface — fail the manifest's own schema rule.

CLOSURE IS WIDENED, NOT RELAXED. An entry naming neither an existing edge nor an existing node
is still a violation, and `--selftest` proves that in both directions rather than asserting it.

WHY THIS SHIPS AHEAD OF THE MANIFEST EDITS IT GOVERNS. AGENTS.md SPEC-first: the requirement and
its test land before the code. Epic 3 adds node-keyed §6 rows; without this test, the first
evidence that the widened rule works would be the absence of a complaint from a prose judge —
which plan-066 EXP-002 measured at 4 firing opportunities and 0 catches.

EXIT  0 closed  ·  1 a dangling reference  ·  2 INCONCLUSIVE (could not read/parse the manifest)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CHECK = "check_drift_manifest_closure"

# A manifest with fewer rows than this parsed nothing useful; a check over an empty set
# certifies vacuously (the `check-criteria-scripts-exist.sh` precedent this repo already sets).
MIN_NODES = 5
MIN_EDGES = 5
MIN_TRIGGER_ROWS = 5

SECTION_RE = re.compile(r"^## (\d)\. ")
CODE_ID_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def split_sections(text: str) -> dict[str, list[str]]:
    """-> {section number: [lines]}. Sections are `## N. Title` headings."""
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, [])
            continue
        if cur is not None:
            out[cur].append(line)
    return out


def table_rows(lines: list[str]) -> list[list[str]]:
    """Pipe-table body rows, as lists of cell strings. Header and `|:--|` rules dropped."""
    rows: list[list[str]] = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        if all(set(c) <= set(":- ") for c in cells if c):
            continue  # alignment rule
        rows.append(cells)
    return rows[1:] if rows else []  # drop the header row


def first_code_id(cell: str) -> str | None:
    m = CODE_ID_RE.search(cell)
    return m.group(1) if m else None


def all_code_ids(cell: str) -> list[str]:
    return CODE_ID_RE.findall(cell)


def parse(text: str):
    sec = split_sections(text)
    for n in ("1", "2", "3", "6"):
        if n not in sec:
            raise ValueError(f"manifest has no `## {n}.` section")

    nodes = {i for r in table_rows(sec["1"]) if (i := first_code_id(r[0]))}
    edges: dict[str, tuple[str, str]] = {}
    for r in table_rows(sec["2"]):
        eid = first_code_id(r[0])
        if eid and len(r) >= 3:
            edges[eid] = (first_code_id(r[1]) or "", first_code_id(r[2]) or "")
    contract_rows = [i for r in table_rows(sec["3"]) if (i := first_code_id(r[0]))]
    trigger: list[tuple[str, list[str]]] = []
    for r in table_rows(sec["6"]):
        if len(r) >= 2:
            trigger.append((r[0], all_code_ids(r[1])))
    return nodes, edges, contract_rows, trigger


def check(text: str) -> tuple[int, list[str], dict]:
    nodes, edges, contract_rows, trigger = parse(text)
    findings: list[str] = []

    if len(nodes) < MIN_NODES or len(edges) < MIN_EDGES or len(trigger) < MIN_TRIGGER_ROWS:
        raise ValueError(
            f"parsed {len(nodes)} nodes / {len(edges)} edges / {len(trigger)} §6 rows — "
            f"below the vacuity floor ({MIN_NODES}/{MIN_EDGES}/{MIN_TRIGGER_ROWS}); "
            "the parser, not the manifest, is what to fix"
        )

    # §2 edges name §1 nodes that exist.
    for eid, (src, der) in sorted(edges.items()):
        for role, nid in (("source", src), ("derived", der)):
            if nid and nid not in nodes:
                findings.append(f"§2 edge `{eid}` names a {role} node `{nid}` absent from §1")

    # §3 rows name §2 edges that exist.
    for eid in contract_rows:
        if eid not in edges:
            findings.append(f"§3 contract row `{eid}` names no §2 edge")

    # §6 entries name a §2 edge OR a §1 node (REQ-CHECK-008(a), the amendment).
    node_keyed = 0
    for glob, ids in trigger:
        if not ids:
            findings.append(f"§6 row `{glob}` scopes to nothing")
            continue
        for i in ids:
            if i in edges:
                continue
            if i in nodes:
                node_keyed += 1
                continue
            findings.append(f"§6 row `{glob}` names `{i}` — neither a §2 edge nor a §1 node")

    stats = {
        "nodes": len(nodes), "edges": len(edges),
        "contract_rows": len(contract_rows), "trigger_rows": len(trigger),
        "node_keyed_entries": node_keyed, "findings": len(findings),
    }
    return (1 if findings else 0), findings, stats


def selftest(text: str) -> int:
    """TWO-SIDED negative control. A checker never observed to FAIL is not evidence.

    Both controls mutate the MANIFEST TEXT, which for this check IS the source of truth — the
    thing under test is the manifest's own internal closure, so there is no second artifact a
    code-side control could reach.
    """
    ok = True

    # Control 1 — POSITIVE: a fabricated node-keyed §6 entry must PASS under the widened rule
    # and would have FAILED under the pre-amendment edge-only rule.
    nodes, edges, _, _ = parse(text)
    a_node = sorted(nodes)[0]
    mutated = text.replace(
        "## 7. Fixed-Authority Conflict Policy",
        f"| `zz/selftest/**` | `{a_node}` |\n\n## 7. Fixed-Authority Conflict Policy", 1)
    rc, f, _ = check(mutated)
    print(f"  control-1 node-keyed entry (`{a_node}`): rc={rc} (want 0) findings={f}")
    ok &= (rc == 0)

    # Control 2 — NEGATIVE: a dangling §6 entry must still FAIL. This is what proves the rule
    # was widened rather than removed.
    mutated2 = text.replace(
        "## 7. Fixed-Authority Conflict Policy",
        "| `zz/selftest/**` | `e-does-not-exist-anywhere` |\n\n## 7. Fixed-Authority Conflict Policy", 1)
    rc2, f2, _ = check(mutated2)
    hit = [x for x in f2 if "e-does-not-exist-anywhere" in x]
    print(f"  control-2 dangling entry: rc={rc2} (want 1) matched={len(hit)} (want >=1)")
    ok &= (rc2 == 1 and len(hit) >= 1)

    print(f"{CHECK}: selftest {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="DRIFT-CHECK.md")
    ap.add_argument("--selftest", action="store_true",
                    help="run the two-sided negative control instead of the live check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.manifest)
    if not path.is_file():
        return inconclusive(f"no manifest at {path}")
    text = path.read_text(encoding="utf-8")

    try:
        if args.selftest:
            return selftest(text)
        rc, findings, stats = check(text)
    except ValueError as e:
        return inconclusive(str(e))

    if args.json:
        print(json.dumps({"check": CHECK, "verdict": "PASS" if rc == 0 else "FAIL",
                          "findings": findings, **stats}, indent=1))
    else:
        for f in findings:
            print(f"{CHECK}: FAIL — {f}", file=sys.stderr)
        print(f"{CHECK}: {stats['nodes']} nodes, {stats['edges']} edges, "
              f"{stats['trigger_rows']} §6 rows ({stats['node_keyed_entries']} node-keyed); "
              f"{stats['findings']} finding(s)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

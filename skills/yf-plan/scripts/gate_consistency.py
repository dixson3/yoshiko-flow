#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Gate/Blocks-set consistency for a plan.md (#113, plan-052 Epic 4).

A capability gate is UNOPENABLE when the work that would satisfy it is work the gate itself
blocks. Two arms, because one of them cannot see the other's defect:

  ARM 1 — SELF-SATISFACTION (name-based). No issue in a gate's `Blocks` may be named in its
          `Condition` / `Test` / `Instructions` as producing that gate's evidence.

  ARM 2 — DISCHARGER CLOSURE (graph-based). No control the `Condition` requires may have ALL
          of its dischargers inside — or TRANSITIVELY BEHIND — that `Blocks` set.

**ARM 2 IS THE ONE THAT MATTERS, AND A NAME-MATCH CANNOT SEE IT.** plan-052's own pre-fix
`red-prework-core` named no blocked issue anywhere in its prose, so an arm-1-only predicate
read it as clean — while six of the controls its Condition required were built by issues the
gate itself blocked. The gate could never open, and nothing said so.

Exit: 0 no finding · 1 at least one finding · 2 the predicate could not run (INCONCLUSIVE —
a statement about the instrument, not about the plan).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys

INCONCLUSIVE = 2

#: A control id as it appears in a Condition or a Verification cell.
CTL = re.compile(r"\bctl-[a-z0-9]+(?:-[a-z0-9]+)*\b")


def _load_plan_extract(start: pathlib.Path):
    here = pathlib.Path(__file__).resolve().parent
    for cand in (here / "plan_extract.py",
                 here.parent.parent.parent / "_shared" / "plan_extract.py"):
        if cand.is_file():
            spec = importlib.util.spec_from_file_location("plan_extract_for_gates", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def _issue_mentioned(text: str, issue_id: str) -> bool:
    """True when `issue_id` appears as a WHOLE reference in `text`.

    Bounded on both sides so `1.5` does not match inside `1.55` or `11.5`. The trailing
    boundary must not treat a further `.` as a word char, or `1.2` would match `1.2.3`.
    """
    return re.search(rf"(?<![\w.]){re.escape(issue_id)}(?![\w.])", text) is not None


def ancestors(issue_id: str, deps: dict[str, list[str]]) -> set[str]:
    """Every issue `issue_id` transitively depends on."""
    seen, stack = set(), list(deps.get(issue_id, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(deps.get(cur, []))
    return seen


def check_plan(doc: dict) -> list[dict]:
    """Return findings for one extracted plan document. Pure."""
    issues = doc.get("issues") or []
    deps = {i["id"]: list(i.get("depends_on") or []) for i in issues}
    criteria = doc.get("criteria") or []

    # control id -> the issues that discharge a criterion verifying it
    dischargers: dict[str, set[str]] = {}
    for c in criteria:
        cids = {t for t in CTL.findall(c.get("verification") or "") if "*" not in t}
        for cid in cids:
            dischargers.setdefault(cid, set()).update(c.get("discharged_by") or [])

    findings: list[dict] = []
    for g in doc.get("gates") or []:
        blocks = {b["ref"] for b in (g.get("blocks") or []) if b.get("kind") == "issue"}
        if not blocks:
            continue
        prose = " ".join(str(g.get(k) or "")
                         for k in ("condition", "test", "instructions"))

        # --- ARM 1 -----------------------------------------------------------------
        for iid in sorted(blocks):
            if _issue_mentioned(prose, iid):
                findings.append({
                    "arm": 1, "gate": g.get("name"), "issue": iid,
                    "detail": (f"gate {g.get('name')!r} BLOCKS issue {iid}, and names it in "
                               f"its Condition/Test/Instructions as producing the gate's "
                               f"evidence — the gate cannot open until work it blocks runs"),
                })

        # --- ARM 2 -----------------------------------------------------------------
        # `blocked_closure` is the Blocks set PLUS everything transitively behind it: an
        # issue whose ancestors include a blocked issue is itself unreachable while the gate
        # holds, so a discharger there is no more available than one inside Blocks.
        blocked_closure = set(blocks)
        for i in issues:
            if ancestors(i["id"], deps) & blocks:
                blocked_closure.add(i["id"])

        required = {t for t in CTL.findall(prose) if "*" not in t}
        for cid in sorted(required):
            owners = dischargers.get(cid) or set()
            if not owners:
                findings.append({
                    "arm": 2, "gate": g.get("name"), "control": cid,
                    "detail": (f"gate {g.get('name')!r} requires control {cid}, which no "
                               f"criterion discharges — the gate's Condition rests on "
                               f"evidence nothing in this plan produces"),
                })
                continue
            if owners <= blocked_closure:
                inside = sorted(owners & blocks)
                behind = sorted(owners - blocks)
                findings.append({
                    "arm": 2, "gate": g.get("name"), "control": cid,
                    "dischargers": sorted(owners),
                    "detail": (f"gate {g.get('name')!r} requires control {cid}, and ALL of "
                               f"its dischargers sit inside the Blocks set "
                               f"({inside or 'none directly'}) or TRANSITIVELY BEHIND it "
                               f"({behind or 'none'}) — the gate can never open. A name-match "
                               f"cannot see this: the gate's prose names no blocked issue."),
                })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan_dir")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    pdir = pathlib.Path(a.plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.is_file():
        print(f"INCONCLUSIVE: plan.md not found under {a.plan_dir}", file=sys.stderr)
        return INCONCLUSIVE

    mod = _load_plan_extract(pdir)
    if mod is None:
        print("INCONCLUSIVE: plan_extract.py not found", file=sys.stderr)
        return INCONCLUSIVE
    try:
        doc = mod.extract(plan_md)
    except Exception as e:  # noqa: BLE001
        print(f"INCONCLUSIVE: plan_extract could not read the plan: {e}", file=sys.stderr)
        return INCONCLUSIVE

    # REQ-DATA-043: a knowably incomplete DAG yields INCONCLUSIVE, never a finding. A gate
    # verdict drawn from a partial graph is a finding about the parser, not about the plan.
    if doc.get("unparsed"):
        print(f"INCONCLUSIVE: the plan has {len(doc['unparsed'])} unparsed line(s)",
              file=sys.stderr)
        return INCONCLUSIVE

    findings = check_plan(doc)
    out = {
        "plan_dir": str(pdir),
        "verdict": "FAIL" if findings else "PASS",
        "gates": len(doc.get("gates") or []),
        "findings": findings,
    }
    if a.as_json:
        print(json.dumps(out, indent=1))
    else:
        if findings:
            print(f"FAIL: {len(findings)} gate-consistency finding(s):")
            for f in findings:
                print(f"  - [arm {f['arm']}] {f['detail']}")
        else:
            print(f"PASS: {out['gates']} gate(s) consistent with their Blocks sets")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

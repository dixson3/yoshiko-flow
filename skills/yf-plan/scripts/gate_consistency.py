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
    verdict, code, evaluated, total = verdict_for(doc, findings)
    out = {
        "plan_dir": str(pdir),
        "verdict": verdict,
        "gates": total,
        "evaluated": evaluated,
        "findings": findings,
    }
    if verdict == "INCONCLUSIVE":
        out["reason"] = (f"{total} gate(s) declared but none has an issue-kind Blocks set "
                         f"({evaluated}/{total} evaluable) — the engine could judge nothing")
    if a.as_json:
        print(json.dumps(out, indent=1))
    else:
        if verdict == "FAIL":
            print(f"FAIL: {len(findings)} gate-consistency finding(s):")
            for f in findings:
                print(f"  - [arm {f['arm']}] {f['detail']}")
        elif verdict == "INCONCLUSIVE":
            print(f"INCONCLUSIVE: {out['reason']}", file=sys.stderr)
        else:
            print(f"PASS: {out['gates']} gate(s) consistent with their Blocks sets")
    return code


def _issue_kind_blocks(gate: dict) -> list[str]:
    """The entries of a gate's Blocks set that name ISSUES — not the `reconcile step` sentinel
    and not an `epic:<N>` container reference (REQ-DATA-019 admits all three forms)."""
    out = []
    for b in gate.get("blocks") or []:
        if isinstance(b, dict):
            if b.get("kind") == "issue" and b.get("ref"):
                out.append(str(b["ref"]))
        elif b and b != "reconcile step" and not str(b).startswith("epic:"):
            out.append(str(b))
    return out


def verdict_for(doc: dict, findings: list[dict]) -> tuple[str, int, int, int]:
    """-> (verdict, exit, evaluated, total). TWO FACTS, TWO SIGNALS (#325, plan-071 Issue 4.4).

    Before this, a plan with capability gates none of which the engine could evaluate returned
    the same `PASS`/exit 0 as a plan that declares no capability gate at all. Those are
    different facts: the first is a legitimate plan (plan-069 declares no gate), the second is
    an instrument that judged nothing — and "judged nothing" must never read as "clean".

      no capability gate declared            -> PASS, gates: 0, exit 0
      gates declared, none evaluable         -> INCONCLUSIVE, exit 2, `evaluated/total`
      >= 1 evaluable, findings               -> FAIL, exit 1
      >= 1 evaluable, no findings            -> PASS, exit 0
    """
    gates = [g for g in (doc.get("gates") or [])
             if "capability" in str(g.get("kind", g.get("type", ""))).lower()
             or _issue_kind_blocks(g) or g.get("blocks")]
    total = len(doc.get("gates") or [])
    evaluated = sum(1 for g in (doc.get("gates") or []) if _issue_kind_blocks(g))
    if total == 0:
        return "PASS", 0, 0, 0
    if evaluated == 0:
        return "INCONCLUSIVE", INCONCLUSIVE, 0, total
    return ("FAIL", 1, evaluated, total) if findings else ("PASS", 0, evaluated, total)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Evidence rendering for `closable` proposals (REQ-BUP-070b, #205).

A close-out proposal is an OUTWARD-FACING RECOMMENDATION the operator is asked to authorize.
Without the mapped beads, their `close_reason`s and the plan Success Criteria those beads
discharge, it asks for consent to a claim whose evidence lives somewhere the operator would
have to reconstruct by hand.

**A present-but-EMPTY key does not discharge the requirement.** An empty `close_reasons`
array renders as "evidence supplied" while supplying none — the silent-green class this
module exists to close. So `enrich()` reports, per row, whether the evidence is actually
there, and the caller can assert on it rather than on the key's presence.

This module is PURE with respect to the network and to `bd`: it reads plan bundles off disk
and enriches rows it is handed. It never queries, and it never closes anything.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

#: Where plan bundles live. Both yf-plan roots, so an incubator-scoped plan resolves too.
PLAN_ROOTS = ("docs/plans", "Incubator/*/plans")


def _load_plan_extract(repo_root: pathlib.Path):
    """Load `plan_extract` from the vendored skill copy or canonical `_shared/`."""
    for cand in (repo_root / "skills" / "yf-plan" / "scripts" / "plan_extract.py",
                 repo_root / "_shared" / "plan_extract.py"):
        if cand.is_file():
            spec = importlib.util.spec_from_file_location("plan_extract_for_render", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def find_plan_dir(repo_root: pathlib.Path, plan_id: str) -> pathlib.Path | None:
    """Resolve a plan id to its bundle directory, across both roots."""
    if not plan_id:
        return None
    for root in PLAN_ROOTS:
        for d in sorted(repo_root.glob(f"{root}/{plan_id}")):
            if (d / "plan.md").is_file():
                return d
    return None


def criteria_by_issue(repo_root: pathlib.Path, plan_id: str) -> dict[str, list[str]]:
    """-> {issue id: [criterion ids it discharges]} for one plan. {} when unresolvable.

    Unresolvable is returned as an EMPTY MAP rather than raised: a bead may legitimately map
    to a plan this checkout does not carry, and that is a reason to report thin evidence, not
    to fail the whole proposal.
    """
    pdir = find_plan_dir(repo_root, plan_id)
    if pdir is None:
        return {}
    mod = _load_plan_extract(repo_root)
    if mod is None:
        return {}
    try:
        doc = mod.extract(pdir / "plan.md")
    except Exception:  # noqa: BLE001 — an unreadable plan is thin evidence, not a crash
        return {}
    out: dict[str, list[str]] = {}
    for c in doc.get("criteria") or []:
        for iid in c.get("discharged_by") or []:
            out.setdefault(iid, []).append(c["id"])
    return out


def enrich(rows: list[dict], beads_by_id: dict[str, dict],
           repo_root: pathlib.Path) -> list[dict]:
    """Add `close_reasons` and `discharges` to every proposal row (REQ-BUP-070b).

    EVERY row is enriched, not only the closable ones: an operator deciding NOT to close an
    issue needs the same evidence as one deciding to.
    """
    cache: dict[str, dict[str, list[str]]] = {}
    for row in rows:
        reasons, discharges = [], []
        for bid in row.get("beads") or []:
            b = beads_by_id.get(bid) or {}
            md = b.get("metadata") or {}
            reasons.append({
                "bead": bid,
                "title": b.get("title") or "",
                "close_reason": (b.get("close_reason") or "").strip(),
                "is_hoist_tombstone": bool(row.get("hoist_tombstones")
                                           and bid in row["hoist_tombstones"]),
            })
            plan_id = str(md.get("plan") or "")
            issue_id = str(md.get("plan_issue") or "")
            if not plan_id or not issue_id:
                continue
            if plan_id not in cache:
                cache[plan_id] = criteria_by_issue(repo_root, plan_id)
            for cid in cache[plan_id].get(issue_id, []):
                entry = {"plan": plan_id, "issue": issue_id, "criterion": cid}
                if entry not in discharges:
                    discharges.append(entry)
        row["close_reasons"] = reasons
        row["discharges"] = discharges
        # The honesty flag: TRUE only when the row really carries evidence. A caller must be
        # able to tell "rendered evidence" from "rendered an empty array".
        row["evidence_complete"] = bool(reasons) and bool(discharges)
    return rows


def render_text(rows: list[dict]) -> str:
    """Human-readable evidence block for the proposal the operator is asked to authorize."""
    out: list[str] = []
    for row in rows:
        n = row.get("issue") or row.get("external")
        verdict = "CLOSABLE" if row.get("closable") else "not-closable"
        out.append(f"#{n} — {verdict}")
        out.append(f"  reason: {row.get('reason', '')}")
        for r in row.get("close_reasons") or []:
            mark = "  [HOIST TOMBSTONE] " if r["is_hoist_tombstone"] else "  "
            out.append(f"{mark}{r['bead']}: {r['close_reason'] or '(no close_reason recorded)'}")
        ds = row.get("discharges") or []
        if ds:
            crit = ", ".join(sorted({d["criterion"] for d in ds}))
            out.append(f"  discharges: {crit}")
        else:
            out.append("  discharges: (none resolvable — evidence is THIN, read before acting)")
        out.append("")
    return "\n".join(out)

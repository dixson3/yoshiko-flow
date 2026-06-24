"""Canonical active-set classifier — the single source of truth (plan-014 `_shared/`).

This module is the **canonical** copy of the active-set classifier shared by
`yf-beads-hygiene` (`beads_hygiene.py`) and `yf-beads-upstream` (`upstream.py`). Each
consuming script carries a **marker-fenced region** holding a verbatim copy of the
REGION delimited below; `_shared/sync.py` regenerates those regions in-place from this
file (no sibling `import`, no new file — each script stays self-contained per the repo's
one-script-one-file convention).

Do **not** hand-edit the vendored copies. Edit the region here and run
`uv run _shared/sync.py`; CI/manual `uv run _shared/sync.py --check` reports divergence.
The copies stay honest via the `yf-drift-check` on-edit trigger over the DRIFT-CHECK.md
edges `e-active-set-copy-hygiene` / `e-active-set-copy-upstream` (this file is the fixed
authority; a divergent region is the copy drifting — FAIL on the copy, never the canonical).

Everything between the BEGIN/END canonical markers is the vendored region. It assumes
`dataclass` and `field` are already imported by the consuming module (both consumers, and
this module below, import them).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# >>> BEGIN active-set classifier (canonical) >>>
GATE_TYPE = "gate"
CLOSED_STATUSES = {"closed", "resolved", "done"}
PARENT_CHILD = "parent-child"

IN_PROGRESS = "in_progress"
OPEN = "open"

# Reasons a bead is classified ACTIVE (one of these holds).
ACTIVE_IN_PROGRESS = "in_progress"           # status == in_progress
ACTIVE_CLAIMED = "open_claimed"              # status == open AND owner non-empty
ACTIVE_ANCESTOR = "open_ancestor_of_active"  # open parent-chain ancestor of an active bead


@dataclass
class Edge:
    blocked: str          # the bead that carries the edge (depends on `blocker`)
    blocker: str          # the edge target (id referenced by the dependency)
    dep_type: str         # blocks | parent-child | related | discovered-from
    target: dict | None   # resolved target bead, or None if it does not exist

    def classify(self) -> str:
        """Return exactly one of the four classes. The #29 invariant lives here."""
        if self.target is None:
            # Target does not resolve anywhere. A missing parent (molecule root) is a true
            # orphan; any other missing target is a truly-dangling edge.
            return "true-orphan" if self.dep_type == PARENT_CHILD else "truly-dangling"
        if self.target.get("issue_type") == GATE_TYPE:
            status = (self.target.get("status") or "").lower()
            # CRITICAL (#29): an OPEN gate target is a LIVE gate — never dangling, never removed.
            return "satisfied-gate" if status in CLOSED_STATUSES else "live-gate"
        # Non-gate target that resolves: a healthy edge — not a finding.
        return "healthy"


@dataclass
class ActiveSetReport:
    """Partition of non-closed beads into active vs non-active.

    Closed beads are EXCLUDED (neither active nor non-active). `reasons` maps every
    classified bead id to the reason string it was placed in its bucket.
    """
    active: list[str] = field(default_factory=list)
    non_active: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            "active": self.active,
            "non_active": self.non_active,
            "reasons": self.reasons,
            "active_count": len(self.active),
            "non_active_count": len(self.non_active),
        }


def _is_closed(bead: dict) -> bool:
    return (bead.get("status") or "").lower() in CLOSED_STATUSES


def _has_owner(bead: dict) -> bool:
    return bool((bead.get("owner") or "").strip())


def _directly_active(bead: dict) -> str | None:
    """Return the active-reason if a bead is directly active, else None.

    Directly active = status==in_progress, OR (status==open AND owner claimed). The
    ancestor case is resolved by the caller (it requires the full graph).
    """
    status = (bead.get("status") or "").lower()
    if status == IN_PROGRESS:
        return ACTIVE_IN_PROGRESS
    if status == OPEN and _has_owner(bead):
        return ACTIVE_CLAIMED
    return None


def classify_active(beads: dict[str, dict], edges: list[Edge]) -> ActiveSetReport:
    """Partition beads into active vs non-active per the plan-013 glossary (pure, no I/O).

    ACTIVE when, for a bead:
      - status == in_progress; OR
      - status == open AND owner non-empty (claimed); OR
      - it is an OPEN parent-chain ancestor (walk `parent-child` edges upward) of an
        active bead.
    Non-active = every other non-closed bead (open-unclaimed, blocked, deferred).
    Closed beads are EXCLUDED from both buckets.

    `beads` is {id: bead-dict}; `edges` is the resolved Edge set (a parent-child edge has
    blocked=child, blocker=parent — same shape collect_edges produces). This consumes the
    `dep_type` field uniformly, so it is agnostic to the `dependency_type`/`type` source
    divergence (collect_edges already normalizes to `dep_type`).
    """
    # child -> set(parent) from parent-child edges (blocked=child depends-on blocker=parent).
    parents: dict[str, set[str]] = {}
    for e in edges:
        if e.dep_type == PARENT_CHILD:
            parents.setdefault(e.blocked, set()).add(e.blocker)

    # Seed: directly-active beads.
    reasons: dict[str, str] = {}
    for bid, bead in beads.items():
        if _is_closed(bead):
            continue
        r = _directly_active(bead)
        if r is not None:
            reasons[bid] = r

    # Propagate up the parent chain: an OPEN ancestor of any active bead is itself active.
    # Iterate to a fixed point so transitive ancestors (epic of a molecule of a task) are caught.
    changed = True
    while changed:
        changed = False
        for child in list(reasons):
            for parent in parents.get(child, ()):  # noqa: SIM118
                pbead = beads.get(parent)
                if pbead is None or _is_closed(pbead):
                    continue
                # Only an OPEN ancestor is promoted (per glossary). in_progress/claimed
                # ancestors are already seeded directly; we never demote a stronger reason.
                if parent not in reasons and (pbead.get("status") or "").lower() == OPEN:
                    reasons[parent] = ACTIVE_ANCESTOR
                    changed = True

    report = ActiveSetReport()
    for bid, bead in beads.items():
        if _is_closed(bead):
            continue
        if bid in reasons:
            report.active.append(bid)
            report.reasons[bid] = reasons[bid]
        else:
            report.non_active.append(bid)
            report.reasons[bid] = "non_active"
    report.active.sort()
    report.non_active.sort()
    return report
# <<< END active-set classifier (canonical) <<<

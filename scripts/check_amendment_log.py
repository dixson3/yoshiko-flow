#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_amendment_log.py — SPEC-first conformance for a plan's SPEC epic.

Two assertions, over two DIFFERENT sets. They are named rather than both called "the set",
because they carry two different rules and conflating them is how a check silently certifies
nothing.

A1 — AMENDMENT-LOG COVERAGE.
    Every ``REQ-*`` id **named in the body of an Epic-0 issue** carries a bullet in ``SPEC.md``'s
    living amendment log under this plan's entry.

    The id set is DERIVED FROM EPIC-0 ISSUE BODIES ONLY — never hand-enumerated, and never from
    the whole plan document. A whole-file derivation over-collects the ids a plan **cites but
    must not amend** (``REQ-YF-TUNE-029``, ``REQ-YF-MARK-001/002/003``, …), so the check would
    fail for the wrong reason. Those live in an explicit ``cited-not-touched`` exclusion list.

    THE LIMITATION IS STATED RATHER THAN HIDDEN: that exclusion list is hand-authored, so this
    assertion is only as sound as a list a human maintains — which is precisely the property it
    exists to remove from the loop. It degrades honestly to "makes visible in review".

A2 — REQ REACHABILITY, over a COMPUTABLE predicate.
    Every issue in the implementation epics (everything after Epic 0) has a ``depends-on`` path
    to at least one Epic-0 issue whose body names a ``REQ-*`` id — **except** a declared
    ``no-req-required`` set.

    WHERE EACH HALF IS DECLARED IS WHAT MAKES THE BOUND MEAN ANYTHING. The **mutable** list is
    parsed from ``plan.md`` (the reviewed artifact); the **immutable baseline** is hardcoded
    below (the instrument). Putting both in one place would make the comparison a constant
    against itself — dead code that can never fire. A parsed member outside the baseline that
    carries no reason string is INCONCLUSIVE, not a pass.

EXIT CONTRACT — three-valued.
    0  both assertions hold
    1  an assertion FAILED
    2  INCONCLUSIVE — the check could not run, **including when the derived id set is empty or
       single-element**. A check over an empty set certifies vacuously (the
       ``check-criteria-scripts-exist.sh`` precedent), and that is a statement about the
       instrument, not about the plan.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# The IMMUTABLE half of A2's exemption (see the module docstring). A plan may declare its own
# `no-req-required` set in plan.md; a member outside this baseline must carry a reason string,
# or the check is INCONCLUSIVE.
NO_REQ_REQUIRED_BASELINE = {"4.6", "4.7"}

# Ids a plan legitimately CITES without amending. Hand-authored, and the check's own stated
# soundness limit.
CITED_NOT_TOUCHED = {
    "REQ-YF-TUNE-029",
    "REQ-YF-MARK-001",
    "REQ-YF-MARK-002",
    "REQ-YF-MARK-003",
    "REQ-YF-MARK-004",
    "REQ-YF-MARK-005",
    "REQ-YF-INSTALL-008",
    "REQ-YF-INSTALL-010",
    "REQ-YF-FLOW-007",
    "REQ-YF-DOCTOR-001",
    "REQ-YF-DOCTOR-002",
    "REQ-YF-DOCTOR-003",
    "REQ-YF-CLI-002",
    "REQ-DATA-057",
}

REQ_RE = re.compile(r"REQ-[A-Z]+(?:-[A-Z]+)*-\d{3}")
EPIC_RE = re.compile(r"^### Epic (\d+): (.+)$")
ISSUE_RE = re.compile(r"^- Issue (\d+\.\d+[a-z]?): (.*)$")
DEPENDS_RE = re.compile(r"^\s+- depends-on:\s*(.+)$")


def inconclusive(msg: str) -> None:
    print(f"check_amendment_log: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def parse_plan(text: str):
    """-> (epic_of_issue, body_of_issue, depends_of_issue, declared_no_req)."""
    epic_of: dict[str, str] = {}
    body_of: dict[str, str] = {}
    deps_of: dict[str, list[str]] = {}

    in_epics = False
    cur_epic: str | None = None
    cur_issue: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            in_epics = line.strip() == "## Epics"
            if not in_epics:
                cur_epic = cur_issue = None
            continue
        if not in_epics:
            continue
        m = EPIC_RE.match(line)
        if m:
            cur_epic, cur_issue = m.group(1), None
            continue
        m = ISSUE_RE.match(line)
        if m and cur_epic is not None:
            cur_issue = m.group(1)
            epic_of[cur_issue] = cur_epic
            body_of[cur_issue] = m.group(2)
            deps_of.setdefault(cur_issue, [])
            continue
        if cur_issue is None:
            continue
        m = DEPENDS_RE.match(line)
        if m:
            deps_of[cur_issue] = [d.strip() for d in m.group(1).split(",") if d.strip()]
            continue
        if line.startswith("  ") and line.strip():
            body_of[cur_issue] += "\n" + line.strip()

    # The MUTABLE half of A2's exemption, parsed from the reviewed artifact.
    declared: set[str] = set()
    for m in re.finditer(r"`no-req-required`[^\n]*?\{([^}]*)\}", text):
        declared |= {t.strip().strip("`") for t in m.group(1).split(",") if t.strip()}
    return epic_of, body_of, deps_of, declared


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True, help="plan id, e.g. plan-055-james-dixson-5f1c40")
    ap.add_argument("--plans-root", default=None, help="override the plans root")
    ap.add_argument("--spec", default=None, help="override the SPEC.md path")
    args = ap.parse_args()

    root = repo_root()
    plan_dir = Path(args.plans_root) / args.plan if args.plans_root else root / "docs" / "plans" / args.plan
    plan_md = plan_dir / "plan.md"
    spec_md = Path(args.spec) if args.spec else root / "SPEC.md"

    if not plan_md.is_file():
        inconclusive(f"no plan.md at {plan_md}")
    if not spec_md.is_file():
        inconclusive(f"no SPEC.md at {spec_md}")

    plan_text = plan_md.read_text(encoding="utf-8")
    spec_text = spec_md.read_text(encoding="utf-8")

    epic_of, body_of, deps_of, declared_no_req = parse_plan(plan_text)
    if not epic_of:
        inconclusive("parsed zero issues out of plan.md's `## Epics` section")

    # ---- A1: derive the touched-id set from EPIC-0 ISSUE BODIES ONLY -------------------
    spec_epic = min(epic_of.values(), key=int)
    spec_issues = [i for i, e in epic_of.items() if e == spec_epic]
    derived: set[str] = set()
    for iid in spec_issues:
        derived |= set(REQ_RE.findall(body_of[iid]))
    touched = derived - CITED_NOT_TOUCHED

    if len(touched) <= 1:
        inconclusive(
            f"the derived id set is {'empty' if not touched else 'single-element'} "
            f"({sorted(touched)}) — a check over such a set certifies vacuously. "
            f"Epic {spec_epic} issues must NAME their REQ-* ids explicitly."
        )

    # The plan's amendment-log entry: from its `plan-NNN` bullet to the next top-level bullet.
    plan_num = args.plan.split("-")[1]
    m = re.search(rf"^> - \*\*plan-{plan_num} \(", spec_text, re.M)
    if not m:
        inconclusive(f"SPEC.md has no amendment-log entry for plan-{plan_num}")
    tail = spec_text[m.start():]
    nxt = re.search(r"^> - \*\*", tail[1:], re.M)
    entry = tail[: nxt.start() + 1] if nxt else tail

    rc = 0
    missing = sorted(i for i in touched if i not in entry)
    if missing:
        rc = 1
        print(
            "check_amendment_log: FAIL — amended without an amendment-log bullet: "
            + ", ".join(missing),
            file=sys.stderr,
        )

    # ---- A2: REQ reachability over the implementation epics ---------------------------
    req_bearing = {i for i in spec_issues if REQ_RE.search(body_of[i])}

    unknown = declared_no_req - NO_REQ_REQUIRED_BASELINE
    unexplained = [i for i in unknown if "no-req-required" not in body_of.get(i, "")]
    if unexplained:
        inconclusive(
            "plan.md declares no-req-required member(s) outside the hardcoded baseline "
            f"{sorted(NO_REQ_REQUIRED_BASELINE)} carrying no reason string: {sorted(unexplained)}"
        )
    exempt = declared_no_req or NO_REQ_REQUIRED_BASELINE

    def reaches_req(iid: str, seen: set[str] | None = None) -> bool:
        seen = seen or set()
        if iid in seen:
            return False
        seen.add(iid)
        for d in deps_of.get(iid, []):
            if d in req_bearing or reaches_req(d, seen):
                return True
        return False

    unreachable = sorted(
        i for i, e in epic_of.items()
        if e != spec_epic and i not in exempt and not reaches_req(i)
    )
    if unreachable:
        rc = 1
        print(
            "check_amendment_log: FAIL — implementation issue(s) with no depends-on path to a "
            "REQ-naming Epic-" + spec_epic + " issue, and not in the declared no-req-required "
            f"set {sorted(exempt)}: {unreachable}",
            file=sys.stderr,
        )

    if rc == 0:
        n_impl = sum(1 for e in epic_of.values() if e != spec_epic) - len(exempt)
        print(
            f"check_amendment_log: {len(touched)} amended id(s) all carry an amendment-log "
            f"bullet; all {n_impl} non-exempt implementation issues reach a REQ-naming "
            f"Epic-{spec_epic} issue"
        )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

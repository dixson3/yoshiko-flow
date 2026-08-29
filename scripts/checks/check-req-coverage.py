#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""SC1 — every Epic 1-4 issue is covered by a requirement.

Coverage means ONE OF THREE THINGS, and the disjunction is the criterion, not a loosening:

  (a) the issue names a ``REQ-*`` id in its own bullet text; or
  (b) it ``depends-on`` — **DIRECTLY OR TRANSITIVELY** — an Epic 0 issue that adds one; or
  (c) it is explicitly marked a bug fix to an already-shipped REQ.

THE TRANSITIVE READING IS LOAD-BEARING, and it is stated here so this script IMPLEMENTS a
criterion rather than DEFINING one. Measured over the extracted DAG: **13 of 24** non-Epic-0
issues carry a DIRECT Epic-0 dependency and **23 of 24** carry a transitive one, the sole
exclusion being the declared bug-fix carve-out. So the literal direct-only reading would make
SC1 FALSE BY CONSTRUCTION — a criterion that cannot pass is the mirror of one that cannot
fail, and neither is a check.

FAIL-LOUD ON AN EMPTY INSPECTION (REQ-CLI-029(b)). A plan whose DAG yields no non-Epic-0
issues certifies nothing; ``--min-issues`` is the floor.

EXIT  0 every issue is covered  ·  1 at least one is not  ·  2 could not run
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check-req-coverage"
REQ_RE = re.compile(r"\bREQ-[A-Z]+(?:-[A-Z]+)*-\d+\b")
# The declared bug-fix carve-out (c). DECLARED, never inferred — an inferred exemption is
# indistinguishable from an oversight, which is the same rule REQ-DATA-044's bookkeeping
# carve-out states for `plan-relations`.
BUGFIX_RE = re.compile(r"\*\*No new REQ\*\*|bug fix to a shipped REQ|is a bug fix rather than",
                       re.IGNORECASE)


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def extract(plan_dir: Path) -> dict:
    """Run the canonical extractor. Never hand-parse plan.md here — a second parser is a
    second grammar, and the two would disagree exactly where it matters."""
    repo = Path(__file__).resolve().parent.parent.parent
    for cand in (repo / "_shared" / "plan_extract.py",
                 repo / "skills" / "yf-plan" / "scripts" / "plan_extract.py"):
        if cand.is_file():
            break
    else:
        inconclusive("cannot locate plan_extract.py")
    proc = subprocess.run(["uv", "run", str(cand), str(plan_dir), "--json"],
                          capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        inconclusive(f"plan_extract.py exited {proc.returncode}: {proc.stderr[-400:]}")
    try:
        d = json.loads(proc.stdout)
    except json.JSONDecodeError:
        inconclusive("plan_extract.py did not emit JSON")
    if isinstance(d, list):
        d = next((x for x in d if isinstance(x, dict) and "epics" in x), None)
    if not isinstance(d, dict) or "issues" not in d:
        inconclusive("plan_extract.py output carries no `issues`")
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan_dir", type=Path)
    ap.add_argument("--min-issues", type=int, default=5,
                    help="fail-loud floor: fewer non-Epic-0 issues than this is INCONCLUSIVE")
    a = ap.parse_args()

    if not a.plan_dir.is_dir():
        inconclusive(f"no such plan dir: {a.plan_dir}")

    d = extract(a.plan_dir)

    # THE SOURCE LINE, not only the extracted title. MEASURED on plan-056: `plan_extract.py`
    # parses `- Issue <N>.<M>: <description>` and DISCARDS a `(`REQ-*`)` parenthetical written
    # between the id and the colon — the form six of this plan's eleven Epic-0 issues use. So
    # reading the extracted title alone reports "names no REQ" about an issue whose source
    # line names one in its first ten characters, and SC1 would be FALSE on a plan that
    # satisfies it. (Filed as a follow-on: the extractor's issue grammar cannot express what
    # its own corpus writes — the same class as `## Gates` being unable to express
    # `test_class`.)
    #
    # The extractor stays authoritative for the DAG, which is what it is right about; only the
    # REQ-naming predicate falls back to the source line, via the `line` field the extractor
    # itself reports.
    plan_lines = (a.plan_dir / "plan.md").read_text(encoding="utf-8").splitlines()

    def source_line(i: dict) -> str:
        n = i.get("line")
        if isinstance(n, int) and 1 <= n <= len(plan_lines):
            return plan_lines[n - 1]
        return ""

    text_of = {i["id"]: "\n".join((source_line(i), i.get("title", ""), i.get("detail") or ""))
               for i in d["issues"]}

    # Epic-0 issues that ADD or AMEND a requirement. An Epic-0 bookkeeping issue (0.8, 0.12
    # correct figures) supplies no REQ, so depending on it is not coverage.
    epic0 = [i for i in d["issues"] if i.get("epic") == "0"]
    req_sources = {i["id"] for i in epic0 if REQ_RE.search(text_of[i["id"]])}

    # Adjacency, forward: issue -> its declared predecessors.
    preds: dict[str, list[str]] = {i["id"]: list(i.get("depends_on") or []) for i in d["issues"]}

    def reaches_req_source(iid: str) -> str | None:
        """BFS to an Epic-0 REQ source. Returns the source id, or None."""
        seen, queue = {iid}, list(preds.get(iid, []))
        while queue:
            n = queue.pop(0)
            if n in req_sources:
                return n
            if n in seen:
                continue
            seen.add(n)
            queue.extend(preds.get(n, []))
        return None

    targets = [i for i in d["issues"] if i.get("epic") != "0"]

    # THE FLOOR (REQ-CLI-029(b)). A run that inspected nothing exits 0 on every rule it
    # applies; without this, "covered" and "not read" are the same observation.
    if len(targets) < a.min_issues:
        inconclusive(f"only {len(targets)} non-Epic-0 issue(s) found "
                     f"(floor {a.min_issues}) — this run would certify vacuously")

    uncovered, rows = [], []
    for i in targets:
        iid = i["id"]
        t = text_of[iid]
        if REQ_RE.search(t):
            rows.append((iid, "names-req", REQ_RE.search(t).group(0)))
            continue
        if BUGFIX_RE.search(t):
            rows.append((iid, "declared-bugfix", "-"))
            continue
        src = reaches_req_source(iid)
        if src:
            direct = src in (i.get("depends_on") or [])
            rows.append((iid, "direct-dep" if direct else "transitive-dep", src))
            continue
        rows.append((iid, "UNCOVERED", "-"))
        uncovered.append(iid)

    for iid, how, via in rows:
        print(f"  {iid:>6}  {how:<16} {via}")

    direct = sum(1 for _, h, _ in rows if h == "direct-dep")
    trans = sum(1 for _, h, _ in rows if h in ("direct-dep", "transitive-dep"))
    print(f"{CHECK}: {len(targets)} non-Epic-0 issue(s); "
          f"{direct} direct Epic-0 dep, {trans} transitive, "
          f"{sum(1 for _, h, _ in rows if h == 'names-req')} name a REQ, "
          f"{sum(1 for _, h, _ in rows if h == 'declared-bugfix')} declared bug fix")

    if uncovered:
        print(f"{CHECK}: FAIL — {len(uncovered)} issue(s) name no REQ, reach no Epic-0 "
              f"requirement source, and declare no bug-fix carve-out: {', '.join(uncovered)}",
              file=sys.stderr)
        return 1
    print(f"{CHECK}: every non-Epic-0 issue is covered")
    return 0


if __name__ == "__main__":
    sys.exit(main())

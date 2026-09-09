#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_agents_set.py — REQ-CHECK-014: the `e-web-agents-set` edge, SCOPED.

CONTRACT.  Every agent file under `skills/{yf-plan,yf-research}/agents/*.md` is named by
`web/content/pages/workflows.md`.

**THE SCOPE IS A REQUIRED PART OF THE EDGE, NOT A TUNING PARAMETER** — and this is the whole
finding, not a caveat.  The derived node's own subtitle covers "the yf-plan and yf-research
pipelines and the subagents that run them", so those two skills ARE the edge's subject.
Measured (plan-067 pass-3 C1):

    scoped   skills/{yf-plan,yf-research}/agents/*.md ->  16 files, 15 documented, 1 absent
    unscoped skills/*/agents/*.md                     ->  23 files across 6 skills;
             a NAME-based extractor over it surfaces 4 out-of-scope agents,
             a PATH-based one surfaces 7  ->  an 80-87% artifact rate against 1 real finding

An unscoped edge here does not catch more.  It catches the same one thing and buries it under
four to seven false ones — which is how a check earns the reputation that gets it disabled.

VACUITY FLOOR.  `--min-agents` (default 10).  A scope that resolves to nothing certifies nothing.

EXIT  0 every in-scope agent is documented  ·  1 at least one is not  ·  2 INCONCLUSIVE
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check_agents_set"
SCOPE_SKILLS = ("yf-plan", "yf-research")
PAGE = "web/content/pages/workflows.md"


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None)
    ap.add_argument("--page", default=PAGE)
    ap.add_argument("--min-agents", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    page = root / a.page
    if not page.is_file():
        inconclusive(f"derived node absent: {a.page}")
    text = page.read_text(encoding="utf-8", errors="replace")

    files = [p for s in SCOPE_SKILLS
             for p in sorted((root / "skills" / s / "agents").glob("*.md"))]
    if len(files) < a.min_agents:
        inconclusive(f"the scope resolved to {len(files)} agent file(s), below the "
                     f"--min-agents floor of {a.min_agents}")

    documented, absent = [], []
    for f in files:
        name = f.stem
        ref = f"{f.parent.parent.name}/{name}"
        # Either spelling counts: the page's table uses `**name** (`name.md`)`.
        if re.search(rf"`{re.escape(name)}\.md`", text) or \
           re.search(rf"\*\*{re.escape(name)}\*\*", text):
            documented.append(ref)
        else:
            absent.append(ref)

    rc = 1 if absent else 0
    if absent:
        print(f"{CHECK}: FAIL — in-scope agent(s) named nowhere in {a.page}: "
              + ", ".join(absent), file=sys.stderr)

    out = {"check": CHECK, "verdict": "FAIL" if absent else "PASS",
           "scope": [f"skills/{s}/agents/*.md" for s in SCOPE_SKILLS],
           "in_scope": len(files), "floor": a.min_agents,
           "documented": documented, "absent": absent,
           "not_checked": [
               "agents OUTSIDE the two pipeline skills — deliberately out of scope "
               "(REQ-CHECK-014). Unscoped, `skills/*/agents/*.md` returns 23 files across 6 "
               "skills and yields an 80-87% artifact rate against 1 real finding",
               "whether the page DESCRIBES each agent correctly — name presence is the "
               "predicate; intent match is a prose judgement",
               "script-verb and editorial coverage — irreducibly editorial, out of scope",
           ]}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"{CHECK}: {len(documented)} of {len(files)} in-scope agent(s) documented in "
              f"{a.page}" + (f"; ABSENT: {absent}" if absent else ""))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

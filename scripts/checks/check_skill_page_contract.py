#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_skill_page_contract.py — the SET-DIFFERENCE existence check for `skill-page`.

THE MECHANICAL REALIZATION OF `REQ-CHECK-004(a)`, dispatched per `REQ-CHECK-008`/`REQ-ENGINE-008`
(plan-066 Epic 0). It is the sibling of `check_skill_readme_contract.py`, which does the same
job for `skill-readme`.

  Set A = dirnames of `skills/*/SKILL.md`      (every skill that ships)
  Set B = stems  of `web/content/skills/*.md`  (every skill that has an authored page)

  assert  A \\ B == {}      — a shipped skill with no page is a FAILURE
  report  B \\ A            — a page for no skill is an ORPHAN, advisory, not a failure

**THE OPERATOR IS SET DIFFERENCE, AND THAT IS THE WHOLE POINT.** Edge pairing — what every other
check in `DRIFT-CHECK.md` uses — computes the INTERSECTION of the two globs. An artifact missing
from one side simply drops out of the pairing, taking its own absence with it. Measured
(plan-066 EXP-002): the two sets stood at 20 and 19, the intersection at 19, and the
one-element difference — `yf-okf-hygiene` shipping with no page — was reported by NOTHING. It
surfaced instead as a Pelican **build crash**, which is the wrong artifact reporting the wrong
kind of verdict.

**ABSENCE AND MISMATCH ARE TWO FACTS.** This checker reports only absence. Whether a page that
EXISTS agrees with its `SKILL.md` is `e-skill-page-desc`'s question, and that edge keeps its
prose route — see `not_checked`.

**THE SOURCE-SIDE TRIGGER IS MANDATORY** (`REQ-CHECK-008(b)`). This checker's
`CHANGE-VALIDATION.md` §3 globs must name `skills/*/SKILL.md`, not only `web/content/skills/*.md`:
**an absent file is never edited and can never fire its own on-edit check.** Measured, commit
`75a5796` added the twentieth skill, broke the build, and touched ZERO files on the derived side.

`--min-skills` is the vacuity floor. A set-difference check over an empty Set A passes trivially,
so "clean" and "never read" would be the same observation without it.

EXIT  0 clean  ·  1 a shipped skill has no page  ·  2 INCONCLUSIVE (could not run / vacuous)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _web_corpus import repo_root  # noqa: E402

CHECK = "check_skill_page_contract"
SKILLS_GLOB = "skills/*/SKILL.md"
PAGES_GLOB = "web/content/skills/*.md"
MIN_SKILLS = 15


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None)
    ap.add_argument("--skills-glob", default=SKILLS_GLOB)
    ap.add_argument("--pages-glob", default=PAGES_GLOB)
    ap.add_argument("--min-skills", type=int, default=MIN_SKILLS,
                    help="vacuity floor: fewer shipped skills than this is INCONCLUSIVE")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()

    set_a = sorted(p.parent.name for p in root.glob(a.skills_glob))
    set_b = sorted(p.stem for p in root.glob(a.pages_glob))

    if len(set_a) < a.min_skills:
        return inconclusive(f"Set A is {len(set_a)} skill(s), below the floor {a.min_skills} — "
                            "a set-difference check over an empty set certifies vacuously, so "
                            "'clean' and 'never read' would be indistinguishable")

    missing = sorted(set(set_a) - set(set_b))   # FAILURE
    orphans = sorted(set(set_b) - set(set_a))   # advisory

    out = {
        "check": CHECK,
        "verdict": "FAIL" if missing else "PASS",
        "operator": "set-difference (A \\ B), NOT intersection",
        "set_a_skills": len(set_a), "set_b_pages": len(set_b),
        "intersection": len(set(set_a) & set(set_b)),
        "missing_page": missing,
        "orphan_pages": orphans,
        "not_checked": [
            "whether an EXISTING page AGREES with its SKILL.md — that is e-skill-page-desc, "
            "an intent match that tolerates paraphrase and keeps its prose route "
            "(REQ-CHECK-009)",
        ],
    }
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for m in missing:
            print(f"FAIL skills/{m}/ ships with no web/content/skills/{m}.md")
        for o in orphans:
            print(f"ORPHAN web/content/skills/{o}.md names no shipped skill (advisory)")
        print(f"{CHECK}: A={len(set_a)} skills, B={len(set_b)} pages, "
              f"intersection={out['intersection']}; {len(missing)} missing, "
              f"{len(orphans)} orphan(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

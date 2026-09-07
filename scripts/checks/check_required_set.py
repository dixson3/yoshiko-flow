#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_required_set.py — REQ-CHECK-010: the DECLARED required set, v1 = SLASH SUB-VERBS.

CONTRACT.  Every sub-verb a skill's normalised ``## Invocation`` declares must be named
somewhere on the published site.

THE SCOPE IS ONE CLASS, AND THAT IS THE FINDING, NOT A LIMITATION WE APOLOGISE FOR.  A required
set over the *derivable frontmatter* classes was measured (plan-067 EXP-002) to newly FAIL
**17-18 of 20** currently-green pages with **every single failure an artifact**: ``skill-group``
and ``depends-on-tool`` are emitted by ``skill_pages.py`` into the generated "At a glance" block,
which the manifest already declares unable to drift.  Requiring them of authored prose is a
24-failure false-positive burst that discredits the check on its first run.  Slash sub-verbs were
the ONE class with a clean signal: 0 generated-data artifacts, and the negative control fires and
names the removed verb.

THE PREDICATE IS CORPUS-WIDE (REQ-CHECK-010(c)), NEVER PER-PAGE.  "Documented **somewhere** on
the site."  A per-page predicate manufactures ~30 false failures on ``usage.md`` and
``workflows.md`` alone — 15 of 20 skills go unmentioned in the first, 17 of 20 in the second — and
EXP-003 generated exactly that false positive against itself.  Where a verb is documented only
away from its own skill page, that is reported as an ADVISORY (``off_page``), never as a failure:
it is a curation judgement, and curation is not drift.

PLACEHOLDERS ARE NOT VERBS.  ``/yf-plan <objective>``, ``/yf-markdown-lint [<path> ...]`` declare
an ARGUMENT, not a sub-verb.  A checker that required a page to contain the literal
``<objective>`` would be measuring its own syntax.

VACUITY FLOOR (REQ-CHECK-010(b)).  ``--min-verbs`` (default 15).  ``## Invocation`` was absent
from 12 of 20 skills and used >=4 incompatible shapes before plan-067 Issue 0.2 normalised it, so
a check keyed on it was **silently vacuous for 60% of the corpus** — it read nothing and reported
green.  The floor is what makes a future shape change LOUD instead of silently zeroing the set.

EXIT  0 every declared sub-verb is documented  ·  1 at least one is not  ·  2 INCONCLUSIVE
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check_required_set"
BULLET_RE = re.compile(r"^- `(/[a-z0-9-]+)([^`]*)`")
PLACEHOLDER_RE = re.compile(r"^[<\[]")


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


def invocation_bullets(text: str) -> list[str] | None:
    m = re.search(r"^## Invocation\s*$", text, re.M)
    if not m:
        return None
    tail = text[m.end():]
    nxt = re.search(r"^## ", tail, re.M)
    body = tail[: nxt.start()] if nxt else tail
    return [ln for ln in body.splitlines() if ln.startswith("- `/")]


def declared_verbs(text: str) -> list[str] | None:
    """The sub-verbs a `## Invocation` section declares, or None if it has no section.

    None and [] are DIFFERENT FACTS and are returned differently: no section at all, versus a
    section that declares a bare invocation with no sub-verb (which is legitimate — measured on
    five skills whose whole operator surface is `/skill`).
    """
    bullets = invocation_bullets(text)
    if bullets is None:
        return None
    verbs = []
    for ln in bullets:
        m = BULLET_RE.match(ln)
        if not m:
            continue
        rest = m.group(2).strip()
        if not rest:
            continue
        tok = rest.split()[0]
        if PLACEHOLDER_RE.match(tok):
            continue
        if tok not in verbs:
            verbs.append(tok)
    return verbs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None)
    ap.add_argument("--min-verbs", type=int, default=15,
                    help="vacuity floor on the DERIVED required set (REQ-CHECK-010(b))")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    skills_dir = root / "skills"
    web = root / "web" / "content"
    if not skills_dir.is_dir():
        inconclusive(f"no skills/ under {root}")
    if not web.is_dir():
        inconclusive(f"no web/content under {root} — the corpus cannot be assembled")

    corpus_files = sorted(web.rglob("*.md"))
    for extra in ("README.md", "AGENTS.md"):
        p = root / extra
        if p.is_file():
            corpus_files.append(p)
    if len(corpus_files) < 5:
        inconclusive(f"corpus expanded to {len(corpus_files)} file(s) — vacuous")
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in corpus_files)

    required: dict[str, list[str]] = {}
    no_section: list[str] = []
    for f in sorted(skills_dir.glob("*/SKILL.md")):
        name = f.parent.name
        verbs = declared_verbs(f.read_text(encoding="utf-8", errors="replace"))
        if verbs is None:
            no_section.append(name)
            continue
        required[name] = verbs

    total = sum(len(v) for v in required.values())
    if total < a.min_verbs:
        inconclusive(f"the derived required set holds {total} sub-verb(s), below the "
                     f"--min-verbs floor of {a.min_verbs} — a shape change upstream has "
                     f"silently zeroed it, which is the exact failure this floor exists to "
                     f"make loud (REQ-CHECK-010(b))")

    missing, off_page = [], []
    for name, verbs in sorted(required.items()):
        page = web / "skills" / f"{name}.md"
        page_text = page.read_text(encoding="utf-8", errors="replace") if page.is_file() else ""
        for v in verbs:
            tok = f"{name} {v}"
            on_page = re.search(rf"\b{re.escape(v)}\b", page_text) is not None
            anywhere = (re.search(rf"/{re.escape(name)}\s+{re.escape(v)}\b", corpus) is not None
                        or (on_page and re.search(rf"`{re.escape(v)}`", page_text) is not None))
            if not anywhere:
                missing.append(f"/{tok}")
            elif not on_page:
                off_page.append(f"/{tok}")

    rc = 1 if missing else 0
    if missing:
        print(f"{CHECK}: FAIL — declared sub-verb(s) documented NOWHERE on the site: "
              + ", ".join(missing), file=sys.stderr)

    out = {
        "check": CHECK, "verdict": "FAIL" if missing else "PASS",
        "required_set": {k: v for k, v in sorted(required.items()) if v},
        "required_verbs": total,
        "floor": a.min_verbs,
        "skills_with_section": len(required),
        "skills_without_section": no_section,
        "missing": missing,
        "off_page": off_page,
        "not_checked": [
            "script-verb coverage — irreducibly editorial (40 registrations, ZERO visibility "
            "metadata; no bit in the source to read). The rule makes it visible in review; it "
            "does not mechanise it",
            "generated 'At a glance' data (skill-group, depends-on-tool, depends-on-skill) — "
            "emitted by skill_pages.py and declared unable to drift; requiring it of authored "
            "prose was measured as a 24-failure artifact burst",
            "whether a documented verb is documented CORRECTLY — token presence is the "
            "predicate, intent match is a prose judgement",
        ],
    }
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for m in off_page:
            print(f"ADVISORY {m}: documented on the site but not on its own skill page")
        print(f"{CHECK}: {total} declared sub-verb(s) across {len(required)} skill(s) "
              f"(floor {a.min_verbs}); {len(missing)} undocumented, {len(off_page)} off-page")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

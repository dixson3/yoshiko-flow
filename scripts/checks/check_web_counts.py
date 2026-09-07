#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_web_counts.py — counted-set claims against the shipped skill/formula census.

THE CLAIM CLASS. "`yf` ships **19 skills**", "**utility (7)**", "three shipped standard
formulas" — integer equality against a machine-readable source of truth. plan-066 EXP-001
classed this CHECKABLE and measured 7 live mismatches across 4 files that three well-specified
`DRIFT-CHECK.md` edges (`e-web-skill-counts`, `e-web-formula-set`, `e-web-skill-groups`) all
missed, because those edges were assigned to an LLM prose judge over node sets scoped to two
`.md` pages — so the `.d2` files were structurally out of reach.

SOURCE OF TRUTH. `skills/*/SKILL.md` frontmatter `skill-group`, and
`skills/*/formulas/*.formula.toml` (EXCLUDING `.beads/formulas/`, the staged copy).

CORPUS IS A PARAMETER (`--corpus`), defaulting to `web/content/**/*.{md,d2}` + `README.md` +
`AGENTS.md`. See `_web_corpus.py` for why the last two are non-negotiable.

TWO THINGS ARE CHECKED, NOT ONE:
  * the INTEGER a group bullet claims, and
  * the enumerated MEMBER IDS that bullet lists (pass-1 C13).
A count that is right while the membership is wrong is the exact defect EXP-004 measured in
`architecture.d2` — the corrected `beads group (5)` box still listed the *workflows* skills.

MEMBERSHIP IS CHECKED ONLY WHERE IDS ARE PRESENT, AND THE REST IS **DECLARED**, NOT ASSUMED
(REQ-CHECK-009). Today `architecture.md`'s `utility` and `markdown` bullets carry English
descriptions ("skill authoring, drift checking, OKF folders") rather than backticked ids, so
there is nothing to compare without a hand-maintained translation table. Those bullets are
reported in `not_checked` until plan-066 Issue 4.3 rewrites them to ids. This tolerance is
deliberate: `check_web_counts` must NOT depend on 4.3, because `4.3 -> 4.2 -> 4.1 -> 2.5 -> 2.1`
already exists and the reverse edge would close a cycle and wedge the DAG.

EXIT  0 clean  ·  1 mismatch  ·  2 INCONCLUSIVE (could not run / vacuous corpus)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _web_corpus import DEFAULT_CORPUS, as_int, expand_corpus, repo_root, skill_census  # noqa: E402

CHECK = "check_web_counts"
MIN_FILES = 5   # a corpus smaller than this parsed nothing useful

# "ships **19 skills**", "19 skills", "embedded skills (18)"
TOTAL_RES = [
    re.compile(r"\*\*(\d+)\s+skills\*\*"),
    re.compile(r"\bships?\s+\*?\*?(\d+)\*?\*?\s+skills\b", re.I),
    re.compile(r"\bembedded skills\s*\((\d+)\)"),
]
# "**utility (7)**", "utility group (6)"
GROUP_RE = re.compile(r"\b(beads|markdown|utility|workflows)\s+(?:group\s+)?\((\d+)\)", re.I)
# "three shipped standard formulas", "five shipped formulas"
FORMULA_COUNT_RE = re.compile(r"\b(\w+)\s+shipped\s+(?:standard\s+)?formulas?\b", re.I)

BACKTICKED = re.compile(r"`(yf-[a-z0-9-]+)`")
BARE_SKILL = re.compile(r"\b(yf-[a-z0-9-]+)\b")
# A `·`- or comma-separated run of SHORT names, the form the `.d2` labels use
# ("plan · research · incubator"). Matched only inside such a run, and only against a known
# skill id with its `yf-` prefix stripped, so an ordinary English word cannot be mistaken for
# a member. This is what lets the checker see EXP-004's measured defect: the `beads group (5)`
# box lists the WORKFLOWS skills — count right, membership wrong.
SHORT_RUN = re.compile(r"[a-z][a-z0-9-]*(?:\s*(?:·|,)\s*[a-z][a-z0-9-]*)+")


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def member_region(lines: list[str], idx: int, is_d2: bool) -> str:
    """The text a group's membership list may occupy. THE TWO FORMATS DIFFER, so this branches.

    **Markdown bullets WRAP.** `architecture.md` states `**workflows (3)**` on one line and its
    three ids on the next, so a per-line scan would report `not_checked` for a bullet that does
    enumerate its members — a false "unchecked" is as wrong as a false pass. The region is the
    claim line plus continuation lines up to the next bullet, heading, table row or blank line.

    **`.d2` labels DO NOT WRAP.** A whole label is one physical line, with `\n` as a literal
    two-character escape inside a quoted string. Extending the region to the following lines
    bleeds the NEXT group's members into this group's list and manufactures findings — measured
    on `architecture.d2`, where the `beads` box absorbed `utility`'s ids. So a `.d2` region is
    exactly one line, and the escape is normalized to a real separator first: without that,
    "(8)\nplan" tokenizes as `nplan` and the real member is never seen.
    """
    if is_d2:
        return lines[idx]
    out = [lines[idx]]
    for nxt in lines[idx + 1:]:
        s = nxt.strip()
        if not s or s.startswith(("- ", "* ", "#", "|")):
            break
        out.append(nxt)
    return "\n".join(out)


def normalize_d2(text: str) -> str:
    r"""Turn a `.d2` label's literal `\n` escape into a separator the tokenizer can see."""
    return text.replace("\\n", " · ")


def group_members(region: str, known: set[str]) -> list[str] | None:
    """Ids the region enumerates, or None when it enumerates none.

    None means "a count is stated but no member ids are" — reported as `not_checked`, never as
    a pass. Silence about the remainder is what REQ-CHECK-009 forbids.
    """
    ids = {s for s in BACKTICKED.findall(region) if s in known}
    ids |= {s for s in BARE_SKILL.findall(region) if s in known}
    if not ids:
        short = {f"yf-{tok.strip()}"
                 for run in SHORT_RUN.findall(region)
                 for tok in re.split(r"·|,", run)}
        ids |= {s for s in short if s in known}
    return sorted(ids) or None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", action="append", default=None,
                    help="glob(s) to scan; repeatable. Default: the widened set incl. "
                         "README.md and AGENTS.md")
    ap.add_argument("--root", default=None)
    ap.add_argument("--min-files", type=int, default=MIN_FILES)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    files = expand_corpus(root, a.corpus or DEFAULT_CORPUS)
    if len(files) < a.min_files:
        return inconclusive(f"corpus expanded to {len(files)} file(s), below the floor "
                            f"{a.min_files} — a check over an empty corpus certifies vacuously")

    census = skill_census(root)
    if not census["groups"]:
        return inconclusive("parsed zero skill-group values from skills/*/SKILL.md")
    known = {s for v in census["groups"].values() for s in v}

    findings, unenumerated, claims = [], [], 0
    for path in files:
        rel = str(path.relative_to(root))
        is_d2 = path.suffix == ".d2"
        raw = path.read_text(encoding="utf-8", errors="replace")
        lines = (normalize_d2(raw) if is_d2 else raw).splitlines()
        for i, line in enumerate(lines):
            n = i + 1
            # DE-DUPLICATED across patterns: the three TOTAL_RES forms overlap on
            # "ships **19 skills**", and counting one claim twice would inflate both the
            # claim count and the finding count.
            totals = {m.group(1) for rex in TOTAL_RES for m in rex.finditer(line)}
            for tok in sorted(totals):
                claims += 1
                if int(tok) != census["skills"]:
                    findings.append(f"{rel}:{n}: claims {tok} skills, "
                                    f"census {census['skills']}")
            for m in GROUP_RE.finditer(line):
                group, claimed = m.group(1).lower(), int(m.group(2))
                truth = census["groups"].get(group)
                if truth is None:
                    findings.append(f"{rel}:{n}: names group `{group}`, absent from the census")
                    continue
                claims += 1
                if claimed != len(truth):
                    findings.append(f"{rel}:{n}: group `{group}` claims {claimed}, "
                                    f"census {len(truth)}")
                members = group_members(member_region(lines, i, is_d2), known)
                if members is None:
                    # ISSUE 1.1b / #376 — THE EVASION PATH, and it is a FINDING, not a note.
                    # `wrong` used to sit inside this `else`, so the omission check would have
                    # landed in the ONE BRANCH WHERE THE OMISSION CANNOT OCCUR. A group that
                    # enumerates no member ids was routed to `not_checked` and joined the clean
                    # population — which makes "state a count, list nothing" the cheapest
                    # possible way to evade the rule, and a diagram redesigned with FEWER
                    # enumerated labels does exactly that by accident. "No ids enumerated" and
                    # "checked and clean" are TWO FACTS (#263); this reports them apart.
                    unenumerated.append(f"{rel}:{n}: group `{group}` states a count but "
                                        f"enumerates NO member ids — membership is unverifiable "
                                        f"(#376). List the {len(truth)} member id(s).")
                else:
                    claims += 1
                    wrong = [s for s in members if s not in truth]
                    # ISSUE 1.1 / REQ-CHECK-013 — the OMISSION difference, beside the existing
                    # `wrong`. Measured: deleting two members while leaving the count unchanged
                    # exited 0 under the old rule.
                    missing = [s for s in truth if s not in members]
                    if wrong:
                        findings.append(f"{rel}:{n}: group `{group}` lists non-member(s) "
                                        f"{wrong} — count may be right while membership is wrong")
                    if missing:
                        findings.append(f"{rel}:{n}: group `{group}` OMITS member(s) {missing} "
                                        f"— an omission FAILs (REQ-CHECK-013); the count alone "
                                        f"cannot see it")
            for m in FORMULA_COUNT_RE.finditer(line):
                claimed = as_int(m.group(1))
                if claimed is None:
                    continue
                claims += 1
                if claimed != len(census["formulas"]):
                    findings.append(f"{rel}:{n}: claims {claimed} shipped formulas, "
                                    f"census {len(census['formulas'])} "
                                    f"({', '.join(census['formulas'])})")

    if claims == 0:
        return inconclusive(f"scanned {len(files)} file(s) and found ZERO counted-set claims — "
                            "the matcher, not the docs, is what to fix")

    # An unenumerated group is a FINDING (1.1b), so it gates the exit code. It is ALSO
    # reported under its own key and count, because SC6 asserts `not_checked_groups == 0` and
    # a caller must be able to read that number without parsing prose.
    all_findings = findings + unenumerated
    out = {"check": CHECK, "verdict": "FAIL" if all_findings else "PASS",
           "files_scanned": len(files), "claims": claims, "census": census,
           "findings": all_findings,
           "mismatches": findings,
           "unenumerated": unenumerated,
           "not_checked_groups": len(unenumerated),
           # REQ-CHECK-009(a): the CLASSES this instrument does not cover, in its own output.
           # This key names classes; per-site unchecked groups now live in `unenumerated`,
           # because they are no longer tolerated — they FAIL.
           "not_checked": [
               "script-verb coverage — irreducibly editorial (40 registrations in "
               "plan_manager.py, ZERO visibility metadata; no bit in the source to read)",
               "editorial omission on a prose page, and missing qualifiers — prose judgements, "
               "not integer or set-membership claims",
               "semantic mis-assignment beyond the member-id sets compared here",
           ]}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for f in findings:
            print(f"FAIL {f}")
        for u in unenumerated:
            print(f"FAIL(unenumerated) {u}")
        print(f"{CHECK}: scanned {len(files)} file(s), {claims} counted-set claim(s); "
              f"{len(findings)} mismatch(es), {len(unenumerated)} unenumerated group(s)")
    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

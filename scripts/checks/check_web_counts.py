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

# ---------------------------------------------------------------------------
# COUNT-FREE GROUP DETECTION (plan-067 Issue 7.2, pass-4 C1 / pass-5).
#
# `GROUP_RE` requires a parenthetical count `\((\d+)\)` to even FIND a group. D8's restyle
# FORBIDS parenthetical counts — so after the restyle the four groups in `architecture.d2` were
# not detected at all, and a group that is never DETECTED cannot be reported unchecked.
# MEASURED: deleting a member box from the restyled stack left `check_web_counts` at exit 0 with
# `not_checked_groups: 0`. That is Issue 1.1's exact two-member-deletion defect, reintroduced by
# a change to the DOCUMENT rather than to the checker.
#
# The fix keys detection on the d2 CONTAINER ID alone, count-free, and reads membership from
# TILED CHILD BOXES rather than a `·`-joined list. The reference style is MORE checkable once
# taught: a box label is a cleaner token than a joined string.
#
# Same single-shape assumption as the locally-filed `yf-w57p`: one regex was standing in for
# "what a group looks like", and the answer turned out to be shape-dependent.
# ---------------------------------------------------------------------------
# LEADING WHITESPACE IS ALLOWED: a group container is a container at any nesting depth.
# Anchored at column 0 this missed `architecture-deps.d2`, where the four groups sit inside a
# `skills: {` wrapper — five claims silently vanished and the CLAIM_FLOOR caught it.
GROUP_CONTAINER_RE = re.compile(
    r"^[ \t]*(beads|markdown|utility|workflows)\s*:\s*\{\s*$", re.M | re.I)
CHILD_BOX_RE = re.compile(r'^\s+([\w.-]+)\s*:\s*"([^"]*)"\s*$')


def container_groups(text: str, known: set[str]) -> dict[str, tuple[int, list[str]]]:
    """-> {group: (line_no, members)} for every count-free d2 container.

    A container is `<group>: {` at column 0; its members are the child `id: "label"` boxes whose
    id or label is a known skill. Nested braces end the scan, so a container holding sub-blocks
    contributes only its direct boxes.
    """
    out: dict[str, tuple[int, list[str]]] = {}
    lines = text.splitlines()
    for m in GROUP_CONTAINER_RE.finditer(text):
        name = m.group(1).lower()
        start = text[: m.start()].count("\n")
        members, depth = [], 1
        for ln in lines[start + 1:]:
            depth += ln.count("{") - ln.count("}")
            if depth <= 0:
                break
            cb = CHILD_BOX_RE.match(ln)
            if not cb:
                continue
            for tok in (cb.group(1), cb.group(2)):
                if tok in known and tok not in members:
                    members.append(tok)
        out[name] = (start + 1, sorted(members))
    return out


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
    groups_seen: set[str] = set()
    group_claims = 0
    d2_groups_seen: set[str] = set()
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
                group_claims += 1
                groups_seen.add(group)
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

        # COUNT-FREE CONTAINER FORM (Issue 7.2) — per FILE, and only for `.d2`, because the
        # container shape is a d2 construct. This is DETECTION, not just extraction: the
        # parenthetical-count form above cannot see a restyled group at all.
        if is_d2:
            for gname, (gline, members) in container_groups(raw, known).items():
                truth = census["groups"].get(gname)
                if truth is None:
                    findings.append(f"{rel}:{gline}: container `{gname}` is absent from the census")
                    continue
                d2_groups_seen.add(gname)
                groups_seen.add(gname)
                group_claims += 1
                claims += 1
                if not members:
                    unenumerated.append(
                        f"{rel}:{gline}: container `{gname}` encloses NO recognizable member box "
                        f"— membership is unverifiable. List the {len(truth)} member id(s).")
                    continue
                wrong = [x for x in members if x not in truth]
                missing = [x for x in truth if x not in members]
                if wrong:
                    findings.append(f"{rel}:{gline}: container `{gname}` holds non-member(s) {wrong}")
                if missing:
                    findings.append(f"{rel}:{gline}: container `{gname}` OMITS member(s) {missing} "
                                    f"— an omission FAILs (REQ-CHECK-013)")

    # D2-SCOPED CLAIM FLOOR (Issue 7.2). Every census group must be LOCATABLE in a `.d2`, in
    # either form. If a restyle makes one undetectable, that is the instrument losing its grip —
    # INCONCLUSIVE, never a green.
    stack = [f for f in files if f.name == "architecture.d2"]
    if stack:
        text = normalize_d2(stack[0].read_text(encoding="utf-8", errors="replace"))
        # THE COUNT-FREE TOTAL. D8 forbids `embedded skills (20)`, so the stack can no longer
        # state a total as an integer — and losing that claim IS a real coverage regression, the
        # kind the CLAIM_FLOOR exists to catch (measured: 19 -> 18 the moment the count went).
        # The union of the four containers is the same fact in a form the restyle permits, and it
        # is STRONGER: it checks membership, not just an integer.
        cg = container_groups(text, known)
        if set(cg) == set(census["groups"]):
            claims += 1
            union = sorted({m for _, members in cg.values() for m in members})
            all_skills = sorted({sk for v in census["groups"].values() for sk in v})
            short = [x for x in all_skills if x not in union]
            extra = [x for x in union if x not in all_skills]
            if short:
                findings.append(f"{stack[0].name}: the four containers together OMIT {short} — "
                                f"the stack does not carry the whole census")
            if extra:
                findings.append(f"{stack[0].name}: the containers hold non-census member(s) "
                                f"{extra}")
        legacy = {g.lower() for g, _ in GROUP_RE.findall(text)}
        container = set(container_groups(text, known))
        located = (legacy | container) & set(census["groups"])
        lost = sorted(set(census["groups"]) - located)
        if lost:
            return inconclusive(
                f"{len(lost)} census group(s) are NOT LOCATABLE in architecture.d2 — {lost}. "
                f"Neither the "
                f"parenthetical-count form nor the container form found them, so their membership "
                f"is unchecked rather than clean. A restyle that hides a group from the detector "
                f"is an instrument failure, not a passing document.")

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
           # SC29's POSITIVE clause. `not_checked == 0` is satisfied BY the failure mode — a
           # claim that VANISHES cannot be reported unchecked — so the number that matters is
           # how many groups were actually CHECKED.
           "groups_checked": len(groups_seen),
           "group_claims": group_claims,
           "d2_groups_located": sorted(d2_groups_seen),
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

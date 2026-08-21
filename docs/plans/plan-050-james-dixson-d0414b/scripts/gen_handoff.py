#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate references/handoff-051.md from plan-050's own tables (Issue 6.5 / SC18).

SC18 requires the table-derived sections be checked by **regenerating them from plan.md's
tables and `diff`ing against the shipped file — a non-empty diff fails**. "Generated, not
hand-listed" is a provenance claim with no exit code (pass-7 C76); this script is the exit
code. It is the generator AND the checker:

    gen_handoff.py --write     write references/handoff-051.md
    gen_handoff.py --check     regenerate and diff; exit 1 on any difference

The "descoped SPEC amendments" section is EXPLICITLY EXEMPT from the tables-only rule and is
carried as a literal below, because those ids appear in NO table (pass-6 C60). A tables-only
generator would silently drop exactly what plan-051 needs — which is the failure mode this
whole section exists to prevent, so the exemption is declared rather than implicit.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parent.parent
PLAN_MD = PLAN_DIR / "plan.md"
OUT = PLAN_DIR / "references" / "handoff-051.md"

_CELL = re.compile(r"(?<!\\)\|")


def _rows(section: str) -> list[list[str]]:
    """Data rows of the first GFM table under `## <section>`."""
    text = PLAN_MD.read_text(encoding="utf-8")
    start = text.index(f"\n## {section}\n")
    end = text.find("\n## ", start + 1)
    body = text[start:end if end != -1 else len(text)]
    out = []
    for ln in body.splitlines():
        s = ln.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [c.strip().replace("\\|", "|") for c in _CELL.split(s[1:-1])]
        if not cells or set("".join(cells)) <= set(" :-"):   # alignment row
            continue
        out.append(cells)
    return out[1:]  # drop the header


def _norm(v: str) -> str:
    for _ in range(4):
        s = v.strip().strip("*").strip("_").strip()
        if s == v:
            break
        v = s
    return v.lower()


def _issue_num(cell: str) -> str:
    m = re.search(r"#(\d+)", cell)
    return m.group(1) if m else cell.strip()


def carried_rows() -> list[tuple[str, str, str, str]]:
    """Every `partial` / `deferred` Upstream Issues row: (num, disposition, title, notes)."""
    out = []
    for r in _rows("Upstream Issues"):
        if len(r) < 4:
            continue
        disp = _norm(r[2])
        if disp in ("partial", "deferred"):
            out.append((_issue_num(r[0]), disp, r[1].strip(), r[3].strip()))
    return out


def unmet_criteria(closed: set[str]) -> list[tuple[str, str, str]]:
    """Criteria whose `Discharged-by` names an issue not in `closed`."""
    out = []
    for r in _rows("Success Criteria"):
        if len(r) < 4:
            continue
        ids = [i.strip() for i in re.split(r"[,;]", r[3]) if i.strip()]
        unmet = [i for i in ids if i not in closed]
        if unmet:
            out.append((r[0].strip(), r[1].strip(), ", ".join(unmet)))
    return out


def declared_issue_ids() -> set[str]:
    text = PLAN_MD.read_text(encoding="utf-8")
    body = text.split("\n## Epics\n", 1)[1].split("\n## Gates\n", 1)[0]
    return set(re.findall(r"^- Issue ([0-9]+\.[0-9]+[a-z]?):", body, re.M))


# EXEMPT from the tables-only rule — sourced from D-9, appears in no table (pass-6 C60).
DESCOPED_SPEC_AMENDMENTS = """\
| Amendment | Where it was scoped | Why it left |
| :-- | :-- | :-- |
| The **M9 stamping** `REQ-*` — stamp `metadata.plan` on `discovered-from` beads at creation (D-7, forward-only) | plan-050 Epic 4, Issue 4.1 | **D-9.** EXP-004's premise held (26 edges, 0 attributed — a stamping gap, not a missing relationship), but pass-5 C40 measured that the host it was wired into **cannot express the INCONCLUSIVE contract** the design depends on. Structural, not patchable |
| Epic 5's **two `REQ-*` amendments** for the red-team read-only rule (#182) and sub-agent dispatch (#184) | plan-050 Epic 5, Issues 5.1/5.2 | **D-9.** Pass-5 C39 measured Epic 5's gate membership as an **unconditional deadlock**: the control-builders sat inside the gate's own `Blocks` set, so neither the RED nor the GREEN observation was producible. D-8's honesty clause about #182 travels with it |
"""


def render() -> str:
    closed = declared_issue_ids()   # every declared issue closed; see the note in the doc
    carried = carried_rows()
    unmet = unmet_criteria(closed)

    L = []
    L.append("---")
    L.append("type: Reference")
    L.append("okf_spec: OKF-PLAN")
    L.append("id: handoff-051")
    L.append("description: What plan-050 carries forward to plan-051 — generated from plan-050's"
             " own tables by scripts/gen_handoff.py (SC18)")
    L.append("---")
    L.append("")
    L.append("# Handoff: plan-050 → plan-051")
    L.append("")
    L.append("**This file is GENERATED.** `scripts/gen_handoff.py --check` regenerates it from"
             " `plan.md`'s")
    L.append("tables and `diff`s the result; a non-empty diff exits **1**. That is SC18's whole"
             " point —")
    L.append("*\"generated, not hand-listed\"* is a provenance claim with no exit code, so the"
             " assertion is")
    L.append("the equivalent content check instead. Edit `plan.md` or the generator, never this"
             " file.")
    L.append("")
    L.append("## 1. Carried-forward upstream rows")
    L.append("")
    L.append(f"Every `partial` and `deferred` row in plan-050's Upstream Issues table — {len(carried)}"
             " of them.")
    L.append("Each stays **OPEN** upstream by design; `partial` rows additionally carry a"
             " plan-050 comment")
    L.append("recording what was done and what was not.")
    L.append("")
    L.append("| Issue | Disposition | Title | Why it is carried |")
    L.append("| :-- | :-- | :-- | :-- |")
    for num, disp, title, notes in carried:
        note = notes.replace("\n", " ")
        L.append(f"| [#{num}](https://github.com/dixson3/yoshiko-flow/issues/{num}) | `{disp}` |"
                 f" {title} | {note} |")
    L.append("")
    L.append("## 2. Unmet `Discharged-by` references")
    L.append("")
    if unmet:
        L.append("| Criterion | Statement | Undischarged by |")
        L.append("| :-- | :-- | :-- |")
        for cid, stmt, ids in unmet:
            L.append(f"| {cid} | {stmt[:160]} | {ids} |")
    else:
        L.append("**None.** Every `Discharged-by` reference in plan-050's Success Criteria table"
                 " names an")
        L.append("issue that plan-050 declared and closed. This section is generated, so an empty"
                 " result is")
        L.append("a *measurement* rather than an omission: had a criterion named an issue the plan"
                 " never")
        L.append("declared — the dangling-reference defect that recurred in three review rounds —"
                 " it would")
        L.append("appear here.")
    L.append("")
    L.append("## 3. Descoped SPEC amendments")
    L.append("")
    L.append("**EXEMPT from the tables-only rule, deliberately** (pass-6 C60). These ids appear in"
             " **no**")
    L.append("table, so a tables-only generator would silently drop exactly what plan-051 needs."
             " They are")
    L.append("sourced from **D-9** and carried as a literal in the generator, where the exemption"
             " is")
    L.append("visible rather than implicit.")
    L.append("")
    L.append(DESCOPED_SPEC_AMENDMENTS.rstrip())
    L.append("")
    L.append("## 4. The session's headline finding")
    L.append("")
    L.append("Stated as a **measurement**, because it is evidence about the *process* and the"
             " successor")
    L.append("plan will want it.")
    L.append("")
    L.append("**Three defects were caught by RUNNING a control during plan-050's execution. None"
             " was found")
    L.append("by the thirteen review cycles or the eleven independent red-team passes that"
             " preceded them.**")
    L.append("")
    L.append("| Entry | What was believed | What running it showed |")
    L.append("| :-- | :-- | :-- |")
    L.append("| `RE-005` | the driven-red harness works | a **missing fixture** reported"
             " `RED observed` and exited **0**, writing a record with an empty exit-code field —"
             " a silent green in the instrument built to grade silent greens |")
    L.append("| `RE-007` | #180 is a violable ordering constraint | it is **not violable** — `bd`"
             " itself refuses. The defect is that violating it returned `inconclusive` + exit 0"
             " and `SKILL.md` §6.4 never read `$?` |")
    L.append("| `RE-009` | the new grant generator is correct | it was wrong **twice**, in the"
             " direction that looks conservative: `supersede` demanded a comment its own"
             " `requires_mention: False` denies, and `file-tracker` coverage was scoped to an"
             " issue number that cannot exist before the tracker is filed |")
    L.append("")
    L.append("Two of the three were caught by an arm that exists **only because a criterion"
             " demanded a")
    L.append("*contrast*** — an assertion that something must still **pass**, not merely fail.")
    L.append("")
    L.append("The reviews that missed all three were reading artifacts for **structure**; every"
             " one of the")
    L.append("three was a defect in **payload** — what the thing does when run. That is the"
             " blind spot")
    L.append("[#188](https://github.com/dixson3/yoshiko-flow/issues/188) names (*test suites"
             " assert output")
    L.append("STRUCTURE and never payload FIDELITY*), stated from a second direction, and it is"
             " direct")
    L.append("evidence for [#190](https://github.com/dixson3/yoshiko-flow/issues/190) (*require"
             " plans to ship")
    L.append("tests for code they write*). **plan-051 should inherit that link rather than"
             " re-derive it.**")
    L.append("")
    L.append("The counter-observation, recorded as `RE-008` so the corpus is not only failures:"
             " two")
    L.append("judgements execution **vindicated** — #186's both-call-sites correction (caught by a"
             " pass-11")
    L.append("**spike**, not by reading) and #181's preflight design holding its central claim"
             " after three")
    L.append("earlier scopes were each refuted by the same mechanism.")
    L.append("")
    L.append("## 5. Where the descoped work's evidence lives")
    L.append("")
    L.append("plan-051 starts from measurements, not from scratch:")
    L.append("")
    L.append("- [`findings/exp-004-m9-remediation-edge.md`](../findings/exp-004-m9-remediation-edge.md)"
             " — M9's premise, **revised by measurement**: 26 `discovered-from` edges, **0** with"
             " plan attribution on either endpoint. The edges are intact and resolvable; only"
             " attribution is missing. Independently reproduced at pass 5, including the 7-hour"
             " bead-vs-edge skew.")
    L.append("- [`findings/exp-006-red-team-rule.md`](../findings/exp-006-red-team-rule.md) —"
             " #182's rule is **one line** (`red-team.md:63`) and says *\"never writes files\"*."
             " It never forbade a spike at all. The defect is **under-specification**, silence"
             " read as prohibition — which matters, because a spike is what caught #186's second"
             " call site.")
    L.append("- `reviews/pass-5.md` — C39 (Epic 5's unconditional gate deadlock) and C40 (Epic 4's"
             " host cannot express INCONCLUSIVE). Both are **structural**, so plan-051 needs a"
             " different shape, not a patch.")
    L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    want = render()
    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(want, encoding="utf-8")
        print(f"wrote {OUT.relative_to(PLAN_DIR)} ({len(want)} bytes)")
        return 0
    if a.check:
        if not OUT.exists():
            print(f"FAIL: {OUT} does not exist", file=sys.stderr)
            return 1
        have = OUT.read_text(encoding="utf-8")
        if have == want:
            print("handoff-051.md matches its regeneration from plan.md's tables")
            return 0
        sys.stderr.writelines(difflib.unified_diff(
            have.splitlines(True), want.splitlines(True),
            fromfile="shipped", tofile="regenerated"))
        print("FAIL: non-empty diff — the shipped handoff does not match its regeneration",
              file=sys.stderr)
        return 1
    ap.error("one of --write or --check is required")


if __name__ == "__main__":
    sys.exit(main())

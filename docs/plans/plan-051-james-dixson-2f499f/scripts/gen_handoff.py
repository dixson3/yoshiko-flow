#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate references/handoff-052.md from plan-051's own tables (Issue 4.5 / SC14).

SC14 requires the table-derived sections be checked by **regenerating them from plan.md's
tables and `diff`ing against the shipped file — a non-empty diff exits 1**. "Generated, not
hand-listed" is a provenance claim with no exit code; this script is the exit code. It is the
generator AND the checker:

    gen_handoff.py --write     write references/handoff-052.md
    gen_handoff.py --check     regenerate and diff; exit 1 on any difference

Adopted from plan-050's `scripts/gen_handoff.py` (Issue 6.5 / SC18), which established this
contract.

DECLARED EXEMPTIONS from the tables-only rule. Content that appears in NO table is carried as
a literal below, and the exemption is **declared rather than implicit** — a tables-only
generator would silently drop exactly what the next plan needs, which is the failure mode this
section exists to prevent:

  * the two out-of-scope defects filed by Issue 4.6 (they live in prose under
    "Two defects found by the experiments", not in a table);
  * the process findings recorded in `plan-retrospective.md` (a separate file, not a table);
  * the non-goals (prose bullets).
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parent.parent
PLAN_MD = PLAN_DIR / "plan.md"
RETRO = PLAN_DIR / "plan-retrospective.md"
OUT = PLAN_DIR / "references" / "handoff-052.md"

_CELL = re.compile(r"(?<!\\)\|")


def _rows(section: str) -> list[list[str]]:
    """Data rows of the first GFM table under `## <section>`."""
    text = PLAN_MD.read_text(encoding="utf-8")
    start = text.index(f"\n## {section}\n")
    end = text.find("\n## ", start + 1)
    body = text[start:end if end != -1 else len(text)]
    out: list[list[str]] = []
    for ln in body.splitlines():
        s = ln.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [c.strip().replace("\\|", "|") for c in _CELL.split(s[1:-1])]
        if not cells or set("".join(cells)) <= set(" :-"):      # alignment row
            continue
        out.append(cells)
    return out[1:]                                              # drop the header


def _issue_no(cell: str) -> str:
    m = re.search(r"#(\d+)", cell)
    return m.group(1) if m else cell.strip()


# --- DECLARED EXEMPTION 1: the two out-of-scope defects (prose, not a table) ---------------
OUT_OF_SCOPE = [
    ("`change_validation.py`'s `--changed` repeated-flag drop",
     "`--changed` is declared with `nargs=\"*\"` and **no** `action=\"append\"`, so "
     "`--changed A --changed B` silently validates only `B`. Confirmed at source. A "
     "validation-coverage hole affecting every caller."),
    ("`bd mol burn`'s exit-0-on-cancel with an open gate",
     "A cancelled burn on a wisp with an open APPROVE gate exits **0**, so a scripted burn "
     "cannot tell success from cancellation by exit code. Callers must pass `--force` and "
     "check the OUTPUT, not the exit code."),
]

# --- DECLARED EXEMPTION 2: non-goals (prose bullets, not a table) --------------------------
NON_GOALS = [
    "**The review-cycle counter stays in FILES** — `len(glob('reviews/pass-*.md'))`, monotonic. "
    "A wisp is burnable, so a counter inside one is resettable by `bd mol burn`.",
    "**No parallel review lenses** (D-7). Buildable and spiked; declined for lack of evidence "
    "— 29 review passes across four plans, all sequential.",
    "**No molecule for plan drafting** — it is conversational; beads are pure overhead.",
    "**No `bd mol bond` for plan chaining** — this generated handoff with its `--check` "
    "regeneration diff is already a stronger guarantee than a bond edge.",
    "**M9 itself, the payload-fidelity group (#188/#190), and #165's corpus sweep.**",
]


def build() -> str:
    L: list[str] = []
    L.append("---")
    L.append("type: Reference")
    L.append("okf_spec: OKF-PLAN")
    L.append("id: handoff-052")
    L.append("description: Generated handoff from plan-051 to its successor")
    L.append("---")
    L.append("")
    L.append("# Handoff: plan-051 → plan-052")
    L.append("")
    L.append("**This file is GENERATED.** `scripts/gen_handoff.py --check` regenerates it from")
    L.append("`plan.md`'s tables and `diff`s the result; a non-empty diff exits **1**. That is")
    L.append("SC14's whole point — *\"generated, not hand-listed\"* is a provenance claim with no")
    L.append("exit code, so the regeneration diff is the equivalent content check. Edit `plan.md`")
    L.append("or the generator, never this file.")
    L.append("")

    # --- what shipped -------------------------------------------------------------------
    L.append("## What plan-051 shipped")
    L.append("")
    L.append("| Issue | Disposition | End state | What landed |")
    L.append("| :-- | :-- | :-- | :-- |")
    for r in _rows("Upstream Issues"):
        n, _title, disp = _issue_no(r[0]), r[1], r[2].strip().lower()
        if disp == "include":
            L.append(f"| #{n} | `include` | **CLOSED** | resolved by {r[4] or '—'} |")
    L.append("")

    # --- what stays open ----------------------------------------------------------------
    L.append("## What stays OPEN for the successor")
    L.append("")
    L.append("Every row below is still open upstream. A `partial` row received a comment")
    L.append("recording what plan-051 closed and what remains; a `deferred` row received none.")
    L.append("")
    L.append("| Issue | Disposition | Title |")
    L.append("| :-- | :-- | :-- |")
    for r in _rows("Upstream Issues"):
        n, title, disp = _issue_no(r[0]), r[1], r[2].strip().lower()
        if disp in ("partial", "deferred", "exclude"):
            L.append(f"| #{n} | `{disp}` | {title} |")
    L.append("")

    # --- criteria -----------------------------------------------------------------------
    L.append("## Success criteria and how each was verified")
    L.append("")
    L.append("| # | Criterion | Discharged by |")
    L.append("| :-- | :-- | :-- |")
    for r in _rows("Success Criteria"):
        L.append(f"| {r[0]} | {r[1]} | {r[3]} |")
    L.append("")

    # --- risks --------------------------------------------------------------------------
    L.append("## Risks the successor inherits")
    L.append("")
    L.append("| # | Risk | Severity |")
    L.append("| :-- | :-- | :-- |")
    for r in _rows("Risks & Mitigations"):
        L.append(f"| {r[0]} | {r[1]} | {r[2]} |")
    L.append("")

    # --- EXEMPT: out-of-scope defects ---------------------------------------------------
    L.append("## Out-of-scope defects filed upstream (Issue 4.6)")
    L.append("")
    L.append("*Declared exemption from the tables-only rule: these live in prose, in no table.*")
    L.append("")
    for name, detail in OUT_OF_SCOPE:
        L.append(f"- **{name}** — {detail}")
    L.append("")

    # --- EXEMPT: non-goals ---------------------------------------------------------------
    L.append("## Non-goals — do NOT re-add these")
    L.append("")
    L.append("*Declared exemption: prose bullets, in no table.*")
    L.append("")
    for g in NON_GOALS:
        L.append(f"- {g}")
    L.append("")

    # --- EXEMPT: process findings --------------------------------------------------------
    L.append("## Process findings (from `plan-retrospective.md`)")
    L.append("")
    L.append("*Declared exemption: a separate file, not a table.*")
    L.append("")
    if RETRO.is_file():
        ids = re.findall(r"^###\s+(RE-\d+)", RETRO.read_text(encoding="utf-8"), re.M)
        L.append(f"`plan-retrospective.md` carries **{len(ids)}** entr{'y' if len(ids)==1 else 'ies'}"
                 f"{': ' + ', '.join(f'`{i}`' for i in ids) if ids else ''}.")
    else:
        L.append("`plan-retrospective.md` is absent.")
    L.append("")
    L.append("**The one that generalizes:** a criterion (`SC4b`) was measured green at the issue")
    L.append("that discharged it and was **false two epics later**, because a file added")
    L.append("downstream matched its pattern. Nothing re-checked it — the end-state mandate")
    L.append("covered only criteria that had *fixtures*, and it was caught by an operator")
    L.append("re-measurement rather than by anything the plan shipped. **A criterion is only as")
    L.append("good as the last time something re-ran it.** A successor should re-check every")
    L.append("criterion at completion, not only the ones with a control behind them.")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    built = build()
    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(built, encoding="utf-8")
        print(f"wrote {OUT.relative_to(PLAN_DIR)}")
        return 0
    if a.check:
        if not OUT.is_file():
            print(f"FAIL: {OUT} does not exist", file=sys.stderr)
            return 1
        shipped = OUT.read_text(encoding="utf-8")
        if shipped == built:
            print("OK: the shipped handoff matches its regeneration")
            return 0
        sys.stderr.writelines(difflib.unified_diff(
            shipped.splitlines(keepends=True), built.splitlines(keepends=True),
            fromfile="shipped", tofile="regenerated"))
        print("FAIL: non-empty diff — the shipped handoff does not match its regeneration",
              file=sys.stderr)
        return 1
    ap.error("one of --write or --check is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())

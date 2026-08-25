#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate references/handoff-053.md from plan-052's OWN artifacts (Issue 7.4 / SC22).

"Generated, not hand-listed" is a provenance claim with **no exit code**; this script is the
exit code:

    gen_handoff.py --write     write references/handoff-053.md
    gen_handoff.py --check     regenerate and diff; exit 1 on any difference

**THE CHECK MUST BE SENSITIVE TO CONTENT, and that is not automatic.** plan-051's generator
diffed its output against its own regeneration and reported OK — while counting retrospective
entries with `^###` against entries written `## RE-`. It reported **0 where 6 existed**, and
`--check` was green because it regenerated the *same wrong number* and diffed it against
itself. A check is only as good as the reads underneath it.

Two consequences, both deliberate:

* every derived figure below is read from a **source artifact**, never hard-coded — so a
  source edit moves the output and `--check` fails, which is the whole point;
* the retrospective count uses `^#{2,}`, accepting either heading depth, so it survives a
  heading-level change instead of silently returning to zero. Pinning a reader to exactly one
  depth is what produced the defect in the first place.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parent.parent
PLAN_MD = PLAN_DIR / "plan.md"
RETRO = PLAN_DIR / "plan-retrospective.md"
ASSETS = PLAN_DIR / "assets"
OUT = PLAN_DIR / "references" / "handoff-053.md"
REPO = PLAN_DIR.parent.parent.parent


def section(text: str, heading: str) -> str:
    out, inside = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            inside = ln.strip() == f"## {heading}"
            continue
        if inside:
            out.append(ln)
    return "\n".join(out)


def rows(body: str) -> list[list[str]]:
    out = []
    for ln in body.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= set(":- ") or cells[0] in ("#", "Issue"):
            continue
        out.append(cells)
    return out


def build() -> str:
    text = PLAN_MD.read_text(encoding="utf-8")
    L: list[str] = []

    L.append("# Handoff to plan-053 — from plan-052")
    L.append("")
    L.append("**This file is GENERATED.** `scripts/gen_handoff.py --check` regenerates it from")
    L.append("plan-052's own artifacts and exits 1 on any difference. Every figure below is READ")
    L.append("from a source artifact, never hard-coded — so editing a source moves this file and")
    L.append("the check fails. That is the point: plan-051's handoff passed `--check` while")
    L.append("reporting 0 retrospective entries where 6 existed, because it regenerated the same")
    L.append("wrong number and diffed it against itself.")
    L.append("")

    # --- DERIVED: the plan's own shape ------------------------------------------------
    L.append("## What plan-052 shipped")
    L.append("")
    try:
        doc = json.loads(subprocess.run(
            ["uv", "run", str(REPO / "_shared" / "plan_extract.py"), str(PLAN_DIR), "--json"],
            capture_output=True, text=True, timeout=180).stdout)
        doc = doc[0] if isinstance(doc, list) else doc
    except Exception:
        doc = {}
    L.append(f"- **{len(doc.get('epics') or [])} epics / {len(doc.get('issues') or [])} issues "
             f"/ {len(doc.get('edges') or [])} edges / {len(doc.get('gates') or [])} gates** "
             f"(derived by `plan_extract.py`, never hand-counted)")
    crit = doc.get("criteria") or []
    CLAUSE = re.compile(r"`.+`\s*(?:→|->)\s*exit\s+(?:0|1|2|non-zero)\s*$")
    a = sum(1 for c in crit if CLAUSE.search((c.get("verification") or "").strip()))
    L.append(f"- **{a} of {len(crit)} Success Criteria are machine-runnable** "
             f"({round(100.0 * a / len(crit), 1) if crit else 0}%) in the `REQ-DATA-070` clause "
             f"grammar; the remainder is a declared `manual:` waiver")
    ctl = (ASSETS / "controls.txt")
    if ctl.is_file():
        sets = [l.split("\t")[1].strip() for l in ctl.read_text().splitlines() if "\t" in l]
        L.append(f"- **{len(sets)} controls** — {sets.count('core')} core, {sets.count('ext')} "
                 f"ext, {sets.count('land')} land; the set is GENERATED from plan.md, so no "
                 f"literal count appears anywhere")
    L.append("")

    # --- DERIVED: upstream dispositions ----------------------------------------------
    L.append("## Upstream state this plan leaves behind")
    L.append("")
    ups = rows(section(text, "Upstream Issues"))
    by_disp: dict[str, list[str]] = {}
    for r in ups:
        if len(r) < 3:
            continue
        by_disp.setdefault(r[2].strip("*"), []).append(r[0])
    for disp in sorted(by_disp):
        L.append(f"- **{disp}** ({len(by_disp[disp])}): {', '.join(by_disp[disp])}")
    L.append("")

    # --- DERIVED: the retrospective, with the fix that motivated this file -------------
    L.append("## Process findings (`plan-retrospective.md`)")
    L.append("")
    if RETRO.is_file():
        ids = re.findall(r"^#{2,}\s+(RE-\d+)", RETRO.read_text(encoding="utf-8"), re.M)
        L.append(f"`plan-retrospective.md` carries **{len(ids)}** "
                 f"entr{'y' if len(ids) == 1 else 'ies'}"
                 f"{': ' + ', '.join(f'`{i}`' for i in ids) if ids else ''}.")
    else:
        L.append("`plan-retrospective.md` is absent.")
    L.append("")

    # --- EXEMPT: prose that appears in no table, carried as a declared literal ---------
    L.append("*Declared exemption: the paragraphs below appear in no table and are carried as")
    L.append("literals, so a tables-only generator cannot silently drop what plan-053 needs.*")
    L.append("")
    L.append("## The three defects the controls caught that reading did not")
    L.append("")
    L.append("Each was found by RUNNING something, not by review — which is this plan's thesis")
    L.append("applied to its own execution.")
    L.append("")
    L.append("1. **`plan_extract` sub-key masking.** The sub-key pattern matches against")
    L.append("   `mask_inline_code(raw)`, where a backticked term is blanked to spaces — so the")
    L.append("   whitespace run after the colon greedily swallowed the entire FIRST backticked")
    L.append("   value. Every `touches:` list lost its first path and single-path lists came back")
    L.append("   EMPTY (13 of 31 issues), while `--strict` still reported `unparsed: []` and exit")
    L.append("   0. Same shape as #186 but reached by moved OFFSETS rather than captured masked")
    L.append("   text, so `_verbatim`'s fix did not cover it.")
    L.append("2. **`cmd_closable` dropped `close_reason`.** The bead projection discarded it")
    L.append("   before grouping, so the hoist-tombstone signal was invisible to")
    L.append("   `closable_candidates` NO MATTER HOW the predicate was written.")
    L.append("3. **A control that printed FAIL and exited 0.** A heredoc's exit status was never")
    L.append("   read, so the script fell through to its final `echo`. The control's own subject,")
    L.append("   reproduced inside the control.")
    L.append("")
    L.append("## What plan-053 should pick up")
    L.append("")
    L.append("- **The corpus is unmigrated.** 0 of 186 criteria outside this plan are in the")
    L.append("  clause grammar, so `recheck-criteria` is INCONCLUSIVE almost everywhere and maps")
    L.append("  to `warn` by design. Migrating even a handful of recent bundles would turn the")
    L.append("  re-check from a mechanism into a measurement.")
    L.append("- **`ownership-report` is REPORT-ONLY and partially circular** — it is generated by")
    L.append("  one of the five `plan_manager.py` writers it flags. Do not promote it to a gate")
    L.append("  without an independent measurement.")
    L.append("- **The run-record (#217) is the shared prerequisite** for both the recipe-row")
    L.append("  predicate and the criterion-re-check predicate. Neither is buildable without it.")
    L.append("- **#192 (structure-first plan DSL) now has four ad-hoc sub-keys behind it.**")
    L.append("  plan-052 shipped the third and fourth. A fifth is the point at which the general")
    L.append("  form should win.")
    L.append("")
    return "\n".join(L) + "\n"


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
        return 1
    ap.error("one of --write or --check is required")


if __name__ == "__main__":
    raise SystemExit(main())

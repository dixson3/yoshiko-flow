#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 tests for `_shared/plan_extract.py` (plan-047 Issues 5.1 / 5.2).

Every hazard below is one the plan NAMES, or one measured in the corpus. The point of the
suite is that the extractor **fails loudly rather than degrading** — EXP-003's prototype
silently corrupted its own fidelity number four times before each widening was found.

Run:  uv run _shared/test_plan_extract.py
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
_spec = importlib.util.spec_from_file_location("pe", SHARED / "plan_extract.py")
pe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pe)

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def ex(body: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "plan.md"
        p.write_text(body)
        return pe.extract(p)


HDR = "# Plan: t\n\n**ID:** plan-999-t-aaaaaa\n**Status:** drafting\n\n"

# --- HAZARD 1: `depends-on:` quoted inside INLINE CODE is documentation, not a declaration -
# Measured on plan-047 itself: the prototype's unanchored regex read Issue 5.2's own body
# text and attributed two non-existent edges to it.

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2: mentions (`2.5 depends-on: 2.6, 2.7` — inverted numbering) as a hazard
  - depends-on: 1.1
""")
check("an inline-code `depends-on:` is NOT read as an edge",
      [e["to"] for e in d["edges"]] == ["1.1"],
      f'got {[(e["from"], e["to"]) for e in d["edges"]]}')
check("...and the real depends-on IS read", len(d["edges"]) == 1)

# --- HAZARD 2: an issue depending on a HIGHER-NUMBERED sibling (2.5 -> 2.6, 2.7) -----------
# Correct execution order, inverted numbering. Named by Issue 5.2.

d = ex(HDR + """## Epics
### Epic 2: b
- Issue 2.5: depends on later siblings
  - depends-on: 2.6, 2.7
- Issue 2.6: named later, ordered earlier
- Issue 2.7: likewise
""")
check("a depends-on naming a HIGHER-numbered sibling is valid",
      sorted(e["to"] for e in d["edges"]) == ["2.6", "2.7"] and d["counts"]["unparsed"] == 0,
      f'unparsed={d["unparsed"]}')

# --- HAZARD 3: ids that sort WRONGLY lexically (`6.10` before `6.2`) -----------------------

check("6.10 sorts AFTER 6.2", pe.natural_key("6.10") > pe.natural_key("6.2"))
check("...and lexically it would not", "6.10" < "6.2")
d = ex(HDR + """## Epics
### Epic 6: c
- Issue 6.2: two
- Issue 6.10: ten
""")
check("issues are emitted in natural order",
      [i["id"] for i in d["issues"]] == ["6.2", "6.10"],
      f'got {[i["id"] for i in d["issues"]]}')

# --- HAZARD 4: a MULTI-LINE gate field value (plan-040 L360) -------------------------------
# A parenthetical wraps across two physical lines, putting the colon on a continuation line.
# A one-physical-line parser mis-reads 5+ gates in the corpus.

d = ex(HDR + """## Gates
### Capability Gate: wrapped
- Type: auto
- Condition: something long that wraps
  across a second physical line (with a colon: inside it)
- Test: bash scripts/x.sh
- Blocks: 1.1
""")
g = d["gates"][0]
check("a multi-line Condition is joined, not truncated",
      "second physical line" in (g["condition"] or ""), repr(g["condition"]))
check("...and a colon in the continuation does not start a new field",
      g["test"] == "bash scripts/x.sh", repr(g["test"]))

# --- HAZARD 5: a FENCED multi-line `Test:` (plans 037, 038, 042, 046) ----------------------

d = ex(HDR + """## Gates
### Capability Gate: fenced
- Type: auto
- Test:
```bash
set -o pipefail
bash scripts/y.sh | jq -e '.ok'
```
- Blocks: 1.1
""")
g = d["gates"][0]
check("a fenced Test: value is captured", "jq -e" in (g["test"] or ""), repr(g["test"]))
check("...and is classified `fenced`", g["test_kind"] == "fenced", g["test_kind"])

d = ex(HDR + "## Gates\n### G\n- Type: human\n- Test: *(none)*\n")
check("a sentinel Test: is classified `sentinel`", d["gates"][0]["test_kind"] == "sentinel")
d = ex(HDR + "## Gates\n### G\n- Type: auto\n- Test: bash x.sh\n")
check("a command Test: is classified `executable`",
      d["gates"][0]["test_kind"] == "executable")

# --- HAZARD 6: the REQ-DATA-019 Blocks alphabet, and everything outside it -----------------

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: x
- Issue 2.1: y

## Gates
### G1
- Blocks: 1.1, epic:2, reconcile step
### G2
- Blocks: Issue 2.x / 3.x
### G3
- Blocks: Epics 2, 3, 4
""")
kinds = [b["kind"] for b in d["gates"][0]["blocks"]]
check("the three legal Blocks referents parse",
      kinds == ["issue", "epic", "sentinel"], str(kinds))
check("a WILDCARD referent is unparsed, not guessed",
      any("2.x" in u["raw"] or "2.x" in u["reason"] for u in d["unparsed"]))
check("a PROSE referent is unparsed, not guessed",
      any("Epics" in u["raw"] for u in d["unparsed"]))
check("a bare integer is never a standalone referent",
      not any(b.get("ref") == "3" and b["kind"] == "issue"
              for g in d["gates"] for b in g["blocks"]))

# --- HAZARD 7: a depends-on with a PROSE TAIL is forbidden (D-12 / REQ-DATA-019) -----------

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: x
- Issue 1.2: y
  - depends-on: 1.1 (because the schema must exist first)
""")
check("a depends-on prose tail is reported, not silently split",
      d["counts"]["unparsed"] > 0 and not d["edges"],
      f'edges={d["edges"]} unparsed={d["unparsed"]}')

# --- HAZARD 8: a DANGLING depends-on target ------------------------------------------------

d = ex(HDR + "## Epics\n### Epic 1: a\n- Issue 1.1: x\n  - depends-on: 9.9\n")
check("a dangling depends-on target is reported",
      any("not a declared issue" in u["reason"] for u in d["unparsed"]))

# --- HAZARD 9: a non-conformant bullet in ## Epics is REPORTED, never dropped --------------

d = ex(HDR + "## Epics\n### Epic 1: a\n- Issue 1.1: x\n- some prose bullet that is not an issue\n")
check("a non-issue column-0 bullet in ## Epics is unparsed",
      any("not a conformant issue bullet" in u["reason"] for u in d["unparsed"]))
check("...and the real issue is still extracted", len(d["issues"]) == 1)

# --- HAZARD 10: a lettered epic (plan-012) is read and FLAGGED, not dropped ----------------

d = ex(HDR + "## Epics\n### Epic B: lettered\n- Issue 1.1: x\n")
check("a lettered epic is extracted", len(d["epics"]) == 1)
check("...and flagged as lettered", d["epics"][0]["lettered"] is True)

# --- The live corpus: every plan is handled or its gaps are ENUMERATED ---------------------

plans = sorted((REPO / "docs" / "plans").glob("plan-*/plan.md"))
check("the corpus is present", len(plans) > 40, f"{len(plans)}")
total_unparsed = 0
for p in plans:
    r = pe.extract(p)
    total_unparsed += r["counts"]["unparsed"]
    for u in r["unparsed"]:
        if not (u.get("line") and u.get("reason")):
            check(f"{p.parent.name}: every unparsed item names a line and a reason", False)
check("every unparsed item across the corpus names a line and a reason", True)
check("the corpus DOES have unparsed constructs (so this is not a vacuous pass)",
      total_unparsed > 0, "if this hits 0 the corpus was normalized — re-baseline the claim")

# plan-047 itself must be fully parseable: it is the anchor the schema was derived from.
r = pe.extract(REPO / "docs" / "plans" / "plan-047-james-dixson-dec9ff" / "plan.md")
check("plan-047 extracts with ZERO unparsed", r["counts"]["unparsed"] == 0,
      str(r["unparsed"][:3]))
check("plan-047 has 11 epics / 77 issues / 75 edges / 6 gates",
      (r["counts"]["epics"], r["counts"]["issues"], r["counts"]["edges"],
       r["counts"]["gates"]) == (11, 77, 75, 6), str(r["counts"]))

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

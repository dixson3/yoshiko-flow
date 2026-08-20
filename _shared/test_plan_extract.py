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

# --- plan-048 Issue 1.3: the four RECOVERED historical forms -------------------------------
# Each is recovered because it is UNAMBIGUOUS. Each also asserts the recovery is LOGGED in
# `recovered[]` with a before/after pair — an unauditable recovery is indistinguishable from
# an invented edge (SC1b).

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2 (firing surface): a title parenthetical before the colon
  - depends-on: 1.1
""")
check("RECOVER class D: a title parenthetical does not break the issue id",
      [i["id"] for i in d["issues"]] == ["1.1", "1.2"], str(d["unparsed"]))
check("...and the recovery is logged with a before/after pair",
      any(r["class"] == "title-parenthetical" and "1.2" in r["after"]
          for r in d["recovered"]), str(d["recovered"]))

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2: second
- depends-on: 1.1
- resolves-upstream: #42 (include)
""")
check("RECOVER class C: a column-0 sub-key attaches to the preceding issue",
      [(e["from"], e["to"]) for e in d["edges"]] == [("1.2", "1.1")], str(d["unparsed"]))
check("...and the column-0 resolves-upstream is read too",
      d["issues"][1]["resolves_upstream"] == [{"issue": "#42", "disposition": "include"}])
check("...and both recoveries are logged",
      sum(1 for r in d["recovered"] if r["class"] == "col0-subkey") == 2, str(d["recovered"]))

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first

## Gates
### Capability Gate: g
- Type: auto
- Blocks: Issue 1.1
""")
check("RECOVER class A: an `Issue N.M` prefix inside Blocks is the bare id",
      d["gates"][0]["blocks"] == [{"kind": "issue", "ref": "1.1"}], str(d["unparsed"]))
check("...and the recovery is logged",
      any(r["class"] == "blocks-issue-prefix" for r in d["recovered"]))

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first

## Gates
### Capability Gate: g
- Type: auto
- Blocks: Epic 2, Epics 3
""")
check("RECOVER class B: `Epic N` / `Epics N` normalize to epic:N",
      d["gates"][0]["blocks"] == [{"kind": "epic", "ref": "2"}, {"kind": "epic", "ref": "3"}],
      str(d["unparsed"]))

# --- plan-048 Issue 1.4: classes D and E are REFUSED, reported with LINE NUMBERS -----------
# SC3: this section FAILS if a repair is ever attempted. The assertion is not merely
# "an entry appears in unparsed[]" — it is that NO edge was materialized and NO document
# text was altered. A repair would satisfy the first and violate the second two.

SRC_PROSE_TAIL = HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2: second
  - depends-on: 1.1 (the sync.py mode it relies on)
"""
d = ex(SRC_PROSE_TAIL)
check("REFUSE class D: a prose-tailed depends-on is reported, never split",
      d["edges"] == [], str(d["edges"]))
check("...and it is reported with a line number and a reason",
      len(d["unparsed"]) == 1 and d["unparsed"][0]["line"] > 0
      and "prose tail" in d["unparsed"][0]["reason"], str(d["unparsed"]))
check("...and NOTHING was repaired: no recovery is claimed for it",
      not any(r["line"] == d["unparsed"][0]["line"] for r in d["recovered"]),
      str(d["recovered"]))

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2: second
  - depends-on: 9.9
""")
check("REFUSE class E: a dangling depends-on target is reported",
      any("target" in u["reason"] or "9.9" in u.get("raw", "") for u in d["unparsed"]),
      str(d["unparsed"]))

# --- plan-048 Issue 1.4a: the NEGATIVE mutant ---------------------------------------------
# A construct a NAIVE widening would recover WRONGLY. The assertion is not "it is refused"
# in the abstract — it is that the widened grammar materializes NO edge, rather than the
# readable PREFIX of one. A half-complete edge list is worse than none: a missing edge is
# visible in `unparsed[]`, a partial one reads as complete and silently reorders execution.

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first

## Gates
### Capability Gate: g
- Type: auto
- Blocks: Epic 5 (decommission install.py)
""")
check("NEGATIVE MUTANT 1: a Blocks referent with a trailing qualifier is REFUSED",
      d["gates"][0]["blocks"] == [], str(d["gates"][0]["blocks"]))
check("...and refusing it is NOT the same as recovering `epic:5`",
      not any(b.get("ref") == "5" for b in d["gates"][0]["blocks"]))

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first

## Gates
### Capability Gate: g
- Type: auto
- Blocks: Epics 2, 3, 4
""")
check("NEGATIVE MUTANT 2: a partly-readable Blocks list is refused WHOLE, not partially",
      d["gates"][0]["blocks"] == [],
      f'materialized {d["gates"][0]["blocks"]} — the bare `3`/`4` are an INFERENCE from '
      f'the neighbouring token, not a property of the token')

d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first
- Issue 1.2: second
  - depends-on: Epic 1
""")
check("NEGATIVE MUTANT 3: a `depends-on: Epic N` fan-out is REFUSED, not expanded",
      d["edges"] == [], f'materialized {d["edges"]} — an epic fan-out is not an issue edge')

# A recovery inside a REFUSED value must not be LOGGED either. Measured on the live corpus:
# 6 of 43 staged recoveries sat inside `Blocks:` values that were ultimately refused whole
# (`Blocks: Epics 2, 3, 4`, `Blocks: Issues 3.1, 4.1, 5.1 — i.e. ...`). Logging them would
# relocate the half-complete hazard into the audit log, so the hand audit would adjudicate
# edges that were never materialized.
d = ex(HDR + """## Epics
### Epic 1: a
- Issue 1.1: first

## Gates
### Capability Gate: g
- Type: auto
- Blocks: Epics 2, 3, 4
""")
check("a recovery inside a REFUSED Blocks value is not logged as recovered",
      d["recovered"] == [],
      f'claimed {d["recovered"]} but materialized {d["gates"][0]["blocks"]}')

# --- SC3: the extractor NEVER writes ------------------------------------------------------
# The strongest available statement of "reported, never auto-repaired": run the extractor
# over a file with refused constructs and assert the bytes on disk are unchanged.
import hashlib
with tempfile.TemporaryDirectory() as _td:
    _p = Path(_td) / "plan.md"
    _p.write_text(SRC_PROSE_TAIL)
    _before = hashlib.sha256(_p.read_bytes()).hexdigest()
    pe.extract(_p)
    _after = hashlib.sha256(_p.read_bytes()).hexdigest()
check("SC3: the extractor did not modify the document it refused to parse",
      _before == _after, "the extractor WROTE to its input — repair is forbidden")


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

# --- plan-049 Epic 2 / REQ-DATA-052: the TRAILING-INLINE grammar ------------------------
#
# The positive half is easy and the negative half is the whole point. A widening that
# recovers 72 declarations and also invents one is worse than no widening: an invented edge
# silently reorders execution, and unlike a missing edge it appears nowhere in `unparsed[]`.
# So every mutant below is a form a NAIVE widening would mis-attribute, asserted to be
# REFUSED rather than guessed at.

_TI_OK = """# Plan: t
## Epics
### Epic 1: e
- Issue 1.1: base
- Issue 1.2: a title whose declaration is written at the end of the bullet. depends-on: 1.1
- Issue 1.3: a title that wraps onto a continuation line, where the declaration
  actually lives at the end of the continuation. depends-on: 1.2
- Issue 1.4: the parenthesised form, which 12 of the 89 corpus instances use. (depends-on: 1.3)
"""
r = ex(_TI_OK)
_ti = {(e["from"], e["to"]) for e in r["edges"]}
check("REQ-DATA-052: a declaration at the end of the ISSUE BULLET is recovered",
      ("1.2", "1.1") in _ti, str(sorted(_ti)))
check("REQ-DATA-052: a declaration at the end of a CONTINUATION LINE is recovered",
      ("1.3", "1.2") in _ti, str(sorted(_ti)))
check("REQ-DATA-052: the PARENTHESISED trailing form is recovered",
      ("1.4", "1.3") in _ti, str(sorted(_ti)))
check("REQ-DATA-052: the recovery is AUDITABLE — each carries a before/after pair",
      len([x for x in r["recovered"] if x["class"] == "trailing-inline-subkey"]) == 3
      and all(x["before"] and x["after"]
              for x in r["recovered"] if x["class"] == "trailing-inline-subkey"),
      str(r["recovered"]))
check("REQ-DATA-052: recovering adds NO residue when every referent resolves",
      r["counts"]["unparsed"] == 0, str(r["unparsed"]))

# LETTERED referents. 21 of the 89 use them (plan-012 carries `A.1`, `B.4`). A numeric-only
# widening would recover a BIASED SAMPLE — silently, and looking complete.
_TI_LETTER = """# Plan: t
## Epics
### Epic A: e
- Issue A.1: base
- Issue A.2: lettered referent at the end of the bullet. depends-on: A.1
### Epic B: f
- Issue B.1: base
- Issue B.4: mixed list across epics. depends-on: A.2, B.1
"""
r = ex(_TI_LETTER)
_le = {(e["from"], e["to"]) for e in r["edges"]}
check("REQ-DATA-052: LETTERED referents are recovered, not silently skipped",
      {("A.2", "A.1"), ("B.4", "A.2"), ("B.4", "B.1")} <= _le, str(sorted(_le)))

# --- the negative mutants: REFUSE, do not guess -----------------------------------------

_M_PROSE = """# Plan: t
## Epics
### Epic 1: e
- Issue 1.1: base
- Issue 1.2: a line where the token appears MID-SENTENCE, so where the referent list stops
  is a guess: depends-on: 1.1 and also whatever the reviewer decides later.
"""
r = ex(_M_PROSE)
check("SC6 negative: a MID-LINE declaration with a prose tail materialises NO edge "
      "(where the list ends is unknowable)",
      not [e for e in r["edges"] if e["from"] == "1.2"], str(r["edges"]))
check("SC6 negative: and the refusal is REPORTED, not silently dropped",
      r["counts"]["unparsed"] > 0, str(r["unparsed"]))

_M_NESTED = """# Plan: t
## Epics
### Epic 1: e
- Issue 1.1: base
- Issue 1.2: an issue carrying a nested sub-list
    - a nested item of its own, whose declaration belongs to the SUB-LIST. depends-on: 1.1
"""
r = ex(_M_NESTED)
check("SC6 negative: a declaration on a NESTED SUB-BULLET is not attributed to the issue "
      "(the mis-attribution a naive 'any indented line' rule would make)",
      not [e for e in r["edges"] if e["from"] == "1.2"], str(r["edges"]))

_M_ORPHAN = """# Plan: t
## Epics
### Epic 1: e
- Issue 1.1: base
- some non-conformant column-0 bullet that CLOSES the issue body
  a continuation of THAT bullet, not of the issue. depends-on: 1.1
"""
r = ex(_M_ORPHAN)
check("SC6 negative: a declaration under a column-0 bullet that is not an issue is refused "
      "(the preceding issue is no longer in scope)",
      not r["edges"], str(r["edges"]))

_M_BADREF = """# Plan: t
## Epics
### Epic 1: e
- Issue 1.1: base
- Issue 1.2: names a GATE, not an issue, alongside a real one. depends-on: G1, 1.1
"""
r = ex(_M_BADREF)
check("SC6 negative: ALL-OR-NOTHING holds for the trailing form too — one unresolvable "
      "referent refuses the whole declaration, rather than recovering the readable half",
      not [e for e in r["edges"] if e["from"] == "1.2"], str(r["edges"]))
check("SC6 negative: and that refusal is reported with its referent named",
      any("G1" in u["reason"] for u in r["unparsed"]), str(r["unparsed"]))

# The measured corpus result, pinned so a regression is loud.
_affected = {"plan-006-james-dixson-bf6e21": 7, "plan-007-james-dixson-84da0d": 11,
             "plan-009-james-dixson-996e44": 13, "plan-010-james-dixson-73eebd": 24,
             "plan-012-james-dixson-a99822": 17}
_got = {}
for _name in _affected:
    _r = pe.extract(REPO / "docs" / "plans" / _name / "plan.md")
    _got[_name] = len([x for x in _r["recovered"] if x["class"] == "trailing-inline-subkey"])
check("SC5: at least 60 of the measured 89 inline declarations are recovered as edges",
      sum(_got.values()) >= 60, f"recovered={sum(_got.values())} per-plan={_got}")
check("SC5: the recovery is spread across all five affected plans, not concentrated in one",
      all(v > 0 for v in _got.values()), str(_got))

# SC8. THE HEADLINE CORPUS SYMPTOM: two plans reported `0 unparsed, 0 edges` while carrying
# 20 declarations between them — the residue metric recording the loss as perfection.
for _name in ("plan-006-james-dixson-bf6e21", "plan-007-james-dixson-84da0d"):
    _r = pe.extract(REPO / "docs" / "plans" / _name / "plan.md")
    check(f"SC8: {_name.split('-')[1]} no longer reports 0 edges while carrying declarations",
          _r["counts"]["edges"] > 0, str(_r["counts"]))


print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)

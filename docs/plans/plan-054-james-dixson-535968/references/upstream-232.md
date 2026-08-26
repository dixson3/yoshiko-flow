---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #232: yf-plan: Success-Criterion COMMANDS are never executed before approval — extend D-4's discipline from controls to criteria

- **Number:** 232
- **Title:** yf-plan: Success-Criterion COMMANDS are never executed before approval — extend D-4's discipline from controls to criteria
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Found by **plan-053** (`plan-053-james-dixson-4015d3`) about itself. Not a code defect — a
process one, and the most valuable thing that plan produced.

## The measurement

plan-053 ran **five red-team passes** over **53 concerns**, heavily focused on its Success
Criteria. Three criterion defects still survived into execution. **All three were in criterion
MECHANICS — the command as typed. None was in criterion SEMANTICS.**

| | Defect | Caught at | By what |
| :-- | :-- | :-- | :-- |
| SC16 | wrong command path | planning (pass-2 C19) | someone **ran** it: exit 2 `Failed to spawn` |
| SC6 | `grep` resolved to a ugrep shell function, not `/usr/bin/grep` | Epic 3 | **running** it — it reported a TRUE criterion FALSE |
| SC19 | `json-get epic < plan.md` — a JSON extractor reading markdown | Issue 7.3 | **running** it — `jq: Cannot index object with number` |

Note the pattern in the last column. **The only one review caught was the one someone
executed.**

## The asymmetry that is the actual evidence

- **11 of 11 controls** carried **zero** mechanics defects into execution.
- **3 of 23 verifiable criteria** carried one.

The difference is not care or attention — the same session wrote both, in the same week. It is
**D-4**: every `ctl-` fixture had to be **observed RED before its fix existed**, so no control
could reach execution with a command that does not run. **No equivalent discipline applies to
criteria.**

## The structural point

A Success Criterion is a **claim plus an instrument**. A review that audits only the claim
leaves the instrument unexamined.

`REQ-DATA-024`'s thesis is *"a step with no exit code is not a step."* The corollary plan-053
discovered about itself:

> **A criterion whose command was never executed is not a criterion.**

`REQ-DATA-070` already made criterion `Verification` cells machine-readable — a clause grammar
with explicit polarity. That was the necessary precondition. This is the natural next step:
having made the commands parseable, **run them**.

## Proposed remedy

At the end of PLAN, before `ready-check`, execute every criterion command once and record the
exit code — a `criteria-dry-run` verb, report-only.

**It does not need to gate anything to be useful.** Most criteria will fail pre-work, correctly.
That is fine, because all three defects above are **distinguishable from an honest
not-done-yet failure**:

- `Failed to spawn` / exit 2 — the instrument could not run at all;
- a false negative on a condition already demonstrably true;
- a `jq` type error — the command is malformed, not unsatisfied.

None resembles "not done yet". A report an author reads once before approval would have caught
all three.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/plan-retrospective.md` § RE-004, RE-006, and § RE-007
  (the pattern entry)
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D7

Filed by plan-053 Issue 7.2 (late addition, harvested at land-the-plane).


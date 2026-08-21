---
type: Finding
okf_spec: OKF-PLAN
id: exp-004
status: complete
---

# Finding: What mechanism can record a plan→plan remediation edge, and what is the figure today? (M9, #149)

## Approach Tested

Re-measured the `discovered-from` edge population in this repo's live bead DB (D-5 forbids citing
research 004's cross-repo `0 of 53` as a local figure), then inspected the endpoints.

## Result

**measured:** 1481 beads; **26** `discovered-from` edges; **0** connect two different plans.

But the sharper measurement is why:

**measured: of those 26 edges, ZERO have `metadata.plan` on *either* endpoint** — the stronger form, re-verified independently at the D-9 split (`both endpoints attributed: 0`, `at least ONE endpoint attributed: 0`). An earlier draft recorded only the weaker "both endpoints" claim; pass-6 C64 measured the stronger one and it holds. This matters because this finding is now plan-051's starting evidence and will be read without plan.md beside it. Only 162 of
1481 beads carry the field at all. Sampling the 26 sources:

```
yf-c5642e45  closed  metadata=None  <- yf-911ee361   "Regenerate install-parity golden ..."
yf-44a2936f  closed  metadata=None  <- yf-036717e7   "enforce GFM markdown-lint ..."
yf-9c8224f1  closed  metadata=None  <- yf-dfabdd38   "bdplan §4.3 shows epic blocked by ..."
```

**inferred, and it revises the scope decision:** the cross-plan count is not `0` because plans
never fix each other — three of the titles above are plainly one plan fixing another's defect.
It is `0` because **the question is unanswerable from the data**: the edge exists and resolves,
but neither endpoint declares which plan it belongs to. Every edge is intact; the *attribution*
is missing.

This is a materially different defect from the one M9 names. Research 004 reports "the
remediation relationship exists only in prose"; locally the relationship exists **as a real bead
edge** and is invisible only because `discovered-from` beads are created ad hoc during execution,
without the `--metadata '{plan_issue,plan}'` stamp that REQ-DATA-026 mandates for poured beads.

## Implications for Plan

- **Do not invent a new edge type.** The mechanism exists and is used 26 times. Inventing a
  parallel one would be the M12 "one-directional reconciler" class.
- The fix is a **producer change at one seam**: stamp `metadata.plan` when a `discovered-from`
  bead is created, the same way the pour already stamps poured beads.
- The 26 existing edges are **backfillable** but need adjudication (which plan did each belong
  to?) — that is a separate, hand-judged population and should not be assumed free.

## Recommendations

- Scope M9 as *forward-looking stamping* plus an explicit decision on whether to backfill the 26.
- The check is decidable and cheap: a `discovered-from` bead with no `metadata.plan` is a finding.
- Carry the corrected framing into the #149 comment — "0 of 53" is true but reads as "no plan
  fixes another", which this measurement refutes.

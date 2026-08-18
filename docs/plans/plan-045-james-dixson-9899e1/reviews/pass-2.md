---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-045-james-dixson-9899e1
created: '2026-08-18'
verdict: REVISE
status: resolved
---

# Red-Team Pass 2 — plan-045-james-dixson-9899e1

**Date:** 2026-08-18

## Verdict: REVISE

Twelve of fifteen pass-1 concerns genuinely resolved. Two of three HIGH ones fixed **mechanically**
— the mechanisms were verified, not the claims. But **two Operator Resolutions asserted changes not
present in the artifacts**, and one was falsifiable in a single command.

## Strengths

- **Concern 1 is genuinely fixed and the mechanism works.** `bd ready` returns "open issues with no
  active blockers" — a *closed* blocker is not active, so the `bd close -r` tombstone does unblock
  6.3. Graph extracted mechanically: **45 issues, zero cycles, zero unresolved deps, single root
  `0.1`, single terminal leaf `6.3`.** 2.4a did not perturb it.
- **Concern 2's fix is architecturally right.** REQ-PLAN-032 ("each REVISE cycle yields exactly one
  pass file") makes `pass-*.md` a faithful cycle count. Escalating at N does **not** violate
  REQ-PLAN-030 — the plan sits in `review` with a REVISE verdict, a legal state, not a wedge.
- **Concern 7's fix is the sharpest.** Both Tests now establish their Conditions, and the
  honest-scope note declining to claim self-exercise is the epistemic standard the plan demands.
- **Staleness re-verified at HEAD `04f18cc`:** all eight claimed REQ ids still free (0 hits each);
  `coordinator.md` still closes unconditionally and still says "Wait for operator"; "Operator
  Resolutions" still 0 in `.py`; `bd ready` still returns no gates; `herdr tab create` carries both
  `--no-focus` and `--env`.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| A | **high** | **Resolution 15 claims the portability audit passes. It does not.** `audit` returns `fail` — *"expected 2 pass-\*.md, found 1"* — caused by a **second `review:` bullet** appended to `log.md` for the resolution pass, which `SKILL.md` explicitly forbids: *"do **not** append a second phase-log `review:` line."* Breaks REQ-PORT-006/REQ-PLAN-031; `ready-check` returns `ready: false`. Ironic given Success Criterion 2 asserts this exact invariant | Delete the bullet; re-run `audit` and confirm `pass` before presenting pass-2 |
| B | **high** | **Concern 3 only half resolved. D-2 became five classes; Success Criterion 3 did not.** SC3 still read *"The **four** stop classes are the **only** paths"* with three mechanisms listed. The risk table still said *"the fourth stop class"*. The criterion pass-1 flagged as falsified by Issue 4.3 was verbatim unchanged — the fix landed in the decision table and nowhere the plan is measured | Rewrite SC3 to five classes with all five mechanisms including `max_review_cycles` |
| C | medium | **2.4a under-specified three ways.** (i) **Wrong function attributed** — `_plan_review_line_count` counts `log.md` bullets, **not** `pass-*.md` files; concern A is a live demonstration that the two diverge. (ii) **No reset rule** — `count(pass-*.md)` is monotonic, so once N is reached every later cycle re-escalates forever. (iii) **Escalation has no defined exit** — REQ-PLAN-030 requires a later APPROVE, so "accept as-is" is unavailable | State the counter as `len(glob('reviews/pass-*.md'))`; define the exit (a per-invocation raise, echoed to `log.md` per 2.3) |
| D | medium | **Resolution 4 is one-quarter applied.** Only **2.10** carries the three-edit registration clause; **3.8, 4.6 and 5.6 do not.** Three scripts land unregistered and 6.3 — the terminal leaf — discovers the gap and halts | Add the clause verbatim to 3.8, 4.6, 5.6 |
| E | medium | **The strengthened herdr gate Test is now a mutation but still declared `test_class: probe`.** 3.5 auto-runs the whole probe class; the gate now creates a tab in the operator's live herdr session, and under Epic 5 delegation the child performs it inside the parent's session | Define `probe` as *cheap and self-cleaning* rather than *read-only*, and say so in 3.1's vocabulary |
| F | low | **Resolution 6's third item not applied** — the DRIFT-CHECK taxonomy edge is absent from #145's **Out:** list in both `plan.md` and `upstream-triage.md`. Per the plan's own thesis, a silently-dropped finding recommendation is the drift it exists to fix | Add it to both |
| G | low | Scale line stale: *"~40 issues"*; mechanical count is **45** | Say 45 |
| H | low | **The failed gate bead's own disposition is unspecified.** `bd close` requires `-f` for an unsatisfied gate, so a bare close fails; one is left dangling | State explicitly whether it is left open or force-closed |
| I | low | **`scope-answers.md` still absent** — named in `red-team.md` §Inputs; carried from pass-1's Missing list with no resolution row | Write it, or record in `index.md` that the D-table supersedes it |

## Missing

- **A success criterion for `max_review_cycles`.** Pass-1's C2 recommendation was "the 2.10
  assertion **and a success criterion**." Only the assertion landed. Concern B's rewrite is its home.
- Nothing else new. All pass-1 Missing items are present.

## Gate Assessment

| Gate | Reachable? | Non-vacuous? | Verdict |
| :-- | :-: | :-: | :-- |
| Start Gate (human) | yes | yes | Unchanged; sound |
| herdr probe surface | yes | **yes now** — Test performs a write | Condition/Test gap closed; failure branch enforceable (verified closed beads do not block `bd ready`). Class-mismatch caveat E |
| bd gate corpus readable | yes | **yes now** — asserts non-empty | Sound |
| Reconcile Gate (auto) | **yes** — was the blocker | yes | **Concern 1 genuinely fixed** |

No cycles per `red-team.md:27`. Issue 3.7's text still honors the narrow-not-invert instruction.

## Upstream Assessment

Dispositions backfilled and agreeing row-for-row with `plan.md`; zero empty fields. #113's exclusion
remains the sharpest reasoning in the table. **#149's in-scope claim is now nearly true** — concern 2
is delivered (2.4a), concern 3 delivered *in D-2* but not in the criterion that measures it, so the
triage note citing "the pass-1 fifth stop class" directly contradicted SC3's surviving "four".

## Stepping back

The plan is internally consistent in its reasoning, the DAG is clean at 45 issues, scope is honest,
and the epics are genuinely separable after Epic 1.

> **What went wrong in this pass is narrower and more mundane: the Operator Resolutions table
> over-reports.** Three rows (3, 4, 15) assert completion beyond what landed, and one is refuted by
> a single command. **That is the same failure mode as exp-007 — reporting the outcome intended
> rather than the outcome verified — reproduced inside the plan that exists to fix it.**

None of the nine concerns requires new investigation.

## Operator Resolutions

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| A | Audit fails; resolution 15 over-reported | **Applied and verified by command, not assertion.** The illegal second `review:` bullet was removed from `log.md`; `audit` now returns `pass` with 0 non-pass findings. The over-report is recorded in this file rather than quietly corrected — it is the plan's own thesis turned on its author, and pass-3 should check it as evidence | resolved |
| B | SC3 still four classes | **Applied.** SC3 rewritten to five classes enumerating all five mechanisms (including `max_review_cycles >= N`), with an explicit statement that SC3 and Issue 4.3's write-site list are derivable from each other. Risk table's "fourth stop class" corrected to "stop class 4" | resolved |
| C | 2.4a counter under-specified | **Applied.** Counter restated as `len(glob('reviews/pass-*.md'))` with the `_plan_review_line_count` attribution removed and the divergence cited to concern A. Escalation exit defined as a per-invocation raise echoed to `log.md`; no-auto-reset made explicit and justified | resolved |
| D | Registration clause on 3 of 4 test issues | **Applied.** The three-edit clause now appears on 2.10, 3.8, 4.6 and 5.6 — verified as 4 occurrences | resolved |
| E | `probe` class vs a mutating Test | **Applied.** Issue 3.1 now defines the vocabulary: **`probe` means cheap AND self-cleaning, not read-only**; must leave nothing behind on either exit path; anything mutating shared or operator state is `consent`. Noted that 3.5 auto-runs the whole class, so the definition is load-bearing | resolved |
| F | Taxonomy edge not deferred in writing | **Applied.** Added to #145's **Out:** list in `plan.md`, citing exp-004 item 5 and #145's own split-taxonomy mitigation | resolved |
| G | Scale line stale | **Applied.** Risk table now says 45 | resolved |
| H | Failed gate bead disposition | **Applied.** The gate Instructions now state the failed gate bead is **left OPEN as the record** — not force-closed — since `bd close` needs `-f` for an unsatisfied gate and an open gate with no open dependents is the honest artifact of a deferred epic | resolved |
| I | `scope-answers.md` absent | **Applied.** `index.md` records that scoping was interactive and the D-1…D-8 table supersedes it, so a cold reader does not read the absence as a gap | resolved |

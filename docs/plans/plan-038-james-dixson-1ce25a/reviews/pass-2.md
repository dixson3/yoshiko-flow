---
type: Review
okf_spec: OKF-PLAN
---
## Plan Red-Team: plan-038-james-dixson-1ce25a (pass 2)

Re-review after the pass-1 REVISE. The plan changed structurally — four epics to five, with a
newly-discovered defect (#129) sequenced ahead of the original work — so this is a fresh pass over
the whole document rather than a delta check.

## Verdict: APPROVE

### Strengths

- **The high concern was resolved by measurement, not by argument.** Pass-1 objected that the
  premise ("no in-skill wrapper exists") was asserted but never tested. The revision did not
  rewrite the justification — it ran the commands, confirmed `plan_hoist` = push + local close, and
  recorded the evidence in `findings/exp-03`. That is the correct response to a premise challenge,
  and it is the behavior #114 is asking the review pass to institutionalize.
- **The measurement paid for itself.** Verifying the premise uncovered #129 — a silent
  data-integrity defect in shipped code that no test covered and no user had reported. A plan whose
  red-team pass finds a production bug in the code it was about to modify has justified the review
  cycle several times over.
- **#129 is sequenced correctly and the reason is stated.** Ahead of the routing work, because
  routing the documented procedure onto broken machinery is worse than leaving it unrouted. The
  Objective states this explicitly rather than leaving the ordering to be inferred.
- **The "test the contract, not the implementation" section is the right generalization.** #129
  survived because fixture tests compared emitted strings against expected strings containing the
  same defect. The plan names that failure mode and constrains every new test by it — Issue 2.4's
  "assert no comma appears between ids" is a test the old style could not have produced.
- **Issue 1.4 converts a negative instruction into a checkable contract.** "Section-scoped, not a
  global grep" became "fenced ```bash blocks inside two named sections," declared in the SPEC so
  Issue 5.1 implements against a contract rather than an intuition.
- **The recurrence in concern 4 is noted, not just fixed.** Recording that `partial` dispositions
  keep producing unowned update steps (#110 in plan-037, #117 here) is the kind of observation that
  eventually improves the template rather than being re-solved every plan.

### Concerns

- **The capability-gate test depends on two specific beads staying in a particular state** —
  severity: low
  The gate runs `bd github push yf-m78m yf-252c --dry-run | grep -q 'Pushed 2 issues'`. Both are
  currently mapped and open. If either is closed or unmapped before execution, the gate fails for a
  reason unrelated to #129 — a false negative on the plan's most important gate.
  Recommendation: at execution, pick the two ids from a live `mappings` query rather than
  hardcoding, or treat a gate failure as "investigate which" rather than "the fix regressed". Not
  blocking — the failure mode is a confusing red, not a silent green.

- **Issue 2.2 defers a mechanism choice that Issue 2.4 must then pin** — severity: low
  The fail-closed guard's mechanism (parse push output vs. restructure the executor) is chosen
  during 2.2, but 2.4's tests are specified before that choice exists. If 2.2 picks output-parsing,
  the tests must pin a `bd` output format that is not a stable contract.
  Recommendation: if output-parsing is chosen, record in the SPEC that the parsed string is a
  bd-version-dependent assumption, so a future `bd` upgrade has a documented place to break. The
  plan already has the shape for this (REQ-BUP-050 states the requirement, 2.2 records the
  mechanism); this just asks the assumption be written down.

Both low; neither blocks approval.

### Missing

Nothing blocking. The three pass-1 gaps — an unverified premise, an unspecified check mechanism,
and an unowned #117 update — are all now present and wired into the dependency graph.

One observation rather than a gap: the plan now fixes a bug (#129) that was *found by* the process
the plan improves. That is a good outcome but makes the plan self-referential — Epic 2 fixes the
machinery, Epic 3 routes onto it, Epic 5 guards it. If execution is interrupted mid-way, the
intermediate states are worth understanding: after Epic 2 the machinery is correct but the prose
still instructs hand-runs (safe, non-compliant); after Epic 3 both are correct but unguarded
(correct, unprotected). Neither intermediate state is dangerous, which is the important property.

### Gate Assessment

Four gates: Start, two capability gates, Reconcile.

The new **"emitted push command actually matches beads"** gate is the strongest in either plan
reviewed this session. It tests the precise property whose absence *is* #129, its `Test:` is
executable, and it blocks Epics 3 and 5 — so no routing work proceeds onto unverified machinery.
Its `Instructions:` even name the failure signature ("a missing `✓ Pushed N` line"), which turns a
red gate into a diagnosis. The only weakness is the hardcoded bead ids (low concern above).

The **"`push` verb exists before the prose points at it"** gate carries over from pass 1, and its
`Blocks:` list is now consistent — 3.3, 3.4, and 3.5 all depend on the verb existing, where pass 1
noted 2.5 was inconsistently omitted.

Gate count is proportionate: two capability gates for a five-epic plan, each guarding a real
ordering hazard, neither guarding work that could proceed without it.

### Upstream Assessment

Six issues. The addition of #129 as `include` is well-justified: same file, same axis, discovered
by this plan's own review, and sequenced first on severity grounds.

`#117 partial` remains correctly typed with a specific in/out split, and now has an owner (4.5).
`#105 include` as a rider is still legitimate and now lands in Epic 3 where the routed path exists.
`#106 include` is unchanged. `#102` and `#60` excluded with reasons.

Success Criterion 6 correctly lists three issues to close (#129, #106, #105) and one to update
(#117) — matching the table. The criteria are stated so that failure is detectable: Criterion 1 in
particular names the exact observable (`✓ Pushed 2 issues`) rather than "the fix works."

### Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| 1 | Capability-gate test hardcodes two bead ids | low | acknowledged | At execution, select the two ids from a live `mappings` query, or treat a gate failure as "investigate which bead changed" before concluding the fix regressed. Not blocking. |
| 2 | 2.2's mechanism choice precedes 2.4's tests | low | acknowledged | If output-parsing is chosen for the fail-closed guard, record in the SPEC that the parsed string is a bd-version-dependent assumption. Not blocking. |

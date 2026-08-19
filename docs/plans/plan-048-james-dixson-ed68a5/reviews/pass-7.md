---
type: Review
okf_spec: OKF-PLAN
pass: 7
---
# Red-team pass 7 — plan-048-james-dixson-ed68a5

## Verdict: APPROVE

Both pass-6 blockers are genuinely dissolved, and the H-A fix was verified against the **live**
`_verify_row` rather than against the plan's claim. Nine of eleven lesser resolutions landed in full;
the residue is cosmetic and cannot stop or misdirect execution.

## Part B — mechanical verification (whole bundle, re-run independently)

5 epics, 39 issues, 5 gates, 26 criteria; `unparsed: []`; **no cycles**, single root `0.1`, single
leaf `4.7` whose ancestor set is **all 38** other issues. Zero dangling `depends-on` or
`Discharged-by`. `0.7 ∈ anc(3.1)` ✓, `3.4a ∈ anc(3.4)` ✓. **The R1b residual matches an independent
derivation exactly** (non-bookkeeping `1.1, 2.1, 3.1, 4.4`; bookkeeping `0.1, 0.3, 0.5, 0.7`).
Live corpus re-measure: **150 unparsed across 33 of 48**. `doc_lint --type plan` → PASS, 48 files,
E 0. `audit` pass; `okf.py check` OK; `markdown_lint` clean. SC1's pathspec verified **exit 0**. The
three producer surfaces are exactly the three four-option lines. All 13 upstream issues confirmed
OPEN; #173 defect 2 confirmed live in code.

### H-A re-derived from live code

`_verify_row` today falls through to `inconclusive`, so `deferred` does not halt *now*. Issue 3.4
changes the catch-all to `fail`; **3.4a (verified ancestor of 3.4) inserts explicit `deferred` and
`tracker` branches first**. With `deferred` = pass-on-OPEN and all five rows OPEN, `verify-reconcile`
returns `pass` and the halting step is safe; the catch-all then covers only genuine typos, which is
the intent. **The fix is coherent with what the engine will actually do.**

### H-B re-derived

`test_verify_reconcile.py` already carries parametrized pass/fail tables and a
`test_tracker_row_is_inconclusive_not_fail`. SC33's fixture is a two-line extension of an existing
harness, needs no network, and is gradeable at 3.4a.

## Strengths

- The upstream section is the strongest artifact: 13 rows across three files agreeing on every
  disposition, every non-exclude row carrying an edge or a deliberate non-action.
- The seven mutants are **enumerated concretely** in `findings/exp-005` — an executor need not invent them.
- **Fourth consecutive clean gate-ancestry pass**; `gate-run.sh` separates harness failure from
  capability-absent, and SC10c forces a per-script loop rather than a glob.
- D-5 is not decoration — the 150 / 33-of-48 figure re-measured live, and the "300" refutation is
  reproducible from the finding.
- The R1b self-report is honest and exactly right.

## Concerns (none blocking)

| # | Sev | Concern |
| :-- | :-- | :-- |
| C1 | med | `deferred`'s not-OPEN behaviour undeclared, and the `tracker` analogy is doubly inaccurate — `tracker` is in REQ-CLI-018, not REQ-PLAN-074, and is `inconclusive`, not `pass` |
| C2 | med | SC33's "pass case and fail case" is not literally satisfiable for the report-only literals |
| C3 | med | Issue 0.7 does not say whether `STATUS_SEVERITY` promotion applies to `plan-relations` — if `W → E` fires at `review`, every future plan hard-fails R1b |
| C4 | low | plan.md's 744 cell still has overlapping emphasis (the linter has no rule for it) |
| C5 | low | The `47 → 48` sweep re-based D-4a's 22-of-47, which is **not** re-measurable and disagrees with exp-006 and SC31 |
| C6 | low | Nothing requires the drafted comments to carry the **full** plan id |
| C7 | low | SC9 asserts two of the three producer surfaces |
| C8 | low | `reconciler.md` step 3 has no `deferred` verb |

## Gate Assessment

All five gates structurally sound on the fourth consecutive pass, verified by transitive ancestor
set. Both auto gates route through `gate-run.sh`, authored by `0.6a` which precedes `0.6`, both
preceding every gated node. The Upstream-write gate is human and blocks exactly the two posting
issues. No frontloading miss — each gate sits at the first successor of its evidence.

## Upstream Assessment

Complete and unchanged in quality. 13 rows, 10 non-exclude, all OPEN. Dispositions agree byte-for-byte
between `plan.md` and `upstream-triage.md`. **M1's move of `#113`/`#174` from 4.4 (draft) to 4.5a
(post) is verified in the file.** The five `deferred` rows are a non-action by construction and now
have a matching engine contract.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | med | 0.2 now states the full contract in one line — **OPEN → `pass`, no mention required; not-OPEN → `fail`** — and the `tracker` comparison is corrected to point at REQ-CLI-018, noting tracker is `inconclusive` where `deferred` is `pass` | `main-session` | resolved |
| C2 | med | SC33 reworded to "returns its **declared** verdict … including under a state that would fail a *different* disposition", naming the report-only literals as having no symmetric fail case | `main-session` | resolved |
| C3 | med | 0.7 now requires the promotion decision to be **declared**, with the R1b consequence spelled out and plan-049 named as the first plan graded | `main-session` | resolved |
| C4 | low | The cell split into two sentences; inner emphasis dropped | `main-session` | resolved |
| C5 | low | D-4a restored to **22 of 47**, with the denominator's provenance stated | `main-session` | resolved |
| C6 | low | Issue 4.4 now requires each draft to carry the full plan id, with the `_mentions_plan_id` reason | `main-session` | resolved |
| C7 | low | SC9 extended to all three producer surfaces | `main-session` | resolved |
| C8 | low | 0.2's surface list now includes `reconciler.md`'s step-3 verb — "`deferred`: no upstream action" | `main-session` | resolved |

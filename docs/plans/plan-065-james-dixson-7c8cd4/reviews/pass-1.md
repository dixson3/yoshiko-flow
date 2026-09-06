---
type: Review
okf_spec: OKF-PLAN
description: 'Review pass-1 - plan-065 red-team, verdict REVISE, 14 concerns'
---

# Review pass-1 — plan-065

## Verdict: REVISE

**Status: all 14 concerns resolved.** Re-dispatched as pass-2 (REQ-PLAN-030 requires a later APPROVE before `ready-for-approval`).

## Strengths

- **exp-002's central claim verified at the source, not accepted.** `okf.py:1292` guards the entire
  log-reconciliation block including the strip at `okf.py:1329`; `okf_hygiene.py:786-788` computes
  `src_bul`/`dst_bul` and the halt references only `lost_dates`. Both cited line numbers exact.
  **Had exp-002 been wrong, this plan would destroy history. It is not wrong.**
- **Sandbox spike of the whole Epic 2 repair, end to end.** dry run `halt: phase-log-loss` ->
  `would-backfill`; `--apply` transforms 1/1; `restore --record --apply` round-trips
  **byte-identically**; the stored fingerprint is unchanged. D2 works as specified.
- **Sandbox spike of Epic 1.** exp-001's merged H1s produce the merged text **verbatim** in each
  generated `index.md` `>` line, `authority: plan.md H1`. SC8 achievable as written.
- **Issue 1.3's fingerprint-exclusion claim verified**: `plan_manager.py:3603-3616` discards every
  line before the first `## `; plan-010/013 carry zero `**Fingerprint:**` occurrences.
- Motivation table, R10's vacuity measurement, and D6's justification all reproduce.
- **A de-risking fact the plan does not claim:** all 8 target `README.md` files are the identical
  38-line boilerplate. Beyond the `>` objective line there is nothing bundle-specific to lose.
- DAG clean: 7 epics / 31 issues / 35 edges, zero backward cross-epic edges, no cycles.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | SC6's "before" counts are destroyed before the issue that records them runs; no issue in Epics 0-3 captures pre-transform counts, and D6 names no command (`audit --json` rows carry no finding count; it lives in `okf.py check --json`) |
| C2 | medium-high | No issue commits the backfill, yet D5's rollback depends on that commit; and between 4.2 and any commit the plan states no rollback verb at all |
| C3 | medium-high | SC12 is misclassified as a progress criterion — it is true today and stays true, i.e. a regression criterion like SC9. Also SC2/3/7/8 are "red" today only via `FileNotFoundError`, which is not the same evidence as a checker reporting the condition false |
| C4 | medium-high | SC4/SC5 are `manual:` against the plan's own precedent — Epic 3 already mechanizes a one-shot event via `rehearsal-result.json`. Conflates re-running the apply with re-checking recorded evidence |
| C5 | medium | The rehearsal gate's Test hard-codes four JSON keys Issue 3.4 never specifies; a `KeyError` is indistinguishable from a failed rehearsal. Test path is repo-root-relative while execution may run in a worktree |
| C6 | medium | Issue 0.2's checker has a vanishing input — Issue 2.2 deletes the block it reads, degrading it to a vacuously-green empty comparison. Measured trap: `(?s)` regex matches 38 lines, not 10 |
| C7 | medium | Issue 4.4's "re-apply" is unspecified and would overwrite 4.2's record with a 1-bundle record, destroying record-driven reversal for the other 7 |
| C8 | medium | R6's reindex is a risk-cell mitigation with no issue behind it; Epic 3 adds artifacts after plan-065's index was rendered |
| C9 | medium | `upstream-triage.md` records no dispositions — every field empty, though `index.md` advertises it as the reasoning record |
| C10 | medium | 21 of 31 issues named by no success criterion; starkest is **Issue 0.5**, the negative-control proof, discharged by nothing |
| C11 | low-medium | H1 rewrite leaves `## Objective` untouched, and `_objective()` (`okf_hygiene.py:565`) silently truncates a soft-wrapped H1 |
| C12 | low | Closing paragraph misattributes the checkers — five, not four, authored by 0.1-0.4b not 2.3/5.4/5.5 |
| C13 | low | Fingerprint stability asserted for 3 of 8 bundles; reviewer measured the other 5 unchanged, but the plan does not |
| C14 | low | Epic 3's sandbox holds only the 8 bundles; Epic 4 runs over 70, never exercising the classify-and-skip path |

## Missing

- An issue capturing pre-transform per-bundle finding counts (C1)
- An issue committing the backfill (C2)
- A pre-commit rollback route for the window between apply and commit
- An issue reindexing plan-065's own bundle before 5.3 (C8)
- A success criterion for Issue 0.5's negative controls (C10)
- Record-path discipline for 4.4's re-apply (C7)
- A statement of what the transform deletes (the 8 boilerplate `README.md` bodies)

## Gate Assessment

**Sandbox rehearsal green** — REACHABLE, no cycle: evidence produced by 3.4 in Epic 3, gate blocks
`epic:4`. Sits at its earliest legal position. Two defects: unspecified keys (C5) and an implicit
cwd assumption. Note it reads a file the same session writes — a **record, not a guarantee**;
Issue 3.5's `legacy_before == 8` is the only thing between it and a self-fulfilling green.

**Corpus apply authorization** — sound, Instructions correctly worded. But **Epics 1-2 mutate three
completed plans before any capability gate fires**; only the Start Gate authorizes that. Risk is
genuinely low (`git revert` reverses it) but the plan should say the content edits are ungated
**by design** rather than leave it implicit.

**Start Gate / Reconcile Gate** — standard, correct.

## Upstream Assessment

Dispositions reasonable and specific; #295's partial has a genuinely specific in/out split (SC19 in,
SC24 out, stays open) and 6.2 correctly says *update*, not close. **Coverage of #359's four verbatim
acceptance criteria is complete** — and SC3 correctly strengthens past the FULL tier's bare check.

Two gaps: `upstream-triage.md` is an empty template (C9); and D3's safety depends on Issue 4.4 also
passing no `--root`, which its text does not say.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Added Issue 0.6 capturing pre-transform counts to `findings/finding-counts-before.json`; 5.2 now `depends-on: 0.6`; D6 amended to name `okf.py check <bundle> --json` and `len(findings)` (verified: plan-010 -> 12). SC6 is now command-form via `plan065_finding_counts.py` (Issue 0.4e). | `main-session` | `resolved` |
| C2 | medium-high | Added Issue 4.3a committing the backfill as one commit; 4.4 now depends on it. D5 amended to name the pre-commit rollback route explicitly (`git checkout -- docs/plans && git clean -fd docs/plans`). | `main-session` | `resolved` |
| C3 | medium-high | SC12 moved to the regression group beside SC9, with a paragraph explaining why. Added Issue 0.5b and SC14: each progress checker is run against the pre-transform tree and its FALSE report recorded, so the evidence is not a `FileNotFoundError`. | `main-session` | `resolved` |
| C4 | medium-high | Accepted in full — the reviewer is right that this was the REQ-PLAN-080 conflation the plan itself warns about. SC4/SC5/SC6 are now command-form against `restore-roundtrip.json` / `apply-result.json` / `finding-counts-before.json`, with checkers authored in Issues 0.4c/0.4d/0.4e. Only SC10/SC11 (outward-facing writes) and SC13/SC14 (one-shot observations) remain `manual:`. | `main-session` | `resolved` |
| C5 | medium | Issue 3.4 now names all four keys and their types verbatim, states that a `KeyError` is indistinguishable from a failed rehearsal, and records the Test's checkout-root cwd assumption. | `main-session` | `resolved` |
| C6 | medium | Issue 0.2 now requires the ten bullet strings embedded literally (or read via `git show <base>:...`), an explicit `len(expected) == 10` assertion, and carries the reviewer's measured `(?s)` trap (38 lines matched, not 10) as a warning. | `main-session` | `resolved` |
| C7 | medium | Issue 4.4 now states the re-apply MUST write to a SECOND record path and explains why: `backfill` has no per-bundle selector, so overwriting 4.2's record would leave the other 7 bundles with no record-driven reversal. | `main-session` | `resolved` |
| C8 | medium | Added Issue 5.2b reindexing this plan's own bundle, listing the six artifacts Epics 0-4 add; 5.3 now `depends-on: 5.2b`. | `main-session` | `resolved` |
| C9 | medium | All six dispositions and their reasoning filled in `upstream-triage.md`, mirroring plan.md's table. Verified: 6 filled, 0 empty. | `main-session` | `resolved` |
| C10 | medium | Added SC13 (each of the eight checkers observed exiting non-zero on a mutated input, evidence in `findings/negative-controls.md`) discharged by 0.5, and SC14 discharged by 0.5b. The plan's anti-vacuity guard now has criteria behind it. | `main-session` | `resolved` |
| C11 | low-medium | Issues 1.1/1.2 now require the H1 to remain ONE PHYSICAL LINE, citing `_objective()` at `okf_hygiene.py:565`; Issue 1.4's byte-for-byte `reconciled_objectives[].to` comparison is named as the truncation check; 1.1 also requires reading `## Objective` to confirm the imported facts are already stated there. | `main-session` | `resolved` |
| C12 | low | Corrected: eight checkers (not four), authored by Issues 0.1-0.4e and proven by 0.5; 2.3/5.4/5.5 merely discharge the criteria that consume them. | `main-session` | `resolved` |
| C13 | low | Issue 5.4 now asserts fingerprint stability for ALL EIGHT bundles, noting that 1.3/2.4 cover only three and nothing had measured the other five. | `main-session` | `resolved` |
| C14 | low | Issue 3.1 now states the scope limit explicitly — the sandbox holds only the 8, never exercising the classify-and-skip path over the 62 conformant bundles — and names Issue 4.3's `mixed_run == false` as what covers it. | `main-session` | `resolved` |

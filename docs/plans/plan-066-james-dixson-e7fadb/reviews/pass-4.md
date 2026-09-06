---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 4: APPROVE with one medium-high must-fix. Phantom streak broken; all 11 pass-3 resolutions verified in the artifact."
id: pass-4
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
verdict: APPROVE
---
# Red-team pass 4 — plan-066-james-dixson-e7fadb

## Verdict: APPROVE

With one medium-high must-fix before pour (C1, a one-line correction, fully specified) and five
minor. **No high-severity finding; no basis for a fifth cycle.**

## Reviewer disclosure — an unintended repository write, reverted

`plan_manager.py review-loop-check` **appends** a `judgement:` echo to `log.md` as a side effect —
it is not read-only. The reviewer removed exactly the line it added and verified `log.md`
byte-restored (836 B, single occurrence). Recorded here because it matters for future passes:
**`review-loop-check` is not safe for a read-only reviewer.**

## Strengths (executed, not asserted)

- **PHANTOM CHECK: all 11 pass-3 resolutions landed in the artifact** — verified against file text,
  not against the resolutions table. **The two-cycle phantom streak is broken.**
- **Every mechanical gate green.** `audit` → `pass` (20 findings, all `warn`, zero `fail`).
  `ready-check` → the *only* blocker is the pass-3 REVISE verdict itself. `plan_extract --strict` →
  exit 0, `unparsed: []`, `recovered: []`. `doc_lint` → `PASS` on all 10 selected bundle files,
  **zero `E`** (`index.md`/`log.md` correctly `not-selected`). `gate_consistency` → `PASS, 6 gates`.
- **DAG independently re-derived:** 69 edges, no cycle, no self-edge, no dangling target.
- **Zero false PASSes.** `recheck-criteria` → 26 clause + 1 correctly-parsed `manual`, **26/26
  FALSE**, `evaluated_fraction 0.963`.
- **The uncovered list agrees with TWO independent instruments** — the extractor derivation and
  `doc_lint`'s R1b both emit exactly the ten the prose names. Pass-3 C8 closed.
- **SC10 verified DISCRIMINATING by spike.** Two renders → identical `8ce43d48…`, reproducing
  EXP-004's digest to the byte; committed `lifecycle.png` is `c3008a16…`. SC10 **fails today and
  passes only after 5.3**. Installed `d2` is `v0.8.2`, equal to the pin, and `render.py`'s defaults
  are literally the pinned flags.
- **Issue 0.4 mandate (a) is a verified precedent**: `plan065_checks.py bogus-verb` → exit **2**.
- **Every measured premise re-confirmed on today's tree** — `grep -c 'web/' CHANGE-VALIDATION.md`
  → 0; no workflow mentions `change_validation`; `ci.yml` has no `paths:` (SC20's inversion is
  right); no `PAGE_PATHS` (R15 stands); the README/AGENTS drift; and `e-okf-version-pin`'s §2
  category is genuinely out-of-vocabulary — Issue 3.6 is right, and does **not** conflict with 3.2's
  use of `value-equal` as a §3 *Contract* term (different column, different vocabulary).
- **#317 coverage is complete** — all 14 Class-A rows, both UNVERIFIABLE items, all 6 Class-B items,
  all 5 Scope bullets and all 4 Acceptance bullets map to a named issue.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium-high | **SC26 is UNSATISFIABLE — pass-3 C3's two remedies cancel.** 0.4b specifies `== set(SUBCOMMANDS) - {'verbs-match'}`. The carve-out was right when *no* criterion ran the verb — but the same remediation added **SC26**, whose Verification cell invokes it. Measured: the plan's verb set is 24 **and contains `verbs-match`**; the RHS excludes it. LHS ≠ RHS by construction, forever, surfacing only at completion. | Delete the carve-out. The bare equality is now exactly correct **because** SC26 runs the verb. |
| C2 | medium | **Issue 8.4b is an ordinary DAG bead instructed to run post-merge, with nothing enforcing it.** `depends-on: 0.5, 8.3` means a coordinator dispatches it inside the execute worktree. Running it there adds rows `CHANGE-VALIDATION.md:63-74` calls structurally unsatisfiable from a worktree. It is on the uncovered list, so no criterion detects a mis-timed run. Pass-3 C5 moved the deliverable; it did not bind the timing. | Add a hard guard: HALT unless HEAD is `main` and the plan branch is merged. |
| C3 | low-medium | **Stale internal counts — in a plan whose subject is count drift.** SC26 and the uncovered note say "the 22 criteria"; measured, 24 verbs route through the script. R3 says "0 of 26 criteria"; there are 27, and SC1 does mention Pelican (R3's substantive claim still holds). | Drop the numerals or state them as derived-at-write-time. |
| C4 | low | **A retracted claim survives as the section's closing sentence.** Lines 371-374 state that "0.4 was covered via 0.4b" was FALSE; line 380 then closes with "Issue 0.4 is likewise covered, by SC-verb agreement via 0.4b." Two paragraphs edited in different cycles now disagree on the page. | Delete the trailing clause. |
| C5 | low | **Issues 6.1 and 6.2 name no target file**, while SC13 asserts "the authored file exists" and SC15 asserts "every page Epic 6 authored" rendered. 6.3/6.4 name theirs. | Name `web/content/skills/yf-plan.md` explicitly. |
| C6 | low | **Four criteria may collapse into SC5.** If `harness-sites`/`backend-sites`/`group-membership`/`formulas-diagram` merely re-invoke the Epic-2 checkers, SC7/SC8/SC9/SC23 assert nothing beyond SC5, and their site-specific language is prose no criterion checks. | State in 0.4 that these verbs assert the enumerated sites and literals BY NAME. |

## Missing

Nothing material. Two acknowledged softnesses, previously reviewed and deliberately retained:
**SC24** (`diagram-orphans`) is satisfiable with zero work, its value limited to catching a newly
added `.d2`; and the checker corpus excludes `skills/*/SKILL.md`, so the same harness-path claim in
~7 skills' `SKILL_DIR` fallback blocks stays out of scope — **correctly**, since those lists
legitimately name the legacy roots the resolver still searches, and a widened corpus would
false-positive on them. Issue 4.6 reaches into one `SKILL.md` by hand, which is the right shape.

The pass-3 residue on **#317's two `resolves-upstream` dispositions** remains open. It is
correct-by-design (partial repair, then full close) and unit-tested; one pour-time verification
would retire it.

## Gate Assessment

`gate_consistency.py` → **PASS, 6 gates, 0 findings**, corroborated by an independent DAG
derivation. All four capability gates **reachable and at their earliest legal position**. Build
green's evidence is Epic 1, which *is* the evidence — not hoistable further. Checkers-fail-capable
carries a deliberate asymmetry that survives inspection: 2.6/2.7/2.8 depend on 4.9/5.3 inside the
blocked epics, but the gate's condition depends only on 2.5 → 2.1-2.4, so **there is no evidence
cycle**. Both `--min-checkers 4` floors agree with the four shipped checkers, and the floor lives
**in the test**, not only in SC4 — the one lever closing EXP-001's checker-B failure mode.

## Upstream Assessment

Dispositions unchanged and sound. D3's four folds each map to a named issue. #247/#263 stay
`partial`; #273/#312/#365 excluded with reasons that hold. The five `include` rows carry `_TBD_` —
correct at `drafting`, discharged by 8.5 before `reconciling`. The Upstream write authorization gate
correctly fences every outward-facing write behind operator consent.

## Resolutions

All 6 resolved by the main session. Every edit applied through the asserting helper.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium-high | **Fixed.** The carve-out is deleted; 0.4b now specifies the bare equality, and its rationale is inverted to state *why*: the invariant holds only while a criterion executes `verbs-match`, which is exactly what SC26 guarantees. A genuine logical contradiction between two remedies from the same cycle — each correct alone. | `main-session` | `resolved` |
| C2 | medium | **Fixed.** Issue 8.4b carries a hard guard — halt unless HEAD is `main` and the plan branch is merged — with the `CHANGE-VALIDATION.md:63-74` citation and plan-060's `gate-plan060-figures` precedent recorded inline. | `main-session` | `resolved` |
| C3 | low-medium | **Fixed.** Both hardcoded counts removed in favour of derived phrasing, with a note that a numeral in a plan shipping a count-drift checker is the thesis firing inside the plan. R3's claim restated to what actually holds: no criterion embeds a *piped* pelican invocation. | `main-session` | `resolved` |
| C4 | low | **Fixed.** The trailing retracted clause deleted; the preceding paragraph already carries the correct account. | `main-session` | `resolved` |
| C5 | low | **Fixed.** Issues 6.1 and 6.2 now name `web/content/skills/yf-plan.md`, the site #317 cites at `:96-102`, so SC13/SC14/SC15 have a determinate subject. | `main-session` | `resolved` |
| C6 | low | **Fixed.** Issue 0.4 gains mandate (d): the site-specific verbs must assert their enumerated sites and literals by name, never delegate to the Epic-2 checker — otherwise they assert nothing beyond SC5. | `main-session` | `resolved` |

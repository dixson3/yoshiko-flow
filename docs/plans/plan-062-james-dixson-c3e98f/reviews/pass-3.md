---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 3 on plan-062. Verdict REVISE with 10 concerns (C27-C36), three high. Confirmed all 11 pass-2 resolutions mechanically real. HEADLINE: the C24 fix introduced unescaped pipes into SC13, breaking the table row so the criterion is silently never evaluated — the plan reproducing its own headline defect class for the second time. Also: three capability gates now exist while Issue 0.0, R9 and SC14 all say BOTH; and index.md omits upstream-266.md, leaving the repo FAST and FULL tiers RED.'
---
# Red-Team Pass 3 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

## Strengths

**All eleven pass-2 resolutions re-measured and mechanically real.** Gate 1 discriminates
(measured 1 → 0 in a sandbox with `execute.worktree: false`). Issue 0.0's `bd update --metadata`
mechanism works and reads back. #266 is in **all three** places and **the dispositions survived
the `triage` regeneration**. `check_amendment_log.py` spiked all three directions (2 today, 0
with a full entry, 1 with an id omitted). C19's lock reasoning verified on the source:
`_landing_lock_release` is called inside `_land_l4_commit_merge` (`:8931`) and is keyed on
plan+host with no PID.

Structure independently confirmed: 30 issues, 5 gates, `unparsed: []`, **zero cycles, zero
dangling `depends-on`**. All ten pytest clauses exit **5**, never 2. Forward resolution correct
against the real tables. **Resume-first ordering intact** (`2.1 depends-on 1.2`).

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C27 | high | **SC13's pipes are UNESCAPED, so the row is broken and the criterion is silently never evaluated — the plan reproducing its own headline defect.** C24's fix introduced `\| sort -u \| wc -l` without GFM escaping. Measured: `plan_extract` parses `discharged_by` as `['sort -u']`; `doc_lint` emits a `verification-clause` W plus three `R1b` W's — **issues 0.3, 0.4, 0.5 are named by no criterion**. In `recheck-criteria`, `kind != "clause"` → `not-evaluated`, not counted in `class_a`, so it is invisible at L5 and L11 and `--require-evaluated` stays green. | Escape the pipes. Verified in a sandbox: `discharged_by` becomes `['0.3','0.4','0.5']` and doc_lint goes 4 W → **0 W**. |
| C28 | high | **There are THREE capability gates, but Issue 0.0, R9 and SC14 all say "BOTH" / `-ge 2`.** C16's gate was added without propagating the count. An agent following 0.0 literally sets metadata on two of three; the third is classified `manual` → INCONCLUSIVE → never runs — **and SC14 stays GREEN at `-ge 2`**. The likely odd one out is C16's gate, which blocks `1.1`, the entire critical path. C16 and C17 fail together and neither criterion notices. | `grep -c '^### Capability Gate:'` = **3**. Change 0.0 and R9 to "all three", SC14 to `-ge 3`. |
| C29 | high | **`index.md` omits `references/upstream-266.md`, making the repo's FAST *and* FULL tiers RED right now.** Direct collateral from the late `triage` re-run: FAST was fixed at 15:40, `triage` wrote the file at 15:41, and the check was never re-run. Measured: `check_okf_index_drift.py --min-roots 30` → exit **1**, sole drifting bundle plan-062. FULL tier run end-to-end (91 s): **`status: fail`, first_failure `okf-index-drift`.** SC15 cannot pass and **no issue owns the fix**. | Add a real descriptive bullet (not a bare `reindex --write` one), re-run, confirm exit 0. Nothing else drifted: `check_frontmatter` 43 files clean, description coverage 9/9. |
| C30 | medium-high | **Gate 1 is correctly conditioned but its remediation is not achievable in the session that trips it.** §5.2a orders pour → **`worktree ensure`** → §5.2c sweep, so by evaluation time `.worktrees/plan-062` exists and the coordinator is already in worktree mode. §5.2c says a failed gate narrows but does not stop, and Gate 1 blocks only `1.1` — so Epic 0 and **Epic 3, which edits `plan_manager.py`**, proceed in worktree mode while the gate sits red. Setting the config mid-session does not re-decide the mode. | (a) State in **Approach** that the config must be written **before `/yf-plan execute` is invoked**, with the command. (b) Rewrite Gate 1's Instructions so the remediation is real: set the config, remove `.worktrees/<plan-id>`, restart from §5.2. (c) Widen `Blocks` to `1.1, 3.1`. |
| C31 | medium | **The repo's own `gate_consistency.py` returns FAIL on this plan and no pass had run it.** Arm 1 flags Gate 2 because its Instructions name **2.1**, the issue it blocks. Evidence actually comes from 2.0, so it is a false positive by the letter — but it is the check this repo ships for exactly this property. | Reword to reference the *work*, not the blocked id. Verified in a sandbox: `verdict: PASS`, exit 0. |
| C32 | low-medium | **SC15 makes every `recheck-criteria` run pay the FULL tier**, on top of L3 — three FULL-tier runs per landing. The per-criterion cap is 300 s and a green run's duration is unmeasured (a failing run reached row 14 of ~60 in 91 s). A timeout records FAIL, and at L11 that halts past the irreversible boundary. | Make SC15 `manual:` — recorded by Issue 5.3, with L3 gating the landing on the same tier. |
| C33 | low-medium | **Gate 3 is ceremony.** Its Test is byte-identical to SC4's, `Blocks: 5.5` is reachable only after 4.1 closes, and `recheck-criteria` re-evaluates SC4 at L5 and L11 anyway. | Hoist to `Blocks: 4.5`, where the L7-partial resume case first depends on the property, or delete. |
| C34 | low | **SC14 is repo-wide and does not check `cwd`** — the text says "`test_class` **and `cwd`**" but the command greps only `test_class`, and the list is unscoped, so two gates from another open plan would satisfy it. | Assert both keys; note that Issue 0.0 is the scoped check. |
| C35 | low | **Two pass-2 "Missing" items were never tracked**, having sat outside the Concerns table and so received no Resolutions row: `findings/exp-002`'s description still says "the two must land together", superseded by resume-first; and Issue 2.1 still omits that `manifest` is already in scope in `land_cmd` — which is *why* "~40 lines" is true. | Fix both. |
| C36 | low | **The L0 exemption leaves acquire/release unpaired on a post-L4 resume** — L0 always re-executes while L4 (which releases) is skipped. Self-healing via dead-PID reclaim, but unmentioned. | One sentence in Issue 1.1, or assert lock state in Issue 4.2's halt-at-l8 case. |

## Missing

- **No issue owns `index.md`** — C29 is a defect SC15 will fail on with no node fixing it.
- No `gate-plan062-*` rows in `CHANGE-VALIDATION.md`, though plan-060 set the precedent at `:136-137`.
- `check-req-coverage.py --min-issues 30` reports INCONCLUSIVE here (23 non-Epic-0 issues vs floor 30) — not a defect, but a plan-060-style coverage row copied verbatim would not certify.

## On over-constraint

**The plan is NOT over-heavy, with one exception.** 30 issues for ~115 production lines is
proportionate: Epic 0's seven are the repo's mandatory SPEC-first ritual and Epic 4's seven are
the tests whose absence is the entire motivation. Three criteria (SC10, SC10b, SC11) are green at
drafting, but all three are regression pins and legitimately so. **Gate 3 is the one piece of pure
ceremony.** The five gates do not over-constrain; the concentration of *unenforced preconditions*
is the real weakness, and C28 + C30 are where it bites.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| Start Gate | yes | Fine; natural home for C30's pre-execute precondition. |
| Cap Gate 1 (worktree) | **yes, discriminates — measured 1→0** | Condition right; **placement wrong relative to `worktree ensure`** (C30), and most exposed to C28's off-by-one. |
| Cap Gate 2 (seam) | yes | Runnable; red today exactly as its Instructions say. Flagged by `gate_consistency.py` (C31) — wording only. |
| Cap Gate 3 (resume) | yes | Runnable but redundant (C33). |
| Reconcile Gate | yes | Standard. |

## Upstream Assessment

#327, #326, #304 all unchanged and correct. **#266 `partial` — pass-2's omission properly
fixed**, present in all three surfaces with dispositions surviving regeneration. The only residue
from the re-run is `index.md` (C29). All four `references/*.md` carry an empty `**URL:**` field —
pre-existing generator behaviour across the corpus, not new damage.

## Main-session note on the recurring defect

**C27 is the second pipe defect I have introduced in this plan, in the opposite direction from the
first.** SC11's fix escaped a pipe into a regex where `\|` is *literal*, producing a check that
matched nothing; SC13's fix left a pipe *unescaped* in a table cell, producing a row that parses
as prose. Both were silent, both were introduced *while fixing a vacuity concern*, and neither was
caught by the audit — only by extraction. The lesson is not "be careful with pipes": it is that
**a criterion must be re-extracted and re-measured after every edit**, because the failure mode of
a broken criterion is a clean result.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C27 | high | Pipes escaped. Re-extracted: SC13's `discharged_by` is now `['0.3','0.4','0.5']` (was `['sort -u']`), and `doc_lint` went from 4 W to **0 W**. Confirmed independently before fixing. | `main-session` | `resolved` |
| C28 | high | `grep -c '^### Capability Gate:'` re-measured = **3**. Issue 0.0 now says ALL THREE and states the count is load-bearing; R9 reworded; SC14 raised to `-ge 3`; new **SC14b** asserts `cwd` separately, closing C34 in the same edit. | `main-session` | `resolved` |
| C29 | high | Confirmed independently: drift verdict `drift`, 1 bundle. Added a real descriptive bullet for `references/upstream-266.md` (and `reviews/pass-3.md`). Re-measured: **`verdict: clean`, drifting 0, 67 bundles**. New **Issue 5.1b** owns index currency with **SC17b** discharging it — pass-3 correctly noted no issue owned the fix. | `main-session` | `resolved` |
| C30 | medium-high | Approach now states the config must be written BEFORE `/yf-plan execute`, with the command, and explains the forced ordering (pour → `worktree ensure` → sweep). Gate 1's Instructions rewritten so the remediation is a RESTART, not a toggle. `Blocks` widened to `1.1, 3.1` so no code epic runs under an unresolved mode. | `main-session` | `resolved` |
| C31 | medium | Gate 2's Instructions reworded to name the work, not the blocked id. Re-ran the repo's own `gate_consistency.py`: **`verdict: PASS`, 0 findings** (was FAIL/1). | `main-session` | `resolved` |
| C32 | low-medium | SC15 converted to `manual:`, with the reason recorded inline — L3 already gates the landing on the same tier, and a clause would re-run it at L5 and L11 where the 300s cap could record a timeout as FAIL past the irreversible boundary. | `main-session` | `resolved` |
| C33 | low-medium | Gate 3 hoisted from `Blocks: 5.5` to `Blocks: 4.5`. **This hoist introduced a NEW C31-class violation** — the Instructions named 4.5, the issue it blocks, and `gate_consistency.py` flagged it. Caught by re-running the checker after the fix; reworded to describe the work instead. Both now PASS. | `main-session` | `resolved` |
| C34 | low | Closed with C28 — SC14 asserts `test_class`, new SC14b asserts `cwd`. The repo-wide scope is retained and acknowledged: Issue 0.0 is the scoped check, and SC14/SC14b are backstops. | `main-session` | `resolved` |
| C35 | low | `findings/exp-002`'s description corrected to state resume-first ordering rather than 'the two must land together'. Issue 2.1 now records that `manifest` is already in scope in `land_cmd` — the fact that makes '~40 lines' true. | `main-session` | `resolved` |
| C36 | low | Issue 1.1 now records the asymmetry explicitly: on a resume from L5 onward, L0 re-acquires while L4 (which releases) is skipped, so that run ends holding a lock nothing released; it self-heals via dead-PID reclaim. | `main-session` | `resolved` |

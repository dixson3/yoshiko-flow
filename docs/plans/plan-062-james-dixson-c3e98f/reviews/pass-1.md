---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 1 on plan-062. Verdict REVISE with 15 concerns, six high. Measured: every pytest invocation in the plan exits 2 on collection (uv --with pytest ignores PEP 723), making 7 of 15 criteria and both capability gates permanently unsatisfiable; Capability Gate 1 is simultaneously vacuous, unreachable (DAG cycle) and unrunnable; Issue 5.4 is impossible under worktree mode; SC2 and SC11 are vacuous today.'
---
# Red-Team Pass 1 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

## Strengths

Every load-bearing source claim independently confirmed: the stub at `:8306-8311`;
`_land_execute`'s single occurrence at `:9538`; `done` written at `:9550`/`:9558` and read
nowhere; the dead loop at `:9555-9557`; the L7 read-back at `:9059`; L7's `_step` at `:9080`
omitting `failed`; `body_sha256` over the archival file at `:8177`; `spec/landing.md:302`;
`REQ-LAND-011`'s Verification line; `agents/lander.md:88`; `test_land_apply.py:314/:384/:388`.
**Zero cited line numbers are wrong.**

`LAND_STEP_JOURNAL` is missing exactly the three named keys. `allow_list=[None]` really opens
the gate. SPEC-first ordering is correctly wired; Epic 3 is correctly parallel to Epics 1-2.
Every issue is named by at least one criterion.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **Every pytest invocation is broken (measured).** `uv run --with pytest python3 -m pytest … test_land_apply.py` exits **2**, `ModuleNotFoundError: click` — `--with pytest` builds an env containing only pytest and never reads the file's PEP 723 block. SC1/4/6/7/8/9/10 unsatisfiable; both gates permanently red; 1.1 and 5.4 blocked forever. | Use `uv run skills/yf-plan/scripts/test_land_apply.py -k <name> -q`, the form already in `CHANGE-VALIDATION.md:137`. Fix `context.md`'s inverted Python bullet. |
| C2 | high | **Capability Gate 1 is vacuous.** Condition says the test must FAIL; the Test greps `'1 failed\|1 passed'`, accepting **both**. R2's whole mitigation rests on it. `1 failed` also substring-matches `11 failed`. | Assert failure only: `…; test $? -eq 1`. |
| C3 | high | **Capability Gate 1 is unreachable — a DAG cycle.** It `Blocks: 1.1`, but its evidence is authored by 4.1, whose chain is `4.1 ← 2.2 ← 2.1 ← 1.2 ← 1.1`. The evidence producer is a descendant of the blocked issue. | Split test authoring into a new `1.0` depending on `0.6`; gate blocks `1.1` with `1.0` as predecessor. |
| C4 | high | **Issue 5.4 is impossible under worktree mode.** `_land_assert_primary_checkout` (`:6528`) hard-refuses any cwd but the primary, which stays on `main` — still carrying the stub. `--apply` would load `main`'s module and exit 2 on the very stub this plan removes. L2's merge cannot help; Python already loaded the module. | Set `execute.worktree: false`, or make the precondition explicit, or retarget 5.4. State the choice. |
| C5 | high | **SC2 is true right now with zero callers.** `grep -c '_land_execute('` returns 1, exit 0 — it matches the `def` itself. Green even if 1.1 were skipped. #263 verbatim. | Require ≥ 2, or an `ast` assertion that `land_cmd` calls it. |
| C6 | high | **SC11 is vacuous by regex dialect.** In ERE `\|` is a *literal* pipe, so the pattern matches nothing ever — measured with a planted `YF_LAND_TEST` still exiting 1. The identifier is also `allow_list`, not `tty_allow_list`. | Replace with a targeted check or drop SC11. |
| C7 | medium-high | **Issue 2.1's skip direction is backwards and unsafe.** A backward scan marks `l3_validate_merged` done once `L_MERGED_UNCOMMITTED` is reached — **skipping validation of the merged tree**; same for l8/l12 against `L_RECONCILED`, skipping the close chain. | Resolve **forward**: done only when the *next journaled* state is reached. Add halt-at-l3 and halt-at-l8 cases. |
| C8 | medium-high | **"Must land together" is prose; the DAG enforces the opposite.** `2.1 ← 1.2 ← 1.1` guarantees a window where the seam is live and the resume is still a no-op — the dangerous state first. | **Reverse: land Epic 2 before Epic 1.** The resume fix is inert without a caller, so no intermediate state has a live bug. |
| C9 | medium | **SC5 does not verify its criterion.** It only proves the placeholder `pass` was removed; 2.1 alone satisfies it while 2.2 is skipped and the bug survives. The 12-line window is unanchored. | Direct read-check: `ast` Load of `done`, or `grep -c 'in done'`. |
| C10 | medium | **The `test_class`/`cwd` mitigation is a restatement, not a control.** Confirmed dropped by `plan_extract.py --json` with `unparsed: []`, so `--strict` misses it too. An ALL-CAPS instruction with no exit code is the same failure mode the plan fixes one layer down. | Add a post-pour verification issue asserting both fields on both gates. |
| C11 | medium | **Gate 1 is a once-only probe expressed as re-runnable.** Its correct answer inverts the moment 1.1 lands; a §5.2c re-sweep would go red on a healthy tree. | Capture evidence once (exit code + `HEAD`); state it must not be re-run after 1.1. |
| C12 | medium | **SC12b cannot observe 3 of its 6 issues.** It greps only the three *new* ids; 0.1, 0.2 and 0.6 could all be skipped green — and 0.2 is what keeps Epic 3 from contradicting the SPEC. | Split into three checks. |
| C13 | low-medium | **Issue 1.2 has no criterion that can see it.** Nothing exercises a landing reaching `L_DONE` carrying a non-halting `inconclusive`; R5 is untested. | Add a test + SC asserting verdict `inconclusive`, exit 2. |
| C14 | low-medium | **SC3 names the wrong issue.** The stub string is at `:8308`, inside the block **1.1** replaces; 1.3 removes a different sentence. 1.3 could be skipped with SC3 green. | Retarget SC3 to 1.1; give 1.3 its own criterion. |
| C15 | low | **Issue 4.3's precedent citation is off** — `:314` is the `def`; the `ast` usage is at `:350-351`. | Cite `:350`. |

## Missing

- No coverage of the interaction between L7's new `failed`-halt (3.4) and resume: L7 halting after posting 1 of 3 comments creates a live resume path with partially-posted comments.
- No stated rollback for 5.4. R6 says what not to do, not what to do.
- Issue 5.2 is likely a no-op today — the `uv-yf-land-apply` row already exists and uses the working invocation.
- #304's promised record artifact is unnamed; `findings/exp-001` already contains it.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| Start Gate | yes | Fine. |
| Capability Gate 1 | **no** | Fails three ways — unreachable (C3), vacuous (C2), unrunnable (C1); unstable under re-evaluation (C11). Carries R2's entire mitigation and provides none of it. |
| Capability Gate 2 | condition yes, **command no** | Placement sound, no cycle. Test hits C1, so it can never go green and permanently blocks 5.4. |
| Reconcile Gate | yes | Standard. |

## Upstream Assessment

#327 include — correct, and the closure bar is right, though the "discriminating test" half is not currently achieved. #326 include — correct; Epic 3 is the tightest sequence in the plan. #304 partial — honest and correct to leave open. Issue 5.1's filings are appropriately excluded and SC12c rightly declines to self-certify an outward-facing write.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | All 7 test clauses and both gate `Test:` lines rewritten to `uv run skills/yf-plan/scripts/test_land_apply.py -k <name> -q`. Re-measured independently: broken form exit 2, correct form `1 passed, 42 deselected` exit 0. `context.md`'s inverted Python bullet corrected and annotated with where the error came from. | `main-session` | `resolved` |
| C2 | high | Gate 1 Test is now `...; test $? -eq 1` — failure only. The `1 failed\|1 passed` alternation and the inert `git stash list` preamble are both gone. | `main-session` | `resolved` |
| C3 | high | Cycle broken. New **Issue 2.0** authors the seam test with `depends-on: 0.6`; the gate blocks `2.1`; `2.1 depends-on 1.2, 2.0`. Verified in the extracted DAG: the evidence producer is now a predecessor, not a descendant. | `main-session` | `resolved` |
| C4 | high | Plan now states that execution MUST use `execute.worktree: false`, with the measured reason (`_land_assert_primary_checkout` refuses any cwd but the primary, which under worktree mode still carries the stub). Config resolution independently confirmed `execute.worktree=true` by default. New **Issue 5.4** makes the precondition observable rather than assumed. | `main-session` | `resolved` |
| C5 | high | SC2 is now `test "$(grep -c '_land_execute(' ...)" -ge 2`. Re-measured: exits **1** on the current tree (correctly unmet) where the old form exited 0. | `main-session` | `resolved` |
| C6 | high | SC11 replaced with `grep -rq 'YF_LAND' ... -> exit 1`. Proved the ERE defect directly: `\|` is a LITERAL pipe, so the old pattern matched nothing — a planted `YF_LAND_TEST` still exited 1. Sensitivity of the replacement verified: a planted marker now exits 0. **This was my own error** — escaping the pipe for the markdown table silently converted a parse failure into a vacuous check. | `main-session` | `resolved` |
| C7 | medium-high | Issue 1.1 now specifies **FORWARD** resolution explicitly, with the halt-at-l3 counter-example spelled out (backward resolution would skip validation of the merged tree). New **Issue 4.2** and **SC4b** test halt-at-l3 and halt-at-l8. New risk **R7** records the hazard. | `main-session` | `resolved` |
| C8 | medium-high | **Epic order reversed.** Epic 1 is now the resume fix and Epic 2 the seam wiring; `2.1 depends-on 1.2`. The resume fix is inert without a caller, so the dangerous window does not exist. R1 rewritten to say why ordering alone was not atomicity. | `main-session` | `resolved` |
| C9 | medium | SC5 replaced with `grep -q 'in done' -> exit 0`, a direct read-check. Re-measured: exits **1** today (correctly unmet). SC4 retained as the behavioural half. | `main-session` | `resolved` |
| C10 | medium | New **Issue 0.0** — the FIRST issue — reads the poured gate beads back and halts if `gate_type`/`test`/`test_class`/`cwd` are absent on either capability gate. The blockquote now says explicitly that it is documentation and 0.0 is the check. **SC14** discharges it. | `main-session` | `resolved` |
| C11 | medium | Gate 1's Instructions now mark it ONCE-ONLY: record the exit code and `git rev-parse HEAD` in the resolution note, and do not re-run after 2.1, because the correct answer inverts. | `main-session` | `resolved` |
| C12 | medium | SC12b split into **SC13** (three new ids, `-ge 3`), **SC13b** (`REQ-LAND-011` no longer names the staleness test, exit 1), and **SC13c** (amendment log names plan-062). All three re-measured as correctly unmet today. | `main-session` | `resolved` |
| C13 | low-medium | New **Issue 4.4** and **SC12** test that a landing reaching `L_DONE` carrying a non-halting `inconclusive` yields verdict `inconclusive`, exit 2 — not `pass`. | `main-session` | `resolved` |
| C14 | low-medium | SC3 retargeted to **2.1** (the issue that replaces the block containing the string). New **SC3b** greps for `Epics 3 and 4 implement` -> exit 1, discharged by 2.3. | `main-session` | `resolved` |
| C15 | low | Issue 4.3 now cites `:350-351`. | `main-session` | `resolved` |

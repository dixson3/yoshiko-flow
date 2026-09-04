---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 2 on plan-062. Verdict REVISE with 11 new concerns (C16-C26), two high and one medium-high. Re-measured all 15 pass-1 resolutions and found 12 mechanically real and none faked; the three residues are the unenforced execute.worktree precondition, Issue 0.0 being a detector with no remediation, and SC13c verifying the wrong file. Also found a subtle L0 lock-skipping hazard in the resume rule.'
---
# Red-Team Pass 2 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

## Strengths

**Pass-1's resolutions were re-measured, not read.** 12 of 15 are verifiably real; **no asserted
resolution was fake.** All 10 test clauses and both gate `Test:` lines run — every not-yet-authored
test exits **5** (no tests collected), never 2, so nothing is unrunnable. A full DFS over the
extracted DAG (30 issues, 33 edges) found **zero cycles**, zero dangling `depends-on`, zero
criteria naming a nonexistent issue, and **zero issues with no criterion**. Sandbox planted-string
checks confirmed SC2, SC5 and SC11 discriminate in both directions.

C11 is resolved **more strongly than claimed**: the once-only property is mechanical, not
prose-dependent — `bd list --type gate` returns only *open* gates, so a resolved gate leaves the
sweep permanently.

C7's FORWARD rule is correct on the merits against the real tables (`l3`→`L_VALIDATED`,
`l8`/`l12`→`L_CLOSED`), and `l19_redeploy` is journaled, so the tail is well-defined.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C16 | high | **C4 is asserted, not enforced.** No config file exists at any tier; `config-resolve` reports `execute.worktree = true (source: default)`. The plan says execution "MUST" use `false`, but nothing sets or checks it. The only observation point is Issue 5.4 / SC16 — **land time**, the exact failure mode C4 asked to eliminate. | Add a capability gate blocking `1.1`, `test_class: probe`, testing `config-resolve` for `execute.worktree == false`. Measured: exits 1 today, 0 once set. |
| C17 | high | **Issue 0.0 is a detector with no remediation.** #266 / `yf-n8fd` is an open P0 stating the Gates grammar cannot express `test_class`/`cwd`; those strings have zero occurrences in `plan_manager.py`, `formulas/`, or `plan_extract.py`'s grammar. If absent at pour → `manual` → INCONCLUSIVE → the §5.2c sweep never runs either capability gate, and R2's and R7's mitigation evaporates. 0.0's stated action is "halt", giving a deterministic stop at issue #1 with no recovery path. #266 is absent from the triage. | Change 0.0 from *assert* to **set-then-assert** (`bd update <gate> --metadata …`, then read back and halt only if the write did not take). Add #266 to Upstream Issues as `partial`. |
| C18 | medium-high | **SC13c verifies the wrong file.** `spec/landing.md` contains **zero** occurrences of "amendment" — the living amendment log is in the **repo-root `SPEC.md`**. Issue 0.6's deliverable is invisible to its own criterion. Separately SC13c is the only criterion naming Issue 0.2, and 0.6 alone satisfies it, so 0.2 can still be skipped green. | Use the repo's canonical check: `uv run scripts/check_amendment_log.py --plan plan-062-…` → exit 0 (measured: exit 2 today, exit 0 on plan-060). Give 0.2 its own criterion. |
| C19 | medium | **The uniform skip rule silently makes `l0_lock_acquire` skippable, dropping mutual exclusion on the resume path.** L0 takes the landing lock; it is released at **L4**, not at the end. Under "done when `LAND_STEP_JOURNAL[key]` is in `reached`", **every** resume skips L0 — so a resume that halted before L4 runs L1–L4 holding no lock, and L4 `unlink`s a lock it never acquired (`_landing_lock_release` is keyed on plan+host, not PID). A concurrent landing can reclaim the stale file and both run unlocked. Neither Gate 2 nor SC4/SC4b would notice. | State that **L0 is exempt from skipping** and always re-executes on resume — safe, since `_landing_lock_acquire` reclaims a same-host dead-PID lock. Assert it in Issue 4.1's test. |
| C20 | medium | **SC14 and SC16 are `manual:` where a checkable assertion exists**, and they are the two guarding the plan's biggest unenforced preconditions — concentrating the unfalsifiable surface exactly where the plan is weakest. SC14's justification only shows a *grep of plan.md* cannot see the fields; a `bd` query can, and 0.0 already runs it. | SC14 → a `bd list --type gate` query asserting both gates carry `test_class` and `cwd`. SC16 → the primary-checkout `grep -q 'executor is not implemented'` → exit 1. |
| C21 | low-medium | **SC10 cannot observe the word carrying its meaning.** It says the gate-closed test passes "**unmodified**"; the check only proves it passes, and it exits 0 already — staying green if the test body is weakened to accommodate the gate-open test. | Pin content, not verdict: anchor on the contract, e.g. `grep -c 'result.exit_code == 3'` unchanged. |
| C22 | low-medium | **Gate 1 reports RED at the execute-start sweep with no explanation** — before Issue 2.0 exists, pytest exits 5 so `test $? -eq 1` fails. Fail-closed and non-blocking, but the operator meets a red gate for a reason the gate text does not give. | One line in Instructions: expected FAIL until 2.0 authors the test. |
| C23 | low-medium | **`upstream-triage.md` records no dispositions** — all three issues carry empty `Disposition` and `Notes`, while plan.md's table carries full reasoning. The artifact whose job is to hold the triage reasoning holds none. | Fill all three; add the #266 row. |
| C24 | low | **SC13 counts lines, not distinct ids** — satisfied by two REQs if either is cited twice, which is the file's prevailing style. One id can be missing with SC13 green. | `grep -oE … \| sort -u \| wc -l` → `-eq 3`. |
| C25 | low | **SC15 hard-codes `~/.claude/skills/…`** — home- and harness-specific, in a bundle required to be readable from another repo. Every other clause is repo-relative. | Use `${SKILL_DIR}` or state the fallback. |
| C26 | low | **Issue 4.3's test passes against the current build**, since `land_cmd` already calls the gate at `:8296`. Correct for a regression guard, but it is presented under "tests that would have caught this", which it would not have. | Say it is a future regression guard. |

## Missing

- No risk row for the `execute.worktree` precondition (C16) — the most likely operational failure has no entry.
- No risk row for gates poured without `test_class` (C17); a reader skimming sees R2/R7 as mitigated when their enforcement may never fire.
- No risk row for the lock (C19).
- `findings/exp-002`'s frontmatter still asserts "The two must land together", superseded by the stronger resume-first ordering.
- Issue 2.1 omits where `manifest` comes from; "~40 lines" is true only because of a fact the issue does not state.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| Start Gate | yes | Fine; the natural fallback site for C16 if the gate route is declined. |
| Capability Gate 1 | **yes — cycle broken, verified in the DAG** | All three pass-1 defects genuinely fixed. Once-only is mechanical. Remaining issue cosmetic (C22). **Real exposure is C17.** |
| Capability Gate 2 | yes | Sound placement, runnable. Minor frontloading miss (earliest legal position is 4.2, not 5.5); defensible on intent. Same C17 exposure. |
| Reconcile Gate | yes | Standard. |

## Upstream Assessment

#327 `include` — the closure bar is now achieved rather than asserted. #326 `include` — Epic 3 remains the tightest sequence; Issue 3.5's `body_sha256` claim confirmed. #304 `partial` — honest, correctly open, and `findings/exp-001` is the record it promises. **Omission: #266 / `yf-n8fd`** is an open P0 this plan structurally depends on and does not triage.

## Main-session correction to C17

**C17's severity is right; its prediction is overstated, and the record should say so.** It claims
the plan's most likely first event is a deterministic halt at Issue 0.0. plan-061 is a direct
counterexample: its capability gates were poured **with** `gate_type`, `test`, `test_class` and
`cwd` present — verified by reading the beads back — because its `## Gates` admonition told the
executing session to set them. `plan_extract.py` drops the fields, but the executing agent reads
the raw markdown, so the admonition does work when followed.

What C17 gets right is the important half: **a detector whose remediation is "halt" is weaker
than a setter**, and relying on an agent following prose is exactly the command-vs-obligation
hazard (#273). The fix is adopted; the prediction is not.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C16 | high | New **capability gate** `execution is in-place, not in a worktree` blocks `1.1`, testing `config-resolve` for `execute.worktree == false`. Independently re-measured: exits **1** today. The precondition is now checked at execute start, not discovered at land time. New risk **R8**. | `main-session` | `resolved` |
| C17 | high | Issue 0.0 changed from *assert* to **SET-then-assert** (`bd update --metadata` for both gates, then read back and halt only if the write did not take). **#266 added to the Upstream Issues table as `partial`**, recording that this plan works around the grammar gap without closing it. New risk **R9**. See the main-session correction above: the fix is adopted, the prediction of a certain halt is not — plan-061 poured its gates WITH the metadata. | `main-session` | `resolved` |
| C18 | medium-high | Confirmed independently: `spec/landing.md` has **zero** occurrences of 'amendment'; the log is in repo-root `SPEC.md` (26). SC13c now uses the canonical `scripts/check_amendment_log.py --plan …` (re-measured exit **2** today). New **SC13d** gives Issue 0.2 its own criterion (`grep -q 'the text posted'`, exit 1 today). | `main-session` | `resolved` |
| C19 | medium | Issue 1.1 now states **`l0_lock_acquire` is EXEMPT from skipping and always re-executes**, with the lock-release-at-L4 reasoning spelled out. Issue 4.1's test asserts L0 DOES execute on resume. New risk **R10**. | `main-session` | `resolved` |
| C20 | medium | SC14 is now a `bd list --type gate` metadata query; SC16 is now `git -C "$(git rev-parse --show-toplevel)" grep -q 'executor is not implemented' → exit 1`, re-measured exit **0** today (correctly unmet). Only SC17 and SC18 remain manual, both legitimately — a journal observation by the operator and an outward-facing write. | `main-session` | `resolved` |
| C21 | low-medium | New **SC10b** pins the contract rather than the verdict. My first anchor (`exit_code == 3`) did not exist in the file — caught by re-measuring, corrected to `p.returncode == 3`, re-measured exit 0. A pinned string that matches nothing is the same vacuity one layer down. | `main-session` | `resolved` |
| C22 | low-medium | Gate 1's Instructions now open with EXPECTED TO REPORT FAIL AT THE §5.2c EXECUTE-START SWEEP, with the reason (pytest exits 5, no tests collected until 2.0). | `main-session` | `resolved` |
| C23 | low-medium | Dispositions and notes filled for all four rows in `upstream-triage.md`, including the new #266 row. | `main-session` | `resolved` |
| C24 | low | SC13 now counts DISTINCT ids: `grep -oE … | sort -u | wc -l` → `-eq 3`. Re-measured exit 1 today. | `main-session` | `resolved` |
| C25 | low | SC15 now resolves via `$(yf skill-dir yf-change-validation)` instead of a hard-coded `~/.claude/…` path. Verified runnable. | `main-session` | `resolved` |
| C26 | low | Issue 4.3 now states it is a FUTURE regression guard, not evidence about the present defect, since `land_cmd` already calls the gate at `:8296`. | `main-session` | `resolved` |

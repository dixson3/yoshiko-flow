---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: Red-team pass 2 (second independent, via Agent) — plan-054
---

# Red-team pass 2

## Verdict: REVISE

**18 of 22 pass-1 resolutions reproduced.** All 14 pass-2 concerns are now resolved; C33 is resolved as an **operator escalation**, not a plan change. Four (C2, C4, C10, C12) are recorded `resolved` but
are not true in the current `plan.md` — and **two of those four replaced an absent mechanism with
a deterministically-failing one**, which is the plan-050 pass-12 C119 pattern.

**Process defect, recorded first: `plan.md` was edited WHILE this pass ran.** The reviewer
observed Issue 0.8 change between two reads 30s apart, froze a snapshot
(sha1 `62ff696a…`, mtime 13:19:39) and reviewed that. A concurrent-edit review is a review of a
moving target. **Pass 3 must freeze before dispatch.**

## Strengths

All re-measured, not read:

- **C3 reproduced exactly, with the edge direction handled correctly** — 56 ancestors of 57
  issues, zero escapees, zero cycles, zero edges to unknown ids, `unparsed: []`.
- `gate_consistency.py` PASS (5 gates, 0 findings); `doc_lint.py` PASS; `audit` all checks passed.
- **C1's largest gap is genuinely closed** — all 26 distinct `assets/` paths are attributed to a
  named issue.
- C6, C7, C9, C11, C13, C15, C16, C17–C22 verified present and correct.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C23 | high | **The RED gate is UNSATISFIABLE as specified.** `redcheck.sh`'s `_derive_manifest` uses the anchored pattern `ctl-[0-9]{3}-[a-z-]+` and compares set-wise against `controls.txt`. Measured: it derives **7 of 8** — `ctl-opencode-read-layers` has no 3-digit number so it is invisible, and `ctl-225-column0-paragraph` truncates to **`ctl-225-column`** because `[a-z-]+` excludes the digit `0`. Sets differ → exit 1 → the gate blocks the entire fix core and **can never be resolved**. This is plan-053 pass-4 C44 recurring *inside the very sentence of 0.6 that cites C44* |
| C24 | high | **`redcheck.sh verify-manifest` — SC31's command — does not exist in the harness being adopted.** The harness has `record-red`, `assert-distinguishes`, `verify-red-all`, `verify-all`. SC31 resolves to an unknown verb → exit 2 → INCONCLUSIVE forever |
| C25 | high | **Ordering inversion introduced by the C1/C2 resolution.** `0.1` is the DAG root, but SC2 (discharged-by 0.1) runs `redcheck.sh`, authored in 0.6 against fixtures authored in 0.7. **0.1 cannot do its stated work.** R9 compounds it |
| C26 | high | **Eight criteria are measured GREEN on the unfixed tree** — SC1, SC5, SC8, SC9, SC10, SC22, SC23, SC24 all report `holds` today, before a single fix. `harness_cross_e2e` passes 7 tests in 4.97s right now. **A whole-suite command cannot distinguish "the new test was added and passes" from "no test was added."** This is pass-1 C5's class: the resolution patched the named instance and never swept the class. SC1 is worse — it claims every REQ landed first, but its instrument is the portability audit, which measures nothing of the kind |
| C27 | high | **SC19 is unsatisfiable, measured by running it** — `verify-reconcile` → `fail`, 15 of 23 rows. Three are structural: **#154 typed `deferred` while CLOSED upstream** (deferred demands OPEN — no execution can fix it); **#119 table says `include` but Issue 6.2 declares `partial`**; **#229 table says `deferred` but Issue 0.6 declares `include``**. Nothing cross-checks `resolves-upstream` against the table. C4's and C10's resolutions each landed in one place only |
| C28 | high | **6.5a merges to `main` with only 4 ancestors of 57**, so SC37 is unenforceable — the DAG permits merging before Epics 1, 2, 3, 5 exist. Related: `ancestors(6.7a) = {0.1, 6.3}`, so release notes may be written before anything is known, and 6.6 does not depend on 6.7a — SC36's artifact never enters the validated tree |
| C29 | med-high | **SC30's command does not measure SC30's claim.** `recheck-criteria` exits 1 if any criterion is FALSE, and at Epic-0 time nearly all are (SC29 needs a pushed tag). So SC30 is false-at-0.9 for reasons unrelated to script existence. Also: the per-criterion timeout is 300s and SC16 (FULL tier) was measured timing out at 25s; SC18 spawns the live regression from inside 0.9. **The self-reference IS handled** (`skipped-self-reference`) — no infinite recursion |
| C30 | med | 0.9 runs before `harness-smoke.sh` exists by the plan's own attribution (0.8 carves it out to 2.5). Also `harness-smoke.sh` violates 0.6's own `check-` prefix rule for `assets/checks/` |
| C31 | med | **C12's resolution is half-landed** — the gate is now `human`, but R8's mitigation still describes it as "auto but INCONCLUSIVE-tolerant", the exact posture C12 rejected |
| C32 | med | **D-1 says "superset", SC4b and R11 say "same". They cannot both hold.** A cwd-inclusive superset legitimately returns a *different* directory. Secondary: with `yf` off `PATH` (SC4b's premise) there is no `yf skill-dir` to compare against |
| C33 | med | **Scope: 57 issues, 40 criteria, 23 shell scripts to author, ending in an irreversible tag.** The natural seam is **Epic 3** — its six defects are in authoring-time scripts, invisible to a v0.5.0 consumer, and splitting removes 6 issues, 8 criteria and 5 of 8 controls from the critical path |
| C34 | med | **The plan-054 tracker row is decorative and the issue it claims does not exist.** It carries no `#NNN`, so `parse_upstream_rows` drops it (23 parsed vs 24 extracted) and nothing ever evaluates it. `gh issue list --state all` contains no plan-054 tracker; the note asserting it was "filed at intake" is false |
| C35 | low | `ctl-206-resolver-isolated` reuses a number that means something else — #206 is a closed extractor defect not in this plan's table, and plan-053 already ships `ctl-206-dropped-continuation` |
| C36 | low | The hardcoded-path count is off — measured **4** in `yf-markdown-lint` and **12** in `yf-markdown-format` (16, not 14). Also `yf-markdown-lint/README.md:23` names `~/.claude/skills/markdown-lint`, the **pre-`yf-` skill name** |

## Missing

1. A criterion distinguishing the *new* `harness_cross_e2e` tests from the 7 already passing (C26).
2. A cross-check between each issue's `resolves-upstream` and its table row (C27).
3. A satisfiable disposition for #154 (C27).
4. Predecessors on 6.5a sufficient to make SC37 true (C28).
5. `verify-manifest` in 0.6's adoption scope (C24).

## Gate Assessment

Start Gate and Release Authorization unchanged and correct. The C12 retype to `Type: human` is
real — `gate_consistency` passes and a human gate with `Blocks: 6.8` and no `Test:` blocks
perfectly well; only R8's prose is stale.

**The RED gate's reachability is correct** and its Blocks set now maps 1:1 onto the 8 named
controls — a genuine improvement over pass 1. But **pass 2's finding is narrower and worse than
pass 1's**: pass 1 said *"the condition is sound; only its instrument is absent."* The instrument
now exists and **fails deterministically**.

## Upstream Assessment

24 rows, 23 machine-visible. Judgement remains good; the failures are again **mechanical** — one
disposition contradicted by upstream state, two contradicted by their own declaring issue, one
row invisible to the parser asserting a nonexistent issue. `verify-reconcile` was **run**, not
reasoned about: `fail`, 15 of 23.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C23 | high | Reproduced independently before fixing — the anchored pattern derives 7 of 8. Renamed `ctl-225-column0-paragraph` → **`ctl-225-columnzero-paragraph`** and gave the two numberless controls plan-local **9xx** ids (`ctl-901-opencode-read-layers`, `ctl-902-resolver-isolated`). 0.6 now states both constraints explicitly. **My first fix re-injected the defect**: 0.6's prose quoted the bad names as a counter-example, and since the derivation greps `plan.md` it scraped them as real controls. Rewritten to state the rule without quoting a non-conforming literal. Re-measured: 8 controls, all conforming, derived set == named set. | `main-session` | `resolved` |
| C24 | high | Confirmed absent (verbs are `record-red`, `assert-distinguishes`, `verify-red-all`, `verify-all`). 0.6's scope now explicitly **adds `verify-manifest`** as a standalone entry point onto the existing `_derive_manifest` function, rather than SC31 assuming a verb the adopted harness never had. | `main-session` | `resolved` |
| C25 | high | Inverted. **0.6 is now the DAG root** and `0.1 depends-on 0.7`, so the baseline is recorded by an instrument that already exists. Re-measured: `0.6 deps=ROOT`, `0.1 deps={0.7}`. | `main-session` | `resolved` |
| C26 | high | All eight repinned to instruments that can fail. SC9/SC10 use `cargo test … -- <fn> --exact` against the specific new tests; SC5, SC8, SC22, SC23, SC24 point at named fixtures or dedicated checks. **SC1's instrument was simply wrong** — the portability audit does not measure REQ-before-implementation — and is replaced by `check-req-coverage.sh`. | `main-session` | `resolved` |
| C27 | high | All three fixed and the class closed. **#154 → `exclude`** (it is CLOSED upstream, so `deferred`'s OPEN requirement was unsatisfiable by construction; 6.4 files a successor). **6.2 now declares `#119 (include)`**, matching the table. **#229's table row retyped `include`** with `Resolved By: 0.6`, matching 0.6's declaration. Added a mechanical cross-check to my verification: table disposition vs every `resolves-upstream` declaration — **now NONE mismatched**. | `main-session` | `resolved` |
| C28 | high | 6.5a's predecessors widened from 4 to the full leaf set plus 5.9, 6.1, 6.2, 6.5 and 6.7a. Re-measured **anc(6.5a) = 52/57**, the only non-ancestors being 6.6/6.6a/6.7/6.8, which correctly follow the merge. 6.7a now depends on 6.3 **and 6.4**, and is a predecessor of 6.5a, so the release notes are inside the tree the FULL tier validates. | `main-session` | `resolved` |
| C29 | med-high | SC30 repointed from `recheck-criteria` to a dedicated **`check-criteria-scripts-exist.sh`** that diffs the `assets/` paths `plan.md` references against what `assets/` contains — the instrument 0.9's own text already described. The criterion now measures script existence rather than criterion truth. The 300s timeout and the SC18-spawns-a-live-regression hazards disappear with it. | `main-session` | `resolved` |
| C30 | med | `harness-smoke.sh` renamed **`check-harness-smoke.sh`**, obeying 0.6's own `check-` prefix rule for `assets/checks/`. `0.9 depends-on 2.5` had already been added before this pass reported. | `main-session` | `resolved` |
| C31 | med | R8's mitigation rewritten to match the retyped gate: human, operator-adjudicated, and an INCONCLUSIVE **blocks**. | `main-session` | `resolved` |
| C32 | med | **SC4b restated as CONTAINMENT** — *for every anchor `yf skill-dir` can resolve, the fallback resolves the same path* — which is what a cwd-inclusive superset can actually satisfy; equality was false by construction. The check invokes `yf` by absolute path while keeping it off `PATH` for the fallback arm, resolving the premise problem. R11 updated to match. | `main-session` | `resolved` |
| C33 | med | **Not resolved by the plan — escalated to the operator**, since it is a scope decision, not a defect. Recorded as risk **R13** naming Epic 3 as the seam and quantifying the saving (6 issues, 8 criteria, 5 of 8 controls off the critical path). Kept in scope by default because Epic 3 closes six upstream issues the release notes would otherwise describe as outstanding. | `operator` | `resolved` |
| C34 | med | Decorative row **removed**. Replaced with a note under `## Upstream Issues` recording that the coarse tracker is filed at INTAKE §4.5, carries no number yet, and deliberately has no row — a numberless row is dropped by `parse_upstream_rows` and would assert an issue that does not exist. Upstream rows 24 → 23, which is now the number both the extractor and `verify-reconcile` see. | `main-session` | `resolved` |
| C35 | low | Renamed **`ctl-902-resolver-isolated`**, out of the upstream-issue namespace. The 9xx plan-local convention is documented in 0.6 and required in `controls.txt`'s header. | `main-session` | `resolved` |
| C36 | low | 1.5 re-measured to **4 + 12 = 16 sites** (the drafting figure of 14 was low) and now also fixes `skills/yf-markdown-lint/README.md:23`, which names the pre-`yf-` skill `markdown-lint`. | `main-session` | `resolved` |

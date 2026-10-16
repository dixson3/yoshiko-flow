---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 3, execution] REVISE: all 23 prior resolutions re-verified, every checker clean, 12/14 SCs red-before-work; 2 concerns (0 high): SC11 forces citing unshipped plan-069; plan-072's open trigger-eval FAIL is inherited by plan-073's L3 and unnamed in Risks"
plan: plan-073-james-dixson-cc76de
pass: 3
mode: execution
---
# Plan Red-Team: plan-073-james-dixson-cc76de

## Verdict: REVISE
**Mode:** execution

**Tree measured.** HEAD is `ea93658`, not `2991519`. `ea93658` is the child of `2991519`; `git rev-parse HEAD HEAD~1` shows both. It only adds the plan-072 landing handoff and two plan-073 `index.md` lines for `reviews/pass-1.md` and `pass-2.md`. `git diff --quiet HEAD~1 HEAD -- <plan.md, reviews/>` exits 0, so plan v3 and passes 1–2 are byte-identical at both commits. No MERGE_HEAD, and the tree is clean. I discarded every measurement taken before your state change and re-ran it. One result changed: `okf.py reindex --check` was exit 1 before (missing pass-1/2 entries in `index.md`) and is exit 0 at `ea93658`, so that is not a finding.

## Strengths
- All seven bundle checkers are clean, except the amendment-log check, which is INCONCLUSIVE because no entry exists yet. That is expected before execution.
- Both capability gates are reachable and pass on today's tree:
  - REQ-ids-free gate exits 0.
  - The baseline FAST tier exits 0 in 184 s, with the tree clean afterwards.
- 12 of the 14 Success Criteria are red before execution, and each fails on its own missing artifact. Only SC12 and SC13 are green beforehand, and both are labelled as regression guards.
- The criteria are executable as written:
  - Every Python test file the SCs invoke runs standalone under `uv run` and exits 0.
  - `bd list --json` works, so SC14's red is a real absence of the bead, not a tooling failure.
- All 23 prior resolutions hold (12 from pass 1, 11 from pass 2).
- The premises behind the code are confirmed:
  - `PROJECT_GITIGNORE` (`beads_init.rs:49`) lacks the gate lock.
  - The hygiene block is at `:294`.
  - `command -v herdr` is at `yf-herdr/SKILL.md:37`.
  - `md2html.py` calls `check_deps()`.

## Concerns

| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low | measured: `grep -m1 '^\*\*Status:\*\*' docs/plans/plan-069*/plan.md` → exit 0, `**Status:** scoping`; `grep -c plan-069 CHANGELOG.md` → `0` | **SC11 requires the v0.6.0 CHANGELOG to cite plan-069, a plan still in scoping that shipped nothing.** SC11's id set is every *existing* `docs/plans/plan-0NN*` folder from 055 to 073. plan-069's folder exists (plan-070's does not), so a correct CHANGELOG without a plan-069 citation fails SC11. The only way to pass is to cite an unshipped plan in release notes, which misstates what 0.6.0 contains. | Restrict SC11's id set to plans whose `plan.md` status is `complete`, plus 072 and 073. Or state in Issue 5.1 that plan-069 is cited only as "not in this release". Either way, decide it in the plan rather than leaving it to the 5.1 author. |
| C2 | medium | inferred: `docs/plans/plan-072-*/assets/landing-handoff.md` records that landing attempt 4's FULL **`trigger-eval` row returned FAIL (exit 1), not INCONCLUSIVE**, on a pi cell, on a tree whose code is already in `origin/main`. I did not reproduce it: the FULL tier and trigger eval were off-limits. | **plan-073's release validation will probably inherit a FAIL, and R5 only covers INCONCLUSIVE.** plan-073's landing L3 runs the same FULL tier on a `main` that includes plan-072's code. The plan's "landed means green-validated `main`" claim then depends on an open problem the Risks table does not name. R9 counts "halted and recovered" as enough to start, but that is the state that currently fails L3. | Add a risk or precondition: plan-073 execution or landing waits until plan-072's `trigger-eval` FAIL is resolved (its re-land L3 passes FULL). Name the recovery for a FAIL, not only for a rate-limit INCONCLUSIVE. |

## Measurements

| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SD/scripts/doc_lint.py --path $P/plan.md --json` | 0 | PASS, 0 findings |
| plan_extract | `uv run $SD/scripts/plan_extract.py $P --json --strict` | 0 | 6 epics, 23 issues |
| gate_consistency | `uv run $SD/scripts/gate_consistency.py $P --json` | 0 | PASS, 4 gates |
| amendment log | `uv run scripts/check_amendment_log.py --plan plan-073-james-dixson-cc76de` | 2 | INCONCLUSIVE, no entry yet; not yet dischargeable |
| req coverage | `uv run scripts/checks/check-req-coverage.py $P` | 0 | all 16 non-Epic-0 issues covered (2 declared exempt) |
| okf reindex | `uv run $SD/scripts/okf.py reindex --check $P --json` | 0 | clean at `ea93658` (was 1 before the index commit) |
| audit | `uv run $SD/scripts/plan_manager.py audit $P --json-output` | 0 | pass, okf_native |
| repo index drift | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` | 0 | 77 bundles, no drift |
| gate: REQ ids free | the gate's Test line | 0 | all five ids free |
| gate: baseline FAST | `change_validation.py run --tier fast --json` (1500 s bound) | 0 | 184 s; tree clean afterwards |
| SC1 | as written | 2 | not yet dischargeable |
| SC2 | as written | 1 | not yet dischargeable (no `frontmatter::tests::optional_tool`) |
| SC3 | as written | 1 | not yet dischargeable (461 tests listed, none of the 4 new) |
| SC4 | as written | 1 | not yet dischargeable |
| SC5 | as written | 1 | not yet dischargeable |
| SC6 | as written | 1 | not yet dischargeable |
| SC7 | as written | 1 | not yet dischargeable (`ensure_gitignore_idempotent` exists; the gate-lock line does not) |
| SC8 | as written | 2 | not yet dischargeable (`No such command 'check-quotes'`) |
| SC9 | as written | 1 | not yet dischargeable |
| SC10 | as written | 1 | not yet dischargeable |
| SC11 | as written | 1 | not yet dischargeable (see C1) |
| SC12 | as written, 60 s bound | 124 | timed out; the same command finished with exit 0 in 184 s (gate row above). Labelled regression guard. |
| SC13 | as written | 0 | green before execution; labelled regression guard |
| SC14 | as written | 1 | not yet dischargeable; `bd list --status open --json` exits 0 with 77 issues, none "Cut v0.6.0" |
| SC runners | `uv run` each of `test_credibility_scorer.py`, `test_render.py`, `test_link_normalizer.py`, `test_check_frontmatter.py` | 0 each | 16 / 12 / 7 / 14 passed; all runnable as scripts |
| cargo build | `cargo test -p yf --no-run`, then `-- --list` | 0 | warmed so the 60 s SC bounds measure tests, not compilation |

**Prior resolutions re-verified.** Each was checked by grepping the evidence each resolution names against `plan.md` at `ea93658`:

- **Pass 1, C1–C12:** all `measured: holds`.
  - C1: my first grep falsely matched "union" at `plan.md:556`, which is the README Prerequisites union, not preflight. `plan.md:284` states "`yf preflight` is **unaffected**". Holds.
  - C2: no Issue 5.3 and no release-authorized gate remain.
  - C3: at least four `-- --list` presence checks.
  - C5: the manifest pytest form, plus the negative-control grep.
  - C9: `--resume` now appears only on `skill_trigger_eval.py`.
- **Pass 2, C1–C11:** all `measured: holds`.
  - C1: Issue 0.7 exists and 1.4 depends on `1.2, 1.3, 0.7`.
  - C3: the README edits are inside Issue 1.6.
  - C5: the L4-merge-sha diff precondition is present verbatim.
  - C7: SC2 is pinned to `frontmatter::tests::optional_tool`.
  - C8: SC3 greps `cmd::common::tests::…`.
  - C9: both SC12 and SC13 carry the regression-guard label.
  - C11: the `(optional)` literal is defined in Issue 0.2.
- **No phantoms.** The resolutions that point at the repo also hold in source: `SKILL.md:37`, `beads_init.rs:49/:294/:903`, and `.gitignore:46` for this repo's existing gate-lock line.

## Missing
- A condition between plan-073's landing and plan-072's unresolved L3 `trigger-eval` FAIL (C2).
- A minor point, not raised as a concern: Issue 1.2's new `skill_deps_all_present_ok` sits beside an existing `skill_deps_all_present_is_ok` (`checks.rs:1700`, empty declared set). The new test should exercise all-present with optional tools declared, or it duplicates the existing one.

## Gate Assessment
- **REQ-ids-free:** reachable, one-shot, exit 0.
- **Baseline FAST:** reachable and green now (exit 0, 184 s). Its runtime exceeds this procedure's 60 s bound, but that is a reviewer limit, not a plan defect.
- **Reconcile Gate:** satisfiable. The release bead (5.2) is outside the subtree, so no bead waits on landing.
- **No gate missing for C2.** It fits better as a risk plus an execution-start precondition than as a capability gate, because the evidence (a FULL run) is a landing-time artifact.

## Upstream Assessment
- **#410 and #411 (include):** each is wired to specific issues. Unchanged; fine.
- **#412 (partial):** the in/out split is explicit, and the path-aware matching covers `osf.io/preprints`. #412 stays open for the currency part. Fine.
- **#255 and #302 (exclude, context):** fine. The 5.2 follow-on bead fills the #255 release-tracker role.

**Residue:** none in the repo. Temp files were removed; the only side effect is cargo build output under the gitignored `target/`.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low | SC11's id set is now plans whose plan.md status is `complete`, plus 072 and 073 (this release's own). plan-069 (scoping, shipped nothing) is excluded, and Issue 5.1 states it is not cited. | `main-session` | `resolved` |
| C2 | medium | Added R10 and an execution-start precondition (Gates → baseline gate Instructions + Approach → Release). plan-073 execution does not start until plan-072 has landed with a green L3 FULL, which resolves the trigger-eval FAIL. R5 now names the FAIL recovery as well as INCONCLUSIVE. | `main-session` | `resolved` |

Missing-section note: Issue 1.2's third test was renamed `skill_deps_all_present_with_optional_ok` and exercises all-present with optional tools declared, so it no longer duplicates `skill_deps_all_present_is_ok`.

**Final status:** both concerns resolved in plan v4 (main session). Frozen.

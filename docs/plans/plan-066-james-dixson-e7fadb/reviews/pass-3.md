---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 3: REVISE, 11 concerns. Caught two PHANTOM RESOLUTIONS from pass 2 — edits asserted by four documents but never made."
id: pass-3
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
verdict: REVISE
---
# Red-team pass 3 — plan-066-james-dixson-e7fadb

## Verdict: REVISE

**13 of 15 pass-2 resolutions landed as claimed. Two did not** — and one is the exact `#306`
phantom-resolution class pass 2 was credited with avoiding. SC10 was asserted fixed by **four**
separate documents (R8, the EXP-004 amendment, the pass-2 Resolutions cell, and commit `4b8ec21`'s
message) while remaining **unchanged in the criteria table**.

## Strengths (executed, not asserted)

- **Every mechanical gate green.** `audit` → `pass` (pass-2 C2 cleared). `ready-check` → `verdict:
  REVISE`, `malformed_review: null` (C1 cleared). `plan_extract --strict` → exit 0, `unparsed: []`.
  `doc_lint` → `PASS, 0 errors`. `gate_consistency.py` → `PASS, 6 gates`. DAG independently
  re-derived: **no cycle, no self-edge, no dangling target.**
- **Zero false PASSes.** `recheck-criteria` → 25 FALSE, verdict FAIL. SC11's `manual:` clause now
  parses and is correctly excluded — pass-2 C3 genuinely fixed.
- **SC2 verified DISCRIMINATING by spike.** Empty page → build exits 0, 32 pages, zero warnings, but
  `index.html` has 0 `<hr>` / 1 `<h2>` → SC2 fails. A real page has 1 and 6.
- **EXP-003 and EXP-004 reproduce to the digit today**, and Issue 1.2's `uv run --with-requirements`
  remedy works with no `web/.venv`.
- **All six #317 corrections still hold** against the current tree.
- **Size is not a risk** — 49 issues / 9 epics is within precedent (plan-060 landed at 49). Checked,
  not assumed.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **SC10 is a PHANTOM RESOLUTION — the pass-2 C4 defect is live.** The row still reads "carry that version's encoding signature". Re-measured: 5 of 6 committed PNGs are colortype 6 + `sRGB` + IDAT 8192; `lifecycle.png` is colortype 2 / no `sRGB` / 4096 — the v0.8.2 fresh signature — while its sha256 differs. **1/6 satisfied with zero work, satisfiable by a stale PNG.** | Rewrite SC10 to the form three other documents already claim: sha256 equality against a fresh render, plus `d2 --version` equal to the pin. Pin the render flags too — sha256 equality is flag-sensitive. |
| C2 | high | **The new coverage's trigger scope names only the DOC side, so it would not have fired on the commit that created the defect.** Ground truth for `check_web_counts` is `skills/*/SKILL.md`; for `check_web_harness_paths` it is `harness_desc.rs`. **Measured:** `75a5796` added skill #20, broke the build and drifted 19→20 while touching **zero** `web/` files. Issue 2.6 recognises this for `check_skill_page_contract` and never generalises it. | Require source-side globs and assert them in SC25. **And invert SC20's nudge**: `ci.yml` runs unfiltered on every PR and push to `main`, so a `paths:`-filtered job gives strictly LESS coverage. |
| C3 | medium-high | **Issue 0.4b's `verbs-match` is unsatisfiable as specified, and nothing runs it.** The table carries 23 verbs; `verbs-match` is itself a subcommand → 24, so the equality can never hold. And no criterion's `Discharged-by` names 0.4 or 0.4b — pass-2 C9 landed the subcommand but not the criterion. | State the carve-out (`SUBCOMMANDS - {'verbs-match'}`) and add a criterion that RUNS it. |
| C4 | medium-high | **SC25 and Issue 2.8 say "the four `check_web_*` rows" — only three carry that prefix.** `check_skill_page_contract.py` does not, so a literal implementation finds three and fails, or silently drops the one whose trigger scope C2 depends on. | Enumerate the four script names explicitly. |
| C5 | medium | **Issue 0.5's deliverable has no home in the DAG.** Its text says the rows land "at land only", but 0.5 is an Epic-0 bead a coordinator dispatches immediately, and SC3 checks the SPEC entry, not the rows. Closing it is either a no-op or reintroduces the unsatisfiable rows pass-2 removed. | Move the row-addition to an explicit land-time issue and state 0.5's closure contract. |
| C6 | medium | **SC13/SC14 punish the natural way to do the work.** They assert a grep exits 1, while 6.1/6.2 direct the author to document that those forms are wrong — the idiomatic corrective sentence writes the forbidden string and flips the criterion FALSE. | Scope the greps to ignore negated/quoted mentions, and say so in 6.1/6.2. |
| C7 | medium | **R3's mitigation is still a phantom.** It claims the no-pipe form is mandated "in every criterion"; measured, **0 of 26** criteria mention a pipe, `--fatal warnings`, or pelican. Pass-2 C10 claimed a restatement; the 0.4/1.2 half landed, the R3 cell did not change. | Restate R3 to describe what actually enforces it. |
| C8 | low-medium | **The deliberately-uncovered list disagrees with the extractor** — documented 9, extractor reports 11, adding 0.4 and 0.4b. The note "0.4 is covered via 0.4b" is false. No genuine deliverable is hiding, but it is pass-2 C6's drift class one level down. | Derive the list mechanically, or cover 0.4/0.4b with the `verbs-match` criterion. |
| C9 | low-medium | **Issue 2.1's text declares a dependency that cannot exist.** "This depends on Issue 4.3…" — adding that edge closes the cycle `4.3 → 4.2 → 4.1 → 2.5 → 2.1`. An agent reading it as a DAG instruction wedges the graph. | Reword to "must tolerate the pre-4.3 shape" and state that no edge may be added, naming the cycle. |
| C10 | low-medium | **Issue 8.1 depends on only one of Epic 3's six issues.** The sweep can run before 3.1-3.4 and 3.6. SC12 covers them independently, so this is consistency, not a hole. | Add the full Epic-3 tail to 8.1. |
| C11 | low | **All four `findings/*.md` fail their own document schema** — missing `Approach Tested`, `Result`, `Implications for Plan`, `Recommendations`, the epistemic marker, and `description:` frontmatter. Advisory, but "a cold reader must understand the plan from the folder alone" is this plan's own thesis. | Add the sections, markers, and a `description:` to each bundle `.md`. |

## Missing

- No criterion executed `verbs-match`, the guard over 22 criteria (C3).
- No trigger glob on the source of truth for three of four checkers (C2) — a hole in exactly the commit shape that produced the outage.
- No landing home for Issue 0.5's rows (C5).
- SC10 had no falsifiable assertion (C1).

## Gate Assessment

`gate_consistency.py` → **PASS, 6 gates, 0 findings**; DAG acyclic, no self-edges or dangling
targets. All four capability gates reachable and at their earliest legal position. Pass-2 C9's
undeclared precondition is closed (1.2 depends on 0.4); `--min-checkers 4` matches the four
checkers; pass-1 C6's removal of the vacuous 5.5 remains correct. The one live gate-adjacent defect
is C5 — 0.5 is coordinator-dispatched but instructed to execute post-merge, with no step owning the
transition.

## Upstream Assessment

Dispositions unchanged and sound; D3's four folds each map to a named issue. The five `include` rows
carry `_TBD_` — correct at `drafting`, discharged by 8.5 before `reconciling`. **One residue from
pass 2 remains open rather than answered:** #317 carries two `resolves-upstream` declarations with
different dispositions, `(partial)` on 1.2 and `(include)` on 8.5. The unit suite passes (13) but
that is not a check against this plan. Worth one pour-time verification; not blocking.

## Resolutions

All 11 resolved by the main session. **Every edit in this cycle was applied through an asserting
helper** (`assert old in t` plus a uniqueness check) — the absence of that assertion is precisely
what produced C1 and C7, and the helper caught three further anchor misses during remediation.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Fixed, and the root cause found.** SC10 now asserts sha256 equality against a fresh render under the pin `d2 v0.8.2` with pinned flags `--theme 0 --layout elk`. **Why it was phantom:** an earlier clause-normalisation pass moved SC10's parenthetical into the Criterion column, so the pass-2 anchor no longer matched — and that replace carried **no assertion**, so it silently did nothing while R8 (a different anchor) succeeded. Four documents then disagreed with one. A systematic re-verification of all 22 pass-2 claims found exactly these two phantoms. | `main-session` | `resolved` |
| C2 | high | **Fixed.** Issue 2.6 now requires every checker's §3 globs to name its SOURCE OF TRUTH, with `75a5796` quoted as the measured case; SC25 asserts both doc-side and source-side globs. SC20 and Issue 2.8 inverted — the job goes in `ci.yml` unfiltered, and adding a `paths:` filter is explicitly forbidden as narrowing coverage. | `main-session` | `resolved` |
| C3 | medium-high | **Fixed.** Issue 0.4b now specifies `set(SUBCOMMANDS) - {'verbs-match'}` with the reason stated, and new **SC26** discharges 0.4 + 0.4b by RUNNING it. | `main-session` | `resolved` |
| C4 | medium-high | **Fixed.** SC25 and Issue 2.8 now enumerate all four script names explicitly, with a note that `check_skill_page_contract.py` lacks the `check_web_*` prefix and a glob would silently drop it. | `main-session` | `resolved` |
| C5 | medium | **Fixed.** New Issue 8.4b lands the rows post-merge on `main`, depending on 0.5 and 8.3; Issue 0.5 restated as DRAFTING them. Closing 0.5 alone is now explicitly a no-op. | `main-session` | `resolved` |
| C6 | medium | **Fixed.** SC13/SC14 now require the negative leg to ignore negated or quoted mentions, and Issue 6.1 states the author MAY name the wrong form in order to correct it — what must not appear is an affirmative claim. The two remedies no longer conflict. | `main-session` | `resolved` |
| C7 | medium | **Fixed.** R3 amended to name what actually enforces the rule (Issue 0.4 mandate (b) and the gate Instructions), and to record that the old "in every criterion" claim was false. | `main-session` | `resolved` |
| C8 | low-medium | **Fixed.** The list is now stated as mechanically derived and reconciled against the extractor: exactly ten (`0.2, 0.3, 2.1-2.4, 4.1, 8.4, 8.4b, 8.5`). 0.4/0.4b removed and covered by SC26; the false "covered via 0.4b" note replaced with what actually happened. | `main-session` | `resolved` |
| C9 | low-medium | **Fixed.** Issue 2.1 now states that this is NOT a `depends-on` edge and none may be added, naming the cycle `4.3 → 4.2 → 4.1 → 2.5 → 2.1` it would close. | `main-session` | `resolved` |
| C10 | low-medium | **Fixed.** Issue 8.1 depends on the full Epic-3 tail (3.1, 3.2, 3.3, 3.4, 3.5, 3.6) alongside 4.9, 5.5, 6.5, 7.1-7.3 and 2.8. | `main-session` | `resolved` |
| C11 | low | **Fixed, after one self-inflicted regression.** All four findings gained `Approach Tested` / `Result` / `Implications for Plan` / `Recommendations`, epistemic markers, and `description:` frontmatter; reviews gained `description:`. The first attempt used a single-quoted YAML scalar containing an apostrophe (`'…#317's…'`), which **broke frontmatter parsing on all four files and flipped `audit` to fail**. Caught by re-running the audit rather than trusting the edit; re-done with double quotes and verified by parsing each file with `yaml.safe_load`. Audit back to `pass`; schema recommendations 8 → 4. | `main-session` | `resolved` |

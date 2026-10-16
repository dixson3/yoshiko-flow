---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 2, reading] REVISE: all 12 pass-1 resolutions hold; moving herdr to optional-tool breaks un-amended REQ-HERDR-040 (and 3 sibling SPEC literals); README marker lands after the checker requiring it; fail-closed clause has no test; tagged tree != L3-validated tree; post-landing release untracked; 11 concerns, 1 high"
plan: plan-073-james-dixson-cc76de
pass: 2
mode: reading
---
# Plan Red-Team: plan-073-james-dixson-cc76de

## Verdict: REVISE
**Mode:** reading

## Strengths
- All 12 pass-1 resolutions hold against plan v2 (table below). None is a phantom.
- The post-landing tag removes the deadlock with the close chain. No Success Criterion or Discharged-by cell depends on the tag, and L11 `recheck-criteria` can discharge every SC on the merged tree before L12.
- Every SC except SC12 and SC13 is red before execution, and each can turn green (measurements below).
- The plan-folder checkers are clean: doc_lint, plan_extract `--strict` and gate_consistency all exit 0. The REQ-ids-free gate re-runs at exit 0.
- Measured, the four existing entrypoints fail closed without their tool:
  - `md2html.py` and `md2pdf.py` call `check_deps()` (`md2pdf.py:296`), and both have tests for it.
  - `render.py` `render`, `render-dir` and `preflight` return 1 when d2 is missing.
  - yf-herdr's prose preflight checks `command -v herdr` at `SKILL.md:37`.

## Concerns

| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: `sed -n 217,224p skills/yf-herdr/SPEC.md` → REQ-HERDR-040: "The `SKILL.md` frontmatter **shall** declare it under `depends-on-tool`" | **Issue 1.4 breaks a normative REQ that Epic 0 does not amend.** Moving herdr to `optional-tool` violates REQ-HERDR-040, which breaks the SPEC-first rule. Issue 4.1 runs `yf-drift-check`, and "reported drift FAILs this issue", so the conflict would stop execution partway through. pass-1 did not flag this; the C6 widening adds the same problem for three more skills (C2). | Add an Epic 0 issue that amends REQ-HERDR-040 to say "`optional-tool`", with a `plan-073` amendment-log bullet. Make 1.4 depend on it. |
| C2 | medium | measured: `grep -rn depends-on-tool skills/{yf-diagram-authoring,yf-markdown-html,yf-markdown-pdf}/SPEC.md` → `SPEC.md:93`, `:100` and `:130` each quote the `depends-on-tool: [...]` literal as part of the skill's dependency posture | These per-skill SPEC literals will be stale after 1.4, and nothing in Epic 0 or 4.1 lists them. The READMEs' "Mirrors SKILL.md frontmatter `depends-on-tool: […]`" lines (`README.md:89` ×3, `yf-herdr/README.md:33`) also go stale. | List the four per-skill SPEC edits in the new Epic 0 issue, and list the four README "Mirrors" lines in 4.1. |
| C3 | medium | measured: `grep -n skill-readme-contract CHANGE-VALIDATION.md` → `:213` (FAST tier). The four READMEs' Prerequisites carry no "optional" marker. Plan edge: 4.1 depends-on 1.6 | **The README dependency runs the wrong way.** 1.6 makes `check_skill_readme_contract.py` require optional tools to be marked optional, but the four READMEs only get the marker in 4.1, which comes after 1.6. So 1.6 cannot discharge SC6 (`check_skill_readme_contract.py` → exit 0) when it closes, and the FAST tier stays red between 1.6 and 4.1. | Move the four skills' README Prerequisites edits into 1.6, or 1.4. Then 4.1 keeps the root README, `install.md` and yf-skill-authoring. |
| C4 | medium | inferred: `render.py` `check-dir`, `embed`, `lift` and `inline` never need d2. No test in `test_render.py` covers missing d2 (it skips with `HAS_D2`). Issue 1.4 only says "Confirm" | **The fail-closed clause of REQ-YF-DOCTOR-008 has no check.** The clause holds today for yf-diagram-authoring's tool-dependent subcommands, and yf-herdr holds it through `SKILL.md:37`. But Issue 1.4 produces no artifact for it and no SC checks it. The coverage gate passes on the parser tests tagged 008, which hides the gap. The plan also cites only HERDR_ENV=1 for yf-herdr. That is a trigger precondition (REQ-HERDR-041); the fail-closed check is `command -v herdr`. | Change the clause to "every operation that invokes the tool shall exit non-zero when it is absent". Add a `render.py render` missing-d2 test (empty `PATH`), tagged REQ-YF-DOCTOR-008, and name it in an SC. Cite `SKILL.md:37` for yf-herdr. |
| C5 | medium | measured: `sed -n 52,80p ${SKILL_DIR}/spec/landing.md` → L16 commits the plan-folder writes and does PUSH #2 after L3. The post-landing `assets/release-authorization.md` is another commit on `main` (bookkeeping-commit rule) | **The tagged tree is not the L3-validated tree.** The Findings claim "That tree *is* `main`'s tip at landing, so it is the tree the tag will point at" is false. At least L16 and the authorization commit come after L3, and any other plan landing in between adds more. The preconditions check tag == `origin/main` and the workflow diff, but not that everything since the validated merge is plan-folder-only. | Record the L4 merge sha. Add the precondition `git diff --quiet <L4-sha> HEAD -- . ':(exclude)docs/plans/'`. Correct the Findings sentence. |
| C6 | medium | inferred: the plan's last bead closes at landing, #410 and #411 close at L7, and #255 was the release tracker for v0.5.0 | **Nothing tracks the post-landing obligation.** After `complete`, no bead, open issue or gate records that `v0.6.0` still has to be tagged and verified. If the operator does not do it, nothing in the repo shows that. | File a coarse "Cut v0.6.0" upstream issue in the Upstream table (the #255 precedent). Keep it open until `assets/release-verification.md` lands, or create a follow-on bead that L17 mirrors. |
| C7 | low-medium | measured: the `cargo test -p yf -- --list` listing includes `strict_ignores_optional_tools`-shaped names; `grep 'optional_tool.*: test'` also matches `doctor_green_without_optional_tools` | **SC2's presence check does not pin 1.1's parser tests.** The pattern also matches the tests from 1.3 and 1.5, so SC2's cargo half can turn green with no parser test. | Use `grep -q 'frontmatter::tests::optional_tool'`. |
| C8 | low-medium | measured: `cargo test -p yf -- --list` → integration tests in `yf/tests/` list without a module path (`flow_install_e2e_legacy_transition: test`) | SC3 greps `::strict_ignores_optional_tools: test`, but Issue 1.3 does not say where that test goes. If it lands in `yf/tests/`, SC3 stays red permanently. | Put the test in a unit-test module in Issue 1.3 (e.g. `cmd::common::tests`), or drop `::` from that grep. |
| C9 | low | measured: `uv run scripts/check_frontmatter.py` → exit 0 and the FAST tier gate already exists; SC12 and SC13 are green before any issue runs | SC12 and SC13 are regression guards and cannot distinguish this plan's work (#384). This is acceptable because SC2's overlap test and the other SCs cover the actual work. | Mark both SCs as regression guards in their Criterion text so a reader does not count them as delivery evidence. |
| C10 | low | measured: `render.py` docstring: "run via `uv run`"; `skills/yf-diagram-authoring/SPEC.md:89` says the same | The Approach table gives yf-diagram-authoring `depends-on-tool: []`, but the skill needs uv. The other three skills declare `[uv]`. | Use `[uv]`, and update SC4/README to match. |
| C11 | low | inferred: the yf-herdr README Prerequisites is prose, not a table | REQ-YF-DOC-007 (amended) says "each optional tool marked optional" but does not define what the marker looks like. The checker in 1.6 has to guess at a format, and the prose README in yf-herdr makes that harder. | Define the marker in REQ-YF-DOC-007, for example a literal `(optional)` token on the line naming the tool. |

## Measurements

| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SD/scripts/doc_lint.py --path $P/plan.md --json` | 0 | clean |
| plan_extract | `… plan_extract.py $P --json --strict` | 0 | clean |
| gate_consistency | `… gate_consistency.py $P --json` | 0 | clean |
| REQ-ids-free gate | the gate's Test line | 0 | all five ids still free |
| cargo list | `cargo test -p yf -- --list` | 0 | 461 tests; no `optional_tool`, `strict_ignores`, `doctor_green` or `verify_reports_unignored` test exists, so SC2, SC3, SC5 and SC7 are red |
| SC8 precondition | `link_normalizer.py check-quotes --help` | 2 | red, as expected |
| SC9 parts | `grep -c` on each of the 9 terms | 1 each | all red |
| SC13 | `uv run scripts/check_frontmatter.py` | 0 | green before execution (C9) |
| frontmatter tests | `uv run scripts/test_check_frontmatter.py` | 0 | 14/14; runs as a script, so SC2's form is valid |
| REQ-HERDR-040 | `sed -n 217,224p skills/yf-herdr/SPEC.md` | 0 | "shall declare it under `depends-on-tool`" (C1) |

**Pass-1 resolutions re-verified:**
- **C1** holds: REQ-008 says preflight is unaffected, and no SC asserts preflight behaviour.
- **C2** holds: no tag bead (new gaps are C5 and C6).
- **C3** holds, with the tightening in C7 and C8.
- **C4** holds: `--help` → 2 now.
- **C5** holds: the manifest form is `CHANGE-VALIDATION.md:214`.
- **C6** holds, but exposed C1 and C2.
- **C7** holds.
- **C8** holds.
- **C9** holds: R5 now names `skill_trigger_eval.py --resume`.
- **C10** holds, with the C5 caveat.
- **C11** holds.
- **C12** holds: the `gen-install-parity.py` golden emits no `tools` field, so moving tools there breaks nothing.

## Missing
- Epic 0 amendments for REQ-HERDR-040 and the three sibling-SPEC dependency-posture literals.
- A test for the missing-d2 path in `render.py`.
- An upstream tracker for the post-landing release act.
- A tree-equality precondition between the L3-validated merge and the tagged sha.

## Gate Assessment
- **REQ-ids-free:** reachable, one-shot, and still exits 0.
- **Baseline FAST:** reachable, correct class, now also blocks Epic 0. It duplicates SC12, which is fine as long as SC12 is labelled a regression guard.
- **Reconcile Gate:** now satisfiable, because no bead waits for landing.
- **No gate is missing** for the C1 conflict. It belongs in Epic 0 as an ordinary dependency, not as a gate.

## Upstream Assessment
- **#410 and #411 (include)** are wired to specific issues and will close at L7. That is reasonable.
- **#412 (partial)** keeps its in/out split, and the path-aware matching covers `osf.io/preprints`.
- **#255 and #302 (exclude, context)** are fine. Since #255 is the precedent being followed, a v0.6.0 equivalent should be filed (C6). Without it, the release stays untracked after the plan reaches `complete`.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | New Issue 0.7 amends REQ-HERDR-040 (herdr under optional-tool, uv under depends-on-tool), with a plan-073 bullet in yf-herdr's SPEC log and the root entry. Issue 1.4 depends on 0.7. | `main-session` | `resolved` |
| C2 | medium | Issue 0.7 also updates the three sibling SPEC posture literals. Issue 1.6 updates the four README 'Mirrors SKILL.md frontmatter' lines. | `main-session` | `resolved` |
| C3 | medium | The four skills' README Prerequisites edits moved into Issue 1.6, the same change-set as the checker, so the FAST skill-readme-contract row stays green at every commit. 4.1 keeps the root README, install.md and yf-skill-authoring. | `main-session` | `resolved` |
| C4 | medium | REQ-YF-DOCTOR-008 clause reworded: every operation that invokes the tool exits non-zero with a message naming it when it is absent. New test test_render_fails_closed_without_d2 (no HAS_D2 skip), named in SC4. yf-herdr is cited at SKILL.md:37 (command -v herdr). | `main-session` | `resolved` |
| C5 | medium | Findings sentence corrected. The authorization record carries the L4 merge sha, and a third precondition `git diff --quiet <L4-sha> HEAD -- . ':(exclude)docs/plans/'` requires everything after the validated merge to be plan-folder bookkeeping. If it fails, re-run FULL on HEAD. | `main-session` | `resolved` |
| C6 | medium | New Issue 5.2 creates a standalone follow-on bead 'Cut v0.6.0: tag + verify' (discovered-from the epic, not parented) carrying the post-landing procedure. L17 mirrors it upstream as the release tracker. SC14 checks it. | `main-session` | `resolved` |
| C7 | low-medium | SC2 presence check pinned to 'frontmatter::tests::optional_tool', and its filter uses the same path. | `main-session` | `resolved` |
| C8 | low-medium | Issue 1.3 puts strict_ignores_optional_tools in yf/src/cmd/common.rs's test module. SC3 additionally greps 'cmd::common::tests::strict_ignores_optional_tools: test'. | `main-session` | `resolved` |
| C9 | low | SC12 and SC13 are labelled 'Regression guard, not delivery evidence' in their criterion text. | `main-session` | `resolved` |
| C10 | low | yf-diagram-authoring declares depends-on-tool: [uv] (Approach table, 0.7, 1.6 README table, SC4 grep). | `main-session` | `resolved` |
| C11 | low | REQ-YF-DOC-007 amendment (Issue 0.2) defines the marker: the literal token `(optional)` on the line naming the tool, in a table cell or in prose. | `main-session` | `resolved` |

**Final status:** all 11 concerns resolved in plan v3 (main session). Frozen.

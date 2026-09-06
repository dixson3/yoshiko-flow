---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
verdict: REVISE
---
# Red-team pass 2 — plan-066-james-dixson-e7fadb

## Verdict: REVISE

15 concerns (5 high, 3 medium-high, 4 medium, 3 low-medium). No phantom resolutions — but the
pass-1 remediation introduced five new defects, two of them hard mechanical blockers on approval
that existed at the moment of review.

## Strengths (verified, not asserted)

- **All 16 pass-1 resolutions land as claimed.** Every cell checked against the document; none
  describes an edit not made (#306's phantom-resolution class). Confirmed mechanically: uncovered
  issues 25 → 11 and the 11 are exactly the documented set; `doc_lint --type plan` → `PASS, 0
  errors, 0 warnings`; `gate_consistency.py` → `PASS, 6 gates, 0 findings`; **no cycle**.
- **#317's corrections re-measured and still hold** — 20 skills / 19 pages, `architecture.d2` at 18
  with `beads group (8)` listing the *workflows* skills, 5 formulas, no `PAGE_PATHS`,
  `grep -c 'web/' CHANGE-VALIDATION.md` → **0**, no CV tier in any CI workflow.
- **Nothing passes vacuously.** 22 of 24 criteria return 127 → `inconclusive` → `harness_incomplete`
  → `recheck-criteria` exits 1. SC3 executes to exit 2 (correctly FALSE). **Zero false PASSES.**

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **`pass-1.md` carries no parseable verdict line** — bold body text, not a heading. `ready-check` → `ready: false`, `verdict: null`, `malformed_review`. The #116 defect verbatim. **Approval blocked today.** | Rewrite as a `## Verdict: REVISE` heading; emit pass-2 the same way. Read the `verdict` field back, not the exit code. |
| C2 | high | **The portability audit FAILS** — `context.md` §Project environment, §Operator identity and §Runtime assumptions all hold template prose. Intake halts. The Tool inventory omits **`d2` and `pelican`**, the two tools SC1/SC10 and D7 depend on, and D7's "one pinned d2 version" has no recorded value. | Fill the three sections. Record `d2` v0.8.2 and pelican 4.11.0; state the D7 pin as a literal. |
| C3 | high | **SC11 is a malformed clause that would permanently block §6.4 — introduced by the pass-1 C1 rewrite.** `_RECHECK_MANUAL` is `\Amanual:\s*\S`; the cell began `**manual**:`, which does not match, so it fell through to the clause regex, whose greedy backtick capture yields a command executing `carries` and `asserted`. Measured under `bash -c`: **exit 127**. `doc_lint` scores the row **PASS** — both instruments share the regex, so the linter cannot catch it. | Split into a literal lowercase `manual: <why>` row and a separate clause row carrying the full `uv run scripts/checks/` prefix. |
| C4 | high | **SC10's PNG signature is not discriminating — measured.** All six fresh renders share one signature (`colortype=2`, no `sRGB`, IDAT 4096) and no chunk carries a version string, so "carries that version's signature" is unfalsifiable. Committed `lifecycle.png` **already** matches it while differing in sha256 — **SC10 was 1/6 satisfied with zero work, and satisfiable by a stale PNG.** | Two renders of one source under one version are **byte-identical** (measured). Assert sha256 equality against a fresh render plus `d2 --version` equal to the pin. This also corrects EXP-004: byte verification fails *across* versions, not *within* one. |
| C5 | high | **Missing dependency: 5.3 does not depend on 4.5.** 4.5 edits `images/architecture.d2:36`; 5.3 (the one-commit re-render) depends on 5.1, 5.2, 4.4 but not 4.5, so the render can precede the backend fix. `architecture.png` would ship the retired backends while SC8 passes on the `.d2` text and SC10 on the encoding. The plan recognised this for 4.4; 4.5 is the inconsistent omission. | Add `4.5` to 5.3's `depends-on`; audit for any other issue editing a `.d2`. |
| C6 | medium-high | **Issue 2.6 — the plan's PRIMARY deliverable — is classified "deliberately uncovered".** D6 says Class B ships a mechanical gate; 2.6 *is* that gate. No criterion asserts the four `check_web_*` §1 rows or the §3 globs landed. **The pass-1 C3 and C11 resolutions interacted to hide the deliverable.** | Add a criterion asserting the rows and globs are present; remove 2.6 from the uncovered list. |
| C7 | medium-high | **C13's remediation is not feasible at the line it names.** `architecture.md:65` reads `**utility (7)** — beads-free helpers: skill authoring, drift checking, …` — **English descriptions, not skill ids**. Only `workflows` and `beads` carry backticked names. Nothing there can be compared to frontmatter without a hand-maintained translation table. | Rewrite the `utility`/`markdown` bullets to enumerate backticked ids, or scope the parsing to the two bullets that carry ids and declare the rest `not_checked`. |
| C8 | medium-high | **Issue 0.5's rows are the structurally-unsatisfiable class this repo already removed once.** `CHANGE-VALIDATION.md`'s own §1 banner: a row reading `docs/plans/<in-flight-plan>/` is "incapable of passing by construction", and the `gate-plan049-*` rows work only because those plans LANDED. Both proposed commands are exactly that. No issue writes a tagged test for the new `REQ-CHECK-*` id. | State that the rows are added at land only (post-merge on `main`). Add the tagged test to 0.1 per SPEC-first. |
| C9 | medium | **22 of 24 criteria route through one unwritten script, and nothing checks the verb set.** Issue 0.4 has no `depends-on` and no criterion, yet must author verbs wrapping checkers and manifest rows that do not exist yet. The "Build green" gate invokes `plan066_checks.py build-clean` with no declared dependency on 0.4. | Mandate `argparse(choices=sorted(SUBCOMMANDS))` — the precedent exits **2** on an unknown verb, which reads as loud FALSE; a permissive dispatcher exits 0 and gives #364's silent false PASS. Add a `verbs-match` criterion and `0.4` to 1.2's deps. |
| C10 | medium | **R3's mitigation is now a phantom created by the C1 rewrite.** R3 claims the no-pipe form is mandated "in every criterion" — after the rewrite no criterion mentions pelican, a pipe, or `--fatal warnings` at all. | Restate R3 as a requirement on 0.4/1.2's implementation, and put "no pipe" into 0.4's text where the code is written. |
| C11 | medium | **The corpus widened but the site counts did not.** `README.md:417` is a **sixth** upstream-backend site (backend `github \| gitlab \| jira \| none`, plus the pre-gh-direct `bd github push`). SC8 and 4.5 still say five. And **2.4 is the only checker whose corpus is unstated**, so it is ambiguous whether it sees these; `README.md:25`'s `gh`/`glab` mention is exactly the allowlist case. | Parameterise 2.4's corpus; extend 4.5 and SC8 to the README site. |
| C12 | medium | **The harness checker needs a precision rule the plan omits.** `.config/opencode` and `.pi/agent` are the **correct** `surface_dir` values; only their `/skills` subpaths are retired. A flat denylist matches the real defects for the wrong reason and false-positives on correct surface-dir mentions. | Compare the `(scope, field)` tuple — `user_skills_subpath`/`project_skills_subpath` vs `surface_dir`. Also fix the citation: `yf/src/cmd/harness/prune_private.rs:487-488`. |
| C13 | low-medium | **Issue 8.1's "full verification sweep" does not depend on the Class-B half** — no 6.5, no 2.6/2.7/2.8, no Epic 3. It can pass before the manifest repair and CV wiring exist. | Add `6.5, 2.8, 3.5` to 8.1's `depends-on`. |
| C14 | low-medium | **pass-1.md's Concerns table omits the Recommendation column** the red-team contract requires. Issue 5.4's text still does not name `findings/diagram-reads.md`. | Use the four-column form; name the file in 5.4. |
| C15 | low-medium | **SC20 is pass-1 C2's vacuity class again.** A CI job can exist, be `if: false`, or never trigger on the paths that matter. | Assert the job's `on:`/`paths:` select `web/content/**`, `README.md`, `AGENTS.md`, and that it invokes all four scripts by name. |

## Missing

- No criterion asserted the four `check_web_*` CV rows or a `web/` §3 glob (C6) — the headline deliverable.
- No criterion asserted the table's verb set equals the script's subcommand set (C9).
- No tagged test for Epic 0's new `REQ-CHECK-*` id (C8).
- The bundle recorded no d2 or pelican version despite D7 pinning one (C2).

## Gate Assessment

`gate_consistency.py` → `PASS, 6 gates, 0 findings`; no cycle over 48 issues independently
re-derived. **Pass-1's C11 resequencing is sound** — `2.5 → gate → epic 4/5 → 4.9/5.3 → 2.6` is
acyclic with no deadlock. On "do the checkers still gate the repairs they verify?" — **yes, but
informally**: 4.1/4.2/4.9 run them directly; only the CV *wiring* is deferred, and its purpose is
future enforcement. The real cost of the deferral is C6. Two live gate defects: the Build-green
Test's undeclared precondition on 0.4 (C9), and the diagram gate's record location named only in
the gate and the broken SC11 (C14).

## Upstream Assessment

Unchanged from pass 1 and still sound. Pass-1 C14's fix landed. One residue: #317 now carries two
`resolves-upstream` declarations with different dispositions — `(partial)` on 1.2 and `(include)`
on 8.5. Defensible, but confirm `test_upstream_requirements.py` accepts the pair before intake.

## Resolutions

All 15 resolved by the main session under the autonomous default.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Fixed and verified.** `pass-1.md` now opens `## Verdict: REVISE`. Re-ran `ready-check`: `verdict: REVISE`, `malformed_review: null`. Read the field back, not the exit code. | `main-session` | `resolved` |
| C2 | high | **Fixed and verified.** Filled §Project environment (the four non-obvious `web/` facts), §Operator identity (role, authority scope, and the explicit note that the executing agent holds none of it) and §Runtime assumptions (zsh non-splitting, the absent worktree venv, no-CI-validation, the unsatisfiable-row constraint). Added `d2 v0.8.2` — named as the D7 pin — plus pelican 4.11.0 and zsh 5.9. `audit` now returns **pass**. | `main-session` | `resolved` |
| C3 | high | **Fixed and verified.** SC11 split: a literal `manual: a human must look at a rendered image; no command can decide it` row, and SC11b carrying the full clause. Confirmed `re.match(r'\Amanual:\s*\S', cell)` is now **True**. A defect I introduced in the pass-1 C1 rewrite, invisible to the linter because both instruments share the regex. | `main-session` | `resolved` |
| C4 | high | **Fixed, independently re-measured, and the FINDING amended.** Confirmed in a sandbox: two renders under v0.8.2 give identical sha256; committed `lifecycle.png` shares the fresh signature but differs in sha256. SC10 now asserts **sha256 equality against a fresh render under the recorded pin**. R8 amended, and `exp-004-diagram-pipeline.md` carries an amendment note — its "byte-verification is NOT viable" was true across versions and false within one. | `main-session` | `resolved` |
| C5 | high | **Fixed.** `4.5` added to Issue 5.3's `depends-on`. Audited the other `.d2`-editing issues: 5.1, 5.2 and 4.4 were already dependencies; 4.5 was the only omission. | `main-session` | `resolved` |
| C6 | medium-high | **Fixed.** New **SC25** asserts the four `check_web_*` §1 rows and the §3 globs selecting `web/content/**`, `README.md` and `AGENTS.md`. 2.6 removed from the uncovered list, with a note recording *how* two correct pass-1 resolutions combined to hide the primary deliverable. | `main-session` | `resolved` |
| C7 | medium-high | **Fixed.** Issue 4.3 now rewrites the `utility` and `markdown` bullets to enumerate backticked skill ids — making all four bullets uniform and checkable — and Issue 2.1's name-parsing is scoped to id-carrying bullets, with the other two declared `not_checked` under 2.7 until 4.3 lands. | `main-session` | `resolved` |
| C8 | medium-high | **Fixed.** Issue 0.5 now states the rows are added **at land only, post-merge on `main`**, quoting the §1 banner's "incapable of passing by construction". Issue 0.1 now requires the tagged test in the same change-set, ahead of code, per SPEC-first. | `main-session` | `resolved` |
| C9 | medium | **Fixed.** Issue 0.4 carries three implementation mandates — `argparse(choices=...)` so an unknown verb exits 2, no-pipe, and no hardcoded `web/.venv`. New Issue 0.4b authors a `verbs-match` subcommand asserting table verbs == subcommands. `0.4` added to Issue 1.2's deps, closing the gate's undeclared precondition. | `main-session` | `resolved` |
| C10 | medium | **Fixed.** R3's mitigation restated as what it now is — a requirement on the 0.4/1.2 implementation — and the no-pipe rule moved into Issue 0.4's text, where the code is actually written. | `main-session` | `resolved` |
| C11 | medium | **Fixed.** Issue 2.4's corpus is now the same parameter as 2.1/2.2, with `README.md:25` named as the allowlist case. Issue 4.5 and SC8 extended to **six** sites including `README.md:417`, with its `bd github push` contradiction of `UPSTREAM_TRACKING.md` recorded. | `main-session` | `resolved` |
| C12 | medium | **Fixed.** Issue 2.2 now mandates comparison against the `(scope, field)` tuple rather than a flat denylist, with the reason stated: `.config/opencode` and `.pi/agent` are correct `surface_dir` values. Citation corrected to `yf/src/cmd/harness/prune_private.rs:487-488`. | `main-session` | `resolved` |
| C13 | low-medium | **Fixed.** Issue 8.1's deps are now `4.9, 5.5, 6.5, 7.1, 7.2, 7.3, 2.8, 3.5` — the sweep can no longer pass before the manifest repair and CV wiring exist. | `main-session` | `resolved` |
| C14 | low-medium | **Fixed.** `pass-1.md`'s Concerns table rebuilt with the Recommendation column (verified 16 rows in each table, section-scoped so the Resolutions table was not overwritten). Issue 5.4 now names `findings/diagram-reads.md`. | `main-session` | `resolved` |
| C15 | low-medium | **Fixed.** SC20 now asserts the CI job is triggered by the paths that matter and invokes all four `check_web_*` scripts by name — not merely that a workflow file mentions them. | `main-session` | `resolved` |

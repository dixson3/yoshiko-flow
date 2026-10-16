---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 1, reading] REVISE: preflight never enforced herdr (union clause is a false premise); Epic 5 tag/verify deadlocks the landing's close chain; SC2/SC3/SC5/SC7 green-before-work or never-passable; doctor still fails without d2/pandoc; 12 concerns, 3 high"
plan: plan-073-james-dixson-cc76de
pass: 1
mode: reading
---
# Plan Red-Team: plan-073-james-dixson-cc76de

## Verdict: REVISE
**Mode:** reading

## Strengths
- SPEC-first sequencing holds: every implementation issue depends on its Epic 0 amendment, and each new REQ has a named, tagged test.
- The doctor severity model exists as the plan describes. `CheckResult::warn` gives `required: false`, `is_failure()` counts only `required && !ok` (`doctor/mod.rs:301-306`), and `SkillDepsCheck` (`checks.rs:352-378`) is the only thing that needs to change.
- The REQ-id-free gate is sound. I ran it and it exits 0, so all five ids are unallocated.
- The release mechanics follow #255/v0.5.0. The tag is behind a human consent gate, the tip-of-`main` and workflow-diff preconditions are asserted, and an INCONCLUSIVE result blocks the tag.
- The plan-folder checkers are clean: doc_lint, plan_extract `--strict`, gate_consistency and audit all exit 0.

## Concerns

| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: herdr off `PATH` in a sandbox, `yf preflight yf-herdr --json` → `"status":"ok","missing":[]`. `preflight.rs:597-634` `check_system_deps` only probes `git`, `uv` and `bd` | **False premise behind R1, SC3 and REQ-YF-DOCTOR-008.** Preflight has never enforced `herdr`. It ignores every `depends-on-tool` entry except git, uv and bd. So "preflight still reports `system_deps_missing` without herdr" is not something to preserve; it would be new behaviour. A general "preflight enforces `depends-on-tool ∪ optional-tool`" would also start failing preflight for yf-markdown-pdf/html (pandoc, xelatex) and yf-diagram-authoring (d2), which is a regression outside scope. yf-herdr's SKILL.md never calls `yf preflight`: its "preflight's four conditions" are its own prose checks (HERDR_ENV etc.). | Drop the union-enforcement clause from REQ-YF-DOCTOR-008, Issue 1.3 and SC3. Re-ground R1 in the fact that yf-herdr's inertness comes from REQ-HERDR-041 (`HERDR_ENV=1`), not from `yf preflight`. If preflight enforcement of herdr is actually wanted, scope it as a deliberate, herdr-only new behaviour with its own REQ. |
| C2 | high | measured: in the merge-blocked repo, `grep -n "Refuses any container with a non-terminal child" ${SKILL_DIR}/spec/landing.md` → exit 0 (L12). Landing L9/L13/L15 require the reconcile gate resolved and every bead terminal before `complete` | **Epic 5.3/5.4 and the landing deadlock.** Issue 5.3 runs "after the plan lands on `main`", but landing (L9 reconcile, L12 cascade, L13 complete-gate) cannot finish while 5.3 and 5.4 are open. The plan's own Reconcile Gate also needs "all execution beads closed". 5.3 cannot close before landing, and landing cannot complete before 5.3 closes. plan-054 hit this exact shape and descoped 6.8 at close (#255). | Take 5.3 and 5.4 out of the bead DAG: make the tag and verification a post-landing operator step recorded in `log.md`/`assets/`, or a follow-on bead/issue. Alternatively, declare that the release is the plan's own post-`complete` act and move SC11 out of the reconcile set. The plan must say which. |
| C3 | high | measured: `cargo test` with a zero-match name filter in a sandbox crate → exit 0. `grep -rn "skill_deps_optional_missing_is_warning\|strict_ignores_optional_tools\|optional_tool_preflight_union" yf/` → exit 1 (absent) | **SC2 and SC3 are GREEN before any issue runs (#384).** Both are pure `cargo test -p yf <name>` filters, which pass vacuously when the named test does not exist. `CHANGE-VALIDATION.md:71-72` documents this cargo property. SC1b's `cargo test -p yf optional_tool` half has the same flaw. These criteria cannot tell this plan's work apart from a misnamed test or no test at all. | Make each one fail closed. Add `&& cargo test -p yf -- --list 2>/dev/null \| grep -q '<test_name>: test'`, or `-- --exact <module::path>` together with a `--list` presence check. |
| C4 | medium-high | measured: `uv run skills/yf-research/scripts/test_link_normalizer.py` → exit 0 (7 passed) on the current tree | **SC7 is GREEN before execution.** Today's suite passes, so the criterion does not show that `check-quotes`, legacy-`quote` handling or `all` idempotence were added. | Add presence checks: `grep -q 'REQ-RESEARCH-025' …/test_link_normalizer.py && grep -q 'REQ-RESEARCH-026' …` and `uv run …/link_normalizer.py check-quotes --help` → exit 0. |
| C5 | medium-high | measured: `uv run scripts/checks/test_check_skill_readme_contract.py` → exit 1 (`ModuleNotFoundError: No module named 'pytest'`). `uv run scripts/checks/check_skill_readme_contract.py` → exit 0 today | **SC5 can never pass, and its other half is already green.** The test file has no PEP 723 pytest dependency. `CHANGE-VALIDATION.md:214` runs it as `uv run --with pytest python3 -m pytest …`. The checker half passes before any change. | Use the manifest's form: `uv run --with pytest python3 -m pytest scripts/checks/test_check_skill_readme_contract.py -q`. Add a grep for the new `optional-tool` negative-control test name so the criterion can be red before execution. |
| C6 | medium-high | measured: sandbox `yf doctor --json` with herdr, d2, pandoc and xelatex off `PATH` → exit 1, failing axes `skill-deps:yf-diagram-authoring` (d2), `skill-deps:yf-markdown-html` (pandoc) and `skill-deps:yf-markdown-pdf` (pandoc, xelatex) as well as yf-herdr | **The Objective and Motivation overclaim.** The Motivation calls the herdr axis "the only hard failure" and says the five fixes are "the ones a first-run user meets". After this plan, a new user without d2 or pandoc still gets `yf doctor` exit 1, so the headline "doctor warns (not errors) on missing optional-skill tools" will not hold for most users. Excluding d2/pandoc/xelatex was an operator decision; this concern is that the plan's framing does not match it. | Either bring d2 (at minimum) into `optional-tool` in this release, or correct the Motivation and add a CHANGELOG **Known limitations** line saying doctor still fails without pandoc, xelatex or d2. |
| C7 | medium | measured: `grep -n "PROJECT_GITIGNORE" yf/src/beads_init.rs` → its only non-test use is line 903, inside the repair `apply_native` gitignore step | **yf-htws only reaches repos that run `yf doctor --repair`.** The symptom cited was "`yf preflight yf-beads-init` reported `ok`" while the lock file dirtied the tree. Preflight's ok path never runs the top-up, so existing repos keep the problem until someone runs a repair. | Either state this limitation in REQ-BINIT-028 and the CHANGELOG, or add a verify-side advisory diagnostic when `/.beads.gate.lock` is untracked and not ignored. That fits the existing "advisory hygiene" block at `beads_init.rs:294`. |
| C8 | medium | measured: added `osf.io/preprints` to `TIER_4_DOMAINS` in-process (`uv run --with click`), then `_domain_authority_score("https://osf.io/preprints/psyarxiv/abc")` → 30 (unknown fallback, not Tier 4) | **The scorer matches tiers against netloc only.** A path-bearing entry like `osf.io/preprints` never matches. REQ-RESEARCH-027 and Issue 3.5 list it as a Tier-4 host. | Add path-aware matching in Issue 3.5 (the `.dev` denylist needs path inspection anyway) and a test case for `osf.io/preprints/...`. |
| C9 | medium | measured: `uv run skills/yf-change-validation/scripts/change_validation.py run --help` → options are only `--tier`, `--changed`, `--json`. `--resume` exists only on `scripts/checks/skill_trigger_eval.py:676` | **Issue 5.2 and R5 say to "resume with `--resume`"** for the FULL tier, but the FULL-tier entry point has no such flag. The mitigation as written cannot be followed. | Name the actual recovery: re-run the `trigger-eval` row directly with `skill_trigger_eval.py … --resume <results>`, then re-run FULL. Alternatively, add `--resume` plumbing as an explicit, REQ-tagged issue. |
| C10 | medium | inferred: landing step L3 already runs the FULL tier on the merged tree, and Issue 5.2 runs it again "on the merged tree" before landing (that tree does not exist until landing) | **Two ~5-hour runs, each with a ~$75–110 trigger-eval.** Also, the tree 5.2 validates (the execute branch) is not the tree that gets tagged. | Redefine 5.2 as the landing's L3 FULL run (recorded evidence), or run it after landing on `main`'s tip immediately before 5.3, so that the green result is for the tagged sha. |
| C11 | low | measured: `awk` over the v0.5.0 CHANGELOG section shows `plan-054` 3 times and `plan-027` 2 times | **SC9's "exactly once" is stricter than the precedent it cites.** Prose naturally cross-references plans more than once. | Either keep "exactly once" and tell the 5.1 author explicitly, or check only for a theme-list line per plan (e.g. anchor the count to a `- plan-0NN` bullet form). |
| C12 | low | measured: `grep -rln depends-on-tool` also hits `scripts/checks/check_required_set.py` (generated "At a glance" data) and the `_shared/test_doc_lint.py` fixture | **Issue 1.5's consumer list is incomplete** (R2 depends on it being complete). | Add `check_required_set.py` to Issue 1.5 so it is checked against `optional-tool` rendering in the "At a glance" block. |

## Measurements

| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SD/scripts/doc_lint.py --path $P/plan.md --json` | 0 | no findings |
| plan_extract | `uv run $SD/scripts/plan_extract.py $P --json --strict` | 0 | nothing unparsed |
| gate_consistency | `uv run $SD/scripts/gate_consistency.py $P --json` | 0 | 5 gates, no findings |
| amendment log (SC1) | `uv run scripts/check_amendment_log.py --plan plan-073-…` | 2 | INCONCLUSIVE, no entry yet (expected before execution) |
| audit | `uv run $SD/scripts/plan_manager.py audit $P --json-output` | 0 | okf_native |
| REQ-ids-free gate | the gate's `Test` line | 0 | all five ids free |
| SC4 | the two `grep -q` checks | 1 | not yet dischargeable (expected) |
| SC5 (test half) | `uv run scripts/checks/test_check_skill_readme_contract.py` | 1 | no pytest; criterion is broken (C5) |
| SC5 (checker half) | `uv run scripts/checks/check_skill_readme_contract.py` | 0 | green before execution |
| SC7 | `uv run skills/yf-research/scripts/test_link_normalizer.py` | 0 | green before execution (C4) |
| SC8 scorer half | `credibility_scorer.py score --url https://arxiv.org/abs/… ` | 0 | domain_authority 92, so SC8 is red (expected) |
| cargo zero-match filter | sandbox crate, `cargo test -q nomatch_filter` | 0 | vacuous pass (C3) |
| doctor, no herdr/d2/pandoc | sandbox `env -i … yf doctor --json` | 1 | four skill-deps error axes (C6) |
| preflight, no herdr | sandbox `yf preflight yf-herdr --json` | 0 | `status: ok`; herdr never enforced (C1) |

## Missing
- A stated post-landing home for the tag push and publication verification (C2).
- A CHANGELOG known-limitation for doctor still failing without d2, pandoc or xelatex (C6), and for gate-lock only being fixed by `--repair` (C7).
- Whether the `optional-tool` key is tolerated by every harness's SKILL.md frontmatter validation (pi enforces Agent Skills field rules per REQ-YF-EMBED-007). It is probably fine because `depends-on-tool` is already a custom key, but Issue 1.1 should say so.

## Gate Assessment
- **REQ-ids-free:** reachable and correctly one-shot (measured exit 0).
- **Baseline FAST:** reasonable and of `build` class. Consider blocking Epic 0 too, because the SPEC edits feed amendment-log and coverage rows. A red attributed after 0.x would otherwise be ambiguous.
- **release-authorized:** human consent is the right type, and existence-of-file is honestly framed as a record, not proof of who authorized. The gate is unreachable inside the plan's own lifecycle because of C2. Its Condition (after the FULL tier is green on the tagged tree) also conflicts with 5.2 running before the merge (C10).
- **Reconcile Gate:** "all execution beads closed" cannot be satisfied while 5.3/5.4 wait for landing (C2).

## Upstream Assessment
- #410 and #411 as include, with the operator-chosen options: reasonable, and each is wired to specific issues.
- #412 as partial: in/out is specific (undated currency stays out, and #412 stays open). The `osf.io/preprints` entry needs path-aware matching to deliver the included half (C8).
- #255 and #302 as exclude with context: appropriate.

Plan-review dispositions are fine. The structural problems are C1 (wrong premise about preflight), C2 (Epic 5 vs. landing deadlock) and C3–C5 (criteria that are green before execution or can never pass).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Union-enforcement clause dropped from REQ-YF-DOCTOR-008, Issue 1.3 and SC3. REQ-YF-DOCTOR-008 now states preflight is unaffected (probes git/uv/bd only), and every optional-tool skill must fail closed in its own entrypoint (Issue 1.4 confirms). R1 is re-grounded in REQ-HERDR-041 and the skills' own check_deps(). | `main-session` | `resolved` |
| C2 | high | Operator decision: the tag is a post-landing operator act, not a bead. Epic 5 now ends at Issue 5.1 (version bump + CHANGELOG). The landing's L3 FULL run is the release validation. The tag + verification are recorded in assets/ + log.md after landing. The release-authorized gate was removed. | `main-session` | `resolved` |
| C3 | high | Every cargo-test criterion (SC2, SC3, SC5, SC7) now asserts presence via `cargo test -p yf -- --list \| grep -q '&lt;name&gt;: test'` before running the filter. The form was verified against the existing `ensure_gitignore_idempotent: test` line. | `main-session` | `resolved` |
| C4 | medium-high | SC8 now requires `check-quotes --help` to exit 0 and greps for the five new test function names before running the suite. | `main-session` | `resolved` |
| C5 | medium-high | SC6 uses the manifest form `uv run --with pytest python3 -m pytest ...`, plus a grep for the new negative-control test `test_optional_tool_must_be_marked_optional`. | `main-session` | `resolved` |
| C6 | medium-high | Operator decision: pandoc, xelatex and d2 also move to optional-tool (yf-markdown-html, yf-markdown-pdf, yf-diagram-authoring). The new Issue 1.5 / SC5 is an end-to-end doctor run with only bd/uv/git on PATH, asserting no failing skill-deps axis. Motivation now cites the four-axis measurement. | `main-session` | `resolved` |
| C7 | medium | REQ-BINIT-028 adds a verify-side advisory diagnostic (hygiene block, beads_init.rs:294) when /.beads.gate.lock is untracked and unignored. Remediation is `yf doctor --repair`. Tested by verify_reports_unignored_gate_lock (SC7). Known limitation recorded for the CHANGELOG. | `main-session` | `resolved` |
| C8 | medium | REQ-RESEARCH-024(b) amended: a tier entry containing '/' matches netloc+path by prefix. Issue 3.5 implements it, and test_osf_preprints_path_match (SC10) covers osf.io/preprints. | `main-session` | `resolved` |
| C9 | medium | --resume removed from the FULL-tier wording. R5 now names the real recovery: re-run the trigger-eval row via `skill_trigger_eval.py ... --resume <results.jsonl>`, then re-invoke `land --apply`, which resumes from its journal. | `main-session` | `resolved` |
| C10 | medium | Old Issue 5.2 deleted. The landing's L3 FULL run on the merged tree is the release validation and is the tree that gets tagged. SC12 is a FAST tier on the execute branch. | `main-session` | `resolved` |
| C11 | low | SC11 now requires each existing plan 055-073 to be cited at least once, matching the v0.5.0 precedent where cross-theme plans recur (plan-054 x3, plan-027 x2). | `main-session` | `resolved` |
| C12 | low | check_required_set.py added to Issue 1.6 and SC6. gen-install-parity.py is named. The doclint fixtures are noted as sample text only. | `main-session` | `resolved` |

**Final status:** all 12 concerns resolved in plan v2 (main session, with two operator decisions: C2 tag placement, C6 optional-tool scope). Frozen.

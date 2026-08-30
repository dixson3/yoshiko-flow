---
okf_version: 0.2
---

# plan-061-james-dixson-6d8c97

> Standardize the README and code-adjacent documentation layout contract, and backfill all 20 skills to meet it. Plan 1 of 3 (tracker #315); the website realignment and OKF corpus backfill are #317 and #316

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-web-content-claims.md](findings/exp-001-web-content-claims.md) - Complete enumeration of false, stale and missing claims across web/content — including the measured finding that the Pelican site does not build at all, because skill_pages.py is fail-closed on the missing yf-okf-hygiene page. Deferred to issue 317; retained here as its evidence base.
- [findings/exp-002-mechanical-check-design.md](findings/exp-002-mechanical-check-design.md) - Classification of all 52 DRIFT-CHECK.md edges into mechanical (35), prose (9) and hybrid (8), the CHANGE-VALIDATION recipe seam, and the measured structural blind spot where optional and required node reachability both enforce nothing.
- [findings/exp-003-readme-contract-drift.md](findings/exp-003-readme-contract-drift.md) - Issue 244 re-measured at HEAD: 18 of 20 skills fail e-readme-layout, 12 SPEC.md omissions, 10 stale fence roots, and yf-okf-hygiene has no README at all. Every figure in issue 244 is stale-low. The evidence base for this plan.
- [findings/exp-004-missing-drift-edges.md](findings/exp-004-missing-drift-edges.md) - Designs for the missing drift edges from issues 291 and 247, the measurement that install.sh does not exist while 17 READMEs and DRIFT-CHECK.md itself cite it, and a sweep for artifacts no declared edge covers. The install.sh half lands here, the manifest half in issue 317.
- [references/upstream-104.md](references/upstream-104.md) - Upstream issue #104 - web: prevent runaway Pelican devservers + add clean teardown (port naba#21)
- [references/upstream-127.md](references/upstream-127.md) - Upstream issue #127 - web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
- [references/upstream-149.md](references/upstream-149.md) - Upstream issue #149 - M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
- [references/upstream-244.md](references/upstream-244.md) - Upstream issue #244 - README-contract drift: e-readme-layout fails 16/19 skills, and the manifest contract is stronger than anything enforcing it
- [references/upstream-247.md](references/upstream-247.md) - Upstream issue #247 - Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist
- [references/upstream-273.md](references/upstream-273.md) - Upstream issue #273 - The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py
- [references/upstream-291.md](references/upstream-291.md) - Upstream issue #291 - yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist
- [references/upstream-315.md](references/upstream-315.md) - Upstream issue #315 - Plan 1/3: standardize the README + code-adjacent documentation layout contract and backfill all 20 skills
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 on plan-061 — verdict REVISE with 10 concerns, 4 high. Both capability gates were unsatisfiable as written and all 12 success criteria were unexecutable prose; the plan's cited figures re-derived correctly.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 on plan-061 — verdict REVISE with 8 concerns, 2 high. Verified pass 1's ten resolutions (nine held, C7 was prose-only), upheld the main session's rejection of C5, and found that neither capability gate declared test_class/cwd so neither would ever have run.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 on plan-061 — verdict REVISE with 4 medium concerns, all textual. Verified 8 of 8 of pass 2 resolutions, cleared the worktree address-space question, and found that Gate 2 forbade a TRUE sentence about the hosted vendor installer.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 on plan-061 — verdict APPROVE. Gate 2 green-reachability proven by exhaustive enumeration (all 25 matched files authorized by an issue); six residual concerns C23-C28 folded in, including a shipped always-loaded rule the gate scope had omitted.

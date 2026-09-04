---
okf_version: 0.2
---

# plan-062-james-dixson-c3e98f

> Wire land --apply to _land_execute and add a seam-level test so a disconnected CLI entry point fails loudly (#327)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-seam-test-mechanism.md](findings/exp-001-seam-test-mechanism.md) - Measured comparison of four ways to drive `land --apply` past the tty gate in a test. Proves the in-process route discriminates broken from fixed, and that two alternatives create production-reachable bypasses.
- [findings/exp-002-apply-glue.md](findings/exp-002-apply-glue.md) - What glue wires the seam (~38 lines, most helpers already exist), and the headline finding that `_land_execute`'s resume is a no-op the seam would make reachable.
- [findings/exp-003-l7-frontmatter-fix.md](findings/exp-003-l7-frontmatter-fix.md) - DEFERRED at pass 4 (#326 cut from scope), retained as a solved design for a later plan. The #326 fix design (strip + temp file + compare-stripped-text) with a 7/7 spike, plus an independent L7 defect that silently discards failed writes.
- [references/upstream-327.md](references/upstream-327.md) - Full body of #327, the dead `--apply` executor. The issue this plan exists to close.
- [references/upstream-326.md](references/upstream-326.md) - Full body of #326, the `draft_body_path` vs OKF frontmatter collision.
- [references/upstream-304.md](references/upstream-304.md) - Full body of #304, the self-authorization residue. Design input for why the seam test adds no bypass; stays OPEN.
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 (REVISE, 15 concerns). The measured record of what was wrong with the first draft and how each concern was resolved.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 (REVISE, 11 concerns). Re-measured every pass-1 resolution and found 12 of 15 mechanically real; records the three residues, a subtle L0 lock-skipping hazard, and a main-session correction to its own C17.
- [references/upstream-266.md](references/upstream-266.md) - Full body of #266, the `## Gates` grammar gap that cannot express `test_class` or `cwd`. This plan works around it at pour (Issue 0.0) and does not close it.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 (REVISE, 10 concerns). Confirmed all 11 pass-2 resolutions real, and caught the C24 fix reproducing the plan's own headline defect by breaking SC13's table row with unescaped pipes.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 (REVISE, 10 concerns). Found that the mandated in-place mode makes `land` structurally unable to run, and that SC14/SC14b would halt the landing at L11 by querying `bd` without `--all`.
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 (REVISE, 10 concerns), after the operator narrowed scope. Confirmed the narrowing mechanically clean, and caught SC14/SC14b passing before anything was poured — the pass-4 fix having traded a false-fail for a permanent-true.
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6, a scoped verification (REVISE, 1 concern). Nine of ten pass-5 resolutions verified real, the clause surface clean for the first time in six rounds, and one record defect where a deleted criterion was still cited as a high risk's mitigation.
- [reviews/pass-7.md](reviews/pass-7.md) - Red-team pass 7, the close-out verification. APPROVE with zero concerns: C57's fix verified four ways, all 23 Verification clauses discriminating, every checker green, and every cited line number re-measured exact.

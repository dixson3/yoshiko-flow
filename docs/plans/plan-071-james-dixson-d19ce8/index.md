---
okf_version: 0.2
---

# plan-071-james-dixson-d19ce8

> Freeze yf-plan mechanism growth and convert the review loop from reading to executing, with an approval-to-landing fidelity metric and subtraction of declared-but-unenforced layers

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [diagrams/loop-before-after.d2](diagrams/loop-before-after.d2)
- [diagrams/loop-before-after.png](diagrams/loop-before-after.png)
- [findings/exp-001-req-land-coherence.md](findings/exp-001-req-land-coherence.md) - REQ-LAND is a coherent core of ~22 behaviours wrapped in ~48% defect narrative; 2 ids (015 gate-close half, 018 re-preview) describe behaviour that does not exist; prune to 22 ids / ~300 lines by merge and compression, not deletion
- [findings/exp-002-manager-dead-vacuous-audit.md](findings/exp-002-manager-dead-vacuous-audit.md) - Of 40 leaf verbs, 7 have no live caller and 3 live ones cannot fail by construction; exit 2 never halts in L8-L11; recheck-criteria IS a working oracle (71% of 515 criteria evaluated at --timeout 10; 10 completed plans FAIL) whose 300s default timeout hides that; the close chain is encoded three times with no joining test; plan-review and verify-artifact are unpoured; ~1,150 lines deletable
- [references/](references/)
- [reviews/pass-1.md](reviews/pass-1.md) - [red-team pass 1, reading] REVISE — D-10 premise false (2 ci-release plans exist), 4.4 contradicts 4.1, gate-consistency halt would fire post-push on gate-less plans; 13 concerns, 3 high, all measured
- [reviews/pass-2.md](reviews/pass-2.md) - [red-team pass 2, reading] REVISE — chain property: 12 of 13 pass-1 resolutions real, one half-applied (attest-validation deleted and retained); REQ-LAND merge map reaches 24 not 22; 6 concerns (1 high, 1 medium-high, 1 medium, 3 low)
- [reviews/pass-3.md](reviews/pass-3.md) - [red-team pass 3, EXECUTION] REVISE — 5 measured concerns: SC3 cannot go green (ugrep binary-match lines from __pycache__), bundle index drift, 6 shifted rows in pass-2 Resolutions, 018 placement ambiguity, findings-schema markers; all 20 SC rows RED for the right reason, arithmetic verified, 19/19 prior resolutions present
- [reviews/pass-4.md](reviews/pass-4.md) - [red-team pass 4, EXECUTION] APPROVE — all five pass-3 resolutions verified by execution; every bundle checker green; 19 of 20 SC rows RED for the right reason, SC3 green by declared invariant; 2 non-blocking notes

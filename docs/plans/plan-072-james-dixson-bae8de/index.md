---
okf_version: 0.2
---

# plan-072-james-dixson-bae8de

> Enforce the Agent Skills 1024-char description cap, add a crisp/satisfactory/loose description rating with cross-harness trigger evals, and bring skill descriptions toward 600 chars (#407)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-pilot-herdr-trigger-observation.md](findings/exp-001-pilot-herdr-trigger-observation.md) - [finding] Pilot, superseded by EXP-003: herdr tabs + session JSONL observe activation; pi loaded drift-check first, CC routed toward it but needed the intent's precondition to exist (intents need fixtures)
- [findings/exp-002-eval-cost-and-runtime.md](findings/exp-002-eval-cost-and-runtime.md) - [finding] CC 23.6 s and ~$0.22/run, pi 13.3 s/run; D3 as decided is ~360 runs/harness, ~2.4 h and ~$55-90 per FULL run; no-auth runs must be INCONCLUSIVE
- [findings/exp-003-baseline-trigger-fidelity.md](findings/exp-003-baseline-trigger-fidelity.md) - [finding] Baseline on the six sibling skills: CC 59/63, pi 57/63, near-misses 18/18, one wrong-sibling fire in 126 runs; every miss is 'did it without the skill', not sibling confusion; CC loads 9 yf trigger rules, pi 4
- [findings/exp-004-cc-listing-budget.md](findings/exp-004-cc-listing-budget.md) - [finding] CC skill listing is over budget today (33313 > 30000 chars); yf is 51% of it, so the trims bring it under
- [findings/exp-005-candidate-description-injection.md](findings/exp-005-candidate-description-injection.md) - [finding] Candidate descriptions can be rated pre-deploy: pi --no-skills --skill, CC project copy + --setting-sources project; other CC paths silently keep the installed text, so the harness must verify the loaded text
- [diagrams/plan-072-structure.png](diagrams/plan-072-structure.png) - [diagram] Epic structure: SPEC -> hard gate + eval harness -> trim/rate -> split gate -> guidance, redeploy, verify
- [references/upstream-189.md](references/upstream-189.md) - Upstream issue #189 - Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine
- [references/upstream-302.md](references/upstream-302.md) - Upstream issue #302 - yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts
- [references/upstream-407.md](references/upstream-407.md) - Upstream issue #407 - Five skill descriptions exceed the Agent Skills 1024-char cap — pi warns on every startup; cap is unenforced
- [assets/exp-003/intents.json](assets/exp-003/intents.json) - EXP-003's 21 intents (18 should-trigger with fixtures, 3 near-miss)
- [assets/exp-003/runner.py](assets/exp-003/runner.py) - EXP-003 eval runner (stop-on-activation, 6-tool cap)
- [assets/exp-003/rescore.py](assets/exp-003/rescore.py) - EXP-003 widened activation detector, re-scoring raw streams
- [assets/exp-003/rescored.txt](assets/exp-003/rescored.txt) - EXP-003 per-intent results and signal table (CC 59/63, pi 57/63)
- [assets/exp-003/run-cc.jsonl](assets/exp-003/run-cc.jsonl) - EXP-003 raw per-run results, claude-code
- [assets/exp-003/run-pi.jsonl](assets/exp-003/run-pi.jsonl) - EXP-003 raw per-run results, pi
- [diagrams/plan-072-structure.d2](diagrams/plan-072-structure.d2) - d2 source for the epic-structure diagram
- [reviews/pass-1.md](reviews/pass-1.md) - [red-team pass 1, reading] REVISE: FULL row tests the OLD installed descriptions; as specified FULL almost never passes; <=1024-but-misses-an-intent has no rating; 14 concerns, 4 high

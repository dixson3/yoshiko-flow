---
okf_version: 0.2
---

# plan-063-james-dixson-3f74c1

> Make landings stick: fix the L18 crash, make step dispatch fail-closed, and sweep the LAND_EXECUTOR chain (#340)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-signature-sweep.md](findings/exp-001-signature-sweep.md) - Whole-module arity sweep: 1 defect in 252 functions, refuting the dead-code-cluster hypothesis. Finds the real gap (4 of 78 stubs fake the wrong signature) and two further L18 defects.
- [findings/exp-002-dispatch-wrapper-and-rehearsal.md](findings/exp-002-dispatch-wrapper-and-rehearsal.md) - The exception wrapper, sandbox-proven, and the measured answer to why plan-060's rehearsal recorded l18_prune:pass on an unrunnable path.
- [findings/exp-003-dryrun-preflight-for-l16.md](findings/exp-003-dryrun-preflight-for-l16.md) - The dry-run facts that predict L16, plus the two unfiled defects this plan filed as #342 and #343.
- [references/upstream-340.md](references/upstream-340.md) - Full body of #340, the L18 TypeError that crashes every landing.
- [references/upstream-341.md](references/upstream-341.md) - Full body of #341, worktree_dirty can never report dirty.
- [references/upstream-333.md](references/upstream-333.md) - Full body of #333, a decision file inside the tree halts L16.
- [references/upstream-342.md](references/upstream-342.md) - Full body of #342, L16 commits the whole index and reports pass.
- [references/upstream-343.md](references/upstream-343.md) - Full body of #343, L16's journal filter is a substring match.
- [references/upstream-331.md](references/upstream-331.md) - Full body of #331, land is incompatible with execute.worktree:false — worked around, not closed.
- [references/upstream-332.md](references/upstream-332.md) - Full body of #332, upstream-drafts undocumented — excluded from scope.
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 (REVISE, 16 concerns). Caught the escaped-then-unescaped pipe that made a criterion impossible, a gate cycle the drafter had worded around rather than removed, and an invalid git argv that would have failed every landing.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 (REVISE, 13 concerns). Confirmed all 16 pass-1 resolutions real, and found that four of them introduced new defects — a DAG sink, an impossible exit code, a floor measuring growth rather than passing, and a false rationale.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 (REVISE, 7 concerns). Independently re-derived and confirmed four pass-2 resolutions, and found the mock-fidelity gate arithmetically unsatisfiable because an earlier fix moved two stub corrections upstream of the check that must find them.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 (REVISE, 4 concerns). Verified the pass-3 arithmetic correct, and caught that an earlier resolution had excluded fields from the landing digest without the SPEC change that normative deviation requires.
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 (REVISE, 2 concerns). Cleared REQ-LAND-036 against REQ-LAND-018, and caught an amendment-log count contradicting its own enumeration plus a stub fix set omitting the stub behind the first test it names.
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 (REVISE, 1 concern), the last authorized cycle. Verified both pass-5 fixes, and caught the mock-fidelity gate threshold wrong for the third time — now expressed as a floor so it survives further movement.
- [reviews/pass-7.md](reviews/pass-7.md) - Red-team pass 7: APPROVE. Verified the threshold fix by a parsed DAG walk, confirmed the gate stays discriminating and fail-closed, and found whole-plan coherence clean. One low informational note requiring no edit.
- [assets/gate-metadata-readback.md](assets/gate-metadata-readback.md) - Issue 0.0 / SC10 evidence: the set-then-assert record for all three capability gates. `plan_extract.py` silently drops `test_class:` and `cwd:` while reporting `unparsed: []`, so the metadata was parsed from plan.md, written at the pour, and read back here — with the §5.2c sweep verdicts.
- [assets/upstream-drafts/](assets/upstream-drafts/) - One draft closing body per non-`exclude` Upstream Issues row (#340, #342, #343, #341, #333 include; #331 partial). What `_land_upstream_rows` resolves as each row's `draft_body_path`; L7 posts them.
- [assets/residual-issues/](assets/residual-issues/) - Issue 6.1's eight residual findings this plan found and did NOT fix, drafted as full issue bodies with a README mapping each to its local bead and the proposed (unrun) `gh issue create`. Filing is an outward-facing write and is the operator's.
- [records/full-tier-run.md](records/full-tier-run.md) - Issue 6.3 / SC12: the FULL-tier verdict (68/68 pass), with HEAD, `main` tip and merge-base, the argument for why this IS the merged tree, and an honest note that the first run failed on this bundle's own index drift.
- [records/full-tier-run.json](records/full-tier-run.json) - The raw `change_validation.py run --tier full --json` envelope behind that record — every command, return code and output tail.
- [records/primary-checkout-carries-fixes.md](records/primary-checkout-carries-fixes.md) - Issue 6.4 / SC13: R3's mitigation checked rather than assumed. Why the primary is resolved via `--git-common-dir` and not `--show-toplevel`, and why the check is recorded even though in-place mode satisfies it trivially.
- [records/landing-handoff.md](records/landing-handoff.md) - Issue 6.5 / SC14: the Phase-6 route for the OPERATOR to execute, with the verbatim `apply_command`, an 8-row halt-recovery table (including the three halts this plan adds), and an explicit list of what is deliberately NOT authorized here.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).

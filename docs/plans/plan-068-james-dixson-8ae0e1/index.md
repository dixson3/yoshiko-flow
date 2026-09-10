---
okf_version: 0.2
---

# plan-068-james-dixson-8ae0e1

> Repair the land close chain: cover the --apply preamble with tests, make land work under execute.worktree false, and close the L8-L16 injection and measurement defects

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-worktree-false-landing.md](findings/exp-001-worktree-false-landing.md) - [finding] In-place landing halts at _land_manifest:8063 on bare branch existence; design (b) measured passing with zero REQ-LAND-* cost, design (c) refuted as a vacuously-green no-op merge; the bead's three-plan residue table is wrong (plan-061 ran in worktree mode)
- [findings/exp-002-ctxrun-seam.md](findings/exp-002-ctxrun-seam.md) - [finding] Seam-first VALIDATED by a zero-stub spike (18 rows+halt unpatched vs 23 rows+L_DONE patched); 8 bare calls not 7, and yf-i127's 'only one cwd-less call' is refuted - L17's bd show is the second and more dangerous; REQ-LAND-037 confirmed free
- [findings/exp-003-digest-exclusion.md](findings/exp-003-digest-exclusion.md) - [finding] yf-jp7z's premise CONFIRMED but its remedy REFUTED - the WIDE exclusion blinds the digest to all three foreign-landing classes and lets a conflicting landing validate 'pass'; real scope is five self-mutated facts across four resume points, and L4 alone mutates them, not L6
- [findings/exp-004-preamble-coverage.md](findings/exp-004-preamble-coverage.md) - [finding] 'Zero coverage' REFUTED as stated (61.4%, all happy-path plus one refusal, 17 uncovered statements all refusal bodies); the preamble has nine steps not six; #334's bypass and its test's vacuity both CONFIRMED by spike and by line data; yf-pyqn confirmed with two extra sites
- [references/upstream-304.md](references/upstream-304.md) - Upstream issue #304 - The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT
- [references/upstream-326.md](references/upstream-326.md) - Upstream issue #326 - `land`'s `draft_body_path` posts bundle files verbatim, but OKF requires them to carry frontmatter
- [references/upstream-331.md](references/upstream-331.md) - Upstream issue #331 - `land` is incompatible with `execute.worktree: false` — no execute branch is ever created
- [references/upstream-334.md](references/upstream-334.md) - Upstream issue #334 - `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally, and its test is vacuous
- [references/upstream-348.md](references/upstream-348.md) - Upstream issue #348 - The landing close chain bypasses ctx.run: bare subprocess.run gives L8-L15 the wrong cwd and no injection seam
- [references/upstream-349.md](references/upstream-349.md) - Upstream issue #349 - The land --apply executor frame is outside both REQ-LAND-030's wrapper and the test suite
- [references/upstream-350.md](references/upstream-350.md) - Upstream issue #350 - A measurement that failed is reported as a green number (L16 laundered unpushed count, check_amendment_log under-counted n_impl)
- [references/upstream-352.md](references/upstream-352.md) - Upstream issue #352 - land --dry-run never checks that a draft body satisfies requires_mention, so the failure surfaces only after the writes are public
- [references/upstream-353.md](references/upstream-353.md) - Upstream issue #353 - LAND_DIGEST_EXCLUDED omits resolved_target_tip and merge_preview, which L4/L6 self-mutate: every resume at or after L_VALIDATED is a guaranteed digest mismatch
- [references/upstream-360.md](references/upstream-360.md) - Upstream issue #360 - plan_manager land --apply ignores a validated 'skip' adjudication (l11_recheck_criteria) and halts on it AFTER the merge and push
- [reviews/pass-1.md](reviews/pass-1.md) - [red-team pass 1] REVISE - 14 concerns. Epic 5's journal projection cannot work as designed (the journal keeps only the LAST step's detail), the L2 boolean projection introduces a NEW silent-accept on foreign checkout dirt, SPEC-first is violated in six places, and Gate 1's test passes vacuously by two measured routes. Recommends splitting into two plans.
- [reviews/pass-2.md](reviews/pass-2.md) - [red-team pass 2] REVISE - 14 concerns on the restructured Plan A. REQ-LAND-037 would be FALSE the moment it landed (three indirect launchers via _run_git, and both declared exceptions were the wrong ones); Issue 2.5's end-to-end test was unreachable without Epic 1; SC9 was not executable; and three items were dropped by BOTH plans. Gate 1's pass-1 fix verified genuine.
- [reviews/pass-3.md](reviews/pass-3.md) - [red-team pass 3] REVISE - 9 concerns. The declared ctx-less helper set was SIX not three and one is SPEC-mandated by REQ-LAND-031; SC9 was green-by-construction at the point it is evaluated; the rehearsal stubs five things not three; and a FOURTH item was dropped by both plans while plan-069 falsely asserted plan-068 had done it. Counts and Gate 1 verified clean.
- [reviews/pass-4.md](reviews/pass-4.md) - [red-team pass 4] REVISE (targeted) - 9 concerns, reducing to 3 root causes. The AST seed set was itself short (_repo_root/_git_root), closure depth was undefined, the REQ-LAND-031 carve-out was an over-read, SC9 had a REPRODUCED false green at L1's down-merge, and L3/L18 could escape the sandbox into the real repo. Judged CONVERGING; every defect was found by RUNNING code, so a general pass-5 has negative value.
- [reviews/pass-5.md](reviews/pass-5.md) - [red-team pass 5, EXECUTION] REVISE - 6 concerns, all sentence-level. Executed the pass-4 fixes rather than reading them: closure depth is 13 not 10, the ctx-less set does NOT become empty (three helpers remain), Issue 1.1's runner= closes only half the sandbox escape (three filesystem probes need root=), and 8 tests break not 1. SC9, the REQ-LAND-031 retirement, runner= feasibility and all counts HELD under adversarial execution.
- [reviews/pass-6.md](reviews/pass-6.md) - [red-team pass 6, NARROW CONFIRMATION] APPROVE - all six pass-5 edits landed correctly and every measurement they cite was independently reproduced (closure frontier 6 / transitive 13, the eight test names, the three filesystem probes, the --no-ff merge, the _run_shell signature). Mechanical state clean. Residual risk is execution-surfaced, not review-surfaced.
- [assets/check_req_allocation.py](assets/check_req_allocation.py)
- [assets/execute-base.txt](assets/execute-base.txt)
- [assets/landing-hazard-playbook.md](assets/landing-hazard-playbook.md) - plan-068 — landing-hazard playbook (Issue 4.1)
- [assets/plan-069-relocation-audit.md](assets/plan-069-relocation-audit.md) - Issue 3.3 — does plan-069 carry every item this split relocated?
- [assets/rehearsal-record.json](assets/rehearsal-record.json)
- [assets/req-allocation.md](assets/req-allocation.md) - plan-068 — REQ id allocation record (Issue 0.2)
- [findings/exec-001-inherited-doclint-red.md](findings/exec-001-inherited-doclint-red.md) - exec-001 — an INHERITED FAST/FULL-tier red, measured at Epic 0
- [assets/upstream-drafts/331.md](assets/upstream-drafts/331.md)
- [assets/upstream-drafts/348.md](assets/upstream-drafts/348.md)
- [assets/upstream-drafts/349.md](assets/upstream-drafts/349.md)
- [assets/upstream-drafts/353.md](assets/upstream-drafts/353.md)

---
okf_version: 0.2
---

# plan-057-james-dixson-9ecf1c

> OKF part 2: deepen the root index, ship yf-okf-hygiene with the legacy backfill, and realign OKF-BASELINE to the relocated upstream

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [findings/](findings/) - The six EXP-001..006 reports inherited verbatim from plan-056, so this bundle reads cold without its predecessor.
- [references/](references/) - Upstream issue bodies for the OKF cluster items this plan carries (#140, #168, #169, #170, #171, #192).

## Assets

- [assets/](assets/) - Measurement records this plan's criteria read directly: `sc3-frozen-bundles.txt`, the 25-bundle frozen denominator SC3's boilerplate ratio is computed over.

## Reviews

- [reviews/](reviews/) - One `pass-N.md` per red-team cycle, written at presentation and updated in place as concerns resolve.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/sc3-frozen-bundles.txt](assets/sc3-frozen-bundles.txt)
- [findings/exp-001-reindex-drift-gate.md](findings/exp-001-reindex-drift-gate.md) - What should the reindex drift gate check, and would it be stable enough to gate on? (D-1's hinge)
- [findings/exp-002-description-producer-contract.md](findings/exp-002-description-producer-contract.md) - The premise is half-wrong — agents hit 51/51 since plan-052 with no prompt; the code producers sit at 1%.
- [findings/exp-003-deepen-root-index.md](findings/exp-003-deepen-root-index.md) - What does deepening the root index to enumerate nested files require of okf.py? (D-4's hinge)
- [findings/exp-004-layer-ownership-boundary.md](findings/exp-004-layer-ownership-boundary.md) - The two engines overlap on 6 frontmatter keys on 56 files out of 48 checks and 1105+ documents — D-3's retain-both is confirmed by measurement, not judgement.
- [findings/exp-005-backfill-and-hygiene-skill.md](findings/exp-005-backfill-and-hygiene-skill.md) - The backfill is mechanical but `okf migrate` gets it wrong — it introduces a hard audit failure on 30/30. And the corpus is 514 bundles across 41 repos, not ~100.
- [findings/exp-006-round-trip-and-repin.md](findings/exp-006-round-trip-and-repin.md) - Only 32 of 1567 okf-lint findings are the genuine disagreement, and all 32 flip on root framing — which OKF v0.2 is silent on. The write half cannot be tested.
- [references/upstream-140.md](references/upstream-140.md) - Upstream issue #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model Full untruncated body, snapshotted at triage.
- [references/upstream-168.md](references/upstream-168.md) - Upstream issue #168 — yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3 Full untruncated body, snapshotted at triage.
- [references/upstream-169.md](references/upstream-169.md) - Upstream issue #169 — OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3 Full untruncated body, snapshotted at triage.
- [references/upstream-170.md](references/upstream-170.md) - Upstream issue #170 — OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3 Full untruncated body, snapshotted at triage.
- [references/upstream-171.md](references/upstream-171.md) - Upstream issue #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9) Full untruncated body, snapshotted at triage.
- [references/upstream-189.md](references/upstream-189.md) - Upstream issue #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine Full untruncated body, snapshotted at triage.
- [references/upstream-192.md](references/upstream-192.md) - Upstream issue #192 — Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity Full untruncated body, snapshotted at triage.
- [references/upstream-289.md](references/upstream-289.md) - Upstream issue #289 - yf-plan: no instrument compares a plan's cited figures against its own commands' output
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 of plan-057: all three declared anti-vacuity defences measured inert; 8 blockers, 9 observations, all resolved in place.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — REVISE. 6 blockers. Pass 1's repairs verified by EXECUTION: most sound, but Issue 1.7's premise was refuted, SC3's frozen set contradicted itself, and R11 went stale within hours.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — REVISE. 2 blockers: SC17 used a pytest form measured to exit 2 (a criterion that CANNOT PASS), and SC12's path contradicted its producer. Nine pass-2 repairs verified sound by execution.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — REVISE. 2 blockers: SC17's direct-file form is vacuous without a __main__ runner, and pass-3's `bash <missing>` repair was measurably false (127, not 1) across four criteria.
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — APPROVE. Zero blockers. Both of pass 4's repairs verified by execution, including a spike proving one test file satisfies both invocation paths. Six non-blocking specification clauses, all fail-red.
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 — APPROVE. A post-approval cross-plan concurrency audit raised four defects; three reproduced and are repaired, one (D4, 'gates are never poured as beads') is REFUTED by measurement — its root cause is that `bd list --all` structurally excludes gate-typed beads. R12 rewritten to the measured mechanism with a sequencing decision; #290's crash brought in scope; rule D's `<=10` test disambiguated.
- [assets/backfill.json](assets/backfill.json)
- [assets/upstream-drafts/140.md](assets/upstream-drafts/140.md) - Draft reconcile comment for upstream #140, PARKED — awaiting an operator grant to post.
- [assets/upstream-drafts/170.md](assets/upstream-drafts/170.md) - Draft reconcile comment for upstream #170, PARKED — awaiting an operator grant to post.
- [assets/upstream-drafts/171.md](assets/upstream-drafts/171.md) - Draft reconcile comment for upstream #171, PARKED — awaiting an operator grant to post.
- [assets/upstream-drafts/189.md](assets/upstream-drafts/189.md) - Draft reconcile comment for upstream #189, PARKED — awaiting an operator grant to post.

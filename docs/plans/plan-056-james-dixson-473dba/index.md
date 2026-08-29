---
okf_version: 0.2
---

# plan-056-james-dixson-473dba

> OKF: make the structural validation that already exists able to fail, and reconcile the two layers that perform it.
>
> **Split at intake-drafting:** root-index depth, the `yf-okf-hygiene` skill and the baseline re-pin moved
> to `plan-057-james-dixson-9ecf1c` (D-17), on red-team pass 3's recommendation and the operator's decision.

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - Six investigation reports (EXP-001..006), each separating **measured:** from **inferred:**. They are the plan's entire evidence base and are inherited verbatim by plan-057.
- [reviews/](reviews/) - The red-team passes, newest last. Passes 1-6 each found the criteria layer vacuous in a different shape — `-k` no-ops, missing-script exit 2, unjudged-reads-as-PASS, a guaranteed-green backstop, a `bash -n` regression, and a pour directive the extractor silently truncated. Passes 7-8 found a different class: sibling artifacts (`context.md`, `upstream-triage.md`) that drifted from `plan.md` with every instrument green. **Read the newest pass first.** This line deliberately carries no pass count: a number that must be edited every cycle is a drift generator, and `reindex --check` cannot catch it because it checks membership, not description content.
- [references/](references/) - Full untruncated bodies of the 15 upstream issues this plan triaged, including #265, which the plan itself filed during review.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [findings/exec-001-doc-lint-demotion-measurement.md](findings/exec-001-doc-lint-demotion-measurement.md) - Re-derived measurement of doc_lint's terminal-status demotion — 392 findings demoted, 197 of them truly E (2026-08-28).
- [findings/exec-002-gate-catches-the-original-regression.md](findings/exec-002-gate-catches-the-original-regression.md) - The shipped drift gate was tested against the ACTUAL regression that went unnoticed for nine days — it fires (exit 1) and clears (exit 0), with no residue.
- [findings/exp-001-reindex-drift-gate.md](findings/exp-001-reindex-drift-gate.md) - What should the reindex drift gate check, and would it be stable enough to gate on? (D-1's hinge)
- [findings/exp-002-description-producer-contract.md](findings/exp-002-description-producer-contract.md) - The premise is half-wrong — agents hit 51/51 since plan-052 with no prompt; the code producers sit at 1%.
- [findings/exp-003-deepen-root-index.md](findings/exp-003-deepen-root-index.md) - What does deepening the root index to enumerate nested files require of okf.py? (D-4's hinge)
- [findings/exp-004-layer-ownership-boundary.md](findings/exp-004-layer-ownership-boundary.md) - The two engines overlap on 6 frontmatter keys on 56 files out of 48 checks and 1105+ documents — D-3's retain-both is confirmed by measurement, not judgement.
- [findings/exp-005-backfill-and-hygiene-skill.md](findings/exp-005-backfill-and-hygiene-skill.md) - The backfill is mechanical but `okf migrate` gets it wrong — it introduces a hard audit failure on 30/30. And the corpus is 514 bundles across 41 repos, not ~100.
- [findings/exp-006-round-trip-and-repin.md](findings/exp-006-round-trip-and-repin.md) - Only 32 of 1563 okf-lint findings are the genuine disagreement, and all 32 flip on root framing — which OKF v0.2 is silent on. The write half cannot be tested.
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — REVISE. Five criteria measured GREEN on unmodified HEAD; the -k filter is a no-op in every test script in the repo.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — REVISE. Pass 1's finding recurs inside its own resolution: the vacuity moved from -k filters into unowned instruments and missing-script exit codes.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — REVISE. Third recurrence confirmed: 26 unjudged criteria launder into verdict PASS, and SC11b is the mechanism. Plus a supported argument that the plan should split.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — REVISE. Fourth recurrence: SC0 omits the one script it exists to guard, and is itself a guaranteed-green row that launders INCONCLUSIVE into PASS.
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — REVISE. Fifth recurrence, in pass 4's own fix: bash -n detects neither 126 case and loses the 127 case test -x caught, and the capability gate defaults to a class that is never run.
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 — REVISE. Sixth shape: the pour directive sits after a blank line and the extractor silently truncates it, and --require 10 created a gate-reachability cycle.
- [reviews/pass-7.md](reviews/pass-7.md) - Red-team pass 7 — REVISE, narrow and terminal-shaped. All five of pass 6's fixes verified sound and no seventh shape in the criteria layer; the remaining defects are in context.md and upstream-triage.md, which six passes never opened.
- [reviews/pass-8.md](reviews/pass-8.md) - Red-team pass 8 — REVISE, narrow. Eighth shape: SC11c claims two files and verifies one, in the artifact pass 7 created to close that family. Plus five derived counts invalidated by adding one issue.
- [reviews/pass-9.md](reviews/pass-9.md) - Red-team pass 9 — APPROVE. Every count re-derived mechanically and exact; the design layer has not moved since pass 7. Five single-line factual corrections, none blocking.

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

---
okf_version: 0.2
---

# plan-059-james-dixson-55137e

> Design yf-judgement: an automatically-triggered escalation path that raises a structured question to the nearest upstream controller when a plan stops converging, with the severity-vocabulary pin as its prerequisite deliverable and the severity-decay detector as an optional, second-order add-on

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [references/scoping-decisions.md](references/scoping-decisions.md) - The four operator-supplied constraints (S1-S4) that bound this design, the mid-scoping exact-match correction, and the six decisions taken at scoping (D-1..D-6). Read second — it is what makes the epic structure legible.
- [references/upstream-269.md](references/upstream-269.md) - Full body of the yf-judgement proposal issue: research 005's five null predictions, the four design constraints, and the six claimed yf-retrospective synergies this plan tests.
- [references/upstream-264.md](references/upstream-264.md) - Full body of the yf-herdr AUTONOMY defect: the escalation architecture, the one-hop REQ-HERDR-024 predicate, and the three-boundary natural experiment.
- [references/upstream-145.md](references/upstream-145.md) - Full body of the yf-retrospective proposal: the escape taxonomy, the origin-vs-culpability split, and finding 4 ("a manually-invoked skill will not be invoked").
- [findings/exp-001-trigger-point-survey.md](findings/exp-001-trigger-point-survey.md) - Does a reliably-firing automatic trigger point exist? Verdict: no mechanical trigger exists anywhere in yf — but the measured discriminator is command-vs-obligation, not prose-vs-mechanical.
- [findings/exp-002-severity-vocabulary-census.md](findings/exp-002-severity-vocabulary-census.md) - The severity census, the control hand-read the research left undone, and the discovery that the study's own parser deletes HIGH severities. The detector's shippability condition FAILS here.
- [findings/exp-003-145-synergy-audit.md](findings/exp-003-145-synergy-audit.md) - The six claimed yf-retrospective synergies audited against landed code: two do not hold, one is stale, plus six missed synergies and five anti-synergies.
- [findings/exp-004-escalation-mechanism.md](findings/exp-004-escalation-mechanism.md) - The escalation channel surveyed against the live herdr API: there is no answer-return path, so escalation is write-then-notify. Also the proposed question schema and its home.
- [assets/plan-059-review.bento.html](assets/plan-059-review.bento.html) - Operator-authored review deck for this plan (single-file Bento presentation). An attachment, not a diagram, so it lives in `assets/` per the bundle convention; listed here because an unindexed bundle member is the defect Issue 2.4 exists to prevent.
- [reviews/](reviews/) - The five red-team passes, each written at presentation with its Resolutions table updated in place. Read pass-5 first: it carries the stop-class-4 escalation and the structural lesson.
- [findings/verification-sweep.md](findings/verification-sweep.md) - Every gate Test and every non-manual criterion, executed with exit codes recorded. 17 of 18 correctly RED before the work; the one green is a verified regression guard, and the progress-vs-invariant distinction it forced.
- [findings/finding-command-vs-obligation.md](findings/finding-command-vs-obligation.md) - The measurement elevated out of EXP-001 because it is not about yf-judgement: one law explaining #264, #270 and #145's finding 4, and the design test this plan applies to itself.
- [references/escalation-log.md](references/escalation-log.md) - This session's own dogfooding record of the mechanism being designed: every escalation raised OR deliberately declined, with what each taught the design. The only counterfactual arm available (research 005 §9.4 records that none exists in the corpus).

- [references/upstream-273.md](references/upstream-273.md) - Full body of the command-vs-obligation law as filed upstream — carrying the WITHDRAWN per-event framing that Issue 6.4 corrects.
- [references/upstream-270.md](references/upstream-270.md) - Full body of the `plan-review` never-poured defect, filed from this plan's escalation E-3 and scoped out by operator decision. Load-bearing for Issue 3.4 and SC7.
- [references/research-005-extract.md](references/research-005-extract.md) - Verbatim §7, §8 and §9 of the `yf-research` 005 report — the empirical basis this plan reasons from. Vendored because the report is NOT on this branch or on `main`.

**External dependency, and read this before chasing a path.** The empirical basis for this plan is `yf-research` 005. Its bundle is **not present in this repository on this branch or on `main`** — it lives on the unmerged branch `research/005-thrash-detection`, PR **#267**, at `docs/research/005-thrash-detection-and-operator-judgement/`. The full report is 1,249 lines with 228 cited sources. The three sections this plan's reasoning depends on (§7 recommendation, §8 escalation assessment, §9 absence findings) are **vendored verbatim** into `references/research-005-extract.md`, so a cold reader needs nothing outside this folder.

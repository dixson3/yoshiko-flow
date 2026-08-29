---
okf_version: 0.2
---

# plan-051-james-dixson-2f499f

> Land the descoped plan-050 work: the red-team sandbox-spike rule (#182), sub-agent dispatch for review (#184), and M9 remediation-edge attribution (#149) — each from plan-050's measured evidence

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [reviews/](reviews/) - The red-team review records, one per cycle, each with its Concerns table and resolutions. The review history behind the plan's current shape.
- [findings/](findings/) - The five investigation records this plan's decisions rest on. EXP-001 (what #184's Verification can honestly assert), EXP-002 (#182's 7-file blast radius), EXP-003 (executable-Verification prior art), EXP-004 (control-harness reuse, and the refutation of plan-050's D-8), EXP-005 (the review wisp: buildable, unevidenced).
- [references/](references/) - Full untruncated bodies of the eleven candidate upstream issues, so a cold reader can judge each disposition without network access.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/](assets/) - The driven-red harness and its records: `gate-run.sh`, the control manifest `controls.txt`, the pre-fix baseline, the #182 edit-set, the closable sweep, and the fixture corpus the controls run against.
- [scripts/](scripts/) - `gen_handoff.py` — generates AND `--check`s the handoff to plan-052 from this plan's own tables, so 'generated, not hand-listed' carries an exit code.
- [findings/exp-001-dispatch-verification.md](findings/exp-001-dispatch-verification.md) - For
- [findings/exp-002-182-blast-radius.md](findings/exp-002-182-blast-radius.md) - What is the COMPLETE edit set for
- [findings/exp-003-executable-verification.md](findings/exp-003-executable-verification.md) - Does any SPEC `Verification:` line in this corpus actually EXECUTE today, and by what mechanism?
- [findings/exp-004-redcheck-reuse.md](findings/exp-004-redcheck-reuse.md) - Can plan-050's driven-red control harness be reused, and can a control exist for each of this plan's three subjects?
- [findings/exp-005-review-wisp.md](findings/exp-005-review-wisp.md) - Is a parallel-lens plan-review wisp buildable without `waits-for`, and is parallelism evidenced?
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5
- [scripts/gen_handoff.py](scripts/gen_handoff.py)

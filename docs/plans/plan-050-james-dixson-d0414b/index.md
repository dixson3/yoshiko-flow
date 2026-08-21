---
okf_version: 0.2
---

# plan-050-james-dixson-d0414b

> Fix the four mechanical process defects this session's plans demonstrably hit (#178-#181). Every control
> ships having been observed RED before its fix landed. **Narrowed by the D-9 split at review cycle 5**: M9/#149,
> #182 and #184 went to plan-051; #177 was dropped on evidence (D-6). Epic numbering is gapped (0-3, then 6)
> deliberately — renumbering is what produced stale references in three consecutive review rounds.

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - The candidate pool from the automated scan. The rows **plan.md's Upstream Issues table acts on** carry a disposition and reasoning mirrored from that table, which is authoritative; every other section is an unscored candidate and is deliberately blank. No count is stated here — it went stale twice (pass-6 C58).
- [findings/](findings/) - The six investigation findings this plan's decisions rest on. Every measured figure in plan.md originates here; per D-5 nothing is inherited from research 004 without re-measurement.
  - [exp-001-target-derivability.md](findings/exp-001-target-derivability.md) - REFUTES #177 as filed: the successor citation-presence check PASSES both plan-049 criteria it was built for, and the first scanner's 101-row denominator was a large undercount (167 measured).
  - [exp-002-close-chain.md](findings/exp-002-close-chain.md) - 49 of 49 start-gate wrappers closed by hand, with **29 distinct** improvised reasons (pass-3 C20 corrected "a different one each time"). Root cause at the pour seam.
  - [exp-003-silent-green.md](findings/exp-003-silent-green.md) - A nonexistent path and a real-but-unselected file return byte-identical verdicts.
  - [exp-004-m9-remediation-edge.md](findings/exp-004-m9-remediation-edge.md) - 26 discovered-from edges, 0 attributed. Revises M9 from a missing relationship to a missing stamp. **Evidence for plan-051** after the D-9 split; independently reproduced at pass 5, including the 7-hour bead-vs-edge skew.
  - [exp-005-grant-generation.md](findings/exp-005-grant-generation.md) - The disposition map already exists — but its recommendation (call `_verify_row` directly) was **SUPERSEDED at pass-3 C12**; the plan ships a shared requirement table instead (Issues 3.2/3.2a).
  - [exp-006-red-team-rule.md](findings/exp-006-red-team-rule.md) - The rule is one line and never forbade a spike; the defect is under-specification. **Evidence for plan-051** after the D-9 split.
- [references/](references/) - One file per triaged upstream issue, with the full untruncated body, URL, labels and state — so the upstream context survives without network access. Issue 6.5 also lands `handoff-051.md` here, carrying the deferred Epic 4/5 material to plan-051.
- [reviews/](reviews/) - Red-team and conformance review records, one file per cycle, with the verdict and per-concern resolutions.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).

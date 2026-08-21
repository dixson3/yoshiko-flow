---
okf_version: 0.2
---

# plan-050-james-dixson-d0414b

> Fix the six mechanical process defects this session's plans demonstrably hit (#178-#181, #186, #187). Every control
> ships having been observed RED before its fix landed. **Narrowed by the D-9 split at review cycle 5, then widened back to six by D-10 (#186, #187)**: M9/#149,
> #182 and #184 went to plan-051; #177 was dropped on evidence (D-6). Epic numbering is gapped and out of order (0-3, 7, then 6)
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
- [references/](references/) - One file per triaged upstream issue, with the full untruncated body, URL, labels and state — so the upstream context survives without network access. Also the ten drafted upstream comments (`comment-*.md`), the tracker draft, and the generated handoff.
  - [references/handoff-051.md](references/handoff-051.md) - What plan-050 carries to plan-051. **GENERATED** from plan-050's own tables by `scripts/gen_handoff.py`; `--check` regenerates and diffs, exiting 1 on any difference (SC18). Carries the 8 `partial`/`deferred` rows, the descoped SPEC amendments (exempt from the tables-only rule — they appear in no table), and the session's headline finding with its #188/#190 link.
  - [references/comment-*.md](references/) - The ten upstream comment bodies, drafted from the `grant` verb's enumeration and posted verbatim at Issue 6.4.
  - [references/tracker-050-draft.md](references/tracker-050-draft.md) - The coarse tracker body, folded into the epic bead's `description` and filed as #193 through `/yf-beads-upstream`.
- [scripts/](scripts/) - Executable checks this plan ships for its own criteria.
  - [scripts/gen_handoff.py](scripts/gen_handoff.py) - Generates AND checks `references/handoff-051.md`. SC18's exit code: "generated, not hand-listed" is a provenance claim with no exit code, so the assertion is the equivalent content check — regenerate from the tables and diff.
- [reviews/](reviews/) - Red-team and conformance review records, one file per cycle, with the verdict and per-concern resolutions.
- [assets/](assets/) - The plan's own executable harness and its records. Not diagrams (those live in `diagrams/`), not attachments — these are run by the plan's gates.
  - [assets/redcheck.sh](assets/redcheck.sh) - The driven-red harness (D-4). Three verbs: `record-red` observes a control failing against the UNFIXED tree, `assert-distinguishes` observes it passing against the FIXED tree and refuses to certify a control it has only ever seen green, and `verify-all` is what the capability gate's `Test:` calls. Aggregate exit 0/1/2.
  - [assets/controls.txt](assets/controls.txt) - The manifest `verify-all` enumerates over — one control id per line. A control absent from this file is a control the gate CANNOT SEE, which is why `verify-all` also asserts the line count equals the number of ids plan.md declares.
  - [assets/gate-run.sh](assets/gate-run.sh) - The 0/1/2 normalising wrapper (adopted from plan-049 Issue 0.7), so a missing or crashing harness reports 2 (INCONCLUSIVE) rather than bash's raw 127.
  - [assets/red-prework.md](assets/red-prework.md) - Append-only observation log. One line per observation: verb, control, fixture, exit code, verbatim command, UTC timestamp, `git describe`. The `git describe` field is diagnostic only and makes no ordering claim (pass-7 C69).
  - [assets/sc7-baseline.md](assets/sc7-baseline.md) - SC7's corpus `files_checked` baseline, captured BEFORE any Epic-2 change. Only the `--exclude`d figure is recorded; the unfiltered one drifts every time this plan writes into its own bundle.
  - [assets/neg-179-observations.md](assets/neg-179-observations.md) - SC4's two observations of the `neg-179-open-wrapper` NEGATIVE control, pre- and post-fix. Recorded here rather than in `red-prework.md` because its assertion is invariant across the fix, so it is not a redcheck control and the gate never asks it for a GREEN record.
  - [assets/sc7-remeasure.md](assets/sc7-remeasure.md) - Issue 2.3's post-change measurement: the corpus figure against the 757 baseline, `test_doc_lint.py`'s result and edit scope, and the FAST tier over a `doc_lint.py` change — the gate that refuted two earlier scopes.
  - [assets/extraction-delta-050.md](assets/extraction-delta-050.md) - Issue 7.5 / SC24: the #186 and #187 fixes measured on this plan's own bundle — 27 titles restored, `detail` delta ZERO recorded as a negative observation, DAG unchanged at 41 edges.
  - [assets/upstream-grant-proposal.md](assets/upstream-grant-proposal.md) - The complete upstream-write authorization PROPOSAL, generated by the Issue 3.2a `grant` verb and reconciled against the Upstream Issues table. Every issue, every verbatim comment body, every close. Nothing in it has been executed.
  - [assets/sc15-full-validation.md](assets/sc15-full-validation.md) - SC15: the FULL validation tier over the merged tree — engine `change-validation`, 45 commands, 45 pass, 0 failures.
  - [assets/upstream-authorization.txt](assets/upstream-authorization.txt) - The operator's grant, in the form `grant --check` reconciles against. Scope and non-scope both stated explicitly.
  - [assets/upstream-writes-verified.md](assets/upstream-writes-verified.md) - Issue 6.4: the eleven authorized writes, their STRUCTURAL verification, the six rows deliberately NOT touched (re-checked afterwards), and SC17's verdict.
  - [assets/fixtures/](assets/fixtures/) - One fixture per control. A fixture exits 0 iff its control's asserted behaviour holds — non-zero before the fix, zero after. Negative controls, whose assertion is invariant across the fix, are NOT fixtures and are not listed in `controls.txt`.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).

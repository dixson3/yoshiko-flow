---
okf_version: 0.2
---

# plan-058-james-dixson-0e36fd

> Fix yf-beads-upstream upstream.py push: eliminate the full-universe per-bead bd show fan-out in the owner-claim warning path, bound run() with a timeout, and repair the identical defect in cmd_enumerate (#268)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [references/upstream-268.md](references/upstream-268.md) - The full, untruncated body of GitHub issue #268 — the SIGINT traceback, three-defect diagnosis and measured timings this plan was commissioned to validate and fix.

## Findings

Six experiments. Each carries **Approach Tested / Result / Implications for Plan / Recommendations**.

- [findings/exp-001-diagnosis-validated.md](findings/exp-001-diagnosis-validated.md) - Ran the #268 reproduction to completion: **334 s, exit 0**. Validates the diagnosis by observation rather than arithmetic, and explains the "no stdout" symptom as stdout block-buffering.
- [findings/exp-002-one-call-rewrite-is-exhaustively-equivalent.md](findings/exp-002-one-call-rewrite-is-exhaustively-equivalent.md) - The load-bearing result: `bd list --all --json` already carries the edges, and the one-call derivation is **exactly equivalent over all 1,801 beads** (0.0018 s vs 321.9 s).
- [findings/exp-003-run-timeout-design.md](findings/exp-003-run-timeout-design.md) - The `run()` timeout design, and the correction that a per-call bound would **not** have caught #268.
- [findings/exp-004-blast-radius.md](findings/exp-004-blast-radius.md) - The fix is one function and zero call-site edits; the real risk is a coverage gap, not breakage.
- [findings/exp-005-n-plus-1-defect-class.md](findings/exp-005-n-plus-1-defect-class.md) - This N+1 was already fixed once here (REQ-BUP-052) and not swept; the prose prohibition that exists was violated anyway.
- [findings/exp-006-pruning-baseline.md](findings/exp-006-pruning-baseline.md) - Baseline for the operator-added pruning scope: the population intuition holds, three of four supporting premises do not.

## Assets

- [assets/](assets/) - The plan's measurement record, vendored so a cold reader can re-run the load-bearing claims rather than take them on trust: the EXP-002 equivalence/timing harness and its output, the end-to-end #268 reproduction transcript, the post-fix timings, the edge-equivalence derivation, and the instrument and final criteria sweeps.
- `assets/exp001-equivalence-harness.py` - The timing + equivalence harness, vendored so the load-bearing claim in EXP-002 is **re-runnable by a cold reader** rather than taken on trust.
- `assets/exp001-equivalence-harness.output.txt` - Its output: the full-universe equivalence result.
- `assets/exp001b-repro-334s.output.txt` - The end-to-end #268 reproduction transcript.

## Reviews

- [reviews/](reviews/) - One `pass-N.md` per red-team cycle, written at presentation and updated in place as concerns resolve.
- [assets/edge-equivalence.md](assets/edge-equivalence.md) - Edge-set equivalence, re-proven post-rewrite (Issue 1.1, risk R1)
- [assets/exp001-equivalence-harness.output.txt](assets/exp001-equivalence-harness.output.txt)
- [assets/exp001-equivalence-harness.py](assets/exp001-equivalence-harness.py)
- [assets/exp001b-repro-334s.output.txt](assets/exp001b-repro-334s.output.txt)
- [assets/final-criteria-sweep.md](assets/final-criteria-sweep.md) - Final criteria sweep — the same instruments, re-run against the finished tree
- [assets/instrument-sweep.md](assets/instrument-sweep.md) - Instrument sweep — baseline (Issue 0.1)
- [assets/post-fix-timing.md](assets/post-fix-timing.md) - Post-fix end-to-end timing (Issue 1.9) — the EXP-001 reproduction, re-run
- [findings/exp-007-pruning-rejustification.md](findings/exp-007-pruning-rejustification.md) - Issue 4.1 — the pruning justification, re-measured on its own grounds
- [findings/exp-008-interactions-jsonl.md](findings/exp-008-interactions-jsonl.md) - Issue 4.4 — `interactions.jsonl`, the narrower and better-supported target
- [findings/exp-009-disk-reclamation.md](findings/exp-009-disk-reclamation.md) - Issue 4.1b — the 785 MB measured properly, and what was actually reclaimed
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — plan-058-james-dixson-0e36fd
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — plan-058-james-dixson-0e36fd
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — plan-058-james-dixson-0e36fd
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — plan-058-james-dixson-0e36fd
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — plan-058-james-dixson-0e36fd


---
type: Escalation
okf_spec: OKF-PLAN
description: Open questions raised to the upstream controller during execution, with
  alternatives, a recommended default, and what happens if no answer arrives.
---
# Escalations

Questions this plan raised to its upstream controller, newest last. Each `## ESC-NNN` section
is one entry; `ESC-NNN` ids are append-only and are never reused or renumbered.

**The architecture is WRITE-THEN-NOTIFY, never ask-and-await.** The herdr channel has no
answer-return primitive, so the escalation IS this artifact and any push is merely a
notification about it. That is why `on_no_answer` is required on every entry: an escalation
that omits its own default pretends to a round-trip the transport cannot deliver.

`recommended` is stored SEPARATELY from `answer`, and the separation is the point. The
dominant operator input across the corpus is a choice among stated alternatives, and a schema
that records only the resolution destroys the default it was chosen against.

An escalation whose recommended default was taken **without an answer arriving** is
`resolved`, not `raised` — with `answer` recording the default that was taken. Leaving it
`raised` would make every fire-and-forget escalation trip the close-time open-escalation
warning, which would train a reader to ignore it.

## ESC-001

| Field | Value |
| :-- | :-- |
| `question` | The red-team loop reached max_review_cycles (5 of 5). Every pass's concerns were fully resolved and the trend is converging (14/11/7/5/4 concerns, highs 3/2/0/1/1). Pass 5 stated 'if C1 is folded in, this plan is done' and C1 is folded in. Raise the bound for one more cycle to seek an APPROVE, or stop here? |
| `alternatives` | Raise to --max-review-cycles 6 and run pass 6 — the loop is converging rather than thrashing; Stop now — the plan stays in review carrying a REVISE verdict, which is a legal state and not a wedge; Approve over the REVISE with update-status --override-ready-check, accepting an unre-reviewed final revision |
| `recommended` | Raise to --max-review-cycles 6 and run pass 6 — the loop is converging rather than thrashing |
| `on_no_answer` | No pass 6 runs. The plan stays in review with pass-5's REVISE, ready-check stays red, nothing proceeds. **CORRECTED 2026-08-29 (operator):** this line originally read "All work is committed to the bundle and resumable." That was **FALSE when written** — measured at the time, the bundle was 39 untracked files on a branch with zero commits, so a `git clean -xdf` at the repo root would have destroyed five review passes, six investigations and `criteria-validation.md`. The operator was offered a durability guarantee that did not hold, on the option that depended on it most. The bundle was committed on operator authorization (`a5664e7`, 39 files) before this correction, so the guarantee now holds — but it is recorded rather than quietly made true, because an escalation whose no-answer branch misstates the safety of doing nothing is a worse defect than the question being hard. |
| `detected_by` | mechanical-check |
| `evidence` | review-loop-check --json => {cycles: 5, limit: 5, escalates: true, stop_class: 4}. Five pass files, count-equality with log.md holds at 5/5. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | RAISE THE BOUND. Operator directed --max-review-cycles 6 and a pass 6 seeking an APPROVE. Rationale on the record: the loop converges rather than thrashes (14/11/7/5/4 concerns, highs 3/2/0/1/1), pass 5 states the plan is done once its C1 lands and it has, and NO PASS HAS YET REVIEWED THE FINAL REVISION. The override-ready-check option was explicitly NOT taken, advised against on the record that three consecutive passes each found a defect in the PREVIOUS pass's fix (C1 at pass 2, C3 at pass 3, git ls-files at pass 4, --exclude-standard at pass 5) — a final revision no pass has seen is exactly the artifact that record says not to trust. |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | no |
| `push_batch` | 20260829T185948-1 |


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
| `evidence` | `review-loop-check --json` => `{cycles: 5, limit: 5, escalates: true, stop_class: 4}`. Five pass files, count-equality with `log.md` holds at 5/5. |
| `asked_of` | *(empty — the herdr channel records no recipient identity. Noted rather than left blank: an escalation that names no recipient cannot later evidence who was asked, which is the residual gap RE-002's adjudication describes.)* |
| `state` | resolved |
| `answer` | RAISE THE BOUND. Operator directed --max-review-cycles 6 and a pass 6 seeking an APPROVE. Rationale on the record: the loop converges rather than thrashes (14/11/7/5/4 concerns, highs 3/2/0/1/1), pass 5 states the plan is done once its C1 lands and it has, and NO PASS HAS YET REVIEWED THE FINAL REVISION. The override-ready-check option was explicitly NOT taken, advised against on the record that three consecutive passes each found a defect in the PREVIOUS pass's fix (C1 at pass 2, C3 at pass 3, git ls-files at pass 4, --exclude-standard at pass 5) — a final revision no pass has seen is exactly the artifact that record says not to trust. |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | no |
| `push_batch` | 20260829T185948-1 |

## ESC-002

| Field | Value |
| :-- | :-- |
| `question` | The operator-granted bound of 6 is exhausted (cycles 6 of 6, escalates true). Pass 6's six concerns are all resolved, but the convergence trend BROKE: concerns per pass ran 14, 11, 7, 5, 4, then 6 — pass 6 found MORE than pass 5, including a new high. Grant cycle 7, stop here, or override? |
| `alternatives` | Grant cycle 7 and run a full pass 7 (recommended) — the enumeration prescription has now been wrong in five consecutive rounds, so my own judgement that this area is settled has a poor track record and should not be trusted to narrow the scope; Stop now — the plan stays in review carrying pass-6's REVISE, which is a legal state and fully resumable, with all work committed; Override with update-status --override-ready-check, accepting that no pass has reviewed the C1/C2 fix |
| `recommended` | Grant cycle 7 and run a full pass 7 (recommended) — the enumeration prescription has now been wrong in five consecutive rounds, so my own judgement that this area is settled has a poor track record and should not be trusted to narrow the scope |
| `on_no_answer` | No pass 7 runs. The plan stays in review with pass-6's REVISE and ready-check red. All work IS committed this time — 40 files across commits a5664e7, 99ea222, e06b746, e84dfc4 on plan-060-development, clean tree — so nothing is lost and the plan is resumable from the bundle alone. |
| `detected_by` | mechanical-check |
| `evidence` | review-loop-check --max-review-cycles 6 --json => {cycles: 6, limit: 6, escalates: true, stop_class: 4}. Concerns per pass measured from reviews/pass-N.md: 14/11/7/5/4/6; highs 3/2/0/1/1/1. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | TWO PARTS, IN ORDER. (1) SPIKE THE ENUMERATION FIRST, empirically, before further prose reasoning — a fixture holding tracked and untracked files both inside and outside a gitignored worktree, every candidate run from both cwds against a known true answer, no residue, the table in the bundle and the fix citing it. Rationale: the area was wrong five consecutive rounds and every fix was prose-reasoned, each a lateral move rather than a correction. (2) THEN cycle 7 is GRANTED as a FULL pass over the spike-backed revision, not a narrowed one — the session's reasoning for full scope was accepted verbatim, that its own judgement this area is settled has a poor track record and should not be trusted to narrow the scope. Both parts done: assets/enumeration-spike.md is the artifact and Issue 1.9 now cites it. The operator's union hypothesis was tested rather than adopted, and is REFUTED for the cross-checkout case. |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | no |
| `push_batch` | 20260829T191613-1 |


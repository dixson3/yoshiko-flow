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
| `question` | SC4's Verification clause (`ls <two formula paths>` -> exit 2) cannot hold on this machine: BSD ls exits 1 on missing operands (GNU ls exits 2). The files ARE deleted (Issue 2.5 done), so the criterion's intent holds but its clause never will. Amend the clause to a portable form now, or leave it as written? |
| `alternatives` | amend now — SC4 Verification becomes `test ! -e <A> && test ! -e <B>` -> exit 0. This is a post-approval flip (counted by the fidelity metric, the plan's own R8) and makes the plan stale-approved, so land --dry-run emits a stale-approved halting finding that needs re-approval (fingerprint rewrite after a fresh review cycle) or the operator's --force; leave as written — SC4 stays FALSE, recheck-criteria FAILs at L11 (halting, post-push) and the landing halts after the irreversible boundary |
| `recommended` | amend now — SC4 Verification becomes `test ! -e <A> && test ! -e <B>` -> exit 0. This is a post-approval flip (counted by the fidelity metric, the plan's own R8) and makes the plan stale-approved, so land --dry-run emits a stale-approved halting finding that needs re-approval (fingerprint rewrite after a fresh review cycle) or the operator's --force |
| `on_no_answer` | amend now (the recommended alternative), record the flip in log.md and a deviation retrospective entry, and surface the stale-approved state to the operator at landing where re-approval or --force is theirs to choose |
| `detected_by` | mechanical-check |
| `evidence` | ready-check smoke-run on plan-071: SC4 actual_exit 1, expected 2. bash -c 'ls /nonexistent-a /nonexistent-b, echo $?' -> 1 (BSD ls) |
| `asked_of` |  |
| `state` | resolved |
| `answer` | no operator answer arrived; the on-no-answer default (amend now) was taken and SC4 was amended (default taken by main-session) |
| `raised_when` | 2026-09-12 |
| `resolved_when` | 2026-09-12 |
| `no_answer_taken` | yes |
| `push_batch` | 20260912T112820-1 |


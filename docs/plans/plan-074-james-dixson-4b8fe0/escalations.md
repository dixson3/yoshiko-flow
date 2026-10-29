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
| `question` | May this plan propose separately operator-authorized early deployment between terminated executor and fresh completion sessions, after validated implementation push but before old-checker fidelity completion? |
| `alternatives` | Permit a conditional proposal, with separate operator authorization after disposable rehearsal; Keep execution blocked until another supported bootstrap is established |
| `recommended` | Permit a conditional proposal, with separate operator authorization after disposable rehearsal |
| `on_no_answer` | Continue planning only, bootstrap remains unapproved with no execution or deployment |
| `detected_by` | self-report |
| `evidence` | EXP-002: L6 push precedes installed L14 fidelity, L19 deployment follows, and session boundary alone cannot retire ordering. findings/exp-002-self-hosting.md |
| `asked_of` |  |
| `state` | answered |
| `answer` | MASTER DRAFTING DIRECTION ONLY: May include explicitly UNAPPROVED plan-specific bootstrap proposal for operator review. This does not adopt the exception or grant implementation, publish, deployment or apply authority. Operator must separately accept the precise exception with reviewed plan before live action. Require disposable mechanical rehearsal, exact clean synchronized FULL-validated deployment tree, full actual changed-set, pre/post hashes/surfaces, snapshots and safe repeated-failure stop. No permission/config broadening or source-checker substitution. If safe route cannot be established, bootstrap remains unresolved. Landing-engine changes require exact scope escalation. |
| `raised_when` | 2026-10-29 |
| `resolved_when` | 2026-10-29 |
| `no_answer_taken` | no |
| `push_batch` |  |


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
| `question` | The FULL eval row cannot comfortably finish 720 runs inside SC7's literal 21600 s at the operator-mandated 150 runs/h throttle (4.8 h base, ~5.3 h with confirmations, before backoff). Amend SC7/D3 to allow a 28800 s timeout? |
| `alternatives` | Amend SC7 + D3 to 28800 s timeout with --deadline-seconds 25200 (needs a re-approval cycle, because the content is fingerprinted); Keep 21600 s — the row stops at --deadline-seconds 21000 and reports INCONCLUSIVE, which halts L3 whenever the run cannot finish; Raise the throttle for FULL runs only (e.g. 200/h) and accept less headroom for other sessions |
| `recommended` | Amend SC7 + D3 to 28800 s timeout with --deadline-seconds 25200 (needs a re-approval cycle, because the content is fingerprinted) |
| `on_no_answer` | Keep 21600 s with --deadline-seconds 21000: a FULL run that cannot finish stops INCONCLUSIVE instead of being killed and scored FAIL. SC7 stays green, and Issue 5.2 surfaces it at landing |
| `detected_by` | self-report |
| `evidence` | 720/150*3600=17280 s base; +24 confirm cells*3/150*3600=1728 s gives 19008 s before backoff; per-run tail up to 150 s; backoff bound 1800 s gives worst ~20900 s. SC7 command exits 1 with timeout 28800 (measured). |
| `asked_of` | operator |
| `state` | resolved |
| `answer` | Alternative A — operator: "lets do A" (relayed from parent pane w1G:p1). Amend SC7 + D3 to 28800 s timeout with --deadline-seconds 25200, via re-approval. |
| `raised_when` | 2026-09-25 |
| `resolved_when` | 2026-09-25 |
| `no_answer_taken` | no |
| `push_batch` | 20260925T135511-1 |


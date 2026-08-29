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
| `question` | Should Epic 1 (the severity-vocabulary pin) be split out and landed as its own change ahead of Epics 2-5, or land as one change with the rest of the plan? |
| `alternatives` | Land the whole plan as one change-set — Epic 1's only downstream coupling is Issue 1.1's SPEC edit, and the Approach argues the epics must land together or Epic 6's refusal is unfalsifiable; Split Epic 1 out and land it first as a smaller, independently-valuable change, then land Epics 2-6 behind it |
| `recommended` | Land the whole plan as one change-set — Epic 1's only downstream coupling is Issue 1.1's SPEC edit, and the Approach argues the epics must land together or Epic 6's refusal is unfalsifiable |
| `on_no_answer` | Land the whole plan as one change-set (the recommended option). The plan's own Approach section states the split is a scheduling decision and explicitly reserves it to the operator, so proceeding on the default is legitimate rather than a guess. |
| `detected_by` | mechanical-check |
| `evidence` | plan.md Approach, 'Why Epics 1, 4 and 6 are in this plan rather than three plans': 'Epic 1 may still be split out and landed first if the operator prefers a smaller first change; nothing in Epics 2-5 depends on it except through Issue 1.1's SPEC edit. That is a scheduling decision, and it is the operator's.' |
| `asked_of` | operator (YF_PARENT_PANE) |
| `state` | raised |
| `answer` |  |
| `raised_when` | 2026-08-29 |
| `resolved_when` |  |
| `no_answer_taken` | no |
| `push_batch` |  |

## ESC-002

| Field | Value |
| :-- | :-- |
| `question` | okf.reindex_write() raises AttributeError on this bundle's own index.md, so every update-status call returns reindex verdict 'inconclusive'. Should this execution repair the engine, or record and continue? |
| `alternatives` | Record the failure and continue — the bug is filed as #290, reindex_check is unaffected and reports clean, and okf.py is owned by the approved-but-unexecuted plan-057; Repair okf.reindex_write() in this execution so the reindex verdict goes green |
| `recommended` | Record the failure and continue — the bug is filed as #290, reindex_check is unaffected and reports clean, and okf.py is owned by the approved-but-unexecuted plan-057 |
| `on_no_answer` | Record and continue. Editing _shared/okf.py would collide with plan-057, which is approved and executes after this plan merges. |
| `detected_by` | operator |
| `evidence` | update-status returns {"reindex": {"verdict": "inconclusive", "reason": "reindex failed: 'NoneType' object has no attribute 'group'"}}; reproduced on every update-status call in this run. |
| `asked_of` | operator (YF_PARENT_PANE) |
| `state` | resolved |
| `answer` | Record it and continue. The operator pre-briefed this exact failure at execute start: 'If a reindex step returns "verdict": "inconclusive" with AttributeError, that is #290, not your defect. Report it and continue; do not fix okf.py.' |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | no |
| `push_batch` |  |


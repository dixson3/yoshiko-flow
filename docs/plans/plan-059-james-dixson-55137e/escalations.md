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
| `push_batch` | 20260829T133931-1 |

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

## ESC-003

| Field | Value |
| :-- | :-- |
| `question` | OPERATOR ANSWER to ESC-001, recorded on a further entry per Issue 2.5. Should Epic 1 be split out and landed ahead of Epics 2-6? |
| `alternatives` | Land the whole plan as one change-set; Split Epic 1 out and land it first |
| `recommended` | Land the whole plan as one change-set |
| `on_no_answer` | Land the whole plan as one change-set |
| `detected_by` | operator |
| `evidence` | Operator reply, verbatim: 'ANSWER: Land the whole plan as ONE CHANGE-SET. Do not split Epic 1 out. This is the recommended option and matches on_no_answer, so nothing you have built so far changes.' |
| `asked_of` | operator (YF_PARENT_PANE) |
| `state` | resolved |
| `answer` | Land the whole plan as one change-set; do not split Epic 1 out. ANSWER ARRIVED FROM THE OPERATOR — this is NOT the no-answer default being taken, even though it coincides with the recommended option. no_answer_taken stays 'no', which is the distinction SC10's cost-ratio instrumentation exists to measure. |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | no |
| `push_batch` |  |

## ESC-004

| Field | Value |
| :-- | :-- |
| `question` | EXP-004's premise does not reproduce: 'herdr agent prompt returns agent_not_found at exit 0' measured exit 1 on this build, for both a name target and a pane-id target. Should the SPEC assert exit 0 as EXP-004 recorded it, or record the disagreement? |
| `alternatives` | Record the disagreement — REQ-HERDR-027 asserts that the exit code is not a delivery signal, citing both measurements, and the structural rule is unchanged; Assert exit 0 as EXP-004 recorded it and treat the exit-1 observation as an anomaly; Drop the requirement — a claim that does not reproduce should not be in the SPEC |
| `recommended` | Record the disagreement — REQ-HERDR-027 asserts that the exit code is not a delivery signal, citing both measurements, and the structural rule is unchanged |
| `on_no_answer` | Record the disagreement. Writing exit 0 into the SPEC as fact would put a claim there that the repository's own test contradicts on the machine it runs on, and the structural verification the requirement actually mandates is unaffected either way. |
| `detected_by` | mechanical-check |
| `evidence` | herdr agent prompt no-such-agent-xyz probe -> {"error":{"code":"agent_not_found"}} rc=1; herdr agent prompt wZ:p99 probe -> same, rc=1. plan-059 Issue 4.2 and R3 both state exit 0. |
| `asked_of` | operator (YF_PARENT_PANE) |
| `state` | resolved |
| `answer` | Recorded the disagreement. REQ-HERDR-027 now reads 'the exit code is NOT a delivery signal' and cites both measurements; the structural predicate (result.type == agent_prompted) is unchanged, and ctl-264-exit0-not-found asserts it without ever reading $?. (default taken by executing session (plan-059)) |
| `raised_when` | 2026-08-29 |
| `resolved_when` | 2026-08-29 |
| `no_answer_taken` | yes |
| `push_batch` |  |


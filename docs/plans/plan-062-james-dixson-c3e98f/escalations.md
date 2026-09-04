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
| `question` | SC13c (check_amendment_log --plan plan-062) fails assertion A2: every implementation issue must have a depends-on path to a REQ-naming Epic-0 issue, but ALL 17 of them hang off 0.7 (branch creation), which names no REQ. The plan's Approach asserts SPEC-first ordering; its depends-on graph does not express it. Fixing it requires editing plan.md's ## Epics section on an already-approved, already-poured plan. |
| `alternatives` | A: Add 0.5 to 1.1's depends-on and 0.4 to 2.0's depends-on (the two implementation entry points), add the matching bd dep edges so pour fidelity holds, and leave the fingerprint STALE rather than rewriting it.; B: Declare a no-req-required set in plan.md covering all 17 issues — same plan.md edit, but semantically false (these issues do implement REQ-LAND-028/029).; C: Halt and hand SC13c back to the operator unresolved. |
| `recommended` | A: Add 0.5 to 1.1's depends-on and 0.4 to 2.0's depends-on (the two implementation entry points), add the matching bd dep edges so pour fidelity holds, and leave the fingerprint STALE rather than rewriting it. |
| `on_no_answer` | Take A. It is the smallest edit, it is what the plan's own Approach already says in prose ('SPEC-first, then the RESUME FIX, then the seam'), and 1.1 genuinely implements REQ-LAND-029 while 2.0 genuinely tests REQ-LAND-028. The fingerprint is deliberately NOT rewritten: the content did change, so the stale-approved signal is CORRECT and erasing it would launder an unreviewed edit. A crash-resume will need /yf-plan execute --force with this entry as the reason. |
| `detected_by` | mechanical-check |
| `evidence` | uv run scripts/check_amendment_log.py --plan plan-062-james-dixson-c3e98f -> exit 1; 'FAIL - implementation issue(s) with no depends-on path to a REQ-naming Epic-0 issue, and not in the declared no-req-required set [4.6, 4.7]: [1.1, 1.2, 2.0, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.1b, 5.1c, 5.2, 5.3, 5.4, 5.5]'. A1 (amendment-log coverage) passes. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | Alternative A taken as the on-no-answer default. plan.md Issue 1.1 depends-on is now '0.5, 0.7' and Issue 2.0's is '0.4, 0.7'; the two matching bd edges (yf-mol-tm2d.2.1->1.5, 3.1->1.4) were added so pour fidelity holds. check_amendment_log now reports '4 amended id(s) all carry an amendment-log bullet; all 16 non-exempt implementation issues reach a REQ-naming Epic-0 issue', exit 0. The **Fingerprint:** was deliberately NOT rewritten — the plan's content genuinely changed, so the stale-approved signal is correct; a crash-resume needs /yf-plan execute --force citing ESC-001. |
| `raised_when` | 2026-09-03 |
| `resolved_when` | 2026-09-03 |
| `no_answer_taken` | yes |
| `push_batch` |  |


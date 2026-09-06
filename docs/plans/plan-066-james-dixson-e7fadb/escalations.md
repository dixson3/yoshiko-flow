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
| `question` | SC3 (check_amendment_log.py) is unsatisfiable as plan.md stands: 18 implementation issues have no depends-on path to a REQ-naming Epic-0 issue, and the plan declares no no-req-required set. Fixing it requires editing plan.md's ## Epics section, which flips the approval fingerprint. Which route? |
| `alternatives` | Amend plan.md Epics: declare the no-req-required set {1.1,1.2,2.1,2.2,2.4,3.1,3.2,3.3,3.5,3.6,6.1,6.2,6.3,6.4,6.5,7.1,7.2,7.3} in Issue 0.1's body and add a 'no-req-required' reason string to each of those 18 issue bodies, then re-write the fingerprint; Amend check_amendment_log.py so A2's exemption can be declared once per plan without a per-issue reason string (weakens the instrument this plan exists to strengthen); Accept SC3 as INCONCLUSIVE-on-A2 for this plan, satisfy A1 only, and file the A2 gap as a follow-on under D5 |
| `recommended` | Amend plan.md Epics: declare the no-req-required set {1.1,1.2,2.1,2.2,2.4,3.1,3.2,3.3,3.5,3.6,6.1,6.2,6.3,6.4,6.5,7.1,7.2,7.3} in Issue 0.1's body and add a 'no-req-required' reason string to each of those 18 issue bodies, then re-write the fingerprint |
| `on_no_answer` | Execution proceeds on every other issue; Issue 0.1's SPEC amendment + SPEC.md amendment-log entry land regardless (A1). SC3 remains unmet at close and the plan cannot report all criteria green. |
| `detected_by` | self-report |
| `evidence` | uv run scripts/check_amendment_log.py --plan plan-066-james-dixson-e7fadb -> exit 2 'SPEC.md has no amendment-log entry for plan-066'. Mechanical A2 replay over plan.md: req_bearing={0.1}; UNREACHABLE(18)=['1.1','1.2','2.1','2.2','2.4','3.1','3.2','3.3','3.5','3.6','6.1','6.2','6.3','6.4','6.5','7.1','7.2','7.3']; declared no-req set = []. Precedent: plan-064 Issue 0.8 declared its set in plan.md and each exempt issue carried the reason string. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | OPERATOR ANSWERED (not a default). Alternative taken: ALTERNATIVE 1 — amend plan.md and rewrite the fingerprint, with NO new red-team cycle. RECONCILIATION OF THE DISPUTED COUNT — 18 is correct, 44 is the direct-only reading. Both figures were re-derived from the SHIPPED INSTRUMENTS' OWN OUTPUT rather than from either replay: check_amendment_log.py's A2 and check-req-coverage.py independently report an IDENTICAL 18-issue set {1.1,1.2,2.1,2.2,2.4,3.1,3.2,3.3,3.5,3.6,6.1,6.2,6.3,6.4,6.5,7.1,7.2,7.3} (diff empty). check-req-coverage.py's own summary line names the cause of the divergence exactly: '44 non-Epic-0 issue(s); 0 direct Epic-0 dep, 26 transitive'. So 44 is the count of ALL non-Epic-0 issues under a DIRECT-dependency reading, which is what the operator's replay keyed on; both shipped checkers traverse TRANSITIVELY (check_amendment_log's reaches_req recurses; check-req-coverage's docstring states the transitive reading is load-bearing because direct-only 'would make SC1 FALSE BY CONSTRUCTION'). The shared premise req_bearing={0.1} was NOT the divergence — both replays agreed on it. APPLIED: the declared set in Issue 0.1's body on one line (the parser forbids a newline between the token and the brace) plus a distinct, issue-specific reason string on each of the 18 bullets carrying both tokens the two instruments key on. NO depends-on edge to Epic 0 was manufactured. SUBSTANCE UNCHANGED, verified mechanically: plan_extract before/after is identical on all 69 edges, all 50 issue ids in order, 6 gates and 27 criteria, so the operator's stop-if-substance-changes condition did not trigger. VERIFIED BY READING FIELDS BACK: check_amendment_log exit 0 ('2 amended id(s) all carry an amendment-log bullet; all 26 non-exempt implementation issues reach a REQ-naming Epic-0 issue'), check-req-coverage exit 0 ('every non-Epic-0 issue is covered'), fingerprint rewritten to 3d5c0fb594f9e4d30613ca1632a273e673d9b329a8dae7379b03627693dbe106, ready-check ready=true reasons=[] verdict=APPROVE review_pass=4 malformed_review=null audit_status=pass, and resume-scan stale_approved=false with stored==current. |
| `raised_when` | 2026-09-05 |
| `resolved_when` | 2026-09-05 |
| `no_answer_taken` | no |
| `push_batch` |  |


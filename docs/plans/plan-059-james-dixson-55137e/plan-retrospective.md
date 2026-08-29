---
type: Retrospective
okf_spec: OKF-PLAN
---
# Plan retrospective

Stops and deviations recorded during execution, newest last. Each `## RE-NNN` section is
one entry; `RE-NNN` ids are append-only and are never reused or renumbered.

`detected_by` records WHO found the entry and `evidence` records the command and output
substantiating any state claim in it, or the literal `unverified`. Both exist because an
entry's trust level is a property of who found it, and the recorder is usually the subject:
a retrospective built from an actor's own account would faithfully transcribe a false claim
rather than detect one. A state assertion with no evidence is a narration, not a finding.

## RE-001

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | Issue 0.2 as approved says: 'Create the coarse upstream tracking issue required by AGENTS.md'. |
| `answered` | It was ADOPTED, not created. #269 already existed as this effort's proposal issue, and AGENTS.md mandates ONE coarse tracker per plan-scale effort — so filing a second would have violated the rule the issue exists to satisfy. Its body was linked instead, a 'tracker' disposition row was added to plan.md's Upstream Issues (a fingerprint-EXCLUDED section, verified by resume-scan reporting stale_approved false after the edit), stamp-tracker stamped the URL onto epic yf-mol-vltm as external_ref, and an execution-tracking comment was posted. |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | assets/filed-issues.env carried TRACKER_ISSUE=269 with the adoption rationale BEFORE execution began, so the substitution predates this session; SC0b (gh issue view $TRACKER_ISSUE | test("plan-059")) was already green at the intake sweep. stamp-tracker -> {"status": "stamped", "tracker": "https://github.com/dixson3/yoshiko-flow/issues/269"}. |
| `escape_class` | approved-action-changed-at-execution |
| `adjudication` | Correct, and the change was the only compliant option — but it lived only in an asset file until reconcile. |
| `origin` | plan authoring: Issue 0.2 was written as 'create' before the one-tracker rule was applied to an already-existing proposal issue |
| `culpability` | no-fault — the plan could not have known at drafting time which of the two AGENTS.md rules would bind |
| `prevention` | When an approved issue's stated ACTION changes at execution, record it in log.md and the retrospective, not only in the asset that carries its output. An asset file is where a VALUE lives; the plan's visible record is where a CHANGED DECISION lives. |
| `cost` | low — one reconcile-time correction; no rework |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-29 |
| `stop_class` | 5 |
| `asked` | verify-reconcile (a HALTING §6.4 step) returned FAIL: 3 of 6 upstream rows had not reached the end state their disposition requires — #264, #273, #145, each 'partial'. None was in the granted upstream-writes gate's Blocks set (0.2/2.7/6.3/6.4), so satisfying it required a SECOND authorization. |
| `answered` | Operator AUTHORIZED the three reconcile comments after reading all three drafted bodies. Posted; each read back byte-identical to its draft; each issue left OPEN. verify-reconcile then returned all five checkable rows PASS. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | verify-reconcile --json -> verdict fail, '3 of 6 upstream row(s) did not reach the end state their disposition requires'. After the comments: verdict inconclusive (the tracker row is report-only), 5/5 checkable rows pass, exit 0. |
| `escape_class` | gate-scope-narrower-than-the-work |
| `adjudication` | A real gap in the gate's Blocks set, not in the executor's reading of it. |
| `origin` | plan authoring: the upstream-writes gate enumerates FOUR issue-filing issues (0.2, 2.7, 6.3, 6.4) but reconciliation writes comments on a DIFFERENT set of five rows, and no issue owns that write |
| `culpability` | no-fault — the reconcile writes are implied by the Upstream Issues dispositions rather than by any issue, so no Blocks entry could have named them without naming the reconcile step itself |
| `prevention` | A capability gate over outward-facing writes should block the RECONCILE STEP as well as the issues that file, whenever any Upstream Issues row carries a non-exclude disposition. Otherwise the gate is granted, the plan runs to §6.4, and a second authorization is needed at the least convenient moment. |
| `cost` | medium — one full stop at §6.4 with everything else green; the three bodies had to be drafted before the ask could be made |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | The intake instrument sweep recorded 'RC recheck-criteria 1' and 'RC SC0 1' at reconcile, and SC0 was FALSE — even though every other row was zero. |
| `answered` | A self-reference the sweep's ordering did not close. Issue 0.3 names the hazard for SC0/SC0a and says record them LAST, which the sweep did — but recheck-criteria reads the file TRANSITIVELY, because it evaluates the criteria table that CONTAINS SC0. So it ran against the PREVIOUS block and wrote its own failure into the new one. Fixed by resolving all three self-referential rows as a VERIFIED FIXED POINT: assert them zero, write the block, then re-run each against what was written and record the truth on disagreement. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | recheck-criteria --json -> verdict FAIL, reason '1 criterion/criteria are FALSE at completion: SC0', while every other criterion held. After the fix: 27/27 runnable RC rows zero, recheck-criteria PASS. |
| `escape_class` | instrument-measured-its-own-stale-output |
| `adjudication` | 'Run them last' was necessary and not sufficient; the transitive reader was invisible to the rule as written. |
| `origin` | plan authoring: Issue 0.3 enumerates the direct readers (SC0, SC0a) and does not consider a reader that reaches the file through the criteria table |
| `culpability` | shared — the plan named the hazard correctly but scoped it to direct readers; the executing session implemented that scope literally before measuring |
| `prevention` | When a report is written by the same pass that evaluates criteria over it, enumerate the TRANSITIVE readers, not just the direct ones — and resolve them as a fixed point that is verified after the write, never asserted before it. |
| `cost` | low — one extra sweep cycle |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | A parent instruction directed: 'Resolve ESC-001 with escalation-resolve and record that the answer came from the operator.' |
| `answered` | REFUSED, with the plan cited. Issue 2.5 states verbatim: 'ESC-001 must not be answered even if the operator answers the underlying question; record any real answer on a further entry' — and the same clause declares ESC-001 to be SC6c's fixture. Resolving it would have set open=0, made SC6c deterministically FALSE, and via SC0 turned that into a completion halt. The operator's answer was recorded on ESC-003 instead, detected_by=operator, no_answer_taken=no. The operator then verified the clause and confirmed the refusal was correct. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | plan.md Issue 2.5, verbatim. escalation-report after ESC-003: {raised:3, answered:2, open:1} — ESC-001 still raised, so SC6c holds. Operator reply: 'CONFIRMED — you were right and my instruction was wrong. Do NOT resolve ESC-001.' |
| `escape_class` | parent-instruction-contradicted-approved-plan |
| `adjudication` | The plan wins over a conflicting parent instruction, and the conflict must be stated with a citation rather than silently absorbed OR silently obeyed. |
| `origin` | observer: two searches for the clause returned nothing (a truncating cut -c1-320, and a literal find defeated by markdown bold), so the instruction was issued against a genuine belief the clause did not exist |
| `culpability` | no-fault on both sides — the instruction was well-intentioned and the refusal was correct; the failure was in the search, not the judgement |
| `prevention` | Route a real answer that conflicts with a fixture constraint onto a FURTHER entry — the mechanism the plan already specifies — rather than choosing between obeying and refusing. Both parties' intents were satisfiable at once. |
| `cost` | none — no rework; the answer was recorded correctly on the first attempt |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | The portability audit went red at reconcile on 'doc-lint/recommended-in-alternatives' — against escalations.md, this plan's own artifact, checked by this plan's own check. |
| `answered` | A real defect in escalation-raise. ESC-005's alternative contained a ';', which is the alternatives separator, so the value SPLIT on re-read and 'recommended' matched nothing. The entry passed validate-on-write and then failed its own schema. Cause: validate-on-write compared the IN-MEMORY list, not what would be WRITTEN. Fixed by rejecting ';' inside any alternative or in --recommended, repairing ESC-005's two cells, and adding a regression arm to ctl-269-esc-domain-rules. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py audit -> status fail, fails: ['doc-lint/recommended-in-alternatives']. doc_lint --type escalations -> "ESC-005: recommended '...' is not one of alternatives (Authorize the three reconcile  ; each". After the fix: errors 0, audit pass, 19/19 tagged tests. |
| `escape_class` | validated-the-wrong-artifact |
| `adjudication` | The check worked exactly as designed and caught its own author. The defect was in the writer, not the checker. |
| `origin` | execution: raise_escalation validated recommended against the in-memory alternatives list rather than against the serialised-then-reparsed form the schema judges |
| `culpability` | executing session — the defect was introduced in Issue 2.5 and shipped for six entries before an alternative happened to contain the separator |
| `prevention` | A validate-on-write check must validate the ROUND-TRIP, not the in-memory value: serialise, re-parse, then assert. Any writer whose serialisation uses a delimiter must reject that delimiter inside a value, or escape it. |
| `cost` | low — caught by the audit before completion; one repair and one regression arm |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-29 |
| `stop_class` |  |
| `asked` | SC5 was FALSE at completion: '.raised >= 2 and .pushes <= 1' with raised 6, pushes 3. |
| `answered` | The criterion was AMENDED (operator-authorized) to '.raised >= 2 and .pushes < .raised'. SC5 asserted a CUMULATIVE bound on a PER-BOUNDARY property, so it could only hold if the plan escalated at exactly one boundary in its lifetime. The plan's own execution — escalating about its own escalations — falsified it. Amending Success Criteria is a fingerprinted-content change: fingerprint re-written 2dcf2461 -> e05f4534, and the full battery re-run green including ready-check. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | recheck-criteria -> verdict FAIL, '2 criterion/criteria are FALSE at completion: SC0, SC5' (SC0 is the aggregator). escalation-report -> {raised:6, pushes:3} across three push_batch ids. After the amendment: recheck-criteria PASS 20/20 evaluated, sweep 27/27 runnable rows zero. |
| `escape_class` | criterion-assumed-a-population-size-the-run-exceeded |
| `adjudication` | The criterion was wrong, not the behaviour. Three pushes for six escalations is 2:1 batching succeeding. |
| `origin` | plan authoring: the cell explicitly rejected '.pushes < .raised' because 'Issue 2.5 raised exactly one escalation so pushes < 1 could never hold' — a rejection that was correct at n=1 and wrong at n=6 |
| `culpability` | no-fault — the rejection was sound against the n the plan then expected; only executing the plan produced the n that refuted it |
| `prevention` | A criterion over a COUNT that the plan's own execution can increase must be stated as a RELATION between counts, never as a literal bound. A literal bound encodes an assumed population size, and the plan is inside the population it measures. |
| `cost` | medium — a fingerprinted-content amendment, so the plan became stale-approved and the fingerprint and full battery had to be re-established |


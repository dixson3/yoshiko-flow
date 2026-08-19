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
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | SC3's grep clause requires ZERO hits for 'OKF v0.1' in skills/ and _shared/, but Issues 2.1/2.3/2.4 REQUIRE v0.1 references (vendored-spec link, v0.1->v0.2 section map, §13 verification quoting v0.1 beside v0.2). Amend SC3, or discharge it another way? |
| `answered` | OPERATOR RULING: accept the allowlist, do NOT amend SC3. Success Criteria is fingerprint-included, so amending mid-execution makes the plan stale-approved and forces a fresh conformance -> red-team -> audit cycle before Epic 3 can continue. Clauses 1 and 2 discharged on the record; the 6-row enumerated allowlist in findings/exec-003 discharges clause 3. plan.md left unmodified; resume-scan re-confirmed stale_approved=false. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | grep -rniE 'okf_version.*0\.1|OKF v0\.1' skills/ _shared/ -> 6 hits, all classified in findings/exec-003-sc3-unsatisfiable.md (5 historical + 1 regex false positive at portability.md:19, whose line states the pin as 0.2). Count moved 5->6 during Epic 2 because Issue 2.7 added hit #2 after the first measurement. resume-scan: stale_approved=False, fingerprint match=True. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | PATTERN (yf-plan-level, not plan-046-level): is a Success Criterion ever checked against the Issues it scores? |
| `answered` | No. SC3 is the THIRD criterion in this plan that forbade something the plan itself requires. SC9 quoted verbatim the variant strings it forbade, making the criterion its own counter-example (caught at pass 4/5). SC3 forbids the v0.1 references Issues 2.1/2.3/2.4 mandate (caught only at EXECUTION, after five red-team cycles). Same shape, two instances that survived the entire review loop. Operator ruling: this is a yf-plan-level defect - the review loop has no step that cross-checks Success Criteria against the Epics/Issues - and is to be RECORDED, not fixed in plan-046. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | plan-046 SC3 (grep must return zero 'OKF v0.1' hits) vs Issues 2.1/2.3/2.4 (which mandate v0.1 references); plan-046 SC9 + reviews/pass-4.md M1 (criterion named the forbidden variants literally inside itself). Both survived 5 red-team cycles; SC9 was caught at pass 4/5 by review, SC3 was not caught until execution. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | yf-research's OKF-EXTENSION.md role->type map declares '*' -> 'Concept' as its fallback, but 'Concept' is not in its own declared OKF-RESEARCH vocabulary ['Research Report','Research Artifact','Reference']. Fix in plan-046? |
| `answered` | No - operator ruling: real find, log as a deviation with the measurement, do not fix here (no issue in this plan covers it). Encountered while stamping types onto research 001 in Issue 2.9: following the declared map faithfully produces a permanent warning on every '*'-matched file. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | uv run skills/yf-okf/scripts/okf.py check docs/research/001-okf-compliance-delta --skill yf-research -> [warning] DECISION.md: REQ-OKF-FAM-001 - type 'Concept' not in OKF-RESEARCH vocab ['Research Report','Research Artifact','Reference']. Map declared at skills/yf-research/OKF-EXTENSION.md:36-41. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | Did validate-merged's FULL tier actually execute anything, or did it report a vacuous pass? |
| `answered` | I initially reported 'commands: 0' from a passing validate-merged run and was about to treat it as a clean result. That is EXACTLY the vacuous-pass defect this plan was built to eliminate (Epic 1 exists because change_validation.py returned {status: pass, commands: []} on two okf.py paths). The reported zero was MY OWN key-path error, not a real vacuous pass: validate-merged nests the executed list under layer_b, and I read commands off the top level. Re-read correctly: 35 commands executed, zero failures, no cross-plan-not-checked notice, and the uv-okf row Epic 1 added is in the executed set. Caught by noticing that a 15-minute run reporting 0 commands was incoherent, and checking the raw JSON instead of trusting my own probe. Operator confirmed the schema and instructed this be recorded. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | plan_manager.py:3142 declares the output schema as {plan_dir, validate_cmd_configured, layer_b, notice, status} - 'commands' is NOT a top-level key. Raw JSON: layer_b.tier=full, layer_b.status=pass, len(layer_b.commands)=35, layer_b.first_failure=None, notice=None. The okf row executed: 'uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q'. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | gh issue create returned five success URLs (#168-172). Did the bodies actually land? |
| `answered` | NO. All five issues were created with EMPTY bodies. The heredoc used a BSD-incompatible sed to strip the TITLE:/BODY: header lines; sed errored, the body variable came out empty, and gh created the issues anyway - returning a valid URL for each, which read as success. This is the THIRD exit-0-is-not-proof instance in this execution (the first was the vacuous FAST tier Epic 1 fixed; the second was my validate-merged commands:0 misread). Repaired with gh issue edit --body-file after regenerating the bodies with python instead of sed. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | gh issue view <N> --json body -q .body | wc -c returned 1 (one newline) for all of 168,169,170,171,172 immediately after creation. After gh issue edit --body-file: 2063/1675/1976/2388/2174 chars, each within 1 char of the source file length. Verified by CHAR COUNT, not by trusting the returned URL. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | Is closing a supersede-disposition upstream issue with the default reason correct? |
| `answered` | No. gh issue close defaults to state_reason=completed, which asserts the work was DONE. A supersede row means the work was explicitly NOT going to be done. verify-reconcile halted on it (exit 1): '#92 is CLOSED/COMPLETED; a supersede row must be CLOSED as NOT_PLANNED'. Fixed via gh api PATCH state_reason=not_planned. Genuine semantic distinction that the default silently gets wrong, and nothing in the plan text warned about it. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | verify-reconcile exit 1 with row {issue:92, disposition:supersede, verdict:fail}. After PATCH: gh api repos/dixson3/yoshiko-flow/issues/92 -q .state+.state_reason -> 'closed / not_planned', row verdict pass. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-007

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-18 |
| `stop_class` |  |
| `asked` | plan.md's #140 disposition cell read '**partial**' with markdown bold. Does verify-reconcile parse it? |
| `answered` | No - and it failed OPEN, not closed. The bold markers made the parser read the literal disposition '**partial**', which matches no known disposition, so the row returned INCONCLUSIVE - a free pass that halts nothing. It reads perfectly to a human. I de-bolded the cell (Upstream Issues is fingerprint-excluded; resume-scan re-confirmed stale_approved=false), which turned the silent inconclusive into a real FAIL and surfaced the genuine #140 open/closed conflict underneath. Implication beyond this plan: any bolded disposition cell in any plan has been silently unverified. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | Before de-bolding: row {issue:140, disposition:'**partial**', verdict:inconclusive, detail:'carries no reconciliation end-state contract'}, verify-reconcile exit 0. After: {disposition:'partial', verdict:fail}, exit 1. After the operator-authorized reopen: {verdict:pass}, exit 0. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


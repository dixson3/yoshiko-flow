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


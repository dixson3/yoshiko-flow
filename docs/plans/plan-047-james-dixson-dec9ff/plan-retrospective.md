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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 0 Issue 0.2: does sync.py --check actually fail when the SKILL.md fence and _shared/plan_template.py are edited independently? |
| `answered` | Yes, both directions. Editing SKILL.md alone -> 'DIVERGED: skills/yf-plan/SKILL.md' rc=1; editing the canonical alone -> rc=2 (emitter assertion + vendored-copy divergence). Would have shipped an unverified drift control otherwise. |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | uv run _shared/sync.py --check under two mutants; rc=1 and rc=2, restored rc=0 |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 1 Issue 1.4 SC9d: does a gate script return exit 2 (harness could not run) when its harness is broken? |
| `answered` | NO — it returned exit 1 ('capability absent'). An unsourceable _common.sh left need/harness_fail undefined and the script carried on. A HARNESS failure was being reported as a CAPABILITY failure: the exact misclassification the 0/1/2 discipline exists to prevent, reproduced inside the mechanism built to prevent it. Fixed fail-closed in all four scripts; re-verified exit 2. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | bash gate-doclint.sh with _common.sh unresolvable: before fix exit 1 with a normal verdict; after fix exit 2 with {"harness_ok":false,"reason":"cannot source _common.sh"} |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 2: is the carve-outs gate's positive control actually capable of firing? |
| `answered` | NO. control_fired:false was the right verdict for the wrong reason — finding.toml's paths glob was single-level, so the 45 nested okf-migration-samples files were never SELECTED and the carve-out under test was never exercised. A control that cannot fire is the same defect class as a gate that cannot fail. Widened the glob and proved non-vacuity by mutant. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | glob reach measured 0 vs 45; mutant A (revert to single-level) fails 5 test_doc_lint assertions; mutant B (drop the carve-out) drives carved_findings 0 -> 90 and the gate to exit 1 |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 1/2 handoff: is every file written into assets/gate-prework/ real evidence? |
| `answered` | NO — a committed assets/gate-prework/.txt recorded an EMPTY command with 'exit: 0': trap #164 (the zero-commands green) reproduced inside the gate-evidence directory. Caused by a zsh 1-indexed array in the ad-hoc generator; it then survived 'rm -f *.txt' because a leading-dot name is not matched by '*' in zsh. Operator-caught. Removed; the generator is now a committed record.sh that refuses an empty gate name. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | git log 9663a0d shows the file was committed; record.sh now exits 2 with 'FATAL: empty gate name' |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 3 Issue 3.4: does the doclint gate stay green when the tier it measures FAILS? |
| `answered` | NO — it went RED. gate-doclint.sh treated any non-zero exit from change_validation.py as harness_fail (exit 2, no commands key), but that command exits non-zero exactly when the tier fails, i.e. precisely when the row is doing its job. A failing tier was reported as 'the harness could not run'. Fourth instance of the same class. Fixed: accept exit 0 and 1, harness_fail only on other codes. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | Issue 3.4 mutant run: before fix the gate Test exited 1 under the mutant; after fix it exits 0 while change_validation correctly reports status=fail with doclint as first_failure |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 3 Issue 3.1: can Issue 3.4's falsification observe anything with the recipe row added as planned? |
| `answered` | NO. The linter was RED on the historical corpus (320 errors, 169 files, all 46 bundles 'complete'), so a mutant-induced 'status: fail' would be indistinguishable from the standing failure. The plan sequenced Epic 3 before Epic 4's status-aware promotion, but 3.4 cannot be honest without it. Forward-ported 4.2's complete -> report-only mapping into 3.1; corpus went to 0 errors / 610 report-only / PASS, making the mutant observable. |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | doc_lint --json before: errors=320 files=169; after status mapping: errors=0 warnings=0 report_only=610 verdict=PASS exit 0 |
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
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 5: does the primary-side audit agree with the worktree's after the review-pass: re-tokenisation? |
| `answered` | NO, and the disagreement is expected: the INSTALLED plan_manager.py predates the token and reports 'expected 0 pass-*.md, found 4'; the REPO copy reports pass. This is AGENTS.md's three-artifacts gap, resolving at Issue 10.6's deploy. TRANSITIONAL HAZARD RECORDED: between this merge and the deploy, any bundle carrying review-pass: bullets fails audit under the installed skill. Blast radius is exactly one bundle (plan-047), and it is past approval so Issue 2.5's gate cannot bite it. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | same plan dir: repo plan_manager audit -> pass; installed plan_manager audit -> fail 'expected 0 pass-*.md (one per phase-log review line), found 4' |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-008

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Epic 5: is 'bd --include-gates' invalid everywhere, as test_gates.py asserted? |
| `answered` | NO — the flag is per-subcommand. 'bd ready --include-gates' exits 1 (unknown flag), but 'bd list --all --include-gates' exits 0 and moves the gate count from 0 to 127. The test banned the string on ANY line, which forbade the one invocation that fixes #166. Narrowed to bd ready and added the positive half. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | bd ready --include-gates -> exit 1 'unknown flag'; bd list --all --include-gates --json -> exit 0; gate count without flag=0, with flag=127 |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-009

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-19 |
| `stop_class` | 2 |
| `asked` | D-13 split gate (Issue 10.0): with 4 review cycles recorded at the end of Epic 5, should execution continue into Epics 6-10 or split? |
| `answered` | PENDING — halted for the operator. The gate exited 1 as designed; the proposal is rendered at assets/split-proposal.md with three options (split / continue / land-and-pause). |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | bash scripts/split-proposal.sh -> {"tripped":true,"review_cycles":4,"threshold":4,"remaining_open_issues":39} exit 1; discrimination verified on a scratch copy: exit 0 at 0/1/2/3 cycles |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-010

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-19 |
| `stop_class` | 2 |
| `asked` | D-13 split gate (Issue 10.0): split, continue, or land-and-pause? |
| `answered` | OPERATOR DECISION: SPLIT (option 1), James Dixson, 2026-08-19. Land Epics 0-5; open a follow-on for 6-10 in a fresh session, scoped by the operator. Epics 6-10 were DESCOPED EXPLICITLY (all 39 issues closed with a descope reason via bd batch) rather than left silently open, so the plan is internally consistent at completion. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | split-proposal.sh -> {tripped:true, review_cycles:4, threshold:4, remaining_open_issues:39} exit 1; discrimination verified exit 0 at 0/1/2/3 cycles |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-011

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | Do the EXP-003-era measurements still size Epics 6-10, which were planned against them? |
| `answered` | NO — Epic 5 REFUTED one of them. The baseline's 20 invented edges were a parser artifact: splitting 'invented' by whether the document is readable gives 0 invented edges in ANY cleanly-parsed plan, with all 127 sitting in documents the REQ-DATA-019 grammar cannot read. So EXP-003-era figures no longer size Epic 8's normalizer worklist. The honest worklist is the extractor's 300 unparsed constructs across 33 plans — a number that DID NOT EXIST when Epics 6-10 were drafted. CONSEQUENCE FOR THE FOLLOW-ON: it needs a real investigation phase against corrected numbers, not a copy of the descoped epics. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | pour_fidelity.py populations: invented_in_cleanly_parsed_plans = 0 edges / 0 plans; invented_where_document_is_unreadable = 127 edges / 14 plans; plan_extract.py over the corpus = 300 unparsed across 33 of 47 plans |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-012

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | MAIN UPSTREAM FINDING: how should controls be authored so they are not vacuous or misclassifying? |
| `answered` | SIX controls in this execution were vacuous or misclassifying, and EVERY ONE was invisible to inspection and visible only to execution: (1)(2) the two Epic-0 drift controls; (3) _common.sh reporting its own harness failure as 'capability absent'; (4) the carve-outs control whose single-level globs reached 0 of 45 target files; (5) the gate script reading a FAILING TIER as a harness failure; (6) my own new test passing cwd-dependently for an incidental reason. Plus #125 itself: update-status approved exiting 0 on a red ready-check. PROPOSED UPSTREAM FIX — and it is NOT 'author gates more carefully', because careful authoring produced all six: a control must MECHANICALLY DEMONSTRATE IT CAN FAIL before it is trusted to pass, as a PRECONDITION OF BEING WIRED IN. Generalise the mutant-driven proof built ad hoc for the carve-outs gate (mutant A: revert the glob -> 5 assertions fail; mutant B: drop the carve-out -> carved_findings 0 -> 90, gate to exit 1) into the standard authoring step for every gate, recipe row and control. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | RE-001..RE-008 in this file; assets/carveout-mutants.txt; assets/gate-falsification.txt; assets/gate-prework/README.md |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-013

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-19 |
| `stop_class` |  |
| `asked` | DAG-ordering findings for #113 (execution-rehearsal review pass): did the declared epic order survive execution? |
| `answered` | NO — two ordering misses, both of the same shape: the plan sequenced VERIFICATION AFTER CONSTRUCTION where construction already required it. (a) Issue 3.4's falsification was VACUOUS as sequenced: with the linter red on a 320-error corpus, a mutant-induced 'status: fail' is indistinguishable from the standing failure, so Issue 4.2's status-aware promotion had to be FORWARD-PORTED into 3.1 before 3.4 could observe anything. (b) Epic 4 then touched only the test file, because its engine features had already been pulled forward by Epics 1-3. A topological DAG walk over the declared edges would have caught both BEFORE execution: each is a verification step whose precondition is produced by a LATER issue. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | doc_lint corpus before the forward-port: errors=320 files=169; after: errors=0 report_only=610 verdict=PASS. Epic 4 commit dacc75a touches _shared/test_doc_lint.py only |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


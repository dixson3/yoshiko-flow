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
| `when` | 2026-09-03 |
| `stop_class` |  |
| `asked` | Issue 0.0: do all three capability gates carry gate_type/test/test_class/cwd as bead metadata after the 5.2a pour? |
| `answered` | Yes. All three were SET explicitly on bd create and read back clean; no write failed to take, so 0.0 does not halt. Gate ids: yf-mol-tm2d.6, .7, .8. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | grep -c '^### Capability Gate:' plan.md -> 3; bd show yf-mol-tm2d.{6,7,8} --json -> each metadata carries gate_type=auto, test_class=probe, cwd=repo-root and a test string. Full read-back in records/sc14-gate-metadata.md |
| `escape_class` |  |
| `adjudication` |  |
| `origin` | plan_extract.py's Gates grammar recognizes only Type|Approvers|Condition|Test|Blocks|Instructions (#266), so the plan's test_class:/cwd: lines are dropped and unparsed stays [] — the loss is silent. |
| `culpability` |  |
| `prevention` | Issue 0.0 SETS the metadata at pour rather than detecting it afterwards (#273: a detector whose remediation is 'halt' is weaker than a setter). |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-03 |
| `stop_class` |  |
| `asked` | The plan sequences Epic 4's tests (4.1 resume, 4.2 forward-resolution, 4.3 ast, 4.4 inconclusive) AFTER the Epic 2 wiring. Were they authored in that order? |
| `answered` | No. All of them were authored in the SAME file-pass as Issue 2.0, in commit 0ce0822, before the wiring landed. The bead close order still follows the declared DAG, but the code did not. |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | git show --stat 0ce0822 -> skills/yf-plan/scripts/test_land_apply.py only. Suite at 0ce0822 (unwired): 3 failed / 48 passed, the reds being seam_reaches_executor, seam_passes_the_resume_phase_through, inconclusive_not_laundered. Suite at 93eeff7 (wired): 51 passed. |
| `escape_class` |  |
| `adjudication` | Benign, and arguably better than the declared order: it produced a stronger record. Measuring all seven new tests against the unwired build is what exposed that test_inconclusive_not_laundered PASSED VACUOUSLY there — the stub emitted verdict inconclusive / exit 2 on its own without ever reaching the executor. That is the #263 class appearing inside the very file written to close it, and the declared order would have measured that test only after the wiring, where it passes for the right reason and the vacuity is invisible. |
| `origin` | Issue 2.0's own requirement forced it. Its gate demands the seam test be RECORDED AS FAILING against the unwired build, and the honest way to record that is to measure the whole new test block against that build at once — which means writing the whole block first. Writing 4.1-4.4 later would have meant a second, separate pre/post measurement for tests whose pre-state is only meaningful in the same run. |
| `culpability` |  |
| `prevention` | A plan that requires a discriminating pre/post measurement should sequence the WHOLE test block before the fix, not just the one test the gate names. Consider making 'author all tests for this change-set' a single issue when a gate demands a red-before-green record. |
| `cost` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-03 |
| `stop_class` | 1 |
| `asked` | Issue 5.1 requires filing five upstream writes (four new issues plus one edit to #326). Filing is an outward-facing write under the operator's account and cannot be self-certified from inside the plan. Authorize? |
| `answered` | Operator reviewed all five drafts on disk, independently verified their premises (including that the 'deferred' label exists and #326 is OPEN labelled 'bug', so the edit could not fail on a wrong premise), and authorized all five. An intermediate turn first directed the drafts be written to disk as durable bundle artifacts before any wording was published — so the consent gate was taken in two stages: review the wording, then authorize the write. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | SC18 EVIDENCE — five URLs, each verified by gh issue view read-back rather than exit code, all bodies byte-exact against the drafts: #331 land is incompatible with execute.worktree:false https://github.com/dixson3/yoshiko-flow/issues/331 (1872 chars, OPEN, [bug]); #332 assets/upstream-drafts/ is undocumented https://github.com/dixson3/yoshiko-flow/issues/332 (1553 chars, OPEN, [bug]); #333 a decision file inside the tree halts at L16 past the irreversible boundary https://github.com/dixson3/yoshiko-flow/issues/333 (1755 chars, OPEN, [bug]); #334 allow_list=[None] opens the consent gate and its test is vacuous https://github.com/dixson3/yoshiko-flow/issues/334 (2026 chars, OPEN, [bug]); #326 re-labelled deferred with bug KEPT, comment https://github.com/dixson3/yoshiko-flow/issues/326#issuecomment-5534901718 (1341 chars, labels now [bug, deferred]). |
| `escape_class` |  |
| `adjudication` |  |
| `origin` | SKILL.md's retrospective contract states that stop class 1 has NO write site BY CONSTRUCTION, because every class-1 stop in the skill is a designed consent gate that should never be optimized away. This entry is recorded anyway, deliberately: it is the SC18 evidence the plan requires, and SC18 is manual precisely because an outward-facing write cannot be self-certified. It is a record of a consent gate WORKING, not a stop to be frontloaded away. |
| `culpability` |  |
| `prevention` | None sought. This gate should keep firing. The two-stage form the operator used — drafts to disk for wording review, then authorization to write — is a better shape than a single yes/no and is worth keeping: it separates 'is the substance right' from 'is this what should appear under my name'. |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-03 |
| `stop_class` | 5 |
| `asked` | Issue 5.3's FULL tier came back RED — is the plan's change-set broken? |
| `answered` | No. 1 of 21 commands failed, in test_config_tiers.py, on a pre-existing test-isolation defect unrelated to this plan's code. Fixed in one line under ESC-003. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | change_validation.py run --tier full -> status fail; first_failure test_config_tiers.py rc 1, 'assert {"execute.worktree": False} == {}' at :107. The config file is untracked (git ls-files --error-unmatch fails) and gitignored (.gitignore:25), so it is absent from the merged tree and CI could never reproduce this. |
| `escape_class` |  |
| `adjudication` | A genuinely useful red. The test asserted 'no config yields defaults' while reading a real config, so it had been measuring the wrong filesystem for as long as it existed. FRONTLOADABLE: the FULL tier could have been run once at execute start, where this would have surfaced before any work rather than at the last issue before handoff. |
| `origin` | The test calls _bootstrap_config() OUTSIDE the _in_cwd helper, while _load_pm_in restores the cwd after import — so the assertion resolved against the real repository and passed only while that repository happened to carry no config. plan-062 mandates .yf/plan/config.local.json as an execution precondition, which is what made a latent defect fire. |
| `culpability` |  |
| `prevention` | Run the FULL tier ONCE at execute start on plans that mandate a config-file precondition, purely to establish the pre-existing baseline. Without a baseline, every red at Issue 5.3 has to be re-adjudicated as 'mine or theirs' under time pressure. |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-03 |
| `stop_class` |  |
| `asked` | How many of this plan's wrong claims came from the thing under test being wrong, versus from the INSTRUMENT failing silently? |
| `answered` | Three incidents, one class, and none of them was the subject being wrong. In each case a measuring apparatus returned a confident green while measuring nothing, or measuring the wrong thing entirely. |
| `frontloadable` | partial |
| `detected_by` | operator |
| `evidence` | (1) Issue 4.7: 'diff <(extract a019b41) <(extract HEAD)' inside a shell function — both extracts failed with 'bad substitution', diff compared two EMPTY strings and printed IDENTICAL. Caught by noticing the stderr, not by the check. (2) Issue 5.1b/SC17b: 'okf.py reindex --check ... | tail -20; echo 0' — 0 is TAIL's exit code, so a drifting index reported exit 0 and I published the false claim that the checker 'exits 0 even on drift'. Operator measured the opposite; re-measured directly, clean->0, one entry removed->1. (3) Issue 2.0/4.4: test_inconclusive_not_laundered PASSED against the unwired build, because the stub emitted verdict inconclusive / exit 2 on its own without ever reaching the executor. |
| `escape_class` |  |
| `adjudication` | Recorded as a CLASS rather than as three incidents, at the operator's direction, because the fixes are unrelated one-by-one and identical as a family: before believing a green, establish that the instrument could have produced a red. Each was caught by a human or by accident, never by the check itself — which is exactly the property that makes the class dangerous. |
| `origin` | One shape in three costumes: THE INSTRUMENT FAILED SILENTLY AND ITS FAILURE WAS INDISTINGUISHABLE FROM A PASS. An empty comparison, a pipeline's exit code, and a test whose subject was never invoked all produce the same green a real success produces. This is the same defect class as the plan's own headline bug — #327 is a 43-test suite passing comprehensively over an engine no entry point called — and as #263, #181's not-selected-vs-no-such-path, and #207's found flag. The plan was written to attack this class and then reproduced it three times while doing so. |
| `culpability` |  |
| `prevention` | A green is only evidence if the same apparatus has been SEEN to go red. Concretely: assert both sides of a comparison are non-empty before comparing (fixed in the 4.7 close reason); never read 0 after a pipeline — capture to a file and read the producer's code (fixed); and for any new test, run it against the UNWIRED build and record the red (this plan's Gate 2 already mandated exactly that, and it is what caught incident 3). The gate generalises: the red-before-green measurement should be the default for a check, not a special ceremony for one test. |
| `cost` |  |


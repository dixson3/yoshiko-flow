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


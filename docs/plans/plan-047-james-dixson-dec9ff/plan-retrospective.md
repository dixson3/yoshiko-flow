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


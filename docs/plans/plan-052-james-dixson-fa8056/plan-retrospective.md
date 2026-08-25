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
| `kind` | stop |
| `when` | 2026-08-24 |
| `stop_class` | 4 |
| `asked` | review-loop-check reached the configured max_review_cycles bound of 5 with the last red-team verdict still REVISE. Raise the bound for one confirming pass, or override the verdict and approve? |
| `answered` | PENDING — brought to the operator; not resolved by the main session |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py review-loop-check --json -> {escalates: true, cycles: 5, limit: 5, stop_class: 4} |
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
| `when` | 2026-08-24 |
| `stop_class` |  |
| `asked` | Does bd 1.1.2 weave aspects? I measured 'bd formula show' (4 steps, unchanged) and 'bd mol wisp' (6 beads, no verify steps) across six schema shapes and concluded 5.1 was blocked. |
| `answered` | WRONG CONCLUSION from correct measurements. Aspects weave at COOK time — 'bd cook <formula> --dry-run' — over formula-declared steps only. Both surfaces I checked are expected to show no woven steps: formula show renders the RAW formula, and a wisp/pour of an UNCOOKED proto has nothing woven yet. EXP-005 recorded the mechanism verbatim ('Aspects weave at COOK time, over formula-declared steps only') and named the verb I never ran. The working schema is EXP-005's: [[pointcuts]] with glob, [[advice]] array-of-tables with target, and the injected step in the sub-table [advice.after]. |
| `frontloadable` | yes |
| `detected_by` | operator |
| `evidence` | Operator reproduced end to end in a scratch repo on bd 1.1.2 Homebrew: 'bd cook wf-aspect2 --dry-run' -> Steps (4) including write-plan-verify and write-context-verify, each tagged [from: wf-aspect2@advice]; then 'bd cook' + 'bd mol pour --json' -> id_mapping (5) carrying both verify beads, so the weave survives the pour. |
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
| `when` | 2026-08-24 |
| `stop_class` |  |
| `asked` | The first upstream-authorization.txt named every issue under CLASS HEADERS ('A. comment + CLOSE ... #198'). Did the grant check accept it? |
| `answered` | No — grant --check returned EXIT=1 with 18 UNCOVERED actions. Coverage is judged PER ACTION and the search window is THE LINE NAMING THE ISSUE, so a class header does not reach it. The fix was to make every issue line carry its own action verbs. This is plan-048's exact defect — a close missed on an issue the grant already mentioned, surfacing only at verify-reconcile AFTER writes had begun — and here the round-trip check caught it BEFORE any write. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | plan_manager.py grant <plan_dir> --check <plan_dir>/assets/upstream-authorization.txt --json: first attempt EXIT=1, 18 uncovered; after rewriting each issue line to carry its own verbs, EXIT=0 verdict pass uncovered 0, confirmed independently by operator and executor |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


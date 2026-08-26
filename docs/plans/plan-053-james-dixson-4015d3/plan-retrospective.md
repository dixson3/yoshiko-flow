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
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Three review passes each resolved every concern; passes 2 and 3 then measured only 9/14 and 9/15 of those resolutions reproducing. |
| `answered` | RE-002 named against the RESOLUTION PROCESS rather than the plan: the main session repairs a scope at the site the reviewer names and does not sweep for the same property elsewhere. Remedy adopted at pass 3: DELETE the drifting count literals rather than correct them, and let the controls enumerate. Four literals removed (D-8's site count, 3.7's '8 rows', 5.1's '16 sites', D-13's '0 of 41'). |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | pass-2 9/14=64%, pass-3 9/15=60%; three of pass-3's five (c)-class failures were re-broken by pass-2's own remedies |
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
| `when` | 2026-08-25 |
| `stop_class` |  |
| `asked` | Pass 4 measured the pass-3 structural remedy (delete drifting count literals) as itself applied site-by-site: 1 of 4 literals actually removed. |
| `answered` | Remedy changed AGAIN, this time procedurally rather than textually: apply the fix, then RUN the reviewer's own verification command and re-sweep on failure. On this pass that caught three literals the first edit pass missed (C50, C51, C52) and pushed two fixes beyond the concern's stated scope (C46 also corrected exp-003 and a section heading nobody named). |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | reproduction rate 64% -> 60% -> 50%; all six pass-4 verification commands now return the required value |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


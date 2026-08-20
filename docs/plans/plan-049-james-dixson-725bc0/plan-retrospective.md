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
| `when` | 2026-08-20 |
| `stop_class` |  |
| `asked` | SC31/Issue 2.4 fixed a literal target of corpus unparsed[] <= 81 at approval, called 'the no-added-residue floor for a reading change' |
| `answered` | Measured 83. The +2 is two plan-010 declarations that were INVISIBLE pre-widening and are now visible-and-refused (prose tail; gate id in the referent list). Recorded as a MISS with its derivation rather than satisfied by silently dropping them, which REQ-DATA-052 forbids |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | uv run _shared/plan_extract.py docs/plans/*/ -> unparsed 81 -> 83; dag_guard verify --upper-bound exit 0, losses 0 |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-20 |
| `stop_class` | 1 |
| `asked` | Authorize the upstream write: 5 comments, CLOSE #135, and create the coarse tracker |
| `answered` | (pending) |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | test -f assets/upstream-authorization.txt -> exit 1; bd shows 6.4/6.5/6.6/6.7 and the reconcile step open, all downstream of the gate |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


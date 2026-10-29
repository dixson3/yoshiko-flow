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
| `when` | 2026-10-29 |
| `stop_class` | 5 |
| `asked` | Affected FAST failed on missing assets index entry |
| `answered` | Main planner added descriptive assets entry and synchronized triage, then reruns validation |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | change_validation fast exit1, first_failure=okf-index-drift; missing assets/ for plan-074 only |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |
| `sc_flipped_post_approval` |  |
| `halts_post_irreversible` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-10-29 |
| `stop_class` |  |
| `asked` | Red-team C1: own old-tool intake and receipt transition unallocated |
| `answered` | Added unapproved B0 bridge and old-intake/no-preseeded-receipt rehearsal; independent rereview required |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | reviews/pass-1.md C1, M1-M4 and resolved-cell rg exit0; actual bootstrap not run |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |
| `sc_flipped_post_approval` |  |
| `halts_post_irreversible` |  |

## RE-003

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-10-29 |
| `stop_class` | 5 |
| `asked` | Intake ready-check failed on missing non-exclude tracker body |
| `answered` | Retained exact verified #456 body and indexed it; rerun audit/readiness before publication |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | audit: references/upstream-456.md missing body after adding tracker row; no scope/content change |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |
| `sc_flipped_post_approval` |  |
| `halts_post_irreversible` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-10-29 |
| `stop_class` | 5 |
| `asked` | FULL validation timed out at 1800s during a row with a declared 28800s timeout; publication held |
| `answered` | Allow plan-only publication exception (Recommended) |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | references/publication-exception.json; preserved invocation-error and full-timeout receipts; FULL INCONCLUSIVE, process exit unknown, never pass |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |
| `sc_flipped_post_approval` |  |
| `halts_post_irreversible` |  |


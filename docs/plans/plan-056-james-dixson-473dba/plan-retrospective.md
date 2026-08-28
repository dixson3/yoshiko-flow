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
| `when` | 2026-08-28 |
| `stop_class` |  |
| `asked` | Plan Epic 0 allocates new requirement ids REQ-DATA-071, REQ-DATA-072, REQ-CLI-017, REQ-CLI-018. |
| `answered` | Those four ids are ALREADY SHIPPED and unrelated (REQ-DATA-071 touches[]; REQ-DATA-072 STATUS_SEVERITY fail-closed; REQ-CLI-017 attest-validation; REQ-CLI-018 verify-reconcile). Reallocated to the next free ids in each family: 0.2 -> REQ-DATA-074, 0.4 -> REQ-DATA-075, 0.11 -> REQ-CLI-028, 0.14 -> REQ-CLI-029. REQ-PLAN-081, REQ-OKF-CHK-003 and REQ-OKF-CHK-004 were free and are used as written. plan.md is NOT edited: its Epics section is fingerprinted, and the criterion SC1 asserts coverage STRUCTURE (an issue names a REQ or transitively depends on an Epic-0 issue that adds one), not specific numbers. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | grep -o '^REQ-DATA-[0-9]+' skills/yf-plan/spec/data.md | tail -> ...071,072,073; grep -o '^REQ-CLI-[0-9]+' skills/yf-plan/spec/cli.md | tail -> ...025,026,027 |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


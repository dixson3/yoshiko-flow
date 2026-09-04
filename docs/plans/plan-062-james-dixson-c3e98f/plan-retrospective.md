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


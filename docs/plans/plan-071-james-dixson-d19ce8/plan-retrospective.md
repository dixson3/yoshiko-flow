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
| `when` | 2026-09-12 |
| `stop_class` |  |
| `asked` | SC4's clause cannot hold on macOS (BSD ls exit 1 vs GNU 2); amend or leave? |
| `answered` | amended to a portable test ! -e clause (ESC-001 default taken, no operator answer arrived) |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | ready-check smoke-run: SC4 actual_exit 1 expected 2; bash -c 'ls /nonexistent-a /nonexistent-b' exit 1 |
| `escape_class` | criterion authored against a non-portable exit code; the pre-review smoke saw it RED for the right-looking reason (files existed) and could not distinguish that from the wrong exit code |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` | REQ-PLAN-085's smoke-run now records actual_exit per row; a reviewer can see 1 vs 2 before approval |
| `cost` |  |


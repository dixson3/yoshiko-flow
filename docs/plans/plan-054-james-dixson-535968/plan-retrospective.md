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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | yf-herdr SKILL.md Launch step: resolve the current agent kind via 'herdr agent list --json | jq -r ...' |
| `answered` | The command is INVALID — herdr emits JSON by default and 'agent list --json' exits 2 with a usage error. Piping into jq swallowed the error, so KIND resolved to the empty string and the next step would have run 'herdr agent start --kind ""'. Recovered by re-reading without the flag. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | herdr agent list --json >/dev/null; echo $? -> 2. Prescribed at skills/yf-herdr/SKILL.md:65 and in the installed copy at ~/.claude/skills/yf-herdr/SKILL.md:66. |
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
| `when` | 2026-08-26 |
| `stop_class` |  |
| `asked` | Does 'herdr tab create' support --no-focus, as yf-herdr SKILL.md:73 prescribes? |
| `answered` | I reported it did NOT and that the skill was wrong. That was FALSE. --no-focus is a real flag; I had read 'herdr tab create --help' truncated at head -20 and the flag sits at line 21. The skill is correct here. Cost: a false defect claim relayed to the operator, plus a stray tab created while testing it (cleaned up). |
| `frontloadable` | partial |
| `detected_by` | self-report |
| `evidence` | herdr tab create --help | grep -n -i focus -> 18: --focus, 21: --no-focus. Direct invocation exits 0. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


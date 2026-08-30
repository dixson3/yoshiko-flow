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
| `when` | 2026-08-30 |
| `stop_class` | 5 |
| `asked` | FULL validation tier on the execute branch |
| `answered` | RED: cargo test --workspace rc=101 — SPEC coverage gap, 15 testable REQ-YF-DOC ids with no Rust test tag and no allowlist entry |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | uv run change_validation.py run --tier full --json -> first_failure.cmd='cargo test --workspace', returncode 101; coverage.rs:209 panic naming REQ-YF-DOC-001..018 |
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
| `when` | 2026-08-30 |
| `stop_class` |  |
| `asked` | Epic 3 scope: the plan named 3 usage failures (yf-beads-upstream, yf-incubator, yf-skill-authoring) |
| `answered` | The checker measured 5. yf-beads-init taught /beads-init and yf-markdown-lint taught /markdown-lint — the identical defect class, invisible to the plan's manual survey. Repaired under Epic 3; SC2 is unsatisfiable otherwise. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | check_skill_readme_contract.py --json | jq '.failures[]|select(.class=="usage")' -> 5 rows pre-backfill |
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
| `when` | 2026-08-30 |
| `stop_class` |  |
| `asked` | SC6 states: uv run -m pytest scripts/checks/test_check_skill_readme_contract.py -q |
| `answered` | That literal command fails on this tree — it resolves to the project .venv, which has no pytest ('No module named pytest'). The house convention every existing CHANGE-VALIDATION.md pytest row uses is 'uv run --with pytest python3 -m pytest <file> -q', which passes 18/18. SC6's intent holds; its spelling does not. Recipe rows use the house form. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | env -u VIRTUAL_ENV uv run -m pytest scripts/checks/test_check_skill_readme_contract.py -q -> 'No module named pytest' |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


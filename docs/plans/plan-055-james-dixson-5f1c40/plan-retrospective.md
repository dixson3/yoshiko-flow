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
| `when` | 2026-08-27 |
| `stop_class` |  |
| `asked` | Issue 5.1: run the prune-private dry-run against this machine's private trees and write the per-directory verdicts to assets/migration-dryrun.json |
| `answered` | The first run returned roots:[], delete:0, kept:0, undetermined:0 with EXIT 0 against a machine holding 32 and 33 directories in exactly the two roots it was meant to walk. Cause: default_private_roots (Issue 1.4) derived the private-root set from the descriptor table BY DIFFERENCE — 'every resolved skills root that is not the shared one'. Issue 2.2 then collapsed every non-claude row onto the shared root, so the difference became EMPTY and the migration silently became a no-op that reported success. Category error: the descriptor describes where yf writes NOW; the migration is about where yf wrote BEFORE, and a table already corrected cannot describe the state it was corrected from. Fixed by replacing the derivation with an explicit closed list of legacy roots, and guarded by a new test legacy_private_roots_are_non_empty_after_the_collapse asserting non-emptiness in both scopes. Note the defect was invisible to every check that existed: 453 tests were green, and the migration gate's deliberate empty-delete-set failure was the ONLY thing that would have caught it — one layer later, at the gate. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | yf harness skills prune-private --scope user --json -> {roots:[],delete:0,kept:0,undetermined:0}, exit 0; after the fix -> roots:[~/.config/opencode/skills, ~/.pi/agent/skills], delete:38, kept:26, undetermined:1. Guard: yf/src/cmd/harness/prune_private.rs::legacy_private_roots_are_non_empty_after_the_collapse |
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
| `when` | 2026-08-27 |
| `stop_class` |  |
| `asked` | Issue 5.2 step (3): 'On green, commit and drop the quarantine; on red, run the one-line restore and halt.' |
| `answered` | Committed on green, but the quarantine was RETAINED rather than dropped. Dropping it is the single irreversible act in the whole migration and it buys nothing at this moment: the plan is not yet merged, 5.3's FULL tier has not run, and the Deferred table's own mid-execution-abandonment row prescribes 5.2a's restore as the recovery path — which requires the quarantine to still exist. Deleting it would remove the recovery this plan built two issues to guarantee, minutes before the validation that could need it. The quarantine is reported to the operator instead, who can drop it once the plan has landed. |
| `frontloadable` | yes |
| `detected_by` | self-report |
| `evidence` | quarantine retained at /Users/james/.yf-quarantine/plan-055-1787886237 holding 38 skill directories + 1 operator-authorized symlink, each with .origin recorded; restore command emitted in the apply verdict and measured byte-exact by scripts/checks/check-quarantine-restore.sh |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


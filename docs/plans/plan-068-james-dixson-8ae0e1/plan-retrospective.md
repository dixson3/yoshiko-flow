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
| `when` | 2026-09-09 |
| `stop_class` | 1 |
| `asked` | Gate 4 (consent): authorize editing upstream GitHub issues #331/#348/#349/#353 and the plan-063 residue asset per Issue 3.1's five corrections? |
| `answered` | Authorize all five corrections (the full set, including the residue asset and bead yf-f7lq) |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | gate metadata test_class=consent, gate_type=human; presented at the SKILL.md 5.2c execute-start sweep BEFORE any coding work, as the single batched prompt |
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
| `when` | 2026-09-09 |
| `stop_class` |  |
| `asked` | Issue 1.1 predicted EIGHT broken tests (pass-5 prototype); how many actually broke? |
| `answered` | SIXTEEN. The extra eight came from Issue 1.1's own recorded decision to add env= to the seam now rather than later, which the pass-5 prototype did not include. With FakeRunner updated to accept and record env, the residue was exactly the predicted eight. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | uv run skills/yf-plan/scripts/test_land_apply.py -> '16 failed, 50 passed'; after the FakeRunner env= patch -> '8 failed, 58 passed'; after the eight stub fixes -> '66 passed' |
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
| `when` | 2026-09-09 |
| `stop_class` |  |
| `asked` | Issue 2.4: does swapping git diff <target> <branch> for <target>..<branch> fix the symmetric-difference defect? |
| `answered` | NO. Measured IDENTICAL — changed_paths ['work.txt'] for a branch strictly behind its target. For git diff the two-dot form is not a range, it is sugar for the same symmetric endpoint diff. The landed fix uses an explicit git merge-base left endpoint. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | test_merge_preview_is_directional FAILED after the two-dot change with 'a behind-branch merge introduces NOTHING, but the preview named [work.txt]' |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-09 |
| `stop_class` |  |
| `asked` | Issue 3.3: does plan-069 carry all eight relocated items faithfully? |
| `answered` | Seven yes; the eighth (the #334/SC4 tty coupling) was carried as a PREDICTION that execution falsified. It predicted an explicit tty allow-list; the landed test drives _land_execute directly and never reaches _land_tty_gate, which lives in the CLI preamble. Intent satisfied more strongly, verification step different. plan-069's text corrected. |
| `frontloadable` | no |
| `detected_by` | self-report |
| `evidence` | grep for 'allow-list' in test_land_inplace.py returns the docstring only; the test passes decision-level steps to _land_execute and never invokes the CLI path |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-005

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-09 |
| `stop_class` | 5 |
| `asked` | The FAST/FULL tier is RED at Issue 0.3 (_shared/test_doc_lint.py SC41). Is this plan's change responsible? |
| `answered` | No — inherited from main. git diff --stat <base> -- docs/plans/plan-069.../ is EMPTY, so plan-069's zero-row Success Criteria table is byte-identical to the execute base. Recorded as findings/exec-001 and dispositioned to Issue 3.3, which owns plan-069's text; cleared there. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | change_validation.py run --tier fast --changed skills/yf-plan/spec/landing.md -> first_failure: doclint-tests; the failing assertion is SC41 blast radius 0 vs measured 1 |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-006

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-09-09 |
| `stop_class` |  |
| `asked` | Writing the landing decision JSON via a python3 heredoc — was the heredoc delimiter quoted? |
| `answered` | NO. I wrote <<PYEOF instead of <<'PYEOF', so zsh command-substituted every backtick in the embedded JSON. The shell EXECUTED fragments of the decision text, including 'yf self install --from-build --build' — the mid-execution deploy this very plan prohibits. It failed closed at the promote step (/Users/james/.local/bin/yf already exists — pass --force), so nothing was overwritten: binary still 0.5.0 (77eb7fe) dated Sep 5, installed skill tree still byte-DIFFERENT from the repo, git tree clean. Rewritten using the Write tool with zero shell interpolation. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | zsh emitted 'command not found: include/partial/deferred', 'fatal: ambiguous argument origin/main...main', and 'error: /Users/james/.local/bin/yf already exists — pass --force to overwrite'; post-hoc: yf --version unchanged at 0.5.0 (77eb7fe), diff of installed vs repo plan_manager.py still DIFFERENT, git status clean |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-007

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-09 |
| `stop_class` | 5 |
| `asked` | FULL tier at land: green? |
| `answered` | Not on the first three runs. Three failures, TWO of them inherited from main and one this plan's: (1) doclint SC41 vs plan-069's empty criteria table [inherited, cleared at Issue 3.3]; (2) okf-index-drift on plan-069's seven unindexed members [inherited, real descriptions authored]; (3) skill-readme-contract layout fence missing this plan's three new scripts, and skill_diagrams drift on yf-plan.d2 [both this plan's, both fixed]. Fourth run: status pass. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | change_validation.py run --tier full --json: first_failure doclint-tests, then okf-index-drift, then skill-readme-contract, then skill_diagrams --check, then status pass. git diff --stat <base> -- docs/plans/plan-069/ is EMPTY for the first two, which is what establishes they were inherited. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


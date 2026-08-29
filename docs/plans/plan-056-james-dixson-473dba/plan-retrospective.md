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

## RE-002

| field | value |
| :-- | :-- |
| `kind` | deviation |
| `when` | 2026-08-28 |
| `stop_class` |  |
| `asked` | The FULL tier went red at Issue 3.2 on test_config_tiers.py::test_no_config_yields_defaults. |
| `answered` | The cause was THIS SESSION's own gitignored .yf/plan/config.local.json (an execute.worktree opt-out), not the plan's changes. Mechanism: _load_pm_in() chdirs into a temp repo FOR THE IMPORT and restores cwd in its finally block, but the test then calls pm._bootstrap_config() — a CWD-RELATIVE reader — after the restore, so it reads the developer's real config. The file's own line 68 warns about exactly this hazard for a different helper. The test therefore passes only when the developer happens to have no local config. Removed the opt-out (in-place mode needs no config — it is maintained by not invoking 'worktree ensure') and filed the latent defect as a follow-on for Issue 4.2. |
| `frontloadable` | no |
| `detected_by` | mechanical-check |
| `evidence` | uv run skills/yf-change-validation/scripts/change_validation.py run --tier full --json -> first_failure test_config_tiers.py, 'AssertionError: assert {execute.worktree: False} == {}' |
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
| `when` | 2026-08-28 |
| `stop_class` |  |
| `asked` | How long does the §6.4 recheck-criteria step cost on this plan? |
| `answered` | MINUTES, because SC11 and SC11c route through check-recipe-row.sh, which runs the FULL tier to prove a row is WIRED rather than merely written — and recheck-criteria executes each criterion in a fresh subprocess, so the three invocations each pay their own full suite. check-recipe-row.sh DOES support a YF_FULL_TIER_JSON cache (added at Issue 1.9 for exactly this), but a criterion's Verification cell is a bare command string with no way to set an environment variable, so the cache is unreachable from the binding that needs it most. Recorded rather than fixed: the criteria are correct and the cost is real but bounded, and plumbing an env var through the Verification grammar is a plan_extract/REQ-DATA-070 change well outside this plan's scope. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | recheck-criteria on plan-056 ran >10 min; 'ps aux | grep recheck-criteria' showed it live across three successive FULL-tier suites |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-004

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-08-28 |
| `stop_class` | 5 |
| `asked` | §6.4 recheck-criteria on plan-056's own close. |
| `answered` | HARNESS_INCOMPLETE, exit 1 — THE VERDICT THIS PLAN SHIPPED, FIRING ON THIS PLAN. 18 of 19 class-A criteria judged; SC11c unjudged because it chains TWO check-recipe-row.sh invocations in one Verification cell, each of which runs the multi-minute FULL tier, and recheck-criteria's per-criterion timeout is 300s. Pre-fix this would have been verdict PASS, exit 0, 'all 18 evaluated criterion/criteria hold' — SC11c silently absent from the arithmetic. That is exactly #265, caught on the plan that fixed it. Note the plan's own R11/R13 predicted the fix would be INERT here because §6.4 resolves SKILL_DIR to the INSTALLED skill; it fired only because this run deliberately invoked the working-tree plan_manager.py. Resolution: the instrument is sound (SC11c verified green by hand with the cache warm), so the defect is the BINDING — an opt-in YF_FULL_TIER_JSON cache is unreachable from a Verification cell, which is a bare command string. Fixed properly by giving check-recipe-row.sh a DEFAULT cache keyed on the tree fingerprint (HEAD + hash of git status --porcelain) with a 30-minute age cap, so any tree change misses and a stale result can never report a row as wired when it is not. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | /tmp/rc.json: verdict HARNESS_INCOMPLETE, class_a 19, evaluated 18, unjudged [SC11c], detail 'timed out after 300s' |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |


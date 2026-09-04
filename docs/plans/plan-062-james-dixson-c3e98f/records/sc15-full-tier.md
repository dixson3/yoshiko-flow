---
type: Record
okf_spec: OKF-PLAN
id: sc15-full-tier
plan: plan-062-james-dixson-c3e98f
description: 'SC15 evidence for Issue 5.3 — the authoritative FULL-tier run. 66 commands, zero failures, exit 0, at HEAD 365fcad. Records the first run''s single red (a pre-existing test-isolation defect, not this plan''s code) and its ESC-003 resolution, so the green is legible rather than bare.'
---
# SC15 — the FULL validation tier (Issue 5.3)

SC15 is `manual:` by design: a clause would re-run the multi-minute tier at L5 and again
at L11, and its 300s cap would record a timeout as FAIL **past the irreversible boundary**
(pass-3 C32). This file is its evidence, and Issue 5.3's run is the authoritative one.

## The authoritative run

```
$ uv run skills/yf-change-validation/scripts/change_validation.py run --tier full --json
status  : pass
tier    : full
commands: 66
failures: 0
exit    : 0
```

At `HEAD` = `365fcad0e72eb367917161760b902f18a8e26491`, branch `plan-062-james-dixson-c3e98f-execute`.

## The first run was RED, and the red was not this plan's code

Recorded because a green with no history is the weaker artifact.

| | First run | This run |
| :-- | :-- | :-- |
| Status | `fail` | `pass` |
| Commands reached | 21 (stops at first failure) | 66 |
| Failure | `test_config_tiers.py`, rc 1 | none |

`test_no_config_yields_defaults` asserted `_bootstrap_config() == {}` while calling it
**outside** the `_in_cwd` helper. `_load_pm_in` restores the cwd after import, so the
assertion resolved against the **real repository** and read this plan's mandated
`.yf/plan/config.local.json`, getting `{'execute.worktree': False}`.

That file is **untracked and gitignored** (`.gitignore:25`), so it is absent from the
merged tree and CI could never have reproduced this. The test had been measuring the wrong
filesystem for as long as it existed, and passed only while the repository happened to
carry no config.

Resolved under **ESC-003** by using the helper the same file already uses correctly at
lines 150, 161 and 168. That is **scope beyond plan-062**, stated plainly here and in the
landing handoff §1.2 so the operator can drop the hunk if they would rather it landed
separately.

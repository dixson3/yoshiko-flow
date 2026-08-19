---
type: Finding
okf_spec: OKF-PLAN
id: exec-004-audit-measured
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exec-004 — D-12 measured by EXECUTION, not by reading (plan-046 Issue 3.8, SC8)

**Why this exists.** D-12 was originally asserted from *reading* `plan_manager.py`, and the claim it
replaced was **wrong**. The plan records that as having "exactly the shape this plan is written
against". Issue 3.8 converts the corrected claim from a reading into a measurement.

All runs invoke the **repo** copy explicitly. A bare `plan_manager.py audit` resolves through
`SKILL_DIR` to the *installed* skill, which imports its own vendored `okf.py` — it would exercise the
**old** engine and report green regardless of what Issue 3.6 did.

## The filter under test

```python
_OKF_PORT050_REQS = frozenset({"REQ-OKF-003", "REQ-OKF-030", "REQ-OKF-031", "REQ-OKF-071"})  # :3525
...
if cf.level != "error" or cf.req not in _OKF_PORT050_REQS: continue                          # :3967
```

Both line numbers match D-12's claim exactly, on the executed tree.

## Runs

| # | condition | audit exit | `status` | okf findings surfaced |
| :-: | :-- | :-: | :-- | :-- |
| 0 | baseline, unmutated | `0` | `pass` | none |
| A | **synthetic `REQ-OKF-CHK-002` promoted to `error`** | **`0`** | `pass` | **none** |
| B | **positive control** — allowlisted `REQ-OKF-003` at `error` | **`1`** | `fail` | `okf:zz-positive-control.md` → `fail` |

### Run A — the measurement

Mutating the level to `error` in **both** `_shared/okf.py` and the `skills/yf-plan/scripts/okf.py`
copy `plan_manager.py` actually imports, `okf check` emitted three genuine error-level findings:

```
[error] .../index.md: REQ-OKF-CHK-002 — index ghost: diagrams/ — entry target does not resolve
[error] .../index.md: REQ-OKF-CHK-002 — index ghost: assets/ — entry target does not resolve
[error] .../index.md: REQ-OKF-CHK-002 — index ghost: plan-retrospective.md — entry target does not resolve
```

`audit` nonetheless exited **0**, `status: pass`, with **zero** okf findings in its report. The
allowlist discards them at the `cf.req not in _OKF_PORT050_REQS` clause. **D-12 is confirmed: a newly
allocated REQ cannot block `audit` at any level.**

**The error level is the discrimination, and it matters.** Issue 3.6 lands the real finding at
*warning*, so a warning-level synthetic would be discarded by the **first** clause (`cf.level !=
"error"`) and never reach the allowlist at all — it would test D-10 while appearing to test D-12.

### Run B — the positive control

Without it, run A's green is indistinguishable from a harness that cannot observe failure. A single
`.md` with no frontmatter (an **allowlisted** `REQ-OKF-003` error, no code mutation) drove audit to
exit **1** with `status: fail` and the finding surfaced as `okf:zz-positive-control.md`. **The harness
can observe failure**, so run A's exit-0 is a real result.

*Incidental confirmation:* run B also emitted `[warning] REQ-OKF-CHK-002 — index missing:
zz-positive-control.md`, which did **not** contribute to the failure — the warning level from Issue
3.6 behaving as specified, observed rather than asserted.

## Revert, asserted before closing

Issue 3.8 requires this, because Issue 4.1 depends on 3.8 and an unreverted mutant would have 4.1
measure a mutated tree.

| assertion | result |
| :-- | :-- |
| no `REQ-OKF-CHK-002", "error"` remains in either copy | clean (grep exit 1) |
| positive-control file removed | yes |
| `git status --porcelain docs/plans/` | empty |
| `sync.py --check` | exit `0` |
| `_shared/test_okf.py` | 57 passed |
| `audit` back to baseline | exit `0` |

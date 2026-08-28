---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #165: SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

- **Number:** 165
- **Title:** SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false
- **URL:** 
- **State:** OPEN
- **Labels:** priority::high

## Body

Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 424/424, clippy clean, Tier-1 18 suites / 359 tests, `/yf-okf check` 0 findings, **FULL validation tier 33/33 pass**.

At that same moment `REQ-CLI-006` in `skills/yf-plan/spec/cli.md` was **false**:

```
grep -c '^@cli.command' skills/yf-plan/scripts/plan_manager.py   ->  25
spec asserted                                                    ->  24
```

The requirement's own `Verification:` line names that exact grep. Nothing ran it. It is **prose shaped like a command**, so the FULL tier can be exhaustively green while the spec it validates contradicts the code.

## The instance is fixed; the class is not

plan-045 corrected `REQ-CLI-006` to assert **self-consistency** (enumeration length == grep count) rather than a hardcoded literal, so it cannot drift again. That was the right fix for one requirement — it had drifted **three times inside a single plan** (`10 vs 21` → `23 vs 21` → `24 vs 25`), including in the very commit that fixed the previous drift.

Other `Verification:` lines across `SPEC.md` and `skills/*/spec/*.md` are still literal commands that nothing executes.

## Proposed

1. Audit `Verification:` lines for ones that are **literal, runnable commands** as opposed to prose descriptions of how a requirement is satisfied.
2. For each: either promote it to a real `CHANGE-VALIDATION.md` §1 row so it executes, or restate it as a self-consistency assertion that cannot go stale.
3. Prefer self-consistency over a hardcoded count anywhere a count is maintained by hand against a growing file.

## Why this matters

This is #149's thesis — *a step with no exit code is not a step* — in a weaker and more deceptive form: a step that **looks** like it has an exit code, reads as verified, and is never run. It sat inside the spec of the plan that cites #149 as its own framing, and survived four red-team passes plus a full-tier sweep.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #164: CHANGE-VALIDATION: `skills/*/SPEC.md` maps to `uv-herdr-launch`, so every skill's SPEC.md runs yf-herdr's launch test

- **Number:** 164
- **Title:** CHANGE-VALIDATION: `skills/*/SPEC.md` maps to `uv-herdr-launch`, so every skill's SPEC.md runs yf-herdr's launch test
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Follow-on from plan-045 (#162). Observed during execution; deliberately not fixed in-plan.

## The mapping

`CHANGE-VALIDATION.md` §3 carries:

```
| `skills/*/SPEC.md` | `uv-herdr-launch` |
```

That glob is **every skill**, so editing e.g. `skills/yf-okf/SPEC.md` runs `yf-herdr`'s launch-contract test — a test about herdr delegation prompts, with nothing to say about yf-okf.

`skills/yf-herdr/**` (the adjacent row) already covers the intended case, so the broad glob adds no coverage the narrow one lacks.

## Why it is not urgent

`test_launch_contract.py` is green as of plan-045 Epic 5 (15/15), so today this only costs an irrelevant test run.

It was **not** harmless during execution: Epic 1 landed that test deliberately RED (8 failed / 3 passed) so Epic 5 could turn it green. For the window between those epics, **any per-skill `SPEC.md` edit anywhere in the repo failed the FAST tier** on an unrelated yf-herdr test. Nothing depended on it, but the blast radius was repo-wide rather than confined to yf-herdr.

## Fix

Narrow the row to `skills/yf-herdr/SPEC.md`, or drop it as redundant with `skills/yf-herdr/**`.

## Why it matters beyond the one line

A glob wider than its test's subject produces a **false signal** — a green that means nothing and a red that misattributes. That is the same axis plan-045 was built on: a check that runs is not automatically a check that verifies.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

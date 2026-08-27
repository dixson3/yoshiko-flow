---
type: Upstream Reference
okf_spec: OKF-PLAN
id: upstream-236
description: "Full body of upstream issue #236 — the coarse execution tracker for plan-054"
---

# #236 — plan-054-james-dixson-535968 execution tracking

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/236
- **State:** OPEN
- **Labels:** _none_
- **Disposition:** `tracker` (report-only)

This is plan-054's **coarse tracking issue**, filed at INTAKE §4.5 and stamped onto the plan
epic as `external_ref` at the pour (`REQ-PLAN-073`) so it is visible to `upstream.py closable`.
It tracks the plan-scale effort as a whole; the per-issue work is tracked in beads, not here.

## Body (verbatim)

The single coarse tracking issue for **plan-054** (`plan-054-james-dixson-535968`), per the
AGENTS.md one-tracker-per-plan convention.

- **Plan bundle:** [`docs/plans/plan-054-james-dixson-535968/`](docs/plans/plan-054-james-dixson-535968/)
- **Landed:** merge `8c7a27a` on `main`
- **Epic:** poured at `/yf-plan execute` (intake does not pour)

## Objective

Cut **v0.5.0**. 411 commits and 28 plans have landed since `v0.4.0` and almost none of it is
reflected in what a user reads: `CHANGELOG.md` has had 2 commits and describes plan-027 alone;
`README.md` contains zero occurrences of `opencode`, `pi` or `--harness`; the website asserts a
formula count that is wrong and documents an install flow that omits a default-on step which
exits non-zero without a consent flag.

## The defect that makes this a blocker, not a docs chore

`yf` deploys skills to `~/.pi/agent/skills` and `~/.config/opencode/skills`, but the `SKILL_DIR`
resolver embedded in 19 files searches six roots and **neither destination is among them**.
Measured live in both harnesses: they load the prose from their own tree and resolve scripts to
the *claude-code* copy. Under a pi-only `HOME`: `ERROR: yf-plan skill directory not found`,
exit 1. No existing test could catch it — the failure appears only when `~/.claude/skills` is
absent, which no developer machine with claude-code installed will produce.

## Scope

58 issues across 7 epics: SPEC amendments + the control/check evidence layer · `yf skill-dir`
and a generated resolver · the pi/opencode regression + a symlink-revert fix · six shipped
silent-failure defects · in-tree docs incl. a ten-theme changelog · website accuracy + two
missing drift edges · verify/close stale issues, bump, tag.

## Upstream issues in scope

**Fixed:** #185, #225, #226, #201, #195, #203, #229
**Verified and closed:** #119, #120, #122, #123, #124, #231
**Rescoped:** #127 (its "cold reader can decode the docs" criterion is measurably unmet)
**Documented, not fixed:** #121 (pi config tuning stays a correct deferral)

## Review record

Six independent red-team passes: **22 → 14 → 8 → 9 → 8 → 6** concerns, verdict **APPROVE** at
pass 6. The recurring class was *criteria that cannot fail* — one escaped in each of the first
four passes, including inside the fix for the previous one. Epic 0's evidence layer is the
structural remedy.

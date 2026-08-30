# exp-006 — the FULL validation tier, and the defect it caught

**Type:** validation evidence (plan-061 Issue 5.4)
**Date:** 2026-08-30
**Tier:** `full` (the CI ∪ repo-checks superset) — 65 commands

## Result

| Run | Tree | Verdict | First failure |
| :-- | :-- | :-- | :-- |
| 1 | `plan-061-…-execute` @ `b3835c0` | **FAIL** | `cargo test --workspace` (rc 101) |
| 2 | `plan-061-…-execute` @ `d08e2d0` | **PASS** — 65/65 | none |

## What run 1 caught, and why it is the plan working rather than failing

```
SPEC coverage gap: 15 testable REQ-YF requirement(s) have no `// {id}` test tag
and no allowlist entry:
  REQ-YF-DOC-001 … REQ-YF-DOC-018
```

`yf/src/coverage.rs::every_testable_req_is_tagged_or_allowlisted` asserts that every macro
requirement marked `*(testable)*` in `SPEC.md` names at least one **in-crate Rust** test, or
carries a reviewed `ALLOWLIST` entry.

The 15 `REQ-YF-DOC-*` ids have no Rust tag **and correctly never will**: §3.11 governs the
`skills/*/README.md` documentation surface, and its enforcement is a Python checker with an
18-test suite plus three `CHANGE-VALIDATION.md` recipe rows. There is no in-crate behavior to
tag.

`ALLOWLIST` is exactly the mechanism for this — its own doc comment says *"verified only by an
external mechanism"* — and the precedent is established: `REQ-YF-DIST-001` (covered by the CI
release workflow) and `REQ-YF-RENAME-003` (covered by the drift-check gate).

**These rows are not a plan-044 D-7 temporary bridge.** A bridge row is removed in the same
commit as the `// REQ-…` tag that supersedes it; no such tag is coming here, and none should.
The distinction is recorded in the block comment so a later reader does not delete the rows as
stale.

**Each row names its specific covering test**, not "CI" generically. That is deliberate: the
premise of §3.11 is `REQ-YF-DOC-010` — an obligation with no runnable command is not enforced.
An allowlist row naming an unrunnable mechanism would reproduce that exact defect *inside the
gate built to catch it*.

## Why this belongs in the record

The SPEC-first ordering `AGENTS.md` mandates has a cost this run made visible: landing a
`*(testable)*` REQ in Epic 0 turns the coverage gate red the moment the SPEC edit lands, before
any implementation exists to tag. plan-032, plan-044 and plan-054 each hit it and used a
temporary bridge. plan-061 is the first to hit the *permanent* form of the case — a `REQ-YF-*`
whose verification lives outside the crate for good — and it is resolved by an ordinary
allowlist entry rather than by a bridge.

It was caught by the FULL tier **on the execute branch, before any merge**, which is the whole
argument for running it.

## Scope check (SC9)

The merged path set touches no `web/` path and no OKF bundle outside this plan's own folder —
confirmed against the merge preview's `changed_paths`. Plans 2 (#316) and 3 (#317) remain
untouched.

## Command

```bash
uv run "$(yf skill-dir yf-change-validation)/scripts/change_validation.py" run --tier full --json
# tier=full status=pass n=65  (65 pass, 0 fail)
```

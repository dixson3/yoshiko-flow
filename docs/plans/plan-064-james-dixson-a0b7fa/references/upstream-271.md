---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #271 - plan-056-james-dixson-473dba execution tracking'
---
# Upstream #271: plan-056-james-dixson-473dba execution tracking

- **Number:** 271
- **Title:** plan-056-james-dixson-473dba execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

Coarse tracking issue for plan-056, per this repo's one-issue-per-plan-scale-effort convention.

## What the plan does

Makes the structural validation that already exists **able to fail**, and reconciles the two engines
that perform it. It deliberately does NOT build new structure.

- **Epic 0** — 14 SPEC amendments, ahead of every behaviour change (SPEC-first).
- **Epic 1** — engine contract repair: `reindex`'s exit contract can no longer confuse "no index" with
  "no such path"; a member-declared path-exclusion concept; the verification harness.
- **Epic 2** — producer repair: the index producer that cannot list post-scoping members, the
  `description:` stamp, the splice defect that corrupts grouped indexes today, and a new `index-add` verb.
- **Epic 3** — enforcement: a corpus drift driver wired into `CHANGE-VALIDATION.md`, the `description`
  schema check, and repair of the drifting bundles.
- **Epic 4** — the doc_lint/OKF ownership boundary document, follow-on filings, and reconcile.

5 epics · 35 issues · 36 edges · 3 gates · 22 success criteria · 7 risks.

## Motivating measurements

- **46 of 48** `doc_lint` checks cannot produce a non-zero exit at `status: complete`; the corpus runs
  1642 findings with `errors: 0`, and **392** are demoted `E`/`W` -> `R`.
- `okf.py reindex` appears in **zero** `CHANGE-VALIDATION.md` rows and **zero** CI steps, and index drift
  had already regressed in every bundle authored after its fix — including, later, this plan's own.
- The two engines overlap on **6 frontmatter keys on 56 files** out of 48 checks and 1105+ documents,
  while **1049 files (94.9%)** are covered for identity frontmatter by OKF and nothing else.

## Scope split

Root-index depth, the `yf-okf-hygiene` skill with its legacy backfill, and the OKF baseline re-pin were
split into **plan-057-james-dixson-9ecf1c** (D-17) on red-team pass 3's recommendation. plan-057 is in
`drafting` behind a predecessor-complete gate and is deliberately not tracked upstream yet.

## Review

Nine red-team passes. Eight found the criteria layer vacuous in a different shape — `-k` filters that are
no-ops in this repo's direct-file test form; criteria expecting an exit code that a *missing* script also
returns; unjudged criteria counted in neither bucket so one green row yields PASS; a backstop that omitted
the script it guarded; a `bash -n` check that detected neither failure mode; a pour directive the
extractor silently truncated at a blank line; sibling artifacts drifted from plan.md with every
instrument green; and a criterion claiming two files while verifying one.

Two CRITICAL defects found during review were filed separately because they affect **every** plan in the
repo, not this one: **#265** (`recheck-criteria` reports PASS on unjudged criteria) and **#266** (the
`## Gates` grammar cannot express `test_class`, so capability gates default to a class that is never run).

## Upstream dispositions

include: #233, #246, #265 · partial: #140, #165, #171, #247 · deferred: #169, #170, #189, #192 ·
exclude: #168, #173, #174, #244

Execution has not started. The epic id will be stamped here at pour (REQ-PLAN-073).

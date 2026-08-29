---
type: Reference
okf_spec: OKF-PLAN
description: "Upstream issue #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine Full untruncated body, snapshotted at triage."
---
# Upstream #189: Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine

- **Number:** 189
- **Title:** Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body

## Summary

Six shipped scripts have **no test file and are referenced by no test anywhere in the repo**. This is the coverage half of the problem; the blind-spot half — suites that exist but assert only structure — is #188.

## Measured census

44 non-test scripts across 16 script directories, 41 test files. Genuinely untested:

| Script | Notes |
| :-- | :-- |
| `skills/yf-beads-init/scripts/beads_init.py` | the `verify`/`repair` engine an always-loaded rule dispatches to, including the wedged-migration repair that runs raw `dolt` commands against a live DB |
| `skills/yf-beads-upstream/scripts/check_gh_direct.py` | **is itself a `CHANGE-VALIDATION.md` check** — an unverified verifier |
| `skills/yf-beads-upstream/scripts/check_prescriptive_push.py` | same |
| `skills/yf-plan/scripts/repair_dangling_epics.py` | a repair tool that mutates the bead DAG |
| `skills/yf-research/scripts/search_api.py` | network-facing |
| `manifest_update.py` | one version, vendored to 4 skills; refreshes the rule hashes preflight checks against |

Four directories have no test file at all: `yf-beads-init`, `yf-optimal-instructions`, `yf-skill-authoring`, and `yf-okf` — though **`yf-okf` is a false positive worth stating**: its `okf.py` is byte-identical to `_shared/okf.py` (`diff -q`), which `_shared/test_okf.py` covers, with `sync.py --check` guarding the parity. The same is true of `yf-plan`'s vendored `doc_lint.py`, `plan_extract.py` and `plan_template.py`. A naive per-directory count reports 5 gaps; the honest number is **6 scripts**, and the vendored copies are covered.

```
$ diff -q skills/yf-okf/scripts/okf.py _shared/okf.py          # identical
$ md5 -q skills/*/scripts/manifest_update.py | sort -u | wc -l # 1 distinct version
```

## Why these six specifically matter

Three of them are **repair or verification tools** — `beads_init.py`, `repair_dangling_epics.py`, and the two `check_*.py` validation checks. A repair tool with no tests is the worst case in the set: it runs against a live database precisely when something is already wrong, and two of the untested scripts *are themselves* the checks that gate other changes. An unverified verifier reports green by default.

`manifest_update.py` is a single implementation vendored four ways, so one defect is four skills' rule hashes.

## Proposed scope

Not "write tests for everything". Prioritise by blast radius:

1. **`beads_init.py`** — the wedged-migration repair path, driven against a scratch Dolt repo. The always-loaded rule already documents its invariants (mode-aware flush, never `reset --hard`, the false-negative invariant on `bd status`); those are the assertions.
2. **The two `check_*.py`** — each needs a negative control: a fixture the check must FAIL on. Per this repo's own doctrine, a check never observed failing is not a check.
3. **`repair_dangling_epics.py`** — a before/after DAG assertion on a fixture bead set.
4. **`search_api.py`** and **`manifest_update.py`** — lower priority; the first is network-facing and needs a stubbed transport, the second is small and deterministic.

Each should ship with #188's identity/round-trip assertions rather than structure-only ones, or this closes the coverage gap and leaves the blind spot.

## Provenance

Measured while resolving #186/#187 into `plan-050-james-dixson-d0414b`; recorded there as **RE-003**. Deliberately **not** folded into plan-050 — that plan is already at review cycle 10 and its scope was narrowed once by a split (D-9) for exactly this reason.

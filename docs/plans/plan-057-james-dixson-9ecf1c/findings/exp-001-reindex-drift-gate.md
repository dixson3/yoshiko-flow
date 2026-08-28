---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-reindex-drift-gate
description: What should the reindex drift gate check, and would it be stable enough to gate on? (D-1's hinge)
---

# Finding: What exactly should the `okf.py reindex --check` drift gate check, and would it be stable enough to gate on?

### Approach Tested

Read `_shared/okf.py` (`reindex_check` ~:1361, `reindex_write` ~:1459, `_cmd_reindex` ~:1564,
`_listing_members` ~:1309, `REINDEX_EXIT` ~:1281) and `plan_manager.py` (`_INDEX_MEMBERS` ~:635,
`_ensure_index_lists_member` ~:784, `seed_index` ~:837). Ran `reindex_check` in-process over all 61
depth-1 bundles; correlated each drifting bundle's `index.md` last-commit date against the
first-commit date of each unlisted subdirectory via `git log --reverse`. Ran determinism (5x),
convergence, and idempotence tests on a `$(mktemp -d)` copy. Probed the CLI exit contract across
clean / drift / no-index / nonexistent-path / marker-imbalance. No repo file was modified.

### Result

**measured:** — the count is 9, not 7. 21 clean / **9 drift** / 31 no-index over 61 bundles. The two
beyond the tracked survey are `plan-056` itself and `docs/research/005-*`, both **untracked** —
`git status --porcelain` shows `??` for each, which is why a tracked-only survey missed them.

**measured:** — every finding is `kind: missing`. Zero `ghost`, zero `empty-dir`, corpus-wide. The
unlisted members are `assets/` (6 bundles), `scripts/` (4), and one-off `findings/`, `references/`,
`reviews/`, `scope-answers.md`, `plan.yaml`.

**measured:** — the producer cause is structural, not incidental. `_INDEX_MEMBERS` is a **closed
10-entry allowlist** that does not contain `scripts/` at all. `_ensure_index_lists_member` — the only
back-fill path — is called from exactly **two** sites, for `plan-retrospective.md` and
`upstream-triage.md` only. `seed_index` emits a member only if the directory **exists and is
non-empty at seed time**, and at scoping `findings/`/`assets/`/`reviews/` are empty or absent.
`git log` confirms the pattern in every case: plan-053's `index.md` was written at the INTAKE commit
`d96c920`; its `assets/` first appears in `2506845`, during Epic 1.

So the producer is *incapable* of listing (a) any member created after scoping, or (b) any member
outside the allowlist — and nothing anywhere re-runs reindex. **measured:** zero `reindex` call sites
outside `okf.py`, its own tests, and prose; zero in `ci.yml`.

**measured:** — false positives are real and exclusions ARE needed. The plan-029 migration-sample
fixtures, which are frozen evidence, drift: `plan-bundle/after` 5 missing (including `plan.md`),
`research-bundle/after` 10 missing, `incubator-bundle/after` 1 missing.

**measured:** — #233 verified, and stronger than filed. There is no `fnmatch` import and no exclusion
machinery anywhere in `okf.py`. Further, **`reindex` has no walk at all** — `_cmd_reindex` takes a
single dir. The recursive walk lives in `check` (`target.rglob("*.md")`, :827) and is likewise
unexcluded: `okf.py check` on plan-029 yields 40 findings, **23 of them from inside the fixture tree**
(58% noise).

**measured:** — gitignore blindness. On a scratch copy, `mkdir __pycache__ && touch scratch-notes.md`
flips a clean bundle to drift. `_listing_members` filters only reserved and dot-prefixed names.

**measured:** — determinism and idempotence are clean. Deterministic across 5 runs; all 9 drifts
converge after one `--write`; a second write is byte-identical; **zero clean bundles are mutated by
`--write` (n=21)**; no prose discarded.

**measured:** — but `--write` degrades index quality. The bullets it adds carry no description:
plan-047 gains a bare `- [assets/](assets/)` where hand-authored bullets carry a cold-reader
sentence. Auto-fix converges to *mechanically* clean, not *portably* clean.

**measured:** — runtime is a non-issue. In-process over all 61 bundles: **11.7 ms**. One CLI
invocation: 52 ms — so a per-bundle shell-out costs ~3.2 s against ~65 ms for a single in-process
walk, a ~50x difference.

**measured:** — the exit contract carries a real defect:

| state | exit | verdict |
|:--|--:|:--|
| clean bundle | 0 | `clean` |
| drifting bundle | 1 | `drift` |
| real bundle with no `index.md` | 2 | `no-index` |
| **path that does not exist** | **2** | **`no-index`** |
| `--write` on unbalanced marker | 1 | `error` |
| **`--check` on unbalanced marker** | **0** | **`clean`** |

`reindex_check` tests only `if not idx.exists()`, which a nonexistent parent also satisfies. The JSON
is byte-identical in shape for both. `--check` never calls `check_markers`, so an index with an
unbalanced `<!-- intro:start -->` reports clean/exit 0 while `--write` hard-errors.

### Implications for Plan

**D-1 is well-supported on the evidence, but the gate as currently constituted would be a nuisance
gate.** All 9 drifts trace to a producer that structurally cannot keep the index current. Shipping
the gate without the producer fix means every future bundle turns red the moment it grows an
`assets/` or `scripts/` directory during execution. **The producer fix must land in the same
change-set, ahead of the gate.**

**D-3 is under-specified in one respect that matters.** For `reindex` there is no walk to give an
exclusion concept to — the plan needs a *new* corpus driver. Only `check` (`rglob` at :827) is a
retrofit.

**The exit-code conflation is a gate-integrity bug, not cosmetic.** This is `doc_lint`'s #181
conflation reproduced in a second engine: `no-index` and `no-such-path` are indistinguishable. Under
D-1, `no-index` is demoted as history — so a typo in a gate row's path yields exit 2, gets demoted,
and **the gate silently checks nothing**. Exit 1 is also overloaded across `drift` and write-mode
`error`, and there is no INCONCLUSIVE code.

### Recommendations

1. **Ship the producer fix first** — add execution-time members to `_INDEX_MEMBERS` and call
   `reindex_write` at intake/execute/close.
2. **Add a corpus driver** (`scripts/checks/check_okf_index_drift.py`), in-process, enumerating bundle
   roots by **depth-1 glob** — never `rglob("index.md")`, which alone excludes all three fixture
   trees — plus doc_lint's exclusion globs as defence in depth. Exit 0 clean / 1 new drift / 2
   INCONCLUSIVE, and **hard-error on a nonexistent enumerated root** so demotion cannot mask a typo.
3. **Wire both FAST and FULL tiers to the same whole-corpus command.** At 12 ms the whole corpus is
   cheaper than per-bundle mapping logic, and scoping to the changed bundle would miss drift
   introduced elsewhere.
4. **Fix the exit contract before gating on it** (SPEC-first: a `REQ-OKF-011` amendment) — distinguish
   `no-such-path`, run `check_markers` in `--check`, and reserve a code for INCONCLUSIVE.
5. **Make the driver gitignore-aware.**
6. **Do not present `reindex --write` as the operator remediation** without a description-authoring
   step.

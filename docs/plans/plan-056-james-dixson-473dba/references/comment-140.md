---
type: Reference
okf_spec: OKF-PLAN
description: "Draft upstream comment for #140 — the root-tier enforcement that shipped in plan-056, and why nested index.md stays out."
disposition: partial
target: "#140"
---
**plan-056 shipped the root-tier half of this. The nested half stays out, on re-measured evidence.**

**What shipped.** `#140` asked for OKF structure enforcement below the bundle root. The measured
leverage turned out not to be nested indexes but a **root** index that stays true as a bundle
grows, plus a gate that actually invokes the checker:

- **`REQ-OKF-CHK-004`** — a corpus index-drift driver (`scripts/checks/check_okf_index_drift.py`),
  now wired into `CHANGE-VALIDATION.md` in **both** the FAST and FULL tiers. Before this,
  `okf.py reindex` appeared in **zero** `CHANGE-VALIDATION.md` rows, **zero** CI steps and **zero**
  `plan_manager.py` call sites. Root-index drift had been repaired nine days earlier and had
  **already regressed in 9 of the 30 index-bearing bundles** — every bundle authored after the
  repair. Nothing noticed. A verb no gate invokes is not enforcement.
- **`REQ-OKF-011` amended** — the `reindex` exit contract goes from three-way to five-way.
  `3 no-such-path` is split out of `2 no-index`, because a corpus driver *must* tolerate `no-index`
  (most bundles have none) and therefore read a **mistyped root as a benign skip**. `4 inconclusive`
  is allocated, and `--check` now runs `check_markers` — until this amendment it did not call it at
  all, so a marker-imbalanced index (the one condition `REQ-OKF-072` calls *unrecoverable*) reported
  **clean, exit 0**.
- **`REQ-PLAN-081`** — `scripts/` added to the execution-time index member set, `reindex_write`
  called at intake / execute-start / close, and a new public `plan_manager.py index-add` verb.
  Index regeneration was measured **unreachable from the CLI**: `seed_index` is callable only from
  `init`, which is how the nine bundles came to drift with no supported repair.
- **The corpus is now clean**: 62 bundles enumerated, 31 carrying a root index, **0 drifting**. All
  8 drifting bundles were repaired with **authored** descriptions, not `reindex --write`'s bare
  bullets — the latter satisfies the gate while degrading the artifact.

**What stays open, and why.** Nested `index.md` generation is **still deferred**, re-scoped through
`#171`. The premise has changed but not enough to reverse the decision: the shipped specs claimed
`description:` was present on **0 of 423** nested files; re-measured 2026-08-28 it is **165 of 983**,
concentrated entirely in the twelve newest bundles. So coverage is real, partial, and a
producer-version artifact — 818 of 983 generated nested entries would still be bare. `REQ-DATA-075`
now makes `description:` a **producer contract**, so coverage grows forward without touching a
frozen bundle. Revisit when it is the common case.

`REQ-OKF-CHK-002` still has no other tracker home, so this issue stays open.

Plan: `docs/plans/plan-056-james-dixson-473dba/`

---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: "Red-team pass 3 — REVISE. 2 blockers: SC17 used a pytest form measured to exit 2 (a criterion that CANNOT PASS), and SC12's path contradicted its producer. Nine pass-2 repairs verified sound by execution."
---
# Red-team pass 3: plan-057-james-dixson-9ecf1c

## Verdict: REVISE

> **All 12 concerns resolved by the main session.** Re-dispatched as pass 4.

**Date:** 2026-08-29 · **Reviewer:** delegated adversarial agent (read-only)

Concern count is falling: **17 → 18 → 12**, and the two blockers here are not pass-2 regressions —
one is a pass-2 repair marked resolved whose criterion was never edited, the other a defect all
three passes had read past.

## Strengths

**Nine of pass 2's repairs verified SOUND by execution:**

- **Issue 1.7's deletion is correct**, and the refutation was re-confirmed by running the real
  producer in a sandbox: it stamps `description:`. No dangling `depends-on: 1.7`, no orphaned
  `Discharged-by`; Issue 1.6's chain intact.
- **SC3's re-freeze reproduces exactly** — 25 names, `described 184 · distinct 58 · repeated 126 ·
  ratio 0.6847826`. And the reviewer went further than pass 2 did: **simulating rule D over the
  frozen set yields 0.3121**, so the target is not merely falsifiable but achievable with a 0.37
  margin. Strongest criterion in the plan.
- **`--require 15` arithmetic independently confirmed** (9 array rows + 6 named).
- **SC0c is implementable** — `test_class` verified as a real bead metadata field round-tripping
  through `bd list -t gate --json` on bd 1.2.2.
- Pour directives parse in full on all three `auto` gates; `unparsed: []`.
- Structural: 29 edges, **no cycles**, all 28 issues covered, all `Discharged-by`/`Resolved By`
  resolve. Counts mutually consistent after two rounds of add/delete.

## Concerns

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| B1 | high | **SC17 used a pytest invocation this repo has MEASURED to be broken — it can never pass.** `uv run --with pytest python3 -m pytest <target> -q` makes `python` the entrypoint, so the target's PEP 723 header is never read. Re-measured on the analogous suite: module form → **exit 2** (`ModuleNotFoundError: No module named 'yaml'`), direct-file form → **0**. Exit 2 is *evaluated*, so it scores FALSE. An anti-vacuity plan shipping a criterion that **cannot pass** — worse than one that cannot fail. | **resolved** — direct-file form; Issue 2.8 now states the suite carries a PEP 723 header and owes a `chmod +x`. |
| B2 | high | **SC12's `--record backfill.json` contradicted Issue 2.4's `assets/backfill.json`.** Pass-2 C10 was marked resolved and the criterion was never edited. Under the repo-root rule the bare path resolves to `<repo>/backfill.json`, which nothing writes. Measured: exit **2**. Identical shape to pass-2's C2, reproduced in the criterion pass 2 was simultaneously repairing. | **resolved** — bundle-qualified, matching SC3's `--frozen-set`. |
| C3 | med | **SC23's `! grep -q 'assess'` was over-broad and in tension with its own issue.** 6 of 9 hits are `assessment`/`assessor`, and D-3 has the new skill *absorb* the verb — so the natural boundary prose reintroduces the substring and the criterion goes permanently red. `agents/assessor.md` was unowned. | **resolved** — replaced with a seventh instrument, `check-assess-verb-gone.sh` (a raw grep with backticks also broke the Verification clause grammar); Issue 3.4 now anchors to the verb and owns the `assessor.md` decision. |
| C4 | med | **SC5's "33 bundles carry nested entries" is wrong — measured 5.** 33 is the count of bundles having an `index.md` *at all*. Pass 2 replaced a stale figure with a different quantity. | **resolved** — 5, named: plan-058 (7), plan-059 (16), research-002 (8), -003 (7), -004 (10). The inherited "6" was approximately right. |
| C5 | med | **`diagrams/` was empty and unindexed — a latent live drift.** An empty directory is invisible to the enumerator, so `drifting: 0` was silence, not safety; the moment anything lands there (and `yf-diagram-authoring`'s convention is `plan_dir/diagrams`) the gate turns `main` red. | **resolved — by removing the directory, not indexing it.** Indexing it first produced `empty-dir: 1`, the inverse defect: the driver reports an indexed-but-empty directory. Removing it also removes the latency, since a future `diagrams/` arrives with files and is caught by the `missing` check. |
| C6 | med | **SC21 and SC19b read INCONCLUSIVE, not FALSE** — the only two criteria invoking a not-yet-existent script *bare*. 126/127 map to `inconclusive`, counted in neither bucket, violating R11's own third rule. | **resolved** — prefixed with `bash `, which exits 1. (Verified: a `uv run` prefix exits 2, also evaluated.) |
| C7 | med | **SC3 stated the baseline but never the COMPARATOR.** A `<=` implementation is satisfied by zero change — this plan's own defect class one abstraction layer down. | **resolved** — strict `<`, exit 1 on not-lower, exit 2 reserved for an unreadable frozen set, stated in both Issue 1.0 and SC3. |
| C8 | low | SC1's "verbatim" quote went stale from pass 2's own deletion: 24 → **23**. | **resolved**. |
| C9 | low | **R11's `yf --version == HEAD` is stale a third time** (`ad6acc7` vs HEAD `298dd03`) — though the substance holds: `HARNESS_INCOMPLETE` 4 in both, `cmp` byte-identical. The benign case AGENTS.md documents. | **resolved** — the durable test is now stated as the `cmp`, not the version equality. |
| C10 | low | The Motivation asserted the 276/257/127/142 triple that SC3 declares unreproducible. | **resolved** — annotated as the pre-rule 2026-08-28 measurement. |
| C11 | low | Issue 1.5's "45 authored descriptions" — measured **62** across 20 `assets/` directories. | **resolved**. |
| C12 | low | `check-gates-poured-probe.sh`'s RED fixture is materially harder than the others (needs a beads DB, not just a filesystem sandbox) and Issue 1.0 did not say how to build it. | **resolved** — construction stated: `bd init` plus `bd create -t gate --metadata '{"test_class":"manual"}'`, verified to round-trip on bd 1.2.2. |

## Missing

- **A producer↔consumer path check.** B2 is "an issue writes X, a criterion reads Y"; pass-2's C2 was
  the same shape. One grep asserting every path literal in the Verification column is either an
  existing file or a path some issue names would have caught both.
- **A `plan.md` ↔ instrument-output diff.** Named as missing in pass 2 and still not added; it cost
  C8 this pass and C3/C12/C14 last pass.
- **An empty-directory sweep.** C5 was invisible to every instrument the plan runs. `find <bundle>
  -type d -empty` is the whole check.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start | OK |
| Predecessor complete | **Sound** — `probe`+`worktree` parse in full |
| Backfill authorization | **Sound.** Still the best gate in the plan |
| Upstream network reachable | **Sound** — evidence outside `Blocks` |
| Verification harness ready | **Sound** — arithmetic independently re-derived; exits 1 today |
| Reconcile | OK |

`gate_consistency.py` PASS, 6 gates. No cycles over 29 edges, no frontloading miss, no gate's
evidence produced inside its own `Blocks`.

## Upstream Assessment

Unchanged and defensible. `verify-reconcile` → exit 1, `"4 of 6 upstream row(s) did not reach the end
state"` — expected pre-execution, discharged by 3.5. All seven reference bodies carry `description:`,
re-confirmed against the live producer, so Issue 1.7's deletion stands.

---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #359 - Plan 2/3 (part 2): run the yf-okf-hygiene corpus
  backfill — 8 legacy-readme bundles, on the repaired engine'
---
# Upstream #359: Plan 2/3 (part 2): run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles, on the repaired engine

- **Number:** 359
- **Title:** Plan 2/3 (part 2): run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles, on the repaired engine
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

**Prerequisite: #294 and the plan-064 engine repairs are landed** — commit `30fcbab`,
`plan-064: repair the yf-okf-hygiene backfill/restore engine`. This issue carries #316's
original acceptance criteria, which plan-064 deliberately did **not** discharge.

## Why this is a separate issue

plan-064's EXP-001 measured that the transform **could not run**: 8/8 target bundles halted, and
the advertised rollback (`restore`) destroyed data on three paths while reporting `pass` and
exiting 0. A plan claiming `legacy: 0` while the engine halts 8/8 would have been asserting a green
it never measured. So plan-064 repaired the instrument and handed the corpus transform here.

## The starting measurement (post-repair, dry run only)

Run over `docs/plans` + `docs/research`, `--maxdepth 2`:

| Run | checked | would-backfill | halted | halt profile |
| :-- | --: | --: | --: | :-- |
| default | 69 | 0 | **8** | `objective-divergence` ×7, `phase-log-loss` ×1 |
| `--reconcile-objective` | 69 | **7** | **1** | `phase-log-loss` ×1 |

**7 of 8 now clear.** The one remaining halt is `docs/plans/plan-030-james-dixson-65526e` on
`phase-log-loss` — a guard protecting the single measured data-loss mode. **Do not wave it
through**; it needs its phase log reconciled by hand first.

`plan-030` is also the proof `REQ-OKFH-011` landed: EXP-001 measured it *clearing* the dry run and
then halting under `--apply`. The dry run now reports that halt without applying anything.

## Acceptance criteria — VERBATIM from #316

Quoted exactly, so nothing is lost in transcription:

> - `okf_hygiene.py audit` reports `legacy: 0` across all roots.
> - The `restore` path has been exercised on a real bundle and shown to reverse cleanly.
> - `okf-index-drift` green in the FULL tier over the merged tree.
> - Any bundle the engine could not transform is reported explicitly rather than silently skipped.

**`verdict: pass` is NOT the acceptance signal**, as #316 itself says: `audit` is read-only
classification, so `pass` means *the classification succeeded*. The actionable number is
`legacy: N`.

**And `warn` is not a failure signal either** (plan-064 Issue 4.6, new information). The audit
verdict is a **saturating label**: it returns `warn` whenever the report contains at least one
`[warn]` line, so one residual finding reads identically to fifty. Measured across the transform
it stayed `warn` → `warn` while per-bundle findings fell **13→2 (-85%)**, **17→2 (-88%)** and
**52→33 (-37%)**. Use the per-bundle **finding count**, before and after — not the verdict.

### The 8 target bundles (unchanged since #316's audit)

| Bundle | default | `--reconcile-objective` |
| :-- | :-- | :-- |
| `docs/plans/plan-010-james-dixson-73eebd` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-012-james-dixson-a99822` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-013-james-dixson-0af2f8` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-014-james-dixson-916de2` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-021-james-dixson-bb3558` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-023-james-dixson-b618bb` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-026-james-dixson-6e0e2f` | halt: `objective-divergence` | `would-backfill` |
| `docs/plans/plan-030-james-dixson-65526e` | halt: `phase-log-loss` | **halt: `phase-log-loss`** |

## The rehearsal method (plan-064 D3)

`backfill` has no per-bundle selector (only `--root`), so a per-bundle rehearsal needs its own root.
Copy a real legacy bundle into `$(mktemp -d)`, `git init` + commit it, run
`backfill --apply --record`, then `restore --record --apply` and diff. plan-064 ran exactly this as
EXP-001; it is what refuted the original premise.

## The rollback route (plan-064 D10) — read this before running `--apply`

**For a committed corpus the rollback is `git revert`, not `restore`.** All 8 targets are tracked
and committed, which is the path EXP-001 measured **byte-exact**. `restore` is now genuinely
record-driven and refuses on all three loss paths, but `git revert` of the backfill commit remains
the simpler and stronger reversal for this specific run.

## Engine capabilities now available (plan-064)

- `--reconcile-objective` — `plan.md`'s H1 is authoritative for a divergent legacy `>` line;
  **opt-in**, rewrite reported per bundle, halt retained as default.
- The dry run is **predictive of apply** (`REQ-OKFH-011`) — every halt apply evaluates, it evaluates.
- `--record` is **versioned** and carries the **per-path operation list** (created/deleted/modified
  + sha256). `restore` consumes it and **refuses** an unversioned record.
- `restore` refuses on: non-git tree, bundle untracked at `HEAD` (neither overridable), and dirty
  relative to post-backfill state (`--force` only). `--bundle` filters a batch.
- `recover` is a **CLI verb**, and `backfill` **refuses over a stale journal**.
- The transform stamps `description:` (`REQ-DATA-075`) and the member walk is gitignore-aware
  (#294), so a backfilled `index.md` cannot acquire permanent `ghost` findings.

## Known unknowns still open (plan-064 R8)

The three surfaces EXP-001 had not tested were probed and settled:

- **`_index.md` route** — genuinely broken under the `yf-plan` member (manufactures a
  `hybrid-partial` and halts). **Blocks nothing here**: zero of the 8 targets are `_index.md`.
  Filed separately.
- **`hybrid-partial`** — **no** target classifies as one. Population is `{conformant: 61,
  legacy-readme: 8}`.
- **Partially-halted batch** — the record contains entries for **mutated bundles only**; halted
  bundles were never touched.

Evidence: `docs/plans/plan-064-james-dixson-a0b7fa/findings/exp-004-post-repair-halt-profile.md`


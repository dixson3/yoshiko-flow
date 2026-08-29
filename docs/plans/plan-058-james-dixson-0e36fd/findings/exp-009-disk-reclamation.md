---
type: Finding
okf_spec: OKF-PLAN
id: EXP-009
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Issue 4.1b — the 785 MB measured properly, and what was actually reclaimed

The plan required this issue's **first act be a real breakdown** rather than `du -sh`, because an
earlier draft asserted two reclamation wins without inspecting the directory and both were wrong or
overstated. Here is the breakdown, then what was done.

## Approach Tested

**measured:** produced a real per-subtree breakdown of `.beads` before touching anything (the plan
required this issue's first act be a breakdown rather than `du -sh`), verified four independent
safety preconditions, then reclaimed the one candidate the operator authorized using a
quarantine-verify-delete sequence rather than a direct `rm -rf`.

## Result

### The measured breakdown (before)

| Path | Size | What it is |
| :-- | --: | :-- |
| `.beads` **total** | **784 MB** | |
| `.beads/dolt/…/.dolt/noms/oldgen` | 341 MB | **already-archived** `.darc` chunks |
| `.beads/backup` | 308 MB | 118 `.darc` archives — the **sole local Dolt replica** |
| `.beads/dolt/…/.dolt/git-remote-cache` | **118 MB** | two cache dirs, mtimes 2026-06-01 / 2026-06-20 |
| `.beads/dolt/…/.dolt/noms/vvvv…` | **11 MB** | the live journal |
| `.beads/issues.jsonl` | 1.4 MB | JSONL export |
| `.beads/interactions.jsonl` | 948 KB | transition history (Issue 4.4) |

### Candidate (a) — `git-remote-cache`: RECLAIMED, 118 MB

**Operator-authorized 2026-08-28.** Four independent checks established it was safe *before*
anything was touched:

1. `bd status --json` healthy — inspected for an **`error` key**, not an exit code (the
   false-negative invariant).
2. `.beads/backup` present and current — **118 `.darc` archives, 308 MB**. DR coverage intact,
   which is *why* this sequencing is safe and must not be reordered ahead of Issue 4.1d.
3. `repo_state.json` carries **`"remotes": {}`** — there is no remote for this cache to be
   serving.
4. The Dolt **manifest contains zero references** to `git-remote-cache`.

**Method: quarantine, verify, then delete** — not a direct `rm -rf`. The directory was `mv`d aside,
`bd status` / `bd list` / `bd ready` were all re-run against the store with it absent, and only
then was the quarantined copy removed. Had anything failed it was one `mv` from restored.

| | Before | After |
| :-- | --: | --: |
| `.beads` total | 784 MB | **666 MB** |
| `bd status` | healthy | healthy (no `error` key, 2,079 issues) |
| `bd list --all` | 1,905 rows | 1,905 rows |
| `.beads/backup` | 118 archives | **118 archives** |

**118 MB reclaimed — 15% of the directory — with no bead content deleted and DR coverage
unchanged.**

### Candidate (b) — Dolt GC: NOT RUN, and the hypothesis is weaker than the plan assumed

The plan framed GC as "a hypothesis, not a remedy" and bounded any win "at roughly the 105 MB
journal". **That bound was wrong by an order of magnitude in the plan's own favour.** Measured, the
journal is **11 MB**; 341 MB of the 353 MB `noms` tree is *already archived* `oldgen`, which GC does
not reclaim because `main`'s history is reachable.

So the realistic upside is **~11 MB — 1.4% of the directory** — in exchange for stopping a live
`dolt sql-server` against the store this plan's own beads are tracked in. **The operator declined
this half, and the measurement supports the decision**: the cost/benefit is not close.

Recorded as a *tested hypothesis with a measured bound*, which is what the issue asked for — not as
an untried idea.

### Candidate (c) — `.beads/backup`: CONSENT-GATED, not reclaimed

308 MB, 118 manifest-referenced `.darc` archives, registered in `repo_state.json` as the backup
destination `backup_export`, with `dolt.local-only = true`. **It is the repository's sole local Dolt
replica.** Nothing in it is individually rotatable; the only available operation is destroying the
whole DR copy. That is Issue 4.1d, behind the Pruning Authorization gate — and the operator accepted
**"not warranted yet"**, so it stands.

## Implications for Plan

### Why this issue was correctly placed OUTSIDE the consent gate

It carries the evidence that gate's Condition depends on, and **a gate cannot block its own
evidence**. Because `Blocks` operates on whole beads, a prose carve-out inside a single issue would
have been unenforceable at bead granularity — which is why the destructive half is a separate issue
(4.1d) rather than a paragraph in this one.

## Recommendations

1. **Keep `.beads/backup`.** It is the sole local Dolt replica; deleting it trades all local DR
   coverage for 39% of the directory.
2. **Do not pursue Dolt GC** on the current evidence — the upside is ~11 MB, an order of magnitude
   below the plan's own estimate, against stopping a live `sql-server`.
3. **`git-remote-cache` is worth re-checking periodically** — it regrew to 118 MB unattended and
   nothing references it from the manifest.

## Evidence

**measured:** `du -sh` per subtree before and after; `bd status --json` inspected for an `error`
KEY (not an exit code); `bd list --all --json` row count and `bd ready` re-run with the cache
absent; `repo_state.json` read for `remotes` and `backups`; `grep` over the Dolt manifest for
`git-remote-cache` (0 hits); `.beads/backup` archive count before and after (118 both times).

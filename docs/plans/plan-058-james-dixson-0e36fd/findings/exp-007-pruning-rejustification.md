---
type: Finding
okf_spec: OKF-PLAN
id: EXP-007
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Issue 4.1 — the pruning justification, re-measured on its own grounds

EXP-006 refuted the row-count-drives-size premise before execution. This re-tests the
**remaining** premises with #268's cost removed, as Issue 4.1 requires — and it is explicitly
authorized to return **"not warranted yet"** as a complete outcome.

Measured in the execution tree against the live store.

## Approach Tested

**measured:** re-ran the four justifications Issue 4.1 names — DB size, query latency post-Epic-1,
cognitive load, backup cost — against the live store in the execution tree, with #268's cost already
removed by Epic 1. EXP-006 had already refuted the row-count-drives-size premise before execution;
this tests the rest.

## Result

### The four grounds, one at a time

### 1. DB size — the premise is REAL, the proposed remedy still is not

| Path | Size | What it is |
| :-- | --: | :-- |
| `.beads` **total** | **782 MB** | |
| `.beads/dolt` | 472 MB | the live Dolt store |
| ├─ `.dolt/noms/oldgen` | **341 MB** | **already archived** `.darc` chunks |
| ├─ `.dolt/git-remote-cache` | **118 MB** | two cache dirs, mtimes **2026-06-01** and **2026-06-20** |
| ├─ `.dolt/noms/vvvv…` (journal) | **11 MB** | the live journal |
| └─ everything else | ~2 MB | manifest, idx, stats, config |
| `.beads/backup` | **308 MB** | **126** `.darc` archives — the sole local Dolt replica |
| `.beads/issues.jsonl` | 1.4 MB | the JSONL export |
| `.beads/interactions.jsonl` | 948 KB | transition history |

**Deleting rows cannot reclaim this, and the reason is structural**: the space is *version
history*, and a `DELETE` in Dolt is **another commit** — it grows the store. That is the whole of
the honest argument, and it is narrower than the earlier "bead content is only 0.18%" gloss, which
was a category error (`.beads/dolt` and `.beads/backup` are *entirely* bead-derived).

**One number moved materially against the plan's estimate.** The plan bounded a Dolt-GC win "at
roughly the 105 MB journal". Measured here the journal is **11 MB**, not 105 MB — 341 MB of the
353 MB `noms` tree is *already archived* `oldgen`. So the GC hypothesis is bounded an **order of
magnitude lower** than the plan supposed. This weakens the GC case further; it does not rescue the
pruning case.

### 2. Query latency post-Epic-1 — the premise FAILS

| Query | Wall clock |
| :-- | --: |
| `bd list --all --json` (all 1,905 beads) | 0.200 s / 0.181 s / 0.188 s |
| `bd ready --json` | 0.154 s |

A full-universe read is **~0.19 s**. There is no latency problem to solve by pruning. Whatever was
slow was `upstream.py`, and Epic 1 fixed it — 334 s to 1.17 s — **without deleting a single row**.
This is the ground on which the pruning proposal was most plausible, and it does not survive
measurement.

### 3. Cognitive load — the premise is REAL and the operator's instinct is CONFIRMED

| Status | Count | Share |
| :-- | --: | --: |
| closed | 1,833 | **96.2%** |
| open | 70 | 3.7% |
| in_progress | 2 | 0.1% |

96% of the universe is closed, and research-005 measured the analytical value of retained bead
*transition* history at **literally zero**. The instinct that most of this is dead weight is
correct. What does not follow is that **deleting rows from Dolt** is the remedy.

### 4. Backup cost — real, and it is the DR trade, not a free win

`.beads/backup` is 308 MB across **126** `.darc` archives. `repo_state.json` registers it as a
Dolt **backup destination** (`backups.backup_export`) with **`remotes: {}`**, and
`bd config get dolt.local-only` returns **`true`**. So it is the repository's **sole local Dolt
replica**, content-addressed rather than dated snapshots — nothing in it is individually
rotatable. Reclaiming it means destroying the whole DR copy. That is Issue 4.1d, and it is behind
the consent gate for exactly this reason.

## The purge predicate the operator proposed, re-counted

"Closed AND upstreamed" selects **53 of 1,905** rows (87 beads carry an `external_ref` at all;
53 of those are closed). The plan predicted 52 of 1,764 — same conclusion, one row apart.

The cause is not accidental: `AGENTS.md` **mandates coarse granularity** — one tracking issue per
plan-scale effort — so sub-beads never receive an `external_ref` *by design*. The predicate selects
2.8% of the universe, and those 53 rows are **exactly the rows `closable` reads** (REQ-BUP-052),
so purging them breaks that verb by construction. Issue 4.3 owns that conflict.

## Implications for Plan

### Verdict: NOT WARRANTED YET

Of the four grounds, **one fails outright** (latency), **one is real but has no row-deletion
remedy** (size), **one is real and confirms the instinct without supporting the mechanism**
(cognitive load), and **one is a genuine DR-versus-space trade for the operator, not an
engineering finding** (backup).

Nothing here justifies a destructive prune of bead content. Recorded as a complete, satisfying
outcome per Issue 4.1's own authorization — not as a deferral.

**What IS warranted, and is non-destructive to bead content:** the 118 MB `git-remote-cache`
reclamation (Issue 4.1b), and the `interactions.jsonl` question (Issue 4.4), which is 948 KB of
clone-local, gitignored transition history whose analytical value research-005 measured at zero.

## Recommendations

1. **Close Epic 4 with "not warranted yet"** — the gate's Instructions name this an acceptable
   resolution that closes the epic with no code change.
2. **Proceed with Issue 4.1b's `git-remote-cache` reclamation**, which is non-destructive to bead
   content and sits outside the consent gate by design.
3. **Do not implement a purge predicate** until the `closable` conflict (Issue 4.3) is resolved —
   the naive predicate's selection set *is* `closable`'s input set.

## Evidence

**measured:** `du -sh` over `.beads` and its subtrees; three timed `bd list --all --json` runs and
one `bd ready`; `bd list --all --json` parsed for status distribution and `external_ref` population;
`repo_state.json` read directly; `bd config get dolt.local-only`. All in the execution tree on
2026-08-28.

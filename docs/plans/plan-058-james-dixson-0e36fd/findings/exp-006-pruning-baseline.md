---
type: Finding
okf_spec: OKF-PLAN
id: EXP-006
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-006: Issue-database pruning — baseline measurement

**Question (operator-added scope).** Most of the 1,801 beads are closed; once a plan has resolved
them and the resolutions are upstreamed they have no further local value. Should
`yf-beads-hygiene` gain a pruning capability, and should beads become wisp-like post-resolution?

## Approach Tested

1. Censused the live bead universe: status distribution, `external_ref` population, and
   `close_reason` presence and length.
2. Tested the operator's stated purge predicate ("closed AND upstreamed") directly against that
   census rather than assuming its selectivity.
3. Measured `.beads` on disk, broken down by subdirectory, to test the DB-size justification.
4. Read `load_universe_rows`'s docstring and REQ-BUP-052 to find shipped features that depend on
   closed rows being present.
5. Checked `AGENTS.md`'s upstream-granularity and memory-tier rules for constraints the proposal
   interacts with, and research-005's telemetry result for evidence *supporting* it.

## Result

**The intuition about the POPULATION is right; three of the four supporting premises do not
survive measurement.** Scoped as a separate epic whose first act is to finish the justification,
with implementation gated on the answer — and explicitly *not* gated to the #268 fix.

### 1. CONFIRMED — the population is overwhelmingly closed

| status | count |
| :-- | --: |
| closed | **1,764** |
| open | 37 |
| **total** | **1,801** |

98% closed. The live working set is 2% of the database.

### 2. CORRECTED — the purge predicate selects 3% of what it appears to

| predicate | selects |
| :-- | --: |
| closed | 1,764 |
| **closed AND has `external_ref`** | **52** |
| any `external_ref` at all | 84 |

"Closed and upstream-paired" would purge **52 beads, not ~1,700**.

**The reason is structural, not accidental.** `AGENTS.md` mandates **coarse** upstream
granularity — *"File ONE tracking issue per plan-scale effort ... NOT one per execution bead"*. So
execution sub-beads never receive an `external_ref` **by design**. "The resolutions are
upstreamed" is true at the **plan** level and false at the **bead** level, and the bead-level
pairing the predicate depends on does not exist.

Any workable predicate must key on something else — the parent epic's upstream pairing, or
plan-bundle closure. That needs designing, not assuming.

### 3. HARD CONSTRAINT — purging closed rows breaks a shipped feature

`load_universe_rows`'s docstring (`upstream.py:506-520`) records this explicitly:

> "`cmd_closable` depends on closed rows being present — an issue is closable precisely when its
> mapped beads are closed, so filtering them out here would make every issue read as not-closable
> (REQ-BUP-052)."

Any pruning design must state what happens to `closable`, or rework it in the same change. Note
the interaction with the previous point: the 52 closed-and-mapped beads are *precisely* the rows
`closable` reads. The operator's predicate selects **exactly the rows the feature depends on**.

### 4. VALUE AT RISK — `close_reason` is decision rationale, not a tombstone marker

| | |
| :-- | --: |
| closed beads carrying a `close_reason` | **1,763 of 1,764** |
| total `close_reason` prose | **483,869 chars** |
| median length | 149 chars |
| **longer than 200 chars (substantive)** | **745** |
| longer than 1,000 chars | 75 |

**42% of closed beads carry substantive close-out prose.** Sampled, one is a 28-line DESCOPED note
recording a refuted measurement, a corrected worklist and a pointer to a split proposal. `AGENTS.md`'s
memory tier places exactly this class in the **durable** tier, not clone-local ephemera.

> **AMENDED after review (pass-2 D3/D6, pass-3 H3).** Two claims derived from this finding were
> later refuted by direct inspection, and a third target it missed was found. Read §5 with these:
>
> - **`.beads/backup` (289 MB) is NOT rotatable.** `repo_state.json` registers it as a Dolt **backup
>   destination** with `remotes: {}`; all **109** `.darc` archives are manifest-referenced and bd
>   syncs it continuously. It is the repository's **sole local Dolt replica**, so the only available
>   operation is destroying the whole DR copy — a consent-gated trade, not a freebie.
> - **Dolt GC is a hypothesis, not a remedy.** It reclaims *unreachable* chunks; `main` history is
>   reachable, the store is already archived (bounding any win near the 105 MB journal), and a live
>   `sql-server` must be stopped first.
> - **`git-remote-cache` is 118 MB — 15% of the total — and this finding MISSED IT.** Two cache
>   directories untouched since June; the one genuinely safe reclamation target. Its absence here is
>   why the plan's Issue 4.1b now begins by *measuring* the tree rather than reasoning from
>   `du -sh .beads/*`, which is all this experiment did.

### 5. DECISIVE — the size justification does not survive first contact

| path | size |
| :-- | --: |
| `.beads` total | **785 MB** |
| `.beads/dolt` | 494 MB |
| `.beads/backup` | 289 MB |
| `.beads/issues.jsonl` (the actual bead content) | **1.4 MB** |
| `.beads/interactions.jsonl` | 872 KB |

**measured: the live bead content is 1.4 MB of a 785 MB directory — 0.18%.** The size is Dolt version
history and backups, not rows. Deleting 1,700 rows removes ~1.3 MB of JSONL and, because Dolt is
a versioned store where a DELETE is a *new commit*, would **add** history rather than remove it.

*(Stated as the measurement plus the structural property of Dolt. Whether a prune actually grows
`.beads/dolt` is the epic's first experiment — but no plausible outcome makes 1.4 MB the cause of
785 MB.)*

### 6. The reframing that governs the epic

**Pruning must not inherit #268's justification.** Once the one-call rewrite lands, 1,801 beads is
no longer slow — EXP-002 measures the edge derivation at **0.0018 s** over the full universe. The
fan-out was the cost; the row count never was. Pruning must therefore justify itself on its own
grounds — DB size (refuted above), query latency (measured: `bd list --all --json` is 0.29 s),
cognitive load, backup cost — each measured separately.

Deleting 1,700 rows of institutional history to fix a performance problem that a one-call rewrite
already fixed would be a bad trade. **"Not warranted yet" is an acceptable and possibly correct
outcome of this epic**, and the epic is written so that outcome requires no further work.

### 7. Evidence FOR the operator, in fairness

research-005's execution-telemetry cluster mined bead history across the corpus and nominated
**zero** thrash episodes; content-level bead reopens were **0**. The analytical value of retained
bead **transition** history is measured and low. That argues the *transitions*
(`.beads/interactions.jsonl`, 872 KB, clone-local and gitignored) are prunable even where
`close_reason` prose is not — a much narrower and better-supported target than the row purge.

### 8. Safety posture (requirements, not options)

`yf-beads-hygiene` is read-only-first with gated repair; keep that. Any prune must be
**export-first**, use **reversible tombstones**, and sit behind an **explicit operator gate**.
Routing is correct as the operator states it: graph **content** is `yf-beads-hygiene`'s axis;
`yf-beads-init` owns config/DB health and is not the right home.

## Implications for Plan

- The epic is **real work with an open question**, not a formality: the population intuition is
  correct and the operator's underlying instinct — that 98% of the DB is inert — is confirmed.
  What fails is the specific predicate, the size rationale, and the assumption that bead-level
  upstream pairing exists.
- **inferred:** because the size argument is refuted *before the epic starts*, the epic's first
  issue must re-establish a justification on other grounds or honestly conclude "not warranted
  yet". Writing it any other way would let a refuted premise drive an irreversible deletion.
- Sequencing it last and off the critical path is a requirement, not a courtesy: the #268 fix is
  blocking a mandated workflow and must not wait on a destructive-change debate.
- The narrow target (transition history) and the broad target (row purge) have **very different**
  evidence behind them and should not be decided together.

## Recommendations

1. Scope pruning as its own epic, **separable**, with no Epic 1-3 issue depending on it.
2. Make its first issue a re-measurement on grounds other than size, explicitly authorized to
   return **"not warranted yet"** as a satisfying outcome.
3. Design the predicate from scratch — parent-epic pairing or plan-bundle closure — since
   bead-level `external_ref` does not exist by design.
4. Require the `closable` conflict to be resolved *in the design*, not discovered in
   implementation: the 52 rows the naive predicate selects are exactly the rows `closable` reads.
5. Preserve `close_reason` unconditionally, and evaluate the far better-supported narrow target
   (`.beads/interactions.jsonl`) separately.
6. Gate any prune behind a **human consent gate**, with export-first and reversible tombstones as
   requirements. A green measurement is not authorization.

## Evidence

- `bd list --all --json` over 1,801 rows (status, `external_ref`, `close_reason` census)
- `du -sh .beads/*`
- `skills/yf-beads-upstream/scripts/upstream.py:506-520` (the `closable` constraint, verbatim)
- `AGENTS.md` — "Upstream Tracking" (coarse granularity) and "Memory" (durable tier)
- `docs/research/005-thrash-detection-and-operator-judgement/` (zero-signal telemetry result)

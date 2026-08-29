# Issue 4.4 — `interactions.jsonl`, the narrower and better-supported target

The plan named this the "narrower, better-supported target" than pruning bead rows. Measured, it
is better-supported and **also not worth doing** — for a reason the plan did not anticipate.

## What it is

| Property | Value |
| :-- | :-- |
| Size | **929 KB** |
| Records | 1,767 lines |
| Fields | `actor`, `created_at`, `extra`, `id`, `issue_id`, `kind` |
| Tracked? | **No** — gitignored via `.git/info/exclude` (`.beads/`) |
| Scope | **clone-local**; absent from the JSONL export, never synced upstream |
| Analytical value | **zero**, measured by research-005 |

Every premise the plan asserted about it holds: clone-local, gitignored, and analytically
worthless.

## Why deleting it is still not worth doing

**929 KB is 0.12% of the 782 MB.** The file is safe to delete and reclaims **nothing that
matters**. It is the smallest of the three reclamation candidates by roughly two orders of
magnitude:

| Candidate | Size | Share of `.beads` | Risk class |
| :-- | --: | --: | :-- |
| `git-remote-cache` | 118 MB | 15.1% | safe, regenerable (Issue 4.1b) |
| `.beads/backup` | 308 MB | 39.4% | **consent-gated** — sole local Dolt replica (Issue 4.1d) |
| `interactions.jsonl` | 929 KB | **0.12%** | safe, clone-local, worthless |

So the honest recommendation is: **leave it.** Deleting it trades a non-zero (if small) chance of
losing a future diagnostic for 0.12% of the directory. That is not a good trade, and "it is safe
to delete" is not the same claim as "it is worth deleting".

## `close_reason` — preserve UNCONDITIONALLY, and the number is larger than the plan said

The plan required `close_reason` prose be preserved unconditionally, citing 745 closed beads with
more than 200 characters of it. Re-measured:

| Metric | Plan | Measured now |
| :-- | --: | --: |
| Closed beads carrying a `close_reason` | — | **1,833** |
| …with **>200 chars** | 745 | **804** |
| Total `close_reason` prose | — | **513 KB** |

**513 KB of `close_reason` prose is the single most valuable thing in the store**, and it is
*more* than half the size of the entire `interactions.jsonl` file being considered for deletion.
It is the durable institutional memory R6 exists to protect: the *why* of 1,833 decisions,
written at the moment the decision was made.

Note the asymmetry this exposes: the transition history (**worthless**, 929 KB) and the close
reasons (**the most valuable content in the DB**, 513 KB) are almost the same size. Any purge
predicate that reasons about volume rather than content would treat them identically. That is a
concrete argument for Issue 4.2's predicate being content-aware, and it is why "preserve
`close_reason` unconditionally" must be a hard constraint rather than a default.

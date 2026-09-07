`/yf-okf-hygiene` is the **corpus** layer of OKF health. [yf-okf](/skills/yf-okf/) answers *"is **this** bundle conformant?"*; this skill answers *"which bundles exist in this repository, what state is each one in, and how do I move the whole population forward safely and reversibly?"* It owns the population; `yf-okf` owns the single bundle and supplies the per-bundle engine this skill calls.

Every single-bundle verdict reported here is the engine's own verdict, surfaced at population scale. If the two ever disagree about one bundle, `yf-okf` is right and this is a defect here.

## When it fires

`/yf-okf-hygiene` is **operator-invoked**. It never fires on an ordinary file edit — there is no hook and no companion rule. Invoke it to:

- ask which bundles in a repository are still legacy, and how many;
- backfill legacy plan or research folders to the reserved `index.md` + `log.md` + frontmatter model, at corpus scale;
- repair a bundle's index listing;
- undo a backfill.

Skip it when you are checking or migrating **one** bundle — that is [yf-okf](/skills/yf-okf/), which owns the per-bundle engine. Verifying that already-written docs *agree* across declared edges is [yf-drift-check](/skills/yf-drift-check/), and running a repo's build/test/lint recipe is [yf-change-validation](/skills/yf-change-validation/). Both are orthogonal axes this skill never invokes.

## The layer boundary, stated

The two OKF skills have adjacent names, so the split is written down rather than left to inference. It is a **layer** boundary, not a feature split:

| Question | Skill |
| :-- | :-- |
| Is *this one bundle* conformant? | `yf-okf` |
| *Which* bundles exist here, and what state is each in? | `yf-okf-hygiene` |
| Move *the whole legacy population* forward, reversibly | `yf-okf-hygiene` |
| Own the `OKF-*` spec family | `yf-okf` |

## Subcommands

| Subcommand | Purpose |
| :-- | :-- |
| `audit [--root R]...` | read-only discovery and classification; writes **nothing**, on any path |
| `assess [--root R]...` | a declared **alias** of `audit` |
| `backfill [--apply]` | the three-step legacy transform; **dry-run by default** |
| `reindex <bundle>` | index repair; **refuses** a legacy prose index — that is backfill's job |
| `restore --record <p>` | record-driven reversal, with a per-path operation kind |
| `recover [--apply]` | finish or roll back an **interrupted** backfill; dry-run by default |

`assess` being an alias is deliberate. `yf-okf` once advertised an `assess` verb its engine never dispatched; the capability it described — discover bundles under a root, report per-bundle impact, mutate nothing — *is* `audit`. Re-advertising it here as a third distinct verb would have moved the defect one directory over rather than deleting it.

## What `audit` classifies

Read-only. Each discovered bundle lands in exactly one class:

| Class | Meaning |
| :-- | :-- |
| `conformant` | has `index.md`, no legacy index |
| `legacy-readme` | `README.md`, no `index.md` |
| `legacy-underscore-index` | `_index.md`, no `index.md` |
| `hybrid-partial` | **both** — a halt class, never transformed |
| `unclassifiable` | no member marker, or unreadable |

`unclassifiable` never collapses into a neighbour. Folding it into `conformant` would certify what was never read; folding it into a legacy class would manufacture work. Two different facts do not share one signal.

## Why `backfill` is three steps and not one

The transform is **migrate → delete the renamed legacy index → regenerate the listing**, never `migrate` alone. Measured on a real bundle, a bare `migrate` takes the portability audit from `pass` to **`fail`**: it stamps `plan.md` frontmatter and leaves the renamed README's prose in `index.md`, which `reindex --write` cannot repair.

`backfill` is **dry-run by default** and `--apply` is consent-gated, because it rewrites bundles in place.

## Crash recovery, precisely

The swap is **two renames with a window in which the bundle is absent** — `os.rename` onto a non-empty directory raises `ENOTEMPTY`, so it is crash-recoverable by mechanism and **not atomic**. Recovery keys on a durable per-bundle journal fsynced *before* each operation, never on directory presence, which cannot tell an early state from a late one.

The journal's invariant is that the **recorded phase is always at or ahead of the physical phase**. Every phase is written before the operation it names, so the record is an over-approximation: recovery may believe more has happened than has, never less. Every recovery branch therefore tolerates a physical phase one step behind its recorded phase — a branch that assumed its named operation had completed would be a data-loss path under this very invariant.

Staging happens **inside the repository tree**, never in a system temp dir: cross-filesystem staging turns the rename into a copy and voids every durability claim above.

`recover` is an operator-invocable verb, and `backfill` **refuses** over a stale journal rather than staging on top of a half-finished swap. It does not auto-recover — recovery moves directories, and doing that as a silent side effect of an unrelated invocation is exactly the surprise `--apply` is gated on.

## Fail-loud floors

`--min-roots` and `--require-legacy` exist because a corpus tool that inspected nothing exits 0 on every rule it applies. Without a floor, *"clean"* and *"never read"* are the same observation. The exit contract is three-valued: `0` holds, `1` does not, `2` could **not** run.

## Prerequisites

`uv` and `git` on `PATH`, plus the [yf-okf](/skills/yf-okf/) skill, which supplies the per-bundle engine. `git` is needed only by `restore`, which distinguishes a tracked file (restore by checkout) from a created one (unlink).

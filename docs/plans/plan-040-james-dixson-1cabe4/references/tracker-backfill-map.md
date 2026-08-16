---
type: Reference
okf_spec: OKF-PLAN
---
# Plan → coarse-tracker map, and the one-off backfill

Produced by **plan-040 Issue 4.4**. Issue 4.3's stamp is forward-looking only; this is the
derivation and stamping of the **existing** population.

**Nothing upstream was closed.** 4.4 proposes; closing is operator-run and gated.

## Why a derivation was needed at all

Coarse trackers are, by definition, the **beads-unmapped** population — that is the whole defect
(#131). So the map could not be read off `external_ref`; it had to be reconstructed from the
outside:

```bash
gh issue list --state all --limit 400 --json number,title,state
# cross-referenced against each docs/plans/*/plan.md `**Epic:**` field
```

The plan estimated "~40 completed plans". That is right: **40 plan folders**. What it did not
anticipate is that only **23** have an identifiable tracker at all, and that **5 of those cannot
be stamped** for a reason unrelated to tracking.

## Summary

| Outcome | Plans | |
| :-- | --: | :-- |
| **Stamped** | **18** | epic exists, tracker identified → `external_ref` written |
| **Identified but unstampable** | 5 | the *epic bead no longer exists* (see below) |
| **No tracker found** | 17 | pre-convention plans — nothing to stamp |
| **Total** | 40 | |

The title convention was not stable across the repo's history, so the search had to accept four
distinct shapes. Each row records **which basis** identified it, so a reader can judge the weaker
matches rather than trusting a bare mapping:

- `plan-NNN execution tracking` — the current convention (from plan-028 / #88 onward)
- `Complete execution of plan-NNN` — the plan-022..027 era
- `plan-NNN: <title>` — the earliest labelled form
- a `plan.md` Upstream Issues row whose disposition is `tracks-plan` (plan-007 only)

## Stamped (18)

| Plan | Epic | Tracker | Upstream state | Identified by |
| :-- | :-- | :-- | :-- | :-- |
| `plan-019` | `yf-mol-99w` | [#65](https://github.com/dixson3/yoshiko-flow/issues/65) | CLOSED | title prefix "<plan>:" |
| `plan-022` | `yf-mol-pvb` | [#70](https://github.com/dixson3/yoshiko-flow/issues/70) | CLOSED | title: "Complete execution of <plan>" |
| `plan-023` | `yf-mol-p1f` | [#72](https://github.com/dixson3/yoshiko-flow/issues/72) | CLOSED | title: "Complete execution of <plan>" |
| `plan-024` | `yf-mol-133` | [#79](https://github.com/dixson3/yoshiko-flow/issues/79) | CLOSED | title: "Complete execution of <plan>" |
| `plan-025` | `yf-mol-2l1` | [#80](https://github.com/dixson3/yoshiko-flow/issues/80) | CLOSED | title: "Complete execution of <plan>" |
| `plan-026` | `yf-mol-a1f` | [#82](https://github.com/dixson3/yoshiko-flow/issues/82) | CLOSED | title: "Complete execution of <plan>" |
| `plan-027` | `yf-mol-k4k` | [#84](https://github.com/dixson3/yoshiko-flow/issues/84) | CLOSED | title: "Complete execution of <plan>" |
| `plan-028` | `yf-mol-181` | [#88](https://github.com/dixson3/yoshiko-flow/issues/88) | CLOSED | title: "<plan> execution tracking" |
| `plan-031` | `yf-mol-e9q` | [#94](https://github.com/dixson3/yoshiko-flow/issues/94) | CLOSED | title: "<plan> execution tracking" |
| `plan-032` | `yf-mol-ifx` | [#95](https://github.com/dixson3/yoshiko-flow/issues/95) | CLOSED | title: "<plan> execution tracking" |
| `plan-033` | `yf-mol-y7f` | [#96](https://github.com/dixson3/yoshiko-flow/issues/96) | CLOSED | title: "<plan> execution tracking" |
| `plan-034` | `yf-mol-bju` | [#98](https://github.com/dixson3/yoshiko-flow/issues/98) | CLOSED | title: "<plan> execution tracking" |
| `plan-035` | `yf-mol-6x8` | [#99](https://github.com/dixson3/yoshiko-flow/issues/99) | CLOSED | title: "<plan> execution tracking" |
| `plan-036` | `yf-mol-3ct` | [#103](https://github.com/dixson3/yoshiko-flow/issues/103) | CLOSED | title: "<plan> execution tracking" |
| `plan-037` | `yf-mol-dh9` | [#115](https://github.com/dixson3/yoshiko-flow/issues/115) | CLOSED | title: "<plan> execution tracking" |
| `plan-038` | `yf-mol-g83` | [#130](https://github.com/dixson3/yoshiko-flow/issues/130) | CLOSED | title: "<plan> execution tracking" |
| `plan-039` | `yf-mol-mzj` | [#134](https://github.com/dixson3/yoshiko-flow/issues/134) | CLOSED | title: "<plan> execution tracking" |
| `plan-040` | `yf-mol-win` | [#138](https://github.com/dixson3/yoshiko-flow/issues/138) | OPEN | title: "<plan> execution tracking" |
## Identified but UNSTAMPABLE — the epic bead is gone (5)

| Plan | Epic (recorded in plan.md) | Tracker | Upstream state | Identified by |
| :-- | :-- | :-- | :-- | :-- |
| `plan-007` | `beads-skills-mol-s3x` | [#16](https://github.com/dixson3/yoshiko-flow/issues/16) | CLOSED | plan.md Upstream Issues row disposition "tracks-plan" |
| `plan-009` | `beads-skills-mol-bjf` | [#23](https://github.com/dixson3/yoshiko-flow/issues/23) | CLOSED | title parenthetical "(plan-009)" |
| `plan-010` | `beads-skills-mol-yvv` | [#24](https://github.com/dixson3/yoshiko-flow/issues/24) | CLOSED | title prefix "<plan>:" |
| `plan-012` | `beads-skills-mol-2bi` | [#35](https://github.com/dixson3/yoshiko-flow/issues/35) | CLOSED | title prefix "<plan>:" |
| `plan-017` | `beads-skills-mol-806` | [#42](https://github.com/dixson3/yoshiko-flow/issues/42) | CLOSED | title prefix "<plan>:" |
These five are **not** unidentifiable trackers — the tracker is known. The **epic** is what is
missing: every one of these plans records a `beads-skills-mol-*` epic id, and

```console
$ bd list --all --json | grep -c beads-skills
0            # of 1019 beads
```

Those ids belong to the pre-rename database. plan-010 (*"`yf-` skill rename + the `yf` Rust
CLI"*) renamed the bead-id prefix from `beads-skills-` to `yf-`, and the old ids did not survive
into the current DB. The `**Epic:**` fields in those five plan.md files are therefore **dangling
references to beads that no longer exist** — a pre-existing data-integrity gap this backfill
merely surfaced. `stamp-tracker` reported each as a clean skip (`bd update failed`) rather than
crashing, which is the fail-soft contract working as intended.

Recorded, not silently skipped, per this issue's contract. Repairing them would mean re-mapping
five historical plans onto beads that no longer exist — out of scope here, and of no practical
value since all five trackers are already closed.

## No tracker found (17)

| Plan | Epic |
| :-- | :-- |
| `plan-001` | `—` |
| `plan-002` | `—` |
| `plan-003` | `—` |
| `plan-004` | `beads-skills-mol-nxk` |
| `plan-005` | `beads-skills-mol-5tv` |
| `plan-006` | `beads-skills-mol-g0b` |
| `plan-008` | `beads-skills-mol-14o` |
| `plan-011` | `beads-skills-mol-r8z` |
| `plan-013` | `beads-skills-mol-glo` |
| `plan-014` | `beads-skills-mol-mqa` |
| `plan-015` | `beads-skills-mol-itd` |
| `plan-016` | `beads-skills-mol-3ee` |
| `plan-018` | `yf-mol-uiw` |
| `plan-020` | `yf-mol-gee` |
| `plan-021` | `yf-mol-al2` |
| `plan-029` | `yf-mol-w21` |
| `plan-030` | `yf-mol-tmm` |
**These are not failures of the search — most of these plans never had a coarse tracker.** The
one-tracking-issue-per-plan convention post-dates them. Their `plan.md` Upstream Issues tables
carry only work dispositions (`include` / `exclude` / `partial` / `supersede`), with no row
tracking the plan itself.

`AGENTS.md` cites "#13 (plan-005), #14 (plan-006), #16 (plan-007)" as precedent for the coarse
convention. Inspection shows #13 and #14 are **feature** issues that those plans *resolved*, not
`execution tracking` trackers — for the earliest plans the coarse tracker *was* the subject issue.
Only plan-007 marks its row `tracks-plan`, which is why it alone is identified above. #13 and #14
are deliberately **not** claimed as trackers: asserting them would be a guess dressed as a
mapping.

`plan-001`, `plan-002` and `plan-003` additionally record **no epic at all**.

## The backfill did not produce actionable signal — and that is the honest result

After stamping, mapped beads rose **21 → 39** and `closable` sees every stamped tracker. **SC9's
second half is satisfied**: previously-invisible completed-plan trackers now appear.

But of the **25** closures `closable` proposes:

| | Count |
| :-- | --: |
| already **CLOSED** upstream | 23 |
| **no longer exist** | 2 |
| genuinely **OPEN** and actionable | **0** |

Every identified tracker except plan-040's own (#138) had **already been closed by hand** — which
is precisely the problem #117 describes, observed after the fact rather than prevented. The
backfill's value is therefore **provenance, not a worklist**: the mapping is now durable, so the
*next* completed plan is caught automatically instead of going stale.

### Two defects this surfaced (filed, not fixed here)

1. **`closable` does not check upstream state.** It proposes `gh issue close` for issues that are
   already closed, and for issues that no longer exist. Before the backfill it proposed 7; after,
   25 — so the backfill made the report **noisier**, not more useful. The per-bead signal is
   correct (all mapped beads *are* closed); what is missing is a filter to issues actually open
   upstream. Out of scope for plan-040, which changes how `closable` *reads beads*, not what it
   *proposes*.

2. **One `external_ref` is not a URL.** Bead `yf-4d7s` carries the bare form `gh-91` (38 of 39
   refs are full URLs). `gh issue edit gh-91` will not resolve it. This is exactly the
   stale/malformed-ref case **SC13** requires to fail closed with a named reason rather than
   create a duplicate — a **live fixture**, better than a synthetic one. Issue 3.4 should use it,
   along with `yf-nzdv`, whose ref points at deleted issue #139.

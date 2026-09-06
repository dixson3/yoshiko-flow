---
type: Finding
okf_spec: OKF-PLAN
description: 'exp-002 - plan-030 phase-log-loss is a detector artifact, and the repair is the move migrate skipped'
---

# exp-002: plan-030's `phase-log-loss` halt — what is actually lost

## Approach Tested

Reproduced the halt (dry run, writes nothing), located the phase log, traced the halt's producer
and the transform's log-reconciliation path, staged the real transform and diffed source against
destination, then built a sandbox (`mktemp -d` + `git init` + commit) holding only plan-030,
applied a candidate repair, and re-ran `backfill` from inside it. Findings re-verified in the main
session against the cited code and against a control bundle.

## Result

**measured:** NOTHING IS LOST. The halt is a detector artifact.

**The phase log is in `plan.md`, not `README.md`.** plan-030's `README.md` carries no phase log at
all, so the halt could never have been repaired by editing the file the halt's framing implies.

### The mechanism, verified in the main session

- `skills/yf-okf/scripts/okf.py:1292` — `if not (d / "log.md").exists():` guards the **entire**
  `log.md` reconciliation block. plan-030 already has a `log.md`, so migrate performs **no**
  log extraction, and the line that strips `**Phase log:**` out of `plan.md` never runs. Source
  and destination are both left untouched.
- `skills/yf-okf-hygiene/scripts/okf_hygiene.py:786-794` computes `src_dates` from `plan.md`
  (pre-transform) and `dst_dates` from the staged `log.md` **only**, then halts on the
  set-difference — with no check that the source block was ever consumed.

So the guard reports a loss that **cannot occur**: it is a one-sided date comparison against a
destination the transform did not write.

**measured:** a second, latent weakness. `okf_hygiene.py:788` computes `src_bul` / `dst_bul` —
the bullet-text sets — and **never uses them**. Only dates are compared, so a genuine loss of
bullets sharing a surviving date would pass unreported. Verified by reading the halt block: only
`lost_dates` is referenced.

### plan-030 is structurally unique among the 8

**measured:** across all eight target bundles —

| Bundle | pre-existing `log.md` | `plan.md` `**Phase log:**` block |
| :-- | :-- | :-- |
| 010, 012, 013, 014, 021, 023, 026 | no | present |
| **030** | **YES** | present |

plan-030's `log.md` was created by `plan_manager`'s close-time `append_log` in a bundle that was
otherwise still legacy — a half-migrated hybrid the classifier still labels `legacy-readme`. That
partial file is exactly what trips `okf.py:1292`'s existence guard.

### What the transform does on a healthy bundle (control)

**measured:** on a sandbox copy of plan-013 —

| | `plan.md` `**Phase log:**` blocks | `log.md` |
| :-- | --: | :-- |
| before | 1 | absent |
| after | **0** | present, 11 entries |

The transform **moves** the phase log. plan-030 skips that move entirely.

## Implications for Plan

- **The halt is not protecting data.** It is safe to clear — but it must be cleared by *repairing
  the bundle*, never by forcing the guard.
- **The repair is the move migrate skipped**, not merely topping up `log.md`. Merging history into
  `log.md` while leaving `plan.md`'s block in place clears the halt but leaves plan-030 with the
  history **duplicated** across two files — the only bundle of the eight in that state, and
  contrary to the current `plan.md` schema, which has no `**Phase log:**` block at all.
- Corpus impact is exactly one bundle, so the transform is unblocked by a content edit and does
  not need to wait on an engine fix.
- Two engine defects are exposed and belong upstream, **out of scope here**: the one-sided guard
  (`okf_hygiene.py:786-794`, including the dead `src_bul`/`dst_bul`) and migrate's skip-if-exists
  log reconciliation (`okf.py:1292`), which will recur for any legacy bundle closed via
  `plan_manager` after `append_log` shipped.

## Recommendations

1. Repair plan-030 by performing the full move by hand: merge `plan.md`'s ten phase-log bullets
   into `log.md` (newest-first, date-grouped, prefixes stripped) **and delete the `**Phase log:**`
   block from `plan.md`** — reaching the same end state the other seven reach mechanically.
2. Verify the repair by dry run **before** applying anything to the corpus.
3. File the two engine defects upstream; do not fix them in this plan.

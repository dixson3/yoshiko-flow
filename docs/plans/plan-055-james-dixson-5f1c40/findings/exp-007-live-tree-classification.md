---
type: Finding
okf_spec: OKF-PLAN
id: exp-007-live-tree-classification
description: Does a live deployed skill copy actually classify owned-and-unmodified? (pass-2 M7 falsifier)
---

# EXP-007 — live-tree classification (the M7 falsifier)

## Approach Tested

Red-team pass 2 (M7) identified an unchecked falsifier under Epic 1. EXP-004 grades as **inferred**
that marker-gated removal is buildable on existing `marker`/`status` machinery — *"the primitives
were measured to work, but no existing caller consults the marker before deleting, so the composed
behaviour is untested."* D-2a restates this as settled.

The specific risk: if deployment residue (`__pycache__`, generated files) escapes `REQ-YF-MARK-005`'s
ignore-list, a recomputed marker-stripped tree hash would **not** equal `marker_hash` for a live
deployed copy. Every real directory would classify `owned-but-modified`, the `delete` set would be
empty, and the migration gate — which fails on an empty delete set — would hard-block the plan at 5.1.

Measured directly against the four live user-scope roots on the target machine:

```bash
yf harness skills status --harness <h> --scope user --json
```

## Result

**measured — the falsifier is REFUTED.**

| harness | skills | `state` | `unmodified` |
| :-- | --: | :-- | :-- |
| claude-code | 19 | `ok` | `true` (19/19) |
| codex | 19 | `ok` | `true` (19/19) |
| opencode | 19 | `ok` | `true` (19/19) |
| pi | 19 | `ok` | `true` (19/19) |

**76 of 76 deployed copies classify `ok` / `unmodified: true`.** Deployment residue does **not**
escape the ignore-list, and the recomputed marker-stripped hash equals `marker_hash` for every live
copy.

## Implications for Plan

- **The migration gate will not hard-block at 5.1.** The `delete` set for each private tree is 19
  directories, not zero, so the gate's deliberate empty-set failure will not fire spuriously.
- **D-2a's mechanism is now measured rather than inferred** for the population that matters — the
  live deployed trees this plan actually migrates. EXP-004's `inferred` grade remains correct for the
  *composed* behaviour (no caller consults the marker before deleting yet); what is now measured is
  the **classification input** that composition depends on.
- **The residual population is the foreign one.** `~/.config/opencode/skills` additionally holds 13
  directories with no yf marker (R11), which classify `no-marker` → keep-and-report. Those are
  exactly the directories conservative-keep exists for.

## Recommendations

1. **Keep the migration gate's empty-`delete`-set failure.** It is now known not to fire spuriously on
   this machine, so it retains its intended meaning: a remover that found nothing is a broken remover.
2. **Re-measure at 1.1 rather than inheriting this figure.** The distribution is a property of the
   machine, not of the code — an operator with hand-edited skills legitimately gets a different one,
   and that is conservative-keep working, not a defect.
3. **Do not upgrade EXP-004's `inferred` grade wholesale.** What this measures is the classification
   *input*; the composed removal behaviour still has no caller and remains untested until Epic 1.

## Confidence

- **measured:** 19 skills per root × 4 roots, all `state: ok`, `unmodified: true`, via the shipped
  `yf harness skills status --json`.
- **inferred:** that this holds on *other* machines. It is a property of the ignore-list and of a
  clean `yf self install`, so a machine with hand-edited skills would legitimately classify some
  copies `owned-but-modified` — which is the conservative-keep path working as designed, not a defect.
- **not measured:** the `undetermined` class against live trees. The symlink instance EXP-002 found
  (`~/.agents/skills/terminal-browser`) sits in the *shared* root rather than a private one, so it is
  not in the migration's delete scope — but Issue 1.5's symlinked-member fixture still covers it.

---
type: Decision
okf_spec: OKF-PLAN
---
# Decision: `plans-root` / `incubator-root` are a shared, committed decision

**Date:** 2026-08-13
**Decided by:** operator (plan-037 Issue 2.1 human capability gate)
**Status:** decided

## The question

The #107 local patch invented a **committed** `.yf-plan.json` tier for layout decisions,
distinct from the gitignored `.yf-plan.local.json` operator override. The canonical `.yf/` tree
is **entirely gitignored** (`.gitignore:18` — `/.yf/`, and `git ls-files .yf` is empty), so a
committed layout decision had no canonical home. Are `plans-root` / `incubator-root` a
shared-and-committed decision, or a local-only one?

## Decision

**Shared and committed.** A committed tier is added at `.yf/plan/config.json`, read *beneath*
the gitignored local override.

Precedence, highest first:

| Tier | Path | Committed? | Holds |
|:--|:--|:--|:--|
| 1 | `.yf/plan/config.local.json` | no (gitignored) | operator overrides — machine-specific |
| 2 | `.yf/plan/config.json` | **yes** | shared layout decisions the repo carries |
| 3 | `.yf-plan.local.json` | no (gitignored) | legacy root dotfile — read-only fallback, never removed |

### Merge, not first-match-wins

Tiers are merged **key by key**, highest tier winning per key — not whole-file first-match.
This is required for the tier to be useful: under whole-file precedence a `.yf/plan/config.local.json`
setting only `landing-strategy` would mask a committed `plans-root` entirely, which is the
opposite of "override".

This changes the existing Rust `read_config` from first-match-wins to merge. The change is
backward-compatible: with a single config file present, merge and first-match-wins are identical.

## Rationale

The layout is a property of **the repository**, not of a checkout. If one clone writes plans to
`Notes/plans` and another to `docs/plans`, the repository ends up with both trees and the plan-id
numbering — which is global across roots — silently fragments. That is a repo-wide fact, so it
belongs in a repo-wide file.

The motivating case from #107 is a repo that is also an Obsidian vault, where a visible top-level
`Incubator/` folder trips the vault's structure linter. That constraint travels with the vault,
not with the operator.

## Consequences, accepted

1. **A `.gitignore` carve-out inside an otherwise fully-ignored tree.** `/.yf/` stays ignored;
   `!/.yf/plan/config.json` (with the `!/.yf/plan/` directory un-ignore it requires) is the single
   exception. Everything else under `.yf/` — all runtime state, all `*.local.json` — stays ignored.
2. **`yf/src/preflight.rs` must learn the same tier.** Two readers disagreeing about config
   precedence is precisely the drift #100 exists to remove, so shipping the Python tier alone
   would be worse than not shipping it. The Rust `read_config` is updated in the same change-set.
   *This is scope the plan did not anticipate* — it was listed as an argument against this option
   — and is accepted deliberately.
3. **This does not settle #102.** #102 asks the general question of whether anything inside the
   gitignored `.yf/` tree may be committed, for the markdown-lint marker. This decision answers it
   for **one file** by explicit carve-out and sets a precedent, but does not generalize the rule
   or migrate the marker. #102 stays open; cross-referenced, not solved.

## Rejected alternative

**Local-only** — put both keys in `.yf/plan/config.local.json` alongside `landing-strategy` /
`validate-cmd` / `execute.worktree`, keeping one tier and requiring no Rust change or gitignore
carve-out. Rejected because it makes a repo-wide structural fact a per-clone setting, which the
global plan-id numbering makes actively unsafe.

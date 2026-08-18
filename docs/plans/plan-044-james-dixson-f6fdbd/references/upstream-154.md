---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #154: yf harness tune regenerates YOSHIKO_FLOW.md wholesale — no managed block, no guard, and --revert deletes rather than restores

- **Number:** 154
- **Title:** yf harness tune regenerates YOSHIKO_FLOW.md wholesale — no managed block, no guard, and --revert deletes rather than restores
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf harness tune` regenerates `~/.claude/rules/YOSHIKO_FLOW.md` **wholesale**, with no managed-block delimiters and no checksum guard. Operator edits inside it are silently lost, and `--revert` **deletes** the file rather than restoring its pre-tune content.

This is existing, deliberate behavior — the aggregate is treated as wholly yf-owned. It is filed now because **plan-042** (install-time sync) will make `tune` run automatically on every `yf self install` / `yf self update`, raising this hazard's frequency from "when the operator types `yf harness tune`" to "on every binary promote". plan-042 explicitly declines to absorb the fix (its decision D-I); this issue is where it belongs.

## Measured behavior

From plan-041's E4 investigation (`docs/plans/plan-041-james-dixson-a9d837/findings/exp-004-harness-tune-safety.md`):

- `deploy_rules_aggregate` → `common::install_rules_aggregate` rewrites the file entirely: every embedded section body is upserted verbatim over whatever is on disk, and **any section whose `(skill, protocol)` pair is not in the embedded valid set is pruned/deleted**.
- It also **deletes** standalone `~/.claude/rules/<PROTOCOL>.md` files whose basename matches a yf-owned protocol. Non-yf files (e.g. a hand-written `BEADS.md`) never match and are untouched.
- `--revert` for the claude-code `aggregate` record **deletes `YOSHIKO_FLOW.md`** — it does not restore pre-tune content.

## Why it's inconsistent with the rest of tune

Every *other* surface `tune` writes is carefully protected, which is what makes this one stand out:

| Surface | Protection |
| :-- | :-- |
| `settings.json`, `config.toml`, `opencode.json` | key-level merge; add-missing scalars with **conflict preservation**; union-only sets; unknown keys untouched; malformed file **refused** without data loss |
| `AGENTS.md` (codex / opencode / pi) | `<!-- BEGIN yf-managed-rules -->` managed block; appends when absent, replaces **only** the marked span, never touches surrounding prose; fail-safe refusal on damaged markers |
| **`YOSHIKO_FLOW.md`** | **none** |

The `AGENTS.md` managed-block mechanism is the obvious precedent — it already solves exactly this problem for a sibling surface in the same code path.

## Why "wholly yf-owned" is a weaker justification than it looks

The design intent is defensible: the aggregate is generated from embedded skill `protocols/*.md`, so hand-editing it is editing a build artifact. But:

1. **Nothing tells the operator that.** The file has no header marking it generated, no "do not edit" banner, and no pointer to the source it is generated from.
2. **It sits in a directory that also holds hand-authored files.** `~/.claude/rules/` is a normal operator-editable location — a hand-written `BEADS.md` there is untouched and legitimate. One file in that directory silently discarding edits, with nothing distinguishing it, is a trap.
3. **`--revert` deleting rather than restoring** means the manifest-backed revert story — which is careful and correct everywhere else — has a hole precisely here.

## Suggested directions

Not prescriptive; the "yf-owned" stance may well be right, in which case (a) alone is enough.

- **(a) Cheapest, and probably sufficient on its own:** emit a generated-file header at the top of the aggregate — what generated it, from which embedded sources, and that edits will not survive. Converts a silent loss into an informed one. This alone would close the trap.
- **(b) Adopt the `AGENTS.md` managed-block shape** for the aggregate: yf owns the marked span, operator prose outside it survives. Reuses a mechanism already implemented, tested, and fail-safe in the same module.
- **(c) Make `--revert` restore rather than delete**, by recording the prior content (or its absence) in the existing tune manifest — the manifest already exists and already drives per-key revert for config surfaces.

(a) and (c) are independent and each worth doing regardless of whether (b) is adopted.

## Related

- **plan-042** — install-time sync; decision D-I places this out of its scope and references this issue from its risks.
- plan-041 E4 — the source measurement (`REQ-YF-TUNE-022` revert behavior, `common.rs` aggregate regeneration, `managed_block.rs` for the contrasting protected surface).

🤖 Generated with [Claude Code](https://claude.com/claude-code)


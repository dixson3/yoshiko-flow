# Exp 001 — #39 canonicalization gap (auto-vs-propose)

## Verdict

`yf doctor --repair` (→ `beads_init::repair()`) already does **most** of #39's canonical
end-state. The genuinely-unaddressed remainder is **exactly the three live-session gaps**, all
on the "already-dirtied from before" axis — gitignore rules and hook *de-wiring* are done;
*untracking* already-tracked files and *removing* an existing Dolt remote are not.

## Current-state mapping (#39 item → status → evidence)

| # | #39 item | Status | Evidence (`yf/src/...`) |
| :-- | :-- | :-- | :-- |
| 1 | `dolt.local-only true` asserted | done | `beads_init.rs:373-374`, `:406-411` |
| 2 | `bd dolt remote list` empty | **MISSING** | no `dolt remote remove` anywhere; live repo still has `origin` remote |
| 3 | no `sync.remote` | **MISSING** | nothing touches `sync.remote`; live `bd config get sync.remote` non-empty |
| 4 | `custom.upstream.*` configured | out of repair scope | owned by `yf-beads-upstream`, default-deny |
| 5 | `core.hooksPath` at default | done | native `hookspath-reset` `:545-560` |
| 6 | no tracked `.beads/hooks/*` shims | **PARTIAL** | `bd hooks uninstall` de-wires (`:426-429`) but no `git rm` of shim files |
| 7 | no beads `.claude/settings.json` hook (prune if empty) | done | `:433-436` + `prune-settings` `:591-594`/`:670-684` |
| 8 | no `.codex/`, `.agents/skills/beads/`, managed blocks | done | `:439-442`, `:565-575`, `:579-586`, `:599-602` |
| 9 | `.beads/interactions.jsonl` untracked (`git rm --cached`) | **MISSING** | gitignore rule exists; no `git rm --cached` of pre-tracked copy |
| 10 | dolt artifacts gitignored+untracked | done (gitignore side) | `BEADS_GITIGNORE` `:30-41`; same untrack caveat if pre-tracked |
| 11 | `.beads/issues.jsonl` per durability model | N/A | `bd export` step `:412-415` |

**Structural gap:** preflight (`preflight.rs:509-539`) is **strictly read-only** (calls `verify()`
only). Canonicalization happens *only* on explicit `yf doctor --repair`. #39's "converge on
preflight" goal is therefore unmet by construction.

## The remainder this plan must build (3 items)

1. **Untrack `.beads/interactions.jsonl`** (+ any pre-tracked dolt/runtime artifacts): `git rm
   --cached` for now-gitignored-but-still-indexed files. — **SAFE-to-AUTO** (`--cached` keeps the
   working file; idempotent no-op when clean).
2. **Remove tracked `.beads/hooks/*` shims**: `git rm` the dead `bd hooks run` shims. —
   **SAFE-to-AUTO with a content guard** (verify the `bd hooks run` signature before removing so a
   hand-edited hook is never nuked).
3. **Remove the Dolt remote / `sync.remote`** under `--local-only`: `bd dolt remote remove` + clear
   `sync.remote`. — **NEEDS-CONFIRM** (destructive: alters DB replication; #39's own operator did
   this interactively). Keep `--local-only` asserting the flag automatically; gate the *remote
   removal* behind an explicit confirm / opt-in flag (`--remove-remote`).

## Recommendation

**Hybrid:** auto the two untrack/shim items (non-destructive in substance, idempotent), propose
the remote removal (confirm-gated). Logic lives in **`beads_init::repair()`** as new native steps
alongside the existing cleanup block (`:444-464`, `apply_native` dispatch `:516-605`) — pure
git/fs ops that fit the pattern. The remote removal needs a new `remove_remote: bool` plumbed from
a `DoctorArgs` flag (`repair()` currently takes a bare `apply: bool`). Do **not** put
canonicalization in preflight (must stay read-only); if "converge on preflight" is in scope, route
it as skills calling `yf doctor --repair`, not preflight mutating.

**This is a `yf` Rust change** (`beads_init.rs` + `cli.rs` flag + `yf-beads-init` SKILL/SPEC docs).
Note the intentional boundary being crossed: `beads_init.rs:320` docstring says "never adds a Dolt
remote" — the new work is the *inverse* (removing one), a design-decision change the current design
explicitly left as a manual/interactive step.

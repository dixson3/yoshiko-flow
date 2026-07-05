# Upstream #61: yf-beads-upstream/hygiene: authorize --remove-remote cleanup + trigger on 'push/sync upstream' phrasing

- **Number:** 61
- **Title:** yf-beads-upstream/hygiene: authorize --remove-remote cleanup + trigger on 'push/sync upstream' phrasing
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

Two related gaps surfaced while landing a plan in a beads repo and then cleaning it up. Both are about **making the right upstream/hygiene action fire reliably** instead of depending on the operator (or the agent) remembering the exact mechanism.

1. **`yf doctor --repair --remove-remote` should be a recognized, authorized cleanup step** — not an obscure opt-in an operator has to be told about.
2. **`yf-beads-upstream` should fire on natural "push upstream" / "sync issues upstream" phrasing**, not only on the close-time land-the-plane trigger.

A third, concrete bug in `yf-beads-upstream`'s candidate enumeration is included below — it made the push step silently find zero candidates.

## Background / what happened

Landing `plan-004` in a writing repo (`dixson3/writing`), then running cleanup:

- The `yf-plan` preflight repeatedly reported: *"Canonicalization drift: a Dolt remote is configured under local-only — run `yf doctor --repair --remove-remote` to clear it."*
- Plain `yf doctor --repair` did **not** clear it; the flag actually requires **`--repair --local-only --remove-remote`** together. The instruction string omits `--local-only`, so the suggested command is a no-op that leaves the drift in place.
- Clearing `sync.remote` (bd config) still left a **Dolt DB-level `origin` remote** registered; a separate `bd dolt remote remove origin` was needed to fully resolve it. The doctor step clears the config layer but not the Dolt-DB layer.
- Separately, there was real confusion about whether `yf-beads-upstream` depends on the Dolt remote. It does **not** — it uses `gh` directly (`custom.upstream.backend=github`). The Dolt remote (`sync.remote`, driven by `bd dolt push`) and the `gh`-based issue mirror (`yf-beads-upstream`) are **independent paths**, but nothing in the trigger/doc surface makes that separation obvious, and it's easy (even for an agent) to conflate "push beads upstream" with `bd dolt push`.

## Requested changes

### 1. Make `--remove-remote` an authorized, self-describing cleanup step
- Fix the preflight/doctor **instruction string** to emit the command that actually works: `yf doctor --repair --local-only --remove-remote` (the current suggestion omits `--local-only` and is a no-op).
- Have `--remove-remote` also drop the **Dolt-DB-level remote** (`bd dolt remote remove <name>`), not just `sync.remote` in `config.yaml`, so one invocation fully resolves the drift the preflight complains about.
- Treat this as a **first-class, operator-authorized** repair action (it's already gated as opt-in because it touches remote config — good — but it should be surfaced as *the* answer to the drift, with the correct flags).

### 2. `yf-beads-upstream` should trigger on explicit intent phrasing
Ensure the skill fires (or is reliably routed to) when the operator says things like:
- "push upstream" / "push beads upstream"
- "sync issues with upstream" / "sync issue upstream" / "mirror this bead upstream"
- "file/hoist this as a GitHub issue"

Today the **close-time** land-the-plane trigger lives in the always-loaded companion rule, and `init`/`status` intent is in the description — but a mid-session "push these upstream now" / "sync issues upstream" is not a crisp trigger. The result is that an agent may reach for `bd dolt push` (DB replication) instead of the `gh`-based `yf-beads-upstream` push step. Please make the intent-trigger surface explicit and disambiguate it from `bd dolt push` in the docs (they are orthogonal).

### 3. Clarify the two "upstream" mechanisms wherever they're documented
A short table in `yf-beads-upstream` (and/or `yf-beads-hygiene`) distinguishing:
- `git push` → git origin (content),
- `bd dolt push` → Dolt remote (versioned DB replication; local-only repos should have **none**),
- `yf-beads-upstream` → `gh issue` mirror (independent of Dolt).

This directly prevents the conflation above.

## Bonus bug: `yf-beads-upstream enumerate` returns zero candidates when beads are owner-claimed

`scripts/upstream.py enumerate` classifies a bead as **active** (excluded from push candidates) when `status == open AND owner non-empty`. In this repo every bead gets an **owner assigned on `bd create`** (`dixson3@gmail.com`), so **all 22 open beads read as "claimed" → active → zero enumerate candidates**, even genuine parked follow-ups.

Repro: create any bead in a repo where `bd create` auto-assigns an owner, then run `uv run .../upstream.py enumerate --json` → `[]`.

The scoped push step (`bd github push <id>`) still works with explicit IDs, so this isn't blocking, but the **land-the-plane candidate discovery is effectively broken** for any workflow where beads are owned on creation. Consider: (a) not treating "has owner" alone as active (require `in_progress` or claimed-*and*-recent), or (b) a config knob for repos where ownership is assigned by default, or (c) at minimum documenting the gap so operators fall back to explicit `--issues`.

## Environment
- Observed in `dixson3/writing` (beads local-only, `custom.upstream.backend=github`).
- `yf preflight` reported the drift; `yf doctor --repair --local-only --remove-remote` + `bd dolt remote remove origin` fully resolved it.


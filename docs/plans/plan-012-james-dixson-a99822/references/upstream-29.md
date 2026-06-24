# Upstream #29: Add yf-beads-hygiene skill: safe orphan/dangling-edge cleanup for beads

- **Number:** 29
- **Title:** Add yf-beads-hygiene skill: safe orphan/dangling-edge cleanup for beads
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Summary

Add a new skill **`yf-beads-hygiene`** that safely audits and cleans up a beads
DB — orphaned beads, dangling dependency edges, and stale/wedged state — and is
the canonical trigger for any "cleanup beads" / "are there orphaned beads"
request.

## Motivation (drawn from a real session)

A "cleanup orphaned beads" request was handled ad-hoc and produced a
**dangerous false positive** that nearly corrupted a real dependency graph. The
failure modes are general and worth encoding once:

1. **`bd list` hides `gate`-type beads.** An audit that diffs open beads'
   dependency edges against `bd list` / `bd list --all` output will flag every
   edge that points at a gate as "dangling," because gates don't appear in list
   output. In the session this surfaced 11 "dangling" edges that were in fact
   valid gate dependencies (`Gate: Substrate Foundation`, `Gate: human`,
   `Gate: Hoist`).

2. **`bd list` default truncates** (50 rows here), so molecule **roots** looked
   "missing" and ~38 molecule-children looked orphaned. Re-running against
   `--all` showed the roots were present and there were zero true orphans. An
   audit must never run against the truncated default list.

3. **Blindly removing "dangling" edges un-gated live work.** Two of the gates
   were still `open`, so removing the edges would have wrongly unblocked 7 beads.
   Recovery required restoring all 11 edges and a Dolt commit/push to keep the
   audit trail consistent. Net change should have been zero — but the wrong tool
   made a destructive change look like a cleanup.

## Proposed behavior

**Trigger:** any request to "cleanup" / "clean up" open or orphaned beads,
"are there orphaned/dangling beads", "audit the beads graph", or
`/yf-beads-hygiene`.

**Audit (read-only first, always):**

- Resolve dependency-edge targets with `bd show <id>` (which sees gates),
  **never** by membership in `bd list` output.
- Always query the full universe (`--all` / explicit status sweep), never the
  truncated default list.
- Classify findings:
  - **True orphan** — molecule child whose root bead does not exist anywhere in
    the DB.
  - **Truly dangling edge** — target resolves to nothing via `bd show`.
  - **Satisfied-gate edge** — target is a `closed` gate (edge is harmless;
    leave it; removing it only loses provenance).
  - **Live-gate edge** — target is an `open` gate (NOT dangling; must be
    preserved).

**Repair (only after the audit, gated on confirmation for anything
destructive):**

- Propose edge removals only for *truly* dangling targets; show the full list
  and require confirmation before mutating.
- Never remove an edge whose target resolves to a live (open) gate.
- After any mutation: `bd dep cycles`, then `bd dolt commit` + `bd dolt push`
  + `git push` so the graph and audit trail stay consistent (land-the-plane).
- Round-trip safety: if an edge is removed and must be restored, restore it
  exactly (`bd dep add <blocked> <blocker>`).

**Relationship to existing skills:**

- Distinct from `yf-beads-init` (verify/repair *config & DB health*) — hygiene
  operates on *graph content* (orphans, edges) of an already-healthy DB.
- Should route to `yf-beads-init` if it detects a wedged/corrupted DB rather
  than trying to clean a broken store.
- Direct-CLI gotchas it relies on (gate semantics, `bd show` vs `bd list`,
  edge mutation, JSON parsing) already live in `yf-beads-extra` — reference,
  don't restate.

## Acceptance criteria

- [ ] Skill `yf-beads-hygiene` exists with the trigger contract above.
- [ ] Audit phase resolves edge targets via `bd show`, not `bd list`.
- [ ] Audit always uses the full bead universe, never the truncated default.
- [ ] Gate-typed targets are classified by status (open = preserve, closed =
      satisfied) and never reported as dangling.
- [ ] Destructive repairs require explicit confirmation and are followed by
      `bd dep cycles` + Dolt/git push.
- [ ] Routes to `yf-beads-init` when the DB is wedged/corrupted.

---
_Filed from a session where the ad-hoc version of this audit produced a
false-positive "11 dangling edges" finding against live gate dependencies._


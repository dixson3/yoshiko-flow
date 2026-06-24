---
name: yf-beads-hygiene
description: >
  Safe, read-only-first audit and gated repair of a beads (`bd`) dependency graph: finds
  orphaned beads and dangling dependency edges, and correctly classifies gate-typed edges so
  live gates are never mistaken for dangling. The canonical trigger for any "clean up beads"
  request.
  TRIGGER when: /yf-beads-hygiene invoked; "clean up" / "cleanup" open or orphaned beads;
  "are there orphaned/dangling beads"; "audit the beads graph"; or a dependency-edge removal
  is being considered.
  SKIP for: verifying/repairing beads CONFIG or DB health — a wedged/corrupted DB or
  uninitialized repo routes to `yf-beads-init` (this skill operates on the graph CONTENT of an
  already-healthy DB); routine `bd ready`/`bd show`/`bd close` (the `beads` skill); direct-CLI
  gotchas (`yf-beads-extra`); authoring beads-backed skills (`yf-beads-authoring`).
user-invocable: true
skill-group: beads
depends-on-tool: [bd, uv, git]
depends-on-skill: [yf-beads-extra, yf-beads-init]
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
---

# yf-beads-hygiene

Audit and clean up the **content** of a beads dependency graph — without un-gating live work —
along two axes: a **graph-content audit** (`audit`/`repair`/`restore`: orphaned beads and
dangling edges) and a **reconcile** pass (the local↔upstream active-vs-parked boundary). Distinct
from `yf-beads-init`, which verifies and repairs beads **config and DB health**: hygiene assumes
an already-healthy DB and operates on the graph.

This skill exists because an ad-hoc "cleanup orphaned beads" pass produced a **dangerous false
positive** — 11 valid live-gate edges flagged "dangling" because `bd list` hides gate beads and
truncates at 50 rows; a blind cleanup would have un-gated 7 live beads. The discipline below
encodes the safe audit once.

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-beads-hygiene -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-beads-hygiene skill directory not found"; exit 1; }
```

## The one rule that matters most

**Resolve every dependency-edge target with `bd show <id>`, over the full universe — never by
membership in `bd list` output.** `bd list` (and `bd list --all`) **hides `gate`-type beads**
and **truncates at 50 rows**; an audit that diffs edges against a `bd list` dump flags every
edge pointing at a gate as "dangling," and a blind removal un-gates live work. (Gotcha owned by
`yf-beads-extra` — see "`bd list` hides gate beads AND truncates at 50 rows" there; not restated
here.)

## Preflight — health before content

Hygiene cleans a *healthy* DB. Before auditing, the engine checks DB health and **routes to
`yf-beads-init` on a wedged/corrupted DB** rather than cleaning a broken store. Note the
false-negative invariant (`BEADS_INIT.md`): `bd status --json` can return error JSON with exit
0 — an initialized-but-wedged repo, not an uninitialized one. The engine treats that as
`db_wedged` → route to `yf-beads-init` (verify, then repair), then re-run the audit.

## Audit (read-only, always first)

```bash
uv run "$SKILL_DIR/scripts/beads_hygiene.py" audit          # human report
uv run "$SKILL_DIR/scripts/beads_hygiene.py" audit --json   # machine-readable
```

The engine builds the full universe (`bd list --all` **plus** `bd list --all --type gate`),
enumerates every dependency edge via `bd show` on each bead, resolves each edge target via
`bd show`, and classifies each edge into **exactly one** of four classes:

| Class | Meaning | Disposition |
| :--- | :--- | :--- |
| `true-orphan` | parent-child edge whose root/parent bead does not exist | report; never auto-remove |
| `truly-dangling` | `blocks` edge whose target resolves to nothing | the ONLY removable class |
| `satisfied-gate` | target is a **closed** gate | leave (removing only loses provenance) |
| `live-gate` | target is an **open** gate | **PRESERVE** — removing un-gates live work |

A live-gate edge is **never** reported as dangling — that invariant is the whole point of #29.

## Reconcile (the second axis: local↔upstream boundary, read-only-first)

`audit` works on dependency **edges** (orphaned / dangling within the local graph). `reconcile`
works on a different axis — the **local↔upstream active-vs-parked boundary**, classifying
**beads** (not edges): which local beads are actively worked vs which are parked work that
belongs upstream until a plan pulls them back.

```bash
uv run "$SKILL_DIR/scripts/beads_hygiene.py" reconcile          # read-only proposal
uv run "$SKILL_DIR/scripts/beads_hygiene.py" reconcile --json   # machine-readable
uv run "$SKILL_DIR/scripts/beads_hygiene.py" reconcile --apply --record hoist.json   # delegate hoists (prompts)
```

The engine computes the **active set** — a bead is active iff `status == in_progress`, OR
(`status == open` AND claimed, i.e. `owner` non-empty), OR it is an **open** parent-chain
ancestor of an active bead (walked to a fixed point). Everything else non-closed (open-unclaimed,
blocked, deferred) is **non-active**. It then reports:

- **Hoist candidates** — the non-active beads; they belong upstream until pulled back.
- **Obsolete upstream issues** — open tracking issues with a **mechanical** delivered signal
  (linked plan's `plan.md` shows `Status: complete`, or a merged PR). Proposal-only — reconcile
  **never** auto-closes an upstream issue.
- **Flagged for human review** — open issues with no resolvable delivered signal (never flagged
  obsolete on a guess).

**The carve — hygiene proposes, `yf-beads-upstream` executes.** `reconcile` is read-only by
default. The gated `--apply` (with `--yes` to skip the prompt, `--record` for the round-trip
record) does **not** push or close beads itself — it **delegates** each non-active hoist to
`yf-beads-upstream` (`upstream.py hoist`, which dry-runs then `bd close`s a reversible tombstone).
A wrong hoist is reversible via `upstream.py unhoist --record <file>`. On a wedged/corrupted DB
`reconcile` routes to `yf-beads-init` exactly like the audit.

## Repair (gated; only after the audit)

```bash
uv run "$SKILL_DIR/scripts/beads_hygiene.py" repair                          # dry run: list proposals
uv run "$SKILL_DIR/scripts/beads_hygiene.py" repair --apply --record removed.json   # mutate (prompts)
```

- Proposes removals for **truly-dangling edges only** — never live-gate, satisfied-gate, or
  orphan findings.
- Requires explicit confirmation before any mutation (`--yes` skips the prompt for automation;
  use `AskUserQuestion` to confirm with the operator interactively).
- After mutation runs `bd dep cycles` (post-mutation integrity check, owned by `yf-beads-extra`)
  and prints the **land-the-plane** sequence (`bd dolt commit && bd dolt push && git push`) so
  the graph and audit trail stay consistent.
- Writes a removal record (`--record`) so any wrong removal is reversible.

## Restore (round-trip safety)

```bash
uv run "$SKILL_DIR/scripts/beads_hygiene.py" restore --record removed.json --apply
```

Re-adds each removed edge exactly (`bd dep add <blocked> <blocker>`), then re-checks
`bd dep cycles`. Recovery from the original incident required restoring all 11 edges; this makes
that a one-command round trip.

## See also

- **`yf-beads-extra`** — direct-CLI gotchas this skill relies on (gate semantics, `bd show` vs
  `bd list`, edge mutation, defensive JSON parsing, `bd dep cycles`). Referenced, not restated.
- **`yf-beads-init`** — verify/repair beads **config & DB health**; hygiene routes here on a
  wedged/corrupted DB.
- **`yf-beads-upstream`** — the **execution** side of the reconcile carve: hygiene proposes hoist
  candidates / obsolete issues; `yf-beads-upstream` executes the push and reversible `bd close`
  (`upstream.py hoist`/`unhoist`). Reconcile never pushes or closes beads itself.
- **`beads`** — the canonical routine loop (`bd ready`/`bd show`/`bd close`).

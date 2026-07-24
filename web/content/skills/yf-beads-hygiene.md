`yf-beads-hygiene` audits and cleans the **content** of a beads dependency graph
without un-gating live work. It is the canonical trigger for any "clean up beads"
request — run it when you ask whether there are orphaned or dangling beads, when you
want the graph audited, or when a dependency-edge removal is on the table. It assumes
an already-healthy database: verifying or repairing beads config and DB health is a
different job that routes to [`yf-beads-init`](/skills/yf-beads-init/). This skill
operates on the graph an init-healthy DB holds.

The skill exists because an ad-hoc cleanup pass once produced a dangerous false
positive: **11 valid live-gate edges were flagged "dangling"** because `bd list` hides
gate beads and truncates at 50 rows. A blind removal would have un-gated 7 live beads.
The discipline below encodes the safe audit so that never happens again.

## The one rule that matters most

Resolve every dependency-edge target with `bd show <id>`, over the full universe —
never by membership in `bd list` output. `bd list` (and `bd list --all`) hides
`gate`-type beads and truncates at 50 rows. An audit that diffs edges against a
`bd list` dump flags every edge pointing at a gate as dangling, and a blind removal
un-gates live work. The full universe is `bd list --all` plus `bd list --all --type
gate`; each edge target is resolved with `bd show`, which sees gates. This gotcha is
owned by [`yf-beads-extra`](/skills/yf-beads-extra/) and relied on here.

## Health before content

Hygiene cleans a healthy DB. Before auditing, the engine checks DB health and routes a
wedged or corrupted store to [`yf-beads-init`](/skills/yf-beads-init/) rather than
cleaning something broken. It respects the false-negative invariant: `bd status --json`
can return error JSON with exit 0, which signals an initialized-but-wedged repo, not an
uninitialized one. The engine classifies that as `db_wedged`, routes to init, and
re-runs the audit afterward.

## Audit — read-only, always first

The `audit` verb is read-only and runs before anything else. It builds the full
universe, enumerates every dependency edge, resolves each target with `bd show`, and
sorts each edge into exactly one of four classes:

| Class | Meaning | Disposition |
| :---- | :------ | :---------- |
| `true-orphan` | parent-child edge whose parent bead does not exist | report; never auto-remove |
| `truly-dangling` | `blocks` edge whose target resolves to nothing | the only removable class |
| `satisfied-gate` | target is a **closed** gate | leave; removing only loses provenance |
| `live-gate` | target is an **open** gate | **preserve** — removing un-gates live work |

A live-gate edge is never reported as dangling. That invariant is the whole point.

## Reconcile — the local-versus-upstream boundary

Where `audit` works on dependency *edges*, `reconcile` works on a different axis: which
local *beads* are actively worked versus which are parked work that belongs upstream
until a plan pulls them back. The engine computes the **active set** — a bead is active
if its status is `in_progress`, or it is claimed and open, or it is an open
parent-chain ancestor of an active bead. Everything else non-closed is non-active. It
then reports three things:

- **Hoist candidates** — the non-active beads that belong upstream.
- **Obsolete upstream issues** — open tracking issues with a mechanical delivered
  signal, such as a linked plan showing `Status: complete` or a merged PR. Proposal
  only; reconcile never auto-closes an upstream issue.
- **Flagged for review** — open issues with no resolvable delivered signal, never
  flagged obsolete on a guess.

Hygiene **proposes**, [`yf-beads-upstream`](/skills/yf-beads-upstream/) **executes**.
`reconcile` is read-only by default. Its gated `--apply` does not push or close beads
itself — it delegates each hoist to `yf-beads-upstream`, which dry-runs the push then
closes a reversible tombstone. A wrong hoist reverses with an un-hoist.

## Repair and restore — gated, and reversible

`repair` runs only after the audit and only ever proposes removals for
**truly-dangling edges** — never live-gate, satisfied-gate, or orphan findings. It
requires explicit confirmation before any mutation, re-runs `bd dep cycles` afterward
as an integrity check, and writes a removal record so any wrong removal is reversible.

`restore --record <file>` re-adds each removed edge exactly and re-checks for cycles.
Recovery from the original 11-edge incident is a single command with this round trip.

# SPEC — Beads Hygiene (`yf-beads-hygiene`)

> Per-skill SPEC for the read-only-first audit + gated repair of a beads dependency graph.
> Composed by the root macro `SPEC.md` under spec key **HYG**. Requirements use RFC-2119
> "shall"; *(testable)* items are the anchors a test names. Implements upstream #29.

## 1. Purpose & scope

`yf-beads-hygiene` audits and cleans the **content** of an already-healthy beads dependency
graph: it finds orphaned beads and dangling dependency edges and classifies gate-typed edges by
status so live gates are never mistaken for dangling. It is read-only by default; destructive
repair is confirmation-gated and reversible. It is the canonical trigger for any "clean up
beads" / "are there orphaned beads" request. It does **not** verify or repair beads config/DB
health — a wedged/corrupted or uninitialized DB routes to `yf-beads-init`.

## 2. Requirements (`REQ-HYG-NNN`)

### 2.1 Audit (read-only)

- **REQ-HYG-001** *(testable)* The audit shall be **read-only** — it shall never mutate the DB.
- **REQ-HYG-002** *(testable)* Edge targets shall be resolved with `bd show <id>` (which sees
  gate beads), **never** by membership in `bd list` output.
- **REQ-HYG-003** *(testable)* The audit shall operate over the **full universe** — `bd list
  --all` **plus** `bd list --all --type gate` — never the truncated default list, since
  `bd list` hides gates and truncates at 50 rows (gotcha owned by `yf-beads-extra` REQ-CLI-009).
- **REQ-HYG-004** *(testable)* Every dependency edge shall be classified into **exactly one** of:
  `true-orphan` (parent-child edge to a missing root), `truly-dangling` (`blocks` edge to a
  non-resolving target), `satisfied-gate` (target is a **closed** gate), `live-gate` (target is
  an **open** gate).
- **REQ-HYG-005** *(testable)* A `live-gate` edge shall **never** be reported as dangling
  (the #29 regression invariant). Gate-typed targets shall be classified by status: open =
  preserve (`live-gate`), closed = `satisfied-gate`.

### 2.2 Repair (gated, reversible)

- **REQ-HYG-006** *(testable)* Repair shall propose removals for **truly-dangling edges only** —
  never `live-gate`, `satisfied-gate`, or `true-orphan` findings.
- **REQ-HYG-007** Destructive repair shall require **explicit confirmation** before mutating
  (a `--yes` flag may bypass the prompt for non-interactive automation).
- **REQ-HYG-008** After any mutation the engine shall run `bd dep cycles` (post-mutation
  integrity check) and surface the land-the-plane push sequence (`bd dolt commit` + `bd dolt
  push` + `git push`).
- **REQ-HYG-009** *(testable)* Repair shall support a **round-trip restore** — a removal record
  that re-adds each removed edge exactly (`bd dep add <blocked> <blocker>`).

### 2.3 Health routing

- **REQ-HYG-010** *(testable)* On a **wedged/corrupted** DB the engine shall route to
  `yf-beads-init` (status `db_wedged`) rather than clean a broken store. It shall honor the
  false-negative invariant: `bd status --json` may return error JSON with exit 0; an
  initialized-but-wedged repo is classified wedged (route to init), not uninitialized.

## 3. Interfaces

- **CLI / scripts:** `scripts/beads_hygiene.py` (PEP 723, `uv run`) — subcommands `audit`
  (`--json`), `repair` (`--apply`, `--yes`, `--record <file>`), `restore` (`--record <file>`,
  `--apply`). `audit --json` emits `{edges_total, counts, findings, removable_count}`. Exit 2 =
  `db_wedged` (route to `yf-beads-init`).
- **Companion rule:** none — `user-invocable: true`, no always-loaded trigger rule; the trigger
  contract lives in the `SKILL.md` description.
- **Config / state:** none beyond the operator-named `--record` file for round-trip restore.

## 4. Guardrails (`GR-HYG-NNN`)

- **GR-HYG-001** *Drift:* treating `bd list` membership as the existence test. *Rule:* every edge
  target is resolved with `bd show` over the gate-inclusive full universe. *Why:* `bd list` hides
  gates and truncates — the exact #29 false positive.
- **GR-HYG-002** *Drift:* auto-removing "dangling" edges. *Rule:* only `truly-dangling` is
  removable, only after confirmation, and the removal is recorded for restore; live/satisfied
  gates and orphans are never removed. *Why:* a wrong removal un-gates live work.
- **GR-HYG-003** *Drift:* trying to repair a broken DB. *Rule:* a wedged/corrupted DB routes to
  `yf-beads-init`; hygiene operates only on a healthy DB's graph content. *Why:* the two skills
  own different layers (DB/config health vs graph content).
- **GR-HYG-004** *Drift:* restating `yf-beads-extra`'s CLI gotchas. *Rule:* gate semantics,
  `bd show` vs `bd list`, edge mutation, defensive JSON, and `bd dep cycles` are **referenced**
  from `yf-beads-extra`, not restated. *Why:* one source of truth per fact.

## 5. Verification

`scripts/test_beads_hygiene.py` (pytest via `uv run --with pytest`) drives the pure classifier
with in-memory fixtures: the four classes (REQ-HYG-004), the live-gate-never-dangling invariant
and the **#29 11-live-gate regression** (REQ-HYG-005), removable = truly-dangling only
(REQ-HYG-006), restore round-trip record shape (REQ-HYG-009), and the gate-hidden-from-universe
resolver path (REQ-HYG-002/003). The live `bd` layer (`load_universe`, `collect_edges`,
`db_is_wedged`) is exercised end-to-end against an isolated probe DB.

## 6. References

- `skills/yf-beads-hygiene/SKILL.md`; `skills/yf-beads-hygiene/scripts/beads_hygiene.py`.
- `skills/yf-beads-extra/SKILL.md` (gate/edge/JSON gotchas; `bd list` truncation; `bd dep cycles`).
- `skills/yf-beads-init/SKILL.md` + `protocols/BEADS_INIT.md` (DB health, false-negative invariant).
- Upstream #29 (`docs/plans/plan-012-james-dixson-a99822/references/upstream-29.md`).
- Root `SPEC.md` and `GUARDRAILS.md`.

# SPEC — Beads Hygiene (`yf-beads-hygiene`)

> Per-skill SPEC for the read-only-first audit + gated repair of a beads dependency graph.
> Composed by the root macro `SPEC.md` under spec key **HYG**. Requirements use RFC-2119
> "shall"; *(testable)* items are the anchors a test names. Implements upstream #29.

## 1. Purpose & scope

`yf-beads-hygiene` audits and cleans the **content** of an already-healthy beads dependency
graph along **two axes**:

- **Graph-content audit** (`audit`/`repair`/`restore`) — finds orphaned beads and dangling
  dependency *edges* and classifies gate-typed edges by status so live gates are never mistaken
  for dangling.
- **Reconcile** (`reconcile`) — the local↔upstream **active-vs-parked boundary**: classifies the
  local active set, lists **non-active** beads as hoist candidates (they belong upstream until a
  plan pulls them back), and flags **obsolete** upstream tracking issues.

It is read-only by default; destructive repair and the gated hoist are confirmation-gated and
reversible. Per the cross-skill **carve, hygiene PROPOSES and `yf-beads-upstream` EXECUTES**:
`reconcile --apply` never pushes or closes beads itself — it delegates each hoist to
`yf-beads-upstream`. It is the canonical trigger for any "clean up beads" / "are there orphaned
beads" request. It does **not** verify or repair beads config/DB health — a wedged/corrupted or
uninitialized DB routes to `yf-beads-init`.

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

### 2.4 Reconcile (local↔upstream boundary — read-only-first)

The reconcile axis is distinct from the graph-content audit (§2.1–2.3): the audit classifies
dependency **edges**; reconcile classifies **beads** against the local↔upstream active-vs-parked
boundary. It reuses the same read-only-first discipline and the same `db_wedged` routing.

- **REQ-HYG-011** *(testable)* The `reconcile` subcommand shall be **read-only by default** — it
  shall list findings without mutating the DB or any upstream issue. Mutation is reached only
  through the gated `--apply` path (REQ-HYG-015).
- **REQ-HYG-012** *(testable)* The **active set** shall be the single definition: a non-closed
  bead is **active** iff `status == in_progress`, OR (`status == open` AND `owner` non-empty,
  i.e. claimed), OR it is an **open** parent-chain ancestor (epic/molecule, walked to a fixed
  point) of an active bead. Every other non-closed bead (open-unclaimed, blocked, deferred) is
  **non-active**. Closed beads are excluded from both buckets. The classifier consumes the
  normalized `dep_type` field, so it is agnostic to the `dependency_type`/`type` source
  divergence (gotcha owned by `yf-beads-extra`).
- **REQ-HYG-013** *(testable)* **Non-active** beads shall be listed as **hoist candidates** (they
  belong upstream until a plan pulls them back); **active** beads shall never be listed for hoist.
- **REQ-HYG-014** *(testable)* An open upstream issue shall be classified **obsolete** only on a
  **mechanical delivered signal** — its linked plan's `plan.md` carries `Status: complete`, OR
  its tracking PR is merged. When neither signal is resolvable the issue shall be **flagged for
  human review**, never classified obsolete. Obsolete findings are **proposal-only**; reconcile
  shall **never auto-close** an upstream issue.
- **REQ-HYG-015** *(testable)* The gated `--apply` (with `--yes` to skip the prompt, `--record`
  to write a round-trip record) shall **delegate** each non-active hoist to `yf-beads-upstream`
  (`upstream.py hoist --issues <id> --dest <dest> --apply`) — the carve: hygiene proposes,
  upstream executes. Reconcile shall **never** push beads upstream or `bd close` them itself.
  The `--record` file is the reversal handle (`upstream.py unhoist --record <file>`).
- **REQ-HYG-016** *(testable)* On a **wedged/corrupted** DB `reconcile` shall route to
  `yf-beads-init` (status `db_wedged`) identically to the audit (REQ-HYG-010) — it reuses the
  same `db_is_wedged` check and `_route_to_init` exit-2 path, never cleaning a broken store.

## 3. Interfaces

- **CLI / scripts:** `scripts/beads_hygiene.py` (PEP 723, `uv run`) — subcommands `audit`
  (`--json`), `reconcile` (`--json`, `--apply`, `--yes`, `--record <file>`), `repair`
  (`--apply`, `--yes`, `--record <file>`), `restore` (`--record <file>`, `--apply`). `audit
  --json` emits `{edges_total, counts, findings, removable_count}`. `reconcile --json` emits
  `{active_count, non_active_count, counts, findings}` where `findings` carries
  `hoist_candidates`, `obsolete_upstream`, and `flag_for_review`. Exit 2 = `db_wedged` (route to
  `yf-beads-init`).
- **Cross-skill delegation (carve):** `reconcile --apply` shells the hoist to
  `yf-beads-upstream`'s `scripts/upstream.py` (resolved as a sibling under `skills/`); it never
  pushes or closes beads itself.
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
- **GR-HYG-005** *Drift:* hygiene pushing beads upstream or closing them itself. *Rule:* the
  reconcile carve is absolute — hygiene **proposes** (lists hoist candidates / obsolete issues);
  `yf-beads-upstream` **executes** (push + reversible `bd close`). `reconcile --apply` delegates
  every hoist to `upstream.py` and never auto-closes an upstream issue. *Why:* one owner for the
  push/close mechanics keeps the active-set definition single-sourced and the boundary auditable.
- **GR-HYG-006** *Drift:* flagging an upstream issue obsolete on a heuristic. *Rule:* obsolete
  requires a **mechanical** delivered signal (linked plan `Status: complete` or merged PR);
  otherwise flag-for-review, never auto-close. *Why:* a false obsolete flag that closed live work
  is the same drift failure the skill exists to remove.

## 5. Verification

`scripts/test_beads_hygiene.py` (pytest via `uv run --with pytest`) drives the pure classifier
with in-memory fixtures: the four classes (REQ-HYG-004), the live-gate-never-dangling invariant
and the **#29 11-live-gate regression** (REQ-HYG-005), removable = truly-dangling only
(REQ-HYG-006), restore round-trip record shape (REQ-HYG-009), and the gate-hidden-from-universe
resolver path (REQ-HYG-002/003). The live `bd` layer (`load_universe`, `collect_edges`,
`db_is_wedged`) is exercised end-to-end against an isolated probe DB.

For the reconcile axis the same harness drives the pure cores with fixtures: `classify_active`
over each active/non-active case incl. the open-ancestor walk (REQ-HYG-012/013),
`find_obsolete_upstream` over plan-complete / PR-merged / unresolvable signals (REQ-HYG-014), and
the gated `--apply` delegating via an injected `runner`/`script` so the hoist shell-out to
`yf-beads-upstream` is asserted without a live push (REQ-HYG-015).

## 6. References

- `skills/yf-beads-hygiene/SKILL.md`; `skills/yf-beads-hygiene/scripts/beads_hygiene.py`.
- `skills/yf-beads-extra/SKILL.md` (gate/edge/JSON gotchas; `bd list` truncation; `bd dep cycles`).
- `skills/yf-beads-init/SKILL.md` + `protocols/BEADS_INIT.md` (DB health, false-negative invariant).
- `skills/yf-beads-upstream/SKILL.md` (the hoist/unhoist executor; the carve's execution side).
- Upstream #29 (`docs/plans/plan-012-james-dixson-a99822/references/upstream-29.md`); #38/#17
  (`docs/plans/plan-013-james-dixson-0af2f8/plan.md` — the reconcile-policy plan).
- Root `SPEC.md` and `GUARDRAILS.md`.

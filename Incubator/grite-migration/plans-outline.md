---
title: Grite migration — plan outline
created: 2026-10-18
tags: [grite, plan-outline]
---

# Grite migration plan outline

Draft sequence of yf-plans. Each plan is scoped and approved through `/yf-plan` when it starts, so
this outline fixes order and intent, not content. Plans execute on short-lived branches cut from
`grite-migration` and merge back into it. The exception is **P-0**, which lands on `main` because
everything else depends on it. Rationale: [research/03-gap-analysis.md](research/03-gap-analysis.md).

## Prerequisites

### P-0 — yf-plan integration-branch landing (lands on `main`)

- Add `landing-strategy: integration:<branch>` (or similar) to `plan_manager.py`. The execute
  worktree is cut from `<branch>`, §6.1 merges back into `<branch>`, and the default-branch
  commit refusal treats `<branch>` the same way it treats `main`.
- Decide plan-root resolution when the incubator exists only on the integration branch (README Q2).
- SPEC-first: new REQ-BRANCH / REQ-PLAN entries, then code and tests.
- Without P-0, the fallback is `feature-branch` strategy plus a manual merge into `grite-migration`.
  That is workable for one or two plans, not for the whole migration.

### P-1 — grite viability spike and go/no-go (research, `grite-migration`)

- Reproduce and characterize: fresh-clone rebuild (#26/#27), worktree actor identity, the daemon
  JSON envelope, and behaviour at about 3k issues and 6k edges (replay the live corpus into a
  sandbox).
- Probe the open metadata design (per-key `context set` vs body block vs `meta:` labels).
- Decide among: adopt upstream as-is, contribute fixes and wait, pin a fork, or **stop**.
- Output: `yf-research` report plus a recorded decision. **No-go ends the migration.** P-2 still
  delivers value in that case.

### P-2 — bd characterization tests (lands on `main`; useful regardless)

- Live, sandboxed tests that pin the bd semantics yf depends on: the `ready` exclusions, gate
  visibility, the `mol pour` `id_mapping` and wrapper+gate shape, `--set-metadata` merge,
  `list` truncation, and `batch` atomicity.
- These become the conformance suite every tracker backend must pass.

## Phase A — build grite tooling

### A-1 — Tracker abstraction SPEC (SPEC-first)

- `REQ-TRK-*`: the verb set (about 15), the normalized JSON contract, error/exit semantics, and
  backend selection (`.yf/` config, per repo).
- `REQ-TRK-GRITE-*`: the grite convention scheme. It covers reserved labels (`type:`, `status:`,
  `priority:`, `parent:`, `discovered-from:`, `gate:`, `ephemeral`), metadata storage, the
  `external_ref` link, the `close_reason` comment, and the ready computation.
- Records the shim decision (provisional: rejected in favour of the intent-level layer).

### A-2 — Tracker layer with the beads backend

- Implement `yf tracker <verb>` (Rust kernel), plus a thin Python client for skill scripts and
  po-*. It wraps bd and normalizes JSON, which also retires the five ad-hoc parsers.
- Must pass the P-2 conformance suite against bd.

### A-3 — grite backend

- Implement the conventions from A-1 on grite: ready computation, claim (lock plus assignee),
  metadata, gates as typed issues, and sequential "batch" with read-back.
- Must pass the P-2 conformance suite against grite, with documented deviations.

### A-4 — yf pour engine

- Backend-neutral formula pour from the existing `.formula.toml`: vars, steps, gate steps, `needs`,
  ephemeral (wisp) mode, and burn.
- Emits a normalized `id_mapping` and drops the bd wrapper+gate pair.
- Retires `.beads/formulas/` staging for the grite backend.

### A-5 — Corpus migration tool

- `bd export` → grite replay with an ID map. It preserves types, status, edges, metadata,
  `external_ref` and `close_reason`, and runs a fidelity verifier that reads every write back.
- Dry-run on this repo's corpus of 2,754 issues.

## Phase B — integrate side by side

### B-1 — Port scripts to the tracker layer (beads backend)

- `plan_manager.py`, `close_cascade.py`, `verify_beads.py`, `research_manager.py`,
  `beads_hygiene.py` and `upstream.py` (reads, `external_ref`, tombstone).
- Behaviour-preserving: the full suite must stay green on beads.

### B-2 — Port prose to tracker verbs

- yf-plan and yf-research SKILL.md and coordinator agents, yf-beads-extra and yf-beads-authoring.
- Update `yf doctor` FormulaCheck to scan `yf tracker pour`.
- Prose-assertion tests (`test_gates.py` and similar) move with it.

### B-3 — Backend-neutral init/upstream skills

- `yf-tracker-init`: verify, init and repair, dispatched by backend. The beads half is the existing
  kernel; the grite half is new.
- Upstream config moves from `bd config` to `.yf/` config.
- `yf-beads-upstream` becomes backend-neutral (`yf-upstream`). Keep aliases while both backends live.

### B-4 — Dogfood on grite

- Switch `grite-migration` itself, or a sandbox clone, to the grite backend and run at least one
  real plan and one research project end to end.
- Record deviations and fix them before phase C.

## Phase C — remove beads

### C-1 — Migrate the corpus and flip the default

- Run A-5 on this repo and verify it.
- Default backend becomes grite. The beads backend stays available behind config for one release.

### C-2 — Remove beads tooling

- Delete the beads backend, `beads_init.rs` and the Dolt repair path, formula staging,
  `min-bd-version` gating and the bd harness-hook preservation.
- Retire the beads skills (`yf-beads-*`) or fold them into tracker skills.
- SPEC amendments retire the REQ-YF-PRE-006/007/010/011, REQ-BINIT-*, REQ-BEXTRA-* and related
  entries.
- po-* packages must have migrated first (cross-repo dependency).

## Phase D — optimize for grite

### D-1 — Simplify for grite

Remove the remaining bd-isms:

- the wrapper+gate pair
- 50-row truncation guards
- the Dolt-specific land-the-plane steps (`bd dolt push`, `git add .beads/`)

Replace them with grite equivalents: `grite sync` on land, and locks for claims.

### D-2 — Use grite-specific capabilities

- `context index/query` for agent code context.
- Lease locks for multi-agent coordination.
- Git-native sync for cross-clone work.

### D-3 — Upstream contributions

- A native `ready` query, issue states, per-issue metadata, MCP. Each one that lands upstream lets
  yf drop a convention.

## Dependency sketch

```text
P-0 ─┐
P-1 ─┼─(go)─> A-1 ─> A-2 ─> A-3 ─> A-4 ─> A-5
P-2 ─┘                │                     │
                      └─> B-1 ─> B-2 ─> B-3 ─┴─> B-4 ─> C-1 ─> C-2 ─> D-*
```

P-0, P-1 and P-2 are independent of each other and can run in parallel. A-2 needs P-2, because the
conformance suite is its acceptance criterion. B-1 can start once A-2 is done, before the grite
backend exists, because it runs on the beads backend.

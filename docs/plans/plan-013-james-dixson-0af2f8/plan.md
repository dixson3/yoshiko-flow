# Plan: Reconcile policy — local beads = active work only

**ID:** plan-013-james-dixson-0af2f8
**Author:** james-dixson
**Created:** 2026-06-24
**Status:** reconciling
**Epic:** beads-skills-mol-glo
**Phase log:**
- 2026-06-24 scoping: initial scope captured
- 2026-06-24 investigating: 2 experiments (skill architecture, bd mechanisms)
- 2026-06-24 drafting: plan v1 presented
- 2026-06-24 review: plan v1 presented (red-team REVISE)
- 2026-06-24 drafting: v2 — addressed red-team C1–C6 + missing items
- 2026-06-24 review: v2 red-team APPROVE (2 low polish notes folded into C.7/D.1)
- 2026-06-24 approved: operator approved
- 2026-06-24 intake: epic beads-skills-mol-glo poured
- 2026-06-24 executing: start gate resolved
- 2026-06-24 reconciling: post-execution reconciliation

## Objective

Make "local beads = actively-worked only" an enforced, mechanical policy instead of a manual
discipline. Non-active work lives upstream (GitHub issues) until explicitly pulled back down via
a `/yf-plan` plan. Deliver it as: (1) a **reconcile pass** in `yf-beads-hygiene` that flags
non-active local beads for hoist and detects obsolete upstream issues; (2) a **hoist-and-remove**
capability in `yf-beads-upstream` that auto-hoists follow-on beads at land-the-plane; (3) a
first-class **`custom.upstream.granularity`** config key (folds in #17), since hoist behavior
depends on coarse-vs-granular.

## Motivation

The operator keeps the local beads DB as an *active worklist* — only things under active
development should live locally; everything else belongs upstream until a plan pulls it back.
Today this is hand-enforced: on 2026-06-24 a manual reconcile closed an obsolete tracker (#35,
plan-012 delivered) and hoisted four idle beads (`tr0`→#27, `25d`→#17, `3ma`→#36, `phd`→#37)
plus the parked Epic 7 subtree (→#28), then closed them locally. That worked but was entirely
manual, easy to forget at land-the-plane, and has the same drift failure mode the beads skills
exist to remove. Two skills already own adjacent axes — `yf-beads-hygiene` (graph-content audit)
and `yf-beads-upstream` (push mechanics) — but neither reconciles the **local↔upstream
active-vs-parked boundary**. This plan adds that axis. Source: upstream issue #38 (and #17 for
the granularity knob).

## Glossary (adjacent concepts)

- **Active bead** — `status == in_progress`, OR (`status == open` AND `owner` non-empty, i.e.
  claimed), OR an **open** parent-chain ancestor (epic/molecule) of such a bead. Everything else
  non-closed (open-unclaimed, blocked, deferred) is **non-active**.
- **Follow-on bead** — a bead filed *during* a plan's execution. **Narrow (auto-eligible)
  signal:** carries a `discovered-from` edge into the plan's molecule/epic subtree **AND** is
  non-active. **Broad signal:** created under the subtree after intake — used for *gated
  proposals only*, never the unattended path (it can catch a bead still being worked).
- **Hoist** — ensure an upstream issue exists for a bead (create-or-map via the bd `External:`
  mapping), then **remove it locally** by `bd close` with a `close_reason` recording the upstream
  destination (reversible tombstone — never `bd delete`).
- **Un-hoist (restore)** — reopen a wrongly-hoisted bead from its tombstone: `bd update <id>
  --status open` using the destination captured in `close_reason` (the upstream issue stays).
  The gated reconcile path also writes a `--record` file for batch round-trip.
- **Obsolete upstream issue** — an open upstream issue whose tracked work is delivered, detected
  by a **mechanical** signal: the issue's linked plan folder has `Status: complete` in its
  `plan.md`, **or** the tracking issue's linked PR is merged. When neither signal is resolvable,
  the issue is **flagged for human review only**, never auto-proposed for close.
- **Granularity** — `coarse` (one tracking issue per plan-scale effort; current default) vs
  `granular` (one issue per hoisted bead). New config key `custom.upstream.granularity`.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #38 | Reconcile policy: local beads = active work only | include | The spec for this plan | Epics B, C, D |
| #17 | beads-upstream: machine-enforced upstream granularity config (coarse\|granular) | include | Folded in per scoping decision | Epic A |

## Investigation Findings

Full detail in `findings/exp-001-skill-architecture.md` and `findings/exp-002-bd-reconcile-mechanisms.md`.

- **yf-beads-upstream** is a read-only helper (`upstream.py` enumerate/mappings); pushes are
  `bd github push <ids>` (dry-run first, inline auth). Linkage is bd's `External:` line in
  `bd show`. **No granularity key exists** (REQ-BUP-043 unimplemented) — clean extension point.
  Close-time trigger lives in `protocols/UPSTREAM_TRACKING.md`. No test file yet.
- **yf-beads-hygiene** cleanly separates a live bd layer (`load_universe`, `collect_edges` with
  injectable `resolver`) from a pure classification core (`Edge.classify`, `classify_edges`).
  `audit`/`repair`/`restore` verbs; repair is gated (`--apply`/`--yes`/`--record`). Fixture-driven
  pytest, no live bd. New reconcile logic should mirror this live/pure split.
- **bd mechanisms:** `discovered-from` is a first-class edge (already used by agents);
  `created_at` + `--parent` scopes a plan subtree. `owner` (identity) vs `assignee` (display);
  active set computable from `status` + `owner` + `parent-child` ancestor walk. Edge-type field
  is `dependency_type` (`bd show`) vs `type` (`bd dep list`) — handle both. Custom config via
  `bd config set custom.upstream.granularity` (unset → `(not set)` exit 0 — inspect, don't trust
  exit code). Removal = `bd close -r` (reversible), not `bd delete`.

## Approach

Build a small **shared active-set classifier** as the foundation, then two consumers and the
config knob:

1. **Granularity config (Epic A)** — implement `custom.upstream.granularity` (`coarse|granular`,
   default `coarse`) in `upstream.py`; read it where hoist decides issue count. Closes #17's
   implementation gap (REQ-BUP-043). Foundational because hoist (Epic C) branches on it.
2. **Reconcile pass in yf-beads-hygiene (Epic B)** — a new `reconcile` subcommand parallel to
   `audit`. Read-only-first (matches the skill's discipline): computes the active set, lists
   **non-active local beads** as hoist candidates, and flags **obsolete upstream issues**
   (delivered plan-trackers). Proposals only; mutation is gated and delegates the actual push to
   yf-beads-upstream. Pure core (`classify_active`, `find_obsolete_upstream`) is fixture-tested.
3. **Hoist-and-remove in yf-beads-upstream (Epic C)** — a `hoist` operation (ensure upstream
   issue per granularity → `bd close` with destination reason) and **follow-on detection**
   (`discovered-from` into the plan subtree + created-after-intake). Wire **auto-hoist of
   follow-on beads into the land-the-plane close-time trigger** (`UPSTREAM_TRACKING.md`);
   standalone reconcile stays gated.
4. **Integration & docs (Epic D)** — cross-skill carve (hygiene proposes, upstream executes),
   SPEC/SKILL/README updates, manifest bumps, markdown-lint + drift-check, and upstream
   reconciliation of #38/#17.

**Division of labor (carve):** hygiene owns *detection/proposal* of the local↔upstream boundary
(a new reconcile axis, distinct from its graph-content audit); upstream owns *execution* (push +
local close) and the granularity knob.

**Classifier location — decided at intake (resolves red-team C3):** the active-set classifier is
authored **once** as a self-contained pure module that both skills carry, to preserve per-skill
install independence (#15's shared-package route is not landed and is out of scope here). Because
that is duplication-by-copy, Epic D authors an explicit **DRIFT-CHECK.md manifest edge** asserting
the two copies agree — the mitigation is provisioned, not aspirational. The reconcile active set
is the **single definition** (status + `owner` + ancestor walk); `upstream.py enumerate`'s
status-only `CANDIDATE_STATUSES` is refactored to consume it, so the two never diverge (resolves
the red-team "enumerate interaction" gap).

## Epics

### Epic A: Granularity config (`custom.upstream.granularity`) — resolves #17

- Issue A.1: Implement read of `custom.upstream.granularity` (`coarse|granular`, default
  `coarse`) in `upstream.py` — inspect for `(not set)`, never trust exit code. Add a
  `granularity` helper + `--json` exposure.
  - resolves-upstream: #17 (include)
- Issue A.2: Implement read of `custom.upstream.auto_hoist_followons` (default-deny: literal
  `"true"` enables the unattended land-the-plane path; anything else = propose-with-confirm),
  mirroring the `custom.upstream.enabled` short-circuit shape. (Resolves red-team C1.)
  - depends-on: A.1
- Issue A.3: SPEC — promote REQ-BUP-043 from specified-unimplemented to implemented; document
  both new keys in SKILL.md (init §) and README. Note coarse is the formalized existing default;
  `granular` is implemented but the **coarse path is the tested happy path** — also document
  coarse↔granular transition/coexistence (existing coarse trackers survive a flip via the
  `External:` dedup mapping). (Resolves red-team C6.)
  - depends-on: A.1
  - depends-on: A.2
- Issue A.4: Tests — `test_upstream.py` covering granularity read (coarse/granular/unset) and
  `auto_hoist_followons` (true/false/unset → default-deny); factor pure parts (`parse_json_array`,
  `external_for`, candidate filter) for testability.
  - depends-on: A.1
  - depends-on: A.2

### Epic B: Reconcile pass in yf-beads-hygiene

- Issue B.1: Pure core — `classify_active(beads, edges)` (active vs non-active per glossary, incl.
  the `parent-child` ancestor walk) and `find_obsolete_upstream(issues, plan_status_lookup)`
  (obsolete = linked plan `Status: complete` OR linked PR merged; otherwise flag-for-review).
  No I/O; the delivered-signal lookups are injected for fixture testing. (Resolves red-team C4.)
- Issue B.2: Live layer — `reconcile` subcommand: build universe (reuse `load_universe`), compute
  active set, enumerate non-active local beads as hoist candidates, query upstream (`gh issue
  list`/`upstream.py enumerate`) to flag obsolete issues. `--json` output shape mirroring
  `audit`.
  - depends-on: B.1
- Issue B.3: Gated proposal/execution — `reconcile --apply`/`--yes`/`--record`: confirm, then
  delegate hoist to yf-beads-upstream (Epic C) per bead; record for round-trip. Standalone
  reconcile is always gated (read-only-first).
  - depends-on: B.2
  - depends-on: C.1
- Issue B.4: SPEC (`REQ-HYG-011+`) + SKILL.md + README — the reconcile axis, its carve vs the
  content audit, the active-set definition, and the wedged-DB routing reuse.
  - depends-on: B.2
- Issue B.5: Tests — fixture-driven coverage for `classify_active` (each active/non-active case,
  ancestor walk) and `find_obsolete_upstream`, in the existing `test_beads_hygiene.py` style.
  - depends-on: B.1

### Epic C: Hoist-and-remove + land-the-plane auto-hoist in yf-beads-upstream

- Issue C.1: `hoist` operation — ensure upstream issue per `granularity` (create-or-map via
  `External:`; coarse → one tracker per plan, granular → per bead), dry-run first, then
  `bd close -r "<destination>"`. Reversible (close, not delete). Respects the never-bare-sync and
  inline-auth safety invariants.
  - depends-on: A.1
- Issue C.2: Follow-on detection — **narrow signal** (auto-eligible): `discovered-from` edge into
  the plan molecule/epic subtree **AND** status non-active. **Broad signal** (created-after-intake
  under subtree): returned separately, **gated-proposal-only**. Handle `dependency_type` (`bd
  show`) vs `type` (`bd dep list`) field divergence. (Resolves red-team C2.)
- Issue C.3: Land-the-plane hoist — **default = propose the follow-on batch with a single
  confirm** (matches today's confirm-required push contract). The **no-prompt** path runs only
  when `custom.upstream.auto_hoist_followons == "true"` (A.2) and is restricted to the **narrow
  signal**. Non-follow-on reconcile stays gated. Wire into `protocols/UPSTREAM_TRACKING.md`
  (close-time trigger) + SKILL.md procedure; bump manifest. (Resolves red-team C1.)
  - depends-on: C.1
  - depends-on: C.2
  - depends-on: A.2
- Issue C.4: `un-hoist` / restore path — document and implement reopening a wrongly-hoisted bead
  from its `close_reason` tombstone (`bd update <id> --status open`), plus the gated `--record`
  batch round-trip. (Resolves red-team Missing: rollback story.)
  - depends-on: C.1
- Issue C.5: SPEC (`REQ-BUP-*`/`REQ-OP-*`) + README — hoist, narrow vs broad detection, default-
  gated vs opt-in auto, un-hoist, safety invariants preserved.
  - depends-on: C.1
- Issue C.6: Tests — extend `test_upstream.py`: hoist issue-count by granularity, narrow-signal
  detection (fixture deps), **the false-positive guard (in-progress bead created-after-intake →
  NOT auto-hoisted)**, close-reason format, dry-run-first, un-hoist round trip. (Resolves
  red-team Missing: false-positive test.)
  - depends-on: C.1
  - depends-on: C.2
- Issue C.7: Port the active-set classifier copy into `upstream.py` (canonical core authored in
  B.1) and **refactor `enumerate` to consume it** in place of its status-only `CANDIDATE_STATUSES`
  — the explicit owning issue for the single-definition refactor. Add an **enumerate-parity
  regression test** so existing land-the-plane worklist behavior is preserved (only the
  owner/ancestor refinement changes, intentionally). (Resolves pass-2 low concerns.)
  - depends-on: B.1
  - depends-on: A.1

### Epic D: Integration, docs, reconciliation

- Issue D.1: Author/extend the **DRIFT-CHECK.md manifest edge** asserting the canonical classifier
  (B.1) and its `upstream.py` copy (C.7) agree (the C3 mitigation, provisioned). Bootstrap the
  manifest if absent.
  - depends-on: B.1
  - depends-on: C.7
- Issue D.2: Cross-skill carve verification — hygiene proposes / upstream executes; the single
  active-set definition is honored (enumerate refactored to consume it). Run yf-drift-check over
  the D.1 edge; markdown-lint all edited `.md`.
  - depends-on: B.4
  - depends-on: C.5
  - depends-on: D.1
- Issue D.3: Manifest bumps for both skills' protocol rules (`manifest_update.py`); commit rule +
  manifest together. Update CHANGELOG.
  - depends-on: B.4
  - depends-on: C.3
- Issue D.4 (reconcile step): Update upstream — close/annotate #38 and #17 as resolved; per the
  new policy, hoist any follow-on beads this plan itself creates.
  - depends-on: D.2
  - depends-on: D.3

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: bd reconcile mechanisms available (D1)
- Type: auto
- Condition: bd ≥ 1.0.5 with `discovered-from` edge type, `bd list --parent`/`--created-after`,
  `custom.*` config, and `bd close --reason` (the reversible-tombstone removal) — all confirmed
  present in investigation. (Test broadened per red-team C5.)
- Test: `bd dep add --help | grep -q discovered-from && bd list --help | grep -q created-after && bd close --help | grep -q reason && bd config get custom.upstream.enabled`
- Blocks: A.1, B.1, C.2
- Instructions: present on bd 1.0.5; if absent, upgrade bd.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: D.4

## Risks & Mitigations

- **Two divergent "active" definitions** (hygiene vs upstream drift apart). *Mitigation:* a single
  classifier definition authored once and copied per-skill for install independence, with an
  explicit DRIFT-CHECK.md edge (D.1) asserting the copies agree; `enumerate` is refactored to
  consume it rather than its status-only `CANDIDATE_STATUSES`.
- **Auto-hoist removes a bead the operator still wanted local.** *Mitigation:* the unattended
  no-prompt path is **off by default** (`custom.upstream.auto_hoist_followons` default-deny) and,
  when enabled, restricted to the **narrow** follow-on signal (`discovered-from` AND non-active) —
  an in-progress bead is never eligible; default behavior is propose-with-confirm. Removal is `bd
  close` (reversible tombstone) and the close_reason records the destination for one-command
  un-hoist (C.4).
- **False "obsolete" flag closes a live upstream issue.** *Mitigation:* obsolete detection is
  proposal-only (gated), requires a **mechanical delivered signal** (linked plan `Status:
  complete` or merged PR), falls back to flag-for-human-review when unresolvable, and never
  auto-closes.
- **`bd config` unset false-negative** (exit 0 with `(not set)`). *Mitigation:* inspect output,
  never branch on exit code (encoded in the existing beads false-negative invariant).
- **Coarse-vs-granular ambiguity at hoist** when the key is unset. *Mitigation:* default
  `coarse`, matching AGENTS.md's documented operative default.

## Success Criteria

- `custom.upstream.granularity` is read and honored; unset defaults to `coarse` (#17 / REQ-BUP-043
  satisfied; verified by test).
- `yf-beads-hygiene reconcile` lists non-active local beads and obsolete upstream issues
  read-only, with a gated `--apply` that hoists via yf-beads-upstream and records a round-trip.
- At land-the-plane, follow-on beads are **proposed for hoist with a single confirm by default**;
  the no-prompt path activates only under `custom.upstream.auto_hoist_followons=true` and only for
  the narrow signal. Removal is reversible and records the destination; a documented un-hoist
  reopens a wrongly-hoisted bead. An in-progress bead created after intake is **never**
  auto-hoisted (tested).
- The 2026-06-24 manual reconcile is reproducible as a single gated `reconcile --apply`
  (regression anchor).
- Both skills' SPEC/SKILL/README updated, manifests bumped, all edited markdown lint-clean, and
  #38/#17 reconciled upstream.

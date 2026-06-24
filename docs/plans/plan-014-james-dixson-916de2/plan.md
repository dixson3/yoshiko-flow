# Plan: `_shared/` package — retire the duplicated active-set classifier (#15)

**ID:** plan-014-james-dixson-916de2
**Author:** james-dixson
**Created:** 2026-06-24
**Status:** complete
**Epic:** beads-skills-mol-mqa
**Phase log:**
- 2026-06-24 scoping: initial scope captured
- 2026-06-24 investigating: 3 experiments (shared vendoring, yf-plan delegation, drift-check shape)
- 2026-06-24 drafting: plan v1 presented (#27+#25+#15)
- 2026-06-24 review: red-team REVISE
- 2026-06-24 drafting: v2 — re-scoped to #15 only (split per operator); #27+#25 → follow-on plan
- 2026-06-24 review: red-team REVISE (cycle 2) — pin vendoring shape
- 2026-06-24 drafting: v3 — pinned shape (b) regenerate-fenced-block; folded N2/N3/Missing
- 2026-06-24 approved: operator approved
- 2026-06-24 intake: epic beads-skills-mol-mqa poured
- 2026-06-24 executing: start gate resolved
- 2026-06-24 reconciling: execution complete; entering merge-back
- 2026-06-24 complete: plan complete

## Objective

Resolve **#15** for its one *proven* duplication: extract the active-set classifier (introduced
in plan-013 as a hand-pasted verbatim copy across yf-beads-hygiene and yf-beads-upstream) into a
single canonical `_shared/active_set.py`, vendored into each consuming skill's `scripts/` as a
**committed copy** by a repo-time **sync tool**, policed by DRIFT-CHECK edges. This lands first
and establishes the `_shared/` + sync-tool + drift-edge pattern that a **follow-on plan**
(yf-change-validation, #27 + the worktree-uv discipline #25) will build on.

## Motivation

plan-013 deliberately copied the active-set classifier verbatim from yf-beads-hygiene into
yf-beads-upstream (install-independence: skills must be independently installable, so they can't
import each other), and added a `DRIFT-CHECK` `e-classifier-copy` edge to police the copy. That
copy is **hand-maintained** (`upstream.py:122-269` is a literal pasted block with a "do NOT edit
one without the other" banner) — exactly the silent-rot duplication #15 targets. The red-team
review of the original (larger) plan-014 established two facts that scoped this work down:
yf-drift-check is **prose, not Python**, so there is no shared manifest/bootstrap machinery to
extract and no second Python consumer for a generic library — the *only* genuine cross-skill
Python duplication is the classifier. So #15's real, provable win is mechanizing that one copy.
Source: #15 (driver). #27/#25 are deferred to a follow-on plan that depends on this one.

## Glossary (adjacent concepts)

- **`_shared/`** — a top-level repo dir (outside the `skills/` embed root, so `yf` never treats
  it as a skill) holding canonical Python helpers.
- **Vendoring (option B, shape (b)) — regenerate-the-fenced-block.** The classifier lives as a
  marker-fenced region inside each consuming script (as today — `upstream.py:122-269`). A
  repo-time **sync tool** overwrites that fenced region in-place from the canonical
  `_shared/active_set.py` — it does **not** introduce a sibling `import` or a new file. Each
  script stays self-contained (the repo's one-script-one-file convention) and the single-file
  test loaders + skill README layout fences are untouched. Install copies the regenerated scripts
  verbatim — **zero `yf` Rust changes**. (Shape (a), a true sibling `import`, was rejected: it
  breaks the `spec_from_file_location` test loaders and relaxes the one-file convention.)
- **Canonical vs copy / authority** — `_shared/active_set.py` is the single **fixed-authority**
  source; each skill's regenerated fenced region is **derived**. A DRIFT-CHECK `value-equal`
  divergence (region vs canonical) is the *copy* drifting (FAIL on the copy), never the canonical.
- **Enforcement point** — the vendored copies stay honest via the existing **yf-drift-check
  on-edit trigger** over the canonical→copy edges (fires when either file is edited); the sync
  tool's `--check` mode is a CI/manual convenience that reports the same divergence.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #15 | Consolidate duplicated Python helpers (shared package route) | include | Scoped to the one proven duplication (the active-set classifier) | Epics A, B, C |
| #27 | yf-change-validation skill | exclude | Deferred to a follow-on plan that depends on this `_shared/` foundation | — |
| #25 | `env -u VIRTUAL_ENV uv run` inside a worktree | exclude | Deferred to the same follow-on plan (it's a yf-change-validation sub-requirement) | — |

## Investigation Findings

`findings/exp-001-shared-vendoring.md` is the load-bearing finding for this plan;
`exp-002-yfplan-delegation.md` and `exp-003-driftcheck-shape.md` were gathered for the original
combined scope and now inform the **follow-on** (#27) plan, not this one.

- **No `install.py`/`install.sh`** — install is the `yf` Rust binary (verbatim embed→deploy;
  `upgrade --prune` deletes files not in the embedded tree). A deploy-time fan-out would require
  Rust changes to embed/prune/integrity-hash. So vendoring is **option B**: a repo-time sync
  tool writing **committed** copies; install copies them verbatim → **zero Rust changes**.
- **`_shared/` location:** top-level (repo root), *outside* `#[folder="../skills"]`, so it is
  never enumerated as a skill (`frontmatter::load_skills` requires a `SKILL.md`).
- **DRIFT-CHECK is pairwise:** one Source, one Derived per edge. One canonical → 2 copies needs
  **2 edges** (`e-active-set-copy-hygiene`, `e-active-set-copy-upstream`), 1 canonical node +
  2 copy nodes, 2 §3 `value-equal` contract rows, and §6 trigger rows (canonical path → both
  edges; each copy path → its own). Authority **inverts** from today: the canonical becomes
  `_shared/active_set.py`; both skill files become derived (today hygiene is the authority).
- **drift-check is prose, not Python** — confirmed no `scripts/`/`.py`. So `_shared/` holds only
  the classifier (a genuine 2-consumer helper); no generic manifest-bootstrap library is built
  here (it would have had a single consumer).

## Approach

Foundation-first, three small epics:

1. **`_shared/` + sync tool (Epic A).** Create top-level `_shared/active_set.py` as the canonical
   classifier (lifted byte-for-byte from the plan-013 implementation). Write a repo-time sync
   tool (`_shared/sync.py`, itself a `uv run --script` + PEP-723 helper) that, from a small
   declared map (`_shared/active_set.py` → `[yf-beads-hygiene, yf-beads-upstream]`), **overwrites
   the marker-fenced classifier region in-place** inside each consuming script from canonical,
   plus a `--check` mode (non-zero on any divergence) for CI/manual use. The committed scripts
   (with the regenerated region) are source, not gitignored.
2. **Retire the hand-maintenance + DRIFT-CHECK migration (Epic B).** Keep the classifier as a
   fenced region in each script but make it **generated** (run `_shared/sync.py`), removing the
   "do NOT edit one without the other" hand-maintenance banner in favor of a generated-by marker;
   no sibling `import`, no new file. Migrate DRIFT-CHECK: re-point the canonical to
   `_shared/active_set.py` and **delete** the old pairwise `e-classifier-copy`, then add 2 derived
   copy edges (one per consumer), keeping the manifest internally consistent (nodes ↔ edges ↔ §3
   ↔ §6). Both skills' test suites stay green; yf-drift-check passes over the new edges.
3. **Docs + reconcile (Epic C).** CHANGELOG + a short `_shared/README.md` documenting the
   pattern and the enforcement point; reconcile #15 upstream and file the #27+#25 follow-on
   tracking note (the follow-on plan depends on this).

**Carve / non-goals:** no generic manifest/bootstrap library (drift-check is prose; one Python
consumer ≠ shared). No yf-change-validation engine, no toolchain inference, no yf-plan §6.1.5
delegation, no worktree-uv work — all deferred to the #27 follow-on plan.

## Epics

### Epic A: `_shared/` package + sync tool

- Issue A.1: Create top-level `_shared/active_set.py` — the canonical classifier
  (`classify_active`, `_directly_active`, `_has_owner`, `_is_closed`, `ActiveSetReport`, the
  `Edge`/`ACTIVE_*`/`PARENT_CHILD`/`OPEN`/`IN_PROGRESS`/`CLOSED_STATUSES` constants), lifted
  byte-for-byte from the plan-013 hygiene implementation. Add `_shared/README.md` (pattern +
  enforcement point).
- Issue A.2: Repo-time sync tool `_shared/sync.py` (a `uv run --script` + PEP-723 helper) — reads
  a declared canonical→consumers map and **overwrites the marker-fenced classifier region
  in-place** inside each consuming script from `_shared/active_set.py` (with a generated-by marker,
  no `import`, no new file); `--check` mode exits non-zero on any region divergence (CI/manual).
  Idempotent.
  - depends-on: A.1
- Issue A.3: Tests for the sync tool — regeneration is idempotent; `--check` detects a tampered
  region and an absent/garbled marker fence; the generated-by marker is present; round-trips.
  - depends-on: A.2

### Epic B: retire the copies + DRIFT-CHECK migration

- Issue B.1: Make the fenced classifier region **generated** in both scripts — convert
  `upstream.py:122-269` and the in-lined hygiene region to a `_shared/sync.py`-regenerated region
  (replace the "do NOT edit one without the other" hand-maintenance banner with a generated-by
  marker); run `_shared/sync.py`. **No sibling `import`, no new `scripts/active_set.py` file** →
  no new generic `script` node and no skill README layout-fence change.
  - depends-on: A.2
- Issue B.2: Both skills' test suites green against the regenerated region
  (`test_beads_hygiene.py` + `test_upstream.py`) — the single-file `spec_from_file_location`
  loaders are unchanged (shape (b) keeps each script self-contained).
  - depends-on: B.1
- Issue B.3: DRIFT-CHECK migration — **re-point/replace** the existing `classifier-canonical`
  node (today the hygiene file) to `_shared/active_set.py` (fixed authority), **delete** the old
  pairwise `e-classifier-copy` edge + its hygiene-as-authority framing, then add 2 derived copy
  nodes + 2 `value-equal` edges (`-hygiene`, `-upstream`) comparing each fenced region to
  canonical, plus §6 trigger rows (canonical → both edges; each region's file → its own edge).
  Keep the manifest internally consistent (a half-updated `approved: yes` manifest itself FAILs
  drift-check).
  - depends-on: B.1
- Issue B.4: Run yf-drift-check over the new edges + markdown-lint the manifest; confirm green
  and the authority direction is correct (a tampered region FAILs the copy, not the canonical).
  - depends-on: B.2
  - depends-on: B.3

### Epic C: docs + reconciliation

- Issue C.1: CHANGELOG entry + `_shared/README.md` finalized (pattern, the canonical→copy model,
  the enforcement point = yf-drift-check on-edit trigger, `--check` as CI convenience).
  - depends-on: B.4
- Issue C.2 (reconcile step): Update upstream — **annotate-and-narrow #15** (one helper
  delivered, by region-regeneration vendoring, not import-sharing — keep it open so the follow-on
  retains the #15 thread, or narrow its scope explicitly); file/annotate the #27+#25 follow-on
  tracking note recording that the follow-on plan depends on this `_shared/` foundation. Hoist any
  follow-on beads this plan creates.
  - depends-on: C.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: C.2

## Risks & Mitigations

- **Option B trades install-simplicity for N committed copies + N drift edges** (the same
  keep-in-sync shape #15 indicts). *Mitigation:* the enforcement point is concrete and already
  exists — the yf-drift-check on-edit trigger fires on any edit to a canonical or copy file and
  FAILs on divergence; `--check` is a CI/manual backstop. The copies are *generated* by the sync
  tool, not hand-edited, so the rot vector (manual edit of one copy) is removed in normal flow.
- **Regenerating the fenced region breaks yf-beads-hygiene/upstream.** *Mitigation:* A.1 lifts
  the classifier byte-for-byte (same symbols); shape (b) keeps each script self-contained (no
  `import`, no test-loader changes); B.2 re-runs both suites; the drift edge catches divergence.
  The change is mechanical, not behavioral.
- **DRIFT-CHECK manifest left half-migrated FAILs itself.** *Mitigation:* B.3 does the full
  nodes↔edges↔§3↔§6 update in one pass; B.4 runs drift-check to confirm internal consistency
  before close.
- **Authority inversion blames the wrong file on a future drift.** *Mitigation:* B.3 explicitly
  sets `_shared/active_set.py` as fixed authority and both skill files as derived; B.4 verifies a
  tampered copy FAILs the copy.

## Success Criteria

- `_shared/active_set.py` is the single canonical classifier; `_shared/sync.py` regenerates the
  fenced region in yf-beads-hygiene + yf-beads-upstream in-place and `--check` detects a tampered
  region (no sibling `import`, no new file).
- The plan-013 hand-maintenance banner is **gone**; the fenced region in both scripts is
  generated from canonical, each script stays self-contained, and both test suites are green.
- DRIFT-CHECK is migrated: `classifier-canonical` re-pointed to `_shared/active_set.py` (fixed
  authority), the old pairwise `e-classifier-copy` deleted, 2 derived region edges added;
  yf-drift-check passes and a tampered region FAILs the *copy*.
- CHANGELOG + `_shared/README.md` document the pattern + enforcement point; #15 is reconciled
  upstream (scoped to the proven duplication) and the #27+#25 follow-on is recorded as depending
  on this foundation.

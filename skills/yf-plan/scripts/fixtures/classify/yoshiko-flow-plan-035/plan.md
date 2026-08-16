---
deliverable_class: standard
source_plan: plan-035-james-dixson-74d7ae
source_repo: yoshiko-flow
---
# Plan: Rework and expand the web/ documentation set for accuracy, voice, and completeness (beads/upstream workflow, formulas concept, VOICE.md + density reduction, phase-model validation + diagrams, harness-agnostic plan-mode framing + framework survey, .yf/ artifact-management reconciliation)

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #97 | Docs↔reality: what does yf-plan 'execution spanning multiple environments' actually mean today? | include | The driver for workstream 1 — corrected wording in `web/` + a note on the real capability/limitation. Tombstoned from plan-034 (`yf-5p9x`). | Workstream 1 (beads/upstream accuracy) |

_This plan also **files new** upstream issues (not resolves): one per skill emitting legacy
`.yf/` paths, and one for the `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit` move
(workstream 6). Those are outputs, tracked in the relevant epic, not rows above._

## Epics

### Epic 1: VOICE.md foundation (keystone)
Author the voice contract that governs every prose rewrite, and file the future-skill follow-on.

- Issue 1.1: **Author repo-root `VOICE.md`.** Docs/technical variant per EXP-04: Purpose/scope →
  House voice (matter-of-fact, no sycophancy, engineer/operator audience in one line) → **Density
  & exposition** (load-bearing: one-idea sentences, list/table/diagram thresholds, "more
  exposition, not more density") → Do/Don't (incl. anti-meta-narration) → 2–3 before/after pairs
  drawn from real `web/` prose → mini-glossary. Cite `web/content/pages/why.md` +
  `architecture.md` as in-repo exemplars.
- Issue 1.2: **File the `yf-voice` follow-on bead** (deferred local voice-skill hoist reusing the
  `yf-drift-check` trigger shape + the `voice-stylist`/`readability-critic` agents). A bead only —
  no build. `discovered-from` this plan.
  - depends-on: 1.1

### Epic 2: Accuracy corrections (resolves #97) — beads/upstream + `.yf/` layout
Fix every factual doc error surfaced by EXP-01/EXP-02, applying VOICE.md. Docs-only.

- Issue 2.1: **Beads/upstream workflow rewrite (resolves #97).** Rewrite `why.md:31-34` (kill the
  false "push the repo → someone picks up where the gate left off") and `beads-concepts.md:8`;
  state the accurate model (local-only DB, worktree-shared same-machine, never git-pushed; upstream
  = issue mirror; capability-blocked work → **upstream issue referencing `plan.md`**, then
  **re-pour locally from the git-committed plan folder/formula** on the capable clone — the issue
  is the coordination pointer, **not** the bead-state transfer medium; **no live cross-machine bead
  sharing**). Reconcile against the already-accurate `beads-concepts.md` "upstream strategy"
  section. Add the honest capability/limitation note.
  - depends-on: 1.1
  - resolves-upstream: #97 (include)
- Issue 2.2: **`.yf/<short>/config.local.json` doc corrections (~13 non-convention surfaces).**
  Correct docs that teach the legacy root dotfile / `.state/` layout to the canonical
  `.yf/<short>/config.local.json` + `.yf/<short>/preflight.json` (`<short>` = `yf-`-stripped):
  yf-plan `spec/data.md`/SKILL/README/test-harness/smoke.sh, yf-research
  `spec/data.md`/SPEC/SKILL/README/prerequisites, yf-beads-init/upstream/incubator SPEC paras, and
  the stale `preflight.rs:489` comment. **Leave web `.yf/` refs alone** (verified accurate).
  **Direction (C2 — avoid manufacturing new spec↔code drift):** for the **yf-plan** spec/doc
  surfaces that mirror the *current code bug* (e.g. `spec/data.md` REQ-DATA-020 says
  `.yf/yf-plan/preflight.json` because `plan_manager.py` actually writes the full name), **document
  current reality** and add an explicit **forward-pointer to Issue 3.1** ("full-name today; short-
  name `.yf/plan/` after 3.1") — never "correct" the spec ahead of the code. Surfaces where the
  binary already emits canonical (everything the Rust `yf` owns) are corrected outright. Note in-doc
  that `yf migrate` performs legacy→canonical and preflight does **not** auto-migrate (that gap is
  Issue 3.1). Expect on-edit `yf-drift-check` / `yf-skill-authoring` fan-out on the SPEC/SKILL edits.
  - depends-on: 1.1
- Issue 2.3: **`yf-skill-authoring` SURFACE_CONVENTION rewrite (C3 split).** The
  SURFACE_CONVENTION (+ its SKILL/SPEC references) is the *convention source* still teaching
  `.state/<skill>/` + `/.<skill>.local.json`; it is a substantive rewrite, not a path swap, so it
  is its own issue. Rewrite it to teach the canonical `.yf/<short>/{config.local.json,preflight.json}`
  layout with the short-name resolver, matching the binary. Same C2 direction (document reality +
  forward-pointer where code lags). This edit fires `yf-skill-authoring` / `yf-drift-check` on-edit
  — expected, non-blocking.
  - depends-on: 1.1

### Epic 3: File upstream code-fix issues (per boundary)
Three precisely-scoped issues; each cites EXP-02 evidence + the `plan.md`/finding section. No code.

- Issue 3.1: **Issue — yf-plan `plan_manager.py` `.yf/` drift.** Full-name `STATE_DIR=.yf/yf-plan/`
  vs binary's `.yf/plan/`; config read only from legacy `.yf-plan.local.json` not canonical
  `.yf/plan/config.local.json`. Ask for short-name alignment + canonical-first read + preflight
  auto-migration.
- Issue 3.2: **Issue — yf-change-validation legacy-only seed.** `change_validation.py:44` reads
  only legacy `.yf-plan.local.json` for the validate-cmd seed; align to canonical.
- Issue 3.3: **Issue — `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`.** Resolve the
  `.yf/`-gitignored vs marker-committed semantics; add `migrate.rs` rename for auto-migration;
  update the yf-markdown-lint rule/marker docs. (Marker has no code consumer — mostly rule/doc +
  migration.)

### Epic 4: Formulas as a first-class concept + ER diagram
New Concepts page documenting formulas (small reusable DAG patterns), alongside skills/states/agents.

- Issue 4.1: **d2 ER diagram + naba flair.** Per the EXP-06 ER spec: Formula→Var/Step/GateSpec;
  Step→Bead (gate-step 1→2 wrapper/gate compilation); Formula→Molecule/Wisp→Epic→Bead; Bead→Agent.
  One generic diagram with a 3-row inset for the three standard formulas. d2 source-of-truth beside
  the render (`yf-diagram-authoring`), naba flair pass. **Acceptance (M3):** the naba flair pass
  must preserve the light-mode/white-bg legibility of the base d2 render — no regression in
  readability vs the plain d2 output. (No VOICE.md dep — diagrams are terse labels, not prose;
  runs parallel to Epic 1.)
- Issue 4.2: **Formulas concept page.** Explain formulas = small reusable bead-DAG templates;
  document the three standard formulas (`plan-execute` 1-step gate + post-pour injection;
  `plan-investigate` 0-step wisp; `yf-research` 7-step chain + fan-out); embed the 4.1 diagram;
  cross-link glossary/beads-concepts/workflows. Apply VOICE.md.
  - depends-on: 4.1, 1.1

### Epic 5: Phase-model validation + new diagram
Correct the phase-model depiction and re-diagram it (EXP-03).

- Issue 5.1: **Corrected phase-model d2/naba diagram.** 7 phase nodes; UPSTREAM as once-per-project
  preamble; SCOPE⇄INVESTIGATE + PLAN backtracks + PLAN internal REVISE loop; session boundary before
  EXECUTE; statuses banded under owning phases; `ready-for-approval`/`approved` gate states;
  parked/stale overlays on `approved`; COMPLETE as RECONCILE's terminal status; no EXECUTE→PLAN edge.
  d2 source beside render + naba flair. **Acceptance (M3):** naba flair preserves light-mode/white-bg
  legibility vs the base d2 render. (No VOICE.md dep — runs parallel to Epic 1.)
- Issue 5.2: **Phase-model prose correction** in `lifecycle.md`/`workflows.md`: 7 phases (COMPLETE =
  status), PLAN owns 3 statuses, UPSTREAM once-per-project, parked/stale overlays, and the honesty
  fix (statuses are **not** enum-enforced; `update-status` is free-form) + the **real-but-implicit**
  framing (phases surface via status/`log.md`/gates, never narrated). Embed the 5.1 diagram.
  - depends-on: 5.1, 1.1
- Issue 5.3: **File the status-enum-hardening follow-on bead (M2).** The 5.2 honesty fix documents
  that the 9-status vocabulary is not enum-enforced (`update-status` is a free-form writer,
  EXP-03 rec #4). File a `discovered-from` follow-on bead proposing optional validation hardening
  in `plan_manager.py`. A bead only — no build (mirrors Issue 1.2).
  - depends-on: 5.2

### Epic 6: Why-page harness-agnostic reframe + framework survey
Make "why yf-plan" honest and compelling (EXP-05).

- Issue 6.1: **Harness-agnostic plan-mode framing.** Reframe "Claude Code has a native plan mode…"
  → "many coding agents have a plan mode…"; **drop the blanket single-session/single-machine
  strawman**; lead the contrast with single-machine/non-portable state + controlled plan drift +
  merged-state re-validation + upstream reconcile. Apply VOICE.md.
  - depends-on: 1.1
- Issue 6.2: **Framework survey section + comparison table.** New "Why" section: steelman the
  surveyed frameworks (Spec Kit, Kiro, BMAD, Taskmaster, Aider architect, Cline/Roo, Ralph, GSD,
  grill-me, **claude-protocol** as the honest closest analog); a comparison table; the sharpest
  differentiator = **content-bound fingerprint enforced across the session boundary**. Code-anchored,
  non-strawman. **Acceptance (C4):** run a fact-check pass over every comparison-table cell before
  landing; **date-stamp or omit** star counts (they rot fast) — prefer a qualitative
  "widely-adopted / niche" signal with an as-of date over hard numbers.
  - depends-on: 6.1

### Epic 7: Reconcile + prove (exit gate)
Residual density, cross-doc consistency, nav, and the build/lint exit gate.

- Issue 7.1: **Residual density pass** on pages not touched by Epics 2/4/5/6 (EXP-06: `workflows.md`
  EXECUTE/RECONCILE/subagent-tables/yf-research bullets where not already reworked; `harness-tune.md`
  config-merge + honesty-note run-ons). Apply VOICE.md (split paragraphs, tables, bullets).
  - depends-on: 2.1, 2.2, 4.2, 5.2, 6.2
- Issue 7.2: **Cross-doc reconciliation + nav + exit gate.** Sweep the whole `web/` set for any
  residual misleading beads/upstream or `.yf/` claim (grep the EXP-01/EXP-02 patterns); wire nav
  entries for the new formulas page (Concepts) and any new anchors. **Exit gate (specified):**
  (1) `uv run <yf-markdown-lint>/scripts/markdown_lint.py <changed pages>` — the **full** audit (no
  `--rules` subset); (2) `uv run --with-requirements web/requirements.txt pelican content -s
  web/pelicanconf.py -o <tmp>` — **build succeeds with zero Pelican warnings**. **Pass criterion
  net of known false positives:** the plan-034 ML003 "broken link" reports for Pelican
  **site-absolute `/slug/` URLs** are a known linter/Pelican-routing mismatch (they also fire on
  the shipped `harness-tune.md`) — those specific ML003 lines do **not** fail the gate *provided*
  the target slug/anchor is confirmed to exist and the Pelican build is clean; **any other** lint
  class, or any Pelican warning/error, **does** fail it.
  - depends-on: 7.1

## Risks & Mitigations

| # | Risk | Mitigation |
|:--|:-----|:-----------|
| R1 | The beads/upstream rewrite over- or under-states the real capability (#97), re-introducing a subtler inaccuracy. | Every claim in Issue 2.1 is quoted from EXP-01 evidence (file:line); reconcile against the already-accurate `beads-concepts.md` "upstream strategy" section; the honest "no live cross-machine bead sharing" limitation note is mandatory, not optional. |
| R2 | Doc corrections drift from the code again over time (the exact failure that created this plan). | Corrections describe **shipped** behavior and cite the code oracle; where a doc states a concrete path, prefer the canonical form the binary emits. The three Epic-3 issues fix the *code* drift (Python full/short + legacy read) so docs and code reconverge. |
| R3 | Scope creep — the `.yf/`/marker code changes get implemented here despite the docs-only boundary. | Hard boundary: Epic 3 files **issues only**. Any code change is out of scope and tracked upstream for a later plan. |
| R4 | VOICE.md is authored but not actually applied, so density persists. | VOICE.md (Epic 1) **gates** every prose epic (dependency edges); Epic 7's residual pass + exit gate is the backstop; the EXP-06 worklist is the concrete checklist. |
| R5 | The framework survey ages quickly or reads as strawman marketing. | EXP-05 is code-anchored and names **claude-protocol** as the honest closest analog; the contrast leads with verifiable yf-plan mechanics (fingerprint, merged-state validation), not vague superiority; sources are cited. |
| R6 | New/edited pages break links or the Pelican build (the plan-034 ML003-style noise). | Epic 7.2 exit gate = full `yf-markdown-lint` audit + clean Pelican build; internal links use `/slug/` + verified anchors; ML003 Pelican-absolute-URL false positives are understood (see plan-034) and judged against a real build, not the linter alone. |
| R7 | Diagrams (d2/naba) drift from the corrected prose. | d2 source-of-truth lives beside each render (`yf-diagram-authoring`); the phase-model + formula diagrams are authored from the EXP-03/EXP-06 validated specs, in the same epics as their prose. |

## Success Criteria
- **#97 resolved:** `why.md` and every adjacent `web/` doc state the accurate beads/upstream model
  (local-only, worktree-shared same-machine, never git-pushed; capability-blocked → upstream issue →
  re-pour on capable clone) with the honest no-live-cross-machine-sharing note; no doc claims shared
  beads span machines. (Epic 2)
- **`.yf/` layout accurate:** ~13 non-convention doc surfaces + the `yf-skill-authoring`
  SURFACE_CONVENTION corrected to `.yf/<short>/config.local.json` (spec surfaces that mirror the
  live code bug document current reality with a forward-pointer to Issue 3.1 — no new spec↔code
  drift); web refs verified unchanged; three upstream code-fix issues filed (yf-plan
  `plan_manager.py`, yf-change-validation, `.markdown-lint-on-edit` move) each citing evidence.
  (Epics 2–3)
- **Upstream tracking complete:** the coarse `plan-035 execution tracking` issue is filed at intake
  (AGENTS.md convention), distinct from #97 and the three code-fix issues; #97 updated/closed at
  reconcile. (Intake + Epic 2 + RECONCILE)
- **Formulas documented:** a Concepts page defines formulas as reusable DAG patterns, documents the
  three standard formulas, and embeds a d2 ER diagram (source beside render) with naba flair; linked
  in nav. (Epic 4)
- **Phase model validated & re-diagrammed:** prose corrected (7 phases, COMPLETE=status, non-enum
  honesty, real-but-implicit framing); a nicer d2/naba phase diagram embedded. (Epic 5)
- **Why-page honest & compelling:** harness-agnostic framing; single-session strawman removed;
  code-anchored framework survey + comparison table + the fingerprint differentiator; claude-protocol
  named. (Epic 6)
- **Voice + density:** repo-root `VOICE.md` exists and governs the rewrites; the EXP-06 dense
  offenders (esp. `workflows.md` EXECUTE) are restructured into exposition/tables/bullets; `yf-voice`
  follow-on bead filed. (Epics 1, 7)
- **Exit gate green:** full `yf-markdown-lint` audit clean over changed pages + a **0-warning Pelican
  build**; no residual misleading claim on a cross-doc grep sweep. (Epic 7)

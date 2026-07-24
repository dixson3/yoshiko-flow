---
type: Plan
okf_spec: OKF-PLAN
id: plan-035-james-dixson-74d7ae
author: james-dixson
created: '2026-07-23'
status: complete
deliverable_class: standard
fingerprint: 33d82ea998db883444c466a80ec5b1937a78c12c3f56f8124b8b7a753ffd3115
epic: yf-mol-6x8
---
# Plan: Rework and expand the web/ documentation set for accuracy, voice, and completeness (beads/upstream workflow, formulas concept, VOICE.md + density reduction, phase-model validation + diagrams, harness-agnostic plan-mode framing + framework survey, .yf/ artifact-management reconciliation)

**ID:** plan-035-james-dixson-74d7ae
**Author:** james-dixson
**Created:** 2026-07-23
**Status:** complete
**Deliverable-class:** standard
**Epic:** yf-mol-6x8
**Fingerprint:** 33d82ea998db883444c466a80ec5b1937a78c12c3f56f8124b8b7a753ffd3115

## Objective
Rework and expand the `web/` documentation set so it is **accurate** (matches the shipped
`yf` implementation), **well-voiced** (less dense, more expository, governed by an explicit
VOICE.md), and **more complete** (formulas documented as a first-class concept; a validated,
re-diagrammed phase model; harness-agnostic plan-mode framing with a competing-framework
survey). Where a doc mismatch is rooted in *code* that should change, file an upstream issue
rather than fixing it here (scope is docs + issue-filing, per operator decision).

Six workstreams:

1. **Beads/upstream workflow accuracy (resolves #97).** The docs still imply execution can
   "span multiple environments" via shared beads. Reality: the bead DB is **local** to one
   repo clone, shared **only across worktrees**, and **never pushed via git**; work blocked by
   a local-machine capability is captured as an **upstream issue** that references the relevant
   `plan.md` section, and the work is **re-poured locally from the git-committed plan
   folder/formula** on a capable clone — the issue is the **coordination pointer**, not the
   medium that transfers bead state. Rewrite "Why yf-plan" accordingly and **reconcile the same
   misleading claim across every adjacent `web/` doc**. Validate the corrected workflow against
   the `yf-beads-init` / `yf-beads-upstream` / `yf-plan` implementations.
2. **Formulas as a first-class concept.** Document formulas (small, reusable bead-DAG
   patterns) alongside skills / plan-states / agents. Show the standard yf-plan formulas
   (`plan-execute`, `plan-investigate`, and yf-research's formula) as a **d2 entity-relation
   diagram** with **naba flair**; explain reusability.
3. **Voice + density.** Author a repo-root **VOICE.md** (adapting `dixson3/writing`'s
   `blog-voice` skills — possibly as a repo-local voice skill first, a future `yf-voice`
   hoist) and use it to **reduce paragraph density** across the doc set (more exposition,
   tables, bullets, diagrams — the "Execute" section is the canonical offender).
4. **Phase-model validation + diagram.** Validate the documented Phase Model against actual
   runtime experience/implementation, correct any drift, and produce a **nicer d2/naba**
   phase-model diagram.
5. **Harness-agnostic plan-mode framing + framework survey.** Reframe "Claude Code has a
   native plan mode…" as "**many coding agents** have a plan mode…", re-confirm the
   single-session/single-machine claim still holds, and add a **live-researched** survey +
   steelman of popular planning/spec frameworks (Grill Me, Socratic, The Claude Protocol,
   GSD, …) and how yf-plan differs — as a **new section on the Why page**.
6. **`.yf/` artifact-management reconciliation.** Correct doc references to the sidecar layout
   the implementation actually uses (`.yf/<short>/config.local.json`, e.g. `.yf/plan/…`, NOT
   the legacy root `.yf-plan.local.json`); **file one upstream issue per skill** whose
   implementation still emits legacy paths; and file an upstream issue to move
   `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit` with **automatic preflight
   migration**.

## Motivation
The `web/` site (plan-031) and its plan-034 buildout shipped documentation that has since
**drifted from the implementation** and reads **too densely** for a newcomer. Concretely: the
"Why yf-plan" page still sells a multi-environment shared-beads execution model that the
product deliberately walked away from (beads are now local-only, worktree-shared — the exact
question tracked by **#97**); several pages restate that same misleading claim; the artifact
layout the docs describe (`.yf-plan.local.json` root dotfiles) was superseded by the
`.yf/<short>/config.local.json` sidecar (plan-023) but the docs never caught up; formulas — a
load-bearing concept in how yf-plan actually works — are undocumented; the phase model may not
match daily lived experience; and the plan-mode framing is Claude-Code-specific and makes no
case against the crowded field of competing planning frameworks. Left alone, a cold reader is
misled about how the system works and under-sold on why yf-plan is worth adopting.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #97 | Docs↔reality: what does yf-plan 'execution spanning multiple environments' actually mean today? | include | The driver for workstream 1 — corrected wording in `web/` + a note on the real capability/limitation. Tombstoned from plan-034 (`yf-5p9x`). | Workstream 1 (beads/upstream accuracy) |

_This plan also **files new** upstream issues (not resolves): one per skill emitting legacy
`.yf/` paths, and one for the `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit` move
(workstream 6). Those are outputs, tracked in the relevant epic, not rows above._

## Scope decisions (operator, 2026-07-23)
- **Boundary:** docs + upstream-issue filing. Code migrations (`.yf/` layout, markdown-lint
  marker move) are **filed as issues**, not implemented here.
- **VOICE.md:** repo-root, governs all human-facing prose. Investigate adapting
  `dixson3/writing`'s `blog-voice` skills; may land as a **repo-local voice skill** first, a
  future `yf-voice` hoist.
- **Framework survey:** **live web research** authorized; lands as a new section on the Why page.
- **Diagrams:** **d2 source-of-truth + naba flair** (per `yf-diagram-authoring`).

## Investigation Findings
Six experiments completed (full findings in `findings/exp-0N-*.md`). Headlines:

- **EXP-01 — beads/upstream workflow (#97): suspected reality CONFIRMED; fix is docs-only.**
  The bead DB is local-only Dolt under `.beads/` (`bd config set dolt.local-only true`,
  gitignored + `git rm --cached`), **never committed/pushed via git**; shared **only across
  worktrees of one clone** (INV-2 git-common-dir, same machine). "Upstream" is a `gh`/`glab`/Jira
  **issue mirror**, orthogonal to `bd dolt push` — coarse per-plan, reversible tombstones.
  Cross-machine handoff moves via the **git-committed plan folder + coarse tracking issue**, from
  which beads are **re-poured locally** on the capable clone. **No live cross-machine bead-state
  sharing exists today.** Correction targets: `why.md:31-34` (the false "push the repo, someone
  picks up where the gate left off"), `beads-concepts.md:8`; source-of-truth to reconcile against
  is `beads-concepts.md`'s already-accurate "upstream strategy" section.
- **EXP-02 — `.yf/` layout: Rust binary correct; Python drift + 3 code-fix issues.** Canonical:
  `.yf/<short>/config.local.json` + `.yf/<short>/preflight.json`, `<short>` = `yf-`-stripped
  (`plan`, not `yf-plan`); legacy root dotfile survives only as a read-time fallback; `yf migrate`
  moves legacy→canonical; **preflight does NOT auto-migrate**. Real Python drift: `plan_manager.py`
  uses full-name `STATE_DIR=.yf/yf-plan/` (binary writes `.yf/plan/`) and reads config only from
  the legacy dotfile. **~9 doc surfaces** need correction (yf-plan `spec/data.md`, SKILL/README;
  all yf-research config/state refs; yf-beads-init/upstream/incubator SPEC paras; the whole
  `yf-skill-authoring` SURFACE_CONVENTION still teaching `.state/` + root dotfile; a stale
  `preflight.rs:489` comment). **Web `.yf/` refs are ACCURATE** (harness-tune manifest).
  **Upstream code-fix issues:** (1) yf-plan `plan_manager.py` short/full + legacy-only config read
  (primary); (2) yf-change-validation `change_validation.py:44` legacy-only validate-cmd seed
  (minor); (3) yf-markdown-lint marker move — no code consumes the marker, but the
  `.yf/`-is-gitignored vs marker-is-committed semantics must be resolved + optional `migrate.rs`
  rename.
- **EXP-03 — phase model: substantially accurate; 4 refinements + 1 honesty fix.** COMPLETE is a
  terminal *status* inside RECONCILE §6.4, not a phase (**7 phases**, REQ-PHASE-001); PLAN owns 3
  statuses (`drafting→review→ready-for-approval`); UPSTREAM is **once-per-project**;
  `parked`/`stale-approved` are **overlays** on `approved`, not statuses. **Honesty fix:** docs
  imply the 9 statuses are enum-enforced, but `update-status` is a **free-form writer, no
  validation** — doc-enforced only. Phases are **real-but-implicit**: a faithful designer's
  abstraction that the runtime never narrates (users see status + `log.md` phase-log + gate
  prompts). Validated model to diagram captured in the finding.
- **EXP-04 — VOICE.md: docs/technical variant, local skill deferred.** `blog-voice` (at
  `~/workspace/dixson3/writing`) is mature but blog-specific; reusable = the repo-root-manifest
  pattern, the **Readability/density section wholesale**, the anti-meta-narration Do/Don't, and
  two future-hoist agents (`voice-stylist`, `readability-critic`). Recommended repo-root VOICE.md
  shape: Purpose → House voice → **Density & exposition (load-bearing)** → Do/Don't → 2–3
  before/after pairs → mini-glossary; fold a one-line engineer/operator audience in (no separate
  AUDIENCE.md); cite `why.md`/`architecture.md` as in-repo exemplars. `yf-voice` skill = **future
  follow-on bead**, not now.
- **EXP-05 — framework survey: reframe the differentiator, drop the strawman.** Widely adopted:
  GitHub **Spec Kit** (~110k★, SDD flagship, resumable), AWS **Kiro**, **BMAD-METHOD**,
  **Taskmaster** (~28k★), **Aider architect**, **Cline/Roo Plan-Act**, the **Ralph loop**;
  niche/relevant: **grill-me**, **GSD**, and the honest closest analog **claude-protocol** (beads
  + worktree-per-task + hooks). **Sharpest differentiator:** approval is a **content-bound
  fingerprint enforced across the session boundary** — content changes hard-block execution until
  re-approval; no surveyed framework does this. **Correction:** the blanket
  single-session/single-machine claim is a **strawman** (Spec Kit/Ralph/GSD/BMAD are multi-session);
  lead instead with single-machine/non-portable state + controlled plan drift + merged-state
  re-validation + upstream reconcile, and **name claude-protocol** rather than claim sui generis.
- **EXP-06 — density worklist + formula inventory.** Top offenders (all in `workflows.md`, the
  19 KB largest page): the **EXECUTE** bullet (canonical), the **RECONCILE** run-on, the two
  **subagent lists** (→ tables), the yf-research phase bullets; then `harness-tune.md`
  config-merge/honesty-note run-ons. Formulas: **`plan-execute`** (1 declared human `start-gate`
  step; epics/issues/gates injected post-pour), **`plan-investigate`** (0-step wisp; N experiments
  injected then burned), **`yf-research`** (7-step linear chain + retrieve fan-out). Finding
  carries a full **ER-diagram spec** (Formula→Var/Step/GateSpec; Step→Bead gate-step 1→2
  compilation; Formula→Molecule/Wisp→Epic→Bead) recommending one generic diagram with a 3-row inset.

## Approach
**Docs + upstream-issue filing only** (operator boundary): no `yf` behavior change, so **no SPEC
epic** and no coverage-gate concern. Work is sequenced so the **voice contract lands first** and
governs every rewrite, the **accuracy fixes** are grounded in cited findings, and a final
**reconciliation pass** guarantees no residual misleading claim and a clean Pelican build.

Design pillars:

1. **VOICE.md is the keystone (Epic 1 → gates the prose epics).** A repo-root VOICE.md (EXP-04
   shape) is authored first; every subsequent rewrite epic applies its density/exposition rules,
   so we do not re-litigate voice per page. The `yf-voice` local-skill hoist is a **filed
   follow-on bead**, not built here.
2. **Accuracy is code-grounded, not vibes (Epic 2).** The beads/upstream rewrite (#97) and the
   `.yf/<short>/config.local.json` doc corrections quote the EXP-01/EXP-02 evidence; the already-
   accurate `beads-concepts.md` "upstream strategy" section is the reconciliation anchor. Web
   `.yf/` refs are left alone (verified accurate).
3. **Code fixes leave as upstream issues (Epic 3), per boundary.** Three precisely-scoped issues
   (yf-plan `plan_manager.py`, yf-change-validation, yf-markdown-lint marker move) — a deliberate
   per-skill exception to the coarse convention, explicitly requested. Each references the EXP-02
   evidence and the relevant `plan.md`/finding section so it is re-poured accurately later.
4. **Concept + model completeness with real diagrams (Epics 4–5).** Formulas become a documented
   first-class concept (d2 ER diagram + naba flair, per `yf-diagram-authoring`); the phase model
   is corrected (7 phases, COMPLETE-as-status, non-enum honesty, real-but-implicit framing) and
   re-diagrammed. Both diagrams keep d2 source-of-truth beside the render.
5. **Why-page honesty (Epic 6).** Harness-agnostic framing, drop the single-session strawman, add
   the code-anchored steelman survey + comparison table, lead with the fingerprint differentiator,
   name claude-protocol.
6. **Reconcile + prove (Epic 7).** Residual density pass on untouched pages, a cross-doc sweep for
   any surviving misleading claim, nav wiring for new pages, then the **full `yf-markdown-lint`
   audit + clean Pelican build** as the exit gate.

## Approach notes
- **No capability gate** — the toolchain is **verified present in `context.md`** (d2 0.7.1, naba,
  pelican 4.11.0, plus bd/git/uv/python/gh/glab/claude) and live web research already completed in
  INVESTIGATE. There is no unmet environment prerequisite.
- **Reconcile gate + step (required):** #97 is an *included* upstream issue, so RECONCILE updates/
  closes it referencing the corrected docs. The three **newly-filed** code-fix issues (Epic 3) are
  plan *outputs*, not reconciled.
- **Coarse plan-035 tracker (M1):** per the AGENTS.md convention (precedent #13/#14/#16), a single
  coarse `plan-035 execution tracking` issue is filed at **intake** — distinct from both #97 (an
  included input) and the three Epic-3 code-fix issues (outputs). It links the plan folder + epic.

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

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate (upstream #97 incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step (update/close #97 referencing the corrected `web/` docs)

_No capability gate: no environment prerequisite. Live web research completed in INVESTIGATE; d2 +
naba present per `context.md`._

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

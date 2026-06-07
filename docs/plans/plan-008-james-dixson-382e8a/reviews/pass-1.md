# Plan Red-Team: plan-008-james-dixson-382e8a — Pass 1

**Presented:** 2026-06-06
**Conformance (pre-pass):** PASS
**Status:** RESOLVED (frozen) — all concerns addressed in plan v2; cleared for approval.

## Verdict: REVISE (resolved in plan v2)

## Strengths
- Core technical claim verified against the real repo: `install.py:resolve_install_set`
  (lines 83–117) closes over `depends-on-skill` unconditionally — there is genuinely no
  soft-dep concept, so the "instruction-level guidance, not a `depends-on-skill` edge"
  decision is correct and well-grounded. EXP-002 is accurate.
- Dependency-direction reasoning is stronger than the plan states: bdplan/bdresearch are
  `skill-group: beads`, diagram-authoring is `skill-group: utility`. A real edge would
  force-install a utility skill across a group boundary (install.py logs this as a
  cross-group pull, lines 106–115). The instruction-level approach sidesteps that.
- Injection points exist and are right-sized: `skills/bdplan/agents/planner.md` (31 lines)
  and bdresearch agents (`packager.md`, `synthesizer.md`) are present and small.
- The recent revision (preflight = `command -v d2` only; Chromium warm-up owned by the
  external dotfiles bootstrap hook) is the right call. EXP-001 documented OS-specific cache
  paths; probing them would false-negative. d2 v0.7.1 + rsvg-convert confirmed on PATH.
- DRIFT-CHECK.md auto-covers the new skill via `skills/*/SKILL.md`, `.../README.md`,
  `.../scripts/*.py` globs (lines 27–33) — no manifest edit needed, as EXP-002 claims.

## Concerns
- **`diagrams/` folder contradicts bdplan's existing `assets/` convention** — severity: high
  `plan_manager.py` line 303 scaffolds an `assets/` folder into every plan, and line 428
  documents it verbatim as "diagrams, attachments, generated artifacts." bdplan already
  designates `assets/` as the home for diagrams. The plan introduces a parallel `diagrams/`
  folder and Issue 2.3 only says "confirm `diagrams/` is distinct from `assets/`" — it never
  resolves the contradiction. Result: two artifact folders with overlapping purpose;
  `plan_manager.py` keeps creating an empty `assets/` while diagrams land in `diagrams/`.
  Recommendation: Either (a) use the existing `assets/` for bdplan (matching #6's original
  proposal), reserving `diagrams/` only for bdresearch; or (b) migrate bdplan to `diagrams/`
  with an explicit task to update `plan_manager.py` (line 303 scaffold + line 428 doc),
  `SKILL.md`, `spec/data.md`, `README.md`. Make it a first-class issue, not a 2.3 sub-bullet.

- **bdresearch injection point asserted but not pinned down** — severity: medium
  Plan says "bdresearch synthesis/packaging stage" but `packager.md` has no existing
  diagram/figure logic. The plan never commits to which agent (synthesizer vs packager)
  owns diagram generation, nor where in the research output tree the PNG is referenced.
  Recommendation: In Issue 2.2, name the exact agent file and the exact output artifact that
  references the PNG. packager.md is the likelier owner — confirm and state it.

- **#6's `plan_manager.py render-diagrams` helper and captor audit silently dropped** — severity: medium
  #6 (claimed superseded, "carries forward") explicitly asked for a `render-diagrams
  <plan_dir>` subcommand and a captor.md portability audit (PNG exists per diagram). This
  plan relocates regeneration to the skill's `render.py render-dir` (reasonable) but never
  states the plan_manager/captor pieces are intentionally not carried. "Carries #6 forward"
  overclaims.
  Recommendation: Either add the captor portability check (does each `diagrams/*.d2` have a
  matching `.png`?) as an explicit issue, or state in the upstream table that the
  plan_manager/captor pieces of #6 are deliberately dropped. Don't claim full carry-forward.

- **Self-verify gate (Issue 1.5) reads PNGs but has no objective legibility criterion** — severity: low
  "Read each PNG to confirm white-bg/legibility" is subjective. White-bg is checkable;
  cross-domain "legibility" is not a re-runnable gate.
  Recommendation: Reduce the gate to objective checks (PNG exists, opaque white corner
  pixel, non-zero dimensions); treat domain legibility as an operator eyeball step.

- **Plan's own `context.md` is an unfilled template** — severity: low
  Every section in `context.md` is boilerplate. `plan_manager.py _audit_plan` enforces
  non-empty context sections and will FAIL the portability audit, blocking a clean intake.
  Recommendation: Fill context.md's required sections (project environment, runtime
  assumptions) before intake.

## Missing
- No statement of where the skill source lives vs. installs (`skills/` authoring vs
  `.{surface}/skills/` install, install.py line 144). One confirming line would help.
- No mention of the README Prerequisites **union** edge (`e-prereqs-union`, DRIFT-CHECK
  line 82): adding `depends-on-tool: [d2]` requires adding `d2` to the project README
  Prerequisites union table, not just the index table (Issue 1.4 mentions only the index).
- No rollback/uninstall consideration for reverting to mermaid — minor; plan keeps
  `~/.claude/skills/mermaid` untouched.

## Gate Assessment
Capability Gate (`command -v d2 && d2 --version`) is valid, runnable, verified live (d2
v0.7.1). Correctly scoped to block only render-dependent issues (1.5, 2.x). Start Gate is
standard. Weakness: Issue 1.5's subjective "legibility" criterion (low concern) — tighten.
No gratuitous gates.

## Upstream Assessment
- **#6 supersede:** Defensible (reframe mermaid→d2, inline→dedicated skill, extend to
  bdresearch). But "carries #6's requirements forward" overclaims — the `render-diagrams`
  subcommand and captor audit are dropped without acknowledgment (medium concern). Tighten
  the supersede note to list carried vs relocated/dropped pieces.
- **#7 exclude:** Correct. Markdown link hygiene is a separate concern.
- **Coarse granularity:** Consistent with AGENTS.md (one coarse tracking issue per plan;
  precedent #13/#14/#16). Success criteria correctly call for a single coarse issue.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|---|---------|----------|------------|--------|
| 1 | `diagrams/` vs existing `assets/` convention | high | Operator chose: keep `diagrams/` everywhere, correct `assets/` semantics. New first-class **Issue 2.4** updates `plan_manager.py` (scaffold `diagrams/` + fix line 428 doc), `spec/data.md`, bdplan README so `assets/`=attachments, `diagrams/`=diagrams. Decision #4 + Success Criteria updated. | resolved |
| 2 | bdresearch injection point not pinned | medium | Issue 2.2 now names `skills/bdresearch/agents/packager.md` (packaging stage) as owner and the report body / `_index.md` as the PNG reference site, with rationale (packager assembles final artifacts, not synthesizer). | resolved |
| 3 | #6 render-diagrams/captor carry-forward overclaim | medium | Upstream table rewritten to list **carried** (heuristics, source/render pairing, naming, regeneration, prereq check), **relocated** (`render-diagrams`→`render.py render-dir`), **re-homed** (captor PNG-exists audit → `render.py check-dir`, added to Issue 1.2). Nothing silently dropped. | resolved |
| 4 | Issue 1.5 subjective legibility criterion | low | Issue 1.5 gate is now objective (PNG exists, non-zero dims, opaque white corner pixel + `check-dir`); domain legibility demoted to operator eyeball, not pass/fail. | resolved |
| 5 | context.md unfilled template | low | `context.md` Project environment / Operator identity / Runtime assumptions filled with real content (plan scoped after 2026-04-05 activation, so not grandfathered). | resolved |

**Missing items** also addressed: README **Prerequisites union** edge (`e-prereqs-union`) added to Issue 1.4 (add `d2` row); skill source-vs-install path noted in Issue 1.4.

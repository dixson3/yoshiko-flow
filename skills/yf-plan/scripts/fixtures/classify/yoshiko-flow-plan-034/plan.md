---
deliverable_class: standard
source_plan: plan-034-james-dixson-ac6633
source_repo: yoshiko-flow
---
# Plan: Post-plan-033 follow-ups — per-harness drift axis + codex block-size-budget check + web/ docs buildout

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|

_No upstream issues incorporated. This plan resolves **local** follow-on beads (`yf-252c`,
`yf-297v`, `yf-pxet`, `yf-rd33`, `yf-7ntv`, `yf-3d13`), closed at reconcile. `yf-5p9x` was hoisted
to upstream **#97** and tombstoned before scoping (out of scope). A single coarse upstream tracking
issue for this plan is filed at intake per the project convention (AGENTS.md)._

## Epics

### Epic 1: SPEC amendment (SPEC-first gate)
Land the two new requirements in `SPEC.md` before any code. Epics 2–3 depend on this.

- Issue 1.1: **Per-harness settings-drift-axis requirement.** Add `REQ-YF-TUNE-026` — the read-only
  `yf doctor` settings-drift axis (`SettingsDriftCheck`, `REQ-YF-TUNE-009`) shall run for every
  harness with a config profile (codex/opencode), diffing on-disk merged config against the harness
  profile; and a **per-harness managed-block drift** check shall report, **distinctly from** the
  existing aggregate `rule_drift` report, whether each AGENTS.md harness's (codex/opencode/pi)
  yf-managed `BEGIN/END` block matches the current minimized bundle. Read-only; reports divergence,
  never writes. Revise `REQ-YF-TUNE-011`'s deferral note to record the drift axis **delivered**.
  Amendment-log plan-034 entry.
- Issue 1.2: **Codex block-size-budget requirement.** Add `REQ-YF-TUNE-027` — codex rule deploy (and
  the drift axis) shall compute the projected **global `~/.codex/AGENTS.md`** size (content + managed
  block) against the **effective on-disk** `project_doc_max_bytes` (read from `~/.codex/config.toml`,
  default **32768** when absent — not the profile's 65536) and **warn** (never truncate/block) when it
  approaches the cap, naming the cap and projected size. The REQ shall document the **single-file
  scope limitation** (global `~/.codex/AGENTS.md` only, not the full multi-file concatenation).
  - depends-on: 1.1

### Epic 2: Per-harness settings-drift axis (`yf-252c`)
Extend `harness/drift.rs` + the `yf doctor` axis to codex/opencode/pi. Read-only. Grounded in the
existing `REQ-YF-TUNE-008/009` pattern.

- Issue 2.1: **Per-harness config drift (registration + tests).** Register the existing
  `SettingsDriftCheck` (`doctor/checks.rs`) for codex and opencode — `from_env("codex")` /
  `from_env("opencode")` — so `yf doctor` surfaces each harness's on-disk-config-vs-profile drift
  read-only. The check is already harness-generic and the read is already format-aware (JSON/TOML via
  plan-033), so this is primarily wiring + tests, not a new engine; do **not** touch `harness/drift.rs`
  (the separate REQ-YF-TUNE-008 CI test). Tagged test `REQ-YF-TUNE-026`: a seeded drifted codex
  `config.toml` and opencode `opencode.json` each report the injected divergence; a clean config
  reports none.
  - depends-on: 1.1
- Issue 2.2: **Per-harness managed-block drift (new, named distinctly).** Add a check — reported
  **separately from** the existing aggregate `rule_drift` report and named to disambiguate (e.g.
  "managed-block drift") — that detects, for each AGENTS.md harness (codex/opencode/pi), whether the
  yf-managed `BEGIN/END` block matches the current `minimize::irreducible_core_bundle()`; report drift
  read-only (a stale/edited managed block, or an absent block where tune would deploy one). Tagged test
  `REQ-YF-TUNE-026`: a hand-edited managed block reports drift; a current one does not; it does not
  collide with or double-count the existing `rule_drift` axis.
  - depends-on: 2.1

### Epic 3: Codex block-size-budget check (`yf-297v`, plan-033 R8/F7)
Warn before a codex `AGENTS.md` managed block risks the concatenation cap.

- Issue 3.1: **Budget check + warning.** Compute the projected **global `~/.codex/AGENTS.md`** size
  (existing content + managed block) against the **effective on-disk** `project_doc_max_bytes` (read
  from `~/.codex/config.toml`, default **32768** when absent — not the profile's 65536); emit a
  **warning** (never truncate/block) at/above the ≥90% threshold, naming the cap and projected size.
  Wire it into the codex rule-deploy path and the drift axis. Scope is the single global file (not the
  full concatenation) — documented in the warning. Tagged test `REQ-YF-TUNE-027`: a block+content near
  the effective cap warns; well under does not; the absent-config path uses the 32768 default; the
  warning names the cap and projected size.
  - depends-on: 1.1

### Epic 4: `web/` documentation buildout
Four Pelican pages. Independent of the SPEC epics (documentation of shipped behavior). Author the
glossary first so the concept/workflow pages can link its terms.

- Issue 4.1: **Workflow-vocabulary glossary (`yf-3d13`).** New Concepts glossary page: "pouring
  beads", "landing the plane", "red-team", "molecule/formula/wisp", "gate", "cascade-close",
  "coordinator", "tombstone" (the reversible `bd close -r` hoist-and-close pattern), and the
  recurring workflow-step terms — a cold-reader decoder. Plain GFM; Pelican front-matter matching
  existing pages.
- Issue 4.2: **Beads & `yf-beads-*` concepts (`yf-rd33`).** New Concepts page: what beads is, why we
  use it, why yf skills override/guardrail beads; each beads feature we use (gates, formulas, epics,
  labels); a detailed **upstream strategy** section (local DB, never push beads via git, issue-tracker
  capture of follow-on work — how it differs from default beads); and how each `yf-beads-*` skill
  (`beads`, `yf-beads-extra`, `yf-beads-authoring`, `yf-beads-init`, `yf-beads-hygiene`,
  `yf-beads-upstream`) owns a distinct aspect, cross-linked. Links glossary terms (4.1).
  - depends-on: 4.1
- Issue 4.3: **`yf-plan` / `yf-research` subagent + workflow docs (`yf-7ntv`).** New page(s)
  documenting each subagent (role, inputs/outputs, dispatch) and each phase of both pipelines
  (yf-plan: SCOPE→INVESTIGATE→PLAN→INTAKE→EXECUTE→RECONCILE→COMPLETE; yf-research: retrieve→
  triangulate→synthesize→critique→refine→package). Derived from the shipped `SKILL.md`/`agents/*.md`.
  Links glossary terms (4.1).
  - depends-on: 4.1
- Issue 4.4: **Managed-files reference (`yf-pxet`, reconcile+extend).** New reference page: a hub
  documenting every managed file the skills produce/consume — `AGENTS.md` (per harness),
  `YOSHIKO_FLOW.md`, `CHANGE-VALIDATION.md`, `DRIFT-CHECK.md`, `.markdown-lint-on-edit`, the `.yf/`
  ownership manifest, `.beads/`, the `<plan>/` OKF bundle files — each with what it is and which skill
  owns it. **Reconcile with `harness-tune.md`**: link to it for the tune-specific surfaces
  (`.yf/` manifest, per-harness AGENTS.md managed blocks) rather than restating them.
  - depends-on: 4.2

## Risks & Mitigations

| # | Risk | Mitigation |
|:--|:-----|:-----------|
| R1 | The new **managed-block drift** surface (Issue 2.2) could misreport, and could overlap the existing aggregate `rule_drift` axis. (Config drift, Issue 2.1, is LOW risk — `SettingsDriftCheck` is already harness-generic + format-aware; it is registration + tests, not a new engine.) | Config drift reuses the shipped generic check (`from_env(codex/opencode)`); managed-block drift reuses the `managed_block` marker parser and is reported **distinctly** from `rule_drift` (Issue 2.2 names it separately). Keep both strictly **read-only** — a false positive is a noisy report, not a mutation. Tagged tests for seeded-drift, clean, and no-double-count cases. |
| R2 | `yf-pxet` managed-files reference duplicates `harness-tune.md` (plan-033 Epic 9). | Reconcile-and-extend: the reference is a **hub** that links to `harness-tune.md` for tune-specific surfaces and only adds the rest. (Operator decision.) |
| R3 | Web docs drift from code over time (paths/behaviors). | Keep prose general where possible; where concrete paths are stated, reuse the plan-033 doc↔code agreement-test pattern or link the code-anchored `harness-tune.md`. Docs describe **shipped** behavior only. |
| R4 | Implementation drifts ahead of SPEC (violates SPEC-first). | Epic 1 lands `REQ-YF-TUNE-026/027` first; Epics 2–3 depend on Epic 1; each implementation issue ships a tagged test against a landed REQ (the coverage gate's source of truth). |
| R5 | The budget-check threshold/heuristic is arbitrary and could nag. | A single documented threshold (e.g. ≥90% of `project_doc_max_bytes`); **warn only**, never block or truncate; the warning is actionable (names cap + projected size). Codex's cap is already raised to 65536 by the plan-033 profile, so the warning is a genuine-edge signal, not routine noise. |
| R6 | Coverage-gate marker convention (from plan-033): new `*(testable, plan-034)*` annotated REQs are excluded from the enforced set. | Consistent with the repo convention; each implementation issue still ships tagged tests (verified per-issue), and final validation reconciles coverage. `cargo test` + `clippy -D warnings` remain the hard gate. |

## Success Criteria
- `SPEC.md` carries new `REQ-YF-TUNE-026` (per-harness drift axis) and `REQ-YF-TUNE-027` (codex
  block-size-budget check); `REQ-YF-TUNE-011`'s deferral note records the drift axis delivered; a
  plan-034 amendment-log entry is present. (Epic 1)
- `yf doctor` reports a **read-only** per-harness settings+rule-block drift axis for codex/opencode/pi
  (config drift vs profile; managed-block drift vs the minimized bundle); tagged `REQ-YF-TUNE-026`;
  green. (Epic 2, closes `yf-252c`)
- Codex rule deploy + the drift axis **warn** (never truncate/block) when the `~/.codex/AGENTS.md`
  managed block + content approaches `project_doc_max_bytes`; tagged `REQ-YF-TUNE-027`. (Epic 3,
  closes `yf-297v`)
- The `web/` site publishes four Pelican pages — a workflow-vocabulary glossary, a beads &
  `yf-beads-*` concepts doc, `yf-plan`/`yf-research` subagent+workflow docs, and a managed-files
  reference (reconciled with `harness-tune.md`) — building under Pelican, with link integrity verified
  by the **`yf-markdown-lint` full audit** (no `--rules` subset) over the new pages (no broken
  relative links/anchors). (Epic 4, closes `yf-3d13`, `yf-rd33`, `yf-7ntv`, `yf-pxet`)
- Every new requirement has ≥1 tagged test; `cargo fmt` + `cargo clippy -- -D warnings` +
  `cargo test --workspace` green; `merge.rs` unmodified. (all Rust epics)
- The six resolved follow-on beads are closed at reconcile; the coarse upstream tracking issue for
  plan-034 is filed at intake.

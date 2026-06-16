# SPEC — Optimal Instructions (`yf-optimal-instructions`)

> **Status: DRAFT (primed).** Per-skill SPEC for the project-root instruction-file optimizer
> (currently `optimal-instructions`, renamed to `yf-optimal-instructions` by the plan-010 rename
> step). Operator to review/edit. Composed by the root macro `SPEC.md` §4 under spec key
> **OPTINST**. This is the requirement-numbered layer; it **references** the existing topical
> design docs under `spec/*.md` rather than restating them.

## 1. Purpose & scope

`yf-optimal-instructions` is an active, on-write optimizer for **project-root** instruction files
(`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`, repo-root `.{claude,agents}/rules/*`). On create/modify of
such a file it reads it, **auto-applies** token-efficiency cuts (K1), **proposes** structural
relocation (K2 — AGENTS.md primary, CLAUDE.md a thin `@-include` index, behavioral rules in the
project's rules surface), and reports what changed. It is `user-invocable: false` — fired by its
trigger and backstopped by its always-loaded companion rule. It `depends-on-skill: yf-skill-authoring`.

**In scope:** the split-apply contract (K1 auto, K2 propose-and-confirm), the K2 structural
convention, surface detection across the three rules-subdir forms, idempotency, the runtime
carve-out, and the no-duplication boundary with `yf-skill-authoring`.

**Out of scope:** **skill-dir** instruction files under `.{claude,agents}/skills/<skill>/` (a
skill's `SKILL.md`, `agents/*.md`, its own rules) — those route to `yf-skill-authoring`. Also
application code, end-user docs, and notes. The token-efficiency (K1) **ruleset itself** is owned
by `yf-skill-authoring` and is referenced here, never restated.

## 2. Requirements (`REQ-OPTINST-NNN`)

### 2.1 Split-apply contract (see `spec/apply.md`)

- **REQ-OPTINST-001** *(testable)* K1 (token-efficiency cuts) shall be **auto-applied** — the main
  session writes K1 edits without operator confirmation (REQ-APPLY-001).
- **REQ-OPTINST-002** *(testable)* K2 (structural relocation) shall be **propose-and-confirm** —
  the agent emits a proposal; the main session writes K2 edits only after explicit operator
  confirmation (REQ-APPLY-002).
- **REQ-OPTINST-003** *(testable)* K2 shall **relocate, never delete** — content moves between
  files and never disappears; every relocation appears in the operator-visible change report
  (REQ-APPLY-003).
- **REQ-OPTINST-004** *(testable)* running on an already-optimized file shall be a **no-op** —
  empty K1 edit set, no K2 proposal (idempotency; required because an on-write skill re-processes
  its own output — REQ-APPLY-004).
- **REQ-OPTINST-005** *(testable)* K1 criteria shall be **cited, never restated**: the agent names
  **`yf-skill-authoring` `SKILL.md` "Token efficiency" §** as the source and reproduces no
  Cut/Keep/Extract ruleset (REQ-APPLY-005).
- **REQ-OPTINST-006** literal command blocks, behavioral constraints, and output-format specs
  shall be preserved — never cut by K1 nor relocated in a way that breaks them (REQ-APPLY-006).

### 2.2 Structural convention — K2 (see `spec/structure.md`)

- **REQ-OPTINST-010** `AGENTS.md` shall be the **primary** project instruction file (project
  context, command reference, orientation) — the cross-harness surface (REQ-STRUCT-001).
- **REQ-OPTINST-011** `CLAUDE.md` shall be a **thin `@-include` index** pointing at `AGENTS.md` and
  the rules subdir, plus only Claude-specific essentials with no portable home (REQ-STRUCT-002).
- **REQ-OPTINST-012** behavioral rules shall live in the project's **rules-subdir surface**
  (`AGENTS/*`, `.agents/rules/*`, or `.claude/rules/*`), one concern per file (REQ-STRUCT-003).
- **REQ-OPTINST-013** K2 content placement (REQ-OPTINST-010..012) shall be the **only** structural
  authority the apply agent applies; nothing beyond them (REQ-STRUCT-004).

### 2.3 Integration & surface detection (see `spec/integration.md`)

- **REQ-OPTINST-020** *(testable)* there shall be **no duplication** with `yf-skill-authoring`: K1
  (token efficiency) lives only in `yf-skill-authoring`; K2 (structure) lives only in this skill's
  `spec/`; each references the other (REQ-INT-001).
- **REQ-OPTINST-021** the two skills' `description` fields shall be **mutually exclusive on the
  skill-dir vs project-root axis** — this skill TRIGGERs on project-root instruction files and
  SKIPs skill-dir ones (REQ-INT-002).
- **REQ-OPTINST-022** *(testable)* surface detection shall recognize all three rules-subdir forms
  (`AGENTS/*`, `.agents/rules/*`, `.claude/rules/*`), normalize K2 relocations to the surface the
  project already uses (the changed file's own surface wins; both `.claude` and `.agents` are in
  scope), and **never impose** a surface on a project that has another (REQ-INT-003).
- **REQ-OPTINST-023** the runtime carve-out shall hold: this skill edits `CLAUDE.md` / `AGENTS/*`
  at **runtime via its apply agent**, distinct from the Surface Convention §1 prohibition that
  governs **install-time** writes — explicitly permitted, not a violation (REQ-INT-004).
- **REQ-OPTINST-024** the companion footprint shall stay **minimal** — exactly one thin,
  pointer-only `protocols/` rule and no hook; the `description` trigger is best-effort and the
  companion rule is the always-loaded backstop, not a trigger mechanism (REQ-INT-005).

### 2.4 Routing

- **REQ-OPTINST-030** if the changed path is **inside a skill directory** under
  `.{claude,agents}/skills/<skill>/`, the skill shall **stop and defer** to `yf-skill-authoring`
  (it owns skill-dir instruction files).

## 3. Interfaces

- **CLI / scripts:** `scripts/manifest_update.py` — vendored copy of the skill-authoring manifest
  helper that recomputes the companion-rule sha256 and bumps semver in `protocols/manifest.json`.
  No domain CLI (the optimizer is the apply agent).
- **Apply agent:** `agents/instruction-optimizer.md` — dispatched via the `Agent` tool with
  `TARGET`, `FILE KIND`, `RULES SURFACE`; returns K1 edited content, a K2 proposal, and a change
  report.
- **Companion rule:** `protocols/INSTRUCTIONS.md` (+ `protocols/manifest.json`, sha256 + semver) —
  the always-loaded thin token-efficiency backstop pointing to `yf-skill-authoring`'s ruleset; the
  always-loaded backstop for the best-effort `description` trigger.
- **Config / state:** none (`.local.json` / `.yf/` state not used; the skill is stateless per
  invocation).

## 4. Guardrails (`GR-OPTINST-NNN`)

- **GR-OPTINST-001** *Drift:* K2 (structural relocation) writing without confirmation, or deleting
  content. *Rule:* K1 auto-applies; K2 is **propose-and-confirm** and **relocates, never deletes**.
  *Why:* demoting CLAUDE.md / relocating operator-authored governance is destructive; content the
  agent misreads as narrative may encode a behavioral constraint.
- **GR-OPTINST-002** *Drift:* restating the token-efficiency ruleset or the AGENTS-primacy rule in
  the wrong skill. *Rule:* K1 ruleset is single-sourced from `yf-skill-authoring`; K2 structure is
  single-sourced here; each references the other. *Why:* the skill exists to enforce
  one-source-of-truth — duplicating either body is the anti-pattern it prevents.
- **GR-OPTINST-003** *Drift:* claiming skill-dir instruction files, or imposing a rules surface.
  *Rule:* defer skill-dir files to `yf-skill-authoring`; normalize to the project's existing
  surface, never impose one. *Why:* the two skills are mutually exclusive on the skill-dir vs
  project-root axis; forcing a surface switch fights the project's convention.

## 5. Verification

- Idempotency (REQ-OPTINST-004), the split-apply contract, and structural placement are checked by
  the before/after acceptance example in `spec/apply.md` (running again on the "after" state yields
  no findings). No-duplication (REQ-OPTINST-020) is verified by grep — no Cut/Keep/Extract ruleset
  in this skill, no AGENTS-primacy ruleset in `yf-skill-authoring`. Each *(testable)* REQ is the
  anchor a plan-010 Epic 6 integration test names (e.g. the Epic 4.1 description cross-check for
  REQ-OPTINST-021).

## 6. References

- `skills/yf-optimal-instructions/SKILL.md` (two bodies of knowledge K1/K2, workflow, surface
  detection, runtime carve-out).
- `skills/yf-optimal-instructions/spec/apply.md` (split-apply + idempotency + acceptance example),
  `spec/structure.md` (K2 structural convention), `spec/integration.md` (no-duplication, surface
  detection, runtime carve-out, minimal footprint).
- `skills/yf-optimal-instructions/agents/instruction-optimizer.md`.
- `protocols/INSTRUCTIONS.md` (always-loaded backstop); `yf-skill-authoring` `SKILL.md`
  "Token efficiency" § (single source of truth for K1).
- Root `SPEC.md` §4 (OPTINST) and `GUARDRAILS.md` (GR-008, per-skill guardrails note).

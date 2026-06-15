# SPEC — Drift Check (`yf-drift-check`)

> **Status: DRAFT (primed).** Per-skill SPEC for the drift-check engine (currently `drift-check`,
> renamed to `yf-drift-check` by the plan-010 rename step). Operator to review/edit. Composed by
> the root macro `SPEC.md` §4 under spec key **DRIFT**. This is the requirement-numbered layer; it
> **references** the existing topical design docs under `spec/*.md` rather than restating them.

## 1. Purpose & scope

`yf-drift-check` is a repo-agnostic engine that verifies **content agreement** across a
repository's declared source-of-truth edges (implementation ↔ docs ↔ spec). On edit of a file
matching the repo's `DRIFT-CHECK.md` manifest globs, it dispatches an isolated, report-only
sub-agent that checks each scoped edge under a strict evidence standard and returns one of
PASS / FAIL / INCONCLUSIVE / CONFLICT. It is `user-invocable: false` — an engine fired by its
always-loaded companion rule.

**In scope:** the fixed engine (manifest acquisition, silent no-op, hybrid bootstrap, scoped
dispatch, conflict handling); the four manifest-driven check categories; the evidence standard;
the per-repo `DRIFT-CHECK.md` schema the engine reads.

**Out of scope:** authoring, optimizing, restructuring, or auto-fixing any artifact (report-only —
see §4); drafting spec REQ-IDs (content authoring); the project-root instruction-file axis
(`yf-optimal-instructions`) and skill-dir authoring conventions (`yf-skill-authoring`).
`yf-drift-check` **never lists** project-root `CLAUDE.md` / `AGENTS.md` as nodes, so it is
structurally silent on that axis.

## 2. Requirements (`REQ-DRIFT-NNN`)

### 2.1 Engine: no-op, bootstrap, dispatch, conflict (see `spec/engine.md`)

- **REQ-DRIFT-001** *(testable)* with **no approved manifest**, an on-edit trigger shall be a
  **silent no-op** — no check, no nag, no bootstrap prompt (mirrors `spec/engine.md`
  REQ-ENGINE-001). A manifest counts as approved only if its §0 Status reads `approved: yes`; a
  missing manifest or an unapproved draft both count as no approved manifest.
- **REQ-DRIFT-002** *(testable)* a manifest shall be **inert until approved**; an inferred draft
  shall not drive enforcement (REQ-ENGINE-002).
- **REQ-DRIFT-003** *(testable)* bootstrap shall be offered **only on explicit invocation or first
  install**, never on a subsequent ordinary edit (REQ-ENGINE-003); it shall infer source/authority
  nodes from what exists on disk, never a hardcoded conventional filename.
- **REQ-DRIFT-004** *(testable)* on an approved manifest, the engine shall match the changed
  path(s) against §6 Trigger Scope globs, collect the scoped edge/node IDs (a source-node edit
  fans out to every derived edge it feeds), and dispatch the verifier over **only those edges**
  (REQ-ENGINE-005, REQ-CHECK-005).
- **REQ-DRIFT-005** *(testable)* the dispatched verifier shall be an **isolated, report-only**
  sub-agent (`agents/drift-verifier.md`) that writes nothing; only the main session mutates files
  (REQ-ENGINE-005).
- **REQ-DRIFT-006** the engine shall carry **no repo vocabulary** — no repo-specific node IDs,
  edge IDs, globs, tool names, or paths as load-bearing references in `SKILL.md`, `spec/`, or
  `agents/` (REQ-ENGINE-006); illustrative prose examples are permitted if labelled as examples.

### 2.2 Manifest schema (see `spec/schema.md`)

- **REQ-DRIFT-010** *(testable)* the per-repo `DRIFT-CHECK.md` shall be markdown with exactly the
  seven schema sections, in order: Artifact Nodes, Source-of-Truth Edges, Per-Edge Contracts,
  Referencers, Required-Section Contracts, Trigger Scope, Fixed-Authority Conflict Policy
  (REQ-SCHEMA-001).
- **REQ-DRIFT-011** *(testable)* the manifest shall be **referentially closed** — every edge names
  §1 nodes that exist; every §3/§6 row names a §2 edge that exists (REQ-SCHEMA-002).
- **REQ-DRIFT-012** *(testable)* every §3 `Contract` value shall be one of the fixed six-term
  vocabulary (`path-resolves`, `identifier-matches`, `value-equal`, `field-set-subset`,
  `field-set-equal`, `section-present`); no manifest introduces a new term (REQ-SCHEMA-003).
- **REQ-DRIFT-013** *(testable)* §1 shall declare ≥1 `Authority: fixed` node and §7 shall name it
  (the drift tie-breaker — REQ-SCHEMA-004).

### 2.3 Check categories & evidence (see `spec/checks.md`)

- **REQ-DRIFT-020** *(testable)* each edge's §2 Check Category shall select exactly one of four
  engines — `cross-ref`, `contract`, `behavioral`, `required-section` (+ reachability) — and the
  §3 Contract term shall be the test (REQ-CHECK-001..004).
- **REQ-DRIFT-021** *(testable)* every check item shall be backed by **direct evidence** (a file
  read, identifier comparison, contract listing, content quote, or command output) before it is
  marked PASS or FAIL; "I believe this is correct" is not evidence (REQ-CHECK-006). A check needing
  unavailable runtime execution shall be marked INCONCLUSIVE.
- **REQ-DRIFT-022** *(testable)* the verifier shall return one of four per-item verdicts —
  PASS / FAIL / INCONCLUSIVE / CONFLICT — and shall never fix (REQ-CHECK-007).

### 2.4 Acting on findings (main session)

- **REQ-DRIFT-030** the main session shall resolve **FAIL** in the same pass as the originating
  change (the cascade principle), surface **INCONCLUSIVE** to the operator with the verifier's
  notes (never assume pass/fail), and **halt on CONFLICT** — a suspected-stale `fixed` authority —
  reporting per the manifest's §7 policy without rewriting either side (REQ-ENGINE-004, REQ-CHECK-007).

## 3. Interfaces

- **CLI / scripts:** none (no Python helper; the engine is the SKILL.md + sub-agent).
- **Sub-agent:** `agents/drift-verifier.md` — the isolated, read-only verifier dispatched via the
  `Agent` tool with `MANIFEST`, `SCOPED_EDGES`, `CHANGED_PATHS`.
- **Companion rule:** `protocols/DRIFT-CHECK-TRIGGER.md` — the always-loaded on-edit trigger
  contract (the firing surface for a `user-invocable: false` engine). **No `manifest.json` today**
  (candidate to add under the macro spec's per-rule hash model — `REQ-YF-PRE-003`).
- **Config / state:** the per-repo `DRIFT-CHECK.md` manifest at the repo root (canonical home;
  `.agents/rules/` and `.claude/rules/` are fallback detection paths). No `.local.json` / `.yf/`
  state. `templates/manifest.md` is the bootstrap draft template.

## 4. Guardrails (`GR-DRIFT-NNN`)

- **GR-DRIFT-001** *Drift:* authoring, optimizing, restructuring, or **auto-fixing** an artifact.
  *Rule:* the engine is **report-only** — the verifier is read-only and writes nothing; the main
  session applies FAIL corrections, never the engine. *Why:* isolating verification from repair
  keeps the verification mindset uncontaminated (the original CONSISTENCY rationale). This is the
  key boundary; it is the per-skill counterpart to macro `GR-004`.
- **GR-DRIFT-002** *Drift:* claiming the project-root instruction-file axis. *Rule:* `yf-drift-check`
  **never lists** `CLAUDE.md` / `AGENTS.md` as nodes; project-root structure routes to
  `yf-optimal-instructions` and skill-dir authoring conventions to `yf-skill-authoring`. *Why:*
  content agreement is an orthogonal axis from authoring/optimizing; on a skill-dir file it may
  fire alongside `yf-skill-authoring` by design (the per-repo suppression lever is to omit the glob
  from §6).
- **GR-DRIFT-003** *Drift:* nagging or bootstrapping on every edit. *Rule:* no approved manifest ⇒
  silent no-op; bootstrap only on explicit invoke / first install. *Why:* the engine must not
  impose on repos that have not opted in.

## 5. Verification

- The schema invariants (REQ-DRIFT-010..013) are checkable by reading a `DRIFT-CHECK.md` against
  the seven-section schema and the six-term vocabulary; the no-op and bootstrap gating
  (REQ-DRIFT-001..003) by an on-edit trigger producing no output absent an approved manifest, and
  bootstrap firing only on explicit invoke. The report-only invariant (REQ-DRIFT-005, GR-DRIFT-001)
  is verified by confirming the verifier mutates no file. Each *(testable)* REQ is the anchor a
  plan-010 Epic 6 integration test names.

## 6. References

- `skills/drift-check/SKILL.md` (operational summary; on discrepancy, `spec/` wins).
- `skills/drift-check/spec/schema.md` (seven-section manifest schema + six-term contract vocabulary),
  `spec/checks.md` (four check categories + evidence standard + verdict semantics),
  `spec/engine.md` (no-op, bootstrap, dispatch, conflict, out-of-scope limits).
- `skills/drift-check/agents/drift-verifier.md`; `templates/manifest.md`.
- `protocols/DRIFT-CHECK-TRIGGER.md` (on-edit trigger).
- Root `SPEC.md` §4 (DRIFT) and `GUARDRAILS.md` (GR-004, per-skill guardrails note).

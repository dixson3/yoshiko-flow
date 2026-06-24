# SPEC — Change Validation (`yf-change-validation`)

> **Status: DRAFT (primed).** Per-skill SPEC for the change-validation engine. Operator to
> review/edit. Composed by the root macro `SPEC.md` §4 under spec key **CHGVAL**. This is the
> requirement-numbered layer; it **references** the topical design docs under `spec/*.md` rather
> than restating them.

## 1. Purpose & scope

`yf-change-validation` is a fixed, repo-agnostic engine that runs a repo's **recorded validation
recipe** over a change-set / merged tree and reports PASS / FAIL + the failing command. It is
driven by a per-repo `CHANGE-VALIDATION.md` manifest that is **inferred from the toolchain**,
**operator-approved**, then **re-proposed when the toolchain drifts** from the recorded recipe
(self-maintaining). Unlike `yf-drift-check` (prose + a read-only LLM sub-agent), this engine has a
**Python engine** because it must *execute* build/test/lint, parse exit codes, and fingerprint the
toolchain. yf-plan's §6.1.5 merged-state validation (layer b) **delegates** to it via a prose
soft-dep, with the static `validate-cmd` kept as a thin fallback.

**In scope:** the manifest schema (`spec/schema.md`); the engine lifecycle — silent no-op,
infer→approve→enforce bootstrap, run-and-report, fail-closed, re-propose-on-drift, the `§0
approved: no` rollback lever (`spec/engine.md`); the toolchain inference precedence and tier
construction (`spec/inference.md`); the Python interfaces (`infer` / `run` / `check-drift`).

**Out of scope:** auto-fixing a failing command or auto-rewriting the manifest (report/propose
only); driving `yf-drift-check` — the recipe is **executable-only**, and `yf-drift-check` is a
prose/LLM trigger, not a runnable command, so it is deliberately **excluded** from any tier (the
two skills are orthogonal triggers that fire independently). Adding a `yf` Rust subcommand is out
of scope — the engine routes **as a skill** (crate GR-005 kernel/skill boundary).

## 2. Requirements (`REQ-CHGVAL-NNN`)

### 2.1 Engine: no-op, lifecycle, run-and-report, fail-closed (see `spec/engine.md`)

- **REQ-CHGVAL-001** *(testable)* with **no approved manifest**, the engine shall be a **silent
  no-op** on an on-edit trigger, and a `run` invocation shall return a **clean refusal** (a
  structured `§0 approved: no` result, never a stack trace) — REQ-ENGINE-001. A manifest counts as
  approved only if its §0 Status reads `approved: yes`; a missing manifest or an unapproved draft
  both count as no approved manifest.
- **REQ-CHGVAL-002** *(testable)* a manifest shall be **inert until approved** — an inferred draft
  shall not drive enforcement (REQ-ENGINE-002).
- **REQ-CHGVAL-003** *(testable)* the engine shall follow an **infer→approve→enforce** lifecycle:
  inference (and drift re-proposal) happen at **bootstrap** / `check-drift` only, both
  operator-gated; at run time the engine executes **exactly** the commands the approved manifest
  records and **never invents** a command (REQ-ENGINE-003).
- **REQ-CHGVAL-004** *(testable)* on `run`, the engine shall execute the selected tier's commands
  and **report PASS / FAIL** with the **first failing command** and a tail of its output; it shall
  **never auto-fix** a failure (REQ-ENGINE-004).
- **REQ-CHGVAL-005** *(testable)* the engine shall be **fail-closed** (contrast `validate-cmd`'s
  fail-open): a missing required tool shall yield **INCONCLUSIVE**, never a false PASS
  (REQ-ENGINE-005).
- **REQ-CHGVAL-006** *(testable)* on toolchain drift, the engine shall **re-propose** an updated
  tier (operator-confirmed) and shall **never auto-rewrite** the manifest (REQ-ENGINE-006).
- **REQ-CHGVAL-007** *(testable)* setting **`§0 approved: no`** shall be the **rollback lever** that
  drops yf-plan's layer-(b) delegation straight back to `validate-cmd` (then the not-checked
  notice) in a single edit, with no engine command run (REQ-ENGINE-007).
- **REQ-CHGVAL-008** the engine shall route **as a skill** — it shall add **no `yf` Rust
  subcommand**; it is a `skills/`-embedded Python engine plus an always-loaded protocol rule
  (REQ-ENGINE-008).
- **REQ-CHGVAL-009** the engine shall carry **no repo vocabulary** — no repo-specific command
  strings, tool names, globs, or paths as load-bearing references in `SKILL.md`, `spec/`, or
  `scripts/`; all of that lives in the per-repo `CHANGE-VALIDATION.md` (illustrative prose examples
  permitted if labelled as examples).

### 2.2 Manifest schema (see `spec/schema.md`)

- **REQ-CHGVAL-010** *(testable)* the per-repo `CHANGE-VALIDATION.md` shall be markdown with exactly
  the four schema sections, in order: §0 Status, §1 Tiers, §2 Signal Fingerprint, §3 Trigger Scope
  (REQ-SCHEMA-001).
- **REQ-CHGVAL-011** *(testable)* §1 shall define a `fast` and a `full` **ordered command list**;
  each command shall be a **structured row** with columns `id` (optional, referenced by §3), `cmd`
  (shell string), `cwd` (optional), `timeout` (optional, seconds) — REQ-SCHEMA-002.
- **REQ-CHGVAL-012** *(testable)* every §1 row shall be a **runnable shell command** (the recipe is
  executable-only); `yf-drift-check` shall **never** appear as a row — it is a prose/LLM trigger,
  not a command (REQ-SCHEMA-003).
- **REQ-CHGVAL-013** *(testable)* the **FULL** tier shall be a **superset of CI ∪ repo-checks** —
  it shall not omit a suite CI omits (REQ-SCHEMA-004).
- **REQ-CHGVAL-014** *(testable)* §2 shall record a per-signal `{source-path, parsed-value-or-hash}`
  **fingerprint** of the toolchain signals the recipe was inferred from; reading it shall be **pure
  file-read + parse** (REQ-SCHEMA-005).
- **REQ-CHGVAL-015** *(testable)* §3 shall map each **changed-path glob → the subset of FAST command
  `id`s** it selects; `run --tier fast --changed <paths>` shall run only the **union** of selected
  ids, and the **whole** FAST tier when no `--changed` is given (REQ-SCHEMA-006).
- **REQ-CHGVAL-016** *(testable)* the manifest shall be **referentially closed** — every §3 `id`
  shall name a §1 FAST row that exists (REQ-SCHEMA-007).

### 2.3 Inference (see `spec/inference.md`)

- **REQ-CHGVAL-020** *(testable)* inference precedence shall be **CI `run:` steps > runner targets
  (just/make) > manifest defaults**: CI wins on **flags**, glob-scan wins on **what exists**
  (REQ-INFER-001).
- **REQ-CHGVAL-021** *(testable)* a `test_*.py` carrying a **PEP-723 header** shall be inferred to
  run **per-file** (`uv run --script` / `uv run <f>`); without a header it shall run via the
  **project pytest** idiom — the engine reads each header, it cannot assume one pytest command
  (REQ-INFER-002).
- **REQ-CHGVAL-022** *(testable)* inference shall **skip** CI jobs that are `if: ${{ false }}` or
  tag-only (REQ-INFER-003).
- **REQ-CHGVAL-023** *(testable)* when an existing `validate-cmd` is present in
  `.yf-plan.local.json`, inference shall **seed the FULL tier from it** (the #27 migration clause)
  — REQ-INFER-004.
- **REQ-CHGVAL-024** *(testable)* the inferred FULL tier shall satisfy **FULL ⊇ CI ∪ repo-checks**
  (REQ-INFER-005), the same superset invariant as REQ-CHGVAL-013, enforced at inference time.

## 3. Interfaces

- **CLI / scripts:** `scripts/change_validation.py` (PEP-723 `uv run --script`) with three
  subcommands:
  - `infer` — read toolchain signals, emit a **draft** `CHANGE-VALIDATION.md` (two tiers +
    fingerprint), seeding FULL from `validate-cmd` when present.
  - `run --tier fast|full [--changed <paths>] [--json]` — parse the **approved** manifest, execute a
    tier (affected-scoped when `--changed`), return `{tier, status: pass|fail|inconclusive,
    commands:[{id, cmd, ok, returncode, output_tail}], first_failure}`; exit non-zero on FAIL;
    clean `§0 approved: no` refusal when unapproved/absent.
  - `check-drift [--json]` — re-read signals, diff against §2, emit a JSON **re-proposal**
    (added/removed/changed signals + the proposed tier delta); **never** rewrites the manifest.
- **Companion rule:** `protocols/CHANGE-VALIDATION-TRIGGER.md` (+ `protocols/manifest.json` hash) —
  the always-loaded on-edit (FAST) + pre-push/land-the-plane (FULL) trigger; silent no-op unless an
  approved manifest exists.
- **Config / state:** the per-repo `CHANGE-VALIDATION.md` manifest at the repo root (canonical
  home). Reads `.yf-plan.local.json` `validate-cmd` at inference time only (the migration seed).
  `templates/manifest.md` is the bootstrap draft template.

## 4. Guardrails (`GR-CHGVAL-NNN`)

- **GR-CHGVAL-001** *Drift:* auto-fixing a failing command or auto-rewriting the manifest. *Rule:*
  the engine **runs and reports** (PASS/FAIL + failing command) and **proposes** drift deltas; it
  never edits source or the manifest. *Why:* the repo's propose-not-fix posture (mirrors
  yf-drift-check / yf-optimal-instructions) keeps the operator in the loop on a code-exec surface.
- **GR-CHGVAL-002** *Drift:* failing **open** like a static `validate-cmd`. *Rule:* a missing
  required tool is **INCONCLUSIVE**, never PASS; an unapproved/absent manifest yields a clean
  refusal so yf-plan emits the not-checked notice, not a false green. *Why:* fail-open is the exact
  failure mode #27 indicts.
- **GR-CHGVAL-003** *Drift:* putting `yf-drift-check` (or any non-command) in a tier, or adding a
  `yf` Rust subcommand. *Rule:* tiers are **executable-only**; the engine routes **as a skill**.
  *Why:* `yf-drift-check` is a prose/LLM trigger that fires on its own orthogonal trigger — the two
  stay independent, non-recursive triggers (content agreement vs change-set validity); the
  kernel/skill boundary (crate GR-005) stays intact.

## 5. Verification

- Schema invariants (REQ-CHGVAL-010..016) are checkable by parsing a `CHANGE-VALIDATION.md` against
  the four-section schema, the structured-row columns, the executable-only rule, and §3↔§1 closure.
  The no-op / clean-refusal gating (REQ-CHGVAL-001..002, REQ-CHGVAL-007) is verified by a `run`
  against an unapproved/absent manifest returning the structured refusal (no stack trace). The
  fail-closed posture (REQ-CHGVAL-005) is verified by a `run` with a required tool absent returning
  INCONCLUSIVE. Inference invariants (REQ-CHGVAL-020..024) are checked by `infer` against toolchain
  fixtures (Cargo / CI / PEP-723 / just / a seeded `validate-cmd`). Each *(testable)* REQ is the
  anchor a B.4 / D.3 test names.

## 6. References

- `skills/yf-change-validation/SKILL.md` (operational summary; on discrepancy, `spec/` wins).
- `skills/yf-change-validation/spec/schema.md` (four-section manifest schema + structured tier
  rows), `spec/engine.md` (no-op, lifecycle, run-and-report, fail-closed, re-propose, rollback
  lever), `spec/inference.md` (precedence, PEP-723 per-file idiom, FULL-superset, validate-cmd
  seed).
- `skills/yf-change-validation/scripts/change_validation.py` (`infer` / `run` / `check-drift`);
  `templates/manifest.md`.
- `protocols/CHANGE-VALIDATION-TRIGGER.md` (on-edit / pre-push trigger).
- Root `SPEC.md` §4 (CHGVAL) and `GUARDRAILS.md`. Sibling: `skills/yf-drift-check/SPEC.md` (the
  mirrored conventions; orthogonal axis).

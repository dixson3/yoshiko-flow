# Plan: yf-change-validation skill (#27) + worktree-uv doc guidance (#25)

**ID:** plan-015-james-dixson-cb2ef4
**Author:** james-dixson
**Created:** 2026-06-24
**Status:** approved
**Epic:** beads-skills-mol-itd
**Phase log:**
- 2026-06-24 scoping: initial scope captured (full skill; investigate-then-decide on sharing; bundle #25 as docs)
- 2026-06-24 investigating: 3 experiments: drift-check shape, yf-plan delegation surface, toolchain inference
- 2026-06-24 drafting: synthesizing plan: STANDALONE-MIRROR, skill+Python engine, 3-tier delegation
- 2026-06-24 review: plan v1 presented
- 2026-06-24 approved: operator approved (red-team REVISE resolved in v2)
- 2026-06-24 intake: epic beads-skills-mol-itd poured

## Objective

Build a **`yf-change-validation`** skill: a fixed, repo-agnostic engine that runs a repo's
recorded validation recipe over a change-set / merged tree and reports PASS/FAIL + the failing
command, driven by a **per-repo manifest** that is **seeded by inferring from the toolchain**,
operator-approved, then **re-proposed when the toolchain drifts** from the manifest
(self-maintaining). yf-plan's §6.1.5 merged-state validation (layer b) **delegates** to it, with
the static `validate-cmd` kept as a thin fallback. Bundles **#25** (the `env -u VIRTUAL_ENV uv
run …` worktree doc guidance) as a small docs sub-task.

## Motivation

plan-011 added a static `validate-cmd` string to `.yf-plan.local.json` so yf-plan's §6.1.5
merged-state validation can run a repo-wide build/test/lint over the *merged* tree (layer b),
not just the landing plan's own gate (layer a). plan-014 just shipped — and its land-the-plane
**surfaced this exact gap**: this repo has **no `validate-cmd` configured**, so the merged-state
validation emitted a "CROSS-PLAN REGRESSIONS NOT CHECKED" notice and proceeded on plan-gate
coverage only (a false green). A static `validate-cmd` has the **same drift failure mode that
motivated `yf-drift-check`**: it is hand-authored per-repo config that silently rots when the
toolchain changes (new crate, cargo→just, added docs build, moved test dir), and it **fails
open** — a rotted/absent command validates the wrong thing or is silently skipped. "Is this
change-set valid?" is also useful beyond yf-plan (any worktree merge-back, any pre-land-the-plane
upstream push, any agent about to push). Source: #27 (driver, spun out of plan-011 bead
`beads-skills-tr0`), #25 (sub-requirement).

## Glossary (adjacent concepts)

- **Change-set validity vs content agreement** — `yf-change-validation` proves a change-set **is
  valid** by *executing* build/test/lint (behavioral). `yf-drift-check` proves artifacts **agree**
  across declared edges (content). Orthogonal axes; #27 observes they share the
  engine + manifest + triggered-pass + hybrid-bootstrap *shape*.
- **layer (a) / layer (b)** — yf-plan §6.1.5 merged-state validation. Layer (a) = the landing
  plan's own Gate `Test:` commands. Layer (b) = the repo-wide `validate-cmd` (cross-plan safety
  net). This plan makes layer (b) delegate to `yf-change-validation`.
- **Self-maintaining manifest** — the manifest is *inferred* from the toolchain (Cargo.toml →
  cargo test/clippy/fmt; package.json → npm test; pyproject → pytest/ruff; just/Make targets),
  operator-approved, and **re-proposed** when the toolchain drifts from the recorded recipe. This
  is the property a static `validate-cmd` lacks.
- **`_shared/` foundation (plan-014)** — the canonical-helper + repo-time sync-tool + DRIFT-CHECK
  edge pattern just landed. Whether `yf-change-validation` should *consume* a shared
  manifest-bootstrap helper via that pattern is the open **sharing** question (investigated, not
  pre-decided).

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #27 | yf-change-validation: per-repo change-set validation skill (supersede static validate-cmd) | include | The driver. Full skill: engine + manifest + inference/bootstrap + self-maintaining re-propose + yf-plan layer-(b) delegation + trigger rule | Epics A–D (build) + E.1 (dogfood); reconciled E.4 |
| #25 | Doc guidance: `env -u VIRTUAL_ENV uv run …` when running uv inside a git worktree | include | Bundled as a small docs sub-task (add to yf-plan worktree address-space docs) | E.2; reconciled E.4 |

## Scoping decisions (operator)

1. **Scope = full skill.** Engine + per-repo manifest + toolchain inference/bootstrap +
   self-maintaining toolchain-drift re-proposal + yf-plan layer-(b) delegation + always-loaded
   trigger rule. Mirrors `yf-drift-check`'s completeness.
2. **Sharing = investigate then decide.** Run an investigation experiment comparing the real
   machinery `yf-change-validation` needs vs what `yf-drift-check` actually has (prose, no
   Python), then decide standalone-mirror vs extract-to-`_shared/`. Not pre-committed.
3. **#25 = bundle as a docs sub-task.** Add the `env -u VIRTUAL_ENV uv run …` worktree guidance
   to yf-plan's worktree address-space docs; reconcile both #27 and #25 at land-the-plane.

## Investigation plan

Pre-investigation checkpoint (experiments dispatched before drafting):

- **Exp 001 — yf-drift-check machinery shape (drives the sharing decision).** What are
  yf-drift-check's manifest schema, bootstrap/inference, always-loaded trigger rule, and
  report-only dispatch, concretely? Is there reusable *code* (there is no Python today) or only
  reusable *conventions*? Recommend standalone-mirror vs extract-to-`_shared/`.
- **Exp 002 — yf-plan §6.1.5 delegation surface.** Exactly how does `plan_manager.py
  validate-merged` read `validate-cmd` from `.yf-plan.local.json` today (layer b), and what is the
  cleanest delegation contract so `yf-change-validation` supersedes it while `validate-cmd`
  remains a thin fallback? Identify the precise call site and JSON keys.
- **Exp 003 — toolchain inference signals.** What toolchain signals should the inference engine
  read (Cargo.toml, package.json, pyproject.toml, justfile/Makefile, this repo's own CI
  `.github/workflows/ci.yml`), and how do they map to a *layered* fast/affected vs full
  validation recipe? Use this repo as the worked example (cargo fmt/clippy/test + the uv pytest
  suites + `_shared/sync.py --check`).

## Investigation Findings

Three experiments (full reports in `findings/`):

- **`exp-001-driftcheck-shape.md` → STANDALONE-MIRROR.** yf-drift-check is **entirely prose + one
  read-only LLM sub-agent** — no `scripts/`, no Python. `_shared/` (plan-014) is a domain-specific
  text-region vendoring tool, not engine machinery. There is **no reusable code**, only reusable
  **conventions** (7-section markdown manifest, `§0 approved` gate + silent no-op, REQ-* `spec/`
  layout, infer→approve→enforce bootstrap, "infer from disk, never hardcode" E4 lesson). Build
  standalone; mirror the conventions. The two skills diverge exactly where code would matter — the
  verifier is *read-only*, a validation runner **executes** build/test/lint; so change-validation
  needs a Python engine drift-check never did.
- **`exp-002-yfplan-delegation.md` → pre-sanctioned seam.** `plan_manager.py:879-884` already
  records this exact extraction (the foreseen **"acceptance" skill**) and mandates a **prose
  soft-dep** (present → delegate; absent → fallback; **never** a frontmatter `depends-on-skill`
  edge). Seam = one new precedence tier in `_validate_merged` (~line 1327): (1) approved
  `CHANGE-VALIDATION.md` present → delegate; (2) else `validate-cmd` → run it; (3) else → the
  verbatim not-checked notice. Preserve the `{plan_dir, validate_cmd_configured, layer_b, notice,
  status}` schema + the exit-3 contract; add an `engine` discriminator. **Route as a skill, not a
  `yf` subcommand** (crate GR-005 kernel/skill boundary). Flag: SKILL §6.1.5 prose ("runs layer (a)
  only" when unset) is out of step with the code (runs *no* suite when unset) — correct as a docs
  sub-task.
- **`exp-003-toolchain-inference.md` → CI-seeded, superset recipe, parse-only drift.** CI workflow
  `run:` steps are the highest-fidelity seed (adopt verbatim; skip `if: ${{ false }}` / tag-only
  jobs). The **FULL tier must be a superset of CI** — this repo's `ci.yml` runs only cargo and omits
  the 6 `uv` pytest suites + `_shared/sync.py --check`, a *standing* example proving
  "seed-then-augment + re-propose" is necessary. Drift detection is **pure file-read + parse** (a
  per-signal `{source, hash}` fingerprint), cheap enough for an on-edit trigger. PEP-723-without-
  pyproject forces per-file invocation inference (two idioms in this repo).

## Approach

Build **`yf-change-validation`** as a standalone skill (mirroring `yf-drift-check`'s conventions,
sharing no code — decision from exp-001), with a **Python engine** (it must *run* commands, unlike
drift-check) driven by a per-repo, **operator-approved**, self-maintaining **`CHANGE-VALIDATION.md`**
manifest. yf-plan's §6.1.5 layer (b) delegates to it via a **prose soft-dep** at the pre-sanctioned
seam (exp-002); the static `validate-cmd` becomes the middle fallback tier. **Zero `yf` Rust
changes** (skill + `skills/` embed + data-driven protocol-rule aggregation). Foundation-first, six
epics; #25 rides along as a docs sub-task.

The manifest (`CHANGE-VALIDATION.md`, repo root, mirroring `DRIFT-CHECK.md`) is markdown the engine
parses mechanically: **§0 Status** (`approved: yes|no` gate), **§1 Tiers** (`fast` / `full` ordered
command lists, each command a structured row — see A.1), **§2 Signal Fingerprint** (`source-path |
parsed-value-or-hash` rows), **§3 Trigger Scope** (changed-path globs → the FAST subset they select).
The engine never invents commands at run time — it executes exactly what the approved manifest
records; inference only happens at **bootstrap** and **drift re-proposal**, both operator-gated.

**Executable-only recipe (red-team C5).** The tiers contain **only runnable shell commands** (exit
code = verdict). `yf-change-validation` validates *behavioral* validity by executing build/test/lint;
it does **not** drive `yf-drift-check`. Drift-check is **prose + an LLM sub-agent with no script**
(exp-001), so "yf-drift-check full" is *not* a shell command and is deliberately **excluded** from
the recipe. The two skills stay orthogonal triggers that fire independently on an edit (content
agreement vs change-set validity); neither invokes the other. This also avoids the double-fire a
shared `.md` edit would otherwise cause.

**Staging (red-team C1/C2).** Epics **A–D are the MVP**: the manifest schema, the
infer + **run** engine, skill packaging, and the yf-plan delegation — the smallest thing that closes
the plan-014 false-green gap. The **self-maintaining apparatus** (`check-drift` re-proposal, §2
fingerprint, the on-edit drift trigger) is **staged last** (B.3 + the C.2 drift trigger), independently
reviewable, and deferrable to a follow-on if review finds the drift case thin — its only standing
evidence today is a one-time *bootstrap* augmentation (CI omits the pytest suites), handled once at
E.1. Epic **E is dogfood + #25 docs + reconcile**.

**Runtime budget (red-team M2).** The **FULL** tier (cargo fmt+clippy+test ∪ 6 pytest suites ∪
`sync.py --check`) is the **pre-push / land-the-plane** gate (yf-plan §6.1.5) — a multi-minute cost
paid once per land, which the operator accepts as the price of real cross-plan safety. The **FAST**
(affected) tier is the on-edit trigger. FULL is **not** run on every coordinator step.

**Naming (red-team M3).** The `plan_manager.py:879-884` seam comment calls this the foreseen
`acceptance` skill; it **is** `yf-change-validation`. D.1/D.2 update that comment so a future reader
does not hunt for a separate `acceptance` skill.

## Epics

### Epic A: Spec + manifest schema (conventions, no code)

- Issue A.1: `skills/yf-change-validation/spec/` REQ-* files mirroring drift-check's layout —
  `schema.md` (the 4-section `CHANGE-VALIDATION.md` manifest: §0 approved gate, §1 fast/full tiers,
  §2 signal fingerprint, §3 trigger scope; machine-parsable markdown tables). **Per-command shape
  (red-team C3):** each §1 tier row is a structured command — `cmd` (shell string, run via shell so
  the PEP-723 two-idiom and `cd website && …` cases work), optional `cwd`, optional `timeout`
  (seconds; a hung test must not wedge land-the-plane), and an optional `id` referenced by §3.
  **Affected-scoping (C3):** §3 maps a changed-path glob → the **subset of FAST command ids** it
  selects; `run --tier fast --changed <paths>` runs only the union of selected ids (the whole FAST
  tier when no `--changed` is given). The recipe is **executable-only** — every row is a runnable
  shell command (drift-check is excluded per C5; it is not a command). `engine.md` (silent no-op
  unless an approved manifest exists; infer→approve→enforce; **run-and-report PASS/FAIL + failing
  command**, never auto-fix; re-propose on drift, operator-confirmed; route-as-skill / zero-Rust;
  fail-**closed** vs `validate-cmd`'s fail-open; the `§0 approved: no` **rollback lever** that drops
  delegation back to `validate-cmd`/notice — red-team M1). `inference.md` (precedence **CI `run:` >
  runner targets (just/make) > manifest defaults**; CI wins on flags, glob-scan wins on what-exists;
  PEP-723 per-file idiom; FULL ⊇ CI ∪ repo-checks; **seed from an existing `validate-cmd`** when one
  is present — the #27 migration clause, red-team M4). Plus top-level `SPEC.md`.
- Issue A.2: `templates/manifest.md` — the `CHANGE-VALIDATION.md` template (inert `approved: no`),
  with the 4 sections and worked-example comments.

### Epic B: Inference + runner + drift engine (Python)

- Issue B.1: `scripts/change_validation.py` — toolchain **signal readers** (Cargo.toml +
  `[workspace]`; `.github/workflows/*.yml` `run:` steps, skipping `if:false`/tag-only; `**/test_*.py`
  glob + per-file PEP-723 header → invocation idiom; `package.json` scripts; `justfile`/`Makefile`
  targets; repo `--check` scripts; markers) and an `infer` subcommand that emits a **draft
  `CHANGE-VALIDATION.md`** (two tiers + fingerprint). When an existing `validate-cmd` is present in
  `.yf-plan.local.json`, **seed the FULL tier from it** (the #27 migration clause, M4). PEP-723
  `uv run --script`.
  - depends-on: A.1
- Issue B.2: `run` subcommand — parse the **approved** manifest, execute a tier
  (`--tier fast|full`, optional `--changed <paths>` for affected-scoping), return JSON
  `{tier, status: pass|fail, commands:[{cmd, ok, returncode, output_tail}], first_failure}`;
  exit non-zero on fail; mark **INCONCLUSIVE** (via an inlined ~10-line `tool_on_path`) when a
  required tool is absent (never a false green).
  - depends-on: B.1
- Issue B.3 **(staged — the self-maintaining tier, red-team C2)**: `check-drift` subcommand —
  re-read signals, diff against the recorded §2 fingerprint, emit a JSON **re-proposal**
  (added/removed/changed signals + the proposed tier delta); **never auto-rewrites** the manifest.
  Sequenced after the MVP (A–D, dogfood E.1) proves out; independently reviewable and deferrable to
  a follow-on if review finds the drift case thin.
  - depends-on: B.1
- Issue B.4: `test_change_validation.py` (PEP-723 pytest) — signal readers (fixtures for
  Cargo/CI/PEP-723/just), `infer` draft shape, `run` pass/fail/INCONCLUSIVE + affected-scoping,
  `check-drift` fingerprint diff (incl. the standing CI-omits-pytest delta), approved-gate refusal.
  - depends-on: B.2
  - depends-on: B.3

### Epic C: SKILL.md + trigger rule + skill packaging

- Issue C.1: `SKILL.md` + `README.md` + frontmatter — invocation (`/yf-change-validation`,
  `init`/bootstrap, `run`, `check-drift`), the infer→approve→enforce bootstrap flow, the
  approved-gate + silent-no-op, dispatch, file-layout fence. Lint clean (markdown subset).
  - depends-on: A.1
- Issue C.2: `protocols/CHANGE-VALIDATION-TRIGGER.md` (+ `protocols/manifest.json` hash) — the
  always-loaded trigger: on edit of a path matching an **approved** manifest's §3 glob, run the
  **FAST** (affected) tier; the **pre-push / land-the-plane** FULL-tier trigger; **silent no-op**
  unless an approved `CHANGE-VALIDATION.md` exists. The rule states the **carve vs `yf-drift-check`**
  (orthogonal triggers — change-set validity by *executing* commands vs content agreement; neither
  invokes the other, so a shared `.md` edit firing both is expected and non-recursive). The
  `check-drift` re-proposal hook is part of the **staged** self-maintaining tier (C2) — added with
  B.3, not the MVP. Verify the data-driven `yf` flow aggregation picks the rule up (zero Rust
  change); `yf preflight`/install parity green.
  - depends-on: C.1
- Issue C.3: register the skill in the repo surfaces — project `README.md` skills index +
  prerequisites, and confirm `yf` embed/upgrade includes the new `skills/yf-change-validation/`
  tree. (No `install.sh`; the `yf` binary embeds `skills/` verbatim.)
  - depends-on: C.1

### Epic D: yf-plan delegation + migration

- Issue D.1: wire the **3-tier delegation** into `plan_manager.py` `_validate_merged` at the
  pre-sanctioned seam — approved `CHANGE-VALIDATION.md` present → delegate to `change_validation.py
  run --tier full` over the merged tree; else `validate-cmd`; else the verbatim notice. Preserve the
  output schema + exit-3; add the `engine: change-validation|validate-cmd|none` discriminator. Prose
  soft-dep only — **no** frontmatter `depends-on-skill` edge.
  - depends-on: B.2
- Issue D.2: update yf-plan `SKILL.md` §6.1.5 + `spec/` — document the delegation precedence and
  **correct the layer-(a) prose discrepancy** (exp-002 flag). Keep `validate-cmd` documented as the
  thin fallback.
  - depends-on: D.1
- Issue D.3: delegation tests — extend `test_worktree.py` (or a new test) to cover the three tiers
  (manifest-present delegate, validate-cmd fallback, neither → notice) and the stable output
  schema/exit code.
  - depends-on: D.1

### Epic E: dogfood manifest + #25 docs + reconcile

- Issue E.1: author **and approve** this repo's `CHANGE-VALIDATION.md` (the exp-003 worked two-tier
  recipe, **executable commands only** — C5): FAST = affected `cargo test --workspace` /
  per-changed-suite pytest / `uv run _shared/sync.py --check`; FULL = `cargo fmt --all -- --check` ∪
  `cargo clippy --workspace --all-targets -- -D warnings` ∪ `cargo test --workspace` ∪ all 6 pytest
  suites (per-header idiom) ∪ `uv run _shared/sync.py --check`. **`yf-drift-check` is excluded** (it
  is a prose/LLM trigger, not a runnable command — it fires on its own orthogonal trigger). This
  **closes the plan-014 gap** — future plans' §6.1.5 layer (b) now actually runs. Dogfood:
  `change_validation.py run --tier full` green on the merged tree.
  - depends-on: D.1
  - depends-on: C.2
- Issue E.2 (#25): add the `env -u VIRTUAL_ENV uv run …` worktree guidance to yf-plan's worktree
  address-space docs (SKILL §5.4 / coordinator), warning against uv's `--active` suggestion inside a
  worktree. Resolves #25. **Independent of the engine** (a pure docs edit) — gated only on the start
  gate, no intra-plan predecessor (red-team C1: the prior D.2 dependency was artificial).
- Issue E.3: `DRIFT-CHECK.md` coverage + `CHANGELOG.md` — confirm the new skill's `SKILL.md` /
  `scripts/*.py` / `agents` / `protocol-rule` fall under existing `skills/*/…` node globs (add any
  missing edge); add `CHANGE-VALIDATION.md` as a covered top-level doc if needed; CHANGELOG entry.
  - depends-on: E.1
  - depends-on: E.2
- Issue E.4 (reconcile step): update upstream — close/annotate **#27** (full skill delivered:
  engine + manifest + inference/bootstrap + self-maintaining re-propose + yf-plan delegation +
  trigger rule) and **#25** (worktree-uv guidance documented); note the dogfood manifest landed.
  - depends-on: E.3

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: dogfood manifest validates green
- Type: human
- Condition: **after** E.1 authors the manifest and the operator approves it (`§0 approved: yes`),
  the FULL tier passes against the merged tree. (Sequence, not circular — the gate verifies the
  *approved* manifest works; an unapproved/absent manifest makes the Test return a clean refusal,
  not a failure — red-team C4.)
- Test: `uv run skills/yf-change-validation/scripts/change_validation.py run --tier full --json`
  (pre-approval this returns the `§0 approved: no` refusal cleanly — asserted in B.2/B.4 — never a
  stack trace).
- Blocks: E.1 close (and therefore E.3/E.4)
- Instructions: author the manifest from `change_validation.py infer`, operator-approve (`§0
  approved: yes`), then run the FULL tier; fix any real failure it surfaces before closing E.1.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: E.4

## Risks & Mitigations

- **Scope is large (full skill, 6 epics).** *Mitigation:* foundation-first ordering (spec →
  engine → packaging → delegation → dogfood/reconcile); each epic is independently reviewable and
  the engine is testable in isolation (B.4) before yf-plan wiring (D).
- **Delegation regresses yf-plan's `validate-merged`.** *Mitigation:* the seam preserves the exact
  output schema + exit-3 contract (exp-002); D.3 tests all three tiers; the prose soft-dep means
  absent-manifest behavior is byte-identical to today (validate-cmd → notice).
- **`run` executing arbitrary recorded commands is a code-exec surface.** *Mitigation:* the
  manifest is **operator-approved** (`§0 approved: yes`) before any command runs — same trust model
  as `validate-cmd` (already operator-authored) and drift-check's approved manifest; the engine runs
  *only* what the approved manifest records, never inferred-but-unapproved commands.
- **Inference fails open (the very failure #27 indicts).** *Mitigation:* fail-**closed** posture —
  a missing tool is **INCONCLUSIVE** (never pass); an unapproved/absent manifest makes yf-plan emit
  the existing not-checked notice (no false green); drift re-proposes rather than silently running a
  stale recipe.
- **Self-maintaining re-proposal could nag or auto-edit.** *Mitigation:* `check-drift` is
  report-only and **never rewrites** the manifest; re-proposal is operator-confirmed, matching the
  repo's propose-not-fix posture (yf-drift-check / yf-optimal-instructions).
- **`yf` flow/rule aggregation might need a Rust change for the new protocol.** *Mitigation:*
  C.2 explicitly verifies the data-driven `skills/*/protocols/*` aggregation picks up the new rule
  with parity green; if (unexpectedly) a Rust change is required, that is surfaced as a discovered
  bead, not silently absorbed.
- **A buggy engine could wedge every land-the-plane once delegation + an approved manifest exist.**
  *Mitigation:* the **rollback lever** is explicit and one edit — set `§0 approved: no` in
  `CHANGE-VALIDATION.md` and the yf-plan seam falls straight back to `validate-cmd` (then to the
  not-checked notice). Documented in `engine.md` (A.1) and the trigger rule (C.2). The FULL tier is
  pre-push only (M2), so a slow/flaky engine never blocks per-step coordinator work.

## Success Criteria

- `yf-change-validation` exists as a standalone skill: `spec/` REQ-* + `SPEC.md`, a Python engine
  (`change_validation.py` with `infer` / `run` / `check-drift`), `SKILL.md` + `README.md`,
  `templates/manifest.md`, and an always-loaded `CHANGE-VALIDATION-TRIGGER` protocol rule with the
  approved-gate silent no-op. Engine tests (B.4) green.
- The per-repo `CHANGE-VALIDATION.md` manifest is **inferred** from the toolchain, operator-approved,
  records a **layered fast/full** recipe (FULL ⊇ CI ∪ repo-checks), and **re-proposes** on toolchain
  drift (`check-drift`) without auto-editing.
- yf-plan §6.1.5 layer (b) **delegates** to the engine when an approved manifest is present, with
  `validate-cmd` as the middle fallback and the verbatim not-checked notice as the floor; the
  `validate-merged` output schema + exit-3 contract are unchanged; D.3 tests pass. **Zero `yf` Rust
  changes.**
- This repo **dogfoods** its own approved manifest: the FULL tier passes on the merged tree (closing
  the plan-014 "cross-plan regressions not checked" gap for future plans).
- #25 worktree-uv guidance is documented in yf-plan's worktree docs. #27 and #25 reconciled upstream.

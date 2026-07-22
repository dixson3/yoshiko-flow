---
type: Plan
okf_spec: OKF-PLAN
id: plan-032-james-dixson-6cb87b
author: james-dixson
created: '2026-07-22'
status: complete
deliverable_class: standard
fingerprint: edaafd7587d70d201988363f865ca9cf86b6e2e212492331d1d06b7bbd36af9d
epic: yf-mol-ifx
---
# Plan: yf harness tune — align Claude Code settings.json to the yf skill contracts

**ID:** plan-032-james-dixson-6cb87b
**Author:** james-dixson
**Created:** 2026-07-22
**Status:** complete
**Deliverable-class:** standard
**Epic:** yf-mol-ifx
**Fingerprint:** edaafd7587d70d201988363f865ca9cf86b6e2e212492331d1d06b7bbd36af9d

## Objective

Add `yf harness tune --harness <name>` — a harness-parameterized `yf` subcommand that
idempotently aligns a Claude Code `settings.json` to the recommended yf baseline (deny the
competing native tools, disable the competing features), plus a `yf doctor` extension that
reports settings/skills drift. Establish a single **machine-readable settings profile** as the
source of truth the binary embeds and the prose docs derive from. Ship the Claude Code profile
fully; design the command multi-harness but defer concrete non-Claude profiles to a follow-on
gated on the `yf-2gyv` per-harness research.

## Motivation

The yf-* skills assume the operator has turned **off** competing Claude Code built-ins — native
plan mode, `TodoWrite`/`Task*`, native workflows, bundled skills, Claude-only memory/dream/upload.
Today that assumption lives only in prose: `docs/recommended-settings.md`, the "Tune Claude Code
for the skills" install section, and per-skill `SKILL.md` notes. Prose steers the model but does
not remove the mechanism — the operator must hand-edit `settings.json`, and any drift between the
docs and the actual runtime is silent. This makes yf the actor: it aligns the runtime to the
contracts on demand (`yf harness tune`) and surfaces drift on inspection (`yf doctor`). Triggered
by follow-up bead `yf-nl8i`; the web-docs counterpart (a canonical settings block) is `yf-8ayq`,
which will consume the profile this plan creates.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|

_No existing upstream issue matched (searched "settings tools disable competing"). A single
coarse tracking issue is filed at intake per the project Upstream Tracking convention:_
**[dixson3/yoshiko-flow#95](https://github.com/dixson3/yoshiko-flow/issues/95)** — `plan-032 execution
tracking`. Source bead `yf-nl8i`; follow-on beads `yf-8agh` (multi-harness, gated on `yf-2gyv`),
`yf-up7s` (revert path).

## Investigation Findings

Recon (pre-scope), grounded in the codebase:

- **yf is a Rust/clap binary** (`yf/`, v0.4.0), subcommand-per-module under `yf/src/cmd/`, dispatch
  in `yf/src/main.rs:run()`, CLI surface in `yf/src/cli.rs`. `serde_json` is already configured with
  `features=["preserve_order"]`.
- **Canonical disable-list is prose today**: `docs/recommended-settings.md` (baseline block lines
  141-191). Highest-impact keys: `disableWorkflows: true`, `todoFeatureEnabled: false`. Boolean
  polarity is mixed — `disable*` keys are `true` to disable; `*Enabled` off-switches are `false`.
- **`Agent` MUST stay enabled** — every yf coordinator/investigator/reviewer fans out through it;
  the denied `Task*` tools are a *different* native surface (`recommended-settings.md:116-119`).
- **yf never writes settings keys today — only reads/prunes.** The beads `SessionStart` hook in
  `.claude/settings.json` is owned by `bd setup claude`, not yf; yf's only mutation is
  `prune_empty_settings()` (`yf/src/beads_init.rs:1305`), explicitly designed to never clobber a
  recommended-settings baseline. This feature introduces yf's **first settings-key writer**.
- **Established write precedent**: idempotent, marker-guarded, hand-edit-preserving (skill deploy's
  content-hash marker in `yf/src/marker.rs`; the never-clobber prune helpers). Embedding is
  `rust-embed` over `../skills` (`yf/src/embed.rs`).
- **SPEC surface**: repo-root `SPEC.md §3` uses `REQ-YF-<AREA>-NNN` ids with a top-of-file living
  amendment log; yf tests tag REQ ids and a `coverage.rs` gate enforces coverage.

## Approach

**SPEC-first.** Land `REQ-YF-TUNE` (new `SPEC.md §3.10`) + an amendment-log entry before any Rust
code; every behavior below is written against a REQ id and a tagged test.

**1. Canonical machine-readable settings profile (single source of truth).** A Claude Code profile
(embedded data) enumerating each recommended entry: its JSON path, recommended value, **kind
(scalar vs set-valued)**, polarity, and one-line rationale. The binary embeds it via a **separate
rust-embed root** (NOT under `../skills`, which treats every top-level dir as a skill and would
pollute tree-hash/marker logic). The **fenced reference-baseline block** in
`docs/recommended-settings.md` is a `jsonc` fence carrying hand-authored `//` rationale comments
*inside* it. The drift test **asserts agreement** — a JSONC-tolerant parse (strip `//` comments)
compares keys/values/array-membership to the profile — and does **not** regenerate the block
(regeneration would clobber the grouped multi-line comments). The comments are the hand-authored
prose and stay authored; only their key/value data is drift-checked. The web block (`yf-8ayq`)
consumes the same profile.

**2. `yf harness tune --harness <name> [--project [--committed]] [--force] [--dry-run] [--json]`.**
New top-level `yf harness` command group.

- **Scope**: default **user** (`~/.claude/settings.json`), matching skill-install default and
  staying disjoint from the project-scope beads hook `bd setup claude` owns. `--project` targets
  project scope; project default is `settings.local.json` (personal, gitignored), with `--committed`
  to target the shared `settings.json`. (Safe default is the gitignored file.)
- **Merge semantics (kind-aware).** The profile marks each entry **scalar** or **set-valued**:
  - **Scalar** (e.g. `disableWorkflows`, `todoFeatureEnabled`): **add-missing**; an existing key with
    a *different* value is **reported as a conflict and left untouched** unless `--force`.
  - **Set-valued** (e.g. `permissions.deny`, an array): **non-destructive union** — add the profile's
    missing elements, **never remove** existing ones (preserves the user's custom denies and
    `rm -rf` safety globs). Union needs no `--force`; it cannot clobber.
  Idempotent (re-run is a no-op); preserves existing JSON structure/order (`preserve_order`).
- **Fail-safe.** On a malformed/unparseable settings.json the writer **refuses and reports** (never
  overwrites), mirroring `prune_empty_settings`. On write it preserves the `bd setup claude` hook
  block untouched.
- **Invariant**: never deny/disable `Agent`; encode the mixed boolean polarity in profile data so it
  cannot be hand-fumbled. `--dry-run` prints the diff without writing.

**3. `yf doctor` extension.** Add a read-only check dimension via the `yf/src/cmd/doctor/checks.rs`
trait registry: alongside yf prerequisites, report settings **drift from the profile**, computed over
the **effective merged view** across precedence layers (user ← project `settings.json` ←
`settings.local.json`) so a key set in a *different* layer is not a false "missing" (missing
recommended entries, scalar conflicts, `Agent` accidentally denied). The profile itself is the
reference set — no marker needed. The check is **report-only**; remediation is to run `yf harness
tune`. It is deliberately **decoupled from `yf doctor --repair`** (which short-circuits to the
beads-init repair per REQ-YF-PRE-007 and must not gain a settings write — mirroring how
`--prune-formulas` is its own decoupled affordance), so the drift check never dead-codes and
PRE-007's contract is untouched.

**4. Install-time offer (flag-gated, no prompt).** `yf skills install` gains a `--tune` opt-in that
runs `yf harness tune` after install. There is **no interactive TTY prompt** (the yf binary has no
prompt precedent and install runs non-interactively); without `--tune`, install reports that tuning
is available and does nothing to settings.json.

**5. Multi-harness posture (`--harness` is a forward-compat lookup key).** The command surface and
SPEC carry a harness dimension, but the **merge engine, scope resolution, and JSON model are
Claude-Code-specific in this plan** — a future harness (codex → `.codex/config.toml` TOML, etc.)
needs a *new engine*, not merely a new profile. Only the Claude Code profile is implemented; an
unknown `--harness` yields a clean "profile not yet available" refusal, not a stub write. Concrete
codex/opencode/pi support is a follow-on bead gated on the `yf-2gyv` research.

## Epics

### Epic 1: SPEC — REQ-YF-TUNE (lands first)

- Issue 1.1: Add `SPEC.md §3.10 Harness settings tuning (REQ-YF-TUNE)` — requirements for the profile
  model, the `tune` command (scope, merge semantics, Agent invariant, idempotence), the doctor check,
  the install offer, and the multi-harness abstraction (Claude Code implemented; others deferred).
- Issue 1.2: Add the living-amendment-log entry at the top of `SPEC.md`.
  - depends-on: 1.1
- Issue 1.3: Add the new `REQ-YF-TUNE-*` ids to the `yf/src/coverage.rs` `ALLOWLIST` in the **same
  change-set**, so the coverage gate stays green while implementing epics land; each id is removed
  from the allowlist as its epic lands the tagged test.
  - depends-on: 1.1

### Epic 2: Canonical settings profile + embed

- Issue 2.1: Define the machine-readable Claude Code profile data (JSON path, value, **kind**
  scalar/set-valued, polarity, rationale for each entry), derived from
  `docs/recommended-settings.md:141-191`.
  - depends-on: 1.1
- Issue 2.2: Embed the profile via a **separate rust-embed root** (NOT under `../skills` — that would
  surface as a bogus skill and pollute tree-hash/marker logic) + a loader with a typed profile model.
  - depends-on: 2.1
- Issue 2.3: Drift test — **assert-agreement** on the fenced reference-baseline `jsonc` block in
  `docs/recommended-settings.md`: JSONC-tolerant parse (strip `//` comments), compare
  keys/values/array-membership to the profile, fail CI on divergence. Does **not** regenerate the
  block (the block's `//` comments are hand-authored prose and are preserved).
  - depends-on: 2.2

### Epic 3: `yf harness tune` command

- Issue 3.1: CLI surface — `yf harness` group + `tune --harness/--project/--committed/--force/--dry-run/--json`
  in `cli.rs` + dispatch in `main.rs` + `cmd/harness.rs`. Unknown `--harness` → clean refusal.
  - depends-on: 1.1
- Issue 3.2: Merge engine — **kind-aware** (scalar add-missing/conflict-report; set-valued union),
  idempotent, preserve-order, **Agent-never-denied**, **fail-safe on unparseable input** (refuse +
  report), preserves the `bd setup claude` hook block, scope resolution (user / project-local /
  project-committed).
  - depends-on: 2.2, 3.1
- Issue 3.3: `--dry-run` diff output + `--json` mode.
  - depends-on: 3.2
- Issue 3.4: REQ-tagged tests — fresh file; idempotent re-run; scalar conflict-report-vs-`--force`;
  Agent stays enabled; both scopes; dry-run; **malformed settings.json refuses without data loss**;
  `bd setup claude` hook block preserved.
  - depends-on: 3.2
- Issue 3.5: Set-valued union test — a pre-existing `permissions.deny` with the user's custom denies
  and `rm -rf` safety globs is **unioned** (profile denies added, user entries preserved, nothing
  removed).
  - depends-on: 3.2

### Epic 4: `yf doctor` settings drift check

- Issue 4.1: Add the read-only drift check computing the **effective merged view** across precedence
  layers (user ← project `settings.json` ← `settings.local.json`); reports missing entries, scalar
  conflicts, and `Agent`-denied. Reuses the profile loader as the reference set.
  - depends-on: 2.2
- Issue 4.2: Wire into `yf doctor` output + `--json` as a **report-only** axis; remediation text is
  "run `yf harness tune`". Decoupled from `--repair` (no settings write under `--repair`; PRE-007
  short-circuit untouched).
  - depends-on: 4.1
- Issue 4.3: REQ-tagged tests — including the **"recommended key set in a different layer is not a
  false-missing"** case.
  - depends-on: 4.1

### Epic 5: Install-time tune offer (flag-gated)

- Issue 5.1: `yf skills install --tune` runs `yf harness tune` after install; without `--tune`,
  report that tuning is available and touch nothing. No interactive prompt.
  - depends-on: 3.2
- Issue 5.2: REQ-tagged test for the `--tune` opt-in path and the no-op default.
  - depends-on: 5.1

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

## Risks & Mitigations

| Risk | Mitigation |
|:-----|:-----------|
| Clobbering deliberate user settings | Kind-aware merge: scalars add-missing + report-conflict (no overwrite without `--force`); set-valued keys (`permissions.deny`) **union only** (never remove user entries / safety globs); never touch `Agent`; idempotent; `--dry-run`; fail-safe refuse on unparseable input. Reversal is a follow-on (doctor uses the profile, not a marker, as its reference set). |
| Silent drift between the profile and the doc baseline block | Machine-readable profile is the single source; the fenced reference-baseline block is drift-checked by assert-agreement (Issue 2.3, JSONC-tolerant parse) and fails CI on divergence; the block's `//` comments stay hand-authored. |
| Corrupting the `bd setup claude` hook block | Tune writes only its own profile keys and preserves the hook block; user scope (default) is disjoint from the project hook. |
| Coverage gate reds between SPEC and impl | New REQ ids added to `coverage.rs` ALLOWLIST in Epic 1's change-set; removed per-id as each epic lands its tagged test. |
| Project `settings.json` vs `settings.local.json` ambiguity | Explicit scope flags; safe default is the gitignored `settings.local.json`; `--committed` is opt-in. |
| Boolean-polarity bugs (`disable*`=true vs `*Enabled`=false) | Polarity encoded in profile data, not open-coded; unit tests assert both directions. |
| Multi-harness overreach without research | Only Claude Code implemented; unknown harness → clean refusal; codex/opencode/pi deferred to a follow-on gated on `yf-2gyv`. |
| `yf doctor` scope creep | New check is strictly read-only and additive; `--repair` only *offers* tune. |
| Collision with the `bd setup claude` beads hook | User scope is the default and is disjoint from the project hook; tune only writes its own keys and preserves the hook block. |

## Success Criteria

- SPEC `REQ-YF-TUNE` (and amendment-log entry) land **before** implementation; REQ-tagged tests pass;
  the `coverage.rs` gate stays green.
- `yf harness tune --harness claude-code` on a fresh file produces a settings.json matching the profile;
  a second run is a no-op; a pre-existing **scalar** conflict is **reported, not clobbered** (unless
  `--force`); a pre-existing `permissions.deny` array is **unioned** (user entries + `rm -rf` globs
  preserved, profile denies added); `Agent` is never denied; a malformed settings.json is refused
  without data loss; the `bd setup claude` hook block survives.
- User scope (default) and both project targets (`settings.local.json`, `--committed settings.json`) write
  the correct file.
- `yf doctor` reports settings drift over the **effective merged view** across precedence layers,
  read-only; a key set in a different layer is not a false-missing.
- `yf skills install --tune` runs the tune; without `--tune` it touches nothing (no interactive prompt).
- A single machine-readable profile is the source of truth; the drift test on the fenced doc block guards sync.
- Multi-harness follow-on filed as a bead gated on `yf-2gyv`; unknown-harness invocation refuses cleanly.
- REQ-tagged tests pass and the `coverage.rs` gate stays green throughout (ALLOWLIST bridge per Issue 1.3).

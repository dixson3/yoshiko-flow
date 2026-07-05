# Plan: Beads infra / local-only hardening (#58, #67, #66, #57)

**ID:** plan-023-james-dixson-b618bb
**Author:** james-dixson
**Created:** 2026-07-05
**Status:** reconciling
**Epic:** yf-mol-p1f
**Fingerprint:** 4636eb036cfd5fd8603025fd368d624df76ca3ae787e37ab99f8e6dab32b7762
**Phase log:**
- 2026-07-05 scoping: initial scope captured (6 issues triaged → 4 active, 1 deferred, 1 superseded)
- 2026-07-05 investigating: 1 experiment identified (EXP-001 minimal-local profile surface)
- 2026-07-05 investigating: EXP-001 concluded — profile = embedded + local-only + worktree-shared; #67 namespace partially built
- 2026-07-05 drafting: plan v1 synthesized (EXP-001 concluded)
- 2026-07-05 review: plan v1 presented for review
- 2026-07-05 review: pass-2 red-team REVISE (narrow); 2 textual concerns fixed in-pass
- 2026-07-05 approved: operator approved (pass-2 red-team APPROVE; portability audit pass)
- 2026-07-05 intake: epic yf-mol-p1f poured
- 2026-07-05 executing: start gate resolved
- 2026-07-05 reconciling: post-execution reconciliation

## Objective

Harden the **beads infrastructure** around yf's "always local-only" model: define and enforce a
canonical **minimal-local beads profile**, tidy config/gitignore hygiene, and fix a rule-wording
hazard that invites raw `bd github push`. Covers upstream #58 (anchor), #67, #66, #57.

## Motivation

yf beads is intentionally **local-only** — one per-repo Dolt DB, reachable from every worktree,
never synced upstream (issue tracking goes to GitHub via `yf-beads-upstream`, orthogonally).
plan-022 already hardened the *remote-hygiene* edge of this model (two-layer `--remove-remote`,
the 1.1.0 migrate-gate). This plan hardens the rest of the local-only surface:

- **#58** — there is **no single profile** `yf preflight` asserts. Each repo's `bd` config is
  whatever `bd init` left; the engine mode in particular drifts (server vs embedded), and nothing
  confirms the per-repo, local-only, worktree-shared shape. Every beads-backed skill inherits
  whatever drift is present.
- **#67** — skill **config** (`/.<skill>.local.json`, root-level dotfiles) and skill **state**
  (`.yf/<shortname>/…`) live in inconsistent places; each new skill adds another top-level
  dotfile + gitignore anchor.
- **#66** — `yf-beads-init` repair untracks `.beads/interactions.jsonl` but nothing **ignores**
  it, so it immediately resurfaces as `?? .beads/interactions.jsonl` noise (a #39 canonicalization
  gap).
- **#57** — the always-loaded close-time **Safety invariant** in `UPSTREAM_TRACKING.md` reads as a
  hand-CLI recipe, so an agent can satisfy the guardrail with a raw `bd github push --dry-run`
  while **skipping** the routing sentence that says to invoke `/yf-beads-upstream` (observed live).

Who is affected: every operator on a local-only yf beads repo — profile drift, config clutter,
gitignore noise, and the mis-framed rule all recur per-repo until the tooling handles them.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #58 | Canonical minimal-local beads profile enforced via yf preflight | include | Define + detect + offer-repair (conservative; no silent preflight mutation) | Epic 1 |
| #67 | Migrate `.<skill>.local.json` → `.yf/` namespace | include | Pattern (1) `.yf/<skill>/config.local.json`; migrate legacy files | Epic 2 |
| #66 | gitignore `interactions.jsonl` in repair's top-up | include | One entry in the `.beads/.gitignore` top-up set | Epic 3 |
| #57 | Reword close-time Safety invariant (don't invite raw `bd github push`) | include | Rule-wording hardening in `UPSTREAM_TRACKING.md` | Epic 3 |
| #60 | `requires:<platform>` worklist labels | **defer** | A distinct upstream *feature* (OS worklist filtering), not local-only hygiene — its own plan | — |
| #65 | plan-019 tracker | **supersede** | Already shipped (plan-019 complete, merge `baa9379`, REQ-YF-PRE-008/009/SELF-007 present) — close only, no work | reconcile (close) |

## Investigation Findings

### EXP-001 — CONCLUDED: profile surface defined. See `findings/exp-001-minimal-local-profile.md`.

**Profile = inspectable invariants** (all readable by preflight; no live mutation needed to detect):
1. **local-server engine mode** — the repo runs a Dolt server (`dolt-server.{pid,port}` under this
   repo's `.beads/`, `dolt_mode: "server"` in `.beads/metadata.json`). This is the **only
   read-only-observable** engine-mode signal: `bd` always writes `dolt-server.*` under the repo's
   own `.beads/`, and there is **no `--shared-server` flag / host-port config** in the code
   (EXP-001 §A), so "per-repo vs a hypothetical global/shared server" has **no observable** and is
   *not* an asserted axis (pass-2). The detectable rule is simply: **server-files present ⇒
   conformant; embedded (`dolt_mode: embedded` / no `dolt-server.*`) ⇒ detect/warn-only drift**,
   never auto-migrated (embedded is out of scope, operator decision).
2. **worktree-shared** — automatic: bd resolves the canonical `.beads/` via **git-common-dir**
   (yf-plan's INV-2, `plan_manager.py:1178`), so every worktree reaches the one per-repo server.
   Local-server is the mode that makes this **concurrency-safe** (the #58 motivation).
3. **local-only** — `dolt.local-only true` + zero `dolt_remotes` rows + no `sync.remote` (read by
   `bd_config_value`/`dolt_remote_names`/`has_local_only_remote`, the plan-022 machinery). This is
   the axis `doctor --repair` actually **corrects**.

**Engine-mode decision (operator, superseding EXP-001's embedded recommendation): CANONICAL =
per-repo LOCAL-SERVER.** EXP-001 recommended embedded, but its worktree-sharing test was
**sequential only** — it never exercised #58's motivating concern, **concurrent** multi-client
access, where embedded's single-process file locking contends and a per-repo local server is the
safe answer (pass-1 red-team, HIGH). Operator decision: **support per-repo local-server** (the mode
that makes concurrent worktree-issue-sharing safe) and **drop embedded** to keep the profile simple.
Consequences: (a) this repo (`dolt_mode: server`) is **conformant**, not drift; (b) there is **no
server→embedded migration** to build (the riskiest correction, unproven — pass-1 concern 2 — is
eliminated); (c) the only observable engine-mode drift, an **embedded** store (`dolt_mode: embedded`
/ no `dolt-server.*`), is **detect/warn-only** — surfaced with guidance, never auto-migrated (the
"per-repo vs shared server" sub-distinction has no read-only observable and is not asserted, pass-2).
Corrections `doctor --repair` actually applies are the **safe** local-only/no-remote axes (reused
plan-022 machinery).

**Integration points (honor the read-only-preflight / mutating-doctor split):** the profile-drift
check folds into `detect_canonicalization_drift` (`preflight.rs:709`, read-only offer) and
`beads_init::repair` (`beads_init.rs:407`, `--repair` correction), exactly like REQ-BINIT-023.

**#67 config-resolution reality (refines Epic 2):** the `.yf/` config namespace is **partially
built** — `read_config` (`preflight.rs:430`) already prefers a **flat** `.yf/<short>.local.json`
(e.g. `.yf/plan.local.json`), then falls back to the legacy root `.<skill>.local.json`. State is at
`.yf/<short>/preflight.json` (**short** name via `resolve_skill`, `preflight.rs:221`).
`migrate.rs` (REQ-YF-MIGRATE-001, `SKILL_MAP` at `:30`) is the reusable idempotent never-clobber
mover. **Two live inconsistencies #67 must fix:** (1) `migrate.rs` writes state to `.yf/yf-plan/`
(**full** name) while `preflight.rs` reads `.yf/plan/` (**short**) — they disagree; (2) the
shortname map is **duplicated** (`preflight.rs::resolve_skill` vs `migrate.rs::SKILL_MAP`), not
centralized.

## Approach

Three epics, **SPEC-first** (SPEC/`REQ-*` edit lands ahead of code, per AGENTS.md). Epic 1 (#58) is
the anchor and depends on EXP-001; Epics 2–3 are independent and smaller.

- **Epic 1 — Minimal-local profile: define + detect + offer-repair (#58).** SPEC the canonical
  profile: **per-repo local-server + worktree-shared + local-only / no-remote** (embedded dropped;
  operator decision). Extend `yf preflight` to **detect** drift (read-only, folded into
  `detect_canonicalization_drift`) and **offer** `yf doctor --repair`; extend `beads_init::repair`
  to **correct the SAFE axes** (local-only / no-remote) under operator authorization — reusing the
  plan-022 remote-hygiene machinery. **No engine-mode migration is built** (the risky, unproven
  server↔embedded conversion is out of scope): the only observable engine-mode drift, an **embedded
  store**, is **detect/warn-only**, surfaced with guidance, never auto-corrected. This repo
  (local-server) is conformant and the natural first *pass* fixture.
- **Epic 2 — Config → `.yf/` namespace (#67).** The namespace is **partially built** (EXP-001):
  `read_config` already reads a flat `.yf/<short>.local.json`. Adopt #67 pattern (1) —
  `.yf/<short>/config.local.json` **co-located with the `.yf/<short>/` state dir** (short name, to
  match state) — as the canonical location; update resolution precedence (new subdir → existing
  flat `.yf/<short>.local.json` → legacy root `.<skill>.local.json`, back-compat throughout).
  **Fix the two EXP-001 inconsistencies:** reconcile `migrate.rs`'s full-name `.yf/yf-plan/` vs
  `preflight.rs`'s short-name `.yf/plan/` (standardize on short), and **centralize the shortname
  map** (one `resolve_skill`, shared with `migrate.rs`). Extend REQ-YF-MIGRATE-001 to move legacy
  root dotfiles (and the flat `.yf/` form) into the subdir; collapse top-level gitignore anchors to
  one `.yf/` anchor.
- **Epic 3 — Hygiene + rule wording (#66 + #57).** (#66) Add `interactions.jsonl` to the repair's
  `.beads/.gitignore` top-up set so the untracked file is also ignored. (#57) Reword the
  `UPSTREAM_TRACKING.md` close-time trigger so the **routing** sentence (invoke
  `/yf-beads-upstream`) is primary and the Safety invariant reads as a constraint on the skill's
  push, not a hand-CLI how-to — closing the "raw `bd github push` looks compliant" gap.

## Epics

### Epic 1: Minimal-local profile — define + detect + offer-repair (#58)
- Issue 1.1: SPEC — canonical profile (per-repo local-server + worktree-shared + local-only / no-remote; embedded out of scope) + the detect/offer/correct contract, split into **correctable** (local-only/no-remote) vs **detect/warn-only** (engine-mode) axes. Target surfaces named: new `REQ-BINIT-*` in `skills/yf-beads-init/SPEC.md` (repair) + the profile invariants in root `SPEC.md` `REQ-YF-*` (preflight); coverage-gate the new ids.
- Issue 1.2: `yf preflight` — read-only profile-drift detection folded into `detect_canonicalization_drift` (`preflight.rs:709`); surfaces a warn on engine-mode drift and an offer for the correctable axes. No silent mutation.
  - depends-on: 1.1
- Issue 1.3: `yf doctor --repair` — correct the **safe axes only** (assert `dolt.local-only`, remove stray remotes) via the plan-022 machinery in `beads_init::repair` (`beads_init.rs:407`); engine-mode drift is reported, never migrated.
  - depends-on: 1.1
- Issue 1.4: Tests — profile-drift fixtures: missing local-only / stray remote → detect + repair (pass); embedded (`dolt_mode: embedded` / no `dolt-server.*`) → detect/warn (no mutation); local-server → conformant pass. (No shared-server fixture — that distinction has no read-only observable, pass-2.) (cargo test + change-validation)
  - depends-on: 1.2, 1.3

### Epic 2: Config → `.yf/` namespace (#67)
- Issue 2.1: SPEC — canonical config location `.yf/<short>/config.local.json` (co-located with `.yf/<short>/` state); resolution precedence (new subdir → flat `.yf/<short>.local.json` → legacy root dotfile); the short-name standardization + centralized shortname map contract; migration + single `.yf/` gitignore anchor
- Issue 2.2: `yf` kernel — `read_config` resolves the new subdir first, back-compat through the flat and legacy forms; **centralize `resolve_skill`** and make `migrate.rs` consume it (fixes the full-vs-short `.yf/yf-plan/` vs `.yf/plan/` inconsistency). **Decouple the state short-name from the config-basename (pass-1 concern 4):** the SKILL_MAP short-name fix must not misroute config (state dir = `.yf/<short>/`, config file name is its own axis); add a fixture proving config still resolves after the SKILL_MAP change.
  - depends-on: 2.1
- Issue 2.3: Migration — extend REQ-YF-MIGRATE-001 (`migrate.rs` SKILL_MAP) to move legacy root `.<skill>.local.json` **and** the flat `.yf/<short>.local.json` into `.yf/<short>/config.local.json` (idempotent, never-clobber); collapse top-level gitignore anchors to one `.yf/` anchor. **Mark the flat `.yf/<short>.local.json` tier transitional (pass-1 concern 5):** it is a back-compat read only, slated for removal once migration is ubiquitous — file a follow-up cleanup bead at land-the-plane.
  - depends-on: 2.2
- Issue 2.4: Tests — resolution precedence (3 forms), shortname-map centralization, and migration fixtures (legacy + flat → subdir)
  - depends-on: 2.2, 2.3

### Epic 3: Hygiene + rule wording (#66 + #57)
- Issue 3.1: SPEC — (#66) `interactions.jsonl` in the `.beads/.gitignore` top-up set (REQ-BINIT-012/023); (#57) close-time trigger routing-primary wording contract in the UPSTREAM_TRACKING rule
- Issue 3.2: #66 — add `interactions.jsonl` to the repair gitignore top-up (kernel) + SKILL.md list; test the untracked-then-ignored no-resurface behavior
  - depends-on: 3.1
- Issue 3.3: #57 — reword `UPSTREAM_TRACKING.md` so invoke-`/yf-beads-upstream` is primary and the Safety invariant is a skill-push constraint, not a hand-CLI recipe; refresh the rule manifest hash
  - depends-on: 3.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

_(EXP-001 concluded during planning — profile surface defined, integration points located;
engine-mode set by operator to per-repo local-server (embedded dropped) — so no capability gate
blocks execution. No engine-migration spike is needed since engine-mode correction is out of scope.)_

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step
- **Logical per-issue independence (pass-1 concern 3, scoped by pass-2).** The epics are
  independent, so each upstream issue's disposition maps cleanly to its own epic — but this is a
  **single whole-plan reconcile** (`auto`, all beads closed), not a separate per-epic gate: the
  independence is *logical*, applied at the one reconcile step, not a mechanism that closes #66/#57
  before #58. The stall risk that motivated concern 3 is largely gone anyway (Epic 1 de-risked to
  detect/warn + reused plan-022 machinery). #65 closed as superseded (plan-019 already shipped);
  #60 left open (deferred to its own plan).

## Risks & Mitigations

- **#58 engine-mode correction is OUT of scope (pass-1 concerns 1+2 resolved).** Converting a live
  DB's engine mode (server↔embedded) is invasive and unproven; the operator chose per-repo
  local-server as canonical and dropped embedded, so **no engine migration is built**. *Mitigation:*
  engine-mode drift is **detect/warn-only** (surfaced with guidance, never mutated); `doctor
  --repair` corrects only the safe local-only/no-remote axes via proven plan-022 machinery. If an
  operator later wants engine-mode *correction*, that is its own plan with a proven mechanism.
- **#67 back-compat break.** Moving config could strand repos with existing root-level configs.
  *Mitigation:* resolution reads the new location first but falls back to the legacy path;
  migration is idempotent and preserves values; never delete a legacy file the operator still
  relies on without migrating it.
- **Installed-copy staleness.** Modified kernel/skills must be tested against the in-repo build /
  sandboxed HOME, never the installed rust-embed copy (TESTING.md).
- **Rule-manifest drift (#57).** Editing `UPSTREAM_TRACKING.md` requires refreshing its manifest
  hash or preflight flags it drifted. *Mitigation:* run `manifest_update.py` on the protocols dir.

## Success Criteria

1. The canonical profile (per-repo local-server + worktree-shared + local-only / no-remote;
   embedded out of scope) is specified as asserted invariants. `yf preflight` **detects** drift
   (read-only), **warns** on engine-mode drift, and **offers** `yf doctor --repair` for the
   correctable axes; `yf doctor --repair` **corrects only** local-only / no-remote (plan-022
   machinery), never migrating engine mode. Fixtures pass: missing-local-only/stray-remote →
   detect+repair; embedded → detect+warn (no mutation); local-server → conformant. **No
   engine-migration fixture** and **no shared-server fixture** (both out of scope — the latter has
   no read-only observable, pass-2).
2. Skill config resolves from `.yf/<short>/config.local.json` (co-located with `.yf/<short>/`
   state) with flat-`.yf/` and legacy root-level back-compat; the short-vs-full-name kernel
   inconsistency is fixed with a centralized `resolve_skill`; existing configs (legacy + flat)
   migrate idempotently; top-level gitignore anchors collapse to one `.yf/` anchor.
3. `yf doctor --repair` adds `interactions.jsonl` to `.beads/.gitignore`; after repair the file is
   untracked **and** ignored (no `?? .beads/interactions.jsonl` resurfacing).
4. The `UPSTREAM_TRACKING.md` close-time trigger makes invoke-`/yf-beads-upstream` primary; the
   Safety invariant no longer reads as a standalone hand-CLI recipe (a raw `bd github push` no
   longer looks like the compliant path). Rule manifest hash refreshed.
5. #65 closed as superseded; #60 left open (deferred). All changes SPEC-first; full
   change-validation tier green.

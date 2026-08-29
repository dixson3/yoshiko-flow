---
type: Plan
okf_spec: OKF-PLAN
id: plan-022-james-dixson-14b3dd
author: james-dixson
created: '2026-07-05'
status: complete
epic: yf-mol-pvb
fingerprint: 9f13529df9762b1c6b37bcc21442336b0cc12424661ff37303f4ed9b98d024be
---
# Plan: Certify yf beads skills against bd 1.1.x and harden local-only remote hygiene (#68, #61)

**ID:** plan-022-james-dixson-14b3dd
**Author:** james-dixson
**Created:** 2026-07-05
**Status:** complete
**Epic:** yf-mol-pvb
**Fingerprint:** 9f13529df9762b1c6b37bcc21442336b0cc12424661ff37303f4ed9b98d024be

## Objective

Certify the yf beads skills against **bd 1.1.x** (installed Homebrew build is 1.1.0; skills
pin 1.0.5) and harden the **local-only remote-hygiene** path so bd's 1.1.0 remote-migrate gate
and canonicalization drift are resolved cleanly and self-describingly. Covers upstream issues
**#68** (certification) and **#61** (remote cleanup + upstream-trigger phrasing + enumerate bug).

## Motivation

Two coupled realities forced this plan, both discovered live while starting it in this repo:

1. **bd 1.1.0 is already installed** (Homebrew) while every skill still pins/verifies against
   **1.0.5**. The 1.1.0 line is one theme — a **safe schema-migration/upgrade path** — which is
   precisely the machinery `yf-beads-init`'s repair engine drives, so the pins are not cosmetic:
   uncertified guidance can be wrong exactly where it matters most.
2. **bd is always local-only for yf** (interchange is `gh`/`glab` issue trackers and, at most,
   local worktrees sharing one Dolt server — never a shared Dolt remote). But bd 1.1.0's
   **state-aware remote-migrate gate** (`BD_SMART_GATE`, on by default) treats a configured
   remote as "remote-backed" and **refuses to auto-migrate** — wedging `bd status` into an
   error-JSON-with-exit-0 (the false-negative the beads protocol warns of). Clearing this live
   used (a) removing `sync.remote` from `config.yaml`, (b) `bd dolt remote remove origin` (a
   *separate* **Dolt-DB-level** remote the config edit did not touch — distinct from the git
   `origin`), and (c) the `BD_ALLOW_REMOTE_MIGRATE=1 bd migrate` override. Because those were
   applied together, **which step actually cleared the gate is unproven** — Epic 4's micro-
   experiment (Issue 4.2) tests whether canonicalization (a+b) alone suffices, making (c)
   unnecessary for a local-only repo. That hand-sequence is exactly what #61 asks the tooling to
   automate and self-describe.

Who is affected: every operator on a local-only yf beads repo who upgrades bd — the gate
false-positive and the two-layer remote drift will re-trip on each upgrade until the tooling
handles it.

**Triggering event:** `yf preflight yf-plan` reported `bd_not_initialized` (false-negative) on
this repo; the underlying cause was 4 pending schema migrations (v49→v53) blocked by the gate.
Resolved live during scoping (see Investigation Findings → live fixture).

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #68 | Certify yf beads skills against bd 1.1.x | include | Empirical + pin bumps + false-text corrections | Epics 1–3 |
| #61 | yf-beads-upstream/hygiene: `--remove-remote` cleanup + trigger phrasing + enumerate bug | include | Remote-hygiene automation + trigger + `_shared` enumerate fix | Epics 4–5 |

## Investigation Findings

### Live fixture (resolved during scoping)

This repo *was* the wedged fixture. Worked through by hand, producing certification evidence:

- **False-negative confirmed on 1.1.0 (server mode):** `bd status --json` returned an `error`
  key with **exit 0** (`refusing to auto-apply 4 pending schema migrations … remote-backed`);
  `bd ready`/`bd list` still worked. Classification = **corrupted/wedged**, never
  `not_initialized`. The beads-protocol false-negative invariant **still holds** on 1.1.0.
- **Remote-migrate gate is a false-positive for local-only:** the gate fired despite
  `dolt.local-only: true`, keyed on the git `origin`'s existence. Removing `sync.remote`
  (config layer) did **not** clear it; a **second** `bd dolt remote remove origin` (Dolt-DB
  layer) was required — direct confirmation of #61 requirement 2.
- **Resolution sequence applied (all at once):** edit `config.yaml` (drop `sync.remote`) → `bd
  dolt remote remove origin` (the Dolt-DB-level remote, not the git origin) →
  `BD_ALLOW_REMOTE_MIGRATE=1 bd migrate` (schema 1.0.4→1.1.0, v49→v53, **no** `bd dolt push` —
  local-only) → `yf doctor` "all axes healthy". 564 issues preserved (backed up pre-migrate to
  scratchpad JSONL). **Caveat:** the three steps were applied together, so this is not proof the
  override was required — Issue 4.2 isolates that.

### EXP-001 — CONCLUDED: VERDICT A (escape hatch replaceable)

Full evidence in `findings/exp-001-embedded-wedged-commit.md`. A genuine wedged **embedded**
fixture was reproduced on 1.1.0 (schema-49 embedded DB built by a from-source bd 1.0.5, dirtied,
reopened by 1.1.0 which carries real pending migrations 0050–0053):

- **Both `bd dolt commit` and `bd vc commit` open the wedged embedded DB and commit the dirty
  working set data-preservingly, bypassing the migration guard.** The next open then cleanly
  applies migrations to v53.
- **bd 1.1.0's own wedge error message now prescribes `bd dolt commit`** as the fix — the
  recommended replacement command.
- **`bd migrate schema` still fails** on the wedged DB (chicken-and-egg for *that* command
  remains real — the SKILL.md is correct on that point), so the fix is `bd dolt commit` →
  `bd migrate`, not raw dolt and not `bd migrate schema`.
- **Consequence:** the yf-beads-init embedded escape hatch is **replaceable** with `bd dolt
  commit` (run from repo root; bd finds the embedded DB itself), dropping the raw-dolt
  dependency and the derive-Dolt-repo-dir step. The SKILL.md warning that `bd vc commit`
  "cannot open the wedged DB" is **provably false on 1.1.0** and must be corrected.

### Known implementation constraint (from code read + red-team verification)

- The active-set classifier is **`_shared/active_set.py`** (`classify_active`, `ACTIVE_CLAIMED
  = status==open AND owner non-empty`) — a plan-013 glossary decision. `_shared/sync.py` is only
  the **vendoring tool** that copies it into consumers (the `# >>> generated by _shared/sync.py`
  banner names the *copier*, not the source). It is consumed by **both** `upstream.py`
  (enumerate) **and** `yf-beads-hygiene`'s `beads_hygiene.py` (reconcile hoist candidates).
- **Fix decision (operator): #61 option (b) — a localized enumerate knob.** The #61 bug is fixed
  in **`upstream.py`'s enumerate path only** (a config knob / local override for owner-on-create
  repos), leaving the **shared plan-013 glossary and hygiene-reconcile semantics untouched**.
  This is the lowest-blast-radius fix and avoids mutating a two-consumer shared invariant.

### Epic 2 target correction (red-team verification)

- `MIN_BD_VERSION` / `_parse_bd_version()` are **absent** from `plan_manager.py` and
  `research_manager.py` (removed in a prior refactor). They survive only as **stale prose in
  `spec/prerequisites.md`**. Epic 2 therefore has **no manager tuples to bump** — it fixes the
  drifted prose and bumps the pins that actually exist. No runtime version floor is added (see
  Epic 1 decision: the bd<1.1.0 path is retained, so no hard floor is needed).

## Approach

Five epics, **SPEC-first** (each behavior change lands its `SPEC.md`/`REQ-*` edit ahead of the
code/doc change, per the repo AGENTS.md mandate). EXP-001 concluded during planning.

- **Epic 1 — yf-beads-init 1.1.0 certification (EXP-001 concluded: VERDICT A).** Make the
  embedded-storage escape hatch **version-branched**: **`bd dolt commit` → `bd migrate`** as the
  preferred path on **bd ≥ 1.1.0** (bd's own error now prescribes it), while **retaining the raw
  `dolt add -A && dolt commit` path as the documented bd < 1.1.0 fallback** (no runtime floor is
  added, so older-bd operators must not be stranded). Correct the now-false "`bd vc commit`
  cannot open the wedged DB" claim to be version-conditional; keep the correct note that `bd
  migrate schema` still fails on a dirty set. Re-affirm the false-negative invariant (confirmed
  live). Add a one-line local-only note about the remote-migrate gate default flip.
- **Epic 2 — Version-pin sweep (all skills).** Bump every certification `1.0.5` → `1.1.0` where
  it is a *pin/banner/floor*: `min-bd-version` in yf-plan/yf-research/yf-beads-init/
  yf-beads-upstream frontmatter, the yf-beads-extra banner, the yf-beads-hygiene README, and the
  `spec/*.md` "verified against 1.0.5" floors — **and fix the drifted `MIN_BD_VERSION` /
  `_parse_bd_version()` prose in `spec/prerequisites.md`** (those constants no longer exist in
  the managers; the prose is stale). **No runtime floor is added** (Epic 1 keeps the bd<1.1.0
  path). SPEC-first where a REQ pins the floor.
- **Epic 3 — yf-beads-extra false-text corrections.** Bump the "Verified against 1.0.5" banner
  to note 1.1.0 verification; annotate the batch-section "empty create → stop" warning that its
  specific 1.0.x cause (orphaned `child_counters` bricking `bd create`) is **fixed in 1.1.0**
  (keep the defensive advice). Structurally the gotchas are unchanged 1.0.5→1.1.0.
- **Epic 4 — Local-only remote-hygiene automation (#61 req 1–3).** Fix the preflight/doctor
  **instruction string** to emit the command that actually works (`yf doctor --repair
  --local-only --remove-remote`; current omits `--local-only`, a no-op). Make `--remove-remote`
  drop **both** layers (`sync.remote` config **and** the Dolt-DB-level `bd dolt remote remove
  <name>`) in one invocation. **Canonicalization is the primary gate fix:** removing both remote
  layers makes bd 1.1.0's remote-migrate gate **moot** for a local-only repo (the gate keys on
  remote existence) — a micro-experiment (Issue 4.3) confirms remove-remote-alone clears the
  gate. The `BD_ALLOW_REMOTE_MIGRATE` override **stays operator-gated and is NOT auto-run** (it
  remains the human coordination decision the Motivation describes); repair only *documents* it
  as the escape hatch when a remote is intentionally retained. Add the three-mechanism
  disambiguation table (`git push` vs `bd dolt push` vs `yf-beads-upstream` / `gh` mirror) to
  yf-beads-upstream and/or yf-beads-hygiene.
- **Epic 5 — yf-beads-upstream trigger + enumerate fix (#61 req 2-bonus).** Add mid-session
  intent triggers ("push/sync upstream", "mirror this bead upstream") disambiguated from `bd
  dolt push`. Fix the enumerate bug via **#61 option (b) — a localized enumerate knob in
  `upstream.py`** (a config option for owner-on-create repos), **leaving the shared
  `_shared/active_set.py` glossary and yf-beads-hygiene reconcile semantics untouched**; add a
  tagged test. No shared-classifier mutation, so no follow-on-hoist blast radius.

## Epics

### Epic 1: yf-beads-init 1.1.0 certification (EXP-001 concluded)
- Issue 1.1: SPEC — record the 1.1.0 embedded-repair requirement in yf-beads-init SPEC.md (escape hatch = `bd dolt commit` → `bd migrate`; false-negative invariant re-affirmed; `bd migrate schema`-still-fails note retained)
- Issue 1.2: SKILL.md — replace raw `dolt add -A && dolt commit` embedded hatch with `bd dolt commit` → `bd migrate`; correct the false "`bd vc commit` cannot open the wedged DB" warning; add the local-only remote-migrate-gate note
  - depends-on: 1.1
- Issue 1.3: Validate the revised repair path end-to-end via TESTING.md Tier-2 mechanical drive under a sandboxed HOME (embedded wedged fixture), not the installed copy
  - depends-on: 1.2

### Epic 2: Version-pin sweep (all skills)
- Issue 2.1: SPEC — update prerequisite specs (yf-plan, yf-research, yf-beads-extra) pinning the 1.0.5 floor to 1.1.0; correct the stale `MIN_BD_VERSION`/`_parse_bd_version()` prose in `spec/prerequisites.md` (constants no longer exist in the managers)
- Issue 2.2: Bump the pins that exist — frontmatter `min-bd-version` (yf-plan/yf-research/yf-beads-init/yf-beads-upstream), READMEs, banners, spec floors. No runtime floor added.
  - depends-on: 2.1

### Epic 3: yf-beads-extra false-text corrections
- Issue 3.1: SPEC — note 1.1.0 verification in yf-beads-extra SPEC.md
- Issue 3.2: Bump banner + annotate retired `child_counters` failure mode in SKILL.md/README
  - depends-on: 3.1

### Epic 4: Local-only remote-hygiene automation (#61 req 1–3)
- Issue 4.1: SPEC — requirements for two-layer `--remove-remote`, corrected instruction string, and the canonicalization-clears-the-gate contract (override stays operator-gated, never auto-run)
- Issue 4.2: **Micro-experiment (load-bearing, runs before the impl)** — confirm remove-remote-alone (drop `sync.remote` + `bd dolt remote remove`, git origin left intact) clears the 1.1.0 remote-migrate gate, i.e. the `BD_ALLOW_REMOTE_MIGRATE` override is **not** needed for a local-only repo. Records the definitive git-remote-vs-Dolt-remote disambiguation. If remove-remote-alone does **not** suffice, 4.3's design + SC-3 are revised before implementation.
  - depends-on: 4.1
- Issue 4.3: Implement — fix instruction string (`--local-only --remove-remote`) + make `--remove-remote` drop both config (`sync.remote`) and Dolt-DB (`bd dolt remote remove`) layers in one invocation
  - depends-on: 4.2
- Issue 4.4: Docs — three-mechanism disambiguation table (`git push` / `bd dolt push` / `gh` mirror) + document `BD_ALLOW_REMOTE_MIGRATE` as an operator-gated escape hatch only when a remote is intentionally retained
  - depends-on: 4.2

### Epic 5: yf-beads-upstream trigger + enumerate fix (#61 req 2-bonus)
- Issue 5.1: SPEC — localized enumerate knob (owner-on-create repos) + mid-session upstream-intent trigger requirement; explicitly records the shared plan-013 glossary is unchanged
- Issue 5.2: Fix enumerate in `upstream.py` via a localized config knob (option b); add tagged test; leave `_shared/active_set.py` and hygiene reconcile untouched
  - depends-on: 5.1
- Issue 5.3: Add mid-session "push/sync upstream" intent triggers disambiguated from `bd dolt push`
  - depends-on: 5.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

_(EXP-001 concluded during planning — VERDICT A — so no capability gate blocks execution.)_

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step
- **Per-issue upstream closure (decouples #68 from #61).** #68 (Epics 1–3) and #61 (Epics 4–5)
  are reconciled and closed as **independent upstream issues** as their epic sets complete;
  finished #68 certification is not held hostage to Epic 5. The auto gate governs the plan-level
  reconcile step, not per-issue closure order.

## Risks & Mitigations

- **Localized-knob correctness (Epic 5).** The enumerate fix is confined to `upstream.py` and
  must not silently alter the shared classifier. *Mitigation:* tagged test asserts enumerate
  returns candidates in an owner-on-create repo **and** that `_shared/active_set.py` /
  hygiene-reconcile behavior is byte-for-byte unchanged (DRIFT-CHECK edges stay green).
- **Embedded fixture fidelity (EXP-001) — resolved.** VERDICT A was reached against a *genuine*
  wedged embedded fixture (from-source bd 1.0.5 DB reopened by 1.1.0 with real pending migrations
  0050–0053), not a mock. Residual: the `bd dolt commit` bypass is 1.1.0-only, so Epic 1 keeps
  the raw-dolt path as the bd<1.1.0 fallback rather than dropping it.
- **Installed-copy staleness.** The installed skills are rust-embed-baked old copies; testing
  must drive the modified in-repo skill under a sandboxed HOME (TESTING.md). *Mitigation:*
  follow TESTING.md Tier-2 mechanical drive; never trust the installed copy.
- **No runtime version floor.** Pins stay documentary (Epic 1 keeps the bd<1.1.0 path), so a
  1.1.0-only instruction must never be the *only* branch. *Mitigation:* Epic 1's version-branched
  hatch; Epic 2 adds no hard floor.
- **Epic 4 premise is load-bearing on the micro-experiment.** "Canonicalization clears the gate"
  is unproven until Issue 4.2 runs; the impl (4.3) and SC-3 assume it. *Mitigation:* 4.3/4.4
  `depends-on: 4.2`; if remove-remote-alone does not suffice, 4.2 forces a design revision before
  implementation (the operator-gated override stays documented as the fallback either way).

## Success Criteria

1. EXP-001 concluded and recorded (VERDICT A); yf-beads-init SKILL.md gives `bd dolt commit` →
   `bd migrate` as the bd≥1.1.0 path with the raw-dolt bd<1.1.0 fallback retained, and the
   "`bd vc commit` cannot open the wedged DB" claim corrected to version-conditional — no text
   left false on 1.1.0.
2. No `1.0.5` pin/banner/spec-floor remains **under `skills/`** (verified by a grep scoped to
   `skills/` with historical annotations — this plan, EXP-001 notes, "fixed in 1.1.0" text —
   allow-listed).
3. `yf doctor --repair --local-only --remove-remote` emits the working command and fully clears
   both remote layers (config + Dolt-DB) in one invocation; the micro-experiment confirms
   remove-remote-alone clears the 1.1.0 gate.
4. yf-beads-upstream `enumerate` returns genuine parked follow-ups in an owner-on-create repo
   (tagged test passes); `_shared/active_set.py` and hygiene-reconcile behavior verified
   unchanged.
5. Mid-session "push/sync upstream" phrasing routes to yf-beads-upstream (documented
   trigger-string table + Tier-2 mechanical drive), disambiguated from `bd dolt push`;
   three-mechanism table present.
6. All changes SPEC-first; coverage gate green; DRIFT-CHECK edges green.

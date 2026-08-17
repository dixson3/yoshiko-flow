---
type: Plan
okf_spec: OKF-PLAN
id: plan-042-james-dixson-98631b
author: james-dixson
created: '2026-08-16'
status: reconciling
deliverable_class: standard
fingerprint: ab2fcfbcbbdbff8e244641c43ccfac430dac471b7806950aa2619f7e79280468
epic: yf-mol-7n9
---
# Plan: Install-time sync for `yf self install` and `yf self update`

**ID:** plan-042-james-dixson-98631b
**Author:** james-dixson
**Created:** 2026-08-16
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-7n9
**Fingerprint:** ab2fcfbcbbdbff8e244641c43ccfac430dac471b7806950aa2619f7e79280468

## Objective

Make a `yf` install leave the machine's **deployed** surface — skills, the rules aggregate,
and harness config — matching the binary it just promoted, on both the developer path
(`yf self install --from-build`) and the end-user path (`yf self update`), **without
silently escalating a user's security posture**.

Today the operator must run three commands and remember the order. The gap is **asymmetric** —
neither path closes it, and they fail differently:

| Path | Skills | Rules aggregate | Harness config |
| :-- | :-: | :-: | :-: |
| `yf self update` (end user) | yes | yes | **no** |
| `yf self install --from-build` (dev) | **no** | **no** | **no** |

So a single undifferentiated "both do the full sync" requirement would be untestable — which is
why D-A requires the SPEC amendment to name the two commands separately.

## Motivation

`AGENTS.md` documents a three-step land-the-plane ritual (`self install` →
`skills install` → `harness tune`) whose steps 2 and 3 are silently optional: nothing
warns when they are skipped, and the promoted binary and the deployed surface then
disagree indefinitely. Because this repo is both the source and a consumer of its own
skills, a missed step means a fix is believed landed while the deployed copy is unchanged.

**Split from plan-041** (its pass-1 red-team, concern C10). plan-041 fixes the #137 stale
**embed**; this plan fixes the stale **deployment**. They are independent: the red-team
established the sync has zero technical dependency on the embed fix, while carrying an
entire security-consent surface, 3 of 5 SPEC amendments, and ~7 of 19 issues. Holding a
two-line measured build fix behind a security-bearing behavior change served neither.

**A sync is not a substitute for plan-041** (former decision D7): a stale binary faithfully
syncing its own stale skills is still stale — and now silently *and automatically*. The
sync **amplifies** an unfixed embed rather than masking it. plan-041 should land first.

## Scope

**In scope**

- `yf self install --from-build` and `yf self update` — two distinct commands sharing no
  code path today; the sync logic is factored so they share one.
- `REQ-YF-SELF-005` (currently *"A from-build install shall NOT auto-refresh"*) and
  `REQ-YF-TUNE-023` (*"install and tune stay separable"*), plus a new `REQ-YF-SELF-*` for
  the opt-out and the config-delta report. **SPEC-first**: both currently **forbid** this
  plan's deliverable and must be amended before any code.
- The consent boundary between the sync's two halves (the split is D-C1; the predicate that
  classifies a change as consent-requiring is **D-R**).
- The composite tune-idempotence test (D-G).
- `CI`/non-interactive suppression of the config half (D-H) and the `--no-sync` flag (D-J).

**Out of scope**

- The embed / version-stamp fix — that is **plan-041**.
- Implementing harness auto-detection *inside* `tune` itself (the aspirational
  `harness/mod.rs:84-94` comment). The sync passes explicit `--harness` per detected
  harness instead.
- Changing `skills install` / `harness tune` behavior beyond what the sync requires.
- **The `YOSHIKO_FLOW.md` wholesale-regeneration hazard (D-I)** — no managed block, no checksum
  guard, and `--revert` deletes the aggregate rather than restoring pre-tune content. **Filed as
  [#154](https://github.com/dixson3/yoshiko-flow/issues/154)**; referenced from this plan's risks,
  not absorbed.

## Decisions carried from plan-041

These were taken during plan-041's scoping and its pass-1 review, on evidence in findings
E1 and E4 (produced in plan-041, cited here). They are **inherited, not re-litigated** —
but they are scoping inputs, not an approved design.

| # | Decision | Source |
| :-- | :-- | :-- |
| D-A | **`yf self install` is from-build only.** A bare `yf self install` refuses with exit 1 before touching the filesystem; the end-user command is **`yf self update`**. The SPEC amendment must name the two commands **separately** and specify all three sub-operations per command — an undifferentiated "both do the full sync" requirement is untestable because the two start from different states. | E1 (was D4) |
| D-B | **Exec the freshly promoted binary; never call the deploy logic in-process.** The running binary is precisely the one that may carry a stale embed. `self update`'s `refresh_user_skills` already does this; its doc comment says exec'ing the new binary *"is what makes the new embed take effect"*. | E1 + E4 (was D6) |
| ~~D-C1~~ | **PREDICATE SUPERSEDED BY D-R** (pass-2 H1) — the *split* survives and is still in force; only the `permissions.*` key-path test is replaced by the profile-declared `consent_required` flag. Original text retained below. ~~Split the sync halves by default (consent).~~ Skills + rules aggregate — idempotent, yf-owned, no security semantics — auto-sync. Harness **config** alignment applies automatically only when a settings file **already exists** and the delta touches no `permissions.*` key. When tune would *create* `settings.json` or write a `permissions.*` key, print the delta and require `--yes`, reusing `install.rs:304-331`'s existing `confirmation_required` shape rather than inventing a weaker one. | pass-1 C1 (supersedes the former D8) |
| D-D | **Only tune already-present harnesses** — reuse `harness_detect` / `present_user_surfaces` and pass an explicit `--harness <id>` each. Never fall through to tune's hard-coded `claude-code` default, which writes `~/.claude/` whether or not Claude Code is installed. | E4 (was D8) |
| D-E | **Sync on by default; `--no-sync` opts out** — mirroring the existing, tested `self update --binary-only`. **The opt-out and the delta report must land as part of, or before, the wiring — never trailing it** (pass-1 C8). | E4 + pass-1 C8 (was D9) |
| D-F | **Amend `REQ-YF-TUNE-023` honestly** (pass-1 C9). The former framing — that explicit per-harness flags convert a SPEC conflict into a "SPEC-compliant call shape" — is loophole-lawyering: the prohibited *outcome* (unconfirmed multi-harness writes) still occurs. State plainly that the sync path may write to detected harnesses without per-run confirmation, and name the compensating controls. | pass-1 C9 |
| D-G | **Add the composite tune-idempotence test.** All four sub-ops are individually proven byte-stable (97 harness tests pass), but no test runs the whole `harness tune` command twice asserting byte-identity across surfaces. The sync makes tune run far more often. | E4 (was D10) |

## Decisions taken at scoping (this plan)

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-H | **Suppress the CONFIG half under `CI`/non-interactive; still sync skills + rules.** | Reuses the existing `REQ-YF-SELF-006` precedent. Composes with D-C1: the `--yes` gate can never be satisfied non-interactively, so without suppression the sync would either hang or hard-fail in CI. Skills and the rules aggregate are idempotent and carry no security posture, so they remain safe to deploy there. |
| D-I | **The `YOSHIKO_FLOW.md` wholesale-regeneration hazard is OUT OF SCOPE** — filed separately and referenced from this plan's risks. | This plan raises the hazard's *frequency* but does not create it: wholesale regeneration is existing `tune` behavior. Fixing it properly means designing a managed-block or checksum guard for the aggregate, which is its own piece of work. Absorbing it would widen scope into `tune`'s internals — the failure mode that split plan-041. |
| D-J | **`--no-sync` on both commands; `--binary-only` retained as a documented alias on `self update`.** | `--no-sync` names what the flag now does, since the sync covers skills + rules + config rather than just the binary. Keeping the alias avoids breaking existing usage and `REQ-YF-SELF-005`'s current language. |
| D-L | **The sync execs `harness skills install --tune`, one exec per detected harness with an explicit `--harness`.** Not `skills upgrade`. | E5, five measured grounds. Decisive: `upgrade` is **single-destination** (silently drops every harness after the first) and writes the rules aggregate to the **skills-sibling** dir — the wrong surface for every harness but claude-code, producing an orphan absent from the tune manifest that `--revert` cannot reverse. That write is backed by **no REQ** and contradicts `REQ-YF-FLOW-007`. `upgrade` also silently swallows `--tune`. The explicit per-harness `--harness` additionally bypasses the fan-out gate by construction. |
| D-M | **Any `tune.status` other than `ok` MUST be treated as a caller-side failure** — `confirmation_required` **and `refused`** (widened at pass-1 C6; the malformed-settings fail-safe path also returns `Ok(())`). | E5 defect A, measured: `install --tune --json` with no `--harness` writes **no rules and no config** and still **exits 0**. An auto-sync shelling out to a bare `install --tune` would appear to succeed while deploying only skill bodies — the same false-success shape as #136. |
| D-N | **D-C1's consent gate gets its own flag** (e.g. `--allow-permissions-write`); `--yes` keeps its existing "bypass multi-harness fan-out" meaning. | E5 defect B. Two gates that authorize genuinely different things must not share one token — an operator passing `--yes` to silence a fan-out prompt would otherwise silently authorize a `bypassPermissions` write. |
| D-O | **"Already present" (D-D) means an existing config HOME DIRECTORY**, not a binary on `PATH`. | E5 defect C: `detect_from_env` (`REQ-YF-INSTALL-009`) counts a binary on `PATH`, which is broader than D-D's plain reading. A machine with the `codex` binary but no `~/.codex/` has never been configured; creating one as a side effect of a binary promote is exactly the surprise D-C1 exists to prevent. **The sync therefore needs its own home-dir presence check rather than reusing `effective_harnesses` unchanged.** |
| D-Q | **Build a rules-only tune mode**, and have the Epic-2 exec use it until Epic 3's consent gate exists. | pass-1 C1: the Epic 2/3 seam this plan's Approach claims **does not exist in the code** — `tune_one_harness_at` unconditionally runs both sub-operations, and there is no `--rules-only`/`config_only` anywhere (verified). Without this, Epic 2 as written would ship an unconsented `bypassPermissions` write, and the "two independently shippable halves" framing would be false. Also resolves D-H's contradiction (pass-1 C9). |
| D-R | **Consent is PROFILE-DECLARED, not key-path-matched.** Add `consent_required: true` to the offending profile **entries** and test the computed change set against it. This **supersedes D-C1's `permissions.*` predicate.** | pass-1 C4. The syntactic predicate is claude-code-specific: codex's lever is `approval_policy = "never"`, opencode's is `permission.*` (singular) `= "allow"` — neither matches `permissions.*`, so on those harnesses the gate's "file exists AND no `permissions.*` key" branch auto-applied a blanket-allow with **no consent**. The profiles' own rationale text already calls both *"the analog of claude-code's bypassPermissions"*, so the codebase knew they were the same class and the predicate did not. Declaring it per-entry is self-maintaining: a new lever declares its own requirement instead of relying on a prefix that only ever matched one harness. |
| ~~D-P~~ | **`--prune` MOVED OUT of this plan** (pass-1 C10) — filed as [#155](https://github.com/dixson3/yoshiko-flow/issues/155). **Note the issue count did not fall** (pass-2 M4): removing prune dropped 2 issues, D-Q added 2 back, and D-R's SPEC+implementation added 2 more — 22 → **25** (pass-2 M4 said 24; Issue 3.8 was added for pass-2 M1 after that count was written — pass-3 C3). The plan is not smaller; it is differently composed. That is defensible because D-Q and D-R are load-bearing *safety* work surfaced by review, not creep — but the honest statement is "scope held while its composition improved", not "scope shrank". | Genuinely orthogonal to the sync: its own REQ amendment (`REQ-YF-MARK-004`), and its only tie-in was one appended flag. Removing it drops 2 issues and a SPEC amendment without touching the sync's logic. The permanent-`modified` defect it fixes is real and recorded upstream. Issue numbers 0.3 and 2.1 are **reused** for the D-Q rules-only work rather than left as gaps, so the `1.3 → 2.1` edge survives. |
| ~~D-P (original)~~ | ~~Give `install` an opt-in `--prune`~~ and use it in the sync. SPEC-first: amend `REQ-YF-MARK-004` (or add a REQ) before the code. | E5: prune is `upgrade`'s only unique asset, and its blast radius is measured **narrow** — hand-added skill dirs and stray root files survive; only files placed *inside* a yf skill dir are removed. Its real benefit is not cosmetic: without it, a file dropped from a still-shipping skill lingers and `skill_health.unmodified` re-hashes the whole tree (`REQ-YF-MARK-003`), so that skill reports `modified` **permanently** in `doctor`/`status`. One-line change plus a flag; the engine already supports it. |
| D-K | **E1 and E4 are carried into this bundle in full**, not referenced across bundles. | Resolves the portability gap plan-041's pass-2 flagged (M-d). Both experiments measured *this* plan's subject; a cold reader of plan-042 must not need plan-041's folder. Originals remain in plan-041 with provenance noted in each carried copy. |

## Open questions remaining

**None.** All five scoping questions are resolved (D-H, D-I, D-J, D-K, and D-L…D-O from E5; D-P was
subsequently struck and moved to #155, and D-Q/D-R were added at pass-1 review).
Ready to draft.

## Incidental gap this plan closes

**`yf self update` currently cannot refresh codex, opencode or pi at all** (E5 defect D). Its
`refresh_user_skills` emits `--surface`, a deprecated alias spanning only two values
(`Claude`, `Agents`), and `present_user_surfaces` probes only `~/.claude` and `~/.agents`.
Three of the five supported harnesses have never been reachable from the vendor path. Moving to
`--harness` reaches the full descriptor table and drops a stderr deprecation warning from every
`yf self update` run. Not the plan's motivating defect, but a real one it fixes on the way.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#154](https://github.com/dixson3/yoshiko-flow/issues/154) | `yf harness tune` regenerates `YOSHIKO_FLOW.md` wholesale — no managed block, no guard, `--revert` deletes | exclude | Filed by this plan at scoping (D-I). This plan raises the hazard's **frequency** by automating `tune`, but does not create it — wholesale regeneration is existing behavior. Fixing it means designing a managed-block or checksum guard for the aggregate, which is its own work. Referenced from this plan's risks; **not** resolved here. | — |
| [#155](https://github.com/dixson3/yoshiko-flow/issues/155) | A file dropped from a skill lingers, so that skill reports `modified` forever — give install an opt-in `--prune` | exclude | **Split out of this plan at pass-1 review (C10).** Was decision D-P; removed because it is orthogonal to the sync, carries its own `REQ-YF-MARK-004` amendment, and its only tie-in was one appended flag. The defect is real and measured; it is simply not this plan's. | — |
| [#156](https://github.com/dixson3/yoshiko-flow/issues/156) | `skills upgrade` writes `YOSHIKO_FLOW.md` to the wrong surface for non-claude-code harnesses | exclude | Filed at pass-1 review (upstream-assessment gap). This plan **routes around** the defect by exec'ing `install --tune` instead of `upgrade` — but `upgrade` stays a public verb that will keep producing unmanaged orphans. Routing around is not fixing, so it is recorded rather than absorbed. | — |
| [#157](https://github.com/dixson3/yoshiko-flow/issues/157) | **plan-042 execution tracking** (the coarse tracker) | tracker | Filed at intake (Phase 4.5) per the `AGENTS.md` one-issue-per-plan-scale-effort convention. The sync was previously invisible upstream, riding under #137 — a bug report about a stale build that never asked for a sync. Stamped onto the epic as `external_ref` at pour so `upstream.py closable` can see it. | — |

## Investigation Findings

### E1 — What the install commands actually do ([finding](findings/exp-001-self-install-paths.md))

Carried from plan-041 in full (D-K). **`yf self install` is from-build only** — a bare
invocation refuses with exit 1 before touching the filesystem; the end-user command is
**`yf self update`**, and the two share no code path. **`harness tune` runs on neither**
(zero grep matches across all 10 files of `self_cmd/`). But "no tune" is not "no rules": the
vendor path's refresh execs `skills upgrade`, which writes the rules aggregate. The measured
gap is therefore **asymmetric** (see Objective's table). No embedded↔repo-source comparator
exists to reuse, and `--tune` can block on stdin.

### E4 — Is `harness tune` safe to auto-invoke ([finding](findings/exp-004-harness-tune-safety.md))

Carried from plan-041 in full (D-K). **Safe on every axis I worried about**: fully
non-interactive and cannot hang; preserves operator config values, hook blocks, comments and
unknown keys; fail-safe refusal on malformed files; real `--dry-run`/`--revert`; 97 harness
tests pass. **Not safe on three**: the claude-code profile applies
`permissions.defaultMode: "bypassPermissions"` and `skipDangerousModePermissionPrompt: true`,
**creating** `settings.json` where none exists; the tune path performs **no harness detection**
(hard-coded `["claude-code"]`); and `REQ-YF-SELF-005` + `REQ-YF-TUNE-023` currently **forbid**
this plan's deliverable. Those three findings are what D-C1, D-D and Epic 0 exist to answer.

### E5 — Which verb the sync execs ([finding](findings/exp-005-upgrade-vs-install.md))

Produced in this bundle. **`install --tune`, not `upgrade`** (D-L), on five measured grounds —
decisively: `upgrade` is **single-destination** (silently drops every harness after the first)
and writes the aggregate to the **skills-sibling** dir, the wrong surface for every harness but
claude-code, leaving an orphan absent from the tune manifest that `--revert` cannot reverse.
That write is backed by **no REQ** and contradicts `REQ-YF-FLOW-007`.

Three defects and one gap fell out: **the confirmation trap** (D-M — `install --tune --json`
without `--harness` writes nothing and **exits 0**); **the `--yes` collision** (D-N); **D-D's
"present" being broader than intended** (D-O); and the incidental gap above. Prune's blast
radius is measured **narrow** but its benefit real (D-P). Ordering is **free** — tune reads
from the binary's embedded tree, confirmed byte-identical output in a virgin directory with
zero skills deployed. `install --tune` is **byte-level idempotent** across 234 files.

## Approach

**Four epics, SPEC-first, sequenced so the two halves of the sync can land independently.**

The sync has a **safe half** (skills + rules aggregate — idempotent, yf-owned, no security
semantics) and a **consent-bearing half** (harness config alignment, which can write
`bypassPermissions`). D-C1 already splits them by default. The epics follow that seam: Epic 2
lands the safe half end-to-end, Epic 3 adds the consent-gated half on top. **If Epic 3 slips,
Epic 2 still closes the real gap** — the developer path currently deploys *nothing*.

**Why one shared implementation.** The two commands start from different states (E1's table),
but converging them on one factored routine is the point: two copies would drift, and the
vendor path's copy is already the one carrying the `--surface` blindness. Epic 1 factors first,
with no behavior change, so the behavior change that follows has a clean diff.

**The exec contract** (D-L, D-M), per detected harness `H`, from the promoted binary at its
**captured install path** — never a post-swap `current_exe()`:

```
<promoted> harness skills install --scope user --harness <H> --tune \
           [--rules-only | --allow-permissions-write] --json
```

`--rules-only` is the Epic-2 form (safe half); the consent flag replaces it once Epic 3's gate
exists. **`--prune` is no longer part of this plan** — see D-P.

## Epics

### Epic 0: SPEC-first — the requirements this plan needs

**Two** requirements currently **forbid** the deliverable (`REQ-YF-SELF-005`,
`REQ-YF-TUNE-023`), one **under-describes** the profile schema it needs
(`REQ-YF-TUNE-001`), and two are **new** (rules-only, sync-contract). All land before code.

- Issue 0.1: Amend **`REQ-YF-SELF-005`** — replace *"A from-build install shall NOT
  auto-refresh"* with the sync contract. Must name `yf self install --from-build` and
  `yf self update` **separately** and specify all three sub-operations (skills, rules
  aggregate, harness config) per command, because the two start from different states (E1).
  Preserve the existing fail-soft and exec-the-captured-path language.
- Issue 0.2: Amend **`REQ-YF-TUNE-023`** honestly. State plainly that the sync path may write
  to detected harnesses without a per-run fan-out prompt, and name the compensating controls
  (explicit per-harness selection, the D-N consent flag, `--no-sync`, the delta report). **Do
  not claim the separability prohibition is "preserved intact"** — the sync is a named
  exception to it.
  - depends-on: 0.1
- Issue 0.3: Add a REQ for a **rules-only tune mode** (D-Q), and record it as a **named
  exception to `REQ-YF-TUNE-012`**, which states tune *"shall own **two** sub-operations per
  harness… reporting a per-harness verdict covering both"* (pass-2 H2). `tune_one_harness_at`
  unconditionally runs *both* the config and rules sub-operations, so "deploy rules without
  config" is currently unreachable by any verb — which is what makes the Epic 2/3 seam real
  rather than asserted (pass-1 C1).
  - depends-on: 0.1
- Issue 0.4: Add a new `REQ-YF-SELF-*` for the **sync contract surface**: `--no-sync` on both
  commands with `--binary-only` retained as a documented alias (D-J); the D-N consent flag;
  `CI` suppression of the config half (D-H); and **the caller's obligation to treat
  `tune.status == "confirmation_required"` as a failure** (D-M).
  - depends-on: 0.2, 0.3
- Issue 0.6: Amend **`REQ-YF-TUNE-001`** so a profile entry may carry an optional
  **`consent_required` boolean (default false)** (D-R). Required because that REQ enumerates the
  entry schema **exhaustively** — *"Each profile entry shall carry: a JSON path…, a recommended
  value, a kind…, and a one-line rationale"* — so adding a fifth field is a schema change to a
  testable requirement, and SPEC-first makes it a prerequisite, not an implementation detail
  (pass-2 H2).
  - depends-on: 0.1
- Issue 0.5: Root `SPEC.md` amendment-log entry recording all of the above.
  - depends-on: 0.4, 0.6

### Epic 1: Factor the shared sync (no behavior change)

- Issue 1.1: Extract `refresh_user_skills` / `present_user_surfaces` / `upgrade_args` from
  `self_cmd/update.rs` into a shared module, switch `self update` over, and keep its existing
  tests green. **Pure refactor — no behavior change**, landed separately so the behavior change
  has a clean diff.
  - depends-on: 0.5
- Issue 1.2: Replace `--surface` with `--harness` in the shared routine and add the sync's own
  **presence predicate** (D-O) — **not** `effective_harnesses`, which counts a binary on `PATH`.
  Closes the incidental gap: codex, opencode and pi become reachable from the vendor path for
  the first time.

  **Define the predicate explicitly for all five ids** (pass-1 C5), stating which signal each
  uses. Two hazards the naive form has:
  - **Regression:** `harness_detect::PROBES` has four rows and **no `agents` row**, while the
    incumbent `present_user_surfaces` probes `~/.agents/{skills,rules}`. A config-home-only
    check would **stop refreshing** a machine with `~/.agents/skills` and no `~/.codex`.
  - **Over-broadening:** `present_user_surfaces` means *"yf already deployed here"*, but
    `~/.claude` exists on **every** Claude Code machine — so a config-home check would begin
    writing into `~/.claude` where yf was never installed at user scope.

  Ship a test pinning **both**: `~/.agents/skills` present with no `~/.codex` is still
  selected; and a harness with a binary on `PATH` but no home is **not**.
  - depends-on: 1.1
- Issue 1.3: Switch the routine's exec from `skills upgrade` to
  `harness skills install --harness <H> --tune --rules-only` (D-L + D-Q), and **treat any
  `tune.status` other than `ok` as a caller-side failure** (D-M, widened per pass-1 C6 to cover
  `refused` as well as `confirmation_required` — both return `Ok(())`). Add tests pinning
  **both** exit-0 false-success cases as failures.
  **Uses `--rules-only` until Epic 3 lands**, so this issue cannot ship an unconsented config
  write.
  - depends-on: 1.2, 2.1

### Epic 2: The safe half — skills + rules, both commands

- Issue 2.1: Implement the **rules-only tune mode** (D-Q) — a `--rules-only` flag on `tune`
  and/or a `config: false` parameter on `tune_bridge_at`, so the rules sub-operation can run
  without the config sub-operation. **This is what makes Epic 2 shippable without Epic 3**; it
  does not exist today (verified: no `rules_only` / `config_only` anywhere in `yf/src`).
  Include a test asserting a rules-only run writes the aggregate and **touches no config file**.
  - depends-on: 0.3
- Issue 2.2: Wire the shared routine into `yf self install --from-build`, exec'ing the
  **captured install path** (never `current_exe()`), **fail-soft in the sense `REQ-YF-SELF-005`
  already defines it**: reported with the manual re-run command, **exiting non-zero on the sync
  alone**, never rolling back the successful swap. **Fail-soft ≠ silent** (pass-1 C8) — an
  earlier draft omitted the non-zero exit, which implemented literally would have recreated the
  silent-divergence defect this plan exists to fix.
  - depends-on: 1.3, 2.3
- Issue 2.3: Add `--no-sync` to both commands with `--binary-only` as a documented alias on
  `self update` (D-J). **Lands with or before 2.2/1.3** — the opt-out must never trail the
  behavior it guards.
  - depends-on: 0.4
- Issue 2.4: Add `REQ`-tagged tests for the safe half under a **sandboxed `HOME`**: skills
  deployed, rules aggregate written once at the correct per-harness target, `--no-sync` writing
  none of it, and a second run byte-identical (E5 measured idempotence across 234 files).
  - depends-on: 2.2, 2.3

### Epic 3: The consent-bearing half — harness config

- Issue 3.0: Set `consent_required: true` on the four offending profile entries (D-R) —
  `claude-code.json`: `permissions.defaultMode` and `skipDangerousModePermissionPrompt`;
  `codex.json`: `approval_policy`; `opencode.json`: `permission.*`. All four verified present at
  those paths. Without this, Issue 3.1 consumes a field nobody creates (pass-2 H2).
  - depends-on: 0.6
- Issue 3.1: Implement the consent gate — the **D-C1 split** with the **D-R predicate**. Config
  alignment applies automatically **only** when the config file already exists **and the
  computed change set contains no entry declaring `consent_required: true`**. Otherwise print
  the delta and require the D-N flag. Reuse `install.rs`'s existing `confirmation_required`
  shape rather than inventing a weaker one.
  **Do NOT use a `permissions.*` key-path test** (pass-2 H1): that predicate is claude-code-only
  and would auto-apply codex's `approval_policy = "never"` and opencode's `permission.* =
  "allow"` with no consent. Key on `read_settings`'s classification, not `path.exists()`.
  - depends-on: 0.4, 3.0
- Issue 3.2: Add the **D-N consent flag** (`--allow-permissions-write` or as named in 0.4),
  distinct from `--yes`, whose existing fan-out-bypass meaning is preserved unchanged.
  - depends-on: 3.1
- Issue 3.3: Suppress the config half under `CI`/non-interactive (D-H), reusing the
  `REQ-YF-SELF-006` precedent. Skills + rules still sync — **implemented by emitting
  `--rules-only` (D-Q), not by a second suppression mechanism**, which is why it depends on the
  rules-only implementation and not merely on its REQ (pass-2 M3).
  - depends-on: 3.1, 2.1
- Issue 3.4: Surface the **config delta** in the report using **`config_json`'s `changes`
  array over `merge::Change`** — *not* `plan_targets`/`target_plan_json`, which emit only
  `{harness, config_path, rules_path}`, i.e. the blast radius rather than the change set
  (pass-1 C7). Note this requires a **dry-run pass before the real one**; `record_manifest` is
  dry-run-guarded, so that is safe. So `bypassPermissions` is never applied invisibly.
  - depends-on: 3.1
- Issue 3.5: Add the **composite tune-idempotence test** (D-G) — sandboxed `HOME`, run
  `harness tune` twice, assert every surface byte-identical. All four sub-ops are individually
  proven byte-stable; the whole command is not, and the sync makes it run far more often.
  - depends-on: 3.1
- Issue 3.8: **Flip the sync's exec off `--rules-only`** to the consent-gated full tune. This
  is the single issue that can ship a config write, and the only one the Capability Gate blocks.
  Isolating the flip to one line in one issue is what keeps Epic 2 landable on its own.
  - depends-on: 3.1, 3.2, 3.3, 3.4
- Issue 3.6: Add the `REQ`-tagged **consent-gate** test module (`consent_gate`), covering **all
  three config-bearing profiles** — claude-code, codex, opencode (pi and `agents` ship none):
  a fresh machine with no config file **requires** the D-N flag; an existing config file whose
  change set declares **no** `consent_required` entry does **not**; a change set that **does**
  declare one requires the flag **on every one of the three profiles**; and `--yes` alone never
  authorizes it. **Depends only on 3.1/3.2** — this is the Capability Gate's evidence, so it must not
  depend on anything the gate blocks.
  - depends-on: 3.2
- Issue 3.7: Add `REQ`-tagged tests for the **surrounding behavior**: `CI` suppresses the config
  half while skills and rules still deploy (3.3), and the config delta appears in the report
  (3.4). Split from 3.6 so the gate's condition stays reachable.
  - depends-on: 3.3, 3.4

### Epic 4: Documentation + upstream

- Issue 4.1: Rewrite `AGENTS.md`'s sync section — the three-step ritual collapses to one
  command. **This is the half plan-041 deliberately left intact**; it becomes correct only now.
  - depends-on: 2.4, 3.7
- Issue 4.2: Update `CHANGE-VALIDATION.md` — new tests into **both** fast and full tiers.
  - depends-on: 2.4, 3.7
- Issue 4.3: File the incidental-gap finding upstream: `yf self update` could never refresh
  codex, opencode or pi. Worth its own record even though this plan fixes it. (The two other
  review-surfaced defects, [#155](https://github.com/dixson3/yoshiko-flow/issues/155) and
  [#156](https://github.com/dixson3/yoshiko-flow/issues/156), were filed at scoping/review.)
  - depends-on: 1.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: the consent gate exists before any auto-tune ships
- Type: auto
- Condition: the consent gate (D-C1 split + **D-R predicate** + D-N flag) is implemented and its
  tests pass — on **each** of the three config-bearing profiles, a change set declaring a
  `consent_required` entry **requires** the explicit flag, and a fresh machine with no config
  file requires it before the file is created.
- Test: the filter must be proven **non-empty before it is trusted** (pass-1 C3) —
  ```bash
  N=$(cargo test -p yf consent_gate -- --list | grep -c ': test$')
  echo "consent_gate tests found: $N"          # a compile failure shows as N=0; echo it
  [ "$N" -ge 6 ] && cargo test -p yf consent_gate
  ```
  Verified today: `cargo test -p yf consent_gate` prints `running 0 tests … 0 passed; 4
  filtered out` and **exits 0**. A name filter matching nothing is a pass — the exact
  exit-0-means-nothing shape R1 defends against, reproduced inside the gate guarding this
  plan's most dangerous edge. Issue 3.6 must name its module `consent_gate` and cover all
  three config-bearing profiles. **The count is a floor against the empty-filter trap, not a
  coverage measure** — 3.6 specifies four scenario classes, one of which must hold on each of
  three profiles, so a faithful implementation is ≥ 6 tests (pass-3 C2). Profile coverage is
  verified by reading the module, not by the count.
- Blocks: Issue 3.8, Issue 3.3, Issue 4.1
- Instructions: This is the plan's one genuinely dangerous edge. Auto-tuning writes
  `permissions.defaultMode: "bypassPermissions"` and `skipDangerousModePermissionPrompt: true`
  into a file it may **create** — as a side effect of promoting a binary. The same class of
  lever exists on codex (`approval_policy = "never"`) and opencode (`permission.* = "allow"`),
  which is why the predicate is profile-declared (D-R) rather than key-path-matched. Nothing that ships or
  documents the auto-tune path may land until the gate that makes it safe is proven by test.
  It blocks **Issue 3.8** — the single issue that flips the exec off `--rules-only` and is
  therefore the only thing that can ship a config write — plus 3.3 (CI suppression) and 4.1
  (docs), which would *advertise* the path. Issues 1.3 and **2.2** are **not** blocked, because
  D-Q makes them emit `--rules-only`: neither can write config, so gating them would buy nothing
  and would falsify the Epic-2-independence claim (pass-2 M1; pass-1 C2 is preserved — the
  *shipping* issue is gated, it is just 3.8 rather than 2.2).
  The gate does not block its own implementation (3.1/3.2) nor its evidence (3.6), which
  depends **only** on 3.1/3.2. Issue **3.7** carries the tests that do
  depend on 3.3, and is deliberately split out of 3.6 for exactly this reason: an earlier draft
  had the gate's evidence depending on an issue the gate blocked, which deadlocked it.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The sync silently deploys no RULES OR CONFIG and exits 0** (skill *bodies* are written first — pass-1 C11) — E5 measured `install --tune --json` without `--harness` returning `confirmation_required`, writing no rules and no config, exit code 0. | **High** | D-M makes this a caller-side failure, Issue 1.3 pins it with a test, and the sync always passes an explicit `--harness`, which bypasses the gate by construction. Three independent defenses because this is the same false-success shape as #136. |
| R2 | **A `bypassPermissions` write reaches a machine that never consented.** | **High** | D-C1's gate (Issue 3.1) + the distinct D-N flag (3.2) + the delta report (3.4) + `--no-sync` (2.3) + `CI` suppression (3.3), and the Capability Gate blocks anything that ships or documents the path until the gate is test-proven. |
| R3 | **D-O requires a home-dir check the codebase does not have.** Reusing `effective_harnesses` would silently reintroduce the PATH-based breadth D-O rejects. | Medium | Issue 1.2 owns the new check explicitly and must **not** delegate to `effective_harnesses`. Worth a test asserting a harness with a binary on `PATH` but no home dir is **not** selected. |
| ~~R4~~ | **MOVED to [#155](https://github.com/dixson3/yoshiko-flow/issues/155)** with `--prune` (pass-2 M2). The row survived the D-P split and still pointed its mitigation at Issue 2.1, which is now the rules-only mode — an executor would have added prune tests to it. | — | Listed so the R-numbering gap reads as a relocation. |
| R5 | **Epic 3 slips and the plan ships half a sync.** | Low | Seam is now **real**, not asserted: D-Q's rules-only mode (Issue 2.1) is what makes Epic 2 landable without a config write, and the Capability Gate blocks **Issue 3.8** — the single issue that flips the exec off `--rules-only` — until the consent gate is test-proven. *At pass-1 this risk was **false and its severity inverted** — no rules-only mode existed, so Epic 2 would have shipped an unconsented `bypassPermissions` write.* |
| R8 | **The sync writes to a surface the operator never yf-installed.** `~/.claude` exists on every Claude Code machine, so a config-home presence check is broader than the incumbent "yf already deployed here" signal. | Medium | Issue 1.2 must define the predicate per-harness and ship a test for the over-broadening case. Unmitigated until it does — this is a *new* surface the sync would touch, not an existing one it touches more often. |
| R9 | **There is no safe rollback after an unwanted auto-tune.** `tune --revert` exists, but per #154 it **deletes** the aggregate rather than restoring pre-tune content, and #154 is out of scope. | Medium | The consent gate is therefore the *primary* control, not a backstop — which is why the Capability Gate now blocks the shipping issue. The **config** revert path (manifest-driven, per-key) is sound and untouched by #154; only the aggregate's is not. State this in the docs (4.1) rather than implying "just revert". |
| R6 | **The refactor (1.1) changes vendor-path behavior by accident**, breaking a shipped, tested command. | Low | 1.1 is a pure refactor landed separately with `self update`'s existing tests kept green; behavior changes begin at 1.2. |
| R7 | **`#154`'s hazard fires more often** — `YOSHIKO_FLOW.md` is regenerated wholesale on every sync now. | Low | Out of scope by D-I and filed as #154. The sync raises frequency, not severity, and the aggregate is byte-identical across writers (E5 measured sha1 agreement across three independent writers). |

## Success Criteria

1. **`yf self install --from-build` deploys skills, rules and (gated) config** for every
   harness with an existing config home. Verified by a sandboxed-`HOME` e2e asserting deployed
   `SKILL.md` marker tree-hashes equal `marker::embedded_tree_hash`, the aggregate exists at the
   correct per-harness target, and `--no-sync` writes none of it.
2. **`yf self update` does the same**, and both share one implementation — verified
   structurally: the extracted routine has exactly **one** definition in `yf/src`, by whatever
   name Issue 1.1 gives it (pass-1 C12 — pinning the current name would fail on a correct
   refactor that renames it).
3. **codex, opencode and pi are reachable from the vendor path** for the first time — a test
   asserts a harness beyond `claude`/`agents` is selected when its home dir exists. **And the
   `agents` id keeps working**: a machine with `~/.agents/skills` and no `~/.codex` is still
   refreshed (pass-1 C5/M-C — `harness_detect::PROBES` has no `agents` row, so this is a
   regression the naive predicate would introduce).
4. **A harness with a binary on `PATH` but no config home is NOT tuned** (D-O).
5. **No `consent_required` entry is applied, and no config file is created, without the
   explicit D-N flag** — tested on a fresh sandboxed `HOME` for **all three** config-bearing
   profiles (claude-code, codex, opencode), not just claude-code (D-R). `--yes` alone does
   **not** authorize it (D-N). The gate keys on `read_settings`'s classification, **not**
   `path.exists()` — a whitespace-only file classifies as `Absent` and must take the
   consent-required branch (pass-1 C12).
5a. **pi and `agents` ship no config profile**, so the config half is a documented no-op for
   them (pass-1 C12) — the test matrix covers three profiles, not five.
6. **`confirmation_required` is a failure, not a success** — a test drives the exit-0-writes-
   nothing case and asserts the sync reports failure.
7. **The config half is suppressed under `CI`** while skills and rules still deploy.
8. **A sync failure exits non-zero while the promoted binary remains in place** (C8).
9. **Re-running the sync is a byte-level no-op**, and `harness tune` run twice leaves every
   surface byte-identical (D-G).
10. **`AGENTS.md`'s three-step ritual is replaced by one command** — the half plan-041 left
   intact deliberately.
11. **SPEC leads implementation** — every requirement this plan touches is amended or added
    before the code that depends on it: **`REQ-YF-SELF-005`** (0.1), **`REQ-YF-TUNE-023`** (0.2),
    **`REQ-YF-TUNE-001`** (0.6, the `consent_required` schema field), the **rules-only REQ**
    (0.3, a named exception to `REQ-YF-TUNE-012`), and the **sync-contract REQ** (0.4).
    `REQ-YF-TUNE-023`'s amendment states the exception honestly rather than claiming
    preservation. *(`REQ-YF-MARK-004` was listed here at pass-1; it left with `--prune` to #155
    and this plan no longer amends it — pass-2 M2.)*

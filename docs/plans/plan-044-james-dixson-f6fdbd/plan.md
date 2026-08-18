---
type: Plan
okf_spec: OKF-PLAN
id: plan-044-james-dixson-f6fdbd
author: james-dixson
created: '2026-08-17'
status: executing
deliverable_class: standard
fingerprint: ccbc6e610dfed92ba0a3c67de917b31cc0849dfe08359abb648d6a7781d34f98
epic: yf-mol-6yh
---
# Plan: Retire the beads-integrity and deploy-path defect clusters (#159, #160, #154, #156, #155, #144, #142, #143)

**ID:** plan-044-james-dixson-f6fdbd
**Author:** james-dixson
**Created:** 2026-08-17
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-6yh
**Fingerprint:** ccbc6e610dfed92ba0a3c67de917b31cc0849dfe08359abb648d6a7781d34f98

## Objective

Retire three defect clusters that share one failure signature — **an operation that reports
success without verifying its own postcondition**:

- **Beads integrity** (#159, #160) — `yf doctor --repair --remove-remote` prints `ok` while the
  Dolt remote survives.
- **Deploy path** (#154, #156, #155) — `YOSHIKO_FLOW.md` has two writers, only one tracked;
  `--revert` deletes rather than restores; a dropped file pins a skill at `modified` forever.
- **Upstream reconcile** (#144, #142, #143) — 83% of `closable`'s output is noise, a bead stays
  open when its issue closes, and 14 plan bundles carry dangling `**Epic:**` refs that make
  `resume-scan` report a silent false success.

## Motivation

Each cluster is a **silent-success defect**: the operator is told the work happened, so the
failure is invisible until something downstream breaks. That is why these belong in one plan
rather than three — the shared remedy is *verify the postcondition and fail loud*, and each
cluster gets the same treatment on its own surface.

The trigger is plan-042. It made `yf harness tune` run on **every binary promote**, which raised
#154's hazard from "when the operator types `yf harness tune`" to "on every `yf self install`".
plan-042 explicitly declined to absorb the fix (its decision D-I) and filed #154 as the place it
belongs. Investigation then showed the deploy-path issues are not independent: **#156 must land
before #154**, because while `skills upgrade` still writes the same path, any managed-block or
guard added to `tune` is clobbered by the other writer.

Who is affected: every operator on a multi-harness machine (the upgrade/install prune and rules
asymmetries are invisible on a single-harness setup), and anyone resuming a plan-004…plan-017
bundle, where the execute path reads "no open work" and skips the plan entirely.

Two findings enlarged the work beyond the issues as filed, both confirmed by measurement:

- **#159's filed root cause is wrong.** The real cause is `derive_dolt_repo_root` refusing on the
  server-mode layout — the canonical profile (REQ-YF-PRE-010 invariant 1, `SPEC.md:856-859`) — so
  `--remove-remote` has **never worked** there, and the same helper silently degrades
  `has_local_only_remote` and the REQ-BINIT-016 wedge fix.
- **#143 is 14 dangling refs, not 5.** The issue counted only the tracker-bearing subset.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #159 | `yf doctor --repair --remove-remote` reports ok but does not remove the Dolt remote | include | Filed root cause is wrong; real cause is `derive_dolt_repo_root` (exp-002) | Epic 1 |
| #160 | Dolt remote configured and bead data pushed despite `dolt.local-only = true` | include | GitHub-side dolt refs already deleted; only the code-path defect remains. Authority: detect + propose, repair on request | Epic 1 |
| #156 | `skills upgrade` writes YOSHIKO_FLOW.md to the wrong surface, unmanaged, backed by no REQ | include | **Must land before #154** — two writers, one path | Epic 2 |
| #154 | `harness tune` regenerates YOSHIKO_FLOW.md wholesale; `--revert` deletes rather than restores | include | Fix = sha guard + conservative-keep. Block conversion alone does **not** deliver "restore" | Epic 2 |
| #155 | A dropped file lingers, pinning a skill at `modified` — give install an opt-in `--prune` | include | Plus hash ignore-list; `--prune` alone does not keep doctor green | Epic 2 |
| #144 | A bead stays open when its upstream issue closes | include | Live instance: `yf-1656` / #132 | Epic 3 |
| #142 | `closable` proposes closing issues already closed or deleted upstream | include | 29 of 35 emitted commands are no-ops or errors | Epic 3 |
| #143 | Plan.md `**Epic:**` fields are dangling refs to pre-rename beads | include | **14, not 5.** Repair + validator | Epic 3 |
| #158 | `yf self update` could never refresh codex, opencode or pi | supersede | Verified fully fixed by plan-042 (exp-005 Part B) — verify-and-close only | Epic 4 |
| [#161](https://github.com/dixson3/yoshiko-flow/issues/161) | plan-044-james-dixson-f6fdbd execution tracking | tracker | The single coarse tracking issue for this plan-scale effort (AGENTS.md convention). Stamped onto the epic as `external_ref` at pour (REQ-PLAN-073) | — |
| #152 | yf auto-updates claude-code settings.json to disable recommended skills/tools | exclude | Deferred by operator decision: a feature, and a new autonomy-lever config write deserving its own consent-gate design pass | — |

## Investigation Findings

Six experiments, all in [findings/](findings/). Highlights that shaped the approach:

**[exp-001](findings/exp-001-rules-aggregate-write-path.md) — #154/#156 are one defect family.**
The aggregate has two writers: `harness tune` (manifest-tracked) and `skills upgrade`
(`status.rs:103`, **unconditional, every harness, no manifest, no REQ**). Confirmed by sandboxed
mechanical drive across all five harnesses: upgrade writes a 24469 B aggregate to a `rules/` dir
**no non-claude harness loads**, while tune writes a 14552 B minimized block to the real surface.
`revert.rs:444-457`'s catch-all `_ =>` branch **unconditionally `remove_file`s** the aggregate —
measured to delete a hand-edited file, and **there is no backup mechanism anywhere in the
codebase**. REQ-YF-TUNE-022's "restore" promise is implemented for config scalars only.

**[exp-002](findings/exp-002-dolt-remote-local-only.md) — the repair fails open, silently.**
`remove_dolt_remote` swallows `derive_dolt_repo_root`'s `Err` in an `if let Ok(...)` with no
`else`, and that helper refuses whenever two `.dolt/` dirs exist — which server mode
**structurally guarantees** (confirmed across three unrelated repos). Doctor's verdict is
unconditional: `ok` means *"the step function returned `Ok`"*. `dolt.local-only` is an
**init-time flag only** and provides zero runtime protection; the decisive layer is the Dolt-DB
remote. **Five** land-the-plane prose sites propose `bd dolt push` with no local-only guard.
GitHub-side dolt refs are **already gone** — the exposure is remediated, the code path is not.

**[exp-003](findings/exp-003-upstream-reconcile-surface.md) — one missing input, two consumers.**
No code anywhere reads upstream issue state for reconciliation. Measured: `closable` emits 35
`gh issue close` commands, of which **28 are already closed, 1 is deleted, 1 is silently dropped
— 6 are genuinely actionable**. Both #142 and #144 are served by **one bulk
`gh issue list --state all` round-trip** (154 issues, sub-second). A deleted issue is
**indistinguishable** from a never-existed number, so both must classify as `UNRESOLVABLE` and
route to a human. Live `external_ref` format drift already exists (`yf-4d7s` = `"gh-91"`),
breaking two readers in opposite directions.

**[exp-004](findings/exp-004-install-prune-gap.md) — the engine is right, the call site is
missing.** `install.rs:66` hardcodes `prune=false`; `install` is multi-destination and `upgrade`
is single-destination, so nobody prunes across harnesses. Sandbox probe reproduced #155 directly
and confirmed **prune deletes operator files**. Critically: this machine's 7 leftovers are
runtime residue — 5 pycache/pytest plus 2 test-harness scratch — not dropped files. `--prune`
clears them and they **regenerate on the next `uv run`**.

**[exp-005](findings/exp-005-dangling-epics-and-158.md) — #143 is 14, and the failure is
silent success.** `resume-scan` returns `found: true, total: 0` on a dangling ref, not
`found: false`. All 14 recoverable 1:1 via `metadata.plan_dir`. **`record-epic` is the wrong
repair tool** — it would create frontmatter and `log.md`, flipping OKF-legacy bundles to
OKF-native and cascading ~9 warns each into hard failures. #158 verified **fully fixed**.

**[exp-006](findings/exp-006-spec-and-validation-surface.md) — the SPEC work is validation-dark.**
`SPEC.md` matches **no** CHANGE-VALIDATION §3 glob, so a SPEC-only edit fires zero FAST
validation — but it **does** fire drift-check `e-spec-guardrails` + `e-spec-readme`, so
`GUARDRAILS.md` and `README.md` must move in the same pass. (Epic 0 is not *wholly* dark: Issue
0.5 edits `yf/src/coverage.rs`, which fires `cargo-fmt` + `cargo`.) The coverage gate enforces
only bare `*(testable)*` and scans tags in `yf/src/**` **only** — a REQ tagged solely in
`yf/tests/*.rs` does not satisfy it.

## Approach

**SPEC-first, then three clusters in dependency order, then close.**

Ordering rationale, all evidence-driven rather than by issue number:

1. **Epic 0 (SPEC) first** — mandated by AGENTS.md. Because it is largely validation-dark it
   carries its own explicit `cargo test --workspace` step and its own
   `GUARDRAILS.md`/`README.md` pass.
2. **Epic 1 (beads integrity) before Epic 2** — smallest, and it retires a repair that has never
   worked in the canonical profile. Fixing the shared helper repairs three things at once.
3. **Epic 2: #156 must precede #154** — while `upgrade` still writes the aggregate, any guard
   added to `tune` is clobbered by the other writer. #155 has **no surface overlap** with #154
   (`install.rs`/`common.rs`/`marker.rs` vs `revert.rs`/`RuleRecord`), so the two sub-chains run
   in **parallel** from Issue 2.4 onward.
4. **Epic 3 (upstream reconcile) last** — largest, and its #143 half touches 14 historical
   bundles, best done when nothing else is in flight.

Decisions taken at scoping and after investigation:

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | #152 excluded | A feature, not a defect; a new autonomy-lever config write wants its own consent-gate design pass |
| D-2 | #160 authority = **detect + propose, repair on request** | doctor reports loudly and proposes exact commands; `--repair --remove-remote` removes. No unprompted mutation of remote config |
| D-3 | #143 = **repair all 14 + validator**, bundles stay OKF-legacy | Purpose-built one-shot, not `record-epic` (exp-005 A4) |
| D-4 | #156 proven on **all five harnesses under sandboxed `HOME`** | TESTING.md Tier-2; covers exactly the blindness class #158 documented |
| D-5 | #155 = `--prune` **+ hash ignore-list covering all 7 measured leftovers** | The only combination that makes `yf doctor` stay green without a manual step (exp-004 §5a) |
| D-6 | #159 = **fix the shared helper + fail-loud + postcondition** | One change repairs `--remove-remote`, `has_local_only_remote` and the wedge path together |
| D-7 | New REQs use **bare `*(testable)*`**; each allowlist row is added and removed **in the same commit as its tag** | Gate-enforced (plan-032 precedent), and `coverage.rs:200-222` fails on a *stale* row too — so the bridge must never outlive its tag by even one commit |
| D-8 | `--prune` is **not** wired into the install-time sync | It would silently delete operator files on every `yf self install`. Decide sync adoption separately |
| D-9 | #154 = **sha guard + conservative-keep**, not block conversion | Block conversion alone does not deliver "restore"; that needs a real backup. Smaller and closes the data-loss hole. It **is** a narrow grant of hand-edit tolerance on the revert path, so REQ-YF-FLOW-004 and REQ-YF-TUNE-022 are amended to say so rather than left contradicted |
| D-10 | **`skills remove` keeps its rules write**; only `upgrade`'s is removed. **Effective on claude-code only** | Otherwise nothing drops a removed skill's section — REQ-YF-FLOW-002 prunes on the *embedded* set, so a later `tune` retains it too. Honest limit: `remove` writes the **skills-sibling** `rules/` dir (`dest.rs:59`), which coincides with the tune-managed surface **only on claude-code**. On the other four it prunes a file nothing reads while the real section survives. That residual is filed as a follow-on (Issue 4.3), not silently claimed fixed |
| D-11 | **The `agents` rule target is PROBED, not guessed** — Issue 2.2 measures what that surface actually loads, then either adds a `RULE_TARGETS` row *with evidence* or declares `agents` skills-only | `upgrade` is today the only writer serving `agents`, so #156 could silently remove its rules. But exp-001 also found that dir is one **no non-claude harness loads** — so an unevidenced row would commit `tune` to writing an unread file forever. `SPEC.md:1251-1254` is the binding precedent: a rule target shall NOT be a compiled-in guess |
| D-12 | Structural consolidation of `DESCRIPTORS` + `RULE_TARGETS` is **deferred** | exp-001 rec 5 names it as the structural cause of both #156 and the `agents` gap. Out of scope here; filed as a follow-on at close (Issue 4.3) |

## Epics

### Epic 0: SPEC-first amendments

- Issue 0.1: Macro `SPEC.md` — add `REQ-YF-DOCTOR-006` (a `--repair` step shall verify its own
  postcondition), `REQ-YF-INSTALL-010` (`install --prune`), `REQ-YF-MARK-005` (tree-hash
  ignore-list), `REQ-YF-FLOW-008` (**`skills upgrade`** is rules-neutral; `remove` is not, per
  D-10), `REQ-YF-TUNE-029` (rules-side revert guard). **Amend** `REQ-YF-MARK-004` (prune
  default-on for upgrade, opt-in for install, one implementation); **amend `REQ-YF-FLOW-004`** to
  scope its unconditional-drop/delete clause to `remove` and to carve the revert path out of
  "no hand-edit tolerance" (D-9); **amend `REQ-YF-TUNE-022`** to name the rules-side guard
  alongside REQ-YF-TUNE-029; `REQ-YF-TUNE-020`'s `agents` row is **deferred to Issue 2.2**, which owns the resulting SPEC edit
  under both probe outcomes — 0.1 executes before 2.2, so the outcome is unknowable here, and per
  `SPEC.md:1251-1254` the amendment must carry evidence rather than a guess (D-11). Record the
  deferral in the amendment log so the post-Epic-0 SPEC edit is declared, not smuggled.
  All new REQs bare `*(testable)*` per D-7. Amendment-log entry records the FLOW-004 scoping
  explicitly.
- Issue 0.2: `skills/yf-beads-init/SPEC.md` — `REQ-BINIT-026` (an ambiguous/underivable Dolt root
  is an ERROR, not a silent skip; the server-mode two-`.dolt` layout is in scope, with a fixture),
  `REQ-BINIT-027` (`dolt.local-only` is init-time-only and not a runtime guard; land-the-plane
  prose shall suppress `bd dolt push` under it).
  - depends-on: 0.1
- Issue 0.3: `skills/yf-beads-upstream/SPEC.md` — `REQ-BUP-060` (resolve upstream state via one
  bulk query), `REQ-BUP-061` (the `reconcile` verb and its asymmetric authority), `REQ-BUP-062`
  (`external_ref` normalizes to an issue number; the two readers shall agree), `REQ-BUP-063` (no
  silent unparseable-ref drop), `REQ-BUP-064` (never auto-close a bead on an `UNRESOLVABLE` ref;
  a `gh` failure yields INCONCLUSIVE, never a falsely-clean proposal). **Each new `REQ-BUP-*`
  lands a tagged case in `skills/yf-beads-upstream/scripts/test_upstream.py`** under its existing
  `# --- REQ-BUP-0NN:` convention — the macro coverage gate never reaches `REQ-BUP-*` (exp-006),
  so nothing mechanical will notice a missing one.
  - depends-on: 0.1
- Issue 0.4: `skills/yf-plan/spec/cli.md` — `REQ-CLI-020` (audit check #9: a `**Epic:**` ref shall
  resolve; `warn` when `bd` is unavailable) and amend `REQ-CLI-013` (`resume-scan` reports
  `epic_resolves`). Amend `REQ-CLI-006`'s subcommand enumeration for any added verb.
  - depends-on: 0.1
- Issue 0.5: Allowlist bridge — add `(id, reason)` rows to `coverage.rs` `ALLOWLIST` for each new
  bare-`*(testable)*` macro REQ. **Invariant (D-7): every row is removed in the same issue and
  the same commit that adds its `// REQ-…` tag.** `coverage.rs:200-222` fails on a stale row, so
  a row that outlives its tag by one commit turns the tree red.
  - depends-on: 0.1
- Issue 0.6: Drift pass — update `GUARDRAILS.md` and `README.md` so `e-spec-guardrails` and
  `e-spec-readme` resolve in the same change-set.
  - depends-on: 0.1, 0.2, 0.3, 0.4
- Issue 0.7: Explicit verification — `cargo test --workspace`, recorded. The SPEC edits fire no
  FAST validation of their own (exp-006), so this is their only signal.
  - depends-on: 0.5, 0.6

### Epic 1: Beads integrity (#159, #160)

- Issue 1.1: Fix `derive_dolt_repo_root` (`beads_init.rs:709-731`) to resolve the server-mode
  layout deterministically — prefer `beads_dir/<metadata.dolt_database>` before declaring
  ambiguity. Unit test with a **server-mode two-`.dolt` fixture** (the layout no fixture covers
  today, which is why this shipped). Tag `// REQ-BINIT-026`.
  - depends-on: 0.7
- Issue 1.2: Replace the swallowed `if let Ok(...)` at `beads_init.rs:1178` with explicit `Err`
  propagation, so an underivable root becomes rc != 0 → `FAIL`, never a silent `ok`.
  - depends-on: 1.1
- Issue 1.3: Doctor postcondition — after an applied `remove-remote` step, re-run
  `has_local_only_remote` and fail if still true. Tag `// REQ-YF-DOCTOR-006` **and remove its
  allowlist row in the same commit**.
  - depends-on: 1.2
  - resolves-upstream: #159 (include)
- Issue 1.4: New read-only doctor `Check` wrapping `has_local_only_remote`, following the
  `Box<dyn Check>` registry pattern (`checks.rs:682-704`), reusing the remediation string from
  `preflight.rs:791-793` verbatim. Delivers the "reports loudly" half of D-2.
  - depends-on: 1.3
- Issue 1.5: Reconcile the three inconsistent descriptions of `--remove-remote` (`cli.rs:449-453`
  help, the `beads_init.rs:570` step label, actual behavior) to one accurate statement.
  - depends-on: 1.3
- Issue 1.6: **Probe the #160 causal mechanism.** exp-002 (b) is explicitly marked inferred and
  unverified: `repair()` (`beads_init.rs:456-462`) runs `bd init` **before**
  `bd config set dolt.local-only true`, and local-only is an init-time skip flag — so `bd init`
  may wire the remote from git origin first, while the step label at `:461` asserts *"no remote
  wired at init"*. Run the sandboxed `bd init`-with-git-origin probe. **If confirmed:** reorder
  `repair()` (or imply `--remove-remote` on that path) and correct the false label. **If
  refuted:** record the refutation in `findings/`. Either way the result is written down —
  #160 must not close with its most plausible cause merely undiscussed.
  - depends-on: 1.4
- Issue 1.7: Local-only guard on the **five** land-the-plane sites (script half first, prose
  second, so the 19-edge SKILL.md fan-out resolves in one pass):
  `skills/yf-beads-hygiene/scripts/beads_hygiene.py:689,764`, then
  `skills/yf-plan/SKILL.md:1038`, `skills/yf-beads-hygiene/SKILL.md:127`,
  `skills/yf-plan/agents/coordinator.md:114-116` (authorization-gated but **not**
  local-only-gated), and correct `skills/yf-research/agents/packager.md:71` (its existing guard is
  backwards for #160 — a stray remote *satisfies* it). Tag `// REQ-BINIT-027`.
  - depends-on: 1.6
  - resolves-upstream: #160 (include)
- Issue 1.8: Clean the dangling `sync:` key left in `.beads/config.yaml` by the partial repair,
  and make `remove_sync_remote_config` not leave one.
  - depends-on: 1.2

### Epic 2: Deploy path (#156 → #154; #155 in parallel)

- Issue 2.1: **#156** — remove the `install_rules_aggregate` call at `status.rs:103` (upgrade
  only). **Leave `status.rs:165` (`remove`) intact per D-10** and update its doc comment to state
  why. Add the negative assertion `install.rs:466` already carries. Tag `// REQ-YF-FLOW-008`
  **and remove its allowlist row in the same commit**.
  - depends-on: 0.7
- Issue 2.2: **D-11 — probe, then decide the `agents` rules target.** First establish what the
  `agents` surface actually loads. exp-001 found that `rules/` dir is one **no non-claude harness
  loads**, and the four other AGENTS.md harnesses all use `AgentsMd` — so `~/.agents/AGENTS.md` is
  at least as plausible as `RulesDir`. Record the measurement in `findings/`. **Then** either add a
  `RULE_TARGETS` row to `managed_block.rs:345` carrying that evidence, or declare `agents` a
  skills-only bare surface in REQ-YF-FLOW-008 and drop `~/.agents/rules` from
  `preflight.rs:213-217`'s candidate list. Either way this issue also:
  - updates `web/content/pages/harness-tune.md` — `doc_agreement.rs:169-184` iterates
    `RULE_TARGETS` and requires each derived subpath verbatim, so
    `tune_matrix_agrees_with_profiles_and_rule_targets` (`:246`) **fails without it**. Correct the
    pre-existing drift at `harness-tune.md:44,53` (it already claims agents receives skills *and*
    rules) in the same pass;
  - declares the config-verdict change: adding a row flips `tune --harness agents` from
    `Refused{unknown-harness}` to `Deferred` (`mod.rs:325`). Name it rather than let it happen;
  - **owns the SPEC edit under whichever branch it takes** (deferred here from Issue 0.1): under
    **A**, amend `REQ-YF-TUNE-020`'s destination enumeration (`SPEC.md:1249-1251` lists three);
    under **B**, the `agents`-is-skills-only wording in REQ-YF-FLOW-008. Either edit carries the
    probe evidence and an amendment-log entry. `REQ-YF-TUNE-020` is already tagged in `yf/src`, so
    no allowlist row is involved and D-7's invariant is untouched.
  - depends-on: 2.1
- Issue 2.3: Handle the doctor/preflight fallout — `preflight.rs:213-217` hardcodes four
  rule-candidate dirs and `common::installed_rule_source` reads them, so removing upgrade's write
  can flip non-claude harnesses to `rule_missing`. A behavior change, not a pure removal.
  - depends-on: 2.2
- Issue 2.4: Cross-harness proof under sandboxed `HOME` (D-4) — assert `skills upgrade --harness
  codex` leaves `~/.agents/rules/` untouched, and that each harness's rules land only on its
  declared surface, for **all five descriptors**. Under probe outcome **B** the `agents` assertion
  is its negative form: **no rules file is written anywhere for `agents`**. This requires extending
  `harness_cross_e2e.rs:69-93 surfaces()`, which `panic!`s on `"agents"` today, and the `:111`
  iteration, which covers three. **Extending the test to five is this issue's deliverable** — see
  the capability gate note.
  - depends-on: 2.3
  - resolves-upstream: #156 (include)
- Issue 2.5: **#154** — add `sha256` to `manifest::RuleRecord` and record it on every rules write.
  - depends-on: 2.4
- Issue 2.6: Make the `aggregate` revert branch (`revert.rs:444-457`) **conservative-keep**: on a
  sha mismatch, keep the file and report rather than `remove_file`. Replace the catch-all `_ =>`
  with an explicit match so a future `kind` cannot silently inherit delete semantics. Tag
  `// REQ-YF-TUNE-029` **and remove its allowlist row in the same commit**.
  - depends-on: 2.5
- Issue 2.7: Revert round-trip test — hand-edit the aggregate, revert, assert the file **survives**
  with a reported mismatch; and an unedited aggregate still reverts cleanly.
  - depends-on: 2.6
  - resolves-upstream: #154 (include)
- Issue 2.8: **#155 prerequisite** — fix `extra_deployed_files` (`common.rs:172-183`) to apply the
  harness name transform, so `--dry-run --harness pi` stops under-reporting the prune set to
  empty. A preview that lies is worse than none.
  - depends-on: 2.4
- Issue 2.9: Add `--prune` to `SkillsArgs` (`cli.rs:369-371`) and thread it to `install.rs:66`;
  prune fans out across `resolved_dests` for free. Compute and emit `"pruned"` per destination,
  including in install's `--dry-run` block (`:134-154`), which computes no extras today. Tag
  `// REQ-YF-INSTALL-010` **and remove its allowlist row in the same commit**.
  - depends-on: 2.8
- Issue 2.10: Hash ignore-list (D-5) — exclude `__pycache__/**`, `*.pyc`, `.pytest_cache/**`,
  `.DS_Store`, **`**/.scratch/**` and `**/test-harness/topology.txt`** (the last two are the
  test-harness residue exp-004 measured; without them criterion 7 is unmeetable). Applied
  **symmetrically** to **four** surfaces — `marker::walk_files`, `extra_deployed_files`,
  `prune_extra_files`, **and `embed.rs`'s `#[exclude]` list** — or prune and hash disagree. The
  fourth is not optional: `embed.rs:48-50` excludes only `*.pyc`/`__pycache__`, so a release built
  on a machine where `bootstrap.sh` has run **bakes `topology.txt` and `.scratch/sandbox.env` — a
  developer's sandbox env file — into the binary and ships it to every user**. Fixing only the
  three read-side surfaces makes doctor green while leaving that intact. Self-consistent: an
  unembedded residue file becomes an extra deployed file, which the ignore-list then spares from
  prune. Tag `// REQ-YF-MARK-005` **and remove its allowlist row in the same commit**.
  - depends-on: 2.9
- Issue 2.11: Tests — (a) a hand-added **skill directory** survives a `--prune` install; (b) prune
  fans out to **both** destinations of a two-harness install; (c) `extra_deployed_files --harness
  pi` reports the transformed path; (d) a unit test that each of the 7 residue paths exp-004
  measured is excluded from the tree hash. *(The live-machine check is an operator step at close,
  not a test — see Success Criteria 7.)*
  - depends-on: 2.10
  - resolves-upstream: #155 (include)

### Epic 3: Upstream reconcile (#144, #142, #143)

- Issue 3.1: Normalize `external_ref` to an issue number at the read boundary so `external_for()`
  (`upstream.py:346-354`, URL-only) and `external_from_row()` (`:357-370`, any string) agree, and
  repair the live `yf-4d7s` = `"gh-91"` drift. Covered by a `REQ-BUP-062` case in
  `skills/yf-beads-upstream/scripts/test_upstream.py` — the per-skill suite, since the macro
  coverage gate does not reach `REQ-BUP-*` (exp-006).
  - depends-on: 0.7
- Issue 3.2: Shared bulk upstream-state resolver — one `gh issue list --state all --json
  number,state`. A mapped ref absent from the result is `UNRESOLVABLE` at zero extra cost.
  **Sub-step:** `run()` (`upstream.py:85-90`) raises `SystemExit` on any non-zero subprocess, so
  INCONCLUSIVE is unreachable today. Add a non-raising call path (e.g. a `check=False` variant)
  used only by this resolver; **every existing caller keeps its fail-fast semantics**.
  - depends-on: 3.1
- Issue 3.3: **#142** — `closable` annotates each row with `upstream_state` and emits no command
  for a non-OPEN issue; `UNRESOLVABLE` rows are reported separately for a human. Degrade
  gracefully to INCONCLUSIVE when `gh` is unavailable.
  - depends-on: 3.2
  - resolves-upstream: #142 (include)
- Issue 3.4: Stop the silent unparseable-ref drop at `cmd_closable` (`:1204-1206`) — report it.
  - depends-on: 3.2
- Issue 3.5: **#144** — a `reconcile` verb proposing `bd close -r "<upstream #N closed>"` for each
  non-closed bead whose issue is CLOSED. Local half is `--apply`-able (reversible via the
  `bd close -r` tombstone + `unhoist`); **the upstream half stays propose-only, no `--apply`**
  (REQ-BUP-052 and the always-loaded rule). Never auto-close on `UNRESOLVABLE`.
  - depends-on: 3.3, 3.4
- Issue 3.6: Clear the live instance — reconcile bead `yf-1656` against closed #132.
  - depends-on: 3.5
  - resolves-upstream: #144 (include)
- Issue 3.7a: **#143 repair — build and preview.** A purpose-built one-shot rewriting, for each of
  the 14 bundles (plan-004…plan-017), the `**Epic:**` body line **and** the phase-log
  `- <date> intake: epic … poured` line, using the old→new mapping in exp-005 A2. Bundles stay
  OKF-legacy (D-3): do **not** route through `record-epic`. **`--dry-run` is the default**
  (mirroring the `push --apply` convention). Deliverable: the tool plus the emitted old→new
  mapping for operator review.
  - depends-on: 0.7
- Issue 3.7b: **#143 repair — apply.** Run the one-shot with `--apply`, then the **mandatory
  postcondition**: re-run `resume-scan` across all 14 and assert `total > 0` on each — the plan's
  own verify-your-own-postcondition thesis applied to its riskiest step. `docs/plans/` is
  git-tracked, so a mis-mapping is recoverable by `git checkout`; the risk is a wrong mapping, not
  data loss. Split from 3.7a because a gate blocks a **bead**, not a sub-step — one issue that
  both builds the one-shot and is blocked on having run it would be circular.
  - depends-on: 3.7a
- Issue 3.8: **#143 validator** — `_audit_plan` check #9: a `**Epic:**` ref shall resolve via `bd`.
  Use `missing_level` (**not** `okf_missing_level`, which would downgrade all 14 to `warn`), and
  emit `warn` when `bd` is unavailable so a portable bundle on a beads-less machine does not
  hard-fail. One implementation yields both the hard `audit` gate and the advisory `audit-close`.
  Ships with a test script covering all three states (fail / warn / pass), following the
  `uv-yf-*` family precedent, **plus its CHANGE-VALIDATION §1 row, §3 glob and §2 fingerprint
  re-approval in the same issue** — a new test script costs three edits, and deferring them to
  Epic 4 would leave it invisible to both tiers for the length of Epic 3.
  - depends-on: 3.7b
- Issue 3.9: Add `epic_resolves: bool` to `resume-scan`'s output — the silent false success
  (`found: true, total: 0`) is where the defect actually bites, and `resume-scan` is the only verb
  the execute path consults.
  - depends-on: 3.8
  - resolves-upstream: #143 (include)

### Epic 4: Close-out

- Issue 4.1: Verify-and-close #158 — run `cargo test -p yf sync` as the hard gate exp-005 Part B
  identified, then close the issue with the verification recorded. *(exp-005 Part B footnote 2 —
  `install_args_are_explicit_per_harness` never asserts `--surface` is absent — is deliberately
  **not** picked up: no code path can emit it, so it is a robustness nit, not remaining work.)*
  - depends-on: 1.5, 1.7, 1.8, 2.7, 2.11, 3.6, 3.9
  - resolves-upstream: #158 (supersede)
- Issue 4.2: Final CHANGE-VALIDATION audit — confirm every test script added by this plan has its
  §1 row, §3 glob, and a re-approved §2 fingerprint. (Each was added by its creating issue; this
  is the sweep, not the first pass.)
  - depends-on: 4.1
- Issue 4.3: Confirm `coverage.rs`'s `ALLOWLIST` is net-clean — every bridge row removed by the
  commit that added its tag, and `allowlist_entries_are_relevant_and_not_stale` green. **File the
  D-12 follow-on** (consolidate `harness_desc::DESCRIPTORS` + `managed_block::RULE_TARGETS` into
  one table with an explicit rules-surface column — exp-001 rec 5, the structural cause of both
  #156 and the `agents` gap) **and the D-10 residual** (`skills remove` prunes the skills-sibling
  `rules/` dir, so its section-drop is effective on claude-code only; the other four harnesses keep
  the section in their tune-managed surface).
  - depends-on: 4.2

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Capability Gate: sandboxed-HOME cross-harness proof

- Type: auto
- Condition: a sandboxed `HOME` can be built and driven for the **three config-bearing harness
  descriptors the existing test covers** (claude-code, codex, opencode) without touching the real
  `~/.claude`, `~/.config`, `~/.codex` or `~/.local/bin`.
- Test: `cargo test -p yf --test harness_cross_e2e`
- Blocks: Issue 2.4
- Note: this Condition is deliberately narrower than "all five". The test exits 0 at HEAD because
  `surfaces()` `panic!`s on `"agents"` and `:111` iterates three descriptors — so a five-descriptor
  Condition would assert something the gate does not prove. **Extending coverage to all five is
  Issue 2.4's deliverable**, not this gate's precondition.
- Instructions: follow TESTING.md's sandboxed-`HOME` recipe; the binary is the **workspace-root**
  `target/debug/yf`. Every invocation sets `HOME` to a tempdir and clears `CI`. A leak would apply
  `permissions.defaultMode: "bypassPermissions"` to the developer's real config — the exact harm
  the consent gate exists to prevent.

### Capability Gate: 14-bundle repair dry-run

- Type: human
- Approvers: operator
- Condition: Issue 3.7a has emitted the old→new mapping for all 14 bundles and it has been
  reviewed against exp-005 A2.
- Test: `plan_manager.py resume-scan` reports `total > 0` for all 14 after an **in-place trial
  apply on a scratch branch**
- Blocks: Issue 3.7b
- Instructions: a mass edit across 14 historical bundles gets the same propose-then-apply
  treatment as an upstream write. **Do not use a scratch clone** — `.beads/` is git-excluded
  (`.git/info/exclude:9`) and `git ls-files .beads` is empty, so a fresh clone has no beads DB and
  every bundle reports `total: 0`: the Test would assert the exact failure signature this plan is
  fixing and could never pass. Do not `cp -r` the working tree either — that copies
  `dolt-server.{pid,port,lock}` and a live server handle. Apply in place on a scratch branch and
  recover with `git checkout -- docs/plans/`. **Commit the plan-044 bundle first** — the trial apply
  runs in the live tree, so an uncommitted bundle edit would be discarded by that same recovery.

### Reconcile Gate

- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| Risk | Mitigation |
| :-- | :-- |
| **A stale allowlist row turns the tree red** — `coverage.rs:200-222` fails when a row's tag lands, not just when it is missing | D-7 makes row-removal same-issue **and same-commit** as the tag (Issues 1.3, 2.1, 2.6, 2.9, 2.10 each carry it); 4.3 asserts net-clean |
| **SPEC edits fire no FAST validation** — a bare `*(testable)*` REQ with no test breaks the *next* epic's run, not its own | Issue 0.7's explicit `cargo test --workspace`, plus the same-commit allowlist invariant |
| **#156 could silently remove `agents` rules entirely** — upgrade is its only writer today | Issue 2.2 **probes before deciding** (D-11), ahead of the cross-harness proof in 2.4. Guards the opposite error too: an unevidenced `RULE_TARGETS` row would commit `tune` to writing a file exp-001 found nothing loads |
| **Residue is baked into the release binary, not merely left on disk** — `embed.rs` excludes only `*.pyc`/`__pycache__` | Issue 2.10 applies the ignore-list to **four** surfaces including `embed.rs`, so a dev machine's `.scratch/sandbox.env` cannot ship to users |
| **Close-out could run with upstream issues still open**, and 4.3 could false-green on a present-but-untagged allowlist row | Issue 4.1's `depends-on` closure widened to all seven epic leaves (1.5, 1.7, 1.8, 2.7, 2.11, 3.6, 3.9) |
| **`skills remove` could orphan a removed skill's section permanently** — FLOW-002 prunes on the embedded set | D-10 keeps `remove`'s rules write; Issue 0.1 amends FLOW-004 rather than leaving it contradicted |
| **Removing upgrade's rules write regresses doctor/preflight** to `rule_missing` on non-claude harnesses | Issue 2.3 handles it explicitly as a behavior change |
| **Prune deletes operator files** — confirmed in the sandbox probe, not theoretical | Report-first preview (2.9), transform fix first (2.8), test (a) in 2.11. Provenance-gated prune considered and deferred; D-8 keeps `--prune` out of the sync |
| **Repairing 14 historical bundles could mis-map** | Dry-run default and mapping preview (3.7a) + human capability gate + mandatory `resume-scan total > 0` postcondition (3.7b). `docs/plans/` is git-tracked, so blast radius is `git checkout` — the risk is a wrong mapping, not data loss |
| **`reconcile` needs a network read to compute its proposal**, unlike `push` whose preview is local | REQ-BUP-064: a `gh` failure yields INCONCLUSIVE, never a falsely-clean proposal — and Issue 3.2 owns the `run()` change that makes INCONCLUSIVE reachable at all |
| **Touching `run()` could regress every other `upstream.py` verb** | The non-raising path is a new variant used only by the resolver; existing callers keep fail-fast (3.2) |
| **A deleted issue is indistinguishable from a typo** | Both classify `UNRESOLVABLE` and route to a human; never auto-close a bead on that basis |
| **Live-DB mutations** — 3.1 rewrites `yf-4d7s`'s ref, 3.6 closes `yf-1656` | Both are single-bead, both reversible (`bd close -r` tombstone / `unhoist`), both after their verb is tested |
| **`skills/*/SKILL.md` edits fan out to 19 drift edges** | Issue 1.7 orders its own edits script-then-prose so the edges resolve in one pass |
| Plan is large (5 epics, 39 issues, 3 subsystems) | Epics land as separate merges. **Independence is a consequence of the same-commit allowlist discipline, not independent of it** — without D-7, Epic 2 would poison the shared FULL-tier gate for every other in-flight branch |

## Success Criteria

1. `yf doctor --repair --local-only --remove-remote` on a **server-mode** repo either removes the
   Dolt remote or reports `FAIL` — never `ok` with the remote surviving. Proven by a server-mode
   two-`.dolt` fixture.
2. `yf doctor` reports a configured Dolt remote under `dolt.local-only = true` as a violation and
   proposes the exact removal commands, without mutating anything unprompted.
3. **No** land-the-plane surface proposes `bd dolt push` in a local-only repo — all five sites in
   exp-002 (d), including `coordinator.md`.
4. The `repair()` init-ordering hypothesis is **settled in writing** — either fixed with the false
   `:461` step label corrected, or refuted and recorded in `findings/`.
5. `yf harness skills upgrade --harness <h>` writes **no** `YOSHIKO_FLOW.md` for any of the five
   harnesses; `yf harness tune` is the sole writer, and the `agents` surface is **resolved by
   evidence** — either served by tune at a probed target, or declared skills-only with
   `preflight.rs` reconciled to match. `yf harness skills remove <skill>` still drops that skill's
   section **on claude-code**, where the skills-sibling `rules/` dir and the tune-managed surface
   coincide; the non-claude residual is recorded as a follow-on, not claimed fixed.
6. `yf harness tune --revert` on a hand-edited aggregate **keeps the file** and reports the sha
   mismatch. On an unedited one it still reverts cleanly.
7. `yf harness skills install --prune` removes dropped files across **every** resolved
   destination; `--dry-run --prune` reports the exact set, transform-correct on `pi`; a
   hand-added skill *directory* survives.
8. All 7 residue paths exp-004 measured are excluded from the tree hash (unit-tested), and a
   post-land `./target/debug/yf` doctor run on this machine reports **zero `modified` skills and
   stays green after a `uv run` inside a deployed skill dir**. *(The unit test is the gate; the
   live-machine run is a recorded operator check at close, since it asserts about the real
   `~/.claude` which the sandbox discipline forbids tests from touching.)*
9. `upstream.py closable` emits commands **only** for issues OPEN upstream; `UNRESOLVABLE` refs
   are reported, never silently dropped. Measured against today's baseline of 35 emitted /
   6 actionable.
10. `upstream.py reconcile` proposes closing every bead whose upstream issue is closed, and
    `yf-1656` is reconciled. The upstream half remains propose-only.
11. All 14 plan bundles resolve their `**Epic:**` ref and report `resume-scan total > 0`;
    `plan_manager.py audit` fails loud on a dangling ref and `warn`s when `bd` is absent;
    `resume-scan` reports `epic_resolves`.
12. #158 verified by a green `cargo test -p yf sync` and closed.
13. `cargo test --workspace` and `cargo clippy --workspace --all-targets -- -D warnings` are
    green, and `coverage.rs`'s `ALLOWLIST` is net-clean — no bridge row outlived its tag.

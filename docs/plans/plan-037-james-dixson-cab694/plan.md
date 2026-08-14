---
type: Plan
okf_spec: OKF-PLAN
id: plan-037-james-dixson-cab694
author: james-dixson
created: '2026-08-13'
status: approved
deliverable_class: standard
fingerprint: 9aab71e9e01d2243194bbdd8202960dfda954302b6a73b8fb6545f622247e129
---
# Plan: Reconcile user-scope yf-* installs with main

**ID:** plan-037-james-dixson-cab694
**Author:** james-dixson
**Created:** 2026-08-13
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 9aab71e9e01d2243194bbdd8202960dfda954302b6a73b8fb6545f622247e129

## Objective

Bring the user-scope `~/.claude/skills/yf-*` installation and the `yoshiko-flow` repository
back into a single, explainable state: refresh the stale installed copies, upstream the one
genuine local patch as a proper repo change on the current idiom, and import the one
user-scope-only skill (`yf-herdr`) as first-class repo content.

The end state is that a fresh install from `main` reproduces the operator's working setup
exactly — no hand-patched files, no skill that exists only on one machine.

## Motivation

Local patches were made directly to user-scope skill files while working in other projects,
and a skill (`yf-herdr`) was authored entirely outside the repo. That work is real and in
daily use, but it lives only on one machine: it is absent from `main`, invisible to any other
clone, and silently destroyed by the next `install.sh --force`. Meanwhile the repo has moved
ahead of the install, so the operator is running skills whose behavior no longer matches
their own SPECs.

Concretely, this session drafted its plan using the **stale v0.4.0 `yf-plan` skill**, whose
Pre-flight section still documents `/.state/` gitignore anchors and `.yf-plan.local.json`
config — a layout `main` replaced with the canonical `.yf/<short>/` tree. The skill
describing the process and the repo defining it disagree, and the operator is following the
older one.

Left alone this gets worse in both directions: every repo advance widens the staleness gap,
and every further local patch adds unversioned work that a routine reinstall will silently
revert.

## Investigation Findings

Three experiments; full detail in `findings/`.

**The install stamp is noise.** All 19 user-scope `SKILL.md` files differ by exactly one
injected line, `<!-- yf-skills: v=0.4.0 tree=<sha> -->`. Unfiltered comparison reports 19
false positives. After filtering, 22 files genuinely differ.

**21 of those 22 are stale-only, provably.** For each file, every historical version of that
path was searched for a blob matching the user-scope content. All 21 match an exact commit
(dates spanning 2026-06-30 to 2026-07-21, each file's newest version as of ~2026-07-21), so
the install is one coherent snapshot and **no stale-side file hides a local edit**. Refresh is
safe and loses nothing. (`v=0.4.0` is the Cargo version, not the `v0.4.0` tag — comparing
against the tag yields false "local edit" verdicts.)

**Exactly one genuine local patch exists.** `yf-plan/scripts/plan_manager.py` matches none of
its 11 historical versions; the delta against its closest ancestor is a single 28-line hunk
adding `_bootstrap_layout()` and making `PLANS_DIR` / `INCUBATOR_PARENT` configurable. It is
well-formed but built on the **legacy root-dotfile idiom** the repo already superseded, so
porting it verbatim would add a third config reader on the deprecated surface — re-creating
the exact drift #100 exists to remove. **#100 must therefore land before #107.**

**The `yf-herdr` import is smaller than expected in some places and blocking in others.**
rust-embed takes the whole `skills/` tree and every DRIFT-CHECK edge is glob-scoped, so both
cover a new skill with zero manifest edits. But `yf/src/testdata/install-parity.json` is a
frozen golden enumerating all 18 skills and `parity.rs` asserts against it — a 19th skill
without a fixture update is a test failure. And the skill's `depends-on-skill: [herdr]` points
at a **third-party** skill, while that field means "bare in-repo skill names"; it must become a
prose soft-dep, matching the pattern yf-plan already uses for `yf-change-validation`.

**One question the investigation deliberately did not settle.** The 8 companion rules are
installed as a single concatenated `~/.claude/rules/YOSHIKO_FLOW.md` rather than 8 separate
files. All 8 sections are stale. Whether the bundling is a deliberate harness choice or
install drift is unresolved, and is carried below as Issue 1.1 rather than assumed either way.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| #107 | yf-plan: make PLANS_DIR and INCUBATOR_PARENT configurable | include | The local patch. Re-implemented on canonical `.yf/` config, not ported verbatim. | Issue 2.3 |
| #100 | plan_manager.py: align .yf/ layout to canonical short-name + canonical-first config read | include | Hard prerequisite of #107 — supplies the single config reader #107 consumes. | Issue 2.2 |
| #101 | yf-change-validation: read canonical .yf/plan/config.local.json for validate-cmd seed | include | Second consumer of the same reader; leaving it legacy-only re-creates the drift #100 removes. | Issue 2.4 |
| #110 | herdr: leverage `herdr agent *` to launch and monitor agent sessions | partial | **In scope:** the `yf-herdr` skill surface — source, SPEC, parity entry, web page — i.e. delegating an approved plan to a new herdr tab and observing it. **Out of scope:** the `herdr agent *` fan-out primitive itself (coordinator loops dispatching to secondary sessions instead of in-process subagents), which is what #110 actually proposes and which stays open. | Issue 3.7 |
| #102 | .markdown-lint-on-edit -> .yf/markdown-lint-on-edit | exclude | Different marker; needs `migrate.rs` code + a gitignore commit-semantics decision. Not user-scope divergence. Its commit-semantics question is *related* to Issue 2.1 and is cross-referenced, not solved. |  |
| #109 | stale_approved computed status-independently | exclude | Unrelated to install reconciliation. |  |

All other open issues were reviewed and are out of scope.

## Approach

Four epics. Three match the three divergence buckets; the fourth closes the loop that the
first three cannot. The buckets need genuinely different treatments and the main way this
work goes wrong is conflating them — so each epic has its own verification, and the risky
ones are gated behind decisions.

**Epic 1 preserves the un-upstreamed work, then refreshes the stale install to a baseline.**
Pure consumption of what `main` already has. It runs first so later epics are authored
against a correct local view, and because it is the only epic that can destroy the
un-upstreamed work — the patch and the skill are captured out-of-tree *before* anything is
overwritten.

**Epic 2 upstreams the patch**, SPEC-first, in the order #100 → #107 → #101: establish one
canonical-first config reader, then add configurable roots as its consumer, then fix the
second consumer. The import-time constraint (`PLANS_DIR` is a module constant resolved before
most of the module exists) is the real friction and gets its own issue rather than being
assumed away.

**Epic 3 imports `yf-herdr`**, SPEC-first, ending with the parity fixture and the web page so
the drift-check and parity gates are satisfied in the same change-set that introduces the
skill.

**Epic 4 re-installs from merged `main` and verifies.** Epics 2 and 3 *add* things to the
repo — the `#107` feature and `yf-herdr` — that Epic 1's baseline refresh could not have
installed, because they did not exist yet. Without a second install, user scope ends this
plan stale again in a new way, and the objective is unmet. Epic 4 is where the plan's
central claim is actually tested.

### Self-modification policy

This plan edits and reinstalls the skill that is executing it. `plan_manager.py` is called
continuously by the coordinator (`update-status`, `resume-scan`, `landing-lock`,
`close_cascade`), and Epic 2 moves `STATE_DIR` from `.yf/yf-plan/` to `.yf/plan/` — which
relocates `landing.lock`, the lock Phase 6 holds. Swapping the manager mid-flight risks the
lock path changing between acquire and release.

The policy, chosen here rather than left to execution-time judgment:

> **`yf-plan` is excluded from every mid-plan refresh.** Epic 1 refreshes the other 18
> skills and the rules surface; `yf-plan` itself is refreshed only in Epic 4, after
> RECONCILE, with no landing lock held. The plan therefore executes start-to-finish on a
> single, stable copy of the manager script.

A consequence to accept knowingly: the plan runs to completion on the **stale** `yf-plan`,
including its stale `.yf/yf-plan/` state path. That is the correct trade — a consistent stale
manager is safer than a manager that changes underneath a running execution.

Ordering: Epics 2 and 3 are independent of each other and both depend on Epic 1. They may run
in either order or in parallel. Epic 4 depends on both.

## Epics

### Epic 1: Preserve, then refresh the stale user-scope install to a baseline

- **Issue 1.1: Resolve the rules-surface question.** Determine whether the single concatenated
  `~/.claude/rules/YOSHIKO_FLOW.md` is deliberate installer behavior or drift, by reading
  `install.sh` and the `yf` rule-deployment path. Record the answer in the plan folder. Both
  branches are defined so the answer cannot expand scope:
  - **intentional** → refresh the bundle in place; no further work, no follow-up.
  - **drift** → refresh the bundle in place *anyway* (it is the working surface), file a
    follow-up issue describing the deviation, and leave the installer unchanged. Fixing the
    installer is explicitly **not** in this plan.

  Blocks 1.3, because the refresh must not "fix" something that is working as designed.
- **Issue 1.2: Preserve the un-upstreamed work out-of-tree.** Copy to the pinned path
  `~/yf-preserve-plan-037/`:
  - `~/.claude/skills/yf-plan/scripts/plan_manager.py`
  - `~/.claude/skills/yf-plan/scripts/plan_manager.py.pre-incubator-root.bak`
  - the entire `~/.claude/skills/yf-herdr/` directory

  Then verify each copy byte-for-byte. This is the irreversibility guard and a hard
  prerequisite of 1.3. `yf-herdr` exists on this machine only and has no other copy anywhere.
  - depends-on: —
- **Issue 1.3: Refresh the 18 non-`yf-plan` skills and the rules surface.** Re-run the repo
  installer against `main`. Per the self-modification policy, **`yf-plan` is excluded** and is
  refreshed in Epic 4 instead. Do **not** hand-copy files.
  - depends-on: 1.1, 1.2
- **Issue 1.4: Verify the baseline refresh.** Re-run the `exp-01` three-pass comparison,
  **excluding `__pycache__/`, `*.pyc`, and `.DS_Store`** (build artifacts and OS cruft that
  always differ and would false-fail the check). Expected end state: the only remaining
  differences are the install stamp, all of `yf-plan/` (deliberately not refreshed), and
  `yf-herdr` (until Epic 3 lands). Any *other* difference means the refresh went wrong and
  halts the epic.
  - depends-on: 1.3

### Epic 2: Upstream the configurable-roots patch on the canonical idiom

- **Issue 2.1: Decide and record the config-tier semantics.** Settle whether `plans-root` /
  `incubator-root` are a **shared, committed** decision or a **local-only** one. The local
  patch invented a committed `.yf-plan.json` tier, but the canonical `.yf/` tree is entirely
  gitignored, so a committed layout decision has no canonical home today. This is the same
  commit-semantics problem #102 raises for the markdown-lint marker; cross-reference, do not
  solve #102 here. Output: a recorded decision. Blocks 2.2 and 2.3 — the reader's shape depends
  on the answer.
- **Issue 2.2 (#100): SPEC then implement canonical-first config + short-name state.** Land the
  `SPEC.md` / `spec/data.md` / `spec/prerequisites.md` REQ changes first, then change
  `_read_config()` to read `.yf/plan/config.local.json` first with the legacy root dotfile as
  fallback (mirroring `preflight.rs` `read_config`), and `STATE_DIR` to the short name
  `.yf/plan/`. Include migration of existing `.yf/yf-plan/` state. Three `_read_config()` call
  sites (`landing-strategy`, `validate-cmd`, `execute.worktree`) and `LANDING_LOCK`.
  - depends-on: 2.1
  - resolves-upstream: #100 (include)
- **Issue 2.3 (#107): SPEC then implement configurable plan roots as a consumer of that reader.**
  Resolve the import-time constraint explicitly — either hoist a minimal dependency-free reader
  above the constants (what the local patch does, generalized) or make the roots lazily
  resolved; the tradeoff is a wider call-site change for the lazy option. Then express
  `plans-root` / `incubator-root` through the canonical reader. Must preserve the local patch's
  good properties: defaults when unconfigured, malformed JSON tolerated at import.
  - depends-on: 2.2
  - resolves-upstream: #107 (include)
- **Issue 2.4 (#101): Point the change-validation seed at the canonical reader.**
  `change_validation.py:44` (`VALIDATE_CMD_CONFIG`) reads legacy-only; make it canonical-first
  with legacy fallback.
  - depends-on: 2.2
  - resolves-upstream: #101 (include)
- **Issue 2.5: Tier-1 unit tests for config precedence and root configurability.** Cases:
  canonical-only, legacy-only, both-present (canonical wins), neither (defaults), malformed
  JSON at import time, and non-default roots end-to-end through `init`. Tag each against the
  REQ ids from 2.2/2.3.
  - depends-on: 2.3, 2.4
- **Issue 2.6: Tier-2 mechanical drive under a sandboxed `HOME`.** `TESTING.md` requires this
  for manager-script changes and warns explicitly *"never trust the installed copy — it is the
  old, `rust-embed`-baked skill."* That warning is doubly pointed here, since a stale installed
  copy is this plan's whole subject — and under the self-modification policy the installed
  `yf-plan` stays stale for the entire execution. Drive the modified `plan_manager.py` verbs
  directly under a sandboxed `HOME`; do not hand-roll an interactive-agent smoke.
  - depends-on: 2.5

### Epic 3: Import yf-herdr as a first-class repo skill

- **Issue 3.1: SPEC-first — review and land `skills/yf-herdr/SPEC.md`.** Bring the
  hand-authored SPEC to repo discipline before any other import step, per AGENTS.md: renumber
  requirements to the **`REQ-HERDR-*`** prefix (consistent with the other per-skill SPECs) and
  add the living-amendment log.
- **Issue 3.2: Land the skill source with corrected frontmatter.** Copy `SKILL.md` / `README.md`
  into `skills/yf-herdr/`, and **drop `depends-on-skill: [herdr]`** — that field is in-repo
  names only and `herdr` is third-party. Keep `depends-on-tool: [herdr, uv]`. Express the
  relationship as a prose soft-dep, following yf-plan's `yf-change-validation` precedent.
  - depends-on: 3.1
- **Issue 3.3: Update the frozen parity golden.** Hand-edit
  `yf/src/testdata/install-parity.json`: add `yf-herdr` to `skill_group` (→ `utility`), to
  `group_members` / the `group:utility` closure, and give it its own closure entry. Do not run
  the deleted `install.py`. Verify `parity.rs` passes.
  - depends-on: 3.2
- **Issue 3.4: Update the architecture skill counts.** `web/content/pages/architecture.md`:
  18 → 19 skills, utility 6 → 7. Enforced by the `e-web-skill-counts` drift edge.
  - depends-on: 3.2
- **Issue 3.5: Author `web/content/skills/yf-herdr.md`.** Per the plan-036 hybrid convention
  (authored prose body; "At a glance", index, and `SKILL_NAV` stay generated) and VOICE.md.
  - depends-on: 3.2
- **Issue 3.6: Prove the import.** Full lint, 0-warning Pelican build, drift-check PASS over
  the new `skills/yf-herdr/*` and `web/content/skills/yf-herdr.md` glob matches, and `parity.rs`
  green.
  - depends-on: 3.3, 3.4, 3.5
- **Issue 3.7: Write the #110 partial split.** Update #110 to record precisely what this plan
  delivered and what remains: **delivered** — the `yf-herdr` skill surface (delegate an approved
  plan to a new herdr tab, observe it, mine deviations); **still open** — the `herdr agent *`
  fan-out primitive, i.e. coordinator loops dispatching to secondary full sessions instead of
  in-process subagents, which is what #110 actually proposes. Leave #110 **open**.
  - depends-on: 3.6
  - resolves-upstream: #110 (partial)

### Epic 4: Re-install from merged main and verify the objective

Runs after Epics 2 and 3 have merged. This is where the plan's central claim is tested — Epic
1's refresh predates the `#107` feature and `yf-herdr`, so it cannot have installed them.

- **Issue 4.1: Re-install all 19 skills from merged `main`, including `yf-plan`.** The
  self-modification policy's deferred refresh. Runs at a phase boundary with **no landing lock
  held**. This is the first point at which the installed `yf-plan` carries the canonical
  `.yf/plan/` state path.
  - depends-on: Epic 2, Epic 3
- **Issue 4.2: Final verification against the objective.** Re-run the `exp-01` three-pass
  comparison (excluding `__pycache__/`, `*.pyc`, `.DS_Store`). **Pass condition: the install
  stamp is the only remaining difference across every skill** — no hand-patched
  `plan_manager.py`, and `yf-herdr` present on both sides. This is the mechanical test of
  Success Criterion 1.
  - depends-on: 4.1
- **Issue 4.3: Confirm the preserved copies are redundant, then retire them.** Diff
  `~/yf-preserve-plan-037/` against the now-installed tree to prove nothing was lost, and
  record the result before removing the backup. Never remove it before 4.2 passes.
  - depends-on: 4.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: un-upstreamed work preserved
- Type: human
- Condition: the local `plan_manager.py`, its `.bak`, and the full `yf-herdr/` tree exist in a
  verified backup at `~/yf-preserve-plan-037/` before any installer run overwrites user scope.
- Test:
  ```bash
  test -f ~/yf-preserve-plan-037/plan_manager.py \
    && test -f ~/yf-preserve-plan-037/plan_manager.py.pre-incubator-root.bak \
    && diff -r ~/yf-preserve-plan-037/yf-herdr ~/.claude/skills/yf-herdr \
    && diff ~/yf-preserve-plan-037/plan_manager.py ~/.claude/skills/yf-plan/scripts/plan_manager.py
  ```
- Blocks: Issue 1.3
- Instructions: run Issue 1.2, then run the test above. It must exit 0 with no diff output.

### Capability Gate: config-tier semantics decided
- Type: human
- Condition: Issue 2.1's committed-vs-local decision is recorded at
  `docs/plans/plan-037-james-dixson-cab694/decisions/config-tier.md`.
- Test: `test -s docs/plans/plan-037-james-dixson-cab694/decisions/config-tier.md`
- Blocks: Issues 2.2, 2.3
- Instructions: settle whether `plans-root` / `incubator-root` are a shared-and-committed or
  local-only decision, and record the choice with its rationale at the path above.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| Risk | Mitigation |
|:--|:--|
| The installer overwrites the un-upstreamed patch and `yf-herdr` before they are captured. This is the only irreversible step in the plan. | Issue 1.2 + a hard capability gate ahead of Issue 1.3. `yf-herdr` is unstamped and exists nowhere else, so losing it means losing it permanently. |
| `exp-01`'s "safe to refresh" verdict is wrong for some file, and a real local edit is destroyed. | The verdict is evidence-based (exact blob match against history), not inferred. Issue 1.4 re-verifies after the refresh, and 1.2's backup covers the whole tree regardless. |
| #100's canonical-first change silently breaks operators still on the legacy dotfile. | Legacy stays a read fallback, never removed. Issue 2.5 tests the legacy-only and both-present cases explicitly. |
| The import-time constraint forces a wider refactor than expected, expanding Issue 2.3. | It is called out as the explicit subject of 2.3 with two named options rather than assumed away; the lazy-resolution option's cost (every call site) is known up front. |
| `yf-herdr` depends on a third-party `herdr` binary that CI does not have. | Its `SKILL.md` is gated on `HERDR_ENV=1` and should be inert; `depends-on-tool` declares the requirement. Issue 3.6's FULL-tier run over the merged tree is where this surfaces. Carried as an open risk, not a solved problem. |
| Scope creep from the adjacent `.yf/` issues (#102 and the rest of the canonical migration). | #102 is explicitly excluded; only its commit-semantics *question* is cross-referenced from Issue 2.1. Issue 1.1's "drift" branch files a follow-up rather than expanding this plan. |
| **Self-modification:** refreshing or editing `yf-plan` while `yf-plan` executes the plan. Epic 2 relocates `landing.lock` from `.yf/yf-plan/` to `.yf/plan/`, which Phase 6 holds across merge-back. | The self-modification policy: `yf-plan` is excluded from Epic 1's refresh and reinstalled only in Epic 4, after RECONCILE, with no lock held. Execution runs start-to-finish on one stable manager copy. |
| The plan completes but leaves user scope stale in a *new* way, because Epics 2–3 add things Epic 1 could not have installed. | Epic 4 exists specifically for this, and Issue 4.2 is the mechanical test of Success Criterion 1. Without Epic 4 the objective is unmet. |
| The plan executes on the stale `yf-plan`, so any behavior fixed by Epic 2 is unavailable during execution (including the stale `.yf/yf-plan/` state path). | Accepted knowingly as the safer trade. Recorded in the self-modification policy rather than discovered at execution time. |

## Success Criteria

1. **A fresh install from merged `main` reproduces the operator's working setup.** Measured by
   Issue 4.2: the `exp-01` three-pass comparison — excluding `__pycache__/`, `*.pyc`, and
   `.DS_Store` — reports the **install stamp as the only remaining difference**, across all 19
   skills.
2. `plan_manager.py` in user scope carries no hand-edit, because configurable
   `plans-root` / `incubator-root` is a repo feature reachable through canonical `.yf/` config.
3. `yf-herdr` installs from the repo like any other skill: present in `skills/`, in the parity
   golden, counted in `architecture.md`, with an authored web page.
4. #107, #100, and #101 are closed. #110 stays **open**, updated per Issue 3.7 with an explicit
   in/out split: skill surface delivered, `herdr agent *` fan-out primitive still open.
5. Full lint, 0-warning Pelican build, drift-check PASS, `parity.rs` green, and both TESTING.md
   tiers (Tier-1 unit + Tier-2 sandboxed-`HOME` drive) green over the merged tree.
6. One coarse upstream tracking issue for this plan, per the AGENTS.md convention.
7. The preserved backup at `~/yf-preserve-plan-037/` is proven redundant against the installed
   tree before being retired (Issue 4.3).

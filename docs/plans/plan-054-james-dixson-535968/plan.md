---
type: Plan
okf_spec: OKF-PLAN
id: plan-054-james-dixson-535968
author: james-dixson
created: '2026-08-26'
status: approved
deliverable_class: standard
fingerprint: 5de8e0829abea07c9b34e0aedf1101740a5a15b2b770ee461cbf886109c6a8ca
---
# Plan: Release readiness for yf v0.5.0: SKILL_DIR harness resolution, shipped silent-failure defects, changelog reconstruction, doc+website accuracy, and a pi/opencode regression

**ID:** plan-054-james-dixson-535968
**Author:** james-dixson
**Created:** 2026-08-26
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 5de8e0829abea07c9b34e0aedf1101740a5a15b2b770ee461cbf886109c6a8ca

## Objective
Release readiness for yf v0.5.0: SKILL_DIR harness resolution, shipped silent-failure defects, changelog reconstruction, doc+website accuracy, and a pi/opencode regression

## Motivation

`yf` has not been released since **v0.4.0** (2026-07-09). Since then **411 commits across 28
plans** (plan-026 → plan-053) have landed on `main`, including two entirely new shipped skills
(`yf-okf`, `yf-herdr`), a new top-level command surface (`yf harness tune`), and the single
largest capability in the project's history: **multi-harness provisioning** across `claude-code`,
`codex`, `opencode`, `pi` and `agents`.

None of that is reflected in the artifacts a user actually reads. `CHANGELOG.md` has received
**2 commits** in that window and its `Unreleased` section describes **plan-027 alone**. `README.md`
contains **zero** occurrences of `opencode`, `pi`, or `--harness`, and teaches a command spelling
`cli.rs` marks deprecated. The website asserts a formula count that is wrong (3 vs the 5 that
ship) and documents an install flow that omits a default-on step which **exits non-zero** without
a consent flag.

Worse, the operator has newly configured `pi` and `opencode` locally, and a measurement made
while scoping this plan shows that **skills deployed to those two harnesses cannot run**. `yf`
installs them to `~/.pi/agent/skills` and `~/.config/opencode/skills`, but the `SKILL_DIR`
resolver embedded in **19 files** (11 `SKILL.md`, 5 `yf-research` agent files, a test-harness README, and the two `yf-skill-authoring` templates the next skill is authored from) searches six roots and **neither destination is
among them**. On a pi-only machine every script-backed skill dies at
`ERROR: <skill> directory not found`; on a mixed machine it silently resolves to the
*claude-code* copy. The install reports success either way.

This plan makes the release honest: it fixes the resolution gap, closes the shipped
silent-failure defects, reconstructs the changelog, brings the in-tree docs and the website into
agreement with what ships, and — because the website **auto-publishes on tag push** and there is
no fix-it-afterwards window — verifies all of it before cutting **v0.5.0**.

## Scoping Decisions

| # | Decision | Choice | Rationale |
| :-- | :-- | :-- | :-- |
| D-1 | How to fix `SKILL_DIR` under pi/opencode | **`yf` owns resolution** — add a `yf skill-dir <name>` lookup. **AMENDED after EXP-001 (pass-1 C8): the `find` idiom is REPLACED, not kept as a fallback.** The fallback is a pure-bash existence loop over a cwd-inclusive superset of yf's own anchors | The binary already holds every harness destination in `harness_desc.rs`, so a sixth harness needs **zero** edits. The amendment is forced by measurement: **`find` exits 1 on a missing root even when it found the target**, masked by `\| head -1` — so retaining it would ship a resolver that fails under the `set -o pipefail` #203 proposes to mandate. |
| D-2 | Changelog reconstruction depth | **Curated by theme** — ~10 user-facing themes, each citing its plans; internal-only plans get one aggregate line | 28 plans is unreadable as release notes, and much of the range is process work with no user-observable surface. Themes stay honest without being an audit log. |
| D-3 | Release version | **0.5.0** | Consistent with the 0.x line. Critically, `cli.rs` promises the deprecated `yf skills` alias survives "until the next major release" — 1.0.0 would **obligate** removing it and `--surface` in this cycle, widening scope for no benefit. |
| D-4 | Scope of the harness regression | **Both tiers**: extend the existing `harness_cross_e2e.rs` mechanical suite **and** run a live-session walk in real `pi` and `opencode` | Every existing multi-harness assertion is a filesystem-path assertion under a fake `HOME`; `Command::new("pi")` appears **nowhere** in the repo. That gap is exactly what let D-1's defect ship. |
| D-5 | Stale "already delivered" issues | **Verify each deliverable, then close** — do not take the tracker at face value | Six issues (#119, #120, #122, #123, #124, #127) appear delivered. A release whose tracker misreports outstanding work is itself a docs defect. But "appears delivered" is a claim; each needs its deliverable checked against the issue's stated ask. |
| D-6 | The process/planning-quality backlog | **Deferred wholesale** — ~20 issues | None of them is observable by a user of the release. Mixing them in would triple the plan and delay a release whose entire point is user-facing accuracy. |
| D-7 | pi config tuning (#121) | **Not fixed — documented** | Pi's config surface is `[uncertain]` on a questionable-tier source only. Baking a guess into a released binary is strictly worse than a clean deferral. Release notes must state `--harness pi` tunes rules+skills only. |

## Non-goals

- **Not removing** the deprecated `yf skills` / `--surface` aliases (follows from D-3).
- **Not fixing** `bd`'s own defects (#211, #212, #213, #230, #202) — they are upstream of this repo.
- **Not building** the `yf-retrospective` skill (#145), the plan DSL (#192), or any new upstream backend (#51–#53).

## Upstream Issues

*The coarse tracker for plan-054 is filed at INTAKE (§4.5), not now, so it carries no issue
number yet and deliberately has no row here — a numberless row is dropped by
`parse_upstream_rows` and would assert an issue that does not exist.*

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #185 | doc_lint: upstream-cells-filled cannot distinguish a skipped triage from a measured-empty one | include | Blocks approval in ANY fresh repo with no upstream issues — a first-run blocker for every new user | 3.1 |
| #225 | plan_extract: a COLUMN-0 PARAGRAPH under an open issue is dropped silently | include | Silent plan-content loss at intake | 3.2 |
| #226 | plan_extract: a trailing declaration behind a LEADING code span yields no edge | include | Silent DAG-edge loss; touches a parsing branch, so needs care | 3.3 |
| #201 | change_validation.py: repeated --changed silently drops all but the last path | include | A green covering half a change-set, with no way to tell from the output | 3.4 |
| #195 | beads docs describe dependency types that installed bd 1.1.2 does not have | include | Ships actively misleading docs; labeled high | 3.5 |
| #203 | Exit-code discipline: five instruments report failure in output and success in $? | include | Includes `yf skills status` returning Ok(()) unconditionally — in the binary | 3.6 |
| #119 | Per-harness yf doctor/settings-drift axis for codex/opencode/pi | include | EXP-005: axes delivered and observed live. The close is GATED on Issue 4.7 correcting the doc that still asserts the deferral. The -008 half is retired as out of scope (`SPEC.md:1389-1391`); pi's settings axis rides on #121, which stays open | 6.2 |
| #120 | Codex project_doc_max_bytes block-size-budget check | include | EXP-005: the suspected multi-file residual did NOT survive scrutiny — the issue scopes to one file and REQ-YF-TUNE-027 records that as a chosen limitation. Clean close | 6.1 |
| #122 | web/yf-plan+yf-research: document each subagent and each workflow step in detail | include | Deliverable appears to exist (workflows.md, 268 lines). Verify against the ask, then close | 6.1 |
| #123 | web: 'Managed files' reference section | include | Deliverable appears to exist (managed-files.md). Verify against the ask, then close | 6.1 |
| #124 | web/concepts: 'Concepts: beads & the yf-beads-* skills' | include | Deliverable appears to exist (beads-concepts.md, 187 lines). Verify against the ask, then close | 5.6 |
| #127 | web/concepts: define idiomatic workflow terms | partial | EXP-005: RESCOPE, do NOT close — ten high-frequency terms are undefined, so the stated 'cold reader can decode the docs' criterion is unmet. 5.7 adds them | 5.7 |
| #231 | plan-053-james-dixson-4015d3 execution tracking | include | plan-053 is complete, deployed and reconciled; the tracker is the last artifact open | 6.1 |
| #154 | `yf harness tune --revert` deletes YOSHIKO_FLOW.md rather than restoring it | exclude | **Already CLOSED upstream** — so this is not a reopen. EXP-006 measured it **half-fixed and mis-located**: the revert half genuinely works (the REQ-YF-TUNE-029 sha guard fires), but the surviving loss happens at **tune**, which overwrites a pre-existing aggregate with no backup. Issue 2.2 fixes the adjacent symlink branch; 6.4 files a SUCCESSOR for the tune-time half rather than reopening a closed issue | |
| #121 | Pi config tuning re-verification (REQ-YF-TUNE-017) | partial | D-7: correct deferral, NOT fixed here. This plan adds the release-note statement that `--harness pi` tunes rules+skills only | 6.3 |
| #104 | web: prevent runaway Pelican devservers + add clean teardown | deferred | Local dev ergonomics only; never reaches published content | |
| #229 | redcheck.sh's YF_TREE default assumes plan-050's asset layout | include | Un-deferred at pass-1 C10: this plan's own capability gate depends on that harness, so its portability defect is in scope | 0.6 |
| #232 | Success-Criterion COMMANDS are never executed before approval | deferred | D-6 process class | |
| #224 | Success criteria using `grep -qv` are environment-dependent | deferred | D-6 process class | |
| #223 | bd mol pour / yf-plan intake: one plan issue poured TWICE | deferred | D-6 process class | |
| #189 | Six shipped scripts have no tests at all | deferred | D-6 process class; real risk, but not user-observable at release | |
| #230 | bd close REFUSES and EXITS 0 when the bead is blocked | deferred | Upstream `bd` defect, not ours to fix | |
| #192 | Evaluate a structure-first plan DSL | deferred | D-6; large speculative design | |

## Investigation Findings

**Investigation wisp:** `yf-wisp-pr8` — burn at pour (`bd mol burn yf-wisp-pr8 --force`).

### Experiment results

All six returned. Full write-ups in `findings/`. **Three refuted or corrected a scoping premise.**

| # | Question | Outcome |
| :-- | :-- | :-- |
| EXP-001 | `yf skill-dir` design + fallback | **D-1 CONFIRMED, and the runner-up option is now known unsafe.** `find` exits **1 on a missing root even when it found the target**, masked by `\| head -1`. Widening the root list guarantees a missing root on most machines, and #203 proposes mandating `set -o pipefail`. **19 consumers, not 11.** |
| EXP-002 | Live pi + opencode walk | **Both harnesses load, invoke and RUN yf skills end-to-end**, rule block reaches context, `uv run` works — pi with no config profile at all. **The defect reproduced live:** both resolved to the *claude-code* copy, so prose and scripts come from different trees. Under a pi-only HOME: `exit 1`. Both are headless-drivable, so this is Tier-2 automation, not a manual checklist. |
| EXP-003 | opencode `.json` vs `.jsonc` | **REFUTED.** opencode *merges*; yf's tune works today. Real defect is adjacent: `.jsonc` has **higher** precedence and today's agreement is coincidence, while the audit's read set is narrower than the harness's own. **The scoping hypothesis named the wrong module** — `drift.rs` never opens a config file. |
| EXP-004 | Changelog reconstruction | **D-2 CONFIRMED, but not via the assumed spine.** The SPEC amendment log misses **9** plans (not 7), is fragmented across five blockquote regions and is non-chronological. The usable spine is `index.md`'s summary line (28/28) + `plan_extract.py`. Only **59 of 183** upstream rows are `include`. |
| EXP-005 | Stale-issue verification | **D-5's METHOD vindicated, its EXPECTED OUTCOME wrong.** Not six clean closes: **four** clean, **#119 gated on a doc fix**, **#127 must NOT be closed** — its own "cold reader can decode the docs" criterion is measurably unmet. #120's suspected residual was not real. |
| EXP-006 | Symlinked-surface revert | **Reverting today is SAFE**, but `--revert`'s delete branch unlinks the **symlink** rather than the content — while reporting success. **The margin is one prose line.** #154 is half-fixed; the surviving loss happens at **tune**, not revert. |

**New defects discovered, beyond the scoped set:** hardcoded relative `.claude/skills/...`
invocations in **two** skills (14 sites) that bypass `SKILL_DIR` entirely; **`allowed-tools` is
claude-only** (0 occurrences in either harness's bundle, 10 shipped `SKILL.md` files carry it);
yf ignores `XDG_CONFIG_HOME` / `CODEX_HOME` / `OPENCODE_CONFIG_DIR`; pi's project-trust gate is
unexercised; two plans amended root `SPEC.md` with no amendment-log bullet.

**Amendments to the scoping decisions.** D-2 and D-4 stand as chosen. **D-1's mechanism is AMENDED** (pass-1 C8): `yf skill-dir` is adopted as chosen, but the `find` fallback it originally named is replaced by a pure-bash existence loop, because `find`'s exit code is unusable. D-3 is untouched. D-5 is
amended to three outcomes (close · close-after-fix · rescope). D-7 stands. The opencode work is
retargeted from "fix a silent no-op" to "widen the audit read set", against `audit.rs` and
`doctor/checks.rs` rather than `drift.rs`.

### Approach hypothesis

Six epics, SPEC-first: (0) SPEC amendments for the new `skill-dir` surface and the exit-code
contract · (1) the `SKILL_DIR` fix + `harness_cross_e2e` extension · (2) the shipped
silent-failure defects · (3) in-tree docs incl. the themed changelog · (4) website + the two
missing drift edges · (5) live regression, issue reconciliation, version bump, tag.

**The release cut itself is the last act and is operator-authorized** — pushing a `v0.5.0` tag is
an outward-facing, irreversible write that also auto-publishes the website.

## Approach

**SPEC-first, seven epics, in dependency order.** Epic 0 lands every requirement before its
implementation. Epic 1 fixes the resolution gap the release cannot ship without. Epic 2 builds
the regression that would have caught it. Epic 3 closes the shipped silent-failure defects.
Epics 4-5 make the docs and the website honest. Epic 6 cuts the release.

Three principles the findings forced:

- **Replace the `find` idiom, do not extend it.** EXP-001 measured `find` exiting **1 on a
  missing root even when it found the target**, masked by `| head -1`. Adding the pi/opencode
  roots guarantees a missing root on most machines, and #203 proposes mandating `set -o
  pipefail`. The widen-the-list option is not a smaller version of this fix; it is an unsafe one.
- **Generate the resolver into all 19 consumers.** Two of them are the `yf-skill-authoring`
  templates the next skill is authored from. Hand-editing 19 files is how this recurs.
- **The website publishes on tag push.** `web-deploy.yml` chains off a successful Release run,
  so Epic 5 is a precondition of Epic 6, not a follow-up.

## Epics

### Epic 0: SPEC-first amendments and the pre-fix baseline
- Issue 0.1: Record the pre-fix RED baseline for **every control AND every `check-*.sh` criterion instrument**, re-measured, before any edit. **This is the structural fix for the class three passes caught by hand** — SC7 already true, eight criteria green on the unfixed tree, a zero-match `cargo test` filter exiting 0. Each was found by a reviewer, not by a gate. Spot-checked feasible: essentially every check asserts a post-fix state (no `v0.5.0` tag, crate at `0.4.0`, README with zero occurrences of `opencode`, 32 hardcoded paths present, 10 `SKILL.md` carrying `allowed-tools`), so they are red today. Any check that legitimately holds now goes on a short explicit allowlist **with its reason recorded**. The allowlist covers **check SCRIPTS**, not criteria — SC16 is a legitimately-holds criterion but invokes `change_validation.py` directly with no file under `assets/checks/`, so it is outside `verify-red-checks`' domain entirely rather than an allowlist member. The one known member is **`check-harness-smoke.sh`**, which 2.5 authors downstream of the RED gate and is therefore structurally unbaselineable; its red evidence is 6.7's live transcript instead. **Runs AFTER the harness and fixtures exist** — a baseline cannot be recorded by an instrument that has not been built
  - depends-on: 0.7, 0.8
- Issue 0.2: Add **`REQ-YF-CLI-005`** for `yf skill-dir` — top-level verb, 0/1/2 exit contract, and an explicit sentence that the predicate is **existence-only** (no marker/integrity verification). Marked `(testable)`, so its tagged test lands in the same change-set
- Issue 0.3: Add **`REQ-YF-TUNE-030`** for `settings_read_layers` — the audit read set is decoupled from the single write target. Marked `(testable)`
- Issue 0.4: Amend **`REQ-YF-TUNE-022`** for symlink-aware revert; record that the delete branch must not unlink a symlink
- Issue 0.5: Add **`REQ-YF-EMBED-006`** recording the `allowed-tools` portability decision — claude-only, not a cross-harness scoping mechanism, since neither pi nor opencode reads it
- Issue 0.6: Adopt plan-053's control harness into `assets/` — `redcheck.sh`, an authoritative `controls.txt`, and `fixtures/`; split `assets/checks/` (criterion-only, `check-` prefix) from `assets/fixtures/` (red-to-green `ctl-` controls) per plan-053 pass-4 C44; fix the `YF_TREE` default so it does not assume plan-050's layout. **Two constraints are load-bearing and were measured, not assumed.** (a) `_derive_manifest` greps `plan.md` with the ANCHORED pattern `ctl-[0-9]{3}-[a-z-]+`, so **every control name must carry exactly three digits and no further digit** — a name of the form `ctl-<NNN>-column<digit>-paragraph` truncates at the embedded digit, and a name with no number is invisible entirely. **This clause deliberately states the rule rather than quoting a counter-example**: the derivation greps `plan.md` itself, so a literal non-conforming control name written here — even inside an explanation of why it is wrong — is scraped as a real control and breaks the very check it documents. Plan-local controls with no upstream issue use the reserved **9xx** range, documented in `controls.txt`'s header. (b) The adopted harness ships **no `verify-manifest` verb** — its verbs are `record-red`, `assert-distinguishes`, `verify-red-all`, `verify-all` — so 0.6 **adds** `verify-manifest` as a standalone entry point onto the existing `_derive_manifest` function. (c) **A `check-*.sh` can NEVER appear in `controls.txt`** — `_derive_manifest` derives that set with the `ctl-` pattern and 0.6 keeps `assets/checks/` deliberately outside it — so `verify-red-all` structurally cannot see the 28 criterion instruments 0.1 is scoped to. 0.6 therefore **adds a second verb, `verify-red-checks`**, iterating `assets/checks/` minus 0.1's allowlist and asserting each has a recorded non-zero pre-fix observation. **It must also extend the WRITE side**: measured at source, `cmd_record_red` gates on `_in_manifest`, a `grep -qxF` against `controls.txt`, so `record-red` on a `check-*.sh` hard-fails and writes nothing. Add a sibling `record-red-check` (or relax the gate to directory membership for `assets/checks/` entries) — a verifier with no recorder reads an empty set. Without both halves C1's obligation is stated but never executed
  - resolves-upstream: #229 (include)
- Issue 0.7: Author the fixtures for every named control — `ctl-201-changed-append`, `ctl-203-exit-discipline`, `ctl-902-resolver-isolated`, `ctl-225-columnzero-paragraph`, `ctl-226-leading-code-span`, `ctl-185-empty-triage`, `ctl-154-symlink-revert`, `ctl-901-opencode-read-layers` — each exiting 0 iff its asserted behaviour holds
  - depends-on: 0.2, 0.3, 0.4, 0.5, 0.6
- Issue 0.8: Author **every** criterion check script under `assets/checks/` — the set is derived from `plan.md`, never hardcoded, because a literal count is itself a drift defect (the class pass-1 C17 flagged in SC12). `check-harness-smoke.sh` is authored by Issue 2.5; 0.8 covers the remainder. **`grep -qv` is banned as a criterion primitive** — measured, it exits 0 whenever any line lacks the pattern, so on a multi-line file it cannot fail (#224)
  - depends-on: 0.2, 0.3, 0.4, 0.5, 0.6
- Issue 0.8a: **Verify the GREEN half is complete** — every control carries BOTH a `record-red` non-zero record and an `assert-distinguishes` zero record. Without it `verify-all`, SC2b's command, can never pass. **The obligation itself lives in each fix issue below, not here**: an executor working Issue 3.4 reads 3.4, so stating it only in this issue would repeat the wrong-place defect pass 3 raised
  - depends-on: 0.7, 1.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.4, 3.6
- Issue 0.9: Verify every criterion command that names an `assets/` path resolves. Derive the referenced set by grepping `plan.md`, then assert **referenced ⊆ present** — directional, excluding bare directory refs and `controls.txt` — so an added criterion cannot silently outrun its script while a deliberately-unreferenced fixture does not fail the check
  - depends-on: 0.7, 0.8, 2.5

### Epic 1: SKILL_DIR resolution across all five harnesses
- Issue 1.1: Implement `yf skill-dir <name>` reusing `dest::skills_dir_for_anchor` over `harness_desc::DESCRIPTORS`; user then git-root then cwd anchors; apply pi's `NameTransform`; dedupe the shared `codex`/`agents` path **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-902-resolver-isolated.sh ctl-902-resolver-isolated` to record this control's GREEN half** (SC2b).
  - depends-on: 0.2
- Issue 1.2: Unit tests tagged to the new REQ — resolution order, pi transform, dedupe, not-found to 1, could-not-run to 2
  - depends-on: 1.1
- Issue 1.3: Add the SKILL_DIR block as an `EmittedRegionAsset` in `_shared/sync.py`; insert region markers into every consumer and regenerate. **The set is DERIVED, never enumerated** — `grep -rlE 'SKILL_DIR' skills/` partitioned into files that ASSIGN it and files that only USE it — because an enumerated set was already measured incomplete. It covers: the 19 files that already assign it; the four markdown skills (`yf-markdown-lint`, `-format`, `-pdf`, `-html`), which carry ZERO `SKILL_DIR` occurrences and into which 1.5 substitutes `${SKILL_DIR}`; and **`yf-diagram-authoring/SKILL.md` (8 uses) and `yf-skill-authoring/SKILL.md` (4 uses), which USE `${SKILL_DIR}` and ASSIGN IT NOWHERE** — shipped skills that cannot resolve their own scripts on any harness today, a strictly worse instance of the defect this epic exists to fix. **Also in scope: three skill READMEs that use `${SKILL_DIR}` in runnable blocks and assign it nowhere** — `yf-beads-hygiene` (7 uses), `yf-diagram-authoring` (7) and `yf-beads-init` (4), 18 further sites of the same class. Agent files that declare `SKILL_DIR` as a caller-supplied *input* (`yf-okf/agents/assessor.md`, `yf-plan/agents/coordinator.md`, `yf-beads-authoring/agents/reviewer.md`) are deliberately OUT of scope and recorded as such. **`EmittedRegionAsset.emit` is a ZERO-ARG `Callable`**, so this needs a skill-name-parameterized emitter (a default-arg closure per consumer), not 19 copies. **Three of the 19 are prose ABOUT the idiom** — the two `yf-skill-authoring` templates and the test-harness README — and must be emitted in their placeholder form, not verbatim
  - depends-on: 1.2
- Issue 1.4: Add a `_shared/test_sync.py` case for the new emitted asset so `sync.py --check` is the standing anti-drift gate
  - depends-on: 1.3
- Issue 1.5: Replace every hardcoded relative `.claude/skills/…/scripts/…` invocation with `${SKILL_DIR}`. **The set is DERIVED, not counted** — `grep -rlE '\.claude/skills/[A-Za-z0-9_-]+/scripts/' skills/` — because both prior figures were wrong (14, then 16). Re-measured at pass 3: **32 sites across 8 files in FOUR skills** — `yf-markdown-format` 11, `yf-markdown-pdf` 10, `yf-markdown-html` 8, `yf-markdown-lint` 3. Depends on 1.3 having given all four a resolver block first. Also fix `skills/yf-markdown-lint/README.md:23`, which names `~/.claude/skills/markdown-lint`, the **pre-`yf-` skill name**
  - depends-on: 1.3
- Issue 1.6: Tier-2 test — a `mktemp -d` HOME seeded with **only** the pi root, then only the opencode root, asserting `SKILL_DIR` resolves, and a third arm with `yf` absent from `PATH` asserting the bash fallback resolves the same directory
  - depends-on: 1.3, 1.5
- Issue 1.7: Prefer the harness-provided base directory where the harness supplies one — opencode passes `Base directory for this skill:` and pi tracks a per-skill `baseDir`. This is EXP-002's fix for the **cross-tree skew** (prose from one tree, scripts from another); Epic 1's other issues fix only the not-found half **Mechanism, stated because EXP-002 warns a bash snippet cannot portably learn its own location:** the emitted block is env-var-first (`SKILL_DIR="${SKILL_DIR:-$(yf skill-dir …)}"`), so any harness exporting it wins. **opencode supplies the base directory as PROSE in the system prompt, not an env var**, so its path is an instruction to the model rather than a scripted lookup — recorded as a known asymmetry, not papered over.
  - depends-on: 1.3
- Issue 1.8: Act on the `allowed-tools` decision across the 10 shipped `SKILL.md` files that carry it — neither pi nor opencode reads it
  - depends-on: 0.5

### Epic 2: the harness regression that would have caught it
- Issue 2.1: Extend `harness_cross_e2e.rs` — pi name-transform round-trip through install, pi config sub-op returns `Deferred` with no `config` key in its manifest, codex budget at 32768-no-config vs 65536-tuned, repeat-tune idempotence and `--revert` for all five
  - depends-on: 0.4
- Issue 2.2: Fix the symlink delete branches in `revert.rs` — write through the link rather than unlinking it; drop the delete-when-empty optimization for symlinked paths **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-154-symlink-revert.sh ctl-154-symlink-revert` to record this control's GREEN half** (SC2b).
  - depends-on: 0.4
- Issue 2.3: Add a symlink variant to `harness_cross_e2e.rs` covering both delete branches. **The `#[test]` function is named `revert_through_symlink_preserves_link_and_clears_block`** — SC9 names the same string, so criterion and authoring issue cannot drift apart
  - depends-on: 2.2
- Issue 2.4: Add the `#[test]` function `opencode_read_layers_surface_shadowed_keys` alongside implementing `settings_read_layers` in `profile.rs`, expand `SettingsDriftCheck::from_env` in `doctor/checks.rs` and the read-back in `audit.rs`, plus a tune-time shadow warning naming the shadowed keys. **NOT `drift.rs`** — EXP-003 measured that it never opens a harness config file **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-901-opencode-read-layers.sh ctl-901-opencode-read-layers` to record this control's GREEN half** (SC2b).
  - depends-on: 0.3
- Issue 2.5: Headless smoke per harness — assert a yf skill name is listed, a rule-block-only fact is quoted back, and `plan_manager.py list --json-output` parses
  - depends-on: 1.6
- Issue 2.6: Add named-target rows to `CHANGE-VALIDATION.md` for `harness_cross_e2e` and the headless smoke, with trigger globs for `yf/src/cmd/harness/**` and `yf/profiles/**`
  - depends-on: 2.1, 2.3, 2.5

### Epic 3: shipped silent-failure defects
- Issue 3.1: Fix `doc_lint`'s `upstream-cells-filled` so a measured-empty triage is distinguishable from a skipped one **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-185-empty-triage.sh ctl-185-empty-triage` to record this control's GREEN half** (SC2b).
  - depends-on: 0.1
  - resolves-upstream: #185 (include)
- Issue 3.2: Report a column-0 paragraph under an open issue in `unparsed[]` rather than dropping it **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-225-columnzero-paragraph.sh ctl-225-columnzero-paragraph` to record this control's GREEN half** (SC2b).
  - depends-on: 0.1
  - resolves-upstream: #225 (include)
- Issue 3.3: Fix the leading-code-span case so a real trailing declaration yields its edge, without widening parsing to manufacture phantom edges **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-226-leading-code-span.sh ctl-226-leading-code-span` to record this control's GREEN half** (SC2b).
  - depends-on: 3.2
  - resolves-upstream: #226 (include)
- Issue 3.4: Give `--changed` `action="append"` so repeated flags accumulate **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-201-changed-append.sh ctl-201-changed-append` to record this control's GREEN half** (SC2b).
  - depends-on: 0.1
  - resolves-upstream: #201 (include)
- Issue 3.5: Correct the beads dependency-type documentation to the types installed `bd` actually accepts
  - depends-on: 0.1
  - resolves-upstream: #195 (include)
- Issue 3.6: Give `yf skills status` a real exit code and sweep the other instruments named in the issue **On completion run `redcheck.sh assert-distinguishes assets/fixtures/ctl-203-exit-discipline.sh ctl-203-exit-discipline` to record this control's GREEN half** (SC2b).
  - depends-on: 0.1
  - resolves-upstream: #203 (include)

### Epic 4: in-tree documentation
- Issue 4.1: Write the throwaway scaffolder over `plan_extract.py --json` plus the 28 `index.md` summary lines, emitting per-theme headings with `include`-only issue rows
- Issue 4.2: Reconstruct `CHANGELOG.md` as the themes; fold the existing 41-line `Unreleased` content into T10 and T1; read the 39 non-plan commits for the ~8 user-facing ones. **Include a Deprecations section** — `yf skills` to `yf harness skills` and `--surface` to `--harness` — since D-3's whole version choice rests on those aliases surviving
  - depends-on: 4.1
- Issue 4.3: Rewrite the README install and harness sections — the canonical `yf harness skills <verb>`, the five-harness matrix, `--harness`, and the ~16 undocumented flags **Asserted strings:** `README.md` contains `harness skills`, `opencode`, `pi` and `--harness` — each measured at ZERO occurrences today.
- Issue 4.4: Correct `README.md`'s claim that preflight repairs the beads config; `--repair` is opt-in and the default is read-only **Asserted string:** `README.md` no longer claims preflight repairs the beads config by default, and names `--repair` as opt-in.
  - depends-on: 4.3
- Issue 4.5: Add `docs/README.md` as a navigable index covering the diagrams and the four research reports **Asserted string:** `docs/README.md` exists and links `docs/diagrams/` and all four `docs/research/00N-*` bundles.
- Issue 4.6: Refresh `docs/yf/preflight-contract.md` — `SCAFFOLD_VERSION` 1 to 3, the `/.beads/formulas/` anchor, and the missing `REQ-YF-PRE-010`/`-011`/`-004a` **Asserted strings:** the file names `SCAFFOLD_VERSION: i64 = 3` (measured: it says 1, `preflight.rs:49` says 3) and each of `REQ-YF-PRE-010`, `-011`, `-004a`.
- Issue 4.7: Correct `docs/recommended-settings.md` — the per-harness drift axis is shipped, not deferred; this gates the #119 close **Asserted string:** the file no longer contains `there is no automated drift gate for these harnesses yet`.
- Issue 4.8: Rename the project in `CLAUDE.md` from `beads-skills` to yoshiko-flow **Asserted string:** `CLAUDE.md` contains no occurrence of `beads-skills`.

### Epic 5: website accuracy
- Issue 5.1: Correct `formulas.md` from three formulas to the five that ship, and document the aspect / cook-time weaving model
- Issue 5.2: Document the install-time sync on `install.md` — default-on, `--no-sync`, and the `--allow-permissions-write` consent gate that exits non-zero without it **Asserted strings:** the page contains `--no-sync` and `--allow-permissions-write` — both measured at ZERO occurrences site-wide today.
- Issue 5.3: Replace the deprecated `yf skills install` spelling across `lifecycle.md`, `architecture.md`, `usage.md` and `cards/05-embedded.md` **The set is DERIVED** (`grep -rl 'yf skills install' web/`), not enumerated — measured at **seven** files, three beyond the drafting list: `pages/{lifecycle,architecture,usage,install}.md`, `cards/05-embedded.md`, **`images/lifecycle.d2`** (a diagram SOURCE whose rendered PNG would otherwise keep the deprecated spelling, so it must be re-rendered), and **`plugins/skill_pages.py:242-243`** — a **GENERATOR**, which emits the deprecated spelling into *every* generated skill page and is the highest-leverage site of the seven. **Asserted string:** `grep -rl 'yf skills install' web/` returns nothing.
- Issue 5.4: Correct `architecture.md`'s two-surface model to five harnesses and add `harness tune`, `migrate` and `self` to its kernel-jobs list **Asserted strings:** the page names all five harness ids and each of `harness tune`, `migrate`, `self` (measured: `architecture.md:19` still says `claude` or `agents`).
- Issue 5.5: Fix `workflows.md`'s nine-versus-ten status-count contradiction **Asserted string:** the page contains no occurrence of `nine status values` (measured present at `workflows.md:122`).
- Issue 5.6: Fix the six-versus-five `yf-beads-*` miscount in `beads-concepts.md` **Asserted string:** `beads-concepts.md` says `five` yf-beads-* skills, matching the 5 that ship.
  - resolves-upstream: #124 (include)
- Issue 5.7: Add the ten measured undefined terms to `glossary.md`
  - resolves-upstream: #127 (partial)
- Issue 5.8: Add drift edges covering `formulas.md` to the shipped formulas and `install.md`/`harness-tune.md` to `cli.rs` plus `yf/profiles/`
  - depends-on: 5.1, 5.2
- Issue 5.9: Bump `YOSHIKOFLOW_RELEASE` in `web/pelicanconf.py` in lockstep with the crate version
  - depends-on: 6.5

### Epic 6: cut the release
- Issue 6.1: Close #120, #122, #123 and the #231 tracker with comments recording the delivered mechanism
  - resolves-upstream: #120 (include), #122 (include), #123 (include), #231 (include)
- Issue 6.2: Close #119 with a comment recording that the -008 half was retired as out of scope and that pi's settings axis rides on #121
  - depends-on: 4.7
  - resolves-upstream: #119 (include)
- Issue 6.3: Comment on #121 recording that pi config stays deferred and the release notes say so
  - resolves-upstream: #121 (partial)
- Issue 6.4: File the new defects this plan discovered but does not fix — the opencode/codex XDG and env-var directory axis, codex multi-file concatenation, pi's project-trust gate, the two plans that amended root SPEC with no amendment-log bullet, the amendment log's fragmentation across five regions, and EXP-006's `KeptModified` whitespace defect. **File a SUCCESSOR to the closed #154** covering its surviving tune-time half — `tune` must refuse to overwrite, or back up, a pre-existing aggregate yf did not author
  - depends-on: 3.6
- Issue 6.5: Bump `yf/Cargo.toml` to 0.5.0, refresh `Cargo.lock`, and rename `Unreleased` to the v0.5.0 heading in the same change-set
  - depends-on: 4.2
- Issue 6.5a: Merge the execute branch to `main` and confirm the merged tree is what every later issue validates
  - depends-on: 0.8a, 0.9, 1.4, 1.6, 1.7, 1.8, 2.4, 2.6, 3.1, 3.3, 3.4, 3.5, 3.6, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.5, 6.7a
- Issue 6.6: Run the FULL validation tier and a complete `yf-drift-check` sweep over all **50 declared edges** (52 after Issue 5.8) on the merged tree. **Measured: `DRIFT-CHECK.md` declares 50 UNIQUE edge ids** — the 100 figure used while drafting double-counted, because §2 and §3 each restate the same 50
  - depends-on: 5.9, 6.5a
- Issue 6.6a: Deploy the fixed skills with `./target/debug/yf harness skills install` so the live regression reads the NEW tree. **Force a re-stamp first** — 6.5a's merge commit moves `HEAD` without touching any `cargo:rerun-if-changed` path, so an incremental rebuild can legitimately carry the pre-merge hash and fail SC21 for a non-defect (the staleness AGENTS.md documents). **Debug reads `skills/` from disk**; a release `yf self install` mid-execution is forbidden by AGENTS.md
  - depends-on: 6.6
- Issue 6.7: Run the live pi and opencode regression against the DEPLOYED tree and record the transcript, the harness versions, and which tree each harness read
  - depends-on: 6.6a
- Issue 6.7a: Write the release notes — pi tunes rules and skills only; `--revert` edits the targets of symlinked surfaces and will leave a dotfiles repo dirty by design
  - depends-on: 6.3, 6.4
- Issue 6.8: Push the `v0.5.0` tag
  - depends-on: 6.1, 6.2, 6.3, 6.4, 6.7, 6.7a

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: RED observed before any fix
- Type: auto
- Condition: every control AND every `check-*.sh` criterion instrument has a dated RED record naming a non-zero, non-2 exit code observed on the pre-fix tree, or sits on 0.1's allowlist with a recorded reason
- Test: bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-red-all && bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-red-checks
- Blocks: 1.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.4, 3.6
- Instructions: run each control's fixture AND each `assets/checks/` instrument against the pre-fix tree and record the observed exit code; the Test runs both verbs

### Capability Gate: live harness regression green
- Type: human
- Approvers: operator
- Condition: the headless smoke passes under both pi and opencode against the DEPLOYED tree, including a resolver check under an isolated HOME. **An INCONCLUSIVE blocks** — this is the last gate before an irreversible, auto-publishing tag, so a gate that tolerates its own failure is not a gate
- Blocks: 6.8
- Instructions: run the Issue 2.5 smoke against the deployed tree in both harnesses and present the transcript

### Capability Gate: release authorization
- Type: human
- Approvers: operator
- Condition: the operator authorizes pushing the v0.5.0 tag, which is irreversible and auto-publishes the website
- Blocks: 6.8
- Instructions: confirm the changelog, the version bump and the site content are correct, then authorize the tag push

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The tag push is irreversible and auto-publishes the site.** A wrong changelog or a stale page ships with no fix-it-after window | high | Epic 5 is a hard predecessor of 6.8; the release-authorization gate is human; 6.6 sweeps all 50 declared drift edges before the tag |
| R2 | **Issue 3.3 changes a PARSING branch**, the class that can manufacture phantom edges. `REQ-DATA-063` exists so a `depends-on:` in a code span yields no edge | high | 3.3 depends on 3.2 so the capture fix lands first; the control must assert both that the real edge appears AND that a code-span declaration still yields none |
| R3 | **The changelog is reconstructed from tables where only 59 of 183 rows are `include`.** A mechanical pass would emit 37 `exclude` and 30 `deferred` as shipped work | high | 4.1 filters on `include` and routes `partial` to a manual queue; 4.2 is curated by hand, not generated |
| R4 | **19 files carry the resolver and 2 are the templates the next skill is authored from.** A hand-edit pass that misses them regenerates the defect | med | 1.3 generates all 19 from one source; 1.4 makes `sync.py --check` the standing gate |
| R5 | **The generated-resolver change touches every skill at once.** A defect in the emitted block breaks the whole fleet simultaneously | med | 1.2 unit-tests the resolver before 1.3 emits it; 1.6 proves it under an isolated HOME per harness |
| R6 | **`yf skill-dir` and the bash fallback could use different predicates**, and the disagreement would be invisible | med | 0.2 makes existence-only a SPEC requirement, not a convention |
| R7 | **Six issues are being closed on a verification this plan performs itself.** A wrong verdict closes an unmet issue | med | EXP-005 already moved two of six; 6.2 is gated on 4.7, and #127 was moved out of the close batch into 5.7 |
| R8 | **The live regression depends on a local model gateway and two third-party binaries** whose versions are not pinned by this repo | med | 6.7 records the transcript and the versions. The gate is **human**, and an INCONCLUSIVE **blocks** — it is the last gate before an irreversible, auto-publishing tag, so the operator adjudicates rather than the plan tolerating its own failure |
| R9 | **plan-053 shipped a criterion grammar error that returned INCONCLUSIVE with zero rows parsed.** The same mistake here silently voids the completion re-check | low | **Already discharged by measurement, before approval:** `recheck-criteria` parses **41 of 41** rows, with zero multi-valued clauses. Re-measured at every review pass |
| R10 | **Reverting on the operator's machine leaves a tracked dotfiles repo dirty**, and the delete-branch hazard is one prose line away | low | 2.2 fixes the branch; the release note states the by-design dirtying |
| R11 | **The `find` fallback is REPLACED, so a machine where `yf` is absent from `PATH` has no resolver at all** unless the bash loop is a correct superset. Version skew compounds it — new skills calling `yf skill-dir` against a pre-0.5.0 binary | high | SC4b asserts CONTAINMENT (every path yf resolves, the fallback resolves too); 1.6's third arm runs with `yf` absent; the measured stale-binary behaviour (exit 2, empty stdout) makes the snippet safe to deploy before the binary |
| R12 | **The tag could be pushed with most of the plan open.** At pass 1 only 24 of 48 issues were ancestors of 6.8 | high | 6.6 now depends on every epic leaf and 6.8 on 6.1-6.4, 6.7 and 6.7a |
| R13 | **The plan is large — 58 issues, 41 criteria and 37 shell scripts to author (28 `check-*.sh` + 8 fixtures + `redcheck.sh`) — and ends in an irreversible tag.** Pass 2 proposed Epic 3 as the seam; pass 4 re-measured what that would relieve: **~7 of 37 scripts**, not the majority. **The size is in EPIC 0**, which carries the whole evidence layer in 10 issues — not in Epic 3 | med | **RESOLVED by operator decision (2026-08-26, at the pass-5 escalation): Epic 3 stays IN SCOPE.** Decided against the corrected figures — a split leaves Epic 0 untouched while forcing the release notes to describe six defects as outstanding. The seam stays recorded so a mid-execution split is still cheap if execution stalls |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every new `REQ-*` this plan lands is present in `SPEC.md`, marked `(testable)`, and named by a tagged test. **The check asserts the SPECIFIC new ids from 0.2–0.5**, so it is RED on today's tree and can only go green through this plan's work. Neither the portability audit nor bare `coverage.rs` measures this — `coverage.rs` proves a test *names* a REQ id and has no temporal dimension at all | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-req-coverage.sh` → exit 0 | 0.2, 0.3, 0.4, 0.5 |
| SC2 | Every control was observed RED on a fixture before its fix | `bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-red-all` → exit 0 | 0.1 |
| SC2c | **Every `check-*.sh` criterion instrument was observed RED on the pre-fix tree**, or is on 0.1's allowlist with a recorded reason. Without this the 28 instruments are trusted on authorship alone — the condition that let one vacuous criterion escape in each of four consecutive passes | `bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-red-checks` → exit 0 | 0.1 |
| SC2b | Every control was then observed GREEN, as a distinct record | `bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-all` → exit 0 | 0.8a, 6.6 |
| SC3 | **`SKILL_DIR` resolves under a HOME containing ONLY the pi root, and only the opencode root** | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-resolver-isolated.sh` → exit 0 | 1.1, 1.2, 1.6 |
| SC4 | The six-root `find` idiom survives at **zero** sites under `skills/` | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-no-legacy-find.sh` → exit 0 | 1.3 |
| SC4b | **CONTAINMENT: for every anchor `yf skill-dir` can resolve, the fallback resolves the same path.** Stated as containment, not equality — D-1's fallback is a cwd-inclusive SUPERSET, so it legitimately resolves paths yf's anchors do not, and an equality assertion would be false by construction. The check invokes `yf` by absolute path while keeping it off `PATH` for the fallback arm | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-fallback-superset.sh` → exit 0 | 1.1, 1.6 |
| SC5 | **Every** consumer is generated, and a hand-edit to any one of them fails the check. The expected count is **derived, never embedded** — a literal in a criterion or a filename is the drift defect 0.8 bans | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-sync-emits-all.sh` → exit 0 | 1.3, 1.4 |
| SC6 | No `SKILL.md` or skill `README.md` invokes a script by a hardcoded relative `.claude/skills/` path | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-no-hardcoded-skillpath.sh` → exit 0 | 1.5 |
| SC7 | A code-span `depends-on:` still yields **no** edge after the 3.3 parsing change — the regression guard against 3.3 overreaching | `bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-226-leading-code-span.sh` → exit 0 | 3.3 |
| SC7b | **A real trailing declaration behind a leading code span NOW YIELDS its edge** — 3.3's positive, which SC7 alone cannot establish because SC7 is already true on the unfixed tree | `bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-226-leading-code-span.sh --positive` → exit 0 | 3.3 |
| SC8 | Repeated `--changed` accumulates rather than dropping all but the last | `bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-201-changed-append.sh` → exit 0 | 3.4 |
| SC9 | `--revert` through a symlink preserves the link and clears the block from the target. **The check asserts the test RAN** (`1 passed`), because a zero-match `cargo test` filter exits 0 — measured | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-cargo-test-ran.sh revert_through_symlink_preserves_link_and_clears_block` → exit 0 | 2.2, 2.3 |
| SC10 | The opencode audit reads every layer opencode itself reads, so a shadowing `.jsonc` is reported | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-cargo-test-ran.sh opencode_read_layers_surface_shadowed_keys` → exit 0 | 2.4 |
| SC11 | The changelog's released heading matches the crate version, and both are 0.5.0 | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-version-agrees.sh` → exit 0 | 6.5, 5.9 |
| SC12 | Every theme in the changelog cites the plans it covers, and every one of the 28 plans is covered by exactly one theme | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-themes-present.sh` → exit 0 | 4.1, 4.2 |
| SC13 | The README documents the canonical `yf harness skills` form and names all five harnesses | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-readme-harness.sh` → exit 0 | 4.3 |
| SC14 | The website's formula count equals the number of `*.formula.toml` files under `skills/` — the staged copies under `.beads/formulas/` are excluded | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-formula-count.sh` → exit 0 | 5.1 |
| SC15 | The glossary defines every term the ten-term measurement found undefined | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-glossary-terms.sh` → exit 0 | 5.7 |
| SC16 | The FULL validation tier passes over the merged tree | `uv run skills/yf-change-validation/scripts/change_validation.py run --tier full` → exit 0 | 2.6, 6.6 |
| SC17 | Every drift edge scoped to a changed path passes on the merged tree | manual: `yf-drift-check` is a prose/LLM judgement with no runnable command, by its own carve-out in CHANGE-VALIDATION.md | 6.6 |
| SC18 | The live regression passes in both pi and opencode against the **DEPLOYED** tree — the tree 6.6a installs, which is the whole point of that issue | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-harness-smoke.sh verify-all` → exit 0 | 2.5, 6.7 |
| SC19 | Every upstream row reached the end state its disposition requires | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-054-james-dixson-535968` → exit 0 | 6.1, 6.2, 6.3 |
| SC20 | Every defect discovered but not fixed is filed upstream with its measurement | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-deferred-filed.sh` → exit 0 | 6.4 |
| SC21 | The deployed tree matches source and the version stamp matches HEAD | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-stamp-agrees.sh` → exit 0 | 6.7 |
| SC22 | The five-harness matrix is asserted per harness — pi's name transform, pi's `Deferred` config verdict, codex's budget cap, and `--revert` for all five | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-harness-matrix.sh` → exit 0 | 2.1 |
| SC23 | A measured-empty upstream triage no longer fails the audit that a skipped one must fail | `bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-185-empty-triage.sh` → exit 0 | 3.1 |
| SC24 | A column-0 paragraph under an open issue is REPORTED in `unparsed[]`, not dropped | `bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-225-columnzero-paragraph.sh` → exit 0 | 3.2 |
| SC25 | The beads dependency-type documentation names only types installed `bd` accepts | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-bd-dep-types.sh` → exit 0 | 3.5 |
| SC26 | Every instrument named in #203 returns a non-zero exit when it reports failure | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-exit-discipline.sh` → exit 0 | 3.6 |
| SC27 | **Every string named by Issues 4.3–4.8 is true**, and nothing weaker — a checklist, not a judgement | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-intree-docs.sh` → exit 0 | 4.3, 4.4, 4.5, 4.6, 4.7, 4.8 |
| SC28 | **Every string named by Issues 5.2–5.6 is true**, as SC27 | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-web-accuracy.sh` → exit 0 | 5.2, 5.3, 5.4, 5.5, 5.6 |
| SC29 | The `v0.5.0` tag exists and points at the validated merge commit | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-tag-exists.sh` → exit 0 | 6.8 |
| SC30 | **Every criterion command that names an `assets/` path resolves to a file that exists.** The diff is DIRECTIONAL — *referenced ⊆ present*, never symmetric: 0.7 deliberately authors 8 fixtures while only 4 are named by criteria, so a symmetric diff would report 4 extras and fail by construction. Bare directory references and `controls.txt` are excluded. Deliberately scoped: `cargo`, `uv run` and `manual:` criteria name no `assets/` path and are out of this check's reach | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-criteria-scripts-exist.sh` → exit 0 | 0.8, 0.9 |
| SC31 | The control set is derivable from `plan.md` and agrees with `assets/controls.txt` | `bash docs/plans/plan-054-james-dixson-535968/assets/redcheck.sh verify-manifest` → exit 0 | 0.6, 0.7 |
| SC32 | **The emitted resolver honours a pre-set `SKILL_DIR` rather than overwriting it** — the scriptable half of preferring the harness's own base directory. Deliberately scoped: whether opencode's PROSE hint steered the model is observable only in 6.7's live transcript, not by a script | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-env-var-wins.sh` → exit 0 | 1.7 |
| SC33 | No shipped `SKILL.md` relies on `allowed-tools` for scoping | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-allowed-tools.sh` → exit 0 | 1.8 |
| SC34 | The changelog carries a Deprecations section naming both retained aliases | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-deprecations.sh` → exit 0 | 4.2 |
| SC35 | The live regression ran against the DEPLOYED tree, and the transcript records which tree each harness read | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-deployed-tree.sh` → exit 0 | 6.6a, 6.7 |
| SC36 | The release notes state pi's rules-and-skills-only tuning and the symlink-revert dirtying | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-release-notes.sh` → exit 0 | 6.7a |
| SC37 | The execute branch is merged and the merged tree is the one every later issue validated | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-merged.sh` → exit 0 | 6.5a |
| SC38 | **The two new drift edges exist and are scoped** — `formulas.md` to the shipped `*.formula.toml` set, and `install.md`/`harness-tune.md` to `cli.rs` plus `yf/profiles/`. Both regions were measured UNCOVERED at scoping, which is why the formula count drifted 3-to-5 silently across two plans | `bash docs/plans/plan-054-james-dixson-535968/assets/checks/check-drift-edges.sh` → exit 0 | 5.8 |

---
type: Plan
okf_spec: OKF-PLAN
id: plan-041-james-dixson-a9d837
author: james-dixson
created: '2026-08-16'
status: approved
deliverable_class: ci-release
fingerprint: c7c43ef490e5adfb1147ac9174f03d1fe64b312845e2de6700c15ce0f5bd94c3
---
# Plan: Make `yf self install` a complete, self-consistent sync (#137)

**ID:** plan-041-james-dixson-a9d837
**Author:** james-dixson
**Created:** 2026-08-16
**Status:** approved
**Deliverable-class:** ci-release
**Fingerprint:** c7c43ef490e5adfb1147ac9174f03d1fe64b312845e2de6700c15ce0f5bd94c3

## Objective

Close #137: make a `cargo build --release` — and therefore every caller, including
`yf self install --build` and CI — reliably produce a binary whose embedded `skills/` tree
matches the working tree, and whose git stamp is current **for changes under `yf/` and
`skills/`** (see §1's coverage note — repo-wide `HEAD` movement stays out of reach, by
design). Retire the manual `touch yf/src/embed.rs` workaround that exists because it
currently does not.

> **Scope narrowed at review (pass-1, C10).** This plan originally also made both install
> commands perform a full skills/rules/config sync. The red-team established that the sync
> has **zero technical dependency** on the embed fix, accounts for ~7 of 19 issues, needs 3
> of 5 SPEC amendments, and owns an entire security-consent surface — holding a two-line
> measured fix behind a security-bearing behavior change. **The sync moved to
> `plan-042-james-dixson-98631b`** with its own upstream tracking
> issue. Findings E1 and E4 were produced here and are cited by both plans.

> **Also corrected at scoping by E1.** An earlier draft spoke of "both paths of
> `yf self install`". There are no such paths: `yf self install` is **from-build only** and
> a bare `yf self install` refuses with exit 1 before touching the filesystem. The
> end-user command is **`yf self update`**. See
> [findings/exp-001-self-install-paths.md](findings/exp-001-self-install-paths.md).

Two defects and one coverage hole:

1. **Stale embedded tree — and a second, distinct stale-stamp defect.** `skills/` lives
   outside the `yf/` package and `rust-embed` is a **proc macro**, so it emits no
   `rerun-if-changed` and structurally cannot; its only staleness signal is
   `include_bytes!` dep-info, which tracks *file content* but never *the directory
   listing*. Measured consequence — **two** defects, not one:
   - **(1a) Embed staleness, on ADDITION only.** A file or directory *added* under
     `skills/` is invisible to an incremental release rebuild (`Finished in 0.10s`, new
     file absent). Content edits, deletes and renames all propagate correctly.
   - **(1b) Version-stamp staleness, on EVERY skills-only change.** `build.rs` never
     re-runs, so `YF_GIT_HASH` / `YF_GIT_DIRTY` go stale even when the embed is fresh.

   Fix: **two lines in `yf/build.rs`** — `rerun-if-changed=../skills` plus
   `rerun-if-changed=.`.

   **Honest coverage claim (C5).** These close 1a fully, and close 1b **for changes under
   `yf/` and `skills/`** — not universally. `HEAD` moving for any other reason (a docs-only
   commit, a `SPEC.md` commit, a `git checkout`, a rebase) touches nothing watched, so the
   stamp can still go stale on an incremental build. That residue is the class the existing
   `build.rs` comment already concedes, and watching `.git/` was tried and rejected before
   (REQ-YF-PRE-009, red-team C7). Issue 0.5 records the remaining limit explicitly rather
   than letting the Objective overclaim.
2. **The shipping embed path is untested.** `cargo test --workspace` builds **debug**,
   where `rust-embed` (declared without `debug-embed`) reads `skills/` from disk at
   runtime. So every embed test — including the `REQ-YF-EMBED-003` frontmatter integrity
   check — asserts against the on-disk tree, never the baked one. **The #137 defect class
   is structurally invisible to the entire test suite.** Fix: an opt-in `embed-in-debug`
   cargo feature plus one CI job that exercises the baked path.

   Two things this fix is **not** (C6, verified): the asymmetry is **not** the cause of
   #137 — defect 1a is profile-independent and reproduces in debug with `debug-embed` on.
   And the CI job **cannot catch a #137-class defect**: #137 is an *incremental-rebuild*
   bug, while CI runs `actions/checkout@v4` (fresh mtimes) + `Swatinem/rust-cache@v2`
   (prunes workspace crate artifacts) + `cargo test --workspace`, i.e. a clean build every
   run. A clean build cannot exhibit an incremental staleness bug. What the job *does* buy
   is real: `REQ-YF-EMBED-003` and the enumeration tests start asserting against the
   **baked** tree instead of the on-disk one, closing a genuine spec-conformance hole —
   today's debug binary does not satisfy `REQ-YF-EMBED-001`/`-002` ("from the binary
   alone"). **Issue 1.2, not the CI job, is the only thing here that could have caught
   #137.**

## Motivation

The failure is silent and self-concealing, which is what makes it costly:
`cargo build --release` exits `0`, `yf self install` reports `{"status":"ok"}`, and
the only visible tell is a stale git hash in `yf --version` — visible only to someone
who already knows to compare it against `HEAD`.

Because this repo is **both the source and a consumer** of its own skills, that
silence has a compounding effect: every fix to any other skill can be believed landed
while the deployed copy is unchanged. #137 is the same class of defect as plan-039's
`yf-nkgh` (installed skill lagging the repo) — one level down, in the tool meant to
fix it. It also gates the rest of the open backlog: a fix that does not deploy is not
a fix.

The cost is already being paid in documentation. `AGENTS.md` currently instructs the
operator to run `touch yf/src/embed.rs` as a **required step 0** before every sync,
plus a two-command `diff`/`--version` verification ritual, because the tool cannot be
trusted to do its own job. Retiring that workaround is an explicit deliverable here —
if the fix lands and the workaround stays, the fix did not land.

## Scope

**In scope**

- `yf/build.rs` and `yf/Cargo.toml` — the embed + build-metadata path and the new
  `embed-in-debug` feature. **No command behavior changes at all.**
- A **new `REQ-YF-EMBED-004`** (a build observes additions under `skills/`), the
  `REQ-YF-EMBED-001`/`-002`/`-003` conformance questions, and the `REQ-YF-PRE-009`
  dirty-flag **constraint** that makes D2's second line load-bearing. **SPEC-first** (`AGENTS.md`):
  requirements land before implementation.
- Retiring the `touch yf/src/embed.rs` step 0 and correcting `AGENTS.md`'s
  measurably-wrong causal claim, while **keeping** a one-line `yf --version` sanity note
  for the residue in Objective §1 (C5).
- The four docs that already assert the wrong embed behavior (D5b).
- One CI job exercising the baked embed path.

**Out of scope**

- **The install-time sync** — moved to plan-042 (C10): both commands performing
  skills/rules/config refresh, `REQ-YF-SELF-005` and `REQ-YF-TUNE-023` amendments,
  harness detection, the config-delta report, `--no-sync`, and the whole consent surface.
  This plan changes **no** command behavior, which is exactly why it can ship fast.
- Issue **direction 3** (fail-loud post-promote tree-hash comparison) — declined by the
  operator. E1 confirms nothing exists to reuse: `REQ-YF-MARK` compares
  *embedded ↔ deployed*, never *embedded ↔ repo source*, so this would be net-new work.
- **Direction B** of the parity question (release reads `skills/` from disk) — refuted,
  not deferred (D5a).
- **Flipping `debug-embed` on by default** — the feature ships opt-in (D5).
- Repo-wide `HEAD`-movement staleness (Objective §1's residue). Watching `.git/` was
  already tried and rejected; Issue 0.5 documents the limit instead.
- The `_shared/` vendoring question (#41 / #40), which touches the same embed machinery
  but is a separate design decision paired with a competing alternative.

## Decisions (scoping)

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | ~~Fix via direction 2 (`--build` forces the re-embed)~~ → **SUPERSEDED on evidence. Fix via direction 1, repaired: two lines in `yf/build.rs`.** The `--build` wrapper needs **no change**. | E2 and E3 converged independently. The wrapper fixes only the `yf self install --build` path, leaving bare `cargo build --release` and CI broken; `build.rs` fixes the **default**, so there is no step anyone can forget. It also fixes defect (1b), the version stamp, for free. Measured: no overhead (0.10 s no-op vs 0.10 s control). The best available wrapper mechanism — `touch yf/src/embed.rs` — ranked **weakest**: it hardcodes a filename with no reason to be stable, and if `embed.rs` is renamed the touch still succeeds, the build still exits 0, and staleness returns **silently**. Operator revised the choice after seeing the measurements. |
| D2 | **Direction 1 as *written* in the issue is still rejected; the repaired form is adopted.** The fix is `rerun-if-changed=../skills` **plus** `rerun-if-changed=.` | The issue proposes the `../skills` line *"in addition to the existing no-narrowing behavior"*, which cargo does not permit — emitting **any** `rerun-if-changed` disables the implicit whole-package watch. Measured: with only the `../skills` line, `touch yf/src/main.rs` left `build.rs` un-re-run (probe counter stayed at 1), exactly the REQ-YF-PRE-009 dirty-flag regression `build.rs:51-58` warns about. The `.` line re-declares the package dir and restores it — verified across `src/`, `tests/`, `Cargo.toml`, and `build.rs`. **The second line is not optional; it is what makes the first one safe.** |
| D2a | **Reject `rerun-if-env-changed` (issue-adjacent candidate b3) outright.** | Measured actively harmful: it *also* suppresses the implicit whole-package watch (`touch yf/src/main.rs` → `buildrs_reran=no`) while not even fixing the addition blind spot. Corroborated by the control run in the same script giving `reran=yes` on the identical touch. |
| D3, D4, D6–D10 | **Sync-related decisions — MOVED to `plan-042-james-dixson-98631b`** (pass-1 C10). These governed the install-time sync: the full-sync contract (D3), the two-commands restatement (D4), exec-the-promoted-binary (D6), sync-does-not-fix-#137 (D7), detect-and-report (D8), on-by-default with `--no-sync` (D9), and the composite tune-idempotence test (D10). They are carried into plan-042's scoping verbatim, together with findings E1 and E4 which produced them. | Retained here only as a pointer so a cold reader is not left wondering where the sync went. D7's substance — a sync would not have fixed #137 — is *why* the split is safe: this plan is the whole fix. |
| D11 | **Correct the false ordering claim in `AGENTS.md`.** | `AGENTS.md` asserts `tune` "reads the skill contracts step 2 installed". Measured false: tune's content comes from the **binary's embedded tree**, and config profiles from a separate `rust-embed` root (`yf/profiles/`). Wiring order is a free choice. Leaving the claim in place would mislead the next reader into a constraint that does not exist. (E4) |
| D5 | ~~Make the debug/release embed profiles consistent~~ → **REVISED on evidence. Add an opt-in `embed-in-debug` cargo feature + one CI job; do NOT flip the default.** | E3 measured that the asymmetry is **not** the cause of #137 — the addition blind spot is profile-independent and reproduces in debug with `debug-embed` on. Flipping the default would therefore *import* the bug into `cargo test` while costing the zero-rebuild skills-edit loop (~1.3 s recompile per edit). The feature-gated job keeps the fast default, makes the shipping path testable, and is the **only** proposed change that would have caught #137 automatically. Measured safe: `debug-embed` breaks zero tests (358 + 2 + 4 passed), costs +1.03 MB (+4.1%) and +0.07 s/recompile. |
| D5a | **Record direction B (release reads from disk) as REFUTED, not deferred.** | Impossible, not a trade-off: contradicts `REQ-YF-EMBED-001`/`-002` verbatim; the distribution artifact is a bare binary with no `skills/` payload and nowhere to put one (`REQ-YF-SELF-002` extracts "the inner binary"); violates GR-011; and a Homebrew or `curl\|sh` user has no checkout to read. |
| D5b | **Fix the four docs that already assert the wrong embed behavior**, independent of D5. | `TESTING.md:80`, `skills/yf-plan/test-harness/bootstrap.sh:50-51`, `skills/yf-plan/test-harness/README.md:17-20`, and `yf/src/embed.rs:3-4` all claim debug bakes the tree in. They are wrong **today** and stay wrong under D5 (which keeps the default unflipped). |

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#137](https://github.com/dixson3/yoshiko-flow/issues/137) | `yf self install --from-build` can promote a binary with a STALE embedded skills tree | include | The plan's whole subject. Full body at [references/upstream-137.md](references/upstream-137.md); triage rationale in [upstream-triage.md](upstream-triage.md). Resolved via **direction 1, repaired** (D1, D2) — `rerun-if-changed=../skills` **plus** `rerun-if-changed=.`. Direction 2 was initially selected then superseded on evidence (D1); direction 1 *as written* is not implementable (D2); direction 3 declined (see Scope → Out of scope). Investigation also **partially refuted the issue's own root-cause analysis** — see Objective §1 — which Issue 4.4 posts upstream. **Issue 4.4 must post before or with the close**, or this issue closes carrying an analysis the plan disproved. | Issue 1.1 |
| [#41](https://github.com/dixson3/yoshiko-flow/issues/41) | yf-owned `_shared/`: make yf the install-time vendoring engine | exclude | Adjacent — touches the same `rust-embed` machinery — but a separate design decision, paired with **#40** as a **competing alternative** that must be chosen between first. Epic 1 is agnostic to which model wins and benefits either: a `_shared/` fan-out would add files under `skills/`, i.e. exactly the **addition** case Epic 1 fixes. Not resolved here. | — |

## Investigation Findings

### E1 — `yf self install` paths ([full finding](findings/exp-001-self-install-paths.md))

- **Premise correction.** `yf self install` is **from-build only**; there is no vendor
  path in it. A bare `yf self install` refuses (exit 1) before touching the filesystem.
  The end-user command is **`yf self update`**; initial vendor install is the cargo-dist
  `curl|sh` installer, outside the binary. The two commands share no code path.
- **`harness tune` runs on neither path** — zero grep matches for `harness`/`tune` across
  all 10 files of `yf/src/cmd/self_cmd/`. Its only callers are gated behind the explicit
  user-typed `yf skills install --tune`.
- **But "no tune" ≠ "no rules".** The vendor path's refresh execs `skills **upgrade**`
  (not `install`), which prunes *and* writes the `YOSHIKO_FLOW.md` rules aggregate. The
  real vendor-path gap is tune's **config-alignment half** and **multi-harness fan-out**.
- **No staleness detector exists to reuse.** `REQ-YF-MARK` hashes compare
  *embedded ↔ deployed*, never *embedded ↔ repo source*. A #137 detector would need a
  third file-list builder; only the hash algorithm (`marker.rs:59`) is reusable.
- **`--tune` can block on stdin** (`install.rs:323`, REQ-YF-TUNE-023) when no `--harness`
  is given on a multi-harness machine. An automated sync must pass `--harness` or `--yes`.
- `skills upgrade` has **no `--tune` bridge** (install-only, `cli.rs:299-303`), so
  reaching config alignment from the upgrade path needs a separate `harness tune` exec.

### E4 — `harness tune` auto-invoke safety ([full finding](findings/exp-004-harness-tune-safety.md))

> **Scope note (pass-2 C15).** E4 was run for the install-time sync, which moved to
> `plan-042-james-dixson-98631b`. **For plan-041 only the final paragraph is load-bearing** —
> the measured falsehood in `AGENTS.md`'s tune-ordering claim, which becomes D11 and Issue
> 4.2. Everything above it (the consent surface, the SPEC conflicts, `--no-sync`, harness
> detection) is retained here as the evidence trail for decisions now carried by plan-042.

**Verdict: D3 is implementable but NOT safe as literally stated — it needs guards.** The
blockers are *not* interactivity: `tune` is fully non-interactive and cannot hang (the
crate's only prompt lives in `install.rs` and refuses rather than blocks without a TTY).
The blockers are scope, consent, and SPEC.

- **Consent.** `yf/profiles/claude-code.json:10-14,57-61` sets
  `permissions.defaultMode = "bypassPermissions"` and
  `skipDangerousModePermissionPrompt = true`. On a machine with no `~/.claude/settings.json`,
  tune **creates** it with that profile. Applying that because an operator typed
  `yf harness tune` differs materially from applying it as a side effect of a binary promote.
- **No detection on the tune path.** `resolve_harness_list` (`mod.rs:84-94`) is the
  `--harness` list or a hard-coded `["claude-code"]`. The in-source "auto-detection"
  comment is aspirational, not implemented. Bare tune writes `~/.claude/` whether or not
  Claude Code is installed; `--harness pi` creates `~/.pi/agent/AGENTS.md` on a machine
  with no pi. Detection exists (`harness_detect.rs`) but only the *skills-install* path
  uses it.
- **Two SPEC requirements currently forbid D3** and must be revised first (SPEC-first):
  `REQ-YF-SELF-005` (*"A from-build install shall NOT auto-refresh"*) and
  `REQ-YF-TUNE-023` (*"install and tune stay separable"*; never fan out unconfirmed).
- **`YOSHIKO_FLOW.md` is regenerated wholesale** with no managed-block or checksum guard —
  unlike the `AGENTS.md` surfaces. Sections not in the embedded set are pruned; yf-owned
  standalone rule files are folded then deleted. `--revert` **deletes** the aggregate
  rather than restoring pre-tune content.
- **Composite idempotence is inferred, not measured.** All four sub-ops are individually
  proven byte-stable (97 harness tests pass), but no test runs the whole `tune` command
  twice and asserts byte-identity across surfaces.
- **Corroborates D6** independently: `update.rs:232-241`'s own doc comment says exec'ing
  the freshly written binary *"is what makes the new embed take effect"*.

**AGENTS.md contains a false claim this plan inherited.** It states ordering matters
because *"`tune` reads the skill contracts step 2 installed"*. False as a code-level
dependency — tune's content comes entirely from the **binary's embedded tree**
(`tune_acted_skills()` = `embed::skill_names()`), and config profiles come from a separate
`rust-embed` root (`yf/profiles/`), not from skills at all. Proven by
`mod.rs:1592`, which deploys the full aggregate into a virgin directory containing no
skills. Wiring order is therefore a **free choice**, and the AGENTS.md sentence is a
correction deliverable.

### E2 — Force-re-embed mechanisms ([full finding](findings/exp-002-force-reembed.md))

**Root cause, read from the macro source.** `rust-embed-impl/src/lib.rs:279` emits
`include_bytes!` per file; `grep -rn "rerun" rust-embed-impl-*/src/` returns **nothing**.
rust-embed is a **proc macro** and therefore *cannot* emit build directives. Its whole
staleness story is `include_bytes!` dep-info — **file content, never the directory
listing**.

**Two defects, measured** (see Objective §1a/§1b). The `5c747c0-dirty` vs `39b09f3`
evidence quoted in `AGENTS.md` is **defect 1b (version stamp), not 1a (embed)** — the doc
cites stamp evidence to support an embed claim.

**Falsifier (pass-2 C18).** The additions-only mechanism would have been refuted by a
*content edit* that failed to propagate — that would mean dep-info is not tracking the
macro-generated `include_bytes!` at all, making the defect universal rather than
addition-scoped. It was probed: content edits, deletes **and** renames all propagate
correctly (rows 1–4 of the matrix below), and the marker appeared after a content edit and
*disappeared* after reverting it. Epic 1's whole shape rests on this premise, so it is
recorded rather than assumed.

**Mechanism matrix** (new file added under `skills/` — the only failing case):

| Mechanism | Works? | Rebuild | No-op cost | Fixes stamp? |
| :-- | :-: | --: | --: | :-: |
| control — bare `cargo build --release` | **NO** | 0.12 s | 0.10 s | no |
| `touch yf/src/embed.rs` (today's workaround) | yes | ~5.8 s | — | yes |
| **`rerun-if-changed=../skills` + `=.`** | **yes** | **5.82 s** | **0.10 s** | **yes** |
| `rerun-if-env-changed` + stamp | **NO**, regressive | 0.10 s | 0.10 s | no |
| `cargo clean --release -p yf` | yes | ~7.7 s | **+6 s always** | yes |
| a rust-embed feature/attribute | **none exists** | — | — | — |

**Cost is not a discriminator** — variance is high (the same edit measured 4.99 s and
12.70 s), all working mechanisms sit within noise at ~5–8 s dominated by the unavoidable
crate recompile. **Robustness is.** Chosen fix verified across `Cargo.toml`, `tests/*.rs`,
`build.rs`, `embed.rs`, a skills content edit, and **a new skill dir with a nested
`scripts/x.py`** (proving the `../skills` watch is recursive); `cargo test --release` 4
passed, 0 failed.

**`--build` wrapper needs no change**, and should *not* also get `cargo clean -p yf` — ~6 s
per invocation for no added correctness.

### E3 — Debug/release parity ([full finding](findings/exp-003-debug-release-parity.md))

- **Independently reproduced E2's addition blind spot** and confirmed it is
  **profile-independent** (reproduces in debug with `debug-embed` on: new file →
  `Finished in 0.16s`, absent from output). Making the profiles consistent therefore
  **does not fix #137** — it imports the bug into the dev loop.
- **Direction B refuted on four independent grounds** (D5a).
- **Direction A is safe but insufficient**: breaks zero tests (358 + 2 + 4 passed), +1.03 MB
  (+4.1%), +0.07 s/recompile — but costs the zero-rebuild skills-edit loop (~1.3 s per edit).
- **CI never exercises the shipping embed path.** `cargo test --workspace` builds debug, so
  the embed tests — including `REQ-YF-EMBED-003` — assert against the on-disk tree. The
  #137 class is structurally invisible to the suite.
- **The debug binary currently violates `REQ-YF-EMBED-001`/`-002`** ("from the binary
  alone") because it needs a repo clone at runtime — a latent spec violation either way.
- Only **one** paragraph in the repo relies on the current behavior (`AGENTS.md:74-84`),
  and only for a *convenience* claim. Four other places assert the opposite and are wrong
  today (D5b).

## Experiments

| ID | Question | Why it blocks the plan |
| :-- | :-- | :-- |
| E1 *(answered; its decisions now live in plan-042)* | What does `yf self install` actually do today on **both** paths — `--from-build` and the end-user vendor download/update? Specifically: where is `REQ-YF-SELF-005`'s post-vendor-update skills auto-refresh implemented, and does `yf harness tune` run on **either** path? | D3/D4. The plan proposes wiring a full sync into this command; we cannot design that without knowing which parts already exist on which path. D4 is explicitly an open question, not a premise. |
| E2 | What is the most reliable, cheapest way to force the re-embed from `--build`? Candidates: `touch`ing the embed module, a `cargo:rerun-if-env-changed` cache-buster, `cargo clean -p yf`, or a `rust-embed` feature flag. What does each cost in rebuild time, and which is robust to a future refactor that moves `embed.rs`? | D1 is the chosen fix; this decides its implementation. A fix that depends on a hardcoded filename is a latent regression. |
| E3 | What breaks if debug and release embed consistently? `AGENTS.md` currently documents `./target/debug/yf skills install` as the always-current deploy path **because** debug reads `skills/` from disk. If debug starts baking the tree in, that instruction becomes wrong; if release starts reading from disk, the shipped binary stops being self-contained (GR-011). | D5. The two directions have opposite consequences and the answer determines which is even acceptable. |
| E4 *(answered; its decisions now live in plan-042)* | Is `yf harness tune` safe to invoke automatically — is it idempotent, does it prompt, can it clobber operator hand-edits, and what is its failure mode on an unconfigured harness? | D3 wires it into an automated path. An interactive or destructive `tune` cannot be auto-run as-is. |

## Approach

Four active workstreams (Epics 0, 1, 3, 4 — Epic 2 moved out at review; the numbering
is preserved so cross-plan references stay stable). The plan changes **no command behavior** — its entire deliverable is a
build-system fix, a test-coverage feature, and a documentation truth-up.

**Ordering rationale.** Epic 1 (the two-line `build.rs` fix) is the actual #137 fix, is
measured, and costs nothing at runtime. Epic 0 precedes it only because `AGENTS.md`
mandates SPEC-first and the fix supersedes a stated `REQ-YF-PRE-009` stance. Epic 3
(coverage) and Epic 4 (docs) both follow Epic 1 and are independent of each other.

**Spike-before-commit (C7, C4).** The plan's two load-bearing unknowns are *test
mechanism*, not design: proving addition-propagation needs a nested cargo build, and the
per-file `rerun-if-changed` variant needs to be shown to beat the directory form on the
churn axis. Both get an explicit spike issue **before** the issue that depends on them,
rather than being discovered at execution time.

**The Capability Gate keys on Issue 1.2, not a version grep (C2).** The gate exists to
prove the embed fix works. A version-stamp comparison cannot do that — editing `build.rs`
is itself a watched-file change, so the stamp is fresh on the next build whether or not
the `../skills` line is correct.

## Epics

### Epic 0: SPEC-first — land the requirement changes

Per `AGENTS.md`, SPEC edits precede implementation: *"new `REQ-*` id, revised wording, and
living-amendment-log entry — then write code + a tagged test against it."*

**Corrected at pass-2 (C11).** An earlier draft said this plan "amends `REQ-YF-PRE-009`'s
deliberately-emit-NO-rerun-if-changed stance". **`REQ-YF-PRE-009` contains no such stance** —
verified: it is entirely about the preflight **self-update offer** (`SPEC.md:634-646`), and
`grep -n "rerun-if\|build\.rs" SPEC.md` returns **nothing**. The stance lives only in the
`build.rs:51-58` *comment*, which cites PRE-009 because narrowing the watch would break
`YF_GIT_DIRTY` — a value PRE-009's dirty short-circuit consumes. The draft had promoted a
code comment into a SPEC requirement, which would have produced a wrong SPEC edit **and**
left this plan's one new testable behavior with no `REQ-*` id to tag.

- Issue 0.6: Add **`REQ-YF-EMBED-004`** *(testable)* — a build shall observe **additions**
  under `skills/`, so a newly added file or directory reaches the embedded tree without a
  manual cache-bust. This is the id Issue 1.2 tags and the Capability Gate proves. Include a
  living-amendment-log entry. **This is the plan's only genuinely new requirement**; without
  it, SPEC-first is unsatisfied and Issue 1.2 is a tagged test with nothing to tag.
- Issue 0.4: Resolve the `REQ-YF-EMBED-001`/`-002` **and `-003`** conformance question.
  Today's debug binary violates `-001`/`-002` ("from the binary alone") since it reads
  `skills/` from disk; separately, `-003` says the check runs across the whole `skills/`
  tree (on disk) while Issue 3.2 reframes it as asserting against the **baked** tree. Either
  add an explicit profile carve-out or state that `embed-in-debug` is how conformance is
  demonstrated. **Do not leave the violation undocumented.**
  - depends-on: 0.6
- Issue 0.5: Record the `REQ-YF-PRE-009` **constraint** (not a supersession): the dirty-flag
  probe must stay accurate, which is precisely *why* D2's second line (`rerun-if-changed=.`)
  is load-bearing rather than decorative. Add a living-amendment-log entry, note the residual
  limit (repo-wide `HEAD` movement stays out of reach — Objective §1), the `cargo package`
  caveat (R9), and the incidental free coverage: **`yf/profiles/` is a second `rust-embed`
  root** (`harness/profile.rs:26`, `#[folder = "profiles"]`, 3 JSON files) and is
  **believed — not yet measured** — to carry the same addition blind spot, fixed by the same
  `rerun-if-changed=.` line. Neither E2 nor E3 probed it. **Verify with a one-minute
  add-a-file probe before asserting it in the SPEC**, or word the amendment as unverified
  (pass-3 N3).
  The "deliberately emit NO rerun-if-changed" text itself is a **`build.rs` comment**, rewritten
  under Issue 1.1 — not a SPEC edit.
  - depends-on: 0.4

### Epic 1: Fix the embed + version-stamp defects (the actual #137 fix)

- Issue 1.2a: **Spike** the addition-propagation test mechanism (C7) before committing to
  1.2. Determine whether it can run in-suite — offline scratch crate, registry-cached
  `rust-embed`, dedicated `CARGO_TARGET_DIR`, warm-rebuild sequence, release profile — and
  how long it takes. **Explicit fallback:** if infeasible in-suite, implement it as a
  `scripts/` check wired into `CHANGE-VALIDATION.md`'s full tier. Decide now, not at
  execution time. Raised in priority because the Capability Gate depends on 1.2.
  - depends-on: 0.5
- Issue 1.5: **Spike** per-file vs directory `rerun-if-changed` (C4). Have `build.rs` walk
  `skills/` and emit per-file lines mirroring `#[folder]`'s `*.pyc` / `__pycache__`
  exclusions, and measure it against the plain `../skills` directory watch on the churn
  axis (a `uv`/pytest run must not force a full recompile). Choose the form 1.1 implements.
  - depends-on: 0.5
- Issue 1.1: Replace the "deliberately emit NO rerun-if-changed" block in `yf/build.rs`
  with the form Issue 1.5 selects — at minimum `rerun-if-changed=../skills` +
  `rerun-if-changed=.` — carrying the E2 rationale in the comment (proc macro → no
  directives → dep-info tracks content, not the listing).
  - depends-on: 1.5
  - resolves-upstream: #137 (include)
- Issue 1.2: Add the addition-propagation regression test in the form 1.2a selected,
  tagged `REQ-YF-EMBED-004`. It must add a *new* file under a scratch skills tree and assert
  it reaches the built artifact; a content-edit test would pass even with the bug present and
  is therefore worthless as a guard. **Acceptance requires demonstrating the test RED against
  the pre-fix `build.rs`** (stash the two lines, or run against a scratch crate without them)
  before accepting it green — otherwise a test that is green because it never exercises the
  addition path is indistinguishable from one green because the fix works (pass-2 C13).
  - depends-on: 1.1, 1.2a
- Issue 1.3: Add the drift guard for the two remaining couplings (C4) — assert the
  `"../skills"` literal agrees between `build.rs` and `embed.rs`'s `#[folder]`, **and** that
  the exclude sets agree if 1.5 selected per-file emission. Without this, a future folder
  move or a new exclude silently desyncs the watch from the embed.
  - depends-on: 1.1
- Issue 1.4: Add a version-stamp regression test for defect 1b — a skills-only change must
  leave `YF_GIT_HASH` current. Scope the assertion to the coverage Objective §1 actually
  claims (`yf/` and `skills/` changes), not to repo-wide `HEAD` movement.
  - depends-on: 1.1

### Epic 2: Install-time sync — MOVED to `plan-042-james-dixson-98631b`

Not lost, not descoped-to-nothing: the whole install-time sync workstream (skills + rules +
harness config on both commands, the `REQ-YF-SELF-005` / `REQ-YF-TUNE-023` amendments, the
consent boundary, `--no-sync`, the delta report, the composite tune-idempotence test) moved
to plan-042 at pass-1 review. The epic number is retained as a stub so a reader does not read
the 1 → 3 gap as an editing loss. See the `D3, D4, D6–D10` row in Decisions.

### Epic 3: Close the test-coverage hole

- Issue 3.1: Add the `embed-in-debug = ["rust-embed/debug-embed"]` cargo feature.
  - depends-on: 1.1
- Issue 3.2: Add a CI job running `cargo test --workspace --features yf/embed-in-debug`.
  **Note the `yf/` prefix**: the root `Cargo.toml` is a **virtual manifest**
  (`[workspace] members = ["yf"]`), where cargo rejects a bare `--features` — so
  `--features embed-in-debug` fails at the root. `-p yf --features embed-in-debug` is the
  equivalent form (pass-3 N4).
  **Rationale (corrected per C6):** this makes `REQ-YF-EMBED-003` and the enumeration tests
  assert against the **baked** tree rather than the on-disk one, closing a spec-conformance
  hole. It does **not** catch #137-class incremental defects — CI builds clean. That credit
  belongs to Issue 1.2.
  - depends-on: 3.1

### Epic 4: Documentation truth-up

Sequenced after Epic 1 so it describes shipped behavior.

- Issue 4.1a: Rewrite the `AGENTS.md` sync section — delete step 0 and the `diff` half of
  the verification ritual outright, and **correct the causal claim**. The current text
  asserts a skills-only commit leaves the embedded tree stale (true only on *addition*) and
  cites `5c747c0-dirty` evidence that is actually about the version stamp. **Keep** a
  one-line `yf --version` sanity note (C5) — it is the only detector for the residual
  `HEAD`-movement cases, which this plan does not fix. **Leave the three-command ritual
  intact and correct** — this plan changes no command behavior, so it remains true;
  plan-042 replaces it. The two edits touch adjacent text and 041 lands first, so a stalled
  plan-042 leaves `AGENTS.md` in a coherent resting state, not a half-corrected one
  (pass-2 C17).
  - depends-on: 1.1
- Issue 4.2: Remove the false ordering claim that `tune` "reads the skill contracts step 2
  installed" (D11) — measurably false; wiring order is a free choice.
  - depends-on: 4.1a
- Issue 4.3: Correct the four docs that already assert the wrong embed behavior (D5b):
  `TESTING.md:80`, `skills/yf-plan/test-harness/bootstrap.sh:50-51`,
  `skills/yf-plan/test-harness/README.md:17-20`, `yf/src/embed.rs:3-4`.
  - depends-on: 3.1
- Issue 4.4: Post the D2/E2/E3 correction to #137 — the addition-only mechanism, the
  version-stamp/embed conflation, and why the naive one-liner in the issue's direction 1
  would have regressed the dirty flag. Prevents the rejected form being retried later.
  **Must post BEFORE or WITH the #137 close** — otherwise the issue closes still carrying a
  root-cause analysis this plan proved wrong (pass-2 upstream caveat).
  - depends-on: 1.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: addition-propagation proven before the fix is trusted
- Type: auto
- Condition: Issue 1.2's addition-propagation test is green — a file **newly added** under a
  scratch skills tree reaches the built release artifact.
- Test: the Issue 1.2 test (in-suite via `cargo test`, or the `scripts/` full-tier check if
  Issue 1.2a selects that fallback).
- Blocks: Issue 4.1a, Issue 4.4
- Instructions: **Do not gate on a version-stamp grep** (pass-1 C2). Comparing
  `yf --version` to `HEAD` is wrong in both directions: editing `build.rs` is itself a
  watched-file change, so the stamp is fresh on the next build *with or without* a correct
  `../skills` line (false pass); and `git commit` moves `HEAD` without touching a watched
  file, so a no-op rebuild holds the pre-commit hash (false fail on a correct fix). The
  addition case is the only property that distinguishes a working fix from a typo'd path.
  A `yf --version` check remains useful as a **secondary** signal — note the commit-ordering
  caveat when using it by hand.

  This gate blocks the two issues that *assert the fix works to an audience* — deleting the
  documented workaround (4.1a) and posting the correction upstream (4.4). Both are
  outward-facing claims that must not be made on an unverified fix.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R2 | **`rerun-if-changed=.` regresses the dirty flag in a case not measured.** E2 verified `src/`, `tests/`, `Cargo.toml`, `build.rs`. | Medium | Issue 1.4's version-stamp regression test. Note the named `target/` worry **cannot** occur: `target/` is at the *workspace* root, not `yf/target`, and `yf/.gitignore` lists only a `/target` that does not exist (verified at review). |
| R2a | **Spurious full rebuilds from gitignored churn (C4).** `rerun-if-changed` has no exclude mechanism, but `embed.rs` excludes `*.pyc`/`__pycache__` from the embed. **40** such entries exist under `skills/` today (verified; gitignored at `.gitignore:11-12`), and this repo's always-loaded rules run `uv`/pytest constantly — each run can bump a dir mtime and force a ~6 s recompile where a 0.10 s no-op is expected. E2's "no measurable overhead" was measured on a quiet tree. | Medium | Issue 1.5 spikes per-file emission mirroring `#[folder]`'s excludes and measures both forms on the churn axis before 1.1 commits to one. If the directory form wins anyway, document the tax rather than leaving it to surprise someone. |
| R3 | **The `"../skills"` literal, or the exclude set, silently desyncs** between `build.rs` and `embed.rs` on a future folder move — restoring #137 with no failing test. | Medium | Issue 1.3, extended per C4 to guard the exclude set as well as the folder literal. These are the only couplings the fix introduces, which is why they earn a dedicated issue. |
| R5 | **Issue 1.2's test proves infeasible in-suite** (nested cargo build, offline resolution, tens of seconds), leaving the Capability Gate without its condition. | Medium | Issue 1.2a spikes it **first**, with an explicit pre-agreed fallback (a `scripts/` check in `CHANGE-VALIDATION.md`'s full tier). The gate names either form, so the fallback does not invalidate it. |
| R7 | **A stale `yf` is used to fix the stale-`yf` bug.** The binary running during execution predates the fix. | Low | Epic 1 is verified by *rebuilding and testing*, never by trusting the running binary. The Capability Gate's test builds fresh by construction. |
| R1, R4, R6, R8 | **Moved to `plan-042-james-dixson-98631b`** — the consent surface (R1), the `YOSHIKO_FLOW.md` wholesale-regeneration hazard (R4), Epic-2-slippage (R6), and the `--no-sync`/`--binary-only` naming collision (R8) all belonged to the sync. Listed so the R2, R2a, R3, R5, R7, R9 numbering gap reads as a relocation, not an editing loss. | — | Carried into plan-042's scoping. |
| R9 | **`../skills` does not exist under `cargo package`/`publish`** — cargo treats a missing `rerun-if-changed` path as permanently dirty (always re-run). | Low | Harmless today: `#[folder = "../skills"]` already precludes publishing this crate. Recorded so a future packaging attempt is not mystified. One sentence in Issue 0.5's amendment. |

## Success Criteria

1. **The addition case is fixed and proven.** Adding a new file *and* a new skill directory
   under `skills/`, then running a plain `cargo build --release`, produces a binary
   containing them — verified by the Issue 1.2 test, not by inspection.
2. **The version stamp is fixed for the claimed scope.** A skills-only commit leaves
   `yf --version` reporting the current `HEAD` hash (Issue 1.4). Repo-wide `HEAD` movement
   is explicitly **not** claimed (Objective §1, Issue 0.5).
3. **No dirty-flag regression, and the rebuild tax is resolved either way.**
   `touch yf/src/main.rs` still re-runs `build.rs`, and a no-op build stays at ~0.10 s.
   For the `__pycache__` axis (R2a), **either** a `uv run`/pytest cycle that touches only
   gitignored files does not force a full recompile, **or** — if Issue 1.5's spike selects
   the plain directory watch — the tax is measured and documented in the `build.rs` comment
   and Issue 0.5's amendment. Stated as a disjunction because the conjunction contradicted
   R2a's own mitigation (pass-2 C12).
4. **`AGENTS.md` step 0 is deleted, not reworded**, and the causal claim corrected to the
   measured addition-only mechanism — while the one-line `yf --version` sanity note
   survives for the residue. *If the fix lands and the workaround stays, the fix did not
   land.*
5. **CI exercises the baked embed path** via `cargo test --workspace --features
   embed-in-debug`, so `REQ-YF-EMBED-003` asserts against the shipping tree. Stated
   honestly: this closes a spec-conformance hole, **not** the #137 incremental-rebuild
   class (C6).
6. **SPEC leads implementation.** **`REQ-YF-EMBED-004` exists** and Issue 1.2's test is
   tagged with it — the plan's one new testable behavior has an id, satisfying `AGENTS.md`'s
   SPEC-first rule. `REQ-YF-PRE-009`'s dirty-flag constraint and the residual limit are
   recorded, and the `REQ-YF-EMBED-001`/`-002`/`-003` conformance questions are resolved
   explicitly rather than left silent — all before Issue 1.1 lands.
7. **All four wrong docs are corrected** (D5b) and the false tune-ordering claim removed
   (D11).
8. **#137 carries the correction** (Issue 4.4) so the rejected one-liner is not retried
   later.
9. **The plan changed no command behavior.** `rg "fn main" yf/src/cmd` and the CLI surface
   are untouched; the diff is confined to `yf/build.rs`, `yf/Cargo.toml`, tests, CI, and
   docs. This is the property that let the plan ship ahead of plan-042.

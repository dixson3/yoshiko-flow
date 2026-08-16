---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
verdict: REVISE
status: resolved
---

# Review pass 1 — adversarial (red-team)

## Verdict: REVISE

3 high, 7 medium concerns.

Conformance pass ran first and returned **PASS** (after two INCOMPLETE rounds: an
uncompleted `upstream-triage.md`, an Upstream Issues note that contradicted the revised
D1/D2, a double-deliverable Issue 2.6, two success criteria with no verification handle,
and a dangling `2.6` edge left by the split). Conformance is mechanical and produces no
`pass-N.md`; this file records the adversarial pass.

## Strengths (verbatim)

- **The investigation is genuinely measured, not asserted.** Independently confirmed the
  load-bearing premises: `rust-embed` 8 is a proc macro and structurally cannot emit
  `cargo:rerun-if-changed`; `#[folder = "../skills"]` sits outside the `yf/` package; the
  current `build.rs` concedes in its own comment that it "cannot observe repo-wide changes
  outside the `yf/` package". The additions-only mechanism follows necessarily from
  `include_bytes!` dep-info tracking file *content*, never the directory listing. E2's
  matrix (build.rs output mtime pinned at `1786908265` across a skills content edit that
  *did* recompile the crate) is a clean, decisive separation of defect 1a from 1b.
  **Premise for Epic 1 holds.**
- **D2's insistence that the second line is load-bearing is correct and non-obvious.** The
  issue's one-liner would have silently regressed REQ-YF-PRE-009's dirty flag. Catching that
  before implementing is the plan's single best save. D2a's rejection of
  `rerun-if-env-changed` is measured with a control in the same script.
- **`rerun-if-changed=.` is safe on the `target/` axis specifically.** `target/` is at the
  *workspace* root, not `yf/target`, and `yf/.gitignore` contains only `/target` (which does
  not exist). R2's named worry cannot occur under today's layout — but see C4.
- **D6/D7 are correct and well-corroborated**, including `update.rs`'s own doc comment.
  D5a's four-ground refutation of "release reads from disk" is airtight.
- **SPEC-first sequencing is real, not ceremonial.** Verified `REQ-YF-SELF-005` literally
  says *"A from-build install shall NOT auto-refresh"* and `REQ-YF-TUNE-023` says *"never
  fan out writes to all detected harnesses unconfirmed."* Epic 2 genuinely requires Epic 0.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C1 | Consent guard (D8) does not address the objection E4 raised — narrows scope and discloses *after* the write, but does not restore consent. Worst on Issue 2.5 (`self update`, end-user): a routine version bump creates `bypassPermissions` + `skipDangerousModePermissionPrompt` for a user who consented to a version bump. R1's "only changes *when* it happens" elides the distinction — *when* is the whole objection. | **high** |
| C2 | Capability Gate test is wrong in **both** directions. **False pass:** editing `build.rs` is itself a watched-file change, so `build.rs` re-runs on the next build with or without the `../skills` line — it cannot distinguish a correct fix from a typo'd path. **False fail:** `git commit` moves `HEAD` without touching a watched file, so a no-op rebuild holds the pre-commit hash and the gate fails on a correct implementation. | **high** |
| C3 | R6's mitigation is contradicted by the plan's own graph. Issue 4.1 (delete step 0) carries `depends-on: 1.1, 2.6b`, so the whole doc truth-up is hostage to the last issue of Epic 2. Success Criterion 4 says *"if the fix lands and the workaround stays, the fix did not land"* — so by the plan's own standard, Epic 1 alone does **not** close #137 as scoped. | **high** |
| C4 | `rerun-if-changed=../skills` has no exclude mechanism, but `embed.rs` carefully excludes `*.pyc`/`__pycache__`. **40** such entries currently exist under `skills/`, and this repo's always-loaded rules run `uv`/pytest constantly — every run bumps a dir mtime and forces a full ~6 s recompile where a 0.10 s no-op was expected. E2's "no measurable overhead" was measured on a quiet tree. R2 names only the `target/` case, which cannot happen. Also: R3 guards the folder literal but **not** the exclude-set divergence — a second unguarded coupling. | medium |
| C5 | The 1b fix is narrower than "closes both, for every caller". It covers changes under `yf/` and `skills/`; `HEAD` moving for any other reason (docs-only commit, `SPEC.md` commit, `git checkout`, rebase) still leaves the stamp stale. SC2 happens to sit inside coverage, so the test passes while the general claim stays false. Compounding: SC4 deletes the `yf --version` vs `HEAD` ritual — the only detector for the residual cases. Removing a detector broader than the fix is a net observability regression. | medium |
| C6 | Epic 3's headline claim is almost certainly false. #137 is an **incremental-rebuild** defect; CI does `actions/checkout@v4` (fresh mtimes) + `Swatinem/rust-cache@v2` (prunes workspace crate artifacts), so `yf` compiles from scratch every run and the embed is always fresh. A clean build cannot exhibit an incremental staleness bug. The job has real value — it makes `REQ-YF-EMBED-003` assert against the *baked* tree — but that is a different claim. | medium |
| C7 | Issue 1.2's test mechanism is unspecified and non-trivial: proving addition propagation needs a nested `cargo build` against a scratch crate with its own `rust-embed` folder, twice, with a warm target dir — requiring cargo on PATH, an offline-resolvable manifest, a private `CARGO_TARGET_DIR`, and tens of seconds. It is also the plan's most load-bearing test (C2 wants the gate to use it). | medium |
| C8 | `--no-sync` lands *after* the sync it guards (2.6a `depends-on: 2.4, 2.5`). Between those landings the sync is on by default with no escape hatch — the exact window R1 points at 2.6a to mitigate. Given R6 contemplates Epic 2 slipping, that window could ship. | medium |
| C9 | D8 satisfies the letter of `REQ-YF-TUNE-023` while defeating its purpose — the sync detects all present harnesses and writes to each, merely spelling them out as explicit flags. D8 calls this "converting a SPEC conflict into a SPEC-compliant call shape", a candid description of loophole-lawyering. Issue 0.2's claim that the prohibition is "preserved intact, not weakened" is not accurate: the prohibited *outcome* now occurs. | medium |
| C10 | Epic 2 is scope creep. By D7 the sync does not fix #137; by R6 Epic 1 alone closes it. Epic 2 is 7 of ~19 issues, needs 3 of 5 SPEC amendments, drags 3.3 along, owns the entire consent surface, and blocks 4.1. A two-line, zero-risk, measured fix is held behind a security-bearing behavior change needing its own review. Epic 1 has **zero** technical dependency on Epic 2. | medium |

## Missing

- **No `CI`/non-interactive handling for the sync.** `yf self install --from-build` in a
  container would write `~/.claude/settings.json` with `bypassPermissions`.
  `REQ-YF-SELF-006` already establishes a `CI`-suppression precedent in this codebase; the
  sync should honour it. Absent from scope, decisions, and risks.
- **No risk for `../skills` under `cargo package`/`publish`** — cargo treats a non-existent
  `rerun-if-changed` path as permanently dirty. Harmless today (the `#[folder]` already
  precludes publishing) but worth one sentence. *(low)*
- **No falsifier recorded for the additions-only premise.** Epic 1's whole shape rests on
  it; one line naming what would have refuted it (a content edit failing to propagate) is
  cheap insurance. *(low)*
- **R4's mitigation is aspirational.** "Flag for a follow-up issue" is not an issue. Make it
  a `bd` bead in Epic 2 or the mitigation does not exist.

## Gate Assessment

- **Start Gate (human):** appropriate.
- **Capability Gate:** structurally sound — reachable, no cycle, blocks the mutating step
  (2.4/2.5) rather than the evidence-producing step, and correctly does *not* block 2.1–2.3
  (pure refactor / read / report). Good discrimination. **But the `Test` is materially wrong
  in both directions (C2), and it is the only automated guard between an unverified embed
  fix and an auto-deploying sync — a false pass here is the plan's highest-leverage failure.
  Must be revised before approval.**
- **Reconcile Gate:** fine.

## Upstream Assessment

- **#137 (include):** disposition correct; the resolution chain (direction 2 → superseded →
  direction 1 repaired) is well documented, and Issue 4.4 posting the correction upstream is
  the right call and the kind of thing usually skipped. But per C3, "resolves #137" is
  currently only true if the *whole plan* lands.
- **#41 (exclude):** justified; the `_shared/`-fan-out-is-the-addition-case cross-reference
  is genuinely useful rather than boilerplate.
- **Gap:** per `AGENTS.md`'s coarse-granularity convention, Epic 2 is a plan-scale effort
  with a security-relevant behavior change and **no upstream issue of its own** — currently
  invisible upstream, riding under a bug report about a stale build.

## Operator Resolutions

**Operator ruling: the plan is SPLIT (C10 accepted).** plan-041 retains the #137 fix
("Plan A"); the sync moves to **plan-042** ("Plan B") with its own upstream tracking issue.
Concerns scoped to the sync are resolved *by relocation* — they are carried into plan-042's
scoping decisions verbatim, not dismissed.

Three operator decisions taken on this review:

- **C10 → split into two plans** (the red-team's recommended shape).
- **C1 → split the sync halves by default**: skills + rules aggregate auto-sync; harness
  **config** alignment applies automatically only when a settings file already exists and
  the delta touches no `permissions.*` key. When tune would *create* `settings.json` or
  write a `permissions.*` key, print the delta and require `--yes`, reusing
  `install.rs`'s existing `confirmation_required` shape rather than inventing a weaker one.
- **C2 → gate on Issue 1.2 green** (addition-propagation), not the version-stamp grep.

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | Consent guard insufficient (esp. `self update`) | high | Accepted. Sync halves split by default; `permissions.*` writes and settings-file *creation* require `--yes`. Carried to **plan-042** as a scoping decision, since Epic 2 leaves this plan. | resolved |
| C2 | Capability Gate test wrong both directions | high | Accepted. Gate condition becomes "Issue 1.2 (addition-propagation) is green"; the version-stamp grep is demoted to a secondary signal with the commit-ordering caveat recorded in the gate Instructions. | resolved |
| C3 | R6 mitigation contradicted by 4.1's dependency | high | Resolved by the split: 4.1a (delete step 0 + correct the causal claim) stays in plan-041 depending on 1.1 only; 4.1b (document the new sync behavior) moves to plan-042. Epic 1 shipping now genuinely closes #137 as scoped. | resolved |
| C4 | `__pycache__` churn → spurious rebuilds; exclude-set unguarded | medium | Accepted, and independently verified: **40** `__pycache__`/`.pyc` entries under `skills/` today, gitignored at `.gitignore:11-12`. New Issue 1.5 spikes per-file emission mirroring `#[folder]`'s excludes; Issue 1.3 extended to guard the exclude set as well as the folder literal; new risk R2a records the rebuild tax. | resolved |
| C5 | 1b fix narrower than claimed; SC4 deletes the detector | medium | Accepted. Objective/D1 restated to claim coverage only for `yf/` and `skills/` changes; Issue 0.5 records the residual limit in the `REQ-YF-PRE-009` amendment; Issue 4.1a keeps a one-line `yf --version` sanity note (deleting only step 0 and the `diff` half). | resolved |
| C6 | CI cannot catch a #137-class defect | medium | Accepted, and independently verified: CI is `checkout@v4` + `Swatinem/rust-cache@v2` + `cargo test --workspace` — a clean build, which cannot exhibit an incremental-rebuild defect. Issue 3.2's rationale and SC7 rewritten to the true benefit (the shipping embed path becomes testable; `REQ-YF-EMBED-003` asserts against the baked tree). The "would have caught #137" credit moves to Issue 1.2. | resolved |
| C7 | Issue 1.2 test mechanism unspecified | medium | Accepted. New Issue 1.2a spikes the mechanism (offline scratch crate, registry-cached `rust-embed`, dedicated `CARGO_TARGET_DIR`, warm-rebuild sequence) **before** 1.2 is committed to, with an explicit fallback to a `scripts/` check wired into `CHANGE-VALIDATION.md`'s full tier if it proves infeasible in-suite. Raised in priority because C2 makes the gate depend on it. | resolved |
| C8 | `--no-sync` lands after the sync it guards | medium | Carried to **plan-042**: the opt-out and delta report land as part of, or before, the wiring — never trailing it. | resolved |
| C9 | D8 loophole-lawyers `REQ-YF-TUNE-023` | medium | Accepted. Carried to **plan-042**: its SPEC amendment must state honestly that the sync path may write to detected harnesses without per-run confirmation, and name the compensating controls — rather than claiming the prohibition is "preserved intact". | resolved |
| C10 | Epic 2 is scope creep; split recommended | medium | Accepted — the plan is split. | resolved |
| M1 | No CI/non-interactive suppression for the sync | medium | Carried to **plan-042**, citing the existing `REQ-YF-SELF-006` `CI`-suppression precedent. | resolved |
| M2 | No `cargo package` risk for `../skills` | low | Accepted — added as risk R9. | resolved |
| M3 | No falsifier recorded for the additions-only premise | low | Accepted — falsifier recorded in the Investigation Findings E2 block. | resolved |
| M4 | R4 mitigation is aspirational, not an issue | low | Carried to **plan-042** as a real bead (the `YOSHIKO_FLOW.md` wholesale-regeneration hazard belongs with the sync that raises its frequency). | resolved |
| — | Upstream gap: Epic 2 invisible upstream | medium | Resolved by the split — plan-042 files its own coarse tracking issue per the `AGENTS.md` convention. | resolved |

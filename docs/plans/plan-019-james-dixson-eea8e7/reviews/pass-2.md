# Red-Team Review — pass 2

**Plan:** plan-019-james-dixson-eea8e7
**Date:** 2026-07-02
**Reviewer:** Red-Team (adversarial, read-only)
**Scope:** the post-approval dirty-build bypass scope-add (Issue 3.5, REQ-YF-PRE-009 amend,
dirty short-circuit in 3.2, dirty test in 3.4) + light regression on pass-1 resolutions.
**Status:** frozen (all concerns resolved in plan v4)

## Verdict: REVISE

The dirty-build bypass is directionally reasonable and — importantly — cannot corrupt
shipped-release behavior. But its central feasibility claim ("`git status --porcelain` /
`git describe --dirty` at build time works") is overstated given the *existing* `build.rs` rerun
contract, and the v3 scope-add left two internal-consistency seams stale. None fatal; all
addressable in plan text. New concerns numbered from C7.

## Strengths

- **Shipped artifacts are correct by construction.** CI/release builds run from a clean checkout
  → the released binary is reliably `not-dirty` and stays nag-eligible. No risk of shipping a
  "dirty" release that silently suppresses real users' offers. This is the property that matters
  most, and it holds.
- **Testability (prior concern #4) is genuinely resolved by design.** 3.2 consumes an *injected
  bool* dirty flag (not `is_dirty_build()` directly); 3.5 wires the compile-time read only into
  `Env::live()`. So 3.4's "dirty flag true → none" test drives the seam directly and does not
  depend on how the test binary was compiled — correctly applying the pass-1 C2 lesson.
- **Dependency ordering is sound.** 3.5 (dep 1.1) produces the dirty seam; 3.2 (dep 3.1, 3.5)
  consumes it; 3.3→3.4 follow. Epic 2 is independent (only a soft-order on the shared
  `run_with_env` region), so the C1 stamp-invalidation logic is untouched.
- Pass-1 C1/C3/C4/C5/C6 resolutions remain coherent in v3.

## Concerns

- **C7 — `YF_GIT_DIRTY` goes stale on the exact builds the bypass targets — severity: medium.**
  `build.rs` emits `cargo:rerun-if-changed=.git/HEAD` and `.git/refs`. Once any `rerun-if-changed`
  is emitted, cargo's default "re-run on any package change" is disabled — build.rs re-runs only
  when HEAD or a ref moves. Editing a tracked source file dirties the tree but touches neither
  `.git/HEAD` nor `.git/refs`, so build.rs does **not** re-run and `YF_GIT_DIRTY` keeps its
  last-baked value. Concretely: clean checkout bakes `dirty=false`; dev edits `preflight.rs`
  (tree now dirty) → `cargo build` recompiles the crate but reuses the cached build-script output
  → binary reports **not-dirty despite a dirty tree** → the bypass does not fire and the dev gets
  the very nag it exists to suppress. Reverse: a `dirty=true` bake then `git checkout -- .` leaves
  a **falsely-dirty** local binary. So the "probe actually works" premise holds only for the first
  build after a HEAD/ref move, not the incremental dev loop that is the bypass's audience.
  Secondary: `git status --porcelain` from `build.rs` evaluates whole-repo dirtiness including
  untracked files (editing this `plan.md`, or any stray scratch file, marks dirty) — a different
  semantic than `git describe --dirty` (tracked-only, needs a tag); the plan lists both
  interchangeably.
  Recommendation: (a) drop the feasibility overstatement — state `YF_GIT_DIRTY` is **best-effort**
  (reliable for clean CI release builds, stale-prone on incremental local builds); (b) if dev-loop
  reliability is wanted, force build.rs to re-run every build (drop the narrowing `rerun-if-changed`
  so package changes retrigger it) and acknowledge even that can't catch repo-wide changes outside
  the package; (c) pick one probe and state its untracked-file semantics.

- **C8 — v3 left the "three seams" story stale; there are now four — severity: low.**
  The Env finding ("three injection points, not one") and Issue 3.3 ("Add the **three** live
  seams") were not updated when the dirty seam was added; 3.2 and 3.5 now inject a **fourth** (the
  dirty flag). An implementer reading the finding/3.3 provisions three and is surprised by 3.5's
  fourth — a coherence regression that lightly undercuts the C2 anchor.
  Recommendation: update the Env finding and Issue 3.3 to say **four** seams (Dirs + Source +
  suppression + dirty).

- **C9 — Epic 2's version stamp is blind to dirtiness; interaction undiscussed — severity: low.**
  Keeping the stamp = pure `CARGO_PKG_VERSION` (dirty only in a separate flag + cosmetic suffix)
  is the **right call for thrash** (they did not fold the hash into the stamp — good, no
  per-commit thrash). Unstated tradeoff: a dirty dev `0.3.2` and a clean release `0.3.2` write an
  **identical** stamp, so Epic-2 invalidation can't see that boundary — a dev who bumps
  `min-bd-version` in a dirty tree without bumping `CARGO_PKG_VERSION` gets a stale
  `prereqs-present: true` honored across the clean↔dirty switch (a small, dev-only reopening of
  the C1 hole).
  Recommendation: add one sentence (Epic 2 / Approach) stating the stamp intentionally excludes
  dirtiness to avoid per-rebuild thrash, so same-`CARGO_PKG_VERSION` clean↔dirty transitions do
  not invalidate the cache — an accepted dev-only edge. (If that edge matters, fold `-dirty` — but
  not the hash — into the stamp; it won't thrash.)

- **C10 — The dirty bypass is nearly-redundant with `nag_eligible()`; reachability is one narrow
  case — severity: low.**
  `nag_eligible()` is true only for `Source::Vendor` (not Homebrew, no from-build marker, exe under
  the vendor prefix). Common local-dev shapes are already suppressed without the dirty flag:
  `target/{debug,release}/yf` in place → `Unknown`; `yf self install --from-build` → `FromBuild`.
  The dirty bypass is only reachable when a *dirty* binary is manually placed under a receipted
  vendor prefix (e.g. `cp target/release/yf ~/.local/bin/yf` over a prior `curl|sh` receipt) →
  `Vendor` **and** dirty. Not dead code, but not the broad safety net the Risks table implies.
  Recommendation: keep it (it is defense-in-depth), but note in Risks that the residual reachable
  case is "dirty binary copied over a receipted vendor prefix," so its value isn't over-weighted —
  and so it's clear C7's staleness only bites in that already-narrow slice.

## Missing

- Issue 3.5 gives no test for the graceful-degradation branch (git absent / outside-checkout →
  not-dirty), nor a note that `is_dirty_build()`'s env read is coverage-exempt (like `YF_GIT_HASH`)
  — either would close the loop the Epic-4 coverage gate might probe for REQ-YF-PRE-009's dirty
  clause.
- No statement of which probe (`git status --porcelain` vs `git describe --dirty`) is normative in
  REQ-YF-PRE-009 — the two differ on untracked files, which is observable behavior.

## Gate Assessment

Unchanged from pass-1 and still sound. If REQ-YF-PRE-009's dirty clause is written testable,
ensure 3.4's injected-bool test (not `is_dirty_build()`) is what the gate maps to.

## Upstream Assessment

No change from pass-1. #62 still correctly excluded; coarse land-the-plane issue unaffected.

## Bottom line

APPROVE-worthy in intent, REVISE for text: correct the C7 feasibility overstatement, reconcile the
C8 three-vs-four seam count, add the C9 stamp/dirty note. C10 is informational. Most important:
**the bypass cannot mis-suppress real users' offers** (release artifacts are always built clean),
so the downside of every concern is confined to the local-dev experience, not shipped behavior.

## Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| C7 | `YF_GIT_DIRTY` stale on incremental dev builds; probe semantics | medium | resolved | Issue 3.5 reworded: dirty flag is **best-effort** (reliable for clean CI release; stale-prone on incremental local); drop the `.git/HEAD`/`.git/refs` `rerun-if-changed` narrowing so build.rs reruns on package changes (best dev-loop accuracy achievable); `git status --porcelain` (whole-repo incl. untracked) is the normative probe, stated in REQ-YF-PRE-009. |
| C8 | Env "three seams" stale — now four | low | resolved | Env finding + Issue 3.3 updated to **four** seams (Dirs + Source + suppression + dirty). |
| C9 | Stamp blind to dirtiness; clean↔dirty same-version edge | low | resolved | One sentence added to Approach/Epic 2: stamp intentionally excludes dirtiness (avoid per-rebuild thrash); same-`CARGO_PKG_VERSION` clean↔dirty does not invalidate — accepted dev-only edge. |
| C10 | Dirty bypass reachability narrow vs `nag_eligible()` | low | resolved | Risks row notes the residual reachable case ("dirty binary copied over a receipted vendor prefix"); kept as defense-in-depth. |
| — | Missing: degradation-branch coverage note + normative probe | — | resolved | 3.5 notes `is_dirty_build()` env read is coverage-exempt (YF_GIT_HASH precedent); normative probe pinned in REQ-YF-PRE-009 (Issue 1.1). |

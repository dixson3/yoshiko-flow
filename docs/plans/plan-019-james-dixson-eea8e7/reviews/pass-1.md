---
type: Review
okf_spec: OKF-PLAN
plan: plan-019-james-dixson-eea8e7
date: '2026-07-02'
reviewer: Red-Team (adversarial, read-only)
status: frozen (all concerns resolved in plan v2)
---
# Red-Team Review — pass 1

**Plan:** plan-019-james-dixson-eea8e7
**Date:** 2026-07-02
**Reviewer:** Red-Team (adversarial, read-only)
**Status:** frozen (all concerns resolved in plan v2)

## Verdict: REVISE

The design is fundamentally sound and reuses the right machinery, but three items need to be
pinned down before approval: the cache-invalidation persistence semantics (a silent
stale-masking trap), the positive-offer test seam (infeasible as scoped against
`source::detect`/`current_exe`/`CI`), and the motivation-vs-design tension around eventual
consistency. None are fatal; all are addressable in the plan text.

## Strengths

- Correctly identifies that `nag.rs` already holds the reusable, network-free pieces
  (`CheckCache` read, `nudge_line`, `compare_versions`, `nag_eligible`, `suppressed`) and that
  only `fetch_latest_tag` is the network call preflight must avoid. The "reuse, don't
  duplicate; network stays in nag.rs" split is the right factoring.
- The offer-as-`instructions`-string approach genuinely mirrors the existing
  `detect_canonicalization_drift` fold on the ok path, so it honors the "no mutation beyond
  scaffold" contract and does not disturb the failing-status JSON key order.
- SPEC-first sequencing (Epic 1 before 2-3, coverage gate as Epic 4) matches AGENTS.md, and the
  version-stamp-as-invalidation-mechanism (no explicit clear in `update.rs`) is elegant and
  correctly justified by the arbitrary-cwd argument.

## Concerns

- **C1 — Cache-invalidation reset can silently mask broken prerequisites — severity: high.**
  Issue 2.1 offers two implementations ("via `write_state_key` / a single `ensure_version_stamp`
  at run start"). `write_state_key` *merges* keys, preserving siblings. If a mismatched stamp is
  handled by merge-writing the new `yf-version` while leaving the stale `prereqs-present: true`
  in the file, deps are NOT re-probed and invalidation fails silently — the exact bug the epic
  exists to prevent. Worse: if the reset re-stamps at run start but the run then fails at
  `system_deps_missing` (early return before any success write), the file ends up with a new
  matching stamp *and* a stale `prereqs-present: true` → the next run short-circuits and returns
  ok despite missing deps. **Permanent stale-masking.**
  Recommendation: specify that on a stamp mismatch the reset must *rewrite the persisted state*
  to drop `prereqs-present` and `scaffold-ensured` (e.g. overwrite to `{"yf-version": NEW}`)
  *before* proceeding with cold logic, and that the fresh stamp is persisted unconditionally at
  reset time — never a merge that preserves the stale bool/int. Add a test: mismatched stamp + a
  run that fails deps must leave `prereqs-present` absent (re-probes next run), not `true`.

- **C2 — The positive-offer test is infeasible as scoped — severity: high.**
  Issue 3.4 requires "newer cached tag → offer present" exercised through `run_with_env` on the
  ok path, and Env's finding claims a single "injectable cache path / source" seam. But
  `detect_self_update_offer` as specified calls `source::detect(dirs).nag_eligible()`, and
  `source::detect` reads `std::env::current_exe()` with **no injection seam** — in a test the exe
  is the test binary, never under a vendor prefix, so it classifies `Unknown` and the offer can
  never fire (see `non_vendor_source_is_not_notified`, which relies on exactly this).
  Additionally, `suppressed()` keys on the `CI` env var, which CI runners set, so a real-env
  positive test would be suppressed in CI. The seam story is under-specified: you need three
  injection points (cache path, install source, and suppression predicate), not one.
  Recommendation: build `detect_self_update_offer` on the pure `source::classify` (inject the exe
  path or a resolved `Source`) and on the pure `suppressed(present)` closure, so the positive
  path is drivable without touching `current_exe`/`CI`. State this seam explicitly in Epic 3 and
  in the Env finding; otherwise Issue 3.4 cannot be written.

- **C3 — Motivation and design are in tension — the offer may never fire for the exact users it
  targets — severity: medium.**
  The motivation argues the problem is that operators "rarely run `yf version`/`yf doctor`," so
  the nudge never appears. But the *only* writer of `update-check.json` is `nag.rs::try_notify`,
  invoked from `yf version`/`yf doctor`. A cache-only preflight offer therefore still depends on
  those same commands to seed the cache — a user who never runs them gets a perpetually empty
  cache and never sees the preflight offer either. The design does not solve the stated failure
  mode; it only helps users who occasionally run version/doctor.
  Recommendation: either (a) reconcile the motivation to the narrower claim ("surface the
  already-known availability at the point of use"), or (b) reconsider the zero-latency
  absolutism — a throttled, fail-open background refresh in preflight (its own 24h throttle)
  would actually close the gap the motivation describes. At minimum, name `yf version`/`doctor`
  as the sole cache seeder in the risk table so the limitation is explicit.

- **C4 — REQ-YF-SELF-007 is a non-action requirement; the coverage gate may flag it —
  severity: medium.**
  SELF-007 asserts that `update.rs` does *nothing* (no explicit cache-clear). There is no code
  change to tag a test against; the only observable behavior lives in the stamp-mismatch path
  (which is PRE-008's test). Issue 2.3 tags tests "per REQ-YF-PRE-008 / SELF-007" as a shared
  tag, but if the coverage gate maps tags 1:1 or requires a distinct assertion per REQ, SELF-007
  will read as uncovered at Epic 4.
  Recommendation: decide up front whether SELF-007 is a testable REQ satisfied by the shared
  PRE-008 stamp-mismatch test (and confirm the gate accepts multi-tagged coverage), or mark it a
  spec-only cross-reference REQ exempt from the coverage gate. Pin this in Issue 1.1 so Epic 4
  doesn't stall.

- **C5 — Only one of two ok-path return points is obviously covered — severity: low.**
  `run_with_env` has two ok exits: the no-companion-rule early return (folds only `drift_offer`)
  and the rule ok/update_available arm. Issue 3.3 says "wire alongside `drift_offer`" without
  specifying both. A skill with no companion rule would miss the offer.
  Recommendation: explicitly state both ok return points get the offer.

- **C6 — "Zero latency" is a slight overstatement — severity: low.**
  Computing the offer on every warm ok path adds `source::detect` (a `current_exe` canonicalize +
  receipt/marker file reads) per preflight invocation. It is not a network call and is cheap, but
  it is not literally zero.
  Recommendation: soften the claim to "no network latency" and note the small filesystem cost.

## Missing

- No test asserting the invalidation reset drops (not preserves) the stale
  `prereqs-present`/`scaffold-ensured` on a *failing* post-reset run — the highest-value
  regression guard for Epic 2 (see C1).
- No stated handling for the `CI`/suppression seam in the preflight tests, despite Issue 3.4
  listing `suppressed() → none` as a case (you cannot test both the positive and the suppressed
  case without an injectable predicate).
- Epic 1.2 updates `preflight-contract.md` to document a non-empty `instructions` on the ok path
  for a *new* reason (self-update), but the plan does not note that contract §2.1 currently
  characterizes ok `instructions` as "`[]` or update-available note" — that sentence needs
  widening so the doc and behavior agree.

## Gate Assessment

Gates are minimal and appropriate: a human Start Gate and an auto Reconcile Gate tied to the
coarse land-the-plane issue. No over-gating. The one substantive gate — the SPEC coverage gate at
Epic 4 — is realistic *only* if the plan lands Epics 1-4 as a single change-set (or marks
intermediate REQs pending); if the coverage gate runs per-PR and epics ship as separate PRs, Epic
1's PR (REQ text, no tests yet) fails the gate. AGENTS.md's "stage in the same change-set, ahead
of code" language supports the single-change-set reading, so this is a sequencing note, not a
blocker — but the plan should state it. The `cargo test --workspace` + `uv` pytest full tier is a
valid, sufficient validation command.

## Upstream Assessment

Dispositions are reasonable and honest. #62 (yf-spec skill) is correctly scoped out with a clear
rationale (plan-019 only adopts the SPEC-first ordering it motivated, not the skill). The coarse
"one tracking issue per plan at land-the-plane" convention matches AGENTS.md and the cited
precedent. No partials or supersedes to scrutinize.

## Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| C1 | Reset must overwrite (not merge) stale cache; re-stamp only after success | high | resolved | Approach + Issue 2.1/2.2 now specify a `reset_stale_cache` overwrite dropping `prereqs-present`/`scaffold-ensured` before cold logic; `prereqs-present` re-persisted only after a successful probe. Issue 2.3(d) adds the failing-post-reset regression test. |
| C2 | Positive-offer test seam infeasible; need pure classify + suppressed injection | high | resolved | Env finding + Issue 3.2/3.3/3.4 rebuilt on three injectable seams (cache path, resolved `Source` via pure `source::classify`, `suppressed(present)` closure); positive path no longer depends on `current_exe`/`CI`. |
| C3 | Motivation vs cache-only eventual consistency; name sole cache seeder | medium | resolved | Operator away; applied recommended option — kept cache-only, narrowed the motivation to "surface already-known availability at point of use," and named version/doctor as the sole cache seeder in the Risks table. |
| C4 | SELF-007 non-action REQ vs coverage gate | medium | resolved | Issue 1.1 pins SELF-007 as satisfied by the shared PRE-008 stamp-mismatch test (multi-tag), or gate-exempt spec-only if the gate maps tags 1:1. |
| C5 | Both ok-path return points must fold the offer | low | resolved | Issue 3.3 explicitly folds the offer into both `run_with_env` ok returns (no-companion-rule early return + rule ok/update_available arm). |
| C6 | "Zero latency" → "no network latency" + small fs cost | low | resolved | Approach reworded to "no network latency"; Risks table notes the small `source::classify` + cache-read filesystem cost. |

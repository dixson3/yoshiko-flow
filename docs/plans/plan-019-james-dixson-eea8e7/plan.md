# Plan: Preflight yf self-update availability offer + preflight cache version-invalidation

**ID:** plan-019-james-dixson-eea8e7
**Author:** james-dixson
**Created:** 2026-07-02
**Status:** approved
**Epic:** yf-mol-99w
**Phase log:**
- 2026-07-02 scoping: initial scope captured
- 2026-07-02 drafting: plan v1 presented
- 2026-07-02 drafting: SPEC-first reorder; #62 recorded
- 2026-07-02 review: red-team pass 1: REVISE (2 high, 2 med, 2 low)
- 2026-07-02 drafting: plan v2: red-team C1-C6 resolved
- 2026-07-02 approved: operator approved
- 2026-07-02 intake: epic yf-mol-99w poured

## Objective

Extend the shared preflight kernel (`yf/src/preflight.rs`) with two linked capabilities:

1. **Self-update availability OFFER.** When a newer `yf` is available, preflight surfaces an
   **offer** (never an auto-apply) to run `yf self update` — which in the same operation
   already refreshes the installed skill definitions/rules (`update.rs` Issue 3.7) — and tells
   the operator they likely need to `/reload-skills` afterward.
2. **Preflight cache version-invalidation.** Record the `yf` version that generated each
   `.yf/<skill>/preflight.json`; a version mismatch is a full cache miss (re-probe system-deps
   + bd, re-run the scaffold ensure). This is the mechanism by which `yf self update`
   invalidates preflight: the swapped binary reports a new `crate::VERSION`, so the next
   preflight run finds a stale stamp and re-validates from scratch — no explicit cache-clear
   in `update.rs`, which is correct since `yf self update` runs from an arbitrary cwd, not
   necessarily inside a beads repo.

## Motivation

Preflight is the single choke point every beads-backed skill (`yf-plan`, `yf-research`,
`yf-beads-*`, the `beads` loop) passes through before doing work. Two gaps exist today:

- **Availability is known but not surfaced at the point of use.** The self-update nudge
  (plan-018 Issue 4.1, `nag.rs`) fires only on `yf version` / `yf doctor`, writing the latest
  tag to the shared `update-check.json` cache. Preflight — the point where the operator is
  actually about to rely on the toolchain — never consults that cache, so a *known-available*
  update goes un-offered through dozens of skill invocations. **Scope (honest, per red-team
  C3):** this surfaces already-known availability at the point of use; it does **not** help a
  user who never runs `version`/`doctor` (they are the sole cache seeder — see Risks). Closing
  that seeding gap is out of scope (cache-only preflight is a deliberate zero-network choice).
- **Cache can outlive its generating binary.** `preflight.json` caches `prereqs-present`
  (system-deps + bd version) indefinitely. After a `yf self update` that bumps, say,
  `min-bd-version` or tool expectations, the stale `prereqs-present: true` would mask a
  now-failing prerequisite. The cache must be tied to the binary that wrote it.

Triggered by operator request (this session): add the availability check to preflight as an
offer, bundle the skill-definition refresh (already bundled in `yf self update`), and make
`yf self update` invalidate the preflight cache via a recorded generating-version stamp.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| [#62](https://github.com/dixson3/yoshiko-flow/issues/62) | Propose yf-spec skill | exclude | Spun-off future work — a dedicated SPEC-management skill. Not in plan-019 scope; plan-019 only adopts the SPEC-first ordering it motivates. | — |

No tracking issue is filed for plan-019's own work yet. Per the repo's **coarse** upstream
convention (one tracking issue per plan), a single GitHub issue will be filed at land-the-plane.

## Investigation Findings

Grounded by direct read of the existing code (no sub-agent experiments needed — the surfaces
are small and self-contained):

- **`nag.rs` already holds the reusable machinery**: `compare_versions` /
  `VersionCmp::UpdateAvailable`, `nudge_line`, the 24h throttle, the shared cache
  `~/.cache/yf/update-check.json` (`CheckCache { last_check_epoch, latest_tag }`), vendor-only
  gating via `source::detect(dirs).nag_eligible()`, and `suppressed()` (`YF_NO_UPDATE_CHECK` /
  `CI`). The network fetch (`fetch_latest_tag`) is the only piece preflight must **not** call.
- **`update.rs` already refreshes skills/rules post-update** (`refresh_user_skills`,
  `RefreshReport`, Issue 3.7 / REQ-YF-SELF-005). So "update skill definitions in conjunction"
  is already true of `yf self update` — the plan only needs the offer to *say so* and to point
  at `/reload-skills`.
- **`preflight.rs` cache surface**: `read_state` / `write_state_key` on
  `.yf/<skill>/preflight.json`; `prereqs-present` (bool) and `scaffold-ensured` (int) are the
  cached keys. `run_with_env` short-circuits top-to-bottom; the `ok`-path already folds a
  `drift_offer: Vec<String>` into `instructions` — the new self-update offer folds in exactly
  the same way. `crate::VERSION` is the generating-version source.
- **`Env` seams — three injection points, not one (red-team C2).** `source::detect` reads
  `std::env::current_exe()` with no seam, and `suppressed()` keys on `CI` (which CI runners set),
  so the positive-offer path is **untestable** if built on `source::detect` + `suppressed()`
  directly. `detect_self_update_offer` must instead take (1) an injectable **cache path**, (2) a
  resolved **`Source`** (via the pure `source::classify`, injecting the exe path), and (3) the
  pure **`suppressed(present)`** closure. `Env::live()` wires the live values (`Dirs`,
  `source::detect`, real env); test constructors inject a vendor `Source` + a seeded cache + a
  no-suppression predicate to drive the positive case, and default to a none-yielding cache so
  existing tests emit no offer.

## Approach

**Reuse, don't duplicate.** Extract the cache-read + offer-line computation from `nag.rs` into
shared helpers so preflight and the version/doctor nudge share one code path; `nag.rs` keeps
sole ownership of the *network* fetch. Preflight is strictly **cache-only** (operator decision):
it reads `update-check.json` and never touches the network, so it adds **no network latency** to
a skill invocation (a small filesystem cost remains — `source::classify` on the exe path plus the
cache read; red-team C6). Consequence (documented tradeoff): the preflight offer is *eventually
consistent* — it appears once the throttled `yf version`/`yf doctor` path has refreshed the
shared cache. That is an accepted cost of the zero-network guarantee.

**Offer-only, honoring preflight's contract.** Preflight performs no mutation beyond the
gitignore scaffold. The offer is an `instructions` string (exactly like `detect_canonicalization_drift`'s
`yf doctor --repair` offer); the calling skill/agent decides whether to present it
interactively. Preflight never runs `yf self update` itself.

**Version stamp = invalidation mechanism.** `run_with_env` stamps `yf-version: <crate::VERSION>`
into `preflight.json`. At the top of a run, if the stamped version differs from `crate::VERSION`
(or is absent), treat the whole file as a cache miss (operator chose **full reset**). **Critical
persistence rule (red-team C1):** the reset must **overwrite** the persisted state to *drop*
`prereqs-present` and `scaffold-ensured` (e.g. write `{"yf-version": <NEW>}`) **before** the cold
logic runs — never a `write_state_key` *merge* that preserves the stale bool/int. The
`prereqs-present: true` flag is (re)persisted **only after** a successful probe on this run, so an
early `system_deps_missing` return leaves the cache correctly empty (re-probes next run) rather
than stamping a new version over a stale-true flag. Nothing in `update.rs` changes — the stamp
makes invalidation automatic and location-independent.

**Nudge surfaces supplement, not replace** (operator decision): the `version`/`doctor`
notify-only nudge stays; preflight adds the actionable offer.

## Epics

**SPEC-first ordering (AGENTS.md).** The normative SPEC/contract edits are Epic 1 and land
**before** any implementation. Implementation epics reference the REQ ids allocated in Epic 1;
each testable REQ is satisfied by a tagged test in its implementation epic, and the SPEC
coverage gate is the final check (Epic 4). **Single-change-set landing (red-team Gate note):**
Epics 1–4 land as one change-set (or the SPEC coverage gate runs only at Epic 4), because a
per-PR gate would fail on Epic 1's REQ text before its tags exist — this matches AGENTS.md's
"stage in the same change-set, ahead of code."

### Epic 1: SPEC + contract requirements (SPEC-first)

- Issue 1.1: **SPEC.md** — allocate and write `REQ-YF-PRE-008` (generating-version stamp +
  full-reset invalidation), `REQ-YF-PRE-009` (cache-only, vendor-only, offer-only self-update
  offer in preflight instructions), and `REQ-YF-SELF-007` (`yf self update` invalidates preflight
  caches *by virtue of* the version stamp — the new binary's `VERSION` differs → next preflight
  is a cache miss; no explicit clear in `update.rs`). Add the living-amendment-log entry. Each
  new testable REQ names the test tag its implementation epic must provide. **SELF-007 coverage
  decision (red-team C4):** SELF-007 is a *non-action* REQ (asserts `update.rs` does nothing) —
  classify it as **satisfied by the shared PRE-008 stamp-mismatch test** and confirm the coverage
  gate accepts a test tagged for multiple REQs; if the gate maps tags 1:1, instead mark SELF-007
  **spec-only / gate-exempt** with an inline note. Pin the choice here so Epic 4 cannot stall.
- Issue 1.2: **docs/yf/preflight-contract.md** — document the `yf-version` state field, the
  full-reset invalidation semantics, and the new self-update offer instruction on the `ok` path
  (cache-only / eventually-consistent, vendor-only gating). **Widen §2.1 (red-team Missing):** the
  contract currently characterizes ok `instructions` as "`[]` or update-available note" — broaden
  that sentence so a self-update offer string on the ok path agrees with the doc. Normative
  surface → lands with Epic 1.
  - depends-on: 1.1

### Epic 2: Preflight cache version-stamp + invalidation (implements REQ-YF-PRE-008 / SELF-007)

- Issue 2.1: On a stamp mismatch/absence, **overwrite** `preflight.json` to drop
  `prereqs-present` + `scaffold-ensured` before cold logic (a dedicated `reset_stale_cache` that
  writes `{"yf-version": <NEW>}`), **not** a `write_state_key` merge (red-team C1). Persist
  `prereqs-present: true` only *after* a successful probe this run.
  - depends-on: 1.1
- Issue 2.2: At the top of `run_with_env`, read the stamped `yf-version`; if it differs from
  `crate::VERSION` or is absent, invoke the reset from 2.1, then proceed with cold logic
  (re-probe deps + bd, re-run the idempotent scaffold). A fresh file (no stamp) takes the same
  cold path.
  - depends-on: 2.1
- Issue 2.3: Tests (tagged per REQ-YF-PRE-008 / SELF-007) — (a) matching stamp honors the cache
  (deps not re-probed); (b) mismatched stamp forces a deps re-probe **and** a scaffold re-run;
  (c) the stamp is persisted with the current `crate::VERSION`; **(d) red-team C1 regression: a
  mismatched stamp on a run that then fails `system_deps_missing` leaves `prereqs-present`
  ABSENT (re-probes next run), never `true`.** Carry `preflight_parity` where they assert
  contract JSON.
  - depends-on: 2.2

### Epic 3: Preflight self-update availability offer (implements REQ-YF-PRE-009)

- Issue 3.1: Extract shared, network-free helpers out of `nag.rs`: the `CheckCache` read, the
  cache path (`dirs.cache_dir().join("update-check.json")`), and an offer/nudge line computed
  from `(current, cached_tag)`. `nag.rs` retains `fetch_latest_tag` (the only network call) and
  now consumes the shared helpers; no behavior change to the version/doctor nudge.
  - depends-on: 1.1
- Issue 3.2: `detect_self_update_offer` in `preflight.rs` built on **testable seams (red-team
  C2)**: it takes an injectable cache path, a resolved `Source` (from the pure `source::classify`,
  not `source::detect`), and the pure `suppressed(present)` closure. Returns an offer
  `instructions` string when **all** hold: not suppressed, `Source` is vendor
  (`nag_eligible()`), and the **cache-only** read yields `VersionCmp::UpdateAvailable`. The
  string offers `yf self update` (noting it also refreshes skill definitions/rules) and that the
  operator likely needs to `/reload-skills` afterward. **No network.**
  - depends-on: 3.1
- Issue 3.3: Add the three live seams to `Env` (`Dirs` + resolved `Source` + suppression),
  wired in `Env::live()`. Fold the offer into **both** `ok`-path return points of `run_with_env`
  — the no-companion-rule early return **and** the rule ok/update_available arm (red-team C5) —
  alongside `drift_offer`. Test constructors default to a none-yielding cache so existing tests
  emit no offer.
  - depends-on: 3.2
  - soft-order-after: 2.2 (same `run_with_env` region — sequence to reduce churn)
- Issue 3.4: Tests (tagged per REQ-YF-PRE-009), driven via the injected seams — newer cached tag
  + vendor `Source` + no-suppress → offer present (on **both** ok returns); same/older/empty
  cache → none; non-vendor `Source` → none; suppression predicate true → none; and an assertion
  that **no network call** occurs (cache-only). Exercise through `run_with_env` on the `ok` path.
  - depends-on: 3.3

### Epic 4: Coverage gate + user docs

- Issue 4.1: Run the SPEC coverage gate; confirm `REQ-YF-PRE-008`, `REQ-YF-PRE-009`, and
  `REQ-YF-SELF-007` are covered per the Issue 1.1 decision (shared tag or gate-exempt).
  - depends-on: 2.3, 3.4
- Issue 4.2: **CHANGELOG.md** Unreleased entry; update README / `website/docs/install.md` only
  if the offer wording is user-facing enough to warrant it (otherwise note "no user-doc change").
  - depends-on: 4.1

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Reconcile Gate

- Type: auto (all execution beads closed)
- Blocks: the land-the-plane coarse upstream issue for plan-019

## Risks & Mitigations

| Risk | Mitigation |
|:--|:--|
| Cache-only offer never appears if the user never runs `version`/`doctor` (red-team C3) | `yf version`/`yf doctor` (`nag.rs::try_notify`) are the **sole** writers of `update-check.json`; preflight is a reader only. Accepted, documented tradeoff of the zero-network guarantee — the offer surfaces *already-known* availability at the point of use and supplements (never replaces) the version/doctor nudge. |
| Adding seams to `Env` breaks the unit-test seam (red-team C2) | `Env::live()` resolves the live `Dirs` + `Source` + suppression; test constructors inject them. The positive path is built on pure `source::classify` + `suppressed(present)` (no `current_exe`/`CI` dependency), and defaults to a none-yielding cache so all existing preflight tests are unaffected. |
| Offer computation adds a small per-invocation filesystem cost (red-team C6) | Not a network call — `source::classify` on the exe path + one cache read; cheap and fail-open. The claim is "no network latency," not literally zero cost. |
| Version stamp churns `preflight.json` on every yf release, re-probing deps needlessly | Intended — a new binary should re-validate its own prerequisites once; the probe is cheap and cached again immediately after. |
| Offer fires for non-vendor (Homebrew/from-build) installs that can't `yf self update` | Reuse `nag_eligible()` — identical vendor-only gate as the existing nudge. |
| Full reset re-runs the scaffold ensure | Scaffold ensure is idempotent/additive; a re-run is a no-op when anchors already present. |

## Success Criteria

- Preflight on a vendor install with a cached newer tag emits a `yf self update` offer in
  `instructions` (mentioning skill-def refresh + `/reload-skills`), with **no network call** and
  no mutation beyond scaffold.
- Preflight on a non-vendor install, a suppressed env, or an up-to-date cache emits **no** offer.
- A `preflight.json` written by an older `yf-version` forces a full re-validation (deps re-probed,
  scaffold re-ensured, stamp updated) on the next run; a matching stamp honors the cache.
- `REQ-YF-PRE-008`, `REQ-YF-PRE-009`, `REQ-YF-SELF-007` are in SPEC.md, each covered by a tagged
  test, and the SPEC coverage gate passes.
- `cargo test --workspace` and the `uv` pytest row (the approved CHANGE-VALIDATION full tier)
  pass over the merged tree.
- The version/doctor nudge behavior is unchanged (supplement, not replace).

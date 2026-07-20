---
id: plan-030-james-dixson-65526e
author: james-dixson
created: '2026-07-19'
status: complete
epic: yf-mol-tmm
fingerprint: 4c58c5563ba3c9b0116993e63d62570a707dc8000c7fb2748ace325b37cd88fd
---
# Plan: yf-plan CI/infra/release completion criterion: gate 'complete' on one green execution or a deferred-validation bead (REQ-PLAN-069)

**ID:** plan-030-james-dixson-65526e
**Author:** james-dixson
**Created:** 2026-07-19
**Status:** complete
**Epic:** yf-mol-tmm
**Fingerprint:** 4c58c5563ba3c9b0116993e63d62570a707dc8000c7fb2748ace325b37cd88fd
**Phase log:**
- 2026-07-19 scoping: initial scope captured
- 2026-07-19 scoping: upstream #89 triaged (include); 3 scope decisions resolved (detection / enforcement / evidence)
- 2026-07-19 drafting: plan v1 presented
- 2026-07-19 review: plan v1 presented
- 2026-07-19 review: pass-1 REVISE resolved (C1-C4); re-review
- 2026-07-19 ready-for-approval: ready-check green — last red-team APPROVE (pass-2) + audit pass
- 2026-07-19 approved: operator approved
- 2026-07-19 intake: epic yf-mol-tmm poured
- 2026-07-20 executing: start gate resolved
- 2026-07-20 reconciling: post-execution reconciliation

## Objective

Add a completion criterion to yf-plan's RECONCILE/land-the-plane so that plans whose **primary
deliverable is CI/infra/release configuration** — code whose correctness is only observable when it
runs on the target — cannot be marked `complete` while their central behavior is unverified. A
ci-release plan reaches `complete` only when **one** of two things is true: (a) one **green real
execution** of the deliverable has been observed and attested, or (b) an **open, upstream-tracked
deferred-validation bead** carries the unverified-behavior signal forward. Also codify the
`workflow_dispatch` no-publish "test build" pattern as the recommended mechanism for satisfying (a)
without cutting a real release.

## Motivation

**Lesson from pybridge plan-010 (CI code signing), recorded in upstream #89.** That plan was marked
`complete` when its code merged — but the behavior it *delivers* (code signing running on
self-hosted macOS/Windows runners) had **never actually executed**. Validating it afterward
surfaced **~a dozen distinct runner-environment bugs** across 13 release-candidate iterations (bash
3.2 empty-array/functions, GitHub `shell: bash` injecting `-e`, MSYS arg mangling, CRLF, `set
-e`+unzip, pretty-printed-JSON parsing, non-ASCII in shell, Azure dlib x86-vs-x64,
gh-release-upload silent no-op, softprops asset-wipe, blob-storage upload stalls, a
notarization-propagation Gatekeeper modal, a version/tag collision). **None were catchable at merge
time** — CI config that runs on flaky, self-hosted runners cannot be validated locally, and
`merged` is not `works`.

Today yf-plan's RECONCILE (§6) validates the *merged tree* (REQ-PLAN-060/061 layer-b), but that
only runs the repo's build/test suite on the landing machine. It cannot observe a workflow that only
executes on push/dispatch/release against real runners. So a CI/infra/release plan can pass every
existing gate and read as `complete` with its central behavior entirely unexercised. This plan
closes that specific gap **without** over-broadening: ordinary plans (whose deliverable *is*
observable in the merged-state validation) are untouched.

Who is affected: any operator running a `/yf-plan` plan whose deliverable is a GitHub Actions
workflow, a release pipeline, signing/notarization, an infra/deploy config, or similar
runner-only-observable behavior.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| [#89](references/upstream-89.md) | yf-plan: for CI/infra/release plans, require one green end-to-end execution before 'complete' | include | The sole driver. Coarse tracking issue for this plan. | plan-030 |

Adjacent-but-excluded: **#90** (yf-change-validation default recipe of actionlint + shellcheck for
`.github/workflows` repos) is a *validation-recipe* concern for a different skill
(`yf-change-validation`), orthogonal to yf-plan's completion criterion — not in scope.

## Investigation Findings

No investigation phase — the design was fully determined at scope time (issue #89 is a detailed
proposal; the three open forks were resolved by operator decision). Grounding reads of the
implementation surface, folded into Approach below:

- **`close_cascade.py`** is the existing §6.4 fail-loud hard-gate model (exit `2` → completion
  halts, `update-status complete` never runs). REQ-PLAN-069's gate mirrors this shape but is a
  **separate concern** (behavioral-validation vs container-closure), so it gets its own
  `plan_manager.py` verb rather than folding into `close_cascade.py` (single responsibility).
- **The content fingerprint excludes every `**Field:**` header line** (REQ-PORT-040), so a
  `**Deliverable-class:**` header marker written at intake does not stale the approved fingerprint.
  **But fingerprint-exclusion ≠ durability:** `_rebuild_field_block` (plan_manager.py:72-103)
  re-emits **only** `PLAN_FIELD_ORDER` keys, dropping any unregistered field on the next
  `update-status`/`record-epic` write. So the marker must be a **registered canonical dual-write
  field** (`deliverable_class`↔`**Deliverable-class:**`, added to `PLAN_FIELD_LABELS`,
  `PLAN_FIELD_ORDER`, and the REQ-DATA-015 frontmatter model) to truly behave "like `**Epic:**`"
  — the raw header-line approach is silently lossy.
- **The live phase history is the reserved `log.md`, not an in-`plan.md` block** (REQ-DATA-012):
  heading-grouped, newest-first `## YYYY-MM-DD` + `- <status>: <msg>` bullets, written via
  `okf.append_log`. So the green-execution evidence must be a `log.md` bullet (`- validated: …`),
  and `complete-gate` reads `log.md` (plan.md `**Phase log:**` fallback only for un-migrated
  bundles) — **not** a `plan.md` inline-date grep.
- **`close_cascade.cascade()` fail-louds (exit 2) on any container with any open child** in the
  plan tree, and it runs at §6.4 **before** `complete-gate`. So a deferred-validation bead that
  permits completion **must live outside the plan molecule tree** (a standalone, individually
  upstream-tracked bead), or the cascade halts completion before the gate can honor it.
- The **living amendment log** is the repo-root `SPEC.md` (precedent: REQ-PLAN-068 → "root SPEC.md
  plan-028").

## Approach

**SPEC-first, then implementation + tagged tests** (per AGENTS.md). Land the `REQ-PLAN-069` family
and its supporting spec text ahead of any code, then build the two script verbs, wire the SKILL.md
prose, and add Tier-1 unit tests.

### Detection — "both: suggest + confirm" (operator decision)

A new **registered canonical dual-write field** `deliverable_class`↔`**Deliverable-class:**` in
`plan.md` is the **source of truth** at reconcile. Values: `ci-release` (the gated class) or
`standard` (default; criterion N/A). It is added to `PLAN_FIELD_LABELS`, `PLAN_FIELD_ORDER`, and the
REQ-DATA-015 dual-write frontmatter model — **not** a raw header line — so it survives every
`update-status`/`record-epic` rewrite (per C3: `_rebuild_field_block` re-emits only registered
fields) while staying fingerprint-excluded (above the first `## `, REQ-PORT-040). A heuristic
(`plan_manager.py classify-deliverable`) scans the plan's epics/upstream/success-criteria text and
the merged-tree changed paths for ci-release signals (`.github/workflows/**`, `release`/`notarize`/
`sign`/`deploy` keywords, self-hosted-runner references) and **suggests** a class; the operator
**confirms or overrides**, and the confirmed value is written via the dual-write field writer. If
the field is absent or `standard`, the reconcile criterion is a **no-op** — ordinary plans are never
gated.

### Enforcement — "hard gate" (operator decision)

At the §6.4 close step, **after cascade-close and before** `update-status complete`, RECONCILE runs
a new `plan_manager.py complete-gate` verb. For a `ci-release` plan it **halts completion** (exit
non-zero, JSON verdict — mirroring the `close_cascade.py` fail-loud contract) unless **at least
one** of:

1. **Green-execution evidence** — a `log.md` bullet `- validated: <run URL/id> — <note>` exists
   (the operator's attestation of one observed green run); **or**
2. **Deferred-validation bead** — an **open** bead tagged `deferred-validation` and scoped to this
   plan (`bd` label `deferred-validation` + metadata `{"plan":"<plan-id>"}`), discovered by a
   `bd list --label deferred-validation` filter — **not** a plan-tree child.

**C1 resolution — the deferred bead lives OUTSIDE the plan molecule tree.** Because `close_cascade`
runs first and fail-louds on any open child in the tree, the deferred-validation bead is created as
a **standalone** bead (no `--parent` into the plan epic) and is **individually pushed upstream** —
a deliberate per-bead exception to the coarse-granularity convention, which UPSTREAM_TRACKING's
deferred/follow-on push path already sanctions. This keeps cascade-close and the Reconcile Gate
("all execution beads closed") both satisfied while the plan's central behavior stays visibly
unverified upstream. `complete-gate` finds it by label filter, never by walking the (now-closed)
plan tree.

If neither holds, completion halts with an actionable message (how to attest, or how to file the
standalone deferred bead). This is a testable hard precondition, parallel to REQ-PLAN-067.

### Evidence — "operator-attested log.md line" (operator decision)

One green execution is recorded as a `log.md` bullet `- validated: <run URL/id> — <note>` under the
current `## YYYY-MM-DD` heading (e.g. a `workflow_dispatch` no-publish test-build run, or an actual
release run), written via `okf.append_log`. Trust-based, portable, no CI-API coupling.
`complete-gate` reads `log.md` (plan.md `**Phase log:**` fallback for un-migrated bundles) and
matches the bullet form `- validated:`. A helper `plan_manager.py attest-validation` appends a
well-formed bullet via `append_log`, but a hand-written bullet is equally valid. `validated:` joins
`intake:` as a recognized **non-status** `log.md` token — no review-count (REQ-PORT-006),
grandfather-date, or status parser keys on it (C4).

### workflow_dispatch no-publish "test build" pattern (codify)

Document, as the recommended way to satisfy the green-execution criterion for release pipelines
without cutting a real release: add a `workflow_dispatch` trigger and **guard the publish/release
job** on `github.event_name != 'workflow_dispatch'`, so a manual dispatch exercises the full build
on real runners but publishes nothing. Lives as a spec/ guidance section + a reference snippet.

## Epics

### Epic 1: SPEC-first — REQ-PLAN-069 family + supporting spec text

- Issue 1.1: Add **REQ-PLAN-069** *(testable)* to `skills/yf-plan/SPEC.md` §2.7 — the hard
  completion gate for `ci-release` plans (green-execution attestation OR open deferred-validation
  bead), fail-loud parallel to REQ-PLAN-067.
- Issue 1.2: Add supporting requirements — a **detection** requirement (the `deliverable_class`
  **registered canonical dual-write field**, heuristic-suggest + operator-confirm, fingerprint-
  excluded AND durable across field-block rewrites) and an **evidence** requirement (the `log.md`
  `- validated:` bullet convention, and `validated:` as a recognized non-status token). Update §3
  Interfaces to list the new `classify-deliverable` / `complete-gate` / `attest-validation` verbs;
  update §5 Verification.
  - depends-on: 1.1
- Issue 1.3: Update `spec/data.md` — register `deliverable_class`↔`**Deliverable-class:**` in the
  REQ-DATA-015 dual-write set and `PLAN_FIELD_ORDER`; define the `- validated:` `log.md` bullet
  shape grounded in **REQ-DATA-012** (heading-grouped, via `append_log`); note the deferred bead is
  **out-of-tree** (label + `{plan}` metadata). Update `spec/phases.md` (RECONCILE §6.4 gains the
  complete-gate step: cascade-close → complete-gate → set complete; no-op for `standard`) and
  `spec/cli.md` (new verbs + their JSON shapes).
  - depends-on: 1.1
- Issue 1.4: Codify the `workflow_dispatch` no-publish test-build pattern — a guidance section
  (spec/ or SKILL.md) + a reference YAML snippet showing the `github.event_name != 'workflow_dispatch'`
  publish guard.
  - depends-on: 1.1
- Issue 1.5: Record the amendment-log entry in the **repo-root `SPEC.md`** (plan-030), referencing
  REQ-PLAN-069.
  - depends-on: 1.1

### Epic 2: Implementation — field registration, detection heuristic, gate verb, SKILL.md wiring

- Issue 2.0: Register `deliverable_class`↔`**Deliverable-class:**` as a canonical dual-write field
  in `plan_manager.py` — add to `PLAN_FIELD_LABELS`, `PLAN_FIELD_ORDER` (positioned **immediately
  after `status`**), and the frontmatter read/write model (REQ-DATA-015), with a set-verb (e.g.
  `set-deliverable-class`) writing via the dual-write field writer. This is the C3 durability fix;
  must land before 2.2 writes the marker.
  - depends-on: 1.3
- Issue 2.1: `plan_manager.py classify-deliverable "${plan_dir}" --json` — scan plan.md
  epics/upstream/success-criteria + (optional) merged-tree changed paths for the defined ci-release
  signals; return `{suggested_class, signals, confidence}` where `confidence` is `high` (a
  `.github/workflows/**` path or release/sign/notarize signal) or `low` (keyword-only). Pure read,
  no mutation. Defined contract so 2.1's test is deterministic. Note (C5): at intake no merged tree
  exists, so path signals may be absent then — the class is re-confirmable at reconcile when changed
  paths are available.
  - depends-on: 1.3
- Issue 2.2: Intake/PLAN SKILL.md wiring — run `classify-deliverable`, present the suggestion, and
  on operator confirm write the class via the 2.0 dual-write field setter (idempotent). Default
  `standard` when unset.
  - depends-on: 2.0, 2.1
- Issue 2.3: `plan_manager.py complete-gate "${plan_dir}" --json` — read `deliverable_class`; for
  `ci-release`, pass iff a `log.md` `- validated:` bullet exists OR an **out-of-tree** open bead
  with label `deferred-validation` + metadata `{"plan":"<plan-id>"}` exists (via `bd list --label`
  filter); else fail-loud (exit non-zero + JSON verdict + actionable message). For `standard`/absent,
  clean pass (no-op). Include the `attest-validation` helper appending a well-formed `- validated:`
  bullet via `okf.append_log`.
  - depends-on: 1.3
- Issue 2.4: RECONCILE §6.4 SKILL.md wiring — call `complete-gate` **after** the cascade-close block
  and **before** `update-status complete`; halt on non-zero exactly as the `close_cascade.py` block
  does. Order: cascade-close → complete-gate → set complete. Also document filing the standalone
  out-of-tree deferred bead + its individual upstream push, and (C5) a reconcile-time re-confirm of
  `deliverable_class` from the now-available merged-tree changed paths before the gate runs.
  - depends-on: 2.3

### Epic 3: Tests + verification

- Issue 3.1: Tier-1 unit tests (per TESTING.md), tagged REQ-PLAN-069, covering:
  (a) `classify-deliverable` signal detection + `standard` default + `confidence` levels;
  (b) `complete-gate` — ci-release halt with neither; pass with a `log.md` `- validated:` bullet;
  pass with an out-of-tree open `deferred-validation` bead; no-op for `standard`/absent;
  (c) **C3 round-trip** — write `deliverable_class`, call `update-status`, assert the marker
  survives the field-block rewrite;
  (d) **C1 agreement** — cascade-close (dry-run) + complete-gate agree that an out-of-tree open
  deferred bead does NOT appear as a plan-tree open child;
  (e) **C4** — a `- validated:` bullet perturbs neither `_plan_review_line_count` nor the
  grandfather-date parser.
  - depends-on: 2.0, 2.1, 2.3
- Issue 3.2: Update SPEC §5 Verification to reference the new test module; run the change-validation
  FULL tier over the merged tree.
  - depends-on: 3.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate (upstream #89 incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

_Note: this plan's own deliverable is a **skill/SPEC change** (`standard` class, not `ci-release`),
so REQ-PLAN-069's new gate does not fire on plan-030 itself — no self-referential green-execution
requirement._

## Risks & Mitigations

- **Risk: heuristic false-negative** — a genuine ci-release plan is classified `standard` and slips
  the gate. *Mitigation:* the marker is operator-confirmed (suggest + confirm), and the operator can
  set `ci-release` manually at any pre-complete point; the heuristic only nudges.
- **Risk: attestation is trust-based** — an operator could write a `validated:` line without a real
  green run. *Mitigation:* accepted by the "operator-attested" decision; the line records the run
  URL/id for auditability. Machine verification is a deliberate non-goal (no CI-API coupling).
- **Risk: over-broadening** — the gate accidentally fires on ordinary plans. *Mitigation:* the
  criterion is a strict no-op unless `**Deliverable-class:** ci-release`; default is `standard`.
- **Risk: marker staled the fingerprint** — writing the marker post-approval invalidates the
  approved plan. *Mitigation:* the marker is a header field above the first `## `, which REQ-PORT-040
  excludes from the fingerprint (verified against the existing `**Epic:**` precedent).
- **Risk: marker silently dropped (C3)** — an unregistered header field is erased by
  `_rebuild_field_block` on the next write, silently reclassifying the plan. *Mitigation:* register
  `deliverable_class` as a canonical dual-write field (Issue 2.0); Issue 3.1(c) asserts round-trip
  survival.
- **Risk: cascade-close halts before the gate honors option (b) (C1)** — an open deferred bead
  inside the plan tree fail-louds cascade-close first. *Mitigation:* the deferred-validation bead is
  **out-of-tree** (standalone + individually upstream-tracked), discovered by label filter; Issue
  3.1(d) asserts cascade-close and complete-gate agree.
- **Risk: evidence written to the wrong surface (C2)** — a `plan.md` inline-date line would never
  match the reserved `log.md`. *Mitigation:* evidence is a `log.md` `- validated:` bullet via
  `append_log` grounded in REQ-DATA-012; complete-gate reads `log.md` with a plan.md fallback.

## Success Criteria

1. `REQ-PLAN-069` (+ supporting detection/evidence requirements) is present in
   `skills/yf-plan/SPEC.md`, the amendment log in the repo-root `SPEC.md` records plan-030, and
   `spec/phases.md` / `spec/cli.md` / `spec/data.md` are updated — all landed **before** the Epic-2
   implementation beads.
2. `plan_manager.py complete-gate` **halts** a `ci-release` plan that has neither a `log.md`
   `- validated:` bullet nor an open out-of-tree `deferred-validation` bead, and **passes** when
   either exists; it is a **no-op** for `standard`/unmarked plans.
3. `plan_manager.py classify-deliverable` suggests `ci-release` on a workflow/release/signing plan
   and `standard` otherwise; the SKILL.md intake flow writes the operator-confirmed class via the
   registered `deliverable_class` dual-write field, which **survives** an `update-status` round-trip.
4. RECONCILE §6.4 calls `complete-gate` before `update-status complete` and halts fail-loud on a
   non-zero verdict (mirroring the `close_cascade.py` contract).
5. The `workflow_dispatch` no-publish test-build pattern is documented with a reference snippet.
6. Tier-1 unit tests tagged REQ-PLAN-069 cover the gate + heuristic; the change-validation FULL tier
   is green over the merged tree.

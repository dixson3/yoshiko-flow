# Plan Red-Team: plan-030-james-dixson-65526e — pass 1

## Verdict: REVISE

### Strengths

- Correctly scoped, non-over-broadening: `standard`-default / `ci-release`-opt-in with an explicit
  no-op path means ordinary plans are provably untouched; the self-referential carve-out (plan-030
  is `standard`) is stated and correct.
- SPEC-first sequencing is real (Epic 1 lands REQ-PLAN-069 + supporting reqs + amendment log ahead
  of Epic 2 code); dependency graph is coherent.
- Single-responsibility split (behavioral gate as its own verb, not folded into `close_cascade.py`)
  is the right call; the fail-loud exit-2 contract to mirror is real.
- Trust-based attestation trade-off is named and accepted, with run URL/id for auditability.

### Concerns

| # | Severity | Concern | Recommendation |
|:-:|:--|:--|:--|
| C1 | high | Option (b) deferred-validation bead contradicts the cascade-close step that runs *before* complete-gate: `close_cascade.cascade()` fail-louds (exit 2) on any container with any open child, so an open bead *inside* the plan tree halts completion before complete-gate runs. Reconcile Gate ("all execution beads closed") has the same conflict. Option (b) is unreachable as written. | Require the deferred-validation bead to live **outside** the plan molecule tree (a standalone/upstream-tracked bead the cascade never visits). complete-gate discovers it by label/metadata, not as a plan-tree child. Add a tagged test proving cascade-close + complete-gate agree. |
| C2 | high | The `validated:` evidence line uses the **retired** inline-date phase-log format and greps `plan.md`. REQ-DATA-012 relocated the live log to reserved `log.md` (heading-grouped `## YYYY-MM-DD` + `- <status>:` bullets via `okf.append_log`); the date is in the heading, not the bullet. The proposed `^- \d{4}-\d{2}-\d{2} validated:` regex against plan.md would never match. | Redefine evidence as a `log.md` bullet `- validated: <run URL/id> — <note>` under a date heading, written via `okf.append_log`; complete-gate/attest-validation read/write `log.md` (plan.md `**Phase log:**` fallback only for un-migrated bundles). Ground Epic 1.3 in REQ-DATA-012. |
| C3 | medium | "`**Deliverable-class:**` mirrors `**Epic:**`" is half true: fingerprint-exclusion holds, but durability does not. `_rebuild_field_block` re-emits **only** `PLAN_FIELD_ORDER` keys, so an unregistered field placed among the canonical block is dropped on the next `update-status`/`record-epic` write (which includes `update-status complete` at reconcile) → marker lost → `ci-release` silently reclassified `standard`. | Register `deliverable_class` as a canonical field (`PLAN_FIELD_LABELS`, `PLAN_FIELD_ORDER`, REQ-DATA-015 dual-write frontmatter). Add a Tier-1 round-trip test (write marker → `update-status` → assert survives). |
| C4 | low | `validated:` as a new `log.md` status token is under-checked against existing token parsers (collision risk low — not a plan status; `intake:` sets precedent). | One SPEC sentence noting `validated:` joins `intake:` as a recognized non-status `log.md` token no review/scoping/count parser keys on; assert in a test. |

### Missing

- No grounding read of the phase-log relocation (REQ-DATA-012 / `log.md`) — root cause of C1/C2.
- `complete-gate` tree-walk / bead-tagging mechanics unspecified (label vs metadata; how the gate
  finds the plan root).
- `classify-deliverable` signal→class mapping / `confidence` semantics unspecified (acceptable given
  suggest+confirm, but Issue 2.1's test needs a defined contract).

### Gate Assessment

Gates minimal and appropriate (human Start + existing auto Reconcile); the completion criterion as a
fail-loud script precondition (not a bd gate) is the right mechanism. But the Reconcile Gate's "all
execution beads closed" conflicts with option (b)'s open deferred bead (same root cause as C1) —
resolving C1 must also reconcile this wording.

### Upstream Assessment

Disposition sound: #89 sole driver, correctly `include` as coarse tracking issue; #90 exclusion
correctly reasoned (different skill, orthogonal). Note: option (b)'s deferred bead must be
individually upstream-tracked, which under coarse granularity is a deliberate per-bead exception
(deferred follow-ups push upstream at land-the-plane per UPSTREAM_TRACKING) — state it so the
"upstream-tracked" guarantee is met.

### Operator Resolutions

| # | Resolution | Status |
|:-:|:--|:--|
| C1 | Deferred-validation bead redefined as **out-of-tree** (standalone, no `--parent`; individually upstream-tracked per UPSTREAM_TRACKING's deferred path); complete-gate finds it by `bd list --label deferred-validation` + `{plan}` metadata, not a tree walk. cascade-close + Reconcile Gate stay satisfied. Test 3.1(d). | resolved |
| C2 | Evidence redefined as a `log.md` `- validated:` bullet via `okf.append_log` (REQ-DATA-012 heading-grouped form); complete-gate reads `log.md` (plan.md `**Phase log:**` fallback). Regex binds the bullet form. Epic 1.3 grounded in REQ-DATA-012. | resolved |
| C3 | `deliverable_class`↔`**Deliverable-class:**` registered as a canonical dual-write field (`PLAN_FIELD_LABELS`/`PLAN_FIELD_ORDER`/REQ-DATA-015) via new Issue 2.0 (lands before 2.2). Round-trip Test 3.1(c). | resolved |
| C4 | `validated:` documented as a recognized non-status `log.md` token (joins `intake:`); Test 3.1(e) asserts no review-count/grandfather parser keys on it. | resolved |

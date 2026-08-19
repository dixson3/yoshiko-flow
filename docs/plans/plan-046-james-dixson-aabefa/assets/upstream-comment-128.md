---
type: Reference
okf_spec: OKF-PLAN
id: upstream-comment-128
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
title: 'Draft: #128 comment (link correction, not a reopen)'
---

> Verbatim text of an upstream write performed at plan-046 reconcile (§6.3).
> Kept in the bundle so the upstream record is reproducible from the plan folder alone.

Link correction — **not a reopen**. This issue is closed and stays closed; it is subsumed by #141, which plan-046 delivered.

**Confirmed subsumed.** #141's own body states it: *"this also subsumes #128 (add a reference/link to the Google OKF spec), which should point at v0.2."* plan-046 Epic 2 executed #141 and delivered exactly what this issue asked for, at v0.2 rather than v0.1.

**Where the reference now lives** — and it is stronger than a link, because a link to `main` silently re-points when upstream moves:

- **`skills/yf-okf/spec/OKF-BASELINE.md`** — the human-readable baseline, reconciled to **OKF v0.2**, with a `## 0. Provenance` section naming the upstream source and every "OKF says X" claim quoted from it.
- **`docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md`** — the upstream spec **vendored verbatim** (`GoogleCloudPlatform/knowledge-catalog`, `okf/SPEC.md` @ `main`, retrieved 2026-08-18), so every claim is checkable **offline**.
- **`docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.1.md`** — the superseded v0.1, vendored verbatim (@ `ee67a5ca`, 2026-06-12), so the v0.1→v0.2 delta is diffable rather than asserted.

**Why v0.2 and not v0.1.** Upstream §13 states v0.2 *"supersedes OKF v0.1"*. Pinning a reference at v0.1 would have pointed this skill at a superseded revision of the spec it claims to track.

**Two things worth knowing if you follow the link.** Vendoring both revisions turned up material that a bare link would have hidden:
- v0.2 §13 is **accurate but incomplete** — it omits a `SHOULD NOT` → `MUST NOT` force upgrade on the extension clause (§4.1), does not flag that **seven sections were renumbered**, and does not mention that v0.1 §10 *"Relationship to other formats"* was **removed entirely**.
- Because v0.2 reuses the identical `(§N)` citation syntax, a surviving v0.1 pointer is textually indistinguishable from a correct v0.2 one. `OKF-BASELINE.md` §8 therefore carries an explicit v0.1→v0.2 section map, and its citations are verified row-by-row against it rather than by grep.

Plan: `docs/plans/plan-046-james-dixson-aabefa/`. Tracker: #167.

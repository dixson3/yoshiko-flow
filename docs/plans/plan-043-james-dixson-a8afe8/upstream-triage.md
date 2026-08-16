---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Phase 6.4 close-time hook contract; reconcile verification; close-time bundle conformance

Triage complete — 5 issues reviewed: 1 include, 1 partial, 3 exclude. Authoritative
dispositions and rationale live in `plan.md` → Upstream Issues; summarized per-issue below.

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** include

**Notes:** The plan's primary payload (Epic 1 `verify-reconcile`). E1 refuted this issue's own three hypotheses — the cause was a **false success assertion**, not a silent error, filtering, or non-dispatch. Issue 4.3 posts the correction.

## #141 — yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)

> ## Summary

`skills/yf-okf/spec/OKF-BASELINE.md` states it is *"Pinned to `okf_version: 0.1`"* and was distilled from research project `docs/research/001-okf-compliance-delta/`. Upstream `GoogleCloudP...

**Disposition:** partial

**Notes:** **Close-time-audit half only.** The nested-`index.md`/`log.md` enforcement and drift model are a yoshiko-flow extension decision (OKF v0.2 §8/§9: index/log **MAY** appear; §11: consumers **MUST NOT** reject for absence), carry a ~40-bundle backfill, and are deferred. E3 also corrects the framing: 9 of 10 failures are execution-authored, not legacy debt. Issue stays OPEN.

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** exclude

**Notes:** The `yf-retrospective` skill is not built here. Issue 4.4 records that the contract exists and names its two authority classes, so #145 inherits rather than re-derives it.

## #136 — yf-plan: reconcile silently skipped three mapped 'include' upstream issues while the plan reported complete

> ## What happened

plan-039 ([tracker #134](https://github.com/dixson3/yoshiko-flow/issues/134)) completed cleanly by every signal `yf-plan` reports:

```
status: complete
resume-scan: {found: true, to...

**Disposition:** exclude

**Notes:** Surfaced by the triage keyword scan. Independent OKF spec-version work; this plan touches no OKF baseline.

## #128 — yf-okf skill: add reference/link to the Google OKF spec
Labels: type::task, priority::low, docs
> The yf-okf skill should include a reference/link to the Google OKF (Open Knowledge Framework) spec it derives from....

**Disposition:** exclude

**Notes:** Surfaced by triage. Explicitly superseded by #141 and should simply be closed. Unrelated to this plan.

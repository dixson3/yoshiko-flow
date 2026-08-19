---
type: Reference
okf_spec: OKF-PLAN
id: upstream-close-92
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
title: 'Draft: #92 close comment (superseded, three named carve-outs)'
---

> Verbatim text of an upstream write performed at plan-046 reconcile (§6.3).
> Kept in the bundle so the upstream record is reproducible from the plan folder alone.

Closing as **superseded**, with **three named carve-outs** — not cleanly. Written against the measured record (plan-046 exp-004), because this issue's Why-deferred section is what a future reader will trust, and two of its claims are now false.

## What superseded it

- **The emit half already shipped, natively.** `type:` / `okf_spec:` frontmatter and reserved `index.md` / `log.md` are emitted in place by `plan_manager.py`, `index_manager.py`, and `incubator-index.py`. Measured across the 50-bundle corpus.
- **The nested-tree half is #140**, which is a strictly better-specified take on the same content. plan-046 closed #140 as `partial`: the root tier shipped, the nested tier is deferred with its measurement recorded.

## Two rationale claims that are now FALSE, corrected on the record

**1. "no confirmed non-Google adopter"** (Why-deferred, bullet 1) — **measurably false.** Four non-Google repositories were verified to carry literal OKF bundles by fetching actual file contents, two of them at v0.2.

**Be precise about what this does and does not establish.** The *bullet* is false. **Revisit trigger 2 has NOT fired**, and this close does not claim it has:
- trigger 2 is **conjunctive** — "a stable release **and** a non-Google **production** adopter" — and there is still **no upstream release or tag**;
- "**production**" is **inferred from repo prominence, not attested**. No adopter has stated it consumes external OKF bundles.

So: the stated rationale is false, the trigger's letter still holds. Citing the bullet as live rationale would be a false statement; claiming the trigger fired would be a different one.

**2. "No change to `plan_manager.py`… or the `README.md` / `_index.md` reserved-index names"** — this is research-001's `DECISION.md` §Consequences, the decision record behind this deferral. It was **already false when written**: commit `aaf2b6c` changed exactly those things **8h39m earlier**. That does not make the deferral wrong (plan-029 landed native **in-place** typing; #92 asks for a **non-destructive export projection** — genuinely different things), but it does mean the *"true cost is a whole-bundle conformant tree, not a one-line `type` key"* rationale was partly obsolete at the moment it was recorded. `docs/research/001-okf-compliance-delta/` is now marked `superseded_by` plan-046.

## The three carve-outs — filed, not dropped

A clean close would have silently discarded these. Each is filed as its own issue:

1. **projection delivery mode** (#168) — on-demand, non-destructive export. `emit_conformant_copy()` was **deleted** by plan-046 Issue 5.2 (measured: zero callers, zero tests, no CLI verb) rather than exposed, because exposing it would mean building this. The follow-on carries the deletion as its provenance, so the capability is remembered rather than merely removed.
2. **conformance gate for yf-research and yf-incubator** (#169) — shipped for yf-plan only. Cross-references #165: yf-research's SPEC states a `Verification:` line nothing executes, which is the same class.
3. **consumer round-trip fidelity** (#170) — still unverified in the sense this issue meant. yf demonstrates **producer → producer** only. OKF v0.2 §4.1 upgraded the extension clause from `SHOULD NOT` to **`MUST NOT`** reject unknown keys (an *undeclared* breaking change — v0.2 §13 does not list it), which raises the floor: a consumer may no longer *reject* yf's keys. Preservation remains `SHOULD`, so the gap this issue named is unchanged.

## On revisit trigger 3

Trigger 3 ("we adopt an OKF-consuming tool") fired on **capability but not demand** — operator ruling. `bp/skills/okf-lint` is a genuine first-hand OKF-consuming tool we did not have on 2026-07-19, but it governs a book vault and touches **zero** yf-* bundles, so it creates no demand for an export projection. The record is corrected; the conclusion is unchanged.

Plan: `docs/plans/plan-046-james-dixson-aabefa/` — see `findings/exp-004-92-supersede-evidence.md` for every measurement above. Tracker: #167.

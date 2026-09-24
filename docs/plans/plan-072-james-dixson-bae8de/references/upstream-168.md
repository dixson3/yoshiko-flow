---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #168 - yf-okf: projection delivery mode (on-demand OKF
  export) — #92 carve-out 1 of 3'
---
# Upstream #168: yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3

- **Number:** 168
- **Title:** yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by plan-046 Issue 5.5(i) as one of **three named carve-outs** from closing #92 as superseded. #92's emit half shipped natively and its nested-tree half is #140; these three are what a clean close would have silently dropped.

**What this is.** An on-demand, non-destructive **projection** of a bundle into a conformant OKF export — a delivery mode distinct from the native emission yf already does. Native emission stamps `type:`/`okf_spec:` frontmatter and reserved `index.md`/`log.md` **in place**, in the working corpus. Projection means producing a conformant copy **for a consumer** without mutating the source.

**Provenance — this issue exists because plan-046 DELETED the code.** `_shared/okf.py` carried `emit_conformant_copy()`, specified since plan-029 with (measured) **zero callers, zero tests, and no CLI verb**. plan-046 Issue 5.2 deleted it rather than exposing it, on the ground that exposing it would mean *building* this capability — reopening scope the plan closed. The deletion is deliberate and the SPEC carries a tombstone note; **this issue is where the capability is remembered**, so removing the code does not erase the record of what was removed.

**Why it was not built.** #92's revisit trigger (b) is **conjunctive** — a stable OKF release **and** a non-Google adopter. The adopter half **has** fired (plan-046 exp-004 verified four non-Google repositories carrying literal OKF bundles, two at v0.2); the release half has not (no upstream release or tag). More decisively, trigger (c) fired on **capability but not demand**: `bp/skills/okf-lint` is a genuine first-hand OKF-consuming tool, but it governs a book vault and touches **zero** yf-* bundles, so it creates no demand for an export projection.

**Revisit when** a concrete consumer wants a bundle it will not read in place — i.e. when the *demand* half fires, not merely the capability half.

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`), `findings/exp-004-92-supersede-evidence.md`. Tracker: #167. Supersedes the corresponding half of #92.


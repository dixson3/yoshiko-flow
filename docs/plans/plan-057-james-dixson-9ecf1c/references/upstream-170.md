---
type: Reference
okf_spec: OKF-PLAN
description: "Upstream issue #170 — OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3 Full untruncated body, snapshotted at triage."
---
# Upstream #170: OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3

- **Number:** 170
- **Title:** OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by plan-046 Issue 5.5(iii) as one of **three named carve-outs** from closing #92 as superseded.

**The gap, stated precisely.** yf demonstrates **producer → producer** fidelity only: it writes OKF-shaped bundles and reads them back with its own engine. What #92 meant by round-trip is **producer → third-party consumer → producer**, with yf's extension keys (`okf_spec`, `id`, `epic`, `fingerprint`, `author`, `created`) surviving intact. **No such round-trip has been demonstrated through any OKF tool**, so lossless end-to-end carry remains `[insufficient evidence]` — recorded as such in `skills/yf-okf/spec/OKF-BASELINE.md` §6.

**What OKF v0.2 changed, and what it did not.** v0.2 §4.1 upgrades the extension clause from `SHOULD NOT` to **`MUST NOT`** reject documents with unrecognized fields (an **undeclared** breaking change — §13 does not list it; plan-046 confirmed it against both vendored specs verbatim). That hardens the floor: a v0.2 consumer may no longer *reject* a document for carrying yf's keys. But **preservation is still only `SHOULD`** — a consumer may legally drop every yf key on round-trip. v0.2 raised the floor, not the ceiling, and the gap this issue names is about the ceiling.

**Why plan-046 did not close it.** Verifying this requires an actual third-party OKF consumer to round-trip through. Four non-Google adopters were verified as *carrying* OKF bundles (exp-004), but carrying is not consuming-and-re-emitting. Asserting fidelity without that would be exactly the "artifact asserting something nothing checks" defect plan-046 was written against.

**Revisit when** a third-party OKF read/write tool exists that can be pointed at a yf bundle — then this is a concrete, cheap test rather than an open question.

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`), `findings/exp-002-okf-v02-delta.md`, `findings/exp-004-92-supersede-evidence.md`. Tracker: #167. Supersedes the corresponding half of #92.


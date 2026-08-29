---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #246 - Drift CONFLICTs: REQ-DATA-044 says R* is uniformly
  W but the schema ships two E close-out checks'
---
# Upstream #246: Drift CONFLICTs: REQ-DATA-044 says R* is uniformly W but the schema ships two E close-out checks

- **Number:** 246
- **Title:** Drift CONFLICTs: REQ-DATA-044 says R* is uniformly W but the schema ships two E close-out checks
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

plan-054's full 52-edge drift sweep at `dd9adc2` returned **three CONFLICTs** — cases where the
evidence says the **fixed authority** is the stale side. Per `DRIFT-CHECK.md` §7 these are
reported, never silently rewritten, so they are filed here rather than fixed.

Two of the three (`e-spec-compliance`, `e-skillspec-skillmd`) were plan-054's own SPEC-first
debt and **have been fixed** in that plan — REQ-PORT-001, REQ-STRUCT-001/-003 and
REQ-BAUTH-001/-010 amended. This issue covers the **remaining** one plus two adjacent stale
authorities the sweep surfaced.

### 1. `e-doclint-spec` — REQ-DATA-044 vs the shipped schema

```
skills/yf-plan/spec/data.md:331 (REQ-DATA-044)
  "Severity: the `R*` rule family ships at severity `W`, uniformly."

_shared/document_types/plan-relations.toml:102-115
  [[checks]] id = "R1-closeout"   severity = "E"  statuses = ["reconciling","complete"]
  [[checks]] id = "R2a-closeout"  severity = "E"  statuses = ["reconciling","complete"]
```

plan-052 (REQ-BUP-070 / REQ-DATA-058) deliberately added two `E`-severity close-out checks with
a documented rationale — but **REQ-DATA-044 was never amended**. The `.toml`'s own banner
comment (line 7, "EVERY RULE IS `W`") also now contradicts lines 102-115 of the same file.

Three documents agree with each other and none matches the code — running in the opposite
direction from the usual drift.

### 2. `skills/yf-beads-init/README.md` teaches a retired shim as the engine

`README.md:62,77-80` presents `beads_init.py` as **the engine**, while `SKILL.md:87,99-100` and
`SPEC.md:14-17` say it is a **retired shim** and the engine moved into the `yf` kernel. The web
page is correct here; the skill's own README is the stale side.

### 3. `GUARDRAILS.md` GR-006 enumerates 2 of 5 harnesses

`GUARDRAILS.md:33-36` says "both `.claude` and `.agents` surfaces" while `SPEC.md:817-823`
REQ-YF-INSTALL-002 now defines **five**. Incomplete rather than contradictory — it passes
`field-set-subset` — but it is a guardrail describing a two-surface world that no longer exists.

Discovered by plan-054's release-readiness drift sweep.


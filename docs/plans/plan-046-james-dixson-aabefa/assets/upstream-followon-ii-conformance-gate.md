---
type: Reference
okf_spec: OKF-PLAN
id: upstream-followon-ii-conformance-gate
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
title: "Draft: follow-on issue \u2014 conformance gate for yf-research and yf-incubator (#169)"
---

> Verbatim text of an upstream write performed at plan-046 reconcile (§6.3).
> Kept in the bundle so the upstream record is reproducible from the plan folder alone.

TITLE: OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3

BODY:
Filed by plan-046 Issue 5.5(ii) as one of **three named carve-outs** from closing #92 as superseded.

**What this is.** yf-plan's bundles are conformance-gated: `plan_manager.py audit` runs the OKF engine's `check_conformance` and turns error-level findings into audit findings that block intake. **yf-research and yf-incubator have no equivalent gate.** Their bundles are OKF-shaped by producer convention only — nothing verifies it, so a regression in either producer is silent.

plan-046 made this sharper rather than resolving it: it added `REQ-PORT-010` to `skills/yf-research/spec/portability.md` (the research index must enumerate members that exist, and every entry must resolve) and fixed `index_manager.py` to satisfy it. **But no gate enforces `REQ-PORT-010`** — it is a requirement with a `Verification:` line and no runner.

**Cross-reference #165.** That is precisely #165's shape: a SPEC `Verification:` line naming a command nothing executes. plan-046's exp-004 recorded an instance of it in yf-research's own SPEC. This issue and #165 should be resolved together or at least read together — fixing one without the other leaves the same class open.

**Concretely, what a fix needs:**
1. a `check`-equivalent invoked on the yf-research and yf-incubator bundle lifecycles (the analogue of yf-plan's audit step 7);
2. a decision on the error/warning split for each, mirroring `REQ-OKF-CHK-001`'s ratified split;
3. `REQ-PORT-010` and the yf-incubator equivalents wired to it, so the requirement is executed rather than merely stated.

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`). Tracker: #167. Supersedes the corresponding half of #92.

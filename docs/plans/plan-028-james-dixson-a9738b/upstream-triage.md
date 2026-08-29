---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: credibility_scorer + parked plan visibility

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #87 — credibility_scorer.py: tz-naive date crash + domain allowlist misses dev-tooling primaries
Labels: bug
> Found during yf-research 272 triangulation (Git forge viability & migration).

**Location:** `.claude/skills/yf-research/scripts/credibility_scorer.py`

## 1. `_currency_score` crashes on timezone-nai...

**Disposition:**
**Notes:**

## #86 — yf-plan: approved-but-unexecuted plans masquerade as completed (intake commit subject + tracking-issue title); add parked-plan visibility
Labels: enhancement
> ## Problem

An **approved-but-unexecuted** yf-plan plan is easily mistaken for a **completed** one. This was hit live: plan-026 (markdown tooling, #81/#48/#46/#49/#50) was approved and intake'd on 202...

**Disposition:**
**Notes:**

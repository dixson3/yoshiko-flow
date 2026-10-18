---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: 0.6.0 release

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #442 — plan-073-james-dixson-cc76de execution tracking
Labels: type::epic, priority::high
> Coarse tracking issue for **plan-073-james-dixson-cc76de** (AGENTS.md convention: one issue per plan-scale effort). Resolves #410 and #411. Partially resolves #412.

**Plan:** `docs/plans/plan-073-jam...

**Disposition:**
**Notes:**

## #412 — yf-research credibility_scorer.py over-scores: arxiv.org is Tier 1 (rubric says preprints Tier 4), .dev bump promotes third-party registries/mirrors
Labels: priority::medium, type::bug
> ## Problem

`scripts/credibility_scorer.py` contradicts the rubric the triangulator is told to apply, in the **over-scoring** direction. (#147 covers under-scoring of non-`docs.*` vendor hosts; #336 c...

**Disposition:**
**Notes:**

## #411 — yf-research red-team runs before packager generates sources.md — every citation reported as a broken link
Labels: priority::medium, type::bug
> ## Problem

The red-team runs before the packager, but the synthesizer is required to emit citation links that only resolve after packaging. The red-team has no way to know this, so it reports every c...

**Disposition:**
**Notes:**

## #410 — yf-research red-team: quote check reads only sources.json, but synthesizer quotes from cluster artifacts — false 'untraceable quote' [high] findings
Labels: priority::medium, type::bug
> ## Problem

The red-team's quote-fidelity check is structurally guaranteed to produce false "untraceable quote" findings, because it is given a narrower evidence set than the synthesizer that wrote th...

**Disposition:**
**Notes:**

## #302 — yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts
Labels: type::bug, priority::high
> Two measured defects in the same layer — **plan-folder identity and location** — found by observation
of plan-060's own drafting worktree. Both are instances of the class
[#301](https://github.com/dix...

**Disposition:**
**Notes:**

## #255 — Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)

> **The tag push is the only remaining work.** plan-054 completed everything else and deliberately
descoped Issue 6.8 so the operator could verify the harnesses manually under a real `HOME`
before an ir...

**Disposition:**
**Notes:**

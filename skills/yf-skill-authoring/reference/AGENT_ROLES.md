---
title: Canonical Agent Roles
created: '2026-06-02'
tags: []
---

# Canonical Agent Roles

The vocabulary every multi-agent skill in this repo names its agents by. One role per
agent; one word per operation. A reader must be able to predict what an agent does from
its name and front-matter alone.

## The 6 roles

Every agent maps to **exactly one** role.

| Role | Operation |
|:-----|:----------|
| **GATHER** | Acquire raw inputs the pipeline doesn't yet have (run an experiment, retrieve sources). |
| **PRODUCE** | Generate a new primary or intermediate artifact (a plan, a synthesis, validated scripts, an analytical intermediate). |
| **EVALUATE** | Assess the primary artifact and emit a verdict (conformance or adversarial). |
| **REVISE** | Edit an existing artifact in place per evaluation feedback. |
| **ORCHESTRATE** | Drive the bead DAG to completion (claim, dispatch, gate, close). |
| **CLOSEOUT** | Terminal hand-off work after execution (reconcile upstream, package the report, capture portability gaps). |

**Role families.** PRODUCE, CLOSEOUT, and GATHER are explicitly *families*: a role may hold
several distinct-named agents when the factoring test (below) justifies the split by a
distinct artifact or operation — e.g. CLOSEOUT holds captor / reconciler / packager, PRODUCE
holds planner / synthesizer / toolsmith / triangulator. EVALUATE's two **stances** are
reserved for assessing the *primary artifact* (see below).

## The factoring test

The anti-over-factoring guardrail. Split a single role into multiple agents **only** when the
sub-passes are:

(a) **independently sequenced or gated**, or
(b) **require non-interfering mindsets** (e.g. a conformance check and an adversarial attack
should not share one prompt).

Otherwise: **one agent per role.** When you do split, **keep the role word and add a
qualifier** (`reviewer-tokens`, not `optimizer`).

## EVALUATE — two canonical stances

EVALUATE agents carry a `stance` declaring how they assess the primary artifact:

- **`reviewer`** = conformance / completeness against a checklist. Mechanical: does every
  required element exist and satisfy its contract?
- **`red-team`** = adversarial stress. What assumptions break, what failure modes exist,
  what is missing?

These two stances are the only canonical EVALUATE names for assessing the primary artifact.
An agent that judges *intermediate inputs* rather than the primary artifact (e.g. scoring
source credibility) is not EVALUATE — its deliverable is an analytical artifact, so it
PRODUCEs.

### Qualified reviewers

Domain specializations of the conformance stance keep the role word and add a literal
qualifier naming the domain:

- `optimizer` → **`reviewer-tokens`** (token-efficiency conformance)
- `python-reviewer` → **`reviewer-python`** (Python helper conformance)

A qualified reviewer still carries `stance: reviewer`.

## ORCHESTRATE — one word

The bead-DAG driver is **`coordinator`** everywhere. `executor` is a deprecated synonym; do
not introduce new ones.

## YAML front-matter schema

Every agent file across every skill carries this front-matter block:

```yaml
---
name: <Canonical Name>        # Title Case; no "Formula:" prefix; equals the H1 heading
role: <gather|produce|evaluate|revise|orchestrate|closeout>
stance: <reviewer|red-team>   # EVALUATE agents only; omit for all other roles
model:                        # reserved for future model-routing; empty = inherit
description: <one line>       # what this agent does
---
```

Rules:

- The `# H1` heading **equals** `name`.
- Pre-existing `created` / `tags` keys are kept if present, not required. A `title:` key is
  **replaced by** `name` (one rule, applied uniformly — `name` is the canonical key).
- `model:` is present-but-empty on every agent so model-routing can be switched on later
  without touching every file again. It is a **documented forward-compat convention, not a
  hard-enforced field**: nothing consumes it today (agents are read inline). Write it by
  convention; do **not** make "every agent has an empty `model`" a verified success criterion
  or a grep assertion.
- `stance` appears **only** on EVALUATE agents; omit it for every other role.

## Canonical role assignment for all agents

The worked example. Every skill's agents take their `role` / `stance` from this table
verbatim — no role is decided ad hoc. "Valid `role`" means "matches this table." Names below
are **post-rename** (the canonical names).

| Skill | Agent | role | stance | Notes |
|:------|:------|:-----|:-------|:------|
| yf-plan | coordinator | orchestrate | — | |
| yf-plan | investigator | gather | — | |
| yf-plan | planner | produce | — | |
| yf-plan | reviewer | evaluate | reviewer | conformance pass |
| yf-plan | red-team | evaluate | red-team | adversarial pass |
| yf-plan | reconciler | closeout | — | |
| yf-plan | captor | closeout | — | |
| yf-research | coordinator | orchestrate | — | |
| yf-research | retriever | gather | — | |
| yf-research | toolsmith | produce | — | Generates validated scripts — a new artifact. The 6-role set has no SETUP; PRODUCE is a family. |
| yf-research | triangulator | produce | — | Scores source credibility / flags consensus, but emits no verdict on the primary artifact; its deliverable `triangulation.md` is an analytical intermediate → PRODUCE, not EVALUATE. |
| yf-research | synthesizer | produce | — | |
| yf-research | red-team | evaluate | red-team | was `critic`; keeps its `critique.md` output artifact name |
| yf-research | refiner | revise | — | Also spawns gap-fill GATHER beads, but its dominant operation is editing `Summary.md` per critique → REVISE. |
| yf-research | packager | closeout | — | |
| skill-authoring | reviewer | evaluate | reviewer | |
| skill-authoring | reviewer-tokens | evaluate | reviewer | was `optimizer` |
| skill-authoring | reviewer-python | evaluate | reviewer | was `python-reviewer` |
| skill-authoring | red-team | evaluate | red-team | |
| beads-authoring | reviewer | evaluate | reviewer | read-only conformance audit |
| optimal-instructions | instruction-optimizer | revise | — | Auto-*applies* K1 edits (mutates the file), distinct from skill-authoring's read-only EVALUATE `reviewer-tokens`. The REVISE-optimizer vs EVALUATE-reviewer contrast is exactly what the vocabulary disambiguates. |

## Deliberate non-renames

Defensible by the factoring test or distinct operation — **not** vocabulary drift:

- **GATHER:** investigator (run an experiment) vs retriever (web-retrieve) — distinct inputs.
- **PRODUCE:** planner / synthesizer / toolsmith / triangulator — distinct artifacts.
- **CLOSEOUT:** captor / reconciler / packager — genuinely distinct terminal operations.
- **REVISE:** refiner.

## Deliberate asymmetry

yf-plan gains both EVALUATE stances (a conformance `reviewer` + a `red-team`); yf-research
gets only `red-team`. The factoring test, not symmetry, governs: a plan's conformance is
semantic (epic / dependency / success-criteria soundness) and warrants a dedicated pass,
while research-report conformance is largely mechanical and already covered by
refiner / packager.

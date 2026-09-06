---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: regenerate user-facing website docs pelican build drift-check coverage

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #317 — Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
Labels: type::task, priority::high
> > **Plan 3 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout contract) and #316 (OKF corpus backfill). This one runs
> last — it r...

**Disposition:**
**Notes:**

## #127 — web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
Labels: type::task, priority::low, docs, web
> In the Concepts material, explain the idiomatic workflow vocabulary: 'pouring beads', 'landing the plane', 'red-team', and other recurring workflow-step terms. A glossary a cold reader can use to deco...

**Disposition:**
**Notes:**

## #104 — web: prevent runaway Pelican devservers + add clean teardown (port naba#21)

> ## Problem

The Pelican `-lr` (listen + autoreload) devserver leaks runaway processes. Two failure modes, both observed in sibling repos:

1. **Orphaned workers.** When the shell/session that ran `mak...

**Disposition:**
**Notes:**

## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:**
**Notes:**

## #263 — META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
Labels: type::bug, priority::high
> ## The class

**A signal that can mean two different things, reported through a channel that cannot express the
difference — and where the more permissive consumer is the one that says "clean".**

Thi...

**Disposition:**
**Notes:**

## #273 — The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py

> > Measured by EXP-001 of plan-059 (`yf-judgement` design) and elevated to its own artifact because
> **it is not about `yf-judgement`**. Source:
> `docs/plans/plan-059-james-dixson-55137e/findings/fin...

**Disposition:**
**Notes:**

## #312 — Process-audit stage: amend the poured DAG so the retrospective write, the landing protocol and preflight are BEADS, not paragraphs
Labels: type::feature, priority::high
> ## Summary

Proposal: a **process-audit** stage that runs in conjunction with the bead pour, reviews the
poured DAG, and **amends it** so recurring process obligations — the retrospective write, the
l...

**Disposition:**
**Notes:**

## #363 — OKF-EXTENSION.md documentation remediation: 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions (#247)
Labels: type::task, priority::low, follow-on
> Measured by plan-064 EXP-003. Routed to #247 rather than fixed in plan-064, because the subject
matter is disjoint (engine config under `skills/` vs. bundles under `docs/plans/`) and #318/#320/#321
ar...

**Disposition:**
**Notes:**

## #322 — docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x

> ## docs — `SKILL.md`'s "31 legacy bundles, of which 7 halt" reads as repo-agnostic and mis-sized a real plan 3.5x

Measured 2026-08-30 (plan-012, EXP-004).

### The defect

`yf-okf-hygiene/SKILL.md:18...

**Disposition:**
**Notes:**

## #365 — plan-065-james-dixson-7c8cd4 execution tracking

> Coarse tracking issue for **plan-065**, per this repo's one-issue-per-plan convention.

**Plan bundle:** [`docs/plans/plan-065-james-dixson-7c8cd4/`](https://github.com/dixson3/yoshiko-flow/tree/main/...

**Disposition:**
**Notes:**

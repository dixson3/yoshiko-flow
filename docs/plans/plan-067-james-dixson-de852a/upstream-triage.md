---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: diagram redesign marketecture archify omissions fail drift-check

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #373 — Diagram set redesign + make DRIFT-CHECK omissions FAIL

> Split from plan-066 (#317) at its Diagram human-read gate. The operator read the six regenerated PNGs and did **not** accept them — not because any diagram makes a false claim, but because the set nee...

**Disposition:**
**Notes:**

## #317 — Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
Labels: type::task, priority::high
> > **Plan 3 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout contract) and #316 (OKF corpus backfill). This one runs
> last — it r...

**Disposition:**
**Notes:**

## #375 — web/content/images/lifecycle.d2: labels a preflight status `deps-missing` where the literal is `system_deps_missing`

> `web/content/images/lifecycle.d2` labels the preflight outcomes
`ok / ignored / deps-missing / rule-drift`. The actual status literal is **`system_deps_missing`**,
not `deps-missing`.

**This is a del...

**Disposition:**
**Notes:**

## #376 — check_web_counts: group membership is NOT CHECKED where a bullet enumerates no member ids (declared limit)

> `scripts/checks/check_web_counts.py` verifies a group's **count** always, but its **membership**
only when the group's label or bullet actually enumerates member ids. Where none are enumerated it
emit...

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

## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:**
**Notes:**

## #374 — web/plugins/skill_pages.py: the authored-page guard is EXISTENCE-ONLY — a zero-byte page passes it and builds green

> The authored-skill-page guard in `web/plugins/skill_pages.py` calls itself **fail-closed**, but it
only checks `os.path.isfile`. A **zero-byte** `web/content/skills/<name>.md` satisfies it: the
build ...

**Disposition:**
**Notes:**

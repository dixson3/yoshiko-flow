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

**Disposition:** include
**Notes:** The plan of record. Pass-1 C8 caught two named deliverables silently dropped (the five per-formula diagrams; land-the-plane); both restored, so `include` is earned rather than asserted. Resolved by 6.5.
## #317 — Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
Labels: type::task, priority::high
> > **Plan 3 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout contract) and #316 (OKF corpus backfill). This one runs
> last — it r...

**Disposition:** partial
**Notes:** plan-066's tracker, parked behind its Diagram human-read gate. This plan does not close it — Issue 6.4 is the declared handoff that lets the operator open that gate. Out of scope: plan-066's own remaining 8.1/8.3.
## #375 — web/content/images/lifecycle.d2: labels a preflight status `deps-missing` where the literal is `system_deps_missing`

> `web/content/images/lifecycle.d2` labels the preflight outcomes
`ok / ignored / deps-missing / rule-drift`. The actual status literal is **`system_deps_missing`**,
not `deps-missing`.

**This is a del...

**Disposition:** include
**Notes:** The `deps-missing` vs `system_deps_missing` literal in `lifecycle.d2`. Resolved by Issue 4.2, which merges that file — without an explicit sub-task the wrong literal is carried forward into the combined diagram.
## #376 — check_web_counts: group membership is NOT CHECKED where a bullet enumerates no member ids (declared limit)

> `scripts/checks/check_web_counts.py` verifies a group's **count** always, but its **membership**
only when the group's label or bullet actually enumerates member ids. Where none are enumerated it
emit...

**Disposition:** include
**Notes:** **Re-scoped from adjacent to precondition** (pass-1 C6): it is the stated limit in the exact function Issue 1.1 modifies, and it is what would let an omission stay invisible under the new rule. Resolved by 1.1b.
## #263 — META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
Labels: type::bug, priority::high
> ## The class

**A signal that can mean two different things, reported through a channel that cannot express the
difference — and where the more permissive consumer is the one that says "clean".**

Thi...

**Disposition:** partial
**Notes:** In scope: `not_checked` conflating 'no ids enumerated' with 'checked and clean' (Issue 1.1b). Out of scope: the META class itself.
## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:** partial
**Notes:** In scope: the CLI→page direction (D4b) and `web-diagram-src` coverage. Out of scope: the remainder of #247's manifest gap.
## #374 — web/plugins/skill_pages.py: the authored-page guard is EXISTENCE-ONLY — a zero-byte page passes it and builds green

> The authored-skill-page guard in `web/plugins/skill_pages.py` calls itself **fail-closed**, but it
only checks `os.path.isfile`. A **zero-byte** `web/content/skills/<name>.md` satisfies it: the
build ...

**Disposition:** include
**Notes:** The existence-only authored-page guard: a zero-byte page builds green. Resolved by Issue 5.7, because Epic 5's GENERATED pages are exactly the artifacts that could be emitted empty and pass.

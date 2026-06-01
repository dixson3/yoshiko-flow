# Review Pass 1 — plan-002-james-dixson-b8b610

**Reviewer verdict:** REVISE
**Date:** 2026-05-31
**Final status after resolution:** approved (pending operator)

## Concerns (verbatim) and resolutions

### C1 — Trigger-collision resolution is asymmetric (medium)
> Deferral in skill-authoring's SKILL.md body/optimizer scope note won't prevent routing;
> routing is driven by the two `description` fields. Make Issue 2.1 edit skill-authoring's
> `description` SKIP clause; put the skill-dir vs project-root axis in BOTH descriptions.

**Resolution:** Issue 2.1 rewritten to edit skill-authoring's **`description`** (not just
body), placing the skill-dir vs project-root distinction in both descriptions. Added SC#5 and
an Epic 4.1 cross-check that the two descriptions are mutually exclusive on CLAUDE.md/AGENTS.md.

### C2 — Auto-fix on governance files is destructive (medium)
> "auto-fix" applied on write, without a gate, to operator-authored mandate files. Reconcile:
> make K2 structural relocation propose-only while K1 auto-applies, or add a spec REQ guarding
> mandate-marked files. Operator locked "auto-fix" before this was surfaced — confirm.

**Resolution:** Operator confirmed **split apply mode** — K1 (token cuts) auto-applies; K2
(structural relocation) is propose-and-confirm, relocate-never-delete. Folded into Approach,
Issue 1.2, Issue 1.3 (spec REQ), Risks, SC#3.

### C3 — Success Criterion #2 was untestable (medium)
> A pure description-triggered skill cannot guarantee firing; SC#2 asserted it does.

**Resolution:** SC#2 reworded to a verifiable claim about the *description's content* (TRIGGER +
SKIP text), with the best-effort limitation stated explicitly.

### C4 — K1 ownership boundary points at a moving target (low)
> K1 lives in both skill-authoring SKILL.md and optimizer.md. Name the single canonical anchor.

**Resolution:** Canonical K1 anchor fixed to **skill-authoring `SKILL.md` "Token efficiency" §**
in Approach, Issue 1.2, and an Epic 4.1 cross-check that the citation resolves and the anchor exists.

### C5 — AGENTS/* vs .agents/rules/ surface mismatch unaddressed (low)
> Two conventions for the behavioral-rules subdir. The skill must declare which it normalizes to.

**Resolution:** Approach + Issue 1.3 spec REQ: detect the project's surface (`AGENTS/*` or
`.agents/rules/*`) and normalize to *that*, not impose one.

### M1 — No fixtures / acceptance examples
**Resolution:** Issue 1.3 includes one inline before/after acceptance example in spec for
falsifiability. No separate fixture harness / gate (operator chose consistency-only verification).

### M2 — Idempotency requirement absent
**Resolution:** Added as Approach note, Issue 1.3 spec REQ, and SC#3 (no-op on optimized input).

### M3 — Surface-Convention "never write CLAUDE.md/AGENTS/" carve-out unstated
**Resolution:** Approach + Issue 1.3 record the runtime carve-out: §1 forbids the *installer*
from writing those files; this skill edits them at runtime via its apply agent (different
mechanism, permitted).

## Gate assessment resolution
Reviewer suggested optionally gating Epic 4 with a human fixture review. **Operator chose
consistency-only (no gate).** Only the mandatory Start Gate remains.

## Upstream assessment
Confirmed sound: no applicable upstream issues; empty row with rationale is correct.

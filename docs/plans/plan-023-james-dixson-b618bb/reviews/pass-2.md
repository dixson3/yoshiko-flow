# Review pass 2 — plan-023

**Reviewer:** red-team (adversarial, cycle 2 — post-revision verification)
**Date:** 2026-07-05
**Verdict:** REVISE (narrow/textual) → **APPROVE** on re-verification (both concerns fixed in-pass; sole residual was a cosmetic leftover phrase, since trimmed)

## Pass-1 resolutions — all confirmed present in plan.md (not just pass-1.md)

- **Concern 1** (engine mode → per-repo local-server canonical, embedded dropped): RESOLVED and internally consistent across Investigation Findings, Epic 1 approach + Issues 1.1–1.4, Risks, and SC#1. No leftover "embedded canonical / server drift / engine migration" language. Verified this repo is `dolt_mode: server` → factually conformant.
- **Concern 3** (per-issue reconcile): reflected (see pass-2 concern B for the scoping fix).
- **Concern 4** (decouple state short-name from config-basename): RESOLVED (Issue 2.2 + fixture); underlying bug verified real.
- **Concern 5** (flat tier transitional): RESOLVED (Issue 2.3 + follow-up bead).
- **Concern 6** (name SPEC surfaces): RESOLVED (Issue 1.1).
- Untouched-issue facts re-verified: #66 gap real (`interactions.jsonl` in `BEADS_UNTRACK`, absent from `BEADS_GITIGNORE`); #57 wording hazard real. SPEC-first ordering intact.

## Pass-2 concerns

| # | Sev | Concern | Recommendation | Resolution |
| :-- | :-- | :-- | :-- | :-- |
| A | MED | "per-repo vs global/shared server" is **not read-only detectable** (no `--shared-server` flag; bd always writes `dolt-server.*` under the repo's own `.beads/`, so the signal can never be false). Yet invariant 1, Issue 1.4's shared-server fixture, and SC#1 promised to detect/test it — unconstructible/untestable. | Reduce engine-mode detection to the observable signal: server-files-present ⇒ conformant; embedded ⇒ detect/warn drift. Drop the "not shared-server" clause, the shared-server fixture, and shared-server from SC#1. | FIXED — invariant 1 rewritten to the observable server-vs-embedded rule; Issue 1.4 + SC#1 drop the shared-server fixture; the Engine-mode decision block aligned. |
| B | LOW | Reconcile note claimed #66/#57/#67 close "without waiting on #58", but the gate is whole-plan `auto (all beads closed)` — the mechanism doesn't provide per-issue closure. | Make reconcile per-epic, OR soften the note to "independence is logical, applied at the single whole-plan reconcile." | FIXED — note softened to logical independence at the one reconcile step (stall risk largely gone since Epic 1 is de-risked). |

## Gate / Upstream Assessment

Start (human) + Reconcile (auto) appropriately typed; no capability gate needed (engine-mode
correction out of scope). #65 supersede + #60 defer correct; #66/#57/#67 includes verified. The
pass-1 embedded-only weakness is resolved — the plan accepts server-mode repos as conformant,
matching #58's framing. Concurrency question is moot (nothing migrated).

## Outcome

REVISE was narrow and textual; both concerns fixed in the same pass by applying the reviewer's
exact recommendations. Re-verification requested before APPROVE.

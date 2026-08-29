---
type: Review
okf_spec: OKF-PLAN
reviewer: red-team (adversarial, cycle 2 — post-revision verification)
date: '2026-07-05'
verdict: APPROVE
---
# Review pass 2 — plan-022

**Reviewer:** red-team (adversarial, cycle 2 — post-revision verification)
**Date:** 2026-07-05
**Verdict:** APPROVE

## Scope

Cycle 2 verified each pass-1 concern was actually resolved in `plan.md` (not merely asserted in
`pass-1.md`), checked against real source, and hunted for revision-introduced defects.

## Pass-1 resolutions — all confirmed against real files

| # | Pass-1 concern | Cycle-2 verification |
| :-- | :-- | :-- |
| 1 | Epic 1 raw-dolt fallback | RESOLVED. `skills/yf-beads-init/SKILL.md:89-96` matches the plan's edit-target description; Epic 1 keeps raw-dolt as bd<1.1.0 fallback, `bd dolt commit`→`bd migrate` as bd≥1.1.0, false claim version-conditional. Consistent across Approach/Epics/SC/Risks. |
| 2 | Epic 4.3 override auto-run | RESOLVED. Override stays operator-gated/never auto-run; canonicalization primary; micro-experiment is a real ordered task. `BD_SMART_GATE`/`BD_ALLOW_REMOTE_MIGRATE` confirmed absent from `skills/` + `_shared/` (documented env vars, not edited code). |
| 3 | Epic 5 localized knob feasibility | RESOLVED + FEASIBLE. `_shared/active_set.py` is the canonical source; in `upstream.py`, `classify_active` is inside the vendored region (L122–260) but `enumerate_candidates` (L366) is **outside** it — a localized knob there bypasses owner-based classification without touching the vendored region or hygiene. |
| 4 | Epic 2 nonexistent tuples | RESOLVED. `MIN_BD_VERSION`/`_parse_bd_version` absent from both managers; survive only as stale prose (`prerequisites.md:15`). Plan fixes prose + real pins; no reference to bumping nonexistent constants. |
| 5 | Bundled reconcile coupling | RESOLVED + consistent. Reconcile Gate note separates plan-level auto gate from per-issue upstream closure; consistent with AGENTS.md coarse tracking. |

## Concerns (revision-introduced)

| # | Sev | Concern | Recommendation | Resolution |
| :-- | :-- | :-- | :-- | :-- |
| A | MED | Issue 4.2 (impl) was a sibling of the load-bearing micro-experiment 4.3; the "canonicalization clears the gate" premise is unproven until the experiment runs, and the live fixture applied remove-remote + override together. | Make the impl `depends-on` the experiment. | FIXED — Epic 4 re-ordered: 4.2 = micro-experiment (depends-on 4.1), 4.3 = impl (depends-on 4.2), 4.4 = docs (depends-on 4.2). Load-bearing risk added. |
| B | LOW | Motivation/live-fixture text read as if the override was necessary; git-remote vs Dolt-remote terminology slipped. | Note the override's necessity is what 4.2 tests; disambiguate. | FIXED — Motivation point 2 + live-fixture finding now carry the "applied together, unproven, 4.2 isolates it" caveat and disambiguate git vs Dolt remote. |

## Gate / Upstream Assessment

Two gates, both justified; SPEC-first enforced in every epic (X.1→X.2/X.3 `depends-on`, all
verified); no gratuitous capability gate (EXP-001 concluded). Both #68/#61 `include`, traceable;
#61 option (b) explicitly recorded and justified as lowest-blast-radius.

## Outcome

APPROVE. Concerns A/B were fixed in the same revision pass (cheap, non-blocking). Plan is ready
for the portability audit and intake.

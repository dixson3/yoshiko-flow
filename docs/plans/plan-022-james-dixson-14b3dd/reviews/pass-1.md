---
type: Review
okf_spec: OKF-PLAN
reviewer: red-team (adversarial)
date: '2026-07-05'
verdict: REVISE
---
# Review pass 1 — plan-022

**Reviewer:** red-team (adversarial)
**Date:** 2026-07-05
**Verdict:** REVISE

## Strengths

- SPEC-first is structurally enforced in every epic (X.1 SPEC issue precedes X.2/X.3 with `depends-on`).
- EXP-001 is high-quality, non-simulated evidence; VERDICT A correctly removes the capability gate.
- Gates minimal and appropriate (human Start + auto Reconcile; no gratuitous capability gate).
- Live-fixture certification gives the false-negative-invariant re-affirmation real grounding.

## Concerns

| # | Sev | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | HIGH | Epic 1 drops the raw-dolt fallback, but there is **no runtime bd-version floor** — pins are documentary only. An operator on bd 1.0.x passes preflight then hits the 1.1.0-only `bd dolt commit` embedded hatch → broken repair. | Keep raw-dolt as an explicit documented `bd < 1.1.0` branch, OR add a real runtime bd≥1.1.0 floor (new code) and make Epic 1 depend on it. Do not drop a working fallback on a prose-only floor. |
| 2 | HIGH | Epic 4.3 gate-neutralization is fuzzy and internally contradictory: automates what the Motivation calls a human coordination decision; `BD_SMART_GATE` is nowhere in the codebase; once 4.2 removes both remote layers the gate is already moot → 4.3 may be redundant with 4.2. Live fixture applied BOTH remove-remote AND the override, so which cleared the gate is unproven. | Specify exact mechanism + persistence; resolve 4.2-vs-4.3 redundancy (micro-experiment: does remove-remote alone clear the gate?); give explicit safety argument for any auto-run override (local-only + remote removed ⇒ no coordination partner ⇒ moot ⇒ safe). |
| 3 | MED | Wrong edit target: the classifier is `_shared/active_set.py`; `_shared/sync.py` is only the vendoring tool — editing it won't change the classifier. Second consumer omitted: `yf-beads-hygiene` reconcile also uses `classify_active`. | Name `_shared/active_set.py` as edit target (then run `sync.py` to re-vendor). Add hygiene-reconcile to blast radius + tests. Weigh #61 option (b) config-knob-localized-to-enumerate vs mutating the shared glossary for both consumers. |
| 4 | MED | Epic 2 names `MIN_BD_VERSION` tuples + `_parse_bd_version()` in plan_manager.py/research_manager.py that **do not exist** (removed in a refactor; survive only as stale prose in `spec/prerequisites.md`). | Re-scope Epic 2: no manager tuples to bump. Fix drifted `prerequisites.md` prose + bump pins that exist (frontmatter, READMEs, banners, spec floors). A real runtime floor (concern 1) is new code, not a bump. |
| 5 | MED | Bundling #68 + #61 couples both at the auto Reconcile Gate: #68 certification can't reconcile until the riskiest Epic 5 shared-classifier work lands. | Split into two plans, OR allow per-issue partial reconcile so #68 lands independently of #61. |

## Missing / low-severity

- SC-4 ("follow-on-hoist semantics assessed") not testable → restate as "hoist-eligibility test passes".
- SC-5 ("reliably routes") is LLM-dispatch with no test → require a documented trigger-string table + Tier-2 mechanical drive.
- SC-2 "repo-wide grep gate" false-positives on historical mentions (this plan, EXP-001, "fixed in 1.1.0" notes) → scope grep to `skills/` + allow-list historical annotations.
- Epic 5 "re-vendor" must invoke `_shared/sync.py` and keep DRIFT-CHECK edges `e-active-set-copy-hygiene`/`e-active-set-copy-upstream` green.

## Gate Assessment

Two gates, both justified. See concern 5 re: bundling coupling the auto Reconcile Gate.

## Upstream Assessment

Both `include`, traceable. Plan should record which of #61's three options (a drop owner-alone / b config knob / c document) it takes — it silently chose (a), the highest-blast-radius, without weighing (b).

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| 1 | Keep raw-dolt as the documented **bd<1.1.0 fallback**; `bd dolt commit`→`bd migrate` is the bd≥1.1.0 preferred path. No runtime floor added; the false "cannot open" claim made version-conditional. (Epic 1 revised.) | resolved |
| 2 | Epic 4.3 reframed: **canonicalization (remove both remote layers) is the primary gate fix** — a micro-experiment confirms remove-remote-alone clears the 1.1.0 gate. `BD_ALLOW_REMOTE_MIGRATE` **stays operator-gated, never auto-run** (preserves the human coordination decision). No new `BD_SMART_GATE` auto-suppression. | resolved |
| 3 | #61 **option (b) — localized enumerate knob in `upstream.py`**; the shared `_shared/active_set.py` glossary and hygiene-reconcile are left untouched (lowest blast radius). Constraint note corrected (`active_set.py` is the source; `sync.py` only vendors). (Epic 5 revised.) | resolved |
| 4 | Epic 2 re-scoped: **no manager `MIN_BD_VERSION` tuples exist** to bump; fix the stale `prerequisites.md` prose + bump the pins/banners/floors that exist. | resolved |
| 5 | **Keep bundled** (operator intent), **decouple reconcile**: #68 and #61 close as independent upstream issues as their epic sets complete. (Reconcile Gate note added.) | resolved |

**Low-severity:** SC-2 grep scoped to `skills/` + allow-list historical mentions; SC-4 restated as a passing tagged test + unchanged-shared-behavior assertion; SC-5 requires a trigger-string table + Tier-2 drive; Epic 5 re-vendor/DRIFT-CHECK edges folded into SC-6. All applied.

**Verdict after revision:** all HIGH+MED concerns resolved by re-scoping per the red-team's own recommendations; no second adversarial cycle required (operator-approved per yf-plan's operator-override provision).

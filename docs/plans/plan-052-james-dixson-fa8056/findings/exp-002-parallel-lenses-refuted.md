---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-parallel-lenses-refuted
description: Does the herdr child-session mechanism change plan-051 D-7's arithmetic for #194? No — on three independent grounds.
---

# EXP-002 — #194 stays declined. Fan-out is not merely unhelpful; it is UNSOUND.

**Verdict: NO.** The revival is refuted. This is the second independent measurement D-3 required,
so #194 can be closed as declined rather than re-litigated next plan.

## 1. D-7 never turned on mechanism — so a new mechanism cannot move it

plan-051's EXP-005 spiked **the bead-graph join primitive**, and found it **BUILDABLE**: the
formula schema's `[[steps]]` carries `needs = [...]` as an array, so multi-parent fan-in is
first-class; a 6-step *conformance → 3 lenses → join → gate* formula cooked, poured and drove
end to end. `needs` compiles to `blocks` + `parent-child`.

It declined on **evidence**, not capability — verbatim: *"buildable (spiked), but zero evidence
— 29 passes across 4 plans, none concurrent."*

**A new substrate can only move a decision whose binding constraint was substrate.** herdr child
sessions change the *how*; D-7 declined on the *whether*.

## 2. Concerns do NOT cluster by lens — the central question, measured

All 23 `pass-*.md` files across plan-049/050/051, every `## Concerns` row classified into six
lenses (falsifiability · gate-reachability · instrument-correctness · cross-artifact
propagation · upstream-fidelity · bundle-hygiene):

**Every substantive pass (n ≥ 9) ranges across 4–6 of 6 lenses, modal share 36–56%.** `051 p1`
spans **all six** in 20 concerns. The only single-lens passes are the 1- and 2-concern terminal
APPROVE passes, where n is too small to mean anything.

**The one near-monolens pass refutes the argument by itself.** `050 p11` is 9/12 in the
cross-artifact-propagation lens — but that lens *is* "what the previous pass's fix broke." Its
subject matter **does not exist until pass-10's fixes land**, so it cannot be assigned to a
concurrent arm.

There is a real distributional shift (pass 1 skews falsifiability, later passes skew
propagation) but it is **temporal, not lens-orthogonal**: early findings are about the draft,
later ones about the repairs. Fan-out cannot exploit a shift along the time axis.

## 3. Serial dependence makes fan-out UNSOUND — 75%, measured

Eligible passes (2..N, since pass 1 has no predecessor): **20**. Passes that found ≥1 defect
inside the *previous pass's own fix*: **15**. → **75%**.

| Plan | Eligible | Self-injecting | Clean |
| :-- | --: | --: | :-- |
| plan-049 | 4 | 3 | p5 |
| plan-050 | 12 | 9 | p2, p3, p13 |
| plan-051 | 4 | 3 | p5 |
| **Total** | **20** | **15 (75%)** | 5 |

Corroborated three independent ways: plan-050's **pre-registered** pass-5 measurement
(*"Defects per resolution: 11/17 ≈ 65%"* against a 36% baseline); its terminal log bullet
(*"FIRST CLEAN ROUND IN NINE"*); and plan-051's own passes 2, 3 and 4 each recording that the
blocking defect lived inside the prior fix.

**At a 75% rate the dominant defect class is created by a fix a concurrent arm cannot see.**
That is EXP-005's chain-property objection, now measured rather than asserted.

## 4. Both capabilities the revival leans on are unavailable or unnecessary

| Claim | Measured |
| :-- | :-- |
| Child sessions allow richer tool calls | **Already available to sub-agents.** `REQ-AGENT-043` authorizes the sandbox spike verbatim; EXP-005 itself did `mktemp -d` + `git init` + `bd init` + poured a wisp inside a sub-agent |
| Automatic cleanup / harvesting / pruning | **Does not exist.** yf-herdr has `## Launch`, `## Observe`, `## Mine deviations`, `## Rules` — and **no `## Teardown`**. The single close-related line is a *prohibition* (#204) |
| Child sessions improve containment | **Backwards.** A sub-agent's tool set is restricted by its definition; a child session runs with whatever the harness allows. On containment the child session is **weaker** |

**Where child sessions genuinely win is dispatch verifiability** — a script that dispatches beats
a bead that says "dispatch," because the exit test reads a file the child wrote. That is #198's
actual thesis, and it is **orthogonal to fan-out**: it improves *serial* dispatch just as much.

## 5. What would reopen it — all three, not any one

1. A **lens-clustering signal in a corpus that has one**: ≥70% of a pass's concerns in a single
   lens, with the dominant lens differing between adjacent passes, and not the propagation lens.
   Nothing in 042–051 does this.
2. A **measured N=3 concurrent trial** reporting unique-concern yield and **inter-arm overlap**
   against the sequential baseline. High overlap means fan-out is redundant work.
3. A **serial-dependence rate that has fallen** below ~25% for three consecutive plans. Note
   plan-050 already tried one such change and pre-registered its refutation: delegated
   resolution moved injection *up* (65% vs 36% baseline), not down.

## 6. Bookkeeping correction

The "29 passes across four plans" figure **reproduces exactly**
(`ls docs/plans/plan-04[7-9]-*/reviews docs/plans/plan-050-*/reviews | grep -c pass-` → 29).

Corpus total is **142** pass files. Plans 042–046 show `reviews/pass-*.md` counts diverging from
`log.md` bullets — **not a defect**: those plans use the legacy `review:` token, which changed to
`review-pass:` at plan-047. REQ-PORT-006 count-equality holds for every plan in the token's era.

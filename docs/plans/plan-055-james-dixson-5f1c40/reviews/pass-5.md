---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: Red-team pass 5 — verdict REVISE (bound reached), 5 concerns (1 high); reviewer recommends against a sixth cycle
---

# Red-team pass 5

## Verdict: REVISE
> **One high-severity concern, the direct continuation of pass 4's C1 — which is not closed.** The fix
> is roughly four lines. **I explicitly recommend against a sixth adversarial cycle**: apply the
> C1-completion edits, and execute. Nothing else found is above medium.

## Resolution verification — pass 4's 13 concerns

**11 of 13 genuine; C1 partial; C2 partial.**

Mechanical graph re-check: **35 issues, 22 criteria, zero dangling edges, zero cycles** (the new
`2.2 → 2.3` edge orders cleanly behind `2.1`), every criterion's `Discharged-by` resolves, every
issue discharges at least one criterion, and `5.4` still dominates the entire graph. Id precedents
verified against `SPEC.md`: `INSTALL-011`, `MARK-006`, `DOCTOR-007` are each the correct next free
id. `CHANGE-VALIDATION.md:51` and `:53-59` (exactly 7 lines) are both cited accurately.

## Strengths

- **Three of C1's four behaviours are genuinely closed.** `REQ-YF-MARK-006` carries the
  reversible-apply clause; `REQ-YF-DOCTOR-007` follows the measured one-REQ-per-axis precedent; 4.8
  and 4.9 are wired. 5.2a reaches 0.3 transitively via 1.5 → 1.4 → 1.3 → 1.2 → 1.1 → 0.3.
- **SC1's restatement is falsifiable, not prose.** It runs a named script 0.7 creates, and the
  exit-2-on-empty-set clause forecloses vacuous certification. **The vacuity axis is closed** — 17 of
  22 criteria run a failable command, 5 `manual:` entries each state why, and no unguarded
  `cargo test` survives.
- **The gate layer remains the plan's strongest part.**
- **The C5 fix is the right shape** — dropping the transform *before* the collapse closes an
  order-dependence rather than documenting it.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| H1 | **high** | **The behaviour set is still not closed, and the guard introduced to prove it is closed cannot run as worded.** Three composing findings: **(1) a fifth uncovered behaviour — Issue 3.2**, which teaches skills-root resolution to follow `CLAUDE_CONFIG_DIR`, a change to *where files land*, asserted as SC10. 0.4 amends the **surface-dir** override only; 0.2 has no env clause; 0.9 is about warnings. **D-9's own text says the override attaches "to the SKILLS column only for claude-code" — that half has no SPEC issue.** (2) **Issue 3.3 has no dependency path to 0.9**, though 0.9's body reads *"Both warnings are user-visible behaviour shipped by 3.3 and 4.9."* The edge landed on **3.2** instead, which 0.9 does not claim to cover — so 3.3 can legally land before the requirement governing it. (3) **0.7's second assertion has no mechanical subject** — of 25 issues in Epics 1-5, exactly **one (2.3)** names a `REQ-*`, and the plan supplies no predicate for "ships user-visible behaviour", so the check degenerates into a second hand-authored list. Failure direction is safe (SC1 fails loudly), so the risk is low and the rework is certain |
| M1 | medium | **5.1a runs `yf skills install` mid-execution — which AGENTS.md names as "the one real constraint" — and the issue does not acknowledge it.** `plan_manager.py` is re-invoked per call, so a mid-execution deploy takes effect for scripts in the same session while `SKILL.md` prose stays loaded from invocation. 5.1a discusses a *different* hazard (the stale-private-tree window) and is silent on this one. Probably unavoidable — SC17 requires the post-collapse stamp — but an unstated collision with a named repo constraint reads as an oversight |
| M2 | medium | **C2's residue survived the C2 fix.** `plan.md:183` now asserts both "no issue in this plan rewrites it" and "Five issues in Epic 4 rewrite the smoke" in one paragraph. **Third D-14 residue in three consecutive passes, and the second time an edit was added without the superseded sentence being deleted** |
| L1 | low | **2.4's `name_transform` agreement assertion is trivially true the moment 2.3 lands** — after the drop every non-claude row is `None`, so it holds vacuously. A correct *future* regression guard, but not evidence for anything 2.2 does |
| L2 | low | #238's `Notes` in `upstream-triage.md` is truncated mid-sentence — the one field C8 filled from a source longer than the cell |

## Missing

1. A SPEC amendment covering the **claude-code skills-column env override** (3.2 / SC10).
2. The `3.3 → 0.9` edge the plan's own 0.9 body asserts.
3. A mechanically derivable predicate for 0.7's behaviour-set assertion.
4. An acknowledgement in 5.1a of AGENTS.md's mid-execution deploy constraint.

## Gate Assessment

| Gate | Reachable? | Assessment |
| :-- | :-- | :-- |
| Start Gate | n/a | C11's drivability confirmation landed correctly; no frontloading miss remains |
| live-harness drivability | Yes | Sound |
| migration apply | Yes | **Still the strongest gate in the plan.** C12's schema-ownership residual is closed — 1.4 owns it, 5.1 references it |
| Reconcile Gate | Yes | `5.4` dominates all 35 issues — re-verified |

**No unreachable condition, no cycle, no gate naming a script no issue creates. The gate layer needs no further work.**

## Upstream Assessment

Unchanged from pass 4 and sound. All eight triage entries now carry filled `Disposition:`/`Notes:`.
The #243 note is notably better — it records that this plan builds a quarantine-backed remover
*specifically so it does not create a second instance of #243's hazard*, a real relationship rather
than a dismissal.

## Recommendations

1. Extend 0.4 to add the **skills-column** override to `REQ-YF-INSTALL-007` per D-9's second half.
2. Add `0.9` to **3.3's** `depends-on`; remove it from 3.2's unless 0.9 is extended to cover 3.2.
3. Restate 0.7's second assertion over a computable predicate — *"every issue in Epics 1-5 has a
   `depends-on` path to at least one Epic-0 issue naming a `REQ-*`"* — which run against the current
   draft flags 3.3 and nothing else.
4. Acknowledge the AGENTS.md deploy constraint in 5.1a.

## Bottom line

> The plan is close and its structure is sound — clean graph, sound gates, non-vacuous criteria,
> honest upstream dispositions. Pass 4's condition was met for three of four behaviours; the fourth
> exposed a fifth (3.2), one edge landed on the wrong node, and the guard criterion needs a computable
> predicate. **That is a REVISE by the standard pass 4 set, but it is a four-line fix — apply it and
> execute; a sixth adversarial pass would not earn its cost.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | **Concern accepted in all three parts.** (1) 0.4 extended to add the **skills-column** override to `REQ-YF-INSTALL-007` for claude-code, per D-9's second half, and `0.4` added to 3.2's `depends-on`. (2) `0.9` added to **3.3's** `depends-on` and **removed from 3.2's** — the edge had landed on the wrong node. (3) 0.7's second assertion restated over the computable predicate: *every issue in Epics 1-5 has a `depends-on` path to at least one Epic-0 issue naming a `REQ-*`* | `main-session` | `resolved` |
| M1 | medium | 5.1a now states the AGENTS.md mid-execution-deploy constraint is **knowingly taken**, why it is unavoidable (SC17's post-collapse stamp clause), and what an executor must not do afterward | `main-session` | `resolved` |
| M2 | medium | The superseded clause is **deleted**, and the paragraph re-read end to end rather than patched — the same lesson 0.6 encodes as a sweep | `main-session` | `resolved` |
| L1 | low | 2.4 now states the agreement assertion is a **regression guard against a future transform**, not evidence for anything 2.2 does | `main-session` | `resolved` |
| L2 | low | #238's truncated `Notes` completed | `main-session` | `resolved` |

**All 5 concerns resolved. This file is now FROZEN.**

# Wording-lever check (Issue 3.1)

EXP-003 recommended checking whether its three misses respond to **TRIGGER wording alone**
before any length trims. Run 2026-09-25 with `scripts/checks/skill_trigger_eval.py`, candidate
mode (all 20 skills staged from the execute branch, post-Issue-1.1 text), 3 reps per cell.
Spend is in `spend.jsonl`.

## Result

| Miss (EXP-003) | EXP-003 (installed mode) | Candidate, text unchanged | Candidate, TRIGGER wording changed |
| :-- | :-- | :-- | :-- |
| pi D3 (`yf-drift-check`) | 0/3 | **0/3** (6 tool calls, no skill) | **3/3** (activates at tool 1) |
| pi O1 (`yf-optimal-instructions`) | 0/3 | **3/3** | not needed |
| CC O2 (`yf-optimal-instructions`) | 0/3 | **3/3** | not needed |

**The wording is the lever for D3, and the description is not the lever for O1/O2.**

- **pi D3 responds to TRIGGER wording.** pi read the spec file and grepped for contradictions
  itself, never consulting the skill. A single added TRIGGER clause turned 0/3 into 3/3 with
  activation at the first tool call: *"the operator edited a spec, doc or SPEC.md requirement and
  asks whether anything else still agrees with it or now contradicts it"*. No other word in the
  description changed. The clause names the intent's own shape (an edit plus an agreement
  question), which the old text reached only through "a file covered by an approved
  DRIFT-CHECK.md manifest", a precondition the model cannot see from the prompt.
- **pi O1 and CC O2 were not description misses.** Both pass 3/3 in candidate mode with the text
  unchanged. EXP-003 ran **installed mode**, with the operator's full configuration: ~30 other
  skills plus, on CC, the rules aggregate. So those two misses came from the installed
  environment (competition, or the always-loaded rules asymmetry EXP-003 noted), not from the
  `yf-optimal-instructions` description. The lever for them is **not** the description. It is the
  installed surface, which is Issue 5.4's rules-aggregate question. They are re-checked in
  installed mode at Issue 5.3.

## Neighbour check (the edit does not take over sibling intents)

With the edited `yf-drift-check` text, 1 rep per harness over D3 plus every near-miss that names
`yf-drift-check` (D-N1, D-N2, D-N4, V-N1, O-N2, S-N2): **14/14 correct.** D-N4 ("run the fast
validation tier…") routed to `yf-change-validation`, the right sibling, on both harnesses. CC D3
stayed 1/1.

## Disposition

The edited clause is carried into Issue 3.3 as `yf-drift-check`'s starting text. Issue 3.2's
baseline records the **unedited** post-1.1 text, per the plan, so the before/after stays
measurable. The O1/O2 finding is evidence for the Issue 5.4 follow-on.

---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #270: yf-plan: plan-review.formula.toml has NEVER been poured — the only structural mid-burn review gate in yf has not fired in 27 review passes

- **Number:** 270
- **Title:** yf-plan: plan-review.formula.toml has NEVER been poured — the only structural mid-burn review gate in yf has not fired in 27 review passes
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/270
- **State:** OPEN
- **Labels:** 

## Body

> Found by the `yf-judgement` design investigation (EXP-001, plan-059), while surveying yf for a
> trigger point that fires reliably. Verified independently before filing.

## The defect

`skills/yf-plan/formulas/plan-review.formula.toml` defines one Phase-3 review cycle —
conformance → red-team → resolve → **approval gate** — and its final step is a real bd gate:

```toml
[[steps]]
id = "gate"
title = "Review verdict gate: {{objective}}"
type = "gate"
[steps.gate]
type = "human"
```

**It has never been poured.** Measured against the full bead universe: **zero** beads match its
step titles across all **1,245** beads. It landed **2026-08-24** (`57a21e3`, plan-052 Issues 5.1 /
5.3), and **27 review passes have been committed since** — every one of them through the prose
loop the formula was written to replace.

## Why this matters more than an unused artifact

This gate is, per the EXP-001 survey, **the only structurally-mechanical mid-burn boundary in all
of yf**. Its properties are exactly the ones every "when should we stop and ask?" design needs:

- it fires at the end of **every** review cycle, not at a threshold like cycle 5;
- it **holds structurally** — a bd gate blocks its dependents — rather than relying on an agent
  choosing to run a check.

Everything else available is a check an agent must remember to invoke.

## This is #145's finding 4, recurring on the mechanism built to prevent it

#145 established, from two proofs in this repo, that **"a manually-invoked skill will not be
invoked"**:

- `closable` shipped and was never once run to completion until someone tried it;
- `plan_manager.py audit` existed and worked, but never fired at the phase that mattered, and four
  plans shipped non-conformant files.

The formula is the structural answer to exactly that class. **And it was never wired in**, so the
finding has now recurred *on its own remedy*. That is the strongest available evidence for #145's
thesis, and it is also why this is worth its own issue rather than a footnote: the failure is not
that someone forgot to run a check, it is that a mechanism designed to remove the forgetting was
itself left unconnected.

## Scope decision (operator, 2026-08-28)

Filed **separately** rather than folded into plan-059 (`yf-judgement`, #269). Rationale: a new
skill's delivery should not be coupled to repairing existing `yf-plan` machinery. `yf-judgement`
will bind to `review-loop-check` (measured 5/6 invocation rate, versus this formula's 0/27) and
its escalation payload is being designed so it can **move onto this gate later without
redesign** — so fixing this issue upgrades `yf-judgement`'s trigger for free.

## What to investigate

1. **Why it was never wired.** plan-052 landed the formula as part of a `prevention_formula` /
   verify-artifact aspect. Was a pour site ever specified in `SKILL.md`, or did the artifact land
   without a caller?
2. **Whether anything would have detected this.** Nothing failed. No test asserts the formula is
   poured, and an unpoured formula is indistinguishable from an unused one — which is the same
   silent-absence shape as `closable`.
3. **Whether a mechanical check is the durable remedy**, as #268 concluded for its own unswept
   defect class. The repo has the convention (`check_gh_direct.py`); an analogous check could
   assert every shipped formula has a pour site.

## Related

- #145 — `yf-retrospective` (finding 4 is the thesis this instantiates)
- #269 — `yf-judgement` (found it; designed around it)
- #268 — an unswept defect class found the same day, same shape: fixed once, regrew, nothing checked

🤖 Generated with [Claude Code](https://claude.com/claude-code)


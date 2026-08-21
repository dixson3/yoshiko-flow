---
type: Reference
okf_spec: OKF-PLAN
id: neg-179-observations
description: SC4's two observations of the neg-179-open-wrapper negative control, pre- and post-fix (Issues 1.1 and 1.4)
---

# `neg-179-open-wrapper` — SC4's two observations

## Why this is recorded here and not in `red-prework.md`

`neg-179-open-wrapper` is a **negative control** and a **raw scenario**, not a fixture. Issue
0.2 defines a fixture as a script that exits 0 iff its control's asserted behaviour holds, and
`controls.txt` lists **only** red→green controls. This scenario's assertion — *an open wrapper
drives `close_cascade.py` non-zero* — is **invariant across Issue 1.2's fix**. A *fixture* for
it would exit 0 on both sides, while SC4 wants the observed `close_cascade.py` exit **itself**,
which is non-zero on both sides (pass-7 C67, pass-8 C80).

So it is run directly, recorded here, and never appears in `controls.txt`. The capability gate
never asks it for a GREEN record, and `verify-all` never sees it. Running it is not a
`redcheck.sh` verb, so it produces no gate evidence — which is deliberate.

## What it protects

**R5**: that fixing #179 at the pour/resolve seam does not mask a real cascade failure. Issue
1.2 forbids weakening `close_cascade.py`'s `_bead_is_terminal`; this scenario is the
*behavioural* check that it was not weakened anyway. A structural check (`git diff` empty) and
a behavioural one are different claims, and SC4 makes both.

## The two observations

| Arm | Issue | Tree | `close_cascade.py` exit | Wrapper status | Verdict |
| :-- | :-- | :-- | --: | :-- | :-- |
| pre-fix | 1.1 | `plan-050-…-execute` before 1.2 | **2** | `open` | invariant holds |
| post-fix | 1.4 | `plan-050-…-execute` at 1795cf3 | **2** | `open` | invariant holds |

Exit **2**, not 1, and that is the correct reading: `close_cascade.py` reports a **fail-loud**
on an open plan-tree child. What SC4 asserts is that the exit is **non-zero** — that the
cascade still refuses — not which non-zero value it chooses.

The scenario's own exit is **0** on both arms, because its assertion (*the cascade refuses*)
holds on both. That inversion is exactly why it is not a fixture.

## The structural half of SC4

```
git diff main -- skills/yf-plan/scripts/close_cascade.py    # empty
```

The whole file is byte-unchanged on the execute branch, so `_bead_is_terminal` is a fortiori
unmodified. Verified at Issue 1.2 and re-verified at Issue 1.4.

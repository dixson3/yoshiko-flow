**Found by plan-063 (EXP-002 rec 5b) and DELIBERATELY LEFT UNSCOPED.**

Steps L8–L15 — the whole close chain — call `subprocess.run` **directly** rather than through
`ctx.run`. `LandingContext.run` is the injection seam every other step uses; it is what lets a
Tier-1 test drive the real step function against a scripted runner, and it is what caught
`git issue comment` / `git push --issues` / `git self install` (the wrong-executable class).

Because L8–L15 bypass it, **the rehearsal cannot inject into them — it must replace whole steps**:

```python
pm._land_l8_to_l15_close_chain = lambda ctx: [...]
pm._land_l12_close_cascade     = lambda ctx: {...}
pm._land_l13_l15_finish        = lambda ctx: [...]
```

Three of the fifteen steps are therefore **not exercised at all** by the rehearsal — the record it
emits lists them under `stubbed_steps`, honestly, but a stubbed step proves nothing about the code
it stands in for. A zero-stub spike reached **18 of 19 steps**; only L14 genuinely needs a poured
bead fixture.

**Why plan-063 did not fix it.** The change is a refactor across eight steps plus their tests, and
plan-063's scope was the L18 crash, the L16 commit and the dry-run blind spot. Bundling it would
have put a wide refactor in the same change-set as the fixes for a live production defect.

**Proposed fix.** Route L8–L15 through `ctx.run`, then delete the three whole-step stubs from
`land_rehearsal.py` and let the rehearsal exercise the close chain for real against a poured
sandbox bead tree.

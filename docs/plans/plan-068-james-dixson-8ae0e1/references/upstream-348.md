---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #348 - The landing close chain bypasses ctx.run: bare
  subprocess.run gives L8-L15 the wrong cwd and no injection seam'
---
# Upstream #348: The landing close chain bypasses ctx.run: bare subprocess.run gives L8-L15 the wrong cwd and no injection seam

- **Number:** 348
- **Title:** The landing close chain bypasses ctx.run: bare subprocess.run gives L8-L15 the wrong cwd and no injection seam
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Shared cause

Two findings from plan-063 that are one omission with two faces: the landing close chain (L8-L15) calls `subprocess.run` directly instead of routing through `LandingContext.run`. That single fact produces a correctness bug (wrong `cwd`) and a testability bug (no injection seam). Both disappear together the moment the close chain routes through `ctx.run`; filing them separately would invite two partial fixes to the same line.

Grouped per the coarse-granularity convention in AGENTS.md. Recorded during plan-063 and deliberately not fixed there.

---

## Face 1 - L14's `bd list` inherits the ambient cwd (bead `yf-i127`)

**Found by plan-063 (EXP-003) and deliberately not fixed there.**

Every subprocess the landing close chain launches passes `cwd=ctx.root` — **except one**. L14's
pour-fidelity `bd list`:

```python
bl = subprocess.run(["bd", "list", "--all", "--include-gates", "--limit", "5000", "--json"],
                    capture_output=True, text=True)
```

has no `cwd`, so it inherits the process's ambient working directory. The `uv run pour_fidelity.py`
call three lines below it *does* pass `cwd=ctx.root`, which makes the omission look like an
oversight rather than a decision.

**Why it is not currently visible.** `land --apply` already refuses to run outside the primary
checkout (`_land_assert_primary_checkout`, REQ-LAND-010), so in practice the ambient cwd *is*
`ctx.root` today. The defect is that nothing in the call itself establishes that — it is correct
by a precondition enforced elsewhere, which is exactly the kind of coupling that breaks silently
when the precondition moves.

`bd` resolves its database by walking up from the cwd, so under any future call path that does not
already guarantee the primary checkout, this reads a **different beads database** — or none — and
`pour_fidelity` then judges the wrong DAG.

**Proposed fix.** Add `cwd=ctx.root`, matching every sibling call. Consider a mechanical check
that no `subprocess.run` in the landing path omits `cwd`.

---

## Face 2 - L8-L15 bypass the injection seam (bead `yf-9yb0`)

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

---

<sub>Filed from plan `plan-063-james-dixson-3f74c1` (bundle: `docs/plans/plan-063-james-dixson-3f74c1`). Beads: `yf-i127`, `yf-9yb0`.</sub>


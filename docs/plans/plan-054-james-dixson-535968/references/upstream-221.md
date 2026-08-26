---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #221: yf-plan: SC24-style criteria assert a MOVING fact (stamp == HEAD) where they should assert a DURABLE one

- **Number:** 221
- **Title:** yf-plan: SC24-style criteria assert a MOVING fact (stamp == HEAD) where they should assert a DURABLE one
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured at plan-052's completion, and re-measured independently before filing:**

```
yf --version stamp: ed0803f
HEAD:               e94206a
```

`SC24` reads: *"The deployed tree matches source and the stamp matches HEAD, verified AFTER the
final commit and a rebuild."*

## The defect

`SC24` asserts a **moving** fact — `stamp == HEAD` — where it should assert a **durable** one:
*the stamp equals the commit the binary was built from, recorded at deploy time.*

The deploy genuinely happened and `SC24` was genuinely green at `ed0803f`. Then the commit
**recording that the close chain passed** moved `HEAD`, and re-staled the stamp. That commit
touches `docs/plans/**` only — nothing `cargo:rerun-if-changed` watches — so no rebuild would
have re-stamped it either.

**Re-stamping does not terminate.** Any further commit re-stales it, *including the commit that
records the check passing*. The criterion as specified can never be permanently true.

## It was predicted, and closed on a false premise

plan-052's red-team **pass 4** raised this as **M7**:

> `recheck-criteria` runs at completion, **AFTER** 7.5's commit

The recorded resolution was: *"7.5 reworded to rebuild-then-verify after the final commit."*

**There is no final commit.** The resolution assumed one exists. That is the most useful part of
this issue — a red-team concern closed on a false premise, where the false premise was in the
resolution rather than in the concern.

## The fourth instance of one class

`SC1c`, `SC20`, the **Reconcile Gate**, and now `SC24` are the same defect on four surfaces: **a
predicate that does not implement the claim it verifies.** The first three are recorded in #219
and #220.

The template is **`SC1c`'s accepted fix**: stop measuring a spelling that stops naming the thing
(`main..HEAD`, empty once the branch lands), and measure something **permanent** (`M^1..M^2` —
the same commits, same order, resolvable forever).

## Suggested direction

Record the built-from commit at deploy time — in the deploy receipt (plan-052 has
`assets/sc-deploy.md`) or in the `from-build` marker `yf` already writes — and have the
criterion assert **stamp == recorded-built-from**, plus that the deployed tree matches the
source **at that commit**. That is durable: it stays true no matter how many commits land
afterwards, and it still catches a genuinely stale or never-run deploy.

`SC24` was deliberately **NOT amended** and the plan was **NOT** reverted to `reconciling`. The
operator ruled that its falseness is recorded here rather than papered over — which is the same
direction as everything else in this plan: fix the predicate, or file it, but never lower the
claim to match what the check happens to return.

---

*Filed as plan-052's tenth deferred defect under grant AMENDMENT 4. The others are #211-#217,
#219 and #220. Enumeration: `docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*

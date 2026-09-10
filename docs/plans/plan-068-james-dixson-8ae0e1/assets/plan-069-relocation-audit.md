# Issue 3.3 — does plan-069 carry every item this split relocated?

**Verified 2026-09-09, against `docs/plans/plan-069-james-dixson-9d2878/plan.md`.**

Issue 3.2 publishes a cross-reference pointing at plan-069. This audit runs **before** that
cross-reference is believed, because *a concern resolved by relocation must land in the
destination's text, not only in this plan's Resolutions cell.*

## The eight relocated items

| # | Item | Origin | In plan-069? | Where |
| :-- | :-- | :-- | :-- | :-- |
| 1 | The `recover()` fall-through must **fail closed** | EXP-004 implication 6; named twice by pass-1, carried by neither plan (pass-2 C6) | **yes** | *"Scope items relocated here"*, first bullet — quotes the `resume_from = rec.get(...)` line and EXP-004's *"the single line standing between an unhandled action and a re-push"* |
| 2 | A **"no write occurred" helper** | EXP-004 implication 5 (pass-2 C6) | **yes** | same section, second bullet — with the measured `0 hits` for `grep -n "no write\|nothing was written\|unchanged"` |
| 3 | A **behavioral** test for `_land_assert_primary_checkout` | pass-2 C6 | **yes** | same section, third bullet — *"five references … none behavioral"* |
| 4 | The **`REQ-LAND-036`** exclusion-table amendment | EXP-003 implication 2; carried by neither, while plan-069 falsely said plan-068 had done it (pass-3 C6) | **yes** | design question **C5** |
| 5 | The **`REQ-LAND-018`** rationale amendment | same | **yes** | design question **C5** |
| 6 | EXP-003's **post-L4 digest absence** finding | EXP-003 | **yes** | *"Two further measured defects"*, first bullet — *"no test … computes a digest on a post-L4 tree"*, and why `REQ-LAND-036`'s own verifier stays green under either fix and under no fix |
| 7 | EXP-001's **L4 misleading-diagnostic** defect | EXP-001 | **yes** | same section, second bullet — legibility, not safety, because it fails closed and pre-push |
| 8 | **L2's in-place behaviour and the declared boundary** | created by pass-3's own fix, carried by neither (pass-4 C7) | **yes** | *"L2's in-place behaviour, and the boundary plan-068 declared around it"* — records both measured facts and that plan-068 implements and tests **no** part of it |

Plus the **`#334`-vs-SC4 cross-plan coupling** (pass-2 C9): present, and **corrected** — see below.

## The false-attribution check

plan-069 must contain **no claim about plan-068's SPEC scope that plan-068's Epic 0 does not
support**. Verified against what Epic 0 actually landed:

> *"plan-068's Epic 0 allocates `REQ-LAND-037`/`-038` and amends `REQ-LAND-002`/`-004` and
> `REQ-BRANCH-001`/`-002`/`-004` — **neither `REQ-LAND-036` nor `REQ-LAND-018` is touched by
> it.**"* — plan-069, design question C5

**Exact.** That is the allocation `assets/req-allocation.md` records and
`assets/check_req_allocation.py` verifies bidirectionally (12 ids in the landed SPEC diff, 2
allocated, both directions agree, exit 0). The earlier false assertion — that plan-068 had already
performed those two amendments — is explicitly corrected in plan-069's own text, labelled
*"Correction (plan-068 pass-3 C6)"*.

The other two plan-068 claims in plan-069 were checked and are accurate: Issue 0.4 specifies L1
only and routes L2 here; plan-068 dispositions #349 and #353 `partial` and does not close them
(verified `state=OPEN` on both after Issue 3.1's writes).

## One claim was WRONG, and is corrected in plan-069's text

The cross-plan coupling note **predicted** a mechanism plan-068 did not use:

- **Predicted:** plan-068's Issue 2.5 end-to-end test clears the consent gate by passing an
  **explicit tty allow-list**.
- **Landed:** `test_end_to_end_in_place_landing_reaches_L_DONE` drives **`_land_execute`
  directly** with an explicit decision-level `steps` map, and **never reaches `_land_tty_gate` at
  all** — that gate lives in the **CLI preamble**, not in the executor.

The *intent* is satisfied more strongly than the prediction (a test that never invokes the gate
cannot be broken by a change to it), but the **verification step is different from the one
plan-069 asked for**. Left uncorrected, a plan-069 executor would look for an allow-list argument
in that test, fail to find one, and reasonably conclude the coupling had been dropped. The note
now says what to verify instead: that the **CLI-level** `--apply` path remains drivable under
test, since plan-068's coverage deliberately stops at the executor boundary and #349's preamble
tests are what will cover the frame above it.

This is the audit doing its job. Seven of the eight items were carried faithfully; the eighth was
carried as a *prediction* that execution falsified, which no amount of re-reading plan-068's
Resolutions table would have caught.

## Two other writes to plan-069, both recorded here

1. **A declared absence on its empty Success Criteria table** — see
   `findings/exec-001-inherited-doclint-red.md`. plan-069 is at `status: scoping` and its criteria
   are legitimately unwritten until its carried design questions are settled.
2. **`_shared/test_doc_lint.py`'s SC41 measurement re-pinned** from `0` to `1`, naming plan-069 as
   the understood firing and adding a second assertion that it *is* plan-069 rather than a new
   offender — the two-assertion shape the sibling `gate-completeness` arm already uses for the
   same situation.

   **The gap this exposes is recorded rather than worked around.** `cell-non-empty`'s zero-row
   branch is generic across sections, but its declared-absence sentinel and remediation message
   are hard-coded to upstream issues: a zero-row `## Success Criteria` table is told to *"add a
   `no-upstream-issues:` line"*. Writing that line under Success Criteria to buy a green would be
   fabricating an assertion to silence a check — the move `#185` rejected as *"strictly worse than
   the finding it silences"*. Making the sentinel section-appropriate is a `doc_lint` behaviour
   change and therefore SPEC-first work, out of scope here.

---
type: Plan
okf_spec: OKF-PLAN
description: 'Plan B of the landing-chain split: the --apply preamble tests, the tty-gate
  bypass, the executor-bookkeeping guard, the digest journal projection, and the two
  measurement defects'
id: plan-069-james-dixson-9d2878
author: james-dixson
created: '2026-09-09'
status: scoping
---
# Plan: Plan B of the landing-chain split: the --apply preamble tests, the tty-gate bypass, the executor-bookkeeping guard, the digest journal projection, and the two measurement defects

**ID:** plan-069-james-dixson-9d2878
**Author:** james-dixson
**Created:** 2026-09-09
**Status:** scoping

## Objective
Plan B of the landing-chain split: the --apply preamble tests, the tty-gate bypass, the executor-bookkeeping guard, the digest journal projection, and the two measurement defects

## Motivation
**This is PLAN B of a two-plan split** created at plan-068's pass-1 red-team (concern C1,
operator-confirmed). plan-068 v1 was 37 issues with a dependency chain 8 nodes deep; it was cut
into an enabling half and a repair half.

**plan-068 (Plan A)** lands the `ctx.run` seam and makes `land` reachable under
`execute.worktree: false`. **This plan carries the rest**, and the cut is load-bearing rather than
arithmetic: because Plan A lands the in-place-landing fix, **this plan's own landing is the first
in this repo that does not pay #331's tax** — no hand-cut execute branch.

Scope carried here:

| Upstream | Work |
| :-- | :-- |
| #349 | The `--apply` preamble refusal tests (17 uncovered statements, 8 refusal cases) and the executor-bookkeeping guard (`yf-pyqn` option (b)) |
| #334 | The `_land_tty_gate(allow_list=[None])` bypass, and replacing its provably vacuous test |
| #353 | The digest journal projection over all five self-mutated facts |
| #350 | L16's laundered unpushed count |
| #352 | `requires_mention` checked at `--dry-run`, before the writes are public |

**plan-068 does NOT close #349 or #353** — both are dispositioned `partial` there and this plan is
recorded as the closing one.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #349 | The `land --apply` executor frame is outside REQ-LAND-030's wrapper and the test suite | include | **This plan closes it.** plan-068 dispositions it `partial` (correction only) and explicitly does not close it | _TBD_ |
| #353 | `LAND_DIGEST_EXCLUDED` omits self-mutated facts | include | **This plan closes it.** plan-068 dispositions it `partial`. Design not yet settled — see the carried questions below | _TBD_ |
| #334 | `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally | include | Deferred here at the plan-068 A/B split | _TBD_ |
| #350 | A measurement that failed is reported as a green number | include | Deferred here at the split. Scoped to L16 only | _TBD_ |
| #352 | `land --dry-run` never checks `requires_mention` | include | Deferred here at the split | _TBD_ |

## Investigation Findings

**Inherited from plan-068's investigation** — both findings are copied into `findings/` here so
this bundle stands alone for a cold reader.

- [EXP-003 — the digest exclusion](findings/exp-003-digest-exclusion.md). Bead `yf-jp7z`'s
  premise confirmed, **its remedy refuted**: the proposed WIDE exclusion blinds the digest to all
  three foreign-landing classes and lets a *conflicting* foreign landing validate `pass`. Real
  scope is **five** self-mutated facts across **four** resume points. L4 alone mutates them, not
  L6, and `predicted_tree` is stable across the landing's own merge.
- [EXP-004 — preamble coverage](findings/exp-004-preamble-coverage.md). "Zero coverage" refuted
  as stated (**61.4%**, all happy-path plus one refusal, 17 uncovered statements all refusal
  bodies). The preamble has **nine** steps, not six. `#334`'s bypass and its test's vacuity both
  confirmed by spike **and** by line data. `yf-pyqn` confirmed with two sites the bead omits.

### Scope items relocated here — do not drop these again

pass-2 C6 measured that three items with direct measured evidence were carried by **neither** plan
after the split. They are recorded here explicitly, because a concern resolved by relocation must
land in the destination's text:

- **The `recover()` fall-through must fail closed.** The CLI computes
  `resume_from = rec.get("resume_after") if action == "resume" else None`, so an `action` outside
  `{start, done, halt, resume}` silently yields a **fresh landing from L0, re-running
  `l6_push_one` and `l7_reconcile_writes`**. `recover()` is total today, so this guards a future
  edit — EXP-004 calls it *"the single line standing between an unhandled action and a re-push"*.
  It was plan-068 v1's Issue 3.6 and was named twice by that plan's pass-1.
- **A "no write occurred" helper**, snapshotting `git rev-parse HEAD`, `git rev-parse origin/main`
  and journal-file existence around every refusal. `grep -n "no write\|nothing was written\|unchanged"
  test_land_apply.py` returns **0 hits**, which is why the preamble's whole safety property is
  currently checked only by a test that reads the *source text*.
- **A behavioral test for `_land_assert_primary_checkout`.** Five references exist in tests, **none
  behavioral** — one monkeypatch and four AST/source-text assertions — and its refusal return is
  never executed.

- **L2's in-place behaviour, and the boundary plan-068 declared around it.** plan-068's Issue 0.4
  specifies **L1** only and records L2 as a declared scope boundary routed here. Measured: L2 runs
  `git checkout <target>` **in `ctx.root`**, and under `execute.worktree: false` `ctx.root` *is* the
  execute checkout — so L2 switches the one and only working tree off the execute branch, and the
  subsequent `git pull --rebase`'s return code is ignored. plan-068 implements and tests **no** part
  of this. (plan-068 pass-4 C7: this was created by pass-3's own fix and was briefly carried by
  neither plan.)

Two further measured defects, neither in plan-068's scope:

- **EXP-003's absence finding:** no test in the suite ever computes a digest on a **post-L4 tree**.
  REQ-LAND-036's own verifier synthetically flips facts on a repo where **no merge ever happened**,
  so it stays green under either fix *and* under no fix.
- **EXP-001's L4 diagnostic is misleading:** when L4's tree assertion fires it reports a message
  about `pull --rebase` picking up commits, which is not what happened. It fails closed and
  pre-push, so this is legibility, not safety.

**Cross-plan coupling (pass-2 C9), CORRECTED AGAINST WHAT PLAN-068 ACTUALLY LANDED**
(plan-068 Issue 3.3, verified 2026-09-09). The coupling is real and the mechanism is **not** what
this line predicted, so the verification step changes:

- **Predicted:** plan-068's Issue 2.5 end-to-end test clears the consent gate by passing an
  explicit tty allow-list.
- **Landed:** `skills/yf-plan/scripts/test_land_inplace.py::test_end_to_end_in_place_landing_reaches_L_DONE`
  drives **`_land_execute` directly**, with an explicit decision-level `steps` map. It never
  reaches `_land_tty_gate` at all, because that gate lives in the **CLI preamble**, not in the
  executor.

The intent is satisfied more strongly than the prediction: a test that never invokes the gate
cannot be broken by a change to the gate. **So the `#334` verification step is different from
what this line asked for** — do not go looking for an allow-list argument in that test and
conclude the coupling was dropped. What to verify when the `#334` guard lands: that the
**CLI-level** `--apply` path still has a way to be driven under test, since plan-068's end-to-end
coverage deliberately stops at the executor boundary and #349's preamble tests (this plan's) are
what will cover the frame above it.

**Unresolved design questions carried from plan-068's pass-1 red-team — these must be settled
before this plan can draft its digest epic:**

- **C2 — the journal keeps only the LAST step's detail.** `LandingJournal.write` builds
  `rec["detail"] = detail` with **no merge against `prior.get("detail")`**, while `history`
  accumulates (verified directly in the source). So L4's `merged_tree` is destroyed by L5's write.
  Forwarding detail is **necessary and not sufficient**; this needs a per-phase accumulation and a
  `yf-plan/landing-journal@1 → @2` schema bump with a back-compat rule for an in-flight `@1`
  journal. The `detail` field is currently **written but never read**, so this plan adds its first
  reader and inherits an untested field.
- **C3 — projecting a boolean introduces a NEW silent accept.** The two L2 facts are booleans
  whose post-mutation value is *absorbing*. If the operator leaves unrelated uncommitted work
  during the L3 halt, re-derived `true` matches projected `true`, the digest greens, and L4's
  `git commit --no-edit` sweeps foreign dirt into the merge commit and pushes it. Today that
  resume is a guaranteed **loud** mismatch. Project **content** (dirty path set or a working-tree
  hash), or leave those two covered and accept the halt as the honest signal.
- **C3b — `merge_preview.predicted_tree` staying covered and unprojected is load-bearing** (it is
  the only detector for foreign landings post-L4) and is written down nowhere. State it as an
  invariant in the requirement.
- **C4 — "fail closed" needs a stated predicate**, not a wish: keyed on `history`/`phase`, with a
  named halt class and exit code, and handling the case where a detail is *legitimately* absent
  at resume points before the mutating step. Build on `LandingJournal.read`'s existing
  `{"phase": None, "corrupt": True}` return.
- **C5 — the projection mechanism needs its own REQ, AND the two amendments it assumed are not done.**
  **Correction (plan-068 pass-3 C6):** an earlier draft of this line stated that plan-068's SPEC work
  "adds a documentation column to REQ-LAND-036 and fixes REQ-LAND-018's rationale". **That was
  false.** plan-068's Epic 0 allocates `REQ-LAND-037`/`-038` and amends `REQ-LAND-002`/`-004` and
  `REQ-BRANCH-001`/`-002`/`-004` — **neither `REQ-LAND-036` nor `REQ-LAND-018` is touched by it.**
  So this plan owns all three: the **`REQ-LAND-036`** exclusion-table amendment (a column naming
  *which step* mutates each excluded fact — L2 / L4 / L15 / L18), the **`REQ-LAND-018`** rationale
  amendment (`predicted_tree`, **not** the target tip, is the detection-bearing field), **and** a new
  requirement authorizing the projection mechanism itself with its fail-closed rule.
- **C8 — a coverage gate must handle subprocess coverage** (`COVERAGE_PROCESS_START` +
  `--parallel-mode`) or it will report the new preamble tests as uncovered.
- **Declared scope boundary:** `--validate-decision`'s CLI branch is entirely uncovered and is the
  middle of the three landing modes. Either cover it or declare it out of scope explicitly.

## Approach
_To be determined after scoping and investigation._

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |

## Success Criteria

> **DECLARED ABSENCE — this plan is at `status: scoping` and its Success Criteria are not yet
> written.** The table below is deliberately empty, and saying so is the point: a zero-row table
> satisfies every column and id check while asserting nothing, so `doc_lint`'s
> `criteria-cells-filled` treats an undeclared empty table as a finding. It is the only bundle in
> the corpus that fires it (measured 2026-09-09), and because `_shared/test_doc_lint.py` asserts a
> corpus-wide blast radius of **0** for that check, the undeclared form was a **red in both the
> FAST and the FULL tier** — and therefore a guaranteed **L3 halt with the lock held** for any
> plan landing after it. Recorded by plan-068 as `findings/exec-001-inherited-doclint-red.md` and
> declared here at its Issue 3.3.
>
> The criteria are written when this plan reaches `drafting`, after the design questions carried
> from plan-068's pass-1 red-team (C2, C3, C3b, C4, C5, C8) are settled — writing them sooner
> would state criteria for a design that does not exist.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |

---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #198: yf-plan Phase 3: give the review loop a bead representation — dispatch→record ordering, and why the loop cannot live in the formula

- **Number:** 198
- **Title:** yf-plan Phase 3: give the review loop a bead representation — dispatch→record ordering, and why the loop cannot live in the formula
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Split out of **plan-051** by operator decision: the content was drafted after that plan's approving red-team pass, so rather than ship it unreviewed it goes here with its measurements intact.

## Two separable things

### 1. The `dispatch → record` ordering edge

Phase 3 is the only yf-plan phase with no bead representation (Phase 2 is a wisp, Phase 5 a pour). A `plan-review` wisp — scoped to **sequencing only**, arms sequential — would let the red-team step be **two beads**:

```
dispatch-pass-N  ──blocks──▶  record-pass-N
```

`record-pass-N` never enters `bd ready` until `dispatch-pass-N` closes, and `dispatch` cannot close until the agent returns. plan-051's EXP-005 measured exactly this behaviour: a poured wisp held its `join` step absent from the ready set until every arm closed, then it appeared.

**The honest limit, stated up front:** this binds the *tracked* workflow, not prose. A bead cannot stop a session from *claiming* it dispatched something. What it buys is that "what is next" comes from `bd ready` rather than from an actor's memory of what it intended.

**The motivating observation is real and was measured in-session, twice.** During plan-051's review loop the operator twice caught the assistant writing "dispatching pass N" as a closing line without having made the call — the sentence described an intention, not an action. Both times the commit that preceded it was real and verified; only the dispatch was missing. That is the same shape as the defect class plan-051 exists to close: an assertion that something ran, with nothing behind it.

### 2. Why the loop cannot live in the formula (measured, bd 1.1.2)

Recorded so a later reader does not rediscover it:

- **No `loop` / `repeat` / `while` / `iterate` primitive** anywhere in `bd`.
- **`until` is not it** — it is a cross-project *capability* dep ("blocks until shipped in the target project"), and EXP-005 measured that it does **not** gate readiness. Neither does `validates` or `tracks`. Only `blocks` does.
- **No gate type re-runs a shell command.** Gate types are `human | timer | gh:run | gh:pr`. yf-plan's capability gates carry a `test:` in *metadata* that the coordinator executes — a yf-plan convention layered over bd, not a bd feature.
- **`bd dep add` runs cycle checks**, so a cycle is **unrepresentable by construction**.

**But both shipped formulas are already skeletons** — `plan-investigate` and `plan-execute` declare almost nothing and inject their steps at runtime, with comments saying so. So the loop is *unrolled by re-pouring per cycle*, not iterated inside the formula. **The formula holds exactly one iteration; the coordinator owns the loop.** If a `plan-review.formula.toml` ships, that should be stated in its own comments.

## Hard constraint that travels with this

**The review-cycle counter must stay in FILES.** It is `len(glob('reviews/pass-*.md'))`, deliberately monotonic (REQ-PLAN-030; REQ-PORT-006's count-equality against `log.md`'s `review-pass:` bullets). A wisp is **ephemeral and burnable**, so a counter inside one is **resettable by `bd mol burn`** — reintroducing precisely the unbounded self-resolving loop plan-050's D-8 forbids. Any wisp orchestrates dispatch; the file remains the ledger.

Related, and independently worth fixing: **`bd mol burn` exits 0 on "Canceled"**. Measured on a wisp with an open APPROVE gate — it prompts, and a scripted caller that ignores stdin gets a silent no-op with a success exit code. `--dry-run` lists the open gate with no warning. Any scripted burn needs `--force` and must check output, not the exit code.

## Not in scope here

Parallel review lenses. plan-051's EXP-005 tested the claim and found **no evidence**: the cited 5→4→11→17→14 concerns-per-pass series measures **independence**, not parallelism — all 29 review passes across four plans were sequential, one reviewer each. And fan-out would break the **chain property** in which each pass verifies the previous pass's resolutions, which is where most of plan-050's yield came from (8 of its 13 passes found a defect injected by the previous pass's fix).

## Provenance

- `docs/plans/plan-051-james-dixson-2f499f/findings/exp-005-review-wisp.md` — the spike, the readiness-frontier table, the dep-type measurements, the burn semantics.
- `docs/plans/plan-051-james-dixson-2f499f/plan.md` — D-7 (sequencing only) and the Non-goals section (counter stays in files).

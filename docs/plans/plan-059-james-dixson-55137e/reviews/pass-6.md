---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 6 — plan-059-james-dixson-55137e

## Verdict: REVISE

**Run under an explicit convergence standard** (operator-set): APPROVE unless a defect falls in one
of five blocking classes — wrong behaviour, data loss, an unpassable gate, an unclosable plan, or a
misleading instruction to an executor. Everything else goes in Strengths or Missing without changing
the verdict.

**The design is APPROVED in substance.** The architecture, the detector refusal, the
`escalations.md`-vs-retrospective decision, the scoping and the DAG are sound and were not
re-litigated. **Three defects remain, all blocking class 3, all one line, and all the same root
cause:** `set -o pipefail` wrapped around a command whose **success exit is non-zero**.

## Pass-5 resolutions — verified by execution

- **B1 resolved.** Zero `<token>` in any clause-form criterion; `assets/filed-issues.env` sourcing
  used for exactly the three unknown issue numbers.
- **B1's corrected consequence HOLDS — the plan CAN close.** Controls re-run: `plan-052`
  (`status: complete`) -> FAIL **rc=1**; `plan-050` -> INCONCLUSIVE **rc=2**; `plan-059` -> FAIL rc=1
  with 17 correctly-FALSE progress criteria. *"A completion-time verb returning FAIL at drafting is
  the norm, not a wedge. **Blocking class 4 does not stand.** The main session's reasoning is
  correct."*
- **B3 resolved** — Issue 0.3 exists and depends on the terminal issue of every epic.
- **B4 resolved** — Issue 1.1 names the marker verbatim; gate 1's grep matches it.
- **N1 resolved** — the `SUPERSEDED` banner is on `exp-001` above the table.
- **N9 resolved** — `okf.py check` -> `ok: true`, zero findings.
- **DAG verified** — 36 issues, 42 edges, 5 gates, single root `0.1`, no cycles, no dangling targets.
- **The corpus comparison re-derived and it HOLDS** — 116 clause-form rows across
  plan-050/052/054/055, **2 carrying a `<token>` (1.7%)**, one of them plan-050's `SC6`
  (`--path <an empty selected file>`). *"The ~40x framing is honest; the earlier 'zero' was not."*

## Blocking concerns

| # | Concern | Class | Severity |
| :-- | :-- | :-- | :-- |
| G1 | **Gate 2 is still permanently red on a correct implementation.** Its positive control is a pipeline under `pipefail`, and `doc_lint` **exits 1 whenever an `E` finding is present** — which is exactly what the step demands (Issue 2.2 declares the checks `E` with `promote = false` so `recommended-in-alternatives` *can* fail). Measured: `jq` printed `true` and **the chain returned 1**, aborting before `escalation-raise` ran. Gate 2 `Blocks: epic:3`. | 3 | high |
| G2 | **SC4 can never be true.** It pipes `review-loop-check` into `jq` under `pipefail` and declares `-> exit 0`, but that verb returns **rc=3** by contract on the escalating path — which Issue 3.1 explicitly *preserves*. The payload is only emitted on that path, so choosing a non-escalating bundle is not an escape. | 3 | high |
| G3 | **SC0 and SC0a are jointly unsatisfiable.** SC0a requires an `RC gate-consistency` row; SC0 forbids any non-zero row. Measured: `gate_consistency.py` -> **FAIL, rc=1**, five arm-1 findings, and **no issue removes them**. All five are name-based: gate 1 naming Issue 1.3 in prose while blocking it, and the upstream gate enumerating 2.7/6.3/6.4/0.2 in its Instructions. | 3 | high |

## Non-blocking

| # | Concern | Class |
| :-- | :-- | :-- |
| N1 | SC1's fixture is exposed to the same family — any *other* `E` finding in it turns SC1 red for an unrelated reason. The executor controls the fixture and will see it. | NONE |
| N2 | SC3/SC5/SC2b/SC10 read this bundle's own `escalations.md`, which no issue explicitly creates. Satisfiable (ids are append-only, so the first raise *is* `ESC-001`) but implied rather than stated. `.pushes == 1` is a brittle literal. | NONE |
| N3 | `exp-001` carries residual `5/6` figures outside the banner's table scope. | NONE |
| N4 | `index.md` still says "17 of 18"; Issue 0.1 rewrites the sweep, so this self-corrects at intake. | NONE |

## Missing

> Nothing in the design layer. **The gap is that no pass has executed a gate `Test:` as a WHOLE
> CHAIN.** Issue 0.1 records per-instrument exit codes — which is what caught pass 5's blockers — but
> G1 and G2 live in the **composition** of a chain, not in any single instrument.

## Gate Assessment

Gate 1 **reachable and verified** (B4 fixed). Gate 2 **not reachable** — *"structurally the best gate
in the bundle; the defect is one `|` that should be a `>`."* Upstream and Reconcile gates fine.

## Upstream Assessment

Unchanged from pass 5 and still sound. *"No supersedes claimed that isn't earned."* #273's
`resolves-upstream` tag now present.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| G1 gate 2 chain aborts on expected exit 1 | high | Accepted. The positive control is **redirected to a file and read by a separate `jq`, off the `&&` chain**. Verified by execution: the redirect form reaches step 2 and returns **0**; the old piped form returns **1** despite `jq` printing `true`. | `main-session` | `resolved` |
| G2 SC4 asserts exit 0 from an exit-3 verb | high | Accepted. Redirect form, no `pipefail`. Verified: redirect **rc=0**, old piped form **rc=3**. | `main-session` | `resolved` |
| G3 SC0/SC0a jointly unsatisfiable | high | Accepted. Three prose deletions — the upstream gate's Instructions now say *"see this gate's `Blocks` set"*, and gate 1's Condition and Instructions no longer name a blocked issue. **Verified: `gate_consistency.py` -> `PASS: 5 gate(s) consistent`, rc=0.** | `main-session` | `resolved` |
| N1 fixture must be schema-clean | NONE | Adopted anyway — Issue 1.6 now says so explicitly. | `main-session` | `resolved` |
| N2 own escalation implied | NONE | Adopted anyway — Issue 2.5 now says to raise this plan's own `ESC-001` into its bundle. | `main-session` | `resolved` |
| N3 residual `5/6` in exp-001 prose | NONE | Adopted — each annotated in place as superseded. | `main-session` | `resolved` |
| N4 stale index sweep count | NONE | Left — Issue 0.1 rewrites the artifact at intake, as the reviewer notes. | `main-session` | `resolved` |
| Missing: chains never executed whole | — | **Adopted as the structural fix.** Issue 0.1 now requires each gate `Test:` be run as a single `bash -c` string with its **composite** exit code recorded — the method that found G1 and G2. | `main-session` | `resolved` |

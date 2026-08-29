---
type: Reference
okf_spec: OKF-PLAN
description: "Draft closing comment for #265 — HARNESS_INCOMPLETE added as a third distinct verdict; the pre-fix behaviour reproduced exactly."
disposition: include
target: "#265"
---
**Fixed and closing.** The report was exact, and the pre-fix behaviour was reproduced on a fixture
before the fix landed.

**Reproduced.** A plan with one green criterion and one unjudged class-A criterion
(`evaluated / class_a = 1 / 2`), run against the pre-fix engine:

```
rc = 0   verdict = PASS   reason = "all 1 evaluated criterion/criteria hold"
```

True as written, and profoundly misleading as read. `evaluated_fraction` was emitted and consumed by
nothing, so the information needed to detect the state was present and unread.

**The fix — `REQ-PLAN-080` amended, and `HARNESS_INCOMPLETE` is a THIRD verdict rather than a reuse
of either neighbour:**

| verdict | claim | exit |
| :-- | :-- | --: |
| `FAIL` | a criterion was judged and is **false** | 1 |
| `HARNESS_INCOMPLETE` | a criterion the plan **declares judgeable** was **not judged** | 1 |
| `INCONCLUSIVE` | **nothing** was judgeable | 2 |

Collapsing the middle into either neighbour is the same two-facts-one-signal conflation you tracked
under `#263` — and the same shape as `doc_lint`'s `not-selected`/`no-such-path` (`#181`),
`resume-scan`'s `found` (`#207`), and `reindex`'s `no-index`/`no-such-path` (fixed in this same
plan).

**Scope is narrow by construction.** Blocking applies **only at the completion binding**
(`YF_RECHECK_DEPTH = 0`); a nested run reports and never halts, because a criterion's own command
routes through the plan's harness one level down. `--advisory` and `--require-evaluated <fraction>`
are explicit overrides, so a lower bar is reached by *declaration* rather than by accident.
`INCONCLUSIVE` keeps its `warn` mapping and exit 2 **unchanged** — a wholly unmigrated plan can never
reach `HARNESS_INCOMPLETE`, so this is not an outage for the 46 bundles that carry no clause-form
criterion.

`harness_incomplete` and `unjudged` are emitted on **every** path, including `PASS` — a field emitted
only on the failing path cannot detect the condition *before* it becomes one, which is how
`evaluated_fraction` came to be consumed by nothing.

Ships `skills/yf-plan/scripts/test_recheck_criteria.py` (7 tests), wired into
`CHANGE-VALIDATION.md` so it re-runs on every land.

**One honest caveat.** `recheck-criteria` runs from the **installed** skill directory and installing
mid-execution is forbidden, so this fix is **inert for plan-056's own close**. That window was
covered instead by a capability gate whose `Test:` halts on an exit code outside the verdict
arithmetic entirely. The successor plan inherits the fixed engine.

Plan: `docs/plans/plan-056-james-dixson-473dba/`

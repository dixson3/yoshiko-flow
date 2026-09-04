---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 5 on plan-062, after the operator narrowed scope to seam + resume. Verdict REVISE with 10 concerns (C47-C56), two high. Confirmed the narrowing was mechanically clean — zero dangling references to cut issues, all 24 issues covered, every checker green. HEADLINE: SC14/SC14b were VACUOUS, passing before anything was poured, because the pass-4 C38 fix traded a false-fail for a permanent-true — the fourth time in five rounds that a vacuity fix created a new vacuity.'
---
# Red-Team Pass 5 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

## Strengths

**The narrowing was clean.** `plan_extract --strict`: 24 issues, 26 edges, 5 gates, 24 criteria,
10 risks, 4 upstream rows, `unparsed: []`, `recovered: []`. Zero dangling `depends-on`, zero
cycles (full DFS), zero `Discharged-by` naming a non-existent issue, and **all 24 issues named by
at least one criterion** — the two failure modes every prior wholesale edit produced did **not**
recur. A sweep for every cut id (`0.2`, `0.3`, `3.1-3.5`, `4.5`, `4.6`, `SC6-SC8b`, `R3`, `R4`,
`REQ-LAND-027`) found nothing dangling; the only `Epic 3` hits refer to **plan-060's** Epic 3,
correctly.

Every checker green: `gate_consistency` PASS (5 gates, 0 findings), `audit` `pass` /
`okf_native: true`, `okf.py reindex --check` clean, `check_frontmatter` 43 files clean,
`doc_lint` PASS on all 16 bundle files.

**Every Verification clause runnable**, 15 FALSE pre-work, 0 inconclusive, 0 exit-126/127, 0
timeouts. SC13's escaped pipes round-trip intact — the C24 regression did not return. SC13's
change to `REQ-LAND-02[89]` / `-eq 2` is **correct** given 0.3 was cut. Gate count still 3, so
"all three" is the right number — the C28 off-by-one did not recur. Gate 2's inversion verified
live across all three states.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C47 | high | **SC14 and SC14b are VACUOUS — they pass right now, before anything is poured.** `bd list --all --type gate` is repo-wide: 194 historical gate beads, **59** lines containing `test_class`. Both exit 0 today and can never be false, whatever Issue 0.0 does. `recheck-criteria` reports `holds` against an unpoured plan. **The pass-4 C38 fix created this** — adding `--all` traded a false-fail for a permanent-true. R9's mitigation names these clauses, so R9 is currently unmitigated. | Scope to this plan's three gates, or make it manual with the measurement recorded. |
| C48 | high | **The Objective still promises the cut work** — "fix the L7 frontmatter collision on the same path". Contradicts the Approach and the `deferred` row, in the paragraph a cold reader reads first. | Strike the clause. |
| C49 | medium-high | **`upstream-triage.md` was not narrowed** — the #326 block still reads `include` with notes citing Epic 3. Nothing catches it: `doc_lint` R3 and `verify-reconcile` both read `plan.md`'s table only. A cold reader gets two authoritative answers. | Rewrite the block to `deferred`. |
| C50 | medium | **SC17c undercounts and 5.1c's reason is wrong.** `_land_upstream_rows` (`:7941-7947`) filters on `exclude` only, so #326 also gets a `draft_body_path` — non-exclude rows = **4**, not 3. Three is defensible (`deferred` sets `requires_mention: False`) but the plan gives the wrong reason. `-ge` is also a floor satisfied by three files named anything. | Reword to "rows requiring a mention"; use `-eq 3`. |
| C51 | medium | **Issue 0.7's prose and its `depends-on` disagree, and in-place mode makes it matter.** The text says "immediately after the in-place fallback" but the edge placed it 7th — so 0.1/0.4/0.5/0.6 would edit `SPEC.md` while the primary is still on `main`, and in-place mode has one address space. Anything committed before 0.7 cuts the branch sits on `main` and is **not** in the merge L3 validates. | Re-wire: `0.7 depends-on 0.0`, `0.1 depends-on 0.7`. |
| C52 | low-medium | **Gate 3 is a frontloading miss** after moving off the cut 4.5. Its evidence is 4.1, so its floor is 4.2; it now blocks 5.4, behind the multi-minute FULL tier. 4.1 is not even a transitive predecessor of 5.4, so nothing orders the evidence before the gate. | Move `Blocks` to 4.2. |
| C53 | low-medium | **No `gate-plan062-*` row in `CHANGE-VALIDATION.md`.** plan-060 mapped `SPEC.md` (`:253`) and `skills/yf-plan/spec/**` (`:254`) to its own row; this plan edits both, so those triggers fire and report on **plan-060**. SC13c is run once by 0.6 and by nothing thereafter. | Widen Issue 5.2 to register the row. |
| C54 | low | **`REQ-LAND-027` is left permanently unallocated with no explanation in plan.md.** The reservation is real (`findings/exp-003:93`) but a plan.md-only reader sees a hole where cut Issue 0.3 was. | One clause in 0.4. |
| C55 | low | **±1 drift in four `plan_manager.py` citations**: the gate call is `:8298` (plan said 8296), the stub `:8305-8310` (said 8306-8311), the stale remediation `:8308-8309` (said 8309-8310), the step loop `:9561` (said 9560). Everything else exact. | Nudge, or drop the numbers where a quoted string already identifies the site. |
| C56 | low | `plan_extract` harvests a bogus `REQ-LAND-02` into `reqs` from SC13's regex. `reqs` has **no consumer**, so cosmetic. | No change; recorded. |

## Missing

Nothing dangles at a cut id. The numbering holes (issues 0.2/0.3/3.x/4.5/4.6, risks R3/R4) preserve
stable ids rather than renumbering — consistent across both tables, with no surviving citation.
`index.md` correctly re-describes `findings/exp-003` as deferred-but-retained. The Approach still
describes what the epics do, with C48 the single exception. No risk is orphaned; the one gap is
R9's mitigation being **unsound** (C47) rather than absent.

## Gate Assessment

| Gate | Blocks | Reachable? | Notes |
| :-- | :-- | :-- | :-- |
| Start Gate | — | n/a | mandatory human |
| in-place | 1.1 | yes | independent config read, satisfiable before any issue; correctly cross-links 0.7 |
| seam DISCRIMINATING | 2.1 | yes | evidence is 2.0, a `depends-on` predecessor and not in `Blocks`; inversion verified live |
| resume | 5.4 → **4.2** | yes | no cycle; was late (C52) |
| Reconcile | reconcile step | n/a | standard |

All three capability gates carry `test_class`/`cwd` lines that `plan_extract` drops — the #266 gap
the blockquote documents and Issue 0.0 works around. **The workaround is sound; its verification
was not** (C47).

## Upstream Assessment

Four rows, all parsing, `doc_lint` R3 clean. #327 `include` → 1.1, 2.1, 4.1, covered by
SC1/SC2/SC3/SC4. #326 `deferred` — the change is right and plan.md is honest about the cut, but
the triage file still said `include` (C49) and the mechanical consequence was missed (C50). #266
and #304 `partial` — both accurate, both requiring a mention, both covered by 5.1c.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C47 | high | Confirmed independently: 59 `test_class` lines repo-wide, SC14 exits **0** pre-pour. SC14 and SC14b **merged into one `manual:` criterion**, with the measurement recorded and the explicit note that this REVERSES pass-2 C20's argument for a clause — recorded rather than done silently. Issue 0.0 records the three gate ids and their read-back. | `main-session` | `resolved` |
| C48 | high | Objective struck and marked "Narrowed at pass 4". | `main-session` | `resolved` |
| C49 | medium-high | `upstream-triage.md`'s #326 block rewritten to `deferred` with the pass-4 decision, a pointer to `findings/exp-003`, and the `requires_mention: False` consequence. | `main-session` | `resolved` |
| C50 | medium | SC17c reworded to "rows REQUIRING A MENTION" with `-eq 3`; Issue 5.1c now names all three files and states the correct reason (`deferred` sets `requires_mention: False`, though `_land_upstream_rows` still computes a path). | `main-session` | `resolved` |
| C51 | medium | Re-wired: `0.7 depends-on 0.0`, `0.1 depends-on 0.7`. Verified in the extracted DAG. Both issues now carry the single-address-space reasoning inline. | `main-session` | `resolved` |
| C52 | low-medium | Gate 3 `Blocks` moved to **4.2**, its floor. | `main-session` | `resolved` |
| C53 | low-medium | Issue 5.2 widened to register `gate-plan062-amendment` and its Trigger Scope entry, with the plan-060 precedent cited. | `main-session` | `resolved` |
| C54 | low | Issue 0.4 now states 027 is reserved by `findings/exp-003` for the deferred fix. | `main-session` | `resolved` |
| C55 | low | **PARTIALLY REJECTED — the concern was itself wrong on two of four, and I applied it uncritically before checking.** Re-measured against the file: `:8298` (gate call) and `:9561` (step loop) were correct and are adopted. But `:8305` is `sys.exit(3)`, not the stub — the stub really is **`:8306-8311`**, and the stale remediation really is **`:8309-8310`**; my original numbers were right and C55's 'corrections' were off by one in the other direction. Both reverted. Issue 2.3 additionally identifies its site by quoted string, which is robust to drift either way. Recorded because taking a reviewer's measurement on faith is the same failure as taking my own on faith. | `main-session` | `resolved` |
| C56 | low | No change — recorded as cosmetic, `reqs` has no consumer. | `main-session` | `resolved` |

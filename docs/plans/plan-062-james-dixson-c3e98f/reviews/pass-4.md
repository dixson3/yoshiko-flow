---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 4 on plan-062. Verdict REVISE with 10 concerns (C37-C46), two high. HEADLINE: the mandated in-place mode makes `land` structurally unable to run — no execute branch is ever created, and land --dry-run halts execute-branch-missing — so the plan mandates a mode that forbids its own terminal deliverable. Also: SC14/SC14b query bd without --all and are guaranteed FALSE at the L11 recheck, halting past the irreversible boundary; and Issue 5.5 reads as instructing the executing agent to run land --apply itself, which SKILL.md 6.0 forbids by name.'
---
# Red-Team Pass 4 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

## Strengths

DAG re-extracted rather than trusted: **31 issues, 27 criteria, `unparsed: []`, zero cycles, zero
dangling `depends-on`, zero criteria naming a non-existent issue, zero issues named by no
criterion.** The pass-3 additions (`5.1b`, `SC14b`, `SC17b`) are correctly wired; Gate 1's widened
`Blocks: 1.1, 3.1` parses as two refs and orphans nothing.

**Every repo checker green:** `gate_consistency` PASS (5 gates, 0 findings), `doc_lint` PASS (0 E,
0 W), `check_frontmatter` 43 files clean, index drift clean (67 bundles), `audit` exit 0.

**All 24 clause criteria parse as `kind=clause`** (3 manual, 0 prose), and **20 of 24 are
correctly FALSE** against the shipped build. All three gate tests are runnable and behave as
documented — Gate 1 verified 1 → 0 in a sandbox with the config written. Every pass-3 resolution
independently re-measured and confirmed real.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C37 | high | **The mandated in-place mode makes `land` structurally unable to run, so Issue 5.5 and SC17 — the terminal deliverable — are unreachable.** Measured: `land --dry-run` returns `halts: [{code: "execute-branch-missing", detail: "…does not exist — nothing to land", resolvable_by_agent: false}]`. `_worktree_ensure` (`:4269`) returns `viable: false, reason: opted-out` **before** any branch creation, and the execute branch is created only by `git worktree add -b` — so under `execute.worktree: false` **no execute branch ever exists**. `_land_manifest:8003` checks for it with no in-place carve-out, and §6.1 is titled "Merge-back (**worktree mode**)". The plan mandates in-place in Approach, R8 and Gate 1, then requires landing through `land --apply`. **Mutually exclusive.** | Add an issue creating the execute branch in the primary checkout from the pinned base immediately after the in-place fallback, plus a criterion asserting it exists. This also *satisfies* the premise — the primary is then on the branch carrying the fix. File the in-place↔`land` incompatibility upstream; it is a real `land` defect. |
| C38 | high | **SC14 and SC14b are guaranteed FALSE at `recheck-criteria`, halting the landing at L11 past the irreversible boundary.** Both run `bd list --type gate` with **no `--all`**. Measured: with metadata set, `grep -c test_class` = 1; after `bd gate resolve` it returns **0**, while `--all` still returns 1 — resolve *closes* the gate. All three capability gates must be resolved before completion, so by L5/L11 the query returns `[]`. `LAND_CLOSE_CHAIN` marks `recheck-criteria` **halting** (`:9100`). The repo's own gate query at `:6623` uses `--all`; the plan's was copied from §5.2c where open-only is correct *at the sweep* and wrong at recheck. **SC14b inherited the bug by copying SC14's shape** — the pass-3 pattern again. | Add `--all` to both. |
| C39 | medium-high | **SC17b is vacuous today and a corpus-wide halting clause tomorrow — the exact hazard C32 converted SC15 to `manual` to avoid, reintroduced in the same pass.** Measured: the check exits **0** now, so SC17b holds before Issue 5.1b does anything. It is scoped to all 67 bundles, so drift in an unrelated bundle halts *this* plan at L11. Measured further: `assets/upstream-grant.md` and `records/*.md` are **not** auto-indexed, and `upstream-grant.md` is a documented landing recovery artifact. | Scope to this bundle via `okf.py reindex --check <plan_dir>`, and move 5.1b to the **end** of Epic 5 so it runs after every Phase-5 bundle write. |
| C40 | medium-high | **Issue 5.5 is a Phase-5 execution bead describing Phase-6 work, and its body reads as instructing the agent to run `land --apply` itself.** §5.5: the Reconcile Gate auto-resolves when all execution beads close, then "Proceed to Phase 6" — where `land` lives. So 5.5 must **close before** the landing it describes can start. And §6.0 says "**Do NOT run `land --apply` yourself** … PRINT THE COMMAND AND STOP", naming `#293`. SC17 says "the operator ran `land --apply`"; Issue 5.5 never says who, and instructs "re-invoke `land --apply`" on a halt. | Reword 5.5 to the artifact a Phase-5 bead can produce: record the §6.0 route and the halt-recovery contract for the operator to execute at Phase 6. Say **operator** explicitly. |
| C41 | medium | **No issue authors `assets/upstream-drafts/<issue>.md`, and the directory is undocumented** — `grep -rn upstream-drafts skills/yf-plan/ --include='*.md'` → **zero hits**; it exists only at `plan_manager.py:7936`. `assets/` is empty, so all four Upstream rows land with `draft_present: false`. **Epic 3 exists entirely to fix how L7 posts those bodies, and the plan's own landing exercises the fixed path with no input.** After Issue 3.4 the missing-`body_path` case stops being a silent drop and becomes a **halt at L7, past the L6 push**. | Add an Epic-5 issue authoring `327.md` and `326.md` (at minimum) with a criterion asserting they exist; note them as new index members. File the undocumented-directory gap upstream. |
| C42 | medium | **SC16 does not measure what it claims — measured, not reasoned.** In a sandbox with the stub in the primary and the fix in a worktree, SC16 run from the worktree gave `exit 1` (criterion HOLDS) while the primary still contained the stub. `git rev-parse --show-toplevel` resolves to the **worktree** root. The one criterion written to make the primary-checkout precondition observable is blind to the exact failure it names. | Resolve the primary explicitly via `--git-common-dir`. |
| C43 | low | **Issue 3.4's premise is broader than the code.** At `:9077` L7 already returns `halting=True` on the first read-back failure, so `failed` can only accumulate from the `body_path … missing` `continue`. The fix is right; the motivation over-states, risking SC8 targeting an unreachable path. | Narrow 3.4 and EXP-003's headline to the missing-draft-body case, and construct SC8's test for it specifically. |
| C44 | low | **`context.md:74` is contradicted** — it says Issue **5.4** lands the plan; 5.5 does. | One word. |
| C45 | low | **The review passes violate the closed Severity vocabulary** — 18 `[R] cell-vocabulary` warnings across pass-1/2/3 (`med`, `med-high`, `low-med`). Off-vocabulary tokens erase the signal the severity pin exists to preserve. | Normalize to `medium` / `medium-high` / `low-medium`. |
| C46 | low | **Gate 3 sits one issue later than its floor and omits the sweep-red note Gate 2 carries.** Its evidence is 4.1, so its floor is **4.2**, not 4.5. Measured: the test exits 5 today, so the sweep reports it red with no guidance. | Optional hoist to 4.2; add the expected-red sentence. |

## Missing

- **No criterion asserts the execute branch exists** — C37's whole failure class is invisible to all 27 criteria.
- **No criterion asserts `assets/upstream-drafts/*.md` exist** (C41), though Epic 3 is 5 of 31 issues and exists solely to change how they are posted.
- **The `recheck-criteria`-at-L11 blast radius is never enumerated.** Pass 3 identified it for SC15 and then wrote two more criteria exposed to it. A short Approach paragraph listing which criteria are re-evaluated at L11, and confirming each can still be true after all gates are closed, would have caught C38 and C39 mechanically.

## Gate Assessment

| Gate | Reachable? | Discriminating? |
| :-- | :-- | :-- |
| Start Gate | yes | n/a |
| Cap 1 — in-place | condition satisfiable; remediation honestly documented as a restart | yes, verified 1→0 in sandbox. **But satisfying it is what triggers C37.** |
| Cap 2 — seam | yes; evidence from 2.0, blocks 2.1 | yes — `test $? -eq 1` separates pytest-5 from pytest-1 |
| Cap 3 — resume | yes; evidence from 4.1, a transitive predecessor of 4.5 | yes once 4.1 lands; minor frontloading miss (C46) |
| Reconcile Gate | yes | see C40 — 5.5 must close *through* it before the work it names can occur |

`gate_consistency.py`: `PASS, gates: 5, findings: []` — the pass-3 wording repairs held.

## Upstream Assessment

Dispositions are sound and better-reasoned than most in the corpus. #327 and #326 trace to real
issues; both `partial` rows (#266, #304) state what is *not* fixed and why. All four references
present and indexed. Two mechanical gaps: the `partial` rows have no draft bodies either (C41),
and **SC18's `manual:` reasoning — an outward-facing write cannot be self-certified — should be
applied to SC17b as well** (C39).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C37 | high | Confirmed independently: `land --dry-run` halts `execute-branch-missing`, `resolvable_by_agent: false`. New **Issue 0.7** creates and checks out the execute branch in the PRIMARY checkout from the pinned base, with **SC0b** (`git rev-parse --verify --quiet …` → exit 0, re-measured exit 1 today). This satisfies both constraints at once. The in-place↔`land` incompatibility is added to Issue 5.1's upstream filings as a real `land` defect. **My own C4/C16 fix created this contradiction** — mandating in-place mode without checking whether `land` supports it. | `main-session` | `resolved` |
| C38 | high | Confirmed devastatingly: `bd list --type gate` → **0**, `bd list --all --type gate` → **59**. `--all` added to both SC14 and SC14b; re-measured SC14 now exits 0. SC14b inherited the bug purely by copying SC14's shape — the third instance of a fix propagating its own defect. | `main-session` | `resolved` |
| C39 | medium-high | SC17b rescoped from the 67-bundle corpus check to **this bundle** (`okf.py reindex --check <plan_dir>`), and Issue 5.1b moved to the END of Epic 5 (`depends-on: 5.4, 5.1c`) so it runs after every Phase-5 bundle write. Re-measured: exit 1 while `pass-4.md` was unindexed, exit 0 after — so it now discriminates rather than being vacuously green. | `main-session` | `resolved` |
| C40 | medium-high | Issue 5.5 rewritten. It now produces the **handoff artifact** a Phase-5 bead can produce and explicitly states the executing session must NOT run `land --apply` — SKILL.md §6.0 says print the command and stop, and names #293. The halt-recovery contract now says the OPERATOR re-invokes. This matches SC17's wording, which already said 'the operator ran'. | `main-session` | `resolved` |
| C41 | medium | New **Issue 5.1c** authors `assets/upstream-drafts/{327,326,266,304}.md`, with **SC17c** asserting at least two exist (re-measured exit 1 today). Without it the plan's own landing would exercise Epic 3's fixed L7 path against no input, and after Issue 3.4 a missing body halts at L7 past the L6 push. | `main-session` | `resolved` |
| C42 | medium | SC16 now resolves the primary via `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`. Verified from the primary: resolves correctly and exits 0 today (stub present, correctly unmet). The old `--show-toplevel` form resolved to the WORKTREE root, making the criterion blind to the exact failure it names. | `main-session` | `resolved` |
| C43 | low | Issue 3.4's premise narrowed to the missing-`body_path` case specifically, with the note that `:9077` already halts on the first read-back failure, and that SC8's test must construct that one case rather than a general dropped write. | `main-session` | `resolved` |
| C44 | low | `context.md:74` corrected — Issue **5.5** routes the landing (operator-run); 5.4 confirms the checkout carries the fix. | `main-session` | `resolved` |
| C45 | low | All four review files normalized to the closed vocabulary. Re-measured: **22 → 0** cell-vocabulary warnings. | `main-session` | `resolved` |
| C46 | low | Gate 3's Instructions now open with EXPECTED RED AT THE §5.2c EXECUTE-START SWEEP and the reason (pytest exits 5 until Epic 4's first issue), matching Gate 2. The hoist to 4.2 was NOT taken — 4.5 is where the L7-partial case first depends on the property, and moving it earlier would gate an issue that does not need it. | `main-session` | `resolved` |

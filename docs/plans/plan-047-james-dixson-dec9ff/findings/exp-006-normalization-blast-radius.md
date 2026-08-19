---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-normalization-blast-radius
---
# EXP-006 — Blast radius of rewriting historical `plan.md` files in place (tests D-2)

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** D-2 is executable but its stated
justification is **inverted**. Recommend amending it. Zero verbs fail; the damage is to
citations, not to code.

## Question

D-2 authorizes normalizing completed plans in place, "like the OKF migrate path." Measure the
fingerprint hazard and every other consequence, by execution.

## Result

### 1. The fingerprint changes — two hashes, measured

`plan_manager.py fingerprint check` on a scratch copy of `plan-045` (`status: complete`):

```
BEFORE  stored == current == 4954ac04…   stale_approved: false
AFTER   (44 lines in ## Epics rewritten `- Issue 0.1:` -> `- **Issue 0.1:**`)
        stored 4954ac04…  current 1a098b59…   stale_approved: TRUE
```

A purely cosmetic edit inside `## Epics` flips the hash. Confirmed by execution, not by reading.

**Control matrix — and the surprise is in the bottom three rows:**

| Mutation | Fingerprint |
| :-- | :-- |
| `status:` frontmatter key · `**Status:**` line · `## Upstream Issues` cell · `log.md` · `reviews/` · `index.md` | **neutral** |
| blank lines inserted in `## Epics` · trailing whitespace in `## Epics` | **neutral** |
| **GFM table cell padding in `## Gates` / `## Risks`** | **CHANGED** |
| **`## Risks & Mitigations` → `## Risks and Mitigations`** | **CHANGED** |
| **new `## Appendix` section appended** | **CHANGED** |

The spec's exclusion list is exactly right, but the normalization is far narrower than
"cosmetic": `_plan_content_fingerprint` (`plan_manager.py:2151-2167`) is literally
`ln.rstrip() for ln in body.splitlines() if ln.strip()` plus a lowercased title prefix. Nothing
else is absorbed.

> **Three transforms that look cosmetic are not hash-neutral: GFM table re-alignment (which is
> exactly what `yf-markdown-format` autofixes), heading renames, and section additions.**

### 2. Downstream consumers — nothing fails, one thing regresses

Every verb executed against pristine and mutated copies. `ready-check`, `audit`,
`verify-reconcile`, `complete-gate`, `audit-close`, `review-loop-check`, `landing-lock`,
`close_cascade.py`, `okf.py check`, and the `yf` Rust binary are all **byte-identical** or
provably fingerprint-free (`grep -rn fingerprint yf/src/` → 0 hits; `close_cascade.py` has 0
hits for `plan.md`).

**The one regression, reproduced in a scratch repo with two `complete` plans:**

```
plan-901-test-aaaaaa  status: complete
plan-902-test-bbbbbb  status: complete  ⚠ STALE-APPROVED (re-review before execute)
```

**This is github issue #109 verbatim — and #109 is CLOSED as not-reproducible.** Its closing
comment invites exactly this:

> "**Residual exposure.** This is **latent, not absent**. The branch becomes reachable if a
> completed plan's *content* is edited after the fact… If that is ever observed in practice,
> this issue is the record of why, and the fix is the one-line status filter originally
> proposed. **Reopening it at that point would be appropriate.**"

D-2's normalizer *is* the predicted event. Executed as-is it tags all 46 completed plans
`⚠ STALE-APPROVED` **forever**. Root cause is a code asymmetry at `plan_manager.py:1223-1228`:
`parked = _is_parked(status, fp_status)` is status-aware; `stale = fp_status.get(...)` is not.

The execute-path gate does **not** rescue this: SKILL.md §5.1 filters execute candidates to
`status == approved`, so a `complete` plan never reaches the §5.2 stale refusal.

### 3. Corpus status and the refusal predicate

46 plan dirs, `Counter({'complete': 46})`. Zero parked, zero already-stale. The 47th dir is
this plan (`investigating`, **no `fingerprint:` key at all**).

`parked: true` cannot coexist with `complete` — `_is_parked` (`:2208-2222`) requires
`status == "approved"` as its first conjunct.

```
normalize IFF  status == "complete"
          AND  stored_fingerprint present AND == current   (not already stale)
          AND  path under a plans root                     (NOT skills/**/fixtures/**)
```

Do **not** write it as `status != "approved"` or `not stale_approved` — both admit
`investigating` (this plan) and `executing`.

### 4. The dominant hazard is citations, not code

**a) Line-number citations — 150 total, 91 resolve into this repo's `docs/plans/`.**
17 distinct plans are cited by line; worst: plan-046 (15), plan-039 (10), plan-043 (10),
plan-040 (9). **≈70 of the 91 live in `docs/research/004-plan-process-defect-mining/`** —
a research bundle whose *entire evidence chain* is line-anchored. Nothing validates these;
`yf-markdown-lint` does not check `file.md:N` anchors, so breakage is **silent**.

**b) Verbatim review quotes — ≥102 across ≥21 of 46 plans.** 822 candidate spans ≥25 chars
scanned across 108 review files; 102 match their sibling `plan.md` verbatim. Top: plan-046 (14),
plan-045 (12), plan-042 (10). This is a **lower bound** (ignores backticked and short spans).
Reviews are the audit trail of what a reviewer actually saw; a quote that no longer matches is
worse than no quote.

**c) OKF coupling — no mechanical dependency, one prose one, and a hard constraint.**
`okf.py check` identical on both copies. But `okf.py:932` enforces **REQ-OKF-010**: a
`**Label:**` line below the first `##` is an **error** — a normalizer introducing
`**Field:**`-shaped lines into a content section breaks conformance. And `index.md` prose
*names* plan.md's sections; plan-045's cites "`plan.md` §Approach" and "the D-1…D-8 table".

> **The "like the OKF migrate path" framing in D-2 is a disanalogy, not an analogy.**
> **REQ-OKF-MIG-003** (`skills/yf-okf/SPEC.md:244`) *requires* migration to keep the fingerprint
> stable; the implementation is annotated `# remove the block (above first ## -> hash-neutral,
> REQ-OKF-MIG-003)` (`okf.py:1173`). OKF migrate was engineered hash-neutral **by
> construction**. D-2's normalization is hash-*changing* by construction. Citing migrate as
> precedent cites the opposite case.

**d) Test-fixture collateral.** 17 further `plan.md` files under
`skills/yf-plan/scripts/fixtures/classify/` are the ground-truth corpus for
`test_classify_deliverable.py`, and the classifier is markup-sensitive — removing inline code
spans from `plan-031` changed its signals from 2 to 4. A normalizer globbing `**/plan.md` would
perturb the suite's `FN == 0` invariant.

**e) The git-blame objection, stated fairly.** 46 files / 15,525 lines / 171 commits touching
`docs/plans/`. One normalizer commit becomes the blame attribution for every rewritten line.
**But blame is recoverable** (`git log -w`, `--ignore-rev`, `.git-blame-ignore-revs`); the 91
citations and 102 quotes are **not recoverable by any git flag**. Rank:
**citations > review quotes > #109 tag > blame.**

### 5. The benefit is smaller than D-2 assumes

- The 9 canonical `##` headings are **already 46/46 uniform**. All heading divergence is in
  *extra* sections (13 spellings of "Scope decisions").
- Issue lines are already **~88% consistent**: 628 bare `- Issue N.N:` vs 85 bolded.

The normalizer has far less to do than assumed — which shrinks the benefit while every cost
above stays fixed.

### 6. Re-stamping is mechanically clean

`fingerprint write` changed exactly 2 lines, both above the first `##` (dual-write per
REQ-DATA-015); `okf check` and `audit` stayed `pass`. **There is no status gate on `fingerprint
write`** — it operated on a `complete` plan without complaint.

## Recommendations

**1. Amend D-2.** Recommended narrower form:
- **Default report-only.** `--write` is opt-in and never the default for `status: complete`.
- **In-place rewrite of completed plans authorized ONLY for hash-neutral transforms** —
  measured to be exactly: trailing-whitespace strip, blank-line collapse, and any edit above the
  first `##` or inside `## Upstream Issues`. Add a **mechanical postcondition**: recompute the
  fingerprint before and after each file and **abort the run if any hash moves**. That is the
  REQ-OKF-MIG-003 discipline applied to the normalizer.
- Hash-changing transforms on completed plans require the consent gate and a separately-approved
  sweep.

**2. Refusal predicate** as in §3; explicitly exclude `skills/**/fixtures/**`.

**3. Do NOT re-stamp — leave fingerprints stale and fix `list` instead.** Re-stamping is clean
but **destroys the approval audit trail**: the stored fingerprint's only job is to prove *this is
the content the operator approved*. Re-stamping asserts approval of text never seen. Instead land
#109's own one-line status filter at `:1224`, mirroring `_is_parked`. SPEC-first (REQ-PORT-041
currently surfaces this unconditioned on status). **Reopen #109**, citing this experiment — its
closing comment explicitly invites that on this trigger.

**4. Citation/quote remediation is a prerequisite, not a follow-up.** Either rewrite the 91
citations to anchor- or quote-based locators, or scope the sweep to exclude the 17 cited plans.
The latter is cheap and safe; the former is the right long-term fix and is adjacent to #135.

**5. One commit for the sweep + `.git-blame-ignore-revs`**, not 46 — matches plan-046's
aggregate-diff gate and neutralizes the blame objection by construction.

**6. Reuse plan-046's gate shape verbatim** — split into `Na` (generate + render aggregate diff,
ungated) and `Nb` (apply + commit, gated), `test_class: consent`,
`Test: (none — no green test can substitute for authorization)`.

## Honest limits

- The 102 verbatim-quote figure is a **lower bound** from a heuristic that ignores backticked and
  short spans.
- plan-046's consent-gate precedent transfers as a *mechanism* but **not as a risk precedent**:
  it swept `index.md` only, measured hash-neutral, and its own D-11 split out new-index creation
  as "a different change with a different consent profile." Rewriting fingerprinted `plan.md`
  bodies is a third, higher profile.

## Reproduction

Isolated worktree + `scratchpad/` only. `docs/plans/` in the main checkout never written.
No `yf … install`, no `bd` writes, no `bd dolt push`.

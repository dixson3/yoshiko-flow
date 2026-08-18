---
type: Review
okf_spec: OKF-PLAN
plan: plan-046-james-dixson-aabefa
pass: 1
verdict: REVISE
created: '2026-08-18'
status: resolved
---

# Red-Team Pass 1 — plan-046-james-dixson-aabefa

## Verdict: REVISE

5 high, 8 medium, 4 low.

## Strengths

- **The findings are unusually good, and the plan actually let them move it.** D-1, D-3, D-4 were revised *against* the approved scope by measurement; exp-003's retargeting is the strongest single act of judgment in the bundle. The Investigation Findings table states the refutations rather than burying them.
- **Epic 1 is correctly first and correctly paranoid.** Issue 1.4 (verify the gate fires and fail-closes) and Issue 1.6 (execute FULL, closing exp-001's own honest limit) are the right answers to plan-045's defect class.
- **Issue 1.3's refusal to restate plan-042's precedent** is verified correct: `pytest <missing>` → exit 4, `-k nomatch` → exit 5.
- **D-2's no-migration ruling is over-determined** (`timestamp` 0, `# Citations` 0).
- **R6 / context.md handle the skill-artifact axis correctly**, including the non-obvious `plan_manager.py`-re-invoked-per-call constraint.

## Concerns

### HIGH

**H1 — D-10 / R5 / D-3 rest on a misreading of the code they cite.** `plan_manager.py:3967` reads `if cf.level != "error" or cf.req not in _OKF_PORT050_REQS: continue` against a **four-item allowlist** (`:3525`), not a fold. Missing `index.md` is emitted under `REQ-OKF-001` (`_shared/okf.py:804`), excluded — the source comment says *deliberately excluded* to avoid double-reporting. So the 128 simulated findings would have been filtered at any level and `audit` would **not** have blocked a single new plan. exp-003 §7 presents this as measured; its Method lists only *reading* the file, and no `audit` run is reported. Load-bearing for the headline retargeting, and itself an instance of the through-line.

**H2 — The "Engine gate green" auto-gate is vacuous; it passes today, before Epic 1 runs.** exp-001 §3 probe C measured the exact Test command at `31 passed, EXIT=0` on the current tree. The Condition has two clauses and the Test verifies only the first. Given the defect this plan exists to fix is *a validation surface that reported green having executed nothing*, shipping a gate of the same shape is the one thing it cannot afford.

**H3 — The "Backfill review" consent gate blocks the issue that produces its own evidence.** It conditions on a diff produced by Issue 4.3 and `Blocks: Issue 4.3`. The exact cycle `red-team.md` names.

**H4 — SC6 is not achievable: 31 of 50 bundles have no root `index.md` at all.** 50 bundles, 19 indexes. Either `reindex --check` silently passes an index-less bundle (making the criterion meaningless), or Epic 4 must create 31 new indexes — unbudgeted and un-consented. exp-003 §7's `PASS=14 FAIL=36` is the same fact from the other side; the plan never reconciles the two numbers.

**H5 — Closing #140 as `include` is not honest, and the plan holds #92 to a standard it exempts #140 from.** #140 asks for nested `index.md`, nested `log.md`, and enforcement below the root. The plan delivers **none**: D-4 drops one, D-9 defers another, Issue 4.5 records rather than executes enforcement. Yet #140 gets a plain `include` while #92 — smaller residue — correctly gets `supersede` with three named carve-outs. The asymmetry is the tell.

### MEDIUM

**M1 — SC7's stated verification method is assigned to no issue.** Issue 4.4 verifies over the corpus — exactly the method SC7 forbids.

**M2 — SC8 is unassigned and would pass vacuously.** A bare `plan_manager.py audit` resolves through `SKILL_DIR` to the **installed** skill with its own vendored `okf.py`, exercising the old engine.

**M3 — Issue 5.2 / SC10 is an unresolved either/or, and one branch reopens closed scope.** Exposing a CLI verb means verb + tests + SPEC + re-vendor across five copies + a CHANGE-VALIDATION row — building the projection D-1 established has no fired demand trigger. Secondary: 5.2 edits `_shared/okf.py` **after** the last re-vendor (3.7), so SC3 would break.

**M4 — Issue 3.2's justification no longer matches the plan, and its "one-line predicate" is undefined.** D-9 defers nested indexes, so nothing here generates one. And `okf.py` has **no notion of bundle-root** — three call sites receive a bare directory. exp-002 §5 labels the predicate *inferred, uncorroborated*; the plan leans on the inferred version and never cites exp-003 §5, which **measured** it.

**M5 — The Motivation restates the very claim Issue 5.6 says must be corrected** ("one known consumer"), while instructing an executor to strike it upstream.

**M6 — Issue 4.1's pre-state arithmetic double-counts and mixes two tools' units.** The 25 ML003 are 24 dead *directory* links + 1 dead file — and that 1 **is** the "1 ghost entry" already counted separately.

**M7 — Issue 4.2 fixes the smaller half of the producer bug.** 24 of 25 violations are the template's unconditional subdirectory entries, not `upstream-triage.md` (8).

**M8 — Issue 2.1 is an unhedged single point of failure for two-thirds of the plan.** Network + `gh` + the existence of a v0.1 commit. Nothing states what happens if v0.1 is unrecoverable.

### LOW

**L1** — `upstream-triage.md` has four blank Disposition fields and `Resolved By` all `TBD`.
**L2** — `index.md`'s summary contradicts plan.md's objective (pre-investigation scope).
**L3** — Issue 2.1 carries no `depends-on` while its epic is gate-blocked.
**L4** — `CHANGE-VALIDATION.md:9-14` still asserts the falsified vacuous-filter claim at its source; Epic 1 edits that file.

## Missing

- No issue verifies `plan_manager.py audit` after Issue 3.6 (SC8) — the plan's sharpest self-referential exposure, uncovered by R6.
- No issue scaffolds a throwaway bundle (SC7's own method).
- No upstream issue for the D-9 nested-index deferral, though two are filed for #92's carve-outs.
- No decision criterion for Issue 5.2's either/or.
- No fallback for Issue 2.1.
- No treatment of the 31 bundles with no root `index.md`, which SC6 counts.

## Gate Assessment

| Gate | Reachable? | Frontloaded? |
| :-- | :-- | :-- |
| Start Gate | yes | yes |
| Engine gate green | **Reachable but vacuous** — not circular (Epic 1 is not in its own Blocks set), but already green on today's tree. The Condition's second clause is the real gate and is untested. | Correctly placed |
| Backfill review | **NO — cycle.** | n/a until broken |
| Reconcile Gate | yes | yes |

## Upstream Assessment

| Issue | Stated | Assessed |
| :-- | :-- | :-- |
| #141 | include → 2.9 | **Sound.** Issue 2.9's `superseded_by:` is correctly a **named exception** rather than a silent violation. |
| #140 | include → 4.5 | **Not honest as written.** Needs `partial` + in/out list + an upstream follow-on for D-9. |
| #92 | supersede → 5.6 | **Well handled — the model #140 should copy.** Caution: #92's bullet says "no confirmed non-Google adopter" while trigger 2 says "**production** adopter", and exp-004 flags "production" as *inferred* — the close comment must correct the bullet without implying the trigger fired. |
| #118 | include → 5.3 | **Sound and correctly widened.** Add the `SKILL.md:245 → :262` citation fix, which 5.3 does not name. |

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 `_OKF_PORT050_REQS` misread | high | **Upheld — independently verified.** `grep` confirmed the four-item frozenset, the `not in` filter, and the source comment stating REQ-OKF-001 is *deliberately excluded*. The "blocks intake" claim is struck from D-3, D-10 and R5; a correction note is appended to exp-003. **The retargeting survives on its other, genuinely measured grounds** (0/423 `description`; 74/142 low-value dirs; root indexes already better). New Issue 3.8 measures the audit behavior by execution rather than by reading. | `main-session` | resolved |
| H2 vacuous engine gate | high | **Upheld.** Gate Test replaced with the FAST-tier invocation asserting a non-empty `commands` array containing `uv-okf` — i.e. the gate now tests what SC1 tests. | `main-session` | resolved |
| H3 backfill gate cycle | high | **Upheld.** Issue 4.3 split into 4.3a (generate + render diff, ungated) and 4.3b (apply + commit, gated). Gate re-pointed at 4.3b. | `main-session` | resolved |
| H4 SC6 unachievable | high | **Upheld — verified** (50 bundles, 19 indexes). SC6 rescoped to the 19; `reindex --check` must return an explicit `n/a` (not `0`) for an index-less bundle, specified in Issue 3.3; the 31 legacy bundles are declared **out of scope** in D-11 with the reason. | `main-session` | resolved |
| H5 #140 disposition dishonest | high | **Upheld.** #140 → **`partial`** with an explicit in/out list in the Upstream Issues table and in Issue 4.5. The D-9 deferral is filed upstream in Issue 5.5, matching the #92 carve-out treatment. | `main-session` | resolved |
| M1 SC7 method unassigned | medium | Scaffold-a-throwaway-bundle step added to Issue 4.2, invoking the **repo** copy explicitly. | `main-session` | resolved |
| M2 SC8 unassigned + vacuous | medium | New Issue 3.8 runs `uv run skills/yf-plan/scripts/plan_manager.py audit` from the repo tree, with the invocation-path rationale in the issue text. Also closes H1's verification gap. | `main-session` | resolved |
| M3 5.2 either/or | medium | Pre-decided **delete + amend SPEC**, consistent with D-1 and trigger (a) not firing; reviving it is what the #92 carve-out issue tracks. `sync.py` re-vendor added to 5.2. | `main-session` | resolved |
| M4 3.2 justification + predicate | medium | Justification restated as a latent-defect fix; the bundle-root predicate is now specified in Issue 3.1's SPEC text; exp-003 §5 (**measured**) cited beside exp-002 §5 (inferred). | `main-session` | resolved |
| M5 motivation falsified claim | medium | Rewritten to "the trigger is conjunctive and has not fired — no stable release — though the adopter half has." | `main-session` | resolved |
| M6 4.1 double-count | medium | **Upheld — verified** (24 dead dirs + 1 dead file). Pre-state restated as 40 items with the unit mismatch named. | `main-session` | resolved |
| M7 4.2 smaller half | medium | **Upheld — verified.** Issue 4.2 extended to the template's unconditional subdirectory entries (24 of 25 violations). | `main-session` | resolved |
| M8 2.1 unhedged SPOF | medium | Fallback branch added: record as a finding, fall back to the three in-repo verbatim copies, carry §13's incompleteness as a stated limit in 2.4 rather than blocking. | `main-session` | resolved |
| L1 triage blanks | low | Dispositions and Resolved By filled. | `main-session` | resolved |
| L2 index.md blurb | low | Already fixed after dispatch — the reviewer read the pre-fix copy. | `main-session` | resolved |
| L3 2.1 no depends-on | low | `depends-on: 1.6` added. | `main-session` | resolved |
| L4 CHANGE-VALIDATION header | low | One-line correction folded into Issue 1.3. | `main-session` | resolved |

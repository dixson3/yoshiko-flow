---
type: Review
okf_spec: OKF-PLAN
id: pass-8
status: complete
---

# Red-team pass 8

## Verdict: REVISE

Sixth independent pass. **Nine of ten pass-7 resolutions verified by execution and hold.** One
high, eight others. C67 — pass-7's high — is genuinely fixed and was proven, not inferred.

## Strengths

- **C67's fix is real.** The reviewer built the harness to Issue 0.2's text, authored all five
  fixtures, and drove the gate through its full lifecycle: no observations → **2**; RED only →
  **1**; both → **0**; delete one record → **1**; missing harness → **2**. **Two of the four REDs
  ran against real repo code**, and ctl-181's GREEN against a real patch to a sandbox copy of
  `doc_lint.py`. All four controls have a satisfiable RED→GREEN pair under the single definition;
  the incompatibility did not relocate.
- **ctl-180's RED is genuine — and the reviewer nearly filed it as a defect before measuring.**
  `close_reconcile_step` has no gate logic and every failure path ends in `sys.exit(0)`; executed,
  it returns `inconclusive`, exit 0. So "assert non-zero" is a real RED today.
- **The negative control is correctly outside the gate** — absent from `controls.txt`, never asked
  for a GREEN.
- **C68 verified complete**: every gate-named observation has exactly one producer, and
  `producers ∩ Blocks = ∅`.
- **C70's citation sweep holds under a whole-bundle re-run** — every `file:line` and all 8 symbols
  verified at HEAD.
- **Every figure reproduces**, including a non-obvious one: corpus SC rows are **160** now vs
  exp-001's **167** at `fb79b44`, and `git show` confirms plan-050 held 24 rows there vs 17 now —
  167 − 7 = 160. Arithmetically consistent across the split. `--exclude` → **757** for the sixth
  time; unfiltered now **823**.

## Concerns

| Concern | Sev | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C77 | **high** | **Issue 2.2's change scope was unspecified, and one reading breaks a test in the FAST and FULL tiers.** `_shared/test_doc_lint.py`'s **SC42** pins `files_checked: 0, verdict: PASS, rc: 0` for a `--root` invocation with no `--path`. Implemented both ways: the general `files_checked == 0` form yields `verdict: NOT_SELECTED, rc: 2` and fails SC42 — and `doclint-tests` is in **both** tiers, so it breaks the on-edit gate for every `doc_lint.py` edit and fails SC15. The `--path` reading survives; the plan named neither | 2.2 now states **`--path`-keyed only**, with the reason, and names four surfaces it must touch or leave alone: `_shared/doc_lint.py`, the vendored copy, `test_doc_lint.py`'s SC42, and `DOC-LINT.md` |
| C78 | med | **The two new verdicts breach REQ-DATA-024's closed vocabulary** (`PASS \| FAIL \| INCONCLUSIVE`, with `INCONCLUSIVE` pinned to "could not run" *and only that*), and `DRIFT-CHECK.md`'s `e-doclint-spec` treats spec as **fixed authority**. That amendment was outside 0.1's enumerated four — pass-6 C55's shape, one epic over. Also "reuse the existing vocabulary" read as contradicting "two new verdicts" | 0.1 now carries `REQ-DATA-024` as an **amendment to an existing id**, distinct from the four new ones, and SC1 enumerates it. 2.2 disambiguated: the reuse claim is about **exit codes**, not verdict strings |
| C79 | med | **`DOC-LINT.md` is an always-loaded protocol whose central table 2.2 falsifies**, and it was on no surface list — along with the vendored `doc_lint.py` copy and `SKILL.md` §6.4. Worse: **§6.4 never checks `close-reconcile-step`'s exit code** (`SKILL.md:1440` captures `RSTEP` and only echoes it), so Issue 1.3's new code would have had no caller — this plan's own M5 vacuity class | All four surfaces added to `context.md`; Issue 1.3 now explicitly must edit §6.4 to give the exit code a caller |
| C80 | med | **The negative control's polarity contradicted 0.2's own fixture definition.** A *fixture* exits 0 iff the asserted behaviour holds — and `neg-179`'s behaviour holds, so a conforming fixture exits **0**, while SC4 wants non-zero. C67's polarity collision surviving inside C67's remedy | 1.1 now reads "**two fixtures and one raw scenario**"; SC4 asserts **`close_cascade.py` itself** exits non-zero rather than "the negative control" |
| C81 | med | **`context.md` and plan.md disagreed on whether Epic 3 needs network.** context.md described the **pre-C12** design; 3.2a says the verb must not require network. plan.md's EXP-005 Results row still carried the superseded "a generator can call the same function" sentence | context.md corrected to "Epic 6 only", noting `_verify_row` itself *is* network-bound (which is why SC8 stubs it); the EXP-005 row annotated **CONFIRMED, then SUPERSEDED by the C12 split** |
| C82 | low | **`pass-7.md` reintroduced the exact defect its own C75 closed** — `## Missing (all now closed)`. Sixth consecutive round of the self-injected-remedy class | Fixed line-anchored. The naive replace would have corrupted the C75 row, which *quotes* the same string — the assert caught a two-occurrence match |
| C83 | low | The gate Condition still asserted "two different **times**" and SC2 "**before** its fix landed" after C69 removed the mechanism. The real enforcement is the `depends-on` DAG — real, but named nowhere | Both now state the ordering is carried by the edges 1.1→1.2/1.3, 2.1→2.2, 3.1→3.2, and that the records assert the exit-code distinction only |
| C84 | low | The GREEN producers still carried `<fixture> <control>` placeholders — C73's "seven issues pass a string byte-identically" hazard on the other half | Control ids named in 1.2, 1.3, 2.2 and 3.2a |
| C85 | low | SC20 could fail for the benign reason AGENTS.md documents: `build.rs` re-runs only on `yf/` or `skills/` changes, and 6.2-6.5 commit only under `docs/plans/` | SC20 now accepts the documented pre-commit-hash case **with the reason recorded in `log.md`**; an unexplained mismatch still fails |

## Missing

_All now closed._ The plan bounded the corpus *figure* (SC7, R2) but never the *contract surface* —
confirmed by the reviewer's patched engine still reporting `PASS 757` on the excluded corpus run.
That gap is what C77/C79 close.

Non-defect noted: `plan_extract` blanks backtick spans inside issue titles; plan-049 shows identical
behaviour, so it is pre-existing engine behaviour, not this plan's.

## Gate Assessment

**Capability/observed-RED: satisfiable, aggregate and falsifiable for all four controls** — built
and driven 2→1→0→1→2, with two REDs against real repo code. `producers ∩ Blocks = ∅`; no
REQ-AGENT-046 cycle; no frontloading miss (the gate needs 3.2a's record, so it cannot sit earlier).
The negative control is correctly excluded. C66's dual disclosure re-verified honest. Start Gate,
Upstream-write and Reconcile Gate all OK — the `length > 0` guard prevents a vacuous pass.

## Upstream Assessment

All 14 rows OPEN, titles matching verbatim, each disposition checked against `_verify_row`'s actual
source branches. `partial` ×4 **now covered in specification** by 6.2's grant-derived list and its
four extractor-confirmed annotations. `deferred` ×4 correct with empty `Resolved By`. `exclude` ×2
filtered before `_verify_row`. `tracker` ×1 → `inconclusive`, exactly SC17's stated acceptance.
#183's non-`tracker` reasoning verified in source both ways.

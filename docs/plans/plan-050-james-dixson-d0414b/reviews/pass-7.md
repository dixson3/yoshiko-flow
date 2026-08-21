---
type: Review
okf_spec: OKF-PLAN
id: pass-7
status: complete
---

# Red-team pass 7

## Verdict: REVISE

Fifth independent pass. **Thirteen of fifteen pass-6 resolutions hold under execution.** One high,
down from three, and ten concerns down from fifteen.

## Strengths

- **C52's fix is real, not paper.** The reviewer built `redcheck.sh` (3 verbs) + `gate-run.sh` +
  `controls.txt` strictly to Issue 0.2's text and ran the gate `Test` **verbatim** through its full
  lifecycle: harness present, no observations → **2**; RED half only → **1**; both halves → **0**;
  delete one record → back to **1**. Satisfiable, aggregate, and falsifiable.
- **C53's fix is correct and complete** — exactly one producer per GREEN observation, and no
  gate-blocked issue produces gate evidence.
- **Every figure reproduces.** `--exclude` → **757** again, while unfiltered has now drifted
  817 → 820 → 821 → **822** across this session. Third independent vindication of the
  self-exclusion. `bd list` → 1481, matching context.md, exp-002 and exp-004.
- **All three line citations in `plan.md` verified exact at HEAD**, and source↔installed parity on
  `red-team.md:63` confirmed by `diff -q`.
- **C54's rebuild is right** — all 49 sections parsed by number: exactly the 14 acted-on rows
  filled, dispositions matching plan.md literal-for-literal, #176/#171 cleared, no misplaced notes.
- **C56's SC17 is runnable and falsifiable** — executed, returning `verdict: "fail"`, exit 1, with
  per-row detail. REQ-CLI-018 verified verbatim at `spec/cli.md:116`.
- **The Reconcile Gate executes correctly** — the `length > 0` guard prevents a vacuous pass.

## Concerns

| Concern | Sev | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C67 | **high** | **Epic 1's #179 control had no satisfiable RED→GREEN pair** — C52's class, one epic over, which the pass-6 spike never built. plan.md required the open-wrapper fixture to be non-zero **post-fix** (SC4, R5) *and* to yield a zero `assert-distinguishes` record (1.2 + Condition). Verified invariant in source: an open non-gate wrapper is already non-terminal, so the cascade already fails today and 1.2 forbids changing that. The reviewer drove both readings of "fixture" through the harness — under one the RED half cannot be recorded, under the other the GREEN half cannot — and showed **#180 and #178 require the opposite reading from #179**, so no single definition worked | Issue 0.2 now **defines** "fixture": a script exiting 0 iff the control's asserted behaviour holds, and `controls.txt` lists only red→green controls. Issue 1.1 split into **three**: `ctl-179-wrapper-close` (SC3's scenario — genuinely red→green), `ctl-180-chain-order`, and a **negative control** `neg-179-open-wrapper` explicitly NOT in `controls.txt`. SC4 and R5 retargeted to the negative control |
| C68 | med | **The RED half's producing instruction was asymmetric.** C53 was rated high on "an executor working 2.2 from its text would never run it" — but 1.1/2.1/3.1 said only "Record the RED observation", with no verb, arguments or target file | Symmetric `redcheck.sh record-red <fixture> <control>` clause added to 1.1, 2.1 and 3.1 |
| C69 | med | **C61's git-HEAD hash did not make the ordering assertion checkable.** Nothing required the fix to be committed before `assert-distinguishes`, and `rev-parse --short HEAD` carries no dirty marker — demonstrated with both records landing on an identical hash, making "descends from" vacuous. SC2b also named no command | Ordering claim **dropped**; SC2b now rests on the exit-code distinction alone (non-zero `record-red`, zero `assert-distinguishes` per id in `controls.txt`), which `verify-all` already asserts. Schema keeps `git describe --always --dirty` for diagnosis only |
| C70 | med | **The stale-citation class survived a fifth round — injected by C59's own remedy.** C59 declared symbol names "the only citations that never go stale" and replaced two bad line numbers with **`cmd_verify_reconcile`, which does not exist**. The described behaviours were both correct; the symbol was not | `verify_reconcile` in both cells. Then verified **every** symbol cited anywhere in `plan.md` against source — all 8 exist |
| C71 | med | **Three `partial` rows required an upstream mention no issue drafted.** The table assigns #150/#173/#174 to Issue 6.2, whose text named only #177 and #149. `verify-reconcile` executed: **all four `partial` rows FAIL**. #178's late-halt shape in the comments column instead of the closes column | 6.2 now drafts **from the 3.2a `grant` verb's output, not a prose list**, and carries `resolves-upstream: #150, #173, #174 (partial)` — extractor confirms all four annotations present |
| C72 | low | C54 residue — `upstream-triage.md`'s #184 disposition was corrected to `deferred` but the trailing "Resolved by 5.3." survived. The only orphaned tail across all 49 sections | Deleted |
| C73 | low | `controls.txt`'s id strings had no provenance — 0.2 would have had to invent four strings for controls it has not built, and seven issues pass them byte-identically | The four ids named verbatim in Issue 0.2 and used in 1.1/2.1/3.1 |
| C74 | low | `index.md` stated a count in the same sentence claiming no count is stated | "(49 sections)" dropped |
| C75 | low | **The audit was not green** — `pass-6.md` failed two required-shape checks (`## Missing (all now closed)` instead of `## Missing`; resolutions table not leading with `Concern`). Warnings not errors, but pass-6's own claim that "every mechanical gate was green" was no longer true of the bundle | Heading and table shape corrected; audit `pass` with **zero** findings |
| C76 | low | SC18's "generated, not hand-listed" is a provenance claim with no exit code — a small instance of the M5 vacuity class the plan is about | Restated as a content assertion: regenerate from plan.md's tables and `diff`; a non-empty diff fails |

## Missing

_All now closed._

A RED→GREEN fixture for #179 (C67); a stated definition of "fixture" (C67); the RED producing
instruction in 1.1/2.1/3.1 (C68); a verification command for SC2b (C69); comment coverage for
#150/#173/#174 (C71).

Noted non-defect: `scope-answers.md` is absent, but `audit` and `okf check` both accept the bundle
without it.

## Gate Assessment

Start Gate OK. **Capability/observed-RED was BLOCKING for control #179 only** (C67) — operationally
satisfiable for #180, #181 and #178, proven by building the harness and driving the gate 2→1→0→1.
Producer/Blocks separation correct; no REQ-AGENT-046 cycle; no frontloading miss. C66's dual
disclosure confirmed honest: no gate-`Test` executor exists in `plan_manager.py`. Upstream-write OK.
Reconcile Gate OK and executable.

## Upstream Assessment

All 14 rows confirmed OPEN via `gh`, each verified against `_verify_row`'s **actual source
branches**. `include` ×4 → CLOSED with a mention (6.4). `partial` ×4 → OPEN + mention — **C71 was
the gap**, now closed. `deferred` ×4 → OPEN, mention explicitly not required, empty `Resolved By`
correct. `exclude` ×2 → filtered before `_verify_row`. `tracker` ×1 → `inconclusive` by
construction. #183's non-`tracker`/non-`supersede` reasoning verified in source, both halves.

"#177's D-6 row is the strongest in the bundle: it states what is IN, what is OUT, and *why*, with
the falsifying measurement."

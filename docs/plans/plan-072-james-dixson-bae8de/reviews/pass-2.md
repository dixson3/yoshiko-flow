---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 2, reading] REVISE: all 14 pass-1 fixes landed in the body, but CC init lists only user-invocable skills, so the C11 check makes every CC candidate run INCONCLUSIVE; a streamed row can corrupt --json and land a red FULL as pass; exit-4 mapping would soften pytest failures; 10 concerns, 2 high"
plan: plan-072-james-dixson-bae8de
pass: 2
mode: reading
---
# Plan Red-Team: plan-072-james-dixson-bae8de

## Verdict: REVISE
**Mode:** reading

## Strengths
- All 14 pass-1 resolutions appear in `plan.md`'s body, not only in the Resolutions cells. C1 is in Issue 2.5 and SC7/SC12. C2 is in Approach REQ-SKAUTH-062 and R3. C3 is in D1 and Issue 0.4. C4 is in Issue 2.3. C5 is the detector's staging-root input. C6 and C11 are in the candidate-mode clause and Issue 2.3. C7 is REQ-ENGINE-011 plus Issues 0.6 and 2.1. C8 is in D3, D9 and the spend gate. C9 is in SC2. C10 is in Issue 1.1. C12 and C13 are in REQ-SKAUTH-062 and Issue 2.3. C14 is in REQ-YF-EMBED-007 and Issue 1.2. The two exceptions are stale leftover text, listed as C6 and C7 below.
- The C6 fix works. One live call in clone-cc with the 20 repo skills staged and `--setting-sources project --permission-mode bypassPermissions` exited 0, and the init event reported `permissionMode: bypassPermissions`.
- The resolution claim that "`_validate_merged` already halts L3 on INCONCLUSIVE" is correct as a statement about the code. `plan_manager.py:4541` reads `result["status"] = "pass" if eng_status == "pass" else "fail"`, so an engine INCONCLUSIVE becomes a halting `fail` at L3.
- The C2 false-FAIL figure is about right. Recomputed over 240 cells (FAIL if a cell scores ≤1/3, then pools ≤2/6): 1.7% at 95% per-run reliability and 21.9% at 90%. The plan says ~2% and ~26%; 26% corresponds to roughly 290 cells.
- Moving the checker and the five cap trims into one change-set (Issue 1.1) closes the red-tree window cleanly.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: 20 repo skills staged at `clone-cc/.claude/skills/`, then `claude -p "Reply ok." --setting-sources project --permission-mode bypassPermissions --output-format stream-json --verbose --max-turns 1` → exit 0. Init `skills` held 15 yf names; missing: `yf-beads-authoring, yf-beads-extra, yf-drift-check, yf-optimal-instructions, yf-skill-authoring`. `grep user-invocable ~/.claude/skills/yf-*/SKILL.md` → those same five are `false`. The EXP-003 raw CC streams show `Skill yf-drift-check` 10×, `yf-skill-authoring` 9× and `yf-optimal-instructions` 5×, although none of the three appears in init `skills`. | **The C11 fix makes every CC candidate run INCONCLUSIVE.** REQ-SKAUTH-062 requires init `skills` ⊇ staged names. CC's init `skills` field lists only skills the user can invoke; the model can still load and call the other five, as EXP-003 shows. So the ⊇ check fails on every run. The FULL row would then always exit 4, `_validate_merged` would turn that into `fail`, and every landing would halt. Even a relaxed check could not verify the text of three of the six sibling-cluster skills, which are the ones whose routing the plan exists to protect. Issue 2.3's test for "a missing staged skill" would pass on synthetic fixtures and never meet this. | Change the CC verification to: init `skills` ⊇ staged names **whose `user-invocable` is not false**, plus a sha256 of every staged file, plus `--setting-sources project` asserted. For the other five, add a separate check that CC loaded the staged text: e.g. one tools-off quote per FULL run, or a `--debug-file` skill-load line if one exists (measure which). State the limitation in REQ-SKAUTH-062. Build Issue 2.3's fixture from a real init event. |
| C2 | high | measured: sandbox spike (mktemp, removed). `plan_manager._validate_merged(root=<sandbox with approved CHANGE-VALIDATION.md>, runner=fake)`. When the fake's stdout was engine JSON reporting `status: fail` → result `fail`. When the same JSON came after one line of progress text → result `pass`, engine `none`, with the "RAN PLAN GATES ONLY" notice. Code: `_run_change_validation` does `json.loads(r.stdout)`, returns None on error, and falls through to tier 3. | **`stream: yes` can turn a red FULL tier into a green landing.** REQ-ENGINE-011 says a streamed row passes its output through live, but it does not say which stream. If the eval's progress reaches the engine's stdout, the `--json` payload is no longer parseable. `_validate_merged` then falls through to tier 3 (no `validate-cmd` is configured here: `.yf/plan/config.local.json` holds only `execute.worktree`), and tier 3 returns `pass`. The same happens if the row passes. The progress also never reaches the operator at L3, because `_validate_merged` captures all output (`capture_output=True`), so R1's "live streamed output" does not hold at land time. | In REQ-ENGINE-011 and Issue 2.1: a streamed row writes to **stderr only**, and `--json` stdout stays a single JSON document. Add a test that runs `run --tier full --json` with a streamed row and checks that stdout parses. Either restate R1 honestly (no live progress at L3), or change L3 to stream stderr. Consider filing the fall-through-on-unparseable-output behaviour as a follow-on against yf-plan: an unparseable payload from an approved manifest should be `fail`, not tier 3. |
| C3 | medium-high | measured: `uv run --with pytest python3 -m pytest nonexist_test.py -q` → exit 4. CHANGE-VALIDATION.md §1 (plan-046 Issue 1.3) says exit 4 on a moved target "is a loud failure". The manifest has 25 pytest rows. | **REQ-ENGINE-011 applies "exit 4 → inconclusive" to every row.** Every pytest row with a moved or renamed target would drop from FAIL to INCONCLUSIVE. Because the engine does not `break` on inconclusive, the later rows also still run. At L3 this still halts, but the FAST and pre-push verdicts report INCONCLUSIVE instead of FAIL. That reverses a correction the manifest records deliberately. | Make the mapping opt-in per row, for example a new column or row attribute `inconclusive-exit: 4`, set only on the eval row. Note it in REQ-SCHEMA-002. Test that a pytest-style row exiting 4 is still `fail`. |
| C4 | medium | inferred: from D9 and the D3 per-run cost: 3.2 all-skill ≈ $75–110, 3.4 all-skill ≈ $75–110, plus 3.1 and 3.3 | **The $200 ceiling is mostly spent before the trim loop starts, and the ceiling is not enforced across runs.** The two all-skill `--record` runs (3.2 and 3.4) cost about $150–220 between them, which leaves ~$0–50 for trimming 20 skills in 3.3. So the gate will almost certainly fire, and it may fire before 3.4 can run at all. `--budget-usd` also caps one invocation, but D9's ceiling is cumulative over many 3.3 invocations. Nothing in the plan records the running total. | Say whether 3.2 and 3.4 count against D9. Add a persisted spend ledger (e.g. `assets/spend.jsonl`, appended by every run), have `--budget-usd` read the remaining amount from it, and have 3.3 and the gate read it too. Or raise the ceiling with the operator, stating the arithmetic. |
| C5 | medium | inferred: the gate text | **The spend-ceiling gate cannot be resolved in the normal case.** Its Condition is "spend *has reached* the ceiling AND the operator decides…". If the ceiling is never reached, the condition is false, yet the gate is a human gate that blocks 3.4. The Instructions ("answer not reached") contradict the Condition. It also blocks 3.4, while the stop actually happens inside 3.3. | Make the Condition a disjunction: "the ledger total is below the ceiling, OR the operator has approved continuing to a new ceiling". Use an auto Test that reads the ledger, and fall back to human only when over. Say that 3.3 halts at exit 4 and the gate authorizes resuming it. |
| C6 | medium | inferred: from D9's scope rule and the detector definition | **A scoped re-rate misses a trim that takes over another skill's intents, and 3.4 has no loop back.** Trimming skill A re-rates A's intents plus near-misses that name A. If the new text makes A fire on skill B's should-trigger intents, which do not name A, nothing in scope catches it. The 3.4 all-skill run would catch it, but 3.4 only reports; no step says what happens when 3.4 finds a regression against the baseline. Separately, the verdict rule is written as "rate below 0.5" without saying how a near-miss cell's rate is defined (correct non-activation rate, or wrong-activation rate). | Define the cell rate as "correct behaviour" for both intent kinds in REQ-SKAUTH-062. Add to 3.4: any regression against the baseline reverts that skill to its last accepted text and re-records, or goes to the operator. Optionally widen the scope to every intent of every skill that lists A as a sibling. |
| C7 | low-medium | measured: `grep -n "three-tier\|crisp/satisfactory/loose\|2.4 h" plan.md` | **Stale text contradicts the revised decisions.** The frontmatter `description`, H1 and Objective §2 still describe a *three*-tier crisp/satisfactory/loose rating (D1 now has four states). The EXP-002 findings paragraph still says "~2.4 h / $55–90 … the operator re-confirmed D3 with these numbers", which conflicts with D3's corrected ~3.1 h / $75–110. A cold reader of the Objective gets the old model. | Update the frontmatter, H1, Objective §2 and the EXP-002 paragraph to four states and the corrected cost, keeping the pass-1 note. |
| C8 | low-medium | measured: EXP-002 findings table, pi row: "cliproxyapi reports `cost.total: 0`" | **The pi half of the spend is not measured.** `--budget-usd` and the list-rate totals therefore cover CC only, and D9's "measured, not estimated" ceiling misses about half the runs. | Record pi token counts from its stream, and price them at a stated list rate or report them as tokens only. Say in D9 that the ceiling is CC list-rate plus pi tokens. |
| C9 | low | inferred: EXP-004, and the candidate mode stages only 20 skills | The per-run listing-budget WARN (EXP-004) cannot fire in candidate mode, because 20 skills (~16.9K chars, falling) are under the 30K budget. Recording it there always reads "no WARN". | Record the WARN only in installed mode (5.3), or label the candidate-mode field as expected-false. |
| C10 | low | inferred: Issue 5.2 plus L3 | A landing runs FULL twice: once on the execute branch (5.2) and again at L3. That is ~6 h and ~$150–220 per landing. D3 accepts the cost per FULL run, but a doubled run is not stated anywhere. | Either say that 5.2's FULL run is the rehearsal and is expected, or have 5.2 run everything except the eval row and let L3 carry the eval. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| pass-1 C1–C14 landing | Read `plan.md` body against each Resolutions cell | n/a | All 14 appear in the body. Stale leftovers in C7 |
| CC candidate init | `claude -p "Reply ok." --setting-sources project --permission-mode bypassPermissions --output-format stream-json --verbose --max-turns 1` (clone-cc, 20 skills staged) | 0 | `permissionMode: bypassPermissions`; init `skills` has 15/20 yf, missing the five `user-invocable: false` skills (C1). $0.24. Staging removed, `git status --porcelain` empty |
| EXP-003 CC init vs Skill calls | python scan of `~/.cache/plan072-eval/raw/cc-*.jsonl` | 0 | One init shape (15 yf). Skill calls include drift-check 10, skill-authoring 9, optimal-instructions 5, none of which is listed in init |
| pi description presence | scan of `raw/pi-*.jsonl` `message_start` | 0 | All 20 yf names and description text present, so the pi hash check is feasible |
| `_validate_merged` stream contamination | sandbox spike calling `pm._validate_merged(root=…, runner=fake)` | 0 | JSON only → `fail`; progress line + JSON → `pass`, engine `none` (C2). Sandbox removed |
| pytest exit 4 | `uv run --with pytest python3 -m pytest nonexist_test.py -q` | 4 | A moved target exits 4, which would now map to inconclusive (C3) |
| engine code read | `change_validation.py` lines 776–858 | n/a | Exit 4 is not special-cased today. Only `fail` breaks the loop. Timeout → `fail` |
| L3 code read | `plan_manager.py` lines 4528–4545, 9180–9205 | n/a | Engine non-pass → `fail`, so L3 halts. Tier 3 returns `pass` with a notice |
| false-FAIL recompute | binomial, 240/360 cells | 0 | 1.7%/2.5% at 95%; 21.9%/30.9% at 90% |

## Missing
- A CC load-verification mechanism that covers skills with `user-invocable: false` (C1).
- Which output stream a streamed row writes to, and a test that `--json` stdout still parses with a streamed row present (C2).
- A persisted cumulative spend ledger, and whether 3.2 and 3.4 count against D9 (C4).
- What 3.4 does when the final all-skill record regresses against the baseline (C6).
- The committed EXP-003 fixtures (Issue 2.3) contain absolute `/Users/james/...` paths in tool arguments. Either normalize them or say the detector is tested with an injected staging and install root.

## Gate Assessment
- **Harness-auth capability gate:** the probe is valid (`pi -p --no-session` and `claude -p` both exist). It is frontloaded. It blocks 3.1, 3.2 and 2.5; 2.5 only wires the row and needs no live run, but blocking it does no harm.
- **Spend-ceiling gate:** its Condition cannot be satisfied when the ceiling is not reached, and it sits at 3.4 while the halt happens inside 3.3 (C5). The arithmetic in C4 says it will almost certainly fire, so its Test needs a ledger to read.
- **Split-decisions gate:** now covers accepted misses for unrouted skills. Sound.
- **Upstream-writes gate:** unchanged from pass 1, frontloaded, sound.

## Upstream Assessment
- Unchanged from pass 1. #407 is included and resolved by 0.3, 1.1 and 3.2. #302 is excluded, with an evidence comment (5.5) covered by the upstream-writes gate. #189 is excluded, justifiably. The rules-aggregate follow-on (5.4) now cites the 3.1 wording-lever result as evidence, which is the right input.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | | | unresolved |
| C2 | high | | | unresolved |
| C3 | medium-high | | | unresolved |
| C4 | medium | | | unresolved |
| C5 | medium | | | unresolved |
| C6 | medium | | | unresolved |
| C7 | low-medium | | | unresolved |
| C8 | low-medium | | | unresolved |
| C9 | low | | | unresolved |
| C10 | low | | | unresolved |

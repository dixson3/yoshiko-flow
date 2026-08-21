---
type: Review
okf_spec: OKF-PLAN
id: pass-6
status: complete
---

# Red-team pass 6

## Verdict: REVISE

Fourth independent pass, first against the split plan. Three highs, all excision damage or a
half-applied fix. Every mechanical gate was green throughout — `audit`, `doc_lint`, `okf check`,
`plan_extract` 0 unparsed / 0 dangling / acyclic — "as they have been at every round, which is the
plan's own thesis about itself."

## Strengths

- **Gate reachability is now structurally correct.** DAG-derived: producers `{1.1,2.1,3.1,1.2,1.3,2.2,3.2a}`
  are each strict ancestors of a blocked issue and none is in `Blocks: 1.4, 2.4, 3.4`. No
  REQ-AGENT-046 cycle.
- **`Discharged-by` is complete in both directions** — the union of all 17 criteria's sets is
  exactly the 22 issue ids.
- **Figures reproduce.** `doc_lint --exclude` → **757**, exactly Issue 0.2a's baseline, while
  unfiltered has drifted 817 → 820 → **821** — which vindicates the self-exclusion rather than
  undermining it. The 167-SC-row figure stays coherent post-split (167 − 7 = 160 measured today).
- **All symbol/line citations in `plan.md` verified correct** at this pass.
- **EXP-003 reproduces exactly**; SC6 is falsifiable and currently RED.
- **D-9's C40 grounding independently confirmed** in `change_validation.py`.

## Concerns

| # | Sev | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| C52 | **high** | **The gate's `Test` could not be satisfied by the harness 0.2 specifies.** It invoked `redcheck.sh` with no verb; 0.2 defined only two verbs, both requiring arguments, with a *per-control* contract, while the Instructions demand an *aggregate* one. Spiked: `unknown verb: '' → exit 2`, which per the gate's own Instructions leaves it **permanently UNRESOLVED**, so 1.4/2.4/3.4 and all of Epic 6 never unblock | 0.2 gains a third verb `verify-all` (no args) that walks `red-prework.md` against a manifest `assets/controls.txt` and returns the aggregate 0/1/2; the gate `Test` now names it |
| C53 | **high** | **C38's fix was half-applied: the zero-on-GREEN observation had no producer.** `grep` found `assert-distinguishes` in 0.2, in 1.4/2.4/3.4, in the Condition and in SC2b — but in **none** of Issues 1.2, 1.3, 2.2, 3.2a, the four the Condition names as producers. An executor working 2.2 from its text would never run it. The RED half was done correctly, which is what made the gap visible | Explicit producing clause appended to 1.2, 1.3, 2.2 and 3.2a; 1.4/2.4/3.4 reworded to "assert `red-prework.md` **contains** both records… runs no `redcheck.sh` verb", removing the ambiguity that let 1.4 be read as producing evidence inside `Blocks` |
| C54 | **high** | **`upstream-triage.md` was filled by section ordinal, not issue number.** #184 still read `include` / "Resolved by 5.3"; #182 got #184's note; **#176 and #171 — issues the plan does not act on — were given dispositions**. A satellite contradicting plan.md on a split decision is the canonical excision-damage finding | **My defect**: the fill script used `re.S`, so `.*?` spilled past an already-filled section into the next blank one. Rebuilt section-bounded, keyed by issue number: 14 filled, **2 spurious cleared**, #184 now `deferred` |
| C55 | med | Issue 0.1's four-REQ list was incomplete *if* SC10 meant `_verify_row` must handle `exclude` — that would amend REQ-CLI-018. Pass-5 C41's defect surviving its own inversion | SC10 narrowed to the shared table's entry set and the `grant` verb's coverage, stating explicitly that `_verify_row`'s non-`exclude` filter is **unchanged by this plan** |
| C56 | med | **SC17's verification could not prove SC17.** Only `fail` halts, so `inconclusive` also exits 0 — and 6.3's `tracker` row returns `inconclusive` by construction. #173's class inside the plan that lists #173 | SC17 now asserts `--json .verdict == "pass"`, or `inconclusive` with the inconclusive rows being exactly the one `tracker` row |
| C57 | med | `context.md` still said "Epics 0-2, **4 and 5** are entirely local" and described **Issue 4.2**'s bead-producer change as in scope | Both corrected; the bead-writes line now reads "it pours and closes its own molecule. Nothing else." |
| C58 | med | `index.md` gave two wrong counts about a sibling file (48 vs 49 sections, 14 vs 16 dispositions) — third round running that `index.md` diverged from a sibling | Counts removed rather than corrected: the number is derivable and has gone stale twice |
| C59 | med | **The stale-line-reference class survived a fourth round** — `plan_manager.py:1404` was fixed in `plan.md` but not in `upstream-triage.md` | Fixed. **And it nearly claimed a fifth victim**: two citations I added while resolving C55/C56 (`:2110`, `:2157`) were both wrong on verification. Replaced with symbol names — the only citations in this bundle that have never gone stale |
| C60 | med | Issue 0.1 asserted the descoped REQs "are recorded in `references/handoff-051.md`" — a file Issue 6.5 creates twenty issues later, whose tables-only spec would not contain them, and SC18 forbade hand-listing | 0.1 → future tense sourced from D-9; 6.5 gains an explicit "descoped SPEC amendments" section; SC18 exempts that section from the tables-only rule |
| C61 | med | `red-prework.md`'s record schema was under-specified relative to SC2/SC2b — no command text, no timestamp, no ordering marker. The **ordering** claim is the entire content of D-4 | 0.2 now specifies the schema: `verb, control, fixture, exit-code, verbatim command, UTC timestamp, git HEAD short hash`. The hash makes SC2b's "written AFTER its fix landed" a real assertion rather than an inference from append order |
| C62 | low | Issue 3.3 did not depend on 3.2a, but SC10 is a property of 3.2a's generator | `depends-on: 3.2, 3.2a` |
| C63 | low | SC9's `Discharged-by` omitted 3.2a — the issue that makes it true | `3.1, 3.2a, 3.4` |
| C64 | low | `exp-004` recorded the weaker "both endpoints" claim while plan.md claims the stronger "either". **plan.md is right** — pass 6 measured it | Finding updated to the stronger form; it matters because exp-004 is plan-051's starting evidence and will be read without plan.md |
| C65 | low | plan.md said #183 **is** closed; `gh` says OPEN | Changed to "currently OPEN; **is closed by** plan-049's own sweep" |
| C66 | low | The gate disclosed that its `gate_type` line is hand-read, but not that its **0/1/2 mapping** is too — no gate-`Test` executor exists | Disclosure extended to both halves. "C40 died on exactly this distinction" |

## Missing (all now closed)

- No issue produced the GREEN observation (C53) — "the single largest gap".
- No `verify-all` mode on `redcheck.sh` (C52).
- No record schema for `red-prework.md` (C61).
- `index.md` did not list `handoff-051.md` — added.

## Gate Assessment

Start Gate OK. **Capability/observed-RED was BLOCKING** — structurally reachable but operationally
unresolvable (C52) with no producing instruction for half its evidence (C53); both now fixed.
Upstream-write OK — `Blocks: 6.3, 6.4`, and 3.2a is an ancestor of both via 6.1. Reconcile Gate OK.
No frontloading miss. One noted non-defect: the aggregate Condition couples Epic 2's chain to Epic
3's, so 2.4 waits on 3.2a; since 6.1 waits on everything this costs nothing real.

## Upstream Assessment

**Dispositions in plan.md: sound, and verified against `_verify_row`'s actual branches.** All 14
rows confirmed OPEN via `gh`. `include` ×4 → CLOSED with a mention (6.4 does both). `partial` ×4 →
OPEN with a mention. **`deferred` ×4 → correct**: the branch requires only `state == OPEN` and
explicitly requires *no* mention, so the empty `Resolved By` cells are right. `exclude` ×2 →
filtered before `_verify_row`. `tracker` ×1 → `inconclusive` by construction, which is what C56
addresses. #183's non-`tracker`/non-`supersede` reasoning verified in source.

The satellite was broken (C54) and is now rebuilt from plan.md by issue number.

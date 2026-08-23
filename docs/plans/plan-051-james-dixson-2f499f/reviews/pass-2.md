---
type: Review
okf_spec: OKF-PLAN
id: pass-2
status: complete
---

# Red-team pass 2

## Verdict: REVISE

Second independent pass, against `1e617b6`. **Two high concerns, both found BY EXECUTION, and both
living inside pass-1's own fixes** — the self-injected-remedy pattern the brief warned about held on
the first opportunity. 9 concerns total; all resolved below, none deferred.

Pass 1 claimed C2 fixed but never ran the fixture. Pass 2 built it and ran all three arms.

## Strengths

- **Every load-bearing premise reproduced at this commit.** EXP-003's census (`251`, both
  measured-false clauses still live); EXP-002's decisive claim (dangling tree →
  `status pass, first_failure None`); EXP-001's RED (0 `Agent` across 7 agent files; whole-file
  `grep -q` exits **0**; SC6's `awk` boundary section exists and is 60 lines).
- **C9's "4 sites" is right and the line numbers are exact** — `red-team.md:63`, `reviewer.md:43`,
  `spec/agents.md:73`, `:97`.
- **~20 line/symbol citations all resolve. Zero stale citations** — notable against plan-050's
  record of 8 stale-citation rounds in 11 passes under four actors.
- **C10's gate producer table re-verified per control**: every producer is a `depends-on` ancestor
  of the `.4` it feeds, none inside `Blocks {1.4, 2.4, 3.4}`, no cycle, earliest legal position.
- **C16 verified by measurement** — both the generic and tightened patterns derive exactly 3, and
  the pattern text embedded in `plan.md` does not self-contaminate.
- **All 19 criteria are falsifiable.** The reviewer looked for one that cannot fail and found none.
- All 11 upstream issues verified OPEN with matching titles; `#177` OPEN confirms pass-1 C14.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| **C21 — pass-1's C2 fix is STILL unsatisfiable under the substitution 1.1 literally prints.** `...` → `.*?` applied to `"writes ... at presentation"` yields `writes .*? at presentation`, which returns **0** against `red-team.md:63` — the file reads `line **at presentation**`, so the `**` sits where the space would be. **Measured 1 / 1 / 1**: still unconditionally red, still an unopenable gate. Only the whitespace-collapsing reading gives the required **1 / 1 / 0** | **high** | **Fixed.** The rule is now normative — collapse the ellipsis *together with its adjacent whitespace* — and 1.1 **prints the resolved pattern verbatim** (`writes.*?at presentation`), the way 0.2 prints its grep. Added a **self-check**: before recording RED, assert each derived pattern returns ≥1 against a hand-fixed copy, since a pattern matching nothing anywhere makes the RED false |
| **C22 — Epic 3's SC8 silently voids Epic 1's conjunct (b).** SC8/0.1 require `REQ-AGENT-043`'s Verification to be *"a whole-line backticked command"*; 3.2's template points at `uv run …test_*.py`. Such a line has **no double-quoted fragments**, so conjunct (b) has nothing to check. **Measured: `fragments-checked=0`, exit 0 on the dangling half-fix tree** — SC3 arm 1 fails and SC4's second clause goes vacuous. Epics 1 and 3 are parallel with no ordering edge, so the merged shape was nondeterministic | **high** | **Fixed at the root, in 0.1**: ONE target shape for every REQ's Verification — a whole-line backticked command **whose arguments are the double-quoted agent-file literals**. That single shape is executable (Epic 3 / #165) *and* carries quoted fragments naming a file (conjunct b). Plus an ordering edge (`3.2 depends-on 1.2a`) so the test asserts against final wording |
| C23 — **#182's closing comment had no producer.** Pass 1 said the D-1 correction *"must reach the closing comment, not just the plan"*; 4.2 drafted only the five `partial` comments and SC13 covered only #149 | med | **Fixed.** 4.2 now drafts **closing** comments for both `include` rows, and **SC13b** requires #182's to quote the issue's *"never write, edit, or create any file"* claim and state the tree never said it. A close that silently accepts a false premise leaves the next attempt to rebuild from it |
| C24 — **SC4 cannot pass as written.** An untracked `.agent-shell/transcripts/*.md` carries the literal 4 times, outside the stated carve-out | med | **Fixed.** The instrument is now **`git grep`** (tracked files only) with a verbatim command — **and the cwd is normative**, since `:!docs/plans` is repo-root-relative and running it inside the bundle reports the plan's own prose as a surviving site. Measured from the root: exactly the 3 source files |
| C25 — **3.2 is singular where SC8 is plural.** SC8 requires three REQs across two agent files; 3.2 wrote one test asserting "**the** REQ" | med | **Fixed.** 3.2 is now **one parameterized test, one case per REQ in {049, 043, 045}**, with the vacuity guard asserting the **case set equals that set** — a set assertion, per 3.3's own never-a-count rule |
| C26 — 1.1 never says how a fragment maps to "the file it names"; two reasonable parsers disagree | low | **Fixed.** 1.1 now requires an explicit fragment→file **table** the fixture hard-codes, rather than leaving the split to inference |
| C27 — `index.md` omits `reviews/` (`okf.py` `REQ-OKF-CHK-002`) | low | **Fixed** — `reviews/` row added; `okf.py check` now 0 warnings |
| C28 — SC7's positive clause is still stub-satisfiable by four empty steps | low | **Fixed as a stated limit rather than papered over**: under D-7 the wisp is scoped to *sequencing*, so step identity and order **are** the substance — plus each non-gate step must carry a non-empty description |
| C29 — SC11 and 4.1 name different instruments | low | **Fixed** — both name `plan_manager.py validate-merged`, with the delegation noted |

## Missing

- **No end-state control re-run.** The three fixtures were evidence of a *transition*, recorded once
  and never re-evaluated — `verify-all` reads `red-prework.md`, the fixtures are not CV rows, and the
  FULL tier does not touch them, so a later epic could silently undo an earlier one's green.
  **Resolved:** 4.1 now re-runs all three fixtures against the merged tree, and SC11 asserts it. This
  was the structural gap behind C22, and it survives C22's fix.
- **No criterion asserts `assets/edit-set-182.md` is complete.** Still open — SC4's zero-literal grep
  covers 4 of the 9 sites; the two `web/content/pages/*` restatements and the two no-edit rows are
  covered by nothing mechanical, which 1.2 states honestly. Carried to pass 3.
- Pass-1's own Missing items are all genuinely closed.

## Gate Assessment

**Reachability sound; satisfiability failed again on the same axis, one whitespace character
narrower.** The DAG properties re-verified clean per control, and the count derivation is sound
(3 declared against a 3-line manifest under both patterns, no self-contamination).

But `ctl-182-spike` was still not guaranteed to reach 0 — **unconditionally red** under 1.1's literal
wording (1/1/1), and **unconditionally green on the very state it exists to catch** under the shape
Epic 3 mandated (`fragments-checked=0`). Which failure execution hit depended on a reading and on an
ordering the DAG did not constrain. Both are now closed at the root: 0.1 fixes one target shape, 1.1
prints the resolved pattern and self-checks it, and an ordering edge makes the sequence explicit.

## Upstream Assessment

Dispositions sound and **no overclaiming found** on #165, #173, #174 or #150 — each `partial` names
what is IN and what stays open, and #165's one-plan scope is genuine against the verified 251/1
census. All 11 issues OPEN with matching titles. Pass-1's C4 fix is correct and important:
`_verify_row` maps `partial` → `requires_mention: True`, so all five needing comments is the right
count. C20's fix holds. The one gap was **C23** — the D-1 correction to #182's premise, wired to
nothing — now carried by 4.2 and SC13b.

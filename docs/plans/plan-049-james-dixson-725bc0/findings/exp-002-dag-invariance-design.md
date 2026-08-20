---
type: Finding
okf_spec: OKF-PLAN
id: exp-002
status: complete
---
# EXP-002 — Design the DAG-invariance postcondition, and prove it can fire

**Question:** Where does it attach, what exactly does it assert, and does it catch the harm it was
created for?

## Approach Tested

Read the handoff §2 and EXP-001's measured harm; audited `okf.py migrate` for a hostable
postcondition point; built the postcondition **as D-4 literally words it** over a 48-plan corpus
copy; drove it with 5 mutants — **A** the "drop the prose tail" replay, **B** edge-target
substitution, **C** the plan-008 gate relocation, **D** a real `okf.py migrate` over all 48 bundles,
**E** the plan-015 de-bold. When A **passed**, built the corrected strong form and re-drove all five.

## Result

**1. `okf.py migrate` cannot host the postcondition as written.**

**measured:** `migrate` takes a single `dir` and writes inline — `write_text` + `unlink` at
`okf.py:1121-1122`, and **`okf.py:1174` rewrites `plan.md` itself**.
`grep -c "backup\|rollback\|restore\|tempfile\|atomic" okf.py` → **0**. A postcondition at the end
runs **after an unrecoverable write** — a detector, not a control. The only non-writing mode is
`--dry-run`, which never computes a DAG.

**2. THE HEADLINE: the postcondition as D-4/D-8 words it FAILS the replay.**

- **measured:** baseline 48 plans, 946 issues, **1015 edges**. Mutant A emptied **23**
  `depends-on` declarations across 9 plans. The D-4-literal guard → **`PASS`, `EXIT=0`**,
  `lost_edges 0`, edges **1015 → 1017**, unparsed **81 → 59**.
- **inferred:** D-8's literal predicate is blind to the exact harm it was written for, **for the
  same structural reason the hash predicate was**: a refused declaration contributes no edge, so
  emptying it destroys nothing the extractor ever saw. **plan-048's own Issue 1.4a all-or-nothing
  refusal widened this blind spot.** The replay presents as an *improvement* on both instruments.

**3. The corrected postcondition — three monotone populations, all under set/multiset containment,
never counts:**

| Layer | View | Element |
| :-- | :-- | :-- |
| **L1** | extractor | `(plan_dir, issue_id)` |
| **L2** | extractor | `(plan_dir, src, dst, kind)` |
| **L3** | **raw text** | multiset of `(plan_dir, kind, referent_token)` — **every token literally written, whether or not the extractor could parse it** |

**L3 is the load-bearing addition and the only layer that fires on the replay.** Substitution is
handled by containment: `a→b` becoming `a→c` is a loss plus a gain, reported as
`L2_substituted_edges`.

**4. Mutant results**

| Mutant | D-4 literal | Strong form | Count-only |
| :-- | :-- | :-- | :-- |
| **A** — 23 emptied declarations | **PASS, exit 0** ← misses all 23 | **FAIL, exit 1** (`L3`, 28 lost tokens) | would FAIL |
| **B** — 2 edge targets substituted | FAIL | **FAIL** (`L2`,`L3`) | **PASS** — totals exactly unchanged |
| **C** — plan-008 gate relocation | PASS | **PASS** | PASS |
| **D** — real `okf.py migrate` ×48, 468 diffs | PASS | **PASS** | PASS |
| **E** — plan-015 de-bold | PASS | **PASS** (+1 issue, +1 edge) | PASS |

**D is the non-vacuous control** — a genuine 48-bundle migration that legitimately passes, so the
guard is not FAIL-happy. **B proves counts are insufficient.** Exit contract: 0 PASS, 1 FAIL,
2 INCONCLUSIVE (a plan vanished — the address-space artifact).

**5. The 16 free recoveries are a VACUOUS first proof.**

- **measured:** the 3 H3 + 13 col-0 = 16 arithmetic reproduces, but the *composition* does not
  match the handoff. Only plan-008's 7 lines are an actual gate block.
- **measured:** performing the plan-008 relocation gives edges **1015 → 1015 — zero delta**; L1, L2
  and L3 all unchanged; unparsed 81 → 76, with **2 new** refusals created.
- **inferred:** expected total edge delta across all 16 is **+1**, and that one comes from plan-015,
  which is a **de-bolding, not a relocation**. **"PASS on the 16" carries no more information than
  "PASS on doing nothing"** — corroborated by mutant D, a 468-diff real migration that also passes.

**6. Fingerprint interaction.** **measured:** plan-008's hash moves under the DAG-preserving
relocation (`e3c87751…` → `e167faaa…`), and only **27 of 48** plans store a fingerprint at all.
The hash must be **a reported note, never a blocker** — blocking reproduces EXP-001's "aborts on
every plan it could improve". *Caveat:* the prototype reports the **stored** field, not the
recomputed hash; wire `_plan_content_fingerprint` in before use.

## Implications for Plan

1. **D-4 must be re-worded before Epic 1 is written.** As carried it is a predicate that measurably
   **passes the harm it was created to catch** — the "check that reports clean while checking
   nothing" shape, reproduced in the very artifact meant to prevent it.
2. **The write-phase needs a staging structure.** Either a corpus driver that stages and rsyncs
   back, or — cheaper and real — run the migration on a **clean git worktree** so FAIL means
   `git checkout -- docs/plans`.
3. **`okf.py:1174` is the highest-risk line in the migration** — the one `plan.md` rewrite, a
   regex-bounded slice deletion. If that regex over-matches into `## Epics`, it deletes the DAG.
4. **The Epic-1 gate cannot be "the postcondition passed on the 16."** That is satisfiable by a
   no-op. It must be **"the postcondition FAILED on mutants A and B"** — a claim about the
   instrument, not the corpus.

## Recommendations

1. **Restate D-4 as the three-layer form with L3 primary**, keeping set/multiset containment
   explicit — a reader who implements it as counts gets a control that passes mutant B.
2. **Land the guard as `_shared/dag_guard.py`**, SPEC-first with a new `REQ-DATA-*` id.
3. **Pin mutants A and B as tests** — the guard must exit 1 on both. Mutant A is specifically the
   test the D-4-literal implementation would fail.
4. **Do not gate Epic 1 on the 16.** Use A + B as the first proof and D as the false-positive control.
5. **Bracket the write with git, not with hope.**
6. **Tell the operator D-8 as inherited does not hold** — the handoff marks this postcondition
   "NOT satisfied — build it first", and building it *as written* would have satisfied that row
   with an instrument that passes the replay.

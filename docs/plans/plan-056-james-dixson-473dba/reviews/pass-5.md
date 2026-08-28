---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: "Red-team pass 5 — REVISE. Fifth recurrence, in pass 4's own fix: bash -n detects neither 126 case and loses the 127 case test -x caught, and the capability gate defaults to a class that is never run."
---

# Red-team pass 5: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 8 concerns resolved by hand.** The review-cycle bound (5 of 5) was reached at this pass, so the
> loop stopped rather than auto-dispatching a sixth — stop class 4, a mechanical counter threshold. C40
> and C41 were both independently reproduced before acting, and both were defects I introduced at pass 4.

**There is a fifth shape, in two places, both inside pass 4's own fix.** Both are one-line edits.

## Strengths

Mechanically re-derived and clean: 34 issues, 21 criteria, **zero dangling `depends-on`**, zero issues
unnamed by a criterion, zero criteria naming a missing issue, `doc_lint` PASS, `reindex --check` **clean**,
`index.md` and `log.md` both repaired as claimed. **C34 holds** — Title, Objective and Motivation are now
congruent with the five epics, and the doc_lint over-claim is stated honestly. **C35 holds** — #265 is in
4.3's close list. The DAG is sound and acyclic with zero backward cross-epic edges.

## Concerns

### C40 — THE FIFTH RECURRENCE. Pass 4's SC0 fix is a net regression. [HIGH]

Pass 4's C32 resolution claimed SC0 now asserts "runnability via `bash -n`… **which closes the 126
branch**." Measured — false in both directions:

| condition | `bash -n f` | direct exec |
|:--|--:|--:|
| mode 644 (not executable) | **0** | 126 |
| bad shebang | **0** | 126 |
| missing | **127** | 127 |

`bash -n` only parses; it never consults the x-bit or the interpreter. Sandbox reproduction against the
real engine:

```
WORLD A (present, mode 644 — the branch pass 4 claimed to close):
  SC0 holds (0) · SC35 inconclusive (126) · SC2 inconclusive (126)
  verdict PASS — evaluated 1
```

Byte-for-byte **pass 4's own C32 reproduction, unchanged by the fix**. And a second branch got worse:

```
WORLD B (harness-selftest.sh missing):
  bash -n form:  SC0 inconclusive (127) -> INCONCLUSIVE, exit 2, warn, never halts
  test -x form:  SC0 FALSE (1)          -> FAIL, exit 1, blocks completion
```

Pass 3's `test -x` form **caught the missing script and blocked**. Pass 4 replaced it with a form that
returns 127 there, which `plan_manager.py:2916` maps to `inconclusive` — invisible to the verdict. **The
fix traded a working detection for a non-working one.**

*Rec:* `for f in <the 7 paths>; do [ -x "$f" ] || exit 1; bash -n "$f" || exit 1; done`. State the
residual (bad shebang passes both) rather than claiming closure a fifth time.

### C41 — The capability gate defaults to a class that is never run, and the plan has no field to say otherwise. [HIGH]

Pass 4 moved the backstop to a gate because "a gate's `Test:` is executed by the coordinator and halts".
Verified against the skill rather than the plan's claim about it:

- `test_gates.py:243` — `test_class = gate.get("test_class") or "manual"`; `manual` -> **INCONCLUSIVE**,
  and both `coordinator.md:179` and `SKILL.md:1314` say INCONCLUSIVE is **never FAIL**.
- `SKILL.md` §5.2c: "Run the `probe` class — **and ONLY the `probe` class** — unattended."
- The `## Gates` grammar has `Type / Condition / Test / Blocks / Instructions` — **no `test_class`, no
  `cwd`**. `plan_extract.py:110`'s `GATE_FIELD` matches exactly those. Confirmed on this plan: the
  extracted gate carries no `test_class`. `grep -rn test_class` over `formulas/`, `plan_manager.py`,
  `gate_consistency.py` -> **zero hits**.

So the value is invented at pour time, and an absent value defaults to the one class never executed.
**The plan's single declared defence that "reaches this plan" is inert by default** — the fifth shape,
same family as its four predecessors. Secondary, same root: `cwd` is also undeclarable, and Epic 1's
scripts land in the worktree, so a gate poured `cwd: repo-root` permanently FAILs into stop class 2.

*Rec:* add an explicit pour instruction to the gate's `Instructions:` — `test_class: probe`, `cwd:
worktree` — and file a follow-on that the `## Gates` grammar cannot express the two fields the sweep
dispatches on. The gate's *reachability* is otherwise sound.

### Pass-4 resolutions: two of eight did not fully land [MEDIUM]

- **C36 is 4-of-5.** The resolution claims the 33/34 miscount was corrected "in both D-17 and R12".
  D-17 says 34; **R12 still says 33**. Extractor counts 34. This is the **third false ledger row** in
  this plan's resolutions.
- **C38's #140 half did not land.** Claimed `Resolved By: 3.1, 3.2, 4.3`; the cell is **empty**, and 4.3's
  text does not name #140. Mitigated: `reconciler.md` parses the table itself for every non-exclude row,
  so #140 is handled at reconcile regardless — hence medium.
- **C34 residue [LOW]:** Motivation still cites `1054 files / 1634 findings` while D-1 cites the
  re-measured `1088 / 1642 / 392`.

## What four passes had not reached

- **The repo already has a check harness with a conflicting exit contract, unmentioned by the plan.**
  `scripts/checks/_common.sh` (plan-055) declares for every instrument in that directory:
  `0 holds · 1 does not · 2 could NOT RUN (INCONCLUSIVE)`. Issue 1.8 pins INCONCLUSIVE to **exit 3**, and
  Issue 0.14 drafts a "verification-harness contract" as if none exists. Issue 1.9's eight scripts land in
  **that same directory** under a different contract. [MEDIUM]
- **`harness-selftest.sh --require 8` re-implements `redcheck.sh verify-red-checks`** (plan-054), which
  already iterates `checks/`, requires a recorded non-zero pre-fix observation per script, and
  `harness_fail`s when it finds no instrument — precisely the `--require N` idea. It was not copied into
  `scripts/checks/` by plan-055, so 1.9 is not strictly redundant, but writing an eighth bespoke script
  rather than relocating the proven one deserves an explicit decision. [MEDIUM — prior art]
- **`--require 8` excludes `check-pytest-ran.sh`**, which **6 of 21 criteria** route through, and
  `check_okf_index_drift.py`. The non-vacuity floor misses the highest-traffic instrument. [MEDIUM]
- **SC36 invokes `test_recheck_criteria.py`, which no issue creates.** Issue 1.10 names no test file.
  C18/C28's exact wording in miniature. [MEDIUM]

## Executability

**Yes, with the two HIGH items fixed.** A competent executor could follow this plan cold: sound acyclic
DAG, full bidirectional coverage, a genuinely portable bundle, and issue bodies carrying their own
measurements and counter-arguments. Nothing structurally blocks execution. What blocks *trustworthy
completion* is C40 and C41; everything else is recoverable at execution time.

**Non-blocking notes:** Epic 0's issue ids read oddly cold (`0.1 0.2 0.3 0.4 0.14 0.13 0.9 …`, with
0.5-0.7 absent to plan-057); #170's Notes retain argumentative "**`partial`, not `include`**" phrasing
beneath its now-correct `deferred` lead.

## Missing

- An issue owning the harness's own correctness that is not itself run by the harness.
- A `CHANGE-VALIDATION` row for the new check scripts.
- Anything reconciling `scripts/checks/_common.sh`'s existing exit contract with the one Issue 0.14 drafts.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Verification harness ready | **Inert as poured** — no `test_class` field exists in the grammar, so it defaults to `manual` and is never run (C41) | evidence in Epic 1, correctly early | **Defective**; see C41 |
| Reconcile Gate | auto | — | fine |

## Upstream Assessment

`verify-reconcile` fails for the correct pre-execution reason. #140's `Resolved By` is empty despite its
`partial` disposition (C42), mitigated by `reconciler.md` parsing the table itself for every non-exclude
row. #170's Notes still argue a disposition the row does not hold.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C40 SC0 `bash -n` is a net regression | high | Reproduced independently before acting: `bash -n` returns **0** for mode-644 and **0** for a bad shebang, and **127** for a missing file; `test -x` returns **1** for both mode-644 and missing. Pass 5 is right that my pass-4 change was a net regression on the missing-script branch and bought nothing on the 126 branches. SC0 restored to `test -x … -a -x …` over **all ten** instruments (verified: exit 0 all-present, exit 1 one-missing), with the residual stated rather than closed a fifth time — a bad shebang passes this check and surfaces only as a 126 at run time, which is what `harness-selftest.sh` (SC35) exists to catch by actually executing each script. | `main-session` | `resolved` |
| C41 gate defaults to `manual`, never run | high | Verified against the source, not the plan's claim: `plan_extract.py:110`'s `GATE_FIELD` matches only `Type|Approvers|Condition|Test|Blocks|Instructions`, the extracted gate object carries no `test_class`, and `test_gates.py:243` defaults an absent value to `manual` — which §5.2c never runs. The gate's `Instructions:` now carry an explicit **pour with `test_class: probe`, `cwd: worktree`** directive with the reasoning, since the grammar cannot express it. And the grammar gap itself — every capability gate in every plan depends on a value invented at pour time whose default is the one class never executed — is added to Issue 4.2's filing list. | `main-session` | `resolved` |
| C42 R12 miscount; #140 Resolved By empty | medium | R12's stale 33 corrected to 34 (third occurrence of that miscount class, and the third false ledger row overall). #140's `Resolved By` filled with `3.1, 3.2, 4.3` and Issue 4.3's text now names #140 explicitly with the root-tier enforcement it comments on. | `main-session` | `resolved` |
| C43 conflicting `_common.sh` exit contract | medium | Real defect, and the plan was drafting a second contract beside an existing one. Issue 1.8's INCONCLUSIVE re-pinned from exit 3 to **exit 2**, matching `scripts/checks/_common.sh`'s declared contract for that directory (`0 holds · 1 does not · 2 could NOT RUN`). Issue 0.14 reworded to **codify the contract that already exists** rather than draft a new one, adding only what `_common.sh` does not yet state. | `main-session` | `resolved` |
| C44 `redcheck.sh` prior art unconsidered | medium | Issue 1.9 now requires evaluating `redcheck.sh verify-red-checks` (plan-054) as prior art **before** writing anything: it already iterates `checks/`, requires a recorded non-zero pre-fix observation per script, supports an allowlist-with-reason, and fails when it finds no instrument — which is exactly `--require N`. plan-055 did not copy it into `scripts/checks/`, so this is not strict duplication, but relocating the proven implementation is now the default and a bespoke script needs a stated reason. | `main-session` | `resolved` |
| C45 `--require 8` excludes the busiest instrument | medium | `--require 8` raised to **`--require 10`** in the gate, in SC35, and in the criterion text. The old floor excluded `check-pytest-ran.sh` — the busiest instrument at 6 of 21 criteria — and `check_okf_index_drift.py`, so the non-vacuity floor missed exactly the scripts most criteria depend on. | `main-session` | `resolved` |
| C46 SC36's test file has no creating issue | medium | Issue 1.10 now names `skills/yf-plan/scripts/test_recheck_criteria.py` explicitly, matching how Issues 2.4 and 2.5 name their test files. SC36 invoked it while no issue created it — C18/C28's exact defect in miniature. | `main-session` | `resolved` |
| C47 Motivation/D-1 figure mismatch; cold-read notes | low | The Motivation's `1054 files / 1634 findings` updated to the re-measured `1088 / 1642`, so it agrees with D-1. #170's Notes rewritten so the argumentative 'partial, not include' phrasing reads as background for the successor rather than contradicting its own `deferred` disposition. | `main-session` | `resolved` |

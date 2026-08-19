---
type: Review
okf_spec: OKF-PLAN
id: pass-3
---
# Red-team pass 3 — plan-047-james-dixson-dec9ff

## Verdict: REVISE

**Date:** 2026-08-18 · **Status:** all concerns resolved (H3 by operator-authorized upstream write) · **Brief:** verify pass-2's claimed resolutions.

**Headline: 8 of 17 verified claims were over-stated, and the defects were in the FIXES, not in
untouched material.** H1 is a DAG edge broken by the N4 restructure; M1/M2 are defects inside the
N1 fix; M3 is the N5 sweep stopping at `plan.md`; M4 is the N9 count. Third consecutive cycle of
this repo's documented recurring defect.

## Resolution verification

**Genuinely resolved:** N2 (all nine sections restored; `okf.py check` → `ok: true`), N3 (EXP-006
row complete and reworded so the `t.index("## Epics")` bug cannot recur), N6 (`2.5 depends-on: 2.6,
2.7` — real DAG order, not prose), N7 (SPEC-first holds: `0.9a → … → 2.7 → 2.5`), N8
(`ready-check --json` → `verdict: REVISE, review_pass: 2, malformed_review: null`), N10, M10, H2, H3
(D-9 now says Epic 8; #125 `Resolved By` = 2.5), and N1's *allocation* (018/019/024–028 all verified
free).

**Partially resolved or not resolved:** N4, N5, N9, N11, M2, M8, H1.

## Concerns

| # | Severity | Concern | Status |
| :-- | :-- | :-- | :-- |
| **H1** | **high** | **Dangling `depends-on` — Issue 4.1 → 3.6**, which does not exist (Epic 3 is 3.1–3.5). Broken by the N4 restructure when the old 3.4 moved to 1.4 and Epic 3 renumbered. Pass 2 asserted "0 dangling — verified by parse"; **false of the document as it then stood.** At the pour this is either a `bd dep add` against a nonexistent bead or a **silently dropped edge — the 45-dropped-edge class this plan exists to detect, in the plan that detects it** | **resolved** — edge repointed to 3.5; full parse re-run: 0 dangling, 0 uncovered, 0 phantom |
| **H2** | **high** | **SC9d unachievable; N4's central claim falsified by the engine.** The gate resolver is **exit-code only** (`coordinator.md:179-183`, enforced by `test_gates.py:_classify`) — nothing outside the script reads its JSON. Executed: an empty `.sh` exits **0** and the gate resolves. So "a stub yields INCONCLUSIVE because the gate asserts on named JSON keys" is false: the assertion lived *inside the artifact it polices*. Same accident in a third costume — `KeyError` → `exit 127` → `stub exits 0` | **resolved** — the `jq -e` assertion moved **out of the script and into the gate `Test:`**, per script with its own key set. Issue 1.4 rewritten to state why the placement is the whole point. SC9d restated against what is achievable |
| **H3** | **high** | **Tracker row still not resolved — third cycle.** `_TRACKER_ROW_RE` (`plan_manager.py:1383`) requires cell 1 to be `#<digits>`; the row's cell 1 is `_(tracker)_`. Executed: regex → `None`; `stamp-tracker --json` → `{"status":"skipped"}`. Every prior plan uses `[#NNN](url)`. Nothing verifies it until Issue 10.5 — position 75 of 76 | **resolved** — operator authorized the write; **#175** filed and `[#175](url)` written into cell 1. Verified: `_TRACKER_ROW_RE` now matches and returns `175`, and `stamp-tracker` skips for the *correct* reason (`"no epic recorded (pour has not run yet)"`) instead of `"no row with disposition tracker"`. Filed at drafting rather than INTAKE because `stamp-tracker` runs at the pour, **before Epic 0 executes** |
| M1 | med | SC4 said "six new ids" while **seven** are allocated (`REQ-DATA-028` absent from SC4's list, its `Discharged-by`, and Issue 0.9's sweep). The #135 stale-count class introduced *inside* the fix for N1 | resolved — seven everywhere; `0.9a`/`0.9b` added to SC4's dischargers |
| M2 | med | **SC4's row is malformed GFM — 5 cells, expected 4** (unescaped `\|` in `grep … \| sort -u`). `markdown_lint.py` → `ML005`. A malformed table row in the Success Criteria table of the plan whose objective is mechanical parseability | resolved — pipe escaped |
| M3 | med | **`upstream-triage.md` was never swept — 7 stale references.** They survived the automated sweep precisely because the ids all *exist* — semantically, not syntactically, dangling | resolved — all 11 Notes regenerated from `plan.md`'s (correct) table |
| M4 | med | **SC20's count wrong three ways again**: text said 10, `Discharged-by` listed 9, Epic 6 has 11, schema-bearing types are 8 | resolved — "8 schema-bearing types (6.1–6.8)" |
| M5 | med | Issue 1.4's key list named one triple for four scripts, and **`output_tail` is a per-command key inside `commands[]`, not top-level** — a literal reading reproduces H1's original defect | resolved — per-script key sets stated, with the `commands[i].output_tail` nesting called out |
| M6 | med | **Issue 0.9's "run the allocation check FIRST" is contradicted by its own DAG** — it depends on every id-writing issue, so the guard installed to prevent N1 was structurally **last**. Pass-1's M3 shape recurring inside the fix for pass-2's highest finding | resolved — split into dependency-free Issue **0.0a** (pre-hoc, publishes the free-id list) and 0.9 (post-hoc sweep). SC0 added |
| L1–L7 | low | `index.md` dirs; SC12 vacuous (Tests already match the regex today); SC40 already passes; `references/*` stated 194/191/183; `2.5 depends-on 2.6` and `6.10 < 6.2` are extractor hazards in the plan that builds the extractor; ML008 on the Upstream table; `log.md` blank line | all resolved — SC12 now asserts the scripts exist and are piped through `jq -e`; SC40 becomes a before/after pair; counts reconciled; L5's two hazards added as explicit Issue 5.2 test cases |

## Strengths

- **Every stated count matches the parse.** 0 duplicate ids, 0 cycles, 0 backward-epic edges,
  **0 cut violations** — nothing in Epics 0–5 depends on 6–10, so D-13's split point is genuine.
- **Issue 1.4's placement is correct and non-obvious** — it precedes Epics 2 and 3, so every gate
  script *can* be run against a tree where it should be red; and Issue 0.6, which pins
  `fingerprints_moved`, precedes 1.4.
- **All four gate Conditions are reachable with a producing issue.** No Condition depends on
  evidence inside its own `Blocks` set.
- **`Resolved By` round-trips exactly** against the parsed `resolves-upstream:` annotations, which is
  what `_verify_row` reads — so SC38 is enforceable.
- **Premises re-verified by execution:** `update-status approved` exits 0 while `ready-check` is red;
  FAST on `docs/plans/**` → `commands: []`; `SKILL.md:365-420` contains `**Phase log:**`;
  `coverage.rs:182` reads `../SPEC.md`; 226 clauses; 30 no-index bundles. All nine spot-checked
  `file:line` citations resolve.
- **39 of 43 criteria genuinely fail against the pre-work tree — above the repo's historical bar.**
  All four exceptions were in content pass 2 added or rewrote.

## Missing

1. ~~An issue that files the coarse tracker~~ — **done at drafting**: #175 filed and written into
   the row. Issue 10.5 remains the close-time confirmation.
2. **A rule distinguishing "red because the capability is absent" from "red because the harness
   broke."** The H1→N4→H2 sequence is three consecutive cycles of a gate failing for a reason
   unrelated to what it measures. That is the recurring root cause and the plan has no rule for it.

## Gate Assessment

All four gates BROKEN today at exit 127 (scripts absent, authored by 1.4), **correctly placed**, and
now internally consistent — each `Instructions:` names the epic that satisfies it, and the `jq -e`
assertion sits in the `Test:` rather than inside the script. Reachability: no cycles; no frontloading
miss; each gate sits at the earliest position its evidence permits.

## Upstream Assessment

Dispositions sound (5 `partial` OPEN, 2 `include` close, 4 `exclude`). `Resolved By` is
generated-correct. Two gaps at pass time: the tracker row shape (H3), and — noted — **`verify-reconcile`
returns `inconclusive` on tracker rows and never fails, so SC38 stays green with the tracker
broken**, exactly as pass 1 warned.

## Operator note

`ls reviews/pass-*.md | wc -l` reaches **4** with the next pass — **D-13's mechanical split trip
condition fires at that point.**

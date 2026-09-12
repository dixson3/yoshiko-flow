---
type: Finding
okf_spec: OKF-PLAN
description: "REQ-LAND is a coherent core of ~22 behaviours wrapped in ~48% defect narrative; 2 ids (015 gate-close half, 018 re-preview) describe behaviour that does not exist; prune to 22 ids / ~300 lines by merge and compression, not deletion"
plan: plan-071-james-dixson-d19ce8
experiment: EXP-001
date: 2026-09-10
---
# EXP-001: Is REQ-LAND-001..038 a coherent design or an accreted patch log?

Read-only measurement by a dispatched investigator (main session wrote this file).

## Approach Tested

Read-only measurement over the repository by a dispatched investigator: enumeration by `grep`, per-id reference counts, code reads at cited line numbers, corpus runs bounded by `timeout`, and sandbox controls under `$(mktemp -d)` (removed). Every claim is tagged **measured:** (command run) or **inferred:** (reasoned).

## Result

**Id set.** **measured:** `grep -o 'REQ-LAND-[0-9a]*' skills/yf-plan/spec/landing.md | sort -u` yields 001–038 plus 017a. **No REQ-LAND-039 exists anywhere** (`grep -rn REQ-LAND-039 skills/yf-plan SPEC.md` is empty; plan-070 allocates it but has not landed). 027 is a reserved hole. 39 ids, 38 with normative text.

**File shape.** **measured:** 760 lines. Only **8** are `>` blockquote lines, so the "amendment log" is *inline bold paragraphs*, not blockquotes. Line categoriser: `req_statement 141 · rationale 99 · verification 48 · amend/measured 33 · other prose 233 · table 52 · blank 131`. **inferred:** normative "shall" text is **19%**; rationale + amendment + argumentative prose is **48%**. Per-REQ block lengths: 037 = 103 lines, 004 = 57, 006 = 41, 002 = 39, 038 = 36, 030 = 34.

**Accretion history.** **measured:** `git log -- skills/yf-plan/spec/landing.md` → 10 commits: plan-060 ×2 (001–026, 017a), plan-062 ×1 (028/029), plan-063 ×2 (030–036), plan-068 ×5 (037/038 + amendments to 002/004). **plan-069 and plan-070 never touched the file.** The accretion is 4 plans, 12 post-060 ids.

**Citations.** **measured:** 23 of 38 blocks cite a `#NNN`; 31 carry a `Rationale:`; 002/004/036/038 carry `Amendment`/`Measured` sub-paragraphs.

**Tests.** **measured:** every Verification-named test function exists (36/36 `def` hits). No id is UNTESTED by that standard, though 005/007/023 have zero id-string mentions in code.

**Two ids describe behaviour that does not exist.**

- **REQ-LAND-015** (route record on apply AND on every gate close): **measured:** `route_record` write sites are only `plan_manager.py:8804` (tty refusal envelope) and `:9205` (landing journal); `resolve_start_gate` (6356–6520) writes none. `gh issue view 393` is OPEN and states the same. Reader `_land_route_record_findings` (6796) exists; writer does not.
- **REQ-LAND-018** (re-preview immediately before merge): **measured:** digest check is at apply entry (8588–8608), before L0; `_land_l2_merge` contains no digest/preview/stale check. **inferred:** staleness is caught only because the digest includes `predicted_tree`.

**Step-order divergence.** **measured:** `LAND_EXECUTOR` has **15** keys (l0–l7, `l8_close_chain_head → _land_l8_to_l15_close_chain`, `l12_close_cascade`, `l13_complete_gate → _land_l13_l15_finish`, l16–l19); spec says "twenty steps". Order preserved; L8–L11 and L13–L15 folded. `_land_l8_to_l15_close_chain` is misnamed (L12/L13 have separate keys). `LAND_STEP_JOURNAL` has 12 entries; the 3 unjournaled keys match 029's list.

**L2 in-place.** **measured:** `_land_l2_merge` (9648) still runs `git pull --rebase` with the return code unchecked, matching the 004 amendment's recorded fact. plan-069 was to take it and has not landed.

**Text duplicates.** **measured:** 025 ≡ 004-L8 row (same `HEAD^1..HEAD`, same #303). 005 ≡ 004-L6 row. 007 repeats 006 §3.2 row 4. 009 repeats 006 ¶2. 036's two "Amendment to" paragraphs (612–620) restate 002 and 011 already patched in place at 37–39 and 230.

## Classification table

| id | class |
| :-- | :-- |
| 001 006 010 013 014 017 019 026 035 | LOAD-BEARING, keep verbatim |
| 002 004 008 011 017a 020 021 022 023 024 029 030 032 033 034 036 037 038 | LOAD-BEARING, compress or merge |
| 003 005 007 009 025 | RESTATEMENT (of 002/026, 004-L6, 006, 006, 004-L8) |
| 012 | half RESTATEMENT of REQ-CLI-021 + blockquote PATCH-LOG |
| 016 027 028 031 | PATCH-LOG (016 has no "shall"; 027 reserved hole; 028 pins #327's seam; 031 wraps one rule) |
| 015 | UNIMPLEMENTED (gate-close half; #393) |
| 018 | UNIMPLEMENTED as worded |

## Implications for Plan

**inferred:** the set is a **coherent core (~22 behaviours) wrapped in ~48% defect narrative**. Pruning is compression and merging, not deletion of behaviour. 015 and 018 must be rewritten to what exists (or implemented) before a freeze, otherwise the freeze locks in a spec-vs-impl disagreement.

## Recommendations

Proposed pruned set: 22 ids, ~280–320 lines.

- **Keep verbatim (9):** 001, 006, 010, 013, 014, 017, 019, 026, 035.
- **Merge (11 → 5):** 002+003+018+036 → facts re-derived + digest coverage table; 004+005+025 (+ L1 explicit-checkout clause from 002) → the order table with those facts as row text; 006+007+008+009 → one journal requirement; 011+029 → one resume requirement; 032+033 → one L16 requirement; 023+031 → one L18 requirement; 024+034 → one dry-run-halting-findings requirement.
- **Rewrite as forward requirements (8):** 012, 017a, 020, 021, 022, 030 (~8 lines), 037 (~20 lines, keep the `DERIVED:` fence — `test_land_seam.py:249` parses it), 038 (~6 lines).
- **Delete (3):** 016 (move to #304), 027, 028 (fold "`--apply` invokes `_land_execute`" into 010; keep `test_seam_reaches_executor`).
- **Decide (1):** 015 — narrow to the two stamps that exist, or implement the gate-close stamp. plan-070 Epic 3 claims the implementation; if plan-070 lands first, keep; otherwise narrow. **Plan decision (pass-3 C4): 018 is absorbed into the group-1 merge, not rewritten as a survivor; the rewrite list above therefore excludes it.**
- State "20 logical steps, 15 executor keys" once; rename `_land_l8_to_l15_close_chain` to its actual scope.
- Correct the plan premise: only 060/062/063/068 touched `spec/landing.md`.

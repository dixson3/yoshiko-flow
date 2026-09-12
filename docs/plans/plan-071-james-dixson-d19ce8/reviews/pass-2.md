---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 2, reading] REVISE — chain property: 12 of 13 pass-1 resolutions real, one half-applied (attest-validation deleted and retained); REQ-LAND merge map reaches 24 not 22; 6 concerns (1 high, 1 medium-high, 1 medium, 3 low)"
plan: plan-071-james-dixson-d19ce8
pass: 2
mode: reading
---
# Plan Red-Team: plan-071-james-dixson-d19ce8

## Verdict: REVISE
**Mode:** reading

## Chain property (pass-1 resolutions vs plan.md)

| Concern | Claimed | Verified (measured: grep plan.md) | Verdict |
| :-- | :-- | :-- | :-- |
| C1 | D-10 withdrawn; 4.2 → test for `attest-validation`; grep-needle rule; #392 In-list | L191 `D-10 (revised at pass 1, C1)`, L246 4.2 rewritten, L197 `^deliverable_class:`, L72 #392 row | **partial** — L244 Issue 4.1 still deletes `attest-validation` (see C1 below) |
| C2 | `gate-consistency` kept; removed from 4.1/SC15 | L250 "verb wrapper is **kept**"; L244 and L330 omit it | real |
| C3 | 4.4 separates no-gates/none-evaluable; 2.4 runs engine at `ready-check` | L250 two facts; L230 "runs `gate_consistency.py` over the bundle" | real |
| C4 | SC1 = 31 with arithmetic in SC1 and 0.3 | L211, L315 both state `41 − 7 − … = 31` | real (arithmetic wrong, C1) |
| C5 | `landing-halt:` bullet in `log.md`; D-4/1.2/1.3 rewritten | L165–170, L218, L220 | real |
| C6 | 070 gate blocks 0.4/3.2; 039 folded; 3.2 delete branch removed; R1 rewritten | L277 gate; L212 "039 folds into 004 L6"; L238 no delete branch; L302 | real |
| C7 | SC14 `manual:` + SC14b; timeout 60s | L328, L329, L248 "300s to 60s" | real |
| C8 | SC11 via `test_close_contract.py` | L325 | real |
| C9 | `_*`/`__pycache__` excluded; imported-by-wired counts | L252, L326 `[!_]*` | real |
| C10 | invocation-form leg; 5th control; R7 | L254, L190, L308 | real |
| C11 | 1.2 runs `recheck-criteria --json` itself | L218 | real |
| C12 | R4 low; flips noted | L305 | real |
| C13 | SC9 notes explicit brief in `log.md` | L323 | real |

12 of 13 fully present; C1's resolution is half-applied — the #306 class the brief asked for.

## Strengths
- Every pass-1 edit except one is in the file; the plan-070 gate is decidable today (measured: gate test exits 1; plan-068's landed `plan.md` spells `status: complete` at frontmatter line 10, so the `^status: complete$` grep will match once 070 lands; `2>/dev/null` covers the untracked-070 case cleanly).
- `landing-halt:` is safe: `_plan_review_line_count` (plan_manager.py:5512) keys only on `review-pass:`/`review:`, and `intake:`/`validated:` are documented inert precedents (spec/data.md REQ-DATA-012/016). No audit parser rejects unknown tokens.
- `_verification_clause_ok` exists (doc_lint.py:1015); all seven test files the gates and SCs name exist.

## Concerns
| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **`attest-validation` is both deleted and retained.** measured: L244 Issue 4.1 "Delete the seven dead verbs (… `attest-validation`)"; L246 Issue 4.2 "Give `attest-validation` a test"; L198–200 D-10 says operator-offered remediation verbs have a live call path. SC1/0.3 count it among "7 dead" (→31); SC15's regex omits it (consistent with survival). Pass-1 C1's resolution cell describes an edit 4.1 never received — a phantom half-resolution. If it survives, a correct tree has 32 verbs and SC1 is red. | Remove `attest-validation` from 4.1 (six dead verbs); set SC1 and REQ-PLAN-086 to `41 − 6 − 3 = 32`; keep SC15 as is. |
| C2 | medium-high | **Issue 0.4's merge map cannot reach ≤22 ids.** measured from L212: 39 ids today (`grep -o … \| sort -u` → 39 real + 1 bare-prefix hit); delete 3 (016/027/028); seven merge groups absorb 19 ids into 7 (006 is also in the verbatim list) → 12 absorbed; survivors = 39 − 3 − 12 = **24**. EXP-001's "merge (11 → 5)" label is inconsistent with its own seven listed groups. SC2 and REQ-PLAN-086's 22 are false by construction; amending them post-approval is exactly a `sc_flipped_post_approval` event. | Either raise both ceilings to 24, or add two merges (e.g. 023+031 and 024+034 into 004's order table) and restate the arithmetic in 0.4 the way 0.3 does for verbs. |
| C3 | medium | **Issue 3.2's `ready-check` option turns a bd-free gate into a bd consumer.** measured: `ready-check` spans plan_manager.py:7843–8672 with zero `bd`/`shutil.which` hits; `_land_route_record_findings` (6796) returns INCONCLUSIVE when `bd` is not on PATH and reads the epic from bd. Its only caller today is `audit-close` (6967, inside 6911–7008). | Drop the `ready-check` alternative; relocate to `land --dry-run` facts, which already call `_land_epic_from_bd`. |
| C4 | low-medium | **`parked` and `judgement-never-fired-report` have live callers the deleting issues do not name.** measured: SKILL.md:1962 and :1977 run `plan_manager.py parked --json` (status nudge + land-the-plane check); SKILL.md:1705 runs `judgement-never-fired-report`; `LAND_CLOSE_CHAIN` row at 9917. The ceiling is not wrong — merging is fine — but 4.1/4.3 name no SKILL.md edit, and `check-provably-necessary` checks verb→caller, never caller→verb, so a stale SKILL.md call would pass it. | Name the SKILL.md lines in 4.1 (→ `list --parked`) and 4.3 (→ `retrospective-report`); 4.7's SKILL.md-order assertion covers the chain row only. |
| C5 | low | SC2/SC3's regex `REQ-LAND-[0-9]*[a-z]*` matches the bare `REQ-LAND-` prefix. measured: 40 vs 39 today — one slot of a zero-slack budget. | Use `[0-9]+[a-z]*`. |
| C6 | low | Issue 2.5's "web count checks" is `scripts/checks/check_web_counts.py`: `FORMULA_COUNT_RE` (line 60) compares a word-number claim to `len(census["formulas"])` over `skills/*/formulas/*.formula.toml` (5 → 3). measured: `web/content/pages/formulas.md:61` reads "## The five shipped formulas". | Name the file and line in 2.5 so the executor changes "five" to "three". |

## Missing
- No `inferred:` premise survives that an SC depends on, except D-7's "22 ids" — which C2 shows the plan's own map contradicts.
- Gate deadlock: plan-070's R2 records that its reconcile gate is the #388 instance and gives a hand-resolution path (plan-068 precedent). inferred: no hard deadlock; the 071 gate's Instructions could cite that path.

## Gate Assessment
- **allocated REQ ids free** — unchanged, reachable, ONE-SHOT.
- **plan-070 has landed** — decidable at execute start (measured above); form matches the corpus (`status: complete` ×68 in frontmatter); correctly frontloaded; blocks only 0.4/3.2. No cycle.
- **baseline suite green** — `Blocks` now covers 2.5/4.5; files exist. Fine.
- **Reconcile** — R5 acknowledged.

## Upstream Assessment
Unchanged from pass 1 and sound; #325 and #392 rows carry the pass-1 adjustments. No new disposition needed. C1 is a further #306 instance worth a note in that row's In-list.

The three high/medium-high items are numeric and local (one issue list, two ceilings, one sentence in 3.2); pass 3 should be execution-only per D-3.

## Resolutions

**Status: all 6 resolved by the main session on 2026-09-10; the Missing-section gate note added to the plan-070 gate Instructions. Pass 3 is execution-only per D-3.**

| :-- | :-- | :-- | :-- | :-- |
| C1 `attest-validation` is both deleted and retained | high | `attest-validation` removed from Issue 4.1 (six dead verbs); SC1 and REQ-PLAN-086 arithmetic set to 41 − 6 − 3 = 32; #392 row notes this #306 instance | `main-session` | `resolved` |
| C2 Issue 0 | medium-high | Two more merges added (023+031 → the 004 order table's L18 row; 024+034 → 026 as one dry-run contract); 0.4 now states the arithmetic 39 − 3 deleted − 14 absorbed = 22; D-7 wording matched | `main-session` | `resolved` |
| C3 Issue 3 | medium | 3.2 relocates the reader to `land --dry-run` facts only; the `ready-check` alternative is dropped | `main-session` | `resolved` |
| C4 `parked` and `judgement-never-fired-report` have live callers the deleting issues do not n | low-medium | 4.1 names SKILL.md:1962/1977 (→ `list --parked`); 4.3 names SKILL.md:1705 (→ `retrospective-report`) | `main-session` | `resolved` |
| C5 SC2/SC3's regex `REQ-LAND-[0-9]*[a-z]*` matches the bare `REQ-LAND-` prefix | low | SC2/SC3 regex tightened to `REQ-LAND-[0-9]+[a-z]*` | `main-session` | `resolved` |
| C6 Issue 2 | low | 2.5 names `scripts/checks/check_web_counts.py` FORMULA_COUNT_RE and `web/content/pages/formulas.md:61` ("five" → "three") | `main-session` | `resolved` |

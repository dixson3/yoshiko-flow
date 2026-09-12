---
type: Finding
okf_spec: OKF-PLAN
description: "Of 40 leaf verbs, 7 have no live caller and 3 live ones cannot fail by construction; exit 2 never halts in L8-L11; recheck-criteria IS a working oracle (71% of 515 criteria evaluated at --timeout 10; 10 completed plans FAIL) whose 300s default timeout hides that; the close chain is encoded three times with no joining test; plan-review and verify-artifact are unpoured; ~1,150 lines deletable"
plan: plan-071-james-dixson-d19ce8
experiment: EXP-002
date: 2026-09-10
---
# EXP-002: Which verbs and checks are dead, vacuous or duplicated?

Read-only measurement by a dispatched investigator (main session wrote this file). Standard applied: **provably necessary** = (a) a live call path from `SKILL.md`, `agents/*.md`, the land executor or `CHANGE-VALIDATION.md`, **and** (b) a test that can make it fail on a fixture.

## Approach Tested

Read-only measurement over the repository by a dispatched investigator: enumeration by `grep`, per-id reference counts, code reads at cited line numbers, corpus runs bounded by `timeout`, and sandbox controls under `$(mktemp -d)` (removed). Every claim is tagged **measured:** (command run) or **inferred:** (reasoned).

## Result

**Verb inventory.** **measured:** 41 `@cli.command` registrations in `plan_manager.py` (10,649 lines).

| class | verbs | evidence |
| :-- | :-- | :-- |
| DEAD (no caller outside tests/spec) | `ownership-report` (L3100, 5× `sys.exit(0)`), `escalation-report` (L7533; `_escalation_report()` already consumed by `judgement-never-fired-report` L6681), `verify-beads` wrapper (L3247), `gate-consistency` wrapper (L3273), `index-add` (L2069), `judgement-echo-check` (L7661), `grant` + 3 helpers (L2930, 259 lines), `attest-validation` (L2488; its one SKILL.md hit is inside an `echo` string at SKILL.md:1833) | `grep -rl <verb>` excluding pm/tests returns only `spec/cli.md` and old plan docs |
| LIVE but ADVISORY, cannot fail | `audit-close` (L7007 `sys.exit(0)` "ALWAYS exits 0"; wraps the same `_audit_plan` engine as `audit`/`ready-check`), `retrospective-report` (no `sys.exit`; `"advisory": True` L7194), `judgement-never-fired-report` (L6717 `raise SystemExit(0)` "always 0. Not conditional"), `classify-deliverable` (no exit path L2478-2487) | quoted lines |
| LIVE, no test | `json-get`, `triage`, `record-epic`, `resolve-start-gate` (SKILL.md:1231), `retrospective-append` | tests column 0 |
| DUPLICATE | `parked` vs `list` filter (L1610/1646 already carry `parked`) | |
| LIVE | the remaining 23 | |

**Close chain.** **measured:** `LAND_CLOSE_CHAIN` (L9914-9922) marks `audit-close`, `retrospective-report`, `judgement-never-fired-report`, `classify-deliverable` `halting=False` and `close-reconcile-step`, `verify-reconcile`, `recheck-criteria` `halting=True`. In `_land_l8_to_l15_close_chain` (L9925-9973) **`rc == 2` never halts for any verb** (L9951-9956 `halting=False ... continue`). L3 INCONCLUSIVE → non-halting; **L5 `_land_l5_advisory_recheck` reports `"pass"` regardless of `proc.returncode`** (L9772-9793); **L14 `pour_fidelity` rc 2 → `halting=True`** is the only place INCONCLUSIVE halts.

**recheck-criteria over the recent corpus** (`timeout 60`, `--json`):

| bundle | exit | verdict | evaluated / rows |
| :-- | --: | :-- | :-- |
| 060, 061, 063, 064, 065, 067 | 124 | **timed out at 60s** | — |
| 062 | 1 | FAIL (1 FALSE) | 19 / 23 |
| 066 | 0 | PASS | 26 / 27 |
| 068 | 2 | INCONCLUSIVE | 0 / 16 |
| 069 | 2 | INCONCLUSIVE (no SC table) | 0 / 0 |
| 070 | 2 | INCONCLUSIVE | 0 / 15 |

**measured:** 6 of 11 exceed 60s; of the 5 that finish, 3 evaluate zero criteria. The `evaluated == 0` arm is `sys.exit(2)`, which never halts a landing. **inferred:** L11's "authoritative halting run" is nominal on most of this corpus, and the verb runs **twice per landing** (L5 + L11).

**Formulas.** **measured:** `grep -rn 'mol pour\|mol wisp' SKILL.md agents plan_manager.py` → `pour plan-execute` ×1, `wisp plan-investigate` ×1. **`plan-review` and `verify-artifact` have zero callers.** Repo-wide hits: `web/` diagrams, `README.md`, `plan066/067_checks.py SHIPPED_FORMULAS`, `test_judgement_trigger.py` (ctl-270-seam), `test_retrospective_fields.py KNOWN`.

**Siblings and repo checks.**

| script | verdict |
| :-- | :-- |
| `gate_consistency.py` (188) | **VACUOUS on 0 gates**: sandbox plan with no gate rows → `{"verdict":"PASS","gates":0}` exit 0 (measured); `test_gate_consistency.py:109` locks that in. **Not vacuous on real plans**: FAIL on plan-068 (4 findings) and plan-070 (3). Consumed by nothing on a live path, so plan-068 landed with 4 gate findings. |
| `_gate_is_resolved` L6278 / `close_cascade._bead_is_terminal` L175 | forward-compat arms unreachable: `bd show <gate> --json` keys have no `gate_status`/`resolved`; 0 hits over 109 gates in `issues.jsonl`. **plan-070 Epic 4 owns this (#394).** |
| `_land_route_record_findings` L6796 (119) | reader with no writer (#393); only `if not rr: continue` is reachable. **plan-070 Epic 3 claims the writer.** |
| `repair_dangling_epics.py` (189) | no caller anywhere |
| `manifest_update.py` (136) | SKILL.md:216 only, no test |
| `scripts/checks/*.sh` (17) + `check-assets-decided.py`, `check-backfill-audit-delta.py`, `check-description-coverage.py`, `check-index-boilerplate-ratio.py`, `plan066_checks.py` | not in `CHANGE-VALIDATION.md`, `.github`, Makefile or justfile (grep 0); referenced only by `harness-selftest.sh` and specs |
| `check_gh_direct.py` (yf-beads-upstream) | 3 of 6 `FORBIDDEN_SUBSTRINGS` vacuous (#281 confirmed by sandbox). **Other skill; out of scope here.** |

Test negativity: `test_gate_consistency.py` and `test_verify_beads.py` do exercise FAIL arms of the engines; no test drives the pm wrapper verbs; `test_audit_close.py` asserts exit 0, never a halt.

## Implications for Plan

Under the retention standard: 8 verbs fail (a) outright; 4 live verbs plus L5 cannot fail. `gate_consistency.py` is the inverse case: a real detector with no live consumer. The landing's criterion gate is mostly nominal on this corpus and costs >60s twice per land.

## Recommendations

- **DELETE** (~600 lines pm + ~190 sibling): the 8 dead verbs and helpers; `repair_dangling_epics.py`; unwired `scripts/checks/*`; `plan-review.formula.toml` + `verify-artifact.formula.toml` (and their `SHIPPED_FORMULAS`/`KNOWN`/ctl-270-seam references).
- **MAKE HALTING OR DELETE**: `_land_l5_advisory_recheck` (delete; L11 is the only run); `audit-close` (same engine as `audit`; delete from chain and verb); `gate_consistency.py` 0-gates → exit 2 (#325) **and add to `LAND_CLOSE_CHAIN` halting**; the chain's `rc == 2` handling for halting verbs → halt; `recheck-criteria evaluated == 0` → a plan defect at `ready-check`, not a warn at L11.
- **MERGE**: `parked` into `list`; `judgement-never-fired-report` into `retrospective-report` (one advisory report, which Epic 1 makes carry the fidelity metric).
- **Leave to plan-070**: `_gate_is_resolved` collapse (#394), `route_record` writer (#393).

## Second measurement (the original investigator, wider corpus, `--timeout 10`)

The first run used a 60s **whole-verb** bound and saw 6 of 11 bundles time out. The second run set `recheck-criteria --timeout 10` **per criterion** over all 22 `plan-05x/06x/07x` bundles:

| verdict | bundles |
| :-- | :-- |
| INCONCLUSIVE (exit 2) | 6 — 050, 051, 068, 069, 070, 071 |
| FAIL (exit 1) | 10 — 052, 053, 054, 056, 057, 059, 062, 063, 064, 065 |
| HARNESS_INCOMPLETE (exit 1) | 4 — 055, 061, 066, 067 |
| PASS | 2 — 058, 060 |

**measured:** 515 criteria, 396 class-A, **364 evaluated (71%)**. The default `--timeout 300` *per criterion* is what made the first pass hang on plan-054.

**Correction to the first table's implication:** `recheck-criteria` is a **working oracle**, not a nominal one. What is defective is (a) the exit-2 arm never halting at L11, (b) the 300s default, and (c) **ten completed plans whose criteria are FALSE today** — post-completion rot or noisy criteria (which of the two is uncorroborated). The code comment "INCONCLUSIVE on 51/52 bundles" is stale for this slice.

Other additions from the second run:

- **measured:** the close chain is encoded **three times** — SKILL.md §6.4's bash block, `LAND_CLOSE_CHAIN` + `_land_l12`/`_land_l13_l15`, and `land_rehearsal.py:162 _REHEARSAL_PM_VERBS`. `test_close_contract.py` parses SKILL.md; `test_land_apply.py:968` checks the table; **no test joins them** (#392's double-enumeration, in triplicate).
- **measured:** `gate_consistency.py` skips any gate whose `Blocks` has no issue-kind member (`check_plan:67 if not blocks: continue`): 99 gates over 22 bundles, **54 skipped**; plans 065, 069, 071 report `PASS` with zero evaluable gates.
- **measured:** **three yf-plan test files run nowhere** (`test_escalations.py`, `test_judgement_trigger.py`, `test_severity_vocabulary.py` are in no CV row or CI).
- **measured:** `harness-selftest.sh` and the 16 checks it wraps have no caller in CV, CI or scripts; six further `check-*.sh` have no caller at all.
- **measured:** `check_gh_direct.py` — **5 of 6** `FORBIDDEN_SUBSTRINGS` unreachable (string tokens are blanked before matching); `FORBIDDEN_NAMES` works. Out of scope here (#281).
- **measured:** `_gate_is_resolved` forward-compat arms and `close_cascade._bead_is_terminal:182-189` are duplicates kept "identical in meaning" by docstring, no drift guard. plan-070 owns the collapse.
- nuance: `clear-epic` and `attest-validation` are **offered as operator remediation** in SKILL.md text rather than invoked; the first investigator classed `attest-validation` dead, the second "live-by-offer". D-10 resolves it on corpus evidence.
- Tier-1 estimate revised to ~1,150 lines (adds `verify_beads.py` + test, `repair_dangling_epics.py`, the caller-less `.sh` files, the route-record reader closure at 178 lines).

Sandbox residue: none (both investigators).

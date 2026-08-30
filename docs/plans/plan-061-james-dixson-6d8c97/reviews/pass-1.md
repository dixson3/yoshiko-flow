---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 1 on plan-061 — verdict REVISE with 10 concerns, 4 high. Both capability gates were unsatisfiable as written and all 12 success criteria were unexecutable prose; the plan''s cited figures re-derived correctly.'
---
# Review pass 1 — adversarial (red-team)

## Verdict: REVISE

**all 10 concerns resolved by the main session; re-dispatched as pass 2**
**Dispatched:** sub-agent (REQ-AGENT-049), read-only w.r.t. the repository; sandbox spike authorized.
**Date:** 2026-08-30

## Strengths

- **The plan's figures hold up.** Five of six re-derived independently and match: SPEC.md omitted
  from **12** READMEs; stale unprefixed fence roots exactly **10** (`yf-beads-init:136`,
  `yf-beads-upstream:91`, `yf-diagram-authoring:127`, `yf-drift-check:71`,
  `yf-markdown-format:159`, `yf-markdown-html:132`, `yf-markdown-lint:132`,
  `yf-markdown-pdf:137`, `yf-optimal-instructions:69`, `yf-skill-authoring:43`); ASCII-tree
  fences **10 of 19**, non-tree **9**, and Issue 2.2's named nine are *exactly* the nine
  measured; `document_types` = **19** `.toml`; 19 READMEs of 20 skills. Given #289 this is the
  right standard.
- SPEC-first Epic 0 → checker → red-run sequencing is the correct shape.
- The `yf-judgement` row (`plan.md:120`) — refusing to document a skill that does not exist.
- R1/R3/R5 are real risks with real mitigations; the scope-split deferral is honest **and was
  verified**: `exp-001`/`exp-004` contain no material this plan acts on beyond the `install.sh`
  half correctly routed to Epic 4.

## Concerns

| # | Severity | Concern | Recommendation | Actor | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| C1 | high | **The sensitivity gate is vacuous.** Spike-measured: an uncaught exception exits **1**, and an unresolvable PEP 723 dependency exits **1**. So a checker that *crashes* satisfies `test $? -eq 1`, resolves the gate and unblocks epic:2 having read nothing. The gate certifies the failure mode it exists to exclude — #181/#207/#263's conflation one layer up, in the plan whose Issue 1.3 exists to fix exactly that. (`$?` itself is fine; no pipeline.) | Gate on the **verdict**, not the exit code: capture `--json`, assert `verdict=="FAIL"`, `skills_enumerated>=20`, `failures>=18`. A crash emits no parseable JSON and fails closed. | **RESOLVED.** Gate 1 now captures `--json` and asserts `verdict=="FAIL" and skills_enumerated>=20 and (failures|length)>=18` via `jq -e`. A crash emits no parseable JSON, so it fails closed. | `main-session` | `resolved` |
| C2 | high | **SC9 × Issue 1.2 × SC2 is a three-way contradiction.** Issue 1.2 has the checker assert README **and web-page** existence — imported from `exp-002:99`, written under the *combined* scope. SC2 demands exit 0 at `--min-skills 20`; SC9 forbids touching `web/`; #317 owns `web/`. `yf-okf-hygiene` is the only skill without a page. **The plan cannot complete as written.** | Delete the web-page half from Issue 1.2; state the carve explicitly (README half only; the artifact-completeness pair lands in #317). | **RESOLVED.** The web-page half is deleted from Issue 1.2, which now states the carve explicitly: README axis only, `web/` belongs to #317. | `main-session` | `resolved` |
| C3 | high | **The install.sh gate is wrong in both directions.** Verified independently by the main session: the Test returns **26**, not 0. *Over-match:* 8 git-tracked archived bundles plus this plan's own `plan.md:82` — SC5's "zero tracked files" would demand rewriting plan history. *Under-match:* only 13 of 17 READMEs use the "repo-level" phrasing; the 4 misses are the worst — `yf-beads-authoring:24` and `yf-beads-extra:22` carry a bare `./install.sh`, and `yf-plan:59-62` / `yf-research:28-31` each teach **four runnable** `./install.sh` invocations. The gate goes green while those keep teaching a command for a script that does not exist. | Scope the path set to `skills/*/README.md DRIFT-CHECK.md README.md` **and** broaden the pattern to catch bare `./install.sh`. Prefer a `scripts/checks/` script with C1's JSON-verdict treatment. Amend 4.2: 13 prose + 4 command-block instances need *different* repairs. | **RESOLVED.** Verified independently (26 unscoped). The Test is now scoped to `skills/*/README.md skills/*/SKILL.md README.md DRIFT-CHECK.md` and broadened to catch bare `./install.sh` — **25 files, and satisfiable**. Issue 4.2 now names the two populations; new Issue 4.2b covers the `SKILL.md` residue. | `main-session` | `resolved` |
| C4 | high | **0 of 12 success criteria are machine-checkable.** Verified independently: `recheck-criteria` returns `total 12, class_a 0, evaluated 0` — all `prose`. §6.4 takes the WARN branch, so completion gates on nothing. The plan adopts #149's *"a step with no exit code is not a step"* and argues from #273 that prose obligations are skipped — then ships 12 prose criteria. | Convert SC2/SC5/SC6/SC7/SC8 to the REQ-DATA-070 clause grammar. **Keep SC1 an artifact claim** (`test -f <red-run>.md`) — a live SC1 is false at completion by construction (plan-051 SC4b shape). | **RESOLVED.** Verified independently (`class_a 0`). Criteria rewritten: **10 clause-form, 2 first-class `manual:`** — `recheck-criteria` now reports `class_a 10, evaluated 10`. SC1 is an artifact claim (`test -f`), never a live run, per the plan-051 SC4b argument. | `main-session` | `resolved` |
| C5 | medium-high | **Gate 1 manufactures a false blocker at the §5.2c sweep.** Measured: `uv run <nonexistent>` exits **2**, so the composite exits 1; `coordinator.md:183` maps non-zero to FAIL. The sweep runs before any coding work — when the checker does not yet exist. The operator gets a FAIL whose Instructions say "repair the checker", which is actively wrong: there is nothing to repair. | Add an existence guard yielding a distinguishable state; amend `Instructions:` to name the not-yet-built case. | **RESOLVED, but NOT as recommended — the recommendation rested on a false premise.** No exit code can signal not-yet-built: `coordinator.md:180-184` maps **any** non-zero to FAIL and reserves INCONCLUSIVE for an **absent** test. A guard returning 2 would still read FAIL. The gate being red before Epic 1 is **correct** — it blocks epics 2/3, which must not start early. Fixed the actual defect: the misleading `Instructions:`, which now state the pre-Epic-1 red is expected, must not be hand-resolved, and that `test -f` buys a clean failure rather than a distinct state. | `main-session` | `resolved` |
| C6 | medium | **`Blocks: epic:2` is under-scoped.** Issues 3.1-3.4 depend only on 1.5, so Epic 3 runs in parallel and ungated — yet it is backfill too, mutating the same READMEs the checker measures. The stated ordering law binds only half the backfill. | `Blocks: epic:2, epic:3`. | **RESOLVED.** `Blocks: epic:2, epic:3`. | `main-session` | `resolved` |
| C7 | medium | **Issue 3.4 / 2.3 ordering hole.** 2.3 regenerates "all 19" fences; 3.4 authors a 20th README in a parallel epic. If 3.4 lands after 2.4, that fence is never regenerated or verified. SC4 says "19 pre-existing" while SC2 demands `--min-skills 20`. | Add `depends-on: 3.4` to 2.3 (or an Issue 2.5 re-run), and reword SC4 to cover all 20. | **RESOLVED.** Issue 2.3 now regenerates **20** fences and gains `depends-on: 3.4`; SC4 reworded to all 20. | `main-session` | `resolved` |
| C8 | medium | **The `--min-skills` floor's exit code is unspecified — and it is R1's sole mitigation.** If the floor trips at exit 1 it is byte-identical to a real FAIL, so Gate 1 passes on a zero-enumeration checker: **R1 realised through its own mitigation.** | Pin the floor to exit **2** in Issue 0.2's REQ text and 1.1, matching `check_okf_index_drift.py:36` and the REQ-DATA-057 INCONCLUSIVE→`warn` precedent. Add to 1.4's tests. | **RESOLVED.** New Issue 0.2b pins the floor to exit **2** in the REQ text; Issue 1.1 carries it; SC6 asserts it via the test suite. | `main-session` | `resolved` |
| C9 | low-medium | **The "19 schemas" figure is ambiguous.** `_shared/document_types` holds 20 entries (19 `.toml` + a `README.md`); `skills/yf-plan/scripts/document_types` holds 19 `.toml`. #244's "20" likely counted the README. | State the denominator and counting rule in the Motivation table. | **RESOLVED.** Motivation now states the denominator and why #244's 20 differs (it counted `_shared/document_types/README.md`). | `main-session` | `resolved` |
| C10 | low-medium | **`gate_consistency.py` returns `PASS, gates: 4, findings: []`** — it caught none of C1/C3/C5/C6. The plan's thesis is that undetected contract drift is the problem; its own gate instrument is blind to two unsatisfiable gates. | Not this plan's remit. Record on #315 or a follow-on bead so the blind spot is not re-discovered. Adjacent to #289. | **RESOLVED.** New Issue 5.6 files the blind spot upstream rather than fixing it here. | `main-session` | `resolved` |

## Missing

- No issue authors the checker's **`--json` schema**, yet SC2/SC3/SC2b read "the checker's
  existence class" and C1's fix requires a stable verdict shape. Add to Issue 0.2 + 1.1.
- No precondition establishes **`jq`** (or `json-get`) for the C1 gate form.
- **Epic 5 has no rollback path** if SC7's FULL tier goes red over the merged tree — and per
  `AGENTS.md` the FULL tier is the last gate before `yf self install`.
- The `install.sh` residue is **not only in READMEs** — `skills/yf-okf/SKILL.md` also matches.
  Issue 4.2 names only READMEs; 4.4 sweeps "repo-wide" with no scoped path set.

## Gate Assessment

| Gate | Reachable | Verdict |
| :-- | :-- | :-- |
| Start Gate (human) | yes | Fine. |
| Capability: checker is sensitive | **no, as written** | Passes on a crashed checker (C1); misleading FAIL at the sweep (C5); under-scoped Blocks (C6). **Placement is correct** — the defect is the Test, not the position. |
| Capability: no install.sh reference | **no** | Returns 26 today; unsatisfiable without rewriting archived bundles; simultaneously blind to 4 runnable `./install.sh` blocks (C3). |
| Reconcile Gate | yes | Standard. |

**Premise check.** The load-bearing inference — *"a checker exiting 1 proves it is sensitive"* —
is an inference, not a measurement, and was **falsified**: three distinct harness faults all
produce exit 1. The plan's own `--min-skills` argument is the same insight one level down; it was
simply not carried up to the gate that consumes it.

## Upstream Assessment

Dispositions sound. #244 full-include with superseded counts and a posted comment is right; the
#247 partial split is specific and recorded; #291 deferred with a noted body error is honest;
#273/#149 as design input is correct; #127/#104 exclusions are the operator's.

**One gap:** Issue 4.3 carries `resolves-upstream: #247 (partial)`, but the Epic-4 gate that
would prove it is unsatisfiable (C3). Do not close a partial on a gate that cannot go green — fix
the gate first, or downgrade 4.3 to a comment.

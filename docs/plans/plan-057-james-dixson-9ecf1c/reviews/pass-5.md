---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: "Red-team pass 5 — APPROVE. Zero blockers. Both of pass 4's repairs verified by execution, including a spike proving one test file satisfies both invocation paths. Six non-blocking specification clauses, all fail-red."
---
# Red-team pass 5: plan-057-james-dixson-9ecf1c

## Verdict: APPROVE

> **All 6 concerns resolved by the main session.** Zero blockers.

**Date:** 2026-08-29 · HEAD `2a1c38d` · Reviewer: delegated adversarial agent (read-only; two sandbox spikes, no residue)

Trend: **17 → 18 → 12 → 8 → 6** concerns; **8 → 6 → 2 → 2 → 0** blockers.

## Strengths

**Pass 4's two blockers verified repaired BY EXECUTION, not by reading.**

- **The `test -x … && bash …` wrapper works, and is safe post-implementation.** All four criteria run
  verbatim exit **1** — none 127 or 2. Traced through `plan_manager.py:3080-3110`: criteria run via
  `bash -c`, `&&` yields the last command's status, so a real non-zero propagates unchanged. **No case
  makes a real failure invisible.** The only added behaviour is: file present but x-bit cleared →
  FALSE rather than the script's true verdict, which is the fail-closed direction, and SC0 asserts the
  x-bit independently. The asymmetry with `uv run` targets is real, not an oversight: `uv run
  <missing>.py` → 2, which is *evaluated*, so SC3/SC8/SC12/SC17/SC19 correctly need no wrapper.
- **Issue 2.8's three-part contract SPIKED — one file satisfies BOTH paths.** A file carrying the PEP
  723 header, `import pytest` and the `__main__` runner gives `uv run` → 0 passing / **1 on
  `assert False`** (SC17 can fail), and `check-pytest-ran.sh` → 0 on a real test / 1 on a failing one
  / 1 on a missing name. No recursion, since module-form import never sets `__name__ == '__main__'`.
  **This was the specific thing that could still have been wrong. It isn't.**
- `2.9 depends-on 2.8, 1.4` parses as a real edge (29 → **30**), DAG still acyclic over 28 nodes.
- SC20's positive grep and SC21's recipe row are **red today for the stated reason** — `SPEC.md:13`
  still reads `knowledge-catalog`, and `CHANGE-VALIDATION.md` carries no `baseline-pin-drift` row.
- **Every count pass 4 corrected is now consistent** across the gate `Test`, SC0b prose, SC0b command
  and SC0's `test -x` list: 9 enumerated + 7 authored = **16**; 28 issues, 30 edges, 29 criteria,
  6 gates, `unparsed: []`.
- **Eight independent figures reproduce**, two to the digit (SC3's `126/184 · 0.6848`; SC5's five
  nested bundles). R11's `cmp` claim TRUE; `HARNESS_INCOMPLETE` 4 in both copies.
- All mechanical instruments clean: `audit` 0, `gate_consistency` 0, `doc_lint` on plan.md **and all
  four reviews** 0 findings each, `okf.py check` 0, `sync.py --check` 0, `check-req-coverage` 0.
- The producer↔consumer path check run by hand again: **all 22 path literals** resolve to a file that
  exists or is created by a named issue.

## Concerns

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | med | **`check-assess-verb-gone.sh`'s general property has a measured false positive.** `yf-okf` advertises `init check migrate assess` while `okf.py --help` dispatches `check migrate reindex scaffold` — `init` is advertised-and-undispatchable *legitimately*, because SKILL.md says only ENGINE-BACKED subcommands route to the script. A literal "every advertised verb" would be permanently red on a conforming skill — the same trap SC20 and SC23 each already dodged. Scope also disagreed between Issue 1.0 and SC23. | **resolved** — qualified to engine-backed verbs, with the measured false positive recorded, and the check now inspects both skills so the two scopes agree. |
| C2 | med | **SC0c said "the three `auto` gates"; the plan has FOUR.** The Reconcile Gate is also `Type: auto` and IS poured as a bead, so an instrument enumerating `type == auto` finds four and goes permanently red on the fourth — while hard-coding `3` reintroduces the hand-maintained number this plan exists to eliminate. | **resolved** — the discriminator `type == "auto" AND test_kind == "executable"` is now named, which yields exactly three. |
| C3 | low | `~144` (Issue 3.1) vs `~147` (SC20) vs measured **152** — two approximations of one quantity three lines apart. | **resolved** — `~150` in both, with the measured 152/150 recorded. |
| C4 | low | **The `${SKILL_DIR}` rule forbade what the plan does.** It carved out an exception for invoking an unmodified skill as a tool, then boasted "0 occurrences" — but SC24 invokes the unmodified `verify-reconcile` by repo path. | **resolved** — exception removed; the rule is now simply "repo path always", which is what the plan actually does. |
| C5 | low | `context.md` says `okf.py` is vendored into "four" trees; Issue 1.6 option (a) makes it five. | **resolved** — parenthetical added. |
| C6 | low | **SC19's `--min-roots 59` is the one-root number on a two-root command** (59 + 5 = 64). Non-vacuous, since `--require-legacy 0` is load-bearing, but loose. | **resolved** — 64. |

## Missing

- **The `plan.md` ↔ instrument-output diff** — named Missing in passes 2, 3, 4 and 5. It would have
  caught C3 mechanically. The longest-running open item across this plan's review history.
- **The producer↔consumer path check** — run by hand in three consecutive passes and clean every
  time; still not an instrument.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start | OK |
| Predecessor complete | **Sound** — directive parses in full, `unparsed: []` |
| Backfill authorization | **Sound** — `Test: none` correctly classified `test_kind: sentinel` |
| Upstream network reachable | **Sound** |
| Verification harness ready | **Sound** — red today (exit 1, "checked 9, --require 16"); evidence from 1.0, which it does not block |
| Reconcile | OK — and now correctly distinguished from the three executable-`Test` gates (C2) |

6 gates consistent, no cycles over 30 edges, no frontloading miss, no gate's evidence inside its own `Blocks`.

## Upstream Assessment

Unchanged and defensible. `verify-reconcile` → exit 1, `"4 of 6 upstream row(s) did not reach the end
state"` — expected pre-execution, discharged by 3.5. #170's two-ground `partial` still carries
EXP-006's "~100 of 1383 concepts inspected" caveat honestly.

## Why APPROVE

Both of pass 4's blockers are repaired and each was verified by **execution** rather than reading. Every
count corrected in pass 4 is consistent across all four surfaces that carry it. Eight independent
figures reproduce. The structure is clean on every mechanical instrument in the repo. The six remaining
concerns were all *specification* clauses on instruments that do not exist yet, and every one fails
**red**, never silently green — which is the direction this plan's review history has been fighting to
guarantee.

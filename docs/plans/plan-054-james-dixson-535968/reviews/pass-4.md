---
type: Review
okf_spec: OKF-PLAN
id: pass-4
description: Red-team pass 4 (fourth independent, via Agent) — plan-054
---

# Red-team pass 4

## Verdict: REVISE

**Frozen-snapshot check: PASS** — `dfc0b1438932…` at start and end.

**8 of 8 pass-3 resolutions reproduced by execution.** Every one landed.

> **Two of this pass's OWN resolution rows (C5, C6) were later found FALSE** and are corrected in
> place below. Both were composed in one edit script that aborted before writing, and both were
> recorded `resolved` without re-reading the file. Found by a systematic measured audit of all
> nine rows at the pass-5 escalation — not by pass 5, which verified C5 as reproduced. Two left residuals one
level down (C2, C3); one was fixed in wording but not yet verifiable (C4).

## Strengths

- **The "cannot fail" hunt came back nearly clean.** Across all 40 criteria, `recheck-criteria`
  reports **exactly one `holds` — SC16** — and the reviewer **defended it rather than flagging
  it**: the FULL tier is a real 28-row suite, "it still passes" is the whole claim, and Issue 2.6
  *adds* rows, so SC16 is strictly stronger after the plan than before.
- N1's fix verified by spike: bogus filter → `0 passed`, exit 0; real name → `1 passed`. The
  predicate genuinely distinguishes, and a target-agnostic invocation yields exactly one match —
  which matters because SC9's test is an integration test and SC10's is a lib unit test.
- **`anc(6.8) = 57/57`** — every issue is now an ancestor of the tag push.
- Every one of 0.6's three load-bearing claims about plan-053's harness verified against the real
  script: `_derive_manifest` exists, the pattern is exactly `ctl-[0-9]{3}-[a-z-]+`, there is no
  `verify-manifest` verb, and the `YF_TREE` default does assume `.worktrees/${PLAN_ID}`.
- Premise spot-checks accurate: 411 commits, crate at `0.4.0`, README at **zero** occurrences of
  `opencode`/`--harness`/`harness skills`, 5 formulas under `skills/`, 10 `SKILL.md` with
  `allowed-tools`, and the 19-file breakdown (11+5+1+2) exactly right.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | **The 28 `check-*.sh` criterion instruments carry no observed-RED obligation.** 0.1 is scoped to "every **control**", and 0.6 declares `assets/checks/` explicitly "criterion-only" — so the redcheck contract covers **8 of 40** criteria and the other 28 are trusted on authorship alone. **That is exactly how C5, C26 and N1 each escaped — one per pass, each caught by hand.** Nothing mechanical would have caught a fourth |
| C2 | high | **1.3's consumer set is ENUMERATED (19+4) and is measurably incomplete.** The plan learned "derive, don't count" for 1.5 and did not generalise it. **`yf-diagram-authoring/SKILL.md` uses `${SKILL_DIR}` at 8 sites and assigns it nowhere** — a shipped skill that cannot resolve its own `render.py` on ANY harness, a strictly worse instance of the defect Epic 1 exists to fix |
| C3 | med | **0.8a is a completeness check with no edges to the work it verifies** — `0.8a → 0.7` only, so it becomes ready the moment 0.7 closes and fails, because the GREEN records come from the eight fix issues. And the `assert-distinguishes` obligation is stated only inside 0.8a: an executor working 3.4 reads 3.4. Same wrong-place shape as N4, moved but not relocated to where the work happens |
| C4 | med | **N7's SPEC-first fix reached 0.7 but missed 0.8**, which authors `check-req-coverage.sh`. Compounding: **no concrete new REQ id appears anywhere in the plan**, so SC1's "asserts the SPECIFIC new ids" is unverifiable — whoever writes the check afterwards writes it to match whatever landed |
| C5 | med | **SC27 and SC28 are the worst-specified checks** — five documents' and six pages' prose-agreement collapsed into one nameless script each, satisfiable by a single `grep -q`. Runners-up: `check-deferred-filed.sh`, `check-deployed-tree.sh`, `check-stamp-agrees.sh`. `check-glossary-terms.sh` is **fine** — its ten terms are enumerated in `findings/exp-005`, which travels in the bundle |
| C6 | low | **R13's figures are stale and the seam relieves less than claimed** — 58 issues (not 57), **37** scripts (not 23). Splitting Epic 3 drops ~7 of 37. **The size is in Epic 0**, which carries the whole evidence layer |
| C7 | low | **"all 100 edges" is asserted, not measured** — `DRIFT-CHECK.md` declares **50** unique edge ids; §2 and §3 restate the same 50 |
| C8 | low | SC18 says "merged tree"; the gate, 6.7 and SC35 all say **DEPLOYED**, and 6.6a deploys after 6.6 |
| C9 | low | Issue 0.8 says `harness-smoke.sh`; SC18 names `check-harness-smoke.sh` |

## Missing

1. A red-record obligation for the 28 `check-*.sh` (C1).
2. A resolver block for `yf-diagram-authoring/SKILL.md` (C2).
3. Edges from 0.8a to its eight producers, and the obligation inside each (C3).
4. Concrete `REQ-*` ids in 0.2/0.3/0.5 (C4).

## Gate Assessment

**Unchanged and still the strongest part of the plan.** Five gates consistent; the RED gate's
`Blocks` set is a clean 1:1 onto the 8 controls with its evidence producer outside that set; both
human gates correctly placed for an irreversible, auto-publishing write; INCONCLUSIVE-blocks
agrees between gate and R8. No frontloading miss. `_derive_manifest` greps `${PLAN_MD}` only, so
review files are not scraped.

## Upstream Assessment

Unchanged from pass 3 and still sound. 23 rows, dispositions coherent, `#154 → exclude` correctly
skipped. `verify-reconcile` fails only on work-not-yet-done, which clears through execution.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Adopted as the structural fix.** Issue 0.1 extended from "every control" to **"every control AND every `check-*.sh` criterion instrument"**, recorded non-zero on the pre-fix tree, with a short explicit allowlist carrying a stated reason for any that legitimately hold. The reviewer's feasibility spot-check is recorded in the issue: no `v0.5.0` tag, crate at `0.4.0`, README at zero `opencode`, 32 hardcoded paths present, 10 `SKILL.md` with `allowed-tools` — so the checks are red today. This converts four passes of whack-a-mole into one gate. | `main-session` | `resolved` |
| C2 | high | Confirmed and **broader than reported**: `grep` found **two** `SKILL.md` files using `${SKILL_DIR}` while assigning it nowhere — `yf-diagram-authoring` (8 uses) **and `yf-skill-authoring` (4 uses)**. 1.3's set is now **DERIVED** (`grep -rlE 'SKILL_DIR' skills/`, partitioned into assign-vs-use) rather than enumerated, and both files are named. Agent files that declare `SKILL_DIR` as a caller-supplied input are declared explicitly out of scope rather than silently omitted. | `main-session` | `resolved` |
| C3 | med | `0.8a depends-on: 0.7, 1.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.4, 3.6` — the eight producers. **The obligation was relocated to where the work happens**: each of those eight issue bodies now carries its own `redcheck.sh assert-distinguishes <its fixture> <its control>` line, and 0.8a is restated as verification rather than as the obligation. | `main-session` | `resolved` |
| C4 | med | `0.8 depends-on: 0.2, 0.3, 0.4, 0.5, 0.6`, matching 0.7. Concrete ids named: **`REQ-YF-CLI-005`** (0.2), **`REQ-YF-TUNE-030`** (0.3), `REQ-YF-TUNE-022` amended (0.4), **`REQ-YF-EMBED-006`** (0.5) — each verified as the next free id in its namespace. SC1's check now has specific strings to assert. | `main-session` | `resolved` |
| C5 | med | **[CORRECTED at pass 5 — this row was FALSE when written.]** The per-issue asserted strings were composed but the edit script aborted before writing, and the row was recorded `resolved` without re-reading the file. Measured at pass 5: **zero occurrences of `Asserted` in `plan.md`**. Now genuinely applied — all **11** issues (4.3–4.8, 5.2–5.6) carry their string, and SC27/SC28 cite those issues by number so the check cannot be written weaker. Ten of the eleven strings independently measured false on today's tree, so the checks are red. | `main-session` | `resolved` |
| C6 | low | **[CORRECTED at the pass-5 escalation — this row was FALSE when written, the same aborted edit script that falsified C5.]** Audited by measurement: R13 still carried the stale `57 issues / 40 criteria / 23 shell scripts`. Now genuinely applied — **58 issues, 41 criteria, 37 scripts**, with the note that splitting Epic 3 relieves ~7 of 37 because **the size is in Epic 0**. The operator then decided against those corrected figures: **Epic 3 stays in scope**, recorded in R13's mitigation. | `main-session` | `resolved` |
| C7 | low | Confirmed independently: **50 unique `e-` ids, 100 raw rows** because §2 and §3 restate each. Corrected to "50 declared edges (52 after 5.8)" in Issue 6.6 and in R1, with the double-count recorded. | `main-session` | `resolved` |
| C8 | low | SC18 changed to **DEPLOYED**, agreeing with the gate, 6.7 and SC35. | `main-session` | `resolved` |
| C9 | low | 0.8's carve-out renamed `check-harness-smoke.sh`. | `main-session` | `resolved` |

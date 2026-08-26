---
type: Review
okf_spec: OKF-PLAN
id: pass-4
description: Red-team pass 4 (fourth independent, via Agent) — REVISE, 10 concerns, 2 high; 7 of 14 reproduced (50%), and pass-3's structural remedy was itself applied site-by-site
---

# Red-team pass 4

## Verdict: REVISE

**Recommended as the LAST PROSE CYCLE.** Every remaining item is verifiable by a supplied
command; cycle 5 should be a targeted mechanical re-check, not a fifth full pass.

## Reproduction of pass-3's 14 resolutions — 7 of 14 (50%)

| Class | Count | Concerns |
| :-- | --: | :-- |
| (a) landed and correct | **7** | C30, C34, C35, C37, C39, C41, C43 |
| (b) recorded but absent | 0 | — |
| (c) landed at one site, defect survives | **4** | C31, C32, C33, C40 |
| (d) itself a new defect | **3** | C36, C38, C42 |

**64% → 60% → 50%. The rate did not improve; it fell by the largest margin yet.**

> **The reason is measurable, and it is the finding of the pass: pass-3's structural remedy was
> ITSELF applied site-by-site.**
>
> | Literal | Retrospective claims | Measured |
> | :-- | :-- | :-- |
> | D-8's site count | removed | **removed** ✓ |
> | 3.7's "8 rows" | removed | removed at 3.7; **survives at D-5, twice** |
> | 5.1's "16 sites" | removed | **never removed** — five occurrences survive |
> | D-13's "0 of 41" | removed | removed at D-13; **survives at R7** |
>
> **1 of 4.** The `plan-retrospective.md` entry naming RE-002 against the resolution process is
> itself an instance of RE-002.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C44 | **high** | **The RED gate is UNSATISFIABLE and it blocks every fix in the plan.** 13 control names now derive from `plan.md`; only 11 have an Epic-1 builder and a RED observation. `ctl-053-full-tier-record` (SC16) and `ctl-210-suite-portable` (SC5b) are named by criteria alone — artifacts pass 3 *added*. Either `controls.txt` carries 13 and the gate Condition cannot be met, or it carries 11 and 1.1(c)'s own derivation assertion fails |
| C45 | **high** | **SC7b is unsatisfiable: C33's remedy widened the CHECK's scope and swept neither the FIX's scope nor 7.2.** `skills/*/README.md` now pulls in `yf-beads-hygiene` (7 bare invocations), `yf-beads-init` (4), and `yf-markdown-{format,lint,pdf}` (10 stale paths) — none in 3.7's `touches`. **Worse, 7.2 still FILES the markdown README paths as an out-of-scope defect while 3.6/3.7 now require them fixed.** The plan both fixes and defers the same defect. Also `skills/*/scripts/**` now selects corpus fixture documents — an FP surface EXP-003's "zero" never covered |
| C46 | medium | **`exp-004`'s correction block is MALFORMED and incomplete** — the blockquote breaks mid-sentence, orphaning a fragment; and line 163 still says "replace the **empty** `agent` target node", the exact premise the block withdraws. `exp-003`'s refuted "8 rows" carries no correction at all |
| C47 | medium | **Issue 0.1 has no downstream edge — SPEC-first is UNENFORCED for #206, the plan's CRITICAL defect.** Every other Epic-0 issue has a real implementation edge; 0.1 alone has none, so 2.1/2.2 can land before `REQ-DATA-063` is amended. It is also not an ancestor of 7.1, contradicting 7.1's own text |
| C48 | medium | **1.6 and 3.5 still direct execution at EXP-003's "existing prototype", which C32 established does not exist.** C32's remedy was applied at 1.0 and nowhere else |
| C49 | medium | **Two of 0.2's six files carry BOTH meanings of `REQ-PLAN-073`** — `SPEC.md` (roots at :239/:919, stamp at :349) and `plan_manager.py` (roots ×3, stamp at :1461). A file-scoped rename corrupts the stamp citations. 1.6c's allowlist must also include `yf-beads-upstream/{SPEC,SKILL}.md`, which no part of the plan mentions |
| C50 | low | R7 still carries "0-of-41"; measured 0 of 46. C40 named D-13 *and* R7; only D-13 was fixed |
| C51 | low | D-5 still carries the "8 rows" literal C33's resolution says was deleted — twice |
| C52 | low | The "16-site" literal was never deleted — five occurrences, including SC11b's referent, which is therefore undefined |
| C53 | low | `ctl-207-epic-state` and `ctl-208-fail-closed` have no runnable fixture — `redcheck.sh` runs `bash "$fx"`, both are specified as pytest arms |

## Strengths

- **The gate topology is now correct** — no cycles across 61 edges; the Blocks closure is
  exactly the 26 fixer issues; all 13 controls and all 7 SPEC issues sit outside it. C39 is the
  model of a resolution: structural, verified, complete.
- **C30's remedy is genuinely structural** — moving `_append` after the rc check makes an rc=2
  record *unwritable*, fixing `verify-all` and `verify-red-all` at once.
- **Every load-bearing premise independently re-measured HOLDS**: the unvendored
  `pour_fidelity.py`, `SKILL.md:1578`, the unread `epic_resolves`, the 31-verb enumeration,
  "Exactly 9", the 9 `update-status` call sites, the six roots-meaning files, `'populated from'`
  at `:989`, `okf.py`'s four consumers. **The plan's factual base is sound; its defects are all
  bookkeeping.**
- `exp-007`'s withdrawal block is a model correction. Mechanical suite fully green, orphans **0**.

## Gate Assessment

Verified programmatically over all 61 edges: no cycles, no unknown refs, Blocks closure = the 26
fixer issues exactly, every control and SPEC issue outside it. The only gate defect is the
control-inventory problem in C44 — a bookkeeping bug, not a topology bug.

## Recommendation

**REVISE, but make this the last prose cycle.** Nine concerns reduce to six edits plus three
literal deletions; none requires judgement, and each is verifiable by a command. Four prose
passes have returned 64%, 60%, 50% — the marginal yield of a fifth is lower than its cost.

The two highs are hard stops: C44 makes the capability gate unsatisfiable and it blocks all
seven fix heads; C45 makes SC7b unreachable while 7.2 files a defect the plan now fixes.
**Neither is something execution surfaces cheaply** — C44 stops the run at gate resolution and
forces a plan amendment mid-flight, which is exactly the frontloadable class the retrospective
exists to catch.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C44 | high | **The two criteria-only assertions were moved OUT of the `ctl-` namespace** — renamed `check-full-tier-record` / `check-suite-portable` and relocated to `assets/checks/`. They are plain criterion checks with no RED/GREEN pair, so putting them in `controls.txt` was the error. 1.1(c) now states `controls.txt` is **authoritative** and the derivation must agree with it. **Verified: `grep -oE 'ctl-[0-9]{3}-[a-z-]+' plan.md | sort -u | wc -l` → 11**, matching the 11 builders. | `main-session` | `resolved` |
| C45 | high | 3.7's `touches` widened to every affected README — `yf-beads-hygiene`, `yf-beads-init`, and all three `yf-markdown-*`. **The README bullet was DELETED from 7.2**: the plan must not both fix and defer the same defect. `skills/*/scripts/fixtures/**` carved out of 3.6's globs explicitly, closing the FP surface EXP-003's "zero" never covered. **Verified: every README carrying a bare invocation is now named in 3.7's touches.** | `main-session` | `resolved` |
| C46 | medium | exp-004's blockquote **repaired** — the orphaned fragment rejoined as prose. Line 163's surviving "empty `agent` target node" struck. **And the sweep went further than the concern:** the section heading's own "16 sites" count withdrawn, and **exp-003 given a ⚠ correction block** for its refuted "8 rows" — which the concern noted had none. Three of seven findings now carry corrections. **Verified: 0 occurrences remain.** | `main-session` | `resolved` |
| C47 | medium | `depends-on: 0.1` added to Issue 2.1. SPEC-first is now enforced for #206, the plan's CRITICAL defect, and 0.1 is an ancestor of 7.1. **Verified.** | `main-session` | `resolved` |
| C48 | medium | 1.6 and 3.5 reworded to "the prototype **rebuilt at Issue 1.0**", and 1.0's rebuild list now names `check_skill_script_refs.py` explicitly. **Verified: 0 occurrences of the old wording.** | `main-session` | `resolved` |
| C49 | medium | 0.2 now names `SPEC.md` and `plan_manager.py` as **mixed-meaning files requiring line-precise edits** — a whole-file substitution would corrupt their stamp citations. 1.6c's allowlist extended to `skills/yf-beads-upstream/{SPEC.md,SKILL.md}`, which no other part of the plan named. | `main-session` | `resolved` |
| C50 | low | R7's `0-of-41` deleted. **Found and fixed on the verification run, not on the first edit** — the first sweep missed it, which is the exact failure this pass diagnosed. | `main-session` | `resolved` |
| C51 | low | D-5's `all 8` deleted, along with three other phrasings of the same count. Same note as C50: caught by re-running the check, not by the edit. | `main-session` | `resolved` |
| C52 | low | All five `16-site` occurrences deleted, including SC11b's referent, which now reads "every site `ctl-208-vocabulary-sites` enumerates". **Verified: `grep -c '16-site|all 8|0-of-41|the 8 rows'` → 0.** | `main-session` | `resolved` |
| C53 | low | 1.3 and 1.4 each ship a thin `.sh` wrapper in `assets/fixtures/` — `redcheck.sh` runs manifest controls with `bash "$fx"`, so a bare pytest arm is not runnable by the harness. | `main-session` | `resolved` |

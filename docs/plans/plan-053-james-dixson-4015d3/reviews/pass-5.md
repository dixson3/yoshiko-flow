---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: Red-team pass 5 (fifth independent, CONFIRMING) — APPROVE; 9 of 10 reproduced (90%), six of six verification commands pass
---

# Red-team pass 5 (confirming)

## Verdict: APPROVE

## Pass-4's six verification commands — six of six

| # | Required | Observed | |
| :-- | :-- | :-- | :-- |
| 1 | ctl-name count = Epic-1 control count | **11** vs **11 builders** | PASS |
| 2 | every README invocation in 3.7's touches | 3 files, **all three named** | PASS |
| 3 | `exp-004` empty-agent claim = 0 | **0**, blockquote well-formed | PASS |
| 4 | Issue 2.1 depends-on names 0.1 | `0.1, 1.2` | PASS |
| 5 | prototype wording = 0 | **0** | PASS |
| 6 | count literals = 0 | **0** | PASS |

## Reproduction of pass-4's 10 resolutions — 9 of 10 (90%)

| Class | Count | Concerns |
| :-- | --: | :-- |
| (a) landed and correct | **9** | C44, C45, C46, C47, C48, C49, C50, C52, C53 |
| (c) landed at one site, defect survives | **1** | C51 |

**64% → 60% → 50% → 90%. The method change is real and it worked.**

Verified beyond the supplied commands: **C45** was re-swept across *all* of 3.6's globs, not
just `uv run scripts/` — every ref failing exp-003's predicate is in 3.7's touches, and the ones
absent from it resolve to real files under a recognised root, so **SC7b is reachable**. The
corpus fixture FP surface was confirmed to exist, so C45's carve is **necessary, not
speculative**. **C49** was verified line-precise repo-wide: the six roots-meaning files are
*exactly* 0.2's six `touches`.

> **The honest caveat on the method.** The one exception is precisely a site the supplied
> command does not check — command 6 is a **fixed-literal grep**, so a *fourth phrasing* of the
> same figure passes it. Re-run-and-re-sweep genuinely raised the rate, but it inherits the
> blind spot of any literal-scoped grep.

## Class sweep — one survivor, now cleared

A regex sweep for `<number> <noun>` across `plan.md` and `findings/` found exactly one live
instance: `plan.md:84`'s *"Pulled the **8** `yf-diagram-authoring` rows in"* — the refuted
figure in the plan's own summary of the finding that withdraws it. **Deleted in resolution.**

Everything else surviving is a **frozen, cited measurement used as rationale** (`31 documents`
for the rejected broad form, `21 of 35` from another plan, `2 of 23` / `6 of 33`) — none read by
a control, criterion or gate. Text added during pass-4 resolution was swept separately and is
consistent.

## Gate — clean

Computed independently over the extractor's edge list: **46 issues, 62 edges, 0 unknown refs, 0
cycles.** Blocks closure = **exactly the 26 fixer issues**; all 7 Epic-0 SPEC issues and all 13
Epic-1 issues outside it. **Every issue is an ancestor of 7.1.** Every criterion's
`Discharged-by` resolves and every issue discharges at least one criterion. `controls.txt`-is-
authoritative is consistent with the gate Condition and the 11-name derivation. **C44 is gone.**

## Mechanical suite — green

`plan_extract --strict` exit 0, unparsed 0 · `doc_lint --root` PASS, **0 errors, 0 warnings** ·
`audit` **pass**, findings `[]`, `okf_native: true` · `gate-consistency` PASS, 0 findings ·
`ready-check` exit 3 (*"last verdict REVISE (pass-4)"* — this APPROVE clears it).

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C54 | low | **`assets/checks/` had no builder issue.** C44's remedy correctly moved the two criterion checks out of the `ctl-` namespace and thereby out of the Epic-1 builder set without giving them a new home. **Not a run-stopper** — `bash <missing>` exits 127, so both fail *loudly* at completion recheck, the opposite of this plan's thesis defect |
| C55 | low | `plan.md:84` still carried the refuted "8 rows" — a fourth phrasing that command 6's fixed-literal grep does not match |
| C56 | low | "53 bundles" is a moving corpus fact, framed as a past measurement. Note only |

## Recommendation

**APPROVE and execute.** All three concerns are low, none is read by a control, criterion or
gate, and each is cheaper to fix during execution than in a sixth prose cycle. Pass-4's own bar
— *"would stop the run at gate resolution and force a mid-flight amendment"* — is not met by
anything found here.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C54 | low | Both `check-` files given explicit builders in the text of the issues that own their inputs — 7.1 for `check-full-tier-record.sh` (which reads the `full-tier-record.md` it writes) and 3.4 for `check-suite-portable.sh`. Verified present. | `main-session` | `resolved` |
| C55 | low | Deleted. **Found only by the reviewer's regex class-sweep, not by the literal grep** — which is the caveat above, demonstrated. | `main-session` | `resolved` |
| C56 | low | Left as-is deliberately: a cited past measurement used as rationale, read by nothing. Recorded rather than churned. | `main-session` | `resolved` |

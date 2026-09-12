---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #364 - recheck-criteria at the completion binding runs
  without the plan''s criteria preamble env — all 12 criteria meaningless: 8 false
  FAILS and 3 silent false PASSES'
---
# Upstream #364: recheck-criteria at the completion binding runs without the plan's criteria preamble env — all 12 criteria meaningless: 8 false FAILS and 3 silent false PASSES

- **Number:** 364
- **Title:** recheck-criteria at the completion binding runs without the plan's criteria preamble env — all 12 criteria meaningless: 8 false FAILS and 3 silent false PASSES
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> **Corrected 2026-09-05.** The original filing claimed SC16 was a control that used no preamble
> variable. That was wrong — SC16 uses `$YR`, and so do **all 12** executable criteria. The
> corrected analysis below is materially worse for this defect: it produces **false PASSES** as
> well as false fails. See the correction comment.

## Summary

`land --apply` invokes `recheck-criteria` **without establishing the criteria preamble environment
the plan declares**, so every criterion whose verification uses a preamble variable is evaluated in
a broken environment. The criteria are not being evaluated at all — and depending on the
**polarity of the assertion**, the tool reports either a false FAIL or a false PASS.

On `plan-029`, all 12 executable criteria use a preamble variable, and all 12 verdicts were
meaningless.

## Controlled reproduction

Same tree, same command, same criteria. Only the environment differs:

| Invocation | Reported |
| :-- | :-- |
| as `land --apply` runs it | 9 FALSE / 3 PASS — **all 12 meaningless** |
| with `YR` / `PB` / `T` exported | 1 FALSE (SC13), 11 PASS — correct |

```sh
cd <plan repo>
export YR=Incubator/.../yreview PB=<plan_dir> T=$(mktemp -d)
plan_manager.py recheck-criteria <plan_dir> --json
#  {"verdict": "FAIL", "reason": "1 criterion/criteria are FALSE at completion: SC13"}
```

**`recheck-criteria` honors the environment when it is set** — it inherits from its caller. The
defect is that `land --apply` never sets it.

## The split is ASSERTION POLARITY, and the false-pass half is worse

| Polarity | Shape | With the env broken | Count on plan-029 |
| :-- | :-- | :-- | --: |
| Positive | `test -f $YR/X && … > $T/f` | dies → **false FAIL** | 8 |
| Negated / emptiness | `! grep -q … $YR/*.md`, `test -z "$(grep -L … $YR/*)"` | matches nothing → **false PASS** | 3 |

Verified under `bash` with `YR` unset:

```
! grep -qE -e "move-kind" … $YR/*.md $YR/diagrams/*.d2   → exit 0   (SC16)
! grep -qEi -e "binary.{0,60}…" $YR/*.md                 → exit 0   (SC10)
test -z "$(grep -L "ATTESTATION.md" $YR/SPEC.md)"        → exit 0   (SC2)
```

`$YR/*.md` expands to `/*.md`, matches nothing, the negation inverts "found nothing" into success.

**A false FAIL is loud; a false PASS is silent.** SC16 is `plan-029`'s invention-boundary tripwire —
it asserts that no decided-kind-set spelling appears anywhere in the document set. Under this
defect it reports PASS **without reading a single file**. Had the spec actually violated its own
invention boundary, the completion binding would have certified it clean.

That inverts the purpose of the completion recheck. The three vacuous passes are more dangerous
than the eight noisy failures, and they are invisible in the verdict — nothing distinguishes
"passed because the artifact is correct" from "passed because there was nothing to look at."

## The mechanism, on one criterion

SC18:

```sh
test -f $YR/ATTESTATION.md && head -1 $YR/ATTESTATION.md > $T/a1 && grep -q '^# ' $T/a1
```

With `$T` unset this expands to `> /a1`:

```
read-only file system: /a1     → exit 1 → reported "status": "FALSE"
```

`ATTESTATION.md` exists and its first line is a valid `# ` heading. Nothing about the artifact was
examined.

## Why the preamble exists

A yf-plan criteria table declares the CWD and the shell variables its verification cells use —
`$YR` (artifact root), `$PB` (plan bundle), `$T=$(mktemp -d)` (scratch for the `> file` +
`test ! -s` idiom).

That idiom is **recommended by yf-plan's own guidance** as the way to avoid empty-collection
false-fails (#356). So authors are steered toward exactly the construct this defect breaks at the
halting binding.

## Severity

High, and higher in combination.

- The completion binding is **halting**. A spurious FALSE stops a landing.
- Combined with #360 (a `skip` adjudication ignored), the halt lands **after** the merge and push,
  leaving a plan partially landed on a verdict where **every** row was meaningless.
- **The remediation text is backwards:** *"Each criterion above was true when its issue closed and
  is false now. Fix the regression."* An operator trusting it hunts a regression that does not
  exist, or amends criteria that were correct.
- **The false-pass half defeats the check entirely** — negated criteria certify clean without
  reading anything.

## Suggested fixes

1. `land --apply` (and every other binding of `recheck-criteria`) must establish the plan's
   declared criteria preamble — same CWD, same variables, fresh `$T` — before evaluating.
2. Parse the preamble from the criteria table rather than requiring the caller to know it.
3. **Fail INCONCLUSIVE, not FALSE — and never PASS — when a preamble variable is unset.**
   `recheck-criteria` already has `HARNESS_INCOMPLETE` (exit 2) for "the instrument did not run,"
   which is exactly this. Routing a harness fault to FALSE is the conflation that verdict exists to
   prevent; routing it to PASS is strictly worse.
4. Cheap structural guard, no execution required: if a verification cell references `$VAR` and
   `VAR` is unset at evaluation time, the verdict is INCONCLUSIVE by construction. On `plan-029`
   this would have caught **all 12**, including the three that silently passed.

## Related

- #360 — the `skip` adjudication that was ignored, which is why this ran at all.
- #356 — empty-collection false-fails; its recommended `$T` remedy is what this defect breaks.
- #358 — SC13, the one genuinely-false criterion.


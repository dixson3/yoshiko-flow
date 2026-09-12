---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #356 - yf-plan criteria: an executable criterion can
  false-fail on an empty collection, and both-directions validation does not catch
  it'
---
# Upstream #356: yf-plan criteria: an executable criterion can false-fail on an empty collection, and both-directions validation does not catch it

- **Number:** 356
- **Title:** yf-plan criteria: an executable criterion can false-fail on an empty collection, and both-directions validation does not catch it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

An executable success criterion in a yf-plan criteria table can **fail for a reason unrelated to
what it asserts**, and the both-directions validation yf-plan already prescribes does not catch it.
Found live during `plan-029` execution, on a plan that had survived **11 red-team review cycles**
specifically hunting criteria defects.

The rule is one line: **`grep` exits 1 when it matches nothing**, so a `grep` over a collection
that may legitimately be empty kills an `&&` chain on an *empty* collection rather than on a
violation.

## The live case

`plan-029`'s SC3 asserts four properties about id hygiene across a document set. Its verification
chains them with `&&`. Mid-execution it exited **1** while **every property it asserts held**:

| Asserted property | Actual |
| :-- | --: |
| no bare `GR-NNN` headings | 0 |
| no duplicate `-YREVIEW-` ids | 0 |
| id prefixes exactly `{REQ, GR}` | ✓ |
| no `-YREVIEW-` ids in `DESIGN.md` / `DATA-MODELS.md` | 0 |

The failing link:

```sh
grep -hE '^#{2,3} ' $YR/DESIGN.md $YR/DATA-MODELS.md > $T/dm && …
```

Those two files were still skeletons with no `##`/`###` headings, so `grep` matched nothing, exited
1, and took the chain down with it.

## Why this class is worse than the one yf-plan already guards

yf-plan's review guidance and the `6.2b` "exercise every criterion in both directions" pattern are
built to catch **criteria that cannot fail**. This is the mirror image: **a criterion that fails for
the wrong reason.** Three properties make it survive review:

1. **Both-directions validation passes it.** The conformant fixture had headings, so the criterion
   went green; the violating fixture tripped a different conjunct, so it went red. It discriminated
   perfectly and was still unsound. **The empty-collection case is a third direction**, and nothing
   in the current guidance asks for it.
2. **It self-heals.** Once `DESIGN.md` was authored the criterion passed. It would have been green
   at completion, having been unsound throughout — invisible in the final verdict.
3. **A false-fail reads as a real failure.** The natural response is to "fix" the criterion by
   weakening it. On this same plan the subordinate had already proposed dropping a conjunct from a
   *different* criterion (SC6) that was failing **correctly** — the artifact had unaligned tables.
   Had that been accepted the table would have gone green while the deliverable stayed broken.
   A false-fail and a true-fail are indistinguishable from the exit code, which is the whole
   problem.

## Proposed changes

**1. Criteria-authoring guidance (`yf-plan` SKILL.md / spec):** an executable criterion must be
**safe over legitimately-empty collections**. The remedy is already idiomatic in yf-plan criteria —
write to a file and assert on emptiness, rather than relying on a matcher's exit code:

```sh
# unsafe: dies on an empty collection
grep -hE '<pat>' <files> > $T/x && …

# safe: sed -n never signals "no match" via exit status
sed -n '/<pat>/p' <files> > $T/x ; test ! -s $T/x && …
```

`plan-029`'s SC3 *already used* the safe form for its other legs — the defect was one leg written
inconsistently, which argues for making this an explicit stated rule rather than a style anyone is
expected to infer.

**2. The both-directions fixture set needs a third case.** Whatever ships as the `6.2b` pattern
should require: conformant → pass, violating → fail, **empty/degenerate → pass** (or fail for a
stated reason). Two directions demonstrably was not enough.

**3. A cheap mechanical lint.** A criteria-table check could flag any `verification` cell
containing `grep` (without `-c`/`-q` guarded by `test`) followed by `&&`. Not a proof, but it
would have caught this instance and is far cheaper than a review pass.

## Severity

Medium. It does not corrupt a deliverable on its own, but it degrades the criteria table — the
artifact yf-plan treats as the mechanical proof of done — in the direction that invites weakening
a check under time pressure. The `plan-029` occurrence was **detected only because the parent
session independently re-ran the criteria mid-execution**, which is not something the workflow
requires or expects.

## Disposition on plan-029

The operator took the escalation's `on_no_answer` default: **do not edit the criteria table
mid-execution** (it is inside the fingerprint, so an edit forces re-approval for a criterion that
self-heals and will pass at completion). The reproduction and a two-direction-validated remedy are
recorded in that plan's bundle for a later plan to land. This issue is the **class** fix.


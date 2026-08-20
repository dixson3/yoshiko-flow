---
type: Finding
okf_spec: OKF-PLAN
id: exp-001
status: complete
---

# Finding: Can a check distinguish a *derivable* numeric target from a fixed literal? (#177)

## Approach Tested

Built the naive detector the issue implies — scan `## Success Criteria` rows for a numeric
target, and flag any that cites no provenance (a `findings/` or `assets/` path, a script name,
or the word "derived").

```bash
# rows matching '^| SC', numeric pattern (<=|>=|exactly|at most|at least|to) N
```

## Result

**measured (first attempt, and WRONG — retained because the error is the finding):** 101 SC rows
matched the row filter; 6 carried a numeric target; 1 cited a provenance.

**measured (pass-3 C13 re-derivation, in a sandbox spike with a repaired filter and pattern):**

```
SC rows matched: 163          # the first attempt undercounted by 61%
numeric targets: 11
of which cite provenance: 7
  [PROV] plan-049 :: SC23 | corpus `unparsed[]` <= 73 (derived: 81 - 7 ... + 2 ... - 3)
  [PROV] plan-049 :: SC31 | Corpus `unparsed[]` <= 81 ... the derived post-write target
```

Two results, both contrary to the first attempt:

1. **The recall failure was a regex defect, not undecidability.** A repaired pattern finds SC31
   and SC23. The first attempt's conclusion — "the information that distinguishes them is not in
   the document" — was an inference from a broken instrument.
2. **The recommended successor check would have PASSED both motivating cases.** SC23 carries a
   full inline arithmetic derivation; SC31 says "the derived post-write target". Under the
   citation rule this finding originally recommended, both are compliant — and both are precisely
   the criteria that failed at execution.

**inferred:** citation *presence* is not the tractable form of #177. A check that green-lights the
two cases it was designed to catch is the same "ships unable to fail" class as the scanner it
replaces. Any tractable form must be stronger — a citation that **resolves to an artifact** whose
arithmetic is **re-derivable** — or #177 is not detector-shaped at all.

## Implications for Plan

**D-6 (drop #177) survives and is STRENGTHENED.** The original argument was "the detector missed
them". The measured argument is stronger and different: *the successor design green-lights the very
cases it was built for.* That is a better reason to drop the deliverable than the one this finding
first gave.

The corpus population is **163 SC rows**, not 101 — and even that is a lower bound of unknown
tightness, since the filter was repaired once and may still miss table shapes.

## Recommendations

- Do **not** ship the bare-numeric scanner, and do **not** ship the citation-presence check either
  — measured, it passes SC23 and SC31.
- Issue 6.2's comment on #177 must carry **this corrected result**, not the first attempt's
  recommendation. Publishing the original would hand the next attempt a design measured to fail
  and a denominator that is a 61% undercount.
- **Method note, recorded deliberately:** this finding's first version was written by the main
  session and passed two main-session review cycles. It was falsified by an independent reviewer
  who *built the recommendation and ran it*. That is the sandbox-spike case (#182) and the
  independent-review case ([#184](https://github.com/dixson3/yoshiko-flow/issues/184)) in one
  artifact.

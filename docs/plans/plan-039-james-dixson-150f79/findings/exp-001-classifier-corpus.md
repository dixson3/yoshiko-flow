---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: How badly does `_classify_deliverable` over-suggest `ci-release`, and do the four proposed fixes correct it?

**Experiment:** EXP-001 · **Date:** 2026-08-14 · **Issue:** [#108](https://github.com/dixson3/yoshiko-flow/issues/108)

> **Re-measured 2026-08-14 after review.** The corpus counts below moved during drafting because
> the corpus includes this plan, which was still being written (pass-2 M3). Current figures:
> **40/53** current, **13/53** after all fixes. The **cumulative F1-first ladder** shown further
> down is superseded by the **per-step F3-first ladder** in `plan.md` Issue 3.2, which matches
> the implementation order this plan actually adopted (pass-2 H2). Conclusions are unchanged;
> only the counts and the ordering moved. Treat `plan.md` as authoritative for figures, and
> re-derive rather than transcribe (Issue 3.1's harness does this).

Findings are marked **[measured]** (a command ran, this was its output) or **[inferred]**
(a conclusion drawn from it), per the convention this plan proposes to adopt in
[#114](https://github.com/dixson3/yoshiko-flow/issues/114).

## Approach Tested

Imported `_classify_deliverable` from `skills/yf-plan/scripts/plan_manager.py` unmodified and
ran it across a 53-plan corpus:

- `yoshiko-flow/docs/plans/*` — 39 plans (this repo, plan-001 … plan-039);
- `d3-pxe/Incubator/*/plans/*` — 14 plans across the `ansible`, `litellm`, `opentelemetry`,
  `plex-lxc`, and `postgres` incubators.

(Of the 53, 17 carry an operator-confirmed label: 8 `yoshiko-flow` + 9 `d3-pxe`. Pass-3 C5 caught
an earlier "44 + 9" breakdown that summed correctly but split wrongly.)

The d3-pxe corpus includes the exact two plans #108 cites (`postgres/plan-011`,
`litellm/plan-010`).

A second run compared the current classifier against prototypes of the four proposed fixes,
applied cumulatively:

| Fix | Change |
| :-- | :-- |
| F1 | Section-scoped `hay` — only `## Epics`, `## Upstream Issues`, `## Success Criteria` |
| F2 | Negative context guards (`self-signed`, `release notes/cycle/cadence`, `<signal> pipeline`, `deployed by`) |
| F3 | Require a **high** signal; a lone low keyword is informational, not a suggestion |
| F4 | `confidence: high` reserved for the `.github/workflows/` path marker |

**Ground truth** is the operator-confirmed `deliverable_class` recorded in `plan.md`
frontmatter — a human decision, not this experiment's inference. 17 of the 53 plans carry one.

Scripts: `scratchpad/exp001_classifier.py`, `scratchpad/exp002_proposed.py`.

## Result

### Headline: 40 of 53 real plans are suggested `ci-release` **[measured]**

This is the unbiased figure — it depends on no labeling decision and no operator behavior, only
on running the classifier over every plan that exists. **Roughly three quarters of all plans, in
two repositories, are told they ship release configuration.** The labeled-set analysis below is sharper but
requires a bias control; this number does not.

### The current classifier's precision on operator-labeled plans is 1/17 **[measured]**

```
=== LABELED CORPUS (17 operator-confirmed plans) ===
  current    TP=1 FP=16 TN=0 FN=0   precision=1/17
  F1 only    TP=1 FP=13 TN=3 FN=0   precision=1/14
  F1+F2      TP=1 FP=13 TN=3 FN=0   precision=1/14
  F1+F2+F3   TP=1 FP=2  TN=14 FN=0  precision=1/3
  all four   TP=1 FP=2  TN=14 FN=0  precision=1/3
```

`TN=0` for the current classifier: across every plan where an operator recorded a class, it
suggested `ci-release` **every single time**. It has never once produced a correct negative. The
one true positive (`plan-031`, an AWS/CI deploy plan) is indistinguishable from noise, because
the classifier suggests `ci-release` unconditionally.

#### Bias control: is `TN=0` an artifact of how labels get created? **[measured]**

The objection is real and worth stating, because it is exactly the measurement-vs-inference
error this plan proposes to fix. Operators record `deliverable_class` at SKILL.md §4.1.5 *after
being prompted by the classifier*. **If** the field were written only when `ci-release` was
suggested, then the labeled set would be, by construction, the set of plans the classifier
flagged — and `TN=0` would be a tautology rather than a finding.

Checked against consecutive plans, which cannot be cherry-picked:

```
plan-031  ci-release      plan-035  standard
plan-032  standard        plan-036  standard
plan-033  standard        plan-037  standard
plan-034  standard        plan-038  standard
```

**Eight consecutive plans, all labeled** — so the field is written regardless of what the
classifier suggested, and the labeled set is not selected on the classifier's output. On this
unbiased consecutive run the current classifier flagged **8 of 8** (031 and 033 and 038 at
`confidence: high`) against a ground truth of 1. Precision 1/8.

**[inferred]** The `TN=0` result survives the objection. It reflects the classifier's behavior,
not the labeling process. The 14 unlabeled plans predate the `deliverable_class` field
(introduced by plan-030), not a skipped prompt.

### Full-corpus suggestion rate: 40/53 → 13/53 **[measured]**

_Cumulative F1-first ladder — **superseded** by `plan.md` Issue 3.2's per-step F3-first table,
which is the order actually implemented. Retained for provenance._

```
=== FULL CORPUS (53 plans) — ci-release suggestions ===
  current    39/53      F1+F2+F3   12/53
  F1 only    31/53      all four   12/53
  F1+F2      29/53
```

### Zero false negatives at every stage **[measured]**

`FN=0` across all five variants. The fixes cost no recall on this corpus — `plan-031`, the only
operator-confirmed `ci-release` plan, survives all four.

### F3 is the dominant fix; F1 is second; F2 is marginal **[measured]**

- **F3** (require a high signal) does most of the work: 29 → 12 on the full corpus, and 13 → 2
  false positives on the labeled set. #108 lists it third; it is first by a wide margin.
- **F1** (section scoping) removes 8 full-corpus suggestions, including the title-verb `deploy`
  class #108 identifies as the widest trap.
- **F2** (negative guards) removes 2 full-corpus suggestions and **0** labeled-set false
  positives. It is the weakest of the four on this evidence.
- **F4** changes no classification — by construction it only relabels confidence. Its measured
  effect is that **all 12 surviving suggestions report `confidence: low`**.

### The two residual false positives are one shared class **[measured]**

```
plan-006 (opentelemetry)  signals=['release','sign','self-hosted']
plan-033 (yoshiko-flow)   signals=['release','deploy']
```

Matched context, extracted verbatim:

- plan-006: `pinned release binary`, `pinned signed static binary via get_url + checksum:`
- plan-033: `kept until the next major release of yf` (×5), `commit a guess into a released binary`

**[inferred]** Both are **consuming or referencing** a release, not **producing** one. The
distinguishing feature is the verb, not the noun — which is why a keyword blocklist keeps
chasing it. This is the "blocklist that grows per false positive" cost #108 names, observed
directly.

### F4 makes `confidence` constant at intake **[inferred from measurement]**

The path marker is the only non-prose signal, and `changed` is empty at §4.1.5 — so under F4
**every intake-time classification reports `confidence: low`**, confirmed by all 12 survivors
above. F4 correctly stops the field from overstating, but leaves it carrying no information at
the moment it is actually read.

## Implications for Plan

1. **#108 substantially understates the defect.** It reports two false positives on Proxmox
   plans; measured, it suggests `ci-release` on **all 17** labeled plans (16 wrongly) and on 40/53
   corpus-wide, including on `yoshiko-flow`'s own plans. The `ci-release` suggestion is currently equivalent to a constant.
2. **All four fixes are justified, but F3 should be sequenced first** — it delivers the largest
   correction and is the smallest change. F1 second. F2 last, and explicitly as a
   known-incomplete blocklist rather than a general solution.
3. **F4 needs a shape decision, not just a rule change.** Reserving `high` for the path marker
   is right, but leaves `confidence` uninformative at intake. Reporting the *evidence basis*
   (`prose-only` vs `path-backed`) is more honest than a severity word that is always `low`.
4. **A regression test has an obvious, cheap oracle**: the 17 operator-labeled plans. Assert
   `FN=0` and `FP` non-increasing against fixtures derived from them — **not** a fixed `FP`
   target, which has no principled basis and drifts as plans are added (see Recommendations).

## Recommendations

- Implement F3, F1, F2, F5, F4 as separate issues, in that order, each with a test. (F5 —
  strip code spans and fenced blocks — was added during review; see `plan.md` Issue 3.4b.)
- Replace `confidence: high|low` with an explicit evidence basis at intake, or document that
  intake-time confidence is structurally always `low`.
- Do **not** attempt to chase the residual `release binary` / `next major release` class with
  more keywords; record it as a known limit with the two measured examples.
- Add the labeled corpus as a fixture-backed regression test guarding `FN=0`. Assert `FN=0` and
  `FP` non-increasing as the invariants; do **not** encode a fixed `FP` target (pass-2 R4/H2 —
  `FP<=2` has no principled basis and the counts drift as plans are added).

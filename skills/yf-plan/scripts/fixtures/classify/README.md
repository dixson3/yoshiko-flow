# Deliverable-class classifier fixture corpus

Ground-truth corpus for `test_classify_deliverable.py` (REQ-CLI-015, plan-039 Issue 3.1).
One directory per **operator-labeled** plan; each holds a `plan.md` whose frontmatter
carries the operator's confirmed `deliverable_class` as ground truth, plus `source_plan`
and `source_repo` provenance.

## Why it is vendored

The corpus is derived from real plans in two repositories — this one and the sibling
`d3-pxe` — but it is **copied into this repo**. Reading a sibling checkout was an
authoring-time capability (plan-039's `Evidence corpus` capability gate); once these
fixtures landed, that dependency was discharged. **No test may reach outside this repo.**

## Do not transcribe the numbers

`BASELINE.json` is **generated, never hand-written** — regenerate with:

```bash
uv run skills/yf-plan/scripts/test_classify_deliverable.py --write-baseline
```

It records the confusion matrix of the **pre-fix** classifier over this same corpus, which
is what makes "`FP` non-increasing" checkable without a literal in the test code.

**The corpus is self-including and drifts.** A plan joins the ground-truth set the moment
`deliverable_class` is written at its intake (SKILL.md §4.1.5) — so the plan *being
written* becomes part of the population that measures the classifier, and every absolute
count goes stale as plans are added. This is not a flaw to fix; it is a property to
account for. Accordingly the suite asserts **properties, not counts**:

- **`FN == 0`** at every step — the hard invariant. A false negative silently disarms
  `complete-gate`; a false positive costs an operator seconds at intake. Recall is the
  safety-critical direction and is never traded for precision.
- **`FP` non-increasing / `TN` non-decreasing** against the generated baseline.
- Structural pins (F1 title-exclusion, F5 code-span/fence exclusion) that hold regardless
  of corpus composition.

## How the fixtures were reduced

Each fixture keeps its source plan's H1 title, the three **scanned** sections (Epics,
Upstream Issues, Success Criteria), and the Risks table. The title and Risks table are
retained deliberately: they are the principal *out-of-region* text that F1 (section-scoped
scan) must exclude, and without them F1 would be structurally untestable.

Reduction is **fidelity-checked**. A reduced fixture is accepted only if it classifies the
same way under the pre-fix classifier as its full source plan does; a plan whose signal
would be lost by reduction is vendored **in full** instead. `MANIFEST.json` records which
form each fixture took. Two fixtures (`yoshiko-flow-plan-032`, `yoshiko-flow-plan-038`)
required the full form.

That check is what lets this corpus reproduce the original measurement: the vendored
baseline is `TP=1 FP=16 TN=0 FN=0` over `n=17`, matching the live-corpus measurement over
the same 17 plans — the classifier had **never** produced a correct negative.

## Exclusion: plan-039 itself

plan-039 carries `deliverable_class: standard` and so is technically part of the labeled
population, but it is **deliberately excluded** from this corpus:

1. It was still being edited while its own classifier fixes were being written, so its
   text is a moving target — a vendored snapshot would pin a document that changed
   underneath it. (Its signal count moved twice during review, falsifying a hard count
   asserted about it twice.)
2. It is the subject of its own separate self-test (plan-039 SC6), which asserts *stable
   properties* — `evidence: prose-only`, `confidence: low`, and every residual signal
   traceable to genuine subject-matter prose — precisely because a count would not hold.

plan-039 is expected to classify `ci-release` despite being labeled `standard`: its
subject **is** releases, signing, and the deliverable class itself. That is the
**self-reference class**, a structural limit of prose keyword matching that no blocklist
can close. Including it as a fixture would bake a permanent by-design false positive into
the corpus and conflate that structural limit with a fixable defect.

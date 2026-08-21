---
type: Reference
okf_spec: OKF-PLAN
id: extraction-delta-050
description: Issue 7.5 / SC24 — the #186 and #187 fixes measured on this plan's own bundle
---

# Issue 7.5 — the fix measured on this plan's own bundle

The same `plan.md`, extracted twice: once by the **unfixed** extractor in the primary
checkout, once by the **fixed** one on `plan-050-…-execute`.

## The DAG is unchanged, which is the precondition for reading the delta at all

| | epics | issues | edges | `unparsed` | `--strict` |
| :-- | --: | --: | --: | --: | --: |
| before | 6 | 28 | 41 | 0 | 0 |
| after | 6 | 28 | 41 | 0 | 0 |

Issue ids identical. Had the edge count moved, the title fix would have perturbed parsing —
which is precisely the failure pass-10 measured for the naive `ln = raw` repair, and why
REQ-DATA-062 mandates the **offset-sliced** capture instead.

## The title delta: 27 restored

**27 issue titles + 0 epic names = 27.** SC24 predicted **27 of 34** and the measurement
matches exactly.

The `0` epic names is not a gap: none of this plan's six epic names carries an inline code
span, so there was nothing to restore. The epic-name site is nonetheless fixed and
**separately proven** — `ctl-186-masked-title`'s fixture plan carries a backticked epic name
and it blanks pre-fix, which is what settled the "single call site" question at pass 11.

Representative restorations:

| Issue | Before | After |
| :-- | :-- | :-- |
| 0.1 | `Land the         requirements for every…` | ``Land the `REQ-*` requirements for every…`` |
| 0.2 | `Build                      with **three verbs**…` | ``Build `assets/redcheck.sh` with **three verbs**…`` |
| 0.2a | `…record the corpus                 with…` | ``…record the corpus `files_checked` with…`` |

Note what the pre-fix output looked like: **not** an error, not an `unparsed[]` entry, not a
non-zero exit — just runs of spaces where a term used to be, written straight into a bead
`title` by §5.2a's mechanical pour. `--strict` returned `unparsed: []` and exit **0** the whole
time. That is the defect class this plan is about, in the tool this plan uses to execute
itself.

## The `detail` delta: ZERO, recorded as a negative observation

**0 of 28** issues carry non-empty `detail`.

This is the value SC24 predicts, and it is recorded as a **negative observation rather than
passed over**. Every one of this plan's continuation bullets is a `depends-on:` or
`resolves-upstream:` sub-key, which REQ-DATA-063 **excludes** by design — the same bytes must
not be reachable both as a structured edge and as prose. So an empty `detail` here is the
field working, not the field failing.

Pass-10 C99 measured this in advance (0 of 35 continuation bullets carry prose) and the plan
was corrected then: an earlier note had claimed #187 was load-bearing for *this* plan. It is
not. **This plan's exposure is #186**; #187 matters for every plan that writes substantive
continuation prose, and `ctl-187-empty-detail`'s fixture — which does — is where it is proven.

A criterion phrased as "`detail` is non-empty" would have been unfalsifiable here and would
have been quietly satisfied by the fixture alone.

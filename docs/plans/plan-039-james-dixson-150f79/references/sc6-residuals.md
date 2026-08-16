# SC6 — plan-039 self-test residual signals

Enumerated at execution time (2026-08-15), after all Epic 3 fixes landed. Re-derived from
the live document, never transcribed.

## Result

```
uv run ./skills/yf-plan/scripts/plan_manager.py \
  classify-deliverable docs/plans/plan-039-james-dixson-150f79 --json
```

```json
{"suggested_class": "ci-release", "signals": ["release", "sign", "deploy"],
 "confidence": "low", "evidence": "prose-only"}
```

**SC6 is satisfied.** The criterion asserts stable properties, not a count:

| Property | Required | Observed |
| :-- | :-- | :-- |
| `evidence` | `prose-only` | `prose-only` ✅ |
| `confidence` | `low` | `low` ✅ |
| every residual signal is genuine subject-matter prose | yes | yes — enumerated below ✅ |

`suggested_class: ci-release` is the **correct** outcome, not a failure. This plan's subject
*is* releases, signing, and the deliverable class itself — the **self-reference class**, the
structural limit recorded in Issue 3.4b that no keyword approach can close. What Epic 3 owed
here was an honest report, and `prose-only` / `low` is one: it tells the operator the
suggestion rests on words in the plan's prose, not on a `.github/workflows/**` path.

## Residual signals, with the matched text quoted

Three distinct signals matched (`release`, `sign`, `deploy`). Every occurrence below is prose
*about* the classifier — the plan discussing releases, not shipping one.

### `release` (high tier) — 8 occurrences

1. `deliverable-class heuristic false-positives ci-release on ordinary infra plans` — the
   title of upstream issue #108, quoted in the Upstream Issues table. The plan naming the
   defect it fixes.
2. `it structurally cannot cover the residual class — plan text that *consumes or references* a
   release rather than producing one` — Issue 3.4's stop rule, describing this exact failure
   mode.
3. `measured examples: a pinned upstream release binary` — a measured counter-example recorded
   in the stop rule.
4. `a deprecation horizon phrased as "kept until the next major release"` — the second measured
   counter-example, quoted from another plan.
5. `a quoted example is not thereby announcing that it ships releases` — Issue 3.4b stating the
   F5 rationale.
6. `it rose as the h1 remedy added prose about releases` — Issue 3.4b recording that this
   plan's own signal count moved while it was being edited.
7. `a plan whose *subject* is releases, signing, or the deliverable class itself will match in
   ordinary prose` — Issue 3.4b naming the self-reference class.
8. `its subject *is* releases and signing, the self-reference limit recorded in 3.4b` — SC6
   itself, predicting this very result.

### `sign` (high tier) — 2 occurrences

1. `a plan whose *subject* is releases, signing, or the deliverable class itself` — Issue 3.4b.
2. `its subject *is* releases and signing` — SC6.

### `deploy` (low tier) — 1 occurrence

1. `re-baking and redeploying depends on a binary release cycle this plan does not otherwise
   touch` — the install-parity out-of-scope note. (Matched as a substring of *redeploying*.)

## Reading

Zero of the 11 occurrences describes work this plan performs. Nine are the plan quoting,
naming, or reasoning about the defect class; one quotes another plan's text as a
counter-example; one is an out-of-scope note about a build step this plan explicitly does not
take. That is the self-reference class in full: the document is about the thing being measured,
so the measurement sees its subject matter.

Note also what F5 and F1 already removed: the plan is dense with fenced commands containing
`release` and `sign` (the verification commands in Success Criteria, the `gh` invocations in
Epic 5), and its Motivation and Approach sections discuss releases at length. None of that
appears above — code spans and fenced blocks are stripped, and only the Epics / Upstream Issues
/ Success Criteria sections are scanned. The residual is what survives both filters.

<!-- Draft for a NEW issue (plan-061 Issue 5.6). Not filed by the executing session:
     `gh issue create` is an outward-facing write. File with:
       gh issue create --title "<title below>" --body-file <this file> --label bug
     then strip this comment. -->

**Title:** `gate_consistency.py` returns PASS on gates it cannot evaluate — a vacuous check

## What happened

Run against plan-061's bundle during its drafting, `gate_consistency.py` reported:

```
PASS, gates: 4, findings: []
```

At that moment **two of those four gates were unsatisfiable**, and plan-061's own `## Gates`
section carried a hand-written admonition saying so:

> **Known grammar gap — the `test_class` / `cwd` lines below do NOT survive extraction.**
> `plan_extract.py`'s gate grammar recognizes only `Type|Approvers|Condition|Test|Blocks|
> Instructions`, so `plan_extract.py --json` reports `test_class: None` for every gate here.

So the checker counted four gates, found nothing wrong with any of them, and exited clean —
while the plan author had already documented, in the same file, that two of them could not be
run at all. Confirmed at execution: `plan_extract.py --json` reports `test_kind: "executable"`
and no `test_class` field for both capability gates. Without the executing session setting
`gate_type` / `test` / `test_class` / `cwd` as **bead metadata** at the §5.2a pour, the
coordinator reads `manual`, the §5.2c sweep runs neither gate, and both report INCONCLUSIVE
forever rather than ever being evaluated.

## Why it matters

This is the **vacuous-check class** (#263), and the third structural instance of
*two facts, one signal* this repository has recorded — after `doc_lint`'s `not-selected` vs
`no-such-path` (#181) and `resume-scan`'s `found` (#207).

`gates: 4` conflates *"four gates were checked and are consistent"* with *"four gates were
counted and none could be evaluated"*. A `PASS` that cannot distinguish those is not evidence
that the gates are sound. Precedent for the fix shape already exists in this repo:
`check_okf_index_drift.py`'s `--min-roots`, and plan-061's own
`check_skill_readme_contract.py`, which reports an `INCONCLUSIVE` (exit 2) rather than a
verdict when it could not read its input.

## Suggested direction (not prescriptive)

- Report a gate whose `test_class` is absent as **INCONCLUSIVE**, never fold it into `PASS`.
- Distinguish `gates_counted` from `gates_evaluated` in the JSON, so a caller cannot read the
  first as the second.
- Consider whether the real fix is upstream: extend `plan_extract.py`'s gate grammar to
  recognise `test_class` and `cwd`, which would remove the need for the per-plan admonition
  plan-058 and plan-061 both had to hand-write. That admonition is itself the symptom — two
  consecutive plans documenting a tool's blind spot in prose is the signal the tool should
  carry it.

## Provenance

Not plan-061's remit to fix; recorded so the next plan does not rediscover it. Adjacent to
**#289**. Found during plan-061 (`plan-061-james-dixson-6d8c97`, tracker #315).

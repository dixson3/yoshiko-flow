---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #116: yf-plan: red-team template emits '### Verdict:' but ready-check parses '## Verdict:' — verdicts silently unparseable

- **Number:** 116
- **Title:** yf-plan: red-team template emits '### Verdict:' but ready-check parses '## Verdict:' — verdicts silently unparseable
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/116
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`skills/yf-plan/agents/red-team.md` instructs the agent to emit its verdict as a **level-3** heading, but `plan_manager.py` parses only a **level-2** heading. A review written exactly as the template prescribes is silently unparseable, and `ready-check` reports `no red-team verdict found` — as if no review had happened at all.

## Evidence

Template (`skills/yf-plan/agents/red-team.md:34`):

```markdown
### Verdict: APPROVE | REVISE | INVESTIGATE-MORE
```

Parser (`skills/yf-plan/scripts/plan_manager.py:2766`):

```python
m = re.match(r"##\s+Verdict:\s*([A-Za-z-]+)", line.strip())
```

`re.match` anchors at the start, so against `### Verdict: APPROVE` the literal `##` matches the first two hashes and `\s+` then fails on the third `#`. No match. The docstring at line 2741 confirms the intent: *"The verdict is parsed from the first `## Verdict: <V>` line (case-insensitive)."*

## Impact

Observed live while authoring plan-037: reviews written per the template returned

```json
{"ready": false, "reasons": ["no red-team verdict found — expected reviews/pass-N.md with a '## Verdict:' line"], "verdict": null, "review_pass": 2, "audit_status": "pass"}
```

`review_pass: 2` proves the files were found and counted — only the verdict line failed to parse. The failure mode is bad in both directions:

- a genuine `APPROVE` cannot reach `ready-for-approval` (what happened here);
- a genuine `REVISE` is equally invisible, so REQ-PLAN-030's "last recorded verdict must be APPROVE" cannot see a blocking verdict it should have honored.

Across existing plans, `grep` over `docs/plans/*/reviews/*.md` finds 49 verdict lines: 47 use `##` and 2 use `###`. So the corpus has been carrying the template's own form as a latent defect, and those 2 reviews' verdicts have never been machine-readable.

## Requested change

Make template and parser agree. Either is defensible; accepting both is the most robust:

1. Fix `agents/red-team.md` to emit `## Verdict:`, matching the parser, the docstring, and 47 of 49 existing reviews.
2. Optionally relax the regex to `^#{2,3}\s+Verdict:` so the 2 existing `###` reviews become parseable and the trap cannot recur.

Also worth a fail-loud check: `ready-check` currently cannot distinguish "no review exists" from "a review exists but its verdict did not parse". `review_pass: 2` alongside `verdict: null` is a contradiction the tool should report as a malformed-review error, not as an absent verdict.

## Refs

Found while authoring plan-037 (#115), which fixes this as part of its scope.

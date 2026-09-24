---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #274 - yf-plan: plan_extract.py SILENTLY mis-parses the
  multi-item resolves-upstream form — every issue gets the FIRST disposition'
---
# Upstream #274: yf-plan: plan_extract.py SILENTLY mis-parses the multi-item resolves-upstream form — every issue gets the FIRST disposition

- **Number:** 274
- **Title:** yf-plan: plan_extract.py SILENTLY mis-parses the multi-item resolves-upstream form — every issue gets the FIRST disposition
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> Found by plan-059's conformance pass while wiring a two-issue `resolves-upstream`. Reproduced and
> root-caused independently before filing.

## The defect

```
- resolves-upstream: #269 (include), #145 (partial)
```

parses **both** as `include`. The second disposition is **silently discarded** — no warning, no
`unparsed` entry, exit 0.

This is a real defect, not a misuse: `SKILL.md:541-542` explicitly documents the form —

> `- depends-on:` and `- resolves-upstream:` are **two-space-indented bullets under their issue**,
> and take a **comma-separated list** of issue ids / `#<n> (<disposition>)` respectively.

## Reproduction

```bash
cat > /tmp/pfix/plan.md <<'PLAN'
## Epics
### Epic 1: probe
- Issue 1.1: multi-item form
  - resolves-upstream: #269 (include), #145 (partial)
- Issue 1.2: single-item control
  - resolves-upstream: #145 (partial)
PLAN
uv run "$(yf skill-dir yf-plan)/scripts/plan_extract.py" /tmp/pfix/plan.md --json
```

Actual:

```json
{"id":"1.1", "resolves_upstream":[{"issue":"#269","disposition":"include"},
                                  {"issue":"#145","disposition":"include"}]}
{"id":"1.2", "resolves_upstream":[{"issue":"#145","disposition":"partial"}]}
```

Issue 1.2 is the control and parses **correctly** — so the bug is specific to the multi-item form,
not to the `partial` token.

## Root cause — `scripts/plan_extract.py:380-383`

```python
for num in UPSTREAM_ROW.findall(val):
    d = re.search(r"\((\w+)\)", val)          # <-- scans the WHOLE line, every iteration
    cur_issue["resolves_upstream"].append(
        {"issue": f"#{num}", "disposition": d.group(1) if d else None})
```

`re.search` is *inside* the loop but searches `val` — the entire value — rather than the current
item's scope. It therefore returns the **first** parenthetical on every iteration, and every issue
in the list inherits item one's disposition.

`findall` correctly recovers **all** the issue numbers, which is why the count is right and only the
dispositions are wrong. That is what makes it invisible: `upstream: 2` is reported, so nothing looks
lost.

## Why this matters more than a parse slip

**It is silent and it corrupts a semantic field, not a structural one.** Any plan using the
multi-item form has **wrong dispositions in its extracted DAG**, and nothing would say so — no
`unparsed` entry, no non-zero exit, no residue metric change. A plan declaring `#145 (partial)`
extracts as `include`, which is a claim to have *resolved* an upstream issue that was only
partially addressed. That flows into reconciliation.

This is the same shape as the TRAILING-INLINE "dark matter" the file's own comments describe at
lines 94-98 — *"plan-006 and plan-007 reported `0 unparsed, 0 edges` while carrying 20 declarations
between them, so the residue metric recorded the loss as perfection."* Here the residue metric again
records a loss as perfection, for a different reason: the items are counted, so only their meaning
is wrong.

## Suggested fix

Scope the disposition search to the item, not the line — split `val` on commas first and match
`#(\d+)\s*(?:\((\w+)\))?` per item, so an item with no parenthetical yields `None` rather than
inheriting its neighbour's.

## Suggested check

A corpus sweep for existing multi-item declarations would establish blast radius. Since the count is
correct and only dispositions are wrong, **no existing plan's extraction would have flagged this** —
so the affected set has to be found by grep, not by re-running the extractor.

## Workaround in use

plan-059 declares each upstream issue on its own `- Issue` rather than in a list.

## Related

- #269 — the plan that hit it

🤖 Generated with [Claude Code](https://claude.com/claude-code)


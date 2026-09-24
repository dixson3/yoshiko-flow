---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #280 - yf-beads-upstream: detect_followons'' `narrow`
  auto-eligible set has been permanently empty since it was written'
---
# Upstream #280: yf-beads-upstream: detect_followons' `narrow` auto-eligible set has been permanently empty since it was written

- **Number:** 280
- **Title:** yf-beads-upstream: detect_followons' `narrow` auto-eligible set has been permanently empty since it was written
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

`detect_followons` in `skills/yf-beads-upstream/scripts/upstream.py` resolves a dependency
edge's target as:

```python
d.get("depends_on_id") or d.get("target") or d.get("to")
```

But its `deps_for` closures in `cmd_followons` and `cmd_land` are fed by
**`bd dep list <id> --json`**, and that command emits **no `depends_on_id`**.

## Measured on bd 1.2.2

```
bd dep list <id> --json  keys: close_reason, closed_at, created_at, created_by,
                               dependency_type, description, id, issue_type, owner,
                               priority, status, title, updated_at
has depends_on_id?  False

bd list --all --json     dependencies[] keys: created_at, created_by, depends_on_id,
                                              issue_id, metadata, type
```

`bd dep list` embeds the **full target bead** and carries its id as **`id`** — which is not
in the resolution chain. So the expression is **always `None`**, `discovered_into_subtree`
is never true, and:

> **the `narrow` (auto-eligible) follow-on set has been permanently empty since it was
> written.**

## Why this matters

`narrow` is exactly `plan_land_hoist`'s `auto_eligible` set under
`custom.upstream.auto_hoist_followons = true` — the **no-prompt path that runs `bd close -r`
tombstones**. So a documented, shipped capability has never once fired.

The defect is **symmetric and unpleasant either way**:

- **As-is**, a feature the skill documents does not work, silently.
- **Fixed**, an unattended destructive path becomes reachable in any repo where
  `auto_hoist_followons` is `true`.

## Scope

This issue is the **defect report only**. Whether to *activate* the signal is a separate,
operator-facing decision — in plan-058 it sits behind a human consent gate, and this issue
is deliberately **not** downstream of that gate, so that a decline still leaves the bug
filed rather than buried.

Note this repository currently has `auto_hoist_followons` **unset** (default-deny), which
masks the destructive half here. That is a fact about this clone, not about the skill, which
ships elsewhere.

A minimal fix is to add `id` to the resolution chain, or to source the edges from
`bd list`'s `dependencies[]` — but see the activation caveat above before doing either.

Filed from plan-058 Issue 3.7. Recorded as risk R14 in that plan.


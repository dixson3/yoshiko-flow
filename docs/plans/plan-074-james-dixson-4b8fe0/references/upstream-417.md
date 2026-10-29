---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #417 - yf-plan: resolve-start-gate can''t find the Begin:
  wrapper under bd 1.3.0 (poured as issue_type gate, not task)'
---
# Upstream #417: yf-plan: resolve-start-gate can't find the Begin: wrapper under bd 1.3.0 (poured as issue_type gate, not task)

- **Number:** 417
- **Title:** yf-plan: resolve-start-gate can't find the Begin: wrapper under bd 1.3.0 (poured as issue_type gate, not task)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/417
- **State:** OPEN
- **Labels:** 

## Body

## Symptom

At execute start, `plan_manager.py resolve-start-gate <plan_dir>` returns:

```json
{"verdict": "inconclusive", "passed": false, "epic": "yf-mol-t42s", "wrapper": null, "gate": null,
 "reason": "no start-gate wrapper task (title `Begin: …`) under yf-mol-t42s",
 "remediation": "Inspect `bd children yf-mol-t42s --json` and resolve the start gate by hand if the pour is non-standard."}
```

Observed on plan-072 (#416), `bd version 1.3.0 (Homebrew)`. The executing session resolved it by hand: `bd gate resolve yf-mol-bpjz`, then `bd close yf-mol-uwmn --reason …`. Execution was unaffected.

## Cause

`skills/yf-plan/formulas/plan-execute.formula.toml` declares the start gate as one step:

```toml
[[steps]]
id = "start-gate"
title = "Begin: {{objective}}"
type = "gate"
[steps.gate]
type = "human"
```

`_find_start_gate_pair` (`plan_manager.py`, docstring cites REQ-PLAN-077) expects the pour to expand that one step into **two** beads: a wrapper **task** titled `Begin: …` and the real gate. It selects the wrapper with:

```python
wrappers = [c for c in children
            if (c.get("issue_type") or c.get("type")) == "task"
            and str(c.get("title", "")).startswith("Begin:")]
```

Under bd 1.3.0 the pour still produces both beads, but the wrapper's type is **`gate`**:

| bead | issue_type | title | depends on |
| :-- | :-- | :-- | :-- |
| `yf-mol-uwmn` | **gate** | `Begin: Enforce the Agent Skills 1024-char…` | `yf-mol-t42s`, `yf-mol-bpjz` |
| `yf-mol-bpjz` | gate | `Gate: human` | `yf-mol-t42s` |

The `== "task"` filter matches nothing, so the lookup reports inconclusive.

## Impact

This is a class, not a one-off: **every** plan poured with bd 1.3.0 hits it. Each execute session must notice the inconclusive verdict and close the wrapper by hand. That is the kind of manual step REQ-PLAN-077's machinery exists to remove, and a less careful session could leave the wrapper open. The work stays blocked then, because entry issues take the wrapper as a `--deps` predecessor.

Related but distinct: #179 (wrapper orphaned at pour, closed).

## Proposed fix

In `_find_start_gate_pair`, identify the wrapper structurally rather than by type. It is the `Begin:`-titled child that **depends on** a human gate under the same epic. The function already resolves the gate from the wrapper's `blocks` edge, so type is not needed to tell the two apart. At minimum, accept `issue_type in ("task", "gate")` for a `Begin:` title, and keep the existing "more than one wrapper → refuse to guess" guard. Add a test fixture in the bd 1.3.0 shape (both beads `gate`-typed).

Found by the parent session observing plan-072's execution via yf-herdr.


---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #207: resume-scan reports found: true for a BURNED epic, making the plan permanently unpourable (both SKILL.md 5.2 branches dead-end)

- **Number:** 207
- **Title:** resume-scan reports found: true for a BURNED epic, making the plan permanently unpourable (both SKILL.md 5.2 branches dead-end)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/207
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

## Summary

`resume-scan` reads the plan's epic id from `plan.md`'s `**Epic:**` field and **never checks whether that epic still exists in the tracker**. If the epic has been deleted (`bd mol burn`), it still reports `found: true` — and per `SKILL.md` §5.2 that makes the plan **permanently unpourable**, with no documented way out.

## Measured

After burning a corrupt molecule (`bd mol burn astrospike-mol-ppt --force` → *"Deleted 48 issue(s)"*), with `bd show astrospike-mol-ppt` returning `no issue found matching`:

```json
{
  "epic_id": "astrospike-mol-ppt",
  "epic_source": "plan_md",
  "found": true,
  "counts": {},
  "total": 0,
  "stuck": [],
  "open_work_remaining": 0
}
```

`found: true` for an epic that does not exist.

## Why it is a wedge, not a cosmetic flaw

`SKILL.md` §5.2 branches on exactly this field:

> - **`found` is `false`** — no epic yet. Under intake-at-execute this is the **normal first execution**: pour the molecule and create the beads (§5.2a).
> - **`found` is `true`** — an epic already exists (a prior, possibly crashed, execute session). Do **not** pour or create a second epic … Prompt the operator with `AskUserQuestion`: **Resume** the existing epic (recommended) or treat as **New**. On **New**, stop and tell the operator a fresh run requires a fresh pour — execute cannot fabricate a second epic.

So with a burned epic, both branches are dead ends:

- **Resume** → resumes against beads that no longer exist.
- **New** → **stops**, telling the operator a fresh run requires a fresh pour — which is precisely what they were trying to do.

Burning a bad molecule is the *documented* remedy for a corrupt pour (it is what #186/#187 required), so this is on the recovery path, not an exotic edge case.

## The shape of the fix

This is the same distinction this repo already fixed once in `doc_lint` — `not-selected` vs `no-such-path`, where two different facts shared one exit code and the conflation was the defect (#181). Here, three states are collapsed into one boolean:

| State | Correct handling |
| :-- | :-- |
| no epic recorded | pour (normal first execution) |
| epic recorded **and present** in the tracker | resume prompt |
| epic recorded but **absent** from the tracker | pour, or offer to clear the stale pointer |

Suggested: reconcile the recorded id against the tracker and return a distinct class (e.g. `epic_source: "plan_md"`, `found: false`, `stale_pointer: "astrospike-mol-ppt"`) so §5.2 can route the third state to the pour path while telling the operator the pointer was stale. `total: 0` / `open_work_remaining: 0` already hint at it, but SKILL.md branches on `found`, not on those.

A `--clear-epic` verb on `plan_manager.py` would also help — there is currently no sanctioned way to remove the `**Epic:**` field.

## Workaround

Manually deleted the `epic:` frontmatter key and the `**Epic:**` header field from `plan.md`, after which `resume-scan` returned `found: false, epic_source: "none"` and the pour path reopened. That is a hand-edit of a field `record-epic` owns, which is why it is worth a verb.


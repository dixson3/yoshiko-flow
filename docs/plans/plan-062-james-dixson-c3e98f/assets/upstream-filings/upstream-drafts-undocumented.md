---
type: Record
okf_spec: OKF-PLAN
title: '`assets/upstream-drafts/` is undocumented in every yf-plan `.md`'
upstream_action: gh issue create
plan: plan-062-james-dixson-c3e98f
discharges: 5.1
status: filed
upstream_url: https://github.com/dixson3/yoshiko-flow/issues/332
description: 'Draft body for a NEW upstream issue: the assets/upstream-drafts/ path that _land_upstream_rows reads is a string literal in plan_manager.py and appears in zero .md files under skills/, so a load-bearing convention is discoverable only by reading code (the #273 class).'
---
# Upstream filing draft — `assets/upstream-drafts/` is undocumented in every yf-plan `.md`

> **FILED** — https://github.com/dixson3/yoshiko-flow/issues/332
>
> Issue 5.1 of plan-062. The operator reviewed this draft on disk
> and authorized the write; the posted body was verified BYTE-EXACT by `gh issue view`
> read-back, not by exit code. Action taken:
> `gh issue create` against `dixson3/yoshiko-flow`. The title above is the intended issue title.

## What

`_land_upstream_rows` expects per-issue draft bodies at:

```
<plan_dir>/assets/upstream-drafts/<issue-number>.md
```

(`skills/yf-plan/scripts/plan_manager.py:7936` and `:7948`.)

That path appears **nowhere in any `.md` file** in `skills/`:

```
$ grep -rn 'upstream-drafts' skills/ --include='*.md' | wc -l
0
$ grep -rn 'upstream-drafts' skills/ --include='*.py' | wc -l
3
```

`SKILL.md` §1.3 enumerates what `init` creates (`findings/`, `diagrams/`, `assets/`,
`references/`, `reviews/`) and describes `assets/` only as "attachments, not diagrams".
Nothing says a landing will look inside it for files named after upstream issue numbers.

## Why it matters

The convention is **load-bearing and invisible**. A plan that does not create these files
gets `draft_present: false` on every upstream row, and discovers it at land time. An operator
reading every `.md` yf-plan ships cannot learn the path exists; the only source of truth is a
string literal in a Python file.

This is the same class as `#273` — an obligation that exists only where nobody looks.

## Suggested fix

Document the path and its naming rule in `SKILL.md` (§1.3's directory listing and §6's
landing description), and state which dispositions require a draft. Note that
`UPSTREAM_REQUIREMENTS["deferred"]` sets `requires_mention: False`, so the required set is
"rows requiring a mention", not "non-exclude rows" — that distinction is currently derivable
only by reading the code.

Found while executing plan-062 (`docs/plans/plan-062-james-dixson-c3e98f`), pass-4 C41.

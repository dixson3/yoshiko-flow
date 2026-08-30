---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #305 - gate_consistency.py: on the INCONCLUSIVE path
  --json is not honoured at all (plain text on stderr, empty stdout), and a caller
  error is indistinguishable from an absent plan'
---
# Upstream #305: gate_consistency.py: on the INCONCLUSIVE path --json is not honoured at all (plain text on stderr, empty stdout), and a caller error is indistinguishable from an absent plan

- **Number:** 305
- **Title:** gate_consistency.py: on the INCONCLUSIVE path --json is not honoured at all (plain text on stderr, empty stdout), and a caller error is indistinguishable from an absent plan
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Two defects in one invocation, found while running the conformance pass for **plan-060**. Surfaced
by the observer session; reproduced and extended here.

Both are instances of [#263](https://github.com/dixson3/yoshiko-flow/issues/263)'s class, and the
second is a **verbatim recurrence of the defect `REQ-CLI-016` was written to close** — in a script
that requirement does not cover.

## Defect 1 — a caller error is reported as a verdict about the plan

`gate_consistency.py` takes the plan **directory**. Handed the `plan.md` path it emits:

```console
$ uv run skills/yf-plan/scripts/gate_consistency.py docs/plans/plan-060-james-dixson-6a6ac9/plan.md --json
INCONCLUSIVE: plan.md not found under docs/plans/plan-060-james-dixson-6a6ac9/plan.md
$ echo $?
2
```

**The message names a path that does exist.** `docs/plans/plan-060-james-dixson-6a6ac9/plan.md` is a
real file — it is the file the caller *meant*. What the script means is *"`<that>/plan.md` does not
exist"*, but it renders the joined path in a way that reads as "your plan is missing its `plan.md`".

Two different facts share one signal:

| Fact | Reported as |
| :-- | :-- |
| the plan bundle genuinely has no `plan.md` | `INCONCLUSIVE: plan.md not found under <dir>`, exit 2 |
| **the caller passed a file where a directory was expected** | **identical** |

This is `doc_lint`'s `not-selected` vs `no-such-path` conflation ([#181](https://github.com/dixson3/yoshiko-flow/issues/181))
one script over, and the remedy is the one #181 already established: **classify first**. If the path
is a file named `plan.md`, either accept it (resolve to its parent) or refuse with a distinct
caller-error message — *"expected a plan DIRECTORY, got a file; did you mean `<parent>`?"* — rather
than a verdict about the plan.

`INCONCLUSIVE` is the right *severity* for a caller error, since nothing about the plan was
established. It is the *wording* that misattributes the fault.

## Defect 2 — under `--json`, the verdict goes to STDERR and stdout is EMPTY

Measured on the same invocation:

```console
$ uv run ... plan.md --json 2>/dev/null            # stdout only
                                                    # <- nothing
$ echo $?
2

$ uv run ... plan.md --json 2>&1 1>/dev/null       # stderr only
INCONCLUSIVE: plan.md not found under docs/plans/plan-060-james-dixson-6a6ac9/plan.md
```

So `--json` produced **no JSON at all**, on stdout **or** stderr, and the only diagnostic went to the
stream a capture does not read.

This is precisely what `REQ-CLI-016` was amended to forbid, in its own words:

> **The verdict JSON goes to STDOUT on EVERY path, including failure** — this requirement previously
> *claimed* the verb mirrored `close_cascade.py` while both of its failing paths in fact wrote to
> **stderr**. That was a measured live defect, not a documentation nit: SKILL.md §6.4 captures the
> verb with `GATE=$(…)`, which captures stdout only, so `echo "$GATE"` printed an **empty string** on
> exactly the path an operator needs to read.

`gate_consistency.py` is not a §6.4 chain step, so `REQ-COMPLETE-003`'s envelope rule does not bind
it and nothing caught this. But it **is** captured by callers the same way, and a caller doing
`GC=$(… --json)` gets an empty string and an exit code with no statement of what went wrong.

## Why it matters more than the invocation

The happy path is fine — a correct directory argument returns a clean envelope:

```console
$ uv run skills/yf-plan/scripts/gate_consistency.py docs/plans/plan-060-james-dixson-6a6ac9 --json
{
 "plan_dir": "docs/plans/plan-060-james-dixson-6a6ac9",
 "verdict": "PASS",
 "gates": 5,
 "findings": []
}
$ echo $?
0
```

So the script is well-behaved exactly where it is exercised, and mis-behaved on the two paths a
human hits when they get the argument shape wrong — which is when they most need a legible answer.

## Suggested remedy

1. **Distinguish the two facts.** Accept a `plan.md` path by resolving to its parent, or refuse with
   an explicit caller-error message. Do not render a caller error as a finding about the plan.
2. **Emit the envelope to stdout on every path**, including `INCONCLUSIVE` and internal errors —
   `{"verdict": "INCONCLUSIVE", "reason": ..., "remediation": ...}`. Keep the human line on stderr if
   useful, but stdout must never be empty under `--json`.
3. Consider whether `REQ-CLI-016`'s stdout rule should be generalised from the §6.4 chain to **every
   `--json`-bearing script in the repo**. This defect exists because the rule is scoped to a chain
   this script is not in, which is the "fixed in isolation" pattern #263 names.

## Provenance

Found during plan-060's conformance pass. The instrument itself was working correctly on the plan —
it caught a genuine self-satisfying capability gate at exit 1 — and this defect only appeared when
the same command was re-run with the argument shape a reader would naturally try.

🤖 Generated with [Claude Code](https://claude.com/claude-code)


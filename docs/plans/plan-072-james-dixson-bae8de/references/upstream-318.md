---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #318 - P0 okf.py: --skill before the subcommand is silently
  dropped, inverting scaffold into an incubator state-file rename (data loss)'
---
# Upstream #318: P0 okf.py: --skill before the subcommand is silently dropped, inverting scaffold into an incubator state-file rename (data loss)

- **Number:** 318
- **Title:** P0 okf.py: --skill before the subcommand is silently dropped, inverting scaffold into an incubator state-file rename (data loss)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## P0 — data loss: `--skill` before the subcommand is silently dropped, inverting scaffold into a state-file rename

Measured 2026-08-30 against `yf-skills v0.5.0` at `~/.claude/skills`, while running the `yf-okf-hygiene` corpus backfill on the `dixson3/writing` repo (plan-012, EXP-001).

### The defect

`okf.py:1943-1963` builds its subparsers with `parents=[common]`, so `--skill` and `--json` are declared on **both** the top-level parser and **every subparser**. The subparser's `default=None` then overwrites whatever the pre-subcommand value was. A flag typed in the natural place is silently discarded.

### The consequence is not cosmetic

With the flag dropped, the extension never resolves, `index_source` falls back to the `"README.md"` default (`okf.py:1261`), and `migrate` **renames the incubator's typed state file** — the exact operation `REQ-INCUB-040` forbids ("the state file *is kept … and is never renamed to `index.md`*"). No `okf_spec` is stamped.

### Two measured transcripts

**Correct — flag AFTER the subcommand:**

```
$ okf.py migrate inc1 --skill yf-incubator --dry-run
20 changes:
  scaffold-index  index.md
  scaffold-log    log.md
  add-frontmatter README.md {type: Incubator, okf_spec: OKF-INCUBATOR}
  ...
```

**Data-loss — flag BEFORE the subcommand:**

```
$ okf.py --json --skill yf-incubator migrate inc1 --dry-run
- rename README.md {'to': 'index.md'}
```

Same intent, same flag, opposite and destructive behaviour, no warning.

### Suggested fix

Either drop `--skill`/`--json` from the `parents=` set so the top-level value survives, or give the subparser copies `default=argparse.SUPPRESS` so an unset subparser flag cannot clobber a set top-level one.

### Relationship to #297

Filed separately rather than folded. #297 groups three **engine-logic** defects (`_INDEX_ENTRY_RE` blindness, INCONCLUSIVE collapsed to FAIL, `migrate` stranding the hybrid log). This is a fourth defect in a different layer — CLI argument wiring — and it is the only one of the four that destroys user data.

Source: `dixson3/writing` `docs/plans/plan-012-james-dixson-c324be/findings/exp-001-okf-incubator-spec.md` §4.


---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #187: CRITICAL: plan_extract.py carries no issue detail, so SKILL.md §5.2a's mechanical pour cannot populate --description (all beads empty)

- **Number:** 187
- **Title:** CRITICAL: plan_extract.py carries no issue detail, so SKILL.md §5.2a's mechanical pour cannot populate --description (all beads empty)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/187
- **State:** OPEN
- **Labels:** type::bug, priority::critical

## Body

## Summary

`skills/yf-plan/scripts/plan_extract.py` returns this per-issue schema, and nothing else:

```
['id', 'title', 'epic', 'line', 'lettered', 'depends_on', 'resolves_upstream']
```

The two-space-indented continuation bullets under each `- Issue N.M:` are scanned for
`depends-on:` and `resolves-upstream:` and then **discarded**. There is no `description`,
`detail`, or `body` field.

But SKILL.md §5.2a instructs the executor to drive bead creation from exactly this output:

> **Derive the DAG mechanically, do not transcribe it.** `_shared/plan_extract.py` reads
> `plan.md` into JSON — epics, issues, edges, gates — … Use it to drive the `bd create` calls
> above.

…where those `bd create` calls are:

```bash
ISSUE_BEAD=$(bd create "Issue ${issue_id}: ${issue_description}" \
  --description="${issue_detail}" -t task -p 2 ...)
```

**`${issue_detail}` has no source.** An executor following the instruction correctly produces beads
with empty descriptions, because the tool it was told to use does not emit that field.

## Measured impact

`dixson3/astrospike` `plan-001-james-dixson-9153de`: **35 of 35** poured task beads have an empty
`DESCRIPTION`. The DAG is otherwise perfect — 35/35 issues mapped, 53 edges, 0 unparsed, no
dangling refs — which is what makes this hard to notice. `bd show` renders:

```
○ astrospike-mol-ppt.1.1 · Issue 1.1: Instantiate … into this repo   [● P2 · OPEN]
DESCRIPTION
  (none)
```

## Why this is critical

The continuation bullets are not decoration — in a mature plan they carry **all** the substantive
instruction. plan-001 went through 7 red-team passes (5 independent, 3 of which executed commands
against the real tree). Every correction those passes bought lives in the bullets and **none of it
reached the beads**:

- "Declare the DO with `new_sqlite_classes`, never `new_classes`" — the key-value backend is
  unavailable to new accounts and fails *at deploy time*.
- The four-form grep in Issue 1.7 — measured to be the **only** control that catches a stale
  content-collection reference, because `astro check` does not error and `pnpm build` exits 0.
- Issue 1.6's two-different-lists asymmetry — listing `settings` in the directory-enumerating
  validator throws `ENOENT` at `astro:build:start`.
- Issue 1.7 as a **delta** against a recorded baseline, never "all four green" — three of six lint
  stages are already red on the unmodified fork.

An executor working from titles alone would rebuild most of the defects those rounds removed. The
plan is intact on disk; the executable artifact derived from it is not.

## Two framings, either acceptable

1. **Extractor gap** — add a `detail` field carrying the issue's continuation lines (minus the
   parsed `depends-on:` / `resolves-upstream:` bullets), so the documented mechanical pour works
   as written. Preferred: it keeps §5.2a honest.
2. **Doc gap** — if the extractor is deliberately edges-only, SKILL.md §5.2a must stop implying it
   can source `${issue_detail}` and say explicitly where descriptions come from.

Silently doing neither is the current state, and it fails closed-mouthed: `--strict` returns
`unparsed: []` and exit 0.

## Why nothing caught it

SKILL.md §6.4 gates completion on `_shared/pour_fidelity.py`, which compares the poured DAG to the
declared one. **That script is not shipped** — the installed skill has no `_shared/` directory
(`plan_extract.py` lives under `scripts/`). So the designated check for exactly this class cannot
run. Worth a separate issue, but it is why this reached execution.

## Related

Companion defect: #186 — `mask_inline_code()`'s output reaches the emitted title, blanking code
spans out of 4 of the same 35 issues.

Found while executing `dixson3/astrospike` plan-001.


---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #230: bd close REFUSES and EXITS 0 when the bead is blocked by an open dependency

- **Number:** 230
- **Title:** bd close REFUSES and EXITS 0 when the bead is blocked by an open dependency
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Found by plan-053 during its own execution. **This is the defect class plan-053 exists to
close, occurring in the tool plan-053 is tracked with.**

## The defect

`bd close <id>` on a bead with an open blocking dependency prints a refusal — and returns
**exit code 0**:

```console
$ bd close yf-mol-bh8.3.3 --reason "TEST"
cannot close yf-mol-bh8.3.3: blocked by open issues [yf-mol-bh8.3.2] (use --force to override)
$ echo $?
0
```

The refusal itself is correct and desirable. **Reporting it as success is not.** Every
non-interactive consumer branches on the exit code, so every one of them records a close that
never happened.

## Measured blast radius, in plan-053's own execution

Six issue beads — `2.3`, `3.2`, `4.4`, `4.5`, `5.0`, `7.1` — silently failed to close. The
ledger read `closed 32 / in_progress 12` while the corresponding work was complete, merged and
validated.

**Nothing inside the run detected it.** It was caught from outside, by an observer comparing
the bead ledger against the completion reports. The Reconcile Gate *would* have caught it — but
only after the upstream filings had already gone out, which is the worst possible ordering for
an outward-facing write.

## Suggested remedy

Exit non-zero on a refusal:

- **`2`** fits an INCONCLUSIVE reading — the instrument declined to act, and said why;
- **`1`** fits a FAIL reading.

Either is enormously better than `0`. `--force` already exists as the deliberate override, so
nothing about the current *behaviour* needs to change — only the code it reports.

## A caller-side note, for completeness

The head of the cascade was a caller error, not a `bd` defect: `bd close` accepts no `--notes`
flag (only `-f/--force`, `-r/--reason`, `--reason-file`), and five closes were issued with one
and errored outright. That half is recorded honestly in plan-053's retrospective rather than
blamed on the tool. It is mentioned here only because the combination — an unknown flag, plus a
refusal at exit 0 — is what made eleven failed closes completely invisible.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/plan-retrospective.md` § RE-005
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D6

Filed by plan-053 Issue 7.2.


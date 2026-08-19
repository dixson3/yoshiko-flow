# Capability-gate RED pre-work (Issues 0.6 / 0.6a — SC10c, SC10d)

Recorded 2026-08-19T23:02:36Z, before any Epic 1 or Epic 3 work landed.

## SC10c — each gate script exits 1 (capability ABSENT), NOT 127

An **explicit per-script loop**, one invocation and one recorded exit code each. A glob
(`scripts/gate-*.sh`) would collapse to a single invocation and record one code for two
scripts, which is why the loop is written out.

```
$ bash scripts/gate-run.sh scripts/gate-grammar.sh
  residue: 150 (baseline 150, target <= 54); plans still carrying unparsed: 33
  GATE: capability ABSENT — unparsed residue 150 exceeds the approval-fixed target of 54
  exit=1
$ bash scripts/gate-run.sh scripts/gate-relations.sh
  GATE: capability ABSENT — doc_lint.py declares no 'plan-relations' check kind (Issue 3.1 not landed)
  exit=1
```

| Script | Exit | Reading |
| :-- | :-- | :-- |
| `gate-grammar.sh` | `1` | capability ABSENT — residue is 150, target 54 |
| `gate-relations.sh` | `1` | capability ABSENT — no `plan-relations` kind yet |

Neither is `127`. A `127` here would mean the harness could not find the script, which
`gate-run.sh` remaps to `2` (INCONCLUSIVE) — an absent harness is not an absent capability.

## SC10d — a MISSING gate script is INCONCLUSIVE (2), never red

```
$ bash scripts/gate-run.sh scripts/gate-does-not-exist.sh
  gate-run.sh: HARNESS FAILURE — gate script not found: docs/plans/plan-048-james-dixson-ed68a5/scripts/gate-does-not-exist.sh
  gate-run.sh: reporting INCONCLUSIVE (2); an absent harness is not an absent capability.
  exit=2
```

And the 127 remap itself, driven with a script that exists but exits 127:

```
$ bash scripts/gate-run.sh <script exiting 127>
  gate-run.sh: HARNESS FAILURE — gate script '<tmp>/x.sh' exited 127, outside the declared {0,1,2} set.
  gate-run.sh: 127 is bash's command-not-found — a missing script or a missing tool, not an absent capability.
  gate-run.sh: remapping 127 -> 2 (INCONCLUSIVE).
  exit=2
```

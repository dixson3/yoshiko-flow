---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-001 - sandbox rehearsal of the yf-okf-hygiene backfill/restore round-trip. Refutes the plan premise - 8/8 target bundles halt, and restore --apply has three silent total-data-loss paths.'
---
# EXP-001: backfill → restore round-trip on real legacy bundles

**This experiment refutes the scoping decision that commissioned it.** Two independent
blockers, both measured on unmodified real input:

1. **The corpus run is a no-op today — 8/8 target bundles halt.**
2. **`restore --apply` is not a safe undo.** Three distinct paths lose data entirely, each
   reporting `verdict: pass`, `exit 0`.

Method: eight sandbox git repos, each a copy of real `docs/plans/plan-0NN-*` bundles committed
as a baseline with per-file `sha256` snapshots; the repo's real engine driven with `cwd` set to
each sandbox (`cmd_backfill`/`cmd_restore` use `Path.cwd()`). No repo writes.

## Approach Tested

**measured:** Eight sandbox git repos, each a copy of one or more real `docs/plans/plan-0NN-james-dixson-*`
bundles, committed as a baseline with per-file `sha256` snapshots. The repository's own engine was
invoked with `cwd` set to each sandbox — `cmd_backfill`/`cmd_restore` use `Path.cwd()` as the tree,
so the real script drives a sandbox corpus with no repository write.

Probes: dry-run vs apply; apply with `--record`; restore dry-run and apply; hash diff against the
baseline; `SIGKILL` injected inside `os.rename` at **both** swap windows; double-apply; post-backfill
mutation; non-git tree; untracked bundle; and a 7-bundle single-record run.

**inferred:** driving the real engine against sandbox copies — rather than reasoning about the code —
is what surfaced the halt profile and all three loss paths. None of them is visible by reading.

Residue: none. Sandboxes removed; `git status --porcelain` empty in the repository throughout.

## Result

### Blocker 1 — zero of the 8 bundles transform

Dry run over all 8:

```
halted 7 transformed 1
plan-010 legacy-readme halt ['objective-divergence']
plan-012 legacy-readme halt ['objective-divergence']
plan-013 legacy-readme halt ['objective-divergence']
plan-014 legacy-readme halt ['objective-divergence']
plan-021 legacy-readme halt ['objective-divergence']
plan-023 legacy-readme halt ['objective-divergence']
plan-026 legacy-readme halt ['objective-divergence']
plan-030 legacy-readme would-backfill []
```

`plan-010`, the nominated rehearsal bundle, halts:

```
"action": "halt", "halts": [{"kind": "objective-divergence",
  "legacy": "Rename all skills to yf- prefix and build a Rust 'yflow' CLI to manage skill
             install/upgrade lifecycle, distributed via homebrew, replacing install.{sh,py}",
  "plan":   "Rename skills to `yf-` prefix and build the `yf` Rust CLI"}]
"verdict": "fail", "exit": 1
```

**The cause is legitimate, not corruption.** `plan.md`'s H1 grew during re-scoping while
`README.md`'s `>` line did not — e.g. plan-026's H1 gained "…and add a new yf-markdown-format
skill…(#85)…". The guard is correctly detecting a real divergence; there is simply nothing in
the engine to reconcile it.

**The lone survivor then halts under `--apply`, on a guard the dry run never runs:**

```
"action": "halt", "halts": [{"kind": "phase-log-loss",
  "detail": "1 phase-log date(s) would be lost", "dates": ["2026-07-19"]}]
"exit": 1
```

**So the dry run is not a faithful predictor of apply.** `phase-log-loss` is computed only
after staging, inside the `if apply:` block (~L556-572), so `would-backfill` is a weaker claim
than it reads as. The halt is clean — `--record` was `{"bundles": []}` and the tree stayed
hash-identical.

`SKILL.md` L189-190 claims "31 legacy bundles, of which **7** halt on objective divergence." On
the population that actually remains, the halt rate is **7/8** — the easy bundles were done, and
what is left is the residue the guard fires on.

### Blocker 2 — `restore` is a `git checkout`, mislabelled as record-driven

**The record file contains no operations at all.** Verbatim:

```json
{"bundles": [{"bundle": "docs/plans/plan-026-james-dixson-6e0e2f", "class": "legacy-readme",
  "detail": {"member": "plan.md", "legacy_index": ["README.md"], "has_index": false},
  "member_skill": "yf-plan",
  "before": {"verdict": "warn"}, "after": {"verdict": "warn"}, "action": "backfilled"}]}
```

It is an **audit record**: a path plus a before/after verdict. Absent are every created,
deleted and modified path, the consumed `README.md`, and any content backup. `restore`
re-derives operations at restore time by `rglob`-ing the *current* bundle and running
`git ls-files --error-unmatch` per file. **The reversal mechanism is `git`, not the record.**

Round-trip **is byte-exact on the happy path** — 7 bundles from one record, `ops 105 unlinks 14
VERDICT pass EXIT 0`, every hash identical. But that is because `git checkout` restores
committed bytes, **not** because the transform is invertible.

Three ways it loses data, all `pass`/exit 0:

| Path | Measured result |
| :-- | :-- |
| **Non-git tree** | `git ls-files --error-unmatch` fails for every path → all 20 files classify `unlink`; compensating `git checkout` is a no-op. `SURVIVING FILES: 0`. **Entire bundle deleted, exit 0.** |
| **Untracked bundle** (a plan not yet committed — the realistic variant) | `ops: 21` → `count=0`. Total loss, exit 0. |
| **Post-backfill edits** | An operator edit to `plan.md`, a new `post-backfill-note.md`, and `diagrams/new.d2` were all destroyed: `unlink … new.d2`, `unlink … post-backfill-note.md`, `git-checkout … plan.md`. **No dirty-tree guard, no warning.** `restore` unlinks *every* untracked file in the bundle, transform-created or not. |

### Blocker 3 — the crash-recovery journal is unsound AND unreachable

**`recover()` has no CLI verb.** The four `add_parser` calls are `audit`/`assess`, `backfill`,
`reindex`, `restore`. An operator whose backfill crashed cannot invoke recovery — and
`backfill` never calls `recover()` on entry, so a stale journal is never noticed.

Even if reachable, both swap windows are mis-journalled:

**(a) Crash after rename 1 — the journal lies, and `recover()` destroys the forward-roll path.**
`j.write("S2")` runs *after* `os.rename(bundle, stash)`, so the S1→S2 transition is
un-journalled:

```
=== journal === "phase": "S1", "meaning": "staged, before rename 1"
=== dirs ===   plan-026-....okf-stash        (bundle ABSENT)
=== recover() === {"recovered": true, "phase": "S1", "action": "discarded staging; bundle untouched"}
--- bundle present? --- NO - STILL ABSENT after a 'recovered: true'
```

`recover()` reads S1, takes the "nothing irreversible happened" branch, **rmtree's the
transformed staging copy**, clears the journal, and reports success with the bundle gone. Data
survives only in an orphaned `.okf-stash` nothing points at. This contradicts the docstring's
claim that recovery "keys on the JOURNAL's recorded phase, never on directory presence — which
is exactly the distinction that makes S1 and S4 separable."

**(b) Crash after rename 2 — unhandled traceback:**

```
=== journal phase === S2
OSError: [Errno 66] Directory not empty: '...okf-stash' -> '...plan-026-james-dixson-6e0e2f'
```

Exactly the errno the module docstring cites as the reason the two-rename design exists.

### What the transform does (measured, plan-026, objective synthetically aligned)

19 files. `README.md` is **consumed** — deleted outright; only its `>` objective line survives
into `index.md`, and all File-map/Reading-order prose is discarded. `index.md` is created
(frontmatter `okf_version: '0.2'`, H1, the `>` objective, a portability sentence, a generated
19-member bullet listing). `log.md` is created **without frontmatter**, with 26 phase-log
bullets moved out of `plan.md`. Frontmatter (`type:` + `okf_spec:`) is added to every
non-reserved `.md`.

**`description:` is never stamped on any file** — the REQ-DATA-075 key is absent from the
transform's output, so a backfilled bundle still fails that convention.

**The audit verdict does not improve**: `"before": {"verdict": "warn"}, "after": {"verdict":
"warn"}` on all 7 transformed bundles.

### What is genuinely sound

`backfill --apply` is well-guarded on the happy path: staging, fsync'd journal, phase-log
equality, a post-condition hybrid assertion, clean halts, no residue. **Re-running over a
conformant bundle is idempotent** — `"action": "skip", "reason": "already conformant"`, exit 0,
tree byte-identical. **`restore --apply` is the dangerous verb, not `backfill`.**

### Batch-record behaviour

One `--apply --record` over 8: `checked 8 transformed 7 halted 1 exit 1`. The record correctly
names only the 7 transformed. But **`restore` accepts no bundle filter** (`--record`, `--apply`,
`--json` only) and issues one `git checkout` over all bundles — so a single record is safe only
if you intend to reverse the whole batch. Note a mixed run **exits 1 while having mutated 7
bundles**: an operator reading the exit code alone would conclude nothing happened.

## Implications for Plan

**The corpus run this plan was commissioned to perform is currently a no-op**, and its advertised
rollback is unsafe. That is not a scheduling problem; it is an engine problem, and it is why the
plan was rescoped (D6) to repair the engine and defer the transform.

- Any epic that assumed "backfill the 8 remaining legacy bundles" must first resolve
  `objective-divergence` — 7 bundles — and `plan-030`'s existing-`log.md` merge case separately.
- **`restore` cannot be the rollback for a corpus rewrite.** It is a `git checkout` with an unlink
  pass wearing a record-driven label, and the `--record` file offers no protection against any of
  the three loss paths because it carries no path list.
- **The journal is not sound and cannot be invoked**, so `SKILL.md`'s durability claim overstates
  what the code delivers — a docs-vs-implementation disagreement in its own right.
- The transform never stamps `description:` (REQ-DATA-075), so a backfilled bundle still fails that
  convention.
- Risk is concentrated in the wrong place from where one would guess: **`backfill --apply` is
  well-guarded; `restore --apply` is the dangerous verb.**

## Recommendations

1. **Do not treat `restore --apply` as the rollback for a corpus backfill.** Use a branch plus
   `git checkout`, or make the backfill a single reviewable commit. If `restore` stays, gate it:
   refuse when `git rev-parse --git-dir` fails, refuse when the bundle is untracked at HEAD, and
   refuse (or require `--force`) when the bundle is dirty relative to its post-backfill state.
2. **Make the record actually record.** Have `backfill --apply` write the per-path op list
   (created / deleted / modified + content hashes) it already knows at transform time, and have
   `restore` consume it instead of re-deriving from `rglob` + `git ls-files`. That alone closes the
   post-backfill-edits and untracked-bundle paths.
3. **Fix the journal ordering** — write `S2` *before* `os.rename(bundle, stash)` and `S3` *before*
   `os.rename(staging, bundle)`, so the recorded phase is always at least the physical phase. Add a
   `recover` CLI verb, wrap the S2 stash-rollback against errno 66, and have `backfill` detect a
   stale journal on entry.
4. **Resolve `objective-divergence` mechanically.** Prefer `plan.md`'s H1 as authoritative and offer
   `--reconcile-objective`, rather than 7 hand-edited READMEs nobody re-verifies.
5. **Move `phase-log-loss` into the dry-run path** (stage into a temp copy without the swap) so
   `would-backfill` means what it says. As it stands a dry run green-lights work that will halt.
6. If a transform proceeds: use **per-bundle records**, since `restore` has no per-bundle filter, and
   land `plan-030` separately — its existing-`log.md` merge is a distinct case from the other seven.

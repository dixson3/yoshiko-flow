---
type: Reference
okf_spec: OKF-PLAN
---
# `gh` unknown-label behavior and `bd` label creation — measured

Produced by **plan-040 Issue 1.1**, behind the *Scratch write for the label test* capability
gate (`yf-mol-win.6`), authorized by the operator on 2026-08-16 for a **scratch issue in
`dixson3/yoshiko-flow`** (the authorized option, not the throwaway-repo alternative).

This file falsifies **both halves** of the premise EXP-001 recorded as `[inferred]` (pass-1 C5).
All command output below is verbatim.

## Verdict

| `gh` fails? | `bd` creates? | Consequence |
| :-: | :-: | :-- |
| **yes** | **yes** | **restrict-and-drop is a DELIBERATE DIVERGENCE from bd — Issue 2.2 must say so** |

Both halves are now **[measured]**. Decision 5 (restrict-and-drop) stands, and risk **R1** is
retired: the premise held. The plan does **not** shrink — Epic 2's label-policy work (2.2) is
still needed, and it must now be worded as a *deliberate divergence* rather than as parity.

## Environment

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-16 -->

- `gh` 2.97.0 (2026-07-31)
- `bd` 1.1.2 (Homebrew)
- Repo: `dixson3/yoshiko-flow`

Label set **before** the test (the EXP-001 baseline — `type::molecule`, `type::chore`,
`type::decision` absent, no P4 label):

```
bug, deferred, docs, documentation, duplicate, enhancement, follow-on, good first issue,
help wanted, invalid, plan-033-followon, priority::high, priority::low, priority::medium,
question, type::bug, type::epic, type::feature, type::task, upstream-followup, web, wontfix
```

## Half A — does `gh issue create --label <nonexistent>` fail?

**Yes. Exit 1, and no issue is created.**

```console
$ gh issue create --repo dixson3/yoshiko-flow \
    --title "SCRATCH plan-040 Issue 1.1 label probe (delete me)" \
    --body "..." \
    --label "type::chore"
could not add label: 'type::chore' not found
EXIT=1
```

**It fails atomically** — a distinct finding beyond the plan's question, and load-bearing for
Issue 2.5's fail-closed verification contract. The failed create left **no orphan issue**:

```console
$ gh issue list --repo dixson3/yoshiko-flow --state all --search 'SCRATCH plan-040 in:title' --json number,title,state
[]
```

So an unknown label is rejected **before** the issue is created, not after. A gh-direct
implementation that passes an unknown label gets a clean failure with no partial upstream state
to reconcile — there is no "issue created but unlabelled" case to handle.

### Half A′ — is `gh label create` idempotent?

**Bare: no (exit 1). With `--force`: yes (exit 0).**

```console
$ gh label create "plan040-scratch-probe" --description "..." --color "ededed"
EXIT=0

$ gh label create "plan040-scratch-probe" --description "..." --color "ededed"
label with name "plan040-scratch-probe" already exists; use `--force` to update its color and description
EXIT=1

$ gh label create "plan040-scratch-probe" --description "..." --color "ededed" --force
EXIT=0
```

Recorded for completeness. Under restrict-and-drop the plan never creates a label, so this is
**not** load-bearing — it only matters if a future revisit (R6) reopens ensure-label-before-use,
in which case `--force` is the idempotent form.

## Half B — does `bd github push` create a missing label on demand?

**Yes.** A scratch bead `yf-nzdv` of type `chore` (label `type::chore` absent at the time) was
pushed via the **current** `bd github push` path:

```console
$ GITHUB_TOKEN=$(gh auth token) bd github push yf-nzdv
✓ Pushed 1 issues
EXIT=0

$ gh label list --limit 200 --json name -q '.[].name' | grep -E 'type::|chore'
type::bug
type::chore      <-- created by bd, did not exist before
type::epic
type::feature
type::task
```

This is the first **measurement** of the claim. EXP-001 rested it on the mere existence of
`upstream-followup` / `plan-033-followon`, which the plan itself flagged as circumstantial
(they could equally have been hand-made). They were not the evidence — this is.

### Incidental: `bd`'s dry-run also prints `✓ Pushed 1 issues`

```console
$ GITHUB_TOKEN=$(gh auth token) bd github push --dry-run yf-nzdv
  [dry-run] Would create in GitHub: SCRATCH plan-040 1.1 bd-label probe (delete me)
Dry run mode - no changes will be made
✓ Pushed 1 issues

Run without --dry-run to apply changes
EXIT=0
```

The success string is emitted **when nothing was pushed**. Independent corroboration for
scoping decision 4 and **SC7**: `Pushed N issues` is not evidence of a write, and replacing that
scrape with structural verification (a returned issue URL) is a correctness fix, not just a
tidying.

### Incidental: measured field mapping (evidence for Issue 2.1)

Issue #139 as `bd` rendered it, before deletion:

```json
{
    "number": 139,
    "title": "SCRATCH plan-040 1.1 bd-label probe (delete me)",
    "body": "Scratch bead for plan-040 Issue 1.1: does bd github push create a missing type::chore label on demand?",
    "labels": [
        { "name": "priority::medium", "description": "", "color": "ededed" },
        { "name": "type::chore",      "description": "", "color": "ededed" }
    ],
    "state": "OPEN",
    "assignees": []
}
```

Confirms, on a second bead independent of `yf-1656`→#132:

- `title` → title **verbatim**; `description` → body **verbatim**
- `issue_type` → `type::<t>`; `priority` 2 → `priority::medium`
- labels created at `color: ededed`, empty description
- **no bead-id backreference in the body** — the mapping is one-way in the body; `external_ref`
  on the bead is the only link

And `external_ref` was written back by `bd` on push:

```console
$ bd show yf-nzdv --json
external_ref: 'https://github.com/dixson3/yoshiko-flow/issues/139'
```

Issue 2.1 should treat this as a second sample, not a specification — R2 (a missed field) is
unaffected, since both samples are beads with no `notes`/`design` content to test.

## Reversal — every write undone

The gate authorized *"a deliberately small, reversible"* write. All of it was reversed:

```console
$ gh issue delete 139 --repo dixson3/yoshiko-flow --yes     # EXIT=0
$ gh label delete "type::chore" --yes                        # EXIT=0  (bd-created side effect)
$ gh label delete "plan040-scratch-probe" --yes              # EXIT=0
$ bd close yf-nzdv --reason "plan-040 Issue 1.1 probe complete; scratch artifact"
```

`type::chore` was deleted deliberately: leaving it would have **silently changed decision 5's
population count**. Decision 5 rests on the uncovered set being `chore` (2), `decision` (1) and
one P4 bead — 3 of 991. A lingering `type::chore` would have shrunk that to 1 as an artifact of
the test measuring it.

Baseline verified restored:

```console
$ gh label list --limit 200 --json name -q '.[].name' | grep -E 'type::|priority::|plan040'
priority::high
priority::low
priority::medium
type::bug
type::epic
type::feature
type::task

$ gh issue list --state all --search 'SCRATCH plan-040 in:title' --json number,title,state
[]
```

Bead `yf-nzdv` is closed, not deleted — it remains as an auditable record of the probe. Its
`external_ref` points at deleted issue #139, which incidentally makes it a **live fixture for
SC13**'s stale-ref case (a ref whose issue no longer exists must fail closed with a named
reason rather than create a duplicate).

## Consequences to carry forward

1. **Issue 2.2** — specify restrict-and-drop as a **deliberate divergence from `bd`**, with the
   rationale stated: `bd` creates labels on demand; gh-direct will not, because label creation is
   a write scope the plan declines to take for 3 beads in 991 (`context.md` "no label-write scope
   is needed" stands).
2. **Issue 2.5 / SC7** — `gh`'s unknown-label failure is atomic and pre-create, so the fail-closed
   contract needs no compensating-delete path.
3. **R1 is retired** — the premise held; the plan does not shrink.
4. **R6's revisit trigger is now sharper** — the divergence is deliberate and documented, so a
   growing uncovered set is a decision to revisit, not a bug.

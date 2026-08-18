---
name: Coordinator
role: orchestrate
model:
description: Drives the plan molecule's bead DAG to completion.
---

# Coordinator

Drives the plan molecule's bead DAG to completion.

## Inputs

- `EPIC` — epic bead ID
- `plan_dir` — plan directory path

## Resume orphan sweep

Implements the beads-authoring resilience contract (REQ-ORCH-008 resume detection,
REQ-ORCH-009 stuck-bead sweep, REQ-ORCH-010 ephemeral-vs-durable). Runs **only on a
resume** (SKILL.md §5.2 detected an existing epic and the operator chose Resume), and
**strictly before the ready loop and before any reconcile-trigger evaluation**. A crashed
prior session can leave beads `in_progress`/claimed; the ready loop skips those, so they
would silently stall.

1. Read the scan: `resume-scan "${plan_dir}" --json` reports the `stuck` list
   (`in_progress`/claimed beads) and descendant counts.
2. **Reset, never close.** For each bead in `stuck`, reset it to re-workable:
   `bd update <id> --status open`. Resetting (not closing) keeps the epic
   non-terminal, so the reconcile gate cannot auto-fire on a resumed-but-incomplete
   plan.
3. **Report, never guess.** Report — do not mutate — any bead the sweep cannot
   positively classify (e.g. orphaned `discovered-from` work, a bead `blocked` with
   no live blocker). There is no reliable bd-state signal separating disposable
   scratch from real work, so the close decision stays with the operator. **No bead
   is ever auto-closed.**
4. Re-run `resume-scan --json` to confirm `stuck` is empty, then enter the loop.

## Loop

**Continue to the next ready bead without operator input.** This is the loop's default and
needs no permission: under the autonomous level (REQ-AGENT-064) the coordinator drains the DAG
and halts *only* on the five declared stop classes. **An epic boundary is a REPORT, NOT A
STOP** — report progress and keep going in the same turn. The loop had no such instruction:
"blocked gate" appeared 11x across the skill while "continue to the next bead" appeared 0x, so
the continue case was unwritten rather than merely under-emphasised, and the only explicit
wait was also the loop's documented exit.

Repeat until `bd ready --json` returns no beads for this epic:

1. `bd ready --limit 500 --json` — filter to beads under `${EPIC}`
2. **Enumerate gates SEPARATELY — `bd ready` never returns them (D-7).**

   ```bash
   bd list --type gate --limit 500 --json     # open gates, WITH metadata
   ```

   Then for each gate under `${EPIC}`, evaluate it with the shared routine (see
   *Evaluating a gate*): resolve on PASS, and on FAIL report and route around it —
   never stop while other beads are ready.
3. `bd update <id> --claim --json`
4. `bd show <id> --json` — read metadata
5. If metadata specifies agent file, spawn sub-agent with that prompt. Otherwise execute directly. Pass context files from `plan_dir`.
6. **Verify the postcondition, THEN branch** — never close and assert success (see below).

### Step 6 — verify before close (D-8)

Step 6 used to be a single unconditional `bd close <id> --reason "Completed"`. That has **no
failure branch at all**: a bead that failed was recorded as having succeeded, and there was no
retry concept anywhere in the loop. Under autonomy that defect stops being cosmetic — with no
operator watching each bead, the close reason *is* the record. Autonomy without this branch is
net-negative, which is why D-8 pairs them.

**Verify first.** Establish that the bead's postcondition actually holds — run the check, read
the exit code, inspect the artifact. A step that prints `ok` without checking its postcondition
is the exact defect plan-044 existed to fix, one layer down.

```bash
# PASS — the postcondition was verified to hold.
bd close <id> --reason "<what was verified, and by which command>" --json

# FAIL — record the failure; do NOT close. Increment FIRST, then branch on the count.
bd update <id> --set-metadata yf_attempts=<n+1> --json

#   below the threshold → RE-QUEUE: leave the bead `open` so `bd ready` returns it again
bd update <id> --status open --json

#   at or above the threshold → ESCALATE (stop class 4): park it out of the ready set
bd update <id> --status blocked --json
```

**Why the branch sets `open` rather than `blocked` below the threshold — measured, not
assumed.** `bd ready` does **not** return a `blocked` bead (verified directly: a bead moved to
`blocked` disappears from `bd ready`). So marking every failure `blocked` would not re-queue it
— it would **silently drop it from the loop forever**, producing a DAG that drains to "empty"
with real work unfinished. That is a vacuous green of exactly the kind this plan exists to
eliminate, and it would have been introduced *by the failure branch meant to prevent it*.
`blocked` is therefore reserved for the escalation case, where parking the bead out of the
ready set is the desired behaviour rather than an accident.

**Close reasons must state what was VERIFIED, not what was intended.** `"Completed"` is a
claim about intent; `"tests green: 424 passed / 0 failed"` is a claim about an observation.
Only the second survives review.

### Step 6a — the attempt counter (`yf_attempts`)

`yf_attempts` lives in the bead's own bd metadata and is the mechanical basis of **stop class
4**. Without it, "scope ambiguity" is a loophole that re-admits arbitrary stopping — a prose
judgement can never trigger a stop class; only this counter can.

**Write it ONLY via `--set-metadata` / `--unset-metadata`.**

```bash
bd update <id> --set-metadata yf_attempts=<n+1> --json   # per-key; merges
bd update <id> --unset-metadata yf_attempts --json       # on close
```

`--set-metadata` merges per-key (measured: setting a second key leaves `yf_attempts`
intact). Whole-object `--metadata` would clobber sibling keys such as `upstream` and
`disposition`. The merge behaviour of `--metadata` is measured-true but **undocumented**;
`--set-metadata` states per-key intent explicitly and is therefore immune to a future
semantics change.

**Increment ON DETECTED FAILURE, never at claim.** Incrementing at claim would count Ctrl-C,
an OOM kill and a reboot as attempts — a crashed session would arrive at a fresh run already
part-way to escalation, and the counter would fabricate escalations rather than record them.
Only the step-6 FAIL branch increments. **Prefer the undercount:** it delays an escalation
rather than inventing one.

**Reset unconditionally on any transition into `closed`.** Not "on success" — on *closed*,
whatever the route. A stale count surviving a close would make the next legitimate failure of
that bead start from a poisoned baseline, and cross-resume accumulation is one of the four
measured false-escalation classes.

**Escalate only AT `N`.** Below `N` the loop **re-queues** (reset the bead to `open`); it does
not stop. At `N` it escalates: park the bead `blocked`, report, and write a
`plan-retrospective.md` entry with `stop_class: 4`.

**A failure RE-QUEUES, it does not stop.** Below the threshold the loop moves to the next ready
bead and revisits this one later; only `yf_attempts >= N` escalates. A single failure is not a
halt.

### Enumerating gates — three measured traps

**Trap 1 — `bd ready` never returns a gate bead.** Measured on a live repo: `bd ready`
returned 24 beads, **0** of them gate-typed, while the same repo held an open gate. The old
loop step 2 said "for gate-type beads" over the `bd ready` result, so **it has never fired
once**. Gates must be enumerated by their own query.

**Trap 2 — the default page silently truncates.** `bd gate list --all --json` returns **50**
records on a repo holding **117**, and **exits 0** with no warning. A sweep that reads the
default page sees a fraction of its input and reports success — the vacuous green this plan
exists to eliminate. **Always pass an explicit `--limit`** (or paginate) and, where it matters,
assert the returned count against a second query.

**Trap 3 — not every enumeration carries `metadata`.** The structured fields 3.1 writes
(`gate_type`, `test`, `test_class`, `cwd`) are only visible on some queries:

| Command | Scope | Carries `metadata`? |
| :-- | :-- | :-- |
| `bd list --type gate --limit N --json` | **open** gates | **yes** — use this for the sweep |
| `bd show <id> --json` | one gate | **yes** |
| `bd gate list --limit N --json` | open gates | no |
| `bd gate list --all --limit N --json` | all gates incl. closed | no |

So the sweep enumerates with `bd list --type gate`, not `bd gate list`. `bd gate list --all` is
for auditing the historical corpus, where the absent metadata does not matter.

*(`bd ready --include-gates` does **not** exist — the flag is rejected with `unknown flag:
--include-gates`, exit 1. Do not reach for it.)*

### Evaluating a gate — the one shared routine

The eager execute-start sweep (SKILL.md §5.2b) and this lazy loop path use **the same
routine**, so the two cannot diverge:

1. Read `gate_type`. **Absent → treat as `human`.**
2. `gate_type: human` → **never auto-resolve.** A green test is not consent. Surface it.
3. Read `test`. Absent, or `test_class: manual` → **INCONCLUSIVE**, not FAIL. An
   unrunnable test has established nothing, in either direction.
4. Otherwise run `test` in the address space `cwd` names (`repo-root` or `worktree`).
   - exit 0 → `bd gate resolve <gate-id>`
   - non-zero → FAIL. Report condition, test output and unblock instructions. If the gate's
     `Instructions:` define a deferral mechanism, execute it and continue; otherwise route
     around the gate and revisit when no other work remains (stop class 2).

### Address-space routing (worktree mode)

When §5.3 created a worktree (verdict `viable`), code edits and builds for a bead's work
target the worktree, never the primary checkout:

- **Sub-agent beads** run with **cwd = `.worktrees/<plan-id>`** (the worktree path; get it
  from `plan_manager.py worktree path "${plan_dir}"`). Direct (non-agent) code edits use
  `git -C .worktrees/<plan-id>` for git ops and write files under that path.
- **`bd` and `plan_manager.py` calls stay primary-side** — run them from the repo root, not
  the worktree. The shared Dolt DB resolves from anywhere (INV-2); the plan folder and
  `plan_dir`-relative verbs are primary-side (SKILL.md §5.4 address-space model).
- EXECUTE sub-agents must **NOT** use `isolation="worktree"` — that harness primitive spawns
  a disposable, auto-cleaned `.claude/worktrees/` tree (wrong lifecycle). The plan worktree
  is an explicit, persistent `git worktree` that survives until §6.2 teardown.
  (`isolation="worktree"` is reserved for INVESTIGATE-phase experiments.)
- **`uv` inside the worktree:** prefix `uv run …` with `env -u VIRTUAL_ENV` so uv resolves the
  worktree's environment, not an inherited primary `VIRTUAL_ENV`. Do **NOT** follow uv's
  `--active` suggestion inside a worktree — it targets the active (primary) venv, the wrong
  address space.

In **fallback (in-place) mode** there is no worktree: all edits land in the primary checkout
as before.

## Blocked gates

Drain all unblocked work before reporting blocked gates (beads-authoring REQ-ORCH-012). A
blocked gate is **not** a reason to stop while any other bead is ready — report it and route
around it. Reporting is not stopping.

Only when `bd ready` returns nothing **and** unclosed beads remain behind blocked gates has
the DAG genuinely stalled. That is **stop class 2** (a capability gate whose `Test:` exits
non-zero) — one of the five declared classes, reached mechanically by an exit code rather than
by judgement:
- Report gate conditions, test results, and unblock instructions
- Write a `plan-retrospective.md` entry for the stop
- **Then** hand the gate to the operator — there is, by construction, no other work to do

A gate whose own `Instructions:` define a **deferral mechanism** (e.g. tombstone the beads it
blocks with `bd close -r`) is *not* a stall: execute that mechanism and continue. Deferral is a
mechanism, not an intention — a gate that says what to do on failure has already told the
coordinator how to keep going.

## Reconcile trigger

When all execution beads (non-reconcile) close:
1. Reconcile gate auto-resolves
2. Load `${SKILL_DIR}/agents/reconciler.md` and dispatch

## Completion

The run is complete when `bd ready` is empty and no resettable stuck beads remain
(beads-authoring REQ-ORCH-014). **Do not close the epic or set status `complete` here** — that
is the RECONCILE §6.4 step's job, which **cascade-closes** every container in the plan tree
(intermediate epics **and** the top-level plan molecule, REQ-PLAN-067) bottom-up and halts
loudly on any still-open child. A bare `bd close ${EPIC}` at this point would leave intermediate
epics open under a closed molecule — exactly the #73 stale-container defect. Report that the bead
DAG is drained and **continue into Phase 6** — reporting drainage is not a request for permission.

**Proceed to RECONCILE (Phase 6) — an internal transition.** After the DAG is drained,
**continue directly into Phase 6 in the same session**. SKILL.md states plainly that *"The
coordinator IS the main session"*, so there is no one to hand back to: the old "hand back" /
"control returns to the SKILL.md main session" phrasing described a control transfer that does
not exist, and reads as a place to stop. It is a section boundary, not a handoff. In **worktree mode** the land-the-plane flow is the
reordered SKILL.md §6.1–§6.2: acquire the landing lock → `git merge --no-ff <plan>` from
the **primary** → validate the merged state (§6.1.5) → conservative push handoff → worktree
teardown. The coordinator does **not** merge or push; it reports completion.

**Git handoff (conservative — do NOT auto-commit or push).** Per the project's git
authority (beads-authoring REQ-ORCH-014), do not commit, push, or run `bd dolt push`
unless the active profile or the operator explicitly authorizes it. Report the handoff:

```bash
git status   # show what changed under ${plan_dir} (docs/plans/ or Incubator/<slug>/plans/) and .beads/
```

Then summarize for the operator: changed files, validation done, and the exact commands
you propose. In **in-place (fallback) mode** these are `git add "${plan_dir}" .beads/`,
`git commit -m "yf-plan: complete ${plan_id}"`, `git pull --rebase`, `bd dolt push`,
`git push`. In **worktree mode** the merge-back + validation already ran (§6.1–§6.1.5);
the proposed commands are just `bd dolt push` + `git push` of the validated merge. Run
them only on explicit authorization.

**Local-only guard (REQ-BINIT-027).** Before proposing either form, read
`bd config get dolt.local-only`. When it is `true`, **drop `bd dolt push` from the proposal
entirely** — the repo declares no Dolt replication target. Authorization-gating is not
sufficient here: it asks the operator to approve a command that should never have been offered.
Key the guard on the **config flag**, never on remote presence.

## Rules

- All task tracking uses `bd`. Never use `TodoWrite`, markdown checklists, or inline task lists.
- Drain all unblocked work before reporting blocked gates.
- New work discovered during execution: `bd create ... --deps discovered-from:<parent-id>`
- Update plan.md status as phases transition.

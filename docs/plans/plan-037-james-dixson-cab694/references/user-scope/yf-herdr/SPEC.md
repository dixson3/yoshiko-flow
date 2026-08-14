# SPEC — Herdr delegation & observation (`yf-herdr`)

> **Status: DRAFT.** Authored 2026-08-12 in `~/.claude/skills/` for hoisting into
> `dixson3/yoshiko-flow`. Requirements use RFC-2119 "shall". Not yet composed by the root macro
> spec; no `OKF-EXTENSION.md` member is claimed (this skill produces no artifact bundle).

## 1. Purpose & scope

`yf-herdr` delegates an **already-approved** `yf-plan` or an **already-gated** `yf-research`
project to a subordinate agent session in a new herdr tab, and then observes that session on the
operator's behalf — escalating what needs a human and mining execution deviations for defects in
the *planning* workflow.

It exists because `yf-plan` and `yf-research` both require a session boundary for execution
(`yf-plan` SKILL.md §4.6, REQ-PHASE-002), and because the parent session is the only vantage point
from which a plan's assumptions can be compared against what execution actually encountered.

**In scope:** the four-condition trigger, agent-kind matching, tab/agent launch, the
turn-boundary observation contract, deviation classification, and improvement reporting.

**Out of scope:** authoring or approving plans (`yf-plan`); driving panes for unrelated purposes
(`herdr`); resolving capability gates (**always** the operator); filing upstream issues without
authorisation.

## 2. Requirements (`REQ-HERDR-NNN`)

### 2.1 Trigger

- **REQ-HERDR-001** — The skill **shall** fire only when all four hold: `HERDR_ENV=1`; `herdr` on
  `PATH`; a **verified** readiness assertion for a specific plan/research project; and a
  **context-dirty** parent session. Failure of any condition **shall** produce an explanation, not
  a spawn.
- **REQ-HERDR-002** — Readiness **shall** be verified mechanically at trigger time, never inferred
  from conversation. For `yf-plan`: status `approved` **and** a non-stale fingerprint
  (`resume-scan` → `stale_approved: false`). A plan in `ready-for-approval`, or `approved` with a
  stale fingerprint, is **not** ready.
- **REQ-HERDR-003** — A **fresh** (non-context-dirty) parent session **shall** execute in place
  rather than spawning a tab. The session boundary is the only justification for a subordinate; a
  session with no boundary to cross gains nothing and loses the observer's co-location.

### 2.2 Launch

- **REQ-HERDR-010** — The subordinate **shall** run the **same agent kind** as the parent, resolved
  at run time by matching `$HERDR_PANE_ID` against `herdr agent list`. The kind **shall not** be
  assumed.
- **REQ-HERDR-011** — The tab **shall** be created in the parent's workspace
  (`$HERDR_WORKSPACE_ID`), with `--cwd` at the repository root and `--no-focus`.
- **REQ-HERDR-012** — All identifiers (pane, tab, agent) **shall** be parsed from JSON responses,
  never predicted or derived from display order.
- **REQ-HERDR-013** — The subordinate **shall** be given a stable short name, and that name plus
  its pane id **shall** be recorded in the parent conversation as the delegation handle.
- **REQ-HERDR-014** — At most **one** subordinate per plan/research project. A second spawn for the
  same target **shall** be refused — two sessions racing one bead DAG is a corruption hazard, not a
  parallelism win.

### 2.3 Observation

- **REQ-HERDR-020** — The skill **shall** state plainly at launch that observation occurs at
  operator turn boundaries and on demand, **not** continuously. A turn-based agent has no execution
  between turns; implying a watcher would be a false promise.
- **REQ-HERDR-021** — On each turn while a subordinate is live, the parent **shall** check
  `agent_status` and report material change.
- **REQ-HERDR-022** — `blocked` **shall** be read before any prompt is sent. A prompt delivered to
  a blocked agent is consumed by its open dialog and lost. (Observed live, twice.)
- **REQ-HERDR-023** — The parent **shall not** resolve a capability gate, and **shall** surface
  each gate with what authorising it actually accepts.
- **REQ-HERDR-024** — The parent **shall** answer a subordinate's question itself **only** when the
  answer is settled by existing approved plan content. Anything that changes scope, risk, or a
  success criterion **shall** go to the operator.
- **REQ-HERDR-025** — `idle`/`done` **shall not** be reported as completion without checking
  remaining beads; both states also occur when a subordinate is merely waiting.

### 2.4 Deviation mining

- **REQ-HERDR-030** — The parent **shall** watch for execution diverging from plan assumptions, and
  for each occurrence record: what was observed, what it implies about the planning process, and
  which skill owns the fix.
- **REQ-HERDR-031** — Each deviation **shall** be classified as a **one-off** or a **recurring
  class**, and the distinction stated. A class implies an upstream fix; a one-off may not.
- **REQ-HERDR-032** — Improvements **shall** be reported to the operator and filed upstream **only**
  on explicit authorisation. Auto-filing is prohibited: transient blips generate noise and
  duplicates, and only the operator can judge whether a pattern is real.
- **REQ-HERDR-033** — The deviation taxonomy **shall** be maintained as evidence accumulates. The
  seed classes in `SKILL.md` derive from observed executions, not speculation.

## 3. Deviation taxonomy — provenance

Each seed class comes from an observed execution, and three produced upstream issues:

| Class | Observed in | Filed |
| :-- | :-- | :-- |
| Premise refuted at execution (inference recorded as measurement) | plan-014 Issue 1.1 refuted plan-014 EXP-001's reboot claim | yoshiko-flow#114 |
| Gate condition unreachable from what it blocks | plan-013 PVE-OBS-001 gate | yoshiko-flow#112 |
| Precondition unavailable at DAG position | plan-013 Issue 3.4; Epic 6 ordering | yoshiko-flow#113 |
| Bead count at pour ≠ plan issue count | plan-013 poured 21 of 23 | — |
| Plan content edited mid-execution | plan-013 Issue 5.1 split; plan-014 reboot descope | — |

## 4. Non-goals

- **Not a scheduler.** No polling loop, no background execution, no cron.
- **Not a supervisor.** The subordinate owns its own execution; the parent observes and escalates.
- **Not an approver.** Every gate, every push, every upstream file stays the operator's.

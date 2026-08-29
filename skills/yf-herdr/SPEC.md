# SPEC — Herdr delegation & observation (`yf-herdr`)

> **Status: Active (plan-037, Epic 3).** Per-skill SPEC for the delegation-and-observation skill.
> Requirements use RFC-2119 "shall"; composed by the root `SPEC.md` macro spec (spec key `HERDR`,
> group `utility`). No `OKF-EXTENSION.md` member is claimed — this skill produces no artifact
> bundle.
>
> Originally authored 2026-08-12 directly in `~/.claude/skills/`, outside version control; plan-037
> imported it as first-class repo content. The pre-import snapshot is preserved at
> `docs/plans/plan-037-james-dixson-cab694/references/user-scope/yf-herdr/`.
>
> **Amendment log:**
> - **plan-037 (2026-08-13):** imported from user scope. Requirements were already `REQ-HERDR-*`
>   numbered and are carried over **unchanged** — the import corrected the skill's *packaging*, not
>   its contract. Status DRAFT → Active; the skill added to the root macro spec's §4 catalog.

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
  (`resume-scan` → `stale_approved: false`). A plan in `abandoned` is terminal and NOT
  execute-eligible, so it is never ready. A plan in `ready-for-approval`, or `approved` with a
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
- **REQ-HERDR-015** — §2.2 governs **prompt content**, not merely tab mechanics. The launch prompt
  **shall** carry three mandatory elements, and they are **requirements, not advice**: (a) an
  **autonomy directive** instructing the subordinate to run to completion, stopping only at the
  gates its plan declares; (b) the **push contract** of REQ-HERDR-026 (when to push, and that
  `--wait` is forbidden); and (c) the **parent handle** — the parent's own pane id, seeded as
  `YF_PARENT_PANE` via `--env` on `tab create` **and** restated in the prompt text. The pane id
  **shall** be preferred over the agent name: `HERDR_PANE_ID` is injected automatically and is
  stable, whereas a name exists only for `agent start`-ed agents and goes stale on rename. The
  three elements **shall** also be passed via `-- --append-system-prompt` so they survive the
  subordinate's context compaction. A launch that omits any of the three is **non-conformant**,
  not merely sub-optimal.

### 2.3 Observation

- **REQ-HERDR-020** — The skill **shall** state plainly at launch that the parent's **own polling**
  occurs at operator turn boundaries and on demand, **not** continuously — a turn-based agent has no
  execution between turns, so implying a watcher would be a false promise. This limit is a property of
  **pull**, and **shall not** be stated as a limit on observation as such: under REQ-HERDR-026 the
  subordinate pushes, so the parent learns of a material event without polling for it.
- **REQ-HERDR-021** — Polling is the **fallback**, not the primary channel. On each turn while a
  subordinate is live **and has not pushed since the last checked turn**, the parent **shall** check
  `agent_status` and report material change. Polling **shall** also be used to investigate a
  subordinate that has gone silent or reads `blocked` (REQ-HERDR-022). Where a push has already
  reported the event, a poll is corroboration, not the source of truth.
- **REQ-HERDR-022** — `blocked` **shall** be read before any prompt is sent. A prompt delivered to
  a blocked agent is consumed by its open dialog and lost. (Observed live, twice.)
- **REQ-HERDR-023** — The parent **shall not** resolve a capability gate, and **shall** surface
  each gate with what authorising it actually accepts.
- **REQ-HERDR-024** — The parent **shall** answer a subordinate's question itself **only** when the
  answer is settled by existing approved plan content. Anything that changes scope, risk, or a
  success criterion **shall** go to the operator.

  **The predicate governs a PUSHED question, not only a `blocked` one, and it has THREE arms.**
  As originally written it read as a two-way branch — answer it, or forward it — evaluated when a
  subordinate was observed `blocked`. Both halves were too narrow, and each was measured:

  1. **LOOK.** Before answering or forwarding, the parent **shall** read the artifact the push
     names. A push under REQ-HERDR-026 is a *notification about an artifact*, not the question
     itself; the message is one line and the question is a file. A parent that answers from the
     line alone is answering a summary. (Measured: plan-059's own E-1 was mis-forwarded because
     the predicate had no "look" arm and the one-line push was treated as the whole question.)
  2. **ANSWER** — only when settled by existing approved plan content, unchanged from above.
  3. **FORWARD** to the operator — anything touching scope, risk, or a success criterion.

  **A pushed question is a first-class input.** Under REQ-HERDR-026 a subordinate raises questions
  *without* going `blocked` — write-then-notify has no blocking step — so a predicate that fires
  only on `blocked` never fires on the ordinary case. The subordinate **shall** continue on its
  stated `on_no_answer` default while the question is outstanding: the transport has no
  answer-return primitive, so waiting is not an available behaviour and pretending otherwise
  converts an asking mechanism into a stall.

- **REQ-HERDR-025** — `idle`/`done` **shall not** be reported as completion without checking
  remaining beads; both states also occur when a subordinate is merely waiting.
- **REQ-HERDR-025a** — **`working` shall not be read as evidence of phase advancement.** The
  sibling of REQ-HERDR-025, and it fails in the opposite direction: where `idle`/`done`
  over-reports completion, `working` over-reports *progress*. `working` says a turn is in
  flight — nothing more. It is equally consistent with a subordinate that has advanced two
  epics and one that has been re-attempting a single bead for an hour, and the two are
  indistinguishable from the status alone. Phase advancement **shall** be established from the
  bead DAG or from a push, never inferred from `working`. Rationale: #264, where a parent read a
  long `working` stretch as progress through a phase the subordinate had not entered.
- **REQ-HERDR-027** — **`herdr agent prompt`'s exit code is NOT a delivery signal.** Delivery
  **shall** be verified **structurally** — by parsing the returned payload and requiring
  `result.type == "agent_prompted"` — and **shall not** be inferred from the exit code.

  **The evidence is a DISAGREEMENT between two measurements, and the disagreement is the
  requirement.** plan-059's EXP-004 measured `agent_not_found` returned **at exit `0`**; the
  same probe re-run during that plan's execution, against both a name target and a pane-id
  target, returned `agent_not_found` **at exit `1`**. Recorded as measured rather than
  reconciled — the two are a fortiori the same finding, because a caller that branches on `$?`
  is wrong under *one* of them and cannot tell which build it is running on. A signal that
  changed once will change again; the payload has been stable across both.
  A caller that branches on `$?` records a delivered push for a pane that does not exist. Three
  further channel facts are recorded with it, because each is undocumented and each silently
  degrades a push: a prompt delivered to a **`blocked`** agent is consumed by its open dialog and
  lost (REQ-HERDR-022); `agent_prompted` acknowledges **injection, not submission**
  (REQ-HERDR-026); and the metadata token channel is **display-only**, so a token is a
  postcondition to read back, never a message. An unparseable or unconfirmed response is
  **UNDELIVERED**, not delivered — an unreadable answer is not a yes — and a sender **shall**
  fail closed, leaving the notification un-stamped so the next boundary retries it rather than
  marking it sent. Rationale: plan-059 EXP-004 and R3. Verification:
  `skills/yf-herdr/scripts/test_herdr_channel.py`.
- **REQ-HERDR-028** — **Autonomy is derived from PROVENANCE, not asked for.** `YF_PARENT_PANE`
  set means a controller exists that can be asked, so the subordinate **shall** continue-or-ask
  and **shall not** go idle at a boundary; `YF_PARENT_PANE` unset means no controller exists and
  a human is present instead, so the artifact is the whole delivery and **zero pushes is the
  correct outcome**, not a degraded one. The variable is already seeded by REQ-HERDR-015(c), so
  this requirement adds a *reading* of an existing signal rather than a new one. Its practical
  consequence is that a push count of `0` under an unset `YF_PARENT_PANE` **shall not** be
  treated as a delivery failure. Rationale: #264 — a subordinate went `idle` at a phase boundary
  rather than asking, twice, under a contract that had already been tightened once; the operator
  named the real defect as **a silent idle**, not stopping as such.
- **REQ-HERDR-026** — Observation is **push-primary, polling-fallback**. The subordinate **shall**
  push to `YF_PARENT_PANE` at three trigger classes and no others: **epic completion**, a
  **blocker / failed gate / halt**, and **plan completion or abort**. It **shall not** push per
  bead — a plan-sized DAG would emit tens of messages and flood the parent's context. The push
  **shall not** use `--wait`: `--wait` reintroduces lockstep, and `--wait --until idle` is
  measurably wrong for a claude subordinate, which settles at `done` and never at `idle`, so the
  wait times out on a turn that in fact completed. Because `agent_prompted` acknowledges
  **injection, not submission**, every push **shall** be paired with an idempotent
  `herdr pane report-metadata --token` stamp on the subordinate's own pane, readable back via
  `pane get` / `agent get` / `agent list`; the token is the mechanical postcondition that makes the
  polling fallback a genuine backstop rather than a parallel mechanism. The parent's autonomy
  predicate is unchanged by this REQ: a pushed question is still answered by the parent **only**
  when settled by existing approved plan content (REQ-HERDR-024).

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

## 5. Verification

`yf-herdr` ships no scripts, so it has no Tier-1 suite. Its requirements are verified by:

- **Install parity** — `yf/src/testdata/install-parity.json` + `parity.rs` assert the skill is
  present in the embedded payload and in the `group:utility` closure.
- **Drift-check** — the manifest's glob-scoped `skill-md`, `skill-readme`,
  `frontmatter-contract`, and `per-skill-spec` edges cover `skills/yf-herdr/*` with no manifest
  edit; `frontmatter-contract` is what holds REQ-HERDR-040 (the `depends-on-skill` carve-out).
- **Observation** — REQ-HERDR-020..025 and the §3 taxonomy are **evidence-driven**: each seed
  class cites the execution that produced it, and REQ-HERDR-033 requires the taxonomy to be
  maintained as evidence accumulates rather than fixed at authoring time.

## 6. Dependency posture

- **REQ-HERDR-040** — `herdr` is a **third-party tool**, not an in-repo skill. The `SKILL.md`
  frontmatter **shall** declare it under `depends-on-tool` and **shall not** name it in
  `depends-on-skill`, whose values are bare in-repo skill names. The relationship to the
  third-party `herdr` skill **shall** be expressed as a **prose soft-dep** — present → delegate,
  absent → explain and hand the command to the operator — following the `yf-plan` ↔
  `yf-change-validation` precedent. Listing it as a hard dependency would be a force-install of a
  skill this repo does not ship.
- **REQ-HERDR-041** — The skill **shall** be inert where `herdr` is unavailable: `HERDR_ENV=1` is
  a trigger precondition (REQ-HERDR-001), so a CI runner without `herdr` never fires it.

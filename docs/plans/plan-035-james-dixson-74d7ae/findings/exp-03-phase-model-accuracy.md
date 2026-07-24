---
type: Finding
okf_spec: OKF-PLAN
---
## Finding: EXP-03 phase-model accuracy

Scope: validate the DOCUMENTED yf-plan phase model against the ACTUAL implementation
(`plan_manager.py`), the declared spec (`SPEC.md`, `spec/phases.md`), and the web docs
(`web/content/pages/lifecycle.md`, `workflows.md`), so the web docs + new diagram reflect reality.

### Ground truth: phases, statuses, transitions (cited)

**Declared source of truth (spec).**
- `skills/yf-plan/SPEC.md:25-30` (REQ-PLAN-001): the 9-value status vocabulary
  `scoping | investigating | drafting | review | ready-for-approval | approved | executing | reconciling | complete`,
  advanced only via `update-status`. `ready-for-approval` is a distinct, non-execute-eligible pre-approval state.
- `SPEC.md:31-32` (REQ-PLAN-002): phase machine
  `UPSTREAM → SCOPE ↔ INVESTIGATE → PLAN → INTAKE → (session boundary) → EXECUTE → RECONCILE → COMPLETE`;
  **no EXECUTE→PLAN transition**.
- `spec/phases.md:5-7` (REQ-PHASE-001): **7 phases** — UPSTREAM, SCOPE, INVESTIGATE, PLAN, INTAKE,
  EXECUTE, RECONCILE. Verification: `grep -c '## Phase [0-6]' SKILL.md` returns 7. **COMPLETE is not a
  phase** — it is the terminal *status* reached inside RECONCILE.
- `spec/phases.md:27` (REQ-STATUS-001): "Exactly 9 status values exist"; `:31-33` (REQ-STATUS-002):
  "Every phase transition sets status via `update-status`"; `:35-37` (REQ-STATUS-003): initial `scoping`
  set by `init`, not a separate `update-status`.
- `spec/phases.md:89-95` (REQ-COMPLETE-001/002): the RECONCILE close step (§6.4) runs
  cascade-close → complete-gate → set-complete; complete-gate is a no-op for `standard`/absent
  deliverable class, hard-gates only `ci-release`.

**SKILL.md (the documented model operators read).**
- Phase-Model diagram + status line: `SKILL.md:142-159`. Per-phase headings: Phase 0 UPSTREAM `:163`,
  1 SCOPE `:205`, 2 INVESTIGATE `:282`, 3 PLAN `:331`, 4 INTAKE `:492`, 5 EXECUTE `:599`,
  6 RECONCILE `:890`, and §6.4 Close (cascade-close → complete-gate → set complete) `:1014`.
- Phase→status mapping (from the per-phase `update-status` calls):
  - SCOPE → `scoping` (seeded at init) then `:275` sets `investigating`.
  - INVESTIGATE → `investigating`.
  - PLAN spans THREE statuses: `drafting` (`:334`) → `review` (`:402`) → `ready-for-approval` (`:478`,
    set only when `ready-check` is green).
  - INTAKE → `approved` (`:506`, after re-running `ready-check` per REQ-PLAN-066 adjacency).
  - EXECUTE → `executing` (`:793`, after start-gate resolve).
  - RECONCILE → `reconciling` (`:893`) then terminal `complete` (§6.4).
- Gate states inside PLAN/INTAKE: `ready-for-approval` (gated pre-approval, NOT execute-eligible,
  `SKILL.md:481`) and `approved` (post-consent, execute-eligible only with a *fresh fingerprint*).

**ACTUAL code (`plan_manager.py`).**
- `update-status` (`:1007-1036`) is **free-form**: its own docstring (`:1010-1011`) states it "accepts
  any status string and does **not** validate against an enum. The status vocabulary is the source of
  truth in SPEC.md … and the SKILL.md Phase Model line." There is **no `VALID_STATUSES` set, no enum,
  no transition guard** anywhere in the script (confirmed: no `VALID`/`_STATUSES` status constant; the
  only `_STATUSES` constant is `_STUCK_STATUSES = ("in_progress",)` at `:2383`, which is a *bead* status,
  not a plan status).
- Status literals the code actually hardcodes: `"scoping"` in `seed_plan_md` (`:432`, the init seed) and
  `"approved"` in the parked filter (`_is_parked`, `:1449`) and the intake commit-subject signal
  (`:1560`). Every other status value reaches plan.md only as a caller-supplied argument.
- CLI verbs that read/derive status: `list`/`status` (`:936`, tag overlays), `parked` (`:984`),
  `resume-scan` (`:2534`), `ready-check` (`:3110`), `complete-gate` (`:1285`),
  `classify-deliverable`/`set-deliverable-class` (`:1252`/`:1230`), `fingerprint` (`:1454`).
- Derived overlays surfaced to the user but NOT in the 9-value vocabulary:
  - `stale_approved` (`:1422-1432`): stored fingerprint ≠ current content; tagged in `list` (`:965`).
  - `parked` (`_is_parked`, `:1437-1449`): `status == "approved"` AND fresh stored fingerprint AND never
    executed; tagged in `list` (`:966`).
  - `deliverable_class` (`standard | ci-release`): a fingerprint-excluded **field** (`PLAN_FIELD_ORDER`
    `:52`), not a status.

**Web docs.** `workflows.md:26-93` reproduces the SKILL.md diagram and the 9-value status line
**verbatim** and documents every phase + all subagents accurately (INTAKE-at-execute pour, stale-approved
gate, merge-back-first, cascade-close all correct). `lifecycle.md` is a *different* abstraction — the
generic 5-stage skill lifecycle (install → preflight → invoke → coordinate/execute → land the plane),
not the yf-plan phase model; §4 (`:61-64`) collapses the phase model to a one-line "scopes → investigates
→ drafts → executes … merges back." No contradiction, but a reader could conflate the two.

### Drift found (doc vs code)

| Claim in docs | Reality in code | Correction |
|---|---|---|
| Diagram nodes imply COMPLETE is a phase (`RECONCILE --> COMPLETE`, SKILL.md:147, workflows.md:30) | Only 7 phases exist (REQ-PHASE-001); COMPLETE is the terminal *status* set by §6.4 *inside* RECONCILE (Phase 6). No `## Phase 7`. | Keep COMPLETE in the graph but render it as a terminal **status/state**, visually distinct from the 7 phase nodes. Do not label it "Phase 7." |
| REQ-STATUS-001/002 + REQ-PLAN-001 present the 9 values as an enforced vocabulary ("Exactly 9 status values exist"; "advanced only via update-status") | `update-status` is a free-form writer with **no enum/validation** (`:1010-1011`). A typo'd or invented status would be written silently; the "9 values" invariant is doc-enforced only, verified by `grep`, never by the code. | Accurate to say the vocabulary is *canonical in the docs*; **inaccurate to imply the code enforces it**. Docs should say the writer trusts the caller; the 9-value set is enforced by SPEC/tests + `grep` verification, not a runtime guard. (Optional impl hardening: add a validated set.) |
| Status line presents a flat 9-value list as if each maps 1:1 to a phase | PLAN maps to **three** statuses (`drafting → review → ready-for-approval`); SCOPE seeds `scoping` then moves to `investigating`; RECONCILE holds `reconciling → complete`. Mapping is many-to-one, not 1:1. | Diagram should group statuses *under* their phase band, showing PLAN owns drafting/review/ready-for-approval and RECONCILE owns reconciling/complete. |
| `stale-approved` (workflows.md:69) reads like a state; `parked` is surfaced in `list` output (`:966`) | Both are **derived overlays on `approved`**, computed from the fingerprint + execution history, not members of the status vocabulary. | Diagram/docs should show `approved` with two derived annotations (stale-approved ⚠, parked ⏸), not as sibling status nodes. |
| Phase-Model diagram shows UPSTREAM as the linear head of the per-plan sequence | `SKILL.md:165` Phase 0: "Runs **once per project** (persisted to CLAUDE.md), re-validated at start of each new plan." It is discovery, not a per-plan step. | Render UPSTREAM as a once-per-project preamble (dashed / distinct band), re-validated per plan — not an equal per-plan phase. |

### Is the model an accurate reflection of lived experience?

**Real-but-implicit — an accurate abstraction, not an inaccurate one.** The seven phases are the
*designer's* orchestration model. There are **no discrete phase announcements** in the runtime: the code
never emits "entering PLAN"; phases exist only as (a) `update-status` transitions written to `plan.md` +
`log.md`, and (b) the structure of the SKILL.md procedure the agent follows. What a user actually SEES is:

- **Status**, via `plan_manager.py list`/`status` output (with the ⚠ stale / ⏸ parked overlay tags,
  `:965-966`) and the `**Status:**` field in `plan.md`.
- **Phase-log lines** in the reserved `log.md` (`- scoping: …`, `- review: …`, `- reconciling: …`).
- **Gate prompts** — the human start gate (session boundary), the `ready-check`/approval prompt, and
  capability-gate stops.

So the operator's observable surface is **status + gate prompts + phase-log**, and phases surface only
*through* status. The operator who said "the phase model is not as explicit of an experience" is correct
about the experience but not about the model: the phases are genuinely there in the machinery — they are
just never narrated as discrete events. The abstraction is faithful (each phase has a distinct
responsibility and a distinct status footprint); it is simply *implicit*.

**What the docs should say about how phases surface:** add one explicit sentence to `workflows.md` (and
the new diagram's caption) — *"Phases are the internal orchestration model; you never see a 'now entering
PLAN' banner. They surface only as `status` values (shown by `/yf-plan status`), phase-log entries in
`log.md`, and the gate prompts at the session boundary and approval."* This closes the lived-experience
gap without changing behavior.

### Recommended validated model for the new diagram

Nodes = 7 phases; COMPLETE = terminal status; statuses grouped under their owning phase.

```
[once per project, re-validated per plan]
  UPSTREAM DISCOVERY  (persisted to CLAUDE.md; not a per-plan step)
        |
  ┌─────────────── per-plan sequence ───────────────┐
  |                                                  |
  SCOPE ⇄ INVESTIGATE  ── PLAN ── INTAKE ═══║═══ EXECUTE ── RECONCILE
  status:               status:   status:  session  status:   status:
   scoping               drafting  approved boundary executing  reconciling
   → investigating       → review                               → complete (§6.4)
   (scoping seeded        → ready-for-approval
    by init)              (gate: ready-check green
                           = last red-team APPROVE
                           + audit pass)
```

Backtracks (must be drawn): INVESTIGATE→SCOPE (findings revise scope, REQ-PHASE-003);
PLAN→INVESTIGATE and PLAN→SCOPE (draft reveals gaps, REQ-PHASE-004); PLAN internal REVISE loop
(red-team REVISE → fresh red-team cycle). **No EXECUTE→PLAN edge** (REQ-PLAN-002).

Status↔phase ownership for the diagram bands:
- SCOPE → `scoping`, `investigating` (shared with INVESTIGATE)
- INVESTIGATE → `investigating`
- PLAN → `drafting`, `review`, `ready-for-approval`  *(three statuses; ready-for-approval is a gate state)*
- INTAKE → `approved`  *(gate: re-run ready-check adjacency before flip)*
- EXECUTE → `executing`
- RECONCILE → `reconciling`, then terminal `complete`

Gate/annotation overlays to render (NOT status nodes):
- `ready-for-approval` = gated, non-execute-eligible (before approval prompt).
- `approved` carries two derived overlays: **⚠ stale-approved** (fingerprint drift → blocks EXECUTE) and
  **⏸ parked** (approved, fresh fingerprint, never executed).
- Session boundary (║) between INTAKE and EXECUTE; execute eligibility carried by the fingerprint, not
  in-memory state.
- `deliverable_class` (standard|ci-release) is a field feeding the §6.4 complete-gate, not a status.

### Implications for Plan

- The documented phase model is **substantially accurate**; the corrections are refinements (COMPLETE as
  status-not-phase, PLAN=3 statuses, UPSTREAM once-per-project, overlays vs statuses) plus one honesty fix
  (docs imply enum enforcement the code does not do).
- The new diagram is the highest-value deliverable: it can encode all four structural refinements the
  current ASCII diagram flattens.
- A small `workflows.md` caption addition closes the lived-experience gap.
- Optional (out of plan-035's likely doc scope): add runtime status validation to `update-status` to make
  the "9 values" invariant code-enforced rather than doc-only. File as a follow-up bead if desired; not
  required for doc accuracy.

### Recommendations

1. Build the new phase diagram per the validated model above (7 phase nodes, COMPLETE as terminal status,
   statuses banded under phases, UPSTREAM as once-per-project preamble, all backtracks, session boundary,
   ready-for-approval/approved gate states, stale/parked overlays). Use `yf-diagram-authoring` (d2).
2. In `workflows.md`, add one caption/sentence stating phases surface only via status, phase-log, and gate
   prompts — never as discrete announcements.
3. Correct the "COMPLETE" depiction in both `SKILL.md:147` and `workflows.md:30` so it reads as a terminal
   status of RECONCILE, not an 8th node/phase (keep it in the graph, restyle it).
4. Soften REQ-STATUS-001/002 doc language (or note it) so it does not imply runtime enum enforcement that
   the free-form `update-status` writer does not provide — OR (stretch) add the validation and keep the
   language.
5. Leave `lifecycle.md` as the generic 5-stage skill lifecycle, but add a one-line pointer clarifying it is
   NOT the yf-plan phase model (that lives in `workflows.md`).
</content>
</invoke>

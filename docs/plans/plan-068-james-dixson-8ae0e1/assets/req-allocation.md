# plan-068 — REQ id allocation record (Issue 0.2)

**Scope of this record.** Every `REQ-*` id that appears in **this plan's SPEC diff** — the diff
of `skills/yf-plan/spec/` and `SPEC.md` between the recorded execute base
(`assets/execute-base.txt`) and this plan's landed tip. Nothing else.

This is the single place the allocation is recorded. SC9b checks it **bidirectionally**:
every id in the landed SPEC diff appears in the table below, **and** every id in the table
appears in the landed diff. The one-directional form could never catch the over-claim pass-4 C6
found, which is why the check is written both ways.

## The allocation table

`role` is one of:

- **`new`** — a previously unused id this plan allocates and defines.
- **`amended`** — an existing id whose text this plan changes. **Consumes no new number.**
- **`referenced`** — an existing id this plan's SPEC prose cites without changing. Listed
  because it lands in the diff and SC9b's forward direction would otherwise flag it.

| REQ id | Role | Home | What this plan does to it | Issue |
| :-- | :-- | :-- | :-- | :-- |
| `REQ-LAND-037` | new | `spec/landing.md` | The `ctx.run` seam: every process a landing step launches **directly** goes through `LandingContext.run`; every *indirect* launcher reachable from an L-step is a declared ctx-less helper resolving its cwd from an explicit argument. Lands `LAND_CTXLESS_HELPERS`. | 0.3 |
| `REQ-LAND-038` | new | `spec/landing.md` | Merge-preview **directionality**: `_land_merge_preview.changed_paths` states what the merge **will land**, not the symmetric difference. Names `touches_skills` / L19's redeploy precondition as the derived consequence. | 0.5 |
| `REQ-LAND-002` | amended | `spec/landing.md` | L1 operates on the **execute branch**, not ambient HEAD, when there is no execute worktree. | 0.4 |
| `REQ-LAND-004` | amended | `spec/landing.md` | Records **L2's in-place behaviour as a declared scope boundary** — measured, not specified-then-unimplemented. Routes the L2 in-place work to plan-069. | 0.4 |
| `REQ-LAND-031` | referenced | `spec/landing.md` | **Carve-out RETIRED as an over-read** (pass-4 C3, verified). The requirement constrains the *call* (`force=False` in keyword form, branch on returned `status`) and says nothing about how the callee launches. Its text is **unchanged**; `REQ-LAND-037` records that the two are compatible. | 0.3 |
| `REQ-BRANCH-001` | amended | `spec/phases.md` | Extends the named-per-phase-branch model to a branch cut with **no `worktree add`** (the in-place path). | 0.6 |
| `REQ-BRANCH-002` | amended | `spec/phases.md` | Two clauses: (i) the pinned base applies to an in-place `checkout -b` as it does to `worktree add -b`; (ii) **the dirty-tree precondition** on the in-place path, as a declared refusal class. | 0.6 |
| `REQ-BRANCH-004` | amended | `spec/phases.md` | An **in-place carve-out** to "never left on a plan branch", which design (b) deliberately contradicts for the duration of in-place execution. | 0.6 |

## Decisions this issue was required to record

### 1. The dirty-tree refusal class gets NO new id — it is a clause inside `REQ-BRANCH-002`

pass-3 C8 caught v2 counting an *amendment* as an *allocation* and leaving Issue 0.6's
dirty-tree refusal class with no id at all. The decision recorded here: **a clause inside
`REQ-BRANCH-002`**, not a new number.

Two reasons, and the second is load-bearing:

1. **Substantive.** `REQ-BRANCH-002` already governs the operation the precondition guards —
   cutting `<plan-id>-execute` from a pinned base. A refusal class on that operation is a
   property of that requirement, not a separate one.
2. **Gate 1 is ONE-SHOT and has already been evaluated.** Its test alternation is
   `REQ-LAND-(037|038)`, and its Instructions say *"If 0.2 allocates further ids, extend the
   alternation."* Gate 1 exits 1 by design once `REQ-LAND-037` lands, so a third id allocated
   *after* the gate resolved could never be checked by it. Recording the refusal class as an
   amendment keeps Gate 1's evaluation **exactly coextensive** with what this plan allocates,
   rather than leaving a silently unchecked id behind.

**Consequence for the reader:** the new-id count for this plan is **two**, and two only.

### 2. `REQ-LAND-018` and `REQ-LAND-036` are NOT this plan's to allocate or amend

pass-4 C6 caught v3 over-claiming both. They belong to **plan-069**:

- `REQ-LAND-036` — the exclusion-table amendment (`resolved_target_tip`, `merge_preview`).
- `REQ-LAND-018` — the rationale amendment.

Issue 3.3 **verifies plan-069 carries them**; this plan neither performs them nor claims to.
Neither id appears in the table above, and neither may appear in this plan's SPEC diff. If one
does, SC9b's forward direction fails — which is the point.

### 3. `REQ-LAND-027` stays reserved

`spec/landing.md:384` holds it for a deferred requirement. This plan does not consume it.
`REQ-LAND-037` and `REQ-LAND-038` are the next two free numbers after `REQ-LAND-036`, both
verified at 0 occurrences across `spec/landing.md`, `spec/phases.md` and `SPEC.md` by Gate 1
before Issue 0.3 landed.

## Verifying this record (SC9b)

```bash
uv run docs/plans/plan-068-james-dixson-8ae0e1/assets/check_req_allocation.py
```

The checker extracts the id set from the table above, extracts the id set from the landed SPEC
diff against `assets/execute-base.txt`, and reports **both** set differences. It exits 0 only
when both are empty.

# Review Pass 1 — plan-007-james-dixson-84da0d

Two passes run in order: conformance (mechanical), then adversarial red-team. The red-team
verdict drives the phase transition.

## Conformance (Reviewer)

**Verdict: INCOMPLETE** (resolved in this revision)

- **Gates** — the Capability Gate declared type + condition but not **approvers** or a
  **test** for the condition. → **Resolved:** added `Approvers: none (auto-resolves)` and a
  `Test:` (`bd show <epic-1-id> --json` all-closed + `test -e protocols/DRIFT-CHECK-TRIGGER.md`).

All other conformance items passed: every epic ≥1 issue with single deliverables; dependency
graph acyclic and references valid; success criteria all name a command/file/grep; upstream
wiring vacuous by design (no incorporated issues); all portability sections present.

## Red-Team (adversarial)

**Verdict: REVISE** (all concerns addressed in this revision)

### Strengths (verbatim)
- Engine/manifest boundary is the right cut; exp-001 is real adversarial evidence (3 PASS + 1
  instructive FAIL), and the plan carries L1/L2 as honest scope limits rather than burying them.
- The E4 discovery (stale `check-prereqs.sh`, confirmed absent) is a genuine win — the
  generalization surfaced a latent bug and the plan files it as discovered work (2.3).
- Migration ordering is mostly safe: 3.1 (reduce the AGENTS files) is gated on 2.2 (engine
  reproduces E1–E3 first). Deleting source-of-truth only after the replacement is proven.
- Report-only/no-auto-fix is the right call and well-justified.

### Concerns + Operator Resolutions

| # | Severity | Concern | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | high | Trigger mechanism unresolved; migration destroys the always-loaded `@AGENTS` trigger and replaces it with a weak `description` heuristic on a `user-invocable: false` skill. | Resolved design decision: trigger = **always-loaded companion rule** (`protocols/DRIFT-CHECK-TRIGGER.md`, installed by `install.py`, mirroring optimal-instructions' `INSTRUCTIONS.md`) **+ manifest §6 globs**. Added **issue 1.6** (firing surface) and gated migration on it; reframed **issue 3.1** to preserve always-loaded firing and state what the CLAUDE.md includes become. | resolved |
| 2 | high | "Any repo" portability asserted, not demonstrated — only validated against this same-shape skills repo. | Added **issue 1.7**: paper-probe one structurally different artifact graph (API spec → generated client, or schema → migration → docs) before the schema/vocabulary freezes; downgrade objective to "this repo family" if it cannot be shown. Added matching success criterion + risk. | resolved |
| 3 | medium | No-manifest behavior undefined (silent no-op vs. nag on every edit). | Resolved design decision + folded into **issues 1.2 and 1.4**: no approved manifest → silent no-op; bootstrap only on explicit invocation / first install, never per-edit. | resolved |
| 4 | medium | Install-group invariant unstated (no-`utility`→`beads`; exact `depends-on-*`). | **Issue 3.2** now states and verifies `skill-group: utility`, `depends-on-tool`, `depends-on-skill`, and asserts the no-`utility`→`beads` invariant transitively. | resolved |
| 5 | medium | skill-authoring perceived redundancy in the flagship instance (both fire on `skills/*/SKILL.md`). | **Issue 1.1** description SKIP now names skill-authoring by the content-vs-authoring axis; **issue 3.3** acceptance adds an operator-overlap check on a real skill edit (legibly distinct axes, not redundant work). | resolved |

### Missing (red-team) → all closed by the revision
- Firing/trigger surface artifact → issue 1.6.
- `install.py` wiring for the companion rule → issue 1.6.
- How the CLAUDE.md `@AGENTS/*` includes are rewritten → issue 3.1 (must state what they become).
- Non-skills bootstrap evidence → issue 1.7.

### Gate Assessment
Start Gate (human/operator) correct. Capability Gate well-placed (engine-before-migration);
revised to also require the firing surface (1.6) and to declare approvers + test. 2.2 → 3.1
hard gate (prove reproduction before deleting source files) retained.

### Upstream Assessment
Vacuous — no upstream issues incorporated. Note carried forward: if concerns 1 or 2 had been
deferred rather than fixed in-plan, they would be filed upstream at land-the-plane. They were
fixed in-plan, so no upstream filing is required.

## Disposition

All conformance gaps and all red-team concerns (2 high, 3 medium) addressed in the plan
revision recorded under this same `review` phase-log entry. Plan is ready for the operator's
approve / revise-further decision. **Not auto-approved** — INTAKE requires explicit operator
approval.

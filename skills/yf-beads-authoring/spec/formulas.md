# Spec: Formula authoring

Contracts for `.formula.toml` authoring and the post-pour wiring that bd 1.0.5 forces.

## Requirements

- **REQ-FORMULA-001:** A `type = "gate"` step pours to **two** beads, both in `id_mapping`:
  `<formula>.<step-id>` (the wrapper, titled `Begin: …`, what downstream `needs`/`--deps`
  reference) and `<formula>.gate-<step-id>` (the actual `gate`, what `bd gate resolve` targets).
  *(amended plan-074, #417)* The wrapper's native type is **version-dependent** — `task` on
  `bd` 1.0.5/1.1.0, `gate` on 1.3.1 — so a consumer shall identify the two **only** by the pour's
  `id_mapping` keys (retained as evidence), never by type or title. On 1.3.1 `bd gate resolve`
  on the wrapper key **succeeds** and closes the wrapper while the actual gate stays open, so a
  closed wrapper is never evidence that the gate was resolved. — *Rationale:* on task-typed
  wrappers resolving the wrapper key fails (`not a gate issue`); on gate-typed wrappers it
  silently resolves the wrong bead; wiring downstream to the gate key strands work. — *Verify:* SKILL.md "Formula gate steps (1.0.5 gotcha)" §; cross-ref
  beads-extra REQ-CLI-007.

- **REQ-FORMULA-002:** A formula's `[[steps]]` encode only the **stable, declared shape** — work
  that always exists at pour time and always wires identically. Dynamic structure (per-run epics,
  fan-out, runtime gates) is injected post-pour via `bd create`/`bd batch`, wiring *beside* declared
  edges, never rewriting/removing one. — *Rationale:* a formula that needs its own declared `needs=`
  edge rewritten at intake is wrong-sized. — *Verify:* SKILL.md "Formula right-sizing" § test.

- **REQ-FORMULA-003:** Formulas stay flat — no step nests another step as a structural parent —
  because bd rejects a task blocking an epic. — *Rationale:* honors the epic-blocking limit
  (beads-extra REQ-CLI-005). — *Verify:* SKILL.md "Formula right-sizing" § structural-limit note.

- **REQ-FORMULA-004:** Fan-out uses the hybrid pattern: pour the fixed skeleton, then inject N
  dynamic beads (`bd create --parent --deps`) and batch their downstream edges (`bd batch`).
  — *Rationale:* bd's native expansion formula type is undocumented/immature. — *Verify:* SKILL.md
  "Dynamic fan-out (hybrid pattern)" §.

- **REQ-FORMULA-005:** Validate a formula with `bd mol pour <name> --dry-run` before wiring the
  full pipeline. — *Rationale:* catches structural errors before live intake. — *Verify:* SKILL.md
  "Beads formulas" § dry-run note.

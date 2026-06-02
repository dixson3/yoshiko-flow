# Spec: Formula authoring

Contracts for `.formula.toml` authoring and the post-pour wiring that bd 1.0.5 forces.

## Requirements

- **REQ-FORMULA-001:** A `type = "gate"` step pours to **two** beads, both in `id_mapping`:
  `<formula>.<step-id>` (a `task` wrapper, titled `Begin: …`, what downstream `needs`/`--deps`
  reference) and `<formula>.gate-<step-id>` (the actual `gate`, what `bd gate resolve` targets).
  — *Rationale:* resolving the wrapper key fails (`not a gate issue`); wiring downstream to the
  gate key strands work. — *Verify:* SKILL.md "Formula gate steps (1.0.5 gotcha)" §; cross-ref
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

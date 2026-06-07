# Upstream #6: bdplan: opportunistically generate mermaid architecture diagrams in plan.md

- **Number:** 6
- **Title:** bdplan: opportunistically generate mermaid architecture diagrams in plan.md
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Summary

Enhance the `bdplan` skill so that, when updating `plan.md` during any phase (SCOPE, INVESTIGATE, PLAN, RECONCILE), it opportunistically generates **mermaid diagrams** for architecture, data models, flows, and state transitions where visuals would improve communication — not just ASCII tables and prose.

## Motivation

Plans for non-trivial systems (editor internals, runtime topologies, event flows, compositor layering, tool-use loops) are much easier to review when the structural relationships are shown, not described. Pure prose scales poorly once more than three subsystems interact. Mermaid is:

- natively rendered on GitHub and most markdown viewers,
- text-first (diffable, mergeable, lives in the repo),
- quick for an agent to author (no graphical tooling).

## Proposed behavior

1. **Opportunistic embedding.** When writing sections of `plan.md` that describe multi-part architecture, lifecycles, state machines, or data models, include a mermaid diagram as a fenced ` ```mermaid ` code block adjacent to the prose. Pick the diagram type that fits the content (flowchart, classDiagram, erDiagram, sequenceDiagram, stateDiagram-v2, C4 component).
2. **PNG export to `assets/`.** Render each diagram to a PNG in the plan's `assets/` folder via `@mermaid-js/mermaid-cli` (available through `npx -p @mermaid-js/mermaid-cli mmdc`). Also save the `.mmd` source alongside the PNG so diagrams can be regenerated and round-tripped. Reference the PNG in the markdown as a fallback for renderers that don't support mermaid natively.
3. **Naming convention.** `assets/<kebab-case-slug>.mmd` and `assets/<kebab-case-slug>.png`, matching the section/topic they illustrate.
4. **Regeneration discipline.** Whenever a mermaid block is edited in `plan.md`, the matching `.mmd` file and PNG are regenerated. Consider a `plan_manager.py` helper like `render-diagrams <plan_dir>` that scans `plan.md` for ` ```mermaid ` blocks, syncs them to `assets/*.mmd`, and (if `mmdc`/`npx` is available) renders PNGs.
5. **Heuristics for when to diagram.** At minimum consider a diagram when the plan describes:
   - a system with more than two interacting components (flowchart / C4),
   - a data model with relationships (classDiagram / erDiagram),
   - a multi-step protocol or lifecycle (sequenceDiagram / stateDiagram-v2),
   - a layered architecture (flowchart with subgraphs),
   - a decision tree or state machine (stateDiagram-v2).
6. **Prereqs check.** Extend `/bdplan init` to verify `mmdc` or `npx` is available. If neither is present, warn the operator and fall back to mermaid-in-markdown-only (no PNG).

## Implementation sketch

- `skills/bdplan/SKILL.md` — add a section "Diagrams" describing the conventions and the heuristic triggers.
- `skills/bdplan/scripts/plan_manager.py`
  - Add `render-diagrams <plan_dir>` subcommand that:
    - Walks `plan.md`, extracts each ` ```mermaid … ``` ` block,
    - Writes/updates `assets/<slug>-NN.mmd` (slug derived from preceding heading),
    - Runs `mmdc -i … -o …` (or `npx -p @mermaid-js/mermaid-cli mmdc …`) if available.
  - Integrate into `/bdplan status` reporting so missing PNGs are surfaced.
- `skills/bdplan/agents/planner.md` — note that diagrams should be included when they improve communication.
- `skills/bdplan/agents/captor.md` — audit diagrams as part of portability checks (PNGs exist for every mermaid block).

## Acceptance criteria

- [ ] `/bdplan init` checks for `mmdc`/`npx`; warns if absent; still works in mermaid-source-only mode.
- [ ] `plan_manager.py render-diagrams <plan_dir>` extracts, syncs, and renders diagrams.
- [ ] Planner agent instructions mention the heuristic triggers for adding diagrams.
- [ ] A plan that embeds mermaid gets matching `.mmd` + `.png` artifacts in `assets/` automatically on status checks.

## Out of scope

- Choosing diagram content for every plan automatically (operator + agent judgment).
- Non-mermaid formats (PlantUML, Graphviz) — defer.
- Embedding interactive/SVG diagrams — PNG is sufficient for review.

## Related

Requested during plan drafting for a complex Emacs-like editor project; multi-subsystem architecture made prose-only plan.md updates hard to scan. Operator asked for mermaid + PNG workflow as a durable convention for bdplan going forward.

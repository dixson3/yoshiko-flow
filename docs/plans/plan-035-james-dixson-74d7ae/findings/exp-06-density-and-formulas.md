---
type: Finding
okf_spec: OKF-PLAN
---
## Finding: EXP-06 density audit + formula inventory

Read-only audit of the full web content set (`web/content/pages/*.md`, `home/hero.md`,
`cards/*.md`) plus the three shipped `.formula.toml` files and the `yf-beads-authoring`
vocabulary. Two catalogues follow: (A) a prioritized density/voice worklist, and (B) a
formula inventory with an ER-diagram spec.

### Part A — Density/voice worklist (prioritized)

Severity scale: **P0** = wall-of-text, must restructure; **P1** = dense, should restructure;
**P2** = minor, optional polish. Pages not listed (`usage.md`, `install.md`, `architecture.md`,
`hero.md`, all `cards/*.md`, `404.md`) are already appropriately chunked and are **not** flagged.

| Page | Section | Problem | Recommended restructure | Severity |
|:-----|:--------|:--------|:------------------------|:---------|
| `workflows.md` | yf-plan → phases → **EXECUTE** bullet (L65–75) | The canonical offender the operator named. One ~11-line bullet packs ≥6 distinct ideas: pour-once/resume gate, absent-vs-present epic branch, stale-approved hard gate, worktree location/branch/base, coordinator drive, in-place fallback. No visual breaks. | Promote EXECUTE to its own `####` sub-heading with 3–4 short paragraphs OR a 2-col table (Mechanism → What it does): "pour-once/resume gate", "stale-approved gate", "worktree", "in-place fallback". Consider a small state diagram (absent epic → pour; present epic → resume). | **P0** |
| `workflows.md` | yf-plan → phases → **RECONCILE** bullet (L76–82) | Second-densest. One bullet chains the entire merge-first ordering (acquire lock → merge `--no-ff` → validate-merged → commit → release), the conservative push, and the reconciler subagent — all as one run-on. | Split into an **ordered list** of the merge sequence (1. acquire lock … 5. release), then a separate short paragraph for push + reconciler. The ordering is inherently a numbered sequence and reads far better as one. | **P0** |
| `workflows.md` | yf-plan → phases → **COMPLETE** bullet (L83–88) | Fixed-order close (cascade-close → complete-gate → set complete) plus fail-loud semantics plus the standard-vs-ci-release gate distinction, all in one bullet. | Break into: a one-line "fixed order: cascade-close → complete-gate → set complete", then two short bullets (cascade-close fail-loud; completion gate standard vs ci-release). | **P1** |
| `workflows.md` | yf-plan → **Key mechanics** (L95–111) | Five sub-bullets, each a mini-essay (2–5 lines) restating phase mechanics already stated above. Redundant density — reads as a second pass over the same material. | Either cut (much duplicates the phase descriptions) or compress each to a single bolded lead + one sentence. Candidate for a "mechanics at a glance" table. | **P1** |
| `workflows.md` | **The yf-plan subagents** (L113–158) and **yf-research subagents** (L220–260) | 7 + 8 subagents, each a dense 4–7-line prose bullet mixing role, inputs, outputs, read-only status. Two long wall-of-bullets back to back. | Convert each subagent list to a **table**: Subagent \| Role \| Inputs \| Output \| Read-only?. Prose bullets this uniform are exactly what a table serves. Cuts scan time sharply. | **P1** |
| `workflows.md` | yf-research → phases (L174–207) | Six phase bullets, each 4–6 dense lines (retrieve/triangulate/synthesize/critique/refine/package) folding inputs, outputs, provider chain, and epistemic caveats together. | Same treatment as the plan phases: promote to short sub-paragraphs or a phase table (Phase \| Subagent \| Input \| Output). The inline "excludes X" context-isolation notes can move to a footnote or the subagent table. | **P1** |
| `harness-tune.md` | **Config merge** para (L61–65) + **An honesty note on surfaces** (L100–110) | Long unbroken paragraphs, multiple clauses each (union-only + format-preserving + bd-hook untouched + TOML trivia replay; then the surface_dir single-value-at-both-scopes explanation with two inline concrete examples). Wall-of-text between otherwise well-tabled sections. | Bulletize the config-merge guarantees (3 bullets: union-only, hook-block untouched, TOML trivia-preserving). For the honesty note, pull the two concrete examples (`opencode`, `codex`) into a tiny 2-row table (Harness \| config/rules dir \| skills dir). | **P1** |
| `beads-concepts.md` | **The upstream strategy** → "Follow-on work goes upstream, coarsely" (L119–133) | Three stacked dense paragraphs contrasting coarse push vs naive `bd dolt sync`, with the orthogonality caveat folded in. A lot of ideas per paragraph. | Split the "opposite of naive" contrast into a short before/after: naive = sync whole DB (dup beads); yf = scoped, push-only, dry-run-first. The Dolt-orthogonality sentence should be its own line or a callout. | **P2** |
| `why.md` | Intro paragraph (L7–10) | Single 4-sentence paragraph carrying the whole thesis (single-session limits + spans days/machines/people + needs investigation + durable artifacts + native mechanisms ephemeral). Front-loaded density on the landing narrative page. | Split into two paragraphs at "The native mechanisms…"; the problem statement and the ephemeral-builtins critique are two beats. | **P2** |
| `lifecycle.md` | **4. Coordinate / execute** (L56–67) | Mild — two bullets (yf-plan, yf-research) plus a resume paragraph. Already chunked, but the yf-plan bullet crams scope→investigate→draft→execute→merge into one arrow-chain sentence. | Optional: keep, or break the yf-plan bullet's arrow chain onto its own line. Low priority — this page is the lighter companion to `workflows.md`. | **P2** |

**Top-5 to fix (by severity, then blast radius):** (1) `workflows.md` EXECUTE bullet, (2)
`workflows.md` RECONCILE bullet, (3) `workflows.md` subagent lists → tables, (4)
`workflows.md` yf-research phase bullets, (5) `harness-tune.md` config-merge / honesty-note
paragraphs. `workflows.md` (19 KB, the largest page) dominates the worklist — it is the single
highest-leverage file to rework.

### Part B — Formula inventory (cited)

Vocabulary framing (from `skills/yf-beads-authoring/SKILL.md`): a **formula** (`.formula.toml`)
is *"the source of truth for what work exists and how it connects"* — a small, reusable,
versioned DAG pattern shipped inside a skill's `formulas/` dir (SKILL.md L45–47, L83–85). It is
**poured** (`bd mol pour <name> --var …`) into a concrete **molecule**: an epic bead plus real
child beads/gates with claimable ids (SKILL.md L94–104). A **wisp** (`bd mol wisp`) is a
lightweight/ephemeral molecule, burned with `bd mol burn <id> --force` (formula
`phase = "vapor"`). Formulas define *what work exists and how it connects*; **agents** define
*how each unit of work is performed* — "do not conflate the two" (SKILL.md L71). A `type="gate"`
step compiles to **two** beads in bd 1.0.5 (SKILL.md L137–150): `<formula>.<step-id>` (a **task
wrapper**, `Begin: …`, the `needs`-edge target) and `<formula>.gate-<step-id>` (the **actual
gate**, the `bd gate resolve` target). Formulas hold only the **stable declared shape**; dynamic
fan-out is injected post-pour via `bd create --parent … --deps …` (SKILL.md L152–190).

There are **three** shipped standard formulas.

**1. `plan-execute`** — `skills/yf-plan/formulas/plan-execute.formula.toml`
- **Purpose:** "Plan execution pipeline with upstream reconciliation" (L2). `type="workflow"`,
  `phase="liquid"` (persistent), `version=1`.
- **Vars:** `objective` (required), `plan_dir` (required) — L7–13.
- **Steps (declared):** exactly **one** — `start-gate`, `type="gate"`, human gate,
  `approvers=["operator"]` (L15–22). Title `Begin: {{objective}}`; resolved in a new session via
  `/yf-plan execute`.
- **Dependency edges (declared):** none in the toml — the formula is deliberately minimal.
- **Injected post-pour (at INTAKE, per the toml comments L24–33 + SKILL.md L182–183):** epics,
  issues, and capability gates are read from `plan.md`'s Epics/Gates sections and created as bd
  issues; **entry leaf issues wire to the start gate** (child epics do not — bd rejects a task
  blocking an epic). A **reconcile gate + reconcile step** are injected **only** when upstream
  issues are incorporated (any non-`exclude` disposition); the reconcile gate depends on all
  execution beads and auto-resolves when they close; the reconcile step depends on the reconcile
  gate.
- **Pour output:** the start-gate molecule (wrapper `plan-execute.start-gate` + gate
  `plan-execute.gate-start-gate`) plus the dynamically-created plan epic tree. Structure: *"Plans
  share no fixed downstream shape, so the formula is only the gate"* (SKILL.md L182–183).

**2. `plan-investigate`** — `skills/yf-plan/formulas/plan-investigate.formula.toml`
- **Purpose:** "Ephemeral investigation for plan scoping" (L2). `type="workflow"`,
  `phase="vapor"` (ephemeral → poured as a **wisp**), `version=1`.
- **Vars:** `objective` (required), `plan_dir` (required) — L7–13.
- **Steps (declared):** **none** — all steps are injected dynamically, one task bead per
  experiment identified during scoping (L15–17).
- **Dependency edges:** none declared; experiments are independent, each dispatched to an
  **investigator** subagent in a disposable worktree.
- **Wisp lifecycle (L18–24):** 1) create `bd mol wisp plan-investigate --var …`; 2) inject
  experiment beads as children; 3) execute investigators in worktrees; 4) **burn**
  `bd mol burn <id>` after findings captured. (This is the wisp that this very EXP-06 finding is
  a child of.)
- **Pour output:** an ephemeral epic (wisp) with N injected experiment task-children, discarded
  at burn — leaves no durable structure.

**3. `yf-research`** — `skills/yf-research/formulas/yf-research.formula.toml`
- **Purpose:** "Multi-phase research pipeline with source credibility scoring" (L2).
  `type="workflow"`, `phase="liquid"`, `version=1`.
- **Vars:** `topic` (required, L7–9); `mode` (enum `quick|standard|deep|ultradeep`,
  default `standard`, L11–14); `research_dir` (required, L16–18).
- **Steps (declared):** **7** static steps (all always exist — SKILL.md L184–186):
  - `gate` — `type="gate"`, human, `approvers=["operator"]` (L20–27). Entry gate.
  - `tooling` — `type="task"`, `needs=["gate"]` (L29–36). Build/validate collection scripts.
  - `triangulate` — `type="task"`, `needs=["tooling"]` (L39–44). Cross-reference + credibility.
  - `synthesize` — `type="task"`, `needs=["triangulate"]` (L46–51). Draft `Summary.md`.
  - `critique` — `type="task"`, `needs=["synthesize"]` (L53–58). Red-team, no `plan.yaml`.
  - `refine` — `type="task"`, `needs=["critique"]` (L60–65). May spawn `discovered-from` beads.
  - `package` — `type="task"`, `needs=["refine"]` (L67–72). Finalize + git handoff.
- **Dependency edges (declared, linear chain):**
  `gate → tooling → triangulate → synthesize → critique → refine → package`.
- **Injected post-pour:** **retrieve** beads (one per source cluster) wire IN **between `tooling`
  and `triangulate`** (toml L37–38 NOTE; SKILL.md L184–186) — no declared edge is rewritten
  (the canonical "right-sized" example).
- **Pour output:** a research epic + the 7 static beads (gate compiled to wrapper
  `yf-research.gate` + gate `yf-research.gate-gate`) + dynamically-injected retrieve fan-out.

### ER diagram spec (entities + relationships to draw)

A d2 ER diagram should show the **formula → poured molecule** lifecycle and the shared
vocabulary. Entities and relationships for the diagram author:

**Entities (with key attributes):**
- **Formula** — attrs: `formula` (name), `description`, `version`, `type` (workflow),
  `phase` (liquid | vapor). File: `<skill>/formulas/<name>.formula.toml`.
- **Var** — attrs: `name`, `required` (bool), `enum`/`default`. (A formula *has many* Vars.)
- **Step** — attrs: `id`, `title`, `type` (**task** | **epic** | **gate**), `description`,
  `needs[]`. (A formula *declares zero-or-more* Steps.)
- **GateSpec** — attrs: `type` (human), `approvers[]`. (A gate-typed Step *has one* GateSpec.)
- **Molecule** — attrs: `new_epic_id`, `id_mapping`. The poured instance.
- **Epic** (bead) — the container/root bead of a molecule.
- **Bead** — attrs: `id`, `type` (task | epic | gate), `status`. Concrete claimable unit.
- **Wisp** — a Molecule subtype where the source Formula `phase = "vapor"` (ephemeral, burnable).
- **Agent** — attrs: `path` (`agents/<name>.md`), bound to a Bead via metadata
  (`{agent, context}`), NOT part of the formula (keep visually distinct — "formulas define
  *what*; agents define *how*").

**Relationships (edges to draw):**
- Formula **1—N** Var ("declares").
- Formula **1—N** Step ("declares").
- Step **N—N** Step ("needs" / dependency edge — the DAG; show the linear chain for
  `yf-research`, and note `plan-*` inject theirs post-pour).
- Step(gate) **1—1** GateSpec ("configured by").
- Step(gate) **compiles to 2** Beads — a **task wrapper** (`<f>.<id>`) AND the **actual gate**
  (`<f>.gate-<id>`); wrapper is the `needs` target, gate is the `bd gate resolve` target. (This
  1→2 compilation is the single most important non-obvious edge to render.)
- Formula **1—1** Molecule ("poured via `bd mol pour`"); a `phase="vapor"` Formula pours to a
  **Wisp** ("`bd mol wisp`" → "`bd mol burn`").
- Molecule **1—1** Epic ("rooted at") **1—N** Bead ("parents").
- Step **1—1** Bead ("instantiated as", via `id_mapping`) — plus dynamically-injected Beads that
  have no declaring Step (fan-out; dashed edge, "injected post-pour via `bd create`").
- Bead **1—1** Agent ("dispatched to", via metadata) — dashed/orthogonal, labelled "how, not
  what".

Suggested diagram title: *"Formula → Molecule: the yf beads lifecycle."* Rendering note: the
three concrete formulas differ in the Step→Bead cardinality — `plan-execute` (1 declared step),
`plan-investigate` (0 declared, all injected, wisp), `yf-research` (7 declared + injected
retrieve). A single ER diagram should be **generic** (Formula/Step/Bead classes) with a small
callout table or inset listing the three instances, rather than three separate diagrams.

### Implications for Plan

- `workflows.md` is the dominant density liability (largest file, most P0/P1 sections). If the
  plan scopes a "voice/density pass," this file is the primary target; the EXECUTE and RECONCILE
  bullets are the specific canonical offenders the operator flagged.
- Restructures split cleanly into three mechanical transforms, each low-risk: (a) dense phase
  bullet → short sub-paragraphs or ordered list; (b) uniform prose bullet-lists → tables
  (subagents, phases); (c) run-on guarantee paragraphs → bullet lists (`harness-tune.md`). None
  require new facts — pure reflow, so drift risk is low.
- The ER diagram is a **new asset**, not a rework: it belongs beside the existing
  `/images/lifecycle.png` and `/images/architecture.png` on the `beads-concepts.md` or
  `workflows.md` page. `yf-diagram-authoring` (d2 → light-mode PNG) is the shipped tool; the spec
  above is sufficient input. The generic-with-inset approach keeps it to one diagram.
- SPEC-first note: web content is documentation, not spec-governed behavior — density edits do
  not require a `REQ-*` change. The ER diagram merely visualizes already-shipped formula
  behavior; no code changes implied.

### Recommendations

1. **Prioritize `workflows.md`.** Do the EXECUTE + RECONCILE bullets first (P0), then convert the
   two subagent lists and the yf-research phase list to tables (P1). This single file clears the
   top 4 of the top-5 worklist.
2. **`harness-tune.md`:** bulletize the config-merge guarantees and table-ize the honesty-note
   examples (P1). The page's existing tables are good; only the interstitial prose is dense.
3. **Author one generic Formula→Molecule ER diagram** (d2, via `yf-diagram-authoring`) using the
   entities/relationships above, with a 3-row inset for the concrete formulas. Render the
   gate-step 1→2 compilation explicitly — it is the least-obvious, most-cited mechanic.
4. **Lower-priority polish** (`beads-concepts.md` upstream para split, `why.md` intro split) can
   be batched into the same voice pass or deferred; they are P2.
5. Leave `usage.md`, `install.md`, `architecture.md`, hero, and cards **unchanged** — they are
   already well-chunked and adding a diagram/table there would be gold-plating.
</content>
</invoke>

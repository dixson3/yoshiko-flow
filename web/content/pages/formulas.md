Title: formulas
Slug: formulas
Subtitle: the reusable bead-DAG templates that yf skills pour into concrete work

A **formula** is a small, reusable bead-DAG template. It is a `.formula.toml` file that ships
inside a skill's `formulas/` directory. It declares the shape of a unit of work — the epic, its
child steps, the gates, and the dependency edges between them — as a versioned pattern. Nothing
is tracked until the formula is **poured**: `bd mol pour` instantiates it into a concrete tree of
[beads](/beads-concepts/) with real, claimable ids. A formula is one of the core building blocks
of a yf skill, alongside [skills](/architecture/) themselves, [plan states and phases](/lifecycle/),
[agents](/workflows/), and beads. This page defines the concept, documents the three shipped
formulas, and explains why a skill declares a formula instead of hand-creating beads.

## What a formula is

A formula separates *what work exists and how it connects* from *how each unit of work is
performed*. The formula owns the first half. It declares the DAG. It does not say who does the
work — that is the [agent](/workflows/)'s job, bound to a bead by metadata after the pour. Keep
the two distinct: formulas define what; agents define how.

A formula file carries a few top-level fields:

- `formula` — the template name (matches the file, `<name>.formula.toml`).
- `description` — a one-line summary of the pipeline.
- `version` — the schema version of this template.
- `type` — `workflow` for every shipped formula.
- `phase` — `liquid` for a persistent molecule, or `vapor` for an ephemeral [wisp](/glossary/).

Below the header sit two repeated blocks. A `[[var]]` block declares an input the pour must
supply — a name, whether it is `required`, and an optional `enum` or `default`. A `[[step]]`
block declares one node in the DAG — an `id`, a `title`, a `type` (`task`, `epic`, or `gate`),
and a `needs` list naming the steps it depends on.

## Pour, inject, burn — the lifecycle

A formula holds only the **stable declared shape**. Real pipelines also need work that is not
known until scoping time — one bead per experiment, one per source cluster. That dynamic work is
**injected** after the pour, not declared in the formula. The full lifecycle has three moves:

1. **Pour.** `bd mol pour <name> --var key=value` reads the formula and creates the molecule — an
   epic bead plus one bead per declared step, each with a real id. The pour returns the new epic id
   and an id-mapping from step id to bead id.
2. **Inject.** Downstream code creates the dynamic beads with `bd create --parent <epic> --deps
   <ids>`, wiring them into the poured DAG. No declared edge is rewritten; injection only adds.
3. **Burn** (vapor only). A `phase="vapor"` formula pours to a **wisp** via `bd mol wisp`. Once its
   purpose ends, `bd mol burn <id> --force` discards the whole wisp, leaving no orphaned beads.

## Gate compilation: one step, two beads

A `type="gate"` step does not compile to a single bead. It compiles to **two**. This is the
least-obvious mechanic in the model, so it is worth stating plainly.

- `<formula>.<step-id>` — a **task wrapper** bead (`Begin: …`). This is the target that downstream
  steps point their `needs` edges at.
- `<formula>.gate-<step-id>` — the **actual gate** bead. This is the target of `bd gate resolve`.

So a plan's start gate named `start-gate` becomes both `plan-execute.start-gate` (the wrapper) and
`plan-execute.gate-start-gate` (the gate a human resolves). Downstream beads block on the wrapper;
the operator resolves the gate; resolving it unblocks the wrapper, which unblocks the work.

## The five shipped formulas

yf ships **five** formulas. They span the full range of the model: zero declared steps, one, four,
a seven-step chain — and one that declares no steps of its own at all, because it is an **aspect**
that attaches steps to somebody else's.

| Formula | Skill | Type | Phase | Declared steps | Injected / woven |
| :------ | :---- | :--- | :---- | :------------- | :--------------- |
| `plan-execute` | [yf-plan](/workflows/) | workflow | liquid | 1 (a human `start-gate`) | epics, issues, capability gates, and an optional reconcile gate + step |
| `plan-investigate` | [yf-plan](/workflows/) | workflow | vapor (wisp) | 0 | one experiment bead per identified experiment |
| `plan-review` | [yf-plan](/workflows/) | workflow | vapor (wisp) | 4 (conformance → red-team → resolve → approval gate) | one `verify` step per declared step, woven by the aspect below |
| `verify-artifact` | [yf-plan](/workflows/) | **aspect** | — | 0 of its own | one `{step.id}-verify` task after every step of the formula that composes it |
| `yf-research` | [yf-research](/workflows/) | workflow | liquid | 7 (linear chain) | retrieve beads, fanned out between `tooling` and `triangulate` |

### Aspects, and when they weave

An **aspect** (`type = "aspect"`) declares no pipeline of its own. It declares **pointcuts** — a
glob selecting which steps it is willing to attach to — and **advice**, the step to inject
relative to each match. `verify-artifact` uses `glob = "*"` and injects one task *after* every
declared step.

Two details are load-bearing, and both fail **silently** if you get them wrong:

- **Aspects weave at COOK time, over formula-declared steps only.** The observation point is
  `bd cook <formula> --dry-run`, which renders the woven plan. `bd formula show` renders the
  **raw** formula and is *expected* to show no woven steps, as is a pour of an uncooked proto.
  Checking either of those and concluding the aspect does not weave is a reading error, not a bd
  defect.
- **The attachment is `[compose] aspects` in the CONSUMER**, never a top-level `aspects` key. A
  top-level key parses, cooks, and composes nothing — so an implementation using it looks correct
  in review and does nothing at runtime.

```toml
# in the consuming formula
[compose]
aspects = ["verify-artifact"]
```

The point of `verify-artifact` is that **a step which reports a verdict and a step which wrote the
file carrying it are different facts**, and only the second is checkable after the session ends.
Attaching the obligation as a step makes it *execute* rather than live in prose.

### plan-execute

`plan-execute.formula.toml` is the plan execution pipeline. It declares exactly **one** step: a
human `start-gate` of `type="gate"`, with `approvers=["operator"]`. You resolve it in a new
session by running `/yf-plan execute`.

Everything else is injected at intake. yf-plan reads the plan's Epics and Gates sections from
`plan.md` and creates them as beads. The entry leaf issues wire to the start gate; child epics do
not, because bd rejects a task blocking an epic. A reconcile gate and reconcile step are injected
**only** when upstream issues are incorporated. The reconcile gate depends on every execution
bead and auto-resolves when they all close.

The formula is deliberately minimal because plans share no fixed downstream shape. The declared
formula is only the gate; the plan tree is built dynamically.

### plan-investigate

`plan-investigate.formula.toml` is the ephemeral investigation used during plan scoping. Its
`phase` is `vapor`, so it pours as a **wisp**. It declares **zero** steps.

The wisp lifecycle runs in four moves:

1. Create the wisp: `bd mol wisp plan-investigate --var …`.
2. Inject one task bead per experiment identified during scoping.
3. Dispatch each experiment to an investigator subagent in a disposable worktree.
4. Burn the wisp with `bd mol burn <id>` once findings are captured.

The experiments are independent, so no dependency edges connect them. The wisp leaves no durable
structure — the findings persist, the tracking scaffold does not.

### yf-research

`yf-research.formula.toml` is the multi-phase research pipeline. It declares **seven** static
steps in a linear chain:

`gate → tooling → triangulate → synthesize → critique → refine → package`

The `gate` step is a human entry gate (`approvers=["operator"]`). The remaining six are tasks,
each with a `needs` edge on its predecessor. Because all seven are declared, they always exist in
every poured molecule.

The dynamic work is the **retrieve** fan-out. After the pour, one retrieve bead is injected per
source cluster, wired **between** `tooling` and `triangulate`. No declared edge is rewritten — the
injection slots into the existing chain. This is the canonical right-sized example: a stable
declared spine plus a data-dependent fan-out injected at run time.

## Why a formula, not hand-created beads

A skill could create its beads by hand each run, with a sequence of `bd create` and `bd dep`
calls. A formula is better on three axes:

- **Consistency.** Every pour of `plan-execute` produces the same start-gate shape. The DAG is
  defined once, reviewed once, and versioned. Hand-created beads drift run to run.
- **Lifecycle.** The pour / inject / burn model cleanly separates the stable declared shape from
  the dynamic fan-out. The stable part lives in the formula; the variable part is injected. A wisp
  can be burned as one unit rather than deleting beads individually.
- **Gate compilation.** The one-step-to-two-beads compilation for a gate is handled by the pour.
  Hand-creating a gate means remembering to build both the wrapper and the gate bead and to wire
  the `needs` edge to the wrapper — exactly the kind of detail a template gets right every time.

The formula is the source of truth for what work exists and how it connects. The skill pours it,
injects the run-specific beads, and lets the [coordinator](/glossary/) drain the DAG.

## The formula lifecycle at a glance

![Formula to molecule: a formula declares vars, steps, and gate specs; bd mol pour instantiates a molecule of an epic and concrete beads, with a gate step compiling to a task wrapper plus the actual gate, dynamic beads injected post-pour, and each bead dispatched to an agent](/images/formulas.png)

*Formula → Molecule: the yf beads lifecycle. A formula declares vars and steps; `bd mol pour`
instantiates a molecule of concrete beads; a gate step compiles to two beads (wrapper + gate);
dynamic beads are injected post-pour; agents are bound to beads to say how, not what.*

## Where to go next

- **[beads-concepts](/beads-concepts/)** — what beads is and the features formulas build on.
- **[workflows](/workflows/)** — the yf-plan and yf-research pipelines that pour these formulas.
- **[glossary](/glossary/)** — one-line definitions for formula, molecule, pour, wisp, and gate.

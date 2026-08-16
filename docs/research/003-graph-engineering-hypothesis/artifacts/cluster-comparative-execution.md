---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: comparative-execution

Evidence on execution-layer semantics in comparable agent-orchestration systems, organised as a
capability matrix. Scope: fan-out/join, conditional branching, loop/retry, checkpoint/resume, and
human-in-the-loop (HITL) gates. Feeds the secondary question *"what do comparable systems do at the
graph layer that yf does not"*.

Per `plan.yaml`, `bd`/beads is **not held fixed** — the execution-graph store itself is in scope, so
tracker-as-execution-store systems (§ Tier C) are treated as first-class comparables rather than as
background.

Per `plan.yaml` exclusions, the scientific/workflow-DAG lineage (Airflow, Dagster, Pegasus) was
deliberately not searched, and thought-leadership with no artifact behind it was discarded.

Citations: `[CE-N]` → `sources-comparative-execution.json`.

## Systems surveyed

Grouped by what they treat as the unit of execution.

| Tier | System | Unit of execution | Sources |
|:-----|:-------|:------------------|:--------|
| A — agent graph runtimes | LangGraph | node in a Pregel-style state graph | `[CE-1]` `[CE-2]` `[CE-3]` `[CE-4]` |
| A — agent graph runtimes | AutoGen GraphFlow | agent as a DiGraph node | `[CE-5]` `[CE-6]` |
| A — agent graph runtimes | Mastra Workflows | typed step in a chainable execution graph | `[CE-7]` |
| B — durable execution engines | Temporal | activity inside a replayable workflow | `[CE-8]` `[CE-9]` |
| B — durable execution engines | DBOS | annotated step checkpointed to Postgres | `[CE-10]` |
| B — durable execution engines | Restate | journaled handler invocation | `[CE-11]` |
| C — tracker-as-execution-store | ticks (`tk`) | issue ("tick") dispatched per dependency wave | `[CE-12]` |
| C — tracker-as-execution-store | clu | typed SQLite issue (task / checkpoint / milestone) | `[CE-13]` |
| C — tracker-as-execution-store | task-orchestrator (MCP) | work item with server-enforced transitions | `[CE-14]` |
| C — tracker-as-execution-store | yolo-runner | task from a pluggable tracker backend | `[CE-15]` |

Tier C is the tier yf's `bd`-backed design sits in.

## Capability matrix

Legend: **Y** = first-class primitive with cited evidence · **P** = partial / caveated ·
**?** = not established by the evidence gathered.

| System | Fan-out / join | Conditional branch | Loop / retry | Checkpoint / resume | HITL gate |
|:-------|:--------------:|:------------------:|:------------:|:-------------------:|:---------:|
| LangGraph | Y (`Send` fan-out; `defer=True` join, caveated) | Y (conditional edges) | Y (cyclic graphs; per-node retry policy `[uncertain]`) | Y (per-super-step + per-task pending writes) | Y (dynamic `interrupt()`) |
| AutoGen GraphFlow | Y (parallel fan-out + join node) | Y (edge conditions) | Y ("loops with safe exit conditions") | P (`save_state`/`load_state`; corrupts on mid-transition interrupt) | ? |
| Mastra Workflows | Y (`.parallel`, `.forEach` w/ concurrency limit) | Y (`.branch`) | Y (`.dowhile` / `.dountil` with `iterationCount`) | Y (suspend/`Run.resume()`; parallel-suspend bugs open) | Y (step-level suspend) |
| Temporal | ? (not searched) | ? (ordinary host-language control flow) | Y (declarative retry policy; `continue-as-new` for unbounded loops) | Y (event-history replay) | Y (signals / updates) `[uncertain]` |
| DBOS | P (durable queues) | ? (host-language control flow) | ? | Y (per-step Postgres checkpoint, replay short-circuits completed steps) | ? |
| Restate | ? | ? (host-language control flow) | Y (server may cancel/reset/retry invocations) | Y (server-side journal is ground truth) | Y (persistent futures / callbacks) `[uncertain]` |
| ticks (`tk`) | Y (dependency waves, one agent per ready tick, wave-by-wave merge) | ? | ? | P (branches/worktrees/notes as durable handoff; "any runner can resume any epic") | Y (approval / review / checkpoint gates) |
| clu | Y (`clu batch` computed fan-out; `milestone` auto-close as join) | P (conditionals live in the *generator*, not the graph) | ? (cascading cancel, not retry) | P (persistent SQLite + atomic claim) | Y (`checkpoint` issue type, `clu approve`) |
| task-orchestrator | Y (typed edges with linear / fan-out / fan-in shortcuts) | ? | ? | Y (`get_context()` returns full state in one call) | Y (server *blocks* the transition, not a prompt convention) |
| yolo-runner | Y (concurrency auto-computed from the graph) | ? | Y (retries owned by the runner) | ? | ? |

The `?` cells are genuine absences in the evidence gathered, not asserted absences in the systems —
see § Absence findings.

## Evidence per capability

### Fan-out / join

The strongest finding of this cluster is that **fan-out and join are separate primitives, and join is
where systems break.** LangGraph's scheduler is Pregel-derived:

> "LangGraph's underlying graph algorithm uses message passing to define a general program. When a
> Node completes its operation, it sends messages along one or more edges to other node(s). ...
> Inspired by Google's Pregel system, the program proceeds in discrete 'super-steps.' A super-step
> can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of
> the same super-step, while nodes that run sequentially belong to separate super-steps." `[CE-1]`

Fan-out is `Send` from a conditional edge; the join is a *different* mechanism, and using a plain
edge for it is the common failure:

> "A normal edge marks its target eligible the moment any single upstream task reaches it. With
> parallel branches — or worse, branches of unequal length ... the aggregator fires early, on
> whichever branch arrives first, and reduces over partial data." `[CE-4]`

And the supplied fix is deliberately blunt:

> "`defer=True` is not a dependency resolver. It does not build a graph of which nodes feed which and
> schedule accordingly. It is a scheduling barrier on the super-step queue — its entire semantics are
> 'run me when nothing else is left to run.'" `[CE-4]`

That is a *global* barrier, so an unrelated running subtree delays the reducer (head-of-line
blocking) `[CE-4]`. `[uncertain]` — `[CE-4]` is an LLM-authored blog with a human editor; its API
facts are corroborated by `[CE-1]`/`[CE-2]`, its framing is not independently confirmed.

AutoGen makes both halves explicit at the team level and derives entry/exit from graph topology:

> "DiGraphBuilder is a fluent utility that lets you easily construct execution graphs for workflows.
> It supports building: Sequential chains, Parallel fan-outs, Conditional branching, Loops with safe
> exit conditions." `[CE-5]`

> "the flow automatically computes all the source and leaf nodes of the graph and the execution
> starts at all the source nodes in the graph and completes execution when no nodes are left to
> execute." `[CE-5]`

Mastra exposes fan-out as typed combinators with bounded concurrency rather than as graph topology:

> "| Parallel | `.parallel([steps])` | Execute multiple steps concurrently | ... | ForEach |
> `.forEach(step, opts?)` | Execute step for each array element |" `[CE-7]`

with `executeForeach()` using "`fastq` for concurrent execution with a configurable concurrency
limit" `[CE-7]`.

In Tier C the join is expressed as *tracker state*, not as a scheduler construct. ticks computes
waves and treats merge as the join barrier:

> "ticks reads the dependency graph, decomposes it into waves, and runs each ready tick as its own
> agent in an isolated git worktree. Waves merge back wave by wave, unblocking the next." `[CE-12]`

clu reifies the join as an issue type:

> "a `milestone` issue *auto-closes* when all its dependencies close — the self-completing umbrella
> behind `clu batch --group` and phase boundaries." `[CE-13]`

task-orchestrator makes fan-in an edge *pattern* the store understands:

> "| Dependencies | `manage_dependencies`, `query_dependencies` | Typed edges with pattern shortcuts
> (linear, fan-out, fan-in) |" `[CE-14]`

and yolo-runner derives parallelism width from the graph rather than from configuration:

> "Smart Concurrency: Automatically calculates optimal parallel execution from dependency graphs"
> `[CE-15]`

### Conditional branching

Two distinct designs appear, and the split matters for a tracker-backed system.

**In-graph conditions.** Mastra evaluates predicates at runtime inside the engine:

> "| Conditional | `.branch([[cond, step]])` | Execute first step whose condition is true | Union of
> all branch outputs |" `[CE-7]`

with a deliberate capability restriction: "Conditions are `ConditionFunction` instances that receive
execution context but cannot call `setState` or `suspend`" `[CE-7]`. AutoGen likewise: "Edges can
optionally have conditions based on agent messages" `[CE-5]`; LangGraph's edges "can be conditional
branches or fixed transitions" `[CE-1]`.

**Conditions hoisted out of the graph.** clu states this trade-off explicitly — the graph is static
and acyclic; all conditional/computed structure happens in the *generator* that emits it:

> "This is the **generation / instantiation split**: any language emits the graph (loops,
> conditionals, computed fan-out — things a static template can't do); clu owns validation and atomic
> instantiation." `[CE-13]`

This is the single most transferable architectural idea in the cluster for a `bd`-backed design:
conditionality can be paid at *pour* time (regenerate the subgraph) instead of at *execution* time
(evaluate an edge predicate), and clu names that choice rather than falling into it.

The Tier B engines sidestep the question entirely — branching is ordinary host-language control flow
inside a durable function, which is why Temporal has no "conditional edge" concept to cite `[CE-8]`.

### Loop / retry

Temporal is the reference design, and its most useful contribution is *where* it places retry:

> "A Retry Policy is declarative. You do not need to implement your own logic for handling the
> retries; you only need to specify the desired behavior and Temporal will provide it." `[CE-8]`

Defaults are concrete: "Initial Interval = 1 second, Backoff Coefficient = 2.0, Maximum Interval =
100 × Initial Interval, Maximum Attempts = ∞, Non-Retryable Errors = []" `[CE-8]`.

Critically, retry is default-**on** at the leaf and default-**off** at the orchestration level, for a
stated reason:

> "Retrying an entire Workflow Execution is not recommended due to the deterministic nature of
> Workflow replay. Since Workflows replay the same sequence of events to reach the same state,
> retrying the whole Workflow would repeat the same logic without resolving the underlying issue that
> caused the failure. ... Instead, retry failed Activities within the Workflow, which is Temporal's
> default behavior." `[CE-8]`

For unbounded loops, Temporal has a named pattern that is a close analogue to an agent session
exhausting its context window:

> "Continue-As-New completes the current Workflow execution and atomically starts a new one with the
> same Workflow ID. The new execution begins with a fresh event history while preserving logical
> continuity. You pass state as arguments to the new execution." `[CE-9]`

> "Without Continue-As-New, you must manually stop and restart Workflows (losing continuity), risk
> hitting history limits and Workflow failures, implement external orchestration to manage Workflow
> lifecycle, and accept degraded performance as history grows large." `[CE-9]`

Mastra carries loops as first-class combinators with an iteration counter available to the predicate:

> "| Do-While Loop | `.dowhile(step, cond)` | Execute step, repeat while condition is true | ... |
> Do-Until Loop | `.dountil(step, cond)` | Execute step, repeat until condition is true |" `[CE-7]`
> ... "Loop conditions are `LoopConditionFunction` instances that receive an `iterationCount`
> parameter" `[CE-7]`

AutoGen advertises "Loops with safe exit conditions" `[CE-5]`. In Tier C, the closest primitive found
is *not* retry but reverse-direction cancellation:

> "Cascading cancel: `clu cancel` walks the dep graph forward and cancels the whole tail." `[CE-13]`

`[uncertain]` — LangGraph does expose per-node retry policies, but no source retrieved in this
cluster states so; that cell is marked provisional rather than cited.

### Checkpoint / resume

The clearest gradient in the matrix. LangGraph checkpoints at two granularities:

> "LangGraph creates a checkpoint at each **super-step** boundary. A super-step is a single 'tick' of
> the graph where all nodes scheduled for that step execute (potentially in parallel)." `[CE-2]`

> "In addition to super-step checkpoints, LangGraph also persists writes at the **node (task) level**.
> As each node within a super-step finishes, its outputs are written to the checkpointer's
> `checkpoint_writes` table as task entries linked to the in-progress checkpoint. These per-task
> writes are what enable pending writes recovery: if another node in the same super-step fails, the
> successful nodes' writes are already durable and don't need to be re-run on resume." `[CE-2]`

The resume cursor is an explicit identifier, not implicit session state: "The checkpointer uses
`thread_id` as the primary key for storing and retrieving checkpoints. Without it, the checkpointer
cannot save state or resume execution after an interrupt" `[CE-2]`. Checkpointing also buys
time-travel and forking: "checkpointers make it possible to fork the graph state at arbitrary
checkpoints to explore alternative trajectories" `[CE-2]`.

DBOS reaches the same guarantee through memoised replay rather than snapshots:

> "As the workflow re-executes, it checks before each step if that step's output is checkpointed in
> Postgres. If there is a checkpoint, the step returns the checkpointed output instead of executing."
> `[CE-10]`

with a stated cost model — "one database write per step ... plus two additional database writes per
workflow" `[CE-10]` — and an explicit warning that step outputs are the write-size driver, so large
artifacts should be pointers, not payloads `[CE-10]`. That is directly relevant to a tracker-backed
store where step "output" is a document.

Restate is the contrarian position on *where* the state lives, and argues the store should be
purpose-built rather than a general database:

> "The server's view on an invocation and its journal is the ground truth; the services follow the
> server's view and function executions may be cancelled/reset/retried as needed." `[CE-11]`

> "This stands somewhat in contrast to the common wisdom 'don't build a new stateful system, just use
> Postgres'." `[CE-11]`

**The negative evidence here is the most useful.** AutoGen GraphFlow ships `save_state`/`load_state`
but the scheduler's readiness queue is not crash-consistent with it:

> "When a GraphFlow workflow is interrupted (e.g., via `KeyboardInterrupt`) during the transition
> between agents, the saved state becomes corrupted. On resume, the workflow terminates immediately
> with: `Digraph execution is complete` —even though agents still have remaining work." `[CE-6]`

> "The GraphFlow coordination mechanism is interrupted before it can enqueue the next agent, leaving
> the system in an inconsistent state: Remaining work exists, No agents are enqueued, The workflow
> appears 'complete' but is actually stuck." `[CE-6]`

Issue #7043 was opened 2025-09-20 and remains open with linked fix PRs `[CE-6]`. The failure mode —
*derived* scheduler state (a ready queue) persisted alongside, but not atomically with, the graph —
is exactly the hazard a tracker-backed design avoids by deriving readiness from the edges on every
query instead of storing it.

Tier C's resume story is materially weaker and rests on durable side-effects rather than on a
journal. ticks: "with branches/worktrees/notes as the durable handoff format so any runner can resume
any epic" `[CE-12]`. task-orchestrator makes rehydration a single call — "A new session picks up
exactly where the last one left off — persistent state, not conversation replay" `[CE-14]`, with
"`get_context()` returns full state in one call" `[CE-14]`. None of the Tier C systems surveyed
checkpoint *mid-task* progress; the task is the atom, and a crash re-runs it whole.

### HITL gate

Three architectural placements, cleanly separated.

**Dynamic, code-level (LangGraph).** The gate is a function call, not a graph annotation:

> "Interrupts allow you to pause graph execution at specific points and wait for external input before
> continuing. ... When an interrupt is triggered, LangGraph saves the graph state using its
> persistence layer and waits indefinitely until you resume execution." `[CE-3]`

> "Unlike static breakpoints (which pause before or after specific nodes), interrupts are dynamic:
> they can be placed anywhere in your code and can be conditional based on your application logic."
> `[CE-3]`

Two caveats stated against the vendor's own interest are worth carrying: re-entrancy —

> "The node restarts from the beginning of the node where the `interrupt` was called when resumed, so
> any code before the `interrupt` runs again" `[CE-3]`

— and the interaction of gates with fan-out, which requires identity-keyed resumption:

> "When parallel branches interrupt simultaneously (for example, fan-out to multiple nodes that each
> call `interrupt()`), you may need to resume multiple interrupts in a single invocation. When
> resuming multiple interrupts with a single invocation, map each interrupt ID to its resume value."
> `[CE-3]`

**Step-level suspend (Mastra).** Gates attach to steps, and the surface is a `.resume()` call
`[CE-7]`. Mastra's own tracker shows the fan-out interaction is unsolved there too: `foreach` "parallel
suspended iterations lose `suspendPayload` after a sibling resumes" (issue #15552, surfaced in
search; not separately cited). `[uncertain]`

**Store-enforced gate (Tier C).** Here the gate is a *record*, and the store refuses to advance:

> "a `checkpoint` issue is a manual gate (stays `checkpoint:pending` until `clu approve`)" `[CE-13]`

task-orchestrator states the design principle most sharply, and it is the strongest single claim in
the cluster for a tracker-backed execution layer:

> "The enforcement happens at the tool level: if a required design note isn't filled, `advance_item`
> returns an error. If a dependency isn't satisfied, the transition is blocked." `[CE-14]`

> "| Enforcement | Instructions that agents should follow | Server blocks the call if rules aren't
> met |" `[CE-14]`

> "Dependency ordering is enforced by the server — structurally, not by convention." `[CE-14]`

ticks confirms gates are considered table stakes in this tier: "Humans stay in the loop via
approval/review/checkpoint gates" `[CE-12]`.

## Cross-cutting observations

1. **Fan-out is easy; join is the recurring defect.** Every Tier A system ships fan-out as a
   first-class primitive, and in every one the join is either a second, weaker mechanism (`defer` as a
   global queue barrier `[CE-4]`) or a source of open bugs. A design that gets join right —
   dependency-derived rather than queue-derived — is differentiating, not table stakes.

2. **Store the edges, derive the readiness.** The AutoGen resume bug is a *derived-state persistence*
   failure: `ready: []` was persisted separately from `remaining` and drifted `[CE-6]`. Systems that
   compute readiness from edges on every query (`tk ready`, `clu ready`, `bd ready`) are structurally
   immune to that specific class of corruption. This is an existing yf strength worth naming as such.

3. **Conditionality can be paid at generation time.** clu's "generation / instantiation split"
   `[CE-13]` shows a static acyclic graph can express loops, conditionals, and computed fan-out
   provided the *emitter* is a program and instantiation is transactional ("a single bad entry aborts
   everything, so you never get a half-built graph" `[CE-13]`). For a `bd`-backed system this is the
   alternative to adding edge predicates to the store.

4. **Retry belongs at the leaf, not at the orchestration.** Temporal's stated rationale — replaying an
   orchestration reproduces the same decisions and does not address the cause `[CE-8]` — transfers
   directly to a plan/epic vs. bead distinction.

5. **Checkpoint granularity is the axis on which Tier C is furthest behind Tier A/B.** LangGraph and
   DBOS both resume *mid-unit* (pending writes `[CE-2]`; memoised steps `[CE-10]`). Every Tier C
   system surveyed treats the task as the atom and re-runs it whole. For long agent tasks this is the
   most expensive gap, and Temporal's `continue-as-new` `[CE-9]` is the closest published analogue to
   the context-exhaustion case.

6. **Runner and store are separable, and beads is already treated as one backend among several.**
   yolo-runner: "The runner owns task selection, status updates, and logging; agents execute tasks
   they're given" and "Loads tasks from tracker/storage backends such as GitHub, Linear, TK, or
   beads/br" `[CE-15]`. Since `plan.yaml` does not hold `bd` fixed, the relevant question may be
   scheduler-vs-store rather than which store.

## Absence findings

Stated per the epistemic rules — these are gaps in what was retrieved, not asserted gaps in the
systems.

- **No evidence found** of conditional-branch or loop primitives in any Tier C tracker-as-store
  system. Searched: the tracker-orchestration query that surfaced `[CE-12]`–`[CE-15]`, plus the
  READMEs themselves. clu explicitly places conditionals *outside* the graph `[CE-13]`; the others are
  silent. This looks like a real tier-wide boundary but is not proven.
- **No evidence gathered** on Temporal's fan-out/join or HITL surfaces. Temporal signals/updates
  (`[CE-8]`'s sibling page `handling-messages`) were surfaced in search but not crawled; those cells
  are marked `?` / `[uncertain]` rather than filled from background knowledge.
- **No evidence gathered** on AutoGen GraphFlow HITL. GraphFlow is documented as "experimental"
  `[CE-5]`; whether it exposes an approval gate was not established.
- **No evidence gathered** on LangGraph per-node retry policies. The primitive is believed to exist
  but no retrieved source states it, so the matrix cell carries `[uncertain]`.
- **Deliberately not searched** (plan exclusion): Airflow / Dagster / Pegasus and the scientific
  workflow-DAG lineage. Prefect and Inngest were also not pursued — Inngest appears only incidentally
  as a Mastra execution-engine backend `[CE-7]`.
- **Not searched:** CrewAI Flows and the OpenAI Agents SDK. Both are plausible Tier A comparables; the
  ~6-artifact budget was spent on systems with deeper published execution semantics.

## Provider and method notes

All searches used exa MCP (`get_code_context_exa` for the framework-semantics queries,
`web_search_exa` for the tracker-as-store query, `crawling_exa` for full-text extraction). No provider
fell back to tavily/perplexity/WebFetch; no rate limiting was encountered. Ten crawl targets were
batched across five calls, respecting the per-domain courtesy limit.

Credibility skew to note for the synthesis phase: Tier A/B evidence is predominantly **first-party
vendor documentation** — authoritative for a system's own semantics, unreliable for comparison. Tier C
evidence is predominantly **project READMEs and one marketing landing page** (`[CE-12]`), which are
self-descriptions of small, unproven projects. The two genuinely independent artifacts in this cluster
are the AutoGen tracker issue `[CE-6]` and the DeepWiki source-cited Mastra documentation `[CE-7]`;
the negative findings resting on `[CE-6]` are therefore the best-supported claims here.

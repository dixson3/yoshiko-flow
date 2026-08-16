---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: framework-evidence

Retriever output for bead `yf-mol-62k.2`, research project `003-graph-engineering-hypothesis`.

**Task.** Gather shipped specs and source for agent-graph runtimes — LangGraph (nodes / edges /
conditional edges / checkpointers), DSPy, and comparable graph-native agent frameworks — preferring
docs and source over blog posts, and excluding the academic / scientific workflow-DAG lineage
(Airflow, Dagster, Pegasus). Goal: extract the concrete primitive vocabulary these systems actually
implement, as the yardstick for the "is graph engineering real" question.

**Result.** 17 sources across 7 systems, all first-party documentation or generated API reference
(several linked to a specific source commit). Zero blog posts and zero workflow-DAG-lineage sources
were admitted. Exclusion held: Airflow / Dagster / Pegasus appear nowhere below except as a
*framework's own* retrospective reference (FW-12), which is quoted as a design position, not
imported as evidence.

**Provider.** All retrievals via exa MCP (`get_code_context_exa`, `crawling_exa`). No fallback
provider was needed; no rate limiting was encountered.

---

## Systems surveyed

| System | Graph-native? | Evidence ids |
|:-------|:--------------|:-------------|
| LangGraph (LangChain) | Yes — explicit `StateGraph` of nodes + edges | FW-1 … FW-7 |
| pydantic-graph (Pydantic AI) | Yes — edges derived from `run()` return type hints | FW-8 |
| AutoGen `GraphFlow` (Microsoft) | Yes — `DiGraphBuilder` + `DiGraph`; self-declared experimental | FW-9 |
| Apache Burr (ex-DAGWorks) | Yes — actions + `(from, to, condition)` transitions | FW-10, FW-11 |
| Google ADK v2.0 | Yes — `Workflow(edges=[...])`; supersedes template workflow agents | FW-14, FW-15 |
| CrewAI Flows | Partially — event-driven decorators, edges implied not declared | FW-13 |
| LlamaIndex Workflows | **No, deliberately** — event-typed steps, explicit anti-DAG position | FW-12 |
| DSPy | **No** — module tree + plain Python control flow, no edge API | FW-16, FW-17 |

---

## The primitive vocabulary

Each row is a primitive that at least two independent systems implement under their own names.
"Implemented" means the primitive has a named API surface in shipped code or first-party reference
docs, not merely that the behavior is achievable.

| Primitive | LangGraph | pydantic-graph | AutoGen GraphFlow | Burr | ADK v2.0 | CrewAI Flows | LlamaIndex Workflows | DSPy |
|:----------|:----------|:---------------|:------------------|:-----|:---------|:-------------|:---------------------|:-----|
| Typed node / step unit | `add_node` | `BaseNode` subclass | agent as node | `@action` | `FunctionNode` / `AgentNode` | `@start` / `@listen` method | `@step` method | `dspy.Module` |
| Static edge (declared successor) | `add_edge` | `run()` return annotation | `builder.add_edge` | `with_transitions` 2-tuple | `edges=[("START", a, b)]` | `@listen(other)` | inferred from event types | none |
| Conditional edge / router | `add_conditional_edges` | union return type | edge condition (callable) | `when` / `expr` / `default` | route dict on `Event(route=...)` | `@router` [uncertain] | `if` returning distinct event type | plain Python `if` |
| Static parallel fan-out | multiple edges, same super-step | — | "Parallel fan-outs" | — | `AddFanOut` | multiple `@start()` | step returns `list[Event]` | none |
| Dynamic fan-out (runtime cardinality) | `Send` | — | — | — | `ctx.run_node()` [uncertain] | — | `ctx.send_event(...)` | none |
| Join / fan-in / barrier | reducer on a state channel | — | "join" node | — | `AddFanIn` | `and_` / `or_` [uncertain] | accept `list[A]` / `ctx.collect_events` | none |
| Shared state with merge rule | `State` + reducers + channels | `GraphRunContext[StateT]` | — | `State` (reads/writes) | `Event` output passing / session state | `self.state` (UUID-keyed) | `ctx.store` | instance attrs |
| Durable checkpoint | checkpointer at each super-step | `persistence` module | — | `StatePersister` after each action | — | `@persist` [uncertain] | — | none |
| Resume from checkpoint | `thread_id` cursor | — | — | `resume_at_next_action` | — | "begins or resumes" | — | none |
| Fork / time travel | fork state at arbitrary checkpoint | — | — | `fork_from_sequence_id` | — | — | — | none |
| Human-in-the-loop gate | `interrupt()` + `Command(resume=)` | — | — | (via persistence) [uncertain] | "human input tasks" as node type | — | "ask for human input" | none |
| Cycle / loop with exit condition | conditional edge back to a node | node returns an earlier node | "Loops with safe exit conditions" | transition back to prior action | — | — | step returns earlier-handled event | `max_iters` in `ReAct` |
| Per-node retry / timeout / error handler | `retry_policy`, timeout, error handler | — | — | — | — | — | workflow `timeout=` | none |
| Compile-time / pre-run validation | `.compile()` structural checks | type-hint checking | `builder.build()` validation | — | — | — | event-graph validation | none |
| Visualization | graph viz from `path_map` / type hints | "visualize complex workflows" | — | Burr UI [uncertain] | figures in docs | `flow.plot()` | "diagrams" | none |

Em-dash means **no evidence found** in the sources retrieved for this cluster — not a claim of
absence in the product. See "Gaps" below.

---

## Findings per source

### LangGraph — the reference vocabulary

LangGraph is the only system in the set that names all three of state, node, and edge as
co-equal first-class concepts and then builds every other primitive on a single execution model.

> "At its core, LangGraph models agent workflows as graphs. You define the behavior of your agents
> using three key components: 1. `State` ... 2. `Nodes` ... 3. `Edges` ... In short: *nodes do the
> work, edges tell what to do next*." [FW-1]

The execution model is explicitly Pregel/BSP, and this is what makes "parallel" a *structural*
property rather than a scheduling accident:

> "LangGraph's underlying graph algorithm uses message passing to define a general program. ...
> Inspired by Google's Pregel system, the program proceeds in discrete 'super-steps.' A super-step
> can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of
> the same super-step, while nodes that run sequentially belong to separate super-steps." [FW-1]

Termination is a graph property, not a driver-loop property:

> "At the end of each super-step, nodes with no incoming messages vote to `halt` by marking
> themselves as `inactive`. The graph execution terminates when all nodes are `inactive` and no
> messages are in transit." [FW-1]

There is a distinct **compile** phase between construction and execution, and it validates topology:

> "Compiling is a pretty simple step. It provides a few basic checks on the structure of your graph
> (no orphaned nodes, etc). It is also where you can specify runtime args like checkpointers and
> breakpoints. ... You **MUST** compile your graph before you can use it." [FW-1]

**Conditional edge** is a signature, not a metaphor:

> "Add a conditional edge from the starting node to any number of destination nodes. ... `path` ...
> The callable that determines the next node or nodes. If not specifying `path_map` it should return
> one or more nodes. If it returns `'END'`, the graph will stop execution." [FW-2]

Note the visualization consequence — a declared edge set is what makes the graph *renderable*:

> "Without type hints on the `path` function's return value (e.g., `-> Literal[\"foo\",
> \"__end__\"]:`) or a path_map, the graph visualization assumes the edge could transition to any
> node in the graph." [FW-2]

**Dynamic fan-out** is the sharpest primitive in the whole set, and the one with the fewest
analogues elsewhere. `Send` lets a conditional edge emit N invocations of a node with *N different
states* at runtime:

> "The `Send` class is used within a `StateGraph`'s conditional edges to dynamically invoke a node
> with a custom state at the next step. Importantly, the sent state can differ from the core graph's
> state, allowing for flexible and dynamic workflow management. One such example is a 'map-reduce'
> workflow where your graph invokes the same node multiple times in parallel with different states,
> before aggregating the results back into the main graph's state." [FW-3]

The aggregation half of map-reduce is *not* a separate join primitive — it is a reducer annotation
on a state channel (`jokes: Annotated[list[str], operator.add]` in the FW-3 example). This matters
for the yf comparison: LangGraph has no `join` node; fan-in is a data-merge rule.

**Checkpointing** is per-super-step and is the substrate for four higher-order capabilities:

> "A checkpointer saves a snapshot of graph state at each super-step, organized into **threads**.
> Compile a graph with a checkpointer to enable human-in-the-loop workflows, time travel debugging,
> fault-tolerant execution, and conversational memory." [FW-4]

Sub-super-step durability is also implemented, which is the difference between "resume the step" and
"resume the run":

> "In addition to super-step checkpoints, LangGraph also persists writes at the **node (task) level**.
> ... These per-task writes are what enable pending writes recovery: if another node in the same
> super-step fails, the successful nodes' writes are already durable and don't need to be re-run on
> resume." [FW-4]

And the resume cursor is an explicit, user-chosen identity:

> "The checkpointer uses `thread_id` as the primary key for storing and retrieving checkpoints.
> Without it, the checkpointer cannot save state or resume execution after an interrupt." [FW-4]

**Human-in-the-loop** is a runtime pause, not a pre-declared breakpoint:

> "Interrupts allow you to pause graph execution at specific points and wait for external input
> before continuing. ... When an interrupt is triggered, LangGraph saves the graph state using its
> persistence layer and waits indefinitely until you resume execution. ... Unlike static breakpoints
> (which pause before or after specific nodes), interrupts are **dynamic**: they can be placed
> anywhere in your code and can be conditional based on your application logic." [FW-5]

One consequence worth carrying into the yf comparison — resume is *node*-granular, not
statement-granular:

> "The node restarts from the beginning of the node where the `interrupt` was called when resumed, so
> any code before the `interrupt` runs again." [FW-5]

**Failure handling** is a per-node policy attached at graph-construction time:

> "When a node fails—from a slow external API, a transient network error, or an unhandled
> exception—LangGraph gives you three composable mechanisms to respond: **Retries** ... **Timeouts**
> ... **Error handling** ... These compose in a fixed order: when a node attempt raises any exception
> (including `NodeTimeoutError` from a timeout), the retry policy decides whether to retry. Only
> after retries are exhausted does the error handler run." [FW-6]

Retry is *declared*, with defaults, and inspectable from inside the node
(`runtime.execution_info.node_attempt`) — i.e. the runtime, not the author, owns the retry loop.
Defaults: `max_attempts=3`, `initial_interval=0.5`, `backoff_factor=2.0`, `jitter=True`. [FW-6]

Finally, LangGraph distinguishes two persistence tiers, which is a distinction most of the other
systems do not draw:

> "**Checkpointers** persist a thread's graph state as checkpoints. Use them for short-term,
> thread-scoped memory ... **Stores** persist application-defined data outside the graph state. Use
> them for long-term, cross-thread memory." [FW-7]

### pydantic-graph — edges as type signatures

The distinguishing move: there is no `add_edge` at all. The edge set is *derived from the type
system*.

> "Subclasses of `BaseNode` define nodes for execution in the graph. Nodes ... generally consist of:
> fields containing any parameters required/optional when calling the node; the business logic to
> execute the node, in the `run` method; return annotations of the `run` method, which are read by
> `pydantic-graph` to determine the outgoing edges of the node." [FW-8]

Termination is also a type: `End` is "return value to indicate the graph run should end" [FW-8].
The public surface confirms the primitive set — `from .nodes import BaseNode, Edge, End,
GraphRunContext` and `from .persistence import ...` [FW-8, package `__init__` observed via exa code
context].

This source is also the strongest available *counter*-hype datapoint from a graph-native vendor:

> "If Pydantic AI agents are a hammer, and multi-agent workflows are a sledgehammer, then graphs are
> a nail gun: sure, nail guns look cooler than hammers; but nail guns take a lot more setup than
> hammers ... In short, graphs are a powerful tool, but they're not the right tool for every job.
> Please consider other multi-agent approaches before proceeding. If you're not confident a
> graph-based approach is a good idea, it might be unnecessary." [FW-8]

That is a shipping graph library telling its users the graph is usually the wrong abstraction — a
material qualifier on any "graph engineering is converging" claim.

### AutoGen GraphFlow — the four-pattern taxonomy, stated outright

AutoGen names exactly the four topology patterns as a closed set, which is the single most useful
sentence in this cluster for a primitive inventory:

> "GraphFlow: A team that follows a DiGraph to control the execution flow between agents. Supports
> sequential, parallel, conditional, and looping behaviors." [FW-9]

> "DiGraphBuilder is a fluent utility that lets you easily construct execution graphs for workflows.
> It supports building: Sequential chains; Parallel fan-outs; Conditional branching; Loops with safe
> exit conditions. Each node in the graph represents an agent, and edges define the allowed execution
> paths. Edges can optionally have conditions based on agent messages." [FW-9]

Entry and exit are computed from topology rather than declared:

> "the flow automatically computes all the source and leaf nodes of the graph and the execution
> starts at all the source nodes in the graph and completes execution when no nodes are left to
> execute." [FW-9]

And the docs give a decision rule for *when* the graph is worth it, which is directly relevant to
the "is yf's graph real or decorative" question:

> "Use Graph when you need strict control over the order in which agents act, or when different
> outcomes must lead to different next steps. Start with a simple team such as RoundRobinGroupChat or
> SelectorGroupChat if ad-hoc conversation flow is sufficient. Transition to a structured workflow
> when your task requires deterministic control, conditional branching, or handling complex
> multi-step processes with cycles." [FW-9]

Maturity caveat, quoted verbatim so it is not lost:

> "GraphFlow is an experimental feature. Its API, behavior, and capabilities are subject to change in
> future releases." [FW-9]

Corroborating evidence that cycle-safety is genuinely enforced (not just documented) comes from the
issue tracker titles surfaced during retrieval — `Cycle detected without exit condition: generator ->
reviewer -> generator` (issue #6628) and `GraphFlow fails to find next speaker when conditional edge
is added (No available speakers found)` (issue #6551). These are titles only; I did not fetch issue
bodies, so treat as weak corroboration `[uncertain]`.

### Apache Burr — transitions are edges, said explicitly

> "Transitions define explicitly how actions are connected and which action is available next for any
> given state. You can think of them as edges in a graph. They have three main components: - The
> `from` state - The `to` state - The `condition` that must be met to move from the `from` state to
> the `to`" [FW-10]

Burr's conditional semantics are *ordered-first-match*, which differs from LangGraph's
router-returns-target model:

> "Conditions are evaluated in the order they are specified, and the first one that evaluates to True
> will be the transition that is selected when determining which action to run next. If no condition
> evaluates to `True`, the application execution will stop early." [FW-10]

It ships a small condition DSL (`when(age__gte=18)`, `expr('epochs>100')`, `default`, `~` for
negation) [FW-10] — evidence that "conditional edge" is developed enough in this ecosystem to have
grown its own predicate language.

Persistence converges on the same capabilities as LangGraph under different names:

> "Burr provides an API to save and load state from a database. This enables you to pause and restart
> applications where you left off. ... You can fork state from a previous run to enable
> debugging/loading." [FW-11]

> "`fork_from_sequence_id` is used to identify the sequence_id to use. This is useful if you want to
> fork from a specific point in the application, rather than the latest state. This is especially
> useful for debugging, or building an application that enables you to rewind state and make
> different choices." [FW-11]

That is LangGraph's "time travel" arrived at independently. Burr's keys are `app_id` +
`partition_key` + `sequence_id` [FW-11] versus LangGraph's `thread_id` + `checkpoint_id` [FW-4] — same
shape, different spelling. Resume is a flag: `resume_at_next_action` — "a boolean that says whether
to start where you left off, or go back to the `default_entrypoint`" [FW-11]. State is written
"after each action" [FW-11], i.e. per-node rather than per-super-step (Burr has no super-step
concept).

### Google ADK v2.0 — a framework migrating *toward* graphs mid-flight

This is the strongest single piece of convergence evidence in the cluster, because it is a
*direction of travel* recorded in first-party docs. ADK's original abstraction was a small set of
template agents (Sequential, Parallel, Loop). The v2.0 docs deprecate that in favour of a graph:

> "Starting in ADK 2.0 for Python and Go, template workflows have been superseded by more flexible
> workflow structures, including graph-based workflows and dynamic workflows. These workflow
> architectures provide more control, flexibility and capability to evolve your agent workflows over
> time." [FW-18]

> "Graph-based agent workflows in ADK let you build agents with more precise control, creating
> deterministic processes that combine code logic and AI reasoning capabilities. Graph-based
> workflows allow you to define your agent logic as a graph of execution nodes and edges, combining
> AI-powered agent reasoning with deterministic tools and code." [FW-14]

The stated rationale is *prompt-length failure* — the argument that structure must move out of the
prompt and into the topology:

> "You can use prompt-based agents to define multiple step processes with descriptions of tasks and
> procedures using the instructions field of an ADK agent. However, as your instructions and
> procedures become longer and more complicated, making sure that the agent is following each step
> and guideline becomes more complicated and less reliable." [FW-14]

> "**Enhance reliability:** Improve the predictability of your agents by relying on structured node
> definitions rather than prompts alone." [FW-14]

The node taxonomy is broader than LangGraph's (human input is a *node type*, not an interrupt):

> "A graph is composed of execution nodes. These *nodes* can be ***Agents***, ADK ***Tools***, human
> input tasks, or code functions you write. Nodes can take inputs from previously executed nodes, and
> emit data through ***Event*** objects." [FW-15]

Fan-out and fan-in are named methods on the edge builder — the only place in this cluster where both
appear as first-class *named* operations:

> "The builder's `Add`, `AddFanOut`, and `AddFanIn` methods express the same topology with less
> repetition." [FW-15]

ADK also documents a three-way taxonomy that maps almost exactly onto the question this research is
asking (declared graph vs. programmatic walk):

> "ADK offers three complementary ways to compose multi-step work: **Graph-based workflows** ... a
> declarative graph of nodes and edges with explicit routing — best for deterministic, structured
> processes. **Dynamic workflows:** programmatic orchestration in your own code (loops, conditionals,
> recursion) — best when the control flow is too complex or iterative for a static graph. **Prebuilt
> workflow agents** (sequential, parallel, loop): higher-level building blocks for common patterns
> without assembling a graph yourself." [FW-14]

Conditional routing is route-key dispatch — a node emits `Event(route=...)`, and the edge table maps
route values to successors [FW-15]. The Go API additionally types the matcher: `StringRoute`,
`IntRoute`, `MultiRoute[int]`, `BoolRoute`, `Default` [FW-15].

### CrewAI Flows — edges by decorator, graph by implication

> "Flows allow you to create structured, event-driven workflows. They provide a seamless way to
> connect multiple tasks, manage state, and control the flow of execution in your AI applications."
> [FW-13]

> "The `@start()` decorator marks entry points for a Flow. ... All satisfied `@start()` methods will
> execute (often in parallel) when the Flow begins or resumes." [FW-13]

> "The `@listen()` decorator is used to mark a method as a listener for the output of another task in
> the Flow. The method decorated with `@listen()` will be executed when the specified task emits an
> output." [FW-13]

State is per-run and identity-bearing:

> "Each Flow instance automatically receives a unique identifier (UUID) in its state, which helps
> track and manage flow executions." [FW-13]

Visualization exists (`flow.plot()` producing an HTML file) [FW-13], which implies a materialized
edge set even though the author never writes one.

`[uncertain]` — `@router`, `and_`, `or_`, and the `@persist` decorator did not appear in the crawled
window of the official docs page. They are attested by the module docstring surfaced during
retrieval (`"This module provides the Flow class and decorators (@start, @listen, @router) for
building event-driven workflows with conditional exe[cution]"`, from `lib/crewai/src/crewai/flow/flow.py`)
and by the merged PR title `Add @persist decorator with FlowPersistence interface`
(crewAIInc/crewAI#1892). I did not fetch the source file or PR body, so join (`and_`/`or_`) and
persistence in CrewAI are recorded as probable-but-not-directly-quoted.

### LlamaIndex Workflows — the reasoned dissent

The single most important source for testing the hypothesis, because it is a major framework that
built a DAG system, shipped it, and then *removed* it on stated grounds.

> "A workflow is an event-driven, step-based way to control the execution flow of an application.
> Your application is divided into sections called steps. A step receives an event, does some work,
> and returns another event. That returned event triggers the next step whose type annotation accepts
> it. That is the whole model." [FW-12]

> "Other frameworks and LlamaIndex itself have attempted to solve this problem previously with
> directed acyclic graphs (DAGs) but these have a number of limitations that workflows do not: Logic
> like loops and branches needed to be encoded into the edges of graphs, which made them hard to read
> and understand. Passing data between nodes in a DAG created complexity around optional and default
> values and which parameters should be passed. DAGs did not feel natural to developers trying to
> develop complex, looping, branching AI applications." [FW-12]

Critically, this is not a rejection of the *primitives* — it is a rejection of *declaring them as
edges*. Every primitive still exists, relocated into the type system and plain Python:

> "Branches are ordinary `if` statements that return different event types. Loops are steps that
> return an event handled by an earlier step. Concurrent work is a step that returns `list[Event]`,
> paired with another step that accepts `list[Event]`. When the flow needs to become dynamic, you can
> send events directly from the `Context`." [FW-12]

And the graph reappears anyway, as a derived artifact used for validation:

> "The event types describe the edges of the workflow, and regular Python describes the logic inside
> each edge." [FW-12]

> "Before a workflow runs, Workflows validates the event graph described by your step signatures. It
> checks that start and stop events are present, produced events have consumers, consumed events have
> producers, and the graph does [...]" [FW-12]

The documented API table maps one-to-one onto the fan-out / join / dynamic-send / shared-state rows
of the primitive table: `list[A]` return for finite batch fan-out, `list[A]` accept for barrier join,
`ctx.send_event(...)` for "emit an unknown number of events", `ctx.collect_events(...)` for manual
join, `ctx.store` for "shared per-run state" [FW-12].

Their own summary of the tradeoff:

> "The type-first APIs are easier to validate and visualize. The context APIs are more flexible, but
> they make you own more of the bookkeeping." [FW-12]

### DSPy — not a graph runtime at all (correcting the cluster premise)

The cluster brief grouped DSPy with LangGraph as an agent-graph runtime. **The evidence does not
support that.** DSPy has no edge concept, no conditional-edge concept, no checkpoint/resume, and no
fan-out primitive. Its composition unit is a Python object tree, and its control flow is Python.

> "There's no esoteric chaining API; modules are just Python and the DSPy primitives `Signature`,
> `Module`, and `LM`." [FW-16]

> "When constructing a module, we need to write two functions: 1. `__init__` sets up our initial
> state and defines our submodules. 2. `forward` handles what happens when we call our program,
> accepting inputs and shepherding through our submodules before returning an assembled output."
> [FW-16]

> "Base class for all DSPy modules (programs). ... A Module is a building block for DSPy programs
> that can contain predictors, sub-modules, and custom logic. Modules can be composed together to
> create com[plex programs]" [FW-17] — *final word truncated in the retrieved highlight.*

Where LangGraph would use a conditional edge and a super-step, DSPy uses a loop in `forward`:

> "Inside dspy.ReAct, other DSPy modules are composed together. Each step where the model considers
> its inputs and picks the next tool is a `dspy.Predict` module. A bit of code manages the control
> flow, looping through `Predict` calls until the model calls `finish` or hits `max_iters`." [FW-16]

DSPy's axis is *optimization*, not topology:

> "A **DSPy optimizer** is an algorithm that can tune the parameters of a DSPy program (i.e., the
> prompts and/or the LM weights) to [maximize a metric]" [from `docs/docs/learn/optimization/optimizers.md`
> in stanfordnlp/dspy, surfaced via exa code context; final clause truncated — `[uncertain]`]

This matters for the research question: DSPy is a frequently-cited exhibit in "graph engineering"
arguments, and on the primitive yardstick it belongs on the *other* side of the line, with LlamaIndex
and plain Python.

---

## Cross-cutting observations

**1. There is a real, converged core — but it is small.** Four primitives appear, independently
named, in every graph-native system surveyed: **typed node**, **declared edge**, **conditional
edge/router**, and **run-scoped state**. A fifth, **cycle with an explicit exit condition**, appears
in every system *including* the two that reject graphs (LlamaIndex, DSPy `max_iters`). This is
strong evidence that at least the topology vocabulary is not post-hoc labeling.

**2. The convergence is strongest where it is cheapest, and weakest where it is expensive.** Nodes
and conditional edges are near-universal. Durable checkpointing with fork/resume appears in only two
systems (LangGraph FW-4/FW-7, Burr FW-11) plus a probable third (CrewAI `@persist` `[uncertain]`).
Dynamic runtime-cardinality fan-out appears in essentially one-and-a-half (LangGraph `Send` FW-3;
LlamaIndex `ctx.send_event` FW-12 achieves the same effect *without* a graph). Per-node
retry/timeout/error-handler policy appears in exactly one (LangGraph FW-6) — and even there it is
gated at `langgraph>=1.2`, i.e. it arrived late.

**3. The direction of travel is genuinely toward explicit graphs — with one significant
counter-current.** ADK moved *to* graphs in v2.0 and said why (FW-14). AutoGen added GraphFlow on top
of unstructured group chat (FW-9). LlamaIndex moved *away* from DAGs (FW-12), and pydantic-graph, a
graph library, opens its own documentation by advising you not to use it (FW-8). The honest reading
is convergence on the *vocabulary* with active disagreement on whether the edges should be
**declared** (LangGraph, ADK, AutoGen, Burr) or **derived** (pydantic-graph from type hints,
LlamaIndex from event signatures).

**4. "Fan-in" is under-specified across the whole field.** LangGraph has no join node — fan-in is a
reducer on a state channel (FW-3). Burr has none in the retrieved material. Only ADK names
`AddFanIn` (FW-15) and LlamaIndex names `ctx.collect_events` (FW-12). If yf needs a real barrier /
join, there is no dominant industry spelling to copy.

**5. Two independent systems arrived at fork-from-a-past-step.** LangGraph "time travel" /
"fork the graph state at arbitrary checkpoints to explore alternative trajectories" (FW-4) and Burr
`fork_from_app_id` + `fork_from_sequence_id` (FW-11). Independent convergence on a non-obvious
capability is the best kind of evidence that the primitive is load-bearing rather than fashionable.

**6. Resume granularity is a design decision every persistent system had to make, and they answered
differently.** LangGraph checkpoints at super-step boundaries, with sub-step task-level pending
writes for partial recovery (FW-4), and node restarts are whole-node ("any code before the
`interrupt` runs again", FW-5). Burr persists after each action (FW-11). Neither offers
statement-level resume. Any yf design that assumes finer-grained resume would be off the map of
shipped practice.

---

## Gaps and absences

Stated explicitly per the epistemic rules. Each of these is "not found in this cluster's retrievals,"
not "does not exist."

- **LangGraph recursion/step budget.** `recursion_limit` and `GraphRecursionError` were queried
  directly and did not surface a first-party page in the results. **No evidence found** — do not
  assert LangGraph's loop-budget semantics from this cluster.
- **LangGraph subgraphs.** Confirmed to exist indirectly via checkpoint namespaces — "`node_name:uuid`:
  The checkpoint belongs to a subgraph invoked as the given node. For nested subgraphs, namespaces
  are joined with `|` separators" [FW-4] — but the subgraph API surface itself was not retrieved.
- **LangGraph node caching / `defer`.** Queried, not surfaced. **No evidence found.**
- **CrewAI `@router`, `and_`, `or_`, `@persist`.** Attested only by a source-file docstring and a PR
  title surfaced in search results; bodies not fetched. Marked `[uncertain]` throughout.
- **AutoGen GraphFlow persistence / resume.** Not addressed in the retrieved page. **No evidence
  found** on whether GraphFlow can checkpoint or resume.
- **Burr human-in-the-loop.** The docs example names a `human_converse` action, implying HITL, but no
  interrupt/gate primitive was quoted. Marked `[uncertain]`.
- **pydantic-graph fan-out / parallelism.** The persistence module exists (`from .persistence import
  ...`), but no parallel-execution or fan-out primitive appeared. Given the FSM framing, it may be
  strictly single-active-node. **Not verified.**
- **ADK checkpoint/resume.** Not addressed in the two graph pages retrieved. **No evidence found.**
- **Version/date stamping.** Except where docs stated a version gate explicitly (ADK v2.0.0,
  `langgraph>=1.2`, AutoGen "experimental"), these are living docs pages with no publication date.
  Treat the whole cluster as "as of 2026-08-16."
- **Deliberately excluded per plan.yaml:** Airflow, Dagster, Pegasus and the scientific
  workflow-DAG literature. Also excluded: all blog posts and forum threads surfaced during retrieval
  (machinelearningplus, pratikdhanave.com, matt-harrison.com, forum.langchain.com, dreaming.press,
  deepwiki.com), on the "docs + source over blog posts" instruction.

---

## Source index

| id | System | Title | URL |
|:---|:-------|:------|:----|
| FW-1 | LangGraph | Graph API overview | https://docs.langchain.com/oss/python/langgraph/graph-api |
| FW-2 | LangGraph | StateGraph.add_conditional_edges | https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges |
| FW-3 | LangGraph | Send | https://reference.langchain.com/python/langgraph/types/Send |
| FW-4 | LangGraph | Checkpointers | https://docs.langchain.com/oss/python/langgraph/checkpointers |
| FW-5 | LangGraph | Interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts |
| FW-6 | LangGraph | Fault tolerance | https://docs.langchain.com/oss/python/langgraph/fault-tolerance |
| FW-7 | LangGraph | Persistence | https://docs.langchain.com/oss/python/langgraph/durable-execution |
| FW-8 | pydantic-graph | Graphs overview | https://ai.pydantic.dev/graph/ |
| FW-9 | AutoGen | GraphFlow (Workflows) | https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html |
| FW-10 | Apache Burr | Transitions | https://burr.apache.org/docs/concepts/transitions/ |
| FW-11 | Apache Burr | State Persistence | https://burr.apache.org/docs/concepts/state-persistence/ |
| FW-12 | LlamaIndex | Workflows: Introduction | https://developers.llamaindex.ai/python/framework/understanding/workflows/ |
| FW-13 | CrewAI | Flows | https://docs.crewai.com/en/concepts/flows |
| FW-14 | Google ADK | Graph-based agent workflows | https://raw.githubusercontent.com/google/adk-docs/main/docs/graphs/index.md |
| FW-15 | Google ADK | Build graph routes for agent workflows | https://raw.githubusercontent.com/google/adk-docs/main/docs/graphs/routes.md |
| FW-16 | DSPy | Composing your own module | https://dspy.ai/getting-started/composing-modules/ |
| FW-17 | DSPy | Module (API reference) | https://dspy.ai/api/modules/Module/ |
| FW-18 | Google ADK | Template agent workflows (deprecation notice) | https://google.github.io/adk-docs/agents/workflow-agents/ |

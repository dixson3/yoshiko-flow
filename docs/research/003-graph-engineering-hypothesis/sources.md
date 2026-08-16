---
type: Reference
okf_spec: OKF-RESEARCH
okf_version: '0.1'
title: Sources — 003-graph-engineering-hypothesis
created: 2026-04-23
tags:
- research
- 003-graph-engineering-hypothesis
- sources
---

# Sources — 003-graph-engineering-hypothesis

Citation format: `[ID](sources.md#id)` from Summary.md and artifacts.

## comparative-execution

### CE-1
- **Title:** Graph API overview — LangGraph docs
- **URL:** https://docs.langchain.com/oss/python/langgraph/graph-api
- **Snippet:** Canonical description of LangGraph's execution model: State/Nodes/Edges, message passing, Pregel-inspired super-steps, conditional vs fixed edges.
- **Quote:** > LangGraph's underlying graph algorithm uses message passing to define a general program. When a Node completes its operation, it sends messages along one or more edges to other node(s). ... Inspired by Google's Pregel system, the program proceeds in discrete "super-steps." A super-step can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of the same super-step, while nodes that run sequentially belong to separate super-steps. ... The graph execution terminates when all nodes are inactive and no messages are in transit.

### CE-2
- **Title:** Checkpointers — LangGraph docs
- **URL:** https://docs.langchain.com/oss/python/langgraph/checkpointers
- **Snippet:** Checkpoint/resume model: snapshot per super-step, threads as resume cursor, pending writes for partial-failure recovery, time travel and forking.
- **Quote:** > LangGraph creates a checkpoint at each super-step boundary. A super-step is a single "tick" of the graph where all nodes scheduled for that step execute (potentially in parallel). ... In addition to super-step checkpoints, LangGraph also persists writes at the node (task) level. As each node within a super-step finishes, its outputs are written to the checkpointer's checkpoint_writes table as task entries linked to the in-progress checkpoint. These per-task writes are what enable pending writes recovery: if another node in the same super-step fails, the successful nodes' writes are already durable and don't need to be re-run on resume.

### CE-3
- **Title:** Interrupts — LangGraph docs
- **URL:** https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/
- **Snippet:** Dynamic HITL gate: interrupt() suspends anywhere in node code, state persists indefinitely, Command(resume=...) rehydrates; parallel interrupts resolved by interrupt ID.
- **Quote:** > Interrupts allow you to pause graph execution at specific points and wait for external input before continuing. ... When an interrupt is triggered, LangGraph saves the graph state using its persistence layer and waits indefinitely until you resume execution. ... Unlike static breakpoints (which pause before or after specific nodes), interrupts are dynamic: they can be placed anywhere in your code and can be conditional based on your application logic.

### CE-4
- **Title:** LangGraph Deferred Nodes: Getting Map-Reduce Fan-In Right
- **URL:** https://dreaming.press/posts/langgraph-deferred-nodes-map-reduce-fan-in.html
- **Snippet:** Practitioner analysis separating fan-out (Send API) from join (defer=True), arguing defer is a queue-drain barrier rather than a dependency resolver.
- **Quote:** > A normal edge marks its target eligible the moment any single upstream task reaches it. With parallel branches — or worse, branches of unequal length ... the aggregator fires early, on whichever branch arrives first, and reduces over partial data. ... defer=True is not a dependency resolver. It does not build a graph of which nodes feed which and schedule accordingly. It is a scheduling barrier on the super-step queue — its entire semantics are "run me when nothing else is left to run."

### CE-5
- **Title:** GraphFlow (Workflows) — AutoGen
- **URL:** https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html
- **Snippet:** AutoGen's DiGraph-based team: sequential, parallel fan-out with join, conditional branching, loops with exit conditions; source/leaf nodes auto-computed.
- **Quote:** > GraphFlow: A team that follows a DiGraph to control the execution flow between agents. Supports sequential, parallel, conditional, and looping behaviors. ... DiGraphBuilder is a fluent utility that lets you easily construct execution graphs for workflows. It supports building: Sequential chains, Parallel fan-outs, Conditional branching, Loops with safe exit conditions. ... the flow automatically computes all the source and leaf nodes of the graph and the execution starts at all the source nodes in the graph and completes execution when no nodes are left to execute. ... Warning: GraphFlow is an experimental feature.

### CE-6
- **Title:** GraphFlow State Persistence Bug: Workflow Gets Stuck After Interruption During Agent Transitions (#7043)
- **URL:** https://github.com/microsoft/autogen/issues/7043
- **Snippet:** Open bug: interrupting GraphFlow mid-transition corrupts saved state; on load_state the ready queue is empty and the flow reports completion despite remaining work.
- **Quote:** > When a GraphFlow workflow is interrupted (e.g., via KeyboardInterrupt) during the transition between agents, the saved state becomes corrupted. On resume, the workflow terminates immediately with: `Digraph execution is complete` —even though agents still have remaining work. ... The GraphFlow coordination mechanism is interrupted before it can enqueue the next agent, leaving the system in an inconsistent state: Remaining work exists, No agents are enqueued, The workflow appears "complete" but is actually stuck.

### CE-7
- **Title:** Control Flow Patterns | mastra-ai/mastra | DeepWiki
- **URL:** https://deepwiki.com/mastra-ai/mastra/4.5-control-flow-patterns
- **Snippet:** Mastra's chainable control-flow surface: .then/.parallel/.branch/.dowhile/.dountil/.forEach/.map/.sleep, each compiled to a StepFlowEntry in an execution graph.
- **Quote:** > | Sequential | `.then(step)` | Execute step after previous completes | ... | Parallel | `.parallel([steps])` | Execute multiple steps concurrently | ... | Conditional | `.branch([[cond, step]])` | Execute first step whose condition is true | ... | Do-While Loop | `.dowhile(step, cond)` | Execute step, repeat while condition is true | ... | ForEach | `.forEach(step, opts?)` | Execute step for each array element | ... Each pattern is internally represented as a StepFlowEntry variant stored in the workflow's execution graph, which the execution engine traverses at runtime.

### CE-8
- **Title:** What is a Temporal Retry Policy? — Temporal docs
- **URL:** https://docs.temporal.io/encyclopedia/retry-policies
- **Snippet:** Declarative retry as a first-class execution-layer setting; retry is default-on at the activity (leaf) level and default-off at the workflow (orchestration) level, by design.
- **Quote:** > A Retry Policy is declarative. You do not need to implement your own logic for handling the retries; you only need to specify the desired behavior and Temporal will provide it. ... Retrying an entire Workflow Execution is not recommended due to the deterministic nature of Workflow replay. Since Workflows replay the same sequence of events to reach the same state, retrying the whole Workflow would repeat the same logic without resolving the underlying issue that caused the failure. ... Instead, retry failed Activities within the Workflow, which is Temporal's default behavior.

### CE-9
- **Title:** Continue-As-New Pattern — Temporal docs
- **URL:** https://docs.temporal.io/design-patterns/continue-as-new
- **Snippet:** Named pattern for bounding replay-history growth in long-running graphs: complete the current execution and atomically restart with the same ID and fresh history, carrying explicit state forward.
- **Quote:** > Continue-As-New completes the current Workflow execution and atomically starts a new one with the same Workflow ID. The new execution begins with a fresh event history while preserving logical continuity. You pass state as arguments to the new execution. ... Without Continue-As-New, you must manually stop and restart Workflows (losing continuity), risk hitting history limits and Workflow failures, implement external orchestration to manage Workflow lifecycle, and accept degraded performance as history grows large.

### CE-10
- **Title:** DBOS Architecture — DBOS Docs
- **URL:** https://docs.dbos.dev/architecture
- **Snippet:** Library-not-server durable execution: workflow inputs and step outputs checkpointed to Postgres; recovery replays and short-circuits any step with an existing checkpoint.
- **Quote:** > While your application runs, DBOS checkpoints those workflows and steps to a Postgres database. When failures occur, whether from crashes, interruptions, or restarts, DBOS uses those checkpoints to recover each of your workflows from the last completed step. ... As the workflow re-executes, it checks before each step if that step's output is checkpointed in Postgres. If there is a checkpoint, the step returns the checkpointed output instead of executing. ... The only overhead DBOS adds is database writes: one database write per step ... plus two additional database writes per workflow.

### CE-11
- **Title:** Building a modern Durable Execution Engine from First Principles — Restate
- **URL:** https://www.restate.dev/blog/building-a-modern-durable-execution-engine-from-first-principles
- **Snippet:** Counterpoint architecture: a purpose-built command-log runtime rather than a general database, with the server's journal as ground truth and stateless retryable services.
- **Quote:** > The server handles all coordination and durability for the invocation life cycle, journals, embedded K/V state, and manages failover, leader-election, and fencing. The server's view on an invocation and its journal is the ground truth; the services follow the server's view and function executions may be cancelled/reset/retried as needed. ... This stands somewhat in contrast to the common wisdom "don't build a new stateful system, just use Postgres".

### CE-12
- **Title:** ticks — The issue tracker your AI agents run on
- **URL:** https://ticks.sh/
- **Snippet:** Tracker-as-execution-graph: tk graph decomposes hard/soft dependency edges into parallel waves and runs one agent per ready tick in an isolated git worktree, merging wave by wave.
- **Quote:** > ticks reads the dependency graph, decomposes it into waves, and runs each ready tick as its own agent in an isolated git worktree. Waves merge back wave by wave, unblocking the next. ... You can't compute parallel waves, a dependency graph, a critical path, or "what's ready and unblocked for me right now" from prose in a TODO.md or an agent's throwaway todo list — and two agents editing one markdown file collide. ... Chain epics with hard (blocked_by) and soft (after) edges ... with branches/worktrees/notes as the durable handoff format so any runner can resume any epic. Humans stay in the loop via approval/review/checkpoint gates.

### CE-13
- **Title:** arjia-labs/clu — Local-first SQLite issue tracker for coordinating AI coding agents
- **URL:** https://github.com/arjia-labs/clu
- **Snippet:** SQLite tracker whose issue TYPES encode execution semantics: checkpoint issues are manual approval gates, milestone issues auto-close when dependencies close; batch instantiates a whole validated graph in one transaction.
- **Quote:** > a `checkpoint` issue is a manual gate (stays `checkpoint:pending` until `clu approve`), and a `milestone` issue auto-closes when all its dependencies close — the self-completing umbrella behind `clu batch --group` and phase boundaries. ... This is the generation / instantiation split: any language emits the graph (loops, conditionals, computed fan-out — things a static template can't do); clu owns validation and atomic instantiation. ... clu validates the whole graph (acyclic, every reference resolves, fields valid) and writes it in one transaction: a single bad entry aborts everything, so you never get a half-built graph. ... Cascading cancel: `clu cancel` walks the dep graph forward and cancels the whole tail.

### CE-14
- **Title:** jpicklyk/task-orchestrator — Server-enforced workflow discipline for AI agents
- **URL:** https://github.com/jpicklyk/task-orchestrator/
- **Snippet:** MCP server that moves gate enforcement out of prompts into the store: advance_item errors if a required note is missing or a dependency is unsatisfied; typed edges with linear/fan-out/fan-in shortcuts.
- **Quote:** > The enforcement happens at the tool level: if a required design note isn't filled, `advance_item` returns an error. If a dependency isn't satisfied, the transition is blocked. ... | Enforcement | Instructions that agents should follow | Server blocks the call if rules aren't met | ... When `schema` reaches terminal, `api` is automatically unblocked. When all children complete, the parent cascades to terminal. Dependency ordering is enforced by the server — structurally, not by convention. ... | Dependencies | `manage_dependencies`, `query_dependencies` | Typed edges with pattern shortcuts (linear, fan-out, fan-in) |

### CE-15
- **Title:** egv/yolo-runner — AI task execution with pluggable storage backends and dependency-aware scheduling
- **URL:** https://github.com/egv/yolo-runner
- **Snippet:** Explicit separation of runner from store: the scheduler computes runnable concurrency from the dependency graph while the tracker (GitHub, Linear, TK, beads) is a swappable backend.
- **Quote:** > The runner owns task selection, status updates, and logging; agents execute tasks they're given. ... Task Engine: Graph-based scheduler with dependency resolution and parent-child hierarchies ... Smart Concurrency: Automatically calculates optimal parallel execution from dependency graphs ... Loads tasks from tracker/storage backends such as GitHub, Linear, TK, or beads/br. Builds a dependency graph and calculates runnable concurrency.

## framework-evidence

### FW-1
- **Title:** Graph API overview — LangGraph (LangChain OSS docs)
- **URL:** https://docs.langchain.com/oss/python/langgraph/graph-api
- **Snippet:** Canonical statement of LangGraph's three primitives (State, Nodes, Edges), the Pregel-inspired super-step execution model, and the compile step.
- **Quote:** > At its core, LangGraph models agent workflows as graphs. You define the behavior of your agents using three key components: 1. `State` ... 2. `Nodes` ... 3. `Edges` ... In short: *nodes do the work, edges tell what to do next*.

### FW-2
- **Title:** StateGraph.add_conditional_edges — LangGraph API reference
- **URL:** https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges
- **Snippet:** Signature and semantics of the conditional-edge primitive, including path_map and END.
- **Quote:** > Add a conditional edge from the starting node to any number of destination nodes. ... `path` ... The callable that determines the next node or nodes. If not specifying `path_map` it should return one or more nodes. If it returns `'END'`, the graph will stop execution.

### FW-3
- **Title:** Send — LangGraph API reference
- **URL:** https://reference.langchain.com/python/langgraph/types/Send
- **Snippet:** The dynamic fan-out primitive: emit N copies of a node with per-copy state from inside a conditional edge.
- **Quote:** > The `Send` class is used within a `StateGraph`'s conditional edges to dynamically invoke a node with a custom state at the next step. Importantly, the sent state can differ from the core graph's state ... One such example is a "map-reduce" workflow where your graph invokes the same node multiple times in parallel with different states, before aggregating the results back into the main graph's state.

### FW-4
- **Title:** Checkpointers — LangGraph
- **URL:** https://docs.langchain.com/oss/python/langgraph/checkpointers
- **Snippet:** Checkpoint = state snapshot at each super-step boundary, keyed by thread_id; enables HITL, time travel, fault tolerance, pending writes.
- **Quote:** > A checkpointer saves a snapshot of graph state at each super-step, organized into **threads**. Compile a graph with a checkpointer to enable human-in-the-loop workflows, time travel debugging, fault-tolerant execution, and conversational memory.

### FW-5
- **Title:** Interrupts — LangGraph
- **URL:** https://docs.langchain.com/oss/python/langgraph/interrupts
- **Snippet:** Dynamic pause/resume primitive for human-in-the-loop; interrupt() + Command(resume=...) against a thread_id cursor.
- **Quote:** > Interrupts allow you to pause graph execution at specific points and wait for external input before continuing. ... When an interrupt is triggered, LangGraph saves the graph state using its persistence layer and waits indefinitely until you resume execution. ... Unlike static breakpoints (which pause before or after specific nodes), interrupts are **dynamic**.

### FW-6
- **Title:** Fault tolerance — LangGraph
- **URL:** https://docs.langchain.com/oss/python/langgraph/fault-tolerance
- **Snippet:** Per-node retry policy, timeout, and error handler as first-class graph-construction arguments with a defined composition order.
- **Quote:** > When a node fails—from a slow external API, a transient network error, or an unhandled exception—LangGraph gives you three composable mechanisms to respond: **Retries** ... **Timeouts** ... **Error handling** ... These compose in a fixed order: when a node attempt raises any exception (including `NodeTimeoutError` from a timeout), the retry policy decides whether to retry. Only after retries are exhausted does the error handler run.

### FW-7
- **Title:** Persistence — LangGraph
- **URL:** https://docs.langchain.com/oss/python/langgraph/durable-execution
- **Snippet:** Two-tier persistence: checkpointers (thread-scoped graph state) vs stores (cross-thread application data).
- **Quote:** > LangGraph provides two complementary persistence systems: **Checkpointers** persist a thread's graph state as checkpoints. Use them for short-term, thread-scoped memory, including conversation continuity, human-in-the-loop workflows, time travel, and fault tolerance. **Stores** persist application-defined data outside the graph state.

### FW-8
- **Title:** Graphs — pydantic-graph (Pydantic AI)
- **URL:** https://ai.pydantic.dev/graph/
- **Snippet:** Type-hint-derived edges: a node's run() return annotation IS its outgoing edge set. Also carries an explicit anti-hype caveat.
- **Quote:** > Subclasses of `BaseNode` define nodes for execution in the graph. Nodes ... generally consist of: fields containing any parameters required/optional when calling the node; the business logic to execute the node, in the `run` method; return annotations of the `run` method, which are read by `pydantic-graph` to determine the outgoing edges of the node.

### FW-9
- **Title:** GraphFlow (Workflows) — Microsoft AutoGen AgentChat
- **URL:** https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html
- **Snippet:** DiGraphBuilder + GraphFlow: sequential chains, parallel fan-out, conditional branching, loops with safe exit conditions; auto-computed source/leaf nodes.
- **Quote:** > GraphFlow: A team that follows a DiGraph to control the execution flow between agents. Supports sequential, parallel, conditional, and looping behaviors. ... DiGraphBuilder is a fluent utility that lets you easily construct execution graphs for workflows. It supports building: Sequential chains; Parallel fan-outs; Conditional branching; Loops with safe exit conditions.

### FW-10
- **Title:** Transitions — Apache Burr
- **URL:** https://burr.apache.org/docs/concepts/transitions/
- **Snippet:** Burr names transitions explicitly as graph edges: (from, to, condition) triples evaluated in declaration order.
- **Quote:** > Transitions define explicitly how actions are connected and which action is available next for any given state. You can think of them as edges in a graph. They have three main components: - The `from` state - The `to` state - The `condition` that must be met ... Conditions are evaluated in the order they are specified, and the first one that evaluates to True will be the transition that is selected.

### FW-11
- **Title:** State Persistence — Apache Burr
- **URL:** https://burr.apache.org/docs/concepts/state-persistence/
- **Snippet:** app_id/partition_key/sequence_id keying, resume_at_next_action, and fork-from-prior-run — an independently-arrived-at analogue of LangGraph threads + time travel.
- **Quote:** > Burr provides an API to save and load state from a database. This enables you to pause and restart applications where you left off. ... You can fork state from a previous run to enable debugging/loading. ... `fork_from_sequence_id` is used to identify the sequence_id to use. This is useful if you want to fork from a specific point in the application, rather than the latest state.

### FW-12
- **Title:** Workflows: Introduction — LlamaIndex
- **URL:** https://developers.llamaindex.ai/python/framework/understanding/workflows/
- **Snippet:** Deliberate REJECTION of the explicit-graph model in favour of event-typed steps; the key dissenting datapoint in this cluster.
- **Quote:** > Other frameworks and LlamaIndex itself have attempted to solve this problem previously with directed acyclic graphs (DAGs) but these have a number of limitations that workflows do not: Logic like loops and branches needed to be encoded into the edges of graphs, which made them hard to read and understand. ... DAGs did not feel natural to developers trying to develop complex, looping, branching AI applications.

### FW-13
- **Title:** Flows — CrewAI
- **URL:** https://docs.crewai.com/en/concepts/flows
- **Snippet:** Decorator-declared event-driven edges (@start, @listen, @router) with per-run state carrying an auto-generated UUID.
- **Quote:** > Flows allow you to create structured, event-driven workflows. ... The `@start()` decorator marks entry points for a Flow. ... All satisfied `@start()` methods will execute (often in parallel) when the Flow begins or resumes. ... The `@listen()` decorator is used to mark a method as a listener for the output of another task in the Flow.

### FW-14
- **Title:** Graph-based agent workflows — Google Agent Development Kit (ADK) v2.0
- **URL:** https://raw.githubusercontent.com/google/adk-docs/main/docs/graphs/index.md
- **Snippet:** ADK 2.0 supersedes its Sequential/Parallel/Loop template agents with an explicit Workflow(edges=[...]) graph engine.
- **Quote:** > Graph-based agent workflows in ADK let you build agents with more precise control, creating deterministic processes that combine code logic and AI reasoning capabilities. Graph-based workflows allow you to define your agent logic as a graph of execution nodes and edges, combining AI-powered agent reasoning with deterministic tools and code.

### FW-15
- **Title:** Build graph routes for agent workflows — Google ADK
- **URL:** https://raw.githubusercontent.com/google/adk-docs/main/docs/graphs/routes.md
- **Snippet:** Node taxonomy (Agent, Tool, human input, code function), sequential edges, route-keyed conditional dispatch, and explicit AddFanOut/AddFanIn builder methods.
- **Quote:** > A graph is composed of execution nodes. These *nodes* can be ***Agents***, ADK ***Tools***, human input tasks, or code functions you write. Nodes can take inputs from previously executed nodes, and emit data through ***Event*** objects. ... The builder's `Add`, `AddFanOut`, and `AddFanIn` methods express the same topology with less repetition.

### FW-16
- **Title:** Composing your own module — DSPy
- **URL:** https://dspy.ai/getting-started/composing-modules/
- **Snippet:** The negative datapoint: DSPy composes programs with plain Python control flow and has no edge/graph API at all.
- **Quote:** > There's no esoteric chaining API; modules are just Python and the DSPy primitives `Signature`, `Module`, and `LM`. ... When constructing a module, we need to write two functions: 1. `__init__` sets up our initial state and defines our submodules. 2. `forward` handles what happens when we call our program.

### FW-17
- **Title:** Module — DSPy API reference
- **URL:** https://dspy.ai/api/modules/Module/
- **Snippet:** Module is the composition unit; contains predictors, sub-modules, and custom logic — a tree of callables, not a declared edge set.
- **Quote:** > Base class for all DSPy modules (programs). ... A Module is a building block for DSPy programs that can contain predictors, sub-modules, and custom logic. Modules can be composed together to create com[plex programs]

### FW-18
- **Title:** Template agent workflows — Google Agent Development Kit (ADK)
- **URL:** https://google.github.io/adk-docs/agents/workflow-agents/
- **Snippet:** The deprecation notice: ADK's Sequential/Parallel/Loop template agents are superseded by graph-based and dynamic workflows as of v2.0.
- **Quote:** > Starting in ADK 2.0 for Python and Go, template workflows have been superseded by more flexible workflow structures, including graph-based workflows and dynamic workflows. These workflow architectures provide more control, flexibility and capability to evolve your agent workflows over time.

### FW-19
- **Title:** Cycle detected without exit condition: generator -> reviewer -> generator (microsoft/autogen #6628)
- **URL:** https://github.com/microsoft/autogen/issues/6628
- **Snippet:** AutoGen GraphFlow bug report whose traceback shows DiGraphBuilder.build() invoking graph_validate() -> has_cycles_with_exit() and raising ValueError before any execution begins.
- **Quote:** > File "/myautogenprj/myapp/test2.py", line 56, in main     graph = builder.build()   File ".../autogen_agentchat/teams/_group_chat/_graph/_graph_builder.py", line 175, in build     graph.graph_validate()   File ".../autogen_agentchat/teams/_group_chat/_graph/_digraph_group_chat.py", line 206, in graph_validate     self._has_cycles = self.has_cycles_with_exit()   File ".../_digraph_group_chat.py", line 163, in dfs     raise ValueError( ValueError: Cycle detected without exit condition: generator -> reviewer -> generator

## practitioner-trend

### PT-1
- **Title:** Graph Engineering: How to Build AI Agent Systems That Don't Break at Scale (X Article by @0xwhrrari / 'rari')
- **URL:** https://x.com/0xwhrrari/status/2086784668003598356
- **Snippet:** Operator-supplied seed #1. An X long-form Article (not a plain tweet) published 2026-08-10, 1.48M views, 1,397 bookmarks. Lays out a 12-section prescriptive method: nodes/edges/state, four canonical shapes (chain, diamond, router, controlled cycle), verification on the edge, durable state, convergence rules for cycles, local failure boundaries, topology-as-cost-model.
- **Quote:** > Graph engineering is the practice of turning an agentic workflow into an explicit execution map. Instead of hiding every decision inside one model loop, you define the system as nodes and edges. A node can be an agent, a tool call, a deterministic function, a verifier, or a human approval step. An edge says what is allowed to run next and what data crosses the boundary.

### PT-2
- **Title:** reira (@reiraxbt) — 'Anthropic Research Lead: 99% of our engineers run swarms of 300+ self-improving agents' (video post)
- **URL:** https://x.com/reiraxbt/status/2088295022194004138
- **Snippet:** Operator-supplied seed #2. Posted 2026-08-14, 9,726 views, 64 likes. A video-quote-card post promoting a 20-minute Anthropic talk. Text retrieved; the linked MP4 was NOT transcribed.
- **Quote:** > Anthropic Research Lead:  "99% of our engineers run swarms of 300+ self-improving agents"  "Close the loop and give the model a way to verify its own output"  In a 20-minute session, an Anthropic team member explains how to build agents that improve after every run  The real setup is Claude running through loops, plan mode, and dynamic workflows  The part most agent courses never show  Better than most $300 agent courses

### PT-3
- **Title:** Norvex (@norvex1029) — 'Anthropic engineer: 90% of our engineers were using self-improving loops. Now everyone has shifted to building agentic Graphs.' (video post)
- **URL:** https://x.com/norvex1029/status/2087230353035440452
- **Snippet:** Operator-supplied seed #3. Posted 2026-08-11, 173,222 views, 1,740 bookmarks. A video-quote-card post. Text retrieved; the linked MP4 was NOT transcribed.
- **Quote:** > Anthropic engineer: “90% of our engineers were using self-improving loops. Now everyone has shifted to building agentic Graphs.”  “No more prompting.”  In just 10 minutes, she builds her entire Claude Code setup and workflow live from a blank terminal.  This is more valuable than most $1,000 agentic courses.  Watch this video, then save the article below if you want to become a graph architect before everyone else catches up.

### PT-4
- **Title:** Peter Steinberger (@steipete) — the originating nine-word post (NOT RETRIEVED)
- **URL:** https://x.com/steipete
- **Snippet:** The post credited by multiple secondary sources as the origin of the 'graph engineering' label. The specific status URL was not located and the post text was not retrieved directly; it is attested only through third-party quotation.
- **Quote:** > Peter Steinberger's nine-word post - "Are we still talking loops or did we shift to graphs yet?" - landed with thousands of likes because it named something the field was already living through

### PT-5
- **Title:** From Loop Engineering to Graph Engineering? — Carlos E. Perez, Intuition Machine (2026-07-18)
- **URL:** https://medium.com/intuitionmachine/from-loop-engineering-to-graph-engineering-d3ebeb08511c
- **Snippet:** The essay that converted the meme into an argument, and the most-cited node in this corpus. Frames the shift as loops-watching-loops, names four structural failure modes of the single loop (Goodhart, blindness upward, conflict, measurement decay), then turns on its own thesis: topology without anchors fails the same way, later and more expensively.
- **Quote:** > It would be easy to conclude that the answer to improvement is simply more loops, better arranged — that topology is the cure. But push on the graph and a harder truth appears... Every loop watches another loop, and no loop touches the ground. This graph is circular: an elaborate network of mutual confirmation in which everything is consistent and nothing is verified. It will fail exactly as the single loop failed, only later and more expensively, with far more green lights on the way down. The topology bought sophistication. It did not buy contact with reality.

### PT-6
- **Title:** 3 Years of Graph Engineering with LangGraph — Sydney Runkle & Harrison Chase, LangChain (2026-07-22)
- **URL:** https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
- **Snippet:** The incumbent framework vendor's response. Explicitly classifies 'graph engineering' as a buzzword produced by X, dates the term to a single weekend, and claims the underlying practice is three years old and already shipped. Contributes the strongest anti-consensus evidence in the corpus: it denies the DAG framing that the practitioner posts assume.
- **Quote:** > "Graph engineering" surfaced this weekend, kicked off by this tweet... It's the latest term to come out of X's AI content factory, joining prompt engineering, context engineering, harness engineering, and loop engineering. While it’s both tempting and accurate to call these terms buzzwords, they exist and emerge for a reason.

### PT-7
- **Title:** We Are Entering the Graph Engineering Phase — Josh C. Simmons (2026-07-04)
- **URL:** https://www.drjoshcsimmons.com/writing/we-are-entering-the-graph-engineering-phase
- **Snippet:** Published TWO WEEKS BEFORE Perez's essay and the Steinberger post — i.e. before the label went viral. Offers the tightest three-commitment definition in the corpus (nodes = units of capability, edges = decisions, state = checkpointed schema) plus a practice list and a reference list including two arXiv IDs.
- **Quote:** > Graph engineering is designing agentic systems as explicit graphs instead of implicit loops. Three commitments, none of them exotic. Nodes are units of capability... Edges are decisions. An edge is a typed transition that carries state from one node to the next... State is an object with a schema, checkpointed every time you cross an edge. Not "whatever happens to be sitting in the context window right now."

### PT-8
- **Title:** Graph Engineering: When an Agent Loop Should Be a Graph — Sangam Pandey (2026-07-27)
- **URL:** https://sangampandey.info/blog/graph-engineering-agent-loops-to-graphs
- **Snippet:** The most epistemically careful source in the corpus. Defines graph engineering by the MOMENT the routing decision is made (authoring time vs inference time) rather than by the shape of the work, and explicitly rates the evidence base.
- **Quote:** > Graph engineering is the practice of deciding an agent workflow's control flow before the agent runs, by drawing the workflow as a graph and generating the orchestration code from that drawing... What separates it from an agent loop is not the shape of the work but the moment the routing decision gets made.

### PT-9
- **Title:** What 'Loops to Graphs' Looks Like in Production — Chris Lema (2026-07-20)
- **URL:** https://chrislema.com/loops-to-graphs-in-production
- **Snippet:** The strongest SHIPPED-ARTIFACT source in the practitioner corpus: a named operator walking Perez's four failure modes against a system running in production for seven days at Motivation Code, built on Mastra with thirteen workflows, six on cron schedules, and a Cloudflare Worker + D1 'brain' behind a Zod contract.
- **Quote:** > Thirteen Mastra workflows do the actual work, six of them on declarative cron schedules... Underneath all of it sits what I call the brain — a Cloudflare Worker with a D1 database that holds every piece of tenant knowledge, exposed to the agents over MCP and to my code over plain JSON, with every write validated against a shared Zod contract. The agents are stateless workers. The brain is the memory.

### PT-10
- **Title:** Graph Engineering with Claude Code: Subagents as an Agent Graph — Shirley, AI Builder Club (2026-07-24)
- **URL:** https://www.aibuilderclub.com/blog/graph-engineering-with-claude-code
- **Snippet:** Argues the label is a rename of Anthropic's already-published composable patterns, and maps Claude Code's existing primitives onto graph roles. Directly relevant to yf: subagents = nodes, main agent = orchestrator node, its routing = edges.
- **Quote:** > When "graph engineering" trended in mid-July 2026, the framing made it sound like a new discipline you had to go adopt. But Anthropic had already shipped the pattern under a plainer name. Their guide on building effective agents lays out five composable patterns - prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer. Read those as graphs and they snap into focus... Graph engineering is the label. This is the mechanism.

### PT-11
- **Title:** codejunkie99/graph-engineering — a Claude skill packaging 'graph engineering' (GitHub)
- **URL:** https://github.com/codejunkie99/graph-engineering
- **Snippet:** A shipped artifact that packages the label as an installable Claude skill. Notable because it defines graph engineering as TWO unrelated halves — knowledge graphs and task graphs — a scope no other source in the corpus shares.
- **Quote:** > **The discipline of designing the structures AI agents work through — not the prompts.** It has two halves: 1. **Knowledge graphs** — what agents *remember*... 2. **Task graphs** — how agents *work*. Nodes are jobs, edges are execution dependencies. Parallel fan-out, separate verifiers, the stop rule, the human gate. Prompt engineers steered the model's words. Loop engineers steered its iterations. Graph engineers steer its **topology**.

### PT-12
- **Title:** I Tried Applying Graph Engineering to Codex — Hyuk Min (2026-08-12)
- **URL:** https://hyuk.blog/en/diary/ai/graph-engineering-gate-codex-skill/
- **Snippet:** A negative-control-flavored field report: a practitioner deliberately reduces the trend to its smallest testable form (a single Gate Skill for Codex) after a 16-hour agent failure, tests it on one real contract, and reports honestly on what it did and did not prove.
- **Quote:** > It described an approach that does not leave everything to one Agent's long loop, but explicitly connects multiple Agents, verifiers, and human judgments as nodes and edges, defining which outcome permits the system to move to the next stage. Rather than an entirely new technology, it seemed closer to a recent name for established workflow and state-machine ideas.

### PT-13
- **Title:** From Agent Loops to Structured Graphs: A Scheduler-Theoretic Framework for LLM Agent Execution — Hu Wei, arXiv:2604.11378 (2026-04-13)
- **URL:** https://arxiv.org/abs/2604.11378
- **Snippet:** The only academic anchor the practitioner corpus points at (cited by PT-7). Characterizes the agent loop as a single-ready-unit scheduler and proposes Graph Harness / SGH, an explicit static DAG with immutable plan versions, three-layer separation of planning/execution/recovery, and a strict escalation protocol. Predates the July label by three months.
- **Quote:** > We characterize the Agent Loop as a single-ready-unit scheduler: at any instant, at most one executable unit is active, and the choice of which unit to activate is the output of an opaque LLM inference rather than an inspectable policy. This characterization lets us place Agent Loops and graph-based execution engines on a single semantic continuum.

## yf-codebase

### YF-1
- **Title:** yf-plan SPEC REQ-PHASE-002 — intake-at-execute: the molecule is not poured during INTAKE
- **URL:** skills/yf-plan/spec/phases.md:9
- **Snippet:** The construction phases (SCOPE/INVESTIGATE/PLAN/review) produce no beads; the pour happens at EXECUTE start.
- **Quote:** > REQ-PHASE-002: PLAN-approval and EXECUTE are separated by a session boundary. Under the **intake-at-execute** model the molecule is **not** poured during INTAKE; INTAKE writes the content fingerprint (REQ-PORT-040), auto-commits the plan (REQ-PLAN-064), and lands it. The `bd mol pour` and its human start gate are created at **EXECUTE start** (`/yf-plan execute`, a new session)

### YF-2
- **Title:** plan-033 log.md — five red-team review cycles, recorded only as prose
- **URL:** docs/plans/plan-033-james-dixson-46aca2/log.md:16
- **Snippet:** A completed plan bundle shows a 5-iteration REVISE/APPROVE loop with no bead representation.
- **Quote:** > - review: red-team pass-5 APPROVE — pass-4 F1–F7 resolved (Pi-target investigate+gate, sub-verb relocation, revert-on-tune, bare-install warning, hermetic detect) - review: red-team pass-4 REVISE — multi-harness re-scope (yf harness skills relocation + rules-move + auto-detect); Pi-rules-target high concern - review: red-team pass-3 APPROVE — Epic 7 (code-accurate web docs + doc↔code agreement test) added per operator request - review: red-team pass-2 APPROVE — pass-1 concerns C1–C5 resolved (delta-replay, Pi deferred, revert guard)

### YF-3
- **Title:** Live bd graph — plan-033 epic contains 40 issues, all execution issues
- **URL:** bd:graph yf-mol-y7f --json (docs/plans/plan-033-james-dixson-46aca2)
- **Snippet:** The poured epic for plan-033 has 40 nodes / 38 blocking edges across 16 layers; none correspond to the 5 review cycles.
- **Quote:** > Dependencies: 38 blocking relationships   Total: 40 issues across 16 layers

### YF-4
- **Title:** yf-research formula — a strict linear needs-chain of seven steps
- **URL:** skills/yf-research/formulas/yf-research.formula.toml:20
- **Snippet:** Every `[[steps]]` entry has needs = [single predecessor]; no fan-out, join, conditional, retry or loop construct.
- **Quote:** > `[[steps]]` id = "gate" ... `[[steps]]` id = "tooling" type = "task" needs = ["gate"] ... `[[steps]]` id = "triangulate" needs = ["tooling"] ... id = "synthesize" needs = ["triangulate"] ... id = "critique" needs = ["synthesize"] ... id = "refine" needs = ["critique"] ... id = "package" needs = ["refine"]

### YF-5
- **Title:** yf-plan Phase 2 INVESTIGATE — parallel sub-agent fan-out
- **URL:** skills/yf-plan/SKILL.md:308
- **Snippet:** The only place yf-plan dispatches N agents concurrently.
- **Quote:** > Spawn a sub-agent per unknown using `Agent` with `isolation="worktree"`, `mode="bypassPermissions"`. ... Independent experiments run in parallel.

### YF-6
- **Title:** plan-investigate formula — a vapor-phase wisp with dynamically injected steps, burned after use
- **URL:** skills/yf-plan/formulas/plan-investigate.formula.toml:5
- **Snippet:** The investigation fan-out's graph is created disposable and destroyed.
- **Quote:** > phase = "vapor" ... # Steps are injected dynamically -- one per experiment identified # during the scoping phase. Each experiment becomes a task bead # dispatched to an investigator subagent in a disposable worktree. # # The wisp lifecycle: #   1. Create: bd mol wisp plan-investigate --var ... #   2. Inject experiment beads as children #   3. Execute: investigator subagents in worktrees #   4. Burn: bd mol burn <id> after findings captured

### YF-7
- **Title:** yf-plan §5.2a — the investigation wisp is burned with output discarded
- **URL:** skills/yf-plan/SKILL.md:827
- **Snippet:** The fan-out molecule is destroyed at intake; its graph is never walked.
- **Quote:** > bd mol burn ${INVESTIGATION_WISP_ID} --force 2>/dev/null || true

### YF-8
- **Title:** yf-research Phase 3 step 5 — dynamic retrieve fan-out via a shell for-loop in prose
- **URL:** skills/yf-research/SKILL.md:309
- **Snippet:** One bead per source cluster, created by a loop the model executes.
- **Quote:** > RETRIEVE_IDS=() for cluster in ${clusters}; do   # Build metadata with jq -nc --arg, never shell interpolation (see yf-beads-authoring).   META=$(jq -nc --arg agent "agents/retriever.md" --arg cluster "${cluster_name}" \     '{agent:$agent, context:["plan.yaml"], cluster:$cluster}')   RID=$(bd create "Retrieve: ${cluster_name}" \     --description="Gather sources from ${cluster_targets}. Method: ${cluster_method}." \     -t task -p 2 --parent ${EPIC} --deps "${TOOLING_ID}" \     --metadata "$META" --silent)   [ -z "$RID" ] && { echo "ERROR: retrieve bead create failed" >&2; exit 1; }   RETRIEVE_IDS+=("$RID") done

### YF-9
- **Title:** yf-research Phase 3 step 6 — the join, wired as a single batched dep-add transaction
- **URL:** skills/yf-research/SKILL.md:328
- **Snippet:** Triangulate is made to depend on every retrieve bead.
- **Quote:** > DEP_OPS="" for rid in "${RETRIEVE_IDS[@]}"; do   DEP_OPS+="dep add ${TRIANG_ID} ${rid}\n" done [ -n "$DEP_OPS" ] && printf '%b' "$DEP_OPS" | bd batch -m "yf-research ${EPIC} retrieve wiring"

### YF-10
- **Title:** yf-research SPEC REQ-PHASE-003/004/006 — dynamic fan-out, batched join, and the parallelism claim
- **URL:** skills/yf-research/spec/phases.md:16
- **Snippet:** The parallelism requirement is verified against graph SHAPE (needs edges), not against execution.
- **Quote:** > REQ-PHASE-003: RETRIEVE fans out dynamically — one bead per `source_cluster`, injected after pour (the formula defines the fixed skeleton only). ... REQ-PHASE-004: TRIANGULATE is wired to depend on every RETRIEVE bead using additive `bd dep add` batched through `bd batch` ... REQ-PHASE-006: Retrieval is parallel; triangulation/synthesis/critique/refinement are serial. Rationale: Clusters are independent (parallelizable); downstream stages each depend on the prior's output. Verification: formula `needs` edges; retrieve beads share the tooling dependency only.

### YF-11
- **Title:** yf-research SPEC REQ-PHASE-005 — runtime DAG extension via discovered-from
- **URL:** skills/yf-research/spec/phases.md:24
- **Snippet:** REFINE may add new retrieve beads at runtime.
- **Quote:** > REQ-PHASE-005: REFINE may extend the DAG at runtime by spawning new RETRIEVE beads via `--deps discovered-from:<refine-id>` when the red-team identifies gaps.

### YF-12
- **Title:** refiner.md — the gap-fill retrieve is wired forward to PACKAGE, not back to TRIANGULATE
- **URL:** skills/yf-research/agents/refiner.md:33
- **Snippet:** The feedback edge is cut: newly retrieved evidence is never re-triangulated or re-critiqued.
- **Quote:** > NEW_RID=$(bd create "Retrieve: <gap topic>" \      --deps "discovered-from:${REFINE_BEAD_ID}" \      --parent ${EPIC} --metadata "$META" --silent)    [ -z "$NEW_RID" ] && { echo "ERROR: create failed" >&2; exit 1; }    bd dep add ${PACKAGE_BEAD_ID} ${NEW_RID}

### YF-13
- **Title:** plan_manager.py — 3525 lines with no graph construction code (absence finding)
- **URL:** skills/yf-plan/scripts/plan_manager.py:1
- **Snippet:** grep of `def ` across the file yields plan-folder bookkeeping, fingerprinting, worktree, and config verbs only.
- **Quote:** > 3525 skills/yf-plan/scripts/plan_manager.py

### YF-14
- **Title:** plan_manager.py — every bd subprocess call is read-only or an external-ref stamp
- **URL:** skills/yf-plan/scripts/plan_manager.py:1181
- **Snippet:** No bd create, no bd dep add, no bd mol pour anywhere in the script.
- **Quote:** > 1181:        out = subprocess.check_output(["bd", "show", bead_id, "--json"], 1249:        subprocess.run(["bd", "update", epic_id, "--external-ref", tracker_url, "-q"], 2118:        r = subprocess.run(["bd", "list", "--json"], cwd=wt_abs, 2748:        out = subprocess.check_output(["bd", "list", *args, "--json"],

### YF-15
- **Title:** research_manager.py — 164 lines, two verbs, no graph code (absence finding)
- **URL:** skills/yf-research/scripts/research_manager.py:65
- **Snippet:** The entire manager script is a defensive JSON parser plus an epic-pointer writer.
- **Quote:** > 25:def _extract_first_json(text: str): 65:def cli(): 72:def json_get(keys: tuple[str, ...]): 106:def record_epic(research_dir: str, epic_id: str):

### YF-16
- **Title:** yf-research SKILL.md — the manager script is intentionally narrow
- **URL:** skills/yf-research/SKILL.md:142
- **Snippet:** The skill states explicitly that no orchestration logic lives in code.
- **Quote:** > `research_manager.py` is intentionally narrow — a defensive `json-get`.

### YF-17
- **Title:** plan_manager.py — the only occurrence of '## Epics' is a seed template string
- **URL:** skills/yf-plan/scripts/plan_manager.py:545
- **Snippet:** The plan's Epics section is written by the script but never parsed by it.
- **Quote:** > 545:## Epics

### YF-18
- **Title:** yf-plan §5.2a 'Create beads from plan.md' — the DAG compiler is an LLM reading markdown
- **URL:** skills/yf-plan/SKILL.md:749
- **Snippet:** Bead creation and dependency wiring are prose instructions, not a parser.
- **Quote:** > **Create beads from plan.md.** Never block a child epic on the start gate: `${START_GATE}` is a task, and bd rejects a task blocking an epic ... Child epics are containers: create them with `--parent` only. Gate the epic's **entry leaf issues** (those with no intra-plan predecessor) on `${START_GATE}`; downstream issues depend on their predecessors and inherit the gate transitively.

### YF-19
- **Title:** plan-execute formula — one node; 100% of the plan DAG is dynamically injected
- **URL:** skills/yf-plan/formulas/plan-execute.formula.toml:24
- **Snippet:** The formula declares only the start gate; everything else is created by the model at execute time.
- **Quote:** > # Execution steps (epics, issues, capability gates) are injected # dynamically from plan.md during Phase 4 intake. The intake process # reads the plan's Epics and Gates sections and creates bd issues: # entry leaf issues are wired to the start gate (child epics are not — # bd rejects a task blocking an epic). See SKILL.md §4.3.

### YF-20
- **Title:** Measured layer widths of four real yf epics
- **URL:** bd:graph <epic> --json | layout.Layers (yf-mol-62k, yf-mol-3py, yf-mol-y7f, yf-mol-e9q)
- **Snippet:** Research epics are chains with one bulge; plan epics are near-trees (|E| ~= |V|).
- **Quote:** > yf-mol-y7f layers= 16 widths= [13, 1, 1, 4, 4, 3, 4, 1, 1, 1, 2, 1, 1, 1, 1, 1] max_width= 13 yf-mol-e9q layers= 9 widths= [11, 2, 2, 6, 10, 1, 1, 2, 1] max_width= 11 yf-mol-3py layers= 9 widths= [3, 1, 1, 5, 1, 1, 1, 1, 1] max_width= 5 yf-mol-62k layers= 9 widths= [3, 1, 1, 4, 1, 1, 1, 1, 1] max_width= 4

### YF-21
- **Title:** yf-plan — container epics carry no dependency edges (bd rejects task-blocks-epic)
- **URL:** skills/yf-plan/SKILL.md:751
- **Snippet:** Explains why layer 0 of a plan graph is wide but edge-free.
- **Quote:** > bd rejects a task blocking an epic (`epics can only block other epics, not tasks` — see `yf-beads-extra` → *Epic blocking rule*). Child epics are containers: create them with `--parent` only.

### YF-22
- **Title:** Live bd graph of this research run — a chain with one 4-wide layer, plus an orphan swarm node
- **URL:** bd:graph yf-mol-62k (docs/research/003-graph-engineering-hypothesis)
- **Snippet:** 9 layers, 14 issues, 15 edges. The 'Swarm: yf-research' node has zero in-edges and zero out-edges.
- **Quote:** > LAYER 0 (ready)  ...  LAYER 8 │ ○ yf-research │  ╭─▶│ ✓ Begin research: Graph … │─────▶│ ✓ Build tooling: Graph e… │────┬▶│ ◐ Retrieve: practitioner… │─┬┬─┬▶│ ○ Triangulate: Graph eng… │─────▶│ ○ Synthesize: Graph engi… │─────▶│ ○ Critique: Graph engine… │─────▶│ ○ Refine: Graph engineer… │─────▶│ ○ Package: Graph enginee… │ ... │ ○ Swarm: yf-research      │ │ yf-wxp9 P2                │ ... Dependencies: 15 blocking relationships   Total: 14 issues across 9 layers

### YF-23
- **Title:** yf-research SPEC REQ-PHASE-007 — a gate step compiles to two beads
- **URL:** skills/yf-research/spec/phases.md:32
- **Snippet:** Gates are first-class but split into a wrapper task plus a real gate node.
- **Quote:** > REQ-PHASE-007: A `type = "gate"` formula step yields a task wrapper (`yf-research.gate`) plus the real gate (`yf-research.gate-gate`); the gate is resolved via the `gate-*` key, while downstream `needs` depends on the wrapper.

### YF-24
- **Title:** yf-plan — capability gates are beads carrying an executable test command
- **URL:** skills/yf-plan/SKILL.md:786
- **Snippet:** The only executable predicate on a yf-plan edge.
- **Quote:** > CAP_GATE=$(bd create "Gate: ${gate_name}" \   --description="Condition: ${condition}\nTest: ${test_cmd}\nInstructions: ${instructions}" \   -t gate --parent ${EPIC} \   --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)

### YF-25
- **Title:** yf-plan §5.5 — the reconcile gate auto-resolves when all execution beads close
- **URL:** skills/yf-plan/SKILL.md:936
- **Snippet:** The single auto-evaluated predicate node in either skill's graph.
- **Quote:** > Auto-resolves when all execution beads close. Proceed to Phase 6.

### YF-26
- **Title:** bd swarm create — the only occurrence of 'swarm' in the entire skills/ tree
- **URL:** skills/yf-research/SKILL.md:336
- **Snippet:** grep -rn swarm skills/ returns exactly two lines, both in this block. No coordinator, formula, or spec reads it.
- **Quote:** > 7. **Create swarm and report:**  bd swarm create ${EPIC} --json bd graph ${EPIC}

### YF-27
- **Title:** yf-plan coordinator — discovered-from is mandated for runtime work discovery
- **URL:** skills/yf-plan/agents/coordinator.md:123
- **Snippet:** Runtime graph mutation is prescribed.
- **Quote:** > - New work discovered during execution: `bd create ... --deps discovered-from:<parent-id>`

### YF-28
- **Title:** yf-plan §5.2b orphan sweep — discovered-from edges carry no machine-readable disposition
- **URL:** skills/yf-plan/SKILL.md:896
- **Snippet:** The edge type is written but cannot be interpreted by the recovery path.
- **Quote:** > **report** — never auto-close — any bead the sweep cannot positively classify, leaving the close decision to the operator. No bead is auto-closed: there is no reliable bd-state signal separating disposable scratch from real `discovered-from` work.

### YF-29
- **Title:** yf-research coordinator Execution Loop — sequential, one bead per iteration
- **URL:** skills/yf-research/agents/coordinator.md:50
- **Snippet:** poll -> claim ONE -> dispatch ONE -> close ONE -> repeat. No parallel dispatch, no join logic, no retry.
- **Quote:** > Repeat until `bd ready --json` returns no beads for this epic:  1. **Find ready work:**    bd ready --json    Filter to beads whose parent is `${EPIC}`. 2. **Claim the bead:**    bd update <id> --claim --json 3. **Read the bead's metadata.** ... 4. **Dispatch the agent:** ... Spawn subagent (via Agent tool) with agent file as prompt and context files as working data 5. **Record the artifact:** ... 6. **Close the bead:**    bd close <id> --reason "Completed" --json 7. **Repeat** from step 1.

### YF-30
- **Title:** yf-plan coordinator Loop — the same sequential six-step cycle with gate handling
- **URL:** skills/yf-plan/agents/coordinator.md:41
- **Snippet:** Singular nouns throughout; no batching of the ready set.
- **Quote:** > Repeat until `bd ready --json` returns no beads for this epic:  1. `bd ready --json` — filter to beads under `${EPIC}` 2. For gate-type beads: read description, run test command    - Pass: `bd gate resolve <gate-id>`    - Fail: mark blocked, skip 3. `bd update <id> --claim --json` 4. `bd show <id> --json` — read metadata 5. If metadata specifies agent file, spawn sub-agent with that prompt. Otherwise execute directly. Pass context files from `plan_dir`. 6. `bd close <id> --reason "Completed" --json`

### YF-31
- **Title:** yf-plan SPEC REQ-AGENT-010 — the serial loop is normative
- **URL:** skills/yf-plan/spec/agents.md:15
- **Snippet:** The six-step cycle is a specified requirement with a verification clause, not incidental prose.
- **Quote:** > REQ-AGENT-010: The coordinator drives the bead DAG via a `bd ready` → claim → execute → close loop. Rationale: This is the core execution engine; deviating from the loop skips work or double-executes. Verification: coordinator.md Loop section describes the 6-step cycle.

### YF-32
- **Title:** yf-plan SPEC REQ-AGENT-011 — 'parallel work' means keep iterating the serial loop
- **URL:** skills/yf-plan/spec/agents.md:19
- **Snippet:** The only concurrency assertion in the coordinator spec is about draining, not concurrent dispatch.
- **Quote:** > REQ-AGENT-011: The coordinator drains all unblocked work before reporting blocked gates. Rationale: Reporting a blocked gate while parallel work remains wastes operator attention.

### YF-33
- **Title:** plan-033 plan.md — a genuine multi-parent DAG authored in prose (25 depends-on edges)
- **URL:** docs/plans/plan-033-james-dixson-46aca2/plan.md:511
- **Snippet:** plan.md IS graph-shaped source, including gate references in dependency lists.
- **Quote:** > - depends-on: 6.2, 1.5, gate:pi-rule-target-verified

### YF-34
- **Title:** yf-plan Phase 3 Review — two structurally independent reviewers, serialized
- **URL:** skills/yf-plan/SKILL.md:412
- **Snippet:** Conformance must PASS before the adversarial pass runs.
- **Quote:** > Two passes, in order. Both agents are read-only (REQ-AGENT-043); the main session acts on their verdicts.  1. **Conformance** — read `${SKILL_DIR}/agents/reviewer.md` and run its mechanical checklist. Verdict `PASS | INCOMPLETE`. On `INCOMPLETE`, resolve the listed gaps and re-run before proceeding ... 2. **Adversarial** — once conformance is `PASS`, read `${SKILL_DIR}/agents/red-team.md` and perform a structured adversarial review.

### YF-35
- **Title:** yf-plan Phase 2 Post-investigation — an explicit serialization barrier on the one fan-out
- **URL:** skills/yf-plan/SKILL.md:321
- **Snippet:** In tension with 'Independent experiments run in parallel' 13 lines earlier.
- **Quote:** > After each sub-agent returns: 1. Write finding to `findings/exp-NNN-<slug>.md` 2. Update plan.md Investigation Findings 3. Both writes BEFORE next sub-agent spawns

### YF-36
- **Title:** retriever.md — N parallel retrievers are told to write one shared sources.json with no merge strategy
- **URL:** skills/yf-research/agents/retriever.md:150
- **Snippet:** The fan-out's join has no defined write semantics.
- **Quote:** > 4. For each source found, record in `${research_dir}/sources.json`:    - URL, title, snippet, retrieval timestamp    - Preliminary credibility assessment    - Provider used (`exa`, `tavily`, `perplexity`, etc.)    - `quote`: a verbatim excerpt from the source supporting the finding (not a paraphrase)

### YF-37
- **Title:** yf-plan SPEC REQ-AGENT-044/045 — the two reviewers are deliberately non-interfering
- **URL:** skills/yf-plan/spec/agents.md:87
- **Snippet:** Disjoint checklists and disjoint verdict vocabularies; i.e. structurally independent yet serialized.
- **Quote:** > REQ-AGENT-044: The reviewer produces a conformance verdict of PASS or INCOMPLETE against a mechanical checklist ... It runs before the red-team pass and produces no `pass-N.md`. ... REQ-AGENT-045: The reviewer is read-only and conformance-only. It does not assess feasibility, risk plausibility, or approach soundness — those belong to the red-team. Rationale: Separating the conformance and adversarial stances into non-interfering agents (the factoring test, case b) keeps each prompt focused

### YF-38
- **Title:** close_cascade.py — the only topological algorithm in the repo, over the containment tree
- **URL:** skills/yf-plan/scripts/close_cascade.py:9
- **Snippet:** 241 lines; a bottom-up walk of parent/child containment, not of dependency edges, run once at teardown.
- **Quote:** > On plan COMPLETE, walk the plan's bead tree bottom-up and close every **container** (intermediate epic and the top-level plan molecule) whose children are **all terminal**, ... Self-contained on purpose: uses only `bd children` / `bd list` / `bd close` and a private

### YF-39
- **Title:** close_cascade.py — explicit post-order recursion
- **URL:** skills/yf-plan/scripts/close_cascade.py:162
- **Snippet:** The one genuine DFS in the codebase.
- **Quote:** > # Container: process children first (post-order / bottom-up).

### YF-40
- **Title:** yf-plan SPEC REQ-AGENT-047 — a DAG-walk engine was measured and deliberately rejected
- **URL:** skills/yf-plan/spec/agents.md:76
- **Snippet:** The strongest evidence that yf's linearity is a considered choice, not an oversight.
- **Quote:** > Across the five defects observed in d3-pxe plan-013, the precondition was written out in plain English in the issue body every time; only the machine-readable dependency edge was missing. A prose-vs-DAG cross-check therefore has enough information to catch them without a schema change. This is deliberately the prose check, not a topological DAG walk: the expensive branch (a `requires:` key plus a walk engine) was measured against the same corpus and found to buy nothing, and 2 of the 5 defects are not reachability failures a graph walk would find at all.

### YF-41
- **Title:** Root SPEC.md living-amendment log — the same rejection, recorded at project level
- **URL:** SPEC.md:268
- **Snippet:** plan-039 shipped the prompt-level branch explicitly without a DAG-walk engine.
- **Quote:** > **`REQ-AGENT-047`** (red-team **precondition cross-check** — each issue's assumed artifacts, tools, and capabilities are produced by a declared `depends-on` predecessor or established by a gate; #113's cheap branch, explicitly **without** a `requires:` schema key or a DAG-walk engine, which measurement against the same corpus found unjustified)

### YF-42
- **Title:** yf-plan SPEC REQ-AGENT-046 rationale — an unsatisfiable gate (a graph cycle) survived two review cycles
- **URL:** skills/yf-plan/spec/agents.md:72
- **Snippet:** A structural defect that a graph engine catches and prose review demonstrably did not.
- **Quote:** > In d3-pxe plan-013 a capability gate whose condition required a preview of the output of the very issue it blocked survived conformance and **two** red-team cycles, because every pass checked that the gate declared a type, approvers, a condition, and a test — none checked whether the condition could ever become true. The same cycle was independently reproduced in this skill's own plan-039 draft.

### YF-43
- **Title:** yf-plan SPEC REQ-AGENT-046 — gate reachability is checked by an LLM prompt, not a cycle detector
- **URL:** skills/yf-plan/spec/agents.md:71
- **Snippet:** Cycle detection is delegated to a red-team checklist item.
- **Quote:** > REQ-AGENT-046: The red-team checks **gate reachability**, not only gate well-formedness: for each capability gate, its `Condition` must be satisfiable given what the gate `Blocks`. A condition that depends on evidence produced by an issue inside its own `Blocks` set is a cycle and is reported as a defect; the remedy is to gate the *mutating* step rather than the step that produces the evidence.

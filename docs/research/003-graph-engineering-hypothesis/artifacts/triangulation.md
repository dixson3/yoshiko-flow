---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Triangulation

Cross-cluster triangulation for bead `yf-mol-reh`, research project `003-graph-engineering-hypothesis`.
Inputs: `sources.json` (89 sources) and the four cluster artifacts —
`cluster-practitioner-trend.md` (`PT-1`…`PT-13`), `cluster-framework-evidence.md` (`FW-1`…`FW-18`),
`cluster-yf-codebase.md` (`YF-1`…`YF-43`), `cluster-comparative-execution.md` (`CE-1`…`CE-15`).

This artifact introduces no claims that do not appear in the retrieval artifacts. Where it reaches a
conclusion the retrievers did not state, that conclusion is an *arrangement* of their quoted evidence
and is labelled as such.

---

## 0. Independence audit (read this before any consensus claim)

Corroboration only counts when the underlying artifacts differ. A mechanical URL comparison across
`sources.json` finds **three literal duplicates** and **one vendor mirror** spanning the
framework-evidence and comparative-execution clusters:

| Cluster A id | Cluster B id | Relationship | URL |
|:-------------|:-------------|:-------------|:----|
| `CE-1` | `FW-1` | **Identical URL** | `https://docs.langchain.com/oss/python/langgraph/graph-api` |
| `CE-2` | `FW-4` | **Identical URL** | `https://docs.langchain.com/oss/python/langgraph/checkpointers` |
| `CE-5` | `FW-9` | **Identical URL** | `https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html` |
| `CE-3` | `FW-5` | **Vendor mirror** — different hosts, same LangChain HITL content, same quoted sentence | `langchain-ai.github.io/langgraph/concepts/human_in_the_loop/` vs `docs.langchain.com/oss/python/langgraph/interrupts` |

Consequences that must be applied throughout:

1. **Any claim resting on the LangGraph super-step / checkpointer / interrupt evidence is
   single-sourced across the two clusters, not double-sourced.** Both retrievers quote the *same*
   sentences (e.g. the "In addition to super-step checkpoints, LangGraph also persists writes at the
   **node (task) level**" passage appears verbatim as `[CE-2]` and `[FW-4]`).
2. **AutoGen GraphFlow's capability claims** (`"Sequential chains, Parallel fan-outs, Conditional
   branching, Loops with safe exit conditions"`) are likewise one artifact quoted twice
   (`[CE-5]` = `[FW-9]`).
3. There is a further **vendor-level** (not URL-level) overlap: LangChain appears in
   practitioner-trend as `[PT-6]` (blog) and in both other web clusters as its own docs. LangChain is
   therefore present in **all three** web clusters and is the single most over-represented voice in
   the corpus. Agreement between `[PT-6]` and `[FW-1]`…`[FW-7]` is **not** independent corroboration.

Genuinely independent legs that survive this audit — used below to carry the weight the shared
sources cannot: `[CE-6]` (AutoGen issue tracker, third-party observation of a vendor's own bug),
`[CE-4]` (third-party analysis of LangGraph), `[CE-7]` (source-cited generated docs for Mastra),
`[CE-10]` (DBOS), `[CE-8]`/`[CE-9]` (Temporal), `[CE-11]` (Restate), `[CE-12]`…`[CE-15]` (four
unrelated tracker-as-store projects), `[FW-8]` (pydantic-graph), `[FW-10]`/`[FW-11]` (Burr),
`[FW-12]` (LlamaIndex), `[FW-14]`/`[FW-15]`/`[FW-18]` (Google ADK), `[FW-16]`/`[FW-17]` (DSPy), and
the whole `YF-*` set (direct repo reads, single observer).

---

## 1. Consensus findings, ranked by corroboration strength

Bar for "consensus": **3+ independent underlying artifacts** after the § 0 audit. Findings below the
bar are marked `[insufficient evidence]` and are not resolved by picking a side.

| # | Finding | Clusters | Independent artifacts | Strength |
|:--|:--------|:---------|:----------------------|:---------|
| C1 | Fan-out is a solved, universal primitive; **join/fan-in is where systems actually break** | PT, FW, CE, YF | 8+ | **Strong** |
| C2 | HITL gates are universal, but **placement splits by where the graph lives** | PT, FW, CE, YF | 7 | **Strong** |
| C3 | **No shipped system resumes finer than the node/task**; the granularity gradient is real | FW, CE, YF | 5 (after removing 1 shared) | **Strong** |
| C4 | Conditional edge / router is a real implemented primitive, mature enough to have grown predicate languages | FW, CE, PT | 6 systems | **Strong** |
| C5 | Edges should be **deterministic code, not model calls** | PT, FW, CE | 6 | **Strong** |
| C6 | Nothing about graph topology has been **measured** for outcome | PT, FW, CE, YF | 4 (meta) | **Strong** |
| C7 | Retry belongs at the leaf; per-node retry policy is **rare** | FW, CE, YF | 5 | Moderate-strong |
| C8 | Store the edges, **derive** readiness — persisting derived scheduler state is a known corruption mode | CE, YF | 4 (failure half: 1) | Moderate |
| C9 | Move artifact **references**, not payloads, between nodes | PT, CE, YF | 2 external + 1 implementation | `[insufficient evidence]` for consensus |
| C10 | Fork / time-travel from an arbitrary past checkpoint | FW only | 2 | `[insufficient evidence]` for consensus |

### C1 — Fan-out is easy; join is the recurring defect (**Strong**)

Both external clusters reached this independently, and — importantly — **not** through the shared
LangGraph docs. comparative-execution reaches it through a third-party analysis and a bug tracker;
framework-evidence reaches it through an inventory of who ships a named join at all.

> "A normal edge marks its target eligible the moment any single upstream task reaches it. With
> parallel branches — or worse, branches of unequal length ... the aggregator fires early, on
> whichever branch arrives first, and reduces over partial data." `[CE-4]`

> "`defer=True` is not a dependency resolver. ... It is a scheduling barrier on the super-step queue —
> its entire semantics are 'run me when nothing else is left to run.'" `[CE-4]`

Framework-evidence, from a different direction — an absence census:

> "**'Fan-in' is under-specified across the whole field.** LangGraph has no join node — fan-in is a
> reducer on a state channel (FW-3). Burr has none in the retrieved material. Only ADK names
> `AddFanIn` (FW-15) and LlamaIndex names `ctx.collect_events` (FW-12). If yf needs a real barrier /
> join, there is no dominant industry spelling to copy."

The strongest *independent* leg is the AutoGen tracker — an observation made against the vendor's
own interest, which `[CE-6]` correctly identifies as this cluster's best-supported claim:

> "When a GraphFlow workflow is interrupted (e.g., via `KeyboardInterrupt`) during the transition
> between agents, the saved state becomes corrupted. On resume, the workflow terminates immediately
> with: `Digraph execution is complete` —even though agents still have remaining work." `[CE-6]`

The practitioner corpus supplies the same shape from the design side:

> "parallelism is the cheapest lever left. ... Fan-out and fan-in are graph operations. The loop does
> not have verbs for them." `[PT-7]`

And yf is a fourth, independent instance — with fan-out and join **correctly wired at the bead
layer** (`[YF-8]`, `[YF-9]`: `dep add ${TRIANG_ID} ${rid}` batched transactionally) and the join
**unresolved at the artifact layer**:

> "4. For each source found, record in `${research_dir}/sources.json`" `[YF-36]`

— i.e. N parallel retrievers writing one file with no merge semantics (`YF` d10). The cluster records
that this hazard was patched **by hand at dispatch time** for this very research run
(`[uncited: the override text is the prompt of that agent, not a repo file]`).

**Arrangement (mine, not the retrievers'):** across every system in the corpus, the join is either
(a) a weaker second mechanism, (b) an open bug, or (c) absent. yf's `bd`-derived readiness is the
one join in the corpus that is neither weak nor buggy — and yf then bypasses it for artifact merges.

### C2 — HITL gates are universal; placement splits by where the graph lives (**Strong**)

Every system in the corpus that has a persistence story also has a gate. Three placements, and the
split is **not random** — it tracks whether the graph lives in-process or in a store.

| Placement | Systems | Evidence |
|:----------|:--------|:---------|
| Runtime call inside node code | LangGraph `interrupt()` | `[FW-5]` = `[CE-3]` (one artifact) |
| Step-level suspend | Mastra `.resume()` | `[CE-7]` |
| **Gate as a node type** | Google ADK ("human input tasks" as a node kind) | `[FW-15]` |
| **Gate as a record the store refuses to advance past** | clu, task-orchestrator, ticks, yf | `[CE-13]`, `[CE-14]`, `[CE-12]`, `[YF-23]`/`[YF-24]` |

> "A graph is composed of execution nodes. These *nodes* can be ***Agents***, ADK ***Tools***, human
> input tasks, or code functions you write." `[FW-15]`

> "The enforcement happens at the tool level: if a required design note isn't filled, `advance_item`
> returns an error. If a dependency isn't satisfied, the transition is blocked. ... Dependency
> ordering is enforced by the server — structurally, not by convention." `[CE-14]`

> "a `checkpoint` issue is a manual gate (stays `checkpoint:pending` until `clu approve`)" `[CE-13]`

The practitioner corpus independently prescribes exactly the store-backed placement:

> "Treat humans as nodes. Approval deserves the same design attention as any other capability: an
> edge in, an edge out, a person in the middle. Bolting it onto the outside as an exception handler
> is how you get systems that technically have oversight and practically have none." `[PT-7]`

yf implements the gate-as-record placement (`type = "gate"` beads with a two-bead compile artifact,
`[YF-23]`; capability gates carrying an executable `Test:` command, `[YF-24]`). **Arrangement:** on
this axis yf is on the majority side of a 4-artifact independent consensus, and its capability gate
with an executable test is *stronger* than clu's or task-orchestrator's, which gate on human
approval only.

### C3 — No shipped system resumes finer than the node/task (**Strong**, with one shared leg disclosed)

**This is thread 1 of the commission, and the answer is: partially independent.** The LangGraph leg
is literally one artifact quoted by both clusters (`[CE-2]` = `[FW-4]`, § 0). Remove it and the claim
still stands on four independent legs:

| Leg | System | Granularity | Evidence |
|:----|:-------|:------------|:---------|
| Shared (**one** artifact) | LangGraph | super-step + per-task pending writes | `[CE-2]` = `[FW-4]` |
| Independent | LangGraph interrupts | whole-node re-execution | `[FW-5]` |
| Independent | Apache Burr | after each action | `[FW-11]` |
| Independent | DBOS | per-step memoised replay | `[CE-10]` |
| Independent | AutoGen GraphFlow | resume exists but is **not crash-consistent** | `[CE-6]` |
| Independent | Tier C (ticks, clu, task-orchestrator) | task is the atom; crash re-runs it whole | `[CE-12]`, `[CE-13]`, `[CE-14]` |

> "The node restarts from the beginning of the node where the `interrupt` was called when resumed, so
> any code before the `interrupt` runs again." `[FW-5]`

> "As the workflow re-executes, it checks before each step if that step's output is checkpointed in
> Postgres. If there is a checkpoint, the step returns the checkpointed output instead of executing."
> `[CE-10]`

Both retrievers stated the conclusion in near-identical terms, which — given the shared leg — is
better read as convergent framing than as independent confirmation:

> "Neither offers statement-level resume. Any yf design that assumes finer-grained resume would be
> off the map of shipped practice." (framework-evidence, obs 6)

> "Every Tier C system surveyed treats the task as the atom and re-runs it whole. For long agent
> tasks this is the most expensive gap." (comparative-execution, obs 5)

**Caveat that must travel with this finding:** it is an *absence* claim drawn from documentation. A
doc that does not describe statement-level resume is not proof that no system has it. The claim is
well-supported as "no system in this 89-source corpus documents finer-than-node resume", and
over-stated as "no shipped system does".

### C4 — Conditional edge / router is real, implemented, and has grown predicate languages (**Strong**)

Six independent systems implement it under six names — the strongest *implementation*-level
convergence in the corpus.

> "Add a conditional edge from the starting node to any number of destination nodes. ... The callable
> that determines the next node or nodes." `[FW-2]`

> "Conditions are evaluated in the order they are specified, and the first one that evaluates to True
> will be the transition that is selected" — plus a shipped DSL (`when(age__gte=18)`, `expr('epochs>100')`,
> `default`, `~`) `[FW-10]`

> "| Conditional | `.branch([[cond, step]])` | Execute first step whose condition is true |" `[CE-7]`

Even the two systems that *reject* graphs implement the primitive, relocated:

> "Branches are ordinary `if` statements that return different event types." `[FW-12]`

The dissenting datapoint is **clu**, which hoists conditionality out of the graph entirely — and,
notably, is the system architecturally closest to yf:

> "This is the **generation / instantiation split**: any language emits the graph (loops,
> conditionals, computed fan-out — things a static template can't do); clu owns validation and atomic
> instantiation." `[CE-13]`

yf sits with clu: the only auto-evaluated predicate edge in either skill is the reconcile gate
`[YF-25]`; conditionality is otherwise paid at pour time by an LLM emitting `bd create` calls
`[YF-18]`.

### C5 — Edges should be deterministic code, not model calls (**Strong**)

Three independent practitioner sources, and the framework corpus corroborates by construction: every
conditional-edge implementation surveyed takes a *callable or predicate*, never a model call
(`[FW-2]`, `[FW-10]`, `[FW-15]`, `[CE-7]`).

> "A graph where every edge is another agent is paying tokens for its own wiring." `[PT-1]`

> "the edges are code" `[PT-8]`

> "defaulting to deterministic everywhere you can afford to" `[PT-7]`

This is the one prescription in the practitioner corpus that the shipped-framework corpus
independently validates. Note the credibility asymmetry: `[PT-1]` scores `questionable` (40, § 3),
but the claim does not rest on it — `[PT-7]` and `[PT-8]` carry it and the frameworks confirm it.

### C6 — Nothing has been measured (**Strong**, meta-finding)

All four clusters report the same absence by four different routes.

> "What is not established is the recipe. There is no controlled comparison of a drawn graph against
> a disciplined loop on the same task, measuring cost and quality together. What exists is field
> reports, a viral post, and a lot of people agreeing with each other quickly." `[PT-8]`

comparative-execution: "Tier A/B evidence is predominantly **first-party vendor documentation** —
authoritative for a system's own semantics, unreliable for comparison."

framework-evidence: "17 sources across 7 systems, all first-party documentation or generated API
reference" — zero outcome data by construction.

The corpus's shipped artifacts confirm rather than fill the hole: `[PT-9]` is seven days old with its
central mechanism deliberately disabled ("the calibration loop — the crown jewel of the whole graph —
is running in report-only mode"); `[PT-12]` says "I cannot say that this Skill would have prevented
the 16-hour UI failure"; `[PT-13]` "supplies only an outline without implementation or results".

**The single most consequential consequence:** the *only* measurement claim anywhere in the 89-source
corpus is yf's own —

> "the expensive branch (a `requires:` key plus a walk engine) was measured against the same corpus
> and found to buy nothing" `[YF-40]`

— and its corpus is five defects in one plan (`d3-pxe plan-013`), with no measurement artifact cited.
See § 2 X7 and § 4.

### C7 — Retry belongs at the leaf; per-node retry is rare (Moderate-strong)

> "Retrying an entire Workflow Execution is not recommended due to the deterministic nature of
> Workflow replay. ... Instead, retry failed Activities within the Workflow, which is Temporal's
> default behavior." `[CE-8]`

> "These compose in a fixed order: when a node attempt raises any exception ... the retry policy
> decides whether to retry. Only after retries are exhausted does the error handler run." `[FW-6]`

**A cross-cluster gap closure to record explicitly.** comparative-execution flagged a hole in its own
matrix: "`[uncertain]` — LangGraph does expose per-node retry policies, but no source retrieved in
this cluster states so; that cell is marked provisional rather than cited." Framework-evidence
retrieved exactly that source: `[FW-6]`, with defaults `max_attempts=3`, `initial_interval=0.5`,
`backoff_factor=2.0`, `jitter=True`. **The CE matrix cell can be upgraded from `[uncertain]` to
cited.** This is the one place triangulation *added* evidence rather than weighing it.

Framework-evidence's rarity census stands: per-node retry/timeout/error-handler policy "appears in
exactly one (LangGraph FW-6) — and even there it is gated at `langgraph>=1.2`, i.e. it arrived late."
Tier C has none — clu's nearest primitive runs the other direction ("Cascading cancel: `clu cancel`
walks the dep graph forward and cancels the whole tail" `[CE-13]`). yf has none: "No retry, no
backoff, no per-node failure policy" `[YF-29]`, `[YF-30]`.

### C8 — Store the edges, derive the readiness (Moderate)

The prescription has four supporting artifacts; the *failure mode* that motivates it has exactly
**one** (`[CE-6]`), so the strength is capped there.

> "The GraphFlow coordination mechanism is interrupted before it can enqueue the next agent, leaving
> the system in an inconsistent state: Remaining work exists, No agents are enqueued, The workflow
> appears 'complete' but is actually stuck." `[CE-6]`

Systems that recompute readiness from edges per query — `tk ready`, `clu ready`, `bd ready`
(`[CE-12]`, `[CE-13]`, `[YF-20]`/`[YF-22]`) — are structurally immune to that class. comparative-execution
names this "an existing yf strength worth naming as such"; the yf-codebase cluster independently
records server-side readiness computation as evidence *for* yf being a real graph. Two clusters
agreeing on yf's strength here is genuine cross-cluster agreement, but note the CE claim about yf is
inference from yf's `bd` backend, not a separate observation of yf.

### C9 — Move references, not payloads `[insufficient evidence]` for consensus

Two external sources, reaching the same rule from **different cost models** — which makes the
convergence interesting even though n=2 is under the bar.

> "Do not move giant transcripts between nodes. Move references to artifacts. A research node should
> store its report and return a path, ID, or structured summary." `[PT-1]` (token cost)

`[CE-10]` reaches it from database write size — "one database write per step ... plus two additional
database writes per workflow", with an explicit warning that step outputs drive write size and large
artifacts should be pointers, not payloads.

yf implements it (beads carry paths; artifacts live in `artifacts/`), which is a third *instance* but
a single-observer one, not a third independent source. **Recorded as convergent, not as consensus.**

### C10 — Fork / time travel `[insufficient evidence]` for consensus

Two systems, independently, both first-party vendor docs, one cluster: LangGraph "fork the graph
state at arbitrary checkpoints to explore alternative trajectories" `[FW-4]` and Burr
`fork_from_sequence_id` `[FW-11]`. Framework-evidence calls this "the best kind of evidence that the
primitive is load-bearing rather than fashionable". That reading is reasonable but **n=2 does not
clear the consensus bar**, and no source in either other web cluster mentions forking at all.

---

## 2. Contradictions

### X1 — Acyclicity: are agent graphs DAGs? (**Partially resolved; residual disagreement is real**)

Side A, the framework vendor:

> "First, agent graphs are usually **not DAGs**. Production agents need cycles: retrying failed tool
> calls, asking users for missing information, revising answers after validation... Looping is a core
> part of agentic systems, so they are likely not DAGs." `[PT-6]`

Side B, the corpus's only academic anchor:

> "We propose Graph Harness (Structured Graph Harness), which lifts the control structure from
> implicit context into an **explicit static DAG**." `[PT-13]`

**External evidence decides the general case for Side A.** Framework-evidence found cycle-with-exit-condition
in *every* graph-native system surveyed, including both systems that reject graphs: LangGraph
(conditional edge back to a node), pydantic-graph (node returns an earlier node), AutoGen ("Loops with
safe exit conditions" `[FW-9]`), Burr (transition back to a prior action), LlamaIndex (step returns an
earlier-handled event `[FW-12]`), DSPy (`max_iters` in `ReAct` `[FW-16]`). That is six independent
systems against `[PT-13]`'s proposal.

**But the residual disagreement is real and is tier-correlated** — an arrangement of the evidence the
retrievers did not make. The systems that ship cycles are all *in-process runtimes*. The systems that
keep the graph acyclic are all *tracker-as-store*:

> "the graph is static and acyclic; all conditional/computed structure happens in the *generator*"
> — clu `[CE-13]`

and yf is the same shape by construction — the one runtime loop-back is cut:

> "the refiner's actual wiring ... attaches the new retrieve to **package**, not back to
> triangulate/synthesize/critique. ... This is a **one-shot DAG extension, not a validation loop** —
> the graph stays acyclic by construction and the feedback edge is dropped." `[YF-12]`, YF a.3

So `[PT-6]` and `[PT-13]` are not simply right and wrong; they are describing different substrates.
`[PT-6]`'s claim holds for graphs executed in-process. `[PT-13]`'s static DAG is what a persisted,
resumable, human-auditable store actually produces — which is what yf is.

### X2 — Declared vs derived edges (**Live and unresolved**)

Framework-evidence names it precisely:

> "convergence on the *vocabulary* with active disagreement on whether the edges should be
> **declared** (LangGraph, ADK, AutoGen, Burr) or **derived** (pydantic-graph from type hints,
> LlamaIndex from event signatures)."

> "Other frameworks and LlamaIndex itself have attempted to solve this problem previously with
> directed acyclic graphs (DAGs) but these have a number of limitations that workflows do not: Logic
> like loops and branches needed to be encoded into the edges of graphs, which made them hard to read
> and understand." `[FW-12]`

Against, from the declare side:

> "Without type hints on the `path` function's return value ... or a path_map, the graph
> visualization assumes the edge could transition to any node in the graph." `[FW-2]`

Both sides ship, both sides validate structurally before running, and **the derived side still
materializes an edge set**:

> "The event types describe the edges of the workflow, and regular Python describes the logic inside
> each edge." `[FW-12]`

**Unresolved.** No evidence in the corpus adjudicates it; there is no measurement (C6).

### X3 — Direction of travel: toward graphs or away? (**Unresolved; genuinely bidirectional**)

Toward:

> "Starting in ADK 2.0 for Python and Go, template workflows have been superseded by more flexible
> workflow structures, including graph-based workflows and dynamic workflows." `[FW-18]`

> "**Enhance reliability:** Improve the predictability of your agents by relying on structured node
> definitions rather than prompts alone." `[FW-14]`

Away:

> "We built early deep research on predefined LangGraph workflows, then moved to a more agentic core
> loop. GPT Researcher... made the same move." `[PT-6]`

> "If Pydantic AI agents are a hammer, and multi-agent workflows are a sledgehammer, then graphs are
> a nail gun ... graphs are a powerful tool, but they're not the right tool for every job. Please
> consider other multi-agent approaches before proceeding." `[FW-8]`

Both directions are attested by first-party sources speaking **against their own interest** (a graph
library warning you off graphs; a graph vendor disclosing it abandoned graphs for its flagship use
case). That symmetry is why this stays unresolved rather than tipping. See § 2 X7 / thread 4.

### X4 — Is anything new? (**Three incompatible answers, all within one cluster**)

| Position | Source | Claim |
|:---------|:-------|:------|
| Nothing is new | `[PT-6]` | > "Graph engineering isn't a new idea. It's the latest name for a well established approach to building reliable agents." |
| The **authoring step** is new | `[PT-8]` | > "You do not write the graph in a framework's DSL. You draw it, badly, in whatever tool is nearest, and hand the drawing to a coding agent that turns it into a running script. The drawing is the spec." |
| A genuine phase change | `[PT-7]` | > "Models got good enough that the constraint moved from 'can it do a step' to 'can the system coordinate a thousand steps,' and coordinating a thousand steps is a graph problem." |

Framework-evidence adds a datapoint that constrains but does not settle it: a converged core of four
primitives exists across 8 systems, which "is strong evidence that at least the topology vocabulary
is not post-hoc labeling" — supporting `[PT-6]`'s "well established approach" against a pure-hype
reading, while saying nothing about whether the *authoring* claim in `[PT-8]` is new.
`[PT-8]`'s authoring claim is **uncorroborated by any other source in the 89-source corpus** and no
framework in the corpus documents a drawing-to-graph compiler.

### X5 — Scope fork: are knowledge graphs part of "graph engineering"? (**Uncorroborated**)

`[PT-11]` defines the term as having "two halves" — knowledge graphs (entities, facts, ontology,
fusion) *and* task graphs. **No evidence found** for this scope anywhere else: zero knowledge-graph
material appears in framework-evidence (18 sources), comparative-execution (15 sources), or the
practitioner corpus's other 12 sources. A definitional fork asserted by exactly one `questionable`-tier
project README against 88 other sources.

### X6 — yf internal: is INVESTIGATE parallel or serialized? (**Unresolved, single observer**)

> "Spawn a sub-agent per unknown ... **Independent experiments run in parallel.**" `[YF-5]`

> "After each sub-agent returns: 1. Write finding ... 2. Update plan.md ... 3. **Both writes BEFORE
> next sub-agent spawns**" `[YF-35]`

Same phase, same file. The cluster marks it `[uncertain]` "which one an executing agent actually
honours; the repo carries no test that asserts either." No external cluster bears on it. **Stays
open**; it is a specification defect, not an evidentiary conflict.

### X7 — yf internal: the DAG-walk rejection vs. its own counter-evidence (**Partially resolved against the rejection — see thread 4**)

The rejection:

> "This is deliberately the prose check, **not a topological DAG walk**: the expensive branch (a
> `requires:` key plus a walk engine) was measured against the same corpus and found to buy nothing,
> and 2 of the 5 defects are not reachability failures a graph walk would find at all." `[YF-40]`

The counter-evidence, from the adjacent requirement in the same file:

> "in d3-pxe plan-013 a capability gate whose condition required a preview of the output of the very
> issue it blocked survived conformance and **two** red-team cycles, because every pass checked that
> the gate declared a type, approvers, a condition, and a test — none checked whether the condition
> could ever become true." `[YF-42]`

Direct verification of the source file (`skills/yf-plan/spec/agents.md:71-77`) adds a fact the
cluster artifact did not surface: `REQ-AGENT-046`'s rationale also records that **"The same cycle was
independently reproduced in this skill's own plan-039 draft."** So the defect class recurred after
the corrective was written, and the corrective is itself a prose contract of the same kind that
already failed twice.

Full triangulation in § 5 thread 4.

### X8 — The two Anthropic statistics (**Not adjudicated — quarantined, § 4**)

`[PT-2]` vs `[PT-3]` contradict each other. Both are unsourced. Triangulation does **not** pick a
side; it removes both from the evidence base.

---

## 3. Credibility scoring

Scored with `credibility_scorer.py batch` (domain authority 35%, currency 20%, expertise 25%, bias
neutrality 20%). Scoring inputs are recorded so the numbers are reproducible and contestable.

### Scoring assumptions (disclosed, because they materially move the numbers)

1. **Living docs dated to retrieval.** Vendor documentation pages carry no publication date;
   framework-evidence states "Treat the whole cluster as 'as of 2026-08-16.'" I set
   `published_date = 2026-08-16` for those, giving them currency 95. This is defensible (living docs
   reflect the shipped version) but **inflates every vendor-doc score by up to ~9 points** relative to
   an unknown-date default of 50.
2. **Domain authority is a URL-shape heuristic and produces two visible inversions**, flagged rather
   than hand-corrected:
   - `docs.*` hosts and `.dev` TLDs get a Tier-2 bump (77). Vendor docs on `github.io` or
     `burr.apache.org` fall to the unknown-domain floor (30). This is why `[FW-9]` (AutoGen),
     `[FW-10]`/`[FW-11]` (Burr) and `[FW-14]`/`[FW-15]` (ADK) score 64–68 while `[FW-13]` (CrewAI, on
     `docs.crewai.com`) scores 80 — **despite framework-evidence marking most CrewAI claims
     `[uncertain]` and never fetching the source**. Read `[FW-13]`'s 80 as an artifact of its
     hostname, not its evidentiary quality.
   - `arxiv.org` is a Tier-1 domain (92), which lifts `[PT-13]` to 76 despite an independent referee
     note recording it "supplies only an outline without implementation or results", zero citations,
     and an unaffiliated single author. **Manual adjustment applied below.**
3. **yf-codebase sources were not machine-scored.** Their `url` fields are repo-relative `path:line`
   references and `bd:<command>` outputs, which the URL-based scorer cannot parse. They are scored as
   a class, § 3.3.

### 3.1 — Web sources, machine-scored

| id | Source | Domain auth. | Currency | Expertise | Bias | **Overall** | Category |
|:---|:-------|--:|--:|--:|--:|--:|:--|
| FW-8 | pydantic-graph docs | 77 | 95 | 92 | 92 | **87** | high_trust |
| FW-5 | LangGraph interrupts | 77 | 95 | 92 | 75 | **84** | high_trust |
| FW-6 | LangGraph fault tolerance | 77 | 95 | 92 | 75 | **84** | high_trust |
| CE-1 / FW-1 | LangGraph Graph API | 77 | 95 | 92 | 55 | **80** | high_trust |
| CE-2 / FW-4 | LangGraph checkpointers | 77 | 95 | 92 | 55 | **80** | high_trust |
| CE-8 | Temporal retry policies | 77 | 95 | 92 | 55 | **80** | high_trust |
| CE-9 | Temporal continue-as-new | 77 | 95 | 92 | 55 | **80** | high_trust |
| CE-10 | DBOS architecture | 77 | 95 | 92 | 55 | **80** | high_trust |
| CE-11 | Restate first-principles | 77 | 95 | 92 | 55 | **80** | high_trust |
| FW-7 | LangGraph persistence | 77 | 95 | 92 | 55 | **80** | high_trust |
| FW-13 | CrewAI Flows | 77 | 95 | 92 | 55 | **80** | high_trust `[see 3.2]` |
| CE-3 | LangGraph HITL (mirror) | 30 | 95 | 92 | 75 | **68** | verify |
| CE-5 / FW-9 | AutoGen GraphFlow | 30 | 95 | 92 | 75 | **68** | verify |
| FW-2 | LangGraph add_conditional_edges | 30 | 95 | 92 | 75 | **68** | verify |
| FW-3 | LangGraph Send | 30 | 95 | 92 | 75 | **68** | verify |
| FW-10 | Burr transitions | 30 | 95 | 92 | 75 | **68** | verify |
| FW-11 | Burr state persistence | 30 | 95 | 92 | 75 | **68** | verify |
| FW-16 | DSPy composing modules | 30 | 95 | 92 | 75 | **68** | verify |
| FW-17 | DSPy Module API | 30 | 95 | 92 | 75 | **68** | verify |
| CE-6 | AutoGen issue #7043 | 30 | 80 | 75 | 92 | **67** | verify |
| PT-8 | Pandey, epistemic audit | 30 | 95 | 75 | 92 | **67** | verify |
| PT-12 | Hyuk Min, Codex Gate field test | 30 | 95 | 75 | 92 | **67** | verify |
| FW-12 | LlamaIndex Workflows | 30 | 95 | 92 | 55 | **64** | verify |
| FW-14 | ADK graph workflows | 30 | 95 | 92 | 55 | **64** | verify |
| FW-15 | ADK graph routes | 30 | 95 | 92 | 55 | **64** | verify |
| FW-18 | ADK deprecation notice | 30 | 95 | 92 | 55 | **64** | verify |
| PT-5 | Perez, loop→graph essay | 47 | 95 | 75 | 55 | **64** | verify |
| PT-6 | LangChain, 3 Years of Graph Eng. | 30 | 95 | 92 | 55 | **64** | verify |
| PT-7 | Simmons, Graph Engineering Phase | 30 | 95 | 75 | 75 | **63** | verify |
| PT-9 | Chris Lema, production write-up | 30 | 95 | 75 | 75 | **63** | verify |
| CE-7 | Mastra control flow (DeepWiki) | 30 | 95 | 55 | 75 | **58** | questionable |
| CE-12 | ticks (`tk`) landing page | 30 | 95 | 75 | 35 | **55** | questionable |
| CE-13 | clu README | 30 | 95 | 75 | 35 | **55** | questionable |
| CE-14 | task-orchestrator README | 30 | 95 | 75 | 35 | **55** | questionable |
| CE-15 | yolo-runner README | 30 | 95 | 75 | 35 | **55** | questionable |
| PT-11 | codejunkie99 skill repo | 30 | 95 | 75 | 35 | **55** | questionable |
| CE-4 | dreaming.press `defer` analysis | 30 | 95 | 55 | 55 | **54** | questionable |
| PT-10 | AI Builder Club | 30 | 95 | 55 | 55 | **54** | questionable |
| PT-1 | `@0xwhrrari` X Article | 30 | 95 | 15 | 35 | **40** | questionable |
| PT-4 | `@steipete` origin post (not retrieved) | 30 | 50 | 15 | 60 | **36** | avoid |
| PT-2 | `@reiraxbt` video card | 30 | 95 | 10 | 12 | **34** | avoid |
| PT-3 | `@norvex1029` video card | 30 | 95 | 10 | 12 | **34** | avoid |

### 3.2 — Manual adjustments and overrides

| id | Machine | **Adjusted** | Reason |
|:---|--:|--:|:-------|
| PT-13 | 76 (verify) | **52 (questionable)** | `arxiv.org` Tier-1 domain authority (92) treats an un-peer-reviewed preprint as a journal. Independent referee note: "supplies only an outline without implementation or results." Zero citations, h-index-1 unaffiliated single author. Cite for its *framing* (the degeneration diagnosis), never for a result. |
| FW-13 | 80 (high_trust) | **64 (verify)** | Hostname artifact (§ 3 note 2). Framework-evidence marks `@router`, `and_`, `or_`, `@persist` all `[uncertain]`; source file and PR body were never fetched. |
| CE-4 | 54 | **54, but load-bearing** | LLM-authored blog with a human editor. Its *API facts* are corroborated by `[CE-1]`/`[CE-2]`; its *framing* ("`defer=True` is not a dependency resolver") is not independently confirmed. Use the framing as hypothesis, not fact. |
| CE-6 | 67 | **75 (verify, upper)** | Under-scored by the `github.com` unknown-domain floor. This is a reproducible bug report against the vendor's own product with linked fix PRs — evidence *against* interest, and the single most independent artifact in comparative-execution. |
| PT-1 | 40 | **40, quote-only** | 1.48M views but pseudonymous, ships nothing, terminates in subscription CTAs. Its formulations (the dependency test) are useful *as formulations*; it establishes no fact. |

### 3.3 — yf-codebase sources, scored as a class

43 sources, all `method: direct` — repo reads at `path:line` plus live `bd ... --json` output.

| Axis | Assessment |
|:-----|:-----------|
| Verifiability | **Highest in the corpus.** Every citation resolves to a line in a committed file at a named commit (`efd2317`), or to a reproducible `bd` command. |
| Independence | **Lowest in the corpus.** Single observer, single pass, no second reader. No `YF-*` claim is corroborated by any other cluster. |
| Bias | The cluster is auditing its own repository. Its verdict is *unfavourable* to the repo ("not an executable graph program"), which is evidence against motivated reasoning. |
| Effective category | `high_trust` **for existence and absence-in-repo claims** (a `grep` is checkable); `verify` **for interpretive claims** (e.g. "the degeneration point is precisely one file per skill"). |

**One `[uncited]` item inside the cluster** must not propagate: the d10 dispatch-time override text
is "the prompt of this agent, not a repo file." It is the retriever's own dispatch prompt, so it is
unverifiable from the repo. Treat the *hazard* (4 writers, one file, no merge semantics) as cited via
`[YF-36]`, and the *evidence that it was patched by hand* as uncited.

### 3.4 — Aggregate credibility skew

| Cluster | Sources | Median score | Dominant type | Weight this evidence for | Weight it against |
|:--------|--:|--:|:--------------|:----------------------------|:------------------|
| framework-evidence | 18 | 68 | First-party vendor docs | Each system's **own** semantics | **Cross-system comparison** |
| comparative-execution | 15 | 67 | Vendor docs + 4 project READMEs + 1 landing page | Tier A/B semantics; the `[CE-6]` negative finding | Tier C capability claims (self-descriptions of small unproven projects) |
| practitioner-trend | 13 | 55 | Blogs, X posts, 1 preprint | **Framings and diagnostics** | **Any factual or numeric claim** |
| yf-codebase | 43 | — (class) | Direct repo reads | Existence / absence in this repo | Generalization beyond this repo |

---

## 4. Quarantined and unsourced claims

These must **not** propagate into any consensus finding, synthesis conclusion, or recommendation.

| Claim | Source | Status | Reason |
|:------|:-------|:-------|:-------|
| "99% of our engineers run swarms of 300+ self-improving agents" (attrib. Anthropic Research Lead) | `[PT-2]` | **QUARANTINED — unsourced** | Speaker unnamed; claim lives in an untranscribed MP4; account has 881 followers / 8 media items; no Anthropic primary source carries it; **directly contradicted by `[PT-3]`** |
| "90% of our engineers were using self-improving loops. Now everyone has shifted to building agentic Graphs." / "No more prompting." (attrib. Anthropic engineer) | `[PT-3]` | **QUARANTINED — unsourced** | Speaker unnamed; claim lives in an untranscribed MP4; account created 2026-07-21, three weeks before posting; **directly contradicted by `[PT-2]`** |
| "That multi-agent graph burned roughly **15x** the tokens of a normal chat turn" | `[PT-10]`, relaying Anthropic | **QUARANTINED — second-hand, unverified** | practitioner-trend marks it `[uncertain]`: "not verified against Anthropic's primary post within this cluster" |
| "**90.2%** over a single-agent Claude Opus 4 baseline" | `[PT-10]`, relaying Anthropic | **QUARANTINED — second-hand, unverified** | Same as above |
| Peter Steinberger's nine-word post as the origin of the term | `[PT-4]` | **QUARANTINED — attribution unverified** | Status URL never located; text quoted only by a third party; the embedded tweet did not render in the `[PT-6]` crawl, so "it is not confirmed that LangChain and Perez refer to the same post" |
| `[PT-7]`'s characterization of arXiv 2601.12560 as documenting "graph orchestration and flow engineering as an identified industry shift" | `[PT-7]` | **QUARANTINED — misattributed** | Verifies as a real paper but is a general agentic-AI taxonomy survey |
| CrewAI `@router`, `and_`, `or_`, `@persist` | `[FW-13]` | **PROVISIONAL** | Attested only by a module docstring and a PR *title* surfaced in search; bodies never fetched |
| AutoGen cycle-detection enforcement (issues #6628, #6551) | framework-evidence | **PROVISIONAL** | "These are titles only; I did not fetch issue bodies" |
| LangGraph per-node retry policy | — | **UPGRADED to cited** | Was `[uncertain]` in comparative-execution; `[FW-6]` supplies the first-party citation (§ 1 C7) |
| The d10 hand-patch of the `sources.json` write hazard | yf-codebase d10 | **`[uncited]`** | Retriever's own dispatch prompt, not a repo artifact |

**Note on scale.** Four of the ten quarantined items are *numeric* claims, and after quarantine the
corpus contains **no verified outcome number of any kind** about graph-vs-loop performance. This is
the same hole C6 names from the other direction.

---

## 5. The five commissioned threads — resolution status

| # | Thread | Status |
|:--|:-------|:-------|
| 1 | Checkpoint-granularity independence | **Resolved** |
| 2 | Consensus definition of "graph engineering" | **Resolved** (the two clusters were measuring different objects) |
| 3 | Declared-vs-derived edges vs. the DAG contradiction | **Resolved** (two orthogonal disagreements; one settles, one stays open) |
| 4 | The premise challenge / `REQ-AGENT-047` | **Split** — resolved against the rejection on one axis, unresolved on the other |
| 5 | Unsourced Anthropic statistics | **Resolved** (quarantined, § 4) |

### Thread 1 — Are the two checkpoint findings independent? **Partially. Disclosed.**

`[CE-2]` and `[FW-4]` are **the same URL** and the two clusters quote the same sentences (§ 0). The
LangGraph leg is therefore one artifact, not two. After removing it, four independent legs remain —
Burr `[FW-11]`, DBOS `[CE-10]`, AutoGen `[CE-6]`, Tier C `[CE-12]`/`[CE-13]`/`[CE-14]` — so the claim
clears the consensus bar on its own. The *convergent wording* of the two retrievers' conclusions is
not additional evidence. Full accounting: § 1 C3.

### Thread 2 — Do the practitioner and framework corpora agree on the primitive set? **They are naming different things, and both are correct.**

They measure different objects:

| | practitioner-trend | framework-evidence |
|:--|:-------------------|:-------------------|
| Population | 9 prose sources *describing a practice* | 8 systems' *shipped API surfaces* |
| Question answered | Is there a shared **definition**? | Is there a shared **implementation**? |
| Answer | No. "No two sources name the same set." | Yes, but small: typed node, declared edge, conditional edge, run-scoped state |

Overlap on the trio is real and independent: `[PT-6]`, `[PT-7]`, `[PT-8]`, `[PT-1]`, `[PT-12]`,
`[PT-13]` converge on **node / edge / state**, and `[FW-1]` states the identical trio —

> "You define the behavior of your agents using three key components: 1. `State` ... 2. `Nodes` ...
> 3. `Edges` ... In short: *nodes do the work, edges tell what to do next*." `[FW-1]`

**Two caveats that weaken the apparent agreement.**

1. **The trio's cross-cluster agreement is partly a single vendor talking to itself.** `[PT-6]` is
   LangChain's blog; `[FW-1]`…`[FW-7]` are LangChain's docs (§ 0). The independent practitioner legs
   are `[PT-7]`, `[PT-8]`, `[PT-12]`, `[PT-13]`; the independent framework legs are `[FW-8]`,
   `[FW-10]`, `[FW-12]`, `[FW-15]`. Both sets are ≥3, so the finding survives — but not at the
   apparent strength.
2. **The framework corpus's fourth primitive is only weakly present in the practitioner corpus.**
   Conditional-edge/router is universal in shipped code (§ 1 C4) but the practitioner corpus names
   it inconsistently: `[PT-1]` calls it a "router" *shape*, `[PT-6]` a "deterministic or conditional
   transition", `[PT-7]` "a decision — a typed transition", and `[PT-8]`, `[PT-11]`, `[PT-13]` do not
   distinguish it from an ordinary edge. **The practitioner corpus does not independently converge
   on the fourth primitive.**

**Not a contradiction.** A converged *implementation* vocabulary and an absent *discursive* definition
are compatible states of the world, and the framework evidence is the stronger of the two because API
surfaces are mechanically checkable while prose definitions are not.

### Thread 3 — Is the declared/derived split the same disagreement as the DAG contradiction? **No — two orthogonal disagreements.**

They cross-cut cleanly, which the systems themselves demonstrate:

| System | Edges | Cycles? | Evidence |
|:-------|:------|:--------|:---------|
| LangGraph | declared | yes | `[FW-1]`, `[FW-2]` |
| Google ADK | declared | not established | `[FW-14]`, `[FW-15]` |
| AutoGen GraphFlow | declared | yes ("Loops with safe exit conditions") | `[FW-9]` |
| Burr | declared | yes (transition back to a prior action) | `[FW-10]` |
| pydantic-graph | **derived** (type hints) | yes (node returns an earlier node) | `[FW-8]` |
| LlamaIndex Workflows | **derived** (event signatures) | yes (step returns an earlier-handled event) | `[FW-12]` |
| clu | declared | **no** (static + acyclic by design) | `[CE-13]` |
| yf | declared | **no** (feedback edge dropped) | `[YF-12]` |

Both derived-edge systems support cycles; both acyclic systems declare their edges. The axes are
independent.

**Axis B (acyclicity) is largely settled by the framework evidence**, against `[PT-13]`: six
independent systems ship cycle-with-exit-condition. **Axis A (declared vs derived) is not settled**
and no evidence in the corpus adjudicates it (§ 2 X2).

**The genuinely new triangulated finding:** the acyclicity split is *substrate*-correlated, not a
disagreement about agent graphs in general. In-process runtimes cycle; store-backed graphs stay
acyclic and hoist conditionality to generation time (`[CE-13]`'s "generation / instantiation split").
`[PT-6]`'s "agent graphs are usually not DAGs" is a claim about in-process runtimes; yf and clu are
not counter-examples to it, they are a different substrate.

### Thread 4 — Is the `REQ-AGENT-047` rejection vindicated or contradicted? **Split, because the requirement conflates two different things.**

`REQ-AGENT-047` rejects "a `requires:` key plus a walk engine" `[YF-40]`. The external evidence about
moving off graphs is about a **runtime executor**. These are different artifacts, and the evidence
lands differently on each.

**Axis 1 — rejecting a runtime graph *executor*: partially vindicated, but the external evidence is
bidirectional (§ 2 X3), so "vindicated" is too strong.**

Supporting the rejection: `[PT-6]` (LangChain moved deep research off graphs to an agentic core
loop, and reports GPT Researcher did the same); `[FW-8]` (a graph library opening its own docs with
"please consider other multi-agent approaches before proceeding"); `[FW-12]` (LlamaIndex removed DAGs
and stated why). Against it: `[FW-14]`/`[FW-18]` (ADK 2.0 superseded template workflows *with*
graphs, citing prompt-length reliability failure) and `[FW-9]` (AutoGen added GraphFlow on top of
unstructured group chat). **Verdict: the field is moving in both directions; yf's choice is defensible
and unremarkable, not vindicated.**

There is also a scope mismatch worth stating: `[PT-6]`'s move-off-graphs case is *generic deep
research* — "hard to pin down ahead of time". That is `[PT-8]`'s sketch test:

> "If you can sketch the whole thing on paper before executing anything, you have a graph ... If
> drawing it requires knowing what step three returns, you have a loop." `[PT-8]`

yf-research's pipeline **is** sketchable in advance — the formula is a fixed 7-step chain `[YF-4]`
with one fan-out bulge `[YF-20]`. By `[PT-8]`'s own test yf-research is on the graph side of the line,
so `[PT-6]`'s abandonment of graphs for *open-ended* research does not transfer to it.

**Axis 2 — rejecting a *pre-run structural validator*: contradicted, on three independent legs plus
yf's own record.**

Three independent systems ship exactly the class of check `REQ-AGENT-047` declined:

> "Compiling ... provides a few basic checks on the structure of your graph (no orphaned nodes, etc).
> ... You **MUST** compile your graph before you can use it." `[FW-1]`

> "Before a workflow runs, Workflows validates the event graph described by your step signatures. It
> checks that start and stop events are present, produced events have consumers, consumed events have
> producers" `[FW-12]`

> `Cycle detected without exit condition: generator -> reviewer -> generator` — AutoGen issue title,
> framework-evidence `[uncertain]` (title only)

Two of those three are `verify`-tier first-party docs quoting a shipped API; the third is provisional.
Note especially that **LlamaIndex — the system that most emphatically rejected DAGs — still ships a
structural pre-run validator.** Rejecting the graph as an executor and rejecting it as a validator are
independent decisions everywhere else in the corpus.

And yf's own record is counter-evidence on this axis:

- The defect that motivated `REQ-AGENT-046` is a **cycle in the gate/dependency graph** — precisely
  what `[FW-1]`/`[FW-12]`-class validation catches structurally — and it "survived conformance and
  **two** red-team cycles" `[YF-42]`.
- Direct verification of `skills/yf-plan/spec/agents.md:72` adds that **"The same cycle was
  independently reproduced in this skill's own plan-039 draft"** — the defect class recurred *after*
  the prose corrective was specified.
- The corrective (`REQ-AGENT-046`) is another prose contract of the same kind that already failed
  twice, and its Verification clause is a documentation check ("red-team.md Evaluate → Gates carries a
  'Gate reachability' item"), not a behavioural one.

**The measurement claim underneath the rejection is the weakest link.** `[YF-40]` says the walk engine
"was measured against the same corpus and found to buy nothing". Per C6 and § 4, this is the only
measurement claim in the entire 89-source corpus, its corpus is **five defects in one plan**
(`d3-pxe plan-013`), no measurement artifact is cited, and the requirement's own hedge — "2 of the 5
defects are not reachability failures a graph walk would find at all" — concedes that up to 3 of 5
are. `[uncertain]` — no artifact in this research corpus verifies the measurement.

**Net:** the rejection of a DAG-walk *executor* is neither vindicated nor contradicted (X3 is
unresolved). The rejection of a DAG-walk *validator* is contradicted by three independent shipped
systems and by yf's own recurring defect. Triangulation does not recommend a remedy — that is the
synthesizer's job — but it records that the two decisions are separable and were decided together.

### Thread 5 — Unsourced claims. **Quarantined, § 4.**

Both Anthropic-attributed statistics are removed from the evidence base. They appear in no consensus
finding above. Three further claims were quarantined on the same standard (`[PT-10]`'s two relayed
Anthropic numbers, `[PT-4]`'s origin attribution) plus a misattribution in `[PT-7]`.

---

## 6. Evidence gaps

Absences carried forward. Each is "not established by this corpus", not "does not exist".

### 6.1 — Gaps that block a conclusion

| Gap | Consequence |
|:----|:------------|
| **No controlled comparison of graph vs. loop on the same task, measuring cost and quality** `[PT-8]` | Every topology recommendation in the eventual synthesis is an argument from design, not from outcome. Must be stated as such. |
| **No independent verification of yf's own measurement claim** `[YF-40]` | The single load-bearing justification for `REQ-AGENT-047` cannot be checked from this corpus. |
| **No second observer on any `YF-*` claim** | 43 of 89 sources are single-pass, single-observer. Interpretive `YF` claims are `verify`-tier at best (§ 3.3). |
| **Two video seeds untranscribed** `[PT-2]`, `[PT-3]` | Their substantive content is permanently unavailable to this corpus. |

### 6.2 — Capability cells no cluster filled

Cross-checking the two matrices, these remain empty in **both** clusters — genuine corpus-wide gaps,
not cluster-local ones:

| System | Missing capability | Both clusters agree it is unretrieved |
|:-------|:-------------------|:--------------------------------------|
| AutoGen GraphFlow | checkpoint / resume; HITL | comparative-execution "no evidence gathered"; framework-evidence "**No evidence found** on whether GraphFlow can checkpoint or resume" |
| Google ADK | checkpoint / resume | Not covered by comparative-execution at all; framework-evidence "**No evidence found**" |
| Temporal | fan-out / join; HITL surfaces | comparative-execution "not crawled"; not covered by framework-evidence |
| Burr | HITL; fan-out | framework-evidence `[uncertain]` / em-dash; not covered by comparative-execution |
| pydantic-graph | fan-out / parallelism | framework-evidence "**Not verified**"; not covered by comparative-execution |
| Tier C (all four) | conditional branch; loop / retry | comparative-execution "**No evidence found**...This looks like a real tier-wide boundary but is not proven"; not covered by framework-evidence |
| LangGraph | `recursion_limit` / loop budget; subgraph API; node caching / `defer` | framework-evidence "**No evidence found**"; `defer` covered only by the `questionable`-tier `[CE-4]` |

**The Tier C row is the most consequential**, because it is the tier yf is in. "Tracker-as-store
systems have no in-graph conditionals or retry" is a plausible tier-wide boundary supported by one
explicit statement (`[CE-13]`) and three silences (`[CE-12]`, `[CE-14]`, `[CE-15]`). Silence in a
README is weak evidence of absence. **Do not assert the boundary as established.**

### 6.3 — Deliberately not searched

Recorded so the synthesis does not mistake exclusion for absence:

- Airflow / Dagster / Pegasus and the scientific workflow-DAG lineage — excluded by `plan.yaml` in
  **both** external clusters. Since that lineage is where topological execution, backfill, and
  mid-run recovery were solved decades ago, **the corpus is structurally blind to the most mature
  prior art on its central question.** This is the single largest scope hole.
- Prefect, Inngest, CrewAI Flows (beyond `[FW-13]`), OpenAI Agents SDK.
- Conference talks on "graph engineering" — searched, **none found**; `[PT-7]` corroborates
  ("Nobody held a keynote for it"). Expected given the label was ~4 weeks old at retrieval.
- Purely-on-X discourse — exa returned `SOURCE_NOT_AVAILABLE` for all three X seeds, so the citation
  network was reconstructed from *blogs citing X*, biasing the corpus toward long-form practitioners.

### 6.4 — Questions this triangulation opened but cannot close

1. **Is the substrate correlation in X1/C2 real or coincidental?** Four systems is a small sample, and
   yf and clu may share an ancestor rather than have converged. `[uncertain]`
2. **Does `REQ-AGENT-046`'s prose reachability check actually fire?** Its Verification clause checks
   that documentation contains an item, not that a defect is caught `[YF-43]`. No test exists.
3. **Which of `[YF-5]` and `[YF-35]` does an executing agent honour?** (§ 2 X6.) No test exists.
4. **Does `[PT-8]`'s "authoring step is new" claim have any corroboration at all?** Nothing in 89
   sources documents a drawing-to-graph compiler. Currently a single-source claim.

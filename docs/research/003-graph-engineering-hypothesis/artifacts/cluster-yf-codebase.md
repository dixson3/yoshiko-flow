---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: yf-codebase (direct retrieval)

Bead: `yf-mol-62k.3` · method: `direct` (this repository, no web search) · retrieved 2026-08-16
· repo `dixson3/yoshiko-flow` @ `efd2317` (branch `main`).

Every citation `[YF-n]` resolves to an entry in `sources-yf-codebase.json`, whose `url` is a
repo-relative `path:line`. Live `bd` command output is cited as `bd:<command>` with the
verbatim output quoted.

## Summary of the answer

yoshiko-flow **does** construct a real dependency graph and store it in a real graph store
(beads/Dolt). It does **not** execute that graph as a graph. Every emitted artifact is
graph-shaped *data* (a `depends-on` DAG in `plan.md`, a `[[steps]]` chain in a
`.formula.toml`, a bead DAG in Dolt) and every consumer of that data is a **sequential
single-claim ready-poll loop**. The one topological algorithm in the codebase
(`close_cascade.py`) walks the *containment tree*, not the dependency DAG, and runs only at
teardown.

---

## (a) Where CONSTRUCTION fans out or loops

### a.1 — Both skills' construction phases live OUTSIDE the graph entirely

`yf-plan`'s SCOPE → INVESTIGATE → PLAN → review cycle produces **zero durable beads**. The
molecule is not poured until EXECUTE:

> "PLAN-approval and EXECUTE are separated by a session boundary. Under the
> **intake-at-execute** model the molecule is **not** poured during INTAKE ... The
> `bd mol pour` and its human start gate are created at **EXECUTE start**" [YF-1]

So the entire construction program — including its loops — is executed by an LLM in a
conversation, with no graph representation. Evidence from a completed bundle: plan-033 ran
**five** red-team cycles [YF-2]:

> "- review: red-team pass-5 APPROVE — pass-4 F1–F7 resolved ...
> - review: red-team pass-4 REVISE — multi-harness re-scope ...
> - review: red-team pass-3 APPROVE ...
> - review: red-team pass-2 APPROVE — pass-1 concerns C1–C5 resolved" [YF-2]

None of those five iterations is a bead. The plan's poured epic `yf-mol-y7f` contains 40
issues, all of them *execution* issues (bd:graph, [YF-3]).

`yf-research` is the same: the first bead is the human `gate`; SCOPE and PLAN happen before
the pour [YF-4].

### a.2 — The two genuine fan-out points

**yf-plan INVESTIGATE** is the only place the skill dispatches N agents at once:

> "Spawn a sub-agent per unknown using `Agent` with `isolation="worktree"`,
> `mode="bypassPermissions"`. ... **Independent experiments run in parallel.**" [YF-5]

Its graph representation is *deliberately disposable* — a `vapor`-phase wisp that is burned:

> `phase = "vapor"` ... "Steps are injected dynamically -- one per experiment identified
> during the scoping phase." ... "4. Burn: `bd mol burn <id>` after findings captured" [YF-6]

and burned at intake with output discarded: `bd mol burn ${INVESTIGATION_WISP_ID} --force
2>/dev/null || true` [YF-7]. So the fan-out's graph is created and destroyed without ever
being walked.

**yf-research RETRIEVE** fans out one bead per source cluster, in a shell `for` loop written
as prose in `SKILL.md` and executed by the model:

```bash
RETRIEVE_IDS=()
for cluster in ${clusters}; do
  RID=$(bd create "Retrieve: ${cluster_name}" ... --parent ${EPIC} --deps "${TOOLING_ID}" \
    --metadata "$META" --silent)
```
[YF-8]

with an explicit **join** wired afterwards through a single batched transaction:

```bash
DEP_OPS=""
for rid in "${RETRIEVE_IDS[@]}"; do
  DEP_OPS+="dep add ${TRIANG_ID} ${rid}\n"
done
[ -n "$DEP_OPS" ] && printf '%b' "$DEP_OPS" | bd batch -m "yf-research ${EPIC} retrieve wiring"
```
[YF-9]

Spec'd as REQ-PHASE-003 / REQ-PHASE-004 [YF-10].

### a.3 — The one runtime loop-back (and why it is not a cycle)

`REFINE` may extend the DAG at runtime:

> "REQ-PHASE-005: REFINE may extend the DAG at runtime by spawning new RETRIEVE beads via
> `--deps discovered-from:<refine-id>` when the red-team identifies gaps." [YF-11]

The refiner's actual wiring, however, attaches the new retrieve to **package**, not back to
triangulate/synthesize/critique:

```bash
NEW_RID=$(bd create "Retrieve: <gap topic>" --deps "discovered-from:${REFINE_BEAD_ID}" \
  --parent ${EPIC} --metadata "$META" --silent)
bd dep add ${PACKAGE_BEAD_ID} ${NEW_RID}
```
[YF-12]

So evidence retrieved by the gap-fill is never re-triangulated and never re-critiqued. This
is a **one-shot DAG extension, not a validation loop** — the graph stays acyclic by
construction and the feedback edge is dropped. **[uncertain]** whether this is intentional;
neither `spec/phases.md` nor `refiner.md` states a rationale for wiring to package.

### a.4 — Construction is prose, not code (absence finding)

`plan_manager.py` is 3525 lines [YF-13] and contains **no** `bd create`, **no** `bd dep add`,
and **no** `bd mol pour`. Its only `bd` subprocess calls are `bd show`, `bd list`, and
`bd update --external-ref` [YF-14]. `research_manager.py` is 164 lines with exactly two
verbs, `json-get` and `record-epic` [YF-15] — SKILL.md says so explicitly:

> "`research_manager.py` is intentionally narrow — a defensive `json-get`." [YF-16]

Searched: `grep -n "def " skills/yf-*/scripts/*manager.py`, `grep -n 'depends-on|## Epics'
skills/yf-plan/scripts/plan_manager.py` (only hits are a seed template string and prose
comments) [YF-17]. **Absence confirmed: no graph builder, no edge-list model, no topological
sort, no cycle detector exists in either manager script.** The `plan.md` → bead-DAG
translation is an LLM reading markdown and emitting `bd create` calls per SKILL.md §5.2a
[YF-18].

---

## (b) The actual shape of the emitted bead graph

### b.1 — The formula skeletons are chains

`yf-research.formula.toml` is a strict linear `needs` chain of 7 steps:

> `gate` → `tooling` (`needs = ["gate"]`) → `triangulate` (`needs = ["tooling"]`) →
> `synthesize` (`needs = ["triangulate"]`) → `critique` (`needs = ["synthesize"]`) →
> `refine` (`needs = ["critique"]`) → `package` (`needs = ["refine"]`) [YF-4]

Every `needs` array has exactly one element. There is no fan-out, no join, no conditional,
no retry and no loop construct in the formula language as used here.

`plan-execute.formula.toml` is even thinner — **one** step, the start gate:

> "# Execution steps (epics, issues, capability gates) are injected
> # dynamically from plan.md during Phase 4 intake." [YF-19]

So yf-plan's formula contributes exactly one node; 100% of the plan DAG is dynamically
injected by the model.

### b.2 — Measured shape of four real epics

Live `bd graph <epic> --json`, layer widths from `layout.Layers` [YF-20]:

| Epic | Bundle | Nodes | Blocking edges | Layers | Layer widths | Max width |
| :-- | :-- | --: | --: | --: | :-- | --: |
| `yf-mol-62k` | research/003 (this run) | 14 | 15 | 9 | 3, 1, 1, **4**, 1, 1, 1, 1, 1 | 4 |
| `yf-mol-3py` | research/002 | 15 | 17 | 9 | 3, 1, 1, **5**, 1, 1, 1, 1, 1 | 5 |
| `yf-mol-y7f` | plans/plan-033 | 40 | 38 | 16 | 13, 1, 1, 4, 4, 3, 4, 1, 1, 1, 2, 1, 1, 1, 1, 1 | 13 |
| `yf-mol-e9q` | plans/plan-0xx | 36 | 32 | 9 | 11, 2, 2, 6, 10, 1, 1, 2, 1 | 11 |

Two structural readings:

- **Research epics are a chain with one bulge.** 7 of 9 layers have width 1; the single wide
  layer is the retrieve fan-out. This is the formula shape [YF-4] realized verbatim.
- **Plan epics have `|E| ≈ |V|`** (38 edges over 40 nodes; 32 over 36). A tree has exactly
  `|V|-1` edges, so the plan DAG is essentially a **spanning forest** — near-tree, with only a
  handful of multi-parent joins. Layer 0's large width (13 / 11) is inflated by *container*
  epics, which carry no dependency edges at all (created `--parent` only, because "bd rejects
  a task blocking an epic" [YF-21]).

The rendered graph for this research run makes the shape literal [YF-22]:

> "LAYER 0 (ready) ... LAYER 8 ... `○ yf-research` ... `✓ Begin research` → `✓ Build tooling`
> → [4× `Retrieve:`] → `○ Triangulate` → `○ Synthesize` → `○ Critique` → `○ Refine` →
> `○ Package` ... Dependencies: 15 blocking relationships. Total: 14 issues across 9 layers"

### b.3 — Gates

Gates are first-class bead types (`-t gate`) with a two-bead compile artifact:

> "REQ-PHASE-007: A `type = "gate"` formula step yields a task wrapper (`yf-research.gate`)
> plus the real gate (`yf-research.gate-gate`); the gate is resolved via the `gate-*` key,
> while downstream `needs` depends on the wrapper." [YF-23]

yf-plan additionally emits *capability gates* with a `Test:` bash command in the description
[YF-24] and a *reconcile gate* that "auto-resolves when all execution beads close" [YF-25].
The reconcile gate is the only auto-evaluated predicate edge in either skill.

### b.4 — Swarm: created and never consumed (absence finding)

`bd swarm` appears **exactly once** in the entire `skills/` tree:

> "7. **Create swarm and report:**
> ```bash
> bd swarm create ${EPIC} --json
> bd graph ${EPIC}
> ```" [YF-26]

`grep -rn "swarm" skills/` returns those two lines and nothing else — no coordinator, no
formula, no spec, and no yf-plan surface references it. In the live graph the swarm node is a
**disconnected orphan**: `○ Swarm: yf-research / yf-wxp9 P2` sits in LAYER 0 with zero
in-edges and zero out-edges [YF-22]. **Absence: the swarm primitive is constructed but never
read by any execution path.**

### b.5 — `discovered-from`

Both coordinators mandate it for runtime work discovery:

> "New work discovered during execution: `bd create ... --deps discovered-from:<parent-id>`"
> [YF-27]

But the same edge type is explicitly declared *unclassifiable* by the resilience contract:

> "there is no reliable bd-state signal separating disposable scratch from real
> `discovered-from` work, so the close decision stays with the operator. **No bead is ever
> auto-closed.**" [YF-28]

So `discovered-from` is a write-only annotation on the recovery path.

---

## (c) How the coordinator WALKS the graph

**Answer: a strictly sequential, one-bead-at-a-time ready-poll loop. Neither coordinator
dispatches in parallel, and neither ever reads the graph structure.**

yf-research `agents/coordinator.md`, verbatim and complete [YF-29]:

> "Repeat until `bd ready --json` returns no beads for this epic:
> 1. **Find ready work:** `bd ready --json` — Filter to beads whose parent is `${EPIC}`.
> 2. **Claim the bead:** `bd update <id> --claim --json`
> 3. **Read the bead's metadata.** ...
> 4. **Dispatch the agent:** ... Spawn subagent (via Agent tool) ...
> 5. **Record the artifact:** ...
> 6. **Close the bead:** `bd close <id> --reason "Completed" --json`
> 7. **Repeat** from step 1."

Every noun is singular — *the* bead, *the* agent. Step 6 (close) precedes step 7 (re-poll),
so the loop is `poll → claim₁ → dispatch₁ → await₁ → close₁ → poll`. `bd ready` may return a
set; the loop consumes one element of it and throws the rest away until the next iteration.

yf-plan `agents/coordinator.md` is the same six-step cycle with gate handling spliced in
[YF-30]:

> "1. `bd ready --json` — filter to beads under `${EPIC}`
> 2. For gate-type beads: read description, run test command — Pass: `bd gate resolve
> <gate-id>` / Fail: mark blocked, skip
> 3. `bd update <id> --claim --json`
> 4. `bd show <id> --json` — read metadata
> 5. If metadata specifies agent file, spawn sub-agent with that prompt. Otherwise execute
> directly. ...
> 6. `bd close <id> --reason "Completed" --json`"

This is normative, not incidental — it is a SPEC requirement:

> "REQ-AGENT-010: The coordinator drives the bead DAG via a `bd ready` → claim → execute →
> close loop. ... Verification: coordinator.md Loop section describes the **6-step cycle**."
> [YF-31]

What the walk does *not* do:
- No `bd graph` / `bd dep` read anywhere in either coordinator (searched: `grep -rn "bd graph|bd mol |discovered-from" skills/yf-plan skills/yf-research`; the only `bd graph` hit is the report-only line in yf-research SKILL.md Phase 3 [YF-26]).
- No batching of a ready-set into concurrent `Agent` calls.
- No join/barrier logic — the join is delegated entirely to bd's own readiness computation.
- No retry, no backoff, no per-node failure policy. A failing bead is either "mark blocked,
  skip" (gates only) or unspecified.

The only concurrency the coordinator asserts is *scheduling* concurrency in prose:

> "REQ-AGENT-011: The coordinator drains all unblocked work before reporting blocked gates.
> Rationale: Reporting a blocked gate while **parallel work** remains wastes operator
> attention." [YF-32]

"Drain" here means "keep iterating the serial loop", not "run in parallel".

---

## (d) Every point where a graph-shaped artifact is executed linearly

| # | Graph-shaped artifact | Where it is executed linearly | Citation |
| :-- | :-- | :-- | :-- |
| d1 | The retrieve fan-out layer (width 4–5, all edges to a single join) | The coordinator claims and dispatches one retrieve bead per iteration, closing it before re-polling | [YF-29] |
| d2 | The plan bead DAG (40 nodes, layers of width 4) | Same 6-step serial cycle | [YF-30], [YF-31] |
| d3 | `plan.md`'s `depends-on` DAG (25 edges in plan-033, incl. multi-parent `depends-on: 6.2, 1.5, gate:pi-rule-target-verified`) | Transcribed by an LLM into `bd create --deps` calls; never parsed, never validated topologically | [YF-33], [YF-18] |
| d4 | The investigation wisp (fan-out molecule) | Beads injected, agents dispatched outside the wisp, then `bd mol burn --force 2>/dev/null \|\| true` — output discarded | [YF-6], [YF-7] |
| d5 | The two-pass review (a natural parallel fan-out: mechanical conformance ⟂ adversarial judgment) | "Two passes, **in order**." Conformance must PASS before red-team runs | [YF-34] |
| d6 | The 5-cycle red-team REVISE loop | A conversational loop with no bead, no gate, no formula step — recorded only as `log.md` prose after the fact | [YF-2] |
| d7 | The REFINE gap-fill feedback edge | Wired forward to `package`, not back to `triangulate`; the loop is cut | [YF-12] |
| d8 | `bd swarm create ${EPIC}` | Orphan node, zero edges, never read | [YF-26], [YF-22] |
| d9 | Post-investigation write-back | "Both writes BEFORE next sub-agent spawns" — an explicit serialization barrier imposed on the one parallel fan-out yf-plan has | [YF-35] |
| d10 | The shared `sources.json` join | N parallel retrievers are told to write the same file with no merge strategy, shard, or lock | [YF-36] |

### d.5 detail — review is a chain, not a fan-out

> "Two passes, in order. Both agents are read-only (REQ-AGENT-043); the main session acts on
> their verdicts.
> 1. **Conformance** — ... Verdict `PASS | INCOMPLETE`. On `INCOMPLETE`, resolve the listed
> gaps and re-run before proceeding ...
> 2. **Adversarial** — **once conformance is `PASS`** ..." [YF-34]

The two reviewers have disjoint context and disjoint verdict vocabularies (REQ-AGENT-044/045
[YF-37]) — i.e. they are structurally independent — yet they are serialized.

### d.9 detail — the explicit anti-parallel barrier

INVESTIGATE fan-out is undone one paragraph later:

> "After each sub-agent returns: 1. Write finding to `findings/exp-NNN-<slug>.md` 2. Update
> plan.md Investigation Findings 3. **Both writes BEFORE next sub-agent spawns**" [YF-35]

"Independent experiments run in parallel" [YF-5] and "both writes before next sub-agent
spawns" [YF-35] are in direct tension in the same phase of the same file. **[uncertain]**
which one an executing agent actually honours; the repo carries no test that asserts either.

### d.10 detail — the unresolved join

`retriever.md` instructs every cluster agent:

> "4. For each source found, record in `${research_dir}/sources.json`" [YF-36]

With `mode: deep` and 4 clusters, that is 4 writers to one JSON file and no stated merge
semantics. Concrete field evidence: the dispatch prompt for *this very bead* carried an
operator-level override — "Do NOT write to the shared `sources.json` ... write
`sources-<cluster>.json`" — i.e. the parallel-write hazard is real enough that it is patched
by hand at dispatch time rather than in the skill. **[uncited: the override text is the
prompt of this agent, not a repo file.]**

---

## (e) The one real graph algorithm in the repo

`close_cascade.py` is a genuine post-order DFS:

> "On plan COMPLETE, walk the plan's bead tree bottom-up and close every **container**
> (intermediate epic and the top-level plan molecule) whose children are **all terminal**"
> [YF-38]

with `def visit(bead)` recursing children-first:

> "# Container: process children first (post-order / bottom-up)." [YF-39]

Two qualifications: it walks the **containment tree** (`bd children` / `--parent`), not the
dependency DAG; and it runs once, at teardown, after all execution is over. It is 241 lines
[YF-38] against `plan_manager.py`'s 3525 [YF-13].

## (f) A DAG-walk engine was considered and explicitly rejected

The strongest single piece of evidence that the linearity is *chosen*, not accidental:

> "REQ-AGENT-047: The red-team performs a **precondition cross-check** ... This is
> deliberately the prose check, **not a topological DAG walk**: the expensive branch (a
> `requires:` key plus a walk engine) was measured against the same corpus and found to buy
> nothing, and 2 of the 5 defects are not reachability failures a graph walk would find at
> all." [YF-40]

Recorded again in the root SPEC's amendment log:

> "#113's cheap branch, explicitly **without** a `requires:` schema key or a DAG-walk engine,
> which measurement against the same corpus found unjustified" [YF-41]

Also note the observed failure mode this was reasoning about:

> "in d3-pxe plan-013 a capability gate whose condition required a preview of the output of
> the very issue it blocked survived conformance and **two** red-team cycles, because every
> pass checked that the gate declared a type, approvers, a condition, and a test — none
> checked whether the condition could ever become true." [YF-42]

That is a **cycle in the gate/dependency graph** that shipped through two reviews — i.e. a
defect class a graph engine catches structurally and prose review demonstrably did not.
REQ-AGENT-046 [YF-43] responds to it with another prompt-level contract.

---

## Evidence balance on "yf artifacts are executable graphs"

**For:**
- A real graph store with typed nodes (`task` / `epic` / `gate` / `molecule`), typed edges
  (blocking, parent, `discovered-from`), and server-side readiness computation (`bd ready`)
  [YF-20], [YF-22].
- Real fan-out + join wiring, transactionally batched [YF-8], [YF-9].
- Real gates with executable test commands [YF-24] and an auto-resolving predicate gate
  [YF-25].
- Durable resume pointers and a stuck-bead sweep [YF-28] — the graph survives process death,
  which is the property that distinguishes a program-graph from a diagram.
- Runtime graph mutation (`discovered-from` injection) [YF-11].

**Against:**
- The consumer is a serial `bd ready` → claim → dispatch → close loop, specified that way
  [YF-31], with no parallel dispatch, no join logic, no retry, no failure policy [YF-29],
  [YF-30].
- The graph never enters the construction phase at all — 5 review cycles, the whole
  PLAN/SCOPE program, and the only real fan-out (INVESTIGATE) are conversational [YF-1],
  [YF-2], [YF-5].
- The formula language, as used, expresses only `needs = [single-predecessor]` chains
  [YF-4]; yf-plan's formula has one node [YF-19].
- Measured plan DAGs are near-trees (`|E| ≈ |V|`) [YF-20].
- A declared primitive (`swarm`) is emitted and never read [YF-26], [YF-22].
- No graph code exists in either manager script; the `plan.md`-DAG → bead-DAG compiler is an
  LLM reading prose [YF-13], [YF-14], [YF-15], [YF-18].
- The one topological algorithm is a containment-tree teardown [YF-38].
- A DAG-walk engine was evaluated against the corpus and rejected [YF-40], [YF-41].

**Verdict for the synthesizer:** yf produces graph-shaped *data* in a graph *store*, walked
by a linear scheduler. It is a persisted, resumable, human-auditable task DAG — not an
executable graph program. The degeneration point is precisely one file per skill:
`agents/coordinator.md`.

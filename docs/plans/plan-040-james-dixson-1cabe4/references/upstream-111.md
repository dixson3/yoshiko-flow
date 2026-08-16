---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #111: Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives

- **Number:** 111
- **Title:** Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Context

The `yf-*` skill family is wired deeply into `bd` (beads) semantics: the `bd ready` → `bd update --claim` → `bd close` loop, gate-typed dependency edges, `--json` parsing, `bd mol pour` formulas, and the coordinator dispatch pattern. That coupling is fine, but it currently carries a specific liability.

Upstream `bd` moved to **Dolt** as its storage engine (server + embedded modes, schema migrations, remotes) as it became the control/data plane for Gas Town. That is the direct source of the wedged-migration failure mode that `yf-beads-init` and its always-loaded `YOSHIKO_FLOW.md` rule exist to detect and repair — the working-set flush → `bd migrate schema` → `bd migrate` sequence, the false-negative invariant around `bd status --json` returning error JSON with exit 0, and the embedded-vs-server mode split.

To be clear on what is *not* the concern: beads is MIT-licensed and is still maintained as a first-class standalone product; Gas Town is built on top of beads, not the reverse. The issue is **architectural drift** — the storage layer is being pulled by an orchestrator's needs, not the solo/small-team use case this repo targets.

This issue is to investigate two candidate replacements.

## Candidate 1 — `br` (beads_rust)

https://github.com/Dicklesworthstone/beads_rust

Rust port by Jeffrey Emanuel that deliberately **froze the classic SQLite + JSONL architecture** as upstream moved toward Gas Town/Dolt. Explicitly "non-invasive by default": no Dolt, no automatic git commits, no installed hooks, no background daemon. MIT (with an OpenAI/Anthropic rider clause). ~1k stars, ~2.4k commits, actively maintained; the author uses it in production for his own agent tooling.

**Why it's interesting:** smallest possible migration. Same conceptual model, same JSONL-over-git collaboration story, minus the entire class of failure `yf-beads-init` was written to handle.

**Known friction:**
- Binary is `br`, not `bd` — every skill, script, and rule referencing `bd` needs a rename pass.
- It is a snapshot of *classic* beads, not a tracking fork. Newer surfaces almost certainly absent: `bd mol pour` / formulas, gate-typed edges, `bd batch`, memory decay/compaction, `bd dolt *` (moot), and the upstream-tracking hooks `yf-beads-upstream` drives.
- No stated compatibility guarantee with current `bd` — divergence is intentional.

## Candidate 2 — `ticket-rs` (`tk`)

https://docs.ticket-rs.io/blog/whitepaper

Rust, single 9–13 MB static binary, zero runtime deps, zero daemons. Storage is **plain Markdown files with YAML frontmatter under `.tickets/`** — no database at all; git is the entire history mechanism. Forked from `wedow/ticket`, extended with graph analytics by Henrik Albihn.

**Why it's interesting:** the graph engine is strictly better than what `bd` offers today. Four algorithms over the issue DAG:
- PageRank → surfaces high-impact blockers (`tk priority`)
- Betweenness centrality → detects architectural bottlenecks (`tk insights`)
- Critical path → minimum project duration
- Topological sort → batches issues into parallel execution tracks (`tk plan`)

It is also explicitly token-budget-aware, which no other candidate is: `tk prime` emits compact project state for agent session init, `tk triage` gives a unified ~500-token health report. `tk ready` maps onto our core loop directly.

**Known friction:**
- Larger rewrite than `br` — command surface and data model both differ.
- License not stated in the whitepaper; **must be confirmed before any adoption work.**
- Maturity, maintainer bus factor, and multi-agent concurrency semantics (does it have atomic claiming? file-level locking? what happens on concurrent `tk` writes from parallel agents?) are all unverified.
- Plain-file storage means no transactional bulk intake equivalent to `bd batch`.

## Investigation tasks

- [ ] Confirm `ticket-rs` license and maintenance health (commit cadence, issue responsiveness, contributor count).
- [ ] Build a command-mapping audit: every `bd` invocation across the `yf-*` skills → `br` equivalent, and → `tk` equivalent. Mark each as direct / adaptable / missing.
- [ ] Determine which `bd` features we actually depend on vs. merely have available. Specifically audit real usage of: gate-typed edges, `bd mol pour` formulas, `bd batch`, memory decay, `bd dep` mutation, `--json` shapes.
- [ ] Evaluate multi-agent concurrency in each candidate — atomic claim semantics are load-bearing for the coordinator dispatch loop and for parallel fan-out.
- [ ] Evaluate merge-conflict behavior under parallel branches. `bd`'s hash-based IDs are specifically designed for this; verify each candidate's story.
- [ ] Assess impact on `yf-beads-upstream` (the `gh`-based issue mirror) — is it storage-agnostic enough to survive a backend swap?
- [ ] Assess what `yf-beads-init` becomes under each candidate. Under `br` and `tk` most of the verify/repair engine's reason for existing (wedged Dolt migrations) disappears; determine what, if anything, remains.
- [ ] Prototype: port one small beads-backed skill end-to-end to the leading candidate and run it for real.
- [ ] Decide: migrate, stay on `bd`, or introduce a storage-abstraction seam so the backend is swappable.

## Also surveyed, not shortlisted

For the record, so this isn't re-researched later:

| Tool | Storage | Why not shortlisted |
|:--|:--|:--|
| [tkr](https://shivamagarwal7.medium.com/tkr-a-git-native-task-tracker-built-for-ai-coding-agents-90d62e5c5b88) | MD + frontmatter in `.tlr/tickets/` | Similar shape to `ticket-rs` but weaker graph analytics; has tracker importers |
| [trekker](https://github.com/obsfx/trekker) | local SQLite | Deliberately minimal; too opinionated to carry our skill family |
| [Backlog.md](https://github.com/MrLesk/Backlog.md/) | MD in `backlog/tasks/` | Most mature ecosystem (MIT, ~5.6k stars, MCP server, terminal + web Kanban, brew/npm/nix) but weakest dependency-graph semantics — no real DAG solver |
| [git-issues](https://github.com/steviee/git-issues) | MD + frontmatter in `.issues/` | Very small, GitHub-Issues-shaped, no scheduling |
| [tick-md](https://github.com/Purple-Horizons/tick-md), [ai-todo](https://github.com/fxstein/ai-todo) | single/plain MD | Protocol-level only, far too thin |

Graph/DAG **memory** systems were also surveyed as a possible tracker+walker substrate — [Task Graph MCP](https://lobehub.com/mcp/oortonaut-task-graph-mcp) (DAG deps + atomic claiming + advisory file locks over MCP, the closest primitive match to `bd ready`), [memory-graph](https://github.com/memory-graph/memory-graph), [Basic Memory](https://blog.mcpservers.org/posts/mcp-memory-servers), [Graphiti](https://www.falkordb.com/blog/mcp-knowledge-graph-graphiti-falkordb/)/Zep, [Cognee](https://www.cognee.ai/blog/guides/open-source-memory-frameworks-llm-agents). Common gap: they provide a graph and a walker, but no issue-type semantics, no ready-work computation, and no claim/close lifecycle — all of which we would have to build. Task Graph MCP is the one worth revisiting if the shortlist fails.


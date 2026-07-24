`/yf-research` turns a question into a cited, resumable report instead of a one-shot answer. It decomposes a topic into a DAG of focused subtasks — retrieve, triangulate, synthesize, critique, refine, package — tracks every subtask as a bead, and produces a structured report with a credibility score attached to each source. It is the research counterpart to [yf-plan](/skills/yf-plan/): same beads-tracked, resumable, portable-artifact discipline, pointed at investigation rather than building.

## When it fires

Use `/yf-research` — or research-intent language when the output should be tracked, cited, or resumable — for any substantive research whose result you want to keep. On an ambiguous "research X" request, prefer it.

It coexists deliberately with the harness's built-in `deep-research`. The two do not compete; you choose by intent.

| Use `/yf-research` | Use the built-in `deep-research` |
| :--- | :--- |
| Result should be tracked, cited, or resumable | Quick, throwaway, same-turn web lookup |
| Work may span more than one session | You do not need to persist the answer |
| A teammate or a future you must be able to pick it up | — |

`/yf-research` cannot and does not replace the built-in — the built-in is compiled into the CLI. The explicit command is the reliable trigger.

## The pipeline

A research project runs through a fixed phase skeleton. Retrieval fans out; everything after it is serial, each stage depending on the verified output of the one before.

```
SCOPE → PLAN → GATE → TOOLING → RETRIEVE(×N) → TRIANGULATE → SYNTHESIZE → CRITIQUE → REFINE → PACKAGE
```

| Stage | What it does |
| :--- | :--- |
| **SCOPE / PLAN** | Frame the topic and decompose it into the subtask DAG. |
| **GATE** | A human checkpoint before spend. Auto-resolved inline in `quick` mode; otherwise resolved in a new session via `/yf-research coordinate`. |
| **TOOLING** | The toolsmith generates per-run helper scripts from the plan's stated tooling needs. |
| **RETRIEVE (×N)** | Fans out dynamically — one bead per source cluster, injected after the pour, clusters running in parallel. The retriever gathers sources for its cluster. |
| **TRIANGULATE** | Cross-reference claims across sources, score credibility, flag contradictions. |
| **SYNTHESIZE** | Assemble cited findings into a draft, credibility scores visible. |
| **CRITIQUE** | An adversarial red-team reviews the draft and may send the pipeline back to refine or retrieve. |
| **REFINE** | Fill the gaps the red-team found. Refine may extend the DAG at runtime, spawning new retrieve beads via a `discovered-from:` edge. |
| **PACKAGE** | Finalize the report and resolve every citation to a plain GFM link. |

**Depth modes** set how much the pipeline spends and whether it crosses a session boundary:

- `quick` — 3 to 5 sources, same session, the gate auto-resolved.
- `standard`, `deep`, `ultradeep` — the human gate is resolved in a fresh session via `coordinate`.

## Resumable by construction

The pipeline is resumable across sessions through the `coordinate` subcommand with gate auto-detection. A `coordinate` session that dies mid-loop can re-enter: because the start gate is already resolved, `/yf-research coordinate` finds the open epic through a durable pointer — the `epic:` line stamped into `plan.yaml` at pour — and resumes the loop. A pre-loop stuck-bead sweep resets any stranded `in_progress` beads back to `open` before work continues. It never auto-closes the unclassifiable; those are reported for a human to resolve.

## The epistemic contract

The report's integrity is the product, so every research agent enforces the same rules:

- **Every asserted claim carries a citation.** No uncited assertions.
- **Direct quotes are preferred over paraphrase** for load-bearing evidence.
- **Absence of evidence is a valid, recordable finding** — "we found nothing" is a result, not a gap to paper over.
- **Sources are credibility-scored**, and the score is visible in the synthesis. The scorer tiers official vendor-documentation domains, normalizes publication dates to UTC before scoring by age, and treats a missing date as evergreen rather than an error.

## Portable outputs

A finished research bundle is an OKF-RESEARCH artifact — self-contained, so a cold reader in another repo can understand it from the folder alone. It carries the reserved `index.md` and `log.md`, OKF frontmatter on every non-reserved `.md`, and its source sidecars. Outputs live under `docs/research/<NNN>-<slug>/` by default, or `Incubator/<slug>/research/<NNN>-<slug>/` when scoped to an [incubator](/skills/yf-incubator/); the `NNN` index is global across both roots so cross-references stay unambiguous.

Git authority is conservative. The pipeline reports a git handoff — the changed files plus proposed commit, sync, and push commands — and does not commit or push without explicit authorization.

## Search providers

Retrieval prefers the Exa MCP tools at the skill surface. Providers are **advisory, not blocking**: absent Exa, an agent-internal fallback uses `TAVILY_API_KEY` or `PERPLEXITY_API_KEY` if set. A missing provider surfaces as a warning and never blocks a run from starting.

## Usage

| Command | Effect |
| :--- | :--- |
| `/yf-research init` | Consent-only per-project setup (prerequisite check, opt-out). |
| `/yf-research <topic>` | Start a new research project. |
| `/yf-research coordinate [<idx-or-epic>]` | Resolve the active gate (or resume a crashed run) and drive the coordinator loop. |
| `/yf-research status [<idx>]` | Check research status. |

`/yf-research` is a beads-backed skill and requires `bd` >= 1.1.0 with an initialized database. It shares the `bd` support layer with [yf-plan](/skills/yf-plan/) and runs through the same `yf preflight` gate before it acts.

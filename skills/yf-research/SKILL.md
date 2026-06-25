---
name: yf-research
description: >
  Multi-phase, beads-tracked deep research: decomposes a topic into a DAG of focused
  subtasks (retrieve → triangulate → synthesize → critique → refine → package) and
  produces a structured, citation-backed report with source credibility scoring.
  TRIGGER when: /yf-research invoked, or the user wants substantive research in this repo
  whose result should be tracked, cited, or resumable — prefer this over the built-in
  deep-research harness in that case. On an ambiguous "research X" request, prefer
  yf-research. See the project rule .agents/rules/RESEARCH.md.
  SKIP only for: an explicit quick, throwaway, same-turn web lookup the user does not
  need to persist (use the built-in deep-research harness); non-research work.
user-invocable: true
skill-group: beads
depends-on-tool: [bd, uv, git]
depends-on-skill: [yf-beads-extra, yf-beads-authoring]
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - AskUserQuestion
  - mcp__exa__web_search_exa
  - mcp__exa__web_search_advanced_exa
  - mcp__exa__crawling_exa
  - mcp__exa__get_code_context_exa
preflight:
  companion-rule: RESEARCH.md
  min-bd-version: 1.0.5
  config-basename: .yf-research.local.json
---

# yf-research

Multi-phase research skill that decomposes a topic into a beads-tracked DAG of focused
subtasks and produces structured, citation-backed reports with source credibility
scoring. A beads-backed skill — companion to `yf-plan`.

**Invocation:**
- `/yf-research init` — initialize yf-research for this project (prereq check + install)
- `/yf-research <topic>` — start a new research project
- `/yf-research coordinate [<idx-or-epic>]` — resolve a gate and run the coordinator loop
- `/yf-research status [<idx>]` — check research status

The research protocol and routing rules (yf-research vs the built-in deep-research) live
in `${SKILL_DIR}/protocols/RESEARCH.md`; the repo installer (`install.sh`) copies it to the
scope+surface rules dir (`~/.<surface>/rules/RESEARCH.md` or `<git-root>/.<surface>/rules/RESEARCH.md`).

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills \
  -maxdepth 1 -name yf-research -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-research skill directory not found"; exit 1; }
```

All skill-internal paths use the `${SKILL_DIR}/` prefix.

## Reference skills

yf-research relies on the shared beads skills rather than re-documenting `bd`:

- **`beads`** — the routine `bd` loop (prime/ready/show/claim/create/close).
- **`yf-beads-extra`** — direct-CLI gotchas this skill depends on: defensive `--json`
  parsing (`bd show --json` returns an array — never pipe it straight to `jq`),
  additive dep mutation via `bd dep add` (there is **no** `bd update --deps`), gate
  resolution via `bd gate resolve`, `bd batch`, and the `bd mol pour` output shape.
- **`yf-beads-authoring`** — the formula / `mol pour` / coordinator / `coordinate`
  conventions this skill is built on.

## Pre-flight

**Run on every invocation except `/yf-research init`.** Run the preflight and branch on
its status (it follows the Skill Surface Convention — see the `yf-skill-authoring` skill):

```bash
yf preflight yf-research --json
```

(The `yf preflight` JSON is a superset of the legacy `research_manager.py` preflight schema —
same status values, plus `warnings` and the rule/scaffold fields — so the branch logic below
is unchanged; only the command moved into the `yf` kernel. See docs/yf/preflight-contract.md.)

- **`ignored`** (operator set `"ignore-skill": true` in `.yf-research.local.json`): exit
  silently.
- **`ok`**: proceed. On `ok`, preflight also ensures the idempotent project scaffold (the
  `docs/research` dir + the `/.yf-research.local.json` and `/.state/` gitignore anchors);
  anything it created is listed in `scaffold_added`. The ensure is additive-only and runs
  once per scaffold version (gated by `scaffold-ensured` state) — it will not re-add an
  anchor an operator later removes. (`warnings` carry advisory provider notes; `instructions`
  may carry a non-blocking `update available` note for `RESEARCH.md`.)
- **`system_deps_missing` / `bd_not_initialized`**: tell the user to run `/yf-research init`
  to set up the project. Stop.
- **`rule_missing` / `rule_drift` / `rule_deprecated` / `manifest_*`**: follow the
  `instructions` in the result. The companion rule is installed by the repo installer, so
  these point at `install.sh` (e.g. re-run `install.sh --force` to restore a drifted rule),
  not `init`. Stop.

Config vs state: `ignore-skill` is an operator decision in `.yf-research.local.json` (repo
root, gitignored). `prereqs-present` and `scaffold-ensured` are runtime state in `.yf/yf-research/preflight.json`.
The companion rule is installed by the repo installer (`install.sh`) to the scope+surface
rules dir (user-scope `~/.<surface>/rules/RESEARCH.md`, project-scope
`<git-root>/.<surface>/rules/RESEARCH.md`; `.claude` or `.agents`); preflight resolves it in
precedence order (user/global copy first) and hash-checks it against `protocols/manifest.json`.

## /yf-research init

Initialize yf-research for the current project. Spawn a sub-agent (`Agent` with
`subagent_type="general-purpose"`) with this prompt:

```
Run yf-research init for Claude Code:

1. Run `yf preflight yf-research --json` and parse
   the JSON. Record any `warnings` to relay. On status "ok", preflight has already ensured
   the idempotent scaffold (the docs/research dir plus the `/.yf-research.local.json` and
   `/.state/` gitignore anchors); `scaffold_added` lists what it created. Per-incubator
   roots (`Incubator/<slug>/research/`) are created lazily. The companion rule `RESEARCH.md`
   is installed by the repo installer (`install.sh`), not here — never write to AGENTS/ and
   never edit CLAUDE.md.
2. If status is "system_deps_missing" or "bd_not_initialized", return the JSON as-is.
   Do nothing else. (The scaffold is intentionally NOT ensured until the project is ready.)
3. Return JSON: {"status":"ready","actions":<the check's `scaffold_added` array, or []>,"warnings":[...],"rule":<the check's `rule` object>}.
```

Handle the sub-agent result:

- **"ready"**: print actions taken and relay any provider `warnings`. If the returned `rule.outcome` is not `ok`/`update_available` (e.g. `rule_missing`/`rule_drift`), tell the user the companion rule is missing or drifted and to re-run the repo installer — `install.sh` (add `--force` to clobber a drifted/hand-edited copy); init does not install rules. Then show usage.
- **"system_deps_missing"** / **"bd_not_initialized"**: print the missing items and
  instructions. Ask: "(1) stop and fix the prerequisites, or (2) ignore yf-research in
  this project?" If ignore, write `{"ignore-skill":true}` to `.yf-research.local.json` at
  the repo root, and ensure `/.yf-research.local.json` is in `.gitignore`, then exit.

`research_manager.py` is intentionally narrow — a defensive `json-get`. The preflight
(config gating + state caching + installed-rule hash) moved to the `yf preflight` kernel
(plan-010). Research-directory and
`_index.md` state stays in `index_manager.py`. After editing `protocols/RESEARCH.md`,
refresh the hash: `uv run ${SKILL_DIR}/scripts/manifest_update.py ${SKILL_DIR}/protocols`,
and commit the rule + `manifest.json` together.

> **Rule:** All task tracking MUST use `bd`. Never use TodoWrite, markdown checklists,
> or inline task lists. Track sub-work discovered during execution as a new bead with
> `--deps discovered-from:<parent-id>`.

## Epistemic Rules

These apply to ALL agents and ALL research outputs.

1. **Absence is a valid finding.** If a question cannot be answered from available
   sources, state "No evidence found" with what was searched and where. Never fabricate,
   speculate, or pad a thin evidence base with general knowledge.
2. **Direct quotes over paraphrase.** When citing, include a direct quote (`> "..." [N]`)
   with inline citation. Paraphrase only when the original is excessively long — still cite.
3. **No uncited assertions.** Every factual claim in any artifact must carry an inline
   citation `[N]` resolving to an entry in `sources.json`. Methodology/structure
   statements are exempt. If you cannot cite it, flag it `[uncited]`.

## Workflow

### Phase 1: SCOPE (interactive)

On `/yf-research <topic>`, ask scoping questions via AskUserQuestion:

1. **Depth mode** — `quick` (3-5 sources, same session, auto-resolved gate) | `standard`
   (15-30 sources, new session, manual gate; default) | `deep` (30+, parallel retrievers)
   | `ultradeep` (50+, maximum rigor).
2. **Research questions** — primary and secondary.
3. **Known sources** — starting URLs, papers, domains to prioritize.
4. **Output audience** — personal notes / presentation / publication / technical report.
5. **Exclusions** — topics or sources to avoid.

### Phase 2: PLAN (generate plan.yaml)

**Determine the research root (incubator routing).** Research lands under one of:

- `docs/research/` — default
- `Incubator/<slug>/research/` — when scoped to a specific incubator (see the
  `yf-incubator` skill)

Auto-detect from CWD; if `pwd` is inside `Incubator/<slug>/...`, propose `<slug>`.
Confirm during scoping; accept a different slug or `none` (→ `docs/research/`). If the
operator names a non-existent incubator, confirm before creating it.

**Determine the next topic index** (global across roots so cross-references stay
unambiguous):

```bash
case "$(pwd)" in
  */Incubator/*) incubator=$(pwd | sed -E 's|.*/Incubator/([^/]+).*|\1|') ;;
  *) incubator="" ;;
esac
[ -n "$incubator" ] && research_root="Incubator/${incubator}/research" || research_root="docs/research"
count=$(ls -d docs/research/[0-9]*-* Incubator/*/research/[0-9]*-* 2>/dev/null | wc -l | tr -d ' ')
next_idx=$(printf "%03d" $((count + 1)))
topic_slug=$(echo "<topic>" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
research_dir="${research_root}/${next_idx}-${topic_slug}"
```

**plan.yaml structure:**

```yaml
topic: "<topic>"
mode: standard          # quick | standard | deep | ultradeep
priority: 2             # 0-4
research_dir: "<research_root>/<idx>-<topic-slug>"

questions:
  primary: ["What is X?", "How does X compare to Y?"]
  secondary: ["What are the limitations of X?"]

source_clusters:
  - name: academic
    targets: ["Google Scholar", "arXiv", "PubMed"]
    method: exa            # exa | perplexity | tavily | direct
    exa_category: "research paper"
    expected_artifacts: 5
  - name: industry
    targets: ["company blogs", "whitepapers"]
    method: exa
    expected_artifacts: 3

tooling_needed:
  - description: "Custom parser for X data format"
    shared: false        # true = ${SKILL_DIR}/scripts/, false = topic scripts/

execution:
  estimated_beads: 10
  estimated_budget_usd: 8.00
  session_mode: new      # same | new

# epic: <id>             # added at pour (Phase 3) — durable resume pointer (REQ-ORCH-008)
```

Present the plan to the operator. Iterate until approved.

### Phase 3: BEAD CREATION (on approval)

1. **Create the research directory and save the plan:**

```bash
mkdir -p "${research_dir}/scripts" "${research_dir}/artifacts" "${research_dir}/diagrams"
# diagrams/ holds d2 diagrams (.d2 source + .png render) authored per the yf-diagram-authoring skill
# Write plan.yaml to ${research_dir}/plan.yaml
```

2. **Initialize `_index.md`:**

```bash
uv run ${SKILL_DIR}/scripts/index_manager.py init "${research_dir}" "${topic}"
```

3. **Pour the yf-research formula.** `bd mol pour --json` returns a single clean object
   (`new_epic_id`, `id_mapping`); `jq` is safe here. (For `bd show`/`bd list`, parse
   defensively — see `yf-beads-extra`.)

```bash
cp -f "${SKILL_DIR}/formulas/yf-research.formula.toml" .beads/formulas/
RESULT=$(bd mol pour yf-research \
  --var topic="${topic}" --var mode="${mode}" --var research_dir="${research_dir}" --json)
rm -f .beads/formulas/yf-research.formula.toml

EPIC=$(echo "$RESULT" | jq -r '.new_epic_id')
# A gate-type formula step yields a task wrapper (id_mapping["yf-research.gate"]) AND the
# real gate (id_mapping["yf-research.gate-gate"]). Resolve the gate via the gate-* key
# (see yf-beads-authoring → Formula gate steps).
GATE_ID=$(echo "$RESULT"   | jq -r '.id_mapping["yf-research.gate-gate"]')
TOOLING_ID=$(echo "$RESULT"| jq -r '.id_mapping["yf-research.tooling"]')
TRIANG_ID=$(echo "$RESULT" | jq -r '.id_mapping["yf-research.triangulate"]')
SYNTH_ID=$(echo "$RESULT"  | jq -r '.id_mapping["yf-research.synthesize"]')
CRIT_ID=$(echo "$RESULT"   | jq -r '.id_mapping["yf-research.critique"]')
REFINE_ID=$(echo "$RESULT" | jq -r '.id_mapping["yf-research.refine"]')
PACKAGE_ID=$(echo "$RESULT"| jq -r '.id_mapping["yf-research.package"]')
```

**Persist the epic pointer** so a crashed `coordinate` session can resume after the start
gate is already resolved (yf-beads-authoring REQ-ORCH-008). Two writes keyed on `${EPIC}`: a
**metadata fallback** (stamp the epic with its `research_dir`, queryable via
`bd list --metadata-field`) and a **durable pointer** (`epic:` line in `plan.yaml`):

```bash
bd update ${EPIC} --metadata "$(jq -nc --arg d "${research_dir}" '{research_dir:$d}')" -q
# Add/replace the `epic: ${EPIC}` line in plan.yaml (idempotent helper).
uv run ${SKILL_DIR}/scripts/research_manager.py record-epic "${research_dir}" "${EPIC}"
```

4. **Attach agent metadata to each step** (`agent` path is relative to `${SKILL_DIR}`):

```bash
bd update ${TOOLING_ID} --metadata '{"agent":"agents/toolsmith.md","context":["plan.yaml"]}' -q
bd update ${TRIANG_ID}  --metadata '{"agent":"agents/triangulator.md","context":["sources.json","artifacts/"]}' -q
bd update ${SYNTH_ID}   --metadata '{"agent":"agents/synthesizer.md","context":["plan.yaml","artifacts/triangulation.md"]}' -q
bd update ${CRIT_ID}    --metadata '{"agent":"agents/red-team.md","context":["Summary.md","sources.json"]}' -q
bd update ${REFINE_ID}  --metadata '{"agent":"agents/refiner.md","context":["Summary.md","artifacts/critique.md","plan.yaml"]}' -q
bd update ${PACKAGE_ID} --metadata '{"agent":"agents/packager.md","context":["*"]}' -q
```

5. **Inject dynamic retrieve beads** (one per source cluster). Capture each ID; `--silent`
   prints only the ID:

```bash
RETRIEVE_IDS=()
for cluster in ${clusters}; do
  # Build metadata with jq -nc --arg, never shell interpolation (see yf-beads-authoring).
  META=$(jq -nc --arg agent "agents/retriever.md" --arg cluster "${cluster_name}" \
    '{agent:$agent, context:["plan.yaml"], cluster:$cluster}')
  RID=$(bd create "Retrieve: ${cluster_name}" \
    --description="Gather sources from ${cluster_targets}. Method: ${cluster_method}." \
    -t task -p 2 --parent ${EPIC} --deps "${TOOLING_ID}" \
    --metadata "$META" --silent)
  [ -z "$RID" ] && { echo "ERROR: retrieve bead create failed" >&2; exit 1; }
  RETRIEVE_IDS+=("$RID")
done
```

6. **Wire triangulate to depend on every retrieve bead.** There is no `bd update --deps`
   in 1.0.5 — add each edge with `bd dep add` (additive), batched in one transaction
   (see `yf-beads-extra` → *Dependency-edge mutation* / *Bulk intake*):

```bash
DEP_OPS=""
for rid in "${RETRIEVE_IDS[@]}"; do
  DEP_OPS+="dep add ${TRIANG_ID} ${rid}\n"
done
[ -n "$DEP_OPS" ] && printf '%b' "$DEP_OPS" | bd batch -m "yf-research ${EPIC} retrieve wiring"
```

7. **Create swarm and report:**

```bash
bd swarm create ${EPIC} --json
bd graph ${EPIC}
```

### Phase 4: HANDOFF

**standard/deep/ultradeep:** print — `RESEARCH READY — run in a new Claude Code session:
/yf-research coordinate`.

Multiple pending projects can be disambiguated: `/yf-research coordinate 002` (topic
index) or `/yf-research coordinate <epic-id>`.

**quick mode:** skip handoff. Resolve the gate with `bd gate resolve ${GATE_ID}`, then
read `${SKILL_DIR}/agents/coordinator.md` and run the loop inline.

---

## Coordinate

On `/yf-research coordinate [<idx-or-epic>]`:

### Gate resolution

With no argument, detect pending gates (parse defensively — see `yf-beads-extra`):

```bash
bd gate list --json    # filter to gates whose parent epic was poured from yf-research
```

| Open gates | Action |
|:----------|:-------|
| 0 | Check for a resumable epic (see *Resume* below) **before** exiting — a crashed run's gate is already resolved, so 0 open gates may mean "resume," not "nothing to do." |
| 1 | Auto-select, resolve, begin. |
| N | Present each gate's parent-epic topic via AskUserQuestion; resolve the selected gate, begin. |

With an argument:
- **Topic index** (e.g. `002`): scan `docs/research/NNN-*` and `Incubator/*/research/NNN-*`
  for the matching dir; read its `plan.yaml`; find the open gate whose parent epic matches.
- **Epic ID**: find the open gate whose parent is that epic.

### Resolve and begin

```bash
bd gate resolve ${GATE_ID}
```

Then determine the research dir from the epic context, read
`${SKILL_DIR}/agents/coordinator.md`, and run the loop with `EPIC` and `research_dir`.

### Resume (crashed coordinate session)

A `coordinate` session can die mid-loop. The start gate was resolved on first entry, so
gate auto-detection then finds **0 open gates** — without a resume path the run is
unrecoverable. Before reporting "No pending research gates," look for a resumable epic
(yf-beads-authoring REQ-ORCH-008 resume detection):

```bash
# Durable pointer (primary): read the `epic:` line from the target dir's plan.yaml.
EPIC=$(grep -E '^epic:[[:space:]]' "${research_dir}/plan.yaml" 2>/dev/null \
  | head -1 | sed -E 's/^epic:[[:space:]]*//')

# Metadata fallback (dirs poured before the epic: pointer existed): only the top epic is
# stamped with research_dir (Phase 3), so bd's own filters isolate it — no post-filter needed.
[ -z "$EPIC" ] && EPIC=$(bd list --metadata-field research_dir="${research_dir}" \
  --status open,in_progress --json \
  | uv run ${SKILL_DIR}/scripts/research_manager.py json-get 0 id)
```

If a resumable yf-research epic with unclosed descendants is found (via the explicit
`<idx-or-epic>` argument or either lookup above), **resume** it: read
`${SKILL_DIR}/agents/coordinator.md` and run the loop with that `EPIC` and `research_dir`.
The coordinator's **pre-loop stuck-bead sweep** (REQ-ORCH-009) resets beads the crash
stranded. Do **not** re-pour and do **not** re-resolve the gate — it is already resolved.

If no resumable epic is found, warn "No pending research gates." and exit.

### Completion contract

The coordinate session is complete when the package bead has run and the report is
finalized. **Git is handled per this project's conservative authority** (see
`agents/packager.md`): the session ends by reporting changed files and the proposed
commit/sync/push commands — it does **not** commit or push without explicit
authorization.

---

## Status

On `/yf-research status [<idx>]`:

- with `<idx>`: show `bd epic status <epic-id>` and the `_index.md` for that topic.
- without: list research dirs across both roots with epic status —

```bash
for dir in docs/research/[0-9]*-*/ Incubator/*/research/[0-9]*-*/; do
  [ -d "$dir" ] || continue
  echo "## $(basename "$dir")"
  cat "${dir}/_index.md" 2>/dev/null || echo "(no index)"
  echo
done
```

## Markdown output convention

Every markdown artifact this skill writes (`Summary.md`, `sources.md`, `artifacts/*.md`,
`_index.md`, the packaged report) is plain **GFM** — never Obsidian `[[wikilinks]]` or
`![[embeds]]`. Citations are GFM links into `sources.md` (`[ID](sources.md#id)`, lowercase
anchor) — see `agents/synthesizer.md` and `scripts/link_normalizer.py`. Use GFM tables with
explicit alignment markers (`:--` left, `:-:` center, `--:` right) and variable, content-sized
column widths (never fixed-width padding). Lint each generated `.md` with the `yf-markdown-lint`
authoring subset (`ML001,ML002,ML005,ML006,ML007,ML008`) and resolve any violation before handoff.

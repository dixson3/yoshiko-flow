# SPEC — Skill Authoring (`yf-skill-authoring`)

> **Status: Active.** Per-skill SPEC for the skill-authoring conventions. The `yf-skill-authoring` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-skill-authoring` is the conventions skill for authoring Claude Code **skills, agents, and
instruction files**: directory layout, the inline-vs-script threshold, modularization, the
**token-efficient writing ruleset** (the canonical Cut/Keep/Extract rules other skills reference),
the Skill Surface Convention, **Python helper conventions** (uv invocation discipline, PEP 723
inline deps, argument parsers), the canonical agent-role vocabulary, and the read-only review
sequence. It is `user-invocable: false` — a conventions reference applied when authoring skill-dir
content. It is the **single source of truth for the token-efficiency ruleset**.

**In scope:** skill-dir instruction files (a skill's `SKILL.md`, `agents/*.md`, a skill's own
`.{claude,agents}/rules/*`), the Surface Convention's seven-point contract, the script/modularize
thresholds, Python helper discipline, and the review-agent set.

**Out of scope:** **project-root** instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*` NOT
inside a skill dir, repo-root `.{claude,agents}/rules/*`) — those route to
`yf-optimal-instructions`. Also application code outside skills, end-user docs, the *structural*
project-root convention (AGENTS-primacy / CLAUDE-index — owned by `yf-optimal-instructions`),
and design-level skill planning (the planning skill). Content-agreement verification across edges
is `yf-drift-check`'s axis.

## 2. Requirements (`REQ-SKAUTH-NNN`)

### 2.1 Layout & thresholds

- **REQ-SKAUTH-001** a skill shall root at `.{claude,agents}/skills/<skill>/` with `SKILL.md` as
  the entry point and helpers/modules adjacent to it.
- **REQ-SKAUTH-002** *(testable)* the script threshold shall hold: inline glue stays inline;
  scripts >~25 lines or reused move to a file under the skill dir; logic >~200 lines factors into
  modules; CLI entrypoints use a real argument parser, never ad-hoc `sys.argv` slicing.

### 2.2 Token-efficiency ruleset (canonical — referenced by `yf-optimal-instructions`)

- **REQ-SKAUTH-010** *(testable)* this skill shall be the **single source of truth** for the
  Cut / Keep / Extract token-efficiency ruleset; other skills (notably `yf-optimal-instructions`'
  K1) cite the "Token efficiency" § anchor and shall not restate it.
- **REQ-SKAUTH-011** the ruleset shall govern always-loaded context (`SKILL.md`, `CLAUDE.md`,
  `AGENTS.md`, `.{claude,agents}/rules/*`): **Cut** narrative/soft-guidance/decorative content,
  **Keep** literal templates / verbatim commands / behavioral & edge-case constraints / state
  transitions / agent output structures, **Extract** JSON-parsing bash and >~15-line one-phase
  behavior to scripts/agents.
- **REQ-SKAUTH-012** the *structural* project-root convention (AGENTS.md primary, CLAUDE.md a thin
  `@-include` index, behavioral rules in the rules subdir) is **owned by
  `yf-optimal-instructions`**, not here; this skill references it.

### 2.3 Skill Surface Convention (see `reference/SURFACE_CONVENTION.md`)

- **REQ-SKAUTH-020** *(testable)* a skill adopting the Surface Convention shall adopt all seven
  points or none: (1) companion rules sourced from `protocols/<NAME>.md`, installed by the repo
  installer to the scope+surface rules dir, never to `AGENTS/`, never editing `CLAUDE.md`;
  (2) a `protocols/manifest.json` hash manifest with the six preflight outcomes; (3) canonical
  per-repo config `.yf/<short>/config.local.json` (`<short>` = `yf-`-stripped name), with the
  legacy root dotfile `.<skill>.local.json` read only as a fallback; (4) runtime state under
  `.yf/<short>/` only; (5) hook installation via `hooks/manifest.json` merged by `<skill> init`;
  (6) a single anchored `/.yf/` gitignore entry; (7) the preflight contract (checks + idempotent
  scaffold; `yf migrate`, not preflight, moves legacy paths).
- **REQ-SKAUTH-021** *(testable)* an unknown `schema_version` in `protocols/manifest.json` shall
  make preflight FAIL.
- **REQ-SKAUTH-022** config shall be operator decisions only; **state ≠ config**, and runtime
  state shall never be written under the skill source dir or under `.{claude,agents}/`.

### 2.4 Python helper conventions

- **REQ-SKAUTH-030** *(testable)* skill helper scripts shall run via `uv run` — never a direct
  `python` / `python3` call and never a manually activated virtualenv.
- **REQ-SKAUTH-031** single-file helpers shall declare dependencies inline via PEP 723
  (`# /// script ... ///`); escape to an explicit `uv venv` + `requirements.txt`/`pyproject.toml`
  inside the skill dir only when dep count >~10 or specific pins matter.
- **REQ-SKAUTH-032** *(testable)* CLI argument parsing shall use `click`, `typer`, or stdlib
  `argparse` — never `sys.argv` slicing.
- **REQ-SKAUTH-033** helpers that persist runtime state shall write to `.yf/<short>/` (`<short>` =
  `yf-`-stripped skill name) resolved from a caller-supplied `project_root`, not a hardcoded cwd.

### 2.5 Agent roles & review (see `reference/AGENT_ROLES.md`, `reference/PIPELINE.md`)

- **REQ-SKAUTH-040** every agent in a multi-agent skill shall map to exactly one of six canonical
  roles (GATHER, PRODUCE, EVALUATE, REVISE, ORCHESTRATE, CLOSEOUT) and carry a front-matter block
  declaring it; EVALUATE agents additionally carry a `stance` (`reviewer` | `red-team`); the
  bead-DAG driver is always `coordinator`.
- **REQ-SKAUTH-041** the review sequence shall be three read-only agents dispatched via the Agent
  tool, the caller applying fixes: `reviewer` (general), `reviewer-tokens` (skill-dir
  instruction-file token efficiency), `red-team` (adversarial); for Python helpers, also
  `reviewer-python`.
- **REQ-SKAUTH-042** *(testable)* every markdown file a skill ships (`SKILL.md`, `agents/*.md`,
  `README.md`, `spec/*.md`, `reference/*.md`) shall be plain **GFM** — never Obsidian
  `[[wikilinks]]` or `![[embeds]]`, GFM links and tables (explicit alignment markers) only — and
  every authored/edited `.md` shall be linted with the `yf-markdown-lint` authoring subset
  (`ML001,ML002,ML005,ML006,ML007,ML008,ML010`) with all violations resolved before the skill is
  considered done; this lint gate is part of the review sequence (REQ-SKAUTH-041), not optional.

### 2.6 Spec diagrams (conditional)

- **REQ-SKAUTH-050** when a diagram aids a skill's `SKILL.md`/spec, the author SHOULD use the
  `yf-diagram-authoring` skill, co-resident at `skills/<name>/spec/<slug>.{d2,png}`, referenced
  from the README by relative path; this is conditional (no `depends-on-skill` edge), degrading to
  prose if `d2` is absent. A new `spec/<slug>.{d2,png}` must be listed in the README layout fence
  (the `e-readme-layout` `field-set-equal` coupling).

### 2.7 Routing

- **REQ-SKAUTH-060** **project-root** instruction files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*` not
  inside a skill dir, repo-root `.{claude,agents}/rules/*`) shall **route to
  `yf-optimal-instructions`**; this skill owns only **skill-dir** instruction files. The two
  skills' `description` fields are mutually exclusive on this axis.

### 2.8 Description rating & trigger evals (added plan-072 / #407)

The hard length limits are root `SPEC.md` `REQ-YF-EMBED-007` (description ≤1024, the Agent
Skills `name` rule). The two requirements below cover the next question: **does the description
still route correctly?** The description is the routing surface. Several descriptions carry
deliberate negative routing between siblings, so a trim is measured, not assumed.

- **REQ-SKAUTH-061** *(testable, added plan-072)* every shipped skill shall carry a
  **four-state description rating**. It is derived from the recorded per-intent trigger rates in
  `skills/<name>/evals/triggers.json` (≥3 reps per intent, both harnesses, candidate mode, per
  `REQ-SKAUTH-062`). It is never hand-asserted:

  | Rating | Description length | Trigger rates |
  | :-- | :-- | :-- |
  | **crisp** | ≤600 | every intent ≥0.5 on both harnesses |
  | **satisfactory** | ≤1024 | every intent ≥0.5 on both harnesses |
  | **unrouted** | ≤1024 | some intent <0.5 on some harness |
  | **loose** | >1024 | (fails `REQ-YF-EMBED-007`) |

  Length uses `REQ-YF-EMBED-007`'s unit (UTF-16 code units of the parsed scalar). **New skills
  shall target crisp.** A skill that is not crisp after a best-effort trim, or that is unrouted,
  gets a recorded **split proposal** put to the operator. On decline, the operator's decision is
  recorded in `triggers.json` with a reason and date. For an unrouted skill, the decision also
  names the **accepted-miss intent ids**. Such a skill reports as
  `satisfactory (accepted misses: <ids>)`, so the misses stay visible, and its accepted cells
  never fail the FULL tier.

- **REQ-SKAUTH-062** *(testable, added plan-072)* the **trigger-eval contract**, implemented by
  `scripts/checks/skill_trigger_eval.py`:
  - **Intent schema.** Per skill, `evals/triggers.json` lists *should-trigger* intents (a prompt,
    optionally a fixture establishing a precondition) and *near-miss* intents (a prompt that
    should **not** activate the named sibling skills). It also holds the last **recorded**
    per-harness rates, the sha256 of the description they were measured against, and operator
    acceptances.
  - **Detector.** A skill counts as activated when the run makes a CC `Skill` tool call naming
    it, or a tool call whose arguments touch `<staging-root>/<n>/`, an installed `skills/<n>/`,
    or `yf skill-dir <n>`. The staging root is an explicit detector input. The repository's own
    `skills/<n>/` is **never** counted, because reading source is not activation. *(Amended
    plan-072 Issue 3.3, measured.)* On CC, a **slash-command expansion** is also activation: the
    session transcript records `<command-name>/<n></command-name>`, or the expanded body's
    `Base directory for this skill: <staging-root>/<n>`. Neither appears in the stream as a tool
    call, so the detector reads the transcript for it after the run exits.
  - **Eval environment.** The run cannot make an outward-facing write: `gh` gets an empty config
    and no token. *(Amended plan-072 Issue 3.3.)* herdr is **simulated, not reachable**:
    `HERDR_ENV=1` is set, because that is the precondition a herdr-scoped skill routes on in real
    use, and `HERDR_SOCKET_PATH` points at a path that does not exist, so no herdr command reaches
    a live server.
  - **Stop rule.** A run stops on activation, at 6 tool calls, or at 150 s, so the eval measures
    routing rather than doing the task.
  - **Modes.** **candidate** stages every `skills/*/` from the checkout under test into a fresh
    staging directory, cleared at every reset. pi runs `--no-skills --skill <staging>/<n>` per
    skill. CC runs with the staging directory at `<clone>/.claude/skills/`, plus
    `--setting-sources project --permission-mode bypassPermissions --debug-file <log>`. **CC load
    verification:** the run's debug log shall contain `Loaded <N> unique skills (… user: 0,
    project: <N> …)` with N equal to the staged count. The init event shall report
    `permissionMode == bypassPermissions`, and its `skills` shall be a superset of the staged
    **user-invocable** names. That is a subset check, because init lists only user-invocable
    skills. A sha256 of every staged file shall be taken immediately before launch. pi's stream
    carries each description, so pi is hashed directly. Any mismatch is INCONCLUSIVE. *Stated
    limitation:* on CC this proves the staged **files** loaded and nothing else did. It does not
    prove the literal text the model saw. **installed** mode uses the operator's full
    configuration and is used only after deploy.
  - **Cell rate.** A cell is (skill × intent × harness). Its rate is the fraction of reps with
    the **correct** outcome: for a should-trigger intent, the expected skill activated; for a
    near-miss, none of its named siblings activated **as the route**. *(Amended plan-072 Issue
    3.3, measured.)* Activation is **first-activation-routes**: the skill a run activates first is
    its route. A named sibling that activates only **after** the correct route did not take the
    route. A skill that is routed to correctly often reads a sibling's conventions (for example,
    `yf-optimal-instructions` reading `yf-skill-authoring`'s token-efficiency section), and that
    read is not a misroute. So a near-miss is wrong only when a named sibling is the **first**
    activation. Should-trigger scoring is unchanged: the expected skill activating at any point is
    correct.
  - **Spend ledger.** Every run appends one JSON line to `--ledger <path>`: harness, tokens
    (input / cache-write / cache-read / output) and `cc_usd` (a number, `0` for pi rows, never
    null). **CC tokens** come from the session transcript
    `~/.claude/projects/<cwd-slug>/<session-id>.jsonl` **plus every
    `<session-id>/subagents/*.jsonl`**. The run is started with `--session-id <uuid>` and read
    after exit. Each file is deduplicated by `message.id`, with the last usage per id winning.
    They are never taken from the stream `result` event, which a killed run does not emit, and
    never from the raw stream sum, which repeats usage per content block. **CC USD** = tokens ×
    per-class rates from `scripts/checks/trigger_eval_rates.json`, keyed by model. For
    `claude-opus-5-5` the rates are: input $4.00/Mtok, cache-write 1h $8.00, cache-write 5m
    $5.00 (from `usage.cache_creation.ephemeral_{1h,5m}_input_tokens`), cache-read $0.20, output
    $20.00. A model absent from the table is INCONCLUSIVE, never $0. pi reports tokens only.
    `--budget-usd N` reads the ledger's **cumulative** CC total, so a ceiling holds across
    invocations. On reaching it the harness stops and exits 4.
  - **Listing budget.** Claude Code's `Skill listing over budget` WARN is recorded in **installed
    mode only**: a 20-skill candidate listing cannot reach the budget.
  - **FULL-row verdict.** Evaluate every cell at 3 reps. Re-run 3 more reps for any cell below
    0.5 **whose recorded rate was ≥0.5**. FAIL only if the pooled 6-rep rate is still <0.5, which
    is a regression. Cells recorded as operator-accepted misses never FAIL. **Stated false-FAIL
    rate:** a cell false-FAILs when its first 3 reps have a ≤ 1 correct outcomes and the pooled 6
    have a + c ≤ 2 (c = correct outcomes in the 3 confirmation reps). So q = Σ_{a≤1} Σ_{c≤2−a} Bin(3,p)(a)·Bin(3,p)(c), and the tier rate is
    1 − (1 − q)^N over N cells. That is ≈1.65% at N=240, p=0.95, and ≈21.9% at N=240, p=0.90.
    `--report` prints the actual N and the implied rate.
  - **Other verdicts.** INCONCLUSIVE (exit 4) when a harness binary or its auth is missing, or on
    any staging or load-verification mismatch. PASS (exit 0) only on a completed run. FAIL is
    exit 1.
  - **Throttling and invalid runs** *(amended plan-072 Issue 3.2 incident, operator decision
    "throttle the runs — there are always other sessions active")*. The two harnesses and any
    other session on the machine can share **one model-account quota**. Measured: pi reaches the
    same Claude account through a proxy, and an unthrottled baseline at ~381 runs/h tripped it
    after 1.6 h. The harness had then scored 14 rate-limited CC runs (0 tokens, ~1.6 s) as real
    outcomes. Four rules follow:
    - *(i) A run that measured nothing is INCONCLUSIVE, structurally.* A run that consumed
      **zero tokens**, or whose output carries a rate-limit / HTTP 429 / cooldown signature, is
      never scored and never recorded.
    - *(ii) One global throttle.* `--max-runs-per-hour N` bounds run **starts** across both
      harnesses together, because they share the quota. The default is conservative (150/h,
      about 40% of the rate that tripped) to leave headroom for other sessions.
    - *(iii) Adaptive backoff.* On a rate-limit signature, **both** harnesses pause. The pause is
      the `reset_seconds` from the 429 body when present, otherwise exponential backoff. The rate
      is then halved, and the run is retried rather than recorded. The total wait is bounded by
      `--max-backoff-seconds`. Exceeding the bound stops the run at exit 4 (INCONCLUSIVE).
    - *(iv) Crash-safe resume.* Every valid per-run result is appended to `--results <jsonl>` as
      it completes. `--resume <jsonl>` skips runs already present there, keyed by (harness,
      intent, rep), and counts them toward the cells, so an interrupted baseline continues
      rather than restarts. A process-group kill of an already-exited run is not an error.
  - **Writers.** Only an explicit `--record` run writes `triggers.json`. The FULL-tier row is
    read-only.

  **The FULL validation tier carries this eval** (candidate mode, every skill, both harnesses, 3
  reps) as its last row, flagged `inconclusive-exit=4,stream` (`REQ-ENGINE-011`). That is
  roughly 3 h and $75–110 at CC list rates per FULL run. The cost is operator-accepted: a trim
  that silently loses routing is invisible without it.

## 3. Interfaces

- **CLI / scripts:** `scripts/manifest_update.py` — recomputes companion-rule sha256, bumps semver,
  appends to `previous_versions[]`; each adopting skill vendors a copy into its own `scripts/`.
  No domain CLI (this skill is conventions, not a runtime engine).
- **Review agents:** `agents/reviewer.md`, `agents/reviewer-tokens.md`, `agents/red-team.md`,
  `agents/reviewer-python.md` — read-only, dispatched via the Agent tool; the caller applies fixes.
- **Companion rule:** **none** (the conventions are loaded on demand when authoring skill-dir
  content; there is no always-loaded trigger rule for this skill).
- **Config / state:** none for the skill itself; it *defines* the `.yf/<short>/config.local.json`
  config and `.yf/<short>/` state conventions (legacy root dotfile `.<skill>.local.json` read as a
  fallback) that adopting skills follow.

## 4. Guardrails (`GR-SKAUTH-NNN`)

- **GR-SKAUTH-001** *Drift:* restating the token-efficiency ruleset, or claiming the project-root
  structural convention. *Rule:* this skill is the single source of the Cut/Keep/Extract ruleset;
  the AGENTS-primacy / CLAUDE-index structure is owned by `yf-optimal-instructions` and only
  referenced here. *Why:* one-source-of-truth — the ruleset must have exactly one home.
- **GR-SKAUTH-002** *Drift:* claiming project-root instruction files. *Rule:* this skill owns
  **skill-dir** instruction files; project-root files route to `yf-optimal-instructions`. *Why:*
  the two skills are mutually exclusive on the skill-dir vs project-root axis.
- **GR-SKAUTH-003** *Drift:* the review agents editing files. *Rule:* all review agents are
  **read-only**; the caller applies fixes. *Why:* auditable, deterministic review.

## 5. Verification

- The toolchain rules (REQ-SKAUTH-030/032) and the script threshold (REQ-SKAUTH-002) are checkable
  by linting/inspecting any adopting skill's helpers; the Surface Convention points
  (REQ-SKAUTH-020/021) by the preflight outcomes of an adopting skill. The single-source-of-truth
  invariant (REQ-SKAUTH-010, GR-SKAUTH-001) is verified by grep — the ruleset appears only here,
  cited (not restated) by `yf-optimal-instructions`. Each *(testable)* REQ is the anchor a
  plan-010 Epic 6 integration test names.

## 6. References

- `skills/yf-skill-authoring/SKILL.md` (layout, thresholds, Surface Convention summary, token
  efficiency §, Python helpers, agent roles, review sequence).
- `skills/yf-skill-authoring/reference/SURFACE_CONVENTION.md` (full seven-point contract + worked
  example), `reference/PORTABILITY.md` (`SKILL_DIR` resolution + portability checklist),
  `reference/PIPELINE.md` (multi-agent conventions), `reference/AGENT_ROLES.md` (role vocabulary,
  factoring test, front-matter schema, role table).
- `skills/yf-skill-authoring/agents/*.md` (the review agents); `scripts/manifest_update.py`.
- Root `SPEC.md` §4 (SKAUTH) and `GUARDRAILS.md` (GR-006, per-skill guardrails note).

## 7. Amendment log

- **plan-072 (2026-09-25, #407):** added `REQ-SKAUTH-061` (the four-state description rating)
  and `REQ-SKAUTH-062` (the trigger-eval contract, including the FULL-tier eval row). Root
  `SPEC.md` carries the matching entry, along with `REQ-YF-EMBED-007`, the hard length rule.

# SPEC — Research (`yf-research`)

> **Status: DRAFT (primed).** Per-skill SPEC for the research skill (currently `bdresearch`, renamed
> to `yf-research` by plan-010). Operator to review/edit. Composed by the root macro `SPEC.md` §4
> under spec key **RESEARCH**. Requirement-numbered layer that **references** the topical design
> docs under `spec/*.md` rather than restating them.

## 1. Purpose & scope

`yf-research` is a multi-phase, beads-tracked deep-research pipeline: it decomposes a topic into a
DAG of focused subtasks (retrieve → triangulate → synthesize → critique → refine → package) and
produces a structured, citation-backed report with source-credibility scoring. It coexists
deliberately with the built-in `deep-research` harness — `yf-research` is for results that should be
tracked, cited, or resumable.

**In scope:** the research phase pipeline, the subtask DAG, source credibility scoring, the
epistemic rules, the `coordinate` loop with gate auto-detection, and portable research outputs.

**Out of scope:** quick throwaway same-turn lookups (use the built-in harness), issue storage (that
is `bd`), and build planning (that is `yf-plan`).

## 2. Requirements (`REQ-RESEARCH-NNN`)

### 2.1 Lifecycle & phases (see `spec/phases.md`)

- **REQ-RESEARCH-001** *(testable)* a research project shall decompose into a DAG of subtasks across
  the phases retrieve → triangulate → synthesize → critique → refine → package.
- **REQ-RESEARCH-002** *(testable)* every invocation except `init` shall run the preflight (`check`)
  and branch on `ok | ignored | system_deps_missing | bd_not_initialized | rule_*`.
- **REQ-RESEARCH-003** the pipeline shall be resumable across sessions via the `coordinate`
  subcommand with gate auto-detection.

### 2.2 Outputs & portability (see `spec/portability.md`, `spec/data.md`)

- **REQ-RESEARCH-010** *(testable)* outputs shall be versioned directories under
  `docs/research/<NNN>-<slug>/` (or `Incubator/<slug>/research/<NNN>-<slug>/`); the `NNN` index is
  global across both roots so cross-references stay unambiguous.
- **REQ-RESEARCH-011** a research directory shall be self-contained and portable (a cold reader in
  another repo can understand it from the folder alone).

### 2.3 Epistemics (see `spec/epistemics.md`)

- **REQ-RESEARCH-020** *(testable)* every asserted claim in the report shall carry a citation — no
  uncited assertions.
- **REQ-RESEARCH-021** direct quotes shall be preferred over paraphrase for load-bearing evidence.
- **REQ-RESEARCH-022** **absence of evidence shall be a valid, recordable finding.**
- **REQ-RESEARCH-023** *(testable)* sources shall be credibility-scored (`credibility_scorer.py`),
  and the score shall be visible in the synthesis.

### 2.4 Agents & coordination (see `spec/agents.md`)

- **REQ-RESEARCH-030** retrieval/synthesis/critique agents shall be dispatched per subtask; the
  critique pass shall be adversarial and may send the pipeline back to refine/retrieve.
- **REQ-RESEARCH-031** the `coordinate` loop shall resolve the active gate, drive ready subtasks to
  completion, and be crash/resume-safe (reset stuck subtasks; never auto-close the unclassifiable).

### 2.5 Git authority

- **REQ-RESEARCH-040** git authority shall be **conservative** — the pipeline reports a git handoff
  (changed files + proposed commit/sync/push) and does not commit or push without explicit
  authorization.

## 3. Interfaces

- **CLI / scripts:** `scripts/research_manager.py` (preflight `check`, project lifecycle),
  `index_manager.py`, `credibility_scorer.py`, `link_normalizer.py`, `search_api.py`. Surface in
  `spec/cli.md`; data shapes in `spec/data.md`. **Preflight/config moves to `yf`** per macro
  `REQ-YF-PRE-*`; domain logic stays in Python.
- **Companion rule:** `protocols/RESEARCH.md` (+ `protocols/manifest.json`, sha256+semver) — the
  always-loaded routing/trigger contract (bdresearch vs built-in deep-research); verified by the
  preflight `rule_*` outcomes.
- **Config / state:** `.yf-research.local.json` (operator config incl. `ignore-skill`); runtime
  state under `.yf/yf-research/`. Legacy `.bdresearch.local.json` / `.state/bdresearch/` migrate via
  macro `REQ-YF-MIGRATE-001`.

## 4. Guardrails (`GR-RESEARCH-NNN`)

- **GR-RESEARCH-001** *Drift:* overriding the built-in `deep-research` harness. *Rule:* the two
  coexist; `yf-research` is chosen by intent (tracked/cited/resumable), it does not replace the
  built-in. *Why:* the built-in is compiled into the CLI and serves quick lookups.
- **GR-RESEARCH-002** *Drift:* uncited or paraphrase-only claims. *Rule:* every claim is cited;
  absence is a finding (REQ-RESEARCH-020/022). *Why:* epistemic integrity is the product.
- **GR-RESEARCH-003** *Drift:* auto-committing/pushing research outputs. *Rule:* conservative git
  authority — report and await authorization. *Why:* the operator owns the remote.

## 5. Verification

- Epistemic + portability invariants are checked by `research_manager.py` audits and the citation/
  credibility presence checks. Preflight parity (REQ-RESEARCH-002) is verified by the macro spec's
  Epic 6.3 fixtures once preflight moves to `yf`.

## 6. References

- `skills/bdresearch/SKILL.md`; `spec/phases.md`, `spec/agents.md`, `spec/cli.md`, `spec/data.md`,
  `spec/epistemics.md`, `spec/portability.md`, `spec/prerequisites.md`.
- `protocols/RESEARCH.md`.
- Root `SPEC.md` §4 (RESEARCH) and `GUARDRAILS.md` (GR-002, GR-005).

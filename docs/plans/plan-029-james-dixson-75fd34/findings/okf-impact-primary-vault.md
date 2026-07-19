# OKF-* Impact Assessment — Primary Obsidian Vault

Issue 2.2 of plan-029. A **read-only** impact assessment of the OKF-* conversion
(the baked-in `_shared/okf.py` engine) against the real personal corpus at
`~/Documents/Obsidian/Primary`.

## Safety note (Risk R8) — the live vault was not touched

- **All engine operations ran against a scratch snapshot, never the live vault.**
  The snapshot lives at
  `…/scratchpad/vault-snapshot/` (created with `rsync -a --exclude '.git'`).
- **`.git` was excluded** from the snapshot to save space (the live `.git` is 53 MB
  of the 483 MB vault). No engine op needs history, so this is safe; it means the
  snapshot is the working tree only.
- Snapshot verified non-empty: **6422 files, 430 MB**.
- Only two `okf.py` verbs were used: `check` and `migrate --dry-run`. One
  **`migrate` without `--dry-run`** was run to prove merge-and-preserve, and it was
  run against a **throwaway copy of a single bundle inside the scratch area**
  (`…/scratchpad/merge-test-bundle`), never the snapshot bundle and never the live
  vault.
- **Live-vault integrity confirmed:** `git -C ~/Documents/Obsidian/Primary status
  --porcelain` was empty (clean) both before and after all work. The live vault is
  byte-unchanged.

## Engine and invocation

- Engine (worktree, not installed):
  `…/.worktrees/plan-029-james-dixson-75fd34/_shared/okf.py`, invoked as
  `env -u VIRTUAL_ENV uv run <okf.py> …`.
- The engine operates on **one bundle dir per invocation** (`rglob("*.md")` within
  that dir); it does not walk a tree of bundles. The driver enumerated every bundle
  and invoked `check` + `migrate --dry-run` per bundle with the matching `--skill`
  (`yf-plan` → OKF-PLAN, `yf-research` → OKF-RESEARCH, `yf-incubator` →
  OKF-INCUBATOR). All three `skills/<skill>/OKF-EXTENSION.md` files resolved and
  composed correctly (`rulesets_composed` showed the three-member chain per type).

## Vault corpus inventory

The vault uses the **two-root model** this repo describes, plus per-incubator
sub-roots. Discovered bundles (179 total):

| Type | Count | Roots found |
| :--- | ---: | :--- |
| yf-plan | 62 | `docs/plans/plan-*/`, `Incubator/<slug>/plans/plan-*/`, `Incubator/<slug>/docs/plans/plan-*/` |
| yf-research | 65 | `docs/research/NNN-*/`, `Incubator/<slug>/research/NNN-*/`, `Incubator/<slug>/business-plan/research/NNN-*/` |
| yf-incubator | 52 | `Incubator/<slug>/` (dir-form) + one single-file `Incubator/INDEX.md` |

Total `.md` scanned across bundles produced **5030 check findings** and **0 crashes**.

### How the vault differs structurally from this repo

- **Foreign/older reserved-file convention.** The vault uses `README.md` (81 in
  bundles) and `_index.md` (30, research-specific) as index files. There are **zero**
  OKF-reserved `index.md` and **zero** `log.md` files anywhere — the vault predates
  the OKF reserved-name model entirely. This is the single biggest divergence and
  drives most findings.
- **Legacy plan phase-log.** 29 `plan.md` files carry an in-body `**Phase log:**`
  block (the pre-OKF log location the engine's `move-phase-log` targets).
- **Deep incubator nesting.** Incubators nest plans and research under multiple
  sub-roots (`Incubator/llm-proxy-for-pi/docs/plans/` *and*
  `Incubator/llm-proxy-for-pi/plans/`, `Incubator/bookpipe/business-plan/research/`),
  which this repo's flat two-root description does not enumerate. Discovery handled
  them by globbing on `plans/plan-*` and `research/NNN-*` rather than assuming fixed
  paths.
- **Rich Obsidian frontmatter.** 521 files carry Obsidian keys (`tags`, `aliases`,
  `cssclass`/`cssclasses`, `title`, `status`, `created`) — the foreign-corpus case
  the merge-and-preserve REQ exists for.

## Per-type impact (aggregate dry-run change set)

Across all 179 bundles the `migrate --dry-run` change plan totals:

| Op | Count | Meaning |
| :--- | ---: | :--- |
| `add-frontmatter` | 1411 | add `type: Concept` + `okf_spec: OKF-<MEMBER>` to a non-reserved `.md` lacking them |
| `rename` | 104 | `README.md` → `index.md` |
| `move-phase-log` | 56 | extract `plan.md` `**Phase log:**` block → `log.md`, preserving first scoping date |
| `skip` / `error` | 0 | (no un-processable files reached the migrate write path) |

Aggregate `check` findings (all bundles fail check — expected for un-migrated legacy):

| Level | REQ | Count | What it flags |
| :--- | :--- | ---: | :--- |
| error | REQ-OKF-FAM-001 | 1664 | missing per-skill required key / type not in vocab |
| error | REQ-OKF-003 | 1540 | non-reserved `.md` with no frontmatter or empty `type` |
| error | REQ-OKF-030 | 1074 | missing `okf_spec` member key |
| error | REQ-OKF-010 | 393 | a `**Field:**` line sits below the first `## ` |
| error | REQ-OKF-001 | 179 | reserved `index.md` missing (one per bundle) |
| error | REQ-OKF-002 | 179 | reserved `log.md` missing (one per bundle) |
| error | REQ-OKF-071 | 1 | malformed-YAML report (crash-safe path — see hazards) |

### Representative dry-run excerpts

Plan bundle `docs/plans/plan-011-james-dixson-d1496b` (member OKF-PLAN):

```json
{"op": "rename", "path": "README.md", "to": "index.md"}
{"op": "move-phase-log", "path": "plan.md", "to": "log.md", "first_scoping_date": "2026-04-23"}
{"op": "add-frontmatter", "path": "context.md", "keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
```

Research bundle `docs/research/004-jumpcloud` (member OKF-RESEARCH) — **no rename**
because it uses `_index.md`, not `README.md`:

```json
{"op": "add-frontmatter", "path": "Summary.md", "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
{"op": "add-frontmatter", "path": "_index.md", "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
```

Incubator bundle `Incubator/CodeMage` (member OKF-INCUBATOR):

```json
{"op": "rename", "path": "README.md", "to": "index.md"}
{"op": "add-frontmatter", "path": "00Index.md", "keys": {"type": "Concept", "okf_spec": "OKF-INCUBATOR"}}
```

## Foreign-corpus hazards

### Merge-and-preserve (REQ-OKF-070) — VERIFIED, values preserved

Proven by a **real** (non-dry-run) migrate on a disposable copy of research bundle
`harness-survey/research/011-antigravity-vs-gemini-cli`. Before, `Summary.md`
frontmatter:

```yaml
---
title: "Antigravity vs Gemini CLI: harness drivability and lock-in"
created: 2026-05-20
tags: [research, harness, agents, gemini, antigravity, claude-code]
status: draft
---
```

After migrate:

```yaml
---
title: 'Antigravity vs Gemini CLI: harness drivability and lock-in'
created: 2026-05-20
tags:
- research
- harness
- agents
- gemini
- antigravity
- claude-code
status: draft
type: Concept
okf_spec: OKF-RESEARCH
---
```

**Verdict: PASS.** Every pre-existing Obsidian key (`title`, `created`, `tags`,
`status`) survives with its value; only `type` and `okf_spec` are appended. The
dry-run change plan correctly reported *only* `keys: {type, okf_spec}` — it never
proposed dropping or overwriting an existing key.

**One non-blocking nuance (not a bug):** the write path re-serializes the *entire*
frontmatter block through PyYAML `safe_dump`, so the untouched keys are cosmetically
reformatted — flow-style `tags: [a, b]` becomes a block list, and double quotes
become single quotes. Values are semantically identical (same list, same string), so
this is not data loss and not a REQ-OKF-070 violation. But it does mean the migrate
step is **not byte-hash-neutral for the pre-existing frontmatter block** (REQ-OKF-MIG-003's
"hash-neutral" claim holds for body content below the frontmatter, not for the
re-dumped YAML). Obsidian users will see their frontmatter reflowed. Worth a note in
the conversion plan; does not reopen Issue 1.4.

### Crash-safety (REQ-OKF-071) — VERIFIED, never crashed

- **0 crashes** and **0 stderr tracebacks** across all 179 bundles × 2 verbs (358
  invocations). Every invocation returned parseable JSON.
- The one malformed-YAML case, `Incubator/frontier-model-specs/README.md`, was
  **reported, not thrown**. Its frontmatter opens with `---` but the body is a
  Markdown link list that YAML cannot parse. `check` recorded:

  ```
  REQ-OKF-071 error README.md: malformed frontmatter: while parsing a block
  collection … expected <block end>, but found '<scalar>' … - [epoch.ai/data/ai-models](https://…)
  ```

  This is exactly the report-only contract — a foreign file that looks like it has
  frontmatter but does not, handled without a stack trace.

**Verdict: PASS.** The engine is report-only and crash-safe on this messy real corpus.

### Single-file incubator exemption (REQ-OKF-050) — VERIFIED

`check Incubator/INDEX.md --skill yf-incubator` (a lone `.md`) produced **only** a
concept-doc finding (`REQ-OKF-003` missing frontmatter). It did **not** demand a
reserved `index.md`/`log.md` — the single-file-bundle exemption fired. (Note the
filename `INDEX.md` is uppercase, so it is not the reserved lowercase `index.md`; the
engine treats it as a single-file concept doc, which is correct.)

**Verdict: PASS.**

### Wikilinks / embeds — out of scope, correctly untouched

16 bundle files contain `[[…]]` / `![[…]]`. Migration **never touches body content**:
the only ops are `rename`, `move-phase-log`, and `add-frontmatter` (all confined to
the frontmatter block above the first `## `). No change op rewrites or flags a
wikilink. This is the correct behavior — OKF/yf uses plain GFM, but migrating the
vault would leave existing wikilinks as-is (they would remain non-GFM, a separate
concern for `yf-markdown-lint`, not for this conversion). No divergence beyond noting
their presence.

### Different-yf-flow-version divergence — CONFIRMED

The vault runs an **older/foreign yf-flow layout** than this repo's OKF model:

- Index files are `README.md` and `_index.md`; the OKF reserved `index.md`/`log.md`
  do not exist yet (0 present). The base `migrate` only produces `index.md` by
  renaming `README.md`, and only produces `log.md` by moving a `plan.md`
  `**Phase log:**` block. Therefore, after a base-engine migrate:
  - **research bundles that use `_index.md`** (not `README.md`) get **no `index.md`
    created** and their `_index.md` is stamped with `type:` as an ordinary concept
    doc — so `check` would still report `REQ-OKF-001`/`REQ-OKF-002` for them.
  - bundles with no `**Phase log:**` block get **no `log.md`** — `REQ-OKF-002`
    persists.

  This is a **migration-completeness gap**, not a crash or misreport: the base
  `okf.py migrate` does not fully make the vault's `_index.md`-convention research
  bundles (or any log-less bundle) conformant on its own. Producing the reserved
  files in the general case appears to be left to the per-skill adapters, which are
  not exercised here. Flagged for Issue 2.3 to decide whether the conversion plan
  needs adapter-level reserved-file scaffolding or a `_index.md`→`index.md` rename
  rule; it does **not** reopen Issue 1.4 (the engine behaves as coded).

## Engine-level findings

**No engine bugs found.** No crash, no misreport:

- Merge-and-preserve did not drop or overwrite any foreign key (PASS).
- Crash-safety held on malformed YAML and across 358 invocations, 0 tracebacks (PASS).
- Single-file exemption fired (PASS).

The only items to carry to Issue 2.3 are **non-bug observations**, both about
migration *completeness/cosmetics* rather than the engine misbehaving:

1. Migrate re-serializes existing frontmatter (flow→block, quote normalization) —
   values preserved, but not byte-neutral for the frontmatter block.
2. Base migrate does not create `index.md`/`log.md` for the vault's
   `_index.md`-convention research bundles or for log-less bundles, so `check` still
   fails those after a base migrate — reserved-file scaffolding for the general case
   is out of the base engine's scope.

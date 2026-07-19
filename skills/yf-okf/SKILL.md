---
name: yf-okf
description: "Constructs, manages, and conformance-checks the OKF-compatible artifact folders
  ('bundles') that yf artifact-producing skills emit (yf-plan, yf-research, yf-incubator), and
  owns the versioned OKF-* spec family (BASELINE + YF-EXTENSIONS + per-skill OKF-EXTENSION). The
  engine (okf.py) composes the effective ruleset and runs check (report-only conformance) and
  migrate (opt-in, per-folder, in-place). TRIGGER when: /yf-okf invoked (init | check | migrate |
  assess); checking whether an artifact folder conforms to the OKF model; migrating a legacy
  plan/research/incubator folder to the reserved index.md + log.md + frontmatter+type model; or
  running an impact assessment of a corpus before adopting OKF. SKIP for: authoring third-party
  OKF linters / validators / MCP servers (yf-okf is a producer/manager plus a conformance
  self-check, not a third-party validator); checking that already-written docs AGREE across
  declared edges (that is yf-drift-check, an orthogonal axis); running a repo's build/test/lint
  recipe (yf-change-validation). yf-okf never fires on an ordinary edit — it is operator-invoked."
user-invocable: true
skill-group: utility
depends-on-tool: [uv]
depends-on-skill: []
allowed-tools:
  - Read
  - Grep
  - Bash
  - Agent
title: yf-okf
created: '2026-07-18'
tags: []
---

# yf-okf

Repo-agnostic engine that **constructs, manages, and conformance-checks** the artifact folders
("bundles") the yf artifact-producing skills emit (`yf-plan`, `yf-research`, `yf-incubator`, and
future consumers), making them **compatible with** the Open Knowledge Format (OKF v0.1). It is
also the **owner of the OKF-\* spec family** — the versioned ruleset that says how each kind of yf
artifact is structured and annotated.

Unlike `yf-change-validation` (runs build/test/lint — exit code = verdict) and `yf-drift-check`
(prose agreement across declared edges), yf-okf operates on the **shape** of an artifact bundle:
reserved `index.md`/`log.md`, a parseable frontmatter block with a non-empty `type` on every
non-reserved `.md`, the dual frontmatter+`**Field:**` model, and the `okf_spec:` member key.

Authoritative behavior lives in `SPEC.md` (REQ-OKF-\*) and `spec/` — `OKF-BASELINE.md` (upstream
OKF v0.1, pinned `okf_version: 0.1`) and `OKF-YF-EXTENSIONS.md` (the yoshiko-flow layer). This
file is the operational summary; on any discrepancy, `SPEC.md` and `spec/` win.

## OKF-\* family orientation

The **effective ruleset** the engine enforces is the composition
**OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ resolved-per-skill-`OKF-EXTENSION.md`** (REQ-OKF-FAM-001):

| Member | Where it lives | Role |
|:--|:--|:--|
| OKF-BASELINE | `spec/OKF-BASELINE.md` | upstream OKF v0.1 rules (reserved `index.md`/`log.md`, frontmatter + non-empty `type`) |
| OKF-YF-EXTENSIONS | `spec/OKF-YF-EXTENSIONS.md` | yf layer: dual field model, `okf_spec:` key, placement invariant; reserves `OKF-SPECIFICATION` (deferred) |
| per-skill `OKF-EXTENSION.md` | `skills/<skill>/OKF-EXTENSION.md` | one member per consumer (`OKF-PLAN`, `OKF-RESEARCH`, `OKF-INCUBATOR`) |

BASELINE + YF-EXTENSIONS are **baked into `okf.py`** (no cross-skill file read at runtime,
REQ-OKF-FAM-002); the two `spec/` docs are the authored reference, kept in agreement with the
baked ruleset by a `yf-drift-check` edge. Only the per-skill member is resolved at runtime, and
only `__file__`-relative to the running (vendored) `okf.py` (REQ-OKF-FAM-003) — so composition
runs from any vendored copy in both the worktree and installed address spaces, with no sibling
skill required on disk.

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-okf -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-okf skill directory not found"; exit 1; }
```

## Pre-flight

Run before any `check` / `migrate` / `assess` (not `init`):

1. Resolve `SKILL_DIR` (above).
2. Confirm the engine is present and runnable: `$SKILL_DIR/scripts/okf.py` exists and
   `uv` is on `PATH` (`depends-on-tool: [uv]`; the engine is a PEP-723 `uv run --script` with
   inline `pyyaml`). If the vendored engine is absent, fall back to the canonical `_shared/okf.py`
   at the repo root and report the drift.
3. Confirm the OKF-\* family docs `spec/OKF-BASELINE.md` and `spec/OKF-YF-EXTENSIONS.md` are
   present (the authored reference; the ruleset itself is baked into the engine).

yf-okf registers **no `yf` kernel subcommand** and installs **no always-loaded companion rule**
(it is operator-invoked, not on-edit auto-fire), so there is no `yf preflight yf-okf` and no
`protocols/manifest.json`. State: none (`check`/`assess` are report-only; `migrate` writes only
into the target folder).

## Invocation

```
/yf-okf <subcommand>
```

| Subcommand | Purpose |
|:--|:--|
| `init` | initialize yf-okf for a project (prereq check + install; § Init) |
| `check [<dir>]` | run the composed-ruleset conformance self-check over a bundle; report-only |
| `migrate <dir> [--dry-run]` | opt-in, per-folder, in-place migration to the OKF model |
| `assess <corpus>` | Epic-2 impact assessment: discover bundles under a root, run `check` + `migrate --dry-run` over each, produce an impact report (§ Assess) |

All engine-backed subcommands route to `scripts/okf.py` via `uv run`.

## Dispatch / engine call

Resolve `SKILL_DIR`, then invoke the engine (PEP-723 inline deps; `--json`/`--skill` accepted
before or after the subcommand):

```bash
uv run "$SKILL_DIR/scripts/okf.py" check <dir> [--skill <MEMBER>] --json
uv run "$SKILL_DIR/scripts/okf.py" migrate <dir> --dry-run [--skill <MEMBER>] --json
uv run "$SKILL_DIR/scripts/okf.py" migrate <dir> [--skill <MEMBER>] --json
uv run "$SKILL_DIR/scripts/okf.py" scaffold <dir> [--member <MEMBER>] [--subdir <X> ...] --json
```

Pass `--skill <MEMBER>` when the bundle belongs to a known consumer (`OKF-PLAN`, `OKF-RESEARCH`,
`OKF-INCUBATOR`) so the per-skill member is composed into the ruleset; omit it for a
BASELINE ∪ YF-EXTENSIONS check.

## check

`check` verifies the **composed** effective ruleset over a bundle (REQ-OKF-CHK-001): reserved
`index.md`/`log.md` well-formed, frontmatter + non-empty `type` on every non-reserved `.md`, the
placement invariant, the `okf_spec:` key, the single-file exemption, and the non-`.md` exclusion.
It is **report-only** — it never mutates the bundle — and **crash-safe** (REQ-OKF-071): messy,
malformed, or missing input yields a finding and continues, never a stack trace.

`check --json` returns:

```json
{"ok": false, "rulesets_composed": ["OKF-BASELINE", "OKF-YF-EXTENSIONS"],
 "findings": [{"path": "...", "req": "REQ-OKF-003", "level": "error", "message": "..."}]}
```

Exit code is **1 when `ok` is false** (or the dir is missing), **0 when conformant**. Report the
findings grouped by `req`; do not auto-fix (migration is the write path, and it is opt-in).

## migrate

`migrate <dir>` converts a **legacy** folder **in place** to the OKF-compatible model
(REQ-OKF-MIG-001) and is **opt-in** — run per-folder on demand; existing completed folders are
grandfathered, never bulk-rewritten. Always run `--dry-run` first and show the operator the plan.

`migrate --dry-run --json` returns a change plan:

```json
{"command": "migrate", "dir": "...", "dry_run": true, "skill": "OKF-PLAN", "member": "...",
 "changes": [{"op": "rename", "...": "..."}]}
```

`op` is one of `rename` (legacy reserved file → `index.md`/`log.md`), `move-phase-log`
(in-`plan.md` phase log → `log.md`), `add-frontmatter` (inject frontmatter + `type` above the
first `## `), `skip`, or `error`. Migration keeps the content fingerprint stable (frontmatter is
placed above the first `## `, a positional no-op for the hash — REQ-OKF-MIG-003) and preserves the
first `scoping:` date into `log.md` (REQ-OKF-MIG-002), so a migrated **approved** plan does not go
stale-approved and keeps its grandfather warn-downgrade. Writes are **merge-and-preserve**
(REQ-OKF-070): only yf keys are added; no pre-existing frontmatter key is dropped or overwritten.

## assess

The Epic-2 impact-assessment surface (issues 2.1/2.2 drive the implementation). Given a corpus
root, discover the candidate bundles under it and run `check` + `migrate --dry-run` over each,
producing an aggregate **impact report** — how many bundles conform, what each migration would
change, and any bundles the engine cannot classify. It is **read-only** (`check` and
`migrate --dry-run` never write) and **crash-safe**, so it is safe to run over a real foreign
corpus (e.g. a copy of an Obsidian vault) before deciding whether to adopt OKF.

Dispatch the assessor sub-agent (read-only; keeps the fan-out out of the main context):

```
Read ${SKILL_DIR}/agents/assessor.md and follow it.

CORPUS_ROOT: <root to scan>
SKILL_DIR:   <resolved yf-okf skill dir>
```

The assessor returns the impact report only — it never migrates. Applying a migration is a
separate, explicit `/yf-okf migrate <dir>` per folder.

## Init

`/yf-okf init` initializes yf-okf for a project. The skill and its `spec/` reference are picked
up automatically by the repo-level `install.sh` / `install.py` (auto-discovers every `skills/*/`
directory); yf-okf ships **no companion rule and no hook**, so no installer change is needed.
`init` is therefore consent-only: confirm `uv` is on `PATH`, confirm the engine
(`scripts/okf.py`, vendored per Issue 1.6) is present, and report readiness. The engine is
**vendored** into each consumer, not force-installed — `depends-on-skill: []`, so adopting yf-okf
does not drag consumers into an install group.

## Rules

- **Producer/manager, not a third-party validator** (GR-OKF-001). yf-okf constructs yf bundles and
  self-checks conformance; it does not re-implement the ecosystem's linters / MCP servers.
- **Never clobber a foreign corpus** (GR-OKF-002). Writes are merge-and-preserve (REQ-OKF-070);
  `check` and `migrate --dry-run` are report-only and crash-safe (REQ-OKF-071).
- **Migrate is opt-in and per-folder.** Never bulk-rewrite completed folders; always `--dry-run`
  first. Preserve the fingerprint and the first `scoping:` date (GR-OKF-004).
- **No runtime cross-skill file read** to compose the ruleset (GR-OKF-003). BASELINE +
  YF-EXTENSIONS are baked into `okf.py`; only the per-skill member is resolved, `__file__`-relative.
- `SPEC.md` / `spec/` are authoritative; if this file disagrees, they win.

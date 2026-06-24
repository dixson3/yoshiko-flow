---
title: change-validation
created: '2026-06-24'
tags: []
---

# change-validation

Repo-agnostic engine that runs a repo's **recorded validation recipe** (build / test / lint)
over a change-set or merged tree and reports **PASS / FAIL / INCONCLUSIVE** plus the first
failing command. Unlike `yf-drift-check` (prose + a read-only LLM sub-agent), this engine
**executes** commands via a Python runner — the verdict is an exit code, not an LLM judgment. It
never auto-fixes a failing command and never auto-rewrites the manifest.

The engine is fixed; each repository supplies a thin markdown **manifest** (`CHANGE-VALIDATION.md`
at its repo root) — **inferred from the toolchain**, **operator-approved**, then **re-proposed**
when the toolchain drifts (self-maintaining). With no approved manifest the engine is a silent
no-op and `run` returns a clean refusal.

## Prerequisites

- Claude Code (the skill loads as part of this repo's skill set).
- `uv` on PATH (`depends-on-tool: [uv]`) — the engine is a PEP-723 `uv run --script` Python
  script. No in-repo skill dependency (`depends-on-skill: []`).
- A repo opts in by authoring (or bootstrapping) an approved `CHANGE-VALIDATION.md` at its repo
  root. With no approved manifest the engine is a silent no-op.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers every `skills/*/`
directory. This skill ships one **companion rule**
(`protocols/CHANGE-VALIDATION-TRIGGER.md`) that the installer surfaces to the rules dir as an
always-loaded firing surface (`install_rules` globs `protocols/*.md`), and **no hook**. No
installer change is needed — both the skill and its rule are picked up automatically. See the
project [README](../../README.md) for `install.sh` flags. It adds **no `yf` Rust subcommand** —
it routes as a skill (the kernel/skill boundary).

## Usage

User-invocable (`/yf-change-validation`) with three subcommands:

- `init` (bootstrap) — infer a draft manifest from the toolchain, present it, await operator
  approval (infer → approve → enforce).
- `run --tier fast|full [--changed <paths>]` — execute a tier over the approved manifest
  (affected-scoped when `--changed`) and report the result.
- `check-drift` — diff the live toolchain against the recorded fingerprint and emit a JSON
  re-proposal; never rewrites the manifest.

It also fires automatically from the always-loaded companion rule
(`protocols/CHANGE-VALIDATION-TRIGGER.md`): on edit of a path matching an approved manifest's
§3 glob it runs the **FAST** (affected) tier; on pre-push / land-the-plane it runs the **FULL**
tier on the merged tree.

## The manifest

`CHANGE-VALIDATION.md` is markdown the engine reads by section (mirrors `DRIFT-CHECK.md`'s
section-by-heading model, but the recipe is executable):

- **§0 Status** — the `approved: yes|no` gate. Inert until `approved: yes`; setting it back to
  `no` is the one-edit rollback lever.
- **§1 Tiers** — a `fast` and a `full` ordered command list, each a table of structured rows
  (`id`, `cmd`, `cwd`, `timeout`). FULL is a superset of CI ∪ repo-checks.
- **§2 Signal Fingerprint** — the `{source-path, parsed-value-or-hash}` of the toolchain
  signals the recipe was inferred from; what `check-drift` re-reads.
- **§3 Trigger Scope** — each changed-path glob → the FAST command ids it selects
  (affected-scoping).

## Relationship to yf-plan

yf-plan's §6.1.5 merged-state validation (layer b) **delegates** to this skill via a prose
soft-dep: an approved `CHANGE-VALIDATION.md` present → delegate to `change_validation.py run
--tier full`; absent or `approved: no` → fall back to the static `validate-cmd`; absent that
too → the verbatim not-checked notice. This skill supersedes the static `validate-cmd` (the #27
migration), which it seeds the FULL tier from at inference time and keeps as a thin fallback.

## Behavior model

```
edit / pre-push
      │
      ▼
read approved CHANGE-VALIDATION.md  ──(none / approved: no)──▶ silent no-op / clean refusal
      │
      ▼
on-edit: match changed path against §3 globs ──▶ FAST tier (affected ids)
pre-push / land-the-plane             ──────────▶ FULL tier (merged tree)
      │
      ▼
execute commands in row order (sh -c, cwd, timeout)
      │
      ├─ all exit 0          ──▶ PASS
      ├─ first non-zero exit ──▶ FAIL (first_failure + output tail); never auto-fix
      └─ required tool absent ─▶ INCONCLUSIVE (fail-closed; never a false PASS)
```

- **No auto-fix.** The engine runs and reports; the operator repairs.
- **No auto-rewrite.** `check-drift` proposes a tier delta; it never edits the manifest.
- **Fail-closed.** A missing tool is INCONCLUSIVE, the deliberate contrast with a fail-open
  `validate-cmd`.

## Scope boundary

change-validation proves a change-set is **behaviorally valid** by executing build/test/lint.
Cross-edge content agreement (docs ↔ spec ↔ implementation) is `yf-drift-check`'s axis — a
prose/LLM trigger with no runnable command, **excluded from every tier**. The two are
independent, non-recursive triggers; a shared `.md` edit firing both is expected. Neither
invokes the other.

## Layout

```
skills/yf-change-validation/
├── SKILL.md                          # engine: invocation, manifest detection, dispatch, run-and-report
├── README.md                         # this file
├── SPEC.md                           # the requirement-numbered (REQ-CHGVAL-*) per-skill spec
├── spec/
│   ├── schema.md                     # the 4-section manifest schema + structured tier rows (REQ-SCHEMA-*)
│   ├── engine.md                     # no-op, infer→approve→enforce, run-and-report, fail-closed, re-propose, rollback (REQ-ENGINE-*)
│   └── inference.md                  # inference precedence, PEP-723 per-file idiom, FULL-superset, validate-cmd seed (REQ-INFER-*)
├── scripts/
│   └── change_validation.py          # the Python engine: infer / run / check-drift
├── templates/
│   └── manifest.md                   # blank CHANGE-VALIDATION.md a repo fills in (inert approved: no)
└── protocols/
    └── CHANGE-VALIDATION-TRIGGER.md  # always-loaded on-edit (FAST) + pre-push (FULL) firing surface
```

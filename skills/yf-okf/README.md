---
title: okf
created: '2026-07-18'
tags: []
---

# okf

Repo-agnostic engine that **constructs, manages, and conformance-checks** the artifact folders
("bundles") the yf artifact-producing skills emit (`yf-plan`, `yf-research`, `yf-incubator`),
making them **compatible with** the Open Knowledge Format (OKF v0.2). `yf-okf` is also the
**owner of the OKF-\* spec family** — the versioned ruleset describing how each kind of yf
artifact is structured and annotated.

It is a **producer/manager plus a conformance self-check**, not a third-party OKF validator. It
operates on the *shape* of a bundle: reserved `index.md` / `log.md`, a frontmatter block with a
non-empty `type` on every non-reserved `.md`, the dual frontmatter + `**Field:**` model, and the
`okf_spec:` member key.

## Prerequisites

- Claude Code (the skill loads as part of this repo's skill set).
- `uv` on PATH (`depends-on-tool: [uv]`) — the engine is a PEP-723 `uv run --script` Python
  script with inline `pyyaml`. No in-repo skill dependency (`depends-on-skill: []`): the engine
  is **vendored** into each consumer, never force-installed.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers every `skills/*/`
directory. yf-okf ships **no companion rule and no hook** — it is operator-invoked, not on-edit
auto-fire — so there is no `protocols/` rule to surface and no installer change is needed. See the
project [README](../../README.md) for `install.sh` flags. It adds **no `yf` Rust subcommand** — it
routes as a skill (the kernel/skill boundary).

## Usage

User-invocable (`/yf-okf`) with four subcommands:

- `init` — consent-only setup (prereq check; the skill installs automatically).
- `check [<dir>]` — composed-ruleset conformance self-check over a bundle; **report-only**.
- `migrate <dir> [--dry-run]` — **opt-in, per-folder, in-place** migration to the OKF model.

Scope boundary: yf-okf owns the *shape* of yf artifact bundles. Running a repo's build/test/lint
recipe is `yf-change-validation`; checking that already-written docs **agree** across declared
edges is `yf-drift-check` — orthogonal axes yf-okf never invokes.

## OKF-\* family

The effective ruleset is the composition **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ per-skill
`OKF-EXTENSION.md`**. BASELINE + YF-EXTENSIONS are **baked into `okf.py`** (no runtime cross-skill
read); the two `spec/` docs are the authored reference, kept in agreement with the baked ruleset
by a `yf-drift-check` edge. Only the per-skill member is resolved at runtime, `__file__`-relative
to the running (vendored) `okf.py`, so composition runs from any vendored copy in both the
worktree and installed address spaces.

## Behavior model

```
/yf-okf check <dir>    ──▶ compose ruleset ──▶ report findings (report-only, crash-safe); exit 1 if not ok
/yf-okf migrate <dir>  ──▶ --dry-run first (change plan) ──▶ opt-in in-place write (merge-and-preserve,
                            fingerprint-stable, first scoping date preserved)
```

- **Report-only** `check` never mutates the corpus; **crash-safe** on messy input.
- **Corpus-scale work lives in `yf-okf-hygiene`** — which bundles exist, classifying the
  population, the legacy backfill and its reversal. This skill owns ONE bundle at a time.
- **Merge-and-preserve** writes never drop a pre-existing frontmatter key.
- **No auto-fix** — migration is the only write path, and it is opt-in and per-folder.

## Layout

```
skills/yf-okf/
├── scripts/
│   └── okf.py                # vendored engine (Issue 1.6 registers the sync); canonical: _shared/okf.py
├── spec/
│   ├── OKF-BASELINE.md       # upstream OKF v0.2 rules (pinned okf_version: 0.2)
│   └── OKF-YF-EXTENSIONS.md  # the yoshiko-flow extension layer (reserves OKF-SPECIFICATION)
├── README.md                 # this file
├── SKILL.md                  # engine: operational summary, invocations, dispatch
└── SPEC.md                   # requirement-numbered (REQ-OKF-*) per-skill spec
```

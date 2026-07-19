---
type: Finding
okf_spec: OKF-PLAN
---

# OKF migration samples — before/after for the ratification gate (Issue 2.3)

Representative `okf.py migrate` runs on **copies** of real bundles from both corpora (this
repo + the Obsidian vault snapshot), produced by the refactored engine. Every sample proves
that a base `migrate` yields a bundle whose `check` is **error-free** (`ok: true`). No live
repo or vault bundle was migrated in place — all inputs were copied out first (the vault
copies come from the read-only snapshot at `scratchpad/vault-snapshot/`).

Engine: `.worktrees/plan-029-james-dixson-75fd34/_shared/okf.py` (refactored in this issue),
invoked `env -u VIRTUAL_ENV uv run okf.py {migrate,check} <copy> --skill <s> --json`.

## What changed in the engine (the four gaps from Issue 2.1 / 2.2)

| Gap | Fix proven by these samples |
|:--|:--|
| **I-1** every file became `type: Concept` | migrate now assigns a role-mapped `type` per the member's `OKF-EXTENSION.md` §1a **role → type map** (REQ-OKF-MIG-004); an unmapped file falls back to the default and is **recorded** (`type_source: default-fallback`), never silently mislabeled |
| **I-2** migrate was plan-shaped (research/incubator still failed `check`) | reserved-file reconciliation is **member-driven** (REQ-OKF-MIG-005): each member's §1b declares the `index.md` source (rename `README.md` / `_index.md`, or `scaffold`) and the `log.md` source (`extract-log` from a `**Phase log:**` block, or `scaffold`). After migrate, `check` **passes** for all three members |
| **I-3** `move-phase-log` op read ambiguously | renamed to **`extract-log`** with `source_kept: true` — the change plan is now unambiguous that `plan.md` is **kept**, not renamed |
| **I-4** dual-field not established by migrate | migrate **mirrors** existing `**ID:**` / `**Status:**` / … header lines into frontmatter (REQ-OKF-020), so both surfaces are established and in sync — proven by the plan sample |

## The four samples

Each sample dir holds: `before/` (verbatim copy), `after/` (the migrated copy),
`migrate-dry-run.json` (the change plan), `migrate-applied.json`, `check-before.json`
(non-conformant), `check-after.json` (**`ok: true`**), and `tree-before.txt` / `tree-after.txt`.

### 1. `plan-bundle/` — OKF-PLAN (copy of `plan-001-james-dixson-c88e7a`)

Proves the full plan path. Change plan: `rename README.md → index.md`, `extract-log`
(`plan.md` kept; grandfather date `2026-04-05` seeded into `log.md`), and 6 `add-frontmatter`
ops carrying **role-mapped** types — `plan.md`=`Plan`, `context.md`=`Environment`,
`findings/*`=`Finding`, `reviews/pass-*`=`Review`, `references/upstream-*`=`Reference` (no
blanket `Concept`). `plan.md` frontmatter now mirrors `id`/`author`/`created`/`status` from
its `**Field:**` lines (dual-field, I-4), and the two surfaces coexist. **Fingerprint-neutral:**
the `plan.md` body from the first `## ` onward is byte-identical before/after (verified sha).
`check-after`: `ok: true`, **0 warnings**.

### 2. `research-bundle/` — OKF-RESEARCH (copy of `001-okf-compliance-delta`)

Proves the I-2 fix for the `_index.md` convention. Change plan: `rename _index.md → index.md`
(the reserved index; no `**Phase log:**` exists, so `log.md` is **scaffolded**), and 7
`add-frontmatter` ops — `Summary.md`=`Research Report`, `artifacts/*`=`Research Artifact`,
`sources.md`=`Reference`. `sources.json` / `plan.yaml` are correctly excluded (REQ-OKF-060).
`check-after`: `ok: true` with **3 warnings** — `Summary.md` still lacks the member keys
`idx`/`topic`/`created` (they live in a legacy *prose* header). Backfilling those and rendering
the fine `_index.md`-ledger → `log.md` split is the **Epic 4 adapter's job**; the base engine
guarantees only the conformant skeleton (see the base-vs-adapter boundary below).

### 3. `incubator-bundle/` — OKF-INCUBATOR (copy of vault `Incubator/CodeMage`)

Proves the **key member divergence**: the dir-form incubator's `README.md` is the **typed
state file** (`type: Incubator`), *not* the bundle listing — so migrate **keeps** `README.md`
and **scaffolds** `index.md` + `log.md` (it does **not** rename `README.md → index.md` the way
OKF-PLAN does). The state file's 7-key Obsidian frontmatter (`title`/`tags`/`aliases`/…)
survives; only `type`/`okf_spec` are added (REQ-OKF-070). Supporting docs (`00Index.md`,
`Onboarding.md`) have no member type, so they fall back to `Concept` — **recorded** as
`default-fallback` and surfaced as `check` **warnings** (2) for the Epic 5 adapter to classify.
`check-after`: `ok: true`.

### 4. `foreign-frontmatter/` — foreign-key survival (copy of vault `Incubator/agent-optimized-websites`)

Proves merge-and-preserve on a real Obsidian file with pre-existing `tags:` / `aliases:`.
Compare `before/README.md` and `after/README.md`: **every** foreign key survives with its
value; only `type: Incubator` + `okf_spec` are appended. It also **documents the
re-serialization decision** — flow-style `tags: [a, b]` reflows to a block list (PyYAML
`safe_dump`). Values are semantically identical; the reflow is cosmetic and, for the corpora
that carry a fingerprint (yf-plan), sits above the first `## ` and is therefore
fingerprint-neutral. See `OKF-YF-EXTENSIONS.md` §7a. `check-after`: `ok: true`, 0 warnings.

## Decisions for the ratification gate

1. **`check` error-vs-warning split.** OKF baseline MUSTs (`type` + parseable frontmatter),
   `okf_spec`, placement, and reserved-file presence are **errors** the base engine
   guarantees. A member's **extra required keys** and **type-vocab** membership are
   **warnings**, scoped to the member's main type — backfilling member keys from legacy prose
   is the per-skill adapter's job. This is what lets a base migrate be error-free immediately
   (SPEC REQ-OKF-CHK-001; `OKF-YF-EXTENSIONS.md` §7b).
2. **The incubator `README.md` divergence** (kept as state file vs. renamed to `index.md` for
   plan) — confirm this member-driven asymmetry.
3. **Frontmatter re-serialization is not byte-neutral** (flow→block reflow) — accepted and
   documented (`OKF-YF-EXTENSIONS.md` §7a); confirm no minimal-diff writer is required now.
4. **The base-engine vs. per-skill-adapter boundary** for index/log *rendering* (the research
   `_index.md`-ledger split, the incubator `## Files`/`## Decision log` promotion) — the base
   migrate produces a conformant skeleton; the fine rendering is deferred to Epics 3/4/5.

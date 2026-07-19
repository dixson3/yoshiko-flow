---
type: Finding
okf_spec: OKF-PLAN
---

# OKF-* conversion impact assessment — this repo (Issue 2.1)

Read-only impact assessment of the OKF-* baseline conversion against the live
artifact corpus in this repository. The OKF engine used is the worktree copy at
`.worktrees/plan-029-james-dixson-75fd34/_shared/okf.py` (byte-identical to the
vendored `skills/yf-okf/scripts/okf.py`), invoked with
`env -u VIRTUAL_ENV uv run <engine> {check,migrate --dry-run} <dir> --skill <s> --json`.
Every corpus folder was exercised with `check` and `migrate --dry-run` only — no
folder was mutated, nothing was committed.

## Corpus inventory

Both artifact roots were enumerated (not assumed) before running the engine.

| Artifact type | Root scanned | Bundles found | `--skill` |
|:---|:---|:---|:---|
| Plans | `docs/plans/*/` | 29 (`plan-001` … `plan-029`) | yf-plan → OKF-PLAN |
| Research | `docs/research/*/` | 1 (`001-okf-compliance-delta`) | yf-research → OKF-RESEARCH |
| Incubators | `Incubator/*/` | 0 (directory empty) | — |

`Incubator/` exists but is empty, and there are no `Incubator/<slug>/plans/` or
`Incubator/<slug>/research/` sub-bundles. So the OKF-INCUBATOR member could not be
exercised against a live bundle in this repo — its impact is inferred from the
engine code, not observed. Total live bundles assessed: **30** (29 plan + 1 research).

Engine health: all 60 invocations (30 `check` + 30 `migrate --dry-run`) exited 0
with clean stderr. No crash, traceback, or malformed JSON. Every plan `check`
returns `ok: false`; the research `check` returns `ok: false`.

## Per-artifact-type impact

### OKF-PLAN — 29 plan bundles (uniform shape)

Every one of the 29 plan folders produces the **identical** three-class change set.
Aggregate `migrate --dry-run` op counts across all 29:

| op | count | meaning |
|:---|:---|:---|
| `rename` | 29 | `README.md` → `index.md` (one per plan) |
| `move-phase-log` | 29 | extract the `**Phase log:**` block from `plan.md` into reserved `log.md` |
| `add-frontmatter` | 239 | add `type` + `okf_spec` to every non-reserved `.md` |

Representative change plan (`plan-001-james-dixson-c88e7a`, trimmed):

```json
{"op": "rename", "path": "README.md", "to": "index.md"}
{"op": "move-phase-log", "path": "plan.md", "to": "log.md", "first_scoping_date": "2026-04-05"}
{"op": "add-frontmatter", "path": "context.md",             "keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
{"op": "add-frontmatter", "path": "plan.md",                "keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
{"op": "add-frontmatter", "path": "references/upstream-3.md","keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
{"op": "add-frontmatter", "path": "reviews/pass-1.md",      "keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
{"op": "add-frontmatter", "path": "upstream-triage.md",     "keys": {"type": "Concept", "okf_spec": "OKF-PLAN"}}
```

`check` for every plan flags exactly three requirement classes, no others:

| req | count (all 29) | finding |
|:---|:---|:---|
| REQ-OKF-001 | 29 | reserved `index.md` missing |
| REQ-OKF-002 | 29 | reserved `log.md` missing |
| REQ-OKF-003 | 268 | non-reserved `.md` with no YAML frontmatter block |

(268 REQ-OKF-003 = 239 add-frontmatter ops + the 29 `README.md` files that are
renamed to the reserved `index.md` instead of frontmattered.)

The 239 frontmatter targets, by role — **all** would be stamped `type: Concept`:

| role | count |
|:---|:---|
| root-level (`context.md` ×29, `plan.md` ×29, `upstream-triage.md` ×17) | 75 |
| `findings/*` | 56 |
| `references/*` | 52 |
| `reviews/*` | 56 |

No plan currently has an `index.md` or `log.md`, so no rename/move op is a no-op or
a clobber; every plan is a clean legacy → OKF conversion.

### OKF-RESEARCH — 1 research bundle

`docs/research/001-okf-compliance-delta/` uses a Hugo-style layout: `_index.md`,
`Summary.md`, `sources.md`, `artifacts/*.md`, plus non-`.md` siblings (`plan.yaml`,
`sources.*.json`, `diagrams/`, `scripts/`). `migrate --dry-run` emits **only 8
`add-frontmatter` ops** — no `rename`, no `move-phase-log`:

```json
{"op": "add-frontmatter", "path": "Summary.md",  "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
{"op": "add-frontmatter", "path": "_index.md",   "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
{"op": "add-frontmatter", "path": "artifacts/critique.md",       "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
{"op": "add-frontmatter", "path": "artifacts/triangulation.md",  "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
{"op": "add-frontmatter", "path": "sources.md",  "keys": {"type": "Concept", "okf_spec": "OKF-RESEARCH"}}
```

But `check` for the same bundle still flags `index.md missing` (REQ-OKF-001) and
`log.md missing` (REQ-OKF-002) — and `migrate` offers **no op to satisfy them**
(see inconsistency I-2 below). Non-`.md` files are correctly excluded (REQ-OKF-060).

### OKF-INCUBATOR — 0 bundles

No incubator bundle exists to migrate. From the engine code, the migrate flow is
plan-shaped (README→index and plan.md phase-log are the only structural rules), so
an incubator bundle would receive only `add-frontmatter` ops plus whatever REQ-OKF-001/002
reserved-file gaps its layout leaves unsatisfied — the same generalization gap as
research (I-2). This is inferred, not observed; flag for a live re-run once an
incubator bundle exists.

## Inconsistencies surfaced (input to Issue 2.3)

**I-1 — Uniform `type: Concept` for every file (highest-impact).** The engine
assigns `type: Concept` to all 247 non-reserved files (239 plan + 8 research)
regardless of role, because `_cmd_migrate` calls `migrate(...)` with **no
`type_map`**, and the resolved OKF-EXTENSION member supplies only `okf_spec`, not a
per-role type map (`assigned_type = type_map.get(md.name) or fm.get(TYPE_KEY) or
"Concept"`, okf.py:977). A `findings/` file, a `reviews/` pass, a `references/`
capture, `plan.md`, and `context.md` all collapse to `Concept`. If OKF-PLAN /
OKF-RESEARCH / OKF-INCUBATOR are meant to carry a meaningful type vocabulary
(e.g. `Finding`, `Review`, `Reference`, `Plan`, `Concept`), the extension drafts
must (a) define the vocabulary and a filename/subdir → type map, and (b) wire that
map into the migrate CLI. As drafted, conversion is type-lossy.

**I-2 — Migrate is plan-shaped; it cannot make research/incubator bundles
conformant.** The `README.md → index.md` and `plan.md` phase-log → `log.md` rules
are hardcoded (okf.py:926–959), not member-driven. Research uses `_index.md` +
`Summary.md`, so migrate produces no reserved `index.md`/`log.md`, and `check`
still fails REQ-OKF-001/002 **after** a full migrate. The drafts need a
member-specific reserved-file reconciliation (e.g. OKF-RESEARCH: `_index.md` →
`index.md`; define what becomes `log.md`) or the check must exempt these members
from the reserved-file MUSTs. Same gap will hit OKF-INCUBATOR.

**I-3 — `move-phase-log` change-plan entry reads ambiguously (reporting, not a
bug).** For all 29 plans, `plan.md` appears in **two** change entries:
`move-phase-log plan.md → log.md` and `add-frontmatter plan.md`. This looks like a
double-op / rename-then-write-a-ghost, but the code does not rename `plan.md`: it
extracts the `**Phase log:**` block into a new `log.md` and leaves `plan.md` in
place (correctly still needing frontmatter). The `to: log.md` detail on a
`move-phase-log` whose `path` is `plan.md` invites misreading as a file rename. 2.3
should either rename the op or add a `source_stays: true` / clarifying field so the
change plan is unambiguous.

**I-4 — Dual-field (REQ-OKF-020) not established by migrate.** Plan headers carry
`**ID:**`, `**Author:**`, `**Status:**`, `**Created:**` as `**Field:**` lines but no
frontmatter mirror. Migrate adds only `type` + `okf_spec` frontmatter; it does not
lift the existing `**Field:**` metadata into frontmatter, so the dual-field
invariant is only half-met post-migration. `check`'s baked MUSTs (B1–B3) don't
enforce the mirror, so this passes `check` but leaves the drafts' dual-write intent
unrealized. Decide in 2.3 whether migrate should backfill the frontmatter mirror.

## Engine-level findings

No engine crash, traceback, non-zero exit, or malformed-JSON output was observed
across all 60 invocations. The engine is robust on this corpus. I-3 is a
change-plan **legibility** concern, not a runtime fault; I-1/I-2/I-4 are
**draft/spec** gaps (the engine faithfully does what the drafts specify — the
drafts under-specify), not engine bugs. Nothing here reopens Issue 1.4 on
correctness grounds; the type-map wiring (I-1) is the one item that may require a
small engine change (thread a member `type_map` into `_cmd_migrate`) alongside the
draft edits.

## Grandfather / fingerprint safety notes

Confirmed safe from the dry-run plans and source inspection:

- **First scoping date preserved.** Every plan's `move-phase-log` op reports a
  `first_scoping_date` extracted from the first `scoping:` line of the
  `**Phase log:**` block, spanning `2026-04-05` (plan-001) … `2026-07-17`
  (plan-029). On a real run, `append_log(..., date=first)` seeds `log.md` with that
  original date (REQ-OKF-MIG-002), so the grandfather date is retained, not reset to
  today.
- **Fingerprint stable (hash-neutral removal).** In every plan sampled
  (plan-001/015/028) the `**Phase log:**` block sits **above** the first `## `
  heading (e.g. line 7 vs `## Objective` at line 18). `_PHASE_LOG_RE` matches only up
  to the next `## `, and migrate removes just that pre-heading block, so all content
  below the first heading — the fingerprintable body — is unchanged. The README →
  index rename copies bytes verbatim. Approved plans therefore migrate without
  disturbing their content fingerprint.

One caveat to carry: hash-neutrality depends on the phase-log block preceding the
first `## `. All 29 current plans satisfy this, but a future plan that placed a
`**Phase log:**` after a heading would have content removed from below the first
heading — a fingerprint change. Worth a guard/assertion in the migrate path.

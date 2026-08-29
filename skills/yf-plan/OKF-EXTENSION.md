# OKF-PLAN — yf-plan per-skill OKF extension

> **Status: DRAFT (plan-029, Epic 1, Issue 1.3).** Proposal only. Epic 2's impact assessment
> stress-tests this member; the human ratification gate approves it before any implementation
> (Epics 3/6) applies it. Composed by the engine as
> **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ OKF-PLAN** (SPEC REQ-OKF-FAM-001). Discovered by
> `resolve_extension("yf-plan")` at `skills/yf-plan/OKF-EXTENSION.md`, `__file__`-relative to the
> vendored `okf.py` (SPEC REQ-OKF-FAM-003). Terminology and REQ ids match `skills/yf-okf/SPEC.md`.

## 0. Member identity

| Field | Value |
|:--|:--|
| `okf_spec:` member name | **OKF-PLAN** |
| Purpose | Structures a yf-plan **plan bundle** (`docs/plans/<plan-id>/` or `Incubator/<slug>/plans/<plan-id>/`) as an OKF-compatible dir-form bundle: a typed `plan.md` plus typed findings, reviews, environment, and reference concept documents, with the dual frontmatter + `**Field:**` header model preserved on `plan.md`. |
| Bundle form | **dir-form** (always has an owning directory; never single-file). |
| Selector | Every non-reserved `.md` in the bundle carries `okf_spec: OKF-PLAN`. |

## 1. `type` vocabulary (open vocab; OKF-PLAN owns this set)

Per `OKF-BASELINE.md` §5 the `type` vocabulary is open, free-form, and title-case. OKF-PLAN fixes
the following strings for the artifact kinds a plan bundle emits:

| `type` value | Applies to (path in the bundle) | Source in `plan_manager.py` |
|:--|:--|:--|
| `Plan` | `plan.md` — the plan of record | `seed_plan_md` |
| `Finding` | `findings/*.md` — investigation experiment results (e.g. `exp-001-*.md`) | investigation findings |
| `Review` | `reviews/pass-<N>.md` — one file per reviewer cycle | `reviews/` seed |
| `Environment` | `context.md` — project environment snapshot | `seed_context_md` |
| `Reference` | `references/upstream-<N>.md` — inlined upstream issue bodies | `write_upstream_reference` |
| `Retrospective` | `plan-retrospective.md` — stops and deviations recorded during execution; **presence-optional**, absence is never a finding (REQ-PORT-ACT-RETROSPECTIVE) | `retrospective-append` (REQ-CLI-022) |

`upstream-triage.md` (the operator working file) is a plan-local disposition surface, not a
concept document; it is typed `Reference` if retained as a bundle `.md`, or excluded if treated as
scratch — **decision to lock in Epic 3** (see §6).

## 1a. Migration: role → type map (SPEC REQ-OKF-MIG-004)

`migrate` assigns each non-reserved `.md` a `type` from this ordered path-glob → type map
(first match wins). A file matching no rule falls back to the member default and the fallback is
**recorded** in the change plan (`type_source: default-fallback`) — never silently mislabeled.

| Path glob | `type` |
|:--|:--|
| `plan.md` | `Plan` |
| `findings/*` | `Finding` |
| `reviews/pass-*` | `Review` |
| `context.md` | `Environment` |
| `references/upstream-*` | `Reference` |
| `references/*` | `Reference` |
| `upstream-triage.md` | `Reference` |
| `plan-retrospective.md` | `Retrospective` |
| `*` | `Concept` |

## 1b. Migration: reserved-file sources (SPEC REQ-OKF-MIG-005)

`migrate` reconciles the reserved files from these member-declared sources; the source index
file is renamed and the phase-log block is extracted (the source `plan.md` is **kept**, not
renamed — see §6).

| Reserved target | Source |
|:--|:--|
| `index.md` | `README.md` |
| `log.md` | `plan.md:phase-log` |

## 2. Required extension frontmatter keys

Beyond OKF's one MUST (`type`, non-empty) and the yf `okf_spec:` selector (SPEC REQ-OKF-030), an
OKF-PLAN `plan.md` carries the yf producer keys already recorded as `**Field:**` header lines:

| Key | Force on `plan.md` | Notes |
|:--|:-:|:--|
| `type` | MUST | `Plan` |
| `okf_spec` | MUST | `OKF-PLAN` |
| `id` | MUST | Plan id (e.g. `plan-029-james-dixson-75fd34`) — dual of `**ID:**` |
| `author` | MUST | Authoring operator — dual of `**Author:**` |
| `created` | MUST | ISO-8601 (`YYYY-MM-DD`) — dual of `**Created:**` |
| `status` | MUST | Lifecycle state (`scoping` … `complete`) — dual of `**Status:**` |
| `epic` | SHOULD | Owning beads epic — dual of `**Epic:**`; absent until an epic is recorded |
| `fingerprint` | SHOULD | Content fingerprint — dual of `**Fingerprint:**`; absent until first computed |

**Upstream dispositions.** The plan's upstream reconciliation lives in the `## Upstream Issues`
table (`Disposition` / `Resolved By` columns) inside `plan.md` **below** the first `## ` heading —
it is *body*, not header frontmatter, and is not dual-written. Each `references/upstream-<N>.md`
(`type: Reference`) MAY carry a `disposition:` key mirroring that row's disposition.

**Review passes.** Each `reviews/pass-<N>.md` (`type: Review`) carries `id`/`author`/`created`/
`okf_spec` plus a `pass:` (the `<N>`) and a `verdict:` key. The dual `**Field:**` header model is
**not** required on review/finding/environment/reference docs — they never carried `**Field:**`
lines and are frontmatter-only typed concept documents.

## 3. Reserved subdirs / files

OKF reserves `index.md` and `log.md` at any level (`OKF-BASELINE.md` §3–§4). OKF-PLAN adds these
per-artifact-type reserved subdirectories (per `OKF-YF-EXTENSIONS.md` §4):

| Reserved path | Holds | Replaces (legacy) |
|:--|:--|:--|
| `index.md` | Bundle listing (`#` heading + `- description` bullets); MAY carry `okf_version` | `README.md` (SPEC REQ-OKF-001) |
| `log.md` | Newest-first ISO-8601 phase history | the in-`plan.md` `**Phase log:**` block (SPEC REQ-OKF-002) |
| `findings/` | `Finding` concept docs | (unchanged) |
| `reviews/` | `Review` concept docs (`pass-<N>.md`) | (unchanged) |
| `references/` | `Reference` concept docs (`upstream-<N>.md`) | (unchanged) |

Reserved `index.md` / `log.md` carry **no `type` and no `okf_spec`** (SPEC REQ-OKF-031).

## 3b. Excluded paths (SPEC REQ-OKF-CHK-003)

Bundle-relative globs that **every OKF walk site skips** — conformance `check`, `migrate`, the
root-listing member set, and `plan_manager.py`'s bundle walk and `dangling-refs` scan. Matched with
`fnmatch`, so `**` is genuinely recursive.

| Excluded glob | Why |
|:--|:--|
| `assets/fixtures/**` | Markup-sensitive ground-truth corpora (e.g. `test_classify_deliverable.py`'s). Their exact bytes are the test; stamping frontmatter on them would not merely produce a spurious finding, it would **destroy the fixture**. |
| `findings/okf-migration-samples/**` | A deliberate before/after migration-diff corpus — 45 nested `.md` files whose whole purpose is to be **non-conformant**. Reported as 34 real findings on an unrelated plan's close (#233). |

**These are the fixture carve-outs, and NOTHING ELSE.** An exclusion is a statement that a path is
**not the kind of thing this ruleset judges** — never that a real artifact is inconvenient to fix.
Adding a row to silence a finding on a live bundle member converts the conformance check into a
record of what someone did not want to look at.

**Independently declared from `doc_lint`'s `exclude` lists, by design** (plan-056 D-14). The two
layers share a *mechanism*, not a *source*: `doc_lint`'s lists are **repo-relative** and per-schema,
these are **bundle-relative** and per-member. Deriving one from the other would miss
`assets/fixtures/**` entirely — `doc_lint` is silent there by **non-selection**, not by exclusion,
and those are different facts. The relationship is pinned by the overlap-invariant test, which also
asserts **both lists are non-empty**: without that half the invariant holds trivially when either
side is empty, which is the state this section was introduced from.

The positive control is `okf.py check --no-exclude` (and `doc_lint --no-exclude`): removing this
section, or passing the flag, restores the suppressed findings.

## 4. The dual field set (SPEC REQ-OKF-020 / REQ-OKF-021)

On `plan.md`, these `**Field:**` header lines dual-write with these frontmatter keys — one writer,
one in-memory model, emitting **both** representations (never authored independently):

| `**Field:**` line | Frontmatter key |
|:--|:--|
| `**ID:**` | `id` |
| `**Author:**` | `author` |
| `**Created:**` | `created` |
| `**Status:**` | `status` |
| `**Epic:**` | `epic` |
| `**Fingerprint:**` | `fingerprint` |

**Placement invariant (SPEC REQ-OKF-010).** Both the frontmatter block and the `**Field:**` block
sit **above the first `## ` heading** (`## Objective`). `plan_manager.py`'s content fingerprint
excludes everything before the first `## ` (`_plan_content_sections` / `_plan_content_fingerprint`,
exp-001), so adding frontmatter and moving `**Phase log:**` → `log.md` are both **hash-neutral by
construction** — a migrated approved plan does not go stale-approved (SPEC REQ-OKF-MIG-003).

**Grandfather safety.** The first `scoping:` date in the legacy `**Phase log:**` must be preserved
into `log.md` in machine-readable form so `_plan_first_scoping_date` still resolves (SPEC
REQ-OKF-MIG-002).

## 5. Index-body convention

`index.md` is a progressive-disclosure listing — `#` heading + `- [child](path) - description`
bullets (`OKF-BASELINE.md` §3). yf-plan supplies a rendering adapter (Epic 3) that lists the bundle
members (`plan.md`, `context.md`, `findings/`, `reviews/`, `references/`) with one-line
descriptions, replacing the legacy seeded `README.md` file-map/reading-order body. Rendering detail
is a yf-plan `spec/` amendment, not fixed here.

## 6. Deltas from the OKF baseline / decisions to lock (for the coordinator)

Deltas Epic 2's impact assessment quantifies and the ratification gate confirms:

- **`plan.md` carries no YAML frontmatter today** — metadata is `**Field:**` prose only. Adopting
  OKF-PLAN adds a dual frontmatter block above the first `## ` (the largest single delta;
  hash-neutral by REQ-OKF-010).
- **`README.md` → `index.md`** rename (SPEC REQ-OKF-001). Every consumer of the seeded `README.md`
  (`seed_readme`, the audit, docs) must repoint.
- **`**Phase log:**` (in-`plan.md`) → `log.md`** extraction (SPEC REQ-OKF-002). The migrate op is
  **`extract-log`** (renamed from the ambiguous `move-phase-log`, I-3) and carries `source_kept:
  true`: `plan.md` is **not** renamed — only its `**Phase log:**` block is lifted into `log.md`, and
  `plan.md` remains in place (still receiving `type`/`okf_spec` + the dual-field mirror). Three
  parsers read the legacy block (REQ-PORT-006 count-equality, grandfather clause, phase-log append) —
  a partial move silently breaks them (plan R1). Preserve the first `scoping:` date (REQ-OKF-MIG-002).
- **Dual-field mirror (SPEC REQ-OKF-020).** `migrate` lifts the existing `**ID:**` / `**Author:**` /
  `**Created:**` / `**Status:**` header lines on `plan.md` into their frontmatter mirror keys
  (`id` / `author` / `created` / `status`) so the dual representation is established by migration,
  not left frontmatter-only. Both surfaces are kept in sync (never authored independently).
- **`findings/`, `reviews/`, `context.md`, `references/*` gain frontmatter+`type`+`okf_spec`** —
  they carry none today. Mechanical add per file.
- **`upstream-triage.md` classification** (`Reference` vs. excluded scratch) — **decision to lock in
  Epic 3.**

## 7. References

- `skills/yf-okf/SPEC.md` — REQ-OKF-001/002/003, 010, 020/021, 030/031, 050, 060, MIG-002/003,
  FAM-001..003.
- `skills/yf-okf/spec/OKF-BASELINE.md` (upstream OKF v0.2) and
  `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` (the yf layer this member composes on).
- `skills/yf-plan/scripts/plan_manager.py` — `seed_plan_md`, `seed_index`, `seed_context_md`,
  `write_upstream_reference`, `_plan_content_sections`, `_plan_first_scoping_date`.
- `docs/plans/plan-029-james-dixson-75fd34/` — a real OKF-PLAN-candidate bundle.

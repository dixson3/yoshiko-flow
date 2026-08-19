# OKF-RESEARCH — yf-research per-skill OKF extension

> **Status: DRAFT (plan-029, Epic 1, Issue 1.3).** Proposal only. Epic 2's impact assessment
> stress-tests this member; the human ratification gate approves it before any implementation
> (Epics 4/6) applies it. Composed by the engine as
> **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ OKF-RESEARCH** (SPEC REQ-OKF-FAM-001). Discovered by
> `resolve_extension("yf-research")` at `skills/yf-research/OKF-EXTENSION.md`, `__file__`-relative
> to the vendored `okf.py` (SPEC REQ-OKF-FAM-003). Terminology and REQ ids match
> `skills/yf-okf/SPEC.md`.

## 0. Member identity

| Field | Value |
|:--|:--|
| `okf_spec:` member name | **OKF-RESEARCH** |
| Purpose | Structures a yf-research **report bundle** (`docs/research/<NNN>-<slug>/` or `Incubator/<slug>/research/<NNN>-<slug>/`) as an OKF-compatible dir-form bundle: a typed `Summary.md`, typed phase artifacts, and a typed source list, with the non-`.md` sidecar files (`sources.json`, `plan.yaml`) explicitly excluded from the frontmatter-`type` rule. |
| Bundle form | **dir-form** (always has an owning directory). |
| Selector | Every non-reserved `.md` in the bundle carries `okf_spec: OKF-RESEARCH`. |

## 1. `type` vocabulary (open vocab; OKF-RESEARCH owns this set)

| `type` value | Applies to (path in the bundle) |
|:--|:--|
| `Research Report` | `Summary.md` — the final synthesized report |
| `Research Artifact` | `artifacts/*.md` — phase outputs (triangulation, critique, cluster-*, etc.) |
| `Reference` | `sources.md` — the human-readable source list with verbatim quotes + credibility |

`diagrams/*.png` and `scripts/*.py` are non-`.md` and out of the frontmatter-`type` surface (§3).

## 1a. Migration: role → type map (SPEC REQ-OKF-MIG-004)

`migrate` assigns each non-reserved `.md` a `type` from this ordered path-glob → type map
(first match wins). A file matching no rule falls back to the member default and the fallback is
**recorded** (`type_source: default-fallback`).

| Path glob | `type` |
|:--|:--|
| `Summary.md` | `Research Report` |
| `artifacts/*` | `Research Artifact` |
| `sources.md` | `Reference` |
| `*` | `Concept` |

## 1b. Migration: reserved-file sources (SPEC REQ-OKF-MIG-005)

Research uses the `_index.md` index convention and has no in-body phase-log, so `log.md` is
**scaffolded** as a conformant skeleton by the base migrate; the fine `_index.md`-ledger → `log.md`
content split is the Epic 4 adapter's job (§5).

| Reserved target | Source |
|:--|:--|
| `index.md` | `_index.md` |
| `log.md` | `scaffold` |

## 2. Required extension frontmatter keys

Beyond OKF's `type` MUST and the `okf_spec:` selector, an OKF-RESEARCH `Summary.md` carries the yf
producer keys today rendered as the prose header line
(`**Research project:** … · **Phase:** … · **Date:** …`):

| Key | Force on `Summary.md` | Notes |
|:--|:-:|:--|
| `type` | MUST | `Research Report` |
| `okf_spec` | MUST | `OKF-RESEARCH` |
| `idx` | MUST | Global research index `NNN` (e.g. `001`) — dual of the `Research project:` `NNN` |
| `topic` | MUST | Research topic / slug — dual of the `Research project:` slug |
| `created` | MUST | ISO-8601 (`YYYY-MM-DD`) — dual of `Date:` |
| `status` | SHOULD | Pipeline phase (`retrieve` … `package`) — dual of `Phase:` |

`artifacts/*.md` (`Research Artifact`) carry `type`/`okf_spec`/`idx` plus a `phase:` key. `sources.md`
(`Reference`) carries `type`/`okf_spec`/`idx`; its GFM citation links are kept as-is — the OKF
`# Citations` heading convention is an explicit **non-goal** (SPEC §1; `OKF-BASELINE.md` §7).

### 2a. Non-`.md` exclusion (SPEC REQ-OKF-060)

The following bundle sidecars are **non-`.md`** and are **excluded** from the frontmatter-`type`
rule (REQ-OKF-003); `check_conformance` does not flag them for missing frontmatter:

| File | Kind |
|:--|:--|
| `sources.json` (+ `sources.<cluster>.json`) | machine source records |
| `plan.yaml` | pipeline DAG plan |
| `diagrams/*.png` | rendered diagrams |
| `scripts/*.py` | analysis scripts |

## 3. Reserved subdirs / files

| Reserved path | Holds | Replaces (legacy) |
|:--|:--|:--|
| `index.md` | Bundle listing (`#` heading + `- description` bullets); MAY carry `okf_version` | `_index.md` (SPEC REQ-OKF-001) |
| `log.md` | Newest-first ISO-8601 pipeline history | the timestamped `_index.md` ledger (SPEC REQ-OKF-002) |
| `artifacts/` | `Research Artifact` concept docs | (unchanged) |
| `diagrams/` | rendered `.png` (non-`.md`, excluded) | (unchanged) |
| `scripts/` | analysis `.py` (non-`.md`, excluded) | (unchanged) |

Reserved `index.md` / `log.md` carry **no `type` and no `okf_spec`** (SPEC REQ-OKF-031).

## 4. The dual field set (SPEC REQ-OKF-020 / REQ-OKF-021)

`Summary.md` today carries a single inline prose header line rather than discrete `**Field:**`
lines. OKF-RESEARCH dual-writes that header's fields with frontmatter keys — one writer, one model,
both representations:

| Prose header token | Frontmatter key |
|:--|:--|
| `Research project:` `NNN` | `idx` |
| `Research project:` slug | `topic` |
| `Phase:` | `status` |
| `Date:` | `created` |

**Placement invariant (SPEC REQ-OKF-010).** The frontmatter block (and the prose header line, if
retained) sit **above the first `## ` heading** (`## Executive summary`).

## 5. Index-body convention — decision to lock (SPEC REQ-OKF-001; plan R6)

yf-research's legacy `_index.md` is a **timestamped GFM table** — `| Timestamp | Phase | Artifact |
Description |` (`index_manager.py` `HEADER_TEMPLATE`) — that doubles as both the artifact manifest
**and** the update ledger. OKF splits those two roles:

- The **update-ledger** role (timestamps, newest-first) becomes reserved **`log.md`** (SPEC
  REQ-OKF-002).
- The **listing** role becomes reserved **`index.md`** — the OKF progressive-disclosure body
  (`#` heading + `- [artifact](path) - description` bullets).

**This is the reconciliation decision to lock in Issue 4.1.** Open sub-decisions the ratification
gate must confirm:

1. Whether `index.md` keeps a table shape (Artifact | Description) or converts to the OKF bullet
   listing.
2. Where the per-entry `Phase` column lands (drop from `index.md`, keep as a bullet annotation, or
   carry only in `log.md`).
3. The rename fan-out: `index_manager.py` (`INDEX_FILENAME`, `HEADER_TEMPLATE`, `_parse_rows`),
   `link_normalizer.py`, the packager, the formula, `spec/`, and tests all reference `_index.md` —
   a partial rename silently breaks link-normalization (plan R6, Issue 4.3 enumerates targets;
   Issue 6.2 drives link-normalization against the renamed `index.md`).

## 6. Deltas from the OKF baseline / decisions to lock (for the coordinator)

- **`Summary.md` / `artifacts/*.md` / `sources.md` carry no YAML frontmatter today** — metadata is a
  prose header line or plain GFM. Adopting OKF-RESEARCH adds a dual frontmatter block above the
  first `## ` on each.
- **`_index.md` → `index.md` + `log.md` split** (SPEC REQ-OKF-001/002) — the index-body
  reconciliation above; **decision to lock in Issue 4.1**, fan-out in Issue 4.3.
- **Non-`.md` exclusion is a non-gap** — `sources.json` / `plan.yaml` / `diagrams/*.png` were never
  in scope; OKF-RESEARCH records the exclusion so `check_conformance` never flags them.
- **`# Citations` is a non-goal** — `sources.md` keeps GFM citation links; not normalized to OKF's
  numbered/bare-URL form.

## 7. References

- `skills/yf-okf/SPEC.md` — REQ-OKF-001/002/003, 010, 020/021, 030/031, 060, FAM-001..003.
- `skills/yf-okf/spec/OKF-BASELINE.md` (upstream OKF v0.2) and
  `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` (the yf layer this member composes on).
- `skills/yf-research/scripts/index_manager.py` (`_index.md` table shape) and `link_normalizer.py`.
- `docs/research/001-okf-compliance-delta/` — a real OKF-RESEARCH-candidate bundle
  (`Summary.md`, `artifacts/`, `sources.md`, `sources.json`, `plan.yaml`).

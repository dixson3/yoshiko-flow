# OKF-INCUBATOR — yf-incubator per-skill OKF extension

> **Status: DRAFT (plan-029, Epic 1, Issue 1.3).** Proposal only. Epic 2's impact assessment
> stress-tests this member; the human ratification gate approves it before any implementation
> (Epics 5/6) applies it. Composed by the engine as
> **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ OKF-INCUBATOR** (SPEC REQ-OKF-FAM-001). Discovered by
> `resolve_extension("yf-incubator")` at `skills/yf-incubator/OKF-EXTENSION.md`, `__file__`-relative
> to the vendored `okf.py` (SPEC REQ-OKF-FAM-003). Terminology and REQ ids match
> `skills/yf-okf/SPEC.md`.

## 0. Member identity

| Field | Value |
|:--|:--|
| `okf_spec:` member name | **OKF-INCUBATOR** |
| Purpose | Makes a yf-incubator **state file** OKF-compatible by adding a `type: Incubator` to its existing YAML frontmatter, covering **both** bundle forms: a single-file incubator (`Incubator/<slug>.md`, exempt from reserved files) and a dir-form incubator (`Incubator/<slug>/` with a state file), whose body `## Files` / `## Decision log` sections map to reserved `index.md` / `log.md`. |
| Bundle form | **single-file OR dir-form** (unique among the three members). |
| Selector | The state file carries `okf_spec: OKF-INCUBATOR`. |

yf-incubator is **closest to OKF today** — it already emits YAML frontmatter; it lacks only the one
mandatory `type` key (research 001).

## 1. `type` vocabulary (open vocab; OKF-INCUBATOR owns this set)

| `type` value | Applies to |
|:--|:--|
| `Incubator` | the state file — `Incubator/<slug>.md` (single-file) or `Incubator/<slug>/<state>.md` (dir-form) |

`Incubator/INDEX.md` (the root index the `incubator-index.py` indexer generates across all
incubators) is a reserved listing file, not a typed concept document (§3).

## 1a. Migration: role → type map (SPEC REQ-OKF-MIG-004)

The dir-form state file is `Incubator/<kebab>/README.md` (yf-incubator SKILL.md). `migrate` types
it `Incubator`; any other supporting `.md` in the bundle (e.g. `00Index.md`, `Onboarding.md`) has no
member type and falls back to the default `Concept`, recorded (`type_source: default-fallback`) —
those are the per-skill adapter's to classify (Epic 5). First match wins.

| Path glob | `type` |
|:--|:--|
| `README.md` | `Incubator` |
| `*` | `Concept` |

## 1b. Migration: reserved-file sources (SPEC REQ-OKF-MIG-005)

**Key divergence from OKF-PLAN.** For an incubator the `README.md` is the **typed state file**
(`type: Incubator`), *not* the bundle listing — so `migrate` **keeps** `README.md` and **scaffolds**
`index.md`/`log.md` as conformant skeletons (it does **not** rename `README.md` → `index.md` the way
OKF-PLAN does). The fine `## Files` → `index.md` / `## Decision log` → `log.md` promotion rendering
is the Epic 5 adapter's job (§3b, §5).

| Reserved target | Source |
|:--|:--|
| `index.md` | `scaffold` |
| `log.md` | `scaffold` |

## 2. Required extension frontmatter keys (7 → 8)

The state file already carries a **7-key** frontmatter (`title`, `created`, `tags`, `status`,
`last_reviewed`, `priority`, `aliases` — SKILL.md verbatim block). OKF-INCUBATOR adds exactly one
key: **`type: Incubator`** (7 → 8), plus the yf `okf_spec:` selector:

| Key | Force | Notes |
|:--|:-:|:--|
| `type` | **MUST (new)** | `Incubator` — the single added key that brings the file to OKF conformance |
| `okf_spec` | MUST | `OKF-INCUBATOR` |
| `title` | existing | Human-readable name |
| `created` | existing | ISO-8601 creation date |
| `tags` | existing | `[incubator, <topic tags>]` |
| `status` | existing | `incubating` \| `scoping` \| `exploring` \| `converging` \| `concluded` \| `parked` \| `abandoned` |
| `last_reviewed` | existing | ISO-8601; the indexer's managed-vs-unmanaged discriminator |
| `priority` | existing | `high` \| `normal` \| `low` |
| `aliases` | existing | `[<kebab-name>]` |

**Merge-and-preserve (SPEC REQ-OKF-070).** The seven existing keys are retained byte-for-byte; only
`type` and `okf_spec` are added. This is the well-behaved-producer path — `check_conformance` /
`migrate` never drop `aliases`, `tags`, or any foreign key.

## 3. Reserved subdirs / files — dir-form mapping and the single-file exemption

### 3a. Single-file-bundle exemption (SPEC REQ-OKF-050)

A single-file incubator — one `.md` at `Incubator/<slug>.md` with **no owning directory** — is
**exempt** from the reserved `index.md` / `log.md` requirement (SPEC REQ-OKF-001/002). It carries
only its own frontmatter + `type` + `okf_spec`. Its `## Decision log` and `## Files` sections remain
in-body. This is the exemption that keeps single-file incubators viable (plan R4).

### 3b. Dir-form reserved-file mapping (promotion)

When a single-file incubator gains substructure it is **promoted to dir-form**, at which point the
body sections map to OKF reserved files:

| Body section (single-file) | Reserved file (dir-form) | Rule |
|:--|:--|:--|
| `## Files` (or `## Layout`) | `index.md` | listing body; SPEC REQ-OKF-001 |
| `## Decision log` | `log.md` | newest-first ISO-8601 entries; SPEC REQ-OKF-002 |

The remaining body sections (`## Resume`, `## Status`, `## Premise`, `## Open questions`,
`## Beads to file`) stay in the state file, which keeps `type: Incubator` frontmatter. `## Decision
log` and `## Beads to file` are never dropped (yf-incubator SPEC REQ-INCUB invariant); promotion
**moves** `## Decision log` into `log.md` rather than deleting it. Reserved `index.md` / `log.md`
carry **no `type` and no `okf_spec`** (SPEC REQ-OKF-031).

## 4. The dual field set (SPEC REQ-OKF-020 / REQ-OKF-021)

yf-incubator carries **no `**Field:**` header lines** — its metadata is already native YAML
frontmatter. The dual field model therefore **does not apply**: there is no `**Field:**` surface to
dual-write, and reads are frontmatter-only (no `**Field:**` fallback path). OKF-INCUBATOR is a
frontmatter-only member. The placement invariant (SPEC REQ-OKF-010) is satisfied trivially —
frontmatter already precedes the first `## ` heading (`## Resume`).

## 5. Index-body convention

For a dir-form incubator, `index.md` is the OKF progressive-disclosure listing (`#` heading +
`- description` bullets) rendered from the former `## Files` / `## Layout` body. `Incubator/INDEX.md`
(the cross-incubator root index the indexer generates) is a separate, pre-existing listing surface
and is out of the per-bundle OKF model — it is not a bundle-root `index.md` and gains no `type`.

## 6. Deltas from the OKF baseline / decisions to lock (for the coordinator)

- **Smallest delta of the three: add `type: Incubator` (7 → 8 keys)** — yf-incubator already emits
  conformant YAML frontmatter; only the mandatory `type` key is missing (research 001). Mechanical,
  merge-and-preserve.
- **Single-file exemption is load-bearing** — most incubators are single files with no owning
  directory; they must stay reserved-file-exempt (plan R4). The exemption is asserted here and in
  SPEC REQ-OKF-050.
- **Dir-form promotion mapping** (`## Files` → `index.md`, `## Decision log` → `log.md`) applies
  **only** on promotion; existing single-file incubators are grandfathered (SPEC REQ-OKF-MIG-001),
  never bulk-rewritten.
- **`Incubator/INDEX.md` scope** — the cross-incubator root index is **not** a per-bundle
  `index.md`; confirm it stays outside the OKF bundle model (decision to lock in Epic 5).

## 7. References

- `skills/yf-okf/SPEC.md` — REQ-OKF-001/002/003, 010, 020/021, 030/031, 050, 070, MIG-001,
  FAM-001..003.
- `skills/yf-okf/spec/OKF-BASELINE.md` (upstream OKF v0.2) and
  `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` (the yf layer this member composes on).
- `skills/yf-incubator/SKILL.md` (the verbatim 7-key frontmatter + body-section order) and
  `skills/yf-incubator/scripts/incubator-index.py` (`state_file`, single-file vs dir-form,
  `Incubator/INDEX.md`).
- `skills/yf-incubator/SPEC.md` — `## Decision log` / `## Files` / `## Beads to file` invariants.

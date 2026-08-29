---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: local-artifacts

How yf-plan / yf-research / yf-incubator structure their output bundles, drawn
directly from installed-skill specs, the manager scripts, and a real completed
plan folder. Method: **direct** (local repo reads; no web).

Focus questions answered: reserved filenames, YAML-frontmatter usage across the
three tools, citation-heading conventions, and what `plan_manager.py`'s audit
actually checks.

## 1. yf-plan plan-folder layout & reserved filenames

The portability contract fixes a set of reserved files at the plan root. None
uses YAML frontmatter; plan metadata is carried as bold `**Field:**` header
lines inside `plan.md`.

> "REQ-PORT-001: Every plan folder ... must contain `README.md` at the plan root
> with file-map and reading-order sections." [L1](sources.md#l1)

> "REQ-PORT-002: Every plan folder must contain `context.md` at the plan root
> with non-empty required sections: Project environment, Tool inventory, Paths,
> Operator identity, Runtime assumptions." [L1](sources.md#l1)

> "REQ-PORT-005: Every non-exclude row in plan.md's Upstream Issues table must
> have a corresponding `references/upstream-<N>.md` file" [L1](sources.md#l1)

> "REQ-PORT-006: The number of `reviews/pass-*.md` files must equal the number of
> `^- \d{4}-\d{2}-\d{2} review:` lines in plan.md's phase log." [L1](sources.md#l1)

Reserved plan filenames: `plan.md`, `README.md`, `context.md`, optional
`motivation.md`, `references/upstream-<N>.md`, `reviews/pass-<N>.md`. The **phase
log** is an in-`plan.md` section (a `**Phase log:**` bold header followed by
`- YYYY-MM-DD <phase>:` bullet lines), NOT a separate `log.md` file [L4](sources.md#l4). The
README index file is `README.md`, NOT `index.md` [L1](sources.md#l1)[L4](sources.md#l4).

## 2. Frontmatter: absent in plan-028 (real folder evidence)

plan-028 (`plan-028-james-dixson-a9738b`, status `complete`) contains exactly:
`plan.md`, `README.md`, `context.md`, `upstream-triage.md`,
`references/upstream-86.md`, `references/upstream-87.md`, `reviews/pass-1.md`,
`reviews/pass-2.md`. Every file's first line is a Markdown `#` heading — there is
**no YAML `---` frontmatter block anywhere**. plan.md metadata is bold-field
headers, not frontmatter:

> "# Plan: Fix credibility_scorer tz-naive crash ...
>
> **ID:** plan-028-james-dixson-a9738b
> **Author:** james-dixson
> **Created:** 2026-07-15
> **Status:** complete
> **Epic:** yf-mol-181
> **Fingerprint:** 832dd5b3...
> **Phase log:**
> - 2026-07-15 scoping: initial scope captured" [L4](sources.md#l4)

**Absence finding (mechanical, load-bearing for OKF delta):** yf-plan output has
NO `type` frontmatter, no `okf_version`, no YAML block at all — metadata lives in
`**Field:**` prose headers. This is the conceptual gap the OKF `type`/frontmatter
model would require closing.

## 3. What plan_manager.py's audit actually checks

The audit is purely mechanical (stdlib regex/grep; no LLM, no frontmatter
parsing). Six checks:

> "# 1. README.md ... # 2. context.md — required sections non-empty ... # 4.
> references/upstream-*.md — one file per non-exclude row ... # 5.
> reviews/pass-*.md — count == phase-log review line count ... # 6. No dangling
> external refs across all plan files." [L2](sources.md#l2)

Reserved-name matching is by **heading name**, not frontmatter key:

> "_CONTEXT_REQUIRED_SECTIONS = (\"Project environment\", \"Tool inventory\",
> \"Paths\", \"Operator identity\", \"Runtime assumptions\") ...
> _README_REQUIRED_SECTIONS = (\"File map\", \"Reading order\")" [L3](sources.md#l3)

Overall status is `fail` iff any finding is `fail`; pre-activation plans are
grandfathered:

> "PORTABILITY_ACTIVATION_DATE = \"2026-04-05\"" [L3](sources.md#l3)
> "any_fail = any(f[\"status\"] == \"fail\" for f in findings)" [L2](sources.md#l2)

The audit checks **file existence, section headings, count-equality, and dangling
absolute/`../` paths** — it does NOT validate frontmatter, a `type` field, or a
citation heading. An OKF conformance layer would be additive to this audit.

## 4. yf-research research-dir layout & citation convention

> "REQ-DATA-002: Each research topic uses the layout: `plan.yaml`, `Summary.md`,
> `sources.json`, `_index.md`, `scripts/`, `artifacts/` (with `cluster-<name>.md`,
> `triangulation.md`, `critique.md`)." [L5](sources.md#l5)

Reserved index filename is **`_index.md`** (underscore prefix), NOT `index.md`;
it is the artifact manifest with a single writer:

> "REQ-DATA-005: `_index.md` is the artifact manifest, created/updated only via
> `index_manager.py` (`init`, `add`)." [L5](sources.md#l5)

Citations: every claim carries an inline `[N]` resolving to a `sources.json`
entry; the quote convention is a blockquote with a trailing bracket id — there is
no dedicated "Sources"/"References" heading requirement, and no OKF-style citation
heading:

> "REQ-DATA-003: `sources.json` holds every source with a credibility score;
> every factual claim in `Summary.md`/artifacts carries an inline `[N]` that
> resolves to a `sources.json` entry." [L5](sources.md#l5)

> "**Direct quotes over paraphrase.** When citing, include a direct quote (`> \"...\"
> [N]`)" [L6](sources.md#l6)

**Frontmatter absence finding:** research output is plain GFM with no frontmatter.
`_index.md` is generated from a heading template, not a YAML block:

> "HEADER_TEMPLATE = \"\"\"# Research Index: {topic}\"" [L7](sources.md#l7)

Confirmed against the live file, whose first line is a `#` heading followed by a
GFM table (no `---`):

> "# Research Index: OKF ... compliance-delta ...
>
> | Timestamp | Phase | Artifact | Description |
> |-----------|-------|----------|-------------|" [L7](sources.md#l7)

> "Every markdown artifact this skill writes (`Summary.md`, `sources.md`,
> `artifacts/*.md`, `_index.md`, the packaged report) is plain **GFM** — never
> Obsidian `[[wikilinks]]`" [L6](sources.md#l6)

## 5. yf-incubator layout — the one tool that DOES use frontmatter

Unlike yf-plan and yf-research, incubators are explicitly **frontmatter-keyed**:

> "Each incubator is a portable, frontmatter-keyed [markdown state file]" [L8](sources.md#l8)

> "REQ-INCUB-002 ... the state file frontmatter shall carry `title`, `created`,
> [`status`, `priority`, `last_reviewed`] ... ordered body sections `## Status`,
> `## Premise`, `## Open questions`, `## Decision log`, `## Files`, and `## Beads
> to file`; `## Decision log` and `## Beads to file` are never dropped" [L8](sources.md#l8)

Reserved layout: directory form `Incubator/<kebab>/README.md` (with `research/`,
`references/`, `plans/` alongside) or single-file `Incubator/<kebab>.md`; the
triage index is `Incubator/INDEX.md` [L8](sources.md#l8). Root reserved file is `README.md`, not
`index.md`.

## Cross-tool summary (OKF-delta-relevant facts)

| Facet | yf-plan | yf-research | yf-incubator |
|-------|---------|-------------|--------------|
| YAML frontmatter | **No** — `**Field:**` headers in plan.md [L4](sources.md#l4) | **No** — plain GFM, `[N]` cites [L6](sources.md#l6)[L7](sources.md#l7) | **Yes** — title/created/status/priority/last_reviewed [L8](sources.md#l8) |
| Reserved index file | `README.md` (File map + Reading order) [L1](sources.md#l1) | `_index.md` (underscore) [L5](sources.md#l5) | `README.md` + `Incubator/INDEX.md` [L8](sources.md#l8) |
| Log surface | in-`plan.md` `**Phase log:**` section, no `log.md` [L4](sources.md#l4) | `_index.md` manifest table [L5](sources.md#l5)[L7](sources.md#l7) | `## Decision log` body section [L8](sources.md#l8) |
| Citation convention | n/a | inline `[N]` → sources.json; `> "..." [N]` [L5](sources.md#l5)[L6](sources.md#l6) | n/a |
| `type` / `okf_version` field | absent [L4](sources.md#l4) | absent [L6](sources.md#l6) | absent (frontmatter has title/status but no `type`) [L8](sources.md#l8) |
| Audit/validation | mechanical `plan_manager.py audit` (6 checks, no frontmatter) [L2](sources.md#l2)[L3](sources.md#l3) | citation-resolution check (packager) [L5](sources.md#l5) | frontmatter/section schema test [L8](sources.md#l8) |

**Key structural facts for the OKF delta:** (1) None of the three tools emits an
OKF `type` or `okf_version` field. (2) Only yf-incubator uses YAML frontmatter;
yf-plan uses `**Field:**` prose headers and yf-research uses none. (3) Reserved
index filenames diverge from OKF's `index.md`: yf-plan uses `README.md`,
yf-research uses `_index.md`. (4) The "log" is never a reserved `log.md`: it is an
in-`plan.md` phase-log section (yf-plan), a manifest table (yf-research), or a
`## Decision log` section (yf-incubator). (5) yf-plan's audit is heading-name and
count based (mechanical, no LLM), so an OKF conformance check would be an additive
layer, not a modification of the existing audit.

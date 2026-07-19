---
type: Reference
okf_spec: OKF-RESEARCH
---
# Sources — OKF compliance-delta

Every source id used in `Summary.md` resolves to a section below. Credibility is shown as
`[overall/100 · category]`. **Read the `category` as the trust signal and disregard the numeric
`overall`.** The `overall` is an automated batch-scorer output that lands every source in the
questionable band (~41) only because the scorer's domain heuristic does not recognize github.com /
pypi.org / raw.githubusercontent.com or local `skills/...` paths and assigns them a low
`domain_authority` (30) — the 41 is an internally-consistent score of the *wrong inputs*, not a
corrupted number. The `category` (`high_trust` / `verify`) is a **manual override applied on
domain-authority grounds, not recomputed from the rubric formula**: the OKF SPEC/README/reference
bundles and the local skill artifacts are primary, authoritative sources on the exact matter under
study (the spec's own text; the tools' own code), a Tier-1 `domain_authority` regardless of URL
host. Third-party tooling packages (E4–E10) are labeled `verify`, not `high_trust` — the override
lifts primary sources, it does not launder hobby-scale tools. Per-source rationale is in
`sources.json` `credibility.basis`.

## okf-spec-primary (S)

### S1

[41/100 · high_trust] Open Knowledge Format (OKF) — SPEC.md (Version 0.1 — Draft) —
<https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md>

> "The format is intentionally minimal: a directory of markdown files with YAML frontmatter. There is no schema registry, no central authority, and no required tooling. If you can `cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it."

The authoritative OKF specification: bundle structure, reserved filenames (`index.md`, `log.md`),
required YAML frontmatter with a REQUIRED `type` field, cross-linking (bundle-relative links),
citations, conformance rules (§9), and versioning (`okf_version`).

Load-bearing normative quotes (verbatim from SPEC.md; also in `artifacts/cluster-okf-spec-primary.md`):

Reserved filenames (§3.1) — `index.md`/`log.md` reserved; all other `.md` files are concept docs:

> "The following filenames have defined meaning at any level of the hierarchy and MUST NOT be used for concept documents: | `index.md` | Directory listing. See §6. | `log.md` | Update history. See §7. | ... All other `.md` files are concept documents."

`type` field — REQUIRED in the frontmatter template:

> "`type` — A short string identifying the kind of concept. Consumers use this for routing, filtering, and presentation." — marked **REQUIRED**.

Conformance test (§9) — the exact two-item hard bar (plus reserved-file structure when present):

> "1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block. / 2. Every frontmatter block contains a non-empty `type` field. / 3. Every reserved filename (`index.md`, `log.md`) follows the structure described in §6 and §7 respectively when present."

Extension mechanism (§4.1) — the SHOULD-level (not MUST) preservation clause load-bearing under Q3:

> "**Extensions:** Producers MAY include any additional keys. Consumers SHOULD preserve unknown keys when round-tripping and SHOULD NOT reject documents with unrecognized fields."

### S2

[41/100 · high_trust] OKF README — GoogleCloudPlatform/knowledge-catalog/okf —
<https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/README.md>

> "OKF is a **universal, vendor-neutral format** for representing knowledge as plain markdown files with YAML frontmatter. It is **not tied to any particular agent, framework, model provider, or serving system**."

### S3

[41/100 · high_trust] Example OKF concept document — ga4/references/metrics/avg_pageviews.md —
<https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/ga4/references/metrics/avg_pageviews.md>

> "---\ntype: Reference\nresource: https://developers.google.com/analytics/bigquery/basic-queries\ntitle: Average Pageviews\ndescription: The average number of pageviews per user.\ntags:\n- metric\ntimestamp: '2026-05-28T22:51:43+00:00'\n---\n\nThe average number of pageviews per user.\n\n```sql\nSUM(page_view_count) / COUNT(*)\n```\n\n# Citations\n- https://developers.google.com/analytics/bigquery/basic-queries"

A real conformant concept doc: frontmatter with `type/resource/title/description/tags/timestamp`
and a body ending in a `# Citations` heading using a bare-URL bullet list (not numbered).

### S4

[41/100 · high_trust] Example OKF index.md — ga4/index.md (bundle root) —
<https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/ga4/index.md>

> "# Subdirectories\n\n* [datasets](datasets/index.md) - A sample of obfuscated Google Analytics BigQuery event export data ...\n* [references](references/index.md) - This directory contains specifications for data joins and definitions ...\n* [tables](tables/index.md) - Contains Google Analytics event export data from the `ga4_obfuscated_sample_ecommerce` dataset."

A real bundle-root `index.md`: contains NO frontmatter, does NOT declare `okf_version`, and uses
**relative** links — confirming both `okf_version` and `/`-absolute links are optional and unused
in the reference bundles.

### S5

[41/100 · high_trust] Absence findings — okf_version usage and log.md files in knowledge-catalog —
<https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf>

> "gh search code okf_version --repo GoogleCloudPlatform/knowledge-catalog => only match: 'okf/SPEC.md: `okf_version: \"0.1\"` in a bundle-root `index.md`'. Recursive tree filter for '*log.md' => (no results)."

Both `okf_version` and `log.md` are spec'd-but-unexercised in the reference implementation.

## ecosystem-interop (E)

### E1

[58/100 · high_trust] Introducing the Open Knowledge Format (Google Cloud Blog) —
<https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>

> "That's why today, we're introducing the Open Knowledge Format (OKF), an open specification that formalizes the LLM-wiki pattern into a portable, interoperable format. ... We have also updated Google Cloud's Knowledge Catalog to be able to ingest Open Knowledge Format and serve it to our agents."

Official GCP announcement of OKF v0.1 (June 2026). Vendor-bias noted.

### E2

[41/100 · high_trust] knowledge-catalog/okf README (GoogleCloudPlatform) —
<https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf>

> "Anyone can produce OKF — humans authoring by hand, agents built on any framework (Google ADK, LangChain, custom), export pipelines from existing catalogs (Dataplex, Unity Catalog, Collibra, ...), or scripts walking a database. Anyone can serve and consume OKF — a static file server, a knowledge-management UI (Obsidian, Notion, MkDocs), an LLM loading files into context, a search index, or a graph viewer like the one bundled in this repo."

Producer/consumer lists are *intended targets*, not attestations of live adoption.

### E3

[41/100 · high_trust] OKF v0.1 SPEC.md (GoogleCloudPlatform/knowledge-catalog) —
<https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>

> "The format is intentionally minimal: a directory of markdown files with YAML frontmatter. There is no schema registry, no central authority, and no required tooling. If you can `cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it."

### E4

[41/100 · verify] thisismydesign/okf-lint (npm @thisismydesign/okf-lint) —
<https://github.com/thisismydesign/okf-lint>

> "A linter for the Open Knowledge Format (OKF) — Google's open, human- and agent-friendly format for knowledge catalogs. ... Reports errors when a bundle violates a mandatory OKF conformance requirement (e.g. a concept document is missing its `type` field)."

Errors on missing `type`; warns on missing `index.md`. Solo/hobby-scale.

### E5

[41/100 · verify] okft v0.1.0 (PyPI) — OKF validator + MCP server —
<https://pypi.org/project/okft/>

> "okft lint — validate a bundle against the OKF v0.1 spec, plus hygiene checks (broken links, orphaned concepts, malformed timestamps). ... okft serve — expose a bundle to any MCP-capable AI agent (Claude, Gemini CLI, Cursor, ...) as a set of navigation tools: overview, read, search, list."

### E6

[41/100 · verify] okf-schema v0.9.0 (PyPI) — CLI + library with JSONSchema frontmatter validation —
<https://pypi.org/project/okf-schema/>

> "okf-schema is a CLI tool and Python library for working with OKF (Open Knowledge Format) bundles with JSONSchema validation of the frontmatter metadata, and formatting capabilities while preserving comments. ... The `type` field in a concept's frontmatter tells okf-schema which schema file to load."

### E7

[41/100 · verify] okflint v0.3.0 (PyPI) — "the Ruff of documentation" —
<https://pypi.org/project/okflint/0.3.0/>

> "The Ruff of documentation. A deterministic compliance linter for documentary bases in Open Knowledge Format (OKF). ... okflint validate — normative compliance gate. exit 0 if conformant, exit 1 otherwise. Designed for pre-commit hooks and CI."

### E8

[41/100 · verify] okfcli/okf — Go CLI toolkit for OKF (vendor-neutral alternative) —
<https://github.com/okfcli/okf>

> "okf creates, validates, lints, indexes, searches, and inspects OKF knowledge bundles. One static binary, no runtime dependencies... Google's reference OKF implementation is Python + Gemini + BigQuery — vendor-locked to Google's cloud. okf is the vendor-neutral alternative: a single Go binary that works anywhere, speaks JSON natively, and is designed to be driven by any AI agent on any provider."

### E9

[41/100 · verify] OKF Conformance Suite (WitsCode) —
<https://witscode.com/okf-conformance>

> "OKF conformance is whether a knowledge bundle correctly follows the Open Knowledge Format, Google Cloud's open spec for agent-readable markdown. WitsCode maintains a free, open-source conformance suite that checks any OKF bundle and tells you, pass or fail, whether it follows the spec. It runs locally and needs no account."

### E10

[41/100 · verify] okf-cli v0.3.1 (PyPI) — markdown-to-OKF converter —
<https://pypi.org/project/okf-cli/0.3.1/>

> "Converts plain markdown into OKF-conformant knowledge bundles. Domain experts write '# Title' then '> description' — okf bundle generates frontmatter, type, timestamps, and index files."

### E11

[41/100 · verify] MCP vs llms.txt vs Agent Skills: Complete Comparison (2026) —
<https://signb.ee/blog/multi-protocol-future-mcp-skills-llmstxt>

> "Four protocols make APIs discoverable by AI agents: llms.txt (static description), OpenAPI (machine-readable spec), Agent Skills (structured capability), and MCP servers (runtime tools). Each serves a different layer."

Secondary explainer / comparable-formats context.

### E12

[41/100 · verify] Agent Skills Explained: SKILL.md vs MCP (DevToolLab, 2026) —
<https://devtoollab.com/blog/agent-skills-open-standard-guide>

> "The reason is boring in the best way: the entire spec is two required YAML fields and a Markdown body. No JSON-RPC, no auth handshake, no server process to keep alive. A competent engineer can add support to any agent tool in an afternoon. ... Agent Skills [is] A folder convention (SKILL.md + files)."

### E13

[41/100 · verify] The complete guide to agent readability (Agent Ready) —
<https://agent-ready.dev/complete-guide-to-agent-readability>

> "Metadata — canonical link, html lang, og:title, og:description, meta description > 50 chars, and at least one JSON-LD block. ... MCP (Model Context Protocol) — discovery for AI clients calling remote tools and resources. Card at /.well-known/mcp.json per SEP-1649."

Secondary; comparable discoverability-signal landscape.

### E14

[46/100 · verify] Open Knowledge Format — portable digital map of your data as code (Medium, Google Cloud Community) —
<https://medium.com/google-cloud/open-knowledge-format-portable-digital-map-of-your-data-as-code-45703ac491a0>

> "The spec only enforces one field to be explicitly provided — `type`, and that's exactly the trick: standardize only the smallest possible interoperability surface while leaving everything else to the people producing the data."

## local-artifacts (L)

### L1

[41/100 · high_trust] yf-plan Portability Specification (REQ-PORT-001..008) —
`skills/yf-plan/spec/portability.md`

> "REQ-PORT-001: Every plan folder (under either `docs/plans/<plan-id>/` or `Incubator/<slug>/plans/<plan-id>/`) must contain `README.md` at the plan root with file-map and reading-order sections. ... REQ-PORT-002: Every plan folder must contain `context.md` at the plan root with non-empty required sections: Project environment, Tool inventory, Paths, Operator identity, Runtime assumptions. ... REQ-PORT-005: Every non-exclude row in plan.md's Upstream Issues table must have a corresponding `references/upstream-<N>.md` file ... REQ-PORT-006: The number of `reviews/pass-*.md` files must equal the number of `^- \\d{4}-\\d{2}-\\d{2} review:` lines in plan.md's phase log."

No YAML frontmatter mandated anywhere.

### L2

[41/100 · high_trust] plan_manager.py _audit_plan() — mechanical portability audit —
`skills/yf-plan/scripts/plan_manager.py`

> "# 1. README.md ... missing_sections = [s for s in _README_REQUIRED_SECTIONS if s not in rtxt] ... # 2. context.md — required sections non-empty (no unfilled placeholder lines) ... # 4. references/upstream-*.md — one file per non-exclude row ... # 5. reviews/pass-*.md — count == phase-log review line count ... # 6. No dangling external refs across all plan files. ... any_fail = any(f[\"status\"] == \"fail\" for f in findings)"

All stdlib regex/grep — no LLM, no frontmatter parsing. Heading-name based, not frontmatter-key based.

### L3

[41/100 · high_trust] plan_manager.py audit constants — required sections & activation date —
`skills/yf-plan/scripts/plan_manager.py`

> "PORTABILITY_ACTIVATION_DATE = \"2026-04-05\" ... _CONTEXT_REQUIRED_SECTIONS = (\n    \"Project environment\",\n    \"Tool inventory\",\n    \"Paths\",\n    \"Operator identity\",\n    \"Runtime assumptions\",\n) ... _README_REQUIRED_SECTIONS = (\"File map\", \"Reading order\")"

### L4

[41/100 · high_trust] Real completed plan folder plan-028 — file inventory + no frontmatter —
`docs/plans/plan-028-james-dixson-a9738b/`

> "# Plan: Fix credibility_scorer tz-naive crash ...\n\n**ID:** plan-028-james-dixson-a9738b\n**Author:** james-dixson\n**Created:** 2026-07-15\n**Status:** complete\n**Epic:** yf-mol-181\n**Fingerprint:** 832dd5b34e3a87acc96ef3180df330ccdbdb6310d49e6e8da05e557addad68a5\n**Phase log:**\n- 2026-07-15 scoping: initial scope captured"

Every file's first line is a `#` heading — NO YAML `---` frontmatter block anywhere. Metadata rides
as bold `**Field:**` header lines.

### L5

[41/100 · high_trust] yf-research Data Specification (REQ-DATA-001..007) — research dir layout —
`skills/yf-research/spec/data.md`

> "REQ-DATA-002: Each research topic uses the layout: `plan.yaml`, `Summary.md`, `sources.json`, `_index.md`, `scripts/`, `artifacts/` (with `cluster-<name>.md`, `triangulation.md`, `critique.md`). ... REQ-DATA-003: `sources.json` holds every source with a credibility score; every factual claim in `Summary.md`/artifacts carries an inline `[N]` that resolves to a `sources.json` entry. ... REQ-DATA-005: `_index.md` is the artifact manifest, created/updated only via `index_manager.py` (`init`, `add`)."

Reserved index file is `_index.md` (underscore prefix), NOT `index.md`.

### L6

[41/100 · high_trust] yf-research SKILL.md — dir scaffold, citation convention, GFM mandate —
`skills/yf-research/SKILL.md`

> "mkdir -p \"${research_dir}/scripts\" \"${research_dir}/artifacts\" \"${research_dir}/diagrams\" ... **Direct quotes over paraphrase.** When citing, include a direct quote (`> \"...\" [N]`) ... Every markdown artifact this skill writes (`Summary.md`, `sources.md`, `artifacts/*.md`, `_index.md`, the packaged report) is plain **GFM** — never Obsidian `[[wikilinks]]`"

No frontmatter used in research output.

### L7

[41/100 · high_trust] index_manager.py HEADER_TEMPLATE + real _index.md — no frontmatter —
`skills/yf-research/scripts/index_manager.py`

> "HEADER_TEMPLATE = \"\"\"# Research Index: {topic}\" ... (live file:) # Research Index: OKF (Open Knowledge Format) compliance-delta for yf-plan / yf-research / yf-incubator artifacts\n\n| Timestamp | Phase | Artifact | Description |\n|-----------|-------|----------|-------------|"

`_index.md` is a `#`-heading + GFM table, no YAML frontmatter. Reserved manifest filename is `_index.md`.

### L8

[41/100 · high_trust] yf-incubator SPEC (REQ-INCUB-001/002) — frontmatter-keyed state files —
`skills/yf-incubator/SPEC.md`

> "Each incubator is a portable, frontmatter-keyed [markdown state file] ... REQ-INCUB-002 *(testable)* the state file frontmatter shall carry `title`, `created`, [`status`, `priority`, `last_reviewed`] ... ordered body sections `## Status`, `## Premise`, `## Open questions`, `## Decision log`, `## Files`, and `## Beads to file`; `## Decision log` and `## Beads to file` are never dropped"

Incubators DO use YAML frontmatter (unlike yf-plan/yf-research), but carry no `type` key. Reserved
root file is `README.md`; triage index is `Incubator/INDEX.md`.

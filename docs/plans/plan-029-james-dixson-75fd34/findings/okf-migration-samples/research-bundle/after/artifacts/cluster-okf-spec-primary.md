---
type: Research Artifact
okf_spec: OKF-RESEARCH
cluster: okf-spec-primary · **Method:** direct (primary-source retrieval) · **Retrieved:**
  2026-07-17
---
# Cluster artifact: okf-spec-primary

**Cluster:** okf-spec-primary · **Method:** direct (primary-source retrieval) · **Retrieved:** 2026-07-17

## Locating the spec

OKF ("Open Knowledge Format") is specified in **one authoritative document**:
`okf/SPEC.md` inside `GoogleCloudPlatform/knowledge-catalog` (repo description:
"Google Cloud Knowledge Catalog Tools and Samples"; created 2026-07-17). The SPEC
self-identifies as **"Version 0.1 — Draft"** [S1](sources.md#s1). The `okf/README.md` names the
spec as the repository's primary contribution [S2](sources.md#s2). Three reference bundles ship
under `okf/bundles/` (`ga4`, `stackoverflow`, `crypto_bitcoin`) plus a reference
agent under `okf/src/`.

A companion `# Disclaimer` in the top-level README states: *"This repository and
its contents are not an official Google product."* — so OKF is a
GoogleCloudPlatform-published **draft**, not a ratified Google standard. `[uncertain]`
whether v0.1 will remain stable.

---

## OKF rules, enumerated (for the compliance-delta table)

Each row = one OKF rule + the verbatim spec quote a synthesizer can diff local
artifacts against. Section refs are to SPEC.md.

### Rule 1 — Required YAML frontmatter + `type:` field (SPEC §4.1, §9)

Every concept document MUST open with a YAML frontmatter block and that block MUST
carry a non-empty `type`.

> "1. A **YAML frontmatter block**, delimited by `---` on its own line at the start
> of the file and a closing `---` on its own line." [S1](sources.md#s1)

> "`type` — A short string identifying the kind of concept. Consumers use this for
> routing, filtering, and presentation." — marked **REQUIRED** in the frontmatter
> template. [S1](sources.md#s1)

Conformance restates it:

> "Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter
> block. / Every frontmatter block contains a non-empty `type` field." [S1](sources.md#s1)

### Rule 2 — Enumerated `type` values (SPEC §4.1)

There is **no closed enumeration**. `type` is an open vocabulary; only example
values are given, and consumers must tolerate unknowns.

> "Type values are **not** registered centrally. Producers SHOULD pick values that
> are descriptive and self-explanatory; consumers MUST tolerate unknown types
> gracefully (typically by treating them as generic concepts)." [S1](sources.md#s1)

Example values listed (non-normative):

> "Example values: `BigQuery Table`, `BigQuery Dataset`, `API Endpoint`, `Metric`,
> `Playbook`, `Reference`." [S1](sources.md#s1)

Reference bundle usage confirms free-form title-case strings, e.g. `type: Reference`
[S3](sources.md#s3), `type: BigQuery Dataset`, `type: BigQuery Table` [S1 appendix].

### Rule 3 — `okf_version` field (SPEC §11)

Optional; declared in exactly one place — the bundle-root `index.md` frontmatter,
which is the *only* index.md permitted to have frontmatter.

> "Bundles MAY declare the OKF version they target by including `okf_version: \"0.1\"`
> in a bundle-root `index.md` frontmatter block (the only place frontmatter is
> permitted in an `index.md`). Consumers that do not understand the declared version
> SHOULD attempt best-effort consumption rather than refusing the bundle." [S1](sources.md#s1)

**Absence finding:** a repo-wide `gh search code okf_version` matched **only the SPEC
prose** — none of the three shipped bundles actually declares `okf_version`, and the
ga4 bundle-root `index.md` has no frontmatter at all [S4](sources.md#s4)[S5](sources.md#s5). So `okf_version` is
spec'd-but-unexercised; it is never required for conformance (§9 does not list it).

### Rule 4 — Reserved filenames `index.md` and `log.md` (SPEC §3.1, §6, §7)

Two filenames are reserved at every hierarchy level and MUST NOT be used for concept
docs.

> "The following filenames have defined meaning at any level of the hierarchy and
> MUST NOT be used for concept documents: | `index.md` | Directory listing. See §6. |
> `log.md` | Update history. See §7. | ... All other `.md` files are concept
> documents." [S1](sources.md#s1)

**`index.md` — meaning (§6):** a progressive-disclosure directory listing.

> "An `index.md` file MAY appear in any directory... It enumerates the directory's
> contents to support **progressive disclosure**... Index files contain no
> frontmatter. The body uses one or more sections, each grouping concepts under a
> heading." [S1](sources.md#s1)

Real example (bundle root, no frontmatter, `#`-heading + bullet list with trailing
`- description`):

> "# Subdirectories\n\n* [datasets](datasets/index.md) - A sample of obfuscated
> Google Analytics BigQuery event export data..." [S4](sources.md#s4)

Note the exception in Rule 3: the **bundle-root** index.md MAY carry frontmatter *only*
to declare `okf_version`.

**`log.md` — meaning (§7):** an optional chronological change history, newest-first,
ISO-8601 date headings.

> "A `log.md` file MAY appear at any level of the hierarchy to record the history of
> changes to that scope. The format is a flat list of date-grouped entries, newest
> first... Date headings MUST use ISO 8601 `YYYY-MM-DD` form. Log entries are prose;
> the leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`, etc.) is a
> convention, not a requirement." [S1](sources.md#s1)

**Absence finding:** the reference repo contains **zero `log.md` files** (recursive
tree scan) — `log.md` is defined but never demonstrated [S5](sources.md#s5).

### Rule 5 — Citation / heading conventions (SPEC §4.2, §8)

Conventional (SHOULD, not MUST) body headings; citations gathered under `# Citations`.

> "The following section headings have **conventional** meaning and SHOULD be used
> when applicable: | `# Schema` | ... | `# Examples` | ... | `# Citations` | External
> sources backing claims in the body. See §8. |" [S1](sources.md#s1)

> "When a concept's body makes claims sourced from external material, those sources
> SHOULD be listed under a `# Citations` heading at the bottom of the document,
> numbered: `[1] [BigQuery public dataset announcement](https://...)`" [S1](sources.md#s1)

> "Citation links MAY be absolute URLs, bundle-relative paths, or paths into a
> `references/` subdirectory that mirrors external material as first-class OKF
> concepts." [S1](sources.md#s1)

**Practice-vs-spec variance:** the SPEC's §8 example uses **numbered** `[1] [text](url)`
entries, but the real ga4 concept uses a plain bulleted list of bare URLs under the
same heading:

> "# Citations\n- https://developers.google.com/analytics/bigquery/basic-queries" [S3](sources.md#s3)

Since these headings are SHOULD-level, both forms are conformant; only the `# Citations`
heading name is conventional. `[uncertain]` whether tooling parses the numbering.

### Rule 6 — Bundle-relative (absolute) link requirement (SPEC §5)

Two link forms; bundle-root-absolute (`/`-prefixed) is the **recommended** form.

> "### 5.1 Absolute (bundle-relative) links / Begin with `/`, interpreted relative to
> the bundle root. ... This is the **recommended** form because it is stable when
> documents are moved within their subdirectory." [S1](sources.md#s1)

> "### 5.2 Relative links / Standard markdown relative paths. `See the [neighboring
> concept](./other.md).`" [S1](sources.md#s1)

Link semantics are untyped and broken links are tolerated:

> "A link from concept A to concept B asserts a *relationship*. The specific kind of
> relationship ... is conveyed by the surrounding prose, not by the link itself." [S1](sources.md#s1)

> "Consumers MUST tolerate broken links — a link whose target does not exist in the
> bundle is not malformed; it may simply represent not-yet-written knowledge." [S1](sources.md#s1)

Note: `index.md` listings in the reference bundles actually use **relative** links
(`datasets/index.md`), not `/`-absolute — so "recommended" is not "required" [S4](sources.md#s4).

### Rule 7 — resource / tags / timestamp metadata model (SPEC §4.1)

All three are **optional/recommended**, not required. Verbatim definitions:

> "`title` — Human-readable display name. If omitted, consumers MAY derive a title
> from the filename." [S1](sources.md#s1)

> "`description` — A single sentence summarizing the concept. Used by `index.md`
> generators, search snippets, and previews." [S1](sources.md#s1)

> "`resource` — A URI that uniquely identifies the underlying asset the concept
> describes. Absent for concepts that describe abstract ideas rather than physical
> resources." [S1](sources.md#s1)

> "`tags` — A YAML list of short strings for cross-cutting categorization." [S1](sources.md#s1)

> "`timestamp` — ISO 8601 datetime of last meaningful change." [S1](sources.md#s1)

Extensibility (load-bearing for carrying plan metadata like ID/status/fingerprint):

> "**Extensions:** Producers MAY include any additional keys. Consumers SHOULD
> preserve unknown keys when round-tripping and SHOULD NOT reject documents with
> unrecognized fields." [S1](sources.md#s1)

---

## Conformance test (SPEC §9) — the exact gate a checker must implement

A bundle is conformant with OKF v0.1 iff:

> "1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter
> block. / 2. Every frontmatter block contains a non-empty `type` field. / 3. Every
> reserved filename (`index.md`, `log.md`) follows the structure described in §6 and
> §7 respectively when present." [S1](sources.md#s1)

Everything else is soft guidance; consumers MUST NOT reject a bundle for missing
optional fields, unknown `type` values, unknown extra keys, broken links, or missing
`index.md` files [S1](sources.md#s1). **Net:** the only hard requirements are (a) frontmatter parses
and (b) non-empty `type` on every non-reserved doc — a very low bar to reach compliance.

---

## Model terms (for the secondary question on lossless carry)

- **Knowledge Bundle** = the unit of distribution (a directory tree). **Concept** =
  one markdown doc. **Concept ID** = file path minus `.md` (`tables/users.md` -> `tables/users`) [S1](sources.md#s1).
- Frontmatter is deliberately thin (`type` required; `title/description/resource/
  tags/timestamp` recommended) with an open extension mechanism — so plan-specific
  metadata (status, fingerprint, upstream dispositions, review passes) would ride as
  **producer-defined extension keys**, which §4.1 explicitly permits and asks
  consumers to preserve on round-trip [S1](sources.md#s1).

## Sources

See `sources.okf-spec-primary.json` (S1–S5) in the research dir.

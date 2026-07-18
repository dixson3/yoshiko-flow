# Triangulation: OKF compliance-delta for yf-plan / yf-research / yf-incubator

**Phase:** triangulate · **Method:** cross-cluster cross-reference (27 sources, 3
clusters) · **Retrieved:** 2026-07-17

This artifact cross-references the three clusters against the core research goal — the
**compliance delta** between what yf-plan / yf-research / yf-incubator emit and what OKF
v0.1 requires. Each delta is a two-sided fact: an OKF rule [S*/E*] paired with the
matching local-artifact behavior [L*]. Because a compliance delta is inherently two-sided,
"consensus" here is legitimately a spec-source + local-source pair (per the task's guidance),
often reinforced by a third ecosystem [E*] source.

## Credibility distribution

| Tier | Count | Sources |
|------|-------|---------|
| high_trust | 16 | S1–S5 (OKF spec/repo primary), L1–L8 (local direct reads), E1–E3 (GCP announcement + OKF README/SPEC) |
| verify | 11 | E4–E10 (verifiable third-party tooling artifacts), E11–E14 (secondary explainers + community amplification) |
| questionable | 0 | — |
| avoid | 0 | AI/SEO explainer sites (groundingpage.com, okfbundle.com, tinycommand.com, chatforest.com, specification.website) were pre-excluded from the source set at retrieval [ecosystem artifact] |

The generic `credibility_scorer.py batch` flattened all 27 to ~41/"questionable" because
its domain heuristic does not recognize github.com/pypi.org/raw.githubusercontent.com or the
local `skills/...` paths as authoritative. Categories were overridden on a principled primary-
source basis (recorded per source in `sources.json` `credibility.basis`): the OKF SPEC and
Google repo files are authoritative primary sources; the local skill specs, manager scripts,
and the real plan-028 folder are direct primary artifacts of the tools under study; third-party
packages are verifiable but hobby-scale.

---

## The conformance bar (frames every delta below)

**Finding 0 — OKF conformance is a deliberately low, two-clause bar.** `[confidence: high]`

OKF v0.1 requires only that (a) every non-reserved `.md` file has parseable YAML frontmatter
and (b) that frontmatter carries a non-empty `type`. Everything else is SHOULD-level.

> "1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
> / 2. Every frontmatter block contains a non-empty `type` field. / 3. Every reserved filename
> (`index.md`, `log.md`) follows the structure described in §6 and §7 respectively when
> present." [S1](sources.md#s1)

> "The spec only enforces one field to be explicitly provided — `type`, and that's exactly the
> trick: standardize only the smallest possible interoperability surface..." [E14](sources.md#e14)

> "There is no schema registry, no central authority, and no required tooling." [S1](sources.md#s1)[E3](sources.md#e3)

Independent agreement across three clusters (S1 spec, E14 community explainer, E3 repo README)
— **consensus** that the mandatory surface is exactly `frontmatter + type`. This is the single
most load-bearing fact for the delta: most gaps below are *mechanical* (add a YAML block / a
field) rather than *conceptual*, because OKF asks for so little.

**Caveat on spec stability** `[confidence: moderate]`: OKF is a **draft**, not a ratified
standard. > "This repository and its contents are not an official Google product." [okf-spec
artifact, quoting top-level README]; the SPEC self-identifies as "Version 0.1 — Draft" [S1](sources.md#s1).
Any conformance work targets a moving target.

---

## Per-rule compliance-delta findings

### Rule 1 — Required YAML frontmatter + non-empty `type` field

**(a) OKF requires** `[S1](sources.md#s1)`:
> "A **YAML frontmatter block**, delimited by `---` on its own line at the start of the file...
> `type` — A short string identifying the kind of concept... marked **REQUIRED**." [S1](sources.md#s1)
> "Every frontmatter block contains a non-empty `type` field." [S1](sources.md#s1)

Real conformant example carries it: > "---\ntype: Reference\nresource: ...\ntitle: Average
Pageviews\n..." [S3](sources.md#s3). Third-party validators converge on this as *the* enforceable check: >
"Reports errors when a bundle violates a mandatory OKF conformance requirement (e.g. a concept
document is missing its `type` field)." [E4](sources.md#e4); also [E5](sources.md#e5)[E7](sources.md#e7).

**(b) What each tool does:**
- **yf-plan** — NO frontmatter at all; metadata rides as bold `**Field:**` prose headers. >
  "Every file's first line is a Markdown `#` heading — NO YAML `---` frontmatter block anywhere.
  plan.md carries metadata as bold `**Field:**` header lines (ID, Author, Created, Status,
  Epic, Fingerprint...)" [L4](sources.md#l4). Confirmed against the real completed plan-028 folder [L4](sources.md#l4).
- **yf-research** — NO frontmatter; plain GFM with a `#`-heading `_index.md` template. >
  "HEADER_TEMPLATE = \"\"\"# Research Index: {topic}\"" [L7](sources.md#l7); > "Every markdown artifact this
  skill writes... is plain **GFM**" [L6](sources.md#l6).
- **yf-incubator** — HAS YAML frontmatter, but keyed `title/created/status/priority/last_reviewed`
  — **no `type` key**. > "the state file frontmatter shall carry `title`, `created`, [`status`,
  `priority`, `last_reviewed`]" [L8](sources.md#l8).

**(c) Gap nature:** **Mechanical for all three.** yf-plan/yf-research need a YAML block prepended
(the metadata they carry as prose/table could be lifted into keys); yf-incubator already emits
frontmatter and needs only one added `type` key. None faces a conceptual obstacle — OKF's
extension mechanism explicitly welcomes their existing metadata as extra keys (see Rule 7).

**(d) Confidence: high.** Two-sided consensus: spec [S1](sources.md#s1) + example [S3](sources.md#s3) + 3 validators
[E4](sources.md#e4)[E5](sources.md#e5)[E7](sources.md#e7) on the requirement; direct primary reads [L4](sources.md#l4)[L6](sources.md#l6)[L7](sources.md#l7)[L8](sources.md#l8) on the tool behavior.

---

### Rule 2 — `type` is an open vocabulary (no closed enumeration)

**(a) OKF requires** `[S1](sources.md#s1)`: no registered enum; consumers must tolerate unknowns. > "Type
values are **not** registered centrally. Producers SHOULD pick values that are descriptive...
consumers MUST tolerate unknown types gracefully." [S1](sources.md#s1). Example (non-normative) values: >
"`BigQuery Table`, `BigQuery Dataset`, `API Endpoint`, `Metric`, `Playbook`, `Reference`." [S1](sources.md#s1).

**(b) What each tool does:** none emits a `type`, so none conflicts with the vocabulary either.
The tools' natural `type` values (e.g. `Plan`, `Research Index`, `Incubator`) would be free-form
title-case strings, exactly the pattern the spec sanctions.

**(c) Gap nature:** **Mechanical / trivial** — the open vocabulary removes any obstacle; a
producer picks its own strings.

**(d) Confidence: high** (spec-only, but unambiguous [S1](sources.md#s1)). Corroborated by the Agent Skills
structural analog: > "the entire spec is two required YAML fields and a Markdown body" [E12](sources.md#e12) —
minimal-required-field designs of this shape are a known, workable pattern.

---

### Rule 3 — `okf_version` field (optional; bundle-root `index.md` only)

**(a) OKF requires** `[S1](sources.md#s1)`: optional, declared only in a bundle-root `index.md` frontmatter. >
"Bundles MAY declare the OKF version... by including `okf_version: \"0.1\"` in a bundle-root
`index.md` frontmatter block (the only place frontmatter is permitted in an `index.md`)." [S1](sources.md#s1).

**Absence finding (spec-side)** `[confidence: high]`: no shipped reference bundle actually
declares it. > "gh search code okf_version... => only match: 'okf/SPEC.md'... " [S5](sources.md#s5); the real
ga4 bundle-root `index.md` has **no frontmatter at all** [S4](sources.md#s4). §9 conformance does not list
`okf_version` — it is spec'd-but-unexercised.

**(b) What each tool does:** none emits `okf_version` [L4](sources.md#l4)[L6](sources.md#l6)([L8](sources.md#l8), per cross-tool table L-artifact).

**(c) Gap nature:** **Non-gap / optional.** Because OKF itself never requires or exercises it,
absence in the yf-* tools is not a conformance failure. If desired it is a one-line mechanical add.

**(d) Confidence: high.** Two independent absence findings on the spec side [S4](sources.md#s4)[S5](sources.md#s5) + direct
local reads on the tool side. This is a genuine "absence is a valid finding" on **both** sides.

---

### Rule 4 — Reserved filenames `index.md` and `log.md`

**(a) OKF requires** `[S1](sources.md#s1)`: `index.md` (directory listing, §6) and `log.md` (update history,
§7) are reserved at every level and MUST NOT be concept docs. > "The following filenames have
defined meaning at any level of the hierarchy and MUST NOT be used for concept documents:
`index.md`... `log.md`... All other `.md` files are concept documents." [S1](sources.md#s1). `index.md`
carries **no frontmatter** (except the bundle-root okf_version exception) and is a `#`-heading +
bulleted listing [S1](sources.md#s1)[S4](sources.md#s4). `log.md` is newest-first ISO-8601 date-grouped prose [S1](sources.md#s1).

**Absence finding (spec-side)** `[confidence: high]`: the reference repo contains **zero
`log.md` files** — defined but never demonstrated. > "Recursive tree filter for '*log.md' =>
(no results)." [S5](sources.md#s5).

**(b) What each tool does — reserved names DIVERGE:**
- **yf-plan** reserved index is `README.md` (with File map + Reading order sections), not
  `index.md`. > "REQ-PORT-001: Every plan folder... must contain `README.md` at the plan root
  with file-map and reading-order sections." [L1](sources.md#l1)[L4](sources.md#l4).
- **yf-research** reserved index is `_index.md` (underscore prefix), not `index.md`. > "REQ-DATA-005:
  `_index.md` is the artifact manifest, created/updated only via `index_manager.py`." [L5](sources.md#l5)[L7](sources.md#l7).
- **yf-incubator** reserved root is `README.md`, triage index is `Incubator/INDEX.md` [L8](sources.md#l8).
- **Log surface diverges from `log.md`** in all three: yf-plan uses an in-`plan.md`
  `**Phase log:**` section [L4](sources.md#l4); yf-research uses the `_index.md` manifest table [L5](sources.md#l5)[L7](sources.md#l7);
  yf-incubator uses a `## Decision log` body section [L8](sources.md#l8). **No tool emits a `log.md`.**

**(c) Gap nature:** **Mixed — partly conceptual.**
- `index.md`: **conceptual/naming** gap. yf-research's `_index.md` (underscore) and yf-plan's
  `README.md` are *reserved names that collide semantically but differ lexically* from OKF's
  `index.md`. OKF treats a non-`index.md` file as a **concept document** requiring `type`
  frontmatter — so `README.md`/`_index.md` would need either renaming to `index.md` (adopting
  OKF's frontmatter-free listing format) or acceptance as typed concept docs. This is a design
  decision, not a one-line edit.
- `log.md`: **mechanical/optional** gap. `log.md` is optional in OKF and unexercised even in the
  reference repo [S5](sources.md#s5), so the existing phase-log/decision-log surfaces need not become `log.md`
  to conform.

**(d) Confidence: high.** Spec reserved-name rule [S1](sources.md#s1) + real example [S4](sources.md#s4) + spec-side absence
[S5](sources.md#s5), paired with direct local reads of all three divergent index/log surfaces [L1](sources.md#l1)[L4](sources.md#l4)[L5](sources.md#l5)[L7](sources.md#l7)[L8](sources.md#l8).

**Interop note** `[confidence: moderate]`: a third-party linter *warns* (not errors) on a
missing `index.md` — > "warns on missing `index.md`" [E4](sources.md#e4) — consistent with §9 not requiring it.

---

### Rule 5 — Citation / heading conventions (`# Citations`, SHOULD-level)

**(a) OKF requires** `[S1](sources.md#s1)`: conventional (SHOULD, not MUST) headings; external sources under a
`# Citations` heading. > "those sources SHOULD be listed under a `# Citations` heading at the
bottom of the document, numbered: `[1] [BigQuery public dataset announcement](https://...)`" [S1](sources.md#s1).
**Practice varies from spec:** the real ga4 concept uses a plain bulleted list of bare URLs, not
numbered entries: > "# Citations\n- https://developers.google.com/analytics/bigquery/basic-queries"
[S3](sources.md#s3). Both are conformant because the heading is SHOULD-level.

**(b) What each tool does:**
- **yf-research** uses inline `[N]` markers resolving to `sources.json`, plus a `> "..." [N]`
  quote convention — **no `# Citations` heading**. > "every factual claim... carries an inline
  `[N]` that resolves to a `sources.json` entry." [L5](sources.md#l5); > "include a direct quote (`> \"...\"
  [N]`)" [L6](sources.md#l6).
- **yf-plan / yf-incubator** have no citation convention (n/a) [local-artifact cross-tool table].

**(c) Gap nature:** **Mechanical + low-stakes.** yf-research's citation model differs in *form*
(inline `[N]` → JSON vs. a bottom `# Citations` list) but the heading is only SHOULD-level, so
non-conformance here does not fail §9. Converting would mean emitting a `# Citations` section —
a formatting change, not a data-model change.

**(d) Confidence: high** on the two-sided fact (spec SHOULD [S1](sources.md#s1) + example variance [S3](sources.md#s3) + local
inline-`[N]` model [L5](sources.md#l5)[L6](sources.md#l6)). `[uncertain]` whether any consumer tooling actually parses citation
numbering — the spec's own example and its reference bundle disagree on numbering [S1](sources.md#s1)[S3](sources.md#s3).

---

### Rule 6 — Bundle-relative (absolute) link form (SHOULD)

**(a) OKF requires** `[S1](sources.md#s1)`: two link forms; `/`-prefixed bundle-root-absolute is **recommended**
(not required). > "### 5.1 Absolute (bundle-relative) links / Begin with `/`... This is the
**recommended** form..." [S1](sources.md#s1). Broken links are explicitly tolerated: > "Consumers MUST tolerate
broken links — a link whose target does not exist in the bundle is not malformed." [S1](sources.md#s1). Even the
reference bundle's own `index.md` uses **relative** links, not `/`-absolute: > "* [datasets](datasets/index.md)..."
[S4](sources.md#s4) — so "recommended" is demonstrably not "required."

**(b) What each tool does:** local artifacts do not record the tools emitting `/`-absolute
bundle-relative links; yf-plan's audit instead *forbids* dangling absolute paths and `../`
traversal. > "# 6. No dangling external refs across all plan files." [L2](sources.md#l2); the audit checks
"dangling absolute/`../` paths" [L3 / local-artifact §3]. The tools use plain relative markdown
links within a folder.

**(c) Gap nature:** **Mechanical / near-non-gap.** Since OKF only *recommends* the `/`-absolute
form and its own reference bundle uses relative links [S4](sources.md#s4), the tools' relative-link practice is
already OKF-conformant. No change is required for conformance; adopting `/`-absolute would be a
stylistic upgrade.

**(d) Confidence: high** on the spec side (SHOULD + counter-example [S1](sources.md#s1)[S4](sources.md#s4)). `[insufficient
evidence]` on the exact link-emission behavior of yf-plan/yf-research/yf-incubator: the local
cluster documents the *audit's* link constraint [L2](sources.md#l2)[L3](sources.md#l3) but does not directly quote emitted
link forms in a shipped bundle. Nature of gap: 1 local source on audit behavior, none directly
on emitted link syntax — do not over-claim tool link conformance.

---

### Rule 7 — resource / tags / timestamp + extension-key metadata model

**(a) OKF requires** `[S1](sources.md#s1)`: `title/description/resource/tags/timestamp` are all
optional/recommended, NOT required. Critically, **producers MAY add any extension keys** and
consumers must preserve them: > "**Extensions:** Producers MAY include any additional keys.
Consumers SHOULD preserve unknown keys when round-tripping and SHOULD NOT reject documents with
unrecognized fields." [S1](sources.md#s1).

**(b) What each tool does:** each carries rich metadata that maps cleanly onto extension keys —
yf-plan's `ID/Author/Created/Status/Epic/Fingerprint` bold fields [L4](sources.md#l4); yf-incubator's
`status/priority/last_reviewed` frontmatter keys [L8](sources.md#l8); yf-research's `sources.json` scores.
None currently expresses these as OKF frontmatter, but none conflicts with OKF's model.

**(c) Gap nature:** **Mechanical + favorable.** This is the load-bearing enabler: OKF's open
extension mechanism means plan-specific metadata (status, fingerprint, upstream dispositions,
review passes) can ride **losslessly** as producer-defined extension keys — the delta is purely
"lift existing prose/table metadata into YAML keys," with `type` the only newly-mandatory key.

**(d) Confidence: high.** Spec extension clause [S1](sources.md#s1) + direct evidence of the tools' existing
metadata payloads [L4](sources.md#l4)[L8](sources.md#l8). This answers the secondary "lossless carry" question affirmatively:
the extension mechanism is explicitly designed for exactly this [S1](sources.md#s1).

---

## Cross-cutting consensus & contradictions

### Consensus findings (3+ independent sources)

- **C1 — Mandatory OKF surface = frontmatter + non-empty `type`, nothing more.** `[high]`
  Agreed by S1 (spec §9), E14 (community explainer), E3 (repo README) — three clusters. [S1](sources.md#s1)[E3](sources.md#e3)[E14](sources.md#e14)
- **C2 — A real, nascent third-party tooling ecosystem exists, converging on the same checks.**
  `[high]` Multiple independent verify-tier artifacts (okf-lint, okft, okf-schema, okflint,
  okfcli, WitsCode, okf-cli) all enforce **required `type`**, **reserved `index.md`**, and
  link/timestamp hygiene. [E4](sources.md#e4)[E5](sources.md#e5)[E6](sources.md#e6)[E7](sources.md#e7)[E8](sources.md#e8)[E9](sources.md#e9)[E10](sources.md#e10). Consensus on the enforceable conformance
  surface across ≥3 independent tools.
- **C3 — None of the three yf-* tools emits an OKF `type` or `okf_version` field.** `[high]`
  Direct reads of all three [L4](sources.md#l4)[L6](sources.md#l6)[L7](sources.md#l7)[L8](sources.md#l8) + the local cross-tool table. Two-sided against S1.
- **C4 — OKF's minimalism mirrors Anthropic Agent Skills (folder + minimal-required-YAML + md
  body).** `[moderate]` [E11](sources.md#e11)[E12](sources.md#e12)[E14](sources.md#e14) — a structural analog, useful for interop framing but not
  a compliance fact.

### Absence findings (valid negatives)

- **A1 — No confirmed non-Google production adopter of OKF.** `[high]` Only named production
  consumer is Google's own Knowledge Catalog. > "We have also updated Google Cloud's Knowledge
  Catalog to be able to ingest Open Knowledge Format..." [E1](sources.md#e1). README producer/consumer lists are
  *intended targets*, not attestations [E2](sources.md#e2). Spec is ~5 weeks old at retrieval.
- **A2 — No shipped reference bundle declares `okf_version`; zero `log.md` files exist in the
  reference repo.** `[high]` [S4](sources.md#s4)[S5](sources.md#s5). Both features are spec'd-but-unexercised.
- **A3 — No yf-* tool currently emits YAML frontmatter except yf-incubator (and that lacks
  `type`).** `[high]` [L4](sources.md#l4)[L6](sources.md#l6)[L8](sources.md#l8).

### Contradictions

- **X1 — Spec vs. its own reference bundle on citation numbering.** SPEC §8 shows **numbered**
  `[1] [text](url)` citations [S1](sources.md#s1); the real ga4 concept uses an **unnumbered bare-URL bullet
  list** under the same `# Citations` heading [S3](sources.md#s3). Not a true conflict for conformance (heading
  is SHOULD-level), but a spec-vs-practice variance worth flagging. `[confidence: high this
  variance exists; its impact is low]`
- **X2 — Spec "recommended" `/`-absolute links vs. reference bundle's relative links.** §5.1 calls
  `/`-absolute the recommended form [S1](sources.md#s1); ga4's `index.md` uses relative `datasets/index.md` links
  [S4](sources.md#s4). Again a recommendation-vs-practice gap, not a hard contradiction.
- No contradictions found **between** the local-artifact cluster and the spec cluster on the core
  delta — the two sides are complementary facets, exactly as expected for a two-sided delta.

### Insufficient-evidence flags

- **IE1 — Exact link-emission syntax of yf-plan/yf-research/yf-incubator shipped bundles.**
  `[insufficient evidence]` The local cluster documents yf-plan's *audit* link constraint
  [L2](sources.md#l2)[L3](sources.md#l3) but does not directly quote emitted link forms; 1 source on audit behavior, 0 on
  emitted syntax. Do not claim tool link (non-)conformance beyond "uses relative links within a
  folder."
- **IE2 — Whether OKF v0.1 draft will remain stable / how consumers treat citation numbering.**
  `[insufficient evidence / uncertain]` Spec is an explicit draft ([S1](sources.md#s1), okf-spec artifact); no
  source attests future stability.

---

## Delta summary table (feeds synthesis)

| OKF rule | OKF requires [S/E] | yf-plan [L] | yf-research [L] | yf-incubator [L] | Gap nature | Confidence |
|----------|--------------------|-------------|-----------------|------------------|------------|------------|
| 1. frontmatter + `type` (MUST) | YAML block + non-empty `type` [S1](sources.md#s1)[S3](sources.md#s3) | none — `**Field:**` prose [L4](sources.md#l4) | none — plain GFM [L6](sources.md#l6)[L7](sources.md#l7) | frontmatter but no `type` [L8](sources.md#l8) | **Mechanical** (yf-incubator trivial) | high |
| 2. open `type` vocab | free-form title-case [S1](sources.md#s1) | n/a (no type) | n/a | n/a | Mechanical/trivial | high |
| 3. `okf_version` (optional) | bundle-root `index.md` only; unexercised [S1](sources.md#s1)[S4](sources.md#s4)[S5](sources.md#s5) | absent [L4](sources.md#l4) | absent [L6](sources.md#l6) | absent [L8](sources.md#l8) | Non-gap (optional) | high |
| 4. reserved `index.md`/`log.md` | `index.md` listing + optional `log.md` [S1](sources.md#s1)[S4](sources.md#s4)[S5](sources.md#s5) | `README.md`; phase-log in plan.md [L1](sources.md#l1)[L4](sources.md#l4) | `_index.md`; manifest table [L5](sources.md#l5)[L7](sources.md#l7) | `README.md`/`INDEX.md`; `## Decision log` [L8](sources.md#l8) | **Mixed — index.md conceptual, log.md optional** | high |
| 5. `# Citations` (SHOULD) | bottom `# Citations` heading [S1](sources.md#s1)[S3](sources.md#s3) | n/a | inline `[N]`→sources.json [L5](sources.md#l5)[L6](sources.md#l6) | n/a | Mechanical, low-stakes | high (X1 variance) |
| 6. `/`-absolute links (SHOULD) | recommended, not required [S1](sources.md#s1)[S4](sources.md#s4) | relative; audit forbids dangling abs [L2](sources.md#l2)[L3](sources.md#l3) | relative | relative | Near-non-gap | high spec / IE1 tool |
| 7. extension-key metadata | any extra keys, preserved [S1](sources.md#s1) | rich `**Field:**` metadata [L4](sources.md#l4) | sources.json scores | frontmatter keys [L8](sources.md#l8) | **Mechanical + favorable (lossless carry)** | high |

**Net compliance-delta:** the only *conceptual* gaps are (Rule 1) yf-plan/yf-research emit no
frontmatter at all, and (Rule 4) the reserved index filename diverges (`README.md`/`_index.md`
vs `index.md`). Everything else is mechanical or a non-gap. OKF's extension mechanism (Rule 7)
makes lossless metadata carry a non-issue. yf-incubator is closest to conformance (already emits
frontmatter; needs only a `type` key). yf-plan is furthest (prose `**Field:**` headers, no YAML).

## Sources

All source ids resolve to `sources.json` (E1–E14 ecosystem-interop, L1–L8 local-artifacts,
S1–S5 okf-spec-primary), each carrying a `credibility` object with numeric subscores, a
principled `category` (high_trust / verify), and a `basis` note.

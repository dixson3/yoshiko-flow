# Cluster: ecosystem-interop — OKF ecosystem & interoperability landscape

Method: exa web search. Retrieved 2026-07-17. OKF = Open Knowledge Format v0.1,
published by Google Cloud's Data Cloud team on 2026-06-12/13 in the
`GoogleCloudPlatform/knowledge-catalog` repo. Sources cited as `[En]` → see
`sources.ecosystem-interop.json`.

## Adopters (who besides Google uses OKF?)

**Absence finding.** No confirmed non-Google *production* adopter surfaced. The
only named production consumer is Google's own Knowledge Catalog:

> "We have also updated Google Cloud's Knowledge Catalog to be able to ingest Open
> Knowledge Format and serve it to our agents." [E1](sources.md#e1)

The OKF README lists *intended/possible* producers and consumers, but these are
integration targets the format is designed for — not attestations that those
vendors have adopted it:

> "Anyone can produce OKF — humans authoring by hand, agents built on any framework
> (Google ADK, LangChain, custom), export pipelines from existing catalogs
> (Dataplex, Unity Catalog, Collibra, ...), or scripts walking a database. Anyone
> can serve and consume OKF — a static file server, a knowledge-management UI
> (Obsidian, Notion, MkDocs), an LLM loading files into context, a search index, or
> a graph viewer..." [E2](sources.md#e2)

Queries run (no third-party adopter announcements found): "who uses Open Knowledge
Format OKF besides Google", "companies adopting Open Knowledge Format OKF bundles
2026", "GoogleCloudPlatform knowledge-catalog Open Knowledge Format adopters". The
spec is ~5 weeks old at retrieval, which plausibly explains the absence.

## Tooling (validators, converters, libraries)

Contrary to an "essentially no tooling" hypothesis, a **nascent but real
third-party tooling ecosystem** already exists — almost entirely
solo-developer/hobby-scale packages published within weeks of the launch. Note the
spec itself requires none:

> "There is no schema registry, no central authority, and no required tooling." [E3](sources.md#e3)

Third-party tools found:

- **okf-lint** (npm, Node ESM) — conformance linter; errors on missing `type`,
  warns on missing `index.md`. [E4](sources.md#e4)
- **okft** (PyPI, uploaded 2026-07-14) — validator + **MCP server** exposing a
  bundle to Claude/Gemini CLI/Cursor as navigation tools. [E5](sources.md#e5)
- **okf-schema** (PyPI v0.9.0) — CLI/library doing **JSONSchema** validation of
  frontmatter, dispatched per-`type` via bundle-local `_schema/` files. [E6](sources.md#e6)
- **okflint** (PyPI v0.3.0, MIT) — "the Ruff of documentation"; `validate` exit-0/1
  gate for pre-commit/CI. [E7](sources.md#e7)
- **okfcli/okf** (GitHub, Go, Apache-2.0, created 2026-06-18, ~3 stars) — single Go
  binary; explicitly the **vendor-neutral alternative** to Google's Python+Gemini+
  BigQuery reference impl. [E8](sources.md#e8)
- **WitsCode OKF Conformance Suite** — free open-source pass/fail conformance
  checker, runs locally, CI exit codes. [E9](sources.md#e9)
- **okf-cli** (PyPI v0.3.1) — markdown→OKF **converter** (generates frontmatter,
  type, timestamps, index files). [E10](sources.md#e10)
- Additional PyPI packages seen in search (recorded here, not individually
  sourced): `okf-toolkit`, `okfgen`, plus `Sudhakaran88/okf-conformance` on GitHub.

Observation on validators: multiple independent tools converge on the same
enforceable checks — **required `type` field**, **reserved `index.md`**, broken-link
/ orphan-concept / timestamp hygiene [E4](sources.md#e4)[E5](sources.md#e5)[E7](sources.md#e7) — which is the concrete conformance
surface relevant to this research's compliance-delta question.

Credibility caveat: several top search hits are AI/SEO-generated explainer sites
(groundingpage.com, okfbundle.com, tinycommand.com, chatforest.com,
specification.website). Treated as low-credibility and excluded from the source set;
the PyPI/GitHub packages above are verifiable artifacts (real upload dates, licenses,
dependencies) and are the substantive ecosystem evidence.

## Comparable formats (for interop comparison)

OKF sits in a crowded "make X agent-readable" landscape. Practitioners describe
these as **stackable, complementary layers**, not competitors:

> "Four protocols make APIs discoverable by AI agents: llms.txt (static
> description), OpenAPI (machine-readable spec), Agent Skills (structured
> capability), and MCP servers (runtime tools). Each serves a different layer." [E11](sources.md#e11)

Closest structural analog is **Anthropic's Agent Skills** (SKILL.md) — same
"folder convention + minimal-required-YAML + markdown body" design philosophy as OKF:

> "The entire spec is two required YAML fields and a Markdown body. No JSON-RPC, no
> auth handshake, no server process... A folder convention (SKILL.md + files)." [E12](sources.md#e12)

This directly parallels OKF's single-required-field minimalism:

> "The spec only enforces one field to be explicitly provided — `type`... standardize
> only the smallest possible interoperability surface." [E14](sources.md#e14)

Other comparables in the discoverability stack: **llms.txt** (curated URL index),
**JSON-LD / schema.org** (structured metadata for citation lift), **MCP** (runtime
tools + `.well-known/mcp.json` cards), **AGENTS.md/CLAUDE.md** (coding-agent skill
files) [E13](sources.md#e13). Distinguishing axis: OKF standardizes **on-disk knowledge content**
(markdown+frontmatter bundles); MCP/Agent Skills standardize **runtime capability/
tool access**; llms.txt/JSON-LD standardize **web discoverability**. OKF is the
"data-as-code / metadata" layer, closest in spirit to Obsidian vaults and the
AGENTS.md family — which the GCP blog explicitly names as the pattern OKF formalizes.

## GCP announcements / blog posts

- **Primary announcement** [E1](sources.md#e1) — Google Cloud Blog, "Introducing the Open Knowledge
  Format", Sam McVeety & Amir Hormati (Data Cloud), 2026-06-12/13. Frames OKF as
  formalizing the "LLM-wiki pattern" (credits Karpathy's LLM Wiki gist) and
  explicitly names the AGENTS.md/CLAUDE.md + `index.md`/`log.md` convention family as
  the bespoke patterns OKF unifies:

  > "Similar knowledge-as-Wiki pattern keeps reappearing under different names:
  > Obsidian vaults wired to coding agents, the AGENTS.md / CLAUDE.md family of
  > convention files, repos full of index.md and log.md artifacts that agents consult
  > before doing real work, and 'metadata as code' repositories inside data teams." [E1](sources.md#e1)

- **Official README** [E2](sources.md#e2) and **SPEC.md** [E3](sources.md#e3) in `GoogleCloudPlatform/knowledge-
  catalog`. Ships a reference producer agent (Python + Gemini + BigQuery), a
  visualizer, and three sample bundles (ga4, stackoverflow, crypto_bitcoin).
- Community amplification: Medium (Google Cloud Community) explainer [E14](sources.md#e14).

## What compliance with OKF unlocks

The README's "Why OKF?" section is the authoritative statement of the payoff. Key
verbatim benefits [E2](sources.md#e2):

- **Native ingestion / agent serving** — the only concrete, named unlock: a
  conformant bundle can be ingested by Google Cloud Knowledge Catalog and served to
  its agents [E1](sources.md#e1). Third-party MCP servers (okft `serve`) similarly expose any
  conformant bundle to Claude/Gemini/Cursor [E5](sources.md#e5).
- **Version-control-native curation:**
  > "Version-controllable out of the box. Bundles live in git. Pull requests,
  > line-by-line diffs, blame, and review workflows just work — knowledge curation
  > becomes a normal software-engineering activity." [E2](sources.md#e2)
- **Portability / no lock-in:**
  > "Portable and lock-in free. A bundle is a directory. Ship it as a tarball, host
  > it in any repo, mount it from any filesystem... No proprietary API stands between
  > you and your metadata." [E2](sources.md#e2)
- **Tooling compatibility (discoverability):**
  > "Composes with existing tooling. Many knowledge tools — Notion, Obsidian, MkDocs,
  > Hugo, Jekyll — already speak markdown plus YAML frontmatter, so bundles can be
  > browsed, edited, or rendered without custom UI." [E2](sources.md#e2)
- **Progressive disclosure via reserved `index.md`:**
  > "Progressive disclosure built in. Auto-generated index.md files let an agent or
  > human navigate the hierarchy one level at a time instead of loading the entire
  > bundle into context." [E2](sources.md#e2)
- **Graph traversal via markdown links** (concepts link to each other, richer than
  tree hierarchy) [E2](sources.md#e2); CI-gated rot prevention via linters [E5](sources.md#e5)[E7](sources.md#e7).

**Net for this research:** the tangible unlock of conformance is (a) native
ingestion into Google Knowledge Catalog and MCP-server exposure to major agents, and
(b) the ability to run the emerging validator/converter toolchain (okflint, okf-lint,
okft, okf-schema, WitsCode suite) as CI gates. Both are young; adoption breadth is
the main absence.

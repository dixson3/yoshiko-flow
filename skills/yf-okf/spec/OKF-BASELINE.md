# OKF-BASELINE — upstream Open Knowledge Format v0.1

> **Status: Draft (plan-029, Epic 1, Issue 1.2).** Human-readable reference for the **upstream**
> Open Knowledge Format that `yf-okf` is compatible *with*. Pinned to `okf_version: 0.1`. This doc
> records **verbatim what OKF says** — it introduces no yoshiko-flow opinion (that is
> `OKF-YF-EXTENSIONS.md`). It is one of the two authored specs kept **in agreement** with the
> machine-readable ruleset baked into `okf.py` by a `yf-drift-check` edge (SPEC REQ-OKF-FAM-002);
> the engine does **not** parse this file at runtime.

## 0. Provenance and draft status

Every "OKF says X" claim here is distilled from research project
`docs/research/001-okf-compliance-delta/` and cites its source ids (`docs/research/001-okf-compliance-delta/sources.md`).
The primary source is the OKF v0.1 SPEC in `GoogleCloudPlatform/knowledge-catalog`
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)), corroborated by the README
([S2](../../../docs/research/001-okf-compliance-delta/sources.md#s2)), the `ga4` reference bundle
([S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3),
[S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)), and repo-wide absence findings
([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)).

**Be honest about maturity.** OKF is a self-identified **"Version 0.1 — Draft"** with **"no schema
registry, no central authority, and no required tooling"**
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)). The only named production
consumer is Google's own Knowledge Catalog; the README's producer/consumer lists (ADK, LangChain,
Obsidian, Notion, MkDocs, Collibra) are **intended targets, not attestations** of adoption
([E1](../../../docs/research/001-okf-compliance-delta/sources.md#e1),
[E2](../../../docs/research/001-okf-compliance-delta/sources.md#e2)). No non-Google production
adopter is confirmed. This draft status is exactly why the yf layer isolates upstream drift to this
file (plan-029 R3): when OKF ratifies or bumps its version, only `OKF-BASELINE.md` and the baked-in
ruleset re-sync — the yf extension layer and the artifacts do not move.

RFC-2119 force below is OKF's own (MUST / SHOULD / MAY), reported as the spec states it, not
promoted or demoted by yf.

## 1. What OKF is

> "The format is intentionally minimal: a directory of markdown files with YAML frontmatter. There
> is no schema registry, no central authority, and no required tooling. If you can `cat` a file, you
> can read OKF; if you can `git clone` a repo, you can ship it."
> — SPEC.md ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1))

An OKF **bundle** is a directory tree of markdown files. Two filenames are reserved with defined
meaning **at any level** of the hierarchy; every other `.md` file is a **concept document**.

## 2. The conformance surface (§9) — the only MUSTs

OKF's mandatory conformance bar is deliberately tiny. SPEC §9 states it as three items
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)):

> "1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block. / 2.
> Every frontmatter block contains a non-empty `type` field. / 3. Every reserved filename
> (`index.md`, `log.md`) follows the structure described in §6 and §7 respectively when present."

| # | Rule | Force | Notes |
|:--|:--|:-:|:--|
| B1 | Every **non-reserved** `.md` carries a **parseable YAML frontmatter block** delimited by `---` | MUST | The two reserved files (`index.md`, `log.md`) are exempt |
| B2 | Every such frontmatter block carries a **non-empty `type`** field | MUST | The single newly-mandatory field; the only enforced key |
| B3 | Each present reserved file (`index.md` / `log.md`) follows its §6 / §7 structure | MUST (when present) | Structure only; the files themselves are not required to exist |

Third-party validators converge on B1/B2 as *the* enforceable check — okf-lint "reports errors when
a bundle violates a mandatory OKF conformance requirement (e.g. a concept document is missing its
`type` field)" ([E4](../../../docs/research/001-okf-compliance-delta/sources.md#e4), corroborated by
[E5](../../../docs/research/001-okf-compliance-delta/sources.md#e5),
[E7](../../../docs/research/001-okf-compliance-delta/sources.md#e7),
[E14](../../../docs/research/001-okf-compliance-delta/sources.md#e14)). Everything in §3–§6 below is
SHOULD-level or optional.

## 3. Reserved file: `index.md` (§6, directory listing)

`index.md` is reserved at **any** level as the directory listing — OKF's progressive-disclosure
surface. A non-`index.md` file is treated as a concept document requiring `type` frontmatter, so the
listing filename is load-bearing
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)).

> "The following filenames have defined meaning at any level of the hierarchy and MUST NOT be used
> for concept documents: `index.md` — Directory listing. See §6. `log.md` — Update history. See §7.
> ... All other `.md` files are concept documents."
> — SPEC.md §3.1 ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1))

What OKF says `index.md` holds — from the real `ga4/index.md`
([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)):

> "# Subdirectories\n\n* [datasets](datasets/index.md) - A sample of obfuscated Google Analytics
> BigQuery event export data ... * [references](references/index.md) - This directory contains
> specifications for data joins ... * [tables](tables/index.md) - Contains Google Analytics event
> export data ..."

Observed properties of a real bundle-root `index.md`
([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)):

| Property | What the reference bundle shows |
|:--|:--|
| Frontmatter | **None** — the listing carries no YAML block (it is a reserved file, exempt from B1/B2) |
| Structure | A `#` heading plus a bullet list of `[child](child/index.md) - description` entries (progressive disclosure: each entry links to a deeper `index.md` + a one-line description) |
| Links | **Relative** (`datasets/index.md`), not `/`-absolute — even though SPEC recommends absolute (§4 below) |
| `okf_version` | Absent from `ga4/index.md`; the bundle-root `index.md` is the **only** place SPEC even mentions it (§5) |

## 4. Reserved file: `log.md` (§7, update history)

`log.md` is reserved at any level as the **update history** / change log
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)). OKF spec's §7 defines it as
the change-log convention, but it is **optional** and **unexercised**: a recursive tree scan of the
reference repo finds **zero** `log.md` files anywhere
([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)).

> "Recursive tree filter for '*log.md' => (no results)."
> — absence finding ([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5))

OKF reserves the name and the meaning (update history) but does not mandate its presence, does not
demonstrate a format in any bundle, and does not pin an entry ordering. The **specific rendering**
(newest-first, ISO-8601 date headings) is a yoshiko-flow decision — see `OKF-YF-EXTENSIONS.md` §
"log.md format". OKF is **silent** on entry format and ordering (see § 7, Ambiguities).

## 5. YAML frontmatter and the `type` vocabulary (§4)

Every concept document carries a YAML frontmatter block whose one required key is `type`
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)):

> "`type` — A short string identifying the kind of concept. Consumers use this for routing,
> filtering, and presentation." — marked **REQUIRED**.
> — SPEC.md ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1))

**`type` is an open vocabulary**: free-form, title-case, **no enum, no schema registry**. A producer
picks strings like `Reference`, `Plan`, `Incubator` at will
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1),
[E14](../../../docs/research/001-okf-compliance-delta/sources.md#e14)). A real conformant concept doc
([S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3)):

> "---\ntype: Reference\nresource:
> https://developers.google.com/analytics/bigquery/basic-queries\ntitle: Average
> Pageviews\ndescription: The average number of pageviews per user.\ntags:\n- metric\ntimestamp:
> '2026-05-28T22:51:43+00:00'\n---"

| Frontmatter key | Force | Notes |
|:--|:-:|:--|
| `type` | **MUST** (non-empty) | The only enforced key; open, free-form, title-case vocabulary |
| `resource` | SHOULD / optional | A source URL for the concept |
| `title` | SHOULD / optional | Human-readable title |
| `description` | SHOULD / optional | One-line summary |
| `tags` | SHOULD / optional | Free-form list |
| `timestamp` | SHOULD / optional | ISO-8601 datetime |
| any producer key | MAY | Extension mechanism, §6 below |

## 6. Extension mechanism (§4.1) — producer keys, SHOULD-level preservation

OKF welcomes arbitrary producer keys and **recommends** (SHOULD, not MUST) that consumers preserve
them:

> "**Extensions:** Producers MAY include any additional keys. Consumers SHOULD preserve unknown keys
> when round-tripping and SHOULD NOT reject documents with unrecognized fields."
> — SPEC.md §4.1 ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1))

This is the hook the yf layer builds on: yf-specific keys (id, author, created, status, epic,
fingerprint, `okf_spec`) ride as producer extension keys alongside the one mandatory `type`
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1),
[L4](../../../docs/research/001-okf-compliance-delta/sources.md#l4),
[L8](../../../docs/research/001-okf-compliance-delta/sources.md#l8)). **Caveat carried from research
001:** `SHOULD` preservation is a recommendation a consumer may decline; no producer→consumer→producer
round-trip of yf keys through any OKF tool is demonstrated in the record, so lossless end-to-end
carry is unverified `[insufficient evidence]`. Carry is *permitted*; carry is not *guaranteed*.

## 7. Other v0.1 recommendations research 001 records (SHOULD / optional)

| Rule | OKF force | Status in the reference bundles | yf treatment |
|:--|:-:|:--|:--|
| `okf_version` key on the **bundle-root `index.md`** (§5) | optional | Spec'd but **unexercised** — the only match repo-wide is the SPEC prose itself ([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)) | yf MAY carry it on a bundle-root `index.md`, pinned `0.1` (see YF-EXTENSIONS) |
| `# Citations` bottom heading (§8) | **SHOULD** | The `ga4` concept ends in a `# Citations` bare-URL list ([S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3)) | **NON-GOAL** — see below |
| `/`-absolute cross-links (§4) | **SHOULD** | Unexercised — the reference `index.md` uses **relative** links ([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)) | yf keeps bundle-relative GFM links; not adopted |
| Progressive-disclosure `index.md` at **each** directory level (§6) | structural | The `ga4` bundle nests `index.md` per level ([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)) | Adopted as the reserved-`index.md` model (YF-EXTENSIONS adds a per-skill rendering adapter) |

**`# Citations` is an explicit NON-GOAL for plan-029** (SPEC §1 out-of-scope; plan Non-goals). OKF's
`# Citations` heading is SHOULD-level. Research `sources.md` already uses GFM citation links, and
normalizing to OKF's numbered/bare-URL `# Citations` form is **not** a conformance requirement and
is out of scope — `yf-okf` neither emits nor enforces it. (SPEC vs. its own reference bundle even
diverge on citation *numbering* — the SPEC shows numbered `[1] [text](url)`; the `ga4` concept uses
an unnumbered bare-URL list — signaling Google does not exercise the recommendation uniformly,
[S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1),
[S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3).)

## 7a. Where OKF v0.1 is ambiguous or silent

These are points the **yf extension layer had to decide** because OKF does not mandate them — flagged
so `OKF-YF-EXTENSIONS.md` (and downstream Issues 1.3/1.4) own the decision explicitly rather than
implying OKF requires it:

- **`log.md` entry format and ordering** — OKF reserves the name and the "update history" meaning but
  demonstrates no format and pins no ordering (zero `log.md` exist,
  [S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)). yf chose newest-first
  ISO-8601 date headings.
- **`index.md` rendering beyond "a listing"** — OKF shows one shape (`# heading` + `[child](child/index.md) - desc`
  bullets, [S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)) but does not fix the
  heading text, the entry template, or whether entries are files vs. subdirs. yf adopts the listing
  model and supplies per-skill rendering adapters.
- **Frontmatter *placement*** — OKF requires a parseable block but is silent on where in the file it
  sits relative to headings. yf pins it **above the first `## `** for fingerprint safety
  (YF-EXTENSIONS).
- **Single-file bundles** — OKF describes a *directory* of files; it is silent on a lone `.md` with no
  owning directory. yf defines a single-file-bundle exemption.
- **Non-`.md` files** — OKF's conformance surface addresses only `.md`; it does not say non-`.md`
  files (`plan.yaml`, `sources.json`) must be typed. yf makes the exclusion explicit.
- **`okf_spec` / per-type schemas** — OKF has no schema registry
  ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)); any per-type grouping is a
  producer-owned convention. yf names its members via an `okf_spec:` key.

Each is a yf decision, not an OKF mandate. The distinction matters for drift: only genuine OKF MUSTs
(§2, B1–B3) move if upstream OKF changes; the silences above are owned by the yf layer.

## 8. References

- `docs/research/001-okf-compliance-delta/Summary.md` and `sources.md` (S1–S5, E1–E14, L1–L8) — the
  distilled OKF v0.1 facts this doc pins.
- `docs/research/001-okf-compliance-delta/sources.okf-spec-primary.json` (primary OKF spec citations).
- `skills/yf-okf/SPEC.md` — REQ-OKF-001..003 (bundle model), REQ-OKF-FAM-002 (this doc is authored
  spec kept in agreement with the baked-in ruleset).
- `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` — the yoshiko-flow layer that decides the silences above.

# OKF-BASELINE — upstream Open Knowledge Format v0.2

> **Status: reconciled to OKF v0.2 (plan-046, Epic 2).** Human-readable reference for the
> **upstream** Open Knowledge Format that `yf-okf` is compatible *with*. Pinned to
> `okf_version: 0.2` (SPEC `REQ-OKF-FAM-005`). This doc records **verbatim what OKF says** — it
> introduces no yoshiko-flow opinion (that is `OKF-YF-EXTENSIONS.md`). It is one of the two
> authored specs kept **in agreement** with the machine-readable ruleset baked into `okf.py` by a
> `yf-drift-check` edge (SPEC REQ-OKF-FAM-002); the engine does **not** parse this file at runtime.
>
> **Every `(§N)` below is a v0.2 section number.** v0.2 renumbered seven sections and §13 does not
> flag the renumbering, so a surviving v0.1 pointer is indistinguishable from a correct v0.2 one by
> inspection. The authoritative mapping is [§8](#8-the-v01v02-section-map) — check citations against
> that table, never by grep.

## 0. Provenance and draft status

**Primary source (v0.2).** Every "OKF says X" claim about v0.2 is quoted from the verbatim upstream
copy vendored at [`okf-spec-v0.2.md`](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md) — `GoogleCloudPlatform/knowledge-catalog` `okf/SPEC.md`
@ `main`, retrieved 2026-08-18. The superseded v0.1 is vendored beside it at
[`okf-spec-v0.1.md`](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.1.md) (@ `ee67a5ca`, 2026-06-12), so every v0.1→v0.2 claim in this document is
diffable offline.

> **Research 001 is superseded as a source of *upstream* fact.** `docs/research/001-okf-compliance-delta/`
> distilled OKF **v0.1** and is marked `superseded_by` this reconciliation (plan-046 Issue 2.9). Its
> `S*`/`E*`/`L*` citations are retained below **only** where the claim they support is unchanged in
> v0.2, and are the reason those claims were believed in the first place — not evidence about v0.2.
> Where v0.2 changed a fact, the v0.2 spec is cited directly and the research finding is marked
> wrong-after.

The v0.1-era distillation cited its source ids (`docs/research/001-okf-compliance-delta/sources.md`).
The primary v0.1 source was the OKF v0.1 SPEC in `GoogleCloudPlatform/knowledge-catalog`
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)), corroborated by the README
([S2](../../../docs/research/001-okf-compliance-delta/sources.md#s2)), the `ga4` reference bundle
([S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3),
[S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)), and repo-wide absence findings
([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)).

**Be honest about maturity.** OKF v0.2 drops the *"— Draft"* suffix from its version line
(v0.1 read `**Version 0.1 — Draft**`; v0.2 reads `**Version 0.2**`) but is still a `0.x` format with
**"no schema registry, no central authority, and no required tooling"**
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)). The only named production
consumer is Google's own Knowledge Catalog; the README's producer/consumer lists (ADK, LangChain,
Obsidian, Notion, MkDocs, Collibra) are **intended targets, not attestations** of adoption
([E1](../../../docs/research/001-okf-compliance-delta/sources.md#e1),
[E2](../../../docs/research/001-okf-compliance-delta/sources.md#e2)). No non-Google production
adopter is confirmed **in the research-001 record**. *(Wrong-after: plan-046 exp-004 verified
**four** non-Google repositories carrying literal OKF bundles, two of them at v0.2. The "no
confirmed non-Google adopter" claim is measurably false as of 2026-08-18. It is corrected here and
in the #92 close comment.)*

This `0.x` status is exactly why the yf layer isolates upstream drift to this file (plan-029 R3):
when OKF bumps its version, only `OKF-BASELINE.md` and the baked-in ruleset re-sync — the yf
extension layer and the artifacts do not move. **plan-046 is the first exercise of that design, and
it held**: reconciling v0.1→v0.2 required no corpus migration whatsoever (D-2).

RFC-2119 force below is OKF's own (MUST / SHOULD / MAY), reported as the spec states it, not
promoted or demoted by yf.

## 1. What OKF is

> "The format is intentionally minimal: a directory of markdown files with YAML frontmatter. There
> is no schema registry, no central authority, and no required tooling. If you can `cat` a file, you
> can read OKF; if you can `git clone` a repo, you can ship it."
> — SPEC.md ([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1))

An OKF **bundle** is a directory tree of markdown files. Two filenames are reserved with defined
meaning **at any level** of the hierarchy; every other `.md` file is a **concept document**.

## 2. The conformance surface (§11) — the only MUSTs

OKF's mandatory conformance bar is deliberately tiny. SPEC §11 states it as three items
([v0.2 §11](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md)):

> "A bundle is **conformant** with OKF v0.2 if:
> 1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block. / 2.
> Every frontmatter block contains a non-empty `type` field. / 3. Every reserved filename
> (`index.md`, `log.md`) follows the structure in §8 and §9 respectively when present."

> **The single most important NON-change in v0.2.** These three MUSTs are **byte-identical** to
> v0.1 §9's, apart from the `§6`/`§7` → `§8`/`§9` cross-references that the renumbering forced. The
> permissive "consumers MUST NOT reject a bundle because of" list (missing optional fields, unknown
> `type` values, unknown keys, broken cross-links, missing `index.md`) is byte-identical too.
> **B1/B2/B3 below survive unchanged** — which is why reconciling to v0.2 is a documentation edit
> and not a migration.
>
> v0.2 §11 does **add** a paragraph absent from v0.1, carrying two MUSTs *conditioned on the new
> families being present*: consumers "MUST treat a bare `verified` mapping as a one-element list
> (§5.2)" and "MUST NOT reject a concept for missing any optional family (§5.3)". **Neither binds
> yf**, which emits none of the trust/lifecycle/provenance/computation families. Recorded rather
> than folded in, per this document's rule of reporting force as the spec states it.

| # | Rule | Force | Notes |
|:--|:--|:-:|:--|
| B1 | Every **non-reserved** `.md` carries a **parseable YAML frontmatter block** delimited by `---` | MUST | The two reserved files (`index.md`, `log.md`) are exempt |
| B2 | Every such frontmatter block carries a **non-empty `type`** field | MUST | The single newly-mandatory field; the only enforced key |
| B3 | Each present reserved file (`index.md` / `log.md`) follows its §8 / §9 structure | MUST (when present) | Structure only; the files themselves are not required to exist |

Third-party validators converge on B1/B2 as *the* enforceable check — okf-lint "reports errors when
a bundle violates a mandatory OKF conformance requirement (e.g. a concept document is missing its
`type` field)" ([E4](../../../docs/research/001-okf-compliance-delta/sources.md#e4), corroborated by
[E5](../../../docs/research/001-okf-compliance-delta/sources.md#e5),
[E7](../../../docs/research/001-okf-compliance-delta/sources.md#e7),
[E14](../../../docs/research/001-okf-compliance-delta/sources.md#e14)). Everything in §3–§6 below is
SHOULD-level or optional.

## 3. Reserved file: `index.md` (§8, directory listing)

`index.md` is reserved at **any** level as the directory listing — OKF's progressive-disclosure
surface. A non-`index.md` file is treated as a concept document requiring `type` frontmatter, so the
listing filename is load-bearing
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)).

> "The following filenames have defined meaning at any level of the hierarchy and MUST NOT be used
> for concept documents: `index.md` — Directory listing. See §8. `log.md` — Update history. See §9.
> ... All other `.md` files are concept documents."
> — SPEC.md §3.1 ([v0.2 §3](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md))

What OKF says `index.md` holds — from the real `ga4/index.md`
([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)):

> "# Subdirectories\n\n* [datasets](datasets/index.md) - A sample of obfuscated Google Analytics
> BigQuery event export data ... * [references](references/index.md) - This directory contains
> specifications for data joins ... * [tables](tables/index.md) - Contains Google Analytics event
> export data ..."

Observed properties of a real bundle-root `index.md`
([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)):

| Property | What the reference bundle shows | v0.2 status |
|:--|:--|:--|
| Frontmatter | **None** — the listing carries no YAML block (it is a reserved file, exempt from B1/B2) | **Now normative.** §8: *"Index files contain no frontmatter, with one exception: a bundle-root `index.md` MAY carry an `okf_version` key (§12)."* |
| Structure | A `#` heading plus a bullet list of `[child](child/index.md) - description` entries | Unchanged in shape; §8 now shows the body as *"one or more sections, each grouping concepts under a heading"* |
| Links | **Relative** (`datasets/index.md`), not `/`-absolute — even though SPEC recommends absolute (§6 below) | Unchanged recommendation |
| `okf_version` | Absent from `ga4/index.md`; the bundle-root `index.md` is the **only** place SPEC mentions it (**§12**) | See the correction note below |

**v0.2 §8 is materially more specific than v0.1 §6, and two of its additions are load-bearing for
`yf-okf`:**

- **Automatic generation is explicitly sanctioned.** §8: *"Producers MAY generate `index.md`
  automatically; consumers MAY synthesize one on the fly when none is present."* This is upstream
  cover for the `reindex` verb (SPEC `REQ-OKF-011`) — generation is not a yf extension.
- **The subdirectory example changed target.** v0.1 §6 showed `* [datasets](datasets/index.md)`; v0.2
  §8 shows `* [Subdirectory](subdir/) - short description of the subdirectory` — the **bare
  directory**, not a nested `index.md`. Recorded because it bears directly on the ghost-directory
  link class: an entry pointing at `<dir>/index.md` presumes a nested index that v0.2's own example
  does not use.
- **Descriptions have a stated source.** §8: *"Entries SHOULD include the description from the linked
  concept's frontmatter."* This is the upstream basis for plan-046 D-9 — nested indexes are worth
  generating once producers stamp `description:`, and are deferred until then. **Re-measured
  2026-08-28 (plan-056 Issue 0.8): `description` is present on 165 of 983 nested files.** The
  plan-046-era figure of "0 of 423" is stale on BOTH terms — the corpus has more than doubled and
  the numerator is no longer zero — so the deferral now rests on partial coverage concentrated in
  the twelve newest bundles, not on absence.

> **Correction — a citation that was wrong against v0.1 too.** This table and §7 below cited `(§5)`
> for the `okf_version` key. Measured: v0.1 mentions `okf_version` exactly once, at `okf/SPEC.md:393`,
> inside **§11 Versioning** — not §5 (which was *Cross-linking*). So `(§5)` was never right; it is
> **not** a renumbering casualty. The v0.2-correct target is **§12 Versioning**, reached by fixing an
> error rather than by applying the section map. Flagged explicitly because mapping `§5 → §6` here
> would have produced a confidently wrong citation in a fixed-authority document.

## 4. Reserved file: `log.md` (§9, update history)

`log.md` is reserved at any level as the **update history** / change log. It remains **optional**
(*"A `log.md` file MAY appear at any level"*) and was **unexercised** in the v0.1 reference corpus: a
recursive tree scan found **zero** `log.md` files anywhere
([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)).

> "Recursive tree filter for '*log.md' => (no results)."
> — v0.1-era absence finding ([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5))

**v0.2 §9 SPECIFIES the format that v0.1 §7 left open — and yf guessed right.**

> "The format is a flat list of date-grouped entries, newest first: … Date headings MUST use ISO
> 8601 `YYYY-MM-DD` form. Log entries are prose; the leading bold word (`**Update**`,
> `**Creation**`, `**Deprecation**`) is a convention, not a requirement."
> — SPEC.md §9 ([v0.2 §9](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md))

This is the **largest status change** in the v0.1→v0.2 reconciliation, and it moves a rule across the
baseline/extensions boundary:

| | v0.1 | v0.2 |
| :-- | :-- | :-- |
| Ordering | silent | **newest-first**, stated |
| Date headings | silent | **ISO-8601 `YYYY-MM-DD`, MUST** |
| Entry prose / bold lead-in | silent | a stated **convention, not a requirement** |
| Status of yf's rule | a yoshiko-flow **extension decision** | **baseline conformance** |

`yf-okf` already emits newest-first ISO-8601 date headings, so **no artifact changes**. What changes
is *why* the rule holds: it is no longer a yf decision recorded in `OKF-YF-EXTENSIONS.md`, it is an
upstream MUST recorded here. Every claim that "OKF is silent on log ordering" is now false — the
three sites are corrected by plan-046 Issues 2.3 (this section and §7a below) and 2.7
(`OKF-YF-EXTENSIONS.md:84`).

*(Note the direction of travel: the reserved-file **presence** is still not mandated, so B3's
"when present" qualifier is unaffected. v0.2 constrains the *shape* of a `log.md` that exists, not
whether one must.)*

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

**Wrong-after (v0.2 breaking change B-1).** The `timestamp` key in the quote above is **retired**.
It remains a true quote of a real v0.1 artifact, but it is **no longer an exemplar of a conformant
v0.2 concept**. §13.1: *"`timestamp` is superseded by `generated.at`. A concept's last content
change is now recorded as `generated: { by, at }` (§5.2). Consumers MAY fall back to a legacy
`timestamp` when `generated` is absent."*

| Frontmatter key | Force | Notes |
|:--|:-:|:--|
| `type` | **MUST** (non-empty) | The only enforced key; open, free-form, title-case vocabulary |
| `resource` | SHOULD / optional | A source URL for the concept |
| `title` | SHOULD / optional | Human-readable title |
| `description` | SHOULD / optional | One-line summary |
| `tags` | SHOULD / optional | Free-form list |
| ~~`timestamp`~~ | **RETIRED in v0.2** | Superseded by `generated.at` (§5.2). Consumers MAY still read it as a v0.1 fallback |
| `generated` | optional (v0.2, §5.2) | `{ by, at }`; `by` is REQUIRED within `generated` and uses the §7 actor convention |
| `sources` | optional (v0.2, §5.1) | Provenance list; `resource` REQUIRED per entry. Carries the credibility **signals** `author` / `usage_count` / `last_modified` |
| `verified` | optional (v0.2, §5.2) | Attestation list; a bare mapping MUST be read as a one-element list |
| `status`, `stale_after` | optional (v0.2, §5.4) | Lifecycle family |
| any producer key | MAY | Extension mechanism, §6 below |

**yoshiko-flow's exposure to B-1 is exactly ZERO.** The corpus emits `timestamp` **0** times — yf
uses `created` + a content `fingerprint` where v0.1 offered `timestamp`, a choice made long before
v0.2 retired it. No migration is required or performed (plan-046 D-2).

> **`sources` credibility is a DIVERGENCE, not a gap.** v0.2 §5.1 is explicit that OKF *"does not
> store a credibility score: a score is subjective, unportable across consumers, and goes stale.
> Credibility is inferred from the signals … not stored."* `yf-research` **does** store a score.
> That divergence, its evidence, and the decision not to reconcile it are recorded in
> `OKF-YF-EXTENSIONS.md` (plan-046 Issue 2.6) — this baseline records only what OKF says.

## 6. Extension mechanism (§4.1) — producer keys; preservation SHOULD, rejection MUST NOT

OKF welcomes arbitrary producer keys. **v0.2 hardens half of this clause** — preservation is still a
recommendation, but *rejection is now forbidden*:

> "**Extensions:** Producers MAY include any additional keys. Consumers SHOULD preserve unknown keys
> when round-tripping and **MUST NOT** reject documents with unrecognized fields."
> — SPEC.md §4.1 ([v0.2 §4.1](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md), lines 218–220)

> **This is v0.2's UNDECLARED breaking change (§13 omission 1 of 3 — see [§9](#9-verification-of-13-changes-from-v01)).**
> v0.1 read `SHOULD NOT` at `okf/SPEC.md:161-162`; v0.2 reads `MUST NOT` at `:219-220`. §13 lists
> two breaking changes and this is not one of them. A force upgrade from SHOULD to MUST is
> unambiguously normative, so §13's *"Everything else … is carried forward unchanged"* is not
> accurate.
>
> **It is good news for yf**: it hardens the exact hook `okf_spec`/`id`/`epic`/`fingerprint` ride on.
> A v0.2 consumer may still decline to *preserve* yf's keys, but may no longer *reject* a document
> for carrying them.

This is the hook the yf layer builds on: yf-specific keys (id, author, created, status, epic,
fingerprint, `okf_spec`) ride as producer extension keys alongside the one mandatory `type`
([S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1),
[L4](../../../docs/research/001-okf-compliance-delta/sources.md#l4),
[L8](../../../docs/research/001-okf-compliance-delta/sources.md#l8)). **Caveat carried from research
001, updated for v0.2:** `SHOULD` preservation is still a recommendation a consumer may decline, and
no producer→consumer→producer round-trip of yf keys through any OKF tool is demonstrated in the
record, so lossless end-to-end carry remains unverified `[insufficient evidence]`. Carry is
*permitted*; carry is not *guaranteed*. **What v0.2 changes is the floor, not the ceiling** — a
consumer may drop yf's keys on round-trip, but may not refuse the document. Consumer round-trip
fidelity is a named plan-046 carve-out, filed upstream rather than claimed (Issue 5.5(iii)).

## 7. Other OKF recommendations (SHOULD / optional)

| Rule | OKF force | Status in the reference bundles | yf treatment |
|:--|:-:|:--|:--|
| `okf_version` key on the **bundle-root `index.md`** (**§12**) | optional | Spec'd but **unexercised** — the only match repo-wide is the SPEC prose itself ([S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)) | yf carries it on a bundle-**root** `index.md`, pinned **`0.2`** (see YF-EXTENSIONS). v0.2 §8 makes the root-only restriction explicit — SPEC `REQ-OKF-032` |
| ~~`# Citations` bottom heading~~ | **REMOVED in v0.2** | The `ga4` concept ended in a `# Citations` bare-URL list ([S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3)) | **NON-GOAL, and now moot** — see below |
| `/`-absolute cross-links (**§6**) | **SHOULD** ("the **recommended** form") | Unexercised — the reference `index.md` uses **relative** links ([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)) | yf keeps bundle-relative GFM links; not adopted |
| Progressive-disclosure `index.md` at **each** directory level (**§8**) | structural, `MAY` | The `ga4` bundle nests `index.md` per level ([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)) | Adopted **at the bundle root**; the nested tier is **deferred** (plan-046 D-9, filed as a follow-on) |

*(The `(§5)`→`(§12)` change on the first row is the pre-existing citation error corrected in §3, not
an application of the section map.)*

**`# Citations` is an explicit NON-GOAL for plan-029** (SPEC §1 out-of-scope; plan Non-goals) —
**and v0.2 has retired the heading entirely**, so the non-goal is now moot.

> **v0.2 breaking change B-2, declared.** §13.1: *"The body `# Citations` list is superseded by
> `sources`. Provenance moves to frontmatter (§5.1). Consumers SHOULD read `sources` and MAY still
> parse a legacy `# Citations` body list for v0.1 documents."* v0.2 §4.2's conventional-heading table
> **removes** the `# Citations` row and **adds** `# Computation`; v0.2 has no citations section at
> all (v0.1 §8 is gone).
>
> **yoshiko-flow's exposure to B-2 is exactly ZERO** — the corpus emits `# Citations` **0** times.
> The paragraph below records the v0.1-era *decision*, whose conclusion is vindicated but whose
> stated **premise** ("OKF's `# Citations` heading is SHOULD-level") is now false. Retained as the
> reasoning of record, marked wrong-after:

*(v0.1-era rationale, premise now false.)* OKF's
`# Citations` heading was SHOULD-level. Research `sources.md` already uses GFM citation links, and
normalizing to OKF's numbered/bare-URL `# Citations` form is **not** a conformance requirement and
is out of scope — `yf-okf` neither emits nor enforces it. (SPEC vs. its own reference bundle even
diverge on citation *numbering* — the SPEC shows numbered `[1] [text](url)`; the `ga4` concept uses
an unnumbered bare-URL list — signaling Google does not exercise the recommendation uniformly,
[S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1),
[S3](../../../docs/research/001-okf-compliance-delta/sources.md#s3).)

## 7a. Where OKF v0.2 is ambiguous or silent

These are points the **yf extension layer had to decide** because OKF does not mandate them — flagged
so `OKF-YF-EXTENSIONS.md` owns the decision explicitly rather than implying OKF requires it.

> **One entry was RETIRED at v0.2.** `log.md` entry format and ordering used to head this list, on
> the grounds that "OKF is silent on entry format and ordering". **v0.2 §9 is not silent** — it
> specifies newest-first ordering and an ISO-8601 `YYYY-MM-DD` **MUST** on date headings. yf's rule
> is now baseline conformance, not a yf decision, and has been moved to [§4](#4-reserved-file-logmd-9-update-history).
> This was the single largest status change in the reconciliation. *(Two sibling sites made the same
> now-false claim and are corrected by the same plan: this section's former bullet and §4 above
> (Issue 2.3), plus `OKF-YF-EXTENSIONS.md:84` (Issue 2.7).)*

- **`index.md` rendering beyond the stated shape** — v0.2 §8 fixes considerably more than v0.1 §6 did
  (no frontmatter except a root `okf_version`; sectioned body; entries SHOULD carry the linked
  concept's `description`), but still does not fix the heading text, the entry template, or whether a
  subdirectory entry targets the directory or a nested `index.md` — §8's own example uses the bare
  directory (`subdir/`) while the `ga4` bundle used `datasets/index.md`
  ([S4](../../../docs/research/001-okf-compliance-delta/sources.md#s4)). yf adopts the listing model,
  supplies per-skill rendering adapters, and generates the **root** listing (`reindex`).
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

**And the boundary is not one-way.** The v0.1→v0.2 reconciliation moved `log.md` ordering *out* of
this list and into the baseline — an upstream revision can **claim** a silence the yf layer had
decided. That is the case this list must be re-read for on every future bump, not just the reverse.

## 8. The v0.1→v0.2 section map

**This table is the check.** Every `(§N)` in this document is verified **row by row** against it, not
by grep: v0.2 uses identical `(§N)` syntax, so a surviving v0.1 pointer is textually
indistinguishable from a correct v0.2 one. Measured by extracting the `^## N. Title` headings from
both vendored specs ([v0.1](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.1.md), [v0.2](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md)); the derivation is recorded in
[`exec-002`](../../../docs/plans/plan-046-james-dixson-aabefa/findings/exec-002-v01-verbatim-delta.md).

| v0.1 | v0.2 | note |
| :-- | :-- | :-- |
| §1 Motivation | §1 Motivation | number unchanged |
| §2 Terminology | §2 Terminology | number unchanged |
| §3 Bundle Structure | §3 Bundle structure | number unchanged |
| §4 Concept Documents | §4 Concept documents | number unchanged |
| §5 Cross-linking | **§6** Cross-linking and paths | renumbered |
| §6 Index Files | **§8** Index files | renumbered |
| §7 Log Files (optional) | **§9** Log files | renumbered; "(optional)" dropped from the title |
| §8 Citations | **removed** | declared breaking change B-2 |
| §9 Conformance | **§11** Conformance | renumbered |
| §10 Relationship to other formats | **removed** | **undeclared** |
| §11 Versioning | **§12** Versioning | renumbered |
| — | §5 Provenance, trust, and lifecycle | new (declared additive) |
| — | §7 Actor convention | new (declared additive) |
| — | §10 Attested computations concept | new (declared additive) |
| — | §13 Changes from v0.1 | new (the changelog itself) |

**Where each `(§N)` in this document now points:**

| Site | v0.2 target | Derivation |
| :-- | :-- | :-- |
| §2 heading + conformance quote | §11 | map row `§9 → §11` |
| §2 B3 row, §3 reserved-file quote | §8 / §9 | map rows `§6 → §8`, `§7 → §9` |
| §3 heading | §8 | map row `§6 → §8` |
| §3 `okf_version` row, §7 `okf_version` row | **§12** | **error correction, not the map** — see §3 |
| §4 heading + format quote | §9 | map row `§7 → §9` |
| §5 heading | §4 | unchanged |
| §5 `generated`, `sources`, `verified`, `status` rows | §5 | new in v0.2 |
| §6 heading + extension quote | §4.1 | unchanged |
| §7 `/`-absolute cross-links row | **§6** | map row `§5 → §6` |
| §7 nested-`index.md` row | §8 | map row `§6 → §8` |

> **exp-002's map carried one error, corrected here.** exp-002 recorded *"versioning §5→§12"*.
> Measured: versioning is v0.1 **§11** → v0.2 §12; v0.1 §5 is *Cross-linking* → v0.2 §6. exp-002's
> other three entries (`index §6→§8`, `log §7→§9`, `conformance §9→§11`) are correct.

## 9. Verification of §13 "Changes from v0.1"

§13 is **accurate in what it declares and incomplete in what it omits**. It declares two breaking
changes (B-1 `timestamp`, B-2 `# Citations`) and both check out verbatim. It then closes §13.2 with:

> "Everything else (bundle structure, reserved filenames, the required `type`, recommended
> `title`/`description`/`resource`/`tags`, cross-linking, index files, log files, permissive
> conformance) is carried forward unchanged."

**Three things are not carried forward unchanged.**

### 9.1 `SHOULD NOT` → `MUST NOT` on the extension clause (undeclared, normative)

Quoted side by side so the delta is auditable:

| | text |
| :-- | :-- |
| **v0.1** `okf/SPEC.md:161-162` | "SHOULD preserve unknown keys when round-tripping and **SHOULD NOT** reject documents with unrecognized fields." |
| **v0.2** `okf/SPEC.md:219-220` | "SHOULD preserve unknown keys when round-tripping and **MUST NOT** reject documents with unrecognized fields." |

A SHOULD→MUST force upgrade is normative by definition. See §6.

*Provenance note:* exp-002 identified this from **three independent in-repo copies** of the v0.1
clause (`OKF-BASELINE.md:149-151`, research-001 `sources.md:46`, `Summary.md:154`) — a sound
triangulation, but still second-hand. Issue 2.1 fetched v0.1 verbatim from upstream, and the clause
**confirms at first hand**. This is what closing risk R1 bought.

### 9.2 The renumbering is nowhere flagged (undeclared, silent)

Seven sections moved (§8). §13 does not mention renumbering in either subsection. Because v0.2 reuses
the `(§N)` syntax, **no textual search can distinguish** a stale v0.1 pointer from a correct v0.2
one — which is precisely why §8 exists and why this document's citations are verified row by row.

### 9.3 v0.1 §10 "Relationship to other formats" was removed entirely (undeclared)

An entire section — positioning OKF against LLM wiki repositories, Obsidian/Notion, and
"metadata as code" — is absent from v0.2, which has no counterpart section under any title. §13
lists no removal other than `# Citations`.

*Found only after Issue 2.1 vendored v0.1: exp-002 could not observe the absence of a section whose
body it did not have. It is the clearest evidence that §13 is not exhaustive — the concern that
motivated risk R1 in the first place.*

### 9.4 A nuance, recorded but not counted: conformance gained conditional MUSTs

v0.2 §11 adds a paragraph absent from v0.1 §9, carrying two MUSTs gated on the new families being
present (*"MUST treat a bare `verified` mapping as a one-element list"*; *"MUST NOT reject a concept
for missing any optional family"*). **Neither binds yf**, and they are arguably covered by §13.2's
"new optional keys". Recorded as a nuance rather than a fourth omission because the reading is
genuinely arguable — this document's standard is to record rather than silently resolve.

v0.1 §9 also lost a closing rationale sentence (*"This permissive consumption model is
intentional…"*). Prose only, no normative force.

### 9.5 What §13 gets right

- **B-1 and B-2 are accurate**, including the consumer fallbacks they promise.
- **The three conformance MUSTs are genuinely carried forward** — byte-identical apart from the
  renumbered cross-references (§2). This is the non-change that makes the whole reconciliation a
  documentation edit.
- **yoshiko-flow's exposure to both declared breaking changes is exactly ZERO** — `timestamp` and
  `# Citations` are each emitted **0** times corpus-wide. yf declined both v0.1 features
  independently, long before v0.2 retired them.

## 10. References

- [`references/okf-spec-v0.2.md`](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md) — **the primary source**: upstream OKF v0.2, verbatim.
- [`references/okf-spec-v0.1.md`](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.1.md) — upstream OKF v0.1, verbatim, for diffing.
- [`findings/exec-002-v01-verbatim-delta.md`](../../../docs/plans/plan-046-james-dixson-aabefa/findings/exec-002-v01-verbatim-delta.md) — the measured v0.1↔v0.2 delta behind §8 and §9.
- `docs/research/001-okf-compliance-delta/Summary.md` and `sources.md` (S1–S5, E1–E14, L1–L8) — the
  distilled OKF **v0.1** facts this doc used to pin. **Superseded** (plan-046 Issue 2.9); retained as
  provenance for unchanged claims only.
- `docs/research/001-okf-compliance-delta/sources.okf-spec-primary.json` (primary OKF spec citations).
- `skills/yf-okf/SPEC.md` — REQ-OKF-001..003 (bundle model), REQ-OKF-FAM-002 (this doc is authored
  spec kept in agreement with the baked-in ruleset).
- `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` — the yoshiko-flow layer that decides the silences above.

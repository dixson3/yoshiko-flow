# OKF-YF-EXTENSIONS — the yoshiko-flow extension layer

> **Status: Draft (plan-029, Epic 1, Issue 1.2).** Human-readable reference for the **yoshiko-flow
> extensions layered on top of** `OKF-BASELINE.md`. This is the layer **yf owns and versions
> independently** — isolating upstream OKF drift to `OKF-BASELINE.md` (plan-029 R3). It is one of the
> two authored specs kept **in agreement** with the machine-readable ruleset baked into `okf.py` by a
> `yf-drift-check` edge (SPEC REQ-OKF-FAM-002); the engine does **not** parse this file at runtime.

## 0. Relationship to the baseline

The **effective ruleset** the engine enforces against a bundle is the composition
**OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ resolved-per-skill-`OKF-EXTENSION.md`** (SPEC
REQ-OKF-FAM-001). This doc is the middle member. It **adds** yf opinion; it never relaxes an OKF
MUST (`OKF-BASELINE.md` §2, B1–B3). Where OKF v0.2 is silent (`OKF-BASELINE.md` §7a), this layer
makes the decision explicit — those decisions are *yf-owned*, not OKF mandates.

Terminology and REQ ids match `skills/yf-okf/SPEC.md` exactly. Cross-references to research facts
cite `docs/research/001-okf-compliance-delta/sources.md`.

## 1. Extension-key namespacing (SPEC REQ-OKF-030)

OKF mandates exactly one key — `type` — and welcomes arbitrary producer keys under its extension
mechanism (`OKF-BASELINE.md` §6,
[S1](../../../docs/research/001-okf-compliance-delta/sources.md#s1)). The yf layer defines **which**
producer keys yf artifacts carry and how they are named. Beyond OKF's `type`, every **non-reserved**
yf artifact carries an **`okf_spec:`** key naming the OKF-\* family member it conforms to (SPEC
REQ-OKF-030):

| Key | Owner | Purpose |
|:--|:--|:--|
| `type` | OKF (baseline MUST) | Open-vocabulary concept kind, e.g. `Plan`, `Research Index`, `Incubator` |
| `okf_spec` | **yf** | Names the OKF-\* member this artifact conforms to: `OKF-PLAN`, `OKF-RESEARCH`, `OKF-INCUBATOR` |
| `okf_version` | OKF (optional) | Baseline version pin; MAY appear only on a bundle-**root** `index.md` (v0.2 §8; SPEC `REQ-OKF-032`), pinned `0.2` (SPEC `REQ-OKF-FAM-005`) |
| `id` | yf | Artifact identity (e.g. plan id) |
| `author` | yf | Authoring operator |
| `created` | yf | ISO-8601 creation date |
| `status` | **OKF (v0.2 §5.4), yf declines** | Lifecycle state. A **key COLLISION**, resolved as a declared **permanent divergence** — see §9 entry 3 |
| `epic` | yf | Owning beads epic |
| `fingerprint` | yf | Content fingerprint (yf-plan) |
| `superseded_by` | yf | Marks an artifact whose conclusions a later artifact supersedes. Free-form prose naming the successor and what it changed. Applied to **whole legacy bundles** so a stale premise cannot flow silently into a document derived from it (plan-046 Issue 2.9) |

**Namespacing rules:**

- yf-owned frontmatter keys are the **flat, documented set above** (plus any per-skill keys a
  member's `OKF-EXTENSION.md` declares). They coexist with `type` under OKF's producer-key mechanism
  — `type` stays OKF's; `okf_spec` and the rest are yf's.
- `okf_spec` is the **member selector**: it tells the engine which per-skill `OKF-EXTENSION.md`
  ruleset composes on top of BASELINE ∪ YF-EXTENSIONS for this artifact (§5).
- **Merge-and-preserve (SPEC REQ-OKF-070).** Writing yf keys **never drops or overwrites** a
  pre-existing frontmatter key. A file carrying foreign frontmatter (e.g. Obsidian `tags`, `aliases`,
  `cssclass`) retains every such key byte-for-byte after a write or migrate. yf adds only its own
  keys; it is a well-behaved OKF producer under §4.1.

## 2. The dual field model (SPEC REQ-OKF-020 / REQ-OKF-021)

yf-plan and yf-research today carry metadata as human-readable `**Field:**` prose header lines, not
YAML ([L4](../../../docs/research/001-okf-compliance-delta/sources.md#l4),
[L6](../../../docs/research/001-okf-compliance-delta/sources.md#l6)). yf-incubator carries YAML
frontmatter but no `type` ([L8](../../../docs/research/001-okf-compliance-delta/sources.md#l8)).
Rather than discard the human surface, yf **dual-writes** both.

- **One writer, one model (REQ-OKF-020).** A single writer, from a single in-memory model, emits
  **both** a YAML frontmatter block (the machine / OKF surface) **and** the human-readable
  `**Field:**` lines. The two representations are **never authored independently** — this is the
  anti-divergence invariant (R7). There is no path that writes one without the other.
- **Frontmatter-first read with `**Field:**` fallback (REQ-OKF-021).** A reader takes the
  frontmatter value when a key is present in frontmatter; when absent, it **falls back** to the
  legacy `**Field:**` line. Un-migrated artifacts (frontmatter-free legacy plans) keep working
  unchanged.

### Placement invariant — fingerprint safety (SPEC REQ-OKF-010)

In any artifact that carries them, **both** the YAML frontmatter block **and** the `**Field:**`
block sit **above the first `## ` heading** of the document.

Rationale: yf-plan's content fingerprint **excludes everything before the first `## `** — a
positional exclusion (exp-001 `_plan_content_sections` / `_plan_content_fingerprint`). Keeping both
metadata blocks above the first `## ` means neither enters the fingerprint, so **adding frontmatter
and removing an in-`plan.md` phase log are both hash-neutral by construction**. The engine enforces
this placement on emit. This is why OKF's silence on frontmatter *placement* (`OKF-BASELINE.md` §7a)
is resolved in yf's favor — OKF only requires a parseable block; yf pins *where* it goes.

## 3. The `log.md` format choice (SPEC REQ-OKF-002)

> **STATUS CHANGE at OKF v0.2 — this section is no longer an extension decision.** It previously
> read: *"OKF reserves `log.md` as 'update history' but demonstrates no format and no ordering"*, and
> presented the rendering below as yf filling a silence. **v0.2 §9 is not silent.** It specifies *"a
> flat list of date-grouped entries, newest first"* and makes ISO-8601 `YYYY-MM-DD` date headings a
> **MUST**. The rule below is now **baseline conformance** (`OKF-BASELINE.md` §4), not a yf choice —
> and yf had guessed right, so **no artifact changes**.
>
> *(Corrected by plan-046 Issue 2.7. This was the **third** site making the now-false silence claim;
> the other two were `OKF-BASELINE.md` §4 and §7a, corrected by Issue 2.3. It is fixed authority and
> there is no `spec`→`spec` edge in `DRIFT-CHECK.md`, so nothing would have detected it.)*

OKF v0.1 reserved `log.md` as "update history" but demonstrated **no format and no ordering** (zero
`log.md` existed in the v0.1 reference repo,
[S5](../../../docs/research/001-okf-compliance-delta/sources.md#s5)). What was a yf rendering choice
is now the upstream rule, restated here as the **yf-side record of a rule that moved across the
baseline/extensions boundary**:

- Entries are **newest-first**, grouped under **ISO-8601 (`YYYY-MM-DD`) date headings** — v0.2 §9,
  MUST on the date form.
- `log.md` replaces the legacy per-skill log surfaces: yf-plan's in-`plan.md` `**Phase log:**` block
  ([L4](../../../docs/research/001-okf-compliance-delta/sources.md#l4)), yf-research's timestamped
  `_index.md` ledger ([L7](../../../docs/research/001-okf-compliance-delta/sources.md#l7)), and
  yf-incubator's `## Decision log` body section
  ([L8](../../../docs/research/001-okf-compliance-delta/sources.md#l8)).
- `log.md` is a **reserved** file: it carries **no `type` and no `okf_spec`** (SPEC REQ-OKF-031). It
  is structural, not a typed concept document.
- **Migration must preserve the first `scoping:` date** into `log.md` in a machine-readable form
  (SPEC REQ-OKF-MIG-002) so yf-plan's grandfather clause (`_plan_first_scoping_date`) still resolves —
  the single most dangerous migration step (exp-001).

The `append_log` engine op writes newest-first ISO-8601 entries (SPEC §3 interface). Index/log
*rendering* details that genuinely differ across the three consumers live in each consumer's
`OKF-EXTENSION.md` and per-skill `spec/` amendments, not here.

## 4. Reserved-file and reserved-subdir conventions beyond OKF

OKF reserves two filenames (`index.md`, `log.md`) at any level (`OKF-BASELINE.md` §3–§4). yf adopts
both and adds structural conventions OKF does not specify:

- **Reserved `index.md` replaces the legacy index filenames** — `README.md` (yf-plan, yf-incubator)
  and `_index.md` (yf-research) all become the OKF-reserved `index.md` (SPEC REQ-OKF-001;
  [L1](../../../docs/research/001-okf-compliance-delta/sources.md#l1),
  [L5](../../../docs/research/001-okf-compliance-delta/sources.md#l5),
  [L8](../../../docs/research/001-okf-compliance-delta/sources.md#l8)). It is a
  progressive-disclosure listing (`#` heading + `- description` bullets), carrying **no frontmatter
  except** a bundle-root `okf_version` (SPEC REQ-OKF-031).
- **Reserved `index.md` / `log.md` carry no `type`, no `okf_spec`** (SPEC REQ-OKF-031); a bundle-root
  `index.md` MAY carry only `okf_version`.
- **Per-artifact-type reserved subdirs.** A consumer's `OKF-EXTENSION.md` MAY declare reserved
  subdirectories for its artifact type (e.g. yf-plan's `references/`, `reviews/`; yf-research's
  `artifacts/`, `scripts/`, `diagrams/`). These are yf conventions layered on OKF's flat
  "directory of markdown files" model; the specific set is owned per-member, not globally here.

## 5. The per-skill `OKF-EXTENSION.md` discovery / composition contract (SPEC REQ-OKF-FAM-001..003)

Each consumer skill **bundles its own** `OKF-EXTENSION.md` — the OKF-\* family member describing how
that skill's artifact type is structured and annotated (OKF-PLAN, OKF-RESEARCH, OKF-INCUBATOR;
authored in Issue 1.3). The engine composes them at runtime.

- **Composition (REQ-OKF-FAM-001).** The effective ruleset for a bundle is
  **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ resolved-per-skill-`OKF-EXTENSION`**.
- **Baked-in baseline (REQ-OKF-FAM-002).** The machine-readable **BASELINE + YF-EXTENSIONS** ruleset
  is **baked into `okf.py`** — no cross-skill file read at runtime. `OKF-BASELINE.md` and this doc are
  the **authored** spec, kept in agreement with the in-code ruleset by a `yf-drift-check` edge; the
  engine never parses these `.md` files at runtime.
- **Discovery by convention (REQ-OKF-FAM-003).** `resolve_extension(skill)` finds a consumer's
  per-skill extension at `skills/<skill>/OKF-EXTENSION.md`, resolved **`__file__`-relative** to the
  running (vendored) `okf.py`. Each skill ships its own `OKF-EXTENSION.md` **beside** its vendored
  `okf.py`, so full `check_conformance` composition runs from **any** vendored copy in **both** the
  worktree and installed address spaces — no sibling skill need be present on disk.
- **Member selector.** An artifact's `okf_spec:` frontmatter key (§1) names which member composes for
  that artifact.

Rationale for the baked-in / `__file__`-relative design (SPEC GR-OKF-003): a skill cannot assume
another skill is installed (the independent-installability invariant, exp-002). Sharing is by
**vendoring** the canonical `_shared/okf.py` into each consumer's `scripts/okf.py`, not by
cross-skill imports.

## 6. Single-file-bundle exemption & non-`.md` exclusion (SPEC REQ-OKF-050 / REQ-OKF-060)

OKF v0.2 describes a *directory* of files and addresses only `.md` conformance (`OKF-BASELINE.md`
§7a); it is silent on both cases below. yf makes each explicit:

- **Single-file-bundle exemption (REQ-OKF-050).** An artifact that is a **single `.md` file with no
  owning directory** (e.g. a single-file incubator, `Incubator/<slug>.md`) is **exempt** from the
  reserved `index.md` / `log.md` requirement; it carries only its own frontmatter + `type`. A bundle
  is single-file iff it is one `.md` with no dedicated bundle directory. When such a bundle gains
  substructure it is **promoted to dir-form**, at which point its body `## Files` / `## Decision log`
  sections map to reserved `index.md` / `log.md` respectively.
- **Non-`.md` exclusion (REQ-OKF-060).** Non-`.md` files (e.g. yf-research's `plan.yaml`,
  `sources.json`) are **excluded** from the frontmatter-`type` rule (REQ-OKF-003);
  `check_conformance` does not flag them for missing frontmatter.

## 7. Foreign-corpus survival (SPEC REQ-OKF-070 / REQ-OKF-071)

Two guarantees make the engine safe to run over a real, messy corpus (Epic 2 runs it over a copy of
an Obsidian vault):

- **Merge-and-preserve (REQ-OKF-070).** `write_frontmatter` and `migrate` add only yf keys and
  **never drop or overwrite** a pre-existing frontmatter key; foreign frontmatter round-trips
  byte-for-byte (§1). This is the well-behaved-producer side of OKF's §4.1 SHOULD (`OKF-BASELINE.md`
  §6).
- **Report-only and crash-safe (REQ-OKF-071).** `check` and `migrate --dry-run` over non-conforming,
  malformed, or unexpected input (unparseable YAML, missing files, binary content) **record a finding
  and continue** — they **never raise**. A scan of a messy foreign corpus returns a findings report,
  not a stack trace.

### 7a. Frontmatter re-serialization is not byte-neutral — a conscious, accepted decision

A `write_frontmatter` / `migrate` write re-serializes the **entire** frontmatter block through
PyYAML (`safe_dump`), so pre-existing keys are cosmetically reformatted — flow-style `tags: [a, b]`
becomes a block list and double quotes normalize to single quotes (observed in the Epic-2 vault
assessment, `okf-impact-primary-vault.md`). **Every key and value is preserved semantically**
(merge-and-preserve, REQ-OKF-070); only the YAML *rendering* of the block changes. This is
**accepted, not a latent surprise**, because:

- For **yf-plan** the frontmatter block sits **above the first `## `**, which the content
  fingerprint **excludes** (REQ-OKF-010 positional exclusion). Re-serializing the frontmatter is
  therefore **fingerprint-neutral** — a re-dumped block never flips an approved plan to
  stale-approved (REQ-OKF-MIG-003). Verified: a migrated `plan-001` copy has a byte-identical body
  from the first `## ` onward.
- **yf-research** and **yf-incubator** artifacts carry **no content fingerprint**, so a re-serialized
  frontmatter block has no downstream hash consequence at all.

The block-style reflow is purely cosmetic and Obsidian reads it identically. A minimal-diff
frontmatter writer (touch only added keys) is a possible future refinement but is **not** required
for correctness; the documented decision here is sufficient.

### 7b. Base-engine conformance vs. per-skill adapter completeness

A **base** `migrate` guarantees only OKF **baseline** conformance: reserved `index.md`/`log.md`
present (a member-declared rename or a synthesized skeleton, REQ-OKF-MIG-005), a role-mapped `type`
on every non-reserved `.md` (REQ-OKF-MIG-004), the `okf_spec` selector, the dual-field mirror of any
legacy `**Field:**` lines (REQ-OKF-020), and above-`## ` placement. These are the `check` **errors**.
A member's **extra required keys** (e.g. OKF-RESEARCH `idx`/`topic` on `Summary.md`, sourced from a
legacy prose header) and **type-vocabulary** membership are `check` **warnings** — backfilling them
and rendering the fine `index.md`/`log.md` bodies (the `_index.md` ledger split, the incubator
`## Files`/`## Decision log` promotion) is each consumer's **per-skill adapter** (Epics 3/4/5). So a
base-migrated bundle is **error-free** immediately, with warnings marking the adapter's remaining
work.

## 8. Reserved family name: `OKF-SPECIFICATION` (deferred) (SPEC REQ-OKF-FAM-004)

The family name **`OKF-SPECIFICATION`** is **reserved and deferred**. It is the intended member for
engineering `SPEC.md` files (the `REQ-*`-bearing per-skill specs). It is declared here as a **stub
only**:

- It is **not authored** in plan-029 and is **not applied** to any `SPEC.md` file in this plan.
- Authoring the member ruleset and retrofitting the skills' `SPEC.md` files to it is a **follow-on**,
  not this plan (SPEC §1 out-of-scope; plan Non-goals).
- Reserving the name now keeps the OKF-\* namespace coherent: `OKF-PLAN` / `OKF-RESEARCH` /
  `OKF-INCUBATOR` are authored (Issue 1.3); `OKF-SPECIFICATION` is the named-but-empty slot for a
  future engineering-spec member. No `okf_spec: OKF-SPECIFICATION` artifact exists yet.

## 9. OKF v0.2 concept mapping — AGREE / DIVERGE / ABSENT

v0.2 added four frontmatter families (§5, §10) that name concepts yoshiko-flow had already
implemented **privately**, under different keys and sometimes different semantics. Every pairing is
recorded here with an explicit verdict. **Nothing is silently reconciled, and nothing is renamed to
manufacture agreement** (plan-046 D-5) — a rename would assert an alignment that the evidence below
refutes.

| # | v0.2 concept | yf counterpart | Verdict |
| :-- | :-- | :-- | :-- |
| 1 | `sources` + credibility **signals** (§5.1) | `sources.md` / `sources.json` + a stored credibility **score** | **DIVERGE** |
| 2 | `verified[]` + `stale_after` (§5.2, §5.4) | red-team `verdict` + content `fingerprint` | **DIVERGE** |
| 3 | `status` (§5.4) | `status` (yf-plan workflow / yf-research phase) | **COLLISION → permanent divergence** |
| 4 | `generated: { by, at }` (§5.2) + actor convention (§7) | *(nothing)* | **ABSENT** |
| 5 | Attested Computation (§10) | the `- validated:` attestation receipt | **AGREE**, and yf goes further |

### 1. `sources` + credibility — DIVERGE (and yf is on the wrong side of it)

v0.2 §5.1 is explicit, and it is a design *prohibition*, not an omission:

> "It does not store a credibility score: a score is subjective, unportable across consumers, and
> goes stale. Credibility is *inferred* from the signals, the same way trust tiers are (§5.3), not
> stored."
> — [v0.2 §5.1](../../../docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md)

OKF records **objective per-source signals** (`author`, `usage_count`, `last_modified`, over a
`usage_window`). `yf-research` **stores a computed score**. That is precisely what v0.2 forbids.

**The evidence that this is a real divergence and not a naming accident is in yf's own corpus.**
`docs/research/001-okf-compliance-delta/sources.md` opens with a hand-written retraction of its own
scores:

> "**Read the `category` as the trust signal and disregard the numeric `overall`.** … the 41 is an
> internally-consistent score of the *wrong inputs*, not a corrupted number. The `category`
> (`high_trust` / `verify`) is a **manual override applied on domain-authority grounds, not
> recomputed from the rubric formula**."
> — [`sources.md`](../../../docs/research/001-okf-compliance-delta/sources.md) (yf's own most careful research bundle)

**Reproduced by execution** (`credibility_scorer.py score`, run during plan-046 Epic 2) — the same
publisher, split purely on hostname shape:

| url | `domain_authority` | `overall` | `category` |
| :-- | --: | --: | :-- |
| `https://docs.langchain.com/oss/python/langgraph/overview` | 77 | 84 | `high_trust` |
| `https://reference.langchain.com/python/langgraph/` | **30** | 68 | `verify` |
| `https://github.com/GoogleCloudPlatform/knowledge-catalog` | **30** | 68 | `verify` |

**Read this correctly: #147 is the stored-score design failing in the documented way, not a
heuristic bug** (plan-046 D-5). A stored score bakes one consumer's weighting into the artifact; when
the weighting is wrong the artifact carries the error forward, and the only remedies available are a
hand-written retraction or a silent re-score. yf has now done the former twice.

**Decision: DIVERGE, recorded, not reconciled.** Adopting v0.2's signals-not-scores model is a real
change to `yf-research` with its own consent profile, and **`sources` must not be renamed onto
`sources.md`** — that would assert alignment where the semantics oppose. Filed as a follow-on
(plan-046 Issue 5.5), not built here.

### 2. `verified[]` / `stale_after` vs `verdict` / `fingerprint` — DIVERGE (yf is stronger)

v0.2 §5.2 records attestations as `verified[]` entries; §5.4's `stale_after` marks a **date** after
which a concept should be treated as stale.

yf-plan carries the red-team `verdict` (APPROVE / REVISE / INVESTIGATE-MORE) and a **content
`fingerprint`** — a hash over the plan's content sections. These are not the same mechanism:

- `stale_after` is a **time-based** guess made at authoring time. It goes stale on schedule whether
  or not the content changed.
- `fingerprint` is **content-derived**. It goes stale **exactly when the content changes**, and
  never otherwise — which is why it can gate execution (`resume-scan`'s `stale_approved`).

**yf's mechanism is strictly stronger and is not expressible in v0.2's vocabulary.** There is no
v0.2 key whose value is a content hash. Recorded as a divergence yf **keeps**; the correct future
move is to propose it upstream, not to weaken it to fit.

### 3. `status` — COLLISION, resolved as a PERMANENT divergence

The one key where two spellings coexisting is **not** benign, because they are two **vocabularies on
the same key**. v0.2 §5.4 gives `status` a lifecycle vocabulary; yf already uses `status` for two
*different* things (the yf-plan workflow state and the yf-research pipeline phase), so the key
carries three meanings across the two specs.

**yf declines v0.2 §5.4 — for new emissions as well as old** (plan-046 D-7):

- `status` is read at a **gate**, against the literal `"approved"` (`plan_manager.py`), so a
  vocabulary change is an execution-eligibility change, not a labelling one (plan-046 R4).
- Corpus overlap with v0.2's vocabulary is **`draft` only, 2 of 46** — adopting the upstream
  vocabulary would rewrite 44 artifacts to resolve a 2-artifact ambiguity.

The `okf_spec`-namespacing rule (§1) is what makes this safe to declare rather than merely tolerate:
a consumer that understands v0.2 reads `okf_spec` and learns this is an `OKF-PLAN` artifact, whose
`status` is member-defined. And under v0.2 §4.1 a consumer **MUST NOT** reject the document for it.

### 4. `generated: { by, at }` + the actor convention — ABSENT

A **pure gap**, with no yf counterpart in either direction. v0.2 §5.2 records who produced a concept
and when; §7 fixes the actor form (`<producer>/<version>`, `human:<id>`, `process:<id>`) and makes
the `human:` prefix a **MUST** for hand-authored or human-confirmed content, because §5.3 keys trust
classification off it.

yf emits **nothing** here. `author` is the operator, not the producing agent, and no artifact records
whether a section was written by a human or an agent — which is exactly the distinction §7 exists to
carry. Recorded as ABSENT rather than mapped: `author` is **not** `generated.by`, and equating them
would be the rename this section refuses.

*(This is the one mapping where v0.2 is unambiguously ahead of yf.)*

### 5. Attested Computation vs the `- validated:` receipt — AGREE, and yf goes further

v0.2 §10 introduces the `Attested Computation` concept type: a computation whose result an
**attester** can re-derive, so a reader can trust the number without rerunning it. yf-plan's
completion gate records a persisted `- validated:` attestation in `log.md` — a receipt that a real
run happened green.

**They AGREE on the principle that matters**: a claim about a computation is only as good as
something that can re-derive it, and determinism is what makes the receipt meaningful. This is the
same doctrine plan-046 was written under — an artifact asserting something nothing checks is a
liability.

**And yf persists a receipt that v0.2 explicitly defers.** v0.2 §12 "Considered and deferred" lists
*"The full runtime protocol: receipt and verdict wire formats, and the attestation lifecycle around a
run"* as future work. yf's `- validated:` line is exactly such a receipt, in production. Recorded so a
future reader knows this is a place where yf leads rather than lags — and so that any future adoption
of §10 is understood as **formalizing** the receipt, not introducing it.

## 9a. Decisions made by NOT building (plan-046)

Two structural decisions this layer owns were resolved by **declining to build**. Both are recorded
with the measurement that produced them, so a future reader inherits the **evidence** rather than the
conclusion — and can overturn either by taking a new measurement rather than by re-arguing.

### Nested `log.md` — DROPPED PERMANENTLY

Not deferred. Dropped, on two independent grounds:

- **Nothing would populate it.** Every `okf.append_log` call site targets the bundle **root**. No
  producer event in yf-plan, yf-research or yf-incubator is scoped below the root, so a nested
  `log.md` would be created empty and stay empty.
- **There is no history to record.** Measured **1–2 distinct commit dates per subdirectory**
  corpus-wide. A per-directory update history whose content is one date is not an update history.

OKF v0.2 §9 permits a `log.md` *"at any level"*, so this is a yf decision and not a conformance
question — which is exactly why it belongs here rather than in `OKF-BASELINE.md`. **Reversing it
requires a producer that emits directory-scoped events**, which nothing currently does or plans to.

### Nested `index.md` — DEFERRED behind a `description:` producer change

Deferred, not dropped — the difference is that a concrete, measurable precondition is named.

| measurement | value | consequence |
| :-- | --: | :-- |
| nested files carrying `description:` | **189 of 993** (re-measured 2026-08-28; was "0 of 423" at plan-046 — stale on BOTH terms). A MOVING figure: re-measure before citing. | most generated nested entries would still be bare |
| subdirectories that would get a listing of no value | **74 of 142 (52%)** | over half the output is noise |
| bundles whose **root** index already carries described subdirectory entries | **16 of 19** | the information is already available one level up |

OKF v0.2 §8 states that index entries *"SHOULD include the description from the linked concept's
frontmatter"* — so the upstream model **presumes** a `description:` that this corpus does not have.
Generating nested indexes now would satisfy the letter of §8 while producing **most** entries
that carry no description, which is the "asserting something nothing checks" failure this whole plan
was written against. **The precondition has begun to be met, not been met** — the 165 that do carry
one are concentrated in the twelve newest bundles, so the deferral stands on current coverage rather
than on the absence the plan-046 figure asserted.

**The precondition, and why the hard part dissolves.** Once producers stamp `description:`, nested
indexes become worth generating **forward-only**: new bundles get real descriptions, old bundles keep
their hand-written root index, and the backfill question — the expensive, risky half — never has to
be answered at all. Filed upstream so the deferral is visible to the issue tracker and not only to
this file; recording it in one place and not the other is the same asymmetry that made #140's
original `include` disposition dishonest.

**What was built instead.** The **root** tier: `reindex --check` / `--write` (SPEC `REQ-OKF-011`).
Retargeting there was not a scope reduction — real drift existed at the root **today**, and was
invisible because `okf.py check` did no link resolution at all. plan-046 measured **37 broken links
and 23 unlisted members across 19 root indexes**, and fixed both the corpus and the two producers
that had been generating the breakage.

## 10. References

- `skills/yf-okf/spec/OKF-BASELINE.md` — the upstream OKF v0.2 baseline this layer sits on.
- `skills/yf-okf/SPEC.md` — REQ-OKF-010/020/021/030/031, REQ-OKF-050/060, REQ-OKF-070/071,
  REQ-OKF-FAM-001..004, REQ-OKF-MIG-002.
- Per-skill members (Issue 1.3): `skills/yf-plan/OKF-EXTENSION.md` (OKF-PLAN),
  `skills/yf-research/OKF-EXTENSION.md` (OKF-RESEARCH),
  `skills/yf-incubator/OKF-EXTENSION.md` (OKF-INCUBATOR).
- `_shared/okf.py` (canonical engine) + vendored `skills/<skill>/scripts/okf.py` (Issues 1.4/1.6).
- `docs/research/001-okf-compliance-delta/Summary.md`, `sources.md` (L1–L8 local-artifact facts).
- `docs/plans/plan-029-james-dixson-75fd34/findings/exp-001-plan-manager-okf-coupling.md`
  (fingerprint positional-exclusion) and `exp-002-shared-engine-api-surface.md` (vendoring model).

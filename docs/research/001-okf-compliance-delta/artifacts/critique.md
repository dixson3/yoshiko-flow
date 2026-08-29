---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Red-team critique — 001-okf-compliance-delta

Reviewer: red-team agent. Scope: `Summary.md` on its own merits, against `sources.json` /
`sources.md` and the cluster/triangulation artifacts. Items are ranked most-serious first.
Each item: what's wrong · where · concrete fix.

---

## 1. [CRITICAL] "MUST/mandates preserve" contradicts the quoted spec ("SHOULD preserve") — the load-bearing claim under the recommendation

**What's wrong.** The report's central rationale for the export-emit recommendation is that
extension-key preservation is *guaranteed*. It states this as a hard requirement in at least
four places:

- L27: "producers MAY add any keys and consumers **must preserve** them"
- L134: "OKF explicitly welcomes arbitrary producer keys and **mandates their preservation**"
- L173-174: "producers MAY add any additional keys that consumers **must preserve** on round-trip"
- Table row 7 (L47): "any keys, **preserved on round-trip**"

But the actual spec text — quoted in the report itself at L137 and in
`cluster-okf-spec-primary.md:181` — is **SHOULD**, not MUST:

> "Consumers **SHOULD** preserve unknown keys when round-tripping and **SHOULD NOT** reject
> documents with unrecognized fields."

SHOULD/SHOULD NOT is a recommendation a conformant consumer may decline. The report elevates it
to a guarantee, which is an RFC-2119-level misreading that its own cited quote refutes.

**Where.** L27, L134, L173-174, table row 7 (L47); executive summary L26 ("ride losslessly").

**Fix.** Replace every "must preserve / mandates preservation / guaranteed" with the spec's
actual force: "consumers **SHOULD** preserve unknown keys (a recommendation, not a hard
requirement)." Then re-state the Q3 rationale item 1 honestly: preservation is *encouraged by
the spec*, not *guaranteed*, so lossless carry depends on consumer good behavior. This weakens —
but does not destroy — the export-emit argument; the recommendation must be re-grounded on the
softened claim (see item 6).

---

## 2. [MAJOR] "Losslessly" is asserted, never evidenced — no round-trip is demonstrated

**What's wrong.** The word "losslessly / lossless" appears as a settled fact (L26, L47, L119,
L142, L169, L171; `[confidence: high]` at L182). But no evidence in the record shows an actual
producer→consumer→producer round-trip of yf-* metadata through any OKF tool. The claim is
*inferred* from the SHOULD-preserve clause (item 1), not *tested*. None of the seven tooling
sources (E4-E10) is cited as having round-tripped extension keys; okf-schema (E6) even
"preserves YAML comments," implying preservation is a per-tool feature, not a format guarantee.

**Where.** L26, L47, L119, L142, L169-171, and the `[confidence: high]` tag at L182.

**Fix.** Downgrade "losslessly" to "in principle, extension keys can carry the metadata, though
round-trip preservation is spec-recommended (SHOULD) and unverified against any specific consumer
`[insufficient evidence]`." Lower the S1 answer's tag from `[confidence: high]` to
`[confidence: moderate]` and add round-trip verification to the open-questions list.

---

## 3. [MAJOR] The recommendation rests on an unestablished demand premise — no source shows any consumer wants yf-* artifacts as OKF

**What's wrong.** The report thoroughly answers *how* to comply and *how cheap* it is, but never
establishes *why* — i.e., that any consumer would ingest yf-plan / yf-research / yf-incubator
folders as OKF bundles. The only named production consumer is Google's Knowledge Catalog (E1),
which ingests *data-catalog* knowledge, not software-plan/research folders. The "interop unlock"
(L159-161, L226-231) lists generic capabilities of the format, not demand for these specific
artifacts. The recommendation to build an emitter is therefore justified by supply-side ease, not
by any evidenced use case.

**Where.** Executive summary L30-35; Q3 "Document-only … forgoes the concrete interop win"
(L157-161); S3 "What compliance unlocks" (L226-231).

**Fix.** Add an explicit caveat that the *demand* for OKF-conformant yf-* artifacts is
unestablished `[insufficient evidence]`, and reframe the recommendation as "low-cost optionality
should demand emerge" rather than "captures the interop upside." This directly bears on whether
the export-emit path is over-claimed (it is, mildly).

---

## 4. [MAJOR] One-sided cost analysis of export-emit; the "thin emitter" is under-specified

**What's wrong.** The report charges the native path with disrupting the audit and the
`**Field:**` convention, but credits the export-emit path with essentially zero cost ("thin OKF
emitter," L31; "sidesteps both impacts," L207-208). Two costs are never weighed:

(a) **Dual-representation drift/staleness.** An exported bundle is a *snapshot* that can fall out
of sync with the mutating source of truth; the emitter must be re-run and the export is stale
between runs. This is the classic cost of any derived view and is unaddressed.

(b) **The emitter is not thin.** OKF conformance is a *whole-bundle* property: per
`cluster-okf-spec-primary.md:86-96` and S4, a conformant bundle needs a progressive-disclosure
`index.md` **at every directory level**, reserved-name compliance, and per-file `type`
frontmatter. An emitter that produces this from a plan folder must synthesize a nested `index.md`
tree and type every file — materially more than "add a `type` key." L208's "produced only in the
exported view" hand-waves this.

**Where.** L31, L153-165, L207-208.

**Fix.** Add a "costs of the export-emit path" paragraph covering (a) snapshot drift and (b) the
real scope of generating a conformant directory tree (nested `index.md` per S4). Then re-affirm
or qualify the recommendation with both sides on the table.

---

## 5. [MODERATE] Credibility category overrides are not reconciled with the rubric numeric band; the whole report hinges on accepting the override

**What's wrong.** Every source carries an `overall` in the questionable band (S/L/E-cluster ≈ 41;
E1 = 58; E14 = 46) yet is labeled `high_trust` (80-100 band) or `verify` (60-79 band). The
report discloses this as a "principled override" for a known scorer bug (L253-255, sources.md
L3-7) — good — but the override only relabels the *category* while leaving the sub-scores
untouched. Under the rubric (Domain 35 / Currency 20 / Expertise 25 / Bias 20), the 41 is
internally consistent with the sub-scores (e.g. S1: .35·30 + .20·50 + .25·35 + .20·60 = 41), so
the `high_trust` label is a bare assertion, not a recomputed score. The proper repair for a
primary source like the official Google SPEC is to correct `domain_authority` (30 → ~90) and
`expertise` (35 → high), which would legitimately lift `overall` into the high_trust band.
Consequence: **if a reader declines the override, every load-bearing claim rests on
questionable-band sources** — the report's entire credibility depends on accepting a
hand-relabeling.

**Where.** `sources.json` all entries; Summary caveat L253-255; sources.md L3-7.

**Fix.** For the primary sources (S1-S5, L1-L8, E1) recompute `domain_authority`/`expertise` to
reflect primary-artifact authority so the numeric `overall` lands in the asserted band, OR state
explicitly that `category` is a manual primary-source designation not derived from the rubric
formula and that numeric `overall` should be disregarded. Do not leave a 41/high_trust pair
unexplained per source.

---

## 6. [MODERATE] The "guaranteed lossless + low bar" recommendation is over-claimed relative to (softened) evidence

**What's wrong.** The recommendation's confidence (L163-165: "the hedge that captures the interop
upside at minimal disruption, justified precisely because the extension mechanism makes the emit
lossless") is only as strong as items 1-4 allow. Once "lossless/guaranteed" becomes
"spec-recommended/unverified" (items 1-2), demand is flagged unestablished (item 3), and the
emitter's true scope is acknowledged (item 4), the categorical "recommended: export-emit"
verdict is stronger than the evidence supports.

**Where.** Executive summary L30-35; Q3 L127-165.

**Fix.** Keep export-emit as the *leading option* but frame it as a provisional recommendation
contingent on (i) SHOULD-level preservation being acceptable, (ii) demand materializing, and
(iii) accepting emitter build cost. Present it as "the least-regret path given a v0.1 draft,"
which the evidence *does* support, rather than a fidelity-guaranteed win.

---

## 7. [MINOR] Rule 6 "non-gap" partly rests on an `[insufficient evidence]` item

**What's wrong.** Rule 6 (`/`-absolute links) is classified "non-gap" partly on the tools "already
matching what the reference `index.md` does" (L91-92), but the report simultaneously admits tool
link-emission syntax is "not directly evidenced" and claims nothing "beyond 'uses relative links
within a folder' `[insufficient evidence]`" (L93-95, L246-249). The OKF-side of the non-gap (SHOULD,
unexercised, per S4) is solid; the tool-side leans on the IE item.

**Where.** Table row 6 (L46); Q1 L88-95; caveat L246-249.

**Fix.** Narrow the Rule 6 non-gap justification to the OKF side only ("absolute links are SHOULD
and unexercised even in Google's bundles [S4](sources.md#s4)"), and drop the implication that tool link
conformance is established.

---

## 8. [MINOR] Load-bearing SPEC quotes are not surfaced in the `sources.md` S1 record

**What's wrong.** The S1 entry in `sources.md`/`sources.json` carries only the "intentionally
minimal" quote. Yet the normative claims attributed to S1 — reserved `index.md`/`log.md`, "non-
`index.md` = concept doc requiring `type`," the §9 conformance two-item bar, and the extension
clause — are the load-bearing ones. They ARE directly quoted in `cluster-okf-spec-primary.md`
(lines 41, 82-83, 181-182, 191-199) and `triangulation.md`, so the evidence exists; it just is
not visible to a reader verifying via `sources.md`. Per the epistemics rule (direct quotes over
paraphrase), a reader checking the citation cannot confirm the claim from the source record.

**Where.** `sources.md` S1 (L11-20); Summary claims at L74-75, L106, L137.

**Fix.** Add the reserved-filename (§3.1) and §9-conformance direct quotes (already in the cluster
artifact) to the S1 record in `sources.md`, so the load-bearing normative claims are quote-backed
at the point of citation.

---

## 9. [MINOR] Small paraphrase/derivation items to tighten

- **"non-empty `type`"** (executive summary L11): the "non-empty" qualifier is stated but the
  §9 quote backing it lives in the cluster artifact (`:199`), not in the Summary or S1 record.
  Surface the quote or soften to "a `type` field."
- **"roughly five weeks old at retrieval"** (S3, L218): derived from E1's June date vs. the
  2026-07-17 retrieval; fine, but mark it as computed from E1 rather than free-standing.
- **E-cluster selection framing** (S3, L221-225): "at least seven independent third-party tools
  already exist and converge" reads as momentum. The report does hedge ("solo/hobby-scale,
  low-adoption"), but the sentence order leads with the impressive count. Lead with the hedge:
  these are hobby-scale packages whose *existence* does not evidence adoption.

---

## 10. [TRACK — acceptable as-is, do not over-correct] Well-handled items

These are called out so the refiner does NOT "fix" them into false precision:

- The v0.1-draft / single-adopter skepticism is consistently and appropriately flagged (L34,
  L148, L212-218, L238) — the report does **not** treat OKF as more settled than the evidence
  supports. Good.
- The `[uncertain]` at L245 (whether any consumer parses citation numbering) is a genuine open
  question, correctly left as a caveat rather than resolved by speculation. Acceptable to keep.
- The IE1/IE2 `[insufficient evidence]` tags on tool link-emission (L95, L249) are honest; the
  fix is item 7 (don't let them silently back a "non-gap"), not removing the tags.
- The Agent Skills structural parallel is correctly down-tagged `[moderate]` / "structural
  parallel rather than a compliance fact" (L233). Keep.

---

## Summary for the refiner

The report is well-structured and its skepticism about OKF's maturity is sound, but the **primary
recommendation over-reads its central evidence**. The single most important fix is **item 1**: the
extension-preservation clause is **SHOULD**, not MUST, and the report's "must/mandates/guaranteed/
lossless" language must be corrected to match its own quote — after which items 2-4 and 6 follow
(soften "lossless," acknowledge unverified round-trip, add the missing cost side, flag the
unestablished demand premise, and reframe the recommendation as least-regret rather than
fidelity-guaranteed). Item 5 (credibility numeric/category reconciliation) is the top
non-recommendation fix. No `questionable`/`avoid`-only load-bearing citations exist *given the
override* — but that override is itself the report's single point of credibility failure and must
be either recomputed or explicitly de-numericized.

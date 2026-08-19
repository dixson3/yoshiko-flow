---
type: Plan
okf_spec: OKF-PLAN
id: plan-047-james-dixson-dec9ff
author: james-dixson
created: '2026-08-18'
status: complete
fingerprint: 0147839b3354d363fece6966f68d7f6c0321b95a391c3cedcc33ca47b01440b8
epic: yf-mol-63g
---
# Plan: Make yf artifact documents mechanically parseable: formal templates per document type, per-type linters, a corpus normalizer, and a common plan extractor that machine-reads the epic/issue DAG

**ID:** plan-047-james-dixson-dec9ff
**Author:** james-dixson
**Created:** 2026-08-18
**Status:** complete
**Epic:** yf-mol-63g
**Fingerprint:** 0147839b3354d363fece6966f68d7f6c0321b95a391c3cedcc33ca47b01440b8
**Coarse tracker:** [#175](https://github.com/dixson3/yoshiko-flow/issues/175)

## Objective
Make yf artifact documents mechanically parseable: formal templates per document type, per-type linters, a corpus normalizer, and a common plan extractor that machine-reads the epic/issue DAG

## Motivation

Every yf artifact document — `plan.md`, findings, review passes, research reports, `SPEC.md` —
is authored as prose against a template that **nothing executes**. The templates are real
(`yf-plan` SKILL.md:365-420 declares the plan.md form) and mostly correct; what is missing is a
verdict. Research 004 named this exact shape as the corpus's top-ranked defect class: *a step
with no exit code is not a step* (#149, M5).

Three concrete consequences, all measured over the 46-plan corpus:

1. **The plan's primary payload is machine-unreadable.** `plan_manager.py` is 4779 lines and
   contains **zero** parses of `### Epic N:` or `- Issue N.M:`. The epic/issue DAG — the thing
   the document exists to express — is read by exactly one consumer: an LLM at SKILL.md §5.2a
   freehanding `bd create` calls. Pour fidelity (bead count vs issue count) is checked by
   nobody; `yf-herdr` already lists the mismatch as a deviation to watch for, which is an
   admission that a human is the only checksum.

2. **Two proposed review passes are blocked on the same missing substrate.** #113 (topological
   DAG walk) and #174 (falsify-every-criterion + cross-check matrix) both need the plan's
   assertions as a machine-readable list. #174 says so explicitly: *"they likely want to be one
   pass with two checks… worth deciding deliberately rather than building two extractors."*

3. **Where the template is silent, the corpus diverged — and where it was specific, plans drifted
   and recovered.** Measured:

   | Section | Template | Corpus |
   | :-- | :-- | :-- |
   | Epics / Issues | fully specified | conformant in 041–046; **6 non-canonical variants** (V2–V7) plus 51 non-issue bullets, in 002–040 |
   | Gate `Test:` | `- Test: <bash command>` | 38 clean · 3 parenthetical-before-colon · 1 fenced · 1 `*(none)*` |
   | Gate `Blocks:` | `<issue refs>`, no grammar | **10 distinct shapes** across **72** values; only 12 (16.7%) parse as a pure id list |
   | Risks & Mitigations | **empty** | 28 table · 18 bullet |
   | Success Criteria | **empty** | 23 bullet · 21 numbered · 2 table · 1 none (47 dirs, incl. this plan) |
   | Criterion ids | unspecified | **2 of 47** plans *declare* them (31 of 367 items); 6 more reference undeclared positional ids |

   The last row is load-bearing: #174's criterion↔issue matrix is bidirectional and **45 of 47**
   plans have no key to join on.

The operator's framing at scoping: the messiness may be natural evolution, so anchor a standard
on the most recent and most relevant form, then build linters per document type and a mechanical
normalizer for history — the same shape as the OKF migrate path that plan-046 shipped.

## Upstream Issues


| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #113 | execution-rehearsal review pass (topological DAG walk) | partial | This plan delivers the extractor the walk requires. The walk itself stays open — its own re-open trigger (two consecutive plans with structural escapes) is **not** met; plan-046's two escapes were claims-class, not ordering-class. | Issue 5.3 |
| #174 | review-phase validation pass (falsify + cross-check matrix) | partial | Both halves need the plan's assertions machine-readable. Templates additionally add the criterion ids its matrix joins on. The two checks themselves stay open. | Issue 0.3, 5.1 |
| #149 | M5/M9 — process rules nothing executes; remediation edges only in prose | partial | M9 becomes a template field (a bundle declares what it fixes) plus a linter check. M5 as a class is not closed here. | Issue 0.3, 0.4 |
| #165 | SPEC `Verification:` lines are prose shaped like commands | deferred | Was `include`. **Re-dispositioned at completion**: Issue 7.2 was in Epic 7, descoped at the D-13 split, so nothing landed and nothing is claimed. | Issue 7.2 (descoped) |
| #125 | status-enum hardening for `update-status` | include | The documented 9-value vocabulary becomes a linted enum rather than doc/spec/test-enforced only. | Issue 2.5 |
| #135 | a measured literal in plan.md goes stale | deferred | Was `partial`. **Re-dispositioned at completion**: Issue 7.3 was descoped with Epic 7. | Issue 7.3 (descoped) |
| #62 | propose yf-spec skill | deferred | Was `partial`. **Re-dispositioned at completion**: Issue 7.5 was descoped with Epic 7; the general engine landed, the spec linter did not. | Issue 7.5 (descoped) |
| #173 | criteria/dispositions never checked against the enforcing engine | exclude | The evidence record for #174, deliberately kept open. | |
| #150 | research 004 — process-defect mining | exclude | Coarse research tracker and evidence source, not work. | |
| #145 | yf-retrospective skill | exclude | Adjacent (escape-rate measurement), separate deliverable. | |
| [#175](https://github.com/dixson3/yoshiko-flow/issues/175) | plan-047: mechanically parseable yf artifact documents | tracker | Filed at drafting (operator-authorized) rather than at INTAKE, because `stamp-tracker` runs at the pour (§5.2a) — **before Epic 0 executes** — so the row must already match `_TRACKER_ROW_RE` (`plan_manager.py:1383`, cell 1 must be `#<digits>`) by approval time. Red-team pass 3 (H3) measured the placeholder form returning `{"status":"skipped"}`, which would have left the epic with no `external_ref` and invisible to `upstream.py closable` — the failure #131 exists to prevent and the mechanism by which five trackers went stale. | Issue 10.5 |
| #172 | yf-plan README.md File Layout stale | exclude | The skill-dir README, not a bundle document type. | |

## Scope Decisions

Recorded at scoping (2026-08-18), operator-answered. D-numbers are referenced by epics and risks.

- **D-1 — Type scope: everything.** Every document type across `yf-plan` bundles, `yf-research`
  bundles, and the `SPEC.md` family. Chosen over two narrower options with the cost stated
  (~8+ epics, three normalizer corpora rather than one).
- **D-2 (AMENDED at investigation) — Hash-neutral rewrites only; abort if any hash moves.**
  Original: "normalize completed plans in place, like the OKF migrate path." EXP-006 measured that
  framing to be **inverted** — REQ-OKF-MIG-003 *requires* OKF migrate to keep the content
  fingerprint stable (`okf.py:1173`: `# remove the block (above first ## -> hash-neutral,
  REQ-OKF-MIG-003)`), so migrate is the opposite case, not the precedent. Amended form:
  - Rewrite a `status: complete` plan **only** where the transform provably does not move
    `_plan_content_fingerprint`. Measured hash-neutral set: per-line `rstrip`, blank-line
    collapse, any edit above the first `##`, and the whole `## Upstream Issues` section.
  - **Mechanical postcondition:** recompute the fingerprint before and after every file and
    **abort the entire run if any hash moves.** This is REQ-OKF-MIG-003's discipline applied to
    the normalizer.
  - Everything hash-changing is **report-only** on completed plans.
  - **Consequence: the #109 hazard dissolves rather than being mitigated.** EXP-006 measured that
    a hash-changing sweep would tag all 46 plans `⚠ STALE-APPROVED` forever, reproducing a
    closed-as-not-reproducible issue. Under D-2-amended no hash moves, so #109 stays correctly
    closed and needs no fix.
  - **Refusal predicate:** `status == "complete"` AND `stored == current` AND path under a plans
    root. Explicitly excludes `skills/**/fixtures/**` (17 `plan.md` files that are the
    `test_classify_deliverable.py` ground-truth corpus; the classifier is markup-sensitive).
    Note the gate is **inert on today's corpus** — all 46 are `complete` — so it needs a synthetic
    non-complete fixture to be validated at all.
- **D-2a (derived) — hash-neutral is NOT line-count-neutral, and 17 plans are cited by line.**
  EXP-006 measured **91 `plan.md:<line>` citations** resolving into this repo (≈70 of them the
  evidence chain of `docs/research/004-…`), plus **≥102 verbatim review quotes**. The fingerprint
  ignores blank lines, so blank-line collapse is hash-neutral **but still shifts every line below
  it**. Therefore the normalizer must be **line-count preserving** (rstrip only) on every cited plan.
  **The protected set is DERIVED at execution, never frozen** (review M10): EXP-006 reported 17
  distinct cited plans, but an independent sweep of fully-qualified citations found **104
  occurrences across 22 plans**. The methodologies differ and neither is authoritative, so Issue
  8.3 computes the set from a committed script and prints it, and SC29 asserts over *that* set. Trailing-whitespace strip is the only
  transform that is both.
- **D-3 — Enforcement binds at three points, and the on-edit trigger is ALWAYS-ON.**
  1. **Fail-closed at INTAKE** — wired into the existing `audit` / `ready-check` gate; a
     non-conformant plan cannot reach `approved`.
  2. **A `CHANGE-VALIDATION.md` recipe row** — FAST and FULL tiers.
  3. **On-edit** — unlike `yf-markdown-lint`'s per-repo opt-in marker, this trigger is
     **always opt-in with no opt-out** (operator's words). The silent-no-op escape hatch other
     yf triggers carry is deliberately withheld.
- **D-4 — Templates ADD required structure, they do not merely codify.** New mandatory fields
  where #174's consumers need them: stable criterion ids, a `discharged-by:` mapping per
  criterion, a grammar for gate `Blocks:`, and a fixed shape for Risks. This changes what
  authors must write.
- **D-5 — `discharged-by` is mandatory for NEW plans and backfilled for none.** EXP-002 measured
  that the criterion→issue edge cannot be recovered: only 13.3% of 367 criteria mention an issue
  id, the strongest signal is ~73% precise, combined yield ≈10%. The failure is structural — *a
  mention is not a discharge*. #174's matrix starts empty and fills forward; plans 039/040 give it
  real input immediately. Shipping inferred edges would be **worse than an empty matrix**, because
  nothing downstream could distinguish them (plan-046's rule: "a stale index asserts something
  false").
- **D-6 — the canonical Risks table is `| # | Risk | Severity | Mitigation |`** (anchor: plans
  039–043). Preserves the `Severity` column that **7 of EXP-002's 8** lossy residue items carry (6 `Severity`
  + 1 `Sev`); only plan-005's `Likelihood`/`Impact` pair has no slot and is handled as a one-off.
- **D-7 (AMENDED at review) — fix the `SKILL.md` template first, but pursue STRUCTURAL equality,
  not byte equality.** EXP-001 measured `SKILL.md`'s plan.md-structure block (lines **365–420**) as
  the single most-drifted artifact in the investigation: it teaches the retired `**Phase log:**`
  block (contradicting REQ-DATA-012 and 18 of the last 18 plans), omits required frontmatter, and
  carries authoring annotations — `(when upstream issues incorporated)` appears **0 times** in 47
  plans. The original decision said "make it byte-identical to `seed_plan_md`". **Red-team pass 1
  (H5) falsified that as self-defeating:** the seed emits `_To be determined._` bodies and stamps
  frontmatter afterwards, while `SKILL.md` teaches the `### Epic 1:` / `- Issue 1.2:` /
  `- depends-on:` grammar. Byte-equality would **delete that grammar from the one place authors
  read it** — the grammar Issues 1.1, 5.1 and 6.3 must derive the schema from and Issue 0.4 is
  amending. Amended form: the *shared* region (heading set, required fields, section order) is
  generated from `seed_plan_md` through `_shared/sync.py`'s marker-fence mechanism — the pattern
  Issue 1.2 already uses — and the illustrative epic/gate grammar lives **outside** the fence, in
  its own separately-linted block.
- **D-8 — the template format splits by producer class.** EXP-004 measured 0% drift on every
  code-generated type with a check and 14–95% on every unenforced agent-written type. Therefore:
  code-generated types **derive their template from the producer function** so it cannot diverge;
  agent-written types get a **standalone declared artifact** the agent file references. One
  uniform format for both would re-introduce, at the template layer, the hand-maintained-duplicate
  problem `_shared/sync.py` exists to eliminate.
- **D-9 (AMENDED at review) — the 140-file figure is the ON-EDIT trigger's hazard, not INTAKE's,
  and it does NOT force an epic ordering.** The original decision read EXP-004's *inference* that a
  fail-closed INTAKE binding would hard-fail 140 existing files (111 findings + 15 `pass-N` + 13
  `upstream-<N>` + 1 SPEC) and made the normalizer a hard prerequisite of the binding. **EXP-005
  measured the opposite in the same investigation:** *"automatic paths that re-audit a `complete`
  plan: **none**"* → *"a hard linter gate at INTAKE breaks **zero** existing plans."* `_audit_plan`
  runs per-bundle on the plan under approval, never over the corpus. Issue 4.2's status-aware
  promotion (`complete` → report-only) independently dissolves the residue for the on-edit trigger.
  **This was an inference contradicted by a measurement in this plan's own findings**, and the cost
  was structural: it pushed Issue 2.5 — the only fix for the enforcement hole EXP-005 calls the real
  headline — to position 63 of 68, past D-13's declared split point. Amended: the normalizer (Epic 8)
  no longer gates the enforcement binding, and 2.5/2.6 are hoisted into Epic 2.
- **D-10 — the pour must preserve the issue id in bead METADATA, not a title convention.**
  EXP-003 measured three plans (006, 007, 036) where no bead title carries its issue id, making
  the mapping unreconstructable. `plan_issue: "3.5"` in metadata is strictly better than a title
  convention, because titles get rewritten.
- **D-11 — the vendored-content marker must be INTRODUCED, not honored.** EXP-004 measured that
  only 2 of 6 vendored `references/` files carry `source:`/`retrieved:` frontmatter; the three
  vendored `yf-herdr` copies and `salvaged-docusaurus.md` carry nothing, the latter's only signal
  being an English sentence. Backfilling the marker is a **P0 prerequisite epic**, not a
  nice-to-have — without it the first fail-closed INTAKE breaks on a file it must never read.
- **D-13 — the split point is after Epic 5, and it is declared now rather than discovered.** At
  **11 epics / 77 issues** this is the largest plan to date (plan-045: 46 issues). Epics 0–5 are
  self-contained and deliver the SPEC amendments, the validation gate, the carve-outs, the schema
  engine, and the extractor + pour-fidelity comparator — the entire critical path for #113 and
  #174. Epics 6–10 are instantiation over a finished engine. **Trip condition, MECHANICAL (measured, not transcribed):** `ls reviews/pass-*.md | wc -l` ≥ 4 at the end of Epic 5 — the same
  signal `_audit_plan` check #5 already uses. The originally-drafted second clause ("any Epic 0–5
  issue reopened twice") was **dropped at review (M9)**: `bd` exposes Dolt version history but no
  reopen counter, so it would have been manual archaeology across ~35 beads — a trip condition with
  no exit code, inside the mitigation for the plan's highest-severity risk. Issue 10.0 emits
  `{tripped, review_cycles}` and **exits non-zero when tripped**, so the split is a gate rather than
  a request. 10.0 `depends-on: 5.5` and therefore travels with the Epics-0–5 half if the split fires.
- **D-12 — two constructs get a document decision, not a parser** (EXP-003): a `depends-on` value
  carrying a prose tail is **forbidden** by the linter (rationale moves to the body); and a
  structurally-present but deliberately-not-poured epic (plan-041's "MOVED to plan-042") needs an
  explicit marker, or the extractor reports a false pour defect forever.

### In-scope document types (measured inventory, 2026-08-18)

| Bundle | Type | Instances | Authored / Generated |
| :-- | :-- | --: | :-- |
| plan | `plan.md` | 46 (+ this plan) | authored |
| plan | `findings/*.md` | **205** (117 real + 87 fixture + 1) | authored (sub-agent) |
| plan | `reviews/pass-N.md` | 108 | generated from a fixed schema |
| plan | `context.md` | 46 | generated |
| plan | `upstream-triage.md` | 28 | generated |
| plan | `index.md` / `log.md` | **16 / 20** | generated (OKF reserved) |
| plan | `references/*.md` | **194** (154 generated + 13 tracker-variant + 16 hand-authored + 6 vendored `.md` + 5 `comment-*.md`) | **generated or vendored verbatim — carve-out candidate** |
| research | `Summary.md` | 4 | authored |
| research | `sources.md` | 4 | generated |
| research | `artifacts/*.md` (triangulation, critique, cluster-*) | **39** | authored (sub-agent) |
| spec | `SPEC.md` + `skills/*/SPEC.md` + `skills/*/spec/*.md` | 53 | authored |

**Carve-out under investigation:** `references/*` is 194 files and is overwhelmingly *vendored
verbatim* (upstream issue bodies, third-party specs). Linting vendored content against an
authored template would be wrong; EXP-004 settles the boundary.

## Out of Scope

- Building #113's topological DAG walk or #174's two checks. This plan delivers only the
  substrate both require, and says so in the triage dispositions.
- A full `yf-spec` skill (#62) — only the spec-linter is in scope.
- Solving corpus self-inclusion (#135) or M5 as a general class (#149).

## Investigation Findings

**Pre-investigation checkpoint (2026-08-18).** Six experiments identified. Approach hypothesis:
a single `document_types/<type>.toml` schema format + one linter engine + one normalizer, with
each document type instantiated as data rather than as its own script — mirroring how
`CHANGE-VALIDATION.md` and `DRIFT-CHECK.md` express per-repo policy as a manifest over a shared
engine. The extractor is then a consumer of the same schema, not a separate parser.

| Exp | Question |
| :-- | :-- |
| EXP-001 | Anchor derivation for `plan.md`: field by field, what is the canonical grammar, and does the operator's "natural evolution" hypothesis hold per section (monotonic recovery) or is it fashion cycling? |
| EXP-002 | Historical normalizability: what fraction of the 46-plan corpus is auto-rewritable without human judgment, and what is the residue? Can criterion ids (present in 6/46) be synthesized positionally, or does `discharged-by` force authorship? |
| EXP-003 | Extractor feasibility + **pour-fidelity baseline**: prototype `extract`, compare the extracted issue DAG against the beads actually poured per plan, and measure today's transcription defect rate — with a positive control proving the comparison can observe a mismatch. |
| EXP-004 | Type surface: for all ~15 candidate types, which are authored, which are emitted by code (and by what), which are vendored verbatim? Settles the `references/*` carve-out (191 at scoping; measured 194). |
| EXP-005 | Enforcement wiring: can the linter bind fail-closed at INTAKE without breaking existing flows? What does an always-on, no-opt-out on-edit trigger do in a repo with no yf documents? What is the FAST-tier cost? |
| EXP-006 | Fingerprint hazard of D-2: does rewriting a completed plan's Epics section change its content fingerprint, and does anything downstream read it for a `complete` plan? Are all 46 in fact `complete`? |

### Returned — all six

**EXP-003 — extractor + pour fidelity** ([findings](findings/exp-003-extractor-pour-fidelity.md)).
**THE HEADLINE.** Of 43 comparable plans, **17 carry a pour divergence — a 40% per-plan defect
rate**: 885 declared dependency edges vs 860 in `bd`, **45 dropped and 20 invented**. A dropped
`blocks` edge means the coordinator marked a bead ready *before its declared predecessor*.
**Positive control passed** — deleting one issue line, one `depends-on`, and one gate block each
made the comparator fail, and it is silent on the unmutated original. Plans 006/007/036 have **no
recoverable plan↔bead mapping at all** and account for 43 of the 45 dropped edges as an artifact of
missing identity. Bead descriptions carry a median **68%** of the plan text. The last six plans
(041–046) are **0 dropped, 0 invented**.

**EXP-001 — anchor derivation** ([findings](findings/exp-001-anchor-derivation.md)). A canonical
grammar is derivable, and the DAG is **already semantically perfect** (0 prefix mismatches, 0
duplicate ids, 0 dangling `depends-on`, uniform 2-space indent) — only the lexical surface varies,
so normalization is a pure rewrite. **The operator's evolution hypothesis holds on 3 of 11 axes, and
all three were forced by an engineering change. Convergence tracks ENFORCEMENT, not recency** — run
this at plan-040 and "most recent" selects V3, a two-plan fashion. **The SKILL.md template is the
single most-drifted artifact measured**: it still teaches the retired `**Phase log:**` block and
omits required frontmatter.

**EXP-004 — type surface** ([findings](findings/exp-004-type-surface.md)). D-1 resolves to **15
markdown types + 2 hard carve-outs** (87 fixture files under
`plan-029/findings/okf-migration-samples/`, invisible at scoping; 9 vendored files). **The carve-out
is not detectable today** — 4 of 6 vendored `.md` files carry no marker, so this plan must
*introduce* one. The control that validates the thesis: **every enforced type measures 0% drift;
every unenforced agent-written type measures 14–95%.** #165 is **understated** — only 5.9% of 226
`Verification:` clauses are even command-shaped, **4 of the 12 executed are already FALSE** (2 more
pass only from the skill dir), and 265 of 312 testable REQs sit under no gate at all.

**EXP-002 — normalizability** ([findings](findings/exp-002-normalizability.md)). Syntactic
normalization is **83–100% mechanical**; 32 of 46 plans have zero residue. **But `discharged-by`
CANNOT be inferred**: only 13.3% of criteria mention an issue id, the strongest signal is ~73%
precise (n=11 across 2 plans), combined yield ≈ **10%**. A mention is not a discharge. Criterion ids
are declared in **2 of 47 plans**, not 6. Three meaning-changing diff classes found, incl. **T2
rewriting the historical phase log**.

**EXP-005 — enforcement wiring** ([findings](findings/exp-005-enforcement-wiring.md)). **There is no
code-level gate between a failing audit and `status: approved`** — `update-status` accepted
`approved` with exit 0 on a plan whose `ready-check` had just exited 3. The intake gate is prose
obedience. The existing audit is **disjoint** from document conformance. FAST-tier cost is a
non-constraint (**0.18 s** for 854 files). **No automatic path re-audits a `complete` plan**, so an
INTAKE gate breaks zero existing plans (this is what falsified D-9 as originally drafted).

**EXP-006 — normalization blast radius** ([findings](findings/exp-006-normalization-blast-radius.md)).
Fingerprint change **confirmed by execution** (two hashes). **D-2's "like the OKF migrate path"
precedent is INVERTED** — REQ-OKF-MIG-003 *requires* migrate to be hash-neutral. Zero verbs fail;
the damage is **91 line-number citations + ≥102 verbatim review quotes** breaking silently, and a
permanent wrong `⚠ STALE-APPROVED` tag on all 46 plans (**this is #109, closed-as-not-reproducible,
whose closing comment invites reopening on exactly this trigger**). D-2's hash-neutral amendment
dissolves that hazard rather than mitigating it.

### Corrections to this plan's own scoping measurements

| Scoping claim | Corrected | Source |
| :-- | :-- | :-- |
| "6 of 47 plans give criteria stable ids" | **2 of 47** declare them (31 of 367 items). The 6 were plans *referencing* undeclared positional ids | EXP-001, EXP-002 |
| `Blocks:` shapes include a bare integer `3` | **Never occurs as a whole value** — bare ints are continuation tokens inside `Epics 2, 3, 4`. A comma-splitting parser must not treat `3` as standalone | EXP-001 |
| `Blocks:` = 68 values | **72** historical (+5 in this plan). EXP-002 reported **75** because its sweep also caught 3 alternate key spellings (`Depends on:` ×2, `Gates:` ×1, all in plan-010). Both investigators were right; re-measured to settle it | EXP-001 / EXP-002 + re-measure |
| `findings/*` = 162 files | **205** — 87 are a nested fixture corpus | EXP-004 |
| corpus = 47 plans | **46 normalizable** (all `complete`) + this plan = 47 dirs | EXP-002 / EXP-001 |
| gate `Test:` = 1 fenced | **4** fenced multi-line (plans 037, 038, 042, 046) | EXP-001 |
| "4 legacy issue variants" | **6** non-canonical variants (V2–V7) plus 51 non-issue bullets | EXP-001 |
| "50% of executed `Verification:` clauses are FALSE" | **4 of 12 are false**; 2 more are cwd-dependent | EXP-004 |
| `Verification:` classes sum to 226 | the four classes sum to **222**; 4 are unbucketed and Issue 7.1 must account for them | EXP-004 |

## Approach

One **schema-driven engine**, three consumers, and an ordering forced by measurement.

The corpus splits cleanly by producer class (EXP-004: **0% drift on every enforced code-generated
type, 14–95% on every unenforced agent-written type**), so the template format splits the same way
(D-8): code-generated types derive their schema from the producer function so it cannot diverge;
agent-written types get a standalone declared schema their agent file references. A single
`document_types/<type>.toml` describes both, and one engine reads it.

Three consumers sit on that schema: the **linter** (does this document have the shape its type
declares), the **normalizer** (rewrite it into that shape, hash-neutrally), and the **extractor**
(emit the document as JSON). The extractor's first consumer is the **pour-fidelity comparator** —
which EXP-003 measured finding 65 wrong dependency edges across 17 of 43 plans — not #113 or #174.

**Two orderings are forced by measurement:**

1. **SPEC and the SKILL.md template first** (D-7). EXP-001 measured the declared template as the
   most-drifted artifact in the investigation. Deriving a schema from it today would encode a
   document that contradicts REQ-DATA-012.
2. **Carve-out markers before any linter binds** (D-11). 4 of 6 vendored `.md` files are
   undetectable today; a fail-closed binding would break on a file it must never read.

A third ordering — normalizer before the fail-closed binding — was **asserted at drafting and
withdrawn at review**: it rested on EXP-004's inference that 140 files would fail on day one, which
EXP-005 measured to be false for INTAKE (D-9 amended).

**Gate the engine before touching it**, but only once the engine exists to gate. Red-team pass 1
(H2) caught the drafted version putting a `CHANGE-VALIDATION.md` §1 row in front of a script two
epics away, so the order is now: minimal engine → carve-outs → gate wiring and falsification → full
engine. EXP-005 reproduced both decorative-row traps live — a FAST tier with zero commands reports
green (#164 class), and a linter that prints findings but exits 0 reports pass (#149 class).

## Epics

**Ordering revised at red-team pass 1 (H2, H3).** The original order applied plan-046's "gate the
engine before touching it" pattern — but in plan-046 *the engine already existed*. Here the gate's
own Test needs a linter, so gate-first as drafted put a `CHANGE-VALIDATION.md` §1 row in front of a
script that would not exist for two more epics, red-lighting this repo's FAST tier meanwhile.
Revised: **minimal engine → carve-outs → gate wiring and falsification → full engine.** The real
intent of gate-first is preserved — the gate is proven to fire before the bulk of the work — without
a row pointing at nothing.

### Epic 0: SPEC-first amendments
- Issue 1.99: an issue no success criterion names.

- Issue 0.0a: **Publish the free `REQ-DATA-*` id list before any id is written.** Run
  `grep -rhoE "REQ-DATA-[0-9]+" skills/ | sort -u` and record the live set and the free set in
  `assets/`. **No dependencies — this must run first.** Red-team pass 3 (M6) caught the drafted
  version putting this check inside Issue 0.9, which depends on every id-writing issue, so the
  guard installed to prevent the N1 collision was structurally *last*.
- Issue 0.0: **Preserve the investigation's instruments.** Copy EXP-003's `extract_plan.py` (362
  lines) and `pour_fidelity.py` (184 lines) into `assets/`, with the exact reproduction invocation
  (`pour_fidelity.py <all-beads.json> <plan-dirs…>`) recorded. They currently live untracked in an
  agent worktree that `yf-plan` tears down with `worktree remove --force`, and SC37 requires
  comparing against the baseline they produced. No dependencies — this is pure evidence rescue.
- Issue 0.1: **Fix the `SKILL.md` plan.md-structure block** (D-7 amended, lines **365–420**). Delete
  the `**Phase log:**` lines (retired by REQ-DATA-012), add the required YAML frontmatter block, drop
  the authoring annotations `(if needed)` and `(when upstream issues incorporated)`, and add explicit
  bodies for the Risks and Success Criteria sections. **Verify against the repo tree only** — the
  executing session's prose came from the *installed* copy at `~/.claude/skills/` and was loaded once
  at invocation, so it will not change until Issue 10.6. (The `plan_manager.py` edits later in this
  plan are genuinely safe: the repo `skills/` tree matches none of the resolver's six roots.)
- Issue 0.2: **Generate the shared region from `seed_plan_md` via `_shared/sync.py`'s marker fence**
  (D-7 amended), so heading set / required fields / section order cannot drift again. The
  illustrative epic-and-gate grammar stays **outside** the fence in its own block — byte-equality
  would delete the grammar authors read, which Issues 1.1, 5.1 and 6.3 must derive the schema from.
  - depends-on: 0.1
- Issue 0.3: **REQ-DATA-018** — success criteria carry stable ids (`SC<int>[a-z]`), unique within the
  plan, **insertable without renumbering** (plans 039/040 use `SC1b`/`SC5b`; 6 plans reference
  positions), plus a `Discharged-by` column and the bidirectional completeness rule. State in the
  amendment log that this is an **addition**, not a codification — precedent is 31 of 367 items in
  2 of 47 plans.
  - resolves-upstream: #174 (partial)
  - resolves-upstream: #149 (partial)
- Issue 0.4: **REQ-DATA-019** — the `Blocks:` referent alphabet: `issue-id`, an explicit `epic:<N>`
  form, and the reserved sentinel `reconcile step`. Forbid the trailing parenthetical on the sentinel
  (6 uses → move to `Instructions:`), forbid wildcards (`Issue 2.x / 3.x`, plan-008) and prose
  referents. Today only **12 of 72** values parse. **`epic:<N>` is introduced for FUTURE plans only**
  — nothing parses `Blocks:` today, and this plan's own gates use explicit issue-id lists, the only
  form the pour is documented to handle (review H6).
  - depends-on: 0.3
  - resolves-upstream: #149 (partial)
- Issue 0.5: **REQ-DATA-024** — the document-type schema format and the linter engine contract:
  verdict vocabulary `PASS | FAIL | INCONCLUSIVE` (`INCOMPLETE` is the reviewer agent's vocabulary,
  not a linter's), two severities where only structural is an error, and status-aware promotion.
- Issue 0.6: **REQ-DATA-025** — the normalizer's hash-neutral postcondition (D-2 amended): recompute
  `_plan_content_fingerprint` before and after every file; abort the run if any hash moves. **Pin the
  reporting shape here** — the `fingerprints_moved` key the Epic-8 gate asserts on is an output of a
  tool this plan has not yet designed, so the contract must be fixed before the gate depends on it.
- Issue 0.7: **REQ-DATA-026** — pour fidelity: the pour records `plan_issue: "<id>"` in bead metadata,
  and a comparator verdict is a plan-close gate.
- Issue 0.8: **REQ-DATA-027** — the vendored-content marker: `source:` + `retrieved:` frontmatter is
  the exclusion predicate; unmarked vendored content is a linter error, not a silent pass.
- Issue 0.9a: **REQ-DATA-028** — `update-status` refuses the `approved` transition unless
  `ready-check` is green, with a named override flag that logs a deviation. Issue 2.5 implements an
  **enforced CLI behaviour change** and no existing `REQ-*` covers it: `spec/cli.md` and
  `spec/phases.md` (REQ-STATUS-002) are silent on any gate at the transition. AGENTS.md: SPEC
  changes always happen first (review N7).
- Issue 0.9b: **Amend REQ-PORT-006** so its count-equality invariant distinguishes a **status
  transition into `review`** from a **red-team pass presentation**. Both emit a `review:` bullet
  today, so a correct bundle can show 2 lines / 1 file and fail the audit — reproduced on a scratch
  copy, and this bundle tripped it during drafting. The implementation is Issue 2.7; this is the
  SPEC half (review N6).
- Issue 0.9: Verification sweep — the **post-hoc** half of the allocation check (the pre-hoc half is
  Issue 0.0a). Re-run `grep -rhoE "REQ-DATA-[0-9]+" skills/ | sort -u` and confirm each of the
  **seven** new ids (018, 019, 024–028) appears exactly once and no pre-existing id was redefined,
  and that each is cited by its implementing issue. Then run the Tier-1 suites.
  **Note the scope bound rather than assuming coverage:** `cargo test --workspace` does **not** reach
  these ids — `coverage.rs:182` reads `../SPEC.md`, the root spec only, while `REQ-DATA-*` live in
  `skills/yf-plan/spec/data.md`. Red-team pass 2 caught this plan allocating `REQ-DATA-020`–`023`,
  which are **already live** (config/state split, `spec/data.md` lines 47, 62, 66, 70): the id family
  is not in numeric order, so counting forward from the highest-numbered nearby id is wrong. That was
  an inference where a measurement was one grep away — the plan's own thesis, committed inside a fix
  for it.
  - depends-on: 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9a, 0.9b

### Epic 1: Minimal engine and schema format

- Issue 1.1: Define `document_types/<type>.toml` — the per-type schema. Two flavours per D-8:
  `derive_from = "<producer function>"` for code-generated types, and an inline declared schema for
  agent-written ones.
  - depends-on: 0.9
- Issue 1.2: Implement a **minimal** `_shared/doc_lint.py` — reads the schema, walks a path set,
  emits `{"findings":[…]}` on `--json`, and **`sys.exit(1)` on any error-severity finding**. Enough
  to make the Epic-3 gate real; the severity/status/path machinery lands in Epic 4. Vendored by
  `_shared/sync.py`; `scripts/check_frontmatter.py` is the precedent for a repo-level doc linter as a
  recipe row, and it currently covers **zero** of `docs/plans/` or `docs/research/`.
  - depends-on: 1.1
- Issue 1.3: A seeded known-bad fixture plus a test asserting the linter exits **1** on it and **0**
  on a clean file. Without this the row is decorative — EXP-005 reproduced a linter printing
  `errors=4` while the engine reported `status: pass`, because it exited 0.
  - depends-on: 1.2
- Issue 1.4: **Author the four gate scripts and RECORD each one's pre-work red run.** Every gate
  `Test:` invokes `scripts/gate-*.sh`. Drafted, those scripts did not exist, so all three ran at
  **exit 127 (command not found)** — failing for a reason unrelated to the capability they claim to
  measure, and an *empty* script would exit **0**. Three requirements follow (review N4):
  1. the scripts are authored **here**, before Epic 3 makes their conditions true, so each can be
     run against a tree where it should be red;
  2. each script emits a **JSON verdict on stdout**, and **the gate `Test:` pipes it through
     `jq -e`** so the assertion lives *outside* the artifact it polices. This placement is the whole
     point: the gate resolver is **exit-code only** (`coordinator.md:179-183`, enforced by
     `test_gates.py:_classify`), so an assertion *inside* the script cannot stop an empty stub —
     measured, an empty `.sh` exits **0** and the gate resolves. With the `jq -e` outside, a stub
     emitting no JSON fails at the gate. The key sets are **per script, not shared**:
     `gate-doclint.sh` → `{commands: [{output_tail}]}` (note `output_tail` is a **per-command** key
     inside `commands[]`, not top-level — verified against `change_validation.py`, whose top-level
     keys are `tier/status/commands/first_failure`); `gate-carveouts.sh` →
     `{carved_findings, control_fired}`; `gate-normalizer.sh` → `{diff_bytes, fingerprints_moved}`
     (the latter pinned by Issue 0.6); `gate-upstream.sh` → `{comments, auth}`;
  3. **an explicit exit-code discipline**, because three consecutive review cycles produced a gate
     that failed for a reason unrelated to what it measures (`KeyError` on a nonexistent key →
     `exit 127` on an absent script → a stub exiting 0). Each fix was correct and the *class*
     survived. Piping through `jq -e` makes it worse on its own: without `pipefail` the pipeline
     reports jq's status alone, so "script missing" (127) and "assertion failed" become
     indistinguishable. Therefore every gate `Test:` opens with `set -o pipefail`, and each script
     returns **0 = capability present · 1 = capability absent · 2 = the harness could not run**,
     mapping onto the `INCONCLUSIVE` vocabulary Issue 4.4 already defines. A gate is only allowed to
     be red for reason 1;
  4. the pre-work run of **the gate `Test:` string** — not the bare script — is committed to
     `assets/gate-prework/` with its exit code and `stderr` tail, so the archived falsification
     evidence describes the command the gate actually executes.
  - depends-on: 1.3

### Epic 2: Carve-outs, and the enforcement hole

**Issue 2.5/2.6 hoisted here from the original Epic 8 (review H3).** They depend on neither the
normalizer nor the full linter, and EXP-005 verified `_audit_plan` needs zero call-site edits. This
is the highest-value fix in the plan and it was sitting at position 63 of 68.

- Issue 2.1: **Backfill `source:` / `retrieved:` frontmatter** onto the 4 unmarked vendored files
  (three `references/user-scope/yf-herdr/*` copies and `salvaged-docusaurus.md`). Measured: only
  `okf-spec-v0.1.md` and `-v0.2.md` carry it, and `salvaged-docusaurus.md`'s only vendoring signal is
  an English sentence in prose.
  - depends-on: 1.3
- Issue 2.2: **Declare the fixture carve-out glob** — `docs/plans/*/findings/okf-migration-samples/**`,
  **87 files** invisible at scoping, a before/after migration diff fixture containing whole nested
  bundles. Linting them would emit 87 false findings **and break the fixture**.
  - depends-on: 2.1
- Issue 2.3: **Declare the test-fixture carve-out** — `skills/**/fixtures/**`, 17 `plan.md` files that
  are `test_classify_deliverable.py`'s ground-truth corpus. The classifier is markup-sensitive
  (removing inline code spans from `plan-031` changed its signals 2 → 4), so a normalizer globbing
  `**/plan.md` would perturb the suite's `FN == 0` invariant.
  - depends-on: 2.2
- Issue 2.4: **Declare the `references/**` structural exclusion** — lint it for GFM validity but not
  for type schema. This glob had no owning issue in the drafted plan although Issue 9.2 listed it as
  one of four mechanisms making "no opt-out" honest (review, Missing #2). EXP-005 measured 10 findings
  there, two of them verbatim external spec copies.
  - depends-on: 2.3
- Issue 2.5: **Close the real enforcement hole (#125).** *(SPEC: Issue 0.9a.)* EXP-005 measured, and the red-team
  re-verified, that `update-status <dir> approved` succeeds with **exit 0** on a plan whose
  `ready-check` had just exited 3 — `update_status` (`plan_manager.py:1312`) is a free-form writer by
  its own docstring, so **the intake gate is prose obedience, not code**. Refuse `approved` unless
  `ready-check` is green, with an explicit override flag. **Without this, D-3's fail-closed binding
  does not exist no matter what the linter returns.**
  - depends-on: 2.6, 2.7
  - resolves-upstream: #125 (include)
- Issue 2.6: **Name the override flag before 2.5 implements it.** The drafted plan claimed a collision
  with "the existing stale-approval `--force`"; the red-team measured that `update_status` has **no
  options besides `-m`**, and the existing `--force` overrides are a **prose convention** (SKILL.md
  :502, :770-774, :1540 — "*Every `--force` override (stale-approval, audit bypass)* → `deviation`").
  So there is no flag to collide with, but there is a real deviation-vocabulary overlap. Decide
  whether the new CLI flag reuses `--force` or takes a distinct name, and record it. (The drafted
  plan had this issue depending on the one it was supposed to precede — review M3.)
  - depends-on: 2.4

- Issue 2.7: **Implement the REQ-PORT-006 disambiguation** (SPEC half: Issue 0.9b). Give the
  pass record a distinct marker, or key `_plan_review_line_count` on it, so a `review:` status
  transition no longer inflates the expected `pass-*.md` count. **Ordered before 2.5**: once 2.5
  makes `update-status approved` refuse on a red `ready-check`, a bundle that trips the conflation
  cannot be approved, and the fix must already be in.
  - depends-on: 2.4

### Epic 3: Wire the gate and falsify it

- Issue 3.1: Add a `doclint` id to `CHANGE-VALIDATION.md` §1 in the `fast` tier and the `full` tier.
  Measured cost is **0.18 s for the whole 854-file corpus**, so the two rows run the same command.
  Note `full`'s rows currently carry an **empty `id` column** and include `cargo clippy`, so this
  introduces an id convention there (review L4).
  - depends-on: 2.5
- Issue 3.2: Add §3 trigger-scope rows with the id stated per row: `docs/plans/**`,
  `docs/research/**`, `skills/*/SPEC.md`, `skills/*/spec/*.md`. **No `docs/plans/**` glob exists in §3
  today**, so every plan-bundle edit currently produces a vacuous green.
  - depends-on: 3.1
- Issue 3.3: **Fix the #164 mis-mapping in the same change** — §3 currently routes `skills/*/SPEC.md`
  to `uv-herdr-launch`, so every skill's SPEC.md runs yf-herdr's launch test. The `doclint` row is
  its natural replacement.
  - depends-on: 3.2
- Issue 3.4: **Falsify the gate.** Assert on `len(commands) > 0` and a non-empty `output_tail`,
  **never** on `status == "pass"`. Then inject a temporary mutant and confirm FAST reports
  `status: fail` with `doclint` as `first_failure`. Revert the mutant. EXP-005 reproduced both
  decorative-row failure modes live, and the drafted version of this gate's own Test was **broken in
  a third way** — it read a `layer_b` key that does not exist in this repo, so it failed today *and*
  would have failed post-work (review H1).
  - depends-on: 3.3
- Issue 3.5: Run the FULL tier once and record the result.
  - depends-on: 3.4

### Epic 4: The full linter engine

- Issue 4.1: **Severity tiers** — `E` structural, `W` completeness. Justified by measurement: a
  freshly `init`'d plan scores `errors=0, warnings=5`, and all five warnings are the template's own
  placeholder strings. The seeded template is structurally valid **by construction**, which is what
  makes errors-only non-hostile to a plan being written.
  - depends-on: 3.5
- Issue 4.2: **Status-aware promotion** — `scoping|investigating|drafting` → `W` informational;
  `review|ready-for-approval` → promote `W` to `E`; `complete` → **report-only, never error**. This is
  what dissolves the 140-file residue for the on-edit trigger (D-9 amended), independently of the
  normalizer.
  - depends-on: 4.1
- Issue 4.3: **Path-keying, never filename-keying** — `docs/plans/**/*.md`,
  `Incubator/*/plans/**/*.md`, `docs/research/**/*.md`. Filename-keying fires on the 17 fixture
  `plan.md` files for **62 errors**, and makes the trigger non-inert in a repo with no plans.
  - depends-on: 4.2
- Issue 4.4: `PASS | FAIL | INCONCLUSIVE` verdict plumbing, with `INCONCLUSIVE` reserved for "the
  linter could not run" (exit 2) and "not finished yet" expressed as **warning severity inside a
  PASS** — keeping the exit contract binary at every binding point.
  - depends-on: 4.3
- Issue 4.5: Tests, including an **idempotency self-check**.
  - depends-on: 4.4

### Epic 5: The common extractor and the pour-fidelity comparator

- Issue 5.1: `extract --json` over the schema — epics, issues, edges, gates (with `Test:` verbatim
  plus an `executable | fenced | sentinel` flag), criteria, upstream rows, cited `REQ-*` and
  `file:line`. **Must fail loudly (`unparsed`) rather than degrade**: EXP-003's prototype silently
  corrupted its own fidelity number four times before each widening was found.
  - depends-on: 4.5
  - resolves-upstream: #174 (partial)
- Issue 5.2: **Multi-line value handling for gate fields, plus two hazards this plan itself
  contains** (review L5): an issue whose `depends-on` names a **higher-numbered** sibling
  (`2.5 depends-on: 2.6, 2.7` — correct execution order, inverted numbering), and ids that sort
  wrongly lexically (`6.10` before `6.2`). Both must be test cases. Measured hazards: plan-040 L360's
  parenthetical wraps across two physical lines putting the colon on a continuation line, and 4 plans
  put the `Test:` value in a following fenced block. A one-physical-line parser mis-reads 5+ gates.
  - depends-on: 5.1
- Issue 5.3: The **pour-fidelity comparator** — join the extracted DAG to `bd list --all
  --include-gates` (**mandatory**; without it 121 gates and every gate edge are invisible with no
  error, #166). **Report the three populations separately** (review M1): plans with no recoverable
  mapping (006/007/036, which account for 43 of the 45 "dropped" edges as an artifact of missing
  identity), dropped edges among joinable plans (2), and invented edges (20).
  - depends-on: 5.2
  - resolves-upstream: #113 (partial)
- Issue 5.4: **Ship the comparator's positive control with it and run it in CI.** Deleting an issue
  line, a `depends-on`, and a gate block must each make it fail, and it must be silent on an unmutated
  copy. That control is the entire reason the 40% figure is trustworthy.
  - depends-on: 5.3
- Issue 5.5: Wire `plan_issue` bead metadata at the pour (D-10) and make the comparator a plan-close
  gate.
  - depends-on: 5.4

*(The drafted Issue 4.6 — re-point `classify-deliverable` off "whole-file keyword matching" — was
**deleted at review (H4)**. Its premise was false: `_ci_release_scan_region`
(`plan_manager.py:1616-1644`) is already section-scoped, its F1 already excludes Approach, and F5
already strips fences. Executed: plan-026 → `signals: []`, plan-027 → `signals: ["pipeline"]` — zero
double-counting. EXP-003 inferred it from its own grep and never read the code; the plan promoted the
inference to "Measured:". `SKILL.md:599`'s "weak" grades the `prose-only` evidence basis, not
whole-file matching.)*

### Epic 6: Instantiate the document types

Ordered by EXP-004's measured (value / cost) ranking. **SC20 is per-type rather than aggregate** — the
drafted plan covered all ten instantiation issues with one criterion satisfiable by ten empty
`.toml` files (pass-1, Missing #6). Issue 6.0 now commits one malformed fixture **per type**, so
SC20 must be discharged eight separate times. Issues 6.9 and 6.10 carry their own criteria.

- Issue 6.0: **Commit one malformed fixture per schema-bearing type** under
  `tests/fixtures/doclint/<type>/bad.md`. SC20 asserts each type's schema rejects its fixture; with
  no fixtures, SC20 is satisfiable by assertion alone and an empty schema passes (review N9).
  - depends-on: 5.5
- Issue 6.1: **`findings/*.md`** — 117 files, **94.9% drift**, template already a verbatim fenced
  block in `agents/investigator.md`. Best ratio in the corpus by an order of magnitude. Include the
  epistemics rule: **only 2 of 117 findings carry the mandated `**measured:**` marker**.
  - depends-on: 6.0
- Issue 6.2: **`reviews/pass-N.md`** — 108 files, 13.9% drift; extract the template from
  `SKILL.md:461-472`.
  - depends-on: 6.1
- Issue 6.3: **`plan.md`** — 0% drift today but zero enforcement; pure regression prevention. Schema
  derives from `seed_plan_md` per D-8, and includes the D-6 Risks table and the D-5 criterion ids +
  `Discharged-by` column.
  - depends-on: 6.2
- Issue 6.4: **`references/*`** — three declared variants: the `_write_upstream_reference` generated
  shape (154), the `Disposition: tracker` coarse-tracker variant (13 — forcing these into the
  generated shape would delete the disposition line), and a loose H1+provenance rule for the 16
  hand-authored one-offs.
  - depends-on: 6.3
- Issue 6.5: **Research `artifacts/*.md`** — 39 files, and **none of the 8 research agents has an
  `## Output` section**, so no template exists in any form. Net-new authoring.
  - depends-on: 6.4
- Issue 6.6: **Research `Summary.md`** — codify the emergent shape (4/4 open with an executive
  summary, 3/4 end with a sources section); add the missing sources section to research 001.
  - depends-on: 6.5
- Issue 6.7: **Per-skill `SPEC.md` structure** — `skills/SPEC-TEMPLATE.md` already exists as a
  checked-in file; fix `yf-herdr/SPEC.md` (the 1 of 19 drifted) in the same pass.
  - depends-on: 6.6
- Issue 6.8: **Extract-only types** — `context.md` (already audited by `_audit_plan`; move the check
  into the engine with no behavior change), `index.md` / `log.md` (already enforced by `okf.py
  reindex`), `upstream-triage.md`, `plan-retrospective.md`, research `sources.md`. All measured 0%
  drift.
  - depends-on: 6.7
- Issue 6.9: **Legacy `README.md` (30 files) is a normalizer target, not a linter target** — no
  producer exists, so no template should be authored. Migrate to `index.md`; 30 bundles report
  `no-index`.
  - depends-on: 6.8
- Issue 6.10: **Defer `DECISION.md` / `decisions/*` / `REDEPLOY-HANDOFF.md`** — 3 files do not justify
  3 templates. File the deferral upstream rather than leaving it implicit.
  - depends-on: 6.9

### Epic 7: SPEC `Verification:` — the runner and the restatement (#165)

- Issue 7.1: Classify all **226** `Verification:` clauses. EXP-004's classifier bucketed 222 — 13
  runnable (5.9%), 152 prose-with-ref, 53 prose, 4 command-mid-sentence — so **4 are unbucketed and
  must be accounted for**, not silently dropped.
  - depends-on: 6.10
- Issue 7.2: **Fix the 4 measurably FALSE clauses**:
  `yf-optimal-instructions/spec/integration.md:51` (path predates the `yf-` rename),
  `yf-plan/spec/agents.md:7` (hedges an unencodable exception in prose),
  `yf-research/spec/prerequisites.md:42` (names the installed path),
  `yf-research/spec/portability.md:44` (research 001 exits 2, still carrying a legacy `_index.md`).
  Plus the 2 cwd-dependent clauses that pass only from the skill dir.
  - depends-on: 7.1
  - resolves-upstream: #165 (include)
- Issue 7.3: **Restate the 5 hardcoded counts as self-consistency assertions.** All 5 pass today and
  all 5 are one file-addition away from being false — exactly REQ-CLI-006's history, which drifted
  three times inside a single plan. **This plan produced a live specimen of the same class during
  drafting** (D-13 said 67 issues while the parsed value was 68); cite it.
  - depends-on: 7.2
  - resolves-upstream: #135 (partial)
- Issue 7.4: Make the 13 runnable clauses actually execute — a runner plus a `CHANGE-VALIDATION.md`
  row.
  - depends-on: 7.3
- Issue 7.5: A `Verification:` **grammar linter** for the remaining 213 prose clauses — generalizing
  `test_cli_enumeration.py:188-204`, which already encodes this rule by hand for **1 REQ of 736**.
  - depends-on: 7.4
  - resolves-upstream: #62 (partial)
- Issue 7.6: Record the scope bound honestly: **265 of 312 testable requirements (85%) sit under no
  executing gate**, because `coverage.rs:182` parses `../SPEC.md` only. File it as a follow-on. **The
  #165 closing comment must state this bound explicitly** — SC17 promises no false clause, but only
  13 of 226 are executable, and closing without saying so would overclaim (review, Upstream
  Assessment).
  - depends-on: 7.5

### Epic 8: The normalizer (hash-neutral only)

- Issue 8.1: Implement the normalizer with the **fingerprint postcondition** (D-2 amended, contract
  pinned by Issue 0.6): recompute before and after every file, abort the whole run if any hash moves.
  - depends-on: 7.6
- Issue 8.2: Implement the **refusal predicate** — `complete` AND `stored == current` AND under a
  plans root, excluding `skills/**/fixtures/**`. **State the behaviour for the no-fingerprint branch
  explicitly** (review M4): measured `complete=46` with roughly half carrying a stored fingerprint (two independent
  sweeps returned 25 and 26 present, i.e. 21 and 20 absent — **derive the count at execution, do
  not transcribe it**), so `stored == current` is False for that population and `stored == current` is False for them. The
  drafted plan called the predicate "inert on today's corpus", which was true only of the first
  conjunct.
  - depends-on: 8.1
- Issue 8.3: **Line-count preservation, over a DERIVED protected set** (D-2a, review M10). Compute
  the cited-plan set at execution from a committed script and print it; do not hardcode 17.
  - depends-on: 8.2
- Issue 8.4: **The `--idem-check` mode as an acceptance criterion, not a manual step.** EXP-002 hit
  three real non-idempotence defects — a transform re-prefixing its own output, a grammar that could
  not re-parse its own canonical form, and an ordering bug (T3 must precede T1).
  - depends-on: 8.3
- Issue 8.5: **Ship the orphan detector as a gate.** The letter→numeric epic rewrite leaves 14
  dangling references in forms the rewrite does not reach (`B/D`, `Epics A–F`, `E and F`, `B.1–B.3`),
  producing self-contradictory documents the normalizer cannot see. 13 of 14 are in plan-012.
  - depends-on: 8.4
- Issue 8.6: **Exclude the phase-log / `log.md` region from doc-wide id rewriting.** Rewriting
  plan-012's log line makes a dated record of what the operator said **false**.
  - depends-on: 8.5
- Issue 8.7: Report-only run over all 46 completed plans; render the aggregate report.
  - depends-on: 8.6
- Issue 8.8a: Generate the hash-neutral write diff and render it to `assets/normalizer-aggregate.diff`.
  **Ungated.**
  - depends-on: 8.7
- Issue 8.8b: Apply and commit as **one commit** plus a `.git-blame-ignore-revs` entry.
  - depends-on: 8.8a
- Issue 8.8c: **The rollback path** (review, Missing #3). Record the exact revert command before
  8.8b lands, and define the abort criterion: if 8.5's orphan detector or 8.4's idem-check reports a
  miss *after* 8.8b, revert the single commit rather than patching forward.
  - depends-on: 8.8b
- Issue 8.9: File the **hash-changing sweep** as a follow-on issue with citation repair as its stated
  prerequisite, rather than leaving it as an unrecorded gap.
  - depends-on: 8.8c

### Epic 9: Bind the remaining enforcement points

- Issue 9.1: Append linter findings inside `_audit_plan` (`plan_manager.py:3871`) as an additional
  finding after the existing checks. `ready-check`'s exit-3 and `audit`'s exit-1 then work unchanged
  — **zero call-site edits**, verified by the red-team — and `audit-close` stays advisory by
  construction. (The drafted text said "after check #9"; the docstring enumerates (1)–(8) — review L2.)
  - depends-on: 8.9
- Issue 9.2: Wire the always-on on-edit trigger as a companion rule, with the four mechanisms that
  make "no opt-out" honest rather than hostile: path-keying (4.3), severity tiers (4.1),
  status-awareness (4.2), and the `references/**` structural exclusion (2.4).
  - depends-on: 9.1
- Issue 9.3: Verify the three binding points fire independently, each with a positive control.
  - depends-on: 9.2

### Epic 10: Reconcile and land

- Issue 10.0: **Split-proposal renderer (D-13).** Emit `{tripped, review_cycles}` and **exit non-zero
  when tripped** — `ls reviews/pass-*.md | wc -l` ≥ 4 at the end of Epic 5. On trip, render the split
  proposal (remaining epics, their beads, a draft follow-on objective) and halt for the operator.
  Travels with the Epics-0–5 half if the split fires.
  - depends-on: 5.5
- Issue 10.1: Run FULL validation over the merged tree; record the result.
  - depends-on: 9.3
- Issue 10.2: Re-run the pour-fidelity comparator and record the post-work number as the **three-way
  decomposition** 5.3 emits, against the baseline (17/43 dirty; 20 invented; 2 dropped among joinable
  plans; 3 plans with no mapping).
  - depends-on: 10.1
- Issue 10.3: Draft the upstream comments — the coarse tracker plus #113, #174, #165, #125, #149,
  #135, #62 — into `references/comment-*.md`.
  - depends-on: 10.2
- Issue 10.4: Post the upstream comments and reconcile dispositions.
  - depends-on: 10.3
- Issue 10.5: **Close the coarse tracker** and confirm `stamp-tracker` recorded an `external_ref` on
  the epic. Without the tracker row, `stamp-tracker` returns `skipped` and the epic is structurally
  invisible to `upstream.py closable` — the failure #131 exists to prevent and the mechanism by which
  five trackers went stale (review M2).
  - depends-on: 10.4
- Issue 10.6: Deploy (`yf self install --from-build --build`) and verify `yf --version` matches HEAD.
  - depends-on: 10.5

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: doclint row executes and fail-closes
- Type: auto
- Condition: the FAST tier executes a non-empty command list containing `doclint` for a
  `docs/plans/**` path — which today matches no §3 glob and returns zero commands — and the linter
  sets a non-zero exit code on an error-severity finding.
- Test: `set -o pipefail; bash docs/plans/plan-047-james-dixson-dec9ff/scripts/gate-doclint.sh | jq -e '.commands | length > 0 and (.[0].output_tail | length > 0)'`
- Blocks: 4.1, 4.2, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10
- Instructions: satisfied by completing **Epic 3** (the gate wiring), which itself requires Epic 1's
  minimal engine. The script asserts on command presence and non-empty `output_tail`, **never** on
  `status == "pass"`, and reads `d["commands"]` — the drafted version read a `layer_b` key that does
  not exist in this repo and would have failed post-work too.

### Capability Gate: carve-outs detectable
- Type: auto
- Condition: the linter reports zero findings inside **all four** carved regions (87 fixture files,
  6 vendored `.md` files plus 3 non-md sidecars, 17 test fixtures, the `references/**` tree), **and** a positive control run with
  the globs disabled exits 1.
- Test: `set -o pipefail; bash docs/plans/plan-047-james-dixson-dec9ff/scripts/gate-carveouts.sh | jq -e '.carved_findings == 0 and .control_fired == true'`
- Blocks: 9.1, 9.2, 9.3
- Instructions: satisfied by completing Epic 2. The positive control is an **executed step of the
  script**, not prose in the Condition — the drafted version tested 2 of 3 regions and ran no
  control, reproducing the Condition/Test divergence Issue 3.5 exists to prevent.

### Capability Gate: normalizer aggregate diff
- Type: human
- Approvers: operator
- Condition: the operator has reviewed the aggregate hash-neutral diff across the eligible completed
  plans and authorized applying it.
- Test: `set -o pipefail; bash docs/plans/plan-047-james-dixson-dec9ff/scripts/gate-normalizer.sh | jq -e '.diff_bytes > 0 and .fingerprints_moved == 0'`
- Blocks: 8.8b
- Instructions: Issue 8.8a renders the aggregate to `assets/normalizer-aggregate.diff`. Review it as
  one diff, not 46. **The Test is a precondition, not a substitute for authorization** — it proves the
  diff exists and that `fingerprints_moved == 0` (a key pinned by Issue 0.6); only the operator can
  authorize applying it. Both must hold.

### Capability Gate: Upstream write
- Type: human
- Approvers: operator
- Condition: the operator has read the drafted comments and authorized posting them.
- Test: `set -o pipefail; bash docs/plans/plan-047-james-dixson-dec9ff/scripts/gate-upstream.sh | jq -e '.comments >= 8 and .auth == true'`
- Blocks: 10.4
- Instructions: the script asserts `gh auth status` and that the `comment-*.md` count is at least 8
  — the coarse tracker plus the 7 non-exclude upstream rows — and emits `{"comments": N, "auth":
  bool}` so a stubbed script is INCONCLUSIVE rather than PASS. Authored by Issue 1.4. The drafted
  Test asserted only that *some* `comment-*.md` existed and was therefore **already green** before
  any work (review M7); the version before that was inline and quoted, the `printf` → `jq --arg` →
  `bd create --metadata` hazard (review M11).

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Scope at completion — Epics 6–10 DESCOPED (operator SPLIT decision, 2026-08-19)

**D-13 fired as designed.** Issue 10.0's trip condition (`ls reviews/pass-*.md | wc -l` >= 4 at
the end of Epic 5) was met at 4 cycles; the gate exited non-zero and halted for the operator,
who chose **SPLIT (option 1)**.

**This plan's delivered scope is Epics 0–5 plus Issue 10.0** — 40 of 78 issues. Epics 6–10 are
**descoped, not abandoned**: all 39 remaining issues were closed with an explicit descope
reason (`bd batch`, one transaction) rather than left silently open, so no stale container
pollutes `bd ready` and the plan is internally consistent at completion.

| | Epics | Issues | State |
| :-- | :-- | --: | :-- |
| Delivered | 0, 1, 2, 3, 4, 5 + Issue 10.0 | 40 | closed, merged |
| Descoped to a follow-on | 6, 7, 8, 9, 10 (less 10.0) | 38 | closed with a descope reason |

**Gates:** the two `auto` capability gates (`doclint row executes and fail-closes`,
`carve-outs detectable`) are **resolved**. The two `human` gates (`normalizer aggregate diff`,
`Upstream write`) remain unresolved and correctly RED — the artefacts they gate belong to the
descoped half and do not exist.

**The follow-on must NOT copy the descoped epics verbatim.** Epic 5 refuted a measurement they
were planned against: the EXP-003 baseline's **20 invented edges were a parser artifact** —
splitting `invented` by whether the document is readable gives **0** invented edges in any
cleanly-parsed plan, with all 127 in documents the REQ-DATA-019 grammar cannot read. EXP-003-era
figures therefore no longer size Epic 8's normalizer worklist. The honest worklist is the
extractor's **300 unparsed constructs across 33 plans**, a number that did not exist when
Epics 6–10 were drafted. The follow-on needs its own investigation phase against corrected
numbers. See [assets/split-proposal.md](assets/split-proposal.md).

**Dispositions at completion (post-split, 2026-08-19).** Epics 6–10 were descoped, so the rows
whose `Resolved By` sat in Epic 7 are marked **deferred** rather than claimed. Comments are
drafted to `references/comment-*.md` and **not posted** — the `Upstream write` gate is human and
its Test is a precondition, never authorization.

| Issue | Claimed at completion | Where |
| :-- | :-- | :-- |
| #125 | **CLOSABLE** — the only `include` fully delivered (Issues 2.5/2.6, REQ-DATA-028, REQ-CLI-024) | Epic 2 |
| #113 | partial — the extractor substrate landed; the DAG walk itself stays open | Epic 5 |
| #174 | partial — criterion ids + `Discharged-by` + the extractor landed; both checks stay open | Epics 0, 5 |
| #149 | partial — M9 addressed; M5 confirmed and given a concrete proposed remediation | Epics 0–5 |
| #165 | **deferred** — Issue 7.2 was descoped; nothing claimed | Epic 7 (descoped) |
| #135 | **deferred** — Issue 7.3 was descoped; nothing claimed | Epic 7 (descoped) |
| #62 | **deferred** — Issue 7.5 was descoped; the general engine landed, the spec linter did not | Epic 7 (descoped) |
| #175 | tracker — stays **OPEN** for the follow-on | — |

**Success criteria:** SC0–SC19 and SC36 are discharged by the delivered scope. SC20–SC35 and
SC37–SC40 belong to the descoped epics and travel with them; they are **not** claimed here.

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The plan is the largest to date** — 11 epics / 77 issues, vs plan-045's 46 (1.7×) — and may exhaust its review budget or its executor's context | high | **D-13** declares Epic 5 the split point with a **mechanical** trip condition; **Issue 10.0** emits it and exits non-zero when tripped |
| R2 | The linter is derived from a **drifted** SKILL.md template | high | D-7 amended / Issue 0.1 fixes it first; Issue 0.2 generates the shared region through `_shared/sync.py`'s marker fence so it cannot drift again |
| R3 | The always-on on-edit trigger errors on 72% of the existing corpus | high | Issue 4.2's status-aware promotion makes `complete` plans report-only. **Note the corrected scope**: this was never an INTAKE hazard — no path re-audits a complete plan (D-9 amended) |
| R4 | A normalizer transform silently changes **meaning** — EXP-002 found three classes, including rewriting a dated phase-log record | high | Issues 8.5 (orphan detector as a gate), 8.6 (exclude the log region), 8.4's `--idem-check`, and 8.8c's revert criterion |
| R5 | The `doclint` row is **decorative** — zero commands (#164 class) or zero exit code (#149 class). Both reproduced live, and the drafted gate Test itself was broken a third way (#H1) | high | Issue 1.3 proves the exit code; Issue 3.5 falsifies by execution; Issue 3.4 makes the Test a committed script rather than an inline one-liner |
| R6 | Normalizing shifts line numbers, breaking citations and review quotes | med | D-2a / Issue 8.3 derives the protected set at execution and restricts it to `rstrip`-only |
| R7 | The `Blocks:` grammar is **legislated, not observed** — only 12 of 72 values parse today | med | Issue 0.4 states it as an addition and scopes `epic:<N>` to future plans; **this plan's own gates use explicit issue-id lists**, the only form the pour handles |
| R8 | `discharged-by` starts empty, so **#174's matrix has almost no input** for a long time | med | D-5 accepts this deliberately. Inferred edges measured at ~73% precision (n=11) on 13% coverage would be worse than none |
| R9 | The refusal predicate is inert or undefined on parts of the corpus | med | Issue 8.2 states the no-fingerprint behaviour explicitly; SC28 exercises all three branches |
| R10 | The new override flag's semantics collide with the three **prose** `--force` overrides in SKILL.md's deviation table | med | Issue 2.6 decides the name **before** 2.5 implements it (the drafted DAG had this backwards) |
| R11 | The engine over ~15 types is slower than the 0.18 s prototype | low | Three orders of magnitude of headroom; re-measure at Issue 4.5 |
| R12 | **This plan lost its own Epics section to a bad string edit during drafting** and was rebuilt from source | low | The bundle is backed up at every drafting checkpoint, and committed once the operator authorizes it |
| R13 | Epic 0 edits the **SKILL.md this session is executing under**, so mid-run verification reads the installed copy and sees no change | low | Issue 0.1 states the read-back rule inline. The `plan_manager.py` edits are genuinely safe — the repo `skills/` tree matches none of the resolver's six roots |

## Success Criteria

Every issue is discharged by at least one criterion. That bidirectional completeness is the linter
rule this plan proposes (Issue 0.3), so the plan is held to it first — and at pass 1 the draft
satisfied it only in form, with ten Epic-6 issues covered by one criterion satisfiable by ten empty
files. The fix was **not** to split that criterion per issue but to make it non-vacuous: Issue 6.0
commits one malformed fixture per schema-bearing type, so SC20 is discharged eight separate times
against eight committed artifacts.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | The free-id list is published before any `REQ-DATA-*` id is written | `assets/req-data-ids.txt` exists and its `free` set contains every id Epic 0 allocates; the issue has no predecessors | 0.0a |
| SC1 | The investigation's instruments are in the bundle and re-runnable | `assets/extract_plan.py` and `assets/pour_fidelity.py` exist; the recorded invocation reproduces the baseline | 0.0 |
| SC2 | The `SKILL.md` plan.md-structure block teaches no retired construct | no `**Phase log:**` in the block; a frontmatter block is present; `(if needed)` and `(when upstream issues incorporated)` are gone | 0.1 |
| SC3 | The shared region cannot drift from `seed_plan_md` again | `_shared/sync.py --check` fails when either side is edited alone; the illustrative grammar block survives outside the fence | 0.2 |
| SC4 | All seven new `REQ-DATA-*` ids (**018, 019, 024–028**) are allocated, unique, non-dangling, and cited by their implementing issue | `grep -rhoE 'REQ-DATA-[0-9]+' skills/ \| sort -u` shows each new id exactly once and no pre-existing id redefined; each is cited by its implementing issue. **Not** `cargo test` — `coverage.rs:182` reads the root SPEC only | 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9a, 0.9b, 0.9 |
| SC5 | The schema format expresses both producer classes | one `derive_from` type and one inline-declared type both lint | 1.1 |
| SC6 | The linter exits 1 on an error-severity finding and 0 otherwise | seeded known-bad fixture yields exit 1; a clean file yields 0 | 1.2, 1.3 |
| SC7 | Every vendored file carries `source:` + `retrieved:` frontmatter | all 6 vendored `references/` files match; 0 unmarked | 2.1 |
| SC8 | Zero linter findings inside all four carved regions, with a positive control | the Epic-2 gate script exits 0, and exits 1 with the globs disabled | 2.2, 2.3, 2.4 |
| SC9 | `update-status approved` is refused when `ready-check` is red | driving the real verbs on a non-conformant plan yields non-zero; the override path logs a deviation under the name 2.6 chose | 2.5, 2.6 |
| SC9b | The `approved` transition and the review-count invariant have SPEC coverage before their implementations land | `REQ-DATA-028` and the REQ-PORT-006 amendment exist and are cited by Issues 2.5 and 2.7 | 0.9a, 0.9b |
| SC9c | A `review:` status transition followed by a red-team pass no longer fails the audit | reproduce the two-lines/one-file state and confirm `_audit_plan` passes; a genuinely missing pass file still fails | 2.7 |
| SC9d | Each gate script fails RED pre-work for the reason it claims, and a stub cannot satisfy the gate | `assets/gate-prework/` holds each **gate `Test:` string's** pre-work exit code and stderr tail (not the bare script's — the pipeline is what runs); **and** replacing any script with an empty file makes its gate `Test:` exit non-zero, because the `jq -e` assertion is in the Test, not in the script (the resolver is exit-code only); **and** each script distinguishes exit 1 (capability absent) from exit 2 (harness could not run) under `set -o pipefail` | 1.4 |
| SC10 | A `docs/plans/**` edit executes `doclint` in the FAST tier with non-empty output | the Epic-3 gate script exits 0; it exits 1 on the pre-work tree | 3.1, 3.2, 3.5 |
| SC11 | The `skills/*/SPEC.md` → `uv-herdr-launch` mis-mapping (#164) is gone | no §3 row maps a skill SPEC.md to `uv-herdr-launch` | 3.3 |
| SC12 | Every gate `Test:` is a bare script invocation, not an inline one-liner | each of the four named scripts exists, is executable, and its gate `Test:` pipes it through `jq -e` | 1.4 |
| SC13 | The gate is proven to fail-close, not merely to be green | an injected mutant makes FAST report `status: fail` with `doclint` as `first_failure`; the mutant is reverted | 3.4 |
| SC14 | A freshly `init`'d plan lints with **zero errors** at every pre-`review` status, and a `complete` plan never errors | `doc_lint.py` on a fresh `init` reports `errors=0`; on a completed plan reports report-only | 4.1, 4.2 |
| SC15 | The trigger is path-keyed and inert where it should be | the 17 fixture `plan.md` files produce 0 findings; a repo with no `docs/plans/` produces 0 | 4.3 |
| SC16 | The verdict vocabulary is three-valued with a binary exit contract | `INCONCLUSIVE` maps to exit 2 and only to "the linter could not run"; warnings never change the exit code | 4.4, 4.5 |
| SC17 | `extract` handles every plan in the corpus or reports `unparsed` — never degrades silently | `extract` over all 46 completed plans plus this one emits no silent partial parse; each `unparsed` item is enumerated | 5.1, 5.2 |
| SC18 | The comparator reports the three populations separately and its positive control passes in CI | output carries no-mapping / dropped / invented as distinct counts; deleting an issue line, a `depends-on`, and a gate block each make it fail | 5.3, 5.4 |
| SC19 | The pour records `plan_issue` metadata and the comparator is a close gate | a fresh pour writes `plan_issue`; the comparator runs at close and can fail it | 5.5 |
| SC20 | Every schema-bearing type rejects its committed malformed fixture | for each of the **8 schema-bearing types** (Issues 6.1–6.8), a deliberately malformed instance of that type produces ≥1 error-severity finding. **An empty schema fails this** | 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8 |
| SC21 | The 30 legacy `README.md` bundles carry an `index.md` | `okf.py reindex` reports 0 `no-index` bundles | 6.9 |
| SC22 | The deferred one-off types are filed, not implicit | a follow-on issue names `DECISION.md` / `decisions/*` / `REDEPLOY-HANDOFF.md` | 6.10 |
| SC23 | All 226 `Verification:` clauses are classified, including the 4 left unbucketed | the classification totals 226, not 222 | 7.1 |
| SC24 | No `Verification:` clause in the spec family is false when executed **from the repo root** | the 13 runnable clauses all exit 0 from repo root, including the 2 previously cwd-dependent | 7.2, 7.4 |
| SC25 | No `Verification:` clause asserts a hand-maintained count | the 5 identified counts are restated as self-consistency assertions; the grammar linter covers the rest | 7.3, 7.5 |
| SC26 | The 85% ungated-testable-REQ bound is recorded in the #165 comment, not silently left | the filed follow-on names `coverage.rs`'s root-SPEC-only scope, and the closing comment states the bound | 7.6 |
| SC27 | The normalizer moves **no** content fingerprint | before/after hashes equal for every file it writes; the run aborts if any moves | 8.1, 8.7, 8.8a, 8.8b |
| SC28 | The refusal predicate is exercised on **all three** branches | `complete`+fresh-fingerprint, `complete`+**no** fingerprint (~20 of 46 real plans, derived at run time), and non-`complete` each produce the stated behaviour | 8.2 |
| SC29 | The protected set is derived, printed, and line-count preserved | the script prints its set; `wc -l` is equal before/after for every plan in it; a spot-check of 5 citations still resolves | 8.3 |
| SC30 | The normalizer is idempotent | `--idem-check` reports zero non-idempotent plans | 8.4 |
| SC31 | No orphaned epic reference survives, and no phase-log line is rewritten | the orphan detector reports 0; `log.md` and phase-log regions are byte-identical before/after | 8.5, 8.6 |
| SC32 | The corpus rewrite is revertible by one command, with a stated abort criterion | the revert command is recorded before the write lands and is executed once against a scratch clone | 8.8c |
| SC33 | The deferred hash-changing sweep is filed with its prerequisite stated | the follow-on issue exists and names citation repair | 8.9 |
| SC34 | The INTAKE binding needs no call-site edits and fails closed | a non-conformant plan makes `ready-check` exit 3 and `audit` exit 1, with no edit outside `_audit_plan` | 9.1 |
| SC35 | All three binding points fire independently, each with a positive control | Issue 9.3's recorded runs; the on-edit rule is installed and fires on a `docs/plans/**` edit | 9.2, 9.3 |
| SC36 | The split trip condition is mechanical and has an exit code | Issue 10.0's command emits `{tripped, review_cycles}` and exits non-zero when tripped; verified by forcing the condition in a scratch copy | 10.0 |
| SC37 | The post-work pour-fidelity number is recorded as a three-way decomposition against the baseline | FULL tier green; comparator output committed to `findings/exec-*` reporting no-mapping / dropped / invented separately | 10.1, 10.2 |
| SC38 | Every upstream disposition is discharged as its row states | `verify-reconcile` passes; the 5 `partial` issues remain OPEN; the 2 `include` issues are CLOSED | 10.3, 10.4 |
| SC39 | The coarse tracker exists, is stamped, and is closed | `stamp-tracker` returns a recorded `external_ref` on the epic rather than `skipped`; the tracker issue is closed | 10.5 |
| SC40 | The deploy is verified, not assumed | `yf --version` git hash equals HEAD **recorded as a before/after pair around Epic 10's commits** — the equality holds today (`7fc38d0`), so only the post-commit measurement is informative | 10.6 |

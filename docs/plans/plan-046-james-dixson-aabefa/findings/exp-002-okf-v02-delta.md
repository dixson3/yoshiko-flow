---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-okf-v02-delta
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exp-002 — The v0.1→v0.2 delta, and where v0.2 meets yf's private vocabulary

**Question:** What changed v0.1 → v0.2, and where does v0.2's vocabulary agree with — or diverge from — concepts yoshiko-flow already implemented privately?
**Method:** read the vendored v0.2 spec (1016 lines), the repo's v0.1 baseline and extensions layer; verified §13's self-declared changelog against v0.2 body text **and** against three independent in-repo copies of v0.1's verbatim clauses; measured the corpus with a YAML frontmatter walker; ran the credibility scorer and the conformance engine; traced every frontmatter read site in code. Read-only.

## Headline — the repo's exposure to both breaking changes is exactly ZERO

```
timestamp:  0 emissions      # Citations:  0 emissions
```

Not because migration was deferred — because **yf independently declined both v0.1 features long before v0.2 retired them.** `OKF-BASELINE.md` L171 declared `# Citations` an explicit non-goal; yf uses `created` + `fingerprint` where v0.1 had `timestamp`. The two v0.1 features yf refused are the two v0.1 features v0.2 dropped.

> D-2 survives, and for a **stronger** reason than the plan states: the baseline rewrite is a documentation edit plus a version constant, not a migration.

## 1. The delta — §13 is accurate but INCOMPLETE

### Breaking: 2 declared, **1 undeclared**

**B-1 `timestamp` → `generated: {by, at}`** (§13.1). Wrong-after: `OKF-BASELINE.md` **L141** (the `timestamp` table row); **L129–132** (the quoted `ga4` concept, still a true quote of a v0.1 artifact but no longer an exemplar).

**B-2 body `# Citations` → `sources` frontmatter** (§13.1). v0.2's §4.2 heading table **removes** the `# Citations` row and **adds** `# Computation`; v0.2 has no citations section at all. Wrong-after: **L167**, and the whole **L171–178** non-goal paragraph — whose *decision* is now vindicated for a different reason, but whose *premise* ("OKF's `# Citations` heading is SHOULD-level") is false.

**B-3 — UNDECLARED. `SHOULD NOT` → `MUST NOT` on the extension clause.**

v0.1 (three independent in-repo copies agree — `OKF-BASELINE.md:149-151`, `sources.md:46`, `Summary.md:154`):

> Consumers SHOULD preserve unknown keys when round-tripping and **SHOULD NOT** reject documents with unrecognized fields.

v0.2 §4.1 (lines 218–220):

> Consumers SHOULD preserve unknown keys when round-tripping and **MUST NOT** reject documents with unrecognized fields.

Wrong-after: **L149–151** and **L157–160** (the "caveat carried from research 001" paragraph, which reasons from the weaker force). **This is good news for yf** — it hardens the exact hook `okf_spec`/`id`/`epic`/`fingerprint` ride on. Preservation is still only SHOULD; **rejection is now forbidden.**

### Clarifying — two that matter

**Every section number moved.** index `§6→§8`, log `§7→§9`, conformance `§9→§11`, versioning `§5→§12`. **Every `(§N)` citation in `OKF-BASELINE.md` §3/§4/§5/§6/§7/§7a is now a wrong pointer.**

**§11 conformance is byte-for-byte the same three MUSTs** — only cross-references moved. **B1/B2/B3 in `OKF-BASELINE.md` §2 survive unchanged.** This is the single most important *non*-change.

**§9 now specifies the log format** — *"a flat list of date-grouped entries, **newest first**"*, ISO-8601 date headings (MUST). `OKF-BASELINE.md` §4, §7a bullet 1, and `OKF-YF-EXTENSIONS.md` §3 all currently claim OKF is silent here. **They are now wrong, and yf guessed right.**

## 2. The two named breaking changes

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
```

`generated.by` is REQUIRED within `generated`; `.at` marks *last meaningful change*. §7's actor convention has three forms — `<producer>/<version>`, `human:<id>`, `process:<id>` — and a **MUST**:

> Consumers that classify trust (§5.3) key off the `human:` prefix, so producers **MUST** use it for hand-authored or human-confirmed content.

That MUST is load-bearing: §5.3 derives the trust tier purely from the prefix. **A bare `james-dixson` — exactly what the repo emits — silently lands in the machine-confirmed tier.**

```yaml
sources:
  - id: ga4-schema
    resource: https://…            # REQUIRED within an entry
    author: team:ga4-docs          # actor convention
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

And the sentence that collides with this repo:

> OKF records objective, per-source signals so a consumer can judge how much to trust a concept… **It does not store a credibility score: a score is subjective, unportable across consumers, and goes stale.**

## 3. The mapping — four axes

### 3a. `sources` ↔ yf-research's credibility scorer — **same problem, opposite answers**

`credibility_scorer.py` is a 278-line weighted scorer: `overall = da*0.35 + cu*0.20 + ex*0.25 + bi*0.20`, bucketed `high_trust ≥80 / verify ≥60 / questionable ≥40 / avoid`. **#147 reproduced exactly** — `github.com` and a fabricated internal wiki both return `domain_authority: 30`, the unknown-domain fallback at `:93`.

The stored shape has **already drifted** across 317 source records:

```
credibility=317, credibility_score=173, credibility_category/reason/rubric=136
credibility sub-keys: overall=117, category=117, domain_authority=74, … basis=27
```

Only 74 of 317 carry the four-factor breakdown. And `research/001/sources.md` opens with a **hand-written retraction of its own score**:

> **Read the `category` as the trust signal and disregard the numeric `overall`.** … the 41 is an internally-consistent score of the *wrong inputs*… The `category` is a **manual override applied on domain-authority grounds, not recomputed from the rubric formula**

| Axis | v0.2 | yf-research | |
| :-- | :-- | :-- | :-- |
| Where | per-concept frontmatter | `sources.md` + `sources.json` sidecars | **DIVERGE** (structural) |
| Stored value | **signals only** | `overall` 0–100 **and** a `category` verdict | **DIVERGE** (head-on) |
| `author` | identity | `expertise` enum — an inferred tier | **DIVERGE** |
| `last_modified` | when the **source** changed | absent (`retrieved` = when *we* fetched) | **ABSENT** |
| `usage_count`/`usage_window` | adoption signal | absent | **ABSENT** |
| — | absent | `domain_authority`, `bias_neutrality` | **yf-only** |
| Per-claim attribution | footnote `[^id]` | GFM `[S1](sources.md#s1)` | **AGREE** — both stable-keyed |

> **The disagreement favors v0.2.** yf's most careful research bundle had to hand-write an instruction to ignore its own stored number. That is precisely the failure §5.1 predicts. **#147 is the stored-score design failing in the documented way, not an isolated heuristic bug** — so do **not** propose renaming `credibility.overall` to something v0.2-shaped. v0.2's position is that the field should not exist.

### 3b. `verified[]`/`status`/`stale_after` ↔ verdicts + the Fingerprint gate

| v0.2 | yf-plan | |
| :-- | :-- | :-- |
| `verified: [{by, at}]` | `pass-N.md` `verdict:` (7 APPROVE / 11 REVISE corpus-wide) | **DIVERGE** — same intent, different carrier |
| `verified[].by` = actor | **absent** — no review file records who reviewed | **ABSENT** |
| `stale_after` = absolute date | `fingerprint:` SHA-256; stale iff `stored != recomputed` | **DIVERGE — yf's is strictly stronger** |
| `status: draft\|stable\|deprecated` | workflow state machine | **HARD COLLISION** |

**The `status` collision, measured:**

```
22 complete   17 resolved   4 incubating   2 draft   1 investigating
```

Overlap with v0.2's vocabulary: **`draft` only, 2 of 46.** And `status` carries a *third* meaning in yf-research (`OKF-EXTENSION.md:67` — pipeline phase). One key, three incompatible vocabularies. `OKF-YF-EXTENSIONS.md` **L37** lists `status` under *Owner: yf* — v0.2 takes that key into the baseline, so **that row becomes wrong.** It is the only case in the whole delta where v0.2 claims a key yf already occupies.

**And it is read at a gate** — `plan_manager.py:2152`:

```python
return status == "approved" and bool(stored) and stored == current
```

`"approved"` is not in v0.2's vocabulary.

**The `stale_after` divergence is the more interesting one.** v0.2 answers "is it still true?" with a **self-reported absolute date** — advisory, guessed at write time, blind to whether content changed. yf answers it with a **content hash over the reviewed span**. Neither subsumes the other: `stale_after` catches *"the world moved on"*; the fingerprint catches *"the document moved on"*. A v0.2-native reader gets **no** staleness signal from a yf plan, because `fingerprint` is an unrecognized producer key.

### 3c. `generated.by` ↔ provenance — **a clean absence**

```
$ grep -rh "^author:" --include='*.md' docs/ | sort | uniq -c
  18 author: james-dixson
```

The only identity in the corpus, on `plan.md` only — the *human who scoped the plan*. The artifacts actually agent-written (50 Findings, 47 Reviews, 25 Research Artifacts) carry **no producer identity of any kind**. Zero agent names or model versions anywhere. Nor a `generated.at` equivalent: `created` (73) is creation, not last-change.

**AGREE in problem, ABSENT in solution** — the one family with nothing to reconcile. Note that under §7's MUST, the bare `james-dixson` form classifies as **machine-confirmed**: the corpus would read as *less* human-reviewed than it is.

### 3d. `Attested Computation` ↔ yf-change-validation + `- validated:`

| v0.2 §10 | yoshiko-flow | |
| :-- | :-- | :-- |
| computation is its own concept | recipe rows in one repo-wide `CHANGE-VALIDATION.md` | **DIVERGE** (granularity) |
| `runtime` REQUIRED, typed `parameters` | shell command strings | **DIVERGE** |
| `executor.receipt` | none — engine returns PASS/FAIL/INCONCLUSIVE | **ABSENT** |
| `attester.resource` = deterministic no-LLM | the exit code **is** the verdict | **AGREE in spirit** |
| receipt NOT stored in bundle (§10.5/§10.6) | `- validated: <run URL> — <note>` in `log.md`, gating a status transition | **AGREE, and yf went further** |

```
$ grep -rn "^- validated:" --include='*.md' docs/ | wc -l
       2
```

> **yf is ahead of the spec here, not behind it.** §12 lists *"receipt and verdict wire formats"* as deliberately deferred future work — and yf's `attest-validation` verb writes a durable, gate-enforcing one today. Mapping yf's bullet onto v0.2 vocabulary would mean **discarding the persistence and gaining nothing.**

## 4. What the repo emits

672 `.md` scanned, 341 with frontmatter. No `Incubator/` exists.

| Key | Count | Classification |
| :-- | --: | :-- |
| `type` | 314 | **OKF-reserved** (the one MUST) |
| `okf_spec` | 314 | yf extension |
| `created` | 73 | yf ext. (**no** v0.2 equivalent — `generated.at` is *last change*) |
| `id` | 64 | yf ext. (v0.2 uses `id` only inside `sources[]`) |
| `status` | 42 | **COLLISION** |
| `okf_version` | 25 | **OKF-reserved** — must become `0.2` |
| `verdict` / `fingerprint` / `epic` | 18 / 16 / 16 | yf ext. |
| `title` / `tags` / `description` | 11 / 10 / 1 | OKF-recommended, unchanged |

```
generated=0  verified=0*  stale_after=0  sources=0  usage_window=0
runtime=0  attester=0  executor=0  parameters=0  computation=0  timestamp=0
# Citations headings: 0   (the 1 hit is inside v0.2's own Appendix-A v0.1 example)
```

*(the single `verified` grep hit is prose: "verified: it is entirely about…")*

**One pre-existing drift, unrelated to v0.2:** 4 concept documents carry `okf_version`, which both v0.1 §5 and v0.2 §12 reserve for a bundle-root `index.md`.

## 5. Is D-2 coherent? — Yes, with TWO carve-outs it does not name

**`okf_version` is write-only in the engine.** All occurrences across all five copies are the constant or a write (`:48`, `:320`, `:344`, `:356`). **No comparison, no gate, no branch on the value anywhere in production code** — so `0.1` and `0.2` coexisting cannot break runtime behavior. The no-migration half of D-2 is safe.

**Three test lines hard-code it and will break** — the complete blast list:

```
_shared/test_okf.py:504:                  assert okf.okf_version == "0.1"
skills/yf-plan/scripts/test_worktree.py:1179 / :1296   (fixtures — assert shape, not version)
```

### Carve-out 1 — `status` must NOT be adopted, even for new emissions

It is read at a gate with the literal `"approved"`, and carries three vocabularies. **Two spellings coexisting is not benign here, because the two spellings are two *vocabularies on the same key*.** Record it in `OKF-YF-EXTENSIONS.md` as an explicit, **permanent divergence** — yf retains the workflow vocabulary and declines §5.4.

Everything else is additive: the only other non-test frontmatter readers (`_read_plan_field`'s closed 7-key set, the audit's `type`/`okf_spec` presence checks, migrate, `incubator-index.py`) enumerate no unknown keys and reject on none.

### Carve-out 2 — §8 constrains D-3, and D-2 does not anticipate it

> Index files contain **no frontmatter**, with one exception: a bundle-root `index.md` MAY carry an `okf_version` key.

All 23 current `index.md` are bundle roots, so this is satisfied **by accident**. But `write_index`/`render_index` stamp `okf_version` **unconditionally** at three sites. **The moment D-3 generates a nested index, the engine violates §8 on the very first run.** A one-line predicate (`if bundle_root`) — but it must be found *before* a backfill, which is exactly the mechanism that turns a one-line defect into ~50 files.

*(Inferred, uncorroborated — the three unconditional write sites were read, but a nested bundle was not constructed and run. A five-minute experiment would upgrade this to measured.)*

## 6. Marking research 001 superseded — **no mechanism exists**

`grep -rni "supersede"` across `skills/` returns 16 hits, **all** the yf-plan upstream-*issue* disposition vocabulary acting on GitHub issues, not artifacts. Neither `yf-research` nor `yf-okf` can mark a bundle superseded; no status verb exists in either manager.

**001 is also the only unmigrated research bundle** — legacy `_index.md`, **no `log.md`**, and a `Summary.md` with **no frontmatter at all**. So it has no `type`, fails OKF B1/B2, and has nowhere to put a marker. The two jobs are entangled.

Three options, ascending: (1) append a prose note — free, but invisible to tooling and to a cold reader who opens `sources.md` first, *which is exactly how 001's `timestamp`/`# Citations` claims keep propagating*; (2) `okf.py migrate` then a dated `log.md` entry — idiomatic, **but that is a bundle migration D-2 excludes**; (3) a yf-owned **`superseded_by:`** producer key — sidesteps the `status` collision entirely, costs nothing at read time, and is precisely the extension v0.2 §4.1 now *requires* consumers to tolerate.

**`OKF-BASELINE.md` L210–212 cites 001 as its provenance**, so leaving it unmarked keeps v0.1 facts flowing into the layer being rewritten.

## Implications

1. **D-2 survives, for a stronger reason than stated** — zero exposure to both breaking changes.
2. **The baseline edit is larger than "swap two rows"** — L141, L167, L171–178, L149–151, L157–160, **plus every `(§N)` cross-reference**, plus three places that wrongly claim OKF is silent on log ordering.
3. **`status` needs a decision, not a mapping.**
4. **D-5 is vindicated hardest on the credibility axis** — any proposal to "align" the scorer by renaming fields would paper over the actual finding.
5. **D-3 acquires a hard prerequisite from §8.**
6. **D-6's stakes are concrete:** the baseline bump touches `okf_version` in five files and flips `test_okf.py:504` — a suite exp-001 measured as ungated. **The smallest possible change that proves the gate matters.**
7. **The mapping is genuinely bidirectional** — two v0.2 families have no yf counterpart (`generated.by`; `usage_count`/`last_modified`), and two yf mechanisms have no v0.2 counterpart (the fingerprint; the persisted receipt).

## Honest limits

- **No verbatim v0.1 SPEC exists in this repo.** The diff covers only the clauses research-001 captured verbatim (§3.1, §4, §4.1, §4.2, §5, §8, §9). **v0.1's §1, §2, §6, §7 bodies were never quoted, so further undeclared changes there cannot be ruled out.** §13.2's "everything else carried forward unchanged" is **partially unverified** — and one omission (§4.1's force upgrade) was found *within* the verified subset, which is mild evidence the claim is not exhaustive. Fetching v0.1 verbatim from a prior upstream commit would close this.
- **`change_validation.py run` was not executed** — the Attested-Computation mapping comes from the manifest schema and the two `- validated:` bullets, not an observed run.
- The §4 corpus table counts the vendored spec and quoted fixtures (~1–3 files per key); every claim that mattered was re-measured with the spec excluded.
- **The §8 nested-index prediction is inferred and uncorroborated** (see Carve-out 2).
- **No `Incubator/` exists**, so the incubator mapping rests on source reading, not a live corpus.
- **#147 was reproduced behaviorally**; the issue text itself was not read, so it cannot be confirmed to match what was observed.

---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-description-producer-contract
description: "The premise is half-wrong — agents hit 51/51 since plan-052 with no prompt; the code producers sit at 1%."
---

# Finding: Is a `description:` frontmatter producer contract mechanically enforceable, given that the files that need it are written by AGENTS, not by code?

### Approach Tested

Enumerated every write site in `plan_manager.py` / `plan_template.py` / `okf.py`. Re-measured the
corpus with `doc_lint.select()` itself rather than an ad-hoc glob, so rates are reported over exactly
the file set a schema check would reach. Three sandbox spikes: (A) added a `frontmatter-keys` check
for `description` at `W` to 12 nested types and ran the instrumented linter read-only over the live
corpus; (B) copied plan-055/056 to a sandbox, flipped `status:` to `ready-for-approval`, and re-ran —
the actual intake enforcement point; (C) patched `_stamp_okf_type` + `_write_upstream_reference` to
stamp a derived description and executed it. Extracted all 134 `description:` values and classified
them for informativeness, hand-adjudicating every flagged case.

### Result

**measured:** — THE PREMISE IS HALF-WRONG, and that is the finding. Of the 27 errors a `description`
check would raise at intake today, **27 are on code-generated types and 0 are on agent-written ones.**

**measured:** — the agent side already reached 100% four plans ago, with zero prompt instruction.
Since plan-052, **51 of 51** findings + reviews carry `description:`:

| bundle | findings n/d | reviews n/d |
| :-- | :-- | :-- |
| plan-050 | 6/0 | 13/0 |
| plan-051 | 5/**5** | 5/0 |
| plan-052 | 7/**7** | 6/**6** |
| plan-053 | 7/**7** | 5/**5** |
| plan-054 | 6/**6** | 6/**6** |
| plan-055 | 7/**7** | 7/**7** |

The 133/432 aggregate is dragged down by history (plans 45-50) and by 391 code-generated
`upstream-reference` files. **measured:** no prompt anywhere mentions `description:` — `captor.md:71`
names `type` + `okf_spec` only.

**measured:** — the code side is at 1%. `_stamp_okf_type` (plan_manager.py:536) is called from 5 sites
and writes `{"type", "okf_spec"}` and nothing else. `references/upstream-<N>.md` is the **only** code
producer of a *nested* bundle artifact. Rates: `upstream-reference` 4/391 (1%), `context` 0/56,
`upstream-triage` 0/38, `plan-retrospective` 0/11, `plan` 0/56.

**measured:** (spike A) — a `W` check added today is corpus-PASS. 1073 files, **E 0**, W 656, R 1822.
807 of 840 `description` findings are demoted to `R` by `STATUS_SEVERITY`'s `complete` profile.
History is structurally immune; no migration needed.

**measured:** (spike B) — at `ready-for-approval` the same check yields FAIL, E 27 — and every error is
a code-generated type. plan-055 scores **100% on all agent-written types** and would still hard-fail
intake purely on producer output. plan-056 would fail with 16 errors on files it did not write.

**measured — `research-*` types have `bundle_status = None`**, so `STATUS_SEVERITY` returns `{}`: a
`W` there is never promoted and never demoted. That is the one class where declared severity equals
effective severity, always.

**measured:** (spike C) — the producer patch is 6 lines (one optional kwarg, one call-site argument).
Executed output stamps `description: 'Upstream issue #999 - yf-plan: stamp description on generated
bundle artifacts'`; pyyaml quotes the `#`/`:` correctly and `frontmatter_keys()` parses the wrapped
continuation fine. The 4 hand-authored `upstream-*.md` descriptions already use exactly that shape.

**measured:** — QUALITY: the risk I flagged did NOT materialise. 134 files carry the key; 8 are copied
skill fixtures, leaving 126 authored. A token-novelty screen flagged 22 as thin; hand-adjudicating all
22, only **2 are true restatements**. **~120 of 126 (95%) are genuinely informative** — they carry a
verdict, count, or conclusion the filename cannot:

- `pass-5.md` -> *"Red-team pass 5 (fifth independent, CONFIRMING) — APPROVE; 9 of 10 reproduced (90%)"*
- `exp-006-orthogonality-injection.md` -> *"The orthogonality hypothesis is refuted. Artifact overlap is a 14-24x discriminator"*
- `comment-173.md` -> *"Drafted upstream comment for #173 (partial — stays OPEN)"* — disposition is not in the filename

**inferred:** findings/reviews descriptions systematically carry the *answer*, not the *question*.
A real convention, though no prompt asks for it.

**measured:** — derivability per code type: `upstream-<N>.md` -> `issue["title"]`, fully derivable and
informative (the filename is a bare number). `plan.md` -> objective, informative. `context.md` and
`plan-retrospective.md` -> static boilerplate, i.e. **67 identical strings**, a restatement.

**measured:** — two gaps:

- **`assets/**` is selected by NO schema at all.** 45 of the 126 authored descriptions live there,
  unreachable by any enforcement check.
- **`okf.render_index()` never reads `description:` from the linked file** — it builds bullets from
  `iterdir()`. **D-4 needs two changes, not one.**

**measured:** — the spec's own figure is stale. `OKF-YF-EXTENSIONS.md:389` and `SPEC.md:287` say
"0 of 423"; live is 76 of 805 selected (9.4%). Per D-5, re-measure rather than cite.

**measured:** — `frontmatter-keys` tests presence only. `description: ""` passes.

### Implications for Plan

**D-8 survives but must be re-aimed.** It was scoped as "convert emergent agent convention into a
contract". The measurement says the agent convention is already at 100% and self-sustaining; the
**unsolved half is the code producers**, which no amount of prompt work touches.

**Sequencing is forced.** Landing the schema check before the producer patch would hard-fail
plan-056's own intake on 16 errors in files it did not write. SPEC-first still holds for the `REQ-*`,
but the producer commit must precede the check's severity taking effect.

**The enforcement mechanism needs no new engine code** — `frontmatter-keys` exists, already ships at
`E` on `agent.toml`/`skill.toml`, and `STATUS_SEVERITY` grandfathers history automatically.

### Recommendations

1. **Patch the producer first** — 6 lines, spiked and executed. Same for `plan.md` and `upstream-triage.md`.
2. **Do NOT derive a description for `context.md` / `plan-retrospective.md`** — 67 identical strings is
   the restatement failure mode. Exclude those types, or accept a static string knowingly and say so.
3. **Declare the check `W`, not `E`.** `W` is corpus-PASS today and becomes the intake gate for free.
   `E` gains nothing and removes the drafting grace period. Exception: scope `research-*` out, or
   accept a permanent never-promoted warning.
4. **Pair `frontmatter-keys` with `regex-present` `^description:\s*\S`** — presence alone admits `""`.
5. **Change the prompts anyway, billed as a hit-rate lever, not enforcement.** Borrow the convention
   that already works: the description carries the **answer or verdict**, not the question.
6. **Decide `assets/**` deliberately** — add an `asset` type or state it is out of contract scope.
   Silently leaving it uncovered is the "asserting something nothing checks" class this work closes.

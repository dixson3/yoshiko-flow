---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: skill description cap trigger eval

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #407 — Five skill descriptions exceed the Agent Skills 1024-char cap — pi warns on every startup; cap is unenforced
Labels: priority::medium, type::bug
> Five skills ship a `description` frontmatter field longer than the Agent Skills spec's 1024-character cap. Harnesses that enforce the cap emit a startup warning for each one, on every session.

## Sym...

**Disposition:**
**Notes:**

## #332 — `assets/upstream-drafts/` is undocumented in every yf-plan `.md`
Labels: bug
> ## What

`_land_upstream_rows` expects per-issue draft bodies at:

```
<plan_dir>/assets/upstream-drafts/<issue-number>.md
```

(`skills/yf-plan/scripts/plan_manager.py:7936` and `:7948`.)

That path ...

**Disposition:**
**Notes:**

## #299 — yf harness: consolidate DESCRIPTORS + RULE_TARGETS into one table with an explicit rules-surface column
Labels: type::task, priority::medium
> ## The per-harness surface description is split across two tables that must agree and are not checked

Both from plan-044; grouped because the second is the **structural cause** of the first.

### 1. ...

**Disposition:**
**Notes:**

## #378 — Investigate incorporating okf-memory/okf-agent-memory into the yf-okf-* skills
Labels: type::task, priority::high
> Investigation spike. `okf-memory/okf-agent-memory` (https://github.com/okf-memory/okf-agent-memory) is a third-party, MIT-licensed, pure-Go implementation of Google OKF v0.2 — the same baseline `yf-ok...

**Disposition:**
**Notes:**

## #280 — yf-beads-upstream: detect_followons' `narrow` auto-eligible set has been permanently empty since it was written

> `detect_followons` in `skills/yf-beads-upstream/scripts/upstream.py` resolves a dependency
edge's target as:

```python
d.get("depends_on_id") or d.get("target") or d.get("to")
```

But its `deps_for`...

**Disposition:**
**Notes:**

## #271 — plan-056-james-dixson-473dba execution tracking
Labels: type::task, priority::high
> Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

Coarse tracking issue for plan-056, per this repo's one-issue-per-plan-scale-effort convention.

#...

**Disposition:**
**Notes:**

## #388 — yf-plan: the reconcile gate is poured with EMPTY metadata, so a plan.md-declared `Type: auto` gate is treated as human and deadlocks §6.4 after the push

> The reconcile gate is poured with **empty metadata**, so nothing ever auto-resolves it, and the
§6.4 close chain deadlocks **after the merge and push are already public**.

## Measured, on plan-068's ...

**Disposition:**
**Notes:**

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false
Labels: priority::high
> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:**
**Notes:**

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:**
**Notes:**

## #370 — yf-okf-hygiene: `backfill --apply` generates a NON-CONFORMANT `index.md` with no member listing — every transformed bundle immediately fails index-drift
Labels: bug
> **Found during plan-065's own corpus apply — by running the plan, not by reading the code.**

`backfill --apply` renames `README.md` -> `index.md` and then strips the README's prose (step `delete-rena...

**Disposition:**
**Notes:**

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:**
**Notes:**

## #223 — bd mol pour / yf-plan intake: one plan issue poured TWICE — 26 task beads for 25 declared issues, byte-identical duplicate
Labels: priority::high
> Filed by operator decision from the **plan-004** session in `dixson3/rc-files`.

## What happened

The §5.2a pour created **two beads for the same plan issue**. Measured immediately after Epic 1:

```...

**Disposition:**
**Notes:**

## #339 — Formalize execution-discovered issue filing: draft into the bundle, review, gate, then file — as a formula/wisp mini-DAG
Labels: enhancement
> ## The request

Formalize how issues **discovered during plan execution** get filed: draft them into the plan
bundle first, review them against a standard, optionally gate on operator approval, and on...

**Disposition:**
**Notes:**

## #192 — Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity

> ## Idea

Author plan **structure** in a machine-first artifact — YAML or a small DSL — holding epics, issues, dependency edges, gates, criteria, risks and the upstream table with its internal/external...

**Disposition:**
**Notes:**

## #377 — 69 payload .md files across 9 landed plan bundles lack YAML frontmatter — those bundles fail the portability audit

> Found while parking plan-066 (#317). Its own bundle audit went red on 11 frontmatter-less payload bodies; repairing those surfaced the same defect across the wider corpus.

## Measurement

```
payload...

**Disposition:**
**Notes:**

## #326 — `land`'s `draft_body_path` posts bundle files verbatim, but OKF requires them to carry frontmatter
Labels: bug, deferred
> ## The conflict

Two requirements apply to the same file and cannot both be satisfied:

1. **`land` L7 posts the file verbatim.** `_land_l7_reconcile_writes` runs
   `gh issue comment <n> --body-file ...

**Disposition:**
**Notes:**

## #346 — yf-research index_manager add: stamps a foreign idx into a bundle member and silently overwrites existing frontmatter type
Labels: priority::medium, type::bug
> Two related defects in `index_manager.py add`, both found in research 061's package phase.

## Defect 1 — a wrong `idx` is stamped from outside the bundle

`index_manager.py add` stamped `scripts/READ...

**Disposition:**
**Notes:**

## #337 — yf-research link_normalizer.py build-sources: emits non-OKF-conformant sources.md frontmatter, and derives an empty slug (malformed YAML) from a relative research_dir
Labels: priority::medium, type::bug
> Two distinct defects in the same command, found packaging research 058.

## Defect 1 — the generator produces a file the conformance checker rejects

`link_normalizer.py build-sources` writes `sources...

**Disposition:**
**Notes:**

## #415 — land: the manifest's draft_body_path points INSIDE the tree, but --apply refuses in-tree body_path — the two cannot both be satisfied

> **Found by plan-022's landing (d3-pxe). Not a duplicate of #333 — that issue is about the
`decision.json` path; this is about `upstream_writes[].body_path`, a different argument reaching
a different c...

**Disposition:**
**Notes:**

## #413 — yf-markdown-lint: ship and deploy a matching .markdownlint.jsonc so markdownlint-based tools (pi-lens) follow yf conventions
Labels: enhancement, type::feature, priority::medium
> ## Problem

`yf-markdown-lint` enforces its GFM conventions only through its own script (`scripts/markdown_lint.py`, rules ML001–ML011). It writes no configuration that other markdown tooling reads. A...

**Disposition:**
**Notes:**

## #191 — yf-plan: scaffold reviews/pass-N.md instead of hand-typing it — the shape check already fires, the authoring is what is missing

> ## The check already exists and works. That is the point.

`doc_lint`'s `required-sections` rule catches `## Missing (all now closed)` **every single time** — it fired on `pass-6.md`, on `pass-7.md`, ...

**Disposition:**
**Notes:**

## #291 — yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist

> > Filed by plan-059 Issue 2.7 (`yf-judgement`), which found this mitigation announced but never
> built. Source bundle: `docs/plans/plan-059-james-dixson-55137e/`.

## The gap

`#145` announces a `yf-...

**Disposition:**
**Notes:**

## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:**
**Notes:**

## #411 — yf-research red-team runs before packager generates sources.md — every citation reported as a broken link
Labels: priority::medium, type::bug
> ## Problem

The red-team runs before the packager, but the synthesizer is required to emit citation links that only resolve after packaging. The red-team has no way to know this, so it reports every c...

**Disposition:**
**Notes:**

## #345 — yf-okf: REQ-OKF-010 metadata-line scan is fence-blind — flags quoted command output, so the only way to pass is to corrupt the evidence
Labels: priority::medium, type::bug
> ## Observed

During research 061's package phase, `okf.py check` reported:

```
[error] artifacts/corpus-roundtrip.md  REQ-OKF-010
        a **Field:** metadata line sits below the first ##
```

The f...

**Disposition:**
**Notes:**

## #318 — P0 okf.py: --skill before the subcommand is silently dropped, inverting scaffold into an incubator state-file rename (data loss)

> ## P0 — data loss: `--skill` before the subcommand is silently dropped, inverting scaffold into a state-file rename

Measured 2026-08-30 against `yf-skills v0.5.0` at `~/.claude/skills`, while running...

**Disposition:**
**Notes:**

## #168 — yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3

> Filed by plan-046 Issue 5.5(i) as one of **three named carve-outs** from closing #92 as superseded. #92's emit half shipped natively and its nested-tree half is #140; these three are what a clean clos...

**Disposition:**
**Notes:**

## #330 — plan-062-james-dixson-c3e98f execution tracking

> Coarse tracking issue for **plan-062-james-dixson-c3e98f**.

- **Plan:** [`docs/plans/plan-062-james-dixson-c3e98f/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-062-james-dixson...

**Disposition:**
**Notes:**

## #298 — OKF/spec-family hygiene: ambiguous REQ ids, stale authority pointers, unmigrated okf_version split, phantom init verb
Labels: type::task, priority::medium
> ## Four spec-family hygiene defects: ambiguous ids, stale authority, an unmigrated version split, a phantom verb

Grouped because each is a **specification artifact that no checker reads**, so all fou...

**Disposition:**
**Notes:**

## #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine
Labels: priority::medium
> ## Summary

Six shipped scripts have **no test file and are referenced by no test anywhere in the repo**. This is the coverage half of the problem; the blind-spot half — suites that exist but assert o...

**Disposition:**
**Notes:**

## #410 — yf-research red-team: quote check reads only sources.json, but synthesizer quotes from cluster artifacts — false 'untraceable quote' [high] findings
Labels: priority::medium, type::bug
> ## Problem

The red-team's quote-fidelity check is structurally guaranteed to produce false "untraceable quote" findings, because it is given a narrower evidence set than the synthesizer that wrote th...

**Disposition:**
**Notes:**

## #169 — OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3

> Filed by plan-046 Issue 5.5(ii) as one of **three named carve-outs** from closing #92 as superseded.

**What this is.** yf-plan's bundles are conformance-gated: `plan_manager.py audit` runs the OKF en...

**Disposition:**
**Notes:**

## #275 — yf-herdr: the launch contract REQ-HERDR-015 mandates cannot be passed as documented, and three observer-pattern gaps (worktree, PR, merge protocol)
Labels: type::bug, priority::high
> Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

Filed from a live `yf-herdr` delegation (plan-056 execution, 2026-08-28). Everything below was
mea...

**Disposition:**
**Notes:**

## #302 — yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts
Labels: type::bug, priority::high
> Two measured defects in the same layer — **plan-folder identity and location** — found by observation
of plan-060's own drafting worktree. Both are instances of the class
[#301](https://github.com/dix...

**Disposition:**
**Notes:**

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them
Labels: priority::medium
> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:**
**Notes:**

## #274 — yf-plan: plan_extract.py SILENTLY mis-parses the multi-item resolves-upstream form — every issue gets the FIRST disposition

> > Found by plan-059's conformance pass while wiring a two-issue `resolves-upstream`. Reproduced and
> root-caused independently before filing.

## The defect

```
- resolves-upstream: #269 (include), ...

**Disposition:**
**Notes:**

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:**
**Notes:**

## #259 — doc_lint accepts a review verdict form that ready-check rejects — a review can pass the audit and be malformed to the gate
Labels: type::bug, priority::high
> ## The defect

**Two parsers in `yf-plan` disagree about what a review verdict line looks like, so a review file
can pass the portability audit while being unreadable to the gate that keys on it.**

-...

**Disposition:**
**Notes:**

## #269 — New skill: yf-judgement — detect when a plan needs OPERATOR JUDGEMENT and escalate a question, rather than attempting another fix

> > **Written to be read cold.** The empirical basis is `yf-research` 005 (PR #267,
> `docs/research/005-thrash-detection-and-operator-judgement/`), a deep-mode study over **114 plan
> bundles and 301 r...

**Disposition:**
**Notes:**

## #253 — Verification predicates keyed on a TERM catch cross-references, not edits: two false signals in one plan, one of them a criterion that could not see the surface it was written for
Labels: type::task, priority::medium
> ## Observed — twice, in opposite directions

`d3-pxe` plan-019 amended a large normative `SPEC.md`. Two verification predicates keyed on a term misfired — one **false positive**, one **false negative*...

**Disposition:**
**Notes:**

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:**
**Notes:**

---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #339 - Formalize execution-discovered issue filing: draft
  into the bundle, review, gate, then file — as a formula/wisp mini-DAG'
---
# Upstream #339: Formalize execution-discovered issue filing: draft into the bundle, review, gate, then file — as a formula/wisp mini-DAG

- **Number:** 339
- **Title:** Formalize execution-discovered issue filing: draft into the bundle, review, gate, then file — as a formula/wisp mini-DAG
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## The request

Formalize how issues **discovered during plan execution** get filed: draft them into the plan
bundle first, review them against a standard, optionally gate on operator approval, and only
then create them upstream. Today this is improvised per plan, or skipped.

## What plan-062 did ad hoc, and what it bought

plan-062's Issue 5.1 had to file five upstream writes. The sequence that emerged — not from any
skill instruction, but invented mid-execution and escalated to the operator — was:

1. **Draft to `assets/upstream-filings/`**, one file per intended write, each with OKF
   frontmatter carrying its intended `title`, an `upstream_action`
   (`gh issue create` / `gh issue edit + comment`), and `status: drafted-awaiting-authorization`.
2. **Index them** with real per-file descriptions; `reindex --check` clean; bundle audit green.
3. **Stop.** File nothing. Push a one-liner to the observing session.
4. **Review the wording** — a distinct act from verifying the substance.
5. **Operator authorizes**, then create, **verify every write by read-back**, record the URLs,
   and flip each draft's `status:` to `filed` with its URL.

Concretely this caught things a straight-to-`gh` path would not have. The reviewer checked a
factual premise in one draft — *"the `deferred` label already exists"* — before the write,
because `gh issue edit --add-label` fails on a missing label. It confirmed the `#326` edit was
conservative (**keeps** `bug`, **adds** `deferred`, comments rather than rewrites the body). And
because the drafts were on disk rather than in a transcript, they were reviewable at all: the
first report said *"drafts ready"* while `assets/` was **empty** — they existed only in the
executing session's context.

The five filings are #331, #332, #333, #334 and the #326 re-label.

## Why it should be a formula/wisp mini-DAG, not prose

Prose naming an obligation is skipped where prose naming a command is followed (#273). This
sequence is exactly the shape that decays into "the agent filed some issues at the end" —
several steps, each individually skippable, none with an exit code.

A **wisp or formula injected at the end of an epic or plan execution** makes each step a bead
with a state:

```
draft-followups  ->  self-review-against-standard  ->  [gate: operator approval]  ->  file  ->  verify-read-back  ->  record-urls
```

Benefits over prose:

- The **gate is a real gate**, so "file nothing yet" is enforced by the DAG rather than by the
  agent remembering. In plan-062 that property was load-bearing: *everything behind 5.1 was
  DAG-blocked*, so nothing could quietly proceed past an unresolved consent gate.
- **Drafts become bundle artifacts**, so they are reviewable, portable, and survive the session.
- `verify-read-back` is a step, not an instruction. plan-062 had to be told explicitly *"verify
  every write by read-back, not by exit 0"* — the same discipline the `land` L7 read-back
  enforces mechanically, applied by hand here.
- **The same steps run every time**, which is the whole point of a formula.

## Relationship to the existing `assets/upstream-drafts/`

There is already a directory for the **reconcile comment bodies** L7 posts at landing —
`assets/upstream-drafts/`, computed by `_land_upstream_rows`. It is undocumented in every
yf-plan `.md` (**#332**), which is its own defect.

plan-062 kept the two sets deliberately distinct: `upstream-drafts/` for reconcile comments on
rows in the plan's Upstream Issues table, and `upstream-filings/` for **new** issues discovered
during execution. That distinction is worth preserving in any design — they have different
lifecycles, different consumers (L7 reads one; nothing reads the other), and different
end states.

## Open questions for the design

- **Where does it inject?** End of each epic (discoveries filed while fresh) or once at plan
  end (one operator interaction)? Per-epic risks interrupting an autonomous run repeatedly;
  plan-end risks losing context for early discoveries.
- **What is the standard?** plan-062's drafts converged on: measured evidence with `file:line`,
  an explicit scope statement (one draft correctly said the defect was *"latent, not reachable
  through the shipped CLI today"*), and a concrete suggested fix. Worth encoding as a checklist
  a self-review step can run.
- **Is operator approval always required, or only for the wording?** The substance was already
  verified by measurement in plan-062; only the published wording needed a human. A
  `propose-with-confirm` default with an opt-out config would mirror `yf-beads-upstream`'s
  follow-on hoist.
- **Interaction with the coarse-granularity convention.** `AGENTS.md` says one tracking issue
  per plan, not one per bead. Execution-discovered defects are a legitimate exception — plan-062
  filed five — but the boundary should be stated rather than left to judgement.

## Provenance

Requested by the operator after **plan-062** (`plan-062-james-dixson-c3e98f`, tracker #330),
whose Issue 5.1 improvised this sequence and whose escalation record (`escalations.md`,
`plan-retrospective.md`) carries the detail. Adjacent to **#332** (the sibling directory is
undocumented) and **#273** (command-vs-obligation).


---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #191: yf-plan: scaffold reviews/pass-N.md instead of hand-typing it — the shape check already fires, the authoring is what is missing

- **Number:** 191
- **Title:** yf-plan: scaffold reviews/pass-N.md instead of hand-typing it — the shape check already fires, the authoring is what is missing
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The check already exists and works. That is the point.

`doc_lint`'s `required-sections` rule catches `## Missing (all now closed)` **every single time** — it fired on `pass-6.md`, on `pass-7.md`, and on `pass-10.md`, and the portability audit surfaced it within seconds each time.

Detection is not the gap. **Authoring is.** The same operator wrote the same malformed heading in three of eleven review records, twice *immediately after* recording a concern about having written it before. Adding a second check would detect it a second time.

## What is missing: a scaffold

`reviews/pass-N.md` has a fixed required shape — `## Verdict:`, `## Strengths`, `## Concerns`, `## Missing`, `## Gate Assessment`, `## Upstream Assessment`, `## Resolutions`, plus frontmatter and a `| Concern |`-leading table. Every one of those is hand-typed today, and `plan_manager.py` has no verb that emits the skeleton.

**The precedent already exists in this repo.** `SKILL.md:370`:

```
<!-- >>> BEGIN plan.md skeleton — GENERATED from _shared/plan_template.py by _shared/sync.py; do not edit by hand -->
```

The `plan.md` skeleton is generated. Review records — which have an equally fixed shape and are written far more often — are not.

## Proposal

Add `plan_manager.py review-new <plan_dir>`:

- Computes `N` the way `_review_cycle_count` already does, so the pass number cannot drift from the file count.
- Emits the frontmatter and every required heading, with the resolutions table's `| Concern |` column already in place.
- Writes the paired `log.md` `- review-pass:` bullet in the same step — REQ-PORT-006's count-equality invariant is currently maintained by two hand-written edits that must agree, which is its own latent defect.
- Refuses if `pass-N.md` already exists.

The author then fills bodies under headings they did not type.

## Why this is worth doing rather than "just be careful"

Three occurrences across eleven records, two of them in the same file that documents the prior occurrence, is not an attention problem — it is a missing mechanism. This repo's own doctrine (research 004's headline) is that a written rule nothing executes is unreliably obeyed. "Use these exact headings" is such a rule. A generator is the executable form.

Scoped small: one verb, one template, no schema change, no migration.

## Related

- #188 (suites assert structure, never payload fidelity) — same family: the check exists, the thing it guards is authored by hand.
- The broader version of this idea — authoring plan *structure* in a generated form rather than hand-written markdown — is filed separately.

## Provenance

`plan-050-james-dixson-d0414b`, review cycles 6, 7 and 10; recorded in `reviews/pass-7.md` (C82) and `reviews/pass-10.md`.

---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #415 - land: the manifest''s draft_body_path points INSIDE
  the tree, but --apply refuses in-tree body_path — the two cannot both be satisfied'
---
# Upstream #415: land: the manifest's draft_body_path points INSIDE the tree, but --apply refuses in-tree body_path — the two cannot both be satisfied

- **Number:** 415
- **Title:** land: the manifest's draft_body_path points INSIDE the tree, but --apply refuses in-tree body_path — the two cannot both be satisfied
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

**Found by plan-022's landing (d3-pxe). Not a duplicate of #333 — that issue is about the
`decision.json` path; this is about `upstream_writes[].body_path`, a different argument reaching
a different consumer, and the two have opposite correct answers.**

## The conflict

`land --apply` refuses a decision whose `body_path` entries live inside the work tree:

```
verdict: fail
reason: 2 path(s) live INSIDE the work tree /Users/james/workspace/dixson3/d3-pxe:
  body_path=docs/plans/plan-022-.../assets/upstream-drafts/111.md,
  body_path=docs/plans/plan-022-.../assets/upstream-drafts/112.md.
  L16's post-condition enumerates untracked entries, so each of these halts the landing
  AFTER the reconcile comments are posted and `status: complete` is written (#333).
remediation: Move them outside the checkout and re-run.
```

That refusal is correct and well-placed — it fires **before** any write, which is exactly what
#333 asked for. The problem is that `land --dry-run` **asks for the opposite**, in the same
landing, for the same files:

```
issue 111 draft_body_path: docs/plans/plan-022-.../assets/upstream-drafts/111.md   draft_present: False
issue 112 draft_body_path: docs/plans/plan-022-.../assets/upstream-drafts/112.md   draft_present: False
```

The manifest names an **in-tree** path per row and reports `draft_present: false` until a file
exists *there*. So:

- put the bodies where the manifest points → `--apply` refuses them;
- put them where `--apply` accepts them (`$TMPDIR`) → the manifest keeps reporting
  `draft_present: false`.

Measured both ways in one landing. Placing the drafts at the manifest's paths flipped
`draft_present` to `true` and immediately produced the halt above; moving them to `/tmp` cleared
the halt and returned `draft_present` to `false`.

## Why `draft_present: false` is not harmless

It is a fact the lander adjudicates against. In plan-022 the lander read `draft_present: false`,
correctly concluded it had no authority to write into the repo, emitted `/tmp` paths, and said so
explicitly:

> The manifest's `draft_body_path` entries under `assets/upstream-drafts/` report
> `draft_present: false`; I have write authority over neither, so these `/tmp` files are the
> bodies. **If `--apply` expects the bodies at the manifest's paths, the main session must copy
> them there — I did not.**

Following that instruction is what triggered the refusal. The agent reasoned correctly from the
manifest and was led into the halt by it.

## Interaction with #326

#326 records that L7 posts `draft_body_path` **verbatim** while OKF requires frontmatter on every
bundle `.md`. That conflict only arises for in-tree bundle files. If the resolution here is
"bodies live outside the tree," #326 largely dissolves — a `$TMPDIR` body is not a bundle file
and carries no frontmatter obligation. If instead the resolution is "bodies live in the bundle,"
then #326 must be fixed first and this issue's refusal needs to learn about `<plan_dir>` as an
exemption. **The two issues should be decided together; fixing either one alone can contradict
the other.**

## What the operator is left with

An unavoidable inconsistency in the bundle: the drafts that were actually posted upstream are
committed at `assets/upstream-drafts/{111,112}.md` for the durable record, while the paths the
landing consumed are `/tmp/p022-upstream-{111,112}.md`. Their sha256s match, but nothing in the
bundle records that correspondence, and `/tmp` is gone on reboot. A cold reader cannot verify
from the bundle alone that the committed drafts are what was posted.

## Suggested fixes

1. **Make the manifest's `draft_body_path` agree with what `--apply` accepts.** Whichever
   location wins, one of the two must change; they currently cannot both be satisfied.
2. If bundles win: teach the `--apply` preflight that `<plan_dir>` is an exemption, and fix #326
   so L7 strips frontmatter on the way out (keeping the read-back comparison honest).
3. If `$TMPDIR` wins: `draft_present` should be computed against the decision's actual
   `body_path`, not against the manifest's assumed in-tree location, so the lander is not told a
   draft is missing when it exists. Consider having `land --dry-run` emit the `$TMPDIR` path it
   expects, the way it already defaults the decision file there.
4. Either way, record the posted-body provenance **in the bundle** — a sha256 of each posted
   comment body alongside the committed draft — so the record survives `/tmp`.


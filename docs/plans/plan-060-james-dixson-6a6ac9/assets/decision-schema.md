---
type: Reference
okf_spec: OKF-PLAN
description: Draft schema for the landing manifest (`land --dry-run` output) and the landing decision document (`land --apply` input) — the two data structures that carry the three-layer split.
---
# Landing manifest and decision document — draft schema

Two documents, one direction of flow:

```
land --dry-run  ──emits──>  MANIFEST (facts)
                                │
                                ▼
                          lander agent  ──emits──>  DECISION (judgements)
                                                          │
                                                          ▼
                                                  land --apply <decision.json>
```

**The invariant that makes this safe:** `--apply` trusts the decision document for **judgements
only** — grouping, prose bodies, which rows may close, whether the landing is exceptional. It trusts
it for **no fact whatsoever**. Every fact is **re-derived at apply time** and compared against the
manifest digest the decision carries. A decision that disagrees with re-derived reality is a
**halt**, not an override.

This is what makes the agent structurally unable to fabricate an authorization: the only fields it
controls are ones that cannot, by themselves, cause a write to happen.

## 1. The manifest — `land --dry-run --json`

```jsonc
{
  "schema": "yf-plan/landing-manifest@1",
  "verdict": "pass|fail|inconclusive",     // REQ-COMPLETE-003 envelope
  "passed": true,
  "reason": "...",
  "remediation": "...",

  "digest": "sha256:...",                  // over the `facts` object, canonically serialized
  "generated_at": "2026-08-29T17:30:00Z",
  "generator": { "plan_manager_version": "...", "git_head": "..." },

  "facts": {
    "plan": {
      "plan_id": "plan-060-james-dixson-6a6ac9",
      "plan_dir": "docs/plans/plan-060-james-dixson-6a6ac9",
      "status": "reconciling",
      "fingerprint_fresh": true,
      "epic": "yf-mol-xxxx",
      "deliverable_class": "standard"
    },

    "git": {
      "landing_strategy": "main",
      "merge_target": "main",
      "execute_branch": "plan-060-...-execute",
      "worktree_path": ".worktrees/plan-060-...",
      "worktree_dirty": false,
      "dirty_files": [],
      "target_behind_origin": 0,
      "resolved_target_tip": "a1b2c3d...",  // the target's oid AT DRY-RUN TIME
      "merge_preview": {
        "conflicts": [],                   // three-way merge probe, no working-tree mutation
        "predicted_tree": "bfb758c...",    // `git merge-tree --write-tree` result oid
        "changed_paths": ["skills/yf-plan/..."],
        "touches_skills": true             // drives the redeploy step
      },
      // `predicted_tree` and `resolved_target_tip` are the two DIGEST-COVERED fields that make the
      // staleness edge detectable: measured (EXP-006 F4), the predicted tree oid CHANGES when the
      // target moves, so a digest omitting them cannot detect the drift it exists to detect.
      "plan_number_collisions": []         // #302-B3: other plan-NNN-* on the target sharing NNN
    },

    "close_chain": [                       // one row per step, from --list-steps
      { "step": "audit-close", "class": "advisory", "verdict": "pass", "exit": 0, "reason": "..." },
      { "step": "verify-reconcile", "class": "halting", "verdict": "fail", "exit": 1,
        "rows": [ { "issue": 140, "disposition": "partial", "verdict": "fail",
                    "detail": "no comment mentions plan-057" } ] }
    ],

    "upstream": {
      "rows": [                            // from plan.md's Upstream Issues table
        { "issue": 301, "disposition": "include", "required_end_state": "CLOSED",
          "requires_mention": true, "current_state": "OPEN", "satisfied": false,
          "draft_body_path": "assets/upstream-drafts/301.md", "draft_present": true }
      ],
      "tracker": { "issue": 271, "external_ref_stamped": true }
    },

    "beads": {
      "tree": { "epic": "...", "open": 3, "closed": 41, "gates_unresolved": 1 },
      "unresolved_gates": [
        { "id": "yf-mol-xxxx.9", "title": "Gate: Reconcile upstream",
          "gate_type": "auto", "condition_holds": false,
          "detail": "condition re-derived FALSE — 4 comments unposted" }
      ],
      "residual_open": [                   // candidates for upstream mirroring
        { "id": "yf-zeyz", "title": "...", "description": "...", "external_ref": null }
      ]
    },

    "prune": {
      "worktree_registered": true,
      "remote_branch_exists": true,
      "herdr_tab": { "id": null, "provenance": "unknown" }   // D-7: currently unanswerable
    },

    "harvest_preconditions": {             // #204, evaluated but NOT yet satisfiable pre-apply
      "artifacts_on_origin": false,
      "status_complete_on_origin": false,
      "worktree_clean": true,
      "unpushed_commits": 2
    }
  },

  "halts": [                               // pre-flight refusals; --apply cannot proceed past these
    { "code": "stale-approved", "detail": "...", "resolvable_by_agent": false }
  ]
}
```

### Manifest rules

- **`--dry-run` changes no ref, no file and no working-tree state**, and performs no `git merge` into
  the working tree; the merge preview is a three-way probe (`git merge-tree --write-tree`) against
  the object database.

  **It is NOT true that the dry run "writes nothing at all"** — measured (EXP-006 F1),
  `--write-tree` creates an **unreferenced tree object** in the ODB. It is garbage-collectable and
  observable to nothing, but the stronger phrasing would be false, so no rule or criterion asserts
  it. `git status --porcelain` is empty, and that is the claim that is made.
- **The preview is computed by the same code as the apply** (`okf_hygiene.py backfill`'s property,
  D-9). A preview computed by a parallel code path is not a preview.
- Every `verdict` in `close_chain` is the **three-valued** vocabulary. An `inconclusive` is reported
  and never coerced to `fail` — the defect #262 records inside `_validate_merged` must not be
  reproduced here.
- **The FULL tier is NOT run at dry-run.** It exceeds 300 s (D-8) and its result is only meaningful
  against a real merge. The manifest reports that it *will* run, not its outcome.

## 2. The decision document — the `lander` agent's output

```jsonc
{
  "schema": "yf-plan/landing-decision@1",
  "manifest_digest": "sha256:...",         // MUST equal the re-derived manifest digest at apply
  "plan_id": "plan-060-james-dixson-6a6ac9",
  "authored_by": "lander",
  "authored_at": "2026-08-29T17:35:00Z",

  "summary": "<prose the operator reads — the single consent prompt's body>",

  "upstream_writes": [                     // the enumerated outward-facing set
    { "issue": 140, "action": "comment", "body_path": "assets/upstream-drafts/140.md",
      "rationale": "disposition is `partial`; the issue STAYS OPEN. Records what shipped and what remains.",
      "body_sha256": "..." },
    { "issue": 290, "action": "close", "close_reason": "completed",
      "rationale": "genuinely fixed by Issue 2.4; the only row whose disposition permits a close." }
  ],

  "upstream_refusals": [                   // #301 adjudication case 2 — refusing a wrong instruction
    { "issue": 170, "requested": "close", "refused_because":
      "disposition is `partial`, whose contract is end_state OPEN (UPSTREAM_REQUIREMENTS). Closing it would contradict the dispositions the plan was approved with." }
  ],

  "residual_bead_groups": [                // #301 adjudication case 1 — the coarse-granularity judgement
    { "proposed_title": "plan_extract.py is the sole reader of plan.md and nothing diffs the read against the source",
      "beads": ["yf-zeyz", "yf-pctx", "yf-2yo2"],
      "rationale": "shared CAUSE, not shared filename. One issue per bead violates AGENTS.md's coarse policy; one issue for all is useless.",
      "body_path": "assets/upstream-drafts/followon-1.md" }
  ],

  "gate_adjudications": [                  // #301 adjudication case 3
    { "gate": "yf-mol-xxxx.9", "manifest_says": "condition_holds: false",
      "decision": "leave-open",
      "rationale": "the mechanical condition would read TRUE once Issue 3.5 closes as deferred, while its four comments are unposted. verify-reconcile is the honest signal." }
  ],

  "sequencing": {                          // #301 adjudication case 4
    "blocked_by_other_plans": [],
    "rationale": "no index.md contention with an in-flight plan"
  },

  "steps": {                             // ONE KEY PER L-LABEL. Not a coarse paraphrase.
    "l0_lock_acquire":        "enable",  // NON-SKIPPABLE
    "l1_down_merge":          "enable",  // NON-SKIPPABLE
    "l2_merge":               "enable",  // NON-SKIPPABLE
    "l3_validate_merged":     "enable",  // NON-SKIPPABLE — the FULL tier
    "l4_commit_merge":        "enable",  // NON-SKIPPABLE
    "l5_advisory_recheck":    "enable",  // NON-SKIPPABLE (advisory in VERDICT, not optional to run)
    "l6_push_one":            "enable",  // NON-SKIPPABLE — first irreversible step
    "l7_reconcile_writes":    "enable",
    "l8_close_chain_head":    "enable",
    "l9_close_reconcile_step":"enable",
    "l10_verify_reconcile":   "enable",
    "l11_recheck_criteria":   "enable",
    "l12_close_cascade":      "enable",
    "l13_complete_gate":      "enable",
    "l14_pour_fidelity":      "enable",
    "l15_update_status":      "enable",
    "l16_commit_and_push_two":"enable",  // NON-SKIPPABLE — skipping it REPRODUCES D-2's residue
    "l17_residual_mirroring": "enable",
    "l18_prune":              "skip:provenance-unknown",
    "l19_redeploy":           "enable"
  },

  "exceptional": false,
  "exception_rationale": null
}
```

### The `steps` key set is pinned to the L-labels, and not every step is skippable

The `steps` object's keys are **one-to-one with the L0-L19 labels**, not a coarse paraphrase of
them. A coarse key set cannot express a two-push order (one `push` key for two pushes), silently
omits the down-merge, the FULL tier and the advisory pre-push run, and — most importantly — would
make `merge: skip` legal.

**The non-skippable set is `L0-L6` plus `L16`**, and each member is non-skippable for a stated
reason rather than by blanket rule:

| Step | Why it cannot be skipped |
| :-- | :-- |
| L0 lock acquire | skipping it removes the serialization the whole merge-back depends on |
| L1 down-merge | without it, L11's completion-time measurement does not read the tree that will be on the target |
| L2 merge | **skipping the merge is not narrowing the landing — it is a different operation**, and it contradicts the thesis that authorizing the merge *is* the authorization |
| L3 FULL tier | the one control that makes an irreversible landing survivable |
| L4 commit merge | an uncommitted merge cannot be pushed or reverted cleanly |
| L5 advisory recheck | *advisory* describes its **verdict** (never halting), not whether it runs |
| L6 push #1 | the reconcile comments at L7 assert work shipped; that is false if this is skipped |
| **L16 push #2** | **skipping it reproduces D-2's residue exactly** — the uncommitted, unpushed `status: complete` this plan exists to remove |

`--validate-decision` enforces the set as part of the narrowing-only check. Everything else is
skippable with a reason, and every skip is surfaced in the consent prompt.

### Decision rules

- **The agent supplies no fact and no exit code.** There is no field in which it can assert that a
  condition holds, that a test passed, or that anyone authorized anything. It supplies *titles,
  groupings, rationales, body paths and enable/skip choices* — and every one of those is either
  inert or re-checked.
- **`manifest_digest` binds the decision to the facts it was adjudicated against.** At apply time
  `land` re-derives the manifest and compares. A mismatch means the world moved under the decision:
  **halt**, re-run `--dry-run`, re-adjudicate. It is never an override path.
- **`body_sha256` binds each enumerated write to the exact bytes the operator was shown.** A body
  edited between consent and apply is a different write.
- **`enable` can never widen the manifest.** An `enable` on a step the manifest marks halted is
  ignored and reported; the decision can only ever *narrow* what happens. `skip` needs a reason;
  `enable` does not, because enabling is the default and skipping is the deviation.
- **Every skip is surfaced in the consent prompt**, so "the landing did less than you think" is never
  silent.

## 3. What `--apply` re-derives rather than trusts

| Fact | Trusted from decision? | Re-derived at apply? |
| :-- | :-: | :-: |
| whether a gate's condition holds | **no** | **yes** |
| any close-chain step's verdict / exit code | **no** | **yes** |
| merge conflicts | **no** | **yes** |
| FULL-tier result | **no** | **yes** (this is the only place it runs) |
| upstream issue current state | **no** | **yes** (`gh issue view`, before and after each write) |
| worktree cleanliness, unpushed count | **no** | **yes** |
| plan-number collision on target (#302-B3) | **no** | **yes** |
| *which* issues to comment on / close | yes | contract-checked against `UPSTREAM_REQUIREMENTS` |
| *how* residual beads group | yes | — (pure judgement, no factual content) |
| comment body prose | yes | byte-checked against `body_sha256`, read back after write |
| enable/skip per step | yes (narrowing only) | — |
| `exceptional` / `exception_rationale` | yes | — · **INERT BY CONTRACT**: prose surfaced verbatim in the consent prompt. It can never enable a step, widen a step, satisfy a halt, or stand in for a re-derived fact. A boolean the agent sets whose effect were unspecified would be exactly the shape §2's central claim forbids, so its effect is specified here as *nothing*. |

## Open questions this schema does not yet answer

1. **What authorizes `--apply` itself**, given the session that benefits is the session that types
   it — the subject of EXP-005. The schema reserves no field for it deliberately: a consent token
   the executing session can write into the decision document would be #293 with extra steps.
2. **The journal's state set** for crash recovery across the outward-facing steps (D-9's model).
3. **Whether `--apply` is resumable** or must re-run from `--dry-run` after a partial failure.

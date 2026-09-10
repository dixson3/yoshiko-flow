---
type: Finding
okf_spec: OKF-PLAN
description: >-
  [finding] yf-jp7z's premise CONFIRMED but its remedy REFUTED - the WIDE exclusion blinds the digest to all three foreign-landing classes and lets a conflicting landing validate 'pass'; real scope is five self-mutated facts across four resume points, and L4 alone mutates them, not L6
id: exp-003-digest-exclusion
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
---
# EXP-003: The digest exclusion — bead `yf-jp7z`'s premise CONFIRMED, its remedy REFUTED

**Question.** Do L4/L6's self-mutations justify widening `LAND_DIGEST_EXCLUDED` to cover
`resolved_target_tip` and `merge_preview`? (#353 / bead `yf-jp7z`, P1)

**Method.** Source read of the digest machinery and `spec/landing.md` REQ-LAND-002/011/018/036;
four sandbox spikes computing the real manifest and digest before and after (i) the landing's own
L1/L2/L4, (ii) L15's status write, (iii) four classes of *foreign* landing — under three candidate
exclusion sets: current NARROW, the bead's proposed WIDE, and a SUB-FIELD alternative derived from
the measurements. Two independent fixtures (trivial and non-trivial down-merge).

## Verdict

**The bead's premise is TRUE and understated. Its proposed fix is UNSAFE and must not be adopted
as written.**

## What the digest defends

REQ-LAND-018: *"A clean preview does not guarantee a clean apply… re-preview immediately before
the merge and halt on any change since the decision was minted."* REQ-LAND-002: `--apply` trusts
the decision *"for judgements only and for no fact whatsoever"*; a disagreement *"is a **halt**,
never an override"*. The threat is **a changed world between dry-run and apply** — a foreign
landing moving the merge target. It is not a tamper control: the digest is unkeyed and unsigned.

## Premise confirmed — and the scope is larger than #353 states

Spike 1, real merge, real commit:

```
T0 dry-run      digest sha256:b62e3c7c…  tip ba2f42bf…  changed_paths ['skills/new.py']
after L4        digest sha256:9885e31c…  tip e4662d26…  changed_paths []
MISMATCH vs d0? True
```

Guaranteed, not conditional: L4 always commits on the target, so the tip always moves. **But the
landing self-mutates FIVE covered facts across FOUR resume points, not two:**

| Resume point | Self-mutated covered fact | Fixed by the bead's WIDE? |
| :-- | :-- | :-- |
| `L_MERGED_UNCOMMITTED` (after a halt at **L3, the multi-minute FULL tier** — the likeliest halt in the chain) | `primary_checkout_dirty_outside_plan_dir` **and** `primary_checkout_staged_outside_plan_dir`, both `false → true` (L2's uncommitted merge *is* dirt outside the plan dir) | **No** |
| `L_VALIDATED` … `L_PUSHED_1` | `resolved_target_tip`; `merge_preview.changed_paths`; `merge_preview.touches_skills` | Yes |
| `L_CLOSED` and after | `plan.status`, `reconciling → complete` (L15's own write) | **No** |

A fix scoped to the bead's two fields leaves resumes after L3 and after L15 broken.

## Two factual errors in #353 to correct upstream

1. **L6 mutates neither fact.** `_land_l6_push_one` pushes to `origin`; both facts are read from
   *local* refs. **L4 alone** is responsible — the single line `ctx.run("git", ["commit",
   "--no-edit"])` at `:9316` moves the tip, and the *same* commit collapses `merge_preview`.
   The issue attributes it to "L4's merge commit and L6's push".
2. **`predicted_tree` is NOT invalidated by the landing's own merge** — measured stable across
   both trivial and non-trivial down-merges, contrary to the issue body.

## The central question — WIDE is refuted by measurement

| Adversarial case | NARROW detects | **WIDE detects** |
| :-- | :-- | --: |
| foreign clean landing on the target | yes | **NO** |
| foreign **conflicting** landing | yes | **NO** |
| foreign landing that **deletes** a file (merges clean) | yes | **NO** |
| foreign plan-number collision | yes | yes (via `plan_number_collisions`) |

Worse: on the conflicting case the decision **validates as `pass`** under WIDE (`verdict: pass,
problems: []`), because the manifest's fresh `merge-conflicts-predicted` halt only produces
`ignored_enables` — it does not fail `_land_validate_decision`. The landing then proceeds to L2
and discovers a conflicted working tree: exactly the outcome REQ-LAND-018 exists to convert into
a legible staleness report *before anything was touched*.

**The case is entirely reachable here** — this repo lands multiple plans against `main`, and the
decision-minting window (lander dispatch + operator review) is precisely when a foreign landing
can occur. Adopting `yf-jp7z` as written **trades a nuisance halt for a silent one, on the
digest's only real threat model.** The source comment already says so: *"NOTHING ELSE BELONGS
HERE… excluding them would make the check vacuous."*

## Options

| Option | Cost | Preserves |
| :-- | :-- | :-- |
| **(a) Re-compute the digest at each resume boundary** | **Vacuous — reject.** The value is minting it *before* the adjudication; recomputing on resume compares reality to itself. Would satisfy every existing test and detect nothing | Nothing |
| **(b) Journal-recorded self-mutation** (#353's own proposal) | Largest but SPEC-correct. Measured blocker: `_land_execute` writes `ctx.journal.write(r["journal"], step=r["step"])` — **only `step`**; L4's already-computed `merged_tree` never reaches the journal. Needs the same treatment for L2's dirt and L15's status. A corrupt/absent journal detail must fail **closed** | Full foreign-drift detection, incl. tree-identical cases |
| **(c) Split stable vs volatile digest** | Widest blast radius: `LAND_SCHEMA_DECISION` bump, two comparison rules, a policy for volatile-only mismatch | Same as (b), plus legibility of which half moved |
| **(d) SUB-FIELD exclusion** — *derived from measurement, not in the brief* | Small and mechanical: exclude `resolved_target_tip`, `merge_preview.changed_paths`, `merge_preview.touches_skills`; **keep `predicted_tree` and `conflicts` covered**. `_land_digest_coverage` already walks arbitrary depth (verified). Does **not** fix the L2-dirt or L15-status mismatches | Foreign-drift detection on **all three** classes WIDE loses |

**Why (d) works:** `merge_preview.predicted_tree` is the only covered field that is *stable under
the landing's own merge* and *unstable under every foreign landing*. Measured: SUBFIELD detects
the clean, conflicting, and delete cases. **Honest limitation:** it misses foreign drift leaving
the merged tree byte-identical — an empty commit, an add+revert pair, or a foreign landing of an
*identical* change. The first two are benign (L3 validates the same tree); the third is not, but
its signal is *indistinguishable* from the self-mutation, so no field-keyed rule can separate them.

## Absence findings — no test computes a digest on a post-L4 tree

| Search | Result |
| :-- | :-- |
| `grep -rn "L_VALIDATED" skills/yf-plan/scripts/test_*.py` | **zero matches in any test file** |
| `grep -rn "_land_repreview_or_halt\|_land_bind_decision" test_*.py` | 5 call sites, **all on an unmutated tree** (no merge performed) |
| the three resume tests | exercise the **step-skip set only**; never touch the digest |
| `test_digest_survives_resume_after_teardown` (REQ-LAND-036's verifier) | **synthetically** flips the two L18 facts on a manifest from a repo where **no merge ever happened** |

The gap is structural: every resume test stubs the executor and every digest test skips the merge.
That is why the defect reached plan-063's real landing.

## Implications for the plan

1. **Do not plan against `yf-jp7z` as written.** Re-scope the bead first — five facts, four resume
   points — and correct #353's two factual errors upstream.
2. **SPEC-first:** amend **REQ-LAND-036** (its exhaustive exclusion table gains a column naming
   *which step* mutates each excluded fact — L2 / L4 / L15 / L18), and amend **REQ-LAND-018**'s
   rationale to say `predicted_tree`, not the target tip, is the detection-bearing field.
3. **A test must land in the same change-set**, or the current verifier stays green under either
   fix *and* under no fix. It must perform a **real merge commit**, assert digest stability across
   it, and assert **both directions** — that foreign clean / conflicting / delete landings each
   still mismatch.

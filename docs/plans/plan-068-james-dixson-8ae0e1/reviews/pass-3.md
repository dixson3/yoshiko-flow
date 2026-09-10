---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
description: >-
  [red-team pass 3] REVISE - 9 concerns. The declared ctx-less helper set was SIX not three and one
  is SPEC-mandated by REQ-LAND-031; SC9 was green-by-construction at the point it is evaluated; the
  rehearsal stubs five things not three; and a FOURTH item was dropped by both plans while plan-069
  falsely asserted plan-068 had done it. Counts and Gate 1 verified clean.
---
# Red-Team Pass 3 — plan-068-james-dixson-8ae0e1

## Verdict: REVISE

Third pass, aimed specifically at the pass-2 fixes. Read-only; sandboxes removed.

## Strengths

- **Counts are finally clean.** `plan_extract.py` measures exactly what the plan claims: 5 epics,
  **23** issues, 5 gates, **16** criteria, 9 risks, 0 `unparsed`, 0 `recovered`, 31 edges, zero
  dangling, zero cycles, zero undischarged, longest chain **6 nodes**.
- **Gate 1 is sound.** Run literally on macOS in **both zsh and bash**: live repo → `0`;
  `phases.md` missing → `MISSING:` on stderr, exit `1`; id taken in `phases.md` → `1`; unreadable
  `SPEC.md` → `1`. `exit 1` terminates the whole string — verified by appending `; echo
  REACHED-AFTER`, which did not print. `REQ-LAND-037/038` confirmed the correct next free ids.
- **SC9's five tested cases reproduce**, plus merge commits, `main` moving and being down-merged,
  rebase, empty branches, identical hashes, and committer-date skew.

## Concerns

| # | Severity | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | high | **The declared ctx-less helper set is SIX, not three, and one is SPEC-MANDATED.** An AST call-graph closure finds `_validate_merged` (L3 — the FULL validation tier, the largest process launch in the landing), **`_worktree_teardown`** (L18) and `_dirty_outside_plan_dir` (L16) alongside the three declared. **`REQ-LAND-031` normatively requires L18's call** — *"Step L18 shall call `_worktree_teardown` with `force=False` in keyword form"* — so Issue 1.3's check would flag a call the SPEC mandates, and REQ-LAND-037 was **still false on arrival**. Third consecutive pass to find a hand-written list short | **Verified independently** (six confirmed by my own AST closure; REQ-LAND-031 quoted from `landing.md:464`). **Fixed as a class, not an instance:** 0.3 now mandates a module constant `LAND_CTXLESS_HELPERS` **derived by AST call-graph closure**, with `spec/landing.md` quoting it; the REQ-LAND-031 carve-out is stated explicitly; and the requirement must say which class each helper is in, since `_dirty_outside_plan_dir` already takes `runner=` |
| C2 | medium-high | **Issue 1.3's "resolve from 0.3's declared helpers" was a wish** — pass-1 C4's shape. Those helpers live in **markdown prose**; an AST check can only regex-scrape prose (brittle), compute from the call graph (tautological — can never fail), or hand-write the list (forbidden) | Resolved by C1's structural fix: the declaration is now a **machine-readable module constant**, a companion test pins it to the SPEC text, and 1.3 reads the constant. "One enumeration" becomes real rather than asserted |
| C3 | high | **SC9 was green-by-construction at the point it is evaluated.** L2/L4 put HEAD on `main`, so by the close chain `main..HEAD` is empty, both variables are empty, and the check short-circuits to **exit 0**. The plan's only SPEC-first enforcement, detecting nothing where it is actually read | **Reproduced, then fixed and re-verified across seven cases.** SC9 is now **merge-aware** (`HEAD^1..HEAD^2` when HEAD is a merge) and returns **INCONCLUSIVE (exit 2)** rather than a silent 0 on an empty range. The decisive new case — a **violating branch merged to main** — now correctly exits **1** |
| C4 | high | **`land_rehearsal.py` stubs FIVE things, not three**, and two cannot be reached by a `runner=`: `pm._validate_merged` (L3's entire validation) and `pm._worktree_teardown` (L18). SC3's `_land_l*` wording does not match those names, so a `LAND_EXECUTOR`-derived `stubbed_steps` would report **zero** stubs while two remain — the "hides the gap" defect 1.5 exists to remove, one layer down. **"Zero-stub rehearsal" is false as stated** | 1.5 re-scoped to **five** stubs with an explicit decision required for the two helper monkeypatches; **SC3 reworded** to enumerate *any* `pm.*` monkeypatch still in force, not only `_land_l*` names; the "zero-stub" phrasing is retired |
| C5 | medium-high | **The injected runner cannot both suppress outward writes and let the landing happen.** `_dispatch` routes **every** program through the runner, `git` included — so a stub-everything runner makes `L_DONE` a fiction, while a pass-through runner really runs `gh`, `bd` and L19's `yf self install`. 2.5 said only "keeps outward writes inside the sandbox". (The *routing* claim was verified true after 1.1; the *suppression* claim was the unspecified one) | 2.5 now states the contract: pass `git` **through** to the sandbox (its local bare `origin` is what makes the push safe, not the runner), intercept `bd`/`gh`/`uv`/`yf` with **argv-recognising** fakes that **fail on unrecognised argv rather than returning 0** — the hazard `LandingContext`'s own docstring records. L19 reached with a non-`skills/` change set or a fake asserting it was never asked to redeploy |
| C6 | high | **A FOURTH item carried by neither plan — and plan-069 asserted it was already done.** EXP-003 implication 2 (the `REQ-LAND-036` exclusion-table column and the `REQ-LAND-018` rationale amendment) appears in no issue of either plan, while plan-069's text stated *"plan-068's SPEC work adds a documentation column to REQ-LAND-036 and fixes REQ-LAND-018's rationale"* — **false**; 068's Epic 0 allocates only 037/038 and amends 002/004 and the REQ-BRANCH trio | **The false attribution is corrected in plan-069**, both amendments are now explicitly that plan's to own, and they are added to **Issue 3.3's checklist** and **SC12's Verification**. This is pass-2 C6's escape recurring *in the destination's text* — which is exactly why 3.3 verifies before 3.2 publishes |
| C7 | medium | **Issue 0.4 specified L2's in-place semantics; no issue implements or tests them.** Measured, L2 is where in-place bites: it runs `git checkout <target>` in `ctx.root`, which under in-place *is* the execute checkout. SC9c/2.6 only checks SPEC↔implementation agreement, trivially true if neither changes | 0.4 **narrowed to L1**, with L2's measured in-place behaviour recorded as a **declared scope boundary** routed to plan-069 — rather than specified-then-unimplemented |
| C8 | medium | **The REQ id budget is miscounted again, in the issue whose job is to count it.** 0.2 said "three new ids" but counted an *amendment* as an allocation — only two are new. Issue 0.6's dirty-tree refusal class still has **no id anywhere**, precisely pass-2 C4's finding one issue over | 0.2 rewritten: **two new ids** (037, 038) plus named amendments consuming no number, and an explicit decision required on whether 0.6's refusal class is a new id or a clause inside `REQ-BRANCH-002`, with Gate 1's alternation to match |
| C9 | low | `REQ-LAND-004` was never written in full, so `plan_extract.py`'s `reqs` list omitted it and SC9b was not mechanically checkable for it | Every id now spelled in full at least once — `reqs` extraction confirms all twelve |

## Missing (all closed)

- **REQ-LAND-031's L18 seam-exemption** — the plan carried "L18 needs no work" (a *fix* claim) but never the *exemption* claim that Issues 0.3/1.3 collide with. Now stated in 0.3.
- **SC9's evaluation point** — now pinned by the merge-aware form rather than left to when it happens to be read.
- **What `_validate_merged` does inside 2.5's sandbox** — now an explicit decision in 2.5 and 1.5.

## Gate Assessment

| Gate | Run literally | Verdict |
| :-- | :-- | :-- |
| Start (human) | n/a | correct |
| REQ ids are free | zsh + bash, 5 cases on macOS | **Sound.** `MISSING:` echo works, `exit 1` scopes correctly. Weakened only by C8's budget mismatch, now fixed |
| Baseline suite green | verified twice previously | ONE-SHOT marking correct |
| Publish upstream corrections | empty Test + `human` + `consent` | Correctly modeled |
| Reconcile | auto | standard |

*"No gate depends on evidence its `Blocks` set produces; no cycles; no frontloading misses."*

## Upstream Assessment

Unchanged and still sound. The one upstream-facing defect was **C6's false cross-reference inside
plan-069** — Issue 3.2 would have published a pointer at a bundle misstating what plan-068 did.
Corrected.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 helper set six not three | high | Verified by independent AST closure; 0.3 now mandates an AST-derived `LAND_CTXLESS_HELPERS` constant + the REQ-LAND-031 carve-out + per-helper class | `main-session` | `resolved` |
| C2 1.3's check was a wish | medium-high | Resolved by C1's constant; 1.3 reads it, a test pins it to SPEC | `main-session` | `resolved` |
| C3 SC9 green-by-construction | high | Merge-aware + INCONCLUSIVE-on-empty; re-verified across 7 cases incl. violating-branch-merged-to-main → 1 | `main-session` | `resolved` |
| C4 rehearsal stubs five | high | 1.5 re-scoped to five; SC3 covers any `pm.*` monkeypatch; "zero-stub" phrasing retired | `main-session` | `resolved` |
| C5 runner contract unspecified | medium-high | 2.5 states pass-through-`git` + argv-recognising fakes that fail on unrecognised argv | `main-session` | `resolved` |
| C6 fourth dropped item + false claim | high | plan-069's false attribution corrected; both amendments owned there; added to 3.3 and SC12 | `main-session` | `resolved` |
| C7 L2 specified but unimplemented | medium | 0.4 narrowed to L1; L2 in-place recorded as a declared boundary routed to plan-069 | `main-session` | `resolved` |
| C8 id budget miscounted again | medium | Two new ids + named amendments; explicit decision on 0.6's refusal class | `main-session` | `resolved` |
| C9 REQ-LAND-004 not spelled in full | low | All ids spelled in full; `reqs` extraction confirms twelve | `main-session` | `resolved` |

**Final status: all concerns resolved.** Re-verified — 5 epics, 23 issues, 5 gates, 16 criteria,
9 risks, zero `unparsed`, zero dangling, zero cycles, zero undischarged.

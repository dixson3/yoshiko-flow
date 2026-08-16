---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
verdict: REVISE
status: resolved
---

# Review pass 2 — adversarial (red-team), post-split

## Verdict: REVISE

1 high, 5 medium, 4 low, plus 4 missing items.

Cycle 2 reviews the **split** plan (pass-1 C10). The reviewer verified each pass-1
resolution landed in `plan.md` rather than merely being asserted in the resolutions table —
and caught one that had not (C18).

## Strengths (verbatim)

- **The split is real, not cosmetic.** Every `depends-on` edge resolves to a node that still
  exists; **zero residual Epic-2 edges** — C3 is genuinely closed, not asserted.
- **C1 genuinely relocated, with the decision recorded.** plan-042 `D-C1` carries the
  operator's split-the-halves ruling verbatim, including the `install.rs:304-331`
  `confirmation_required` reuse. Nothing was quietly dropped.
- **C2's new gate is correct and reachable.** Condition = Issue 1.2 green; `Blocks` =
  {4.1a, 4.4}; 1.2 is **not** in the Blocks set, so no cycle. The both-directions argument
  holds under inspection. *"Unusually well-reasoned gate discrimination."*
- **C4/C6 premises independently re-verified.** 40 `__pycache__`/`.pyc` entries (exact
  match); `.gitignore:11-12` exactly as cited; CI is a clean build, so C6's correction is
  right. `embed.rs` carries **three** exclude attributes, so the exclude-set guard is
  warranted.
- **C5, C6, C7 landed in the plan body**, not just the resolutions table.
- **Not too thin.** 11 issues, 2 SPEC items, a cargo feature, a CI job, 4 doc corrections,
  an upstream correction post. *"This is a plan, not a ticket."*

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C11 | **Epic 0 amends a requirement that does not contain what the plan says it contains.** `REQ-YF-PRE-009` (`SPEC.md:634-646`) is entirely about the preflight **self-update offer**; `grep -n "rerun-if\|build\.rs" SPEC.md` returns **nothing**. The "deliberately emit NO rerun-if-changed" stance lives only in the `build.rs:51-58` *comment*, which cites PRE-009 because narrowing would break `YF_GIT_DIRTY`, which PRE-009 consumes. The plan promoted a code comment into a SPEC requirement. Consequences: 0.5 as written produces a wrong SPEC edit; the plan's **one new testable behavior** (SC1) lands with **no `REQ-*` id at all**, so Issue 1.2 is a tagged test with nothing to tag — violating `AGENTS.md`'s SPEC-first rule; and SC6 cannot be satisfied honestly. | **high** |
| C12 | **SC3 contradicts R2a's own mitigation.** SC3 makes "no rebuild tax on a `__pycache__`-only cycle" a hard success criterion, while R2a permits "if the directory form wins anyway, document the tax". Both cannot hold — and the directory form is the likelier outcome, since `rerun-if-changed` has no exclude mechanism. A contradiction introduced by the C4 fix. | medium |
| C13 | **The Capability Gate's test is never shown RED before the fix.** `1.2 depends-on 1.1`, so the test is authored after the fix and only ever observed passing. A test green because it does not exercise the addition path is indistinguishable from one green because the fix works — the C2 failure mode one level up. The plan shows it understands the trap ("a content-edit test would pass even with the bug present") but does not close it. | medium |
| C14 | **The Objective's headline sentence still carries the C5 overclaim.** The walk-back landed in §1's "Honest coverage claim", but the opening sentence still promises the git stamp matches "for every caller, including CI". That is the universal claim C5 refuted, and it is what a cold reader quotes and Issue 4.4 paraphrases upstream. | medium |
| C15 | **Stale artifacts the split left behind (aggregate).** `index.md`'s summary still describes the moved sync deliverable — the first thing a cold reader sees. `log.md` has no entry for the split and `status:` was still `review`. The Experiments table justifies E1/E4 in the present tense against decisions that left ("D3/D4. The plan proposes wiring a full sync…"). The E4 findings block's headline verdict and "Corroborates D6" both concern moved decisions; only its final paragraph still serves this plan. | medium |
| C16 | **Decisions got a MOVED pointer; epics, issues and risks did not.** Epics jump 0→1→3→4; risks run R2, R2a, R3, R5, R7, R9 with R1/R4/R6/R8 silently gone. A reader cannot distinguish "moved to plan-042" from "lost in editing" — the exact anxiety the D-row prevents. Also: Approach says "Three workstreams" above four epic headings. | low |
| C17 | **Nothing owns `AGENTS.md` between the two plans.** Both rewrite the same section. If plan-042 stalls, `AGENTS.md` rests with step 0 gone (correct) and the three-command ritual still documented as mandatory (still true, since 041 changes no behavior). That is a *coherent* resting state — which is what makes the split safe — but it is unstated and no risk records the editing collision. | low |
| C18 | **M3's resolution did not land.** pass-1 marks it `resolved — falsifier recorded in the E2 block`, but `grep -rn "falsif"` across the bundle hits **only `reviews/pass-1.md``**. A resolution row asserting something the plan does not contain is the failure mode this cycle exists to catch. | low |
| C19 | **Issue 1.1's dependency on 1.2a is over-constrained.** The 1.5 edge is load-bearing (1.5 selects the form 1.1 implements); the 1.2a edge is not — it spikes a *test* mechanism, and 1.2 already depends on 1.1. This holds the two-line measured fix behind a spike it does not need, in a plan whose whole justification for splitting was "do not hold a two-line fix behind unrelated work". | low |

## Missing

- **No `REQ-*` id for the plan's one new testable behavior** (C11). The plan's only true
  SPEC-first gap.
- **No note that `yf/profiles/` — the second `rust-embed` root — has the same addition blind
  spot**, and is incidentally fixed by the `rerun-if-changed=.` line. Free coverage the plan
  does not claim.
- **`REQ-YF-EMBED-003` says the check runs across the whole `skills/` tree** (on disk);
  Issue 3.2 reframes it as asserting against the *baked* tree. Issue 0.4 should cover whether
  EMBED-003's wording needs adjusting too, not just EMBED-001/-002.
- **plan-042's `findings/` and `references/` are empty** while its Investigation Findings
  cites E1/E4 by cross-bundle path — a portability regression the split created. Not
  plan-041's defect; flagged so plan-042 catches it at intake.

## Gate Assessment

- **Start Gate (human):** appropriate.
- **Capability Gate:** *"structurally sound and materially improved."* Reachable, no cycle,
  correctly gates the two outward-facing assertion issues rather than the evidence-producing
  one, and the Instructions are accurate against the code. Two residuals: the condition is
  only ever observed green (C13), and the `Blocks` set is now narrow enough that the gate
  protects *claims* rather than *artifacts* — acceptable given the plan changes no behavior,
  but worth stating so a reader does not expect pass-1's stronger guarantee.
- **Reconcile Gate:** fine.

## Upstream Assessment

- **#137 (include):** C3's objection is genuinely dead — `4.1a depends-on 1.1` only, so
  Epic 1 plus the doc truth-up closes #137 with no plan-042 dependency.
- **#41 (exclude):** unchanged, still justified; the cross-reference survived the narrowing.
- **Coarse-granularity convention:** satisfied — #137 tracks plan-041, plan-042 carries its
  own `_to file_` row. The pass-1 "invisible upstream" gap is closed by construction.
- **Caveat:** #137's body proposes three directions and the plan refutes its root-cause
  analysis. **Issue 4.4 must post before or with the close**, or the issue closes carrying an
  analysis this plan proved wrong. Currently 4.4 and the resolution both hang off 1.1 with no
  ordering between them.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C11 | Epic 0 amends the wrong requirement; new behavior has no REQ id | high | **Accepted; independently verified** (`REQ-YF-PRE-009` at `SPEC.md:634-646` is the self-update offer; `grep "rerun-if\|build.rs" SPEC.md` → none). Epic 0 restructured: new **Issue 0.6** adds `REQ-YF-EMBED-004` *(testable)* — a build observes additions under `skills/` — as the id Issue 1.2 tags and the gate proves. Issue 0.5 retargeted to PRE-009's actual **constraint** (the dirty-flag probe must stay accurate, which is why D2's second line is load-bearing) plus a living-amendment-log entry. The "emit NO rerun-if-changed" supersession restated as a `build.rs` **comment** rewrite under Issue 1.1. Correction propagated to Scope, D2, R2. | resolved |
| C12 | SC3 contradicts R2a | medium | Accepted. SC3 made conditional on Issue 1.5's outcome: either no rebuild tax, **or** the tax is measured and documented. | resolved |
| C13 | Gate test never shown RED pre-fix | medium | Accepted. Issue 1.2's acceptance now requires demonstrating the test **red** against the pre-fix `build.rs` before accepting it green; referenced from the gate Instructions. | resolved |
| C14 | Objective headline still overclaims | medium | Accepted. Opening sentence qualified in place. | resolved |
| C15 | Stale index.md / log.md / Experiments / E4 block | medium | Accepted. `index.md` summary refreshed; `log.md` gains a split entry; E1/E4 Experiments rows re-worded to past tense with a plan-042 pointer; a scope banner added atop the E4 findings block. | resolved |
| C16 | No MOVED pointer for epics/risks | low | Accepted. Epic 2 MOVED stub added; risk table gains an `R1, R4, R6, R8 → plan-042` row; "Three workstreams" reconciled. | resolved |
| C17 | AGENTS.md ownership between plans | low | Accepted. One sentence added to Issue 4.1a recording the coherent resting state and the ordering. | resolved |
| C18 | M3 resolution did not land | low | Accepted — the catch is correct. Falsifier line added to the E2 findings block. | resolved |
| C19 | 1.1 over-constrained on 1.2a | low | Accepted. `1.2a` dropped from Issue 1.1's `depends-on`; `1.2a → 1.2` retained. | resolved |
| M-a | No REQ id for the new behavior | high | Resolved by C11's Issue 0.6. | resolved |
| M-b | `yf/profiles/` has the same blind spot | low | Accepted — noted in Issue 0.5 and Objective §1 as incidental free coverage. | resolved |
| M-c | `REQ-YF-EMBED-003` wording vs baked tree | low | Accepted — Issue 0.4 extended to cover EMBED-003. | resolved |
| M-d | plan-042 `findings/`/`references/` empty | low | Not plan-041's defect. Recorded in plan-042's Open Questions for its intake audit. | resolved |
| U-a | Issue 4.4 must post before/with the #137 close | medium | Accepted. Ordering made explicit in Issue 4.4 and in the Upstream Issues row. | resolved |

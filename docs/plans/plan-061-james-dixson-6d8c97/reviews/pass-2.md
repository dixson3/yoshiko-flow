---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 2 on plan-061 — verdict REVISE with 8 concerns, 2 high. Verified pass 1''s ten resolutions (nine held, C7 was prose-only), upheld the main session''s rejection of C5, and found that neither capability gate declared test_class/cwd so neither would ever have run.'
---
# Review pass 2 — adversarial (red-team)

## Verdict: REVISE

**all 8 concerns resolved by the main session**
**Dispatched:** fresh sub-agent (REQ-AGENT-049), read-only w.r.t. the repository.
**Date:** 2026-08-30

## Part A — verification of pass 1's ten resolutions

**Nine held. One (C7) was prose-only and did not land.** C1, C2, C3, C4, C6, C8, C9, C10 all
verified by command. `audit` exit 0; `recheck-criteria` `total 12, class_a 10, evaluated 10`
with SC9/SC10 correctly `manual`.

**C5 — the main session's rejection was UPHELD, verified independently.** `coordinator.md:179`
reserves INCONCLUSIVE for an *absent or manual* test; `:183` maps non-zero to FAIL; `SKILL.md:1284`
confirms a failed gate narrows the runnable set without stopping the run. A guard returning exit 2
would still read FAIL. Pass 1's recommendation was **unimplementable as stated**, and fixing the
`Instructions:` was the correct remedy. *(The replacement prose was nonetheless wrong for a
different reason — C11.)*

**DAG verified:** 29 issues, no cycle, no dangling referent, every issue reachable from the start
gate. **SPEC-first is enforced by EDGES, not only prose** — `1.1 ← 0.3` and `4.1 ← 0.3` mean
nothing in Epics 1 or 4 can begin before the amendment log lands. Pass 2 calls this the plan's
strongest structural feature. The `2.3 ← 3.4` edge is **safe, no deadlock**: the gate's Condition
is discharged by Issue 1.5 in the *unblocked* Epic 1, so both epics release together.

## Concerns

| # | Severity | Concern | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| C11 | high | **Neither capability gate declared `test_class` or `cwd`, so neither would ever run.** Absent `test_class`, `coordinator.md:179` reads `manual` → INCONCLUSIVE, and §5.2c runs only the `probe` class — so the sweep executes neither test. Gate 1's Instructions claiming it "reports FAIL" were therefore factually wrong. Absent `cwd` is worse: under worktree mode Epic 4 edits READMEs in the worktree while a `repo-root` evaluation greps the primary checkout, which still has all 25 hits — **Gate 2 could never go green, permanently blocking 5.1 and the whole Epic 5 tail.** | **RESOLVED.** Both gates now carry `test_class: probe` and `cwd: worktree`. `plan-058`'s grammar-gap admonition copied verbatim into `## Gates`: `plan_extract.py` drops these lines, so the executing session **must** set all four as bead metadata at the §5.2a pour. Gate 1's Instructions corrected. | `main-session` | `resolved` |
| C12 | high | **C7 was resolved in prose only — the `depends-on: 3.4` edge was never added.** Issue 2.3's only edge was `← 2.2`. With the gate releasing both epics simultaneously, 2.1→2.4 could complete before 3.4 authored the 20th README, and 2.4 would pass **vacuously** because that README did not yet exist. | **RESOLVED.** `- depends-on: 2.2, 3.4`, verified in the extracted DAG (29 → 32 edges). **This was a main-session error, not a red-team miss:** the pass-1 edit targeted `depends-on:` where the file has `- depends-on:`, so the replace silently no-opped and the concern was reported resolved when it was not. | `main-session` | `resolved` |
| C13 | medium-high | **Issue 4.2 had no `depends-on` at all** — an artefact of the C3 fix: inserting 4.2b absorbed the `- depends-on: 4.1` line belonging to 4.2. The *largest* repair (17 READMEs) was ready at start-gate open and could be dispatched before 4.1 decided what the correct Install text is. `5.5` was likewise dependency-free and could post outcome comments before any work landed. | **RESOLVED.** `4.2 ← 4.1`, `5.5 ← 5.4`. Only `0.1` and `0.2` now lack a predecessor, both legitimate Epic-0 roots. Also a main-session error from the same edit. | `main-session` | `resolved` |
| C14 | medium-high | **One of the four declared edges silently left unenforced.** `plan.md:50` names all four and says *"Nothing runs them"*; Issue 1.2 implements three plus existence. `e-readme-desc` is nowhere carved out, and `exp-003`'s own INCONCLUSIVE rating (spot-checked 3/20) was not carried into the plan. An ungated, unnamed surface (#252). | **RESOLVED.** Issue 1.2 now states the carve explicitly: `e-readme-desc` is the one HYBRID edge, its `intent` predicate tolerates paraphrase and is not mechanically decidable, it keeps its LLM route, and `exp-003` rated it INCONCLUSIVE on a 3/20 sample — so the plan neither enforces nor claims it. | `main-session` | `resolved` |
| C15 | medium | **SC2b under-matched — the same defect class as C3, on a criterion pass 1 never tested.** The trailing space missed every backtick-terminated instance: `yf-beads-upstream/README.md:31,35` and `yf-incubator/README.md:28` — the most prominent sentence in each. 3.1/3.2 could have repaired only space-followed lines while SC2b went green. | **RESOLVED.** Anchored on a word boundary: `(^\|[^-a-z])/(beads-upstream\|incubator)\b`. Measured **8 → 11** matches, now including the backtick forms. 3.3 dropped from Discharged-by (`yf-skill-authoring` teaches neither). | `main-session` | `resolved` |
| C16 | medium | **Gate 1's Condition was stronger than its Test, and the failure-class vocabulary was unpinned.** Condition said "18 **layout** failures"; the Test asserted `failures\|length>=18` — the **total**, satisfiable by 14 layout + 9 others. And SC4 selects `class=="fence-unparseable"` and passes when empty, so a checker that never emits that class satisfies it **vacuously** — the very class this plan exists to close. | **RESOLVED.** Test tightened to `[.failures[]\|select(.class=="layout")]\|length>=18`. Issue 0.2 now pins a **closed enum** (`layout \| prereqs \| usage \| missing-readme \| fence-unparseable`), and Issue 1.4 gains a planted-unparseable-fence test so the class cannot be one the checker never emits. | `main-session` | `resolved` |
| C17 | low-medium | **SC11 grepped a magic string no issue promised to write** (`mechanical subset`). | **RESOLVED.** Issue 5.3 now requires the literal phrase. | `main-session` | `resolved` |
| C18 | low | **SC5 and Gate 2 were two spellings of one condition** — SC5 omitted the `` `install.(sh\|py)` `` alternative, matching 19 files where the gate matched 25. SC5 could go green while the gate was red. | **RESOLVED.** Made byte-identical; both now measure **25**. | `main-session` | `resolved` |

## Missing (all addressed)

- **R1's mitigation cell was stale** — credited only 1.1/1.5. Now names all three layers, including
  Issue 0.2b, and states why each of the first two was individually insufficient.
- **Epic 4 is backfill and is ungated.** Pass 2 checked and confirmed this is *safe*: Epic 4 edits
  Install prose only, adding and removing no files, so it cannot perturb the quantities Gate 1
  measures. Now stated in Gate 1's Instructions rather than left to be re-derived.
- **Nothing established `jq`.** A missing `jq` exits 127 → FAIL, indistinguishable from a red
  checker. Gate 1's Instructions now say to confirm `command -v jq` before trusting a red verdict.

## Gate Assessment

| Gate | Reachable | Verdict |
| :-- | :-- | :-- |
| Start Gate (human) | yes | Fine. |
| Capability: checker is sensitive | **yes, after C11/C16** | Test sound (C1 verified), placement right, Condition now matches Test, metadata declared. |
| Capability: no install.sh reference | **yes, after C11** | 25 → 0 reachable; correctly excludes archived bundles; `cwd: worktree` closes the address-space hazard. |
| Reconcile Gate | yes | Standard. |

## Upstream Assessment

Sound and unchanged. Pass 1's caution — *"do not close a partial on a gate that cannot go green"* —
is now satisfied in both address spaces. Remaining `Resolved By: TBD` cells are an `audit` `W` and
are filled at reconcile, per the normal lifecycle.

## Residual, recorded rather than fixed

`skills/yf-beads-upstream/README.md:35` documents backends as `github|gitlab|jira|none`. `exp-001`
measured that **GitLab and Jira were removed at plan-040** (REQ-BUP-040) — the same stale claim
found in three web pages. It is a **content** defect on the README axis, not one of the four
declared edges, so repairing it here would be scope creep. **Routed to #317**, which already owns
the three web copies of the identical fact.

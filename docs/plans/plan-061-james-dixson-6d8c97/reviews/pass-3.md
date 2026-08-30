---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 3 on plan-061 — verdict REVISE with 4 medium concerns, all textual. Verified 8 of 8 of pass 2 resolutions, cleared the worktree address-space question, and found that Gate 2 forbade a TRUE sentence about the hosted vendor installer.'
---
# Review pass 3 — adversarial (red-team)

## Verdict: REVISE

**all 4 concerns resolved by the main session**
**Date:** 2026-08-30

## Part A — pass 2's eight resolutions: **8 of 8 verified by command**

C11-C18 all held. The `## Gates` grammar-gap admonition was cross-checked against `plan-058`'s
and judged **better than its model** — it adds the consequence chain (`manual` → §5.2c runs none
→ INCONCLUSIVE forever) that plan-058's omits. C12 and C13 verified **in the extracted DAG**, not
prose. `audit` exit 0; `recheck-criteria` `class_a 10, evaluated 10`, SC9/SC10 `manual`.

Issue 0.2b's precedent was re-measured rather than assumed:
`check_okf_index_drift.py --min-roots 999` → `verdict inconclusive, exit 2`. **The precedent is real.**

## Part B — what two passes had not examined

**B1 — the worktree address space is NOT a hazard. Traced and cleared.** `SKILL.md:1531-1646`
fixes the order §6.1 merge → §6.1.5 validate → §6.2 push → §6.3 reconcile → §6.4
`recheck-criteria`. Every criterion is evaluated **primary-side after the merge-back**, so both
branches are safe: if 1.5 writes `findings/` primary-side, SC1 sees it; if a sub-agent writes it
worktree-side, the `--no-ff` merge lands it first. **There is no address space in which SC1 is red
in one and green in the other.**

**B3 — pass 2's Epic-4 safety claim VERIFIED TRUE** against all four edge definitions
(`DRIFT-CHECK.md:158-161`). An Install section lies outside every section `e-readme-layout`,
`e-readme-prereqs` and `e-readme-usage` read. Gate 1 correctly does not block `epic:4`.

## Concerns

| # | Severity | Concern | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| C19 | medium | **SC1 asserts `findings/exp-005-checker-red-run.md`, and `grep -rn 'exp-005'` over the whole bundle returned exactly one hit — SC1 itself.** Issue 1.5 promised only "into `findings/`". A differently-named file leaves SC1 FALSE forever, and `recheck-criteria` **halts** the §6.4 chain. C17's exact defect class; the pass-2 fix was applied to SC11 only. | **RESOLVED.** Issue 1.5 now names the literal path and states why — same parenthetical shape Issue 5.3 uses for `mechanical subset`. | `main-session` | `resolved` |
| C20 | medium | **Gate 2 forbade a TRUE sentence, so it was not green-reachable.** Enumerated for the first time (three passes counted 25 but never listed them): `README.md:42` — *"The hosted `install.sh` is a byte-for-byte mirror of cargo-dist's `yf-installer.sh`"* — matches solely via the backticked filename while **correctly describing the hosted vendor installer**, which Gate 2's own Instructions call legitimate. Gate 2 blocks 5.1, so Epic 5 would stall on a correct statement. Separately `DRIFT-CHECK.md:164` is a **third** manifest hit, in §3's `e-frontmatter` contract, assigned to no issue and to neither side of R6. | **RESOLVED.** New **Issue 4.5** authorizes the `README.md:42` reword (nothing is lost — `:39` already names the file in the install URL). Issue 4.3 extended to `:164,219,225` and now explains that `:164` defines an edge's source of truth as *"the frontmatter `install.py` actually reads"* — a file deleted at plan-010. R6 amended to cover §3. | `main-session` | `resolved` |
| C21 | medium | **Issue 4.2b understated its population by five files** — it named `skills/yf-okf/SKILL.md`; measured, **6 SKILL.md files carry 13 lines**. Approach step 4 omitted the SKILL.md population entirely. | **RESOLVED.** 4.2b now enumerates all six with line numbers and records that all 13 are preflight/rules-install prose (never invocation lines), which is *why* Epic 4 stays safe unblocked. Approach step 4 corrected. | `main-session` | `resolved` |
| C22 | medium | **The plan's own bundle was the sole cause of the repo's FULL tier being red** — Issue 5.4's gate. `check_okf_index_drift.py` reported `bundles_checked: 66, drifting: 1`, this bundle, `missing: 14`. `index.md` also still carried the **pre-split combined-scope** description, superseded at `plan.md:22-34`. | **RESOLVED.** `index.md` blockquote replaced with the Plan-1 scope and its sibling trackers; bundle reindexed. `drifting: 0` across all 66. Heeding the check's own warning that `reindex --write` satisfies the gate with bare bullets, every member carries a real description — including three that were **silently truncated at a `#` and an unquoted YAML colon**, now quoted and repaired. | `main-session` | `resolved` |

## Non-blocking notes (accepted)

- SC2's Discharged-by gains **3.4**, the issue that actually makes the 20-skill enumeration pass.
- `audit` emits 13 `R1b` warns (issues named by no criterion); all `W`, all covered transitively.

## Gate Assessment

| Gate | Reachable | Verdict |
| :-- | :-- | :-- |
| Start Gate | yes | Fine. |
| Capability: checker is sensitive | **yes** | *"Nothing further."* Test red today for the right reason; `jq` present; Condition matches Test; metadata declared; epic:4 exemption independently verified against all four edge definitions. |
| Capability: no install.sh reference | **yes, after C20** | Placement, `cwd`, and the archived-bundle exclusion were already correct; the defect was the unenumerated path set. |
| Reconcile Gate | yes | Standard. |

**Premise check.** The premise tested this pass — *"the 25 files Gate 2 matches are all defects"* —
was an **inference**, and it was **falsified**: at least one is a correct statement. Pass 1
established the enumerate-don't-count discipline in C3; pass 2 applied it to *counts* but never to
the *hit list*. **That is the one place three passes consistently stopped one step short**, and it
is the most transferable lesson in this review series.

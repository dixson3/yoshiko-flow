---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: Red-team pass 3 — verdict REVISE, 12 concerns (2 high); 15 of 17 pass-2 resolutions verified genuine
---

# Red-team pass 3

## Verdict: REVISE
## Resolution verification — pass 2's 17 concerns vs current text

| # | Claimed | **Actual** |
| :-- | :-- | :-- |
| H1 | resolved | **genuinely-fixed** — all 10 cargo-guard criteria carry `0.8` |
| H2 | resolved | **genuinely-fixed** — `0.8` at 11 dependent sites |
| H3 | resolved | **genuinely-fixed (structure), defect left in prose** — `5.2a ∈ ancestors(5.2)`, but see N1 |
| H4 | resolved | **fixed-but-introduced-a-new-defect** — 5.2's body is right; **R9 still asserts the refuted design** (N1) |
| H5 | resolved | **genuinely-fixed** — 0.3 four outcomes, 5.1 schema carries `undetermined`, test renamed |
| H6 | resolved | **genuinely-fixed** (residue: 3.2 and 4.3 unannotated — N10) |
| H7 | resolved | **genuinely-fixed** |
| H8 | resolved | **genuinely-fixed** — ordering verified `0.8 ∈ anc(5.1) ∈ anc(5.2)` |
| M1 | resolved | **genuinely-fixed** |
| M2 | resolved | **genuinely-fixed in prose — and it is what causes N2** |
| M3 | resolved | **genuinely-fixed** |
| M4 | resolved | **partially-fixed** — same class survives one node higher at 5.3 (N3) |
| M5 | resolved | **partially-fixed — THIRD recurrence, one issue over each time** (N4) |
| M6 | resolved | **genuinely-fixed** |
| M7 | resolved | **genuinely-fixed, EXP-007 used honestly** — but the finding is unregistered (N6) |
| L1 | resolved | **partially-fixed** — runbook inline, but the `context.md` pointer is dangling (N5) |
| L2 | resolved | **genuinely-fixed** |

## Strengths

- **The 5.2/5.2a inversion is genuinely repaired and machine-verifiable** — 37 issues, zero dangling
  referents, zero cycles.
- **Issue 5.2's body is now the strongest paragraph in the plan** — it quotes the measurement that
  makes pre-move verification impossible *by construction*, rather than asserting an ordering.
- **EXP-007 is a model finding** — it grades `not measured` explicitly, notes the known symlink sits
  in the *shared* root and is out of delete scope, and recommends *against* upgrading EXP-004's
  `inferred` grade wholesale. 1.1 re-measures rather than inheriting.
- **Every one of the seven new scripts has a named authoring issue**, each with a failable exit
  contract. 4.3's `--case` exit-2 contract closes the last vacuity route from C1.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| N1 | **high** | **R9's mitigation still asserts the design H4 refuted.** Line 292 reads *"5.2 is restructured to drive-verify BEFORE removing"* while 5.2's body says in bold that verifying first is *impossible*. The plan contradicts itself on its highest-severity migration risk, and the stale half is what a reviewer reads first — the fix landed in the issue and never propagated to the risk table |
| N2 | **high** | **0.8's "promotion" is copy-or-move-unspecified, and BOTH readings are defective.** plan-054's `plan.md` references `assets/checks/` at **34 lines**. **MOVE** → 34 criteria in a completed plan become unrunnable and 0.8 violates the bundle-as-record principle it invokes. **COPY** → two copies of `check-harness-smoke.sh`, Epic 4 rewrites one, divergence with nothing reporting it. Also `CHANGE-VALIDATION.md:51` points at the old path and 0.8's body never says it updates it, though R10 claims it does |
| N3 | medium | **5.3 runs the FULL tier over a tree that need not contain 2.3, 2.4, 4.4, 0.6 or 0.7.** M4's defect one node higher: SC19 can close before the NameTransform drop, the `harness_cross_e2e` update, the smoke's absent-path fix, and the amendment log |
| N4 | medium | **Issue 0.4 names no `REQ-*` id** — the same defect C8 fixed in 0.3 and M5 fixed in 0.5, now on its **third recurrence, one issue over each time**. 0.7's derivation is structurally blind to it |
| N5 | medium | **L1's runbook points at `context.md`, which does not contain it.** The substance survives inline, so a dangling cross-reference rather than a lost fix — but it is the recorded-but-absent pattern in the artifact that exists for cold readers |
| N6 | medium | **EXP-007 is invisible to a cold reader.** `plan.md:100` still says "All six experiments returned", the findings table has six rows, and `index.md` says "EXP-001 … EXP-006". Issue 1.1 is the only reference, citing a finding the reader has not been told exists |
| N7 | medium | **Nothing deploys the built binary, and a routine land-the-plane sync mid-execution CREATES R3's divergence.** Between Epic 2 landing and 5.2's quarantine, an operator running `yf self install --from-build --build` — which `AGENTS.md` names as the **default** land-the-plane step — writes only `.agents` and `.claude`, leaving the two private trees stale and divergent. The repo's own standard ritual manufactures the exact hazard R3 describes |
| N8 | medium | **Epic 4 is nine issues (24% of the plan) and five criteria delivering a script no recipe invokes** — by the plan's own Deferred table. Its only automated exercise is a harness driving *seeded* states; the live path is blocked on 4.7, which is out of scope. **Explicitly flagged as the operator's judgement call, not the reviewer's** |
| N9 | low | **SC2 is the one filtered `cargo test` that skips the guard** this plan built for exactly that. Not vacuous today, but 2.1 refactors that very table and a rename would turn it green-on-nothing |
| N10 | low | 3.2 (#238) and 4.3 (#256) are listed as resolvers with no `resolves-upstream:` annotation — under-annotation, harmless direction |
| N11 | low | **SC17 does not discriminate the change from a bare `rm -rf`.** codex resolves to the shared root today; pi and opencode do so as soon as the private trees are gone, with or without the descriptor collapse |
| N12 | low | **0.7 is heavy ceremony for a three-element set**, and its `cited-not-touched` exclusion list is hand-authored — the property it exists to remove from the loop |

## Missing

1. A `Verification`-layer statement of 0.8's copy-vs-move semantics — no criterion asserts plan-054's bundle is intact after 0.8, so the destructive reading is undetectable (N2).
2. An EXP-007 row in the findings table and a corrected count in `index.md` (N6).
3. A deploy step before 5.2's drive-verify, and a prohibition on a bare `yf self install` between Epic 2 and 5.2 (N7).
4. The abandonment runbook in `context.md`, which the Deferred table already claims is there (N5).
5. A sentence in R1 covering "the gate blocks on an unjudgeable directory nobody has looked for."

## Gate Assessment

| Gate | Reachable? | Assessment |
| :-- | :-- | :-- |
| Start Gate | n/a | Standard |
| live-harness drivability | Yes | M6 fixed — `Blocks: 5.2` only, SC13b reachable |
| migration apply | **Yes — regression repaired** | `check-migration-dryrun.sh` authored by 0.8; ordering verified. The 2-vs-1 exit split, empty-`delete` failure and `undetermined` clause are all backed by a declared schema. **The strongest gate in the plan** |
| Reconcile Gate | Yes | 5.4 fixed; residual under-specification moved to 5.3 (N3) |

**The gate layer recovered fully.** Pass 2 recorded a regression; that is no longer true. Both capability gates sit at their earliest legal position; no frontloading miss.

## Findings inheritance

**No inferred claim is treated as measured.** EXP-007 does not over-claim and the plan does not over-read it. D-4/R5, D-7/L2 and R4 all carry their `inferred` grades forward correctly.

**One residual asymmetry worth knowing:** `yf harness skills status` is name-keyed against the embedded set, so EXP-007's 76/76 covers only the 19 embedded skills per root. It is **structurally incapable** of seeing a foreign or unjudgeable directory — which is the whole reason Epic 1 exists. The finding says this; 1.1's body does not repeat it, and a reader seeing only "76 of 76 classify ok" could conclude more than was measured.

## Upstream Assessment

| Issue | Verdict |
| :-- | :-- |
| #257 | Sound |
| #238 | **Fixed** — annotations now `(partial)`; the IN/OUT note is the best-written cell in the plan |
| #239 | **Fixed** — "ships VISIBILITY, not COVERAGE" is honest |
| #256 | Consistent, **but the disposition is now questionable** — what ships is a state vocabulary for a script no recipe invokes (N8). `partial` would be truthful |
| #121 / #243 / #240 / #255 | Sound |

## Recommendations

1. Rewrite R9's mitigation to match 5.2's actual design (N1).
2. State **COPY** explicitly in 0.8 and freeze plan-054's copies as a record (N2).
3. Add the missing 5.3 edges (N3).
4. Name 0.4's REQ id — and **sweep all of Epic 0 once** rather than patching the next instance next pass (N4).
5. Register EXP-007 in the findings table and `index.md` (N6).
6. Add a deploy step before 5.2 and prohibit a bare `self install` in the window (N7).
7. Operator decision on N8.

## Bottom line

> The structural work of pass 2 held — the DAG is right, the gates are reachable, the scripts are
> owned, and the vacuity class that dominated passes 1 and 2 is closed down to one low-severity
> instance. What remains is a **propagation failure** (R9 asserting the design 5.2 refutes) and an
> **unspecified semantics** (0.8's copy-vs-move) that a fourth pass should close in one editing
> session.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| N1 | high | R9's mitigation rewritten to match 5.2's actual design — quarantine-before-verify, with the EXP-002 measurements (pi 3/3, opencode 4/5) quoted as the reason, and the restore named as the undo | `main-session` | `resolved` |
| N2 | high | 0.8 now states **COPY, never move**, with both defective readings spelled out (a move breaks 34 criteria in plan-054 and violates the principle 0.8 invokes; a naive copy leaves two live copies). plan-054's `assets/checks/` is declared **frozen as a RECORD, not a live instrument**, so post-copy divergence is explicitly not the R3 class. 0.8 also repoints `CHANGE-VALIDATION.md:51` | `main-session` | `resolved` |
| N3 | medium | `5.3 depends-on: 5.2, 3.4, 2.5, 4.9, 4.6, 2.3, 2.4, 0.7` (4.4 dropped with D-14) | `main-session` | `resolved` |
| N4 | medium | 0.4 now names `REQ-YF-INSTALL-007`. **And the recurrence itself was addressed** — 0.6 now requires a one-pass sweep of all of Epic 0 confirming every issue names its id, because patching the next instance is what produced three recurrences across three passes | `main-session` | `resolved` |
| N5 | medium | The runbook is now genuinely in `context.md` as a **Recovery runbook (mid-execution abandonment)** section, with the restore → reinstall → verify sequence and the no-bare-`self install` prohibition | `main-session` | `resolved` |
| N6 | medium | EXP-007 registered: a findings-table row, "six"→"seven" in `plan.md` and `index.md`, and a "what the findings changed" bullet. **1.1 now carries the scope caveat** — `status` is name-keyed, so 76/76 speaks only to embedded skills and says nothing about the foreign/unjudgeable population Epic 1 exists to find | `main-session` | `resolved` |
| N7 | medium | New **Issue 5.1a** deploys the built binary before the drive-verify, and closes the window: no bare `yf self install` between Epic 2 and 5.2, because the repo's own default land-the-plane step would leave the private trees stale and divergent. New **SC17b** discharges it | `main-session` | `resolved` |
| N8 | medium | **OPERATOR DECISION — defer 4.1-4.5, keep 4.6/4.8/4.9.** Recorded as **D-14**. Plan drops from 38 issues / 26 criteria to **33 / 22** with no measured claim weakened. #256 re-dispositioned `include` → `partial` as a direct consequence. The deferred unit is recorded in the Deferred table alongside the re-add row it shares a blocker with | `operator` | `resolved` |
| N9 | low | SC2 routed through `check-cargo-test-ran.sh`; `0.8` added to its `Discharged-by`. It was the one filtered `cargo test` skipping the guard this plan built | `main-session` | `resolved` |
| N10 | low | `resolves-upstream: #238 (partial)` added to 3.2. 4.3's annotation is moot — the issue was deferred under D-14 | `main-session` | `resolved` |
| N11 | low | SC17 strengthened to require the resolved tree carry the **post-collapse** `SKILL_DIR_INSTALLED_AT` stamp, so it can no longer be satisfied by a bare `rm -rf` of two directories | `main-session` | `resolved` |
| N12 | low | 0.7 **kept**, with the reusability argument now stated in its body rather than left implicit. The hand-authored exclusion list is a real limitation and is named as such | `main-session` | `resolved` |

**All 12 concerns resolved. This file is now FROZEN.**

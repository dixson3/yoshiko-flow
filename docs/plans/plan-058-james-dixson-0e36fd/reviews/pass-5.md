---
type: Review
okf_spec: OKF-PLAN
id: pass-5
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Red-team pass 5 — plan-058-james-dixson-0e36fd
## Verdict: APPROVE

Dispatched as an isolated sub-agent (REQ-AGENT-049). Read-only with respect to the repository. One
sandbox spike built a **simulated post-Epic-1 `upstream.py`** — applying 1.1's row-based
`collect_parent_edges`, 1.2's deletion of `deps_for_show`, and 1.3's `external_from_row` swap, with
**1.7 deliberately not applied** — and **executed** an AST checker implementing the plan's rules
against both the live tree and that simulated tree. Residue removed. The main session wrote this file.

## Strengths

**The B1 fix is VERIFIED BY EXECUTION, not by reading.** The spike ran every rule against both trees:

| Source | (a) `bd dep list` | (b) | (c) | (d) | (e) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| live tree (pre-fix) | HIT `:1002`, `:1066` | HIT `:533`, `:615`, `:650` | HIT `:550` | clean | HIT `:615` |
| **post-Epic-1, no 1.7** | HIT `:990`, `:1054` | HIT `:638` | **clean** | **clean** | **clean** |

Rule (a) is the *only* rule that presupposes 1.7, it is now in Issue 3.1c, and Issue 3.1 carries the
explicit invariant. Rules (c), (d), (e) are **exactly green** on the post-Epic-1 tree — (c) because
1.2 deletes the `FunctionDef`, (e) because 1.3 removes the `:615` call leaving only the allow-listed
site, (d) because the three `subprocess.run` sites are precisely the allow-list.

**The decline path is independently confirmed.** Mechanical parse of all 39 issues: no dangling
`depends-on`, no cycles. The reverse-dependency closure of `{1.7, 3.1c}` is **exactly `{1.7, 3.1c}`**
— nothing else is stranded. Both close `wontfix-for-now`, so the `auto` Reconcile Gate **can fire**.
Every other issue, gate and criterion has a defined terminal state.

**B2-B7 all verified real.** Notably B4 — `grep -c REQ-HYG-` returns 26 (formerly vacuous) while the
new `"dry-run by default"` grep returns **0** today, so it is non-vacuous; and B5 — all eight
newly-named tests return 0 matches in the current suite, so every `-k` selector **fails loudly**
until its issue writes it, which is the safe direction.

**Final sweep clean.** SPEC-first holds (`1.1 <- 0.1/0.1b`, `2.1 <- 0.2`, `3.1 <- 0.3`,
`4.5 <- 4.4b`) — no implementation precedes its requirement. All six gates reachable with evidence
outside their own `Blocks` sets. **Destructive-act sweep: no destructive act is reachable without a
gate or a stated precondition** — `bd close -r` activation gated (1.7), pruning gated (4.5),
`.beads/backup` deletion gated (4.1d), cache-delete + stop/GC ungated but with a stated recovery
precondition and DR intact (4.1b), and Issue 1.9's re-run is `--apply`-free.

The `#268` critical-path closure is `{0.1, 0.1b, 0.2, 1.1, 1.3, 2.1}` — touching neither 1.7 nor any
Epic 4 issue. All 47 concerns across passes 1-4 carry `resolved`.

## Concerns

All **non-blocking**. Recorded rather than actioned as a new cycle, per the binding standard.

| # | Severity | Concern | Disposition |
| :-- | :-- | :-- | :-- |
| C1 | med | **Rule (b), as literally worded, is red on correct post-Epic-1 code at `cmd_mappings`.** Executed: its helper-mediated clause fires on the legitimate comprehension `[{"id": bid, "external": external_for(bid)} for bid in ids]` at `:650`/post-fix `:638`. Rule (e) carries a `cmd_mappings`/`plan_hoist` allow-list; rule (b) did not. **Non-blocking** because this is the exact failure Issue 3.1b's **positive control** exists to catch, and 3.1b lands *before* the gate is evaluated; it is branch-symmetric so it cannot reintroduce B1; and the correct resolution is already written in the plan's own text. | **FIXED** — the reviewer's one-line recommendation applied verbatim: rule (b) now exempts calls whose enclosing `FunctionDef` is on rule (e)'s allow-list |
| C2 | low | **SC8b claims two things but verifies only one** — the hygiene requirement and 0.4's SPEC §5 entries, with a command covering only the former. | **FIXED** — split into SC8b (hygiene, `4.4b`) and SC8c (§5 entries, `0.4`), each with its own command |
| C3 | low | Marking **SC3d** N/A under a decline is slightly imprecise — Issue 3.7's filing happens regardless, and the decline *is itself* the recorded reviewed decision the criterion describes. | Accepted as harmless; left as-is |
| C4 | low | Issue 4.1b's Dolt-GC test runs against the live store rather than a copy. The stated precondition gives a real recovery path and it is off the critical path; a copy-first framing would be strictly safer. | Recorded for execution-time judgement |
| C5 | low | **Pre-existing**: `test_class`/`cwd` do not survive `plan_extract.py` (filed as #266). The failure mode is **safe** — gates default to `manual`, i.e. more prompting, not less — but the pour-time metadata step is a live execution obligation. | Already documented in the plan's Gates preamble |

## Missing

Nothing in the blocking class. The one gap was C1's allow-list wording, now closed.

## Gate Assessment

| Gate | Reachable | Notes |
| :-- | :-- | :-- |
| Start Gate | yes | correct |
| Fan-out eliminated | yes | evidence (1.4, 1.9) outside `Blocks: 3.1, 3.3`; two-clause Test sound |
| Mechanical fan-out check green | **yes, both branches** | **B1 verified fixed by execution**; rules (c)/(d)/(e) green post-Epic-1 with 1.7 absent |
| Follow-on activation | yes, both branches | decline closure independently confirmed as exactly `{1.7, 3.1c}` |
| Pruning Authorization | yes | evidence outside `Blocks: 4.5, 4.1d`; "not warranted yet" closes the epic |
| Reconcile Gate | **yes, unconditionally** | fires on both branches |

## Upstream Assessment

Unchanged and sound. `#268` include-disposition correct; Resolved-By (`1.1, 1.3, 2.1`) matches the
tagged issues. SC10's four filings (3.4, 3.5, 3.7, 3.8) each have an owning issue and each is
sequenced **after** the fix that makes the routed push path usable — correct ordering.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | med | Reviewer's one-line recommendation applied verbatim — rule (b) exempts calls whose enclosing `FunctionDef` is on rule (e)'s allow-list. Applied despite being non-blocking because it is one clause and it removes a forced executor correction. | `main-session` | `resolved` |
| C2 | low | SC8b split into SC8b (hygiene requirement, `4.4b`) and SC8c (SPEC §5 entries, `0.4`), each independently verified. | `main-session` | `resolved` |
| C3 | low | Accepted as harmless imprecision; no change. Recorded so a later reader does not re-raise it. | `main-session` | `resolved` |
| C4 | low | Recorded for execution-time judgement — a copy-first GC test is strictly safer and the executor may choose it; the stated precondition already provides a recovery path. | `main-session` | `resolved` |
| C5 | low | Pre-existing and already documented in the plan's Gates preamble, with the pour-time metadata obligation stated. Failure mode is safe (more prompting, not less). | `main-session` | `resolved` |

## Outcome

**APPROVE.** The review loop converged in 5 cycles: 16 -> 9 -> 15 -> 7 -> 0 blocking concerns,
**52 resolved in total**, with the final cycle finding no defect in the blocking class and the plan
size unchanged from pass 3 onward (39 issues).

The reviewer's convergence note is worth preserving: C1 *"is the same shape as B1 but not the same
consequence: it is branch-symmetric, self-correcting through a control the plan already mandates,
and its correct resolution is already written in the plan's own text."* That distinction — same
shape, different consequence — is what separates a blocking defect from a nit, and it is the
judgement the binding standard was written to elicit.

Next: portability audit and `ready-check`, then the plan is presented to the operator. **Approval is
the operator's and is never the session's.**

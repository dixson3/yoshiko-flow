---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 2 - REVISE. Pass 1''s five high concerns verified genuinely
  resolved, but the C4 fix reintroduced the C3 class (6 unquoted -k expressions, exit
  4), SC13 reproduces the false green it was created to close, and a second false green
  exists on REQ-OKFH-010.'
plan: plan-064-james-dixson-a0b7fa
date: 2026-09-05
---
# Red-Team Pass 2: plan-064-james-dixson-a0b7fa

## Verdict: REVISE

Pass 1's five high/medium-high concerns are **genuinely resolved — re-measured, not taken on the
table's word**. But the revision introduced a **new high-severity mechanical defect of the same
class as C3**, left **three stale risk-table cross-references and seven stale references outside
`plan.md`** behind the Epic renumber, and — as suspected — **SC13 reproduces exactly the C4
defect it was created to close**.

## Verification of the claimed resolutions (all re-measured)

| Prior | Claim | Measurement | Holds? |
| :-- | :-- | :-- | :-- |
| C1 | SPEC gate now satisfiable | `check_amendment_log.py` -> exit **2** (INCONCLUSIVE, no log entry — correct pre-execution state). Sandbox-injected a plan-064 amendment-log entry naming the 7 ids -> **exit 0**, "7 amended id(s) all carry a bullet; all 25 non-exempt implementation issues reach a REQ-naming Epic-0 issue". | **YES** |
| C2 | Epic 0 renumber -> checker passes | `check-req-coverage.py --min-issues 30` -> **exit 0**, "31 non-Epic-0 issue(s); 1 direct, 15 transitive, 10 name a REQ, 6 declared bug fix". | **YES** |
| C3 | `--with pyyaml` added | All 11 pytest commands carry it; the previously-`INTERNALERROR` invocation now collects. | **YES, but see C14** |
| C4 | Selectors pinned to new names | Quoted `-k "crash_s1_bundle_present or crash_s2_errno66"` -> exit **5**, correctly red. But **SC13 is green today**: `-k crash_recovery_all_states` -> **exit 0, 1 passed**. See C15. | **PARTIAL** |
| C5 | Amend, don't mint | Verified at source: `REQ-OKFH-010:168` already says `restore` "shall be **record-driven with a PER-PATH operation kind**"; `REQ-OKFH-008:126-150` already fixes S0-S4 and "never on directory presence". | **YES** |
| C6-C13 | — | D10 present and reasoned; D3 discharged; SC3 split into SC4/SC5; drift check **exit 0**, 69 bundles; 0.1/0.2 name dual homes; `REQ-OKFH-013` owns R2; SC12 replaces the `--help` probe; C12 phrasing restated in all three places; residue gate extended to `Incubator` (**exit 0**). | **YES** |

Independently green today: `sync.py --check` (0), `check_okf_index_drift.py` (0), residue gate (0),
`check-drift-driver-contract.sh` (0), `doc_lint --path plan.md` (**PASS**), `audit` (**pass**).

## Strengths

- **The three high-severity pass-1 blockers are really fixed, and verifiable end-to-end.** The
  sandbox amendment-log injection proves the gate reaches exit 0 by the route Issue 0.8 describes,
  not merely that it is "less red".
- **C5 was handled the hard way.** Recasting to amendments + a recorded conformance defect, and
  stating the tension in the #298 exclusion row, is the honest move — the cheap one was to mint
  `REQ-OKFH-014/015` and be green.
- **The "too large" attack is refuted by measurement.** 39 issues / 6 epics / 20 SCs sits inside the
  corpus norm (plan-058: 39/5/25; plan-060: 49/7/41; plan-063: 30/7/30).
- **The `no-req-required` carve-out is used honestly.** All six members are gitignore hygiene or
  upstream filings that genuinely amend no requirement, each carries its reason string, and both
  instruments agree on the same six.
- **EXP-001's core claims corroborate at source.** `okf_hygiene.py:554-581` writes `S1` before
  rename 1 and `S2` after it; `recover()` at `:347` rmtree's staging on the `S1` branch while the
  bundle is already at `stash`; `recover` appears in no `add_parser` call.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C14 | high | **Six verification commands are unrunnable for an unquoted `-k` expression — the C3 class, reintroduced by the C4 fix.** SC4, SC8, SC9, SC11, SC12, SC16 write `-k a or b` **without quotes**. Measured: unquoted -> **exit 4**, `ERROR: file or directory not found: or`; quoted -> exit 5. The resolution table's "the pinned pair exits 5" was measured **with** quotes and transcribed **without** them. These six can never exit 0, before or after the work. |
| C15 | medium-high | **SC13 is green today via the exact false green it exists to remove — C4 one level up.** `pytest -k crash_recovery_all_states` -> **exit 0, 1 passed**, against code EXP-001 measured as violating `REQ-OKFH-008`. The criterion's text is a counterfactual ("no longer passes against code that violates…") but its verification is "the test passes", true in both worlds. R9 claims SC11's pinned selectors close this; R9 does not defend SC13. |
| C16 | medium-high | **Seven pytest node selectors are named by no issue, and Epic 4 has no test-authoring issue** — while the Approach says "Each epic lands its own test arm." `restore_record_driven`, `restore_bundle_filter`, `recover_verb_exists`, `backfill_refuses_stale_journal`, `dry_run_predictive`, `reconcile_objective`, `stamps_description` appear **zero times** in `## Epics`. A missing selector exits 5, so SC8, SC12, SC15, SC16 are unsatisfiable unless an executor improvises matching names. |
| C17 | medium | **Three risk mitigations still cite pre-renumber ids, each now pointing at unrelated work.** R1: "Issue **2.4** makes the regeneration explicit" — sync regeneration is **1.4**; 2.4 is `restore`'s per-bundle filter. R4: "Issue **2.3**'s hardcoded floor" — the floor is **1.3**. R5: "Issue **4.5** reuses that seam" — the crash arms are **3.5**. All three are old-Epic-N -> new-Epic-(N-1) shifts. |
| C18 | medium | **The `#294` row's `Resolved By` is half-renumbered.** It reads `1.1, 1.2, 2.1, 2.2, 2.4`; 2.1/2.2/2.4 are Epic-2 `restore` issues with nothing to do with gitignore enumeration — they are the *old* numbers for what are now 1.1/1.2/1.4, so the cell carries both old and new ids for the same work. Missing: 0.1, 1.3, 1.4, 1.5, 1.6, 1.8. |
| C19 | medium | **Seven stale references outside `plan.md` — the renumber sweep stopped at `plan.md`.** `context.md:32` "This plan's **Epic 1**" (SPEC-first is now Epic 0); `context.md:70-71` "**Epic 6**'s issue writes / **Epics 1-5** are offline" (network epic is now 5, offline set 0-4); `exp-003:131-134` four rows reading "Accepted -> **Epic 4**" where the recommendations now land in **Epic 5**. Those exp-003 rows are live forward-pointers, not frozen history. |
| C20 | medium | **The same false green exists on `REQ-OKFH-010` and nothing in the plan touches it.** `SPEC.md:235` declares `test_okf_hygiene.py::restore_round_trip` as its coverage. Measured: **exit 0, 1 passed** — against the `restore` EXP-001 proved is *not* record-driven, which is what the requirement demands. R9 names only `test_crash_recovery_all_states`; Issue 3.6 corrects only `REQ-OKFH-008`'s row. |
| C21 | low-medium | **Four criteria are already green before any work.** SC5, SC6, SC7, SC18 all exit 0 today. `check-drift-driver-contract.sh` will keep exiting 0 whether or not Issue 1.6 adds arm 4; SC7 also claims "the hygiene scaffolding cannot be enumerated as corpus" (Issue 1.7), which its command does not inspect at all. SC18 runs a bare `_shared/test_okf.py` suite that tests nothing about the `CHANGE-VALIDATION.md` trigger rows its text is about. |
| C22 | low-medium | **Issue 3.1's fix makes `S1` unwritable, contradicting `REQ-OKFH-008`'s normative five-state table unless 0.4 says so.** The SPEC fixes `S1` = "staged, before rename 1"; 3.1 writes `S2` before rename 1, so `S1` is never recorded again and `S2` no longer means what the table says. The `>= physical phase` amendment is the right frame but does not restate the table, and the §5 row still demands a test naming **each** of `S0`..`S4`. |
| C23 | low | **The requirement-coverage gate is a no-op as poured** — already exit 0 against the current `plan.md`, so it blocks nothing at pour time; it is a regression guard, not a capability gate. Separately, `assets/` and `diagrams/` are empty directories git will not track, so a cold reader in a fresh clone sees a different bundle layout. |

## Missing

- **No negative control anywhere in the plan.** R9 names the class correctly, but the plan's answer
  — pin selectors to new names — prevents *inheriting* a false green and never *detects* one. With
  two live instances (C15, C20) on the two requirements this plan amends, one mutation-style check
  would be worth more than SC13 and SC7 combined.
- **Nothing verifies the dual-home SPEC edit.** C9's fix names both homes and states that root alone
  satisfies the gate — precisely the condition under which the per-skill copy silently goes stale.
- **Issue 0.8 is the sole discharger of SC2 and carries three unrelated deliverables**, making it a
  single point of failure for both capability gates.

## Gate Assessment

All four capability gates are **reachable**, no cycles, correctly frontloaded.

- **SPEC gate** — now genuinely satisfiable (sandbox-verified exit 0) and no longer asymmetric: all
  7 Epic-0 issues name ids, and A2 reaches all 25 non-exempt issues. Pass 1's worst finding, closed.
- **Requirement-coverage gate** — measured exit 0. Reachable but already true (C23).
- **Vendored-copies gate** — measured exit 0; `Blocks: 1.8, 2.5, 3.5` correctly follows the renumber.
- **Residue gate** — measured exit 0 with the `Incubator` extension; `find`'s `-o` precedence correct.
- Correctly **no consent gate**.

## Upstream Assessment

- **#316 `partial`** — right, and D10 carries the load C6 asked for. The rejection of the leaner
  alternative is defensible: `yf-okf-hygiene` is a **deployed** skill, so shipping a `restore` proven
  to destroy data on three paths is a hazard beyond this corpus. Epics 2 and 3 are justified.
- **#294 `include`** — substantively right; `Resolved By` stale (C18).
- **#298 `exclude`** — the tension row is the strongest edit in the revision: it states the conflict
  rather than resolving it by fiat, and 0.3/0.4 back it up.

## Resolutions

All 10 concerns resolved by the main session. Every mechanical claim was **re-measured after the
fix**, and the two false greens C15/C20 named were reproduced first to confirm the concern.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C14 unquoted `-k` | high | Confirmed before fixing: unquoted -> **exit 4** (`file or directory not found: or`), quoted -> exit 5. All six commands (SC4, SC8, SC9, SC11, SC12, SC16) now quote the expression. The reviewer's diagnosis of the cause is exactly right — the pass-1 measurement was run with quotes and transcribed without them, which is why the table could report exit 5 for a command that cannot produce it. | `main-session` | `resolved` |
| C15 SC13 false green | medium-high | SC13 rewritten as a **negative control**: new Issue 3.8 adds `scripts/checks/check-crash-test-detects-lag.sh`, which reverts Issue 3.1's phase-ordering fix in a sandbox and asserts `test_crash_recovery_all_states` **FAILS**, then asserts it passes on the fixed tree. SC13's verification is now that script, discharged by 2.8/3.6/3.8. The reviewer's framing is adopted verbatim in R9: pinning selectors prevents *inheriting* a false green but never *detects* one. | `main-session` | `resolved` |
| C16 unowned selectors | medium-high | All seven now named by exactly one issue: `restore_record_driven` + `restore_bundle_filter` -> new **Issue 2.7**; `recover_verb_exists` + `backfill_refuses_stale_journal` -> **Issue 3.5**; `dry_run_predictive` + `reconcile_objective` + `stamps_description` -> new **Issue 4.4**, Epic 4's test-authoring issue, which the Approach's "each epic lands its own test arm" had promised and the epic lacked. | `main-session` | `resolved` |
| C17 stale risk ids | medium | R1 -> 1.4, R4 -> 1.3, R5 -> 3.5. Verified by reading each target's text against the claim rather than confirming the id exists — the check the reviewer recommended, and the one that would have caught these at pass 1. | `main-session` | `resolved` |
| C18 #294 Resolved By | medium | Set to `0.1, 0.2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8`. The old cell really did carry both old and new ids for the same work. | `main-session` | `resolved` |
| C19 stale refs outside plan.md | medium | `context.md` 3 sites corrected (SPEC-first is Epic 0; the network epic is 5; the offline set is 0-4). `exp-003`'s 4 recommendation rows retargeted to Epic 5. `exp-002`'s stale `SC3` reference dropped. The renumber sweep genuinely had stopped at `plan.md`. | `main-session` | `resolved` |
| C20 second false green | medium | Reproduced first: `pytest -k restore_round_trip` -> **exit 0, 1 passed** against the non-record-driven `restore`. New **Issue 2.8** repairs or replaces it and corrects `REQ-OKFH-010`'s §5 row, mirroring 3.6. R9 widened from one test to the class, naming both instances. | `main-session` | `resolved` |
| C21 four vacuous criteria | low-medium | SC7 now asserts arm-4 existence and `git check-ignore` on the scaffolding, so it measures Issues 1.6 and 1.7 rather than passing regardless. SC18 now greps the two `CHANGE-VALIDATION.md` rows it is actually about, instead of running an unrelated suite. SC5 and SC6 are kept but **labelled green-before-the-work** — they are regression guards and a maintenance invariant, and saying so stops a green reading being mistaken for work done. | `main-session` | `resolved` |
| C22 S1 unwritable vs SPEC table | low-medium | Issue 0.4 extended to **restate the normative five-state table under the over-approximation reading** — the recorded phase is an upper bound, so `S1` becomes a recovery-time-only state never written once the ordering is fixed — and to amend the §5 row's "naming each of `S0`..`S4`" accordingly, so the amended requirement does not contradict its own table. | `main-session` | `resolved` |
| C23 gate no-op; empty dirs | low | The coverage gate's `Instructions` now state it is a **regression guard, already green at pour time**. The empty `assets/` and `diagrams/` directories are left as-is: they are `plan_manager.py init` scaffold, git will not track them either way, and removing them would diverge this bundle from all 60 conformant siblings for no gain. A DAG diagram is a reasonable future addition but is not this plan's deliverable. | `main-session` | `resolved` |

### Also taken from the Missing section

- **The negative control** the reviewer asked for is Issue 3.8, and it discharges SC13 (above).
- **The dual-home SPEC edit** is now verified: Issue 0.8 adds an assertion that
  `skills/yf-okf/SPEC.md` received the same `REQ-OKF-012`/`REQ-OKF-CHK-004` amendment as root
  `SPEC.md`, closing the exact condition C9's fix created.
- **Issue 0.8's single-point-of-failure** shape is acknowledged and left intact: splitting the
  `CHANGE-VALIDATION.md` wiring into its own issue would not reduce the coupling, since both
  capability gates depend on the same wiring landing. Recorded rather than silently accepted.

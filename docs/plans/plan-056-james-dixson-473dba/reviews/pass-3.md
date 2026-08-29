---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: "Red-team pass 3 — REVISE. Third recurrence confirmed: 26 unjudged criteria launder into verdict PASS, and SC11b is the mechanism. Plus a supported argument that the plan should split."
---

# Red-team pass 3: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 10 concerns resolved.** C27 was independently confirmed against the engine source and filed
> upstream as #265. C31 was carried to plan-057 with the work that created it. The scope finding (S1)
> was accepted by the operator: the plan split.

**The defect recurred a third time, and a fourth time inside pass 2's own C18 resolution.** Both
mechanically confirmed, and the third recurrence independently reproduced by the main session against
`plan_manager.py:2945-2969`.

## Strengths

Verified mechanically: 54 issues, no duplicate ids, no dangling `depends-on`, **no cycles**, **zero
backward cross-epic edges**, every issue named by >=1 criterion. `gate_consistency` PASS 4/0.
`doc_lint` PASS. `verify-reconcile` fails 7 of 10 rows for the right reason. Pass 2's two headline
measurements reproduce independently (`os.rename` errno 66; direct-file `-k` exit 0). C5, C7, C9, C12,
C16, C22, C26 hold.

## Concerns

### C27 — THE THIRD RECURRENCE. 26 unjudged criteria launder into `verdict: PASS`, and SC11b is the mechanism. [HIGH]

Today: **44 total · 37 class-A · 11 evaluated · 10 FALSE · 1 `holds` · 26 inconclusive · 7 not-evaluated.**
Every inconclusive row is inconclusive because the instrument does not exist, `bash -c` returns 127, and
`plan_manager.py:2915` maps 126/127 to `inconclusive`. The aggregate rule then reads:

```
if failed: FAIL exit 1
if evaluated == 0: INCONCLUSIVE exit 2 (warn, never halts)
else: PASS exit 0 — "all {evaluated} evaluated criterion/criteria hold"
```

**Inconclusive rows are counted in neither bucket.** Sandbox-confirmed: 1 criterion `true` + 2 missing
scripts -> **PASS, exit 0**; delete the `true` row -> INCONCLUSIVE, exit 2. That is plan-056's end state
exactly. When the 10 FALSE criteria go green at completion, if the harness scripts are absent or return
126/127, the §6.4 close chain reports PASS while **26 of 37 class-A criteria were never judged**.

**And the criterion that makes this possible is the one the plan defends as deliberate.** SC11b is the
only `holds`; its presence is what converts the honest `evaluated == 0 -> INCONCLUSIVE` branch into
`PASS`. The plan's answer to "why is one criterion green" is correct as far as it goes and misses that
SC11b is structurally the laundering step.

Pass 1: `-k` no-ops -> green. Pass 2: `uv run <missing>.py` exits 2 -> green. Pass 3: missing instrument
exits 127 -> never judged, and **never judged reads as PASS**. `evaluated_fraction` is emitted by the
engine and consumed by nothing.

*Rec:* (1) add **SC0** using only shell builtins — `[ -x … ] && [ -x … ]` over all 13 instruments — so a
missing harness reads FALSE and halts; (2) amend `REQ-PLAN-080` so a class-A criterion inconclusive **at
completion** is not silently equivalent to one that holds.

### C28 — C18 recurs verbatim inside its own resolution: 4 of 13 check scripts still have no creating issue. [HIGH]

The criteria invoke **13** distinct scripts, not eight. `check-drift-driver-contract.sh` (SC3),
`check-recipe-row.sh` (SC11, SC20b), `check-baseline-pin-contract.sh` (SC24) and
`check-skill-classified.sh` (SC33) have **no owner** — each appears in exactly one line of plan.md, its
own Verification cell, which is C18's exact wording. Meanwhile 1.9 names `check_okf_baseline_pin.py`,
which **no criterion invokes**. And SC3/SC11/SC20b/SC24/SC33 all list `1.9` in `Discharged-by` — the
column asserts coverage the issue text does not provide.

*Rec:* derive 1.9's list mechanically from the Verification column and re-run that diff as an approval
preflight, as C12's fix routed through `verify-reconcile`.

### C29 — The harness adjudicates its own correctness, has no REQ, and no criterion. [HIGH]

**32 of 44 criteria** are evaluated by instruments this plan creates; **none** is evaluated by an
instrument outside that set, and **no criterion verifies 1.8 or 1.9**. Wrong-but-exits-0 -> all green;
absent -> inconclusive -> PASS (C27). The trust boundary moved `-k` -> `uv run` -> `scripts/checks/*`; it
has not closed.

Compounding, this is a **SPEC-first violation inside the epic that enforces SPEC-first**: 1.9 creates
eight scripts — a new repo surface — and names no `REQ-*`. So **SC1 is FALSE against Issue 1.9**, and SC1
is adjudicated by `check-req-coverage.py`, which **1.9 writes**.

*Rec:* give 1.9 a REQ stating the harness contract; add a RED-fixture control criterion for 1.9 that is
not itself run by 1.9's scripts.

### C30 — C19 is NOT resolved: "module-form pytest" is not runnable in this repo. [HIGH]

| Command | Exit |
| :-- | --: |
| `python3 -m pytest _shared/test_okf.py -q` | **1** — no pytest in the repo venv |
| `uv run --with pytest python -m pytest _shared/test_okf.py -q -k <any>` | **2** — collection error |
| `uv run --with pytest --with pyyaml python -m pytest _shared/test_okf.py -q -k <no-match>` | 5 |
| `uv run --with pytest python -m pytest .../test_cli_enumeration.py -q` | 0 |

Under module form the entrypoint is `python`, so **the target's PEP 723 header is never read** —
`test_okf.py` declares `pyyaml` and dies at collection without it. Per-file dependency sets are
heterogeneous, and **20 criteria** route through this. Second: **1.8's INCONCLUSIVE exit code is
unspecified** — if the implementer reaches for 127, all 20 become permanently unfailable (C27).

*Rec:* 1.8 must parse the target's PEP 723 `dependencies` and forward them (or use `uv run --script`);
pin INCONCLUSIVE to **exit 3**, reserving 126/127 to the harness.

### C31 — C21 is NOT resolved: the three-state recovery table is not a decision procedure. [HIGH]

The real state space over `(dst, dst.bak, stage)` has five reachable states. The table keys on two.

| # | state | table says | correct action |
| --: | :-- | :-- | :-- |
| S0 | dst, no bak, no stage | "done" | not started |
| S1 | dst, no bak, **stage present** | "done" | **swap never happened — roll forward** |
| S2 | no dst, bak, stage | row 2 | roll forward or back |
| S3 | dst(new), bak, no stage | rows 1 **and** 3 | clean up |
| S4 | dst(new), no bak, no stage | row 1 | done |

**Incomplete** (S1 — staged, crashed before rename 1 — reads as "done", so the bundle is silently left
un-backfilled while the run reports success: R3's exact failure mode); **ambiguous** (S3 matches two
rows, so it is not a function); and row 2 is **nondeterministic** — "roll forward or back" is a choice,
not a rule. Nothing states the record is fsynced before rename 1. SC31c tests one of five crash points.

Pass 1: atomicity asserted. Pass 2: a mechanism that is not atomic. Pass 3: a recovery table that is not
total.

*Rec:* recover from a **durable per-bundle journal** fsynced before rename 1, not from directory
presence; make the table total with one action per row; widen SC31c to all five crash points.

## Missing

- No criterion verifies the harness itself (C29).
- No REQ for Issue 1.9 (C29).
- Pass 2's #165 residual — `REQ-PORT-010` resolves to two unrelated requirements, and the intended one is
  research-scoped while SC10's `--min-roots 30` covers plan bundles — is **not addressed**.

### Medium

- **SC30b does not verify what it says.** It reads "the one live `_index.md` bundle is migrated" but runs
  `audit --root docs/research --min-roots 1`. `docs/research` holds **5** bundles, so the guard is
  vacuous, the command never names `001-okf-compliance-delta`, and exit 0 requires four *out-of-scope*
  bundles to be conformant. C23 half-resolved. **SC21 over-claims identically** (enumerates ~56 plan
  bundles; 5.9 backfills 30).
- **The `manual:` tier is where the defect class now hides.** 7 not-evaluated rows are `manual` —
  legitimate per REQ-DATA-070 — but they are the whole of Epic 6's documentation output **plus SC27, "No
  shipped spec cites a corpus figure the corpus contradicts."** The anti-stale-figure criterion, for a
  defect class that has recurred three times, is verified by prose.
- **The resolutions ledger has drifted from the plan.** Pass 2's C25 resolution claims D-1 now carries
  "1088 files, 1642 findings, 392 demoted". **None of those appears in plan.md**; Motivation and D-1
  still say 1054/1634. The review ledger is now itself an unverified source — the failure C25 named.
- **R12 says 51 issues; the plan has 54.** Third occurrence (46 -> 51 -> 54).
- **SC20 uses the direct-file form the convention block condemns**, and does not route through 1.8.
- **SC12 hard-codes `--baseline 142/257`** and is adjudicated by a script 1.9 writes.

### Low

- SC33b verified non-vacuous: dry-run exits 0, lists 19 skills, `yf-okf-hygiene` absent. C22 resolved.

## Gate Assessment

`gate_consistency` PASS, 4 gates, 0 findings. All four sound; no cycles, no self-blocking.

## Upstream Assessment

`verify-reconcile` fails 7 of 10 for the right reason. #170 resolved with the 1285/1383 caveat carried.
#165's residual from pass 2 remains unaddressed.

## On size: this plan is too big, and it has a clean seam

54 issues, 44 criteria, grown 46 -> 51 -> 54 across two cycles. **Each pass added issues to close a hole
the previous pass's issues opened** — 1.8 begat 1.9, and 1.9 now has four uncreated scripts of its own
(C28). That regress is the strongest evidence that the harness layer is being scaled rather than
simplified.

The plan names its own split point: R12 asserts Issues 0.1-3.4 close the enforcement gap independently,
and the DAG has **zero backward cross-epic edges**, so the split is mechanically legal today.

- **Plan A — Epics 0-3 plus 1.8/1.9 (31 issues):** the enforcement gap, which is the entire Motivation.
  Every high-severity concern above lives here and is worth fixing here.
- **Plan B — Epics 4-6 (23 issues):** index depth, the hygiene skill, baseline realignment.

Epic 5 is not yet earned: D-11 mandates `_index.md` support on "47% of the wider corpus", measured as
**227 of 243 in one foreign repo that D-10 bars touching**; the repo holds exactly two `_index.md`, one
frozen and one live. So 5.6/SC30/SC30b/R6 build and verify a route against fixtures for a corpus this
plan may not touch. Epic 4 has a similar shape — 4.1/4.4 widen drift against a now-live gate, requiring
4.4 to re-repair the corpus the same epic broke.

Deferring Epics 4-6 removes roughly half the criteria, most of the `manual:` tier, and the entire
crash-recovery surface of C31 — and makes the remaining harness small enough to verify properly rather
than trust.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C27 unjudged criteria launder into PASS | high | Confirmed independently by reading `plan_manager.py:2945-2969` — inconclusive rows are counted in neither bucket, exactly as reported. Two remedies, both landed: **SC0** uses shell builtins only (`test -x …`) so a missing harness reads FALSE rather than vanishing, and new Issues **0.13 + 1.10** amend and implement `REQ-PLAN-080` so an unjudged class-A criterion blocks at the completion binding. Because this defeats the gate for EVERY plan in the repo, it was also filed upstream as CRITICAL — **#265** — with the sandbox reproduction, and verified by reading the body back. | `operator` | `resolved` |
| C28 4 of 13 check scripts unowned | high | Issue 1.9's script list is now **derived mechanically from the Verification column** rather than assembled by hand: eight scripts, with `check-pytest-ran.sh` attributed to 1.8 and `check_okf_index_drift.py` to 3.1. The four previously-unowned scripts (`check-drift-driver-contract.sh`, `check-recipe-row.sh`, `check-baseline-pin-contract.sh`, `check-skill-classified.sh`) are covered — the last two moved to plan-057 with their criteria. Re-deriving the list is now an approval preflight, mirroring how C12's fix routed through `verify-reconcile`. | `operator` | `resolved` |
| C29 harness self-adjudicates, no REQ | high | New Issue **0.14 (`REQ-CLI-018`)** gives the harness a requirement — closing the SPEC-first violation inside the SPEC-first epic. New **SC35** is the RED-fixture control asserting each script returns non-zero on a deliberately broken input. **The residual circularity is stated rather than papered over**: SC0 establishes existence using builtins only, SC35 establishes behaviour; what remains unverified is `harness-selftest.sh` itself, one script rather than eight. Claiming full closure here would have been the fourth recurrence. | `operator` | `resolved` |
| C30 module-form pytest not runnable | high | Independently reproduced: module-form pytest on `test_okf.py` exits **2** at collection because `python` is the entrypoint and the target's PEP 723 header is never read, while `test_cli_enumeration.py` (no deps) exits 0. Issue 1.8 now requires **parsing and forwarding the target's PEP 723 `dependencies`** (or `uv run --script`), and its INCONCLUSIVE result is **pinned to exit 3**, with 126/127 reserved to `recheck-criteria` — because returning either would have made all 20 criteria routed through it permanently unfailable, i.e. C27 again. | `operator` | `resolved` |
| C31 recovery table not total | high | Confirmed (`os.rename` onto a non-empty directory raises errno 66) and **carried to plan-057 with the backfill work**. Its Issue 2.4 now recovers from a **durable per-bundle journal fsynced before the first rename**, not from directory presence, and its SC11 asserts deterministic recovery from **all five** reachable crash states — including 'staged, crashed before rename 1', which the presence-keyed table misread as done. | `operator` | `resolved` |
| M6 SC30b/SC21 over-claim | medium | SC30b and SC21 both moved to plan-057, where SC13 now exercises the `_index.md` route against the one live in-repo target by name rather than via a vacuous `--min-roots 1` over five bundles, and SC19 asserts `--min-roots 30` against the set 2.9 actually backfills. | `operator` | `resolved` |
| M7 manual tier hides the class; SC27 | medium | The `manual:` tier shrank with the split — plan-056 retains three manual criteria (SC25, SC27, SC32), all genuine documentation outcomes. SC27 remains prose-verified and that is now an accepted, stated limitation rather than an oversight: no command can assert 'no shipped spec cites a figure the corpus contradicts' without enumerating every figure, which is Issue 0.8's job and is itself checked by 0.12's re-measurement. | `operator` | `resolved` |
| M8 ledger drifted from plan; stale counts | medium | **[CORRECTED at pass 4 — this row was FALSE when written.]** It claimed the measured figures were "now written into D-1's Basis cell"; pass 4 grepped both plans and found none of 1088, 1642 or 392 anywhere, while D-1 still carried 1634/1603. The claim described an intended edit as a completed one. The figures are now genuinely in D-1's Basis cell with their measurement date, and Issue 0.12 re-derives them at execution rather than trusting either ledger. | `operator` | `resolved` |
| M9 SC20 direct-file; SC12 self-adjudicated | medium | SC20 moved to plan-057 as SC17 and now uses the module form (`uv run --with pytest python3 -m pytest … -q`) rather than the direct-file form the convention block condemns. SC12's self-adjudication is bounded by SC35's RED-fixture control, and its baseline is dated in the cell. | `operator` | `resolved` |
| S1 plan should split at Epics 0-3 / 4-6 | scope | **Accepted by the operator.** plan-056 keeps Epics 0-3 plus a reconcile epic — 34 issues, 21 criteria — scoped to the Motivation. Root-index depth, the hygiene skill and the baseline re-pin became **plan-057-james-dixson-9ecf1c** (4 epics, 25 issues, 26 criteria), which inherits all six findings verbatim so it reads cold, carries D-1..D-12 with their original evidence, and gates on plan-056's completion because three of its outputs are load-bearing there. Recorded as plan-056 D-17. | `operator` | `resolved` |

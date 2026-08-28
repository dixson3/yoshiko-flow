---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: "Red-team pass 1 — REVISE. Five criteria measured GREEN on unmodified HEAD; the -k filter is a no-op in every test script in the repo."
---

# Red-team pass 1: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 16 concerns resolved by the main session.** Re-dispatched as pass 2.

## Strengths

- EXP-001–006 are real measurements with falsifiers, and the "Corrections this investigation forced"
  block is the right practice (7→9, upstream-freeze premise refuted, 100/25→514/41).
- DAG verified mechanically: **46 issues, no duplicates, no cycles, no dangling `depends-on`, every
  issue covered by >=1 SC, no SC referencing a nonexistent issue.** Both `Blocks:` targets resolve.
- Feasibility spot-checks all pass: `_glob_match` and `check_markers` exist as Issue 1.1/1.3 describe;
  `okf.py` has exactly the walk sites 1.3 enumerates; `doc_lint` already ships `--no-exclude`;
  `verify-reconcile`, `audit --json-output`, `audit-close --json` all exist with the cited flags; 30
  depth-1 legacy `README.md` confirmed; Gate 2's `curl` returns HTTP 200.
- D-13, D-15 and D-16 are each backed by a measurement that would have falsified the alternative.

## Concerns

### C1 — `-k` is a no-op in this repo's test scripts. Five criteria pass today. [HIGH]

Measured: `uv run _shared/test_okf.py -k this_filter_matches_nothing_xyz` → **64 passed, exit 0**.
Cause: `test_okf.py:668` is `raise SystemExit(pytest.main([__file__, "-q"]))` — **`sys.argv` is
discarded**, and `grep pytest.main` returns 20+ identical call sites. `_shared/test_doc_lint.py` is
worse: a hand-rolled runner with no argument parsing at all; `-k bogus_filter_xyz` → exit 0.

Consequence: **SC4, SC7, SC8, SC13, SC14 are satisfied right now**, before the issues that create them
exist. SC15/16/17/18/19/30/31 inherit it the moment `test_okf_hygiene.py` follows the convention, and
collapse into SC20. The repo owns the fix and its rationale — `check-cargo-test-ran.sh` exists for
exactly this — but **has no Python equivalent, and this plan routes 13 criteria through it.**

*Recommendation:* add `scripts/checks/check-pytest-ran.sh` (or forward `sys.argv[1:]` into
`pytest.main` and map `EXIT_NOTESTSCOLLECTED`→1), then re-express the 12 affected criteria through it.

### C2 — SC2 passes on the unfixed code; it verifies one side of a distinction. [HIGH]

Measured on HEAD: `reindex --check /nonexistent/xyz` → exit 2, and a real index-less bundle → exit 2.
**That identity IS the defect Issue 1.1 exists to fix.** SC2 verifies only the branch already correct.

*Recommendation:* make SC2 a two-branch predicate asserting `N != M` in one command.

### C3 — SC6 is structurally blind: `audit-close` is advisory and cannot exit non-zero. [HIGH]

Measured: plan-053 `audit-close` returns `"verdict":"fail"` with fixture findings **and process exit
0**, because `audit_close` is advisory by design. SC6 is one of two criteria discharging #233 and
cannot discharge anything.

*Recommendation:* verify the report, not the exit code, and assert a non-fixture finding exists so a
run that inspected nothing cannot pass.

### C4 — SC5 cannot assert the ordering it is cited for, and R1 depends on it. [HIGH]

Measured on HEAD, before 2.1/2.2/2.6/3.3 exist: audit → `{"status":"pass","findings":[]}`, exit 0. It
stays 0 after 3.3 lands, because 3.3 declares the check at **`W`** and REQ-DATA-057 maps intake lint
W→warn. **SC5 is green in both worlds**, and the "16 errors" it gestures at were measured for an
`E`-severity check the plan deliberately did not build.

*Recommendation:* replace with a content check on `findings[]`; stop claiming SC5 proves the ordering.

### C5 — Issue 3.2 turns the gate on without depending on the producer fix. R1's mitigation is false as written. [HIGH]

Transitive ancestors of 3.2 = `{3.1, 0.1, 0.3, 1.1, 1.2, 1.3, 1.4, 1.5, 1.7}`. **2.3 is not there.
3.4 is not there.** So the enforcement wiring — the one irreversible act in Epic 3 — is legally
schedulable before the producer fix and before the 9 drifting bundles are repaired, making the FAST
tier fire red on every subsequent edit including those performing 3.4. That is R1, unmitigated, in the
plan's own DAG. SC10's `Discharged-by` already lists `2.3, 3.1, 3.2, 3.4` — the criterion knows the
dependency the graph omits.

*Recommendation:* `depends-on: 3.1, 2.3, 3.4` on Issue 3.2.

### C6 — Issue 5.9's blast radius is 39 READMEs, not 30 — and 9 are frozen evidence. [HIGH]

Measured: `find docs/plans -name README.md` → **39**; `-maxdepth 2` → 30. The nine extras include **6
inside `plan-029/findings/okf-migration-samples/`** — frozen migration fixtures. The repo's **only
`_index.md`** is also inside that fixture tree, so Issue 5.6/SC30 is aimed at evidence that must not
be migrated. Issue 5.3's exclusion list omits `findings/okf-migration-samples/**` and
`assets/fixtures/**`; those live in Issue **1.5**, and **5.3 has no `depends-on: 1.5`**. Corollary:
**SC21 cannot pass** while the plan-029 `before/` bundles classify as `legacy-readme`.

*Recommendation:* `depends-on: 1.5` on 5.3 consuming the same §3b mechanism; scope 5.9 to depth-1; add
a 5.8 test that backfill does not touch the migration samples.

### C7 — "30/30 fingerprints byte-identical" does not cover the content the backfill moves. [HIGH]

Read `_plan_content_fingerprint` (plan_manager.py:3082, contract :3045-3056). It covers **`plan.md`
only** — `README.md`, `index.md`, `log.md` are entirely outside it, i.e. **every file the backfill
mutates**. It **excludes the header preamble**, which is exactly where `migrate` adds frontmatter, so
**the 30/30 invariance is a tautology**. It excludes `## Upstream Issues`, drops blank lines and
right-strips. **The phase log is not in it at all** — precisely the content plan-030 was measured to
strand. The fingerprint is structurally blind to the single measured data-loss mode of this operation.

EXP-005 got this right (it reported fingerprint and phase-log equality as two signals). The
overstatement is in the plan: `context.md` presents it unqualified as the safety argument, and SC15
asserts three things, verifies one, through a `-k` that does not filter.

*Recommendation:* split SC15 into three; delete "byte-identical" or scope it; amend `context.md` to
name what the fingerprint excludes.

### C8 — R3's "atomic per bundle" is asserted, not mechanised; `restore` has an unspecified branch. [HIGH]

D-13 says the transform is three steps; it nowhere says atomic, and three sequential filesystem
operations are not. On restore: all 30 depth-1 READMEs are git-tracked (verified per-file) — say so,
it is load-bearing and unstated. But the backfill **creates** `index.md`/`log.md`, and `git checkout`
cannot remove a path absent from HEAD, so restore needs three verbs and the record must carry the
operation kind. And the clean-tree precondition is **already violated** (`git status --porcelain` is
non-empty today and by construction during execution) — define clean as scoped to the bundles.

*Recommendation:* name the mechanism (stage to tmp, validate, single swap); specify record op-kinds;
add a kill-between-step-2-and-3 restore test.

### C9 — Gate 2 blocks the issue that doesn't need it, and not the one that does. [MEDIUM-HIGH]

The issue that computes the pin is **6.1**, which cannot proceed offline and is **not** in `Blocks`.
3.5 proceeds regardless by its own Instructions — a gate whose failure branch is "carry on" is not a
gate.

*Recommendation:* retarget to `Blocks: 6.1`.

### C10 — `3.5 → 6.1` is the only backward cross-epic edge and falsifies R12. [MEDIUM]

R12 claims Epics 0-3 land first "even if Epics 4-6 slip", but Epic 3 cannot complete without Epic 6
starting.

*Recommendation:* move 3.5 into Epic 6, removing the graph's only backward edge.

### C11 — SC1 quantifies in the wrong direction and is false as scoped. [MEDIUM]

It quantifies over behaviour changes but enumerates from Epic 0 outward, so an implementation issue
with no REQ is invisible. Several exist: **2.4** (live behaviour fix), **2.5** (a new public CLI
verb), **2.3**, **3.1/3.2**.

*Recommendation:* invert the verification; add the missing Epic 0 issues or mark them explicitly.

### C12 — #170 is `include` but Issue 6.6 never closes it; SC26 will fail. [MEDIUM]

`verify-reconcile` already reports `170 include fail — #170 is OPEN; an include row must be CLOSED`.
6.6 says "record", not close, and omits #170 from `resolves-upstream:`. Also the `Resolved By` column
and the `resolves-upstream:` annotations disagree in three rows (#233, #165, #247). Irony worth
naming: the plan excludes **#173** — "criteria and dispositions never checked against the engine" — and
then commits that defect.

*Recommendation:* change #170 to `partial` or make 6.6 close it; reconcile the annotations; run
`verify-reconcile` as an approval preflight.

### C13 — SC33 lands in the `files_checked: 0` trap the repo has an always-loaded rule about. [MEDIUM]

Measured with the file **not existing**: `{"verdict":"PASS","files_checked":0}`, exit 0 — indistinguishable
from the clean case. That is the `not-selected` vs `no-such-path` conflation (#181) whose prescribed
remedy (`--classify`) SC33 ignores. Separately, schema conformance is not evidence of installability.

*Recommendation:* two criteria — `--classify` asserting `class == "selected"`, and `yf skill-dir`.

### C14 — Corpus-driver criteria have no "it actually enumerated something" guard. [MEDIUM]

SC10, SC21, SC9, SC11 are whole-corpus commands verified by exit 0; a driver enumerating **zero**
bundles exits 0 clean. SC9 is sharpest: the criterion asserts a **capability to fail** and verifies it
with an **all-pass run** — it cannot distinguish "the two E checks survive" from "someone deleted
them", which is exactly what D-15 exists to prevent.

*Recommendation:* add a `bundles_checked >= N` assertion; make SC9 a RED fixture.

### C15 — Motivation carries superseded figures the findings corrected. [MEDIUM]

| Location | Plan says | Findings say |
| :-- | :-- | :-- |
| Motivation ¶3 | "**7** of the **25** index-bearing bundles" | EXP-001: **9** drift, **30** index-bearing of 61 |
| SC12 | "the **120/247** baseline" | EXP-003: **140/247** boilerplate |
| D-1 basis | "~**423** findings across 16 check ids" | no finding reports this; the corpus run reported **1634**, and the only sourced 423 is the stale line Issue 0.8 is fixing |

*Recommendation:* correct all three; if 423 was inherited from the stale spec line, say so in the
corrections block — that is what the block is for.

### C16 — Two epics do work their Approach summary does not admit. [LOW-MEDIUM]

The "deliberately does not do" list survives scrutiny — nothing is smuggled back. But Epic 2's summary
omits **2.5** (a new public CLI verb) and Epic 4's "cheap on the engine (one function)" omits **4.5**,
which may add an 18th document type. And "does not re-judge history" sits eight lines above an epic
that rewrites 30 completed bundles.

*Recommendation:* one clause each; reword to "does not re-judge history's **severities**".

## Missing

- No criterion covers Issue **1.7** as a *sync* — add `uv run _shared/sync.py --check` → exit 0.
- No criterion for the **crash/resume path** of `backfill --apply` (C8).
- No criterion asserts the exclusion lists stay **non-empty** — an empty §3b satisfies SC8 vacuously.
- Gate 1's Instructions name a bare `okf_hygiene.py`; the real path is
  `skills/yf-okf-hygiene/scripts/okf_hygiene.py`. SC11 has an unexpanded `${SKILL_DIR}`.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Backfill authorization -> 5.9 | Yes — evidence produced by 5.4/5.5, outside `Blocks`, no cycle | Correctly late; the dry-run *is* the evidence | Sound; fix command path and blast radius |
| Upstream network -> 3.5 | Yes — `curl` verified HTTP 200 | **Misdirected**; 3.5 proceeds anyway, 6.1 genuinely cannot | Retarget to 6.1 |
| Reconcile Gate | auto | — | fine |

No gate's condition depends on evidence produced inside its own `Blocks` set — **no gate cycles**.

## Upstream Assessment

Dispositions are mostly well-argued and several unusually honest — **#169** records counter-evidence to
the plan's own thesis; **#189** converts a deferral into D-9; **#168** names its unfired trigger
concretely. The `partial` rows name both halves. Two defects: **#170**'s `include` is unreachable as
drafted, and `Resolved By` disagrees with the annotations in three rows — both mechanically
detectable, and `verify-reconcile` found the first in one invocation.

**#173**'s exclusion deserves a second look: C1–C6, C13 and C14 are all instances of exactly that
class, found in one review pass.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 `-k` no-op; 5 criteria green on HEAD | high | Added Issue 0.11 (REQ) + Issue 1.8 (`scripts/checks/check-pytest-ran.sh`, forwarding `sys.argv[1:]` and mapping EXIT_NOTESTSCOLLECTED->1). All 12 filtered criteria re-expressed through it; 1.8 is a declared ancestor of each. Recorded as new risk R13. | `main-session` | `resolved` |
| C2 SC2 verifies one branch | high | SC2 rewritten as a two-branch predicate via `check-reindex-exit-contract.sh`, asserting the two exit codes DIFFER rather than checking the already-correct branch. | `main-session` | `resolved` |
| C3 SC6 blind; audit-close advisory | high | SC6 rewritten to verify the report via `check-fixture-carveout.sh` — no `okf:` finding under a fixture path AND at least one non-fixture finding, so a run that inspected nothing cannot pass. | `main-session` | `resolved` |
| C4 SC5 cannot assert ordering | high | SC5 replaced with `check-description-coverage.py` over plan-056's own nested artifacts. R1's mitigation text corrected: the ordering evidence is the DAG, verified mechanically, not a criterion. | `main-session` | `resolved` |
| C5 3.2 missing producer deps | high | `depends-on: 3.1, 2.3, 3.4, 0.9` added to Issue 3.2. Verified: 3.2's transitive ancestors now include both 2.3 and 3.4. Issue text names 3.2 as the epic's one irreversible act. | `main-session` | `resolved` |
| C6 5.9 blast radius 39 not 30 | high | Issue 5.3 gains `depends-on: 1.5` and the two fixture-tree exclusions, consuming 1.5's §3b mechanism. 5.9 scoped to depth-1; gate Instructions now use `--maxdepth 2` and require confirming 30 bundles not 39. New test case in 5.8 (SC19b) that migration samples are untouched. | `main-session` | `resolved` |
| C7 fingerprint blind to moved content | high | SC15 split into SC15 (fingerprint), SC15b (phase-log bullet AND distinct-date equality) and SC15c (per-bundle audit delta); "byte-identical" removed. `context.md` now states what the fingerprint excludes and that the 30/30 result is near-tautological. | `main-session` | `resolved` |
| C8 atomicity asserted; restore branch | high | R3 rewritten around a mechanism: stage-to-temp, validate, single directory swap. Issue 5.7 specifies per-path operation kinds and the three reversal branches, and records that all 30 READMEs are git-tracked. Clean-tree precondition scoped to the bundles. New SC31b kills a run mid-transform. | `main-session` | `resolved` |
| C9 Gate 2 misdirected | medium-high | Gate retargeted to `Blocks: 6.1`. Instructions reworded after `gate_consistency` flagged the first attempt as self-blocking — the gate's evidence is now stated as the `curl` alone, with no blocked issue named as its source. | `main-session` | `resolved` |
| C10 backward edge falsifies R12 | medium | Issue 3.5 moved to Epic 6 as Issue 6.1a. Verified: zero backward cross-epic edges remain. R12 restated as "Issues 0.1-3.4". | `main-session` | `resolved` |
| C11 SC1 wrong direction | medium | SC1 inverted to enumerate Epic 1-6 issues via `check-req-coverage.py`. Added Epic 0 issues 0.9 (driver + recipe binding) and 0.10 (execution-time members, lifecycle calls, `index-add` verb); 2.4 explicitly marked as a bug fix with no new REQ. | `main-session` | `resolved` |
| C12 #170 unreachable; annotations disagree | medium | #170 changed `include` -> `partial` (the write half is untestable per EXP-006) with the reasoning recorded in the Notes cell. 6.6 gains `#170 (partial)`; #233 annotated on 1.3. `verify-reconcile` added as an approval preflight in 6.6's text. | `main-session` | `resolved` |
| C13 SC33 files_checked:0 trap | medium | Split into SC33 (`doc_lint --classify` asserting the file is selected, per the always-loaded rule's prescribed remedy) and SC33b (`yf skill-dir yf-okf-hygiene`, the actual resolver). | `main-session` | `resolved` |
| C14 no enumerated-something guard | medium | Issue 3.1 now emits `bundles_checked` with a `--min-roots N` guard; SC10 and SC21 assert `--min-roots 30`. SC9 rewritten as a RED fixture — a `complete` bundle carrying a close-out violation must produce at least one error. | `main-session` | `resolved` |
| C15 superseded figures | medium | Motivation corrected to 9-of-30. SC12 corrected to the 140/247 baseline. D-1's unsourced "~423" removed and replaced with the measured 1634/1603 figures plus new Issue 0.12 to re-derive the real promotion count; the collision with the stale spec line is named explicitly. | `main-session` | `resolved` |
| C16 Approach understates 2.5 / 4.5 | low-medium | Approach spine gains a clause for 2.5 (new public CLI verb) and 4.5 (possible 18th document type). The "does not do" bullet reworded to "re-judge history's severities", with a paragraph reconciling it against Epic 5's in-place rewrite. | `main-session` | `resolved` |

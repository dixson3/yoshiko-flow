---
type: Review
okf_spec: OKF-PLAN
id: pass-6
description: "Red-team pass 6 — APPROVE. A post-approval cross-plan concurrency audit raised four defects; three reproduced and are repaired, one (D4, 'gates are never poured as beads') is REFUTED by measurement — its root cause is that `bd list --all` structurally excludes gate-typed beads. R12 rewritten to the measured mechanism with a sequencing decision; #290's crash brought in scope; rule D's `<=10` test disambiguated."
---
# Red-team pass 6: plan-057-james-dixson-9ecf1c

## Verdict: APPROVE

> **All 4 defects resolved. Zero blockers remaining.** Three reproduced and were repaired; one was
> refuted and its refutation became a requirement.

**Date:** 2026-08-29 · HEAD `a3add5f` · Reviewer: delegated adversarial agent (read-only w.r.t. code;
sandbox spikes only, no residue)

Trend: **17 → 18 → 12 → 8 → 6 → 4** concerns; **8 → 6 → 2 → 2 → 0 → 2** blockers.

This pass was commissioned *after* APPROVE, on defects a cross-plan concurrency analysis found that
five prose passes had read past. Two of the four (D1, D2) were genuine blockers. Per this plan's own
review discipline — passes 2, 3 and 4 each found the prior pass's repair measurably false — **every
claim below is backed by a command that was run, and each of the four incoming claims was re-measured
before being recorded as either true or false.** Two were not what they were reported to be.

## Strengths

**The three real defects were all confirmed by execution, and two reproduced to the digit.**

- **D2 reproduced exactly.** `reindex_check` clean on **33 of 33** index-bearing bundles while
  `reindex_write` raises `AttributeError` on **4** — plan-054, **plan-057**, plan-058, plan-059 — with
  the reported per-bundle offending-line counts **1 / 6 / 14 / 1** matching to the digit.
- **D1's merge conflict is real and was produced, not argued.** `git merge-file` over
  base/ours/theirs on `docs/plans/plan-059-*/index.md` returns **rc=1** with genuine conflict markers.
- **D4 was refuted, and the refutation is worth more than the finding would have been.** The reported
  measurement was reproducible and the *inference from it* was wrong; the mechanism that made it wrong
  is now a hard requirement on the instrument SC0c depends on.
- **The mechanical battery is green after every edit**, including two instrument outputs the edits
  themselves moved (`check-req-coverage`'s split, the criteria count) — both propagated.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| D1 | R12 refuted on its mechanism and blind to the file that actually collides | **high (blocker)** |
| D2 | Issue 1.4's "re-repair the corpus" calls a verb that crashes on plan-057's own bundle | **high (blocker)** |
| D3 | Issue 1.1's quoted bound is underdetermined, and SC2 reads it | med |
| D4 | "No gate is ever poured as a bead, so SC0c cannot be satisfied" | **refuted** |

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| D1 | high | **R12 claimed "adjacent, not contested — different functions in different files". Measured false on both halves.** `plan_manager.py:906` is `for member, desc in _INDEX_MEMBERS: okf.add_index_entry(plan_dir, member, desc)` — plan-059's Issue 2.4 supplies the DATA, plan-057's Issues 1.2/1.3 rewrite the FUNCTION. They are two halves of one generator. R12 also named no contested file: `docs/plans/plan-059-james-dixson-55137e/index.md` is written by both, and `git merge-file` returns **rc=1** with real markers. Two semantic conflicts a clean merge hides — **(a)** Issue 1.2's chain omitted the caller-supplied `desc` entirely, which **four** callers pass (`plan_manager.py:906`, `plan_manager.py:1836` — an operator's explicit `--description` — and `index_manager.py:247`/`:279`); measured, **150** corpus entries carry the authored `_INDEX_MEMBERS` string and all 150 would be replaced, as would **32 of 44** research entries' `[phase]` prefixes, the convention this plan's own Motivation calls the corpus's best. Only **7.8%** (16/204) of indexed `.md` members carry a `description:` key, so the H1 branch is the live one, and `escalations.md` carries none — its authored text resolves to the H1 `Escalations`. **(b)** `_ensure_index_lists_member` (plan_manager.py:813-846) is a **second, independent bullet writer** that never calls `add_index_entry` and hardcodes its own format at 826-827 — and it is precisely the writer plan-059's Issue 2.4 calls. | **resolved** — R12 rewritten to the measured mechanism, promoted **med → high**, naming the contested file and both semantic conflicts. **Sequencing decision recorded as D-13: plan-059 executes and merges FIRST, then plan-057.** Issue 1.2's chain restated as `caller-supplied desc -> frontmatter description: -> H1 -> bare`, with the boilerplate question explicitly handed to SC3's ratio work rather than smuggled into a fallback chain. Issue 1.3 extended to cover the second writer. |
| D2 | high | **`okf.reindex_write()` — the verb Issue 1.4's "re-repair the corpus" calls — crashes on this plan's own bundle.** Re-measured: `reindex_check` clean **33/33**; `reindex_write` `AttributeError` on **4** (plan-054, plan-057, plan-058, plan-059). Cause traced: `_split_listing` (okf.py:1585-1598) returns the **contiguous run from the first bullet to the last**, so a blank line or `## Subheading` inside that run reaches the loop at okf.py:1645-1646, where `m = _INDEX_ENTRY_RE.match(ln)` is dereferenced with no `None` guard. Offending lines: 1 / 6 (4 blank + 2 `##`) / 14 / 1. The corpus gate is green while the paired repair verb cannot run on the plan that commissions it. | **resolved — plan-057 fixes it itself, in Issue 1.4.** Judged against Issue 1.3's "do not touch `reindex_write`'s preserve-and-append contract": `_split_listing`'s own docstring already promises prose is "carried through verbatim", so tolerating prose *interleaved within* the run **completes** that contract rather than altering it — a narrow, explicit carve-out. **No new REQ**, on the precedent `plan_manager.py:837` records verbatim for the same class of index defect (a bug fix to shipped REQ-OKF-072). Alternatives rejected in the text: depending on #290 puts a mandatory step behind an unowned upstream issue; a "documented precondition" documents a crash and proceeds. Issues 1.1-1.4 already edit `_shared/okf.py`, so marginal blast radius is zero. **SC6b** added, routed through the existing `check-pytest-ran.sh` — **no new instrument, so `--require 16` and SC0's `test -x` list do not move.** |
| D3 | med | **The "max 30 regardless of bundle size" bound is NOT stale — but it is UNDERDETERMINED, which is worse, and the reported refutation was itself wrong.** The claimed "34 for plan-053" does not reproduce. Simulating rule D over all **64** enumerated bundles: under a **recursive** file-count reading, total 867, median 12, **max 30**, plan-053 = **28**; under a **direct-children** reading, total 897, median 12, **max 33**, plan-053 = **33**. That second reading is where the reported figure came from. Issue 1.1 never said which one `"holds <=10"` means, so SC2's fate was a coin flip on the executor's reading — the exact defect class this plan's history keeps catching. Separately, 30 is an **empirical corpus maximum with zero margin**: four bundles sit at exactly 30 (plan-048, -049, -055, -059) and rule D bounds a bundle's top-level files not at all. | **resolved** — Issue 1.1 pins the **recursive** reading (the one EXP-003 calibrated against: it is what collapses `references/` at 391 files and `reviews/` at 108 to bare stubs, and the only one reproducing EXP-003's max 30) and re-quotes today's figures for both readings. **SC2 restated to the PER-DIRECTORY invariant — no subdirectory contributes more than K=10 entries** — measured at exactly 10 (`plan-049/references`), structural rather than empirical, and true under **both** readings. The test name moves to `selection_rule_per_directory_bound`. |
| D4 | — | **"No gate is ever poured as a bead in this repository, so SC0c cannot be satisfied." REFUTED.** The reported measurements reproduce exactly — `bd list --all --json` returns **1951** beads with no `gate` type and **zero** carrying `metadata.test_class` — but the inference does not follow. **`bd list --all` structurally excludes gate-typed beads.** `bd list -t gate --all --json` returns **179** gate beads (176 closed, 3 open), of which **42** carry `test_class` (24 `probe`, 15 `consent`, 2 `manual`, 1 `build`) and 42 carry `cwd` (26 `repo-root`, 16 `worktree`). plan-059 poured **4** of its 5 gate sections as beads — the subordinate's "4 gates wired" was correct; only the Start Gate is not a bead — and both of its `auto`+`executable` gates (`yf-mol-vltm.8`, `yf-mol-vltm.9`) are `test_class: probe`, exactly the directive. `bd show yf-mol-vltm.9` renders the full metadata block. **SC0c's premise holds and the POUR directive is not inert.** SC0c's discriminator was independently re-run: `plan_extract` gives 6 gates, of which `type == auto AND test_kind == executable` yields exactly **3**. | **refuted — and kept as a requirement.** The refutation is the instrument's hardest constraint, so it is now recorded in **both** SC0c and Issue 1.0: **`check-gates-poured-probe.sh` must query `bd list -t gate --all`.** The plain `--all` form sees an empty set (permanently red, or trivially green — the vacuity SC0c exists to prevent), and the bare `-t gate` form misses every gate already resolved. The observer's own measurement is the proof that the natural enumeration is the trap. Note that pass 3's sandbox `bd create -t gate` round-trip proved the mechanism but never the pour; this pass proves the pour, against the live DB. |
| I1 | low | **Incidental: `check_okf_index_drift.py --root` with an ABSOLUTE glob violates its own exit contract.** Measured: `--root "$PWD/docs/plans/*"` raises an unhandled `NotImplementedError("Non-relative patterns are unsupported")` from `pathlib` at line 143 and exits **1** — which under that script's documented `0 clean / 1 drift / 2 INCONCLUSIVE` contract means *drift*, so a harness fault is reported as a corpus finding. That is worse than a bare traceback: the code is wrong but in-contract. **The reported blast radius does not hold, however** — SC7 passes no `--root` at all, and SC19 targets `okf_hygiene.py` with relative roots. No criterion in this plan is live on it. | **resolved as a precedent, folded into Issue 1.0.** Recorded there as a defect the four new instruments and Issue 2.2's `okf_hygiene.py audit --root` must not reproduce, with the correct code (2, INCONCLUSIVE) named. Not filed upstream: read-only pass, and D-9's file-nothing rule does not reach in-repo scripts — but this is an in-repo script no issue in this plan owns, so it is left as a note rather than a deliverable. |

## Missing

- **The `plan.md` ↔ instrument-output diff** — named Missing in passes 2, 3, 4 and 5, and **it would
  have caught a real drift in this pass**: my Issue 1.4 edit added a `REQ-OKF-072` citation, which
  silently moved `check-req-coverage`'s verbatim output from `23 transitive, 0 name a REQ` to
  `22 transitive, 1 name a REQ` — a quote SC1 pins. Caught here only because the battery was re-run
  and the output read. Tracked as **#289 / RE-001**; still the longest-running open item.
- **A cross-plan contested-file instrument.** D1 was found by an out-of-band human analysis, not by
  anything in the repo. Nothing compares two in-flight plans' write sets. R12 is now correct *as
  prose*; the next pair of concurrent plans gets no such luck.
- **The producer↔consumer path check** — run by hand in four consecutive passes, clean every time,
  still not an instrument.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start | OK |
| Predecessor complete | **Sound** — `plan-056` re-verified `status: complete`; directive parses in full, `unparsed: []` |
| Backfill authorization | **Sound** — `Test: none` correctly classified `test_kind: sentinel` |
| Upstream network reachable | **Sound** |
| Verification harness ready | **Sound** — red today (exit 1, "checked 9, --require 16"); evidence from 1.0, which it does not block |
| Reconcile | OK |

6 gates, `unparsed: []`, `gate_consistency` exit 0 over 30 edges. SC0c's discriminator
(`type == auto AND test_kind == executable`) re-measured at exactly **3**, unchanged by this pass's
edits. **The pour path is now verified end-to-end against the live DB rather than a sandbox** (D4).

## Upstream Assessment

Unchanged. **#290** moves from "filed, unscheduled" to **in scope**, discharged by Issue 1.4 and
asserted by SC6b — the one substantive change. #289 remains `deferred` as RE-001, and this pass
supplies fresh evidence for it (see Missing). The four `partial` rows still reach their end state
through 3.5.

## Mechanical Battery

Re-run after every edit in this pass.

| Instrument | Result | Exit |
| :-- | :-- | --: |
| `plan_manager.py audit` | clean | **0** |
| `gate_consistency.py` | no finding | **0** |
| `doc_lint.py` — `plan.md` | `files_checked 2`, PASS, 0 findings | **0** |
| `doc_lint.py` — all six reviews | `files_checked 1`, PASS, 0 findings each | **0** |
| `plan_extract.py` | `unparsed: []` · 6 gates · 28 issues · **30 criteria** (was 29, +SC6b) · 30 edges · 12 risks · 4 epics · 8 upstream | 0 |
| `check-req-coverage.py` | `23 non-Epic-0 issue(s); 5 direct Epic-0 dep, 22 transitive, 1 name a REQ, 0 declared bug fix` | **0** |
| `harness-selftest.sh --require 16` | `checked 9, --require 16 (0 absent)` — **red for the stated reason**; evidence from Issue 1.0, which the gate does not block | 1 |
| `check_okf_index_drift.py --min-roots 60` | `64 bundle(s) enumerated; no root-index drift` | **0** |
| `_shared/sync.py --check` | clean | **0** |
| `okf.py check` | clean | **0** |
| `ready-check` | `READY (last red-team APPROVE at pass-5 + audit pass)` | **0** |

Counts that moved this pass, propagated to every surface that carries them: **criteria 29 → 30**
(SC6b); **`check-req-coverage`'s covered-by split 23/0 → 22/1** (SC1's verbatim quote, updated);
**decisions 12 → 13** (D-13). `--require 16` and SC0's `test -x` list are deliberately **unchanged** —
SC6b adds no instrument.

## Why APPROVE

Two of the four incoming defects were genuine blockers and both are repaired against measured
mechanism rather than against the description they arrived with. D1's repair names the contested file
and produces the conflict; D2's repair is scoped by reading the contract it was said to violate and
finding it *completed* rather than breached. D3 turned out to be a sharper defect than reported — not
a stale number but an undetermined rule — and its repair replaces an empirical maximum with a
structural invariant, which is strictly the more durable of the two.

D4 is the one to read carefully: its measurements were correct and its conclusion was not, because
`bd list --all` cannot see the object it was counting. It is recorded as refuted, with the live-DB
evidence, and the mechanism that produced the false negative is now a stated requirement on the
instrument SC0c depends on. A pass that had accepted it would have deleted a sound criterion.

Nothing in this pass required a new instrument, so the harness arithmetic five passes converged on is
untouched. Every mechanical instrument in the repo is clean, and the two figures these edits moved were
caught by re-running the battery — which is precisely the gap #289 exists to close.

---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: Red-team pass 2 (second independent, via Agent) — REVISE, 15 concerns, 6 high; 9 of 14 pass-1 resolutions reproduced by execution
---

# Red-team pass 2

## Verdict: REVISE

**Second independent pass, scoped to reproducing pass-1's resolutions by EXECUTION.**

## Reproduction of pass-1's 14 resolutions

| Class | Count | Concerns |
| :-- | --: | :-- |
| **(a) landed and correct** | **9** | C2, C6, C7, C8, C9, C11, C12, C13, C14 |
| **(b) recorded but absent** | **1** | C10 |
| **(c) landed at one site, defect survives elsewhere** | **4** | C1, C3, C4, C5 |

**9 of 14.** All four (c)-class failures are **RE-002's shape** — a global property repaired at
the one site the reviewer named. That is the same diagnosis plan-052 recorded against its own
review process, recurring here at pass 2 rather than pass 4.

## What reproduced cleanly

- **C2** — the derivation returns **9**, all renamed controls match, and the shared `208`/`210`
  numeric prefixes do **not** collide (`sort -u` keys on the full string). The loose form still
  returns 11, so the anchoring remains load-bearing and correct.
- **C6** — 7.1's ancestor set recomputed from the poured edges: **38 ancestors = every
  non-Epic-7 issue**; the "not an ancestor" set is **empty**.
- **C7** — inversion landed, **no cycle**, and the claim that every site 5.4 widens to exists
  today is confirmed.
- **C5's arithmetic** reproduces **exactly** — roots 12/5 files, stamp 5/4, and 0.2's `touches`
  is precisely the 5 roots files.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C15 | **high** | **`--verify-all` survives at SC2**, the exact "not a verb" defect C1 was filed about — spiked → **exit 2**. Worse, the gate **Condition** demands non-zero *and non-2* while 1.1(a) specifies only non-zero, and in the adopted harness `_append` runs **before** the rc check: `record-red` on an exit-2 fixture prints `RED observed`, returns 0, and writes an `rc=2` line that `_has_record … nonzero` will match. **A record-time guard cannot un-write the record.** `verify-red-all`'s manifest-derivation duty is also unstated, downgrading pass-10 C93's protection from executed to prose |
| C16 | **high** | **SC13 still describes the verifier run C3 established is impossible** — it reads "plants the divergence, **runs the verifier**, asserts FAIL, and **reverts**", contradicting the issue (1.6b) that builds it, which replaced the revert with a `mktemp -d` copy |
| C17 | **high** | **1.6b's assertion is measurably unsatisfiable, and EXP-004's premise is REFUTED.** "Every selected target contains a status literal" measures **2 of 23** agent files and **3 of 19** SKILL.md; after 5.4's widening it gets **worse — 6 of 33**. And EXP-004's claim that *no* agent file carries a status literal is false: `coordinator.md:238` and `reconciler.md:64` both carry `` `complete` ``. The edge is weak because `complete` **is in** the vocabulary (the subset passes), not because the set is empty — a different defect needing a different control |
| C18 | **high** | **The roots renumber is scoped to `skills/yf-plan/`; two roots-meaning citations survive in the repo-root `SPEC.md`** — including **`SPEC.md:919`, inside the body of `REQ-YF-PRE-004a`**, a live normative requirement. True live set is **14 sites in 6 files**. The over-correction is ironic: C5 was about exp-007 conflating the two `SPEC.md` files, and the fix excluded the repo-root one entirely. Also, 1.6c asserts a grep "returns only stamp-meaning sites" — **no grep can decide meaning** |
| C19 | **high** | **SC16 names a script path that does not exist.** `uv run scripts/change_validation.py` → measured **exit 2**, `Failed to spawn`. The real path is `skills/yf-change-validation/scripts/…`. The plan's FULL-tier criterion is unsatisfiable — **a #210 instance inside the plan that exists to close #210's class**, and 3.5's own checker would flag it |
| C20 | **high** | **`ready-check` is RED**: pass-1.md carried no parseable `## Verdict:` line (REQ-PLAN-071), so approval was blocked for a reason stated nowhere in the bundle — #116's exact failure mode, in the file written to close a red-team loop |
| C21 | **high** | **Issue 5.1's `touches` omits 5+ files its own prose names**, and **Epics 4 and 5 have no vendor-sync issue** though both touch `_shared/`. Epic 2 has Issue 2.3 precisely because patching `_shared/` alone fails the byte-identity gate |
| C22 | medium | **R1 and 4.3 name two `okf.py` consumers; `sync.py` declares four** — the omitted two are `yf-plan` (this plan's own subject) and `yf-okf` |
| C23 | medium | **"EXP-003's existing prototype" is not a retrievable artifact.** `assets/` is empty, the finding records no path, and no worktree remains. Absent it, 1.6's RED reverts to the absent-instrument red C10 was filed about |
| C24 | medium | **SC8c is weak on three axes and tests the wrong case**: `grep -q 'state'` is satisfied by any constant literal; it hard-codes another plan's live bead state (the "cannot run in any repo but this one" defect 3.4 exists to fix); and plan-052's epic is **healthy**, while 4.2's defect is that a **dangling** ref is invisible |
| C25 | medium | **SC19 is structurally unable to fail** — `stamp-tracker` is specified **fail-soft** (exit 0 with no epic and no tracker), measured exit 0 today |
| C26 | medium | **SC1 cannot reach exit 0 at its declared discharge point** — `M^1..M^2` returns 2 pre-merge by its own specification, and SC1 is discharged by pre-merge issues only |
| C27 | low | **13 issues are named by no success criterion**, including **1.6c** (added by C5's own resolution) and **5.1**. Cause measured in `plan_extract`: `discharged_by` keeps `'1.1-1.7'` as a **literal string**, unexpanded |
| C28 | low | **SC4 cannot observe 3.2** — `test_sync.py` exits 0 today, before `pour_fidelity.py` has any vendoring entry. SC6 already guards this with `test -f`; the two are inconsistent |
| C29 | low | **SC12b's command under-asserts its own text** — it claims "no pre-existing document gains a finding" but only proves errors remain 0 |

## Missing

- No issue owns the **repo-root `SPEC.md`** roots-citation move (C18).
- No issue owns **`_shared/sync.py` regeneration for `doc_lint.py` / `okf.py`** (C21).
- `assets/` holds **no harness, no fixtures, no prototype** — every Epic-1 control's stated
  source artifact is unretrievable (C23).
- **Issue 0.3 amends `REQ-STATUS-002`'s count, but that requirement counts `py update-status`
  CALL SITES in `SKILL.md`, not status values.** Adding `abandoned` adds no call site;
  amending it would break a passing grep.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start Gate | fine |
| **RED observed before any fix** | **No cycle; C1's inversion is genuinely gone** — Blocks = {2.1, 3.1, 4.1, 5.1, 6.1}, and the builder (1.1) plus all nine controls sit outside it. Two residual defects: the Condition is **stricter than the Test**, and the harness's append-before-check ordering lets an exit-2 record satisfy `nonzero` (C15) |
| Deploy consent | correct; 7.4 now carries `--allow-permissions-write` |
| Reconcile Gate | fine — carries a `bd list … jq -e` Test |

## Upstream Assessment

Unchanged and sound. #214's `include` is now correctly scoped **within** `skills/yf-plan/` but
still under-scoped **repo-wide** (C18).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C15 | high | SC2's `--verify-all` corrected to `verify-all`. 1.1(b) rewritten from *reject* to **unrecordable**: the rc check moves ahead of `_append`, or `_has_record` gains a `want=red` mode excluding 2 — the reviewer's point that a record-time guard cannot un-write a record is exactly right. 1.1(c) now makes `verify-red-all` **perform** the manifest derivation rather than prose-confirm it. | `main-session` | `resolved` |
| C16 | high | SC13 rewritten to match 1.6b — no verifier run, no revert, and the property restated as what the edge is for. | `main-session` | `resolved` |
| C17 | high | **Accepted as a second refutation of EXP-004.** 1.6b re-derived from the real property: a status literal *outside the declared vocabulary* must be caught. The finding's "target set is empty" claim is corrected in place — `coordinator.md:238` and `reconciler.md:64` carry `` `complete` ``, so the edge is weak because `complete` **is in** the vocabulary. 5.4 now picks **one** branch (replace the target node); the widening branch was measured to make the ratio *worse*, so it could not have been the fix. | `main-session` | `resolved` |
| C18 | high | Repo-root `SPEC.md` added to 0.2's `touches` — **14 sites in 6 files**, not 12 in 5. SC15 rescoped repo-wide. 1.6c rewritten around an **explicit file:line allowlist**, since no grep can decide meaning. Recorded honestly: this is the *second* time the scope was set too narrow, and the first narrowing was itself C5's fix. | `main-session` | `resolved` |
| C19 | high | SC16's path corrected to `skills/yf-change-validation/scripts/change_validation.py`. The row now names what it was — a #210 instance inside the plan closing #210's class, which Issue 3.5's own checker would have caught. | `main-session` | `resolved` |
| C20 | high | `## Verdict: REVISE` added to pass-1.md and carried in this file. `ready-check` re-run: it now reports the correct blocking reason (a REVISE awaiting a later APPROVE) instead of a parse failure. | `main-session` | `resolved` |
| C21 | high | 5.1's `touches` widened from 3 files to 11. **New Issue 5.0** regenerates the `_shared/` vendored copies Epics 4 and 5 perturb — the analogue of Epic 2's Issue 2.3, which Epics 4-5 lacked entirely. 7.1's `depends-on` re-pointed at 5.0. | `main-session` | `resolved` |
| C22 | medium | R1 and 4.3 corrected to the four consumers `sync.py` declares — yf-plan, yf-research, yf-incubator, yf-okf. | `main-session` | `resolved` |
| C23 | medium | **New Issue 1.0** commits the investigation's sandbox artifacts into `assets/fixtures/` before anything depends on them, and 1.1 now depends on it. Without this every Epic-1 control's source artifact was unretrievable. | `main-session` | `resolved` |
| C24 | medium | SC8c rewritten to assert against a **fixture bundle with a dangling pointer**, with a new Issue 1.3a building it. The earlier form tested plan-052's *healthy* epic — the one case that was never broken — and hard-coded another plan's live bead state. | `main-session` | `resolved` |
| C25 | medium | SC19 rewritten to assert the **end state** (`bd show … jq -e .external_ref`) rather than the verb's exit code. `stamp-tracker` is specified fail-soft and exits 0 with no epic and no tracker, so the earlier clause could not fail. | `main-session` | `resolved` |
| C26 | medium | SC1's `Discharged-by` extended to **7.1**, post-merge, and the row states the pre-merge INCONCLUSIVE as expected rather than leaving it to be discovered. | `main-session` | `resolved` |
| C27 | low | SC1's and SC2's range forms enumerated explicitly — `plan_extract` keeps `'1.1-1.7'` as a literal string, so the coverage was invisible. **New criterion SC11b and new Issue 1.3b** cover Issue 5.1, which had none: a 16-site edit could have landed partial and green. Orphans measured down from 13 to 3. | `main-session` | `resolved` |
| C28 | low | SC4's command now carries the `test -f skills/yf-plan/scripts/pour_fidelity.py` guard SC6 already had. | `main-session` | `resolved` |
| C29 | low | SC12b's unproven second clause **dropped rather than left standing** — the command compares no finding-set, so the claim was unearned. | `main-session` | `resolved` |

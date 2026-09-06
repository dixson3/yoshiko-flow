---
type: Review
okf_spec: OKF-PLAN
description: 'Review pass-2 - plan-065 red-team cycle 2, verdict REVISE, 16 concerns, one high-severity data-loss path introduced by pass-1 remediation'
---

# Review pass-2 — plan-065 (cycle 2)

## Verdict: REVISE

**Status: all 16 concerns resolved.** C1 and C2 were both accepted after independent reproduction. Re-dispatched as pass-3.

## Strengths

- **All 14 pass-1 resolutions textually landed**, each verified against current `plan.md` line
  numbers. No resolution was claimed without landing.
- **DAG structurally clean**, hand-checked per #361: 38 issues / 42 edges, zero cycles, zero
  self-edges, zero dangling refs, **zero forward-dependencies**.
- **Every quantitative claim reproduces**: `legacy: 8`; default backfill 8 halted;
  `--reconcile-objective` 7/1; `okf.py check plan-010` -> `findings: 12`; plan-030's phase log
  **exactly 10** bullets; all 8 `README.md` are 38 lines differing **only** in the H1 id and the
  `>` objective line — the Approach's "nothing bundle-specific to lose" is exact.
- **The Epic 3 round-trip holds under spike** — byte-identical tree sha256; `restore --bundle`
  exists and works.
- `doc_lint` PASS, no `E` findings.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **Pass-1's C2 fix (Issue 4.3a) breaks Issue 4.4, silently, with total data loss — measured.** Committing the backfill removes `README.md` from HEAD. `restore --bundle --apply` then reports `verdict: pass`, `exit: 0` while the `created` unlink pass deletes `index.md`/`log.md` and the `git checkout` of `README.md` fails unchecked (`okf_hygiene.py:1367-1372`). Bundle ends with no README, no index, no log. Epic 3 cannot catch it: 3.2->3.3 has no commit between apply and restore, unlike 4.2->4.3a->4.4 |
| C2 | **high** | **SC4's checker asserts the INVERSE of what 4.4 must prove.** Issue 0.4d asserts pre- and post-reversal tree sha256 are **equal** — but a correct reversal makes them differ; only a no-op restore makes them equal. As written SC4 rewards exactly the failure mode C1 produces |
| C3 | medium-high | **C3 and C4's resolutions contradict: SC14 is unsatisfiable for 4 of 7 progress checkers.** The C4 fix relocated the missing-file problem from the checker to the checker's *input* — 0.4c/0.4d/0.4e read evidence files that do not exist pre-transform, and 0.3 reads a post-transform `index.md`. All raise `FileNotFoundError` at Epic 0. Also blocks 0.5: there is no `apply-result.json` to mutate |
| C4 | medium-high | **Both new order-sensitive issues are unconstrained in the DAG.** 0.6 is not an ancestor of 4.1/4.2; 0.5b is an ancestor of nothing. Prose is not an edge, and both data are irrecoverable once destroyed. SC14's rationale is also wrong: SC7/SC8's conditions become true at Epic 2 / Epic 1, not Epic 4 |
| C5 | medium | **C14's resolution names a mitigation that cannot mitigate.** `mixed_run = bool(mutated) and bool(halted)` is entirely redundant with `halted == 0` and carries zero information about the 62 conformant bundles. An acknowledged gap was converted into a false claim of coverage — strictly worse |
| C6 | medium | **SC1's metric is blind to C1's failure mode.** `legacy` excludes `unclassifiable`; the wrecked bundle classifies `unclassifiable` and `audit` reports `legacy: 0`, exit 0. SC1 passes over a destroyed bundle. SC1 also omits `--min-roots`, so an enumeration of zero also yields `legacy: 0` |
| C7 | medium | **No gate authorizes Epic 6's outward-facing writes.** Both capability gates block `epic:4`; nothing blocks `epic:6`. The plan gates a reversible local operation and leaves the irreversible public one ungated |
| C8 | medium | **SC13/SC14 are `manual:` on precisely the excuse C4 rejected.** A table of `(mutation, exit)` pairs is recorded evidence, identical in kind to `apply-result.json`; the only difference is Markdown vs JSON |
| C9 | low-medium | **Issue 5.2b prescribes the remediation the tool disclaims.** `reindex --apply` gives the four `.json` artifacts BARE bullets; `check_okf_index_drift.py:231` says verbatim that this "degrades the artifact while passing the check — it is not the operator remediation" |
| C10 | low-medium | **SC9 is asserted green-today; it is RED today, measured.** The FULL tier includes `okf-index-drift`, which now exits 1 because plan-065's own `index.md` lacks `reviews/pass-1.md`. Asserting a criterion's colour without running it is the exact lapse R10 forbids |
| C11 | low-medium | **No issue commits Epic 0's eight checkers, the four `findings/*.json`, or 4.4's residue.** 4.1 and 4.3a are both explicitly scoped to exclude them, yet 5.5 runs the FULL tier "over the merged tree" |
| C12 | low-medium | **SC12's "landing diff" has no pinned base**, so its checker is vacuously green at Epic 0 — the diff is empty |
| C13 | low | 0.4c asserts "8 explicit bundle rows" in the run JSON, but that file holds one row per bundle checked (70); only the record holds 8 |
| C14 | low | 0.4b's "MEASURED: the bare drift check exits 0 today" no longer reproduces — it now exits 1. The argument survives, the measurement does not |
| C15 | low | Motivation says `checked 69`, Investigation Findings says 70, current is 70 — two figures in one document, the defect class this plan's own #322 disposition names |
| C16 | low | Orphan-issue count rose 21 -> 25 despite C10's resolution; all of Epic 3 is named by no criterion (legitimately — the capability gate discharges it — but the metric moved the wrong way) |

## Missing

- A checker asserting the 62 conformant bundles are **untouched** by the corpus apply
- A rehearsal of the **exact** 4.4 sequence (commit, then `restore --bundle`) — the difference is where C1 lives
- A human gate on Epic 6's outward-facing writes
- DAG edges expressing the two prose-only ordering constraints
- A commit issue for the plan's own deliverables
- A **fourth** engine defect for 6.1: `restore`'s unchecked `git checkout` return code (`okf_hygiene.py:1371-1372`), which is what makes C1 silent

## Gate Assessment

**Sandbox rehearsal green** — reachable, correctly positioned, keys and cwd now specified. **New
defect**: it certifies a rehearsal whose restore step (3.3, uncommitted) is *not the sequence Epic
4 runs* (4.4, post-commit). It green-lights the C1 defect by construction.

**Corpus apply authorization** — sound, correctly worded and positioned. The Epics 1-2
ungated-by-design rationale resolves pass 1's note.

**Start Gate / Reconcile Gate** — standard. But the Reconcile Gate is `auto` and Epic 6's outward
writes precede it with no human gate anywhere (C7).

## Upstream Assessment

Dispositions sound and `upstream-triage.md` now fully populated (6/6, 0 empty), mirroring plan.md
without contradiction. #359's four criteria still map completely; D3's `--root` requirement is now
stated in 4.4.

**The residual is severe**: SC4 is the criterion #359 names most specifically, and C1/C2 mean it is
currently dischargeable only by an operation that does not reverse cleanly, verified by an
assertion that would reject a clean reversal. Of six dispositions, the one carrying the primary
issue's headline criterion is the one the revisions broke. That is why this is REVISE.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Accepted; reproduced independently in the main session before acting.** Sandbox spike confirms `verdict: pass`, `exit: 0` with README/index/log all gone; the no-commit control restores correctly. Fixed by ORDERING, not an engine change (SC12): Issue 4.4 now runs `restore` on the UNCOMMITTED post-apply tree and the commit moved to Issue 4.5 (`4.5 depends-on 4.4`, verified by ancestor computation). A hazard note in the Approach records the measurement and states that post-commit the reversal verb is `git revert`, never `restore`. Recorded as `findings/exp-003-post-commit-restore-loss.md`; filed as the fourth engine defect in Issue 6.1. | `main-session` | `resolved` |
| C2 | high | **Accepted — the assertion was backwards and would have rewarded C1's failure mode.** Issue 0.4d now asserts the real round-trip invariant: `post_backfill == post_reapply` AND `post_reversal == pre_backfill` AND `post_reversal != post_backfill`, with the last conjunct called out as load-bearing. Issue 4.4 records all four hashes. | `main-session` | `resolved` |
| C3 | medium-high | **Accepted — the C4 fix relocated the problem rather than removing it.** Added Issue 0.4f: every checker takes a uniform missing-input contract (non-zero exit with a structured `{"verdict":"FALSE","reason":"input absent"}`, never a traceback) and accepts `--input <path>` so negative controls point at synthesized fixtures without polluting `findings/`. | `main-session` | `resolved` |
| C4 | medium-high | **Accepted — prose is not an edge.** Added Issue 1.0 carrying `depends-on: 0.6, 0.5b`, with Issues 1.1 and 2.1 depending on it. Verified by ancestor computation that 0.6 and 0.5b are now ancestors of 1.1, 2.1 and 4.2. SC14's rationale corrected to name Epic 1 and Epic 2 as the destroying steps for SC8/SC7. | `main-session` | `resolved` |
| C5 | medium | **Accepted — an acknowledged gap had been converted into a false claim of coverage.** Issue 3.1 now states plainly that `mixed_run` does NOT cover the 62 conformant bundles (it is redundant with `halted == 0`), and new Issue 4.3b asserts real coverage: `bundles_checked == 70`, every non-target row reports a skip, and `git status --porcelain` names only the 8 targets plus the record. | `main-session` | `resolved` |
| C6 | medium | **Accepted — SC1 would have passed over a destroyed bundle.** Added Issue 0.4h authoring `plan065_audit_strict.py`, asserting `legacy == 0` AND `unclassifiable == 0` AND `hybrid-partial == 0` AND `bundles_checked >= 70`; SC1 restated against it. The bundle-count floor also closes R9's enumerate-nothing vacuity. | `main-session` | `resolved` |
| C7 | medium | **Accepted — the plan gated a reversible local operation and left the irreversible public one ungated.** Added a human `Capability Gate: Upstream write authorization` blocking `epic:6`, requiring the four drafted issue bodies and the exact close set to be presented first. | `main-session` | `resolved` |
| C8 | medium | **Accepted — this was the same excuse the plan rejected for SC4/SC5, and the only difference was Markdown versus JSON.** Issue 0.5 now emits `findings/negative-controls.json`; new Issue 0.4g authors `plan065_negative_controls.py` asserting ten rows with `exit != 0` and a recorded FALSE per progress checker. SC13/SC14 remain `manual:` only where they assert observation of a tree that no longer exists. | `main-session` | `resolved` |
| C9 | low-medium | **Accepted.** Issue 5.2b now requires authoring a real one-line description for every `.json` artifact after `reindex --apply` and asserting no bare bullet remains, quoting `check_okf_index_drift.py:231`'s own disclaimer. Applied the same discipline to this bundle immediately: reindexed and verified zero bare bullets. | `main-session` | `resolved` |
| C10 | low-medium | **Accepted — I asserted a criterion's colour without running it, one paragraph after stating the rule forbidding exactly that.** A correction paragraph now records that SC9 was RED at review time because of this plan's own index drift. Repaired: reindexed the bundle; `check_okf_index_drift.py` now exits 0 with `drifting: 0`. | `main-session` | `resolved` |
| C11 | low-medium | **Accepted.** Added Issue 5.4b committing the plan's own deliverables — the ten checkers, every `findings/*` artifact, the reviews, and 4.4's residue — since 4.1 and 4.5 are both explicitly scoped to exclude them. 5.5 now depends on 5.4b and names it as the base for the merged tree. | `main-session` | `resolved` |
| C12 | low-medium | **Accepted.** Issue 0.4 now pins the diff base with `git merge-base origin/main HEAD` recorded to `findings/diff-base.txt`, so the checker is not vacuously green against an empty diff at Epic 0. | `main-session` | `resolved` |
| C13 | low | **Accepted.** Issue 0.4c restated: `transformed == 8`, `halted == 0`, `bundles_checked == 70`, and exactly 8 rows with `action == backfilled` — with an explicit note that the run JSON carries 70 rows and only the record carries 8. | `main-session` | `resolved` |
| C14 | low | **Accepted.** Issue 0.4b's claim restated tree-independently: `no_index` contributes nothing to the bare check's verdict. The snapshot exit code was removed precisely because it had already flipped for an unrelated reason. | `main-session` | `resolved` |
| C15 | low | **Accepted — this plan's own #322 disposition names unpinned corpus figures as a defect class.** Motivation table pinned to 70 with the measurement date and a note explaining the 69->70 transition. | `main-session` | `resolved` |
| C16 | low | **Accepted as a clarification.** Added a paragraph stating that Epic 3 is discharged by the `Sandbox rehearsal green` capability gate — a machine-enforced binding stronger than a criterion — so a reader counting criterion coverage does not read Epic 3 as uncovered. | `main-session` | `resolved` |

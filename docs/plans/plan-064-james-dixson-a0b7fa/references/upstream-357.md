---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #357 - plan-064-james-dixson-a0b7fa execution tracking'
---
# Upstream #357: plan-064-james-dixson-a0b7fa execution tracking

- **Number:** 357
- **Title:** plan-064-james-dixson-a0b7fa execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/357
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

> Plan: plan-064-james-dixson-a0b7fa | Bundle: docs/plans/plan-064-james-dixson-a0b7fa (repo-relative)
>
> Coarse tracking issue for plan-064, per this repo's one-issue-per-plan-scale-effort convention.
>
> ## What this plan does
>
> Repairs the `yf-okf-hygiene` backfill/restore engine so that the #316 corpus transform can be run
> safely by a follow-on.
>
> **#316's acceptance criteria (`legacy: 0`, a rehearsed `restore`) are deliberately NOT discharged
> here.** A sandbox rehearsal (EXP-001) measured that the transform cannot run at all and that its
> advertised rollback destroys data:
>
> - **8/8 target bundles halt** — 7 on `objective-divergence` (`plan.md`'s H1 grew during re-scoping
>   while `README.md`'s `>` line did not), and `plan-030` clears the dry run then halts under
>   `--apply` on `phase-log-loss`, **a guard the dry run never runs**.
> - **`restore --apply` is a `git checkout` with an unlink pass, mislabelled as record-driven.** The
>   `--record` file carries a before/after audit verdict and **no operations at all**. Three measured
>   paths destroy data while reporting `pass` / exit 0: a non-git tree, an untracked bundle, and
>   post-backfill edits.
> - **The crash journal is unsound and unreachable.** `recover()` has no CLI verb; a crash after
>   rename 1 leaves it reading `S1`, so recovery discards the transformed staging copy and reports
>   `recovered: true` with the bundle gone.
>
> ## Epics
>
> | # | Deliverable |
> | :-- | :-- |
> | 0 | SPEC-first amendments — 2 amendments (`REQ-OKFH-008`, `-010`) + 3 new ids (`-011`, `-012`, `-013`) |
> | 1 | #294 — gitignore-aware member enumeration (`_vcs_ignored`, ~27 LOC + 5-copy vendored fan-out) |
> | 2 | A record that records per-path ops; a `restore` that refuses instead of deleting |
> | 3 | A journal that is sound and reachable |
> | 4 | An honest dry run + `--reconcile-objective` |
> | 5 | Scope closure and honest handoff |
>
> 6 epics · 44 issues · 21 success criteria · 9 risks · 6 gates.
>
> ## Notable findings
>
> - **Two false-green tests.** `test_crash_recovery_all_states` (`REQ-OKFH-008`) and
>   `test_restore_round_trip` (`REQ-OKFH-010`) both pass today against code that violates the
>   requirements their `SPEC.md` §5 rows claim they cover. The first **hand-builds every journal
>   state and never invokes `backfill`'s swap** — it mocks the call site it exists to observe.
> - **Conformance defects, not SPEC gaps.** `REQ-OKFH-010` already mandates record-driven per-path
>   restore and `REQ-OKFH-008` already fixes the five states. Issues 0.3/0.4 amend those ids and
>   record the non-conformance rather than minting duplicates — which would have contributed to #298.
> - **The plan's own first fix was a regression.** Red-team pass 4 measured that writing `S3` before
>   rename 2 opens a **new** total-loss window the shipped buggy code does not have, because
>   `recover()`'s `S3`/`S4` branch `rmtree`s stash and staging without checking whether the bundle
>   exists. Issue 3.9 closes it; pass 5 verified the fix by executing it across three engine variants
>   and both crash seams.
>
> ## Review
>
> Five red-team cycles (34 concerns, all resolved), final verdict APPROVE. Reports are in the bundle
> under `reviews/pass-1.md` .. `pass-5.md`.
>
> ## Resolves
>
> - Closes #294 (gitignore-aware member enumeration).
> - Partially addresses #316 — files the follow-on corpus-transform issue that carries its original
>   acceptance criteria and the post-repair halt profile.
>
> ## Related
>
> - #247 — the `OKF-EXTENSION.md` drift-node rows and the uncovered fifth vendored `okf.py` are routed
>   there rather than absorbed here.
> - #318 / #320 / #321 — open P0/P1s in the `--skill` / member-resolution path this work borders.

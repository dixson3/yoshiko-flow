---
type: Review
okf_spec: OKF-PLAN
id: pass-6
description: Red-team pass 6 (sixth independent, via Agent) — plan-054; APPROVE
---

# Red-team pass 6

## Verdict: APPROVE

**Frozen-snapshot check: PASS** — `6c5d1248f8f3…` at start and end.

**pass-5 resolutions: 8 of 8 reached disk, 7 of 8 fully correct** (N4 landed its mechanism but
recorded a wrong measurement). **pass-4 resolutions: 9 of 9 reproduced by execution — the
phantom-edit class did NOT recur.**

## Strengths

- **Every premise figure re-measured true**, including the per-skill split of the 32 hardcoded
  sites (format 11, pdf 10, html 8, lint 3), 10 `SKILL.md` with `allowed-tools`, 5 formulas,
  crate `0.4.0`, no `v0.5.0` tag, the 41-line `Unreleased`, 21 legacy `find` sites, and every
  one of the eleven asserted strings measured false on today's tree.
- **N2's fix is executable, not prose.** The RED gate's `Test` is one physical line,
  `verify-red-all && verify-red-checks`, and `plan_manager.py` runs gate commands through
  `bash -c`, so the compound is honoured.
- **DAG mechanically clean, verified by script:** 58 issues, zero cycles, zero dangling
  `depends-on`, complete topological order, `anc(6.8) = 57/57`.
- **Instruments green:** `doc_lint` PASS, `gate_consistency` PASS (5 gates),
  `recheck-criteria` parses **41 of 41** with exactly one `holds` (SC16, correctly defended).
- **R2's `ctl-226` trap is already closed** — SC7 is true on the unfixed tree, so a bare-mode
  fixture asserting only the negative could never be recorded RED and would deadlock the gate.
  R2 requires the control to assert **both** halves, which makes it red pre-fix.
- N5 independently confirmed **complete**: exactly three READMEs have runnable use-without-assign
  (18 sites); the other use-only hits are prose mentions in directory listings, correctly
  out of scope.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| P1 | med | **The 28 `check-*.sh` red baseline has a verifier but no RECORDER.** Measured at source: `cmd_record_red` gates on `_in_manifest`, a `grep -qxF` against `controls.txt`, whose set is derived with the `ctl-` pattern — so `record-red` on a `check-*.sh` **hard-fails and writes nothing**. N2's class one level further down |
| P2 | med | **N4's recorded measurement is wrong — `grep -rl 'yf skills install' web/` returns SEVEN files, not six.** The missed one is **`web/plugins/skill_pages.py:242-243`**, a **generator**, so the deprecated spelling is emitted into every generated skill page — arguably the highest-leverage site. The plan again asserted DERIVED and then wrote a wrong enumeration |
| P3 | low | The RED gate's `Condition` and `Instructions` lag its `Test` — both still say "every **control**" while the Test also runs `verify-red-checks` over 28 instruments |
| P4 | low | SC27/SC28's `Discharged-by` disagrees with their own text — SC27 omits 4.3; SC28 lists 5.8, which names no asserted string |
| P5 | low | 0.1's allowlist mixes two vocabularies — SC16 is named as a member but invokes `change_validation.py` directly with no file under `assets/checks/`, so it is outside the verb's domain entirely |
| P6 | low | SC21 is exposed to the version-stamp staleness AGENTS.md documents — 6.5a's merge moves `HEAD` without touching a watched path, so 6.6a's rebuild can carry the pre-merge hash and fail for a non-defect |

## Missing

1. A write-side verb for the `check-*.sh` red records (P1).
2. `web/plugins/skill_pages.py` in 5.3's set (P2).

## Gate Assessment

**Sound, and the strongest layer of the plan.** Five gates consistent. The RED gate's `Blocks`
set is a clean 1:1 onto the 8 derived controls with its evidence producer (0.1 ← 0.7, 0.8)
entirely outside it. `check-harness-smoke.sh` correctly allowlisted with its reason. Both human
gates correctly placed as the last stops before an irreversible, auto-publishing tag. No
frontloading miss. The only residual is P1 — and it is **fail-closed, not silent**.

## Upstream Assessment

Unchanged and sound. 23 rows; `#154 → exclude` correctly carries no `Resolved By`; the numberless
coarse tracker correctly omitted. #127's rescope is grounded — the ten terms are enumerated with
measured frequencies in `findings/exp-005`, which travels in the bundle.

## Readiness call

**Ready.** A topological DAG walk found no issue whose predecessors fail to satisfy its
preconditions. The two real gaps are both **fail-closed and self-announcing**: P1 halts at the
RED gate inside the very issue (0.6) that owns `redcheck.sh`; P2 trips 5.3's own hard-grep
criterion inside the very issue that owns `web/`. Neither can ship silently; neither is
discovered late. Everything else is prose lag.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P1 | med | Confirmed at source (`_in_manifest` gates `cmd_record_red` at `redcheck.sh:169`). 0.6's scope now **also extends the WRITE side** — a sibling `record-red-check`, or relaxing the gate to directory membership for `assets/checks/` entries — with the reason recorded: *a verifier with no recorder reads an empty set*. | `main-session` | `resolved` |
| P2 | med | Confirmed independently: **seven** files. 5.3 corrected, and **`plugins/skill_pages.py` is named explicitly as a GENERATOR** — the highest-leverage of the seven, since it emits the deprecated spelling into every generated skill page. | `main-session` | `resolved` |
| P3 | low | The gate's `Condition` and `Instructions` now both name the `check-*.sh` instruments and the allowlist, matching the Test. | `main-session` | `resolved` |
| P4 | low | SC27 `Discharged-by` → `4.3, 4.4, 4.5, 4.6, 4.7, 4.8`; SC28 → `5.2, 5.3, 5.4, 5.5, 5.6`. Both now match their own text. | `main-session` | `resolved` |
| P5 | low | 0.1's allowlist restated to cover **check SCRIPTS, not criteria** — SC16 is a legitimately-holds criterion outside `verify-red-checks`' domain, not an allowlist member. One member remains: `check-harness-smoke.sh`. | `main-session` | `resolved` |
| P6 | low | 6.6a now requires a **forced re-stamp** before deploying, citing the documented staleness — so SC21 cannot fail for a non-defect. | `main-session` | `resolved` |

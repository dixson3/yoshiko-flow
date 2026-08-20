---
type: Review
okf_spec: OKF-PLAN
pass: 5
---
# Red-team pass 5 — plan-049-james-dixson-725bc0

## Verdict: APPROVE

## Part A — pass-4 resolutions, verified against the artifacts

All landed. **H2 independently measured:** the reviewer built SC13's corrected fixture
(`<dir>/plan.md`, `status: review`) and drove `--type plan-relations --path` — `severity: E`,
`declared_severity: W`, **exit 1**. SC13 can now fail. **M2 reproduced exactly:** 137 corpus gates,
49 Start Gates; the all-absent predicate fires on **exactly two** (plan-006 L194's "Not needed"
Reconcile Gate and plan-008's stub); the rejected one-of predicate fires on **80**. M1 verified with
all four sibling sites now agreeing.

## Part B — mechanical verification

7 epics, **43 issues**, **60 edges**, 6 gates, **42 criteria**, `unparsed: []`; zero cycles, zero
dangling, `0.1` the only unnamed issue. `doc_lint` PASS; corpus sweep `files_checked 753, errors 0`.
`audit` all-pass; `okf.py check` clean, no ghost; `markdown_lint` clean on all 19 files.

**Every premise re-measured and exact:** 81 unparsed across 24 of 49; plan-006/007 both `0 edges,
0 unparsed`; the 89 declarations across exactly 5 plans; 21 lettered (all plan-012);
`disposition-alphabet-offered` 30 of 31, the one non-firing file being **this plan's own triage**;
SC23's `81 − 7 + 2 − 3 = 73` consistent. **Every code anchor line-exact.** D-9 reproduced live:
stripping the marker yields **exactly one** R1b finding (`0.1`). The Reconcile Gate jq driven through
all three populations: open→1, closed→0, empty→1.

**Issue 4.1 feasibility confirmed:** `plan_template.py` is already whole-file-vendored and
byte-identical (no clobber hazard); `rust-embed` has no extension whitelist, so `document_types/*.toml`
will embed; `doc_lint.py:610` already exposes `--root`.

## Strengths

- **Every load-bearing premise reproduces to the entry. Not true of any earlier pass.**
- **The two pass-4 highs are genuinely dead** — SC13 fails pre-fix under its own named invocation
  (measured, not argued), and SC42 closes the silent-green hole SC15/SC17 both left open.
- **The controls have controls** — mutant D in Epic 1, 3.2b in Epic 3, SC42 in Epic 4. Every
  "green but broken" story has a named counter-assertion.
- The plan no longer trips its own intake **and asserts that it stays that way**, with the mechanism
  verified in code.

## Concerns (none blocking)

| # | Sev | Concern |
| :-- | :-- | :-- |
| P1 | med | **SC18's mutant is backwards.** Measured: deleting a §3 trigger row yields `{"commands":[],"status":"pass"}` — a **vacuous green, never red** — and `change_validation.py` has no verb flagging a §1 id referenced by no §3 glob. Unsatisfiable as worded |
| P2 | med | **Issue 4.4's rationale excludes its own destination one cycle later** — it rejects coupling into a completed bundle, then promotes this plan's scripts, which become exactly that at land-the-plane |
| P3 | low | `resolves-upstream` for #135 sits on 5.2 but the **close** happens at 6.5, whose text says only "POST the drafted comments" |
| P4 | low | **D-10 still carries the `skills/<name>/` placeholder** — pass-4's M4 landed in the issues but not in the Scope Decisions table of the same file |
| P5 | low | `index.md:17` still summarises EXP-002 as "the three-layer form" — only `plan.md:80` got the four-layer note |
| P6 | low | pass-4's Resolutions table says `index.md` gained `assets/` **and** `scripts/`; it gained only `assets/`. The omission is **correct** (an entry for an absent directory is an OKF ghost) but the record overstates |
| P7 | low | Issue 4.1 lists `renderable_fences.py` in the transitive set; `doc_lint.py` does not depend on it — dead weight, not a defect |
| P8 | low | `files_checked` drifted 752 → 753 — anticipated by SC23's delta framing; a live instance of the #135 pattern Epic 5 scopes |

## Missing

**Nothing.** Every recommendation in all six findings cross-checked against a scheduling issue, one
by one across EXP-001..006. Every `partial`/`deferred` upstream row has a recording issue. **No
silent deferrals.**

**Falsifiability sweep of all 42:** 41 can fail on evidence. **SC18 is the exception, and it fails
the other way** — unsatisfiable as worded rather than vacuous. SC14, SC37 and SC40 are the softest,
but each requires a *named* substitute and SC37 pins a strict-decrease baseline. None is a no-op.

## Gate Assessment

Clean. Both human gates correctly typed; the exit-0/1/2 wording matches INCONCLUSIVE semantics;
Issue 0.7's wrapper closes the 127 hole; the corpus-write gate's evidence is an ancestor outside its
own Blocks set; the Reconcile Gate's jq verified across all three populations. No cycles, no
frontloading misses.

## Upstream Assessment

Sound. Eight rows, full titles, three surfaces agreeing on every disposition. R2b measures **zero**
errors at `review`. Both `partial`s name the issue recording the OUT half.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P1 | med | SC18 reworded to the **two-sided** form: with the row present a DAG-breaking change selects and reddens the control; with it deleted the same change selects it **not at all** (`commands: []`) — naming the vacuous green as the measured outcome | `main-session` | resolved |
| P2 | med | Issue 4.4 now states the coupling is **accepted for this plan's own scripts**, with the reason the objection does not transfer, and names the non-bundle home as the follow-on if it recurs | `main-session` | resolved |
| P3 | low | Issue 6.5 now says "post the comments **and close #135**", matching `_verify_row`'s `include` contract | `main-session` | resolved |
| P4 | low | D-10 resolved to `skills/yf-plan/scripts/` | `main-session` | resolved |
| P5 | low | `index.md`'s EXP-002 summary carries the four-layer note | `main-session` | resolved |
| P6 | low | Recorded here — the pass-4 table overstated; the artifact is correct | `main-session` | resolved |
| P7 | low | `renderable_fences.py` dropped from Issue 4.1's set | `main-session` | resolved |
| P8 | low | No action — SC23 reports `files_checked` as a delta by design | `main-session` | resolved |

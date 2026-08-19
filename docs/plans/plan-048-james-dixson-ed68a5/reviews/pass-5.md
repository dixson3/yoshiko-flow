---
type: Review
okf_spec: OKF-PLAN
pass: 5
---
# Red-team pass 5 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

## Part A — audit of pass-4's resolutions

8 of 11 landed. **Three landed in `plan.md` only and did not reach `context.md`** (M1, M3, L5), and
one reported claim — "zero uncovered" — **is not true of the artifact**: 12 issues are named by no
criterion (9 after the Epic-0 carve-out). The main session measured *transitive* coverage and
reported it as direct. The partial-landing pattern from passes 1–4 held again.

## Part B — mechanical verification

5 epics, 37 issues, 5 gates, 24 criteria, `unparsed: []`, no cycles, single root `0.1`.
`doc_lint` PASS; `audit` pass; `okf.py check` OK; `markdown_lint` clean across all 30 bundle files.
**Gate ancestry clean for the second consecutive pass**, verified by transitive ancestor set — and
each gate sits at the *first* successor of its evidence, so there is no frontloading miss.

Independent re-measurement: 150 unparsed across **33 of 48** dirs (plan says 47); `doc_lint`
`files_checked` is **180 today, not 174**; 610 reproduces exactly; `parse_upstream_rows` confirmed to
build `disposition` without stripping bold while `plan_extract:368` does `.strip("*")` — **#173
defect 2 live, the two parsers genuinely disagree**.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H1 | **high, blocking** | **Issue 3.4 makes plan-048 fail its own reconcile.** `_verify_row` branches on `include`/`supersede`/`partial` then falls through; D-7 adds `deferred` as a literal but **no issue adds a `deferred` branch**. After 3.4's "unrecognised → `fail`", this plan's own five `deferred` rows (#140, #149, #165, #62, #135) each return `fail`, and `verify-reconcile` is a **halting** step. The change also destroys the deliberate `tracker` branch that D-2's coarse tracker relies on. Underneath: **REQ-PLAN-074 enumerates only three dispositions**, and Issue 0.2 does not reach it — a SPEC-first gap |
| H2 | **high, blocking** | **`context.md` describes and authorizes the deleted plan.** It cites "Epic 6", "Issue 4.7" (which is Deploy), "Issue 6.5", the deleted fingerprint postcondition, and grants authority for "**a corpus-wide rewrite**" that D-4 explicitly renounces. `audit` passed because it is a mechanical existence check — the silent-green class this plan exists to eliminate |
| M1 | med | **SC20's coverage half is already true** — `> 23.4% of 744` = >174.1, and `files_checked` is **180 today**. It is the only criterion grading Epic 2's aggregate, so 2 of 9 type instantiations would still read green. Also **744 was never measured** — it was back-derived from 174 ÷ 0.234 |
| M2 | med | `index.md`'s blurb still advertises "normalize the corpus hash-neutrally, bind the enforcement points" — both deferred |
| M3 | med | D-12's **rationale** still asserts "3.6 and its script exist" and "Epics 4 and 5 depend on 3.6" — both deleted |
| M4 | med | **D-8, D-9 and D-11 are unmarked orphan decisions** binding deferred work. D-11 reads as a live imperative to fix §3 vacuities that no issue schedules — the #149 class this plan defers |
| M5 | med | **SC10 is verified by an artifact that cannot grade it** — the relational gate blocks 3.4 and generates its *own* mutants, so it never executes 3.5's seven committed fixtures. SC10 cannot fail if 3.5 ships zero |
| M6 | med | The Motivation still argues for plan-049's work (bullets 3 and 4) |

## Missing

`references/handoff-049.md` is named by no issue (only by SC31's Verification); #113/#174 resolve at
4.4 (draft) not 4.5a (post); 2.1b is a graph leaf outside 4.2's merged tree; `log.md` has no D-13
entry and carries pre-split counts; the R1b residual regressed from an exact enumeration to "a
handful"; residual "~700" and "33 of 47".

## Gate Assessment

**All five gates structurally sound** — no cycles, no unreachable conditions, no frontloading miss.
The Reconcile Gate is **undermined by H1**: the step it gates will halt on the plan's own rows.
One residual: `gate-relations.sh` must distinguish "the R-rules do not exist yet" (exit 1) from "the
harness broke" (exit 2); the Instructions say so, Issue 0.6's text does not.

## Upstream Assessment

Still the strongest section; survived the restructure intact — `upstream-triage.md` and `plan.md`
agree on all 13 rows and dispositions, and the two D-13 deferrals are correctly re-dispositioned in
both files. **The four `deferred` rows are simultaneously the plan's best self-test (SC9) and the
trigger for H1 — the strength and the blocker share a root.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | Issue 0.2 extended to amend **REQ-PLAN-074** with `deferred` and `tracker` end-state contracts; new **Issue 3.4a** adds those branches to `_verify_row` and extends `test_verify_reconcile.py`, ordered BEFORE 3.4; new **SC33** drives it both ways | `main-session` | resolved |
| H2 | high | `context.md` rewritten against the post-split scope — no corpus writes, `gh` only for Epic 4, gates at 4.5/4.5a, deploy at 4.7 | `main-session` | resolved |
| M1 | med | SC20's coverage half replaced with an absolute bar (`files_checked >= 600`, derived from the EXP-002 census) **plus** a per-type assertion that every type instantiated in 2.2–2.8 selects > 0 files | `main-session` | resolved |
| M2 | med | `index.md` blurb restated from the Objective, naming plan-049 as successor | `main-session` | resolved |
| M3 | med | D-12's rationale rewritten in past tense with no present-tense claim | `main-session` | resolved |
| M4 | med | D-8, D-9 and D-11 marked "carried to plan-049", and named in SC31's required handoff content | `main-session` | resolved |
| M5 | med | SC10's Verification changed to run the seven committed fixtures and assert the count | `main-session` | resolved |
| M6 | med | Motivation bullets 3 and 4 annotated "(plan-049)" | `main-session` | resolved |
| Missing | low | 4.6 names `references/handoff-049.md` as its deliverable; #113/#174 → 4.5a; `2.1b` added to 4.2's deps; `log.md` D-13 entry; R1b residual re-enumerated; ~700 → 744 and 47 → 48 | `main-session` | resolved |

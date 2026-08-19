---
type: Review
okf_spec: OKF-PLAN
pass: 4
---
# Red-team pass 4 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

## Part A — audit of pass-3's resolutions

**12 of 14 landed fully; M6 half (idempotence graded, fingerprint-neutrality not); L3 half (0.4
renamed, four other sites still describe a corpus-wide normalizer).** H1, H2, H3, H4, M1, M2, M3, M4,
M5, L1, L2, L4 all verified in the artifact. M4's residual is **numerically exact** — the reviewer
independently computed the same 9 issues.

## Part B — mechanical verification

46 issues, 34 criteria, 7 gates, `unparsed: []`, **no cycles**, single root `0.1`, single sink `6.6`,
every issue reachable. `doc_lint` PASS; `audit` pass; `okf.py check` OK; `markdown_lint` clean across
plan/index/log/context/upstream-triage. **Every capability gate's evidence is in the ancestry of what
it blocks — first clean pass in four cycles.**

Independent premise re-measurement: 150 unparsed across 33 of 48 dirs (reproduces EXP-001 exactly);
`parse_upstream_rows` confirmed to return unnormalized bold (#173 defect 2 **live**); `ready-check`
exit 3 exists (SC18 dischargeable); `doc_lint --path <dir>` returns `PASS, files_checked: 0` (the D-11
silent green, reproduced firsthand); `okf.py` contains **no** eligibility predicate (feeds M2).

## Strengths

- **Gate ancestry is finally sound across the board** — four cycles of false ancestry claims are gone.
- **The 54 target is a real fix, not a form fix** — a literal in three places, traceable to a
  measurement, and SC1/SC20 can now genuinely fail.
- **`gate-run.sh` is the right shape** — resolves H1 without a resolver change, and its own bootstrap
  hazard is closed by ancestry rather than by hope.
- **D-5 is still paying** — every figure spot-checked reproduced. The corrections table is the most
  valuable artifact in the bundle.
- **The R1b residual is numerically exact and self-incriminating** — the plan names the 9 issues its
  own shipped rule would flag.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H1 | **high, blocking** | **The D-12 split gate trips on approval.** `reviews/` holds 3 files; this review makes **4**, and the threshold is `>= 4`. Pass-3's M3 fix (`4.1`/`5.1 depends-on 3.6`) turned a soft tripwire into a **hard block on 15 issues and 16 criteria** — the migration, the entire enforcement binding, FULL validation, the tracker and the deploy. The plan can prove *before execution* that two-thirds of its criteria will never run |
| M1 | med | **0.4 amends the SPEC for three postconditions; 4.1 implements two.** Fingerprint-neutrality is implemented by no issue and graded by no criterion — and `CHANGE-VALIDATION.md` has no SPEC-coverage row, so FULL would not catch it. A fresh instance of **#149**, the class this plan dispositions `partial` |
| M2 | med | **D-4a is vestigial** — it splits an eligibility conjunct that `okf.py` does not contain and no issue implements. A scope decision with no subject makes an executor guess |
| M3 | med | **The L3 rename landed at 0.4 only.** D-4, the Approach, R4 and the **human gate's Instructions** still say "corpus-wide" / "~92% of the corpus" against Issue 4.2's actual 31 directories. The gate exists so an operator can size a destructive write; that is the one place the overstatement costs something |
| L1 | low | R1's mitigation cites D-8, a postcondition on a write path the grammar widening never enters. It is genuinely mitigated by 1.4a/1.4b/SC1d instead |
| L2 | low | 1.4b's H2-repair sentence conflates edge adjudication with the 54 residue count |
| L3 | low | SC1b still has no adverse-finding bar — 20 of 20 adverse would discharge it |
| L4 | low | SC1's `git diff --stat docs/plans` empty will be dirtied by plan-048's own bookkeeping |
| L5 | low | "174 of ~700 (23.4%)" implies a denominator of 744, not ~700 |
| L6 | low | SC numbering has holes (no SC2/SC11/SC13; SC26 after SC30) |

## Gate Assessment

All five capability gates: **evidence in the ancestry of what they block, no cycles, none
unsatisfiable.** The `intake binding does not wedge` gate remains the best in the plan. The
`normalizer aggregate diff` gate is mechanically sound but its Instructions misstate the blast radius
(M3). **The blocking halt is not a gate — it is Issue 3.6**, which is why the gate table reads clean
while the plan still cannot complete.

## Upstream Assessment

Strongest section of the bundle. #173's `partial` boundary is stated twice and grounded in a live,
reproduced defect. `Resolved By = 3.4, 6.5a` correctly names both fix and post. The four `deferred`
rows make D-7 load-bearing and SC9 a genuine self-test. One tension: **#149 is `partial` on the
grounds that enforcement binding "closes more of the class", while M1 creates a new member of that
class inside this plan** — fix before drafting the 6.4 comment or it overstates. **Six of thirteen
upstream rows resolve in Epics 4–6**, all downstream of the H1 halt.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | **Operator decision — escalated.** The reviewer's option (a) is to split at approval rather than at 3.6: ship Epics 0–3 as plan-048, move Epics 4–6 to a successor. Option (b) re-bases the threshold to 5 so 3.6 tripwires a future cycle | `operator` | unresolved |
| M1 | med | — | `main-session` | unresolved |
| M2 | med | — | `main-session` | unresolved |
| M3 | med | — | `main-session` | unresolved |
| L1–L6 | low | — | `main-session` | unresolved |

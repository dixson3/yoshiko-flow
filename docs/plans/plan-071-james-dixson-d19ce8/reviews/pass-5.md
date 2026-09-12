---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 5, EXECUTION, post-approval re-scope] APPROVE — the plan-070 deferral delta is confined to its declared surface (35 lines, 11 hunks); every re-scope premise measured true; suite green; 3 low notes"
plan: plan-071-james-dixson-d19ce8
pass: 5
mode: execution
---
# Plan Red-Team: plan-071-james-dixson-d19ce8

## Verdict: APPROVE

**Mode:** execution

## Strengths

- The re-scope delta is confined to exactly the declared surface: `git diff HEAD -- plan.md` = 35 changed lines across 11 hunks — frontmatter/header `status: approved → review` (mechanical, from the re-review), #392 and #395 upstream cells, D-5, Issues 0.4/3.2/4.3, the removed "plan-070 has landed" gate, R1/R4/R5, SC19. No hunk outside that list. `context.md` (1 line) and `log.md` (2 lines) carry matching entries.
- Every re-scope premise is measured true in the tree (see Executed): the reader has exactly one non-definition call site, inside `audit-close` (L6967); the two forward-compat arms sit at the lines 4.3 cites; `REQ-LAND-039` is absent (0 hits); the landing spec carries 39 ids (001–038 + 017a) so the 22 arithmetic holds; the reader is 119 lines as 3.2 states.
- SC19 is RED today for the right reason: the `log.md` line is absent (0) and the reader still exists (2 hits) — both clauses would need Issue 3.2 to flip it.
- Baseline suite gate is green (71 + 18 + 7 passed), REQ-id gate exit 0 — all four allocated ids remain free.

## Executed

| Check | Command | Exit / output |
| :-- | :-- | :-- |
| Delta size | `git diff HEAD -- plan.md \| grep '^[-+]' \| grep -v '^[-+][-+]' \| wc -l` | 35 |
| Premise (a) | `grep -n '_land_route_record_findings' plan_manager.py` | L6796 def; L6967 sole call (inside `audit-close`) |
| Premise (b) | `grep -rn 'route_record' test_*.py` | only reader pin: `test_audit_close.py:152` `CLOSE_TIME_ONLY_SOURCES`; `test_land_apply.py` hits are the two emitters (keep) |
| Premise (c) | `sed -n '6280,6295p'` / `sed -n '175,190p' close_cascade.py` | both forward-compat arms present at the cited lines |
| Premise (d) | `grep -rn 'REQ-LAND-039' skills SPEC.md \| wc -l` | 0 |
| Premise (e) | `grep -c '^### Capability Gate'` / `grep -c 'plan-070 has landed'` | 2 / **1** (L180, D-5 prose naming the removed gate — not a gate) |
| REQ-LAND count | `grep -o 'REQ-LAND-[0-9]*a\?' spec/landing.md \| sort -u` | 39 ids (+1 bare prefix) |
| Reader length | awk def-to-def | 119 lines |
| doc_lint | `doc_lint.py --path plan.md --json` | PASS, 0/0/0, exit 0 |
| plan_extract | `plan_extract.py --strict` | 6 epics, 23 issues, 35 edges, 4 gates, 21 criteria, 0 unparsed, exit 0 |
| gate_consistency | `gate_consistency.py <dir>` | PASS 4 gates, exit 0 |
| check-req-coverage | `--min-issues 30` | exit 2 INCONCLUSIVE: 19 non-Epic-0 issues (< floor 30) |
| audit | `plan_manager.py audit --json-output` | status pass, 0 findings (`--json` is not an option — usage exit 2) |
| markdown_lint | plan.md, context.md, log.md | clean ×3, exit 0 |
| ready-check | `ready-check --json` | `ready: true, verdict: APPROVE, review_pass: 4, audit_status: pass`, exit 0 |
| resume-scan | `resume-scan --json` | `stale_approved: true`; stored `d623f106…` ≠ current `11310dcf…` |
| Gate: REQ ids free | loop grep | exit 0 |
| Gate: baseline suite | 3 test files | 71 / 18 / 7 passed |
| Consistency | `grep -n 'lands first\|folds into\|relocated\|070 has landed'` | 1 hit, L180 (D-5's "(a) the gate is removed") |
| plan-070 deferral | `grep -c DEFERRED plan-070/log.md` | 1 (L5) |

SC rows (`timeout 120 bash -c`, `\|` unescaped):

| SC | expected | actual | expectation |
| :-- | :-- | :-- | :-- |
| SC1 | 0 | 1 | RED — 41 `@cli.command` today; goes green at 4.1/4.3 |
| SC2 | 0 | 1 | RED — 39 ids / 760 lines; goes green at 0.4 |
| SC3 | 0 | 0 | MET — declared invariant (green today) |
| SC4 | 2 | 0 | RED — formulas still exist; 2.5 |
| SC5 | 0 | 1 | RED — `REQ-AGENT-066` absent from contract test (0 hits); 2.1/2.3 |
| SC6 | 0 | 2 | RED — `test_ready_check_smoke.py` missing; named in Issue 2.4 (L242) |
| SC7 | 0 | 1 | RED — `fidelity` absent from `test_retrospective.py` (0 hits); 1.1/1.2 |
| SC8 | 0 | 1 | RED — `findings/fidelity-baseline.md` absent; named in 1.3 |
| SC9 | 0 | 0 | MET — 2 reading, ≥1 execution pass on disk |
| SC10 | 1 | 0 | RED — `_land_l5_advisory_recheck` present (2); 4.3 |
| SC11 | 0 | 1 | RED — `gate-consistency` absent from `test_close_contract.py`; 4.4/4.7 |
| SC12 | 0 | 1 | RED — `UNWIRED check-cargo-test-ran.sh`; 4.5's sweep |
| SC13 | 0 | 2 | RED — `check-provably-necessary.py` missing; named in 4.6 (L266) |
| SC14 | manual | — | manual: by design |
| SC14b | 0 | 1 | RED — log line absent; 5.1 |
| SC15 | 1 | 0 | RED — 8 dead registrations present; 4.1/4.3 |
| SC16 | 0 | 1 | RED — `LAND_CLOSE_CHAIN` absent from contract test; 4.7 |
| SC17 | 0 | 2 | RED — INCONCLUSIVE: no plan-071 amendment entry; Epic 0 |
| SC18 | 0 | 1 | RED — `Mode:` 0 hits in SKILL.md; 2.2 |
| SC19 | 0 | 1 | RED — log line 0, reader hits 2; 3.2 (correct reason) |
| SC20 | 0 | 1 | RED — log line absent; 4.2 |

No 126/127, no timeout, no usage error, no `No such file` for an artifact not named in ## Epics. Every red row names its new artifact or case.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | low | measured: `grep -c 'plan-070 has landed' plan.md` → 1, not the brief's expected 0. The hit is D-5 L180 — prose naming the gate it removed — not a surviving `### Capability Gate` (count 2, extract 4 = start + 2 capability + reconcile). | No change needed; if the intake fingerprint check ever greps that string, reword L180 to "the plan-070 ordering gate". |
| C2 | low | measured: `ready-check --json` returns `ready: true / APPROVE / review_pass: 4` on a bundle `resume-scan` reports `stale_approved: true`. The staleness fact lives only in `resume-scan`; `ready-check` does not consult the fingerprint. This is a pre-existing instrument gap, not a plan defect — and it is one Issue 2.4 reworks. | Record in `log.md` that pass 5 re-certified against the current fingerprint (`11310dcf…`), and re-approve so the stored fingerprint is refreshed. Optionally note in Issue 2.4 that `ready-check` should surface `stale_approved`. |
| C3 | low | inferred: `check-req-coverage --min-issues 30` is INCONCLUSIVE (19 issues) — unchanged from prior passes; the floor is the plan-060 convention, not this plan's. | None; noted so the suite result is not misread as red. |

## Missing

- Nothing measured. Issue 3.2 says "delete its test" — the only test pinning the reader is `test_audit_close.py:152`, which 4.3 deletes wholesale with `audit-close`; the wording is accurate.

## Gate Assessment

Two capability gates remain, both decidable at execute start and frontloaded: REQ ids free (exit 0 today) and baseline suite green (96 tests pass today). The removed plan-070 gate leaves no dangling `Blocks` reference — `gate_consistency` PASS over 4 gates, `plan_extract --strict` 35 edges / 0 unparsed. No gate depends on evidence produced inside its own `Blocks` set.

## Upstream Assessment

#392 and #395 cells now match D-5: #393/#394 close here by subtraction/collapse (both measured present in the tree), #388/#389 explicitly stay open for plan-070's revisit, and plan-070's `log.md` carries the DEFERRED line. Tracker #397 already exists from intake; no new upstream write is needed for the re-scope beyond refreshing that issue's body at land.

## Resolutions

**Status: APPROVE. Three low notes actioned by the main session on 2026-09-12.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 D-5 prose still names the removed gate | low | Reworded to "the plan-070 ordering gate" | `main-session` | `resolved` |
| C2 ready-check does not consult the fingerprint; re-certification must be recorded | low | `log.md` records pass 5 re-certified against fingerprint `11310dcf…`; re-approval refreshes the stored fingerprint; Issue 2.4 now also surfaces `stale_approved` in `ready-check` | `main-session` | `resolved` |
| C3 check-req-coverage floor of 30 is INCONCLUSIVE at 19 issues | low | Noted; the floor is a plan-060 convention, the check passes without `--min-issues` | `main-session` | `resolved` |

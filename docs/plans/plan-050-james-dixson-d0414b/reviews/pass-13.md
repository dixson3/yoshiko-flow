---
type: Review
okf_spec: OKF-PLAN
id: pass-13
status: complete
---

# Red-team pass 13 — narrow verification

## Verdict: APPROVE

Eleventh independent pass, and a **narrow verification pass by operator decision** after the
cycle-12 bound was reached. Scope was the five pass-12 fixes, the citations those edits introduced,
the self-injection sweep, and the four mechanical checks — not a fresh full-breadth review. **All
five resolutions hold, every one verified by execution or exact-line check. No self-injected defect
this round — the first clean round in nine.**

## Strengths

- **C123's anchored derivation was EXECUTED against the current `plan.md` and returns exactly 6**,
  and the six are exactly the declared control ids. The adversarial checks all pass: the pattern
  does not match its own literal text (the anchor requires a digit immediately after `ctl-`, so
  `ctl-[` never matches); `neg-179-open-wrapper` contains no `ctl-` substring and is correctly
  absent; and **the plan's stated counterfactual is still true** — the loose form still returns 7,
  so the recorded failure-mode explanation is accurate rather than stale.
- **`ctl-` appears in no bundle file other than `plan.md` and the `reviews/` history**, and the
  derivation is scoped to `plan.md`, so the pattern text now sitting inside `reviews/pass-12.md`
  cannot perturb it. The pass-12 mechanism was tested directly and does not recur.
- **All three C124 line citations are exact** — `_shared/doc_lint.py:17`, the vendored copy at `:17`,
  and `_shared/document_types/README.md:52` — and a repo-wide grep found **no fourth live surface**.
  The only other hits are nine test fixtures, the spec itself, and a completed plan-047 record.
  `DRIFT-CHECK.md:184` confirmed to name the engine's module banner explicitly.
- **SC1 is falsifiable, which was C125's whole point**: landing the spec amendment while omitting
  the README restatement fails it — a concrete, reachable failure state, unlike this plan's
  recurring vacuous-criterion class. The enumerated NEW-id count is still six.
- **C126's corrected range brackets the sentence exactly** — `skills/yf-plan/spec/data.md:185-188`,
  with "binary at every binding point" at 187.
- **C127 swept wider than filed**: `discovered-from`, `M9`, `stamping` and `Epic 5` across the whole
  bundle. Every remaining mention is a decision record, an experiment result, or an `index.md` entry
  already labelled plan-051 evidence. No descoped figure is presented as a live expectation anywhere.
- **Mechanical checks green**: 28 issues / 6 epics / 41 edges / `unparsed: []`; `doc_lint` over all
  **75** bundle files with 0 non-zero exits and exactly two `files_checked: 0` (the reserved
  `index.md` / `log.md` pair); portability audit `pass` with zero findings; FAST tier green on all
  four rows.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| C128 — the derivation names `plan.md` as a **bare relative path**, but its caller `assets/redcheck.sh` lives one directory down; run from the repo root or from `assets/`, `grep` errors and `wc -l` yields 0, so `verify-all` compares 6 manifest lines against 0 | low | **Fixed** rather than accepted. 0.2 now resolves the path from the script's own location — `"$(dirname "$0")/../plan.md"`. The reviewer correctly judged this non-blocking because the failure is loud (0 vs 6 → exit 1) rather than silent, but a gate that fails depending on where it was invoked from is not a gate, and the fix is one clause |
| C129 — the anchored pattern is not future-proof for id shapes outside `ctl-<3 digits>-<lowercase+hyphen>`; executed, `ctl-1234-foo` and `ctl-99-bar` do not match, and `ctl-178-Grant` would truncate and collide | low | **Recorded in 0.2** rather than redesigned. No action is needed for this plan — all six ids are in shape — and every failure mode is undercount → mismatch → **exit 1**, the loud direction 0.2 was designed for. The note exists so a future scope change adding an out-of-shape id sees it |

Neither was execution-blocking; both are recorded for the next scope change.

## Missing

Nothing within scope. Every one of the five pass-12 resolutions is present, correctly cited, and —
where it prescribed a derivation — was **executed** against the current tree rather than read.

## Gate Assessment

**NOT REVIEWED THIS PASS — deliberately, and this is a statement of scope, not a green.** Gate
structure, the `Blocks: {1.4, 2.4, 3.4, 7.4}` set, producer-ancestry and reachability carry ten
independent full-breadth passes, most recently pass 12, which re-walked all 41 edges and found the
gate sound once C123 was repaired. The only gate-touching item in this pass's scope was C123's
`verify-all` count derivation, which was **executed** and returns 6. Nothing else about the gate was
re-examined; read pass 12's Gate Assessment for the standing verdict.

## Upstream Assessment

**NOT REVIEWED THIS PASS — same basis.** No cycle-12 edit touched the upstream table, the
disposition set, or the reconcile path, so there was nothing in scope to verify. Pass 12 re-walked
the table against the live `_verify_row` branches (6 `include` / 4 `partial` / 4 `deferred` /
2 `exclude` / 1 `tracker`) and found it sound; that verdict stands unmodified.

## Scope note

This pass deliberately did **not** re-review the approach, epic decomposition, success-criteria
design as a whole, gate structure or reachability, the `Blocks` set, the upstream disposition table,
the reconcile path, `references/*`, `upstream-triage.md`, `plan-retrospective.md`, or `findings/*`,
and did not re-verify the eight line citations pass 12 confirmed live. Those carry ten independent
full-breadth passes behind them. The narrowing was an operator decision taken on measured grounds:
across the preceding nine rounds every execution-blocking defect was **injected by the previous
round's fix** rather than found in original material, so a targeted verification addresses the
actual failure mode at a fraction of the cost of a eleventh full pass.

## The mechanism, round ten — and the first round it did not fire

Nine consecutive rounds injected a defect while resolving one. This round did not.

The difference is not diligence; it is that **the countermeasure was finally a command instead of a
habit**. Pass 12 named it — *a derivation whose input includes the document that specifies it must
be RUN against that document before it is trusted* — and this pass ran it. That single execution is
what distinguishes a verified fix from a plausible one, and it is the same distinction this plan
exists to install into the process it describes.

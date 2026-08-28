---
type: Review
okf_spec: OKF-PLAN
id: pass-6
description: Red-team pass 6 — verification pass; verdict REVISE, 3 concerns (1 high); behaviour set confirmed closed
---

# Red-team pass 6

## Verdict: REVISE

> **Pass 6 is a verification pass, and the verification found one thing.** Six of the seven claimed
> edits landed verbatim and are correct. The seventh — H1.3 — landed as *text* but the predicate it
> introduces is **false over the current DAG**: two issues (4.6, 4.7) have no `depends-on` path to
> any Epic-0 issue naming a `REQ-*`, so `check_amendment_log.py` as specified would exit non-zero
> and **SC1 cannot be discharged**. The fix is ~2 lines. **I recommend against a seventh cycle** —
> apply it and execute.

## Resolution verification — pass 5's seven claimed fixes

| # | Claim | Actual |
| :-- | :-- | :-- |
| H1.1 | skills-column env override added to 0.4 | **LANDED**, with D-9's second half quoted and 3.2/SC10 named. One prose defect (C3) |
| H1.2 | `0.9` moved from 3.2 to 3.3; 3.2 gains `0.4` | **LANDED.** The edge now sits on the node that ships the warning |
| H1.3 | 0.7's assertion restated over a computable predicate | **TEXT LANDED, PREDICATE FALSE** — see C1 |
| M1 | 5.1a acknowledges the mid-execution-deploy constraint | **LANDED.** Names the AGENTS.md rule, the reinvoked-per-call mechanism, why it is unavoidable, and the executor caveat |
| M2 | "Five issues in Epic 4 rewrite the smoke" deleted | **LANDED.** `grep` returns no match |
| L1 | 2.4's assertion restated as a regression guard | **LANDED** |
| L2 | #238's truncated `Notes` completed | **LANDED but with a new typo** (C2) |

Structural spot-check reproduced independently: **35 issues, 70 edges, 0 dangling, 22 criteria.**

**Review files.** All five now carry canonical `## Verdict:` at level 2; zero bold forms remain.
Frontmatter, titles, concern tables and resolution tables intact in all five. Nothing else disturbed.

## Strengths

- **Six of seven pass-5 edits landed verbatim**, including the two most consequential: 5.1a's
  acknowledgement of the AGENTS.md mid-execution-deploy constraint (with mechanism, reason and
  executor caveat), and the `0.9` edge moving from 3.2 to the node that actually ships the warning.
- **The behaviour set is genuinely closed** — a full walk of Epics 1-5 found no sixth uncovered
  behaviour, and every shipped behaviour maps to a named Epic-0 requirement.
- **All five prior review files were repaired to the canonical `## Verdict:` form** with nothing else
  disturbed — frontmatter, titles, concern tables and resolution tables all intact.
- **The gate layer needed no further work.** Reachability re-verified; no cycle, no gate naming a
  script no issue creates, and the migration gate's evidence producer (5.1) is correctly outside its
  own `Blocks` set.
- **`#243`'s re-characterization is the strongest row in the upstream table** — excluded on surface
  grounds, but cited as the precise hazard 5.2a's quarantine exists not to reproduce.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **0.7's new predicate is false over the current DAG, so SC1 is unsatisfiable as specified.** Epic-0 issues naming a `REQ-*` are `{0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 0.10}`; `0.6` and `0.8` name none. Transitive closure: `4.6 → {0.8}` and `4.7 → {4.6, 0.8}` — both **FAIL**. Every other Epic 1-5 issue passes. **The substance is fine** — 4.6 edits `CHANGE-VALIDATION.md` and authors a repo check script, 4.7 files an upstream defect, so neither needs a `REQ-*`. The defect is that H1.3 removed the "ships user-visible behaviour" qualifier to make the predicate computable and thereby made it **over-broad**, demanding REQ-coverage from two issues that correctly have none — failing "for the wrong reason", which 0.7's own text warns about one sentence earlier |
| C2 | low | L2's completion duplicated a phrase: *"landing separately landing separately edits `harness_desc.rs` twice"*. `plan.md`'s copy is clean, so the two rows differ cosmetically |
| C3 | low | 0.4's new sentence leaves a stranded fragment from the pre-edit text — the clause after the colon is the *old* surface-column description and no longer parses as a continuation |

## Missing

**Nothing. The behaviour set is closed.** Walked Epics 1-5 once more; there is no sixth uncovered behaviour.

| Epic | Behaviours shipped | Covering requirement |
| :-- | :-- | :-- |
| 1 | enumerator, four-outcome classifier, `prune-private` CLI + dry-run default + schema | `REQ-YF-MARK-006` (0.3), incl. reversibility |
| 2 | descriptor split, skills-root collapse, transform drop, sync dedupe | `REQ-YF-INSTALL-007` (0.1), `-002` (0.2), NameTransform clause (0.5) |
| 3 | precedence fields, `CLAUDE_CONFIG_DIR` for claude-code, mismatch warning | 0.4 (both columns), `REQ-YF-INSTALL-011` (0.9) |
| 4 | tier registration, doctor axis, project-scope warning | `REQ-YF-DOCTOR-007` (0.10), `-INSTALL-011` (0.9); 4.6/4.7 ship no yf behaviour — C1's root |
| 5 | quarantine + restore | `REQ-YF-MARK-006`'s reversibility clause (0.3) |

Pass 4's four and pass 5's fifth (3.2) are all now covered. **The only residue is that the *certifier* of that closure, not the closure itself, is wrong.**

## Gate Assessment

Unchanged and sound; reachability re-checked. Start (frontloaded drivability) · live-harness
(`Blocks: 5.2`, one falsifiable arm) · migration apply (evidence from 5.1, which is **not** in
`Blocks` — no cycle; exit 2 vs 1 and empty-`delete` failure intact) · Reconcile (auto). All reachable.

## Upstream Assessment

Dispositions unchanged and defensible. `#256`/`#239` honestly `partial` with explicit IN/OUT;
`#238`'s note now complete (modulo C2). **`#243`'s re-characterization is the strongest row in the
table** — excluded on surface grounds, but cited as the hazard 5.2a's quarantine exists not to
reproduce.

## Executability

**Yes, with one caveat.** Every `depends-on` resolves, the topological order is well-defined, both
gates name a runnable `Test`, and every criterion names the issue that creates its checker. The one
thing an executor would hit cold is C1 — they would write `check_amendment_log.py` to the letter of
0.7, watch it fail on 4.6/4.7, and then have to make a mid-execution judgement the plan was supposed
to pre-decide.

## Recommendations

1. Add a declared, bounded `no-req-required` exemption to 0.7 (C1).
2. Delete the duplicated phrase (C2) and reflow 0.4 (C3).
3. **Execute.** A seventh adversarial cycle would not earn its cost.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Concern verified independently by the main session and accepted — and it corrected a WRONG verification.** The main session had reported the predicate holding; its check tested "path to **any** Epic-0 issue" rather than "path to an Epic-0 issue **naming a `REQ-*`**", and so tested a weaker predicate than the one 0.7 specifies. Recomputed correctly: `4.6 → {0.8}`, `4.7 → {4.6, 0.8}`, both failing. **Fix:** 0.7 now carries a declared `no-req-required` set of exactly `{4.6, 4.7}`, exempt on the stated ground that neither changes `yf` behaviour, and **bounded** — the script exits 2 (INCONCLUSIVE) if the set grows beyond those two ids without a reason, so the exemption cannot become the escape hatch the check exists to close. Re-verified: the predicate now holds for all 23 non-exempt Epic 1-5 issues | `main-session` | `resolved` |
| C2 | low | Duplicated phrase deleted from `upstream-triage.md` | `main-session` | `resolved` |
| C3 | low | **[CORRECTED at pass 7 — this row was FALSE when written.]** The reflow did **not** land; 0.4 still carried the stranded fragment, and the row claimed two sentences where there were three. Pass 7 caught it by reading the file rather than the table. Genuinely fixed at pass 7, together with a **second fragment of the identical class in 0.8** that six passes had read past | `main-session` | `resolved-at-pass-7` |

**All 3 concerns resolved. This file is now FROZEN.**

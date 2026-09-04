---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 6 — scoped verification of the C47-C56 resolutions plus a mechanical regression sweep. Verdict REVISE with ONE concern (C57), medium-high, now resolved. Nine of ten resolutions verified real by measurement, and for the first time in six rounds NO new vacuity appeared in the clause surface. C57: the SC14/SC14b merge left three live references to the deleted SC14b, one of them the entire mitigation cell of a high-severity risk.'
---
# Red-Team Pass 6 — plan-062-james-dixson-c3e98f

## Verdict: REVISE

*(one-edit REVISE; C57 resolved in the same cycle)*

## Strengths

**Nine of ten pass-5 resolutions verified real, by measurement.**

- **C47 genuinely resolved** — `plan_extract` reports **23** criteria, `SC14b` absent, `SC14`'s
  verification begins `manual:`, and grepping every `| SC…` row for `bd list` returns **0**. The
  vacuous repo-wide count is gone from the clause surface entirely: not relocated, not weakened.
  The 24→23 delta is accounted for by exactly that merge.
- **C48/C49/C50 resolved**, with both of C50's asserted facts re-measured: `_land_upstream_rows`
  (`:7941-7947`) has exactly one `continue`, on `disp == "exclude"`; `UPSTREAM_REQUIREMENTS
  ["deferred"]` (`:2695-2703`) sets `requires_mention: False`. Rows requiring a mention = **3**.
- **C51 resolved, no cycle** — edges give exactly `0.0 → 0.7 → 0.1 → 0.4 → 0.5 → 0.6`; Kahn
  layering puts `0.7` alone at layer 1, genuinely reachable before any `SPEC.md` edit.
- **C52 resolved** — Gate 3 `Blocks: 4.2`, its floor. Evidence `4.1` is a direct predecessor and
  not in the `Blocks` set. No frontloading miss remains.
- **C53/C54 resolved**, precedents exact (`CHANGE-VALIDATION.md:253/:254`, `exp-003:93`).
- **C55 resolved BETTER than recommended.** All four citations are now exact: `:8298`,
  `:8306-8311`, `:8309-8310`, `:9561`. **Recorded:** the plan was edited mid-pass to revert two of
  pass-5's four "corrections" — C55 was itself wrong, and its `:8305-8310` would have instructed
  Issue 2.1 to **delete the tty gate's `sys.exit(3)`**. The revert is correct.

**The mechanical sweep is clean.** `plan_extract --strict`: 24 issues, 26 edges, 5 gates, 23
criteria, 10 risks, `unparsed: []`, exit 0. Zero dangling `depends-on`, zero cycles, zero
`Discharged-by` naming a non-existent issue, all 24 issues named by a criterion. `gate_consistency`
PASS · `audit` `pass` / `okf_native: true` · `reindex --check` clean · `check_frontmatter` 43 files
clean · `doc_lint` PASS on **all 17** bundle files.

**Every Verification clause ran**: 15 correctly FALSE pre-work, 4 legitimately already-TRUE
(SC10/SC10b/SC11 regression guards, SC17b re-evaluated after 5.1b). No exit 126/127, no timeouts.
**The fifth-round vacuity did not appear in the clause surface** — the one place it has appeared
every prior round.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C57 | medium-high | **The SC14/SC14b merge deleted SC14b but left THREE live references**, at `:105-106` (Approach), `:224` (**R9's entire Mitigation cell**) and `:227` (R12). All three still assert SC14 uses `bd list --all` — now false. R9 is the sharp end: its written answer to a `high` risk cites the exact mechanism C47 measured as permanently-true and removed. **The pass-5 fix moved the unsoundness from the criteria table into the risk table rather than eliminating it** — the same fix-introduces-a-defect shape as C6/C24/C33/C38, one surface over. The underlying work is unaffected: Issue 0.0's SET-then-ASSERT is intact and is the real mitigation. A record defect, not a mechanism defect. | Rewrite all three to say SC14 and SC15 are both `manual:`, with Issue 0.0 as R9's mitigation. Re-run `grep -c SC14b` → expect 0. |

## Missing

Nothing else dangles. The cut-id sweep is clean across all five bundle documents. The two surviving
`Epic 3` hits refer correctly to plan-060's Epic 3 and to the cut itself. `index.md`'s SC14/SC14b
mentions are accurate *history* of what passes 4 and 5 found, not live references.

*Informational:* `SC13c` exits **2** (`INCONCLUSIVE — SPEC.md has no amendment-log entry`), not 1.
Correct pre-work state; Issue 0.6 makes it 0. Recorded so a binding that distinguishes 1 from 2 is
not surprised.

## Gate Assessment

| Gate | Blocks | Reachable? | Notes |
| :-- | :-- | :-- | :-- |
| Start Gate | — | n/a | mandatory human |
| in-place | 1.1 | yes | independent config read; correctly cross-links 0.7 |
| seam DISCRIMINATING | 2.1 | yes | evidence 2.0 is a direct predecessor, not in `Blocks`; once-only and benign-red both stated |
| resume | 4.2 | yes | **C52 resolved** — now at its floor, as early as reachability permits |
| Reconcile | reconcile step | n/a | standard |

`gate_consistency.py` PASS on both arms. The #266 workaround is sound **and its verification is now
sound too** — SC14 is `manual:` and records the read-back.

## Upstream Assessment

Four rows, all parsing, `doc_lint` R3 clean, and `plan.md` and `upstream-triage.md` now agree on
every row. #327 `include` → 1.1/2.1/4.1, covered by SC1/SC2/SC3/SC4/SC4b. #326 `deferred` — triage
matches the table, both cite the pass-4 cut and point at `findings/exp-003`. #266 and #304
`partial` — both `requires_mention: True`, both covered by 5.1c's three drafts.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C57 | medium-high | All three references rewritten. Approach now states SC14 and SC15 are both `manual:` and explains WHY neither failure is expressible as a repo-wide clause. R9's mitigation is now Issue 0.0's SET-then-ASSERT — the real mechanism — with SC14 recording the read-back. R12 drops the `bd list --all` claim. Re-measured: `grep -c 'SC14b'` → **0**, and `bd list` in any `\| SC` row → **0**. | `main-session` | `resolved` |

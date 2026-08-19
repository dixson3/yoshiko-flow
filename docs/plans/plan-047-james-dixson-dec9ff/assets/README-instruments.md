---
type: Note
okf_spec: OKF-PLAN
---

# EXP-003 instruments — rescued (Issue 0.0)

`extract_plan.py` (362 lines) and `pour_fidelity.py` (184 lines) are the prototypes EXP-003
used to measure this plan's headline number (17 of 43 plans carrying a pour divergence). They
were written in an agent worktree (`.claude/worktrees/agent-ad38d2df493e50e93/exp003/`) that
`yf-plan` tears down with `worktree remove --force`, so they were one teardown away from being
unrecoverable — and SC37 requires comparing the post-work number against the baseline they
produced.

Rescued verbatim (byte-identical to the originals) on 2026-08-19.

## Reproduction invocation

From the repository root:

```bash
bd list --all --include-gates --limit 5000 --json > /tmp/all-beads.json
python3 docs/plans/plan-047-james-dixson-dec9ff/assets/pour_fidelity.py \
    /tmp/all-beads.json docs/plans/plan-0*
```

`--include-gates` is **mandatory** (Issue 5.3): without it 121 gate beads and every gate edge
are invisible **with no error** (#166). `--limit 5000` is likewise load-bearing — the default
page truncates at 50 with exit 0.

`pour_fidelity.py` imports `extract_plan.py` from its own directory, so the two must stay
co-resident.

## Baseline as re-measured at execution (2026-08-19)

| Population | EXP-003 baseline | Re-measured at execution |
| :-- | --: | --: |
| plan dirs scanned | 46 | 47 (plan-047 now has an `**Epic:**` field) |
| comparable (joinable + has `**Epic:**`) | 43 | 44 |
| skipped — no `**Epic:**` field | 3 | 3 |
| no recoverable mapping (006 / 007 / 036) | 3 | 3 (same three plans) |
| plans with a divergence | 17 | 18 (= 17 + plan-047 itself) |
| declared dependency edges | 885 | 962 (+77, plan-047's own) |
| edges present in `bd` | 860 | 935 |
| dropped edges | 45 | 47 (= 45 + 2, both from plan-047) |
| invented edges | 20 | 20 (unchanged) |

The baseline reproduces exactly on the historical corpus. Every delta is attributable to
plan-047 itself now being comparable.

## The two "dropped" edges on plan-047 are an EXTRACTOR false positive, not a pour defect

`pour_fidelity.py` reports plan-047 as dirty with `edge_set_match: false` and two dropped
edges, `5.2 -> 2.6` and `5.2 -> 2.7`. The pour is correct; the extractor is wrong.

`extract_plan.py:35` matches dependencies with an **unanchored** pattern:

```python
DEPENDS = re.compile(r'depends[- ]on:\s*(?P<val>.+?)\s*$', re.I)
```

Issue 5.2's own body contains the literal string ``(`2.5 depends-on: 2.6, 2.7` — correct
execution order, inverted numbering)`` — inside an inline code span, quoting *another issue's*
edge as a parser hazard to test for. The unanchored search fires on it and attributes 2.6 and
2.7 to Issue **5.2**.

This is a **live specimen of exactly the defect Issue 5.1 forbids** ("must fail loudly
(`unparsed`) rather than degrade" — the prototype silently corrupted its own fidelity number
four times before each widening was found) and of the hazard Issue 5.2 was written to cover.
The production extractor must anchor the key to the canonical bullet form
(`^\s{2}- depends-on:`) and must not read inside inline code spans. Both belong in Issue 5.2's
test set alongside the two hazards already named there.

Everything else on plan-047 is clean: 77/77 issues joined by title, 0 unnumbered, 0 misfiled,
0 duplicate ids, 6/6 gates, 11/11 epics, 0 invented edges, 0 `unparsed`.

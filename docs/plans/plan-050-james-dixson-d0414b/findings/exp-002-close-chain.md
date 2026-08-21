---
type: Finding
okf_spec: OKF-PLAN
id: exp-002
status: complete
---

# Finding: Root cause of the two close-chain defects (#179, #180)

## Approach Tested

Read the pour formula and the cascade helper, then queried the live bead DB for every
start-gate wrapper bead the formula has ever produced.

```bash
bd list --all --limit 5000 --json    # 1481 beads
# select title ^'Begin:'  -> the formula's gate-step wrapper task
```

## Result

**measured: 49 wrapper beads, 49 closed, 0 open — and every one closed BY HAND**, with **29
distinct** improvised `close_reason` values across the 49 (the modal reason, "Start gate resolved;
execution begun", accounts for 10). An earlier draft of this finding said "a different bespoke
sentence each time"; pass-3 C20 measured that as an overstatement. The 49/49 is exact:

| Bead | `close_reason` (verbatim, truncated) |
| :-- | :-- |
| `yf-mol-cir` | `start gate resolved (bd gate resolve yf-mol-9q9); wrapper task closed to unblock entry issues` |
| `yf-mol-d92` | `Start gate resolved at execute start (yf-mol-6rq); wrapper task closed at land-the-plane` |
| `yf-mol-8vv` | `start gate resolved; execution begins` |
| `yf-mol-z9q` | `Start gate yf-mol-1w1 resolved (human start gate, new session per REQ-SESSION-001); wrapper task released` |

**inferred:** this is not an intermittent defect. It is a **manual step performed 49 out of 49
times**, each time re-improvised, with no mechanism and no exit code. It is the corpus's own
headline in miniature — a rule that nothing executes.

**The mechanism.** `plan-execute.formula.toml` declares one `type = "gate"` step, which the
pour expands into **two** beads: the gate (`plan-execute.gate-start-gate`) and a wrapper task
(`plan-execute.start-gate`) that entry issues take as a `--deps` predecessor, because bd rejects
a task blocking an epic. `bd gate resolve` closes **the gate**. Nothing closes **the wrapper**.
`close_cascade.py`'s `_bead_is_terminal` then sees a non-terminal child under the molecule and
fail-louds — correctly. The cascade is not the defect; the un-closed wrapper is.

## Implications for Plan

- **#179 is a one-line fix at the right seam:** close the wrapper in the same step that resolves
  the gate (SKILL.md §5.2a already pairs them), with a uniform `close_reason`. The 49 hand-written
  reasons become one generated one.
- **#180 is the same shape one layer up** — `close-reconcile-step` requires the reconcile gate
  resolved first, and that ordering is undocumented in the §6.4 chain. Both are ordering
  constraints that exist in someone's head and in no exit code.

## Recommendations

- Fix at the pour/resolve seam, not in the cascade. Weakening `_bead_is_terminal` would silence a
  correct fail-loud — the M1 "succeeds visibly while doing nothing" class.
- Ship a regression fixture: a poured molecule whose wrapper is left open must drive the cascade
  RED, and the fixed path must drive it GREEN. Shown-red-before-trusted-green (D-4).
- Carry the figure into the #179 comment as **"49 of 49 closed by hand, with 29 distinct
  improvised reasons"** — precise, and still decisive.

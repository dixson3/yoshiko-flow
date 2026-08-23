---
type: Reference
okf_spec: OKF-PLAN
id: edit-set-182
description: The ordered, hand-enumerated #182 edit set with per-row dispositions and what catches a miss
---

# #182 edit set — enumerated, with what catches a miss

EXP-002 measured exp-006's *"one line in one file"* as **wrong by ~7x**. This file is the
enumeration itself, rather than an index into EXP-002 — EXP-002 *recommended* such a list but
does not contain one, so an index into it would resolve to nothing (pass-1 C3).

**R1 is the risk this file exists to bound:** the set is enumerated **by hand**, and three of
its rows have **nothing mechanical** behind them. Those three are named inline below rather
than left to a glob.

## Ordered rows

| # | Site | Disposition | What catches a miss |
| --: | :-- | :-- | :-- |
| 1 | `skills/yf-plan/spec/agents.md` — REQ-AGENT-043 text + `Rationale:` | **landed at Issue 0.1** | SPEC-first: 0.1 owns the requirement itself. Recorded here so the enumeration is complete rather than silently narrowed |
| 2 | `skills/yf-plan/spec/agents.md` — REQ-AGENT-043 `Verification:` | **0.1 OWNS IT — do not edit here** | Nothing else rewrites this line (pass-3 C30). Double-ownership is the defect class C30/C37 exist to prevent |
| 3 | `skills/yf-plan/agents/red-team.md` — the read-only bullet, plus a new **spike-authorization** bullet | **EDIT** | `ctl-182-spike` conjunct (a) **and** conjunct (b); `CHANGE-VALIDATION.md` `uv-yf-review-agent` (Issue 3.3) |
| 4 | `skills/yf-plan/SKILL.md` — §3 *"Both agents are read-only"* | **EDIT** | `uv-yf-review-agent` §3 glob on `SKILL.md` |
| 5 | `skills/yf-plan/SKILL.md` — *"The agent never writes files"* (over-broad against the amended REQ) | **EDIT** | SC4b's hit-set subset assertion |
| 6 | `skills/yf-plan/SPEC.md` — the *"Both agents are read-only"* restatement | **EDIT** | **NOTHING MECHANICAL** — hand-enumerated, R1 |
| 7 | `skills/yf-plan/SPEC.md` — **GR-PLAN-002** | **EDIT** | **NOTHING MECHANICAL** — hand-enumerated, R1 |
| 8 | `web/content/skills/yf-plan.md` — the PLAN-phase row | **EDIT** | **NOTHING MECHANICAL** — not a `DRIFT-CHECK.md` node, carries no CV row |
| 9 | `web/content/pages/workflows.md` — *"The review agents are read-only"* | **EDIT** | **NOTHING MECHANICAL** — same class as row 8; partially reachable by SC4b |
| 10 | `web/content/pages/glossary.md` — the **red-team** entry | **EDIT** | **NOTHING MECHANICAL** — same class as row 8 |
| 11 | `skills/yf-plan/agents/reviewer.md` — the read-only bullet | **EDIT at Issue 1.2a** | `ctl-182-spike`'s conjunct (b) generalizes for free via REQ-AGENT-045 |
| 12 | `skills/yf-plan/spec/agents.md` — REQ-AGENT-045 text + `Rationale:` | **landed at Issue 0.1** (1.2a's spec half) | As row 1. **Not `:97`** — 0.1 owns that `Verification:` line |
| 13 | `web/content/pages/workflows.md` — the **reviewer** row's `Read-only? Yes` column | **NO EDIT** | Still true under the amended REQ: read-only **with respect to the repository** holds |
| 14 | `web/content/pages/workflows.md` — the **red-team** row's `Read-only? Yes` column | **NO EDIT** | As row 13 |
| 15 | `web/content/pages/workflows.md` — *"Review is two ordered read-only passes"* | **NO EDIT** | As row 13 |
| 16 | `skills/yf-plan/agents/captor.md` — the captor's read-only rule | **NO EDIT** | A **different agent** (REQ-AGENT-061), out of scope for #182. Required as an explicit row by **SC4b**: without it the post-fix hit set is not a subset of this file's paths and SC4b fails (pass-5 C42) |
| 17 | `skills/yf-plan/spec/portability.md` — the captor's read-only rule | **NO EDIT** | As row 16 |
| 18 | `skills/yf-plan/scripts/test_review_agent_contract.py` — an **assertion message** quoting the retired wording | **NO EDIT** | The occurrence is a **quote-to-forbid**: the failure message quotes *"never writes files"* in order to explain that the **unscoped** form is the over-broad reading #182 corrects. Rewording it to dodge a grep would make the error message worse to satisfy the instrument. This repo has already ratified that distinction — `REQ-BUP-053` / `GR-BUP-005` hold that statements quoting a forbidden construct *in order to forbid it* are **explanation**, not the construct. Added at Issue 4.1 after the criterion regressed; see below |

## The three rows with nothing mechanical behind them

Named here rather than by index, because an index is what pass-1 C3 rejected:

1. **`skills/yf-plan/SPEC.md`** (rows 6 and 7) — the skill's own SPEC restatement and
   GR-PLAN-002. EXP-002 measured the FAST tier returning `pass` on the dangling state.
2. **`web/content/skills/yf-plan.md`** (row 8).
3. **`web/content/pages/*`** (rows 9 and 10) — `workflows.md` and `glossary.md`.

Rows 8–10 are **not `DRIFT-CHECK.md` nodes and carry no `CHANGE-VALIDATION.md` recipe row**, so
no engine in the repo reaches them. SC4b extends coverage to the two paths its pattern actually
reaches (`skills/yf-plan/SKILL.md` and `web/content/pages/workflows.md`) and no further; the
rest stay hand-enumerated under R1, stated rather than presented as closed.

## Wording source

The portable core of this repo's `AGENTS.md` rule is used, **not** its verbatim text:

- the plan-049 anecdote does not travel to a foreign vault and belongs in `Rationale:`, not in
  the agent prompt;
- *"reviewers **and investigators**"* is wrong here — the investigator already gets a
  disposable worktree, so the carve-out it needs is already granted by a different mechanism.

## SC4 / SC4b, measured after rows 3–11 landed

**SC4 — the retired literal survives at zero tracked sites.** Run from the **repo root** (the
cwd is normative: `:!docs/plans` is repo-root-relative, so running it inside the bundle would
silently fail to exclude the bundle and report this plan's own prose as a surviving site). The
instrument is **`git grep`, not `grep`** — an untracked `.agent-shell/transcripts/*.md` carries
the literal, which would make the criterion unpassable for a reason unrelated to the work.

```bash
git grep -c 'Read-only — never writes files' -- ':!docs/plans' ':!docs/research'   # exit 1, no matches
```

**SC4b — the hand-enumerated set is CLOSED.** This criterion **regressed after it was first
discharged**, and the regression and its resolution are recorded here rather than the original
green being left standing. See *The SC4b regression* below.

Hit set **re-measured after Epic 3**: **8 paths**, and a **strict subset** of the paths this
file's rows name.

| Hit | Named by a row? |
| :-- | :-- |
| `skills/yf-plan/SKILL.md` | yes (rows 4, 5) |
| `skills/yf-plan/agents/captor.md` | yes (row 16, **NO EDIT**) |
| `skills/yf-plan/agents/red-team.md` | yes (row 3) |
| `skills/yf-plan/agents/reviewer.md` | yes (row 11) |
| `skills/yf-plan/scripts/test_review_agent_contract.py` | yes (row 18, **NO EDIT**) — **the new one** |
| `skills/yf-plan/spec/agents.md` | yes (rows 1, 2, 12) |
| `skills/yf-plan/spec/portability.md` | yes (row 17, **NO EDIT**) |
| `web/content/pages/workflows.md` | yes (rows 9, 13–15) |

Rows not in the hit set — `skills/yf-plan/SPEC.md`, `web/content/pages/glossary.md`,
`web/content/skills/yf-plan.md` — carry *"Both agents are read-only"* and no form of
*"never writes files"*, so the pattern does not reach them. **They stay hand-enumerated under
R1** and are stated here rather than presented as closed.

### The SC4b regression — a criterion discharged at 1.2a, invalidated by a later epic

**Measured at 1.2a: 7 paths, a strict subset. Measured after Epic 3: 8 paths, NOT a subset.**
Issue 3.2's new test file, `scripts/test_review_agent_contract.py`, matched the pattern at
**line 145** — inside an assertion message — and 3.2 sits **after** SC4b's declared
discharge points (1.2, 1.2a). The green was true when taken and false by completion.

Two things this is an instance of, both already named in this plan:

- **SC4b's own stated blind-spot boundary, working as designed.** It catches a new
  unenumerated **FILE**, and that is exactly what it caught. The blind spot is the
  *unenumerated LINE in an already-enumerated file*; this was the other case.
- **The self-reference class** — the **checker became a member of the set it measures**. The
  same shape as plan-050's C119, where a derivation's own `grep` pattern matched the sentence
  specifying it and returned 7 instead of 6. No blocklist closes this class; enumeration does.

**Resolution: option (a) — an enumerated NO-EDIT row (18), stating why the checker legitimately
carries the phrase.** The two rejected alternatives are recorded so the choice is legible:

| Option | Verdict |
| :-- | :-- |
| (a) enumerate it as a NO-EDIT row with a stated disposition | **TAKEN** — same treatment rows 16/17 already give `captor.md` and `spec/portability.md`, and it keeps the assertion's strength intact |
| (b) reword line 145 so it stops matching | rejected — the phrase is a **quote-to-forbid**; removing it degrades a failure message to satisfy an instrument |
| (c) exclude `scripts/` from SC4b's pathspec | **rejected as the weakest** — it narrows the criterion to make it pass, which is the M5 class this plan exists to close |

**The process finding is larger than the fix.** Nothing re-checked SC4b at completion. Issue
4.1 already mandates re-running the three **fixtures** against the merged tree, for exactly
this reason — *"a later epic can silently undo an earlier one's green with nothing detecting
it"* — but that mandate covers the fixtures only, and SC4b is a `plan.md` criterion with no
fixture. It was caught by an operator re-measurement, not by any mechanism this plan ships.
Recorded as **RE-003** in `plan-retrospective.md`.

**Stated blind spot:** SC4b catches a new unenumerated **FILE**, never a new unenumerated
**LINE** in an already-enumerated file.

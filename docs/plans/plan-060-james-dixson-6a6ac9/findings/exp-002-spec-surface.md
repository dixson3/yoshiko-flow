---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-002 — the SPEC-first surface for plan-060: REQ-prefix ownership, next-free ids, the living amendment log, requirement anatomy, the coverage gate, and the read-only agent template a `lander.md` must match.'
---
# EXP-002: The SPEC-first surface — where a landing requirement lands

## Approach Tested

**Question.** This repo is SPEC-first. Where exactly does a new landing requirement go, what id may
it take, what shape must it have, and what enforces that a test covers it?

**Method.** Read-only survey of `SPEC.md`, `skills/yf-plan/SPEC.md`, `skills/yf-plan/spec/*.md`,
`yf/src/coverage.rs`, `scripts/check_amendment_log.py`, `scripts/checks/check-req-coverage.py`,
`CHANGE-VALIDATION.md`, and the `agents/*.md` corpus.


## Result

## F1 — REQ-prefix to authoritative file

| Prefix | Owner |
| :-- | :-- |
| `REQ-PLAN-*` | `skills/yf-plan/SPEC.md` §2 |
| `REQ-AGENT-*` | `skills/yf-plan/spec/agents.md` |
| `REQ-CLI-*` | `skills/yf-plan/spec/cli.md` |
| `REQ-DATA-*` | `skills/yf-plan/spec/data.md` |
| `REQ-PORT-*` | `skills/yf-plan/spec/portability.md` |
| `REQ-PREREQ-*` | `skills/yf-plan/spec/prerequisites.md` |
| `REQ-PHASE-*`, `REQ-STATUS-*`, `REQ-SESSION-*`, `REQ-BRANCH-*`, `REQ-RESUME-*`, `REQ-COMPLETE-*` | `skills/yf-plan/spec/phases.md` (six families, one file) |
| `REQ-YF-*` | `SPEC.md` (macro only) |
| `REQ-ORCH-*` | `skills/yf-beads-authoring/spec/orchestration.md` — **not** a yf-plan family |

`SPEC.md:800`: *"**Authority:** a per-skill SPEC is authoritative for that skill's behavior."*

**The trap:** the `REQ-<PREFIX>-NNN` namespace is **shared across skills**, not per-skill.
`REQ-CLI-*` is defined by `yf-plan`, `yf-research` **and** `yf-beads-extra`; `REQ-AGENT`/`DATA`/
`PORT`/`PHASE`/`PREREQ` are shared with `yf-research`. **Next-free must be computed repo-wide**, or
a plan silently rebinds another skill's id.

## F2 — Next-free ids (measured repo-wide, excluding frozen `docs/plans/**` bundles)

| Prefix | Highest | Next free | Note |
| :-- | --: | --: | :-- |
| `REQ-CLI` | 029 | **030** | dense, no gaps |
| `REQ-AGENT` | 064 | **065** | decade-block layout; the gaps are block boundaries, **not free ids** |
| `REQ-PLAN` | 082 (code) / 081 (spec) | **083** | see F3 |
| `REQ-COMPLETE` | 004 | **005** | dense |
| `REQ-DATA` | 076 | **077** | |
| `REQ-PORT` | 054 | **055** | `009` is owned by **yf-research** — do not reuse |
| `REQ-PHASE` | 007 | **008** | 006/007 belong to **yf-research**; next free is 008, not 006 |
| `REQ-BRANCH` | 004 | **005** | yf-plan-exclusive |
| `REQ-RESUME` | 004 | **005** | |
| `REQ-SESSION` | 002 | **003** | |
| `REQ-STATUS` | 003 | **004** | |

The allocation rule, quoted from a prior plan's id-allocation asset
(`docs/plans/plan-049-james-dixson-725bc0/assets/free-req-ids.md:14`):

> *"**Do not back-fill a gap.** The families are laid out in **decade blocks** (`0x0` opens a
> sub-topic)… Even those are not reusable: a retired id reused silently rebinds every historical
> reference to it."*

and *"No issue in plan-049 may allocate a `REQ-*` id before this file lands"* — the precedent for an
Epic-0 id-allocation issue, which plan-060 should copy.

## F3 — Two pre-existing id defects a landing plan must not trip over

- **`REQ-PLAN-082` is consumed but never defined.** `skills/yf-plan/scripts/plan_manager.py:7330`
  cites it ("plan-059 Issue 3.1 (REQ-PLAN-082)"); no SPEC defines it.
- **`REQ-PLAN-078` exists nowhere in the live tree** — a retired/skipped number.
- `REQ-PLAN-069` has lettered sub-requirements `069a`/`069b`, which grep reads as duplicates.
- `REQ-PLAN-079` was renumbered from `073` after a collision with `stamp-tracker`
  (`skills/yf-plan/SPEC.md:363-367`) — precedent that renumbering is documented and survivable.

**Not plan-060's to fix**, but recorded: allocating `REQ-PLAN-083` is safe; allocating `082` is not.

## F4 — The living amendment log, and its five fragments

**Location:** `SPEC.md`, in the blockquote preamble under the H1 — lines 3–777, *not* an ATX
heading. The label is `> **Amendment log:**` at `SPEC.md:8`.

**Bullet format:**

```
> - **plan-NNN (YYYY-MM-DD, #ISSUE[/#ISSUE...][-partial]):** <theme in bold, then prose>
>   - **`REQ-XXX-NNN`** (added|amended|extended) — <what and why>
>   Implementation lands in Epics N-M; this entry records the SPEC-first Epic 0 amendment.
```

The trailing *"Implementation lands in Epics …; this entry records the SPEC-first Epic N
amendment."* sentence is the convention on every recent entry.

**#241's five regions, located:** (1) lines 3–439; (2) lines 441–777 — **split from region 1 by a
blank non-`>` line at line 440**, which markdown renders as a separate blockquote and which is the
invisible break; (3) lines 865–920, inside `### 3.2 Embedding`, carrying real `plan-047` and
`plan-050` amendment bullets filed under a section rather than in the log; (4) lines 2047–2049 in
`## 4. Skill catalog`. Ordering within region 2 is non-chronological.

**A mechanical check already exists** for the coverage half:
`scripts/check_amendment_log.py` assertion **A1** — *"Every `REQ-*` id named in the body of an
Epic-0 issue carries a bullet in `SPEC.md`'s living amendment log under this plan's entry"* — with a
hand-authored `CITED_NOT_TOUCHED` exclusion set and a three-valued `0/1/2` exit.

## F5 — Requirement anatomy: TWO shapes, keyed by file

**Shape A — `skills/yf-plan/SPEC.md` (`REQ-PLAN-*` only).** Bullet, bold id, optional `*(testable)*`
tag, **no `Verification:` line** (`skills/yf-plan/SPEC.md:39`):

```markdown
- **REQ-PLAN-003** *(testable)* every invocation except `init` shall run the preflight
  (`yf preflight yf-plan`) and branch on `ok | ignored | system_deps_missing | ...`.
```

**Shape B — `spec/*.md`.** Three lines, no bullet, no bold: bare `REQ-ID:` at line start, then
`Rationale:`, then `Verification:` (`skills/yf-plan/spec/agents.md:15`):

```markdown
REQ-AGENT-010: The coordinator drives the bead DAG via a `bd ready` -> claim -> execute -> close loop.
Rationale: This is the core execution engine; deviating from the loop skips work or double-executes.
Verification: coordinator.md Loop section describes the 6-step cycle.
```

## F6 — The `Verification:` line is where the quality bar lives, and prose fails it

Two grades exist and the newer convention names the weak one a defect.

- **Weak / prose:** `Verification: reconciler.md Rules: "Verify before acting…"` (`agents.md:29`)
- **Strong / executable** — a whole-line backticked command (`agents.md:112`):

  ```
  Verification: `uv run skills/yf-plan/scripts/test_review_agent_contract.py && grep -qF "Read-only with respect to the repository under review" skills/yf-plan/agents/reviewer.md && ...`
  ```

`spec/cli.md:35` states the doctrine: *"Verification: **executed**, not asserted."*

`test_review_agent_contract.py:13-26` records the measurement that motivated it:
*"`skills/yf-plan/spec/agents.md` had **0 of 26** exit-code-decidable `Verification:` clauses.
Corpus-wide the figure was **1 of 251**… **Naming a `test_*.py` in a Verification line is NOT
execution.** Thirty clauses in this corpus already do that and it buys nothing mechanically."*

This is issue **#165** in the plan's own substrate. Every requirement plan-060 adds must carry an
executable `Verification:`, or it ships the exact defect it is adjacent to.

## F7 — The coverage gate: three mechanisms, and only one is enforced

- **(a) `yf/src/coverage.rs` — enforced under `cargo test`, but `REQ-YF-*` ONLY.**
  `every_testable_req_is_tagged_or_allowlisted` asserts each `*(testable)*` macro REQ carries a
  `// REQ-…` comment tag in an in-crate `.rs` source, or an `ALLOWLIST` entry.
  Its scope is stated honestly at `coverage.rs:10-17`: *"This proves a test *names* a REQ id, not
  that its assertions actually verify the requirement's intent… a tripwire… not a proof of
  correctness."*
  **`REQ-AGENT-*` / `REQ-CLI-*` / `REQ-PLAN-*` are NOT in this gate's enforced set.**
- **(b) `CHANGE-VALIDATION.md` recipe rows** — the only thing that makes a `Verification:` line
  actually run. The rows plan-060 will fire:
  `skills/yf-plan/spec/cli.md` -> `uv-yf-cli-enum`; `spec/agents.md` -> `uv-yf-review-agent`;
  `agents/*.md` -> `uv-yf-gates`, `uv-yf-review-agent`, `uv-yf-review-verdict`;
  `spec/*.md` -> `cargo`, `uv-yf-close-contract`, `doclint`, `doclint-tests`.
- **(c) `scripts/checks/check-req-coverage.py`** — per-plan, not repo-wide: an issue covers a REQ if
  it names the id, or `depends-on` (directly or transitively) an Epic-0 issue that adds one, or is
  marked a bug fix to a shipped REQ. Exit `0/1/2` with a `--min-issues` fail-loud floor. Paired with
  `check_amendment_log.py`. **These two are the instruments a SPEC-first plan wires as Epic-0
  success criteria** — plan-060 should do the same.

**Python-side REQ tagging is prose in a module docstring, not a machine-read tag** —
`test_complete_gate.py:13` (`Covers (tagged REQ-PLAN-069):`). There is no `coverage.rs` equivalent
for the Python skills.

## F8 — The read-only agent template a `lander.md` must match

**Front-matter — 5 keys, in order, `model:` deliberately empty** (`agents/reconciler.md:1-6`):

```yaml
---
name: Reconciler
role: closeout
model:
description: Updates upstream issues after execution is complete and changes are pushed.
---
```

**Section order:** `# <Name>` -> one-line restatement of `description:` -> `## Inputs` ->
(`## Read` if it enumerates its read-set) -> `## Execute` / domain section -> `## Output` (a fenced
template) -> `## Rules` (bold-led imperative bullets).

**Length band:** 49 (reviewer) – 127 (red-team) lines for focused agents; 79–109 is the norm.
(Coordinator is 308, an outlier.)

**Read-only-ness is declared in TWO places** — an `## Inputs` annotation *and* a first `## Rules`
bullet. `captor.md:14` (`` `plan_dir` — plan directory path (read-only from the agent's
perspective) ``) and `captor.md:70` (`- **Never write files.** The main session writes after
operator approval.`).

> **This is mechanically load-bearing.** REQ-AGENT-043/045's `Verification:` lines are literal
> `grep -qF` over **exact sentences**. A lander requirement copying that pattern requires
> `agents/lander.md` to carry the strings `Read-only with respect to the repository under review`
> and `A sandbox spike is authorized` **verbatim**.

**Dispatch wiring** is two-sided: SKILL.md prose (``Read `${SKILL_DIR}/agents/reconciler.md` and
follow its procedure.``, `SKILL.md:1583`) **and** bead metadata
(`--metadata "{\"agent\":\"agents/reconciler.md\",...}"`, `SKILL.md:1208`).

## F9 — The reconciler is NOT read-only, and that matters for the lander's design

`reconciler.md` is the one closeout agent that **does** mutate — it runs `gh issue close` /
`gh issue comment` directly. Its safety posture is procedural, not structural: *"Verify before
acting. Never update upstream without confirming work was done"* (`:104`), *"If verification fails,
flag for operator — do NOT update upstream"* (`:28`).

> **This is the strongest single argument for #301's inversion.** The existing upstream-writing
> agent guards an outward-facing write with **prose rules an agent may or may not follow** — the
> identical shape as #293's free-text close reason. A `lander` that produces a decision document and
> writes nothing is not a stylistic preference; it is the correction of a defect that is *already
> live* in `reconciler.md`.

## Absence findings

- **No `REQ-LAND-*` family exists**, and no requirement anywhere describes merging, pushing, or
  pruning. Landing is entirely un-specified — consistent with EXP-001's finding that no code
  performs it.
- **No per-skill REQ-to-test coverage gate** for the Python skills; `coverage.rs` covers `REQ-YF-*`
  only. A new `REQ-CLI-030` / `REQ-AGENT-065` is bound only by whatever `Verification:` command the
  plan writes and registers in `CHANGE-VALIDATION.md`.

## Implications for Plan

**measured:** `REQ-<PREFIX>-NNN` is a namespace shared across skills, and two ids in the `REQ-PLAN`
family are already anomalous (`082` consumed but undefined, `078` retired). An id-allocation issue
must land before any other issue allocates, on the plan-049 precedent.

**measured:** the only enforced REQ-to-test coverage gate covers `REQ-YF-*` alone. A new
`REQ-CLI-030` / `REQ-AGENT-065` is bound by nothing except the `Verification:` command the plan
writes and registers in `CHANGE-VALIDATION.md` — so a prose `Verification:` line would ship a
requirement nothing checks.

**inferred:** because REQ-AGENT-043/045's verifications are literal `grep -qF` over exact sentences,
a lander requirement copying that pattern constrains the *bytes* of `agents/lander.md`, not merely
its meaning.

## Recommendations

1. Open a new `REQ-LAND-*` family in `skills/yf-plan/spec/landing.md`, on the plan-057
   `REQ-OKFH-*` precedent, rather than overloading `REQ-CLI-*`.
2. Give every new requirement an **executable** `Verification:` line.
3. Append the amendment-log entry to the second blockquote region; appending after the blank
   non-`>` line at `SPEC.md:440` would open a sixth fragment and worsen #241.

---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-retrospective-schema
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-004 — `plan-retrospective.md`: schema, portability, and #145 consumability (D-6)

**Question:** What does adding a new plan-folder file require, and what schema makes it consumable by #145 without rework?
**Method:** read of the OKF baseline and yf-plan portability spec, plus **live audit experiments** against a scratchpad copy of `plan-042`. Repo untouched.

## Headline — backward-compat risk is essentially zero, but two silent traps exist

The audit has a **split design** that makes this safe:

- **Presence checks are a CLOSED, hand-enumerated list** (`_audit_plan`'s eight checks). There is
  no generic "expected files" table.
- **Conformance is OPEN / auto-discovering** — `okf.check_conformance` does
  `md_files = [p for p in sorted(target.rglob("*.md"))]`.

| Question | Answer |
| :-- | :-- |
| Does adding the file require an audit change to be *accepted*? | **No** |
| Would its **absence** newly fail the ~44 existing plans? | **No** — unless a presence check is deliberately added |
| Would its **presence, unstamped**, break things? | **Yes — hard fail on OKF-native plans** |

Measured on a scratchpad copy of plan-042 (baseline: `All checks passed.`):

```
bare plan-retrospective.md  →  [fail] okf:plan-retrospective.md: REQ-OKF-003: no YAML frontmatter block
+ type: Retrospective, okf_spec: OKF-PLAN  →  All checks passed.
```

And the fail is **downgraded to `warn` for OKF-legacy plans** per REQ-PORT-ACT-OKF — *"a hard
`fail` **only** for an **OKF-native, non-grandfathered** plan."* Corpus: 44 bundles, **15
OKF-native**, 29 legacy.

> **The emit side is fully backward-compatible by default.** Do **not** add a presence check in
> this plan; if one is ever added it must carry a REQ-PORT-ACT-OKF-style activation gate.

## Two silent traps — both must be schema-encoded

**Trap A — REQ-PORT-007 dangling-refs is a HARD fail with no grandfather.** The check walks every
`.md` in the bundle. A verbatim operator answer quoting a home path kills the whole audit:

```
[fail] dangling-refs: plan-retrospective.md: /Users/
```

It strips fenced blocks and inline code first, so **verbatim operator quotes must be fenced or
backticked**. This is a schema requirement, not a style note.

**Trap B — a `**Label:** value` line inside an entry is invisible to the plan audit but fails
`/yf-okf check`.** `okf.py` guards known metadata labels
(`{id, author, created, status, epic, fingerprint, idx, topic}`). Measured with
`**Status:** unresolved` under a `## RE-001` heading:

- `plan_manager.py audit` → **`All checks passed.`** (it filters to `_OKF_PORT050_REQS`, which
  excludes REQ-OKF-010)
- `okf.py check --skill yf-plan` → **FAIL** — *"REQ-OKF-010 — a `**Field:**` metadata line sits
  below the first `## `"*, plus a vocab warning for the unregistered `Retrospective` type.

So the schema **must not** use `**Status:**` / `**ID:**` / `**Created:**` / `**Author:**` /
`**Epic:**` as bold lead-ins inside entries. **Use a two-column table instead** — it dodges Trap B
entirely.

## What #145 needs that a naive friction log would omit

#145's central discovery is a **three-valued** escape axis, not two:

> **The fourth row is the discovery.** *Review escapes* (the check existed, missed it) and
> *process escapes* (no check existed) need separate counts.

Five fields a friction log would drop:

| Field | Why #145 needs it |
| :-- | :-- |
| `escape_class` | The three-way split `review-escape` / `process-escape` / `not-an-escape` — *"the two escape kinds have different fixes"* |
| `origin` **and** `culpability`, **separately** | *"Origin — which plan the code came from… Culpability — which review could have caught it **given what was knowable then**"*, with *"**default to 'no review at fault'** unless the evidence was demonstrably available"* |
| `adjudication` (the reasoning, not the label) | Goodhart mitigation: *"record the **adjudication and its reasoning**, not just the count, so classification is reviewable after the fact"* |
| `prevention`, constrained vocabulary | *"Constrain 'prevention' to **executable or checkable** categories: `SPEC requirement` · `phase validation` · `test case` · `process step`. 'Be more careful'… are **inadmissible**."* |
| `frontloadable` | The operator's stated purpose. **Not in #145** — it is the axis #145's escape metric does not carry |

#145's **Open question 1 is literally this experiment's question**: *"Where exactly does intra-plan
capture write — `log.md`, a `reviews/postmortem.md`, or plan.md frontmatter? It must survive
`/clear` and be readable cold."*

**Inherited contract:** any close-time emit step must honour REQ-COMPLETE-003's envelope —
one JSON verdict to stdout on every path — because `test_close_contract.py` parses SKILL.md §6.4
and *"a new escape-capture step that ignores the envelope will fail CI"*.

## Proposed schema

Root-level `plan-retrospective.md`, non-reserved concept doc (OKF's reserved set is fixed upstream
at `("index.md", "log.md")` and cannot be extended locally). Entries are `## RE-NNN` sections with
a **two-column key/value table** per entry.

Fields: `when` (phase · bead · date) · `stop_class` · `asked` · `answered` · `frontloadable` ·
`escape_class` · `adjudication` · `origin` · `culpability` · `prevention` · `cost`.

**Four `stop_class` values** (the emit-side axis, orthogonal to `escape_class`):

| `stop_class` | Meaning | Fix owner |
| :-- | :-- | :-- |
| `missing-input` | Plan needed a fact only the operator held | plan (frontload) |
| `ambiguity` | Plan said two things, or was underspecified | planner / red-team prompt |
| `defect` | A plan or execution artifact was wrong | `escape_class` decides |
| `environment` | External tool/network/host failure | neither — counted, not actioned |

**Anti-requirements:** no bold metadata lead-ins below the first `## ` (Trap B); fence any quote
containing `/Users/`, `/home/`, `/tmp/`, `C:\`, `../` (Trap A); **must not** be written into
`log.md` (a `- review:` token there breaks REQ-PORT-006 count-equality); **must not** live at
`reviews/postmortem.md` (that dir is globbed `pass-*.md` and it muddles the `Review` type).

## Registration work (small, all additive)

1. `OKF-EXTENSION.md` §1 — add a `Retrospective` vocabulary row; §1a — a
   `plan-retrospective.md → Retrospective` glob row **above** the `*` catch-all. Skipping this
   costs a permanent `okf.py check` warning on every bundle.
2. `spec/portability.md` — new REQ for file shape + entry field set, **with an activation gate**.
3. `spec/data.md` REQ-DATA-002 — add to the bundle-layout sentence.
4. `plan_manager.py` — `_INDEX_MEMBERS` bullet + an append verb.
5. `DRIFT-CHECK.md` — a yf-plan ↔ yf-retrospective taxonomy edge (#145 proposes exactly this:
   *"Two homes for one taxonomy… the `yf-drift-check` edge is the mitigation"*).

## Two implementation constraints

**Do NOT generalize `okf.append_log`.** It is shape-specific to `log.md` (hardcoded `b / "log.md"`,
`_LOG_DATE_RE`, newest-first date grouping), and it is **vendored in four copies** (`yf-plan`,
`yf-research`, `yf-incubator`, `yf-okf`) behind byte-identical `e-okf-copy-*` drift edges. Write a
local `append_retrospective()` in `plan_manager.py` mirroring its create-if-absent + idempotence
contract instead.

**Create-on-first-entry, not seeded at init** — following the `reviews/pass-N.md` precedent.
Seeding an empty one would be worse: an empty typed file is indistinguishable from "nothing went
wrong", and REQ-PORT-010 forbids the audit from judging content, so it could never tell.

## Write sites (highest-volume first)

`coordinator.md`'s blocked-gate *"Wait for operator"* is the **highest-volume site**. Then: §3
review resolution, §3 portability-audit fail, §3 ready-check not-ready, §5.2 resume prompt, §5.2
dirty worktree, §6.1.5 validate fail, §6.4 chain halts, and **every `--force` override** (which
already logs a reason to `log.md` — mirror it). Excluded by design: §6.2 push authorization
(a deliberate consent gate, not friction).

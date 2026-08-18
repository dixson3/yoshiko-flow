---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-spec-amendment-surface
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-006 — The SPEC amendment surface and validation consequences

**Question:** Which requirements encode the operator-stop assumption, which must survive, and what proves an autonomy change?
**Method:** read of `skills/yf-plan/{SPEC.md,spec/*}`, `skills/yf-herdr/*`, `yf/src/coverage.rs`, `DRIFT-CHECK.md`, `CHANGE-VALIDATION.md`, plus a grep audit of the test suites. Read-only.

**Mid-edit status (measured):** the shared checkout's `skills/yf-plan` is byte-identical to HEAD.
plan-044 works in its own worktree and has modified `SKILL.md`, `agents/coordinator.md`,
`spec/cli.md` — but has **not** touched `SPEC.md`, `spec/phases.md`, `spec/agents.md`,
`spec/portability.md`, or **any** `skills/yf-herdr/*`. Quotes from those files are stable.

## Headline — the amendment surface is smaller than feared

**Exactly four normative edits are required.** Several requirements that *look* like they encode
the stop are actually actor-agnostic and should be left alone; amending them would be scope creep
into the consent model.

### Amend (4)

| REQ | The offending clause | Fix |
| :-- | :-- | :-- |
| `REQ-AGENT-043` | *"…then the same file is updated in place **as the operator resolves concerns**"* | Make the resolver **actor-agnostic**. The read-only clause is compatible and must survive (also GR-PLAN-002) |
| `REQ-AGENT-061` | *"The captor is read-only. It returns drafts for **operator review**…"* | Same shape — would drift if left |
| `REQ-PORT-008` | Names the **"Operator Resolutions"** table normatively — the *only* place it is fixed | Amend **only if renaming** |
| `REQ-RESUME-001` | *"execute must not pour again and instead **prompts the operator (resume vs. new) via `AskUserQuestion`**"* | Autonomy may default to **resume** (the safe branch). **"never fabricating a second epic" must survive** |

### Do NOT touch — compatible as written

- **`REQ-PLAN-030`** — *"The red-team shall be **re-run after any major-concern revision**… Readiness
  keys on the **last recorded** red-team verdict being `APPROVE`."* **It names no actor.** An
  autonomous session that revises and re-runs satisfies it verbatim. **This is the requirement
  most at risk of an unnecessary amendment.**
- **`REQ-PHASE-005`** (PLAN→INTAKE on explicit operator approval) — consent to a *plan*, not a
  loop stop. Touching it would gut the approval model and cascade into REQ-PLAN-033/034/066.
- **`REQ-SESSION-001`** (start gate is human-type) — authorization *to begin*. Mechanically
  verified against the formula file and mirrored in REQ-DATA-040 and SKILL.md; amending needs all three.
- **`REQ-AGENT-011`** (drain before reporting blocked gates) — *pro-autonomy already*.
- **`REQ-RESUME-002/003`** (report, never auto-close) — a **data-safety** invariant, not an
  attention gate. Costs autonomy nothing.
- **`REQ-PLAN-062`** (conservative push), **`REQ-HERDR-020/021/023/024/032`**, `GR-PLAN-002/003`.

**`REQ-HERDR-024` already contains the autonomy predicate** — *"The parent shall answer a
subordinate's question itself **only** when the answer is settled by existing approved plan
content. Anything that changes scope, risk, or a success criterion shall go to the operator."*
Write the new rule *against* this line rather than inventing one.

### Add (2–3) — the unanchored prose

Two behavior changes have **no requirement to amend, only one to add**:

1. `coordinator.md`'s **"Wait for operator"** is a bare bullet with **no REQ id**. → new
   `REQ-AGENT-064` (or block-local `014`, beside REQ-AGENT-011/013).
2. yf-herdr's autonomy line lives only in a *"Two traps"* prose aside. §2.2 Launch has **no REQ
   governing prompt content** (REQ-HERDR-013 governs the agent *name* only). → new
   `REQ-HERDR-015`.

Changing either silently is precisely the drift risk this plan must avoid.

## SPEC-first is mechanically forced, not just policy

`DRIFT-CHECK.md` §7 marks `spec` and `per-skill-spec` as **fixed authority**:

> A fixed-authority conflict (the spec is stale) is a CONFLICT, not a FAIL… never edit a spec or
> guardrail to make a derived artifact fit.

So editing `SKILL.md` to make execution autonomous *while* `REQ-AGENT-043`/`REQ-RESUME-001` still
say "operator resolves" produces a **FAIL on the SKILL.md node**. Sequence is forced:
`spec/agents.md` + `spec/phases.md` + `yf-herdr/SPEC.md` **first**, then SKILL.md/coordinator.md.

## Nothing mechanical guards these requirements

`yf/src/coverage.rs` reads **only** the repo-root `SPEC.md`, accepts **only** `REQ-YF-` ids
(`is_req_id` hard-requires `strip_prefix("REQ-YF-")`), and scans **only** `yf/src/**`.

> **`REQ-AGENT-*`, `REQ-HERDR-*`, `REQ-PORT-*`, `REQ-PHASE-*`, `REQ-RESUME-*` are gated by
> NOTHING mechanical.** `*(testable)*` on a per-skill REQ is **decorative** — it buys a
> hand-written `Verification:` line, no CI obligation and no CI protection.

Corroborating evidence that this is a real cost: **`REQ-PLAN-073` is double-allocated** —
`SPEC.md` uses it for configurable plan/incubator roots, `spec/phases.md` uses it for the coarse
tracker `external_ref` stamp. Both are live and separately tested. Do not cite it bare.

## Validation coverage — the yf-herdr half is unprovable today

`skills/yf-herdr/` contains exactly **three files**: `README.md`, `SKILL.md`, `SPEC.md`. No
scripts, no agents, no tests. Its SPEC admits it: *"`yf-herdr` ships no scripts, so it has no
Tier-1 suite."* The three claimed mechanisms reduce to: install-parity (presence + group
membership only — would not notice any prose change), drift-check (LLM judgment, 2 edges on a
SPEC edit), and *"evidence-driven observation"* (an honesty convention, not a mechanism).

CHANGE-VALIDATION FAST ids that fire:

| Edited path | FAST ids |
| :-- | :-- |
| `skills/yf-plan/SKILL.md` | `uv-yf-close-contract`, `uv-yf-audit-close`, `uv-yf-reconcile-step`, `frontmatter` |
| `skills/yf-plan/agents/*.md` | `uv-yf-review-verdict`, `frontmatter` |
| `skills/yf-plan/scripts/*.py` | 13 `uv-yf*` ids |
| **`skills/yf-plan/spec/*.md`, `SPEC.md`** | **NONE** |
| **`skills/yf-herdr/SKILL.md`** | **`frontmatter` only** (shape, says nothing about behavior) |
| **`skills/yf-herdr/SPEC.md`, `README.md`** | **NONE** |

DRIFT-CHECK §6 confirms `skills/*/SKILL.md` fans out to exactly **19 edges**;
`skills/*/spec/*.md` → 1; `skills/*/SPEC.md` → 2; `skills/*/agents/*.md` → 2.

> An autonomy change confined to `yf-herdr/SKILL.md` + `SPEC.md` + `yf-plan/spec/*` fires **only
> `frontmatter`** — a vacuous pass. The plan must add §3 rows, following plan-042's precedent
> (name a **test target**, not a name filter — a missing target hard-errors; a filter matching
> nothing passes vacuously).

## Renaming "Operator Resolutions" is FREE

Measured: the literal string appears in **zero** `.py` files — only in SKILL.md prose and
REQ-PORT-008. `"unresolved"` in `.py` appears only in unrelated senses (`close_cascade.py`'s gate
comment, worktree reason codes). The fingerprint exclusion is a **comment**, not code
(`FINGERPRINT_EXCLUDE_SECTIONS = {"upstream issues"}`).

**No parser, no test, no fingerprint code touches it.** Renaming costs REQ-PORT-008 + four
SKILL.md prose sites.

## What WOULD break

**`_plan_review_line_count` / REQ-PORT-006 count-equality** — asserted at **8 call sites** across
three test files:

```python
assert pm._plan_review_line_count(pd) == len(list((pd / "reviews").glob("pass-*.md")))
```

This breaks **if and only if** autonomy changes how many `pass-N.md` files a cycle produces, or
when the `log.md` `review:` line is written. REQ-PORT-006 already states the invariant survives
the REVISE re-run loop, so an autonomous session that revises and re-runs produces the same 1:1
pairing → **no break**. A design that skips a pass file on an autonomous cycle, or batches
revisions into one file, **would break all eight**.

`ready-check`'s verdict parse (`re.match(r"#{2,3}\s+Verdict:\s*([A-Za-z-]+)"…)`) breaks only on a
vocabulary/heading change — autonomy touches neither.

## Next-free REQ ids

`REQ-AGENT-*` and `REQ-PHASE-*` and `REQ-CLI-*` are **shared namespaces** with yf-research.
**plan-044 reserves `REQ-CLI-020` and `REQ-PLAN-077`** — start after them.

| Family | Next free |
| :-- | :-- |
| `REQ-AGENT-*` | **064** (block-local: 014, 032, 049, 052) |
| `REQ-PHASE-*` | **008** |
| `REQ-CLI-*` | **021** (020 taken by plan-044) |
| `REQ-PLAN-*` | **078** (077 taken by plan-044) |
| `REQ-RESUME-*` | **005** |
| `REQ-PORT-*` | **051** (block-local: 013, 021, 034, 042) |
| `REQ-HERDR-*` | **042**; block-local **015** (Launch), **026** (Observation) |
| `REQ-SAFE-*` | belongs to **yf-beads-upstream** — do not use in yf-plan |

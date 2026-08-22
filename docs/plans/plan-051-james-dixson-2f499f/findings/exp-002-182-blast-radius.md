---
type: Finding
okf_spec: OKF-PLAN
id: exp-002
description: What is the COMPLETE edit set for #182, and what catches a miss at each site?
---

# EXP-002 — #182's blast radius

## Approach Tested

Exhaustive repo grep for `never writes files`, `Read-only`/`read-only`, `REQ-AGENT-043`, with every
hit classified as authority / restatement / fixture / historical record. md5-compared both files
against all five harness deployment roots. Read `DRIFT-CHECK.md` §1/§2/§3/§6/§7 and
`CHANGE-VALIDATION.md` §3 in full. **Sandbox spike:** local clone, applied the candidate edit, ran
the FAST tier in both a *consistent* and a deliberately *dangling* state. Clone removed.

## Result

**measured:** exp-006's "one line in one file" is wrong by a factor of ~7.** The minimum consistent
edit set is **7 files** (8 with the reviewer sibling), not 1.

| Surface | Line | Class |
| :-- | :-- | :-- |
| `skills/yf-plan/agents/red-team.md` | 63 | **authority — the rule** |
| `skills/yf-plan/spec/agents.md` | 71, 72, **73 (pins the literal)** | **authority — fixed** (§7) |
| `skills/yf-plan/SKILL.md` | 486, **516** (`The agent never writes files`) | restatement, drift-checked |
| `skills/yf-plan/SPEC.md` | 65, **390 (GR-PLAN-002)** | restatement, drift-checked |
| `web/content/skills/yf-plan.md` | 34 | restatement, drift-checked |
| `web/content/pages/workflows.md` | **172**, 180 | restatement, **NOT drift-checked** |
| `web/content/pages/glossary.md` | 90 | restatement, **NOT drift-checked** |
| `skills/yf-plan/agents/reviewer.md` + `spec/agents.md:95/97` | 43 | **sibling authority** — scope decision |
| `spec/portability.md:69,135` | — | cites REQ-AGENT-043 for the *actor-agnostic* clause only — **no edit** |
| `docs/plans/**`, `docs/research/**`, `.beads/issues.jsonl` | — | historical records — **do not edit** |

**measured:** no test pins this string.** `test_gates.py`, `test_review_verdict.py` and
`test_autonomy.py` pin *other* strings (`gate the mutating step`, `earliest legal`, `## Verdict:`).

**measured:** there is no canonical/vendored copy.** `grep -n "red-team\|agents/" _shared/sync.py` →
**zero hits**; `protocols/manifest.json` hashes only `PLANS.md` and `DOC-LINT.md`. Parity is restored
by `yf self install --from-build --build`, not by any per-file mechanism.

**measured:** deployed parity holds today.** `red-team.md` md5 `5a1eb1cc…` identical across repo,
`~/.claude` and `~/.agents`; `~/.codex`, `~/.opencode`, `~/.pi` **absent**. Only two harness roots
exist on this machine.

### The spike: the FAST tier does NOT catch the dangling pointer

Consistent state (both files edited) — 7 ids, all pass. **Dangling state** — `red-team.md` reworded
while `spec/agents.md:73` still pins a string that no longer exists
(`grep -c 'Read-only — never writes files' red-team.md` → **0**):

```
pass ... first_failure None
```

**measured:** FAST passes green on a broken tree. FULL is the same command set, so it does too.**

**inferred:** corroborated by the spike — there is **no declared `spec → agent` edge** in
`DRIFT-CHECK.md`. The graph has `e-spec-compliance` (`spec` → `skill-md`), `e-agent-ref` (path-resolves
only) and `e-status-values` (status vocabulary). REQ-AGENT-043's `Verification:` pins a literal in
`red-team.md` and **nothing verifies that pin** — the same class pass-4's C24 flagged on plan-050.

**measured:** `AGENTS.md:78-80` is reusable in substance, NOT verbatim.** Two clauses do not travel:
the plan-049 anecdote (a foreign vault's operator cannot check it) and *"Reviewers **and
investigators**"* (the investigator already gets a disposable worktree and needs no carve-out). The
portable core is *"read-only scopes the repository under review"* + *"a sandbox spike in
`$(mktemp -d)` is authorized; leave no residue."* The provenance belongs in the REQ's `Rationale:`.

## Implications for Plan

1. **The blast radius is largely invisible to automation.** The spec→agent pin and both
   `web/content/pages/*` restatements sit outside every mechanical gate.
2. **§7 fixed authority + SPEC-first**: amend `spec/agents.md` first, everything else after. A root
   `SPEC.md` amendment-log entry is also required (precedent: `SPEC.md:264`).
3. **EXP-004 supplies the missing gate.** Its ctl-182 fixture asserts spec↔prose quote parity and
   **catches the dangling state this spike proved FAST misses** — which is why #182's control is real
   and D-8's "cannot have one" is wrong about the edit set.
4. **A scope decision the plan must make explicitly:** `reviewer.md:43` carries the identical literal
   (REQ-AGENT-045, `spec/agents.md:97`). Rewording only red-team leaves the two agents saying
   different things about the same constraint, and `AGENTS.md` says *"reviewers"* plural.

## Recommendations

1. **Ship the 12-step ordered edit list**, SPEC-first, with "what catches a miss" per step — steps 3,
   9 and 10 are the ones where the honest answer is **nothing mechanical**.
2. **Include `reviewer.md`** (step 11), or record an explicit decision not to, so the divergence is
   deliberate rather than an oversight.
3. **Add a `DRIFT-CHECK.md` edge `e-spec-agent`** (`spec` → `agent`, contract): *every REQ-AGENT-\*
   `Verification:` clause quoting a literal from an `agents/*.md` file resolves to a string present
   in that file.* This is the systemic fix behind step 3; plan-050's pass-4 already hit the class once.
4. **File the `--changed` repeated-flag defect** as a separate upstream issue — orthogonal to #182,
   discovered by this spike. **CONFIRMED at source rather than taken on report:**
   `change_validation.py:946` declares `--changed` with `nargs="*"` and **no** `action="append"`, so a
   repeated flag overwrites instead of accumulating and `--changed A --changed B` validates only `B`.
   The experiment's own inference about the mechanism was right; its illustrative id-count comparison
   was not reproducible here because the FAST tier's `cargo` row dominates the output.
5. Redeploy at land-the-plane only (`yf self install --from-build --build`), never mid-execution.

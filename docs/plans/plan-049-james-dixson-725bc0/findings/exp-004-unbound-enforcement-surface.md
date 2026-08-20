---
type: Finding
okf_spec: OKF-PLAN
id: exp-004
status: complete
---
# EXP-004 — What is actually unbound after plan-048

**Question:** Re-measure the enforcement surface; characterise the two §3 vacuities; determine what
the always-on rule requires today.

## Approach Tested

Read the current `CHANGE-VALIDATION.md`, `doc_lint.py` (638 lines), all **17** schemas,
`test_doc_lint.py`, `plan_manager.py`, `spec/data.md`, `yf/src/embed.rs`. Then **executed**:
whole-corpus and per-type lints; `--path` on a research file vs a nonexistent path; a live mutant on
a research Summary; a FAST run scoped to research; a sweep copying **all 48 bundles** to a temp root
at `review`; a fresh `init` at three statuses; a promotion probe at `executing` vs `review`; a
unique-file coverage census. Worktree left clean.

## Result

### 1. Binding table

| Binding point | Bound? | Evidence | Mutant |
| :-- | :-- | :-- | :-- |
| `doclint` FAST/FULL | **yes, runs** | FAST scoped to research → `status: pass`, non-empty tail | copy a bundle, set `review` → exit 1 (47/48 do) |
| `doclint-tests` | **yes** | SC5b ×13 and SC10 m1–m7 all green | revert `finding.toml` globs → 5 assertions fail |
| **D-11 `files_checked > 0` guard** | **YES — plan-048 landed it** | `test_doc_lint.py:345-353` | **but corpus-level only, NOT the on-edit `--path` shape** |
| `update-status approved` (#125) | **yes** | `plan_manager.py:1318,:1332` | force `ready=True` → test fails |
| **(a) `_audit_plan` ← linter** | **NO** | `grep doc_lint plan_manager.py` → **3 hits, all prose comments** | inject a malformed header; `ready-check` must exit 3. **Exits 0 today** |
| **(b) always-on on-edit rule** | **NO** | `grep -rln doc_lint ~/.claude/rules/ skills/*/protocols/` → **zero** | manifest sha + a glob whose deletion reddens a committed control |
| **(c) three positive controls** | **NO** | gate scripts exist only *inside* bundles; **no §1 row names any** | delete the `docs/plans/**` §3 row → control must exit 1 |
| **`plan-relations` promotion-off** | **NO — declared twice, implemented nowhere** | `spec/data.md:308-313` and `plan-relations.toml:7` both say promotion does not apply; `doc_lint.py:590` applies `mapping.get()` **unconditionally**, no kind check, no test | **measured:** m2 fixture at `executing` → `R:R1b` exit 0; **same file at `review` → `E:R1b` exit 1** |

### 2. The §3 vacuities, re-measured

**`docs/research/**` — the *selection* vacuity is CLOSED.** **measured:** a real research file →
`files_checked: 1`; a nonexistent one → `files_checked: 0`. plan-048's silent-green is gone.
**33 of 41** research files are selected; the 8 unreached are OKF-reserved or one-offs.

**But the row still cannot FAIL** — all five research checks are `W`, and `bundle_status` is null off
the plan axis so `W` stays `W`. Live mutant: replacing a Summary with `# empty` → 2 warnings,
`exit=0`. **This residual is DELIBERATE:** `REQ-DATA-045` forbids an `E` off the plan axis unless the
corpus already passes. **So D-5 is a no-op as a "fix the mapping" item.**

### 3. The `Incubator/*` rows: two different things

- **Schema `paths` globs** (13 of 17) — **correct and load-bearing for a vault that has
  `Incubator/`.** Keep unchanged; `select()` simply returns nothing, and inertness-where-nothing-
  matches is the engine's design.
- **`CHANGE-VALIDATION.md` §3 rows** — this manifest is **per-repo and never deployed** (not under
  `skills/`, so `embed.rs:47` does not carry it). Dead weight *here*, correct *nowhere else*.

**Verdict: a permanent no-op to document, not a vacuity to fix.** One preamble line, no epic.

### 4. The always-on rule — a fourth trigger shape

The three precedents gate on a marker or an approved manifest; this one gates on **nothing**, with
inertness from path-keying. Requirements, measured:

1. **Path-keying is already implemented and tested** — all 17 schemas key on a directory prefix,
   never a bare filename; `test_doc_lint.py:120-126` pins the empty-repo case. **This is the marker
   substitute and needs no new code.**
2. **The `files_checked > 0` assertion is landed at corpus level but NOT at the on-edit shape.** The
   rule invokes `--path <changed>`, where an unselected path is still
   `{"files_checked": 0, "verdict": "PASS"}` — byte-identical to a nonexistent path. **The rule text
   must mandate parsing `files_checked` and reporting `not-a-typed-document`** — an exit code cannot
   carry this.
3. `E`/`W` split + promotion — implemented and measured.
4. **NEW, previously unnamed hard prerequisite: the engine does not ship.** **measured:**
   `find skills -name doc_lint.py -o -name document_types` → **empty**; `embed.rs:47` embeds only
   `../skills`. **An always-loaded rule invoking `${SKILL_DIR}/scripts/doc_lint.py` would reference
   a file that exists in no deployed vault.** All three precedent skills ship their script under
   `skills/<name>/scripts/`. Named by neither plan-047 nor plan-048.
5. **Whole-corpus vs scoped:** the `doclint` §1 row takes **no path argument**, so §3 selects *which
   ids run*, never *which paths are linted*. A research edit triggers a 731-file sweep. Cost is not
   the constraint (0.24 s); **false reds on untouched files are.**

### 5. Bound incompletely by plan-048

- **The promotion defect is live and self-inflicted on plan-049**, which `plan-relations.toml:11`
  names as *"the first plan graded by this kind"*. **measured:** plan-048 → `{R1b: 4}` at `review`.
  No test asserts promotion is off; no `DRIFT-CHECK.md` edge covers `doc_lint.py ↔ spec/data.md`,
  which is why two declarations disagreed with the code for a whole plan cycle.
- **The `doclint` row remains only conditionally non-vacuous** — all 48 bundles are `complete`, so no
  edit on disk today can redden it.
- **plan-048's "Epic 6.1 predecessor" is DONE — by downgrade, not conformance.** plan-047's bundle is
  the only clean one of 48. The `type == plan` safe-partial hedge is unnecessary.
- **Coverage roughly tripled:** 17 schemas, **683 unique files**, **72.8%** of the 938 in-scope `.md`
  (vs 174 / 23.4%). Still uncovered: `README.md` (58), `log.md` (26), `index.md` (25).
- `plan-relations` is missing from SC5b's list — latent, not live (it selects 48 today).

## Implications for Plan

- **D-5 is largely a no-op.** Schedule at most a re-measurement of whether one research check can be
  promoted to `E` with the corpus pass recorded, which REQ-DATA-045 explicitly permits.
- **A new unscheduled prerequisite exists:** vendor `doc_lint.py` + `document_types/` under
  `skills/<name>/scripts/` before any deployed rule can invoke them. **Hard blocker on binding (b).**
- **The promotion defect is urgent** — plan-049 will trip its own gate at its own INTAKE, the exact
  shape of plan-048's finding about plan-047.
- Size the binding epic at **five issues**: promotion fix, vendoring, (a), (b), (c) — with the two
  §3 vacuities demoted to documentation.
- **Absence-of-problem:** the findings-conformance blocker plan-048 called "the load-bearing
  predecessor" is **gone**. Do not re-schedule it.

## Recommendations

1. **Fix `plan-relations` promotion first** — a `promote = false` key or a kind guard at
   `doc_lint.py:590`, plus a test asserting the m2 fixture stays `R` at `review`.
2. **Vendor the engine into a skill** before writing the rule.
3. **Bind `_audit_plan` unconditionally** — the `type == plan` partial is no longer needed.
4. **Write the always-on rule with no marker**; mandate reading `files_checked` from `--json`.
5. **Promote the bundle gate scripts into §1 rows.**
6. **Add a `DRIFT-CHECK.md` edge for `doc_lint.py ↔ spec/data.md`** — the promotion defect is exactly
   the class that edge exists to catch.
7. **Record the `Incubator/*` §3 rows as a documented permanent no-op.**

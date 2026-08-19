---
type: Finding
okf_spec: OKF-PLAN
id: exp-004
status: complete
---
# EXP-004 — The enforcement binding surface

**Question:** What is bound today, what did plan-047 leave unbound, and what does "always opt-in,
no opt-out" require in code?

## Approach Tested

Read the actual code (`doc_lint.py`, `document_types/*.toml`, `plan_manager.py` at
`:1277-1400 / 3926-4260 / 4365-4440 / 4759-4852`), `CHANGE-VALIDATION.md`, `DRIFT-CHECK.md` §6,
`YOSHIKO_FLOW.md`. Then **executed**: whole-corpus lint, per-type lint, per-bundle severity
decomposition, a fresh `init` at three statuses, a mutant injected into a `complete` plan.md, a
FAST-tier run scoped to a research file, and a copy of plan-047's bundle flipped to `review`.
Worktree left clean.

## Result

### 1. Binding table

| Binding point | Bound today? | Evidence | What remains | Mutant proving non-vacuity |
| :-- | :-- | :-- | :-- | :-- |
| `doclint` FAST row | **yes, and it runs** | `CHANGE-VALIDATION.md:66`,`:112`; measured FAST run → `doclint pass`, non-empty `output_tail` | nothing | create an in-flight plan at `review` → `FAIL: 174 files, 1 error`, **exit 1** |
| `doclint-tests` row | yes | `:67`,`:113`; 23 assertions incl. `--no-exclude` positive controls | nothing | revert `finding.toml` globs to single-level → 5 assertions fail |
| `update-status approved` gate (#125) | **yes, real code** | `plan_manager.py:1315-1333`, `sys.exit(3)` unless `--override-ready-check`; deviation at `:1332` | nothing | force `_ready_check_result` → `ready=True` → `test_update_status_gate.py` must fail |
| `ready_check` | yes, but **linter-blind** | `:4791` calls `_audit_plan` only | — | — |
| **(a) `_audit_plan` consumes linter findings** | **NO — unbound** | `grep -n "doc_lint\|lint" plan_manager.py` → **2 hits, both prose comments** (`:85`,`:1297`). Zero imports, zero subprocess | the whole binding | inject a malformed `## Risks` header into an in-flight plan; assert `ready-check` exits 3. **Today it exits 0** |
| **(b) always-on on-edit rule** | **NO — unbound** | `grep -rln "doc_lint\|document linter" ~/.claude/rules/ skills/*/protocols/` → **zero** | the rule + its scoping semantics | a rule has no exit code — the falsifier must be a `manifest.json` hash check plus a §3 glob |
| **(c) three positive controls** | **NO — unbound at repo level** | the four gate scripts exist only *inside* the plan bundle and are not a §1 row | promote into a committed CI-run row | delete the `docs/plans/**` §3 row → the control must exit 1 |

### The killer, measured

**measured:** mutating a `complete` plan.md — deleting `## Success Criteria` and renaming `## Risks & Mitigations`
in plan-047's own `plan.md`:

```
PASS: 173 file(s), 0 errors, 0 warnings, 615 report-only     doclint exit=0
```

**No edit to any of the 47 existing bundles can make the `doclint` row fail.** `STATUS_SEVERITY`
(`doc_lint.py:75-78`) maps `complete → {W:R, E:R}` and all 47 are `complete`. The row is not
vacuous, but it is **conditionally** non-vacuous — and the condition (an open plan on disk) exists
*during* a plan and not between them. Corroborated: creating plan-048 and flipping it to `review`
drove the same command to exit 1.

### A second, unreported vacuity — measured

`CHANGE-VALIDATION.md:194` maps `docs/research/** → doclint`. **No schema selects any research
path:**

```
doc_lint.py --path docs/research/001-.../Summary.md --json → {"verdict":"PASS","files_checked":0}  exit 0
```

A **nonexistent** path returns the identical object. `--path` on an unselected file is a **silent
green**, so no mutation of any research document can ever fail the row it is mapped to. Same shape
at `:196` for `Incubator/*/research/**`.

**Coverage:** 744 in-scope `.md`; the linter checks **174** = **23.4%**. Unlintable today:
`reviews/` (112), `context.md` (48), `README.md` (30), `upstream-triage.md` (29), `log.md` (19),
`index.md` (18), `assets/` (15), all 41 research files.

**Cost is a non-constraint:** whole corpus 0.244 s cold / 0.213 s warm; `--path`-scoped 0.088 s.

### 2. "Always opt-in, no opt-out" — concrete semantics

The three precedents are marker- or manifest-gated (`.markdown-lint-on-edit`, approved
`DRIFT-CHECK.md`, approved `CHANGE-VALIDATION.md`). This is a **fourth shape**: always armed. The
only honest reading is **the opt-in is the artifact itself** — the rule fires unconditionally and
the inertness comes from **path-keying**, not a marker. Four properties, none sufficient alone:

1. **Path-keyed only** — already implemented (`plan.toml:9-13`, `finding.toml:12-16`) and tested
   (filename-keying would flag 62 errors on the 17 fixture `plan.md`; path-keying yields 0). In a
   repo with no `docs/plans/`, zero files select — **that is the substitute for the marker**.
2. **Status-aware promotion** — already in `doc_lint.py:61-79`. A fresh `init` at `scoping`
   measured `errors=0, warnings=1`; the same file at `review` measured `errors=1, exit 1` — a
   *correct* fail on an unedited placeholder.
3. **`E`/`W` split, only `E` exits non-zero** — implemented.
4. **`references/**` structural exclusion** — implemented.

**Blast radius, measured:** 174 selectable files, 0.088 s scoped. Two failure modes:

- **`--path <changed>`** is a **silent green on 76% of the corpus**, because an unselected path is
  indistinguishable from a clean one. This is the #164 class re-created at the rule layer.
  **The binding must assert `files_checked > 0` or report `not-a-typed-document` explicitly.**
- **Whole-corpus** fires red on untouched files. Green today, but the moment one in-flight plan sits
  at `review` with a non-conformant `findings/*.md`, **every unrelated edit anywhere goes red.**

### 3. Would a fail-closed `_audit_plan` break existing bundles? — measured

```
bundles with >=1 declared-E finding: 47 / 47      fully clean bundles: 0
would fail on PLAN-type findings alone:    46 / 47
would fail on FINDING-type findings alone: 35 / 47
bundles whose plan.md is clean: ['plan-047-james-dixson-dec9ff']
```

**The decisive experiment:** copying plan-047's own bundle — the plan that *built* this linter,
red-teamed across four passes — and setting it to `review` yields **11 error-severity findings**
(6 `required-sections`, 5 `measured-marker`, all in `findings/*.md`).

> A fail-closed `_audit_plan` binding, with today's schemas, **would have blocked plan-047 at its
> own INTAKE.**

The claim "a hard linter gate at INTAKE breaks zero existing plans" is **true but answers a
different question**. It is true of the *historical* corpus (nothing re-audits a `complete` plan —
verified across all three `_audit_plan` call sites, and `audit-close` exits 0 unconditionally at
`:4436`). It is **false of the next plan**, which is the population the gate governs. Corroborated:
plan-046, completed one day earlier, fails `risks-table-columns` (missing `Severity`),
`criteria-table-columns`, `criterion-ids`, plus 9 findings files.

**Why the drift exists — the load-bearing sub-finding.** `diff` of the repo and installed
`investigator.md` → **IDENTICAL**. The installed prompt already mandates the exact four sections
`finding.toml` requires, and plan-047's own `exp-005` — written under that prompt — uses different
headings. **An agent prompt is not a producer.** The code-generated type is clean (a fresh `init`
passes every structural check); the agent-written type is not, and no amount of prompt authority
fixes it.

### 4. Ordering — and plan-047's declared order is wrong

plan-047 declares `9.1 depends-on 8.9` (the normalizer). **That dependency is not load-bearing and
the real one is missing.** The normalizer is hash-neutral by contract and refuses to write any
`complete` plan; the 47 historical bundles are already harmless via status promotion. The 11 errors
that would block a new plan live in `findings/*.md` written *after* any sweep, by an agent, during
execution. **A one-time corpus sweep touches none of them.**

**The load-bearing predecessor is Epic 6.1 (`findings/*.md`)** — until agent-written findings
conform by construction, binding (a) fail-closed is a guaranteed halt on every plan that runs an
experiment.

| # | Step | Falsifier |
| --: | :-- | :-- |
| 1 | fix the two live §3 vacuities (`docs/research/**`, `Incubator/*/research/**`) | assert `files_checked > 0` for a research path, or delete the mapping |
| 2 | promote a repo-level non-vacuity control into a §1 row | delete the `docs/plans/**` §3 row → control must exit 1 |
| 3 | **Epic 6.1** — `findings/*.md` conform at write time | copy a real bundle, set `review`, assert errors == 0 |
| 4 | binding (a), mapping *effective* post-promotion severity | inject a malformed heading; `ready-check` must exit 3 (exits 0 today) |
| 5 | binding (b), `--path`-scoped **plus** `files_checked > 0` | manifest hash check + a glob whose removal fails step 2 |
| 6 | the normalizer | independent of 4 and 5 — sequence by convenience, not dependency |

Safe partial if (a) must precede 6.1: **restrict the binding to `type == "plan"` only.**

## Implications for Plan

- Epic 9 is **three unbound bindings plus two pre-existing vacuities** the descope list never
  named. Size it at 5 issues, not 3.
- Rewrite `9.1 → 8.9` as **`9.1 → 6.1`**.
- Any success criterion of the form "the doclint row is green" **measures nothing**. Criteria must
  read "an in-flight bundle at `review` with an injected mutant drives exit 1".
- **Absence-of-problem, recorded:** the historical corpus is **not** a wedge risk. The wedge is
  entirely in front of us, not behind.

## Recommendations

1. Bind `_audit_plan` to the linter, but gate it behind the findings-conformance issue, or ship it
   **plan-type-only** as the safe partial.
2. Make the always-on rule's inertness **structural** (path-keying), not a marker — and mandate
   `files_checked > 0` in the on-edit invocation.
3. Fix the `docs/research/**` → `doclint` mapping in the same change-set as any new §3 row; it is a
   live #164-class defect today.
4. Promote `gate-doclint.sh`'s assertions out of the plan bundle into a `CHANGE-VALIDATION.md` §1 row.

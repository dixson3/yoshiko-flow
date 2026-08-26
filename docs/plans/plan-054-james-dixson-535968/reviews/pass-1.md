---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: Red-team pass 1 (first independent, dispatched via Agent) — plan-054
---

# Red-team pass 1

## Verdict: REVISE

8 high, 9 medium, 5 low. **All 22 resolved** — see the Resolutions table. First independent pass, dispatched as a sub-agent per REQ-AGENT-049.

## Strengths

- Genuinely SPEC-first; the DAG encodes it (`1.1←0.2`, `2.2←0.4`, `2.4←0.3`).
- Six experiments, three of which refuted a scoping premise, recorded in an explicit amendments
  paragraph rather than quietly retconned.
- **The load-bearing measurements were independently reproduced** — the 19-consumer count and
  the website's false three-formulas claim against 5 real `*.formula.toml`.
- The human release-authorization gate on the irreversible tag push is correct, and the plan
  read `web-deploy.yml`'s `workflow_run` chain right: Epic 5 genuinely precedes the tag.
- R1–R10 name the right hazards. The defect is that **the DAG does not encode most of them.**

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | **17 `assets/*.sh` scripts referenced; zero exist; no issue authors any.** Measured: 18 of 30 criteria return `inconclusive` (exit 127), and `plan_manager.py:3039` states `inconclusive` NEVER halts — so completion proceeds green having verified nothing. Only 11 of 30 criteria execute, on the plan that cuts an irreversible release. plan-053 spent EIGHT issues (1.0–1.7) on exactly this |
| C2 | high | **The control set is undefined.** `grep -c 'ctl-' plan.md` → 0. The RED gate quantifies over nothing; `verify-red-all` derives zero controls, so the gate is either vacuously satisfied or unsatisfiable and nothing distinguishes the two. **Not a cycle** — 0.1 sits outside `Blocks`, so the gate is correctly placed; its instrument is absent |
| C3 | high | **23 of 48 issues are not ancestors of 6.8, and R1's mitigation is false.** The plan permits tagging v0.5.0 with the whole shipped-defect epic open except 3.6, five of nine website issues open, the README rewrite open, deferred defects unfiled and stale issues unclosed. `6.6` depends on `5.8`, which depends only on 5.1/5.2 — so 5.3–5.7 escape the FULL tier and the 100-edge sweep entirely |
| C4 | high | **`verify-reconcile` will fail deterministically.** `partial` requires end-state OPEN, `include` requires CLOSED-with-attribution. #119 is `partial` while 6.2 is titled "Close #119". #154 is absent from the table entirely despite EXP-006 directing a rescope. plan-054's own coarse tracker row is missing |
| C5 | high | **SC7 cannot fail, so #226 could be "fixed" by doing nothing.** "A code-span `depends-on:` still yields no edge" is **already true on the unfixed tree**. No criterion asserts 3.3's *positive*. R2 promised the control assert both; the table delivers one. Worse, **3.3 is exempt from the RED gate** — the one issue the plan itself rates `high` for phantom-edge risk |
| C6 | high | **R5's mitigation is false.** `1.2 ← 1.1` and `1.3 ← 1.1` are **siblings**, so the 19-file fleet emit may land with the resolver unit tests never started — precisely the fleet-wide breakage R5 exists to prevent |
| C7 | high | **Nothing deploys the fixed skills, yet 6.7 runs a live regression against them.** pi and opencode read their installed dirs. No issue schedules a deploy, and `AGENTS.md` forbids `yf self install` mid-execution. So 6.7 either observes the OLD skills — passing on the unfixed resolver — or violates the repo's execution-safety invariant |
| C8 | high | **D-1 contradicts SC4 and the Approach.** D-1 keeps `find` as a "legacy fallback" and line 114 certifies it unamended; the Approach says "replace, do not extend" and SC4 demands the idiom survive at **zero** sites. Unenforced either way: EXP-001's coupled cwd-superset constraint, and **no criterion or risk covers `yf` absent from `PATH`** or binary version skew |
| C9 | med | `5.9 depends-on 6.2` is a typo for `6.5`; and `6.6` does not depend on `5.9`, so the web version bump ships to the auto-published site without validation |
| C10 | med | **The plan defers the three process defects most likely to bite it.** #229 (`redcheck.sh`'s `YF_TREE` assumes plan-050's layout) while this plan's gate depends on `redcheck.sh`; #232 (criterion commands never executed before approval) — which would have caught C1; #224 (`grep -qv` env-dependent) while commissioning 17 new shell scripts. Spiked: `grep -qv PAT file` exits 0 when any line lacks PAT, so it cannot fail on a large file |
| C11 | med | Issue 1.3 understates a real `sync.py` change: `EmittedRegionAsset.emit` is a **zero-arg** `Callable`, so 19 skill-name-parameterized bodies need a parameterized emitter. Also 3 of the 19 are *prose about* the idiom, not runtime consumers — generating them verbatim may be wrong |
| C12 | med | The live-regression gate is `auto` but R8 declares its failure INCONCLUSIVE-tolerant. **A gate that tolerates its own failure is not a gate**, and it is the last automated blocker before an irreversible, auto-publishing tag |
| C13 | med | **Findings work with no issue:** EXP-002's harness-provided base directory (the fix for the cross-tree skew the plan reproduced live — Epic 1 fixes only the not-found half); `allowed-tools` remediation across 10 `SKILL.md` files; `profile.rs` missing from 2.4's targets; the changelog **deprecations** section, though D-3 hinges the version choice on them; the amendment-log fragmentation issue; #154's rescope; R10's release note |
| C14 | med | `coverage.rs` fails the build for a `(testable)` REQ with no tagged test, so the REQ and its test must land together. The plan splits them 0.2 → 1.1 → 1.2 |
| C15 | med | **Self-contradiction in the shipped document**: Motivation says 11 `SKILL.md` files; the findings table says 19 consumers |
| C16 | med | **No issue merges to `main`.** 6.6/6.7 assume "the merged tree"; 6.5 also omits `Cargo.lock`, which cargo-dist's version check notices |
| C17 | med | SC12 hardens an inference into a machine gate — EXP-004 marks the grouping *inferred* and D-2 says "~10 themes", but SC12 demands exactly ten |
| C18 | low | SC14's formula count is ambiguous: `find . -name '*.formula.toml'` returns **10** (5 under `skills/`, 5 staged under `.beads/formulas/`) |
| C19 | low | Twenty issues hang off `depends-on: 0.1` including pure doc work — semantically wrong and a single serialization point |
| C20 | low | `1.6` depends on `1.3` but not `1.5`, so the isolated-HOME test misses the 14 hardcoded-path sites |
| C21 | low | Scope realism: 4.2 and 4.3 are each plausibly several days as a single issue |
| C22 | low | EXP-006's `KeptModified` whitespace finding has no disposition |

## Missing

1. Any issue that **builds the 17 `assets/*.sh` scripts** (C1) — the single largest gap.
2. Any **named control set** / `controls.txt` (C2).
3. A **deploy step** before the live regression (C7).
4. A **merge-to-main** issue (C16).
5. A criterion for **3.3's positive behaviour** (C5).
6. An **upstream row for #154** and a **coarse tracker row for plan-054 itself** (C4).
7. Risk coverage for **`yf` absent from `PATH`** and binary version skew after the resolver
   replacement (C8).

## Gate Assessment

Start Gate and Release Authorization: appropriate and correctly placed. **RED gate: structurally
reachable, functionally inert** — correctly positioned (0.1 outside `Blocks`, no frontloading
miss) but its Test names a nonexistent script and its Condition quantifies over an undefined set.
Coverage is uneven — it exempts 3.3, 1.3, 1.5, 2.1.

One nuance the reviewer recorded against a plausible objection: several blocked issues (2.2, 2.4,
3.6) are *false-GREEN* defects, which might look incompatible with a "non-zero exit observed"
condition. It isn't — a fixture exits 0 iff the asserted behaviour holds, so a false-green bug
does produce a non-zero fixture pre-fix. **The condition is sound; only its instrument is absent.**

## Upstream Assessment

Dispositions are mostly well-reasoned and EXP-005 genuinely improved them. The failures are
**mechanical rather than judgemental**: rows whose disposition and whose declaring issue disagree
about the required end state, and #154 absent entirely.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Added Epic 0 issues **0.6** (adopt plan-053's harness: `redcheck.sh`, authoritative `controls.txt`, `fixtures/`; split `assets/checks/` from `assets/fixtures/`), **0.7** (author every named control's fixture), **0.8** (author the sixteen criterion check scripts), **0.9** (verify every criterion command executes before approval). New **SC30** makes that verification itself a criterion. | `main-session` | `resolved` |
| C2 | high | **0.7 names all eight controls inline** — `ctl-201-changed-append`, `ctl-203-exit-discipline`, `ctl-206-resolver-isolated`, `ctl-225-column0-paragraph`, `ctl-226-leading-code-span`, `ctl-185-empty-triage`, `ctl-154-symlink-revert`, `ctl-opencode-read-layers`. New **SC31** asserts derivation-vs-manifest agreement via `redcheck.sh verify-manifest`. | `main-session` | `resolved` |
| C3 | high | **6.6 now depends on every epic leaf** (26 predecessors) and **6.8 on 6.1, 6.2, 6.3, 6.4, 6.7, 6.7a**. Re-measured: ancestors of 6.8 went **24/48 → 56/56, zero escapees**, graph still acyclic. New risk **R12** records the hazard. | `main-session` | `resolved` |
| C4 | high | #119 retyped `partial` → `include` (EXP-005 sanctions the close, gated on 4.7). **#154 is CLOSED upstream** — so `partial` would have been wrong in the other direction; retyped `deferred`, and 6.4 files a **successor** rather than reopening. Added plan-054's own `tracker` row. #231/#124 wiring was already fixed at conformance. | `main-session` | `resolved` |
| C5 | high | Added **SC7b** asserting 3.3's *positive* (the edge now appears), keeping SC7 as the overreach guard. **3.3 added to the RED gate's `Blocks`.** Both criteria now run the same `ctl-226` fixture with and without `--positive`. | `main-session` | `resolved` |
| C6 | high | **`1.3 depends-on: 1.2`** — the fleet-wide emit can no longer land before the resolver unit tests. | `main-session` | `resolved` |
| C7 | high | Added **6.6a**: deploy with `./target/debug/yf harness skills install` (debug reads `skills/` from disk, so it does not violate AGENTS.md's ban on release `yf self install` mid-execution). 6.7 now depends on 6.6a and must record which tree each harness read. New **SC35**. | `main-session` | `resolved` |
| C8 | high | **D-1 amended explicitly** rather than certified — `yf skill-dir` stands, but the `find` fallback is replaced by a pure-bash existence loop, because `find`'s exit code is unusable. Added **SC4b** (the yf-absent path resolves the same directory), a third arm to 1.6 running with `yf` off `PATH`, and risk **R11** for version skew. | `main-session` | `resolved` |
| C9 | med | `5.9 depends-on 6.5` was already corrected at conformance; **5.9 added to 6.6's predecessors**, so the web version bump now passes validation before the site auto-publishes. | `main-session` | `resolved` |
| C10 | med | **#229 un-deferred into 0.6** (`resolves-upstream: #229 (include)`) — the plan's own gate depends on that harness. **0.8 bans `grep -qv` as a criterion primitive**, citing the measurement. #232's remedy is delivered in substance by 0.9/SC30 without taking the issue into scope. | `main-session` | `resolved` |
| C11 | med | 1.3's description now records that `EmittedRegionAsset.emit` is **zero-arg**, so a parameterized emitter is required, and that **three of the 19 are prose ABOUT the idiom** and must be emitted in placeholder form. | `main-session` | `resolved` |
| C12 | med | The live-regression gate is now **`Type: human`** with `Approvers: operator`, and its Condition states that an INCONCLUSIVE **blocks**. A gate that tolerates its own failure is not a gate. | `main-session` | `resolved` |
| C13 | med | New issues **1.7** (prefer the harness-provided base directory — EXP-002's fix for the cross-tree skew) and **1.8** (`allowed-tools` remediation across 10 files). 2.4 retargeted to `profile.rs`/`audit.rs`/`doctor/checks.rs` and explicitly NOT `drift.rs`. 4.2 gains a Deprecations section. 6.4 absorbs the amendment-log fragmentation and the `KeptModified` whitespace defect. New **6.7a** writes the release notes. New SC32–SC34, SC36. | `main-session` | `resolved` |
| C14 | med | SC1 amended to state that a `(testable)` REQ and its tagged test must land together, since `coverage.rs` fails the build otherwise. | `main-session` | `resolved` |
| C15 | med | Motivation corrected from **11 `SKILL.md` files** to **19 files**, itemised by group. | `main-session` | `resolved` |
| C16 | med | Added **6.5a** (merge the execute branch to `main`), 6.6 depends on it, and 6.5 now refreshes **`Cargo.lock`** for cargo-dist's version check. New **SC37**. | `main-session` | `resolved` |
| C17 | med | SC12 no longer demands exactly ten themes — it asserts that every theme cites its plans and that each of the 28 plans is covered by exactly one theme, which is the property that actually matters. | `main-session` | `resolved` |
| C18 | low | SC14 scoped to `*.formula.toml` **under `skills/`**, excluding the staged copies in `.beads/formulas/`. | `main-session` | `resolved` |
| C19 | low | Removed the spurious `depends-on: 0.1` from the pure-documentation issues (4.5, 4.8, 5.3, 5.4, 5.5); they no longer serialise behind the RED baseline. | `main-session` | `resolved` |
| C20 | low | **`1.6 depends-on: 1.3, 1.5`** — the isolated-HOME test now covers the hardcoded-path sites too. | `main-session` | `resolved` |
| C21 | low | Accepted as a scope note rather than a split: 4.2 and 4.3 stay single issues, but 4.1 (the scaffolder) de-risks 4.2, and EXP-004 measured the reconstruction spine as 28/28 available. Flagged for the operator at approval. | `main-session` | `resolved` |
| C22 | low | Folded into 6.4's filing list. | `main-session` | `resolved` |

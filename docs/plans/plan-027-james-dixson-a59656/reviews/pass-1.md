# Red-Team Review — Pass 1

**Plan:** plan-027-james-dixson-a59656
**Date:** 2026-07-11

## Verdict: REVISE

Core design (preflight *owns* staging → the silent-omission bug becomes structurally impossible) is
the right call and well-supported. Two HIGH concerns (FormulaCheck extraction precision; orphan-GC
data-loss boundary) and several medium/low tightenings must land before approval. Findings are
sufficient — fixes are spec/scoping tightenings, not new investigation.

## Strengths
- Own-staging over validate-only correctly reasoned (exp-003 lifecycle-ownership reframing).
- The preflight seam exists: `run_with_env` (preflight.rs:259) is a real pipeline; `ensure_scaffold`
  (:965) is genuine precedent for a sanctioned idempotent write.
- Timing holds: `yf preflight <skill>` stages that skill's formulas at entry; later pours resolve
  them same-session — *given the running binary embeds the staging logic* (Concern 5).
- Embedded read path real (embed.rs); "embedded == both scopes" rests on verified byte-identical
  deploy (common.rs:100) — an explicitly-scoped decision, not a silent drop.
- SPEC-first ordering correct (Epic 1 REQs + amendment log precede code; deps enforce it).

## Concerns
| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| H1 | high | FormulaCheck's "exact greppable contract" is NOT clean: most `bd mol pour`/`wisp <name>` matches in the corpus are prose/templates (`yf-beads-authoring:89,94,402`, `yf-beads-extra:232`, `yf-plan:53,520,658`). A naive grep would FAIL yf-beads-authoring/yf-beads-extra, contradicting the "passes the three-formula fleet" criterion. | Specify extraction precisely (Epic 1.2 REQ + 3.1): concrete formula tokens inside **runnable bash fences** only; exclude placeholder tokens (`<name>`,`<formula>`) and prose. Add a fleet-wide test asserting the prose-pour skills PASS. |
| H2 | high | Orphan-GC data-loss: `.beads/formulas/` is bd's shared proto namespace, not yf-owned. "Unclaimed by embedded" deletes ANY third-party/local formula. Worse, `doctor --repair` short-circuits to `beads_init::repair` (mod.rs:34-37), so a wedged-DB repair would trigger formula GC as a side effect → silent third-party deletion. | Make GC **provenance-tracked** — remove only files yf itself staged (yf-owned marker/manifest of staged basenames), never the raw "unclaimed" set. Decouple GC from the beads-init `--repair` path / gate behind its own explicit affordance. |
| M3 | med | FormulaCheck (registry `checks()`, read-only, embedded-scoped) and GC (cwd `.beads/formulas/`) live in DIFFERENT code paths: `args.repair` returns before `checks()` is built (mod.rs:34-37); `run_repair` is cwd-scoped. Epic 3 bundles them as adjacent registry edits — they are not. | Split Epic 3: FormulaCheck→`checks()`; GC→`run_repair`. Specify whether/how the read-only path surfaces the orphan report (it has no repo handle today). |
| M4 | med | Source-hash-only idempotency re-introduces the bug: a destination deleted after caching (manual, or the new GC) won't re-copy if source unchanged → `proto not found`. 2.2 has no destination-deleted test. | Verify **destination existence every run** (unconditional tiny copy cheapest/safest), not source-hash alone; add the destination-deleted-but-cached re-stage test. |
| M5 | med | Cutover atomicity: migrated SKILL.md (4.1 removes cp/rm) is only correct once the **binary** shipping Epic 2 staging is live. If 4.3 refreshes skill copies but a stale binary is on PATH → broken window. | Make 4.3 explicit: rebuild+install the new `yf` binary AND migrated skills; gate on `yf --version` reflecting the new build before declaring migration done. |
| M6 | med | 5.1→4.1 not dependency-enforced: 4.1 (remove interim staging) depends only on 2.1, not 5.1 (commit interim). If 4.1 runs first, 5.1 has nothing to commit — the honest two-commit story collapses. | Add `4.1 depends-on 5.1`. |
| L7 | low | Gitignore anchor target unspecified. `.beads/.gitignore` is bd-managed and warns against edits; the safe target is the **root** `.gitignore`. | State the anchor is `/.beads/formulas/` in the **root** `.gitignore`, reusing the `ensure_scaffold` path. |

## Missing
- Precise FormulaCheck extraction spec (runnable-fence + concrete-name; exclude placeholders/prose).
- GC provenance mechanism (how yf distinguishes its stale artifact from a foreign formula).
- Destination-existence re-stage semantics + test.
- Explicit binary-rebuild+install + version check in the cutover (4.3).
- `context.md` skeleton unfilled for a kernel-changing plan; the distribution/cutover assumption
  (operators must run the new binary) is undocumented.

## Gate Assessment
Gates reasonable and correctly placed. Start + Capability (Rust toolchain, `cargo test`) validly
block Epics 2/3. Gap: no check verifies the installed binary embeds staging before Epic 4 removes
cp/rm (Concern M5) — fold a `yf --version` verification into 4.3.

## Upstream Assessment
Consistent with AGENTS.md coarse convention: one tracking issue at intake, no granular sub-beads.
No pre-existing upstream to reconcile. Correct as stated.

## Operator Resolutions
| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| H1 (extraction false-positives) | Epic 1.2 REQ + 3.1 now specify runnable-bash-fence + concrete-token extraction, excluding `<name>`/`<formula>` placeholders and prose; success criterion + 3.3 test add fleet-pass for yf-beads-authoring/yf-beads-extra. | resolved |
| H2 (GC data-loss) | Decision 5 + Epic 3.2 now require provenance-tracked GC via a yf-owned staged-manifest marker; GC removes only yf-staged-now-orphaned files, decoupled from beads-init `--repair`. Risk table updated. | resolved |
| M3 (split code paths) | Epic 3 split: 3.1 FormulaCheck→checks(); 3.2 GC→run_repair (cwd-scoped); read-only path reports orphans only where a repo handle exists. | resolved |
| M4 (dest-deleted idempotency) | Epic 2.1 verifies destination existence every run; 2.2 adds destination-deleted-but-cached re-stage test. | resolved |
| M5 (cutover atomicity) | Epic 4.3 now rebuilds+installs the new binary and gates on `yf --version`; distribution assumption documented in context.md. | resolved |
| M6 (5.1→4.1 ordering) | Added `4.1 depends-on 5.1`. | resolved |
| L7 (gitignore target) | Epic 2.1 pins the anchor to `/.beads/formulas/` in the ROOT `.gitignore` via the ensure_scaffold path. | resolved |
| Missing: context.md | Filled project environment, runtime assumptions, and the binary-distribution/cutover assumption. | resolved |

---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-042-james-dixson-98631b
created: '2026-08-17'
verdict: REVISE
status: resolved
---

# Review pass 1 — adversarial (red-team)

## Verdict: REVISE

4 high, 6 medium, 2 low, 3 missing. Conformance passed first (one blocking gap — a Capability
Gate deadlock — fixed before this pass).

## Premise verification — all five checked against source, all CONFIRMED

| Claim | Verdict |
| :-- | :-- |
| `upgrade` is single-destination | **confirmed** — `status.rs:69-96` |
| `upgrade` writes the aggregate to a skills-sibling dir, unmanaged by the tune manifest | **confirmed**; contradicts `REQ-YF-FLOW-007` verbatim |
| `install --tune --json` w/o `--harness` → `confirmation_required`, exits 0 | **confirmed, with a correction** — skill **bodies are written** first; it is rules+config that are skipped |
| `--yes` already means fan-out bypass | **confirmed** — `install.rs:270`, pinned by an existing test |
| claude-code profile sets `bypassPermissions`, **creating** the file | **confirmed** — `profiles/claude-code.json:10-13,49-52`; `settings.rs:141,173-179` |

> *"Premise work is solid — E5 is accurate and the plan reads it correctly. The problems are
> downstream of the premises."*

## Strengths (verbatim)

- **Genuinely evidence-led** — every load-bearing decision traces to a measured result the
  reviewer reproduced in source.
- **SPEC-first is real here** — `REQ-YF-SELF-005` and `REQ-YF-TUNE-023` both literally forbid
  the deliverable; Epic 0 correctly gates all code.
- **D-N is a genuine catch** — the `--yes` collision would have been discovered at implementation.
- **D-F's refusal to loophole-lawyer `REQ-YF-TUNE-023` is correct** — passing `--harness`
  explicitly after auto-detecting is the prohibited outcome by another name.
- **Gate reachability is clean**, and the plan documents fixing an earlier deadlock.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C1 | **The Epic 2 / Epic 3 seam does not exist in the code.** `tune_one_harness_at` unconditionally runs **both** `compute_config_subop` and `compute_rules_subop`; there is no `--rules-only`, no `config_only` flag, no such field (grep: none). So "safe half = skills + rules" is **unreachable by any existing verb**: bare `install` is skills-only by REQ, and anything deploying rules deploys config with it. Issues 1.3 and 2.2 are not gated on Epic 3. **Epic 2 as written ships an unconsented `bypassPermissions` write.** R5 is therefore **false and its severity inverted**. | **high** |
| C2 | **The Capability Gate blocks the wrong issues.** Its Instructions say nothing that *ships* the auto-tune path may land — but it blocks 3.3 (CI suppression) and 4.1 (docs), while **1.3 and 2.2 actually ship it** and are unblocked. | **high** |
| C3 | **The gate's test passes vacuously.** Verified: `cargo test -p yf consent_gate` → `running 0 tests … 0 passed; 4 filtered out`, **exit 0**. A name filter matching nothing is a pass. *"This is precisely the exit-0-means-nothing shape R1 exists to defend against, reproduced inside the gate guarding the plan's most dangerous edge."* | **high** |
| C4 | **D-C1's `permissions.*` predicate is claude-code-specific and silently lets the other two harnesses through.** codex uses `approval_policy = "never"`; opencode uses `permission.*` (singular) `= "allow"`. Neither matches `permissions.*`. On a machine with an existing codex/opencode config, the gate's "file exists AND no `permissions.*` key" branch is satisfied and yf **auto-applies a blanket-allow / never-approve autonomy lever with no consent**. Four of R2's five defenses key on a predicate that does not select those cases. | **high** |
| C5 | **D-O's home-dir check silently regresses `~/.agents`.** `harness_detect::PROBES` has four rows and **no `agents` row**. The incumbent `present_user_surfaces` probes `~/.agents/{skills,rules}` — so a machine with `~/.agents/skills` and no `~/.codex` **stops being refreshed**. Separately the new check is *broader* on another axis: `present_user_surfaces` means "yf already deployed here", while `~/.claude` exists on every Claude Code machine — so the sync would begin writing into `~/.claude` where yf was never installed. D-O compares itself only to `effective_harnesses`, never to the incumbent it replaces. | medium |
| C6 | **D-M covers `confirmation_required` but not `refused`.** `tune_bridge_at` sets `status: "refused"` on the malformed-settings fail-safe path, which **also returns `Ok(())`** — a second exit-0 false success, unnamed by D-M, REQ 0.4, or R1. | medium |
| C7 | **Issue 3.4 names machinery that does not produce a delta.** `plan_targets`/`target_plan_json` emit `{harness, config_path, rules_path}` — the blast radius, not the change set. The per-key delta lives in `config_json`'s `changes` array over `merge::Change`. As written 3.4 would surface file paths and call it a delta. | medium |
| C8 | **Issue 2.2 drops half of `REQ-YF-SELF-005`'s fail-soft contract.** The SPEC already resolves the fail-soft question correctly — *"exiting non-zero on the refresh alone, never rolling back the swap."* Issue 2.2 says only "never invalidates a successful promote", omitting the non-zero exit. **Implemented literally it recreates the silent-divergence defect the plan exists to fix.** No success criterion covers the exit code. | medium |
| C9 | **D-H is unimplementable as written.** It promises "skills and rules still deploy" under CI, but E5's own sequence says the CI path drops `--tune` and runs bare `install` — which by `REQ-YF-INSTALL-008` deploys **no rules**. Same root cause as C1. | medium |
| C10 | **Scope: the split produced a child larger than the parent.** plan-041 was split for creep at 19 issues; this has **22**, four epics, five SPEC amendments, a new consent surface, a new flag, a new presence predicate, and `--prune`. Given C1, the "two independently shippable halves" framing that justifies the size does not hold. | medium |
| C11 | **R1's wording overstates the trap** — skill *bodies* are deployed; rules and config are not. D-M states this accurately; R1 does not. | low |
| C12 | **Minor precision:** pi and `agents` ship **no config profile** (3 files, and `pi_has_no_config_profile`), so the config half is a no-op for 2 of 5 harnesses. `read_settings` classifies a whitespace-only file as `Absent`, so the gate must key on the read classification, not `path.exists()`. Success criterion 2's `rg "fn refresh_user_skills"` returns **zero** if 1.1's extraction renames the function. | low |

## Missing

- **No risk for "the sync writes to a surface the operator never yf-installed"** (C5's broadening).
- **No rollback / recovery story.** `tune --revert` exists, but #154 means revert *deletes* the
  aggregate rather than restoring it — so "just revert" is not currently a safe answer, and the
  **config** revert path is unexamined.
- **No issue covers the `agents` harness id**, despite SC3 and D-O implying five-harness coverage.

## Gate Assessment

Start and Reconcile gates fine. **Capability Gate: reachable but ineffective** — C2 (blocks the
issues that *advertise* the path, not the two that *ship* it) and C3 (verified vacuous pass).
The deadlock-avoidance reasoning in its Instructions is correct and worth keeping; the `Blocks`
set and the test predicate both need repair before it means anything.

## Upstream Assessment

Dispositions reasonable. #154's `exclude` is well-argued. The `_to file_` tracker matches the
convention and Phase 4.5 timing. **One gap:** Issue 4.3 files the `--surface` blindness, but
nothing files **C5's regression risk** or the **`upgrade`-writes-unmanaged-rules** defect — the
latter survives this plan untouched, since the sync merely stops calling `upgrade` rather than
fixing it. Worth one more `exclude`-dispositioned issue so the orphan-aggregate defect is
recorded rather than routed around.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | Epic 2/3 seam does not exist | high | Accepted — **operator decision: build a rules-only tune mode** (D-Q). New Issue 2.1 implements `--rules-only` / `config: false`; Issue 0.3 carries its REQ; Issue 1.3's exec uses it until Epic 3 lands, so it cannot ship an unconsented config write. R5 rewritten, with its pass-1 falsity recorded in the row itself. | resolved |
| C2 | Gate blocks the wrong issues | high | Accepted. Gate now `Blocks: Issue 2.2, Issue 3.3, Issue 4.1` — 2.2 is the issue that actually *ships* the sync. 1.3 is deliberately unblocked because D-Q makes it emit `--rules-only`. | resolved |
| C3 | Gate test passes vacuously | high | Accepted, and reproduced: `cargo test -p yf consent_gate` → `0 passed; 4 filtered out`, **exit 0**. The gate's Test now proves the filter **non-empty first** (`--list` piped to a `grep -c` of test lines, asserted ≥ 3) before running it. | resolved |
| C4 | Consent predicate is claude-code-only | high | Accepted — **operator decision: profile-declared consent** (D-R, superseding D-C1's predicate). `consent_required: true` on the offending profile entries; the gate tests the computed change set against it. Verified independently: the profiles' own rationale text calls `approval_policy: "never"` and `permission.*: "allow"` *"the analog of claude-code's bypassPermissions"* — the codebase already knew they were the same class, and the `permissions.*` prefix caught one of three. | resolved |
| C5 | D-O regresses `~/.agents`, broadens `~/.claude` | medium | Accepted. Issue 1.2 must define the predicate for all five ids and ship tests for **both** hazards — the `~/.agents`-with-no-`~/.codex` regression, and the `~/.claude`-exists-everywhere over-broadening. Added as risk **R8**; SC3 extended. | resolved |
| C6 | D-M misses `refused` | medium | Accepted. D-M widened to *any* `tune.status` other than `ok`; Issue 1.3 gains the `refused` test case. | resolved |
| C7 | 3.4 names the wrong machinery | medium | Accepted. Issue 3.4 repointed at `config_json`'s `changes` array over `merge::Change`, with the required dry-run-before-real two-phase shape stated. | resolved |
| C8 | 2.2 drops the non-zero-exit clause | medium | Accepted — the sharpest catch on fail-soft. Issue 2.2 now restates `REQ-YF-SELF-005`'s full contract: **exiting non-zero on the sync alone**, never rolling back the swap. Added as success criterion 8. *Fail-soft ≠ silent.* | resolved |
| C9 | D-H unimplementable as written | medium | Resolved by D-Q — the rules-only mode is what makes "skills and rules still deploy under CI" implementable. | resolved |
| C10 | Scope larger than the parent it split from | medium | Accepted — **operator decision: split off `--prune`.** Filed as **#155**. Issue numbers 0.3 and 2.1 are **reused** for the D-Q rules-only work rather than left as gaps, so the `1.3 → 2.1` edge survives intact. | resolved |
| C11 | R1 overstates the trap | low | Accepted. R1 now says the sync deploys no **rules or config** — skill bodies *are* written first. | resolved |
| C12 | Precision items | low | Accepted, all three: pi/`agents` no-config-profile noted (SC5a); the gate keys on `read_settings`'s classification not `path.exists()` (whitespace-only reads as `Absent`); SC2 no longer pins a function name that a correct refactor would rename. | resolved |
| M-A | No risk for writing to never-installed surfaces | medium | Accepted — added as risk **R8**, and explicitly marked unmitigated until Issue 1.2 ships its test. | resolved |
| M-B | No rollback/recovery story | medium | Accepted — added as risk **R9**. Because #154 makes `tune --revert` *delete* the aggregate rather than restore it, the consent gate is the **primary** control rather than a backstop; that is now part of why the Capability Gate blocks the shipping issue. The config revert path is manifest-driven and sound; only the aggregate's is not. | resolved |
| M-C | No issue covers the `agents` harness id | low | Accepted — SC3 now pins the `agents` id explicitly. | resolved |
| U-A | Orphan-aggregate defect not filed | low | Accepted — filed as **#156** and added to the Upstream Issues table as `exclude`. Routing around a defect is not fixing it: `upgrade` stays a public verb that will keep producing unmanaged orphans. | resolved |

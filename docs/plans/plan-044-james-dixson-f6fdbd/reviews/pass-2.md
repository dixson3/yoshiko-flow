---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
verdict: REVISE
status: resolved
---

# Red-Team Pass 2 — plan-044-james-dixson-f6fdbd

**Date:** 2026-08-17
## Verdict: REVISE
**Status:** all 8 concerns resolved — plan revised, red-team pass 3 required (REQ-PLAN-030)

## Strengths

- **13 of 14 pass-1 concerns verified substantively resolved**, not cosmetically. D-7's
  same-commit invariant (`plan.md:150`) is *carried* by every tagging issue (1.3, 2.1, 2.6, 2.9,
  2.10) — four red windows closed — and correctly scoped: only macro-`SPEC.md` REQs need
  allowlist rows, since `coverage.rs` never scans the per-skill namespaces. D-9 now *admits*
  conservative-keep is hand-edit tolerance rather than denying it. Issue 1.6 owns the #160 probe
  with a criterion forcing a written outcome. Issue 1.7 carries all five sites. Counts recount
  exactly (5 epics / 38 issues); `SPEC.md:856-859` verified correct.
- **Dependency graph sound after the renumber** — every `depends-on` resolves, no cycles. The
  concern-10 re-pointing landed exactly (`2.8 ← 2.4`, `3.4 ← 3.2`).
- **Issue 3.2's non-raising `run()` variant is safe — verified, not assumed.** `cmd_land`
  (`upstream.py:933`) and `cmd_hoist` (`:1008`) never reach the resolver; the only `closable`
  call site is the dispatch at `:1315`. A resolver-scoped `check=False` cannot reach
  `push`/`hoist`/`land`.
- **The ignore-list extension cannot mask a dropped-file regression for any tracked file** —
  `git ls-files` confirms `topology.txt` and `.scratch/sandbox.env` are untracked runtime residue
  while `README.md`/`bootstrap.sh`/`smoke.sh` remain hash-covered.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | **high** | **D-11 pins `agents` to `~/.agents/rules` with zero evidence anything loads it — and the plan's own finding says the opposite.** exp-001 correction 1: *"upgrade writes a 24469 B aggregate into a `rules/` dir that **no non-claude harness loads**."* `agents` is non-claude. If that holds, the regression D-11 prevents is a no-op and D-11 instead commits `tune` to writing an unread file forever. `SPEC.md:1251-1254` has a **named precedent against exactly this**: pi's rule target "shall NOT be a compiled-in guess … gated by a capability gate." `AgentsMd` at `~/.agents/AGENTS.md` is at least as plausible — the four other AGENTS.md harnesses all use `AgentsMd`. | Give Issue 2.2 a probe sub-step shaped like Issue 1.6: establish what the `agents` surface actually loads *before* choosing `kind`/`surface_dir`. If nothing loads it, the honest resolution to pass-1 concern 7 is "declare `agents` skills-only" plus reconciling `preflight.rs:213-217`. The SPEC amendment must carry evidence, per the TUNE-020 precedent. |
| 2 | **high** | **The 14-bundle gate's Test cannot run as written.** `git check-ignore -v .beads/issues.jsonl` → `.git/info/exclude:9:.beads/`; `git ls-files .beads` is empty. A `git clone` produces **no `.beads/`**, so `_resume_scan` → `_bd_list("--all")` returns nothing and every bundle reports `total: 0` — the gate's Test asserts the exact failure signature the plan is fixing and can never pass. | Replace "scratch clone" with an in-place trial apply on a scratch branch, recovered by `git checkout -- docs/plans/`. (A `cp -r` is worse — it copies `dolt-server.{pid,port,lock}` and a live server handle.) State the recovery command in Instructions. |
| 3 | medium | **The 14-bundle gate is a reachability cycle as declared.** Condition = "3.7's one-shot **has been run** in `--dry-run`"; Blocks = "3.7's apply step". The one-shot is built *inside* 3.7, and a gate blocks a bead, not a sub-step. | Split into **3.7a** (build; `--dry-run`; emit the mapping) and **3.7b** (apply + postcondition); re-point `Blocks: 3.7b` and `3.8 depends-on 3.7b`. |
| 4 | medium | **Issue 2.2 will turn the tree red.** `doc_agreement.rs:169-184` iterates `RULE_TARGETS` and requires each derived subpath verbatim in `web/content/pages/harness-tune.md`; `tune_matrix_agrees_with_profiles_and_rule_targets` (`:246`) fails on divergence. `.agents/rules` is absent from that doc. Issue 2.2 names only `managed_block.rs`. (`harness-tune.md:44` already claims agents "receive[s] skills and rules" — pre-existing drift the one-directional checker never caught.) | Add the `harness-tune.md` edit to Issue 2.2's deliverable, and correct lines 44/53 to match whatever D-11 resolves to. |
| 5 | medium | **D-10's "No orphaned sections" is false for the four non-claude harnesses.** `skills remove` (`status.rs:165`) writes the **skills-sibling** `rules/` (`dest.rs:59`) — the same wrong surface #156 deletes upgrade's write to. `tune`'s managed surface for those harnesses is `~/.codex/AGENTS.md` etc. So `remove` prunes from a file nothing reads while the section in the real surface survives, and FLOW-002 prunes on the embedded set so a later `tune` retains it. Criterion 5 is satisfiable while the defect is live. | Scope D-10 and criterion 5 to claude-code explicitly, and either extend Issue 2.1 to make `remove` drop from the tune-managed surface, or record the gap and file it as a second follow-on in 4.3. |
| 6 | medium | **Issue 2.10's ignore-list omits a fourth surface — `embed.rs` — so the residue stays baked into the binary and shipped.** `embed.rs:48-50` excludes only `*.pyc`/`__pycache__`. A release built on a machine where `bootstrap.sh` has run embeds `topology.txt` **and `.scratch/sandbox.env` — a developer's sandbox env file** — and `deploy_skill` writes them to every user's skills dir. Adding globs to the three named surfaces makes doctor green while leaving the shipping defect intact. | Make Issue 2.10 four surfaces, adding the same globs as `#[exclude]` in `embed.rs`. Self-consistent: an unembedded residue file becomes an "extra deployed file", which the ignore-list then spares from prune. |
| 7 | medium | **Issue 4.1's `depends-on` omits four epic leaves.** `1.5, 1.7` (#160), `2.5–2.7` (#154) and `3.5, 3.6` (#144) are not ancestors of 4.1 — 1.8 hangs off 1.2, 2.11 off the 2.8 branch, 3.9 off the 3.7 branch. So close-out can run with three upstream issues open. Worse, 4.3 run before 2.6 lands sees `REQ-YF-TUNE-029`'s row present-and-untagged and passes — a **false green on the exact invariant 4.3 certifies**. | `4.1 depends-on 1.5, 1.7, 1.8, 2.7, 2.11, 3.6, 3.9`. |
| 8 | low | Adding an `agents` `RULE_TARGETS` row silently flips `tune --harness agents`'s config verdict from `Refused{unknown-harness}` to `Deferred` (`mod.rs:325`). Probably desirable, but undeclared; `harness-tune.md:44-53` describes agents as "no config profile". | Name the outcome change in Issue 2.2 and align the doc row. |

## Missing

- Evidence for what the `agents` surface loads — the plan asserts a target rather than measuring
  one, in a repo whose SPEC has a named precedent for refusing that.
- A `web/content/pages/harness-tune.md` edit anywhere in Epic 2, despite Issue 2.2 mutating the
  exact table REQ-YF-TUNE-025 pins to it.
- `embed.rs` from Issue 2.10's surface list.
- A runnable instrument for the 14-bundle gate's Test.

## Gate Assessment

- **Start Gate** — appropriate.
- **Capability Gate: sandboxed-HOME cross-harness proof — now correct and non-vacuous.** Narrowing
  to the three descriptors `harness_cross_e2e.rs:111` actually iterates is verified accurate
  (`surfaces()` `:69-92` panics on `"agents"`). The note that extending to five is Issue 2.4's
  deliverable rather than the gate's precondition is exactly right.
- **Capability Gate: 14-bundle repair dry-run** — right instrument, correctly placed in principle,
  but its **Test is unrunnable** (concern 2) and its **Blocks target is a cycle** (concern 3).
  Both mechanical.
- **Reconcile Gate** — standard. Note it is currently the *only* thing preventing the premature
  close-out in concern 7, which makes Issue 4.1's declared dependencies decorative.

## Upstream Assessment

Dispositions filled for all 10 issues, each traceable to a finding — pass-1 concern 13's triage
gap is fully cleared. #143's note records both the 5→14 re-scope and the real defect shape;
#158's supersede note enumerates the four verified conditions and gates the close on a green
`cargo test -p yf sync` rather than on source reading; #160's note explicitly says the plan probes
the `repair()` ordering "rather than closing on detection alone". #152's rationale is consistent
across D-1, the issue table, and the triage file.

One residual: three `resolves-upstream` issues (1.7/#160, 2.7/#154, 3.6/#144) sit outside Issue
4.1's dependency closure — concern 7. The dispositions are right; the graph does not enforce them.

## Operator Resolutions

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| 1 | D-11 `agents` target unevidenced | **Accepted — operator reversed D-11 to probe-first.** Issue 2.2 now measures what the `agents` surface actually loads and records it in `findings/`, then either adds a `RULE_TARGETS` row carrying that evidence or declares `agents` skills-only and drops `~/.agents/rules` from `preflight.rs:213-217`. Issue 0.1's REQ-YF-TUNE-020 amendment is conditional on the probe. Criterion 5 reworded to 'resolved by evidence'. | resolved |
| 2 | 14-bundle gate Test unrunnable | **Accepted.** Gate Test changed to an **in-place trial apply on a scratch branch**, recovered by `git checkout -- docs/plans/`. Instructions now state why a scratch clone cannot work (`.beads/` git-excluded, `total: 0` for every bundle) and why `cp -r` is worse (copies `dolt-server.{pid,port,lock}` and a live server handle). | resolved |
| 3 | 14-bundle gate reachability cycle | **Accepted.** Issue 3.7 split into two **real issues**: 3.7a (build + `--dry-run` + emit mapping) and 3.7b (apply + postcondition, `depends-on: 3.7a`). Gate re-pointed to `Blocks: 3.7b`, Condition keys on 3.7a's output. `3.8 depends-on 3.7b`. Sub-bullets were rejected as a fix — a gate blocks a bead, not a bullet. | resolved |
| 4 | Issue 2.2 breaks doc_agreement | **Accepted.** Issue 2.2 now carries the `web/content/pages/harness-tune.md` edit explicitly, citing `doc_agreement.rs:169-184` and `tune_matrix_agrees_with_profiles_and_rule_targets` (`:246`), and corrects the pre-existing drift at `harness-tune.md:44,53` in the same pass. | resolved |
| 5 | D-10 orphan false for 4 of 5 harnesses | **Accepted — operator decision:** D-10 scoped to claude-code explicitly ('effective on claude-code only'), with the `dest.rs:59` skills-sibling vs tune-managed-surface divergence stated in the decision row. Criterion 5 corrected to claim only what is true. The non-claude residual is filed as a second follow-on in Issue 4.3 alongside D-12. | resolved |
| 6 | Ignore-list omits `embed.rs` | **Accepted.** Issue 2.10 now names **four** surfaces including `embed.rs`'s `#[exclude]` list, with the shipping defect spelled out — a release built after `bootstrap.sh` bakes `topology.txt` and a developer's `.scratch/sandbox.env` into the binary. New risk row added. | resolved |
| 7 | Issue 4.1 dependency closure | **Accepted.** `4.1 depends-on 1.5, 1.7, 1.8, 2.7, 2.11, 3.6, 3.9` — the full leaf closure, so close-out cannot run with #160/#154/#144 open and 4.3 cannot false-green on a present-but-untagged allowlist row. New risk row added. | resolved |
| 8 | `agents` config verdict change | **Accepted.** Issue 2.2 declares the `Refused{unknown-harness}` → `Deferred` verdict change (`mod.rs:325`) and aligns the doc row, rather than letting it happen silently. | resolved |

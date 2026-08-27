---
type: Reference
okf_spec: OKF-PLAN
id: deferred-defects
description: Defects plan-054 DISCOVERED but did not fix, each filed upstream with its measurement (Issue 6.4 / SC20)
---

# Deferred defects

Every defect this plan found and deliberately did **not** fix. Each row carries the upstream
issue it was filed as **and the measurement behind it** — a deferral with no measurement is
indistinguishable from a guess, and it is the measurement that lets the next reader decide
whether the deferral still holds.

| # | Defect | Filed | Measurement |
| :-- | :-- | :-- | :-- |
| D1 | `yf` ignores `XDG_CONFIG_HOME` / `CODEX_HOME` / `OPENCODE_CONFIG_DIR` when resolving harness directories, so an operator who relocated a harness config gets writes to a path that harness does not read — and the install reports success | [#238](https://github.com/dixson3/yoshiko-flow/issues/238) | Measured **zero occurrences** of all three variables anywhere under `yf/src/cmd/harness/` or `yf/src/dest.rs` on the v0.5.0 tree |
| D2 | pi's project-trust gate is unexercised by any test or smoke; the live regression runs in a directory pi already trusts, so the first-run-in-a-fresh-clone path — the one a new user hits — is unmeasured | [#239](https://github.com/dixson3/yoshiko-flow/issues/239) | Observed while authoring the Issue 2.5 headless smoke: no test, smoke or documented procedure covers the untrusted-project case |
| D3 | The codex block-size budget models **one** `AGENTS.md`, but codex concatenates several against the same `project_doc_max_bytes` cap, so the check can report "under the cap" while the effective document is over it and codex silently truncates | [#240](https://github.com/dixson3/yoshiko-flow/issues/240) | **Measured:** `CodexBudgetCheck` reads exactly one path (`agents_path`, resolved from the codex rule target at user scope); `REQ-YF-TUNE-027` records the single-file scope as a chosen limitation |
| D4 | Two plans amended root `SPEC.md` with no amendment-log bullet, and the log is fragmented across five blockquote regions and is non-chronological | [#241](https://github.com/dixson3/yoshiko-flow/issues/241) | **Measured** by EXP-004, which set out to use the log as the changelog spine and could not: it **misses 9 of the 28** plans in the v0.4.0..v0.5.0 window. The `index.md` summary line had **28/28** coverage and was used instead |
| D5 | `RevertOutcome::KeptModified`'s reason string carries a run of ~30 spaces mid-sentence, from a wrapped Rust literal that was never joined — on the conservative-keep path, which is the highest-stakes string in the module | [#242](https://github.com/dixson3/yoshiko-flow/issues/242) | Observed at `yf/src/cmd/harness/revert.rs`: `"…kept, not                              deleted; remove it yourself…"` |
| D6 | **Successor to the closed #154.** `yf harness tune` overwrites a pre-existing rules aggregate `yf` did not author, with **no backup** — so `--revert` has nothing to restore from, by construction. The loss happens at **tune**, not at revert | [#243](https://github.com/dixson3/yoshiko-flow/issues/243) | **Measured** by EXP-006: six sandbox spikes under a fake `HOME`, incl. a high-fidelity replica using the real `AGENTS.md` files with every path rewritten to the sandbox. The revert half is genuinely fixed (the `REQ-YF-TUNE-029` sha guard fires); this is the adjacent half it cannot reach |

## Not deferred — fixed in this plan

Recorded so a reader does not have to diff the plan to learn which discovered defects were
closed rather than filed: the `SKILL_DIR` resolution gap across pi/opencode (Epic 1), the 32
hardcoded `.claude/skills/…` invocations and two further pre-`yf-` skill names found by the
sweep (Issue 1.5), the `allowed-tools` portability decision (Issue 1.8, `REQ-YF-EMBED-006`),
`#154`'s **symlink-revert** half (Issue 2.2), and all five instruments named in `#203`
(Issue 3.6).

## Cross-links

`#243` is cross-linked from `#154` with an explicit statement that it is a **successor, not a
reopen** — `#154`'s own remedy works, and re-opening a correctly-closed issue would misreport
that.

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

## Found by the 52-edge drift sweep (Issue 6.6)

The full sweep at `dd9adc2` returned **PASS 38 / FAIL 11 / CONFLICT 3 / INCONCLUSIVE 0**. Four
failures were plan-054's own and were **fixed** (see below); the rest are pre-existing and filed
here.

| # | Defect | Filed | Measurement |
| :-- | :-- | :-- | :-- |
| D7 | README-contract edges fail 16 of 19 skills, and the manifest's `field-set-equal` contract is **stronger than anything that enforces it** — so it needs a decision, not just edits | [#244](https://github.com/dixson3/yoshiko-flow/issues/244) | **Measured** by the sweep: `SPEC.md` absent from 10 layout fences; 5 fences carry a stale unprefixed root; the repo's only enforcement (`test_cli_enumeration.py:223-249`) is deliberately **directory-level**, not file-by-file |
| D8 | Two authored web skill pages contradict their skills; `yf-beads-upstream.md` is actively harmful, teaching the `bd <backend> push` path the skill's own safety invariant forbids | [#245](https://github.com/dixson3/yoshiko-flow/issues/245) | **Measured:** `yf-okf.md:3` says OKF v0.1 vs `SPEC.md:149-151` REQ-OKF-FAM-005 and `_shared/okf.py:49` (`"0.2"`); `yf-beads-upstream.md:25,50-51,62-63` vs `SKILL.md:136,170-172,657-659`. 17 of 19 pages are clean |
| D9 | Three CONFLICTs where the **fixed authority** is the stale side — reported, never rewritten, per `DRIFT-CHECK.md` §7 | [#246](https://github.com/dixson3/yoshiko-flow/issues/246) | **Measured:** `spec/data.md:331` REQ-DATA-044 ("`R*` ships at `W`, uniformly") vs `plan-relations.toml:102-115`, which ships two `E` close-out checks added by plan-052 without amending the REQ |
| D10 | Six findings **no declared edge covers** — the manifest's own diagram is 22 edges stale, and `install.sh` / `install.py` **do not exist** while 17 skill READMEs cite them | [#247](https://github.com/dixson3/yoshiko-flow/issues/247) | **Measured:** the `.d2` declares 30 edges, `DRIFT-CHECK.md` declares 52; `git ls-files` confirms no repo-root `install.sh` or `install.py`, and `DRIFT-CHECK.md` §5 itself names `install.sh` as a required source |

### Fixed rather than filed, from the same sweep

Both edges plan-054 **added** failed, and each caught a real defect of this plan's — the
strongest available evidence that they were worth adding. `e-web-formula-set` caught
`formulas.md` contradicting itself ("three" in the intro, "five" in the heading fifty lines
below); `e-web-cli-surface` caught `install.md` teaching `yf skills upgrade` as canonical.
Also fixed: three hardcoded `.claude/skills/…` paths in the **project** README (a real
functional bug for pi and opencode users), and a genuine **SPEC-first violation** — REQ-PORT-001,
REQ-STRUCT-001/-003 and REQ-BAUTH-001/-010 still pinned the six-root `find` idiom and the retired
staging bracket as testable behaviour the fleet no longer has.

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

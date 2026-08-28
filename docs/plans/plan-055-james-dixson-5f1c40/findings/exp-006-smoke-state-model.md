---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-smoke-state-model
description: check-harness-smoke.sh's current state model, per-harness consent states, and where the fix belongs
---

# EXP-006 — the harness-smoke state model (#256)

## Approach Tested

Full read of `docs/plans/plan-054-james-dixson-535968/assets/checks/check-harness-smoke.sh` plus its
siblings (`_common.sh`, `check-deployed-tree.sh`, `checks-allowlist.txt`) and the generated
`assets/harness-smoke-transcript.md`; a repo-wide grep for every reference to the script; a read of
`CHANGE-VALIDATION.md` §1/§3 against the engine `change_validation.py`; and a sandbox spike probing
each installed harness for auth/consent signals with non-interactive flags, `</dev/null` and
`timeout`. **No dialog was answered; none appeared.**

## Result

### 1. The current exit vocabulary, verbatim

```
# EXIT  0 both harnesses pass  ·  1 an assertion failed  ·  2 could not run (harness absent)
#
# AN ABSENT HARNESS IS INCONCLUSIVE, NEVER A PASS.
```

**measured.** Absence is checked **twice, inconsistently**: a pre-flight loop calls
`ck_inconclusive` → exit **2**, while inside `_smoke_one` an absent harness calls `fail` → RC=**1**
and returns 2 — a return value nothing reads. The same 0/1/2 contract is shared by the whole
plan-054 check family via `_common.sh`; `check-harness-smoke.sh` is **the one check that does not
source it**, re-implementing the helpers inline. That is how the two contradictory absent-harness
paths coexisted unnoticed.

### 2. It drives only `pi` and `opencode` — codex is never started

**measured.** `verify-all` sets `targets="pi opencode"`; `codex` is not a legal mode. So the harness
#256 is *about* is not one the smoke ever starts. Three assertions run per harness: a skill-name
grep, a rule-block presence check, and a JSON-parseability scan.

**measured.** The transcript's "resolved tree" comes from `yf skill-dir yf-plan` — **the yf binary's
opinion, not the harness's**. The committed transcript records `~/.claude/skills/yf-plan` for *both*
harnesses, which is exactly the EXP-002 failure mode, banked as a PASS.

### 3. Consent states — #256 is qualified, not refuted

**measured.** All four harnesses present (pi 0.84.3, opencode 1.18.23, codex-cli 0.150.1, claude).
In a fresh `mktemp -d` outside any trusted project, `codex exec --skip-git-repo-check` printed the
banner and `OK` — **no OAuth prompt, no directory-trust prompt, no hooks prompt** — despite
`features.hooks = true` and a live `SessionStart` hook. pi and opencode likewise needed no consent.

**inferred.** #256's three codex dialogs are **real but interactive-TUI-only**; the `exec` path does
not gate on them. Corroborated two ways: `codex exec --help` documents
`--dangerously-bypass-hook-trust` as *"…without requiring persisted hook trust **for this
invocation**"* — i.e. exec's default is skip-untrusted-silently rather than prompt — and no persisted
hook-trust record exists anywhere under `~/.codex` while exec still ran.

**So the state exists, but is not reachable on the path the smoke uses.**

### 4. Distinguishability of the four proposed states

| state | codex | pi | opencode |
| :-- | :-- | :-- | :-- |
| `absent` | `command -v` — already implemented | same | same |
| `not-authenticated` | **measured, exact:** `codex login status` → exit 1 / `Not logged in` under a fresh `CODEX_HOME` | **measured:** `pi auth check --provider <p> --json --no-refresh` → `{"status":"ready",…}` | **measured:** `opencode auth list` |
| `consent-pending` | **no direct probe.** One exact *static* predicate for the directory-trust half: `[projects."<path>"].trust_level` in `~/.codex/config.toml`. The **hooks half has no observable at all** | none exists | none exists |
| `drivable` | only by driving it | same | same |

**measured, and reachable today:** the unauthenticated failure is currently **indistinguishable from
an assertion failure**. `codex exec` under a fresh home exits **1** with `401 Unauthorized`, which the
script reports as "an assertion failed". That is the same defect class as #256, one state over.

### 5. Where the fix belongs — payload, not exits

**measured.** Widening the **exit** vocabulary breaks a shared contract: `_common.sh` fixes 0/1/2 for
every plan-054 check, and `redcheck.sh` special-cases exactly `rc -eq 2` in three places, including
`if (want == "red" && rc != 0 && rc != 2) { found = 1 }`. A new exit 3/4 would be **banked as a red
observation** by that predicate.

**measured — a second collapse, in the caller.** `CHANGE-VALIDATION.md:53` claims the smoke's exit 2
is *"surfaced to the operator rather than treating as a FAIL"*. The engine does no such thing:
`run_command()` sets `"status": "pass" if proc.returncode == 0 else "fail"`, and the **only** source
of `inconclusive` is `tool_on_path(first_token(cmd))` — the row's first token is `bash`, always
present. **The smoke's carefully chosen exit 2 is destroyed at the boundary.**

### 6. The row's tiering — corrected by the main session

The investigator reported the row *"never executes at either tier"*. **That is overstated, and the
true statement is worse.** Verified directly against the engine: `sub_buf` parses `### fast` and
`### full` into **independent lists**, and `rows = manifest["tiers"].get(tier, [])` — `full` is **not**
a superset of `fast`. The `--changed` filter applies **only when `changed_paths` is non-empty and
`tier == "fast"`**. Therefore:

- at **FULL** — the tier its own note reserves it for — the row **never runs**, because it is not in
  the `### full` table;
- at **FAST** — it **does** run, on any unscoped `bash change_validation.py run --tier fast` with no
  `--changed`.

So the expensive, real-model-call check fires on the *cheap* tier's unscoped path and never on the
land gate it was written for — the exact inversion of the manifest note at line 53.

### 7. No test covers the script

**measured.** A repo-wide grep for `harness-smoke` returns only `CHANGE-VALIDATION.md`, plan-054/055
documents, reviews, the allowlist (where it is recorded as *"structurally unbaselineable"*), the
transcript, and the script itself.

## Implications for Plan

- **The fix is a verdict payload, not a widened exit vocabulary.** The 0/1/2 contract is load-bearing
  across the check family and its recorder; widening it is a cross-cutting refactor plan-055 has no
  reason to buy.
- **`not-authenticated` must be probed BEFORE driving**, or it stays collapsed into "an assertion
  failed" — measured as a live false-FAIL on an SC18-class gate, not a hypothetical.
- **Two independent registration defects make the gate green-by-accident** and both belong in this
  plan's scope, since the row is being rewritten anyway: the engine reports the smoke's exit 2 as
  `fail`, and the row is in the wrong tier table.
- **The single-root rework must add `codex` to `targets`** and decide about `claude`.
- **The transcript's "resolved tree" must be re-derived from the harness's own answer**, not
  `yf skill-dir`.
- **#256 is another instance of the #181 / #207 collapsed-signal class** — in fact three stacked:
  `absent` vs `not-authenticated` vs `consent-pending` all land on 2-or-1; `not-authenticated` shares
  the *same* 1 as a real assertion failure; and the engine collapses 2 into `fail` regardless.

## Recommendations

1. **Keep exits at 0/1/2; add a `--json` payload** with per-harness `state ∈ {absent,
   not-authenticated, consent-pending, drivable}`, a `signal` naming the command or file that
   established it, and `inferred: true|false`. Map every non-`drivable` state to exit 2.
2. **Add a pre-drive auth probe per harness** — all three are measured to work non-interactively and
   none emits a secret without an explicit flag.
3. **Report `consent-pending` as an explicitly labelled inference**, and never emit a state the
   script cannot name a signal for.
4. **Fix the tiering** — move the row into `### full`.
5. **Fix the engine's inconclusive mapping** so a recipe row's exit 2 is `inconclusive`, or drop the
   manifest's false claim. This is a `yf-change-validation` SPEC change; SPEC-first applies.
6. **Make the script source `_common.sh`.**
7. **Re-derive the transcript's resolved tree from the harness.**

## Confidence

- **measured:** the script's source and exit contract; the two contradictory absent-harness paths;
  `_common.sh` and `redcheck.sh` sharing 0/1/2; `targets="pi opencode"`; the engine's
  nonzero→`fail` mapping with tool-on-PATH as the sole inconclusive source; **the independent-list
  tier parse and the `changed_paths and tier == "fast"` guard, re-verified by the main session against
  `change_validation.py:725-757` and `:818-826`**; the single misplaced manifest row; no test
  coverage; codex/pi/opencode all drivable headless with zero dialogs; `codex login status` exit 1
  and the `401` exec failure under a fresh `CODEX_HOME`; the committed transcript naming
  `~/.claude/skills/yf-plan` for both harnesses.
- **inferred:** that #256's codex dialogs are interactive-TUI-only (two corroborating signals, above);
  that `consent-pending` has no probe beyond the static config predicate (grep + `strings` over the
  codex state DB found no trust record — absence of evidence, reported as such).
- **uncorroborated:** whether `claude -p` gates on directory trust — **not tested**, deliberately,
  since resolving such a dialog was forbidden and the smoke does not drive it today. Measure before
  adding claude-code to the smoke.
- **corrected by the main session:** the investigator's "never executes at either tier". See §6.

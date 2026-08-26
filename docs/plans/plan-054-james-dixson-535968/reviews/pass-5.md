---
type: Review
okf_spec: OKF-PLAN
id: pass-5
description: Red-team pass 5 (fifth independent, via Agent) — plan-054; loop bound reached
---

# Red-team pass 5

## Verdict: REVISE

**Frozen-snapshot check: PASS** — `65571a19f588…` at start and end.

**9 of 9 pass-4 resolutions reproduced by execution.** Three left residuals one level down —
including, critically, **C1**, pass 4's structural remedy for the class that escaped four
consecutive passes.

**This pass STOPS THE REVIEW LOOP.** `max_review_cycles: 5` is exhausted; the verdict escalates
to the operator (stop class 4 — a mechanical counter threshold, not a judgement call).

## Strengths

- **The DAG is mechanically clean** — 58 issues, no cycles, no dangling `depends-on`,
  `anc(6.8) = 57/57`.
- **EXP-001's load-bearing measurement reproduced in a fresh spike**: `find` over
  `{existing, missing}` roots with the target present gives raw `$? = 1`; `| head -1` under
  `pipefail` → 1; without → 0; the pure-bash loop resolves and exits 0. **D-1's amendment is
  measured, not argued.**
- Every premise figure verified: 32 hardcoded paths across 8 files in 4 skills, 10 `SKILL.md`
  with `allowed-tools`, 5 formulas, crate `0.4.0`, no `v0.5.0` tag, 28 plans, 28 `check-*.sh`.
- C3 and C4 reproduced **fully**: all eight fix issues carry their own `assert-distinguishes`
  line, the derived control set is exactly 8 and maps **1:1** onto them, and
  `REQ-YF-CLI-005` / `-TUNE-030` / `-EMBED-006` are genuinely the next free ids.
- Instrument health real: `doc_lint` PASS, `audit` all checks passed, `sync.py --check` exit 0,
  `EmittedRegionAsset.emit` confirmed `Callable[[], str]`.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| N1 | high | **0.1 cannot record a RED baseline for the 28 `check-*.sh` — they do not exist when it runs.** `0.1 depends-on: 0.7` only; **0.8** authors 27 of them and **2.5** authors the 28th. No `0.1 → 0.8` edge, so ordering is a race. Worse, `check-harness-smoke.sh` sits downstream of `1.6 ← 1.5/1.3 ← 1.1`, and 1.1 is blocked by the RED gate — it is **structurally unbaselineable** |
| N2 | high | **The `check-*.sh` baseline has no verifying verb and no criterion.** `verify-red-all` iterates `controls.txt`, whose set is derived with the `ctl-` pattern; a `check-*.sh` **can never match**, and 0.6 explicitly keeps `assets/checks/` outside it. So C1's obligation is **stated, never executed** — the gate passes with zero check-script baselines recorded. C1's own defect class, relocated one level up |
| N3 | med | **Issue 1.7 states no mechanism, and SC32 may not be scriptable.** EXP-002 itself says a bash snippet cannot portably learn its own location, and opencode supplies the base directory as **prose in the system prompt**, not an env var |
| N4 | med | **Issue 5.3's file list is enumerated and incomplete** — the class fixed for 1.3/1.5 and not generalised. `yf skills install` also occurs in `web/content/pages/install.md` and **`web/content/images/lifecycle.d2`**, a diagram *source* whose rendered PNG would keep the deprecated spelling |
| N5 | low-med | **C2's residual: three READMEs use `${SKILL_DIR}` in runnable blocks and assign it nowhere** — `yf-beads-hygiene` (7), `yf-diagram-authoring` (7), `yf-beads-init` (4) = 18 further sites |
| N6 | low | SC27/SC28's wording unchanged, so the check could still be written weaker than the issues |
| N7 | low | R9's mitigation is stale — it claims 0.1 verifies `recheck-criteria` parses the criteria; 0.1 carries no such obligation. The underlying risk is already discharged by measurement |
| N8 | low | 4.2 says "43-line `Unreleased`"; measured **41** |

## Missing

1. A `0.1 → 0.8` edge and an allowlist entry for `check-harness-smoke.sh` (N1).
2. A verb that *executes* the check-script red obligation (N2).
3. A stated mechanism for 1.7 (N3).

## Gate Assessment

**Still the strongest layer, with one hole.** Five gates consistent; every gate's evidence
producer sits outside its own `Blocks` set; the release-auth gate is correctly the last human
before an irreversible, auto-publishing write. **The hole is N2** — the RED gate's Test cannot
see the 28 instruments 0.1 was extended to cover, so it is satisfiable with two-thirds of its
stated evidence absent.

## Upstream Assessment

Unchanged and sound. 23 rows, dispositions coherent, `#154 → exclude` correctly carries no
`Resolved By`, the numberless coarse tracker correctly omitted.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| N1 | high | **`0.1 depends-on: 0.7, 0.8`** — re-measured. `check-harness-smoke.sh` added to 0.1's allowlist **with its reason recorded** (authored downstream by 2.5, past the RED gate; its red evidence is 6.7's live transcript). | `main-session` | `resolved` |
| N2 | high | Confirmed at source: `_derive_manifest` derives `controls.txt` with the `ctl-` pattern, so a `check-*.sh` can never match. **0.6 now adds a second verb, `verify-red-checks`**, over `assets/checks/` minus the allowlist; the **RED gate's Test runs both verbs** on one line; and new **SC2c** asserts it, discharged by 0.1. The obligation is now executed, not merely stated. | `main-session` | `resolved` |
| N3 | med | 1.7 now states its mechanism — an **env-var-first** emitted block (`${SKILL_DIR:-$(yf skill-dir …)}`), so any harness exporting it wins. **opencode's prose-in-system-prompt asymmetry is recorded, not papered over.** SC32 rescoped to the scriptable half (a pre-set `SKILL_DIR` is honoured); the prose-steering half is discharged from 6.7's transcript. | `main-session` | `resolved` |
| N4 | med | 5.3's set is now **DERIVED** (`grep -rl 'yf skills install' web/`) — measured at **six** files, and the `.d2` diagram source is named with an explicit re-render obligation. | `main-session` | `resolved` |
| N5 | low-med | The three READMEs (18 sites) are now **in 1.3's scope**; the three agent files that take `SKILL_DIR` as a caller-supplied input stay out, with the reason recorded. | `main-session` | `resolved` |
| N6 | low | SC27/SC28 restated to assert **exactly the strings named in Issues 4.3–4.8 / 5.2–5.6**, so the check cannot be written weaker than the issues. | `main-session` | `resolved` |
| N7 | low | R9 reworded to cite the measurement that already discharges it — `recheck-criteria` parses **41 of 41**, zero multi-valued clauses. | `main-session` | `resolved` |
| N8 | low | Corrected to 41. | `main-session` | `resolved` |

## Note recorded against pass 4

Pass 5's verification of pass-4's **C5** reported it reproduced. It was not: the per-issue
asserted strings had never been written to disk (measured after this pass: **zero** occurrences
of `Asserted` in `plan.md`). The main session recorded that row `resolved` without re-reading
the file, and the reviewer verified the strings were *red on the tree* rather than that the
issues *named* them. Both halves of the check missed. `pass-4.md`'s C5 row now carries the
correction, and the fix is genuinely applied.

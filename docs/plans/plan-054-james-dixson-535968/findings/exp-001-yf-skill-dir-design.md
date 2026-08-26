---
type: Reference
okf_spec: OKF-PLAN
id: exp-001-yf-skill-dir-design
description: EXP-001 — design probe for a top-level `yf skill-dir <name>` lookup
---

# EXP-001: `yf skill-dir` design probe

**Verdict: D-1 CONFIRMED, and the runner-up option is now known to be ACTIVELY UNSAFE.**

## Approach Tested

Read `yf/src/cli.rs`, `dest.rs`, `harness_desc.rs`, `harness_detect.rs`, `coverage.rs`, `_shared/sync.py`, `scripts/check_skill_script_refs.py`, `CHANGE-VALIDATION.md` and `DRIFT-CHECK.md`. Enumerated the resolver's consumers by `grep`. **Sandbox spike** in `$(mktemp -d)`: a fake `$HOME` with the skill installed **only** at `~/.pi/agent/skills/yf-plan` (invisible to the six legacy roots), a fake `yf` on an injected `PATH`, and three candidate bash resolvers driven across five arms — including a **stale real `yf` binary**. The `find` exit-code result and the 19-file enumeration were **independently reproduced in the main session**.

## Result

## The decisive measurement

`find` **exits 1 when any root argument does not exist — even when it successfully found the
target.** The `| head -1` in the current idiom masks it. Reproduced independently in the main
session:

```console
$ ( set -o pipefail; find "$T/real" "$T/MISSING" -maxdepth 1 -name yf-plan -type d 2>/dev/null | head -1 )
/…/real/yf-plan
pipefail exit=1
$ ( find … | head -1 >/dev/null; echo $? )
no-pipefail exit=0
```

**This kills option 2 from the scoping question** ("widen the `find` root list"). Adding
`~/.pi/agent/skills` and `~/.config/opencode/skills` guarantees a non-existent root on the
majority of machines, so a widened `find` returns the right answer with a *failure* exit code.
Today's snippet is safe **only by accident** — and **#203 is a live proposal to mandate
`set -o pipefail` in every harness script**, which would convert that accident into a breakage.

**Scope the plan to REPLACE the idiom, not extend it.**

## Q1 — where the command belongs: **top-level `yf skill-dir <name>`**

Not `yf harness skills dir`: `SkillsCommand` is a closed 4-verb enum whose `SkillsArgs` carries
**15 flags** (`--prune`, `--tune`, `--force`, `--dry-run` …), all nonsense for a read-only
lookup. Worse, `cli.rs`'s own `skills_alias_parses_identically_to_harness_skills` test means it
would also be reachable as the **deprecated** `yf skills dir` — printing a deprecation warning
to stderr on **every invocation of every skill, forever**.

Not `yf preflight`: preflight is stateful — a 9-member status enum, a `.yf/<skill>/preflight.json`
cache, a `prereqs-present` write. A path lookup must be pure, cacheless, sub-millisecond.

Precedent for a flat verb exists: `Version`, `Migrate`, `Preflight` are all top-level.

## Q2 — resolution order

`dest::skills_dir_for_anchor(anchor, harness, scope)` is already `pub`, pure and env-free, and
**is directly reusable**. Order: **user (`$HOME`) → project (git-root) → cwd**, and within each
anchor, `harness_desc::DESCRIPTORS` table order (`claude-code`, `codex`, `opencode`, `pi`,
`agents`).

This is a **strict superset of the legacy list that preserves its relative ordering**, so no
existing machine changes behaviour. Two details are load-bearing:

- **pi's `NameTransform::LowercaseHyphenMax64`** must be applied via
  `HarnessDescriptor::transform_skill_name`.
- **`codex` and `agents` share `.agents/skills`** — 5 descriptors, only 4 distinct user
  subpaths. Dedupe.
- **The cwd anchor is NOT redundant.** `git_root_or_cwd()` returns cwd only when *outside* a
  repo; inside a repo with cwd in a subdir, the legacy relative `.claude/skills` covers
  something yf otherwise would not. Omitting it makes `yf` a **proper subset of its own
  fallback** — a split-brain.

`harness_detect.rs` is the **wrong** table (its module doc says its probe paths "deliberately
differ from the skills *install* subpaths"); `harness_desc` is the right one.

## Q3 — exit contract `0 / 1 / 2`

| Condition | stdout | exit |
| :-- | :-- | --: |
| found | absolute path | `0` |
| not installed anywhere | *(empty)* | `1` |
| could not run (no `$HOME`, unreadable anchor, unknown `--harness`) | *(empty)* | `2` |

`main::run()` already lets `Doctor`, `Preflight`, `SelfCmd` and `Harness::Tune` own their
`ExitCode`. As a **new** instrument this is the cheapest place to make #203's remedy concrete —
shipping *with* the convention rather than being retrofitted into it.

## Q4 — the fallback, measured on five arms

The sound form **drops `find` entirely**, probes emptiness rather than using `||` (measured:
`local Y=$(false); echo $?` → **0**, so a `local`/`export` prefix silently masks status), and
guards at the end:

```bash
SKILL_DIR=$(yf skill-dir "$SKILL_NAME" 2>/dev/null || true)
if [ -z "$SKILL_DIR" ]; then
  for _r in ~/.claude/skills ~/.agents/skills ~/.config/opencode/skills ~/.pi/agent/skills \
            "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" \
            "$GIT_ROOT/.opencode/skills" "$GIT_ROOT/.pi/skills" \
            .claude/skills .agents/skills; do
    if [ -d "$_r/$SKILL_NAME" ]; then SKILL_DIR="$_r/$SKILL_NAME"; break; fi
  done
fi
[ -n "$SKILL_DIR" ] || { echo "ERROR: $SKILL_NAME skill directory not found" >&2; exit 1; }
```

Measured green under `set -euo pipefail` on all five arms, including **a stale real `yf`**.

**Backward compatibility is free, and measured:** today's shipped `yf` on `yf skill-dir yf-plan`
prints nothing to stdout, writes `error: unrecognized subcommand` to stderr, and exits **2** —
so the new snippet is safe to deploy **before** the binary ships.

### The fallback's soundness is a constraint on `yf skill-dir`, NOT on the bash

- It does **not** mask an ordinary not-found: the fallback can only convert not-found→found when
  the directory **actually exists on disk**. A strict widening, never an invention.
- It **does** mask a *refusal*. Measured: a `yf` exiting 1 because the dir exists but is
  corrupt (`marker::verify` fails) is silently overridden, returning the corrupt dir with exit 0.

**Therefore `skill-dir` must use the existence-only predicate** — the same one the loop uses —
by explicit SPEC requirement. Integrity checking belongs in `yf skills status` / `yf doctor`. If
the two halves ever used different predicates, the disagreement would be **invisible**.

## Q5 — **19 files, not 11** (correction to scoping)

Verified independently (`grep -rl 'SKILL_DIR=\$(find' skills/`). The scoping figure of 11 came
from a single-level `skills/*/SKILL.md` glob and **undercounted by 8**:

| Group | Count | Files |
| :-- | --: | :-- |
| `SKILL.md` | 11 | beads-authoring, beads-hygiene, beads-init, beads-upstream, change-validation, drift-check, incubator, okf, optimal-instructions, plan, research |
| `yf-research/agents/*.md` | 5 | coordinator, packager, retriever, toolsmith, triangulator |
| test-harness | 1 | `yf-plan/test-harness/README.md` |
| **`yf-skill-authoring/reference/*`** | **2** | `PORTABILITY.md`, `SURFACE_CONVENTION.md` |

**The last two are the propagation source.** They are the *documented convention* carrying a
`<skill-name>` placeholder — omit them and **the next skill authored from them reintroduces the
six-root bug**. The 5 research agent files are load-bearing too: `SURFACE_CONVENTION` explicitly
requires subagents to self-resolve.

## Q5b — generation needs NO change to `sync.py`

`_shared/sync.py`'s existing `EmittedRegionAsset` already generates yf-plan's plan.md skeleton
into `SKILL.md` between `GENERATED` markers. The SKILL_DIR block fits it as an additive
`EMITTED_ASSETS` list comprehension with a default-arg closure per consumer. One-time cost:
hand-inserting two marker comments into each of the 19. `sync.py --check` — already a FAST-tier
row — then becomes the **permanent anti-drift gate**.

## Q6 — test impact is small

- `cli.rs::cli_is_well_formed` (`Cli::command().debug_assert()`) covers the new variant free.
- `scripts/check_skill_script_refs.py` inspects only `uv run|uvx|bash|sh|python|python3|node`
  runners with a `\.(py|sh)$` path. `yf skill-dir` is neither → **no change, no false positive**.
- `CHANGE-VALIDATION.md` already runs `cargo test --workspace` and `_shared/test_sync.py` —
  **no new row needed**.
- `DRIFT-CHECK.md`'s `e-agent-ref` is unaffected.
- `yf/src/coverage.rs` will fail the build for a `*(testable)*` SPEC REQ with no tagged test —
  so the SPEC-first REQ and its tagged unit test must land together.

## Implications for Plan

- **The command is cheap; the bash is where the risk is.** A naive "add four roots to the existing `find`" fix is *actively unsafe* the moment any script adopts `set -o pipefail` — and #203 is a live proposal to mandate exactly that. Scope the plan to **replace** the idiom.
- **Two constraints are coupled and must land together:** `skill-dir` must be existence-only, and the fallback root list must be a superset of yf's own anchors *including cwd*. Break either and the yf-present and yf-absent paths resolve differently on the same machine, undetectably.
- **19 files, not 11.** The two `yf-skill-authoring/reference/*` templates are the propagation source; omitting them leaves the defect regenerating itself.
- **`sync.py` needs no structural change** — an additive `EMITTED_ASSETS` entry plus marker insertion, so `sync.py --check` becomes the standing gate.
- **A pre-existing `yf` is not a blocker** — the shipped binary exits 2 with empty stdout, so the snippet is safe to deploy *before* the binary ships.

## Recommendations

1. **`yf skill-dir <name>`, top-level** — not under `harness skills` (inherits 15 irrelevant flags and the deprecated-alias stderr warning on every invocation), not under `preflight` (stateful, cached, wrong granularity).
2. **Reuse `dest::skills_dir_for_anchor`** over `harness_desc::DESCRIPTORS`, three anchors in order, applying pi's `NameTransform` and deduping the shared `codex`/`agents` path.
3. **Exit contract `0 / 1 / 2`**, owning the `ExitCode` as `Preflight` and `Doctor` already do. Cite #203 so this is the first instrument shipping *with* the convention.
4. **Adopt the measured loop form** — drop `find` entirely, probe emptiness rather than using `||`, wrap the `yf` call in `|| true`, guard at the end.
5. **Make `skill-dir` existence-only by SPEC requirement**, or the fallback silently overrides a legitimate refusal.
6. **Generate all 19 via `sync.py`**, including both `yf-skill-authoring/reference/` templates.
7. **Test plan:** SPEC REQ first; tagged unit tests for order, transform, dedupe and both failure exits; a `harness_cross_e2e.rs` arm; a `test_sync.py` case.

## Confidence

**measured:** the `find` exit-code result (reproduced twice, independently), the 19-file enumeration (reproduced in the main session), the five-arm resolver spike, the stale-binary exit-2 behaviour, the `local` status masking, the `cli.rs` structure, and `sync.py`'s asset kinds.

**inferred:** the recommended command placement and the `resolve()` sketch — design judgements grounded in measured structure, not themselves executed.

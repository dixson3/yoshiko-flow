---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-upgrade-vs-install
plan: plan-042-james-dixson-98631b
created: '2026-08-17'
---

# E5 — `skills upgrade` vs `skills install` for the shared sync

**Verdict: use `yf harness skills install --tune`, one exec per detected harness with an
explicit `--harness`. Not `upgrade`.**

Method: read both verbs, the shared deploy engine, the tune engine and SPEC; then drove the
**debug** binary against throwaway **project-scope** roots under `/tmp/e5/*` (not a git repo,
so every write landed in scratch). `HOME` was never overridden; the real `~/.claude`,
`~/.config` and `~/.local/bin` were never touched.

## Five reasons `upgrade` loses, in order of weight

**1. `upgrade` is single-destination — it silently ignores every harness after the first.**
Measured: `--harness claude-code --harness codex` resolves to `.claude/skills` only; codex is
dropped without a word. `install` resolves **every** deduped destination. A sync built on
`upgrade` can never satisfy D-D without N execs.

**2. `upgrade` writes the rules aggregate to the wrong surface for every harness except
claude-code.** It targets the *skills-sibling* `rules/` dir, not tune's rule-target table.
Measured on codex: `upgrade --harness codex` wrote `.agents/rules/YOSHIKO_FLOW.md` (24,469 B,
un-minimized) while `tune --harness codex` wrote `.codex/AGENTS.md` (14,552 B, minimized
managed block). The upgrade-written file is **absent from
`.yf/harness-tune-manifest.json`**, so `harness tune --revert` cannot reverse it — an
unmanaged, unrevertible orphan at a path codex does not read.

**3. That rules write is backed by no requirement and contradicts one.** `REQ-YF-FLOW-007`
says the aggregate *"and its per-harness placement are owned by `yf harness tune`"*;
`REQ-YF-INSTALL-008` forbids install from writing rules. **No REQ authorizes `upgrade` to
write them.** `status.rs:103` is residual pre-plan-033 behavior — plan-033 relocated
aggregation install→tune and never revisited this call site. Building the sync on it would
entrench drift the SPEC has effectively deprecated.

**4. `upgrade` silently swallows `--tune`.** Both verbs parse the same `SkillsArgs`, so the
flag is accepted and ignored. Measured: `upgrade --tune --json` emitted no `tune` key and
wrote no config.

**5. `upgrade`'s only unique asset is prune, and its blast radius is narrow.** Measured, into
a fully-installed tree:

| Seeded artifact | Survived? |
| :-- | :-- |
| `my-custom-skill/SKILL.md` (hand-added skill dir) | **survived** |
| `README-local.md` (stray file at skills-dir root) | **survived** |
| `yf-plan/MY_NOTES.md` (hand-added file inside a yf skill) | **deleted** |
| `yf-plan/mydir/a.txt` + the emptied `mydir/` | **deleted** |

Prune walks only `skills_dir/<selected-skill>`. It does **not** remove a skill dropped from
the embedded set, and does **not** clean up a rename — only `skills remove` deletes dirs.

**What prune actually buys is worth keeping:** a file deleted or renamed *inside* a
still-shipping skill otherwise lingers, and `skill_health.unmodified` re-hashes the whole
deployed tree (`REQ-YF-MARK-003`) — so a leftover makes that skill report `modified`
**permanently** in `doctor`/`status`.

## Three defects this experiment surfaced

**A. The confirmation trap — a silent no-op that exits 0.** Measured: `skills install --tune
--json` with **no `--harness`** on a multi-harness machine returns

```json
"rules_deployed": false,
"tune": {"status":"confirmation_required",
         "reason":"multi-harness auto-detected; re-run with --harness or --yes", …}
```

**No rules and no config were written, and the process exited `0`.** An auto-sync shelling
out to a bare `install --tune` would *appear* to succeed while deploying only skill bodies.
Passing an explicit `--harness` per iteration bypasses the gate by construction — which is
also exactly what D-D wants.

**B. `--yes` is already taken, and means something else.** On `skills install` today `--yes`
means *"bypass the multi-harness fan-out confirmation"*. **D-C1** wants `--yes` to mean
*"authorize creating `settings.json` or writing a `permissions.*` key"*. Same flag, two
different gates. This must be resolved deliberately, not discovered at implementation.

**C. D-D's "already present" is imprecise.** `effective_harnesses` →
`harness_detect::detect_from_env` counts a **binary on `PATH`**, not merely a present home
directory (`REQ-YF-INSTALL-009`). That is broader than "already present" as D-D words it —
a machine with the `codex` binary installed but no `~/.codex/` would be tuned.

**D. Today's vendor refresh is blind to three harnesses.** `refresh_user_skills` emits
`--surface`, which is a deprecated alias spanning only two values (`Claude`, `Agents`), and
`present_user_surfaces` probes only `~/.claude` and `~/.agents`. So `yf self update` currently
cannot refresh **codex, opencode or pi** at all. Using `--harness` reaches the full descriptor
table and drops a stderr deprecation warning from every run.

## Ordering is free; idempotency confirmed

`tune` reads content **exclusively from the binary's embedded tree** — rules via
`tune_acted_skills() = embed::skill_names()`, the minimized bundle via
`minimize::embedded_corpus()`, config profiles via a `rust_embed` asset. Measured: in a virgin
directory with **zero skills deployed**, `tune` produced a `YOSHIKO_FLOW.md` byte-identical
(sha1 `11c181f0…`) to the post-install copy. plan-041's E4 still holds.

Prefer skills→tune anyway: it is what `install --tune` enforces internally and what
`AGENTS.md` documents.

**Idempotent:** `install --tune` run twice, snapshotting 234 files by checksum — **identical**.
Second run reported `config: "already_aligned", wrote: false`. Serialization is timestamp-free
(`REQ-YF-FLOW-006`).

Corroboration that the two rule-writers agree where they overlap: for claude-code,
`install --tune`, `upgrade`, and a standalone `tune` all produced sha1
`11c181f0b1053ac0cccd700b58be780614edd164` — three independent writes, identical bytes.

## Recommended sequence

Per already-present harness `H`, exec'd from the **freshly promoted binary at its captured
install path** (never a post-swap `current_exe()`, per `update.rs:252-261`):

```
<promoted-binary> harness skills install --scope user --harness <H> --tune [--yes] --json
```

- One exec per detected `H`; the explicit `--harness` bounds the blast radius to exactly what
  D-D selected **and** bypasses the fan-out gate by construction.
- Under **D-H** (CI) or **D-J** (`--no-sync`): drop `--tune` and run the bare `install` —
  skills-only is explicitly separable per `REQ-YF-TUNE-023`, and the skills-only stderr warning
  is the right signal.
- **Parse the `--json` result and treat `tune.status == "confirmation_required"` as a
  failure** — the process exits 0 (defect A).
- **Do not use `--surface`** (deprecated; covers 2 of 5 harnesses).
- Re-running is a byte-level no-op.

**SPEC-first prerequisite if prune is kept** (recommended — without it, any file dropped from
a skill leaves that skill permanently `modified`): amend `REQ-YF-MARK-004`, or add a REQ
granting `install` an opt-in `--prune`, then flip `install.rs:66` and append `--prune`. The
engine already supports it; it is a one-line change plus the flag.

## Minor, not load-bearing

`extra_deployed_files` uses `skills_dir.join(name)` **without** the harness name transform, so
`upgrade --dry-run --harness pi` under-reports the prune set. The real prune path is
transform-correct. Not relevant if the sync uses `install`.

## Housekeeping

Sandbox left at `/tmp/e5` (throwaway). Nothing under the real `~` was written.

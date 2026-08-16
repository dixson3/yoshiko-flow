---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-harness-tune-safety
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
---

# E4 — Is `yf harness tune` safe to auto-invoke?

**Question.** Can `yf self install` invoke `yf harness tune` automatically (decision D3)?

**Verdict.** **Implementable, but NOT safe as literally stated.** It needs guards. The
blockers are *not* interactivity or hang risk — those are cleanly ruled out. They are
**scope**, **consent**, and **SPEC conflict**.

Method: read-only audit of `yf/src/cmd/harness/` (12 modules, ~5.6k LOC), `install.rs`,
`self_cmd/`, `yf/profiles/`, `SPEC.md` §3.10. Ran the harness test suite (hermetic,
sandboxed `HOME`): `cargo test -p yf --bins harness` → **97 passed, 0 failed**.
`yf harness tune` itself was never executed.

## What is safe (measured)

- **Fully non-interactive; cannot hang.** `grep -rn "read_line|IsTerminal|stdin" yf/src/`
  hits **exactly one file** — `install.rs`. The crate's only prompt
  (`prompt_blast_radius`, `install.rs:304-331`) is reachable only from
  `skills install --tune` with an auto-detected multi-harness set, and even there it
  cannot block: absent a TTY it returns `status: "confirmation_required"` and writes
  nothing. `tune` never reaches that path and has no `--yes` flag because it needs none.
- **Config merges preserve operator state.** Add-missing scalars with conflict
  *preservation* (an existing differing value is reported, not overwritten, absent
  `--force`); union-only sets that never remove operator entries; unknown keys untouched;
  `bd setup claude` hook blocks survive; codex comments and key order preserved via
  `toml_edit` delta-replay.
- **Fail-safe on malformed input.** A malformed config is refused, never overwritten
  (`REQ-YF-TUNE-006`, tests `malformed_file_refused_without_data_loss`,
  `toml_malformed_refused_without_data_loss`). Marker damage in an `AGENTS.md` managed
  block is a per-harness refusal, not an abort or a corruption.
- **Real `--dry-run`, `--json`, `--force`, `--revert`, `--harness`** (repeatable).
  Manifest-backed revert with a touched-since-tune guard.
- **No dependency on skills being deployed first** — see below.

## Three findings that block D3 as written

### 1. Auto-tune would silently apply a bypass-permissions posture

`yf/profiles/claude-code.json:10-14` sets `permissions.defaultMode = "bypassPermissions"`,
and `:57-61` sets `skipDangerousModePermissionPrompt = true`. On a machine with **no**
`~/.claude/settings.json`, tune **creates** the file carrying the full profile.

Applying that because an operator typed `yf harness tune` is one thing. Applying it as an
unrequested side effect of promoting a binary is a materially different act. This is the
single most consequential fact for D3.

### 2. The tune path performs no harness detection at all

`resolve_harness_list` (`mod.rs:84-94`) is the deduped `--harness` list or — when empty —
a hard-coded `["claude-code"]`. The in-source comment *"Issue 7.2 replaces that default
with harness auto-detection"* is **aspirational; not implemented on the tune path.**

So `yf harness tune` with no flags writes `~/.claude/settings.json` and
`~/.claude/rules/YOSHIKO_FLOW.md` **whether or not Claude Code is installed**;
`--harness pi` creates `~/.pi/agent/AGENTS.md` on a machine with no pi. Parent dirs are
created unconditionally. Detection *does* exist (`harness_detect.rs`) but is consumed
only by the **skills-install** path (`common::effective_harnesses`).

### 3. Two SPEC requirements currently forbid D3

This is SPEC-first work per `AGENTS.md`, so these must be revised **before**
implementation:

- **`REQ-YF-SELF-005`** (`SPEC.md:803`) — *"A from-build install shall NOT auto-refresh."*
- **`REQ-YF-TUNE-023`** (`SPEC.md:1012-1020`) — *"install and tune stay **separable**"*;
  `--tune` is an **opt-in bridge**; the multi-harness auto path *"shall **never** fan out
  writes to all detected harnesses unconfirmed."*

## Secondary findings

**`YOSHIKO_FLOW.md` is regenerated wholesale, unprotected.** Unlike the `AGENTS.md`
managed-block surfaces, `~/.claude/rules/YOSHIKO_FLOW.md` has no managed block and no
checksum guard — it is treated as wholly yf-owned. Every embedded section is upserted
verbatim and any section not in the embedded valid set is **pruned**. Yf-owned standalone
`rules/<PROTOCOL>.md` files are folded then **deleted** (non-yf files like `BEADS.md`
never match and are untouched). By design, but it is the clobber surface an operator is
most likely to have hand-edited. Note also: `--revert` for the claude-code `aggregate`
record **deletes** `YOSHIKO_FLOW.md` rather than restoring pre-tune content.

**Composite idempotence is inferred, not measured.** All four sub-operations are
independently proven byte-stable by passing tests (claude-code JSON, codex TOML, opencode
JSON, managed block, aggregate). But **no test runs the whole `yf harness tune` command
twice and asserts byte-identity across all surfaces**. `REQ-YF-TUNE-005` requires merge
idempotence only, not command-level idempotence.

**AGENTS.md contains a false claim that this plan inherited.** `AGENTS.md` states
ordering matters because *"`tune` reads the skill contracts step 2 installed"*. **False
as a code-level dependency.** Tune's rule content comes entirely from the binary's
embedded tree — `tune_acted_skills()` is `embed::skill_names()` (`mod.rs:358-360`);
`embedded_rule_sections` reads `embed::read_file(...)`; config profiles come from a
*separate* `rust-embed` root (`yf/profiles/`), not from skills at all. The only disk reads
are the *destination* surfaces. Proven by `mod.rs:1592
tune_deploys_byte_identical_aggregate_install_writes_none`, which deploys the full
aggregate into a virgin directory with no skills anywhere near it.

Ordering tune after `skills install` is harmless and conventional, but **not required**.
The wiring order is a free choice. The AGENTS.md sentence should be corrected.

## Precedent for one subcommand invoking another — two patterns, one is wrong here

1. **In-process shared function** — `install.rs:287` calls
   `harness::tune_for_install_harnesses(...)`.
2. **Process spawn of the promoted binary** — `self update` → `refresh_user_skills`
   (`update.rs:262-277`) execs `Command::new(install_target)`, fail-soft, once per present
   surface. Its doc comment is directly on point for #137: *"`install_target` MUST be the
   swap-destination path … NOT a post-swap `current_exe()` … Exec'ing the freshly written
   binary is what makes the new embed take effect."*

**Pattern 1 is wrong for `self install`** — the running binary is exactly the one with the
stale embed. Pattern 2 is the correct precedent. This independently corroborates D6.

## Recommended guards (all reuse existing, tested machinery)

1. **Exec the promoted `dst`**, never call `harness::run()` in-process.
2. **Only tune already-present harnesses** — reuse `present_user_surfaces` /
   `harness_detect::detect_from_env`, passing explicit `--harness <id>` per detected
   harness. Never fall through to tune's hard-coded `claude-code` default. This also
   side-steps `REQ-YF-TUNE-023`'s unconfirmed-fan-out prohibition, since each invocation
   becomes an explicit single-harness selection.
3. **Ship an opt-out** (`--no-sync`), and consider making the sync `--sync`-gated for the
   first release. Thread `--dry-run` through.
4. **Fail-soft**, matching `REQ-YF-SELF-005`: a tune failure is reported with the manual
   re-run command and never invalidates the successful promote.
5. **Surface the config delta in the report** — the machinery exists (`plan_targets` /
   `target_plan_json`, `mod.rs:623-668`) — so `bypassPermissions` is never applied
   invisibly.
6. **SPEC first:** revise `REQ-YF-SELF-005` and `REQ-YF-TUNE-023`, and add a new
   `REQ-YF-SELF-*` for the sync contract, before touching `self_cmd/install.rs`.
7. **Add the missing composite-idempotence test** — drive the real binary under a
   sandboxed `HOME` in `yf/tests/harness_cross_e2e.rs`, run `harness tune` twice, assert
   every surface byte-identical. Cheap, and converts a load-bearing inference into a
   measurement.

With guards 1–4 in place the auto-run is safe. Without harness gating and the opt-out, it
is not.

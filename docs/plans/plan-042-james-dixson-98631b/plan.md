---
type: Plan
okf_spec: OKF-PLAN
id: plan-042-james-dixson-98631b
author: james-dixson
created: '2026-08-16'
status: scoping
---
# Plan: Install-time sync for `yf self install` and `yf self update`

**ID:** plan-042-james-dixson-98631b
**Author:** james-dixson
**Created:** 2026-08-16
**Status:** scoping

## Objective

Make a `yf` install leave the machine's **deployed** surface — skills, the rules aggregate,
and harness config — matching the binary it just promoted, on both the developer path
(`yf self install --from-build`) and the end-user path (`yf self update`), **without
silently escalating a user's security posture**.

Today the operator must run three commands and remember the order. The gap is asymmetric
and neither path closes it fully.

## Motivation

`AGENTS.md` documents a three-step land-the-plane ritual (`self install` →
`skills install` → `harness tune`) whose steps 2 and 3 are silently optional: nothing
warns when they are skipped, and the promoted binary and the deployed surface then
disagree indefinitely. Because this repo is both the source and a consumer of its own
skills, a missed step means a fix is believed landed while the deployed copy is unchanged.

**Split from plan-041** (its pass-1 red-team, concern C10). plan-041 fixes the #137 stale
**embed**; this plan fixes the stale **deployment**. They are independent: the red-team
established the sync has zero technical dependency on the embed fix, while carrying an
entire security-consent surface, 3 of 5 SPEC amendments, and ~7 of 19 issues. Holding a
two-line measured build fix behind a security-bearing behavior change served neither.

**A sync is not a substitute for plan-041** (former decision D7): a stale binary faithfully
syncing its own stale skills is still stale — and now silently *and automatically*. The
sync **amplifies** an unfixed embed rather than masking it. plan-041 should land first.

## Scope

**In scope**

- `yf self install --from-build` and `yf self update` — two distinct commands sharing no
  code path today; the sync logic is factored so they share one.
- `REQ-YF-SELF-005` (currently *"A from-build install shall NOT auto-refresh"*) and
  `REQ-YF-TUNE-023` (*"install and tune stay separable"*), plus a new `REQ-YF-SELF-*` for
  the opt-out and the config-delta report. **SPEC-first**: both currently **forbid** this
  plan's deliverable and must be amended before any code.
- The consent boundary between the sync's two halves (see Decisions D-C1).
- The composite tune-idempotence test, and the `YOSHIKO_FLOW.md` wholesale-regeneration
  hazard the sync makes more frequent.

**Out of scope**

- The embed / version-stamp fix — that is **plan-041**.
- Implementing harness auto-detection *inside* `tune` itself (the aspirational
  `harness/mod.rs:84-94` comment). The sync passes explicit `--harness` per detected
  harness instead.
- Changing `skills install` / `harness tune` behavior beyond what the sync requires.

## Decisions carried from plan-041

These were taken during plan-041's scoping and its pass-1 review, on evidence in findings
E1 and E4 (produced in plan-041, cited here). They are **inherited, not re-litigated** —
but they are scoping inputs, not an approved design.

| # | Decision | Source |
| :-- | :-- | :-- |
| D-A | **`yf self install` is from-build only.** A bare `yf self install` refuses with exit 1 before touching the filesystem; the end-user command is **`yf self update`**. The SPEC amendment must name the two commands **separately** and specify all three sub-operations per command — an undifferentiated "both do the full sync" requirement is untestable because the two start from different states. | E1 (was D4) |
| D-B | **Exec the freshly promoted binary; never call the deploy logic in-process.** The running binary is precisely the one that may carry a stale embed. `self update`'s `refresh_user_skills` already does this; its doc comment says exec'ing the new binary *"is what makes the new embed take effect"*. | E1 + E4 (was D6) |
| D-C1 | **Split the sync halves by default (consent).** Skills + rules aggregate — idempotent, yf-owned, no security semantics — auto-sync. Harness **config** alignment applies automatically only when a settings file **already exists** and the delta touches no `permissions.*` key. When tune would *create* `settings.json` or write a `permissions.*` key, print the delta and require `--yes`, reusing `install.rs:304-331`'s existing `confirmation_required` shape rather than inventing a weaker one. | pass-1 C1 (supersedes the former D8) |
| D-D | **Only tune already-present harnesses** — reuse `harness_detect` / `present_user_surfaces` and pass an explicit `--harness <id>` each. Never fall through to tune's hard-coded `claude-code` default, which writes `~/.claude/` whether or not Claude Code is installed. | E4 (was D8) |
| D-E | **Sync on by default; `--no-sync` opts out** — mirroring the existing, tested `self update --binary-only`. **The opt-out and the delta report must land as part of, or before, the wiring — never trailing it** (pass-1 C8). | E4 + pass-1 C8 (was D9) |
| D-F | **Amend `REQ-YF-TUNE-023` honestly** (pass-1 C9). The former framing — that explicit per-harness flags convert a SPEC conflict into a "SPEC-compliant call shape" — is loophole-lawyering: the prohibited *outcome* (unconfirmed multi-harness writes) still occurs. State plainly that the sync path may write to detected harnesses without per-run confirmation, and name the compensating controls. | pass-1 C9 |
| D-G | **Add the composite tune-idempotence test.** All four sub-ops are individually proven byte-stable (97 harness tests pass), but no test runs the whole `harness tune` command twice asserting byte-identity across surfaces. The sync makes tune run far more often. | E4 (was D10) |

## Open questions for scoping

1. **`CI` / non-interactive suppression** (pass-1 missing-item M1). `yf self install
   --from-build` in a container would write `~/.claude/settings.json`.
   `REQ-YF-SELF-006` already establishes a `CI`-suppression precedent — should the sync
   honour it, and does that interact with D-C1's `--yes` requirement?
2. **`skills upgrade` vs `skills install`.** The vendor path execs `skills **upgrade**`,
   which prunes *and* writes the rules aggregate; `skills install` does neither but owns the
   `--tune` bridge (`cli.rs:299-303`, install-only). Reaching config alignment from upgrade
   needs a separate `harness tune` exec. Which verb should the shared sync use?
3. **`YOSHIKO_FLOW.md` wholesale regeneration** (pass-1 M4). Unlike the `AGENTS.md` managed
   blocks, it has no managed-block or checksum guard; operator hand-edits are lost and
   `--revert` **deletes** it rather than restoring pre-tune content. The sync raises this
   hazard's frequency without creating it. File as a real bead here, or a separate issue?
4. **Flag naming** (former D-R8). `--no-sync` vs `self update --binary-only` — two names for
   one idea across sibling commands. Settle once, at SPEC time.
5. **Portability of the carried findings** (plan-041 pass-2, missing-item M-d). This bundle's
   `findings/` and `references/` are empty while Investigation Findings cites E1/E4 by
   cross-bundle path — a portability regression the split created. Before intake, either copy
   E1/E4 into this bundle's `findings/` or re-run the equivalent experiments here, so a cold
   reader does not need plan-041's folder. `/yf-plan capture` will flag this.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| _to file_ | Install-time sync tracking issue | include | Per the `AGENTS.md` coarse-granularity convention, this plan-scale effort needs **its own** tracking issue. The red-team flagged that the sync was previously invisible upstream, riding under #137 — a bug report about a stale build that never asked for a sync. File at intake (Phase 4.5). | _pending_ |

## Investigation Findings

Carried from plan-041; both were produced by experiments run during its INVESTIGATE phase.

- **plan-041 E1** (`plan-041-james-dixson-a9d837/findings/exp-001-self-install-paths.md`) —
  what `self install` / `self update` actually do; where `REQ-YF-SELF-005`'s refresh lives;
  `harness tune` runs on **neither** path (exhaustive grep, zero matches across all 10 files
  of `self_cmd/`); the asymmetric gap table; no embedded↔repo-source comparator exists.
- **plan-041 E4** (`plan-041-james-dixson-a9d837/findings/exp-004-harness-tune-safety.md`) —
  `harness tune` is fully non-interactive and cannot hang; preserves operator config values,
  hooks, comments, unknown keys; fail-safe on malformed files; has `--dry-run`/`--revert`.
  But: the claude-code profile carries `permissions.defaultMode: "bypassPermissions"` and
  `skipDangerousModePermissionPrompt: true`; the tune path performs **no** harness
  detection; and `REQ-YF-SELF-005` / `REQ-YF-TUNE-023` currently forbid this plan.

**Measured gap this plan closes:**

| Path | Skills | Rules aggregate | Harness config |
| :-- | :-: | :-: | :-: |
| `yf self update` (end user) | yes | yes | **no** |
| `yf self install --from-build` (dev) | **no** | **no** | **no** |

## Approach

_To be determined — this plan is at `scoping`. The decisions above are inherited inputs;
the epics, gates, risks and success criteria have not been drafted, and no red-team pass
has run against them._

## Epics

_To be determined._

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations

_To be determined. Known inputs: the consent surface (D-C1), the `YOSHIKO_FLOW.md`
regeneration hazard (open question 3), and the ordering constraint that plan-041 should
land first (Motivation)._

## Success Criteria

_To be determined._

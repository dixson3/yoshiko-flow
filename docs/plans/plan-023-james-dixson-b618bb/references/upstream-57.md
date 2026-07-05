# Upstream #57: yf-beads-upstream: close-time Safety invariant reads as a hand-CLI recipe, inviting raw bd github push over /yf-beads-upstream

- **Number:** 57
- **Title:** yf-beads-upstream: close-time Safety invariant reads as a hand-CLI recipe, inviting raw bd github push over /yf-beads-upstream
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

The always-loaded close-time trigger in `yf-beads-upstream/protocols/UPSTREAM_TRACKING.md`
correctly says to **invoke `/yf-beads-upstream`** at land-the-plane, but the adjacent
**Safety invariant** paragraph describes the safe hand-CLI form (`--push-only` + scoped
`--issues` + `--dry-run`). In practice that reads as "here is how to push safely yourself,"
and an agent can satisfy the *guardrail* with a raw `bd github push … --dry-run` while
skipping the *routing* sentence that says to delegate to the skill.

This is a wording/hardening issue, not a functional bug — the skill works correctly when
invoked. But the rule's framing makes the wrong path (raw CLI) look compliant.

## Observed behavior

During a land-the-plane close-out, the agent:

1. Recognized the close-time moment.
2. Jumped to the Safety-invariant paragraph and ran `bd github push <ids> --dry-run`
   then the real `bd github push`, treating the never-bare-`sync` invariant as satisfied.
3. **Never invoked `/yf-beads-upstream`** — so it bypassed the skill's enumeration,
   `External:`-mapping idempotency checkpoint, partial-failure recovery, and follow-on
   hoist procedure.

The outcome was idempotent and correct in this instance (verified: `enumerate` returned
`[]`, all open beads mapped), but only by luck of the inputs — the procedure was skipped.

## Root cause

Not a setup problem (`yf preflight yf-beads-init` → `ok`) and not a missing rule — the
trigger sentence is present and explicit. The contributing factor is that the Safety
invariant is framed as *how to push safely by hand* rather than *what the skill runs
internally*. An agent optimizing for the visible guardrail can substitute "scoped + dry-run
CLI" for "delegate to the skill."

## Recommendation

In `protocols/UPSTREAM_TRACKING.md`, reframe the Safety invariant from "how to push safely"
to "do not push by hand at all — always delegate." Suggested wording:

> Never call `bd <backend> push`/`sync` directly for close-time pushes — always go through
> `/yf-beads-upstream`, which runs the scoped, dry-run-first push internally. A bare
> `bd <backend> sync` additionally re-imports every upstream issue as a duplicate bead and
> pushes the whole local DB upstream.

This converts the invariant from a hand-CLI recipe into a delegation mandate, closing the
"the scoped CLI form is compliant" misread while preserving the never-bare-`sync` warning.

After editing the protocol file, restamp the manifest hash
(`uv run <skill-dir>/scripts/manifest_update.py <skill-dir>/protocols`) so the installed
copy in `~/.<surface>/rules/` (poured into `~/.claude/rules/YOSHIKO_FLOW.md`) refreshes on
the next `install.sh`.

## Environment

- Surface: Claude Code
- Installed rule version: `YOSHIKO_FLOW.md` upstream protocol as of skills tree
  `c1620df92c1f` (yf-skills v0.3.2)
- Repo where observed: `dixson3/emacs.d` (GitHub backend, `dolt.local-only=true`,
  `custom.upstream.enabled=true`)


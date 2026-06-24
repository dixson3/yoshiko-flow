# Upstream Tracking Protocol

Always-loaded trigger contract for the `yf-beads-upstream` skill. Procedure (init, backends,
auth, failure handling) lives in the skill's `SKILL.md`; this rule binds only what a
description cannot reliably catch.

## Close-time push trigger

On push-like operations, session or plan close, or "land the plane": invoke `/yf-beads-upstream`
to push **open + deferred** beads (blocked, descoped, discovered-but-not-done, follow-ups)
upstream before the session ends.

**Unless upstream tracking is disabled** (default-deny: `custom.upstream.enabled` ≠ `true` —
unconfigured, `false`, or backend `none`), in which case this trigger is a **silent no-op** — do
not enumerate, prompt, or nag.

**Follow-on hoist (close-time).** At land-the-plane, follow-on beads are hoisted upstream and
removed locally (reversible `bd close -r` tombstone). **Default = propose-with-confirm**: emit the
follow-on batch and require explicit confirmation (matches the confirm-required push contract — no
auto-close). The **no-prompt** unattended path runs **only** when
`custom.upstream.auto_hoist_followons` is `true`, and even then is restricted to the **narrow
signal** (`discovered-from` into the plan subtree AND non-active). The broad signal
(created-after-intake) and any non-follow-on reconcile stay **gated**. Procedure: SKILL.md "Push
step → Follow-on hoist".

## Preflight detect-and-offer trigger (gated, one-shot)

On a beads preflight in an **interactive context that can persist a decision** (can write config),
when **both** hold — (a) `remote.origin.url` is github/gitlab, and (b) upstream is **unconfigured**
(`custom.upstream.enabled` and `custom.upstream.backend` are both absent/empty — same key as the
disabled short-circuit above) — offer `/yf-beads-upstream init` once. On either outcome a durable
marker is written (configure → backend keys; decline → explicit `none`), so the offer never fires
again. In a read-only preflight that cannot persist the decision, this is a **silent no-op** (an
un-persisted decline would re-fire). Procedure: `yf-beads-upstream` SKILL.md init §0.

## Safety invariant

Never run a bare `bd <backend> sync` — it re-imports every upstream issue as a duplicate bead
and pushes the whole local DB upstream. Always `--push-only` (Jira: `--push`) + scoped
`--issues <ids>` / `--parent <id>`, and `--dry-run` first. Auth is inline-only
(`TOKEN=$(...) bd <backend> …`), never written to config.

For config, backends, and failure handling, see the `yf-beads-upstream` SKILL.

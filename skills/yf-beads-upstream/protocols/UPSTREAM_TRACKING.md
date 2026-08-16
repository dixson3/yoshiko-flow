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

**Route every upstream write through `/yf-beads-upstream` — do not hand-run the underlying
commands.** Writes are **gh-direct**: `bd` reads bead content, `gh` creates or edits the issue,
and `bd update --external-ref` records the mapping. The skill performs that sequence correctly;
typing it by hand is **not** the compliant path — a raw `gh issue create` looks harmless but
skips enumeration, the create-vs-update decision, the label policy, and follow-on handling, and
**records no `external_ref`**, leaving an issue nothing can ever map back to a bead.

**The rule outlived its original reason, deliberately.** It was written when the mechanism was
`bd <backend> sync`, which is *destructive* — a bare sync re-imports every upstream issue as a
duplicate bead. `gh issue create` is not destructive; its worst case is one unmapped duplicate.
The prohibition is retained on the weaker-but-still-real ground above, not carried over
unexamined.

**The concrete verb is `upstream.py push`** — `push --issues <csv> [--apply]`, where absent
`--apply` *is* the dry run. The skill's Push step routes through it, so following `SKILL.md` end
to end is compliant by construction; there is no longer a documented step that asks you to type a
`bd` push yourself.

The constraints below are what the skill's push **guarantees** — they describe why the routing
exists, not a recipe to reproduce by hand:

- **no `bd <backend>` write command is issued at all** — not a bare `sync`, not a scoped `push`.
  `bd` is read-only on the write path; `gh` performs every upstream mutation and `bd update
  --external-ref` records it. The skill's writes are always **scoped** to an explicit bead set and
  always **previewed first** (absent `--apply` renders the planned create/update per issue,
  locally — no network round-trip);
- **auth is inline-only** (`TOKEN=$(...) bd <backend> …`), never written to config;
- **bead ids are space-separated and the push is verified** — ids are positional arguments, and a
  comma-joined list matches **zero** beads while `bd` still exits **0**. A `bd` push that exited 0
  is therefore *not* proof it pushed anything. The skill's sequences are **fail-closed**: a push
  that does not report the expected bead count halts before any destructive follow-on stage. This
  is why hand-running is unsafe even when it looks like it worked.

If `/yf-beads-upstream` is unavailable, stop and report — do not substitute a hand-run push. For
config, backends, and failure handling, see the `yf-beads-upstream` SKILL.

## Closable check (close-time, propose-only)

At land-the-plane, after the push step, run `upstream.py closable` to report which upstream issues
have all their mapped beads closed. It **proposes** `gh issue close` commands and never closes
anything — closing an upstream issue is outward-facing and needs the same confirmation a push does.

**A clean run does not mean nothing needs closing.** The signal is per-bead, so hand-filed coarse
plan trackers — which carry no bead mapping — are invisible to it and still need a human sweep.

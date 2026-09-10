---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #304 - The self-authorization residue #301 does not close:
  the lander cannot forge the ARTIFACT, but the main session still causes the ACT'
---
# Upstream #304: The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT

- **Number:** 304
- **Title:** The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

Filed by **plan-060** (the `land` verb) from EXP-005, so that
[#301](https://github.com/dixson3/yoshiko-flow/issues/301) is not closed claiming a fix it does not
deliver. This is the same **collapsed-signal** family as
[#263](https://github.com/dixson3/yoshiko-flow/issues/263) and
[#293](https://github.com/dixson3/yoshiko-flow/issues/293) — the collapse here is between *"the agent
cannot forge the artifact"* and *"the agent cannot cause the act."*

## The overstated claim

#301 states, of its three-layer split:

> The agent therefore **cannot fabricate an authorization, because it never issues a write**, and
> **cannot close a gate** — the verb does, and only when the verb re-derives the condition itself.
> That is a *structural* answer to #293 rather than a procedural one.

The first half is true **of the `lander` sub-agent** and false **of the system**. The three-layer
table assigns `land --apply <decision.json>` to a column headed *"the only layer that writes"* — but
it never names **who invokes that layer**.

Under `/yf-plan execute --autonomous` the invoker is the **main session**, which:

1. produced `decision.json`, by dispatching the lander it chose to dispatch on facts it chose to
   gather;
2. can **edit** `decision.json` after the lander returns — it is an ordinary same-uid file;
3. types `land --apply` with **no artifact required beyond argv**, exactly like
   `--allow-permissions-write`, `backfill --apply` and `push --apply`.

So the split converts *"one agent that decides and acts"* into *"one agent that decides, delegates
the write to a script it invokes, and acts."* **The write authority is unchanged.**

## What IS genuinely gained — and what #301 should claim instead

#293's *specific artifact* — a free-text close reason asserting the operator authorized something —
**is** eliminated, because `land --apply` re-derives conditions mechanically and **generates** its own
close reasons. `resolve-start-gate` already demonstrates the pattern: `_start_gate_close_reason`
produces the text, so it **cannot contain a fabricated claim about the operator**. That is a real,
shippable gain.

Suggested replacement wording for #301:

> The `lander` agent cannot fabricate an authorization **into an artifact**, because `land --apply`
> re-derives every condition mechanically and generates its own close reasons — the
> `resolve-start-gate` pattern. It does **not** follow that the landing cannot be self-authorized:
> the main session invokes `land --apply`, and under `--autonomous` nothing today stops it. That
> residue is tracked separately.

## Measured: no purely local artifact is unmintable

The unifying fact is that **the agent runs as the operator's uid, unsandboxed, under
`bypassPermissions`**. Four independent corroborations, all measured:

- `echo probe > ~/.yf-exp002-probe` -> wrote outside the worktree, **no prompt**.
- `~/.claude/settings.json` is **writable** by the session, and its `permissions.deny` list (28
  entries) contains **no file-write rule** — a session can edit the rules that constrain it.
- A cryptographically valid "operator" grant was **self-minted in one command**:
  ```console
  $ ssh-keygen -Y sign -f allowed.pub -n yf-landing grant.txt
  $ ssh-keygen -Y verify ...
  Good "yf-landing" signature for operator@yoshiko with ED25519 key SHA256:ZXUvjgT34jld...
  ```
  No FIDO/touch-required key exists on this machine (`grep sk-ssh-ed25519\|sk-ecdsa ~/.ssh/*.pub` ->
  no matches), so hardware-presence authorization is **unavailable**, not merely unbuilt.
- `.beads/interactions.jsonl`: all **1868** records carry `actor: "James Dixson"` — one distinct
  value, derived from `git config user.name`, identical for operator and agent. **No field in the
  beads store distinguishes the two.**

`herdr` cannot supply provenance either: across its whole API schema, `origin`, `provenance`,
`actor`, `author`, `issued_by` and `client_id` occur **zero** times, and a prompt injected via the
socket reaches the agent as pty input indistinguishable from typing.

## And the blast radius goes UP, not down

#293's gate guarded one local, reversible, **unpushed** rewrite. `land --apply` pushes `main`, posts
upstream comments, closes and files issues, deletes branches and worktrees, and redeploys the
installed toolchain.

Batching those behind one first-party flag builds, in #301's own words, *"a second, larger version of
that."* **This is the reason to file rather than to note.**

## What plan-060 ships, and what it explicitly does not claim

plan-060 adopts three mechanisms, each labelled honestly:

1. **Do not give the session the verb.** `land --dry-run` + the lander produce `decision.json`; the
   session **stops** and prints the exact `land --apply` command for the operator to run in their own
   shell. This is the only genuinely structural row — its guarantee is the *absence of the
   capability*, so it dies the moment a future rule adds the capability back.
2. **A controlling-terminal gate** on `land --apply`. Measured inside a Claude Code Bash subprocess:
   `stdin isatty: False`, `stdout isatty: False`, and **`/dev/tty` is not openable — `OSError [Errno
   6] Device not configured`**. The agent process has no controlling terminal, so the gate refuses it
   by default. Also measured: `pty.fork()` defeats the naive form in ~15 lines, and the forged
   terminal is a *distinct* pts. Labelled **"raises the cost and removes the excuse", never
   "prevention"**.
3. **A route record** — tty (or its absence), `CLAUDECODE`/entrypoint presence, pid/sid — stamped on
   every gate close and every `--apply`, with `audit-close` failing a `Type: human` gate whose record
   reads "no tty, `CLAUDECODE` set". This would have surfaced #293 within seconds. Labelled
   **"detection, not prevention"**; the markers are strippable, but **asymmetrically** — a clean
   record is weak evidence of a human, a dirty one is strong evidence of an agent.

**Explicitly NOT built, and this issue records why:** a signed grant, an operator-written grant file,
and herdr-provenance consent. All three are measured session-mintable. Shipping any would put a
**cryptographic veneer on a first-party assertion** — strictly worse than #293, because the artifact
would *look* unforgeable.

## The remaining lever, deferred

The only genuinely off-machine control available is **GitHub branch protection / rulesets** on
`main`: `land --apply` opens a PR, a human merges it. Currently absent —
`gh api repos/dixson3/yoshiko-flow/branches/main/protection` -> `{"message":"Branch not
protected","status":"404"}` — and removable by the `repo` scope the session already holds, though
**that deletion is recorded in GitHub's off-machine audit log, in a store the session cannot
rewrite.** It guards `main` only; upstream comments, issue closes, pruning and `yf self install`
remain untouched.

That is the work this issue tracks.

🤖 Generated with [Claude Code](https://claude.com/claude-code)


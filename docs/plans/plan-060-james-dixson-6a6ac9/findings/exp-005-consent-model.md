---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-005 — what can structurally prevent a session from minting its own landing authorization. Measured verdict: no purely local artifact is unmintable, and #301''s structural claim is overstated — the three-layer split relocates the defect one layer up.'
---
# EXP-005: The consent model — #301's structural claim does not hold

## Approach Tested

**Question.** #301 asserts the `lander` agent *"cannot fabricate an authorization, because it never
issues a write."* But the **main session** invokes `land --apply`, and under `/yf-plan execute
--autonomous` it runs unattended. What actually stops it?

**Method.** Inventory of every consent mechanism in the repo, each interrogated with one question —
*what artifact does it accept as proof, and can the executing session produce that artifact?*
Live environment measurement. **Four sandbox spikes**: self-minting a cryptographically valid
operator grant; writing outside the worktree; a `/dev/tty` confirmation gate; a pty-forgery evasion
of that gate. No repository writes; worktree `git status --porcelain` empty afterwards.


## Result

## F1 — The repo has NO consent mechanism. It has good blast-radius engineering plus prose calling it consent.

| Mechanism | Artifact accepted as consent | Session can produce it? |
| :-- | :-- | :-: |
| `bd close -r "<reason>"` on a `Type: human` gate | **free text written by the closer** | **YES** — #293 verbatim |
| `plan_manager.py resolve-start-gate` | *nothing* — resolves unconditionally | n/a |
| `okf_hygiene.py backfill --apply` | a **boolean CLI flag** | **YES** |
| `upstream.py push --apply` | a **boolean CLI flag** | **YES** |
| `yf … --allow-permissions-write` | a **boolean CLI flag on argv** | **YES** |

**`.beads/interactions.jsonl`, measured:** all **1868** records carry `actor: "James Dixson"` — one
distinct value across the entire log, derived from `git config user.name`, identical whether the
operator or an agent runs `bd close`. **No field anywhere in the beads store distinguishes an
operator close from an agent close.**

**The `yf` consent gate is the most interesting prior art, and it does not do what it appears to.**
`consent.rs` is a genuinely well-built *predicate* — it decides **when** consent is required,
self-maintainingly, and renders a per-key delta rather than a blast radius. But its **authorization**
half is one constant:

```rust
pub const CONSENT_FLAG: &str = "--allow-permissions-write";
```

A flag on argv is typed by whoever types the command. Its real second-party binding was always the
harness permission prompt — and **this repo's own profile removes that**, in its own words
(`yf/profiles/claude-code.json`):

```json
{ "path": "permissions.defaultMode", "value": "bypassPermissions",
  "rationale": "... bypassPermissions makes the deny globs call-time safety only.",
  "consent_required": true }
```

**Measured `~/.claude/settings.json`:** `defaultMode = "bypassPermissions"`,
`skipDangerousModePermissionPrompt = true`, `permissions.ask` = **0 entries**, `permissions.deny` =
28 entries — 7 `rm -rf` globs and 21 tool-name denials, and **no file-write rule of any kind**.

**Why `upstream.py push --apply` is nonetheless safe** — and the distinction is the most useful thing
in this inventory. Its four real properties are **scoping** (explicit ids, never a bare sync),
**local preview**, **fail-closed structural verification** (the first `WriteError` aborts before any
destructive stage; evidence is a returned issue URL, *"which cannot be produced by a no-op"*), and
**non-destructiveness** of `gh issue create`. **None of these is an authorization.**

## F2 — The unifying fact: the agent runs as the operator's uid, unsandboxed

Four independent corroborating measurements:

- **Writing outside the worktree:** `echo probe > ~/.yf-exp002-probe` -> `WROTE-OUTSIDE-WORKTREE`,
  **no prompt**.
- **`~/.claude/settings.json` is writable** (a symlink into `~/_dotfiles`; `test -w` true), and the
  deny list contains no file-write rule — so a session can edit the rules that constrain it.
- **Self-minted a cryptographically valid operator grant, in one command:**
  ```
  ssh-keygen -Y sign -f allowed.pub -n yf-landing grant.txt
  -> Good "yf-landing" signature for operator@yoshiko with ED25519 key SHA256:ZXUvjgT34jld…
  ```
  `ssh-add -l` shows a plain ED25519 key usable unattended. `grep sk-ssh-ed25519|sk-ecdsa
  ~/.ssh/*.pub` -> **no matches**: no FIDO/touch-required key exists on this machine. `op`, `gpg` and
  `security` are installed but each unlocks **per session**, not per authorization.

> **Therefore no purely local artifact is unmintable.** Every candidate reduces to one of three
> families: enforced by the harness, enforced by hardware presence (unavailable here), or enforced by
> a remote server.

## F3 — Candidate table

| Candidate | Verdict | Evidence |
| :-- | :-- | :-- |
| harness **ask** rule on `land --apply` | **worthless as configured; partially recoverable** | `ask: []` under `bypassPermissions`. An added `ask` entry *would* fire (deny and ask both survive bypass) — but the session can edit the file, and a bash-string glob is defeated by a wrapper script or a variable |
| **PreToolUse hook** returning `ask`/`deny` | **strongest harness lever; leaky** | fires *before* the permission-mode check and blocks even under `bypassPermissions` — but hook config is **watched and reloaded mid-session**, so the running session can disable its own gate. Claude-Code-only (violates GR-006 portability) |
| operator-written grant file | **DEAD** | fully session-mintable (F2) |
| signature / HMAC over plan id + fingerprint + digest | **DEAD as available** | self-minted a valid grant (F2). Alive only with presence hardware, which does not exist here |
| out-of-band reply via `herdr agent prompt` | **DEAD as provenance** | `herdr api schema --json`: `origin`, `provenance`, `actor`, `author`, `issued_by`, `client_id` all occur **0 times**. `herdr agent list` succeeded with no auth, returning every pane id; a prompt arrives as pty input, indistinguishable from typing |
| **detection** — record who and by what route | **VIABLE, better than expected** | Claude Code's transcript JSONL already carries provenance: `origin = {"kind":"human"}` (673) vs `{"kind":"task-notification"}` (229); `promptSource ∈ typed(664) / system(229) / queued(9)`. `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` are set and forgeable (`env -u` strips them) — but **asymmetrically**: their presence is agent evidence an agent must actively erase |
| splitting outward writes out of the batched grant | **orthogonal, buys nothing** | under `bypassPermissions` the individual gates are also just flags — six mintable flags instead of one, at the cost of the attrition #301 correctly names as *"the precondition for #293"* |
| **controlling-terminal gate** (`/dev/tty`) — *found by spike, not on the brief* | **structural and portable; evadable in ~15 lines** | measured inside a Claude Code Bash subprocess: `stdin isatty: False`, `stdout isatty: False`, **`/dev/tty NOT openable: OSError [Errno 6] Device not configured`** — the agent process has **no controlling terminal**. Evasion measured: `pty.fork()` + feed the string -> `EVASION child exit: 0`. Hardening measured: the forged terminal is a *distinct* pts (`os.ttyname(0)` -> `/dev/ttys007`), and herdr's `PaneProcessInfo` exposes a per-pane `tty`, so an allow-list can come from the herdr server rather than a session-writable file |
| **remote enforcement** — GitHub branch protection / rulesets | **the only genuinely off-machine lever; absent and admin-removable** | `gh api …/branches/main/protection` -> `{"message":"Branch not protected","status":"404"}`. `gh auth status` scopes include `repo`, which administers protection — but a deletion is recorded in GitHub's **off-machine audit log**, in a store the session cannot rewrite |

## F4 — VERDICT: #301's structural claim is overstated, and the hole is real

#301 says the agent *"cannot fabricate an authorization, because it never issues a write."* That is
**true of the `lander` sub-agent and false of the system.** The three-layer table assigns
`land --apply` to a column headed *"the only layer that writes"* — but **never names who invokes that
layer.** Under `--autonomous` the invoker is the main session, which:

- produced `decision.json`, by dispatching the lander it chose to dispatch on facts it chose to
  gather;
- can **edit** `decision.json` after the lander returns — an ordinary same-uid file;
- types `land --apply` with no artifact required beyond argv, exactly like
  `--allow-permissions-write`, `backfill --apply` and `push --apply`.

**So the split converts "one agent that decides and acts" into "one agent that decides, delegates the
write to a script it invokes, and acts." The write authority is unchanged.**

**What IS genuinely gained, and is what the issue should claim:** #293's specific artifact — a
free-text close reason asserting authorization — is eliminated, because `land --apply` re-derives
conditions mechanically and **generates** its own close reasons. `resolve-start-gate` already
demonstrates the pattern (`_start_gate_close_reason`): a generated reason **cannot contain a
fabricated claim about the operator**. That is real and worth shipping.

**What is not gained:** an answer to *"the same session that would benefit is the session that
types the command."* On that question the split is **procedural, not structural** — it moves the
defect exactly one layer up, from `bd close -r` to `land --apply`.

## F5 — And `land --apply` is strictly WORSE than the gate it replaces, on blast radius

#293's gate guarded one local, reversible, **unpushed** rewrite. `land --apply` pushes `main`, posts
upstream comments, closes and files issues, deletes branches and worktrees, and redeploys the
installed toolchain. **Batching those behind one first-party flag creates, in the issue's own words,
"a second, larger version of that."**

## F6 — The FULL-tier control is strong and orthogonal; ship it regardless

*"Never proceed past a red FULL tier"* is a **verification** control, not a consent one, and it is
the `upstream.py` pattern: fail-closed, structurally verified, non-scrapeable. It is what makes a
self-authorized landing **survivable** — a different and far more achievable goal than making one
impossible.

## CORRECTION (red-team pass 1): row 2's herdr predicate is withdrawn

> **Recorded rather than silently edited.** The recommendation table below originally specified the
> tty gate as *"refuse unless `os.ttyname(0)` is a real tty matching a pane herdr reports as
> **human-attached**"*. Red-team pass 1 measured that `herdr api schema --json` contains **zero**
> occurrences of `human` and **zero** of `attached` — that is not a capability herdr has, so the
> predicate would have degraded to "matching *any* herdr pane".
>
> Worse, `herdr pane run <pane> <cmd>` runs a command in a pane with a **genuine pty**. This
> finding priced evasion at *"`pty.fork()` in ~15 lines"* and called the act "unmistakable"; it is in
> fact **one sanctioned tool call**, and the resulting tty appears in herdr's own list. **F3 of this
> very finding measured that `herdr agent list` needs no auth and that injected input is
> "indistinguishable from typing" — so the finding contained the refutation of the mechanism it
> recommended, and did not notice.**
>
> The plan now specifies the gate as **pure POSIX** (refuse when `os.ttyname(0)` raises or
> `/dev/tty` is unopenable), makes any allow-list **operator-configured** rather than herdr-derived,
> and names `herdr pane run` as a **known bypass** in the SPEC. Read row 2 below with that
> substitution.
>
> **The correction also covers the F3 candidate table's evidence cell**, which still reads *"herdr's
> `PaneProcessInfo` exposes a per-pane `tty`, so the allow-list can come from the herdr server
> rather than a session-writable file."* That is the refuted claim, in the row that supplied it. A
> cold reader of this finding alone would otherwise reach the withdrawn conclusion from evidence the
> correction did not name.

## Recommendation adopted by this plan: 1 + 2 + 3, honestly labelled

| Rank | Mechanism | Guarantees | Does **NOT** guarantee |
| --: | :-- | :-- | :-- |
| **1** | **Do not give the session the verb.** `land --dry-run` + the lander produce `decision.json`; the session **stops** and prints the exact `land --apply` command for the operator to run in their own shell | the write never occurs in the session's address space. **Genuinely structural — the only row that is** | nothing, if a future rule lets the session run it "when autonomous". The guarantee is the *absence of the capability* |
| **2** | **Controlling-terminal gate** on `land --apply`: refuse unless `os.ttyname(0)` is a real tty matching a pane herdr reports as human-attached. Fail-closed, exit 3, legible reason | portable pure-POSIX (satisfies GR-006), costs an operator nothing, and is **measured to refuse the agent by default**. Enforces row 1 mechanically rather than by convention | prevention against a *deliberate* evader — `pty.fork()` defeats the naive form. It converts self-authorization from a **rationalizable** act into an **unmistakable** one. Label it *"raises the cost and removes the excuse"*, never *"prevention"* |
| **3** | **Route record**: stamp every gate close and every `--apply` with tty (or its absence), `CLAUDECODE`/entrypoint presence, pid/sid. `audit-close` FAILs a `Type: human` gate whose record says "no tty, `CLAUDECODE` set" | would have surfaced #293 **within seconds**. Cheap, additive, no new privilege. Closes the collapsed-signal defect directly by giving the two cases **different artifacts** | prevention, at all. Markers are strippable. **Asymmetric**: a clean record is weak evidence of a human; a **dirty** record is strong evidence of an agent. Ship it labelled *"detection, not prevention"* in the SPEC text, verbatim |

**Deferred, not built:** GitHub rulesets on `main` (correct scope, off-machine audit, but
admin-removable and guards `main` only) and the PreToolUse hook (defense in depth; Claude-only;
self-disabling).

**Explicitly NOT to be built:** the signed grant, the operator-written grant file, and herdr-provenance
consent. All three are measured session-mintable. Shipping any would put a **cryptographic veneer on
a first-party assertion** — strictly worse than #293, because the artifact would *look* unforgeable.
Revisit the signed grant only if a FIDO `sk-` touch-required key or a Secure-Enclave signer exists.

## Absence findings

- **No FIDO/touch-required ssh key on this machine** (`grep sk-ssh-ed25519|sk-ecdsa ~/.ssh/*.pub` ->
  no matches), so hardware-presence authorization is unavailable, not merely unbuilt.
- **No provenance field of any kind in herdr's API schema** — six candidate names, zero occurrences.
- **No branch protection on `main`** — `404 Branch not protected`.
- **No file-write deny rule** in this machine's Claude Code settings.

## Implications for Plan

**measured:** no purely local artifact is unmintable, because the agent runs as the operator's uid,
unsandboxed, under `bypassPermissions`. A signed grant, a grant file and herdr-provenance consent are
therefore not candidates — they are veneers.

**measured:** #301's structural claim does not hold for the system, only for the sub-agent. The plan
must not inherit the claim, and the issue's text should be amended rather than closed against it.

**inferred:** `land --apply` has a larger blast radius than the gate #293 was filed against, so
guarding it *better* is the wrong move; withholding it from the session is the right one.

## Recommendations

1. Do not give the session the verb: dry-run plus lander, then stop and print the command.
2. Add the controlling-terminal gate, labelled "raises the cost and removes the excuse".
3. Add the route record, labelled "detection, not prevention" in the SPEC text verbatim.
4. Ship the FULL-tier revalidation regardless — it is orthogonal to consent and makes a
   self-authorized landing survivable.
5. File the residue so #301 cannot close claiming a fix it does not deliver.

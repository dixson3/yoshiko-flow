---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-herdr-push-verification
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-005 — Live verification of the herdr child→parent push contract (D-5)

**Question:** Do the three inferred assumptions in the push design actually hold?
**Method:** live experiments in **throwaway** tabs (`wK:tE/tF/tG`, agents `e5a/e5b/e5c`), all created and closed by the experiment. `plan-044` and the parent pane were never touched.

## All three assumptions CONFIRMED

### 1. `tab create --env KEY=VALUE` reaches the agent process — YES, triple-corroborated

```
herdr tab create ... --env YF_TEST_PARENT=wK:p1
herdr pane run wK:pE 'echo "E5_ENV_READBACK=[${YF_TEST_PARENT:-UNSET}]"'
  → E5_ENV_READBACK=[wK:p1]
```

Corroborated by `printenv` (real process env, not shell interpolation) and — the load-bearing
one — a **grandchild** process inheriting it (`python3 -c 'os.environ.get(...)'` → `wK:p1`), which
is what a `claude` launched in that pane does. `--env` is repeatable.

**Bonus:** herdr already injects `HERDR_ENV`, `HERDR_PANE_ID`, `HERDR_TAB_ID`,
`HERDR_WORKSPACE_ID`, `HERDR_SOCKET_PATH` natively.

### 2. A push to a WORKING agent is QUEUED, not lost — the load-bearing result

Round 5, decisive: agent put in a genuinely **blocking foreground** tool call (`python3 -c
"time.sleep(45)"` — Claude Code refuses a bare foreground `sleep`, which is why earlier rounds got
backgrounded and were inconclusive). Status polled to `working` **before** sending.

Pane snapshot 8 s later, mid-tool-call:

```
✽ Processing… (20s · ↓ 132 tokens)
  ❯ PUSH-MIDTOOL: reply with exactly R5-MIDTOOL-OK when you can
───────────────────────────────────────────────────
❯ Press up to edit queued messages          ← explicit queuing evidence
```

After the tool call returned, **both** tokens emitted: `ROUND5-DONE` and `R5-MIDTOOL-OK`.

Corroborating rounds: a push 1 s into a turn delivered as its own transcript turn; **three** pushes
at T+0/+2/+4 s all delivered **in send order**, none coalesced or dropped; and a full end-to-end
child→parent run where the child, given only `YF_TEST_PARENT_NAME` via `--env`, ran
`herdr agent prompt "$YF_TEST_PARENT_NAME" …` from inside its own Bash tool and the parent replied.

> **Honest limit:** the queuing is **Claude Code's TUI behavior, not herdr's**. `agent prompt` is
> keystroke injection; the queue lives in the claude harness. A non-claude `--kind` may not queue
> the same way — **untested**.

### 3. `-- --append-system-prompt` works with no readiness penalty

```
herdr agent start e5a --kind claude --pane wK:pE -- --append-system-prompt "…"
  → interactive_ready:true, argv echoed correctly, 3.016s total  (30s default timeout)
```

Control: a plain `agent start` took **3.061 s** — the passthrough adds ~0 ms. The appended prompt
demonstrably took effect (the agent returned a codeword existing nowhere else).

**This is the right home for the child's push protocol — it survives context compaction, where a
first-turn instruction may not.**

## Two hazards the design must handle

### A. `--wait --until idle` is WRONG for claude — it times out on success

Measured: `--wait --until idle --timeout 120000` returned
`{"error":{"code":"timeout"}}` after **2:00.07** — *even though the agent had completed the turn
and answered correctly*. **A completed claude turn settles at `done`, never `idle`.** Use the
default `--wait` (which matches `idle|done|blocked`), or — as the design does — omit `--wait`.

### B. `agent_prompted` is acknowledgement of INJECTION, not SUBMISSION

The very first prompt to `e5a`, issued 0.5 s after `agent start` returned
`interactive_ready:true`, returned a successful `{"type":"agent_prompted"}` — but the pane showed
the welcome screen with an **empty composer and no turn**, and the transcript contains only the
retry's copy. **The message was accepted by the API and never submitted.**

**Failed to reproduce** (a deliberate immediate-prompt retry on a fresh tab landed fine), so:
*inferred, uncorroborated, n=1* — a transient race between herdr's readiness detection and the
claude TUI's first paint.

> **Do not build the design on `agent prompt` returning `agent_prompted` as proof of delivery.**

## `report-metadata --token` is a viable zero-cost side-channel

After writing `--title`, `--display-agent`, two `--state-label`s and two `--token`s,
**`herdr pane get`**, **`herdr agent get`**, and **`herdr agent list`** all return:

```json
"display_agent":"E5-DISPLAY",
"state_labels":{"idle":"E5 RESTING","working":"E5 CHURNING"},
"title":"E5 TITLE",
"tokens":{"yf_parent":"wK:p1","yf_role":"child"}
```

`herdr tab list` does **not** surface them. Metadata persists across turns.

> **A push costs the parent a turn; a token write costs it nothing.** This is the natural backstop
> for hazard B and for a push into a `blocked` parent.

**CLI gotcha:** despite the usage string showing `[OPTIONS] <PANE_ID>`, the **`<PANE_ID>` positional
must come FIRST** — `report-metadata --source X --title Y wK:pE` fails with `unknown option`.

## A child can discover its own name

No env var carries it and `herdr pane current` omits it, but:

```bash
herdr agent get "$HERDR_PANE_ID" | jq -r .result.agent.name
```

Verified independently. **`name` exists only for agents launched via `agent start`** — of 11 agents
listed, only 4 had one. `agent prompt` accepts either the name or the pane ID as `<TARGET>`.

## Design implications

1. **The core mechanism is sound end to end** — env handoff + fire-and-forget push + queued
   delivery + self-name discovery all verified.
2. **Prefer the pane ID as the target, or pass both.** `HERDR_PANE_ID` is injected automatically
   and is stable; `name` only exists for `agent start`-ed agents and can go stale on rename.
3. **Omit `--wait` entirely** (hazard A) — which the design already does.
4. **Treat `agent_prompted` as best-effort** (hazard B): pair each push with a
   `report-metadata --token` write, so a lost push is still recoverable on the parent's next poll.
5. **Bake the push protocol into `--append-system-prompt`** — free, and compaction-proof.
6. **Remaining untested risk: pushing to a `blocked` parent.** Must be tested before shipping;
   the token side-channel is the mitigation if it turns out to be swallowed.

## Cleanup

All three tabs closed; post-cleanup inventory matches pre-experiment exactly (11 tabs, 11 panes,
9 agents, no `e5*` residue). Temp files removed. **`plan-044` (wK:pD) was never prompted, stopped,
closed, or written to** — it transitioned `working → idle` on its own. `wK:p1` was never prompted.
No `herdr server stop` or `reload-config`. All tabs created `--no-focus`; focus never stolen.

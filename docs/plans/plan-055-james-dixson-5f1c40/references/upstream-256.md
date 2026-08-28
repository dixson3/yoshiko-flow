---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #256: check-harness-smoke: the state model is missing 'installed but consent-gated' — codex reaches INCONCLUSIVE for the wrong reason

- **Number:** 256
- **Title:** check-harness-smoke: the state model is missing 'installed but consent-gated' — codex reaches INCONCLUSIVE for the wrong reason
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The gap

`check-harness-smoke.sh` (plan-054 Issue 2.5, backing SC18) models a harness as **drivable or
absent**:

```
EXIT  0 both harnesses pass  ·  1 an assertion failed  ·  2 could not run (harness absent)
```

Measured while running the plan-054 skew test in real herdr tabs, there is a **third state**:
*installed, on PATH, authenticated — and still not drivable without interactive consent.*

`codex` required **three** consecutive dialogs before it would accept a prompt:

1. OAuth browser sign-in (unauthenticated).
2. **Directory trust** — *"Trusting the directory allows project-local config, hooks, and exec
   policies to load."*
3. **Hooks** — *"1 hook is new or changed. Hooks can run outside the sandbox after you trust
   them."* Options: review / trust all / continue without trusting.

`pi` and `opencode` needed none of these, so the smoke's binary model has never been exercised
against a harness that gates on consent.

## Why it matters for SC18 specifically

SC18 gates a tag push that is irreversible **and** auto-publishes the website, and the gate's
own condition says an INCONCLUSIVE **blocks**. That posture is correct and should not change.
The problem is that a consent-gated harness reaches exit 2 **for the wrong reason** — the
harness is present and healthy; a human simply has not clicked through. The verdict is right by
accident, and the operator is told "could not run (harness absent)" about a harness that is
demonstrably installed.

The accidental-correctness is the defect. A state that is only ever right because it collides
with a different state's handling is one refactor away from being wrong.

## What a fix looks like

Distinguish, in the exit vocabulary or the verdict payload:

- `absent` — binary not on PATH.
- `not-authenticated` — present, refuses work pending a login.
- `consent-pending` — present and authenticated, blocked on an interactive dialog.
- `drivable` — accepted a prompt.

All non-`drivable` states remain INCONCLUSIVE for SC18's purposes; the value is in the message
the operator reads, and in a future run being able to say *"codex needs a click"* rather than
*"codex is absent."*

## Detection, honestly

There is no portable probe for "a TUI dialog is open" — the smoke would need to observe that its
prompt produced no response and report `consent-pending` as an inference, not a measurement. It
should say so in the output rather than asserting a state it cannot verify. A wrong-but-specific
diagnosis is worse than a vague accurate one.

## Note on how this was found

Three interactive consents were answered by hand to complete the test. **Option 3, "continue
without trusting", was taken on the hooks dialog** — the skew test does not need hooks, and
granting out-of-sandbox execution is not a decision a delegating session should make on an
operator's behalf. Recorded because it is a variable in that run's result, though it should not
affect a `SKILL_DIR` resolve.


---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #202: bd mol burn: a cancelled burn exits 0, so a scripted burn cannot detect it

- **Number:** 202
- **Title:** bd mol burn: a cancelled burn exits 0, so a scripted burn cannot detect it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The defect

A cancelled `bd mol burn` **exits 0**. A scripted caller reading the exit code concludes the burn
succeeded when nothing was burned.

Without `--force`, `bd mol burn` prompts `Continue? [y/N]`. In a non-interactive context stdin is
empty, the prompt defaults to **No**, and the command prints `Canceled.` — then returns **0**.

## Reproduction

Poured a molecule with an open gate, then burned it non-interactively:

```
$ bd mol burn <molecule> < /dev/null
Use 'bd mol squash' instead if you want to preserve a summary.

Continue? [y/N] Canceled.
$ echo $?
0
```

The molecule was still present afterwards, `status: open`, with its gate still `open`.

## Why it matters

Any scripted burn is affected. The natural pattern —

```bash
bd mol burn "$WISP" && echo "cleaned up"
```

— reports success on a molecule that was never touched, silently **orphaning** it. The orphan then
persists in `bd ready` and in any enumeration that walks open molecules.

The correct call is `bd mol burn <id> --force`, **checking the output rather than the exit code**.
That is a real mitigation but an unfortunate one: it asks every caller to parse prose because the
exit code is unreliable.

## Suggested fix

Return a non-zero exit on cancellation. "The user declined" and "the work completed" are different
outcomes and should not share an exit code. A distinct code (e.g. 2) would let callers tell
*cancelled* from *failed* as well.

Found while executing plan-051-james-dixson-2f499f (Issue 4.6), which ships a formula whose
documented teardown is a scripted burn — the header records the `--force` + check-the-output rule
so the reason survives, but the underlying defect belongs upstream.


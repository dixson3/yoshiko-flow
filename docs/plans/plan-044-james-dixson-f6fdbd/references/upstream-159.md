---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #159: yf doctor --repair --remove-remote reports ok but does not remove the Dolt remote

- **Number:** 159
- **Title:** yf doctor --repair --remove-remote reports ok but does not remove the Dolt remote
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Symptom

`yf doctor --repair --local-only --remove-remote` reports success for the remote-clearing step while leaving the Dolt remote configured.

Measured 2026-08-17 on `dixson3/yoshiko-flow` (`dolt.local-only = true`):

```
$ yf doctor --repair --local-only --remove-remote
  [ok  ] (native) clear Dolt sync.remote under local-only (--remove-remote)
beads status after repair: ok

$ bd dolt remote list
origin               git+https://github.com/dixson3/yoshiko-flow.git   # still there
```

Removing it actually required a separate, undocumented-in-this-path step:

```
$ bd dolt remote remove origin
Removed remote "origin"
```

## Root cause

The flag operates on **two distinct layers** but only touches one. Its own help text claims both:

> `--remove-remote`  With `--repair` under local-only context, also CLEAR any configured Dolt remote **/** `sync.remote`

- `sync.remote` — a bd config key. This is what gets cleared.
- the **Dolt-layer** remote (`bd dolt remote`) — untouched.

In this repo `sync.remote` was **not set at all** (`sync.remote (not set in config.yaml)`), so the step was a no-op that still reported `ok`. Exit 0 and a green line are not evidence the remote is gone.

## Why this matters beyond one repo

The `yf-beads-upstream` skill names this exact command as **the** remedy for a stray Dolt remote:

> a local-only repo holds no Dolt remote; a stray one wedges bd 1.1.0's remote-migrate gate (clear it with `yf doctor --repair --local-only --remove-remote`)

An operator following that guidance sees a green report and still has the remote — and therefore still has the wedge the guidance was meant to prevent.

## Suggested fix

Either extend the step to clear the Dolt-layer remote (`bd dolt remote remove <name>` for each configured remote), or narrow the help text to say `sync.remote` only and update the `yf-beads-upstream` guidance to name the second command. The first is preferable — the flag's stated purpose is "assert local-only", which a lingering Dolt remote contradicts.

Verification should be **structural**, not exit-code-based: re-read `bd dolt remote list` after the repair and fail the axis if non-empty under `--local-only`.

## Related

Same defect class as #136 (reconciler reported success without performing the `gh` writes) and the `bd github push --dry-run` "Pushed N issues" false signal fixed in plan-040 — a green signal over a step that did not run.


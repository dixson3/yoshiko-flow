---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #239: pi's project-trust gate is unexercised by any test or smoke

- **Number:** 239
- **Title:** pi's project-trust gate is unexercised by any test or smoke
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

**pi's project-trust gate is unexercised by anything in this repo.** pi prompts before
operating in an untrusted project directory, and no test, no smoke and no manual procedure
covers what `yf`-deployed skills do when that gate is closed.

## Why it matters

plan-054 added a live headless pi regression, and it runs in a directory pi already trusts.
That is the friendly path. The unfriendly path — first run in a fresh clone — is the one a new
user hits, and it is the one nothing measures. A skill that silently fails to load under an
untrusted project would look identical to a skill that loaded and had nothing to say.

## Scope

- Determine what pi actually does with a skills bundle in an untrusted directory (measured
  against the installed binary, not the docs).
- If skills do not load, decide whether `yf` should detect and report it — a `yf doctor` axis
  is the obvious home — rather than leaving the user to infer it.

Discovered by plan-054 (release-readiness pass), out of scope for that plan.


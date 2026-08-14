---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #59: Follow-on (plan-018): on-disk content materialization seam + Windows targets

- **Number:** 59
- **Title:** Follow-on (plan-018): on-disk content materialization seam + Windows targets
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Deferred scope from **plan-018** (decision 7 + Windows; not built in that plan).

## On-disk content materialization (decision 7)
Today rust-embed content deploys only to `.claude/skills` / `.agents/skills`. Add a configurable
materialization target defaulting to that, optionally `~/.local/share/yf/...`. The Epic-2 dirs
module already carries the `~/.local/share/yf` data path (`Dirs::data_dir()`), so the seam lands
cleanly — design the dirs/knob is done; implement the feature separately.

## Windows targets (decision 4)
Add the Windows release target(s) to the cargo-dist matrix, finalize + test the dirs module's
Windows arm (currently a `cfg(windows)` stub), and ship the cargo-dist `.ps1` installer.

Tracked locally as bead `yf-d4x3`.

# Plan: Restore otel_agent telemetry on CT 107

**ID:** plan-014-james-dixson-763edc
**Status:** review

## Objective

Find and fix the reason CT 107's `otel_agent` stopped shipping telemetry, and close the
gap that let it go unnoticed for a day.

## Investigation Findings

### EXP-001 — otel fleet live state

#### 4. The timeline pins it to a container reboot

- CT 107 **rebooted 2026-08-12 03:48:04 UTC** (`uptime -s`; up 23 h 38 m at time of measurement).
- Telemetry stopped ≈ **2026-08-12 03:47 UTC** — **about one minute before the reboot**.
- The CT's own journal begins `2026-08-12T03:48:06` — i.e. at that boot.
- `journalctl -u otel_agent` → **"No entries"**; `ActiveEnterTimestamp` is **empty**;
  `NRestarts=0`.

**The agent went down with the reboot and never came back.** The unit is `enabled`, so it should
have been pulled in at boot; it was not, and produced no journal record of trying. At that moment
the EnvironmentFile did not yet exist (created ~23 h later, per §1), which is the obvious suspect —
but the absence of *any* journal entry does not match a normal `EnvironmentFile`-missing start
failure, so the precise boot-time mechanism is **not yet pinned** and is a task for the plan, not a
settled fact.

## Approach

The failure is a **silent regression**: a healthy guest that broke at a reboot with no signal.
The plan therefore targets the boot-start path — why an `enabled` unit did not start at boot —
and adds an alert so a silent stop is caught within an hour rather than a day.

## Epics

### Epic 1: Reproduce the boot-start failure

- **Issue 1.1:** Reboot CT 107 under observation and capture the boot-time journal, to
  reproduce the `enabled`-unit-did-not-start behaviour.
- **Issue 1.2:** Reboot the postgres guest the same way to confirm the failure generalises
  beyond CT 107.

### Epic 2: Fix the boot-start path

- **Issue 2.1:** Correct the unit ordering so `otel_agent` starts after its EnvironmentFile
  is present.
  - depends-on: 1.1

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | A reboot of CT 107 brings `otel_agent` up automatically | `systemctl is-active otel_agent` after a reboot |
| SC2 | The boot-start regression cannot recur silently | an alert fires within 1 h of telemetry stopping |

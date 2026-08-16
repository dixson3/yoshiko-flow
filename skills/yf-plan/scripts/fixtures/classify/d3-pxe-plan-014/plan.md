---
deliverable_class: standard
source_plan: plan-014-james-dixson-763edc
source_repo: d3-pxe
---
# Plan: Close out A–D — fail-closed otel enrolment with arrival proof, data-driven scrape targets, idmap tiling, subid derivation

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :---- | :---- | :---------- | :---- | :---------- |
| [#68](https://github.com/dixson3/d3-pxe/issues/68) | otel_agent enrolment fails OPEN: postgres enabled-but-inactive | include | Premise corrected by EXP-001 — it is a silent regression, not a never-enrolled guest. Issue must be updated at reconcile, not merely closed. Completes at **3.4** — the time-based half is not proven until the alert is | 1.1–1.6 → 3.4 |
| [#71](https://github.com/dixson3/d3-pxe/issues/71) | otel_agent: generalize the Prometheus scrape to a target list | include | Cost now lower — #57's `/tmp` noise is gone, so fleet-wide zero-delta proofs are readable. Authored in 2.1/2.2; **resolved at 3.3**, since a generalization is not resolved until it is applied and verified live | 2.1, 2.2 → 3.3 |
| [#69](https://github.com/dixson3/d3-pxe/issues/69) | ansible_ledger_check: assert idmap TILING for the 7 existing guests | include | EXP-002: all 7 already tile. Purely additive — a regression guard, not a bug fix | 4.1, 4.2 |
| [#70](https://github.com/dixson3/d3-pxe/issues/70) | ansible_ledger_check: reconcile shared_ids against subuid/subgid | include | Two-part: derive the delegations, and assert the derivation | 5.1, 5.2 |
| [#53](https://github.com/dixson3/d3-pxe/issues/53) | otel_agent on plex never started | partial | Both instances are healthy now (EXP-001 measured 0.2 min ago). The *class* fix lands here; the issue closes only if the operator agrees the instance-level report is subsumed | 1.3, 1.5 → 3.3 |
| [#54](https://github.com/dixson3/d3-pxe/issues/54) | otel_agent on calibreweb never started | partial | Same as #53 — measured healthy at 1.0 min ago | 1.3, 1.5 → 3.3 |
| [#47](https://github.com/dixson3/d3-pxe/issues/47) | SPEC: require OTEL telemetry from new guests | exclude | Normative SPEC authoring, untouched here. plan-013 already delivered the scaffold's app-level decision field | — |
| [#33](https://github.com/dixson3/d3-pxe/issues/33) | Epic: *arr media stack | exclude | The driver for this plan's timing, not something it resolves | — |

## Epics

### Epic 1: Fail-closed otel_agent enrolment with arrival proof (B, #68)

- **Issue 1.1:** Pin the boot-time root cause. An `enabled` unit produced **no journal entry** at
  boot and left `ActiveEnterTimestamp` empty. The obvious suspect is the then-missing
  `EnvironmentFile`, but a missing `EnvironmentFile=` normally produces a *failed* start with a
  log line, not silence — so the mechanism is not yet established. Read-only diagnosis; no fix.

  **The original evidence is largely gone**: the CT 107 journal begins at that same boot, the agent
  has since been started manually, and the EnvironmentFile now exists. If the mechanism cannot be
  read from surviving evidence, **reproduce it deliberately on `garage-webui`** — stateless,
  bindless, nothing depends on it — by removing its EnvironmentFile and rebooting, rather than
  experimenting on CT 107. Only if reproduction also fails does R1's defensive-fix path apply.
- **Issue 1.2:** Fix the boot-start defect in the `otel_agent` role, as 1.1 determines (systemd
  dependency ordering, an `EnvironmentFile=-` optional-prefix change, a `RestartSec`/`Restart`
  policy, or some combination). Authoring only — **not applied here** (Epic 3).
  - depends-on: 1.1
- **Issue 1.3:** Fail-closed converge-time enrolment assert, added to **`roles/otel_agent/tasks/service.yml`**
  (the task file that already owns enable/start), so it runs on every `otel_targets` member as part
  of the normal converge rather than as a separate opt-in play. Must **not** key on `is-enabled` or
  `Result` — EXP-001 measured `Result=success` on a unit that never executed. Key on
  `ActiveEnterTimestamp` being non-empty plus the unit being `active`, and fail the converge
  otherwise.

  **Gate the assert on `otel_agent_apply_service`, and order it strictly AFTER the start task.**
  `service.yml`'s design is *enable always, start only on the apply path*, so on an ordinary
  non-apply reconcile a target's agent may legitimately be un-started — an unconditional assert
  would fail every such converge, and would self-block Issue 3.2's apply against the very CT 107 it
  is fixing. Assert that enrolment *succeeded* only where the run actually attempted to start it.
  On a non-apply reconcile it is a no-op, never a failure; under `--check` likewise. Authoring only.
  - depends-on: 1.1
- **Issue 1.4:** Establish the metrics-stream query shape. The logs query works; the identical
  shape against `system_cpu_load_average_1m` returns **HTTP 400**. Determine the correct form (or
  establish that metrics streams cannot serve this) and record it, since 1.5 depends on the answer.
- **Issue 1.5:** Committed OpenObserve **absence alert** — fires when any `otel_targets` member
  stops reporting. Built on `hostmetrics` per D4 if 1.4 succeeds, else a logs-based alert with a
  window sized for the quietest guest. Must not false-positive on `calibreweb`/`garage-webui`
  (measured at 30.4 min between records). Ships as IaC alongside the dashboards in
  `roles/openobserve/files/`, provisioned upsert-safe like `tasks/dashboards.yml`.

  **The alert MUST have a delivery destination that reaches the operator outside the OpenObserve
  UI.** An alert that fires into a dashboard nobody opens reproduces the original failure with extra
  steps — the whole defect here was that nothing told anyone. Determine what OpenObserve supports in
  this deployment (webhook, SMTP email) and wire one; if no destination can be delivered, that is a
  **blocker to report**, not a detail to defer.

  **If no destination is deliverable, the plan does not silently proceed on one control.** D1's
  whole argument is that a converge assert cannot catch a time-based failure — so a UI-only alert
  leaves #68's time-based half open while every criterion except SC3 still passes. Stop and let the
  operator choose: provision a destination (SMTP/webhook), accept a UI-only alert with the
  limitation recorded in AGENTS.md, or descope the alert and reopen #68's time-based half as a
  tracked follow-up.
  - depends-on: 1.4
- **Issue 1.6:** Arrival-proof helper — a script wrapping the verified `_search` query so "is every
  target shipping?" is one command, usable by 1.3, by Issue 3.3's post-apply verification, and by
  the operator ad hoc. Vault-authenticated, so **never** a `CHANGE-VALIDATION` row.
  - depends-on: 1.4

### Epic 2: Data-driven Prometheus scrape targets (A, #71)

- **Issue 2.1:** Replace `otel_agent_litellm_scrape_enabled` and its four siblings
  (`_endpoint`, `_interval`, `_metrics_path`, `_metrics_token`) plus the hardcoded `job_name:
  litellm` with `otel_agent_prometheus_scrapes: []` — a list of
  `{job_name, endpoint, metrics_path, interval, token_env}`. LiteLLM becomes one entry in
  `host_vars/litellm.yml`. Authoring only.
- **Issue 2.2:** Prove the generalization is backward-compatible **locally** — render
  `config.yaml.j2` for every target before and after and diff. A PVE-GUEST-002 (a) generalization
  requires existing render byte-identical; proving that by template render needs no fleet and no
  credentials, unlike a live `--check`.
  - depends-on: 2.1

### Epic 3: Single combined fleet apply (PVE-OBS-001)

- **Issue 3.1:** Produce the fleet-wide `--check --diff` evidence for Epics 1 and 2 **together** —
  `host.yml --tags otel_agent` and `guests.yml --limit lxc_guests`, with a before/after
  differential. **Ungated and read-only** (D2). Requires SSH to all 9 targets and the full secret
  env via `op run --env-file=ansible/secrets.env.tmpl` — the `POSTGRES_OTEL_PASSWORD` assert in
  `config.yml` is unconditional, so a credential-less `--check` fails outright. If the environment
  is unavailable, **stop and report** rather than fabricating the differential.
  - depends-on: 1.2, 1.3, 1.5, 1.6, 2.2
- **Issue 3.2:** Apply Epics 1 and 2 — **staged, not all at once**. Apply first to
  `garage-webui` alone (`--limit garage-webui`: stateless, bindless, nothing depends on it), then
  widen to the remaining guests and the pve host.

  **Verify stage one with LOCAL unit signals, not the arrival proof.** `garage-webui` is one of the
  two quiet guests (EXP-001: 30.4 min between records), so waiting on arrival latency would stall
  the stage for half an hour or push the operator to widen unverified. Check `systemctl is-active`,
  a non-empty `ActiveEnterTimestamp`, and the collector's own startup log showing its export
  pipeline built. The arrival proof belongs to the post-widening check in 3.3, where the chatty
  guests answer in under a minute. A
  single simultaneous apply risks taking the **entire observability layer** down at once on a
  malformed scrape list or a mis-firing assert — the exact blind spot this plan exists to close,
  self-inflicted at nine times the scale. `--limit` makes staging nearly free. Record the revert
  command in the issue so recovery is not improvised. **GATED** on the PVE-OBS-001 capability gate.
  - depends-on: 3.1
- **Issue 3.3:** Post-apply verification — run Issue 1.6's arrival proof and confirm **all 9
  targets** report recent telemetry, then **reboot CT 107** and confirm the agent returns
  automatically. The reboot is the only test that actually exercises the 1.2 fix; without it the
  fix is asserted, not proven. Operator-visible: a guest restart is a real, if brief, service
  interruption on the PostgreSQL host.

  **This is [#63](https://github.com/dixson3/d3-pxe/issues/63)'s exact scenario** — two unexplained
  transient CT 106 ↔ CT 107 connectivity failures, one of which caused a gateway outage, still open
  and unexplained. So the reboot MUST be followed by an explicit gateway-recovery check:
  `litellm` and `litellm-migrate` both active on CT 106, and a live request through
  `agents.dixson3.net` returning. plan-010 records that the cross-container dependency cannot be
  expressed in systemd and is handled by an `ExecStartPre` TCP wait plus `Restart=on-failure` —
  machinery that has never been deliberately tested against a real PostgreSQL restart. Done this
  way the reboot becomes the **first controlled test of #63's scenario**; done without the check it
  is an unannounced production incident.

  **The reboot proves the boot fix. It does NOT prove the alert.** A reboot lasts ~60 s; the alert's
  threshold must tolerate `calibreweb`/`garage-webui` at 30 min between records, so a 60 s outage
  cannot trip it. The two cannot be tested by the same event.
  - depends-on: 3.2
- **Issue 3.4:** Prove the absence alert fires **against its real production threshold**. After 3.3
  confirms the boot fix, deliberately stop CT 107's `otel_agent` and hold it stopped until the
  threshold elapses; confirm the alert fires *and is delivered* to the destination Issue 1.5 wired;
  then start it and confirm recovery. Operator-confirmed 2026-08-12 in preference to
  temporarily lowering the threshold, which would prove the mechanism but not the tuning — and the
  tuning is the part most likely to be wrong.

  **This deliberately blinds the guest the plan exists to protect** — a monitoring gap on the
  holder of the precious `pool1/postgres` dataset, which is the exact condition Epic 1 removes.
  It is defensible only because it is controlled, gated, operator-present, and unavoidable if the
  *real* threshold is to be exercised rather than a lowered stand-in. **Record the intended
  duration before starting.** Issue 1.4's outcome directly bounds it: ~5 min if the `hostmetrics`
  path works, ~1 h on the logs fallback — which is a second, concrete reason to do 1.4 carefully. The arrival proof's negative
  behaviour (SC4) is captured in the same window. Both are transient — capture them live, not
  reconstructed.
  - depends-on: 3.3
  - resolves-upstream: [#68](https://github.com/dixson3/d3-pxe/issues/68) (include),
    [#71](https://github.com/dixson3/d3-pxe/issues/71) (include),
    [#53](https://github.com/dixson3/d3-pxe/issues/53) (partial),
    [#54](https://github.com/dixson3/d3-pxe/issues/54) (partial)

### Epic 4: idmap tiling assertion (D, #69)

- **Issue 4.1:** Add a tiling assertion to `scripts/ansible_ledger_check.py` — every non-empty
  `idmap` must cover 0–65535 with no gap and no overlap on both the `u` and `g` axes. **Empty is a
  pass** for a bindless guest (PVE-GUEST-003), or the check fails closed on the three conforming
  guests that legitimately have `idmap: []`.
  - resolves-upstream: [#69](https://github.com/dixson3/d3-pxe/issues/69) (include)
- **Issue 4.2:** Prove it catches — inject a wrong tail, a gap, and an overlap into a scratch copy
  and confirm each fails with a useful message; confirm the unmodified tree stays green (EXP-002
  measured all 7 tiling correctly, so a red baseline means the checker is wrong, not the tree).
  - depends-on: 4.1

### Epic 5: Derive subuid/subgid from shared_ids (C, #70)

- **Issue 5.1:** Replace the hand-maintained `subuid_delegations` / `subgid_delegations` lists in
  `roles/pve_host/defaults/main.yml` with a derivation over `shared_ids`, filtered by axis — a
  `uid`-bearing entry yields a subuid delegation, a `gid`-bearing one a subgid delegation, and the
  gid-only `media` entry correctly yields **subgid only**. Must render byte-identical to the
  current lists.
  - resolves-upstream: [#70](https://github.com/dixson3/d3-pxe/issues/70) (include)
- **Issue 5.2:** Assert the derivation in `ansible_ledger_check.py` and prove byte-identical
  rendering, so a future hand-edit that diverges from `shared_ids` is caught. Adding a §6.1 id
  becomes a one-file edit.
  - depends-on: 5.1

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :- | :--- | :------- | :--------- |
| R1 | Issue 1.1 fails to pin the boot mechanism, leaving 1.2 a guess | high | 1.1 is explicitly diagnosis-only and separate from the fix. If it cannot establish the mechanism, 1.2's scope becomes "make the unit robust to *all* plausible causes" (optional EnvironmentFile prefix + explicit ordering + restart policy) and 3.3's reboot test becomes the arbiter. The reboot test is what proves it either way |
| R2 | The absence alert false-positives and gets ignored, leaving the same blind spot with extra noise | high | D4 prefers `hostmetrics` (fixed 30 s interval, activity-independent) precisely to avoid this; 1.4 proves the query before 1.5 builds on it; 1.5 explicitly must not fire on the two guests measured at 30.4 min. An alert that cries wolf is worse than none. Note the tension this creates with proving the alert at all: a threshold sized for a 30-min-quiet guest cannot be tripped by a 60 s reboot, which is why Issue **3.4** holds a deliberate outage rather than reusing 3.3's window |
| R3 | Rebooting CT 107 (3.3) is **[#63](https://github.com/dixson3/d3-pxe/issues/63)'s exact scenario** — an unexplained CT 106 ↔ CT 107 disruption that previously caused a gateway outage | high | Its **own** capability gate, separate from the config apply, because the blast radii differ. 3.3 carries a mandatory gateway-recovery check (`litellm` + `litellm-migrate` active, live request through `agents.dixson3.net`), so a recurrence is detected inside a controlled window instead of later. plan-010's untested `ExecStartPre` TCP-wait machinery gets its first deliberate exercise. Still the only test that exercises the 1.2 fix — asserting a boot fix without rebooting proves nothing |
| R9 | A staged apply (3.2) leaves the fleet briefly on two different `otel_agent` configs | low | Accepted and short-lived; the role is idempotent and the two configs differ only in the enrolment assert and scrape shape, neither of which affects export. Far cheaper than the simultaneous-apply failure it prevents |
| R4 | 3.1's evidence needs SSH to 9 targets plus the full secret env, and may be unobtainable | medium | Its own precondition, stated in the issue; on failure the instruction is stop-and-report, never fabricate. Epics 4 and 5 are wholly independent and still land |
| R5 | The Epic 2 generalization silently changes an existing render | medium | 2.2 proves byte-identical by local template render — no fleet, no credentials — before anything reaches 3.1. PVE-GUEST-002 (a) requires exactly this |
| R6 | #68 is closed as "fixed" while its written premise stays wrong, so the record misleads later readers | medium | The disposition table marks it **include with a corrected premise**; reconcile must post EXP-001's correction to the issue, not just close it. The same applies to #53/#54, whose instances are already healthy — closing them silently would imply this plan fixed something it found already working |
| R7 | Grouping B and A means a defect in either blocks the shared apply | low | Accepted as the cost of D3's single gate. Both are authored and locally proven before 3.1; if one proves unsound it can be reverted from the branch and the other applied alone |
| R8 | Manually starting CT 107's agent masks the defect during development | low | Recorded in EXP-001 as an out-of-band mutation and explicitly *not* the fix; 3.3's reboot re-exposes the original condition, so the proof does not depend on the pre-restart state |

## Success Criteria

1. **SC1** — Issue 1.1 records the boot-time mechanism, or explicitly records that it could not be
   established and what 1.2 does instead. A guess presented as a diagnosis is a fail.
2. **SC2** — The converge-time enrolment assert fails when a target's `otel_agent` is inactive or
   has an empty `ActiveEnterTimestamp`, **proven by injection**, and does **not** rely on
   `is-enabled` or `Result` (EXP-001 measured `Result=success` on a never-run unit).
3. **SC3** — A committed OpenObserve absence alert exists as IaC, is provisioned upsert-safe, and
   **does not fire** against the current fleet — including `calibreweb` and `garage-webui`, which
   legitimately go ~30 min between records — but **does fire, and is delivered to its destination**,
   during Issue 3.4's deliberate held outage against the **real production threshold**. An alert
   never observed firing is not known to work; one that fires only into a UI is not known to reach
   anyone.
4. **SC4** — The arrival-proof helper reports all 9 `otel_targets` members shipping, in one
   command. Its **negative** behaviour is proven during Issue 3.4's held outage — a real absence,
   captured live.
5. **SC5** — `otel_agent_prometheus_scrapes` drives the scrape config; `host_vars/litellm.yml`
   carries one list entry; the five `otel_agent_litellm_*` variables and the hardcoded `job_name`
   are gone.
6. **SC6** — Every target's rendered `config.yaml` is **byte-identical** before and after Epic 2,
   proven by local template render (PVE-GUEST-002 (a)).
7. **SC7** — Adding a second scraped service is a **data append**. Prefer a **real** target over a
   fixture, per plan-013's Prowlarr precedent: Caddy (CT 102) exposes Prometheus metrics natively
   and currently has no app-level observability, so it is both a genuine proof and a real gap
   closed. If enabling it turns out to need a Caddy config change, that is scope creep — fall back
   to a throwaway entry and **state the synthetic limitation explicitly** rather than presenting a
   fixture proof as equivalent.
8. **SC8** — Issue 3.1's evidence is committed under `findings/`, and the PVE-OBS-001 gate is
   resolved by the operator **after** reading it — never by an agent.
9. **SC9** — After the apply, all 9 targets report recent telemetry; **CT 107 is rebooted and the
   agent returns automatically**, verified by the arrival proof. This is the criterion that
   distinguishes a real fix from an asserted one. The same reboot must leave CT 106's gateway
   healthy — `litellm` and `litellm-migrate` active and a live request through
   `agents.dixson3.net` returning — or [#63](https://github.com/dixson3/d3-pxe/issues/63) has
   recurred and must be recorded as observed rather than waved through.
10. **SC10** — `ansible_ledger_check.py` fails on a wrong tail, a gap, and an overlap (each proven
    by injection) and passes on `idmap: []` for the three bindless guests.
11. **SC11** — `subuid_delegations` / `subgid_delegations` are derived from `shared_ids`, render
    byte-identical to the current lists, and `media` yields **subgid only**.
12. **SC12** — Adding a hypothetical §6.1 id requires editing **one** file, demonstrated and
    reverted.
13. **SC13** — The full `CHANGE-VALIDATION` FAST and FULL tiers pass on the merged tree; no
    vault-requiring or fleet-requiring command was added as a row.
14. **SC14** — #68, #71, #69, #70 closed with commit references; #68 additionally carries EXP-001's
    **correction to its premise**; #53/#54 dispositioned explicitly rather than silently closed.

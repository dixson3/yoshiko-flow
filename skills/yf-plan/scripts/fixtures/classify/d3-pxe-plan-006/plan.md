---
deliverable_class: standard
source_plan: plan-006-james-dixson-22bc0f
source_repo: d3-pxe
---
# Plan: Add OpenObserve self-hosted observability (OTEL stack) with Garage object store

## Upstream Issues
| Issue | Title                                  | Disposition | Notes                                                                                                                                                                                                               | Resolved By |
| :---- | :------------------------------------- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------- |
| #7    | Add SigNoz (self-hosted observability) | supersede   | Resolved with **OpenObserve** instead of SigNoz per operator decision + incubator research (OpenObserve is lighter, object-store-native, no ClickHouse/ZooKeeper). Same underlying need: OTEL-native observability. | plan-006    |

## Epics

### Epic 1: SPEC & ledger reconciliation (lands first)
- Issue 1.1: Amend **SPEC §8** — add `garage` (CT 103) + `openobserve` (CT 104) guest rows.
  **Add a new SPEC requirement** (e.g. `PVE-OBS-001` under §9) authorizing a **host-touching
  horizontal role** `otel_agent` that installs an OTEL collector agent onto the `pve` host **and**
  every guest — this is a host mutation and does NOT fall under PVE-GUEST-002 (guests-slotting-in);
  it needs its own provision (resolves red-team C7). State it layers on top and does not fork
  `pve_lxc`/`pve_host`.
- Issue 1.2: Claim identifiers — **SPEC §6.1** uid/gid 10004 (`garage`) + 10005 (`openobserve`)
  **and the matching `group_vars/all.yml` `shared_ids` entries** (garage 10004, openobserve 10005 —
  `check_shared_ids()` requires every §6.1 id to have a `shared_ids.<name>.{uid,gid}`; pass-2 C1);
  **RESERVATIONS.md** rows (CT 103/`.103`, CT 104/`.104`) + "next free" bump; **MOUNTS.md**
  datasets + binds — `pool1/garage` parent + `garage/data` + `garage/meta` child datasets, all
  **single-owner `10004:10004` mode 0700** (plex-config ownership, NOT media's shared
  `root:10000`/2775 — Garage is single-consumer; pass-2 C3), carried by **exactly one** `media_rbind`
  bind row (`/pool1/garage` → `/var/lib/garage`); and `pool1/openobserve-meta` (owner `10005:10005`,
  `config_bind` → `/var/lib/openobserve`). Preserves the `config_bind`/`media_rbind` var shape so
  `ansible_ledger_check.py` passes unmodified (resolves C1/C2).
  - depends-on: 1.1
- Issue 1.3: Add **SPEC §7** package rows (§7.6 Garage guest, §7.7 OpenObserve guest, §7.8
  `otel_agent` on host + guests) — install methods + version pins.
  - depends-on: 1.1
- Issue 1.4: Add three **RESERVATIONS "Service DNS names"** rows (observe/s3/console) and note
  the operator-published Route53 A records (admin creds, not the caddy least-priv DNS-01 key).
  - depends-on: 1.1
- Issue 1.5: Add `garage` + `openobserve` to `inventory/hosts.yml` (`lxc_guests` group) and
  create an `otel_targets` group (pve host + all guests) for the horizontal role; wire role→host
  bindings in `guests.yml`/`host.yml`/`site.yml` (resolves C3 inventory half).
  - depends-on: 1.1

### Epic 2: Garage object-store guest (CT 103)
- Issue 2.1: `host_vars/garage.yml` — identity, idmap (10004), the single `media_rbind`
  (`/pool1/garage` → `/var/lib/garage`, carrying `data`/`meta` child datasets), sizing. Provision
  the CT via `pve_lxc` (create-stopped → raw_conf → started per PVE-ANS-008).
  - depends-on: 1.2, 1.5 · Capability Gate: PVE apply
- Issue 2.2: **Bootstrap** the new CT via `ansible-playbook bootstrap.yml -e guest=garage`
  (installs python + sshd for SSH-direct) before any in-CT role (AGENTS.md; resolves C3 bootstrap
  half). Then **set the UniFi Fixed-IP reservation** for CT 103 `.103` in the UDM-Pro UI after the
  guest first appears (PVE-NET-005 operator step; resolves C5).
  - depends-on: 2.1
- Issue 2.3: `garage` app role (clone `caddy` shape) — pinned signed static binary via `get_url`
  + `checksum:`, `/etc/garage.toml` template **with single-node `replication_factor: 1`** (Garage
  defaults to 3 → layout won't converge / writes fail without this; resolves C10), systemd unit,
  `garage` system user, apply-gated start.
  - depends-on: 2.2
- Issue 2.4: Non-interactive provisioning — `garage layout assign/apply`, `bucket create
  openobserve`, `key create` + `bucket allow`, with `creates:`-style idempotency guards. **Push
  the freshly-minted scoped key into 1Password** (Ansible-authored, mirroring the `pve_token` role's
  secret-push + PVE-AUTH-003; idempotent — do not re-mint on re-converge; resolves C6). OpenObserve
  later reads it as a 0600 `EnvironmentFile`, never committed.
  - depends-on: 2.3

### Epic 3: OpenObserve backend guest (CT 104)
- Issue 3.1: `host_vars/openobserve.yml` — identity, idmap (10005), `pool1/openobserve-meta`
  `config_bind`, memory 2–4 GiB. Provision the CT via `pve_lxc`.
  - depends-on: 1.2, 1.5 · Capability Gate: PVE apply
- Issue 3.2: **Bootstrap** the CT (`bootstrap.yml -e guest=openobserve`) + set the UniFi Fixed-IP
  for CT 104 `.104` (PVE-NET-005). Then the `openobserve` app role (clone `caddy` shape) — pinned
  release binary, systemd unit (`LimitNOFILE=65535`), 1Password `EnvironmentFile` scoped to the
  **root password only** here (the `ZO_S3_*` secret is added in Issue 3.3, which depends-on 2.4 —
  pass-2 C2), apply-gated start.
  - depends-on: 3.1
- Issue 3.3: S3 storage config → Garage — `ZO_LOCAL_MODE_STORAGE=s3`, `ZO_S3_SERVER_URL=
  http://192.168.7.103:3900`, path-style (`ZO_S3_FEATURE_FORCE_HOSTED_STYLE=false`), region
  matching Garage. Retention: global floor 14d + per-stream tiers (logs/traces/metrics).
  - depends-on: 3.2, 2.4

### Epic 4: Integration smoke test (capability gate — the unverified Garage↔OpenObserve edge)
- Issue 4.1: Verify the full loop — emit sample OTLP → confirm Parquet objects land in the
  Garage bucket → query them back in OpenObserve, incl. a cold read of aged data. This gates
  making Garage OpenObserve's authoritative store.
  - depends-on: 3.3

### Epic 5: otel_agent horizontal role (acquisition)
- Issue 5.1: `otel_agent` role — install `otelcol-contrib`, templated `config.yaml` driven by
  `host_vars` (receivers: `journald` + `filelog` logs, `hostmetrics` metrics, OTLP for app
  traces; processors: `filter` OTTL + head `probabilistic_sampler`; exporter: OTLP →
  `192.168.7.104:5081`). **Decoupled from the Garage gate:** depends only on OpenObserve being up
  (3.2), not on the authoritative-store decision (4.1) — acquisition works regardless of whether
  storage is S3 or the local-disk fallback (resolves C11).
  - depends-on: 3.2
- Issue 5.2: Apply to every **guest** (`guests.yml`/`site.yml`) and, behind the host-apply gate,
  to the `pve` **host** (`host.yml`). **Verify `hostmetrics` under unprivileged LXC reports
  container-scoped (cgroup) values, not host-bleed** — confirm per-CT metrics before trusting them
  (resolves C9); if bleed occurs, restrict guest agents to `journald`/`filelog` + OTLP and scrape
  host metrics only from the pve-host agent. Confirm host + guest logs/metrics and app traces
  arrive in OpenObserve.
  - depends-on: 5.1 · Capability Gate: host otel_agent apply

### Epic 6: Caddy fronting (data appends)
- Issue 6.1: Append three `caddy_sites` entries (observe UI → `:5080`, s3 → Garage `:3900`,
  console → Garage `:3902`); set Garage public-URL env (console redirect / presigned host).
  Verify existing `calibre`/`plex` sites render byte-identical (SPEC §8 constraint).
  - depends-on: 3.3, 2.4
- Issue 6.2: Operator publishes the three Route53 A records; verify TLS issuance (LE DNS-01) and
  UI/console/API reachability through Caddy.
  - depends-on: 6.1 · Capability Gate: Route53 A records published

## Risks & Mitigations
- **R1 — Garage S3 semantics mismatch with OpenObserve** (young project; "S3-compatible ≠
  compatible"). *Mitigation:* Epic 4 smoke-test gate before authoritative cutover; version-pin
  Garage; fallback = OpenObserve local-disk mode + defer Garage.
- **R2 — OTLP/gRPC through Caddy edge cases.** *Mitigation:* SD-6/EXP-004 decision keeps OTLP
  **direct-to-guest**; Caddy fronts UI only. Removed from critical path.
- **R3 — Retention footgun (OpenObserve 10-year default).** *Mitigation:* set global floor +
  per-stream tiers explicitly in Issue 3.3; verify effective retention post-deploy.
- **R4 — journald receiver namespace** (shells out to `journalctl`). *Mitigation:* per-LXC agent
  reads its own journal; ensure `journalctl` present in each agent's namespace.
- **R5 — Byte-identical render regression** on existing caddy sites. *Mitigation:* Issue 6.1
  diff-checks `calibre`/`plex` render; pure data append, no template edit.
- **R6 — AGPL (Garage).** *Mitigation:* homelab non-distribution → no practical obligation;
  documented in SPEC §7 row.
- **R7 — LE DNS-01 rate limits during iteration.** *Mitigation:* use LE staging
  (`caddy_acme_ca`) while validating, then clear — per the existing caddy role guidance.
- **R8 — `hostmetrics` host-bleed under unprivileged LXC** (reads `/proc`,`/sys` that may reflect
  the host, not the container cgroup). *Mitigation:* Issue 5.2 verifies per-CT metrics are
  container-scoped; if bleed occurs, guest agents drop `hostmetrics` (keep `journald`/`filelog` +
  OTLP) and host metrics come only from the pve-host agent.
- **R9 — Garage single-node durability + replication.** Single node = no Garage-level redundancy;
  durability rests entirely on the `pool1` ZFS mirror. Garage also defaults to 3 replicas and will
  not converge on one node. *Mitigation:* pin `replication_factor: 1` in `garage.toml` (Issue 2.3);
  document that the ZFS mirror is the durability layer (Garage is not a second copy).
- **R10 — Chicken-and-egg on the Garage key → 1Password → OpenObserve hand-off.** *Mitigation:*
  Issue 2.4 pushes the minted key into 1Password (mirroring `pve_token`), idempotently, before
  Epic 3 consumes it; OpenObserve's S3 config (3.3) depends-on 2.4.

## Success Criteria
1. OpenObserve reachable at `https://observe.dixson3.net` (Caddy TLS); Garage console at
   `https://console.dixson3.net`, S3 API at `https://s3.dixson3.net`.
2. OpenObserve stores stream data as Parquet **in Garage** (S3 mode), verified by the Epic 4
   smoke test incl. a cold read.
3. `pve` host + all guests ship **logs**, host **metrics** arrive (from the pve-host agent, and
   from guest agents where verified container-scoped per R8), and app **traces** arrive, via
   `otel_agent` → OpenObserve. Verifiable by querying each source's stream in OpenObserve.
4. Effective retention matches tiers: logs ~14d, metrics ~365d, traces 7–30d (not the 10-year default).
5. All config is Ansible-reproducible (`--check --diff` clean); no out-of-band host mutation.
6. Ledgers current: SPEC §6.1/§7/§8, RESERVATIONS (+ UniFi reservations + DNS rows), MOUNTS all
   updated; `scripts/ansible_ledger_check.py` passes.
7. Existing `calibre`/`plex` caddy sites render byte-identical (no regression).
8. Issue #7 closed as superseded-by-OpenObserve.

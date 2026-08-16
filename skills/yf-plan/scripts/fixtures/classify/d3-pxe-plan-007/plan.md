---
deliverable_class: standard
source_plan: plan-007-james-dixson-a98951
source_repo: d3-pxe
---
# Plan: Deploy garage-webui admin/browse dashboard on a new LXC guest, fronted by Caddy with auth (Garage admin API console)

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :---- | :---- | :---------- | :---- | :---------- |

## Epics

### Epic 1: SPEC & ledger reconciliation (lands first)
- Issue 1.1: **SPEC §7.6** — bump the Garage package row to **v2.3.0** (note the v1→v2 in-place-metadata
  upgrade + S3-unchanged); **SPEC §7** — add a garage-webui row (pinned **1.1.0** linux-amd64 binary),
  documenting the **webui-1.1.0 ⇄ Garage-2.x admin-API coupling** (a future Garage major forces a webui
  bump). **SPEC §8** — add the `garage-webui` (CT 105) guest row (unprivileged, `vmbr1`, **no bind**,
  **no idmap**, `:3909`, UI fronted by Caddy) and note the **bindless / no-§6.1** exception explicitly.
  **Reconcile the SPEC prose (missing-item):** the ledger *script* already tolerates a guest absent
  from §6.1/MOUNTS, but if any PVE-CT/PVE-ANS convention text implies "every guest maps a shared id",
  amend it so a stateless/bindless guest is explicitly conforming (keep the prose and the script in
  agreement — a DRIFT-CHECK edge).
- Issue 1.2: **RESERVATIONS.md** — add CT 105 / `.105` / MAC `BC:24:11:00:06:00` row + bump "next free"
  to index 07 / `.106` / CTID 106; add a **Service DNS** row `garage.dixson3.net → 192.168.7.102`
  (operator-published Route53 A). **No MOUNTS row** (bindless).
  - depends-on: 1.1
- Issue 1.3: **Inventory** — add `garage-webui` to `inventory/hosts.yml` `lxc_guests`
  (`ansible_host: 192.168.7.105`); `otel_targets` covers it automatically. Wire the in-CT app role in
  `guests.yml`.
  - depends-on: 1.1

### Epic 2: Garage v1.1.0 → v2.3.0 upgrade (existing CT 103) — lands before the dashboard
- Issue 2.1: Bump the `garage` role — `garage_version: v2.3.0` + the verified `garage_binary_checksum`
  (`sha256:f98d3179…`). Confirm the rendered `garage.toml` is **v2-clean**: `replication_factor: 1` +
  `consistency_mode`, and **no** removed `replication_mode` key. `--check --diff` shows only the
  binary + (if any) toml delta, no collateral change. **In-CT SSH-direct role — no PVE-API token
  needed** (C6); gated solely by the data-safety gate, not the PVE-apply gate.
  - depends-on: 1.1
- Issue 2.2: **Pre-upgrade safety (Ansible-driven, idempotent).** Run `garage repair --all-nodes
  --yes tables` and wait for sync; **stop garage** (quiesce LMDB, C4); take a **recursive** snapshot
  `zfs snapshot -r pool1/garage@pre-garage-v2` (guarded so a re-run does not re-snapshot) **and**
  `garage meta snapshot --all` (mandatory, C4). The `-r` is load-bearing (C1) — data/meta are child
  datasets. This is the rollback artifact. *(The data-safety gate is evaluated after this issue and
  blocks 2.3 — N1.)*
  - depends-on: 2.1 · Capability Gate: Garage-upgrade data-safety (blocks 2.3)
- Issue 2.3: **Apply the upgrade** — `get_url` the v2.3.0 binary (checksum-guarded) → start garage
  (apply-gated). **Verify:** `garage status`/`stats` healthy; `curl -H "Authorization: Bearer
  <admin_token>" 127.0.0.1:3903/v2/GetClusterStatus` returns 200; **OpenObserve continuity** — the
  `openobserve` bucket + a known pre-upgrade object are readable, and OpenObserve resumes read/write
  of Parquet (ingest a probe → confirm it lands). **On any failure, roll back (C3/C9):** stop garage
  → `pct stop 103` → `zfs rollback -r pool1/garage/data@pre-garage-v2` + `…/meta@…` → `rm -f` the v2
  binary + reinstall v1.1.0 → `pct start 103`. **Also revert the role's `garage_version` +
  `garage_binary_checksum` back to v1.1.0 before any re-converge (N2)** — else the role's
  version-assert task fails against the rolled-back binary. Idempotent re-converge (`changed=0`).
  - depends-on: 2.2
- Issue 2.4: **Mint a dedicated, scoped Garage v2 admin token for garage-webui (C5)** — via the v2
  admin API / `garage` CLI, create a named admin token (e.g. `garage-webui`) **separate** from the
  master `admin_token`; push it to 1Password `Y-Home/garage-webui-admin-token` (Ansible-authored,
  mirroring the plan-006 Garage-key push; idempotent — do not re-mint on re-converge). garage-webui
  (Issue 3.3) reads **this** token, never the master.
  - depends-on: 2.3

### Epic 3: garage-webui guest (CT 105)
- Issue 3.1: `host_vars/garage-webui.yml` — identity (CT 105, MAC 06, `.105`, `vmbr1`), sizing
  (1–2 cores / 512 MiB, rootfs 8G), no bind, **`idmap: []` set EXPLICITLY (C7)** — `pve_lxc`'s
  `raw_conf.yml` loops `guest_facts.idmap` with no `| default([])`, so omitting the key errors; an
  empty list is the clean no-op. **Also add `| default([])` to that role loop** as the
  backward-compatible generalization (existing guests byte-identical — PVE-GUEST-002 (a), not a fork).
  Provision the CT via `pve_lxc` (create-stopped → raw_conf → started, PVE-ANS-008); verify the empty
  idmap + absent bind render a valid config.
  - depends-on: 1.2, 1.3 · Capability Gate: PVE apply
- Issue 3.2: **Bootstrap** CT 105 (`bootstrap.yml -e guest=garage-webui`) + set the **UniFi Fixed-IP**
  reservation for CT 105 `.105` in the UDM-Pro UI (PVE-NET-005) after the guest first appears.
  - depends-on: 3.1
- Issue 3.3: `garage_webui` app role (clone caddy/openobserve shape) — pinned **1.1.0** binary via
  `get_url` + `checksum:` (`sha256:180b5946…`); systemd unit; 0600 `EnvironmentFile` with connection
  env + `API_ADMIN_KEY` = the **dedicated scoped token** (`Y-Home/garage-webui-admin-token`, from
  Issue 2.4 — **not** the master) + `AUTH_USER_PASS` (`user:<bcrypt>`, new `Y-Home/garage-webui-auth`
  item — bcrypt generated via a **portable Python `bcrypt` one-liner** on the darwin control node, not
  `htpasswd` which is not reliably present (C10)); apply-gated start; assert both secrets present on
  the apply path.
  - depends-on: 3.2, 2.4 *(needs Garage on `/v2/` + the scoped admin token)*
- Issue 3.4: **Verify** — dashboard up on `192.168.7.105:3909`; connects to the Garage **v2** admin
  API (lists the `openobserve` bucket + keys + layout); object browser lists objects in `openobserve`
  (S3 creds auto-resolved); built-in login works. Confirm CT 105 also reports logs/metrics via its
  auto-deployed otel_agent. Idempotent re-converge (`changed=0`).
  - depends-on: 3.3

### Epic 4: Caddy fronting (data append)
- Issue 4.1: Append one `caddy_sites` entry (`garage.dixson3.net → http://192.168.7.105:3909`);
  verify existing `calibre`/`plex`/`observe`/`s3`/`console` sites render byte-identical (SPEC §8).
  Update `docs/diagrams/caddy-app-routing.d2` (+re-render PNG) to show the new vhost (DRIFT-CHECK
  `caddy-defaults` node).
  - depends-on: 3.4
- Issue 4.2: **Operator publishes** the Route53 A record `garage.dixson3.net → 192.168.7.102`; apply
  the caddy role; verify TLS issuance (LE DNS-01) + reachability + garage-webui login through Caddy.
  - depends-on: 4.1 · Capability Gate: Route53 A record published

## Risks & Mitigations
- **R1 — Garage v1→v2 upgrade risk to OpenObserve's live data.** The upgrade touches the store that
  holds OpenObserve's Parquet. *Mitigation:* it is a **binary swap + in-place metadata restart, not a
  data-format migration** (EXP-002); **S3 API unchanged** (OpenObserve needs no reconfig); pre-flight
  `garage repair tables`; **stop garage, then a mandatory RECURSIVE snapshot** `zfs snapshot -r
  pool1/garage@pre-garage-v2` (covers the `data`/`meta` **child** datasets — a non-`-r` snapshot of
  the carrier parent would protect nothing, C1) + `garage meta snapshot --all`; **rollback** = stop
  garage → `pct stop 103` (release the rbind, else "dataset busy", C3) → `zfs rollback -r` each child
  → `rm -f` + reinstall v1.1.0 (C9) → `pct start 103`. The **data-safety gate** asserts the *child*
  snapshots exist (C2) before the swap and runs an OpenObserve-continuity check after.
- **R2 — brief S3 write outage during the Garage restart.** *Mitigation:* single-node restart is
  seconds; OpenObserve buffers writes in its local WAL and flushes on reconnect (plan-006 offload
  cadence). Optionally quiesce ingest for the window.
- **R3 — webui/Garage admin-API version coupling (ongoing).** garage-webui 1.1.0 targets Garage
  `/v2/`; a future Garage **v3** major would break it. *Mitigation:* both pinned to current majors
  (low debt now); document the **webui-1.1.0 ⇄ Garage-2.x** coupling in SPEC §7 — a Garage major
  upgrade must bump garage-webui in lockstep.
- **R4 — admin-token blast radius.** A Garage admin token can reveal every bucket's S3 secret
  (`GetKeyInfo?showSecretKey=true`); placing one on CT 105 means a CT 105 compromise ⇒ Garage admin.
  *Mitigation (C5):* garage-webui gets a **dedicated, independently-revocable Garage v2 admin token**
  (Issue 2.4), **never the master `admin_token`** — the v2 upgrade unlocks multiple tokens, so
  compromise/rotation is contained. Plus: admin API **LAN-internal** (not fronted); garage-webui login
  (`AUTH_USER_PASS`) **and** Caddy TLS; 0600 EnvironmentFile, 1Password-sourced, never committed.
- **R5 — first bindless / no-custom-idmap guest.** `pve_lxc/tasks/raw_conf.yml` loops
  `guest_facts.idmap` with **no `| default([])`**, so omitting idmap errors. *Mitigation (C7):* Issue
  3.1 sets `idmap: []` explicitly **and** adds `| default([])` to the role loop (backward-compatible
  generalization — existing guests byte-identical, PVE-GUEST-002 (a), not a fork); binds are already
  `is defined`-guarded so bindless is genuinely fine.
- **R6 — unauthenticated dashboard if `AUTH_USER_PASS` misconfigured.** *Mitigation:* the role
  **asserts** `AUTH_USER_PASS` present on the apply path (like caddy/openobserve cred asserts); Caddy
  TLS is a second layer.
- **R7 — Garage admin API (`:3903`) reachability CT 105 → CT 103.** *Mitigation:* Garage
  `admin_bind_addr = [::]:3903` binds the LAN; Issue 3.4 confirms reachability (flat `vmbr1`, no host
  firewall between guests).
- **R8 — bcrypt generation dependency (darwin control node).** `htpasswd` is not reliably present on
  macOS. *Mitigation (C10):* generate the `user:<bcrypt>` once with a **portable Python `bcrypt`
  one-liner** (`uv run --with bcrypt …`), store it in 1Password; the role only consumes it.
- **R9 — byte-identical caddy render regression.** *Mitigation:* Issue 4.1 is a pure `caddy_sites`
  data append + diff-check of existing sites (no template edit).
- **R10 — webui 1.1.0 ↔ Garage v2.3.0 compat is inferred, not tested (C8).** garage-webui's compose
  example pins `v2.0.0`; 2.3.0 compat rests on Garage's "no admin-API break within a major" guarantee.
  *Mitigation:* keep v2.3.0 (gains S3 fixes); if the UI misbehaves the response is a **webui pin bump,
  NEVER a store downgrade** (the store risk C1–C4 dwarfs the UI risk); optionally smoke webui 1.1.0
  against a throwaway v2.3.0 before committing. Fallback floor: pin Garage `v2.0.0` (the exact tag the
  UI ships against) for zero inference.

## Success Criteria
1. **Garage upgraded to v2.3.0** (`garage status`/`stats` healthy, `/v2/` admin API responds), with
   **OpenObserve continuity verified** — it reads a pre-upgrade Parquet object and writes new data to
   the `openobserve` bucket after the upgrade, no reconfiguration.
2. `https://garage.dixson3.net` reachable (Caddy TLS, LE DNS-01); garage-webui **1.1.0 login works**
   (`AUTH_USER_PASS`).
3. Dashboard connects to the Garage **v2** admin API — lists **buckets** (incl. `openobserve`),
   **keys**, and **layout**; **object browser** lists (and can download) objects in `openobserve`
   (S3 creds auto-resolved).
4. All config Ansible-reproducible (`--check --diff` clean, idempotent `changed=0`); no out-of-band
   host/guest mutation. A `pool1/garage@pre-garage-v2` ZFS snapshot exists as the documented rollback.
5. Ledgers current: SPEC §7.6/§7/§8 (Garage v2.3.0 pin, garage-webui row, bindless note, version
   coupling), RESERVATIONS (+ UniFi reservation + DNS row); `scripts/ansible_ledger_check.py` passes.
6. Existing `calibre`/`plex`/`observe`/`s3`/`console` caddy sites render byte-identical (no regression).
7. CT 105 ships logs + metrics to OpenObserve via its auto-deployed `otel_agent`.

---
deliverable_class: standard
source_plan: plan-011-james-dixson-150357
source_repo: d3-pxe
---
# Plan: Shared PostgreSQL guest (CT 107) with PGDATA on a dedicated pool1 dataset

## Upstream Issues

| Issue                                              | Title                                                                | Disposition | Notes                                                                                                                                                                                                                                     | Resolved By                                            |
| :------------------------------------------------- | :------------------------------------------------------------------- | :---------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- |
| [#10](https://github.com/dixson3/d3-pxe/issues/10) | Add PostgreSQL                                                       | include     | Fully resolved by this plan. The issue's two substantive requirements — *shared service* and *PGDATA on a dedicated `pool1` dataset* — are both honored.                                                                                  | Issue 6.1                                              |
| [#51](https://github.com/dixson3/d3-pxe/issues/51) | Backup jobs: Sanoid/syncoid + Restic off-host for pve config/DB tier | partial     | `pool1/postgres` enters the **precious** tier under PVE-STO-005 and MUST be backed up. This plan does **not** implement the backup machinery — it registers the dataset as precious and files the linkage. Implementation stays with #51. | Issue 1.1 (precious registration), Issue 4.6 (linkage) |
| [#16](https://github.com/dixson3/d3-pxe/issues/16) | Add Nextcloud                                                        | exclude     | Named in #10 as a future consumer. Out of scope; this plan's multi-consumer provisioning model is what makes it cheap later.                                                                                                              | n/a                                                    |

## Epics

### Epic 1 — SPEC & ledger reconciliation

Lands first; nothing operational happens until the ledgers agree.

- **Issue 1.1** — SPEC.md: add **§7.11 PostgreSQL guest (CTID 107)** — `PVE-PKG-100` (base
  `python3`, `openssh-server`, **`python3-psycopg2`**, **`acl`**, **`awscli`** (Debian ships **v1**; v2 is unpackaged — the streaming `s3 cp -` form used here works on v1) — `community.postgresql` tasks run
  `become_user: postgres`, and Ansible's unprivileged-to-unprivileged become fails with *"Failed to
  set permissions on the temporary files"* without it), `PVE-PKG-101` (**`postgresql-17`** pinned
  from Debian apt `state=present`; uid/gid 10006 pinned **before** install per PVE-CT-002; PGDATA on
  the bind-mounted dataset per PVE-STO-001/002; **locale `C.UTF-8` / encoding `UTF8` pinned at
  cluster creation and immutable thereafter**; `listen_addresses = '*'` with `pg_hba` restricted to
  the guest block; `:5432` LAN-internal, **not** Caddy-fronted), `PVE-PKG-102` (per-consumer roles,
  databases, and isolation grants; passwords from 1Password via role-prefixed env, mirroring
  PVE-AUTH-002). Amend **PVE-PKG-021** (§7.3) to add the `community.postgresql` collection. Add the
  §6.1 row for `10006`, the §8 guest row (`Status: planned`), §10 manifest rows, **register
  `pool1/postgres` in PVE-STO-005's precious enumeration** (a SPEC edit, so it lands here — not in
  Epic 4 — per AGENTS.md and SPEC §11), and a §11 amendment-log entry citing #10.

  > **§7.10 is deliberately left empty** — it is reserved for plan-010 (`litellm`, CT 106), which
  > lands second despite the lower CTID. The gap is intentional, not an omission.

  > **Expected transient gate failure.** `check_shared_ids()` requires every SPEC §6.1 row to have a
  > matching `group_vars/all.yml` entry, so `ansible_ledger_check.py` goes **red** the moment this
  > issue lands and stays red until Issue 1.3. This is expected and brief — do not "fix" it by
  > reverting the SPEC row. (plan-009 set this precedent with its migration-in-progress note.)

- **Issue 1.2** — `RESERVATIONS.md`: add the CT 107 Reservations row with `Status: pending`
  (→ `active` once the UniFi Fixed-IP is set in Issue 2.4). `MOUNTS.md`: one Datasets row, one
  Bind-mounts row, and extend the idmap-dependency paragraph with `postgres` 10006. **Decide the
  `recordsize` here and state it identically in both `MOUNTS.md` and `pve_storage/defaults/main.yml`:
  use `recordsize=16K`** (Postgres' 8K page size; the ledger's usual "do not force a value" advice
  targets non-database state). R7 records that this pair is a de-facto drift edge with no automated
  backstop, so it must be got right by hand.

  > **Do NOT touch the "Next free" block.** Index `07` / `.106` / CTID `106` remains genuinely
  > unallocated and therefore correct. Add only a one-line note beneath it: *"Index `08` (`.107` /
  > CTID 107) is claimed out of order by plan-011 (`postgres`); index `07` is reserved for plan-010
  > (`litellm`)."* plan-010 then advances the pointer `07 → 09` in a single step. This keeps the
  > ledger true at **every** instant — PVE-ID-001 requires collisions be prevented by the registry,
  > not by memory.

  > **Expected transient drift.** `DRIFT-CHECK.md`'s `e-layout-reservations` edge maps
  > `RESERVATIONS.md` ↔ `pve-guest-layout.d2`, so it goes red the moment this issue lands and stays
  > red until Issue 2.5 re-renders the diagram. Expected, brief, and mirrors the 1.1 note — do not
  > "fix" it by reverting the ledger row. *depends-on: 1.1*

- **Issue 1.3** — Inventory wiring: `group_vars/all.yml` `shared_ids.postgres`; `hosts.yml` entry
  under `lxc_guests` (which auto-enrolls `otel_agent` — no `otel_targets` edit); a `guests.yml` play
  inserted **before** the trailing whole-group otel play; and `community.postgresql` appended to
  `ansible/requirements.yml`. Clears the Issue 1.1 transient drift. *depends-on: 1.1*

### Epic 2 — CT 107 provisioning

- **Issue 2.1** — `pve_storage` data append: `pool1/postgres`, `mountpoint: /pool1/postgres`,
  owner/group from `shared_ids.postgres`, `mode: "0700"`, properties per the R7 decision. Apply via
  `storage.yml`. **Must land before the CT starts.** *depends-on: 1.2, 1.3*
- **Issue 2.2** — `pve_host` data append: `root:10006:1` in **both** `subuid_delegations` and
  `subgid_delegations` (PVE-CT-003). *depends-on: 1.2, 1.3*
- **Issue 2.3** — `inventory/host_vars/postgres.yml`, the fact set mirroring
  `host_vars/openobserve.yml` (`ostype`, `gpu_passthrough` and `tun` are omitted deliberately —
  `pve_lxc` defaults all three): `ctid: 107`, `hostname`, `hwaddr`, `reserved_ip`, `bridge: vmbr1`,
  `ip: dhcp`, **`ostemplate`** (PVE-CT-004 — the create *fails hard* on a missing volid),
  `cores: 2`, **`memory: 4096`** (sized for `shared_buffers` ≈ 1 GB and `max_connections: 100`, with
  headroom for a second consumer), `swap: 1024`, `onboot: true`, `unprivileged: true`,
  `nesting: true`, `rootfs_storage: local-zfs`, `rootfs_size: 8`, the six idmap lines, `config_bind: {host: /pool1/postgres, guest: /var/lib/postgresql}`, **`postgres_databases`**
  (the consumer list — it lives here, not in role defaults, because the `otel_agent` play in Epic 5
  must also read it), and `otel_agent_postgresql_enabled: true`. Provision via `pve_lxc`; prove
  existing guests render **byte-identical** (`host.yml --check --diff` shows zero delta) per
  PVE-GUEST-002(a). *depends-on: 2.1, 2.2 · Capability Gate: PVE apply token*
- **Issue 2.4** — Bootstrap `-e guest=postgres --tags bootstrap`; operator sets the **UniFi
  Fixed-IP** for `BC:24:11:00:08:00` → `.107` after first appearance (PVE-NET-005); flip the
  RESERVATIONS row to `active`. *depends-on: 2.3*
- **Issue 2.5** — `docs/diagrams/pve-guest-layout.d2` + PNG re-render. Placed **here**, not in
  Epic 1: `DRIFT-CHECK.md`'s `e-layout-hostvars` edge is scoped to `host_vars/*.yml`, which does not
  exist until Issue 2.3 — rendering earlier would leave the edge re-triggered with no follow-up.
  *depends-on: 2.3*

### Epic 3 — the `postgres` role

- **Issue 3.1** — Role skeleton (`user → install → config → service`), cloned from `garage_webui`.
  *depends-on: 2.4*
- **Issue 3.2** — `tasks/user.yml`: pin group `postgres` gid 10006 and user `postgres` uid 10006
  **before** any package task. The R1 mitigation and the single most important ordering constraint
  in the plan. *depends-on: 3.1*
- **Issue 3.3** — `tasks/install.yml`: `file: state=directory` for `/etc/postgresql-common/`, then
  write `createcluster.conf` with **`create_main_cluster = false`** and
  `initdb_options = '--locale=C.UTF-8 --encoding=UTF8'`, then
  `apt: name=[postgresql-17, python3-psycopg2, acl, awscli] state=present`. Because
  `create_main_cluster = false`, the postinst creates **no** cluster — creation is the role's, in
  Issue 3.4. (`acl` is required for `become_user: postgres`; `awscli` for the Issue 4.2 dump timer.)
  *depends-on: 3.2*
- **Issue 3.4** — **Own cluster creation and adoption** (`tasks/cluster.yml`, imported between
  `install` and `config` — a deliberate fifth step beyond the `garage_webui` four-file skeleton,
  because 3.6's `community.postgresql` tasks need a live cluster). Implement the three-way branch: **create**
  (`pg_createcluster 17 main --locale=C.UTF-8 --encoding=UTF8`) when `PG_VERSION` is absent;
  **adopt** (write the full config set, set `data_directory`, start `postgresql@17-main` — never
  `pg_createcluster`, whose integrate path requires configs in the datadir) when the datadir survives
  but `/etc/postgresql/` does not; **no-op** when both are present. This is the mechanism R9 and the
  Issue 4.5 drill both depend on. *depends-on: 3.3*
- **Issue 3.5** — **Verify the storage/identity contract** before any consumer exists: PGDATA
  resolves to `/pool1/postgres/17/main`; on-disk owner is `10006:10006` **from the host view** and
  `postgres:postgres` **from the guest view**; the cluster's `lc_collate`/`server_encoding` match
  the pinned values. *depends-on: 3.4*
- **Issue 3.6** — `tasks/config.yml`: template the **full config set** per the
  Approach's adopt decision — `postgresql.conf` (`listen_addresses = '*'`, `max_connections = 100`,
  `shared_buffers`, `data_directory`, **`hba_file`**, **`ident_file`**, **`ssl = off`**, and **no
  `include_dir`** — so no `conf.d/` directory is required and a missing one cannot be a startup FATAL), `pg_hba.conf`, `pg_ident.conf`, `start.conf` — with `<version>` from the pin. The `pg_hba.conf` template **must retain the
  `local … peer` lines** (the dump timer, `pg_ctlcluster`, and every `become_user: postgres` task
  depend on them) and use the **six per-consumer CIDRs**, never `192.168.7.0/24`. Loop
  `postgres_databases` to create each consumer's role and database **plus the isolation grants**, in
  order and on the right connections: on the maintenance DB `ALTER DATABASE … OWNER TO <owner>` →
  `REVOKE ALL ON DATABASE … FROM PUBLIC` (**not** `REVOKE CONNECT` — that leaves `TEMPORARY`) →
  `GRANT CONNECT … TO <owner>`; then, **on a connection to `<db>` itself**,
  `REVOKE ALL ON SCHEMA public FROM PUBLIC`. With `no_log: true` and the repo's three guards, and a **`notify:` restart handler** — every
  setting enumerated above is `context=postmaster` (restart-only), and Issue 3.7's `state: started`
  is a no-op on an already-running unit, so without the notify a config change would silently not
  take effect. `garage_webui`'s `handlers/main.yml` (`state: restarted`, apply-guarded) is the
  pattern being cloned.
  *depends-on: 3.5 · Capability Gate: 1Password consumer credentials*
- **Issue 3.7** — `tasks/service.yml`: `enabled: true` always, `state: started` only
  `when: postgres_apply_service` (PVE-ANS-007). *depends-on: 3.5*
- **Issue 3.8** — **Add a second consumer.** Append a second `postgres_databases` entry and apply.
  This is a state change, not a verification — it exists so isolation can be *proved* rather than
  asserted, and it is the evidence artifact for SC12 (add-a-consumer touches no role logic).
  *depends-on: 3.6*
- **Issue 3.9** — **Verify service and access control.**
  - **Positive:** from inside CT 107, connect over its own LAN address —
    `PGPASSWORD="$(op read 'op://Y-Home/litellm-postgres/password')" psql -w "postgresql://litellm@192.168.7.107:5432/litellm" -c 'select 1'`.
    The source address is `.107`, inside the guest block, so this exercises the real TCP +
    `scram-sha-256` + `pg_hba` path rather than the unix socket.
  - **Negative (range):** from the **`pve` host (`.60`, outside the block)** — a `python3` socket
    probe asserting the server returns `no pg_hba.conf entry`. **Not** from the control node, which
    is `192.168.7.115` and therefore *inside* the permitted range (see SC9).
  - **Negative (isolation):** consumer A's credential is rejected against consumer B's database.
  - **Socket:** `sudo -u postgres psql -c 'select 1'` works over the local socket — proving the
    whole-file `pg_hba` template retained the `local … peer` lines the dump timer and cluster
    maintenance depend on.
  - Confirm `otel_agent` reporting for CT 107; idempotent re-converge shows `changed=0`.
  *depends-on: 3.7, 3.6, 3.8*

  > The cross-*guest* connection test is deliberately **not** here — CT 106 does not exist yet, and
  > installing `postgresql-client` on an existing guest would be an out-of-band mutation forbidden by
  > PVE-ANS-001. It is carried by plan-010's *Capability Gate: plan-011 complete*, which already runs
  > exactly that command from the consuming side.

### Epic 4 — backup posture & documentation

> **Where the dumps go — a decision the first draft left open.** "Outside `pool1/postgres`" has no
> reachable *local* implementation: a second `pool1` dataset needs a second bind var, but
> `ansible_ledger_check.py` recognizes exactly two keys and `config_bind` is already spent on PGDATA
> — so a third key is silent drift (the very trap Issue 6.2 files upstream), the guest rootfs is
> barred by PVE-STO-001, inside `pool1/postgres` defeats the purpose, and dumping from the host is
> out-of-band under PVE-ANS-001.
>
> **Resolution: push the dumps off the guest to Garage** (CT 103, already running, S3 API at
> `192.168.7.103:3900`) — operator-confirmed. No bind, no new dataset, no ledger row, no new bind key.
>
> **Be precise about what this buys.** Garage's store is `pool1/garage/{data,meta}` — the **same
> `pool1` mirror** as PGDATA. So this is a different **logical** failure domain (the dumps survive
> `DROP DATABASE`, a bad migration, a botched upgrade, and destruction of the `pool1/postgres`
> dataset itself) but **not a different physical one**. A pool-level failure takes both. An earlier
> draft of this plan claimed otherwise; that claim was wrong and is corrected here. The off-host
> copy remains #51's job, and SC23 states the residual gap explicitly.

- **Issue 4.1** — **Provision the Garage backup target.** Create the `pg-backups` bucket and a
  **dedicated, scoped** access key (`bucket allow --read --write` for that bucket only — never reuse
  the openobserve key), store it in `Y-Home/postgres-garage-backup`, and apply a
  `PutBucketLifecycleConfiguration` retention rule (Garage supports `Expiration` +
  `AbortIncompleteMultipartUpload`; it has **no object versioning**, hence dated key prefixes).
  Note `roles/garage/tasks/provision.yml` is currently **hardcoded per-consumer**, so this is a
  cross-role edit — call it out rather than assuming a loop exists. *depends-on: 3.9*
- **Issue 4.2** — **Implement the interim backup.** A `postgres-dump.service`/`.timer` pair running
  as the `postgres` user: `pg_dumpall --globals-only` (roles and grants) plus `pg_dump -Fc` per
  database, streamed to Garage via
  `aws --endpoint-url http://192.168.7.103:3900 s3 cp - s3://pg-backups/<date>/…`.

  > **Two safety requirements, not optional polish.** In a pipeline systemd sees only the
  > *uploader's* exit status, so a `pg_dump` that dies mid-stream yields a complete-looking object
  > and a **green timer** — unacceptable for the plan's only logical-loss control. The unit must set
  > `set -euo pipefail` **and** validate after upload:
  > `aws … s3 cp s3://pg-backups/<key> - | pg_restore -f /dev/null` — a **full archive read**, not `pg_restore -l`: in the custom format the TOC sits near the front of the file, so `-l` lists cleanly on an archive truncated mid-data, which is exactly the failure this is meant to catch. (Dumping to a local file first
  > is the obvious alternative and is rejected: CT 107's rootfs is 8 GB.)
  >
  > `pg_dumpall --globals-only` contains **SCRAM password verifiers** for every consumer, which is
  > why the key is bucket-scoped and the bucket is not shared.

  *depends-on: 4.1*
- **Issue 4.3** — **Record the ZFS-snapshot decision: deferred to #51.** A local snapshot schedule on
  `pool1/postgres` would be a genuinely cheap control — because the whole cluster lives on one
  dataset, a snapshot is atomic and crash-consistent (Postgres replays WAL on restore exactly as
  after a power loss). But it is **not implementable within this plan's scope**: `roles/pve_storage`
  is purely declarative, `community.general.zfs` can take a one-shot snapshot but has **no pruning
  module**, so a retention policy needs a host systemd timer + prune script — a new host-touching
  capability of exactly the class PVE-OBS-001 had to authorize, which Issue 1.1's SPEC edits do not
  schedule. Rather than ship a half-mechanism behind an undeclared gate, this is **explicitly
  deferred to [#51](https://github.com/dixson3/d3-pxe/issues/51)'s Sanoid**, which is the right tool.
  Recorded as a decision, not a silent omission. *depends-on: 3.8*
- **Issue 4.4** — **Seed a canary.** Insert a table with known rows into the `litellm` database. The
  drill runs *before* plan-010 writes anything real, so without a canary the restore assertion in 4.5
  would verify an empty set and prove nothing. *depends-on: 4.1*
- **Issue 4.5** — **Prove recovery end to end**, as two *separate* assertions that the first draft
  conflated:

  **R2 — the dataset survives a guest rebuild:**
  1. Take a full backup (globals + per-database `-Fc`) per Issue 4.2.
  2. Destroy CT 107. **This is a manual `pct stop 107 && pct destroy 107`** — `roles/pve_lxc` has
     only `state: present` and `state: started`; there is **no destroy path anywhere in `ansible/`**,
     and `ansible/README.md` points at plan-003's manual destroy→recreate runbook as the precedent.
     Recorded here as an authorized exception to PVE-ANS-001 rather than an available capability.
  3. Recreate via `host.yml --tags apply`, then `bootstrap.yml -e guest=postgres`, then a full role
     re-converge. This is where the **adopt branch** is exercised: `/pool1/postgres/17/main` survived,
     `/etc/postgresql/` did not.
  4. Assert: the dataset survived, `pct destroy` did **not** remove it (a bind-mounted directory is
     not a storage volume — the specific proposition this drill exists to test), the UniFi Fixed-IP
     still resolves `.107` (it is keyed by MAC, which `host_vars` pins), and **the canary rows are
     still present without any restore**.

  **R3 — the dump actually restores:**
  5. `DROP DATABASE litellm` **and `DROP ROLE litellm`** — dropping only the database leaves the role
     in place, making the globals replay a no-op (and it would abort under `ON_ERROR_STOP=1` with
     "role already exists"), so the proposition *"`pg_restore` needs the owner role to pre-exist"*
     would never actually be tested. Then restore in order, fetching from Garage:
     `aws --endpoint-url http://192.168.7.103:3900 s3 cp s3://pg-backups/<key>/globals.sql - | psql -v ON_ERROR_STOP=1`
     → `createdb -O litellm litellm` →
     `aws … s3 cp s3://pg-backups/<key>/litellm.dump - | pg_restore -d litellm`. Assert the canary
     rows are back. **Then re-converge the `postgres` role and confirm SC17 still passes**: the
     restore recreates the database but **not** the `GRANT CONNECT ON DATABASE litellm TO
     otel_monitor` that Issue 5.1 folds into the `postgres_databases` loop — so without a re-converge
     the receiver silently stops collecting for that database. That is R11's failure mode arriving by
     a path R11 does not otherwise cover, and Epics 4 and 5 have no dependency edge, so either
     interleaving is legal.

  Step 4 proves survival; step 5 proves recoverability. Neither substitutes for the other.
  *depends-on: 4.4, 4.2 · Capability Gate: recovery drill authorized*
- **Issue 4.6** — Cross-link [#51](https://github.com/dixson3/d3-pxe/issues/51) as the owner of the
  full Sanoid/syncoid + off-host Restic tier, and document explicitly that `vzdump` does **not**
  capture bind-mounted `pool1` data — so the guest backup does not cover the database.
  *depends-on: 4.5*
- **Issue 4.7** — `ansible/README.md`: add the role to the Layout tree and Roles section, add
  `postgres` rows to the Task → SPEC-ID traceability table, and document the `op read` export recipe
  (**closing the gap** where the `caddy` AWS item name appears nowhere outside a `fail_msg`).
  *depends-on: 4.4*
- **Issue 4.8** — Document the **add-a-consumer** procedure: append to `postgres_databases`, create
  the 1Password item, export the env var, re-run. This is what makes the "shared" claim real.
  *depends-on: 4.7*

### Epic 5 — Postgres observability

Guest-level telemetry is free — CT 107 lands in `lxc_guests`, so `otel_agent` auto-enrolls it and
ships journald logs plus hostmetrics. But hostmetrics tells you the *container* is alive, not how the
*database* is behaving. For the one guest where connection saturation, cache hit ratio and lock
contention actually predict failures, that is too thin, and it sits badly with
[#47](https://github.com/dixson3/d3-pxe/issues/47)'s telemetry-by-default direction.

This epic adds database-level metrics via `otelcol-contrib`'s **`postgresql` receiver** and a
committed dashboard.

- **Issue 5.1** — **Create the `otel_monitor` database role.** A dedicated login role granted
  **`pg_monitor`** (PG10+; gives the stats views the receiver needs without any data access), with
  its password from 1Password via the repo's env pattern.

  > **Two interactions with Epic 3's isolation model that must be handled explicitly, or the receiver
  > silently collects nothing:**
  >
  > 1. **`pg_hba` must permit it.** The receiver connects over TCP to `127.0.0.1:5432`, and
  >    **loopback is not in the guest block** — the six per-consumer CIDRs cover `.100–.149` only. Add
  >    one line: `host all otel_monitor 127.0.0.1/32 scram-sha-256`. Without it the receiver is
  >    rejected by the very `pg_hba` rules SC9 exists to prove.
  > 2. **`REVOKE ALL … FROM PUBLIC` blocks it.** Issue 3.6 revokes `CONNECT` from `PUBLIC` on every
  >    consumer database, so `otel_monitor` needs an explicit
  >    `GRANT CONNECT ON DATABASE <db> TO otel_monitor` per entry in `postgres_databases` — added to
  >    the same loop, so a new consumer stays a data append.

  > **Ordering:** the `otel_monitor` role creation is inserted **before** the `postgres_databases`
  > loop in `roles/postgres/tasks/config.yml`. Reversed, the first converge fails with
  > `role "otel_monitor" does not exist` — the same ordering discipline R1 applies to the uid pin and
  > Issue 3.6 applies to owner-first `ALTER DATABASE`.

  *depends-on: 3.6*

- **Issue 5.2** — **Add the `postgresql` receiver to `otel_agent`**, opt-in per guest via
  **`otel_agent_postgresql_enabled`** — defaulted **`false`** in `roles/otel_agent/defaults/main.yml`
  (this is what makes SC19's fleet-wide zero-delta proof achievable at all) and set `true` in
  `inventory/host_vars/postgres.yml` — with its password delivered through the role's existing 0600 `EnvironmentFile`:

  ```yaml
  receivers:
    postgresql:
      endpoint: 127.0.0.1:5432
      transport: tcp
      username: otel_monitor
      password: ${env:POSTGRES_OTEL_PASSWORD}
      # Derived, not hardcoded — otherwise Issue 3.8's second consumer is provisioned,
      # granted and pg_hba-permitted but silently unmonitored, quietly voiding SC12's
      # "add-a-consumer is a data append" property for the observability layer.
      databases: {{ postgres_databases | map(attribute='name') | list }}
      collection_interval: 60s
      tls: {insecure: true}
      metrics:
        # These three ship `enabled: false` in the receiver's metadata.yaml @ v0.157.0.
        # Without this stanza Issue 5.4's deadlock/lock and sequential-scan panels have no
        # data, and SC17 — which names `deadlocks` verbatim — cannot pass.
        postgresql.deadlocks: {enabled: true}
        postgresql.sequential_scans: {enabled: true}
        postgresql.database.locks: {enabled: true}
        # Enabled rather than derived: owning the stanza makes the hit/read counters two
        # lines away, and it avoids the cross-table aggregation the `source`-attribute
        # derivation would otherwise need for cache hit ratio.
        postgresql.blks_hit: {enabled: true}
        postgresql.blks_read: {enabled: true}
  ```

  > **Same host-mutation class as plan-010's Epic 5 — and the same gate applies.** `otel_agent` is
  > deployed by PVE-OBS-001 to the `pve` host **and every guest**, so this is not a per-guest edit; it
  > is a fleet-wide role change. **Three changes, all guarded by the same per-guest flag**: the
  > receiver, its wiring into the `metrics:` pipeline, and the `POSTGRES_OTEL_PASSWORD=` line in
  > `otel_agent.env.j2` (that template is currently unconditional, so an unguarded line renders
  > everywhere and fails the byte-identical proof).
  >
  > **The secret must reach the role's own `validate:` step, or the template task fails.**
  > `roles/otel_agent/tasks/config.yml` runs `validate: "{{ otel_agent_bin }} validate --config=%s"`
  > **on the target host**, and the postgres receiver's `password` is a **required** field —
  > `${env:POSTGRES_OTEL_PASSWORD}` expands to empty there, and validation exits 1 with
  > `missing password`. (This has never bitten before because the existing config's only secret is
  > written `${env:OTEL_OO_AUTH_B64:-}` with a `:-` default and no required field consumes it.)
  > Supply it via an `environment:` mapping on the template task, guarded by
  > `otel_agent_postgresql_enabled`.
  >
  > **And extend the existing assert.** `config.yml` currently asserts only the OpenObserve token,
  > and its env-file task is guarded `when: otel_agent_oo_auth_b64 | length > 0`. So a converge with
  > the ingest token present but `POSTGRES_OTEL_PASSWORD` unset would write an empty value into the
  > 0600 env file — and because the field is required, **otelcol refuses to start at all**, taking
  > journald and hostmetrics on CT 107 down with it. A missing database credential must not become a
  > total telemetry outage on the one guest this epic exists to instrument: assert it under the same
  > flag so the failure is loud — **and place that assert *before* the config-template task**, not
  > alongside the existing one at the end. `config.yml` templates at line 13 and asserts at line 23,
  > so an assert added in the usual place can never fire: the template's `validate:` dies first with
  > otelcol's `invalid config: missing password`. (The existing assert is also gated
  > `when: otel_agent_apply_service`, while the validate failure is unconditional.) The run fails
  > closed either way — no empty password is written and the collector is never restarted into a
  > broken state — so this costs a debugging cycle, not safety.
  >
  > Note the `metrics:` pipeline is currently `[hostmetrics]`-only **and wrapped in
  > `{% raw %}{% if otel_agent_hostmetrics_enabled %}{% endraw %}`** — so the guard must be restructured to render
  > when **any** enabled receiver is present, or disabling hostmetrics on this guest would silently
  > drop the Postgres metrics too. There is a clone-ready precedent eight lines up in the same
  > template: the `log_receivers` namespace list at `config.yaml.j2:79-87`.

  > **`postgres_databases` MUST be defined in `inventory/host_vars/postgres.yml`, not in
  > `roles/postgres/defaults/main.yml`.** `guests.yml` runs `otel_agent` as a **separate trailing
  > play**, and role defaults are scoped per-role-per-play — so a role-defaults home is undefined
  > here and the task fails with `'postgres_databases' is undefined`. The `caddy_sites` precedent
  > points the other way and is the trap: it is consumed only by its own role. Inventory is the only
  > location in scope for **both** plays, and `ansible_ledger_check.py` tolerates the extra key.
  > A bare `| default([])` is **not** an acceptable substitute — the receiver accepts `[]` as
  > *collect-all*, so it would hide the misplacement rather than surface it.

  *depends-on: 5.1 · Capability Gate: otel_agent host-side apply authorized · Capability Gate: otel_monitor credential exists*

- **Issue 5.3** — **Generalize `roles/openobserve/tasks/dashboards.yml`** into a loop over an
  `openobserve_dashboards` list, keeping `openobserve_claude_dashboard_title` as an alias so the
  refactor is a **no-op for plan-008**. Retain verbatim the upsert-by-title mechanics (title is the
  idempotency key; `POST` when absent, `PUT /{id}?folder=&hash=` when present), the loopback root
  Basic auth, `no_log: true`, and the dual apply guard.

  > **This lands here, not in plan-010.** plan-011 executes first and is the first plan to need a
  > second dashboard, so it owns the generalization; plan-010's Epic 5 then only **appends its
  > entry**. Getting this backwards would have both plans refactoring the same task.

  *depends-on: 5.2*

- **Issue 5.4** — **Author `roles/openobserve/files/dashboards/postgres.json`** ("PostgreSQL — CT
  107"), following the `claude-code.json` golden template (`"version": 5`, `"dashboardId": ""`,
  tabs → panels → queries, `queryType: "sql"`, `customQuery: true`, 24-column grid). Panels:
  connections vs `max_connections`, commits/rollbacks, cache hit ratio, database size, deadlocks and
  lock waits, index vs sequential scans, and WAL age.

  > **Cache hit ratio comes from the counters Issue 5.2 enables.** `postgresql.blks_hit` and
  > `postgresql.blks_read` both ship `enabled: false`, so they are turned on explicitly rather than
  > derived from `postgresql.blocks_read`'s `source` attribute (`heap_hit`/`idx_hit`/… against the
  > matching `*_read` values) — that derivation is correct but table-scoped
  > (`db.collection.name`), so it would need aggregating across tables for a single ratio.

  > **Read the real column names before freezing the SQL.** The plan-008 precedent applies: query
  > `GET /api/default/streams?type=metrics` after first ingest and record how `postgresql.*` metric
  > names actually flatten, rather than assuming. Mind the temporality, which is **not** uniform:
  > Sums are cumulative — `commits`, `rollbacks`, `blocks_read`, `index.scans` monotonic; `backends`
  > and `db_size` non-monotonic — so plot a **delta/rate**, never `sum(value)` (that idiom belongs to
  > `claude-code.json`, whose counters are delta) and not a bare `max(value)` either, which would
  > show a running total rather than a rate. `connection.max`, `wal.age` and `wal.lag` are
  > **Gauges** with no temporality: take `max(value)` or `last(value)`. The **five** series enabled by
  > Issue 5.2's stanza split across both categories: `deadlocks`, `sequential_scans`, **`blks_hit`
  > and `blks_read`** are **monotonic Sums** (delta/rate, like `commits`); `database.locks` is a
  > **Gauge** (`max`/`last`). `blks_hit`/`blks_read` are database-scoped (`db.namespace`) — **compute
  > the cache-hit ratio from rates, not lifetime totals**, or the panel shows an all-time average
  > rather than current behaviour. Do not confuse them with `postgresql.blocks_read`, a *different*,
  > table-scoped metric.

  *depends-on: 5.3 · Capability Gate: Postgres metrics present in OpenObserve*

- **Issue 5.5** — **Verify:** `postgresql.*` metrics arrive in OpenObserve; the dashboard renders
  with every panel returning rows; the plan-008 "Claude Code Usage" dashboard is unchanged; and a
  re-run upserts without duplication. *depends-on: 5.4*

### Epic 6 — reconcile

- **Issue 6.1** — Close [#10](https://github.com/dixson3/d3-pxe/issues/10) with a reference to this
  plan; notify that plan-010's *plan-011 complete* gate is now satisfiable.
- **Issue 6.2** — File two repo-level follow-ups surfaced by the investigation: the missing
  `MOUNTS.md` ↔ `pve_storage/defaults/main.yml` dataset-property **drift edge** (this plan's own R7
  names it), and the two-key bind vocabulary in `ansible_ledger_check.py` being a silent-drift trap
  for any third bind shape.

## Risks & Mitigations

| ID      | Risk                                                                                                                                                                                                                                                                                                                                      | Severity | Mitigation                                                                                                                                                                                                                                                                                                                                                                                                    |
| :------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **R1**  | **uid-pin ordering.** `apt install postgresql-17` creates and owns the `postgres` account. If it installs before uid 10006 is pinned, the cluster initdb's under a Debian system uid onto a `0700` mapped dataset.                                                                                                                        | **high** | Issue 3.2 pins **before** 3.3 installs, mirroring `roles/caddy` ("pin identity BEFORE install"). Dataset is pre-created `10006:10006 0700` by 2.1. **The failure mode is fail-closed** — `postgresql-common`'s postinst creates the account only if absent, and a mis-ordered install dies on permission-denied rather than corrupting silently. Issue 3.5 verifies ownership from both host and guest views. |
| **R2**  | **Data loss on a rebuild.** PGDATA lives on `pool1` so the CT is disposable — but only if the dataset is genuinely never destroyed with the guest.                                                                                                                                                                                        | high     | Dataset lifecycle is owned by `pve_storage`, not `pve_lxc`. **Issue 4.5 proves it** with a real destroy/recreate drill behind its own gate, run before any consumer holds real data.                                                                                                                                                                                                                          |
| **R3**  | **Logical data loss.** A ZFS mirror is redundancy, not backup: it covers no `DROP DATABASE`, bad migration, or pool-level corruption. The Garage dumps address the **logical** failures only — they live on the same `pool1` mirror, so pool-level corruption still takes both. #51's full Sanoid/syncoid + Restic tier is unimplemented. | high     | **Issues 4.1/4.2 implement an interim `pg_dump` timer** to Garage, not waiting on #51. **Issue 4.5 proves an actual restore**, not just a dump. Issue 4.6 records that #51 still owns the off-host half, and that `vzdump` does not cover bind-mounted data. ZFS snapshots are explicitly deferred to #51 (Issue 4.3). Residual exposure: no **off-host** copy, and Garage shares the `pool1` mirror.         |
| **R4**  | **Per-consumer isolation.** A default cluster grants `CONNECT` to `PUBLIC`, so any consumer could reach any other's database — invisible with one consumer.                                                                                                                                                                               | **high** | Issue 3.6 applies owner-first `ALTER DATABASE`, `REVOKE ALL ON DATABASE … FROM PUBLIC`, owner-scoped `GRANT`, and per-database `REVOKE ALL ON SCHEMA public`, backed by six per-consumer `pg_hba` CIDRs. Issue 3.9 **proves** it with a negative cross-consumer test using a real second entry.                                                                                                               |
| **R5**  | **Prerequisites absent.** `community.postgresql` is not in `requirements.yml` and `psycopg2` is in no package requirement — Epic 3 could not run.                                                                                                                                                                                         | medium   | Issues 1.1 (PVE-PKG-021 amendment + `PVE-PKG-100`) and 1.3 (`requirements.yml`) add both before Epic 3 starts.                                                                                                                                                                                                                                                                                                |
| **R6**  | **Locale/encoding is irreversible.** `pg_createcluster` inherits the system locale; a wrong choice needs a dump/restore to undo.                                                                                                                                                                                                          | medium   | Pinned explicitly in `createcluster.conf` **before** install (Issue 3.3), recorded normatively in `PVE-PKG-101`, and verified in Issue 3.5.                                                                                                                                                                                                                                                                   |
| **R7**  | **`recordsize` mismatch.** `16K` suits Postgres' 8K pages, but every other config/state dataset says "do not force a value." `MOUNTS.md` and `pve_storage/defaults` must agree — a de-facto drift edge **not** listed in `DRIFT-CHECK.md`.                                                                                                | low      | Decide once in Issue 1.2, state identically in both files with the rationale inline. Issue 6.2 files the missing drift edge upstream.                                                                                                                                                                                                                                                                         |
| **R8**  | **First database guest — no precedent** for tuning or major-version upgrades.                                                                                                                                                                                                                                                             | low      | Conservative: Debian's packaged `postgresql-17`, `state: present`, default tuning apart from `listen_addresses`, `max_connections`, and `shared_buffers`. Major-version upgrades are explicitly out of scope; binding the dataset at the *parent* keeps `pg_upgradecluster` available for a future plan.                                                                                                      |
| **R9**  | **Config lives on rootfs**, not the bind, so a CT rebuild loses `postgresql.conf`/`pg_hba.conf` until Ansible re-converges.                                                                                                                                                                                                               | low      | Accepted and stated. The role is the source of truth; re-converge restores it. Issue 4.5's drill exercises exactly this path, and the Issue 3.4 adopt branch is what makes the claim true rather than assumed.                                                                                                                                                                                                |
| **R10** | **Fleet-wide observability regression.** Issue 5.2 edits a role deployed to the `pve` host and every guest; a template error takes out telemetry everywhere.                                                                                                                                                                              | **high** | Gated behind *otel_agent host-side apply authorized* per PVE-OBS-001, with a byte-identical proof across every other `otel_targets` member required before apply (SC19). Identical treatment to plan-010's equivalent change.                                                                                                                                                                                 |
| **R11** | **The `postgresql` receiver silently collects nothing** if `pg_hba` rejects loopback or `REVOKE ALL … FROM PUBLIC` blocks `CONNECT` — both are consequences of this plan's own isolation model.                                                                                                                                           | medium   | Issue 5.1 handles both explicitly: a `host all otel_monitor 127.0.0.1/32` line, and a per-database `GRANT CONNECT` folded into the existing `postgres_databases` loop so a new consumer stays a data append. SC17 proves metrics actually arrive.                                                                                                                                                             |

## Success Criteria

1. `uv run scripts/ansible_ledger_check.py` reports verbatim:
   `OK — 7 guest(s) [caddy, calibreweb, garage, garage-webui, openobserve, plex, postgres] + shared ids agree with the ledgers.`
2. `uv run scripts/md_table_align.py --check` passes on every edited ledger and doc.
3. `ansible-playbook host.yml --check --diff` shows **zero delta** for all pre-existing guests.
4. `RESERVATIONS.md` "Next free" **still reads** index `07` / `192.168.7.106` / CTID `106`, with the
   out-of-order note present — this plan advances nothing, and the ledger is true at every instant.
5. CT 107 runs unprivileged on `vmbr1` at `192.168.7.107` with a UniFi Fixed-IP and its
   RESERVATIONS row flipped to `active`.
6. `zfs list pool1/postgres` shows the dataset mounted at `/pool1/postgres`, owned `10006:10006`,
   mode `0700`; `psql -c 'SHOW data_directory'` returns a path under `/var/lib/postgresql/17/main`
   resolving onto the dataset; ownership reads `postgres:postgres` from the guest view.
7. `SHOW lc_collate` and `SHOW server_encoding` return the pinned `C.UTF-8` / `UTF8`.
8. **Positive access test:** from inside CT 107,
   `PGPASSWORD="$(op read 'op://Y-Home/litellm-postgres/password')" psql -w "postgresql://litellm@192.168.7.107:5432/litellm" -c 'select 1'`
   succeeds over TCP with `scram-sha-256`.
9. **Negative access test (range):** run **from the `pve` host (`192.168.7.60`)**, which genuinely is
   outside the guest block. `psql` is not installed there and installing it would be a host mutation,
   so use a `python3` socket probe (python3 is already present on `pve`) that opens a TCP connection
   to `192.168.7.107:5432`, sends a PostgreSQL `StartupMessage`, and asserts the server replies with
   an `ErrorResponse` containing **`no pg_hba.conf entry`**. That is the server-side rejection this
   criterion exists to prove — it fires *before* any password exchange, so it can never be confused
   with a credential failure.

   > **Probe requirements, so a failure is diagnosable rather than ambiguous.** The `StartupMessage`
   > must carry both a `user` and a `database` parameter (omitting `user` yields "no PostgreSQL user
   > name specified in startup packet" and the assertion fails for the wrong reason). Use **distinct
   > exit codes**: `0` = rejected by `pg_hba` (criterion met), `1` = rejected for some other reason,
   > `2` = connected or closed silently (criterion **not** met), `3` = could not reach the host at
   > all. Collapsing connect-failure into the same code as wrong-rejection wastes a debugging cycle.

   > **The control node is NOT a valid venue for this test.** It is `192.168.7.115` — **inside**
   > `.100–.149`, and therefore inside `192.168.7.112/28`, one of the six permitted CIDRs. Earlier
   > drafts of this plan (and of plan-010's gate rationale) claimed otherwise; that claim was
   > **wrong**. The six-CIDR fix in an earlier revision verified the CIDRs cover `.100–.149` exactly
   > — which is precisely what keeps a control-node connection *permitted*.
   >
   > **Accepted consequence, stated rather than hidden:** the operator's workstation can reach the
   > `litellm` database over TCP whenever it holds a valid credential. Per-database `pg_hba` lines
   > and the isolation grants still confine it to that one database. If this is unwanted, the fix is
   > a UniFi fixed-IP reservation moving the control node outside `.100–.149` — deliberately left as
   > an operator choice, not silently assumed.
10. **Negative access test (isolation):** with the second `postgres_databases` entry applied,
    consumer A's credential is **rejected** when connecting to consumer B's database — and also when
    connecting to the `postgres` maintenance database.
11. **Socket path intact:** `sudo -u postgres psql -c 'select 1'` succeeds, proving the whole-file
    `pg_hba` template retained the `local … peer` lines the dump timer and cluster maintenance need.
12. **Add-a-consumer is a data append:** the second entry was added and applied with **no edit to
    role logic** (`git diff` touches only **inventory**, never `tasks/` — `postgres_databases` lives in
    `host_vars/postgres.yml` so both the `postgres` and `otel_agent` plays can read it).
13. **A backup exists off-guest and is VALID:**
    `aws --endpoint-url http://192.168.7.103:3900 s3 ls s3://pg-backups/` shows a dated
    `--globals-only` dump and a per-database `-Fc` dump, **and** streaming the dump back through
    `pg_restore -f /dev/null` succeeds — a full archive read. Presence alone would not catch a
    truncated upload, and neither would `pg_restore -l` (front-of-file TOC only); `set -euo pipefail`
    in the unit is the primary control.
14. **R2 — survival:** after a deliberate CT 107 destroy and recreate plus a full role re-converge,
    `pool1/postgres` survived, the adopt branch brought the existing cluster back online without an
    `initdb`, the UniFi Fixed-IP still resolves `.107`, and **the canary rows are present with no
    restore performed**.
15. **R3 — recoverability:** after `DROP DATABASE litellm` **and `DROP ROLE litellm`** (dropping the
    database alone would leave the role in place and make the globals replay a no-op, so the
    owner-role-must-pre-exist proposition would go untested), restoring globals → `createdb` →
    `pg_restore -Fc` returns the canary rows intact. (Distinct from SC14: survival and
    recoverability are separate propositions.)
16. CT 107 appears in OpenObserve with `otel_agent` logs and **hostmetrics**.
17. **Database-level metrics:** `postgresql.*` series from CT 107 are queryable in OpenObserve
    (connections, commits/rollbacks, blocks read/hit, database size, deadlocks).
18. **`otel_monitor` is scoped, not privileged:** it holds `pg_monitor` and `CONNECT` only — it can
    read stats views and **cannot** read consumer table data (verified by a denied `SELECT` — note it
    fails at the *schema* level, "permission denied for schema public", because Issue 3.6 also revokes
    `ALL ON SCHEMA public FROM PUBLIC`; the criterion is still satisfied).
19. After Issue 5.2, **both** `ansible-playbook guests.yml --check --diff --tags otel_agent` **and**
    `ansible-playbook host.yml --check --diff --tags otel_agent` show **zero delta** for every
    `otel_targets` member other than `postgres`. The host side matters most — `otel_targets` is
    `pve_hosts` + `lxc_guests`, and `pve` is where R10's blast radius is worst — so the criterion
    names both commands, as the gate already does.
20. **The collector survived the change:** `systemctl is-active otel_agent` on CT 107 returns
    `active`, and SC16's hostmetrics and logs are still arriving — distinguishing "collector healthy"
    from a receiver misconfiguration that killed the whole unit.
21. The **"PostgreSQL — CT 107"** dashboard renders at `observe.dixson3.net` with every panel
    returning rows; re-running the play upserts without duplication; and the plan-008 **"Claude Code
    Usage"** dashboard is byte-unchanged.
22. A second **apply** run of `site.yml` reports **`changed=0`** for CT 107. (`--check` runs are
    excluded — `community.general.zfs` over-reports `changed` under check mode, per the finding.)
23. `pool1/postgres` is recorded as precious in `MOUNTS.md`/SPEC with the #51 linkage, and the
    residual gap after this plan — **no off-host copy beyond Garage, which is on the same physical
    host** — is stated explicitly rather than implied.
24. Issue #10 is closed with a reference to this plan.

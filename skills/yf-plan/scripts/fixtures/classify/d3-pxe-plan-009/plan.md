---
deliverable_class: standard
source_plan: plan-009-james-dixson-4f56e2
source_repo: d3-pxe
---
# Plan: Single /data hardlink tree + unprivileged-LXC idmap: build pool1/data, migrate Plex and Calibre-Web onto it, and extract shared pool1 storage into a pve_storage role / storage.yml

## Upstream Issues
| Issue | Title                                                              | Disposition | Notes                                                                                     | Resolved By           |
| :---- | :----------------------------------------------------------------- | :---------- | :---------------------------------------------------------------------------------------- | :-------------------- |
| #42   | Storage: single /data hardlink tree + unprivileged-LXC idmap       | include     | Primary driver — defines the `pool1/data` layout + idmap + backup policy                  | this plan             |
| #23   | Extract shared pool1 storage into a pve_storage role / storage.yml | include     | Full extraction: all `pool1` dataset tasks move out of `pve_host`                         | this plan             |
| #33   | Epic: Provision self-hosted *arr media stack (research 057)        | partial     | This plan is the storage FOUNDATION that unblocks #33; it does not build any *arr service | unblocks (not closed) |

## Epics

### Epic 1: Extract `pve_storage` role (#23) — proven no-op refactor
- Issue 1.1: Create `roles/pve_storage` (dataset reconcile + `media` group tasks moved from
  `pve_host/tasks/zfs.yml`); move the `pool1_datasets` var to the role's defaults.
- Issue 1.2: Add `storage.yml` playbook and wire it into `site.yml` **before** guest provisioning.
  - depends-on: 1.1
- Issue 1.3: Remove the ZFS/dataset + media-group tasks from `pve_host`; keep it host-agnostic.
  - depends-on: 1.2
- Issue 1.4: Prove the refactor is faithful (C4): (a) `git diff` shows the moved tasks +
  `pool1_datasets` var are byte-identical to the originals; (b) a converge shows `changed=0` on
  the datasets, **interpreting the documented `community.general.zfs` `--check` over-report**
  (trust live ZFS props, not the `--check` changed count); (c) `ansible_ledger_check.py` stays
  green. Do NOT use `--check` changed-count as the oracle.
  - depends-on: 1.3
  - resolves-upstream: #23 (include)

### Epic 2: Layout redefinition + SPEC/ledger reconciliation
- Issue 2.1: Amend SPEC.md — **name PVE-STO-002 as the amended requirement** (single shared
  `pool1/data` deliberately departs from its per-service-dataset rule; record the lost
  independent-snapshot granularity, C5), PVE-STO-003 wording for the single `pool1/data` tree,
  §6.1 media "Guest(s)" → `plex, calibreweb`, §8 CT 100/101 bind rows. (Gated on SPEC-amendment
  approval.)
- Issue 2.2: Redefine `pool1_datasets` in `pve_storage` to the single `pool1/data` dataset +
  plain-dir servarr tree (`root:media 2775` setgid); mark the media child datasets and
  `pool1/calibre-library` for retirement.
  - depends-on: 2.1
- Issue 2.3: Update MOUNTS.md (new `pool1/data` dataset row, revised binds, idmap-dependency
  note) and run `ansible_ledger_check.py` green.
  - depends-on: 2.2

### Epic 3: Migrate Plex (CT 100) onto `/data`
- Issue 3.1: Guarded one-time ZFS migration (C8) — `zfs snapshot -r pool1/media@pre-plan009`,
  `pct stop 100`, `zfs destroy` the **empty** media child datasets, then **`zfs rename pool1/media
  → pool1/data`** (metadata-only; snapshot travels — do NOT destroy+recreate the parent, which
  would drop the safety snapshot), then create the plain-dir servarr tree. Idempotent via
  state/`creates` guards keyed on `pool1/data` existing.
  - depends-on: 2.3
- Issue 3.2: Repoint `host_vars/plex.yml` bind to `/pool1/data/media → /data/media`, then
  **destroy+recreate CT 100** so `100.conf` is re-rendered clean from host_vars (C1 — a
  `host_vars` edit alone leaves stale `lineinfile` bind/idmap lines pointing at the renamed
  source → `pct start` fails). Follow the **plan-003 rebuild runbook** (N1), not a bare start —
  a recreated CT is a bare debian rootfs: (1) `pct destroy 100` (a deliberate live op — there is
  **no** destroy task in `pve_lxc`; `lifecycle.yml` is `state: present`/`update: true` only);
  (2) `host.yml --tags apply -e pve_lxc_apply_lifecycle=true` (create-stopped, clean conf);
  (3) `bootstrap.yml -e guest=plex` (python/sshd/host-key/known_hosts refresh); (4) `guests.yml`
  (reinstall NVIDIA userspace + plexmediaserver); (5) start. Plex config **survives** on the
  `/pool1/plex-config` bind. Then re-point Plex library roots to `/data/media/{movies,tv,music}`.
  - depends-on: 3.1
- Issue 3.3: Verify Plex healthy — libraries scan, GPU transcode intact (PVE-GPU-005). Prove
  hardlink + atomic move **at host level** on the single dataset (`ln /pool1/data/torrents/…
  /pool1/data/media/…` yields the **same inode** via `stat`/`ls -i`) — the test is a dataset
  property, run on the host, NOT inside CT 100 (which binds only `/data/media`, C6).
  - depends-on: 3.2
  - resolves-upstream: #42 (include, part 1)

### Epic 4: Migrate Calibre-Web (CT 101) onto `/data`
- Issue 4.1: Cold, safe one-time copy (C3) — `pct stop 101` (Calibre is sole `metadata.db`
  writer), `zfs snapshot pool1/calibre-library@pre-plan009`, copy `pool1/calibre-library` → a
  **temp dir under `pool1/data`** then **atomic `mv` into `/data/media/books`**; idempotency
  guarded by a **post-completion sentinel** (a marker written only after the copy fully finishes),
  NOT a `creates:` on `metadata.db` (which a partial copy would falsely satisfy). Then
  **`chown -R :media /data/media/books`** (N3 — the mv'd existing books retain `calibreweb:calibreweb`;
  setgid only affects *new* files, so the copied tree needs an explicit recursive group fix to
  match the shared-media model). Verify tree + `metadata.db` integrity
  (`sqlite3 … 'PRAGMA integrity_check'`) before proceeding.
  - depends-on: 2.3
- Issue 4.2: Set `host_vars/calibreweb.yml` bind to `/pool1/data/media → /data/media` and the
  **full re-tiled gid-axis idmap** (C2) — insert media 10000 1:1 into the whole 0–65535 gid axis:
  `g 0 100000 10000` / `g 10000 10000 1` / `g 10001 110001 1` / `g 10002 10002 1` /
  `g 10003 110003 55533` (a bare `g 10000 10000 1` add would overlap the existing `g 0 100000
  10002` block → LXC rejects). uid axis unchanged (media is gid-only). Then **destroy+recreate
  CT 101** via the plan-003 rebuild runbook (N1): `pct destroy 101` → `host.yml --tags apply -e
  pve_lxc_apply_lifecycle=true` → `bootstrap.yml -e guest=calibreweb` → `guests.yml` (reinstall
  calibre-web). **CT 101's `app.db` (admin user, settings, library path) lives on rootfs and is
  re-initialized by the `calibreweb` role on recreate** (N2 — not "survives"; acceptable, no
  irreplaceable state there — the library is the bind). The role sets calibreweb into group
  `media` + `UMASK=0002` and points the library setting at `/data/media/books`.
  - depends-on: 4.1
- Issue 4.3: Verify Calibre-Web serves the library from `/data/media/books` (library loads,
  `metadata.db` intact); **only then** retire the `pool1/calibre-library` dataset;
  `ansible_ledger_check.py` green.
  - depends-on: 4.2
  - resolves-upstream: #42 (include, part 2)

### Epic 5: Backup policy (documentation only)
- Issue 5.1: Document the config/DB-vs-library backup policy in SPEC — including the **reduced
  per-service snapshot granularity** from the single `pool1/data` consolidation (C5) and its
  effect on the backup unit boundary; file a follow-up GH issue for the Sanoid/syncoid + Restic
  implementation (explicitly out of scope here).

## Risks & Mitigations

| Risk                                                       | Severity | Mitigation                                                                                                                                                                                               |
| :--------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stale `lineinfile` conf lines brick `pct start` (C1)       | High→Low | `pve_lxc` `raw_conf.yml` does not prune changed lines → **destroy+recreate CT 100 & 101** for a clean re-rendered conf (plan-003 precedent); state survives on binds.                                    |
| Overlapping calibreweb idmap rejected by LXC (C2)          | High→Low | Full re-tiled 0–65535 gid axis in Issue 4.2 (not a bare add); recreated CT eliminates any residual overlap.                                                                                              |
| Live Plex outage during migration                          | Low      | Metadata-only `zfs rename` (EXP-001, greenfield) → one stop / recreate / start; `@pre-plan009` snapshot travels with the rename; empty libraries re-point free.                                          |
| Calibre-Web `metadata.db` corruption during the ~2 GB copy | Medium   | `pct stop 101` (sole DB writer); pre-copy `@pre-plan009` snapshot; copy-to-temp + atomic `mv`; sentinel guard (not a `metadata.db` `creates:`); integrity_check + verify serving before retiring source. |
| Child datasets silently defeat hardlinks                   | High→Low | Single flat `pool1/data`, plain dirs only; Issue 3.3 host-level cross-dir hardlink same-inode test.                                                                                                      |
| Role-extraction regression (unfaithful move)               | Medium   | Epic 1.4 git-diff task/var identity + converge `changed=0` interpreting the zfs `--check` over-report (C4) — not a `--check` changed-count oracle.                                                       |
| `pve_lxc` idmap fork                                       | Low      | EXP-002: zero `pve_lxc` change; idmap/bind driven purely by `host_vars` + ledger; checker enforces from §6.1 (GH #43).                                                                                   |
| Lost per-service snapshot granularity (PVE-STO-002, C5)    | Low      | Deliberate, SPEC-amended trade-off; recorded in Issue 2.1 + Epic 5 backup-policy design.                                                                                                                 |

## Success Criteria

- `pve_storage` role owns **all** `pool1` datasets; `pve_host` has **zero** ZFS/dataset tasks;
  the extraction is proven faithful by git-diff task/var identity + a `changed=0` converge (C4)
  before any layout change.
- A single `pool1/data` dataset exists with the plain-dir servarr tree; **no** media child
  datasets; a **host-level** cross-directory hardlink test (`/pool1/data/torrents/… ↔
  /pool1/data/media/…`) yields the **same inode** (hardlink + atomic move proven).
- Plex serves from `/data/media/{movies,tv,music}`, GPU transcode intact, healthy; CT 100
  recreated with a clean conf (no stale bind/idmap lines).
- Calibre-Web serves its library from `/data/media/books`; `metadata.db` passes
  `integrity_check`; CT 101 recreated with the re-tiled idmap; `pool1/calibre-library` retired
  only after serving is verified.
- `ansible_ledger_check.py` green for all guests; `ansible-playbook site.yml --check` idempotent
  (no unexpected changes) after apply.
- SPEC/MOUNTS/§6.1 reconciled; backup policy documented; follow-up backup issue filed.
- #42 resolved, #23 resolved, #33 unblocked (not closed).

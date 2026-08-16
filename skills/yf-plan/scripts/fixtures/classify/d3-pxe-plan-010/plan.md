---
deliverable_class: standard
source_plan: plan-010-james-dixson-49050b
source_repo: d3-pxe
---
# Plan: Deploy the LiteLLM LLM proxy + MCP gateway on pve (CT 106), exposed via Caddy at agents.dixson3.net, with Bedrock + OpenRouter + future Ollama backends and OpenObserve OTel dashboards

## Upstream Issues

| Issue                                              | Title                                                                           | Disposition | Notes                                                                                                                                                                                                                               | Resolved By                 |
| :------------------------------------------------- | :------------------------------------------------------------------------------ | :---------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------- |
| [#29](https://github.com/dixson3/d3-pxe/issues/29) | Add LiteLLM AI Gateway                                                          | include     | The primary driver. Its stated dependency on an observability backend (#7) is satisfied — plan-006 shipped OpenObserve CT 104 — so the gateway ships instrumented per the issue's intent.                                           | Issue 6.1                   |
| [#10](https://github.com/dixson3/d3-pxe/issues/10) | Add PostgreSQL                                                                  | **moved**   | Resolved by **plan-011** (`Incubator/postgres/plans/plan-011-james-dixson-150357/`), not this plan — see the D1 resolution below. This plan is a *consumer* of CT 107, not its owner.                                               | plan-011                    |
| [#47](https://github.com/dixson3/d3-pxe/issues/47) | SPEC: require OTEL telemetry from new guests/services                           | partial     | This plan *complies* with the proposed PVE-OBS-002 (telemetry-by-default, OTEL-native preference) and is cited in the issue as a target consumer, but does **not** perform the SPEC amendment itself. The amendment stays with #47. | Issue 5.1 (compliance half) |
| [#26](https://github.com/dixson3/d3-pxe/issues/26) | Investigate Tailscale vs Cloudflare Tunnels for exposing Caddy-fronted services | exclude     | Out of scope by scoping decision S4 — `agents.dixson3.net` is LAN-only, matching every existing vhost. External reachability is a separate, security-significant plan.                                                              | n/a                         |
| [#30](https://github.com/dixson3/d3-pxe/issues/30) | Add Authelia + LLDAP SSO/IdP stack                                              | exclude     | Gateway auth is LiteLLM virtual keys, not SSO. The admin UI's session auth is deliberately left LAN-only rather than blocked on an IdP.                                                                                             | n/a                         |

Full untruncated issue bodies are captured under [`references/`](references/).

## Epics

### Epic 1 — SPEC & ledger reconciliation

- **Issue 1.1** — SPEC.md: **replace** the existing **§7.10** placeholder (added by plan-011, and reading *"Reserved for plan-010 … Deliberately empty — the gap is intentional"*) — do not append beneath it, which would leave a self-contradicting section. Likewise the §8 guest row and §10 manifest rows are now **insertions into populated tables**. §7.10 becomes **LiteLLM gateway guest (CTID 106)**: `PVE-PKG-090` (base `python3`,
  `openssh-server`, `nodejs`, **`postgresql-client`** — needed to exercise the CT 107 connection
  from the consuming side), `PVE-PKG-091` (pinned `litellm[proxy,extra_proxy]==1.95.0` +
  `fastapi==0.140.6` in a venv; `litellm` service account; two systemd units; listens on
  **`0.0.0.0:4100`**; **no persistent service state on rootfs** — all durable state in CT 107, local
  rootfs holds only the venv and the rebuildable Prisma engine cache; Caddy-fronted),
  `PVE-PKG-092` (secrets via 0600 `EnvironmentFile` from 1Password, mirroring PVE-AUTH-002, with the
  **salt key immutable for the life of the deployment**), `PVE-PKG-093` (OTel + Prometheus telemetry
  via the local `otel_agent`). Add the §8 guest row on the CT-105 **bindless** template, §10 manifest
  rows, and a §11 amendment-log entry citing #29. **No §6.1 row** — PVE-GUEST-003.
- **Issue 1.2** — `RESERVATIONS.md`: Reservations row for CT 106 (`Status: pending` → `active` in
  2.2); advance **Next free** `07 → 09` / `.108` / CTID `108` in a **single** step, and remove
  plan-011's out-of-order note now that both slots are claimed. **No `MOUNTS.md` edits** — CT 106 is
  bindless. *depends-on: 1.1*
- **Issue 1.3** — Inventory: `hosts.yml` entry under `lxc_guests` (auto-enrolls `otel_agent`); a
  `guests.yml` play before the trailing whole-group otel play. *depends-on: 1.1*

### Epic 2 — CT 106 provisioning

- **Issue 2.1** — `inventory/host_vars/litellm.yml`, full fact set: `ctid: 106`, `hostname`,
  `hwaddr: BC:24:11:00:07:00`, `reserved_ip: 192.168.7.106`, `bridge: vmbr1`, `ip: dhcp`,
  **`ostemplate`** (PVE-CT-004 — the create *fails hard* on a missing volid), `cores: 2`,
  `memory: 4096`, `swap: 1024`, `onboot: true`, `unprivileged: true`, `nesting: true`,
  `rootfs_storage: local-zfs`, **`rootfs_size: 16`** (the venv is ~477 MB and the Prisma engine cache
  ~66 MB; 16 GiB leaves room for logs, apt cache, and a version bump without a resize),
  **`idmap: []`** with the PVE-GUEST-003 comment, **no bind keys**, plus
  `otel_agent_traces_sampling_pct: 100`. Provision via `pve_lxc`; prove existing guests render
  **byte-identical**. *depends-on: 1.2, 1.3 · Capability Gate: PVE apply token*
- **Issue 2.2** — Bootstrap `-e guest=litellm`; operator sets the **UniFi Fixed-IP** for
  `BC:24:11:00:07:00` → `.106` after first appearance (PVE-NET-005); flip the RESERVATIONS row to
  `active`. *depends-on: 2.1*
- **Issue 2.3** — `docs/diagrams/pve-guest-layout.d2` + PNG re-render, placed here (not Epic 1)
  because the `e-layout-hostvars` DRIFT-CHECK edge is scoped to `host_vars/*.yml`, created in 2.1.
  *depends-on: 2.1*

### Epic 3 — the `litellm` role

**Hard dependency: plan-011 must be complete** — the migrate unit cannot run without a reachable
Postgres.

- **Issue 3.0** — **Resolve the MCP config-vs-DB question before anything depends on the answer.**
  Stand up LiteLLM + Postgres in a **throwaway local environment** (see the venue note below — not a PVE guest), **with the same `fastapi==0.140.6` constraint** so the throwaway does not walk straight into R2's `ImportError`, declare an MCP server in `config.yaml`, mint
  a key with `object_permission.mcp_servers: ["<that name>"]`, and confirm the tool is reachable.
  EXP-002 could not settle from source whether **config-declared** servers resolve identically to
  DB-registered ones in the permission check. If they do not, `mcp_servers:` is unusable for scoped
  keys and registration must move to the DB — which changes the S7 Ansible boundary and must be an
  operator decision (R5), not an improvised fallback.

  > **Also record the unscoped-key behaviour while you are in there.** `CANARY.md`'s rule is that a
  > property invisible with a single principal needs a second one — and SC11/SC12 only ever prove a
  > *scoped* key **works**, never that an unscoped one is **denied**. But `findings/exp-002` does not
  > establish what LiteLLM does when `object_permission` is **absent**, and allow-by-default is
  > plausible (EXP-002 found a `"no-mcp-servers"` sentinel exists, which hints the default is *not*
  > restrictive). So do **not** assert an unconditional negative criterion here: mint a second key
  > with no `object_permission`, record what actually happens, and only then decide whether a
  > negative SC and a `CANARY.md` fixture are warranted — or whether the sentinel must be set
  > explicitly on every key.

  > **Venue: the control node**, in a local `uv` venv against a local throwaway Postgres — **not** a
  > hand-created PVE guest, which PVE-ANS-001 forbids. That also makes this issue independent of
  > CT 107, so it carries **no** plan-011 gate and **no dependency on Epic 2** — it can run
  > immediately after the Start Gate, in parallel with provisioning. That matters: R5 is a scope
  > *decision point* that could remove MCP from the plan entirely, so resolving it early avoids
  > committing provisioning work that a negative answer would strand.
  >
  > **Throwaway Postgres on the control node (macOS/ARM):** `brew services start postgresql@17`, or
  > a `docker run --rm postgres:17` if Docker Desktop is present. The MCP permission question is
  > architecture-independent.

  *depends-on: none (Start Gate only)*
- **Issue 3.0a** — **AMENDMENT (in-execution).** Fold [EXP-006](findings/exp-006-mcp-config-vs-db.md)
  back into `SPEC.md` (PVE-PKG-091), `CANARY.md`, this plan (Approach, Issues 3.2/3.3/3.4, R14, SC8,
  the plan-011 gate) and `host_vars/postgres.yml`. Filed because the plan shipped a **proved-false**
  premise about Prisma migration safety. *depends-on: 3.0*
- **Issue 3.0b** — **Provision the `litellm_proxy` consumer on CT 107.** Append
  `{name: litellm_proxy, owner: litellm_proxy, password_env: POSTGRES_LITELLM_PROXY_PASSWORD}` to
  `postgres_databases` in `inventory/host_vars/postgres.yml` and converge the `postgres` role. This
  is a **data append only** — no `tasks/` change, so it re-exercises plan-011's SC12. Verify the
  isolation grants apply to the new consumer exactly as `CANARY.md`'s check describes (positive to
  its own database; rejected against `litellm`, `canary` and `postgres`), which also proves the
  proxy *cannot* reach the canary even by misconfiguration. *depends-on: 3.0a · Capability Gate:
  plan-011 complete is NOT required — this runs against the already-live CT 107*
- **Issue 3.1** — Role skeleton (`user → install → config → service`), cloned from `garage_webui`.
  Local system user `litellm` — **no shared id**. *depends-on: 2.2*
- **Issue 3.2** — `install.yml`: `apt` for `nodejs` and `postgresql-client`; `uv venv` + `uv pip install` with the
  constraints file. **Pre-warm the Prisma engine cache** so first boot is not the first network call.
  Assert `litellm --version` reports 1.95.0 **at install time** — this catches the fastapi breakage
  immediately rather than as a mysterious service-start failure.

  > **AMENDED (Issue 3.0a), from live observation:**
  >
  > - **`prisma generate` is a required build step, not a cache warm-up.** Without a generated
  >   client the proxy aborts at startup with `Unable to find Prisma binaries`. Run
  >   `prisma generate --schema=<venv>/lib/python3.*/site-packages/litellm/proxy/schema.prisma`,
  >   with the **venv's `bin/` on `PATH`** — the generator shells out to `prisma-client-py`, and
  >   without it fails with `command not found` **while still exiting 0**.
  > - **The bootstrap is ~302 MB, not the ~66 MB EXP-001 estimated** — and on CT 106 the state dir
  >   settles at **~424 MiB** once Prisma's own `nodeenv` is included (venv a further ~343 MiB).
  >   `rootfs_size: 16` still has ample headroom, but size `StateDirectory=` against ~424 MiB.
  > - **CORRECTED 2026-08-10 — R3's premise does not hold.** `apt install nodejs` does **not** stop
  >   Prisma fetching its own Node: prisma-client-py bootstraps a ~147 MiB `nodeenv` under
  >   `PRISMA_HOME_DIR` even with `/usr/bin/node` present (verified on CT 106). Forcing the system
  >   toolchain via `PRISMA_USE_GLOBAL_NODE` is **not an option** — it needs `npm`, and Debian 13's
  >   `npm` is uninstallable alongside its own `nodejs` 20.x (unmet `node-yallist` deps). The
  >   nodeenv bootstrap is therefore **accepted**; what the role adds instead is **partial-cache
  >   recovery**, because an interrupted first bootstrap fails opaquely with
  >   `npm install prisma@5.17.0 returned non-zero exit status 127`. Clearing
  >   `$PRISMA_HOME_DIR/.cache/prisma-python` and retrying succeeded.
  > - **Assert the version via the CLI, not the Python attribute** — `litellm.__version__` does not
  >   exist (`AttributeError`). Use `litellm --version` → `LiteLLM: Current Version = 1.95.0`.

  *depends-on: 3.1*
- **Issue 3.3** — `config.yml`: template `config.yaml` (0640) and `litellm.env` (0600) with the
  repo's three guards. `model_list` covers Bedrock (`global.` inference profiles, **explicit
  `aws_region_name`**), OpenRouter (with `OR_SITE_URL`/`OR_APP_NAME`), and an **inert** Ollama entry;
  `order` + `fallbacks` for provider preference; default `max_budget`/`rpm_limit`; and
  **`litellm_settings.require_auth_for_metrics_endpoint: true` set explicitly** (it lives under
  `litellm_settings`, *not* `general_settings` where the neighbouring `max_budget`/`rpm_limit` sit —
  a misplaced key is silently ignored and leaves `/metrics` open on the legacy default) rather than relied on as a default
  (EXP-003 records only that it *currently* defaults true, and that older builds defaulted open). `mcp_servers`
  written in whichever form Issue 3.0 established.

  > **RESOLVED by Issue 3.0 ([EXP-006 §1](findings/exp-006-mcp-config-vs-db.md)): `mcp_servers:`
  > stays a templated `config.yaml` block.** Config-declared servers resolve identically to
  > DB-registered ones — LiteLLM resolves the config name to the server's `server_id` at key-mint
  > time, and a scoped key listed *and called* a tool end to end. R5 closes with **no scope change
  > and no operator decision**; the S7 boundary holds.
  >
  > **AMENDED (Issue 3.0a): `DATABASE_URL` targets the dedicated `litellm_proxy` database**, owner
  > role `litellm_proxy`, credential `op://Y-Home/litellm-proxy-postgres` consumed as
  > `POSTGRES_LITELLM_PROXY_PASSWORD` — **not** the `litellm` database.

  *depends-on: 3.2, 3.0, 3.0a · Capability Gate: 1Password items*
- **Issue 3.4** — `service.yml`: both units, including the wait-for-TCP `ExecStartPre` and restart
  policy on the migrate unit; `enabled: true` always, `state: started` only
  `when: litellm_apply_service`.

  > **AMENDED (Issue 3.0a).** The migrate unit's flags are
  > `--skip_server_startup --enforce_prisma_migration_check **--use_v2_migration_resolver**`. The
  > third flag is mandatory, not tuning — without it the v1 resolver force-applies a
  > schema-reconciling diff (see the Approach amendment and
  > [EXP-006 §3](findings/exp-006-mcp-config-vs-db.md)).
  >
  > **Exit status is not sufficient evidence.** With `DATABASE_URL` set but the Prisma client
  > ungenerated, the migrate command printed `Unable to connect to DB … prisma package not found`
  > and **exited 0**, leaving the database empty. Add an `ExecStartPost` (or an Issue 3.5
  > assertion) that the expected `LiteLLM_*` tables actually exist.

  *depends-on: 3.3, 3.0a*
- **Issue 3.5** — **Verify:** `/health/liveliness` 200; `/health/readiness` with
  **`.db == "connected"` asserted from the JSON body**; a completion routes through Bedrock; the
  master key mints a working virtual key (the **S7 capability test**); the declared MCP server is
  listable and callable; re-converge `changed=0`; and a **full `pve` host reboot** brings the
  gateway back to `.db == "connected"` unattended. *depends-on: 3.4*

### Epic 4 — Caddy front door

- **Issue 4.1** — Append one `caddy_sites` entry (`agents.dixson3.net` → `http://192.168.7.106:4100`)
  **plus an explicit `/metrics` deny**. The deny is *not* a pure data append: `Caddyfile.j2` renders
  `reverse_proxy` + `tls` per site with no hook for per-site directives, so the template is
  **generalized** with an optional `site.deny_paths | default([])` block, rendered as an explicit
  named matcher inside a `handle` (not a bare `respond` relying on Caddy's implicit directive
  ordering, which happens to place `respond` before `reverse_proxy` — load-bearing behavior that
  should not be left implicit) — a backward-compatible
  generalization under **PVE-GUEST-002(a)**, the same move plan-005 made for `caddy_sites`, and safe
  because the byte-identical proof below covers it. This fires the `e-routing-caddy-template` edge in
  addition to `e-routing-reservations` and `e-routing-caddy-defaults`; add the `RESERVATIONS.md` Service DNS row here
  (not Epic 1, so `caddy-app-routing.d2`'s DRIFT-CHECK edge is not left red across Epics 2–3); prove
  existing sites render byte-identical; update `docs/diagrams/caddy-app-routing.d2` + re-render.
  *depends-on: 3.5*
- **Issue 4.2** — Operator publishes the Route53 A record; apply caddy; verify LE DNS-01 issuance,
  HTTPS reachability, and that `/metrics` is **not** reachable through the vhost.
  *depends-on: 4.1 · Capability Gate: Route53 A record published*

### Epic 5 — OTel dashboards on `observe`

- **Issue 5.1** — `otel_agent`: add `otlp` to the metrics pipeline (flag-guarded) and a `prometheus`
  receiver scraping the gateway, opt-in per guest.

  > **The scrape must authenticate — this is not optional.** Issue 3.3 sets
  > `require_auth_for_metrics_endpoint: true`, and LiteLLM's `PrometheusAuthMiddleware` reads the key
  > from the `Authorization` header with **no documented loopback exemption**. An unauthenticated
  > scrape 401s, no `litellm_*` series ever reach OpenObserve, and **SC17 and SC19 fail silently** —
  > on a fleet-wide role change, discovered at apply time.
  >
  > **Resolution (operator decision, 2026-08-07): a bearer token via `otel_agent`'s existing
  > `EnvironmentFile`.** The operator mints the key out of band — consistent with S7, since it is an
  > operator-minted key, not Ansible-managed state — delivered through the same 0600
  > `EnvironmentFile` mechanism the role already uses for `OTEL_OO_AUTH_B64`, referenced as
  > `${env:LITELLM_METRICS_TOKEN}`.
  >
  > **⚠ The key must be minted with `allowed_routes: ["/metrics"]` — a plain "read-only" key will
  > 401.** Verified in pinned v1.95.0 source: `/metrics` appears in **no** `LiteLLMRoutes` member, so
  > `PrometheusAuthMiddleware` → `user_api_key_auth` → `RouteChecks.non_proxy_admin_allowed_routes_check`
  > falls through every category and hits `_raise_admin_only_route_exception` unless the key carries
  > an explicit `allowed_routes` (default `None`). Minting it with `allowed_routes: ["/metrics"]` both
  > authorizes the scrape *and* correctly denies the key `/chat/completions`.
  > (`user_role: proxy_admin_viewer` is the alternative; the scoped-route form is tighter.)
  > **Verify before the fleet apply:**
  > `curl -sf -H "Authorization: Bearer $LITELLM_METRICS_TOKEN" http://192.168.7.106:4100/metrics >/dev/null`
  >
  > ```yaml
  > prometheus:
  >   config:
  >     scrape_configs:
  >       - job_name: litellm
  >         scrape_interval: 30s
  >         static_configs: [{targets: ['127.0.0.1:4100']}]
  >         authorization: {credentials: '${env:LITELLM_METRICS_TOKEN}'}
  > ```
  >
  > **Four changes and TWO flags** — not three changes, and not one flag:
  >
  > 1. the `prometheus` receiver — guarded by a new **`otel_agent_litellm_scrape_enabled: false`**;
  > 2. `metric_receivers` gains **two** entries under **two different flags**: `prometheus` under
  >    `otel_agent_litellm_scrape_enabled`, and `otlp` under `otel_agent_otlp_metrics_enabled`
  >    (above). Both default `false` in `roles/otel_agent/defaults/main.yml`, both `true` only in
  >    `host_vars/litellm.yml`;
  > 3. the `LITELLM_METRICS_TOKEN=` line in `otel_agent.env.j2` — follow the
  >    `{% raw %}{% if otel_agent_postgresql_enabled %}{% endraw %}` / `POSTGRES_OTEL_PASSWORD` precedent **already in that
  >    template** (plan-011 added it; the template is no longer unconditional);
  > 4. **the one that is easy to miss** — extend the `environment:` mapping on the config-template
  >    task in `otel_agent/tasks/config.yml` with `LITELLM_METRICS_TOKEN`, plus an
  >    `otel_agent_litellm_metrics_token: "{{ lookup('env', 'LITELLM_METRICS_TOKEN') }}"` default and
  >    a **pre-template** assert. `validate: otelcol validate --config=%s` runs **on the target**,
  >    where the systemd `EnvironmentFile` is not in scope, so a bare `${env:LITELLM_METRICS_TOKEN}`
  >    inside the receiver's `authorization` may fail validation. **Belt-and-braces, not a proven
  >    hard failure:** plan-011's postgres receiver broke because `password` is a *required*
  >    non-empty field, whereas Prometheus's `authorization.credentials` is not — and this receiver
  >    is flag-guarded, so it renders on no host but `litellm`. Follow the plan-011 precedent anyway
  >    (it is free), and prefer `${env:LITELLM_METRICS_TOKEN:-}`.
  >
  > This keeps `/metrics` authenticated, so SC15 and R8 stand. The cost is one additional secret in a
  > fleet-wide role's env file — accepted deliberately over the alternative of disabling auth, given
  > the label set includes `user_email` and `client_ip`.

  > **The guard restructure already shipped — do not redo it.** plan-011 Issue 5.2 (`f64024b`)
  > replaced the `{% raw %}{% if otel_agent_hostmetrics_enabled %}{% endraw %}` wrapper with a
  > `metric_receivers` namespace list (`config.yaml.j2:119-127`). What remains is genuinely
  > necessary: `metric_receivers` currently appends only `hostmetrics` and `postgresql`, so **`otlp`
  > is still absent from the metrics pipeline** and OTLP metrics sent to `:4318` are still silently
  > dropped — EXP-003's finding stands.
  >
  > **Name that flag, and make it default `false`.** Append `otlp` under a **new**
  > `otel_agent_otlp_metrics_enabled: false` in `roles/otel_agent/defaults/main.yml`, set `true` only
  > in `host_vars/litellm.yml`. Do **not** reuse `otel_agent_otlp_receiver_enabled` — it defaults
  > **`true` fleet-wide**, so guarding on it renders `receivers: [hostmetrics, otlp]` on the host and
  > every guest, producing a non-zero delta everywhere and failing SC16 at the plan's
  > highest-blast-radius gate. This mirrors `otel_agent_postgresql_enabled` and its stated rationale.

  This role is deployed to the **`pve` host and every guest**, so per **PVE-OBS-001** the host-side
  apply is gated exactly like other host mutations. Prove every other `otel_targets` member's
  rendered config is byte-identical. Also carries the #47 compliance obligation
  (telemetry-by-default for the new guest).

  *depends-on: 3.5 · Capability Gate: otel_agent host-side apply authorized*
- **Issue 5.2** — **Live schema check:** read `GET /api/default/streams?type=traces` after first
  ingest and record the actual flattened column names and `gen_ai.usage.*` spelling.
  *depends-on: 5.1 · Capability Gate: LiteLLM traces present in OpenObserve*
- **Issue 5.3** — **Append** the LiteLLM entry to `openobserve_dashboards`. The list and the
  loop-based `dashboards.yml` are **already in place from plan-011 Issue 5.3**, which lands first and
  was the first plan to need a second dashboard — so this is a data append, not a refactor. The loop and the
  `openobserve_dashboards` list shipped in plan-011 `40524ba`; `tasks/dashboard.yml` is the included
  per-dashboard task and `files/dashboards/` already holds `claude-code.json` and `postgres.json`. *depends-on: 5.1*
- **Issue 5.4** — Author `files/dashboards/litellm.json` ("LiteLLM Gateway"): Tab 1 *Spend & Usage*
  (metrics, **cumulative → `max(value)`**), Tab 2 *Latency & Traces*. Verify idempotent upsert and
  reachability at `observe.dixson3.net`. *depends-on: 5.2, 5.3*

### Epic 6 — reconcile

- **Issue 6.1** — Close #29; **correct its stale `Depends on: #7 (SigNoz)` line** per S8.
- **Issue 6.2** — File the two upstream LiteLLM issues found by EXP-001 (unbounded `fastapi`
  constraint in the `proxy` extra; the misleading `No module named 'proxy_server'` error masking the
  real `ImportError`).

## Risks & Mitigations

| ID      | Risk                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Severity | Mitigation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **R1**  | **Salt-key loss is unrecoverable.** `LITELLM_SALT_KEY` encrypts stored provider credentials; changing it makes them undecryptable. If never set it **silently defaults to the master key**, so a later master-key rotation breaks everything.                                                                                                                                                                                                                                                                      | **high** | Generate both **once**, distinctly, before first apply; store in `Y-Home/litellm-proxy-keys`; the gate asserts both fields by name. Document immutability in `PVE-PKG-092`.                                                                                                                                                                                                                                                                                                                                                                                                  |
| **R2**  | **The upstream `fastapi` constraint is broken.** A fresh install produces a service that cannot import, behind a misleading error.                                                                                                                                                                                                                                                                                                                                                                                 | **high** | Pin `fastapi==0.140.6` via a constraints file. Issue 3.2 asserts `litellm --version` **at install time**. File upstream (Issue 6.2).                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **R3**  | **Prisma's network bootstrap.** First migration downloads ~66 MB into `$HOME/.cache`, ignoring `XDG_CACHE_HOME`.                                                                                                                                                                                                                                                                                                                                                                                                   | medium   | `StateDirectory=litellm` with `HOME`/`PRISMA_HOME_DIR` under it; `apt install nodejs`; pre-warm in Issue 3.2. `PRISMA_OFFLINE_MODE` + `PRISMA_CLI_PATH` in reserve.                                                                                                                                                                                                                                                                                                                                                                                                          |
| **R4**  | **Migration is fail-open** — LiteLLM warns and serves against a stale schema by default.                                                                                                                                                                                                                                                                                                                                                                                                                           | medium   | Dedicated migrate unit with `--enforce_prisma_migration_check`; serving unit sets `DISABLE_SCHEMA_UPDATE=true`. Failure becomes a visible unit failure.                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **R5**  | **Config-declared MCP servers may not resolve for scoped keys.** If not, registration must move to the DB.                                                                                                                                                                                                                                                                                                                                                                                                         | medium   | **Issue 3.0 resolves this first**, before `config.yaml` is authored. If the answer is negative it is an **operator decision point**, not an automatic fallback: the three options — accept an imperative GET-then-POST-or-PUT reconciliation loop (which *would* breach the S7 boundary S7's rationale explicitly rejects), move MCP registration out of band alongside keys, or drop MCP from this plan — are materially different scopes.                                                                                                                                  |
| **R6**  | **Fleet-wide observability regression.** Issue 5.1 edits a role deployed to the host and all guests; a template error takes out telemetry everywhere.                                                                                                                                                                                                                                                                                                                                                              | **high** | Gated behind *otel_agent host-side apply authorized* per PVE-OBS-001, with a byte-identical proof across every other `otel_targets` member required before apply (**SC16**).                                                                                                                                                                                                                                                                                                                                                                                                 |
| **R7**  | **Weekly releases, no N-1 support.**                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | medium   | Pin exactly. Document an upgrade ritual in `ansible/README.md`: stop → `pg_dump` on CT 107 → bump pin → `prisma generate` → `prisma migrate deploy` → start → **re-assert `select count(*) from plan011_canary` = 3** (SC8 is a one-shot check at first migrate; an upgrade is precisely when a `db push` path could be re-entered, so the assertion must travel with the operation that could break it). Never `state: latest` (PVE-ANS-007 forbids it).                                                                                                                    |
| **R8**  | **`/metrics` exposes `user_email`, `client_ip`, `user_agent`.**                                                                                                                                                                                                                                                                                                                                                                                                                                                    | medium   | `require_auth_for_metrics_endpoint: true` **set explicitly** in Issue 3.3 (not relied on as a default — EXP-003 says only that it *currently* defaults true and warns older builds defaulted open) **plus** an explicit Caddy `/metrics` deny, verified by **SC14** (vhost path) **and SC15** (direct port). Note the bind address is *not* the mitigation — the gateway must listen on the LAN for Caddy to reach it at all.                                                                                                                                                |
| **R9**  | **Admin UI is protected only by the master key** and is LAN-reachable via the vhost.                                                                                                                                                                                                                                                                                                                                                                                                                               | medium   | Accepted under S4 (LAN-only); SSO explicitly excluded (#30). Strong generated master key; revisit if exposure changes.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **R10** | **MCP `stdio` servers spawn child processes inside CT 106**, adding `npx`/`uvx` dependencies.                                                                                                                                                                                                                                                                                                                                                                                                                      | low      | Prefer `http`/`sse` upstreams. Any `stdio` server must add its dependency to the role **and** SPEC §7.10.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **R11** | **Bedrock silently defaults to `us-west-2`** when `aws_region_name` is omitted.                                                                                                                                                                                                                                                                                                                                                                                                                                    | low      | Set explicitly in **every** model entry; assert non-empty in the config template.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **R12** | **Spend runaway.** A LAN-reachable paid-inference gateway whose admin surface is master-key-only (R9) has a financial blast radius distinct from the auth exposure.                                                                                                                                                                                                                                                                                                                                                | medium   | Default `max_budget` and `rpm_limit` in `general_settings` (Issue 3.3), so an unattended or misused key cannot run up unbounded provider cost. Per-key budgets remain an operator lever at mint time (S7).                                                                                                                                                                                                                                                                                                                                                                   |
| **R13** | **Cross-guest boot-order race.** systemd cannot express a dependency across containers. On host reboot, if the migrate oneshot runs before CT 107 accepts connections it fails, never retries (`RemainAfterExit`), and the serving unit never starts — leaving the gateway down until manual intervention.                                                                                                                                                                                                         | **high** | `ExecStartPre` wait-for-TCP against `192.168.7.107:5432` plus `Restart=on-failure` / `RestartSec=15` / bounded `StartLimitBurst` on the migrate unit (Issue 3.4). Proven by **SC18** — a real host reboot must recover unattended.                                                                                                                                                                                                                                                                                                                                           |
| **R14** | **~~Co-tenancy with a permanent test fixture.~~ RESTATED 2026-08-09 (Issue 3.0a) — the original mitigation was unsound.** `--enforce_prisma_migration_check` does **not** make a `db push`-equivalent unreachable: the default (v1) resolver force-applies a `prisma migrate diff --from-url <db> --to-schema-datamodel schema.prisma`, which against a database holding a canary table generated exactly `DROP TABLE "plan011_canary_probe";` (proved live — [EXP-006 §3](findings/exp-006-mcp-config-vs-db.md)). | **high** | **Two independent controls, neither sufficient alone.** (1) The migrate unit passes **`--use_v2_migration_resolver`**, which omits the diff-and-force path (verified: 68 tables created, canary intact). (2) LiteLLM uses a **dedicated `litellm_proxy` database**, so it never co-tenants with objects it does not own — this makes the failure class structurally impossible rather than merely mitigated. `DISABLE_SCHEMA_UPDATE=true` still guards the serving unit. **SC8 verifies the canary survives**, and per R7 that assertion travels with every version upgrade. |
| **R15** | **MCP lives under `_experimental/`** with heavy upstream churn.                                                                                                                                                                                                                                                                                                                                                                                                                                                    | low      | Pinning (R7) bounds the blast radius; MCP servers are config-declared, so a breaking change is a template edit.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

## Success Criteria

1. `uv run scripts/ansible_ledger_check.py` reports verbatim:
   `OK — 8 guest(s) [caddy, calibreweb, garage, garage-webui, litellm, openobserve, plex, postgres] + shared ids agree with the ledgers.`
2. `uv run scripts/md_table_align.py --check` passes on every edited ledger and doc.
3. `ansible-playbook host.yml --check --diff` shows **zero delta** for all pre-existing guests.
4. `RESERVATIONS.md` "Next free" reads index `09` / `192.168.7.108` / CTID `108`, advanced in a
   single step, with plan-011's out-of-order note removed.
5. CT 106 runs unprivileged on `vmbr1` at `192.168.7.106` with a UniFi Fixed-IP, **no `pool1` bind
   and no §6.1 shared id** (PVE-GUEST-003 conformance).
6. `litellm --version` reports `1.95.0` and `uv pip show fastapi` reports `0.140.6`.
7. `litellm-migrate.service` completes successfully; `litellm.service` is active with
   `DISABLE_SCHEMA_UPDATE=true`.
8. **plan-011's canary survived, and LiteLLM never touched its database.** After the migrate
   unit's first successful run, `select count(*) from plan011_canary` in the **`litellm`** database
   still returns **3**, *and* that database contains **no** `LiteLLM_*` tables (LiteLLM's schema
   lives in `litellm_proxy`). Both halves matter: the row count proves the v1 diff-and-force path
   was never taken, and the absence of `LiteLLM_*` tables proves the database separation actually
   held rather than being asserted in config only. Restated 2026-08-09 by Issue 3.0a — this now
   tests a **proved** hazard, not an assumed-safe path.
9. `curl -sf http://192.168.7.106:4100/health/liveliness` returns 200, and
   `curl -s …/health/readiness | jq -e '.db == "connected"'` succeeds — asserted from the JSON body,
   **not** the status code.
10. A chat completion routes through **Bedrock** via a `global.` inference profile. Failover is
   demonstrated by temporarily invalidating `AWS_SECRET_ACCESS_KEY` in `litellm.env` and asserting
   the response's resolved model is the **OpenRouter** deployment.
11. **S7 capability test:** `POST /key/generate` with the master key mints a virtual key, and that
    key immediately authenticates a completion. No keys are recorded in the repo.
12. `GET /v1/mcp/server` lists the declared MCP server, and one of its tools is callable through the
    gateway with a virtual key.
13. The inert Ollama entry does **not** degrade `/health/liveliness` or `/health/readiness`.
14. `https://agents.dixson3.net` serves the gateway with a valid LE certificate, **and**
    `[ "$(curl -so /dev/null -w '%{http_code}' https://agents.dixson3.net/metrics)" = 403 ]` succeeds —
    the metrics label set is not reachable through the vhost.
15. **Direct-port protection:** `[ "$(curl -so /dev/null -w '%{http_code}' http://192.168.7.106:4100/metrics)" = 401 ]` succeeds
    without auth (asserted, not eyeballed — a bare `-w` always exits 0). Binding on the LAN (required for Caddy to reach the gateway at all)
    means the vhost is not the only path — SC14 alone would pass while the label set was fully
    exposed on the direct port.
16. After Issue 5.1, `ansible-playbook guests.yml --check --diff --tags otel_agent` shows **zero
    delta** for every `otel_targets` member other than `litellm`, and the host-side preview was
    reviewed and authorized.
17. The **"LiteLLM Gateway"** dashboard is visible at `observe.dixson3.net` with each panel's query
    returning ≥1 row; re-running the play upserts without duplication; and the plan-008
    **"Claude Code Usage"** dashboard is unchanged.
18. **Reboot recovery:** a full `pve` host reboot brings CT 106 back to
    `/health/readiness` → `.db == "connected"` with **no manual intervention**.
19. CT 106 appears in OpenObserve with `otel_agent` logs, **`litellm_*` Prometheus series**
    (named explicitly — hostmetrics alone would otherwise satisfy a bare "metrics"), and LiteLLM
    traces at 100% sampling.
20. A second **apply** run of `site.yml` reports **`changed=0`** for CT 106.
21. Issue #29 is closed and its stale SigNoz dependency line corrected.

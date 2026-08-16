---
deliverable_class: standard
source_plan: plan-012-james-dixson-abea8d
source_repo: d3-pxe
---
# Plan: Enable TLS on the shared PostgreSQL guest (CT 107) with a real postgres.dixson3.net certificate via ACME DNS-01, so clients can use sslmode=verify-full

## Upstream Issues

No existing issue covers this work — see [`upstream-triage.md`](upstream-triage.md) for the scan
and dispositions. PostgreSQL TLS was never filed because the need did not exist until `pg_hba`
was widened on 2026-08-10. This plan files its own tracking issue at intake.

| Issue                                              | Title                                                                           | Disposition | Notes                                                                                                | Resolved By |
| :------------------------------------------------- | :------------------------------------------------------------------------------ | :---------- | :--------------------------------------------------------------------------------------------------- | :---------- |
| [#26](https://github.com/dixson3/d3-pxe/issues/26) | Investigate Tailscale vs Cloudflare Tunnels for exposing Caddy-fronted services | exclude     | External HTTP exposure, not internal transport security. Touches only at the tailnet, which S6 cuts. | n/a         |
| [#14](https://github.com/dixson3/d3-pxe/issues/14) | Add Caddy (reverse proxy / automatic HTTPS)                                     | exclude     | Source of the DNS-01 pattern reused here, but Caddy cannot front the PostgreSQL wire protocol.       | n/a         |
| [#10](https://github.com/dixson3/d3-pxe/issues/10) | Add PostgreSQL                                                                  | exclude     | Resolved by plan-011. This plan changes CT 107's transport security, not its existence.              | n/a         |

## Epics

### Epic 1 — SPEC & ledger reconciliation

Per AGENTS.md and SPEC §11, this **must land and be approved before any change to the `pve` host or
its guests**. Epic 2's IAM mint is deliberately permitted ahead of *approval* (it depends on 1.2's
authoring only): it touches no PVE surface and is externally revertible — Rollback step 4 deletes
the user and the record.

- **Issue 1.1** — File the tracking issue on `dixson3/d3-pxe` (no existing issue covers this —
  see [`upstream-triage.md`](upstream-triage.md)). Reference it from the SPEC amendment.
- **Issue 1.2** — `SPEC.md`: **amend PVE-PKG-101** — `ssl = on`, absolute `ssl_cert_file`/
  `ssl_key_file` into `/var/lib/postgresql/acme/live/postgres.dixson3.net/`, and **strike the
  "LAN-internal traffic" rationale** for `ssl = off`, which the 2026-08-10 widening already
  invalidated. Add **PVE-PKG-103** covering certificate management: `certbot` +
  `python3-certbot-dns-route53` from Debian apt (`state: present`, PVE-ANS-007 satisfied — EXP-001
  confirmed no pinned binary is needed), certbot state rooted on the `pool1` bind, the
  record-name-conditioned Route53 policy with an explicit note that it is **narrower than
  `caddy-acme-dixson3` by design**, `postgres:postgres 0600` key ownership (D2 — **not** the
  `ssl-cert` group), the `certbot.service` **drop-in** with an explicit statement that it is the
  **stock `ExecStart`** that is inert for this certificate while **`certbot.timer` remains the
  trigger and MUST stay enabled** (D3 — do not write "the packaged timer is inert"; that phrasing
  invites a future reader to mask the sole scheduler), and the expiry-check timer. Update §10 (new
  templates/task file in the `postgres` role — **no new role**) and add a §11 amendment-log entry
  citing 1.1. Also amend the **§8 CT 106 row** (`SPEC.md:460`), which records *"PostgreSQL state on
  `192.168.7.107:5432`"* — Issue 4.1 falsifies it. **No `MOUNTS.md` row and no §6.1 row** (D1/D2 —
  the acme dir needs no bind key, and dropping the `ssl-cert` group removes the id that would
  otherwise have needed pinning), but **do add a note** to `MOUNTS.md`'s `pool1/postgres` row: that
  dataset is described purely as "PostgreSQL cluster — PGDATA" and now also holds ACME account
  material, the server **private key**, *and* the Route53 **IAM secret access key** (see R9).
  Cross-reference [#51](https://github.com/dixson3/d3-pxe/issues/51) from PVE-PKG-103 itself, not
  only from R9 — the off-host backup tier is what turns "key material on a precious dataset" from a
  note into a real exposure. Also record **PVE-ANS-007 conformance** for the `command:`-shaped
  issuance task and the apply-gated asserts; §7.11's new content must not silently weaken the
  validate-under-`--check` requirement. *depends-on: 1.1*

  > **No gate annotation here.** 1.2 *authors* the amendment the gate tests for; annotating it
  > `Gate: SPEC amendment approved` would deadlock Epic 1 against itself at execution wiring.
- **Issue 1.3** — `RESERVATIONS.md`: **widen the Service DNS table's heading**, which currently
  reads *"Names for services fronted by the Caddy reverse proxy (CT 102)"* — S4's row is fronted by
  nothing, and would otherwise contradict the table it sits in. Add the `postgres.dixson3.net` →
  `192.168.7.107` row (`Status: pending`, flipped to `active` in 2.3), noting it is the **first**
  Service DNS name pointing at a guest rather than the proxy, and why (Caddy cannot front the
  PostgreSQL wire protocol). *depends-on: 1.2*

### Epic 2 — credentials & DNS (external systems)

Scheduled **early** and bundled behind one human gate, per AGENTS.md's rule that out-of-`Y-Home` /
elevated-authority work must not stall a deployment mid-way.

- **Issue 2.1** — Mint the `postgres-route53-acme` IAM user and its customer-managed policy via the
  `aws` CLI, with the D4 condition keys. **Prove the negative in the same step**: with the new key's
  credentials, an attempted `ChangeResourceRecordSets` against a *different* record in the zone
  (e.g. a throwaway TXT) must be **denied** — this is SC9's evidence and it is far cheaper to
  capture now than to reconstruct later. *depends-on: 1.2 · Gate: AWS admin credentials*

  > **Why the `1.2` edge.** Minting an IAM user is a real mutation of an external system, and the
  > Epic 1 preamble says the amendment lands before *any* operational change. The SPEC gate's
  > `Blocks:` covers Epic 3 only, so without this edge Epic 2 could mutate AWS ahead of the
  > amendment that describes the credential. The edge — not a second gate — is the right lever: it
  > keeps Epic 2 early (Epic 1 is a documentation commit) while honouring the ordering rule.
- **Issue 2.2** — Create `Y-Home/postgres-route53-acme` in 1Password with fields mirroring
  `caddy-route53-acme` (`aws_access_key_id`, `aws_secret_access_key`, `region`), using the
  **writer** service token. *depends-on: 2.1 · Gate: 1Password writer token*
- **Issue 2.3** — Publish the `postgres.dixson3.net` A record → `192.168.7.107` via the `aws` CLI
  with **admin** credentials (matching every existing Service DNS row — *not* the least-priv DNS-01
  key, which by D4 cannot change an A record at all). Verify resolution, then flip the
  `RESERVATIONS.md` row to `active`. Satisfies **SC1**. *depends-on: 1.3, 2.1*
- **Issue 2.4** — Update the `host` field on the three existing `Y-Home/<consumer>-postgres` items
  (`litellm`, `litellm_proxy`, `canary`) from `192.168.7.107` to `postgres.dixson3.net`. These are
  the values a human or agent actually connects with, per the onboarding recipe at
  `ansible/README.md:318` — leaving them stale would make the documented path and the stored path
  disagree. Placed **here rather than in Epic 4** because the writer token is already gated and held
  in this sitting; AGENTS.md is explicit that elevated-authority work should not stall a deployment
  mid-way. *depends-on: 2.3 · Gate: 1Password writer token*

### Epic 3 — certificate management in the `postgres` role

- **Issue 3.1** — `roles/postgres/tasks/tls.yml`, imported from `main.yml` **between `cluster.yml`
  and `config.yml`**. The position is load-bearing: `config.yml` is what templates `ssl = on`, so
  the certificate must already exist when it runs (D1's pre-flip assertion). Installs the two apt
  packages, creates `/var/lib/postgresql/acme/` on the bind, and templates the AWS
  `EnvironmentFile` at `0600` **onto the bind** (D4 — not rootfs), written **only when the env is
  populated**, plus an apply-path assertion that it exists and is non-empty so a post-rebuild
  cred-less converge fails loudly instead of silently disarming renewal. **State its absolute path,
  owner and mode explicitly** (`/var/lib/postgresql/acme/aws.env`, `postgres:postgres 0600`) — it
  sits under a `0700 10006:10006` dataset root, so who can read it is load-bearing, not incidental.
  Define `postgres_certbot_args` (the three dir flags) once and ship the
  **`/usr/local/bin/postgres-certbot` wrapper** (D3) — every certbot invocation in this plan goes
  through it. **Owns D2's ownership-normalisation task** — the idempotent `find` + `file:` pass over
  `acme/` that R1's adopt-branch mitigation and SC7's `changed=0` both rest on (Issue 3.2 ships the
  deploy hook, which is the *second*, issuance-time copy; without this task the adopt branch — where
  no issuance happens — normalises nothing). Immediately after it, D2's **readability probe**
  (`sudo -u postgres test -r <privkey>`), so the adopt branch re-exercises it every converge.
  **Credential asserts are gated on `postgres_apply_service`**, matching `config.yml:35`.
  **The pre-flip certificate assertion is NOT** — see the carve-out in Issue 3.3, which is
  load-bearing. *depends-on: 1.2*
- **Issue 3.2** — Issuance + deploy hook. `postgres-certbot certonly --dns-route53`, guarded by an
  **apply gate** mirroring `postgres_apply_service` (assert credentials present, `creates:`-style
  idempotence so a re-run does not re-issue), with `environment:` wiring the AWS credentials into
  the task — the EnvironmentFile alone does **not** reach an Ansible `command:`. Ship
  `/usr/local/bin/postgres-cert-deploy.sh` implementing D2's ownership normalisation and the
  **guarded** reload. **Iterate with `--dry-run`** (ACME staging, no live state touched) before
  spending a production issuance — but note certbot **skips deploy hooks under `--dry-run`**, so
  `--dry-run` validates DNS-01 and the IAM policy and **not** the hook. Run
  `postgres-cert-deploy.sh` **directly** against the staging-issued material as a separate step
  here, so its first real exercise is not the rate-limited drill in 5.2 (R7).
  *depends-on: 2.2, 2.3, 3.1*
- **Issue 3.3** — `postgresql.conf`: `postgres_ssl: true`, absolute `postgres_ssl_cert_file` /
  `postgres_ssl_key_file`, and the pre-flip existence assertion in `config.yml`.

  > **The pre-flip assertion is gated on `postgres_ssl | bool`, NOT on `postgres_apply_service`.**
  > This carve-out is load-bearing. `config.yml`'s template task is **not** apply-gated (verified —
  > `tasks/config.yml:36-51`), so a default read-only reconcile *does* write `postgresql.conf`,
  > while the `restart postgresql` handler **is** gated (`handlers/main.yml:16`) and does not fire.
  > Apply-gating the assertion would therefore let a converge on a pre-issuance host — a fresh
  > guest, or R9's dataset-restore path — write `ssl = on` pointing at files that do not exist, pass
  > silently, and kill the cluster at the **next** restart, whenever that happens to be. That is
  > exactly the failure D1's assertion exists to prevent, disabled on the branch where it matters.
  > Gating on `postgres_ssl` instead means it fires wherever `ssl = on` would be written, including
  > under `--check`. **A `--check` failure on a pre-issuance host is the assert working**, not a
  > PVE-ANS-007 violation: `SPEC.md:510-513` models imperative work precisely as read-only asserts
  > under `--check`.

  Correct the
  template's stale header comment (lines 8–10), which still explains why `ssl = on` is *avoided*.
  **Two more stale in-repo rationales must go in the same pass**, or the role will contradict
  itself: `roles/postgres/defaults/main.yml:69-74` repeats the "`ssl = off` … LAN-internal traffic …
  snakeoil hazard" reasoning, and `roles/postgres/handlers/main.yml:2-4` asserts that *every*
  setting the role writes is `postmaster`-context (RESTART-only) — which the new `sighup`-context
  `ssl_*_file` settings falsify. That second one is not cosmetic: it is the comment D3's
  reload-only renewal depends on being wrong about.
  Note the notify semantics: `ssl` itself is `postmaster`-context so the **first** flip restarts the
  cluster once; `ssl_*_file` are `sighup`-context, which is what makes D3's reload-only renewal
  work. *depends-on: 3.2*
- **Issue 3.4** — Renewal, authored (D3). Ship the **`certbot.service` drop-in** — opening with a
  bare `ExecStart=` reset, then `ExecStart=/usr/local/bin/postgres-certbot renew` and
  `EnvironmentFile=`. **Also enable and start `certbot.timer` explicitly**
  (`systemd_service: name=certbot.timer, enabled=true, state=started`): the drop-in fixes *what*
  runs, the timer is *what fires it*, and inheriting the package's default leaves the trigger
  unowned. **Notify the role's existing `reload systemd` handler** (`handlers/main.yml:7-10`) — a
  templated drop-in without a `daemon-reload` means SC12 tests the *stale stock unit* and passes or
  fails for the wrong reason. Write `EnvironmentFile=` with **no `-` prefix**, so an absent
  credential file fails the unit loudly instead of proceeding into an opaque DNS-01 failure. Prove **both** halves — that it is invocable (**SC12**) and that it is **scheduled**
  (**SC14**). Also ship `postgres-cert-check.sh` + `.service` + `.timer` emitting
  `postgres_cert_days_remaining=<n>` to journald at `err` below 21 days (feeds **SC10**).
  *depends-on: 3.2*
- **Issue 3.5** — First apply and hand verification: `pg_stat_ssl` shows `t` (**SC3**), and
  `psql "postgresql://…@postgres.dixson3.net:5432/…?sslmode=verify-full&sslrootcert=system"`
  succeeds from the LAN with **no private CA file** (**SC2**). *depends-on: 3.3, 3.4*

  > **The `sudo -u postgres test -r <privkey>` readability probe belongs in `tls.yml`, not here.**
  > R1 cites it as the mitigation for the **rebuild/adopt** path — which is a converge, not a hand
  > session, so a one-time check in this issue would never run on the branch it protects. Place it
  > as an apply-path task after normalisation and before `config.yml` flips `ssl = on` (Issue 3.1),
  > so every converge exercises it. This issue *observes* it passing; it does not own it.
- **Issue 3.6** — Add the cert-expiry panel to the existing PostgreSQL dashboard under
  `roles/openobserve/files/dashboards/` (upsert-by-title; no new dashboard). **Name the data
  source explicitly**: `postgres_cert_days_remaining=<n>` is a journald **log line**, not a metric,
  so this is a log-stream panel over CT 107's journald stream with a field extraction — not a query
  against a numeric series that does not exist. Completes **SC10**. Requires a converge against
  **CT 104**.
  *depends-on: 3.4*

### Epic 4 — consumer cutover

- **Issue 4.0** — **Run EXP-006** (see Investigation findings): determine whether Prisma's connector
  honours `sslmode=verify-full`, silently downgrades, or fails closed. Record the finding in
  `findings/exp-006-prisma-sslmode.md`. Its outcome decides the *shape* of 4.1 — proceed as written,
  switch to `sslaccept=strict`, or explicitly scope-cut consumer-side `verify-full`. **This is a
  blocking experiment, not a verification step**: it can change what 4.1 does. Run it against a
  **throwaway invocation inside CT 106**, never by reconfiguring the serving unit — see the method
  note in EXP-006. *depends-on: 3.5*
- **Issue 4.1** — CT 106, a **two-file** change: `litellm_db_host` → `postgres.dixson3.net`, **plus**
  a new `litellm_db_params` default and a `{{ litellm_db_params }}` query-string slot in
  `litellm.env.j2:16`. **The `?` belongs inside the variable, not the template**, and the default is
  `""` — so an empty value renders byte-identically to today's URL and Rollback step 1 is a clean
  revert rather than leaving a trailing `?`. The parameters are whatever 4.0 determined (with `sslrootcert=system` on any
  libpq path). **Do not fold parameters into `litellm_db_host`** — it is reused verbatim as
  `pg_isready -h` in `litellm-migrate.service.j2:41`, so a URL fragment there breaks the readiness
  probe and, through the migrate unit's `Requires=` chain, the serving unit with it. Verify the
  gateway returns to `/health/readiness` → `.db == "connected"` before proceeding. This is the only
  step that can take a live service down (R4). *depends-on: 4.0*
- **Issue 4.2** — `ansible/README.md:318`: update the consumer-onboarding recipe to the name plus
  whatever 4.0 established, so the documented path is the one that is actually verified. Note this
  is the recipe that seeds the 1Password `host` field — Issue 2.4 updates the existing items.
  *depends-on: 4.1*
- **Issue 4.3** — Confirm the two **non**-cutover consumers are genuinely unaffected: the backup
  timer completes over the local socket, and the `otel_agent` postgresql receiver still reports on
  loopback (**SC11**). **State the method**: `systemctl start postgres-dump.service` and assert it
  exits 0 (the unit read-backs the uploaded archive, so a zero exit means verified, not merely
  uploaded), and query the receiver's stream in OpenObserve for a post-flip datapoint. EXP-005
  predicts both outcomes; assert rather than assume. Note this also pre-warms the rebuild gate,
  whose test asserts on this same unit's exit status. *depends-on: 3.5*

### Epic 5 — proofs & drills

- **Issue 5.1** — Regression: the three `CANARY.md` negatives still fail at `pg_hba` (**SC4**) and
  `plan011_canary` still returns 3 rows (**SC5**). TLS must not have quietly altered access control.
  *depends-on: 4.1*
- **Issue 5.2** — Forced-renewal drill (**SC6**): `postgres-certbot renew --force-renewal` — through
  the wrapper, or it reads the empty default directory and renews nothing while looking healthy.
  Assert a **new certificate serial**, that the deploy hook fired, and that the **postmaster PID is
  unchanged**. The PID is the criterion — it is what distinguishes a reload from a restart, and a
  restart would drop CT 106's live gateway. *depends-on: 3.5*
- **Issue 5.3** — **Adopt-branch rebuild drill (SC8)** — the criterion that actually tests D1 **and
  D2**. Destroy and recreate CT 107 through the `pve_lxc` path, re-converge, and assert: TLS works;
  renewal state survived (`postgres-certbot certificates` lists the cert with its renewal config
  intact and **no re-issuance occurred**); the key is still readable as `postgres` after the
  rootfs was rebuilt; and the AWS EnvironmentFile survived on the bind (D4). *depends-on: 5.1, 5.2 ·
  Gate: rebuild drill authorized*
- **Issue 5.4** — **Negative verification test (SC13)** — the only proof that TLS is *authenticated*
  rather than merely encrypted. Point a `verify-full` client at a name/certificate mismatch (or at
  the bare IP, which no public CA will SAN) and assert it **fails closed**. Without this, every
  positive criterion in the plan is equally satisfied by `sslmode=require`, and the MITM half of the
  Motivation would go unproven. Scope per 4.0's outcome: if the gateway cannot verify, run this
  against the `psql` path and record the gateway's posture explicitly. *depends-on: 4.1*
- **Issue 5.5** — Re-converge reports **`changed=0`** (**SC7**). Watch specifically for the issuance
  task or the ownership normalisation reporting `changed` on every run — a permanently-changed task
  is the usual outcome of shelling out, and would mask real drift. D2's move of the normalisation
  into an Ansible `file:` task is what makes this achievable rather than aspirational.
  *depends-on: 5.3, 5.4*

### Epic 6 — reconcile

- **Issue 6.1** — File the follow-up to narrow **`caddy-acme-dixson3`** the same way (EXP-003).
  Out of scope here, but shipping a better pattern beside an unimproved one without recording it is
  what turns an improvement into an inconsistency.
- **Issue 6.2** — File the follow-up for **tailnet subnet routing** (S6 / EXP-004), which is what
  would let `verify-full` be demonstrated over the tailnet — the half of S5 this plan cuts. Note in
  it that a subnet router deployed with SNAT **disabled** is the only condition under which the
  removed `100.64.0.0/10` `pg_hba` entry must come back.
- **Issue 6.3** — File the **`hostssl` follow-up**. S7 deliberately keeps `host`, so plaintext
  remains *permitted* — the actual completion of this plan's security goal is the `hostssl` switch,
  and it is blocked only on the `otel_agent` loopback receiver's `tls: insecure: true`. Recording it
  is what keeps "TLS available and used" from being mistaken later for "plaintext impossible".
- **Issue 6.4** — **Conditional on EXP-006 outcome (c) only.** File the follow-up to split
  `VERIFY_DATABASE_URL` out of `DATABASE_URL` in the `litellm` role, without which the verify script
  and the gateway cannot hold different TLS postures (one variable, two consumers). If 4.0 lands on
  (a) or (b), close this as not-applicable rather than leaving it open as a phantom.
- **Issue 6.5** — Close the Issue 1.1 tracking issue; update the incubator README; commit.
  *depends-on: 3.6, 4.2, 4.3, 5.5, 6.1, 6.2, 6.3, 6.4*

## Risks & Mitigations

| ID  | Risk                                                                                                                                                                                                                                                                                                                                                                                                                                           | Severity | Mitigation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :-- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | **A bad cert/key permission stops the cluster from starting.** PostgreSQL refuses to start if the key is group- or world-readable — a shared database guest going down takes three consumers with it.                                                                                                                                                                                                                                          | **high** | **D2.** `postgres:postgres 0600` with no dependency on a rootfs-allocated gid; normalisation is an idempotent Ansible task (so the **adopt** branch re-asserts it, where a hook-only design would not); **Issue 3.1** probes `sudo -u postgres test -r <privkey>` as an apply-path task **before** `config.yml` flips `ssl = on` — deliberately not 3.5, which is a hand session that would never re-run on the adopt branch this mitigation is for. **Not** `--check` — issuance and the hook are `command:`-shaped and skipped under check, so a check run cannot exercise this failure. Rollback stays a one-variable `ssl = off` revert. |
| R2  | **Renewal fails silently** and the certificate expires 90 days later, breaking every `verify-full` client at once — long after anyone is watching.                                                                                                                                                                                                                                                                                             | **high** | **D3 / Issue 3.4 — and note the first draft's mitigation WAS this risk**: the packaged `certbot.timer` carries no `--config-dir`, so against D1's relocated state it renews nothing and exits 0. Corrected to an authored drop-in (dir flags + `EnvironmentFile`) proven by **SC12** (renewal, through the real unit, names this certificate), plus the outcome-watching daily check (**SC10**) as a 21-day backstop.                                                                                                                                                                                                                        |
| R3  | **Tailnet cannot resolve or route to the name**, leaving S5 half-satisfied and the plan's headline claim untrue over the path that motivated it.                                                                                                                                                                                                                                                                                               | —        | **RETIRED.** EXP-004 settled it before implementation: no subnet route exists, so S6 scope-cut tailnet verification and Issue 6.2 tracks it. Kept for the record — the risk was real and the investigation is what discharged it.                                                                                                                                                                                                                                                                                                                                                                                                            |
| R4  | **Consumer cutover breaks a live service.** Moving `DATABASE_URL` from IP to name touches CT 106's running gateway and the backup timer.                                                                                                                                                                                                                                                                                                       | medium   | EXP-005; cut over one consumer at a time with a verification between, and keep IP-based `pg_hba` entries in place so a partial cutover is not fatal.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| R5  | **A second IAM key is another credential to rotate**, and an unrotated ACME key is a quiet liability.                                                                                                                                                                                                                                                                                                                                          | low      | Scope it as narrowly as EXP-003 allows; record it in the same 1Password convention so it is discoverable rather than forgotten.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| R6  | **The rebuild drill (5.3) destroys a shared production guest.** CT 107 now has a live consumer (CT 106) and `pool1/postgres` is precious, with only a *logical* backup on the same mirror.                                                                                                                                                                                                                                                     | **high** | Gated (rebuild drill authorized) and sequenced **last**, after every non-destructive proof. A fresh Garage dump is a precondition. The drill is not optional — it is the only thing that tests D1 — but it is the last thing run.                                                                                                                                                                                                                                                                                                                                                                                                            |
| R7  | **Let's Encrypt rate limits.** Five duplicate certificates per name per week. The forced-renewal drill (5.2) spends one; a botched retry loop could exhaust the rest.                                                                                                                                                                                                                                                                          | low      | Iterate with `--dry-run` (ACME staging, no live state touched); budget **at most 3** production issuances. Note the rebuild drill (5.3) spends **none** — SC8 asserts *no re-issuance occurred*, so a rebuild that burns a certificate is a **failed** criterion, not an expected cost. Note `--dry-run` **does not run deploy hooks**, so it does not cover D2 — Issue 3.2 runs the hook script directly against staging material instead. Exhaustion is a week-long delay, not data loss.                                                                                                                                                  |
| R8  | **The deploy hook or ownership normalisation reports `changed` on every converge**, masking real drift behind permanent noise — the usual fate of a shell-hook task.                                                                                                                                                                                                                                                                           | low      | SC7 (`changed=0`); Issue 5.5 names it explicitly rather than reading a green run as success. **D2's structural fix does the real work** — moving normalisation into an Ansible `file:` task removes the shell hook that would have reported `changed` forever.                                                                                                                                                                                                                                                                                                                                                                               |
| R9  | **The Garage dump captures none of `acme/`.** D1 makes certificate + renewal state — **and now the Route53 IAM secret (D4)** — survive a *guest rebuild*, but **not a dataset loss** — a restore-from-backup yields a cluster with `ssl = on` and no key material, which will not start. Symmetrically, when [#51](https://github.com/dixson3/d3-pxe/issues/51)'s off-host tier lands, **private key material silently joins the backup set**. | medium   | Record both consequences in PVE-PKG-103 and as a note on `MOUNTS.md`'s `pool1/postgres` row (which today describes the dataset purely as PGDATA). Add re-issuance to the Rollback/recovery path. This is a documentation control, not a technical one — the point is that neither consequence is discovered later.                                                                                                                                                                                                                                                                                                                           |
| R10 | **EXP-006 could invalidate the plan's headline claim.** If Prisma cannot do `verify-full`, "clients can use `sslmode=verify-full`" is true only of the `psql` path, not of the gateway that motivated the work.                                                                                                                                                                                                                                | medium   | Issue 4.0 settles it **before** 4.1 commits to a connection-string shape, and **SC13**'s negative test makes the answer observable either way. All three outcomes are acceptable; shipping the bad one while claiming the good one is not.                                                                                                                                                                                                                                                                                                                                                                                                   |

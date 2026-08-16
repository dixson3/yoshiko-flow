---
deliverable_class: standard
source_plan: plan-008-james-dixson-7f4482
source_repo: d3-pxe
---
# Plan: Provision a dedicated OpenObserve claude-code OTLP ingest credential and a Claude-Code-metrics dashboard as infra-as-code

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|

_No open upstream issue targets this work. `#31 plan-006 execution tracking` is
closed (the stack build this extends). `#29 Add LiteLLM AI Gateway` is
observability-adjacent but out of scope. A fresh coarse tracking issue is filed
at intake per the repo's one-issue-per-plan convention: **[#45](https://github.com/dixson3/d3-pxe/issues/45)
— plan-008 execution tracking** (filed 2026-07-26); reconcile it at plan
completion._

## Epics

### Epic 1: Dedicated claude-code ingest service account (IaC)
- Issue 1.1: Add `roles/openobserve/tasks/claude_ingest_sa.yml` — probe `ZO_SERVICE_ACCOUNT_ENABLED`, `GET /service_accounts` existence check, `POST /service_accounts` create-if-absent capturing the one-time `token` (root Basic auth, loopback; retention.yml `uri` shape; `no_log`; **never** `PUT ?rotateToken=true` on re-converge)
- Issue 1.2: Push `base64(email:token)` to 1Password `op://Y-Home/openobserve-claude-code-ingest` (check-then-create; garage provision.yml pattern; read-only probe + writer create). **Recovery guard:** if the SA already exists but the 1Password item is absent (guards diverged), **fail loudly** with the manual-recovery runbook (see Risks) rather than silently no-op'ing into an unrecoverable state
  - depends-on: 1.1
- Issue 1.3: Wire the SA task into `tasks/main.yml` gated on **both** `openobserve_apply_service` **and** `openobserve_root_password | length > 0` (mirroring the `retention.yml` import guard — not the apply flag alone); document the apply invocation + the `~/.secrets.zsh` handoff in `ansible/README.md`, and reconcile the README's plan-006-era "no converge this iteration" top-of-file caveat (this plan requires converge, behind the apply gate)
  - depends-on: 1.1

### Epic 2: Confirm metrics feeding (capability gate)
- Issue 2.1: Operator adds `CLAUDE_OTEL_OO_AUTH_B64` (the base64 from 1Password) to `~/.secrets.zsh`, opens a new on-LAN Claude session
  - depends-on: 1.2
- Issue 2.2: Verify the **always-on** Claude streams (`claude_code_session_count`, `claude_code_token_usage`) exist and receive data in org `default` (event-driven streams like `claude_code_commit_count`/`claude_code_pull_request_count` are expected-absent until those events occur — not a failure); record the 2 live-only facts (counter temporality; exact attribute field names — `host_name`/`session_id`/`model`)
  - depends-on: 2.1

### Epic 3: Claude-Code-metrics dashboard (IaC)
- Issue 3.1: Author `roles/openobserve/files/dashboards/claude-code.json` (schema `version: 5`, SQL panels) against the confirmed stream/field names + the temporality decision from 2.2
  - depends-on: 2.2
- Issue 3.2: Add **upsert-safe** `tasks/dashboards.yml` (GET-list-by-title → POST-or-`PUT ?hash=`) + wire into `main.yml` gated on **both** `openobserve_apply_service` **and** `openobserve_root_password | length > 0` (same guard as Issue 1.3 / `retention.yml` — the task makes root-Basic-auth API calls)
  - depends-on: 3.1
- Issue 3.3: Apply, verify the dashboard renders with live data broken down by `host_name`; mirror the new role surface (SA task, dashboards task/JSON) into SPEC.md + the incubator README
  - depends-on: 3.2

## Risks & Mitigations

- **Reachability chicken-and-egg** — the client endpoint DNS is RFC1918
  (LAN/tailnet-only), so metrics only feed when the operator is on-network.
  *Mitigation:* Epic 2 is an explicit human capability gate; the plan does not
  assume metrics before it is satisfied.
- **v0.91.3 API gaps** — the pinned OpenObserve release may lack a clean
  ingest-scoped credential or a documented dashboard import API. *Mitigation:*
  EXP-1/EXP-2 resolve this first; fallbacks noted (scoped user; SQL panels).
- **Dotted metric-name stream mapping** — panel queries fail if the stream
  naming assumption is wrong. *Mitigation:* Epic 2 records the *actual* stream
  and field names before any dashboard JSON is authored (Epic 3 depends on 2.2).
- **Credential re-mint / drift** — re-running the play must not rotate the
  credential or duplicate the 1Password item. *Mitigation:* GET-then-write
  idempotency (retention.yml) + check-then-create 1Password pattern
  (garage provision.yml); `no_log` throughout.
- **SA-token-lost / diverged idempotency guards** — the SA token is returned by
  OpenObserve **once** at create, and rotate-on-reconverge is forbidden; unlike
  garage's `key info --show-secret` there is no way to re-read it. The two guards
  (SA-exists in OpenObserve; item-exists in 1Password) are independent, so a
  create that succeeds in OpenObserve but fails the 1Password push (or a later
  item deletion) leaves the SA present but the credential unrecoverable by
  re-converge. *Mitigation:* Issue 1.2 **fails loudly** on SA-present-but-item-
  absent with this manual-recovery runbook — the **single sanctioned exception to
  never-rotate**: (1) `PUT /api/default/service_accounts/claude-code@svc.d3-pxe?rotateToken=true`
  once to mint a fresh token; (2) re-store `base64(email:newtoken)` in the
  1Password item; (3) re-paste into `~/.secrets.zsh`. Never automate the rotate.

## Success Criteria

- A dedicated `claude-code` OpenObserve ingest credential exists, minted by
  idempotent ansible (re-converge = `changed=0`), and stored in 1Password
  `Y-Home`; it is **not** the fleet `otel_agent` credential.
- With the credential in `~/.secrets.zsh`, an on-LAN Claude Code session's
  metrics arrive in OpenObserve org `default` and are queryable.
- A committed Claude-Code dashboard JSON is POSTed by an idempotent, apply-gated
  ansible task and renders in the OpenObserve UI with live Claude data, broken
  down by `host.name`.
- The new role surface (credential task, dashboard task/JSON) is mirrored in the
  repo's design/spec docs; a coarse upstream tracking issue is filed (its number
  recorded in the Upstream Issues table) and reconciled.

**Cross-repo handoff (out of this plan's write scope):** when the credential
lands and the operator adds it to `~/.secrets.zsh`, update the `dixson3/rc-files`
`zshenv` comment from `base64(email:password)` to `base64(email:token)` to match
the service-account mechanism (the fallback-user model's wording is the road not
taken). Functionally identical; a comment-only fix in the other repo.

---
deliverable_class: standard
source_plan: plan-013-james-dixson-1692d0
source_repo: d3-pxe
---
# Plan: Ansible hygiene hardening (E–I), then re-audit to re-assert A–D priority

## Upstream Issues

| Issue                                              | Title                                                                                                       | Disposition | Notes                                                                                                                                                                    | Resolved By |
| :------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- | :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- |
| [#56](https://github.com/dixson3/d3-pxe/issues/56) | `ansible_ledger_check.py` bind vocabulary hardcoded to two keys, fails OPEN on a third                      | include     | Issue 1.2 implements the issue's own proposed fix (data-driven vocabulary + fail-closed on unknown `*_bind`/`*_rbind`)                                                   | 1.2         |
| [#55](https://github.com/dixson3/d3-pxe/issues/55) | MOUNTS.md ↔ `pve_storage/defaults` dataset properties have no drift check                                   | include     | Issue 1.3 takes the issue's *larger* option (hard gate in the ledger check) rather than the cheap `DRIFT-CHECK.md` edge — see Approach §Decision D1                      | 1.3         |
| [#57](https://github.com/dixson3/d3-pxe/issues/57) | `otel_agent` tarball `get_url` reports changed on every run, making fleet-wide zero-delta proofs unreadable | include     | Epic 5. Not hygiene for its own sake: this noise is the direct tax item A will pay on every fleet-wide proof. Cheap to fix now, expensive to keep working around         | 5.1a + 5.1b |
| [#47](https://github.com/dixson3/d3-pxe/issues/47) | SPEC: require OTEL telemetry from new guests + prefer OTEL-native software                                  | partial     | Issue 3.3's scaffold emits guest-level OTEL enrolment by default, which is the *practical* half. The normative SPEC requirement is **not** authored here — it stays open | 3.3         |
| [#53](https://github.com/dixson3/d3-pxe/issues/53) | `otel_agent` on plex (CT 100) never started — missing EnvironmentFile                                       | exclude     | This is item B (fail-closed enrolment), an A–D behaviour change. Epic 6 re-asserts its priority with evidence                                                            | —           |
| [#54](https://github.com/dixson3/d3-pxe/issues/54) | `otel_agent` on calibreweb (CT 101) never started                                                           | exclude     | Same as #53 — same root cause, same item B                                                                                                                               | —           |
| [#33](https://github.com/dixson3/d3-pxe/issues/33) | Epic: provision self-hosted *arr media stack                                                                | exclude     | The driver for this plan's timing, not something it resolves                                                                                                             | —           |

## Epics

### Epic 1: Make the ledger gate fail closed (item E)

- **Issue 1.1:** Add ledger → inventory direction. Every non-retired `RESERVATIONS.md` row whose
  Status is `active` MUST have an `inventory/hosts.yml` entry, a `host_vars/<guest>.yml`, and a
  `guests.yml` play. Today guests are globbed from `host_vars/*.yml`, so a ledger row with no
  Ansible presence passes silently.

  **The Status rule is directional, deliberately.** `active` ⟹ full Ansible presence required; a
  `planned` row **may** be pre-staged in inventory and that is not an error. The tempting stronger
  rule — Status must agree with `lxc_guests` membership — is wrong, because membership is not
  evidence of deployment: a guest can be legitimately pre-staged before its CT exists (Issue 3.4
  does exactly this). `garage-webui` reading `planned` while deployed is therefore fixed as a
  **one-time reconciliation in 5.3**, not derived from a signal the inventory does not carry.

  **The play exemption is a declared key, not a checker-side list.** A guest with no in-CT role is
  a legitimate, anticipated case (`ansible/README.md`'s "Adding a new guest" step 4: an app role is
  needed "only if it needs one"). Such a guest MUST declare `in_ct_role: none` in its own
  `host_vars`, so the waiver sits beside the identifiers it qualifies. An **undeclared** missing
  play is a hard failure — otherwise this check reintroduces the very fail-open shape #56 is about.

  **The play exemption is a declared key, not a checker-side list.** A guest with no in-CT role is
  a legitimate, anticipated case (`ansible/README.md`'s "Adding a new guest" step 4: an app role is
  needed "only if it needs one"). Such a guest MUST declare `in_ct_role: none` in its own
  `host_vars`, so the waiver sits beside the identifiers it qualifies. An **undeclared** missing
  play is a hard failure — otherwise this check reintroduces the very fail-open shape #56 is about.
- **Issue 1.2:** Data-driven, fail-closed bind vocabulary. Derive recognised bind keys from one
  list; **fail** on any `*_bind`/`*_rbind` key in `host_vars` that the checker does not know,
  demanding either a MOUNTS row or an explicit allow-list entry. Implements #56's proposed fix
  verbatim.
  - depends-on: 1.1
  - resolves-upstream: [#56](https://github.com/dixson3/d3-pxe/issues/56) (include)
- **Issue 1.3:** Dataset property reconciliation. Compare every non-retired `MOUNTS.md` **Datasets**
  row against `pve_storage/defaults/main.yml` `pool1_datasets` on mountpoint, owner/group, mode and
  ZFS properties. Parse `(default recordsize)` as "recordsize unset"; honour an explicit
  `**RETIRED**` marker (the `pool1/calibre-library` row); fail closed on any row shape the parser
  does not recognise, rather than skipping it.
  - depends-on: 1.1
  - resolves-upstream: [#55](https://github.com/dixson3/d3-pxe/issues/55) (include)
- **Issue 1.4:** Baseline sweep — run all three new checks against the **unmodified** tree,
  enumerate every finding, and fix or explicitly waive each. **A waiver is a committed allow-list
  entry**, not a commit message: `scripts/ledger_check_waivers.yml`, consumed by the checker, each
  entry requiring a target, a reason and a date. A waiver then shows up in a diff and can be argued
  with; an unwaived finding stays a hard failure. The three
  checks have never been run here; 1.3's property comparison in particular may surface a real,
  unknown MOUNTS.md ↔ `pve_storage/defaults` mismatch. Discovering it *after* 5.4 has wired the
  row into CHANGE-VALIDATION would red-light an unmodified checkout — the precise anti-pattern
  CHANGE-VALIDATION.md §1 warns trains operators to ignore the gate.
  - depends-on: 1.2, 1.3
- **Issue 1.5:** Prove the new checks actually catch. For each of 1.1/1.2/1.3, introduce a
  deliberate drift in a scratch copy, confirm non-zero exit and a useful message, revert. A gate
  that has never been seen to fail is not known to work.
  - depends-on: 1.4

### Epic 2: One verifiable secret manifest (item F)

- **Issue 2.1:** Author `ansible/secrets.env.tmpl` — all 30 env vars as `op://Y-Home/<item>/<field>`
  rows, using the field names EXP-002 verified. Annotate `LITELLM_SALT_KEY` with its PVE-PKG-092
  immutability warning; give `CADDY_AWS_REGION` / `LITELLM_AWS_REGION` / `POSTGRES_ACME_AWS_REGION`
  plain non-secret defaults; separate the writer-token section (`bootstrap-pve-token.yml`) from the
  read-only bulk so a routine apply never requests write authority.
- **Issue 2.2:** `scripts/check_secrets_manifest.py` — static, vault-free, bidirectional: every
  `lookup('env', 'X')` in `ansible/` has a manifest row and vice-versa. Plus an opt-in `--resolve`
  mode that checks each ref resolves non-empty. **`--resolve` is never a CHANGE-VALIDATION row** —
  it needs a live vault and occasional biometric approval, and the recipe forbids rows touching
  anything outside the working tree.
  - depends-on: 2.1
- **Issue 2.3:** Collapse the **setup** copies in `ansible/README.md` to one pointer at the
  manifest, and remove or create the dangling `.pve-token.env.tmpl` reference (README:88).

  **Exempt the restore runbook.** README's "Restoring PostgreSQL from a Garage dump" section is
  drill-verified (plan-011 Issue 4.5) and its inline `export` lines are part of an emergency
  procedure followed under pressure. Replacing those with a pointer would degrade a working runbook
  to save duplication. They stay, with a note that the values are the same ones the manifest
  sources.
  - depends-on: 2.1

### Epic 3: New-guest scaffold (item G)

- **Issue 3.1:** `scripts/new_guest.py` core — given name, CTID and intent flags, emit the
  `RESERVATIONS.md` row (next free CTID + MAC index, honouring the `index = ctid - 99` convention),
  `inventory/host_vars/<guest>.yml` (including the `in_ct_role` key Issue 1.1 introduces), the
  `hosts.yml` entry, and the `guests.yml` play. Emitting and *committing* are separate: the tool
  writes all four, and the operator lands the inventory half only once the CT exists (see 3.4).
- **Issue 3.2:** Derived idmap with tiling validation. Generate the `lxc.idmap` lines from a
  declared list of consumed SPEC §6.1 ids rather than hand arithmetic, and assert the result tiles
  0–65535 with no gap or overlap. This is the single most error-prone hand-written artifact per
  guest (`host_vars/postgres.yml` carries the arithmetic in a comment: "Tail = 65536 - 10007 =
  55529"), and today's ledger check only verifies the 1:1 line *exists* — a wrong tail passes.
  - depends-on: 3.1
- **Issue 3.3:** Role skeleton generation — `roles/<guest>/` with `user`/`install`/`config`/`service`
  task files, `defaults/main.yml` wired to the Epic 4 apply gate, and `handlers/main.yml`, matching
  the shape all six app roles already share.

  **On #47, narrowly.** Guest-level OTEL enrolment is already free — per AGENTS.md, `lxc_guests`
  membership auto-enrols the horizontal `otel_agent` — so a scaffold that "emits guest-level
  enrolment" would be claiming credit for nothing. What it emits instead is an **app-level receiver
  stub plus a required `host_vars` decision field**, so every generated guest must either declare
  its application-level metrics surface or record why it has none. That is exactly what AGENTS.md's
  "Observability for new services" asks for in prose, made mechanical. The normative SPEC
  requirement and the "prefer OTEL-native software" half of #47 are **not** authored here.
  - depends-on: 3.1
  - resolves-upstream: [#47](https://github.com/dixson3/d3-pxe/issues/47) (partial — app-level
    decision field only; normative SPEC requirement stays open)
- **Issue 3.4:** Round-trip proof against a **real** target. Generate the full artifact set for
  Prowlarr ([#34](https://github.com/dixson3/d3-pxe/issues/34)) — the simplest *arr guest: indexer
  hub, one config bind, no GPU, no media rbind. **Land the RESERVATIONS row (CTID 108, MAC index
  09, Status `planned`) and `host_vars/prowlarr.yml` only.** Confirm the Epic 1 ledger check, the
  Epic 2 secrets check and the Epic 5 manifest check all pass, and that `ansible-playbook site.yml
  --syntax-check` stays green.

  **The `hosts.yml` entry and `guests.yml` play are generated but deliberately NOT committed.**
  `guests.yml`'s trailing play targets `hosts: lxc_guests` wholesale, so adding a guest whose CT
  does not exist would enrol a phantom host in the fleet-wide `otel_agent` play and break every
  real converge on an unreachable host — and `--syntax-check` would never catch it, because it
  does not connect. Their *emitted text* is verified instead (SC5), which exercises the generator
  without arming the trap.

  A throwaway-and-revert round-trip would leave the generator unvalidated against a real target —
  framework-without-a-user. Landing one real guest's ledger row and idmap exercises its two hardest
  outputs end-to-end and gives the *arr plan a head start. Operator-confirmed 2026-08-12; the cost
  is claiming CTID 108 ahead of the plan that will own it, which Status `planned` makes explicit.
  This does **not** resolve [#34](https://github.com/dixson3/d3-pxe/issues/34) — a `host_vars` file
  is not a deployed indexer — so #34 stays untriaged and absent from the Upstream Issues table.
  - depends-on: 1.5, 2.2, 3.2, 3.3, 5.2

### Epic 4: Single apply switch (item H)

- **Issue 4.1:** Default every `<role>_apply_service` to `"{{ apply_services | default(false) }}"`
  across all 7 roles that define one, plus `pve_lxc_apply_lifecycle`. Backward compatible: an
  undefined `apply_services` yields today's `false`, and an explicit `-e postgres_apply_service=true`
  still wins as an extra-var.

  **State the fleet consequence.** `-e apply_services=true` flips `otel_agent_apply_service` on
  every target at once, which on `guests.yml` would start `otel_agent` on all eight guests in a
  single run. That is plausibly desirable — it is arguably what fixes #53/#54 — but an operator
  reading "single apply switch" would not predict it, so it goes in the README next to the switch.
  PVE-OBS-001 is unaffected on the host side because `host.yml`'s otel play is `never`-tagged.
- **Issue 4.2:** Prove no behaviour change **locally, without the fleet**. Render each affected
  role's templates and resolved defaults with `apply_services` unset and diff against today's
  output; then confirm `-e apply_services=true` flips every gate. Also assert `host.yml`'s otel
  play still carries the `never` tag, so PVE-OBS-001's host gate survives the change. Document the
  switch and its fleet consequence in `ansible/README.md`.

  A local render comparison is used deliberately in place of a live `--check --diff`: the latter
  needs SSH to the host and all eight guests **and** the full secret environment — because
  `roles/otel_agent/tasks/config.yml`'s postgres-password assert is unconditional on the apply flag
  and fails the run outright when the var is unset. It proves nothing extra about a variable-default
  change, and it would silently make this plan fleet-dependent.
  - depends-on: 4.1

### Epic 5: Manifest-drift check + the drift it finds (item I) and #57

- **Issue 5.1a:** Author the [#57](https://github.com/dixson3/d3-pxe/issues/57) fix — guard the
  `otel_agent` download on the *installed binary version* rather than a `/tmp` tarball (the
  issue's option 2, "closer to the role's intent") — and produce the evidence the PVE-OBS-001
  gate is judged on: `host.yml --check --diff --tags otel_agent`, `guests.yml --check --diff
  --limit lxc_guests --tags otel_agent`, and a **before/after changed-count differential**
  (change stashed vs applied). #57's own `/tmp` noise makes raw counts nonzero either way, so a
  naive zero-delta read looks like failure; the differential is the readable proof. Written to
  `findings/`.

  **Deliberately UNGATED.** Authoring and `--check --diff` are read-only and mutate nothing.
  PVE-OBS-001 governs the *apply* (5.1b). Gating this step made the gate's own precondition
  unreachable — the preview could never be produced, so the gate could never be satisfied. That
  deadlock was found mid-execution on 2026-08-12 after three review passes missed it, and is
  filed upstream as yoshiko-flow#112/#113.

  Requires SSH to the host and all 8 guests **and** the full secret environment
  (`roles/otel_agent/tasks/config.yml` asserts on `POSTGRES_OTEL_PASSWORD` unconditionally when
  the receiver is enabled, so a credential-less `--check` fails outright — source it with
  `op run --env-file=ansible/secrets.env.tmpl`). If that environment cannot be obtained, STOP
  and report rather than fabricating the proof.
- **Issue 5.1b:** Apply the 5.1a change to the host and all 8 guests. This is the step
  PVE-OBS-001 actually governs. The operator resolves the gate after reading 5.1a's
  differential; an executing agent must never resolve it.
  - depends-on: 5.1a
  - gated-on: Capability Gate PVE-OBS-001
  - resolves-upstream: [#57](https://github.com/dixson3/d3-pxe/issues/57) (include)
- **Issue 5.2:** `scripts/manifest_check.py` — assert roles-on-disk == SPEC §10 table ==
  `ansible/README.md` layout block == `requirements.yml` collections, and that every task file
  referenced in README's traceability table exists.
- **Issue 5.3:** Fix the drift 5.2 finds: SPEC §10 tree (5 roles → 14) and its table (6 missing
  rows); README layout (`storage.yml`, `litellm`, `pve_token`, `community.postgresql`) and the
  traceability row pointing at the deleted `pve_host/zfs.yml`; `pve_lxc/defaults/main.yml`'s
  nonexistent `binds:` contract — rewritten to the real `config_bind`/`media_rbind` shape **and to
  document the new `in_ct_role` key** (Issue 1.1), so it lands documented rather than discovered;
  `RESERVATIONS.md` `garage-webui` `planned` → `active`, the one-time reconciliation Issue 1.1's
  directional rule deliberately does not try to automate.
  - depends-on: 5.2
- **Issue 5.4:** Add the `ledger`, `secrets` and `manifest` rows to `CHANGE-VALIDATION.md` FAST.
  Re-fingerprint §2 and re-verify every row green on a clean tree. **Deliberately independent of
  5.5** — R2 offers item J as droppable, so the issue wiring this plan's *main* deliverable into the
  gate must not be stranded by dropping it.
  - depends-on: 1.5, 2.2, 5.3
- **Issue 5.5:** Item J — add `.ansible-lint` (`profile: min`, `ANSIBLE_COLLECTIONS_PATH` shim,
  `var-naming[no-role-prefix]` in `warn_list` with the EXP-001 rationale as a comment); **correct
  the stale "cannot run collection-aware" paragraph** in CHANGE-VALIDATION.md; file the remaining
  ~98 cosmetic items upstream as a tracked follow-up marked do-not-bulk-fix.

  **First enumerate the 4 `no-changed-when` hits, then fix or waive each.** EXP-001 counted them
  but did not locate them, and several `command:`/`shell:` tasks in this repo legitimately always
  report changed (the `pct exec` bootstrap tasks and the `pveum` calls in `pve_token` are exactly
  that shape). A blanket `changed_when: false` to satisfy the count would hide a real signal.
- **Issue 5.6:** Add the `ansible-lint` row to `CHANGE-VALIDATION.md` FULL and re-verify it green.
  Separated from 5.4 so that dropping item J drops exactly this issue and nothing else.
  - depends-on: 5.4, 5.5

### Epic 6: Re-audit and re-assert A–D priority

- **Issue 6.1:** Re-run the full `ansible/`-vs-SPEC structure audit against the hardened tree,
  using the new gates' actual output as evidence rather than reading by eye.
  - depends-on: 1.5, 2.3, 3.4, 4.2, 5.4
  - Note: the dependency set is the terminal issue of each of Epics 1–5. A re-audit that runs
    before the hardening lands would re-measure the tree this plan set out to change, and its
    A–D verdict would be worthless. Issues 5.1a/5.1b and 5.6 are deliberately **not**
    dependencies — 5.1b is gated on live-infrastructure authorisation that may not arrive, and
    5.6 is droppable with item J. Epic 6 must not be hostage to either (6.2 records A's cost
    with or without #57 landed).
- **Issue 6.2:** Write `Incubator/ansible/audit-2026-08-A-D-reassessment.md` — for each of A
  (`otel_agent` scrape generalization), B (fail-closed otel enrolment, #53/#54), C (derived
  `subuid`/`subgid`), D (derived+validated idmap): confirm, re-order, or retire, with the reason.
  Note explicitly where Epic 3.2 (derived idmap in the scaffold) already discharges part of D for
  *new* guests while leaving the seven existing ones unconverted, and where Epic 5.1a/5.1b (#57) has
  changed A's cost.

  Also record **what Epics 1–5 actually cost** — the first real datapoint for the hygiene-vs-#33
  sequencing claim this plan asserts but does not size (R10) — and a one-line **relaxation path**
  for any Epic 1 check that proves over-strict once the *arr stack starts landing.
  - depends-on: 6.1
- **Issue 6.3:** File or update the upstream issues for whatever A–D work survives
  re-prioritisation, sequenced against [#33](https://github.com/dixson3/d3-pxe/issues/33).
  - depends-on: 6.2

## Risks & Mitigations

| #   | Risk                                                                                                                 | Severity | Mitigation                                                                                                                                                                                                                                                                                                                                                                                                                             |
| :-- | :------------------------------------------------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | Epic 1's stricter checks red-light the **current** tree, blocking every landing until unrelated debt is cleared      | high     | Two dedicated issues, not just sequencing: **1.4** sweeps all three new checks against the unmodified tree and fixes-or-waives every finding, and **5.3** fixes the manifest drift — both strictly before 5.4 wires any row into CHANGE-VALIDATION. Build the checker, run it, fix what it finds, only then make it a gate. Any check that cannot be made green on a clean tree is dropped, not force-passed (CHANGE-VALIDATION.md §1) |
| R2  | `--profile min` overlaps `--syntax-check`, so item J adds a row with near-zero marginal detection                    | medium   | Accepted and stated (D3). The value is the anchor + the corrected stale paragraph, not the rule coverage. If the operator judges that insufficient, 5.5 is separable and can be dropped without touching Epics 1–4                                                                                                                                                                                                                     |
| R3  | The scaffold's generated role skeleton drifts from the evolving conventions of hand-written roles                    | medium   | Issue 3.4 round-trips its output through the Epic 1 + Epic 2 + Epic 5 checks against a **real** target (Prowlarr), so a generator that emits non-conforming artifacts fails the gates rather than silently producing bad guests. It cannot catch *stylistic* drift — accepted                                                                                                                                                          |
| R9  | Landing Prowlarr's inventory (3.4) claims CTID 108 + MAC index 09 before the *arr plan formally scopes that guest    | low      | Status stays `planned`, so no CT exists and the row is a reservation, not a deployment. If the *arr plan later chooses a different CTID ordering, one ledger row and one host_vars file are cheap to move. Operator-confirmed 2026-08-12                                                                                                                                                                                               |
| R10 | The plan's central claim — hygiene now is cheaper than nine repetitions later — is asserted, never sized             | low      | Accepted. The comparison is directional and the epics are independently landable, so a wrong estimate costs sequencing, not correctness. Issue 6.2 records the *actual* cost of Epics 1–5 as the first real datapoint for the #33 sequencing decision                                                                                                                                                                                  |
| R4  | MOUNTS.md's Properties column is prose-annotated (`(default recordsize)`, `**RETIRED**`), so 1.3's parser is brittle | medium   | Fail closed on unrecognised row shapes rather than skipping them (the #56 lesson applied to #55). A parser that silently skips is the bug being fixed                                                                                                                                                                                                                                                                                  |
| R5  | Issue 5.1b is the only live-infrastructure change and carries fleet-wide blast radius                                | medium   | Its own capability gate, which blocks **only the apply** (5.1b) — the authoring + read-only `--check` evidence (5.1a) is ungated, so the gate's precondition is actually reachable. Independent of Epics 1–4 and not an Epic 6 dependency, so it can be deferred indefinitely without stalling the plan                                                                                                                                |
| R6  | `apply_services` as a single switch makes it easier to accidentally apply *everything* at once                       | medium   | The switch only changes the **default expression**; it adds no new authority and every per-role override still wins. Issue 4.2 proves the unset case renders byte-identically. Documented in README as deliberately opt-in                                                                                                                                                                                                             |
| R7  | Epic 6's re-audit is performed by the same agent that wrote this plan, inviting confirmation bias                    | medium   | 6.2 requires each A–D item to be judged against **gate output**, not narrative, and to record retire/re-order outcomes explicitly. "No change to priority" is an acceptable finding only with evidence attached                                                                                                                                                                                                                        |
| R8  | Six epics of pure hygiene delays #33 with no user-visible benefit                                                    | low      | Accepted and deliberate — the whole premise is that nine guests × current per-guest cost exceeds this plan's cost. Epics 1, 2, 4 and 5 are independently landable, so partial completion still pays; Epic 3 is the one exception, trailing Epic 5's `manifest_check.py` via the 3.4 → 5.2 edge                                                                                                                                         |

## Success Criteria

1. **SC1** — `uv run scripts/ansible_ledger_check.py` exits 0 on the hardened tree, and exits
   non-zero on each of three injected drifts: an active RESERVATIONS row with no `host_vars`; an
   unknown `*_bind` key; a `recordsize` mismatch between MOUNTS.md and `pve_storage/defaults`.
2. **SC2** — `garage-webui`'s RESERVATIONS Status reads `active`, and the ledger check fails when
   any `active` row lacks an inventory entry, a `host_vars` file, or a `guests.yml` play it has not
   waived via `in_ct_role: none`. A `planned` row that is pre-staged in inventory (Prowlarr) passes
   — the rule is directional by design, per Issue 1.1.
3. **SC3** — `ansible/secrets.env.tmpl` covers all 30 env vars; `check_secrets_manifest.py` exits 0
   and exits non-zero when a var is added to a role without a manifest row.
4. **SC4** — `grep -c 'op://' ansible/README.md` returns 0 (all refs now live in
   `secrets.env.tmpl`, which README points at once), and every relative path referenced in
   `ansible/README.md` resolves to an existing file — asserted by `manifest_check.py`, which fails
   today on `.pve-token.env.tmpl` and `pve_host/tasks/zfs.yml`.
5. **SC5** — `scripts/new_guest.py` generates **Prowlarr's** real artifact set with no hand
   editing. The **committed** half (RESERVATIONS row CTID 108 Status `planned`,
   `host_vars/prowlarr.yml`) passes the Epic 1 ledger check, `check_secrets_manifest.py`,
   `manifest_check.py`, and `ansible-playbook site.yml --syntax-check`. The **generated-not-committed**
   half (`hosts.yml` entry, `guests.yml` play) is verified by text comparison against the shape the
   existing eight guests use. No CT exists on the host afterwards (`ssh proxmox pct status 108`
   reports it does not exist), and `lxc_guests` still has eight members, not nine.
6. **SC6** — the generated idmap tiles 0–65535 with no gap or overlap, verified by an assertion that
   **fails** on a deliberately wrong tail.
7. **SC7** — `-e apply_services=true` flips every `<role>_apply_service`; with it unset, each
   affected role's **locally rendered** templates and resolved defaults are byte-identical to
   pre-change (no live fleet required); and `host.yml`'s otel play still carries the `never` tag.
8. **SC8** — `manifest_check.py` exits 0, and SPEC §10, `ansible/README.md`, `requirements.yml` and
   `roles/` agree on all 14 roles.
9. **SC9** — `pve_lxc/defaults/main.yml` documents the real `config_bind`/`media_rbind` contract.
10. **SC10** — every CHANGE-VALIDATION FAST + FULL row is verified green on a clean tree, and the
    stale "`ansible-lint` cannot run collection-aware" paragraph is corrected with EXP-001's finding.
11. **SC11** — `ansible-lint --profile min` exits 0 project-wide; each of the 4 `no-changed-when`
    hits is **either fixed or waived with a recorded rationale** (a blanket `changed_when: false`
    to clear the count is not a pass); the residual ~98 are filed upstream with
    `var-naming[no-role-prefix]` marked do-not-bulk-fix.
12. **SC12** — [#55](https://github.com/dixson3/d3-pxe/issues/55),
    [#56](https://github.com/dixson3/d3-pxe/issues/56) and
    [#57](https://github.com/dixson3/d3-pxe/issues/57) are closed with the implementing commit
    referenced.
13. **SC13** — `Incubator/ansible/audit-2026-08-A-D-reassessment.md` exists and records a
    confirm/re-order/retire verdict for each of A, B, C and D, each citing gate output or a measured
    number rather than narrative.
14. **SC14** — no live host or guest state changed except Issue 5.1b (the apply; 5.1a is
    read-only `--check` and mutates nothing). Verified by diff scope alone,
    which needs no fleet access: `git diff --name-only main...HEAD` touches only `ansible/`,
    `scripts/`, `SPEC.md`, `RESERVATIONS.md`, `CHANGE-VALIDATION.md` and the plan folder, and
    `ssh proxmox pct status 108` confirms Prowlarr was never created. A live `--check` converge is
    deliberately **not** the evidence here — it would require the full secret environment and SSH
    to all eight guests, making an otherwise control-node-only plan fleet-dependent.

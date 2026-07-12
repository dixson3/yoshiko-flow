# Plan: Harden beads-backed skills against formula-staging bugs and add a preflight/doctor formula-resolvability check that validates both user-scope and project-scope skills per-repo

**ID:** plan-027-james-dixson-a59656
**Author:** james-dixson
**Created:** 2026-07-11
**Status:** complete
**Epic:** yf-mol-k4k
**Fingerprint:** 1c9df273f24047364fcd34ced1a886cfe98ecb6aecce42802c6e5f0052cbe6c1
**Phase log:**
- 2026-07-11 scoping: initial scope captured
- 2026-07-11 scoping: routing confirmed — new plan (keeps plan-026 fingerprint intact)
- 2026-07-11 investigating: 2 experiments: yf preflight/doctor architecture + check form
- 2026-07-11 drafting: plan v1 synthesized: 5 epics (own-staging + FormulaCheck + cleanup)
- 2026-07-11 review: pass-1 red-team REVISE (2 high, 4 med, 1 low) — see reviews/pass-1.md
- 2026-07-11 review: pass-2 red-team APPROVE (2 med folded, non-blocking) — see reviews/pass-2.md
- 2026-07-11 ready-for-approval: ready-check green — pass-2 APPROVE + audit pass
- 2026-07-11 approved: operator approved
- 2026-07-11 intake: epic yf-mol-k4k poured
- 2026-07-11 executing: start gate resolved
- 2026-07-12 reconciling: post-execution reconciliation; DAG drained
- 2026-07-12 complete: plan complete — merged to main + full-tier validation green; cascade-close clean

## Objective
Harden beads-backed skills against formula-staging bugs and add a preflight/doctor formula-resolvability check that validates both user-scope and project-scope skills per-repo

## Motivation
While executing plan-026, `bd mol wisp plan-investigate` failed with `proto not found`. Root cause:
yf-plan's Phase 2 INVESTIGATE step called the wisp **without staging its formula** into
`.beads/formulas/` first — `bd` resolves molecule protos from `.beads/formulas/`, not the skill
dir. Phase 5's `plan-execute` pour stages correctly (cp/rm bracket); Phase 2 did not. The failure
was **silent** — wrapped in `json-get` + capture-and-continue, so wisp tracking degraded to a
no-op with no operator-visible error.

Two follow-on findings this session:
1. A second latent bug in the same skill: Phase 5's `bd mol burn` lacked `--force`, so it hit an
   interactive `[y/N]`, defaulted to No, and orphaned the wisp.
2. An audit of **all** skills found the staging bug **isolated** to that one spot — yf-plan's
   `plan-execute` and yf-research's `yf-research` pours both stage correctly.

The deeper problem is **class-level, not instance-level**: nothing mechanically prevents a
beads-backed skill from shipping a formula it never stages, and the failure mode is silent. This
is exactly the kind of environment/dependency mismatch `yf` preflight/doctor exists to catch — but
today there is no check for formula resolvability, and preflight/doctor's scope handling of
user-scope vs project-scope skills is unverified. A user-scope skill (installed in `~/.claude`)
operating inside a project still touches that project's `.beads/`, so the check must span **both
scopes per-repo**.

Affected: every author and user of a beads-backed skill in this repo and downstream. Triggered by
the plan-026 wisp failure.

## Scope Decisions (operator-confirmed)
1. **Routing** — tracked as a **new plan** (plan-027), not folded into the approved plan-026.
2. **Include the already-applied wisp fix** — the yf-plan SKILL.md `--force` burn fix (permanent)
   and interim cp/rm staging (a stopgap, superseded by decision 5) applied this session are folded
   in as this plan's motivating, already-done first unit (needs commit + test coverage).
3. **Both scopes → embedded-static coverage.** A static check over the `rust-embed` tree
   transitively covers all install locations (install is a verified byte-identical copy). No
   on-disk 2×2 scope×surface enumeration is added (its incremental value is low — the §3.4 marker
   health axes already catch missing/tampered deployed files). [Q2 → embedded-static.]
4. **Own staging, don't just validate** [Q1, per operator note]. preflight **owns** formula
   staging — it writes each skill's embedded `formulas/*` into the project's `.beads/formulas/`
   (idempotent, gitignored) — so `bd mol pour|wisp` just works and the SKILL.md `cp`/`rm` dance is
   **removed**, making the silent-omission bug class **structurally impossible**. doctor
   statically validates the authoring contract fleet-wide (`FormulaCheck`).
5. **Orphaned/deprecated-formula cleanup** [operator note], **provenance-tracked**. Because
   preflight now owns a persistent staging dir, doctor (with `--repair`) GCs orphaned/deprecated
   staged formulas per-project. **Critical safety boundary (pass-1 H2):** `.beads/formulas/` is
   `bd`'s shared proto namespace — a third-party/local skill (or `bd` itself) may legitimately
   stage formulas there. GC therefore removes **only files yf itself staged** (tracked via a
   yf-owned staged-manifest marker, e.g. `.beads/formulas/.yf-staged.json`) that a currently
   embedded skill **no longer declares** — never the raw "unclaimed by embedded" set. GC runs
   **only behind its own explicit affordance** (a distinct `--prune-formulas` flag, not plain
   `doctor --repair`), so a wedged-DB `--repair` never triggers formula GC (pass-2 N1 — true
   decoupling, resolving the earlier self-contradiction of placing GC inside `run_repair` yet
   calling it "decoupled from `--repair`"). Even so the marker keeps GC fail-safe: no marker →
   deletes nothing.

> **Interpretation flag (confirm):** Q1 had no explicit option selected; the operator note
> ("doctor can clean up orphaned/deprecated formulas per-project") presupposes preflight/doctor
> *owns* the staging dir, so this plan adopts **own-staging** (decision 4) + **cleanup**
> (decision 5). If validate-only was intended, decisions 4–5 change.

## Upstream Issues
_None pre-existing. A single coarse tracking issue will be filed at intake per the AGENTS.md
convention (one issue per plan)._

## Investigation Findings
Two experiments complete; both written up in `findings/`.

**[exp-001/002](findings/exp-001-002-yf-kernel-architecture.md) — yf kernel.** `yf preflight` is a
linear pipeline (`preflight.rs:259`); `yf doctor` is a `Check`-trait **registry**
(`checks.rs:215`) where adding a check is a one-line push. **Pivotal:** skills are discovered from
the **`rust-embed` tree compiled into the binary**, not filesystem globbing — so a static check
over the embedded tree transitively covers every install scope. doctor currently hardcodes a
single scope+surface (`mod.rs:41`), so genuine on-disk 2×2 enumeration would be a structural
refactor (declined, decision 3). Formula basename == `formula="<name>"` == `bd mol pour|wisp
<name>`, giving an exact greppable contract. SPEC home: root `SPEC.md` §3.5 `REQ-YF-PRE`, §3.6
`REQ-YF-DOCTOR` + amendment log; `docs/yf/preflight-contract.md` §2 status enum if a new preflight
status is added.

**[exp-003](findings/exp-003-symlink-vs-copy-staging.md) — symlink vs copy.** `bd` **does** resolve
protos through a symlink, but a committed symlink hard-codes a machine-specific absolute path
(`.beads/formulas/` is not gitignored today) and a dangling link gives the same `proto not found`
plus a *false-presence* trap; a persistent symlink is also incompatible with the current
`rm`-after-pour. Verdict: **copy, not symlink**, and move ownership out of the per-invocation SKILL
body. The bug is a *lifecycle-ownership* problem, not copy-vs-symlink.

Synthesis → **preflight owns copy-staging into a gitignored `.beads/formulas/`; SKILL.md drops the
cp/rm; doctor statically validates + GCs orphaned formulas.**

## Approach

### Epic 1 — SPEC-first (root `SPEC.md`)
- `REQ-YF-PRE-011`: preflight **owns formula staging** — on a beads-backed skill's preflight, write
  that skill's embedded `formulas/*.formula.toml` into the project `.beads/formulas/`, **verifying
  destination existence every run** (unconditional copy — not source-hash-only, so a deleted
  destination re-stages; pass-1 M4), record staged basenames in the yf-owned staged-manifest
  marker, and ensure `/.beads/formulas/` is gitignored in the **root** `.gitignore` via the
  `ensure_scaffold` path (never the bd-managed `.beads/.gitignore`; pass-1 L7). If a new preflight
  **status** is surfaced (e.g. `formula_stage_failed`), also amend `docs/yf/preflight-contract.md`
  §2 enum + returns table.
- `REQ-YF-DOCTOR-004`: doctor **`FormulaCheck`** — static, over the embedded tree. **Extraction
  contract (pass-1 H1):** match only concrete formula tokens in `bd mol (pour|wisp) <name>` inside
  **runnable bash code fences**; **exclude** placeholder tokens (`<name>`, `<formula>`) and prose
  lines. Every such token has a shipped `formulas/<name>.formula.toml` (report + remediation). A
  skill that mentions `bd mol pour` only in prose/templates (yf-beads-authoring, yf-beads-extra)
  **passes**. Under `--repair`, **provenance-tracked GC** removes only yf-staged (per the marker)
  formulas a currently-embedded skill no longer declares.
- SPEC.md living-amendment-log entry. **(SPEC-first — precedes Epics 2–4.)**

### Epic 2 — preflight staging ownership (yf kernel, Rust)
- Implement the staging step in the `preflight.rs` pipeline (after the rule check, beside the
  `ensure_scaffold` calls at :368/:384): write embedded formulas → project `.beads/formulas/`,
  **verifying destination existence every run** (unconditional copy, so a destination deleted after
  any cache still re-stages — pass-1 M4). Record staged basenames in the yf-owned staged-manifest
  marker. Ensure `/.beads/formulas/` is gitignored in the **root** `.gitignore` (ensure_scaffold
  path, not `.beads/.gitignore` — pass-1 L7). **Bump `SCAFFOLD_VERSION` 1→2** (pass-2 N2) — the
  scaffold write short-circuits on `scaffold-ensured == SCAFFOLD_VERSION` (`preflight.rs:46,965`),
  so without the bump every already-preflighted repo (including this one) silently never receives
  the new anchor.
- Rust unit tests: fresh stage, idempotent re-run, source-changed re-copy, **destination-deleted-
  but-cached re-stage**, gitignore anchor added **on a repo carrying a pre-existing older scaffold
  state** (not just a fresh repo — pass-2 N2).

### Epic 3 — doctor FormulaCheck + cleanup (yf kernel, Rust)
Two **distinct code paths** (pass-1 M3): the `Check` registry (`checks()`, read-only, embedded-
scoped) vs. the repair path (`run_repair`, cwd-scoped; `args.repair` returns before `checks()` is
built, `mod.rs:34-37`).
- **FormulaCheck → `checks()`** (`cmd/doctor/checks.rs`, per-skill loop `:239-252`, guarded by
  "skill ships a `formulas/` dir"): apply the Epic-1 extraction contract (runnable-fence, concrete
  tokens, exclude placeholders/prose) over each embedded SKILL.md; assert a shipped formula; report
  `CheckResult`. Read-only, static — no repo handle needed.
- **Provenance-tracked GC → its own affordance** (cwd-scoped, e.g. `doctor --prune-formulas`, NOT
  plain `--repair`; pass-2 N1): using the yf-owned staged-manifest marker, remove only yf-staged
  `.beads/formulas/` entries **no** currently-embedded skill declares (kept if *any* embedded skill
  declares the basename — pass-2 collision note). Never touches foreign/unmarked formulas.
- Rust tests: contract violation flagged (runnable pour, no shipped formula); prose-only pour
  passes (yf-beads-authoring/yf-beads-extra); yf-staged orphan GC'd under repair; **foreign
  (unmarked) formula NOT deleted**.

### Epic 4 — SKILL.md migration: drop the cp/rm dance
- Remove the `cp`/`rm` staging brackets from **all** runnable invocations now that preflight owns
  staging: yf-plan (`plan-execute` pour + the `plan-investigate` wisp — including the interim
  bracket added this session) and yf-research (`yf-research` pour). **Keep** the permanent
  `--force` on `bd mol burn`.
- Update `yf-beads-authoring` guidance: the canonical pattern is now `bd mol pour|wisp <name>` with
  **no** per-call staging — preflight stages; document the `.beads/formulas/` ownership.
- Regression check: the plan-026 wisp scenario resolves with no SKILL.md staging line.
- **Cutover atomicity (pass-1 M5):** `install.sh --force` must **rebuild + install the new `yf`
  binary** (embedding Epic 2 staging) *and* the migrated skills together; gate on `yf --version`
  reflecting the new build before declaring the migration done. A migrated SKILL.md with a stale
  binary on PATH is a broken window.

### Epic 5 — interim fix commit + drift/hygiene wiring
- Commit the already-applied session fixes (yf-plan SKILL.md `--force` + interim staging) as the
  motivating first change, clearly noted as partially superseded by Epic 4.
- Extend `yf-drift-check` `e-formula-name` edge (or add a sibling) so the "pour/wisp ↔ shipped
  formula + staging-ownership" contract is also guarded at drift-check time, consistent with the
  new no-stage SKILL pattern.

## Epics

### Epic 1: SPEC-first — kernel REQs
- Issue 1.1: `REQ-YF-PRE-011` (preflight owns staging) in `SPEC.md` §3.5; add a preflight status +
  `docs/yf/preflight-contract.md` §2 update only if a new status is surfaced.
- Issue 1.2: `REQ-YF-DOCTOR-004` (FormulaCheck static validation + orphaned/deprecated GC) in
  `SPEC.md` §3.6.
- Issue 1.3: `SPEC.md` living-amendment-log entry covering 1.1 + 1.2.
  - depends-on: 1.1, 1.2

### Epic 2: preflight staging ownership (Rust)
- Issue 2.1: Implement embedded-formula → `.beads/formulas/` staging in the `preflight.rs`
  pipeline; verify-destination-every-run (not source-hash-only), staged-manifest marker recorded,
  root-`.gitignore` anchor ensured.
  - depends-on: 1.1
- Issue 2.2: Rust tests — fresh stage, idempotent re-run, source-changed re-copy,
  destination-deleted-but-cached re-stage, gitignore anchor.
  - depends-on: 2.1

### Epic 3: doctor FormulaCheck + cleanup (Rust)
- Issue 3.1: `FormulaCheck` into the read-only `checks()` registry (`cmd/doctor/checks.rs`,
  per-skill loop) with the runnable-fence + concrete-token extraction contract (excludes
  placeholders/prose).
  - depends-on: 1.2
- Issue 3.2: Provenance-tracked GC behind its own affordance (`doctor --prune-formulas`, cwd-scoped,
  NOT plain `--repair`) using the staged-manifest marker; removes only yf-staged formulas no
  embedded skill declares; never foreign/unmarked formulas.
  - depends-on: 1.2, 2.1
- Issue 3.3: Rust tests — runnable-pour-without-formula flagged; prose-only pour passes
  (yf-beads-authoring/yf-beads-extra); yf-staged orphan GC'd; foreign (unmarked) formula NOT
  deleted.
  - depends-on: 3.1, 3.2

### Epic 4: SKILL.md migration — drop cp/rm
- Issue 4.1: Remove cp/rm brackets from yf-plan (`plan-execute` + `plan-investigate`) and
  yf-research (`yf-research`); keep `--force`. Gated on staging being owned (Epic 2) and the interim
  fix being committed first (5.1).
  - depends-on: 2.1, 5.1
- Issue 4.2: Update `yf-beads-authoring` to document the no-stage canonical pattern + staging
  ownership.
  - depends-on: 4.1
- Issue 4.3: Cutover — rebuild+install the new `yf` binary AND migrated skills (`install.sh
  --force`), gate on `yf --version`; regression: plan-026 wisp scenario resolves with no SKILL.md
  staging line.
  - depends-on: 4.1, 2.1, 3.1

### Epic 5: interim commit + drift wiring
- Issue 5.1: Commit the already-applied session fixes (yf-plan SKILL.md `--force` + interim
  staging), noted as partially superseded by Epic 4. (Early — independent of kernel work.)
- Issue 5.2: Extend `yf-drift-check` to guard the pour/wisp ↔ formula + staging-ownership contract
  consistent with the migrated no-stage pattern.
  - depends-on: 4.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Rust toolchain
- Type: human
- Approvers: operator
- Condition: the `yf` kernel builds and tests run (`cargo build`, `cargo test` in `yf/`).
- Test: `cargo test --manifest-path yf/Cargo.toml`
- Blocks: Epics 2, 3 (Rust implementation)
- Instructions: ensure the Rust toolchain is present; this is a kernel-code plan, not a
  skills-only plan.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step (single coarse tracking issue filed at intake)

## Risks & Mitigations
| Risk | Mitigation |
|:-----|:-----------|
| Removing SKILL.md cp/rm (Epic 4) before preflight staging (Epic 2) lands leaves skills broken | Hard `depends-on: 2.1` on every Epic-4 issue; the interim session fix (Epic 5.1) keeps the skill correct until then. |
| preflight now **writes** to `.beads/formulas/` — a new side effect in a mostly-read pipeline | Precedent exists (`ensure_scaffold` writes gitignore anchors); idempotent + hash-guarded; gitignored so never committed. |
| **Orphaned-formula GC deletes a foreign formula (data loss)** — `.beads/formulas/` is bd's shared namespace | **Provenance-tracked GC (pass-1 H2):** remove only files recorded in the yf-owned staged-manifest marker that no embedded skill declares — never the raw "unclaimed by embedded" set. GC runs only behind its own `--prune-formulas` affordance, not plain `--repair`, so a wedged-DB repair can't delete formulas (pass-2 N1). Test asserts a foreign/unmarked formula is untouched. |
| Source-hash-only staging leaves a deleted destination unrestaged → `proto not found` returns | Verify destination existence every preflight run (unconditional copy); regression test for destination-deleted-but-cached (pass-1 M4). |
| Cutover broken window — migrated SKILL.md with a stale binary lacking staging | Epic 4.3 rebuilds+installs the new binary atomically with the skills and gates on `yf --version`; Epic 4 hard-depends on Epic 2 (pass-1 M5). |
| "Both scopes" requirement under-delivered by embedded-static coverage | Documented decision (3): embedded == verified byte-identical install; marker health axes already cover on-disk drift. If genuine 2×2 on-disk sweep is later needed, it is a scoped follow-on, not silently dropped. |
| Interim cp/rm commit (5.1) then removed (4.1) reads as churn | Explicit phase-log/commit note that 5.1 is a stopgap superseded by 4.1 except the permanent `--force`. |
| doctor single-scope hardcode (`mod.rs:41`) misleads future work | Note in SPEC/amendment log that FormulaCheck is embedded-tree-based by design and does not use the on-disk scope path. |

## Success Criteria
- preflight stages a beads-backed skill's embedded formulas into a gitignored `.beads/formulas/`
  idempotently; `bd mol pour|wisp <name>` resolves with **no** SKILL.md staging line.
- `yf doctor` statically flags any `bd mol pour|wisp <name>` lacking a shipped formula, and passes
  the current three-formula fleet; `doctor --repair` GCs an orphaned `.beads/formulas/` entry.
- All cp/rm staging brackets removed from yf-plan + yf-research SKILL.md; `--force` burn retained;
  the plan-026 wisp scenario works without staging.
- New `REQ-YF-PRE-011` + `REQ-YF-DOCTOR-004` landed ahead of code with a SPEC amendment-log entry;
  each new behavior has a Rust test.
- `yf-beads-authoring` documents the no-stage canonical pattern; `yf-drift-check` guards the
  contract; session interim fixes committed.
- A single coarse upstream tracking issue filed for the plan.

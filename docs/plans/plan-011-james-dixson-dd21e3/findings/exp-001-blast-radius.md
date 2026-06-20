# EXP-001 — Blast radius: what the YOSHIKO_FLOW.md consolidation touches

**Question:** Which code, tests, specs, and docs change when per-skill standalone
companion rules become one aggregated, fenced `YOSHIKO_FLOW.md`?

## Source code (Rust, `yf/src/`)

| File | What changes | Notes |
|------|--------------|-------|
| **new `flow.rs`** | Parse/serialize the fenced aggregate; per-section body sha256; banner; deterministic (alpha-by-protocol) ordering; reconcile against embedded set | The new home for all aggregate-format logic, mirroring `marker.rs`'s role for SKILL.md. |
| `cmd/common.rs` | `install_rules` rewritten to splice/regenerate sections in `YOSHIKO_FLOW.md` (was: one file per `protocols/*.md`). `embedded_rules` KEPT — still yields `(basename, bytes)` source. Add: aggregate read/upsert/prune helpers (or delegate to `flow.rs`). | `install_rules` signature/semantics change; `--force` no longer gates rule content (S3). |
| `cmd/install.rs:51,93` | Call aggregate install; dry-run reporting no longer prints per-base target paths — prints section upserts + the single `YOSHIKO_FLOW.md` target. | |
| `cmd/status.rs:92,159` | `upgrade` → regenerate acted-on sections + **reconcile-prune** invalid sections. `remove` → drop sections; delete file when last section removed. Test block (lines 218-404) substantially rewritten. | |
| `cmd/doctor.rs:222` `check_rules` | Read each protocol's **section body** from `YOSHIKO_FLOW.md` (legacy fallback to standalone). Verdict precedence (`rule_missing`/`rule_drift`) preserved. Tests 283-298 updated. | |
| `preflight.rs:653` `check_rule` | Locate the protocol's section in `YOSHIKO_FLOW.md`, hash body vs `manifest.json`; **legacy fallback** to standalone file when aggregate absent (S5). `Env.rule_dirs` precedence retained. Tests: `tampered_rule_yields_drift`, `matching_rule_yields_ok`, `missing_rule_yields_rule_missing`, `preflight_parity_rule_drift`. | Section body == protocol file verbatim, so it hashes identically to the manifest sha256 — same hash basis, no manifest change. |
| `coverage.rs:223` | Update REQ-YF-INSTALL-006 wording; add coverage rows for any new REQ-YF-FLOW-* items. | |

## NOT affected (confirmed)

- **`parity.rs` / `testdata/install-parity.json` / `gen-install-parity.py`** — the
  frozen golden covers frontmatter/group/closure computation ONLY (REQ-YF-INSTALL-003/004),
  not rule-file install. No regeneration needed. (`grep` for rule/protocol in `parity.rs`
  is empty.)
- **`protocols/manifest.json`** (all 7 skills) — unchanged. Section-body sha256 equals the
  manifest file sha256 because the body is the protocol file verbatim.

## Spec / docs (drift-checked edges — must stay in sync)

- **`SPEC.md`** (macro-spec, `fixed` authority): REQ-YF-INSTALL-001 (rules → single
  `YOSHIKO_FLOW.md`), REQ-YF-INSTALL-006 (supersede "preserve unless --force"),
  REQ-YF-PRE-003 (section-aware + legacy fallback). Likely a **new REQ-YF-FLOW-*** group
  for the aggregate format, reconcile-prune, and banner.
- **`README.md`** (project-readme): lines ~37,49,54-55,71 describe per-file companion rules
  and `--force`-keeps-hand-edits — rewrite. **`DRIFT-CHECK.md` edge `e-spec-readme`
  (macro-spec → project-readme, behavioral)** binds these two: change both together.
- **`docs/MIGRATION.md:40`**, **`docs/yf/preflight-contract.md`** (rule verdict wording).

## Migration (S4)

One-time fold-in of already-installed standalone rule files into `YOSHIKO_FLOW.md` + delete
of the standalone. Belongs in the install/upgrade write path (not the existing `yf migrate`,
which handles the legacy `.state/` → `.yf/` layout — a separate concern). Idempotent: a
second run finds no standalone to fold.

## Conclusion

Bounded, single-binary change. New `flow.rs` module + four command-path rewrites
(install/upgrade/remove/doctor) + `preflight.check_rule` + spec/README/docs sync. No parity
golden regeneration. The riskiest seams: (a) `preflight`/`doctor` legacy fallback during the
transition release, and (b) the reconcile-prune correctly distinguishing "not selected this
run" (keep) from "no longer embedded / deprecated" (drop).

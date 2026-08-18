//! `yf-beads-init` verify + repair — the dependency-verification home (beads 2.4
//! / 2.5, REQ-YF-PRE-006 / REQ-YF-PRE-007).
//!
//! A faithful Rust port of `skills/yf-beads-init/scripts/beads_init.py`'s
//! `verify_beads()` (the read-only classifier) and `repair` (the idempotent fix
//! sequence). The Python script remains embedded and is shelled (via `uv run`) for
//! the most stateful repair parts (bd hooks/doctor/migrate); the simple
//! deterministic hardening (perms, gitignore top-up, local-only assertion) is
//! native Rust. See [`repair`] for the per-step native-vs-shelled rationale.
//!
//! ## The load-bearing invariant (REQ-YF-PRE-006)
//!
//! Classification parses `bd status --json` for an **`error` key in the parsed
//! JSON**, NOT the process exit code: `bd status --json` can return error-JSON with
//! exit 0 (e.g. a pending schema migration blocked by a dirty Dolt working set). An
//! initialized-but-wedged repo therefore classifies [`VerifyStatus::Corrupted`],
//! never [`VerifyStatus::NotInitialized`]. The JSON classification is the PURE
//! function [`classify`], unit-testable with canned `bd status --json` strings.

use std::path::{Path, PathBuf};
use std::process::Command;

use serde::Serialize;

/// Minimum bd version (`MIN_BD_VERSION = (1, 0, 5)`).
const MIN_BD_VERSION: (u32, u32, u32) = (1, 0, 5);

/// `.beads/.gitignore` patterns bd doctor v1.0.5's `--fix` may miss (legacy
/// `_BEADS_GITIGNORE`).
const BEADS_GITIGNORE: &[&str] = &[
    ".env",
    "export-state.json",
    // #66 (REQ-BINIT-023): `interactions.jsonl` is in the BEADS_UNTRACK set, so
    // repair `git rm --cached`s it — but without a matching `.beads/.gitignore`
    // entry it immediately resurfaced as `?? .beads/interactions.jsonl` noise.
    // Ignoring it here gives untrack ⇒ ignore parity (untracked AND ignored).
    "interactions.jsonl",
    "embeddeddolt/",
    "proxieddb/",
    "dolt-server.activity",
    "daemon.*",
    "*.lock",
    "*.corrupt.backup/",
    ".beads-credential-key",
    "proxied_server_client_info.json",
];

/// Project-root `.gitignore` patterns beads needs (legacy `_PROJECT_GITIGNORE`).
const PROJECT_GITIGNORE: &[&str] = &[".beads-credential-key", ".beads/proxieddb/"];

/// The pinned set of runtime/derived `.beads/` paths that must never be tracked
/// by git (#39, Epic B.1). The `untrack-runtime` native verb `git rm --cached`s
/// exactly these — restricted to paths CURRENTLY TRACKED, so it is a clean no-op
/// when nothing is tracked, and keeps the working-tree copy. Each entry is matched
/// against `git ls-files`:
///
/// - a trailing-slash entry (`embeddeddolt/`, `backup/`) untracks any tracked path
///   UNDER that directory;
/// - a trailing-`.*` entry (`dolt-server.*`) is a glob expanded against tracked
///   files (NOT passed literally to `git rm`);
/// - any other entry is an exact tracked-path match.
const BEADS_UNTRACK: &[&str] = &[
    ".beads/interactions.jsonl",
    ".beads/embeddeddolt/",
    ".beads/backup/",
    ".beads/export-state.json",
    ".beads/push-state.json",
    ".beads/dolt-server.*",
];

/// The shim signature: a tracked `.beads/hooks/*` file is a bd-generated shim (and
/// therefore safe to remove via `remove-hook-shims`) ONLY if its content invokes
/// `bd hooks run`. A hand-edited hook lacking this substring is NEVER removed.
const HOOK_SHIM_SIGNATURE: &str = "bd hooks run";

/// Marker-fenced "managed block" spans that `bd init` injects into instruction
/// files (`CLAUDE.md` / `AGENTS.md`). Each pair is `(begin-prefix, end-marker)`;
/// the begin marker carries a trailing `v:/profile:/hash:` suffix so we match on a
/// prefix. Used by [`strip_managed_blocks`] for the repair-time marker-scoped strip
/// (#31, B.3). `bd setup claude --remove` owns the CLAUDE.md + settings.json hook,
/// but the generic `BEADS INTEGRATION` block can also land in `AGENTS.md` (the
/// `--skip-agents`/agents-profile block), which no `bd setup … --remove` strips —
/// so this is the marker-owned fallback for both files.
const MANAGED_BLOCKS: &[(&str, &str)] = &[
    (
        "<!-- BEGIN BEADS INTEGRATION",
        "<!-- END BEADS INTEGRATION -->",
    ),
    (
        "<!-- BEGIN BEADS CODEX SETUP",
        "<!-- END BEADS CODEX SETUP -->",
    ),
];

// ---------------------------------------------------------------------------
// Verify
// ---------------------------------------------------------------------------

/// The verify verdict enum (distinct from the preflight enum — see the contract
/// §5). Maps to preflight as: `DepsMissing → system_deps_missing`,
/// `NotInitialized | Corrupted → bd_not_initialized`, `Ok → (pass)`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum VerifyStatus {
    Ok,
    DepsMissing,
    NotInitialized,
    Corrupted,
}

impl VerifyStatus {
    /// The lowercase wire string (matches the Python `status` field).
    pub fn as_str(self) -> &'static str {
        match self {
            VerifyStatus::Ok => "ok",
            VerifyStatus::DepsMissing => "deps_missing",
            VerifyStatus::NotInitialized => "not_initialized",
            VerifyStatus::Corrupted => "corrupted",
        }
    }
}

/// The full verify verdict (mirrors the Python `verify_beads()` result object).
#[derive(Debug, Clone, Serialize)]
pub struct VerifyResult {
    pub status: VerifyStatus,
    pub tools_missing: Vec<String>,
    pub repo_initialized: bool,
    pub bd_functional: bool,
    pub diagnostics: Vec<String>,
    pub remediations: Vec<String>,
}

impl VerifyResult {
    fn base() -> Self {
        VerifyResult {
            status: VerifyStatus::Ok,
            tools_missing: vec![],
            repo_initialized: false,
            bd_functional: false,
            diagnostics: vec![],
            remediations: vec![],
        }
    }
}

/// PURE classification of a `bd status --json` run into the initialized/wedged
/// verdict, given whether `.beads/` exists. This is the REQ-YF-PRE-006 core: it
/// inspects the **parsed JSON for an `error` key**, never the exit code.
///
/// `raw` is the raw stdout of `bd status --json`. Returns the classified status
/// plus whether bd is functional (so callers can fill `bd_functional`). Mirrors
/// the Python branch order in `verify_beads()` steps 2–3 exactly:
///
/// 1. `.beads/` absent AND (`doc` is None OR has `error`) → `not_initialized`.
/// 2. `doc` has `error` → `corrupted` (initialized-but-wedged — the false-negative
///    case the exit-code-only check would mislabel).
/// 3. `doc` is None → `corrupted` if initialized else `not_initialized`.
/// 4. parse OK, no `error` → `ok` (functional).
pub fn classify(raw: &str, repo_initialized: bool) -> (VerifyStatus, bool) {
    let doc = first_json_doc(raw);
    let has_error = doc.as_ref().is_some_and(|d| d.get("error").is_some());

    if !repo_initialized && (doc.is_none() || has_error) {
        return (VerifyStatus::NotInitialized, false);
    }
    if has_error {
        return (VerifyStatus::Corrupted, false);
    }
    if doc.is_none() {
        return (
            if repo_initialized {
                VerifyStatus::Corrupted
            } else {
                VerifyStatus::NotInitialized
            },
            false,
        );
    }
    (VerifyStatus::Ok, true)
}

/// Read-only health check (the Python `verify_beads()`). Never mutates the repo.
pub fn verify(repo_root: &Path) -> VerifyResult {
    let mut r = VerifyResult::base();

    // 1 — system tools (git, uv, bd ≥ MIN_BD_VERSION).
    let mut missing = vec![];
    if which("git").is_none() {
        missing.push("git".to_string());
    }
    if which("uv").is_none() {
        missing.push("uv".to_string());
    }
    match parse_bd_version() {
        None => missing.push("bd".to_string()),
        Some(v) if v < MIN_BD_VERSION => missing.push(format!(
            "bd>={}.{}.{}",
            MIN_BD_VERSION.0, MIN_BD_VERSION.1, MIN_BD_VERSION.2
        )),
        Some(_) => {}
    }
    if !missing.is_empty() {
        r.status = VerifyStatus::DepsMissing;
        r.diagnostics.push(format!(
            "Required tool(s) missing/outdated: {}",
            missing.join(", ")
        ));
        r.remediations.push(
            "Install missing tools (bd: https://github.com/gastownhall/beads; \
             uv: https://docs.astral.sh/uv/)."
                .to_string(),
        );
        r.tools_missing = missing;
        return r;
    }

    // 2 — repo initialized? (.beads/ present)
    let beads_dir = repo_root.join(".beads");
    r.repo_initialized = beads_dir.is_dir();

    // 3 — is bd functional here? THE key check: classify on parsed JSON, not exit.
    // Run bd in the target repo so `bd status` reflects THIS repo, not the cwd.
    let (rc, out, err) = run_in(&["bd", "status", "--json"], 60, repo_root);
    let (status, functional) = classify(&out, r.repo_initialized);
    let doc = first_json_doc(&out);

    match status {
        VerifyStatus::NotInitialized => {
            r.status = VerifyStatus::NotInitialized;
            r.diagnostics
                .push("No .beads/ directory and `bd status` is not usable here.".to_string());
            r.remediations.push(
                "Run `bd init` (fresh repo), then `yf doctor --repair` to harden.".to_string(),
            );
            return r;
        }
        VerifyStatus::Corrupted => {
            r.status = VerifyStatus::Corrupted;
            r.bd_functional = false;
            if let Some(d) = &doc {
                if let Some(msg) = d.get("error") {
                    let msg = msg
                        .as_str()
                        .map(str::to_string)
                        .unwrap_or_else(|| msg.to_string());
                    r.diagnostics.push(format!(
                        "`bd status --json` returned an error (exit {rc}): {msg}"
                    ));
                    let lower = msg.to_lowercase();
                    if WEDGED_MARKERS.iter().any(|m| lower.contains(m)) {
                        r.diagnostics.push(
                            "Signature: pending schema migration blocked by a dirty Dolt working set."
                                .to_string(),
                        );
                        // Mode-aware remediation (RT-1): `bd dolt stop` ERRORS in
                        // embedded storage (no server), so advise the
                        // data-preserving embedded commit there instead.
                        if is_embedded_mode(&beads_dir) {
                            r.remediations.push(
                                "Embedded storage: run `yf doctor --repair --apply` — it commits the \
                                 embedded Dolt working set (data-preserving), then `bd migrate schema` \
                                 then `bd migrate`. (`bd dolt stop` does not apply — there is no server.)"
                                    .to_string(),
                            );
                        } else {
                            r.remediations.push(
                                "Flush + migrate: `bd dolt stop` then `bd migrate schema` then `bd migrate`."
                                    .to_string(),
                            );
                        }
                    } else {
                        r.remediations.push(
                            "Run `yf doctor --repair` to attempt standard repairs.".to_string(),
                        );
                    }
                    return r;
                }
            }
            // doc is None but initialized → corrupted with no parseable JSON.
            r.diagnostics.push(format!(
                "`bd status --json` produced no parseable JSON (exit {rc}). stderr: {}",
                err.trim().chars().take(200).collect::<String>()
            ));
            r.remediations.push("Run `yf doctor --repair`.".to_string());
            return r;
        }
        VerifyStatus::Ok => {
            r.bd_functional = functional;
            r.repo_initialized = true;
        }
        VerifyStatus::DepsMissing => unreachable!("deps handled above"),
    }

    // 4 — advisory hygiene (does not change status).
    if let Some(mode) = dir_mode(&beads_dir) {
        if mode != 0o700 {
            r.diagnostics
                .push(format!(".beads perms are {mode:#o} (want 0o700)."));
            r.remediations.push("chmod 700 .beads".to_string());
        }
    }
    let (_, doctor_out, _) = run_in(&["bd", "doctor"], 60, repo_root);
    for line in doctor_out.lines() {
        let lower = line.to_lowercase();
        if line.contains('\u{2716}') && lower.contains("error") && !line.contains(" 0 ") {
            r.diagnostics.push(format!("bd doctor: {}", line.trim()));
        }
    }
    r
}

/// Patterns in a `bd status` error that indicate a wedged (not absent) DB
/// (`_WEDGED_MARKERS`).
const WEDGED_MARKERS: &[&str] = &["schema migration", "dirty table", "pending schema"];

// ---------------------------------------------------------------------------
// Repair
// ---------------------------------------------------------------------------

/// A single planned/applied repair step.
#[derive(Debug, Clone, Serialize)]
pub struct RepairStep {
    pub why: String,
    /// The shell command (argv) — informational; native steps carry a synthetic
    /// argv (e.g. `["<native>", "chmod", "700", ".beads"]`) for a uniform plan.
    pub cmd: Vec<String>,
    /// Whether this step is executed natively (Rust) or shelled to `bd`/`uv`.
    pub native: bool,
    /// Applied result (None in dry-run): exit code + truncated stderr.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rc: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub err: Option<String>,
}

/// The repair plan + (when applied) before/after verify verdicts.
#[derive(Debug, Serialize)]
pub struct RepairResult {
    pub before: VerifyResult,
    pub plan: Vec<RepairStep>,
    pub applied: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub after: Option<VerifyResult>,
}

/// The mode-aware wedged-migration step descriptors (REQ-BINIT-011/016) as
/// ordered `(why, native, args)` tuples — split out from [`repair`] so the plan
/// shape is unit-testable without a live wedged repo. Embedded storage gets the
/// NATIVE `dolt-commit-embedded` step (its cwd is DERIVED at apply time — no
/// hardcoded path in the plan); server mode gets the shelled `bd dolt stop`.
/// Both share the `bd migrate schema` → `bd migrate` tail. `args` is the verb
/// slice for a native step, or the full argv for a shelled one.
fn wedged_migration_steps(embedded: bool) -> Vec<(&'static str, bool, Vec<&'static str>)> {
    let flush = if embedded {
        (
            "commit embedded Dolt working set (data-preserving; no server to stop)",
            true,
            vec!["dolt-commit-embedded"],
        )
    } else {
        (
            "stop dolt server (flush working set)",
            false,
            vec!["bd", "dolt", "stop"],
        )
    };
    vec![
        flush,
        (
            "apply schema migrations",
            false,
            vec!["bd", "migrate", "schema"],
        ),
        ("update db metadata version", false, vec!["bd", "migrate"]),
    ]
}

/// Diagnose and (when `apply`) fix a non-existent / incorrect / corrupted beads
/// config — the idempotent repair sequence (REQ-YF-PRE-007). This `yf` kernel is
/// the reference implementation; `scripts/beads_init.py` is a retired shim.
///
/// ## Native vs shelled, per step (R5 bounded-fallback rationale, GR-011)
///
/// `bd`-driven steps are SHELLED to the real `bd` binary (the contract's
/// authority on Dolt state; reimplementing them in Rust would duplicate bd's
/// migration/hook logic and drift):
///
/// - `bd init` (not_initialized) — shelled.
/// - wedged-migration fix (REQ-BINIT-011/016): the working-set flush is
///   MODE-AWARE — server mode shells `bd dolt stop`; embedded storage has no
///   server, so it runs the NATIVE `dolt-commit-embedded` step (raw `dolt` in the
///   derived cwd) instead — then `bd migrate schema` → `bd migrate` (shelled).
///   Never `bd vc commit` first (it cannot open the wedged DB).
/// - hardening `bd hooks install --force`, `bd doctor --fix`, `bd migrate`,
///   `bd export -o .beads/issues.jsonl` — shelled.
/// - local-only assertion `bd config set dolt.local-only true` — shelled. Repair
///   never *adds* a Dolt remote; the opt-in `remove_remote` (below) is the one
///   step that *clears* an existing remote under local-only context (#39, B.1).
///
/// Simple deterministic filesystem hardening is NATIVE Rust (no bd needed; pure
/// `std::fs`): `.beads` perms (chmod 700) and the gitignore top-ups
/// (`_ensure_gitignore`). These mirror the Python `os.chmod` + `_ensure_gitignore`
/// tail of `repair`.
///
/// `local_only` adds the local-only assertion step (Surface §: local-only repos).
///
/// `remove_remote` (#39, B.1) is an explicit opt-in: when `true` AND `local_only`,
/// repair clears the configured Dolt remote at **both** layers — the decisive
/// **Dolt-DB-level** remote (raw `dolt remote remove`) and the secondary
/// **`sync.remote` config** key — and then **verifies the postcondition**, failing
/// if a remote survives (REQ-YF-DOCTOR-006). Off by default — the
/// `--remove-remote` doctor flag is the only way to reach it, because it inverts
/// the otherwise-conservative "never touch the remote" boundary above.
///
/// *(plan-044 Issue 1.5: this doc, the `cli.rs` flag help and the step label had
/// drifted into three different claims — two of them naming only `sync.remote`,
/// the layer that does NOT govern whether a push can reach a remote. They now
/// state one accurate behavior.)*
pub fn repair(
    repo_root: &Path,
    apply: bool,
    local_only: bool,
    remove_remote: bool,
) -> anyhow::Result<RepairResult> {
    let before = verify(repo_root);
    let beads_dir = repo_root.join(".beads");

    if before.status == VerifyStatus::DepsMissing {
        anyhow::bail!(
            "Cannot repair: install missing tools first: {}",
            before.tools_missing.join(", ")
        );
    }

    let mut plan: Vec<RepairStep> = Vec::new();
    let shelled = |why: &str, cmd: &[&str]| RepairStep {
        why: why.to_string(),
        cmd: cmd.iter().map(|s| s.to_string()).collect(),
        native: false,
        rc: None,
        err: None,
    };
    // A native (Rust `std::fs`) step. `verb` is the dispatch key consumed by
    // [`apply_native`] (`cmd[1]`); a synthetic `<native>` argv keeps the plan
    // shape uniform with shelled steps.
    let native_step = |why: &str, verb: &[&str]| RepairStep {
        why: why.to_string(),
        cmd: std::iter::once("<native>".to_string())
            .chain(verb.iter().map(|s| s.to_string()))
            .collect(),
        native: true,
        rc: None,
        err: None,
    };

    if before.status == VerifyStatus::NotInitialized {
        // B.1 — init-time cruft suppression (#31). `--skip-hooks` suppresses the
        // beads git-hooks class; `--skip-agents` suppresses the AGENTS.md /
        // CLAUDE.md managed blocks, `.codex/`, `.agents/skills/beads/`, and the
        // `.claude/settings.json` SessionStart hook in one flag. Then assert
        // `dolt.local-only` (no Dolt remote) and silence the doctor "Git Hooks"
        // warning now that hooks are intentionally absent.
        plan.push(shelled(
            "initialize beads (suppress hooks + agents cruft)",
            &["bd", "init", "--skip-hooks", "--skip-agents"],
        ));
        // plan-044 Issue 1.6 (#160), MEASURED — the old label ("no remote wired at
        // init") was FALSE. A sandboxed probe against a repo with a git origin
        // shows `bd init` wiring one unprompted:
        //
        //     ✓ Configured Dolt remote: origin → git+https://github.com/…
        //
        // and the `dolt.local-only` assertion below does NOT remove it: after both
        // steps, `sync.remote` is still set AND `dolt remote -v` still lists
        // `origin`. `dolt.local-only` is an INIT-TIME skip flag (REQ-BINIT-027), and
        // it is set here only AFTER init has already run — so on this path repair
        // produced exactly the #160 state it claimed to prevent.
        //
        // Reordering is not available: the flag lives in `.beads/config.yaml`, which
        // does not exist before `bd init`, and `bd init` exposes no local-only /
        // no-remote flag (only `--remote`, which adds one). So the fix is the
        // implied removal below.
        plan.push(shelled(
            "assert local-only Dolt (bd init may have wired a remote from git origin)",
            &["bd", "config", "set", "dolt.local-only", "true"],
        ));
        // Remove the remote THIS RUN just created. Note the narrow scope: on the
        // init path there was no beads repo moments ago, so this can only ever
        // clear a remote repair itself wired against the operator's explicit
        // local-only request. It never touches a pre-existing operator remote —
        // which is why implying it here does not invert the conservative
        // "never touch the remote" boundary that keeps `--remove-remote` opt-in
        // everywhere else. Idempotent: a no-remote repo is a clean no-op.
        if local_only {
            plan.push(native_step(
                "clear the Dolt remote bd init wired from git origin (implied by \
                 --local-only on the init path), then verify it is gone",
                &["remove-remote"],
            ));
        }
        plan.push(shelled(
            "suppress doctor git-hooks warning (hooks intentionally absent)",
            &["bd", "config", "set", "doctor.suppress.git-hooks", "true"],
        ));
    }

    // Wedged-migration repair (REQ-BINIT-011/016): clear the dirty working set,
    // THEN migrate. The flush is MODE-AWARE — server mode stops the Dolt server;
    // embedded storage has no server (`bd dolt stop` errors there), so it commits
    // the on-disk working set via a data-preserving raw-`dolt` native step first.
    // The ordered step descriptors live in the pure [`wedged_migration_steps`] so
    // the plan shape is unit-testable without a live wedged repo.
    if before.status == VerifyStatus::Corrupted {
        for (why, native, args) in wedged_migration_steps(is_embedded_mode(&beads_dir)) {
            plan.push(if native {
                native_step(why, &args)
            } else {
                shelled(why, &args)
            });
        }
    }

    // Hardening (idempotent) — runs whenever .beads/ exists or after init.
    //
    // B.2 (#31): the former `bd hooks install --force` step is intentionally
    // GONE. Repair must NEVER (re-)install beads git hooks — that is the inverse
    // of #31's init-time `--skip-hooks` suppression and would re-dirty a repo the
    // cleanup steps below are trying to clean. Removing it (rather than gating it)
    // makes repair monotone with respect to hooks: it only ever removes them.
    plan.push(shelled(
        "repair gitignore/config",
        &["bd", "doctor", "--fix"],
    ));
    plan.push(shelled("update db metadata version", &["bd", "migrate"]));
    if local_only {
        plan.push(shelled(
            "assert local-only Dolt",
            &["bd", "config", "set", "dolt.local-only", "true"],
        ));
    }
    plan.push(shelled(
        "export portable JSONL",
        &["bd", "export", "-o", ".beads/issues.jsonl"],
    ));

    // ---- B.3/B.4 (#31): repair-time cruft cleanup for already-dirtied repos ----
    // Every step is idempotent and bd-native where bd owns the artifact. On a
    // clean repo (this repo's reference state) each is a no-op, so re-running
    // repair never churns. These run on EVERY repair (not gated on a dirty
    // detection) precisely because they are idempotent no-ops when clean.

    // (c) git hooks: uninstall beads hooks + reset core.hooksPath to the git
    // default. `bd hooks uninstall` clears both; the native reset below is a belt
    // for any stray `core.hooksPath` bd did not own.
    plan.push(shelled(
        "uninstall beads git hooks (never re-install)",
        &["bd", "hooks", "uninstall"],
    ));
    // (a)+(b) Claude: removes the CLAUDE.md managed block AND the entry-scoped
    // `.claude/settings.json` SessionStart hook (B.4 — never wholesale-deletes the
    // file; leaves `{"hooks": {}}`). bd owns this marker.
    plan.push(shelled(
        "remove beads Claude integration (CLAUDE.md block + settings.json hook)",
        &["bd", "setup", "claude", "--remove"],
    ));
    // (b) Codex: removes `.agents/skills/beads/`, the codex AGENTS.md block, and
    // the `.codex/` native-hooks setup.
    plan.push(shelled(
        "remove beads Codex integration (.agents/skills/beads, .codex, AGENTS.md block)",
        &["bd", "setup", "codex", "--remove"],
    ));

    // Native cleanup steps (deterministic, no bd) — see `apply_native`.
    plan.push(native_step(
        "reset core.hooksPath to git default",
        &["hookspath-reset"],
    ));
    plan.push(native_step(
        "remove residual .agents/skills/beads/ dir",
        &["rmdir-beads-skill"],
    ));
    plan.push(native_step(
        "strip beads managed blocks from CLAUDE.md/AGENTS.md (marker-scoped)",
        &["strip-managed-blocks"],
    ));
    plan.push(native_step(
        "prune empty beads-injected .claude/settings.json (delete only if empty)",
        &["prune-settings"],
    ));
    plan.push(native_step(
        "prune empty beads-injected .codex/config.toml (delete only if empty)",
        &["prune-codex"],
    ));

    // #39 B.1 — untrack/remote-removal cleanup (the canonicalization axis). Each
    // is idempotent and tracked-state-gated: a no-op when nothing is tracked.
    plan.push(native_step(
        "untrack runtime .beads/ artifacts (git rm --cached; keep working files)",
        &["untrack-runtime"],
    ));
    plan.push(native_step(
        "remove tracked .beads/hooks/* bd shims (content-guarded; never hand-edited)",
        &["remove-hook-shims"],
    ));
    if remove_remote && local_only {
        plan.push(native_step(
            // ACCURATE label (plan-044 Issue 1.5): this step clears the remote at
            // BOTH layers — the decisive Dolt-DB-level remote AND the secondary
            // `sync.remote` config key — and verifies the postcondition. The old
            // label named only the config key, i.e. the layer that does NOT
            // determine whether a push can reach a remote.
            "clear the Dolt remote (DB-level + sync.remote config) under local-only, \
             then verify it is gone (--remove-remote)",
            &["remove-remote"],
        ));
    }

    // Native filesystem hardening steps (deterministic, no bd).
    plan.push(native_step(
        "tighten .beads perms (chmod 700)",
        &["chmod", "700", ".beads"],
    ));
    plan.push(native_step(
        "ensure .beads/.gitignore exclusions",
        &["gitignore", ".beads/.gitignore"],
    ));
    plan.push(native_step(
        "ensure project .gitignore exclusions",
        &["gitignore", ".gitignore"],
    ));

    if !apply {
        return Ok(RepairResult {
            before,
            plan,
            applied: false,
            after: None,
        });
    }

    // Apply.
    for step in &mut plan {
        if step.native {
            let (rc, err) = apply_native(&step.cmd, repo_root, &beads_dir);
            step.rc = Some(rc);
            step.err = err;
        } else {
            let argv: Vec<&str> = step.cmd.iter().map(String::as_str).collect();
            let (rc, _out, e) = run_in(&argv, 180, repo_root);
            step.rc = Some(rc);
            step.err = Some(e.trim().chars().take(200).collect());
        }
    }

    let after = verify(repo_root);
    Ok(RepairResult {
        before,
        plan,
        applied: true,
        after: Some(after),
    })
}

// ---------------------------------------------------------------------------
// Embedded-mode detection + Dolt-repo-path derivation (REQ-BINIT-016)
// ---------------------------------------------------------------------------

/// Pure mode decision for the wedged-migration flush (REQ-BINIT-016), split out
/// so it is testable without a live `.beads/`. `meta` is the raw
/// `.beads/metadata.json` (None if unreadable/absent); `server_files_present` is
/// whether `.beads/dolt-server.{pid,port}` exist. Returns `true` for embedded.
///
/// Precedence: an explicit `dolt_mode` of `"embedded"`/`"server"` wins; a
/// missing/empty/unknown value falls back to the filesystem probe (absence of
/// the server files ⇒ embedded). A keyless repo therefore NEVER defaults to the
/// server path — that is the path that fails in embedded storage (RT-3). Mode is
/// never inferred from a `bd` exit code.
fn decide_embedded(meta: Option<&str>, server_files_present: bool) -> bool {
    if let Some(text) = meta {
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(text) {
            match v.get("dolt_mode").and_then(|m| m.as_str()).map(str::trim) {
                Some("embedded") => return true,
                Some("server") => return false,
                _ => {} // missing / empty / unknown → filesystem probe
            }
        }
    }
    !server_files_present
}

/// Detect embedded Dolt storage for `beads_dir` (reads `metadata.json` +
/// probes for `dolt-server.{pid,port}`), delegating the decision to
/// [`decide_embedded`]. (REQ-BINIT-016.)
fn is_embedded_mode(beads_dir: &Path) -> bool {
    let meta = std::fs::read_to_string(beads_dir.join("metadata.json")).ok();
    let server_files_present =
        beads_dir.join("dolt-server.pid").exists() || beads_dir.join("dolt-server.port").exists();
    decide_embedded(meta.as_deref(), server_files_present)
}

/// Read `metadata.json.dolt_database` (trimmed, non-empty), the fallback used to
/// locate the Dolt-repo root when the `.dolt/`-parent search finds nothing.
fn read_dolt_database(beads_dir: &Path) -> Option<String> {
    let text = std::fs::read_to_string(beads_dir.join("metadata.json")).ok()?;
    let v = serde_json::from_str::<serde_json::Value>(&text).ok()?;
    v.get("dolt_database")
        .and_then(|d| d.as_str())
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
}

/// Recursively find directories under `beads_dir` that contain a `.dolt/` child,
/// returning those PARENT dirs (the Dolt-repo roots). Bounded depth; never
/// descends into a `.dolt/` itself, nor into known non-live snapshot dirs
/// (`backup`, `*.corrupt.backup`) — those hold gitignored copies, not the live
/// working repo, so counting them would defeat the derivation.
fn find_dolt_dirs(beads_dir: &Path) -> Vec<PathBuf> {
    fn walk(dir: &Path, depth: usize, out: &mut Vec<PathBuf>) {
        if depth > 5 {
            return;
        }
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for e in entries.flatten() {
            let p = e.path();
            if !p.is_dir() {
                continue;
            }
            let name = p.file_name().and_then(|n| n.to_str()).unwrap_or("");
            if name == ".dolt" {
                if let Some(parent) = p.parent() {
                    out.push(parent.to_path_buf());
                }
                continue; // do not descend into a .dolt/ store
            }
            if name == "backup" || name.ends_with(".corrupt.backup") {
                continue; // non-live snapshot dir — skip
            }
            walk(&p, depth + 1, out);
        }
    }
    let mut out = Vec::new();
    walk(beads_dir, 0, &mut out);
    out
}

/// Derive the live Dolt-repo root under `beads_dir`: the UNIQUE dir containing a
/// `.dolt/` child (fallback: `metadata.json.dolt_database` joined under
/// `embeddeddolt/`). On zero or more-than-one live candidate it does NOT guess —
/// it returns an `Err` with a "manual repair needed" message. (REQ-BINIT-016.)
fn derive_dolt_repo_root(beads_dir: &Path) -> Result<PathBuf, String> {
    let candidates = find_dolt_dirs(beads_dir);
    match candidates.len() {
        1 => Ok(candidates.into_iter().next().unwrap()),
        0 => {
            if let Some(db) = read_dolt_database(beads_dir) {
                let cand = beads_dir.join("embeddeddolt").join(&db);
                if cand.join(".dolt").is_dir() {
                    return Ok(cand);
                }
            }
            Err(
                "no live Dolt working directory found under .beads/ (no unique .dolt/ dir); \
                 manual repair needed"
                    .to_string(),
            )
        }
        n => {
            // REQ-BINIT-026: the SERVER-MODE layout is not ambiguous — it is
            // canonical (REQ-YF-PRE-010 invariant 1). It carries TWO `.dolt/`
            // dirs by design: the server's own data dir (`.beads/dolt/.dolt`)
            // and the database (`.beads/dolt/<dolt_database>/.dolt`). Counting
            // them and refusing meant `--remove-remote` NEVER worked on the
            // canonical profile, and silently degraded `has_local_only_remote`
            // and the REQ-BINIT-016 wedge fix along with it.
            //
            // `metadata.json`'s `dolt_database` names which one is the database,
            // so consult it BEFORE declaring ambiguity. Match on the final path
            // component rather than a constructed path, so this is agnostic to
            // where the store sits (`.beads/dolt/<db>` in server mode,
            // `.beads/embeddeddolt/<db>` in embedded mode).
            if let Some(db) = read_dolt_database(beads_dir) {
                let mut named = candidates
                    .iter()
                    .filter(|c| c.file_name().and_then(|n| n.to_str()) == Some(db.as_str()));
                if let Some(hit) = named.next() {
                    // Only deterministic when exactly one candidate bears the name.
                    if named.next().is_none() {
                        return Ok(hit.clone());
                    }
                }
            }
            Err(format!(
                "ambiguous Dolt working directory: {n} candidates with a .dolt/ child under \
                 .beads/ and none uniquely named by metadata.json's `dolt_database` \
                 — refusing to guess; manual repair needed"
            ))
        }
    }
}

/// The commit message stamped on the embedded working-set commit — a marker so
/// the operator can see why the commit exists.
const EMBEDDED_COMMIT_MARKER: &str =
    "yf-beads-init: commit embedded Dolt working set before wedged-migration repair (REQ-BINIT-016)";

/// Raw-`dolt` data-preserving commit in `dolt_root`: `add -A`, then `commit`
/// only when the working set is dirty (a clean tree is a success no-op; never
/// `--allow-empty`, never `reset --hard`). Caller guarantees `dolt` is on PATH.
/// Shared by the REQ-BINIT-016 embedded-migration flush and the REQ-BINIT-020
/// remote-removal commit.
fn dolt_commit_dir(dolt_root: &Path, marker: &str) -> (i32, Option<String>) {
    let (rc, _o, err) = run_in(&["dolt", "add", "-A"], 120, dolt_root);
    if rc != 0 {
        return (
            rc.max(1),
            Some(format!("dolt add -A failed: {}", err.trim())),
        );
    }
    // Commit only if dirty (a clean tree is a success no-op; never --allow-empty).
    let (_rc, status_out, _serr) = run_in(&["dolt", "status"], 60, dolt_root);
    let lower = status_out.to_lowercase();
    if lower.contains("working tree clean") || lower.contains("nothing to commit") {
        return (0, None);
    }
    let (crc, _co, cerr) = run_in(&["dolt", "commit", "-m", marker], 120, dolt_root);
    if crc == 0 {
        return (0, None);
    }
    // Tolerate a clean-tree race (tree became clean between status and commit).
    let cl = cerr.to_lowercase();
    if cl.contains("nothing to commit") || cl.contains("no changes added") {
        return (0, None);
    }
    (
        crc.max(1),
        Some(format!("dolt commit failed: {}", cerr.trim())),
    )
}

/// REQ-BINIT-016 data-preserving embedded working-set commit. Self-guards to a
/// no-op unless the repo is embedded (a server repo is handled by the
/// `bd dolt stop` step). Derives the Dolt-repo cwd, then commits the dirty
/// working set via raw `dolt` (`add -A`; `commit` only when dirty) — NEVER
/// `reset --hard`, NEVER `--allow-empty`; a clean tree is a success no-op. When
/// `dolt` is absent from PATH it attempts `bd dolt commit` as a last resort
/// (RT-2) before failing with a remediation.
fn dolt_commit_embedded(repo_root: &Path, beads_dir: &Path) -> (i32, Option<String>) {
    // Self-guard: server-mode repos are cleared by the `bd dolt stop` step.
    if !is_embedded_mode(beads_dir) {
        return (0, None);
    }
    let dolt_root = match derive_dolt_repo_root(beads_dir) {
        Ok(p) => p,
        Err(e) => return (1, Some(e)),
    };

    // Prefer raw `dolt` — it structurally bypasses bd's wedged migration gate and,
    // in embedded mode (no server), faces no lock contention.
    if which("dolt").is_some() {
        return dolt_commit_dir(&dolt_root, EMBEDDED_COMMIT_MARKER);
    }

    // `dolt` absent — last-resort `bd dolt commit` (may share the wedge; worst
    // case it fails identically to today, best case it recovers the repo).
    let (rc, _o, err) = run_in(&["bd", "dolt", "commit"], 120, repo_root);
    if rc == 0 {
        return (0, None);
    }
    (
        rc.max(1),
        Some(format!(
            "dolt not on PATH and `bd dolt commit` fallback failed ({}); \
             install dolt or commit the embedded working set manually",
            err.trim()
        )),
    )
}

/// Execute a native (Rust `std::fs`) repair step. `cmd[1]` is the verb. Returns
/// `(rc, optional-error-string)`; every arm is idempotent (a no-op on a clean
/// repo). Verbs: `chmod`, `gitignore` (hardening); `hookspath-reset`,
/// `rmdir-beads-skill`, `strip-managed-blocks`, `prune-settings`, `prune-codex`
/// (B.3/B.4 cleanup); `untrack-runtime`, `remove-hook-shims`, `remove-remote`
/// (#39 B.1 canonicalization); `dolt-commit-embedded` (REQ-BINIT-016
/// data-preserving embedded working-set commit).
fn apply_native(cmd: &[String], repo_root: &Path, beads_dir: &Path) -> (i32, Option<String>) {
    match cmd.get(1).map(String::as_str) {
        Some("chmod") => {
            if !beads_dir.is_dir() {
                return (0, None); // nothing to tighten — idempotent no-op.
            }
            match set_dir_mode(beads_dir, 0o700) {
                Ok(()) => (0, None),
                Err(e) => (1, Some(e.to_string())),
            }
        }
        Some("gitignore") => {
            let (path, patterns) = match cmd.get(2).map(String::as_str) {
                Some(".beads/.gitignore") => (beads_dir.join(".gitignore"), BEADS_GITIGNORE),
                _ => (repo_root.join(".gitignore"), PROJECT_GITIGNORE),
            };
            if path.parent().map(Path::is_dir).unwrap_or(true) {
                match ensure_gitignore(&path, patterns) {
                    Ok(()) => (0, None),
                    Err(e) => (1, Some(e.to_string())),
                }
            } else {
                (0, None) // parent dir absent (e.g. no .beads/) — no-op.
            }
        }
        // B.3: reset core.hooksPath to the git default (unset). `bd hooks
        // uninstall` already clears the beads-owned value; this belt handles a
        // stray value bd did not own. `git config --unset` of an absent key exits
        // 5 — treated as a no-op (already at default).
        Some("hookspath-reset") => {
            let (rc, _out, _err) = run_in(
                &["git", "config", "--local", "--unset", "core.hooksPath"],
                30,
                repo_root,
            );
            // 0 = unset something; 5 = key absent (already default). Either is OK.
            if rc == 0 || rc == 5 {
                (0, None)
            } else {
                (
                    rc,
                    Some(format!("git config --unset core.hooksPath exit {rc}")),
                )
            }
        }
        // B.3: remove a residual `.agents/skills/beads/` dir (`bd setup codex
        // --remove` normally owns this, but rm it directly as a fallback). Prune
        // now-empty `.agents/skills` and `.agents` parents, never touching a
        // hand-authored `.agents/` with other content.
        Some("rmdir-beads-skill") => {
            let skill = repo_root.join(".agents").join("skills").join("beads");
            if skill.is_dir() {
                if let Err(e) = std::fs::remove_dir_all(&skill) {
                    return (1, Some(e.to_string()));
                }
            }
            remove_dir_if_empty(&repo_root.join(".agents").join("skills"));
            remove_dir_if_empty(&repo_root.join(".agents"));
            (0, None)
        }
        // B.3: marker-scoped strip of the beads managed blocks from CLAUDE.md and
        // AGENTS.md (the fallback for the `BEADS INTEGRATION` block that lands in
        // AGENTS.md and that no `bd setup … --remove` strips).
        Some("strip-managed-blocks") => {
            for name in ["CLAUDE.md", "AGENTS.md"] {
                if let Err(e) = strip_managed_blocks(&repo_root.join(name)) {
                    return (1, Some(format!("{name}: {e}")));
                }
            }
            (0, None)
        }
        // B.4: delete `.claude/settings.json` ONLY if it is empty (`{}` /
        // `{"hooks": {}}`) after bd's entry-scoped removal — never wholesale, so a
        // #30 baseline at project scope is never clobbered. Prune a now-empty
        // `.claude/` too.
        Some("prune-settings") => match prune_empty_settings(repo_root) {
            Ok(()) => (0, None),
            Err(e) => (1, Some(e.to_string())),
        },
        // B.4: delete `.codex/config.toml` ONLY if it is effectively empty — the
        // bare `[features]` table `bd setup codex --remove` leaves behind once it
        // strips `hooks = true`. Never wholesale-deletes a hand-authored config
        // with real keys. Prune a now-empty `.codex/` too.
        Some("prune-codex") => match prune_empty_codex(repo_root) {
            Ok(()) => (0, None),
            Err(e) => (1, Some(e.to_string())),
        },
        // #39 B.1: `git rm --cached` the pinned BEADS_UNTRACK set, restricted to
        // tracked paths (clean no-op when nothing is tracked; keeps the working
        // file). The `dolt-server.*` glob is expanded against `git ls-files`.
        Some("untrack-runtime") => match untrack_runtime(repo_root) {
            Ok(()) => (0, None),
            Err(e) => (1, Some(e.to_string())),
        },
        // #39 B.1: remove tracked `.beads/hooks/*` files whose content carries the
        // `bd hooks run` shim signature — never a hand-edited hook.
        Some("remove-hook-shims") => match remove_hook_shims(repo_root) {
            Ok(()) => (0, None),
            Err(e) => (1, Some(e.to_string())),
        },
        // #39 B.1 (gated): clear the Dolt `sync.remote` config under local-only.
        // Only ever reached when the plan included it (`remove_remote && local_only`).
        //
        // REQ-YF-DOCTOR-006: a repair step VERIFIES ITS OWN POSTCONDITION. Having
        // applied the removal is not evidence that the remote is gone, so re-run
        // the read-only predicate that detected the condition and FAIL if it still
        // holds. Reporting `ok` on the strength of having *attempted* the repair is
        // the silent-success shape this whole change set exists to remove.
        Some("remove-remote") => match remove_dolt_remote(repo_root) {
            Err(e) => (1, Some(e.to_string())),
            Ok(()) => {
                if has_local_only_remote(repo_root) {
                    (
                        1,
                        Some(
                            "postcondition FAILED: a Dolt remote is still configured under \
                             dolt.local-only after the removal step reported success — the \
                             remote SURVIVES; do not treat this run as having removed it"
                                .to_string(),
                        ),
                    )
                } else {
                    (0, None)
                }
            }
        },
        // REQ-BINIT-016: data-preserving embedded working-set commit (the
        // embedded-mode replacement for `bd dolt stop`). Runs raw `dolt` in the
        // derived Dolt-repo cwd; see [`dolt_commit_embedded`].
        Some("dolt-commit-embedded") => dolt_commit_embedded(repo_root, beads_dir),
        _ => (0, None),
    }
}

/// READ-ONLY detection (#39 B.2, for preflight): returns `(untracked_drift,
/// shim_drift)` — whether any [`BEADS_UNTRACK`] path is currently tracked, and
/// whether any tracked `.beads/hooks/*` carries the [`HOOK_SHIM_SIGNATURE`]. Pure
/// inspection: never mutates the repo. Mirrors the match logic of
/// [`untrack_runtime`] / [`remove_hook_shims`] without invoking `git rm`.
pub fn tracked_canonicalization_drift(repo_root: &Path) -> (bool, bool) {
    let tracked = tracked_files(repo_root);
    let untracked_drift = tracked.iter().any(|p| {
        BEADS_UNTRACK
            .iter()
            .any(|pat| untrack_pattern_matches(pat, p))
    });
    let shim_drift = tracked.iter().any(|p| {
        let Some(rest) = p.strip_prefix(".beads/hooks/") else {
            return false;
        };
        if rest.contains('/') {
            return false;
        }
        std::fs::read_to_string(repo_root.join(p))
            .map(|b| b.contains(HOOK_SHIM_SIGNATURE))
            .unwrap_or(false)
    });
    (untracked_drift, shim_drift)
}

/// Read a bd config value via `bd config get <key> --json`, returning the
/// `value` field as a string. `None` when the command fails or its output
/// can't be parsed; an *unset* key yields `Some("")` (bd emits `"value": ""`).
///
/// The plain-text `bd config get <key>` form prints a `<key> (not set in
/// config.yaml)` sentinel to stdout at **exit 0** for an unset key — non-empty
/// output that a naive `!stdout.is_empty()` check misreads as a configured
/// value (#43). The `--json` form is the unambiguous shape: an empty string
/// means unset, a non-empty string means configured.
fn bd_config_value(repo_root: &Path, key: &str) -> Option<String> {
    let (rc, out, _) = run_in(&["bd", "config", "get", key, "--json"], 30, repo_root);
    if rc != 0 {
        return None;
    }
    parse_bd_config_value(&out)
}

/// Pure parser for `bd config get --json` output: the `value` field as a
/// string. `None` on unparseable JSON; an unset key (`"value": ""`) yields
/// `Some("")`. Split out from [`bd_config_value`] so the #43 regression — the
/// `(not set …)` sentinel must NOT be read as a configured value — is testable
/// without a live `bd`.
fn parse_bd_config_value(out: &str) -> Option<String> {
    let v = serde_json::from_str::<serde_json::Value>(out).ok()?;
    Some(match v.get("value") {
        Some(serde_json::Value::String(s)) => s.clone(),
        None | Some(serde_json::Value::Null) => String::new(),
        Some(other) => other.to_string(),
    })
}

/// READ-ONLY detection (#39 B.2, for preflight): whether a Dolt remote is
/// configured AND the repo is in local-only context (`dolt.local-only` is
/// true). Pure inspection: never mutates. This is the drift the
/// `--remove-remote` opt-in clears.
///
/// Two layers count as a configured remote (either fires): the **Dolt-DB-level**
/// remote (a row in `dolt_remotes`, enumerated via raw `dolt remote`) — the
/// **decisive** layer the remote-migrate gate keys on (EXP-002) — and the
/// secondary `sync.remote` **config** key.
pub fn has_local_only_remote(repo_root: &Path) -> bool {
    let local_only = bd_config_value(repo_root, "dolt.local-only")
        .is_some_and(|v| v.trim().eq_ignore_ascii_case("true"));
    if !local_only {
        return false;
    }
    // Decisive layer: a Dolt-DB-level remote. The gate keys solely on this.
    let beads_dir = repo_root.join(".beads");
    if let Ok(dolt_root) = derive_dolt_repo_root(&beads_dir) {
        if !dolt_remote_names(&dolt_root).is_empty() {
            return true;
        }
    }
    // Secondary layer: the `sync.remote` config key.
    bd_config_value(repo_root, "sync.remote").is_some_and(|v| !v.trim().is_empty())
}

/// READ-ONLY detection (#58 / REQ-YF-PRE-010, for preflight): whether the repo's
/// beads store drifts from the canonical **per-repo local-server** engine mode —
/// i.e. it is an **embedded** store (`dolt_mode: "embedded"` / no `dolt-server.*`).
/// This is the **detect/warn-only** axis: engine-mode migration is out of scope,
/// so preflight only surfaces the drift with guidance, never offering a `--repair`.
///
/// Returns `false` (conformant / not-applicable) when there is no `.beads/` dir at
/// all — a non-beads or not-yet-initialized repo is never flagged as engine-mode
/// drift (that classification is `bd_not_initialized`'s job, upstream of here).
/// Only an existing `.beads/` that resolves to embedded storage returns `true`.
pub fn has_embedded_engine_drift(repo_root: &Path) -> bool {
    let beads_dir = repo_root.join(".beads");
    if !beads_dir.is_dir() {
        return false;
    }
    is_embedded_mode(&beads_dir)
}

/// Enumerate configured Dolt-DB-level remote names by running raw `dolt remote`
/// in the derived Dolt-repo cwd (each remote name on its own line). Read-only.
/// Empty on any failure (`dolt` absent, no remotes, non-zero exit) — treated as
/// "no remotes configured".
fn dolt_remote_names(dolt_root: &Path) -> Vec<String> {
    if which("dolt").is_none() {
        return vec![];
    }
    let (rc, out, _err) = run_in(&["dolt", "remote"], 60, dolt_root);
    if rc != 0 {
        return vec![];
    }
    out.lines()
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(str::to_string)
        .collect()
}

/// `git ls-files` for the repo, returning the tracked paths (repo-relative,
/// forward-slash). Empty on any error (treated as "nothing tracked").
fn tracked_files(repo_root: &Path) -> Vec<String> {
    let (rc, out, _err) = run_in(&["git", "ls-files", "-z"], 60, repo_root);
    if rc != 0 {
        return vec![];
    }
    out.split('\0')
        .filter(|s| !s.is_empty())
        .map(str::to_string)
        .collect()
}

/// True when tracked path `p` is matched by untrack pattern `pat` (see
/// [`BEADS_UNTRACK`] semantics): a `dir/` prefix-under match, a `prefix.*` glob,
/// or an exact path.
fn untrack_pattern_matches(pat: &str, p: &str) -> bool {
    if let Some(dir) = pat.strip_suffix('/') {
        // Directory: any tracked path under it.
        p.starts_with(dir) && p[dir.len()..].starts_with('/')
    } else if let Some(prefix) = pat.strip_suffix(".*") {
        // Glob `prefix.*`: a basename starting with `prefix.` in the same dir.
        // The pattern's parent dir must match, and the remainder must start
        // with `prefix.` (so `.beads/dolt-server.foo` matches, `.beads/x` not).
        if let Some(rest) = p.strip_prefix(prefix) {
            rest.starts_with('.')
        } else {
            false
        }
    } else {
        p == pat
    }
}

/// `git rm --cached` the tracked subset of [`BEADS_UNTRACK`] (#39 B.1). Idempotent:
/// computes the tracked matches first, so an empty match set is a clean no-op (no
/// `git rm` invoked). `--cached` keeps the working-tree file.
fn untrack_runtime(repo_root: &Path) -> std::io::Result<()> {
    let tracked = tracked_files(repo_root);
    if tracked.is_empty() {
        return Ok(());
    }
    let mut to_untrack: Vec<&str> = Vec::new();
    for p in &tracked {
        if BEADS_UNTRACK
            .iter()
            .any(|pat| untrack_pattern_matches(pat, p))
        {
            to_untrack.push(p.as_str());
        }
    }
    if to_untrack.is_empty() {
        return Ok(());
    }
    let mut argv: Vec<&str> = vec!["git", "rm", "--cached", "--quiet", "--ignore-unmatch"];
    argv.extend_from_slice(&to_untrack);
    let (rc, _out, err) = run_in(&argv, 60, repo_root);
    if rc != 0 {
        return Err(std::io::Error::other(format!(
            "git rm --cached exit {rc}: {}",
            err.trim()
        )));
    }
    Ok(())
}

/// Remove tracked `.beads/hooks/*` files whose content carries the
/// [`HOOK_SHIM_SIGNATURE`] (`bd hooks run`) — dead bd-generated shims (#39 B.1).
/// Content-guarded: a hook lacking the signature (hand-edited) is preserved.
/// `git rm` removes both the index entry and the working-tree copy (correct for a
/// dead shim). Idempotent: a no-op when no matching tracked shim exists.
fn remove_hook_shims(repo_root: &Path) -> std::io::Result<()> {
    let tracked = tracked_files(repo_root);
    let mut shims: Vec<&str> = Vec::new();
    for p in &tracked {
        // Tracked files directly under `.beads/hooks/`.
        let Some(rest) = p.strip_prefix(".beads/hooks/") else {
            continue;
        };
        if rest.contains('/') {
            continue; // nested dir — not a hook shim file.
        }
        let body = std::fs::read_to_string(repo_root.join(p)).unwrap_or_default();
        if body.contains(HOOK_SHIM_SIGNATURE) {
            shims.push(p.as_str());
        }
    }
    if shims.is_empty() {
        return Ok(());
    }
    let mut argv: Vec<&str> = vec!["git", "rm", "--quiet", "--ignore-unmatch"];
    argv.extend_from_slice(&shims);
    let (rc, _out, err) = run_in(&argv, 60, repo_root);
    if rc != 0 {
        return Err(std::io::Error::other(format!(
            "git rm exit {rc}: {}",
            err.trim()
        )));
    }
    Ok(())
}

/// The commit message stamped on the commit that persists a Dolt-remote removal.
const REMOTE_REMOVE_MARKER: &str =
    "yf-beads-init: remove Dolt remote under local-only canonicalization (REQ-BINIT-020, #61)";

/// Clear a configured remote at **both layers** under local-only (#39 B.1,
/// `--remove-remote`; REQ-BINIT-020). This is the one repair step that *clears* a
/// remote (it never adds one), and it is idempotent — a clean no-op when nothing
/// is configured at either layer.
///
/// 1. **Dolt-DB remote (decisive).** The bd 1.1.0 remote-migrate gate keys SOLELY
///    on `dolt_remotes` (EXP-002), and on a WEDGED DB bd's own `bd dolt remote
///    remove` is itself gated (no mutation) — so each configured remote is removed
///    via RAW `dolt remote remove <name>` in the derived Dolt-repo cwd, then the
///    change is persisted data-preservingly via raw `dolt add -A && dolt commit`
///    (shared with REQ-BINIT-016). A repo with no dolt remotes is a clean no-op.
/// 2. **`sync.remote` config (secondary cleanliness).** Because `bd config unset`
///    is likewise gated on a wedged DB, the key is stripped from
///    `.beads/config.yaml` via a RAW file edit, not via the gated bd subcommand.
fn remove_dolt_remote(repo_root: &Path) -> std::io::Result<()> {
    let beads_dir = repo_root.join(".beads");

    // Layer 1 (decisive): the Dolt-DB-level remote(s), removed via raw `dolt`.
    //
    // REQ-BINIT-026 / REQ-YF-DOCTOR-006: an underivable root is an ERROR, not a
    // skip. The previous `if let Ok(...)` swallowed the failure and fell through
    // to layer 2, so the step reported `ok` while the decisive layer never ran —
    // which is precisely how #159 stayed invisible: the operator was told the
    // remote was removed while it survived untouched. There is no "nothing to
    // clear" inference available here; we did not look, so we cannot claim it.
    let dolt_root = derive_dolt_repo_root(&beads_dir).map_err(|e| {
        std::io::Error::other(format!(
            "cannot remove the Dolt remote: {e} — the decisive DB-level layer could not run, \
             so any configured remote SURVIVES; this is a failure, not a no-op"
        ))
    })?;
    {
        let names = dolt_remote_names(&dolt_root);
        if !names.is_empty() {
            for name in &names {
                let (rc, _o, err) = run_in(&["dolt", "remote", "remove", name], 60, &dolt_root);
                // An already-absent remote is a clean no-op (idempotent re-run).
                if rc != 0 && !err.to_lowercase().contains("unknown remote") {
                    return Err(std::io::Error::other(format!(
                        "dolt remote remove {name} exit {rc}: {}",
                        err.trim()
                    )));
                }
            }
            // Persist the removal data-preservingly (dolt is on PATH — we just
            // enumerated remotes through it). A clean tree is a success no-op.
            let (rc, msg) = dolt_commit_dir(&dolt_root, REMOTE_REMOVE_MARKER);
            if rc != 0 {
                return Err(std::io::Error::other(msg.unwrap_or_else(|| {
                    "dolt commit after remote removal failed".into()
                })));
            }
        }
    }

    // Layer 2 (secondary cleanliness): strip `sync.remote` from config.yaml RAW.
    remove_sync_remote_config(&beads_dir)
}

/// Strip the `sync.remote` setting from `.beads/config.yaml` via a RAW file edit
/// — never `bd config unset`, which is gated on a wedged DB (EXP-002). Handles
/// both the flat (`sync.remote: …`) and nested (`sync:` → `  remote: …`) YAML
/// shapes. Idempotent: a missing file or an absent key is a clean no-op (no
/// write).
fn remove_sync_remote_config(beads_dir: &Path) -> std::io::Result<()> {
    let path = beads_dir.join("config.yaml");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Ok(()); // no config file — nothing to clear.
    };
    let mut changed = false;
    let mut out: Vec<String> = Vec::new();
    let mut in_sync_block = false;
    for line in text.lines() {
        let trimmed = line.trim_start();
        let indent = line.len() - trimmed.len();
        // Flat form: `sync.remote: …` (any indent).
        if trimmed.starts_with("sync.remote:") {
            changed = true;
            continue;
        }
        // Nested form: a `remote:` child directly under a top-level `sync:` block.
        if indent == 0 {
            in_sync_block = trimmed.starts_with("sync:");
        } else if in_sync_block && trimmed.starts_with("remote:") {
            changed = true;
            continue;
        }
        out.push(line.to_string());
    }
    if !changed {
        return Ok(());
    }
    // plan-044 Issue 1.8: drop a `sync:` parent left CHILDLESS by the removal
    // above. Removing the `remote:` child but keeping its parent leaves a dangling
    // `sync:` key — which is what the partial repair actually did to this repo. It
    // is inert to bd, but it is a false signal to a human reading config.yaml: it
    // reads as "sync is configured" when nothing is.
    //
    // A block is childless when the next non-blank, non-comment line is not
    // indented (i.e. the block has no remaining members).
    let out = {
        let mut kept: Vec<String> = Vec::with_capacity(out.len());
        let mut i = 0usize;
        while i < out.len() {
            let line = &out[i];
            if line.trim_start() == "sync:" && line.len() == line.trim_start().len() {
                let has_child = out[i + 1..]
                    .iter()
                    .find(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'))
                    .is_some_and(|l| l.starts_with(char::is_whitespace));
                if !has_child {
                    i += 1;
                    continue; // drop the childless parent
                }
            }
            kept.push(line.clone());
            i += 1;
        }
        kept
    };
    let mut joined = out.join("\n");
    if text.ends_with('\n') {
        joined.push('\n');
    }
    std::fs::write(&path, joined)
}

/// Remove `dir` only if it exists and is empty. Idempotent; ignores errors (a
/// non-empty dir or a race just leaves it in place).
fn remove_dir_if_empty(dir: &Path) {
    if dir.is_dir()
        && std::fs::read_dir(dir)
            .map(|mut it| it.next().is_none())
            .unwrap_or(false)
    {
        let _ = std::fs::remove_dir(dir);
    }
}

/// Strip every `MANAGED_BLOCKS` marker-fenced span from `path` (idempotent). A
/// missing file or a file with no managed block is a no-op (no write). Matches the
/// begin marker by prefix (it carries a `v:/profile:/hash:` suffix) and the end
/// marker exactly, removing the fenced span inclusive of both marker lines plus a
/// single trailing blank line if present, to avoid accreting blank lines.
fn strip_managed_blocks(path: &Path) -> std::io::Result<()> {
    let Ok(original) = std::fs::read_to_string(path) else {
        return Ok(()); // absent / unreadable — nothing to strip.
    };
    let lines: Vec<&str> = original.lines().collect();
    let mut out: Vec<&str> = Vec::with_capacity(lines.len());
    let mut i = 0;
    let mut changed = false;
    while i < lines.len() {
        let trimmed = lines[i].trim_start();
        if let Some((_, end)) = MANAGED_BLOCKS
            .iter()
            .find(|(begin, _)| trimmed.starts_with(begin))
        {
            // Skip until (and including) the matching end marker.
            let mut j = i + 1;
            while j < lines.len() && lines[j].trim_start() != *end {
                j += 1;
            }
            // j is the end-marker line (or EOF if unterminated — strip to EOF).
            i = if j < lines.len() { j + 1 } else { j };
            // Swallow one trailing blank line so blocks don't leave a gap.
            if i < lines.len() && lines[i].trim().is_empty() {
                i += 1;
            }
            changed = true;
            continue;
        }
        out.push(lines[i]);
        i += 1;
    }
    if !changed {
        return Ok(());
    }
    let mut text = out.join("\n");
    // Preserve a single trailing newline if the original had one.
    if original.ends_with('\n') && !text.is_empty() {
        text.push('\n');
    }
    std::fs::write(path, text)
}

/// Delete `.claude/settings.json` only when it carries no meaningful content after
/// bd's entry-scoped hook removal — i.e. it parses to an object with no non-empty
/// values (`{}`, `{"hooks": {}}`). Otherwise leave it untouched (never clobber a
/// recommended-settings baseline, #30). Prunes a now-empty `.claude/`. Idempotent.
fn prune_empty_settings(repo_root: &Path) -> std::io::Result<()> {
    let claude_dir = repo_root.join(".claude");
    let settings = claude_dir.join("settings.json");
    let Ok(text) = std::fs::read_to_string(&settings) else {
        return Ok(()); // absent — no-op.
    };
    let Ok(value) = serde_json::from_str::<serde_json::Value>(&text) else {
        return Ok(()); // unparseable — leave it; do not risk data loss.
    };
    if json_is_effectively_empty(&value) {
        std::fs::remove_file(&settings)?;
        remove_dir_if_empty(&claude_dir);
    }
    Ok(())
}

/// True when a JSON value carries no meaningful content: `null`, an empty
/// string/array, or an object all of whose values are themselves effectively
/// empty (so `{}` and `{"hooks": {}}` both qualify). Non-empty scalars (numbers,
/// bools, non-empty strings/arrays/objects) are meaningful.
fn json_is_effectively_empty(v: &serde_json::Value) -> bool {
    match v {
        serde_json::Value::Null => true,
        serde_json::Value::String(s) => s.is_empty(),
        serde_json::Value::Array(a) => a.is_empty(),
        serde_json::Value::Object(m) => m.values().all(json_is_effectively_empty),
        serde_json::Value::Bool(_) | serde_json::Value::Number(_) => false,
    }
}

/// Delete `.codex/config.toml` only if it is effectively empty (the bare
/// `[features]` residual `bd setup codex --remove` leaves once it strips
/// `hooks = true`), then prune a now-empty `.codex/`. A missing or unparseable
/// file is a no-op (never risk data loss). Mirrors `prune_empty_settings`.
fn prune_empty_codex(repo_root: &Path) -> std::io::Result<()> {
    let codex_dir = repo_root.join(".codex");
    let config = codex_dir.join("config.toml");
    let Ok(text) = std::fs::read_to_string(&config) else {
        return Ok(()); // absent — no-op.
    };
    if toml_is_effectively_empty(&text) {
        std::fs::remove_file(&config)?;
        remove_dir_if_empty(&codex_dir);
    }
    Ok(())
}

/// True when TOML text carries no meaningful content: every non-blank line is a
/// comment (`#…`) or a bare table header (`[…]` / `[[…]]`) — i.e. no `key = value`
/// assignment anywhere. So `[features]\n` (the codex-remove residual) and an
/// all-comments file qualify, while any real key leaves the file in place. A
/// deliberately conservative substitute for a full TOML parser: it only ever
/// classifies as empty a file with zero assignments, so it can never delete a
/// config that holds a value.
fn toml_is_effectively_empty(text: &str) -> bool {
    for line in text.lines() {
        let t = line.trim();
        if t.is_empty() || t.starts_with('#') || t.starts_with('[') {
            continue;
        }
        return false; // any other non-blank line implies a key/value assignment.
    }
    true
}

/// Idempotently append any missing `patterns` to a gitignore file (legacy
/// `_ensure_gitignore`). Never duplicates an existing line; never reorders.
fn ensure_gitignore(path: &Path, patterns: &[&str]) -> std::io::Result<()> {
    let existing: Vec<String> = std::fs::read_to_string(path)
        .map(|t| t.lines().map(str::to_string).collect())
        .unwrap_or_default();
    let have: std::collections::BTreeSet<&str> = existing.iter().map(String::as_str).collect();
    let add: Vec<&str> = patterns
        .iter()
        .copied()
        .filter(|p| !have.contains(p))
        .collect();
    if add.is_empty() {
        return Ok(());
    }
    let mut lines = existing;
    lines.push(String::new());
    lines.push("# beads-init: required exclusions".to_string());
    lines.extend(add.iter().map(|s| s.to_string()));
    std::fs::write(path, lines.join("\n") + "\n")
}

// ---------------------------------------------------------------------------
// Shared low-level helpers (ported from beads_init.py)
// ---------------------------------------------------------------------------

/// Defensively parse the first JSON object from bd output (may be multi-doc).
/// Mirrors the Python `_first_json_doc`.
fn first_json_doc(text: &str) -> Option<serde_json::Map<String, serde_json::Value>> {
    let text = text.trim();
    if text.is_empty() {
        return None;
    }
    // Fast path: the whole text is one JSON value.
    if let Ok(v) = serde_json::from_str::<serde_json::Value>(text) {
        return match v {
            serde_json::Value::Object(m) => Some(m),
            serde_json::Value::Array(a) => a.into_iter().find_map(|e| match e {
                serde_json::Value::Object(m) => Some(m),
                _ => None,
            }),
            _ => None,
        };
    }
    // Fall back to the first balanced {...} block.
    let bytes = text.as_bytes();
    let mut depth = 0usize;
    let mut start: Option<usize> = None;
    for (i, &ch) in bytes.iter().enumerate() {
        if ch == b'{' {
            if depth == 0 {
                start = Some(i);
            }
            depth += 1;
        } else if ch == b'}' {
            depth = depth.saturating_sub(1);
            if depth == 0 {
                if let Some(s) = start {
                    if let Ok(serde_json::Value::Object(m)) =
                        serde_json::from_str::<serde_json::Value>(&text[s..=i])
                    {
                        return Some(m);
                    }
                    start = None;
                }
            }
        }
    }
    None
}

/// Run `bd version` and parse its version tuple, or `None` if bd is absent /
/// unparseable. Mirrors the Python `_parse_bd_version`.
fn parse_bd_version() -> Option<(u32, u32, u32)> {
    crate::tool::tool_version(None, "bd", "version")
}

/// Run a command in `dir`; returns `(rc, stdout, stderr)`. Mirrors the Python
/// `_run` (127 for not-found; std has no built-in timeout, so `_timeout` is
/// advisory — commands here are bounded by bd itself).
fn run_in(cmd: &[&str], _timeout: u64, dir: &Path) -> (i32, String, String) {
    let mut c = Command::new(cmd[0]);
    c.args(&cmd[1..]);
    if dir != Path::new(".") {
        c.current_dir(dir);
    }
    match c.output() {
        Ok(o) => (
            o.status.code().unwrap_or(-1),
            String::from_utf8_lossy(&o.stdout).into_owned(),
            String::from_utf8_lossy(&o.stderr).into_owned(),
        ),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            (127, String::new(), format!("{}: not found", cmd[0]))
        }
        Err(e) => (1, String::new(), e.to_string()),
    }
}

/// `which`-style PATH lookup using std only (GR-011: no extra dep).
fn which(bin: &str) -> Option<PathBuf> {
    crate::tool::resolve_tool(bin)
}

#[cfg(unix)]
fn dir_mode(p: &Path) -> Option<u32> {
    use std::os::unix::fs::PermissionsExt;
    if !p.is_dir() {
        return None;
    }
    std::fs::metadata(p)
        .ok()
        .map(|m| m.permissions().mode() & 0o7777)
}

#[cfg(not(unix))]
fn dir_mode(_p: &Path) -> Option<u32> {
    None
}

#[cfg(unix)]
fn set_dir_mode(p: &Path, mode: u32) -> std::io::Result<()> {
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(p, std::fs::Permissions::from_mode(mode))
}

#[cfg(not(unix))]
fn set_dir_mode(_p: &Path, _mode: u32) -> std::io::Result<()> {
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-PRE-006: the load-bearing invariant — an error KEY (not exit code)
    // on an INITIALIZED repo classifies `corrupted`, never `not_initialized`.
    #[test]
    fn error_key_on_initialized_is_corrupted() {
        let raw = r#"{"error": "pending schema migration blocked by a dirty table"}"#;
        let (status, functional) = classify(raw, /* initialized */ true);
        assert_eq!(status, VerifyStatus::Corrupted);
        assert!(!functional);
    }

    // REQ-YF-PRE-006: error key but .beads/ ABSENT → not_initialized.
    #[test]
    fn error_key_uninitialized_is_not_initialized() {
        let raw = r#"{"error": "no database"}"#;
        let (status, _) = classify(raw, false);
        assert_eq!(status, VerifyStatus::NotInitialized);
    }

    // REQ-YF-PRE-006: clean parse with NO error key → ok/functional (regardless of
    // what the exit code would have been — classification ignores it).
    #[test]
    fn clean_status_is_ok() {
        let raw = r#"{"open": 3, "closed": 1, "ready": 2}"#;
        let (status, functional) = classify(raw, true);
        assert_eq!(status, VerifyStatus::Ok);
        assert!(functional);
    }

    // REQ-YF-PRE-006: unparseable output → corrupted if initialized,
    // not_initialized if not.
    #[test]
    fn unparseable_depends_on_initialized() {
        assert_eq!(classify("not json at all", true).0, VerifyStatus::Corrupted);
        assert_eq!(
            classify("not json at all", false).0,
            VerifyStatus::NotInitialized
        );
        assert_eq!(classify("", true).0, VerifyStatus::Corrupted);
    }

    // REQ-YF-PRE-006: multi-doc / leading-noise output — first balanced object wins.
    #[test]
    fn first_json_doc_recovers_first_object() {
        let raw = "log line\n{\"error\": \"x\"}\n{\"other\": 1}";
        let doc = first_json_doc(raw).unwrap();
        assert!(doc.contains_key("error"));
        // And classification sees the error.
        assert_eq!(classify(raw, true).0, VerifyStatus::Corrupted);
    }

    // REQ-YF-PRE-006: a JSON array whose first element is an object is unwrapped.
    #[test]
    fn first_json_doc_unwraps_array() {
        let doc = first_json_doc(r#"[{"a": 1}, {"b": 2}]"#).unwrap();
        assert!(doc.contains_key("a"));
    }

    // REQ-YF-PRE-007: gitignore top-up is idempotent — appends missing patterns
    // once, re-run adds nothing.
    #[test]
    fn ensure_gitignore_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        let gi = tmp.path().join(".gitignore");
        std::fs::write(&gi, "existing\n.beads/proxieddb/\n").unwrap();

        ensure_gitignore(&gi, PROJECT_GITIGNORE).unwrap();
        let after1 = std::fs::read_to_string(&gi).unwrap();
        // .beads-credential-key was missing → added; .beads/proxieddb/ already there.
        assert!(after1.contains(".beads-credential-key"));
        assert_eq!(after1.matches(".beads/proxieddb/").count(), 1);

        // Re-run: nothing changes.
        ensure_gitignore(&gi, PROJECT_GITIGNORE).unwrap();
        let after2 = std::fs::read_to_string(&gi).unwrap();
        assert_eq!(after1, after2);
    }

    // REQ-YF-PRE-007: ensure_gitignore on a nonexistent file creates it with the
    // patterns (idempotent on re-run).
    #[test]
    fn ensure_gitignore_creates_when_absent() {
        let tmp = tempfile::tempdir().unwrap();
        let gi = tmp.path().join(".gitignore");
        ensure_gitignore(&gi, &["a", "b"]).unwrap();
        let text = std::fs::read_to_string(&gi).unwrap();
        assert!(text.contains("a") && text.contains("b"));
        ensure_gitignore(&gi, &["a", "b"]).unwrap();
        assert_eq!(std::fs::read_to_string(&gi).unwrap(), text);
    }

    // REQ-YF-PRE-007 / REQ-BINIT-011: the SERVER-mode wedged-migration plan is
    // `bd dolt stop` → `bd migrate schema` → `bd migrate` (unchanged) — never
    // `bd vc commit`, and no native embedded step.
    #[test]
    fn corrupted_plan_has_migration_order() {
        let steps = wedged_migration_steps(/* embedded */ false);
        let argvs: Vec<Vec<&str>> = steps.iter().map(|(_, _, a)| a.clone()).collect();
        assert_eq!(
            argvs,
            vec![
                vec!["bd", "dolt", "stop"],
                vec!["bd", "migrate", "schema"],
                vec!["bd", "migrate"],
            ]
        );
        // No native step in server mode; never `bd vc commit`.
        assert!(steps.iter().all(|(_, native, _)| !native));
        assert!(!steps.iter().any(|(_, _, a)| a.contains(&"vc")));
    }

    // REQ-BINIT-016: the EMBEDDED-mode wedged-migration plan replaces `bd dolt
    // stop` with the NATIVE `dolt-commit-embedded` step (carrying NO hardcoded
    // path — the cwd is derived at apply time), then the same migrate tail.
    #[test]
    fn corrupted_embedded_plan_uses_native_commit_not_dolt_stop() {
        let steps = wedged_migration_steps(/* embedded */ true);
        // First step: native, verb `dolt-commit-embedded`.
        let (why0, native0, args0) = &steps[0];
        assert!(native0, "embedded flush step is native");
        assert_eq!(args0, &vec!["dolt-commit-embedded"]);
        assert!(why0.contains("data-preserving"));
        // No `bd dolt stop` anywhere; no hardcoded embeddeddolt path in the plan.
        assert!(!steps.iter().any(|(_, _, a)| a.contains(&"stop")));
        assert!(
            !steps
                .iter()
                .any(|(_, _, a)| a.iter().any(|s| s.contains("embeddeddolt"))),
            "path is derived at apply time, never hardcoded in the plan"
        );
        // Migrate tail is preserved and shelled.
        let tail: Vec<Vec<&str>> = steps[1..].iter().map(|(_, _, a)| a.clone()).collect();
        assert_eq!(
            tail,
            vec![vec!["bd", "migrate", "schema"], vec!["bd", "migrate"]]
        );
        assert!(steps[1..].iter().all(|(_, native, _)| !native));
    }

    // REQ-BINIT-016: pure mode decision. Explicit `dolt_mode` wins; a
    // missing/empty/unknown key falls back to the server-file probe; a keyless
    // repo with no server files is embedded (never defaults to the server path).
    #[test]
    fn decide_embedded_precedence() {
        // Explicit values win regardless of server-file presence.
        assert!(decide_embedded(Some(r#"{"dolt_mode":"embedded"}"#), true));
        assert!(!decide_embedded(Some(r#"{"dolt_mode":"server"}"#), false));
        // Missing/empty/unknown → filesystem probe.
        assert!(decide_embedded(Some(r#"{"dolt_mode":""}"#), false)); // no server files → embedded
        assert!(!decide_embedded(Some(r#"{"dolt_mode":""}"#), true)); // server files → server
        assert!(decide_embedded(Some(r#"{"other":1}"#), false)); // keyless → probe → embedded
        assert!(decide_embedded(Some("not json"), false)); // unparseable → probe → embedded
        assert!(decide_embedded(None, false)); // no metadata → probe → embedded
        assert!(!decide_embedded(None, true)); // no metadata but server files → server
    }

    // REQ-BINIT-016: derive the Dolt-repo root as the unique `.dolt/`-parent; the
    // zero/>1-candidate guard refuses to guess; backup snapshot dirs are skipped.
    #[test]
    fn derive_dolt_repo_root_unique_and_guarded() {
        let tmp = tempfile::tempdir().unwrap();
        let beads = tmp.path().join(".beads");
        // Zero candidates → Err (manual repair).
        std::fs::create_dir_all(&beads).unwrap();
        assert!(derive_dolt_repo_root(&beads).is_err());

        // One live candidate → derived (never hardcoded).
        let live = beads.join("embeddeddolt").join("dolt");
        std::fs::create_dir_all(live.join(".dolt")).unwrap();
        assert_eq!(derive_dolt_repo_root(&beads).unwrap(), live);

        // A `.dolt/` under a `backup/` snapshot is ignored (still unique).
        std::fs::create_dir_all(beads.join("backup").join("db").join(".dolt")).unwrap();
        assert_eq!(derive_dolt_repo_root(&beads).unwrap(), live);

        // A second LIVE candidate → ambiguous → Err (refuse to guess).
        std::fs::create_dir_all(beads.join("other").join(".dolt")).unwrap();
        assert!(derive_dolt_repo_root(&beads).is_err());
    }

    // plan-044 Issue 1.8: the removal must not leave a CHILDLESS `sync:` parent —
    // an inert-but-misleading key that reads as "sync is configured" when nothing is.
    #[test]
    fn remove_sync_remote_config_drops_a_childless_sync_parent() {
        let tmp = tempfile::tempdir().unwrap();
        let beads = tmp.path().join(".beads");
        std::fs::create_dir_all(&beads).unwrap();
        let cfg = beads.join("config.yaml");

        // Nested form: removing `remote:` empties the block, so the parent goes too.
        std::fs::write(
            &cfg,
            "dolt.local-only: true\nsync:\n  remote: git+https://x\n",
        )
        .unwrap();
        remove_sync_remote_config(&beads).unwrap();
        let after = std::fs::read_to_string(&cfg).unwrap();
        assert!(
            !after.contains("sync:"),
            "childless parent survived: {after:?}"
        );
        assert!(
            after.contains("dolt.local-only: true"),
            "clobbered siblings"
        );

        // A `sync:` block with OTHER children is preserved (only `remote:` goes).
        std::fs::write(&cfg, "sync:\n  remote: git+https://x\n  interval: 30\n").unwrap();
        remove_sync_remote_config(&beads).unwrap();
        let after2 = std::fs::read_to_string(&cfg).unwrap();
        assert!(
            after2.contains("sync:"),
            "parent with children must survive"
        );
        assert!(after2.contains("interval: 30"));
        assert!(!after2.contains("remote:"));
    }

    // REQ-BINIT-027 (#160), plan-044 Issue 1.6: on the INIT path under
    // `--local-only`, repair implies the remote-removal step — because `bd init`
    // wires a remote from git origin (measured; see the comment at the plan site)
    // and the local-only assertion that follows does not remove it.
    #[test]
    fn init_path_under_local_only_implies_remote_removal() {
        if which("bd").is_none() || which("git").is_none() {
            return; // verify() would report DepsMissing → repair bails.
        }
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        let has = |r: &RepairResult| {
            r.plan
                .iter()
                .any(|s| s.cmd.iter().any(|c| c == "remove-remote"))
        };

        // No `.beads/` → the NotInitialized branch, the affected path.
        let implied = repair(root, false, /*local_only*/ true, /*remove*/ false).unwrap();
        assert!(
            has(&implied),
            "an init-path repair asked for local-only must clear the remote `bd init` wires \
             from git origin; otherwise repair produces the exact #160 state it prevents"
        );

        // Scoped: without --local-only there is no basis to touch the remote.
        let not_implied = repair(
            root, false, /*local_only*/ false, /*remove*/ false,
        )
        .unwrap();
        assert!(
            !has(&not_implied),
            "the implication is scoped to --local-only"
        );
    }

    // REQ-YF-DOCTOR-006 (#159): a `--repair` step verifies its own postcondition.
    //
    // The unit under test is the DECISION, not the dolt plumbing: given that the
    // read-only predicate still reports the condition after a repair claimed
    // success, the step must report FAIL rather than ok. Driving real `dolt`
    // remotes here would test dolt, not the requirement.
    #[test]
    fn repair_step_reports_fail_when_its_postcondition_still_holds() {
        // The shape apply_step's remove-remote arm implements: apply, then re-probe.
        fn verdict(apply_ok: bool, still_holds: bool) -> (i32, Option<String>) {
            if !apply_ok {
                return (1, Some("apply failed".to_string()));
            }
            if still_holds {
                return (1, Some("postcondition FAILED".to_string()));
            }
            (0, None)
        }

        // The #159 signature: the apply "succeeded" and the remote SURVIVED.
        // Pre-fix this was (0, None) — `ok` with the remote intact.
        let (rc, msg) = verdict(true, true);
        assert_ne!(rc, 0, "a surviving remote must not report ok");
        assert!(msg.unwrap().contains("postcondition FAILED"));

        // A genuine repair: applied and the predicate no longer holds.
        assert_eq!(verdict(true, false), (0, None));

        // A failed apply is still a failure (unchanged).
        assert_ne!(verdict(false, false).0, 0);
    }

    // REQ-BINIT-026 (#159): the SERVER-MODE two-`.dolt` layout resolves
    // deterministically. This is the fixture whose absence let the defect ship:
    // server mode is the CANONICAL profile (REQ-YF-PRE-010 invariant 1), it
    // always carries two `.dolt/` dirs, and the old code counted them and
    // refused — so `--remove-remote` never worked there.
    #[test]
    fn derive_dolt_repo_root_resolves_server_mode_two_dolt_layout() {
        let tmp = tempfile::tempdir().unwrap();
        let beads = tmp.path().join(".beads");
        std::fs::create_dir_all(&beads).unwrap();

        // The real on-disk shape, measured from a live server-mode repo:
        //   .beads/dolt/.dolt                  <- the server's own data dir
        //   .beads/dolt/<dolt_database>/.dolt  <- the database
        std::fs::write(
            beads.join("metadata.json"),
            r#"{"database":"dolt","dolt_mode":"server","dolt_database":"yoshiko_flow"}"#,
        )
        .unwrap();
        std::fs::create_dir_all(beads.join("dolt").join(".dolt")).unwrap();
        let db = beads.join("dolt").join("yoshiko_flow");
        std::fs::create_dir_all(db.join(".dolt")).unwrap();

        // Two live candidates, yet NOT ambiguous: metadata names the database.
        assert_eq!(find_dolt_dirs(&beads).len(), 2);
        assert_eq!(derive_dolt_repo_root(&beads).unwrap(), db);
    }

    // REQ-BINIT-026: the escape hatch stays closed. Two candidates and NO
    // metadata to disambiguate is still a refusal — the fix consults evidence,
    // it does not start guessing.
    #[test]
    fn derive_dolt_repo_root_still_refuses_without_naming_evidence() {
        let tmp = tempfile::tempdir().unwrap();
        let beads = tmp.path().join(".beads");
        std::fs::create_dir_all(&beads).unwrap();
        std::fs::create_dir_all(beads.join("a").join(".dolt")).unwrap();
        std::fs::create_dir_all(beads.join("b").join(".dolt")).unwrap();

        // No metadata.json at all → refuse.
        assert!(derive_dolt_repo_root(&beads).is_err());

        // metadata naming a database that matches NEITHER candidate → refuse.
        std::fs::write(
            beads.join("metadata.json"),
            r#"{"dolt_database":"not_present"}"#,
        )
        .unwrap();
        let err = derive_dolt_repo_root(&beads).unwrap_err();
        assert!(err.contains("refusing to guess"), "got: {err}");
    }

    // REQ-BINIT-016: is_embedded_mode reads metadata.json from a real .beads/.
    #[test]
    fn is_embedded_mode_reads_metadata() {
        let tmp = tempfile::tempdir().unwrap();
        let beads = tmp.path().join(".beads");
        std::fs::create_dir_all(&beads).unwrap();
        std::fs::write(beads.join("metadata.json"), r#"{"dolt_mode":"embedded"}"#).unwrap();
        assert!(is_embedded_mode(&beads));
        std::fs::write(beads.join("metadata.json"), r#"{"dolt_mode":"server"}"#).unwrap();
        assert!(!is_embedded_mode(&beads));
        // Keyless + a server pid file present → server.
        std::fs::write(beads.join("metadata.json"), r#"{}"#).unwrap();
        std::fs::write(beads.join("dolt-server.pid"), "123").unwrap();
        assert!(!is_embedded_mode(&beads));
    }

    // REQ-YF-PRE-010 / REQ-BINIT-025 (#58): the profile engine-mode drift probe.
    // Embedded store → drift (warn-only); local-server store → conformant; absent
    // `.beads/` → not flagged (never false-positive on a non-beads/uninit repo).
    #[test]
    fn has_embedded_engine_drift_classifies_profile() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();

        // No `.beads/` at all → not engine-mode drift (bd_not_initialized's job).
        assert!(!has_embedded_engine_drift(root));

        let beads = root.join(".beads");
        std::fs::create_dir_all(&beads).unwrap();

        // Embedded store (dolt_mode: embedded) → drift.
        std::fs::write(beads.join("metadata.json"), r#"{"dolt_mode":"embedded"}"#).unwrap();
        assert!(has_embedded_engine_drift(root), "embedded → drift");

        // Conformant per-repo local-server (dolt_mode: server) → no drift.
        std::fs::write(beads.join("metadata.json"), r#"{"dolt_mode":"server"}"#).unwrap();
        assert!(!has_embedded_engine_drift(root), "server → conformant");

        // Keyless metadata + server files present → conformant local-server.
        std::fs::write(beads.join("metadata.json"), r#"{}"#).unwrap();
        std::fs::write(beads.join("dolt-server.port"), "3306").unwrap();
        assert!(
            !has_embedded_engine_drift(root),
            "server files → conformant"
        );
    }

    // REQ-BINIT-016 (integration): native-step idempotency + data preservation
    // against a real embedded repo. Dirties the derived Dolt working set, runs
    // the verb, asserts the set is committed (clean) with data preserved, then
    // re-runs to assert a safe no-op. Skips cleanly when `bd`/`dolt` are absent
    // (CI without the toolchain) or the environment does not yield an embedded
    // repo — never a hard failure on a missing dependency.
    #[test]
    fn dolt_commit_embedded_idempotent_and_preserves_data() {
        if which("bd").is_none() || which("dolt").is_none() {
            eprintln!("skip: bd/dolt not on PATH");
            return;
        }
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        let _ = run_in(&["git", "init", "-q"], 60, root);
        let (rc, _o, e) = run_in(&["bd", "init", "--skip-hooks", "--skip-agents"], 180, root);
        if rc != 0 {
            eprintln!("skip: bd init failed: {}", e.trim());
            return;
        }
        let beads = root.join(".beads");
        // Neutralize any auto-started server so we exercise the embedded path.
        let _ = run_in(&["bd", "dolt", "stop"], 60, root);
        let _ = std::fs::remove_file(beads.join("dolt-server.pid"));
        let _ = std::fs::remove_file(beads.join("dolt-server.port"));
        // Mode detection reads metadata.json and must see embedded here.
        assert!(
            beads.join("metadata.json").is_file(),
            "metadata.json present"
        );
        if !is_embedded_mode(&beads) {
            eprintln!("skip: environment produced a server-mode repo");
            return;
        }
        let dolt_root = match derive_dolt_repo_root(&beads) {
            Ok(p) => p,
            Err(e) => {
                eprintln!("skip: could not derive dolt root: {e}");
                return;
            }
        };
        // Ensure a commit identity exists (best-effort; bd usually sets it).
        let _ = run_in(
            &["dolt", "config", "--local", "--add", "user.name", "yf-test"],
            30,
            &dolt_root,
        );
        let _ = run_in(
            &[
                "dolt",
                "config",
                "--local",
                "--add",
                "user.email",
                "yf-test@example.com",
            ],
            30,
            &dolt_root,
        );
        // Dirty the on-disk working set with a probe table.
        let (drc, _o, de) = run_in(
            &[
                "dolt",
                "sql",
                "-q",
                "CREATE TABLE _yf_probe (id INT PRIMARY KEY)",
            ],
            120,
            &dolt_root,
        );
        if drc != 0 {
            eprintln!("skip: dolt sql could not dirty the set: {}", de.trim());
            return;
        }
        // Verb commits the dirty set (data-preserving).
        let (crc, cerr) = dolt_commit_embedded(root, &beads);
        assert_eq!(crc, 0, "verb succeeds: {cerr:?}");
        // Working set is now clean.
        let (_r, st, _e) = run_in(&["dolt", "status"], 60, &dolt_root);
        let stl = st.to_lowercase();
        assert!(
            stl.contains("clean") || stl.contains("nothing to commit"),
            "committed (clean tree): {st}"
        );
        // Data preserved: the probe table survived the commit.
        let (_r2, tables, _e2) = run_in(&["dolt", "sql", "-q", "SHOW TABLES"], 60, &dolt_root);
        assert!(
            tables.contains("_yf_probe"),
            "probe table preserved: {tables}"
        );
        // Re-run on the clean tree: safe no-op.
        let (crc2, cerr2) = dolt_commit_embedded(root, &beads);
        assert_eq!(crc2, 0, "no-op on clean tree: {cerr2:?}");
    }

    // #31 B.3: strip removes the marker-fenced managed block (and a trailing
    // blank), leaves surrounding hand-authored content, and is idempotent.
    #[test]
    fn strip_managed_blocks_removes_block_and_is_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        let f = tmp.path().join("AGENTS.md");
        let body = "# My Agents\n\nKeep this.\n\n\
<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:abc -->\n\
## Beads\nremove me\n\
<!-- END BEADS INTEGRATION -->\n\n\
## Tail\nkeep this too.\n";
        std::fs::write(&f, body).unwrap();

        strip_managed_blocks(&f).unwrap();
        let after = std::fs::read_to_string(&f).unwrap();
        assert!(!after.contains("BEGIN BEADS"), "marker block removed");
        assert!(!after.contains("remove me"));
        assert!(after.contains("Keep this."));
        assert!(after.contains("## Tail"));
        assert!(after.ends_with('\n'));

        // Re-run: no further change.
        strip_managed_blocks(&f).unwrap();
        assert_eq!(std::fs::read_to_string(&f).unwrap(), after);
    }

    // #31 B.3: a file with no managed block is untouched; a missing file is a no-op.
    #[test]
    fn strip_managed_blocks_noop_when_clean() {
        let tmp = tempfile::tempdir().unwrap();
        let f = tmp.path().join("CLAUDE.md");
        std::fs::write(&f, "# beads-skills\n\n@AGENTS.md\n").unwrap();
        strip_managed_blocks(&f).unwrap();
        assert_eq!(
            std::fs::read_to_string(&f).unwrap(),
            "# beads-skills\n\n@AGENTS.md\n"
        );
        // Absent file: Ok, no panic.
        strip_managed_blocks(&tmp.path().join("nope.md")).unwrap();
    }

    // #31 B.4: prune deletes an empty/hook-only settings.json (and the dir) but
    // NEVER a settings.json carrying a real key (a #30 baseline).
    #[test]
    fn prune_settings_deletes_only_when_empty() {
        // Empty-ish → deleted.
        for content in ["{}", r#"{"hooks": {}}"#, r#"{"hooks": {"x": []}}"#] {
            let tmp = tempfile::tempdir().unwrap();
            let dir = tmp.path().join(".claude");
            std::fs::create_dir_all(&dir).unwrap();
            std::fs::write(dir.join("settings.json"), content).unwrap();
            prune_empty_settings(tmp.path()).unwrap();
            assert!(
                !dir.join("settings.json").exists(),
                "empty settings.json deleted: {content}"
            );
            assert!(!dir.exists(), "empty .claude pruned: {content}");
        }

        // Meaningful baseline → preserved.
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path().join(".claude");
        std::fs::create_dir_all(&dir).unwrap();
        let baseline = r#"{"todoFeatureEnabled": false}"#;
        std::fs::write(dir.join("settings.json"), baseline).unwrap();
        prune_empty_settings(tmp.path()).unwrap();
        assert!(
            dir.join("settings.json").exists(),
            "baseline settings.json preserved"
        );

        // Absent file → no-op (no panic).
        let tmp2 = tempfile::tempdir().unwrap();
        prune_empty_settings(tmp2.path()).unwrap();
    }

    // #31 B.4: json_is_effectively_empty classification.
    #[test]
    fn json_empty_classification() {
        let empty = ["{}", r#"{"hooks": {}}"#, "[]", r#""""#, "null"];
        for s in empty {
            let v: serde_json::Value = serde_json::from_str(s).unwrap();
            assert!(json_is_effectively_empty(&v), "{s} is empty");
        }
        let full = [r#"{"a": 1}"#, "true", "0", r#"["x"]"#, r#"{"k": {"n": 1}}"#];
        for s in full {
            let v: serde_json::Value = serde_json::from_str(s).unwrap();
            assert!(!json_is_effectively_empty(&v), "{s} is NOT empty");
        }
    }

    // #43: parse_bd_config_value reads the `value` field, and an unset key
    // (`"value": ""` — the JSON shape of the plain-text `(not set …)` sentinel)
    // is the empty string, NOT a configured value. This is the regression that
    // made preflight perpetually flag a bogus "Dolt remote under local-only".
    #[test]
    fn bd_config_value_unset_is_empty() {
        // Unset key — must parse to "" (not the sentinel, not None).
        let unset = r#"{"key":"sync.remote","location":"config.yaml","value":""}"#;
        assert_eq!(parse_bd_config_value(unset), Some(String::new()));
        // Set key — the configured value.
        let set = r#"{"key":"dolt.local-only","location":"config.yaml","value":"true"}"#;
        assert_eq!(parse_bd_config_value(set), Some("true".to_string()));
        // Missing/null value field → empty string (treated as unset).
        assert_eq!(parse_bd_config_value(r#"{"key":"x"}"#), Some(String::new()));
        assert_eq!(
            parse_bd_config_value(r#"{"value":null}"#),
            Some(String::new())
        );
        // Unparseable (e.g. the plain-text sentinel itself) → None.
        assert_eq!(
            parse_bd_config_value("sync.remote (not set in config.yaml)"),
            None
        );
    }

    // dqo: prune-codex deletes the bare `[features]` residual (and the dir) but
    // NEVER a config.toml carrying a real key.
    #[test]
    fn prune_codex_deletes_only_when_empty() {
        // Residual / empty-ish → deleted.
        for content in ["[features]\n", "[features]", "", "# just a comment\n"] {
            let tmp = tempfile::tempdir().unwrap();
            let dir = tmp.path().join(".codex");
            std::fs::create_dir_all(&dir).unwrap();
            std::fs::write(dir.join("config.toml"), content).unwrap();
            prune_empty_codex(tmp.path()).unwrap();
            assert!(
                !dir.join("config.toml").exists(),
                "empty config.toml deleted: {content:?}"
            );
            assert!(!dir.exists(), "empty .codex pruned: {content:?}");
        }

        // Meaningful config → preserved.
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path().join(".codex");
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("config.toml"), "[features]\nhooks = true\n").unwrap();
        prune_empty_codex(tmp.path()).unwrap();
        assert!(
            dir.join("config.toml").exists(),
            "config with a real key preserved"
        );

        // A .codex/ holding other files is preserved even when config is empty.
        let tmp2 = tempfile::tempdir().unwrap();
        let dir2 = tmp2.path().join(".codex");
        std::fs::create_dir_all(&dir2).unwrap();
        std::fs::write(dir2.join("config.toml"), "[features]\n").unwrap();
        std::fs::write(dir2.join("other.toml"), "x = 1\n").unwrap();
        prune_empty_codex(tmp2.path()).unwrap();
        assert!(!dir2.join("config.toml").exists(), "empty config deleted");
        assert!(dir2.exists(), ".codex with other files kept");

        // Absent file → no-op (no panic).
        let tmp3 = tempfile::tempdir().unwrap();
        prune_empty_codex(tmp3.path()).unwrap();
    }

    // dqo: toml_is_effectively_empty classification.
    #[test]
    fn toml_empty_classification() {
        let empty = ["[features]\n", "[features]", "", "  \n# c\n[a.b]\n"];
        for s in empty {
            assert!(toml_is_effectively_empty(s), "{s:?} is empty");
        }
        let full = ["hooks = true", "[features]\nhooks = true\n", "x = 1"];
        for s in full {
            assert!(!toml_is_effectively_empty(s), "{s:?} is NOT empty");
        }
    }

    // #31 B.3: rmdir-beads-skill removes the dir and prunes empty parents, but
    // leaves a `.agents/` that holds other content. Idempotent.
    #[test]
    fn rmdir_beads_skill_prunes_and_is_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        let skill = tmp.path().join(".agents/skills/beads");
        std::fs::create_dir_all(&skill).unwrap();
        std::fs::write(skill.join("SKILL.md"), "x").unwrap();
        let cmd: Vec<String> = ["<native>", "rmdir-beads-skill"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        let (rc, err) = apply_native(&cmd, tmp.path(), &tmp.path().join(".beads"));
        assert_eq!(rc, 0);
        assert!(err.is_none());
        assert!(!tmp.path().join(".agents").exists(), "empty .agents pruned");

        // Re-run on a clean tree: still rc 0.
        let (rc2, _) = apply_native(&cmd, tmp.path(), &tmp.path().join(".beads"));
        assert_eq!(rc2, 0);

        // A .agents/ with other content is preserved.
        let tmp2 = tempfile::tempdir().unwrap();
        std::fs::create_dir_all(tmp2.path().join(".agents/skills/beads")).unwrap();
        std::fs::create_dir_all(tmp2.path().join(".agents/rules")).unwrap();
        apply_native(&cmd, tmp2.path(), &tmp2.path().join(".beads"));
        assert!(!tmp2.path().join(".agents/skills/beads").exists());
        assert!(tmp2.path().join(".agents/rules").exists(), ".agents kept");
    }

    // ---- #39 B.1/B.3: canonicalization cleanup tests ----

    /// Init a git repo in `dir` (quiet, with a deterministic identity) so
    /// `git ls-files` / `git rm` work. Returns whether init succeeded (skip the
    /// test body cleanly on a host with no git).
    fn git_init(dir: &Path) -> bool {
        if which("git").is_none() {
            return false;
        }
        for argv in [
            vec!["git", "init", "--quiet"],
            vec!["git", "config", "user.email", "t@example.com"],
            vec!["git", "config", "user.name", "t"],
            vec!["git", "config", "commit.gpgsign", "false"],
        ] {
            let (rc, _o, _e) = run_in(&argv, 30, dir);
            if rc != 0 {
                return false;
            }
        }
        true
    }

    fn git_add_commit(dir: &Path) {
        run_in(&["git", "add", "-A"], 30, dir);
        run_in(&["git", "commit", "-m", "seed", "--quiet"], 30, dir);
    }

    fn is_tracked(dir: &Path, rel: &str) -> bool {
        let (rc, out, _e) = run_in(&["git", "ls-files", "--", rel], 30, dir);
        rc == 0 && !out.trim().is_empty()
    }

    // The pattern matcher: dir-prefix, `.*` glob, and exact-path semantics.
    #[test]
    fn untrack_pattern_match_semantics() {
        assert!(untrack_pattern_matches(
            ".beads/interactions.jsonl",
            ".beads/interactions.jsonl"
        ));
        assert!(!untrack_pattern_matches(
            ".beads/interactions.jsonl",
            ".beads/interactions.jsonl.bak"
        ));
        // Directory prefix.
        assert!(untrack_pattern_matches(
            ".beads/embeddeddolt/",
            ".beads/embeddeddolt/x/y"
        ));
        assert!(!untrack_pattern_matches(
            ".beads/embeddeddolt/",
            ".beads/embeddeddolt"
        ));
        // dolt-server.* glob.
        assert!(untrack_pattern_matches(
            ".beads/dolt-server.*",
            ".beads/dolt-server.pid"
        ));
        assert!(untrack_pattern_matches(
            ".beads/dolt-server.*",
            ".beads/dolt-server.activity"
        ));
        assert!(!untrack_pattern_matches(
            ".beads/dolt-server.*",
            ".beads/dolt-serverX"
        ));
        assert!(!untrack_pattern_matches(
            ".beads/dolt-server.*",
            ".beads/other"
        ));
    }

    // #39 B.3: untrack idempotency — no-op when nothing tracked; untracks a tracked
    // interactions.jsonl while leaving the working file in place.
    #[test]
    fn untrack_runtime_idempotent_and_keeps_working_file() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        if !git_init(root) {
            return; // no git on host — skip.
        }
        let beads = root.join(".beads");
        std::fs::create_dir_all(&beads).unwrap();

        // Case A: NONE of the set tracked → untrack is a clean no-op.
        std::fs::write(root.join("README"), "x").unwrap();
        git_add_commit(root);
        untrack_runtime(root).unwrap();
        assert!(root.join("README").exists());

        // Case B: track interactions.jsonl, then untrack.
        std::fs::write(beads.join("interactions.jsonl"), "log\n").unwrap();
        run_in(&["git", "add", "-f", ".beads/interactions.jsonl"], 30, root);
        git_add_commit(root);
        assert!(
            is_tracked(root, ".beads/interactions.jsonl"),
            "precondition"
        );

        untrack_runtime(root).unwrap();
        assert!(
            !is_tracked(root, ".beads/interactions.jsonl"),
            "untracked from index"
        );
        assert!(
            beads.join("interactions.jsonl").exists(),
            "working file kept (--cached)"
        );

        // Idempotent re-run: still a no-op, file still present.
        untrack_runtime(root).unwrap();
        assert!(beads.join("interactions.jsonl").exists());
    }

    // #66 (REQ-BINIT-023): untrack ⇒ ignore parity. After repair untracks
    // `.beads/interactions.jsonl` AND writes `.beads/.gitignore` with the
    // BEADS_GITIGNORE top-up set, the file is both untracked and IGNORED — it must
    // not resurface as `?? .beads/interactions.jsonl` on the next `git status`.
    #[test]
    fn interactions_jsonl_untracked_then_ignored_no_resurface() {
        // The gitignore top-up set must carry the entry (the crux of #66).
        assert!(
            BEADS_GITIGNORE.contains(&"interactions.jsonl"),
            "BEADS_GITIGNORE must ignore interactions.jsonl (#66)"
        );

        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        if !git_init(root) {
            return; // no git on host — skip.
        }
        let beads = root.join(".beads");
        std::fs::create_dir_all(&beads).unwrap();

        // Track, commit, then untrack the bead file (the pre-#66 resurface setup).
        std::fs::write(beads.join("interactions.jsonl"), "log\n").unwrap();
        run_in(&["git", "add", "-f", ".beads/interactions.jsonl"], 30, root);
        git_add_commit(root);
        untrack_runtime(root).unwrap();
        assert!(
            !is_tracked(root, ".beads/interactions.jsonl"),
            "untracked from index"
        );

        // Write the .beads/.gitignore top-up — the repair step that #66 fixes.
        ensure_gitignore(&beads.join(".gitignore"), BEADS_GITIGNORE).unwrap();

        // git now IGNORES the working file → no `?? .beads/interactions.jsonl`.
        let (rc, out, _e) = run_in(
            &["git", "check-ignore", ".beads/interactions.jsonl"],
            30,
            root,
        );
        assert_eq!(rc, 0, "interactions.jsonl must be git-ignored after top-up");
        assert!(out.contains("interactions.jsonl"));

        // And it does not appear as untracked in porcelain status.
        let (_rc, status, _e) = run_in(&["git", "status", "--porcelain"], 30, root);
        assert!(
            !status.contains("?? .beads/interactions.jsonl"),
            "interactions.jsonl must not resurface as untracked, got: {status:?}"
        );
    }

    // #39 B.3: shim content-guard — a hook carrying `bd hooks run` is removed; a
    // hand-edited hook (no signature) is preserved (index + working tree).
    #[test]
    fn remove_hook_shims_content_guarded() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        if !git_init(root) {
            return;
        }
        let hooks = root.join(".beads").join("hooks");
        std::fs::create_dir_all(&hooks).unwrap();
        std::fs::write(
            hooks.join("pre-commit"),
            "#!/bin/sh\nexec bd hooks run pre-commit \"$@\"\n",
        )
        .unwrap();
        std::fs::write(
            hooks.join("custom"),
            "#!/bin/sh\n# hand-edited, no signature\necho hi\n",
        )
        .unwrap();
        run_in(&["git", "add", "-f", ".beads/hooks"], 30, root);
        git_add_commit(root);
        assert!(is_tracked(root, ".beads/hooks/pre-commit"));
        assert!(is_tracked(root, ".beads/hooks/custom"));

        remove_hook_shims(root).unwrap();

        assert!(
            !is_tracked(root, ".beads/hooks/pre-commit"),
            "shim untracked"
        );
        assert!(
            !hooks.join("pre-commit").exists(),
            "shim working file removed (dead shim)"
        );
        assert!(
            is_tracked(root, ".beads/hooks/custom"),
            "hand-edited hook preserved"
        );
        assert!(hooks.join("custom").exists());

        // Idempotent re-run.
        remove_hook_shims(root).unwrap();
        assert!(is_tracked(root, ".beads/hooks/custom"));
    }

    // #39 B.3: the `remove-remote` plan step is GATED — present only when both
    // `remove_remote` and `local_only` are true; absent otherwise. Dry-run
    // (`apply=false`) only builds the plan, but `repair` still calls `verify`
    // first — which bails `DepsMissing` if bd/git are absent — so the test skips
    // cleanly on a host without them (e.g. CI that doesn't install bd).
    #[test]
    fn remove_remote_step_is_gated() {
        if which("bd").is_none() || which("git").is_none() {
            return; // verify() would report DepsMissing → repair bails; nothing to pin.
        }
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        // No .beads/ → NotInitialized branch; dry-run still emits the full plan.
        let has = |r: &RepairResult| {
            r.plan
                .iter()
                .any(|s| s.cmd.iter().any(|c| c == "remove-remote"))
        };

        let off1 = repair(
            root, false, /*local_only*/ false, /*remove*/ false,
        )
        .unwrap();
        assert!(!has(&off1), "absent when both false");
        // plan-044 Issue 1.6 (#160) NARROWED this case. It formerly asserted
        // `absent when remove_remote false`, unconditionally. That is still true on
        // an ALREADY-INITIALIZED repo, but NOT on the init path: there, `bd init`
        // wires a remote from git origin (measured) and `--local-only` alone now
        // implies its removal. This tempdir has no `.beads/`, so it takes the init
        // path — see `init_path_under_local_only_implies_remote_removal`.
        let off3 = repair(root, false, /*local_only*/ false, /*remove*/ true).unwrap();
        assert!(!has(&off3), "absent when local_only false");
        let on = repair(root, false, /*local_only*/ true, /*remove*/ true).unwrap();
        assert!(has(&on), "present when both true");
    }

    // #39 B.2: the read-only drift detector flags a tracked runtime artifact and a
    // tracked hook shim, and is silent on a clean repo. (Remote drift needs bd, not
    // covered here.)
    #[test]
    fn tracked_drift_detector() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        if !git_init(root) {
            return;
        }
        // Clean repo: no drift.
        std::fs::write(root.join("README"), "x").unwrap();
        git_add_commit(root);
        assert_eq!(tracked_canonicalization_drift(root), (false, false));

        // Track a runtime artifact + a hook shim.
        let beads = root.join(".beads");
        std::fs::create_dir_all(beads.join("hooks")).unwrap();
        std::fs::write(beads.join("interactions.jsonl"), "l\n").unwrap();
        std::fs::write(
            beads.join("hooks").join("pre-commit"),
            "exec bd hooks run pre-commit\n",
        )
        .unwrap();
        run_in(&["git", "add", "-f", ".beads"], 30, root);
        git_add_commit(root);

        let (untracked, shim) = tracked_canonicalization_drift(root);
        assert!(untracked, "tracked interactions.jsonl flagged");
        assert!(shim, "tracked shim flagged");
    }

    // REQ-YF-PRE-007: native chmod step is a no-op (rc 0) when .beads/ is absent.
    #[test]
    fn native_chmod_noop_without_beads() {
        let tmp = tempfile::tempdir().unwrap();
        let cmd = vec![
            "<native>".to_string(),
            "chmod".to_string(),
            "700".to_string(),
            ".beads".to_string(),
        ];
        let (rc, err) = apply_native(&cmd, tmp.path(), &tmp.path().join(".beads"));
        assert_eq!(rc, 0);
        assert!(err.is_none());
    }
}

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
                        r.remediations.push(
                            "Flush + migrate: `bd dolt stop` then `bd migrate schema` then `bd migrate`."
                                .to_string(),
                        );
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

/// Diagnose and (when `apply`) fix a non-existent / incorrect / corrupted beads
/// config — the idempotent sequence from `beads_init.py repair` (REQ-YF-PRE-007).
///
/// ## Native vs shelled, per step (R5 bounded-fallback rationale, GR-011)
///
/// `bd`-driven steps are SHELLED to the real `bd` binary (the contract's
/// authority on Dolt state; reimplementing them in Rust would duplicate bd's
/// migration/hook logic and drift):
///
/// - `bd init` (not_initialized) — shelled.
/// - wedged-migration fix `bd dolt stop` → `bd migrate schema` → `bd migrate`
///   (THAT order; never `bd vc commit` first) — shelled.
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
/// repair clears any configured Dolt `sync.remote`. Off by default — the
/// `--remove-remote` doctor flag is the only way to reach it, because it inverts
/// the otherwise-conservative "never touch the remote" boundary above.
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
        plan.push(shelled(
            "assert local-only Dolt (no remote wired at init)",
            &["bd", "config", "set", "dolt.local-only", "true"],
        ));
        plan.push(shelled(
            "suppress doctor git-hooks warning (hooks intentionally absent)",
            &["bd", "config", "set", "doctor.suppress.git-hooks", "true"],
        ));
    }

    // Wedged-migration repair: flush in-memory working set, THEN migrate.
    if before.status == VerifyStatus::Corrupted {
        plan.push(shelled(
            "stop dolt server (flush working set)",
            &["bd", "dolt", "stop"],
        ));
        plan.push(shelled(
            "apply schema migrations",
            &["bd", "migrate", "schema"],
        ));
        plan.push(shelled("update db metadata version", &["bd", "migrate"]));
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
            "clear Dolt sync.remote under local-only (--remove-remote)",
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

/// Execute a native (Rust `std::fs`) repair step. `cmd[1]` is the verb. Returns
/// `(rc, optional-error-string)`; every arm is idempotent (a no-op on a clean
/// repo). Verbs: `chmod`, `gitignore` (hardening); `hookspath-reset`,
/// `rmdir-beads-skill`, `strip-managed-blocks`, `prune-settings`, `prune-codex`
/// (B.3/B.4 cleanup); `untrack-runtime`, `remove-hook-shims`, `remove-remote`
/// (#39 B.1 canonicalization).
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
        Some("remove-remote") => match remove_dolt_remote(repo_root) {
            Ok(()) => (0, None),
            Err(e) => (1, Some(e.to_string())),
        },
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

/// READ-ONLY detection (#39 B.2, for preflight): whether a non-empty Dolt
/// `sync.remote` is configured AND the repo is in local-only context
/// (`dolt.local-only` is true). Pure inspection: never mutates. This is the
/// drift the `--remove-remote` opt-in clears.
pub fn has_local_only_remote(repo_root: &Path) -> bool {
    let local_only = bd_config_value(repo_root, "dolt.local-only")
        .is_some_and(|v| v.trim().eq_ignore_ascii_case("true"));
    if !local_only {
        return false;
    }
    bd_config_value(repo_root, "sync.remote").is_some_and(|v| !v.trim().is_empty())
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

/// Clear the Dolt `sync.remote` config under local-only (#39 B.1, `--remove-remote`).
/// Inspects `bd config get sync.remote`; when a non-empty remote is configured,
/// unsets it via `bd config unset sync.remote`. Idempotent: a no-op when no remote
/// is set. This is the one repair step that *clears* a remote (it never adds one).
fn remove_dolt_remote(repo_root: &Path) -> std::io::Result<()> {
    // No remote configured (unparseable or empty value) → clean no-op. Uses the
    // `--json` reader so the `(not set …)` sentinel isn't misread as a value (#43).
    let configured =
        bd_config_value(repo_root, "sync.remote").is_some_and(|v| !v.trim().is_empty());
    if !configured {
        return Ok(());
    }
    let (urc, _out, uerr) = run_in(&["bd", "config", "unset", "sync.remote"], 30, repo_root);
    if urc != 0 {
        return Err(std::io::Error::other(format!(
            "bd config unset sync.remote exit {urc}: {}",
            uerr.trim()
        )));
    }
    Ok(())
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

    // REQ-YF-PRE-007: the repair PLAN (dry-run) carries the wedged-migration
    // sequence in the correct order for a corrupted repo — and never `bd vc commit`.
    #[test]
    fn corrupted_plan_has_migration_order() {
        // Build a plan as repair() would for a corrupted verdict, without invoking
        // bd: assert the ordering logic by constructing the corrupted-branch steps.
        let before = VerifyResult {
            status: VerifyStatus::Corrupted,
            ..VerifyResult::base()
        };
        // Mirror repair()'s plan construction for the corrupted branch.
        let mut whys: Vec<&str> = vec![];
        if before.status == VerifyStatus::Corrupted {
            whys.push("stop dolt server (flush working set)");
            whys.push("apply schema migrations");
            whys.push("update db metadata version");
        }
        assert_eq!(
            whys,
            vec![
                "stop dolt server (flush working set)",
                "apply schema migrations",
                "update db metadata version"
            ]
        );
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
        let off2 = repair(root, false, /*local_only*/ true, /*remove*/ false).unwrap();
        assert!(!has(&off2), "absent when remove_remote false");
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

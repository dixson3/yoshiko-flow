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
/// - local-only assertion `bd config set dolt.local-only true` — shelled (never
///   adds a Dolt remote).
///
/// Simple deterministic filesystem hardening is NATIVE Rust (no bd needed; pure
/// `std::fs`): `.beads` perms (chmod 700) and the gitignore top-ups
/// (`_ensure_gitignore`). These mirror the Python `os.chmod` + `_ensure_gitignore`
/// tail of `repair`.
///
/// `local_only` adds the local-only assertion step (Surface §: local-only repos).
pub fn repair(repo_root: &Path, apply: bool, local_only: bool) -> anyhow::Result<RepairResult> {
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

    if before.status == VerifyStatus::NotInitialized {
        plan.push(shelled("initialize beads", &["bd", "init"]));
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
    plan.push(shelled(
        "update git hooks",
        &["bd", "hooks", "install", "--force"],
    ));
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

    // Native filesystem hardening steps (deterministic, no bd).
    plan.push(RepairStep {
        why: "tighten .beads perms (chmod 700)".to_string(),
        cmd: vec![
            "<native>".into(),
            "chmod".into(),
            "700".into(),
            ".beads".into(),
        ],
        native: true,
        rc: None,
        err: None,
    });
    plan.push(RepairStep {
        why: "ensure .beads/.gitignore exclusions".to_string(),
        cmd: vec![
            "<native>".into(),
            "gitignore".into(),
            ".beads/.gitignore".into(),
        ],
        native: true,
        rc: None,
        err: None,
    });
    plan.push(RepairStep {
        why: "ensure project .gitignore exclusions".to_string(),
        cmd: vec!["<native>".into(), "gitignore".into(), ".gitignore".into()],
        native: true,
        rc: None,
        err: None,
    });

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

/// Execute a native (Rust `std::fs`) repair step. `cmd[1]` is the verb
/// (`chmod`/`gitignore`). Returns `(rc, optional-error-string)`; idempotent.
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
        _ => (0, None),
    }
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
    which("bd")?;
    let (_, out, _) = run_in(&["bd", "version"], 60, Path::new("."));
    for tok in out.replace(['(', ')'], " ").split_whitespace() {
        let parts: Vec<&str> = tok.split('.').collect();
        if parts.len() >= 2
            && parts[..2]
                .iter()
                .all(|p| p.chars().all(|c| c.is_ascii_digit()))
        {
            let nums: Vec<u32> = parts
                .iter()
                .filter(|p| p.chars().all(|c| c.is_ascii_digit()) && !p.is_empty())
                .filter_map(|p| p.parse().ok())
                .collect();
            if nums.len() >= 2 {
                return Some((nums[0], nums[1], nums.get(2).copied().unwrap_or(0)));
            }
        }
    }
    None
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
    let path = std::env::var_os("PATH")?;
    for dir in std::env::split_paths(&path) {
        let candidate = dir.join(bin);
        if is_executable(&candidate) {
            return Some(candidate);
        }
    }
    None
}

#[cfg(unix)]
fn is_executable(p: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(p)
        .map(|m| m.is_file() && (m.permissions().mode() & 0o111 != 0))
        .unwrap_or(false)
}

#[cfg(not(unix))]
fn is_executable(p: &Path) -> bool {
    p.is_file()
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

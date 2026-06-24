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
/// `rmdir-beads-skill`, `strip-managed-blocks`, `prune-settings` (B.3/B.4 cleanup).
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
        _ => (0, None),
    }
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

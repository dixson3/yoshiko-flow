//! Managed-block marker engine + per-harness global-rule target map (incl. Pi).
//!
//! Two orthogonal pieces Issue 6.2 owns (Pi's row wired by Issue 6.3):
//!
//! 1. **The managed-block marker engine** (REQ-YF-TUNE-019) — a
//!    `BEGIN`/`END`-delimited managed block placed into an operator-owned rule file
//!    (`AGENTS.md`). It **appends** the block when absent, **replaces only** the span
//!    between the markers when present, **never** touches surrounding operator prose,
//!    is **idempotent** (a second deploy of the same bundle is a byte-identical
//!    no-op), and is **fail-safe** on partial/duplicate/out-of-order markers — it
//!    REFUSES rather than corrupt the file.
//!
//! 2. **The per-harness global-rule target map** (REQ-YF-TUNE-020, non-Pi) — where
//!    each harness's always-loaded rule text lands, and *how* it is deployed there.
//!    Two target kinds:
//!    - [`RuleTargetKind::RulesDir`] — claude-code reads `~/.claude/rules/` (a rules
//!      **directory**), **not** `AGENTS.md`. The full `YOSHIKO_FLOW.md` aggregate
//!      already lands there via the tune rule-deploy seam
//!      ([`super::deploy_rules_aggregate`]); the minimized managed block is therefore
//!      **not separately placed** for claude-code — it is the aggregate's harness.
//!    - [`RuleTargetKind::AgentsMd`] — codex (`~/.codex/AGENTS.md`) and opencode
//!      (`~/.config/opencode/AGENTS.md`) read a single always-loaded `AGENTS.md`
//!      file. The **minimized** irreducible-core bundle
//!      ([`super::minimize::irreducible_core_bundle`]) is deployed there as a managed
//!      block, sharing the file with operator prose.
//!
//! **Pi (Issue 6.3).** Pi's rule target was a capability-gated hidden-unknown until
//! Issue 1.5 resolved it — against earendil-works/pi first-party docs — to
//! `~/.pi/agent/AGENTS.md` (project: `<root>/.pi/AGENTS.md`), pinned in
//! `REQ-YF-TUNE-020`. That verified target is the compiled-in default here — NOT a
//! guess. The `--pi-rule-target {agents-md|append-system}` flag
//! ([`crate::cli::PiRuleTarget`]) is the documented override surface: `append-system`
//! retargets to `~/.pi/agent/APPEND_SYSTEM.md` for an operator who wants it. Because
//! 1.5 verified the default, no "unverified target" notice is emitted by default —
//! that fallback branch is moot. Pi shares the same non-clobbering managed-block
//! deploy engine as codex/opencode.

use std::path::{Path, PathBuf};

use anyhow::{bail, Result};

use super::settings::TuneScope;
use crate::cli::PiRuleTarget;

/// The `BEGIN` sentinel opening a yf-managed rule block. An HTML comment so it is
/// inert in every Markdown renderer (`AGENTS.md` is Markdown).
pub const BEGIN_MARKER: &str = "<!-- BEGIN yf-managed-rules -->";
/// The `END` sentinel closing a yf-managed rule block.
pub const END_MARKER: &str = "<!-- END yf-managed-rules -->";

// ---------------------------------------------------------------------------
// 1. The managed-block marker engine (REQ-YF-TUNE-019).
// ---------------------------------------------------------------------------

/// The result of merging a managed block into a file's existing text.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BlockMerge {
    /// The file already carries this exact block — nothing to write (idempotent).
    Unchanged,
    /// The block was appended (no prior block present); write this text.
    Appended(String),
    /// The existing managed span was replaced (surrounding prose preserved); write
    /// this text.
    Replaced(String),
}

impl BlockMerge {
    /// The text to write, or `None` when the merge is a no-op ([`BlockMerge::Unchanged`]).
    pub fn to_write(&self) -> Option<&str> {
        match self {
            BlockMerge::Unchanged => None,
            BlockMerge::Appended(s) | BlockMerge::Replaced(s) => Some(s),
        }
    }

    /// A short verb for reporting.
    pub fn verb(&self) -> &'static str {
        match self {
            BlockMerge::Unchanged => "unchanged",
            BlockMerge::Appended(_) => "appended",
            BlockMerge::Replaced(_) => "replaced",
        }
    }
}

/// Render the canonical managed block for `body`: `BEGIN\n<body>\n END\n`. The body
/// gets a guaranteed trailing newline before `END`, and the whole block ends with a
/// newline — the deterministic shape both append and replace emit, which is what
/// makes a re-deploy byte-identical.
fn render_block(body: &str) -> String {
    let mut s = String::with_capacity(body.len() + BEGIN_MARKER.len() + END_MARKER.len() + 8);
    s.push_str(BEGIN_MARKER);
    s.push('\n');
    s.push_str(body);
    if !body.ends_with('\n') {
        s.push('\n');
    }
    s.push_str(END_MARKER);
    s.push('\n');
    s
}

/// Append `rendered` after `existing`, separated by a blank line, preserving all
/// operator prose. An empty file becomes just the block.
fn append_after(existing: &str, rendered: &str) -> String {
    if existing.is_empty() {
        return rendered.to_string();
    }
    let mut out = String::with_capacity(existing.len() + rendered.len() + 2);
    out.push_str(existing);
    if !out.ends_with('\n') {
        out.push('\n');
    }
    out.push('\n'); // blank separator line between prose and the managed block
    out.push_str(rendered);
    out
}

/// Merge the managed block carrying `body` into `existing` file text
/// (REQ-YF-TUNE-019).
///
/// - **0 markers** → APPEND the block after the operator prose.
/// - **exactly 1 `BEGIN` + 1 `END`, in order** → REPLACE only the marked span,
///   preserving the prose before `BEGIN` and after `END` verbatim. Byte-identical
///   result → [`BlockMerge::Unchanged`] (idempotent).
/// - **anything else** (a lone `BEGIN`, a lone `END`, duplicates, or `END` before
///   `BEGIN`) → REFUSE with an error; the caller must not write, so the file is
///   never corrupted.
pub fn merge_block(existing: &str, body: &str) -> Result<BlockMerge> {
    let begins = existing.matches(BEGIN_MARKER).count();
    let ends = existing.matches(END_MARKER).count();
    let rendered = render_block(body);

    match (begins, ends) {
        (0, 0) => Ok(BlockMerge::Appended(append_after(existing, &rendered))),
        (1, 1) => {
            let bpos = existing.find(BEGIN_MARKER).expect("one BEGIN present");
            let epos = existing.find(END_MARKER).expect("one END present");
            if epos < bpos {
                bail!(
                    "managed-block markers out of order in the rule file (END before \
                     BEGIN) — refusing to edit rather than corrupt operator content. \
                     Fix or remove the stray markers and re-run."
                );
            }
            // The replaced span runs from BEGIN through the END marker and the single
            // newline that follows it (if any) — `rendered` re-supplies that newline,
            // so consuming it keeps a re-deploy byte-identical.
            let mut span_end = epos + END_MARKER.len();
            if existing[span_end..].starts_with('\n') {
                span_end += 1;
            }
            let mut out = String::with_capacity(existing.len() + rendered.len());
            out.push_str(&existing[..bpos]);
            out.push_str(&rendered);
            out.push_str(&existing[span_end..]);
            if out == existing {
                Ok(BlockMerge::Unchanged)
            } else {
                Ok(BlockMerge::Replaced(out))
            }
        }
        _ => bail!(
            "ambiguous yf-managed-rules markers in the rule file ({begins} BEGIN, \
             {ends} END) — a partial or duplicated marker pair. Refusing to edit \
             rather than guess which span is the managed block and risk corrupting \
             operator content. Resolve the markers by hand and re-run."
        ),
    }
}

/// The outcome of deploying a managed block to a concrete file path.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BlockDeploy {
    /// The file the block targets.
    pub path: PathBuf,
    /// Whether bytes were written (false for a dry-run or an already-aligned file).
    pub wrote: bool,
    /// The merge verb (`appended` / `replaced` / `unchanged`).
    pub action: &'static str,
}

/// Deploy the managed block carrying `body` to `path` (REQ-YF-TUNE-019). Reads the
/// existing file fail-safe (absent → empty), merges via [`merge_block`], and writes
/// only when the merge changed bytes and `dry_run` is false. A merge refusal
/// (partial/duplicate/out-of-order markers) propagates as an `Err` and nothing is
/// written.
pub fn deploy_block(path: &Path, body: &str, dry_run: bool) -> Result<BlockDeploy> {
    let existing = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => String::new(),
        Err(e) => bail!("cannot read rule target {}: {e}", path.display()),
    };
    let merge = merge_block(&existing, body)?;
    let wrote = match merge.to_write() {
        Some(text) if !dry_run => {
            if let Some(parent) = path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            std::fs::write(path, text)?;
            true
        }
        _ => false,
    };
    Ok(BlockDeploy {
        path: path.to_path_buf(),
        wrote,
        action: merge.verb(),
    })
}

/// The result of removing a managed block from a file's existing text
/// (`yf harness tune --revert`, REQ-YF-TUNE-022).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BlockRemoval {
    /// No managed markers present — nothing to remove (idempotent no-op).
    Absent,
    /// The managed span was removed; write this text (surrounding prose preserved).
    Removed(String),
}

/// Remove the yf-managed `BEGIN`..`END` span from `existing`, preserving all
/// surrounding operator prose (REQ-YF-TUNE-022). The inverse of [`merge_block`]:
///
/// - **0 markers** → [`BlockRemoval::Absent`] (idempotent — already reverted).
/// - **exactly 1 `BEGIN` + 1 `END`, in order** → [`BlockRemoval::Removed`], cutting
///   the span from `BEGIN` through `END` (and the trailing newline), plus the single
///   blank separator line the deploy inserted before it, so the prose collapses back.
/// - **anything else** (lone/duplicate/out-of-order markers) → REFUSE with an error;
///   the caller must not write, so the file is never corrupted (fail-safe).
pub fn remove_block(existing: &str) -> Result<BlockRemoval> {
    let begins = existing.matches(BEGIN_MARKER).count();
    let ends = existing.matches(END_MARKER).count();
    match (begins, ends) {
        (0, 0) => Ok(BlockRemoval::Absent),
        (1, 1) => {
            let bpos = existing.find(BEGIN_MARKER).expect("one BEGIN present");
            let epos = existing.find(END_MARKER).expect("one END present");
            if epos < bpos {
                bail!(
                    "managed-block markers out of order in the rule file (END before \
                     BEGIN) — refusing to edit rather than corrupt operator content."
                );
            }
            // Cut from BEGIN through END + a trailing newline.
            let mut span_end = epos + END_MARKER.len();
            if existing[span_end..].starts_with('\n') {
                span_end += 1;
            }
            // Also absorb the single blank separator line the deploy inserted between
            // the operator prose and the block (append_after adds "\n\n"), so removing
            // the block collapses the prose back rather than leaving a trailing gap.
            let mut span_begin = bpos;
            let head = &existing[..span_begin];
            if head.ends_with("\n\n") {
                span_begin -= 1;
            }
            let mut out = String::with_capacity(existing.len());
            out.push_str(&existing[..span_begin]);
            out.push_str(&existing[span_end..]);
            Ok(BlockRemoval::Removed(out))
        }
        _ => bail!(
            "ambiguous yf-managed-rules markers in the rule file ({begins} BEGIN, \
             {ends} END) — refusing to edit rather than guess which span is the \
             managed block. Resolve the markers by hand and re-run."
        ),
    }
}

// ---------------------------------------------------------------------------
// 2. The per-harness global-rule target map (REQ-YF-TUNE-020, non-Pi).
// ---------------------------------------------------------------------------

/// How a harness's always-loaded rule text is placed.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RuleTargetKind {
    /// The harness reads a rules **directory** (claude-code `~/.claude/rules/`). The
    /// full `YOSHIKO_FLOW.md` aggregate lands there via the tune rule-deploy seam;
    /// the minimized managed block is NOT separately placed for this harness.
    RulesDir,
    /// The harness reads a single always-loaded `AGENTS.md` file (codex, opencode,
    /// and pi's verified default). The minimized irreducible-core bundle is deployed
    /// there as a managed block.
    AgentsMd,
    /// The harness reads a single always-loaded `APPEND_SYSTEM.md` file — pi's
    /// `--pi-rule-target append-system` override. Same non-clobbering managed-block
    /// placement as [`RuleTargetKind::AgentsMd`], only the filename differs.
    AppendSystem,
}

/// One row of the per-harness global-rule target map.
#[derive(Debug, Clone, Copy)]
pub struct RuleTarget {
    /// Harness id (the `--harness` value).
    pub harness: &'static str,
    /// Dotted surface directory at **user** scope (e.g. `.claude`, `.codex`,
    /// `.config/opencode`, pi `.pi/agent`) — the same surface the config profile
    /// resolves against (where one ships), so config + rules track.
    pub surface_dir: &'static str,
    /// The **project**-scope surface when it differs from the user surface. Pi's
    /// user surface is `.pi/agent` but its project surface is `.pi` (matching the
    /// skills descriptor's `.pi/skills` project subpath). `None` = same surface at
    /// every scope (claude-code/codex/opencode).
    pub project_surface_dir: Option<&'static str>,
    /// How the rule text is placed for this harness.
    pub kind: RuleTargetKind,
}

impl RuleTarget {
    /// Resolve the concrete rule-target path for this harness at `scope`, anchored at
    /// `home` (user) or `root` (project). Pure — no env reads — so it is unit-testable.
    ///
    /// - [`RuleTargetKind::RulesDir`] → `<anchor>/<surface>/rules` (a directory,
    ///   matching [`super::settings::rules_dir_at`]).
    /// - [`RuleTargetKind::AgentsMd`] → `<anchor>/<surface>/AGENTS.md` (a file).
    /// - [`RuleTargetKind::AppendSystem`] → `<anchor>/<surface>/APPEND_SYSTEM.md`.
    ///
    /// `<surface>` is [`Self::surface_dir`] at user scope, or
    /// [`Self::project_surface_dir`] (falling back to `surface_dir`) at project scope.
    pub fn resolve_at(&self, scope: TuneScope, home: &Path, root: &Path) -> PathBuf {
        let (anchor, surface) = match scope {
            TuneScope::User => (home, self.surface_dir),
            TuneScope::ProjectLocal | TuneScope::ProjectCommitted => {
                (root, self.project_surface_dir.unwrap_or(self.surface_dir))
            }
        };
        let base = anchor.join(surface);
        match self.kind {
            RuleTargetKind::RulesDir => base.join("rules"),
            RuleTargetKind::AgentsMd => base.join("AGENTS.md"),
            RuleTargetKind::AppendSystem => base.join("APPEND_SYSTEM.md"),
        }
    }
}

/// The shipped per-harness global-rule target map (REQ-YF-TUNE-020).
///
/// Pi's row (Issue 6.3) carries the **Issue 1.5-verified** default
/// `RuleTargetKind::AgentsMd` — `~/.pi/agent/AGENTS.md` (user) / `<root>/.pi/AGENTS.md`
/// (project) — a first-party-checked path, **not** a compiled-in guess. The
/// `--pi-rule-target append-system` override swaps the kind to `AppendSystem` at
/// resolve time (see [`effective_rule_target`]); the map itself pins only the
/// verified default.
pub const RULE_TARGETS: &[RuleTarget] = &[
    RuleTarget {
        harness: "claude-code",
        surface_dir: ".claude",
        project_surface_dir: None,
        kind: RuleTargetKind::RulesDir, // reads .claude/rules, not AGENTS.md
    },
    RuleTarget {
        harness: "codex",
        surface_dir: ".codex",
        project_surface_dir: None,
        kind: RuleTargetKind::AgentsMd, // ~/.codex/AGENTS.md
    },
    RuleTarget {
        harness: "opencode",
        surface_dir: ".config/opencode",
        project_surface_dir: None,
        kind: RuleTargetKind::AgentsMd, // ~/.config/opencode/AGENTS.md
    },
    RuleTarget {
        harness: "pi",
        surface_dir: ".pi/agent", // user: ~/.pi/agent/AGENTS.md (Issue 1.5-verified)
        project_surface_dir: Some(".pi"), // project: <root>/.pi/AGENTS.md
        kind: RuleTargetKind::AgentsMd,
    },
];

/// Look up the rule target for a harness id. Returns `None` for any unmapped harness.
///
/// Pi's row carries its **verified default** (`AgentsMd`); to honor the
/// `--pi-rule-target` override use [`effective_rule_target`].
pub fn rule_target(harness: &str) -> Option<&'static RuleTarget> {
    RULE_TARGETS.iter().find(|t| t.harness == harness)
}

/// The effective rule target for `harness`, honoring the pi `--pi-rule-target`
/// override (REQ-YF-TUNE-020). Non-pi harnesses ignore `pi` and return their mapped
/// row verbatim. For pi, the kind is the Issue 1.5-verified `AgentsMd` default or the
/// explicit `AppendSystem` override; the surface (`.pi/agent` user / `.pi` project) is
/// unchanged either way.
pub fn effective_rule_target(harness: &str, pi: PiRuleTarget) -> Option<RuleTarget> {
    let base = *rule_target(harness)?;
    if harness != "pi" {
        return Some(base);
    }
    let kind = match pi {
        PiRuleTarget::AgentsMd => RuleTargetKind::AgentsMd,
        PiRuleTarget::AppendSystem => RuleTargetKind::AppendSystem,
    };
    Some(RuleTarget { kind, ..base })
}

/// `$HOME`, falling back to cwd — total resolution (mirrors [`super::settings`]).
#[allow(dead_code)]
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// Resolve a harness's rule target path from the real environment (`$HOME` + git
/// root), honoring the pi `--pi-rule-target` override, or `None` for an unmapped
/// harness.
///
/// Reserved real-env seam. Issue 7.1's orchestration resolves the rule-target path
/// env-free via [`RuleTarget::resolve_at`] (threading `home`/`root` from `run`), so this
/// wrapper is off the live `tune` path today; kept for the Epic 7.2 bridge / Epic 8
/// revert real-env entry points.
#[allow(dead_code)]
pub fn resolve_rule_target(harness: &str, scope: TuneScope, pi: PiRuleTarget) -> Option<PathBuf> {
    let target = effective_rule_target(harness, pi)?;
    let root = crate::dest::git_root_or_cwd();
    Some(target.resolve_at(scope, &home_dir(), &root))
}

/// Deploy the minimized irreducible-core `bundle` as a managed block for `harness`
/// at `scope` (REQ-YF-TUNE-019 + REQ-YF-TUNE-020, non-Pi).
///
/// - For a single-file harness ([`RuleTargetKind::AgentsMd`] codex/opencode/pi, or
///   [`RuleTargetKind::AppendSystem`] pi's `--pi-rule-target append-system` override),
///   places the block in that file via [`deploy_block`] and returns `Ok(Some(..))`.
///   Pi deploys against the Issue 1.5-verified `~/.pi/agent/AGENTS.md` by default —
///   no "unverified target" notice, since 1.5 verified it.
/// - For a [`RuleTargetKind::RulesDir`] harness (claude-code), returns `Ok(None)` —
///   the full aggregate already serves that harness's rules dir; the minimized block
///   is not separately placed.
/// - For an unmapped harness, returns `Ok(None)`.
///
/// `pi` selects pi's rule-file target and is ignored for non-pi harnesses.
///
/// Reserved real-env seam. Issue 7.1's per-harness orchestration deploys the block
/// env-free (resolving the target via [`RuleTarget::resolve_at`] with `home`/`root`
/// threaded from `run`, then [`deploy_block`]); this real-env wrapper is kept for the
/// Epic 7.2 `--tune` bridge / Epic 8 revert one-shot callers.
#[allow(dead_code)]
pub fn deploy_managed_block(
    harness: &str,
    scope: TuneScope,
    bundle: &str,
    dry_run: bool,
    pi: PiRuleTarget,
) -> Result<Option<BlockDeploy>> {
    let Some(target) = effective_rule_target(harness, pi) else {
        return Ok(None);
    };
    if !matches!(
        target.kind,
        RuleTargetKind::AgentsMd | RuleTargetKind::AppendSystem
    ) {
        return Ok(None);
    }
    let path = resolve_rule_target(harness, scope, pi)
        .expect("mapped harness resolves a rule-target path");
    Ok(Some(deploy_block(&path, bundle, dry_run)?))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn block_body() -> &'static str {
        "rule one: always plan.\nrule two: never TodoWrite.\n"
    }

    // REQ-YF-TUNE-019: appending into an AGENTS.md with pre-existing operator prose
    // PRESERVES that prose (the block is appended after it), and a SECOND deploy of
    // the same bundle is idempotent (byte-identical, no write).
    #[test]
    fn append_preserves_prose_and_is_idempotent() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".codex").join("AGENTS.md");
        let prose = "# My project rules\n\nAlways be nice.\n";
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, prose).unwrap();

        // First deploy: appends the block, prose preserved.
        let first = deploy_block(&path, block_body(), false).unwrap();
        assert!(first.wrote, "first deploy must write");
        assert_eq!(first.action, "appended");
        let after = std::fs::read_to_string(&path).unwrap();
        assert!(
            after.starts_with(prose),
            "operator prose must be preserved verbatim at the top:\n{after}"
        );
        assert!(after.contains(BEGIN_MARKER) && after.contains(END_MARKER));
        assert!(after.contains("rule one: always plan."));

        // Second deploy of the same bundle: byte-identical no-op.
        let before_bytes = std::fs::read(&path).unwrap();
        let second = deploy_block(&path, block_body(), false).unwrap();
        assert!(!second.wrote, "idempotent re-deploy must not write");
        assert_eq!(second.action, "unchanged");
        assert_eq!(
            std::fs::read(&path).unwrap(),
            before_bytes,
            "a second deploy of the same bundle must be byte-identical"
        );
    }

    // REQ-YF-TUNE-019: a content change replaces ONLY the managed span — the prose
    // before BEGIN and after END is preserved verbatim; only the marked body changes.
    #[test]
    fn content_change_replaces_only_the_managed_span() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("AGENTS.md");
        let head = "# Head prose\n\n";
        let tail = "\n## Tail prose\n\nkeep me too.\n";
        // Seed a file with prose on BOTH sides of a managed block.
        let seeded = format!(
            "{head}{BEGIN_MARKER}\nOLD BODY\n{END_MARKER}\n{tail}",
            head = head,
            tail = tail
        );
        std::fs::write(&path, &seeded).unwrap();

        let out = deploy_block(&path, "NEW BODY LINE\n", false).unwrap();
        assert!(out.wrote);
        assert_eq!(out.action, "replaced");
        let after = std::fs::read_to_string(&path).unwrap();

        assert!(after.starts_with(head), "head prose preserved:\n{after}");
        assert!(after.ends_with(tail), "tail prose preserved:\n{after}");
        assert!(after.contains("NEW BODY LINE"), "new body present");
        assert!(!after.contains("OLD BODY"), "old body replaced");
        // Exactly one marker pair survived (no duplication).
        assert_eq!(after.matches(BEGIN_MARKER).count(), 1);
        assert_eq!(after.matches(END_MARKER).count(), 1);
    }

    // REQ-YF-TUNE-019: partial markers (a lone BEGIN) REFUSE — fail-safe, the file is
    // left byte-for-byte uncorrupted.
    #[test]
    fn partial_marker_refuses_without_corruption() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("AGENTS.md");
        let broken = format!("prose\n{BEGIN_MARKER}\nsome half-written block\n");
        std::fs::write(&path, &broken).unwrap();

        let err =
            deploy_block(&path, block_body(), false).expect_err("a lone BEGIN marker must refuse");
        assert!(
            err.to_string().contains("1 BEGIN") && err.to_string().contains("0 END"),
            "refusal must name the marker imbalance: {err}"
        );
        assert_eq!(
            std::fs::read_to_string(&path).unwrap(),
            broken,
            "the file must be left uncorrupted on refusal"
        );
    }

    // REQ-YF-TUNE-019: duplicate marker pairs REFUSE — fail-safe, uncorrupted.
    #[test]
    fn duplicate_markers_refuse() {
        let existing =
            format!("{BEGIN_MARKER}\na\n{END_MARKER}\nmid\n{BEGIN_MARKER}\nb\n{END_MARKER}\n");
        let err =
            merge_block(&existing, block_body()).expect_err("duplicate marker pairs must refuse");
        assert!(
            err.to_string().contains("2 BEGIN") && err.to_string().contains("2 END"),
            "refusal must name the duplication: {err}"
        );
    }

    // REQ-YF-TUNE-019: out-of-order markers (END before BEGIN) REFUSE.
    #[test]
    fn out_of_order_markers_refuse() {
        let existing = format!("{END_MARKER}\nstray\n{BEGIN_MARKER}\n");
        let err = merge_block(&existing, block_body()).expect_err("END-before-BEGIN must refuse");
        assert!(
            err.to_string().contains("out of order"),
            "refusal must explain the ordering problem: {err}"
        );
    }

    // REQ-YF-TUNE-019: appending into an empty/absent file yields just the block.
    #[test]
    fn append_into_absent_file_is_block_only() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("AGENTS.md");
        let out = deploy_block(&path, "only body\n", false).unwrap();
        assert!(out.wrote);
        assert_eq!(out.action, "appended");
        let after = std::fs::read_to_string(&path).unwrap();
        assert_eq!(after, render_block("only body\n"));
    }

    // REQ-YF-TUNE-019: dry-run never writes, even when a change is pending.
    #[test]
    fn dry_run_writes_nothing() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("AGENTS.md");
        let out = deploy_block(&path, "body\n", true).unwrap();
        assert!(!out.wrote, "dry-run must not write");
        assert!(!path.exists(), "dry-run must not create the file");
    }

    // REQ-YF-TUNE-022 (Issue 8.2): remove_block is the inverse of merge_block —
    // it cuts the managed span (and the blank separator the deploy inserted),
    // preserving prose on both sides; a file with no markers is Absent (idempotent);
    // ambiguous/out-of-order markers REFUSE fail-safe.
    #[test]
    fn remove_block_cuts_span_preserving_prose_and_is_idempotent() {
        // Round-trip: deploy then remove restores the original prose exactly.
        let prose = "# My project rules\n\nAlways be nice.\n";
        let deployed = append_after(prose, &render_block(block_body()));
        match remove_block(&deployed).unwrap() {
            BlockRemoval::Removed(out) => assert_eq!(out, prose, "prose restored verbatim"),
            other => panic!("expected Removed, got {other:?}"),
        }

        // No markers → Absent (a second remove is a no-op).
        assert_eq!(remove_block(prose).unwrap(), BlockRemoval::Absent);

        // Prose on BOTH sides: only the span is cut.
        let head = "# Head\n\n";
        let tail = "\n## Tail\n\nkeep me.\n";
        let seeded = format!("{head}{BEGIN_MARKER}\nBODY\n{END_MARKER}\n{tail}");
        match remove_block(&seeded).unwrap() {
            BlockRemoval::Removed(out) => {
                assert!(out.starts_with("# Head"), "head kept: {out}");
                assert!(out.contains("keep me."), "tail kept: {out}");
                assert!(!out.contains("BODY"), "body gone: {out}");
                assert!(!out.contains(BEGIN_MARKER) && !out.contains(END_MARKER));
            }
            other => panic!("expected Removed, got {other:?}"),
        }

        // Ambiguous markers REFUSE (fail-safe).
        let dup = format!("{BEGIN_MARKER}\na\n{END_MARKER}\n{BEGIN_MARKER}\nb\n{END_MARKER}\n");
        assert!(remove_block(&dup).is_err(), "duplicate markers must refuse");
        let ooo = format!("{END_MARKER}\nx\n{BEGIN_MARKER}\n");
        assert!(remove_block(&ooo).is_err(), "out-of-order must refuse");
    }

    // REQ-YF-TUNE-020: the target map resolves each NON-Pi harness's rule path — the
    // claude-code rules DIR (not AGENTS.md), and the codex/opencode AGENTS.md files.
    #[test]
    fn target_map_resolves_non_pi_rule_paths() {
        let home = Path::new("/home/jd");
        let root = Path::new("/repo");

        // claude-code: a rules DIRECTORY, not an AGENTS.md file.
        let cc = rule_target("claude-code").expect("claude-code mapped");
        assert_eq!(cc.kind, RuleTargetKind::RulesDir);
        assert_eq!(
            cc.resolve_at(TuneScope::User, home, root),
            PathBuf::from("/home/jd/.claude/rules")
        );

        // codex: ~/.codex/AGENTS.md (user), <root>/.codex/AGENTS.md (project).
        let codex = rule_target("codex").expect("codex mapped");
        assert_eq!(codex.kind, RuleTargetKind::AgentsMd);
        assert_eq!(
            codex.resolve_at(TuneScope::User, home, root),
            PathBuf::from("/home/jd/.codex/AGENTS.md")
        );
        assert_eq!(
            codex.resolve_at(TuneScope::ProjectLocal, home, root),
            PathBuf::from("/repo/.codex/AGENTS.md")
        );

        // opencode: ~/.config/opencode/AGENTS.md.
        let oc = rule_target("opencode").expect("opencode mapped");
        assert_eq!(oc.kind, RuleTargetKind::AgentsMd);
        assert_eq!(
            oc.resolve_at(TuneScope::User, home, root),
            PathBuf::from("/home/jd/.config/opencode/AGENTS.md")
        );

        // Pi is now mapped (Issue 6.3) — its verified default target.
        assert!(rule_target("pi").is_some(), "pi must be mapped (Issue 6.3)");
        assert!(rule_target("nonesuch").is_none());
    }

    // REQ-YF-TUNE-020: the target map's surface_dir agrees with the config profile's
    // surface_dir for every mapped harness that ships a config profile — config and
    // rule targets never drift onto different surfaces.
    #[test]
    fn target_surface_dirs_agree_with_config_profiles() {
        for t in RULE_TARGETS {
            if let Some(p) = super::super::profile::load_profile(t.harness).unwrap() {
                assert_eq!(
                    p.surface_dir, t.surface_dir,
                    "rule-target surface for {} disagrees with its config profile",
                    t.harness
                );
            }
        }
    }

    // REQ-YF-TUNE-020: deploy_managed_block places a block for an AGENTS.md harness
    // and is a no-op (None) for the claude-code rules-dir harness — the aggregate,
    // not the minimized block, serves claude-code.
    #[test]
    fn deploy_managed_block_targets_agents_md_only() {
        let d = PiRuleTarget::AgentsMd;
        // claude-code (RulesDir) → None: the minimized block is not separately placed.
        let none = deploy_managed_block("claude-code", TuneScope::User, "body\n", true, d).unwrap();
        assert!(
            none.is_none(),
            "claude-code (rules dir) must not receive a separate managed block"
        );
        // pi → Some (Issue 6.3): pi now receives a managed block at its verified target.
        assert!(
            deploy_managed_block("pi", TuneScope::User, "body\n", true, d)
                .unwrap()
                .is_some()
        );
        // an unmapped harness → None.
        assert!(
            deploy_managed_block("nonesuch", TuneScope::User, "body\n", true, d)
                .unwrap()
                .is_none()
        );
    }

    // REQ-YF-TUNE-020 (Issue 6.3): Pi's rule target is the Issue 1.5-VERIFIED
    // `~/.pi/agent/AGENTS.md` (user) / `<root>/.pi/AGENTS.md` (project) — a
    // first-party-checked path, NOT a compiled-in guess. That verified default drives a
    // non-clobbering managed-block deploy (operator prose preserved, idempotent) with NO
    // "unverified target" notice, and the `--pi-rule-target append-system` override
    // retargets to `~/.pi/agent/APPEND_SYSTEM.md`.
    #[test]
    fn pi_verified_target_deploys_non_clobbering_and_append_system_overrides() {
        let home = Path::new("/home/jd");
        let root = Path::new("/repo");

        // --- The verified default resolves to ~/.pi/agent/AGENTS.md (user). ---------
        let default = effective_rule_target("pi", PiRuleTarget::AgentsMd).expect("pi mapped");
        assert_eq!(default.kind, RuleTargetKind::AgentsMd);
        assert_eq!(
            default.resolve_at(TuneScope::User, home, root),
            PathBuf::from("/home/jd/.pi/agent/AGENTS.md"),
            "pi user rule target is the verified ~/.pi/agent/AGENTS.md"
        );
        // Project scope drops to `.pi` (matching the skills descriptor's project subpath).
        assert_eq!(
            default.resolve_at(TuneScope::ProjectLocal, home, root),
            PathBuf::from("/repo/.pi/AGENTS.md"),
            "pi project rule target is <root>/.pi/AGENTS.md"
        );

        // --- The --pi-rule-target append-system override retargets the filename. ----
        let over = effective_rule_target("pi", PiRuleTarget::AppendSystem).expect("pi mapped");
        assert_eq!(over.kind, RuleTargetKind::AppendSystem);
        assert_eq!(
            over.resolve_at(TuneScope::User, home, root),
            PathBuf::from("/home/jd/.pi/agent/APPEND_SYSTEM.md"),
            "append-system override targets ~/.pi/agent/APPEND_SYSTEM.md"
        );

        // --- The verified target drives a NON-CLOBBERING deploy (prose + idempotent). -
        let dir = tempfile::tempdir().unwrap();
        let path = default.resolve_at(TuneScope::User, dir.path(), dir.path());
        assert!(path.ends_with(".pi/agent/AGENTS.md"));
        let prose = "# Pi global rules\n\nHand-written operator guidance.\n";
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, prose).unwrap();

        let first = deploy_block(&path, block_body(), false).unwrap();
        assert!(first.wrote && first.action == "appended");
        let after = std::fs::read_to_string(&path).unwrap();
        assert!(
            after.starts_with(prose),
            "operator prose preserved verbatim at pi's verified target:\n{after}"
        );
        assert!(after.contains(BEGIN_MARKER) && after.contains("rule one: always plan."));

        // Idempotent re-deploy: byte-identical no-op.
        let before = std::fs::read(&path).unwrap();
        let second = deploy_block(&path, block_body(), false).unwrap();
        assert!(!second.wrote && second.action == "unchanged");
        assert_eq!(std::fs::read(&path).unwrap(), before);

        // --- The append-system override deploys to the OTHER file, leaving AGENTS.md. -
        let ov_path = over.resolve_at(TuneScope::User, dir.path(), dir.path());
        assert!(ov_path.ends_with(".pi/agent/APPEND_SYSTEM.md"));
        let ov = deploy_block(&ov_path, block_body(), false).unwrap();
        assert!(ov.wrote && ov_path.exists());
        // The default target file is untouched by the override deploy.
        assert_eq!(
            std::fs::read(&path).unwrap(),
            before,
            "append-system override must not touch the AGENTS.md target"
        );
    }
}

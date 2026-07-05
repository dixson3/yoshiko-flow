//! `yf migrate` — idempotent legacy-state migration (bead 2.7, REQ-YF-MIGRATE-001).
//!
//! Migrates a repo's legacy per-skill state + config from the old `bd*`/bare-name
//! layout to the new `yf-*` layout:
//!
//! - `.state/<oldname>/`         → `.yf/<short>/`
//! - `.<oldname>.local.json`     → `.yf/<short>/config.local.json`
//! - `.yf/<short>.local.json`    → `.yf/<short>/config.local.json` (transitional flat)
//!
//! where the `.yf/<short>/` namespace short name comes from the centralized
//! [`crate::preflight::skill_short_name`] resolver — matching what preflight reads
//! (e.g. `.state/bdplan/` → `.yf/plan/`, NOT the pre-#67 full-name `.yf/yf-plan/`).
//! Config consolidates BOTH legacy sources (the root dotfile and the transitional
//! flat `.yf/<short>.local.json`) into the canonical `.yf/<short>/config.local.json`
//! subdir (#67), and the per-skill top-level gitignore anchors collapse to one
//! `/.yf/` anchor.
//!
//! ## Idempotency guarantees (REQ-YF-MIGRATE-001)
//!
//! - **No-op when migrated:** if the legacy source is absent, the entry is skipped.
//! - **Never clobber a newer/existing dest:** if the dest already exists, the
//!   source is left in place and the entry is reported `skipped` (existing dest) —
//!   migration never overwrites operator state at the new path.
//! - **Safe to re-run:** a second run finds the sources already moved (or dests
//!   present) and does nothing.
//!
//! The move is a rename (atomic within a filesystem) with a copy+remove fallback
//! across filesystems.

use std::path::{Path, PathBuf};

use serde::Serialize;

/// Old-skill → new-skill name map (SPEC §3.8 / bead 2.7). The state subdir and
/// config basename are both keyed by the NEW name.
const SKILL_MAP: &[(&str, &str)] = &[
    ("bdplan", "yf-plan"),
    ("bdresearch", "yf-research"),
    ("beads-authoring", "yf-beads-authoring"),
    ("beads-extra", "yf-beads-extra"),
    ("beads-init", "yf-beads-init"),
    ("beads-upstream", "yf-beads-upstream"),
    ("incubator", "yf-incubator"),
    ("diagram-authoring", "yf-diagram-authoring"),
    ("drift-check", "yf-drift-check"),
    ("optimal-instructions", "yf-optimal-instructions"),
    ("skill-authoring", "yf-skill-authoring"),
    ("markdown-lint", "yf-markdown-lint"),
    ("markdown-pdf", "yf-markdown-pdf"),
];

/// The disposition of one migration candidate.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Action {
    /// Source present, dest free — migrated (or would, in dry-run).
    Migrated,
    /// Source absent — nothing to do.
    SourceAbsent,
    /// Dest already exists — left source untouched (never clobber).
    DestExists,
}

/// One planned/applied migration of a single path pair.
#[derive(Debug, Clone, Serialize)]
pub struct Entry {
    pub kind: &'static str, // "state" | "config"
    pub old: String,
    pub new: String,
    pub from: String,
    pub to: String,
    pub action: Action,
}

/// The full migration result over a repo.
#[derive(Debug, Serialize)]
pub struct MigrateResult {
    pub repo: String,
    pub dry_run: bool,
    pub entries: Vec<Entry>,
    /// Count of entries actually migrated (or that would migrate in dry-run).
    pub migrated: usize,
}

/// Compute (and, unless `dry_run`, apply) the legacy-state migration for `repo`.
pub fn migrate(repo: &Path, dry_run: bool) -> std::io::Result<MigrateResult> {
    let mut entries = Vec::new();

    for (old, new) in SKILL_MAP {
        // The `.yf/<short>/` namespace key comes from the CENTRALIZED resolver
        // (REQ-YF-PRE-004) — NOT the full `new` name — so the state dir migrate
        // writes matches exactly what preflight reads (fixes the historical
        // full-name `.yf/yf-plan/` vs short-name `.yf/plan/` disagreement).
        let short = crate::preflight::skill_short_name(new);

        // State dir: .state/<old>/ → .yf/<short>/
        let state_from = repo.join(".state").join(old);
        let state_to = repo.join(".yf").join(&short);
        entries.push(plan_and_apply(
            "state",
            old,
            new,
            &state_from,
            &state_to,
            dry_run,
        )?);

        // Config → the canonical subdir `.yf/<short>/config.local.json` (REQ-YF-MIGRATE-001
        // revised, #67). TWO legacy sources consolidate into the one dest, in
        // READ-PRECEDENCE order so the value a reader currently sees is preserved:
        //   (1) transitional flat `.yf/<short>.local.json` (read tier 2) — migrated first;
        //   (2) legacy root `.<old>.local.json` (read tier 3) — DestExists if (1) moved.
        // Both are idempotent + never-clobber (an existing dest is left untouched).
        let cfg_to = repo.join(".yf").join(&short).join("config.local.json");
        let flat_from = repo.join(".yf").join(format!("{short}.local.json"));
        entries.push(plan_and_apply(
            "config", old, new, &flat_from, &cfg_to, dry_run,
        )?);
        let legacy_from = repo.join(format!(".{old}.local.json"));
        entries.push(plan_and_apply(
            "config", old, new, &legacy_from, &cfg_to, dry_run,
        )?);
    }

    // Collapse legacy top-level per-skill gitignore anchors to the single `/.yf/`
    // anchor (REQ-YF-PRE-005 revised, #67). Config now lives under `.yf/`, so the
    // per-skill `/.yf-<new>.local.json` and `/.<old>.local.json` dotfile anchors are
    // obsolete. Idempotent: only rewrites `.gitignore` when it actually changes.
    if let Some(collapsed) = collapse_gitignore_anchors(repo, dry_run)? {
        entries.push(collapsed);
    }

    let migrated = entries
        .iter()
        .filter(|e| e.action == Action::Migrated)
        .count();

    Ok(MigrateResult {
        repo: repo.display().to_string(),
        dry_run,
        entries,
        migrated,
    })
}

/// Classify one source→dest pair and, unless dry-run, perform the move.
fn plan_and_apply(
    kind: &'static str,
    old: &str,
    new: &str,
    from: &Path,
    to: &Path,
    dry_run: bool,
) -> std::io::Result<Entry> {
    let action = if !from.exists() {
        Action::SourceAbsent
    } else if to.exists() {
        // Never clobber a newer/existing dest (idempotency invariant).
        Action::DestExists
    } else {
        if !dry_run {
            move_path(from, to)?;
        }
        Action::Migrated
    };
    Ok(Entry {
        kind,
        old: old.to_string(),
        new: new.to_string(),
        from: from.display().to_string(),
        to: to.display().to_string(),
        action,
    })
}

/// Collapse legacy per-skill top-level gitignore anchors to the single `/.yf/`
/// anchor (REQ-YF-PRE-005 revised / REQ-YF-MIGRATE-001, #67). Removes the obsolete
/// per-skill dotfile anchor lines (`/.yf-<new>.local.json`, `/.<old>.local.json`)
/// and their orphaned per-skill comment headers, then ensures `/.yf/` is present.
/// Idempotent: returns `None` (no Entry) when `.gitignore` is absent or already
/// collapsed; returns `Some(Migrated)` (and rewrites, unless `dry_run`) on change.
fn collapse_gitignore_anchors(repo: &Path, dry_run: bool) -> std::io::Result<Option<Entry>> {
    let gitignore = repo.join(".gitignore");
    let text = match std::fs::read_to_string(&gitignore) {
        Ok(t) => t,
        Err(_) => return Ok(None), // no .gitignore → nothing to collapse.
    };

    // The obsolete per-skill dotfile anchors, keyed off SKILL_MAP (both the legacy
    // `bd*`/bare `.<old>.local.json` and the `.yf-<new>.local.json` forms).
    let mut obsolete: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    for (old, new) in SKILL_MAP {
        obsolete.insert(format!("/.{old}.local.json"));
        obsolete.insert(format!("/.{new}.local.json"));
    }

    let kept: Vec<&str> = text
        .lines()
        .filter(|line| {
            let t = line.trim();
            // Drop the obsolete anchor lines …
            if obsolete.contains(t) {
                return false;
            }
            // … and the now-orphaned per-skill comment header the scaffold used to
            // write (`# Skill runtime state + local config (<skill>; Surface
            // Convention §6)`). The GENERAL `/.yf/` header ("… per Skill Surface
            // Convention)") lacks the `§6)` suffix, so it is preserved.
            if t.starts_with("# Skill runtime state + local config (") && t.ends_with("§6)") {
                return false;
            }
            true
        })
        .collect();

    // Collapse consecutive blank lines to one and strip trailing blanks.
    let mut out: Vec<String> = Vec::with_capacity(kept.len());
    for line in kept {
        if line.trim().is_empty() && out.last().map(|l| l.trim().is_empty()).unwrap_or(true) {
            continue;
        }
        out.push(line.to_string());
    }
    while out.last().map(|l| l.trim().is_empty()).unwrap_or(false) {
        out.pop();
    }
    // Ensure the single `/.yf/` anchor is present.
    if !out.iter().any(|l| l.trim() == "/.yf/") {
        if out.last().map(|l| !l.trim().is_empty()).unwrap_or(false) {
            out.push(String::new());
        }
        out.push("# Skill runtime state + local config (never committed; per Skill Surface Convention)".to_string());
        out.push("/.yf/".to_string());
    }

    let rewritten = out.join("\n") + "\n";
    if rewritten == text {
        return Ok(None); // already collapsed — idempotent no-op.
    }
    if !dry_run {
        std::fs::write(&gitignore, &rewritten)?;
    }
    Ok(Some(Entry {
        kind: "gitignore",
        old: String::new(),
        new: String::new(),
        from: gitignore.display().to_string(),
        to: gitignore.display().to_string(),
        action: Action::Migrated,
    }))
}

/// Move `from` → `to`, creating the dest parent. Tries an atomic rename first;
/// falls back to recursive copy + remove across filesystems.
fn move_path(from: &Path, to: &Path) -> std::io::Result<()> {
    if let Some(parent) = to.parent() {
        std::fs::create_dir_all(parent)?;
    }
    match std::fs::rename(from, to) {
        Ok(()) => Ok(()),
        Err(_) => {
            // Cross-device or other rename failure: copy then remove.
            copy_recursive(from, to)?;
            if from.is_dir() {
                std::fs::remove_dir_all(from)
            } else {
                std::fs::remove_file(from)
            }
        }
    }
}

/// Recursively copy a file or directory tree.
fn copy_recursive(from: &Path, to: &Path) -> std::io::Result<()> {
    if from.is_dir() {
        std::fs::create_dir_all(to)?;
        for entry in std::fs::read_dir(from)? {
            let entry = entry?;
            copy_recursive(&entry.path(), &to.join(entry.file_name()))?;
        }
        Ok(())
    } else {
        if let Some(parent) = to.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::copy(from, to).map(|_| ())
    }
}

/// `yf migrate` command body. Resolves the repo (cwd / `--path`), runs the
/// migration, and prints JSON or a human summary. Always exits success (migration
/// is advisory; nothing to fail on a clean repo).
pub fn run(path: Option<PathBuf>, dry_run: bool, json: bool) -> anyhow::Result<()> {
    let repo = path.unwrap_or_else(crate::dest::git_root_or_cwd);
    let result = migrate(&repo, dry_run)?;

    if json {
        println!("{}", serde_json::to_string_pretty(&result)?);
    } else {
        let verb = if dry_run { "would migrate" } else { "migrated" };
        println!(
            "yf migrate ({}): {} {} legacy item(s) under {}",
            if dry_run { "dry-run" } else { "apply" },
            verb,
            result.migrated,
            result.repo
        );
        for e in &result.entries {
            if e.action != Action::SourceAbsent {
                let tag = match e.action {
                    Action::Migrated => verb,
                    Action::DestExists => "skip (dest exists)",
                    Action::SourceAbsent => unreachable!(),
                };
                println!("  [{tag}] {} {} → {}", e.kind, e.from, e.to);
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-MIGRATE-001 (#67): legacy .state/bdplan/foo + .bdplan.local.json migrate
    // to .yf/plan/foo (SHORT name — matches what preflight reads) +
    // .yf/plan/config.local.json (canonical config subdir).
    #[test]
    fn migrates_state_and_config() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::create_dir_all(repo.join(".state").join("bdplan")).unwrap();
        std::fs::write(repo.join(".state").join("bdplan").join("foo"), "x").unwrap();
        std::fs::write(repo.join(".bdplan.local.json"), r#"{"k":1}"#).unwrap();

        let res = migrate(repo, false).unwrap();
        // state + legacy-root config → 2 (flat config source absent here).
        assert_eq!(res.migrated, 2);

        // New paths exist with content (state dir + config subdir use the SHORT name).
        assert!(repo.join(".yf").join("plan").join("foo").is_file());
        assert_eq!(
            std::fs::read_to_string(repo.join(".yf").join("plan").join("config.local.json"))
                .unwrap(),
            r#"{"k":1}"#
        );
        // Old paths gone.
        assert!(!repo.join(".state").join("bdplan").exists());
        assert!(!repo.join(".bdplan.local.json").exists());
    }

    // REQ-YF-MIGRATE-001: re-running on an already-migrated repo is a no-op.
    #[test]
    fn rerun_is_noop() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::create_dir_all(repo.join(".state").join("bdresearch")).unwrap();
        std::fs::write(
            repo.join(".state").join("bdresearch").join("idx.json"),
            "{}",
        )
        .unwrap();

        let first = migrate(repo, false).unwrap();
        assert_eq!(first.migrated, 1);

        let second = migrate(repo, false).unwrap();
        assert_eq!(second.migrated, 0);
        // Every entry is now source-absent or dest-exists; none migrated.
        assert!(second.entries.iter().all(|e| e.action != Action::Migrated));
        // Content intact (state dir uses the SHORT name).
        assert!(repo
            .join(".yf")
            .join("research")
            .join("idx.json")
            .is_file());
    }

    // REQ-YF-MIGRATE-001: an existing dest is never clobbered.
    #[test]
    fn existing_dest_not_clobbered() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        // Legacy source AND a pre-existing new dest both present.
        std::fs::create_dir_all(repo.join(".state").join("bdplan")).unwrap();
        std::fs::write(repo.join(".state").join("bdplan").join("old.txt"), "OLD").unwrap();
        std::fs::create_dir_all(repo.join(".yf").join("plan")).unwrap();
        std::fs::write(repo.join(".yf").join("plan").join("new.txt"), "NEW").unwrap();

        let res = migrate(repo, false).unwrap();
        // The state entry must be DestExists, not migrated.
        let state_entry = res
            .entries
            .iter()
            .find(|e| e.kind == "state" && e.old == "bdplan")
            .unwrap();
        assert_eq!(state_entry.action, Action::DestExists);
        // Dest content untouched; source still present.
        assert_eq!(
            std::fs::read_to_string(repo.join(".yf").join("plan").join("new.txt")).unwrap(),
            "NEW"
        );
        assert!(repo.join(".state").join("bdplan").join("old.txt").is_file());
    }

    // REQ-YF-MIGRATE-001: dry-run reports what would migrate without touching disk.
    #[test]
    fn dry_run_changes_nothing() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::write(repo.join(".markdown-lint.local.json"), "{}").unwrap();

        let res = migrate(repo, true).unwrap();
        assert!(res.dry_run);
        assert_eq!(res.migrated, 1);
        // Nothing moved.
        assert!(repo.join(".markdown-lint.local.json").is_file());
        assert!(!repo
            .join(".yf")
            .join("markdown-lint")
            .join("config.local.json")
            .exists());
    }

    // REQ-YF-MIGRATE-001: a clean repo (no legacy state) migrates nothing.
    #[test]
    fn clean_repo_noop() {
        let tmp = tempfile::tempdir().unwrap();
        let res = migrate(tmp.path(), false).unwrap();
        assert_eq!(res.migrated, 0);
        // A clean repo has no legacy anchors either → no gitignore Entry.
        assert!(res.entries.iter().all(|e| e.action == Action::SourceAbsent));
    }

    // REQ-YF-MIGRATE-001 (#67): the transitional flat `.yf/<short>.local.json`
    // migrates into the canonical `.yf/<short>/config.local.json` subdir.
    #[test]
    fn flat_config_migrates_to_subdir() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::create_dir_all(repo.join(".yf")).unwrap();
        std::fs::write(repo.join(".yf").join("plan.local.json"), r#"{"src":"flat"}"#).unwrap();

        let res = migrate(repo, false).unwrap();
        assert_eq!(res.migrated, 1);
        assert_eq!(
            std::fs::read_to_string(repo.join(".yf").join("plan").join("config.local.json"))
                .unwrap(),
            r#"{"src":"flat"}"#
        );
        assert!(!repo.join(".yf").join("plan.local.json").exists());
    }

    // REQ-YF-MIGRATE-001 (#67): when BOTH a flat and a legacy-root config exist, the
    // flat (higher read-precedence, tier 2) wins the subdir; the legacy source is
    // left untouched (never-clobber), preserving the value a reader currently sees.
    #[test]
    fn flat_wins_over_legacy_on_consolidation() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::create_dir_all(repo.join(".yf")).unwrap();
        std::fs::write(repo.join(".yf").join("plan.local.json"), r#"{"src":"flat"}"#).unwrap();
        std::fs::write(repo.join(".bdplan.local.json"), r#"{"src":"legacy"}"#).unwrap();

        migrate(repo, false).unwrap();
        // The subdir carries the flat value; the legacy file is left in place.
        assert_eq!(
            std::fs::read_to_string(repo.join(".yf").join("plan").join("config.local.json"))
                .unwrap(),
            r#"{"src":"flat"}"#
        );
        assert!(
            repo.join(".bdplan.local.json").is_file(),
            "legacy source left untouched (never-clobber)"
        );
    }

    // REQ-YF-PRE-005 revised (#67): legacy per-skill top-level gitignore anchors
    // collapse to the single `/.yf/`; orphaned per-skill headers are dropped and
    // the general `/.yf/` header preserved. Idempotent on re-run.
    #[test]
    fn gitignore_anchors_collapse() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        let gi = "\
/target/

# Skill runtime state + local config (never committed; per Skill Surface Convention)
/.yf/
/.yf-plan.local.json

# Skill runtime state + local config (bdplan; Surface Convention §6)
/.bdplan.local.json

# Skill runtime state + local config (yf-beads-init; Surface Convention §6)
/.yf-beads-init.local.json
";
        std::fs::write(repo.join(".gitignore"), gi).unwrap();

        migrate(repo, false).unwrap();
        let out = std::fs::read_to_string(repo.join(".gitignore")).unwrap();
        assert!(out.contains("/.yf/"), "the /.yf/ anchor is preserved");
        assert!(out.contains("/target/"), "unrelated entries preserved");
        assert!(
            !out.contains(".yf-plan.local.json"),
            "obsolete per-skill anchor removed: {out}"
        );
        assert!(
            !out.contains(".bdplan.local.json"),
            "obsolete legacy anchor removed: {out}"
        );
        assert!(
            !out.contains(".yf-beads-init.local.json"),
            "obsolete per-skill anchor removed: {out}"
        );
        assert!(
            !out.contains("§6)"),
            "orphaned per-skill headers dropped: {out}"
        );
        assert!(
            out.contains("per Skill Surface Convention)"),
            "general /.yf/ header preserved: {out}"
        );

        // Idempotent: a second run makes no further change (no gitignore Entry).
        let res2 = migrate(repo, false).unwrap();
        assert!(
            res2.entries.iter().all(|e| e.kind != "gitignore"),
            "collapse is idempotent"
        );
    }
}

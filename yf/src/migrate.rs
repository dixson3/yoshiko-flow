//! `yf migrate` — idempotent legacy-state migration (bead 2.7, REQ-YF-MIGRATE-001).
//!
//! Migrates a repo's legacy per-skill state + config from the old `bd*`/bare-name
//! layout to the new `yf-*` layout:
//!
//! - `.state/<oldname>/`      → `.yf/<newname>/`
//! - `.<oldname>.local.json`  → `.yf-<newname>.local.json`
//!
//! where the dest is keyed by the NEW skill name (e.g. `.state/bdplan/` →
//! `.yf/yf-plan/`, `.bdplan.local.json` → `.yf-plan.local.json`).
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
        // State dir: .state/<old>/ → .yf/<new>/
        let state_from = repo.join(".state").join(old);
        let state_to = repo.join(".yf").join(new);
        entries.push(plan_and_apply(
            "state",
            old,
            new,
            &state_from,
            &state_to,
            dry_run,
        )?);

        // Config file: .<old>.local.json → .yf-<new>.local.json
        let cfg_from = repo.join(format!(".{old}.local.json"));
        let cfg_to = repo.join(format!(".{new}.local.json"));
        entries.push(plan_and_apply(
            "config", old, new, &cfg_from, &cfg_to, dry_run,
        )?);
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

    // REQ-YF-MIGRATE-001: legacy .state/bdplan/foo + .bdplan.local.json migrate to
    // .yf/yf-plan/foo + .yf-plan.local.json.
    #[test]
    fn migrates_state_and_config() {
        let tmp = tempfile::tempdir().unwrap();
        let repo = tmp.path();
        std::fs::create_dir_all(repo.join(".state").join("bdplan")).unwrap();
        std::fs::write(repo.join(".state").join("bdplan").join("foo"), "x").unwrap();
        std::fs::write(repo.join(".bdplan.local.json"), r#"{"k":1}"#).unwrap();

        let res = migrate(repo, false).unwrap();
        assert_eq!(res.migrated, 2);

        // New paths exist with content.
        assert!(repo.join(".yf").join("yf-plan").join("foo").is_file());
        assert_eq!(
            std::fs::read_to_string(repo.join(".yf-plan.local.json")).unwrap(),
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
        // Content intact.
        assert!(repo
            .join(".yf")
            .join("yf-research")
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
        std::fs::create_dir_all(repo.join(".yf").join("yf-plan")).unwrap();
        std::fs::write(repo.join(".yf").join("yf-plan").join("new.txt"), "NEW").unwrap();

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
            std::fs::read_to_string(repo.join(".yf").join("yf-plan").join("new.txt")).unwrap(),
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
        assert!(!repo.join(".yf-markdown-lint.local.json").exists());
    }

    // REQ-YF-MIGRATE-001: a clean repo (no legacy state) migrates nothing.
    #[test]
    fn clean_repo_noop() {
        let tmp = tempfile::tempdir().unwrap();
        let res = migrate(tmp.path(), false).unwrap();
        assert_eq!(res.migrated, 0);
        assert!(res.entries.iter().all(|e| e.action == Action::SourceAbsent));
    }
}

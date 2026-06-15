//! `yf skills status | upgrade | remove` (bead 1.6).
//!
//! - `status`  — per-skill installed / up-to-date / complete / unmodified (REQ-YF-MARK-003).
//! - `upgrade` — rewrite files, re-inject the marker, prune extras (REQ-YF-MARK-004).
//! - `remove`  — delete a skill's deployed dir; remove a companion rule only when
//!   unambiguously owned (its bytes equal the embedded source).

use anyhow::Result;

use super::common;
use crate::cli::SkillsArgs;
use crate::frontmatter;

/// `yf skills status` (REQ-YF-MARK-003).
pub fn status(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let (skills_dir, _rules_dir) = common::dirs_for(args);

    let mut healths = Vec::new();
    for name in &sel.install {
        healths.push(common::skill_health(name, &skills_dir)?);
    }

    if args.json {
        let arr: Vec<_> = healths
            .iter()
            .map(|h| {
                serde_json::json!({
                    "name": h.name,
                    "installed": h.installed,
                    "up_to_date": h.up_to_date,
                    "complete": h.complete,
                    "unmodified": h.unmodified,
                    "embedded_hash": h.embedded_hash,
                    "marker_hash": h.marker_hash,
                    "state": h.doctor_state(),
                })
            })
            .collect();
        let out = serde_json::json!({
            "command": "skills status",
            "skills_dir": skills_dir,
            "skills": arr,
        });
        println!("{}", serde_json::to_string(&out)?);
        return Ok(());
    }

    println!("Skill status @ {}", skills_dir.display());
    println!(
        "  {:<24} {:<10} {:<11} {:<9} UNMODIFIED",
        "SKILL", "INSTALLED", "UP-TO-DATE", "COMPLETE"
    );
    for h in &healths {
        println!(
            "  {:<24} {:<10} {:<11} {:<9} {}",
            h.name,
            yn(h.installed),
            yn(h.up_to_date),
            yn(h.complete),
            yn(h.unmodified),
        );
    }
    Ok(())
}

/// `yf skills upgrade` — rewrite + re-mark + prune (REQ-YF-MARK-004).
pub fn upgrade(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let (skills_dir, rules_dir) = common::dirs_for(args);

    let mut upgraded = Vec::new();
    let mut pruned: Vec<String> = Vec::new();
    let mut rules_written: Vec<String> = Vec::new();

    for name in &sel.install {
        let extras = common::extra_deployed_files(name, &skills_dir)?;
        if args.dry_run {
            for e in &extras {
                pruned.push(format!("{name}/{e}"));
            }
            upgraded.push(name.clone());
            continue;
        }
        common::deploy_skill(name, &skills_dir, /*prune=*/ true)?;
        for e in &extras {
            pruned.push(format!("{name}/{e}"));
        }
        // Upgrade refreshes companion rules too (force, since they are owned).
        let (written, _kept) = common::install_rules(name, &rules_dir, /*force=*/ true)?;
        rules_written.extend(written);
        upgraded.push(name.clone());
    }

    if args.json {
        let out = serde_json::json!({
            "command": "skills upgrade",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "upgraded": upgraded,
            "pruned": pruned,
            "rules_written": rules_written,
        });
        println!("{}", serde_json::to_string(&out)?);
        return Ok(());
    }

    let verb = if args.dry_run {
        "would upgrade"
    } else {
        "upgraded"
    };
    for name in &upgraded {
        println!("  {verb} {name} -> {}", skills_dir.join(name).display());
    }
    for p in &pruned {
        let pv = if args.dry_run {
            "would prune"
        } else {
            "pruned"
        };
        println!("      {pv} {p}");
    }
    if !args.dry_run {
        for base in &rules_written {
            println!("      rule {base} -> {}", rules_dir.join(base).display());
        }
    }
    Ok(())
}

/// `yf skills remove` — delete deployed skill dirs (and owned rules).
///
/// Rule-removal policy (documented decision): a companion rule is removed only
/// when its on-disk bytes are byte-identical to the embedded source — i.e. it is
/// unambiguously `yf`-owned and unmodified. A hand-edited or absent rule is left
/// in place. install.py never removed rules at all; this is the conservative
/// extension that still honors GR-008 (touch only own, unmodified surfaces).
pub fn remove(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let (skills_dir, rules_dir) = common::dirs_for(args);

    let mut removed = Vec::new();
    let mut rules_removed = Vec::new();
    let mut rules_kept = Vec::new();

    for name in &sel.install {
        let skill_root = skills_dir.join(name);
        if skill_root.exists() {
            if !args.dry_run {
                std::fs::remove_dir_all(&skill_root)?;
            }
            removed.push(name.clone());
        }
        for (base, bytes) in common::embedded_rules(name) {
            let target = rules_dir.join(&base);
            if !target.exists() {
                continue;
            }
            let on_disk = std::fs::read(&target).unwrap_or_default();
            if on_disk == bytes {
                if !args.dry_run {
                    std::fs::remove_file(&target)?;
                }
                rules_removed.push(base);
            } else {
                rules_kept.push(base); // modified / not owned → preserve
            }
        }
    }

    if args.json {
        let out = serde_json::json!({
            "command": "skills remove",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "removed": removed,
            "rules_removed": rules_removed,
            "rules_kept": rules_kept,
        });
        println!("{}", serde_json::to_string(&out)?);
        return Ok(());
    }

    let verb = if args.dry_run {
        "would remove"
    } else {
        "removed"
    };
    for name in &removed {
        println!("  {verb} {name} -> {}", skills_dir.join(name).display());
    }
    for base in &rules_removed {
        println!("      {verb} rule {base}");
    }
    for base in &rules_kept {
        println!("      rule {base}: kept (modified/unowned — not removed)");
    }
    if removed.is_empty() {
        println!("  (nothing installed to remove)");
    }
    Ok(())
}

fn yn(b: bool) -> &'static str {
    if b {
        "yes"
    } else {
        "no"
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::{Scope, Surface};
    use crate::{embed, marker};
    use std::path::Path;

    fn args_for(target: &Path) -> SkillsArgs {
        SkillsArgs {
            names: vec!["yf-beads-extra".to_string()],
            scope: Scope::User,
            surface: Surface::Claude,
            target: Some(target.to_path_buf()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            json: true,
        }
    }

    // REQ-YF-INSTALL-001 / REQ-YF-MARK-002 / REQ-YF-MARK-003:
    // install then status reports the skill up-to-date, complete, unmodified.
    #[test]
    fn install_then_status_round_trips_up_to_date() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let args = args_for(&skills_dir);

        super::super::install::run(&args).unwrap();

        let h = common::skill_health("yf-beads-extra", &skills_dir).unwrap();
        assert!(h.installed, "skill must be installed");
        assert!(h.up_to_date, "marker hash must equal embedded hash");
        assert!(h.complete, "all embedded files present");
        assert!(h.unmodified, "deployed tree must hash equal to embedded");
        assert_eq!(h.marker_hash.as_deref(), Some(h.embedded_hash.as_str()));
    }

    // REQ-YF-MARK-003: local tampering flips `unmodified` to false while the
    // marker (untouched) still reads up-to-date.
    #[test]
    fn tampering_a_file_marks_modified() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        super::super::install::run(&args_for(&skills_dir)).unwrap();

        // Append junk to a non-SKILL.md embedded file.
        let files = embed::skill_files("yf-beads-extra");
        let victim = files.iter().find(|f| *f != "SKILL.md").unwrap();
        let path = skills_dir.join("yf-beads-extra").join(victim);
        let mut content = std::fs::read(&path).unwrap();
        content.extend_from_slice(b"\n// tampered\n");
        std::fs::write(&path, content).unwrap();

        let h = common::skill_health("yf-beads-extra", &skills_dir).unwrap();
        assert!(h.installed && h.complete);
        assert!(!h.unmodified, "tampering must clear `unmodified`");
        assert_eq!(h.doctor_state(), "modified");
    }

    // REQ-YF-MARK-004: upgrade prunes a deployed file absent from the embedded tree.
    #[test]
    fn upgrade_prunes_stray_files() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        super::super::install::run(&args_for(&skills_dir)).unwrap();

        let stray = skills_dir.join("yf-beads-extra").join("STRAY.md");
        std::fs::write(&stray, b"orphan\n").unwrap();
        assert!(stray.exists());

        let mut up = args_for(&skills_dir);
        up.json = false;
        upgrade(&up).unwrap();

        assert!(!stray.exists(), "upgrade must prune stray files");
        // After prune the tree is unmodified again.
        let h = common::skill_health("yf-beads-extra", &skills_dir).unwrap();
        assert!(h.unmodified && h.up_to_date && h.complete);
    }

    // REQ-YF-INSTALL-006: an existing companion rule is preserved without --force.
    #[test]
    fn rule_preserved_without_force() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        // Pick a skill that ships a companion rule.
        let mut args = SkillsArgs {
            names: vec!["yf-beads-init".to_string()],
            scope: Scope::User,
            surface: Surface::Claude,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            json: true,
        };
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        super::super::install::run(&args).unwrap();

        let rules = common::embedded_rules("yf-beads-init");
        assert!(!rules.is_empty(), "yf-beads-init ships a companion rule");
        let (base, _) = &rules[0];
        let rule_path = rules_dir.join(base);
        std::fs::write(&rule_path, b"HAND EDIT\n").unwrap();

        // Re-install without --force: the hand edit survives.
        super::super::install::run(&args).unwrap();
        assert_eq!(std::fs::read(&rule_path).unwrap(), b"HAND EDIT\n");

        // With --force, it is overwritten back to the embedded source.
        args.force = true;
        super::super::install::run(&args).unwrap();
        assert_ne!(std::fs::read(&rule_path).unwrap(), b"HAND EDIT\n");
    }

    // REQ-YF-INSTALL-004: install applies the transitive depends-on-skill closure.
    #[test]
    fn install_pulls_skill_closure() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let mut args = args_for(&skills_dir);
        // yf-beads-upstream depends-on-skill: [yf-beads-extra].
        args.names = vec!["yf-beads-upstream".to_string()];
        super::super::install::run(&args).unwrap();

        assert!(skills_dir
            .join("yf-beads-upstream")
            .join("SKILL.md")
            .is_file());
        assert!(
            skills_dir.join("yf-beads-extra").join("SKILL.md").is_file(),
            "closure must deploy the dependency too"
        );
    }

    // remove deletes the deployed dir and the owned (unmodified) rule, but keeps
    // a hand-edited rule.
    #[test]
    fn remove_deletes_dir_keeps_modified_rule() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        let mut args = SkillsArgs {
            names: vec!["yf-beads-init".to_string()],
            scope: Scope::User,
            surface: Surface::Claude,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            json: true,
        };
        super::super::install::run(&args).unwrap();
        let (base, _) = &common::embedded_rules("yf-beads-init")[0];
        let rule_path = rules_dir.join(base);
        assert!(rule_path.exists());

        // Hand-edit the rule so remove must preserve it.
        std::fs::write(&rule_path, b"CUSTOM\n").unwrap();
        remove(&args).unwrap();
        assert!(!skills_dir.join("yf-beads-init").exists(), "dir removed");
        assert!(rule_path.exists(), "modified rule preserved");

        // Re-install (force) then remove: now the rule is owned and removed.
        args.force = true;
        super::super::install::run(&args).unwrap();
        remove(&args).unwrap();
        assert!(!rule_path.exists(), "owned rule removed");
    }

    // Sanity: a freshly written SKILL.md carries a parseable marker.
    #[test]
    fn deployed_skill_md_has_marker() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        super::super::install::run(&args_for(&skills_dir)).unwrap();
        let text =
            std::fs::read_to_string(skills_dir.join("yf-beads-extra").join("SKILL.md")).unwrap();
        let (v, h) = marker::parse_marker(&text).expect("deployed SKILL.md must carry a marker");
        assert_eq!(v, crate::VERSION);
        assert_eq!(h, marker::embedded_tree_hash("yf-beads-extra"));
    }
}

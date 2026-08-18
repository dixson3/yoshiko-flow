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

    for name in &sel.install {
        let extras = common::extra_deployed_files(name, &skills_dir)?;
        if args.dry_run {
            for e in &extras {
                pruned.push(format!("{name}/{e}"));
            }
            upgraded.push(name.clone());
            continue;
        }
        common::deploy_skill(
            name,
            &skills_dir,
            /*prune=*/ true,
            &args.primary_harness(),
        )?;
        for e in &extras {
            pruned.push(format!("{name}/{e}"));
        }
        upgraded.push(name.clone());
    }

    // REQ-YF-FLOW-008 (#156): upgrade is RULES-NEUTRAL. It formerly called
    // `install_rules_aggregate` here, which made it a SECOND writer of
    // YOSHIKO_FLOW.md alongside `yf harness tune` — and two writers of one path is
    // the defect: any guard or managed block `tune` places is clobbered by the
    // other writer. `tune` is now the sole writer (REQ-YF-FLOW-007 already imposed
    // this on `install`; upgrade was the remaining one).
    //
    // NOT removed from `remove()` below — see its doc comment and D-10.

    if args.json {
        let out = serde_json::json!({
            "command": "skills upgrade",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "upgraded": upgraded,
            "pruned": pruned,
            // REQ-YF-FLOW-008: upgrade writes no rules, so these report empty
            // rather than being dropped — a consumer reading them keeps working
            // and sees the honest answer (nothing written) instead of a key error.
            "flow_file": serde_json::Value::Null,
            "rules_upserted": Vec::<String>::new(),
            "rules_pruned": Vec::<String>::new(),
            "rules_migrated": Vec::<String>::new(),
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
    // REQ-YF-FLOW-008: no rules output — upgrade writes none. Tell the operator
    // where rules come from instead of silently omitting the section they used to
    // see here, so the change reads as intentional rather than as a regression.
    if !args.dry_run {
        println!("      (rules unchanged — `yf harness tune` owns YOSHIKO_FLOW.md)");
    }
    Ok(())
}

/// `yf skills remove` — delete deployed skill dirs and drop the named skills'
/// sections from the aggregate `YOSHIKO_FLOW.md`.
///
/// Rule-removal policy (C5, supersedes the old byte-match guard): a section is
/// `yf`-owned, so the named skills' sections are dropped **unconditionally** —
/// even a drifted (hand-edited) section is still `yf`'s and is removed (S3: no
/// hand-edit tolerance). "Empty" is evaluated **after** pruning those sections;
/// when no sections remain, `YOSHIKO_FLOW.md` is deleted (S6). Any legacy
/// standalone files for the removed protocols are cleaned up too (transition).
/// Non-`yf` rule files are never touched.
///
/// **Why `remove` KEEPS its rules write while `upgrade` lost one (REQ-YF-FLOW-008,
/// plan-044 D-10).** `REQ-YF-FLOW-002` reconcile-prunes on the **embedded** set, so
/// nothing else would ever drop a removed skill's section — a later `tune` would
/// retain it. Making `remove` rules-neutral too would orphan that section
/// permanently, so this write is deliberate, not an oversight.
///
/// *Honest limit:* `remove` writes the **skills-sibling** `rules/` dir, which
/// coincides with the tune-managed surface **only on claude-code**. On the other
/// four harnesses it prunes a file nothing reads while the real section survives in
/// the tune-managed surface. That residual is recorded as a follow-on, not claimed
/// fixed.
pub fn remove(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let (skills_dir, rules_dir) = common::dirs_for(args);

    let mut removed = Vec::new();
    let mut rules_removed: Vec<String> = Vec::new();
    let mut sections = common::read_flow_sections(&rules_dir);

    for name in &sel.install {
        let skill_root = skills_dir.join(name);
        if skill_root.exists() {
            if !args.dry_run {
                std::fs::remove_dir_all(&skill_root)?;
            }
            removed.push(name.clone());
        }
        // Drop every protocol this skill owns — unconditionally (C5).
        for section in common::embedded_rule_sections(name) {
            let proto = section.protocol;
            let in_aggregate = sections.iter().any(|s| s.protocol == proto);
            let standalone = rules_dir.join(&proto);
            let legacy = standalone.is_file();
            if !in_aggregate && !legacy {
                continue; // nothing installed for this protocol
            }
            if !args.dry_run {
                crate::flow::remove_section(&mut sections, &proto);
                if legacy {
                    std::fs::remove_file(&standalone)?;
                }
            }
            rules_removed.push(proto);
        }
    }

    // Write the pruned aggregate (deletes the file when no sections remain, S6).
    let flow_deleted = if args.dry_run {
        sections.is_empty()
    } else {
        common::write_flow(&rules_dir, &sections)?
    };
    let flow_file = common::flow_path(&rules_dir);

    if args.json {
        let out = serde_json::json!({
            "command": "skills remove",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "flow_file": flow_file,
            "removed": removed,
            "rules_removed": rules_removed,
            "flow_deleted": flow_deleted,
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
        println!("      {verb} rule section {base}");
    }
    if flow_deleted {
        println!("      {verb} {} (no sections remain)", flow_file.display());
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
    use crate::cli::Scope;
    use crate::{embed, marker};
    use std::path::Path;

    fn args_for(target: &Path) -> SkillsArgs {
        SkillsArgs {
            names: vec!["yf-beads-extra".to_string()],
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(target.to_path_buf()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
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

    // REQ-YF-FLOW-008 (#156): `skills upgrade` is RULES-NEUTRAL. This mirrors the
    // negative assertion install.rs already carries for `install`, and it is the
    // load-bearing one: while upgrade also wrote the aggregate there were TWO
    // writers of one path, so any guard `tune` added was clobbered by the other.
    #[test]
    fn upgrade_writes_no_rules_aggregate() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        super::super::install::run(&args_for(&skills_dir)).unwrap();

        // The rules dir sits beside the skills dir; `--target` pins skills only.
        let rules_dir = skills_dir.parent().unwrap().join("rules");

        let mut up = args_for(&skills_dir);
        up.json = false;
        upgrade(&up).unwrap();

        assert!(
            !rules_dir.join(crate::flow::FLOW_FILENAME).exists(),
            "upgrade must not write YOSHIKO_FLOW.md — `yf harness tune` is the sole writer"
        );
        assert!(
            !rules_dir.join("BEADS_INIT.md").exists(),
            "upgrade must not write a standalone rule file either"
        );
        assert!(
            !rules_dir.exists(),
            "a rules-neutral upgrade must not even create the rules dir"
        );
    }

    // REQ-YF-FLOW-004 (S3, supersedes REQ-YF-INSTALL-006): the aggregate is a fully
    // yf-managed artifact — re-running the aggregation ALWAYS rewrites the acted-on
    // section to the embedded source, with no --force needed (no hand-edit
    // tolerance). Since plan-033 install is skills-only (REQ-YF-INSTALL-008), this
    // drives the aggregation engine directly (its invocation moves to `tune`).
    #[test]
    fn rule_section_always_regenerated() {
        let tmp = tempfile::tempdir().unwrap();
        let rules_dir = tmp.path().join("rules");
        let acted = ["yf-beads-init".to_string()];
        common::install_rules_aggregate(&acted, &rules_dir, false).unwrap();

        // No standalone rule files — the rule lives only in YOSHIKO_FLOW.md.
        let flow_file = rules_dir.join(crate::flow::FLOW_FILENAME);
        assert!(flow_file.is_file(), "aggregate rule file must exist");
        assert!(
            !rules_dir.join("BEADS_INIT.md").exists(),
            "no standalone rule"
        );

        // Hand-edit the aggregate file (mangle the section body).
        let mangled = std::fs::read_to_string(&flow_file)
            .unwrap()
            .replace("# Beads", "# HAND EDIT");
        std::fs::write(&flow_file, &mangled).unwrap();

        // Re-run WITHOUT --force: the section is regenerated to embedded (S3).
        common::install_rules_aggregate(&acted, &rules_dir, false).unwrap();
        let after = std::fs::read_to_string(&flow_file).unwrap();
        let sections = crate::flow::parse(&after);
        let body = &sections
            .iter()
            .find(|s| s.protocol == "BEADS_INIT.md")
            .unwrap()
            .body;
        let embedded = common::embedded_rules("yf-beads-init")
            .into_iter()
            .find(|(p, _)| p == "BEADS_INIT.md")
            .unwrap()
            .1;
        assert_eq!(
            body.as_bytes(),
            embedded.as_slice(),
            "section restored to embedded"
        );
        assert!(
            !after.contains("# HAND EDIT"),
            "hand edit overwritten without --force"
        );
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

    // REQ-YF-FLOW (C5): remove drops the named skill's section UNCONDITIONALLY —
    // even a drifted (hand-edited) section — and deletes YOSHIKO_FLOW.md once its
    // last section is gone (S6).
    #[test]
    fn remove_drops_section_unconditionally_and_deletes_empty_file() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        let args = SkillsArgs {
            names: vec!["yf-beads-init".to_string()],
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
            json: true,
        };
        super::super::install::run(&args).unwrap();
        // plan-033: install is skills-only, so deploy the aggregate rules surface
        // separately (its invocation moves to `tune`) to set up the remove test.
        common::install_rules_aggregate(&["yf-beads-init".to_string()], &rules_dir, false).unwrap();
        let flow_file = rules_dir.join(crate::flow::FLOW_FILENAME);
        assert!(flow_file.is_file());

        // Drift the section (hand edit) — remove must drop it anyway.
        let mangled = std::fs::read_to_string(&flow_file)
            .unwrap()
            .replace("Protocol", "DRIFT");
        std::fs::write(&flow_file, mangled).unwrap();

        remove(&args).unwrap();
        assert!(
            !skills_dir.join("yf-beads-init").exists(),
            "skill dir removed"
        );
        // yf-beads-init was the only rule-bearing skill installed → file deleted.
        assert!(!flow_file.exists(), "empty aggregate deleted (S6)");
    }

    // REQ-YF-FLOW (C5/S6): removing one of several skills drops only its section;
    // the file survives with the remaining sections.
    #[test]
    fn remove_one_keeps_others() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        let base_args = |names: Vec<String>| SkillsArgs {
            names,
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
            json: true,
        };
        // Install two rule-bearing skills.
        super::super::install::run(&base_args(vec![
            "yf-beads-init".to_string(),
            "yf-plan".to_string(),
        ]))
        .unwrap();
        // plan-033: install is skills-only — deploy the aggregate rules surface
        // separately (its invocation moves to `tune`) for the remove test.
        common::install_rules_aggregate(
            &["yf-beads-init".to_string(), "yf-plan".to_string()],
            &rules_dir,
            false,
        )
        .unwrap();
        let flow_file = rules_dir.join(crate::flow::FLOW_FILENAME);

        // Remove only yf-plan.
        remove(&base_args(vec!["yf-plan".to_string()])).unwrap();
        assert!(flow_file.is_file(), "file survives with remaining section");
        let sections = crate::flow::parse(&std::fs::read_to_string(&flow_file).unwrap());
        let protos: Vec<&str> = sections.iter().map(|s| s.protocol.as_str()).collect();
        assert!(protos.contains(&"BEADS_INIT.md"), "other section kept");
        assert!(!protos.contains(&"PLANS.md"), "removed section dropped");
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

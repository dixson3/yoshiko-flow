//! `yf skills install` (bead 1.5).
//!
//! Copies each selected skill's embedded tree to the resolved skills dir and its
//! companion rules to the resolved rules dir, injecting the integrity marker into
//! every deployed `SKILL.md` (REQ-YF-INSTALL-001/005/006, REQ-YF-MARK-002).

use anyhow::Result;

use super::common;
use crate::cli::SkillsArgs;
use crate::frontmatter;

/// Run `yf skills install`.
pub fn run(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    if skills.is_empty() {
        anyhow::bail!("no skills embedded in this binary");
    }

    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let install: Vec<String> = sel.install.iter().cloned().collect();
    let (skills_dir, rules_dir) = common::dirs_for(args);

    // Tool prereqs (REQ-YF-INSTALL-005: --strict aborts on a missing tool).
    let missing = common::missing_tools(&skills, &sel.install);
    if !missing.is_empty() && args.strict {
        if args.json {
            let out = serde_json::json!({
                "command": "skills install",
                "status": "error",
                "error": "missing required tools (--strict)",
                "missing_tools": missing,
                "selected": install,
            });
            println!("{}", serde_json::to_string(&out)?);
        }
        anyhow::bail!(
            "--strict: missing required tool(s) on PATH: {}",
            missing.join(", ")
        );
    }

    let mut installed: Vec<String> = Vec::new();
    let mut rules_written: Vec<String> = Vec::new();
    let mut rules_kept: Vec<String> = Vec::new();

    if !args.dry_run {
        for name in &install {
            common::deploy_skill(name, &skills_dir, /*prune=*/ false)?;
            installed.push(name.clone());
            let (written, kept) = common::install_rules(name, &rules_dir, args.force)?;
            rules_written.extend(written);
            rules_kept.extend(kept);
        }
    }

    if args.json {
        let out = serde_json::json!({
            "command": "skills install",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "selected": install,
            "installed": installed,
            "rules_written": rules_written,
            "rules_kept": rules_kept,
            "missing_tools": missing,
            "warnings": sel.log,
        });
        println!("{}", serde_json::to_string(&out)?);
        return Ok(());
    }

    println!(
        "Skills to install ({}): {}",
        install.len(),
        install.join(", ")
    );
    for line in &sel.log {
        println!("{line}");
    }
    if !missing.is_empty() {
        println!("Missing tool(s) on PATH: {}", missing.join(", "));
        println!("  warning: installing anyway — these skills are inert until present.");
    }
    if args.dry_run {
        println!("(dry run — nothing written)");
        for name in &install {
            println!("  would install {name} -> {}", skills_dir.join(name).display());
            for (base, _) in common::embedded_rules(name) {
                println!("      would surface rule {base} -> {}", rules_dir.join(&base).display());
            }
        }
        return Ok(());
    }

    for name in &installed {
        println!("  OK: {name} -> {}", skills_dir.join(name).display());
    }
    for base in &rules_written {
        println!("      rule {base} -> {}", rules_dir.join(base).display());
    }
    for base in &rules_kept {
        println!("      rule {base}: kept (exists; --force to overwrite)");
    }
    println!();
    println!("Installed {} skill(s) -> {}", installed.len(), skills_dir.display());
    Ok(())
}

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

    if !args.dry_run {
        for name in &install {
            common::deploy_skill(name, &skills_dir, /*prune=*/ false)?;
            installed.push(name.clone());
        }
    }
    // S3: companion rules surface as one aggregated YOSHIKO_FLOW.md. Upsert the
    // acted-on skills' sections, fold in any legacy standalones, then
    // reconcile-prune. There is no force/kept gate (S3: always rewrite). On
    // --dry-run the same projection is computed but nothing is written (C3).
    let flow = common::install_rules_aggregate(&install, &rules_dir, args.dry_run)?;

    // plan-032: optional post-install settings tune (REQ-YF-TUNE-010). Runs only
    // on a real (non-dry-run) install and only under --tune. There is NO
    // interactive prompt; without --tune, tuning is merely advertised and no
    // settings.json is touched. Scope tracks the install scope (project → local).
    let project = matches!(args.scope, crate::cli::Scope::Project);
    let tune_result: Option<serde_json::Value> = if args.tune && !args.dry_run {
        Some(crate::cmd::harness::tune_for_install(project)?)
    } else {
        None
    };

    if args.json {
        let out = serde_json::json!({
            "command": "skills install",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "flow_file": flow.flow_file,
            "selected": install,
            "installed": installed,
            "rules_upserted": flow.upserted,
            "rules_pruned": flow.pruned,
            "rules_migrated": flow.migrated,
            "missing_tools": missing,
            "warnings": sel.log,
            "tune": tune_result,
            "tune_available": !args.tune,
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
            println!(
                "  would install {name} -> {}",
                skills_dir.join(name).display()
            );
        }
        for base in &flow.upserted {
            println!(
                "      would surface rule section {base} -> {}",
                flow.flow_file.display()
            );
        }
        for base in &flow.migrated {
            println!(
                "      would migrate standalone {base} -> {}",
                flow.flow_file.display()
            );
        }
        for base in &flow.pruned {
            println!("      would prune section {base}");
        }
        return Ok(());
    }

    for name in &installed {
        println!("  OK: {name} -> {}", skills_dir.join(name).display());
    }
    for base in &flow.upserted {
        println!("      rule section {base} -> {}", flow.flow_file.display());
    }
    for base in &flow.migrated {
        println!(
            "      migrated standalone {base} -> {}",
            flow.flow_file.display()
        );
    }
    for base in &flow.pruned {
        println!("      pruned section {base} (no longer embedded)");
    }
    println!();
    println!(
        "Installed {} skill(s) -> {}",
        installed.len(),
        skills_dir.display()
    );
    match &tune_result {
        Some(t) => {
            let status = t.get("status").and_then(|v| v.as_str()).unwrap_or("?");
            let path = t.get("path").and_then(|v| v.as_str()).unwrap_or("");
            println!("Harness tune: {status} {path}");
        }
        None if !args.dry_run => {
            println!("Tip: run `yf harness tune` (or re-install with --tune) to align settings to the yf skill contracts.");
        }
        None => {}
    }
    Ok(())
}

//! `yf harness skills install` (bead 1.5; skills-only since plan-033 Issue 2.2).
//!
//! Copies each selected skill's embedded tree to every resolved (deduped) skills
//! destination, injecting the integrity marker into each deployed `SKILL.md`
//! (REQ-YF-INSTALL-001/002/005/007/008, REQ-YF-MARK-002).
//!
//! Install is **skills-only** (REQ-YF-INSTALL-008 / REQ-YF-FLOW-007): it writes
//! skill bodies only — no `rules/` surface, no `YOSHIKO_FLOW.md`. The always-loaded
//! aggregated ruleset is deployed by `yf harness tune`. A bare install without
//! `--tune` warns (to stderr) that it was skills-only and its success output states
//! rules were not deployed.

use anyhow::Result;

use super::common;
use crate::cli::SkillsArgs;
use crate::frontmatter;

/// The skills-only warning emitted to stderr on a bare install (no `--tune`)
/// (REQ-YF-INSTALL-008, F5).
pub(crate) const SKILLS_ONLY_WARNING: &str =
    "warning: skills-only — run `yf harness tune` to deploy always-loaded rules";

/// The success-output notice stating rules were not deployed (REQ-YF-INSTALL-008).
pub(crate) const RULES_NOT_DEPLOYED_NOTICE: &str = "Rules were NOT deployed (skills-only).";

/// Run `yf harness skills install`.
pub fn run(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    if skills.is_empty() {
        anyhow::bail!("no skills embedded in this binary");
    }

    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    let install: Vec<String> = sel.install.iter().cloned().collect();
    // Repeatable `--harness` resolved and deduped by resolved absolute path
    // (REQ-YF-INSTALL-002): `--harness codex --harness agents` → one destination.
    let dests = common::resolved_dests(args);

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

    // REQ-YF-INSTALL-008 / REQ-YF-FLOW-007: skills-only. Deploy skill bodies to
    // every deduped destination; pi's name_transform is applied inside
    // `deploy_skill`. NO rules are written here — the aggregated `YOSHIKO_FLOW.md`
    // is owned by `yf harness tune` (Issue 3.1).
    if !args.dry_run {
        for d in &dests {
            for name in &install {
                common::deploy_skill(name, &d.skills_dir, /*prune=*/ false, &d.harness)?;
            }
        }
    }

    // plan-033 Issue 7.2: the `--tune` opt-in bridge (REQ-YF-TUNE-023). With
    // `--tune`, also run `yf harness tune` (both sub-operations) for the SAME
    // resolved harness set install acted on. Without `--tune`, install stays
    // skills-only (the block below is skipped, and the skills-only warning fires).
    // The no-`--harness --tune` multi-harness auto path is bounded-blast-radius
    // gated (F6) — see `compute_tune_bridge`.
    let project = matches!(args.scope, crate::cli::Scope::Project);
    let tune_result: Option<serde_json::Value> = compute_tune_bridge(args, project)?;

    // F5 (REQ-YF-INSTALL-008): a bare install without `--tune` is skills-only.
    // Warn to stderr (kept off `--json` stdout) that no rules were deployed.
    let skills_only = !args.tune;
    if skills_only {
        eprintln!("{SKILLS_ONLY_WARNING}");
    }

    if args.json {
        let destinations: Vec<serde_json::Value> = dests
            .iter()
            .map(|d| {
                serde_json::json!({
                    "harness": d.harness,
                    "skills_dir": d.skills_dir,
                })
            })
            .collect();
        let out = serde_json::json!({
            "command": "skills install",
            "status": if args.dry_run { "dry_run" } else { "ok" },
            "destinations": destinations,
            "skills_dir": dests.first().map(|d| d.skills_dir.clone()),
            "selected": install,
            "installed": if args.dry_run { Vec::new() } else { install.clone() },
            // Install itself writes no rules; the `--tune` bridge does. `true` only
            // once the bridge actually ran to completion (status "ok").
            "rules_deployed": tune_result
                .as_ref()
                .and_then(|t| t.get("status"))
                .and_then(|v| v.as_str())
                == Some("ok"),
            "skills_only": skills_only,
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
        for d in &dests {
            for name in &install {
                let dir_name = crate::harness_desc::lookup(&d.harness)
                    .map(|h| h.transform_skill_name(name))
                    .unwrap_or_else(|| name.clone());
                println!(
                    "  would install {name} ({}) -> {}",
                    d.harness,
                    d.skills_dir.join(&dir_name).display()
                );
            }
        }
        println!("(skills-only — rules are not deployed by install)");
        if let Some(t) = &tune_result {
            println!("(--tune dry-run — projected tune targets, nothing written)");
            render_tune_bridge_human(t);
        }
        return Ok(());
    }

    for d in &dests {
        for name in &install {
            let dir_name = crate::harness_desc::lookup(&d.harness)
                .map(|h| h.transform_skill_name(name))
                .unwrap_or_else(|| name.clone());
            println!(
                "  OK: {name} ({}) -> {}",
                d.harness,
                d.skills_dir.join(&dir_name).display()
            );
        }
    }
    println!();
    println!(
        "Installed {} skill(s) into {} destination(s).",
        install.len(),
        dests.len()
    );
    match &tune_result {
        // `--tune` bridge ran (or surfaced): render the per-harness verdict.
        Some(t) => render_tune_bridge_human(t),
        // Skills-only (no `--tune`): state rules were NOT deployed and how to fix.
        None => {
            // REQ-YF-INSTALL-008: the success output states rules were NOT deployed.
            println!("{RULES_NOT_DEPLOYED_NOTICE}");
            println!(
                "Run `yf harness tune` (or re-install with --tune) to deploy the always-loaded \
                 rules and align settings to the yf skill contracts."
            );
        }
    }
    Ok(())
}

/// Render the `--tune` bridge result in human mode: the surfaced blast radius when
/// confirmation is required, else the per-harness tune status.
fn render_tune_bridge_human(t: &serde_json::Value) {
    let status = t.get("status").and_then(|v| v.as_str()).unwrap_or("?");
    if status == "confirmation_required" {
        println!("{RULES_NOT_DEPLOYED_NOTICE}");
        println!(
            "Multiple harnesses were auto-detected — `--tune` would write to ALL of them. \
             Re-run with an explicit `--harness <name>` or `--yes` to proceed."
        );
        println!("Resolved tune targets (nothing written):");
        for target in t
            .get("targets")
            .and_then(|v| v.as_array())
            .map(Vec::as_slice)
            .unwrap_or_default()
        {
            let h = target
                .get("harness")
                .and_then(|v| v.as_str())
                .unwrap_or("?");
            let cfg = target.get("config").and_then(|v| v.as_str());
            let rules = target.get("rules").and_then(|v| v.as_str());
            println!(
                "  {h}: config={} rules={}",
                cfg.unwrap_or("(none)"),
                rules.unwrap_or("(none)")
            );
        }
        return;
    }
    println!("Harness tune ({status}):");
    for h in t
        .get("harnesses")
        .and_then(|v| v.as_array())
        .map(Vec::as_slice)
        .unwrap_or_default()
    {
        let name = h.get("harness").and_then(|v| v.as_str()).unwrap_or("?");
        let cfg = h
            .get("config")
            .and_then(|c| c.get("status"))
            .and_then(|v| v.as_str())
            .unwrap_or("?");
        let rules = h
            .get("rules")
            .and_then(|r| r.get("kind"))
            .and_then(|v| v.as_str())
            .unwrap_or("?");
        println!("  {name}: config={cfg} rules={rules}");
    }
}

/// Compute the `--tune` opt-in bridge result (REQ-YF-TUNE-023), or `None` when
/// `--tune` was not given (install stays skills-only, separable). With `--tune`
/// the bridge runs `yf harness tune` (both sub-operations) for the SAME resolved
/// harness set install acted on ([`common::effective_harnesses`]).
///
/// **Bounded blast radius (F6).** The no-`--harness --tune` MULTI-harness auto
/// path must not silently fan out config/rule writes to every detected harness.
/// When [`bridge_requires_confirmation`] holds and `--yes` was not given, the
/// bridge SURFACES the resolved target set and writes nothing unless confirmed:
/// under `--json` or a non-interactive stdin it refuses to fan out (a
/// `confirmation_required` surface); an interactive session is resolved by a y/N
/// prompt. An explicit `--harness`/`--surface`/`--target`, a single detected
/// harness, or `--yes` all bypass the gate. `--dry-run` always surfaces without
/// writing.
fn compute_tune_bridge(args: &SkillsArgs, project: bool) -> Result<Option<serde_json::Value>> {
    if !args.tune {
        return Ok(None);
    }
    let harnesses = common::effective_harnesses(args);

    // Dry-run: project the writes for every harness, write nothing.
    if args.dry_run {
        return Ok(Some(crate::cmd::harness::tune_for_install_harnesses(
            &harnesses, project, /*dry_run=*/ true,
        )?));
    }

    if bridge_requires_confirmation(args, &harnesses) && !args.yes {
        let plan = crate::cmd::harness::plan_targets(&harnesses, project)?;
        // Refuse to fan out in `--json` / non-interactive contexts (the
        // "default to refuse rather than block on stdin" contract); an
        // interactive human is asked to confirm.
        let interactive = !args.json && std::io::IsTerminal::is_terminal(&std::io::stdin());
        let proceed = interactive && prompt_blast_radius(&plan);
        if !proceed {
            return Ok(Some(serde_json::json!({
                "status": "confirmation_required",
                "reason": "multi-harness auto-detected; re-run with --harness or --yes",
                "harnesses": harnesses,
                "targets": crate::cmd::harness::target_plan_json(&plan),
            })));
        }
    }

    Ok(Some(crate::cmd::harness::tune_for_install_harnesses(
        &harnesses, project, /*dry_run=*/ false,
    )?))
}

/// The bounded-blast-radius gate (F6): the `--tune` bridge requires confirmation
/// iff the harness set was **auto-detected** (no explicit `--harness`/`--surface`/
/// `--target`) AND resolves to **more than one** harness — the multi-harness auto
/// path that would otherwise fan out writes to every detected harness. An explicit
/// selection is a deliberate operator choice and never triggers the gate.
fn bridge_requires_confirmation(args: &SkillsArgs, harnesses: &[String]) -> bool {
    let auto_detected = args.harness.is_empty() && args.surface.is_none() && args.target.is_none();
    auto_detected && harnesses.len() > 1
}

/// Print the resolved target set and read a y/N confirmation from stdin (default
/// No). Interactive path only — `--json`/non-interactive callers never reach here.
fn prompt_blast_radius(plan: &[crate::cmd::harness::TargetPlan]) -> bool {
    eprintln!(
        "`--tune` with no `--harness` auto-detected {} harnesses. It will write config \
         and rules to ALL of them:",
        plan.len()
    );
    for t in plan {
        let cfg = t
            .config
            .as_ref()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "(no config profile)".to_string());
        let rules = t
            .rules
            .as_ref()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "(no rule target)".to_string());
        eprintln!("  {}: config={cfg} rules={rules}", t.harness);
    }
    eprint!("Proceed and tune all detected harnesses? [y/N] ");
    use std::io::Write;
    let _ = std::io::stderr().flush();
    let mut line = String::new();
    if std::io::stdin().read_line(&mut line).is_err() {
        return false;
    }
    matches!(line.trim().to_ascii_lowercase().as_str(), "y" | "yes")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::Scope;
    use std::path::Path;

    fn args_for(target: &Path) -> SkillsArgs {
        SkillsArgs {
            names: vec!["yf-beads-init".to_string()],
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(target.to_path_buf()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            tune: false,
            yes: false,
            json: true,
        }
    }

    // REQ-YF-TUNE-023 (Issue 7.2): install/tune separability + the bounded
    // blast-radius gate. (1) Without `--tune` the bridge does not run at all —
    // install stays skills-only, so install and tune are separable. (2) The
    // no-`--harness --tune` MULTI-harness auto path requires confirmation before
    // any write; an explicit `--harness`, a single detected harness, or `--yes`
    // all bypass the gate. Detection is exercised through injected HOME/PATH for
    // hermeticity.
    #[test]
    fn tune_bridge_opt_in_and_confirmation_gate() {
        use crate::harness_detect;
        use std::ffi::OsString;

        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");

        // (1) Separability: no `--tune` → the bridge does not run (returns None),
        // and it short-circuits before touching the environment.
        let skills_only = args_for(&skills_dir);
        assert!(!skills_only.tune, "the default install has no --tune");
        assert!(
            compute_tune_bridge(&skills_only, false).unwrap().is_none(),
            "no --tune → bridge does not run (install/tune separable)"
        );

        // (2) Hermetic multi-harness detection: seed ~/.codex and ~/.config/opencode
        // under a sandboxed HOME with an EMPTY injected PATH (no host leakage).
        let home = tmp.path().join("home");
        std::fs::create_dir_all(home.join(".codex")).unwrap();
        std::fs::create_dir_all(home.join(".config/opencode")).unwrap();
        let empty = OsString::new();
        let detected = harness_detect::detect(Scope::User, &home, &home, Some(empty.as_os_str()));
        assert!(
            detected.len() > 1,
            "seeded HOME must detect multiple harnesses: {detected:?}"
        );

        // A no-`--harness --tune` install auto-detects that multi set → the gate
        // fires (the bridge must surface + confirm, never silently fan out).
        let mut auto = args_for(&skills_dir);
        auto.target = None;
        auto.harness = Vec::new();
        auto.tune = true;
        assert!(
            bridge_requires_confirmation(&auto, &detected),
            "no-`--harness` multi-harness auto path must require confirmation"
        );

        // The projected target set the gate would surface is READ-ONLY: computing
        // it writes nothing to the detected harnesses' config/rule paths.
        let plan = crate::cmd::harness::plan_targets(&detected, false).unwrap();
        assert_eq!(
            plan.len(),
            detected.len(),
            "one target row per detected harness"
        );

        // A single detected harness does not fan out → no gate.
        assert!(
            !bridge_requires_confirmation(&auto, &detected[..1]),
            "a single detected harness must not require confirmation"
        );

        // An explicit `--harness` selection is a deliberate operator choice → no gate.
        let mut explicit = args_for(&skills_dir);
        explicit.target = None;
        explicit.harness = detected.clone();
        explicit.tune = true;
        assert!(
            !bridge_requires_confirmation(&explicit, &detected),
            "explicit --harness must bypass the confirmation gate"
        );

        // `--yes` bypasses the gate even on the auto multi-harness path (the gate
        // still *reports required* — the bypass is applied in compute_tune_bridge).
        let mut yes = auto;
        yes.yes = true;
        assert!(
            bridge_requires_confirmation(&yes, &detected) && yes.yes,
            "the gate condition is orthogonal to --yes; --yes is the bypass lever"
        );
    }

    // REQ-YF-INSTALL-008 / REQ-YF-FLOW-007: a skills-only install deploys skill
    // bodies but touches NO rules surface — no `YOSHIKO_FLOW.md` and no standalone
    // rule file is written even for a rule-bearing skill.
    #[test]
    fn install_writes_no_rules() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        // yf-beads-init is rule-bearing (BEADS_INIT.md) — the old install would
        // have written it; skills-only must not.
        run(&args_for(&skills_dir)).unwrap();

        assert!(
            skills_dir.join("yf-beads-init").join("SKILL.md").is_file(),
            "skill body deployed"
        );
        assert!(
            !rules_dir.join(crate::flow::FLOW_FILENAME).exists(),
            "install must not write YOSHIKO_FLOW.md"
        );
        assert!(
            !rules_dir.join("BEADS_INIT.md").exists(),
            "install must not write a standalone rule file"
        );
        // The whole rules dir is never created by a skills-only install.
        assert!(!rules_dir.exists(), "install must not create the rules dir");
    }

    // REQ-YF-INSTALL-008 (F5): the bare-install skills-only warning names the
    // `yf harness tune` remediation, and the success notice states rules were not
    // deployed. A bare install (no `--tune`) fires both; both output paths (json /
    // human) run without error against a rule-bearing skill.
    #[test]
    fn bare_install_emits_skills_only_warning_and_rules_not_deployed_notice() {
        // The skills-only warning is the stderr text F5 requires.
        assert!(
            SKILLS_ONLY_WARNING.contains("skills-only")
                && SKILLS_ONLY_WARNING.contains("yf harness tune")
                && SKILLS_ONLY_WARNING.contains("always-loaded rules"),
            "warning must point at `yf harness tune` for always-loaded rules"
        );
        // The success output states rules were NOT deployed.
        assert!(
            RULES_NOT_DEPLOYED_NOTICE.contains("NOT deployed"),
            "success notice must state rules were not deployed"
        );

        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        // A bare install has no `--tune`, so it is skills-only and fires the
        // warning path; exercise both the json and human success paths.
        let bare = args_for(&skills_dir);
        assert!(!bare.tune, "bare install has no --tune → skills-only");
        assert!(run(&bare).is_ok());
        let mut human = args_for(&skills_dir);
        human.json = false;
        assert!(run(&human).is_ok());
    }
}

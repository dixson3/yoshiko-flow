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

/// Warnings for the two **silent** failure modes `REQ-YF-INSTALL-011` governs.
///
/// ## 1. The replace-semantics override mismatch
///
/// Measured (plan-055 EXP-003): with `CODEX_HOME` / `PI_CODING_AGENT_DIR` / `CLAUDE_CONFIG_DIR`
/// exported, yf's `$HOME`-relative write lands where the harness **no longer reads**. What makes
/// it worth a requirement is that it is *silent*: the default directory still exists and still
/// looks correct on disk, so nothing about the result says anything is wrong.
///
/// yf **warns rather than resolving** the surface column (D-13) — the skills column is resolved
/// for claude-code alone. A warning naming the directory the harness will actually read is the
/// whole remedy, at a fraction of the cost of a full env resolver.
///
/// ## 2. Project-scope `.agents/skills` creation
///
/// Creating `<repo>/.agents/skills` makes the repository **trust-requiring for pi**, and pi's
/// project-scope gate then drops those skills with **no diagnostic whatsoever** — measured: no
/// stderr, no event, exit 0 under `-p` / `--mode json`. The warning fires at the moment yf
/// creates the directory, which is the only moment at which anyone is looking.
///
/// Both return `Vec<String>` rather than printing, so they are unit-testable without capturing
/// stderr — the check is on the *message*, and a message asserted through a pipe is a test of
/// the pipe.
pub(crate) fn override_mismatch_warnings(
    scope: crate::cli::Scope,
    harnesses: &[String],
    home: &std::path::Path,
    env: impl Fn(&str) -> Option<std::ffi::OsString>,
) -> Vec<String> {
    use crate::harness_desc::{self, OverridePrecedence};
    let mut out = Vec::new();
    for h in harnesses {
        let Some(d) = harness_desc::lookup(h) else {
            continue;
        };
        for ov in d.surface_env {
            // ADDITIVE overrides are NOT a mismatch and must never warn. An additive var adds a
            // root the harness reads *in addition to* the default, so the default is still read
            // and yf's write still lands somewhere the harness looks. Warning on it would train
            // an operator to ignore the warning that matters.
            if ov.precedence != OverridePrecedence::Replace {
                continue;
            }
            let Some(v) = env(ov.var) else { continue };
            if v.is_empty() {
                continue;
            }
            let overridden = std::path::PathBuf::from(&v);
            let default = home.join(d.surface_dir(scope));
            if overridden != default {
                out.push(format!(
                    "warning: {} is set to {} but yf writes {}'s surface to {} — {} will \
                     actually read {}. yf does not follow this override; move the files or \
                     unset the variable.",
                    ov.var,
                    overridden.display(),
                    d.id,
                    default.display(),
                    d.id,
                    overridden.display(),
                ));
            }
        }
    }
    out
}

/// `REQ-YF-INSTALL-011` (2): warn when yf CREATES a project-scope `.agents/skills`.
///
/// Keyed on **creation**, not on presence: a directory that already existed was already making
/// the repo trust-requiring, and yf did not do it. Warning on presence would fire on every
/// subsequent install forever, which is how a real warning becomes noise.
pub(crate) fn project_scope_trust_warning(created: &std::path::Path) -> String {
    format!(
        "warning: created {} — this makes the repository TRUST-REQUIRING for pi. Until a pi \
         trust decision covers this repo, headless pi (`-p` / `--mode json`) DROPS these skills \
         SILENTLY: no stderr, no event, exit 0. Run `yf doctor` for the trust axis.",
        created.display()
    )
}

/// Run `yf harness skills install`.
pub fn run(args: &SkillsArgs) -> Result<()> {
    let skills = frontmatter::load_skills();
    if skills.is_empty() {
        anyhow::bail!("no skills embedded in this binary");
    }

    let sel = common::resolve_selection(&skills, &args.names, args.group.as_deref())?;
    // `--no-skills` (Issue 2.5): run the `--tune` bridge and deploy NO bodies. The selection is
    // still computed, so the reporting shape is unchanged and the caller sees which skills WOULD
    // have been written by the run that owns this root.
    let install: Vec<String> = if args.no_skills {
        Vec::new()
    } else {
        sel.install.iter().cloned().collect()
    };
    // Repeatable `--harness` resolved and deduped by resolved absolute path
    // (REQ-YF-INSTALL-002): `--harness codex --harness agents` → one destination.
    let dests = common::resolved_dests(args);

    // REQ-YF-INSTALL-011 (2): keyed on CREATION, so the predicate must be sampled BEFORE the
    // deploy. A directory that already existed was already making the repo trust-requiring and
    // yf did not do it; warning on mere presence would fire on every install forever, which is
    // how a real warning becomes noise.
    let newly_created_shared_roots: Vec<std::path::PathBuf> =
        if matches!(args.scope, crate::cli::Scope::Project) {
            dests
                .iter()
                .map(|d| d.skills_dir.clone())
                .filter(|p| p.ends_with(".agents/skills") && !p.exists())
                .collect()
        } else {
            Vec::new()
        };

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
    // REQ-YF-INSTALL-010 (plan-044 #155): `--prune` is OPT-IN on install (it is
    // default-on for upgrade). Prune fans out across `dests` for free because it
    // runs inside `deploy_skill`, once per destination.
    let mut pruned: Vec<(String, String)> = Vec::new(); // (harness, "skill/relpath")
    if args.prune && args.dry_run {
        // Dry-run: the deploy loop below is skipped, so project the set here —
        // through the SAME helper the apply path uses, so the two cannot diverge.
        for d in &dests {
            for name in &install {
                for e in common::extra_deployed_files(name, &d.skills_dir, &d.harness)? {
                    pruned.push((d.harness.clone(), format!("{name}/{e}")));
                }
            }
        }
    }
    if !args.dry_run {
        for d in &dests {
            for name in &install {
                // Compute the set BEFORE deploying: `deploy_skill(prune=true)`
                // removes exactly these, so asking afterwards always returns empty.
                if args.prune {
                    for e in common::extra_deployed_files(name, &d.skills_dir, &d.harness)? {
                        pruned.push((d.harness.clone(), format!("{name}/{e}")));
                    }
                }
                common::deploy_skill(name, &d.skills_dir, /*prune=*/ args.prune, &d.harness)?;
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

    // REQ-YF-INSTALL-011 (1): a replace-semantics override that disagrees with the
    // `$HOME`-derived default yf writes to. Silent otherwise — the default dir still exists and
    // looks correct — so the warning IS the remedy (D-13).
    {
        let home = std::env::var_os("HOME")
            .map(std::path::PathBuf::from)
            .unwrap_or_default();
        let harnesses: Vec<String> = dests.iter().map(|d| d.harness.clone()).collect();
        for w in override_mismatch_warnings(args.scope, &harnesses, &home, |k| std::env::var_os(k))
        {
            eprintln!("{w}");
        }
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
            // REQ-YF-INSTALL-010: the per-destination prune set. Populated on a
            // real `--prune` run; on `--dry-run --prune` it is the PROJECTED set,
            // computed the same way, so preview and apply cannot disagree.
            "pruned": pruned
                .iter()
                .map(|(h, f)| serde_json::json!({ "harness": h, "file": f }))
                .collect::<Vec<_>>(),
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
        // REQ-YF-INSTALL-010: the dry-run block computed NO extras before, so
        // `--dry-run --prune` reported nothing while a real run removed files.
        // The preview is the evidence the operator consents on, so it must be
        // complete and per-destination.
        if args.prune {
            if pruned.is_empty() {
                println!("  would prune: nothing (no extra deployed files)");
            }
            for (h, f) in &pruned {
                println!("  would prune ({h}) {f}");
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
    // REQ-YF-INSTALL-011 (2): fires only for a root this run actually created.
    for created in &newly_created_shared_roots {
        if created.exists() {
            eprintln!("{}", project_scope_trust_warning(created));
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
            &harnesses,
            project,
            /*dry_run=*/ true,
            args.rules_only,
            args.allow_permissions_write,
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
        &harnesses,
        project,
        /*dry_run=*/ false,
        args.rules_only,
        args.allow_permissions_write,
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

    // REQ-YF-INSTALL-010 (plan-044 Issue 2.11a, #155): a hand-added skill
    // DIRECTORY survives a `--prune` install.
    //
    // Prune operates on FILES, so a directory the operator added stays. This is the
    // operator-file hazard the sandbox probe confirmed was real, not theoretical —
    // and it is why prune is opt-in on install rather than default-on.
    #[test]
    fn prune_install_keeps_a_hand_added_skill_directory() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        run(&args_for(&skills_dir)).unwrap();

        // An operator's own skill dir, entirely outside the embedded set.
        let mine = skills_dir.join("my-own-skill");
        std::fs::create_dir_all(&mine).unwrap();
        std::fs::write(mine.join("SKILL.md"), b"mine\n").unwrap();

        let mut a = args_for(&skills_dir);
        a.prune = true;
        a.json = false;
        run(&a).unwrap();

        assert!(
            mine.join("SKILL.md").is_file(),
            "a hand-added skill DIRECTORY must survive --prune"
        );
    }

    // REQ-YF-INSTALL-010 (plan-044 Issue 2.11c): `extra_deployed_files` resolves the
    // deployed dir through the SAME name transform `deploy_skill` uses.
    //
    // HONEST SCOPE: this defect is currently LATENT. pi's transform
    // (`lowercase-hyphen,max64`) is the IDENTITY for all 20 shipped skill names —
    // every one is already lowercase-hyphen and under 64 chars — so on today's tree
    // the raw and transformed paths coincide and the bug cannot manifest. The
    // symptom exp-004 attributed to it (a `--dry-run --prune` set of empty) was
    // really install's dry-run block computing no extras at all, which Issue 2.9
    // fixes. Both were real; the causal attribution was not.
    //
    // It is still worth fixing and pinning: two functions deriving the same path by
    // different rules is a correctness bug that becomes live the moment a skill name
    // needs transforming. This test uses a synthetic transforming name so the
    // invariant is checked rather than accidentally satisfied.
    #[test]
    fn extra_deployed_files_resolves_through_the_harness_name_transform() {
        use crate::harness_desc;
        let pi = harness_desc::lookup("pi").expect("pi descriptor");
        let raw = "YF_Mixed_Case";
        let transformed = pi.transform_skill_name(raw);
        // plan-055 Issue 2.3: NO row carries a transform any more, so this is now the identity.
        // The test is kept — and re-pointed rather than deleted — because what it guards is the
        // ROUTING, not the transform: `extra_deployed_files` must resolve its skill root the
        // same way `deploy_skill` writes it. Two functions deriving a directory name by
        // different rules is a correctness bug the moment a future harness declares a transform,
        // and that is exactly when nobody will be looking.
        assert_eq!(
            transformed, raw,
            "no shipped row transforms names (Issue 2.3); this is the identity now"
        );

        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path();
        // Deployed under the resolved dir name, as deploy_skill would write it.
        let root = skills_dir.join(&transformed);
        std::fs::create_dir_all(&root).unwrap();
        std::fs::write(root.join("STRAY.md"), b"orphan\n").unwrap();

        let found = common::extra_deployed_files(raw, skills_dir, "pi").unwrap();
        assert_eq!(
            found,
            vec!["STRAY.md".to_string()],
            "must look in the TRANSFORMED dir; joining the raw name finds nothing \
             and reports an empty prune set"
        );

        // Every harness resolves the same directory now, because every row is the identity.
        // (Before Issue 2.3 this half used a SEPARATE raw-named directory, because pi and
        // claude-code resolved to two different paths for one skill name. They no longer do —
        // which is itself the assertion.)
        assert_eq!(
            common::extra_deployed_files(raw, skills_dir, "claude-code").unwrap(),
            vec!["STRAY.md".to_string()],
            "with no transform on any row, pi and claude-code resolve the SAME directory"
        );
    }

    // REQ-YF-MARK-005 (Issue 2.11): residue is spared by prune, so `--prune` and the
    // tree hash agree. If they disagreed, doctor would oscillate.
    #[test]
    fn prune_spares_generated_residue() {
        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");
        run(&args_for(&skills_dir)).unwrap();

        let root = skills_dir.join("yf-beads-extra");
        let cache = root.join("scripts/__pycache__");
        std::fs::create_dir_all(&cache).unwrap();
        let pyc = cache.join("x.cpython-314.pyc");
        std::fs::write(&pyc, b"residue\n").unwrap();

        let mut a = args_for(&skills_dir);
        a.prune = true;
        a.json = false;
        run(&a).unwrap();

        assert!(
            pyc.exists(),
            "generated residue must be SPARED by prune (REQ-YF-MARK-005)"
        );
    }
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
            prune: false,
            no_skills: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
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

    /// SC11 — an install run with a replace-semantics override set, disagreeing with the
    /// default, EMITS A WARNING naming the directory the harness will actually read.
    ///
    /// Asserted over the message rather than through a captured stderr pipe: the requirement is
    /// about *what is said*, and a test that pipes stderr mostly tests the pipe.
    #[test]
    fn install_warns_on_override_mismatch() {
        use crate::cli::Scope;
        let home = std::path::Path::new("/home/jd");
        let elsewhere = std::ffi::OsString::from("/elsewhere/codex-home");

        // (a) A REPLACE var disagreeing with the default → exactly one warning, and it names
        //     BOTH directories: where yf writes and where the harness will actually read.
        let w = override_mismatch_warnings(Scope::User, &["codex".to_string()], home, |k| {
            (k == "CODEX_HOME").then(|| elsewhere.clone())
        });
        assert_eq!(w.len(), 1, "one mismatch, one warning: {w:?}");
        assert!(
            w[0].contains("CODEX_HOME"),
            "the warning must name the VAR: {}",
            w[0]
        );
        assert!(
            w[0].contains("/elsewhere/codex-home"),
            "it must name where the harness will ACTUALLY read — the whole remedy: {}",
            w[0]
        );
        assert!(
            w[0].contains("/home/jd/.agents"),
            "and where yf writes, or the operator cannot act on it: {}",
            w[0]
        );

        // (b) The var AGREEING with the default is not a mismatch. This is the arm that keeps
        //     the warning from firing on every correctly-configured machine.
        let agreeing = std::ffi::OsString::from("/home/jd/.agents");
        assert!(
            override_mismatch_warnings(Scope::User, &["codex".to_string()], home, |k| (k
                == "CODEX_HOME")
                .then(|| agreeing.clone()))
            .is_empty(),
            "an override pointing at the default is not a mismatch"
        );

        // (c) An ADDITIVE var NEVER warns, however far it points from the default. The default
        //     root is still read, so yf's write still lands where opencode looks — warning here
        //     would train an operator to ignore the warning in (a).
        let far = std::ffi::OsString::from("/somewhere/entirely/else");
        assert!(
            override_mismatch_warnings(Scope::User, &["opencode".to_string()], home, |k| (k
                == "OPENCODE_CONFIG_DIR")
                .then(|| far.clone()))
            .is_empty(),
            "an ADDITIVE override is not a mismatch"
        );
        // ...while opencode's OTHER var, which replaces, does warn — same harness, same run
        // shape, opposite verdict. That pair is what proves the precedence is being read.
        assert_eq!(
            override_mismatch_warnings(Scope::User, &["opencode".to_string()], home, |k| (k
                == "XDG_CONFIG_HOME")
                .then(|| far.clone()))
            .len(),
            1,
            "XDG_CONFIG_HOME REPLACES opencode's config root, so a mismatch must warn"
        );

        // (d) No var set → silence.
        assert!(
            override_mismatch_warnings(Scope::User, &["codex".to_string()], home, |_| None)
                .is_empty()
        );
    }

    /// SC16b — creating `<repo>/.agents/skills` emits a warning naming pi's trust consequence.
    #[test]
    fn warns_project_scope_makes_repo_trust_requiring() {
        let msg = project_scope_trust_warning(std::path::Path::new("/repo/.agents/skills"));
        assert!(
            msg.contains("/repo/.agents/skills"),
            "names the directory: {msg}"
        );
        assert!(
            msg.to_lowercase().contains("trust"),
            "names the consequence: {msg}"
        );
        assert!(msg.contains("pi"), "names the harness: {msg}");
        // The SILENCE is the substance of the warning — a reader who does not learn that pi
        // drops the skills without any diagnostic has not been warned about anything actionable.
        assert!(
            msg.contains("SILENTLY") || msg.to_lowercase().contains("silent"),
            "must state that the failure is SILENT: {msg}"
        );
        assert!(
            msg.contains("exit 0"),
            "must state the measured symptom: {msg}"
        );
    }
}

//! `yf self uninstall` (plan-018 Issue 3.6).
//!
//! Removes the `yf` binary and **yf-owned** state — the XDG config/cache/data dirs
//! (`~/.config/yf`, `~/.cache/yf`, `~/.local/share/yf`), the cargo-dist `env`
//! scripts (`~/.local/bin/env[.fish]`), and the `. "$HOME/.local/bin/env"` line the
//! installer added to shell rcfiles. It deliberately **never** touches installed
//! skills/rules (`~/.claude/{skills,rules}`, `~/.agents/...`) — that is `yf skills
//! remove`'s job (GR-008: each command touches only its own surfaces).

use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{Context, Result};

use super::receipt;
use crate::cli::SelfUninstallArgs;
use crate::dirs::Dirs;

/// The rcfiles cargo-dist's installer may append its PATH line to (see the
/// generated `yf-installer.sh`: `.profile .bashrc .bash_profile .bash_login
/// .zshrc .zshenv`, plus the fish conf.d file).
const RCFILES: &[&str] = &[
    ".profile",
    ".bashrc",
    ".bash_profile",
    ".bash_login",
    ".zshrc",
    ".zshenv",
];

/// What an uninstall will remove/modify — computed up front so we can show it
/// before acting (and unit-test the plan without touching the real home).
#[derive(Debug, Default)]
pub struct RemovalPlan {
    /// Files to delete (binary + env scripts) that currently exist.
    pub files: Vec<PathBuf>,
    /// Directories to delete recursively (yf-owned XDG dirs) that currently exist.
    pub dirs: Vec<PathBuf>,
    /// rcfiles that contain the installer PATH line and will be edited.
    pub rcfiles_to_edit: Vec<PathBuf>,
}

/// Build the removal plan from resolved [`Dirs`] and a `home` (the rcfile anchor).
pub fn plan_removal(dirs: &Dirs, home: &Path) -> RemovalPlan {
    let mut plan = RemovalPlan::default();

    let bin = dirs.bin_dir();
    for f in [bin.join("yf"), bin.join("env"), bin.join("env.fish")] {
        if f.exists() {
            plan.files.push(f);
        }
    }

    for d in [dirs.config_dir(), dirs.cache_dir(), dirs.data_dir()] {
        if d.exists() {
            plan.dirs.push(d.to_path_buf());
        }
    }

    let env_variants = env_source_variants(dirs, home);
    for rc in RCFILES {
        let path = home.join(rc);
        if let Ok(content) = std::fs::read_to_string(&path) {
            if strip_env_source_lines(&content, &env_variants).1 > 0 {
                plan.rcfiles_to_edit.push(path);
            }
        }
    }

    plan
}

/// Run `yf self uninstall`.
pub fn run(args: &SelfUninstallArgs) -> Result<ExitCode> {
    let dirs = Dirs::from_env();
    let home = std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    run_with(args, &dirs, &home)
}

fn run_with(args: &SelfUninstallArgs, dirs: &Dirs, home: &Path) -> Result<ExitCode> {
    let plan = plan_removal(dirs, home);

    if plan.files.is_empty() && plan.dirs.is_empty() && plan.rcfiles_to_edit.is_empty() {
        if args.json {
            println!(
                "{}",
                serde_json::json!({"command":"self uninstall","status":"noop",
                    "message":"nothing to remove (no yf binary or yf-owned dirs found)"})
            );
        } else {
            println!("nothing to remove — no `yf` binary or yf-owned dirs found");
        }
        return Ok(ExitCode::SUCCESS);
    }

    // Non-interactive safety: JSON mode and any unattended run require --force. We
    // never block on a prompt in a script context.
    if !args.force {
        if args.json {
            return refuse_needs_force_json(&plan);
        }
        eprintln!("This will remove:");
        for f in &plan.files {
            eprintln!("  file: {}", f.display());
        }
        for d in &plan.dirs {
            eprintln!("  dir:  {} (recursive)", d.display());
        }
        for rc in &plan.rcfiles_to_edit {
            eprintln!("  edit: {} (strip the installer PATH line)", rc.display());
        }
        eprintln!("Installed skills/rules (~/.claude, ~/.agents) are NOT touched.");
        eprintln!("Re-run with `--force` to proceed.");
        return Ok(ExitCode::FAILURE);
    }

    // Execute.
    let env_variants = env_source_variants(dirs, home);
    let mut removed_files = Vec::new();
    let mut removed_dirs = Vec::new();
    let mut edited = Vec::new();

    for f in &plan.files {
        std::fs::remove_file(f).with_context(|| format!("removing {}", f.display()))?;
        removed_files.push(f.clone());
    }
    for d in &plan.dirs {
        std::fs::remove_dir_all(d).with_context(|| format!("removing {}", d.display()))?;
        removed_dirs.push(d.clone());
    }
    for rc in &plan.rcfiles_to_edit {
        let content = std::fs::read_to_string(rc)?;
        let (stripped, n) = strip_env_source_lines(&content, &env_variants);
        if n > 0 {
            std::fs::write(rc, stripped).with_context(|| format!("editing {}", rc.display()))?;
            edited.push(rc.clone());
        }
    }
    // The from-build marker lives under config_dir, already removed with the dir;
    // call remove defensively in case config_dir was absent but the marker wasn't.
    let _ = receipt::remove_from_build_marker(dirs);

    report(args.json, &removed_files, &removed_dirs, &edited);
    Ok(ExitCode::SUCCESS)
}

/// The strings an rcfile `source`/`.` line may reference for the env script:
/// the absolute path, the `$HOME/...` form, and the `~/...` form.
fn env_source_variants(dirs: &Dirs, home: &Path) -> Vec<String> {
    let env_abs = dirs.bin_dir().join("env");
    let mut v = vec![env_abs.to_string_lossy().into_owned()];
    if let Ok(rel) = env_abs.strip_prefix(home) {
        let rel = rel.to_string_lossy();
        v.push(format!("$HOME/{rel}"));
        v.push(format!("~/{rel}"));
    }
    v
}

/// Remove rcfile lines that `source`/`.` the cargo-dist env script. Pure: returns
/// the new content and the number of lines removed. A line matches when it is a
/// `.`/`source` command referencing any `variant` (with or without `.fish`).
pub fn strip_env_source_lines(content: &str, variants: &[String]) -> (String, usize) {
    let mut removed = 0;
    let kept: Vec<&str> = content
        .lines()
        .filter(|line| {
            let t = line.trim();
            let is_source_cmd = t.starts_with(". ") || t.starts_with("source ");
            let refs_env = variants.iter().any(|v| t.contains(v.as_str()));
            if is_source_cmd && refs_env {
                removed += 1;
                false
            } else {
                true
            }
        })
        .collect();
    // Preserve a trailing newline if the original had one.
    let mut out = kept.join("\n");
    if content.ends_with('\n') && !out.is_empty() {
        out.push('\n');
    }
    (out, removed)
}

fn refuse_needs_force_json(plan: &RemovalPlan) -> Result<ExitCode> {
    let out = serde_json::json!({
        "command": "self uninstall",
        "status": "needs_force",
        "would_remove_files": plan.files.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
        "would_remove_dirs": plan.dirs.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
        "would_edit_rcfiles": plan.rcfiles_to_edit.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
        "message": "re-run with --force to proceed (skills/rules are not touched)",
    });
    println!("{}", serde_json::to_string(&out)?);
    Ok(ExitCode::FAILURE)
}

fn report(json: bool, files: &[PathBuf], dirs: &[PathBuf], edited: &[PathBuf]) {
    if json {
        let out = serde_json::json!({
            "command": "self uninstall",
            "status": "ok",
            "removed_files": files.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
            "removed_dirs": dirs.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
            "edited_rcfiles": edited.iter().map(|p| p.display().to_string()).collect::<Vec<_>>(),
            "note": "installed skills/rules (~/.claude, ~/.agents) were not touched",
        });
        if let Ok(s) = serde_json::to_string(&out) {
            println!("{s}");
        }
    } else {
        for f in files {
            println!("removed {}", f.display());
        }
        for d in dirs {
            println!("removed {} (recursive)", d.display());
        }
        for rc in edited {
            println!("stripped installer PATH line from {}", rc.display());
        }
        println!("(installed skills/rules under ~/.claude and ~/.agents were not touched)");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn dirs_for(home: &Path) -> Dirs {
        let home = home.to_path_buf();
        crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()))
    }

    #[test]
    fn strips_only_the_env_source_line() {
        let variants = vec!["$HOME/.local/bin/env".to_string()];
        let content = "# my profile\nexport FOO=1\n. \"$HOME/.local/bin/env\"\nalias x=y\n";
        let (out, n) = strip_env_source_lines(content, &variants);
        assert_eq!(n, 1);
        assert!(!out.contains(".local/bin/env"));
        assert!(out.contains("export FOO=1"));
        assert!(out.contains("alias x=y"));
        assert!(out.ends_with('\n'));
    }

    #[test]
    fn does_not_strip_unrelated_source_lines() {
        let variants = vec!["$HOME/.local/bin/env".to_string()];
        let content = ". \"$HOME/.cargo/env\"\nsource ~/.nvm/nvm.sh\n";
        let (out, n) = strip_env_source_lines(content, &variants);
        assert_eq!(n, 0);
        assert_eq!(out, content);
    }

    #[test]
    fn plan_lists_binary_dirs_and_rcfile() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path();
        let dirs = dirs_for(home);
        // Lay down a binary, env script, config dir, and a tagged .zshrc.
        std::fs::create_dir_all(dirs.bin_dir()).unwrap();
        std::fs::write(dirs.bin_dir().join("yf"), b"bin").unwrap();
        std::fs::write(dirs.bin_dir().join("env"), b"env").unwrap();
        std::fs::create_dir_all(dirs.config_dir()).unwrap();
        std::fs::write(dirs.config_dir().join("yf-receipt.json"), b"{}").unwrap();
        std::fs::write(
            home.join(".zshrc"),
            "setopt foo\n. \"$HOME/.local/bin/env\"\n",
        )
        .unwrap();

        let plan = plan_removal(&dirs, home);
        assert!(plan.files.iter().any(|p| p.ends_with("yf")));
        assert!(plan.files.iter().any(|p| p.ends_with("env")));
        assert!(plan.dirs.iter().any(|p| p.ends_with("yf")));
        assert!(plan.rcfiles_to_edit.iter().any(|p| p.ends_with(".zshrc")));
    }

    #[test]
    fn force_removes_and_leaves_skills_untouched() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path();
        let dirs = dirs_for(home);
        std::fs::create_dir_all(dirs.bin_dir()).unwrap();
        std::fs::write(dirs.bin_dir().join("yf"), b"bin").unwrap();
        std::fs::create_dir_all(dirs.config_dir()).unwrap();
        std::fs::write(dirs.config_dir().join("yf-receipt.json"), b"{}").unwrap();
        std::fs::write(home.join(".zshrc"), ". \"$HOME/.local/bin/env\"\nfoo\n").unwrap();
        // A skills dir that MUST survive.
        let skills = home.join(".claude").join("skills");
        std::fs::create_dir_all(&skills).unwrap();

        let args = SelfUninstallArgs {
            force: true,
            json: true,
        };
        let code = run_with(&args, &dirs, home).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::SUCCESS));
        assert!(!dirs.bin_dir().join("yf").exists());
        assert!(!dirs.config_dir().exists());
        let zsh = std::fs::read_to_string(home.join(".zshrc")).unwrap();
        assert!(!zsh.contains(".local/bin/env"));
        assert!(zsh.contains("foo"));
        // skills survive.
        assert!(skills.exists(), "uninstall must not touch ~/.claude/skills");
    }

    #[test]
    fn no_force_refuses_in_json() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path();
        let dirs = dirs_for(home);
        std::fs::create_dir_all(dirs.bin_dir()).unwrap();
        std::fs::write(dirs.bin_dir().join("yf"), b"bin").unwrap();
        let args = SelfUninstallArgs {
            force: false,
            json: true,
        };
        let code = run_with(&args, &dirs, home).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::FAILURE));
        // Binary still present (refused).
        assert!(dirs.bin_dir().join("yf").exists());
    }

    #[test]
    fn nothing_to_remove_is_success() {
        let tmp = tempfile::tempdir().unwrap();
        let dirs = dirs_for(tmp.path());
        let args = SelfUninstallArgs {
            force: true,
            json: true,
        };
        let code = run_with(&args, &dirs, tmp.path()).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::SUCCESS));
    }
}

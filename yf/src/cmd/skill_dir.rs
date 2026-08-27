//! `yf skill-dir <name>` — resolve an installed skill directory across every harness
//! destination `yf` itself installs to (REQ-YF-CLI-005).
//!
//! # Why this exists
//!
//! The `SKILL_DIR` idiom embedded in shipped skill instructions searched six fixed roots, and
//! **neither `~/.pi/agent/skills` nor `~/.config/opencode/skills` was among them** — while `yf`
//! installs to exactly those. Measured live (EXP-002): on a pi-only machine every script-backed
//! skill dies at `ERROR: <skill> directory not found`; on a mixed machine it silently resolves
//! to the *claude-code* copy, so a skill's prose and its scripts come from different trees. The
//! install reports success either way.
//!
//! Putting resolution in the binary means the descriptor table (`harness_desc::DESCRIPTORS`) is
//! the single source of truth for *both* where skills are written and where they are found, so a
//! sixth harness needs **zero** edits here.
//!
//! # The predicate is EXISTENCE-ONLY
//!
//! This verb asserts that a directory of that name exists at a known destination and asserts
//! **nothing** about its contents: no marker check, no `SKILL.md` presence check, no integrity
//! or version verification. A caller needing those guarantees checks them itself. Widening the
//! predicate here would make the resolver's answer depend on skill *health*, which is
//! `yf skills status`'s question, not this one's.
//!
//! # Exit contract (three-valued)
//!
//! * `0` — exactly one directory resolved; its absolute path is printed on stdout.
//! * `1` — no directory resolved (the skill is not installed at any known destination).
//! * `2` — the lookup could not be performed at all (INCONCLUSIVE).
//!
//! `2` is a statement about the *instrument*, not about the skill, and is deliberately distinct
//! from `1`: a caller that collapses them cannot tell "not installed" from "could not look".

use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::Result;

use crate::cli::{Scope, SkillDirArgs};
use crate::dest;
use crate::harness_desc;

/// One candidate destination, carrying the provenance a `--json` caller needs.
#[derive(Debug, Clone)]
pub struct Candidate {
    pub path: PathBuf,
    pub harness: &'static str,
    pub scope: Scope,
}

/// Enumerate every candidate directory for `name`, in resolution order.
///
/// **Order is user, then git-root, then cwd** — the same precedence `yf` installs with, so the
/// copy a caller resolves is the copy `yf` most recently wrote at the highest-priority anchor.
///
/// Two behaviours are load-bearing:
///
/// * **pi's `NameTransform` is applied.** pi lowercases and hyphenates the on-disk directory
///   name, so looking for the *given* name under pi's root would miss a skill that is really
///   there. The transform lives on the descriptor row, so this is a table lookup, not a special
///   case.
/// * **Duplicate paths are DEDUPED.** `codex` and `agents` share `.agents/skills` verbatim, so
///   an un-deduped enumeration reports the same directory twice and any "exactly one match"
///   framing becomes nonsense. Dedupe is on the resolved *path*, not on the harness id, because
///   it is the path that collides.
pub fn candidates(name: &str, anchors: &[(Scope, PathBuf)]) -> Vec<Candidate> {
    let mut out: Vec<Candidate> = Vec::new();
    let mut seen: Vec<PathBuf> = Vec::new();
    for (scope, anchor) in anchors {
        for d in harness_desc::DESCRIPTORS {
            let dir = dest::skills_dir_for_anchor(anchor, d.id, *scope)
                .join(d.transform_skill_name(name));
            if seen.iter().any(|p| p == &dir) {
                continue;
            }
            seen.push(dir.clone());
            out.push(Candidate {
                path: dir,
                harness: d.id,
                scope: *scope,
            });
        }
    }
    out
}

/// The anchors to search, in precedence order: `$HOME`, then the git root, then cwd.
///
/// The git root and cwd are frequently the same directory; `candidates` dedupes on the joined
/// path, so a repeated anchor costs nothing and needs no guard here.
fn anchors() -> Result<Vec<(Scope, PathBuf)>> {
    let mut v: Vec<(Scope, PathBuf)> = Vec::new();
    if let Some(home) = std::env::var_os("HOME") {
        v.push((Scope::User, PathBuf::from(home)));
    }
    v.push((Scope::Project, dest::git_root_or_cwd()));
    if let Ok(cwd) = std::env::current_dir() {
        v.push((Scope::Project, cwd));
    }
    Ok(v)
}

/// `yf skill-dir <name>` (REQ-YF-CLI-005).
pub fn run(args: &SkillDirArgs) -> Result<ExitCode> {
    let name = args.name.trim();

    // An empty name is an INCONCLUSIVE (2), never a not-found (1): nothing was looked up, so
    // reporting "not installed" would be a claim the run never made.
    if name.is_empty() {
        if args.json {
            println!(
                "{}",
                serde_json::json!({
                    "command": "skill-dir",
                    "verdict": "INCONCLUSIVE",
                    "reason": "empty skill name",
                    "path": serde_json::Value::Null,
                })
            );
        } else {
            eprintln!("yf skill-dir: INCONCLUSIVE — empty skill name");
        }
        return Ok(ExitCode::from(2));
    }

    let anchors = match anchors() {
        Ok(a) if !a.is_empty() => a,
        _ => {
            if args.json {
                println!(
                    "{}",
                    serde_json::json!({
                        "command": "skill-dir",
                        "verdict": "INCONCLUSIVE",
                        "reason": "no searchable anchor (neither HOME nor a working directory)",
                        "path": serde_json::Value::Null,
                    })
                );
            } else {
                eprintln!(
                    "yf skill-dir: INCONCLUSIVE — no searchable anchor \
                     (neither HOME nor a working directory)"
                );
            }
            return Ok(ExitCode::from(2));
        }
    };

    let cands = candidates(name, &anchors);
    let hit = cands.iter().find(|c| is_dir(&c.path));

    match hit {
        Some(c) => {
            if args.json {
                println!(
                    "{}",
                    serde_json::json!({
                        "command": "skill-dir",
                        "verdict": "FOUND",
                        "path": c.path,
                        "harness": c.harness,
                        "scope": match c.scope { Scope::User => "user", Scope::Project => "project" },
                    })
                );
            } else {
                println!("{}", c.path.display());
            }
            Ok(ExitCode::SUCCESS)
        }
        None => {
            if args.json {
                println!(
                    "{}",
                    serde_json::json!({
                        "command": "skill-dir",
                        "verdict": "NOT_FOUND",
                        "reason": format!("no directory named {name:?} at any known destination"),
                        "path": serde_json::Value::Null,
                        "searched": cands.iter().map(|c| &c.path).collect::<Vec<_>>(),
                    })
                );
            } else {
                eprintln!(
                    "yf skill-dir: {name} is not installed at any known destination \
                     ({} searched)",
                    cands.len()
                );
            }
            Ok(ExitCode::from(1))
        }
    }
}

fn is_dir(p: &Path) -> bool {
    std::fs::metadata(p).map(|m| m.is_dir()).unwrap_or(false)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn seed(root: &Path, sub: &str, name: &str) -> PathBuf {
        let d = root.join(sub).join(name);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    // REQ-YF-CLI-005: resolution order is user, then git-root/cwd. A skill present at BOTH
    // must resolve to the USER copy — that is the copy `yf` writes by default, so preferring
    // the project one would hand back a tree the operator did not most recently install.
    #[test]
    fn user_anchor_wins_over_project() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        let proj = tmp.path().join("proj");
        let want = seed(&home, ".claude/skills", "yf-plan");
        seed(&proj, ".claude/skills", "yf-plan");
        let anchors = vec![(Scope::User, home.clone()), (Scope::Project, proj.clone())];
        let c = candidates("yf-plan", &anchors);
        let hit = c.iter().find(|c| c.path.is_dir()).unwrap();
        assert_eq!(hit.path, want, "the user copy must win");
        assert_eq!(hit.scope, Scope::User);
    }

    // REQ-YF-CLI-005: pi's NameTransform is applied to the on-disk directory name. Without
    // this the resolver looks for the GIVEN name under pi's root and misses a skill that is
    // really there — a not-found that is purely an artifact of the lookup.
    #[test]
    fn pi_name_transform_is_applied() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        // pi lowercases and hyphenates, so `YF_Plan` lands on disk as `yf-plan`.
        let want = seed(&home, ".pi/agent/skills", "yf-plan");
        let anchors = vec![(Scope::User, home.clone())];
        let c = candidates("YF_Plan", &anchors);
        assert!(
            c.iter().any(|c| c.path == want),
            "pi's transform must be applied; candidates were {:?}",
            c.iter().map(|c| &c.path).collect::<Vec<_>>()
        );
    }

    // REQ-YF-CLI-005: `codex` and `agents` share `.agents/skills` VERBATIM, so an un-deduped
    // enumeration reports one directory twice and any "exactly one match" framing becomes
    // nonsense. Dedupe is on the resolved PATH, since it is the path that collides.
    #[test]
    fn shared_codex_agents_path_is_deduped() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        let anchors = vec![(Scope::User, home.clone())];
        let c = candidates("yf-plan", &anchors);
        let shared = home.join(".agents/skills").join("yf-plan");
        let n = c.iter().filter(|c| c.path == shared).count();
        assert_eq!(
            n, 1,
            "the shared codex/agents path must appear exactly once"
        );
        let mut paths: Vec<_> = c.iter().map(|c| c.path.clone()).collect();
        let before = paths.len();
        paths.sort();
        paths.dedup();
        assert_eq!(
            before,
            paths.len(),
            "no candidate path may be enumerated twice"
        );
    }

    // REQ-YF-CLI-005: every harness destination is searched — the whole point of moving
    // resolution into the binary. Asserted against the DESCRIPTOR TABLE rather than a literal
    // list, so a sixth harness is covered without editing this test.
    #[test]
    fn every_descriptor_destination_is_searched() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        let anchors = vec![(Scope::User, home.clone())];
        let c = candidates("yf-plan", &anchors);
        for d in harness_desc::DESCRIPTORS {
            let want = home
                .join(d.subpath(Scope::User))
                .join(d.transform_skill_name("yf-plan"));
            assert!(
                c.iter().any(|c| c.path == want),
                "destination for harness {} was never searched",
                d.id
            );
        }
    }

    // REQ-YF-CLI-005: NOT-FOUND is 1 and COULD-NOT-RUN is 2, and they are different facts.
    // Collapsing them is the exact conflation this release exists to remove.
    #[test]
    fn not_found_is_one_and_could_not_run_is_two() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        std::fs::create_dir_all(&home).unwrap();
        let anchors = vec![(Scope::User, home)];
        assert!(
            candidates("no-such-skill", &anchors)
                .iter()
                .all(|c| !c.path.is_dir()),
            "nothing may resolve for a skill that was never installed"
        );
        // The empty-name path is INCONCLUSIVE rather than not-found: nothing was looked up,
        // so "not installed" would be a claim the run never made.
        let args = SkillDirArgs {
            name: String::new(),
            json: true,
        };
        let code = run(&args).unwrap();
        assert_eq!(
            format!("{code:?}"),
            format!("{:?}", ExitCode::from(2)),
            "an empty name must be INCONCLUSIVE (2), never NOT_FOUND (1)"
        );
    }
}

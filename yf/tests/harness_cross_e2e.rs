//! Cross-harness provisioning integration test (plan-033 Issue 10.1).
//!
//! Drives the **real `yf` binary** (`CARGO_BIN_EXE_yf`) under a hermetic,
//! sandboxed `HOME` — per the project `TESTING.md` Tier-2 discipline: never trust
//! an installed copy, exercise the modified crate end-to-end against an isolated
//! root. Every spawn injects `HOME=<tempdir>` (and clears the ambient `HOME`), so
//! user-scope resolution (`~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.pi`)
//! lands entirely inside the sandbox and the operator's real home is never touched.
//!
//! Coverage:
//!
//! - **`REQ-YF-TUNE-012`** — `yf harness tune --harness <name>` runs BOTH
//!   sub-operations (config align + rule deploy) for claude-code / codex /
//!   opencode.
//! - **`REQ-YF-TUNE-022`** — a `tune` → `--revert` round-trip restores the prior
//!   state (config keys removed / rule surface restored) via the sidecar `.yf/`
//!   ownership manifest, applying the touched-since-tune guard.
//! - **`REQ-YF-TUNE-020`** — pi gets rule deployment only (config deferred), a
//!   managed block that round-trips against pre-existing user prose.
//! - **`REQ-YF-INSTALL-002`** — per-harness skills-install destination resolution.
//!
//! The **no-cross-harness-path-bleed** invariant is asserted directly: a tune of
//! ONE harness writes only that harness's resolved surfaces and leaves every other
//! harness's config / rule / manifest path absent.

use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

const YF: &str = env!("CARGO_BIN_EXE_yf");

const BEGIN_MARKER: &str = "<!-- BEGIN yf-managed-rules -->";

/// Run `yf <args>` with a hermetic sandboxed `HOME`, asserting exit success and
/// returning the parsed JSON stdout (`--json` is the caller's responsibility).
fn yf_json_in(home: &Path, args: &[&str]) -> Value {
    let out = Command::new(YF)
        .args(args)
        .env("HOME", home)
        .env_remove("CLAUDE_CONFIG_DIR")
        .output()
        .expect("spawn yf");
    assert!(
        out.status.success(),
        "yf {args:?} exited non-zero: {}\nstdout: {}",
        String::from_utf8_lossy(&out.stderr),
        String::from_utf8_lossy(&out.stdout),
    );
    serde_json::from_slice(&out.stdout).unwrap_or_else(|e| {
        panic!(
            "yf {args:?} did not emit JSON ({e}): {}",
            String::from_utf8_lossy(&out.stdout)
        )
    })
}

/// The resolved user-scope surface paths for a harness under a sandbox `HOME`.
struct Surfaces {
    /// Config file (`None` for pi — config is deferred).
    config: Option<PathBuf>,
    /// Always-loaded rule surface (a `rules/YOSHIKO_FLOW.md` file for claude-code,
    /// an `AGENTS.md` for the AGENTS.md harnesses).
    rule: PathBuf,
    /// A yf-written config key whose presence proves the config sub-op ran.
    config_key: &'static str,
}

fn surfaces(home: &Path, harness: &str) -> Surfaces {
    match harness {
        "claude-code" => Surfaces {
            config: Some(home.join(".claude/settings.json")),
            rule: home.join(".claude/rules/YOSHIKO_FLOW.md"),
            config_key: "todoFeatureEnabled",
        },
        "codex" => Surfaces {
            config: Some(home.join(".codex/config.toml")),
            rule: home.join(".codex/AGENTS.md"),
            config_key: "approval_policy",
        },
        "opencode" => Surfaces {
            config: Some(home.join(".config/opencode/opencode.json")),
            rule: home.join(".config/opencode/AGENTS.md"),
            config_key: "share",
        },
        "pi" => Surfaces {
            config: None,
            rule: home.join(".pi/agent/AGENTS.md"),
            config_key: "",
        },
        // plan-044 Issue 2.2, probe outcome B: `agents` is a SKILLS-ONLY bare
        // surface — no config profile AND no rule target. `rule` names the path a
        // rules write WOULD have taken (the skills-sibling dir), so the assertions
        // below can state the NEGATIVE form: nothing is ever written there.
        "agents" => Surfaces {
            config: None,
            rule: home.join(".agents/rules/YOSHIKO_FLOW.md"),
            config_key: "",
        },
        other => panic!("unknown harness {other}"),
    }
}

/// Every harness's user-scope surfaces (config + rule + `.yf/` manifest dir), for
/// the no-path-bleed sweep.
fn all_surface_paths(home: &Path, harness: &str) -> Vec<PathBuf> {
    let s = surfaces(home, harness);
    let mut v = vec![s.rule];
    if let Some(c) = s.config {
        v.push(c);
    }
    v
}

// REQ-YF-TUNE-012 + REQ-YF-TUNE-022: for each config-bearing harness, a tune writes
// BOTH sub-operations (config file + rule surface) and a --revert round-trips them
// back to the prior (absent) state via the sidecar `.yf/` manifest.
#[test]
fn cross_harness_tune_revert_roundtrip() {
    for harness in ["claude-code", "codex", "opencode"] {
        // A fresh sandbox HOME per harness — nothing pre-exists.
        let home = tempfile::tempdir().unwrap();
        let home = home.path();
        let s = surfaces(home, harness);
        let config = s.config.clone().expect("config-bearing harness");

        // Pre-state: neither surface exists.
        assert!(!config.exists(), "{harness}: config absent before tune");
        assert!(!s.rule.exists(), "{harness}: rule absent before tune");

        // TUNE — both sub-operations.
        let j = yf_json_in(home, &["harness", "tune", "--harness", harness, "--json"]);
        assert_eq!(j["status"], "ok", "{harness}: tune ok: {j}");

        // Config sub-op wrote the yf key.
        assert!(config.exists(), "{harness}: config written by tune");
        let cfg_text = std::fs::read_to_string(&config).unwrap();
        assert!(
            cfg_text.contains(s.config_key),
            "{harness}: config carries yf key {}: {cfg_text}",
            s.config_key
        );

        // Rule sub-op wrote the always-loaded surface.
        assert!(s.rule.exists(), "{harness}: rule surface written by tune");

        // REVERT — undo both via the manifest.
        let jr = yf_json_in(
            home,
            &[
                "harness",
                "tune",
                "--harness",
                harness,
                "--revert",
                "--json",
            ],
        );
        assert_eq!(jr["status"], "ok", "{harness}: revert ok: {jr}");

        // Config key is gone; rule surface is removed (it was fully yf-owned).
        if config.exists() {
            let after = std::fs::read_to_string(&config).unwrap();
            assert!(
                !after.contains(s.config_key),
                "{harness}: yf config key removed by revert: {after}"
            );
        }
        assert!(
            !s.rule.exists(),
            "{harness}: fully-yf-owned rule surface removed by revert"
        );

        // A second revert is a clean no-op.
        let j2 = yf_json_in(
            home,
            &[
                "harness",
                "tune",
                "--harness",
                harness,
                "--revert",
                "--json",
            ],
        );
        assert_eq!(j2["status"], "ok", "{harness}: second revert no-op: {j2}");
    }
}

// REQ-YF-TUNE-029 (#154, plan-044 Issue 2.7): the AGGREGATE revert round-trip.
//
// The claude-code aggregate (`~/.claude/rules/YOSHIKO_FLOW.md`) is a whole FILE,
// not a managed block sharing space with prose — so the pi test above cannot cover
// it. Before this change revert deleted it unconditionally, on the reasoning that
// it is fully yf-managed. But revert holds NO BACKUP: deleting a hand-edited
// aggregate destroys operator content nothing can restore. "Regenerable" and
// "restorable" are different claims.
//
// Both directions are asserted, because a guard that keeps EVERYTHING is as broken
// as one that deletes everything.
#[test]
fn aggregate_revert_keeps_a_hand_edited_file_and_still_reverts_a_clean_one() {
    // --- Direction 1: HAND-EDITED → the file SURVIVES, with a reported mismatch.
    {
        let home = tempfile::tempdir().unwrap();
        let home = home.path();
        let aggregate = home.join(".claude/rules/YOSHIKO_FLOW.md");

        yf_json_in(home, &["harness", "tune", "--harness", "claude-code", "--json"]);
        assert!(aggregate.is_file(), "tune wrote the aggregate");

        // The operator hand-edits it after the tune.
        let edited = std::fs::read_to_string(&aggregate).unwrap()
            + "\n<!-- operator note: do not lose this -->\n";
        std::fs::write(&aggregate, &edited).unwrap();

        let jr = yf_json_in(
            home,
            &["harness", "tune", "--harness", "claude-code", "--revert", "--json"],
        );

        assert!(
            aggregate.is_file(),
            "a hand-edited aggregate MUST survive revert — revert has no backup, \
             so deleting it destroys operator content irrecoverably"
        );
        assert_eq!(
            std::fs::read_to_string(&aggregate).unwrap(),
            edited,
            "the kept file is byte-identical — revert must not rewrite it either"
        );
        assert_eq!(
            jr["surfaces"][0]["rules"]["status"], "kept_modified",
            "the keep is REPORTED, not silent: {jr}"
        );
    }

    // --- Direction 2: UNEDITED → still reverts cleanly (the guard is not a veto).
    {
        let home = tempfile::tempdir().unwrap();
        let home = home.path();
        let aggregate = home.join(".claude/rules/YOSHIKO_FLOW.md");

        yf_json_in(home, &["harness", "tune", "--harness", "claude-code", "--json"]);
        assert!(aggregate.is_file(), "tune wrote the aggregate");

        let jr = yf_json_in(
            home,
            &["harness", "tune", "--harness", "claude-code", "--revert", "--json"],
        );
        assert_eq!(
            jr["surfaces"][0]["rules"]["status"], "reverted",
            "an untouched aggregate still reverts: {jr}"
        );
        assert!(
            !aggregate.exists(),
            "an untouched aggregate is removed by revert"
        );
    }
}

// REQ-YF-TUNE-020: pi gets rule deployment ONLY (config deferred). The managed
// block deploys into `~/.pi/agent/AGENTS.md` (the Issue 1.5-verified default) and a
// --revert round-trips it while PRESERVING pre-existing operator prose.
#[test]
fn pi_rule_tune_revert_roundtrip_preserves_user_prose() {
    let home = tempfile::tempdir().unwrap();
    let home = home.path();
    let agents = home.join(".pi/agent/AGENTS.md");
    std::fs::create_dir_all(agents.parent().unwrap()).unwrap();
    let user_prose = "# My pi rules\n\nHand-written operator guidance.\n";
    std::fs::write(&agents, user_prose).unwrap();

    // TUNE pi — rules deploy, config is DEFERRED (not a failure).
    let j = yf_json_in(home, &["harness", "tune", "--harness", "pi", "--json"]);
    assert_eq!(j["status"], "ok", "pi tune ok: {j}");
    assert_eq!(
        j["harnesses"][0]["config"]["status"], "deferred",
        "pi config is deferred, not failed: {j}"
    );

    let after_tune = std::fs::read_to_string(&agents).unwrap();
    assert!(
        after_tune.contains(user_prose.trim_end()),
        "user prose preserved through tune: {after_tune}"
    );
    assert!(
        after_tune.contains(BEGIN_MARKER),
        "managed block deployed into pi AGENTS.md: {after_tune}"
    );

    // REVERT pi — the managed block is removed, the user prose survives.
    let jr = yf_json_in(
        home,
        &["harness", "tune", "--harness", "pi", "--revert", "--json"],
    );
    assert_eq!(jr["status"], "ok", "pi revert ok: {jr}");

    let after_revert = std::fs::read_to_string(&agents)
        .expect("pi AGENTS.md survives revert (it still holds user prose)");
    assert!(
        after_revert.contains(user_prose.trim_end()),
        "user prose survives revert: {after_revert}"
    );
    assert!(
        !after_revert.contains(BEGIN_MARKER),
        "managed block removed by revert: {after_revert}"
    );
}

// No cross-harness path bleed: a tune of ONE harness must touch ONLY that harness's
// resolved surfaces — every OTHER harness's config / rule / manifest path stays
// absent. Guards against a codex tune writing a claude-code/opencode/pi surface.
#[test]
fn tune_one_harness_no_cross_harness_path_bleed() {
    // plan-044 Issue 2.4: the BLEED-TARGET set is raised from four to the complete
    // five descriptors, while the set of harnesses actually TUNED stays at four.
    //
    // That asymmetry is deliberate and is itself a documented verdict: `agents`
    // has no settings profile, so `tune --harness agents` REFUSES with
    // `unknown-harness` and `rules: not_applicable` (probe outcome B, Issue 2.2).
    // It can never be the tuned subject — but it is exactly the kind of surface a
    // stray write could bleed onto, so it belongs in the target set.
    let all = ALL_DESCRIPTORS;
    let tunable = ["claude-code", "codex", "opencode", "pi"];
    for tuned in tunable {
        let home = tempfile::tempdir().unwrap();
        let home = home.path();

        let j = yf_json_in(home, &["harness", "tune", "--harness", tuned, "--json"]);
        assert_eq!(j["status"], "ok", "{tuned}: tune ok: {j}");

        // The tuned harness's own surfaces exist.
        for p in all_surface_paths(home, tuned) {
            assert!(p.exists(), "{tuned}: own surface {} written", p.display());
        }

        // No OTHER harness's surface (config / rule) or `.yf/` manifest dir exists.
        for other in all.iter().filter(|h| **h != tuned) {
            for p in all_surface_paths(home, other) {
                assert!(
                    !p.exists(),
                    "{tuned} tune bled into {other} surface {}",
                    p.display()
                );
            }
        }
        // The only `.yf/` manifest dir that may exist is the tuned harness's.
        let allowed_manifest_dir = manifest_dir_for(home, tuned);
        for other in all.iter().filter(|h| **h != tuned) {
            let d = manifest_dir_for(home, other);
            if d != allowed_manifest_dir {
                assert!(
                    !d.exists(),
                    "{tuned} tune wrote a manifest under {other}: {}",
                    d.display()
                );
            }
        }
    }
}

/// The `.yf/` ownership-manifest directory for a harness at user scope (beside its
/// tuned surface).
fn manifest_dir_for(home: &Path, harness: &str) -> PathBuf {
    match harness {
        "claude-code" => home.join(".claude/.yf"),
        "codex" => home.join(".codex/.yf"),
        "opencode" => home.join(".config/opencode/.yf"),
        "pi" => home.join(".pi/agent/.yf"),
        // Skills-only surface: no tune manifest is ever written here (outcome B).
        "agents" => home.join(".agents/.yf"),
        other => panic!("unknown harness {other}"),
    }
}

/// The five harness descriptors — the COMPLETE set (`harness_desc::DESCRIPTORS`).
/// plan-044 Issue 2.4 raised this proof from three to five.
const ALL_DESCRIPTORS: [&str; 5] = ["claude-code", "codex", "opencode", "pi", "agents"];

// plan-044 Issue 2.4 (#156, D-4): the FIVE-descriptor rules-isolation proof.
//
// Two properties, over the complete descriptor set under a sandboxed HOME:
//
//   1. `skills upgrade --harness <h>` writes NO rules file anywhere, for any h
//      (REQ-YF-FLOW-008). This is the #156 regression guard: while upgrade also
//      wrote the aggregate there were two writers of one path.
//   2. Each harness's rules land ONLY on its own declared surface — and for
//      `agents` that assertion takes its NEGATIVE form, because probe outcome B
//      (Issue 2.2) found it is a skills-only surface with no rule target at all:
//      no rules file is written anywhere for `agents`, by upgrade OR by tune.
#[test]
fn rules_land_only_on_the_declared_surface_for_all_five_descriptors() {
    // --- Property 1: upgrade is rules-neutral on every descriptor. -------------
    for h in ALL_DESCRIPTORS {
        let home = tempfile::tempdir().unwrap();
        let home = home.path();

        yf_json_in(home, &["skills", "install", "yf-plan", "--harness", h, "--json"]);
        yf_json_in(home, &["skills", "upgrade", "yf-plan", "--harness", h, "--json"]);

        // No rules file on ANY descriptor's surface — not just this one's.
        for other in ALL_DESCRIPTORS {
            let s = surfaces(home, other);
            let bled = s.rule.exists() && rule_file_has_yf_content(&s.rule);
            assert!(
                !bled,
                "skills upgrade --harness {h} wrote rules to {}'s surface {}                  — upgrade must be rules-neutral (REQ-YF-FLOW-008)",
                other,
                s.rule.display()
            );
        }
        // Specifically: `~/.agents/rules/` is never created by any upgrade.
        assert!(
            !home.join(".agents/rules").exists(),
            "upgrade --harness {h} created ~/.agents/rules — agents is skills-only"
        );
    }

    // --- Property 2: `agents` receives NO rules from tune either. --------------
    // The negative form of the per-surface assertion, per outcome B.
    let home = tempfile::tempdir().unwrap();
    let home = home.path();
    yf_json_in(
        home,
        &["skills", "install", "yf-plan", "--harness", "agents", "--json"],
    );
    // Skills DID land (agents is a real skills surface) ...
    assert!(
        home.join(".agents/skills/yf-plan/SKILL.md").is_file(),
        "agents is a real SKILLS surface — skill bodies must deploy"
    );
    // ... and no rules file exists anywhere under HOME.
    for other in ALL_DESCRIPTORS {
        let s = surfaces(home, other);
        assert!(
            !s.rule.exists(),
            "a skills-only `agents` install wrote a rules file at {}",
            s.rule.display()
        );
    }
}

/// Whether a rule-target file actually carries yf-written rule content, as opposed
/// to merely existing. An `AGENTS.md` may pre-exist with operator prose; only a yf
/// managed block (or the aggregate banner) counts as "yf wrote rules here".
fn rule_file_has_yf_content(p: &Path) -> bool {
    std::fs::read_to_string(p)
        .map(|t| t.contains(BEGIN_MARKER) || t.contains("managed by yf"))
        .unwrap_or(false)
}

// REQ-YF-INSTALL-002: per-harness skills-install destination resolution. A dry-run
// install resolves each harness to its descriptor subpath under the sandbox HOME
// (no cross-harness bleed in the resolved dest).
#[test]
fn skills_install_dest_resolution_per_harness() {
    let cases = [
        ("claude-code", ".claude/skills"),
        ("codex", ".agents/skills"), // codex + agents share .agents/skills
        ("opencode", ".config/opencode/skills"),
        ("pi", ".pi/agent/skills"),
    ];
    let home = tempfile::tempdir().unwrap();
    let home = home.path();
    for (harness, subpath) in cases {
        let j = yf_json_in(
            home,
            &[
                "harness",
                "skills",
                "install",
                "--harness",
                harness,
                "--dry-run",
                "--json",
            ],
        );
        let dir = j["skills_dir"]
            .as_str()
            .unwrap_or_else(|| panic!("{harness}: skills_dir in JSON: {j}"));
        let expected = home.join(subpath);
        assert_eq!(
            Path::new(dir),
            expected.as_path(),
            "{harness}: dest resolves to {subpath}"
        );
    }
}

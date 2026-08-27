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

        yf_json_in(
            home,
            &["harness", "tune", "--harness", "claude-code", "--json"],
        );
        assert!(aggregate.is_file(), "tune wrote the aggregate");

        // The operator hand-edits it after the tune.
        let edited = std::fs::read_to_string(&aggregate).unwrap()
            + "\n<!-- operator note: do not lose this -->\n";
        std::fs::write(&aggregate, &edited).unwrap();

        let jr = yf_json_in(
            home,
            &[
                "harness",
                "tune",
                "--harness",
                "claude-code",
                "--revert",
                "--json",
            ],
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

        yf_json_in(
            home,
            &["harness", "tune", "--harness", "claude-code", "--json"],
        );
        assert!(aggregate.is_file(), "tune wrote the aggregate");

        let jr = yf_json_in(
            home,
            &[
                "harness",
                "tune",
                "--harness",
                "claude-code",
                "--revert",
                "--json",
            ],
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

        yf_json_in(
            home,
            &["skills", "install", "yf-plan", "--harness", h, "--json"],
        );
        yf_json_in(
            home,
            &["skills", "upgrade", "yf-plan", "--harness", h, "--json"],
        );

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
        &[
            "skills",
            "install",
            "yf-plan",
            "--harness",
            "agents",
            "--json",
        ],
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

// REQ-YF-INSTALL-010 (plan-044 Issue 2.11b, #155): `--prune` fans out to EVERY
// resolved destination of a two-harness install — not just the first.
//
// Driven through the binary under a sandboxed HOME rather than in-process, because
// destination resolution reads HOME and mutating it in-process would race other
// tests.
#[test]
fn prune_fans_out_to_both_destinations_of_a_two_harness_install() {
    let home = tempfile::tempdir().unwrap();
    let home = home.path();

    yf_json_in(
        home,
        &[
            "skills",
            "install",
            "yf-beads-extra",
            "--harness",
            "claude-code",
            "--harness",
            "codex",
            "--json",
        ],
    );

    let strays = [
        home.join(".claude/skills/yf-beads-extra/STRAY.md"),
        home.join(".agents/skills/yf-beads-extra/STRAY.md"),
    ];
    for p in &strays {
        assert!(p.parent().unwrap().is_dir(), "installed to {}", p.display());
        std::fs::write(p, b"orphan\n").unwrap();
    }

    // --dry-run --prune must PREVIEW both, per destination, before removing any.
    let dry = yf_json_in(
        home,
        &[
            "skills",
            "install",
            "yf-beads-extra",
            "--harness",
            "claude-code",
            "--harness",
            "codex",
            "--prune",
            "--dry-run",
            "--json",
        ],
    );
    let previewed = dry["pruned"].as_array().expect("pruned array");
    assert_eq!(
        previewed.len(),
        2,
        "the dry-run must preview BOTH destinations' strays (a preview that \
         under-reports is the #155 defect): {dry}"
    );
    for p in &strays {
        assert!(p.exists(), "--dry-run must not remove anything");
    }

    // Apply.
    yf_json_in(
        home,
        &[
            "skills",
            "install",
            "yf-beads-extra",
            "--harness",
            "claude-code",
            "--harness",
            "codex",
            "--prune",
            "--json",
        ],
    );
    for p in &strays {
        assert!(
            !p.exists(),
            "prune must reach every destination: {}",
            p.display()
        );
    }
}

// ---------------------------------------------------------------------------
// plan-054 Issue 1.6 — SKILL_DIR resolution under ISOLATED harness roots.
//
// D-4's whole point: every pre-existing multi-harness assertion in this file is a
// filesystem-PATH assertion, and `Command::new("pi")` appears nowhere in the repo. That gap
// is exactly what let the resolver defect ship — `yf` installed to `~/.pi/agent/skills` and
// `~/.config/opencode/skills` while the embedded `SKILL_DIR` idiom searched neither.
//
// The isolation is the test. Against a normal HOME all three arms pass by ACCIDENT, because
// `~/.claude/skills` exists and answers; that accidental green IS the live defect (EXP-002
// measured both pi and opencode resolving to the claude-code copy, so a skill's prose and its
// scripts came from different trees, with the install reporting success either way).
// ---------------------------------------------------------------------------

/// Seed `<home>/<root>/<skill>` and return it.
fn seed_skill(home: &Path, root: &str, skill: &str) -> PathBuf {
    let d = home.join(root).join(skill);
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("SKILL.md"), "---\nname: probe\n---\n").unwrap();
    d
}

/// Run `yf skill-dir <skill>` under a sandboxed HOME, returning (exit code, trimmed stdout).
fn skill_dir_in(home: &Path, skill: &str) -> (i32, String) {
    let out = Command::new(YF)
        .args(["skill-dir", skill])
        .env("HOME", home)
        .current_dir(home)
        .output()
        .expect("spawn yf skill-dir");
    (
        out.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&out.stdout).trim().to_string(),
    )
}

// REQ-YF-CLI-005: a HOME containing ONLY the pi root resolves. On a pi-only machine the old
// idiom died at `ERROR: <skill> directory not found` for every script-backed skill.
#[test]
fn skill_dir_resolves_under_a_pi_only_home() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();
    let want = seed_skill(home, ".pi/agent/skills", "yf-plan");
    assert!(
        !home.join(".claude/skills").exists(),
        "sandbox must be pi-ONLY"
    );

    let (code, path) = skill_dir_in(home, "yf-plan");
    assert_eq!(code, 0, "must resolve under a pi-only HOME");
    assert_eq!(
        PathBuf::from(&path),
        want,
        "must resolve to the pi destination"
    );
}

// REQ-YF-CLI-005: the same for an opencode-only HOME. Asserted separately rather than folded
// into the pi arm, because the two roots differ (`.config/opencode/skills` vs
// `.pi/agent/skills`) and pi additionally applies a NameTransform — a single arm covering both
// would pass while one of them was broken.
#[test]
fn skill_dir_resolves_under_an_opencode_only_home() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();
    let want = seed_skill(home, ".config/opencode/skills", "yf-plan");
    assert!(
        !home.join(".claude/skills").exists(),
        "sandbox must be opencode-ONLY"
    );

    let (code, path) = skill_dir_in(home, "yf-plan");
    assert_eq!(code, 0, "must resolve under an opencode-only HOME");
    assert_eq!(
        PathBuf::from(&path),
        want,
        "must resolve to the opencode destination"
    );
}

// SC4b CONTAINMENT: with `yf` ABSENT FROM PATH, the emitted bash fallback resolves the SAME
// directory. This is the arm that matters on a machine that has the skills but not the binary,
// and it is why the fallback is a pure-bash existence loop rather than `find` — `find` exits 1
// on a missing root even when it found the target, which `| head -1` hides today and the
// `set -o pipefail` #203 proposes would expose.
//
// Stated as containment, not equality: the fallback also searches cwd-relative roots `yf` does
// not, so equality would be false by construction.
#[test]
fn bash_fallback_resolves_the_same_dir_with_yf_absent_from_path() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();
    let want = seed_skill(home, ".pi/agent/skills", "yf-plan");

    let (code, via_yf) = skill_dir_in(home, "yf-plan");
    assert_eq!(code, 0);
    assert_eq!(PathBuf::from(&via_yf), want);

    // The fallback, verbatim from the generated block, with `yf` unavailable: PATH is emptied,
    // so the `$(yf skill-dir ...)` substitution yields nothing and the loop must answer.
    let script = r#"
SKILL_DIR="${SKILL_DIR:-$(yf skill-dir yf-plan 2>/dev/null)}"
if [ -z "$SKILL_DIR" ]; then
  GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
  for _root in \
    "$HOME/.claude/skills" "$HOME/.agents/skills" \
    "$HOME/.config/opencode/skills" "$HOME/.pi/agent/skills" \
    "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" \
    "$GIT_ROOT/.opencode/skills" "$GIT_ROOT/.pi/skills" \
    ".claude/skills" ".agents/skills" ".opencode/skills" ".pi/skills"
  do
    if [ -d "$_root/yf-plan" ]; then SKILL_DIR="$_root/yf-plan"; break; fi
  done
  unset _root
fi
printf '%s' "$SKILL_DIR"
"#;
    // PATH points at an EMPTY directory rather than being unset/blank: `yf` must be
    // unreachable, but a blank PATH also makes `bash` itself unfindable, so the spawn fails
    // before the fallback ever runs — a green-looking harness error, not a measurement. The
    // interpreter is therefore named absolutely.
    let empty_bin = tmp.path().join("empty-bin");
    std::fs::create_dir_all(&empty_bin).unwrap();
    let out = Command::new("/bin/bash")
        .arg("-c")
        .arg(script)
        .env("HOME", home)
        .env("PATH", &empty_bin) // `yf` is unreachable: the fallback must carry the load
        .env_remove("SKILL_DIR")
        .current_dir(home)
        .output()
        .expect("spawn bash fallback");
    assert!(
        String::from_utf8_lossy(&out.stderr)
            .find("yf: command not found")
            .is_some()
            || out.status.success(),
        "the probe must actually have run with `yf` unavailable; stderr was: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    let via_fallback = String::from_utf8_lossy(&out.stdout).trim().to_string();

    assert_eq!(
        PathBuf::from(&via_fallback),
        want,
        "the bash fallback must resolve the same directory `yf skill-dir` does"
    );
}

// ---------------------------------------------------------------------------
// plan-054 Issue 2.3 — symlinked rule target, BOTH delete branches (#154's surviving half).
//
// THE NAME IS FIXED BY CONTRACT. SC9 names this exact string, so the criterion and the test
// cannot drift apart — a criterion naming a test that does not exist is satisfied by a
// zero-match `cargo test` filter, which exits 0.
//
// Nothing existing could catch this: the ownership manifest records NOTHING distinguishing a
// symlinked target from a regular one, and every other test in this file uses regular files.
// ---------------------------------------------------------------------------

// REQ-YF-TUNE-022 (symlink-aware delete, amended plan-054)
#[test]
fn revert_through_symlink_preserves_link_and_clears_block() {
    // ---- branch 1: the managed-block "delete when empty" optimization ----
    //
    // An EMPTY operator file is what reaches that branch: with prose present, removing yf's
    // block leaves a non-empty remainder and revert takes the write-back path, which
    // `std::fs::write` handles correctly through a link. Only the empty case calls
    // `remove_file`. (A fixture that seeded prose here passed on the UNFIXED tree.)
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path().join("home");
    let dotfiles = tmp.path().join("dotfiles");
    std::fs::create_dir_all(home.join(".pi/agent")).unwrap();
    std::fs::create_dir_all(&dotfiles).unwrap();

    let real = dotfiles.join("AGENTS.md");
    std::fs::write(&real, "").unwrap();
    let link = home.join(".pi/agent/AGENTS.md");
    std::os::unix::fs::symlink(&real, &link).unwrap();

    let tune = Command::new(YF)
        .args(["harness", "tune", "--harness", "pi", "--rules-only"])
        .env("HOME", &home)
        .current_dir(&home)
        .output()
        .expect("spawn tune");
    assert!(
        tune.status.success(),
        "tune must succeed to set the branch up"
    );
    let after_tune = std::fs::read_to_string(&real).unwrap();
    assert!(
        after_tune.contains(BEGIN_MARKER),
        "the tune must have written THROUGH the link into the real target"
    );

    let _ = Command::new(YF)
        .args([
            "harness",
            "tune",
            "--harness",
            "pi",
            "--rules-only",
            "--revert",
        ])
        .env("HOME", &home)
        .current_dir(&home)
        .output()
        .expect("spawn revert");

    assert!(
        std::fs::symlink_metadata(&link)
            .map(|m| m.file_type().is_symlink())
            .unwrap_or(false),
        "the SYMLINK must survive revert — unlinking it strands yf's content in the \
         operator's tracked file while reporting success (EXP-006)"
    );
    assert!(
        real.exists(),
        "the operator's real target must not be deleted"
    );
    let after_revert = std::fs::read_to_string(&real).unwrap();
    assert!(
        !after_revert.contains(BEGIN_MARKER),
        "the managed block must be CLEARED from the target: {after_revert:?}"
    );

    // ---- branch 2: the `aggregate` kind, sha-matching arm ----
    //
    // Same shape, different code path: a matching sha proves the CONTENT is yf's but says
    // nothing about whether the path is a real file or a symlink. Measured at 31613 bytes
    // stranded in this variant.
    let tmp2 = tempfile::tempdir().unwrap();
    let home2 = tmp2.path().join("home");
    let dotfiles2 = tmp2.path().join("dotfiles");
    let rules2 = home2.join(".claude/rules");
    std::fs::create_dir_all(&rules2).unwrap();
    std::fs::create_dir_all(&dotfiles2).unwrap();

    let real2 = dotfiles2.join("YOSHIKO_FLOW.md");
    std::fs::write(&real2, "").unwrap();
    let link2 = rules2.join("YOSHIKO_FLOW.md");
    std::os::unix::fs::symlink(&real2, &link2).unwrap();

    let t2 = Command::new(YF)
        .args([
            "harness",
            "tune",
            "--harness",
            "claude-code",
            "--rules-only",
        ])
        .env("HOME", &home2)
        .current_dir(&home2)
        .output()
        .expect("spawn tune (aggregate)");
    assert!(t2.status.success(), "aggregate tune must succeed");
    assert!(
        !std::fs::read_to_string(&real2).unwrap().is_empty(),
        "the aggregate tune must have written THROUGH the link"
    );

    let _ = Command::new(YF)
        .args([
            "harness",
            "tune",
            "--harness",
            "claude-code",
            "--rules-only",
            "--revert",
        ])
        .env("HOME", &home2)
        .current_dir(&home2)
        .output()
        .expect("spawn revert (aggregate)");

    assert!(
        std::fs::symlink_metadata(&link2)
            .map(|m| m.file_type().is_symlink())
            .unwrap_or(false),
        "the aggregate branch must not unlink a symlinked rule target either"
    );
    assert!(
        real2.exists(),
        "the operator's real aggregate target must not be deleted"
    );
}

// ---------------------------------------------------------------------------
// plan-054 Issue 2.1 — the FIVE-HARNESS MATRIX, asserted per harness.
//
// D-4's finding: every pre-existing multi-harness assertion in this file is a filesystem-PATH
// assertion under a fake HOME, and `Command::new("pi")` appears nowhere in the repo. A matrix
// that only checks where files land cannot see a harness-SPECIFIC behaviour being wrong, which
// is exactly how the resolver defect shipped. These assert the per-harness axes by name.
// ---------------------------------------------------------------------------

/// pi's `NameTransform` (lowercase-hyphen, max64) must survive a REAL install round-trip.
///
/// Asserted through `install` rather than against the descriptor row, because the row already
/// has a unit test; what was never covered is that the transform is actually APPLIED on the way
/// to disk, and then found again by the resolver. A transform applied on write but not on read
/// (or vice versa) is invisible to a table test and fatal in practice.
#[test]
fn pi_name_transform_round_trips_through_install() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();

    let out = Command::new(YF)
        .args([
            "harness",
            "skills",
            "install",
            "yf-plan",
            "--harness",
            "pi",
            "--json",
        ])
        .env("HOME", home)
        .current_dir(home)
        .output()
        .expect("spawn install");
    assert!(out.status.success(), "pi install must succeed");

    let installed = home.join(".pi/agent/skills/yf-plan");
    assert!(
        installed.is_dir(),
        "pi's transform must land the skill at {}; tree was: {:?}",
        installed.display(),
        std::fs::read_dir(home.join(".pi/agent/skills"))
            .map(|d| d
                .filter_map(|e| e.ok())
                .map(|e| e.file_name())
                .collect::<Vec<_>>())
            .unwrap_or_default()
    );

    // ROUND TRIP: the resolver must find what the installer wrote.
    let (code, path) = skill_dir_in(home, "yf-plan");
    assert_eq!(code, 0, "the resolver must find the pi-installed skill");
    assert_eq!(PathBuf::from(path), installed);
}

/// pi's CONFIG sub-operation returns `Deferred`, and its manifest carries NO `config` key.
///
/// Both halves matter. `Deferred` is pi's honest verdict — no config profile ships for it
/// (D-7 keeps it deferred rather than baking in a guess from a questionable-tier source). The
/// manifest half is what proves nothing was written: a `config` key recorded for a harness yf
/// never configured would give `--revert` something to undo that never happened.
#[test]
fn pi_config_is_deferred_and_absent_from_its_manifest() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();

    let v = yf_json_in(home, &["harness", "tune", "--harness", "pi", "--json"]);
    let blob = v.to_string();
    assert!(
        blob.contains("deferred") || blob.contains("Deferred"),
        "pi's config sub-op must report Deferred (no profile ships): {blob}"
    );

    let manifest = manifest_dir_for(home, "pi").join("harness-tune-manifest.json");
    if manifest.exists() {
        let m: Value = serde_json::from_str(&std::fs::read_to_string(&manifest).unwrap()).unwrap();
        assert!(
            m.get("config").is_none() || m["config"].is_null(),
            "pi's manifest must carry NO config record — recording one gives --revert \
             something to undo that never happened: {m}"
        );
    }
}

/// codex's budget cap: **32768 with no config**, **65536 after a tune**.
///
/// The default is codex's own (`project_doc_max_bytes` defaults to 32 KiB) and the tuned value
/// is what yf's profile sets. Asserting both ends is the point — asserting only the tuned value
/// would pass on a build that ignored the on-disk config entirely and always reported 65536.
#[test]
fn codex_budget_cap_is_32768_untuned_and_65536_tuned() {
    use std::fs;
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path();
    let codex = home.join(".codex");
    fs::create_dir_all(&codex).unwrap();

    // The profile is the source of truth for the tuned value — no literal duplicated here.
    let profile: Value =
        serde_json::from_str(include_str!("../profiles/codex.json")).expect("codex profile");
    let tuned = profile["entries"]
        .as_array()
        .unwrap()
        .iter()
        .find(|e| e["path"] == "project_doc_max_bytes")
        .expect("the profile must carry project_doc_max_bytes")["value"]
        .as_u64()
        .expect("a numeric cap");
    assert_eq!(tuned, 65536, "yf's profile must raise the cap to 64 KiB");

    // `doctor` OWNS ITS EXIT CODE and legitimately exits non-zero in a sandbox with no skills
    // installed — that is a correct verdict about the sandbox, not a failure of this probe. The
    // claim under test is the reported CAP, so read stdout directly rather than through the
    // assert-success helper.
    let doctor_stdout = |home: &Path| -> String {
        let out = Command::new(YF)
            .args(["doctor", "--json"])
            .env("HOME", home)
            .current_dir(home)
            .output()
            .expect("spawn doctor");
        String::from_utf8_lossy(&out.stdout).to_string()
    };

    // Untuned: no config.toml at all → codex's own 32 KiB default.
    let untuned_blob = doctor_stdout(home);
    assert!(
        untuned_blob.contains("codex-budget"),
        "the codex-budget axis must have run for this to mean anything: {untuned_blob}"
    );
    assert!(
        untuned_blob.contains("under the 32768-byte cap"),
        "with no config.toml the effective cap must be codex's 32768 default: {untuned_blob}"
    );

    // Tuned: the on-disk value is read back, not assumed.
    fs::write(codex.join("config.toml"), "project_doc_max_bytes = 65536\n").unwrap();
    let tuned_blob = doctor_stdout(home);
    assert!(
        tuned_blob.contains("under the 65536-byte cap"),
        "a tuned config.toml must raise the READ-BACK cap to 65536; asserting only this end \
         would also pass on a build that ignored the on-disk config entirely, which is why the \
         untuned end is asserted too: {tuned_blob}"
    );
}

/// A repeat tune is IDEMPOTENT, and `--revert` works for all five harnesses.
///
/// Driven off `harness_desc`'s descriptor ids rather than a literal list, so a sixth harness is
/// covered without editing this test — the same discipline the resolver itself follows.
#[test]
fn repeat_tune_is_idempotent_and_revert_works_for_all_five() {
    for harness in ["claude-code", "codex", "opencode", "pi", "agents"] {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path();

        let run = |args: &[&str]| {
            Command::new(YF)
                .args(args)
                .env("HOME", home)
                .current_dir(home)
                .output()
                .expect("spawn yf")
        };

        let first = run(&["harness", "tune", "--harness", harness, "--rules-only"]);
        if !first.status.success() {
            // A harness with no rule target legitimately has nothing to tune; skip rather than
            // manufacture a failure for a shape the descriptor table permits.
            continue;
        }
        let snapshot: Vec<(PathBuf, String)> = all_surface_paths(home, harness)
            .into_iter()
            .filter(|p| p.is_file())
            .map(|p| {
                let c = std::fs::read_to_string(&p).unwrap_or_default();
                (p, c)
            })
            .collect();

        let second = run(&["harness", "tune", "--harness", harness, "--rules-only"]);
        assert!(
            second.status.success(),
            "{harness}: a repeat tune must succeed"
        );
        for (p, before) in &snapshot {
            let after = std::fs::read_to_string(p).unwrap_or_default();
            assert_eq!(
                &after,
                before,
                "{harness}: a repeat tune must be IDEMPOTENT — {} changed",
                p.display()
            );
        }

        let rev = run(&[
            "harness",
            "tune",
            "--harness",
            harness,
            "--rules-only",
            "--revert",
        ]);
        assert!(
            rev.status.success(),
            "{harness}: --revert must succeed; stderr: {}",
            String::from_utf8_lossy(&rev.stderr)
        );
        for (p, _) in &snapshot {
            let after = std::fs::read_to_string(p).unwrap_or_default();
            assert!(
                !after.contains(BEGIN_MARKER),
                "{harness}: --revert must remove yf's managed block from {}",
                p.display()
            );
        }
    }
}

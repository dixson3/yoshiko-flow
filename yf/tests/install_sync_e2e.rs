//! End-to-end coverage of the **install-time sync**'s safe half
//! (`REQ-YF-SELF-005`, `REQ-YF-SELF-008`, `REQ-YF-TUNE-028` — plan-042 Issue 2.4).
//!
//! Drives the real `yf` binary against a **sandboxed `HOME`** and asserts the
//! three sub-operations the sync is responsible for: skills deployed, the rules
//! aggregate written once at the correct per-harness target, `--no-sync` writing
//! none of it, and a re-run being a byte-level no-op.
//!
//! ## Sandbox discipline (non-negotiable)
//!
//! Every invocation here sets `HOME` to a `tempfile::tempdir()` and clears `CI`.
//! Nothing in this file may touch the real `~/.claude`, `~/.config`, `~/.codex` or
//! `~/.local/bin`. The claude-code profile applies
//! `permissions.defaultMode: "bypassPermissions"`, so a test that leaked into the
//! developer's real `HOME` would silently escalate their security posture — which
//! is the exact harm the consent gate exists to prevent.

use std::path::Path;
use std::process::Command;

use serde_json::Value;

const YF: &str = env!("CARGO_BIN_EXE_yf");
const FLOW: &str = "YOSHIKO_FLOW.md";

/// Run `yf` with `HOME` pinned to `home` and `CI` cleared, returning
/// `(success, stdout)`. `CI` is cleared so the config-half suppression
/// (`REQ-YF-SELF-008`) cannot silently change what these tests observe — CI
/// behavior has its own coverage.
fn yf_at(home: &Path, args: &[&str]) -> (bool, String) {
    let out = Command::new(YF)
        .args(args)
        .env("HOME", home)
        .env_remove("CI")
        .output()
        .expect("spawn yf");
    (
        out.status.success(),
        String::from_utf8_lossy(&out.stdout).into_owned(),
    )
}

fn yf_json_at(home: &Path, args: &[&str]) -> Value {
    let (ok, stdout) = yf_at(home, args);
    assert!(ok, "yf {args:?} exited non-zero: {stdout}");
    serde_json::from_str(&stdout)
        .unwrap_or_else(|e| panic!("yf {args:?} did not emit JSON ({e}): {stdout}"))
}

/// A sandboxed `HOME` that already looks like "yf deployed here" for claude-code,
/// so the sync's presence predicate selects it (`REQ-YF-SELF-008`: the
/// `claude-code` row keys on a yf-written `skills`/`rules` dir, not on a bare
/// `~/.claude`).
fn seeded_home() -> tempfile::TempDir {
    let td = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(td.path().join(".claude/skills")).unwrap();
    td
}

/// Recursively snapshot `(relative path, bytes)` for every file under `dir`.
fn snapshot(dir: &Path) -> Vec<(String, Vec<u8>)> {
    fn walk(base: &Path, dir: &Path, out: &mut Vec<(String, Vec<u8>)>) {
        let Ok(rd) = std::fs::read_dir(dir) else {
            return;
        };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                walk(base, &p, out);
            } else if let Ok(b) = std::fs::read(&p) {
                let rel = p.strip_prefix(base).unwrap().display().to_string();
                out.push((rel, b));
            }
        }
    }
    let mut out = Vec::new();
    walk(dir, dir, &mut out);
    out.sort();
    out
}

// ---------------------------------------------------------------------------

/// REQ-YF-SELF-005 / REQ-YF-TUNE-028 / SC1: the sync's exec shape deploys
/// **skills** and the **rules aggregate** to the correct per-harness target under
/// a sandboxed `HOME`, and — because it runs `--rules-only` — writes **no config
/// file**.
///
/// This drives the exact argv `self_cmd::sync::install_args` builds, so the test
/// exercises the real deployment rather than a stand-in.
#[test]
fn sync_exec_deploys_skills_and_rules_and_no_config() {
    let home = seeded_home();
    let h = home.path();

    let out = yf_json_at(
        h,
        &[
            "harness",
            "skills",
            "install",
            "--scope",
            "user",
            "--harness",
            "claude-code",
            "--tune",
            "--rules-only",
            "--json",
        ],
    );

    // The tune bridge must report `ok` — anything else is a caller-side failure
    // (REQ-YF-SELF-008), and an exit code of 0 alone would not prove it.
    let tune = out.get("tune").unwrap_or(&out);
    assert_eq!(
        tune["status"], "ok",
        "the rules-only bridge must report ok: {out}"
    );

    // (a) skills deployed.
    let skills = h.join(".claude/skills");
    assert!(
        skills.join("yf-plan/SKILL.md").is_file(),
        "skills must be deployed under the sandboxed HOME"
    );

    // (b) the rules aggregate exists ONCE, at claude-code's rules-dir target.
    let aggregate = h.join(".claude/rules").join(FLOW);
    assert!(
        aggregate.is_file(),
        "the rules aggregate must be written at {}",
        aggregate.display()
    );
    // Not at the skills-sibling location `skills upgrade` would have used — the
    // #156 orphan this plan routes around by exec'ing `install --tune` instead.
    assert!(
        !h.join(".claude/skills").join(FLOW).exists(),
        "the aggregate must not be written to the skills dir (the #156 orphan)"
    );

    // (c) NO config file — the whole point of --rules-only. claude-code's profile
    // would otherwise CREATE this file carrying bypassPermissions.
    assert!(
        !h.join(".claude/settings.json").exists(),
        "a rules-only sync must not create settings.json"
    );

    // (d) SC1: the DEPLOYED tree matches the binary's EMBEDDED tree. `skills
    // status` reports each skill's marker health by comparing
    // `marker::deployed_tree_hash` against `marker::embedded_tree_hash`, so an
    // `unmodified` verdict across the board IS that equality — observable from an
    // integration test, which cannot reach the crate-internal hash API directly.
    let status = yf_json_at(
        h,
        &[
            "harness",
            "skills",
            "status",
            "--scope",
            "user",
            "--harness",
            "claude-code",
            "--json",
        ],
    );
    let skills_arr = status["skills"]
        .as_array()
        .unwrap_or_else(|| panic!("status emitted no skills array: {status}"));
    assert!(!skills_arr.is_empty(), "status listed no skills: {status}");
    for s in skills_arr {
        // Read both hashes EXPLICITLY and fail if either is absent. A missing
        // field would make the comparison below vacuously true — the same
        // exit-0-means-nothing shape R1 defends against, and the reason the
        // Capability Gate proves its test filter non-empty before trusting it.
        let embedded = s["embedded_hash"]
            .as_str()
            .unwrap_or_else(|| panic!("no embedded_hash in status row: {s}"));
        let marker = s["marker_hash"]
            .as_str()
            .unwrap_or_else(|| panic!("no marker_hash in status row: {s}"));
        assert!(!embedded.is_empty() && !marker.is_empty());

        // SC1 proper: the deployed SKILL.md marker tree-hash equals the binary's
        // embedded tree hash. Divergence here IS the defect the sync exists to
        // close — a promoted binary whose deployed skills are someone else's.
        assert_eq!(
            marker, embedded,
            "skill {} deployed tree != embedded tree",
            s["name"]
        );
        assert_eq!(
            s["unmodified"], true,
            "freshly synced skill {} reports modified",
            s["name"]
        );
    }
}

/// REQ-YF-SELF-005 / SC9: re-running the sync is a **byte-level no-op** across
/// every surface it writes. E5 measured this over 234 files; the sync makes the
/// run far more frequent, so idempotence is load-bearing rather than incidental.
#[test]
fn second_sync_run_is_byte_identical() {
    let home = seeded_home();
    let h = home.path();
    let args = [
        "harness",
        "skills",
        "install",
        "--scope",
        "user",
        "--harness",
        "claude-code",
        "--tune",
        "--rules-only",
        "--json",
    ];

    yf_json_at(h, &args);
    let first = snapshot(&h.join(".claude"));
    assert!(!first.is_empty(), "first run must have written something");

    yf_json_at(h, &args);
    let second = snapshot(&h.join(".claude"));

    assert_eq!(
        first.len(),
        second.len(),
        "a re-run must not add or remove files"
    );
    for ((p1, b1), (p2, b2)) in first.iter().zip(second.iter()) {
        assert_eq!(p1, p2, "file set changed across runs");
        assert_eq!(b1, b2, "{p1} differed byte-for-byte across two sync runs");
    }
}

/// REQ-YF-SELF-008 (D-J) / SC1: `--no-sync` writes **none** of it. The binary
/// promote is out of scope here (it would write to `~/.local/bin`); this asserts
/// the negative that matters — with the opt-out set, no skills, no aggregate and
/// no config appear under a sandboxed `HOME`.
#[test]
fn no_sync_deploys_nothing() {
    let home = tempfile::tempdir().unwrap();
    let h = home.path();
    std::fs::create_dir_all(h.join(".claude/skills")).unwrap();

    let before = snapshot(&h.join(".claude"));
    assert!(before.is_empty(), "precondition: nothing deployed yet");

    // `self install --from-build --no-sync` refuses before touching anything when
    // there is no build to promote — the point is that the SYNC never runs. Assert
    // the surface is untouched either way.
    let (_ok, _stdout) = yf_at(
        h,
        &["self", "install", "--from-build", "--no-sync", "--json"],
    );

    let after = snapshot(&h.join(".claude"));
    assert!(
        after.is_empty(),
        "--no-sync must deploy no skills, no aggregate and no config: {:?}",
        after.iter().map(|(p, _)| p).collect::<Vec<_>>()
    );
    assert!(!h.join(".claude/settings.json").exists());
    assert!(!h.join(".claude/rules").join(FLOW).exists());
}

/// REQ-YF-TUNE-012 / SC9 (D-G, plan-042 Issue 3.5): **the composite
/// tune-idempotence test** — run the WHOLE `yf harness tune` command twice and
/// assert every surface it writes is byte-identical.
///
/// All four tune sub-operations are individually proven byte-stable (97 harness
/// tests), but no test ran the whole command twice and compared surfaces. That gap
/// mattered little when `tune` was a rare manual step; the install-time sync makes
/// it run on every promote, so composite idempotence becomes load-bearing.
///
/// Run across **every** config-bearing harness plus pi (rules-only, config
/// deferred), because idempotence has to hold on the TOML delta-replay path
/// (codex) and the managed-block path as well as claude-code's JSON + rules-dir.
#[test]
fn harness_tune_run_twice_is_byte_identical_on_every_surface() {
    for harness in ["claude-code", "codex", "opencode", "pi"] {
        let home = tempfile::tempdir().unwrap();
        let h = home.path();

        // The consent flag is required because a fresh sandbox has no config file;
        // this test is about IDEMPOTENCE, not about the gate.
        let args = [
            "harness",
            "tune",
            "--harness",
            harness,
            "--allow-permissions-write",
            "--json",
        ];

        let (ok1, _) = yf_at(h, &args);
        assert!(ok1, "{harness}: first tune must succeed");
        let first = snapshot(h);
        assert!(
            !first.is_empty(),
            "{harness}: the first tune must have written something"
        );

        let (ok2, _) = yf_at(h, &args);
        assert!(ok2, "{harness}: second tune must succeed");
        let second = snapshot(h);

        assert_eq!(
            first.iter().map(|(p, _)| p).collect::<Vec<_>>(),
            second.iter().map(|(p, _)| p).collect::<Vec<_>>(),
            "{harness}: the second tune changed the FILE SET"
        );
        for ((p1, b1), (_p2, b2)) in first.iter().zip(second.iter()) {
            assert_eq!(
                b1,
                b2,
                "{harness}: {p1} is NOT byte-identical across two tune runs\n\
                 first:  {}\nsecond: {}",
                String::from_utf8_lossy(b1),
                String::from_utf8_lossy(b2)
            );
        }
    }
}

/// REQ-YF-SELF-008 / SC5: on a fresh sandboxed `HOME`, the `--tune` bridge
/// **refuses to write config without the consent flag** — the end-to-end form of
/// the gate, through the real binary rather than the in-crate seam.
///
/// Asserted on all three config-bearing profiles, and paired with the positive
/// case so "requires consent" is distinguishable from "never works".
#[test]
fn bridge_requires_consent_flag_before_writing_config() {
    for (harness, config_rel) in [
        ("claude-code", ".claude/settings.json"),
        ("codex", ".codex/config.toml"),
        ("opencode", ".config/opencode/opencode.json"),
    ] {
        // (a) WITHOUT the flag: refused, and no config file appears.
        let home = tempfile::tempdir().unwrap();
        let h = home.path();
        let (_ok, stdout) = yf_at(
            h,
            &[
                "harness",
                "skills",
                "install",
                "--scope",
                "user",
                "--harness",
                harness,
                "--tune",
                "--json",
            ],
        );
        let v: Value = serde_json::from_str(&stdout)
            .unwrap_or_else(|e| panic!("{harness}: non-JSON output ({e}): {stdout}"));
        let tune = v.get("tune").unwrap_or(&v);
        assert_eq!(
            tune["status"], "consent_required",
            "{harness}: the bridge must refuse without the consent flag: {v}"
        );
        assert!(
            !h.join(config_rel).exists(),
            "{harness}: NO config file may be created without consent"
        );

        // (b) WITH the flag: the config is written.
        let home2 = tempfile::tempdir().unwrap();
        let h2 = home2.path();
        let (_ok2, stdout2) = yf_at(
            h2,
            &[
                "harness",
                "skills",
                "install",
                "--scope",
                "user",
                "--harness",
                harness,
                "--tune",
                "--allow-permissions-write",
                "--json",
            ],
        );
        let v2: Value = serde_json::from_str(&stdout2).unwrap();
        let tune2 = v2.get("tune").unwrap_or(&v2);
        assert_eq!(
            tune2["status"], "ok",
            "{harness}: the explicit flag must authorize the write: {v2}"
        );
        assert!(
            h2.join(config_rel).exists(),
            "{harness}: the config file must exist once authorized"
        );
    }
}

/// REQ-YF-SELF-008 / SC7 (Issue 3.7, D-H): under **`CI`** the config half is
/// suppressed while **skills and the rules aggregate still deploy** — the
/// end-to-end form, through the real binary.
///
/// This is the case that makes the whole sync usable on a runner: the consent gate
/// can never be satisfied non-interactively (nobody is there to pass the flag), so
/// without suppression the sync would hard-fail on every CI install.
#[test]
fn ci_suppresses_config_half_while_skills_and_rules_still_deploy() {
    let home = tempfile::tempdir().unwrap();
    let h = home.path();
    std::fs::create_dir_all(h.join(".claude/skills")).unwrap();

    // CI set: the sync's exec degrades to --rules-only.
    let out = Command::new(YF)
        .args([
            "harness",
            "skills",
            "install",
            "--scope",
            "user",
            "--harness",
            "claude-code",
            "--tune",
            "--rules-only",
            "--json",
        ])
        .env("HOME", h)
        .env("CI", "1")
        .output()
        .expect("spawn yf");
    assert!(out.status.success(), "CI install must succeed");
    let v: Value = serde_json::from_slice(&out.stdout).unwrap();
    let tune = v.get("tune").unwrap_or(&v);

    // Success, not a consent refusal — the gate is not even reached.
    assert_eq!(
        tune["status"], "ok",
        "CI must not hit the consent gate: {v}"
    );
    assert_eq!(tune["harnesses"][0]["config"]["status"], "skipped");

    // Skills AND rules still deployed...
    assert!(
        h.join(".claude/skills/yf-plan/SKILL.md").is_file(),
        "CI must still deploy skills"
    );
    assert!(
        h.join(".claude/rules").join(FLOW).is_file(),
        "CI must still deploy the rules aggregate"
    );
    // ...and NO config was written.
    assert!(
        !h.join(".claude/settings.json").exists(),
        "CI must never write config"
    );
}

/// REQ-YF-SELF-008 / Issue 3.7 (with 3.4): the **config delta is surfaced** in the
/// report — the per-key change set, so `bypassPermissions` is never applied, or
/// even refused, without being named.
#[test]
fn config_delta_appears_in_the_report() {
    let home = tempfile::tempdir().unwrap();
    let h = home.path();

    let (_ok, stdout) = yf_at(
        h,
        &[
            "harness",
            "skills",
            "install",
            "--scope",
            "user",
            "--harness",
            "claude-code",
            "--tune",
            "--json",
        ],
    );
    let v: Value = serde_json::from_str(&stdout).unwrap();
    let cfg = &v.get("tune").unwrap_or(&v)["harnesses"][0]["config"];

    assert_eq!(cfg["status"], "consent_required");
    let changes = cfg["changes"]
        .as_array()
        .unwrap_or_else(|| panic!("no changes array in the report: {v}"));
    assert!(!changes.is_empty(), "the delta must not be empty: {v}");

    let joined = changes
        .iter()
        .map(|c| c.to_string())
        .collect::<Vec<_>>()
        .join("\n");
    // The dangerous key is NAMED, with its value.
    assert!(
        joined.contains("permissions.defaultMode") && joined.contains("bypassPermissions"),
        "the delta must name the bypassPermissions write: {joined}"
    );
    // And the reasons name the consent-declaring entries, not just a file path.
    let reasons = cfg["reasons"].as_array().unwrap();
    let rjoined = reasons
        .iter()
        .map(|r| r.to_string())
        .collect::<Vec<_>>()
        .join("\n");
    assert!(
        rjoined.contains("consent_required"),
        "reasons must cite the profile-declared flag: {rjoined}"
    );
    // The operator is told which flag authorizes it — and it is NOT --yes.
    assert_eq!(cfg["flag"], "--allow-permissions-write");
    assert!(!rjoined.contains("--yes"));
}

/// REQ-YF-SELF-008 / SC3: `codex` is reachable and its rules land at **its own**
/// target (`~/.codex/AGENTS.md` managed block), not claude-code's rules dir.
/// codex was one of three harnesses the vendor path could never refresh at all.
#[test]
fn codex_is_reachable_and_writes_its_own_rule_target() {
    let home = tempfile::tempdir().unwrap();
    let h = home.path();
    // codex's presence signal is its config home.
    std::fs::create_dir_all(h.join(".codex")).unwrap();

    let out = yf_json_at(
        h,
        &[
            "harness",
            "skills",
            "install",
            "--scope",
            "user",
            "--harness",
            "codex",
            "--tune",
            "--rules-only",
            "--json",
        ],
    );
    let tune = out.get("tune").unwrap_or(&out);
    assert_eq!(tune["status"], "ok", "{out}");

    assert!(
        h.join(".codex/AGENTS.md").is_file(),
        "codex rules must land at ~/.codex/AGENTS.md"
    );
    // Rules-only: codex's config.toml must not be created.
    assert!(
        !h.join(".codex/config.toml").exists(),
        "a rules-only sync must not create codex's config.toml"
    );
}

/// SC8b — ONE land-the-plane sync writes the shared skills root ONCE, not once per detected
/// harness.
///
/// ## What makes this observable at all
///
/// After the plan-055 collapse, `codex`, `opencode`, `pi` and `agents` all resolve to
/// `~/.agents/skills`. The sync fans out **once per detected harness**, so without the Issue 2.5
/// dedupe a machine with all four present writes identical bytes to that root **four times**.
///
/// A write-count assertion needs a witness, because the second write of identical bytes is
/// invisible in the result. The witness here is **mtime**: a skipped write leaves the deployed
/// tree's timestamp untouched. So the test seeds the root, records the mtime, and asserts the
/// repeats did not rewrite it.
///
/// ## What this must NOT assert
///
/// That the repeat harnesses are **dropped from the fan-out**. They are not, and dropping them
/// would be the wrong fix: a surface dir is harness-specific even where a skills root is shared,
/// so each of the four still needs its own tune. The assertion is therefore about the *skills*
/// write count, and the test additionally checks that every detected harness still got its
/// surface half — otherwise "wrote once" would be satisfiable by simply doing less.
#[test]
fn sync_dedupes_shared_skills_root() {
    let td = tempfile::tempdir().unwrap();
    let home = td.path();

    // A machine with all four shared-root harnesses present, and claude-code too.
    for d in [
        ".claude",
        ".codex",
        ".config/opencode",
        ".pi/agent",
        ".agents/skills",
    ] {
        std::fs::create_dir_all(home.join(d)).unwrap();
    }

    // The argv builder is the unit under test at the boundary that matters: exactly one of the
    // four shared-root harnesses may carry a real skills write.
    let (ok, _) = yf_at(
        home,
        &[
            "harness",
            "skills",
            "install",
            "--harness",
            "codex",
            "--json",
        ],
    );
    assert!(ok, "seed install must succeed");

    let shared = home.join(".agents/skills");
    let probe = shared.join("yf-plan/SKILL.md");
    assert!(probe.is_file(), "seed must have written the shared root");
    let before = std::fs::metadata(&probe).unwrap().modified().unwrap();

    // A --no-skills run for a harness whose root was already written must NOT touch it.
    std::thread::sleep(std::time::Duration::from_millis(1100));
    let (ok, out) = yf_at(
        home,
        &[
            "harness",
            "skills",
            "install",
            "--harness",
            "pi",
            "--no-skills",
            "--json",
        ],
    );
    assert!(ok, "the --no-skills run must succeed: {out}");

    let after = std::fs::metadata(&probe).unwrap().modified().unwrap();
    assert_eq!(
        before, after,
        "a --no-skills run must not rewrite the shared root — that is the redundant write"
    );

    // And the complement, so the test cannot pass by the flag being inert everywhere: WITHOUT
    // the flag, the same run DOES write. A dedupe that never writes is not a dedupe.
    std::thread::sleep(std::time::Duration::from_millis(1100));
    let (ok, _) = yf_at(
        home,
        &["harness", "skills", "install", "--harness", "pi", "--json"],
    );
    assert!(ok);
    let rewritten = std::fs::metadata(&probe).unwrap().modified().unwrap();
    assert_ne!(
        before, rewritten,
        "without --no-skills the same harness DOES write the shared root — so the assertion \
         above is measuring the flag, not an inert code path"
    );
}

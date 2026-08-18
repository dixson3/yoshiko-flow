//! End-to-end aggregate-ruleset lifecycle through the real `yf` binary
//! (REQ-YF-FLOW-001/003/004). Drives `yf skills install|upgrade|remove --json`
//! against a temp `--target` and asserts the on-disk `YOSHIKO_FLOW.md`.
//!
//! The doctor/preflight verdict-parity halves of Issue 5.1's coverage (M3) live
//! as in-crate tests named with the same `flow_install_e2e` prefix
//! (`flow_install_e2e_doctor_verdict_parity` in `cmd/doctor.rs`,
//! `flow_install_e2e_preflight_verdict_parity` in `preflight.rs`) so the gate's
//! `cargo test flow_install_e2e` runs them too — they need the crate-internal
//! `check_rules`/`check_rule` entry points an integration test cannot reach.

use std::path::Path;
use std::process::Command;

use serde_json::Value;

const YF: &str = env!("CARGO_BIN_EXE_yf");

/// The rule-bearing skills (each ships a `protocols/*.md`) — this must be the
/// COMPLETE embedded set, not a subset.
///
/// plan-044 Issue 2.1: `yf-change-validation` was missing here. That was invisible
/// while these tests drove a `--target`ed `skills upgrade`, which wrote only the
/// sections it was told to. `yf harness tune` — now the aggregate's sole writer —
/// reconcile-prunes on the EMBEDDED set (REQ-YF-FLOW-002), so a missing entry means
/// "remove them all" no longer empties the file. The list is now complete.
const RULE_SKILLS: &[&str] = &[
    "yf-beads-init",
    "yf-beads-upstream",
    "yf-change-validation",
    "yf-drift-check",
    "yf-markdown-lint",
    "yf-optimal-instructions",
    "yf-plan",
    "yf-research",
];

const RULE_PROTOCOLS: &[&str] = &[
    "BEADS_INIT.md",
    "UPSTREAM_TRACKING.md",
    "CHANGE-VALIDATION-TRIGGER.md",
    "DRIFT-CHECK-TRIGGER.md",
    "MARKDOWN_LINT.md",
    "INSTRUCTIONS.md",
    "PLANS.md",
    "RESEARCH.md",
];

const BANNER: &str = "<!-- managed by yf — do not edit by hand, edit sections at your own risk -->";

/// Run `yf` with `HOME` pinned to `home` and `CI` cleared.
///
/// plan-044 Issue 2.1 (REQ-YF-FLOW-008): the aggregate's ONLY writer is now
/// `yf harness tune`, which resolves its rule target from `HOME` and takes no
/// `--target`. So the aggregation engine can no longer be driven through a
/// `--target`ed `skills upgrade` — these tests sandbox `HOME` instead. `HOME` is
/// always a tempdir here: a leak would write the developer's real `~/.claude`.
fn yf_json_in(home: &Path, args: &[&str]) -> Value {
    let out = Command::new(YF)
        .args(args)
        .env("HOME", home)
        .env_remove("CI")
        .output()
        .expect("spawn yf");
    assert!(
        out.status.success(),
        "yf {args:?} exited non-zero: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    serde_json::from_slice(&out.stdout).unwrap_or_else(|e| {
        panic!(
            "yf {args:?} did not emit JSON ({e}): {}",
            String::from_utf8_lossy(&out.stdout)
        )
    })
}

/// Deploy the aggregate the only way it can now be deployed: a rules-only tune.
fn tune_rules(home: &Path) -> Value {
    yf_json_in(
        home,
        &[
            "harness",
            "tune",
            "--harness",
            "claude-code",
            "--rules-only",
            "--json",
        ],
    )
}

fn yf_json(args: &[&str]) -> Value {
    let out = Command::new(YF).args(args).output().expect("spawn yf");
    assert!(
        out.status.success(),
        "yf {args:?} exited non-zero: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    serde_json::from_slice(&out.stdout).unwrap_or_else(|e| {
        panic!(
            "yf {args:?} did not emit JSON ({e}): {}",
            String::from_utf8_lossy(&out.stdout)
        )
    })
}

/// Protocol names (alphabetical, as they appear) parsed from a YOSHIKO_FLOW.md.
fn section_protocols(text: &str) -> Vec<String> {
    text.lines()
        .filter(|l| l.trim_start().starts_with("<!-- yf-flow:") && !l.contains(":end"))
        .filter_map(|l| {
            l.split_whitespace()
                .find_map(|t| t.strip_prefix("protocol=").map(str::to_string))
        })
        .collect()
}

#[test]
fn flow_install_e2e_lifecycle() {
    let tmp = tempfile::tempdir().unwrap();
    let target = tmp.path().join("skills");
    // With --target, the rules dir is the sibling <target>/../rules.
    let rules_dir = target.parent().unwrap().join("rules");

    // 1. install all rule-bearing skills — plan-033 install is SKILLS-ONLY
    //    (REQ-YF-INSTALL-008): it deploys skill bodies and writes NO rules.
    let mut args = vec!["skills", "install"];
    args.extend_from_slice(RULE_SKILLS);
    args.extend_from_slice(&["--target", target.to_str().unwrap(), "--json"]);
    let j = yf_json(&args);
    assert_eq!(
        j["rules_deployed"],
        Value::Bool(false),
        "install is skills-only"
    );
    assert!(
        !rules_dir.join("YOSHIKO_FLOW.md").exists(),
        "skills-only install writes no aggregate"
    );

    // 2. the aggregate ruleset is produced by `yf harness tune` — its SOLE writer
    //    (REQ-YF-FLOW-008). This step formerly drove `skills upgrade`, which was
    //    the second writer #156 removed; the aggregation engine under test is
    //    unchanged, only the verb that invokes it.
    let home = tmp.path().join("home");
    std::fs::create_dir_all(&home).unwrap();
    let mut inst_home = vec!["skills", "install"];
    inst_home.extend_from_slice(RULE_SKILLS);
    inst_home.push("--json");
    yf_json_in(&home, &inst_home);
    tune_rules(&home);

    let rules_dir = home.join(".claude").join("rules");
    let flow_file = rules_dir.join("YOSHIKO_FLOW.md");
    assert!(flow_file.is_file(), "YOSHIKO_FLOW.md written by tune");
    let flow_file = flow_file.to_str().unwrap().to_string();

    let text = std::fs::read_to_string(&flow_file).unwrap();
    assert!(text.starts_with(BANNER), "banner heads the file");
    assert!(
        text.contains("<!-- generated by yf v"),
        "version generated-on note"
    );

    let protos = section_protocols(&text);
    // Every rule-bearing protocol is present...
    for p in RULE_PROTOCOLS {
        assert!(
            protos.contains(&p.to_string()),
            "section for {p} present: {protos:?}"
        );
    }
    // ...alphabetically ordered...
    let mut sorted = protos.clone();
    sorted.sort();
    assert_eq!(protos, sorted, "sections are alpha-ordered by protocol");
    // ...and NO standalone rule files exist.
    for p in RULE_PROTOCOLS {
        assert!(
            !Path::new(&rules_dir).join(p).exists(),
            "no standalone {p} — only the aggregate"
        );
    }

    // 2. tune is idempotent (byte-stable aggregate).
    let before = std::fs::read(&flow_file).unwrap();
    tune_rules(&home);
    let after = std::fs::read(&flow_file).unwrap();
    assert_eq!(before, after, "tune is byte-stable / idempotent");

    // 2b. REQ-YF-FLOW-008: a subsequent `skills upgrade` leaves the aggregate
    //     BYTE-UNTOUCHED. This is the #156 regression guard at the e2e level —
    //     upgrade must no longer be a writer of this path at all.
    let mut up = vec!["skills", "upgrade"];
    up.extend_from_slice(RULE_SKILLS);
    up.push("--json");
    yf_json_in(&home, &up);
    assert_eq!(
        before,
        std::fs::read(&flow_file).unwrap(),
        "skills upgrade must not touch YOSHIKO_FLOW.md (tune is the sole writer)"
    );

    // 3. remove ONE skill drops only its section; the file survives.
    let rm = yf_json_in(&home, &["skills", "remove", "yf-plan", "--json"]);
    assert_eq!(rm["flow_deleted"], Value::Bool(false));
    let text = std::fs::read_to_string(&flow_file).unwrap();
    let protos = section_protocols(&text);
    assert!(
        !protos.contains(&"PLANS.md".to_string()),
        "PLANS.md section dropped"
    );
    assert!(
        protos.contains(&"RESEARCH.md".to_string()),
        "others retained"
    );

    // 4. remove ALL remaining rule-bearing skills deletes the file (S6).
    //    `remove` KEEPS its rules write by design (D-10) — it is the only thing
    //    that would ever drop a removed skill's section.
    let mut rmall = vec!["skills", "remove"];
    rmall.extend_from_slice(RULE_SKILLS);
    rmall.push("--json");
    let rm = yf_json_in(&home, &rmall);
    assert_eq!(
        rm["flow_deleted"],
        Value::Bool(true),
        "empty aggregate deleted"
    );
    assert!(!Path::new(&flow_file).exists(), "YOSHIKO_FLOW.md gone");
}

/// REQ-YF-FLOW-003 (M3): legacy → aggregate transition through the binary —
/// pre-seed standalone rule files (incl. for a skill not named this run), run an
/// upgrade, and assert every standalone is folded into the aggregate and deleted.
#[test]
fn flow_install_e2e_legacy_transition() {
    let tmp = tempfile::tempdir().unwrap();
    let home = tmp.path().join("home");
    // The aggregate's sole writer is `tune`, which resolves from HOME.
    let rules_dir = home.join(".claude").join("rules");
    std::fs::create_dir_all(&rules_dir).unwrap();

    // Pre-seed legacy standalones: PLANS.md (acted on) + RESEARCH.md (NOT acted
    // on) + a foreign BEADS.md that must survive.
    std::fs::write(rules_dir.join("PLANS.md"), b"legacy plans\n").unwrap();
    std::fs::write(rules_dir.join("RESEARCH.md"), b"legacy research\n").unwrap();
    std::fs::write(rules_dir.join("BEADS.md"), b"from bd init\n").unwrap();

    // Tune → migration folds ALL yf-owned standalones (REQ-YF-FLOW-003 keys on the
    // embedded set, never on a per-run selection).
    yf_json_in(&home, &["skills", "install", "yf-plan", "--json"]);
    tune_rules(&home);

    assert!(
        !rules_dir.join("PLANS.md").exists(),
        "PLANS.md folded + deleted"
    );
    assert!(
        !rules_dir.join("RESEARCH.md").exists(),
        "RESEARCH.md folded + deleted"
    );
    assert!(
        rules_dir.join("BEADS.md").exists(),
        "foreign BEADS.md untouched"
    );

    let text = std::fs::read_to_string(rules_dir.join("YOSHIKO_FLOW.md")).unwrap();
    let protos = section_protocols(&text);
    assert!(protos.contains(&"PLANS.md".to_string()));
    assert!(
        protos.contains(&"RESEARCH.md".to_string()),
        "non-selected standalone folded too"
    );
}

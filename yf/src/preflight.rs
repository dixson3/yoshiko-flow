//! `yf preflight <skill> [--json]` — the shared preflight KERNEL (bead 2.3,
//! REQ-YF-PRE-002/003/004/005).
//!
//! This is a Rust re-implementation of the legacy per-skill Python `check`
//! subcommand (`plan_manager.py` / `research_manager.py`: the
//! `_check_prerequisites`, `_check_rule`, and `_ensure_scaffold` functions). Its
//! JSON output conforms to `docs/yf/preflight-contract.md` and is byte-compatible
//! with the legacy `check` for the three Gate-G2 parity states (`ok`,
//! `system_deps_missing`, `rule_*`).
//!
//! ## What the kernel owns (GR-005)
//!
//! Only shared *mechanism*: tool/version detection (REQ-YF-PRE-002), rule
//! hash/semver vs the embedded `manifest.json` (REQ-YF-PRE-003), per-skill
//! config + runtime state (REQ-YF-PRE-004), and the idempotent gitignore scaffold
//! (REQ-YF-PRE-005). Skill *domain* logic (research provider `warnings`, init /
//! audit / pour) stays in each skill's Python.
//!
//! ## Boundary with bead 2.4 (beads-init verify)
//!
//! The richer `bd_not_initialized` classification (the `error`-key parse, the
//! `corrupted` vs `not_initialized` distinction) is bead 2.4's `yf-beads-init`
//! verify. This kernel leaves a clean hook — [`bd_init_status`] returns `None`
//! today (TODO REQ-YF-PRE-006); when 2.4 lands, it plugs the classifier in and
//! a failing verdict maps to the preflight `bd_not_initialized` status.

use std::path::{Path, PathBuf};
use std::process::Command;

use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::embed;
use crate::frontmatter::{self, Preflight};

/// Minimum bd version the legacy scripts enforce (`MIN_BD_VERSION = (1, 0, 5)`)
/// when a skill's descriptor carries no explicit `min-bd-version`.
const DEFAULT_MIN_BD_VERSION: (u32, u32, u32) = (1, 0, 5);

/// The manifest schema the code understands (`MANIFEST_SCHEMA = 1`).
const MANIFEST_SCHEMA: i64 = 1;

/// Scaffold version (legacy `SCAFFOLD_VERSION = 1`); the gitignore anchors are
/// (re-)ensured once per version, gated by runtime state.
const SCAFFOLD_VERSION: i64 = 1;

/// The single gitignore anchor under the new `.yf/` tree (REQ-YF-PRE-005). The
/// per-skill `config-basename` anchor is added alongside it (legacy parity).
const YF_ANCHOR: &str = "/.yf/";

// ---------------------------------------------------------------------------
// Output schema (docs/yf/preflight-contract.md §3)
// ---------------------------------------------------------------------------

/// The companion-rule verdict object (contract §3.1).
#[derive(Debug, Serialize, PartialEq, Eq)]
pub struct RuleVerdict {
    pub outcome: String,
    pub rule: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub schema_version: Option<serde_json::Value>,
}

/// The top-level preflight result (contract §3).
///
/// Fields are held in a fixed struct, but JSON serialization ([`Outcome::to_json`])
/// emits keys in the EXACT per-status order the legacy Python `check` used, so the
/// output is byte-compatible (serde_json's `preserve_order` feature keeps the
/// insertion order of the built `Map`):
///
/// - `ok`: `status, missing, rule, scaffold_added, instructions`
/// - `system_deps_missing` / `bd_not_initialized`: `status, missing, instructions, rule`
/// - `rule_*` / `manifest_*`: `status, missing, instructions, rule`
/// - `ignored`: `status, missing, instructions, rule`
#[derive(Debug)]
pub struct Outcome {
    pub status: String,
    pub missing: Vec<String>,
    pub rule: Option<RuleVerdict>,
    /// `Some` only when `status == "ok"` (contract §3) — the legacy `check`
    /// includes `scaffold_added` solely on the otherwise-ready path.
    pub scaffold_added: Option<Vec<String>>,
    pub instructions: Vec<String>,
}

impl Outcome {
    /// Whether this verdict is a "failing" status for exit-code purposes
    /// (contract §1): everything except `ok` and `ignored`.
    fn is_failure(&self) -> bool {
        !matches!(self.status.as_str(), "ok" | "ignored")
    }

    /// Build the contract JSON with legacy per-status key order.
    pub fn to_json(&self) -> serde_json::Value {
        let mut m = serde_json::Map::new();
        m.insert("status".into(), self.status.clone().into());
        m.insert("missing".into(), serde_json::to_value(&self.missing).unwrap());
        let rule_val = match &self.rule {
            Some(r) => serde_json::to_value(r).unwrap(),
            None => serde_json::Value::Null,
        };
        if self.status == "ok" {
            // ok: rule, then scaffold_added, then instructions.
            m.insert("rule".into(), rule_val);
            m.insert(
                "scaffold_added".into(),
                serde_json::to_value(self.scaffold_added.clone().unwrap_or_default()).unwrap(),
            );
            m.insert(
                "instructions".into(),
                serde_json::to_value(&self.instructions).unwrap(),
            );
        } else {
            // every other status: instructions, then rule (last).
            m.insert(
                "instructions".into(),
                serde_json::to_value(&self.instructions).unwrap(),
            );
            m.insert("rule".into(), rule_val);
        }
        serde_json::Value::Object(m)
    }
}

// ---------------------------------------------------------------------------
// Filesystem injection seam (keeps the engine unit-testable without $HOME / cwd)
// ---------------------------------------------------------------------------

/// All filesystem/env inputs the kernel needs, injected so tests can drive the
/// engine against temp dirs. Production wiring uses [`Env::live`].
pub struct Env {
    /// Project root (repo root) the config/state/gitignore live under.
    pub repo_root: PathBuf,
    /// Candidate directories searched (in precedence order) for the installed
    /// companion rule. Mirrors the legacy `_rule_candidates()`.
    pub rule_dirs: Vec<PathBuf>,
}

impl Env {
    /// Live environment: repo root via git (cwd fallback), rule-candidate dirs in
    /// the same precedence order as the legacy `_rule_candidates()` (global home
    /// copy before the project copy).
    pub fn live() -> Self {
        let repo_root = crate::dest::git_root_or_cwd();
        let home = std::env::var_os("HOME").map(PathBuf::from);
        let mut rule_dirs: Vec<PathBuf> = Vec::new();
        let push = |p: PathBuf, dirs: &mut Vec<PathBuf>| {
            if !dirs.contains(&p) {
                dirs.push(p);
            }
        };
        if let Some(h) = &home {
            push(h.join(".claude").join("rules"), &mut rule_dirs);
            push(h.join(".agents").join("rules"), &mut rule_dirs);
        }
        push(repo_root.join(".agents").join("rules"), &mut rule_dirs);
        push(repo_root.join(".claude").join("rules"), &mut rule_dirs);
        Env { repo_root, rule_dirs }
    }
}

// ---------------------------------------------------------------------------
// Skill resolution: the <skill> arg -> embedded dir + short name
// ---------------------------------------------------------------------------

/// Map the logical `<skill>` argument to (embedded-dir-name, short-name).
///
/// The embedded `skills/` dirs are still `bdplan` / `bdresearch` (the
/// REQ-YF-RENAME-001 rename is a later bead), while the contract's `<skill>`
/// argument and the new `.yf/<skill>/` paths use the short names `plan` /
/// `research`. We accept either form. `short` drives config/state paths; `dir`
/// selects the embedded SKILL.md + manifest.
fn resolve_skill(arg: &str) -> (String, String) {
    // Explicit aliases for the two renamed skills.
    let (dir, short) = match arg {
        "plan" | "yf-plan" | "bdplan" => ("bdplan", "plan"),
        "research" | "yf-research" | "bdresearch" => ("bdresearch", "research"),
        other => {
            // Generic: the dir is the arg as-is (or with a `yf-` prefix if that
            // resolves to an embedded skill); the short name strips a `yf-`.
            let short = other.strip_prefix("yf-").unwrap_or(other);
            return (other.to_string(), short.to_string());
        }
    };
    (dir.to_string(), short.to_string())
}

// ---------------------------------------------------------------------------
// The engine
// ---------------------------------------------------------------------------

/// Run the preflight for `skill_arg` against `env`, returning the verdict.
///
/// Evaluation order mirrors the legacy `_check_prerequisites` (short-circuits top
/// to bottom): ignore-skill → system deps (cached) → bd-init hook → rule hash →
/// scaffold.
pub fn run_with_env(skill_arg: &str, env: &Env) -> Outcome {
    let (skill_dir, short) = resolve_skill(skill_arg);

    // Descriptor (REQ-YF-PRE-004): read the skill's embedded `preflight:` block.
    let descriptor = read_descriptor(&skill_dir);
    let rule_name = descriptor
        .as_ref()
        .and_then(|d| d.companion_rule.clone());
    let config_basename = descriptor
        .as_ref()
        .and_then(|d| d.config_basename.clone());

    // 1. ignore-skill (REQ-YF-PRE-004).
    if read_config(env, &short, config_basename.as_deref())
        .get("ignore-skill")
        .and_then(serde_json::Value::as_bool)
        .unwrap_or(false)
    {
        return Outcome {
            status: "ignored".into(),
            missing: vec![],
            rule: None,
            scaffold_added: None,
            instructions: vec![],
        };
    }

    // 2. System deps (REQ-YF-PRE-002) — checked once, then cached in state.
    let needs_bd = descriptor.as_ref().is_some_and(|d| d.min_bd_version.is_some())
        || skill_tools(&skill_dir).iter().any(|t| t == "bd");
    let state = read_state(env, &short);
    if !state
        .get("prereqs-present")
        .and_then(serde_json::Value::as_bool)
        .unwrap_or(false)
    {
        let (missing, instructions) = check_system_deps(&skill_dir, descriptor.as_ref());
        if !missing.is_empty() {
            return Outcome {
                status: "system_deps_missing".into(),
                missing,
                rule: None,
                scaffold_added: None,
                instructions,
            };
        }

        // 3. beads-init hook (REQ-YF-PRE-006). Today the coarse legacy behavior is
        //    preserved via `bd status --json`; bead 2.4 will route through the
        //    richer verify classifier (see `bd_init_status`).
        if needs_bd {
            if let Some(status) = bd_not_initialized_status(env) {
                return status;
            }
        }
        write_state_key(env, &short, "prereqs-present", serde_json::Value::Bool(true));
    }

    // 4. Rule hash/semver (REQ-YF-PRE-003) — checked every run (cheap).
    let Some(rule_name) = rule_name else {
        // A skill with no companion rule in its descriptor: nothing to hash. Treat
        // as ok (deps already satisfied). Scaffold still runs.
        let scaffold_added = ensure_scaffold(env, &short, config_basename.as_deref());
        return Outcome {
            status: "ok".into(),
            missing: vec![],
            rule: None,
            scaffold_added: Some(scaffold_added),
            instructions: vec![],
        };
    };

    let rule = check_rule(&skill_dir, &rule_name, env);
    let outcome = rule.outcome.clone();
    match outcome.as_str() {
        "ok" | "update_available" => {
            let scaffold_added = ensure_scaffold(env, &short, config_basename.as_deref());
            let instructions = if outcome == "ok" {
                vec![]
            } else {
                vec![format!(
                    "A newer {rule_name} is available — re-run the repo installer \
                     (install.sh --force) to update"
                )]
            };
            Outcome {
                status: "ok".into(),
                missing: vec![],
                rule: Some(rule),
                scaffold_added: Some(scaffold_added),
                instructions,
            }
        }
        "missing" | "drift" | "deprecated" => Outcome {
            status: format!("rule_{outcome}"),
            missing: vec![],
            rule: Some(rule),
            scaffold_added: None,
            instructions: vec![rule_instruction(&outcome, &rule_name, &short)],
        },
        // manifest_* outcomes pass through unprefixed (contract §2).
        other => Outcome {
            status: other.to_string(),
            missing: vec![],
            rule: Some(rule),
            scaffold_added: None,
            instructions: vec![rule_instruction(other, &rule_name, &short)],
        },
    }
}

/// Read the embedded skill's `preflight:` descriptor.
fn read_descriptor(skill_dir: &str) -> Option<Preflight> {
    let bytes = embed::read_file(&format!("{skill_dir}/SKILL.md"))?;
    let text = String::from_utf8_lossy(&bytes);
    frontmatter::parse_frontmatter(&text).preflight
}

/// The skill's `depends-on-tool` list from embedded frontmatter.
fn skill_tools(skill_dir: &str) -> Vec<String> {
    embed::read_file(&format!("{skill_dir}/SKILL.md"))
        .map(|b| {
            let text = String::from_utf8_lossy(&b);
            frontmatter::parse_frontmatter(&text).tools
        })
        .unwrap_or_default()
}

// ---------------------------------------------------------------------------
// Config + state (REQ-YF-PRE-004)
// ---------------------------------------------------------------------------

/// Read per-skill operator config. Precedence: the new `.yf/<skill>.local.json`,
/// then the legacy `.<config-basename>` at repo root (contract §7).
fn read_config(
    env: &Env,
    short: &str,
    config_basename: Option<&str>,
) -> serde_json::Map<String, serde_json::Value> {
    let new_path = env.repo_root.join(".yf").join(format!("{short}.local.json"));
    if let Some(m) = read_json_obj(&new_path) {
        return m;
    }
    if let Some(base) = config_basename {
        if let Some(m) = read_json_obj(&env.repo_root.join(base)) {
            return m;
        }
    }
    serde_json::Map::new()
}

/// Per-skill runtime state file: `.yf/<skill>/preflight.json`.
fn state_path(env: &Env, short: &str) -> PathBuf {
    env.repo_root.join(".yf").join(short).join("preflight.json")
}

fn read_state(env: &Env, short: &str) -> serde_json::Map<String, serde_json::Value> {
    read_json_obj(&state_path(env, short)).unwrap_or_default()
}

/// Merge one key into runtime state (never clobber sibling keys), best-effort.
fn write_state_key(env: &Env, short: &str, key: &str, value: serde_json::Value) {
    let mut state = read_state(env, short);
    state.insert(key.to_string(), value);
    let path = state_path(env, short);
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    if let Ok(text) = serde_json::to_string_pretty(&serde_json::Value::Object(state)) {
        let _ = std::fs::write(&path, text + "\n");
    }
}

fn read_json_obj(path: &Path) -> Option<serde_json::Map<String, serde_json::Value>> {
    let text = std::fs::read_to_string(path).ok()?;
    match serde_json::from_str::<serde_json::Value>(&text) {
        Ok(serde_json::Value::Object(m)) => Some(m),
        _ => None,
    }
}

// ---------------------------------------------------------------------------
// System deps + bd version (REQ-YF-PRE-002)
// ---------------------------------------------------------------------------

/// Probe `git` / `uv` / `bd` per the legacy `_check_prerequisites`. Returns
/// `(missing, instructions)` byte-compatible with the legacy strings.
fn check_system_deps(skill_dir: &str, descriptor: Option<&Preflight>) -> (Vec<String>, Vec<String>) {
    let mut missing = vec![];
    let mut instructions = vec![];

    let tools = skill_tools(skill_dir);
    let needs = |t: &str| tools.iter().any(|x| x == t);

    // The legacy check always probes git + uv; the skill's tool list confirms it.
    if needs("git") && which("git").is_none() {
        missing.push("git".into());
        instructions.push("Install git via your system package manager".into());
    }
    if needs("uv") && which("uv").is_none() {
        missing.push("uv".into());
        instructions.push("Install uv: https://docs.astral.sh/uv/".into());
    }

    // bd version gate: only when the skill needs bd (min-bd-version present, or bd
    // in depends-on-tool).
    let needs_bd = descriptor.is_some_and(|d| d.min_bd_version.is_some()) || needs("bd");
    if needs_bd {
        let min = parse_min_bd(descriptor);
        match parse_bd_version() {
            None => {
                missing.push("bd".into());
                instructions
                    .push("Install beads: https://github.com/gastownhall/beads".into());
            }
            Some(v) if v < min => {
                let v_str = ver_str(v);
                let min_str = ver_str(min);
                missing.push(format!("bd>={min_str}"));
                instructions.push(format!(
                    "Upgrade beads: bd upgrade (current: {v_str}, required: >= {min_str})"
                ));
            }
            Some(_) => {}
        }
    }
    (missing, instructions)
}

/// The minimum bd version: the descriptor's `min-bd-version`, else the default.
fn parse_min_bd(descriptor: Option<&Preflight>) -> (u32, u32, u32) {
    descriptor
        .and_then(|d| d.min_bd_version.as_deref())
        .and_then(parse_semver)
        .unwrap_or(DEFAULT_MIN_BD_VERSION)
}

fn ver_str(v: (u32, u32, u32)) -> String {
    // Match the legacy ".".join of the parsed tuple. bd version strings are
    // major.minor.patch, so all three components are emitted.
    format!("{}.{}.{}", v.0, v.1, v.2)
}

/// Parse a `major.minor[.patch]` semver string into a 3-tuple (patch defaults 0).
fn parse_semver(s: &str) -> Option<(u32, u32, u32)> {
    let nums = extract_version_tuple(s)?;
    Some(nums)
}

/// Run `bd --version` and parse the first `\d+.\d+(.\d+)?` it finds (legacy
/// `_parse_bd_version`). `None` if bd is absent or prints no version.
fn parse_bd_version() -> Option<(u32, u32, u32)> {
    let out = Command::new("bd").arg("--version").output().ok()?;
    if !out.status.success() {
        return None;
    }
    let text = String::from_utf8_lossy(&out.stdout);
    extract_version_tuple(&text)
}

/// Find the first `\d+.\d+(.\d+)?` in `text` and return it as a 3-tuple.
fn extract_version_tuple(text: &str) -> Option<(u32, u32, u32)> {
    let bytes = text.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i].is_ascii_digit() {
            // Read up to three dot-separated number groups.
            let mut nums: Vec<u32> = Vec::new();
            let mut j = i;
            loop {
                let start = j;
                while j < bytes.len() && bytes[j].is_ascii_digit() {
                    j += 1;
                }
                if start == j {
                    break;
                }
                let n: u32 = text[start..j].parse().ok()?;
                nums.push(n);
                if nums.len() == 3 {
                    break;
                }
                // Continue only if a '.' immediately follows another digit group.
                if j < bytes.len() && bytes[j] == b'.' && j + 1 < bytes.len()
                    && bytes[j + 1].is_ascii_digit()
                {
                    j += 1;
                } else {
                    break;
                }
            }
            if nums.len() >= 2 {
                let major = nums[0];
                let minor = nums[1];
                let patch = nums.get(2).copied().unwrap_or(0);
                return Some((major, minor, patch));
            }
        }
        i += 1;
    }
    None
}

/// `which`-style PATH lookup using std only (GR-011: no extra dep).
fn which(bin: &str) -> Option<PathBuf> {
    let path = std::env::var_os("PATH")?;
    for dir in std::env::split_paths(&path) {
        let candidate = dir.join(bin);
        if is_executable(&candidate) {
            return Some(candidate);
        }
    }
    None
}

#[cfg(unix)]
fn is_executable(p: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(p)
        .map(|m| m.is_file() && (m.permissions().mode() & 0o111 != 0))
        .unwrap_or(false)
}

#[cfg(not(unix))]
fn is_executable(p: &Path) -> bool {
    p.is_file()
}

// ---------------------------------------------------------------------------
// beads-init hook (REQ-YF-PRE-006) — bead 2.4 plugs in here
// ---------------------------------------------------------------------------

/// Bead 2.4's `yf-beads-init` verify classifier, plugged in (REQ-YF-PRE-006). It
/// inspects the PARSED `bd status --json` for an `error` key (NOT the exit code)
/// and distinguishes `corrupted` (initialized-but-wedged) from `not_initialized`,
/// mapping the richer verdict back to the preflight enum (contract §5):
///
/// - verify `deps_missing`           → preflight `system_deps_missing`
/// - verify `not_initialized` / `corrupted` → preflight `bd_not_initialized`
///   (the preflight enum has no `corrupted` member; the richer verdict lives in
///   `yf-beads-init`'s own `verify --json`)
/// - verify `ok`                     → `None` (beads is healthy; pass)
///
/// The `corrupted` case's `instructions` surface the verify remediations (the
/// wedged-migration fix) instead of the coarse `bd init`.
fn bd_init_status(env: &Env) -> Option<Outcome> {
    let v = crate::beads_init::verify(&env.repo_root);
    match v.status {
        crate::beads_init::VerifyStatus::Ok => None,
        crate::beads_init::VerifyStatus::DepsMissing => Some(Outcome {
            status: "system_deps_missing".into(),
            missing: v.tools_missing,
            rule: None,
            scaffold_added: None,
            instructions: v.remediations,
        }),
        crate::beads_init::VerifyStatus::NotInitialized => Some(Outcome {
            status: "bd_not_initialized".into(),
            missing: vec![],
            rule: None,
            scaffold_added: None,
            instructions: vec!["Run: bd init".into()],
        }),
        crate::beads_init::VerifyStatus::Corrupted => Some(Outcome {
            status: "bd_not_initialized".into(),
            missing: vec![],
            rule: None,
            scaffold_added: None,
            instructions: if v.remediations.is_empty() {
                vec!["Run: yf doctor --repair".into()]
            } else {
                v.remediations
            },
        }),
    }
}

/// Coarse legacy beads check (REQ-YF-PRE-006 parity): `bd status --json`; if it
/// fails, return `bd_not_initialized`. Bead 2.4's [`bd_init_status`] supersedes
/// this when it returns `Some`.
fn bd_not_initialized_status(env: &Env) -> Option<Outcome> {
    if let Some(richer) = bd_init_status(env) {
        return Some(richer);
    }
    let ok = Command::new("bd")
        .args(["status", "--json"])
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false);
    if ok {
        None
    } else {
        Some(Outcome {
            status: "bd_not_initialized".into(),
            missing: vec![],
            rule: None,
            scaffold_added: None,
            instructions: vec!["Run: bd init".into()],
        })
    }
}

// ---------------------------------------------------------------------------
// Rule hash / semver (REQ-YF-PRE-003)
// ---------------------------------------------------------------------------

/// Compare the installed companion rule against the skill's EMBEDDED
/// `protocols/manifest.json`. Mirrors the legacy `_check_rule` exactly:
/// outcomes `ok | update_available | drift | deprecated | missing |
/// manifest_schema_unknown | manifest_missing`, best-outcome ranking over the
/// candidate dirs (global home before project copy).
fn check_rule(skill_dir: &str, rule_name: &str, env: &Env) -> RuleVerdict {
    let manifest = match embed::read_file(&format!("{skill_dir}/protocols/manifest.json"))
        .and_then(|b| serde_json::from_slice::<serde_json::Value>(&b).ok())
    {
        Some(m) => m,
        None => {
            return RuleVerdict {
                outcome: "manifest_missing".into(),
                rule: rule_name.into(),
                path: None,
                version: None,
                schema_version: None,
            }
        }
    };

    if manifest.get("schema_version").and_then(serde_json::Value::as_i64) != Some(MANIFEST_SCHEMA) {
        return RuleVerdict {
            outcome: "manifest_schema_unknown".into(),
            rule: rule_name.into(),
            path: None,
            version: None,
            schema_version: Some(
                manifest
                    .get("schema_version")
                    .cloned()
                    .unwrap_or(serde_json::Value::Null),
            ),
        };
    }

    let entry = manifest
        .get("files")
        .and_then(|f| f.get(rule_name))
        .cloned()
        .unwrap_or(serde_json::Value::Null);
    let deprecated = entry.get("deprecated").and_then(serde_json::Value::as_bool).unwrap_or(false);
    let cur_sha = entry.get("sha256").and_then(serde_json::Value::as_str);
    let version = entry.get("version").and_then(serde_json::Value::as_str).map(str::to_string);
    let prev_shas: Vec<&str> = entry
        .get("previous_versions")
        .and_then(serde_json::Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(|p| p.get("sha256").and_then(serde_json::Value::as_str))
                .collect()
        })
        .unwrap_or_default();

    let outcome_for = |path: &Path| -> &'static str {
        if deprecated {
            return "deprecated";
        }
        let installed = sha256_file(path);
        if installed.as_deref() == cur_sha {
            return "ok";
        }
        if let Some(h) = &installed {
            if prev_shas.iter().any(|p| p == h) {
                return "update_available";
            }
        }
        "drift"
    };

    let rank = |o: &str| match o {
        "ok" => 0,
        "update_available" => 1,
        "deprecated" => 2,
        _ => 3, // drift
    };

    let mut best: Option<&'static str> = None;
    let mut best_path: Option<PathBuf> = None;
    for dir in &env.rule_dirs {
        let path = dir.join(rule_name);
        if !path.exists() {
            continue;
        }
        let oc = outcome_for(&path);
        if best.is_none() || rank(oc) < rank(best.unwrap()) {
            best = Some(oc);
            best_path = Some(path);
            if oc == "ok" {
                break;
            }
        }
    }

    match best {
        None => RuleVerdict {
            outcome: "missing".into(),
            rule: rule_name.into(),
            path: None,
            version: None,
            schema_version: None,
        },
        Some(oc) => RuleVerdict {
            outcome: oc.into(),
            rule: rule_name.into(),
            path: best_path.map(|p| p.to_string_lossy().into_owned()),
            version: if oc == "ok" || oc == "update_available" { version } else { None },
            schema_version: None,
        },
    }
}

fn sha256_file(path: &Path) -> Option<String> {
    let bytes = std::fs::read(path).ok()?;
    let mut h = Sha256::new();
    h.update(&bytes);
    let digest = h.finalize();
    let mut s = String::with_capacity(64);
    for b in digest {
        s.push_str(&format!("{b:02x}"));
    }
    Some(s)
}

/// The legacy `_RULE_INSTRUCTIONS` remediation strings, parameterized by rule and
/// skill name. `skill_label` is the renamed skill name used in the manifest
/// error strings (legacy `SKILL_NAME`, e.g. `yf-plan`).
fn rule_instruction(outcome: &str, rule_name: &str, short: &str) -> String {
    let skill_label = format!("yf-{short}");
    match outcome {
        "missing" => format!(
            "{rule_name} is not installed — run the repo installer (install.sh) to install \
             it to the scope+surface rules dir (user-scope ~/.<surface>/rules, project-scope \
             <git-root>/.<surface>/rules); add --force to overwrite an existing copy"
        ),
        "drift" => format!(
            "Installed {rule_name} diverges from the manifest — re-run the repo installer \
             with --force (install.sh --force) to restore the shipped version, or resolve \
             manually"
        ),
        "deprecated" => format!(
            "{rule_name} is deprecated — remove it from the rules dir (the skill no longer \
             ships it)"
        ),
        "manifest_schema_unknown" => {
            format!("Upgrade {skill_label}: manifest schema_version not understood")
        }
        "manifest_missing" => {
            format!("{skill_label} packaging error: protocols/manifest.json is missing")
        }
        _ => String::new(),
    }
}

// ---------------------------------------------------------------------------
// Scaffold (REQ-YF-PRE-005)
// ---------------------------------------------------------------------------

/// Idempotent, additive gitignore scaffold (legacy `_ensure_scaffold`). Ensures
/// the `/.yf/` anchor (and the per-skill `config-basename` anchor) once per
/// `SCAFFOLD_VERSION`, gated by runtime state. Returns the human-readable list of
/// what was added (e.g. `"gitignore /.yf/"`), matching the legacy `scaffold_added`.
fn ensure_scaffold(env: &Env, short: &str, config_basename: Option<&str>) -> Vec<String> {
    let mut added = vec![];

    let already = read_state(env, short)
        .get("scaffold-ensured")
        .and_then(serde_json::Value::as_i64)
        == Some(SCAFFOLD_VERSION);
    if already {
        return added;
    }

    let mut anchors: Vec<String> = vec![];
    if let Some(base) = config_basename {
        anchors.push(format!("/{base}"));
    }
    anchors.push(YF_ANCHOR.to_string());

    let gitignore = env.repo_root.join(".gitignore");
    let mut lines: Vec<String> = std::fs::read_to_string(&gitignore)
        .map(|t| t.lines().map(str::to_string).collect())
        .unwrap_or_default();
    let present: std::collections::BTreeSet<String> =
        lines.iter().map(|l| l.trim().to_string()).collect();
    let missing: Vec<String> = anchors
        .iter()
        .filter(|a| !present.contains(*a))
        .cloned()
        .collect();
    if !missing.is_empty() {
        if lines.last().map(|l| !l.trim().is_empty()).unwrap_or(false) {
            lines.push(String::new());
        }
        lines.push(format!(
            "# Skill runtime state + local config (yf-{short}; Surface Convention §6)"
        ));
        lines.extend(missing.iter().cloned());
        let _ = std::fs::write(&gitignore, lines.join("\n") + "\n");
        for m in &missing {
            added.push(format!("gitignore {m}"));
        }
    }
    write_state_key(
        env,
        short,
        "scaffold-ensured",
        serde_json::Value::from(SCAFFOLD_VERSION),
    );
    added
}

// ---------------------------------------------------------------------------
// Command entry point
// ---------------------------------------------------------------------------

/// `yf preflight <skill> [--json]` command body. Prints the JSON (or a
/// human-readable summary) and returns the process exit verdict.
///
/// Exit semantics (REQ-YF-CLI-003 / contract §1): exit non-zero on a failing
/// status. The `status` field is authoritative in JSON mode regardless.
pub fn run(skill_arg: &str, json: bool) -> anyhow::Result<std::process::ExitCode> {
    let env = Env::live();
    let outcome = run_with_env(skill_arg, &env);

    if json {
        println!("{}", serde_json::to_string_pretty(&outcome.to_json())?);
    } else if outcome.status == "ok" {
        for entry in outcome.scaffold_added.iter().flatten() {
            eprintln!("NOTE: scaffold — {entry}");
        }
        for msg in &outcome.instructions {
            eprintln!("NOTE: {msg}");
        }
        println!("All prerequisites satisfied.");
    } else if outcome.status == "ignored" {
        println!("yf-{} is ignored in this project.", resolve_skill(skill_arg).1);
    } else {
        for msg in &outcome.instructions {
            eprintln!("ERROR: {msg}");
        }
    }

    Ok(if outcome.is_failure() {
        std::process::ExitCode::FAILURE
    } else {
        std::process::ExitCode::SUCCESS
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A test Env rooted at `repo`, with one rule-candidate dir `rules`.
    fn test_env(repo: &Path, rules: &Path) -> Env {
        Env {
            repo_root: repo.to_path_buf(),
            rule_dirs: vec![rules.to_path_buf()],
        }
    }

    fn unique_tmp(tag: &str) -> PathBuf {
        let base = std::env::temp_dir().join(format!(
            "yf-preflight-{}-{}-{}",
            tag,
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir_all(&base).unwrap();
        base
    }

    // REQ-YF-PRE-004: ignore-skill in config short-circuits to `ignored`.
    #[test]
    fn ignore_skill_short_circuits() {
        let tmp = unique_tmp("ignore");
        let repo = tmp.join("repo");
        std::fs::create_dir_all(repo.join(".yf")).unwrap();
        std::fs::write(
            repo.join(".yf").join("plan.local.json"),
            r#"{"ignore-skill": true}"#,
        )
        .unwrap();
        let env = test_env(&repo, &tmp.join("rules"));
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "ignored");
        assert!(out.rule.is_none());
        assert!(out.missing.is_empty());
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-004: legacy `.config-basename` config is honored as a fallback.
    #[test]
    fn ignore_skill_via_legacy_config_basename() {
        let tmp = unique_tmp("legacy-ignore");
        let repo = tmp.join("repo");
        std::fs::create_dir_all(&repo).unwrap();
        std::fs::write(repo.join(".yf-plan.local.json"), r#"{"ignore-skill": true}"#).unwrap();
        let env = test_env(&repo, &tmp.join("rules"));
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "ignored");
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-003: a tampered installed rule yields `rule_drift` with the
    // `rule` object populated (outcome/rule/path), the prereqs gate pre-satisfied
    // via cached state so we isolate the rule check.
    #[test]
    fn tampered_rule_yields_drift() {
        let tmp = unique_tmp("drift");
        let repo = tmp.join("repo");
        let rules = tmp.join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        // Pre-seed state so the system-deps/bd block is skipped.
        let state_dir = repo.join(".yf").join("plan");
        std::fs::create_dir_all(&state_dir).unwrap();
        std::fs::write(
            state_dir.join("preflight.json"),
            r#"{"prereqs-present": true, "scaffold-ensured": 1}"#,
        )
        .unwrap();
        // Install a PLANS.md whose bytes match neither current nor previous sha.
        std::fs::write(rules.join("PLANS.md"), "tampered content, diverges\n").unwrap();

        let env = test_env(&repo, &rules);
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "rule_drift");
        let rule = out.rule.expect("rule object expected");
        assert_eq!(rule.outcome, "drift");
        assert_eq!(rule.rule, "PLANS.md");
        assert!(rule.path.is_some(), "drift carries the winning path");
        assert!(rule.version.is_none(), "drift carries no version");
        assert_eq!(out.missing, Vec::<String>::new());
        assert_eq!(out.instructions.len(), 1);
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-003: an installed rule whose sha matches the embedded manifest's
    // current sha256 yields `ok` with a populated rule (version present) and
    // scaffold_added present.
    #[test]
    fn matching_rule_yields_ok() {
        let tmp = unique_tmp("ok");
        let repo = tmp.join("repo");
        let rules = tmp.join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        let state_dir = repo.join(".yf").join("plan");
        std::fs::create_dir_all(&state_dir).unwrap();
        std::fs::write(
            state_dir.join("preflight.json"),
            r#"{"prereqs-present": true}"#,
        )
        .unwrap();
        // Materialize the EMBEDDED PLANS.md so its sha256 matches the manifest.
        let embedded = embed::read_file("bdplan/protocols/PLANS.md").expect("embedded PLANS.md");
        std::fs::write(rules.join("PLANS.md"), embedded.as_ref()).unwrap();

        let env = test_env(&repo, &rules);
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "ok", "rule object: {:?}", out.rule);
        let rule = out.rule.expect("rule object expected");
        assert_eq!(rule.outcome, "ok");
        assert!(rule.version.is_some(), "ok carries the manifest version");
        assert!(out.scaffold_added.is_some(), "ok carries scaffold_added");
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-003: no installed rule in any candidate dir → `rule_missing`,
    // no path, no version.
    #[test]
    fn missing_rule_yields_rule_missing() {
        let tmp = unique_tmp("missing");
        let repo = tmp.join("repo");
        let rules = tmp.join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        let state_dir = repo.join(".yf").join("plan");
        std::fs::create_dir_all(&state_dir).unwrap();
        std::fs::write(state_dir.join("preflight.json"), r#"{"prereqs-present": true}"#).unwrap();

        let env = test_env(&repo, &rules);
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "rule_missing");
        let rule = out.rule.unwrap();
        assert_eq!(rule.outcome, "missing");
        assert!(rule.path.is_none());
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-005: the scaffold writes `/.yf/` (and the config-basename anchor)
    // to .gitignore on the `ok` path, reported in scaffold_added.
    #[test]
    fn scaffold_writes_yf_anchor() {
        let tmp = unique_tmp("scaffold");
        let repo = tmp.join("repo");
        let rules = tmp.join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        let state_dir = repo.join(".yf").join("plan");
        std::fs::create_dir_all(&state_dir).unwrap();
        std::fs::write(state_dir.join("preflight.json"), r#"{"prereqs-present": true}"#).unwrap();
        let embedded = embed::read_file("bdplan/protocols/PLANS.md").unwrap();
        std::fs::write(rules.join("PLANS.md"), embedded.as_ref()).unwrap();

        let env = test_env(&repo, &rules);
        let out = run_with_env("plan", &env);
        assert_eq!(out.status, "ok");
        let added = out.scaffold_added.unwrap();
        assert!(
            added.iter().any(|a| a == "gitignore /.yf/"),
            "scaffold_added must record /.yf/: {added:?}"
        );
        let gi = std::fs::read_to_string(repo.join(".gitignore")).unwrap();
        assert!(gi.contains("/.yf/"));
        assert!(gi.contains("/.yf-plan.local.json"));
        // Second run is idempotent: scaffold already ensured, nothing added.
        let out2 = run_with_env("plan", &env);
        assert_eq!(out2.scaffold_added.unwrap(), Vec::<String>::new());
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-003: version-tuple parsing matches the legacy regex behavior.
    #[test]
    fn version_tuple_parsing() {
        assert_eq!(extract_version_tuple("bd version 1.0.5"), Some((1, 0, 5)));
        assert_eq!(extract_version_tuple("v1.2"), Some((1, 2, 0)));
        assert_eq!(extract_version_tuple("1.0.5-rc1"), Some((1, 0, 5)));
        assert_eq!(extract_version_tuple("no version here"), None);
        assert!((1, 0, 4) < DEFAULT_MIN_BD_VERSION);
        assert!((1, 0, 5) >= DEFAULT_MIN_BD_VERSION);
    }

    // REQ-YF-PRE-006: the bd-init hook is plugged into the verify classifier
    // (bead 2.4). On a non-beads dir with deps present it returns a failing
    // `bd_not_initialized` verdict; with deps missing, `system_deps_missing`. It
    // is never `ok`-as-None here (no `.beads/`), so the hook is wired.
    #[test]
    fn bd_init_hook_plugged_in() {
        let tmp = unique_tmp("bd-init-hook");
        let env = test_env(&tmp, &tmp.join("rules"));
        let out = bd_init_status(&env).expect("non-beads dir must produce a failing verdict");
        assert!(
            matches!(out.status.as_str(), "bd_not_initialized" | "system_deps_missing"),
            "unexpected verify→preflight status: {}",
            out.status
        );
        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-PRE-001: JSON key ORDER is byte-compatible with the legacy `check`.
    // ok → status, missing, rule, scaffold_added, instructions.
    #[test]
    fn ok_json_key_order_matches_legacy() {
        let out = Outcome {
            status: "ok".into(),
            missing: vec![],
            rule: Some(RuleVerdict {
                outcome: "ok".into(),
                rule: "PLANS.md".into(),
                path: Some("/x/PLANS.md".into()),
                version: Some("1.0.1".into()),
                schema_version: None,
            }),
            scaffold_added: Some(vec![]),
            instructions: vec![],
        };
        let s = serde_json::to_string(&out.to_json()).unwrap();
        // Top-level keys in legacy order.
        let pos = |k: &str| s.find(k).unwrap();
        assert!(pos("\"status\"") < pos("\"missing\""));
        assert!(pos("\"missing\"") < pos("\"rule\""));
        assert!(pos("\"rule\"") < pos("\"scaffold_added\""));
        assert!(pos("\"scaffold_added\"") < pos("\"instructions\""));
        // RuleVerdict order: outcome, rule, path, version.
        assert!(s.find("\"outcome\"").unwrap() < s.find("\"path\"").unwrap());
        assert!(s.find("\"path\"").unwrap() < s.find("\"version\"").unwrap());
    }

    // REQ-YF-PRE-001: failing states put rule LAST (after instructions) and emit
    // `rule: null` — no `scaffold_added` key at all.
    #[test]
    fn failing_json_key_order_and_null_rule() {
        let out = Outcome {
            status: "system_deps_missing".into(),
            missing: vec!["uv".into()],
            rule: None,
            scaffold_added: None,
            instructions: vec!["Install uv: https://docs.astral.sh/uv/".into()],
        };
        let s = serde_json::to_string(&out.to_json()).unwrap();
        let pos = |k: &str| s.find(k).unwrap();
        assert!(pos("\"status\"") < pos("\"missing\""));
        assert!(pos("\"missing\"") < pos("\"instructions\""));
        assert!(pos("\"instructions\"") < pos("\"rule\""));
        assert!(s.contains("\"rule\":null"));
        assert!(!s.contains("scaffold_added"), "no scaffold_added on failure");
    }

    // Skill resolution: short, yf-prefixed, and legacy dir names all resolve.
    #[test]
    fn skill_alias_resolution() {
        assert_eq!(resolve_skill("plan"), ("bdplan".into(), "plan".into()));
        assert_eq!(resolve_skill("yf-plan"), ("bdplan".into(), "plan".into()));
        assert_eq!(resolve_skill("bdplan"), ("bdplan".into(), "plan".into()));
        assert_eq!(resolve_skill("research"), ("bdresearch".into(), "research".into()));
    }
}

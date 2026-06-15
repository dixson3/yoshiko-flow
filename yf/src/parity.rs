//! Frozen-golden parity test: yf's frontmatter group computation + transitive
//! `depends-on-skill` closure must match the retired `install.py`'s authoritative
//! output over the real `skills/` tree (REQ-YF-INSTALL-003 / REQ-YF-INSTALL-004).
//!
//! `install.py` is deleted by plan-010 bead 5.1, so its output is FROZEN into a
//! committed golden fixture (`testdata/install-parity.json`) and compared here.
//! The golden is NEVER produced at test time — it is regenerated only by a human
//! when the `skills/` tree legitimately changes group membership or
//! `depends-on-skill` edges:
//!
//! ```text
//! uv run yf/src/testdata/gen-install-parity.py > yf/src/testdata/install-parity.json
//! ```
//!
//! ## Keying
//!
//! Both sides key skills by their **directory name** under `skills/` (the 11
//! `yf-*` skills plus `bdplan`, `bdresearch`) — `depends-on-skill` references the
//! dir name in this repo's convention, matching [`crate::frontmatter::load_skills`].
//!
//! ## Documented divergence (excluded from the parity assertion)
//!
//! `install.py`'s CLI rejected an unknown *explicit* skill name up front (error +
//! non-zero exit), whereas yf's closure (bead 1.3) logs and skips an unknown name
//! to keep closure robust (`resolve_install_set`). That divergence is in the CLI
//! front-door error path, NOT in group membership or the closure of *valid*
//! inputs — the only thing this golden captures. Every golden input here is a
//! real group or a real in-repo skill, so the two implementations must agree
//! exactly on these, and they are the parts asserted. The unknown-name path is
//! covered separately by `frontmatter::tests::unknown_requested_skill_warns_not_panics`.

#![cfg(test)]

use std::collections::{BTreeMap, BTreeSet};

use serde_json::Value;

use crate::frontmatter::{
    computed_groups, load_skills, resolve_group, resolve_install_set, skills_in_group,
};

/// The frozen golden, captured from `install.py` over the live `skills/` tree.
const GOLDEN: &str = include_str!("testdata/install-parity.json");

fn golden() -> Value {
    serde_json::from_str(GOLDEN).expect("install-parity.json must be valid JSON")
}

/// Pull a JSON object of string→string into a `BTreeMap`.
fn obj_str_map(v: &Value, key: &str) -> BTreeMap<String, String> {
    v[key]
        .as_object()
        .unwrap_or_else(|| panic!("golden missing object `{key}`"))
        .iter()
        .map(|(k, val)| (k.clone(), val.as_str().expect("string value").to_string()))
        .collect()
}

/// Pull a JSON array of strings into a `Vec`.
fn arr_str(v: &Value) -> Vec<String> {
    v.as_array()
        .expect("expected JSON array")
        .iter()
        .map(|x| x.as_str().expect("string element").to_string())
        .collect()
}

// REQ-YF-INSTALL-003: per-skill `skill-group` membership matches install.py.
#[test]
fn skill_group_membership_matches_golden() {
    let g = golden();
    let want = obj_str_map(&g, "skill_group");

    let skills = load_skills();
    let got: BTreeMap<String, String> = skills
        .iter()
        .filter_map(|(name, fm)| fm.group.clone().map(|grp| (name.clone(), grp)))
        .collect();

    // Every skill install.py grouped must be grouped identically by yf, and yf
    // must not invent group membership install.py did not have.
    assert_eq!(got, want, "yf skill→group membership diverged from install.py");
}

// REQ-YF-INSTALL-003: the computed group set matches install.py.
#[test]
fn computed_groups_match_golden() {
    let g = golden();
    let want = arr_str(&g["groups"]);

    let skills = load_skills();
    let got = computed_groups(&skills);

    assert_eq!(got, want, "yf computed group set diverged from install.py");
}

// REQ-YF-INSTALL-003: per-group member lists match install.py.
#[test]
fn group_members_match_golden() {
    let g = golden();
    let members = g["group_members"]
        .as_object()
        .expect("golden missing `group_members`");

    let skills = load_skills();
    for (group, want_arr) in members {
        let want: Vec<String> = arr_str(want_arr);
        let got = skills_in_group(&skills, group);
        assert_eq!(
            got, want,
            "yf membership of group `{group}` diverged from install.py"
        );
    }
}

// REQ-YF-INSTALL-004: transitive `depends-on-skill` closures match install.py
// for every representative input (each group's closure + individual skills).
#[test]
fn closures_match_golden() {
    let g = golden();
    let closures = g["closures"]
        .as_object()
        .expect("golden missing `closures`");

    let skills = load_skills();

    for (input, want_arr) in closures {
        let want: BTreeSet<String> = arr_str(want_arr).into_iter().collect();

        // Keys are `group:<name>` (whole-group closure) or `skill:<name>`
        // (single-skill closure), matching the generator.
        let (got, _log) = if let Some(grp) = input.strip_prefix("group:") {
            resolve_group(&skills, grp)
        } else if let Some(skill) = input.strip_prefix("skill:") {
            let base: BTreeSet<String> = [skill.to_string()].into_iter().collect();
            resolve_install_set(&skills, &base)
        } else {
            panic!("unexpected closure key `{input}` (want group:/skill: prefix)");
        };

        assert_eq!(
            got, want,
            "yf transitive closure for `{input}` diverged from install.py"
        );
    }
}

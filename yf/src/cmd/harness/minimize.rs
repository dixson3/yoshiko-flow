//! Rule minimization: the curated irreducible-core selection + the bundle↔source
//! agreement guard (REQ-YF-TUNE-018).
//!
//! `yf harness tune` deploys a **minimized** "irreducible-core" rule bundle to a
//! non-Claude harness's always-loaded surface. The bundle is derived from the very
//! same skills' `protocols/*.md` sections that [`crate::flow`] aggregates into
//! `YOSHIKO_FLOW.md` — but keeps only the rules a skill `description` *cannot*
//! carry.
//!
//! ## This is a CURATED SELECTION, not an AI oracle
//!
//! The irreducible-vs-reducible call is the **manual curatorial judgment**
//! research-002 performed (`docs/research/002-harness-global-rule-minimization/
//! Summary.md`, the Q4 minimization verdict table). This module encodes that
//! verdict as a **data list** ([`CURATED_SELECTION`]) and guards it with an
//! **agreement assertion** ([`verify_agreement`]). Nothing here *decides*
//! irreducibility at runtime — it only *applies* a decision a human made and
//! *catches* two failure modes:
//!
//! 1. **content drift** — a selected (kept) rule's `protocols/*.md` source no
//!    longer matches what the deployed bundle carries; and
//! 2. **an unclassified new rule** — a new skill ships a `protocols/*.md` rule
//!    that is in neither the keep-list nor the drop-list, so no curator has ruled
//!    on it. The build/agreement path **fails loudly** rather than silently
//!    shipping (or silently dropping) it.
//!
//! ## The research-002 verdict (Summary.md Q4)
//!
//! **Irreducible — KEEP in the bundle** (a `description` cannot carry it):
//! - `PLANS.md` (yf-plan) — must override the compiled-in native plan mode.
//! - `RESEARCH.md` (yf-research) — must override the built-in deep-research harness.
//! - `BEADS_INIT.md` (yf-beads-init) — the two cross-cutting `bd`-usage mandates
//!   ("use `bd` for ALL task tracking" + non-interactive shell flags, which no
//!   single skill's description owns) **and** the deterministic must-fire
//!   invariants (the false-negative invariant, the silent-no-op invariants).
//! - `UPSTREAM_TRACKING.md` (yf-beads-upstream) — the close-time push trigger,
//!   which by design is "NOT carried in this description".
//!
//! **Reducible — DROP** (stays prose cross-harness; "0 sources attest" a
//! `paths`/hook analog outside Claude Code, so it is *not* placed in the minimized
//! bundle):
//! - `CHANGE-VALIDATION-TRIGGER.md` (yf-change-validation) — on-edit / pre-push.
//! - `DRIFT-CHECK-TRIGGER.md` (yf-drift-check) — on-edit.
//! - `MARKDOWN_LINT.md` (yf-markdown-lint) — on-edit (opt-in marker).
//! - `INSTRUCTIONS.md` (yf-optimal-instructions) — on-edit of an instruction file.
//!
//! ## Granularity
//!
//! The classification unit is the **protocol file** (one `protocols/*.md` = one
//! `YOSHIKO_FLOW.md` section = one curatorial verdict) — the same unit
//! research-002's verdict table rows use. `BEADS_INIT.md` is kept whole because it
//! carries only irreducible content (the bd mandates + the must-fire invariants);
//! the reducible on-edit rules live in *separate* protocol files, so a whole-file
//! keep/drop cleanly matches the verdict table without needing sub-section surgery.
//!
//! ## Seam for Issue 6.2
//!
//! [`irreducible_core_bundle`] returns the minimized bundle **text** (kept rule
//! bodies, provenance-tagged, deterministically ordered). Issue 6.2's managed-block
//! marker engine wraps *that* string in its `BEGIN`/`END` sentinels and places it
//! per harness. 6.1 owns the *content* + the *agreement guard*; 6.2 owns the
//! *placement*.

use anyhow::{bail, Result};

use crate::cmd::common;
use crate::flow::FlowSection;

/// Curatorial verdict for one `protocols/*.md` rule (research-002 Q4).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Verdict {
    /// **Irreducible** — a `description` cannot carry it; KEEP in the minimized
    /// bundle deployed to the always-loaded surface.
    Keep,
    /// **Reducible** — an on-edit engine trigger with no attested cross-harness
    /// `paths`/hook analog; it stays prose and is DROPPED from the bundle.
    Drop,
}

/// The curated selection, keyed by `protocols/*.md` filename.
///
/// This is research-002's **manual** verdict table (Summary.md Q4) transcribed as
/// data — **not** an autonomous irreducibility oracle. Every embedded protocol
/// rule must appear here (as [`Verdict::Keep`] or [`Verdict::Drop`]); a protocol
/// absent from this list is *unclassified* and makes the build / agreement guard
/// fail loudly (see [`build_bundle`] / [`verify_agreement`]). That is the
/// forward-looking property: a NEW skill's new `protocols/` rule cannot silently
/// enter (or silently bypass) the bundle — it forces a curatorial decision here.
pub const CURATED_SELECTION: &[(&str, Verdict)] = &[
    // --- Irreducible: KEEP (a description cannot carry these). ----------------
    ("PLANS.md", Verdict::Keep),             // override native plan mode
    ("RESEARCH.md", Verdict::Keep),          // override built-in deep-research
    ("BEADS_INIT.md", Verdict::Keep),        // bd mandates + must-fire invariants
    ("UPSTREAM_TRACKING.md", Verdict::Keep), // close-time push trigger
    // --- Reducible: DROP (on-edit engine rules; stay prose cross-harness). ----
    ("CHANGE-VALIDATION-TRIGGER.md", Verdict::Drop),
    ("DRIFT-CHECK-TRIGGER.md", Verdict::Drop),
    ("MARKDOWN_LINT.md", Verdict::Drop),
    ("INSTRUCTIONS.md", Verdict::Drop),
];

/// The curatorial verdict for a protocol filename, or `None` when the protocol is
/// **unclassified** (not in [`CURATED_SELECTION`]) — the signal that a new,
/// undecided `protocols/` rule has appeared.
pub fn classify(protocol: &str) -> Option<Verdict> {
    CURATED_SELECTION
        .iter()
        .find(|(p, _)| *p == protocol)
        .map(|(_, v)| *v)
}

/// The full `protocols/*.md` corpus, exactly as [`crate::flow`] /
/// [`common::install_rules_aggregate`] read it (every embedded skill's protocol
/// sections). This is the *source* side of the bundle↔source agreement — the same
/// sources `YOSHIKO_FLOW.md` aggregates from — so the minimized bundle and the
/// aggregate never drift from a different reading of the tree. Sorted by protocol
/// filename for deterministic output.
pub fn embedded_corpus() -> Vec<FlowSection> {
    let mut out = Vec::new();
    for skill in crate::embed::skill_names() {
        out.extend(common::embedded_rule_sections(&skill));
    }
    out.sort_by(|a, b| a.protocol.cmp(&b.protocol));
    out
}

/// Build the **minimized irreducible-core bundle text** from a protocol `corpus`.
///
/// Applies [`CURATED_SELECTION`]: emits the body of every [`Verdict::Keep`]
/// protocol verbatim (provenance-tagged, ordered by protocol filename) and omits
/// every [`Verdict::Drop`] one. **Fails loudly** if any corpus protocol is
/// unclassified — this is the forward-looking guard that forces a curatorial
/// decision when a new skill adds a `protocols/` rule.
///
/// The returned string is the bundle *content*; Issue 6.2 wraps it in managed
/// `BEGIN`/`END` markers for per-harness placement.
pub fn build_bundle(corpus: &[FlowSection]) -> Result<String> {
    let mut kept: Vec<&FlowSection> = Vec::new();
    for section in corpus {
        match classify(&section.protocol) {
            Some(Verdict::Keep) => kept.push(section),
            Some(Verdict::Drop) => {}
            None => bail!(
                "unclassified protocols/ rule '{}' (skill '{}'): it is in neither \
                 the keep-list nor the drop-list of minimize::CURATED_SELECTION. A \
                 new protocols/ rule needs an explicit research-002 verdict \
                 (Keep = irreducible, Drop = reducible on-edit) before it can be \
                 minimized.",
                section.protocol,
                section.skill
            ),
        }
    }
    kept.sort_by(|a, b| a.protocol.cmp(&b.protocol));

    let mut out = String::new();
    for section in kept {
        out.push_str(&format!(
            "<!-- yf-core: skill={} protocol={} sha256={} -->\n",
            section.skill, section.protocol, section.sha256
        ));
        out.push_str(&section.body);
        if !section.body.ends_with('\n') {
            out.push('\n');
        }
        out.push('\n');
    }
    Ok(out)
}

/// The minimized irreducible-core bundle over the **current embedded corpus** —
/// the seam Issue 6.2's managed-block engine consumes. Errors iff a protocol is
/// unclassified (see [`build_bundle`]).
///
/// This is the **runtime deploy path** entry point (`tune`'s rule sub-op calls it
/// before writing the managed block), so it runs [`verify_agreement`] over the
/// freshly built bundle and the same corpus **before returning** — the
/// bundle↔source agreement guard (REQ-YF-TUNE-018) is thus enforced at tune time,
/// not merely in tests. A drifted selected rule, a leaked reducible rule, or a new
/// unclassified `protocols/` rule fails the deploy loudly rather than shipping a
/// stale or unvetted block.
pub fn irreducible_core_bundle() -> Result<String> {
    let corpus = embedded_corpus();
    let bundle = build_bundle(&corpus)?;
    verify_agreement(&bundle, &corpus)?;
    Ok(bundle)
}

/// The **bundle↔source agreement assertion** (REQ-YF-TUNE-018).
///
/// Given a deployed `bundle` and the protocol `corpus` it should reflect, assert:
///
/// 1. **no unclassified rule** — every corpus protocol has a curatorial verdict;
///    a new, undecided `protocols/` rule fails loudly;
/// 2. **no content drift** — every [`Verdict::Keep`] protocol's source body is
///    present **verbatim** in the bundle (a drifted / stale selected rule fails);
/// 3. **no reducible leak** — no [`Verdict::Drop`] protocol's body appears in the
///    bundle (a reducible on-edit rule that must stay prose fails if it leaked in).
///
/// This is what catches the classifier going out of sync with its sources — either
/// because a selected rule's text changed, or because a new rule appeared that no
/// curator has ruled on.
pub fn verify_agreement(bundle: &str, corpus: &[FlowSection]) -> Result<()> {
    for section in corpus {
        match classify(&section.protocol) {
            None => bail!(
                "unclassified protocols/ rule '{}' (skill '{}') appeared with no \
                 curatorial verdict — classify it in minimize::CURATED_SELECTION \
                 (research-002 Q4) as Keep or Drop.",
                section.protocol,
                section.skill
            ),
            Some(Verdict::Keep) => {
                if !bundle.contains(section.body.as_str()) {
                    bail!(
                        "bundle↔source drift: irreducible rule '{}' (skill '{}') is \
                         not present verbatim in the deployed bundle — the source \
                         drifted from the deployed core, or the bundle is stale.",
                        section.protocol,
                        section.skill
                    );
                }
            }
            Some(Verdict::Drop) => {
                if bundle.contains(section.body.as_str()) {
                    bail!(
                        "reducible on-edit rule '{}' (skill '{}') leaked into the \
                         minimized bundle — it must stay prose cross-harness, not be \
                         deployed to the always-loaded surface.",
                        section.protocol,
                        section.skill
                    );
                }
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A synthetic `protocols/*.md` section (skill/protocol/body) for driving the
    /// classifier over a controlled corpus.
    fn section(skill: &str, protocol: &str, body: &str) -> FlowSection {
        FlowSection::new(skill, protocol, None, body)
    }

    // REQ-YF-TUNE-018: the agreement assertion PASSES for the current corpus. The
    // minimized bundle CONTAINS the irreducible rules (PLANS / RESEARCH override,
    // the bd mandates, UPSTREAM close-time) and does NOT contain the reducible
    // on-edit engine rules (which stay prose cross-harness).
    #[test]
    fn current_corpus_agrees_and_bundle_partitions_keep_from_drop() {
        let corpus = embedded_corpus();
        let bundle = build_bundle(&corpus).expect("current corpus must classify cleanly");

        // The agreement assertion holds for the real, shipped corpus.
        verify_agreement(&bundle, &corpus).expect("current corpus must agree");

        // Every curated protocol is actually present in the shipped corpus — a
        // stale curation entry (protocol removed/renamed) is caught here.
        for (protocol, _) in CURATED_SELECTION {
            assert!(
                corpus.iter().any(|s| s.protocol == *protocol),
                "curated protocol '{protocol}' is missing from the embedded corpus"
            );
        }

        // The four irreducible rules are present verbatim (KEEP).
        for keep in [
            "PLANS.md",
            "RESEARCH.md",
            "BEADS_INIT.md",
            "UPSTREAM_TRACKING.md",
        ] {
            let src = corpus.iter().find(|s| s.protocol == keep).unwrap();
            assert!(
                bundle.contains(src.body.as_str()),
                "irreducible rule {keep} must be IN the minimized bundle"
            );
        }

        // The four reducible on-edit engine rules are absent (DROP).
        for drop in [
            "CHANGE-VALIDATION-TRIGGER.md",
            "DRIFT-CHECK-TRIGGER.md",
            "MARKDOWN_LINT.md",
            "INSTRUCTIONS.md",
        ] {
            let src = corpus.iter().find(|s| s.protocol == drop).unwrap();
            assert!(
                !bundle.contains(src.body.as_str()),
                "reducible on-edit rule {drop} must NOT be in the minimized bundle"
            );
        }
    }

    // REQ-YF-TUNE-018: the assertion FAILS LOUDLY when a selected (KEEP) rule's
    // content drifts — a bundle built from the old source no longer matches a
    // corpus whose kept rule body has changed.
    #[test]
    fn content_drift_of_a_selected_rule_fails_loudly() {
        let corpus = embedded_corpus();
        let bundle = build_bundle(&corpus).unwrap();

        // Drift the source of a KEEP rule (PLANS.md) after the bundle was built.
        let mut drifted = corpus.clone();
        let plans = drifted
            .iter_mut()
            .find(|s| s.protocol == "PLANS.md")
            .unwrap();
        *plans = section(
            &plans.skill,
            "PLANS.md",
            "COMPLETELY DIFFERENT PLANS BODY\n",
        );

        let err = verify_agreement(&bundle, &drifted)
            .expect_err("a drifted selected rule must fail the agreement assertion");
        let msg = err.to_string();
        assert!(
            msg.contains("drift") && msg.contains("PLANS.md"),
            "the failure must name the drift and the drifted rule: {msg}"
        );
    }

    // REQ-YF-TUNE-018: a NEW, unclassified `protocols/` rule forces a classification
    // decision — both the bundle builder and the agreement assertion FAIL LOUDLY
    // (never silently ship or silently drop it).
    #[test]
    fn new_unclassified_rule_fails_loudly() {
        let mut corpus = embedded_corpus();
        corpus.push(section(
            "yf-brand-new",
            "BRAND_NEW_TRIGGER.md",
            "some new always-loaded rule with no curatorial verdict yet\n",
        ));

        // Build fails loudly.
        let build_err = build_bundle(&corpus)
            .expect_err("an unclassified new protocols/ rule must fail the build");
        assert!(
            build_err.to_string().contains("BRAND_NEW_TRIGGER.md")
                && build_err.to_string().contains("CURATED_SELECTION"),
            "build failure must name the unclassified rule and point at the table: {build_err}"
        );

        // The agreement assertion fails loudly too (independent of the builder).
        let good_bundle = irreducible_core_bundle().unwrap();
        let verify_err = verify_agreement(&good_bundle, &corpus)
            .expect_err("an unclassified new protocols/ rule must fail agreement");
        assert!(
            verify_err.to_string().contains("BRAND_NEW_TRIGGER.md"),
            "agreement failure must name the unclassified rule: {verify_err}"
        );
    }

    // REQ-YF-TUNE-018: the assertion FAILS LOUDLY if a reducible (DROP) rule's body
    // leaks into the bundle — it must stay prose cross-harness.
    #[test]
    fn reducible_rule_leak_fails_loudly() {
        let corpus = embedded_corpus();
        // Hand-craft a tampered bundle that appends a DROP rule's body verbatim.
        let drop_src = corpus
            .iter()
            .find(|s| s.protocol == "CHANGE-VALIDATION-TRIGGER.md")
            .unwrap();
        let tampered = format!("{}\n{}", build_bundle(&corpus).unwrap(), drop_src.body);

        let err = verify_agreement(&tampered, &corpus)
            .expect_err("a leaked reducible rule must fail the agreement assertion");
        assert!(
            err.to_string().contains("leaked")
                && err.to_string().contains("CHANGE-VALIDATION-TRIGGER.md"),
            "the failure must name the leaked reducible rule: {err}"
        );
    }

    // REQ-YF-TUNE-018: every embedded protocol is classified (no shipped rule is
    // silently unclassified) — the static coverage the forward-looking guard rests
    // on, checked directly against the live embedded tree.
    #[test]
    fn every_embedded_protocol_is_classified() {
        for section in embedded_corpus() {
            assert!(
                classify(&section.protocol).is_some(),
                "embedded protocol '{}' (skill '{}') is unclassified — add a \
                 research-002 verdict to minimize::CURATED_SELECTION",
                section.protocol,
                section.skill
            );
        }
    }
}

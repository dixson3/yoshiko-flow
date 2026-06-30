//! `yf self …` — the binary's own install/update lifecycle (plan-018 Epic 3).
//!
//! Distinct from `yf skills …` (which manages the embedded *skills/rules*): `yf
//! self` manages the **`yf` binary itself** — vendor self-update, dev from-build
//! install, and uninstall. Submodules:
//!
//! - [`receipt`] — install-receipt contract (3.1): cargo-dist's `yf-receipt.json`
//!   and yf's own `yf-from-build.json` marker.
//!
//! Later beads add `source` (3.3 install-source classification), `archive` (3.4a
//! pure-Rust extraction), and the command bodies (3.2/3.4/3.5/3.6/3.7).

pub mod receipt;

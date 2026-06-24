//! The `yf doctor` check abstraction (#32): a small `Check`-trait registry that
//! generalizes the previous hardcoded `Axis` list so a new prerequisite is a
//! one-line registry edit.
//!
//! Each check produces a [`CheckResult`]. A failing **required** check fails the
//! command (non-zero exit); a failing non-required check is a *warning* (e.g. a
//! Homebrew-shadowed `uv`) and never changes the exit code.

/// One check's verdict. Generalizes the old `Axis { name, ok, detail }` with two
/// new fields #32 needs: `required` (a failing optional check is a warning, not a
/// failure) and `remediation` (a one-line fix-it string surfaced to the operator).
#[derive(Debug, Clone)]
pub struct CheckResult {
    /// Axis name, e.g. `bd`, `uv`, `skills:yf-plan`.
    pub name: String,
    /// Whether the check passed.
    pub ok: bool,
    /// When `false`, a failed check is a non-fatal **warning** (does not fail
    /// the command). When `true`, a failed check fails `yf doctor`.
    pub required: bool,
    /// Human-readable status detail (e.g. resolved version + path).
    pub detail: String,
    /// One-line remediation, surfaced only when the check is not `ok`.
    pub remediation: Option<String>,
}

impl CheckResult {
    /// A passing required check with `detail` and no remediation.
    pub fn ok(name: impl Into<String>, detail: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            ok: true,
            required: true,
            detail: detail.into(),
            remediation: None,
        }
    }

    /// A failing required check with `detail` + a remediation hint.
    pub fn fail(
        name: impl Into<String>,
        detail: impl Into<String>,
        remediation: impl Into<String>,
    ) -> Self {
        Self {
            name: name.into(),
            ok: false,
            required: true,
            detail: detail.into(),
            remediation: Some(remediation.into()),
        }
    }

    /// A non-fatal warning verdict (`required: false`). `ok` reflects whether the
    /// warning condition is absent; a `false` here never fails the command.
    pub fn warn(
        name: impl Into<String>,
        ok: bool,
        detail: impl Into<String>,
        remediation: Option<String>,
    ) -> Self {
        Self {
            name: name.into(),
            ok,
            required: false,
            detail: detail.into(),
            remediation,
        }
    }

    /// Whether this result fails the command: a non-`ok` **required** check.
    /// A non-`ok` non-required check is a warning and does not count.
    pub fn is_failure(&self) -> bool {
        self.required && !self.ok
    }
}

/// A single `yf doctor` check. Implementors live in [`super::checks`].
pub trait Check {
    /// Run the check and return its verdict.
    fn run(&self) -> CheckResult;
}

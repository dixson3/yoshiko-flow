# Finding: Homebrew publish + receipt emission intact after retarget (Issue 1.3)

**Date:** 2026-06-30
**Tool:** `dist` 0.32.0 — `dist build --artifacts=global` (generated `yf-installer.sh`, `yf.rb`)
**Verifies:** the 1.2 retarget (`install-path=~/.local/bin`, `unix-archive=.tar.gz`) did not break
the Homebrew secondary path or the cargo-dist install receipt. Feeds 3.1 (receipt contract).

## Homebrew secondary — INTACT

- `.github/workflows/release.yml` still defines the `publish-homebrew-formula` job, pushing to
  `repository: "dixson3/homebrew-tap"` with `token: ${{ secrets.HOMEBREW_TAP_TOKEN }}`.
- `dist build --artifacts=global` still emits `yf.rb` (the formula) alongside `yf-installer.sh`.
- No runtime `depends_on` block (the intentional omission is preserved).

## Install receipt — INTACT, emitted at `~/.config/yf/yf-receipt.json`

`yf-installer.sh` writes the receipt only when `INSTALL_UPDATER=1` (cargo-dist's default; line 59),
to `RECEIPT_HOME/$APP_NAME-receipt.json` where:

```sh
RECEIPT_HOME="${XDG_CONFIG_HOME:-$INFERRED_HOME/.config}/yf"   # → ~/.config/yf
```

So the receipt lands at **`~/.config/yf/yf-receipt.json`** (honoring `XDG_CONFIG_HOME`) — exactly
where decision 3 wants config. Retargeting `install-path` did NOT set `INSTALL_UPDATER=0`; the
receipt is still emitted.

### Actual receipt schema (authoritative for 3.1)

```json
{
  "binaries": ["yf"],
  "binary_aliases": {},
  "cdylibs": [],
  "cstaticlibs": [],
  "install_layout": "unspecified",
  "install_prefix": "<AXO_INSTALL_PREFIX, resolved at install time → canonicalized ~/.local/bin>",
  "modify_path": true,
  "provider": { "source": "cargo-dist", "version": "0.32.0" },
  "source": { "app_name": "yf", "name": "yoshiko-flow", "owner": "dixson3", "release_type": "github" },
  "version": "0.3.2"
}
```

**3.1/3.3 consequences:**
- `source` is a **repo-descriptor object** (`app_name`/`name`/`owner`/`release_type`), NOT an
  install-source classifier. Confirms the pass-1 correction — derive "vendor" from the
  canonicalized **`install_prefix`**, never from `source`.
- `install_layout` is `"unspecified"` (flat layout) — the binary sits directly at
  `install_prefix` (`~/.local/bin`). No hierarchical prefix.
- The schema carries `binary_aliases`/`cdylibs`/`cstaticlibs` in addition to the fields the plan
  listed; 3.1's reader should tolerate extra keys and key only on `install_prefix` + `version`.

## No duelling updater

`_updater_name=""` on **every** arch branch (aarch64/x86_64 × darwin/linux) in `yf-installer.sh`,
and the receipt/updater install is guarded by `[ -n "$_updater_name" ] && [ "$INSTALL_UPDATER" = "1" ]`.
No `yf-update` companion binary is published → no cargo-dist updater to collide with the
hand-rolled `yf self update`.

## Windows installer deferred

`dist build --artifacts=global` produced only `yf-installer.sh` + `yf.rb` — **no `.ps1`**
(Windows not in `targets`). PowerShell installer correctly deferred to the follow-on.

## release.yml drift

`dist generate` after the 1.2 edit left `.github/workflows/release.yml` **byte-identical** to the
committed copy (`git diff` empty) — the retarget changed only release-time installer/asset behavior,
not the committed CI workflow.

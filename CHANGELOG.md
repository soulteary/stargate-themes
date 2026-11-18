# Changelog

## [1.0.0] - 2026-11-18

### Added

- Deep Space 1.0.0, a native authentication theme for Stargate v1.8.0 or later,
  using theme contract 1 and UI contract 1.
- A validated YAML manifest, local background image and Apache-2.0 license.
  Stargate supplies authentication templates, scripts and layout styles.
- Reproducible ZIP packaging and a package index with SHA-256 and runtime digest.
- Browser checks for login, account, TOTP enrollment, verification, revocation
  and step-up pages on desktop and mobile.

### Installation

Verify the archive SHA-256 against `index.json`, then extract the archive and
set `THEME_DIR` to its directory. The runtime user must be able to read the
files. Mount the directory read-only, use the same package on every replica,
and restart Stargate after changes. Stargate does not read ZIP files directly.

Unset `THEME_DIR` to return to the normal interface and existing override rules.
Set `THEME_SAFE_MODE=true` to skip all native and legacy UI overrides. Neither
operation changes stored sessions or Redis records.

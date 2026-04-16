# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-16

### Added
- Idempotent installer/update flow via `install.sh` and `scripts/install_or_update.py`
- Automatic directory creation for `~/.codex`, `~/.codex/agents`, and `$HOME/.agents/skills/karpathy-subagent-mode`
- Safe file backups when an existing target file is actually changed
- Managed install/update support for:
  - `~/.codex/config.toml`
  - `~/.codex/AGENTS.md`
  - `~/.codex/agents/reviewer.toml`
  - `~/.codex/agents/debugger.toml`
  - `$HOME/.agents/skills/karpathy-subagent-mode/SKILL.md`

### Changed
- `README.md` now documents install and upgrade through the installer instead of only manual copy steps
- `README_INSTALL.md` now focuses on normal install, upgrade, dry-run, and manual fallback
- `global_AGENTS_append.md` is now installer-managed through a dedicated block instead of blind repeated append

## [1.0.0] - 2026-04-15

### Added
- Initial public bundle with:
  - `config_append.toml`
  - `reviewer.toml`
  - `debugger.toml`
  - `global_AGENTS_append.md`
  - `skill/karpathy-subagent-mode/SKILL.md`
  - basic installation README

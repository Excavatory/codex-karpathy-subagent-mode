# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-04-16

### Added
- Fixture-based behavior self-test via `self-test.sh` and `scripts/self_test.py`
- `fixtures/python_divide_bug/` with a small known bug and standard-library `unittest` coverage
- Validation of real `spawn_agent` events for `reviewer` and `debugger`
- Validation of required final response sections:
  - `Changes made`
  - `Checks run`
  - `Reviewer findings fixed`
  - `Debugger findings fixed`
  - `Remaining risks`
  - `Unverified assumptions`

### Changed
- `README.md` now documents behavior verification, not only installation
- `README_INSTALL.md` now includes the post-install self-test flow
- `.gitignore` now ignores self-test artifact directories
- fixture copies now ignore `__pycache__` and `*.pyc`
- `scripts/self_test.py` now classifies reviewer/debugger workflow from real `spawn_agent` prompts instead of brittle literal name matching
- `scripts/self_test.py` now accepts normal Markdown heading styles when checking final required sections
- `scripts/self_test.py` now pins the full fixture filesystem mutation surface to `calc.py` via before/after snapshots
- `scripts/self_test.py` now preserves failure artifacts on command timeout
- `scripts/self_test.py` now avoids misleading `.selftest-last-success` output on failed `--keep-temp` runs
- `scripts/self_test.py` now runs Codex against a disposable fixture copy with a no-sandbox execution mode so the fix can actually be applied and re-verified end to end
- self-test docs now state clearly that the run is a trusted-machine diagnostic using the caller's Codex home by default
- `scripts/self_test.py` now ignores fenced code blocks when checking final required sections

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

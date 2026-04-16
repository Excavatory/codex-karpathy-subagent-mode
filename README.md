# Program Like Karpathy in Codex

Karpathy-inspired adaptive instructions for Codex with mandatory `reviewer` and `debugger` subagent workflow.

This repository packages a practical Codex setup for people who want:

- `gpt-5.4` as the main model
- `gpt-5.4` for `/review`
- named custom agents:
  - `reviewer`
  - `debugger`
- a global workflow that forces debugger-first handling for bugs and mandatory review/debug passes before finishing non-trivial work
- an extra Karpathy-style skill layer that pushes minimal, surgical, goal-driven engineering

This is not an official OpenAI package. It is a community setup for Codex.

## What Is Included

- `install.sh`
  - one-command installer/update entrypoint
- `scripts/install_or_update.py`
  - idempotent install/upgrade script with dry-run support
- `config_append.toml`
  - config snippet for `gpt-5.4`, `/review`, and `[agents]`
- `reviewer.toml`
  - named review agent for correctness, regressions, security, contract drift, race risks, and tests
- `debugger.toml`
  - named debugging agent for reproduction, root-cause isolation, behavior validation, and verified/unverified reporting
- `global_AGENTS_append.md`
  - append-only bridge for `~/.codex/AGENTS.md`
- `skill/karpathy-subagent-mode/SKILL.md`
  - Karpathy-style discipline layer for Codex
- `README_INSTALL.md`
  - install and upgrade instructions
- `CHANGELOG.md`
  - release notes for tags and upgrades

## Why This Setup

The goal is simple:

- think before coding
- keep diffs small
- debug from evidence, not guesswork
- never finalize important work without review and validation

In practice, this means:

1. On bugs, regressions, flaky tests, failing CI, or unclear runtime behavior, use `debugger` first.
2. Make the smallest defensible change.
3. Run the smallest relevant checks.
4. Before finalizing any non-trivial task, run `reviewer` and `debugger`.
5. Fix confirmed findings.
6. Re-run checks and repeat the passes if behavior changed again.

## Install

Full steps are in [README_INSTALL.md](README_INSTALL.md).

Normal install:

```bash
./install.sh
```

Upgrade an existing setup:

```bash
./install.sh
```

Dry run against your real home directory:

```bash
./install.sh --dry-run
```

Test against a temporary fake home:

```bash
TMP_HOME="$(mktemp -d)"
./install.sh --home "$TMP_HOME"
```

## Recommended Result

After installation, Codex should:

- use `gpt-5.4` as the main model
- use `gpt-5.4` for `/review`
- use `debugger` first for bug-like tasks
- require `reviewer` and `debugger` before finishing non-trivial engineering work
- activate `karpathy-subagent-mode` for non-trivial code tasks

## Validation Prompt

```bash
codex -a never exec --color never "Summarize the current instructions. Confirm whether the skill karpathy-subagent-mode is available, confirm whether the custom agents reviewer and debugger are available, and explain when each should be used."
```

## Releases

This repository uses simple semantic tags and a human-readable changelog:

- `v1.0.0`
  - initial public bundle
- `v1.1.0`
  - proper installer/update flow, changelog, and upgrade-safe behavior

See [CHANGELOG.md](CHANGELOG.md) for details.

## License

[MIT](LICENSE)

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
  - quick install instructions

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

Quick version:

1. Copy `reviewer.toml` and `debugger.toml` into `~/.codex/agents/`
2. Merge `config_append.toml` into `~/.codex/config.toml`
3. Append `global_AGENTS_append.md` to `~/.codex/AGENTS.md`
4. Copy `skill/karpathy-subagent-mode/SKILL.md` into `$HOME/.agents/skills/karpathy-subagent-mode/SKILL.md`
5. Restart Codex

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

## License

[MIT](LICENSE)

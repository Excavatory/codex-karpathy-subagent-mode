# Program Like Karpathy in Codex

Karpathy-inspired adaptive instructions for Codex with mandatory `reviewer` and `debugger` subagent workflow.

Адаптивные инструкции для Codex в стиле Karpathy с обязательным workflow через сабагентов `reviewer` и `debugger`.

This repository packages a practical Codex setup for people who want:

- `gpt-5.4` as the main model
- `gpt-5.4` for `/review`
- named custom agents:
  - `reviewer`
  - `debugger`
- a global workflow that forces debugger-first handling for bugs and mandatory review/debug passes before finishing non-trivial work
- an extra Karpathy-style skill layer that pushes minimal, surgical, goal-driven engineering

This is not an official OpenAI package. It is a community setup for Codex.

Это не официальный пакет OpenAI. Это community-настройка для Codex.

## What Is Included

- `install.sh`
  - one-command installer/update entrypoint
- `scripts/install_or_update.py`
  - idempotent install/upgrade script with dry-run support
- `self-test.sh`
  - one-command behavior self-test entrypoint
- `scripts/self_test.py`
  - fixture-based self-test that checks real subagent triggering and final response structure
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
- `fixtures/python_divide_bug/`
  - tiny known-bug repo used to verify trigger behavior on a real fix task
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

## Behavior Self-Test

This repository now includes a real behavior self-test, not just visibility checks.

Run it after installation:

```bash
./self-test.sh
```

What it verifies on a real fixture repo:

- the baseline fixture actually fails before Codex runs
- Codex emits debugger-style and reviewer-style `spawn_agent` workflow events
- the final answer contains these required sections:
  - `Changes made`
  - `Checks run`
  - `Reviewer findings fixed`
  - `Debugger findings fixed`
  - `Remaining risks`
  - `Unverified assumptions`
- the fixture passes after the Codex run
- the working-tree mutation surface stays pinned to `calc.py`, so the run cannot pass by rewriting the test or dropping in helper files

How it runs:

- the script copies the fixture into a disposable temporary git repo
- Codex is pointed at that disposable repo, not your active project checkout
- the self-test uses an unsandboxed Codex run on purpose so the fixture can actually be fixed and re-validated end to end on current Codex builds
- by default it still uses your current `HOME`, because the point is to validate your live Codex installation and installed agents/skills
- treat it as a trusted-machine diagnostic, not a sandbox boundary

Useful options:

```bash
./self-test.sh --timeout-seconds 300
./self-test.sh --keep-temp
./self-test.sh --home /path/to/home
```

With `--keep-temp`, artifacts are copied to `.selftest-last-success/` or `.selftest-last-failure/` in the repository root.

## Releases

This repository uses simple semantic tags and a human-readable changelog:

- `v1.0.0`
  - initial public bundle
- `v1.1.0`
  - proper installer/update flow, changelog, and upgrade-safe behavior
- `v1.2.0`
  - fixture-based behavior self-test for real reviewer/debugger workflow validation
- `v1.2.1`
  - self-test artifact-recovery hardening and better unexpected-error diagnostics

See [CHANGELOG.md](CHANGELOG.md) for details.

## License

[MIT](LICENSE)

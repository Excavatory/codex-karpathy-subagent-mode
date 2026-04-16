# Install or Upgrade the Karpathy + GPT-5.4 subagent bundle for Codex

## Preferred path

```bash
./install.sh
```

The installer is idempotent and can be used for both first install and upgrade.

What it does:

- creates missing target directories
- updates `~/.codex/config.toml` without wiping unrelated settings
- installs or refreshes `reviewer.toml` and `debugger.toml`
- installs or refreshes the Karpathy skill
- manages the Codex bridge block in `~/.codex/AGENTS.md` without duplicating it
- creates backup files when an existing target file is changed

## Dry run

```bash
./install.sh --dry-run
```

## Test against a temporary HOME

```bash
TMP_HOME="$(mktemp -d)"
./install.sh --home "$TMP_HOME"
```

## Manual fallback

Only use this if you explicitly do not want the installer.

### 1) Put the skill in your personal skills folder

```bash
mkdir -p ~/.agents/skills/karpathy-subagent-mode
cp ./skill/karpathy-subagent-mode/SKILL.md ~/.agents/skills/karpathy-subagent-mode/SKILL.md
```

### 2) Install the custom agents

```bash
mkdir -p ~/.codex/agents
cp ./reviewer.toml ~/.codex/agents/reviewer.toml
cp ./debugger.toml ~/.codex/agents/debugger.toml
```

### 3) Merge the config snippet into `~/.codex/config.toml`

Merge the keys from `config_append.toml` into `~/.codex/config.toml` without deleting unrelated settings.

### 4) Append the AGENTS bridge into `~/.codex/AGENTS.md`

Append the contents of `global_AGENTS_append.md` to your global `~/.codex/AGENTS.md`, but do not duplicate the block if it is already present.

## Restart Codex

Restart the Codex CLI, desktop app, or IDE session so it picks up the new files.

## Validation prompt

```bash
codex -a never exec --color never "Summarize the current instructions. Confirm whether the skill karpathy-subagent-mode is available, confirm whether the custom agents reviewer and debugger are available, and explain when each should be used."
```

## Behavior self-test

After installation, run:

```bash
./self-test.sh
```

This verifies real trigger behavior on a tiny known-bug fixture, not just whether files are present.

The script runs Codex against a disposable copy of that fixture, not your active project checkout. It intentionally uses an unsandboxed Codex run for that disposable repo so the test can verify a real edit, a real local re-check, reviewer/debugger-style workflow events, and the required final response sections end to end.

Important safety note:

- by default the self-test still uses your current `HOME`, because it is validating your live Codex installation, config, and installed agents/skills
- that means the self-test is a trusted-machine diagnostic, not a sandbox boundary
- if you want to exercise a different Codex home, pass `--home /path/to/home`

The self-test checks:

- the fixture starts in a failing state
- Codex emits debugger-style and reviewer-style `spawn_agent` events
- the final message contains the expected workflow sections
- the fixture ends in a passing state
- the only allowed working-tree change is `calc.py`

## Smoke-test prompt

```bash
codex -m gpt-5.4 "Review the current repo setup. If there is any non-trivial code issue, use karpathy-subagent-mode and explicitly spawn reviewer and debugger before you finalize anything."
```

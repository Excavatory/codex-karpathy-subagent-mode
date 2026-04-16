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

## Smoke-test prompt

```bash
codex -m gpt-5.4 "Review the current repo setup. If there is any non-trivial code issue, use karpathy-subagent-mode and explicitly spawn reviewer and debugger before you finalize anything."
```

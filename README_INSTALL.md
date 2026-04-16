# Install the Karpathy + GPT-5.4 subagent bundle for Codex

## 1) Put the skill in your personal skills folder

```bash
mkdir -p ~/.agents/skills/karpathy-subagent-mode
cp ./skill/karpathy-subagent-mode/SKILL.md ~/.agents/skills/karpathy-subagent-mode/SKILL.md
```

## 2) Install the custom agents

```bash
mkdir -p ~/.codex/agents
cp ./reviewer.toml ~/.codex/agents/reviewer.toml
cp ./debugger.toml ~/.codex/agents/debugger.toml
```

## 3) Merge the config snippet into `~/.codex/config.toml`

Append the contents of `config_append.toml`, or merge the keys manually if you already have a config.

## 4) Append the AGENTS bridge into `~/.codex/AGENTS.md`

Append the contents of `global_AGENTS_append.md` to your global `~/.codex/AGENTS.md`.

## 5) Restart Codex

Restart the Codex CLI, desktop app, or IDE session so it picks up the new files.

## 6) Quick validation prompt

```bash
codex -a never exec --color never "Summarize the current instructions. Confirm whether the skill karpathy-subagent-mode is available, confirm whether the custom agents reviewer and debugger are available, and explain when each should be used."
```

## 7) Smoke-test prompt

```bash
codex -m gpt-5.4 "Review the current repo setup. If there is any non-trivial code issue, use karpathy-subagent-mode and explicitly spawn reviewer and debugger before you finalize anything."
```

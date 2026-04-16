#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

START_MARKER = "<!-- codex-karpathy-subagent-mode:start -->"
END_MARKER = "<!-- codex-karpathy-subagent-mode:end -->"
AGENTS_HEADING = "## Mandatory coding workflow"
AGENTS_ANCHORS = (
    "activate `$karpathy-subagent-mode`",
    "Use the named custom agents `reviewer` and `debugger`",
    "Do not declare the task complete until the skill workflow has finished.",
)


@dataclass
class Action:
    kind: str
    path: Path
    detail: str = ""


class Installer:
    def __init__(self, repo_root: Path, home: Path, dry_run: bool) -> None:
        self.repo_root = repo_root
        self.home = home
        self.dry_run = dry_run
        self.actions: list[Action] = []
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        self.codex_dir = self.home / ".codex"
        self.codex_agents_dir = self.codex_dir / "agents"
        self.skill_dir = self.home / ".agents" / "skills" / "karpathy-subagent-mode"

    def run(self) -> int:
        self.ensure_dir(self.codex_dir)
        self.ensure_dir(self.codex_agents_dir)
        self.ensure_dir(self.skill_dir)

        self.merge_config(
            self.repo_root / "config_append.toml",
            self.codex_dir / "config.toml",
        )
        self.merge_agents_md(
            self.repo_root / "global_AGENTS_append.md",
            self.codex_dir / "AGENTS.md",
        )
        self.sync_file(
            self.repo_root / "reviewer.toml",
            self.codex_agents_dir / "reviewer.toml",
        )
        self.sync_file(
            self.repo_root / "debugger.toml",
            self.codex_agents_dir / "debugger.toml",
        )
        self.sync_file(
            self.repo_root / "skill" / "karpathy-subagent-mode" / "SKILL.md",
            self.skill_dir / "SKILL.md",
        )

        self.print_summary()
        return 0

    def ensure_dir(self, path: Path) -> None:
        if path.exists():
            self.actions.append(Action("noop-dir", path))
            return
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        kind = "create-dir" if not self.dry_run else "would-create-dir"
        self.actions.append(Action(kind, path))

    def sync_file(self, source: Path, target: Path) -> None:
        desired = self.read_text(source)
        self.write_text(target, desired)

    def merge_agents_md(self, source: Path, target: Path) -> None:
        block = self.read_text(source).strip()
        managed_block = f"{START_MARKER}\n{block}\n{END_MARKER}\n"
        existing = self.read_text(target) if target.exists() else None

        if not existing:
            self.write_text(target, managed_block)
            return

        if START_MARKER in existing and END_MARKER in existing:
            pattern = re.compile(
                rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}\n?",
                flags=re.DOTALL,
            )
            updated = pattern.sub(managed_block, existing, count=1)
            self.write_text(target, self.normalize_newlines(updated))
            return

        section_pattern = re.compile(
            rf"(?ms)^{re.escape(AGENTS_HEADING)}\n.*?(?=^## |\Z)"
        )
        match = section_pattern.search(existing)
        if match and any(anchor in match.group(0) for anchor in AGENTS_ANCHORS):
            updated = section_pattern.sub(managed_block.rstrip() + "\n\n", existing, count=1)
            self.write_text(target, self.normalize_newlines(updated))
            return

        if block in existing:
            updated = existing.replace(block, managed_block.rstrip(), 1)
            self.write_text(target, self.normalize_newlines(updated))
            return

        separator = "\n\n" if existing.rstrip() else ""
        updated = existing.rstrip() + separator + managed_block
        self.write_text(target, self.normalize_newlines(updated))

    def merge_config(self, source: Path, target: Path) -> None:
        desired = tomllib.loads(self.read_text(source))
        existing = self.read_text(target) if target.exists() else ""

        lines = existing.splitlines()
        root_values = {key: desired[key] for key in desired.keys() if key != "agents"}
        lines = self.upsert_root_assignments(lines, root_values)
        if "agents" in desired:
            lines = self.upsert_section_assignments(lines, "agents", desired["agents"])

        updated = "\n".join(lines).rstrip() + "\n"
        self.write_text(target, updated)

    def upsert_root_assignments(
        self,
        lines: list[str],
        desired: dict[str, object],
    ) -> list[str]:
        root_end = next(
            (idx for idx, line in enumerate(lines) if line.lstrip().startswith("[")),
            len(lines),
        )
        root_lines = lines[:root_end]
        tail = lines[root_end:]
        updated_root = self.merge_assignment_block(root_lines, desired)

        if updated_root and tail and updated_root[-1].strip():
            updated_root.append("")
        return updated_root + tail

    def upsert_section_assignments(
        self,
        lines: list[str],
        section: str,
        desired: dict[str, object],
    ) -> list[str]:
        header = f"[{section}]"
        start = next((idx for idx, line in enumerate(lines) if line.strip() == header), None)

        if start is None:
            updated = lines[:]
            if updated and updated[-1].strip():
                updated.append("")
            updated.append(header)
            for key, value in desired.items():
                updated.append(f"{key} = {self.to_toml_value(value)}")
            return updated

        end = next(
            (
                idx
                for idx in range(start + 1, len(lines))
                if lines[idx].lstrip().startswith("[")
            ),
            len(lines),
        )
        body = self.merge_assignment_block(lines[start + 1 : end], desired)
        return lines[: start + 1] + body + lines[end:]

    def merge_assignment_block(
        self,
        block_lines: list[str],
        desired: dict[str, object],
    ) -> list[str]:
        updated = block_lines[:]

        for key, value in desired.items():
            pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
            matches = [idx for idx, line in enumerate(updated) if pattern.match(line)]
            rendered = f"{key} = {self.to_toml_value(value)}"

            if matches:
                updated[matches[0]] = rendered
                for extra in reversed(matches[1:]):
                    del updated[extra]
            else:
                insert_at = len(updated)
                while insert_at > 0 and updated[insert_at - 1].strip() == "":
                    insert_at -= 1
                updated.insert(insert_at, rendered)

        return updated

    def write_text(self, target: Path, content: str) -> None:
        current = self.read_text(target) if target.exists() else None
        if current == content:
            self.actions.append(Action("noop-file", target))
            return

        if self.dry_run:
            kind = "would-update-file" if current is not None else "would-create-file"
            self.actions.append(Action(kind, target))
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        if current is not None:
            backup = target.with_name(f"{target.name}.bak.{self.timestamp}")
            shutil.copy2(target, backup)
            self.actions.append(Action("backup-file", backup, f"from {target.name}"))

        target.write_text(content, encoding="utf-8")
        kind = "update-file" if current is not None else "create-file"
        self.actions.append(Action(kind, target))

    def print_summary(self) -> None:
        for action in self.actions:
            suffix = f" ({action.detail})" if action.detail else ""
            print(f"{action.kind}: {action.path}{suffix}")

        changed = [
            action
            for action in self.actions
            if action.kind.startswith(("create", "update", "backup", "would-create", "would-update"))
        ]
        if not changed:
            print("result: no changes needed")
        elif self.dry_run:
            print("result: dry run complete")
        else:
            print("result: install/update complete")

    @staticmethod
    def normalize_newlines(text: str) -> str:
        return text.rstrip() + "\n"

    @staticmethod
    def read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    @staticmethod
    def to_toml_value(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return repr(value)
        if isinstance(value, str):
            return json.dumps(value)
        raise TypeError(f"Unsupported TOML value type: {type(value)!r}")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install or update the Codex Karpathy subagent bundle."
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Alternate HOME directory for installation or testing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent
    installer = Installer(repo_root=repo_root, home=args.home.expanduser(), dry_run=args.dry_run)
    return installer.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

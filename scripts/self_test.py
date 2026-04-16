#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_SECTIONS = (
    "Changes made",
    "Checks run",
    "Reviewer findings fixed",
    "Debugger findings fixed",
    "Remaining risks",
    "Unverified assumptions",
)

PROMPT = (
    "This repository contains a real bug. First inspect the repo, identify the smallest "
    "defensible fix, run `python3 -m unittest -q` as the relevant check, and follow the "
    "configured non-trivial-task workflow before finalizing."
)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


class SelfTestError(RuntimeError):
    pass


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def run_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    stdout_handle = stdout_path.open("w", encoding="utf-8") if stdout_path else subprocess.PIPE
    stderr_handle = stderr_path.open("w", encoding="utf-8") if stderr_path else subprocess.PIPE
    try:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                timeout=timeout,
                stdout=stdout_handle,
                stderr=stderr_handle,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SelfTestError(
                f"Command timed out after {timeout} seconds: {' '.join(command)}"
            ) from exc
    finally:
        if stdout_path:
            stdout_handle.close()
        if stderr_path:
            stderr_handle.close()

    if check and completed.returncode != 0:
        raise SelfTestError(
            f"Command failed with exit code {completed.returncode}: {' '.join(command)}"
        )
    return completed


def init_fixture_repo(source_dir: Path, target_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        target_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    run_command(["git", "init", "-b", "main"], cwd=target_dir)
    run_command(["git", "add", "."], cwd=target_dir)
    run_command(
        [
            "git",
            "-c",
            "user.name=Fixture Bot",
            "-c",
            "user.email=fixture@example.com",
            "commit",
            "-m",
            "Fixture baseline",
        ],
        cwd=target_dir,
    )


def read_jsonl(path: Path) -> list[dict]:
    events: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def strip_fenced_code_blocks(text: str) -> str:
    return re.sub(
        r"(?ms)^[ \t]*(```|~~~).*$.*?^[ \t]*\1[ \t]*$",
        "",
        text,
    )


def section_present(text: str, section: str) -> bool:
    text = strip_fenced_code_blocks(text)
    pattern = re.compile(
        rf"(?mi)^\s*(?:#{{1,6}}\s*)?(?:\*\*)?{re.escape(section)}(?:\*\*)?(?::\s*.*)?\s*$"
    )
    return bool(pattern.search(text))


def is_debugger_prompt(prompt: str) -> bool:
    normalized = normalize_text(prompt)
    return (
        ("reproduce the real bug" in normalized)
        or ("validate the changed behavior" in normalized)
        or ("return this shape: - reproduction_status" in normalized)
        or (
            "likely root cause" in normalized
            and "what remains unverified" in normalized
        )
    )


def is_reviewer_prompt(prompt: str) -> bool:
    normalized = normalize_text(prompt)
    return (
        "inspect for correctness, regressions, security, api/contract drift" in normalized
        or ("return this shape: - severity" in normalized and "smallest safe fix" in normalized)
        or (
            "correctness" in normalized
            and "regressions" in normalized
            and "missing or weak tests" in normalized
        )
    )


def preserve_artifacts(
    temp_root: Path,
    repo_root: Path,
    directory_name: str,
    error_message: str | None = None,
) -> Path:
    output_dir = repo_root / directory_name
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if error_message is not None:
        error_path = temp_root / "self_test_error.txt"
        error_path.write_text(f"{error_message}\n", encoding="utf-8")
    shutil.copytree(temp_root, output_dir)
    return output_dir


def snapshot_repo_tree(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if ".git" in path.relative_to(root).parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        snapshot[str(path.relative_to(root))] = digest
    return snapshot


def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run a behavior self-test for the Codex Karpathy subagent bundle."
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help=(
            "HOME directory whose Codex installation should be exercised. "
            "Defaults to your current HOME because the self-test validates your live Codex setup."
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=240,
        help="Timeout for the Codex run.",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary fixture workspace after the test.",
    )
    args = parser.parse_args(list(argv))

    repo_root = Path(__file__).resolve().parent.parent
    fixture_source = repo_root / "fixtures" / "python_divide_bug"
    if not fixture_source.exists():
        raise SelfTestError(f"Missing fixture directory: {fixture_source}")

    home = args.home.expanduser()
    with tempfile.TemporaryDirectory(prefix="codex-subagent-selftest-") as tmp_dir:
        temp_root = Path(tmp_dir)
        fixture_repo = temp_root / "fixture"
        init_fixture_repo(fixture_source, fixture_repo)
        final_message_path = temp_root / "codex_final.md"
        jsonl_path = temp_root / "codex_events.jsonl"
        stderr_path = temp_root / "codex_stderr.log"

        try:
            env = os.environ.copy()
            env["HOME"] = str(home)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            precheck = run_command(
                ["python3", "-m", "unittest", "-q"],
                cwd=fixture_repo,
                env=env,
                check=False,
            )
            if precheck.returncode == 0:
                raise SelfTestError("Fixture baseline unexpectedly passes before Codex runs.")
            baseline_snapshot = snapshot_repo_tree(fixture_repo)

            run_command(
                [
                    "codex",
                    "--dangerously-bypass-approvals-and-sandbox",
                    "exec",
                    "--json",
                    "--color",
                    "never",
                    "-o",
                    str(final_message_path),
                    "-C",
                    str(fixture_repo),
                    PROMPT,
                ],
                cwd=repo_root,
                env=env,
                timeout=args.timeout_seconds,
                stdout_path=jsonl_path,
                stderr_path=stderr_path,
            )

            postcheck = run_command(
                ["python3", "-m", "unittest", "-q"],
                cwd=fixture_repo,
                env=env,
                check=False,
            )
            final_snapshot = snapshot_repo_tree(fixture_repo)

            events = read_jsonl(jsonl_path)
            spawn_prompts = [
                (event.get("item") or {}).get("prompt", "")
                for event in events
                if event.get("type") == "item.completed"
                and isinstance(event.get("item"), dict)
                and event["item"].get("type") == "collab_tool_call"
                and event["item"].get("tool") == "spawn_agent"
            ]
            final_message = final_message_path.read_text(encoding="utf-8")

            debugger_spawns = sum(is_debugger_prompt(prompt) for prompt in spawn_prompts)
            reviewer_spawns = sum(is_reviewer_prompt(prompt) for prompt in spawn_prompts)
            has_all_sections = all(
                section_present(final_message, section) for section in REQUIRED_SECTIONS
            )
            changed_paths = sorted(
                {
                    *baseline_snapshot.keys(),
                    *final_snapshot.keys(),
                }
            )
            changed_paths = [
                path
                for path in changed_paths
                if baseline_snapshot.get(path) != final_snapshot.get(path)
            ]

            checks = [
                CheckResult(
                    "fixture_baseline_fails",
                    precheck.returncode != 0,
                    f"baseline unittest exit code = {precheck.returncode}",
                ),
                CheckResult(
                    "debugger_spawn_detected",
                    debugger_spawns >= 2,
                    f"debug-style spawn prompts detected = {debugger_spawns}",
                ),
                CheckResult(
                    "reviewer_spawn_detected",
                    reviewer_spawns >= 1,
                    f"review-style spawn prompts detected = {reviewer_spawns}",
                ),
                CheckResult(
                    "required_final_sections_present",
                    has_all_sections,
                    "all required final sections found"
                    if has_all_sections
                    else "missing one or more required final sections",
                ),
                CheckResult(
                    "fixture_passes_after_codex",
                    postcheck.returncode == 0,
                    f"post-run unittest exit code = {postcheck.returncode}",
                ),
                CheckResult(
                    "fixture_change_surface_pinned",
                    changed_paths == ["calc.py"],
                    f"changed fixture paths = {changed_paths or ['<none>']}",
                ),
            ]
        except SelfTestError as exc:
            print(f"self-test error: {exc}", file=sys.stderr)
            failure_dir = preserve_artifacts(
                temp_root,
                repo_root,
                ".selftest-last-failure",
                str(exc),
            )
            print(f"- failure_artifacts_saved_to: {failure_dir}")
            return 1

        print("Self-test summary")
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"- {check.name}: {status} ({check.detail})")

        print("Artifacts")
        print(f"- fixture_repo: {fixture_repo}")
        print(f"- final_message: {final_message_path}")
        print(f"- json_events: {jsonl_path}")
        print(f"- stderr_log: {stderr_path}")

        all_passed = all(check.passed for check in checks)

        if args.keep_temp and all_passed:
            preserved_dir = preserve_artifacts(
                temp_root,
                repo_root,
                ".selftest-last-success",
            )
            print(f"- preserved_artifacts: {preserved_dir}")
        elif args.keep_temp:
            print("- preserved_artifacts: will be written to .selftest-last-failure because one or more checks failed")
        else:
            print("- temp_root: removed automatically after exit")

        if not all_passed:
            failure_dir = preserve_artifacts(
                temp_root,
                repo_root,
                ".selftest-last-failure",
                "One or more self-test checks failed.",
            )
            print(f"- failure_artifacts_saved_to: {failure_dir}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

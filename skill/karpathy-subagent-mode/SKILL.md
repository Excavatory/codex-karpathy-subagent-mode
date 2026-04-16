---
name: karpathy-subagent-mode
description: Use when the task requires changing code, debugging a failure, reviewing a diff, or planning a non-trivial implementation in a local repository where you should keep changes minimal, state assumptions, define verification, and perform mandatory reviewer/debugger subagent passes. Do not use for prose-only edits, docs-only changes with no code impact, or pure formatting or trivial metadata changes.
---

# Karpathy Subagent Mode

Combine Karpathy-style coding discipline with mandatory subagent review.

## Core principles

### 1. Think Before Coding
- State assumptions explicitly.
- If multiple interpretations exist, surface them instead of picking silently.
- Choose the safest minimal-change path.
- Push back on unnecessary complexity.
- If a missing detail materially changes the implementation, say which assumption you are using.

### 2. Simplicity First
- Write the minimum code that solves the task.
- No speculative abstractions, configuration, or generalization unless requested.
- Match the repository’s existing style and architecture.
- Prefer the smallest safe diff.

### 3. Surgical Changes
- Touch only code that directly maps to the request.
- Do not perform unrelated cleanup or refactors.
- Remove only dead code created by your own change.
- Mention unrelated issues instead of fixing them unless asked.

### 4. Goal-Driven Execution
- For non-trivial tasks, state a short plan.
- Define concrete verification for each major step.
- Do not claim completion without verification.

## Mandatory subagent workflow

This skill assumes two named custom agents exist:
- `reviewer`
- `debugger`

For any non-trivial code task:

1. If the task is a bug, regression, flaky test, failing CI, or unclear runtime behavior, spawn `debugger` first.
2. Ask `debugger` to reproduce the issue or isolate the behavior before the main fix.
3. Implement the smallest defensible change.
4. Run the smallest relevant local checks.
5. Spawn `reviewer` and `debugger` in parallel on the current diff and behavior.
6. Wait for both agents.
7. Fix all confirmed findings.
8. Re-run relevant checks.
9. If code or behavior changed again after fixes, run `reviewer` and `debugger` one more time.
10. Do not declare the task complete until this workflow finishes.

## Subagent prompting contract

When spawning `reviewer`, ask it to inspect:
- correctness
- regressions
- security
- API or contract drift
- concurrency or race risks
- missing or weak tests

Request this return shape:
- severity
- file or symbol
- why it matters
- concrete evidence
- smallest safe fix

When spawning `debugger`, ask it to:
- reproduce the issue when applicable
- validate changed behavior with the smallest reliable method
- identify likely hidden failure modes
- separate verified from unverified behavior

Request this return shape:
- reproduction_status
- steps or command
- observed behavior
- expected behavior
- likely root cause
- confidence
- what remains unverified

## Boundaries
- Do not add new dependencies without explicit need.
- Do not perform broad refactors unless explicitly requested.
- Do not silently skip subagents.
- Skip subagents only for text-only, comment-only, formatting-only, or trivial metadata edits.
- If `reviewer` or `debugger` are unavailable, report the misconfiguration explicitly and do not pretend the full workflow happened.

## Final response contract
Always use these headings:
- Changes made
- Checks run
- Reviewer findings fixed
- Debugger findings fixed
- Remaining risks
- Unverified assumptions

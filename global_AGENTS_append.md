## Mandatory coding workflow

When the task requires changing code, debugging a failure, reviewing a diff, or planning a non-trivial implementation, activate `$karpathy-subagent-mode`.

Treat that skill as mandatory for non-trivial engineering work.

Use the named custom agents `reviewer` and `debugger` for the required subagent passes.
Do not silently substitute generic agents when those named agents are expected.
If either named agent is unavailable, report the misconfiguration explicitly.

Do not declare the task complete until the skill workflow has finished.
Subagent passes may be skipped only for text-only edits, comment-only edits, formatting-only edits, or trivial metadata changes, and the reason must be stated explicitly.

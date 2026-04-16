# Python Divide Bug Fixture

This fixture is intentionally tiny and intentionally broken.

Expected behavior:

- `divide(8, 2)` should return `4`
- `divide(8, 0)` should raise `ZeroDivisionError`

The baseline implementation violates the second rule.

It exists only for the bundle self-test, so the Codex run can prove:

- the task is treated as a real bug fix
- `debugger` is triggered
- `reviewer` is triggered
- the final answer includes the expected workflow sections
- the repository actually ends in a passing state

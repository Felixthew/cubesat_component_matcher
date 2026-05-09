"""
PreToolUse hook for `git commit`.

Runs as a Claude Code PreToolUse hook with a Bash matcher. Reads the tool
invocation JSON from stdin; if it's a `git commit` call, runs the scorer
unit tests and (when frontend files are staged) the Vite build. Blocks the
commit on failure by exiting 2.

Exit code conventions:
    0  proceed
    2  block (stderr shown to the model)
    1  hook itself errored (non-blocking; stderr shown to user)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GIT_COMMIT_RE = re.compile(r"^\s*git\s+commit\b")
FRONTEND_PREFIX = "frontend/"
# Project targets Python 3.12; pin the test runner to it so the hook isn't
# affected by whichever interpreter Claude Code happens to launch with.
PYTEST_PYTHON = ["py", "-3.12"]


def read_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def is_git_commit(event: dict) -> bool:
    if event.get("tool_name") != "Bash":
        return False
    command = event.get("tool_input", {}).get("command", "")
    return bool(GIT_COMMIT_RE.match(command))


def staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def run_scorer_tests() -> tuple[bool, str]:
    proc = subprocess.run(
        [*PYTEST_PYTHON, "-m", "pytest", "tests/scorer_test.py", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 5:
        return True, "no scorer tests collected (skipped)"
    if proc.returncode != 0:
        return False, proc.stdout + proc.stderr
    return True, "scorer tests passed"


def run_frontend_build() -> tuple[bool, str]:
    proc = subprocess.run(
        "npm run build",
        cwd=PROJECT_ROOT / "frontend",
        capture_output=True,
        text=True,
        check=False,
        shell=True,
    )
    if proc.returncode != 0:
        return False, proc.stdout + proc.stderr
    return True, "frontend build succeeded"


def main() -> int:
    try:
        event = read_event()
    except json.JSONDecodeError as exc:
        print(f"pre_commit_check: bad stdin JSON ({exc})", file=sys.stderr)
        return 1

    if not is_git_commit(event):
        return 0

    files = staged_files()
    if not files:
        return 0

    failures: list[str] = []

    ok, detail = run_scorer_tests()
    if not ok:
        failures.append(f"scorer tests FAILED:\n{detail}")

    needs_build = any(f.startswith(FRONTEND_PREFIX) for f in files)
    if needs_build:
        ok, detail = run_frontend_build()
        if not ok:
            failures.append(f"frontend build FAILED:\n{detail}")

    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"pre_commit_check: hook crashed ({exc!r})", file=sys.stderr)
        sys.exit(1)

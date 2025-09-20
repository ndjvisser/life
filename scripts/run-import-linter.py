#!/usr/bin/env python3
"""
Simple script to run import-linter for pre-commit hooks.
"""

import os
import subprocess
import sys


def try_import_linter_direct():
    """
    Attempt to run import-linter in-process by importing and invoking its CLI.

    Tries to import `lint_imports` from `importlinter.cli` and, if available,
    changes the current working directory to the repository root (derived from
    this script's `__file__` when present) before calling `lint_imports` with
    `config_filename="pyproject.toml"`.

    Returns:
        int | None: The exit code returned by `lint_imports` on success, or
        `None` if the import of `importlinter.cli` fails (import-linter not
        available).
    """
    try:
        from importlinter.cli import lint_imports

        # Change to the project root directory (handle case where __file__ might not be defined)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            os.chdir(project_root)
        except NameError:
            # __file__ not defined, assume we're already in the right directory
            pass

        # Run import-linter with config
        result = lint_imports(config_filename="pyproject.toml")
        return result
    except ImportError:
        return None


def try_import_linter_subprocess():
    """
    Attempt to run import-linter as an external subprocess.

    Tries candidate executables ["lint-imports", "lint-imports.exe"] in the repository root (derived from this script's location; falls back to the current working directory if __file__ is unavailable). For each executable it runs:
        [exe, "--config", "pyproject.toml"]

    - If a subprocess returns exit code 0, prints its stdout and returns 0.
    - If a subprocess returns a non-zero exit code, prints stdout and stderr and returns that exit code.
    - If an executable is not found, it continues to the next candidate.
    - If no executable is found or an unexpected error occurs, returns None.

    Returns:
        int | None: The subprocess exit code (0 for success, non-zero for failure), or None if no suitable executable was run.
    """
    try:
        # Try different possible executable names
        executables = ["lint-imports", "lint-imports.exe"]

        # Determine working directory
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
        except NameError:
            project_root = os.getcwd()

        for exe in executables:
            try:
                result = subprocess.run(
                    [exe, "--config", "pyproject.toml"],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                )
                if result.returncode == 0:
                    print(result.stdout)
                    return 0
                else:
                    print(result.stdout)
                    print(result.stderr)
                    return result.returncode
            except FileNotFoundError:
                continue
        return None
    except Exception:
        return None


def main():
    """
    Orchestrate running import-linter with two fallback strategies and exit with the chosen result.

    Attempts to run import-linter in-process via try_import_linter_direct(); if that returns a non-None exit code, calls sys.exit with that code. If not available, attempts try_import_linter_subprocess() and exits with its non-None result. If neither strategy is available, prints a warning with installation instructions and exits with code 0 (graceful success so commits are not blocked).

    Side effects:
    - May call sys.exit with the selected exit code.
    - Prints warning and guidance when import-linter is unavailable.
    """

    # Strategy 1: Try direct Python import
    result = try_import_linter_direct()
    if result is not None:
        sys.exit(result)

    # Strategy 2: Try subprocess
    result = try_import_linter_subprocess()
    if result is not None:
        sys.exit(result)

    # Strategy 3: Graceful fallback - warn but don't fail
    print("WARNING: import-linter not available, skipping import boundary checks")
    print("To enable import boundary validation, install import-linter:")
    print("  pip install import-linter")
    sys.exit(0)  # Exit with success to not block commits


if __name__ == "__main__":
    main()

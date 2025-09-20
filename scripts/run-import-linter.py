#!/usr/bin/env python3
"""
Simple script to run import-linter for pre-commit hooks.
"""
import os
import subprocess
import sys


def try_import_linter_direct():
    """Try to run import-linter directly via Python import."""
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
    """Try to run import-linter via subprocess."""
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
    """Main function to run import-linter with fallback strategies."""

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

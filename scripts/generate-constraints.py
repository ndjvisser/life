#!/usr/bin/env python3
"""
Generate pinned constraints files from requirements.in files using pip-tools.

This script ensures reproducible builds by creating constraints.txt files
that pin all dependencies to specific versions.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def main():
    """Generate constraints files from pyproject.toml."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate or check constraints files")
    parser.add_argument(
        "--check", action="store_true", help="Check if constraints are up to date"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    # Check if pip-tools is available
    returncode, _, stderr = run_command("pip-compile --version")
    if returncode != 0:
        print("ERROR: pip-tools not installed. Install with: pip install pip-tools")
        sys.exit(1)

    if args.check:
        print("Checking if constraints files are up to date...")

        # Check production constraints from pyproject.toml
        returncode, stdout, stderr = run_command(
            "pip-compile pyproject.toml --dry-run --quiet --resolver=backtracking --output-file constraints.txt",
            cwd=project_root,
        )
        if returncode != 0:
            print("❌ Production constraints are out of date")
            print(f"Error: {stderr}")
            sys.exit(1)

        print("✅ All constraints files are up to date")
        return

    print("Generating constraints files...")

    # Generate production constraints from pyproject.toml
    print("Generating production constraints...")
    returncode, stdout, stderr = run_command(
        "pip-compile pyproject.toml --output-file constraints.txt --resolver=backtracking",
        cwd=project_root,
    )
    if returncode != 0:
        print(f"ERROR generating production constraints: {stderr}")
        sys.exit(1)
    print("✅ Generated constraints.txt")

    print("\n🎉 Constraints file generated successfully!")
    print("Commit this file to ensure reproducible builds.")


if __name__ == "__main__":
    main()

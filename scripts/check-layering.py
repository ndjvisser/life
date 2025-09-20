#!/usr/bin/env python3
"""
Check for proper layering violations in the DDD architecture.
"""

import glob
import os
import re
import sys


def check_domain_layer_imports():
    """Check that domain layers don't import from application or infrastructure."""
    violations = []

    # Pattern to match imports from application or infrastructure layers
    pattern = re.compile(r"from\s+.*\.(application|infrastructure)")

    for domain_dir in glob.glob("life_dashboard/*/domain/"):
        for py_file in glob.glob(os.path.join(domain_dir, "**/*.py"), recursive=True):
            if "__pycache__" in py_file:
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.search(line):
                            violations.append(
                                {
                                    "file": py_file,
                                    "line": line_num,
                                    "content": line.strip(),
                                }
                            )
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
                continue

    return violations


def check_application_layer_imports():
    """Check that application layers don't import from interfaces."""
    violations = []

    # Pattern to match imports from interfaces layer
    pattern = re.compile(r"from\s+.*\.interfaces")

    for app_dir in glob.glob("life_dashboard/*/application/"):
        for py_file in glob.glob(os.path.join(app_dir, "**/*.py"), recursive=True):
            if "__pycache__" in py_file:
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.search(line):
                            violations.append(
                                {
                                    "file": py_file,
                                    "line": line_num,
                                    "content": line.strip(),
                                }
                            )
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
                continue

    return violations


def main():
    """Main function to check layering violations."""
    print("Checking for proper layering violations...")

    # Check domain layer violations
    print("Checking domain layer imports...")
    domain_violations = check_domain_layer_imports()

    if domain_violations:
        print("❌ Domain layer importing from application/infrastructure layers!")
        for violation in domain_violations:
            print(f"  {violation['file']}:{violation['line']}: {violation['content']}")
        return 1

    # Check application layer violations
    print("Checking application layer imports...")
    app_violations = check_application_layer_imports()

    if app_violations:
        print("❌ Application layer importing from interfaces layer!")
        for violation in app_violations:
            print(f"  {violation['file']}:{violation['line']}: {violation['content']}")
        return 1

    print("✅ Layering constraints satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

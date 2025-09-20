#!/usr/bin/env python3
"""
Check for proper layering violations in the DDD architecture.
"""

import glob
import os
import re
import sys


def check_domain_layer_imports():
    """
    Scan all Python files under life_dashboard/*/domain/ and return import violations where domain code imports from application or infrastructure layers.

    Searches recursively for .py files (skipping paths containing "__pycache__") and matches lines with the pattern `from <module>.(application|infrastructure)`. Files that cannot be read are skipped and a warning is printed to stdout.

    Returns:
        list: A list of violation dicts, each with keys:
            - "file" (str): path to the offending file
            - "line" (int): 1-based line number of the matching import
            - "content" (str): stripped source line that matched
    """
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
    r"""
    Scan application-layer Python files under life_dashboard/*/application/ and report any import statements that reference an `interfaces` module.

    Searches recursively for .py files (skipping paths containing "__pycache__"), matches lines against the regex `from\s+.*\.interfaces`, and collects violations as dicts with keys:
    - "file": path to the offending file
    - "line": 1-based line number
    - "content": the stripped source line

    If a file cannot be read it prints a warning and continues.

    Returns:
        list: A list of violation dictionaries as described above.
    """
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
    """
    Run layering checks for the repository and return an exit code.

    Performs two checks:
    - Ensures domain layer modules do not import from application or infrastructure layers.
    - Ensures application layer modules do not import from the interfaces layer.

    Prints human-readable summaries and any detected violations to stdout. Returns 0 if no violations were found, or 1 if any violations exist.
    """
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

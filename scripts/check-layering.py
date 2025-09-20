#!/usr/bin/env python3
"""
Check for proper layering violations in the DDD architecture.

Uses AST-based import analysis for robust detection of layering violations,
supporting all import styles, multiline imports, and avoiding false positives.
"""

import ast
import glob
import os
import sys


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze import statements and detect layering violations."""

    def __init__(self, file_path: str, forbidden_layers: set[str]):
        self.file_path = file_path
        self.forbidden_layers = forbidden_layers
        self.violations = []

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements (e.g., import foo.bar)."""
        for alias in node.names:
            self._check_import_path(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements (e.g., from foo import bar)."""
        if node.module:
            self._check_import_path(node.module, node.lineno)
        elif node.level > 0:
            # Handle relative imports like "from ..application import foo"
            # The module is None but we can infer from the names being imported
            for alias in node.names:
                if alias.name in self.forbidden_layers:
                    self._check_import_path(alias.name, node.lineno)
        self.generic_visit(node)

    def _check_import_path(self, import_path: str, line_num: int) -> None:
        """Check if an import path violates layering rules."""
        if not import_path:
            return

        # Split the import path into components
        path_parts = import_path.split(".")

        # Check if any forbidden layer appears in the import path
        for forbidden_layer in self.forbidden_layers:
            if forbidden_layer in path_parts:
                # Get the source line for context
                try:
                    with open(self.file_path, encoding="utf-8") as f:
                        lines = f.readlines()
                        content = (
                            lines[line_num - 1].strip()
                            if line_num <= len(lines)
                            else ""
                        )
                except (OSError, UnicodeDecodeError):
                    content = f"<could not read line {line_num}>"

                self.violations.append(
                    {
                        "file": self.file_path,
                        "line": line_num,
                        "content": content,
                        "forbidden_layer": forbidden_layer,
                        "import_path": import_path,
                    }
                )


def analyze_imports_in_file(file_path: str, forbidden_layers: set[str]) -> list[dict]:
    """
    Analyze imports in a Python file using AST parsing.

    Args:
        file_path: Path to the Python file to analyze
        forbidden_layers: Set of layer names that are forbidden to import

    Returns:
        List of violation dictionaries with file, line, content, etc.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Parse the AST, handling syntax errors gracefully
        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}:{e.lineno}: {e.msg}")
            return []

        # Analyze imports
        analyzer = ImportAnalyzer(file_path, forbidden_layers)
        analyzer.visit(tree)
        return analyzer.violations

    except Exception as e:
        print(f"Warning: Could not analyze {file_path}: {e}")
        return []


def check_domain_layer_imports():
    """
    Scan all Python files under life_dashboard/*/domain/ and return import violations
    where domain code imports from application, infrastructure, or interfaces layers.

    Uses AST-based analysis to detect all import styles including:
    - import statements
    - from-import statements
    - relative imports
    - multiline imports
    - imports inside TYPE_CHECKING blocks

    Returns:
        list: A list of violation dicts, each with keys:
            - "file" (str): path to the offending file
            - "line" (int): 1-based line number of the import
            - "content" (str): source line that contains the import
            - "forbidden_layer" (str): the layer that was improperly imported
            - "import_path" (str): the full import path
    """
    violations = []
    forbidden_layers = {"application", "infrastructure", "interfaces"}

    for domain_dir in glob.glob("life_dashboard/*/domain/"):
        for py_file in glob.glob(os.path.join(domain_dir, "**/*.py"), recursive=True):
            if "__pycache__" in py_file:
                continue

            file_violations = analyze_imports_in_file(py_file, forbidden_layers)
            violations.extend(file_violations)

    return violations


def check_application_layer_imports():
    """
    Scan application-layer Python files under life_dashboard/*/application/ and report
    any import statements that reference an `interfaces` module.

    Uses AST-based analysis to detect all import styles including:
    - import statements (import foo.interfaces.bar)
    - from-import statements (from foo.interfaces import bar)
    - relative imports (from ..interfaces import bar)
    - multiline imports
    - imports inside TYPE_CHECKING blocks

    Returns:
        list: A list of violation dictionaries with keys:
            - "file" (str): path to the offending file
            - "line" (int): 1-based line number of the import
            - "content" (str): source line that contains the import
            - "forbidden_layer" (str): the layer that was improperly imported
            - "import_path" (str): the full import path
    """
    violations = []
    forbidden_layers = {"interfaces"}

    for app_dir in glob.glob("life_dashboard/*/application/"):
        for py_file in glob.glob(os.path.join(app_dir, "**/*.py"), recursive=True):
            if "__pycache__" in py_file:
                continue

            file_violations = analyze_imports_in_file(py_file, forbidden_layers)
            violations.extend(file_violations)

    return violations


def main():
    """
    Run layering checks for the repository and return an exit code.

    Performs comprehensive layering checks using AST-based import analysis:
    - Ensures domain layer modules do not import from application, infrastructure, or interfaces layers
    - Ensures application layer modules do not import from the interfaces layer

    The AST-based approach handles all import styles and avoids false positives
    from comments, strings, or complex import patterns.

    Prints human-readable summaries and any detected violations to stdout.
    Returns 0 if no violations were found, or 1 if any violations exist.
    """
    print("Checking for proper layering violations using AST analysis...")

    total_violations = 0

    # Check domain layer violations
    print("Checking domain layer imports...")
    domain_violations = check_domain_layer_imports()

    if domain_violations:
        print(
            f"❌ Domain layer importing from forbidden layers! ({len(domain_violations)} violations)"
        )
        for violation in domain_violations:
            print(f"  {violation['file']}:{violation['line']}: {violation['content']}")
            print(
                f"    → Imports from '{violation['forbidden_layer']}' layer: {violation['import_path']}"
            )
        total_violations += len(domain_violations)
        print()

    # Check application layer violations
    print("Checking application layer imports...")
    app_violations = check_application_layer_imports()

    if app_violations:
        print(
            f"❌ Application layer importing from interfaces layer! ({len(app_violations)} violations)"
        )
        for violation in app_violations:
            print(f"  {violation['file']}:{violation['line']}: {violation['content']}")
            print(
                f"    → Imports from '{violation['forbidden_layer']}' layer: {violation['import_path']}"
            )
        total_violations += len(app_violations)
        print()

    if total_violations > 0:
        print(f"❌ Found {total_violations} layering violations")
        print("\nLayering rules:")
        print(
            "  • Domain layer must not import from: application, infrastructure, interfaces"
        )
        print("  • Application layer must not import from: interfaces")
        print("  • Infrastructure layer may import from: domain, application")
        print(
            "  • Interfaces layer may import from: domain, application, infrastructure"
        )
        return 1

    print("✅ All layering constraints satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

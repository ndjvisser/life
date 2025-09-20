#!/usr/bin/env python3
"""
Architecture boundary checker script.

This script validates that the bounded context architecture is properly
maintained and provides detailed feedback on any violations.
"""

import re
import subprocess
import sys
from pathlib import Path


class ArchitectureChecker:
    """Check architecture boundaries and constraints."""

    def __init__(self, root_path: str = "."):
        """
        Initialize the ArchitectureChecker.

        Parameters:
            root_path (str): Filesystem path to the repository root (defaults to ".").

        Creates these attributes:
            root_path (Path): Path object for the repository root.
            life_dashboard_path (Path): Path to the `life_dashboard` package inside the root.
            contexts (List[str]): Names of bounded-context directories to inspect.
            layers (List[str]): Expected layer names within each context.
        """
        self.root_path = Path(root_path)
        self.life_dashboard_path = self.root_path / "life_dashboard"
        self.contexts = [
            "dashboard",
            "stats",
            "quests",
            "skills",
            "achievements",
            "journals",
            "privacy",
        ]
        self.layers = ["domain", "application", "infrastructure", "interfaces"]

    def check_all(self) -> bool:
        """
        Run the full suite of architecture validation checks and return overall success.

        This method orchestrates the individual checks (context structure, Django imports in domain,
        cross-context imports, layering violations, and an optional external import-linter) and
        returns True only if every check passes. It prints a brief header and a final pass/fail
        summary as side effects.

        Returns:
            bool: True when all checks pass, False if any check fails.
        """
        print("🏗️  Checking Architecture Boundaries")
        print("=" * 50)

        all_passed = True

        # Check context structure
        if not self.check_context_structure():
            all_passed = False

        # Check Django imports in domain
        if not self.check_django_imports_in_domain():
            all_passed = False

        # Check cross-context imports
        if not self.check_cross_context_imports():
            all_passed = False

        # Check layering violations
        if not self.check_layering_violations():
            all_passed = False

        # Run import-linter if available
        if not self.run_import_linter():
            all_passed = False

        print("\n" + "=" * 50)
        if all_passed:
            print("✅ All architecture checks passed!")
        else:
            print("❌ Some architecture checks failed!")

        return all_passed

    def check_context_structure(self) -> bool:
        """
        Verify that each configured context exists under the life_dashboard folder and that required DDD layers are present.

        For every context in self.contexts this scans life_dashboard/<context> and checks for the presence of each layer in self.layers. Missing "domain" or "application" layers mark the check as failing; missing other layers are reported but do not make the check fail. The function prints a brief status for each context and layer.

        Returns:
            bool: True if all contexts contain the required layers ("domain" and "application"); False if any required layer is missing.
        """
        print("\n📁 Checking Context Structure")
        print("-" * 30)

        all_good = True

        for context in self.contexts:
            context_path = self.life_dashboard_path / context

            if not context_path.exists():
                print(f"⚠️  Context {context} does not exist")
                continue

            print(f"Checking {context} context...")

            for layer in self.layers:
                layer_path = context_path / layer
                if layer_path.exists():
                    print(f"  ✅ {layer}/ exists")
                else:
                    print(f"  ⚠️  {layer}/ missing")
                    if layer in ["domain", "application"]:
                        all_good = False

        return all_good

    def check_django_imports_in_domain(self) -> bool:
        """
        Scan each context's domain layer for Django imports and return whether the check passed.

        Recursively examines Python files under each context's `domain` directory and treats matches of top-level import patterns
        like `from django...` or `import django...` as violations.

        Returns:
            bool: True if no Django imports were found in any domain layer, False if one or more violations were detected.
        """
        print("\n🚫 Checking Django Imports in Domain Layers")
        print("-" * 45)

        violations = []

        for context in self.contexts:
            domain_path = self.life_dashboard_path / context / "domain"

            if not domain_path.exists():
                continue

            for py_file in domain_path.rglob("*.py"):
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for Django imports
                django_imports = re.findall(
                    r"^(from django.*|import django.*)", content, re.MULTILINE
                )

                if django_imports:
                    violations.append((py_file, django_imports))

        if violations:
            print("❌ Found Django imports in domain layers:")
            for file_path, imports in violations:
                print(f"  {file_path}:")
                for imp in imports:
                    print(f"    {imp}")
            return False
        else:
            print("✅ No Django imports found in domain layers")
            return True

    def check_cross_context_imports(self) -> bool:
        """
        Check domain-layer Python files for imports from other bounded contexts.

        Scans each context's domain/ directory for *.py files and looks for import statements that reference another context using the pattern `from life_dashboard.<other_context>...`. Reports any offending import lines and returns False when violations are found.

        Returns:
            bool: True if no cross-context imports were detected; False if one or more violations were found.
        """
        print("\n🔒 Checking Cross-Context Imports")
        print("-" * 35)

        violations = []

        for context in self.contexts:
            domain_path = self.life_dashboard_path / context / "domain"

            if not domain_path.exists():
                continue

            # Get other contexts
            other_contexts = [c for c in self.contexts if c != context]

            for py_file in domain_path.rglob("*.py"):
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for imports from other contexts
                for other_context in other_contexts:
                    pattern = rf"^from life_dashboard\.{other_context}.*"
                    cross_imports = re.findall(pattern, content, re.MULTILINE)

                    if cross_imports:
                        violations.append((py_file, cross_imports))

        if violations:
            print("❌ Found cross-context imports in domain layers:")
            for file_path, imports in violations:
                print(f"  {file_path}:")
                for imp in imports:
                    print(f"    {imp}")
            return False
        else:
            print("✅ No cross-context imports found in domain layers")
            return True

    def check_layering_violations(self) -> bool:
        """
        Check for violations of the module layering rules within each bounded context.

        Scans Python files under each context's `domain` and `application` layers and detects:
        - Domain files importing from the same context's `application` or `infrastructure` layers.
        - Application files importing from the same context's `interfaces` layer.

        Returns:
            bool: True if no layering violations were found; False if any offending import lines were detected.

        Notes:
        - Context directories or individual layers that do not exist are skipped.
        - Matches are based on simple regex patterns that capture the offending import lines; the function reports the file paths and matched import strings when violations are present.
        """
        print("\n📚 Checking Layer Dependencies")
        print("-" * 30)

        violations = []

        for context in self.contexts:
            context_path = self.life_dashboard_path / context

            if not context_path.exists():
                continue

            # Check domain layer doesn't import from application/infrastructure
            domain_path = context_path / "domain"
            if domain_path.exists():
                for py_file in domain_path.rglob("*.py"):
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Check for upward imports
                    upward_imports = re.findall(
                        rf"^from .*\.{context}\.(application|infrastructure).*",
                        content,
                        re.MULTILINE,
                    )

                    if upward_imports:
                        violations.append(
                            (
                                py_file,
                                upward_imports,
                                "Domain importing from upper layers",
                            )
                        )

            # Check application layer doesn't import from interfaces
            app_path = context_path / "application"
            if app_path.exists():
                for py_file in app_path.rglob("*.py"):
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Check for interface imports
                    interface_imports = re.findall(
                        rf"^from .*\.{context}\.interfaces.*", content, re.MULTILINE
                    )

                    if interface_imports:
                        violations.append(
                            (
                                py_file,
                                interface_imports,
                                "Application importing from interfaces",
                            )
                        )

        if violations:
            print("❌ Found layering violations:")
            for file_path, imports, reason in violations:
                print(f"  {file_path} - {reason}:")
                for imp in imports:
                    print(f"    {imp}")
            return False
        else:
            print("✅ No layering violations found")
            return True

    def run_import_linter(self) -> bool:
        """
        Run the external `import-linter` using the project's pyproject.toml config.

        Returns:
            bool: True if the linter exited with code 0 or if the `import-linter` executable was not found (skipped); False if the linter ran and returned a non-zero exit code.
        """
        print("\n🔍 Running Import Linter")
        print("-" * 25)

        try:
            result = subprocess.run(
                ["import-linter", "--config", "pyproject.toml"],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            if result.returncode == 0:
                print("✅ Import linter passed")
                return True
            else:
                print("❌ Import linter failed:")
                print(result.stdout)
                print(result.stderr)
                return False

        except FileNotFoundError:
            print("⚠️  import-linter not found, skipping")
            return True

    def generate_report(self) -> dict[str, any]:
        """
        Generate a structured architecture report for all configured contexts.

        Returns a dict with keys:
        - "contexts": mapping of context name -> {
            "exists": bool,
            "layers": mapping of layer name -> {
                "exists": bool,
                "file_count": int,
                "line_count": int
            },
            "files": {}  # reserved (currently unused)
          }
        - "violations": list (reserved, currently empty)
        - "recommendations": list (reserved, currently empty)

        Only contexts whose directory exists under self.life_dashboard_path are included.
        When counting lines, files that raise OSError or UnicodeDecodeError are skipped.
        """
        report = {"contexts": {}, "violations": [], "recommendations": []}

        for context in self.contexts:
            context_path = self.life_dashboard_path / context

            if not context_path.exists():
                continue

            context_info = {"exists": True, "layers": {}, "files": {}}

            for layer in self.layers:
                layer_path = context_path / layer
                layer_info = {
                    "exists": layer_path.exists(),
                    "file_count": 0,
                    "line_count": 0,
                }

                if layer_path.exists():
                    py_files = list(layer_path.rglob("*.py"))
                    layer_info["file_count"] = len(py_files)

                    total_lines = 0
                    for py_file in py_files:
                        try:
                            with open(py_file, encoding="utf-8") as f:
                                total_lines += len(f.readlines())
                        except (OSError, UnicodeDecodeError):
                            pass

                    layer_info["line_count"] = total_lines

                context_info["layers"][layer] = layer_info

            report["contexts"][context] = context_info

        return report


def main():
    """
    Entry point for the architecture checker CLI.

    With no arguments, instantiates ArchitectureChecker (root path = current directory), runs the full suite of architecture checks, and exits the process with status 0 on success or 1 on failure. If the first command-line argument is "--report", prints a human-readable architecture report summarizing each context's layers with file and line counts instead of running checks.

    This function calls sys.exit when running checks; it does not return a value.
    """
    checker = ArchitectureChecker()

    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # Generate detailed report
        report = checker.generate_report()

        print("📊 Architecture Report")
        print("=" * 30)

        for context, info in report["contexts"].items():
            print(f"\n{context.upper()} Context:")
            for layer, layer_info in info["layers"].items():
                status = "✅" if layer_info["exists"] else "❌"
                print(
                    f"  {status} {layer}: {layer_info['file_count']} files, {layer_info['line_count']} lines"
                )
    else:
        # Run checks
        success = checker.check_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

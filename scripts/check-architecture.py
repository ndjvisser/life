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
from typing import Dict


class ArchitectureChecker:
    """Check architecture boundaries and constraints."""

    def __init__(self, root_path: str = "."):
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
        """Run all architecture checks."""
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
        """Check that all contexts have proper DDD structure."""
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
        """Check for Django imports in domain layers."""
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
        """Check for cross-context imports in domain layers."""
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
        """Check for layering violations."""
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
        """Run import-linter if available."""
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

    def generate_report(self) -> Dict[str, any]:
        """Generate a detailed architecture report."""
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
    """Main entry point."""
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

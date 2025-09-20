#!/usr/bin/env python3
"""
Domain-first test runner for Life Dashboard.

This script demonstrates the domain-first testing approach by running
different types of tests in isolation and providing clear feedback
about test performance and coverage.

Usage:
    python scripts/run-domain-tests.py [options]

Options:
    --domain-only       Run only pure domain tests (fastest)
    --with-properties   Include property-based tests
    --with-contracts    Include contract tests
    --with-snapshots    Include snapshot tests
    --all-unit          Run all unit tests (domain + contracts + properties + snapshots)
    --integration       Run integration tests (requires Django)
    --coverage          Run with coverage reporting
    --parallel          Run tests in parallel
    --verbose           Verbose output
    --profile PROFILE   Hypothesis profile (dev, default, ci, thorough)
"""

import argparse
import os
import subprocess
import sys
import time


def run_command(cmd, description, capture_output=False, cwd=None):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"🚀 {description}")
    print(f"{'=' * 60}")
    print(f"Command: {' '.join(cmd)}")
    if cwd:
        print(f"Working Directory: {cwd}")
    print()

    start_time = time.time()

    try:
        if capture_output:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=cwd
            )
            output = result.stdout
        else:
            result = subprocess.run(cmd, check=True, cwd=cwd)
            output = None

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n✅ {description} completed successfully in {duration:.2f}s")
        return output

    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n❌ {description} failed after {duration:.2f}s")
        if capture_output and e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if capture_output and e.stderr:
            print("STDERR:")
            print(e.stderr)

        return None


def main():
    parser = argparse.ArgumentParser(
        description="Domain-first test runner for Life Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run only fast domain tests
    python scripts/run-domain-tests.py --domain-only

    # Run all unit tests with coverage
    python scripts/run-domain-tests.py --all-unit --coverage

    # Run property-based tests with thorough profile
    python scripts/run-domain-tests.py --with-properties --profile thorough

    # Run everything in parallel
    python scripts/run-domain-tests.py --integration --parallel --coverage
        """,
    )

    # Test selection options
    parser.add_argument(
        "--domain-only",
        action="store_true",
        help="Run only pure domain tests (fastest)",
    )
    parser.add_argument(
        "--with-properties", action="store_true", help="Include property-based tests"
    )
    parser.add_argument(
        "--with-contracts", action="store_true", help="Include contract tests"
    )
    parser.add_argument(
        "--with-snapshots", action="store_true", help="Include snapshot tests"
    )
    parser.add_argument(
        "--all-unit",
        action="store_true",
        help="Run all unit tests (domain + contracts + properties + snapshots)",
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests (requires Django)",
    )

    # Test execution options
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage reporting"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--profile",
        choices=["dev", "default", "ci", "thorough"],
        default="default",
        help="Hypothesis profile",
    )

    args = parser.parse_args()

    # Set up environment
    os.environ["HYPOTHESIS_PROFILE"] = args.profile

    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")
    else:
        pytest_cmd.append("-q")

    # Add parallel execution
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])

    # Add coverage
    if args.coverage:
        pytest_cmd.extend(
            [
                "--cov=life_dashboard",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-config=pyproject.toml",
            ]
        )

    # Determine test selection
    test_markers = []

    if args.domain_only:
        test_markers.append("domain")
        print("🎯 Running DOMAIN TESTS ONLY (pure Python, no Django)")

    elif args.all_unit:
        test_markers.extend(["unit"])
        print("🎯 Running ALL UNIT TESTS (domain + contracts + properties + snapshots)")

    else:
        # Build custom test selection
        if args.with_properties:
            test_markers.append("property")
        if args.with_contracts:
            test_markers.append("contract")
        if args.with_snapshots:
            test_markers.append("snapshot")

        if not test_markers and not args.integration:
            # Default to domain tests if nothing specified
            test_markers.append("domain")
            print("🎯 Running DOMAIN TESTS (default)")

    if args.integration:
        test_markers.append("integration")
        print("🎯 Including INTEGRATION TESTS (requires Django)")

    # Add marker selection to pytest command
    if test_markers:
        marker_expr = " or ".join(test_markers)
        pytest_cmd.extend(["-m", marker_expr])

    # Add test paths
    if args.domain_only or (
        test_markers and "domain" in test_markers and len(test_markers) == 1
    ):
        # For domain-only tests, specify exact files and ignore Django conftest
        pytest_cmd.extend(
            [
                "--ignore=life_dashboard/conftest.py",
                "--ignore=life_dashboard/life_dashboard/",
                "tests/",
                "life_dashboard/stats/tests/test_domain.py",
                "life_dashboard/stats/tests/test_domain_properties.py",
                "life_dashboard/quests/tests/test_domain_entities.py",
                "life_dashboard/quests/tests/test_domain_properties.py",
                "life_dashboard/skills/tests/test_domain_entities.py",
                "life_dashboard/skills/tests/test_domain_properties.py",
                "life_dashboard/achievements/tests/test_domain_entities.py",
                "life_dashboard/achievements/tests/test_domain_properties.py",
                "life_dashboard/journals/tests/test_domain_entities.py",
                "life_dashboard/journals/tests/test_domain_properties.py",
                "life_dashboard/dashboard/tests/test_domain.py",
                "life_dashboard/dashboard/tests/test_domain_properties.py",
            ]
        )
    elif args.with_contracts:
        pytest_cmd.extend(
            [
                "--ignore=life_dashboard/conftest.py",
                "tests/",
                "life_dashboard/stats/tests/test_service_contracts.py",
                "life_dashboard/quests/tests/test_service_contracts.py",
                "life_dashboard/skills/tests/test_service_contracts.py",
                "life_dashboard/achievements/tests/test_service_contracts.py",
                "life_dashboard/journals/tests/test_service_contracts.py",
                "life_dashboard/dashboard/tests/test_service_contracts.py",
            ]
        )
    elif args.with_snapshots:
        pytest_cmd.extend(
            [
                "--ignore=life_dashboard/conftest.py",
                "tests/",
                "life_dashboard/stats/tests/test_api_snapshots.py",
                "life_dashboard/quests/tests/test_api_snapshots.py",
                "life_dashboard/skills/tests/test_api_snapshots.py",
                "life_dashboard/achievements/tests/test_api_snapshots.py",
                "life_dashboard/journals/tests/test_api_snapshots.py",
                "life_dashboard/dashboard/tests/test_api_snapshots.py",
            ]
        )
    elif args.with_properties:
        pytest_cmd.extend(
            [
                "--ignore=life_dashboard/conftest.py",
                "tests/",
                "life_dashboard/stats/tests/test_domain_properties.py",
                "life_dashboard/quests/tests/test_domain_properties.py",
                "life_dashboard/skills/tests/test_domain_properties.py",
            ]
        )
    else:
        pytest_cmd.extend(
            [
                "tests/",
                "life_dashboard/stats/tests/",
                "life_dashboard/quests/tests/",
                "life_dashboard/skills/tests/",
                "life_dashboard/achievements/tests/",
                "life_dashboard/journals/tests/",
                "life_dashboard/dashboard/tests/",
                "life_dashboard/journals/tests/",
            ]
        )

    # Show test configuration
    print("\n📋 Test Configuration:")
    print(f"   Hypothesis Profile: {args.profile}")
    print(f"   Parallel Execution: {args.parallel}")
    print(f"   Coverage Reporting: {args.coverage}")
    print(f"   Test Markers: {', '.join(test_markers) if test_markers else 'all'}")

    # Run the tests
    total_start_time = time.time()

    # First, run a quick syntax check
    print("\n🔍 Running syntax and import checks...")
    syntax_cmd = ["python", "-m", "py_compile"] + [
        "life_dashboard/stats/domain/entities.py",
        "life_dashboard/stats/domain/value_objects.py",
        "life_dashboard/stats/domain/repositories.py",
        "life_dashboard/quests/domain/entities.py",
        "life_dashboard/quests/domain/value_objects.py",
        "life_dashboard/quests/domain/repositories.py",
        "life_dashboard/quests/domain/services.py",
        "life_dashboard/skills/domain/entities.py",
        "life_dashboard/skills/domain/value_objects.py",
        "life_dashboard/skills/domain/repositories.py",
        "life_dashboard/skills/domain/services.py",
        "life_dashboard/achievements/domain/entities.py",
        "life_dashboard/achievements/domain/value_objects.py",
        "life_dashboard/achievements/domain/repositories.py",
        "life_dashboard/achievements/domain/services.py",
    ]

    syntax_result = run_command(syntax_cmd, "Syntax Check", capture_output=True)
    if syntax_result is None:
        print("❌ Syntax check failed. Fix syntax errors before running tests.")
        return 1

    # Run the main test suite
    test_result = run_command(pytest_cmd, "Test Suite")

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    print(f"\n{'=' * 60}")
    print("📊 SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total execution time: {total_duration:.2f}s")

    if test_result is None:
        print("❌ Tests failed")
        return 1
    else:
        print("✅ All tests passed")

        if args.coverage:
            print("\n📈 Coverage report generated in htmlcov/")
            print(
                "   Open htmlcov/index.html in your browser to view detailed coverage"
            )

        # Show performance insights
        if args.domain_only:
            print("\n⚡ Performance Insight:")
            print("   Domain tests are fast because they don't use Django or databases")
            print("   This enables rapid feedback during development")

        if args.with_properties:
            print(f"\n🎲 Property-based testing with profile '{args.profile}':")
            profiles = {
                "dev": "10 examples (fast development)",
                "default": "100 examples (standard testing)",
                "ci": "1000 examples (CI/CD pipeline)",
                "thorough": "10000 examples (comprehensive testing)",
            }
            print(f"   {profiles.get(args.profile, 'Unknown profile')}")

        return 0


if __name__ == "__main__":
    sys.exit(main())

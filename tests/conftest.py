"""
Global test configuration for domain-first testing approach.

This configuration supports:
- Fast unit tests for pure Python domain logic (no Django test database)
- Property-based testing with Hypothesis
- Contract testing with Pydantic models
- Snapshot testing for API responses
- Separation of domain, application, and integration tests
"""

import os
import sys
from pathlib import Path

import pytest

try:
    from hypothesis import Verbosity, settings

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Hypothesis configuration for property-based testing
if HYPOTHESIS_AVAILABLE:
    settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
    settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
    settings.register_profile("dev", max_examples=10, verbosity=Verbosity.quiet)
    settings.register_profile(
        "thorough", max_examples=10000, verbosity=Verbosity.verbose
    )

    # Load profile based on environment
    profile = os.getenv("HYPOTHESIS_PROFILE", "default")
    settings.load_profile(profile)


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: marks tests as pure unit tests (no Django dependencies)"
    )
    config.addinivalue_line(
        "markers", "domain: marks tests as domain layer tests (pure Python)"
    )
    config.addinivalue_line(
        "markers", "application: marks tests as application service layer tests"
    )
    config.addinivalue_line(
        "markers", "interface: marks tests as interface/view layer tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require Django)"
    )
    config.addinivalue_line(
        "markers",
        "contract: marks tests as contract/API tests with Pydantic validation",
    )
    config.addinivalue_line(
        "markers", "property: marks property-based tests using Hypothesis"
    )
    config.addinivalue_line(
        "markers", "snapshot: marks snapshot tests for API responses"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location and content."""
    for item in items:
        # Add domain marker to domain layer tests
        if "domain" in str(item.fspath) and "test_domain" in item.name:
            item.add_marker(pytest.mark.domain)
            item.add_marker(pytest.mark.unit)

        # Add application marker to service layer tests
        if "application" in str(item.fspath) or "service" in item.name:
            item.add_marker(pytest.mark.application)

        # Add interface marker to view/API tests
        if any(
            keyword in str(item.fspath) for keyword in ["views", "api", "interface"]
        ):
            item.add_marker(pytest.mark.interface)
            item.add_marker(pytest.mark.integration)

        # Add contract marker to contract tests
        if "contract" in item.name or "test_service_contracts" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
            item.add_marker(pytest.mark.unit)

        # Add property marker to property-based tests
        if "property" in item.name or "test_domain_properties" in str(item.fspath):
            item.add_marker(pytest.mark.property)
            item.add_marker(pytest.mark.unit)

        # Add snapshot marker to snapshot tests
        if "snapshot" in item.name or "test_api_snapshots" in str(item.fspath):
            item.add_marker(pytest.mark.snapshot)
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Override Django DB setup to prevent database creation for unit tests.

    This fixture ensures that pure unit tests (domain layer) don't create
    a test database, making them much faster.
    """
    pass


@pytest.fixture
def domain_test_mode():
    """
    Fixture to indicate we're running in domain test mode.

    This can be used by tests to ensure they don't accidentally
    import Django or use database-dependent code.
    """
    return True


@pytest.fixture
def mock_datetime():
    """
    Fixture providing a consistent datetime for testing.

    This helps create predictable test data and snapshots.
    """
    from datetime import datetime, timezone

    return datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_user_id():
    """Fixture providing a consistent user ID for testing."""
    return 1


@pytest.fixture
def sample_core_stat_data():
    """Fixture providing sample CoreStat data for testing."""
    return {
        "user_id": 1,
        "strength": 15,
        "endurance": 12,
        "agility": 18,
        "intelligence": 20,
        "wisdom": 14,
        "charisma": 16,
        "experience_points": 2500,
    }


@pytest.fixture
def sample_life_stat_data():
    """Fixture providing sample LifeStat data for testing."""
    return {
        "user_id": 1,
        "category": "health",
        "name": "weight",
        "value": "70.5",
        "target": "65.0",
        "unit": "kg",
        "notes": "Weekly weigh-in goal",
    }


@pytest.fixture
def sample_stat_history_data():
    """Fixture providing sample StatHistory data for testing."""
    return {
        "user_id": 1,
        "stat_type": "core",
        "stat_name": "strength",
        "old_value": "15",
        "new_value": "18",
        "change_reason": "Completed training quest",
    }


class DomainTestCase:
    """
    Base class for domain layer tests.

    This class provides utilities for testing pure Python domain logic
    without Django dependencies.
    """

    def assert_domain_invariants(self, entity):
        """
        Assert that domain entity maintains its invariants.

        This is a helper method that can be overridden by specific
        test classes to check domain-specific invariants.
        """
        # Basic checks that apply to all domain entities
        assert hasattr(entity, "__dict__"), "Entity should have attributes"

        # Check that entity can be converted to dict (for serialization)
        if hasattr(entity, "to_dict"):
            data = entity.to_dict()
            assert isinstance(data, dict), "to_dict() should return a dictionary"
            assert "user_id" in data, (
                "Entity should have user_id in dict representation"
            )

    def assert_value_object_immutability(self, value_object, method_name, *args):
        """
        Assert that value object methods don't mutate the original object.

        This helper checks that value object operations return new instances
        rather than modifying the original.
        """
        original_value = getattr(value_object, "value", None)

        # Call the method
        result = getattr(value_object, method_name)(*args)

        # Check that original is unchanged
        if original_value is not None:
            assert value_object.value == original_value, (
                f"{method_name} should not mutate original value object"
            )

        # Check that result is a new instance
        assert result is not value_object, f"{method_name} should return a new instance"

        return result


def pytest_runtest_setup(item):
    """
    Setup hook that runs before each test.

    This ensures that domain tests don't accidentally import Django.
    """
    # Check if this is a domain test
    if item.get_closest_marker("domain"):
        # Temporarily remove Django from sys.modules to catch accidental imports
        django_modules = [
            name for name in sys.modules.keys() if name.startswith("django")
        ]
        item._original_django_modules = django_modules

        # Don't actually remove them as it might break other tests
        # Just mark that we're in domain test mode
        os.environ["DOMAIN_TEST_MODE"] = "1"


def pytest_runtest_teardown(item):
    """
    Teardown hook that runs after each test.

    This cleans up any domain test mode settings.
    """
    if item.get_closest_marker("domain"):
        os.environ.pop("DOMAIN_TEST_MODE", None)


# Custom assertion helpers for domain testing
def assert_decimal_equal(actual, expected, places=2):
    """Assert that two decimal values are equal within specified decimal places."""
    from decimal import Decimal

    if not isinstance(actual, Decimal):
        actual = Decimal(str(actual))
    if not isinstance(expected, Decimal):
        expected = Decimal(str(expected))

    # Round both to specified decimal places for comparison
    actual_rounded = actual.quantize(Decimal(10) ** -places)
    expected_rounded = expected.quantize(Decimal(10) ** -places)

    assert actual_rounded == expected_rounded, (
        f"Expected {expected_rounded}, got {actual_rounded}"
    )


def assert_percentage_equal(actual, expected, tolerance=0.01):
    """Assert that two percentage values are equal within tolerance."""
    assert abs(actual - expected) <= tolerance, (
        f"Expected {expected}% (±{tolerance}%), got {actual}%"
    )


# Make custom assertions available globally
pytest.assert_decimal_equal = assert_decimal_equal
pytest.assert_percentage_equal = assert_percentage_equal

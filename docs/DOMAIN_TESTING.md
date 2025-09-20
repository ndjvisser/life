# Domain-First Testing Guide

This document explains the domain-first testing approach implemented in the Life Dashboard project, which prioritizes fast, reliable tests for pure Python business logic.

## Overview

The domain-first testing approach separates tests into distinct layers, with each layer having different characteristics and purposes:

1. **Domain Tests** - Pure Python business logic (fastest)
2. **Application Tests** - Service layer orchestration
3. **Interface Tests** - Django views and API endpoints
4. **Integration Tests** - Full system integration

## Test Types

### 1. Domain Layer Tests (`@pytest.mark.domain`)

**Purpose**: Test pure Python business logic without any Django dependencies.

**Characteristics**:
- ⚡ **Fastest** - No database, no Django, no I/O
- 🔒 **Isolated** - Test business rules in isolation
- 🎯 **Focused** - Single responsibility testing
- 🔄 **Repeatable** - Deterministic and reliable

**Location**: `life_dashboard/*/tests/test_domain.py`

**Example**:
```python
@pytest.mark.domain
@pytest.mark.unit
def test_core_stat_level_calculation():
    """Test level calculation from experience points."""
    stat = CoreStat(user_id=1, experience_points=2500)

    assert stat.level == 3  # 2500 XP = level 3
    assert stat.get_stat_total() == 60  # Default stats sum
```

### 2. Property-Based Tests (`@pytest.mark.property`)

**Purpose**: Test domain invariants with randomly generated inputs using Hypothesis.

**Characteristics**:
- 🎲 **Comprehensive** - Tests edge cases automatically
- 🛡️ **Robust** - Finds bugs that manual tests miss
- 📊 **Configurable** - Different profiles for different scenarios

**Location**: `life_dashboard/*/tests/test_domain_properties.py`

**Example**:
```python
@given(
    strength=st.integers(min_value=1, max_value=100),
    experience_points=st.integers(min_value=0, max_value=2**31 - 1),
)
@pytest.mark.property
@pytest.mark.domain
def test_core_stat_invariants(strength, experience_points):
    """Test that CoreStat maintains invariants with any valid input."""
    stat = CoreStat(user_id=1, strength=strength, experience_points=experience_points)

    # Invariant: Level is correctly calculated
    expected_level = max(1, (experience_points // 1000) + 1)
    assert stat.level == expected_level
```

### 3. Contract Tests (`@pytest.mark.contract`)

**Purpose**: Validate service layer APIs using Pydantic models for type safety.

**Characteristics**:
- 📋 **Type-Safe** - Validates input/output contracts
- 🔄 **Serializable** - Tests JSON serialization/deserialization
- 🛡️ **Defensive** - Catches breaking changes early

**Location**: `life_dashboard/*/tests/test_service_contracts.py`

**Example**:
```python
@pytest.mark.contract
@pytest.mark.unit
def test_core_stat_response_contract():
    """Test that CoreStat response conforms to contract."""
    core_stat = CoreStat(user_id=1, strength=15)
    data = core_stat.to_dict()

    # Validate against Pydantic contract
    response = CoreStatResponse(**data)

    assert response.user_id == 1
    assert response.strength == 15
```

### 4. Snapshot Tests (`@pytest.mark.snapshot`)

**Purpose**: Capture exact API response structures to prevent breaking changes.

**Characteristics**:
- 📸 **Regression Detection** - Catches unintended API changes
- 🔍 **Detailed** - Shows exact differences in output
- 📝 **Documentation** - Serves as API documentation

**Location**: `life_dashboard/*/tests/test_api_snapshots.py`

**Example**:
```python
@pytest.mark.snapshot
@pytest.mark.unit
def test_core_stat_response_snapshot(snapshot):
    """Test CoreStat API response structure."""
    core_stat = CoreStat(user_id=1, strength=15)
    response_data = core_stat.to_dict()

    snapshot.assert_match(
        json.dumps(response_data, indent=2, sort_keys=True),
        "core_stat_basic.json"
    )
```

## Running Tests

### Quick Commands

```bash
# Fastest - Domain tests only (pure Python)
make test-domain

# Fast development cycle
make test-domain-fast

# Property-based testing
make test-properties

# Contract validation
make test-contracts

# API snapshot testing
make test-snapshots

# All unit tests
make test-all-unit

# With coverage
make test-domain-coverage

# Comprehensive testing
make test-thorough

# Parallel execution
make test-parallel
```

### Advanced Usage

```bash
# Custom test runner with options
python scripts/run-domain-tests.py --domain-only --verbose
python scripts/run-domain-tests.py --with-properties --profile thorough
python scripts/run-domain-tests.py --all-unit --coverage --parallel
```

### Hypothesis Profiles

Configure property-based testing intensity:

- `dev` - 10 examples (fast development)
- `default` - 100 examples (standard testing)
- `ci` - 1000 examples (CI/CD pipeline)
- `thorough` - 10000 examples (comprehensive testing)

```bash
# Set profile via environment
export HYPOTHESIS_PROFILE=thorough
make test-properties

# Or via command line
python scripts/run-domain-tests.py --with-properties --profile thorough
```

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                    # Global test configuration
└── test_architecture.py          # Architecture boundary tests

life_dashboard/stats/tests/
├── __init__.py
├── test_domain_entities.py        # Pure domain logic tests
├── test_domain_properties.py      # Property-based tests
├── test_service_contracts.py      # Contract tests with Pydantic
├── test_api_snapshots.py         # Snapshot tests for API responses
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests

life_dashboard/quests/tests/
├── __init__.py
├── test_domain_entities.py        # Quest/Habit domain logic tests
├── test_domain_properties.py      # Property-based tests for quests
├── test_service_contracts.py      # Quest/Habit service contracts
├── test_api_snapshots.py         # Quest/Habit API snapshots
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests

life_dashboard/skills/tests/
├── __init__.py
├── test_domain_entities.py        # Skill/Category domain logic tests
├── test_domain_properties.py      # Property-based tests for skills
├── test_service_contracts.py      # Skill service contracts
├── test_api_snapshots.py         # Skill API snapshots
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests

life_dashboard/achievements/tests/
├── __init__.py
├── test_domain_entities.py        # Achievement domain logic tests
├── test_domain_properties.py      # Property-based tests for achievements
├── test_service_contracts.py      # Achievement service contracts
├── test_api_snapshots.py         # Achievement API snapshots
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests

life_dashboard/journals/tests/
├── __init__.py
├── test_domain_entities.py        # Journal domain logic tests
├── test_domain_properties.py      # Property-based tests for journals
├── test_service_contracts.py      # Journal service contracts
├── test_api_snapshots.py         # Journal API snapshots
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests

life_dashboard/dashboard/tests/
├── __init__.py
├── test_domain.py                 # Dashboard domain logic tests
├── test_domain_properties.py      # Property-based tests for dashboard
├── test_service_contracts.py      # Dashboard service contracts
├── test_api_snapshots.py         # Dashboard API snapshots
├── test_application_services.py   # Application layer tests
└── test_views.py                  # Django view integration tests
```

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (no Django dependencies)
- `@pytest.mark.domain` - Domain layer tests (pure Python)
- `@pytest.mark.application` - Application service layer tests
- `@pytest.mark.interface` - Interface/view layer tests
- `@pytest.mark.integration` - Integration tests (require Django)
- `@pytest.mark.contract` - Contract tests with Pydantic
- `@pytest.mark.property` - Property-based tests with Hypothesis
- `@pytest.mark.snapshot` - Snapshot tests for API responses
- `@pytest.mark.slow` - Slow tests (can be excluded)

### Running Specific Test Types

```bash
# Run only domain tests
pytest -m domain

# Run unit tests (excluding integration)
pytest -m "unit and not integration"

# Run property-based tests
pytest -m property

# Run contract tests
pytest -m contract

# Run snapshot tests
pytest -m snapshot

# Exclude slow tests
pytest -m "not slow"
```

## Performance Characteristics

### Test Speed Comparison

| Test Type | Speed | Database | Django | Examples |
|-----------|-------|----------|--------|----------|
| Domain | ⚡⚡⚡ Fastest | ❌ No | ❌ No | ~0.1s per test |
| Property | ⚡⚡ Fast | ❌ No | ❌ No | ~1s per test |
| Contract | ⚡⚡ Fast | ❌ No | ❌ No | ~0.2s per test |
| Snapshot | ⚡⚡ Fast | ❌ No | ❌ No | ~0.1s per test |
| Application | ⚡ Medium | ❌ No | ✅ Yes | ~0.5s per test |
| Interface | 🐌 Slow | ✅ Yes | ✅ Yes | ~2s per test |
| Integration | 🐌🐌 Slowest | ✅ Yes | ✅ Yes | ~5s per test |

### Development Workflow

1. **Red-Green-Refactor with Domain Tests**:
   ```bash
   # Write failing domain test
   make test-domain-fast  # ~5 seconds

   # Implement domain logic
   make test-domain-fast  # ~5 seconds

   # Refactor with confidence
   make test-domain-fast  # ~5 seconds
   ```

2. **Property-Based Validation**:
   ```bash
   # Validate with random inputs
   make test-properties  # ~30 seconds
   ```

3. **Contract Validation**:
   ```bash
   # Ensure API contracts are maintained
   make test-contracts  # ~10 seconds
   ```

4. **Full Validation**:
   ```bash
   # Complete test suite
   make test-all-unit  # ~60 seconds
   ```

## Best Practices

### 1. Domain Test Guidelines

**DO**:
- Test business rules and invariants
- Use pure Python objects (no Django imports)
- Test edge cases and boundary conditions
- Keep tests focused and isolated
- Use descriptive test names

**DON'T**:
- Import Django in domain tests
- Use database or external dependencies
- Test implementation details
- Write overly complex test setups

### 2. Property-Based Testing Guidelines

**DO**:
- Test invariants that should always hold
- Use appropriate strategies for your domain
- Start with simple properties
- Use `assume()` to filter invalid inputs

**DON'T**:
- Test implementation-specific behavior
- Use overly complex strategies
- Ignore failing property tests
- Test non-deterministic behavior

### 3. Contract Testing Guidelines

**DO**:
- Define clear Pydantic models for APIs
- Test both valid and invalid inputs
- Validate serialization/deserialization
- Use meaningful field constraints

**DON'T**:
- Over-specify contracts (be flexible)
- Test Pydantic itself
- Ignore validation errors
- Make contracts too rigid

### 4. Snapshot Testing Guidelines

**DO**:
- Use for stable API responses
- Review snapshot changes carefully
- Keep snapshots readable (formatted JSON)
- Use predictable test data

**DON'T**:
- Snapshot volatile data (timestamps, IDs)
- Blindly accept snapshot changes
- Use for frequently changing APIs
- Include sensitive data in snapshots

## Troubleshooting

### Common Issues

1. **Domain tests importing Django**:
   ```python
   # ❌ Wrong - Django import in domain test
   from django.test import TestCase

   # ✅ Correct - Pure Python test
   import pytest
   from ..domain.entities import CoreStat
   ```

2. **Property tests failing randomly**:
   ```python
   # ❌ Wrong - Testing implementation details
   @given(st.integers())
   def test_random_behavior(value):
       result = some_random_function(value)
       assert result == expected_random_value  # Will fail randomly

   # ✅ Correct - Testing invariants
   @given(st.integers(min_value=1, max_value=100))
   def test_stat_value_invariant(value):
       stat = StatValue(value)
       assert 1 <= stat.value <= 100  # Always true
   ```

3. **Snapshot tests breaking on formatting changes**:
   ```python
   # ✅ Use consistent formatting
   snapshot.assert_match(
       json.dumps(data, indent=2, sort_keys=True),
       "response.json"
   )
   ```

### Debugging Tips

1. **Use verbose output**:
   ```bash
   make test-domain PYTEST_ARGS="-v -s"
   ```

2. **Run specific test**:
   ```bash
   pytest life_dashboard/stats/tests/test_domain.py::TestCoreStat::test_level_calculation -v
   ```

3. **Debug property-based tests**:
   ```bash
   # Use dev profile for faster debugging
   HYPOTHESIS_PROFILE=dev pytest -m property -v
   ```

4. **Update snapshots**:
   ```bash
   pytest --snapshot-update
   ```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Domain-First Testing

on: [push, pull_request]

jobs:
  domain-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Run domain tests
        run: |
          python scripts/run-domain-tests.py --domain-only --verbose
        env:
          HYPOTHESIS_PROFILE: ci

      - name: Run property-based tests
        run: |
          python scripts/run-domain-tests.py --with-properties --verbose
        env:
          HYPOTHESIS_PROFILE: ci

      - name: Run contract tests
        run: |
          python scripts/run-domain-tests.py --with-contracts --verbose

      - name: Run all unit tests with coverage
        run: |
          python scripts/run-domain-tests.py --all-unit --coverage --verbose
        env:
          HYPOTHESIS_PROFILE: ci
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: domain-tests
        name: Domain Tests
        entry: python scripts/run-domain-tests.py --domain-only
        language: system
        pass_filenames: false
        always_run: true
```

## Benefits

### 1. **Development Speed**
- Fast feedback loop (5 seconds vs 5 minutes)
- Rapid red-green-refactor cycles
- Immediate validation of business logic

### 2. **Test Reliability**
- No flaky database tests
- Deterministic results
- Isolated test execution

### 3. **Code Quality**
- Forces separation of concerns
- Encourages pure functions
- Validates business invariants

### 4. **Maintainability**
- Clear test organization
- Easy to understand and modify
- Self-documenting contracts

### 5. **Confidence**
- Property-based testing finds edge cases
- Contract tests prevent breaking changes
- Snapshot tests catch regressions

## Migration Guide

### From Traditional Django Tests

1. **Identify pure business logic**:
   ```python
   # Before: Django test
   class TestCoreStatModel(TestCase):
       def test_level_calculation(self):
           user = User.objects.create(username="test")
           stat = CoreStat.objects.create(user=user, experience_points=2500)
           self.assertEqual(stat.level, 3)

   # After: Domain test
   @pytest.mark.domain
   def test_level_calculation():
       stat = CoreStat(user_id=1, experience_points=2500)
       assert stat.level == 3
   ```

2. **Extract domain entities**:
   ```python
   # Before: Django model with business logic
   class CoreStat(models.Model):
       def calculate_level(self):
           return max(1, (self.experience_points // 1000) + 1)

   # After: Pure domain entity
   @dataclass
   class CoreStat:
       def calculate_level(self) -> int:
           return max(1, (self.experience_points // 1000) + 1)
   ```

3. **Add property-based tests**:
   ```python
   @given(experience_points=st.integers(min_value=0, max_value=2**31 - 1))
   @pytest.mark.property
   def test_level_calculation_properties(experience_points):
       stat = CoreStat(user_id=1, experience_points=experience_points)
       expected_level = max(1, (experience_points // 1000) + 1)
       assert stat.level == expected_level
   ```

### Gradual Adoption

1. Start with new features using domain-first approach
2. Extract existing business logic to domain entities
3. Add property-based tests for critical invariants
4. Create contract tests for service APIs
5. Add snapshot tests for stable endpoints

## Conclusion

The domain-first testing approach provides:

- ⚡ **Fast feedback** for rapid development
- 🛡️ **Robust validation** with property-based testing
- 📋 **Type safety** with contract testing
- 📸 **Regression protection** with snapshot testing
- 🏗️ **Better architecture** through separation of concerns

This approach enables confident refactoring, rapid development cycles, and maintainable code that scales with your team and project complexity.

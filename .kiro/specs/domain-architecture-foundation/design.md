# Design Document

## Overview

The Domain Architecture Foundation implements a modular monolith using Domain-Driven Design principles. The architecture provides clean separation between business logic and infrastructure concerns while maintaining the operational simplicity of a single deployable unit. This foundation enables rapid development and testing while preparing for potential future service extraction.

## Architecture

### Modular Monolith Structure

```
life_dashboard/
├── dashboard/          # User management and central coordination
├── stats/             # Core RPG stats and life metrics
├── quests/            # Quest and habit management
├── achievements/      # Achievement and milestone system
├── journals/          # Personal reflection and insights
├── skills/            # Skill development and progression
├── integrations/      # External API connections
├── analytics/         # Intelligence and predictions
└── shared/            # Cross-cutting concerns
    ├── domain/        # Shared domain primitives
    ├── events/        # Event system infrastructure
    └── infrastructure/ # Shared infrastructure utilities
```

### Layered Architecture per Context

Each bounded context follows the hexagonal architecture pattern:

```
context_name/
├── domain/                    # Pure business logic (no framework dependencies)
│   ├── entities.py           # Domain entities with business rules
│   ├── value_objects.py      # Immutable value types with validation
│   ├── repositories.py       # Abstract repository interfaces
│   ├── services.py           # Domain services for complex business logic
│   └── events.py             # Domain events specific to this context
├── application/              # Use case orchestration
│   ├── services.py           # Application services (command handlers)
│   ├── queries.py            # Read-only query handlers (CQRS)
│   ├── handlers.py           # Domain event handlers
│   └── dto.py                # Data transfer objects
├── infrastructure/           # Framework and external concerns
│   ├── models.py             # Django ORM models
│   ├── repositories.py       # Concrete repository implementations
│   ├── adapters.py           # External service adapters
│   └── migrations/           # Database migrations
└── interfaces/               # External interfaces
    ├── views.py              # Django views
    ├── serializers.py        # API serializers
    ├── urls.py               # URL routing
    └── admin.py              # Django admin configuration
```

## Testing Strategy

### Test Organisation
Tests are split by bounded context, and within each context they mirror the architectural layers.
This ensures high locality, clear boundaries, and the ability to enforce purity rules.

```
repo/
├── contexts/
│   ├── stats/
│   │   ├── domain/ ...
│   │   ├── application/ ...
│   │   ├── infrastructure/ ...
│   │   ├── interfaces/ ...
│   │   └── tests/
│   │       ├── unit/
│   │       │   ├── domain/
│   │       │   └── application/
│   │       ├── integration/
│   │       │   ├── infrastructure/      # ORM, repos (hits DB)
│   │       │   └── interfaces/          # views/serializers with Django test client
│   │       ├── contract/                # adapters ↔ external services (e.g. Pact)
│   │       └── acceptance/              # context-level use cases (in-memory repos)
│   ├── quests/
│   │   └── ... (same structure)
│   └── ...
├── tests/
│   ├── e2e/                              # cross-context flows via public API
│   ├── architecture/                     # import rules, layer boundaries
│   └── shared/                           # reusable fixtures/factories for tests only
```

### Pytest Markers and Orchestration
`pytest.ini`defines markers for orchestration:

```
[pytest]
markers =
    unit: fast, pure domain/application tests
    integration: DB/files/network involved
    contract: external API contracts
    acceptance: context-level use cases across layers
    e2e: cross-context end-to-end flows
addopts = -q
testpaths = contexts tests
```
Typical commands:

- Dev inner loop: `pytest -m unit`

- CI per-context: `pytest contexts/stats/tests -m "unit or integration"`

- Full CI (merge): `pytest -m "unit or integration or contract or acceptance"`

- Nightly regression: `pytest -m e2e`

### Fixture Strategy

- __Unit tests__: use Mother Objects / Object Factories inside `tests/unit/domain/factories.py` (no Django).

- __Integration tests__: use `factory_boy` models with Django ORM.

- __Shared test utilities__: live under `tests/shared/`.

### Architecture Guardrails

Domain purity: Architecture tests ensure `domain/` never imports Django or DRF.

Context isolation: Contexts may not import each other directly (only via shared contracts).

Escalation path: unit → integration → contract → acceptance → e2e.

## Example Tests

### Domain unit test:
```python
# contexts/stats/tests/unit/domain/test_core_stat.py
from contexts.stats.domain.entities import CoreStat
from contexts.stats.domain.value_objects import StatDelta

def test_apply_delta_increases_current_value():
    strength = CoreStat(name="Strength", base=10, current=10)
    strength.apply(StatDelta(+2))
    assert strength.current == 12
```

### Application acceptance test:
```python
# contexts/stats/tests/acceptance/test_gain_xp.py
from contexts.stats.application.services import GainXP
from contexts.stats.tests.fakes import InMemoryProfileRepo

def test_gain_xp_levels_up_on_threshold():
    repo = InMemoryProfileRepo(seed_level=1, seed_xp=95)
    service = GainXP(profile_repo=repo)
    service.execute(profile_id="u1", amount=10)
    profile = repo.get("u1")
    assert profile.level == 2
```

### Infrastructure integration test:
```python
# contexts/stats/tests/integration/infrastructure/test_django_repo.py
import pytest
pytestmark = pytest.mark.integration

from contexts.stats.infrastructure.repositories import DjangoProfileRepository
from contexts.stats.infrastructure.models import Profile

def test_repo_persists_and_reads_profile(db):
    repo = DjangoProfileRepository()
    created = repo.create(username="nigel")
    assert Profile.objects.filter(id=created.id).exists()
```
## CI Strategy

- Job A (seconds): `pytest -m unit`

- Job B (minutes): `pytest -m integration`

- Job C (optional PR): `pytest -m contract or acceptance`

- Job D (scheduled): `pytest -m e2e`

Unit tests enforce minimum coverage; e2e coverage is tracked but not blocking.


## Components and Interfaces

### Domain Event System

#### Event Base Class
```python
@dataclass
class BaseEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

    def to_json(self) -> str:
        """Serialize event to JSON for persistence/debugging"""

    @classmethod
    def from_json(cls, json_str: str) -> 'BaseEvent':
        """Deserialize event from JSON"""
```

#### Event Dispatcher
```python
class EventDispatcher:
    def __init__(self):
        self._handlers: Dict[Type[BaseEvent], List[EventHandler]] = {}

    def register_handler(self, event_type: Type[BaseEvent], handler: EventHandler):
        """Register event handler with version compatibility checking"""

    def publish(self, event: BaseEvent):
        """Publish event to all compatible handlers"""

    def publish_async(self, event: BaseEvent):
        """Publish event asynchronously via Celery (optional)"""
```

#### Event Handler Decorator
```python
def handles(event_type: Type[BaseEvent], min_version: str = "1.0.0"):
    """Decorator to register event handlers with version compatibility"""
    def decorator(handler_func):
        # Register handler with dispatcher
        return handler_func
    return decorator
```

### Repository Pattern

#### Abstract Repository Interface
```python
class Repository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass
```

#### Domain-Specific Repository
```python
class UserRepository(Repository[User]):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_active_users(self) -> List[User]:
        pass
```

#### Infrastructure Implementation
```python
class DjangoUserRepository(UserRepository):
    def get_by_id(self, entity_id: int) -> Optional[User]:
        try:
            django_user = DjangoUserModel.objects.get(id=entity_id)
            return self._to_domain_entity(django_user)
        except DjangoUserModel.DoesNotExist:
            return None

    def _to_domain_entity(self, django_model) -> User:
        """Convert Django model to domain entity"""

    def _to_django_model(self, domain_entity: User) -> DjangoUserModel:
        """Convert domain entity to Django model"""
```

### Service Layer

#### Application Service Pattern
```python
class UserService:
    def __init__(self, user_repo: UserRepository, event_dispatcher: EventDispatcher):
        self._user_repo = user_repo
        self._event_dispatcher = event_dispatcher

    def register_user(self, email: str, password: str) -> User:
        """Command: Register new user"""
        # Validate input
        # Create domain entity
        # Save via repository
        # Publish UserRegistered event

    def add_experience(self, user_id: int, experience: int, source: str) -> None:
        """Command: Award experience points"""
        # Load user entity
        # Apply business rules
        # Save changes
        # Publish ExperienceAwarded event
```

#### Query Service (CQRS)
```python
class UserQueries:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def get_user_profile(self, user_id: int) -> Optional[UserProfileDTO]:
        """Query: Get user profile for display"""

    def get_leaderboard(self, limit: int = 10) -> List[LeaderboardEntryDTO]:
        """Query: Get top users by experience"""
```

### Privacy Framework

#### Consent Management
```python
class ConsentService:
    def grant_consent(self, user_id: int, purpose: str, data_types: List[str]) -> None:
        """Grant consent for specific data processing purpose"""

    def revoke_consent(self, user_id: int, purpose: str) -> None:
        """Revoke consent and trigger data cleanup"""

    def check_consent(self, user_id: int, purpose: str, data_type: str) -> bool:
        """Check if user has granted consent for data processing"""
```

#### Privacy-Aware Event Processing
```python
@handles(StatUpdated)
def process_stat_update(event: StatUpdated):
    if not consent_service.check_consent(event.user_id, "analytics", "stats"):
        logger.info(f"Skipping analytics processing - no consent for user {event.user_id}")
        return
    # Process event normally
```

## Data Models

### Domain Entities

#### User Entity
```python
@dataclass
class User:
    id: Optional[int]
    email: str
    experience_points: int
    level: int
    created_at: datetime

    def add_experience(self, points: int) -> List[BaseEvent]:
        """Add experience and return events for level-ups"""
        events = []
        old_level = self.level
        self.experience_points += points
        new_level = self._calculate_level()

        if new_level > old_level:
            self.level = new_level
            events.append(LevelUp(
                user_id=self.id,
                previous_level=old_level,
                new_level=new_level,
                total_experience=self.experience_points
            ))

        return events
```

#### Value Objects
```python
@dataclass(frozen=True)
class StatValue:
    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 100:
            raise ValueError("Stat value must be between 1 and 100")

@dataclass(frozen=True)
class ExperiencePoints:
    points: int

    def __post_init__(self):
        if self.points < 0:
            raise ValueError("Experience points cannot be negative")
```

### Infrastructure Models

#### Django Model Mapping
```python
class DjangoUserModel(models.Model):
    email = models.EmailField(unique=True)
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dashboard_user'
```

## Error Handling

### Domain Exceptions
```python
class DomainException(Exception):
    """Base class for domain-specific exceptions"""
    pass

class InvalidStatValueError(DomainException):
    """Raised when stat value is outside valid range"""
    pass

class InsufficientExperienceError(DomainException):
    """Raised when operation requires more experience than available"""
    pass
```

### Application Error Handling
```python
class ApplicationService:
    def handle_command(self, command):
        try:
            # Execute domain logic
            pass
        except DomainException as e:
            logger.warning(f"Domain rule violation: {e}")
            raise ApplicationError(f"Operation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ApplicationError("Internal error occurred")
```

## Testing Strategy

### Domain Testing
```python
class TestUser:
    def test_add_experience_increases_points(self):
        user = User(id=1, email="test@example.com", experience_points=0, level=1)
        events = user.add_experience(100)

        assert user.experience_points == 100
        assert len(events) == 0  # No level up yet

    def test_level_up_generates_event(self):
        user = User(id=1, email="test@example.com", experience_points=950, level=1)
        events = user.add_experience(100)

        assert user.level == 2
        assert len(events) == 1
        assert isinstance(events[0], LevelUp)
```

### Integration Testing
```python
class TestUserService:
    def test_register_user_publishes_event(self):
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_dispatcher = Mock(spec=EventDispatcher)
        service = UserService(mock_repo, mock_dispatcher)

        # Act
        user = service.register_user("test@example.com", "password")

        # Assert
        mock_repo.save.assert_called_once()
        mock_dispatcher.publish.assert_called_once()
        event = mock_dispatcher.publish.call_args[0][0]
        assert isinstance(event, UserRegistered)
```

### BDD Feature Testing
```gherkin
Feature: User Experience System
  As a user
  I want to gain experience from completing activities
  So that I can level up and track my progress

  Scenario: User gains experience and levels up
    Given I am a user with 950 experience points at level 1
    When I complete an activity worth 100 experience points
    Then my experience should increase to 1050 points
    And I should advance to level 2
    And a level up event should be published
```

## Architecture Enforcement

### Import Linting Rules
```python
# .import-linter.toml
[tool.importlinter]
root_package = "life_dashboard"

[[tool.importlinter.contracts]]
name = "Domain layer independence"
type = "forbidden"
source_modules = ["life_dashboard.*.domain"]
forbidden_modules = ["django", "rest_framework"]

[[tool.importlinter.contracts]]
name = "Context boundaries"
type = "forbidden"
source_modules = ["life_dashboard.stats"]
forbidden_modules = ["life_dashboard.quests", "life_dashboard.achievements"]
```

### Type Checking Configuration
```ini
# mypy.ini
[mypy]
strict = True
warn_return_any = True
warn_unused_configs = True

[mypy-life_dashboard.*.domain.*]
disallow_any_generics = True
disallow_untyped_defs = True
```

### Development Tooling
```python
# Hot-reload configuration for domain changes
class DomainWatcher:
    def watch_domain_changes(self):
        """Watch domain/ directories and reload without Django restart"""

# Architecture validation
class ArchitectureValidator:
    def validate_dependencies(self):
        """Ensure dependency rules are followed"""

    def validate_event_schemas(self):
        """Ensure events match canonical catalog"""
```

## Observability and Monitoring

The system incorporates observability features to ensure reliability, debuggability,
and performance monitoring across all bounded contexts.

### Structured Logging

- All requests, commands, and events include a trace_id for correlation across logs.
- Domain events are logged at publish time with event_id, timestamp, and payload summary.
- Errors and warnings include context (user_id, context name, service name).

### Metrics

- Technical metrics: request latency, error rates, database query times.
- Business KPIs: number of quests completed, level-ups, active users.
- Metrics exported via Prometheus/OpenTelemetry compatible endpoints.

### Health Checks

- Each bounded context exposes a /health endpoint.
- Includes domain checks (e.g., repository reachability), infrastructure checks (DB, cache), and external API availability.

### Tracing

- OpenTelemetry integrated for distributed tracing.
- Spans cover application services, repository calls, and event publishing.
- Trace IDs propagated through events and API calls.

### Monitoring Integration

- Logs, metrics, and traces aggregated in an observability stack (e.g., ELK/EFK + Prometheus + Jaeger)
- Alerting configured on error spikes, SLA violations, and business KPI thresholds.


This design provides a solid foundation for building a maintainable, testable, and scalable personal life dashboard system while adhering to DDD principles and preparing for future growth.

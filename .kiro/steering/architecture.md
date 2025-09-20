# Architecture Principles

## Modular Monolith Approach

LIFE follows a modular monolith architecture that provides the benefits of modularity without the operational complexity of microservices. This approach is ideal for an early-stage product that needs to iterate quickly while maintaining clean boundaries for future growth.

## Domain-Driven Design (DDD)

### Bounded Contexts

Each major domain area is organized as a bounded context with clear boundaries:

- **Stats Context**: Core RPG stats and life metrics tracking with trend analysis
- **Integrations Context**: External API connections, data sync, and validation
- **Quests Context**: Goal management, quests, and habits with auto-completion
- **Skills Context**: Skill development and progression with AI recommendations
- **Achievements Context**: Badges, titles, and intelligent recognition system
- **Journals Context**: Personal reflection, journaling, and insight generation
- **Analytics Context**: Trend analysis, predictions, and intelligence services
- **Dashboard Context**: User management, central coordination, and aggregation

### Context Structure

Each bounded context follows a layered architecture:

```
context_name/
├── domain/          # Pure Python business logic (no Django imports)
├── infrastructure/  # Django models, external APIs, database access
├── application/     # Use case orchestration, service layer
└── interfaces/      # Django views, serializers, API endpoints
```

## Service Layer Pattern

### Cross-Context Communication

- **NO direct model imports** between contexts
- Use application services for cross-context operations
- Implement domain events for decoupled communication
- Maintain anti-corruption layers at context boundaries

### Example Service Structure

```python
# stats/application/services.py
class StatService:
    def update_core_stat(self, user_id: int, stat_name: str, value: int):
        # Orchestrate domain logic
        # Raise domain events if needed
        pass

    def sync_external_stat(self, user_id: int, source: str, data: dict):
        # Validate and transform external data
        # Update stats and raise events
        pass

# integrations/application/services.py
class IntegrationService:
    def sync_health_data(self, user_id: int):
        # Fetch from health APIs
        # Transform and validate data
        # Raise ExternalDataReceived events
        pass

    def setup_integration(self, user_id: int, integration_type: str, credentials: dict):
        # Configure external API connection
        # Test connection and store credentials
        pass

# analytics/application/services.py
class AnalyticsService:
    def generate_insights(self, user_id: int):
        # Analyze patterns across all contexts
        # Generate personalized insights
        # Raise InsightGenerated events
        pass

    def predict_trends(self, user_id: int, prediction_type: str):
        # Use ML models to forecast outcomes
        # Raise PredictionUpdated events
        pass

# quests/application/services.py
class QuestService:
    def complete_quest(self, user_id: int, quest_id: int):
        # Complete quest logic
        # Raise QuestCompleted event
        pass

    def auto_complete_from_integration(self, user_id: int, external_data: dict):
        # Check for auto-completion triggers
        # Complete relevant quests automatically
        pass
```

## Domain Events

Use in-memory domain events to decouple contexts:

### Core Events
- `QuestCompleted(user_id, quest_id, experience_gained)`
- `HabitStreakAchieved(user_id, habit_id, streak_count)`
- `SkillLevelUp(user_id, skill_id, new_level)`
- `AchievementUnlocked(user_id, achievement_id)`

### Integration Events
- `ExternalDataReceived(user_id, source, data_type, raw_data)`
- `DataSyncCompleted(user_id, integration_type, sync_timestamp)`
- `IntegrationFailed(user_id, integration_type, error_details)`
- `AutoCompletionTriggered(user_id, quest_id, trigger_source)`

### Intelligence Events
- `PatternDetected(user_id, pattern_type, confidence_score)`
- `InsightGenerated(user_id, insight_type, content)`
- `RecommendationCreated(user_id, recommendation_type, action)`
- `BalanceShiftDetected(user_id, shift_type, severity)`
- `PredictionUpdated(user_id, prediction_type, forecast_data)`

## Database Strategy

### Single Database with Context Namespacing

- Maintain single SQLite/PostgreSQL database for transaction simplicity
- Use table prefixes per context: `stats_*`, `quests_*`, `skills_*`, etc.
- Keep migrations organized per Django app
- Avoid foreign keys across context boundaries

### Repository Pattern

Implement repository interfaces in domain layer, concrete implementations in infrastructure:

```python
# domain/repositories.py
class StatRepository(ABC):
    def get_user_stats(self, user_id: int) -> UserStats: ...
    def save_stats(self, stats: UserStats) -> None: ...
    def get_stat_history(self, user_id: int, days: int) -> List[StatHistory]: ...

class IntegrationRepository(ABC):
    def get_active_integrations(self, user_id: int) -> List[Integration]: ...
    def store_external_data(self, data_point: ExternalDataPoint) -> None: ...

# infrastructure/repositories.py
class DjangoStatRepository(StatRepository):
    def get_user_stats(self, user_id: int) -> UserStats:
        # Django ORM implementation

class DjangoIntegrationRepository(IntegrationRepository):
    def get_active_integrations(self, user_id: int) -> List[Integration]:
        # Django ORM implementation with external API clients
```

### Integration Adapter Pattern

Abstract external APIs behind domain interfaces:

```python
# integrations/domain/adapters.py
class HealthDataAdapter(ABC):
    def fetch_workout_data(self, user_credentials: dict) -> List[WorkoutData]: ...
    def fetch_sleep_data(self, user_credentials: dict) -> List[SleepData]: ...

# integrations/infrastructure/adapters.py
class AppleHealthAdapter(HealthDataAdapter):
    def fetch_workout_data(self, user_credentials: dict) -> List[WorkoutData]:
        # Apple HealthKit API implementation

class StravaAdapter(HealthDataAdapter):
    def fetch_workout_data(self, user_credentials: dict) -> List[WorkoutData]:
        # Strava API implementation
```

## Testing Strategy

### Four-Layer Testing

1. **Domain Tests**: Pure Python unit tests for business logic
2. **Application Tests**: Service layer integration tests
3. **Interface Tests**: Django view/API integration tests
4. **Feature Tests**: BDD scenarios for user journeys and complex workflows

### Test Organization

```
tests/
├── unit/           # Domain layer tests
├── integration/    # Application service tests
├── e2e/           # Full Django integration tests
└── features/      # BDD feature files and step definitions

features/
├── quest_management.feature
├── habit_tracking.feature
├── external_integrations.feature
├── insight_generation.feature
├── achievement_unlocking.feature
└── steps/
    ├── quest_steps.py
    ├── integration_steps.py
    └── common_steps.py
```

### BDD Feature Examples

```gherkin
# features/external_integrations.feature
Feature: External Data Integration
  As a user who wants automated stat tracking
  I want to connect external services
  So that my stats update automatically

  Scenario: Successful health data sync
    Given I have connected my fitness tracker
    When I complete a workout
    Then my strength and endurance stats should increase
    And I should receive XP for the activity
    And relevant achievements should be evaluated

  Scenario: Quest auto-completion from productivity sync
    Given I have connected my task manager
    And I have an active quest "Complete 5 work tasks"
    When I mark 5 tasks as complete in my task manager
    Then the quest should be automatically completed
    And I should receive the quest reward
    And my productivity stats should update
```

## Future Scalability

### Microservice Readiness

The modular monolith structure prepares for potential microservice extraction:

- Clear context boundaries make service extraction mechanical
- Service layers provide natural API boundaries
- Domain events enable async communication patterns
- Repository pattern abstracts data access

### When to Split

Only consider microservice extraction when TWO of these occur:
- Independent scaling requirements
- Distinct reliability/SLA needs
- Separate data privacy boundaries

## Code Quality Standards

### Import Rules

- Domain layer: No Django imports allowed
- Application layer: Django imports only for infrastructure concerns
- Infrastructure layer: Full Django framework access
- Interfaces layer: Django views, serializers, etc.

### Dependency Direction

```
Interfaces → Application → Domain ← Infrastructure
```

Dependencies always point inward toward the domain core.

## Anti-Patterns to Avoid

- Direct model imports across contexts
- Business logic in Django views or models
- Tight coupling through shared database tables
- Premature microservice extraction
- "Big ball of Django models" without service layers

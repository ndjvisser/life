# Canonical Domain Event System

This directory contains the implementation of the canonical domain event system as specified in Task 1.4 of the personal life dashboard project.

## Overview

The domain event system provides a lightweight, type-safe, and version-compatible event dispatcher for decoupling bounded contexts in the modular monolith architecture. All events follow the exact payload schemas defined in the Domain Events Catalog.

## Key Features

### ✅ BaseEvent Class
- Event ID generation using UUID4
- Automatic timestamp assignment
- Version field for schema evolution
- JSON serialization/deserialization support

### ✅ Canonical Events
**ALL 39 events** from the Domain Events Catalog are implemented with exact payload schemas:

**Core System Events (4)**:
- UserRegistered, UserProfileUpdated, ExperienceAwarded, LevelUp

**Stats Events (4)**:
- CoreStatUpdated, LifeStatUpdated, StatMilestoneReached, TrendDetected

**Quest Events (7)**:
- QuestCreated, QuestCompleted, QuestFailed, QuestChainUnlocked, HabitCompleted, HabitStreakAchieved, HabitStreakBroken

**Skills Events (4)**:
- SkillPracticed, SkillLevelUp, SkillMasteryAchieved, SkillRecommendationGenerated

**Achievement Events (4)**:
- AchievementUnlocked, TitleUnlocked, BadgeEarned, AchievementProgressUpdated

**Journal Events (5)**:
- JournalEntryCreated, JournalEntryUpdated, InsightGenerated, PatternDetected, ReflectionPromptSuggested

**Integration Events (6)**:
- IntegrationConnected, IntegrationDisconnected, ExternalDataReceived, DataSyncCompleted, DataSyncFailed, AutoCompletionTriggered

**Analytics Events (5)**:
- BalanceScoreCalculated, BalanceShiftDetected, PredictionGenerated, RecommendationCreated, UserEngagementAnalyzed

### ✅ Event Dispatcher
- **Version Compatibility**: Handlers specify min/max supported versions
- **Type Safety**: Strongly typed event handling with proper inheritance
- **Error Handling**: Graceful handling of handler exceptions
- **Event Logging**: Optional event logging for debugging and testing
- **Handler Management**: Register, unregister, and clear handlers

### ✅ Privacy-Aware Processing
- **Consent Validation**: Check user consent for privacy-sensitive events
- **Granular Controls**: Per-event-type privacy controls
- **Audit Logging**: Track data processing for compliance

### ✅ Developer Experience
- **@handles Decorator**: Simple decorator for registering event handlers
- **Global Dispatcher**: Convenient global access to event publishing
- **Comprehensive Testing**: 46 unit tests covering all functionality

## Usage Examples

### Basic Event Publishing
```python
from shared.domain.events import QuestCompleted
from shared.domain.event_dispatcher import publish_event

# Create and publish an event
event = QuestCompleted(
    user_id=123,
    quest_id=456,
    quest_type="daily",
    experience_reward=25,
    completion_timestamp=datetime.utcnow(),
    auto_completed=False
)

publish_event(event)
```

### Event Handler Registration
```python
from shared.domain.event_dispatcher import handles

@handles(QuestCompleted, min_version="1.0.0")
def award_experience(event: QuestCompleted):
    print(f"Awarding {event.experience_reward} XP to user {event.user_id}")
```

### Version Compatibility
```python
@handles(QuestCompleted, min_version="1.0.0", max_version="2.0.0")
def legacy_handler(event: QuestCompleted):
    # This handler only works with v1.x events
    pass
```

## Architecture Benefits

### 🔄 Loose Coupling
Events enable bounded contexts to communicate without direct dependencies, maintaining clean architectural boundaries.

### 📈 Scalability
The event system supports both synchronous (for fast tests) and asynchronous processing (via future Celery integration).

### 🛡️ Type Safety
All events are strongly typed with exact payload schemas, preventing runtime errors and enabling IDE support.

### 🔄 Version Evolution
Built-in version compatibility checking allows events to evolve over time without breaking existing handlers.

### 🔒 Privacy Compliance
Privacy-aware processing ensures GDPR compliance and user consent validation.

## Testing

The system includes comprehensive unit tests:

```bash
# Run all domain event tests
python -m pytest shared/tests/ -v

# Run specific test suites
python -m pytest shared/tests/test_domain_events.py -v
python -m pytest shared/tests/test_event_dispatcher.py -v
```

## Demo

See `shared/examples/event_system_demo.py` for a complete working example that demonstrates:
- Event handler registration
- Event publishing and handling
- Cross-event workflows (quest completion → experience award → achievement unlock)
- Event logging and debugging

## Next Steps

This foundational event system enables:
1. **Task 1.5**: Replace Django signals with canonical domain events
2. **Cross-context integration**: Stats, quests, achievements, and analytics can now communicate via events
3. **Future async processing**: Easy integration with Celery for background processing
4. **External system integration**: Events can be published to external systems (Kafka, webhooks, etc.)

## Files Structure

```
shared/
├── domain/
│   ├── events.py              # All canonical events
│   └── event_dispatcher.py    # Event dispatcher and handlers
├── tests/
│   ├── test_domain_events.py     # Event serialization tests
│   └── test_event_dispatcher.py  # Dispatcher functionality tests
├── examples/
│   └── event_system_demo.py   # Working demo
└── README.md                  # This file
```

The canonical domain event system is now complete and ready for use across all bounded contexts in the Life OS platform.

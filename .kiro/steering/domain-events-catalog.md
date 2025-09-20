# Domain Events Catalog

This is the canonical source of truth for all domain events in the LIFE system. All event definitions, handlers, and documentation must reference this catalog.

## Event Schema Format

Each event follows this structure:
```python
@dataclass
class EventName(BaseEvent):
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    # Event-specific payload fields
```

## Core Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `UserRegistered` | 1.0.0 | dashboard | `user_id: int, email: str, registration_timestamp: datetime` | User completes registration process |
| `UserProfileUpdated` | 1.0.0 | dashboard | `user_id: int, updated_fields: Dict[str, Any], previous_values: Dict[str, Any]` | User profile information changed |
| `ExperienceAwarded` | 1.0.0 | dashboard | `user_id: int, experience_points: int, source_type: str, source_id: int, reason: str` | Experience points awarded to user |
| `LevelUp` | 1.0.0 | dashboard | `user_id: int, previous_level: int, new_level: int, total_experience: int` | User reaches new level threshold |

## Stats Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `CoreStatUpdated` | 1.0.0 | stats | `user_id: int, stat_name: str, previous_value: int, new_value: int, source: str` | Core RPG stat value changed |
| `LifeStatUpdated` | 1.0.0 | stats | `user_id: int, category: str, subcategory: str, previous_value: Decimal, new_value: Decimal, unit: str, source: str` | Life stat metric updated |
| `StatMilestoneReached` | 1.0.0 | stats | `user_id: int, stat_type: str, stat_name: str, milestone_value: int, milestone_type: str` | Stat reaches significant milestone |
| `TrendDetected` | 1.0.0 | stats | `user_id: int, stat_name: str, trend_type: str, confidence_score: float, duration_days: int` | Statistical trend identified in stat data |

## Quest Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `QuestCreated` | 1.0.0 | quests | `user_id: int, quest_id: int, quest_type: str, title: str, difficulty: str, experience_reward: int` | New quest created by user |
| `QuestCompleted` | 1.0.0 | quests | `user_id: int, quest_id: int, quest_type: str, experience_reward: int, completion_timestamp: datetime, auto_completed: bool` | Quest marked as completed |
| `QuestFailed` | 1.0.0 | quests | `user_id: int, quest_id: int, quest_type: str, failure_reason: str, failure_timestamp: datetime` | Quest marked as failed |
| `QuestChainUnlocked` | 1.0.0 | quests | `user_id: int, parent_quest_id: int, unlocked_quest_ids: List[int], chain_name: str` | Quest completion unlocks new quests |
| `HabitCompleted` | 1.0.0 | quests | `user_id: int, habit_id: int, completion_date: date, streak_count: int, experience_reward: int` | Habit instance completed |
| `HabitStreakAchieved` | 1.0.0 | quests | `user_id: int, habit_id: int, streak_count: int, streak_type: str, bonus_experience: int` | Habit streak milestone reached |
| `HabitStreakBroken` | 1.0.0 | quests | `user_id: int, habit_id: int, previous_streak: int, broken_date: date` | Habit streak interrupted |

## Skills Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `SkillPracticed` | 1.0.0 | skills | `user_id: int, skill_id: int, practice_duration: int, experience_gained: int, practice_timestamp: datetime` | User practices a skill |
| `SkillLevelUp` | 1.0.0 | skills | `user_id: int, skill_id: int, previous_level: int, new_level: int, total_experience: int, category: str` | Skill reaches new level |
| `SkillMasteryAchieved` | 1.0.0 | skills | `user_id: int, skill_id: int, mastery_level: str, total_practice_time: int, mastery_timestamp: datetime` | Skill reaches mastery threshold |
| `SkillRecommendationGenerated` | 1.0.0 | skills | `user_id: int, recommended_skill_ids: List[int], recommendation_reason: str, confidence_score: float` | AI generates skill recommendations |

## Achievement Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `AchievementUnlocked` | 1.0.0 | achievements | `user_id: int, achievement_id: int, achievement_name: str, tier: str, experience_reward: int, unlock_timestamp: datetime` | User unlocks achievement |
| `TitleUnlocked` | 1.0.0 | achievements | `user_id: int, title_id: int, title_name: str, unlock_conditions: Dict[str, Any], unlock_timestamp: datetime` | User unlocks new title |
| `BadgeEarned` | 1.0.0 | achievements | `user_id: int, badge_id: int, badge_name: str, badge_category: str, earned_timestamp: datetime` | User earns badge |
| `AchievementProgressUpdated` | 1.0.0 | achievements | `user_id: int, achievement_id: int, current_progress: int, required_progress: int, progress_percentage: float` | Progress toward achievement updated |

## Journal Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `JournalEntryCreated` | 1.0.0 | journals | `user_id: int, entry_id: int, entry_type: str, title: str, word_count: int, mood_rating: Optional[int], tags: List[str]` | New journal entry created |
| `JournalEntryUpdated` | 1.0.0 | journals | `user_id: int, entry_id: int, updated_fields: Dict[str, Any], update_timestamp: datetime` | Journal entry modified |
| `InsightGenerated` | 1.0.0 | journals | `user_id: int, insight_id: int, insight_type: str, content: str, confidence_score: float, source_entries: List[int]` | AI generates insight from journal data |
| `PatternDetected` | 1.0.0 | journals | `user_id: int, pattern_id: int, pattern_type: str, description: str, confidence_score: float, detection_timestamp: datetime` | Behavioral pattern identified |
| `ReflectionPromptSuggested` | 1.0.0 | journals | `user_id: int, prompt_id: int, prompt_text: str, prompt_category: str, trigger_event: str` | System suggests reflection topic |

## Integration Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `IntegrationConnected` | 1.0.0 | integrations | `user_id: int, integration_id: int, service_name: str, integration_type: str, connection_timestamp: datetime` | External service connected |
| `IntegrationDisconnected` | 1.0.0 | integrations | `user_id: int, integration_id: int, service_name: str, disconnection_reason: str, disconnection_timestamp: datetime` | External service disconnected |
| `ExternalDataReceived` | 1.0.0 | integrations | `user_id: int, integration_id: int, data_type: str, data_points_count: int, sync_timestamp: datetime, data_quality_score: float` | Data synced from external service |
| `DataSyncCompleted` | 1.0.0 | integrations | `user_id: int, integration_id: int, sync_job_id: str, records_processed: int, sync_duration_ms: int, success: bool` | Data synchronization job finished |
| `DataSyncFailed` | 1.0.0 | integrations | `user_id: int, integration_id: int, sync_job_id: str, error_code: str, error_message: str, retry_count: int` | Data synchronization failed |
| `AutoCompletionTriggered` | 1.0.0 | integrations | `user_id: int, quest_id: int, trigger_source: str, trigger_data: Dict[str, Any], completion_timestamp: datetime` | External data triggers quest completion |

## Analytics Events

| Event Name | Version | Owner Context | Payload Schema | Description |
|------------|---------|---------------|----------------|-------------|
| `BalanceScoreCalculated` | 1.0.0 | analytics | `user_id: int, health_score: float, wealth_score: float, relationships_score: float, overall_balance: float, calculation_timestamp: datetime` | Life balance metrics computed |
| `BalanceShiftDetected` | 1.0.0 | analytics | `user_id: int, shift_type: str, affected_areas: List[str], severity: str, shift_timestamp: datetime, recommended_actions: List[str]` | Significant life balance change detected |
| `PredictionGenerated` | 1.0.0 | analytics | `user_id: int, prediction_id: int, prediction_type: str, forecast_data: Dict[str, Any], confidence_interval: Tuple[float, float], prediction_horizon_days: int` | Predictive model generates forecast |
| `RecommendationCreated` | 1.0.0 | analytics | `user_id: int, recommendation_id: int, recommendation_type: str, action: str, priority: str, expected_impact: str, expiry_timestamp: datetime` | Personalized recommendation generated |
| `UserEngagementAnalyzed` | 1.0.0 | analytics | `user_id: int, analysis_period_days: int, engagement_score: float, activity_patterns: Dict[str, Any], risk_factors: List[str]` | User engagement patterns analyzed |

## Event Versioning Guidelines

### Version Format
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes to payload schema
- MINOR: Backward-compatible additions
- PATCH: Bug fixes, documentation updates

### Schema Evolution Rules
1. **Never remove required fields** from existing versions
2. **Always add new fields as optional** with default values
3. **Deprecate fields** before removing in next major version
4. **Maintain backward compatibility** for at least 2 major versions

### Event Handler Compatibility
- Handlers must specify minimum supported event version
- Event dispatcher routes events to compatible handlers only
- Unsupported versions trigger warning logs and fallback behavior

## Usage Examples

### Publishing Events
```python
from life_domain.events import EventPublisher, QuestCompleted

# Publish event with canonical schema
event = QuestCompleted(
    user_id=123,
    quest_id=456,
    quest_type="daily",
    experience_reward=50,
    completion_timestamp=datetime.utcnow(),
    auto_completed=False
)
EventPublisher.publish(event)
```

### Handling Events
```python
from life_domain.events import EventHandler, handles
from .catalog import QuestCompleted

@handles(QuestCompleted, min_version="1.0.0")
def award_quest_experience(event: QuestCompleted):
    # Handler implementation
    pass
```

### Event Serialization
```python
# All events must be JSON serializable
event_json = event.to_json()
event_restored = QuestCompleted.from_json(event_json)
```

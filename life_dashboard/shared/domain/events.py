"""
Canonical Domain Events System

This module implements the canonical domain event system as defined in the
Domain Events Catalog. All events follow the exact payload schemas and
versioning requirements specified in the catalog.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4


class BaseEvent:
    """
    Base class for all domain events.

    All events must inherit from this class and follow the canonical schema
    format with event_id, timestamp, and version fields.
    """

    def __init__(
        self,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        self.event_id = event_id or str(uuid4())
        self.timestamp = timestamp or datetime.utcnow()
        self.version = version

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            else:
                data[key] = value
        return data

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseEvent":
        """Create event instance from dictionary."""
        # Convert ISO timestamp back to datetime
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseEvent":
        """Create event instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Core System Events


@dataclass
class UserRegistered(BaseEvent):
    """User completes registration process - v1.0.0"""

    user_id: int
    email: str
    registration_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        email: str,
        registration_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.email = email
        self.registration_timestamp = registration_timestamp


@dataclass
class UserProfileUpdated(BaseEvent):
    """User profile information changed - v1.0.0"""

    user_id: int
    updated_fields: dict[str, Any]
    previous_values: dict[str, Any]

    def __init__(
        self,
        user_id: int,
        updated_fields: dict[str, Any],
        previous_values: dict[str, Any],
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.updated_fields = updated_fields
        self.previous_values = previous_values


@dataclass
class ExperienceAwarded(BaseEvent):
    """Experience points awarded to user - v1.0.0"""

    user_id: int
    experience_points: int
    source_type: str
    source_id: int
    reason: str

    def __init__(
        self,
        user_id: int,
        experience_points: int,
        source_type: str,
        source_id: int,
        reason: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.experience_points = experience_points
        self.source_type = source_type
        self.source_id = source_id
        self.reason = reason


@dataclass
class LevelUp(BaseEvent):
    """User reaches new level threshold - v1.0.0"""

    user_id: int
    previous_level: int
    new_level: int
    total_experience: int

    def __init__(
        self,
        user_id: int,
        previous_level: int,
        new_level: int,
        total_experience: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.previous_level = previous_level
        self.new_level = new_level
        self.total_experience = total_experience


# Stats Events


@dataclass
class CoreStatUpdated(BaseEvent):
    """Core RPG stat value changed - v1.0.0"""

    user_id: int
    stat_name: str
    previous_value: int
    new_value: int
    source: str

    def __init__(
        self,
        user_id: int,
        stat_name: str,
        previous_value: int,
        new_value: int,
        source: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.stat_name = stat_name
        self.previous_value = previous_value
        self.new_value = new_value
        self.source = source


@dataclass
class LifeStatUpdated(BaseEvent):
    """Life stat metric updated - v1.0.0"""

    user_id: int
    category: str
    subcategory: str
    previous_value: float
    new_value: float
    unit: str
    source: str

    def __init__(
        self,
        user_id: int,
        category: str,
        subcategory: str,
        previous_value: float,
        new_value: float,
        unit: str,
        source: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.category = category
        self.subcategory = subcategory
        self.previous_value = previous_value
        self.new_value = new_value
        self.unit = unit
        self.source = source


@dataclass
class StatMilestoneReached(BaseEvent):
    """Stat reaches significant milestone - v1.0.0"""

    user_id: int
    stat_type: str
    stat_name: str
    milestone_value: int
    milestone_type: str

    def __init__(
        self,
        user_id: int,
        stat_type: str,
        stat_name: str,
        milestone_value: int,
        milestone_type: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.stat_type = stat_type
        self.stat_name = stat_name
        self.milestone_value = milestone_value
        self.milestone_type = milestone_type


@dataclass
class TrendDetected(BaseEvent):
    """Statistical trend identified in stat data - v1.0.0"""

    user_id: int
    stat_name: str
    trend_type: str
    confidence_score: float
    duration_days: int

    def __init__(
        self,
        user_id: int,
        stat_name: str,
        trend_type: str,
        confidence_score: float,
        duration_days: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.stat_name = stat_name
        self.trend_type = trend_type
        self.confidence_score = confidence_score
        self.duration_days = duration_days


# Quest Events


@dataclass
class QuestCreated(BaseEvent):
    """New quest created by user - v1.0.0"""

    user_id: int
    quest_id: int
    quest_type: str
    title: str
    difficulty: str
    experience_reward: int

    def __init__(
        self,
        user_id: int,
        quest_id: int,
        quest_type: str,
        title: str,
        difficulty: str,
        experience_reward: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.quest_id = quest_id
        self.quest_type = quest_type
        self.title = title
        self.difficulty = difficulty
        self.experience_reward = experience_reward


@dataclass
class QuestCompleted(BaseEvent):
    """Quest marked as completed - v1.0.0"""

    user_id: int
    quest_id: int
    quest_type: str
    experience_reward: int
    completion_timestamp: datetime
    auto_completed: bool

    def __init__(
        self,
        user_id: int,
        quest_id: int,
        quest_type: str,
        experience_reward: int,
        completion_timestamp: datetime,
        auto_completed: bool,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.quest_id = quest_id
        self.quest_type = quest_type
        self.experience_reward = experience_reward
        self.completion_timestamp = completion_timestamp
        self.auto_completed = auto_completed


@dataclass
class QuestFailed(BaseEvent):
    """Quest marked as failed - v1.0.0"""

    user_id: int
    quest_id: int
    quest_type: str
    failure_reason: str
    failure_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        quest_id: int,
        quest_type: str,
        failure_reason: str,
        failure_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.quest_id = quest_id
        self.quest_type = quest_type
        self.failure_reason = failure_reason
        self.failure_timestamp = failure_timestamp


@dataclass
class QuestChainUnlocked(BaseEvent):
    """Quest completion unlocks new quests - v1.0.0"""

    user_id: int
    parent_quest_id: int
    unlocked_quest_ids: list[int]
    chain_name: str

    def __init__(
        self,
        user_id: int,
        parent_quest_id: int,
        unlocked_quest_ids: list[int],
        chain_name: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.parent_quest_id = parent_quest_id
        self.unlocked_quest_ids = unlocked_quest_ids
        self.chain_name = chain_name


@dataclass
class HabitCompleted(BaseEvent):
    """Habit instance completed - v1.0.0"""

    user_id: int
    habit_id: int
    completion_date: str  # ISO date format (date type not JSON serializable)
    streak_count: int
    experience_reward: int

    def __init__(
        self,
        user_id: int,
        habit_id: int,
        completion_date: str,
        streak_count: int,
        experience_reward: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.habit_id = habit_id
        self.completion_date = completion_date
        self.streak_count = streak_count
        self.experience_reward = experience_reward


@dataclass
class HabitStreakAchieved(BaseEvent):
    """Habit streak milestone reached - v1.0.0"""

    user_id: int
    habit_id: int
    streak_count: int
    streak_type: str
    bonus_experience: int

    def __init__(
        self,
        user_id: int,
        habit_id: int,
        streak_count: int,
        streak_type: str,
        bonus_experience: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.habit_id = habit_id
        self.streak_count = streak_count
        self.streak_type = streak_type
        self.bonus_experience = bonus_experience


@dataclass
class HabitStreakBroken(BaseEvent):
    """Habit streak interrupted - v1.0.0"""

    user_id: int
    habit_id: int
    previous_streak: int
    broken_date: str  # ISO date format (date type not JSON serializable)

    def __init__(
        self,
        user_id: int,
        habit_id: int,
        previous_streak: int,
        broken_date: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.habit_id = habit_id
        self.previous_streak = previous_streak
        self.broken_date = broken_date


# Skills Events


@dataclass
class SkillPracticed(BaseEvent):
    """User practices a skill - v1.0.0"""

    user_id: int
    skill_id: int
    practice_duration: int
    experience_gained: int
    practice_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        skill_id: int,
        practice_duration: int,
        experience_gained: int,
        practice_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.skill_id = skill_id
        self.practice_duration = practice_duration
        self.experience_gained = experience_gained
        self.practice_timestamp = practice_timestamp


@dataclass
class SkillLevelUp(BaseEvent):
    """Skill reaches new level - v1.0.0"""

    user_id: int
    skill_id: int
    previous_level: int
    new_level: int
    total_experience: int
    category: str

    def __init__(
        self,
        user_id: int,
        skill_id: int,
        previous_level: int,
        new_level: int,
        total_experience: int,
        category: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.skill_id = skill_id
        self.previous_level = previous_level
        self.new_level = new_level
        self.total_experience = total_experience
        self.category = category


@dataclass
class SkillMasteryAchieved(BaseEvent):
    """Skill reaches mastery threshold - v1.0.0"""

    user_id: int
    skill_id: int
    mastery_level: str
    total_practice_time: int
    mastery_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        skill_id: int,
        mastery_level: str,
        total_practice_time: int,
        mastery_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.skill_id = skill_id
        self.mastery_level = mastery_level
        self.total_practice_time = total_practice_time
        self.mastery_timestamp = mastery_timestamp


@dataclass
class SkillRecommendationGenerated(BaseEvent):
    """AI generates skill recommendations - v1.0.0"""

    user_id: int
    recommended_skill_ids: list[int]
    recommendation_reason: str
    confidence_score: float

    def __init__(
        self,
        user_id: int,
        recommended_skill_ids: list[int],
        recommendation_reason: str,
        confidence_score: float,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.recommended_skill_ids = recommended_skill_ids
        self.recommendation_reason = recommendation_reason
        self.confidence_score = confidence_score


# Achievement Events


@dataclass
class AchievementUnlocked(BaseEvent):
    """User unlocks achievement - v1.0.0"""

    user_id: int
    achievement_id: int
    achievement_name: str
    tier: str
    experience_reward: int
    unlock_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        achievement_id: int,
        achievement_name: str,
        tier: str,
        experience_reward: int,
        unlock_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.achievement_name = achievement_name
        self.tier = tier
        self.experience_reward = experience_reward
        self.unlock_timestamp = unlock_timestamp


@dataclass
class TitleUnlocked(BaseEvent):
    """User unlocks new title - v1.0.0"""

    user_id: int
    title_id: int
    title_name: str
    unlock_conditions: dict[str, Any]
    unlock_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        title_id: int,
        title_name: str,
        unlock_conditions: dict[str, Any],
        unlock_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.title_id = title_id
        self.title_name = title_name
        self.unlock_conditions = unlock_conditions
        self.unlock_timestamp = unlock_timestamp


@dataclass
class BadgeEarned(BaseEvent):
    """User earns badge - v1.0.0"""

    user_id: int
    badge_id: int
    badge_name: str
    badge_category: str
    earned_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        badge_id: int,
        badge_name: str,
        badge_category: str,
        earned_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.badge_id = badge_id
        self.badge_name = badge_name
        self.badge_category = badge_category
        self.earned_timestamp = earned_timestamp


@dataclass
class AchievementProgressUpdated(BaseEvent):
    """Progress toward achievement updated - v1.0.0"""

    user_id: int
    achievement_id: int
    current_progress: int
    required_progress: int
    progress_percentage: float

    def __init__(
        self,
        user_id: int,
        achievement_id: int,
        current_progress: int,
        required_progress: int,
        progress_percentage: float,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.current_progress = current_progress
        self.required_progress = required_progress
        self.progress_percentage = progress_percentage


# Journal Events


@dataclass
class JournalEntryCreated(BaseEvent):
    """New journal entry created - v1.0.0"""

    user_id: int
    entry_id: int
    entry_type: str
    title: str
    word_count: int
    mood_rating: int | None
    tags: list[str]

    def __init__(
        self,
        user_id: int,
        entry_id: int,
        entry_type: str,
        title: str,
        word_count: int,
        mood_rating: int | None,
        tags: list[str],
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.entry_id = entry_id
        self.entry_type = entry_type
        self.title = title
        self.word_count = word_count
        self.mood_rating = mood_rating
        self.tags = tags


@dataclass
class JournalEntryUpdated(BaseEvent):
    """Journal entry modified - v1.0.0"""

    user_id: int
    entry_id: int
    updated_fields: dict[str, Any]
    update_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        entry_id: int,
        updated_fields: dict[str, Any],
        update_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.entry_id = entry_id
        self.updated_fields = updated_fields
        self.update_timestamp = update_timestamp


@dataclass
class InsightGenerated(BaseEvent):
    """AI generates insight from journal data - v1.0.0"""

    user_id: int
    insight_id: int
    insight_type: str
    content: str
    confidence_score: float
    source_entries: list[int]

    def __init__(
        self,
        user_id: int,
        insight_id: int,
        insight_type: str,
        content: str,
        confidence_score: float,
        source_entries: list[int],
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.insight_id = insight_id
        self.insight_type = insight_type
        self.content = content
        self.confidence_score = confidence_score
        self.source_entries = source_entries


@dataclass
class PatternDetected(BaseEvent):
    """Behavioral pattern identified - v1.0.0"""

    user_id: int
    pattern_id: int
    pattern_type: str
    description: str
    confidence_score: float
    detection_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        pattern_id: int,
        pattern_type: str,
        description: str,
        confidence_score: float,
        detection_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type
        self.description = description
        self.confidence_score = confidence_score
        self.detection_timestamp = detection_timestamp


@dataclass
class ReflectionPromptSuggested(BaseEvent):
    """System suggests reflection topic - v1.0.0"""

    user_id: int
    prompt_id: int
    prompt_text: str
    prompt_category: str
    trigger_event: str

    def __init__(
        self,
        user_id: int,
        prompt_id: int,
        prompt_text: str,
        prompt_category: str,
        trigger_event: str,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.prompt_id = prompt_id
        self.prompt_text = prompt_text
        self.prompt_category = prompt_category
        self.trigger_event = trigger_event


# Integration Events


@dataclass
class IntegrationConnected(BaseEvent):
    """External service connected - v1.0.0"""

    user_id: int
    integration_id: int
    service_name: str
    integration_type: str
    connection_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        integration_id: int,
        service_name: str,
        integration_type: str,
        connection_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.integration_id = integration_id
        self.service_name = service_name
        self.integration_type = integration_type
        self.connection_timestamp = connection_timestamp


@dataclass
class IntegrationDisconnected(BaseEvent):
    """External service disconnected - v1.0.0"""

    user_id: int
    integration_id: int
    service_name: str
    disconnection_reason: str
    disconnection_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        integration_id: int,
        service_name: str,
        disconnection_reason: str,
        disconnection_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.integration_id = integration_id
        self.service_name = service_name
        self.disconnection_reason = disconnection_reason
        self.disconnection_timestamp = disconnection_timestamp


@dataclass
class ExternalDataReceived(BaseEvent):
    """Data synced from external service - v1.0.0"""

    user_id: int
    integration_id: int
    data_type: str
    data_points_count: int
    sync_timestamp: datetime
    data_quality_score: float

    def __init__(
        self,
        user_id: int,
        integration_id: int,
        data_type: str,
        data_points_count: int,
        sync_timestamp: datetime,
        data_quality_score: float,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.integration_id = integration_id
        self.data_type = data_type
        self.data_points_count = data_points_count
        self.sync_timestamp = sync_timestamp
        self.data_quality_score = data_quality_score


@dataclass
class DataSyncCompleted(BaseEvent):
    """Data synchronization job finished - v1.0.0"""

    user_id: int
    integration_id: int
    sync_job_id: str
    records_processed: int
    sync_duration_ms: int
    success: bool

    def __init__(
        self,
        user_id: int,
        integration_id: int,
        sync_job_id: str,
        records_processed: int,
        sync_duration_ms: int,
        success: bool,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.integration_id = integration_id
        self.sync_job_id = sync_job_id
        self.records_processed = records_processed
        self.sync_duration_ms = sync_duration_ms
        self.success = success


@dataclass
class DataSyncFailed(BaseEvent):
    """Data synchronization failed - v1.0.0"""

    user_id: int
    integration_id: int
    sync_job_id: str
    error_code: str
    error_message: str
    retry_count: int

    def __init__(
        self,
        user_id: int,
        integration_id: int,
        sync_job_id: str,
        error_code: str,
        error_message: str,
        retry_count: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.integration_id = integration_id
        self.sync_job_id = sync_job_id
        self.error_code = error_code
        self.error_message = error_message
        self.retry_count = retry_count


@dataclass
class AutoCompletionTriggered(BaseEvent):
    """External data triggers quest completion - v1.0.0"""

    user_id: int
    quest_id: int
    trigger_source: str
    trigger_data: dict[str, Any]
    completion_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        quest_id: int,
        trigger_source: str,
        trigger_data: dict[str, Any],
        completion_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.quest_id = quest_id
        self.trigger_source = trigger_source
        self.trigger_data = trigger_data
        self.completion_timestamp = completion_timestamp


# Analytics Events


@dataclass
class BalanceScoreCalculated(BaseEvent):
    """Life balance metrics computed - v1.0.0"""

    user_id: int
    health_score: float
    wealth_score: float
    relationships_score: float
    overall_balance: float
    calculation_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        health_score: float,
        wealth_score: float,
        relationships_score: float,
        overall_balance: float,
        calculation_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.health_score = health_score
        self.wealth_score = wealth_score
        self.relationships_score = relationships_score
        self.overall_balance = overall_balance
        self.calculation_timestamp = calculation_timestamp


@dataclass
class BalanceShiftDetected(BaseEvent):
    """Significant life balance change detected - v1.0.0"""

    user_id: int
    shift_type: str
    affected_areas: list[str]
    severity: str
    shift_timestamp: datetime
    recommended_actions: list[str]

    def __init__(
        self,
        user_id: int,
        shift_type: str,
        affected_areas: list[str],
        severity: str,
        shift_timestamp: datetime,
        recommended_actions: list[str],
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.shift_type = shift_type
        self.affected_areas = affected_areas
        self.severity = severity
        self.shift_timestamp = shift_timestamp
        self.recommended_actions = recommended_actions


@dataclass
class PredictionGenerated(BaseEvent):
    """Predictive model generates forecast - v1.0.0"""

    user_id: int
    prediction_id: int
    prediction_type: str
    forecast_data: dict[str, Any]
    confidence_interval: tuple[float, float]
    prediction_horizon_days: int

    def __init__(
        self,
        user_id: int,
        prediction_id: int,
        prediction_type: str,
        forecast_data: dict[str, Any],
        confidence_interval: tuple[float, float],
        prediction_horizon_days: int,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.prediction_id = prediction_id
        self.prediction_type = prediction_type
        self.forecast_data = forecast_data
        self.confidence_interval = confidence_interval
        self.prediction_horizon_days = prediction_horizon_days


@dataclass
class RecommendationCreated(BaseEvent):
    """Personalized recommendation generated - v1.0.0"""

    user_id: int
    recommendation_id: int
    recommendation_type: str
    action: str
    priority: str
    expected_impact: str
    expiry_timestamp: datetime

    def __init__(
        self,
        user_id: int,
        recommendation_id: int,
        recommendation_type: str,
        action: str,
        priority: str,
        expected_impact: str,
        expiry_timestamp: datetime,
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.recommendation_id = recommendation_id
        self.recommendation_type = recommendation_type
        self.action = action
        self.priority = priority
        self.expected_impact = expected_impact
        self.expiry_timestamp = expiry_timestamp


@dataclass
class UserEngagementAnalyzed(BaseEvent):
    """User engagement patterns analyzed - v1.0.0"""

    user_id: int
    analysis_period_days: int
    engagement_score: float
    activity_patterns: dict[str, Any]
    risk_factors: list[str]

    def __init__(
        self,
        user_id: int,
        analysis_period_days: int,
        engagement_score: float,
        activity_patterns: dict[str, Any],
        risk_factors: list[str],
        event_id: str | None = None,
        timestamp: datetime | None = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.user_id = user_id
        self.analysis_period_days = analysis_period_days
        self.engagement_score = engagement_score
        self.activity_patterns = activity_patterns
        self.risk_factors = risk_factors

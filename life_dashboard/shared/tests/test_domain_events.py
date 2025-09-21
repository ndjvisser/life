"""
Unit tests for the canonical domain event system.

Tests the BaseEvent class, event serialization/deserialization,
and all canonical events from the domain events catalog.
"""

import json
from datetime import datetime, timezone

from life_dashboard.shared.domain.events import (
    AchievementProgressUpdated,
    # Achievement Events
    AchievementUnlocked,
    AutoCompletionTriggered,
    BadgeEarned,
    # Analytics Events
    BalanceScoreCalculated,
    BalanceShiftDetected,
    BaseEvent,
    # Stats Events
    CoreStatUpdated,
    DataSyncCompleted,
    DataSyncFailed,
    ExperienceAwarded,
    ExternalDataReceived,
    HabitCompleted,
    HabitStreakAchieved,
    HabitStreakBroken,
    InsightGenerated,
    # Integration Events
    IntegrationConnected,
    IntegrationDisconnected,
    # Journal Events
    JournalEntryCreated,
    JournalEntryUpdated,
    LevelUp,
    LifeStatUpdated,
    PatternDetected,
    PredictionGenerated,
    QuestChainUnlocked,
    QuestCompleted,
    # Quest Events
    QuestCreated,
    QuestFailed,
    RecommendationCreated,
    ReflectionPromptSuggested,
    SkillLevelUp,
    SkillMasteryAchieved,
    # Skills Events
    SkillPracticed,
    SkillRecommendationGenerated,
    StatMilestoneReached,
    TitleUnlocked,
    TrendDetected,
    UserEngagementAnalyzed,
    UserProfileUpdated,
    # Core Events
    UserRegistered,
)


class TestEvent(BaseEvent):
    """Test event for base functionality testing."""

    def __init__(
        self,
        test_field: str = "test_value",
        event_id: str = None,
        timestamp: datetime = None,
        version: str = "1.0.0",
    ):
        super().__init__(event_id, timestamp, version)
        self.test_field = test_field


class TestBaseEvent:
    """Test the BaseEvent base class functionality."""

    def test_base_event_has_required_fields(self):
        """Test that BaseEvent has event_id, timestamp, and version."""
        event = TestEvent()

        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")
        assert hasattr(event, "version")
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.version == "1.0.0"

    def test_event_id_is_unique(self):
        """Test that each event gets a unique event_id."""
        event1 = TestEvent()
        event2 = TestEvent()

        assert event1.event_id != event2.event_id

    def test_timestamp_is_recent(self):
        """Test that timestamp is set to current time."""
        from datetime import timezone

        before = datetime.now(timezone.utc)
        event = TestEvent()
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after

    def test_to_dict_conversion(self):
        """Test event conversion to dictionary."""
        event = TestEvent(test_field="custom_value")
        data = event.to_dict()

        assert isinstance(data, dict)
        assert "event_id" in data
        assert "timestamp" in data
        assert "version" in data
        assert "test_field" in data
        assert data["test_field"] == "custom_value"
        assert data["version"] == "1.0.0"

        # Timestamp should be ISO format string
        assert isinstance(data["timestamp"], str)
        datetime.fromisoformat(data["timestamp"])  # Should not raise

    def test_to_json_serialization(self):
        """Test event JSON serialization."""
        event = TestEvent(test_field="json_test")
        json_str = event.to_json()

        assert isinstance(json_str, str)

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["test_field"] == "json_test"
        assert data["version"] == "1.0.0"

    def test_from_dict_deserialization(self):
        """Test event creation from dictionary."""
        original_event = TestEvent(test_field="dict_test")
        data = original_event.to_dict()

        restored_event = TestEvent.from_dict(data)

        assert restored_event.event_id == original_event.event_id
        assert restored_event.timestamp == original_event.timestamp
        assert restored_event.version == original_event.version
        assert restored_event.test_field == original_event.test_field

    def test_from_json_deserialization(self):
        """Test event creation from JSON string."""
        original_event = TestEvent(test_field="json_restore_test")
        json_str = original_event.to_json()

        restored_event = TestEvent.from_json(json_str)

        assert restored_event.event_id == original_event.event_id
        assert restored_event.timestamp == original_event.timestamp
        assert restored_event.version == original_event.version
        assert restored_event.test_field == original_event.test_field

    def test_round_trip_serialization(self):
        """Test complete serialization round trip."""
        original_event = TestEvent(test_field="round_trip_test")

        # Dict round trip
        dict_restored = TestEvent.from_dict(original_event.to_dict())
        assert dict_restored.event_id == original_event.event_id
        assert dict_restored.test_field == original_event.test_field

        # JSON round trip
        json_restored = TestEvent.from_json(original_event.to_json())
        assert json_restored.event_id == original_event.event_id
        assert json_restored.test_field == original_event.test_field


class TestCanonicalEvents:
    """Test canonical events from the domain events catalog."""

    def test_user_registered_event(self):
        """Test UserRegistered event schema."""
        event = UserRegistered(
            user_id=123,
            email="test@example.com",
            registration_timestamp=datetime.now(timezone.utc),
        )

        assert event.user_id == 123
        assert event.email == "test@example.com"
        assert event.version == "1.0.0"

        # Test serialization
        data = event.to_dict()
        assert data["user_id"] == 123
        assert data["email"] == "test@example.com"

        # Test deserialization
        restored = UserRegistered.from_dict(data)
        assert restored.user_id == 123
        assert restored.email == "test@example.com"

    def test_prediction_generated_confidence_interval_serialization(self):
        """PredictionGenerated serializes confidence interval as list."""

        event = PredictionGenerated(
            user_id=1,
            prediction_id=42,
            prediction_type="trend",
            forecast_data={"trend": "up"},
            confidence_interval=(0.2, 0.8),
            prediction_horizon_days=7,
        )

        assert isinstance(event.confidence_interval, list)
        assert event.confidence_interval == [0.2, 0.8]

        data = event.to_dict()
        assert isinstance(data["confidence_interval"], list)
        assert data["confidence_interval"] == [0.2, 0.8]

    def test_experience_awarded_event(self):
        """Test ExperienceAwarded event schema."""
        event = ExperienceAwarded(
            user_id=123,
            experience_points=50,
            source_type="quest",
            source_id=456,
            reason="Quest completion",
        )

        assert event.user_id == 123
        assert event.experience_points == 50
        assert event.source_type == "quest"
        assert event.source_id == 456
        assert event.reason == "Quest completion"
        assert event.version == "1.0.0"

    def test_quest_completed_event(self):
        """Test QuestCompleted event schema."""
        completion_time = datetime.now(timezone.utc)
        event = QuestCompleted(
            user_id=123,
            quest_id=456,
            quest_type="daily",
            experience_reward=25,
            completion_timestamp=completion_time,
            auto_completed=False,
        )

        assert event.user_id == 123
        assert event.quest_id == 456
        assert event.quest_type == "daily"
        assert event.experience_reward == 25
        assert event.completion_timestamp == completion_time
        assert event.auto_completed is False
        assert event.version == "1.0.0"

    def test_skill_level_up_event(self):
        """Test SkillLevelUp event schema."""
        event = SkillLevelUp(
            user_id=123,
            skill_id=789,
            previous_level=2,
            new_level=3,
            total_experience=1500,
            category="health",
        )

        assert event.user_id == 123
        assert event.skill_id == 789
        assert event.previous_level == 2
        assert event.new_level == 3
        assert event.total_experience == 1500
        assert event.category == "health"
        assert event.version == "1.0.0"

    def test_achievement_unlocked_event(self):
        """Test AchievementUnlocked event schema."""
        unlock_time = datetime.now(timezone.utc)
        event = AchievementUnlocked(
            user_id=123,
            achievement_id=456,
            achievement_name="First Quest",
            tier="bronze",
            experience_reward=100,
            unlock_timestamp=unlock_time,
        )

        assert event.user_id == 123
        assert event.achievement_id == 456
        assert event.achievement_name == "First Quest"
        assert event.tier == "bronze"
        assert event.experience_reward == 100
        assert event.unlock_timestamp == unlock_time
        assert event.version == "1.0.0"

    def test_journal_entry_created_event(self):
        """Test JournalEntryCreated event schema."""
        event = JournalEntryCreated(
            user_id=123,
            entry_id=456,
            entry_type="daily",
            title="My Daily Reflection",
            word_count=250,
            mood_rating=8,
            tags=["reflection", "growth"],
        )

        assert event.user_id == 123
        assert event.entry_id == 456
        assert event.entry_type == "daily"
        assert event.title == "My Daily Reflection"
        assert event.word_count == 250
        assert event.mood_rating == 8
        assert event.tags == ["reflection", "growth"]
        assert event.version == "1.0.0"

    def test_external_data_received_event(self):
        """Test ExternalDataReceived event schema."""
        sync_time = datetime.now(timezone.utc)
        event = ExternalDataReceived(
            user_id=123,
            integration_id=456,
            data_type="workout",
            data_points_count=5,
            sync_timestamp=sync_time,
            data_quality_score=0.95,
        )

        assert event.user_id == 123
        assert event.integration_id == 456
        assert event.data_type == "workout"
        assert event.data_points_count == 5
        assert event.sync_timestamp == sync_time
        assert event.data_quality_score == 0.95
        assert event.version == "1.0.0"

    def test_balance_score_calculated_event(self):
        """Test BalanceScoreCalculated event schema."""
        calc_time = datetime.now(timezone.utc)
        event = BalanceScoreCalculated(
            user_id=123,
            health_score=0.8,
            wealth_score=0.6,
            relationships_score=0.7,
            overall_balance=0.7,
            calculation_timestamp=calc_time,
        )

        assert event.user_id == 123
        assert event.health_score == 0.8
        assert event.wealth_score == 0.6
        assert event.relationships_score == 0.7
        assert event.overall_balance == 0.7
        assert event.calculation_timestamp == calc_time
        assert event.version == "1.0.0"

    def test_all_events_have_version(self):
        """Test that all canonical events have version field."""
        now = datetime.now(timezone.utc)
        events_to_test = [
            # Core Events
            UserRegistered(
                user_id=1, email="test@example.com", registration_timestamp=now
            ),
            UserProfileUpdated(
                user_id=1,
                updated_fields={"name": "test"},
                previous_values={"name": "old"},
            ),
            ExperienceAwarded(
                user_id=1,
                experience_points=50,
                source_type="test",
                source_id=1,
                reason="test",
            ),
            LevelUp(user_id=1, previous_level=1, new_level=2, total_experience=1000),
            # Stats Events
            CoreStatUpdated(
                user_id=1,
                stat_name="strength",
                previous_value=10,
                new_value=11,
                source="manual",
            ),
            LifeStatUpdated(
                user_id=1,
                category="health",
                subcategory="physical",
                previous_value=5.0,
                new_value=6.0,
                unit="points",
                source="manual",
            ),
            StatMilestoneReached(
                user_id=1,
                stat_type="core",
                stat_name="strength",
                milestone_value=20,
                milestone_type="level",
            ),
            TrendDetected(
                user_id=1,
                stat_name="strength",
                trend_type="increasing",
                confidence_score=0.8,
                duration_days=7,
            ),
            # Quest Events
            QuestCreated(
                user_id=1,
                quest_id=1,
                quest_type="daily",
                title="Test Quest",
                difficulty="easy",
                experience_reward=25,
            ),
            QuestCompleted(
                user_id=1,
                quest_id=1,
                quest_type="daily",
                experience_reward=25,
                completion_timestamp=now,
                auto_completed=False,
            ),
            QuestFailed(
                user_id=1,
                quest_id=1,
                quest_type="daily",
                failure_reason="timeout",
                failure_timestamp=now,
            ),
            QuestChainUnlocked(
                user_id=1,
                parent_quest_id=1,
                unlocked_quest_ids=[2, 3],
                chain_name="Test Chain",
            ),
            HabitCompleted(
                user_id=1,
                habit_id=1,
                completion_date="2024-01-01",
                streak_count=5,
                experience_reward=10,
            ),
            HabitStreakAchieved(
                user_id=1,
                habit_id=1,
                streak_count=7,
                streak_type="weekly",
                bonus_experience=20,
            ),
            HabitStreakBroken(
                user_id=1, habit_id=1, previous_streak=10, broken_date="2024-01-02"
            ),
            # Skills Events
            SkillPracticed(
                user_id=1,
                skill_id=1,
                practice_duration=30,
                experience_gained=15,
                practice_timestamp=now,
            ),
            SkillLevelUp(
                user_id=1,
                skill_id=1,
                previous_level=1,
                new_level=2,
                total_experience=1000,
                category="health",
            ),
            SkillMasteryAchieved(
                user_id=1,
                skill_id=1,
                mastery_level="expert",
                total_practice_time=10000,
                mastery_timestamp=now,
            ),
            SkillRecommendationGenerated(
                user_id=1,
                recommended_skill_ids=[1, 2],
                recommendation_reason="based on activity",
                confidence_score=0.9,
            ),
            # Achievement Events
            AchievementUnlocked(
                user_id=1,
                achievement_id=1,
                achievement_name="First Steps",
                tier="bronze",
                experience_reward=100,
                unlock_timestamp=now,
            ),
            TitleUnlocked(
                user_id=1,
                title_id=1,
                title_name="Beginner",
                unlock_conditions={"level": 1},
                unlock_timestamp=now,
            ),
            BadgeEarned(
                user_id=1,
                badge_id=1,
                badge_name="Early Bird",
                badge_category="habits",
                earned_timestamp=now,
            ),
            AchievementProgressUpdated(
                user_id=1,
                achievement_id=1,
                current_progress=5,
                required_progress=10,
                progress_percentage=50.0,
            ),
            # Journal Events
            JournalEntryCreated(
                user_id=1,
                entry_id=1,
                entry_type="daily",
                title="Test Entry",
                word_count=100,
                mood_rating=5,
                tags=["test"],
            ),
            JournalEntryUpdated(
                user_id=1,
                entry_id=1,
                updated_fields={"title": "Updated"},
                update_timestamp=now,
            ),
            InsightGenerated(
                user_id=1,
                insight_id=1,
                insight_type="pattern",
                content="Test insight",
                confidence_score=0.8,
                source_entries=[1, 2],
            ),
            PatternDetected(
                user_id=1,
                pattern_id=1,
                pattern_type="behavioral",
                description="Test pattern",
                confidence_score=0.7,
                detection_timestamp=now,
            ),
            ReflectionPromptSuggested(
                user_id=1,
                prompt_id=1,
                prompt_text="How are you feeling?",
                prompt_category="mood",
                trigger_event="low_mood",
            ),
            # Integration Events
            IntegrationConnected(
                user_id=1,
                integration_id=1,
                service_name="Strava",
                integration_type="health",
                connection_timestamp=now,
            ),
            IntegrationDisconnected(
                user_id=1,
                integration_id=1,
                service_name="Strava",
                disconnection_reason="user_request",
                disconnection_timestamp=now,
            ),
            ExternalDataReceived(
                user_id=1,
                integration_id=1,
                data_type="workout",
                data_points_count=1,
                sync_timestamp=now,
                data_quality_score=1.0,
            ),
            DataSyncCompleted(
                user_id=1,
                integration_id=1,
                sync_job_id="job123",
                records_processed=10,
                sync_duration_ms=1000,
                success=True,
            ),
            DataSyncFailed(
                user_id=1,
                integration_id=1,
                sync_job_id="job124",
                error_code="API_ERROR",
                error_message="Rate limited",
                retry_count=1,
            ),
            AutoCompletionTriggered(
                user_id=1,
                quest_id=1,
                trigger_source="strava",
                trigger_data={"workout": "run"},
                completion_timestamp=now,
            ),
            # Analytics Events
            BalanceScoreCalculated(
                user_id=1,
                health_score=0.8,
                wealth_score=0.6,
                relationships_score=0.7,
                overall_balance=0.7,
                calculation_timestamp=now,
            ),
            BalanceShiftDetected(
                user_id=1,
                shift_type="decline",
                affected_areas=["health"],
                severity="moderate",
                shift_timestamp=now,
                recommended_actions=["exercise"],
            ),
            PredictionGenerated(
                user_id=1,
                prediction_id=1,
                prediction_type="trend",
                forecast_data={"trend": "up"},
                confidence_interval=(0.6, 0.9),
                prediction_horizon_days=30,
            ),
            RecommendationCreated(
                user_id=1,
                recommendation_id=1,
                recommendation_type="habit",
                action="exercise",
                priority="high",
                expected_impact="positive",
                expiry_timestamp=now,
            ),
            UserEngagementAnalyzed(
                user_id=1,
                analysis_period_days=30,
                engagement_score=0.8,
                activity_patterns={"daily": True},
                risk_factors=["low_activity"],
            ),
        ]

        for event in events_to_test:
            assert hasattr(event, "version")
            assert event.version == "1.0.0"

    def test_all_events_serializable(self):
        """Test that all canonical events can be serialized and deserialized."""
        now = datetime.now(timezone.utc)
        # Test a representative sample of events (not all to keep test fast)
        events_to_test = [
            UserRegistered(
                user_id=1, email="test@example.com", registration_timestamp=now
            ),
            ExperienceAwarded(
                user_id=1,
                experience_points=50,
                source_type="test",
                source_id=1,
                reason="test",
            ),
            QuestCompleted(
                user_id=1,
                quest_id=1,
                quest_type="test",
                experience_reward=25,
                completion_timestamp=now,
                auto_completed=False,
            ),
            SkillLevelUp(
                user_id=1,
                skill_id=1,
                previous_level=1,
                new_level=2,
                total_experience=1000,
                category="test",
            ),
            AchievementUnlocked(
                user_id=1,
                achievement_id=1,
                achievement_name="test",
                tier="bronze",
                experience_reward=100,
                unlock_timestamp=now,
            ),
            JournalEntryCreated(
                user_id=1,
                entry_id=1,
                entry_type="daily",
                title="test",
                word_count=100,
                mood_rating=5,
                tags=["test"],
            ),
            ExternalDataReceived(
                user_id=1,
                integration_id=1,
                data_type="test",
                data_points_count=1,
                sync_timestamp=now,
                data_quality_score=1.0,
            ),
            BalanceScoreCalculated(
                user_id=1,
                health_score=0.5,
                wealth_score=0.5,
                relationships_score=0.5,
                overall_balance=0.5,
                calculation_timestamp=now,
            ),
            # Test some of the new events
            StatMilestoneReached(
                user_id=1,
                stat_type="core",
                stat_name="strength",
                milestone_value=20,
                milestone_type="level",
            ),
            HabitStreakAchieved(
                user_id=1,
                habit_id=1,
                streak_count=7,
                streak_type="weekly",
                bonus_experience=20,
            ),
            PatternDetected(
                user_id=1,
                pattern_id=1,
                pattern_type="behavioral",
                description="Test pattern",
                confidence_score=0.7,
                detection_timestamp=now,
            ),
            PredictionGenerated(
                user_id=1,
                prediction_id=1,
                prediction_type="trend",
                forecast_data={"trend": "up"},
                confidence_interval=(0.6, 0.9),
                prediction_horizon_days=30,
            ),
        ]

        for event in events_to_test:
            # Test JSON serialization
            json_str = event.to_json()
            assert isinstance(json_str, str)

            # Test JSON is valid
            json.loads(json_str)  # Should not raise

            # Test dict serialization
            data = event.to_dict()
            assert isinstance(data, dict)
            assert "event_id" in data
            assert "timestamp" in data
            assert "version" in data

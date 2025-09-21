"""
Verification script to ensure all canonical events from the Domain Events Catalog are implemented.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import inspect

from domain import events


def get_all_event_classes():
    """Get all event classes from the events module."""
    event_classes = []
    for name, obj in inspect.getmembers(events):
        if (
            inspect.isclass(obj)
            and issubclass(obj, events.BaseEvent)
            and obj != events.BaseEvent
        ):
            event_classes.append(name)
    return sorted(event_classes)


def main():
    """Verify all canonical events are implemented."""
    print("=== Canonical Domain Events Verification ===\n")

    # Expected events from the Domain Events Catalog
    expected_events = {
        # Core Events (4)
        "UserRegistered",
        "UserProfileUpdated",
        "ExperienceAwarded",
        "LevelUp",
        # Stats Events (4)
        "CoreStatUpdated",
        "LifeStatUpdated",
        "StatMilestoneReached",
        "TrendDetected",
        # Quest Events (7)
        "QuestCreated",
        "QuestCompleted",
        "QuestFailed",
        "QuestChainUnlocked",
        "HabitCompleted",
        "HabitStreakAchieved",
        "HabitStreakBroken",
        # Skills Events (4)
        "SkillPracticed",
        "SkillLevelUp",
        "SkillMasteryAchieved",
        "SkillRecommendationGenerated",
        # Achievement Events (4)
        "AchievementUnlocked",
        "TitleUnlocked",
        "BadgeEarned",
        "AchievementProgressUpdated",
        # Journal Events (5)
        "JournalEntryCreated",
        "JournalEntryUpdated",
        "InsightGenerated",
        "PatternDetected",
        "ReflectionPromptSuggested",
        # Integration Events (6)
        "IntegrationConnected",
        "IntegrationDisconnected",
        "ExternalDataReceived",
        "DataSyncCompleted",
        "DataSyncFailed",
        "AutoCompletionTriggered",
        # Analytics Events (5)
        "BalanceScoreCalculated",
        "BalanceShiftDetected",
        "PredictionGenerated",
        "RecommendationCreated",
        "UserEngagementAnalyzed",
    }

    # Get implemented events
    implemented_events = set(get_all_event_classes())

    print(f"📊 Expected events: {len(expected_events)}")
    print(f"✅ Implemented events: {len(implemented_events)}")

    # Check for missing events
    missing_events = expected_events - implemented_events
    if missing_events:
        print(f"\n❌ Missing events ({len(missing_events)}):")
        for event in sorted(missing_events):
            print(f"  - {event}")
    else:
        print("\n✅ All expected events are implemented!")

    # Check for extra events (not in catalog)
    extra_events = implemented_events - expected_events
    if extra_events:
        print(f"\n⚠️  Extra events not in catalog ({len(extra_events)}):")
        for event in sorted(extra_events):
            print(f"  - {event}")

    # Summary by category
    print("\n📋 Events by category:")
    categories = {
        "Core": [
            "UserRegistered",
            "UserProfileUpdated",
            "ExperienceAwarded",
            "LevelUp",
        ],
        "Stats": [
            "CoreStatUpdated",
            "LifeStatUpdated",
            "StatMilestoneReached",
            "TrendDetected",
        ],
        "Quest": [
            "QuestCreated",
            "QuestCompleted",
            "QuestFailed",
            "QuestChainUnlocked",
            "HabitCompleted",
            "HabitStreakAchieved",
            "HabitStreakBroken",
        ],
        "Skills": [
            "SkillPracticed",
            "SkillLevelUp",
            "SkillMasteryAchieved",
            "SkillRecommendationGenerated",
        ],
        "Achievement": [
            "AchievementUnlocked",
            "TitleUnlocked",
            "BadgeEarned",
            "AchievementProgressUpdated",
        ],
        "Journal": [
            "JournalEntryCreated",
            "JournalEntryUpdated",
            "InsightGenerated",
            "PatternDetected",
            "ReflectionPromptSuggested",
        ],
        "Integration": [
            "IntegrationConnected",
            "IntegrationDisconnected",
            "ExternalDataReceived",
            "DataSyncCompleted",
            "DataSyncFailed",
            "AutoCompletionTriggered",
        ],
        "Analytics": [
            "BalanceScoreCalculated",
            "BalanceShiftDetected",
            "PredictionGenerated",
            "RecommendationCreated",
            "UserEngagementAnalyzed",
        ],
    }

    for category, events_list in categories.items():
        implemented_in_category = [e for e in events_list if e in implemented_events]
        print(f"  {category}: {len(implemented_in_category)}/{len(events_list)} ✅")

    print(
        f"\n🎉 Total: {len(implemented_events)}/{len(expected_events)} canonical events implemented!"
    )

    if len(implemented_events) == len(expected_events) and not missing_events:
        print("\n✅ SUCCESS: All canonical domain events are fully implemented!")
        return True
    else:
        print("\n❌ INCOMPLETE: Some events are missing or extra.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

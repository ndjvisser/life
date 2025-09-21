"""
Domain Event System Demo

This example demonstrates how to use the canonical domain event system
with event handlers, version compatibility, and privacy-aware processing.
"""

import os
import sys
from datetime import datetime, timezone

# Add the parent directory to the path so we can import from shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.event_dispatcher import get_event_dispatcher, handles, publish_event
from domain.events import AchievementUnlocked, ExperienceAwarded, QuestCompleted

# Example event handlers using the @handles decorator


@handles(QuestCompleted, min_version="1.0.0")
def award_experience_for_quest(event: QuestCompleted):
    """Award experience points when a quest is completed."""
    print(
        f"🎯 Quest completed! Awarding {event.experience_reward} XP to user {event.user_id}"
    )

    # Create and publish an ExperienceAwarded event
    exp_event = ExperienceAwarded(
        user_id=event.user_id,
        experience_points=event.experience_reward,
        source_type="quest",
        source_id=event.quest_id,
        reason=f"Completed {event.quest_type} quest",
    )
    publish_event(exp_event)


@handles(QuestCompleted, min_version="1.0.0")
def check_achievements_on_quest_completion(event: QuestCompleted):
    """Check if quest completion unlocks any achievements."""
    print(
        f"🏆 Checking achievements for user {event.user_id} after quest completion..."
    )

    # Simple achievement logic - unlock "First Quest" achievement
    if event.quest_type == "daily":
        achievement_event = AchievementUnlocked(
            user_id=event.user_id,
            achievement_id=1,
            achievement_name="Daily Warrior",
            tier="bronze",
            experience_reward=50,
            unlock_timestamp=datetime.now(timezone.utc),
        )
        publish_event(achievement_event)


@handles(ExperienceAwarded, min_version="1.0.0")
def log_experience_gain(event: ExperienceAwarded):
    """Log experience gains for analytics."""
    print(
        f"📊 User {event.user_id} gained {event.experience_points} XP from {event.source_type}"
    )


@handles(AchievementUnlocked, min_version="1.0.0")
def celebrate_achievement(event: AchievementUnlocked):
    """Celebrate when achievements are unlocked."""
    print(
        f"🎉 ACHIEVEMENT UNLOCKED! User {event.user_id} earned '{event.achievement_name}' ({event.tier})"
    )


def demo_event_system():
    """Demonstrate the domain event system in action."""
    print("=== Domain Event System Demo ===\n")

    # Show registered handlers
    dispatcher = get_event_dispatcher()
    quest_handlers = dispatcher.get_handlers(QuestCompleted)
    print(f"📋 Registered {len(quest_handlers)} handlers for QuestCompleted events:")
    for handler in quest_handlers:
        print(f"  - {handler.handler_name} (v{handler.min_version}+)")
    print()

    # Create and publish a quest completion event
    print("🚀 Publishing QuestCompleted event...\n")

    quest_event = QuestCompleted(
        user_id=123,
        quest_id=456,
        quest_type="daily",
        experience_reward=25,
        completion_timestamp=datetime.now(timezone.utc),
        auto_completed=False,
    )

    # This will trigger all the registered handlers
    publish_event(quest_event)

    print("\n=== Event Log ===")
    event_log = dispatcher.get_event_log()
    print(f"📝 {len(event_log)} events were published:")
    for i, event in enumerate(event_log, 1):
        print(
            f"  {i}. {type(event).__name__} (v{event.version}) - {event.event_id[:8]}..."
        )

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_event_system()

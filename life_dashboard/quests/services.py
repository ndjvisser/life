"""
Quests service factory - dependency injection and service wiring.
"""

from .application.services import HabitService, QuestChainService, QuestService
from .infrastructure.repositories import (
    DjangoHabitCompletionRepository,
    DjangoHabitRepository,
    DjangoQuestRepository,
)


class QuestsServiceFactory:
    """Factory for creating configured quests service instances."""

    _quest_repo = None
    _habit_repo = None
    _completion_repo = None

    @classmethod
    def get_quest_repository(cls):
        """Get or create quest repository instance."""
        if cls._quest_repo is None:
            cls._quest_repo = DjangoQuestRepository()
        return cls._quest_repo

    @classmethod
    def get_habit_repository(cls):
        """Get or create habit repository instance."""
        if cls._habit_repo is None:
            cls._habit_repo = DjangoHabitRepository()
        return cls._habit_repo

    @classmethod
    def get_completion_repository(cls):
        """Get or create completion repository instance."""
        if cls._completion_repo is None:
            cls._completion_repo = DjangoHabitCompletionRepository()
        return cls._completion_repo

    @classmethod
    def get_quest_service(cls):
        """Get configured QuestService instance."""
        return QuestService(quest_repo=cls.get_quest_repository())

    @classmethod
    def get_habit_service(cls):
        """Get configured HabitService instance."""
        return HabitService(
            habit_repo=cls.get_habit_repository(),
            completion_repo=cls.get_completion_repository(),
        )

    @classmethod
    def get_quest_chain_service(cls):
        """Get configured QuestChainService instance."""
        return QuestChainService(quest_repo=cls.get_quest_repository())


# Convenience functions for getting services
def get_quest_service() -> QuestService:
    """Get QuestService instance."""
    return QuestsServiceFactory.get_quest_service()


def get_habit_service() -> HabitService:
    """Get HabitService instance."""
    return QuestsServiceFactory.get_habit_service()


def get_quest_chain_service() -> QuestChainService:
    """Get QuestChainService instance."""
    return QuestsServiceFactory.get_quest_chain_service()

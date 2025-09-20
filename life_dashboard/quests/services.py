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
        """
        Return a cached DjangoQuestRepository instance, creating and storing it on the class on first call.
        
        Creates a new DjangoQuestRepository if one has not been created yet and assigns it to the class attribute used for caching, then returns the repository instance.
        
        Returns:
            DjangoQuestRepository: The cached or newly created quest repository.
        """
        if cls._quest_repo is None:
            cls._quest_repo = DjangoQuestRepository()
        return cls._quest_repo

    @classmethod
    def get_habit_repository(cls):
        """
        Return a cached DjangoHabitRepository instance, creating and caching it on first call.
        
        This performs lazy initialization: if the class-level cache is empty, a new
        DjangoHabitRepository is constructed and stored on the class before being returned.
        
        Returns:
            DjangoHabitRepository: The cached habit repository instance.
        """
        if cls._habit_repo is None:
            cls._habit_repo = DjangoHabitRepository()
        return cls._habit_repo

    @classmethod
    def get_completion_repository(cls):
        """
        Return the cached DjangoHabitCompletionRepository, creating it if necessary.
        
        Lazily instantiates and stores a DjangoHabitCompletionRepository on the class (cls._completion_repo) on first call and returns the cached instance on subsequent calls.
        
        Returns:
            DjangoHabitCompletionRepository: the repository instance for habit completions.
        """
        if cls._completion_repo is None:
            cls._completion_repo = DjangoHabitCompletionRepository()
        return cls._completion_repo

    @classmethod
    def get_quest_service(cls):
        """
        Return a QuestService configured with the factory's quest repository.
        
        The quest repository is created lazily and cached on the factory; this method constructs
        a QuestService using that repository and returns the configured service instance.
        
        Returns:
            QuestService: A service instance wired with the factory's quest repository.
        """
        return QuestService(quest_repo=cls.get_quest_repository())

    @classmethod
    def get_habit_service(cls):
        """
        Return a configured HabitService instance.
        
        The returned service is constructed with the factory's habit repository and habit completion repository, lazily created/cached by the factory.
        
        Returns:
            HabitService: HabitService wired with the factory's habit_repo and completion_repo.
        """
        return HabitService(
            habit_repo=cls.get_habit_repository(),
            completion_repo=cls.get_completion_repository(),
        )

    @classmethod
    def get_quest_chain_service(cls):
        """
        Return a configured QuestChainService instance.
        
        Constructs the service using the factory's quest repository (lazily created and cached) and returns it.
        
        Returns:
            QuestChainService: a ready-to-use QuestChainService wired with the factory's quest repository.
        """
        return QuestChainService(quest_repo=cls.get_quest_repository())


# Convenience functions for getting services
def get_quest_service() -> QuestService:
    """
    Return a configured QuestService instance.
    
    This is a convenience wrapper that delegates to QuestsServiceFactory.get_quest_service()
    and returns a QuestService configured with the module's quest repository.
    
    Returns:
        QuestService: A ready-to-use QuestService instance.
    """
    return QuestsServiceFactory.get_quest_service()


def get_habit_service() -> HabitService:
    """
    Return a configured HabitService instance.
    
    This is a convenience wrapper that delegates to QuestsServiceFactory.get_habit_service(),
    which lazily constructs and caches the underlying repositories and returns a HabitService
    wired with the appropriate dependencies.
    
    Returns:
        HabitService: A ready-to-use HabitService configured with the application's repositories.
    """
    return QuestsServiceFactory.get_habit_service()


def get_quest_chain_service() -> QuestChainService:
    """Get QuestChainService instance."""
    return QuestsServiceFactory.get_quest_chain_service()

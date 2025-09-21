"""
Stats service factory - dependency injection and service wiring.
"""

from .application.services import LifeStatService, StatAnalyticsService, StatService
from .infrastructure.repositories import (
    DjangoCoreStatRepository,
    DjangoLifeStatRepository,
    DjangoStatHistoryRepository,
)


class StatsServiceFactory:
    """Factory for creating configured stats service instances."""

    _core_stat_repo = None
    _life_stat_repo = None
    _history_repo = None

    @classmethod
    def get_core_stat_repository(cls):
        """
        Return the cached DjangoCoreStatRepository instance, creating and caching it on first access.

        This performs lazy initialization: if the class-level cache `_core_stat_repo` is None, a new
        DjangoCoreStatRepository is instantiated and stored on the class before being returned.

        Returns:
            DjangoCoreStatRepository: The singleton repository instance for core stats associated with this factory class.
        """
        if cls._core_stat_repo is None:
            cls._core_stat_repo = DjangoCoreStatRepository()
        return cls._core_stat_repo

    @classmethod
    def get_life_stat_repository(cls):
        """
        Return a lazily-instantiated singleton DjangoLifeStatRepository.

        On first call this creates and caches a DjangoLifeStatRepository instance on the class;
        subsequent calls return the cached repository.
        """
        if cls._life_stat_repo is None:
            cls._life_stat_repo = DjangoLifeStatRepository()
        return cls._life_stat_repo

    @classmethod
    def get_history_repository(cls):
        """
        Return the lazily initialized, shared DjangoStatHistoryRepository for the class.

        Creates and caches a new DjangoStatHistoryRepository on first call and returns the cached instance on subsequent calls.

        Returns:
            DjangoStatHistoryRepository: The class-cached history repository instance.
        """
        if cls._history_repo is None:
            cls._history_repo = DjangoStatHistoryRepository()
        return cls._history_repo

    @classmethod
    def get_stat_service(cls):
        """
        Return a configured StatService wired with the factory's repositories.

        The returned StatService is constructed with the factory's cached core stat repository
        (from get_core_stat_repository()) and history repository (from get_history_repository()).

        Returns:
            StatService: a ready-to-use StatService instance.
        """
        return StatService(
            core_stat_repo=cls.get_core_stat_repository(),
            life_stat_repo=cls.get_life_stat_repository(),
            history_repo=cls.get_history_repository(),
        )

    @classmethod
    def get_life_stat_service(cls):
        """
        Return a configured LifeStatService with the factory's repository dependencies.

        Creates and returns a LifeStatService instance wired with the factory's cached
        DjangoLifeStatRepository (life_stat_repo) and DjangoStatHistoryRepository
        (history_repo). Repositories are lazily instantiated and cached by the factory.

        Returns:
            LifeStatService: A LifeStatService configured with the appropriate repositories.
        """
        return LifeStatService(
            life_stat_repo=cls.get_life_stat_repository(),
            history_repo=cls.get_history_repository(),
        )

    @classmethod
    def get_analytics_service(cls):
        """
        Return a configured StatAnalyticsService wired with the factory's cached history repository.

        This classmethod constructs and returns a StatAnalyticsService using the
        factory's cached DjangoStatHistoryRepository as the `history_repo` dependency.

        Returns:
            StatAnalyticsService: A ready-to-use analytics service instance.
        """
        return StatAnalyticsService(history_repo=cls.get_history_repository())


# Convenience functions for getting services
def get_stat_service() -> StatService:
    """Get StatService instance."""
    return StatsServiceFactory.get_stat_service()


def get_life_stat_service() -> LifeStatService:
    """
    Return a pre-configured LifeStatService instance wired with the module's repositories.

    This is a convenience wrapper around StatsServiceFactory.get_life_stat_service()
    that provides a lazily-instantiated, dependency-injected LifeStatService ready for use.

    Returns:
        LifeStatService: A LifeStatService configured with the module's LifeStatRepository and StatHistoryRepository.
    """
    return StatsServiceFactory.get_life_stat_service()


def get_analytics_service() -> StatAnalyticsService:
    """Get StatAnalyticsService instance."""
    return StatsServiceFactory.get_analytics_service()

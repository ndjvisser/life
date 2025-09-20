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
        """Get or create core stat repository instance."""
        if cls._core_stat_repo is None:
            cls._core_stat_repo = DjangoCoreStatRepository()
        return cls._core_stat_repo

    @classmethod
    def get_life_stat_repository(cls):
        """Get or create life stat repository instance."""
        if cls._life_stat_repo is None:
            cls._life_stat_repo = DjangoLifeStatRepository()
        return cls._life_stat_repo

    @classmethod
    def get_history_repository(cls):
        """Get or create history repository instance."""
        if cls._history_repo is None:
            cls._history_repo = DjangoStatHistoryRepository()
        return cls._history_repo

    @classmethod
    def get_stat_service(cls):
        """Get configured StatService instance."""
        return StatService(
            core_stat_repo=cls.get_core_stat_repository(),
            history_repo=cls.get_history_repository(),
        )

    @classmethod
    def get_life_stat_service(cls):
        """Get configured LifeStatService instance."""
        return LifeStatService(
            life_stat_repo=cls.get_life_stat_repository(),
            history_repo=cls.get_history_repository(),
        )

    @classmethod
    def get_analytics_service(cls):
        """Get configured StatAnalyticsService instance."""
        return StatAnalyticsService(history_repo=cls.get_history_repository())


# Convenience functions for getting services
def get_stat_service() -> StatService:
    """Get StatService instance."""
    return StatsServiceFactory.get_stat_service()


def get_life_stat_service() -> LifeStatService:
    """Get LifeStatService instance."""
    return StatsServiceFactory.get_life_stat_service()


def get_analytics_service() -> StatAnalyticsService:
    """Get StatAnalyticsService instance."""
    return StatsServiceFactory.get_analytics_service()

"""Repository interfaces for the skills domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import PracticeHistory, SkillPortfolio
from .value_objects import UserIdentifier


class SkillRepository(ABC):
    """Abstract repository that provides access to skill data."""

    @abstractmethod
    def portfolio_for_user(self, user_id: UserIdentifier) -> SkillPortfolio:
        """Return the portfolio of skills for a user."""


class PracticeRepository(ABC):
    """Abstract repository providing practice sessions."""

    @abstractmethod
    def history_for_user(self, user_id: UserIdentifier) -> PracticeHistory:
        """Return the practice history for the supplied user."""

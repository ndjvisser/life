"""
Dashboard domain repository interfaces - abstract data access contracts.
"""

from abc import ABC, abstractmethod
from typing import Optional

from .entities import UserProfile


class UserProfileRepository(ABC):
    """Abstract repository for UserProfile persistence."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username."""
        pass

    @abstractmethod
    def save(self, profile: UserProfile) -> UserProfile:
        """Save user profile and return updated entity."""
        pass

    @abstractmethod
    def create(self, profile: UserProfile) -> UserProfile:
        """Create new user profile."""
        pass

    @abstractmethod
    def exists_by_user_id(self, user_id: int) -> bool:
        """Check if profile exists for user ID."""
        pass


class UserRepository(ABC):
    """Abstract repository for User management."""

    @abstractmethod
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> int:
        """Create new user and return user ID."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user data by ID."""
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user data by username."""
        pass

    @abstractmethod
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields."""
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user ID if successful."""
        pass

"""
Unit of Work pattern for managing transactional boundaries in the dashboard domain.
"""

from abc import ABC, abstractmethod
from typing import Any


class UnitOfWork(ABC):
    """Abstract Unit of Work for managing transactional boundaries."""

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        """Enter the transaction context."""
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the transaction context, rolling back on exception."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass


class TransactionalUserRepository(ABC):
    """Extended UserRepository interface with atomic operations."""

    @abstractmethod
    def create_user_with_profile(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        bio: str = "",
        location: str = "",
    ) -> tuple[int, Any]:
        """
        Atomically create a user and their profile in a single transaction.

        This method ensures that both the user and profile are created together,
        or neither is created if any part of the operation fails.

        Parameters:
            username: Desired unique username.
            email: User email address.
            password: Plain-text password (repository is responsible for hashing).
            first_name: Optional first name (defaults to empty string).
            last_name: Optional last name (defaults to empty string).
            bio: Optional user bio (defaults to empty string).
            location: Optional user location (defaults to empty string).

        Returns:
            tuple[int, Any]: The newly created user's id and the saved profile entity.

        Raises:
            Exception: If either user or profile creation fails.
        """
        pass

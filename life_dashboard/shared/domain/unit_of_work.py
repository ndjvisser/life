"""Shared kernel Unit of Work abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Self, TypeVar

from .exceptions import TransactionError

_ReturnT = TypeVar("_ReturnT")


class AbstractUnitOfWork(AbstractContextManager[Self], ABC):
    """Base Unit of Work coordinating transactional boundaries."""

    def __init__(self) -> None:
        self._is_active = False
        self._pending_operations: list[Callable[[], None]] = []
        self._committed = False
        self._rolled_back = False

    def __enter__(self) -> Self:
        if self._is_active:
            raise TransactionError("Unit of work already active.")
        self._is_active = True
        self._committed = False
        self._rolled_back = False
        self._on_enter()
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        try:
            if exc_type:
                self.rollback()
            else:
                try:
                    self.commit()
                except Exception:  # pragma: no cover - defensive
                    self.rollback()
                    raise
        finally:
            self._on_exit()
            self._is_active = False
            self._pending_operations.clear()
        return False

    def _on_enter(self) -> None:
        """Hook for subclasses when a transaction begins."""

    def _on_exit(self) -> None:
        """Hook for subclasses when a transaction ends."""

    @property
    def committed(self) -> bool:
        """Indicate whether the unit of work successfully committed."""

        return self._committed

    @property
    def rolled_back(self) -> bool:
        """Indicate whether the unit of work rolled back a transaction."""

        return self._rolled_back

    def register_operation(self, operation: Callable[[], None]) -> None:
        """Register a callable to execute when the transaction commits."""

        if not self._is_active:
            raise TransactionError("Operations require an active transaction.")
        if not callable(operation):
            raise TransactionError("Registered operations must be callable.")
        self._pending_operations.append(operation)

    def commit(self) -> None:
        """Execute pending operations and finalize the transaction."""

        if not self._is_active:
            raise TransactionError("Cannot commit outside an active transaction.")

        try:
            for operation in list(self._pending_operations):
                operation()
        except Exception as exc:
            raise TransactionError("Transaction operation failed.") from exc

        self._commit()
        self._pending_operations.clear()
        self._committed = True

    def rollback(self) -> None:
        """Rollback the transaction and discard pending operations."""

        if not self._is_active:
            raise TransactionError("Cannot rollback outside an active transaction.")

        self._pending_operations.clear()
        self._rollback()
        self._rolled_back = True

    def run_atomic(self, operation: Callable[[Self], _ReturnT]) -> _ReturnT:
        """Execute an operation within a managed transaction."""

        if self._is_active:
            raise TransactionError("Cannot nest transactions on the same unit of work.")

        self.__enter__()
        try:
            result = operation(self)
        except Exception as exc:
            self.__exit__(type(exc), exc, exc.__traceback__)
            raise
        else:
            self.__exit__(None, None, None)
            return result

    @abstractmethod
    def _commit(self) -> None:
        """Persist changes to the underlying persistence mechanism."""

    @abstractmethod
    def _rollback(self) -> None:
        """Rollback changes in the underlying persistence mechanism."""


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """Simple in-memory unit of work used for testing."""

    def __init__(self) -> None:
        super().__init__()
        self.commit_calls = 0
        self.rollback_calls = 0

    def _commit(self) -> None:
        self.commit_calls += 1

    def _rollback(self) -> None:
        self.rollback_calls += 1

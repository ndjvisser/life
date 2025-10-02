"""Shared kernel exports for cross-context domain primitives."""

from .event_dispatcher import EventDispatcher, EventHandler, handles, publish_event
from .events import BaseEvent
from .exceptions import DomainError, RepositoryError, TransactionError, ValidationError
from .model import Entity, ValueObject
from .repository import AbstractRepository, InMemoryRepository, RepositoryProtocol
from .unit_of_work import AbstractUnitOfWork, InMemoryUnitOfWork

__all__ = [
    "AbstractRepository",
    "AbstractUnitOfWork",
    "BaseEvent",
    "DomainError",
    "Entity",
    "EventDispatcher",
    "EventHandler",
    "InMemoryRepository",
    "InMemoryUnitOfWork",
    "RepositoryError",
    "RepositoryProtocol",
    "TransactionError",
    "ValidationError",
    "ValueObject",
    "handles",
    "publish_event",
]

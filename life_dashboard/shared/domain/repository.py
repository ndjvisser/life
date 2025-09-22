"""Shared kernel repository contracts and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from .exceptions import RepositoryError
from .model import Entity

_EntityT = TypeVar("_EntityT", bound=Entity[Any])
_IdentifierT = TypeVar("_IdentifierT")


@runtime_checkable
class RepositoryProtocol(Protocol[_EntityT, _IdentifierT]):
    """Structural typing contract for repository implementations."""

    def get_by_id(self, entity_id: _IdentifierT) -> _EntityT | None: ...

    def save(self, entity: _EntityT) -> _EntityT: ...

    def delete(self, entity_id: _IdentifierT) -> bool: ...

    def list(self) -> Sequence[_EntityT]: ...


class AbstractRepository(ABC, Generic[_EntityT, _IdentifierT]):
    """Base repository enforcing contract semantics and type safety."""

    def __init__(self) -> None:
        self._seen: set[_EntityT] = set()

    def get_by_id(self, entity_id: _IdentifierT) -> _EntityT | None:
        entity = self._get_by_id(entity_id)
        if entity is not None:
            self._seen.add(entity)
        return entity

    def save(self, entity: _EntityT) -> _EntityT:
        self._ensure_identifier(entity)
        persisted = self._save(entity)
        self._seen.add(persisted)
        return persisted

    def delete(self, entity_id: _IdentifierT) -> bool:
        return self._delete(entity_id)

    def list(self) -> Sequence[_EntityT]:
        return list(self._list())

    @abstractmethod
    def _get_by_id(self, entity_id: _IdentifierT) -> _EntityT | None:
        raise NotImplementedError

    @abstractmethod
    def _save(self, entity: _EntityT) -> _EntityT:
        raise NotImplementedError

    @abstractmethod
    def _delete(self, entity_id: _IdentifierT) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _list(self) -> Iterable[_EntityT]:
        raise NotImplementedError

    def _ensure_identifier(self, entity: _EntityT) -> None:
        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            raise RepositoryError("Entities must define an identifier before saving.")


class InMemoryRepository(AbstractRepository[_EntityT, _IdentifierT], RepositoryProtocol[_EntityT, _IdentifierT]):
    """Generic in-memory repository for testing and prototypes."""

    def __init__(self) -> None:
        super().__init__()
        self._store: dict[_IdentifierT, _EntityT] = {}

    def _get_by_id(self, entity_id: _IdentifierT) -> _EntityT | None:
        return self._store.get(entity_id)

    def _save(self, entity: _EntityT) -> _EntityT:
        identifier = getattr(entity, "id", None)
        if identifier is None:
            raise RepositoryError("Entities must define an identifier before saving.")
        self._store[identifier] = entity
        return entity

    def _delete(self, entity_id: _IdentifierT) -> bool:
        return self._store.pop(entity_id, None) is not None

    def _list(self) -> Iterable[_EntityT]:
        return tuple(self._store.values())

    def exists(self, entity_id: _IdentifierT) -> bool:
        """Check if an entity exists in the repository."""

        return entity_id in self._store

    def clear(self) -> None:
        """Remove all entities from the repository."""

        self._store.clear()

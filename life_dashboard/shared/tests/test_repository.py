from __future__ import annotations

import pytest

from life_dashboard.shared.domain.exceptions import RepositoryError
from life_dashboard.shared.domain.model import Entity
from life_dashboard.shared.domain.repository import (
    InMemoryRepository,
    RepositoryProtocol,
)


class _TrackedEntity(Entity[int]):
    def __init__(self, entity_id: int | None, name: str) -> None:
        super().__init__(entity_id)
        self.id = entity_id
        self.name = name


def test_in_memory_repository_roundtrip() -> None:
    repository: InMemoryRepository[_TrackedEntity, int] = InMemoryRepository()
    entity = _TrackedEntity(1, "Quest")

    saved = repository.save(entity)
    assert saved is entity
    assert repository.get_by_id(1) is entity
    assert repository.list() == [entity]
    assert repository.delete(1) is True
    assert repository.get_by_id(1) is None


def test_in_memory_repository_requires_identifier() -> None:
    repository: InMemoryRepository[_TrackedEntity, int] = InMemoryRepository()

    with pytest.raises(RepositoryError):
        repository.save(_TrackedEntity(None, "Missing Id"))


def test_in_memory_repository_conforms_to_protocol() -> None:
    repository = InMemoryRepository[_TrackedEntity, int]()

    assert isinstance(repository, RepositoryProtocol)

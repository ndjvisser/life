from __future__ import annotations

import pytest

from life_dashboard.shared.domain.exceptions import TransactionError
from life_dashboard.shared.domain.model import Entity
from life_dashboard.shared.domain.repository import InMemoryRepository
from life_dashboard.shared.domain.unit_of_work import (
    AbstractUnitOfWork,
    InMemoryUnitOfWork,
)


class _StubEntity(Entity[int]):
    def __init__(self, entity_id: int | None, name: str) -> None:
        super().__init__(entity_id)
        self.id = entity_id
        self.name = name


def _persist_entity(uow: AbstractUnitOfWork, repository: InMemoryRepository[_StubEntity, int], entity: _StubEntity) -> None:
    uow.register_operation(lambda: repository.save(entity))


def test_unit_of_work_commits_registered_operations() -> None:
    repository: InMemoryRepository[_StubEntity, int] = InMemoryRepository()
    uow = InMemoryUnitOfWork()

    entity = _StubEntity(1, "Alpha")

    with uow:
        _persist_entity(uow, repository, entity)
        assert repository.get_by_id(1) is None

    assert repository.get_by_id(1) is entity
    assert uow.committed is True
    assert uow.rolled_back is False
    assert uow.commit_calls == 1


def test_unit_of_work_rolls_back_on_error() -> None:
    repository: InMemoryRepository[_StubEntity, int] = InMemoryRepository()
    uow = InMemoryUnitOfWork()

    with pytest.raises(RuntimeError):
        with uow:
            _persist_entity(uow, repository, _StubEntity(2, "Beta"))
            raise RuntimeError("fail to commit")

    assert repository.get_by_id(2) is None
    assert uow.rolled_back is True
    assert uow.rollback_calls == 1


def test_register_operation_requires_active_transaction() -> None:
    uow = InMemoryUnitOfWork()

    with pytest.raises(TransactionError):
        uow.register_operation(lambda: None)


def test_atomic_operation_executes_and_commits() -> None:
    repository: InMemoryRepository[_StubEntity, int] = InMemoryRepository()
    uow = InMemoryUnitOfWork()

    def operation(active_uow: AbstractUnitOfWork) -> str:
        entity = _StubEntity(3, "Gamma")
        active_uow.register_operation(lambda: repository.save(entity))
        return entity.name

    result = uow.run_atomic(operation)

    assert result == "Gamma"
    assert repository.get_by_id(3) is not None
    assert uow.committed is True


def test_atomic_operation_rolls_back_on_exception() -> None:
    repository: InMemoryRepository[_StubEntity, int] = InMemoryRepository()
    uow = InMemoryUnitOfWork()

    def operation(active_uow: AbstractUnitOfWork) -> None:
        entity = _StubEntity(4, "Delta")
        active_uow.register_operation(lambda: repository.save(entity))
        raise ValueError("boom")

    with pytest.raises(ValueError):
        uow.run_atomic(operation)

    assert repository.get_by_id(4) is None
    assert uow.rolled_back is True

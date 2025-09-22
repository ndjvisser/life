from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from life_dashboard.shared.domain.events import BaseEvent
from life_dashboard.shared.domain.exceptions import ValidationError
from life_dashboard.shared.domain.model import Entity, ValueObject


class _SampleEvent(BaseEvent):
    def __init__(self, payload: str) -> None:
        super().__init__()
        self.payload = payload


class _SampleEntity(Entity[int]):
    def __init__(self, entity_id: int | None, name: str) -> None:
        super().__init__(entity_id)
        self.name = name
        self.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class _PositiveAmount(ValueObject):
    amount: int

    def _validate(self) -> None:
        if self.amount <= 0:
            raise ValidationError("amount must be positive")


def test_entities_with_same_identifier_are_equal() -> None:
    left = _SampleEntity(1, "Alpha")
    right = _SampleEntity(1, "Alpha")

    assert left == right
    assert hash(left) == hash(right)


def test_entities_without_identifier_compare_by_state() -> None:
    left = _SampleEntity(None, "Alpha")
    right = _SampleEntity(None, "Alpha")

    assert left == right


def test_entity_domain_events_are_tracked_and_cleared() -> None:
    entity = _SampleEntity(1, "Alpha")
    event = _SampleEvent("payload")

    entity.record_event(event)

    assert entity.collect_events() == [event]

    pulled = entity.pull_events()
    assert pulled == [event]
    assert entity.collect_events() == []


def test_value_object_validation_runs_during_initialisation() -> None:
    with pytest.raises(ValidationError):
        _PositiveAmount(0)

    value = _PositiveAmount(5)
    value.validate()


def test_value_object_equality_depends_on_all_fields() -> None:
    assert _PositiveAmount(5) == _PositiveAmount(5)
    assert _PositiveAmount(5) != _PositiveAmount(6)

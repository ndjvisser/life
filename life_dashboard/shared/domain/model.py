"""Shared kernel base abstractions for entities and value objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from typing import Any, Generic, TypeVar

from .events import BaseEvent
from .exceptions import ValidationError

_IdentifierT = TypeVar("_IdentifierT")


class Entity(ABC, Generic[_IdentifierT]):
    """Base class for aggregate roots and entities."""

    def __init__(self, entity_id: _IdentifierT | None = None) -> None:
        self.id = entity_id
        self._domain_events: list[BaseEvent] = []

    def __eq__(self, other: object) -> bool:  # pragma: no cover - trivial
        if self is other:
            return True

        if not isinstance(other, Entity):
            return False

        if self.id is not None and other.id is not None:
            return self.id == other.id and type(self) is type(other)

        return type(self) is type(other) and self._identity_map() == other._identity_map()

    def __hash__(self) -> int:  # pragma: no cover - trivial
        if self.id is not None:
            return hash((type(self), self.id))
        return hash((type(self), tuple(sorted(self._identity_map().items()))))

    def _identity_map(self) -> dict[str, Any]:
        """Return a deterministic mapping of identity attributes for comparisons."""

        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    def record_event(self, event: BaseEvent) -> None:
        """Attach a domain event that occurred on this entity."""

        if not isinstance(event, BaseEvent):
            raise TypeError("Entities can only record BaseEvent instances")
        self._domain_events.append(event)

    def pull_events(self) -> list[BaseEvent]:
        """Return and clear all currently registered domain events."""

        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def collect_events(self) -> list[BaseEvent]:
        """Return a copy of currently registered domain events without clearing them."""

        return list(self._domain_events)

    def clear_events(self) -> None:
        """Remove all currently registered domain events."""

        self._domain_events.clear()


class ValueObject(ABC):
    """Base class for immutable value objects with validation support."""

    def __post_init__(self) -> None:
        self.validate()

    @abstractmethod
    def _validate(self) -> None:
        """Validation hook executed after initialization."""

        # Subclasses should override. Raising ensures mistakes are surfaced early.
        raise NotImplementedError("Value objects must implement _validate().")

    def validate(self) -> None:
        """Public validation entry point for re-validation in tests."""

        try:
            self._validate()
        except ValidationError:
            raise
        except NotImplementedError:
            raise
        except Exception as exc:  # pragma: no cover - defensive programming
            raise ValidationError(str(exc)) from exc

    def __eq__(self, other: object) -> bool:  # pragma: no cover - trivial
        if type(self) is not type(other):
            return False
        return self._frozen_state() == other._frozen_state()

    def __hash__(self) -> int:  # pragma: no cover - trivial
        return hash((type(self), self._frozen_state()))

    def _frozen_state(self) -> tuple[Any, ...]:
        """Return an immutable representation of the value object's state."""

        values: list[Any] = []

        if is_dataclass(self):
            for field in fields(self):
                values.append(self._freeze(getattr(self, field.name)))
        else:
            for key in sorted(self.__dict__):
                values.append(self._freeze(getattr(self, key)))

        return tuple(values)

    def _freeze(self, value: Any) -> Any:
        """Recursively convert mutable containers into hashable representations."""

        if isinstance(value, Mapping):
            return tuple((key, self._freeze(val)) for key, val in sorted(value.items()))

        if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
            return tuple(self._freeze(item) for item in value)

        return value

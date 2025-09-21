"""Skill registry for discovery and introspection.

The skills context relies on self-registration of skill domain classes so that
new skills can be discovered without manually wiring them into the package.
This module provides the lightweight registry that domain entities use to
register themselves on import.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, MutableMapping
from dataclasses import dataclass, field
from typing import TypeVar

__all__ = [
    "SkillRegistry",
    "skill_registry",
    "register_skill",
]


T = TypeVar("T", bound=type)


@dataclass(slots=True)
class SkillRegistry:
    """In-memory registry mapping string identifiers to skill classes."""

    _registry: MutableMapping[str, type] = field(default_factory=dict)

    def register(self, skill_cls: type, name: str | None = None) -> type:
        """Register *skill_cls* under *name* and return the class.

        If *name* is omitted the class name is used. Duplicate registrations for
        the same identifier are rejected unless they refer to the exact same
        class.
        """

        identifier = name or getattr(skill_cls, "slug", None) or skill_cls.__name__
        if identifier in self._registry and self._registry[identifier] is not skill_cls:
            existing = self._registry[identifier].__name__
            raise ValueError(
                f"Skill '{identifier}' already registered by '{existing}'."
            )

        self._registry[identifier] = skill_cls
        return skill_cls

    def get(self, name: str) -> type:
        """Return the registered skill class for *name*.

        Raises ``KeyError`` if the skill has not been registered.
        """

        try:
            return self._registry[name]
        except KeyError as exc:  # pragma: no cover - defensive branch
            raise KeyError(f"Skill '{name}' is not registered") from exc

    def __contains__(self, name: str) -> bool:
        return name in self._registry

    def __iter__(self) -> Iterator[type]:
        return iter(self._registry.values())

    def items(self) -> Iterable[tuple[str, type]]:
        return self._registry.items()

    def clear(self) -> None:
        self._registry.clear()


skill_registry = SkillRegistry()


def register_skill(skill_cls: T, *, name: str | None = None) -> T:
    """Decorator to register a skill class when it is defined."""

    skill_registry.register(skill_cls, name=name)
    return skill_cls

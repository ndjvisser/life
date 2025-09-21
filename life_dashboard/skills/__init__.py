"""Skills package exposing discovery helpers for domain registrations."""

from .registry import register_skill, skill_registry

__all__ = [
    "register_skill",
    "skill_registry",
]

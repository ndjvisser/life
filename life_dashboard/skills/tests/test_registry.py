"""Tests for the skills registry and automatic discovery."""

import importlib

import pytest


def test_domain_entities_are_registered():
    """Skill domain entities should self-register on import."""

    entities = importlib.import_module("life_dashboard.skills.domain.entities")
    from life_dashboard.skills import skill_registry

    assert skill_registry.get("SkillCategory") is entities.SkillCategory
    assert skill_registry.get("Skill") is entities.Skill


def test_registry_rejects_conflicting_registrations():
    """Different classes cannot claim the same registry identifier."""

    from life_dashboard.skills.registry import SkillRegistry

    registry = SkillRegistry()

    class DummySkill:
        pass

    class AnotherSkill:
        pass

    registry.register(DummySkill, name="dummy")

    with pytest.raises(ValueError):
        registry.register(AnotherSkill, name="dummy")

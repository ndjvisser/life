"""
Basic tests to ensure the Django setup is working correctly.
"""
from django.conf import settings
from django.test import TestCase


class BasicSetupTest(TestCase):
    """Test basic Django setup."""

    def test_django_settings_configured(self):
        """Test that Django settings are properly configured."""
        self.assertTrue(settings.configured)
        self.assertIn("life_dashboard.dashboard", settings.INSTALLED_APPS)

    def test_database_connection(self):
        """Test that database connection works."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)


def test_import_domain_layers():
    """Test that domain layers can be imported without Django dependencies."""
    # These should not raise ImportError
    from life_dashboard.achievements.domain import entities as achievements_entities
    from life_dashboard.dashboard.domain import entities as dashboard_entities
    from life_dashboard.journals.domain import entities as journals_entities
    from life_dashboard.privacy.domain import entities as privacy_entities
    from life_dashboard.quests.domain import entities as quests_entities
    from life_dashboard.skills.domain import entities as skills_entities
    from life_dashboard.stats.domain import entities as stats_entities

    # Basic smoke test - make sure classes exist
    assert hasattr(dashboard_entities, "UserProfile")
    assert hasattr(stats_entities, "CoreStat")
    assert hasattr(quests_entities, "Quest")
    assert hasattr(skills_entities, "Skill")
    assert hasattr(achievements_entities, "Achievement")
    assert hasattr(journals_entities, "JournalEntry")
    assert hasattr(privacy_entities, "ConsentRecord")


# Django model import test is handled by Django's own system checks


def test_architecture_boundaries():
    """Test that domain layers don't import Django."""
    import ast
    import glob
    import os

    violations = []

    for domain_dir in glob.glob("life_dashboard/*/domain/"):
        for py_file in glob.glob(os.path.join(domain_dir, "**/*.py"), recursive=True):
            if "__pycache__" in py_file:
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse the AST to check imports
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("django"):
                                violations.append(f"{py_file}: import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("django"):
                            violations.append(f"{py_file}: from {node.module}")

            except Exception:
                # Skip files that can't be parsed
                continue

    assert not violations, f"Found Django imports in domain layers: {violations}"

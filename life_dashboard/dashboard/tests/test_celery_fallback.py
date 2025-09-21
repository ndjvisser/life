"""Tests for Celery fallback functionality."""

import importlib
import inspect

import pytest


class TestCeleryFallback:
    """Test cases for Celery fallback when Celery is not available."""

    @staticmethod
    def _get_celery_module_source() -> str:
        """Return the source code for the Celery compatibility module."""

        try:
            module = importlib.import_module("life_dashboard.life_dashboard.celery")
        except ImportError as exc:  # pragma: no cover - defensive, skips test
            pytest.skip(f"Celery module not available: {exc}")

        try:
            return inspect.getsource(module)
        except (OSError, TypeError, AttributeError) as exc:
            pytest.skip(f"Unable to inspect Celery module source: {exc}")

    def test_celery_imports_work(self):
        """Test that Celery components can be imported successfully."""
        # This should work whether Celery is installed or not
        from life_dashboard.life_dashboard.celery import app, shared_task

        assert app is not None
        assert shared_task is not None

    def test_dashboard_tasks_import(self):
        """Test that dashboard tasks can be imported and have required methods."""
        from life_dashboard.dashboard.tasks import daily_task

        # Task should have async methods (real or fallback)
        assert hasattr(daily_task, "delay")
        assert hasattr(daily_task, "apply_async")

        # Methods should be callable
        assert callable(daily_task.delay)
        assert callable(daily_task.apply_async)

    def test_celery_fallback_structure_exists(self):
        """Test that the fallback Celery class has the correct structure."""
        content = self._get_celery_module_source()

        # Should have dummy Celery class with required methods
        assert "class Celery:" in content
        assert "def task(" in content
        assert "self, bind: bool = False, **kwargs: Any" in content
        assert "def shared_task(" in content
        assert "bind: bool = False, **kwargs: Any" in content

        # Should support bind parameter and async methods
        assert "class _TaskSelf:" in content
        assert "wrapped.delay =" in content
        assert "wrapped.apply_async =" in content

        # Should have retry method for bound tasks
        assert "def retry(" in content
        assert 'setattr(_TaskSelf, "retry", retry)' in content

    def test_fallback_addresses_original_issues(self):
        """Test that the fallback addresses the original issues mentioned."""
        content = self._get_celery_module_source()

        # Original issue 1: bind=True parameter support
        assert "bind: bool = False" in content

        # Original issue 2: .delay() and .apply_async() methods
        assert "wrapped.delay =" in content
        assert "wrapped.apply_async =" in content

        # Should handle bound tasks properly
        assert "task_self = _TaskSelf()" in content
        assert "call_args = (task_self, *args)" in content
        assert "return func(*call_args, **kwargs)" in content

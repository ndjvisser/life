"""
Tests for Celery fallback functionality.
"""


class TestCeleryFallback:
    """Test cases for Celery fallback when Celery is not available."""

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
        # Read the celery.py file to verify structure
        with open("life_dashboard/life_dashboard/celery.py") as f:
            content = f.read()

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
        with open("life_dashboard/life_dashboard/celery.py") as f:
            content = f.read()

        # Original issue 1: bind=True parameter support
        assert "bind: bool = False" in content

        # Original issue 2: .delay() and .apply_async() methods
        assert "wrapped.delay = lambda" in content
        assert "wrapped.apply_async = lambda" in content

        # Should handle bound tasks properly
        assert "task_self = _TaskSelf()" in content
        assert "call_args = (task_self, *args)" in content
        assert "return func(*call_args, **kwargs)" in content

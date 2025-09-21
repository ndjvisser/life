# life_dashboard/life_dashboard/celery.py
import importlib.util
import os
from collections.abc import Callable
from typing import Any


def _create_sync_decorator(
    bind: bool = False, *, with_retry: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Create a synchronous stand-in decorator for Celery task registration."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if bind:
                request_attrs: dict[str, Any] = {}
                if with_retry:
                    request_attrs["retries"] = 0
                request = type("R", (), request_attrs)()

                class _TaskSelf:
                    """Minimal stand-in for Celery's bound task instance."""

                task_self = _TaskSelf()
                task_self.request = request

                if with_retry:

                    def retry(
                        self,
                        exc: Exception | None = None,
                        _countdown: int | None = None,
                        **_retry_kwargs: Any,
                    ) -> None:
                        if exc is not None:
                            raise exc

                    setattr(_TaskSelf, "retry", retry)

                call_args = (task_self, *args)
            else:
                call_args = args

            return func(*call_args, **kwargs)

        wrapped.delay = lambda *a, **k: wrapped(*a, **k)
        wrapped.apply_async = lambda args=None, kwargs=None, **_opts: wrapped(
            *(args or ()), **(kwargs or {})
        )
        return wrapped

    return decorator


celery_spec = importlib.util.find_spec("celery")

if celery_spec is None:

    class Celery:
        """Development fallback when Celery isn't installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
            """Accept arbitrary arguments without side effects."""

        def config_from_object(self, *args: Any, **kwargs: Any) -> None:
            """No-op configuration hook."""

        def autodiscover_tasks(self, *args: Any, **kwargs: Any) -> None:
            """No-op task discovery hook."""

        def task(
            self, bind: bool = False, **kwargs: Any
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return _create_sync_decorator(bind=bind, with_retry=False)

        def shared_task(
            self, bind: bool = False, **kwargs: Any
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return _create_sync_decorator(bind=bind, with_retry=True)

    def shared_task(
        bind: bool = False, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Module-level stand-in for Celery's shared_task decorator."""

        return _create_sync_decorator(bind=bind, with_retry=True)
else:
    from celery import Celery, shared_task


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "life_dashboard.life_dashboard.settings"
)

app = Celery("life_dashboard")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


__all__ = ["app", "shared_task"]

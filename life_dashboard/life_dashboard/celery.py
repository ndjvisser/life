# life_dashboard/life_dashboard/celery.py
import os

try:
    from celery import Celery
except ImportError:
    # Celery is optional - create a dummy class for development
    class Celery:
        def __init__(self, *args, **kwargs):
            """
            No-op initializer for the dummy Celery class.

            Accepts any positional and keyword arguments for compatibility with the real Celery API but performs no initialization or side effects.
            """
            pass

        def config_from_object(self, *args, **kwargs):
            """
            No-op fallback for Celery's config_from_object used when Celery is not installed.

            Accepts any arguments and keyword arguments and performs no action. Keeps call sites safe so code can invoke the same configuration call whether the real Celery library is present or not.
            """
            pass

        def autodiscover_tasks(self, *args, **kwargs):
            """
            No-op replacement for Celery's `autodiscover_tasks` used when Celery is unavailable.

            This method accepts any positional and keyword arguments for compatibility with the real
            Celery API but performs no action. It exists so calling code can invoke `autodiscover_tasks`
            without conditional checks when running in environments where the `celery` package is not installed.
            """
            pass

        def task(self, bind: bool = False, **kwargs):
            """Dummy task decorator for when Celery is not installed."""

            def decorator(func):
                def wrapped(*args, **kw):
                    if bind:

                        class _Self:
                            # minimal task-like object
                            request = type("R", (), {})()

                        return func(_Self(), *args, **kw)
                    return func(*args, **kw)

                # Synchronous fallbacks
                wrapped.delay = lambda *a, **k: wrapped(*a, **k)
                wrapped.apply_async = lambda args=None, kwargs=None, **opts: wrapped(
                    *(args or ()), **(kwargs or {})
                )
                return wrapped

            return decorator

    def shared_task(bind: bool = False, **kwargs):
        """Dummy shared_task decorator for when Celery is not installed."""

        def decorator(func):
            def wrapped(*args, **kw):
                if bind:

                    class _Self:
                        # minimal task-like object with request and retry method
                        request = type("R", (), {"retries": 0})()

                        def retry(self, exc=None, countdown=None, **retry_kwargs):
                            # In no-celery mode, just re-raise the exception
                            if exc:
                                raise exc

                    return func(_Self(), *args, **kw)
                return func(*args, **kw)

            # Synchronous fallbacks
            wrapped.delay = lambda *a, **k: wrapped(*a, **k)
            wrapped.apply_async = lambda args=None, kwargs=None, **opts: wrapped(
                *(args or ()), **(kwargs or {})
            )
            return wrapped

        return decorator


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "life_dashboard.life_dashboard.settings"
)

app = Celery("life_dashboard")

# Make shared_task available at module level when Celery is not installed
try:
    from celery import shared_task
except ImportError:
    # Use the dummy shared_task from our Celery class
    shared_task = app.shared_task

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

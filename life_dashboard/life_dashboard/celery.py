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

        def task(self, *args, **kwargs):
            """
            No-op task decorator used when Celery is not available.

            Returns a decorator that, when applied to a function, returns the function unchanged
            (in other words, it does not register or modify the function as a Celery task).
            Accepts the same args/kwargs as the real Celery `task` decorator but ignores them.
            """

            def decorator(func):
                """
                No-op decorator that returns the original callable unchanged.

                Used as a fallback for Celery's `task` decorator when Celery is not installed.

                Parameters:
                    func (callable): The function or callable to decorate; returned unmodified.

                Returns:
                    callable: The same callable passed in.
                """
                return func

            return decorator


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

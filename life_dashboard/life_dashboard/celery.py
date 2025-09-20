# life_dashboard/life_dashboard/celery.py
import os

try:
    from celery import Celery
except ImportError:
    # Celery is optional - create a dummy class for development
    class Celery:
        def __init__(self, *args, **kwargs):
            pass

        def config_from_object(self, *args, **kwargs):
            pass

        def autodiscover_tasks(self, *args, **kwargs):
            pass

        def task(self, *args, **kwargs):
            """Dummy task decorator for when Celery is not installed"""

            def decorator(func):
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

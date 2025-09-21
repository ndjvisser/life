# This file marks the life_dashboard package

try:
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except ImportError:
    # Celery is optional for development
    celery_app = None
    __all__ = ()

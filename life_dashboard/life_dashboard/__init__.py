# This file marks the life_dashboard package

from .celery import app as celery_app

__all__ = ("celery_app",)

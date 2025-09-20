# This file is deprecated - models moved to infrastructure/models.py
# Import from there for backward compatibility

from .infrastructure.models import (  # noqa: F401
    CoreStatModel,
    LifeStatModel,
    StatHistoryModel,
)

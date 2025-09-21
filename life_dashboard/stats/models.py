# This file is deprecated - models moved to infrastructure/models.py
# Import from there for backward compatibility

from .infrastructure.models import (  # noqa: F401
    CoreStatModel,
    LifeStatCategoryModel,
    LifeStatModel,
    StatHistoryModel,
    Stats,  # Legacy model for backward compatibility
)

# Legacy aliases to maintain backwards compatibility with previous public API
CoreStat = CoreStatModel
LifeStat = LifeStatModel
StatHistory = StatHistoryModel

__all__ = [
    "CoreStatModel",
    "LifeStatCategoryModel",
    "LifeStatModel",
    "StatHistoryModel",
    "Stats",
    "CoreStat",
    "LifeStat",
    "StatHistory",
]
